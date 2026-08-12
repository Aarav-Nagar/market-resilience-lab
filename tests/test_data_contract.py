from pathlib import Path

import pytest

from market_resilience_lab.data_contract import load_observations_csv


def _write_csv(tmp_path: Path, rows: str) -> Path:
    path = tmp_path / "observations.csv"
    path.write_text(rows, encoding="utf-8")
    return path


def test_loader_validates_and_sorts_point_in_time_rows(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "asset,as_of,available_at,label_end,label_return,feature__momentum\n"
        "BBB,2020-02-29,2020-02-28,2020-03-31,-0.02,0.10\n"
        "AAA,2020-01-31,2020-01-31,2020-02-29,0.03,0.20\n",
    )

    observations = load_observations_csv(path)

    assert [row.asset for row in observations] == ["AAA", "BBB"]
    assert observations[0].features == {"momentum": 0.20}


def test_loader_rejects_late_feature_availability(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "asset,as_of,available_at,label_end,label_return,feature__momentum\n"
        "AAA,2020-01-31,2020-02-01,2020-02-29,0.03,0.20\n",
    )

    with pytest.raises(ValueError, match="available_at.*after as_of"):
        load_observations_csv(path)


def test_loader_rejects_nonfuture_label(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "asset,as_of,available_at,label_end,label_return,feature__momentum\n"
        "AAA,2020-01-31,2020-01-31,2020-01-31,0.03,0.20\n",
    )

    with pytest.raises(ValueError, match="label_end.*after as_of"):
        load_observations_csv(path)


def test_loader_rejects_duplicate_asset_dates(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "asset,as_of,available_at,label_end,label_return,feature__momentum\n"
        "AAA,2020-01-31,2020-01-31,2020-02-29,0.03,0.20\n"
        "AAA,2020-01-31,2020-01-31,2020-02-29,0.01,0.10\n",
    )

    with pytest.raises(ValueError, match="duplicate asset/as_of"):
        load_observations_csv(path)


def test_loader_rejects_nonfinite_model_input(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "asset,as_of,available_at,label_end,label_return,feature__momentum\n"
        "AAA,2020-01-31,2020-01-31,2020-02-29,0.03,nan\n",
    )

    with pytest.raises(ValueError, match="must be finite"):
        load_observations_csv(path)
