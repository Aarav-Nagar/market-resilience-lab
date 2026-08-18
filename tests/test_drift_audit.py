from datetime import date
from market_resilience_lab.data_contract import Observation
from market_resilience_lab.experiments.drift_audit import run_drift_audit
from market_resilience_lab.experiments.provenance import InputProvenance
from market_resilience_lab.experiments.ridge_walk_forward import RidgeWalkForwardConfig

def test_drift_audit_uses_only_train_window_statistics() -> None:
    rows = [Observation(a, date(2020,m,28), date(2020,m,28), date(2020,min(m+1,12),28), y, {"mom_12_1": x}) for m in range(1,7) for a,x,y in (("A",-1.,-.01),("B",1.,.01))]
    audit = run_drift_audit(rows, config=RidgeWalkForwardConfig(min_train_periods=2, embargo_periods=1, sleeve_size=1), input_provenance=InputProvenance("x",None,None))
    assert len(audit["months"]) == 3
    assert all(0 <= item["outside_training_range_share"] <= 1 for item in audit["months"])
