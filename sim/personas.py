"""Synthetic personas: an OnboardingPayload (what the engine sees) plus HiddenTraits (what it never sees)."""

from dataclasses import dataclass

import numpy as np
from rebound_engine.actions import default_library
from rebound_engine.models import Barrier, Behaviour, OnboardingPayload, PastHelper
from rebound_engine.safety import SCREENING_QUESTIONS, SEE_DOCTOR_QUESTIONS

# Frozen to what personas used before Task 05 Part B (movement and sleep only), so their random draws don't change.
BCT_CODES = sorted({a.bct_code for a in default_library() if a.behaviour in (Behaviour.movement, Behaviour.sleep)})
BARRIERS = [b.value for b in (Barrier.time, Barrier.energy_fatigue, Barrier.illness_pain, Barrier.schedule_change,
                              Barrier.environment, Barrier.low_motivation, Barrier.social_family, Barrier.forgot)]
SEGMENTS = ("schedule_type", "language", "mobility_limitation", "health_literacy")


@dataclass
class HiddenTraits:
    persona_id: int
    segment: dict[str, str]  # schedule_type, language (ar/en/south_asian), mobility_limitation, health_literacy
    fasting: bool
    motivation_mean: float
    motivation_volatility: float
    capacity_tier: dict[str, int]  # per behaviour: highest tier the persona can sustain
    bct_responsiveness: dict[str, float]
    preferred_window: str
    true_barrier_weights: dict[str, float]
    checkin_answer_rate: float
    streak_sensitivity: float
    habit0: dict[str, float]
    novelty_drop: float = 0.0


def _pick(rng: np.random.Generator, dist: dict[str, float]) -> str:
    keys = list(dist)
    p = np.array([dist[k] for k in keys], dtype=float)
    return keys[rng.choice(len(keys), p=p / p.sum())]


def _payload(rng: np.random.Generator, cfg: dict) -> tuple[dict, dict]:
    pc = cfg["personas"]
    schedule = _pick(rng, pc["schedule_type"])
    language = _pick(rng, pc["language"])
    literacy = _pick(rng, pc["health_literacy"])
    mobility = _pick(rng, pc["mobility_limitation"])
    sex = _pick(rng, pc["sex"])
    age = int(rng.integers(pc["age"][0], pc["age"][1] + 1))
    goals = {"both": ["movement", "sleep"], "movement": ["movement"], "sleep": ["sleep"]}[_pick(rng, pc["goals"])]

    screening: dict = {q: False for q in SCREENING_QUESTIONS}
    if rng.random() < pc["screening_flag_rate"]:
        doctor = rng.random() < pc["see_doctor_share"]
        options = SEE_DOCTOR_QUESTIONS if doctor else [q for q in SCREENING_QUESTIONS if q not in SEE_DOCTOR_QUESTIONS]
        screening[options[rng.integers(len(options))]] = True
    if sex == "female":
        screening["pregnant"] = "yes" if 18 <= age <= 45 and rng.random() < pc["pregnant_rate"] else "no"
    screening["mobility_limitation"] = mobility

    shift_key = schedule
    if schedule == "shift":
        shift_key = "shift_night" if rng.random() < pc["night_shift_share"] else "shift_day"
    wake, sleep = pc["wake_sleep"][shift_key]
    helpers = [h.value for h in PastHelper]
    payload = {
        "basics": {
            "language": "ar" if language == "ar" else "en",
            "age_years": age,
            "sex": sex,
            "goals": goals,
            "schedule_type": schedule,
            "usual_wake_time": f"{wake:02d}:00",
            "usual_sleep_time": f"{sleep:02d}:00",
        },
        "screening": screening,
        "baseline": {
            "active_days_per_week": int(rng.choice(8, p=pc["active_days_p"])),
            "sleep_hours_typical": float(np.round(rng.normal(6.5, 1.0), 1).clip(3, 10)),
            "sleep_quality_self": int(rng.choice(5, p=pc["sleep_quality_p"])) + 1,
        },
        "history": {
            "tried_before": bool(rng.random() < 0.6),
            "past_helpers": list(rng.choice(helpers, rng.integers(0, pc["max_past_helpers"] + 1), replace=False)),
            "past_stop_reasons": list(
                rng.choice(BARRIERS, rng.integers(0, pc["max_past_stop_reasons"] + 1), replace=False)
            ),
        },
        "preferences": {
            "setting": _pick(rng, pc["setting"]),
            "fasting_ramadan": False,  # set below
            "quiet_hours": {"start": f"{sleep:02d}:00", "end": f"{wake:02d}:00"},
        },
    }
    segment = {
        "schedule_type": schedule,
        "language": language,
        "mobility_limitation": mobility,
        "health_literacy": literacy,
    }
    return payload, segment


def _traits(rng: np.random.Generator, cfg: dict, pid: int, payload: dict, segment: dict) -> HiddenTraits:
    tc, bc = cfg["traits"], cfg["behaviour"]
    active_days = payload["baseline"]["active_days_per_week"]
    quality = payload["baseline"]["sleep_quality_self"]
    extra = [-1, 0, 1]
    move_cap = 1 + round(active_days / 7 * 3) + extra[rng.choice(3, p=tc["capacity_extra_p"])]
    if segment["mobility_limitation"] != "none":
        move_cap = min(move_cap, 2)
    sleep_cap = round(quality / 5 * 4) + extra[rng.choice(3, p=tc["capacity_extra_p"])]

    weights = np.full(len(BARRIERS), tc["barrier_alpha"])
    for reason in payload["history"]["past_stop_reasons"]:
        weights[BARRIERS.index(reason)] += tc["stop_reason_boost"]
    for barrier, boost in tc["schedule_barrier_boost"].get(segment["schedule_type"], {}).items():
        weights[BARRIERS.index(barrier)] += boost
    barrier_p = rng.dirichlet(weights)

    return HiddenTraits(
        persona_id=pid,
        segment=segment,
        fasting=payload["preferences"]["fasting_ramadan"],
        motivation_mean=float(rng.normal(*tc["motivation_mean"]) + tc["literacy_shift"][segment["health_literacy"]]),
        motivation_volatility=float(rng.uniform(*tc["motivation_volatility"])),
        capacity_tier={"movement": int(np.clip(move_cap, 1, 4)), "sleep": int(np.clip(sleep_cap, 1, 4))},
        bct_responsiveness={c: float(rng.normal(0, tc["bct_responsiveness_sd"])) for c in BCT_CODES},
        preferred_window=_pick(rng, tc["preferred_window"][segment["schedule_type"]]),
        true_barrier_weights=dict(zip(BARRIERS, barrier_p.tolist(), strict=True)),
        checkin_answer_rate=float(rng.beta(*tc["checkin_answer_rate"])),
        streak_sensitivity=float(rng.uniform(*tc["streak_sensitivity"])),
        novelty_drop=float(rng.uniform(*tc["novelty_drop"])),
        habit0={
            "movement": bc["habit_start_scale"] * active_days / 7,
            "sleep": bc["habit_start_scale"] * (quality - 1) / 4,
        },
    )


def generate_personas(n: int, seed: int, cfg: dict) -> list[tuple[OnboardingPayload, HiddenTraits]]:
    rng = np.random.default_rng([seed, 1])
    out = []
    for pid in range(n):
        payload, segment = _payload(rng, cfg)
        payload["preferences"]["fasting_ramadan"] = bool(rng.random() < cfg["personas"]["fasting_rate"])
        traits = _traits(rng, cfg, pid, payload, segment)
        out.append((OnboardingPayload.model_validate(payload), traits))
    return out
