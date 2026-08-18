# Initial ridge methodology screen

`ff49_ridge_initial.json` is the first completed Market Resilience Lab result.
It is deliberately a **bounded negative result**, not an investment conclusion.

## Configuration

- Source: Fama--French value-weighted 49 Industry Portfolios, downloaded
  directly through the documented adapter.
- Source archive SHA-256: `a0b23457eac619c8a3cce362de563b6f57acc3514779ceccdb99886edfa0a804`
- Canonical observation CSV SHA-256:
  `24b8e76309e8e7ef90cf4cfd6656542ff8a75bde78f8c55945a31781372492fc`
- 1,000 initial monthly training periods; one-month embargo; 186 one-month
  holdout periods; ridge alpha 1.0.
- One lagged 12-1 momentum feature; top/bottom five industry portfolios; 10
  basis points of one-way transaction costs.

## Outcome

The mean cross-sectional rank IC was **-0.0444** over 186 scored months. The
compounded gross long/short return was **-93.41%** and the cost-adjusted result
was **-94.10%**. Average turnover was 0.585 and the arithmetic sum of modeled
transaction costs was 10.88%.

This means the initial ridge/momentum configuration did not establish a useful
positive ranking signal in this industry-portfolio screen. It does **not** show
that ridge regression, momentum, other supervised models, or individual-stock
signals generally fail. The run has one source, one feature, one alpha, one
portfolio construction, no uncertainty interval, and no regime-level analysis.

The result is retained because the project asks when models break. The exact
zero and momentum baselines are now included below; uncertainty and regime
diagnostics remain necessary before judging any model family.

## Exact-split baseline comparison

`ff49_zero_baseline.json` and `ff49_momentum_baseline.json` use the identical
canonical input hash, 1,000-month initial training window, one-month embargo,
186 holdout months, top/bottom-five sleeve, and 10-basis-point cost assumption
as the ridge screen. The zero baseline has no trainable parameters; it retains
the split metadata solely to make the comparison exact.

Every committed result now embeds the validated input-sidecar manifest and its
SHA-256 alongside the canonical CSV hash. This preserves the exact source URL,
archive digest, retrieval timestamp, schema, and row count used by the run,
without committing the provider's raw archive or CSV.

| Score source | Mean rank IC | Compounded gross return | Compounded net return | Avg. turnover |
| --- | ---: | ---: | ---: | ---: |
| Neutral zero score | Not defined (all ties) | 0.00% | 0.00% | 0.000 |
| Direct lagged 12-1 momentum | 0.0311 | 309.61% | 269.64% | 0.555 |
| Ridge on lagged 12-1 momentum | -0.0444 | -93.41% | -94.10% | 0.585 |

This is a useful *failure contrast*, not an outperformance claim. On this
single historical industry-portfolio screen, the direct point-in-time momentum
ordering had positive historical ranking and portfolio diagnostics while the
specified ridge configuration did not. It does not establish that momentum is
profitable, that regularization caused the difference, or that either result
will persist in other universes, periods, regimes, or after unmodeled costs.
The next smallest research task is to diagnose the divergence by month and
regime before selecting another model family.

## Month-level divergence audit

[`ff49_ridge_momentum_divergence.json`](ff49_ridge_momentum_divergence.json)
records rank IC and one-month gross portfolio return for both scores in every
holdout month. Ridge inverted the direct momentum ranking in 182 of 186 months
and preserved it in four. Because this screen has one feature, that is the
expected set of ranking behaviors for a fitted linear score: it can preserve or
reverse the raw feature order as its learned coefficient changes sign. This
identifies a sign-selection mechanism; it does not yet explain *why* the sign
was selected or whether it clusters by documented market regime.

## Initial regime grouping

[`ff49_ridge_momentum_by_regime.json`](ff49_ridge_momentum_by_regime.json)
aggregates the monthly audit using the small, source-linked registry in
[`config/regimes_v1.json`](../config/regimes_v1.json). The March--April 2020
recession label has only two months; the March 2022--July 2023 FOMC tightening
window has 17; the remaining 167 months are explicitly `normal_or_unlabeled`.
Those counts are too small and the registry too incomplete for a regime-level
claim. The report is retained as a reproducible descriptive slice and preserves
the monthly gross-return/cost limitation in its artifact.

## Feature drift audit

[`ff49_ridge_feature_drift.json`](ff49_ridge_feature_drift.json) records 186
holdout-month feature-drift observations, each standardized only with its own
expanding training window. It reports magnitude and training-range exceedance;
it does not claim that drift caused coefficient-sign selection or returns.
