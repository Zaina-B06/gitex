"""Demo-only data and shapes (DEMO_MODE=true): time-travel patterns and seeded synthetic personas."""

import random
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from rebound_engine.demo import demo_payload
from rebound_engine.models import Behaviour, EngagementState

OUTCOMES = ("completed", "partial", "skipped", "no_response")
# P(completed, partial, skipped, no answer) per action per day. Demo-only numbers, not the simulator's model.
PATTERNS: dict[str, tuple[float, float, float, float]] = {
    "good": (0.85, 0.10, 0.05, 0.0),
    "mixed": (0.45, 0.15, 0.20, 0.20),
    "lapse": (0.0, 0.0, 0.0, 1.0),
}
PERSONA_WARMUP_DAYS = 7  # seeded personas start with a week of "good" days, so there's a habit to lapse from
ORG_SIZE = 12
ORG_DAYS = 14
ORG_PATTERNS = ("good", "mixed", "lapse")  # org users cycle through these, so aggregates show a spread


class AdvanceIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    days: int = Field(ge=1, le=60)
    pattern: Literal["good", "lapse", "mixed"]
    scenario: Literal["ramadan", "heat"] | None = None  # turned on for the user (and left on)


class DayRow(BaseModel):
    day: int
    outcomes: dict[str, str]  # action id -> outcome ("no_response" = left unanswered)
    engagement_state: EngagementState  # as of the end of this day's answers
    habit_strength: dict[Behaviour, float]
    checkin_due: bool


class SeedPersona(BaseModel):
    name: str
    user_id: str
    token: str


class SeedOut(BaseModel):
    personas: list[SeedPersona]
    org_id: str
    org_size: int


def _body(**groups: dict[str, Any]) -> dict[str, Any]:
    body = demo_payload().model_dump(mode="json")
    for group, fields in groups.items():
        body[group] = {**(body.get(group) or {}), **fields}
    return body


DEMO_PERSONAS: list[tuple[str, dict[str, Any]]] = [
    ("Ahmed, night-shift worker", _body(
        basics={"language": "ar", "sex": "male", "age_years": 41, "schedule_type": "shift",
                "usual_wake_time": "13:00", "usual_sleep_time": "05:00"},
        screening={"pregnant": None},
        history={"motivation_reason": "أريد أن ألعب مع أطفالي"},
        preferences={"fasting_ramadan": True},
    )),
    ("Sara, office worker", _body(basics={"age_years": 29})),
    ("Mariam, uses a wheelchair", _body(
        basics={"age_years": 52, "schedule_type": "home_caregiver"},
        screening={"mobility_limitation": "mobility_aid"},
        preferences={"setting": "indoor"},
    )),
]


def org_bodies(org_id: str) -> list[dict[str, Any]]:
    """ORG_SIZE synthetic employees, varied but reproducible for a given org id."""
    rng = random.Random(org_id)
    schedules = ("office", "shift", "outdoor_manual", "office")
    bodies = []
    for i in range(ORG_SIZE):
        female = i % 2 == 0
        bodies.append({
            **_body(
                basics={"language": "ar" if i % 3 == 0 else "en", "sex": "female" if female else "male",
                        "age_years": rng.randint(22, 60), "schedule_type": schedules[i % len(schedules)]},
                screening={"pregnant": "no" if female else None},
                baseline={"active_days_per_week": rng.randint(0, 5)},
                history={"motivation_reason": None},
            ),
            "org_id": org_id,
        })
    return bodies
