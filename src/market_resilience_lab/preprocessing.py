"""Feature transformations that make the training/holdout boundary explicit."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import isfinite, sqrt
from typing import Iterable, Sequence

from .data_contract import Observation


@dataclass(frozen=True)
class TransformedObservation:
    """An observation with transformed features and its original target intact."""

    asset: str
    as_of: date
    available_at: date
    label_end: date
    label_return: float
    features: dict[str, float]


@dataclass(frozen=True)
class FeatureStandardizer:
    """Frozen feature statistics fit only on one training window."""

    feature_names: tuple[str, ...]
    means: dict[str, float]
    scales: dict[str, float]
    constant_features: tuple[str, ...]

    @classmethod
    def fit(cls, train: Sequence[Observation]) -> "FeatureStandardizer":
        """Fit standardization statistics from training observations only."""
        if not train:
            raise ValueError("cannot fit preprocessing on an empty training window")
        feature_names = _feature_schema(train[0])
        _validate_schema_and_values(train, feature_names, "train")
        means = {
            name: sum(row.features[name] for row in train) / len(train)
            for name in feature_names
        }
        variances = {
            name: sum((row.features[name] - means[name]) ** 2 for row in train) / len(train)
            for name in feature_names
        }
        constant_features = tuple(name for name in feature_names if variances[name] == 0.0)
        scales = {
            name: 1.0 if name in constant_features else sqrt(variances[name])
            for name in feature_names
        }
        return cls(
            feature_names=feature_names,
            means=means,
            scales=scales,
            constant_features=constant_features,
        )

    def transform(self, observations: Iterable[Observation]) -> list[TransformedObservation]:
        """Transform holdout or training rows with already-frozen statistics."""
        rows = list(observations)
        _validate_schema_and_values(rows, self.feature_names, "transform")
        return [
            TransformedObservation(
                asset=row.asset,
                as_of=row.as_of,
                available_at=row.available_at,
                label_end=row.label_end,
                label_return=row.label_return,
                features={
                    name: 0.0
                    if name in self.constant_features
                    else (row.features[name] - self.means[name]) / self.scales[name]
                    for name in self.feature_names
                },
            )
            for row in rows
        ]


def standardize_train_test(
    train: Sequence[Observation], test: Sequence[Observation]
) -> tuple[FeatureStandardizer, list[TransformedObservation], list[TransformedObservation]]:
    """Fit once on ``train``, then apply the frozen scaler to train and test."""
    standardizer = FeatureStandardizer.fit(train)
    return standardizer, standardizer.transform(train), standardizer.transform(test)


def _feature_schema(row: Observation) -> tuple[str, ...]:
    if not row.features:
        raise ValueError("at least one feature is required for preprocessing")
    return tuple(sorted(row.features))


def _validate_schema_and_values(
    rows: Sequence[Observation], feature_names: tuple[str, ...], context: str
) -> None:
    expected = set(feature_names)
    for row in rows:
        if set(row.features) != expected:
            raise ValueError(f"{context} feature schema does not match fitted schema")
        if any(not isfinite(value) for value in row.features.values()):
            raise ValueError(f"{context} features must be finite")
