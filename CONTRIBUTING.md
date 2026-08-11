# Contributing

Contributions should improve research validity, reproducibility, or usability.

- Keep commits small and independently reviewable; do not create activity-only
  commits, generated-data commits, or placeholder work.
- Add focused tests for behavior changes, especially split boundaries, timestamp
  availability, metric calculations, and leakage controls.
- Record exact commands, configuration, seed, data version/hash, and package
  versions for any reported experiment.
- State limitations. Do not convert a historical association into a causal or
  future-performance claim.
- Keep data adapters separate from generated data. Respect source licenses and
  redistribution terms.

Before opening a pull request, run `python -m pytest` and include the output in
the PR description.
