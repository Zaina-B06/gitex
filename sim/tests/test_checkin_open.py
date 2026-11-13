"""Pre-registered rule (ASSUMPTIONS.md, "Check-ins answered only on open days")."""

import json

import pytest
from sim import _merge, load_config
from sim.run import simulate

CFG = load_config("baseline")
STRICT = _merge(CFG, {"traits": {"checkin_needs_open_app": True}})


def _answered_days_open(events):
    """For every answered check-in: was the app open that persona-day? (Days with no action row, e.g. movement-only
    and ill, carry no app_open value and are left out.)"""
    opens = events[events["kind"] == "action"].groupby(["arm", "persona_id", "day"])["app_open"].first()
    answered = events[events["kind"] == "checkin_answered"]
    keys = [(r.arm, r.persona_id, r.day) for r in answered.itertuples()]
    return [bool(opens[k]) for k in keys if k in opens.index]


@pytest.fixture(scope="module")
def runs():
    any_day = simulate(30, 60, [1], ["A", "A0", "B", "C"], CFG, workers=1, quiet=True)
    strict = simulate(30, 60, [1], ["A", "A0", "B", "C"], STRICT, workers=1, quiet=True)
    return any_day, strict


def test_default_is_off_so_run_007_reproduces():
    assert CFG["traits"]["checkin_needs_open_app"] is False


def test_strict_rule_answers_only_on_open_days(runs):
    any_day, strict = runs
    assert not all(_answered_days_open(any_day[0]))  # the old world does answer on closed days (not vacuous)
    flags = _answered_days_open(strict[0])
    assert flags and all(flags)


def test_static_arms_are_unaffected(runs):
    """Validity check from the pre-registration: A and A0 send no check-ins, so their metrics can't change."""
    any_day, strict = runs
    for arm in ("A", "A0"):
        assert json.dumps(any_day[2]["arms"][arm], sort_keys=True) == json.dumps(strict[2]["arms"][arm], sort_keys=True)
