import hashlib

import pytest

from market_resilience_lab.experiments.provenance import load_input_provenance


def test_load_input_provenance_binds_csv_and_sidecar_manifest(tmp_path) -> None:
    csv_path = tmp_path / "observations.csv"
    csv_path.write_text("asset,as_of\nA,2020-01-31\n", encoding="utf-8")
    manifest = b'{"archive_sha256":"archive","row_count":1}\n'
    manifest_path = csv_path.with_suffix(".csv.manifest.json")
    manifest_path.write_bytes(manifest)

    provenance = load_input_provenance(csv_path)

    assert provenance.input_sha256 == hashlib.sha256(csv_path.read_bytes()).hexdigest()
    assert provenance.manifest_sha256 == hashlib.sha256(manifest).hexdigest()
    assert provenance.manifest == {"archive_sha256": "archive", "row_count": 1}


def test_load_input_provenance_rejects_nested_manifest(tmp_path) -> None:
    csv_path = tmp_path / "observations.csv"
    csv_path.write_text("content", encoding="utf-8")
    csv_path.with_suffix(".csv.manifest.json").write_text('{"nested": {}}', encoding="utf-8")

    with pytest.raises(ValueError, match="flat object"):
        load_input_provenance(csv_path)
