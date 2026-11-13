"""Outcome metrics (Task 02 Part 3), per arm and per seed, then mean + 95% interval across seeds."""

import math
import statistics

import numpy as np
import pandas as pd

from .personas import SEGMENTS

RECOVERY_WINDOW = 14
CAUSE_LOOKBACK = 7  # a lapse is attributed to a disruption active on the onset day or the 7 days before
CAUSES = ("shock", "labelled", "none")
MIN_SEGMENT_SIZE = 5  # smaller segments are left out of the best-worst gap (too noisy)

# name -> (label, unit). pct metrics are stored as 0-1 and shown as percentages / points.
METRICS = {
    "persistence_w4": ("Persistence, week 4", "pct"),
    "persistence_w8": ("Persistence, week 8", "pct"),
    "persistence_w12": ("Persistence, week 12", "pct"),
    "persistence_all": ("Persistence, weeks 4+8+12", "pct"),
    "recovery_rate": ("Recovery within 14 days", "pct"),
    "recovery_labelled": ("Recovery within 14 days, after a labelled disruption", "pct"),
    "recovery_shock": ("Recovery within 14 days, after an unlabelled shock", "pct"),
    "recovery_none": ("Recovery within 14 days, no disruption nearby", "pct"),
    "days_to_active": ("Median days from lapse to active", "days"),
    "time_to_recover": ("Median days from lapse to recovering", "days"),
    "delta_minutes": ("Δ weekly active minutes (wk1→wk12)", "min"),
    "delta_sleep_effort": ("Δ tier-weighted sleep nights (wk1→wk12)", "pct"),
    "delta_sleep": ("Δ sleep nights completed, raw (wk1→wk12)", "pct"),
    "retention": ("Retention at end", "pct"),
    "messages_per_week": ("Messages per persona-week", "count"),
    "quiet_messages": ("Messages in quiet hours", "count"),
    "quiet_share": ("Share of messages in quiet hours", "pct"),
    "safety_violations": ("Safety violations", "count"),
}
EQUITY_METRICS = ("persistence_w12", "recovery_rate", "retention", "delta_minutes")
COMPARE_METRICS = ("persistence_w12", "persistence_all", "recovery_rate", "recovery_labelled", "recovery_shock",
                   "days_to_active", "retention", "delta_minutes", "delta_sleep_effort")  # raw sleep share is in the table only (biased)
COMPARISONS = (("C", "A"), ("B", "A"), ("C", "B"), ("C", "A0"),
               ("C4", "C"), ("C4", "A"), ("C4", "A0"))  # C4 = pre-registered step-up test

_T95 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26, 10: 2.23,
        12: 2.18, 15: 2.13, 20: 2.09, 30: 2.04}


def _t95(df: int) -> float:
    return _T95[max(k for k in _T95 if k <= df)] if df >= 1 else float("nan")


def summarise(values: list[float]) -> dict:
    """Mean, 95% t-interval for the mean across seeds, and min-max."""
    vals = [v for v in values if v is not None and not math.isnan(v)]
    if not vals:
        return {"mean": None, "ci_low": None, "ci_high": None, "min": None, "max": None, "n": 0}
    mean = statistics.fmean(vals)
    half = _t95(len(vals) - 1) * statistics.stdev(vals) / math.sqrt(len(vals)) if len(vals) > 1 else 0.0
    return {"mean": mean, "ci_low": mean - half, "ci_high": mean + half, "min": min(vals), "max": max(vals),
            "n": len(vals)}


# ---------- per persona ----------


def onset_cause(day: int, shock_days: set[int], labelled_days: set[int]) -> str:
    """What preceded a lapse: an unlabelled shock wins over a labelled disruption if both were active."""
    window = range(day - CAUSE_LOOKBACK, day + 1)
    if any(d in shock_days for d in window):
        return "shock"
    if any(d in labelled_days for d in window):
        return "labelled"
    return "none"


def persona_table(events: pd.DataFrame, personas: pd.DataFrame, days: int) -> pd.DataFrame:
    """One row per (seed, arm, persona) with everything the metrics need."""
    weeks = days // 7
    acts = events[events["kind"] == "action"]
    key = ["seed", "arm", "persona_id"]
    churn_day = events[events["kind"] == "churn"].groupby(key)["day"].min().to_dict()
    checkins_sent = events[events["kind"] == "checkin_sent"].groupby(key).size().to_dict()
    rows = []
    for (seed, arm, pid), g in acts.groupby(["seed", "arm", "persona_id"], sort=True):
        done = g["outcome"].isin(["completed", "partial"])
        day_active = done.groupby(g["day"]).any()
        week_active = np.zeros(weeks + 1)
        for d, active in day_active.items():
            if active and (d - 1) // 7 + 1 <= weeks:
                week_active[(d - 1) // 7 + 1] += 1

        states = g.groupby("day")["state"].first().sort_index()
        flags = g.groupby("day")[["shock", "labelled"]].any().astype(bool) if "shock" in g else None
        shock_days = set(flags.index[flags["shock"]]) if flags is not None else set()
        labelled_days = set(flags.index[flags["labelled"]]) if flags is not None else set()
        by_cause = {c: [0, 0] for c in CAUSES}  # cause -> [onsets, recovered]
        onsets, recovered, times, to_active = 0, 0, [], []
        prev = None
        days_list, state_list = list(states.index), list(states.values)
        for i, (d, s) in enumerate(zip(days_list, state_list, strict=True)):
            if s == "lapsed" and prev != "lapsed" and d <= days - RECOVERY_WINDOW:
                onsets += 1
                cause = onset_cause(int(d), shock_days, labelled_days)
                by_cause[cause][0] += 1
                later = list(zip(days_list[i + 1 :], state_list[i + 1 :], strict=True))
                if any(s2 == "active" and d2 - d <= RECOVERY_WINDOW for d2, s2 in later):
                    recovered += 1
                    by_cause[cause][1] += 1
                back = next((d2 for d2, s2 in later if s2 in ("recovering", "active")), None)
                if back is not None:
                    times.append(int(back - d))
                active_day = next((d2 for d2, s2 in later if s2 == "active"), None)
                if active_day is not None:
                    to_active.append(int(active_day - d))
            prev = s

        # numpy arrays, not Series: pandas 3 keeps empty text columns as strings and won't multiply them.
        mv = g[g["behaviour"] == "movement"]
        mv_out = mv["outcome"].to_numpy(dtype=object)
        credit = np.where(mv_out == "completed", 1.0, np.where(mv_out == "partial", 0.5, 0.0))
        minutes = mv["duration_min"].to_numpy(dtype=float) * credit
        mv_week = (mv["day"].to_numpy(dtype=int) - 1) // 7 + 1
        slp = g[g["behaviour"] == "sleep"]
        slp_week = (slp["day"].to_numpy(dtype=int) - 1) // 7 + 1
        slp_out = slp["outcome"].to_numpy(dtype=object)
        slp_done = slp_out == "completed"
        # Tier-weighted: a completed night earns tier / 4 (half for a partial), so harder sleep actions count more.
        slp_effort = slp["tier"].to_numpy(dtype=float) / 4 * np.where(
            slp_done, 1.0, np.where(slp_out == "partial", 0.5, 0.0)
        )
        churned_on = churn_day.get((seed, arm, pid))
        last_day = int(churned_on) if churned_on is not None else days
        rows.append({
            "seed": seed, "arm": arm, "persona_id": pid,
            **{f"active_w{k}": week_active[k] for k in range(1, weeks + 1)},
            "lapse_onsets": onsets, "lapses_recovered": recovered, "recovery_times": times, "to_active": to_active,
            **{f"onsets_{c}": by_cause[c][0] for c in CAUSES},
            **{f"recovered_{c}": by_cause[c][1] for c in CAUSES},
            "has_movement": len(mv) > 0, "has_sleep": len(slp) > 0,
            "minutes_w1": float(minutes[mv_week == 1].sum()), "minutes_w12": float(minutes[mv_week == 12].sum()),
            "sleep_w1": float(slp_done[slp_week == 1].sum()) / 7, "sleep_w12": float(slp_done[slp_week == 12].sum()) / 7,
            "sleep_effort_w1": float(slp_effort[slp_week == 1].sum()) / 7,
            "sleep_effort_w12": float(slp_effort[slp_week == 12].sum()) / 7,
            "churned": churned_on is not None,
            "messages": int(len(g) + checkins_sent.get((seed, arm, pid), 0)),
            "alive_weeks": last_day / 7,
            "quiet_messages": int(g["quiet"].sum()),
            "violations": int((g["violation"].fillna("") != "").sum()),
        })
    table = pd.DataFrame(rows)
    return table.merge(personas, on=["seed", "persona_id"], how="left")


def _group_metrics(t: pd.DataFrame, days: int) -> dict:
    weeks = days // 7
    out = {}
    for k in (4, 8, 12):
        out[f"persistence_w{k}"] = float((t[f"active_w{k}"] >= 3).mean()) if k <= weeks else float("nan")
    if weeks >= 12:
        out["persistence_all"] = float(((t["active_w4"] >= 3) & (t["active_w8"] >= 3) & (t["active_w12"] >= 3)).mean())
    else:
        out["persistence_all"] = float("nan")
    onsets = t["lapse_onsets"].sum()
    out["recovery_rate"] = float(t["lapses_recovered"].sum() / onsets) if onsets else float("nan")
    for c in CAUSES:
        n_c = t[f"onsets_{c}"].sum()
        out[f"recovery_{c}"] = float(t[f"recovered_{c}"].sum() / n_c) if n_c else float("nan")
    times = [x for ts in t["recovery_times"] for x in ts]
    out["time_to_recover"] = float(statistics.median(times)) if times else float("nan")
    to_active = [x for ts in t["to_active"] for x in ts]
    out["days_to_active"] = float(statistics.median(to_active)) if to_active else float("nan")
    mv, sl = t[t["has_movement"]], t[t["has_sleep"]]
    out["delta_minutes"] = float((mv["minutes_w12"] - mv["minutes_w1"]).mean()) if len(mv) else float("nan")
    out["delta_sleep"] = float((sl["sleep_w12"] - sl["sleep_w1"]).mean()) if len(sl) else float("nan")
    out["delta_sleep_effort"] = (
        float((sl["sleep_effort_w12"] - sl["sleep_effort_w1"]).mean()) if len(sl) else float("nan")
    )
    out["retention"] = float(1 - t["churned"].mean())
    out["messages_per_week"] = float(t["messages"].sum() / t["alive_weeks"].sum())
    out["quiet_messages"] = float(t["quiet_messages"].sum())
    out["quiet_share"] = float(t["quiet_messages"].sum() / max(1, t["messages"].sum()))
    out["safety_violations"] = float(t["violations"].sum())
    return out


def seed_metrics(table: pd.DataFrame, days: int) -> dict:
    """{arm: {"overall": metrics, "by_week": [...], "equity": {segment: {value: metrics}}, "recovery_times": [...]}}"""
    weeks = days // 7
    out = {}
    for arm, t in table.groupby("arm"):
        equity = {}
        for seg in SEGMENTS:
            equity[seg] = {
                str(v): {**_group_metrics(g, days), "n": len(g)} for v, g in t.groupby(seg)
            }
        out[arm] = {
            "overall": _group_metrics(t, days),
            "by_week": [float((t[f"active_w{k}"] >= 3).mean()) for k in range(1, weeks + 1)],
            "equity": equity,
            "recovery_times": [x for ts in t["to_active"] for x in ts],  # lapse -> active, for the chart
        }
    return out


# ---------- across seeds ----------


def aggregate(per_seed: dict[int, dict]) -> dict:
    seeds = sorted(per_seed)
    arms = sorted({a for s in seeds for a in per_seed[s]})
    result: dict = {"seeds": seeds, "arms": {}, "persistence_by_week": {}, "equity": {}, "equity_gap": {},
                    "comparisons": {}, "recovery_times": {}}
    for arm in arms:
        runs = [per_seed[s][arm] for s in seeds if arm in per_seed[s]]
        result["arms"][arm] = {m: summarise([r["overall"][m] for r in runs]) for m in METRICS}
        n_weeks = len(runs[0]["by_week"])
        result["persistence_by_week"][arm] = [summarise([r["by_week"][k] for r in runs]) for k in range(n_weeks)]
        result["recovery_times"][arm] = [x for r in runs for x in r["recovery_times"]]
        result["equity"][arm], result["equity_gap"][arm] = {}, {}
        for seg in SEGMENTS:
            values = sorted({v for r in runs for v in r["equity"][seg]})
            result["equity"][arm][seg] = {
                v: {m: summarise([r["equity"][seg][v][m] for r in runs if v in r["equity"][seg]]) for m in EQUITY_METRICS}
                | {"n": statistics.fmean([r["equity"][seg][v]["n"] for r in runs if v in r["equity"][seg]])}
                for v in values
            }
            gaps = {m: [] for m in EQUITY_METRICS}
            for r in runs:
                groups = [g for g in r["equity"][seg].values() if g["n"] >= MIN_SEGMENT_SIZE]
                for m in EQUITY_METRICS:
                    vals = [g[m] for g in groups if not math.isnan(g[m])]
                    if len(vals) >= 2:
                        gaps[m].append(max(vals) - min(vals))
            result["equity_gap"][arm][seg] = {m: summarise(v) for m, v in gaps.items()}
    for a, b in COMPARISONS:
        if a in arms and b in arms:
            common = [s for s in seeds if a in per_seed[s] and b in per_seed[s]]
            result["comparisons"][f"{a}_vs_{b}"] = {
                m: summarise([per_seed[s][a]["overall"][m] - per_seed[s][b]["overall"][m] for s in common])
                for m in COMPARE_METRICS
            }
    return result
