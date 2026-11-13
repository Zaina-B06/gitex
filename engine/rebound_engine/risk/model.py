"""Loading and using a trained lapse-risk model (Task 02b).

scikit-learn and joblib are optional: install `rebound_engine[risk]`. They're imported only when a model is loaded,
so `Engine()` without a risk model stays pure Python."""

from dataclasses import dataclass, field
from pathlib import Path

from .features import FEATURE_NAMES, REASONS


@dataclass
class RiskModel:
    model: object  # fitted scikit-learn estimator with predict_proba
    kind: str  # "logistic" or "gradient_boosting"
    feature_names: tuple[str, ...]
    threshold: float  # alert when risk >= threshold (frozen from the validation seeds)
    mean: dict[str, float]
    std: dict[str, float]
    weights: dict[str, float]  # logistic: standardised coefficients; boosting: permutation importances
    meta: dict = field(default_factory=dict)  # training seeds, alert rate, metrics summary

    def _row(self, features: dict[str, float]) -> list[float]:
        missing = set(self.feature_names) - set(features)
        if missing:
            raise ValueError(f"missing features: {sorted(missing)}")
        return [float(features[n]) for n in self.feature_names]

    def predict(self, features: dict[str, float]) -> float:
        """Probability of reaching the lapsed state within the next 7 days."""
        return float(self.model.predict_proba([self._row(features)])[0][1])

    def predict_many(self, rows: list[dict[str, float]]) -> list[float]:
        return [float(p[1]) for p in self.model.predict_proba([self._row(r) for r in rows])]

    def explain(self, features: dict[str, float], k: int = 3) -> list[str]:
        """Up to k features that push this person's risk up *in an intuitive direction* (see REASONS).

        A feature qualifies only if it's in REASONS, its value is on the risky side of average for that direction,
        and (logistic) its coefficient has the intuitive sign, so collinear features with a backwards sign (e.g. a
        positive weight on completion rate) are never shown. Ranking: logistic = exact contribution to the log-odds
        (coefficient × standardised value); boosting = permutation importance × distance from average
        (approximate). This only affects the explanation, never the risk score."""
        scores = {}
        for n in self.feature_names:
            if n not in REASONS:
                continue
            direction = REASONS[n][0]
            z = (float(features[n]) - self.mean[n]) / (self.std[n] or 1.0)
            w = self.weights.get(n, 0.0)
            if direction * z <= 0:
                continue  # value isn't on the risky side for this person
            if self.kind == "logistic":
                if direction * w <= 0:
                    continue  # backwards coefficient (collinearity): not a believable reason
                scores[n] = w * z
            else:
                scores[n] = w * abs(z)
        return [n for n, s in sorted(scores.items(), key=lambda kv: -kv[1])[:k] if s > 0]

    def reasons(self, features: dict[str, float], k: int = 3) -> list[str]:
        """Plain-language reasons for the app, e.g. ["fewer replies in the last 2 weeks", ...]."""
        return [REASONS[n][1] for n in self.explain(features, k)]

    def alert(self, features: dict[str, float]) -> bool:
        return self.predict(features) >= self.threshold


def save_risk_model(model: RiskModel, path: Path | str) -> None:
    import joblib

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load_risk_model(path: Path | str) -> RiskModel:
    import joblib

    model = joblib.load(path)
    if not isinstance(model, RiskModel) or tuple(model.feature_names) != FEATURE_NAMES:
        raise ValueError(f"{path} is not a lapse-risk model for this engine version (feature list differs)")
    return model
