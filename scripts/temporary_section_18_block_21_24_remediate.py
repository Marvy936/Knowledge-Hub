from pathlib import Path

ROOT = Path("docs/18-machine-learning-fundamentals")


def replace_once(filename: str, old: str, new: str) -> None:
    path = ROOT / filename
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{filename}: expected one replacement target, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


replace_once(
    "data-quality-bias-responsible-ai.md",
    """## 3. Data quality ako fitness for purpose

Quality dimensions sa interpretujú voči intended use:

- validity — hodnota spĺňa schema, domain a temporal rules;
- completeness — povinné fields alebo records nechýbajú pre relevantnú population;
- accuracy — measurement zodpovedá intended real-world quantity;
- consistency — rovnaký concept má kompatibilné semantics naprieč sources/time;
- uniqueness — duplicate observations alebo entity aliases sú identifikované;
- timeliness — data boli dostupné pri prediction time a nie až po outcome;
- representativeness — sample pokrýva deployment population a critical cohorts;
- lineage — source, transformation, ownership a mutation sa dajú auditovať.

Stopercentná completeness môže byť zlá, ak missing values boli nepresne imputované a pôvodný missingness signal sa stratil. Syntaktická accuracy timestampu nepreukazuje správny event time. Quality gate preto kombinuje automated constraints s domain validation a outcome-based evidence.""",
    """## 3. Data quality ako fitness for purpose

Quality sa posudzuje voči konkrétnemu prediction a decision lifecycle-u. Rovnaký dataset môže byť dostatočný pre aggregate reporting a neprijateľný pre per-operation automated action, pretože druhý use case potrebuje presnejší event time, vyššiu feature coverage a reprezentatívne critical cohorts. Každá quality dimension preto musí pomenovať failure, ktorý by sa preniesol do features, labels, evaluation alebo policy.

Validity znamená, že hodnota spĺňa schema, domain a temporal rules; validný formát však ešte nepreukazuje správny real-world význam. Completeness sleduje, či povinné fields alebo records nechýbajú v relevantnej population, pričom missingness môže byť samo osebe informatívne a differential medzi cohorts. Accuracy porovnáva measurement s intended quantity alebo autoritatívnym source-om. Consistency vyžaduje kompatibilné semantics naprieč systems a time versions, nie iba rovnaký column name.

Uniqueness odhaľuje duplicate observations a entity aliases, ktoré môžu meniť sample weights alebo preniknúť cez split boundary. Timeliness dokazuje, že feature bola dostupná pri prediction time a nevstúpila až po outcome. Representativeness skúma coverage deployment population a critical intersections. Lineage spája source, transformation, ownera, version a mutation tak, aby sa chybný derived feature dal izolovať a opraviť.

Stopercentná completeness môže byť zlá, ak missing values boli nepresne imputované a pôvodný missingness signal sa stratil. Syntaktická accuracy timestampu nepreukazuje správny event time. Quality gate preto kombinuje automated constraints s domain validation, population funnelom a outcome-based evidence; jeden zelený schema check nemá authority uzavrieť fitness-for-purpose verdict.""",
)

replace_once(
    "data-quality-bias-responsible-ai.md",
    """## 6. Label quality a target validity

Label je operational definition targetu, nie čistá pravda. Dôležité dimensions:

- source authority a adjudication process;
- maturity delay a censoring;
- inter-annotator agreement a guideline version;
- positive/negative/unknown semantics;
- label leakage z post-outcome data;
- differential error medzi cohorts;
- feedback zo starej model policy.

```yaml
label_contract:
  positive: confirmed_recoverable_loss_within_21d
  negative: mature_no_loss_after_21d
  unknown: unresolved_or_unobserved
  adjudication: chargeback_plus_manual_confirmation_v4
  guideline_version: fraud-ops-2026-06
```

Unknown nesmie byť automaticky mapované na negative. Pri delayed outcomes sa evaluation cutoff nastaví tak, aby labels dozreli. Noisy label model môže optimalizovať consistency s chybným processom namiesto intended business conceptu.""",
    """## 6. Label quality a target validity

Label je operational definition targetu, nie čistá pravda. Jeho validity závisí od celého processu, ktorý z latentného real-world outcome-u vytvorí recorded class alebo value. Label audit preto nesleduje iba class counts; rekonštruuje authority, timing, adjudication, unknown state a policy, ktorá rozhodla, ktoré cases vôbec dostali pozorovateľný outcome.

Source authority určuje, či label pochádza z chargebacku, manual confirmation, customer reportu alebo iba heuristiky, a adjudication process rieši konflikty medzi zdrojmi. Maturity delay a censoring určujú, kedy možno outcome považovať za complete; príliš skorý cutoff systematicky označí late positives ako negatives. Inter-annotator agreement a guideline version odhaľujú, či rovnaký case dostáva konzistentný label a či sa definition nezmenila medzi training windows.

Positive, negative a unknown musia mať samostatné semantics. Negative znamená mature evidence o absencii target eventu, nie iba chýbajúci positive record. Label leakage vzniká, keď post-outcome data alebo reviewer decision vstúpi do feature či target generation pred deklarovaným prediction time. Differential error skúma, či measurement alebo adjudication zlyháva častejšie v konkrétnych cohorts. Feedback zo starej model policy sleduje, či labels existujú prevažne pre cases, ktoré predchádzajúci systém vybral na action.

```yaml
label_contract:
  positive: confirmed_recoverable_loss_within_21d
  negative: mature_no_loss_after_21d
  unknown: unresolved_or_unobserved
  adjudication: chargeback_plus_manual_confirmation_v4
  guideline_version: fraud-ops-2026-06
```

Unknown nesmie byť automaticky mapované na negative. Pri delayed outcomes sa evaluation cutoff nastaví tak, aby labels dozreli, a unresolved records zostali viditeľné v denominator lineage. Noisy label model môže optimalizovať consistency s chybným processom namiesto intended business conceptu; preto sa label correction alebo guideline change vydáva ako nová generation a invaliduje dependent evidence podľa scope-u.""",
)

replace_once(
    "data-quality-bias-responsible-ai.md",
    """## 23. Competing failure hypotheses

Responsible-AI incident sa nesmie redukovať na „model bias“. Diagnostika rekonštruuje population funnel, measurement/label process, model predictions, policy actions, human decisions a realized outcomes.

- coverage bias — relevantná population alebo subgroup chýba už v source/sampling frame;""",
    """## 23. Competing failure hypotheses

Responsible-AI incident sa nesmie redukovať na „model bias“. Diagnostika rekonštruuje population funnel, measurement/label process, model predictions, policy actions, human decisions a realized outcomes. Najprv sa určí najskoršia vrstva, v ktorej vzniká rozdiel medzi groups alebo harms: source coverage, measurement, label availability, fitted model, threshold/queue, reviewer action alebo realized impact.

Hypotézy musia predpovedať odlišné evidence patterns. Coverage bias sa prejaví už v počtoch a join-success rates pred inference. Measurement alebo label bias vytvorí rozdiel medzi operational recordom a audit authority. Model underfit sa objaví v predictions pri rovnakom policy contracte, kým queue/workflow disparity vznikne až po score generation. Ak sa gap mení iba pri inom denominator definition, problém je v metric subjecte a nie automaticky v model weights. Pred treatmentom sa preto rozlišujú tieto mechanisms:

- coverage bias — relevantná population alebo subgroup chýba už v source/sampling frame;""",
)

replace_once(
    "explainability-feature-importance.md",
    """## 3. Explanation question a audience

Najprv sa určí, čo má explanation zodpovedať:

- model debugging — ktoré inputs a interactions riadia chyby alebo unexpected behavior;""",
    """## 3. Explanation question a audience

Explanation method sa vyberá až po definovaní rozhodnutia, ktoré má artifact podporiť. Debugger potrebuje fidelity voči model function a prístup k transformed features; reviewer potrebuje actionable evidence a hranice confidence; affected user môže potrebovať policy-approved reason, ktorý vysvetľuje final action, nie interný gradient. Rovnaký chart preto nemožno bez transformácie a validation použiť pre všetky audiences.

Question určuje aj správny output a reference population. Pri performance debugging-u môže byť relevantný raw score a failure cohort, pri threshold incidente calibrated probability a pri notice final rule/queue decision. Audience určuje allowed complexity, terminology, privacy a security exposure. Po tejto definícii sa rozlišujú najmä tieto ciele:

- model debugging — ktoré inputs a interactions riadia chyby alebo unexpected behavior;""",
)

replace_once(
    "explainability-feature-importance.md",
    """## 21. Competing failure hypotheses

Explainability incident sa diagnostikuje cez exact artifact a question. Najprv sa určí, či problém je v model reliance, explainer assumptions, reference data, transformation mapping alebo interpretation/presentation.

- wrong output explained — attribution sa počíta pre raw score, ale prezentuje ako calibrated probability alebo final action;""",
    """## 21. Competing failure hypotheses

Explainability incident sa diagnostikuje cez exact artifact a question. Najprv sa určí, či problém je v model reliance, explainer assumptions, reference data, transformation mapping alebo interpretation/presentation. Reproduction začína rovnakým inputom a model digestom: ak prediction sedí a attribution nie, problém je pravdepodobne v explainer/background generation; ak nesedí už prediction, explanation je iba downstream symptom.

Každá hypotéza musí meniť inú kontrolnú veličinu. Wrong-output explanation sa odhalí porovnaním raw score, calibrated probability a final action. Background mismatch zmení baseline a contributions bez zmeny modelu. Correlated-substitute masking reaguje na grouped permutation alebo ablation, kým off-manifold perturbation sa prejaví invalidnými synthetic combinations. Policy-layer omission zachová model attribution, ale nezodpovedá rule alebo queue reasonu. Pred opravou reportu sa preto rozlišujú tieto mechanisms:

- wrong output explained — attribution sa počíta pre raw score, ale prezentuje ako calibrated probability alebo final action;""",
)

replace_once(
    "reproducibility-random-seeds.md",
    """## 2. Úrovne reproducibility

Reproducibility sa deklaruje podľa use case-u:

- bitwise reproducibility — outputs sú byte-for-byte identické v constrained environment;""",
    """## 2. Úrovne reproducibility

Reproducibility sa deklaruje podľa operation a dôkazu, ktorý treba zopakovať. Forensic checkpoint test môže vyžadovať rovnakú training trajectory v pevnom environment-e, zatiaľ čo model promotion medzi podporovanými GPU generations môže akceptovať malé numerické rozdiely, ak predictions, metrics a business verdict zostanú v tolerancii. Bez tejto voľby tím buď požaduje nemožnú bitwise identitu, alebo príliš voľne označí akýkoľvek podobný výsledok za reproducible.

Úrovne tvoria hierarchy dôkazov, nie navzájom zameniteľné labels. Byte identity je najužšia a najsilnejšie viazaná na platformu. Statistical alebo procedural reproducibility je širšia, ale potrebuje viac runov, explicitnú distribution/tolerance a independent operatora. Contract preto vyberá jednu primárnu úroveň a doplnkové gates:

- bitwise reproducibility — outputs sú byte-for-byte identické v constrained environment;""",
)
