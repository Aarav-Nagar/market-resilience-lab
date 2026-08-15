# Prediction evaluation

Market Resilience Lab keeps **prediction** and **portfolio** evidence separate.
A model can rank assets well yet fail after turnover and costs, or produce an
apparently attractive portfolio while being poorly calibrated. Both views are
reported from the same holdout rows.

## Cross-sectional rank IC

For each evaluation month, `rank_ic` computes Spearman correlation between
predictions and realized returns. Tied values receive average ranks. A month
with constant predictions or constant realized returns is marked unscorable and
excluded from the mean; it is never converted into a zero or a favorable score.

## Calibration

`calibration` fits the descriptive holdout relationship
`realized_return = intercept + slope * prediction` and reports mean error and
mean squared error. It is not a causal model or a forecast of future accuracy.
Constant predictions have a defined mean error/MSE but no slope.

## Portfolio evidence

Use `evaluate_long_short_portfolio` on the same rows to report gross return,
turnover, transaction cost, and net return. The evaluation runner will later
combine this module with regimes and confidence intervals. No single metric is
treated as proof of investability.
