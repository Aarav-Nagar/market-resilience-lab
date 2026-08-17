# Regime registry

`config/regimes_v1.json` is a deliberately small, source-linked registry for
the first regime audit. Intervals are inclusive, non-overlapping, and assigned
from each result row's `as_of` month. Months outside an interval receive
`normal_or_unlabeled`; this is a residual bucket, not an assertion of normality.

| Label | Inclusive months | Definition and source |
| --- | --- | --- |
| `covid_recession_nber_trough` | 2020-03 through 2020-04 | FRED's monthly USREC trough-method convention, which maps NBER business-cycle dates to recession shading. [USREC notes](https://fred.stlouisfed.org/series/USREC) |
| `fomc_tightening_2022_2023` | 2022-03 through 2023-07 | Inclusive window from the March 2022 FOMC rate increase to the July 2023 increase. This is a policy-window label, not proof that policy caused any observed outcome. [March 2022](https://www.federalreserve.gov/newsevents/pressreleases/monetary20220316a.htm), [July 2023](https://www.federalreserve.gov/newsevents/pressreleases/monetary20230726a.htm) |

The registry does not yet cover every historical episode. New intervals must
cite a primary source, explain their date rule, and pass the overlap guardrail.

## Reproduce the descriptive report

```powershell
python -m market_resilience_lab.experiments.regime_report `
  results/ff49_ridge_momentum_divergence.json config/regimes_v1.json `
  results/ff49_ridge_momentum_by_regime.json
```
