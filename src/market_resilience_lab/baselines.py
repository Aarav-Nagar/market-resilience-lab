"""Transparent score baselines for leakage-aware supervised-model comparisons."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from .data_contract import Observation


@dataclass(frozen=True)
class ScoredObservation:
    """A model-independent prediction tied to its formation date and asset."""

    asset: str
    as_of: date
    prediction: float


def zero_score(observations: Iterable[Observation]) -> list[ScoredObservation]:
    """Return a neutral score for every validated observation.

    Equal scores are intentional. A downstream portfolio constructor must not
    break this tie based on asset names and present the result as a strategy.
    """
    return [
        ScoredObservation(asset=row.asset, as_of=row.as_of, prediction=0.0)
        for row in observations
    ]


def lagged_momentum_score(
    observations: Iterable[Observation], *, feature_name: str = "mom_12_1"
) -> list[ScoredObservation]:
    """Use a validated, adapter-supplied lagged feature as an interpretable score.

    The point-in-time loader verifies that feature availability predates the
    formation date. This function never accesses the future label.
    """
    scores: list[ScoredObservation] = []
    for row in observations:
        try:
            prediction = row.features[feature_name]
        except KeyError as error:
            raise ValueError(
                f"{feature_name!r} is required for lagged_momentum_score; "
                f"missing for {row.asset} on {row.as_of}"
            ) from error
        scores.append(
            ScoredObservation(
                asset=row.asset, as_of=row.as_of, prediction=prediction
            )
        )
    return scores
