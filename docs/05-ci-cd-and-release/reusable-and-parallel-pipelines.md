# Reusable a parallel pipelines

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Reusable pipeline nie je skopírovaný YAML fragment. Je to versionovaný provider–consumer contract, z ktorého CI platforma vytvorí konkrétny resolved execution graph. Paralelizácia následne rozdelí jeden immutable subject medzi viac jobs a znovu ich spojí do verdictu. Dôveryhodnosť preto závisí od troch vecí naraz: explicitného contractu, úplnosti graphu a identity výsledkov.

```text
consumer intent
+ pinned provider revision
+ typed inputs a permissions
→ resolved graph
→ jeden immutable candidate
→ očakávaný fan-out
→ izolované paralelné jobs
→ identity-aware fan-in
→ complete evidence manifest
```

## 1. Cieľ kapitoly

Nosný model kapitoly je reusable-and-parallel evidence lifecycle:

```text
potreba opakovanej delivery capability
→ provider contract
→ consumer binding
→ resolved graph a effective permissions
→ immutable execution subject
→ fan-out inventory
→ izolácia a paralelné vykonanie
→ fan-in completeness
→ verdict a evidence manifest
→ provider rollout, support a migration
```

Cieľom nie je maximalizovať počet template-ov ani jobs. Cieľom je skrátiť feedback bez toho, aby reuse skrylo authority a paralelizácia skryla chýbajúci alebo neporovnateľný dôkaz.

## 2. Nosný scenár: Atlas template 4.2 a Orders 3.10.1

Atlas platform tím publikuje reusable delivery template 4.2. Orders tím ho používa pre release candidate 3.10.1.

Consumer deklaruje:

```yaml
service: atlas-orders
contract_version: 2
build_target: orders-api
platforms:
  - linux-amd64
  - linux-arm64
required_checks:
  - unit
  - component
  - sast
  - image-scan
  - migration-contract
publish_release_candidate: true
```

Provider template sľubuje:

```text
inputs validované podľa contract v2
→ jeden build artifact digest D
→ presne definovaný verification inventory
→ každý job overuje D
→ fan-in vytvorí evidence manifest E pre D
→ release candidate sa publikuje iba z D + E
```

Resolved graph pre Orders vyzerá takto:

```text
validate consumer contract
        ↓
build artifact D
        ├───────────────┬───────────────┬───────────────┐
        ↓               ↓               ↓               ↓
unit/component      SAST source      scan D         migration contract
        │                               │               │
        ├──────────── linux-amd64 verify ───────────────┤
        └──────────── linux-arm64 verify ───────────────┤
                                                        ↓
                                      fan-in: expected inventory + D
                                                        ↓
                                          evidence manifest E
                                                        ↓
                                     publish candidate 3.10.1-rc.2
```

Tento graph je autoritatívnejší než consumer YAML alebo provider template samostatne. Až resolved graph ukazuje skutočné jobs, edges, conditions, runners, permissions, artifacts a failure propagation.

## 3. Provider a consumer vlastnia odlišné časti systému

Provider vlastní reusable capability:

- input a output schema;
- graph semantics;
- tool a runtime dependencies;
- maximálny permission envelope;
- artifact a evidence contract;
- compatibility, release a deprecation policy;
- representative fixtures, canary rollout a support.

Consumer vlastní konkrétne použitie:

- pinovanú provider revision;
- správne inputy a repository assumptions;
- domain-specific testy;
- požadovanú support matrix;
- environment a deployment policy v dovolených hraniciach;
- migráciu pri zmene provider major contractu.

Provider nevie dokázať business correctness Orders služby. Consumer zas nemá potichu meniť required graph tak, že odstráni centrálne provenance alebo security controls.

## 4. Reuse boundary má byť čo najnižšia, ale úplná

Reusable logika môže byť umiestnená v rôznych vrstvách:

```text
library alebo CLI
→ script
→ pinovaný tool image
→ reusable job
→ reusable workflow
→ child alebo multi-project pipeline
→ platform capability
```

Atlas umiestňuje build a release logiku do testovateľného CLI `atlas-delivery`, zatiaľ čo template 4.2 rieši orchestration, credentials, runner selection, artifacts a gates.

```text
CLI contract
→ validácia, plan, build, publication a machine-readable result

pipeline contract
→ kedy a s akou authority sa CLI spustí, čo sa paralelizuje a ako vznikne verdict
```

Ak sa stovky riadkov business logiky ukryjú v template inheritance, nedajú sa spoľahlivo testovať mimo CI platformy. Ak sa naopak každý tím pokúsi lokálne skladať security a publication flow, vznikne copy-paste drift. Správna boundary oddeľuje prenositeľnú delivery logiku od platformového execution a trust modelu.

## 5. Provider contract musí pokryť správanie, nie iba názvy inputov

Contract v2 pre Atlas definuje:

```text
inputs
→ typy, povinnosť, defaults, allowed values a precedence

execution
→ runtime images, architecture, runner capabilities, network a timeouts

authority
→ token permissions, workload identity, secrets a environment access

outputs
→ artifact digest, report schema, evidence manifest a deployment records

failure
→ failed, canceled, timed out, incomplete, optional a tool-error semantics

lifecycle
→ compatibility, deprecation, support window a migration
```

Breaking change preto nie je iba odstránenie inputu. Provider rozbije contract aj vtedy, keď:

- zmení default z `publish=false` na `true`;
- premenuje artifact alebo output field;
- zmení required runner OS;
- rozšíri permissions;
- pridá nový blocking gate;
- zmení cancellation alebo retry propagation;
- prestane čakať na child pipeline;
- zmení význam overall verdictu.

Versionovanie reusable componentu musí tieto behaviorálne zmeny komunikovať rovnako dôsledne ako API knižnice.

## 6. Consumer binduje immutable provider identity

Orders repository neodkazuje na floating `main` ani `latest`:

```text
atlas-orders commit C
+ platform-template commit T
+ atlas-delivery image digest I
+ organization policy revision P
→ resolved graph digest G
```

Pre každý run sa zachová:

- consumer commit;
- provider a transitive include revisions;
- tool a image digests;
- typed inputs bez secret materialu;
- effective permissions;
- resolved graph digest;
- policy revision;
- runner identities.

Ak sa delivery behavior zmení bez diffu v Orders repository, prvá otázka nie je „čo sa pokazilo v aplikácii“, ale „ktorá časť resolved dependency setu alebo policy sa zmenila“.

## 7. Parallelizácia začína dependency graphom

Jobs môžu bežať súbežne iba vtedy, keď medzi nimi neexistuje skutočná control, data alebo policy dependency.

```text
control edge
→ downstream čaká na výsledok upstreamu

data edge
→ downstream potrebuje artifact alebo report upstreamu

policy edge
→ downstream potrebuje gate verdict alebo approval
```

Atlas môže spustiť unit tests, SAST a migration-contract kontrolu po validácii source paralelne. Image scan a platform verification však musia čakať na artifact digest D. Release publication musí čakať na complete fan-in E.

Zbytočný edge predlžuje critical path. Chýbajúci edge môže publikovať candidate skôr, než existuje required evidence.

## 8. Critical path nie je súčet jobov

Trvanie pipeline určuje najdlhšia required dependency cesta:

```text
validate 1 min
→ build 6 min
→ arm64 verify 9 min
→ fan-in 1 min
→ publish 1 min
= critical path približne 18 min
```

SAST môže trvať 7 minút a unit tests 4 minúty, ale ak bežia súbežne s buildom alebo platform verification, ich celý čas sa k pipeline latency nepripočíta.

Optimalizácia má rozlišovať:

- wall-clock latency;
- critical path;
- queue time;
- total compute;
- artifact transfer;
- canceled alebo retry waste;
- external-service contention.

Rozdelenie jedného 12-minútového test jobu na osem shardov nemusí pipeline zrýchliť, ak všetky čakajú na nedostupný runner pool alebo opakovane sťahujú 4 GB fixture.

## 9. Fan-out musí mať explicitný expected inventory

Po builde Atlas vytvorí fan-out manifest:

```yaml
subject: sha256:D
required_results:
  - unit
  - component
  - sast
  - image-scan
  - migration-contract
  - platform/linux-amd64
  - platform/linux-arm64
optional_results:
  - performance-advisory
```

Tento inventory vzniká pred vykonaním children. Nie je odvodený iba z výsledkov, ktoré náhodne dorazili.

Každý result obsahuje:

```text
result identity
subject digest D
check type a tool version
job/shard identity
attempt number
verdict
report digest
producer a runner identity
```

Ak arm64 job nevznikne pre chybu matrix generatora, fan-in vidí chýbajúcu required identity. Bez expected inventory by iba spočítal prijaté zelené výsledky a vytvoril false success.

## 10. Matrix a sharding sú inventory problémy

Matrix rozširuje deklarované dimensions na konkrétne jobs:

```text
platforms = [linux-amd64, linux-arm64]
runtimes = [java-21]
→ dve required platform identities
```

Sharding rozdeľuje jeden logical test inventory:

```text
suite manifest S
→ deterministic assignment shard-1..shard-4
→ každý test presne raz
→ reports zachovajú shard a attempt identity
→ fan-in overí missing aj duplicate tests
```

Dôveryhodný shard model potrebuje:

- jednoznačný test inventory;
- auditovateľné assignment pravidlo;
- izolované test data;
- deterministic seed alebo zaznamenanú randomizáciu;
- missing a duplicate detection;
- report merge bez straty pôvodu;
- zachovanie first-attempt failure pri retry.

Historical-duration balancing je optimalizácia. Pri zmene suite musí invalidovať starý model, inak môže jeden nový dlhý test vytvoriť outlier, ktorý drží celý fan-in.

## 11. Selective execution vytvára explicitné reziduálne riziko

Orders nemusí pri každom documentation commite spúšťať full platform matrix. Selection policy však musí vedieť vysvetliť:

```text
change inventory
→ affected-component mapping
→ selected checks
→ skipped checks s dôvodom
→ conservative fallback pri unknown
```

Rename migration súboru, zmena root build configu alebo neznámy dependency edge spúšťa širší fallback. Periodický full run kontroluje, či selector systematicky nevynecháva relevantné combinations.

„Job sa nevytvoril“ nesmie byť nerozoznateľné od „job nebol potrebný podľa policy“.

## 12. Paralelné jobs musia zdieľať identitu, nie mutable state

Všetky verification jobs čítajú rovnaký artifact digest D. Nepoužívajú mutable tag `candidate` a nerebuildujú source.

```text
build D
→ publish immutable D
→ paralelné jobs pull D
→ results bind to D
```

Mutable shared state sa izoluje:

- per-run database schema alebo tenant;
- unique object-storage prefix;
- immutable artifact names;
- per-platform cache namespace;
- environment lease pre shared deployment target;
- scoped credentials;
- idempotentný setup a cleanup.

Ak dva jobs zapisujú do rovnakého test accountu alebo migration schema, ich výsledok už nereprezentuje nezávislé overenie kandidáta. Race môže vytvoriť flaky failure aj false pass.

## 13. Cache nesmie niesť release evidence

Cache zrýchľuje obnoviteľné inputs. Artifact store a evidence store zachovávajú release-critical outputs.

Atlas používa:

```text
read-only trusted base cache
+ exact key podľa OS, architecture, toolchain a lock digestu
→ validovaný restore
→ designated writer publikuje až po úspechu
```

Untrusted pull-request jobs nezapisujú do namespace, ktorý číta privileged release job. Cold-cache run periodicky dokazuje, že pipeline je korektná aj bez cache.

Cache hit nie je dôkaz, že obsah patrí aktuálnemu source alebo artifactu. Fan-in z cache nikdy neskladá release verdict.

## 14. Retry vytvára nový attempt, nie automaticky nový dôkaz

Retry record zachová:

```text
logical job identity
attempt 1 → input D → failed result R1
attempt 2 → input D → passed result R2
selection policy → final verdict + first failure retained
```

Build retry je citlivejší. Ak attempt 2 vytvorí digest D2 namiesto D1, vznikol nový subject. Test z D1 a scan z D2 sa nesmú zlúčiť.

```text
D1 evidence set ≠ D2 evidence set
```

Fan-in kontroluje subject digest každého výsledku. Retry dôvod, attempt a vybraný final result zostávajú v evidence manifeste, aby flaky alebo infrastructure failure nezmizli za posledným zeleným pokusom.

## 15. Cancellation a fail-fast sú súčasťou graph contractu

Pri novšom Orders commite môže platforma zrušiť superseded pipeline. Cancellation musí propagovať:

```text
parent cancel
→ child a matrix cancel
→ mutation jobs prestanú bezpečne
→ cleanup a evidence upload dobehnú
→ verdict = canceled/incomplete, nie pass
```

Fail-fast je vhodný pre rýchly merge feedback, keď ďalšie jobs nepridajú nezávislú diagnostickú hodnotu. Nie je vhodný pre release compatibility matrix, ktorá potrebuje úplný failure inventory.

Optional advisory job môže zlyhať bez blokovania, ale jeho status zostáva viditeľný a má ownera, dôvod aj expiry. Permanentne červený optional job je nefunkčná kontrola.

## 16. Child a multi-project pipeline musia propagovať výsledok

Atlas parent pipeline môže spustiť child graph pre database migrations alebo promotion do GitOps repository. Trigger success dokazuje iba vytvorenie child runu.

Parent contract musí určiť:

- immutable child input;
- inherited a explicitné permissions;
- completion a failure propagation;
- artifacts a outputs;
- cancellation a retry semantics;
- timeout;
- idempotency a cycle prevention;
- correlation medzi run identities.

Fire-and-forget child nie je required gate. Ak parent publikuje candidate skôr, než child migration contract skončí, graph má chýbajúcu policy dependency.

## 17. Permission inheritance je samostatná trust boundary

Reusable workflow môže dostať authority caller-a. Atlas preto vyhodnocuje effective permissions po resolution:

```text
consumer token ceiling
∩ provider job requirements
∩ organization policy
∩ environment policy
→ effective job identity
```

Untrusted validation jobs nemajú production workload identity. Environment-scoped credential vznikne až v trusted deployment entrypointe a iba pre konkrétny release manifest a target.

Implicitné `inherit all secrets` je neakceptovateľné, pretože provider update by mohol potichu rozšíriť exposure do nového jobu.

## 18. Provider zmenu rolloutuje ako produktovú zmenu

Template 4.2 neprejde okamžite na všetkých consumerov:

```text
contract a static tests
→ disposable runner component tests
→ representative consumer fixtures
→ interný canary consumer
→ malý opt-in cohort
→ staged adoption
→ deprecation 4.1
```

Provider sleduje:

- failure rate podľa provider revision;
- resolved-graph a permission diffs;
- critical-path contribution a queue time;
- artifact/evidence completeness;
- rollback frequency;
- adopciu, overrides a deprecated consumers;
- support incidenty.

Centralizácia znižuje lokálny drift, ale zväčšuje globálny blast radius. Pinning, canary rollout, rollback a support ownership sú preto súčasťou reusable contractu.

## 19. Worked failure: arm64 shard zmizol a fan-in zostal zelený

Atlas matrix generator pri spracovaní `platforms` omylom odfiltroval `linux-arm64`:

```text
contract očakával amd64 + arm64
→ generator vytvoril iba amd64 job
→ amd64, tests a scan prešli
→ starý fan-in agregoval iba prijaté results
→ evidence manifest označil candidate ako complete
→ arm64 production node stiahol neoverený variant
→ proces zlyhal pri štarte pre chýbajúcu native knižnicu
```

### Root cause

Fan-in nemal pre-run expected inventory. Neprítomný result interpretoval ako neprítomný failure. Provider testoval YAML syntax, nie graph completeness.

### Náprava

- fan-out manifest deklaruje required result identities pred schedulingom;
- fan-in používa set equality nad expected a received inventory;
- variant result obsahuje child digest a platform identity;
- unknown selector state spúšťa conservative full matrix;
- provider fixture overuje amd64/arm64 graph a missing-child failure;
- release manifest nepovolí variant bez vlastného evidence setu.

## 20. Worked failure: retry zmiešal dva artifacty

Build attempt 1 publikoval D1 a následne timeoutol pri odovzdaní metadata. Automatický retry rebuildol source s pohyblivým base image a publikoval D2:

```text
unit a component testy už bežali nad D1
→ retry build vytvoril D2
→ image scan a signature patrili D2
→ fan-in spároval results iba podľa release version 3.10.1-rc.2
→ candidate obsahoval D2, ale časť approval evidence dokazovala D1
```

### Root cause

Artifact identity nebola súčasťou result key. Build retry nebol idempotentný a použil mutable build input.

### Náprava

- build inputs vrátane base image sú pinované;
- publication používa idempotency key a create-only semantics;
- timeout po publish sa reconciliuje lookupom očakávaného digestu, nie slepým rebuildom;
- každý result a approval sa viaže na subject digest;
- nový digest vytvorí nový candidate a nový evidence inventory.

## 21. Diagnostický postup

Keď reusable alebo parallel pipeline zlyhá:

1. potvrď consumer commit, provider revision, tool images a policy revision;
2. načítaj resolved graph digest a effective permissions;
3. identifikuj jeden immutable artifact alebo release-manifest subject;
4. porovnaj expected fan-out inventory s vytvorenými jobs;
5. porovnaj expected inventory s prijatými results;
6. rozlíš failed, missing, canceled, timed-out, optional a tool-error stavy;
7. over subject, shard, platform a attempt identity každého reportu;
8. skontroluj shared resources, cache namespaces, locks a quotas;
9. zmeraj critical path, queue time a shard imbalance;
10. pri provider regresii pinni poslednú známu dobrú revision a zachovaj failed evidence;
11. pridaj provider fixture alebo graph contract test pre zistený failure mode.

Postup ide od declarovaného contractu cez resolved graph po runtime evidence. Náhodné re-runovanie bez identity auditu môže iba prekryť chybu ďalším attemptom.

## 22. Referenčné pravidlá

- Reusable component je dependency s providerom, contractom a lifecycle-om.
- Consumer pinuje immutable provider a transitive identities.
- Review subject je resolved graph, nie iba source fragment.
- Každý parallel branch overuje rovnaký immutable subject.
- Expected fan-out inventory vzniká pred execution.
- Fan-in rozlišuje missing, duplicate, stale, canceled a optional results.
- Matrix a sharding zachovávajú úplný inventory a attempt identity.
- Retry nesmie miešať evidence rôznych digestov.
- Shared mutable state je izolovaný, zamknutý alebo explicitne vlastnený.
- Cache nie je artifact ani evidence store.
- Child completion a cancellation sa propagujú do parent verdictu.
- Effective permissions sa kontrolujú po template resolution.
- Provider rollout používa fixtures, canary cohort, telemetry a rollback.

## 23. Časté omyly

### „Reusable pipeline je centrálna YAML šablóna“

Bez explicitného behavior, permission a compatibility contractu je to iba vzdialený source fragment s veľkým blast radiusom.

### „Viac paralelných jobs vždy znamená rýchlejšiu pipeline“

Queueing, setup overhead, transfer a external contention môžu critical path predĺžiť a výrazne zvýšiť total compute.

### „Fan-in je zelený, keď všetky doručené reports sú zelené“

Najprv musí dokázať, že doručený set je úplný a patrí rovnakému subjectu.

### „Retry vymaže pôvodný failure“

Retry je ďalší attempt. Pôvodný výsledok, dôvod a artifact identity zostávajú v evidence.

### „Optional job môžeme ignorovať“

Optional znamená explicitne akceptované reziduálne riziko, nie neviditeľný alebo trvalo pokazený check.

### „Parent pipeline splnil úlohu, keď spustil child“

Trigger nie je completion ani verdict. Required child musí propagovať svoj výsledok.

## 24. Zhrnutie

Atlas reusable a parallel model je:

```text
versionovaný provider contract
→ pinovaný consumer binding
→ resolved graph a effective permissions
→ jeden immutable candidate
→ explicitný expected fan-out inventory
→ izolované matrix/shard jobs
→ results viazané na subject, shard a attempt
→ completeness-aware fan-in
→ evidence manifest
→ provider canary, support a migration lifecycle
```

Reuse znižuje drift iba vtedy, keď má stabilný contract a kontrolovaný blast radius. Paralelizácia zrýchľuje feedback iba vtedy, keď zachováva dependency edges, immutable artifact identity, úplnosť výsledkov a failure semantics. Nasledujúca kapitola preto preberá presnú identitu artifactu, ktorý tento graph vyrobil a overil.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Pipeline as Code](pipeline-as-code.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Artifact versioning →](artifact-versioning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
