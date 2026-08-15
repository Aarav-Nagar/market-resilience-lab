import pytest

from market_resilience_lab.evaluation import calibration, rank_ic, summarize_rank_ic


def _rows(predictions: list[float], realized: list[float]) -> list[dict[str, float | str]]:
    return [
        {"asset": f"asset-{index}", "prediction": prediction, "realized_return": target}
        for index, (prediction, target) in enumerate(zip(predictions, realized, strict=True))
    ]


def test_rank_ic_uses_average_ranks_for_ties() -> None:
    value = rank_ic(_rows([1.0, 1.0, 3.0], [1.0, 2.0, 3.0]))

    assert value == pytest.approx(0.8660254038)


def test_constant_cross_section_is_unscorable_not_zero() -> None:
    summary = summarize_rank_ic([_rows([0.0, 0.0], [0.1, -0.1])])

    assert summary.mean_rank_ic is None
    assert summary.scored_periods == 0
    assert summary.unscorable_periods == 1


def test_calibration_reports_perfect_linear_relationship() -> None:
    diagnostics = calibration(_rows([-1.0, 0.0, 1.0], [-1.0, 2.0, 5.0]))

    assert diagnostics.intercept == pytest.approx(2.0)
    assert diagnostics.slope == pytest.approx(3.0)
    assert diagnostics.mean_error == pytest.approx(0.0)
    assert diagnostics.mean_squared_error == pytest.approx(0.0)


def test_calibration_handles_constant_predictions_without_fake_slope() -> None:
    diagnostics = calibration(_rows([2.0, 2.0], [0.0, 2.0]))

    assert diagnostics.intercept == 1.0
    assert diagnostics.slope is None
    assert diagnostics.mean_squared_error == 1.0


def test_calibration_allows_the_same_asset_in_different_holdout_months() -> None:
    rows = [
        {"asset": "A", "prediction": 0.0, "realized_return": 0.0},
        {"asset": "A", "prediction": 1.0, "realized_return": 1.0},
    ]

    diagnostics = calibration(rows)

    assert diagnostics.slope == 1.0
