"""Read-only community events (Task 05): peer support and community campaigns, no user posts.

Real programmes carry a source URL and the date checked; anything else is an Example and says so in its title."""

import json
from datetime import date
from functools import cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator
from rebound_engine.models import (
    Behaviour,
    Language,
    LocalizedText,
    MobilityLimitation,
    SpacePreference,
    UserProfile,
)

EVENTS_PATH = Path(__file__).resolve().parent / "data" / "community_events.json"
Category = Literal[
    "walking_group", "park_run", "sports_night", "free_health_screening", "family_activity", "women_only",
    "wheelchair_accessible",
]
Household = Literal["alone", "family", "children", "older_relatives"]


class CommunityEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    title: LocalizedText
    category: Category
    behaviours: list[Behaviour]  # empty = relevant to everyone (e.g. a health screening)
    city: str
    area: str
    schedule: str
    cost: str
    accessibility: str
    women_only: bool
    wheelchair_accessible: bool
    family_friendly: bool
    languages: list[Language]  # empty = not specified
    organiser: str
    source_url: str | None
    last_checked: date | None
    example: bool

    @model_validator(mode="after")
    def _real_or_labelled(self) -> "CommunityEvent":
        if self.example:
            if not self.title.en.startswith("Example:") or self.source_url is not None:
                raise ValueError(f"{self.id}: an example is titled 'Example:' and has no source")
        elif not (self.source_url and self.source_url.startswith("https://") and self.last_checked):
            raise ValueError(f"{self.id}: a real event needs a source URL and the date it was checked")
        return self


@cache
def load_events(path: Path = EVENTS_PATH) -> tuple[CommunityEvent, ...]:
    return tuple(CommunityEvent.model_validate(e) for e in json.loads(path.read_text(encoding="utf-8"))["events"])


def filter_events(
    profile: UserProfile, household: Household | None = None, behaviour: Behaviour | None = None,
    city: str | None = None,
) -> list[CommunityEvent]:
    """Events that fit the user's goals, space preference, mobility and language: a mobility aid shows only
    wheelchair-accessible events, "some" limitation ranks them first. Household and city come from the request only
    (no location tracking, nothing stored)."""
    goals = {behaviour} if behaviour else set(profile.basics.goals)
    women_only = profile.preferences.space_preference == SpacePreference.women_only_spaces
    needs_access = profile.screening.mobility_limitation == MobilityLimitation.mobility_aid
    prefers_access = profile.screening.mobility_limitation == MobilityLimitation.some
    lang = profile.basics.language

    def fits(e: CommunityEvent) -> bool:
        return (
            (not e.behaviours or bool(goals & set(e.behaviours)))
            and (not women_only or e.women_only or Behaviour.movement not in e.behaviours)  # exercise spaces
            and (not needs_access or e.wheelchair_accessible)
            and (not e.languages or lang in e.languages)
            and (household not in ("family", "children") or e.family_friendly)
            and (city is None or e.city.lower() == city.strip().lower())
        )

    found = [e for e in load_events() if fits(e)]
    if prefers_access:  # "some" limitation: everything, wheelchair-accessible first (stable sort keeps file order)
        found.sort(key=lambda e: not e.wheelchair_accessible)
    return found
