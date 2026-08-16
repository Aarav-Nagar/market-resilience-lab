from datetime import date

from market_resilience_lab.data_contract import Observation
from market_resilience_lab.experiments.divergence_audit import run_divergence_audit
from market_resilience_lab.experiments.provenance import InputProvenance
from market_resilience_lab.experiments.ridge_walk_forward import RidgeWalkForwardConfig


def test_audit_uses_identical_embargoed_months_for_both_scores() -> None:
    rows = [
        Observation(asset=asset, as_of=date(2020, month, 28), available_at=date(2020, month, 28),
                    label_end=date(2020, min(month + 1, 12), 28), label_return=label,
                    features={"mom_12_1": feature + month * .01})
        for month in range(1, 7)
        for asset, feature, label in (("A", -1.0, -.01), ("B", 1.0, .01))
    ]
    audit = run_divergence_audit(
        rows,
        config=RidgeWalkForwardConfig(min_train_periods=2, embargo_periods=1, sleeve_size=1),
        input_provenance=InputProvenance("input", None, None),
    )

    assert [month.as_of for month in audit.months] == ["2020-04-28", "2020-05-28", "2020-06-28"]
    assert all(month.ridge_rank_ic is not None for month in audit.months)
    assert all(month.momentum_rank_ic is not None for month in audit.months)
    assert sum(audit.rank_order_summary.values()) == 3
