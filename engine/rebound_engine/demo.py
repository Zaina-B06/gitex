"""30-day demo for one synthetic user: python -m rebound_engine.demo --days 30 --seed 1

Outcome generator (simple, seeded):
  - days 11-14: motivation dip, 25% full completion
  - days 15-18: forced lapse, no response at all
  - other days: 80% full (minus 5% per tier above 1), 10% partial, 5% no response, rest skipped
When a check-in is due and the user is responding, they answer it with a random barrier.
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
    for day in range(1, days + 1):
        note = ""
        if engine.get_state(uid).checkin_due and day not in LAPSE_DAYS:
            barrier = rng.choice(DEMO_BARRIERS)
            engine.checkin(uid, [barrier])
            note = f"check-in: {barrier.value}"
        action = engine.today(uid, day).action
        if action is None:
            state = engine.get_state(uid)
            outcome = "-"
        else:
            outcome = simulate_outcome(rng, day, action.tier)
            state = engine.record(Event(user_id=uid, day=day, type=outcome, action_id=action.id))
        rows.append(
            {
                "day": day,
                "behaviour": action.behaviour.value if action else "-",
                "tier": action.tier if action else "-",
                "action": action.id if action else "-",
                "outcome": str(outcome),
                "h_move": state.habit_strength[Behaviour.movement],
                "h_sleep": state.habit_strength[Behaviour.sleep],
                "state": state.engagement_state.value,
                "note": note,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebound engine 30-day demo")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()
    header = f"{'day':>3}  {'behaviour':<9} {'tier':>4}  {'action':<26} {'outcome':<12} {'H_move':>6} {'H_sleep':>7}  {'state':<10} note"
    print(header)
    print("-" * len(header))
    for r in run(args.days, args.seed):
        print(
            f"{r['day']:>3}  {r['behaviour']:<9} {r['tier']!s:>4}  {r['action']:<26} {r['outcome']:<12}"
            f" {r['h_move']:>6.3f} {r['h_sleep']:>7.3f}  {r['state']:<10} {r['note']}"
        )


if __name__ == "__main__":
    main()
