# Terraform state drift

Challenge lab for Terraform drift detection and reconciliation. Terraform 1.15.6 and the official `hashicorp/local` provider are bundled inside the public lab image. The lab creates a managed file, changes it outside Terraform, and asks the learner to diagnose the plan and reconcile the resource.

Run:

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest terraform-state-drift
```
