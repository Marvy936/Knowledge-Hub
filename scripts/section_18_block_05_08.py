from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "18-machine-learning-fundamentals"
README = SECTION / "README.md"
ROADMAP = ROOT / "ROADMAP.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"

ARTICLES = {
    "train-validation-test-split.md": [
        "training set", "validation set", "test set", "group", "time-based", "cross-validation", "ml-pay-84"
    ],
    "data-preprocessing-normalization-encoding.md": [
        "preprocessing", "standardscaler", "onehotencoder", "missing", "pipeline", "parity", "ml-pay-84"
    ],
    "feature-engineering-feature-selection.md": [
        "feature engineering", "feature selection", "point-in-time", "selectkbest", "rfecv", "freshness", "ml-pay-84"
    ],
    "data-leakage-train-serving-skew.md": [
        "data leakage", "target leakage", "temporal leakage", "train-serving skew", "feature skew", "tfdv", "ml-pay-84"
    ],
}

GROUPS = [
    ("subject", "identity", "generation"),
    ("evidence", "dôkaz", "preukazuje", "read-back", "parity"),
    ("failure", "zlyh", "incident", "root cause", "leakage", "skew"),
    ("recovery", "obnova", "náprava", "rollback", "containment"),
    ("acceptance", "positive", "forbidden", "second-"),
]


def read(path):
    return path.read_text(encoding="utf-8")


def write(path, text):
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def replace_once(text, old, new, label):
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise RuntimeError(f"Missing {label}")


for filename, concepts in ARTICLES.items():
    text = read(SECTION / filename)
    lower = text.lower()
    if len(text.split()) < 1800:
        raise RuntimeError(f"{filename} is too short")
    if text.count("```") < 10:
        raise RuntimeError(f"{filename} lacks model/code surface")
    missing = [item for item in concepts if item not in lower]
    if missing:
        raise RuntimeError(f"{filename} missing concepts: {missing}")
    missing_groups = [group for group in GROUPS if not any(token in lower for token in group)]
    if missing_groups:
        raise RuntimeError(f"{filename} missing semantic groups: {missing_groups}")
    for heading in ("## Kontrolné otázky", "## Glossary impact", "## Primárne zdroje"):
        if heading not in text:
            raise RuntimeError(f"{filename} lacks {heading}")

items = [
    (5, "Train, validation a test split", "train-validation-test-split.md"),
    (6, "Data preprocessing, normalization a encoding", "data-preprocessing-normalization-encoding.md"),
    (7, "Feature engineering a feature selection", "feature-engineering-feature-selection.md"),
    (8, "Data leakage a train-serving skew", "data-leakage-train-serving-skew.md"),
]

readme = read(README)
for number, title, filename in items:
    readme = replace_once(
        readme,
        f"{number}. {title}",
        f"{number}. [{title}]({filename})",
        f"README item {number}",
    )
readme = replace_once(
    readme,
    "Aktuálny authoritative stav sekcie je **4/26 · In progress**. Prvý blok aktivuje spoločný lifecycle od AI-system scope-u cez dataset a learning signal po task formulation. Kapitoly 5–26 zostávajú plánovaným inventorym a nesmú sa interpretovať ako hotová dokumentácia.",
    "Aktuálny authoritative stav sekcie je **8/26 · In progress**. Druhý blok uzatvára evaluation isolation, fitted preprocessing, feature lifecycle a leakage/train-serving parity. Kapitoly 9–26 zostávajú plánovaným inventorym a nesmú sa interpretovať ako hotová dokumentácia.",
    "README status",
)
write(README, readme)

roadmap = read(ROADMAP)
for _, title, filename in items:
    roadmap = replace_once(
        roadmap,
        f"- [ ] {title}",
        f"- [x] [{title}](docs/18-machine-learning-fundamentals/{filename})",
        f"ROADMAP {title}",
    )
write(ROADMAP, roadmap)

ledger = read(LEDGER)
lines = ledger.splitlines()
indexes = [i for i, line in enumerate(lines) if line.startswith("| `18-machine-learning-fundamentals`")]
if len(indexes) != 1:
    raise RuntimeError("Expected one Section 18 ledger row")
lines[indexes[0]] = (
    "| `18-machine-learning-fundamentals` — Machine Learning Fundamentals | 8/26 authoritative drafting | "
    "In progress | 2026-08-02 | Osem authoritative kapitol je aktívnych. Blok 5–8 spája train/validation/test "
    "authority, group/time split a untouched-test boundary; fitted parsing, imputation, scaling, normalization, "
    "categorical encoding a pipeline packaging; point-in-time feature engineering, filter/wrapper/embedded selection, "
    "freshness, lineage a cold-start; a target/temporal/entity/preprocessing/selection leakage so schema, feature, "
    "distribution, transformation a availability train-serving skew. Incident `ML-PAY-84` prepája contaminated "
    "evaluation a cross-language serving mismatch. Kapitoly 9–26 zostávajú plánované. Reálne training, serving a "
    "business actions neboli vykonané. |"
)
write(LEDGER, "\n".join(lines))

if "**8/26 · In progress**" not in read(README):
    raise RuntimeError("Section 18 did not advance to 8/26")
if "9. Linear a logistic regression" not in read(README):
    raise RuntimeError("Planned chapter 9 inventory not preserved")

print("Section 18 block 05-08 passed and advanced to 8/26.")
