# Trigger, artifact a cache

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Trigger, artifact a cache sú tri odlišné časti jedného delivery provenance reťazca. Trigger vytvorí konkrétny pipeline run a určí jeho trust context. Artifact je autoritatívny immutable výstup viazaný na presné build inputs a evidence. Cache je odstrániteľná optimalizácia, ktorá môže zrýchliť výpočet, ale nesmie rozhodovať o correctness ani release identity.

```text
autentizovaný event alebo príkaz
→ resolved source, target, candidate a workflow revision
→ pipeline run v konkrétnom permission contexte
→ validovaný cache restore alebo cold recompute
→ build a verification
→ immutable artifact digest + provenance
→ complete evidence fan-in
→ retention, promotion alebo distribúcia
```

## 1. Cieľ kapitoly

Nosný model kapitoly je trigger-to-artifact lifecycle:

```text
event identity
→ authorization a deduplication
→ authoritative candidate/run identity
→ trusted execution context
→ cache ako nedôveryhodný optional input
→ immutable artifact publication
→ evidence manifest a eligibility
→ promotion/rollback retention
→ audit a incident traceability
```

Cieľom nie je naučiť sa zoznam triggerov, artifact store-ov a cache keys. Cieľom je rozumieť, ako sa z udalosti stane konkrétny, reprodukovateľný a auditovateľný release output bez zámeny oportunistického state za dôveryhodný artifact.

## 2. Nosný scenár: Atlas Orders 3.10.1

Atlas mení payment retry behavior a migration bundle. Zmena môže spustiť viac udalostí:

```text
pull request synchronization
push na feature branch
merge-queue candidate
push na protected main
release tag
manual production promotion
```

Každá udalosť má iný účel a trust:

```text
fork/PR run
→ validuje nedôveryhodný candidate bez secrets

merge-queue run
→ rozhoduje o budúcom main candidate

protected-main build
→ publikuje release-eligible immutable artifacts

manual promotion
→ vyberá existujúci schválený release manifest digest
```

Atlas musí vedieť odpovedať:

- ktorý event a actor vytvorili run;
- ktoré source, target a candidate SHA sa vykonali;
- ktorá workflow revision a policy rozhodovali;
- či cache pochádzala zo správneho trust namespace;
- ktoré bytes vznikli a aký majú digest;
- ktoré reports, signatures a attestations patria tomuto digestu;
- kde je artifact nasadený a dokedy je rollback-eligible.

## 3. Trigger je vytvorenie runtime contractu

Trigger neurčuje iba čas spustenia. Vytvára pipeline runtime contract:

```text
repository + event ID + actor
+ event type a payload
+ source/target refs
+ resolved source/target/candidate SHA
+ workflow revision
+ typed inputs
+ permissions a secret scope
+ concurrency group
→ pipeline run identity
```

Rovnaký YAML môže byť bezpečný pri protected-main run-e a nebezpečný pri fork pull requeste. Permissions sa preto odvodzujú z overeného event contextu a server-side policy, nie z user-controlled názvu branchu alebo jobu.

## 4. Authoritative run a candidate identity

Pre jednu zmenu môže vzniknúť viac runs. Atlas explicitne určuje ich autoritu:

| Run | Predmet rozhodnutia | Povolené outputs |
|---|---|---|
| PR source run | rýchly branch feedback | diagnostické reports |
| merge-result/queue run | budúci main candidate | required integration verdict |
| protected-main run | prijatý main commit | signed release artifacts |
| schedule | časovo alebo scope závislá kontrola | refresh/drift evidence |
| manual promotion | existujúci manifest digest | environment deployment record |

Branch name nie je candidate identity. Required status sa viaže na presný synthetic merge alebo queue SHA a invaliduje sa pri zmene source, target alebo workflow policy.

## 5. Event payload je nedôveryhodný input

Branch name, tag, pull-request title, comment, changed path, manual input alebo webhook field môžu byť kontrolované používateľom.

Bezpečný flow:

```text
payload bytes
→ signature/authentication
→ schema a type validation
→ canonicalization a allowlist
→ authorization pre požadovanú operáciu
→ použitie ako dátový argument
```

Hodnoty sa nesmú priamo skladať do shell commandu, filesystem pathu, cloud role name, SQL alebo Kubernetes resource name. Quoting rieši iba časť injection rizika; nerieši, či má actor právo zvoliť `production`.

## 6. Deduplikácia a supersession

PR synchronization môže vytvoriť push aj merge-request event. Webhook môže byť opakovaný po timeout-e. Bez idempotency vznikajú paralelné buildy, mutable-tag races a nejasný authoritative result.

Atlas používa run key:

```text
repository
+ event class
+ delivery/event ID
+ candidate SHA
+ workflow revision
```

Policy určuje:

- ktorý run publikuje required status;
- ktorý smie publikovať release artifact;
- ako sa duplicate event deduplikuje;
- kedy novší commit superseduje starší validation run;
- ktoré mutation jobs sa nesmú tvrdo cancelovať.

Read-only verification možno agresívne rušiť. Publication, migration alebo deployment potrebuje state-aware cancellation a cleanup.

## 7. Path selection je dependency decision

Monorepo trigger môže vybrať affected set, ale glob pattern nie je úplný dependency model.

```text
changed path
→ dependency a generated-artifact graph
→ affected components a controls
→ conservative fallback pri neznámom edge
```

Root config, lockfile, schema, base image, shared library, workflow template, rename alebo delete môžu ovplyvniť služby mimo priameho path matchu. False-green selection incident opravuje dependency graph alebo fallback policy, nie iba konkrétny test.

## 8. Schedule a manual trigger

Scheduled run je vhodný pre vlastnosti závislé od času alebo širokého scope-u: dependency refresh, vulnerability rescan, certificate expiry, drift, restore drill, full regression a cold-cache verification. Nemá nahrádzať merge gate pre známy blocking failure.

Manual trigger je používateľské API. Atlas production promotion prijíma:

```text
environment_id: stable allowlisted ID
release_manifest_digest: sha256:...
strategy: canary | rolling | blue-green
change_reference: audit identifier
```

Neprijíma branch name, ktorý by sa v produkčnom kroku znovu buildol. Manual promotion vyberá existujúci eligible digest.

## 9. Cache je optional a nedôveryhodný input

Cache môže zrýchliť dependency download, compiler, container layer alebo analysis. Jej lifecycle:

```text
vypočítať exact key a trust namespace
→ restore exact/fallback/miss
→ validovať manifest, toolchain a integrity
→ recompute chýbajúci state
→ vykonať build/test
→ zapísať nový cache iba z povoleného úspešného runu
```

Workflow musí zostať správny po úplnom odstránení cache. Cold run je correctness test pipeline.

## 10. Cache key a namespace

Key reprezentuje relevantné inputs:

```text
trust namespace
+ OS/base image digest
+ architecture
+ toolchain version
+ dependency lock hash
+ build flags
+ generator/schema/config identity
```

Atlas oddeľuje minimálne:

```text
untrusted-pr-readonly
trusted-main
release-builder
```

Fork run nesmie zapisovať executable cache, ktorú neskôr obnoví privileged main alebo signing job. Cache name ani metadata nesmú obsahovať secrets.

## 11. Artifact je autoritatívny output

Atlas artifacts pre release 3.10.1:

```text
orders-api image digest A
payment-worker image digest B
migration bundle digest M
release manifest digest R = {A, B, M, config schema}
SBOM, signatures a provenance
```

Artifact má:

- content-derived immutable digest;
- source commit a workflow/run identity;
- builder a toolchain identity;
- dependency/base-image materials;
- SBOM, provenance a podpis podľa policy;
- explicitný retention a revocation state;
- eligibility oddelenú od samotnej existencie.

Mutable tag môže byť alias. Deployment a evidence sa viažu na resolved digest.

## 12. Identity, integrity, authenticity a provenance

Tieto dôkazy odpovedajú na rozdielne otázky:

```text
digest
→ ktoré bytes?

integrity verification
→ zmenili sa bytes?

signature/identity
→ kto ich vytvoril alebo schválil?

provenance
→ z akého source, materials, workflowu a buildera vznikli?

policy verdict
→ smú sa použiť pre daný environment?
```

Hash uložený vedľa kompromitovaného artifactu nepreukazuje dôveryhodný pôvod.

## 13. Build once, promote many

Atlas buildne release artifacts iba v protected-main release builderi:

```text
accepted commit C
→ pinned build inputs
→ digesty A, B, M
→ immutable release manifest R
→ všetky ďalšie testy a environments používajú R
```

Staging ani produkcia nerebuildujú. Rebuild by vytvoril nový supply-chain event a nové bytes, pre ktoré stará evidence neplatí.

## 14. Evidence fan-out a fan-in

Po publikovaní manifestu R bežia paralelné controls:

```text
R
├─> signature/provenance verification
├─> image/SCA scan
├─> component a migration tests
├─> staging deployment/smoke
└─> compatibility policy
```

Fan-in vytvorí evidence manifest a overí:

- očakávané evidence IDs a shardy;
- väzbu každého reportu na R alebo jeho component digest;
- completion status nástroja;
- freshness a policy version;
- absence revocation;
- platné exceptions.

„Nula findings“ bez complete scan reportu nie je pass.

## 15. Artifact state a retention

Artifact lifecycle:

```text
built
→ verified
→ signed/attested
→ promotable
→ deployed/released
→ superseded alebo revoked
→ retained podľa rollback/audit policy
```

Retention pokrýva rollback window, incident investigation, SBOM/provenance a audit. Pipeline-local krátkodobý ZIP nie je vhodný ako jediný production artifact store.

Revoked artifact zostáva identifikovateľný pre audit, ale promotion policy ho blokuje.

## 16. Worked failure: duplicate triggers prepísali release alias

Atlas po merge-i spustil push pipeline aj upstream release pipeline. Obe publikovali mutable tag `orders:3.10.1`:

```text
push run buildol digest A1
upstream run buildol digest A2 s novším base-image resolve
→ oba zapisovali rovnaký tag
→ staging overil A1
→ posledný writer nastavil tag na A2
→ produkcia nasadila A2
```

### Root cause

Chýbala authoritative-run policy, deduplication a build-once contract. Mutable alias sa používal ako artifact identity.

### Náprava

- iba protected-main run publikuje release artifact;
- run key deduplikuje rovnaký candidate/workflow;
- artifact sa publikuje immutable digestom;
- tag je alias s resolved-digest auditom;
- release manifest viaže evidence na presné digests;
- promotion overuje digest, nie tag.

## 17. Worked failure: fork otrávil privileged cache

Fork PR mohol zapisovať shared compiler cache. Útočník vložil executable wrapper pod cestu, ktorú neskôr použil trusted signing job:

```text
untrusted PR zapísal shared cache
→ main signing job obnovil cache hit
→ wrapper bežal s registry/signing tokenom
→ pokúsil sa exfiltrovať credentials
```

### Root cause

Cache bola považovaná za neškodnú performance vrstvu, hoci obsahovala executable state a prekračovala trust boundary.

### Náprava

- cache namespaces sú oddelené podľa trustu;
- fork nemá write do trusted namespace;
- privileged job používa clean ephemeral runner;
- executable dependencies sa overujú podľa lockfile/checksum;
- signing job nepreberá branch workspace;
- security incident uchová cache metadata a provenance pred invalidáciou.

## 18. Failure taxonomy

Lifecycle rozlišuje:

- trigger rejected alebo unauthorized;
- duplicate/superseded run;
- invalid candidate/workflow context;
- cache miss ako normálny recompute stav;
- cache corrupt/poisoned/backend failure;
- build failure;
- artifact publication alebo integrity failure;
- incomplete/expired evidence;
- revoked alebo retention-missing artifact;
- promotion denied.

Cache miss nie je product failure. Chýbajúci production artifact alebo povinná attestation naopak nie je advisory detail.

## 19. Diagnostický postup

1. Potvrď event ID, actor, trigger class a authoritative-run policy.
2. Over source, target, candidate a workflow revision.
3. Skontroluj deduplication/concurrency key a supersession state.
4. Rozlíš cache exact hit, fallback, miss, corruption a backend failure.
5. Spusti cold build na čistom ephemeral runneri.
6. Porovnaj artifact digest, nie tag alebo filename.
7. Over builder, materials, provenance a signature.
8. Skontroluj expected evidence manifest a väzbu reportov na digest.
9. Over retention, revocation a promotion history.
10. Pri trust incidente zachovaj run/cache/artifact evidence pred cleanupom.
11. Oprav trigger, cache namespace alebo artifact policy a potvrď nový first-attempt flow.

## 20. Referenčné pravidlá

- Trigger definuje trust, candidate, workflow a permissions, nie iba čas.
- Event payload je nedôveryhodný input.
- Required result patrí presnému authoritative candidate SHA.
- Duplicate a replay eventy potrebujú idempotency.
- Production promotion prijíma existujúci digest, nie branch name na rebuild.
- Cache je odstrániteľná a validovaná optimalizácia.
- Cache trust namespaces nesmú prepájať fork a privileged workflows.
- Artifact má immutable content identity a provenance.
- Build-once znamená rovnaké bytes vo všetkých environments.
- Fan-in overuje completeness aj subject identity evidence.
- Retention musí prežiť rollback a audit window.
- Trigger-to-production traceability je incidentný zdroj pravdy.

## 21. Časté omyly

### „Trigger určuje iba kedy pipeline beží“

Určuje aj actor, trust context, candidate revision, workflow revision a povolené side effects.

### „Tag je verzia artifactu“

Tag môže byť mutable. Autoritatívna identity je resolved content digest.

### „Cache hit je vždy bezpečný“

Cache môže byť stale, corrupt alebo pochádzať z nedôveryhodného writera.

### „Cache a artifact sú iba dva typy uložených súborov“

Artifact môže byť correctness a release input; cache musí byť postrádateľná.

### „Manual production job môže prijať branch name“

Tým sa obchádza build-once a dôkaz sa oddeľuje od nasadených bytes.

### „Scan bez findings je pass“

Iba ak sa scan kompletne vykonal a report patrí správnemu digestu.

## 22. Zhrnutie

Dôveryhodný Atlas provenance chain je:

```text
autentizovaný a deduplikovaný trigger
→ explicitný candidate/workflow/permission context
→ validovaný optional cache alebo cold recompute
→ protected build
→ immutable artifact a release manifest digest
→ complete subject-bound evidence
→ promotion a retention
→ auditovateľná väzba až po production deployment
```

Trigger vytvára runtime identity, artifact nesie dôveryhodný output a cache iba optimalizuje výpočet. Ich zámennosť vytvára false green, supply-chain drift aj incidentný chaos.

## 23. Kontrolné otázky

1. Čo všetko trigger definuje okrem času spustenia?
2. Prečo branch name nie je candidate identity?
3. Ako sa určuje authoritative run pri viacerých eventoch?
4. Prečo event payload potrebuje authorization aj po validácii syntaxe?
5. Kedy možno bezpečne cancelovať superseded run?
6. Prečo path trigger potrebuje dependency model a fallback?
7. Prečo production promotion prijíma digest namiesto branchu?
8. Ako sa líšia artifact identity, integrity, authenticity a provenance?
9. Ako build-once chráni platnosť evidence?
10. Prečo cache musí byť postrádateľná?
11. Ako trust namespace zabraňuje cache poisoningu?
12. Čo musí fan-in overiť pred promotion?
13. Prečo rollback window ovplyvňuje retention?
14. Ako vznikol Atlas duplicate-trigger artifact drift?

## Glossary impact

Relevantné pojmy: trigger contract, authoritative run, event payload, trigger deduplication, superseded run, candidate SHA, manual promotion, artifact, release manifest, artifact digest, integrity, authenticity, provenance, build once promote many, evidence fan-in, artifact eligibility, artifact retention, cache, cache key, cache namespace, cache poisoning a cold build.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Pipeline, stage, job a runner](pipeline-stage-job-runner.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Environment a promotion →](environment-and-promotion.md)
<!-- KNOWLEDGE-NAVIGATION:END -->