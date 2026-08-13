# Data sources

## Fama--French 49 Industry Portfolios (first adapter)

The first supported adapter downloads the **value-weighted monthly 49 Industry
Portfolios** directly from the [Kenneth R. French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html).
The provider describes the portfolios as NYSE, AMEX, and NASDAQ stocks assigned
to industries using SIC codes at the end of June, then held from July through
June. The Library also warns that it reconstructs historical returns when the
underlying CRSP data are updated. [Dataset detail](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/det_30_ind_port.html)

### Why this is the first adapter

It provides a small, long monthly cross-section that lets the project exercise
the full time-safe evaluation pipeline without redistributing CRSP data or
claiming stock-level coverage. Each industry portfolio is treated as an asset
in the initial **methodology demonstration**, not as a tradable security.

### Boundaries

- The adapter downloads directly from the provider and the repository does not
  include the raw archive. The source file is copyrighted by Eugene F. Fama and
  Kenneth R. French; users must review the provider's current terms before any
  separate redistribution or commercial use.
- It is **not** a survivorship-free individual-stock universe. Its aggregate
  construction cannot support claims about individual-stock selection.
- Industry returns are provider-produced, value-weighted total returns. The
  adapter does not infer constituents, prices, corporate actions, or intramonth
  availability.
- A monthly signal forms only after month-end. `mom_12_1` compounds returns
  from months *t-12* through *t-1*; the label is return in *t+1*. This avoids
  using the label or same-month return as a feature.
- The Library can revise its history. Every future experiment must record the
  downloaded archive's SHA-256 digest and retrieval timestamp.

### Reproduce the adapter output

```powershell
python -m market_resilience_lab.adapters.fama_french_49 output/ff49_observations.csv
```

The command writes a canonical observation CSV and prints the provider URL,
archive SHA-256, and row count. Review its manifest before treating the output
as an experiment input.
