"""Tie-aware prediction diagnostics for holdout cross-sections."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Iterable, Mapping


@dataclass(frozen=True)
class RankDiagnostics:
    """Summary of monthly Spearman rank information coefficients."""

    mean_rank_ic: float | None
    scored_periods: int
    unscorable_periods: int


@dataclass(frozen=True)
class CalibrationDiagnostics:
    """Descriptive relationship between predictions and realized returns."""

    intercept: float
    slope: float | None
    mean_error: float
    mean_squared_error: float
    samples: int


def rank_ic(month_rows: Iterable[Mapping[str, float | str]]) -> float | None:
    """Return Spearman rank correlation, or None when a cross-section is constant."""
    rows = _validated_rows(month_rows, require_unique_assets=True)
    predictions = [float(row["prediction"]) for row in rows]
    realized = [float(row["realized_return"]) for row in rows]
    prediction_ranks = _average_ranks(predictions)
    realized_ranks = _average_ranks(realized)
    return _pearson(prediction_ranks, realized_ranks)


def summarize_rank_ic(
    monthly_rows: Iterable[Iterable[Mapping[str, float | str]]],
) -> RankDiagnostics:
    """Average only the monthly rank ICs that are mathematically defined."""
    values: list[float] = []
    unscorable = 0
    for month in monthly_rows:
        value = rank_ic(month)
        if value is None:
            unscorable += 1
        else:
            values.append(value)
    return RankDiagnostics(
        mean_rank_ic=None if not values else sum(values) / len(values),
        scored_periods=len(values),
        unscorable_periods=unscorable,
    )


def calibration(rows: Iterable[Mapping[str, float | str]]) -> CalibrationDiagnostics:
    """Calculate descriptive calibration and error diagnostics for holdout rows."""
    data = _validated_rows(rows, require_unique_assets=False)
    predictions = [float(row["prediction"]) for row in data]
    realized = [float(row["realized_return"]) for row in data]
    mean_prediction = sum(predictions) / len(predictions)
    mean_realized = sum(realized) / len(realized)
    centered_prediction = [value - mean_prediction for value in predictions]
    variance = sum(value * value for value in centered_prediction)
    if variance == 0.0:
        slope = None
        intercept = mean_realized
    else:
        slope = sum(
            feature * (target - mean_realized)
            for feature, target in zip(centered_prediction, realized, strict=True)
        ) / variance
        intercept = mean_realized - slope * mean_prediction
    fitted = [
        intercept if slope is None else intercept + slope * prediction
        for prediction in predictions
    ]
    errors = [actual - predicted for actual, predicted in zip(realized, fitted, strict=True)]
    return CalibrationDiagnostics(
        intercept=intercept,
        slope=slope,
        mean_error=sum(errors) / len(errors),
        mean_squared_error=sum(error * error for error in errors) / len(errors),
        samples=len(data),
    )


def _validated_rows(
    rows: Iterable[Mapping[str, float | str]], *, require_unique_assets: bool
) -> list[Mapping[str, float | str]]:
    data = list(rows)
    if len(data) < 2:
        raise ValueError("at least two rows are required for prediction diagnostics")
    assets = [str(row["asset"]) for row in data]
    if require_unique_assets and len(set(assets)) != len(assets):
        raise ValueError("asset identifiers must be unique within a cross-section")
    for row in data:
        if not isfinite(float(row["prediction"])) or not isfinite(float(row["realized_return"])):
            raise ValueError("predictions and realized returns must be finite")
    return data


def _average_ranks(values: list[float]) -> list[float]:
    ranks = [0.0] * len(values)
    ordered = sorted(enumerate(values), key=lambda pair: pair[1])
    start = 0
    while start < len(ordered):
        end = start + 1
        while end < len(ordered) and ordered[end][1] == ordered[start][1]:
            end += 1
        average_rank = ((start + 1) + end) / 2.0
        for index, _ in ordered[start:end]:
            ranks[index] = average_rank
        start = end
    return ranks


def _pearson(left: list[float], right: list[float]) -> float | None:
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum(
        (left_value - left_mean) * (right_value - right_mean)
        for left_value, right_value in zip(left, right, strict=True)
    )
    left_sum_squares = sum((value - left_mean) ** 2 for value in left)
    right_sum_squares = sum((value - right_mean) ** 2 for value in right)
    if left_sum_squares == 0.0 or right_sum_squares == 0.0:
        return None
    return numerator / sqrt(left_sum_squares * right_sum_squares)
