from datetime import date

import pytest

from market_resilience_lab.data_contract import Observation
from market_resilience_lab.preprocessing import FeatureStandardizer, standardize_train_test


def _row(asset: str, momentum: float, quality: float = 1.0) -> Observation:
    return Observation(
        asset=asset,
        as_of=date(2020, 1, 31),
        available_at=date(2020, 1, 31),
        label_end=date(2020, 2, 29),
        label_return=0.01,
        features={"mom_12_1": momentum, "quality": quality},
    )


def test_holdout_values_do_not_change_training_statistics() -> None:
    train = [_row("A", 1.0), _row("B", 3.0)]
    test = [_row("C", 1000.0)]

    scaler, transformed_train, transformed_test = standardize_train_test(train, test)

    assert scaler.means["mom_12_1"] == 2.0
    assert scaler.scales["mom_12_1"] == 1.0
    assert [row.features["mom_12_1"] for row in transformed_train] == [-1.0, 1.0]
    assert transformed_test[0].features["mom_12_1"] == 998.0


def test_constant_training_feature_transforms_to_zero() -> None:
    scaler, _, transformed_test = standardize_train_test(
        [_row("A", 1.0, quality=5.0), _row("B", 3.0, quality=5.0)],
        [_row("C", 2.0, quality=99.0)],
    )

    assert scaler.constant_features == ("quality",)
    assert transformed_test[0].features["quality"] == 0.0


def test_transform_rejects_schema_drift() -> None:
    scaler = FeatureStandardizer.fit([_row("A", 1.0)])
    drifted = Observation(
        asset="B",
        as_of=date(2020, 2, 29),
        available_at=date(2020, 2, 29),
        label_end=date(2020, 3, 31),
        label_return=0.01,
        features={"mom_12_1": 2.0},
    )

    with pytest.raises(ValueError, match="schema"):
        scaler.transform([drifted])


def test_fit_rejects_empty_train_window() -> None:
    with pytest.raises(ValueError, match="empty"):
        FeatureStandardizer.fit([])
