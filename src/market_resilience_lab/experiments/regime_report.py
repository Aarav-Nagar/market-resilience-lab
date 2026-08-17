"""Aggregate completed month-level audit evidence by validated regime labels."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from ..regimes import label_periods, load_regimes


def summarize_audit_by_regime(audit: dict[str, object], *, registry_path: str | Path) -> dict[str, object]:
    """Return descriptive, non-causal summaries for an audit's completed months."""
    months = audit["months"]
    if not isinstance(months, list):
        raise ValueError("audit must contain a months list")
    registry_payload = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    intervals = load_regimes(registry_path)
    default = registry_payload["unlabeled_value"]
    parsed_dates = [date.fromisoformat(row["as_of"]) for row in months]
    labels = label_periods(parsed_dates, intervals, default=default)
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row, period in zip(months, parsed_dates, strict=True):
        groups[labels[period]].append(row)

    summaries: dict[str, dict[str, float | int]] = {}
    for label, rows in sorted(groups.items()):
        summaries[label] = {
            "months": len(rows),
            "mean_ridge_rank_ic": _mean(rows, "ridge_rank_ic"),
            "mean_momentum_rank_ic": _mean(rows, "momentum_rank_ic"),
            "mean_ridge_gross_return": _mean(rows, "ridge_gross_return"),
            "mean_momentum_gross_return": _mean(rows, "momentum_gross_return"),
            "inverted_rank_order_months": sum(row["rank_ic_difference"] is not None and row["rank_ic_difference"] < 0 for row in rows),
        }
    return {
        "experiment": "ridge_momentum_regime_report_v1",
        "audit_experiment": audit.get("experiment"),
        "audit_input_provenance": audit.get("input_provenance"),
        "registry": registry_payload,
        "summaries": summaries,
        "limitations": [
            "Descriptive historical grouping only; no causal or outperformance claim.",
            "The normal_or_unlabeled bucket includes all months outside the small initial registry.",
            "Gross monthly returns exclude sequential turnover costs; use aggregate artifacts for cost-aware results.",
        ],
    }


def _mean(rows: list[dict[str, object]], key: str) -> float:
    values = [float(row[key]) for row in rows if row[key] is not None]
    return sum(values) / len(values) if values else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit_json")
    parser.add_argument("registry_json")
    parser.add_argument("output_json")
    args = parser.parse_args()
    audit = json.loads(Path(args.audit_json).read_text(encoding="utf-8"))
    report = summarize_audit_by_regime(audit, registry_path=args.registry_json)
    Path(args.output_json).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
