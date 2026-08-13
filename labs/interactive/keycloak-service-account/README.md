# Keycloak service-account / client-credentials lab

A guided one-command lab using a real Keycloak 26.7.0 container. The learner obtains a machine-to-machine token, inspects the JWT, and validates it through Keycloak introspection.

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest keycloak-service-account
```

Inside the lab run `help` for the assignment. No Keycloak, curl, jq, Java or other tool is required on the host; only Docker.
