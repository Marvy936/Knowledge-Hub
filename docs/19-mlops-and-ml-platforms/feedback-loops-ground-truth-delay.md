# Feedback loops a ground-truth delay

Feedback loop vzniká, keď modelová predikcia ovplyvní action, action ovplyvní budúce dáta a tieto dáta sa neskôr použijú na monitoring alebo retraining. Produkčný dataset preto nie je pasívne pozorovanie sveta. Je čiastočne výsledkom predchádzajúceho modelu, policy, human review a kapacitných obmedzení.

V incidente `MLOPS-PAY-95` boli high-risk transakcie posielané na manuálne review a dostávali rýchly label. Low-risk schválené transakcie získavali fraud label až po chargeback delay alebo nikdy. Monitoring počítal accuracy iba z dostupných labels a candidate vyzeral lepšie, pretože poslal viac prípadov do review. Následný retraining zosilnil túto policy a zmenšil observed population. Root cause nebol iba delayed label, ale action-conditioned selective feedback loop.

## 1. End-to-end feedback lifecycle

Feedback lifecycle musí zachovať prediction, assignment, action, label source, event time, maturity a join identity.

```text
eligible event
→ features
→ prediction
→ policy a action
→ environment/human response
→ provisional signal
→ mature ground truth
→ join a coverage analysis
→ evaluation
→ retraining candidate
```

Každý krok môže meniť population. Model môže rozhodnúť, kto dostane human review, čím ovplyvní pravdepodobnosť získania labelu. Preto sa evaluation dataset nevytvára jednoduchým `WHERE label IS NOT NULL`.

## 2. Exact feedback subject

Feedback record viaže operation ID, entity ID, release, prediction, action policy a label provenance.

```json
{
  "operation_id": "op-4f93",
  "entity_id": "txn-881",
  "event_time": "2026-08-03T09:14:22Z",
  "release_id": "fraud-serving-2026-08-03.4",
  "score": 0.87,
  "action": "manual_review",
  "action_policy": "queue-capacity-v8",
  "label": "fraud",
  "label_source": "chargeback_confirmed",
  "label_event_time": "2026-08-17T11:03:00Z",
  "label_maturity": "final"
}
```

Label definition je versioned contract. `fraud=true` môže znamenať investigator verdict, chargeback alebo confirmed loss. Zmena definície bez novej generation vytvorí apparent concept drift.

## 3. Ground-truth delay a maturity

Ground-truth delay je rozdiel medzi decision eventom a dostupnosťou spoľahlivého labelu. Distribúcia delay môže byť segmentová a action-dependent. Jediný pevný cutoff preto nemusí stačiť.

Maturity policy definuje, kedy sa outcome považuje za dostatočne stabilný. Recent predictions, ktoré ešte nemali čas dostať label, sa nesmú započítať ako negatives alebo missing failures.

```text
prediction at t0
→ provisional review at t0 + 1 h
→ dispute window at t0 + 7 d
→ mature financial outcome at t0 + 30 d
```

Monitoring môže používať viac horizons, ale nesmie ich zamieňať. Early proxy pomáha containmentu; mature outcome rozhoduje dlhodobý verdict.

## 4. Coverage a censoring

Coverage chain rozlišuje expected, observed, valid a joined labels.

```text
eligible predictions
→ labels expected by cutoff
→ labels observed
→ labels valid
→ labels joined
```

Right censoring vzniká, keď recent outcomes ešte nie sú pozorovateľné. Selective labels vznikajú, keď pravdepodobnosť labelu závisí od action alebo prediction. Missing-at-random assumption preto často neplatí.

Report musí segmentovať coverage podľa release, action, score bucket, channel a label source. Vysoká aggregate coverage môže skrývať, že jedna rozhodujúca population labels nemá.

## 5. Human-in-the-loop feedback

Human review nie je automaticky ground truth. Reviewer môže používať model score, explanation alebo front-end ordering, čím vzniká automation bias. Review capacity môže viesť k truncation: spracujú sa iba top cases a zvyšok nedostane verdict.

Audit sample, blind review alebo independent adjudication môže znížiť bias. Reviewer identity sa nemusí používať ako metric label, ale evidence store musí vedieť dohľadať workflow generation, rubric a disagreement.

Human corrections sa nesmú bez validácie okamžite zapisovať do online training setu. Potrebujú provenance, quality gate a ochranu pred duplicate alebo adversarial feedbackom.

## 6. Self-reinforcing loops

Model môže zmeniť svet, ktorý neskôr pozoruje. Recommendation model zvyšuje exposure odporúčaných položiek; fraud model zvyšuje review rizikových prípadov; credit model mení, kto dostane úver a tým aj repayment labels.

```text
prediction
→ exposure/action
→ observed behavior
→ logged label
→ retraining data
→ stronger future prediction
```

Tento loop môže znižovať exploration a skrývať counterfactual outcomes. Random audit sample, holdout policy alebo controlled exploration môže vytvoriť reprezentatívnejší feedback, ale musí rešpektovať safety a právne hranice.

## 7. Proxies a performance estimation

Bez mature labels možno používať proxy metrics alebo estimated performance. Proxy musí mať zdokumentovaný vzťah k outcome a known failure modes. Zmena proxy nie je realized performance.

Estimated performance používa modelové predpoklady a uncertainty. Dashboard musí odlišovať `estimated`, `provisional` a `realized`. Automatický promotion alebo rollback iba podľa estimate je forbidden, pokiaľ risk policy výslovne neurčuje bounded emergency action.

## 8. Join, deduplication a event time

Prediction a label sa spájajú stable identity a event-time pravidlami. Entity môže mať viac predictions a viac outcomes; join preto potrebuje operation alebo decision ID, nie iba customer ID.

Late-arriving labels a corrections sa spracujú idempotentne. Label event má version alebo source sequence. Retraining snapshot určuje watermark a correction policy, aby opakovaný build vytvoril rovnakú population.

```sql
SELECT
  p.operation_id,
  p.release_id,
  p.score,
  a.action,
  l.label,
  l.label_source
FROM predictions p
JOIN actions a USING (operation_id)
LEFT JOIN mature_labels l USING (operation_id)
WHERE p.event_time < :maturity_cutoff;
```

SQL je iba ilustrácia. Authoritative pipeline musí zachovať dataset version, query code a input checksums.

## 9. Monitoring a retraining triggers

Feedback monitoring sleduje label delay distribution, coverage, join success, duplicate/correction rate, action-conditioned propensity a segment performance. Trigger na retraining musí overiť, že dataset je complete a zmena nie je spôsobená label pipeline alebo policy.

Candidate training set obsahuje feedback manifest:

```yaml
snapshot: fraud-feedback-2026-08-01
maturity_cutoff: 30d
label_definition: fraud-loss-v5
coverage_min: 0.92
audit_sample: random-2pct-v3
policy_generations:
  - queue-capacity-v8
  - rules-v6
```

Bez policy generations nemožno vysvetliť, prečo sa observed population zmenila.

## 10. Recovery a acceptance

Pri apparent performance zmene sa najprv overí label freshness, coverage, definition, join a action mix. Containment môže zmraziť retraining, obnoviť label pipeline, oddeliť provisional a mature dashboards alebo vrátiť action policy.

Pozitívna acceptance vyžaduje versioned label contract, maturity cutoff, coverage denominators, action-conditioned segmenty a reprodukovateľný join. Recovery acceptance vyžaduje backfill aj ďalšie prirodzene dozreté window. Forbidden acceptance je accuracy na `label IS NOT NULL`, proxy označená ako truth alebo automatic retraining z nekompletného feedbacku.

Second-operation test zostaví ďalší snapshot rovnakou policy. Ak prvý výsledok vyžadoval ručný backfill alebo nezdokumentované exclusions, feedback loop nie je authoritative.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Performance, latency, throughput a cost monitoring](performance-latency-throughput-cost-monitoring.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Model rollback a recovery →](model-rollback-recovery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
