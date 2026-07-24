# Trigger, artifact a cache

Pipeline potrebuje vedieť tri rozdielne veci:

```text
prečo a v akom trust contexte sa spustila
→ aký identifikovateľný výstup vytvorila
→ ktoré odstrániteľné dáta môže znovu použiť na zrýchlenie práce
```

Trigger, artifact a cache riešia odlišné problémy. Trigger vytvára runtime context a rozhoduje, čo sa má vykonať. Artifact je dôveryhodný výstup viazaný na konkrétne vstupy a evidence. Cache je oportunistická optimalizácia, ktorá nesmie byť potrebná na correctness workflowu.

## 1. Mental model

Celý lifecycle možno opísať takto:

```text
event alebo explicitný príkaz
→ autentizácia a authorization triggeru
→ resolution repository/ref/SHA a workflow verzie
→ pipeline run
→ build a verification
→ immutable artifact + reports + provenance
→ promotion alebo distribúcia

medzitým:
cache lookup
→ bezpečný restore
→ validation/recompute
→ prípadný cache write
```

Najdôležitejšie invariants:

- **Trigger context je explicitný —** rovnaký YAML nemusí mať rovnaké permissions pri fork pull requeste a protected tage.
- **Build input je jednoznačný —** branch name nestačí; rozhodujúci je resolved commit alebo synthetic merge-result SHA.
- **Artifact je identifikovaný obsahom —** digest je stabilnejší než mutable tag alebo názov súboru.
- **Promotion nemení bytes —** staging a produkcia dostávajú ten istý overený artifact.
- **Cache je postrádateľná —** cold run musí zostať korektný.
- **Evidence je úplná —** chýbajúci report, shard alebo attestation nie je automaticky pass.

## 2. Trigger ako vytvorenie pipeline runu

Trigger je udalosť alebo autorizovaný príkaz, ktorý vytvorí konkrétnu runtime inštanciu workflowu. Pipeline definícia je šablóna; trigger dodá event payload, identity, source revision, variables, permissions a časový kontext.

Typické trigger typy:

- **Push —** nový commit alebo ref update na branchi.
- **Pull/merge request —** otvorenie, synchronizácia, zmena targetu alebo approval event.
- **Tag alebo release event —** vytvorenie release candidate alebo produkčného release toku.
- **Schedule —** periodický regression, drift, expiry alebo cleanup workflow.
- **Manual dispatch —** explicitné spustenie človekom s validovanými vstupmi.
- **API alebo webhook —** externý systém vyžiada workflow cez autentizované rozhranie.
- **Parent/upstream pipeline —** iný workflow odovzdá artifact, metadata alebo rozhodnutie.
- **Repository dependency event —** zmena shared library, schema alebo base image vyvolá downstream validáciu.
- **Deployment/environment event —** post-deploy verification, promotion alebo rollback workflow.

Trigger neurčuje iba „kedy“. Určuje aj trust level, authoritative SHA a povolené side effects.

## 3. Runtime context triggeru

Každý run má minimálne tieto vstupy:

- repository a workflow path,
- workflow revision,
- event type a event ID,
- actor alebo service identity,
- source ref a target ref,
- resolved source SHA,
- synthetic merge-result SHA, ak existuje,
- environment alebo deployment target,
- typed inputs,
- token permissions a secret scope,
- concurrency group,
- timestamps a run ID.

Dôležité je rozlišovať workflow revision od application revision. Niektoré platformy pri pull requeste vykonajú workflow z target branchu, iné zo source branchu alebo kombinácie. To je security aj reproducibility rozhodnutie.

## 4. Event payload nie je automaticky dôveryhodný

Event payload môže obsahovať údaje kontrolované nedôveryhodným používateľom:

- branch a tag name,
- commit message,
- pull-request title alebo body,
- actor display name,
- custom input,
- changed path,
- issue comment,
- repository alebo artifact URL.

Tieto hodnoty nesmú byť priamo interpolované do shellu, filesystem pathu, Kubernetes resource name, cloud role name alebo SQL query.

Bezpečný postup:

1. načítaj hodnotu ako dátový argument, nie ako shell fragment;
2. validuj typ, formát, dĺžku a allowlist;
3. používaj argument arrays alebo bezpečné API klienty;
4. canonicalizuj path a kontroluj boundary;
5. nikdy neodvodzuj privileged environment iba z user-controlled stringu;
6. loguj identifikátor bezpečne bez secrets a control characters.

Quoting znižuje injection riziko, ale nenahrádza authorization. Hodnota `production` môže byť syntakticky bezpečná a stále neoprávnená.

## 5. Push pipeline verzus merge-request pipeline

Push pipeline typicky overuje branch tip. Pull/merge-request pipeline môže overovať viac revízií:

- source branch SHA,
- pull-request head SHA,
- synthetic merge commit vytvorený proti target branchu,
- merge queue alebo merge train candidate,
- rebase candidate.

Najsilnejší integračný dôkaz sa viaže na bytes, ktoré sa skutočne dostanú do mainline. Branch-tip pass môže byť neplatný po zmene target branchu.

Príklad freshness problému:

```text
PR A prejde proti main M1
→ PR B sa merge-ne a vytvorí M2
→ výsledok A už nehovorí nič o integrácii A + M2
```

Ochrany:

- testovať synthetic merge result,
- invalidovať approval a checks pri zmene targetu alebo source SHA,
- používať merge queue,
- zaznamenať candidate SHA vo všetkých reports,
- odmietnuť merge, ak status patrí staršiemu SHA.

## 6. Trigger deduplikácia

Rovnaká zmena môže spustiť push, pull-request a upstream pipeline. Bez explicitnej policy vznikajú:

- duplicitné náklady,
- viac statusov pre rovnaké rozhodnutie,
- racing artifact uploads,
- paralelné deploymenty,
- nejasný authoritative result,
- cache contention.

Workflow rules majú definovať:

- ktorý event vytvára validation pipeline,
- ktorý event vytvára release pipeline,
- či push na branch s otvoreným PR zruší alebo nespustí duplicitný run,
- ktorý run publikuje required status,
- ako sa deduplikuje event s rovnakým delivery ID,
- ako sa spracuje replay webhooku.

Idempotency key môže byť napríklad kombinácia repository, event ID, candidate SHA a workflow version.

## 7. Supersession a cancellation

Novší commit môže znížiť hodnotu staršieho validation runu. Concurrency policy môže starší run zrušiť, ale cancellation musí rešpektovať side effects.

Bezpečné pravidlá:

- read-only validation možno agresívne cancelovať;
- artifact publishing musí zabrániť prepísaniu immutable identity;
- deployment alebo migration job sa nesmie prerušiť bez cleanup/reconcile mechanizmu;
- cancellation musí uploadnúť failure artifacts, ak je to možné;
- superseded result nesmie zostať authoritative pre nový SHA;
- release signing alebo promotion sa má serializovať podľa artifact/environmentu.

## 8. Path-based triggers

Monorepo môže spúšťať iba affected workloads:

```text
services/api/**
→ API build a tests

services/web/**
→ frontend build a tests
```

Jednoduché glob patterns však nemusia zachytiť:

- shared library alebo schema zmenu,
- build tool, lockfile alebo root config,
- generated code,
- rename alebo delete,
- implicitnú runtime dependency,
- base image alebo infrastructure module,
- zmenu workflow template.

Bezpečnejší model používa dependency graph a conservative fallback:

```text
presný affected graph
→ targeted pipeline

neznáma alebo root-level zmena
→ širší validation set
```

Selection mechanizmus sám potrebuje tests a incident review pri false-green výsledku.

## 9. Scheduled pipelines

Schedule je vhodný pre kontroly, ktorých hodnota závisí od času alebo širokého scope:

- full regression,
- dependency a base-image refresh,
- certificate, token alebo secret expiry,
- drift detection,
- periodický security scan,
- restore alebo resilience exercise,
- cleanup orphan resources,
- cache cold-run verification.

Schedule nesmie byť jediná ochrana pre failure, ktorý má blokovať merge. Nočný compile alebo contract test je príliš neskorý na ochranu mainline.

Scheduled run musí explicitne určiť source revision. „Latest main at start time“ je validný model, ale musí byť zaznamenaný resolved SHA, aby bol výsledok reprodukovateľný.

## 10. Manual dispatch

Manual trigger je používateľské API. Potrebuje typed inputs, authorization a audit trail.

Príklad vstupného kontraktu:

```text
environment: staging | production
artifact_digest: sha256:<64 hex chars>
change_ticket: non-empty identifier
strategy: canary | rolling | blue-green
```

Kontroluj:

- caller identity a role,
- environment allowlist,
- artifact existenciu a podpis,
- artifact eligibility pre dané prostredie,
- approval freshness,
- concurrency lock,
- input length a canonical form,
- timeout/expiry manuálneho requestu.

Manual dispatch nemá povoliť rebuild z ľubovoľného branch name pre produkciu. Produkčný krok má vyberať už existujúci overený digest.

## 11. API a webhook triggers

Externý trigger potrebuje:

- autentizáciu odosielateľa,
- signature verification payloadu,
- ochranu proti replayu,
- event ID deduplikáciu,
- timestamp alebo nonce policy,
- schema validation,
- rate limit,
- bezpečnú odpoveď bez citlivých detailov.

HTTP 2xx na webhook neznamená, že pipeline bola vytvorená presne raz. Receiver musí definovať idempotency a retry semantics.

## 12. Trigger permissions

Permissions majú byť odvodené z trust contextu a konkrétnej úlohy, nie iba z názvu workflowu.

Príklad:

| Trigger context | Typický trust | Povolenia |
|---|---|---|
| Fork pull request | nedôveryhodný kód | read-only source, bez secrets a protected cache write |
| Internal branch | čiastočne dôveryhodný | build/test, obmedzený artifact publish |
| Protected main | dôveryhodný ref po gates | publish immutable artifact, signing podľa policy |
| Protected tag | release identity | release metadata a podpis, nie automaticky production deploy |
| Manual production promotion | autorizovaný actor | environment-scoped short-lived deploy identity |
| Schedule | service identity | iba presne definovaný scope |

Rovnaký YAML môže spúšťať nedôveryhodný kód. Preto secrets a privileged tokens musia byť vydávané až po overení trigger contextu a ref policy.

## 13. Artifact

Artifact je versionovaný, identifikovateľný výstup workflowu určený na ďalšie overenie, distribúciu, deployment alebo audit.

Príklady:

- container image,
- binary alebo language package,
- archive alebo installer,
- Helm chart alebo rendered deployment bundle,
- SBOM,
- provenance attestation,
- signature,
- test a scan report,
- generated documentation,
- database migration bundle.

Nie všetky artifacts majú rovnakú dôveru. Pull-request build môže byť diagnostický artifact, ale nemusí byť eligible na produkčnú promotion.

## 14. Artifact state model

Artifact môže prechádzať stavmi:

```text
built
→ verified
→ signed/attested
→ release candidate
→ promoted to environment
→ released
→ retained / deprecated / revoked
```

Stav nemá byť odvodený iba z mutable tagu. Promotion record má ukázať:

- digest,
- source a workflow identity,
- evidence bundle,
- policy version,
- approval alebo automated decision,
- environment a timestamp,
- aktuálny release/rollback status.

Revoked artifact musí zostať identifikovateľný, ale policy má zabrániť ďalšej promotion.

## 15. Build once, promote many

Správny model:

```text
source commit + pinned build inputs
→ build
→ immutable artifact digest A
→ verification
→ staging deployment A
→ production deployment A
```

Nesprávny model:

```text
source commit
→ staging build A
→ neskorší production rebuild B
```

Rebuild môže zmeniť:

- dependency resolution,
- base image,
- compiler alebo linker,
- timestamp a generated metadata,
- external download,
- build environment,
- nondeterministické poradie.

Ak produkcia dostane B, staging evidence pre A nie je dôkazom produkčného artifactu.

## 16. Artifact identity

Silná identity obsahuje content digest. Ďalšie metadata vysvetľujú pôvod:

- immutable version,
- source repository a commit SHA,
- workflow a pipeline run ID,
- builder identity,
- toolchain a base-image digests,
- dependency graph alebo lock identity,
- timestamp,
- SBOM,
- provenance a signature.

Tag `latest`, branch name alebo filename nie sú content identity. Môžu byť convenience aliases, ale deployment record má vždy zachovať resolved digest.

## 17. Integrity, authenticity a provenance

Tieto pojmy nie sú totožné:

- **Integrity —** bytes sa od merania hashu nezmenili.
- **Authenticity —** podpis alebo identity dokazuje, kto artifact schválil alebo vytvoril.
- **Provenance —** zaznamenáva source, workflow, builder, materials a build podmienky.
- **Policy compliance —** overuje, či dôkaz spĺňa organizačné pravidlá.

Hash publikovaný spolu s kompromitovaným artifactom poskytuje identity, nie dôveryhodnosť. Dôveryhodný deploy verifikuje podpis/attestation voči schválenej identity a policy.

## 18. Artifact repository alebo registry

Durable artifact store má poskytovať:

- immutable upload alebo version protection,
- content-addressable identity,
- access control,
- checksums a signature metadata,
- retention a legal hold,
- vulnerability alebo policy scanning,
- replication a availability,
- audit log,
- garbage collection s referenčnou ochranou,
- promotion alebo release metadata.

Pipeline-local artifacts sú vhodné pre krátkodobú diagnostiku. Produkčný binary, image alebo package potrebuje registry lifecycle nezávislý od retention jedného pipeline runu.

## 19. Artifact retention

Retention musí zohľadniť účel:

- ephemeral debug logs,
- pull-request artifacts,
- test reports,
- release candidates,
- produkčné releases,
- rollback versions,
- SBOM a provenance,
- compliance evidence,
- artifacts pod legal holdom.

Dôležité invariants:

- rollback artifact neexpiruje pred podporovaným rollback window;
- release evidence prežije auditnú dobu;
- deletion rešpektuje references z deployment history;
- revokovaný artifact sa nezmaže skôr, než je incident vyšetrený;
- secrets a osobné dáta sa do artifactov vôbec nemajú dostať.

Retention nie je iba storage-cost nastavenie. Je súčasť recovery a auditability.

## 20. Reports ako evidence artifacts

Reports môžu byť interpretované platformou a zároveň uložené ako súbory:

- JUnit,
- coverage,
- SAST/SCA,
- SBOM,
- performance result,
- policy decision,
- deployment verification,
- provenance bundle.

Pri failure sa majú uploadnúť cez `always`/equivalent semantics. Ak test job zlyhá a report sa stratí, pipeline síce blokuje, ale diagnostika a audit trail sú slabé.

Report musí obsahovať candidate/artifact identity. Agregovaný report bez SHA alebo digestu sa môže omylom priradiť k inému runu.

## 21. Artifact fan-out a fan-in

Jeden immutable artifact môže byť vstupom pre paralelné kontroly:

```text
artifact digest A
├─> malware/SCA scan
├─> SBOM a provenance verification
├─> component tests
├─> deployment do ephemeral environment
└─> performance validation
```

Fan-in promotion job musí overiť:

- všetky povinné výsledky patria digestu A,
- žiadny shard/report nechýba,
- evidence je čerstvá podľa policy,
- tool failures nie sú interpretované ako pass,
- artifact nebol medzičasom revoked.

## 22. Cache

Cache je optimalizácia na znovupoužitie draho získaných alebo vypočítaných dát. Môže obsahovať:

- downloaded packages,
- compiler cache,
- build-system intermediate state,
- container layers,
- package-manager metadata,
- test discovery alebo analysis cache.

Cache môže byť missing, stale, evicted, corrupt, partially restored alebo nedostupná. Workflow musí zostať korektný po jej úplnom odstránení.

## 23. Artifact verzus cache

| Vlastnosť | Artifact | Cache |
|---|---|---|
| Účel | dôveryhodný výstup alebo evidence | zrýchlenie |
| Identity | explicitný digest/verzia | cache key a namespace |
| Downstream correctness | môže byť autoritatívny vstup | nesmie byť nevyhnutná |
| Retention | release, rollback a audit lifecycle | oportunistická |
| Immutability | typicky povinná | často nahraditeľná |
| Missing stav | môže blokovať workflow | má viesť k recompute |
| Trust | overený pôvod a policy | opatrný restore a validation |

Build output, ktorý bude nasadený, nemá byť publikovaný iba ako cache.

## 24. Cache key

Cache key musí reprezentovať všetky relevantné vstupy ovplyvňujúce obsah:

```text
trust namespace
+ OS image/digest
+ architecture
+ runtime/toolchain version
+ lockfile hash
+ build flags
+ relevant config/schema
```

Slabý key:

```text
python-dependencies
```

Silnejší key:

```text
trusted-main-linux-amd64-python-3.12-${hash(requirements.lock)}
```

Key nemá obsahovať secret. Cache metadata a názvy sú často viditeľné širšiemu okruhu než secret store.

## 25. Exact a fallback restore

Bezpečný restore lifecycle:

1. vypočítaj exact key;
2. hľadaj cache v správnom trust namespace;
3. prípadne použi obmedzený fallback;
4. validuj alebo znovu vyrieš dependencies podľa lockfileu;
5. vykonaj build/test;
6. pri úspechu ulož nový exact cache;
7. nepublikuj cache z neúspešného alebo nedôveryhodného runu do privileged namespace.

Fallback je vhodný napríklad na downloaded packages. Nie je vhodný na slepé použitie starého generated code alebo compiled outputu bez správnej invalidácie.

## 26. Cache poisoning

Cache poisoning vzniká, keď nedôveryhodný run zapíše obsah, ktorý neskôr použije privileged workflow.

Attack path:

```text
fork PR vykoná útočníkov kód
→ zapíše shared cache
→ protected main obnoví cache
→ vykoná poisoned binary/script s privileged tokenom
```

Ochrany:

- oddelené namespaces podľa trust levelu,
- fork a untrusted runs nemôžu zapisovať protected cache,
- privileged run používa read-only alebo provenance-aware cache,
- package integrity sa verifikuje,
- executable cache obsah sa nepoužíva bez validation,
- cache key zahŕňa toolchain a lock identity,
- secrets nikdy nie sú súčasťou cached filesystemu,
- persistent runner workspace sa nepovažuje za cache bez explicitnej policy.

## 27. Cache write timing

Cache sa nemá ukladať automaticky po každom neúspešnom jobe. Partial alebo corrupt stav môže kontaminovať ďalšie runs.

Definuj:

- ktorý job je writer,
- či write nastáva iba po úspešnej validation,
- ako sa rieši race viacerých writerov,
- či je cache immutable per exact key,
- kto môže cache mazať alebo invalidovať,
- ako sa deteguje incomplete upload.

Pri content-addressed caches môže viac writerov bezpečne publikovať rovnaký obsah, ale mutable branch cache potrebuje serializáciu alebo last-writer policy s dôsledkami.

## 28. Partial restore a validita

Cache restore môže skončiť úspešne na úrovni API, ale obsah môže byť neúplný. Pipeline má vedieť rozlíšiť:

- exact hit,
- fallback hit,
- partial/corrupt restore,
- miss,
- cache backend failure.

Po restore over:

- očakávané manifesty alebo metadata,
- checksumy, ak sú dostupné,
- kompatibilitu toolchainu,
- lockfile resolution,
- permissions a ownership,
- absenciu neočakávaných executable paths.

## 29. Cache invalidation

Invalidáciu vyžaduje zmena:

- dependency lockfileu,
- toolchainu alebo compileru,
- base OS/container image,
- architecture,
- build flags,
- relevantných environment variables,
- generatora alebo schema,
- build-system verzie,
- security/trust policy.

Príliš široký key znižuje hit rate. Príliš úzky key vytvára stale a nereprodukovateľné failures. Rozhodnutie má byť podložené modelom build inputs.

## 30. Dependency cache verzus dependency policy

Cache urýchľuje download. Dependency correctness definujú:

- lockfile,
- version constraints,
- checksums/signatures,
- schválené registry,
- vendoring policy,
- vulnerability a license rules.

Cache nesmie nahradiť resolver ani integrity verification. Cold run musí stiahnuť rovnaký povolený graph.

## 31. Container layer cache

Container build cache znovu používa layers podľa build instruction a context identity. Riziká:

- mutable base tag,
- secret zapísaný do layeru,
- príliš široký alebo nestabilný build context,
- stale package index,
- cross-project reuse,
- privileged builder contamination,
- nepresná invalidácia `COPY` krokov.

Ochrany:

- base image pinovaný digestom,
- secret mounts namiesto `ARG`/`COPY`,
- minimálny `.dockerignore`,
- oddelený cache scope podľa trustu,
- pravidelný cold rebuild,
- scan finálneho artifactu, nie iba cached layers.

## 32. Cold-run verification

Pipeline, ktorá vždy používa warm cache, môže skrývať chýbajúci dependency declaration alebo nereprodukovateľný build.

Periodicky spusti:

- prázdny dependency cache,
- prázdny compiler cache,
- fresh ephemeral runner,
- clean checkout,
- pinned external inputs.

Porovnaj artifact digest alebo aspoň deklarovanú reproducibility charakteristiku. Cold run je test correctness pipeline, nie výkonová optimalizácia.

## 33. Trigger-to-artifact traceability

Pre každý release musí byť možné odpovedať:

1. ktorý event a actor vytvorili pipeline run;
2. aká workflow revision a policy sa použila;
3. ktorý source alebo merge-result SHA sa buildol;
4. aké build materials a toolchain vstúpili do procesu;
5. ktorý runner/builder identity build vykonal;
6. aký artifact digest vznikol;
7. ktoré reports, signatures a attestations patria digestu;
8. ktoré gates prešli, zlyhali alebo boli waived;
9. do ktorých environments bol artifact promovaný;
10. ktorá verzia je aktuálne released a rollback-eligible.

Toto je základ supply-chain auditability a incident response.

## 34. Failure semantics

Trigger/artifact/cache workflow má rozlišovať:

- **Trigger rejected —** event alebo caller nemal oprávnenie alebo validné vstupy.
- **Duplicate/superseded —** run sa nespustil alebo bol zrušený podľa concurrency policy.
- **Build failure —** artifact nevznikol.
- **Artifact upload failure —** build mohol prejsť, ale autoritatívny output chýba.
- **Evidence incomplete —** report, shard, SBOM alebo attestation chýba.
- **Cache miss —** normálny recompute stav.
- **Cache backend failure —** performance degradácia alebo podľa policy dočasný infra failure.
- **Integrity/authenticity failure —** artifact alebo cache sa nesmie použiť.
- **Retention/deletion conflict —** potrebný release alebo rollback artifact bol odstránený.

Cache miss sa nemá zamieňať s pipeline failure. Chýbajúci release artifact sa naopak nesmie ignorovať.

## 35. Diagnostický postup

### Pipeline sa spustila dvakrát

Over event typy, workflow rules, event ID, branch s otvoreným PR, upstream trigger a concurrency group. Urči, ktorý run publikuje authoritative status a artifacts.

### Testy prešli, ale merge je nebezpečný

Porovnaj source SHA, target SHA a synthetic merge-result SHA. Skontroluj freshness statusu a či merge queue invalidovala staré výsledky.

### Artifact downstream chýba

Over upload job, artifact name/path, retention, permissions, dependency edge, region registry a či upload prebehol pri failure stave.

### Produkcia má iné bytes než staging

Porovnaj digest, nie tag. Hľadaj rebuild, mutable tag, registry replication race alebo nesprávny environment manifest.

### Cache hit spôsobuje chybu

Spusti cold run. Porovnaj key inputs, fallback path, toolchain, lockfile, restore logs a trust namespace. Cache zmaž až po uchovaní evidence, ak môže ísť o poisoning.

### Cache sa nikdy nenájde

Skontroluj key, hashing, OS/arch, namespace, branch policy, retention, upload timing, path a backend connectivity.

## 36. Typické anti-patterny

### Cache je považovaná za artifact

Odstránenie cache potom znemožní build alebo deployment. Autoritatívny output musí mať explicitný artifact lifecycle.

### Mutable tag je jediná identity

Nie je možné dokázať, ktoré bytes boli testované a nasadené.

### Fork pipeline dostane protected cache write a secrets

Nedôveryhodný kód môže kontaminovať privileged workflow alebo odcudziť credentials.

### Schedule nahrádza merge gates

Chyba sa odhalí až po integrácii a mainline zostane červená.

### Manual production trigger prijíma branch name

Produkcia môže rebuildnúť alebo nasadiť neoverený source namiesto schváleného digestu.

### Artifact retention je kratšia než rollback window

Incident recovery nemá dostupnú predchádzajúcu overenú verziu.

### Cache write po failed build-e

Partial state spôsobí následné nejasné failures.

### Trigger result nie je viazaný na SHA

Starý zelený status sa omylom použije pre novú revíziu.

## 37. Praktický checklist

Pred označením workflowu za dôveryhodný over:

- trigger types a authoritative run sú explicitné,
- event payload sa validuje ako nedôveryhodný input,
- trigger permissions zodpovedajú trust contextu,
- webhooky majú signature, replay protection a deduplikáciu,
- candidate SHA a workflow revision sú zaznamenané,
- duplicate a superseded runs majú policy,
- path selection má dependency-aware fallback,
- manual inputs sú typed a autorizované,
- artifact je immutable a identifikovaný digestom,
- build once/promote many je vynútený,
- reports a attestations patria presnému digestu,
- retention pokrýva rollback a audit potreby,
- cache je odstrániteľná a cold run funguje,
- cache namespaces oddeľujú trust levels,
- cache write nastáva iba z vhodného stavu,
- cache key zahŕňa relevantné inputs,
- tool/cache failure sa neinterpretuje ako pass,
- trigger-to-production traceability je dohľadateľná.

## 38. Kontrolné otázky

1. Čo trigger okrem času spustenia definuje?
2. Prečo event payload nemožno automaticky považovať za dôveryhodný?
3. Aký je rozdiel medzi source SHA a synthetic merge-result SHA?
4. Ako vznikajú duplicate pipelines a ktorý výsledok má byť authoritative?
5. Čo znamená superseded run a kedy ho možno bezpečne zrušiť?
6. Prečo path-based trigger potrebuje dependency graph alebo fallback?
7. Ako má byť chránený manuálny produkčný trigger?
8. Aký je rozdiel medzi artifact identity, integrity, authenticity a provenance?
9. Prečo build once, promote many chráni evidence?
10. Aké artifact stavy a retention pravidlá potrebuje release lifecycle?
11. Čím sa artifact líši od cache?
12. Čo musí obsahovať bezpečný cache key?
13. Ako vzniká cache poisoning?
14. Kedy je fallback restore bezpečný?
15. Prečo cache write po neúspešnom jobe môže byť nebezpečný?
16. Čo overuje cold-cache run?
17. Ako fan-in job dokáže úplnosť evidence pre jeden digest?
18. Aké odpovede musí poskytovať trigger-to-artifact traceability?

## Summary

Trigger vytvára pipeline run s konkrétnou identity, revision, permissions a event contextom. Artifact je dôveryhodný, immutable a obsahovo identifikovaný výstup, ktorý sa medzi prostrediami promuje bez rebuildu. Cache je odstrániteľná optimalizácia a musí byť oddelená podľa trustu, správne invalidovaná a bezpečne obnovovaná. Dôveryhodný delivery lifecycle viaže event, candidate SHA, workflow, builder, evidence, artifact digest a environment promotion do jedného auditovateľného reťazca.

## Glossary impact

Relevantné pojmy: trigger, event payload, event replay, pipeline deduplication, superseded run, source SHA, synthetic merge result, manual dispatch, artifact, artifact digest, artifact state, artifact repository, retention, legal hold, integrity, authenticity, provenance, build once promote many, cache, cache key, cache namespace, cache poisoning, fallback restore, cache invalidation a cold build.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Pipeline, stage, job a runner](pipeline-stage-job-runner.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Environment a promotion →](environment-and-promotion.md)
<!-- KNOWLEDGE-NAVIGATION:END -->