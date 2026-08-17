from datetime import date
from pathlib import Path

import pytest

from market_resilience_lab.regimes import RegimeInterval, label_periods, load_regimes


def test_labels_are_inclusive_and_default_outside_intervals() -> None:
    intervals = (RegimeInterval("episode", date(2020, 3, 1), date(2020, 4, 30), "source", "why"),)
    assert label_periods([date(2020, 3, 31), date(2020, 5, 31)], intervals, default="normal") == {
        date(2020, 3, 31): "episode", date(2020, 5, 31): "normal"
    }


def test_rejects_overlapping_intervals(tmp_path: Path) -> None:
    path = tmp_path / "regimes.json"
    path.write_text('{"intervals":[{"name":"a","start":"2020-01-01","end":"2020-02-01","source_url":"s","rationale":"r"},{"name":"b","start":"2020-02-01","end":"2020-03-01","source_url":"s","rationale":"r"}]}', encoding="utf-8")
    with pytest.raises(ValueError, match="overlap"):
        load_regimes(path)
