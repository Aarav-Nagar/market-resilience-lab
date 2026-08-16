"""Month-level ridge versus direct-momentum divergence audit."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from ..baselines import lagged_momentum_score
from ..data_contract import Observation, load_observations_csv
from ..evaluation import rank_ic
from ..metrics import evaluate_long_short_portfolio
from ..models import RidgeRegressor
from ..preprocessing import standardize_train_test
from ..splits import expanding_window_splits
from .provenance import InputProvenance, load_input_provenance
from .ridge_walk_forward import RidgeWalkForwardConfig, _group_by_period


@dataclass(frozen=True)
class DivergenceMonth:
    as_of: str
    ridge_rank_ic: float | None
    momentum_rank_ic: float | None
    rank_ic_difference: float | None
    ridge_gross_return: float
    momentum_gross_return: float


@dataclass(frozen=True)
class DivergenceAudit:
    config: RidgeWalkForwardConfig
    input_provenance: InputProvenance
    months: tuple[DivergenceMonth, ...]

    @property
    def rank_order_summary(self) -> dict[str, int]:
        """Classify whether one-feature ridge preserved or inverted each ranking."""
        same = inverted = other = 0
        for month in self.months:
            if month.ridge_rank_ic is None or month.momentum_rank_ic is None:
                other += 1
            elif abs(month.ridge_rank_ic - month.momentum_rank_ic) < 1e-12:
                same += 1
            elif abs(month.ridge_rank_ic + month.momentum_rank_ic) < 1e-12:
                inverted += 1
            else:
                other += 1
        return {"same_rank_order_months": same, "inverted_rank_order_months": inverted, "other_months": other}

    def as_dict(self) -> dict[str, object]:
        return {
            "experiment": "ridge_momentum_divergence_audit_v1",
            "target": "next_month_return",
            "config": asdict(self.config),
            "input_provenance": self.input_provenance.as_dict(),
            "rank_order_summary": self.rank_order_summary,
            "months": [asdict(month) for month in self.months],
        }


def run_divergence_audit(
    observations: Iterable[Observation], *, config: RidgeWalkForwardConfig, input_provenance: InputProvenance
) -> DivergenceAudit:
    """Compare both scores on each identical embargoed holdout cross-section."""
    grouped = _group_by_period(observations)
    periods = tuple(sorted(grouped))
    splits = expanding_window_splits(
        periods, min_train_periods=config.min_train_periods, embargo_periods=config.embargo_periods
    )
    if not splits:
        raise ValueError("configuration produces no walk-forward test windows")
    months: list[DivergenceMonth] = []
    for split in splits:
        train = [row for index in split.train_indices for row in grouped[periods[index]]]
        test = [row for index in split.test_indices for row in grouped[periods[index]]]
        _, transformed_train, transformed_test = standardize_train_test(train, test)
        ridge_predictions = RidgeRegressor.fit(transformed_train, alpha=config.alpha).predict(transformed_test)
        momentum_predictions = lagged_momentum_score(test)
        ridge_rows = _scored_rows(test, ridge_predictions)
        momentum_rows = _scored_rows(test, momentum_predictions)
        ridge_ic = rank_ic(ridge_rows)
        momentum_ic = rank_ic(momentum_rows)
        if len(ridge_rows) < config.sleeve_size * 2:
            raise ValueError("test period has fewer than twice sleeve_size observations")
        months.append(
            DivergenceMonth(
                as_of=test[0].as_of.isoformat(),
                ridge_rank_ic=ridge_ic,
                momentum_rank_ic=momentum_ic,
                rank_ic_difference=None if ridge_ic is None or momentum_ic is None else ridge_ic - momentum_ic,
                ridge_gross_return=evaluate_long_short_portfolio([ridge_rows], sleeve_size=config.sleeve_size, cost_bps=0).gross_return,
                momentum_gross_return=evaluate_long_short_portfolio([momentum_rows], sleeve_size=config.sleeve_size, cost_bps=0).gross_return,
            )
        )
    return DivergenceAudit(config=config, input_provenance=input_provenance, months=tuple(months))


def _scored_rows(observations: Iterable[Observation], scores) -> list[dict[str, float | str]]:
    return [
        {
            "asset": row.asset,
            "prediction": float(score) if isinstance(score, (float, int)) else score.prediction,
            "realized_return": row.label_return,
        }
        for row, score in zip(observations, scores, strict=True)
    ]


def run_from_csv(path: str | Path, *, config: RidgeWalkForwardConfig) -> DivergenceAudit:
    csv_path = Path(path)
    provenance = load_input_provenance(csv_path)
    return run_divergence_audit(load_observations_csv(csv_path), config=config, input_provenance=provenance)


def write_audit(path: str | Path, audit: DivergenceAudit) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=output_path.parent, suffix=".tmp") as handle:
        temporary_path = Path(handle.name)
        json.dump(audit.as_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary_path, output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv")
    parser.add_argument("output_json")
    parser.add_argument("--min-train-periods", type=int, default=120)
    parser.add_argument("--embargo-periods", type=int, default=1)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--sleeve-size", type=int, default=5)
    args = parser.parse_args()
    audit = run_from_csv(args.input_csv, config=RidgeWalkForwardConfig(
        min_train_periods=args.min_train_periods, embargo_periods=args.embargo_periods,
        alpha=args.alpha, sleeve_size=args.sleeve_size
    ))
    write_audit(args.output_json, audit)
    print(json.dumps(audit.as_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
