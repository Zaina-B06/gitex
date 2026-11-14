"""Curated recipes (Task 05 Part B), suggested when a nutrition step involves cooking."""

from functools import cache
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

from .models import Action, Condition, ContextFlag, LocalizedText, UserProfile

# shortcut: path works for the editable install only (same as actions.yaml); move data/ into the package for a wheel.
RECIPES_PATH = Path(__file__).resolve().parent.parent / "data" / "recipes.yaml"
RECIPE_TAGS = frozenset({"diabetes_friendly", "fasting", "family", "quick", "budget"})
CUISINES = ("emirati", "arab", "south_asian")
NOTE = "General guidance, not medical advice."


class Recipe(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    title: LocalizedText
    cuisine: str = Field(pattern="^(emirati|arab|south_asian)$")
    minutes: int = Field(gt=0)
    tags: list[str]
    ingredients: list[str] = Field(min_length=1)
    steps: list[str] = Field(min_length=1)
    swap: str  # the healthier swap this recipe shows


@cache
def load_recipes(path: Path = RECIPES_PATH) -> tuple[Recipe, ...]:
    recipes = tuple(Recipe.model_validate(r) for r in yaml.safe_load(path.read_text(encoding="utf-8"))["recipes"])
    if len({r.id for r in recipes}) != len(recipes):
        raise ValueError("duplicate recipe id")
    unknown = {t for r in recipes for t in r.tags} - RECIPE_TAGS
    if unknown:
        raise ValueError(f"unknown recipe tags {sorted(unknown)}")
    return recipes


def suggest_recipe(profile: UserProfile, action: Action, day: int, flags: set[ContextFlag]) -> Recipe | None:
    """One recipe for a cooking step, rotating by day: diabetes-friendly ones for people managing diabetes, ones
    that suit suhoor or iftar during Ramadan. None if the step doesn't involve cooking."""
    if "cooking" not in action.tags:
        return None
    pool = list(load_recipes())
    for wanted, applies in (
        ("diabetes_friendly", Condition.diabetes in profile.conditions.managing),
        ("fasting", ContextFlag.ramadan in flags),
    ):
        narrowed = [r for r in pool if wanted in r.tags]
        if applies and narrowed:
            pool = narrowed
    return pool[day % len(pool)]
