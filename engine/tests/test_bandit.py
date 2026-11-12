import random

import pytest

from rebound_engine.actions import default_library, filter_actions
from rebound_engine.models import (
    Behaviour,
    Context,
    ContextFlag,
    Event,
    EventType,
    ScheduledAction,
    TimeWindow,
    UserState,
)
from rebound_engine.policy import (
    ThompsonBandit,
    arm_key,
    choose_action,
    update_arm,
)
from rebound_engine.safety import screening_flags
from rebound_engine.state import initial_state

OUTCOMES = [EventType.completed, EventType.partial, EventType.skipped, EventType.no_response]


def _empty_state() -> UserState:
    return UserState(user_id="t", habit_strength={}, current_tier={}, successes_at_tier={}, fails_at_tier={})


def test_toy_three_arm_problem_finds_best_arm():
    lib = default_library()[:3]
    arms = [ScheduledAction(action=a, time_window=TimeWindow.morning, hour=8, explanation_id=a.id) for a in lib]
    true_rate = {lib[0].id: 0.2, lib[1].id: 0.5, lib[2].id: 0.8}
    rng = random.Random(7)
    bandit = ThompsonBandit(random.Random(1))
    state = _empty_state()
    picks = []
    for _ in range(300):
        arm = bandit.select(arms, state)
        picks.append(arm.action.id)
        reward = 1.0 if rng.random() < true_rate[arm.action.id] else 0.0
        update_arm(state, arm_key(arm.action.id, arm.time_window), reward)
    after_200 = picks[200:]
    assert after_200.count(lib[2].id) / len(after_200) > 0.7


def test_fractional_update():
    state = _empty_state()
    update_arm(state, "x@morning", 0.5)
    assert state.bandit_params["x@morning"] == [1.5, 1.5]


class SpyBandit(ThompsonBandit):
    """Checks every arm it's offered is safe, and that it returns one of them."""

    def __init__(self, rng, profile):
        super().__init__(rng)
        self.profile = profile
        self.calls = 0

    def select(self, arms, user_state):
        for arm in arms:
            ctx = Context(flags=user_state.context_flags, hour=arm.hour)
            assert arm.action in filter_actions(self.profile, user_state, ctx)
            assert arm.action.tier <= user_state.current_tier[arm.action.behaviour]
        choice = super().select(arms, user_state)
        assert choice in arms
        self.calls += 1
        return choice


@pytest.mark.parametrize(
    "groups",
    [
        {},
        {"screening": {"pregnant": "yes"}},
        {"screening": {"mobility_limitation": "some", "chest_pain": True}},
        {"preferences": {"quiet_hours": {"start": "12:00", "end": "15:00"}}},
    ],
)
def test_bandit_only_returns_allowed_arms(make_engine, make_payload, make_profile, groups):
    profile = make_profile(**groups)
    spy = SpyBandit(random.Random(3), profile)
    engine = make_engine(bandit=spy, policy_mode="bandit")
    uid = engine.onboard(make_payload(**groups), user_id="test-user").user_id
    rng = random.Random(5)
    for day in range(1, 41):
        if day == 10:
            engine.set_context(uid, ContextFlag.heat, True)
        if day == 20:
            engine.set_context(uid, ContextFlag.ramadan, True)
        for s in engine.today(uid, day).actions:
            engine.record(Event(user_id=uid, day=day, type=rng.choice(OUTCOMES), action_id=s.action.id))
    assert spy.calls > 40


def _first_movement_bct(make_engine, make_payload, helpers, seed):
    engine = make_engine(policy_mode="bandit", rng=random.Random(seed))
    payload = make_payload(
        basics={"goals": ["movement"]},
        baseline={"active_days_per_week": 3},  # tier 2: one of three actions is 8.7 Graded tasks
        history={"past_helpers": helpers},
    )
    uid = engine.onboard(payload, user_id=f"u{seed}").user_id
    return engine.today(uid, 1).actions[0].action.bct_code


def test_warm_start_raises_share_of_helper_matched_arm(make_engine, make_payload):
    n = 300
    with_helper = sum(_first_movement_bct(make_engine, make_payload, ["small_steps"], s) == "8.7" for s in range(n))
    without = sum(_first_movement_bct(make_engine, make_payload, [], s) == "8.7" for s in range(n))
    assert with_helper / n > without / n + 0.05


def test_completion_updates_the_shown_arm(make_engine, make_payload):
    engine = make_engine(policy_mode="bandit", rng=random.Random(2))
    uid = engine.onboard(make_payload(basics={"goals": ["movement"]}), user_id="u").user_id
    shown = engine.today(uid, 1).actions[0]
    key = arm_key(shown.action.id, shown.time_window)
    before = list(engine.get_state(uid).bandit_params[key])
    engine.record(Event(user_id=uid, day=1, type=EventType.completed, action_id=shown.action.id))
    assert engine.get_state(uid).bandit_params[key] == [before[0] + 1, before[1]]


def test_same_seed_same_choices(make_engine, make_payload):
    def run(seed):
        engine = make_engine(policy_mode="bandit", rng=random.Random(seed))
        uid = engine.onboard(make_payload(), user_id="u").user_id
        out = []
        for day in range(1, 15):
            for s in engine.today(uid, day).actions:
                out.append((s.action.id, s.time_window))
                engine.record(Event(user_id=uid, day=day, type=EventType.skipped, action_id=s.action.id))
        return out

    assert run(4) == run(4)


def test_unknown_policy_mode_rejected(make_engine):
    with pytest.raises(ValueError):
        make_engine(policy_mode="magic")


# ---------- quiet hours ----------


def test_rules_mode_skips_a_quiet_default_window(make_profile):
    profile = make_profile(preferences={"quiet_hours": {"start": "12:00", "end": "15:00"}})
    state = initial_state(profile, screening_flags(profile))
    state.time_window = TimeWindow.afternoon  # 13:00 is quiet
    pick = choose_action(profile, state, Behaviour.movement)
    assert pick.time_window == TimeWindow.evening and pick.hour == 20


def test_all_windows_quiet_moves_to_end_of_quiet_hours(make_profile):
    profile = make_profile(preferences={"quiet_hours": {"start": "05:00", "end": "23:00"}})
    state = initial_state(profile, screening_flags(profile))
    pick = choose_action(profile, state, Behaviour.movement)
    assert pick.time_window == TimeWindow.morning and pick.hour == 23


def test_quiet_hours_crossing_midnight(make_engine, make_payload):
    # Night-shift style: asleep 06:00-14:00, so morning (wake 14:30 -> 15:00) is fine, afternoon (13:00) isn't.
    engine = make_engine(policy_mode="bandit", rng=random.Random(9))
    payload = make_payload(
        basics={"usual_wake_time": "14:30", "usual_sleep_time": "06:00"},
        preferences={"quiet_hours": {"start": "06:00", "end": "14:00"}},
    )
    uid = engine.onboard(payload, user_id="u").user_id
    for day in range(1, 30):
        for s in engine.today(uid, day).actions:
            assert not 6 <= s.hour < 14
            engine.record(Event(user_id=uid, day=day, type=EventType.skipped, action_id=s.action.id))
