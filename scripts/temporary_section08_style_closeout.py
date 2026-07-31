from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WALKTHROUGH = ROOT / "docs/08-container-fundamentals-and-docker/docker-practical-walkthrough.md"
README = ROOT / "docs/08-container-fundamentals-and-docker/README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label} occurrence, found {count}")
    return text.replace(old, new, 1)


walkthrough = WALKTHROUGH.read_text(encoding="utf-8")

walkthrough = replace_once(
    walkthrough,
    """FROM ${RUNTIME_IMAGE} AS runtime

LABEL org.opencontainers.image.title=\"Atlas Payments API\" \\
""",
    """FROM ${RUNTIME_IMAGE} AS runtime
ARG VERSION
ARG VCS_REF

LABEL org.opencontainers.image.title=\"Atlas Payments API\" \\
""",
    "runtime-stage ARG declarations",
)

walkthrough = replace_once(
    walkthrough,
    """  buildkitVersion: v0.26.2
  buildxVersion: v0.29.1
""",
    """  buildkitVersion: <recorded-buildkit-version>
  buildxVersion: <recorded-buildx-version>
""",
    "tool-version placeholders",
)

walkthrough = replace_once(
    walkthrough,
    """docker run --rm \\
  --user 0:0 \\
  --mount type=volume,source=atlas-payments-data,target=/data \\
  \"$RUNTIME_IMAGE\" \\
  sh -c 'mkdir -p /data && chown -R 65532:65532 /data'
""",
    """docker run --rm \\
  --user 0:0 \\
  --mount type=volume,source=atlas-payments-data,target=/data \\
  busybox:1.36.1@sha256:<verified-busybox-digest> \\
  sh -c 'mkdir -p /data && chown -R 65532:65532 /data'
""",
    "volume initializer image",
)

walkthrough = replace_once(
    walkthrough,
    """  init-data:
    image: gcr.io/distroless/static-debian12:nonroot@sha256:<verified-runtime-base-digest>
    user: \"0:0\"
    entrypoint: [\"/busybox/sh\", \"-ec\"]
""",
    """  init-data:
    image: busybox:1.36.1@sha256:<verified-busybox-digest>
    user: \"0:0\"
    entrypoint: [\"/bin/sh\", \"-ec\"]
""",
    "Compose initializer image",
)

walkthrough = replace_once(
    walkthrough,
    """docker compose \\
  --env-file .env \\
  --profile verify \\
  run --rm verifier
""",
    """docker compose \\
  --env-file .env \\
  --profile verify \\
  run --rm --no-deps verifier
""",
    "verifier execution",
)

WALKTHROUGH.write_text(walkthrough, encoding="utf-8")

readme = README.read_text(encoding="utf-8")
readme = readme.replace(
    "Praktický Docker projekt od Dockerfile-u po overený Compose runtime",
    "Praktický Docker release od source zmeny po overený runtime",
)

old_description = """Kapitola [Praktický Docker release od source zmeny po overený runtime](docker-practical-walkthrough.md) vytvára malú Go HTTP službu s health, readiness, version a persistentným payment write/read contractom. Následne prechádza celý source tree, unit testy, `.dockerignore`, multi-stage Dockerfile, explicitný BuildKit test target, local single-platform build, image config a filesystem inspection, constrained `docker run`, non-root volume initialization, PID 1 a signal handling, health history, host port, named-volume persistence, Compose interpolation a resolved model, `depends_on` conditions, service DNS, runtime-hardening read-back, second `compose up`, configuration recreate, multi-platform registry publication, digest-pinned consumption a evidence-preserving troubleshooting.

Walkthrough obsahuje reálny Go source, testy, Dockerfile, Compose YAML, Bash a PowerShell commands, `jq`/`yq` assertions a GitLab release skeleton. Pri každom významnom kroku vysvetľuje, čo output preukazuje a čo ešte nie. Failure paths zahŕňajú container-loopback bind mismatch, volume ownership, mount obscuring, green process health pri zlyhávajúcom business write, mutable tag po scan-e, cgroup OOM a nesprávnu platformu alebo loader.
"""

new_description = """Kapitola [Praktický Docker release od source zmeny po overený runtime](docker-practical-walkthrough.md) používa existujúcu službu `payments-api` ako jeden súvislý release scenár. Neodbieha do implementácie aplikácie; sústreďuje sa na Docker mechanizmus od build contextu a multi-stage graphu cez explicitný test target, image config/layers/digest, registry publication, constrained container create/start, PID 1, volume a network identity až po Compose reconciliation, multi-platform read-back a business verification.

Text je prepracovaný v rovnakom prose-first rytme ako Keycloak a CI/CD: najprv vysvetlí dominantný source-to-runtime model, potom presný release subject, konkrétne Dockerfile a Compose rozhodnutia, dôkazové hranice jednotlivých príkazov a connected incident `CTR-PAY-81`. Incident spája rozdielnych builderov, mutable tag, neúplný platform scan, plytký health oracle a nekompatibilný volume ownership do jedného diagnostického a recovery flowu.
"""

readme = replace_once(readme, old_description, new_description, "README walkthrough description")
README.write_text(readme, encoding="utf-8")

ledger = LEDGER.read_text(encoding="utf-8")
old_ledger = "Praktická remediation pridala `docker-practical-walkthrough.md`, ktorý vytvára celý Go/Docker/Compose project od source a testov cez `.dockerignore`, multi-stage Dockerfile, BuildKit test graph, local a multi-platform image build, image/runtime inspect, non-root read-only container, cgroup/capability boundary, named-volume persistence, host port a service DNS, Compose resolved model, second reconciliation, digest-pinned registry consumption a evidence-preserving troubleshooting."
new_ledger = "Praktická remediation pridala a následne prose-first prepracovala `docker-practical-walkthrough.md`. Kapitola už neprogramuje celý ukážkový Go projekt, ale sleduje jeden Docker release od build contextu a multi-stage graphu cez explicitný test target, image/index/platform digesty, constrained runtime, volume a network identity, Compose reconciliation a connected incident `CTR-PAY-81` až po evidence-preserving recovery."
ledger = replace_once(ledger, old_ledger, new_ledger, "ledger walkthrough summary")
LEDGER.write_text(ledger, encoding="utf-8")
