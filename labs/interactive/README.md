# Knowledge Hub Interactive Labs

Interactive Labs are disposable hands-on environments distributed through one public GHCR runtime image. The learner needs only Docker on the host. Lab-specific CLIs, services, editors, hints, reset logic and validators run inside the container.

## List labs

```bash
docker run --pull=always --rm ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest list
```

The list shows each lab's runtime profile:

- `shell` runs entirely inside the outer image and does not start nested Docker;
- `docker` starts an isolated Docker-in-Docker daemon and requires `--privileged`;
- `k3s` starts the same isolated nested Docker runtime plus a disposable K3s node and additionally needs the host cgroup namespace and writable cgroup-v2 mount.

## Run a lab

Shell-only lab:

```bash
docker run --pull=always --rm -it ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest <shell-lab-id>
```

Docker-backed lab:

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest <docker-lab-id>
```

K3s-backed lab:

```bash
docker run --pull=always --rm -it --privileged --cgroupns=host -v /sys/fs/cgroup:/sys/fs/cgroup:rw ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest <k3s-lab-id>
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
| `kubernetes-service-selector` | challenge | Repair a Service selector so healthy Pods become endpoints and receive real Service traffic. |
| `s3-versioning-minio` | challenge | Use AWS CLI S3 API commands against MinIO, enable versioning and create a second object version. |
| `rabbitmq-routing-key` | challenge | Repair a direct-exchange binding so a published event reaches the correct RabbitMQ queue. |
| `postgres-backup-restore` | challenge | Inspect a real data-only `pg_dump` and recover a missing PostgreSQL row without duplicating intact data. |
| `localstack-s3-versioning` | challenge | Use the bundled AWS CLI against LocalStack, enable S3 bucket versioning and create a second object version. |
| `ansible-idempotency` | challenge | Repair a playbook so desired file content converges and an identical second run reports `changed=0`. |
| `git-three-way-merge` | challenge | Resolve a real Git three-way merge while preserving the required integrated configuration. |
| `bash-pipeline-failure` | challenge | Repair pipeline failure propagation so a failed build cannot be reported as a successful release. |
| `linux-service-permissions` | challenge | Repair Linux owner, group and mode bits so a service gets read-only least-privilege access. |

The authoritative runtime profile for every lab is stored in `runtime/labs.tsv` and surfaced by the `list` command.

If no lab ID is supplied, `docker-network-debug` remains the default for backward compatibility.

A lab assignment can be shown without starting any runtime profile:

```bash
docker run --rm ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest <lab-id> help
```

Inside a lab, type `help` at any time. The common commands are `status`, `check`, `hint`, `reset`, and `apply` where the scenario has editable runtime configuration. `labs` lists the bundled labs. Lab-specific tools such as `kubectl`, `aws`, `ansible-playbook`, `git`, Terraform and Docker CLI live inside the image, so corresponding host tools are not required.

Container-backed profiles start a private Docker-in-Docker daemon and scenario containers never use the host Docker socket. `shell` deliberately skips `dockerd`, removing the need for the expanded privileges associated with `--privileged`.

## Runtime contract

A lab is accepted only when its built-in `self-test` proves the intended lifecycle. Challenge labs must fail in their initial state, pass after the intended repair, and fail again after `reset`. Guided labs must prove the real external component and validation path they teach, then return to incomplete learner state after reset.

The lab registry is stored in `runtime/labs.tsv` as `lab-id`, `runtime-profile`, and description. CI derives the lab sets and host requirements from that contract: `shell` is self-tested unprivileged, `k3s` receives the cgroup flags, and ordinary `docker` labs use the isolated nested daemon. MinIO S3 and RabbitMQ retain explicit preflight steps because of their service-specific startup/timeout characteristics. Image build validates the registry structure before runtime testing. The publish workflow builds the same multi-lab image, publishes `latest` plus an immutable SHA tag to GHCR, logs out, removes local tags, anonymously pulls `latest` again and proves an unprivileged shell lab from the registry copy.

The MinIO and LocalStack labs are S3-compatible local training environments and are not evidence of behavior in a real AWS account. The Kubernetes labs run disposable K3s servers inside the isolated nested Docker engine. The current GHCR repository name is retained from the first pilot package so its public visibility can be reused for all subsequent labs.
