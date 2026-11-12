"""30-day demo for one synthetic user: python -m rebound_engine.demo --days 30 --seed 1

Each day the user gets one movement and one sleep action. Outcome generator (simple, seeded, per action):
  - days 11-14: motivation dip, 25% full completion
  - days 15-18: forced lapse, no response at all
  - other days: 80% full (minus 5% per tier above 1), 10% partial, 5% no response, rest skipped
A check-in is sent when the state enters drifting or lapsed; the user answers it (random barrier)
the next day they respond, i.e. not during the lapse.
"""

import argparse
import random

from .engine import Engine
from .models import Barrier, Behaviour, Event, EventType, OnboardingPayload

DIP_DAYS = range(11, 15)
LAPSE_DAYS = range(15, 19)
DEMO_BARRIERS = (Barrier.time, Barrier.energy_fatigue, Barrier.forgot, Barrier.low_motivation)


def demo_payload() -> OnboardingPayload:
    return OnboardingPayload.model_validate(
        {
            "basics": {
                "language": "en",
                "age_years": 34,
                "sex": "female",
                "goals": ["movement", "sleep"],
                "schedule_type": "office",
                "usual_wake_time": "06:30",
                "usual_sleep_time": "23:00",
            },
            "screening": {
                "heart_condition_or_high_bp": False,
                "chest_pain": False,
                "dizziness_or_fainting": False,
                "other_long_term_condition": False,
                "prescribed_medication": False,
                "bone_joint_muscle_problem": False,
                "supervised_exercise_only": False,
                "pregnant": "no",
                "mobility_limitation": "none",
            },
            "baseline": {"active_days_per_week": 2, "sleep_hours_typical": 6.0, "sleep_quality_self": 3},
            "history": {"tried_before": True, "past_helpers": ["small_steps"], "past_stop_reasons": ["time"],
                        "motivation_reason": "Keep up with my kids"},
        }
    )


def simulate_outcome(rng: random.Random, day: int, tier: int) -> EventType:
    if day in LAPSE_DAYS:
        return EventType.no_response
    p_full = 0.25 if day in DIP_DAYS else 0.80 - 0.05 * (tier - 1)
    r = rng.random()
    if r < p_full:
        return EventType.completed
    if r < p_full + 0.10:
        return EventType.partial
    if r < p_full + 0.15:
        return EventType.no_response
    return EventType.skipped


def run(days: int = 30, seed: int = 1) -> list[dict]:
    rng = random.Random(seed)
    engine = Engine()
    uid = engine.onboard(demo_payload(), user_id="demo-user").user_id
    rows = []
    prev_state = engine.get_state(uid).engagement_state
    for day in range(1, days + 1):
        notes = []
        if engine.get_state(uid).checkin_due and day not in LAPSE_DAYS:
            barrier = rng.choice(DEMO_BARRIERS)
            engine.checkin(uid, [barrier])
            notes.append(f"check-in answered: {barrier.value}")
        row: dict = {"day": day}
        for b in Behaviour:
            row[b.value] = row[f"{b.value}_outcome"] = "-"
        state = engine.get_state(uid)
        for scheduled in engine.today(uid, day).actions:
            a = scheduled.action
            outcome = simulate_outcome(rng, day, a.tier)
            state = engine.record(Event(user_id=uid, day=day, type=outcome, action_id=a.id))
            row[a.behaviour.value] = a.id
            row[f"{a.behaviour.value}_outcome"] = outcome.value
        if state.engagement_state != prev_state and state.checkin_due:
            notes.append("check-in sent")
        prev_state = state.engagement_state
        row |= {
            "h_move": state.habit_strength[Behaviour.movement],
            "h_sleep": state.habit_strength[Behaviour.sleep],
            "state": state.engagement_state.value,
            "note": "; ".join(notes),
        }
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebound engine 30-day demo")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()
    header = (
        f"{'day':>3}  {'movement':<26} {'outcome':<11}  {'sleep':<26} {'outcome':<11}"
        f" {'H_move':>6} {'H_sleep':>7}  {'state':<10} note"
    )
    print(header)
    print("-" * len(header))
    for r in run(args.days, args.seed):
        print(
            f"{r['day']:>3}  {r['movement']:<26} {r['movement_outcome']:<11}  {r['sleep']:<26}"
            f" {r['sleep_outcome']:<11} {r['h_move']:>6.3f} {r['h_sleep']:>7.3f}  {r['state']:<10} {r['note']}"
        )


if __name__ == "__main__":
    main()
