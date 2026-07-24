# Reusable a parallel pipelines

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Reusable pipeline component je versionovaný delivery contract, ktorý môže viac consumerov použiť bez kopírovania jeho implementácie. Paralelná pipeline je execution graph, v ktorom sa nezávislé práce vykonávajú súbežne a následne sa ich výsledky bezpečne agregujú.

Reuse a paralelizácia riešia odlišné problémy:

```text
reuse
→ konzistentnosť, ownership, údržba a štandardizácia

parallel execution
→ kratší critical path a rýchlejší feedback
```

Obe techniky môžu zlyhať rovnakým spôsobom: skryjú dependencies a vytvoria false-green výsledok. Reusable template bez explicitného contractu môže rozbiť desiatky repositories. Parallel fan-in bez kontroly úplnosti môže označiť release candidate za zelený, hoci jeden shard vôbec nebežal.

## 2. Mental model: provider, consumer a runtime graph

Reuse má dve organizačné strany:

- **Provider —** tím alebo platforma, ktorá reusable component navrhuje, versionuje, testuje a podporuje.
- **Consumer —** repository alebo workflow, ktorý komponent volá s konkrétnymi inputs, permissions a očakávanými outputs.

Runtime vzniká až po spojení oboch strán:

```text
consumer definition
+ pinned provider version
+ inputs a secrets references
+ platform policy
→ resolved pipeline graph
→ jobs, permissions, artifacts a verdicts
```

Dôveryhodnosť sa preto neviaže iba na source YAML consumera. Potrebujeme poznať aj provider revision, resolved configuration a skutočný graph vykonaný platformou.

## 3. Úrovne reuse

Reuse môže existovať na viacerých úrovniach. Každá má iný contract a blast radius.

- **Library alebo CLI tool —** reusable business alebo deployment logika s explicitným API/CLI kontraktom; môže sa testovať mimo CI platformy.
- **Script —** malá orchestration alebo automation jednotka, ktorú možno spustiť lokálne aj v jobe.
- **Containerized tool —** pinovaný runtime s dependencies; vhodný pre analyzátor, builder alebo release utility.
- **Reusable step/job —** platform-specific execution contract s runtime, permissions, inputs a outputs.
- **Reusable workflow/template —** skladá viac jobs, gates a artifact flows.
- **Child pipeline —** samostatný runtime graph vytvorený parent pipeline.
- **Multi-project workflow —** koordinuje viac repositories alebo delivery domén.
- **Platform capability —** produktizovaný golden path s policy, observability, supportom a lifecycle.

Preferuj najnižšiu úroveň reuse, ktorá poskytne potrebnú hodnotu. Komplexná business logika v centrálnej YAML inheritance vrstve je ťažšie testovateľná než normálny tool s unit testami.

## 4. Reusable script a tool

Script alebo nástroj je vhodný, keď logika nemá byť závislá od konkrétnej CI platformy.

```bash
./scripts/verify.sh
./tools/build --output dist/
./tools/deploy --artifact sha256:... --environment staging
```

Dobrý CLI contract definuje:

- **Inputs —** arguments, environment alebo config file s typmi a validation.
- **Outputs —** stdout pre machine-readable result, stderr pre diagnostics a explicitné files/artifacts.
- **Exit codes —** stabilné rozlíšenie success, validation failure, transient infrastructure failure a usage error.
- **Idempotency —** opakovaný beh s rovnakým inputom nespôsobí nekontrolované duplicity.
- **Timeout/cancellation —** nástroj reaguje na signal a zachová failure evidence.
- **Version identity —** výsledok uvádza verziu toolu a relevantné dependencies.

Pipeline YAML potom ostáva orchestration vrstvou a nemusí kopírovať stovky riadkov shell logiky.

## 5. Reusable job contract

Reusable job je najmenšia platformou plánovaná reusable execution unit. Contract má explicitne uviesť:

- input names, types, defaults a allowed values,
- secret alebo workload-identity requirements,
- runtime image a architecture,
- runner capabilities,
- required network access,
- minimal permissions,
- commands alebo tool entrypoint,
- timeout a retry semantics,
- outputs a ich schema,
- artifacts, reports a retention,
- success, failure, canceled a incomplete behavior,
- supported platform/version matrix,
- ownership a support channel.

Skrytá závislosť na názve branch, repository layout-e alebo implicitnom `latest` image je súčasť contractu, aj keď nie je zdokumentovaná. Práve takéto implicitné assumptions najčastejšie rozbijú consumers.

## 6. Reusable workflow contract

Reusable workflow skladá viac jobs do jednej capability, napríklad:

```text
standard service build
├─> validate source
├─> test
├─> build immutable artifact
├─> generate SBOM/provenance
├─> scan artifact
└─> publish evidence manifest
```

Contract musí definovať nielen inputs a outputs, ale aj systémové vlastnosti:

- **Graph semantics —** ktoré jobs sú povinné, optional alebo conditional.
- **Artifact identity —** ktorý job artifact vytvára a ako consumers dostanú digest.
- **Verdict semantics —** čo znamená overall pass, warn, incomplete alebo tool error.
- **Permission envelope —** maximálne práva, ktoré workflow potrebuje.
- **Secret propagation —** ktoré secrets sa prenášajú a do ktorých jobs.
- **Cancellation —** čo sa stane s child jobs a cleanupom.
- **Observability —** aké deployment/build records a metrics workflow produkuje.
- **Compatibility —** podporované consumer versions a deprecation policy.

## 7. Resolved template identity

Consumer často odkazuje na template fragment, ktorý ďalej zahŕňa ďalšie templates. Zdrojový odkaz preto nemusí stačiť na reprodukciu.

Pre runtime run uchovaj:

- consumer commit SHA,
- reusable workflow alebo template revision,
- všetky transitive include revisions,
- rendered/resolved configuration digest,
- policy revision,
- runner/executor identity,
- input values bez secret materialu,
- effective permissions,
- generated execution graph.

```text
source fragments
→ include/merge/render
→ policy mutation alebo validation
→ resolved graph digest
→ runtime execution
```

Keď pipeline zmení správanie bez diffu v application repository, prvým diagnostickým krokom je porovnať resolved graph a všetky provider revisions.

## 8. Versioning reusable components

Reusable component je dependency. Musí mať immutable identity a kontrolovaný update model.

Možnosti:

- **Commit SHA —** silná immutable identity, ale slabšia ľudská čitateľnosť.
- **Protected immutable tag —** čitateľná release verzia, ak sa tag nedá prepísať.
- **Semantic version —** vyjadruje kompatibilitu contractu, ak provider SemVer disciplinovane používa.
- **Release channel —** napríklad `stable-v2`, ak channel update je auditovaný a consumer pozná riziko pohyblivej referencie.

Floating `main` alebo `latest` môže zmeniť pipeline bez consumer diffu. To je vhodné len v explicitnom centrally managed modeli s canary rolloutom, rollbackom a presnou auditnou stopou.

## 9. Compatibility contract

Breaking change nie je iba odstránenie inputu. Reusable workflow môže byť nekompatibilný aj zmenou behavioru.

Breaking zmeny môžu zahŕňať:

- zmenu default value alebo precedence,
- zmenu artifact name, path alebo media type,
- zmenu output schema,
- zmenu required permissions,
- zmenu runner OS/architecture,
- zmenu timeoutu alebo retry behavioru,
- nový blocking gate,
- zmenu failure alebo cancellation propagation,
- zmenu secret scope,
- zmenu deployment side effects,
- odstránenie podporovanej platformy.

Provider má publikovať contract, changelog, migration guide, deprecation warning a support window. Consumer potrebuje možnosť zostať na starej verzii počas riadenej migrácie.

## 10. Contract negotiation a capability detection

Pri veľkom počte consumerov môže template podporovať viac contract verzií alebo capabilities.

Príklad:

```text
consumer requests:
- contract_version: 2
- artifact_output: oci-digest
- sbom: required
- deploy: disabled
```

Provider má odmietnuť neznámu alebo nepodporovanú kombináciu pred runtime execution. Silent fallback na iný behavior vytvára false confidence.

Capability detection musí byť explicitná. Consumer nemá hádať, že nová output field existuje podľa template tagu alebo nezdokumentovaného job name.

## 11. Centralizácia verzus autonómia

Príliš málo reuse vytvára copy-paste drift. Príliš veľa centralizácie vytvára globálny failure domain a blokuje domain-specific potreby.

Vyvážený model:

- platforma poskytuje opinionated golden paths,
- kritické security a provenance controls sú centrálne enforced,
- service tím vlastní business-specific testy a rollout policy v dovolených hraniciach,
- escape hatch je explicitný, auditovaný a časovo obmedzený,
- consumer môže version pinovať a migrovať v support windowe,
- provider meria adopciu, overrides a failure rate.

Template nemá byť univerzálny framework pre každý workload. Má poskytovať stabilnú capability s jasnou boundary.

## 12. Provider ownership a service model

Reusable pipeline je interný produkt. Provider potrebuje:

- dokumentovaný owner a support channel,
- compatibility a release policy,
- security review a dependency update proces,
- representative test suite,
- usage telemetry,
- incident a rollback runbook,
- deprecation lifecycle,
- SLO pre kritické shared capabilities podľa významu.

Ak template zlyhá a nikto nevie, kto ho opravuje, centralizácia iba presunula problém z repositories do neviditeľného bottlenecku.

## 13. Consumer responsibilities

Consumer nie je pasívny používateľ. Musí:

- pinovať podporovanú provider version,
- validovať inputs a repository assumptions,
- deklarovať potrebné permissions a secrets,
- spracovať outputs podľa contractu,
- sledovať deprecation notices,
- testovať domain-specific behavior,
- vlastniť overrides a exceptions,
- overiť migration pred updateom major version.

Provider nemôže garantovať správnosť aplikačných tests alebo deployment konfigurácie, ktorú consumer odovzdá ako input.

## 14. Parallel execution a critical path

Jobs bez dependency môžu bežať paralelne. Trvanie pipeline určuje najdlhšia dependency cesta, nie súčet runtime všetkých jobs.

```text
lint ────────────────┐
unit tests ──────────┼─> build/package ─> verify artifact ─> release candidate
SAST ────────────────┘
```

Critical path optimalizácia môže:

- odstrániť zbytočné stage barriers,
- začať nezávislé checks skôr,
- rozdeliť veľký suite na shards,
- presunúť reusable setup do pinovaného image,
- znížiť artifact transfer overhead,
- pridať kapacitu bottleneck runner poolu.

Viac paralelizácie však môže zvýšiť total compute, queueing a external-service contention.

## 15. DAG dependencies

DAG edge je execution contract. Znamená, že downstream job potrebuje completion, result alebo artifact konkrétneho upstream jobu.

Rozlišuj:

- **Control dependency —** job môže začať až po výsledku upstreamu.
- **Data dependency —** job potrebuje konkrétny artifact alebo report.
- **Policy dependency —** promotion potrebuje gate verdict alebo approval.
- **Optional dependency —** absence alebo failure je povolený podľa explicitnej policy.

Nesprávny alebo chýbajúci edge môže spustiť deployment pred dokončením security scan-u. Zbytočný edge zas predlžuje critical path bez zvýšenia dôkazu.

## 16. Fan-out

Fan-out rozdelí jeden immutable input na viac nezávislých kontrol:

```text
artifact digest D
├─> Linux verification
├─> Windows verification
├─> arm64 verification
├─> vulnerability scan
└─> signature/provenance verification
```

Každý consumer musí overiť rovnaký digest. Ak jednotlivé branches rebuildujú source alebo čítajú mutable tag, fan-out neoveruje jeden release candidate.

Fan-out manifest má uviesť expected children. To umožní neskôr rozpoznať chýbajúci job alebo shard.

## 17. Fan-in a completeness

Fan-in agreguje paralelné výsledky do jedného rozhodnutia.

```text
expected set
+ received results
+ result identities
+ policy
→ complete verdict
```

Aggregation job musí:

- poznať očakávaný počet a identity výsledkov,
- rozlíšiť required a optional children,
- odmietnuť duplicate alebo výsledok z iného artifactu,
- rozpoznať missing, canceled a timed-out child,
- zachovať first-attempt failure,
- overiť report schema a integrity,
- publikovať overall verdict s provenance.

Zelený fan-in pri chýbajúcom sharde je false success.

## 18. Matrix pipeline

Matrix generuje jobs z kombinácie dimensions:

```yaml
matrix:
  os: [linux, windows]
  runtime: [3.11, 3.12]
```

Výsledný graph je Cartesian product, pokiaľ platforma nepoužíva `include` alebo `exclude` pravidlá.

Matrix contract má definovať:

- support matrix zdroj pravdy,
- required a experimental kombinácie,
- expected job identities,
- concurrency limits,
- fail-fast policy,
- report aggregation,
- update lifecycle pri pridaní alebo odstránení platformy.

## 19. Selective matrix

Nie všetky kombinácie musia bežať pri každom commite. Vrstvený model môže používať:

- representative smoke matrix v pull requeste,
- affected combinations podľa componentu,
- oldest a newest supported runtime ako povinné boundaries,
- full matrix pred releaseom,
- periodickú compatibility matrix,
- experimentálne combinations ako advisory.

Selection policy vytvára false-negative risk. Musí mať konzervatívny fallback a periodický full run, ktorý odhalí nesprávny mapping.

## 20. Test sharding

Sharding rozdeľuje jeden logical suite medzi viac workers.

Metódy:

- statické rozdelenie podľa files,
- hash test ID,
- historical-duration balancing,
- dynamic work stealing,
- domain alebo fixture affinity.

Dobrý shard model zachováva:

- jednoznačný test inventory,
- deterministic alebo auditovateľný assignment,
- seed a environment identity,
- izolované test data,
- missing/duplicate detection,
- report merge bez straty source shardu,
- first-attempt result aj pri retry,
- stabilný cleanup.

## 21. Shard imbalance

Pipeline končí podľa najpomalšieho required shardu. Priemerná shard duration môže byť dobrá, hoci jeden outlier drží celý fan-in.

Sleduj:

- p50/p95 shard duration,
- rozdiel najrýchlejší verzus najpomalší shard,
- test setup overhead,
- historické outliers,
- retry a flaky distribution,
- queue time podľa runner poolu.

Historical balancing musí invalidovať model pri výraznej zmene test inventory alebo runtime environmentu.

## 22. Shared-state race conditions

Paralelné jobs sa môžu ovplyvňovať cez zdieľaný mutable state:

- rovnakú databázu alebo schema,
- statický tenant alebo test account,
- object-storage prefix,
- mutable artifact tag,
- shared cache key,
- fixed port,
- environment alebo deployment target,
- rate-limited external API,
- globálny feature flag,
- lock alebo migration state.

Ochrany:

- unique run/test IDs,
- per-worker namespace alebo schema,
- immutable artifact names,
- environment lease,
- idempotentný setup/cleanup,
- scoped credentials,
- rate a concurrency budget,
- explicitný owner shared resourceu.

## 23. Artifact flow

Jobs si nemajú odovzdávať release-critical dáta cez nezdokumentovaný shared workspace.

Správny flow:

```text
build job
→ publish immutable artifact D
→ verification jobs read D
→ fan-in creates evidence manifest for D
→ promotion consumes D + evidence manifest
```

Každý transfer má overiť digest, media type, access policy a retention. Artifact produced by retry musí mať jednoznačný relationship k pôvodnému attemptu; downstream nesmie náhodne zmiešať outputs z rôznych attempts.

## 24. Retry identity

Retry môže znamenať:

- nový attempt toho istého jobu,
- nový job instance,
- nový child pipeline,
- celý nový pipeline run.

Evidence musí zachovať:

- original failure,
- attempt number,
- input identity,
- artifact identity produced by each attempt,
- reason for retry,
- final selected result.

Ak build job pri retry vytvorí nový artifact digest, všetky downstream evidence musia patriť k vybranému digestu. Nie je bezpečné kombinovať test z prvého attemptu so scanom druhého artifactu.

## 25. Cache pri paralelizácii

Súbežný zápis do rovnakého cache key môže vytvoriť last-writer-wins, partial content alebo cross-platform contamination.

Bezpečné patterns:

- shared base cache je read-only,
- exact cache je scoped podľa OS, architecture, toolchain a input hash,
- jeden designated writer publikuje po úspešnom jobe,
- publication je atomic,
- untrusted jobs nezapisujú do trusted namespace,
- cache output sa pred použitím validuje,
- cold-cache run periodicky overuje correctness.

Cache nie je fan-in mechanizmus ani release artifact store.

## 26. Concurrency limits a backpressure

Fan-out musí rešpektovať kapacitu celého systému:

- runner pools,
- CI organization quota,
- registry throughput,
- package mirrors,
- database connection limits,
- cloud API quotas,
- external sandbox rate limits,
- ephemeral environment capacity.

Neobmedzený fan-out môže predĺžiť queue time všetkým projektom. Použi bounded concurrency, workload classes, priority policy a backpressure.

## 27. Resource-aware scheduling

Jobs majú rozdielne resource profiles:

- CPU-heavy compilation,
- memory-heavy static analysis,
- I/O-heavy dependency restore,
- network-heavy artifact transfer,
- GPU workload,
- private-network deployment.

Runner label iba opisuje capability; nie je dostatočná security boundary. Použi oddelené pools, identity, network segmentation a explicitné permissions.

Capacity plánovanie má pracovať s queue time, utilization, startup latency, throttling, OOM a critical-path impactom.

## 28. Fail-fast

Fail-fast zastaví zostávajúce matrix alebo sibling jobs po prvom relevantnom failure.

Je vhodný, keď:

- cieľom je čo najrýchlejší merge feedback,
- ďalšie results nepridajú významnú diagnostickú hodnotu,
- cancellation je bezpečná,
- cleanup a report upload zostanú aktívne.

Nie je vhodný, keď:

- potrebujeme kompletnú compatibility matrix,
- release decision vyžaduje všetky failures,
- výsledky sú drahé a periodické,
- zvyšné jobs poskytujú nezávislé evidence.

Fail-fast policy musí zachovať completed artifacts a original failure.

## 29. Continue-on-error a optional support

Optional job môže zlyhať bez blokovania overall verdictu, ale jeho status musí zostať viditeľný.

`continue-on-error` potrebuje:

- explicitný risk dôvod,
- ownera,
- označenie experimental/advisory,
- expiráciu alebo maturity criteria,
- oddelenie od required support matrixu,
- metrics a alert pri dlhodobom failure.

Permanentne červený optional job je mŕtva kontrola, nie užitočné pokrytie.

## 30. Child pipelines

Parent pipeline môže vytvoriť child graph podľa componentu, environmentu alebo generated configuration.

Contract musí definovať:

- child input identity,
- inherited a explicitné permissions,
- artifacts a outputs,
- completion/failure propagation,
- cancellation propagation,
- retry semantics,
- parent fan-in behavior,
- traceability medzi run IDs,
- maximálnu recursion/depth a cycle prevention.

Parent nesmie skončiť zeleno iba preto, že úspešne spustil child pipeline. Musí vedieť, či má čakať na child completion a ktoré výsledky sú required.

## 31. Multi-project pipelines

Cross-repository workflow sa používa napríklad pri promotion artifactu do GitOps repository alebo pri coordinated release viacerých komponentov.

Potrebné controls:

- short-lived scoped authentication,
- immutable source a artifact identity,
- versioned request/response contract,
- idempotency key,
- cycle a trigger-storm prevention,
- authorization target repository a environmentu,
- audit correlation ID,
- timeout a failure propagation,
- explicitný ownership boundary.

Generic trigger token s právom spustiť ľubovoľný privileged workflow je security risk.

## 32. Reusable deployment workflow

Deployment workflow má začínať immutable release inputom, nie source checkoutom alebo mutable tagom.

Odporúčané inputs:

- artifact digest alebo release-manifest digest,
- target environment identity,
- config revision,
- rollout strategy a guardrails,
- change/risk metadata,
- evidence-manifest reference,
- requested release exposure.

Deployment workflow nemá implicitne rebuildovať source. Má overiť provenance, policy, eligibility a vykonať idempotentnú state transition.

## 33. Permission inheritance

Reusable workflows môžu dediť tokeny, secrets alebo permissions od caller-a. To je významná trust boundary.

Kontroluj:

- či callee môže rozšíriť práva alebo iba zúžiť,
- ktoré secrets sa prenášajú explicitne,
- či nested workflow dostane rovnaké credentials,
- či untrusted branch môže zvoliť privileged reusable workflow,
- environment-scoped identity až v deployment jobe,
- effective permissions v resolved graph-e.

Implicitné `inherit all secrets` zväčšuje blast radius a komplikuje audit.

## 34. Testing reusable components

Provider má testovať viac vrstiev:

### Static contract tests

- input/output schema,
- resolved config,
- DAG cycles a missing dependencies,
- permission policy,
- pinning externých dependencies.

### Unit tests tools/scripts

- argument parsing,
- error classes,
- idempotency,
- plan generation,
- cancellation a timeout.

### Component tests

- disposable runner,
- artifact publication a retrieval,
- reports a outputs,
- failure/cancel/cleanup paths.

### Representative consumer fixtures

- jednoduchá služba,
- monorepo,
- Windows/Linux workload,
- protected deployment,
- optional feature combinations,
- old a new supported contract versions.

### Canary rollout

- provider release najprv používa interný alebo malý consumer set,
- sleduje failure, runtime a permission changes,
- až potom rozširuje adoption.

## 35. Observability providera

Provider potrebuje vedieť:

- počet consumerov podľa version,
- adoption a migration rate,
- failure rate podľa provider revision,
- critical-path contribution,
- invalid/incomplete graph rate,
- deprecated consumers,
- override a escape-hatch patterns,
- permissions používané v praxi,
- support incidenty,
- rollback frequency.

Bez usage telemetry nie je možné bezpečne ukončiť starú version alebo posúdiť globálny blast radius zmeny.

## 36. Performance a cost model

Optimalizácia pipeline musí rozlišovať:

- **Wall-clock latency —** čas, ktorý čaká developer alebo release.
- **Critical path —** najdlhšia required dependency cesta.
- **Total compute —** súčet runner času všetkých jobs.
- **Queue time —** čakanie na kompatibilnú kapacitu.
- **Transfer overhead —** artifact/cache upload a download.
- **External cost —** API, test environmenty a licencované nástroje.
- **Canceled waste —** compute spotrebovaný superseded alebo fail-fast jobs.

Skrátenie wall-clock času z 20 na 10 minút pri desaťnásobnom compute môže byť správne pre kritický feedback, ale musí to byť vedomý trade-off.

## 37. Diagnostický postup

Keď reusable alebo parallel pipeline zlyhá:

1. identifikuj consumer commit a provider/template revisions;
2. získaj resolved graph digest a effective permissions;
3. over immutable artifact identity použitú všetkými branches;
4. porovnaj expected a actual child/shard inventory;
5. rozlíš job failure, missing job, cancellation, timeout a tool error;
6. skontroluj data/control dependencies a fan-in policy;
7. over shared resources, locks, cache namespaces a quotas;
8. skontroluj retry attempts a artifacts z každého attemptu;
9. zmeraj critical path, queue time a shard imbalance;
10. rollbackni provider version alebo zúž graph podľa compatibility policy;
11. zachovaj evidence a pridaj regression fixture na zistený failure mode.

## 38. Typické anti-patterny

### Reuse ako copy-paste YAML

Lokálna duplikácia nemá provider contract, versioning ani centrálnu opravu.

### Floating template pre všetkých consumerov

Jedna zmena môže bez consumer diffu naraz rozbiť celú organizáciu.

### Template s implicitnými admin permissions

Pohodlný reusable workflow sa stane privilege-escalation cestou.

### Fan-out z mutable tagu

Jednotlivé jobs môžu overovať rozdielny obsah.

### Fan-in bez expected inventory

Chýbajúci shard sa interpretuje ako neprítomný failure a pipeline je false green.

### Maximum parallelism bez capacity budgetu

Queueing a throttling predĺžia feedback a poškodia ostatné pipelines.

### Retry bez attempt identity

Výsledky a artifacts z rôznych attempts sa zmiešajú do neplatného evidence setu.

### Child pipeline fire-and-forget

Parent skončí úspešne po vytvorení child runu bez čakania na required výsledok.

### Optional job bez lifecycle

Dlhodobo červená kontrola sa stane ignorovanou dekoráciou.

### Centralizácia bez escape hatchu

Template núti rozdielne workloads do nesprávneho modelu a tímy ho začnú obchádzať mimo auditu.

## 39. Praktický rozhodovací rámec

1. Ktorá úroveň reuse je najnižšia a stále dostatočná?
2. Kto je provider a kto consumer?
3. Aký je explicitný input/output a failure contract?
4. Aká immutable provider version sa používa?
5. Ktoré zmeny sú breaking a aký je migration window?
6. Aká resolved configuration sa reálne vykoná?
7. Aké effective permissions a secrets workflow dostane?
8. Ktoré jobs sú nezávislé a ktoré edges sú skutočne required?
9. Aký expected inventory má fan-out/matrix/sharding?
10. Ako fan-in rozpozná missing, duplicate alebo stale result?
11. Používajú všetky jobs rovnaký artifact digest?
12. Aké shared-state races a external quotas existujú?
13. Ako sa propaguje cancellation, timeout a retry?
14. Kedy je fail-fast vhodný?
15. Ako sa meria critical path verzus total compute?
16. Ako provider rolloutuje a rollbackuje novú template version?
17. Ako sa deprecation a consumer adoption sledujú?

## 40. Kontrolný checklist

Pred publikovaním reusable alebo parallel workflowu over:

- contract je versionovaný a dokumentovaný,
- provider revision a transitive dependencies sú pinned,
- resolved graph a permissions sú auditovateľné,
- inputs majú typy, defaults a validation,
- outputs majú schema a provenance,
- secrets sa neprenášajú implicitne,
- artifact fan-out používa jeden immutable digest,
- expected matrix/shard inventory je známy,
- fan-in blokuje pri missing required result,
- retry attempts sa nemiešajú,
- shared resources sú izolované alebo zamknuté,
- concurrency rešpektuje capacity a quotas,
- cleanup beží pri failure aj cancel,
- child/multi-project completion sa správne propaguje,
- provider má representative test fixtures,
- major zmena má migration guide a rollback,
- observability sleduje adoption, failures, cost a deprecated consumers.

## 41. Kontrolné otázky

1. Aký je rozdiel medzi reusable scriptom, jobom a workflowom?
2. Čo tvorí provider/consumer contract?
3. Prečo je resolved-template identity dôležitejšia než samotný include odkaz?
4. Ktoré zmeny reusable workflowu môžu byť breaking bez zmeny input names?
5. Ako funguje contract negotiation alebo capability detection?
6. Prečo critical path nie je súčet všetkých job durations?
7. Aký je rozdiel medzi control, data a policy dependency?
8. Ako fan-in dokáže, že dostal kompletný result set?
9. Prečo musia všetky fan-out jobs používať rovnaký artifact digest?
10. Ako selective matrix vytvára false-negative risk?
11. Čo musí zachovať dôveryhodný shard model?
12. Ako retry mení artifact a evidence identity?
13. Kedy je fail-fast vhodný a kedy škodlivý?
14. Aké riziká má permission inheritance reusable workflowov?
15. Ako parent pipeline správne vyhodnotí child pipeline?
16. Ako sa vyvažuje wall-clock latency a total compute?
17. Aké telemetry potrebuje provider centrálneho template?

## Summary

Reusable pipelines sú versionované provider/consumer contracts, nie iba zdieľané YAML fragmenty. Dôveryhodný model pozná immutable provider revision, resolved graph, effective permissions, input/output schema, compatibility a deprecation lifecycle. Paralelizácia skracuje critical path iba vtedy, keď DAG dependencies, artifact identity, shard inventory, fan-in completeness, shared-state isolation, retry identity a cancellation semantics zostávajú explicitné. Platforma musí súčasne merať latency, total compute, queueing, adoption a globálny blast radius shared zmien.

## Glossary impact

Relevantné pojmy: reusable pipeline, provider, consumer, reusable job, workflow template, template contract, resolved graph, contract negotiation, fan-out, fan-in, expected result inventory, matrix pipeline, selective matrix, test sharding, shard imbalance, child pipeline, multi-project pipeline, permission inheritance, fail-fast, continue-on-error, critical path a total compute.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Pipeline as Code](pipeline-as-code.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Artifact versioning →](artifact-versioning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->