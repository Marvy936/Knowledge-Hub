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
    "feature-engineering-feature-selection.md",
    "## 2. Exact feature subject\n\n```yaml",
    """## 2. Exact feature subject

Feature manifest rozhoduje, či dve columns s rovnakým názvom reprezentujú tú istú information generation. Spája entity a prediction subject, source authority, time window, availability, missingness, offline/online implementations a ownera. Bez tejto väzby sa nedá preukázať, či model počas trainingu a servingu používal rovnaký measurement alebo iba podobne pomenovaný field.

Nasledujúci subject preto nie je katalóg metadata. Je to contract, podľa ktorého sa feature materializuje, validuje, publikuje a pri incidente porovnáva s loaded online hodnotou. Zmena window boundary, denominatora, late-event policy alebo implementation digestu vytvára successor generation aj pri rovnakom output type.

```yaml""",
    "feature exact-subject introduction",
)

patch(
    "data-leakage-train-serving-skew.md",
    "## 2. Exact leakage a skew subject\n\n```yaml",
    """## 2. Exact leakage a skew subject

Leakage a skew diagnosis potrebuje spojiť dva rozdielne comparison contracts. Prvý porovnáva feature availability a fit domain s intended prediction time a evidence splitom; druhý porovnáva offline a online representation toho istého sample-u. Bez exact modelu, splitu, preprocessing state-u a matched operation identity môže rovnaký symptom viesť k nesprávnej oprave — retrainingu pri implementation skew alebo serving rollbacku pri contaminated trainingu.

Incident manifest preto fixuje artifact generations aj jednu porovnateľnú operation. Preprocessing digest conflict signalizuje rozdielnu loaded transformáciu, zatiaľ čo split a prediction-time fields umožnia samostatne overiť, či training information bola vôbec legitímna. Jeden manifest tak nezamieňa parity verdict s leakage verdictom.

```yaml""",
    "leakage exact-subject introduction",
)

patch(
    "data-leakage-train-serving-skew.md",
    """Atlas model mal štyri vrstvy leakage:

1. Retry/entity leakage cez random row split.
2. Temporal leakage cez current-state chargeback aggregate.
3. Preprocessing leakage cez scaler/encoder fitnutý na all data.
4. Selection/test leakage cez target-based selector a repeated test dashboard.

Serving potom pridal tri skew vrstvy:

1. Amount cents/eur conversion mismatch.
2. Category normalization a unknown handling difference.
3. Offline complete aggregates versus online stale/missing features.
""",
    """Atlas model mal štyri vrstvy leakage, ktoré sa navzájom zosilňovali. Každá vrstva preniesla inú forbidden information: shared entity context, future outcome, test distribution alebo test labels a human feedback. Preto nestačilo odstrániť jednu podozrivú column a znovu spustiť training.

1. Retry/entity leakage — random row split umiestnil attempts rovnakej operation a histories rovnakých merchantov do train aj test, takže model mohol využívať shared identity patterns namiesto generalization na nový decision subject.
2. Temporal leakage — current-state chargeback aggregate obsahoval outcomes a corrections, ktoré pri historical authorization time ešte neexistovali.
3. Preprocessing leakage — scaler a encoder boli fitnuté na all data, čím training transform získal means, variance a vocabulary aj z validation/test population.
4. Selection/test leakage — target-based selector videl all labels a repeated test dashboard viedol engineerov k ďalším feature changes, takže test prestal byť nezávislou acceptance population.

Serving potom pridal tri skew vrstvy. Tie už nemenili, čo sa model naučil, ale menili feature vector, ktorý loaded artifact dostal pre live operation. Vďaka tomu mohol model endpoint úspešne odpovedať a zároveň vykonávať úplne inú numeric function než pri offline evaluation.

1. Amount unit mismatch — jedna route poslala cents do transformácie očakávajúcej euros, takže scaled amount bol rádovo odlišný bez schema alebo shape erroru.
2. Category normalization mismatch — offline path uppercasoval country codes a mal fitted unknown policy, zatiaľ čo online lookup bol case-sensitive a legitimate categories mapoval do unknown bucketu.
3. Availability/freshness mismatch — offline history bola po backfill-e complete, kým online aggregates boli stale alebo missing a fallback ich ticho nahradil ordinary values.
""",
    "expanded ML-PAY-84 mechanisms",
)

print("Applied focused Section 18 block 05-08 prose closeout.")
