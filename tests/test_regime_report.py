import json

from market_resilience_lab.experiments.regime_report import summarize_audit_by_regime


def test_summarizes_months_by_inclusive_regime_labels(tmp_path) -> None:
    registry = tmp_path / "regimes.json"
    registry.write_text(json.dumps({"unlabeled_value": "other", "intervals": [{"name": "episode", "start": "2020-03-01", "end": "2020-04-30", "source_url": "s", "rationale": "r"}]}), encoding="utf-8")
    audit = {"experiment": "audit", "months": [
        {"as_of": "2020-03-31", "ridge_rank_ic": -0.2, "momentum_rank_ic": 0.2, "ridge_gross_return": -0.01, "momentum_gross_return": 0.01, "rank_ic_difference": -0.4},
        {"as_of": "2020-05-31", "ridge_rank_ic": 0.1, "momentum_rank_ic": -0.1, "ridge_gross_return": 0.01, "momentum_gross_return": -0.01, "rank_ic_difference": 0.2},
    ]}
    report = summarize_audit_by_regime(audit, registry_path=registry)
    assert report["summaries"]["episode"]["months"] == 1
    assert report["summaries"]["episode"]["inverted_rank_order_months"] == 1
    assert report["summaries"]["other"]["mean_ridge_rank_ic"] == 0.1
