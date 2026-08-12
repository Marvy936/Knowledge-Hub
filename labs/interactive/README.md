# Knowledge Hub Interactive Labs

Interactive Labs are disposable hands-on environments where the learner runs real commands, changes a scenario, and validates the result.

## Docker-only host contract

The host requirement is intentionally small:

- Docker Engine or Docker Desktop,
- Docker Compose v2 (`docker compose`).

Lab-specific tools belong inside containers. A lab may contain Docker CLI, `curl`, `jq`, editors, `kubectl`, Helm, Terraform, Ansible, AWS CLI, or other tooling without requiring those programs on the learner's host.

The standard entry point for a lab is:

```bash
docker compose run --build --rm lab
```

After that command the learner works inside the prepared lab terminal.

## Framework direction

Each interactive lab owns its Compose environment and a `lab` image that provides:

- the interactive shell,
- tools required by the exercise,
- learner workspace,
- progressive hints,
- automated validation,
- reset/recovery commands.

The host is only responsible for running Docker.

For labs that teach Docker itself, the preferred isolation model is Docker-in-Docker rather than exposing `/var/run/docker.sock`. This keeps the exercise daemon and its scenario containers inside the lab project.

## Reference lab

[`docker-network-debug`](docker-network-debug/README.md) is the first reference implementation. It provides a deliberately broken PostgreSQL connectivity scenario and supports the lifecycle:

```text
run -> inspect -> edit -> apply -> check -> reset
```

CI proves both sides of the teaching contract: the initial state must fail validation, and the intended learner repair must pass.
