from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "18-machine-learning-fundamentals"
README = SECTION / "README.md"
ROADMAP = ROOT / "ROADMAP.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"

ARTICLES = {
    "linear-logistic-regression.md": [
        "ordinary least squares", "logistic regression", "regularization", "calibration", "threshold", "ml-pay-85"
    ],
    "decision-trees-random-forests-gradient-boosting.md": [
        "decision tree", "random forest", "gradient boosting", "out-of-bag", "learning rate", "histogram", "ml-pay-85"
    ],
    "neural-network-fundamentals.md": [
        "dense layer", "activation", "backpropagation", "gradienttape", "dropout", "batch normalization", "ml-pay-85"
    ],
    "loss-functions-optimization.md": [
        "loss function", "cross-entropy", "gradient descent", "learning rate", "adam", "optimizer state", "ml-pay-85"
    ],
}

GROUPS = [
    ("subject", "identity", "generation"),
    ("evidence", "dôkaz", "preukazuje", "read-back", "verdict"),
    ("failure", "zlyh", "incident", "root cause", "non-finite"),
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
    path = SECTION / filename
    if not path.exists():
        raise RuntimeError(f"Missing chapter: {filename}")
    text = read(path)
    lower = text.lower()
    if len(text.split()) < 1800:
        raise RuntimeError(f"{filename} is too short: {len(text.split())}")
    if text.count("```") < 10:
        raise RuntimeError(f"{filename} lacks executable/model surface")
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
    (9, "Linear a logistic regression", "linear-logistic-regression.md"),
    (10, "Decision trees, random forests a gradient boosting", "decision-trees-random-forests-gradient-boosting.md"),
    (11, "Neural network fundamentals", "neural-network-fundamentals.md"),
    (12, "Loss functions a optimization", "loss-functions-optimization.md"),
]

readme = read(README)
for number, title, filename in items:
    readme = replace_once(readme, f"{number}. {title}", f"{number}. [{title}]({filename})", f"README item {number}")
readme = replace_once(
    readme,
    "Aktuálny authoritative stav sekcie je **8/26 · In progress**. Druhý blok uzatvára evaluation isolation, fitted preprocessing, feature lifecycle a leakage/train-serving parity. Kapitoly 9–26 zostávajú plánovaným inventorym a nesmú sa interpretovať ako hotová dokumentácia.",
    "Aktuálny authoritative stav sekcie je **12/26 · In progress**. Tretí blok uzatvára linear/logistic model form, tree ensembles, neural architecture a loss/optimizer lifecycle. Kapitoly 13–26 zostávajú plánovaným inventorym a nesmú sa interpretovať ako hotová dokumentácia.",
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
    "| `18-machine-learning-fundamentals` — Machine Learning Fundamentals | 12/26 authoritative drafting | "
    "In progress | 2026-08-02 | Dvanásť authoritative kapitol je aktívnych. Blok 9–12 spája linear/OLS a logistic "
    "logit/probability/regularization/calibration/threshold boundaries; decision-tree partition, pruning, random-forest "
    "bagging/OOB a stage-wise histogram gradient boosting; neural layer graph, activations, backpropagation, complete "
    "checkpoint, training/inference mode a export; a per-example loss, reduction, regularization, gradients, SGD, "
    "Adam/AdamW, schedules, mixed precision, complete optimizer-state resume a business-metric separation. Incident "
    "`ML-PAY-85` prepája uncontrolled model comparison, incomplete checkpoint a wrong loss/optimizer semantics. Kapitoly "
    "13–26 zostávajú plánované. Reálne training, export, serving a business actions neboli vykonané. |"
)
write(LEDGER, "\n".join(lines))

if "**12/26 · In progress**" not in read(README):
    raise RuntimeError("Section 18 did not advance to 12/26")
if "13. Gradient descent, learning rate a convergence" not in read(README):
    raise RuntimeError("Planned chapter 13 inventory not preserved")

print("Section 18 block 09-12 passed and advanced to 12/26.")
