"""Alert reasons shown to users: intuitive direction only, plain language, never changes the risk score."""

from rebound_engine.risk import FEATURE_NAMES, REASONS, RiskModel


class FixedProba:
    def predict_proba(self, rows):
        return [[0.3, 0.7] for _ in rows]


def _model(kind="logistic", **weights):
    mean = {n: 0.5 for n in FEATURE_NAMES}
    std = {n: 0.1 for n in FEATURE_NAMES}
    return RiskModel(model=FixedProba(), kind=kind, feature_names=FEATURE_NAMES, threshold=0.5, mean=mean, std=std,
                     weights={n: weights.get(n, 0.0) for n in FEATURE_NAMES})


def _features(**values):
    return {n: values.get(n, 0.5) for n in FEATURE_NAMES}


def test_backwards_coefficient_is_never_a_reason():
    # Collinearity can give completion rate a positive coefficient: high completion would then "raise" risk.
    model = _model(comp_rate_14=+0.9, no_response_share_14=+0.7)
    feats = _features(comp_rate_14=0.9, no_response_share_14=0.9)  # both above average
    assert model.explain(feats) == ["no_response_share_14"]
    assert model.reasons(feats) == ["fewer replies in the last 2 weeks"]


def test_value_on_the_safe_side_is_not_a_reason():
    model = _model(no_response_share_14=+0.7, h_movement=-0.4)
    feats = _features(no_response_share_14=0.1, h_movement=0.9)  # few no-replies, strong habit: nothing risky
    assert model.explain(feats) == []


def test_unlisted_features_are_never_reasons():
    model = _model(n_shown_7=+2.0, schedule_shift=+2.0, has_screening_flag=+2.0, consecutive_misses=+0.3)
    feats = _features(n_shown_7=0.9, schedule_shift=0.9, has_screening_flag=0.9, consecutive_misses=0.9)
    assert model.explain(feats) == ["consecutive_misses"]
    assert {"n_shown_7", "schedule_shift", "has_screening_flag"}.isdisjoint(REASONS)


def test_boosting_uses_direction_too():
    model = _model(kind="gradient_boosting", comp_rate_7=0.05, h_slope_movement=0.02)
    feats = _features(comp_rate_7=0.9, h_slope_movement=0.1)  # high completion (safe), falling habit (risky)
    assert model.explain(feats) == ["h_slope_movement"]


def test_explanation_never_changes_the_score():
    model = _model(comp_rate_14=+0.9)
    feats = _features(comp_rate_14=0.9)
    before = model.predict(feats)
    model.explain(feats)
    model.reasons(feats)
    assert model.predict(feats) == before == 0.7


def test_every_reason_is_a_real_feature_with_a_phrase():
    assert set(REASONS) <= set(FEATURE_NAMES)
    assert all(d in (-1, 1) and phrase for d, phrase in REASONS.values())
