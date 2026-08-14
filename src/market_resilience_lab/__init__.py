"""Leakage-aware building blocks for Market Resilience Lab."""

from .metrics import PortfolioMetrics, evaluate_long_short_portfolio
from .splits import WalkForwardSplit, expanding_window_splits
from .data_contract import Observation, load_observations_csv
from .baselines import ScoredObservation, lagged_momentum_score, zero_score
from .preprocessing import FeatureStandardizer, standardize_train_test

__all__ = [
    "PortfolioMetrics",
    "Observation",
    "ScoredObservation",
    "FeatureStandardizer",
    "WalkForwardSplit",
    "evaluate_long_short_portfolio",
    "expanding_window_splits",
    "lagged_momentum_score",
    "load_observations_csv",
    "standardize_train_test",
    "zero_score",
]
