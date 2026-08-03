#!/usr/bin/env python3
"""Temporary closeout helper for Section 19 chapters 13-16."""

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
    section / "model-validation-promotion-gates.md",
    "## 2. Exact validation subject\n\n```yaml",
    "## 2. Exact validation subject\n\nValidation subject spája všetky authority, ktoré môžu zmeniť verdict. Candidate a baseline určujú porovnávané artifacts, evaluation dataset určuje population a labels, evaluator určuje výpočet a policy určuje rozhodnutie. Ak čo i len jedna z týchto generácií zostane implicitná, rovnaké modely môžu pri ďalšom spustení dostať iný výsledok bez vysvetliteľnej príčiny. Manifest preto nie je administratívny zoznam; je to reprodukčný contract, podľa ktorého sa dajú znovu zostaviť predictions, metrics aj promotion decision.\n\n```yaml",
)

replace_once_or_present(
    section / "batch-online-streaming-inference.md",
    "## 2. Exact inference subject\n\n```yaml",
    "## 2. Exact inference subject\n\nInference subject musí určiť nielen model, ale aj spôsob spracovania observation a hranicu následného side effectu. Batch run vlastní interval a collection, online request vlastní deadline a request identity a streaming path vlastní event, partition a offset. Spoločný release fingerprint následne viaže model, features, runtime a policy. Bez tejto zloženej identity sa rovnaký model digest môže objaviť v troch paths s odlišným input cutoffom, fallbackom alebo retry semantics a ich výsledky sa nedajú korektne porovnať ani reconciliovať.\n\n```yaml",
)

replace_once_or_present(
    section / "shadow-canary-ab-model-deployment.md",
    "## 1. Spoločný deployment lifecycle\n\n```text",
    "## 1. Spoločný deployment lifecycle\n\nVšetky tri patterns zdieľajú technický prechod od immutable release k request exposure, ale rozchádzajú sa pri authority nad action a pri type dôkazu. Shadow zastaví lifecycle pred autoritatívnym side effectom, canary dovolí bounded live action a A/B pridá stable randomization a causal outcome analysis. Preto sa pattern neurčuje iba routing percentom. Najprv sa pomenúva otázka, eligibility population, assignment unit, actual exposure a action boundary; až potom sa vyberie traffic mechanizmus a acceptance verdict.\n\n```text",
)

replace_once_or_present(
    section / "shadow-canary-ab-model-deployment.md",
    "## 2. Exact rollout subject\n\n```yaml",
    "## 2. Exact rollout subject\n\nRollout subject uzatvára všetky generácie, ktoré rozhodujú, kto candidate skutočne uvidí a aký následok môže vzniknúť. Candidate a control release určujú composite behavior, eligibility a assignment určujú population, router určuje actual exposure a guardrail policy určuje, či rollout pokračuje. Samotné číslo 5 % nevysvetľuje request distribution, stable entity assignment ani shared-capacity interference. Manifest preto slúži ako authority pre reprodukciu routing decisionu, exposure denominátorov, rollback targetu a druhého no-op apply.\n\n```yaml",
)

roadmap = ROOT / "ROADMAP.md"
replacements = {
    "- [ ] Continuous Training a retraining triggers":
        "- [x] [Continuous Training a retraining triggers](docs/19-mlops-and-ml-platforms/continuous-training-retraining-triggers.md)",
    "- [ ] Model validation a promotion gates":
        "- [x] [Model validation a promotion gates](docs/19-mlops-and-ml-platforms/model-validation-promotion-gates.md)",
    "- [ ] Batch, online a streaming inference":
        "- [x] [Batch, online a streaming inference](docs/19-mlops-and-ml-platforms/batch-online-streaming-inference.md)",
    "- [ ] Shadow, canary a A/B model deployment":
        "- [x] [Shadow, canary a A/B model deployment](docs/19-mlops-and-ml-platforms/shadow-canary-ab-model-deployment.md)",
}
for old, new in replacements.items():
    replace_once_or_present(roadmap, old, new)

review = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = review.read_text(encoding="utf-8").splitlines()
prefix = "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms |"
new_line = (
    "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms | "
    "16/34 authoritative drafting | In progress | 2026-08-03 | "
    "Štvrtý authoritative blok aktivuje kapitoly 13–16 a incident `MLOPS-PAY-93`. "
    "Continuous Training oddeľuje periodic/event trigger od validated retraining need, data/label readiness, watermark, deduplication, concurrency a candidate-only outcome. "
    "Validation a promotion gates viažu exact candidate/baseline/dataset/evaluator/policy, aggregate aj decision metrics, segment/calibration/robustness/package/runtime evidence, waivers a conditional Registry mutation. "
    "Inference kapitola rozlišuje batch manifests a intervals, online request/deadline/fallback a streaming partition/offset/watermark/idempotency semantics s cross-mode parity. "
    "Shadow/canary/A-B kapitola oddeľuje zero-side-effect live comparison, bounded rollout a causal experiment cez stable assignment, actual exposure, interference, mature outcomes a composite rollback. "
    "Kapitoly 13–16 prešli substantial prose, executable/model surface a subject/evidence/failure/recovery/acceptance gate-om. Reálne triggers, evaluations, inference paths, experiments a business outcomes neboli vykonané; sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
matching = [index for index, line in enumerate(lines) if line.startswith(prefix)]
if len(matching) != 1:
    raise SystemExit(f"DOCUMENTATION-REVIEW-STATUS.md: expected one Section 19 row, found {len(matching)}")
lines[matching[0]] = new_line
review.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

print("Section 19 block 13-16 status files updated.")
