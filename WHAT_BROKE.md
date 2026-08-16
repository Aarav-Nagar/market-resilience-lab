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

**Next falsifiable check.** Produce month-level ridge and direct-momentum rank
IC/portfolio-return records, then compare their divergence across documented,
non-overlapping regimes. Do not add another model until that diagnostic shows
whether the reversal is broad, period-concentrated, or a data/split artifact.

## Entry rules

- Link every finding to a committed result artifact and its reproduction command.
- State the exact task, universe, input digest, split, and cost assumptions.
- Separate observed behavior from causal explanations and future-performance
  claims.
- Add corrections as new entries or explicit amendments; do not erase prior
  findings.
