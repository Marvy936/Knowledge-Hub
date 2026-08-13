# Redis cache TTL

Challenge lab for stale-cache diagnosis. The initial Redis key contains an outdated value and no expiration. Use real `redis-cli` commands through the sandbox container, repair the cached value and give it a bounded TTL, then run `check`.

Run:

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest redis-cache-ttl
```
