# Knowledge Hub Interactive Labs

Interactive Labs are disposable, task-oriented environments layered on top of the existing Knowledge Hub practical material. The goal is not merely to start services. A learner starts a scenario, changes the environment, and proves the result with an automated checker.

## Requirements

- Docker Engine or Docker Desktop
- Docker Compose v2 (`docker compose`)
- Python 3.9+

No Python packages are required; the runner uses only the standard library.

## Runner

From the repository root:

```powershell
.\kh-lab.ps1 list
.\kh-lab.ps1 run docker-network-debug
.\kh-lab.ps1 status docker-network-debug
.\kh-lab.ps1 check docker-network-debug
.\kh-lab.ps1 hint docker-network-debug
.\kh-lab.ps1 reset docker-network-debug
.\kh-lab.ps1 stop docker-network-debug
```

Linux/macOS users can use `./kh-lab.sh ...`, and all platforms can call `python kh-lab.py ...` directly.

`run` creates a disposable learner workspace under `.kh-labs/<lab-id>/`. Source files under `labs/interactive/` remain immutable during the exercise. `reset` tears down the Compose project, removes its volumes, and reconstructs the initial workspace.

## Framework contract

Every lab is a directory under `labs/interactive/<lab-id>/` with a `lab.json` manifest and a Compose file. The v0.1 manifest defines:

- identity and learner-facing metadata,
- Compose project/file configuration,
- workspace templates,
- ordered tasks and progressive hints,
- services that must become ready before the exercise begins,
- automated checks.

The runner currently supports these check types:

- `service_running`
- `service_health`
- `compose_exec`

This deliberately small contract is enough for the first Docker challenge while keeping future Keycloak, RAG, MLOps and Kubernetes adapters possible without baking one lab's assumptions into the runner.

## Authoring rule

A challenge is valid only when its initial state fails at least one meaningful checker and the intended learner repair makes every checker pass. CI enforces that property for the reference lab.

## Reference lab

[`docker-network-debug`](docker-network-debug/README.md) is the first reference implementation. It teaches Docker Compose service discovery by starting with an intentionally invalid database hostname.
