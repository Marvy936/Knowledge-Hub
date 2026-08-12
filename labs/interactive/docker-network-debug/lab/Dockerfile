FROM docker:27-cli

RUN apk add --no-cache \
      bash \
      bind-tools \
      curl \
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

RUN chmod +x /opt/knowledge-hub/bin/*

ENV PATH="/opt/knowledge-hub/bin:${PATH}"
WORKDIR /workspace
ENTRYPOINT ["/opt/knowledge-hub/bin/entrypoint.sh"]
