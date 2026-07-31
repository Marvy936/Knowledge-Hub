# Well-Architected Framework

AWS Well-Architected Framework je opakovateľný model na vyhodnocovanie architektonických rozhodnutí a ich rizík. Nie je to certifikát workloadu, automatický scanner ani checklist, ktorý z existencie AWS resource-u odvodí bezpečnosť, spoľahlivosť alebo pripravenosť na obnovu. Framework dáva tímu spoločný jazyk a otázky; dôkaz o skutočnom stave musí stále vzniknúť z exact workload generation, runtime observations, failure experimentov a business výsledkov.

Review má preto zmysel iba ako uzavretý rozhodovací lifecycle:

```text
business outcome a constraints
→ exact workload/review subject
→ current evidence inventory a cut-off
→ applicable question a best-practice interpretation
→ evidence-backed answer
→ causal failure scenario a risk
→ owned improvement alebo expiring acceptance
→ bounded implementation
→ effective-state a business validation
→ residual-risk verdict
→ immutable milestone a re-review trigger
```

Zaškrtnutá odpoveď bez evidence nie je control. Vytvorený ticket nie je odstránený risk. Milestone je historický snapshot review state-u, nie dôkaz, že produkcia zostala odvtedy nezmenená.

## Exact workload a review subject

Celá AWS sekcia používa payment capability `CAP-PAY-42`. Well-Architected review nad ňou má subject `WA-PAY-42`. Business outcome je autorizovať, settle-nuť a zaúčtovať payment presne raz, s mesačnou availability 99,95 %, p99 do 750 ms, RTO dve hodiny a ledger RPO pätnásť minút.

Samotný názov workloadu nestačí. Review generation `WA-PAY-2026-07-R3` je viazaná na production accounts, Regions, application release `payments-api 7.18.0`, Lambda settlement release `5.4.0`, databázový subject `DB-PAY-42`, schema generation `SCHEMA-215`, recovery contract `REC-PAY-42`, IaC commit `INFRA-64` a evidence cut-off `2026-07-28T12:00:00Z`. Keď sa po review zmení retry policy, target-group routing, KMS key, RTO, account boundary alebo provider contract, dotknuté answers sú stale aj vtedy, keď workload ID a posledný milestone zostali rovnaké.

Workload boundary je business capability, nie iba AWS diagram. Zahŕňa clientov, DNS a edge cestu, application a event processing, databázy a queues, externého payment providera, identity a secrets, delivery pipeline, observability, incident response, backup, reconciliation aj ľudí s rozhodovacou právomocou. Komponent vlastnený iným tímom alebo vendorom je dependency s failure contractom; nie je automaticky `not applicable`.

Praktický versionovaný review manifest môže vyzerať takto:

```yaml
review:
  id: WA-PAY-2026-07-R3
  workloadId: WA-PAY-42
  evidenceCutoff: "2026-07-28T12:00:00Z"
  frameworkLens: wellarchitected
  applicationRelease: payments-api-7.18.0
  schemaGeneration: SCHEMA-215
  infrastructureCommit: INFRA-64

businessOutcome:
  operation: authorize-and-settle-payment
  availabilityMonthly: 99.95
  latencyP99Ms: 750
  rtoMinutes: 120
  ledgerRpoMinutes: 15

evidence:
  architecture: ARCH-31
  deployedState: DEPLOY-64
  sliDashboard: OBS-19
  cloudTrailWindow: EVID-42
  failoverDrill: FD-12
  restoreTest: RT-PAY-6
  costReport: FIN-PAY-42

forbiddenOutcomes:
  - configured resource accepted as an effective control
  - stale milestone accepted as current production truth
  - external provider excluded from the workload boundary
  - risk closed only because a ticket exists
  - accepted risk without owner, expiry, and review trigger
```

Tento YAML nie je AWS WA Tool import format. Je to repository authority, ktorá určuje, čo presne sa reviewuje a aké evidence musia answers referencovať. AWS WA Tool potom drží review state a milestone history; runtime, IaC, incident a business evidence zostávajú vo svojich authoritative systémoch.

## Od otázky k evidence-backed answer

Framework používa šesť pilierov: operational excellence, security, reliability, performance efficiency, cost optimization a sustainability. Nie sú to oddelené checklisty. Každý pillar skúma inú vlastnosť toho istého business outcome-u a zmena v jednom často mení riziko v ďalších.

| Pillar | Hlavná otázka | Dôkaz, ktorý nestačí | Silnejší dôkaz |
|---|---|---|---|
| Operational Excellence | Vieme workload bezpečne meniť, pozorovať a prevádzkovať? | existujúci runbook | vykonaný runbook nad current topology s ownerom, výsledkom a recovery |
| Security | Kto môže vykonať akú operáciu a ako zistíme zneužitie? | policy JSON | effective allow/deny test, CloudTrail evidence, revocation a second-session test |
| Reliability | Dokáže business operation prežiť failure alebo sa korektne obnoviť? | `MultiAZ=true` | failover test cez client, transaction, provider side effect a reconciliation |
| Performance Efficiency | Spĺňa resource model latency a throughput pri reálnom demand-e? | priemerné CPU | representative workload, p95/p99, queue age, saturation a scaling delay |
| Cost Optimization | Mení spend na business value bez poškodenia iných outcomes? | recommendation accepted | normalized unit cost po bounded zmene so SLO a security guardrails |
| Sustainability | Minimalizuje systém zbytočnú spotrebu na užitočný outcome? | odstránená idle capacity | demand-matched capacity so zachovaným recovery headroomom |

Answer musí rozlišovať applicability a evidence quality. `Applicable and implemented` znamená, že konkrétna best practice má relevantný mechanismus a current evidence. `Partially implemented` znamená, že control pokrýva iba časť subjectu alebo generation. `Not applicable` potrebuje explicitné vysvetlenie, prečo failure scenario nevzniká. Ak evidence chýba alebo je stale, správny verdict je `unknown`, nie optimistické `yes`.

Silný risk statement je kauzálny. Namiesto „zlepšiť reliability“ má vysvetliť trigger, mechanismus a outcome:

```text
Pretože payments-api po strate database acknowledgement-u retryuje
provider authorization bez reconciliation podľa business idempotency key,
môže RDS failover po durable commit-e vytvoriť druhú autorizáciu,
hoci databáza aj Multi-AZ control fungujú podľa infraštruktúrneho contractu.
```

Takýto statement sa dá overiť experimentom, priradiť ownerovi a uzavrieť konkrétnym acceptance oracle. Vágna položka sa nedá spoľahlivo prioritizovať ani dokázať ako vyriešená.

## Praktický AWS CLI walkthrough

Nasledujúci walkthrough ukazuje rozdiel medzi review state-om a effective workload state-om. Používa AWS CLI v2, exact Region a 32-znakový workload ID. Well-Architected workload ID je regionálny subject, preto je `--region` súčasťou identity operácie.

```bash
export AWS_REGION=eu-central-1
export WA_WORKLOAD_ID=0123456789abcdef0123456789abcdef
export WA_LENS=wellarchitected

aws sts get-caller-identity

aws wellarchitected get-workload \
  --region "$AWS_REGION" \
  --workload-id "$WA_WORKLOAD_ID" \
  --query 'Workload.{
    Name:WorkloadName,
    Owner:ReviewOwner,
    Environment:Environment,
    Regions:AwsRegions,
    UpdatedAt:UpdatedAt,
    Lenses:Lenses
  }' \
  --output yaml
```

`get-caller-identity` fixuje principal a account, z ktorého sa review číta. `get-workload` potom vracia workload metadata z konkrétneho Regionu. Úspešný call dokazuje API authorization a existenciu workload recordu. Nedokazuje, že metadata opisujú current production release alebo že answers majú čerstvé evidence.

Reliability answers sa načítajú samostatne:

```bash
aws wellarchitected list-answers \
  --region "$AWS_REGION" \
  --workload-id "$WA_WORKLOAD_ID" \
  --lens-alias "$WA_LENS" \
  --pillar-id reliability \
  --query 'AnswerSummaries[].{
    QuestionId:QuestionId,
    Title:QuestionTitle,
    Risk:Risk,
    SelectedChoices:SelectedChoices
  }' \
  --output table
```

Výstup poskytne current question IDs, selected choices a vypočítaný risk. IDs sa nemajú hardcodovať z cudzieho workloadu alebo starého exportu. Z outputu sa vyberie exact question a jej detail sa prečíta pred mutation:

```bash
export WA_QUESTION_ID=REL10

aws wellarchitected get-answer \
  --region "$AWS_REGION" \
  --workload-id "$WA_WORKLOAD_ID" \
  --lens-alias "$WA_LENS" \
  --question-id "$WA_QUESTION_ID" \
  --query 'Answer.{
    QuestionId:QuestionId,
    Title:QuestionTitle,
    Risk:Risk,
    SelectedChoices:SelectedChoices,
    Notes:Notes,
    IsApplicable:IsApplicable
  }' \
  --output yaml
```

`REL10` je v príklade placeholder; reálna hodnota musí pochádzať z current `list-answers` outputu. Rovnako sa z `get-answer` vyberú valid choice IDs. Update sa vykoná cez explicitný JSON artefakt, aby shell quoting nezmenil notes alebo array:

```json
{
  "WorkloadId": "0123456789abcdef0123456789abcdef",
  "LensAlias": "wellarchitected",
  "QuestionId": "REL10",
  "SelectedChoices": ["CHOICE_ID_FROM_GET_ANSWER"],
  "IsApplicable": true,
  "Notes": "WA-PAY-2026-07-R3; evidence FD-12 and RT-PAY-6. Multi-AZ is configured. Unknown-commit reconciliation test is still missing, therefore the control is not accepted as fully effective."
}
```

```bash
aws wellarchitected update-answer \
  --region "$AWS_REGION" \
  --cli-input-json file://wa-answer.json
```

`update-answer` mení review record. Nezapína Multi-AZ, neopravuje retry contract a nevykonáva failover test. Preto musí nasledovať API read-back a potom nezávislé overenie linked evidence:

```bash
aws wellarchitected get-answer \
  --region "$AWS_REGION" \
  --workload-id "$WA_WORKLOAD_ID" \
  --lens-alias "$WA_LENS" \
  --question-id "$WA_QUESTION_ID" \
  --query 'Answer.{
    Risk:Risk,
    SelectedChoices:SelectedChoices,
    Notes:Notes,
    UpdatedAt:UpdatedAt
  }' \
  --output yaml

test -f evidence/FD-12/failover-result.json
jq -e '
  .businessOutcome == "accepted" and
  .duplicateAuthorizations == 0 and
  .reconciliationSecondPassChanges == 0
' evidence/FD-12/failover-result.json
```

Prvý read-back potvrdzuje uloženú answer generation. Druhý príkaz kontroluje evidence artefakt vytvorený failure experimentom. Ak JSON neexistuje alebo business assertions neprejdú, answer nesmie byť interpretovaná ako effective reliability control.

Milestone sa vytvorí až po dokončení review alebo validated improvement bloku:

```bash
aws wellarchitected create-milestone \
  --region "$AWS_REGION" \
  --workload-id "$WA_WORKLOAD_ID" \
  --milestone-name "WA-PAY-2026-07-R3 validated failover"

aws wellarchitected list-milestones \
  --region "$AWS_REGION" \
  --workload-id "$WA_WORKLOAD_ID" \
  --query 'MilestoneSummaries[].{
    Number:MilestoneNumber,
    Name:MilestoneName,
    RecordedAt:RecordedAt
  }' \
  --output table
```

Milestone je immutable comparison point. Jeho vznik dokazuje uloženie review snapshotu, nie continued compliance produkcie. Ďalší release alebo zmena failure contractu musí vytvoriť nový review subject a revalidation.

## Worked failure: Multi-AZ screenshot uzavrel nesprávny risk

Review `WA-PAY-2026-06-R2` označil reliability otázku ako splnenú, pretože RDS mala Multi-AZ, AWS Backup jobs boli green, application používala retry library a runbook prikazoval request zopakovať po reconnecte. Evidence tvoril console screenshot a architecture diagram. Diagram končil pri database commit-e; payment provider a unknown-outcome boundary v ňom neboli.

Po RDS failover-e payment `P-884` prešiel týmto pathom:

```text
provider authorization succeeded
→ database transaction a outbox durable commit
→ connection lost before application acknowledgement
→ client classified operation as failed
→ retry repeated provider authorization
→ duplicate external business side effect
```

Infrastructure control fungoval. RDS endpoint sa presmeroval a databáza bola dostupná. Business reliability zlyhala, pretože retry mechanismus nerozlišoval confirmed failure od unknown outcome.

Competing hypotheses zahŕňali neskorší production drift, stale evidence, nesprávny workload boundary, chybné pochopenie question, netestovaný retry contract a vedome accepted risk. Review history ukázala, že retry konfigurácia bola rovnaká už v čase review, provider nebol v evidence inventory, failover drill neexistoval a ticket na idempotency nemal ownera ani risk link. Root cause teda nebol drift. Bol to evidence-free inference: tím zamenil infrastructure redundancy za end-to-end reliability.

Containment zastavil blind retries a obmedzil settlement consumers. Incident tím zachoval database, application, provider a CloudTrail evidence, reconcilioval ledger podľa payment identity a duplicate authorization voidol podľa business runbooku. Recovery zaviedla provider idempotency key, transactional outbox a reconciliation pred opakovaním unknown operation.

Review-system recovery znovu otvorila HRI, rozšírila workload boundary o provider a client retry, nahradila screenshot failure experimentom a vytvorila owned improvement contract. Risk sa môže uzavrieť až keď production-equivalent failover experiment preukáže presne jeden provider aj ledger outcome, nulovú duplicate authorization a druhý reconciliation pass bez zmeny.

## Improvement, acceptance a continuous review

Improvement item je bounded change contract, nie iba názov iniciatívy. Musí viazať exact risk na target state, ownera, dependencies, safety model, acceptance oracle, forbidden outcomes a evidence location.

```yaml
riskId: WA-PAY-REL-17
subject: WA-PAY-2026-07-R3
failure: duplicate-provider-authorization-after-unknown-commit
owner: atlas-payments
change:
  - provider-idempotency-key-bound-to-payment-id
  - reconcile-before-retry
  - transactional-outbox
validation:
  positive: exactly-one-provider-and-ledger-outcome
  recovery: failover-between-commit-and-acknowledgement
  forbidden: duplicate-authorization
  secondOperation: reconciliation-second-pass-is-no-op
evidence: evidence/FD-12/failover-result.json
```

Risk acceptance je odlišná operácia. Ak zmena zatiaľ nie je možná, accountable approver musí poznať exact residual scenario, compensating controls, expiry a re-review trigger. Acceptance bez expiry sa mení na neviditeľný permanentný design.

Continuous Well-Architected spája architecture decision, deployment evidence, SLO a security observations, failure drills, improvement backlog a milestone history. Re-review spúšťa nový Region alebo account, major release, data migration, zmena SLO/RTO/RPO, security incident, neúspešný restore, významná zmena demandu alebo costu, expirácia accepted risku či zmena AWS capability alebo support contractu.

Positive acceptance znamená, že current workload generation má evidence-backed answers a business outcome prešiel. Recovery acceptance znamená, že konkrétny failure bol vyvolaný alebo vierohodne simulovaný, recovery prešla v objective a dáta aj external side effects boli reconciliované. Forbidden acceptance overuje, že nevznikol duplicate payment, unauthorized access, stale rollback subject alebo iný explicitne zakázaný výsledok. Second-operation test preukazuje, že opakované reconcile, review update alebo recovery nevytvorí ďalší side effect.

## Kontrolné otázky

1. Prečo workload boundary nemôže skončiť na AWS resource diagrame?
2. Ktoré generation identities robia review answer aktuálnou alebo stale?
3. Čo presne dokazuje `update-answer` a čo nedokazuje?
4. Prečo je `unknown` bezpečnejší verdict než unsupported `implemented`?
5. Ako sa configured control zmení na effective control?
6. Ktoré evidence rozlišujú RDS failover od business exactly-once recovery?
7. Prečo ticket ani milestone samy osebe neuzatvárajú risk?
8. Ako musí cross-pillar optimization chrániť reliability, security a business value?
9. Kedy je risk acceptance legitímna a kedy je iba odložený neviditeľný failure?
10. Aký second-operation test by si použil pri reconciliation alebo review update?

## Glossary impact

Relevantné pojmy: workload-review subject, evidence cut-off, applicability verdict, configured control, effective control, causal risk statement, improvement contract, expiring risk acceptance, milestone generation, review-staleness trigger, cross-pillar decision, positive acceptance, recovery acceptance, forbidden acceptance a second-operation validation.

## Oficiálna dokumentácia

- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
- [The pillars of the framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/the-pillars-of-the-framework.html)
- [AWS Well-Architected Tool](https://docs.aws.amazon.com/wellarchitected/latest/userguide/waf.html)
- [Using lenses](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses.html)
- [Milestones](https://docs.aws.amazon.com/wellarchitected/latest/userguide/milestones.html)
- [Implement and track improvements](https://docs.aws.amazon.com/wellarchitected/latest/userguide/implement-and-track-improvements.html)
- [AWS CLI: get-workload](https://docs.aws.amazon.com/cli/latest/reference/wellarchitected/get-workload.html)
- [AWS CLI: list-answers](https://docs.aws.amazon.com/cli/latest/reference/wellarchitected/list-answers.html)
- [AWS CLI: update-answer](https://docs.aws.amazon.com/cli/latest/reference/wellarchitected/update-answer.html)
- [AWS CLI: create-milestone](https://docs.aws.amazon.com/cli/latest/reference/wellarchitected/create-milestone.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: AWS Backup](aws-backup.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Cost management a FinOps →](cost-management-finops.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
