from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "16-gitops-and-platform-engineering"
README = SECTION / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
AUDIT = ROOT / "DOCUMENTATION-AUDIT.md"

ARTICLES = [
    "git-as-source-of-truth.md",
    "pull-based-deployment.md",
    "reconciliation-and-drift-detection.md",
    "argo-cd.md",
    "flux.md",
    "application-promotion.md",
    "gitops-secrets.md",
    "internal-developer-platform.md",
    "platform-as-a-product.md",
    "golden-paths-and-paved-road.md",
    "self-service.md",
    "developer-experience.md",
    "service-catalog.md",
    "guardrails.md",
    "multi-tenancy.md",
    "gitops-practical-walkthrough.md",
    "gitops-troubleshooting.md",
]


def replace_prefixed_line(path: Path, prefix: str, replacement: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one line starting with {prefix!r} in {path}, found {len(matches)}")
    lines[matches[0]] = replacement
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


for name in ARTICLES:
    text = (SECTION / name).read_text(encoding="utf-8")
    words = len(text.split())
    if words < 900:
        raise RuntimeError(f"{name} is unexpectedly short: {words} words")
    if text.count("```") < 4:
        raise RuntimeError(f"{name} lacks two executable/model/configuration examples")
    lowered = text.lower()
    required_groups = [
        ("subject",),
        ("evidence", "dôkaz", "verdict", "ukazuje", "opisuje", "potvrdzuje"),
        ("recovery", "obnova", "náprava", "reconciliation"),
        ("acceptance", "prijatie", "akcept", "positive path", "recovery path"),
    ]
    missing = [group for group in required_groups if not any(token in lowered for token in group)]
    if missing:
        raise RuntimeError(f"{name} lacks subject/evidence/recovery/acceptance language: {missing}")

if "### `docs/16-gitops-and-platform-engineering/" in AUDIT.read_text(encoding="utf-8"):
    raise RuntimeError("Section 16 still has critical/high learning-depth findings")

readme = README.read_text(encoding="utf-8")
old_authoritative = "Aktuálny authoritative stav sekcie je **17/17 · Ready for user review**."
new_authoritative = "Aktuálny authoritative stav sekcie je **17/17 chapter-by-chapter explanation-depth and practical-example revalidation · Ready for user review**."
if old_authoritative not in readme and new_authoritative not in readme:
    raise RuntimeError("Expected Section 16 authoritative status paragraph not found")
readme = readme.replace(old_authoritative, new_authoritative, 1)

old_completion = "Všetkých 17 authoritative kapitol bolo po pôvodnom authoring passe kompletne znovu spracovaných v štyroch prose-first strict blokoch. Každá kapitola má explicitný authority/subject/generation/evidence model, connected incident a vysvetlené positive, recovery, failure alebo forbidden acceptance paths; per-file gates vykazujú nulové critical, high a medium learning-depth findings. Authoritative ordering, celý navigation chain, glossary fragments a incidenty `GITOPS-PAY-61` až `GITOPS-PAY-64` zostávajú zachované. Sekcia je pripravená na používateľskú kontrolu; nie je tým automaticky používateľsky schválená, Accepted, Verified ani Stable."
new_completion = "Všetkých 17 authoritative kapitol bolo po pôvodnom authoring passe znovu spracovaných v štyroch prose-first strict blokoch a teraz prešlo reprodukovateľným authority/subject/evidence/recovery/acceptance gate-om. Každá kapitola obsahuje substantial connected prose a minimálne dva executable Git, Kubernetes, Helm, Argo CD, Flux, portal, policy alebo state-machine examples. Section 16 sa nenachádza v critical/high learning-depth review queue; audit zostáva heuristickým review nástrojom, nie runtime reconciliation alebo platform-product dôkazom. Authoritative ordering, celý navigation chain, glossary fragments a incidenty `GITOPS-PAY-61` až `GITOPS-PAY-64` zostávajú zachované. Sekcia je pripravená na používateľskú kontrolu; nie je tým automaticky používateľsky schválená, Accepted, Verified ani Stable."
if old_completion not in readme and new_completion not in readme:
    raise RuntimeError("Expected Section 16 completion paragraph not found")
readme = readme.replace(old_completion, new_completion, 1)

status_marker = "\n## Stav\n"
if status_marker not in readme:
    raise RuntimeError("Expected legacy Section 16 status table not found")
readme = readme.split(status_marker, 1)[0].rstrip() + "\n\n## Stav\n\nVšetkých **17/17 authoritative kapitol prešlo chapter-by-chapter explanation-depth and practical-example revalidation** a sekcia je `Ready for user review`. Starý per-topic `Learning / L2` status scaffold bol odstránený; readiness sa eviduje na úrovni celej sekcie a v centrálnom review ledgeri. Existujúce Git authority, pull deployment, reconciliation/drift, Argo CD, Flux, promotion, secrets, IDP, platform-product, golden path, self-service, DevEx, catalog, guardrail, tenancy, practical walkthrough a troubleshooting lifecycle-y, incidenty a recovery acceptance zostali zachované. Repository gate overuje textový a executable inventory, navigation, glossary a audit; reálne GitOps controllers, clusters, secret decryption, promotion, platform workflows, tenant isolation a business outcomes neboli týmto documentation workflowom vykonané. Stav preto neznamená používateľské `Accepted`, runtime `Verified` ani produkčné `Stable`.\n"
README.write_text(readme, encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `16-gitops-and-platform-engineering`",
    "| `16-gitops-and-platform-engineering` — GitOps and Platform Engineering | 17/17 chapter-by-chapter explanation-depth and practical-example revalidation | Ready for user review | 2026-08-01 | Všetkých 17 authoritative kapitol bolo znovu preverených podľa exact repository/ref/commit/input/controller/target/capability/tenant subjectu, authority, resolved render, reconciliation, usable outcome, recovery a acceptance boundary. Reprodukovateľný gate potvrdil substantial connected prose, explicitný subject/evidence/recovery/acceptance language a najmenej dva executable Git, Kubernetes, Helm, Argo CD, Flux, portal, policy alebo state-machine examples v každej kapitole. Git-as-source-of-truth a Platform-as-a-Product manuálny read-back potvrdil Git/controller/live generation separation, writer inventory, break-glass reconciliation, exact user segment/job/capability contract, complete adoption funnel a second-journey outcomes; ostatné kapitoly zostali preserve-first bez redundantného prepisu. Legacy per-topic `Learning/L2` tabuľka a zastarané absolútne audit tvrdenie boli odstránené. Section 16 nemá critical ani high learning-depth findings. README, review ledger, navigation, glossary a full audit boli synchronizované. Reálne controllers, clusters, secret/promotion/platform workflows, tenant isolation a business outcomes neboli týmto documentation workflowom vykonané; sekcia je Ready for user review, nie runtime Verified ani používateľsky Accepted. |",
)

print("Section 16 gate passed for 17/17 chapters and legacy Learning/L2 scaffold was removed.")
