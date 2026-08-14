# Training-only preprocessing

Feature scaling is fitted **inside each walk-forward training window**. The
holdout window is transformed using those frozen training statistics; it never
changes the mean or scale. This is necessary even for a simple momentum feature:
using the test-period distribution would leak future cross-sectional information
into the model-input transformation.

## Contract

`standardize_train_test(train, test)` requires both inputs to use the same
non-empty feature schema. It returns a fitted `FeatureStandardizer` and two
transformed collections.

- Mean: arithmetic mean from the training rows only.
- Scale: population standard deviation from the training rows only.
- Constant training features: transformed to zero and recorded in
  `constant_features`; they are not silently divided by zero.
- Missing, extra, or non-finite feature values: hard errors.

The scaler has no data-splitting logic by design. The experiment runner must
produce `train` and `test` using the embargoed expanding-window splitter first,
then call this function for each split. The function's explicit two-input API
makes the training/holdout boundary reviewable in code and tests.
