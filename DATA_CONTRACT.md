# Data contract and adapter gate

Market Resilience Lab accepts an experiment dataset only when every feature has
an auditable availability time. This avoids a common but subtle failure: a row
dated at month-end can accidentally contain accounting or corporate-action data
that was not public until later.

## Canonical observation schema

One row represents one asset at one signal-formation date. CSV adapters must
produce these required columns:

| Column | Meaning | Constraint |
| --- | --- | --- |
| `asset` | Stable asset identifier | Unique within an `as_of` date |
| `as_of` | Signal-formation date, ISO `YYYY-MM-DD` | Dataset is strictly chronological |
| `available_at` | Latest time at which all feature values in the row were known | Must be on or before `as_of` |
| `label_end` | End of the future return horizon | Must be after `as_of` |
| `label_return` | Realized simple return over the declared horizon | May not be used as a feature |
| `feature__*` | Numeric model inputs | At least one is required |

The `available_at` field is conservative: it must be the maximum availability
time across all features in a row. Adapters with feature-level release times may
either validate them independently or store their maximum in this field.

## Before adding a data adapter

An adapter PR must add a source note that states:

1. Provider, dataset/version, retrieval date, and license/redistribution terms.
2. The equity-universe rule and whether delisted securities are included. If
   they are not, results must carry a survivorship-bias warning.
3. Corporate-action adjustment policy and whether prices are adjusted.
4. How every feature's public availability time is derived.
5. The exact label-horizon calculation, missing-data policy, and data checksum.

No model result belongs in the README until its adapter passes these checks and
the experiment captures the input hash and configuration. The repository does
not ship market data or claim that a provider is survivorship-free by default.

## Minimal adapter output

```csv
asset,as_of,available_at,label_end,label_return,feature__mom_12_1
AAA,2020-01-31,2020-01-31,2020-02-29,0.03,0.18
```

Use `load_observations_csv` to validate an adapter output before splitting,
fitting, or backtesting.
