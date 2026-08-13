# PostgreSQL index performance

Run with Docker only:

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest postgres-index-performance
```

The lab seeds 100000 orders, starts with a sequential-scan query plan and asks the learner to add a useful composite index. `check` verifies the index, the actual PostgreSQL plan and the unchanged query result. `reset` removes the repair and restores the original state.
