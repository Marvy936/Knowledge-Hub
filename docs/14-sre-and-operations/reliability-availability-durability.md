# Reliability, availability a durability

Reliability nie je synonymum pre uptime a availability nie je synonymum pre zdravý proces. **Reliability** vyjadruje, či systém počas definovaných podmienok opakovane vykonáva požadovanú funkciu. **Availability** opisuje, či je konkrétna capability použiteľná vtedy, keď vznikne oprávnená potreba. **Durability** opisuje, či už prijatý a potvrdený business state zostane zachovaný alebo reprodukovateľný počas dohodnutého obdobia. Systém môže mať všetky procesy `Running`, prijímať HTTP requesty a napriek tomu byť nespoľahlivý, ak nedokončí business journey, vytvára duplicity alebo stráca potvrdený stav.

Tieto vlastnosti sa majú hodnotiť nad jedným presným subjectom. Bez operation, cohort, generation, acknowledgement boundary a observation pointu sa z „99.99 % availability“ stáva číslo bez reprodukovateľnej semantics. Táto kapitola používa Atlas settlement journey, pri ktorej API prijme merchant intent, atomicky uloží payment a outbox record, publisher pošle command do brokeru, worker vykoná provider operation a reconciler potvrdí final business outcome.

## 1. Dominantný capability-to-recovery model

Reliability vzniká až vtedy, keď sa business expectation preloží na merateľné vlastnosti, runtime ich skutočne presadí a recovery obnoví pôvodný outcome. Diagram preto nie je zoznam komponentov, ale sled od sľubu používateľovi po dôkaz, že systém zvládol aj zlyhanie.

```text
business capability a user expectation
→ exact reliability subject a conditions
→ required function a acknowledgement boundary
→ availability, correctness, latency a durability contracts
→ dependency a failure-domain model
→ runtime operation a authoritative observations
→ impact classification a containment
→ recovery alebo reconciliation
→ original-outcome validation
→ forbidden-path a second-failure validation
```

Každá šípka je samostatná decision boundary. `HTTP 202` môže potvrdiť iba prijatie requestu, PostgreSQL commit môže potvrdiť durable intent a provider ledger môže potvrdiť finálny settlement. Ak tím tieto boundaries zleje do jedného zeleného health checku, nevie odlíšiť dostupné API od dokončenej služby.

## 2. Exact reliability subject

Tvrdenie „payments sú reliable“ sa nedá auditovať ani diagnostikovať. Exact subject musí zachovať identitu operation, používateľského cohortu, release a infrastructure generation, časové okno, požadovaný outcome, dependency scope, acknowledgement semantics a evidence authority.

```text
subject: REL-PAY-52-v2
capability: submit and complete settlement
cohort: valid production merchant requests
release: atlas-settlement-api 7.25.0
region: eu-central-1
operation key: merchant + idempotency key
acknowledgement: HTTP 202 až po payment + outbox commit
completion: provider-confirmed exactly once do 10 minút
durability: acknowledged intent reconstructable 90 dní
window: rolling 28 days
observation: edge + PostgreSQL + broker + provider ledger
```

Ak sa zmení `202` contract, provider, Region, release, retention policy alebo SLI query, mení sa generation analyzovaného subjectu. Priemerná hodnota cez starú a novú generation môže zakryť regresiu rovnako ako priemer cez všetkých tenants môže zakryť úplný výpadok jedného kritického cohortu.

## 3. Reliability ako súbor nekompenzovateľných vlastností

Reliability je širšia než availability. Availability opisuje použiteľnosť capability, correctness pravdivosť výsledku, latency časovú hranicu a durability schopnosť zachovať alebo reprodukovať už potvrdený business state. Pre Atlas settlement journey sa tieto vlastnosti vyhodnocujú samostatne, pretože každá má inú failure boundary a iný authoritative dôkaz.

- **availability** — validný merchant môže operation začať a dostať pravdivý výsledok alebo bezpečný explicitný failure;
- **correctness** — výsledný amount, currency, tenant, provider a workflow transition zodpovedajú business contractu;
- **latency** — acknowledgement aj final completion nastanú v bounded čase;
- **durability** — potvrdený intent a jeho audit lineage sa nestratia ani pri process, storage alebo operator failure;
- **recoverability** — po poruche možno obnoviť nielen bytes, ale aj konzistentný a vykonateľný business state.

Tieto vlastnosti sa nemajú spriemerovať do jedného composite score. Dobrá latency nekompenzuje duplicate settlement a vysoká front-door availability nekompenzuje stratený outbox command. Critical objective má vlastný verdict a môže zablokovať release aj pri zelených ostatných osiach.

## 4. Availability: čas, udalosti a partial cohorts

Time-based availability meria podiel eligible času, počas ktorého je capability použiteľná. Je vhodná pre continuously expected endpoint alebo control plane, ale musí definovať service window, planned-maintenance semantics, observation point a čo presne znamená `usable`.

```text
time availability = usable eligible time / total eligible time
```

Event-based availability meria podiel oprávnených opportunities, ktoré skončili good outcome-om. Pre request-driven služby lepšie zachytáva peak traffic aj partial failures.

```text
event availability = good eligible operations / total eligible operations
```

Denominator je súčasť security a reliability contractu. Malformed request môže byť mimo population, ale rate-limited valid request môže byť skutočný availability failure, ak limit chráni iba nedostatočnú kapacitu. Retries možno merať ako transport attempts aj ako unique business operations; ide o dva odlišné subjecty a nesmú sa nevedomky zameniť.

Availability tiež nie je binárne `up/down`. Atlas môže zlyhávať iba pre jeden tenant, novú release cohortu, konkrétny provider, write path alebo payload class. Globálne `99.99 %` môže zostať zelené, aj keď top-tier merchant nedokáže dokončiť ani jednu operáciu. Každý významný cohort preto potrebuje samostatný denominator alebo explicitný coverage dôkaz.

## 5. Durability a acknowledgement boundary

Durability sa začína otázkou: **čo systém sľúbil v okamihu acknowledgementu?** Pre settlement API je správna hranica:

```text
merchant request
→ validate tenant, amount a idempotency key
→ jedna PostgreSQL transaction:
   payment row + outbox row
→ commit
→ až potom HTTP 202
```

Po tomto bode musí intent prežiť process crash, broker outage aj retry. Stratená response po commite vytvára unknown outcome, nie bezpečný dôvod na novú business operation. Opakovaný request s rovnakým idempotency keyom musí nájsť pôvodný state alebo atomicky pokračovať v tej istej operation identity.

Replication sama osebe durability nedokazuje. Dokáže rýchlo rozmnožiť chybný `DELETE`, corruption alebo malicious mutation. Kompletný durability contract zahŕňa transaction boundary, replicas a logs, retention, soft-delete alebo immutable lineage, backup/restore, encryption-key dependency a business validation po obnove.

```text
acknowledged business intent
→ committed state a execution lineage
→ replicated/journaled copies
→ mutation a retention lifecycle
→ independent recovery lineage
→ reconstructed state
→ application validation
→ business reconciliation
```

Restore, ktorý načíta tabuľky, ale nevie obnoviť chýbajúce provider identifiers alebo consistent outbox state, obnovil bytes, nie službu.

## 6. Dependencies, degraded modes a truthful acknowledgement

End-to-end reliability zahŕňa dependencies, ktoré používateľ nevidí. Ak broker nie je dostupný, API má tri legitímne možnosti: bezpečne prijať durable intent s bounded backlog contractom, prejsť do degraded mode s explicitným stavom, alebo request odmietnuť skôr, než vytvorí nepravdivý acknowledgement. Nemá pokračovať v `202`, ak už nedokáže garantovať uchovanie a neskoršie spracovanie.

Degraded mode musí chrániť business invariant. Read-only status page môže zostať dostupná, kým new settlements sú zastavené. Load shedding môže chrániť recovery capacity, ale validné odmietnuté operations sa stále musia objaviť v availability a business-impact evidence. „Dependency failure“ nie je automatická exclusion, pretože používateľ kupuje end-to-end capability.

## 7. Connected incident `SRE-PAY-52`

Dňa 29. júla 2026 o `08:15 UTC` broker partition zvýšila publish latency. API naďalej atomicky commitovalo payment a outbox rows a vracalo `202`. Front-door dashboard meral iba HTTP responses a ukazoval request availability `99.99 %`.

On-call použil opakovaný recovery runbook:

```text
nájsť outbox rows staršie než 30 minút
→ zvýšiť počet workers
→ pri pretrvávajúcom backloge spustiť cleanup SQL
→ reštartovať publisher
```

Cleanup query filtrovala iba `created_at < now() - interval '30 minutes'`. Nevyžadovala `published_at IS NOT NULL` ani provider/reconciliation proof. O `09:02 UTC` odstránila `4 182` stále nepublikovaných commands. Payment rows zostali, takže API a základné status reads pôsobili zdravo, ale potvrdené settlement intents už neboli vykonateľné.

Incident narušil viac properties naraz. Availability acceptance pathu ostala vysoká. Reliability required function `provider-confirmed exactly once do 10 minút` zlyhala. Business durability zlyhala, pretože po acknowledgement-e zmizla execution lineage. Correctness zlyhala, pretože stav `accepted` predstieral existenciu vykonateľného intentu.

Broker partition bola trigger. Primárny root cause bol nebezpečný cleanup/retention contract, ktorý nerozlišoval published a unpublished commands. Green front-door SLI, privileged manual workflow a chýbajúca reconciliation boli causal amplifiers.

## 8. Diagnostika cez competing hypotheses

Symptóm „accepted settlement sa nedokončil“ môže mať viac príčin: request sa nedostal k API, transaction necommitla, response sa stratila po commite, publisher stojí, broker command existuje bez consumer progressu, provider vykonal operation bez acknowledgementu, projection je stale alebo outbox row bola po commite zmazaná.

Diagnostika preto sleduje jednu operation identity cez observation points:

```text
merchant + idempotency key
→ edge request a response
→ payment/outbox transaction ID
→ WAL alebo CDC history
→ publisher attempt a cursor
→ broker message/offset
→ worker execution
→ provider idempotency ledger
→ projection generation
```

Prítomná payment row, chýbajúca outbox row, nulová broker/provider evidence a PITR snapshot s pôvodným outbox recordom dokazujú post-commit logical deletion. CPU graph alebo počet running Pods túto hypotézu nepotvrdí ani nevyvráti.

## 9. Evidence-preserving containment a recovery

Prvým krokom je zastaviť cleanup job a odobrať mu write capability. API potom musí prestať vytvárať nové nepravdivé acknowledgements alebo prejsť na bounded backpressure. Tím zachová SQL text, actor identity, audit records, WAL/CDC lineage a current payment, outbox, broker a provider snapshots.

Recovery nepoužíva blind replay. Najprv rozdelí operations na completed, pending, unknown a proven-lost cohorts. Chýbajúce outbox commands sa obnovia z isolated PITR do staging table, porovnajú s current payment state a provider ledgerom a až potom sa reinsertujú s pôvodnou operation identity. Provider idempotency key zabráni duplicate external effectu.

Po obnove sa overuje pôvodný business outcome: všetkých `4 182` acknowledged intents je buď provider-confirmed exactly once, alebo má explicitný terminal failure komunikovaný merchantovi. Následne sa vykoná second-failure test s broker outage-om, aby nová retention policy nedokázala zmazať unpublished row.

## 10. Reliability acceptance contract

Acceptance nie je zoznam komponentov, ktoré „sú zelené“. Positive path musí preukázať, že validná operation prejde od requestu po authoritative provider outcome v bounded čase a že acknowledgement nastane až po durable transaction boundary. Recovery path musí preukázať reconstructability z nezávislej lineage.

Forbidden paths musia zlyhať kontrolovane. Systém nesmie potvrdiť intent bez payment/outbox commitu, nesmie publishnúť dve provider operations pre jeden idempotency key, nesmie odstrániť unpublished command, nesmie označiť stale projection za final a nesmie považovať restore bez business reconciliation za recovery.

```text
positive:
valid operation → durable ack → exactly-once completion → correct projection

recovery:
logical deletion → isolated restore → reconciliation → original outcome

forbidden:
ack without durable intent
duplicate provider effect
silent lost intent
stale status as final truth
old unsafe cleanup generation
```

Acceptance verdict patrí exact release, configuration, retention-policy a recovery generation. Druhý release alebo druhý Region potrebuje vlastný test; úspech jedného subjectu sa neprenáša automaticky.

## 11. Troubleshooting model

Pri reliability incidente začni user-visible capability a exact operation cohortou, nie infraštruktúrnym grafom. Urči acknowledgement, required final outcome a časovú hranicu. Potom sleduj durable state a async lineage, porovnaj competing hypotheses a zachovaj evidence pred mutation.

```text
symptom a affected cohort
→ exact operation/release/time
→ acknowledged promise
→ authoritative state identities
→ dependency a async lineage
→ competing hypotheses
→ discriminating evidence
→ containment
→ recovery/reconciliation
→ original + forbidden outcome validation
```

Ak front-door SLI vyzerá zdravo, neuzatváraj incident. Môže iba dokazovať, že jedna skorá boundary funguje.

## 12. Anti-patterny

Nasledujúce skratky zamieňajú čiastkový technický signal za celý reliability outcome. Každá z nich odstráni dôležitú boundary z merania alebo recovery, a preto môže vytvoriť zelený verdict počas reálneho user impactu.

- **Uptime equals reliability —** Running proces alebo úspešný health check nepreukazuje correctness, durability ani final business completion. Zelený process signal musí byť korelovaný s operation-level outcome-om.
- **Replication equals backup —** Replication zvyšuje availability a odolnosť voči physical failure-u, ale replikuje aj chybnú mutation. Recovery potrebuje oddelenú lineage, restore test a business reconciliation.
- **`202` znamená, že sa o to systém postará —** `202` je sľub iba v rozsahu server-side contractu. Bez durable intentu, status identity a bounded completion/failure semantics je acknowledgement nepravdivý.
- **Globálny priemer —** Aggregate availability môže skryť úplný failure kritického tenant-a, Regionu alebo release cohorty. Critical cohorts preto potrebujú vlastný denominator a verdict.
- **Recovery overená počtom rows —** Technický row count nepreukazuje referential, workflow ani provider consistency. Validácia musí skončiť pôvodným business outcome-om a forbidden duplicate/lost paths.

## 13. Kontrolné otázky

1. Čo tvorí exact reliability subject?
2. Prečo reliability nie je synonymum availability?
3. Kedy je vhodnejšia time-based a kedy event-based availability?
4. Ako denominator mení SLI semantics?
5. Prečo `202` musí nasledovať až po presnej durable boundary?
6. Prečo replication nechráni pred logical deletion?
7. Čo odlišuje restore bytes od business recovery?
8. Ako partial cohort failure zostane skrytý v globálnom priemere?
9. Ktoré evidence odlíši lost response od lost committed intentu?
10. Prečo broker partition nebola root cause `SRE-PAY-52`?
11. Ktoré forbidden paths musí acceptance test odmietnuť?
12. Prečo je potrebný second-failure test?

## Glossary impact

Relevantné pojmy: reliability subject, required function, stated conditions, event-based availability, time-based availability, partial availability, acknowledgement boundary, business durability, execution lineage, reconstructability, reliability acceptance contract, forbidden reliability path a second-failure validation.

## Primárne zdroje

- [Google SRE — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google SRE — Embracing Risk](https://sre.google/sre-book/embracing-risk/)
- [Google SRE — Availability Table](https://sre.google/sre-book/availability-table/)
- [Google SRE — Data Integrity](https://sre.google/sre-book/data-integrity/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Zero Trust](../13-security-and-identity/zero-trust.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: SLI, SLO a SLA →](sli-slo-sla.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
