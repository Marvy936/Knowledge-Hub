# Prometheus scrape target and alert troubleshooting

Run with Docker only:

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest prometheus-target-alert
```

The lab starts a real Prometheus and node-exporter. The scrape target uses the wrong port, so `up{job="node"}` is 0 and `NodeExporterDown` fires. The learner repairs `prometheus.yml`; `check` validates target health, the recorded metric and alert resolution.
