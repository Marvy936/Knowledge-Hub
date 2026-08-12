# Docker service discovery troubleshooting

This is the first Docker-only Knowledge Hub interactive lab.

## Host requirement

Only Docker with Docker Compose v2 is required. You do not need Python, Git, `curl`, `jq`, PostgreSQL tools, or any other lab dependency installed on the host.

Open this directory and run:

```bash
docker compose run --build --rm lab
```

The command builds the lab image, starts an isolated Docker-in-Docker sandbox, creates the intentionally broken PostgreSQL scenario, and drops you into the lab terminal.

## Inside the lab

You will see a prompt similar to:

```text
lab@knowledgehub:/workspace$
```

Start with normal Docker troubleshooting commands:

```bash
status
docker ps
docker logs kh-lab-app
docker inspect kh-lab-app
```

The learner-editable configuration is:

```text
/workspace/scenario.env
```

Edit it with:

```bash
nano scenario.env
```

Then re-apply the configuration and validate the result:

```bash
apply
check
```

Progressive help is available through:

```bash
hint
```

To restore the intentionally broken state:

```bash
reset
```

A correct repair ends with:

```text
LAB COMPLETED
```

## Isolation model

The Docker CLI inside the lab talks to a nested Docker daemon running in a disposable `docker:dind` service. It does not mount the host Docker socket. Scenario containers and learner state therefore stay inside the lab's Compose project and named volumes.

When you are finished, exit the lab shell:

```bash
exit
```

Then remove the complete sandbox from the host:

```bash
docker compose down -v
```

## Learning objective

The scenario teaches Docker Compose service discovery. Containers in one Compose network resolve another service by its service name. The application starts with an invalid PostgreSQL hostname, and the learner has to diagnose and repair the configuration using real Docker commands.
