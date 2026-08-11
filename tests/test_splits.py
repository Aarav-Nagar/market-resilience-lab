from datetime import date

import pytest

from market_resilience_lab.splits import expanding_window_splits


def test_expanding_splits_keep_embargo_between_train_and_test() -> None:
    periods = [date(2020, month, 1) for month in range(1, 8)]

    splits = expanding_window_splits(
        periods, min_train_periods=3, test_periods=1, embargo_periods=1
    )

    assert len(splits) == 3
    assert splits[0].train_indices == (0, 1, 2)
    assert splits[0].embargo_indices == (3,)
    assert splits[0].test_indices == (4,)
    assert splits[1].train_indices == (0, 1, 2, 3)
    assert splits[1].test_indices == (5,)


def test_periods_must_be_strictly_increasing() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        expanding_window_splits(
            [date(2020, 2, 1), date(2020, 1, 1)], min_train_periods=1
        )
