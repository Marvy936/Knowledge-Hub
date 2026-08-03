#!/usr/bin/env python3
"""Temporary closeout helper for final Section 19 chapters 33-34."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once_or_present(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{path.relative_to(ROOT)}: expected one replacement target, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


section = ROOT / "docs/19-mlops-and-ml-platforms"
replace_once_or_present(
    section / "mlops-platform-architecture.md",
    """## 2. Domény a bounded contexts

Praktická platforma sa rozdeľuje na bounded contexts s jasným ownershipom:

- source a CI authority,
- data a feature authority,
- pipeline a training orchestration,
- tracking, artifact a Registry authority,
- evaluation a governance,
- release a deployment control,
- online, batch a streaming inference,
- observability, feedback a cost,
- security, privacy a supply chain,
- backup, recovery a retirement.

Hranica nie je iba organizačná. Každý context vlastní konkrétne objects a nesmie implicitne prepisovať authority iného contextu. Registry napríklad eviduje candidate/version a promotion control, ale serving platforma vlastní loaded runtime a traffic. Feature store vlastní feature definitions a values, nie business label.
""",
    """## 2. Domény a bounded contexts

Praktická platforma sa rozdeľuje na bounded contexts podľa authority, ktorú musí každý tím vlastniť a vedieť obnoviť. Source a CI context vlastní reviewed code, build definition a provenance; data a feature context vlastní snapshoty, schemas, event-time hranice, feature definitions a materialization state. Pipeline a training context vlastní orchestration operation, task attempts, distributed topology a checkpoint lifecycle, zatiaľ čo tracking, artifact a Registry context vlastní experiment metadata, immutable bytes, candidate versions a promotion pointers.

Evaluation a governance context rozhoduje nad presne označeným evidence bundle-om a nesmie meniť model artifacts. Release a deployment context skladá schválené generácie do composite release a vlastní rollout, routing a rollback intent. Online, batch a streaming inference context vlastní runtime execution a side-effect semantics; observability, feedback a cost context vlastní meranie actual exposure, result classes, label maturity a useful-work denominators.

Security, privacy a supply-chain context presadzuje identity, integrity, minimization a trust policies naprieč ostatnými doménami. Backup, recovery a retirement context vlastní obnoviteľnosť authoritative stores, poradie restore a bezpečné ukončenie modelu aj jeho dátových a prevádzkových závislostí. Tieto hranice nie sú iba organizačné: každý context vlastní konkrétne objects a nesmie implicitne prepisovať authority iného contextu. Registry napríklad eviduje candidate/version a promotion control, ale serving platforma vlastní loaded runtime a traffic. Feature store vlastní feature definitions a values, nie business label.
""",
)

replace_once_or_present(
    section / "mlops-troubleshooting.md",
    """## 4. Evidence preservation a change freeze

Pred restartom, retry alebo rollbackom sa zachytí:

- source a release manifest,
- API objects vrátane generations a conditions,
- task/job attempts a events,
- Pod specs, images, node/device assignment,
- logs a traces s time range,
- artifact manifests a digests,
- cache hit/miss evidence,
- monitoring query a denominator,
- external side-effect state.

Change freeze neznamená úplné zastavenie businessu. Znamená zákaz nekorelovaných mutations. Emergency containment sa loguje ako nová operation s jasným subjectom.
""",
    """## 4. Evidence preservation a change freeze

Pred restartom, retry alebo rollbackom sa vytvorí evidence bundle, ktorý zachováva každú vrstvu state ladderu. Source commit a release manifest ukazujú intended generation. API objects vrátane `generation`, `observedGeneration`, conditions a resolved specs dokazujú configured a controller-resolved stav. Task a job attempts, Kubernetes events, Pod specs, image digests a node/device assignment vysvetľujú, čo orchestrátor skutočne spustil a kde.

Logs a traces sa ukladajú s presným time rangeom, clock contextom a release identity, aby sa dali spojiť s requestmi a attempts. Artifact manifests, object versions a digests dokazujú, aké bytes vznikli alebo boli načítané; cache hit/miss evidence vysvetľuje, či sa výpočet vykonal alebo znovu použil starší output. Monitoring query sa archivuje spolu s filtrom, denominatorom, samplingom a dashboard transformáciou, pretože samotný screenshot neumožňuje reprodukciu alarmu. External side-effect state sa číta priamo z Registry, deployment targetu, databázy alebo queue, aby timeout nebol nesprávne interpretovaný ako neúspech.

Change freeze neznamená úplné zastavenie businessu. Znamená zákaz nekorelovaných mutations, ktoré by zmenili viac hypotheses naraz alebo prepísali dôkaz. Emergency containment sa loguje ako nová operation s jasným subjectom, actorom, dôvodom a expected effectom.
""",
)

section_readme = section / "README.md"
text = section_readme.read_text(encoding="utf-8")
active_anchor = "32. [Amazon SageMaker a cloud MLOps mapping](amazon-sagemaker-cloud-mlops-mapping.md)"
active_final = (
    active_anchor
    + "\n33. [MLOps platform architecture](mlops-platform-architecture.md)"
    + "\n34. [MLOps troubleshooting](mlops-troubleshooting.md)"
)
if active_final not in text:
    if text.count(active_anchor) != 1:
        raise SystemExit("Section README: active chapter 32 anchor is not unique")
    text = text.replace(active_anchor, active_final, 1)

planned_start = "\n## Plánované authoritative poradie\n"
authoring_start = "\n## Authoring a evidence štandard\n"
if planned_start in text:
    before, remainder = text.split(planned_start, 1)
    if authoring_start not in remainder:
        raise SystemExit("Section README: authoring section missing after planned inventory")
    _, after = remainder.split(authoring_start, 1)
    text = before + authoring_start + after

lines = text.splitlines()
status_prefix = "Aktuálny authoritative stav sekcie je **"
status_line = (
    "Aktuálny authoritative stav sekcie je **34/34 · Ready for user review**. "
    "Deviaty a záverečný authoritative blok uzatvára sekciu incidentom `MLOPS-PAY-98`. "
    "Platform architecture kapitola spája business capabilities, bounded contexts, control a data planes, authoritative stores, immutable release manifest, event identities, tenancy a trust zones, paved roads, build/train/serve planes, cross-platform lineage, observability, governance, DR a platform SLO do jedného implementačného modelu. "
    "Troubleshooting kapitola používa jednotný intended → configured → resolved → loaded → exercised → outcome ladder, evidence preservation, read-before-retry, cross-system timeline, competing hypotheses a first-divergence analysis naprieč pipelines, distributed trainingom, artifacts/Registry, features, servingom, monitoringom, feedbackom, security a cost/capacity. "
    "Všetkých 34 kapitol sekcie má authoritative prose-first obsah a synchronizovaný repository evidence model. Dokumentačné kontroly nepreukazujú vykonanie reálnych pipelines, training jobs, serving trafficu, restores ani mature business outcomes; sekcia je preto `Ready for user review`, nie runtime `Verified`, production `Stable` ani user `Accepted`."
)
matching = [index for index, line in enumerate(lines) if line.startswith(status_prefix)]
if len(matching) != 1:
    raise SystemExit(f"Section README: expected one status paragraph, found {len(matching)}")
lines[matching[0]] = status_line
section_readme.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

roadmap = ROOT / "ROADMAP.md"
replace_once_or_present(
    roadmap,
    "- [ ] MLOps platform architecture",
    "- [x] [MLOps platform architecture](docs/19-mlops-and-ml-platforms/mlops-platform-architecture.md)",
)
replace_once_or_present(
    roadmap,
    "- [ ] MLOps troubleshooting",
    "- [x] [MLOps troubleshooting](docs/19-mlops-and-ml-platforms/mlops-troubleshooting.md)",
)

review = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
review_lines = review.read_text(encoding="utf-8").splitlines()
prefix = "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms |"
new_line = (
    "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms | "
    "34/34 authoritative drafting | Ready for user review | 2026-08-03 | "
    "Záverečný authoritative blok aktivuje kapitoly 33–34 a incident `MLOPS-PAY-98`. "
    "Platform architecture kapitola definuje capabilities a bounded contexts, control/data planes, authoritative stores, immutable cross-platform release manifest, event/idempotency contracts, workload identity, trust zones, paved roads, build/train/serve planes, lineage, feedback, governance, backup/DR, hybrid build-versus-buy rozhodovanie a platform SLO. "
    "Troubleshooting kapitola zavádza exact incident subject, intended/configured/resolved/loaded/exercised/outcome ladder, evidence freeze, unknown-outcome read-before-retry, subsystem-specific hypotheses, unified timeline, controlled experiments, containment/recovery/correction, read-only runbooks a second-operation acceptance. "
    "Všetkých 34 kapitol sekcie je authoritative a prešlo repository prose/executable/subject/evidence/failure/recovery/acceptance kontrolami. Reálne MLOps platform operations, restore/failover drilly a business outcomes neboli vykonané; stav je `Ready for user review`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
indices = [index for index, line in enumerate(review_lines) if line.startswith(prefix)]
if len(indices) != 1:
    raise SystemExit(
        f"DOCUMENTATION-REVIEW-STATUS.md: expected one Section 19 row, found {len(indices)}"
    )
review_lines[indices[0]] = new_line
review.write_text("\n".join(review_lines) + "\n", encoding="utf-8", newline="\n")

print("Section 19 final block status files updated.")
