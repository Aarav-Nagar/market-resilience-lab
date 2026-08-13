from datetime import date

import pytest

from market_resilience_lab.baselines import lagged_momentum_score, zero_score
from market_resilience_lab.data_contract import Observation


def _observation(asset: str, momentum: float = 0.15) -> Observation:
    return Observation(
        asset=asset,
        as_of=date(2020, 1, 31),
        available_at=date(2020, 1, 31),
        label_end=date(2020, 2, 29),
        label_return=-0.25,
        features={"mom_12_1": momentum},
    )


def test_zero_score_is_neutral_for_every_observation() -> None:
    scores = zero_score([_observation("BBB"), _observation("AAA")])

    assert [(score.asset, score.prediction) for score in scores] == [
        ("BBB", 0.0),
        ("AAA", 0.0),
    ]


def test_momentum_baseline_reads_feature_not_future_label() -> None:
    scores = lagged_momentum_score([_observation("AAA", momentum=0.12)])

    assert scores[0].prediction == 0.12
    assert scores[0].as_of == date(2020, 1, 31)


def test_momentum_baseline_rejects_missing_declared_feature() -> None:
    observation = _observation("AAA")
    observation = Observation(
        asset=observation.asset,
        as_of=observation.as_of,
        available_at=observation.available_at,
        label_end=observation.label_end,
        label_return=observation.label_return,
        features={"value": 1.0},
    )

    with pytest.raises(ValueError, match="mom_12_1.*missing"):
        lagged_momentum_score([observation])
