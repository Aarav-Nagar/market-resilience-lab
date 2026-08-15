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

The result is retained because the project asks when models break. The next
experiments should compare the zero and momentum baselines under the exact same
splits, then add uncertainty and regime diagnostics before judging any model
family.
