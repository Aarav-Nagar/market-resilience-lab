"""Training-window-only feature drift audit for completed ridge protocols."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from ..data_contract import Observation, load_observations_csv
from ..models import RidgeRegressor
from ..preprocessing import standardize_train_test
from ..splits import expanding_window_splits
from .provenance import InputProvenance, load_input_provenance
from .ridge_walk_forward import RidgeWalkForwardConfig, _group_by_period


@dataclass(frozen=True)
class DriftMonth:
    as_of: str
    mean_abs_z_score: float
    max_abs_z_score: float
    outside_training_range_share: float
    ridge_coefficient_sign: int


def run_drift_audit(observations: Iterable[Observation], *, config: RidgeWalkForwardConfig, input_provenance: InputProvenance) -> dict[str, object]:
    grouped = _group_by_period(observations)
    periods = tuple(sorted(grouped))
    splits = expanding_window_splits(periods, min_train_periods=config.min_train_periods, embargo_periods=config.embargo_periods)
    if not splits:
        raise ValueError("configuration produces no walk-forward test windows")
    months: list[DriftMonth] = []
    for split in splits:
        train = [row for i in split.train_indices for row in grouped[periods[i]]]
        test = [row for i in split.test_indices for row in grouped[periods[i]]]
        scaler, transformed_train, transformed_test = standardize_train_test(train, test)
        model = RidgeRegressor.fit(transformed_train, alpha=config.alpha)
        z_values = [abs(value) for row in transformed_test for value in row.features.values()]
        training_ranges = {
            name: (min(train_row.features[name] for train_row in train), max(train_row.features[name] for train_row in train))
            for name in scaler.feature_names
        }
        outside = sum(
            row.features[name] < training_ranges[name][0] or row.features[name] > training_ranges[name][1]
            for row in test for name in scaler.feature_names
        )
        coefficient = next(iter(model.coefficients.values()))
        months.append(DriftMonth(test[0].as_of.isoformat(), sum(z_values) / len(z_values), max(z_values), outside / len(z_values), 1 if coefficient > 0 else -1))
    return {"experiment": "ridge_feature_drift_audit_v1", "config": asdict(config), "input_provenance": input_provenance.as_dict(), "months": [asdict(month) for month in months], "limitations": ["Univariate feature drift only; no claim that drift caused prediction failure.", "Scores are standardized using each training window only."]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv"); parser.add_argument("output_json"); parser.add_argument("--min-train-periods", type=int, default=120); parser.add_argument("--embargo-periods", type=int, default=1); parser.add_argument("--alpha", type=float, default=1.0)
    args = parser.parse_args(); path = Path(args.input_csv); provenance = load_input_provenance(path)
    audit = run_drift_audit(load_observations_csv(path), config=RidgeWalkForwardConfig(min_train_periods=args.min_train_periods, embargo_periods=args.embargo_periods, alpha=args.alpha), input_provenance=provenance)
    Path(args.output_json).write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__": main()
