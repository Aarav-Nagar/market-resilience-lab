"""Transparent, dependency-free portfolio metrics for cross-sectional scores."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class PortfolioMetrics:
    """Aggregate results for a deterministic equal-weight long/short sleeve."""

    gross_return: float
    net_return: float
    average_turnover: float
    transaction_cost: float
    periods: int


def evaluate_long_short_portfolio(
    monthly_rows: Iterable[Iterable[Mapping[str, float | str]]],
    *,
    sleeve_size: int,
    cost_bps: float,
) -> PortfolioMetrics:
    """Evaluate equal-weight long/short returns for scored monthly universes.

    Rows need ``asset``, ``prediction``, and ``realized_return`` keys. Higher
    predictions go long; lower predictions go short. An all-tied score vector
    expresses no cross-sectional preference and produces neutral weights rather
    than an arbitrary asset-name tie break. Turnover is the half-sum of absolute
    changes in signed portfolio weights across adjacent months. ``cost_bps`` is
    charged on that turnover, so a 10 bps cost is ``10 / 10_000``.
    """
    if sleeve_size < 1:
        raise ValueError("sleeve_size must be at least 1")
    if cost_bps < 0:
        raise ValueError("cost_bps cannot be negative")

    previous_weights: dict[str, float] = {}
    gross_returns: list[float] = []
    net_returns: list[float] = []
    turnovers: list[float] = []
    for month in monthly_rows:
        rows = list(month)
        if len(rows) < sleeve_size * 2:
            raise ValueError("each month needs at least twice sleeve_size rows")
        assets = [str(row["asset"]) for row in rows]
        if len(set(assets)) != len(assets):
            raise ValueError("asset identifiers must be unique within a month")

        predictions = {float(row["prediction"]) for row in rows}
        if len(predictions) == 1:
            weights: dict[str, float] = {}
        else:
            ordered = sorted(rows, key=lambda row: (float(row["prediction"]), str(row["asset"])))
            short_rows = ordered[:sleeve_size]
            long_rows = ordered[-sleeve_size:]
            weights = {str(row["asset"]): -1.0 / sleeve_size for row in short_rows}
            weights.update({str(row["asset"]): 1.0 / sleeve_size for row in long_rows})
        gross_return = (
            sum(
                weights.get(str(row["asset"]), 0.0) * float(row["realized_return"])
                for row in rows
            )
        )
        universe = set(previous_weights) | set(weights)
        turnovers.append(
            0.5 * sum(abs(weights.get(asset, 0.0) - previous_weights.get(asset, 0.0)) for asset in universe)
        )
        net_returns.append(gross_return - turnovers[-1] * cost_bps / 10_000)
        gross_returns.append(gross_return)
        previous_weights = weights

    if not gross_returns:
        raise ValueError("at least one month is required")
    average_turnover = sum(turnovers) / len(turnovers)
    transaction_cost = sum(turnovers) * cost_bps / 10_000
    gross_return = _compound_returns(gross_returns)
    net_return = _compound_returns(net_returns)
    return PortfolioMetrics(
        gross_return=gross_return,
        net_return=net_return,
        average_turnover=average_turnover,
        transaction_cost=transaction_cost,
        periods=len(gross_returns),
    )


def _compound_returns(returns: Iterable[float]) -> float:
    wealth = 1.0
    for period_return in returns:
        wealth *= 1.0 + period_return
    return wealth - 1.0
