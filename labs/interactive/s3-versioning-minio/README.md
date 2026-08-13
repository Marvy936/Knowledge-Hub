# S3 Versioning with MinIO

This challenge uses a disposable MinIO server as a local S3-compatible endpoint. The learner uses standard AWS CLI `s3api` commands to inspect bucket versioning, enable it, upload a second object version, and prove that both versions exist.

This is a local S3-compatible training environment. Passing the lab is not evidence of behavior in a real AWS account.

Run:

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest s3-versioning-minio
```

Inside the lab, use `help`, `status`, `check`, `hint`, and `reset`.
