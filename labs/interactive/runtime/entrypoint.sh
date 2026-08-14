#!/usr/bin/env bash
set -euo pipefail

ROOT="/opt/knowledge-hub"
LABS_ROOT="$ROOT/labs"
REGISTRY="$ROOT/runtime/labs.tsv"
DEFAULT_LAB="docker-network-debug"
DOCKERD_LOG="/tmp/knowledge-hub-dockerd.log"

if [[ "${1:-}" == "list" || "${1:-}" == "labs" ]]; then
  exec "$ROOT/runtime/list-labs"
fi
if [[ "${1:-}" == "ids" ]]; then
  exec "$ROOT/runtime/list-lab-ids"
fi

LAB_ID="${KH_LAB:-$DEFAULT_LAB}"
if [[ $# -gt 0 && -d "$LABS_ROOT/$1" ]]; then
  LAB_ID="$1"
  shift
fi

LAB_ROOT="$LABS_ROOT/$LAB_ID"
LAB_BIN="$LAB_ROOT/lab"
LAB_WORKSPACE="/workspace"
LAB_SCENARIO="$LAB_WORKSPACE/scenario.compose.yaml"
LAB_ENV_FILE="$LAB_WORKSPACE/scenario.env"

if [[ ! -d "$LAB_ROOT" || ! -x "$LAB_BIN/lab-help" ]]; then
  echo "Unknown lab: $LAB_ID" >&2
  "$ROOT/runtime/list-labs" >&2
  exit 2
fi

LAB_RUNTIME="$(awk -F $'\t' -v id="$LAB_ID" '$1 == id { print $2; exit }' "$REGISTRY")"
case "$LAB_RUNTIME" in
  shell|docker) ;;
  *)
    echo "Invalid or missing runtime mode for lab: $LAB_ID" >&2
    exit 2
    ;;
esac

export LAB_ID LAB_ROOT LAB_BIN LAB_WORKSPACE LAB_SCENARIO LAB_ENV_FILE LAB_RUNTIME
export PATH="$LAB_BIN:$ROOT/runtime:$PATH"

if [[ "${1:-}" == "help" || "${1:-}" == "task" || "${1:-}" == "lab-help" ]]; then
  shift || true
  exec lab-help "$@"
fi

mkdir -p "$LAB_WORKSPACE"
if [[ -f "$LAB_ROOT/scenario.compose.yaml" && ! -f "$LAB_SCENARIO" ]]; then
  cp "$LAB_ROOT/scenario.compose.yaml" "$LAB_SCENARIO"
fi
if [[ -f "$LAB_ROOT/scenario.env.template" && ! -f "$LAB_ENV_FILE" ]]; then
  cp "$LAB_ROOT/scenario.env.template" "$LAB_ENV_FILE"
fi
if [[ -x "$LAB_BIN/workspace-init" ]]; then
  "$LAB_BIN/workspace-init"
fi

if [[ "$LAB_RUNTIME" == "docker" ]]; then
  if [[ ! -f "$LAB_SCENARIO" ]]; then
    echo "Docker-backed lab is missing scenario.compose.yaml: $LAB_ID" >&2
    exit 2
  fi
  [[ -f "$LAB_ENV_FILE" ]] || : > "$LAB_ENV_FILE"

  rm -f /var/run/docker.pid
  printf 'Starting isolated Docker engine for %s...\n' "$LAB_ID"
  dockerd \
    --host=unix:///var/run/docker.sock \
    --storage-driver=vfs \
    >"$DOCKERD_LOG" 2>&1 &
  DOCKERD_PID=$!

  for _ in $(seq 1 90); do
    if docker info >/dev/null 2>&1; then
      break
    fi
    if ! kill -0 "$DOCKERD_PID" >/dev/null 2>&1; then
      echo "Nested Docker engine exited unexpectedly." >&2
      cat "$DOCKERD_LOG" >&2 || true
      exit 1
    fi
    sleep 1
  done

  if ! docker info >/dev/null 2>&1; then
    echo "Nested Docker engine did not become ready." >&2
    cat "$DOCKERD_LOG" >&2 || true
    exit 1
  fi

  printf 'Preparing lab scenario...\n'
  docker compose -f "$LAB_SCENARIO" --env-file "$LAB_ENV_FILE" up -d >/dev/null
else
  printf 'Preparing shell-only lab %s (nested Docker not required)...\n' "$LAB_ID"
fi

if [[ -x "$LAB_BIN/wait-ready" ]]; then
  "$LAB_BIN/wait-ready"
fi

if [[ $# -gt 0 ]]; then
  exec "$@"
fi

lab-help
exec bash --noprofile --rcfile "$ROOT/runtime/bashrc" -i
