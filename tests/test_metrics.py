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
    assert result.net_return == pytest.approx(0.196602)


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


def test_all_tied_scores_produce_neutral_portfolio_not_asset_name_tie_break() -> None:
    result = evaluate_long_short_portfolio(
        [[
            {"asset": "Z", "prediction": 0.0, "realized_return": 0.10},
            {"asset": "A", "prediction": 0.0, "realized_return": -0.10},
        ]],
        sleeve_size=1,
        cost_bps=10,
    )

    assert result.gross_return == 0.0
    assert result.net_return == 0.0
    assert result.average_turnover == 0.0


def test_portfolio_return_is_compounded_across_months() -> None:
    months = [
        [
            {"asset": "A", "prediction": 1.0, "realized_return": 0.10},
            {"asset": "B", "prediction": 0.0, "realized_return": -0.10},
        ],
        [
            {"asset": "A", "prediction": 1.0, "realized_return": 0.10},
            {"asset": "B", "prediction": 0.0, "realized_return": -0.10},
        ],
    ]

    result = evaluate_long_short_portfolio(months, sleeve_size=1, cost_bps=10)

    assert result.gross_return == pytest.approx(0.44)
    assert result.net_return == pytest.approx(0.4388)
