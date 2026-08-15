"""Embargoed walk-forward reference baselines with provenance-rich output."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Literal

from ..baselines import lagged_momentum_score, zero_score
from ..data_contract import Observation, load_observations_csv
from ..evaluation import CalibrationDiagnostics, RankDiagnostics, calibration, summarize_rank_ic
from ..metrics import PortfolioMetrics, evaluate_long_short_portfolio
from ..splits import expanding_window_splits
from .provenance import InputProvenance, load_input_provenance
from .ridge_walk_forward import RidgeWalkForwardConfig, _group_by_period


BaselineName = Literal["zero_score", "lagged_momentum_score"]


@dataclass(frozen=True)
class BaselineWalkForwardResult:
    """A reference baseline evaluated on the exact ridge walk-forward windows."""

    baseline: BaselineName
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
            "experiment": "baseline_walk_forward_v1",
            "baseline": self.baseline,
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


def run_baseline_walk_forward(
    observations: Iterable[Observation],
    *,
    baseline: BaselineName,
    config: RidgeWalkForwardConfig,
    input_sha256: str | None = None,
    input_provenance: InputProvenance | None = None,
) -> BaselineWalkForwardResult:
    """Score each embargoed holdout window using an explicit, non-fitted baseline."""
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
        test = [row for index in split.test_indices for row in grouped[periods[index]]]
        scores = _score(test, baseline=baseline)
        rows = [
            {
                "asset": row.asset,
                "prediction": score.prediction,
                "realized_return": row.label_return,
            }
            for row, score in zip(test, scores, strict=True)
        ]
        if len(rows) < config.sleeve_size * 2:
            raise ValueError("test period has fewer than twice sleeve_size observations")
        scored_months.append(rows)

    flat_rows = [row for month in scored_months for row in month]
    return BaselineWalkForwardResult(
        baseline=baseline,
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


def run_from_csv(
    path: str | Path, *, baseline: BaselineName, config: RidgeWalkForwardConfig
) -> BaselineWalkForwardResult:
    """Load a canonical CSV and bind its content digest into the result."""
    csv_path = Path(path)
    provenance = load_input_provenance(csv_path)
    return run_baseline_walk_forward(
        load_observations_csv(csv_path),
        baseline=baseline,
        config=config,
        input_sha256=provenance.input_sha256,
        input_provenance=provenance,
    )


def write_result(path: str | Path, result: BaselineWalkForwardResult) -> None:
    """Atomically write a completed baseline result JSON."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", delete=False, dir=output_path.parent, suffix=".tmp"
    ) as handle:
        temporary_path = Path(handle.name)
        json.dump(result.as_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary_path, output_path)


def _score(observations: Iterable[Observation], *, baseline: BaselineName):
    if baseline == "zero_score":
        return zero_score(observations)
    if baseline == "lagged_momentum_score":
        return lagged_momentum_score(observations)
    raise ValueError(f"unsupported baseline: {baseline}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv")
    parser.add_argument("output_json")
    parser.add_argument("--baseline", choices=("zero_score", "lagged_momentum_score"), required=True)
    parser.add_argument("--min-train-periods", type=int, default=120)
    parser.add_argument("--embargo-periods", type=int, default=1)
    parser.add_argument("--sleeve-size", type=int, default=5)
    parser.add_argument("--cost-bps", type=float, default=10.0)
    args = parser.parse_args()
    config = RidgeWalkForwardConfig(
        min_train_periods=args.min_train_periods,
        embargo_periods=args.embargo_periods,
        sleeve_size=args.sleeve_size,
        cost_bps=args.cost_bps,
    )
    result = run_from_csv(args.input_csv, baseline=args.baseline, config=config)
    write_result(args.output_json, result)
    print(json.dumps(result.as_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
