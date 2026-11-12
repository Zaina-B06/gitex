import random

import pytest

from rebound_engine.models import Behaviour, DayLog, DayOutcome, EngagementState
from rebound_engine.safety import screening_flags
from rebound_engine.state import compute_engagement_state, initial_state, update_habit_strength

CODES = {
    "C": DayOutcome.completed,
    "H": DayOutcome.partial,
    "S": DayOutcome.skipped,
    "N": DayOutcome.no_response,
    "P": DayOutcome.paused,
    "I": DayOutcome.illness,
}


def states_for(seq: str) -> list[EngagementState]:
    history: list[DayLog] = []
    state = EngagementState.active
    out = []
    for i, c in enumerate(seq):
        history.append(DayLog(day=i + 1, outcome=CODES[c]))
        state = compute_engagement_state(history, state)
        out.append(state)
    return out


def dedupe(states: list[EngagementState]) -> list[EngagementState]:
    return [s for i, s in enumerate(states) if i == 0 or s != states[i - 1]]


# ---------- habit strength ----------


def test_one_miss_after_ten_completions_keeps_h_above_half():
    h = 0.0
    for _ in range(10):
        h = update_habit_strength(h, DayOutcome.completed)
    h = update_habit_strength(h, DayOutcome.skipped)
    assert h > 0.5


def test_h_stays_between_0_and_1():
    rng = random.Random(0)
    h = 0.0
    for _ in range(1000):
        h = update_habit_strength(h, rng.choice(list(DayOutcome)))
        assert 0.0 <= h <= 1.0
    assert update_habit_strength(1.0, DayOutcome.completed) <= 1.0
    assert update_habit_strength(0.0, DayOutcome.no_response) >= 0.0


def test_partial_counts_half():
    assert update_habit_strength(0.0, DayOutcome.partial) == pytest.approx(0.05)


def test_paused_and_illness_days_leave_h_unchanged():
    assert update_habit_strength(0.7, DayOutcome.paused) == 0.7
    assert update_habit_strength(0.7, DayOutcome.illness) == 0.7


def test_lapse_decays_but_never_resets():
    h = 0.0
    for _ in range(10):
        h = update_habit_strength(h, DayOutcome.completed)
    for _ in range(4):
        h = update_habit_strength(h, DayOutcome.no_response)
    assert h > 0.0


# ---------- engagement state ----------


def test_full_cycle_active_drifting_lapsed_recovering_active():
    states = states_for("C" * 7 + "S" * 6 + "C" * 4)
    assert dedupe(states) == [
        EngagementState.active,
        EngagementState.drifting,
        EngagementState.lapsed,
        EngagementState.recovering,
        EngagementState.active,
    ]


def test_partials_count_as_completions():
    assert states_for("HHHHHHH")[-1] == EngagementState.active


def test_three_consecutive_no_responses_is_lapsed():
    states = states_for("C" * 7 + "NNN")
    assert states[-2] == EngagementState.active  # 5/7 completions, only 2 no-responses so far
    assert states[-1] == EngagementState.lapsed


def test_paused_and_illness_days_dont_count():
    assert states_for("C" * 7 + "P" * 5)[-1] == EngagementState.active
    assert states_for("C" * 7 + "I" * 5)[-1] == EngagementState.active


def test_two_goals_count_each_action():
    # Movement done, sleep skipped every day: 7/14 = 0.5 < 4/7 -> drifting.
    history = [DayLog(day=d, outcome=o) for d in range(1, 8) for o in (DayOutcome.completed, DayOutcome.skipped)]
    assert compute_engagement_state(history, EngagementState.active) == EngagementState.drifting


def test_silent_day_needs_every_action_unanswered():
    history = [DayLog(day=d, outcome=DayOutcome.completed) for d in range(1, 8)]
    for d in (8, 9, 10):
        history += [DayLog(day=d, outcome=DayOutcome.no_response), DayLog(day=d, outcome=DayOutcome.skipped)]
    assert compute_engagement_state(history, EngagementState.active) != EngagementState.lapsed
    for d in (8, 9, 10):
        history.append(DayLog(day=d + 3, outcome=DayOutcome.no_response))
    assert compute_engagement_state(history, EngagementState.active) == EngagementState.lapsed


@pytest.mark.parametrize(
    ("active_days", "quality", "h_move", "h_sleep"),
    [(0, 1, 0.0, 0.0), (7, 5, 0.5, 0.5), (2, 3, 0.5 * 2 / 7, 0.25)],
)
def test_initial_h_from_baseline(make_profile, active_days, quality, h_move, h_sleep):
    profile = make_profile(baseline={"active_days_per_week": active_days, "sleep_quality_self": quality})
    state = initial_state(profile, screening_flags(profile))
    assert state.habit_strength[Behaviour.movement] == pytest.approx(h_move)
    assert state.habit_strength[Behaviour.sleep] == pytest.approx(h_sleep)


def test_lapsed_user_needs_two_of_four_to_recover():
    states = states_for("S" * 7 + "C")
    assert states[-1] == EngagementState.lapsed
    assert states_for("S" * 7 + "CC")[-1] == EngagementState.recovering
