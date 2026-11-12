"""Action library loader, validation and per-user filtering."""

from functools import cache
from pathlib import Path

import yaml

from .models import (
    Action,
    ActionSetting,
    Barrier,
    Behaviour,
    Context,
    PlaceSetting,
    UserProfile,
    UserState,
)
from .safety import SCREENING_QUESTIONS, context_filter, screening_flags

# shortcut: path works for the editable install only; move data/ into the package before building a wheel.
DEFAULT_LIBRARY_PATH = Path(__file__).resolve().parent.parent / "data" / "actions.yaml"


def load_actions(path: Path | str = DEFAULT_LIBRARY_PATH) -> list[Action]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    actions = [Action.model_validate(a) for a in raw["actions"]]
    _validate_library(actions)
    return actions


@cache
def default_library() -> tuple[Action, ...]:
    return tuple(load_actions())


def _validate_library(actions: list[Action]) -> None:
    by_id: dict[str, Action] = {}
    for a in actions:
        if a.id in by_id:
            raise ValueError(f"duplicate action id {a.id}")
        by_id[a.id] = a
    for a in actions:
        if a.seated_variant_id is not None:
            v = by_id.get(a.seated_variant_id)
            if v is None or not v.seated or v.behaviour != a.behaviour:
                raise ValueError(f"{a.id}: seated_variant_id must name a seated {a.behaviour} action")
        unknown = set(a.contraindications) - set(SCREENING_QUESTIONS)
        if unknown:
            raise ValueError(f"{a.id}: unknown contraindications {sorted(unknown)}")
    # Every behaviour needs a tier-1 action that survives every safety filter, so a plan is never empty.
    for b in Behaviour:
        if not any(_safe_floor(a) for a in actions if a.behaviour == b):
            raise ValueError(f"no tier-1 {b} action that is safe for every profile and context")


def _safe_floor(a: Action) -> bool:
    return (
        a.tier == 1
        and a.fasting_safe
        and a.pregnancy_safe
        and a.low_energy_ok
        and a.setting != ActionSetting.outdoor
        and not a.contraindications
        and (a.seated or a.behaviour != Behaviour.movement)
    )


def filter_actions(
    profile: UserProfile,
    state: UserState,
    context: Context,
    library: list[Action] | tuple[Action, ...] | None = None,
) -> list[Action]:
    """Actions this user may get right now: goals, then safety, then plan adjustments from check-ins."""
    actions = [a for a in (library or default_library()) if a.behaviour in profile.basics.goals]
    actions = context_filter(actions, context.flags, context.hour, screening_flags(profile))
    if state.prefer_indoor or profile.preferences.setting == PlaceSetting.indoor:
        actions = [a for a in actions if a.setting != ActionSetting.outdoor]
    if state.last_barrier == Barrier.energy_fatigue:
        actions = [a for a in actions if a.low_energy_ok]
    return actions
