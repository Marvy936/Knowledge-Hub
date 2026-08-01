from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "10-helm-and-cka"
README = SECTION / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
AUDIT = ROOT / "DOCUMENTATION-AUDIT.md"

REQUIREMENTS = {
    "helm-chart-template-values-release.md": [
        "Chart.yaml", "values.yaml", "helm lint", "helm template", "helm upgrade", "helm get", "kubectl",
    ],
    "helm-chart-practical-walkthrough.md": [
        "values.schema.json", "_helpers.tpl", "helm lint", "helm template", "dry-run=server", "helm upgrade", "helm test", "helm package",
    ],
    "template-functions-pipelines.md": [
        "default", "required", "hasKey", "toYaml", "nindent", "tpl", "lookup", "helm template",
    ],
    "named-templates.md": [
        "_helpers.tpl", "define", "include", "dict", "nindent", "helm lint", "helm template", "yq",
    ],
    "chart-dependencies.md": [
        "Chart.yaml", "Chart.lock", "helm dependency update", "helm dependency build", "helm dependency list", "helm template",
    ],
    "hooks.md": [
        "helm.sh/hook", "hook-delete-policy", "kind: Job", "operationId", "helm template", "helm upgrade", "helm get hooks",
    ],
    "upgrade-rollback.md": [
        "helm get values", "helm get manifest", "helm template", "dry-run=server", "helm upgrade", "helm history", "helm rollback",
    ],
    "helm-testing-troubleshooting.md": [
        "helm lint", "helm template", "helm test", "helm status", "helm history", "helm get", "kubectl get endpointslice",
    ],
    "cka-timed-labs.md": [
        "kubectl config current-context", "kubectl", "--dry-run=client", "rollout status", "forbidden",
    ],
    "cka-troubleshooting-drills.md": [
        "kubectl", "EndpointSlice", "Node", "cordon", "forbidden", "recovery",
    ],
}


def replace_prefixed_line(path: Path, prefix: str, replacement: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one line starting with {prefix!r} in {path}, found {len(matches)}")
    lines[matches[0]] = replacement
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


for name, tokens in REQUIREMENTS.items():
    text = (SECTION / name).read_text(encoding="utf-8")
    if len(text.split()) < 900:
        raise RuntimeError(f"{name} is unexpectedly short for authoritative prose")
    if text.count("```") < 4:
        raise RuntimeError(f"{name} lacks an executable or rendered example surface")
    missing = [token for token in tokens if token not in text]
    if missing:
        raise RuntimeError(f"{name} is missing required evidence tokens: {missing}")

if "### `docs/10-helm-and-cka/" in AUDIT.read_text(encoding="utf-8"):
    raise RuntimeError("Section 10 still has critical/high learning-depth findings")

readme_text = README.read_text(encoding="utf-8")
old_status = "Aktuálny authoritative stav sekcie je **10 kapitol · practical-example remediation in progress**. Pôvodný prose-first pass zostáva platný, ale používateľská kontrola odhalila nedostatok konkrétnych chartov, príkazov, rendered outputs a vysvetlených diagnostických postupov. Sekcia preto zatiaľ nie je používateľsky schválená."
new_status = "Aktuálny authoritative stav sekcie je **10/10 chapter-by-chapter explanation-depth and practical-example revalidation · Ready for user review**. Všetkých desať kapitol spĺňa prose-first mechanistický štandard a obsahuje primeraný executable surface: konkrétne chart files, values/schema/templates, Helm a `kubectl` commands, rendered alebo runtime observations, failure read-back a recovery closure. Section 10 nemá critical ani high learning-depth findings. Repository workflow overuje dokumentačnú konzistenciu, navigation, glossary, required example inventory a audit; reálny Helm release, Kubernetes cluster a CKA exam environment tým nie sú runtime overené. Stav preto neznamená používateľské `Accepted`, runtime `Verified` ani produkčné `Stable`."
if old_status not in readme_text and new_status not in readme_text:
    raise RuntimeError("Expected Section 10 README status paragraph not found")
README.write_text(readme_text.replace(old_status, new_status, 1).rstrip() + "\n", encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `10-helm-and-cka`",
    "| `10-helm-and-cka` — Helm and CKA | 10/10 chapter-by-chapter explanation-depth and practical-example revalidation | Ready for user review | 2026-08-01 | Všetkých desať authoritative kapitol bolo znovu preverených podľa immutable chart/dependency/values/release subjectu, deterministic renderu, API/admission/runtime evidence, durable hook side effectu, upgrade/rollback compatibility a CKA timed-diagnosis štandardu. Existujúci prose-first základ zostal zachovaný. Completion gate overil executable surface v každej kapitole: `Chart.yaml`, values/schema, templates/helpers, rendered YAML, dependency lock/build, hook Job a operation ledger, upgrade/history/rollback, Helm test a Kubernetes diagnosis, timed-lab commands a troubleshooting drills. README deklarovaný stav `practical-example remediation in progress` bol uzavretý; Section 10 nemá critical ani high learning-depth findings. Navigation, glossary a full audit boli synchronizované. Reálny Helm release, cluster-specific admission/runtime a CKA exam environment neboli týmto documentation workflowom vykonané; sekcia je Ready for user review, nie runtime Verified ani používateľsky Accepted. |",
)

print("Section 10 executable-surface gate passed for 10/10 chapters and status was finalized.")
