#!/usr/bin/env bash
set -euo pipefail

: "${VENV_DIR:?VENV_DIR is required}"
: "${RUNTIME_DIR:?RUNTIME_DIR is required}"
: "${SUBJECT_SHA:?SUBJECT_SHA is required}"
: "${TRACKING_URI:=http://127.0.0.1:5057}"

ML_RUNTIME="$RUNTIME_DIR/ml"
BACKEND_DB="$RUNTIME_DIR/mlflow.db"
ARTIFACT_ROOT="$RUNTIME_DIR/mlartifacts"
DOWNLOAD_DIR="$RUNTIME_DIR/downloaded"
SERVER_LOG="$RUNTIME_DIR/mlflow-server.log"
SERVER_PID=""

stop_server() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID"
    wait "$SERVER_PID" || true
  fi
  SERVER_PID=""
}

start_server() {
  "$VENV_DIR/bin/mlflow" server \
    --host 127.0.0.1 \
    --port 5057 \
    --backend-store-uri "sqlite:///$BACKEND_DB" \
    --artifacts-destination "file://$ARTIFACT_ROOT" \
    --allowed-hosts "127.0.0.1:*,localhost:*" \
    >"$SERVER_LOG" 2>&1 &
  SERVER_PID=$!

  for attempt in $(seq 1 60); do
    if "$VENV_DIR/bin/python" - <<'PY'
import os
import urllib.request

try:
    with urllib.request.urlopen(os.environ["TRACKING_URI"] + "/health", timeout=1) as response:
        raise SystemExit(0 if response.status == 200 else 1)
except Exception:
    raise SystemExit(1)
PY
    then
      return 0
    fi
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
      cat "$SERVER_LOG"
      return 1
    fi
    sleep 1
  done

  cat "$SERVER_LOG"
  return 1
}

trap stop_server EXIT
rm -rf "$RUNTIME_DIR"
mkdir -p "$ML_RUNTIME" "$ARTIFACT_ROOT" "$DOWNLOAD_DIR"

"$VENV_DIR/bin/python" -m ml_lab generate-data \
  --output "$ML_RUNTIME/customers.csv" \
  --rows 1200 \
  --seed 20260805

GITHUB_SHA="$SUBJECT_SHA" "$VENV_DIR/bin/python" -m ml_lab train \
  --input "$ML_RUNTIME/customers.csv" \
  --output-dir "$ML_RUNTIME/artifact" \
  --seed 20260805

"$VENV_DIR/bin/python" -m mlops_lab snapshot \
  --dataset "$ML_RUNTIME/customers.csv" \
  --output "$ML_RUNTIME/dataset-manifest.json" \
  --dataset-name churn-training \
  --generation hosted-registry-v1

"$VENV_DIR/bin/python" -m mlops_lab evaluation-from-training \
  --training-manifest "$ML_RUNTIME/artifact/manifest.json" \
  --dataset "$ML_RUNTIME/customers.csv" \
  --model "$ML_RUNTIME/artifact/model.joblib" \
  --source-revision "$SUBJECT_SHA" \
  --policy-generation ml-training-manifest-v1 \
  --output "$ML_RUNTIME/evaluation.json"

"$VENV_DIR/bin/python" -m mlops_lab candidate \
  --dataset-manifest "$ML_RUNTIME/dataset-manifest.json" \
  --model "$ML_RUNTIME/artifact/model.joblib" \
  --evaluation "$ML_RUNTIME/evaluation.json" \
  --source-revision "$SUBJECT_SHA" \
  --output "$ML_RUNTIME/candidate.json"

start_server

"$VENV_DIR/bin/python" -m mlops_lab registry-roundtrip \
  --candidate "$ML_RUNTIME/candidate.json" \
  --model "$ML_RUNTIME/artifact/model.joblib" \
  --sample-request labs/machine-learning/data/sample-request.json \
  --tracking-uri "$TRACKING_URI" \
  --experiment-name knowledge-hub-mlops-hosted \
  --model-name KnowledgeHubChurn \
  --alias champion \
  --download-dir "$DOWNLOAD_DIR" \
  --output "$RUNTIME_DIR/registry-evidence.json"

"$VENV_DIR/bin/python" -m mlops_lab registry-verify \
  --evidence "$RUNTIME_DIR/registry-evidence.json" \
  --sample-request labs/machine-learning/data/sample-request.json \
  --tracking-uri "$TRACKING_URI"

stop_server
start_server

"$VENV_DIR/bin/python" -m mlops_lab registry-verify \
  --evidence "$RUNTIME_DIR/registry-evidence.json" \
  --sample-request labs/machine-learning/data/sample-request.json \
  --tracking-uri "$TRACKING_URI"

stop_server

test -s "$BACKEND_DB"
test -d "$ARTIFACT_ROOT"
test -n "$(find "$ARTIFACT_ROOT" -type f -print -quit)"
test -s "$RUNTIME_DIR/registry-evidence.json"
test -s "$ML_RUNTIME/artifact/manifest.json"
test -s "$ML_RUNTIME/evaluation.json"

"$VENV_DIR/bin/python" - <<'PY'
import json
import os
from pathlib import Path

runtime = Path(os.environ["RUNTIME_DIR"])
manifest = json.loads((runtime / "ml" / "artifact" / "manifest.json").read_text(encoding="utf-8"))
evaluation = json.loads((runtime / "ml" / "evaluation.json").read_text(encoding="utf-8"))
candidate = json.loads((runtime / "ml" / "candidate.json").read_text(encoding="utf-8"))
evidence = json.loads((runtime / "registry-evidence.json").read_text(encoding="utf-8"))

assert manifest["source_revision"] == os.environ["SUBJECT_SHA"]
assert manifest["dataset_sha256"] == candidate["dataset"]["sha256"]
assert manifest["model_sha256"] == candidate["model"]["sha256"]
assert evaluation["accepted"] is True
assert evaluation["policy_generation"] == "ml-training-manifest-v1"
assert evaluation["metrics"]["f1"] == manifest["test_metrics"]["f1"]
assert evaluation["metrics"]["recall"] == manifest["test_metrics"]["recall"]
assert evaluation["metrics"]["decision_threshold"] == manifest["decision_threshold"]
assert evidence["source_revision"] == os.environ["SUBJECT_SHA"]
assert evidence["candidate_id"] == candidate["candidate_id"]
assert evidence["artifact_readback"]["downloaded_sha256"] == manifest["model_sha256"]
assert evidence["artifact_readback"]["passed"] is True
assert evidence["parity"]["passed"] is True
assert evidence["registry"]["alias_resolved_version"] == evidence["registry"]["version"]
assert "@" not in evidence["registry"]["exact_uri"]
PY
