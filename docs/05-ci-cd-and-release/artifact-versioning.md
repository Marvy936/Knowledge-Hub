# Artifact versioning

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Artifact versioning spája ľudsky čitateľný release význam s presnou identitou bytes. Logical version pomáha ľuďom a dependency resolverom. Content digest identifikuje konkrétny artifact. Provenance vysvetľuje jeho pôvod. Release manifest viaže viac artifacts a konfigurácií do jednej podporovanej kombinácie.

```text
source candidate a pinované build inputs
→ immutable artifact digest
→ write-once publication
→ evidence viazaná na digest
→ release manifest
→ promotion bez rebuildu
→ deployment record
→ retention, revocation a recovery
```

## 1. Cieľ kapitoly

Nosný model kapitoly je artifact-identity lifecycle:

```text
release intent
→ build subject
→ content identity
→ logical version
→ publication transaction
→ provenance a evidence binding
→ release assembly
→ promotion a runtime identity
→ retention alebo revocation
→ recovery eligibility
```

Cieľom nie je vybrať pekný názov image tagu. Cieľom je vedieť dokázať, ktoré bytes boli vytvorené, overené, schválené, nasadené a zachované pre obnovu.

## 2. Nosný scenár: Atlas Orders 3.10.1-rc.2

Reusable pipeline z predchádzajúcej kapitoly vytvorí Orders candidate:

```text
source commit C
+ pipeline graph G
+ builder image B
+ dependency lock L
+ base image digest P
→ orders-api artifact digest D_api
→ migration bundle digest D_migration
→ evidence manifest digest E
```

Release candidate dostane logical version:

```text
3.10.1-rc.2
```

Atlas vytvorí content-addressed release manifest M:

```yaml
release: 3.10.1-rc.2
components:
  orders-api: sha256:D_api
  migrations: sha256:D_migration
evidence: sha256:E
source: C
pipeline_graph: G
config_schema: 12
```

Po úspešnom schválení finalizácia nevytvorí nový build. Vytvorí final release record `3.10.1`, ktorý stále smeruje na manifest M a tie isté component digests.

```text
candidate M
→ testy a approval nad M
→ final alias 3.10.1 → M
→ staging aj production nasadia M
```

Ak production pipeline znovu buildne source, vznikne iný subject. Predchádzajúce testy a approval ho nepreukazujú, aj keby commit aj logical version zostali rovnaké.

## 3. Source, artifact a release nie sú rovnaká identita

Source commit odpovedá:

```text
aká verzia source stromu bola vstupom?
```

Artifact digest odpovedá:

```text
aké konkrétne bytes vznikli?
```

Release manifest odpovedá:

```text
aká presná kombinácia componentov, migration, evidence a config contractu sa riadi ako jeden release?
```

Rovnaký source commit môže vytvoriť rozdielne bytes pri zmene:

- compileru alebo toolchainu;
- base image;
- dependency resolutionu;
- build flags;
- target architecture;
- locale, timezone alebo timestampov;
- network-fetched vstupu;
- pipeline alebo builder behavioru.

Commit C preto zostáva dôležitou provenance stopou, ale nie úplnou artifact identity.

## 4. Tri vrstvy identity

Atlas rozlišuje:

### Logical identity

```text
atlas/orders-api:3.10.1
```

Komunikuje release intent, ordering alebo compatibility policy v konkrétnom namespace.

### Content identity

```text
registry.internal/atlas/orders-api@sha256:D_api
```

Identifikuje konkrétny manifest a nepriamo jeho content. Zmena bytes vytvorí nový digest.

### Runtime identity

```text
release manifest M
+ rendered config revision R
+ secret references S
+ infrastructure revision I
+ database migration state DB
+ feature exposure F
+ target environment production-eu
```

Incidentný tím potrebuje všetky tri. Logical version bez digestu nevysvetlí historické bytes. Digest bez release a runtime contextu nevysvetlí compatibility ani effective behavior.

## 5. Namespace je súčasť version identity

Číslo `3.10.1` nie je globálne jednoznačné:

```text
atlas/orders-api:3.10.1
atlas/orders-worker:3.10.1
atlas/payments-api:3.10.1
```

Plná identity typicky obsahuje:

```text
registry alebo repository
→ organization/project namespace
→ artifact name
→ logical version alebo alias
→ platform/variant podľa potreby
→ content digest
```

Aj CI build number `18422` má význam iba spolu s project a pipeline namespace. Po migrácii CI platformy nemusí byť monotónny ani unikátny.

## 6. Logical version a digest riešia rozdielne otázky

Logical version môže používať SemVer, calendar version alebo internú monotónnu sekvenciu. Jej contract musí definovať:

- scope namespace;
- ordering alebo compatibility význam;
- pre-release pravidlá;
- immutability;
- ownership publication práva.

Digest je content identity. Umožňuje:

- presne pinovať deployment;
- overiť transport integrity;
- viazať test, scan, signature a approval;
- rozlíšiť dva buildy rovnakej logical version;
- auditovať pohyb mutable aliasu.

Hash sám nepreukazuje dôveryhodnosť. Škodlivý artifact môže mať úplne správny digest. Dôvera vzniká až z publisher identity, provenance, policy a quality evidence.

## 7. Publication je write-once state transition

Atlas publication flow je transakcia:

```text
build output
→ vypočítaj a over digest
→ uploadni temporary object
→ potvrď registry content identity
→ create-only publish candidate version
→ publikuj provenance, SBOM a evidence references
→ vytvor alebo aktualizuj audit record
```

Publication contract určuje:

- kto vlastní namespace;
- ktoré identity smú publikovať;
- create-only alebo write-once správanie;
- collision behavior;
- idempotency key;
- atomicitu version a metadata publication;
- retry po unknown outcome;
- cleanup partial uploadu;
- kto môže posunúť alias, yanknúť alebo revokovať release.

Vydaná version sa neopravuje prepísaním. Chybný `3.10.1` dostane `3.10.2`, yank alebo revocation record podľa charakteru problému.

## 8. Unknown publication outcome vyžaduje reconciliation

Pipeline môže timeoutnúť po tom, čo registry artifact prijala, ale pred tým, než job zaznamenal success.

Nesprávny recovery:

```text
timeout
→ slepý rebuild
→ druhý digest pod rovnakou candidate version
```

Správny recovery:

```text
timeout
→ lookup publication podľa idempotency key a očakávaného digestu
→ existuje rovnaký digest: pokračuj
→ version neexistuje: bezpečne retry upload
→ version existuje s iným digestom: collision a hard failure
```

Unknown outcome nie je to isté ako failure. Reconciliation zabraňuje duplicitnej publication aj miešaniu evidence.

## 9. Build once, promote many

Atlas používa jeden candidate subject:

```text
build M
→ verify M
→ staging deploy M
→ production deploy M
```

Promotion mení eligibility, target assignment alebo release status. Nemení bytes.

Rizikový model:

```text
staging build M1
→ testy nad M1
→ production rebuild M2
→ approval nad M1, deployment M2
```

Aj pri rovnakom commite môže M2 obsahovať iný base image, dependency alebo timestamp. Produkcia potom nedostala overený subject.

## 10. Rebuild a reproducible build sú odlišné mechanizmy

Rebuild je nový execution attempt. Reproducible build overuje, či rovnaké deklarované vstupy vytvoria identický alebo ekvivalentný output.

```text
pôvodný release subject D
→ nezávislý rebuild s rovnakými pinovanými vstupmi
→ výsledok D'
→ porovnanie D a D'
```

Zhodný digest zvyšuje dôveru v kontrolu vstupov. Nezhodný digest môže odhaliť nondeterministický timestamp, file ordering, mutable dependency alebo toolchain drift.

Reproducibility nenahrádza promotion pôvodného D. Produkčný deployment stále používa pôvodný schválený digest.

## 11. Evidence musí byť viazaná na immutable subject

Každý Atlas result obsahuje:

```text
subject digest alebo release-manifest digest
check type a tool version
verdict
report digest
producer a runner identity
context a timestamp
freshness scope
attempt identity
```

Branch name, tag alebo release number nestačí, ak sa môže pohnúť alebo byť prepísaný.

```text
unit result → D_api
image scan → D_api
migration test → D_migration
compatibility approval → M
production deployment record → M + runtime revisions
```

Dôkaz musí zodpovedať vrstve, ktorú hodnotí. Source SAST môže patriť source commit C, ale image vulnerability scan patrí final image digestu D_api.

## 12. Provenance vysvetľuje vznik artifactu

Provenance pre D_api obsahuje:

```text
source repository a commit C
pipeline a resolved graph G
builder workload identity
builder image digest B
dependency lock L
base image digest P
target platform
build parameters
output digest D_api
```

Policy môže odmietnuť artifact, ak:

- source nepochádza z povoleného repository alebo trusted ref contextu;
- pipeline graph alebo tool dependency nebola pinovaná;
- builder nebol schválený;
- output vznikol na nedôveryhodnom runneri;
- attestation neviaže správny subject;
- required claims alebo signatures chýbajú.

Provenance nepreukazuje funkčnosť. Vysvetľuje a autentizuje supply-chain cestu, ktorú quality evidence dopĺňa.

## 13. Signature potvrdzuje identity claim, nie kvalitu

Signature alebo keyless attestation viaže signer či workload identity na digest alebo provenance statement.

Verification kontroluje:

- presný signed subject;
- signer alebo certificate identity;
- povolený repository a workflow context;
- trust chain, validity a revocation stav;
- policy revision;
- čas a transparency/audit record podľa modelu.

Podpísaný chybný artifact zostáva chybný. Signature nie je náhrada tests, scanov ani compatibility evidence.

## 14. SBOM patrí final artifactu

Atlas SBOM je viazaný na D_api. Source-only inventory nestačí, pretože final image môže obsahovať:

- base image packages;
- build-generated dependencies;
- vendored libraries;
- platform-specific native components;
- runtime packages pridané packaging krokom.

Multi-platform image môže mať odlišný SBOM pre amd64 a arm64 variant. Scan result aj SBOM preto rozlišujú index digest a child manifest digest.

## 15. Multi-platform release potrebuje variant identity

Orders image môže mať OCI index digest I:

```text
I
├─ linux/amd64 digest D_amd64
└─ linux/arm64 digest D_arm64
```

Deployment pinovaný na I resolve-ne child variant podľa platformy. Evidence musí vedieť, či overovala index alebo konkrétny child.

```text
platform verification amd64 → D_amd64
platform verification arm64 → D_arm64
release identity → I + obidva child evidence sets
```

Zelený amd64 test nie je dôkazom arm64 artifactu.

## 16. Release manifest uzatvára multi-component identity

Orders release nie je iba API image. Manifest M viaže:

```text
orders-api D_api
migrations D_migration
evidence E
config schema 12
minimum database state 2026_07_26_01
```

Manifest je:

- immutable alebo content-addressed;
- podpisovaný podľa policy;
- validovaný proti compatibility rules;
- subjectom approvalu a promotion;
- vstupom deploymentu aj recovery;
- retention rootom počas support windowu.

Bez manifestu môže production skombinovať API z RC2 s migration bundle-om z RC1. Jednotlivé artifacts by boli platné, ale kombinácia nebola testovaná.

## 17. Mutable alias je pointer, nie historická identity

Alias `candidate`, `stable` alebo `production` môže smerovať na digest:

```text
stable → M
```

Pri každom pohybe Atlas zaznamená:

- starý a nový digest;
- actor alebo workload identity;
- promotion record;
- policy verdict;
- čas a dôvod.

Deployment môže alias resolve-nuť, ale uloží výsledný immutable digest. Historický deployment sa nikdy nediagnostikuje podľa dnešnej hodnoty `stable`.

Vydaná logical version `3.10.1` je write-once. `stable` je zámerne mutable release channel.

## 18. Runtime version je širšia než artifact version

Rovnaký manifest M môže mať odlišný behavior v staging a production:

```text
runtime state
= M
+ rendered config revision
+ secret/certificate versions
+ infrastructure a IAM revision
+ database state
+ feature flags a traffic exposure
```

Deployment record preto zachová effective revisions. Artifact versioning odstraňuje nejasnosť bytes, ale samo neodstraňuje config alebo environment drift.

## 19. Yank, revocation a deletion sú rozdielne prechody

### Yank

Version zostáva dostupná pre existujúci lock alebo audit, ale nové resolution ju nemá bežne vybrať. Používa sa pri chybnej compatibility metadata alebo závažnom defekte, ktorý nevyžaduje okamžité security blokovanie všetkých použití.

### Revocation

Policy označí digest alebo manifest ako nepovolený. Môže:

- zablokovať nové deployments;
- upozorniť aktívne environments;
- spustiť incident, rollback alebo roll-forward;
- quarantine-nuť artifact;
- revokovať súvisiacu trust identity.

### Deletion

Fyzicky odstráni bytes. Je samostatná chránená operácia, pretože revokovaný artifact môže byť stále potrebný pre forenznú analýzu.

## 20. Retention sa riadi referenciami a recovery, nie iba vekom

Artifact je retention root, ak je:

- aktívne nasadený;
- súčasť podporovaného release manifestu;
- rollback candidate;
- predmet incidentu alebo legal hold;
- potrebný pre audit alebo reproducibility;
- referencovaný iným artifactom alebo release setom.

Lifecycle môže vyzerať:

```text
transient branch artifact
→ release candidate
→ active supported release
→ rollback window
→ historical support alebo deprecation
→ unreferenced quarantine
→ grace period
→ garbage collection
```

CI run expiry nesmie odstrániť production artifact. Artifact store potrebuje vlastnú reference-aware retention policy.

## 21. Recovery eligibility je viac než dostupný starý tag

Pred označením M_prev za rollback candidate Atlas overí:

- bytes, manifest a provenance sú dostupné;
- signatures a trust policy ich stále povoľujú;
- config a secret references existujú;
- database a event state zostávajú kompatibilné;
- deployment tool pozná návrat;
- potrebné migrations alebo reconciliation sú definované;
- post-rollback validation existuje.

Logical version bez zachovaných bytes a compatibility dôkazu nie je recovery capability.

## 22. Worked failure: `3.10.1-rc.2` označovala dva digesty

Dva build jobs súbežne publikovali rovnakú candidate version. Registry povoľovala mutable tag:

```text
job A → D1 → tag 3.10.1-rc.2
job B → D2 → prepíše tag 3.10.1-rc.2
unit tests a approval → D1
production resolve tag neskôr → D2
```

Production dostala bytes, ktoré neprešli daným evidence setom.

### Root cause

Logical version nebola write-once a evidence sa viazala na tag namiesto digestu. Publication nemala create-if-absent semantics ani release lock.

### Náprava

- candidate version je unikátna a immutable;
- publication používa create-only operation a idempotency key;
- každý result, approval a deployment record obsahuje digest;
- final alias sa posúva iba transakčne po overení očakávaného old state;
- collision s iným digestom je hard failure, nie retryable overwrite.

## 23. Worked failure: garbage collection odstránil rollback artifact

Registry čistila artifacts staršie než 30 dní podľa CI pipeline timestampu. Orders `3.9.8` bol stále schválený last-known-good rollback release, ale pôvodný run expiroval:

```text
GC nevidel deployment a rollback references
→ odstránil component digest D_old
→ incident v 3.10.1 vyžadoval návrat
→ manifest existoval, bytes nie
→ recovery sa zmenila na urgentný rebuild neoveriteľného historického stavu
```

### Root cause

Retention model sledoval vek tagu, nie reference graph a support/recovery policy.

### Náprava

- active deployment a rollback manifests sú retention roots;
- release record drží component digests nezávisle od CI runu;
- deletion používa quarantine a grace period;
- secondary registry replikuje bytes, metadata aj signatures;
- restore a rollback pull sa pravidelne testujú.

## 24. Diagnostický postup

Pri nejasnosti artifact identity:

1. identifikuj plný registry/package namespace;
2. resolve-ni logical version alebo alias na digest;
3. porovnaj digest s release, evidence a deployment recordom;
4. identifikuj release manifest, index a platform child variant;
5. over source commit, builder, graph a declared build inputs;
6. skontroluj publication audit, collision a alias movement;
7. over provenance, signature a subject identity SBOM/reportov;
8. porovnaj candidate a final release — finalizácia nesmie rebuildovať;
9. skontroluj yank, revocation, quarantine a policy eligibility;
10. over retention roots, replication a recovery eligibility;
11. pri rozdielnom rebuilde porovnaj mutable alebo nondeterministické inputs.

Postup ide od mena k immutable subjectu a následne k pôvodu, evidence a runtime použitiu.

## 25. Referenčné pravidlá

- Source commit, logical version, digest a runtime identity sú odlišné vrstvy.
- Plný namespace je súčasť artifact identity.
- Vydaná logical version je write-once.
- Mutable alias slúži na channel alebo discovery, nie na historický audit.
- Promotion používa pôvodný digest bez rebuildu.
- Unknown publication outcome sa reconciliuje, nie slepo opakuje.
- Testy, scans, signatures, SBOM a approvals sa viažu na immutable subject.
- Multi-platform a multi-component release používa explicitný manifest.
- Revocation neznamená automatickú deletion.
- Retention sleduje references, support a recovery policy.
- Rollback eligibility zahŕňa artifact, config, data, trust a deployment contract.

## 26. Časté omyly

### „Commit SHA je verzia artifactu“

Commit identifikuje source, nie toolchain, dependencies, platform ani výsledné bytes.

### „Tag `latest` presne hovorí, čo beží“

Je to mutable pointer. Historický deployment potrebuje uložený digest.

### „Rovnaký source možno pri promotion znovu buildnúť“

Nový build je nový subject. Predchádzajúca evidence sa naň automaticky nevzťahuje.

### „Podpísaný artifact je bezpečný a funkčný“

Signature potvrdzuje identity claim. Kvalitu a compatibility dokazujú iné evidence vrstvy.

### „Starý tag znamená, že rollback je pripravený“

Bytes môžu chýbať a shared state môže byť nekompatibilný.

### „Revokovaný artifact treba okamžite zmazať“

Policy zákaz a fyzická deletion sú rozdielne kroky. Forenzná a recovery stopa môže byť stále potrebná.

## 27. Zhrnutie

Atlas artifact identity lifecycle je:

```text
pinované build inputs
→ immutable component digest
→ write-once candidate publication
→ provenance, SBOM a evidence viazané na digest
→ content-addressed release manifest
→ final logical version bez rebuildu
→ deployment record s runtime revisions
→ reference-aware retention
→ yank, revocation alebo tested recovery
```

Logical version komunikuje význam. Digest identifikuje bytes. Manifest identifikuje podporovanú kombináciu. Provenance a evidence vysvetľujú pôvod a kvalitu. Nasledujúca kapitola rozoberá, kedy logical version `3.10.1`, `3.11.0` alebo `4.0.0` správne komunikuje compatibility zmeny.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Reusable a parallel pipelines](reusable-and-parallel-pipelines.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Semantic Versioning →](semantic-versioning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->