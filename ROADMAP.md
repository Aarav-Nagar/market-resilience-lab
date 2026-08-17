# Research roadmap

## Milestone 1 — Reproducible experiment contract

- [x] Define and enforce the prediction task's point-in-time data rules.
- [x] Implement expanding-window splits with a label-horizon embargo.
- [x] Implement deterministic cross-sectional portfolio metrics with costs.
- [x] Specify a versioned public data adapter and licensing note.

## Milestone 2 — Baselines before complexity

- [x] Add a zero-score baseline and a simple momentum baseline.
- [x] Add a per-window preprocessing pipeline that fits only on training data.
- [x] Report tie-aware ranking, calibration, turnover, and cost-adjusted return metrics.
- [x] Connect the source, split, preprocessing, ridge, and evaluation layers in one runner.

## Milestone 3 — Comparable supervised models

- [x] Add an inspectable ridge-regression reference model.
- [ ] Add regularized linear, k-nearest-neighbor, SVM, tree, random-forest,
      extra-trees, and histogram-gradient-boosting adapters.
- [ ] Persist each run's configuration, seed, package versions, and data hash.
- [ ] Produce Model Resilience Cards from a common result schema.

## Milestone 4 — Regime and failure analysis

- [x] Define initial regime intervals with sources and non-overlapping labeling rules.
- [ ] Add calibration and data-drift diagnostics.
- [ ] Build the Regime Stress Test report/dashboard.
- [x] Maintain a public `WHAT_BROKE.md` log for failed or inconclusive findings.

## Out of scope until explicitly approved

- Brokerage execution, account access, or personalized recommendations.
- Paid, private, or redistribution-restricted data.
- Claims of investable outperformance without a documented dataset and completed
  leakage, cost, and robustness checks.
