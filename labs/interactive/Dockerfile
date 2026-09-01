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
      python3 \
 && aws --version \
 && ansible-playbook --version >/dev/null \
 && git --version >/dev/null \
 && python3 --version >/dev/null \
 && stat --version >/dev/null \
 && su -s /bin/sh root -c 'true'

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
COPY nginx-rate-limiting /opt/knowledge-hub/labs/nginx-rate-limiting
COPY linux-process-signals /opt/knowledge-hub/labs/linux-process-signals
COPY rag-indirect-prompt-injection /opt/knowledge-hub/labs/rag-indirect-prompt-injection
COPY mlops-model-promotion /opt/knowledge-hub/labs/mlops-model-promotion
COPY mlops-feature-parity /opt/knowledge-hub/labs/mlops-feature-parity
COPY mlops-drift-monitoring /opt/knowledge-hub/labs/mlops-drift-monitoring
COPY mlops-canary-rollback /opt/knowledge-hub/labs/mlops-canary-rollback
COPY mlops-ab-experiment-integrity /opt/knowledge-hub/labs/mlops-ab-experiment-integrity
COPY mlops-retraining-trigger /opt/knowledge-hub/labs/mlops-retraining-trigger
COPY mlops-training-run-lineage /opt/knowledge-hub/labs/mlops-training-run-lineage
COPY mlops-offline-evaluation-integrity /opt/knowledge-hub/labs/mlops-offline-evaluation-integrity
COPY mlops-release-delivery-integrity /opt/knowledge-hub/labs/mlops-release-delivery-integrity
COPY mlops-feedback-ground-truth-integrity /opt/knowledge-hub/labs/mlops-feedback-ground-truth-integrity
COPY mlops-online-inference-integrity /opt/knowledge-hub/labs/mlops-online-inference-integrity
COPY mlops-streaming-inference-integrity /opt/knowledge-hub/labs/mlops-streaming-inference-integrity
COPY mlops-batch-inference-integrity /opt/knowledge-hub/labs/mlops-batch-inference-integrity
COPY mlops-serving-autoscaling-integrity /opt/knowledge-hub/labs/mlops-serving-autoscaling-integrity
COPY mlops-gpu-resource-isolation-integrity /opt/knowledge-hub/labs/mlops-gpu-resource-isolation-integrity
COPY mlops-model-monitoring-integrity /opt/knowledge-hub/labs/mlops-model-monitoring-integrity
COPY mlops-drift-population-integrity /opt/knowledge-hub/labs/mlops-drift-population-integrity
COPY mlops-performance-cost-integrity /opt/knowledge-hub/labs/mlops-performance-cost-integrity
COPY mlops-rollback-recovery-integrity /opt/knowledge-hub/labs/mlops-rollback-recovery-integrity
COPY mlops-governance-approval-audit-integrity /opt/knowledge-hub/labs/mlops-governance-approval-audit-integrity
COPY mlops-security-privacy-integrity /opt/knowledge-hub/labs/mlops-security-privacy-integrity

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
 && ln -s selftest /opt/knowledge-hub/labs/linux-file-permissions/lab/self-test \
 && ln -s verify /opt/knowledge-hub/labs/nginx-rate-limiting/lab/check \
 && ln -s hints /opt/knowledge-hub/labs/nginx-rate-limiting/lab/hint \
 && ln -s reset-lab /opt/knowledge-hub/labs/nginx-rate-limiting/lab/reset \
 && ln -s status-lab /opt/knowledge-hub/labs/nginx-rate-limiting/lab/status \
 && ln -s selftest /opt/knowledge-hub/labs/nginx-rate-limiting/lab/self-test \
 && ln -s verify /opt/knowledge-hub/labs/linux-process-signals/lab/check \
 && ln -s hints /opt/knowledge-hub/labs/linux-process-signals/lab/hint \
 && ln -s reset-lab /opt/knowledge-hub/labs/linux-process-signals/lab/reset \
 && ln -s status-lab /opt/knowledge-hub/labs/linux-process-signals/lab/status \
 && ln -s selftest /opt/knowledge-hub/labs/linux-process-signals/lab/self-test \
 && ln -s verify /opt/knowledge-hub/labs/rag-indirect-prompt-injection/lab/check \
 && ln -s hints /opt/knowledge-hub/labs/rag-indirect-prompt-injection/lab/hint \
 && ln -s reset-lab /opt/knowledge-hub/labs/rag-indirect-prompt-injection/lab/reset \
 && ln -s status-lab /opt/knowledge-hub/labs/rag-indirect-prompt-injection/lab/status \
 && ln -s selftest /opt/knowledge-hub/labs/rag-indirect-prompt-injection/lab/self-test \
 && ln -s verify /opt/knowledge-hub/labs/mlops-model-promotion/lab/check \
 && ln -s hints /opt/knowledge-hub/labs/mlops-model-promotion/lab/hint \
 && ln -s reset-lab /opt/knowledge-hub/labs/mlops-model-promotion/lab/reset \
 && ln -s status-lab /opt/knowledge-hub/labs/mlops-model-promotion/lab/status \
 && ln -s selftest /opt/knowledge-hub/labs/mlops-model-promotion/lab/self-test \
 && ln -s verify /opt/knowledge-hub/labs/mlops-feature-parity/lab/check \
 && ln -s hints /opt/knowledge-hub/labs/mlops-feature-parity/lab/hint \
 && ln -s reset-lab /opt/knowledge-hub/labs/mlops-feature-parity/lab/reset \
 && ln -s status-lab /opt/knowledge-hub/labs/mlops-feature-parity/lab/status \
 && ln -s selftest /opt/knowledge-hub/labs/mlops-feature-parity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-drift-monitoring/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-drift-monitoring/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-drift-monitoring/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-drift-monitoring/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-drift-monitoring/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-drift-monitoring/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-drift-monitoring/lab/analyze \
 && ln -s driver /opt/knowledge-hub/labs/mlops-canary-rollback/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-canary-rollback/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-canary-rollback/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-canary-rollback/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-canary-rollback/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-canary-rollback/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-canary-rollback/lab/decide \
 && ln -s driver /opt/knowledge-hub/labs/mlops-ab-experiment-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-ab-experiment-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-ab-experiment-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-ab-experiment-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-ab-experiment-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-ab-experiment-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-ab-experiment-integrity/lab/analyze \
 && ln -s driver /opt/knowledge-hub/labs/mlops-retraining-trigger/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-retraining-trigger/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-retraining-trigger/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-retraining-trigger/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-retraining-trigger/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-retraining-trigger/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-retraining-trigger/lab/coordinate \
 && ln -s driver /opt/knowledge-hub/labs/mlops-training-run-lineage/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-training-run-lineage/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-training-run-lineage/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-training-run-lineage/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-training-run-lineage/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-training-run-lineage/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-training-run-lineage/lab/attest \
 && ln -s driver /opt/knowledge-hub/labs/mlops-offline-evaluation-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-offline-evaluation-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-offline-evaluation-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-offline-evaluation-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-offline-evaluation-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-offline-evaluation-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-offline-evaluation-integrity/lab/evaluate \
 && ln -s driver /opt/knowledge-hub/labs/mlops-release-delivery-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-release-delivery-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-release-delivery-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-release-delivery-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-release-delivery-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-release-delivery-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-release-delivery-integrity/lab/deliver \
 && ln -s driver /opt/knowledge-hub/labs/mlops-feedback-ground-truth-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-feedback-ground-truth-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-feedback-ground-truth-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-feedback-ground-truth-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-feedback-ground-truth-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-feedback-ground-truth-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-feedback-ground-truth-integrity/lab/analyze \
 && ln -s driver /opt/knowledge-hub/labs/mlops-online-inference-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-online-inference-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-online-inference-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-online-inference-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-online-inference-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-online-inference-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-online-inference-integrity/lab/infer \
 && ln -s driver /opt/knowledge-hub/labs/mlops-streaming-inference-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-streaming-inference-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-streaming-inference-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-streaming-inference-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-streaming-inference-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-streaming-inference-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-streaming-inference-integrity/lab/consume \
 && ln -s driver /opt/knowledge-hub/labs/mlops-batch-inference-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-batch-inference-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-batch-inference-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-batch-inference-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-batch-inference-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-batch-inference-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-batch-inference-integrity/lab/run \
 && ln -s driver /opt/knowledge-hub/labs/mlops-serving-autoscaling-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-serving-autoscaling-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-serving-autoscaling-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-serving-autoscaling-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-serving-autoscaling-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-serving-autoscaling-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-serving-autoscaling-integrity/lab/assess \
 && ln -s driver /opt/knowledge-hub/labs/mlops-gpu-resource-isolation-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-gpu-resource-isolation-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-gpu-resource-isolation-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-gpu-resource-isolation-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-gpu-resource-isolation-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-gpu-resource-isolation-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-gpu-resource-isolation-integrity/lab/assess \
 && ln -s driver /opt/knowledge-hub/labs/mlops-model-monitoring-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-model-monitoring-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-model-monitoring-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-model-monitoring-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-model-monitoring-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-model-monitoring-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-model-monitoring-integrity/lab/assess \
 && ln -s driver /opt/knowledge-hub/labs/mlops-drift-population-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-drift-population-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-drift-population-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-drift-population-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-drift-population-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-drift-population-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-drift-population-integrity/lab/assess

RUN ln -s driver /opt/knowledge-hub/labs/mlops-performance-cost-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-performance-cost-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-performance-cost-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-performance-cost-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-performance-cost-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-performance-cost-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-performance-cost-integrity/lab/assess

RUN ln -s driver /opt/knowledge-hub/labs/mlops-rollback-recovery-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-rollback-recovery-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-rollback-recovery-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-rollback-recovery-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-rollback-recovery-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-rollback-recovery-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-rollback-recovery-integrity/lab/assess \
 && ln -s driver /opt/knowledge-hub/labs/mlops-rollback-recovery-integrity/lab/recover

RUN ln -s driver /opt/knowledge-hub/labs/mlops-governance-approval-audit-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-governance-approval-audit-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-governance-approval-audit-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-governance-approval-audit-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-governance-approval-audit-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-governance-approval-audit-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-governance-approval-audit-integrity/lab/assess \
 && ln -s driver /opt/knowledge-hub/labs/mlops-governance-approval-audit-integrity/lab/review

RUN ln -s driver /opt/knowledge-hub/labs/mlops-security-privacy-integrity/lab/lab-help \
 && ln -s driver /opt/knowledge-hub/labs/mlops-security-privacy-integrity/lab/check \
 && ln -s driver /opt/knowledge-hub/labs/mlops-security-privacy-integrity/lab/hint \
 && ln -s driver /opt/knowledge-hub/labs/mlops-security-privacy-integrity/lab/reset \
 && ln -s driver /opt/knowledge-hub/labs/mlops-security-privacy-integrity/lab/status \
 && ln -s driver /opt/knowledge-hub/labs/mlops-security-privacy-integrity/lab/self-test \
 && ln -s driver /opt/knowledge-hub/labs/mlops-security-privacy-integrity/lab/assess \
 && ln -s driver /opt/knowledge-hub/labs/mlops-security-privacy-integrity/lab/secure

RUN chmod +x \
      /opt/knowledge-hub/runtime/entrypoint.sh \
      /opt/knowledge-hub/runtime/list-labs \
      /opt/knowledge-hub/runtime/list-lab-ids \
      /opt/knowledge-hub/runtime/validate-registry \
 && find /opt/knowledge-hub/labs -type f -path '*/lab/*' -exec chmod +x {} + \
 && /opt/knowledge-hub/runtime/validate-registry

ENV DOCKER_TLS_CERTDIR=""
WORKDIR /workspace
ENTRYPOINT ["/opt/knowledge-hub/runtime/entrypoint.sh"]