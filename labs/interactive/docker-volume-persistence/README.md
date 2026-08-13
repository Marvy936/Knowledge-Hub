# Docker volume persistence troubleshooting

A challenge where a named volume exists but is mounted at the wrong destination, so application data does not survive container recreation.

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest docker-volume-persistence
```

Inside the lab use `help`, normal Docker inspection commands, edit `/workspace/scenario.compose.yaml`, then run `apply` and `check`.
