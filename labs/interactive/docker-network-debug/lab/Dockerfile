FROM docker:27-dind

LABEL org.opencontainers.image.source="https://github.com/Marvy936/Knowledge-Hub" \
      org.opencontainers.image.title="Knowledge Hub - Docker Network Debug Lab" \
      org.opencontainers.image.description="Self-contained Docker-only interactive troubleshooting lab"

RUN apk add --no-cache \
      bash \
      bind-tools \
      curl \
      docker-cli-compose \
      iputils \
      jq \
      nano

COPY scenario.compose.yaml /opt/knowledge-hub/scenario.compose.yaml
COPY scenario.env.template /opt/knowledge-hub/scenario.env.template
COPY lab/entrypoint.sh /opt/knowledge-hub/bin/entrypoint.sh
COPY lab/check /opt/knowledge-hub/bin/check
COPY lab/hint /opt/knowledge-hub/bin/hint
COPY lab/apply /opt/knowledge-hub/bin/apply
COPY lab/reset /opt/knowledge-hub/bin/reset
COPY lab/status /opt/knowledge-hub/bin/status
COPY lab/lab-help /opt/knowledge-hub/bin/lab-help
COPY lab/self-test /opt/knowledge-hub/bin/self-test
COPY lab/bashrc /opt/knowledge-hub/bashrc

RUN chmod +x /opt/knowledge-hub/bin/*

ENV PATH="/opt/knowledge-hub/bin:${PATH}" \
    DOCKER_HOST="unix:///var/run/docker.sock" \
    LAB_WORKSPACE="/workspace"

WORKDIR /workspace
ENTRYPOINT ["/opt/knowledge-hub/bin/entrypoint.sh"]
