from __future__ import annotations

from pathlib import Path


FORBIDDEN_SOURCE_TOKENS = (
    "import subprocess",
    "from subprocess",
    "import socket",
    "from socket",
    "import requests",
    "from requests",
    "import httpx",
    "from httpx",
    "urllib.request",
    "os.system(",
    "os.popen(",
    "shell=True",
)


def test_agent_core_has_no_shell_or_network_mutation_client() -> None:
    source_root = Path(__file__).resolve().parents[1] / "src" / "agent_ops"
    violations: list[str] = []
    for path in sorted(source_root.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_SOURCE_TOKENS:
            if token in text:
                violations.append(f"{path.relative_to(source_root)}: {token}")
    assert violations == []
