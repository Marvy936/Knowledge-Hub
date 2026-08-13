# Docker service discovery troubleshooting

A one-command challenge about Docker Compose DNS/service discovery.

## Run

Only Docker is required on the host:

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest docker-network-debug
```

Inside the lab, type `help` at any time to show the assignment again. The useful commands are `status`, `check`, `hint`, `apply`, `reset` and normal Docker commands such as `docker ps`, `docker logs` and `docker inspect`.

The scenario is intentionally broken. The application uses an invalid PostgreSQL hostname; the learner diagnoses Docker service discovery and repairs `/workspace/scenario.env`.
