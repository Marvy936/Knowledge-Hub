# A/B testing

A/B testing porovnáva súbežné variants na kontrolovane priradených populations a snaží sa odhadnúť kauzálny dopad treatmentu na vopred definovaný outcome. Traffic split vytvára dve skupiny, ale dôveryhodný experiment vznikne až vtedy, keď assignment, exposure, measurement a decision contract umožnia rozlíšiť treatment effect od selection biasu, interference, novelty alebo chyby merania.

A/B experiment nie je primárne release-safety mechanizmus. Canary sa pýta, či nový release nespôsobuje neprijateľnú regresiu. A/B test sa pýta, či konkrétny treatment spôsobuje zmenu business outcome-u. Jeden rollout môže používať oba modely, no ich hypotheses, samples a verdicty sa nesmú zlúčiť.

## 1. Dominantný hypothesis-to-decision model

```text
kauzálna hypotéza a decision owner
→ exact control a treatment generations
→ eligibility a randomization unit
→ stable assignment a exposure logging
→ guardrails a primary outcome
→ sample-size a duration contract
→ valid observations a quality checks
→ effect estimate a uncertainty
→ ship, stop, iterate alebo inconclusive decision
→ cleanup a long-term validation
```

Experiment musí byť navrhnutý pred čítaním výsledkov. Dodatočná zmena primary metric, cohorty alebo duration podľa priaznivého grafu zvyšuje false-positive risk.

## 2. Exact experiment subject

```yaml
experimentSubject:
  id: EXP-PAY-204
  hypothesis: simplified-review-page increases completed settlements without increasing approval errors
  owner: payments-product
  control:
    release: payments-10.0.0
    featureGeneration: review-page-v1
  treatment:
    release: payments-10.0.0
    featureGeneration: review-page-v2
  eligibility:
    regions: [eu-central]
    accountTypes: [standard, enterprise]
    excluded: [regulatory-critical, support-intervention]
  assignment:
    unit: account_id
    saltGeneration: exp-pay-204-v1
    allocation: {control: 50, treatment: 50}
  primaryOutcome: settlement_completion_within_10m
  guardrails:
    - duplicate_provider_effects
    - approval_reversal_rate
    - support_contacts_per_1000_accounts
  minimumDuration: 14d
  minimumAccountsPerVariant: 20000
```

Control a treatment môžu používať rovnaký artifact a odlišný feature generation. Experiment identity preto nie je iba release version. Eligibility a assignment generation musia zostať stabilné počas measurement window-u.

## 3. Randomization unit a stable assignment

Randomization unit má zodpovedať nezávislej causal unit. Per-request assignment je nevhodný, ak jeden account vykoná viac súvisiacich steps alebo sa users navzájom ovplyvňujú.

```python
import hashlib

def variant(account_id: str, salt: str) -> str:
    value = int.from_bytes(hashlib.sha256(f"{salt}:{account_id}".encode()).digest()[:8], "big")
    return "treatment" if value % 100 < 50 else "control"
```

Function preukazuje deterministic split pre rovnaké inputs. Nepreukazuje správnu eligibility, balanced covariates ani to, že všetky services používajú rovnaký salt. Assignment event sa má uložiť s experiment a variant generation.

## 4. Exposure versus assignment

Assigned user nemusí treatment skutočne vidieť. Page sa nemusí načítať, flag evaluation môže failnúť alebo user journey skončí skôr. Analysis má rozlišovať:

```text
eligible
→ assigned
→ exposed
→ outcome observed
```

Intent-to-treat analysis zachová randomization a hodnotí assigned groups. Per-protocol analysis podľa actual exposure môže byť biased, pretože exposure súvisí s behaviorom. Experiment contract má vopred určiť primary analysis.

## 5. Instrumentation a authoritative denominator

Každý outcome potrebuje stable event semantics a correlation identity. HTTP page render nie je settlement completion. Atlas používa authoritative settlement table a exposure events.

Príklad SQL kontroly populations:

```sql
SELECT variant,
       COUNT(DISTINCT account_id) AS accounts,
       COUNT(*) FILTER (WHERE exposed_at IS NOT NULL) AS exposures,
       COUNT(*) FILTER (WHERE completed_within_10m) AS completions
FROM experiment_assignments
WHERE experiment_id = 'EXP-PAY-204'
GROUP BY variant;
```

Query preukazuje rows v konkrétnej database snapshot-e a definitions v columns. Nepreukazuje absence duplicate assignments, event-loss ani correct `completed_within_10m` derivation. Data-quality checks musia testovať one-assignment-per-unit, sample-ratio mismatch a freshness.

## 6. Sample-ratio mismatch

Pri 50/50 allocation má veľká odchýlka naznačovať assignment, eligibility alebo logging defect. Nejde automaticky o treatment effect.

```python
from scipy.stats import chisquare
observed = [19850, 21190]
expected = [sum(observed)/2, sum(observed)/2]
print(chisquare(observed, expected))
```

P-value pomáha detegovať mismatch za assumptions testu. Nepreukazuje príčinu ani validitu experimentu. Root cause môže byť flag outage, bot filtering, caching alebo treatment-specific logging loss.

## 7. Metrics, guardrails a multiplicity

Primary metric odpovedá na hypothesis. Guardrails chránia safety a quality. Diagnostic metrics pomáhajú vysvetliť mechanism. Ak tím skúša desiatky metrics a vyberie najlepší result, false discovery rastie.

Outcome má definovaný numerator, denominator, time horizon a attribution. Revenue per exposed account sa správa inak než conversion per session. Heavy-tailed metrics môžu vyžadovať robust methods alebo pre-aggregation.

## 8. Duration, novelty a seasonality

Experiment má trvať dostatočne dlho na traffic cycle, delayed outcomes a repeat behavior. Stop pri prvom nominally significant výsledku mení error rate, ak sequential testing nie je vopred navrhnuté.

Deployment alebo incident počas experimentu môže ovplyvniť iba jeden variant. Experiment log má zachovať release, routing, flag, data-pipeline a dependency generations počas celého window-u.

## 9. Interference a contamination

Users môžu zdieľať organization, support agent, inventory alebo provider quota. Treatment jednej unit ovplyvní control outcome. Vtedy randomization unit môže byť account group, tenant alebo Region. Shared caches a sessions môžu variant contamination spôsobiť aj technicky.

A/A test s identickým behaviorom môže overiť assignment, logging a analysis pipeline. Nepreukazuje však treatment-specific instrumentation paths.

## 10. Decision a rollout

Statistical evidence nie je automatické ship rozhodnutie. Decision kombinuje effect size, uncertainty, guardrails, operational cost, segment heterogeneity a strategic value. Výsledok môže byť:

```text
SHIP
STOP_HARM
ITERATE
INCONCLUSIVE
SEGMENTED_ROLLOUT
```

Po ship-e sa treatment stane novým defaultom cez versionovaný flag/release transition. Experiment artifacts a stale branches sa odstránia; inak permanentná experiment complexity zvyšuje risk.

## Doplnenie výkladu: experiment, randomizácia a kauzálny výsledok

A/B test je experiment určený na odhad kauzálneho vplyvu variantu na outcome. Nie je to iba rollout na dve verzie.

Najprv sa definuje hypotéza, primary metric, guardrails a **unit of assignment**. Unit môže byť user, tenant alebo session. Musí zodpovedať tomu, kde vzniká interference a opakované správanie.

Randomizácia vytvára porovnateľné skupiny v priemere. Assignment sa má uložiť stabilne; per-request randomization mieša experience a porušuje assumptions.

**Sample Ratio Mismatch** znamená, že observed počet participants v A/B sa významne líši od očakávaného pomeru. Môže signalizovať chybu assignmentu, filtering alebo telemetry loss a diskvalifikuje causal interpretation.

Primary metric sa vyberá pred experimentom. Hľadanie ľubovoľnej zlepšenej metriky po výsledkoch zvyšuje false discoveries. Guardrails chránia napríklad error rate, latency, fraud alebo support contacts.

Statistical significance neznamená praktickú významnosť. Malý efekt pri obrovskom sample môže byť štatisticky presný, ale business bezvýznamný. Report uvádza effect size a interval neistoty.

A/B test neslúži ako jediný safety gate. Variant musí prejsť technickými controls pred experimentom. Experiment rozhoduje o value, nie o základnej correctness alebo security.

## 11. Connected incident `REL-PAY-70`

Atlas testoval nový settlement review flow. Assignment sa vykonával per HTTP request a experiment dashboard počítal conversion iba z requests s exposure eventom. Treatment JavaScript error zabránil časti users emitovať exposure, takže failed journeys zmizli z denominatora.

```text
per-request assignment
→ jeden account miešal control/treatment
→ treatment failures bez exposure eventu
→ biased exposed-only analysis
→ reported uplift +6.4 %
→ full rollout
```

Authoritative account-level completion po rolloute klesla o 3.1 %. Support contacts vzrástli 18 %. Sample-ratio check neexistoval a primary metric sa počas experimentu zmenila z account completion na exposed-session conversion.

Root cause bol experiment contract, nie iba frontend bug.

## 12. Redesign a acceptance verdict

Redesign používa stable account assignment, immutable metric definition, intent-to-treat primary analysis, authoritative outcome records, SRM gate a predeclared guardrails. Experiment changes vytvárajú novú generation a resetujú decision window.

A/B test je prijatý iba vtedy, keď:

```text
hypothesis a decision sú predeclared
+ control/treatment generations sú exact
+ randomization unit zodpovedá interference modelu
+ assignment je stable a logged
+ exposure a outcome sa nezlievajú
+ denominator zahŕňa relevantné failures
+ SRM/data-quality checks prejdú
+ duration/sample contract je splnený
+ guardrails a uncertainty sú vyhodnotené
+ second-segment a post-ship validation prejdú
```

## 13. Troubleshooting flow

```text
hypothesis/subject
→ eligibility
→ assignment implementation
→ exposure logging
→ outcome authority
→ data quality/SRM
→ analysis population
→ metric calculation
→ decision and subsequent rollout
```

Competing hypotheses môžu byť assignment drift, contamination, missing exposure, delayed outcome, bot/filter difference, treatment-specific instrumentation, seasonality alebo actual effect. Dashboard uplift bez raw assignment/outcome evidence nie je dostatočný.

## 14. Anti-patterny

### Traffic split ako celý experiment

Bez causal hypothesis, stable assignment a measurement contract ide iba o rozdelenie trafficu.

### Exposed-only analysis bez bias modelu

Exposure môže byť ovplyvnená treatmentom a vylúčiť failures.

### Zmena primary metric po výsledkoch

Decision sa potom prispôsobuje data, nie vopred definovanej otázke.

### Stop pri prvom zelenom grafe

Ignoruje sequential testing, cycles a delayed outcomes.

### Experiment flag ponechaný navždy

Stale variants a code paths vytvárajú runtime a testing debt.

## 15. Kontrolné otázky

1. Čím sa A/B test odlišuje od canary?
2. Čo tvorí exact experiment subject?
3. Ako sa volí randomization unit?
4. Aký je rozdiel medzi assignment a exposure?
5. Prečo exposed-only analysis môže byť biased?
6. Čo deteguje sample-ratio mismatch?
7. Ako sa definujú primary metric a guardrails?
8. Prečo duration nie je iba dosiahnutie p-value?
9. Ako interference mení design?
10. Čo sa pokazilo v `REL-PAY-70`?
11. Ako sa treatment po decision-e bezpečne shipne?
12. Čo musí overiť post-ship validation?

## Glossary impact

Relevantné pojmy: A/B testing, causal hypothesis, control, treatment, randomization unit, stable assignment, eligibility, exposure, intent-to-treat, per-protocol analysis, sample-ratio mismatch, guardrail metric, interference, contamination, A/A test, effect size a experiment cleanup.

## Primárne zdroje

- [Trustworthy Online Controlled Experiments](https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/)
- [Microsoft ExP Platform](https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/)
- [OpenFeature specification](https://openfeature.dev/specification/)
- [SciPy — Statistical tests](https://docs.scipy.org/doc/scipy/reference/stats.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Canary deployment](canary-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Shadow deployment →](shadow-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
