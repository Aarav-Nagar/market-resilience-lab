from datetime import date
from pathlib import Path

from market_resilience_lab.data_contract import Observation
from market_resilience_lab.experiments.ridge_walk_forward import (
    RidgeWalkForwardConfig,
    run_ridge_walk_forward,
    write_result,
)


def _observations() -> list[Observation]:
    rows: list[Observation] = []
    for index in range(6):
        year, month = 2020, index + 1
        for asset, feature, label in (("A", -1.0, -0.01), ("B", 1.0, 0.01)):
            rows.append(
                Observation(
                    asset=asset,
                    as_of=date(year, month, 28),
                    available_at=date(year, month, 28),
                    label_end=date(year, min(month + 1, 12), 28),
                    label_return=label,
                    features={"momentum": feature + index * 0.01},
                )
            )
    return rows


def test_runner_uses_embargoed_expanding_windows_and_returns_all_diagnostics(tmp_path: Path) -> None:
    result = run_ridge_walk_forward(
        _observations(),
        config=RidgeWalkForwardConfig(
            min_train_periods=2, embargo_periods=1, alpha=1.0, sleeve_size=1, cost_bps=10.0
        ),
        input_sha256="known-input",
    )

    assert result.split_count == 3
    assert result.evaluated_periods == 3
    assert result.rank.scored_periods == 3
    assert result.calibration.samples == 6
    assert result.portfolio.periods == 3
    assert result.input_sha256 == "known-input"
    assert result.input_provenance is None

    output = tmp_path / "result.json"
    write_result(output, result)
    assert '"experiment": "ridge_walk_forward_v1"' in output.read_text(encoding="utf-8")
