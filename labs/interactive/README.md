# Knowledge Hub Interactive Labs

Interactive Labs are disposable hands-on environments distributed through one public GHCR runtime image. The learner needs only Docker on the host. Lab-specific CLIs, services, editors, hints, reset logic and validators run inside the container.

## List labs

```bash
docker run --pull=always --rm ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest list
```

## Run a lab

For most labs:

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest <lab-id>
```

The Kubernetes lab additionally needs access to the Docker host cgroup-v2 hierarchy used by the disposable nested K3s node:

```bash
docker run --pull=always --rm -it --privileged --cgroupns=host -v /sys/fs/cgroup:/sys/fs/cgroup:rw ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest kubernetes-configmap-rollout
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
| `redis-cache-ttl` | challenge | Repair stale Redis data and enforce an explicit bounded TTL. |
| `tls-certificate-hostname` | challenge | Repair a certificate SAN and restore hostname-verified HTTPS. |
| `terraform-state-drift` | challenge | Detect out-of-band Terraform drift and reconcile the managed resource. |
| `kubernetes-configmap-rollout` | challenge | Repair a ConfigMap and roll a Deployment so the running Pod consumes the corrected value. |
| `s3-versioning-minio` | challenge | Use AWS CLI S3 API commands against MinIO, enable versioning and create a second object version. |
| `rabbitmq-routing-key` | challenge | Repair a direct-exchange binding so a published event reaches the correct RabbitMQ queue. |

If no lab ID is supplied, `docker-network-debug` remains the default for backward compatibility.

A lab assignment can be shown without starting Docker-in-Docker:

```bash
docker run --rm ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest <lab-id> help
```

Inside a lab, type `help` at any time. The common commands are `status`, `check`, `hint`, `reset`, and `apply` where the scenario has editable runtime configuration. `labs` lists the bundled labs. Lab-specific tools such as `kubectl`, `aws`, Terraform and Docker CLI live inside the image, so corresponding host tools are not required.

The runtime starts a private Docker-in-Docker daemon. Scenario containers never use the host Docker socket. Most executable labs need only `--privileged`; the nested K3s lab also needs the host cgroup namespace and writable cgroup-v2 mount shown above.

## Runtime contract

A lab is accepted only when its built-in `self-test` proves the intended lifecycle. Challenge labs must fail in their initial state, pass after the intended repair, and fail again after `reset`. Guided labs must prove the real external component and validation path they teach, then return to incomplete learner state after reset.

The lab registry is stored in `runtime/labs.tsv`. CI derives the lab IDs from that registry. Kubernetes, MinIO S3 and RabbitMQ are preflighted separately because they exercise distinct platform runtimes; the remaining lab IDs are then executed automatically. The publish workflow builds the same multi-lab image, publishes `latest` plus an immutable SHA tag to GHCR, logs out, removes local tags, anonymously pulls `latest` again and smoke-tests the registry copy.

The MinIO lab is an S3-compatible local training environment and is not evidence of behavior in a real AWS account. The Kubernetes lab runs a disposable K3s server inside the isolated nested Docker engine. The current GHCR repository name is retained from the first pilot package so its public visibility can be reused for all subsequent labs.
