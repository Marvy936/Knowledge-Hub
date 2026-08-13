# Nginx reverse-proxy troubleshooting

Run with Docker only:

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest nginx-reverse-proxy
```

The backend is healthy, but the Nginx gateway starts with an invalid upstream hostname. The learner uses real Nginx logs and Docker service names to repair `nginx.conf`. `check` validates backend health, gateway state and the proxied response.
