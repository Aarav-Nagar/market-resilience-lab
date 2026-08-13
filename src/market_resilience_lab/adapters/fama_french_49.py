"""Adapter for the Fama--French 49 Industry Portfolios monthly CSV archive.

This module downloads provider data on demand, never bundles it, and emits the
project's canonical point-in-time schema with a digest for reproducibility.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile


ARCHIVE_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    "49_Industry_Portfolios_CSV.zip"
)
MISSING_RETURN_PERCENT = -99.0


@dataclass(frozen=True)
class IndustryReturnMonth:
    """One monthly cross-section of provider-supplied industry returns."""

    as_of: date
    returns: dict[str, float | None]


def download_archive(url: str = ARCHIVE_URL) -> bytes:
    """Download the provider archive without persisting it in the repository."""
    with urlopen(url, timeout=60) as response:
        return response.read()


def parse_value_weighted_monthly(archive_bytes: bytes) -> list[IndustryReturnMonth]:
    """Parse only the archive's value-weighted monthly return table.

    Returns in the provider CSV are percentages and are converted to decimal
    simple returns. Provider missing-value sentinels (such as -99.99) become
    ``None`` so an observation builder must explicitly skip incomplete windows.
    """
    with ZipFile(BytesIO(archive_bytes)) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise ValueError("expected exactly one CSV file in provider archive")
        text = archive.read(csv_names[0]).decode("latin-1")

    lines = text.splitlines()
    try:
        table_start = next(
            index
            for index, line in enumerate(lines)
            if line.strip() == "Average Value Weighted Returns -- Monthly"
        )
    except StopIteration as error:
        raise ValueError("value-weighted monthly table not found in provider archive") from error

    reader = csv.reader(lines[table_start + 1 :])
    header = next(reader, None)
    if header is None or len(header) < 2:
        raise ValueError("monthly table has no header")
    assets = [asset.strip() for asset in header[1:]]
    if len(assets) != 49 or len(set(assets)) != len(assets):
        raise ValueError("expected 49 unique industry portfolio columns")

    months: list[IndustryReturnMonth] = []
    for row in reader:
        if not row or not row[0].strip().isdigit() or len(row[0].strip()) != 6:
            break
        if len(row) != len(assets) + 1:
            raise ValueError(f"unexpected value count for {row[0].strip()}")
        year_month = row[0].strip()
        year, month = int(year_month[:4]), int(year_month[4:])
        as_of = _month_end(year, month)
        returns = {asset: _parse_percent(value) for asset, value in zip(assets, row[1:])}
        months.append(IndustryReturnMonth(as_of=as_of, returns=returns))
    if not months:
        raise ValueError("monthly table contained no data rows")
    return months


def build_momentum_observations(months: list[IndustryReturnMonth]) -> list[dict[str, str | float]]:
    """Build canonical rows with 12-1 momentum and the next month's label.

    At month *t* close, the feature compounds returns t-12 through t-1. The
    next-month return t+1 becomes the label. Windows containing a provider
    missing value are omitted rather than imputed.
    """
    if len(months) < 14:
        raise ValueError("at least 14 monthly cross-sections are required")
    assets = list(months[0].returns)
    if any(list(month.returns) != assets for month in months[1:]):
        raise ValueError("industry columns must remain consistent across months")

    rows: list[dict[str, str | float]] = []
    for index in range(12, len(months) - 1):
        current, label_month = months[index], months[index + 1]
        trailing = months[index - 12 : index]
        for asset in assets:
            history = [month.returns[asset] for month in trailing]
            label_return = label_month.returns[asset]
            if label_return is None or any(value is None for value in history):
                continue
            momentum = 1.0
            for value in history:
                momentum *= 1.0 + float(value)
            rows.append(
                {
                    "asset": asset,
                    "as_of": current.as_of.isoformat(),
                    "available_at": current.as_of.isoformat(),
                    "label_end": label_month.as_of.isoformat(),
                    "label_return": float(label_return),
                    "feature__mom_12_1": momentum - 1.0,
                }
            )
    return rows


def write_observations(output_path: str | Path, archive_bytes: bytes) -> dict[str, str | int]:
    """Parse archive and write canonical CSV plus a reproducibility manifest."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = build_momentum_observations(parse_value_weighted_monthly(archive_bytes))
    fieldnames = [
        "asset",
        "as_of",
        "available_at",
        "label_end",
        "label_return",
        "feature__mom_12_1",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    manifest: dict[str, str | int] = {
        "source_url": ARCHIVE_URL,
        "archive_sha256": hashlib.sha256(archive_bytes).hexdigest(),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "row_count": len(rows),
        "schema": "market-resilience-lab canonical observation CSV v1",
    }
    path.with_suffix(path.suffix + ".manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def _parse_percent(value: str) -> float | None:
    parsed = float(value.strip())
    return None if parsed <= MISSING_RETURN_PERCENT else parsed / 100.0


def _month_end(year: int, month: int) -> date:
    if not 1 <= month <= 12:
        raise ValueError(f"invalid month in provider data: {month}")
    return date(year, month, monthrange(year, month)[1])


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m market_resilience_lab.adapters.fama_french_49 OUTPUT.csv")
    manifest = write_observations(sys.argv[1], download_archive())
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
