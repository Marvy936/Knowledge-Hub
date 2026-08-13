# TLS certificate hostname

Challenge lab for certificate SAN troubleshooting. The initial server certificate is signed by the lab CA but is valid for the wrong hostname. Repair the certificate request configuration, regenerate the certificate with `apply`, and prove a hostname-verified HTTPS request succeeds.

Run:

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest tls-certificate-hostname
```
