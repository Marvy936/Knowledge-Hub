from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "18-machine-learning-fundamentals"
README = SECTION / "README.md"
ROADMAP = ROOT / "ROADMAP.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"

ARTICLES = {
    "artificial-intelligence-machine-learning-deep-learning-generative-ai.md": {
        "title": "Artificial intelligence, machine learning, deep learning a generative AI",
        "concepts": [
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "generative ai",
            "training",
            "inference",
            "model artifact",
            "ml-pay-83",
        ],
    },
    "dataset-sample-feature-label-target.md": {
        "title": "Dataset, sample, feature, label a target",
        "concepts": [
            "observation unit",
            "prediction time",
            "feature cutoff",
            "point-in-time",
            "label maturity",
            "dataset manifest",
            "ml-pay-83",
        ],
    },
    "supervised-unsupervised-reinforcement-learning.md": {
        "title": "Supervised, unsupervised a reinforcement learning",
        "concepts": [
            "supervised learning",
            "unsupervised learning",
            "reinforcement learning",
            "reward",
            "policy",
            "exploration",
            "ml-pay-83",
        ],
    },
    "regression-classification-ranking-clustering.md": {
        "title": "Regression, classification, ranking a clustering",
        "concepts": [
            "regression",
            "classification",
            "ranking",
            "clustering",
            "pointwise",
            "pairwise",
            "listwise",
            "top-k",
            "ml-pay-83",
        ],
    },
}

SEMANTIC_GROUPS = [
    ("subject", "identity", "generation"),
    ("evidence", "dôkaz", "preukazuje", "potvrdzuje", "read-back"),
    ("failure", "zlyh", "incident", "root cause", "competing"),
    ("recovery", "obnova", "náprava", "rollback", "containment"),
    ("acceptance", "positive", "forbidden", "second-operation", "second-"),
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise RuntimeError(f"Missing {label} anchor")


for filename, spec in ARTICLES.items():
    path = SECTION / filename
    if not path.exists():
        raise RuntimeError(f"Missing ML chapter: {filename}")
    text = read(path)
    lowered = text.lower()
    words = len(text.split())
    fences = text.count("```")
    if words < 1800:
        raise RuntimeError(f"{filename} is unexpectedly short: {words} words")
    if fences < 12:
        raise RuntimeError(f"{filename} lacks executable/model surface: {fences} fences")
    missing = [concept for concept in spec["concepts"] if concept not in lowered]
    if missing:
        raise RuntimeError(f"{filename} is missing required concepts: {missing}")
    missing_groups = [group for group in SEMANTIC_GROUPS if not any(token in lowered for token in group)]
    if missing_groups:
        raise RuntimeError(f"{filename} lacks semantic contract groups: {missing_groups}")
    for required_heading in ("## Kontrolné otázky", "## Glossary impact", "## Primárne zdroje"):
        if required_heading not in text:
            raise RuntimeError(f"{filename} lacks {required_heading}")

readme = read(README)
links = [
    (
        "1. Artificial intelligence, machine learning, deep learning a generative AI",
        "1. [Artificial intelligence, machine learning, deep learning a generative AI](artificial-intelligence-machine-learning-deep-learning-generative-ai.md)",
    ),
    (
        "2. Dataset, sample, feature, label a target",
        "2. [Dataset, sample, feature, label a target](dataset-sample-feature-label-target.md)",
    ),
    (
        "3. Supervised, unsupervised a reinforcement learning",
        "3. [Supervised, unsupervised a reinforcement learning](supervised-unsupervised-reinforcement-learning.md)",
    ),
    (
        "4. Regression, classification, ranking a clustering",
        "4. [Regression, classification, ranking a clustering](regression-classification-ranking-clustering.md)",
    ),
]
for old, new in links:
    readme = replace_once(readme, old, new, f"README topic {old}")
readme = replace_once(
    readme,
    "Aktuálny authoritative stav sekcie je **0/26 · In progress**. Inventory a dependencies sú aktivované; prvé kapitoly ešte nie sú označené ako spracované.",
    "Aktuálny authoritative stav sekcie je **4/26 · In progress**. Prvý blok aktivuje spoločný lifecycle od AI-system scope-u cez dataset a learning signal po task formulation. Kapitoly 5–26 zostávajú plánovaným inventorym a nesmú sa interpretovať ako hotová dokumentácia.",
    "Section 18 status",
)
write(README, readme)

roadmap = read(ROADMAP)
roadmap_links = [
    (
        "- [ ] Artificial intelligence, machine learning, deep learning a generative AI",
        "- [x] [Artificial intelligence, machine learning, deep learning a generative AI](docs/18-machine-learning-fundamentals/artificial-intelligence-machine-learning-deep-learning-generative-ai.md)",
    ),
    (
        "- [ ] Dataset, sample, feature, label a target",
        "- [x] [Dataset, sample, feature, label a target](docs/18-machine-learning-fundamentals/dataset-sample-feature-label-target.md)",
    ),
    (
        "- [ ] Supervised, unsupervised a reinforcement learning",
        "- [x] [Supervised, unsupervised a reinforcement learning](docs/18-machine-learning-fundamentals/supervised-unsupervised-reinforcement-learning.md)",
    ),
    (
        "- [ ] Regression, classification, ranking a clustering",
        "- [x] [Regression, classification, ranking a clustering](docs/18-machine-learning-fundamentals/regression-classification-ranking-clustering.md)",
    ),
]
for old, new in roadmap_links:
    roadmap = replace_once(roadmap, old, new, f"ROADMAP topic {old}")
write(ROADMAP, roadmap)

ledger = read(LEDGER)
lines = ledger.splitlines()
indexes = [i for i, line in enumerate(lines) if line.startswith("| `18-machine-learning-fundamentals`")]
if len(indexes) != 1:
    raise RuntimeError(f"Expected one Section 18 ledger row, found {len(indexes)}")
lines[indexes[0]] = (
    "| `18-machine-learning-fundamentals` — Machine Learning Fundamentals | "
    "4/26 authoritative drafting | In progress | 2026-08-02 | "
    "Prvý authoritative blok zavádza exact AI-system/model/data/task subjects a spája ich incidentom `ML-PAY-83`. "
    "Oddeľuje AI systém od fitted modelu, ML od deep/generative AI, operation-level sample od retry attemptu, "
    "point-in-time feature od future leakage, observed label od target conceptu, supervised/unsupervised/RL learning "
    "signals a regression/classification/ranking/clustering output semantics. Blok používa concrete Python/SQL/YAML "
    "modely, evidence-preserving containment a positive/recovery/forbidden/second-operation acceptance. Kapitoly "
    "5–26 zostávajú plánované. Training, inference, simulator, model serving a business actions neboli týmto "
    "documentation workflowom vykonané. |"
)
write(LEDGER, "\n".join(lines))

# Final read-back after mutation.
updated_readme = read(README)
if "**4/26 · In progress**" not in updated_readme:
    raise RuntimeError("Section 18 README did not advance to 4/26")
for _, linked in links:
    if linked not in updated_readme:
        raise RuntimeError(f"Missing active README link: {linked}")
if "5. Train, validation a test split" not in updated_readme:
    raise RuntimeError("Planned chapter 5 inventory was not preserved")

print("Section 18 block 01-04 gate passed and metadata advanced to 4/26.")
