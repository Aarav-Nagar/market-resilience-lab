# What broke?

This is the public log of negative, inconclusive, and validity-limiting findings
in Market Resilience Lab. Entries preserve completed evidence rather than
rewriting history after a more attractive result appears. They are historical
research notes, not investment advice.

## 2026-08-15 — Ridge reversed the direct momentum ordering

**Question.** Does a ridge regression trained on one point-in-time 12-1
momentum feature improve the direct feature ranking on the first reproducible
industry-portfolio screen?

**Evidence.** The three result files below use exactly the same Fama--French
49 Industry Portfolios canonical CSV, 1,000 initial monthly training periods,
one-month embargo, 186 holdout months, top/bottom-five long-short sleeve, and
10-basis-point one-way transaction cost:

| Score | Mean rank IC | Compounded net return | Average turnover |
| --- | ---: | ---: | ---: |
| Direct lagged 12-1 momentum | 0.0311 | 269.64% | 0.555 |
| Ridge on lagged 12-1 momentum | -0.0444 | -94.10% | 0.585 |
| Neutral zero score | Not defined (all ties) | 0.00% | 0.000 |

The artifacts are [`results/ff49_momentum_baseline.json`](results/ff49_momentum_baseline.json),
[`results/ff49_ridge_initial.json`](results/ff49_ridge_initial.json), and
[`results/ff49_zero_baseline.json`](results/ff49_zero_baseline.json). Each
embeds the matching canonical CSV hash and adapter-manifest provenance.

**What failed.** This specified ridge configuration did not preserve the
positive historical cross-sectional ordering shown by the direct lagged feature.
It is therefore not an acceptable improvement over that baseline in this
screen.

**What this does not establish.** The contrast does not prove that momentum is
profitable, that ridge regression generally fails, that regularization caused
the difference, or that either score survives a different universe, time range,
regime, portfolio construction, uncertainty analysis, or unmodeled costs.

**Month-level follow-up (2026-08-16).** The committed
[`results/ff49_ridge_momentum_divergence.json`](results/ff49_ridge_momentum_divergence.json)
contains all 186 identical holdout months. Ridge inverted the direct momentum
rank order in 182 months and preserved it in four. This is expectedly narrow:
with one feature, a linear ridge score can only maintain that feature's ordering
or reverse it when the fitted coefficient changes sign. The evidence therefore
does not support a story about nonlinear model behavior or a period-isolated
failure; it identifies learned coefficient sign as the immediate mechanism.

**Next falsifiable check.** Define and source non-overlapping historical regime
intervals, then aggregate the already-recorded monthly divergence by regime.
Do not add another model until that diagnostic determines whether negative
coefficient selection clusters in documented market episodes.

**Initial grouping result (2026-08-17).** The first source-linked grouping is
available in [`results/ff49_ridge_momentum_by_regime.json`](results/ff49_ridge_momentum_by_regime.json).
It has only two NBER/FRED recession months and 17 FOMC-tightening months, while
167 months remain `normal_or_unlabeled`. It is therefore a registry and report
validation step, not evidence that the ridge reversal is concentrated in either
episode. The next addition must expand sourced intervals before interpreting
cross-regime differences.

## Entry rules

- Link every finding to a committed result artifact and its reproduction command.
- State the exact task, universe, input digest, split, and cost assumptions.
- Separate observed behavior from causal explanations and future-performance
  claims.
- Add corrections as new entries or explicit amendments; do not erase prior
  findings.
