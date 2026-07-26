# Continuous Integration

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Continuous Integration (CI) je pracovný a technický model, v ktorom sa malé zmeny často skladajú do spoločnej hlavnej línie a každý kandidátny integračný stav dostane automatizovaný, reprodukovateľný a auditovateľný verdict.

```text
malá source zmena
→ presný candidate integration state
→ čistý a reprodukovateľný build
→ vrstvené verification evidence
→ immutable artifact
→ merge alebo oprava
→ zdravá mainline
```

CI nie je iba server spúšťajúci testy. Jeho základnou jednotkou je **integračné rozhodnutie**: môžeme tento konkrétny výsledný tree bezpečne pridať k aktuálnemu spoločnému stavu?

## 1. Cieľ kapitoly

Nosný model kapitoly je candidate-evidence lifecycle:

```text
source change a target main
→ candidate identity
→ trusted checkout a explicitné build inputs
→ compile/test/contract/policy evidence
→ complete aggregation
→ immutable artifact a provenance
→ fresh merge decision
→ mainline health alebo urgent recovery
→ defect escape späť do dependency/test/policy modelu
```

Zelený branch, úspešný lokálny build ani starý pipeline run samy osebe neodpovedajú na integračnú otázku. Dôkaz musí patriť presnému kandidátovi, aktuálnemu targetu a autoritatívnej workflow policy.

## 2. Nosný scenár: Atlas Orders 3.10.0

Atlas pripravuje dve paralelné zmeny:

- **PR A** pridáva `priority` do `OrderCreated` eventu a aktualizuje generated client;
- **PR B** mení retry klasifikáciu workeru a jeho dependency lockfile;
- `main` medzitým aktualizuje spoločný serialization package.

Integračný chain je:

```text
PR source SHA
+ aktuálny main SHA
+ workflow definition a toolchain
→ synthetic merge candidate
→ build orders-api a payment-worker
→ contract a compatibility checks
→ tests a security policy
→ package image digest
→ merge decision
```

CI musí overiť výsledný spoločný stav, nie tri izolované branches testované proti starším predpokladom.

## 3. Mainline ako integračný kontrakt

`main` reprezentuje najnovší akceptovaný spoločný stav. Nemusí byť automaticky releasnutý, ale musí byť dôveryhodným vstupom pre ďalší delivery proces.

Mainline invariants:

- source a dependency metadata tvoria konzistentný tree;
- autoritatívny build sa dá zopakovať v deklarovanom prostredí;
- required evidence je complete a fresh;
- artifact identity je previazaná na candidate a pipeline;
- chýbajúci shard, report alebo scanner nie je pass;
- broken main má urgentného ownera a recovery policy.

Zelená ikona bez candidate identity, evidence completeness a workflow freshness nie je integračný kontrakt.

## 4. Malý batch a častá integrácia

Dlhodobá branch akumuluje integračný dlh:

```text
zmena vzniká proti starému main
→ ďalší kód začne závisieť od lokálnych assumptions
→ target a dependencies sa menia
→ merge vytvorí nový neoverený stav
→ failure má veľa možných príčin
```

Atlas rozdeľuje veľkú capability cez backward-compatible schema, branch by abstraction, feature flag a oddelený destructive cleanup. Menší batch znižuje počet assumptions, review scope, merge conflicts aj rollback blast radius.

Skrytý feature path však stále musí byť buildable, bezpečný a kompatibilný. Flag nie je výnimka z CI invariants.

## 5. Candidate identity

Pipeline musí explicitne rozlišovať:

- source branch SHA;
- target branch SHA;
- synthetic merge alebo rebased candidate SHA;
- merge-queue group SHA;
- workflow definition revision;
- tag alebo release commit, ak je relevantný.

Atlas PR A môže byť zelený proti `main=M1`, ale po merge PR B vznikne `M2`. Pôvodný výsledok A už nepreukazuje kompatibilitu s M2.

```text
A green against M1
B green against M1
B merged → M2
A merged without revalidation
→ A + B combination nikdy nebola testovaná
```

Dôveryhodný verdict sa invaliduje pri zmene targetu, candidate tree alebo required policy.

## 6. Merge-result testing a merge queue

Merge-result pipeline testuje tree, ktorý by po integrácii skutočne vznikol. Atlas tým overí:

- kombinovaný dependency graph a lockfile;
- generated client po event schema zmene;
- semantic compatibility API a workeru;
- spoločný build a test corpus;
- policy nad výsledným repository stavom.

Merge queue potom vytvára predpokladaný budúci main:

```text
approved PR
→ queue position
→ candidate against queue predecessor
→ required evidence
→ merge
→ invalidation/rebuild ďalšieho kandidáta
```

Queue rieši race medzi paralelne zelenými PRs. Nenahrádza však úplný dependency graph ani kvalitné oracles.

## 7. Autoritatívny CI lifecycle

Atlas workflow:

```text
resolve event, source, target a candidate
→ clean checkout
→ restore pinned toolchain a dependencies
→ fast static/schema checks
→ build binaries
→ unit/integration/contract tests
→ package jeden immutable artifact
→ artifact/SBOM/signature policy
→ aggregate complete evidence
→ publish candidate verdict
```

DAG môže nezávislé kontroly paralelizovať. Artifact-dependent checks však musia pracovať s rovnakým build outputom, ktorý sa publikuje. Rebuild po testoch by vytvoril nový supply-chain event.

## 8. Reprodukovateľný build

Build inputs sú širšie než source:

```text
commit a submodules
+ dependency lockfiles
+ compiler/SDK/build image
+ build flags a environment
+ generated-code tools
+ architecture, locale a timezone
+ pipeline templates/actions
+ povolené network-fetched inputs
→ artifact bytes
```

Implicitný host toolchain, mutable base image alebo nezamknutá dependency znamenajú, že rovnaký commit nemusí vytvoriť rovnaký výsledok.

Atlas pinne build image digest, package lock a schema generator. Cold build musí fungovať bez lokálneho workspace stateu.

## 9. Build once a immutable artifact

Odporúčaný model:

```text
candidate C
→ build artifact digest A
→ verify A
→ publikovať A s provenance
→ neskôr promovať ten istý A
```

Artifact record obsahuje minimálne:

- digest a registry location;
- source a candidate SHA;
- build workflow a runner image;
- dependency/toolchain metadata;
- SBOM a signature podľa risku;
- evidence bundle a retention;
- verification status.

Environment-specific konfigurácia sa od artifactu oddeľuje. Rebuild „pre staging“ alebo „pre produkciu“ ruší väzbu medzi testovanými a nasadenými bytes.

## 10. Evidence a complete verdict

CI produkuje rozhodovací dôkaz:

- compile a test reports vrátane first-attempt výsledku;
- coverage a mutation evidence;
- contract compatibility;
- SAST, SCA a secret findings;
- SBOM, checksums a provenance;
- candidate/target identity;
- runner, tool a policy versions;
- očakávaný a skutočný shard manifest.

Verdict rozlišuje:

```text
PASS
→ všetky required controls sa vykonali a splnili oracle

CHANGE_FAILURE
→ kód, contract alebo policy je porušená

INCOMPLETE
→ chýba shard, report, artifact alebo required input

TOOL/INFRA_FAILURE
→ control sa nedal dôveryhodne vykonať

CANCELED/SUPERSEDED
→ run už nereprezentuje aktuálny candidate
```

Chýbajúci report ani analyzer crash nie sú zelený výsledok.

## 11. Cache ako optimalizácia

Cache nesmie byť hidden source of truth. Kľúč musí zohľadniť relevantné inputs: OS, architecture, toolchain, lock hash, flags a config.

Atlas oddelí cache namespace pre untrusted PRs od trusted buildov. Pipeline periodicky robí cold-cache build.

Riziká:

- stale output po neúplnej invalidácii;
- cache poisoning z nedôveryhodného kódu;
- cross-project contamination;
- warm build, ktorý maskuje chýbajúci generated step;
- privileged artifact obnovený v untrusted jobe.

Cache miss má znížiť výkon, nie correctness.

## 12. Trust boundaries

Atlas rozdeľuje workflow:

```text
untrusted PR verification
→ read source, bez production secrets

trusted build po policy boundary
→ write iba do candidate artifact namespace

artifact verification/signing
→ read immutable artifact, samostatná identity

deployment
→ environment-scoped short-lived identity
```

PR code môže meniť scripts a pokúsiť sa čítať credentials alebo poisonovať shared state. Preto sa untrusted code nespúšťa na persistent privileged runneri s produkčným network accessom.

Workflow definitions a reusable actions sú privilegovaný software. Potrebujú review, pinning a ownership.

## 13. Runner isolation a capacity

Runner je execution, trust a capacity boundary. Atlas používa:

- ephemeral pool pre untrusted verification;
- samostatný trusted build pool;
- protected deploy pool bez spúšťania PR source;
- short-lived workload identity;
- explicitné network egress a resource limits.

Container poskytuje izolovaný userspace, ale zdieľa kernel. Persistent shell runner môže zachovať workspace, procesy, credentials a poisoned cache. Executor sa volí podľa trust levelu, nie iba startup času.

## 14. Gates, retry a flakiness

Blocking gate musí chrániť významný risk a byť presný, reprodukovateľný, complete, akčný a vlastnený. Nový alebo heuristický signal môže začať advisory s maturity plánom.

Retry je vhodný pre identifikovaný transient transport alebo runner provisioning failure. Nie pre compile error, contract incompatibility alebo neznámy test failure.

Atlas zachováva každý attempt:

```text
first attempt failure
→ diagnostický rerun
→ final classification
```

Pass-after-retry nie je pass-on-first-attempt. Quarantine mení gate policy dočasne; neodstraňuje root cause.

## 15. Worked failure: dva zelené PRs rozbili main

PR A pridal optional event field a regeneroval client. PR B aktualizoval serialization package, ale každý bol testovaný iba proti M1:

```text
A/M1 green
B/M1 green
B merged → M2
A merged bez merge-result pipeline
→ generated client a nový serializer vytvorili odlišný enum representation
→ payment-worker nevedel deserializovať nové eventy
→ main pipeline zlyhala až po merge
```

### Root cause

Branch status sa zamieňal za integračný verdict. Required checks neboli viazané na synthetic merge candidate voči aktuálnemu targetu.

### Náprava

- merge-result pipeline a merge queue;
- candidate SHA v reports a artifact provenance;
- invalidácia pri zmene target SHA;
- contract replay s historickými aj novými event fixtures;
- urgent broken-main revert a následná regression edge v dependency modeli.

## 16. Worked failure: warm cache vytvorila false green

Generated API client nebol deklarovaný ako build dependency. Persistent runner ho mal zo staršieho jobu:

```text
warm workspace obsahoval generated client
→ build a tests green
→ clean release runner nemal generated output
→ package chýbal potrebný module
→ publication zlyhala
```

### Root cause

Workspace/cache boli nezdokumentovaným build inputom. Pipeline netestovala cold invariant a cleanup nebol spoľahlivý.

### Náprava

- ephemeral clean workspace;
- generated step je explicitný DAG predecessor;
- artifact transfer nahrádza implicitný filesystem state;
- cold-cache periodic job;
- build manifest obsahuje generated-tool version a output checksum.

## 17. Broken main recovery

Pri zlyhaní autoritatívneho main candidate:

```text
main marked broken
→ zastaviť ďalšie rizikové merges
→ identifikovať first bad integration a failure class
→ revert alebo minimálny roll-forward fix
→ znovu vytvoriť complete artifact/evidence
→ overiť downstream consumers
→ opraviť kontrolu, ktorá failure prepustila
```

Dlhodobo červený main ničí význam spoločného contractu. Recovery má prednosť pred novou feature prácou podľa explicitnej policy.

## 18. Výkon CI feedback loopu

CI optimalizuje čas k užitočnému rozhodnutiu:

- queue time;
- time to first useful feedback;
- critical-path duration;
- merge-queue wait a invalidation rate;
- shard imbalance a fan-in time;
- canceled/superseded execution;
- cache benefit verzus cold-build reliability;
- flaky, tool a infrastructure failure rate;
- čas broken main.

Viac paralelných jobs nemusí skrátiť critical path a môže zvýšiť runner contention alebo quotas.

## 19. Diagnostický postup

Pri CI failure:

1. Potvrď source, target, candidate a workflow revision.
2. Klasifikuj change, flaky, tool, infrastructure alebo incomplete failure.
3. Over checkout tree, submodules, LFS a generated files.
4. Porovnaj runner image, architecture, resources, locale a network.
5. Skontroluj lockfiles, cache key a cold-cache reprodukciu.
6. Potvrď očakávaný shard/report manifest.
7. Zachovaj logs, reports, core dumps a artifact metadata prvého attemptu.
8. Reprodukuj najmenší job s rovnakými deklarovanými inputs.
9. Pri merge failure analyzuj synthetic merge tree, nie iba source branch.
10. Oprav root cause a potvrď first-attempt green nový candidate.
11. Ak failure unikol na main, oprav dependency/test/policy model.

## 20. Referenčné pravidlá

- CI chráni candidate integration state, nie branch label.
- Required evidence sa viaže na source, target, candidate a workflow revision.
- Mainline má byť trvalo buildable a dôveryhodná.
- Merge-result testing a queue riešia stale-green race.
- Build inputs musia byť explicitné a cold-reproducible.
- Buildni raz a ďalej používaj rovnaký immutable digest.
- Cache a workspace nie sú source of truth.
- Untrusted verification, signing a deployment majú oddelené identities.
- Incomplete alebo tool failure nie je pass.
- Retry zachová first-attempt evidence a je viazaný na transient class.
- Broken main sa obnovuje urgentne.
- Defect escape mení test selection, dependency graph alebo policy.

## 21. Časté omyly

### „PR bol zelený“

Bez target a candidate identity nevieme, či výsledok platí pre skutočný merge.

### „CI je nočný build“

Neskorý veľký batch nevytvára krátku integračnú feedback loop.

### „Rovnaký source znamená rovnaký artifact“

Toolchain, dependencies, base image a build environment môžu vytvoriť iné bytes.

### „Cache failure je iba performance problém“

Ak build potrebuje cache na correctness, cache sa stala skrytým vstupom.

### „Container runner je automaticky bezpečný“

Privileged mounts, shared kernel, credentials a network access stále určujú trust boundary.

### „Rerun prešiel, pipeline je zelená“

Fail-then-pass je evidence flakiness alebo intermittency, nie čistý prvý verdict.

## 22. Zhrnutie

Dôveryhodné CI pre Atlas je:

```text
malá zmena
→ aktuálny merge candidate
→ čistý pinned build context
→ complete layered evidence
→ jeden immutable artifact
→ fresh integration verdict
→ zdravý main alebo urgent recovery
→ uniknutý failure späť do control modelu
```

CI skracuje integračný feedback a udržiava spoločnú líniu ako dôveryhodný vstup pre Continuous Delivery. Neoptimalizuje počet pipeline behov; optimalizuje kvalitu a rýchlosť integračného rozhodnutia.

## 23. Kontrolné otázky

1. Prečo je integračné rozhodnutie základnou jednotkou CI?
2. Aký je rozdiel medzi source SHA, target SHA a candidate SHA?
3. Aký stale-green race rieši merge-result pipeline?
4. Ako merge queue vytvára predpokladaný budúci main?
5. Ktoré inputs patria do reprodukovateľného buildu?
6. Prečo build-once podporuje dôveryhodnú promotion?
7. Ako complete evidence odlišuje pass od incomplete runu?
8. Prečo cache a persistent workspace nesmú byť source of truth?
9. Ako Atlas oddeľuje untrusted verification, build, signing a deployment?
10. Kedy je retry legitímny a čo musí zachovať?
11. Ako vznikol Atlas failure dvoch individuálne zelených PRs?
12. Ako sa obnovuje broken main a zlepšuje control model?

## Glossary impact

Relevantné pojmy: Continuous Integration, mainline, integration decision, candidate SHA, merge-result pipeline, synthetic merge commit, merge queue, reproducible build, build once, immutable artifact, evidence provenance, complete evidence, cold build, runner isolation, broken main, critical path a time to first useful feedback.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Chaos testing](../04-testing-and-quality/chaos-testing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Continuous Delivery →](continuous-delivery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
