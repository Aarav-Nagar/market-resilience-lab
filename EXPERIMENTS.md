# Walk-forward experiment protocol

`ridge_walk_forward` is the first complete experiment runner. It connects the
canonical input CSV, embargoed expanding-window splits, training-only
preprocessing, ridge regression, prediction diagnostics, and a cost-aware
long/short portfolio calculation.

## Default configuration

- 120 initial monthly training periods
- 1-month label-horizon embargo
- 1-month test window advanced one month at a time
- ridge alpha of 1.0
- top/bottom five industry portfolios with 10 basis points of one-way costs

The defaults are a reproducible methodology demonstration, not tuned choices or
an investment strategy. The JSON result records every setting, the canonical
input SHA-256, counts of scored/unscorable months, and the diagnostics. Result
writes are atomic so an interrupted run cannot leave a partial evidence file.

The committed initial screen uses a 1,000-month training window instead of the
120-month default so the full historical run remains bounded in the local
execution environment. Its exact configuration and negative outcome are in
`results/README.md` and `results/ff49_ridge_initial.json`.

## Run the initial demonstration

```powershell
python -m market_resilience_lab.adapters.fama_french_49 output/ff49_observations.csv
python -m market_resilience_lab.experiments.ridge_walk_forward `
  output/ff49_observations.csv results/ff49_ridge_initial.json
```

Interpret this as a historical industry-portfolio methodology screen only. The
source limitations in `DATA_SOURCES.md`, the no-investment-advice disclaimer,
and the absence of uncertainty intervals still apply.
