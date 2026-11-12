from typing import ClassVar

import numpy as np
import pytest
import sim.arms
import yaml
from rebound_engine import config as engine_config
from rebound_engine.models import ContextFlag
from sim import SIM_DIR, _merge, load_config
from sim.metrics import onset_cause
from sim.personas import generate_personas
from sim.run import run_seed, simulate
from sim.sweep import get_path, set_path, sweep
from sim.user_model import PersonaSim

CFG = load_config("baseline")
SCENARIOS = yaml.safe_load((SIM_DIR / "scenarios.yaml").read_text(encoding="utf-8"))


def _flatten(d: dict, prefix: str = "") -> dict:
    out = {}
    for k, v in d.items():
        path = f"{prefix}{k}"
        if isinstance(v, dict) and v:
            out.update(_flatten(v, path + "."))
        else:
            out[path] = v
    return out


# ---------- scenarios ----------


@pytest.mark.parametrize("name", list(SCENARIOS))
def test_each_scenario_changes_only_the_parameters_it_declares(name):
    base = _flatten(load_config("baseline"))
    cfg = _flatten(load_config(name))
    declared = _flatten(SCENARIOS[name] or {})
    assert set(declared) <= set(base), f"{name} declares keys that don't exist: {set(declared) - set(base)}"
    changed = {k for k in base if cfg.get(k) != base[k]}
    assert changed == set(declared)
    assert set(cfg) == set(base)  # nothing added either


def test_harsh_attrition_and_seven_scenarios_exist():
    assert {"baseline", "ramadan_heavy", "hot_summer", "low_checkin", "high_dropout", "shock_heavy",
            "harsh_attrition"} <= set(SCENARIOS)


# ---------- unlabelled shocks ----------


class SpyEngine(sim.arms.Engine):
    """Records every call the simulator makes into the engine."""

    calls: ClassVar[list] = []

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if callable(attr) and not name.startswith("_") and name in (
            "onboard", "today", "record", "checkin", "set_context", "get_state", "events"
        ):
            def wrapper(*args, **kwargs):
                SpyEngine.calls.append((name, repr(args), repr(kwargs)))
                return attr(*args, **kwargs)
            return wrapper
        return attr


def test_unlabelled_shocks_never_reach_the_engine(monkeypatch):
    monkeypatch.setattr(sim.arms, "Engine", SpyEngine)
    SpyEngine.calls = []
    cfg = _merge(CFG, {"disruptions": {"shocks": {"rate": 6.0}}})
    events, _, _ = simulate(8, 45, [1], ["B", "C"], cfg, workers=1, quiet=True)
    assert events.loc[events["kind"] == "action", "shock"].any()  # shocks did happen
    assert SpyEngine.calls
    for name, args, kwargs in SpyEngine.calls:
        assert "shock" not in (args + kwargs).lower()
        if name == "set_context":
            assert any(f.value in args for f in (ContextFlag.heat, ContextFlag.ramadan, ContextFlag.illness))


def test_shock_lowers_motivation_on_its_days_only():
    traits = generate_personas(1, 1, CFG)[0][1]
    cfg = _merge(CFG, {"disruptions": {"shocks": {"rate": 30.0, "length": [3, 3], "motivation_drop": [1.0, 1.0]}}})
    sim_ = PersonaSim(traits, cfg, 90, np.random.default_rng(0), np.random.default_rng(1), np.random.default_rng(2))
    assert sim_.shocks
    shock_day = min(sim_.shocks)
    sim_.start_day(shock_day)
    assert sim_.shock_today()
    assert sim_.motivation_today() == pytest.approx(
        sim_.motivation - sim_.shocks[shock_day]
        - (cfg["disruptions"]["workload"]["motivation_drop"] if shock_day in sim_.workload else 0.0)
    )


def test_shocks_use_their_own_random_stream():
    """Adding shocks must not reshuffle the labelled disruption schedule."""
    traits = generate_personas(1, 1, CFG)[0][1]
    no_shocks = _merge(CFG, {"disruptions": {"shocks": {"rate": 0.0}}})
    a = PersonaSim(traits, no_shocks, 90, np.random.default_rng(5), np.random.default_rng(6), np.random.default_rng(7))
    b = PersonaSim(traits, CFG, 90, np.random.default_rng(5), np.random.default_rng(6), np.random.default_rng(7))
    assert (a.illness, a.travel, a.workload) == (b.illness, b.travel, b.workload)


def test_onset_cause():
    assert onset_cause(20, shock_days={15}, labelled_days={18}) == "shock"
    assert onset_cause(20, shock_days={5}, labelled_days={13}) == "labelled"
    assert onset_cause(20, shock_days={12}, labelled_days={21}) == "none"


# ---------- sweep ----------


def test_set_path_refuses_typos_and_copies():
    assert get_path(set_path(CFG, "traits.success_feedback", 0.1), "traits.success_feedback") == 0.1
    assert CFG["traits"]["success_feedback"] == 0.05  # original untouched
    with pytest.raises(ValueError):
        set_path(CFG, "traits.succes_feedback", 0.1)
    with pytest.raises(ValueError):
        set_path(CFG, "engine_overrides.NOT_A_CONSTANT", 1)
    assert get_path(CFG, "engine_overrides.STEP_UP_SUCCESSES") == engine_config.STEP_UP_SUCCESSES


def test_engine_override_is_applied_and_restored():
    before = engine_config.STEP_UP_SUCCESSES
    seen = []
    original = sim.arms._run_engine

    def spy(*args, **kwargs):
        seen.append(engine_config.STEP_UP_SUCCESSES)
        return original(*args, **kwargs)

    sim.arms._run_engine = spy
    try:
        run_seed((1, 2, 10, ["B"], _merge(CFG, {"engine_overrides": {"STEP_UP_SUCCESSES": before + 2}, "days": 10})))
    finally:
        sim.arms._run_engine = original
    assert seen and all(v == before + 2 for v in seen)
    assert engine_config.STEP_UP_SUCCESSES == before
    with pytest.raises(ValueError):
        run_seed((1, 2, 10, ["B"], _merge(CFG, {"engine_overrides": {"NOPE": 1}})))


def test_tiny_sweep_records_every_gap():
    data = sweep({"traits.success_feedback": [0.0, 0.1]}, n=6, days=84, seeds=[1], base_cfg=CFG, workers=1, quiet=True)
    assert [r["value"] for r in data["results"]] == [0.0, 0.1]
    assert data["baseline"]["traits.success_feedback"] == 0.05
    for r in data["results"]:
        assert set(r["gaps"]) == {"C_vs_A.persistence_w12", "C_vs_A0.persistence_w12", "C_vs_A.recovery_rate",
                                  "C_vs_A0.recovery_rate", "C_vs_A.retention", "C_vs_A0.retention",
                                  "C_vs_A0.delta_minutes", "C_vs_A0.delta_sleep_effort"}
