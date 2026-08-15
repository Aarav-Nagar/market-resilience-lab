"""Leakage-aware building blocks for Market Resilience Lab."""

from .metrics import PortfolioMetrics, evaluate_long_short_portfolio
from .splits import WalkForwardSplit, expanding_window_splits
from .data_contract import Observation, load_observations_csv
from .baselines import ScoredObservation, lagged_momentum_score, zero_score
from .preprocessing import FeatureStandardizer, standardize_train_test
from .models import RidgeRegressor
from .evaluation import CalibrationDiagnostics, RankDiagnostics, calibration, rank_ic, summarize_rank_ic

__all__ = [
    "PortfolioMetrics",
    "Observation",
    "ScoredObservation",
    "FeatureStandardizer",
    "RidgeRegressor",
    "CalibrationDiagnostics",
    "RankDiagnostics",
    "WalkForwardSplit",
    "evaluate_long_short_portfolio",
    "expanding_window_splits",
    "lagged_momentum_score",
    "calibration",
    "load_observations_csv",
    "standardize_train_test",
    "rank_ic",
    "summarize_rank_ic",
    "zero_score",
]
