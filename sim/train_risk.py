"""Train and evaluate the lapse-risk model (Task 02b, Drop A).

python -m sim.train_risk --run sim/out/risk_001

1. Generates training data (arm C, baseline, seeds 21-30 by default): one row per persona-day, features from
   rebound_engine.risk.compute_features (engine-visible data only), plus the engine's engagement state.
2. Label: the engine's state becomes `lapsed` within the next 7 days.
3. Split by seed, so no persona is in two splits: train 21-26, validation 27-28, test 29-30.
4. Logistic regression and gradient boosting; pick by validation AUROC. Two baselines: the drifting rule and a
   last-7-day completion-rate heuristic (threshold set on validation at the same alert rate).
5. Writes models/lapse_risk.joblib, and <run>/risk/: metrics_risk.json, summary.md, roc.png, calibration.png,
   feature_importance.png, alerts_examples.csv.
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from rebound_engine import config as engine_config
from rebound_engine.risk import FEATURE_NAMES, RiskModel, save_risk_model
from sklearn.calibration import calibration_curve
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score, roc_curve
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from . import load_config
from .arms import run_persona
from .personas import generate_personas
from .run import map_seeds, parse_seeds, personas_frame

LABEL_DAYS = 7
RESERVED_SEEDS = set(range(1, 21)) | {101}  # evaluation (1-10), step-up test (11-20), calibration (101)
FAIRNESS_SEGMENTS = ("schedule_type", "language", "mobility_limitation")
BOOTSTRAP = 200
KEY = ["seed", "persona_id"]


# ---------- data ----------


def _feature_seed(job: tuple) -> tuple[int, pd.DataFrame, pd.DataFrame]:
    seed, n, days, cfg = job
    personas = generate_personas(n, seed, cfg)
    rows: list[dict] = []
    for payload, traits in personas:
        run_persona("C", payload, traits, cfg, days, seed, features=rows)
    return seed, pd.DataFrame(rows), personas_frame(seed, personas)


def generate(n: int, days: int, seeds: list[int], cfg: dict, workers: int = 0, quiet: bool = False):
    """(features, personas) for arm C on the given seeds."""
    cfg = {**cfg, "days": days}
    results = map_seeds(_feature_seed, [(s, n, days, cfg) for s in seeds], workers, quiet)
    return pd.concat([r[1] for r in results], ignore_index=True), pd.concat([r[2] for r in results], ignore_index=True)


def add_labels(df: pd.DataFrame, days: int) -> pd.DataFrame:
    """label = engine state is `lapsed` on any of the next 7 days. `valid` rows: not already lapsed, and the full
    7-day window exists (day <= days - 7). `alertable` rows: not already lapsed (used for warning time)."""
    df = df.sort_values([*KEY, "day"]).reset_index(drop=True)
    labels = np.zeros(len(df), dtype=bool)
    for _, g in df.groupby(KEY, sort=False):
        lapsed_days = set(g.loc[g["engine_state"] == "lapsed", "day"])
        for i, d in zip(g.index, g["day"], strict=True):
            labels[i] = any(d + k in lapsed_days for k in range(1, LABEL_DAYS + 1))
    df["label"] = labels
    df["alertable"] = df["engine_state"] != "lapsed"
    df["valid"] = df["alertable"] & (df["day"] <= days - LABEL_DAYS)
    return df


def lapse_onsets(df: pd.DataFrame) -> list[tuple[int, int, int]]:
    """(seed, persona_id, onset day) for every transition into the engine's `lapsed` state."""
    out = []
    for (seed, pid), g in df.sort_values("day").groupby(KEY):
        prev = None
        for d, s in zip(g["day"], g["engine_state"], strict=True):
            if s == "lapsed" and prev not in (None, "lapsed"):
                out.append((seed, pid, int(d)))
            prev = s
    return out


def split(df: pd.DataFrame, train: list[int], val: list[int], test: list[int]):
    sets = [set(train), set(val), set(test)]
    if sets[0] & sets[1] or sets[0] & sets[2] or sets[1] & sets[2]:
        raise ValueError("train / validation / test seeds must not overlap (personas are split by seed)")
    return tuple(df[df["seed"].isin(s)] for s in (train, val, test))


# ---------- metrics ----------


def _bootstrap(frame: pd.DataFrame, fn, rng: np.random.Generator) -> tuple[float, float]:
    """95% percentile interval over personas (resampled with replacement)."""
    groups = list(frame.reset_index(drop=True).groupby(KEY).indices.values())
    vals = []
    for _ in range(BOOTSTRAP):
        pick = rng.integers(len(groups), size=len(groups))
        idx = np.concatenate([groups[i] for i in pick])
        v = fn(idx)
        if v is not None and not np.isnan(v):
            vals.append(v)
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))) if vals else (float("nan"),) * 2


def _safe_auc(y: np.ndarray, s: np.ndarray) -> float:
    return float(roc_auc_score(y, s)) if 0 < y.sum() < len(y) else float("nan")


def warning_times(alert_frame: pd.DataFrame, alerts: np.ndarray, onsets: list[tuple[int, int, int]]) -> dict:
    """For each lapse onset, was there an alert in the 7 days before it, and how early was the first one?"""
    alerted = {(s, p, d) for (s, p, d), a in zip(
        alert_frame[["seed", "persona_id", "day"]].itertuples(index=False, name=None), alerts, strict=True) if a}
    caught, leads = 0, []
    for seed, pid, onset in onsets:
        days = [onset - k for k in range(LABEL_DAYS, 0, -1) if (seed, pid, onset - k) in alerted]
        if days:
            caught += 1
            leads.append(onset - days[0])
    return {"lapses": len(onsets), "caught": caught, "caught_share": caught / len(onsets) if onsets else float("nan"),
            "median_warning_days": float(np.median(leads)) if leads else float("nan")}


def evaluate(name: str, scores: np.ndarray, threshold: float, lab: pd.DataFrame, alert_frame: pd.DataFrame,
             alert_scores: np.ndarray, onsets: list, probabilistic: bool, rng: np.random.Generator) -> dict:
    y = lab["label"].to_numpy()
    alerts = scores >= threshold
    pos = y.sum()
    out = {
        "name": name,
        "threshold": float(threshold),
        "auroc": _safe_auc(y, scores),
        "pr_auc": float(average_precision_score(y, scores)) if pos else float("nan"),
        "brier": float(brier_score_loss(y, scores)) if probabilistic else None,
        "alert_rate": float(alerts.mean()),
        "recall": float((alerts & y).sum() / pos) if pos else float("nan"),
        "precision": float((alerts & y).sum() / alerts.sum()) if alerts.sum() else float("nan"),
        "positives": int(pos),
        "rows": len(y),
    }
    lab_r = lab.reset_index(drop=True)
    out["auroc_ci"] = _bootstrap(lab_r, lambda i: _safe_auc(y[i], scores[i]), rng)
    out["recall_ci"] = _bootstrap(lab_r, lambda i: (alerts[i] & y[i]).sum() / y[i].sum() if y[i].sum() else None, rng)
    out["warning"] = warning_times(alert_frame, alert_scores >= threshold, onsets)
    return out


# ---------- training ----------


def fit_models(train: pd.DataFrame) -> dict[str, object]:
    X, y = train[list(FEATURE_NAMES)].to_numpy(float), train["label"].to_numpy()
    logistic = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    logistic.fit(X, y)
    boosting = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, random_state=0)
    boosting.fit(X, y)
    return {"logistic": logistic, "gradient_boosting": boosting}


def model_weights(kind: str, model, val: pd.DataFrame) -> dict[str, float]:
    if kind == "logistic":
        return dict(zip(FEATURE_NAMES, model[-1].coef_[0].tolist(), strict=True))
    X, y = val[list(FEATURE_NAMES)].to_numpy(float), val["label"].to_numpy()
    imp = permutation_importance(model, X, y, scoring="roc_auc", n_repeats=5, random_state=0)
    return dict(zip(FEATURE_NAMES, imp.importances_mean.tolist(), strict=True))


def train_and_evaluate(feats: pd.DataFrame, personas: pd.DataFrame, days: int, train_s: list[int], val_s: list[int],
                       test_s: list[int], alert_rate: float, quiet: bool = False) -> tuple[RiskModel, dict, dict]:
    df = add_labels(feats, days)
    tr_all, va_all, te_all = split(df, train_s, val_s, test_s)
    tr, va, te = (f[f["valid"]] for f in (tr_all, va_all, te_all))
    te_alert = te_all[te_all["alertable"]]
    onsets = lapse_onsets(te_all)
    rng = np.random.default_rng(0)

    models = fit_models(tr)
    Xva, Xte, Xal = (f[list(FEATURE_NAMES)].to_numpy(float) for f in (va, te, te_alert))
    yva = va["label"].to_numpy()
    val_auc = {k: _safe_auc(yva, m.predict_proba(Xva)[:, 1]) for k, m in models.items()}
    chosen = max(val_auc, key=val_auc.get)

    results, thresholds = {}, {}
    for kind, m in models.items():
        thresholds[kind] = float(np.quantile(m.predict_proba(Xva)[:, 1], 1 - alert_rate))
        results[kind] = evaluate(kind, m.predict_proba(Xte)[:, 1], thresholds[kind], te, te_alert,
                                 m.predict_proba(Xal)[:, 1], onsets, True, rng)
    # Baseline 1: the engine's own drifting rule (alert = state is drifting).
    results["drifting_rule"] = evaluate("drifting_rule", te["state_drifting"].to_numpy(), 0.5, te, te_alert,
                                        te_alert["state_drifting"].to_numpy(), onsets, False, rng)
    # Baseline 2: low last-7-day completion, threshold set on validation at the same alert rate.
    heur_thr = float(np.quantile(1 - va["comp_rate_7"].to_numpy(), 1 - alert_rate))
    results["completion_heuristic"] = evaluate("completion_heuristic", 1 - te["comp_rate_7"].to_numpy(), heur_thr, te,
                                               te_alert, 1 - te_alert["comp_rate_7"].to_numpy(), onsets, False, rng)

    # Model minus heuristic AUROC, same persona resamples.
    y = te["label"].to_numpy()
    s_model = models[chosen].predict_proba(Xte)[:, 1]
    s_heur = 1 - te["comp_rate_7"].to_numpy()
    diff_ci = _bootstrap(te.reset_index(drop=True), lambda i: _safe_auc(y[i], s_model[i]) - _safe_auc(y[i], s_heur[i]),
                         rng)

    # Fairness: chosen model and heuristic by segment.
    seg = te.merge(personas, on=KEY, how="left")
    fairness = {}
    for col in FAIRNESS_SEGMENTS:
        fairness[col] = {}
        for value, g in seg.groupby(col):
            yy = g["label"].to_numpy()
            sm = models[chosen].predict_proba(g[list(FEATURE_NAMES)].to_numpy(float))[:, 1]
            sh = 1 - g["comp_rate_7"].to_numpy()
            fairness[col][str(value)] = {
                "rows": len(g), "positives": int(yy.sum()),
                "model_auroc": _safe_auc(yy, sm),
                "model_recall": float(((sm >= thresholds[chosen]) & yy).sum() / yy.sum()) if yy.sum() else None,
                "heuristic_auroc": _safe_auc(yy, sh),
                "heuristic_recall": float(((sh >= heur_thr) & yy).sum() / yy.sum()) if yy.sum() else None,
            }

    Xtr = tr[list(FEATURE_NAMES)].to_numpy(float)
    risk_model = RiskModel(
        model=models[chosen], kind=chosen, feature_names=FEATURE_NAMES, threshold=thresholds[chosen],
        mean=dict(zip(FEATURE_NAMES, Xtr.mean(axis=0).tolist(), strict=True)),
        std=dict(zip(FEATURE_NAMES, Xtr.std(axis=0).tolist(), strict=True)),
        weights=model_weights(chosen, models[chosen], va),
        meta={"train_seeds": train_s, "val_seeds": val_s, "test_seeds": test_s, "alert_rate": alert_rate,
              "label_days": LABEL_DAYS, "val_auroc": val_auc},
    )
    other = "gradient_boosting" if chosen == "logistic" else "logistic"
    metrics = {
        "chosen": chosen, "val_auroc": val_auc, "alert_rate_target": alert_rate,
        "splits": {"train": train_s, "val": val_s, "test": test_s,
                   "rows": {"train": len(tr), "val": len(va), "test": len(te)},
                   "positive_share": {"train": float(tr["label"].mean()), "val": float(va["label"].mean()),
                                      "test": float(te["label"].mean())}},
        "test": results,
        "model_minus_heuristic_auroc_ci": diff_ci,
        "fairness": fairness,
        "weights": {chosen: risk_model.weights, other: model_weights(other, models[other], va)},
    }
    curves = {k: models[k].predict_proba(Xte)[:, 1] for k in models}
    return risk_model, metrics, {"y": y, "scores": curves, "heuristic": s_heur, "drifting": te["state_drifting"].to_numpy(),
                                 "test_alert": te_alert, "alert_scores": models[chosen].predict_proba(Xal)[:, 1]}


# ---------- outputs ----------


def charts(metrics: dict, extra: dict, out: Path) -> None:
    y = extra["y"]
    fig, ax = plt.subplots(figsize=(5.5, 5))
    for kind, s in extra["scores"].items():
        fpr, tpr, _ = roc_curve(y, s)
        ax.plot(fpr, tpr, lw=2, label=f"{kind} (AUROC {metrics['test'][kind]['auroc']:.3f})")
    fpr, tpr, _ = roc_curve(y, extra["heuristic"])
    ax.plot(fpr, tpr, lw=1.5, ls="--", label=f"completion heuristic ({metrics['test']['completion_heuristic']['auroc']:.3f})")
    d = metrics["test"]["drifting_rule"]
    fp = ((extra["drifting"] >= 0.5) & ~y).sum() / max(1, (~y).sum())
    ax.scatter([fp], [d["recall"]], color="black", zorder=3, label="drifting rule")
    ax.plot([0, 1], [0, 1], color="grey", lw=0.8)
    ax.set(xlabel="False positive rate", ylabel="True positive rate", title="Lapse within 7 days: ROC (test seeds)")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "roc.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.5, 5))
    for kind, s in extra["scores"].items():
        frac, mean_pred = calibration_curve(y, s, n_bins=10, strategy="quantile")
        ax.plot(mean_pred, frac, marker="o", lw=1.5, label=kind)
    ax.plot([0, 1], [0, 1], color="grey", lw=0.8)
    ax.set(xlabel="Predicted risk", ylabel="Observed share that lapsed", title="Calibration (test seeds)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out / "calibration.png", dpi=150)
    plt.close(fig)

    chosen = metrics["chosen"]
    w = metrics["weights"][chosen]
    top = sorted(w.items(), key=lambda kv: -abs(kv[1]))[:15][::-1]
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.barh([k for k, _ in top], [v for _, v in top], color=["#b5487a" if v > 0 else "#5b8def" for _, v in top])
    ax.set(xlabel="standardised coefficient" if chosen == "logistic" else "permutation importance (AUROC drop)",
           title=f"Top features: {chosen}")
    fig.tight_layout()
    fig.savefig(out / "feature_importance.png", dpi=150)
    plt.close(fig)


def summary_markdown(metrics: dict) -> str:
    def ci(v, lohi):
        return f"{v:.3f} [{lohi[0]:.3f}, {lohi[1]:.3f}]"

    lines = [
        "## Lapse-risk model (Task 02b, Drop A)", "",
        (f"Trained on arm C, baseline scenario, seeds {metrics['splits']['train']}; threshold set on validation seeds "
        f"{metrics['splits']['val']}; all numbers below are on test seeds {metrics['splits']['test']} (different "
        "personas). Simulated data only: this shows the pipeline works, not real-world accuracy."), "",
        (f"Chosen by validation AUROC: **{metrics['chosen']}** "
        f"(validation AUROC: {', '.join(f'{k} {v:.3f}' for k, v in metrics['val_auroc'].items())})."), "",
        ("| Predictor | AUROC [95% CI] | PR-AUC | Brier | Alert rate | Recall [95% CI] | Precision | Lapses caught "
        "| Median warning (days) |"),
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for k, r in metrics["test"].items():
        brier = f"{r['brier']:.3f}" if r["brier"] is not None else "n/a"
        w = r["warning"]
        lines.append(f"| {k} | {ci(r['auroc'], r['auroc_ci'])} | {r['pr_auc']:.3f} | {brier} | {r['alert_rate']:.1%} | "
                     f"{ci(r['recall'], r['recall_ci'])} | {r['precision']:.3f} | {w['caught']}/{w['lapses']} "
                     f"({w['caught_share']:.0%}) | {w['median_warning_days']:.1f} |")
    lo, hi = metrics["model_minus_heuristic_auroc_ci"]
    lines += ["", f"Chosen model minus completion heuristic, AUROC: 95% CI [{lo:+.3f}, {hi:+.3f}] (persona bootstrap).",
              "", ("Alert rate is the share of test days flagged. Lapses caught: an alert in the 7 days before the "
              "engine entered `lapsed`. Warning: days from the first such alert to the lapse."), "",
              "### Fairness (test seeds)", "", ("| Segment | Value | Rows | Lapses ahead | Model AUROC | Model recall | "
              "Heuristic AUROC | Heuristic recall |"), "|---|---|---|---|---|---|---|---|"]
    for col, vals in metrics["fairness"].items():
        for v, r in vals.items():
            def f(x):
                return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.3f}"
            lines.append(f"| {col} | {v} | {r['rows']} | {r['positives']} | {f(r['model_auroc'])} | "
                         f"{f(r['model_recall'])} | {f(r['heuristic_auroc'])} | {f(r['heuristic_recall'])} |")
    w = metrics["weights"][metrics["chosen"]]
    top = sorted(w.items(), key=lambda kv: -abs(kv[1]))[:10]
    lines += ["", f"### Top features ({metrics['chosen']})", ""] + [f"- {k}: {v:+.3f}" for k, v in top]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Train + evaluate the lapse-risk model")
    ap.add_argument("--run", default="sim/out/risk_001", help="folder for training data and outputs")
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--seeds", default="21-30")
    ap.add_argument("--train", default="21-26")
    ap.add_argument("--val", default="27-28")
    ap.add_argument("--test", default="29-30")
    ap.add_argument("--scenario", default="baseline")
    ap.add_argument("--alert-rate", type=float, default=engine_config.RISK_ALERT_RATE)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--model-out", default="models/lapse_risk.joblib")
    ap.add_argument("--regenerate", action="store_true", help="rebuild training data even if it exists")
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    seeds = parse_seeds(args.seeds)
    train_s, val_s, test_s = (parse_seeds(x) for x in (args.train, args.val, args.test))
    if set(train_s) | set(val_s) | set(test_s) != set(seeds):
        sys.exit("--train/--val/--test must together be exactly --seeds")
    if set(seeds) & RESERVED_SEEDS:
        sys.exit(f"seeds {sorted(set(seeds) & RESERVED_SEEDS)} are reserved for evaluation/calibration; use others")

    run = Path(args.run)
    run.mkdir(parents=True, exist_ok=True)
    fpath, ppath = run / "features.parquet", run / "personas.parquet"
    try:
        if fpath.exists() and ppath.exists() and not args.regenerate:
            feats, personas = pd.read_parquet(fpath), pd.read_parquet(ppath)
            print(f"using existing training data in {run}")
        else:
            print(f"generating training data: arm C, scenario={args.scenario}, n={args.n}, seeds={seeds}")
            feats, personas = generate(args.n, args.days, seeds, load_config(args.scenario), args.workers)
            feats.to_parquet(fpath, index=False)
            personas.to_parquet(ppath, index=False)
        print("training and evaluating...")
        model, metrics, extra = train_and_evaluate(feats, personas, args.days, train_s, val_s, test_s, args.alert_rate)
    except KeyboardInterrupt:
        print("\ninterrupted: nothing written", file=sys.stderr)
        sys.exit(130)

    out = run / "risk"
    out.mkdir(exist_ok=True)
    save_risk_model(model, args.model_out)
    (out / "metrics_risk.json").write_text(json.dumps(metrics, indent=1, sort_keys=True, default=float), encoding="utf-8")
    charts(metrics, extra, out)
    te_alert, scores = extra["test_alert"].reset_index(drop=True), extra["alert_scores"]
    picks = np.flatnonzero(scores >= model.threshold)[:200]
    rows = []
    for i in picks:
        feats_i = {n: float(te_alert.at[i, n]) for n in FEATURE_NAMES}
        rows.append({"seed": int(te_alert.at[i, "seed"]), "persona_id": int(te_alert.at[i, "persona_id"]),
                     "day": int(te_alert.at[i, "day"]), "risk": float(scores[i]),
                     "lapsed_within_7d": bool(te_alert.at[i, "label"]),
                     "reasons": "; ".join(model.reasons(feats_i)), "reason_features": "; ".join(model.explain(feats_i))})
    pd.DataFrame(rows).to_csv(out / "alerts_examples.csv", index=False)
    md = summary_markdown(metrics)
    (out / "summary.md").write_text(md, encoding="utf-8")
    print(md)
    print(f"model: {args.model_out}; outputs: {out}")


if __name__ == "__main__":
    main()
