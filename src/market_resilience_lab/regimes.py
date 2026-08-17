"""Validated, source-linked date labels for regime-stratified research."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class RegimeInterval:
    name: str
    start: date
    end: date
    source_url: str
    rationale: str


def load_regimes(path: str | Path) -> tuple[RegimeInterval, ...]:
    """Load non-overlapping inclusive date intervals from a versioned registry."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    intervals = tuple(
        RegimeInterval(
            name=item["name"], start=date.fromisoformat(item["start"]), end=date.fromisoformat(item["end"]),
            source_url=item["source_url"], rationale=item["rationale"],
        )
        for item in payload["intervals"]
    )
    if any(not item.name or not item.source_url or item.start > item.end for item in intervals):
        raise ValueError("regime intervals require names, sources, and valid dates")
    ordered = sorted(intervals, key=lambda item: item.start)
    if any(left.end >= right.start for left, right in zip(ordered, ordered[1:])):
        raise ValueError("regime intervals must not overlap")
    return intervals


def label_periods(periods: Iterable[date], intervals: Iterable[RegimeInterval], *, default: str) -> dict[date, str]:
    """Assign each period at most one inclusive interval label."""
    registry = tuple(intervals)
    return {
        period: next((item.name for item in registry if item.start <= period <= item.end), default)
        for period in periods
    }
