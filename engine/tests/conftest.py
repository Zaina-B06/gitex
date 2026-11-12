import copy
from datetime import UTC, datetime

import pytest

from rebound_engine.models import OnboardingPayload, UserProfile
from rebound_engine.safety import SCREENING_QUESTIONS

BASE = {
    "basics": {
        "language": "en",
        "age_years": 35,
        "sex": "female",
        "goals": ["movement", "sleep"],
        "schedule_type": "office",
        "usual_wake_time": "06:30",
        "usual_sleep_time": "23:00",
    },
    "screening": {**{q: False for q in SCREENING_QUESTIONS}, "pregnant": "no", "mobility_limitation": "none"},
    "baseline": {"active_days_per_week": 1, "sleep_hours_typical": 6.5, "sleep_quality_self": 3},
}


def _data(**groups: dict) -> dict:
    """BASE with each group's fields overridden, e.g. _data(screening={"chest_pain": True})."""
    data = copy.deepcopy(BASE)
    for group, fields in groups.items():
        data.setdefault(group, {}).update(fields)
    return data


@pytest.fixture
def make_payload():
    return lambda **groups: OnboardingPayload.model_validate(_data(**groups))


@pytest.fixture
def make_profile():
    return lambda **groups: UserProfile.model_validate(
        {**_data(**groups), "user_id": "test-user", "created_at": datetime(2026, 1, 1, tzinfo=UTC)}
    )
