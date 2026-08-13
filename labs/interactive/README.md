# Knowledge Hub Interactive Labs

Interactive Labs are disposable hands-on environments distributed through one public GHCR runtime image. The learner needs only Docker on the host. Lab-specific CLIs, services, editors, hints, reset logic and validators run inside the container.

## List labs

```bash
docker run --pull=always --rm ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest list
```

## Run a lab

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest <lab-id>
```

Current labs:

| Lab | Type | Goal |
|---|---|---|
| `docker-network-debug` | challenge | Diagnose Docker service discovery and fix an invalid database hostname. |
| `docker-volume-persistence` | challenge | Repair a named-volume mount and prove data survives recreation. |
| `keycloak-service-account` | guided | Obtain, inspect and validate a real Keycloak client-credentials token. |
| `postgres-index-performance` | challenge | Diagnose a sequential scan and add a useful composite PostgreSQL index. |
| `prometheus-target-alert` | challenge | Repair a broken Prometheus scrape target and resolve the resulting alert. |
| `nginx-reverse-proxy` | challenge | Repair an invalid Nginx upstream and restore proxy traffic. |

If no lab ID is supplied, `docker-network-debug` remains the default for backward compatibility.

A lab assignment can be shown without starting Docker-in-Docker:

```bash
docker run --rm ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest <lab-id> help
```

Inside a lab, type `help` at any time. The common commands are `status`, `check`, `hint`, `reset`, and `apply` where the scenario has editable runtime configuration. `labs` lists the bundled labs.

The runtime starts a private Docker-in-Docker daemon, so executable labs currently require `--privileged`. Scenario containers never use the host Docker socket.

## Runtime contract

A lab is accepted only when its built-in `self-test` proves the intended lifecycle. Challenge labs must fail in their initial state, pass after the intended repair, and fail again after `reset`. Guided labs must prove the real external component and validation path they teach, then return to incomplete learner state after reset.

The lab registry is stored in `runtime/labs.tsv`. CI derives the lab IDs from that registry and executes every bundled `self-test`, so adding a lab does not require a separate workflow job. The publish workflow builds the same multi-lab image, publishes `latest` plus an immutable SHA tag to GHCR, logs out, removes local tags, anonymously pulls `latest` again and smoke-tests the registry copy.

The current GHCR repository name is retained from the first pilot package so its public visibility can be reused for all subsequent labs.
