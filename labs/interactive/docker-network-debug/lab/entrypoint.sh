#!/usr/bin/env bash
set -euo pipefail

ROOT="/opt/knowledge-hub"
WORKSPACE="${LAB_WORKSPACE:-/workspace}"
SCENARIO="$ROOT/scenario.compose.yaml"
ENV_FILE="$WORKSPACE/scenario.env"
DOCKERD_LOG="/tmp/knowledge-hub-dockerd.log"

mkdir -p "$WORKSPACE"
rm -f /var/run/docker.pid

printf 'Starting isolated Docker engine...\n'
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

if [[ ! -f "$ENV_FILE" ]]; then
  cp "$ROOT/scenario.env.template" "$ENV_FILE"
fi

printf 'Preparing lab scenario...\n'
docker compose -f "$SCENARIO" --env-file "$ENV_FILE" up -d >/dev/null

if [[ "$#" -gt 0 ]]; then
  exec "$@"
fi

lab-help
exec bash --noprofile --rcfile "$ROOT/bashrc" -i
