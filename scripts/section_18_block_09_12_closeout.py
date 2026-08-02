from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "18-machine-learning-fundamentals"


def patch(name, old, new, label):
    path = SECTION / name
    text = path.read_text(encoding="utf-8")
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise RuntimeError(f"Missing {label}")
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


patch(
    "linear-logistic-regression.md",
    "## 2. Exact linear-model subject\n\n```yaml",
    """## 2. Exact linear-model subject

Linear-model manifest musí zviazať representation, objective a downstream decision, pretože samotné coefficients nemajú význam bez feature units, preprocessing, regularization a output interpretation. Rovnaký estimator class môže vytvoriť odlišné fitted functions pri zmene scaleru, class weights alebo `C`; rovnaká fitted function môže vytvoriť odlišné business actions pri zmene calibration alebo threshold/ranking policy.

Nasledujúci subject preto oddeľuje, čo optimizer fituje, čo calibration mení a čo application policy vykonáva. Pri incidente umožňuje porovnať requested experiment, final refit, loaded artifact a active queue policy bez zjednodušenia všetkých vrstiev na názov „logistic regression“.

```yaml""",
    "linear subject intro",
)

patch(
    "neural-network-fundamentals.md",
    "## 2. Exact neural model subject\n\n```yaml",
    """## 2. Exact neural model subject

Neural model identity musí pokryť graph aj všetok state, ktorý mení forward alebo training behavior. Architecture určuje tensor transitions, checkpoint nesie trainable a non-trainable layer state, optimizer a global step určujú resume trajectory a export/runtime určujú skutočný inference graph. Názov `nn-v2` ani samotný weights file preto nestačí na reprodukciu alebo rollback.

Nasledujúci subject fixuje input schema, layer graph, initialization, loss, optimizer, batching, seeds, checkpoint a serving export. Tým umožňuje rozlíšiť complete training continuation od weights-only warm startu a training checkpoint od production artifactu, ktorý musí prejsť signature a output-parity read-backom.

```yaml""",
    "neural subject intro",
)

print("Applied focused Section 18 block 09-12 prose closeout.")
