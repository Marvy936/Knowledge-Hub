# Docker service discovery troubleshooting

A small application container cannot reach PostgreSQL. The lab starts successfully, but the application health check remains unhealthy. Diagnose the problem and repair only the learner workspace.

## Start

From the repository root on Windows:

```powershell
.\kh-lab.ps1 run docker-network-debug
```

Linux/macOS:

```bash
./kh-lab.sh run docker-network-debug
```

The runner prints the task list and creates:

```text
.kh-labs/docker-network-debug/scenario.env
```

Do not edit `compose.yaml`. Treat it as the known-good platform definition; the fault belongs to the scenario configuration.

## Useful commands

```powershell
.\kh-lab.ps1 status docker-network-debug
docker compose --project-name kh-docker-network-debug --env-file .kh-labs/docker-network-debug/scenario.env -f labs/interactive/docker-network-debug/compose.yaml logs app
.\kh-lab.ps1 hint docker-network-debug
.\kh-lab.ps1 check docker-network-debug
```

After changing the scenario, re-apply it:

```powershell
.\kh-lab.ps1 run docker-network-debug
.\kh-lab.ps1 check docker-network-debug
```

A successful solution ends with `LAB COMPLETED`.

## Reset

```powershell
.\kh-lab.ps1 reset docker-network-debug
```

This removes the Compose project volumes and restores the intentionally broken scenario.

## Learning objective

The important behavior is Docker Compose DNS/service discovery: containers on the same Compose network resolve other services by their service name. The checker validates both the application health state and a real PostgreSQL readiness probe from inside the application container.
