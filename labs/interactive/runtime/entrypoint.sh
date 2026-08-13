#!/usr/bin/env bash
set -euo pipefail

ROOT="/opt/knowledge-hub"
LABS_ROOT="$ROOT/labs"
DEFAULT_LAB="docker-network-debug"
DOCKERD_LOG="/tmp/knowledge-hub-dockerd.log"

if [[ "${1:-}" == "list" || "${1:-}" == "labs" ]]; then
  exec "$ROOT/runtime/list-labs"
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

export LAB_ID LAB_ROOT LAB_BIN LAB_WORKSPACE LAB_SCENARIO LAB_ENV_FILE
export PATH="$LAB_BIN:$ROOT/runtime:$PATH"

mkdir -p "$LAB_WORKSPACE"
[[ -f "$LAB_SCENARIO" ]] || cp "$LAB_ROOT/scenario.compose.yaml" "$LAB_SCENARIO"
[[ -f "$LAB_ENV_FILE" ]] || cp "$LAB_ROOT/scenario.env.template" "$LAB_ENV_FILE"

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

if [[ -x "$LAB_BIN/wait-ready" ]]; then
  "$LAB_BIN/wait-ready"
fi

if [[ $# -gt 0 ]]; then
  if [[ "$1" == "help" || "$1" == "task" ]]; then
    shift
    exec lab-help "$@"
  fi
  exec "$@"
fi

lab-help
exec bash --noprofile --rcfile "$ROOT/runtime/bashrc" -i
