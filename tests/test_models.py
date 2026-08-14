from datetime import date

import pytest

from market_resilience_lab.models import RidgeRegressor
from market_resilience_lab.preprocessing import TransformedObservation


def _row(feature: float, label: float, *, other: float = 0.0) -> TransformedObservation:
    return TransformedObservation(
        asset=f"asset-{feature}",
        as_of=date(2020, 1, 31),
        available_at=date(2020, 1, 31),
        label_end=date(2020, 2, 29),
        label_return=label,
        features={"momentum": feature, "other": other},
    )


def test_ridge_learns_linear_training_relation() -> None:
    train = [_row(-1.0, -1.0), _row(0.0, 1.0), _row(1.0, 3.0)]

    model = RidgeRegressor.fit(train, alpha=0.001)

    assert model.intercept == pytest.approx(1.0, abs=0.001)
    assert model.coefficients["momentum"] == pytest.approx(2.0, abs=0.001)
    assert model.predict([_row(2.0, label=-999.0)])[0] == pytest.approx(5.0, abs=0.01)


def test_ridge_regularization_shrinks_feature_coefficient() -> None:
    train = [_row(-1.0, -1.0), _row(0.0, 1.0), _row(1.0, 3.0)]

    weak_penalty = RidgeRegressor.fit(train, alpha=0.01)
    strong_penalty = RidgeRegressor.fit(train, alpha=100.0)

    assert abs(strong_penalty.coefficients["momentum"]) < abs(
        weak_penalty.coefficients["momentum"]
    )


def test_predict_rejects_schema_drift() -> None:
    model = RidgeRegressor.fit([_row(0.0, 1.0)], alpha=1.0)
    drifted = TransformedObservation(
        asset="drifted",
        as_of=date(2020, 2, 29),
        available_at=date(2020, 2, 29),
        label_end=date(2020, 3, 31),
        label_return=99.0,
        features={"momentum": 0.0},
    )

    with pytest.raises(ValueError, match="schema"):
        model.predict([drifted])


def test_fit_rejects_nonpositive_alpha() -> None:
    with pytest.raises(ValueError, match="positive"):
        RidgeRegressor.fit([_row(0.0, 1.0)], alpha=0.0)


def test_prediction_does_not_read_holdout_label() -> None:
    model = RidgeRegressor.fit([_row(-1.0, -1.0), _row(1.0, 3.0)], alpha=1.0)
    holdout = _row(0.5, label=-0.03)
    altered_label = TransformedObservation(
        asset=holdout.asset,
        as_of=holdout.as_of,
        available_at=holdout.available_at,
        label_end=holdout.label_end,
        label_return=999.0,
        features=holdout.features,
    )

    assert model.predict([holdout]) == model.predict([altered_label])
