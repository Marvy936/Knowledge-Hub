from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    docs = root / "docs"
    docs.mkdir(parents=True)
    (docs / "guide.md").write_text(
        "# Guide\n\nDeterministic retrieval begins with deterministic source identity.\n\n## Recovery\n\nNo data is not success.\n",
        encoding="utf-8",
    )
    return root


def test_module_help_exposes_corpus_commands() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "knowledge_hub_rag", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "snapshot" in completed.stdout
    assert "verify-snapshot" in completed.stdout
    assert "chunk" in completed.stdout
    assert "validate-chunks" in completed.stdout


def test_cli_snapshot_chunk_and_readback(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    snapshot_path = tmp_path / "snapshot.json"
    chunks_path = tmp_path / "chunks.json"
    revision = "b" * 40

    snapshot = subprocess.run(
        [
            sys.executable,
            "-m",
            "knowledge_hub_rag",
            "snapshot",
            "--repo-root",
            str(root),
            "--source-revision",
            revision,
            "--output",
            str(snapshot_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert snapshot.returncode == 0, snapshot.stderr
    snapshot_result = json.loads(snapshot.stdout)
    assert snapshot_result["status"] == "corpus_snapshot_recorded"

    verify = subprocess.run(
        [
            sys.executable,
            "-m",
            "knowledge_hub_rag",
            "verify-snapshot",
            "--repo-root",
            str(root),
            "--snapshot",
            str(snapshot_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert verify.returncode == 0, verify.stderr
    assert json.loads(verify.stdout)["status"] == "corpus_snapshot_verified"

    chunks = subprocess.run(
        [
            sys.executable,
            "-m",
            "knowledge_hub_rag",
            "chunk",
            "--repo-root",
            str(root),
            "--snapshot",
            str(snapshot_path),
            "--max-chars",
            "400",
            "--min-chars",
            "40",
            "--output",
            str(chunks_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert chunks.returncode == 0, chunks.stderr
    chunk_result = json.loads(chunks.stdout)
    assert chunk_result["status"] == "chunk_manifest_recorded"

    validate = subprocess.run(
        [
            sys.executable,
            "-m",
            "knowledge_hub_rag",
            "validate-chunks",
            "--repo-root",
            str(root),
            "--manifest",
            str(chunks_path),
            "--snapshot",
            str(snapshot_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert validate.returncode == 0, validate.stderr
    result = json.loads(validate.stdout)
    assert result["status"] == "chunk_manifest_valid"
    assert result["corpus_snapshot_id"] == snapshot_result["corpus_snapshot_id"]


def test_cli_refuses_changed_snapshot_bytes(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    snapshot_path = tmp_path / "snapshot.json"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "knowledge_hub_rag",
            "snapshot",
            "--repo-root",
            str(root),
            "--source-revision",
            "c" * 40,
            "--output",
            str(snapshot_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    (root / "docs" / "guide.md").write_text("# Changed\n", encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "knowledge_hub_rag",
            "verify-snapshot",
            "--repo-root",
            str(root),
            "--snapshot",
            str(snapshot_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 2
    assert json.loads(completed.stderr)["status"] == "refused"
