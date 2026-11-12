"""Hidden behaviour model: how a persona responds to each action shown. The engine never sees any of this."""

import math

import numpy as np
from rebound_engine.models import Action, ActionSetting, Barrier

from .personas import BARRIERS, HiddenTraits

HEAT_START, HEAT_END = 11, 16


def _sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def _episodes(rng: np.random.Generator, rate: float, length: list[int], days: int) -> set[int]:
    out: set[int] = set()
    for _ in range(rng.poisson(rate * days / 90)):
        start = int(rng.integers(1, days + 1))
        out.update(range(start, start + int(rng.integers(length[0], length[1] + 1))))
    return out


class PersonaSim:
    def __init__(
        self, traits: HiddenTraits, cfg: dict, days: int, rng: np.random.Generator, day_rng: np.random.Generator
    ) -> None:
        """rng: disruption schedule, outcome draws, check-in answers.
        day_rng: motivation noise and the app-open draw only, one fixed pair of draws per day, so the daily
        process is identical in every arm unless the arm itself moves motivation (arm A's streak penalty)."""
        self.t = traits
        self.b = cfg["behaviour"]
        self.d = cfg["disruptions"]
        self.rng = rng
        self.day_rng = day_rng
        self.phi = cfg["traits"]["motivation_ar1"]
        self.tau = cfg["traits"]["novelty_tau_days"]
        self.motivation = traits.motivation_mean
        self.habit = dict(traits.habit0)
        self.silent_days = 0
        self.churned_on: int | None = None
        seg = traits.segment["schedule_type"]
        self.illness = _episodes(rng, self.d["illness"]["rate"], self.d["illness"]["length"], days)
        travel_rate = self.d["travel"].get("segment_rate", {}).get(seg, self.d["travel"]["rate"])
        self.travel = _episodes(rng, travel_rate, self.d["travel"]["length"], days)
        work_rate = self.d["workload"].get("segment_rate", {}).get(seg, self.d["workload"]["rate"])
        self.workload = _episodes(rng, work_rate, self.d["workload"]["length"], days)
        r0, r1 = self.d["ramadan_days"]
        self.ramadan = set(range(r0, r1 + 1)) if traits.fasting else set()
        h0, h1 = self.d["heat_days"]
        self.heat = set(range(h0, h1 + 1))

    # ---------- daily dynamics ----------

    def start_day(self, day: int) -> None:
        """AR(1) motivation reverting to a mean that drifts down as novelty wears off."""
        mean = self.t.motivation_mean - self.t.novelty_drop * (1 - math.exp(-day / self.tau))
        noise = self.day_rng.normal(0, self.t.motivation_volatility)
        self.motivation = mean + self.phi * (self.motivation - mean) + noise
        self.day = day
        # Engagement is decided per day: on a closed-app day every action goes unanswered.
        self.app_open = self.day_rng.random() < _sigmoid(self.b["open_base"] + self.b["open_slope"] * self.motivation_today())

    def motivation_today(self) -> float:
        drop = self.d["workload"]["motivation_drop"] if self.day in self.workload else 0.0
        return self.motivation - drop

    def outcome(self, action: Action, window: str, hour: int) -> str:
        b, t, day = self.b, self.t, self.day
        behaviour = action.behaviour.value
        cap = t.capacity_tier[behaviour]
        if action.tier <= cap:
            tier_fit = min(b["tier_easier_cap"], b["tier_easier_bonus"] * (cap - action.tier))
        else:
            tier_fit = -b["tier_fit_penalty"] * (action.tier - cap)
        preferred = "evening" if day in self.ramadan else t.preferred_window  # windows shift after iftar
        window_match = 1.0 if behaviour == "sleep" or window == preferred else 0.0

        penalty = 0.0
        if day in self.ramadan and not action.fasting_safe:
            penalty += self.d["ramadan_penalty"]
        if day in self.heat and action.setting == ActionSetting.outdoor:
            mult = self.d["heat_multiplier"].get(t.segment["schedule_type"], 1.0)
            penalty += self.d["heat_penalty"] * mult * (1.0 if HEAT_START <= hour < HEAT_END else 0.5)
        if day in self.illness:
            ill = self.d["illness"]
            penalty += ill["penalty_movement"] if behaviour == "movement" else ill["penalty_sleep"]
        if day in self.travel:
            penalty += self.d["travel"]["penalty"]

        m = self.motivation_today()
        logit = (
            b["b0"]
            + b["b_motivation"] * m
            + b["b_habit"] * self.habit[behaviour]
            + b["b_tier_fit"] * tier_fit
            + b["b_bct"] * t.bct_responsiveness.get(action.bct_code, 0.0)
            + b["b_window"] * window_match
            - penalty
        )
        p = _sigmoid(logit)
        u = self.rng.random()
        if not self.app_open:
            result = "no_response"
        elif u < p:
            result = "completed"
        elif u < p + b["partial_share"] * (1 - p):
            result = "partial"
        else:
            p_silent = _sigmoid(b["no_response_base"] - b["no_response_slope"] * m)
            result = "no_response" if self.rng.random() < p_silent else "skipped"
        a = {"completed": 1.0, "partial": 0.5}.get(result, 0.0)
        self.habit[behaviour] = (1 - b["habit_rate"]) * self.habit[behaviour] + b["habit_rate"] * a
        return result

    def end_day(self, outcomes: list[str]) -> None:
        """14 silent days in a row (every action unanswered) -> the persona churns for good."""
        if outcomes and all(o == "no_response" for o in outcomes):
            self.silent_days += 1
        elif outcomes:
            self.silent_days = 0
        if self.silent_days >= self.b["dropout_silent_days"]:
            self.churned_on = self.day

    def streak_reset(self, sensitivity: float) -> None:
        """Abstinence-violation effect (arm A): a broken streak knocks motivation down."""
        self.motivation -= sensitivity

    # ---------- check-ins ----------

    def true_barrier(self) -> str:
        if self.day in self.illness:
            return Barrier.illness_pain.value
        if self.day in self.travel:
            return Barrier.schedule_change.value
        if self.day in self.workload:
            return Barrier.time.value
        if self.day in self.ramadan:
            return Barrier.energy_fatigue.value
        w = self.t.true_barrier_weights
        return BARRIERS[self.rng.choice(len(BARRIERS), p=[w[k] for k in BARRIERS])]

    def answer_checkin(self) -> str | None:
        """None = not answered today. Otherwise the true barrier with p = 0.8, else a random one."""
        if self.rng.random() >= self.t.checkin_answer_rate:
            return None
        if self.rng.random() < 0.8:
            return self.true_barrier()
        return BARRIERS[self.rng.integers(len(BARRIERS))]

    def is_ill(self) -> bool:
        return self.day in self.illness
