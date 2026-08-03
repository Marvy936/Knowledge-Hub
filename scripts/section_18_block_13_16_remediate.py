from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "18-machine-learning-fundamentals"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one replacement target, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


replace_once(
    SECTION / "hyperparameters-hyperparameter-optimization.md",
    """## 13. Failure hypotheses

Pri sklamaní searchu treba odlíšiť aspoň tieto hypotézy:

- search space neobsahuje použiteľnú konfiguráciu;
- objective nereprezentuje business outcome;
- split alebo CV porušuje time/entity boundary;
- sampler nemal dostatočný budget;
- pruner odstránil kandidátov príliš skoro;
- trial failures systematicky zasahujú určitú časť space-u;
- parallel scheduler zvýhodňuje krátke trialy;
- selected configuration bola refitovaná iným pipeline contractom;
- validation set bol opakovaným tuningom preťažený;
- apparent gain je seed alebo fold variance.

Každá hypotéza musí predpovedať odlišný evidence pattern. Viac trialov samo osebe nevyrieši zlý objective alebo leakage.
""",
    """## 13. Failure hypotheses

Sklamanie hyperparameter searchu nie je jeden failure mode. Najprv treba určiť, či search skúmal nesprávny priestor, vyhodnocoval nesprávny outcome, spotreboval nedostatočný budget alebo vytvoril skreslenie v scheduling a selection procese. Každá hypotéza musí vysvetliť nielen najlepší trial, ale aj distribution výsledkov, failed/pruned population a rozdiel medzi trial evidence a refit artifactom.

Ak **search space neobsahuje použiteľnú konfiguráciu**, výsledky sa tlačia k boundary hodnotám alebo všetky kandidáty zdieľajú rovnaký limit. Ak **objective nereprezentuje business outcome**, offline optimum zlepšuje optimalizovanú metriku, ale nie capacity-constrained top-K alebo cost-sensitive decision. Ak **split alebo CV porušuje time/entity boundary**, gain sa koncentruje na duplicated entities alebo future windows a mizne na independent holdoute. Tieto tri mechanizmy nevyrieši vyšší počet trialov; treba opraviť search contract alebo evaluation authority.

Ak **sampler nemal dostatočný budget**, promising region zostáva riedko pokrytý a výsledok je citlivý na seed. Ak **pruner odstránil kandidátov príliš skoro**, pruned trials majú pomalší early learning curve, ale pri dlhšom bounded replayi prekonajú selected trial. Ak **trial failures systematicky zasahujú určitú časť space-u**, success-only ranking potichu vylúči drahé, memory-intensive alebo numericky citlivé konfigurácie. Ak **parallel scheduler zvýhodňuje krátke trialy**, completed population nereprezentuje sampled population a wall-clock ordering sa stane hidden selection policy.

Selected configuration môže zlyhať aj po korektnom searchi. **Refit pipeline mismatch** sa prejaví iným preprocessing, sample countom alebo feature schema než v triale. **Validation overuse** vzniká, keď study po každom pozretí výsledku mení space, objective alebo constraints nad tým istým holdoutom; validation sa potom správa ako training signal pre ľudský selection loop. **Seed alebo fold variance** znamená, že apparent gain nie je stabilný naprieč repeatmi a confidence interval zahŕňa baseline. Recovery preto začína trial ledgerom a compatibility read-backom, nie automatickým zvýšením `n_trials`.
""",
)

replace_once(
    SECTION / "overfitting-underfitting-bias-variance.md",
    """## 2. Exact generalization subject

```yaml
""",
    """## 2. Exact generalization subject

Generalization verdict je platný iba pre konkrétnu kombináciu tasku, population, splitu, feature/model procedure, regularization a repeat policy. Manifest nižšie preto nie je administratívny popis experimentu: určuje, ktoré train/validation gaps, cohort výsledky a seed variability možno porovnávať a ktoré patria inej generation. Bez tejto identity sa zmena feature schema alebo campaign population ľahko nesprávne označí ako overfitting modelu.

```yaml
""",
)

replace_once(
    SECTION / "overfitting-underfitting-bias-variance.md",
    """## 11. Approximation, estimation a optimization error

Observed error can be separated conceptually:

- approximation error — model class cannot represent desired function;
- estimation error — finite/noisy data means fitted function differs from best in class;
- optimization error — training failed to find sufficiently good parameters for empirical objective;
- evaluation error — metric/split/implementation does not estimate intended scenario.

Increasing model capacity addresses approximation but may worsen estimation. Training longer addresses optimization, not wrong target/split. This taxonomy prevents random fixes.
""",
    """## 11. Approximation, estimation a optimization error

Observed error vzniká cez viac odlišných mechanizmov a rovnaký nízky validation score preto nemá jednu univerzálnu opravu. **Approximation error** znamená, že zvolená model class ani pri ideálnom fitte nevie reprezentovať potrebný relationship; diagnostický pattern je stabilne podobná systematická chyba naprieč seeds a väčší training dataset ju zásadne nemení. Zvýšenie relevantnej capacity alebo zmena representation môže tento limit znížiť, ale zároveň môže zvýšiť citlivosť na sample.

**Estimation error** vzniká, keď finite alebo noisy training sample vedie k fitted function odlišnej od najlepšej function v model class. Prejavuje sa fold/seed variability, low-support instability a zlepšením pri väčšom reprezentatívnom datasete. **Optimization error** je iný path: objective a model class môžu byť vhodné, ale training nedosiahol dostatočne dobré parameters pre empirical objective. Evidence zahŕňa nezmenšený gradient/update norm, sensitivity na learning-rate trajectory alebo lepší training objective po korektnom pokračovaní.

**Evaluation error** znamená, že metric, split, cohort construction alebo implementation neodhaduje intended production scenario. Vtedy môže byť fitted model technicky dobrý, ale verdict je chybný; príkladom je random split cez rovnakých merchantov alebo top-K business decision hodnotený iba globálnou accuracy. Increasing capacity rieši approximation, viac dát môže znížiť estimation, dlhší alebo stabilnejší training rieši optimization a opravený split/metric rieši evaluation. Táto taxonomy zabraňuje random fixom, ktoré menia nesprávnu vrstvu.
""",
)

replace_once(
    SECTION / "gradient-descent-learning-rate-convergence.md",
    """## 18. Early stopping a checkpoint authority

```python
""",
    """## 18. Early stopping a checkpoint authority

Early stopping premieňa validation sequence na selection rozhodnutie nad konkrétnymi training steps. Authority preto nie je posledná epoch ani callback status, ale presne určený monitored metric, patience/min-delta contract a checkpoint generation, ktorá zodpovedá vybranému stepu. Ak sa obnovia iba weights bez optimizer a schedule state-u, artifact môže byť správny pre inference, ale nie pre exact continuation trainingu.

```python
""",
)

replace_once(
    SECTION / "regularization-early-stopping.md",
    """## 2. Exact regularization subject

```yaml
""",
    """## 2. Exact regularization subject

Regularization subject musí zviazať všetky mechanisms, ktoré menia objective, parameter update, stochastic training graph alebo checkpoint selection. Manifest je authority pre porovnanie experimentov: ak sa zmení decay exclusion, dropout placement alebo stopping metric, vzniká iná training procedure aj vtedy, keď model architecture a numeric strength vyzerajú rovnako. Bez tohto contractu nemožno pripísať gain jednej technike ani reprodukovať recovery.

```yaml
""",
)

print("Applied focused prose remediation for Section 18 chapters 13-16.")
