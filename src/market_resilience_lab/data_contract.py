"""Point-in-time observation validation for data adapters.

The loader intentionally validates timestamps before it exposes model features.
This makes a future-label or late-available feature a hard error rather than a
quietly optimistic model result.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from math import isfinite
from pathlib import Path
from typing import Mapping


REQUIRED_COLUMNS = frozenset(
    {"asset", "as_of", "available_at", "label_end", "label_return"}
)
FEATURE_PREFIX = "feature__"


@dataclass(frozen=True)
class Observation:
    """One validated, point-in-time cross-sectional model observation."""

    asset: str
    as_of: date
    available_at: date
    label_end: date
    label_return: float
    features: Mapping[str, float]


def load_observations_csv(path: str | Path) -> list[Observation]:
    """Load and validate a canonical adapter CSV.

    The returned observations are sorted chronologically. Rows cannot contain a
    label that ends on/before the signal date, a feature known after the signal
    date, duplicate asset/date pairs, or non-numeric feature values.
    """
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")
        feature_columns = sorted(column for column in columns if column.startswith(FEATURE_PREFIX))
        if not feature_columns:
            raise ValueError(f"at least one {FEATURE_PREFIX} feature column is required")

        observations = [
            _parse_row(row, row_number, feature_columns)
            for row_number, row in enumerate(reader, start=2)
        ]

    seen = set()
    for observation in observations:
        key = (observation.asset, observation.as_of)
        if key in seen:
            raise ValueError(f"duplicate asset/as_of pair: {observation.asset} on {observation.as_of}")
        seen.add(key)
    return sorted(observations, key=lambda row: (row.as_of, row.asset))


def _parse_row(
    row: Mapping[str, str | None], row_number: int, feature_columns: list[str]
) -> Observation:
    try:
        asset = _require_text(row, "asset")
        as_of = date.fromisoformat(_require_text(row, "as_of"))
        available_at = date.fromisoformat(_require_text(row, "available_at"))
        label_end = date.fromisoformat(_require_text(row, "label_end"))
        label_return = float(_require_text(row, "label_return"))
        features = {
            column.removeprefix(FEATURE_PREFIX): float(_require_text(row, column))
            for column in feature_columns
        }
    except ValueError as error:
        raise ValueError(f"invalid value in CSV row {row_number}: {error}") from error

    if available_at > as_of:
        raise ValueError(
            f"CSV row {row_number}: available_at {available_at} is after as_of {as_of}"
        )
    if label_end <= as_of:
        raise ValueError(
            f"CSV row {row_number}: label_end {label_end} must be after as_of {as_of}"
        )
    if not isfinite(label_return) or any(not isfinite(value) for value in features.values()):
        raise ValueError(f"CSV row {row_number}: labels and features must be finite")
    return Observation(
        asset=asset,
        as_of=as_of,
        available_at=available_at,
        label_end=label_end,
        label_return=label_return,
        features=features,
    )


def _require_text(row: Mapping[str, str | None], column: str) -> str:
    value = row.get(column)
    if value is None or not value.strip():
        raise ValueError(f"{column} is required")
    return value.strip()
