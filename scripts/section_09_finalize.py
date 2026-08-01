from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "docs" / "09-kubernetes" / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"


def replace_line(path: Path, prefix: str, replacement: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one {prefix!r} line in {path}, found {len(matches)}")
    lines[matches[0]] = replacement
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


replace_line(
    README,
    "Celkový authoritative stav je **32/32",
    "Celkový authoritative stav je **32/32 chapter-by-chapter explanation-depth revalidation · Ready for user review**. Posledný preserve-first pass uzavrel watch/resync a reconcile troubleshooting model, Service-to-EndpointSlice evidence, RBAC operation checks a indirect workload authority, Node capability gates, NetworkPolicy egress identity, configuration-driven rollout, layered Deployment evidence, HPA ownership a observation, Job attempt identity, server-side diff/apply, probes, QoS, quota/LimitRange, scheduling Events, taints/tolerations a upgrade inventory. Existujúce YAML, CLI, incidents, practical walkthrough a troubleshooting zostali zachované. Section 09 nemá critical ani high learning-depth findings. Repository workflow overuje dokumentačnú konzistenciu, navigation, glossary a audit; reálny Kubernetes cluster, admission, CNI, CSI, metrics pipeline, registry, cloud provider, etcd restore a upgrade neboli týmto passom vykonané. Stav preto neznamená používateľské `Accepted`, runtime `Verified` ani produkčné `Stable`.",
)

replace_line(
    LEDGER,
    "| `09-kubernetes`",
    "| `09-kubernetes` — Kubernetes | 32/32 chapter-by-chapter explanation-depth revalidation | Ready for user review | 2026-08-01 | Všetkých 32 authoritative kapitol bolo znovu prečítaných podľa API object/UID/generation, controller transition, Pod/Node/runtime identity, dataplane, storage, security a business-evidence štandardu. Existujúci plynulý `payments-api` chain, YAML/CLI/JSON, incidenty, practical walkthrough a preserve-first troubleshooting zostali zachované. Cielený pass doplnil event-independent reconcile a unknown-outcome recovery; Service/EndpointSlice a Node-cohort diagnosis; RBAC authorization a workload-created indirect privilege; capability canary, egress identity, configuration checksum rollout a layered Deployment evidence; HPA scale ownership, Job attempt identity, server-side diff/apply, probe/EndpointSlice correlation, QoS, quota/LimitRange, scheduling Events, toleration semantics a complete upgrade inventory. Section 09 nemá critical ani high learning-depth findings. README, review ledger, navigation, glossary a full audit boli synchronizované. Kubernetes API/admission, CNI/CSI, metrics, registry, cloud integrations, etcd restore a upgrade outcomes neboli týmto documentation workflowom vykonané; sekcia je Ready for user review, nie runtime Verified ani používateľsky Accepted. |",
)

print("Finalized Section 09 README and review ledger.")
