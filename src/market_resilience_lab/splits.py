"""Expanding-window time splits with an explicit label-horizon embargo."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Sequence


@dataclass(frozen=True)
class WalkForwardSplit:
    """A training/test split defined by index positions in ordered periods.

    ``embargo_periods`` prevents a training label whose horizon overlaps the
    test feature period from entering the training sample.
    """

    train_indices: tuple[int, ...]
    test_indices: tuple[int, ...]
    embargo_indices: tuple[int, ...]


def expanding_window_splits(
    periods: Sequence[date],
    *,
    min_train_periods: int,
    test_periods: int = 1,
    embargo_periods: int = 1,
) -> list[WalkForwardSplit]:
    """Return chronologically ordered expanding-window splits.

    Args:
        periods: Strictly increasing, unique feature-availability periods.
        min_train_periods: Number of initial periods available for fitting.
        test_periods: Consecutive periods in each holdout window.
        embargo_periods: Periods skipped after train before test. For a
            next-month label, use at least one period.

    Raises:
        ValueError: If periods are not strictly increasing or configuration is
            invalid.
    """
    if min_train_periods < 1:
        raise ValueError("min_train_periods must be at least 1")
    if test_periods < 1:
        raise ValueError("test_periods must be at least 1")
    if embargo_periods < 0:
        raise ValueError("embargo_periods cannot be negative")
    if any(left >= right for left, right in zip(periods, periods[1:])):
        raise ValueError("periods must be strictly increasing and unique")

    splits: list[WalkForwardSplit] = []
    train_end = min_train_periods
    while train_end + embargo_periods + test_periods <= len(periods):
        test_start = train_end + embargo_periods
        splits.append(
            WalkForwardSplit(
                train_indices=tuple(range(train_end)),
                embargo_indices=tuple(range(train_end, test_start)),
                test_indices=tuple(range(test_start, test_start + test_periods)),
            )
        )
        train_end += test_periods
    return splits
