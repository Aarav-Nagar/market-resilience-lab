import pytest

from market_resilience_lab.metrics import evaluate_long_short_portfolio


def test_long_short_metrics_include_turnover_costs() -> None:
    months = [
        [
            {"asset": "A", "prediction": 0.9, "realized_return": 0.10},
            {"asset": "B", "prediction": 0.1, "realized_return": -0.10},
        ],
        [
            {"asset": "A", "prediction": 0.1, "realized_return": 0.00},
            {"asset": "B", "prediction": 0.9, "realized_return": 0.00},
        ],
    ]

    result = evaluate_long_short_portfolio(months, sleeve_size=1, cost_bps=10)

    assert result.gross_return == pytest.approx(0.20)
    assert result.average_turnover == pytest.approx(1.5)
    assert result.transaction_cost == pytest.approx(0.003)
    assert result.net_return == pytest.approx(0.197)


def test_month_requires_unique_assets() -> None:
    with pytest.raises(ValueError, match="unique"):
        evaluate_long_short_portfolio(
            [[
                {"asset": "A", "prediction": 0.9, "realized_return": 0.1},
                {"asset": "A", "prediction": 0.1, "realized_return": -0.1},
            ]],
            sleeve_size=1,
            cost_bps=0,
        )
