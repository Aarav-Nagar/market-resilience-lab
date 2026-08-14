"""Small, inspectable supervised models for the common experiment protocol."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Sequence

from .preprocessing import TransformedObservation


@dataclass(frozen=True)
class RidgeRegressor:
    """Deterministic ridge regression with an unpenalized intercept."""

    alpha: float
    feature_names: tuple[str, ...]
    intercept: float
    coefficients: dict[str, float]

    @classmethod
    def fit(
        cls, train: Sequence[TransformedObservation], *, alpha: float
    ) -> "RidgeRegressor":
        """Fit only on transformed training rows and their training labels."""
        if alpha <= 0 or not isfinite(alpha):
            raise ValueError("alpha must be a positive finite number")
        if not train:
            raise ValueError("cannot fit ridge regression on an empty training window")
        feature_names = _validate_rows(train, context="train")
        dimensions = len(feature_names) + 1
        gram = [[0.0 for _ in range(dimensions)] for _ in range(dimensions)]
        target = [0.0 for _ in range(dimensions)]
        for row in train:
            vector = [1.0, *(row.features[name] for name in feature_names)]
            for left in range(dimensions):
                target[left] += vector[left] * row.label_return
                for right in range(dimensions):
                    gram[left][right] += vector[left] * vector[right]
        for index in range(1, dimensions):
            gram[index][index] += alpha
        solution = _solve_linear_system(gram, target)
        return cls(
            alpha=alpha,
            feature_names=feature_names,
            intercept=solution[0],
            coefficients=dict(zip(feature_names, solution[1:], strict=True)),
        )

    def predict(self, rows: Iterable[TransformedObservation]) -> list[float]:
        """Score transformed observations without accessing their labels."""
        observations = list(rows)
        _validate_rows(observations, expected=self.feature_names, context="predict")
        return [
            self.intercept
            + sum(self.coefficients[name] * row.features[name] for name in self.feature_names)
            for row in observations
        ]


def _validate_rows(
    rows: Sequence[TransformedObservation],
    *,
    context: str,
    expected: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    if not rows:
        return expected or ()
    feature_names = tuple(sorted(rows[0].features))
    if not feature_names:
        raise ValueError(f"{context} rows require at least one feature")
    if expected is not None and feature_names != expected:
        raise ValueError(f"{context} feature schema does not match fitted model")
    for row in rows:
        if tuple(sorted(row.features)) != feature_names:
            raise ValueError(f"{context} feature schema is inconsistent")
        if any(not isfinite(value) for value in row.features.values()):
            raise ValueError(f"{context} features must be finite")
        if context == "train" and not isfinite(row.label_return):
            raise ValueError("train labels must be finite")
    return feature_names


def _solve_linear_system(matrix: list[list[float]], target: list[float]) -> list[float]:
    """Solve a square system by Gauss-Jordan elimination with partial pivoting."""
    size = len(target)
    augmented = [row[:] + [value] for row, value in zip(matrix, target, strict=True)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise ValueError("ridge system is numerically singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [value / pivot_value for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[column], strict=True)
            ]
    return [row[-1] for row in augmented]
