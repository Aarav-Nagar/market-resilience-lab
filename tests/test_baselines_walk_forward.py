from datetime import date

from market_resilience_lab.data_contract import Observation
from market_resilience_lab.experiments.baselines_walk_forward import run_baseline_walk_forward
from market_resilience_lab.experiments.ridge_walk_forward import RidgeWalkForwardConfig


def _observations() -> list[Observation]:
    rows: list[Observation] = []
    for month in range(1, 7):
        for asset, momentum, label in (("A", -1.0, -0.01), ("B", 1.0, 0.01)):
            rows.append(
                Observation(
                    asset=asset,
                    as_of=date(2020, month, 28),
                    available_at=date(2020, month, 28),
                    label_end=date(2020, min(month + 1, 12), 28),
                    label_return=label,
                    features={"mom_12_1": momentum + month * 0.01},
                )
            )
    return rows


def _config() -> RidgeWalkForwardConfig:
    return RidgeWalkForwardConfig(
        min_train_periods=2, embargo_periods=1, sleeve_size=1, cost_bps=10.0
    )


def test_zero_score_remains_neutral_on_every_embargoed_holdout() -> None:
    result = run_baseline_walk_forward(
        _observations(), baseline="zero_score", config=_config(), input_sha256="known-input"
    )

    assert result.split_count == 3
    assert result.rank.scored_periods == 0
    assert result.rank.unscorable_periods == 3
    assert result.calibration.slope is None
    assert result.portfolio.gross_return == 0.0
    assert result.portfolio.net_return == 0.0
    assert result.portfolio.average_turnover == 0.0
    assert result.input_sha256 == "known-input"
    assert result.input_provenance is None


def test_lagged_momentum_is_scored_on_the_same_embargoed_holdouts() -> None:
    result = run_baseline_walk_forward(
        _observations(), baseline="lagged_momentum_score", config=_config()
    )

    assert result.split_count == 3
    assert result.evaluated_periods == 3
    assert result.rank.scored_periods == 3
    assert result.portfolio.periods == 3
