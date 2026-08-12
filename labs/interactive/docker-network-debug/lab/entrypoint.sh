#!/usr/bin/env bash
set -euo pipefail

ROOT="/opt/knowledge-hub"
WORKSPACE="${LAB_WORKSPACE:-/workspace}"
SCENARIO="$ROOT/scenario.compose.yaml"
ENV_FILE="$WORKSPACE/scenario.env"

mkdir -p "$WORKSPACE"

printf 'Preparing isolated Docker lab...\n'
for _ in $(seq 1 60); do
  if docker info >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! docker info >/dev/null 2>&1; then
  echo "Nested Docker engine did not become ready." >&2
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  cp "$ROOT/scenario.env.template" "$ENV_FILE"
fi

docker compose -f "$SCENARIO" --env-file "$ENV_FILE" up -d >/dev/null

if [[ "$#" -gt 0 ]]; then
  exec "$@"
fi

cat <<'EOF'

Knowledge Hub Interactive Lab
────────────────────────────────────────────────────
Docker: Service Discovery Troubleshooting

Scenario
  An application container cannot connect to PostgreSQL.
  Diagnose the failure and restore connectivity.

Host requirement
  Docker + Docker Compose only.
  Everything you use now runs inside this disposable lab.

Start here
  status
  docker ps
  docker logs kh-lab-app
  docker inspect kh-lab-app

Workspace
  /workspace/scenario.env

Lab commands
  status   show the scenario containers
  check    validate your current solution
  hint     reveal the next progressive hint
  apply    re-apply scenario.env after you edit it
  reset    restore the intentionally broken scenario

Editor
  nano scenario.env

Exit the shell with: exit
From the host, remove the whole sandbox with:
  docker compose down -v

EOF

export PS1='lab@knowledgehub:\w$ '
exec bash --noprofile --norc
