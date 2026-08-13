# Baselines: the standards every model must beat

Complex models are useful only when compared with clear, reproducible reference
rules. Market Resilience Lab begins with two score-generating baselines:

| Baseline | Score | Purpose |
| --- | --- | --- |
| `zero_score` | `0.0` for every asset/date | Tests whether a model adds any cross-sectional preference at all. |
| `lagged_momentum_score` | A validated lagged momentum feature | Tests whether model complexity improves on a simple, interpretable signal. |

## Important tie rule

A zero score expresses **no preference**, not an instruction to long whichever
symbols happen to sort last alphabetically. Ranking/backtest code must preserve
the tie and treat an all-tied score vector as neutral (no long/short sleeve),
or apply a documented, non-asset-dependent tie policy. It must never turn a
stable implementation detail into a fake baseline return.

## Momentum definition

The default feature key is `mom_12_1`: a provider-defined trailing 12-month
return with the most recent month excluded. The eventual adapter must document
the exact return convention, price-adjustment policy, formation date, and the
availability time used to construct it. The code does not calculate momentum
from the label and rejects an observation that does not supply the declared
feature.

These functions emit scores only. They do not claim that a baseline is
investable or profitable; portfolio results remain subject to the same
walk-forward, transaction-cost, universe, and survivorship checks as models.
