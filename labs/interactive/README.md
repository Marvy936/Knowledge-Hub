# Knowledge Hub Interactive Labs

Interactive Labs are disposable hands-on environments distributed as container images. The learner should need only Docker on the host; lab-specific CLIs, services, validation, hints, reset logic and editors live inside the image.

## User contract

A published lab should be runnable from any terminal with one command of this form:

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/<lab-image>:latest
```

Not every future lab will require `--privileged`; the first Docker troubleshooting lab does because it runs a nested Docker daemon. Public GHCR packages can be pulled anonymously.

Inside a lab, the common learner commands are:

```text
help      show the assignment and command list
status    inspect the current scenario
check     validate the learner solution
hint      reveal progressive help
apply     re-apply learner configuration when relevant
reset     restore the initial scenario
```

`lab-help` and `task` are aliases for the full help screen in the reference implementation.

## Reference lab

[`docker-network-debug`](docker-network-debug/README.md) is the first reference implementation. It packages the Docker CLI, Docker Compose plugin, troubleshooting utilities, a nested Docker engine, PostgreSQL scenario, progressive hints and automated validation in one image.

The reference challenge is valid only if:

1. the initial scenario fails meaningful validation,
2. the intended learner repair makes validation pass,
3. `reset` restores the failing initial state,
4. the complete lifecycle runs without host-side tooling other than Docker.

CI enforces this contract by running the image's built-in `self-test`.

## Registry

The initial registry target is GitHub Container Registry (GHCR). The repository workflow publishes:

```text
ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest
```

GitHub creates a new GHCR package as private by default. After its first publication, package visibility must be changed to Public once in GitHub Package settings so learners can run it without authentication.
