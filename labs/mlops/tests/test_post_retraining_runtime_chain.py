from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_post_retraining_runtime_chain.py"
SPEC = importlib.util.spec_from_file_location("run_post_retraining_runtime_chain", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


def _subjects() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    retraining = {
        "retraining": {
            "candidate_id": "a" * 64,
            "release_id": "b" * 64,
            "registry_evidence_id": "c" * 64,
            "registry_version": "2",
            "model_sha256": "d" * 64,
        }
    }
    container = {
        "input_mode": "explicit-subjects",
        "release_source": "provided-release",
        "candidate_id": "a" * 64,
        "release_id": "b" * 64,
        "registry_evidence_id": "c" * 64,
        "registry_version": "2",
        "model_sha256": "d" * 64,
        "docker_image_id": "sha256:" + "e" * 64,
        "image_reference": "knowledge-hub-mlops-runtime:test",
        "deployment_id": "f" * 64,
    }
    deployment = {
        "deployment_id": "f" * 64,
        "candidate_id": "a" * 64,
        "release_id": "b" * 64,
        "model": {
            "registry_evidence_id": "c" * 64,
            "registry_version": "2",
            "sha256": "d" * 64,
        },
        "image": {
            "digest": "sha256:" + "e" * 64,
            "reference": "knowledge-hub-mlops-runtime:test",
        },
    }
    return retraining, container, deployment


def test_subject_sha_requires_exact_lowercase_git_sha1() -> None:
    assert runtime._require_subject_sha("a" * 40) == "a" * 40
    with pytest.raises(runtime.PostRetrainingChainError, match="40-character"):
        runtime._require_subject_sha("a" * 39)
    with pytest.raises(runtime.PostRetrainingChainError, match="40-character"):
        runtime._require_subject_sha("A" * 40)


def test_component_lineage_requires_exact_retraining_container_deployment_binding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    retraining, container, deployment = _subjects()
    monkeypatch.setattr(runtime, "validate_deployment_manifest", lambda value: None)

    runtime._validate_component_lineage(
        retraining=retraining,
        container=container,
        deployment=deployment,
    )

    detached = dict(container)
    detached["registry_version"] = "3"
    with pytest.raises(runtime.PostRetrainingChainError, match="registry_version"):
        runtime._validate_component_lineage(
            retraining=retraining,
            container=detached,
            deployment=deployment,
        )

    wrong_release = dict(container)
    wrong_release["release_source"] = "generated-baseline-release"
    with pytest.raises(runtime.PostRetrainingChainError, match="regenerated release"):
        runtime._validate_component_lineage(
            retraining=retraining,
            container=wrong_release,
            deployment=deployment,
        )

    wrong_image = dict(deployment)
    wrong_image["image"] = {
        "digest": "sha256:" + "0" * 64,
        "reference": deployment["image"]["reference"],
    }
    with pytest.raises(runtime.PostRetrainingChainError, match="image digest"):
        runtime._validate_component_lineage(
            retraining=retraining,
            container=container,
            deployment=wrong_image,
        )


def test_route_probe_search_is_bounded_and_requires_requested_role(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_route_request(*, routing_state, deployments, routing_key):
        index = int(routing_key.rsplit("-", 1)[1])
        role = "canary" if index == 3 else "stable"
        return {
            "selected_role": role,
            "deployment_id": "canary" if role == "canary" else "stable",
            "routing_key": routing_key,
        }

    monkeypatch.setattr(runtime, "route_request", fake_route_request)
    probe = runtime._find_route_probe(
        routing_state={},
        deployments={},
        selected_role="canary",
    )
    assert probe["selected_role"] == "canary"
    assert probe["routing_key"] == "post-retraining-probe-3"
