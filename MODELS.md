# Supervised-model protocol

## Ridge regression: first model

The first supervised model is dependency-free ridge regression. It predicts the
next-month return from a frozen set of already standardized features, with an
unpenalized intercept and an L2 penalty on feature coefficients.

Ridge is intentionally the first comparator because its behavior is inspectable:
it gives a simple answer to whether feature information adds value beyond the
two baseline scores before the project moves to nonlinear models.

## Boundary rules

1. Call `standardize_train_test` for a walk-forward split before fitting.
2. Fit `RidgeRegressor` on transformed **training** observations only.
3. Call `predict` on transformed holdout observations; this method does not read
   their labels.
4. Preserve the feature schema. A missing or extra feature is a hard error.
5. Treat a prediction as a score for evaluation, not an investment
   recommendation or evidence of future returns.

`alpha` must be strictly positive. The solver uses deterministic partial
pivoting and does not require a scientific-computing dependency, which keeps the
first model portable and its linear algebra testable. Later adapters may use
scikit-learn but must implement the same schema and split boundaries.
