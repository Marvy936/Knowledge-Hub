#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LABS_ROOT = ROOT / "labs" / "interactive"
STATE_ROOT = ROOT / ".kh-labs"


class LabError(RuntimeError):
    pass


def load_manifest(lab_id: str) -> tuple[dict[str, Any], Path]:
    lab_dir = (LABS_ROOT / lab_id).resolve()
    if lab_dir.parent != LABS_ROOT.resolve():
        raise LabError(f"Invalid lab id: {lab_id}")
    manifest_path = lab_dir / "lab.json"
    if not manifest_path.is_file():
        raise LabError(f"Unknown lab '{lab_id}'. Run 'kh-lab list'.")
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    validate_manifest(manifest, lab_dir)
    return manifest, lab_dir


def validate_manifest(manifest: dict[str, Any], lab_dir: Path) -> None:
    required = {
        "id": str,
        "title": str,
        "type": str,
        "difficulty": str,
        "estimated_minutes": int,
        "compose_file": str,
        "project_name": str,
        "tasks": list,
        "hints": list,
        "checks": list,
    }
    for key, expected in required.items():
        if key not in manifest:
            raise LabError(f"{lab_dir}: missing manifest key '{key}'")
        if not isinstance(manifest[key], expected):
            raise LabError(f"{lab_dir}: '{key}' must be {expected.__name__}")
    if manifest["id"] != lab_dir.name:
        raise LabError(f"{lab_dir}: manifest id must equal directory name")
    compose_path = safe_child(lab_dir, manifest["compose_file"])
    if not compose_path.is_file():
        raise LabError(f"{lab_dir}: compose file does not exist: {compose_path}")
    for mapping in manifest.get("workspace_files", []):
        if not isinstance(mapping, dict) or "source" not in mapping or "target" not in mapping:
            raise LabError(f"{lab_dir}: invalid workspace_files entry")
        source = safe_child(lab_dir, mapping["source"])
        if not source.is_file():
            raise LabError(f"{lab_dir}: workspace source does not exist: {source}")
        safe_relative(mapping["target"])
    if "compose_env_file" in manifest:
        safe_relative(manifest["compose_env_file"])
    supported = {"service_running", "service_health", "compose_exec"}
    for check in manifest["checks"]:
        if not isinstance(check, dict) or check.get("type") not in supported:
            raise LabError(f"{lab_dir}: unsupported check: {check}")


def safe_relative(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise LabError(f"Unsafe relative path: {value}")
    return path


def safe_child(parent: Path, relative: str) -> Path:
    rel = safe_relative(relative)
    result = (parent / rel).resolve()
    if parent.resolve() not in result.parents and result != parent.resolve():
        raise LabError(f"Path escapes lab directory: {relative}")
    return result


def workspace_for(lab_id: str) -> Path:
    return STATE_ROOT / lab_id


def ensure_workspace(manifest: dict[str, Any], lab_dir: Path, *, replace: bool = False) -> Path:
    workspace = workspace_for(manifest["id"])
    if replace and workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    for mapping in manifest.get("workspace_files", []):
        source = safe_child(lab_dir, mapping["source"])
        target = workspace / safe_relative(mapping["target"])
        target.parent.mkdir(parents=True, exist_ok=True)
        if replace or not target.exists():
            shutil.copy2(source, target)
    return workspace


def docker_available() -> bool:
    return shutil.which("docker") is not None


def run_process(command: list[str], *, capture: bool = False, check: bool = False) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, cwd=ROOT, text=True, capture_output=capture, check=check)
    except FileNotFoundError as exc:
        raise LabError(f"Required command not found: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise LabError(f"Command failed ({exc.returncode}): {' '.join(command)}\n{detail}") from exc


def preflight() -> None:
    if not docker_available():
        raise LabError("Docker is not installed or is not on PATH.")
    docker = run_process(["docker", "version", "--format", "{{.Server.Version}}"], capture=True)
    if docker.returncode != 0:
        raise LabError("Docker daemon is not reachable.")
    compose = run_process(["docker", "compose", "version"], capture=True)
    if compose.returncode != 0:
        raise LabError("Docker Compose v2 is required ('docker compose').")


def compose_command(manifest: dict[str, Any], lab_dir: Path, workspace: Path) -> list[str]:
    command = ["docker", "compose", "--project-name", manifest["project_name"]]
    env_file = manifest.get("compose_env_file")
    if env_file:
        command.extend(["--env-file", str(workspace / safe_relative(env_file))])
    command.extend(["-f", str(safe_child(lab_dir, manifest["compose_file"]))])
    return command


def compose(manifest: dict[str, Any], lab_dir: Path, workspace: Path, args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return run_process(compose_command(manifest, lab_dir, workspace) + args, capture=capture)


def container_id(manifest: dict[str, Any], lab_dir: Path, workspace: Path, service: str) -> str:
    result = compose(manifest, lab_dir, workspace, ["ps", "-q", service], capture=True)
    return result.stdout.strip()


def service_running(manifest: dict[str, Any], lab_dir: Path, workspace: Path, service: str) -> tuple[bool, str]:
    cid = container_id(manifest, lab_dir, workspace, service)
    if not cid:
        return False, "container not found"
    result = run_process(["docker", "inspect", "-f", "{{.State.Running}}", cid], capture=True)
    state = result.stdout.strip()
    return state == "true", f"running={state or 'unknown'}"


def service_health(manifest: dict[str, Any], lab_dir: Path, workspace: Path, service: str) -> tuple[bool, str]:
    cid = container_id(manifest, lab_dir, workspace, service)
    if not cid:
        return False, "container not found"
    result = run_process(["docker", "inspect", "-f", "{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}", cid], capture=True)
    state = result.stdout.strip()
    return state == "healthy", f"health={state or 'unknown'}"


def wait_for_ready(manifest: dict[str, Any], lab_dir: Path, workspace: Path) -> None:
    services = manifest.get("ready_services", [])
    if not services:
        return
    timeout = int(manifest.get("ready_timeout_seconds", 45))
    deadline = time.monotonic() + timeout
    remaining = set(services)
    while remaining and time.monotonic() < deadline:
        for service in list(remaining):
            ok, _ = service_health(manifest, lab_dir, workspace, service)
            if ok:
                remaining.remove(service)
        if remaining:
            time.sleep(1)
    if remaining:
        raise LabError(f"Timed out waiting for ready service(s): {', '.join(sorted(remaining))}")


def fmt(text: str, workspace: Path) -> str:
    return text.replace("{workspace}", str(workspace.relative_to(ROOT)))


def print_tasks(manifest: dict[str, Any], workspace: Path) -> None:
    print()
    print(f"{manifest['title']} [{manifest['type']}, {manifest['difficulty']}, ~{manifest['estimated_minutes']} min]")
    print(f"Workspace: {workspace.relative_to(ROOT)}")
    print()
    for index, task in enumerate(manifest["tasks"], 1):
        print(f"Task {index}: {fmt(str(task), workspace)}")
    print()
    print(f"When ready: python kh-lab.py check {manifest['id']}")


def command_list(_: argparse.Namespace) -> int:
    if not LABS_ROOT.exists():
        print("No interactive labs found.")
        return 0
    rows: list[tuple[str, str, str, int]] = []
    for manifest_path in sorted(LABS_ROOT.glob("*/lab.json")):
        manifest, _ = load_manifest(manifest_path.parent.name)
        rows.append((manifest["id"], manifest["title"], manifest["difficulty"], manifest["estimated_minutes"]))
    if not rows:
        print("No interactive labs found.")
        return 0
    width = max(len(row[0]) for row in rows)
    for lab_id, title, difficulty, minutes in rows:
        print(f"{lab_id:<{width}}  {difficulty:<12} ~{minutes:>2} min  {title}")
    return 0


def command_validate(_: argparse.Namespace) -> int:
    count = 0
    for manifest_path in sorted(LABS_ROOT.glob("*/lab.json")):
        load_manifest(manifest_path.parent.name)
        count += 1
    print(f"Validated {count} interactive lab manifest(s).")
    return 0


def command_run(args: argparse.Namespace) -> int:
    manifest, lab_dir = load_manifest(args.lab)
    preflight()
    workspace = ensure_workspace(manifest, lab_dir)
    result = compose(manifest, lab_dir, workspace, ["up", "-d"])
    if result.returncode != 0:
        raise LabError("Docker Compose could not start the lab.")
    wait_for_ready(manifest, lab_dir, workspace)
    print(f"Lab '{manifest['id']}' started.")
    print_tasks(manifest, workspace)
    return 0


def command_status(args: argparse.Namespace) -> int:
    manifest, lab_dir = load_manifest(args.lab)
    preflight()
    workspace = ensure_workspace(manifest, lab_dir)
    result = compose(manifest, lab_dir, workspace, ["ps"])
    return result.returncode


def evaluate_check(manifest: dict[str, Any], lab_dir: Path, workspace: Path, check: dict[str, Any]) -> tuple[bool, str]:
    kind = check["type"]
    service = check.get("service", "")
    if kind == "service_running":
        return service_running(manifest, lab_dir, workspace, service)
    if kind == "service_health":
        return service_health(manifest, lab_dir, workspace, service)
    if kind == "compose_exec":
        command = check.get("command")
        if not isinstance(command, list) or not command:
            return False, "invalid compose_exec command"
        result = compose(manifest, lab_dir, workspace, ["exec", "-T", service] + [str(part) for part in command], capture=True)
        detail = (result.stdout or result.stderr or "").strip()
        expected = int(check.get("expect_exit", 0))
        ok = result.returncode == expected
        needle = check.get("stdout_contains")
        if needle is not None:
            ok = ok and str(needle) in result.stdout
        return ok, detail or f"exit={result.returncode}"
    return False, f"unsupported check type: {kind}"


def command_check(args: argparse.Namespace) -> int:
    manifest, lab_dir = load_manifest(args.lab)
    preflight()
    workspace = ensure_workspace(manifest, lab_dir)
    timeout = int(manifest.get("check_timeout_seconds", 8))
    all_ok = True
    print(f"Checking '{manifest['id']}'...")
    for check in manifest["checks"]:
        label = check.get("name") or f"{check['type']}:{check.get('service', '')}"
        deadline = time.monotonic() + timeout
        ok = False
        detail = "not evaluated"
        while True:
            ok, detail = evaluate_check(manifest, lab_dir, workspace, check)
            if ok or time.monotonic() >= deadline:
                break
            time.sleep(1)
        symbol = "PASS" if ok else "FAIL"
        print(f"[{symbol}] {label}: {detail}")
        all_ok = all_ok and ok
    if all_ok:
        print("LAB COMPLETED")
        return 0
    print("LAB NOT COMPLETE")
    print(f"Need help? python kh-lab.py hint {manifest['id']}")
    return 1


def command_hint(args: argparse.Namespace) -> int:
    manifest, _ = load_manifest(args.lab)
    hints = manifest["hints"]
    if not hints:
        print("No hints are defined for this lab.")
        return 0
    index = args.number if args.number is not None else 1
    if index < 1 or index > len(hints):
        raise LabError(f"Hint number must be between 1 and {len(hints)}.")
    print(f"Hint {index}/{len(hints)}: {hints[index - 1]}")
    if index < len(hints):
        print(f"Next hint: python kh-lab.py hint {manifest['id']} {index + 1}")
    return 0


def command_reset(args: argparse.Namespace) -> int:
    manifest, lab_dir = load_manifest(args.lab)
    workspace = ensure_workspace(manifest, lab_dir)
    if docker_available():
        compose(manifest, lab_dir, workspace, ["down", "-v", "--remove-orphans"])
    workspace = ensure_workspace(manifest, lab_dir, replace=True)
    print(f"Lab '{manifest['id']}' reset.")
    print(f"Workspace: {workspace.relative_to(ROOT)}")
    return 0


def command_stop(args: argparse.Namespace) -> int:
    manifest, lab_dir = load_manifest(args.lab)
    preflight()
    workspace = ensure_workspace(manifest, lab_dir)
    result = compose(manifest, lab_dir, workspace, ["down", "-v", "--remove-orphans"])
    if result.returncode == 0:
        print(f"Lab '{manifest['id']}' stopped and lab volumes removed.")
    return result.returncode


def command_info(args: argparse.Namespace) -> int:
    manifest, lab_dir = load_manifest(args.lab)
    workspace = ensure_workspace(manifest, lab_dir)
    print_tasks(manifest, workspace)
    return 0


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description="Knowledge Hub interactive lab runner")
    sub = cli.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List available labs").set_defaults(func=command_list)
    sub.add_parser("validate", help="Validate all lab manifests").set_defaults(func=command_validate)
    for name, func, help_text in [
        ("run", command_run, "Start or re-apply a lab"),
        ("status", command_status, "Show Docker Compose status"),
        ("check", command_check, "Validate the learner's result"),
        ("reset", command_reset, "Reset lab state to the initial scenario"),
        ("stop", command_stop, "Stop lab and remove lab volumes"),
        ("info", command_info, "Show lab tasks"),
    ]:
        item = sub.add_parser(name, help=help_text)
        item.add_argument("lab")
        item.set_defaults(func=func)
    hint = sub.add_parser("hint", help="Show a progressive hint")
    hint.add_argument("lab")
    hint.add_argument("number", type=int, nargs="?")
    hint.set_defaults(func=command_hint)
    return cli


def main() -> int:
    try:
        args = parser().parse_args()
        return int(args.func(args))
    except LabError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid lab manifest JSON: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
