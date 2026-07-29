# Root cause analysis

Root cause analysis (RCA) je systematické vysvetlenie, **prečo konkrétny nežiaduci outcome vznikol, prečo ho existujúce kontroly nezastavili, prečo dosiahol daný impact a čo musí byť zmenené, aby sa rovnaký failure mechanismus neopakoval**.

RCA nie je hľadanie jednej osoby, posledného commitu ani prvého chybného log riadku. V komplexnom systéme incident zvyčajne vzniká z kombinácie triggera, technického mechanismu, latentných podmienok, neúplných kontrol a recovery constraints.

```text
incident alebo reliability failure
→ exact analysis subject a evidence cutoff
→ overená timeline a state transitions
→ trigger a proximate mechanism
→ contributing conditions a latent controls
→ competing causal hypotheses
→ causal graph a counterfactual tests
→ root, escape, amplification a recovery causes
→ corrective-action portfolio
→ recurrence a second-operation validation
```

## 1. Exact RCA subject

Tvrdenie `analyzujeme incident` je príliš široké. RCA subject musí uviesť:

- incident ID;
- affected business capability;
- presný service, data a operation scope;
- release, configuration a policy generations;
- affected tenant, Region, cluster alebo cohort;
- impact interval;
- evidence cutoff;
- known-good a first-known-bad state;
- ownera analýzy;
- explicitne vylúčený scope.

Príklad:

```text
incident: SRE-PAY-54
capability: merchant settlement reconciliation
release: payments-api 7.25.0
job: settlement-ledger-compactor generation 54
scope: production EU, all merchant tenants
first bad mutation: 2026-07-29 02:14:07 UTC
impact: active settlements označené ako archived
analysis cutoff: 2026-07-29 12:00 UTC
excluded: provider-side settlement calculation
```

Bez subject identity sa môžu zmiešať dve nezávislé poruchy alebo sa neskoršia recovery action nesprávne označí za pôvodnú príčinu.

## 2. Outcome pred príčinou

Analýza začína presným nežiaducim outcome-om:

```text
actor alebo user
+ intended operation
+ expected state transition
+ observed state transition
+ business impact
```

V `SRE-PAY-54` nebol outcome `database mala problém`. Presný outcome bol:

```text
aktívne settlement rows
→ mali zostať queryable a correlatable
→ compactor ich označil ako archived
→ odstránil provider/outbox correlation metadata
→ provider callbacks sa nedali bezpečne priradiť
→ merchant stav zostal stale alebo unknown
```

System health bez správneho business state-u nie je úspech.

## 3. Timeline ako model state transitions

Timeline nie je chronologický dump všetkých logs. Zachytáva kauzálne významné transitions:

| Čas UTC | Subject | Transition | Dôkaz |
|---|---|---|---|
| 02:02 | release 7.25.0 | deployed → ready | deployment a readiness evidence |
| 02:10 | compactor config 54 | loaded s missing `tenant_scope` | config read-back |
| 02:14:07 | batch 54-1 | eligible query → wildcard scope | query plan a job log |
| 02:14:12 | settlement ledger | 186 420 rows → archived | WAL/audit |
| 02:15–02:31 | replicas/backups | current corruption → replicated/captured | replication a snapshot evidence |
| 02:33 | provider callbacks | normal → correlation failures | callback logs |
| 02:37 | business SLI | completion correctness fast burn | SLI evaluation |
| 02:41 | incident | detected → declared | incident log |
| 02:48 | compactor | active → disabled | controller audit |

Každý bod potrebuje time authority a subject. Application timestamp, database commit time, provider time a incident-chat time nemusia byť identické.

## 4. Trigger, mechanismus a impact

### Trigger

Udalosť, ktorá aktivovala failure path. V incidente to bol prvý production run compactoru po release `7.25.0`.

### Proximate mechanismus

Bezprostredný technický mechanismus:

```text
missing tenant_scope
→ query generator použil wildcard semantics
→ destructive batch zahrnul všetkých tenantov
→ active rows prešli do archived state-u
```

### Impact mechanismus

Ako sa lokálna chyba zmenila na user impact:

```text
archived state
→ correlation metadata odstránené
→ callback nemožno priradiť
→ final settlement state nemožno bezpečne potvrdiť
→ stale/unknown merchant outcome
```

Trigger nie je automaticky root cause. Rovnaký release by nevyvolal incident, keby destructive operation fail-closed odmietla missing scope.

## 5. Viac druhov príčin

Užitočná RCA rozlišuje:

### Technical root cause

Mechanismus, bez ktorého by incident nevznikol. Tu: missing scope sa v destructive query interpretoval ako wildcard.

### Systemic root cause

Design alebo governance podmienka umožňujúca mechanismu existovať. Tu: destructive batch contract nemal mandatory exact scope, affected manifest, maximum row count ani invariant gate.

### Escape cause

Prečo defect neodhalili testy, review alebo rollout. Canary dataset nemal žiadne eligible rows a test overoval iba successful job exit.

### Detection cause

Prečo incident nebol zistený skôr. Monitoring sledoval DB errors a job success, nie active-to-archived transition rate ani callback-correlation correctness.

### Amplification cause

Čo zväčšilo blast radius. Unbounded batch, broad DB role a multi-tenant scope umožnili 186 420 mutations v jednom run-e.

### Recovery-delay cause

Čo predĺžilo obnovu. Restore plan nebol rehearsed po zmene encryption/account grants a neexistoval manifest consistency groupu medzi database, outbox, broker a provider ledgerom.

Jedna veta `root cause bol bug` je preto neúplná.

## 6. Causal graph

Causal graph spája podmienky a transitions:

```text
release 7.25.0
        |
        v
missing tenant_scope ----> wildcard default
                               |
missing fail-closed schema ----+
                               v
                      broad destructive query
                       /       |         \
              no max rows   broad role   zero-row canary
                       \       |         /
                               v
                     186 420 rows archived
                               |
              correlation metadata removed
                               |
                   callback mapping failure
                               |
                stale/unknown merchant state
```

Graph ukazuje, ktoré podmienky sú necessary, sufficient alebo iba amplifying. Zároveň bráni tomu, aby sa posledný človek v chain-e stal falošným vysvetlením celého systému.

## 7. Competing hypotheses

RCA nesmie spätne predstierať, že správna odpoveď bola od začiatku zrejmá. Zaznamenaj relevantné hypotézy:

| Hypotéza | Očakávaný dôkaz | Pozorovanie | Verdict |
|---|---|---|---|
| provider poslal poškodené callbacks | invalid provider payload pred DB mutation | payloads boli validné | zamietnutá |
| replica lag vrátil stale row | failures iba na replica reads | failures aj na primary | zamietnutá |
| compactor broad-archived rows | batch IDs korelujú s mutations | WAL a audit sa zhodujú | potvrdená |
| manual operator query | interactive actor v audit logu | actor bol workload identity | zamietnutá |

Rejected hypotheses sú hodnotné. Ukazujú, ktoré evidence paths boli použité a zabraňujú opakovaniu slepých diagnostických ciest.

## 8. Counterfactual reasoning

Counterfactual otázka skúma, či by odstránenie podmienky zmenilo outcome:

```text
Keby tenant_scope bol mandatory a fail-closed,
spustil by sa broad batch?
→ nie

Keby canary obsahovala eligible active rows a invariant check,
prešiel by release gate?
→ nie

Keby existoval max_rows=500,
dosiahol by incident rovnaký blast radius?
→ nie

Keby snapshot fungoval bez business reconciliation,
bol by user outcome bezpečne obnovený?
→ nie
```

Counterfactual nie je matematický dôkaz kauzality, ale disciplinuje tvrdenia a oddeľuje príčinu od korelácie.

## 9. Five Whys a jeho hranice

`Five Whys` môže pomôcť rozvinúť jednoduchý lineárny chain, ale má limity:

- počet päť nie je technický zákon;
- otázky môžu byť vedené k preferovanému záveru;
- distributed incident má viac paralelných vetiev;
- môže skončiť abstraktným `human error`;
- nemusí zachytiť escape, detection a recovery causes;
- môže ignorovať organizáciu a incentives.

Použi ho ako prompt, nie ako jedinú RCA metódu. Pre komplexný incident kombinuj timeline, causal graph, change analysis, barrier analysis, fault tree alebo STPA-style control reasoning podľa potreby.

## 10. Root-cause depth

Analýza má ísť dostatočne hlboko na actionable a controllable mechanismus.

Príliš plytké:

```text
engineer zabudol tenant parameter
```

Príliš abstraktné:

```text
komplexné systémy zlyhávajú
```

Actionable depth:

```text
destructive production operation prijala missing scope,
pretože schema povoľovala optional field,
runtime použil wildcard default,
policy nekontrolovala affected manifest
a canary neobsahovala positive eligible population
```

Osobné rozhodnutie môže byť súčasťou timeline, ale RCA sa pýta, prečo systém považoval dané rozhodnutie za bezpečné a povolené.

## 11. Human action bez human blame

Blameless neznamená, že ľudské actions sa vynechajú. Znamená, že sa opisujú fakticky:

```text
responder spustil RB-PAY-17
pretože alert odkazoval na tento runbook,
dokument bol označený current
a queue-length panel krátkodobo ukazoval zlepšenie
```

Namiesto:

```text
responder bezhlavo spustil zlý príkaz
```

Ak existuje úmyselné porušenie policy, podvod alebo hrubé zanedbanie, patrí do príslušného people/compliance procesu. Technická RCA stále analyzuje, ako systém takú akciu detegoval, obmedzil alebo neobmedzil.

## 12. Evidence quality

Každé závažné tvrdenie má mať:

- source;
- subject;
- timestamp a clock authority;
- generation/version;
- completeness;
- retention status;
- confidence;
- known limitations.

Preferuj authoritative evidence:

```text
DB WAL/transaction audit
> parsed application log
> dashboard aggregation
> incident-chat recollection
```

Hierarchia nie je absolútna. WAL potvrdí mutation, ale nie user-visible interpretáciu. Business outcome môže vyžadovať provider ledger a customer-facing state.

## 13. Worked incident `SRE-PAY-54`

Release `payments-api 7.25.0` pridal `settlement-ledger-compactor`. Intended operation bola:

```text
exact tenant
+ terminal settlement
+ provider finalized
+ age > 90 dní
→ archive correlation metadata
```

Production config vynechala `tenant_scope`. Config schema pole povoľovala a query generator použil:

```text
missing scope → all tenants
```

Canary dataset neobsahoval žiadne eligible rows. Test preto dostal `0 rows affected`, job skončil s exit code `0` a rollout gate ho označil za successful.

Prvý production batch o `02:14:07 UTC`:

- vybral `186 420` rows;
- z toho `7 842` nebolo terminal;
- odstránil provider/outbox correlation metadata;
- `613` neskorších provider callbacks sa nedalo priradiť bez secondary evidence;
- `91` merchant-visible settlements zostalo dočasne stale alebo unknown;
- database replication a nové snapshots faithfully zachytili poškodený logical state.

### Causal verdict

Trigger:

```text
prvý production run compactor generation 54
```

Technical root cause:

```text
missing tenant scope sa pre destructive operation interpretoval ako wildcard
```

Systemic root cause:

```text
chýbal fail-closed destructive-operation contract:
mandatory scope, affected manifest, max rows/rate,
dual authorization a business invariant gate
```

Escape cause:

```text
zero-row canary + exit-code oracle
bez positive mutation population a forbidden-state assertion
```

Amplifiers:

- broad production role;
- unbounded multi-tenant batch;
- detection až cez downstream correlation failures;
- replicas a backups kopírujúce logical corruption;
- neúplný consistency-group inventory.

Recovery delay:

- restore identity nemala current decryption grant;
- isolated restore nebol rehearsed po account migration;
- post-clean-point provider operations vyžadovali manuálne zostavený manifest.

## 14. Containment pred analýzou

RCA nesmie blokovať urgentné containment. Zároveň containment zachová evidence:

1. disable compactor generation 54;
2. revoke jeho write capability;
3. preserve config, query text, plan, actor, WAL a affected IDs;
4. block ďalšie archive/delete jobs;
5. snapshot current corrupted state pre forensic comparison;
6. preserve provider callbacks a broker/outbox evidence;
7. classify merchant impact;
8. nezačať broad production rollback bez clean-point a divergence analýzy.

Editovanie jobu alebo runbooku in-place pred preservation môže zničiť generation evidence.

## 15. Corrective-action portfolio

Silné corrective actions pokrývajú viac control layers:

### Eliminate mechanism

- `tenant_scope` mandatory v schema;
- missing/empty scope fail-closed;
- typed destructive-operation API bez wildcard defaultu.

### Limit blast radius

- exact affected manifest;
- max rows a rate;
- per-tenant batches;
- automatic abort pri invariant breach.

### Improve detection

- active-to-archived transition SLI;
- callback-correlation correctness;
- unexpected multi-tenant mutation alert;
- business canary s positive eligible population.

### Improve recovery

- versionovaný consistency-group inventory;
- tested isolated PITR;
- current decryption/access canary;
- provider-ledger reconciliation tooling.

### Improve organization

- destructive-change review owner;
- postmortem action SLO;
- cross-service review podobných wildcard semantics.

`Buďte opatrnejší` nie je dostatočná corrective action.

## 16. Action-item quality

Každý action item potrebuje:

```text
failure mechanism
→ concrete control
→ owner
→ priority
→ due date
→ dependency
→ verification evidence
→ retirement alebo residual-risk verdict
```

Príklad:

```text
Action: ARCH-219
Mechanism: missing scope → wildcard destructive query
Control: schema-required tenant_scope + runtime fail-closed
Owner: Settlement Platform
Due: 2026-08-05
Verification: unit, integration a production shadow test;
              missing, empty a wrong tenant sú odmietnuté
```

Action `napísať dokumentáciu` môže byť užitočná, ale sama neodstráni executable failure path.

## 17. RCA acceptance verdict

Analýza je prijatá, keď:

- exact incident a impact subject sú definované;
- timeline používa overené state transitions a clock limitations;
- trigger, proximate mechanismus a business impact sú oddelené;
- technical, systemic, escape, detection, amplification a recovery causes sú vyhodnotené;
- relevantné competing hypotheses majú evidence verdict;
- causal claims prežijú counterfactual otázky;
- human actions sú faktické a zasadené do system contextu;
- corrective actions mapujú na konkrétne mechanisms;
- každý action má ownera, priority, termín a verification;
- similar-system search bol vykonaný;
- recurrence a second-operation test potvrdia odstránenie pathu;
- residual risk má explicitného ownera.

## 18. Troubleshooting slabej RCA

```text
incident sa opakuje alebo action items nefungujú
→ exact prior RCA generation
→ pôvodný causal graph
→ ktoré actions boli closed a akým dôkazom
→ či control bol iba configured alebo effective
→ či recurrence použila rovnaký mechanismus
→ či analysis skončila pri triggeri/osobe
→ missing escape/detection/recovery branches
→ organizational incentive alebo ownership gap
→ re-open RCA a prepracuj action portfolio
```

Closed ticket nie je dôkaz closed failure mechanismu.

## 19. Anti-patterny

### Posledná zmena je root cause

Change môže byť trigger, ale systémové kontroly mali obmedziť jeho nesprávny outcome.

### Human error

Opisuje actor action bez vysvetlenia, prečo bola možná, rozumná alebo neobmedzená.

### Jedna root cause za každú cenu

Skryje paralelné escape, amplification a recovery paths.

### Five Whys ako rituál

Lineárny chain nahradí skutočný distributed causal graph.

### Timeline z incident chatu

Chat je neúplný a časovo skreslený; musí sa korelovať s authoritative system evidence.

### Action item = training

Training môže pomôcť, ale bez executable guardrailu sa rovnaký mechanismus vráti.

### RCA bez follow-up verification

Dokument vysvetlí minulosť, ale nezmení production behavior.

## 20. Kontrolné otázky

1. Čo tvorí exact RCA subject?
2. Ako sa trigger, proximate mechanismus a root cause líšia?
3. Prečo treba odlíšiť technical, systemic a escape cause?
4. Ako causal graph zlepšuje analýzu oproti lineárnemu príbehu?
5. Čo testuje counterfactual otázka?
6. Aké sú limity Five Whys?
7. Kedy je root-cause depth príliš plytká alebo príliš abstraktná?
8. Ako zapísať human action blameless, ale presne?
9. Prečo replication a backup nezabránili `SRE-PAY-54`?
10. Čo robí corrective action overiteľnou?
11. Ako similar-system search znižuje recurrence risk?
12. Čo musí overiť RCA acceptance verdict?

## Glossary impact

Relevantné pojmy: RCA subject, proximate mechanismus, technical root cause, systemic root cause, escape cause, detection cause, amplification cause, recovery-delay cause, causal graph, counterfactual test, root-cause depth, corrective-action portfolio, mechanism closure, similar-system search a RCA acceptance verdict.

## Primárne zdroje

- [Google SRE — Postmortem Culture: Learning from Failure](https://sre.google/sre-book/postmortem-culture/)
- [Google SRE Workbook — Postmortem Culture: Learning from Failure](https://sre.google/workbook/postmortem-culture/)
- [Google SRE — Effective Troubleshooting](https://sre.google/sre-book/effective-troubleshooting/)
- [NIST SP 800-61 Rev. 3 — Incident Response Recommendations and Considerations](https://csrc.nist.gov/pubs/sp/800/61/r3/final)
