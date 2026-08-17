# Knowledge Hub Interactive Labs

Interactive Labs are disposable hands-on environments distributed through one public GHCR runtime image. The learner needs only Docker on the host. Lab-specific CLIs, services, editors, hints, reset logic and validators run inside the container.

## List labs

```bash
docker run --pull=always --rm ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest list
```

The list shows every lab's runtime profile:

- `shell` runs entirely inside the disposable outer image and does not start nested Docker;
- `docker` starts an isolated Docker-in-Docker daemon and requires `--privileged`;
- `k3s` starts the isolated nested Docker runtime plus a disposable K3s node and additionally needs the host cgroup namespace and writable cgroup-v2 mount.

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

| Lab | Type | Profile | Goal |
|---|---|---|---|
| `docker-network-debug` | challenge | `docker` | Diagnose Docker service discovery and fix an invalid database hostname. |
| `docker-volume-persistence` | challenge | `docker` | Repair a named-volume mount and prove data survives recreation. |
| `keycloak-service-account` | guided | `docker` | Obtain, inspect and validate a real Keycloak client-credentials token. |
| `postgres-index-performance` | challenge | `docker` | Diagnose a sequential scan and add a useful composite PostgreSQL index. |
| `prometheus-target-alert` | challenge | `docker` | Repair a broken Prometheus scrape target and resolve the resulting alert. |
| `nginx-reverse-proxy` | challenge | `docker` | Repair an invalid Nginx upstream and restore proxy traffic. |
| `redis-cache-ttl` | challenge | `docker` | Repair stale Redis data and enforce an explicit bounded TTL. |
| `tls-certificate-hostname` | challenge | `docker` | Repair a certificate SAN and restore hostname-verified HTTPS. |
| `terraform-state-drift` | challenge | `shell` | Detect out-of-band Terraform drift and reconcile the managed resource. |
| `kubernetes-configmap-rollout` | challenge | `k3s` | Repair a ConfigMap and roll a Deployment so the running Pod consumes the corrected value. |
| `s3-versioning-minio` | challenge | `docker` | Use AWS CLI S3 API commands against MinIO, enable versioning and create a second object version. |
| `rabbitmq-routing-key` | challenge | `docker` | Repair a direct-exchange binding so a published event reaches the correct RabbitMQ queue. |
| `postgres-backup-restore` | challenge | `docker` | Inspect a real data-only `pg_dump` and recover a missing PostgreSQL row without duplicating intact data. |
| `localstack-s3-versioning` | challenge | `docker` | Use the bundled AWS CLI against LocalStack, enable S3 bucket versioning and create a second object version. |
| `ansible-idempotency` | challenge | `shell` | Repair a non-idempotent Ansible file task so an identical second run converges with `changed=0`. |
| `git-three-way-merge` | challenge | `shell` | Resolve a real Git three-way merge while preserving the required integrated configuration. |
| `bash-pipeline-failure` | challenge | `shell` | Repair pipeline failure propagation so a failed build cannot be reported as a successful release. |
| `linux-file-permissions` | challenge | `shell` | Repair Unix owner/group/other access so deploy can write, the app can only read, and an unrelated account has no access. |
| `nginx-rate-limiting` | challenge | `docker` | Enforce per-client request throttling with burst handling and HTTP 429 responses. |
| `linux-process-signals` | challenge | `shell` | Repair child exit propagation, graceful signal forwarding and process reaping. |
| `rag-indirect-prompt-injection` | challenge | `shell` | Keep retrieved content as evidence while binding tool execution to explicit trusted intent. |
| `mlops-model-promotion` | challenge | `shell` | Reconcile exact model, evaluation, dataset, schema and segment evidence before promotion. |
| `mlops-feature-parity` | challenge | `shell` | Repair training-serving skew by binding serving to the exact feature contract and reproducing offline vectors. |
| `mlops-drift-monitoring` | challenge | `shell` | Repair biased drift population/window semantics and separate drift evidence from retraining authority. |
| `mlops-canary-rollback` | challenge | `shell` | Repair canary rollout authority using actual stable-unit exposure, candidate-only guardrails and exact rollback state. |
| `mlops-ab-experiment-integrity` | challenge | `shell` | Repair A/B experiment causal integrity across stable assignment, SRM, shared-resource interference and mature fixed-horizon analysis. |
| `mlops-retraining-trigger` | challenge | `shell` | Repair Continuous Training authority across persistent degradation, mature data readiness, semantic deduplication and explicit separation from promotion. |
| `mlops-training-run-lineage` | challenge | `shell` | Bind the approved retraining subject to the exact loaded dataset, code, trainer image, config and resulting artifact bytes before candidate registration. |
| `mlops-offline-evaluation-integrity` | challenge | `shell` | Bind a lineage-verified candidate to an immutable independent holdout, reject leakage or immature evidence, and recompute offline metrics before promotion review. |
| `mlops-release-delivery-integrity` | challenge | `shell` | Verify an immutable promoted release across exact deployment rendering, controller reconciliation and complete fleet fingerprints without granting rollout authority. |

The authoritative runtime profile for every lab is stored in `runtime/labs.tsv` and surfaced by the `list` command. If no lab ID is supplied, `docker-network-debug` remains the default for backward compatibility.

A lab assignment can be shown without starting any runtime profile:

```bash
docker run --rm ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest <lab-id> help
```

Inside a lab, type `help` at any time. The common commands are `status`, `check`, `hint`, `reset`, and `apply` where the scenario has editable runtime configuration. `labs` lists the bundled labs. Lab-specific tools such as `kubectl`, `aws`, `ansible-playbook`, `git`, Terraform and Docker CLI live inside the image, so corresponding host tools are not required.

Container-backed profiles start a private Docker-in-Docker daemon. Scenario containers never use the host Docker socket. The `shell` profile deliberately skips `dockerd`, so shell-only labs do not need the expanded privileges associated with `--privileged`.

## Runtime contract

A lab is accepted only when its built-in `self-test` proves the intended lifecycle. Challenge labs must fail in their initial state, pass after the intended repair, and fail again after `reset`. Guided labs must prove the real external component and validation path they teach, then return to incomplete learner state after reset.

The lab registry is stored in `runtime/labs.tsv` as `lab-id`, `runtime-profile`, and description. The image build validates that registry against the bundled lab directories and runtime entrypoints. CI derives the lab sets and host requirements from the same contract: `shell` is self-tested unprivileged, `k3s` receives the cgroup flags, and ordinary `docker` labs use the isolated nested daemon. MinIO S3 and RabbitMQ retain explicit preflight steps because of their service-specific startup and timeout characteristics.

`Interactive Labs` is the pull-request/manual validation workflow. On `main`, `Publish Interactive Lab Image` is the authoritative full-suite gate: it validates every profile, publishes `latest` plus an immutable SHA tag to GHCR, logs out, removes local tags, anonymously pulls `latest` again, and proves both a shell-only runtime without privileged mode and a Docker-backed runtime from the public registry copy.

The MinIO and LocalStack labs are S3-compatible local training environments and are not evidence of behavior in a real AWS account. K3s labs run disposable K3s servers inside the isolated nested Docker engine. The current GHCR repository name is retained from the first pilot package so its public visibility can be reused for all subsequent labs.