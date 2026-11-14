"""Task 05 Part B added behaviours, barriers and BCT codes to the engine; Part E added family steps. Personas must not
see them, or every persona's random draws would change and run_011 would no longer reproduce."""

import importlib
import json

import pytest
from rebound_engine import actions as actions_module
from rebound_engine import engine as engine_module
from rebound_engine.models import Behaviour
from sim import load_config
from sim.personas import BARRIERS, BCT_CODES

PART_E_TAGS = {"family", "family_iftar", "caregiver"}
# Reloaded in dependency order, so anything they compute from the library at import time is recomputed too.
SIM_MODULES = ("sim.personas", "sim.user_model", "sim.arms", "sim.run")


def test_persona_barriers_are_the_original_eight():
    assert BARRIERS == ["time", "energy_fatigue", "illness_pain", "schedule_change", "environment",
                        "low_motivation", "social_family", "forgot"]


def test_persona_bct_codes_are_the_run_011_movement_and_sleep_codes():
    codes = {a.bct_code for a in actions_module.default_library()
             if a.behaviour in (Behaviour.movement, Behaviour.sleep) and not PART_E_TAGS & set(a.tags)}
    assert BCT_CODES == sorted(codes) == ["1.4", "2.3", "7.1", "8.1", "8.3", "8.7"]


def _short_run(monkeypatch: pytest.MonkeyPatch, library: tuple) -> str:
    try:
        with monkeypatch.context() as m:
            m.setattr(actions_module, "default_library", lambda: library)
            m.setattr(engine_module, "default_library", lambda: library)
            run = [importlib.reload(importlib.import_module(name)) for name in SIM_MODULES][-1]
            metrics = run.simulate(30, 20, [1], ["A", "A0", "B", "C"], load_config("baseline"), workers=1, quiet=True)[2]
    finally:
        for name in SIM_MODULES:  # back to the real library for the other tests
            importlib.reload(importlib.import_module(name))
    return json.dumps(metrics, sort_keys=True)


def test_family_actions_are_invisible_to_the_simulator(monkeypatch):
    """Every arm (incl. the streak app A and the kind fixed plan A0) gives identical results with and without the
    Part E family actions in the library. Personas have no household, so nothing may change."""
    full = actions_module.default_library()
    without = tuple(a for a in full if not PART_E_TAGS & set(a.tags))
    assert len(without) < len(full)  # the family actions are really there
    assert _short_run(monkeypatch, full) == _short_run(monkeypatch, without)
