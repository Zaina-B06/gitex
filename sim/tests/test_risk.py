"""Lapse-risk training pipeline (Task 02b, Drop A)."""

import pandas as pd
import pytest
import sim.arms
from rebound_engine.models import Event, UserProfile, UserState
from rebound_engine.risk import FEATURE_NAMES, load_risk_model, save_risk_model
from sim import load_config
from sim.train_risk import add_labels, generate, lapse_onsets, split, train_and_evaluate, warning_times

CFG = load_config("baseline")
META = {"seed", "persona_id", "day", "engine_state"}


def test_feature_function_only_receives_engine_objects(monkeypatch):
    seen = []
    original = sim.arms.compute_features

    def spy(profile, state, events, day):
        assert isinstance(profile, UserProfile) and isinstance(state, UserState)
        assert all(isinstance(e, Event) for e in events) and isinstance(day, int)
        seen.append(day)
        return original(profile, state, events, day)

    monkeypatch.setattr(sim.arms, "compute_features", spy)
    feats, _ = generate(4, 20, [21], CFG, workers=1, quiet=True)
    assert seen and len(feats) == len(seen)
    assert set(feats.columns) == set(FEATURE_NAMES) | META  # nothing hidden (no shock, app_open, motivation...)


def _states(seq: str, seed=21, pid=0) -> pd.DataFrame:
    names = {"a": "active", "d": "drifting", "l": "lapsed", "r": "recovering"}
    return pd.DataFrame({"seed": seed, "persona_id": pid, "day": range(1, len(seq) + 1),
                         "engine_state": [names[c] for c in seq]})


def test_labels_look_seven_days_ahead():
    df = add_labels(_states("aaaaadlllraaaaaaaaaa"), days=20)  # lapse onset on day 7
    lab = dict(zip(df["day"], df["label"], strict=True))
    assert all(lab[d] for d in range(1, 7))  # days 1-6: day 7 is within the next 7 days
    assert not lab[10] and not lab[11]  # recovering/active after the lapse, none ahead
    valid = dict(zip(df["day"], df["valid"], strict=True))
    assert not valid[7] and not valid[8]  # already lapsed
    assert not valid[14] and valid[13]  # day 14 + 7 > 20: no full window


def test_lapse_onsets_and_warning_time():
    df = _states("aaaaadlllraaaaaaaaaa")
    onsets = lapse_onsets(df)
    assert onsets == [(21, 0, 7)]
    frame = df[df["engine_state"] != "lapsed"].reset_index(drop=True)
    alerts = frame["day"].isin([3, 5]).to_numpy()
    w = warning_times(frame, alerts, onsets)
    assert w["caught"] == 1 and w["median_warning_days"] == 4  # first alert on day 3, lapse on day 7


def test_split_keeps_personas_apart():
    df = pd.concat([_states("aaaa", seed=s, pid=p) for s in (21, 22, 23) for p in range(3)])
    tr, va, te = split(df, [21], [22], [23])
    keys = [set(zip(f["seed"], f["persona_id"], strict=True)) for f in (tr, va, te)]
    assert not (keys[0] & keys[1]) and not (keys[0] & keys[2]) and not (keys[1] & keys[2])
    with pytest.raises(ValueError):
        split(df, [21, 22], [22], [23])


def test_model_saves_loads_and_predicts_deterministically(tmp_path):
    feats, personas = generate(25, 60, [21, 22, 23], CFG, workers=1, quiet=True)
    model, metrics, _ = train_and_evaluate(feats, personas, 60, [21], [22], [23], 0.15, quiet=True)
    path = tmp_path / "risk.joblib"
    save_risk_model(model, path)
    rows = [dict(zip(FEATURE_NAMES, r, strict=True)) for r in feats[list(FEATURE_NAMES)].head(50).to_numpy(float)]
    a, b = load_risk_model(path), load_risk_model(path)
    assert a.predict_many(rows) == b.predict_many(rows) == model.predict_many(rows)
    again, _, _ = train_and_evaluate(feats, personas, 60, [21], [22], [23], 0.15, quiet=True)
    assert again.predict_many(rows) == model.predict_many(rows)  # retraining is deterministic too
    assert len(a.explain(rows[0])) <= 3
    assert {"drifting_rule", "completion_heuristic", "logistic", "gradient_boosting"} <= set(metrics["test"])
