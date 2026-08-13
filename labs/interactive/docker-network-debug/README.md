# Docker service discovery troubleshooting

This is the first one-command Knowledge Hub interactive lab.

## Requirement

Only Docker is required on the host. You do not need this repository, Git, Docker Compose, Python, `curl`, `jq`, PostgreSQL tools, or any other lab dependency.

Once the GHCR package is public, run from any terminal:

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest
```

The image starts its own isolated Docker engine, creates the intentionally broken PostgreSQL scenario, and drops you directly into the lab terminal.

## Inside the lab

You will see:

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

To display the assignment and command list again at any time:

```bash
help
```

`lab-help` and `task` show the same screen.

To restore the intentionally broken state:

```bash
reset
```

A correct repair ends with:

```text
LAB COMPLETED
```

## Isolation and security model

The image runs a nested Docker daemon inside the lab container. Scenario containers never use the host Docker socket. The lab therefore needs `--privileged`, which gives the lab container elevated privileges inside the Docker host/VM. Run only trusted Knowledge Hub lab images and keep the image reference explicit.

Because the outer container is started with `--rm`, exiting the lab removes the complete disposable sandbox:

```bash
exit
```

## Learning objective

The scenario teaches Docker Compose service discovery. Containers in one Compose network resolve another service by its service name. The application starts with an invalid PostgreSQL hostname, and the learner has to diagnose and repair the configuration using real Docker commands.
