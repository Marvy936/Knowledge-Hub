FROM hashicorp/terraform:1.15.6 AS terraform

FROM docker:27-dind

# docker:27-dind can contain older Alpine base packages than the current
# repository index. Upgrade the base first so Python/libexpat and aws-cli
# are installed from one consistent package set.
RUN apk upgrade --no-cache \
 && apk add --no-cache \
      ansible-core \
      aws-cli \
      bash \
      bind-tools \
      coreutils \
      curl \
      docker-cli-compose \
      git \
      iputils \
      jq \
      nano \
      openssl \
      shadow \
 && aws --version \
 && ansible-playbook --version >/dev/null \
 && git --version >/dev/null \
 && su --version >/dev/null

COPY --from=terraform /bin/terraform /usr/local/bin/terraform
RUN terraform version >/dev/null

LABEL org.opencontainers.image.source="https://github.com/Marvy936/Knowledge-Hub" \
      org.opencontainers.image.description="Knowledge Hub one-command interactive lab runtime"

COPY runtime /opt/knowledge-hub/runtime
COPY docker-network-debug /opt/knowledge-hub/labs/docker-network-debug
COPY docker-volume-persistence /opt/knowledge-hub/labs/docker-volume-persistence
COPY keycloak-service-account /opt/knowledge-hub/labs/keycloak-service-account
COPY postgres-index-performance /opt/knowledge-hub/labs/postgres-index-performance
COPY prometheus-target-alert /opt/knowledge-hub/labs/prometheus-target-alert
COPY nginx-reverse-proxy /opt/knowledge-hub/labs/nginx-reverse-proxy
COPY redis-cache-ttl /opt/knowledge-hub/labs/redis-cache-ttl
COPY tls-certificate-hostname /opt/knowledge-hub/labs/tls-certificate-hostname
COPY terraform-state-drift /opt/knowledge-hub/labs/terraform-state-drift
COPY kubernetes-configmap-rollout /opt/knowledge-hub/labs/kubernetes-configmap-rollout
COPY s3-versioning-minio /opt/knowledge-hub/labs/s3-versioning-minio
COPY rabbitmq-routing-key /opt/knowledge-hub/labs/rabbitmq-routing-key
COPY postgres-backup-restore /opt/knowledge-hub/labs/postgres-backup-restore
COPY localstack-s3-versioning /opt/knowledge-hub/labs/localstack-s3-versioning
COPY ansible-idempotency /opt/knowledge-hub/labs/ansible-idempotency
COPY git-three-way-merge /opt/knowledge-hub/labs/git-three-way-merge
COPY bash-pipeline-failure /opt/knowledge-hub/labs/bash-pipeline-failure
COPY linux-file-permissions /opt/knowledge-hub/labs/linux-file-permissions

# README remains the canonical assignment; generate tiny runtime wrappers.
# Every help entrypoint starts with the shared marker used by registry smoke tests.
RUN printf '%s\n' \
      '#!/usr/bin/env bash' \
      'echo "Knowledge Hub Interactive Lab"' \
      'cat "$LAB_ROOT/README.md"' \
      > /opt/knowledge-hub/labs/postgres-backup-restore/lab/lab-help \
 && printf '%s\n' '#!/usr/bin/env bash' 'check || true' \
      > /opt/knowledge-hub/labs/postgres-backup-restore/lab/status

# Source helper names avoid GitHub write-path restrictions; expose the normal
# lab UX names in the built image.
RUN ln -s verify /opt/knowledge-hub/labs/ansible-idempotency/lab/check \
 && ln -s hints /opt/knowledge-hub/labs/ansible-idempotency/lab/hint \
 && ln -s reset-lab /opt/knowledge-hub/labs/ansible-idempotency/lab/reset \
 && ln -s status-lab /opt/knowledge-hub/labs/ansible-idempotency/lab/status \
 && ln -s selftest /opt/knowledge-hub/labs/ansible-idempotency/lab/self-test \
 && ln -s verify /opt/knowledge-hub/labs/git-three-way-merge/lab/check \
 && ln -s hints /opt/knowledge-hub/labs/git-three-way-merge/lab/hint \
 && ln -s reset-lab /opt/knowledge-hub/labs/git-three-way-merge/lab/reset \
 && ln -s status-lab /opt/knowledge-hub/labs/git-three-way-merge/lab/status \
 && ln -s selftest /opt/knowledge-hub/labs/git-three-way-merge/lab/self-test \
 && ln -s verify /opt/knowledge-hub/labs/bash-pipeline-failure/lab/check \
 && ln -s hints /opt/knowledge-hub/labs/bash-pipeline-failure/lab/hint \
 && ln -s reset-lab /opt/knowledge-hub/labs/bash-pipeline-failure/lab/reset \
 && ln -s status-lab /opt/knowledge-hub/labs/bash-pipeline-failure/lab/status \
 && ln -s selftest /opt/knowledge-hub/labs/bash-pipeline-failure/lab/self-test \
 && ln -s verify /opt/knowledge-hub/labs/linux-file-permissions/lab/check \
 && ln -s hints /opt/knowledge-hub/labs/linux-file-permissions/lab/hint \
 && ln -s reset-lab /opt/knowledge-hub/labs/linux-file-permissions/lab/reset \
 && ln -s status-lab /opt/knowledge-hub/labs/linux-file-permissions/lab/status \
 && ln -s selftest /opt/knowledge-hub/labs/linux-file-permissions/lab/self-test

RUN chmod +x \
      /opt/knowledge-hub/runtime/entrypoint.sh \
      /opt/knowledge-hub/runtime/list-labs \
      /opt/knowledge-hub/runtime/list-lab-ids \
 && find /opt/knowledge-hub/labs -type f -path '*/lab/*' -exec chmod +x {} +

ENV DOCKER_TLS_CERTDIR=""
WORKDIR /workspace
ENTRYPOINT ["/opt/knowledge-hub/runtime/entrypoint.sh"]
