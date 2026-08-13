FROM docker:27-dind

RUN apk add --no-cache \
      bash \
      bind-tools \
      curl \
      docker-cli-compose \
      iputils \
      jq \
      nano

LABEL org.opencontainers.image.source="https://github.com/Marvy936/Knowledge-Hub" \
      org.opencontainers.image.description="Knowledge Hub one-command interactive lab runtime"

COPY runtime /opt/knowledge-hub/runtime
COPY docker-network-debug /opt/knowledge-hub/labs/docker-network-debug
COPY docker-volume-persistence /opt/knowledge-hub/labs/docker-volume-persistence
COPY keycloak-service-account /opt/knowledge-hub/labs/keycloak-service-account
COPY postgres-index-performance /opt/knowledge-hub/labs/postgres-index-performance
COPY prometheus-target-alert /opt/knowledge-hub/labs/prometheus-target-alert
COPY nginx-reverse-proxy /opt/knowledge-hub/labs/nginx-reverse-proxy

RUN chmod +x \
      /opt/knowledge-hub/runtime/entrypoint.sh \
      /opt/knowledge-hub/runtime/list-labs \
      /opt/knowledge-hub/runtime/list-lab-ids \
 && find /opt/knowledge-hub/labs -type f -path '*/lab/*' -exec chmod +x {} +

ENV DOCKER_TLS_CERTDIR=""
WORKDIR /workspace
ENTRYPOINT ["/opt/knowledge-hub/runtime/entrypoint.sh"]
