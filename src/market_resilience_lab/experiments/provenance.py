"""Input-digest and adapter-manifest provenance for completed experiments."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class InputProvenance:
    """Content-bound identity of a canonical CSV and its optional sidecar manifest."""

    input_sha256: str
    manifest_sha256: str | None
    manifest: dict[str, str | int] | None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def load_input_provenance(csv_path: str | Path) -> InputProvenance:
    """Load a canonical CSV's digest and validate its adjacent adapter manifest.

    The manifest is copied into completed result evidence so a result retains
    provider archive identity after the ignored local adapter output changes.
    """
    path = Path(csv_path)
    manifest_path = path.with_suffix(path.suffix + ".manifest.json")
    manifest: dict[str, str | int] | None = None
    manifest_sha256: str | None = None
    if manifest_path.exists():
        manifest_bytes = manifest_path.read_bytes()
        parsed = json.loads(manifest_bytes)
        if not isinstance(parsed, dict) or not all(
            isinstance(key, str) and isinstance(value, (str, int))
            for key, value in parsed.items()
        ):
            raise ValueError("input manifest must be a flat object with string or integer values")
        manifest = parsed
        manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    return InputProvenance(
        input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        manifest_sha256=manifest_sha256,
        manifest=manifest,
    )
