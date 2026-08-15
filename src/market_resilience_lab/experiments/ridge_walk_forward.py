"""Embargoed walk-forward ridge experiment with provenance-rich JSON output."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

from ..data_contract import Observation, load_observations_csv
from ..evaluation import CalibrationDiagnostics, RankDiagnostics, calibration, summarize_rank_ic
from ..metrics import PortfolioMetrics, evaluate_long_short_portfolio
from ..models import RidgeRegressor
from ..preprocessing import standardize_train_test
from ..splits import expanding_window_splits
from .provenance import InputProvenance, load_input_provenance


@dataclass(frozen=True)
class RidgeWalkForwardConfig:
    min_train_periods: int = 120
    embargo_periods: int = 1
    alpha: float = 1.0
    sleeve_size: int = 5
    cost_bps: float = 10.0


@dataclass(frozen=True)
class RidgeWalkForwardResult:
    config: RidgeWalkForwardConfig
    input_sha256: str | None
    input_provenance: InputProvenance | None
    split_count: int
    evaluated_periods: int
    rank: RankDiagnostics
    calibration: CalibrationDiagnostics
    portfolio: PortfolioMetrics

    def as_dict(self) -> dict[str, object]:
        return {
            "experiment": "ridge_walk_forward_v1",
            "target": "next_month_return",
            "config": asdict(self.config),
            "input_sha256": self.input_sha256,
            "input_provenance": None if self.input_provenance is None else self.input_provenance.as_dict(),
            "split_count": self.split_count,
            "evaluated_periods": self.evaluated_periods,
            "rank": asdict(self.rank),
            "calibration": asdict(self.calibration),
            "portfolio": asdict(self.portfolio),
        }


def run_ridge_walk_forward(
    observations: Iterable[Observation],
    *,
    config: RidgeWalkForwardConfig,
    input_sha256: str | None = None,
    input_provenance: InputProvenance | None = None,
) -> RidgeWalkForwardResult:
    """Run ridge on each embargoed expanding split without reusing holdout rows."""
    grouped = _group_by_period(observations)
    periods = tuple(sorted(grouped))
    splits = expanding_window_splits(
        periods,
        min_train_periods=config.min_train_periods,
        test_periods=1,
        embargo_periods=config.embargo_periods,
    )
    if not splits:
        raise ValueError("configuration produces no walk-forward test windows")

    scored_months: list[list[dict[str, float | str]]] = []
    for split in splits:
        train = [row for index in split.train_indices for row in grouped[periods[index]]]
        test = [row for index in split.test_indices for row in grouped[periods[index]]]
        _, transformed_train, transformed_test = standardize_train_test(train, test)
        model = RidgeRegressor.fit(transformed_train, alpha=config.alpha)
        predictions = model.predict(transformed_test)
        rows_by_period: dict[date, list[dict[str, float | str]]] = {}
        for row, prediction in zip(transformed_test, predictions, strict=True):
            rows_by_period.setdefault(row.as_of, []).append(
                {
                    "asset": row.asset,
                    "prediction": prediction,
                    "realized_return": row.label_return,
                }
            )
        for period in sorted(rows_by_period):
            rows = rows_by_period[period]
            if len(rows) < config.sleeve_size * 2:
                raise ValueError(
                    f"test period {period} has fewer than twice sleeve_size observations"
                )
            scored_months.append(rows)

    flat_rows = [row for month in scored_months for row in month]
    return RidgeWalkForwardResult(
        config=config,
        input_sha256=input_sha256,
        input_provenance=input_provenance,
        split_count=len(splits),
        evaluated_periods=len(scored_months),
        rank=summarize_rank_ic(scored_months),
        calibration=calibration(flat_rows),
        portfolio=evaluate_long_short_portfolio(
            scored_months, sleeve_size=config.sleeve_size, cost_bps=config.cost_bps
        ),
    )


def run_from_csv(path: str | Path, *, config: RidgeWalkForwardConfig) -> RidgeWalkForwardResult:
    """Load a canonical CSV and retain its exact content digest in the result."""
    csv_path = Path(path)
    provenance = load_input_provenance(csv_path)
    return run_ridge_walk_forward(
        load_observations_csv(csv_path),
        config=config,
        input_sha256=provenance.input_sha256,
        input_provenance=provenance,
    )


def write_result(path: str | Path, result: RidgeWalkForwardResult) -> None:
    """Atomically write a completed result JSON to avoid partial evidence files."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", delete=False, dir=output_path.parent, suffix=".tmp"
    ) as handle:
        temporary_path = Path(handle.name)
        json.dump(result.as_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary_path, output_path)


def _group_by_period(observations: Iterable[Observation]) -> dict[date, list[Observation]]:
    grouped: dict[date, list[Observation]] = {}
    for row in observations:
        grouped.setdefault(row.as_of, []).append(row)
    if not grouped:
        raise ValueError("at least one observation is required")
    return grouped


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv")
    parser.add_argument("output_json")
    parser.add_argument("--min-train-periods", type=int, default=120)
    parser.add_argument("--embargo-periods", type=int, default=1)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--sleeve-size", type=int, default=5)
    parser.add_argument("--cost-bps", type=float, default=10.0)
    args = parser.parse_args()
    config = RidgeWalkForwardConfig(
        min_train_periods=args.min_train_periods,
        embargo_periods=args.embargo_periods,
        alpha=args.alpha,
        sleeve_size=args.sleeve_size,
        cost_bps=args.cost_bps,
    )
    result = run_from_csv(args.input_csv, config=config)
    write_result(args.output_json, result)
    print(json.dumps(result.as_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
