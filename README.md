# Market Resilience Lab

**When do supervised-learning investing signals remain useful—and when do they break?**

Market Resilience Lab is a reproducible research project for evaluating supervised
learning models across changing market regimes. It is deliberately not a contest
to find a "best stock-prediction model." A strong aggregate score can hide poor
calibration, high turnover, or failure during stressed markets. This repository
makes those trade-offs visible.

## Research question

Using only information available on each historical date, how do supervised
models rank or classify future equity returns, and how do their accuracy,
calibration, turnover, and transaction-cost-aware portfolio outcomes vary by
market regime?

The initial task is **monthly cross-sectional return ranking**:

- **Universe:** a documented, reproducible equity universe supplied by a data
  adapter; no survivorship-free claim is made until the selected source supports it.
- **Features:** lagged, point-in-time features whose availability timestamp is
  recorded.
- **Label:** next-month realized return, kept separate from features.
- **Prediction:** a score used to form equal-weight long and short sleeves.
- **Regimes:** explicit historical intervals, including normal, high-volatility,
  rate/inflation shock, drawdown, and recovery periods.

## What makes the project different

Every fitted model will receive a **Model Resilience Card** with its intended
use, exact data contract, walk-forward protocol, performance by regime,
calibration/confidence diagnostics, turnover/cost sensitivity, failure modes,
and reproduction command. A companion Regime Stress Test report will distinguish
an average leaderboard from performance in documented historical episodes.

The project also asks whether a model appeared uncertain before it failed. That
is an audit of calibration and data drift—not evidence that uncertainty predicts
the future with certainty.

## Validity rules

1. All splits are expanding-window and include an embargo between training and
   evaluation when labels overlap the test start.
2. Preprocessing, feature selection, and model fitting occur inside each
   training window only.
3. Reported portfolio results include turnover and configurable transaction
   costs; uncosted returns are labeled as such.
4. Aggregate and regime-level results are reported together, with the same
   configuration and random seed.
5. Negative, inconclusive, or unstable results remain in the research log.

## Status

The first milestone establishes an enforced point-in-time data contract,
expanding-window split generator, and deterministic transaction-cost-aware
portfolio metrics. No empirical performance claim has been made yet.

See [ROADMAP.md](ROADMAP.md) for planned research milestones and
[CONTRIBUTING.md](CONTRIBUTING.md) for the project quality bar. The required
adapter fields and evidence gate are in [DATA_CONTRACT.md](DATA_CONTRACT.md).
Every later model will also be evaluated against the explicit rules in
[BASELINES.md](BASELINES.md). The first documented source adapter and its
boundaries are in [DATA_SOURCES.md](DATA_SOURCES.md), and the training-only
preprocessing contract is in [PREPROCESSING.md](PREPROCESSING.md).
The first supervised-model protocol is in [MODELS.md](MODELS.md).
Prediction diagnostics and their limits are documented in [EVALUATION.md](EVALUATION.md).

## Quick start

Requires Python 3.11+.

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

## Scope and disclaimer

This is educational research, not investment advice, a solicitation, or a
recommendation to trade. Historical evaluation does not establish future
performance or causation. Data-source licenses and availability constraints will
be documented before each experiment is published.
