# Runners a executors

## Metadata

- Status: Learning
- Level: L2
- Domain: GitLab

GitLab Runner je execution agent, ktorý prijíma eligible CI/CD jobs a vykonáva ich pomocou konkrétneho executora. Runner nie je iba výpočtový worker. Je to bezpečnostná a prevádzková hranica medzi pipeline kódom, repository obsahom, secrets, cache, artifact storage, hostom, cloud identitou a cieľovým environmentom.

## 1. Mental model

Zjednodušený tok:

```text
pipeline job
→ GitLab scheduler
→ runner eligibility a selection
→ executor vytvorí runtime
→ checkout / artifacts / cache / credentials
→ user script
→ reports a outputs
→ cleanup
→ runtime disposal alebo reuse
```

Dôveryhodný výsledok vyžaduje, aby každá fáza mala jednoznačnú identitu, oprávnenia, failure semantics a cleanup contract.

## 2. Runner, runner manager a worker

Rozlišuj tri úrovne:

- **GitLab Runner software —** komunikuje s GitLabom, vyžiada job, pripraví execution context a odošle výsledok.
- **Runner manager —** dlhšie žijúci proces alebo instance, ktorá môže orches­trovať viac job workers.
- **Worker runtime —** konkrétny container, pod, VM, instance alebo shell workspace, v ktorom sa vykoná jeden job.

Pri autoscaling modeli môže manager existovať trvalo, zatiaľ čo workers vznikajú pre každý job. Pri shell executore sú manager a worker často rovnaký host, čo výrazne zväčšuje cross-job trust.

## 3. Executor

Executor určuje, ako runner vytvorí job runtime. Bežné modely:

- Docker executor,
- Kubernetes executor,
- Docker Autoscaler,
- Instance executor,
- Shell executor.

Executor nie je iba syntaxická voľba. Určuje isolation, startup latency, resource model, storage, networking, credential exposure, cleanup a failure modes.

## 4. Runner scope

Runner môže byť dostupný na instance, group alebo project scope.

Scope odpovedá:

```text
Ktoré projekty môžu runner zaradiť medzi kandidátov?
```

Neodpovedá automaticky:

```text
Je job dostatočne dôveryhodný pre host, credentials a sieť runnera?
```

Instance runner má veľký organizačný blast radius. Project runner má menší scheduling scope, ale môže byť stále nebezpečný, ak je persistentný, privileged alebo pripojený k produkčnej sieti.

## 5. Job trust classification

Pred návrhom poolov klasifikuj jobs napríklad ako:

- **Untrusted validation —** merge requests z fork-u alebo kód od externého autora.
- **Trusted verification —** kód po review na chránenom ref-e, ale bez produkčných oprávnení.
- **Artifact build —** job vytvára release-relevantné bytes a provenance.
- **Signing alebo publishing —** job používa vysoko citlivú identity.
- **Deployment —** job mutuje runtime environment.
- **Administrative automation —** job mení GitLab, cloud alebo platform policy.

Tieto triedy nemajú zdieľať rovnaký pool iba preto, že používajú rovnaký operačný systém.

## 6. Runner selection

Job sa spáruje s runnerom podľa kombinácie:

- runner scope,
- tags,
- protected-ref eligibility,
- runner state,
- job requirements,
- dostupnej concurrency.

Tag je scheduling label. Sám osebe nepreukazuje security vlastnosť. Tag `production` je bezpečný iba vtedy, keď neoprávnený projekt alebo job nemôže taký runner použiť a runner má skutočne obmedzenú identity aj network scope.

## 7. Protected runners

Protected runner obmedzuje execution na chránené refs podľa GitLab trust modelu. Pomáha oddeliť release jobs od bežných feature branches.

Nechráni však pred:

- škodlivou zmenou pipeline kódu, ktorá sa dostala na chránený ref,
- mutable included template,
- príliš širokou deploy identitou,
- kompromitovaným runner hostom,
- únikom cez logs, artifacts alebo external egress,
- nesprávne chráneným tagom.

Protected runner je jeden authorization filter, nie úplná trust boundary.

## 8. Runner authentication identity

Runner authentication token identifikuje runner voči GitLabu. Odlišuj ho od:

- `CI_JOB_TOKEN`,
- ID tokenu pre workload federation,
- registry credentialu,
- project alebo group access tokenu,
- cloud deployment credentialu.

Runner token potrebuje:

- ownera,
- bezpečné bootstrap doručenie,
- obmedzený storage access,
- rotáciu,
- revokáciu pri decommissioningu,
- incident postup pri kompromitácii.

Kompromitovaný runner môže získať jobs a ich runtime dáta podľa svojho scope-u.

## 9. Job execution lifecycle

Typický lifecycle:

```text
request job
→ prepare executor
→ provision runtime
→ inject predefined context
→ checkout source
→ restore cache
→ download artifacts
→ start services
→ run script
→ collect reports/artifacts
→ upload cache
→ cleanup secrets a workspace
→ dispose alebo recycle runtime
```

Failure pred `script` je iná trieda než test failure. Pipeline a operátori musia rozlíšiť minimálne:

- scheduler/selection failure,
- provisioning failure,
- image pull failure,
- checkout failure,
- cache/artifact transport failure,
- user script failure,
- report upload failure,
- cleanup/disposal failure.

## 10. Docker executor

Docker executor vytvára job container a voliteľné service containers.

Výhody:

- explicitný runtime image,
- rýchly startup,
- jednoduchšie lokálne reprodukovanie,
- oddelený filesystem a process namespace,
- vhodný model pre bežné build/test jobs.

Riziká:

- shared host kernel,
- privileged mode,
- Docker socket mount,
- shared volumes a cache,
- mutable images,
- container runtime vulnerabilities,
- host-level network reachability.

Container isolation nie je VM isolation.

## 11. Docker socket a privileged builds

Mount Docker socketu typicky poskytuje jobu veľmi širokú kontrolu nad daemon hostom. Job môže vytvárať privileged containers, mountovať host filesystem alebo čítať iné workloads.

Preferuj podľa use case:

- rootless BuildKit alebo Buildah,
- dedikovaný remote builder,
- izolovaný ephemeral worker,
- kanonický build service,
- workload identity s presným publish scope-om.

Privileged build runner nemá vykonávať nedôveryhodné merge-request jobs.

## 12. Kubernetes executor

Kubernetes executor typicky vytvorí pod pre job. Pod môže obsahovať build, helper a service containers.

Výhody:

- ephemeral runtime,
- scheduler a autoscaling,
- resource requests a limits,
- namespaces, service accounts a NetworkPolicy,
- oddelenie pools pomocou nodes a runtime classes.

Riziká:

- príliš široký service account,
- hostPath, privileged alebo host-network workload,
- shared-cluster side channels,
- weak egress isolation,
- unbounded pod creation,
- secrets v pod spec alebo environment-e,
- nedostatočné node separation od produkcie.

CI workload je arbitrary code execution. Nemá automaticky patriť do rovnakého trust domainu ako produkčné workloads.

## 13. Kubernetes safety baseline

Podľa rizika používaj:

- dedikovaný namespace alebo cluster,
- least-privilege service account,
- Pod Security enforcement,
- seccomp a dropped capabilities,
- read-only root filesystem,
- zakázané host mounts,
- NetworkPolicy a egress controls,
- quotas a LimitRanges,
- node isolation a taints,
- krátkodobú federovanú identity,
- automatické odstránenie orphaned pods.

Over effective pod spec po mutations a defaults, nie iba CI YAML.

## 14. Shell executor

Shell executor spúšťa job priamo na hoste.

Je vhodný iba v úzkych prípadoch, napríklad pre dôveryhodné workloads vyžadujúce konkrétny hardware alebo proprietárny toolchain na dedikovanom hoste.

Riziká:

- shared filesystem a procesy,
- slabé oddelenie používateľov,
- dependency drift,
- zvyškové credentials,
- background procesy po jobe,
- prístup k host službám,
- kompromitácia ďalších jobs.

Shell runner pre viac nedôveryhodných projektov je nebezpečný operating model.

## 15. Autoscaling a instance executors

Autoscaling model vytvára alebo prideľuje instances podľa queue dopytu.

Riadiť treba:

- golden image a jeho provenance,
- secure bootstrap,
- runner registration a token delivery,
- instance identity,
- cloud quotas,
- boot latency,
- spot/preemptible termination,
- idle capacity,
- stale worker detection,
- cleanup a deprovisioning,
- cost attribution.

Worker, ktorý job dokončil, ale nebol odstránený, sa stáva persistentným neauditovaným runnerom.

## 16. Ephemeral verzus persistent workers

Ephemeral worker zanikne po jobe alebo malom počte jobs. Znižuje cross-job contamination a zjednodušuje incident containment.

Persistent worker je lacnejší a rýchlejší pri opakovanom použití, ale potrebuje silnejší hygiene model:

- čistý workspace,
- procesový cleanup,
- rotáciu credentials,
- disk quotas,
- izolované cache paths,
- pravidelný immutable rebuild hosta,
- drift detection.

Ephemeral neznamená automaticky čistý, ak sa worker vytvára z kompromitovaného image alebo zdieľa persistentný volume.

## 17. Workspace a helper lifecycle

Runner helper funkcionalita vykonáva checkout, artifact a cache transport a ďalšie orchestration kroky. Helper image a runner version sú súčasťou execution environmentu.

Zachovaj:

- kompatibilitu runner/helper verzií,
- pinned alebo kontrolované images,
- registry dostupnosť,
- TLS trust,
- checksum alebo signature verification podľa assurance modelu,
- diagnostiku pred-script failures.

Workspace po jobe nesmie obsahovať source, tokens, generated keys, sockets ani credentials files dostupné ďalšiemu jobu.

## 18. Secrets a credential injection

Runner môže sprostredkovať variables, file secrets, job tokeny a ID tokens. Bezpečný model:

```text
job identity
→ overené claims
→ short-lived scoped credential
→ konkrétna operácia
→ expirácia
```

Runner host nemá držať univerzálny cloud key pre všetky jobs. Credential scope viaž na project, ref, environment, job účel, audience a krátku lifetime.

## 19. Network boundary

Job egress môže byť rovnako citlivý ako credentials. Zváž:

- povolené registries a package endpoints,
- dependency proxy,
- blokovanie cloud metadata endpointu,
- egress proxy a allowlist,
- DNS policy,
- segmentáciu od produkčných sietí,
- audit outbound trafficu,
- explicitný prístup k deployment API.

Signing alebo release job s neobmedzeným internetom a vysoko privilegovanou identity má veľký exfiltration risk.

## 20. Resource model

Runner pool potrebuje plán pre:

- CPU a memory,
- disk a inode capacity,
- image-pull bandwidth,
- cache backend throughput,
- external API quotas,
- licenses,
- IP adresy a Kubernetes pod quotas,
- build concurrency.

Príliš vysoká concurrency môže zvýšiť job duration, OOM rate a queue instability. Optimalizuj celý critical path, nie iba percento využitia runnera.

## 21. Resource limits

Jeden job nemá nekontrolovane spotrebovať celý pool. Vynucuj podľa platformy:

- CPU a memory limits,
- ephemeral storage,
- process count,
- job timeout,
- maximum artifact/cache size,
- network bandwidth alebo egress policy,
- maximálny počet service containers.

Limit failure musí byť diagnostikovateľný ako OOM, quota alebo timeout, nie iba ako všeobecný exit code.

## 22. Image a toolchain provenance

Job image, helper image a base VM image sú build inputs. Pre release-relevantné jobs zachovaj:

- image digest,
- image build provenance,
- OS a architecture,
- runner a executor version,
- toolchain versions,
- runtime configuration,
- policy version.

Mutable runner image môže zmeniť artifact bez zmeny source repository.

## 23. Cache a shared storage

Cache, mounted volumes a object storage vytvárajú cross-job state. Oddeľ:

- trusted a untrusted cache namespaces,
- project a group boundaries,
- protected a non-protected refs,
- architectures a toolchains,
- release build od bežného branch build-u.

Workspace nemá fungovať ako implicitná cache. Každý shared state potrebuje explicitný owner, key a cleanup policy.

## 24. Runner upgrade lifecycle

Runner upgrades ovplyvňujú helper behavior, executor API, networking aj cleanup.

Bezpečný flow:

```text
review release a compatibility
→ test canary runner
→ spusti reprezentatívne jobs
→ porovnaj failure signatures
→ rozšír pool po vlnách
→ zachovaj rollback image/config
→ odstráň deprecated nastavenia
```

Neaktualizuj celý signing alebo production pool naraz bez observation window.

## 25. Runner decommissioning

Pri vyradení:

1. zastav prijímanie nových jobs,
2. nechaj dokončiť alebo bezpečne zruš aktívne jobs,
3. revokuj runner authentication token,
4. odstráň cloud/service identities,
5. zmaž caches a workspaces podľa policy,
6. zachovaj potrebné logs a audit evidence,
7. odstráň instance, pods, volumes a DNS records,
8. over, že runner už nie je eligible.

Vypnutá VM bez revokovaného runnera a identity nie je dokončený decommissioning.

## 26. Compromise response

Pri podozrení na kompromitáciu runnera:

- pause alebo revoke runner,
- zastav citlivé pools a jobs,
- rotuj runner tokeny a dostupné credentials,
- identifikuj jobs, projects a artifacts, ktoré runner spracoval,
- považuj vytvorené artifacts za potenciálne nedôveryhodné,
- audituj registry pushes, deployments a external calls,
- zachovaj forensic evidence,
- obnov runner z čistého immutable image,
- oprav trust boundary pred opätovným zapnutím.

Rebuild hosta bez revokácie ukradnutých credentials problém neuzatvára.

## 27. Observability

Sleduj:

- queue duration podľa trust poolu,
- job a provisioning duration,
- runner utilization a concurrency,
- image pull latency,
- system failure rate,
- OOM, disk a inode pressure,
- stale/offline workers,
- cache hit/miss,
- worker creation a cleanup failures,
- cost per job alebo compute minute,
- protected jobs vykonané mimo očakávaného poolu.

Metrics musia obsahovať runner/pool/executor identitu bez úniku secrets.

## 28. Failure verdicty

Rozlišuj:

- **Job failed —** user script alebo test našiel problém.
- **Runner system failure —** runner, executor alebo host nedokončil execution contract.
- **Infrastructure unavailable —** registry, cluster alebo cloud API nebolo dostupné.
- **Canceled/superseded —** job bol vedome zrušený podľa pipeline policy.
- **Cleanup incomplete —** výsledok môže byť známy, ale runtime alebo credentials neboli bezpečne odstránené.
- **Invalid environment —** job bežal na nesprávnom architecture, image alebo pool-e.

Retry má byť viazaný na transientnú triedu. Nemá premeniť opakovateľný product failure na zelený výsledok.

## 29. Diagnostický postup

Keď job zostane pending alebo zlyhá pred scriptom:

1. over pipeline a job inclusion,
2. over runner scope, tags a protected eligibility,
3. over runner online/paused stav a queue capacity,
4. identifikuj executor provisioning fázu,
5. over image, architecture, TLS a registry auth,
6. over quotas, scheduler a resource limits,
7. over checkout, cache a artifact transport,
8. over injected identity a network policy,
9. skontroluj cleanup pred retry,
10. uchovaj presnú runner a worker identitu.

## 30. Typické anti-patterny

### Jeden runner pre všetko

Untrusted test, signing aj production deployment zdieľajú host, cache a credentials boundary.

### Tags ako jediná security policy

Projekt schopný požadovať tag môže získať citlivý runner bez ďalších scope a protection controls.

### Persistent privileged runner pre merge requests

Nedôveryhodný kód môže kompromitovať host a ďalšie jobs.

### Shared static cloud key na runner hoste

Každý job v pool-e získava rovnaký veľký blast radius.

### Shell executor bez workspace cleanup

Súbory, tokens a procesy jedného projektu ovplyvňujú ďalší.

### Autoscaler bez deprovisioning evidence

Orphaned workers zostávajú aktívne s platnou identity.

### Release artifact z neidentifikovaného runner image

Build provenance nevie vysvetliť toolchain a execution environment.

## 31. Praktický rozhodovací rámec

Pre každý runner pool odpovedz:

1. Aké job trust classes vykonáva?
2. Ktoré projects a refs sú eligible?
3. Aký executor a isolation model používa?
4. Je worker ephemeral alebo persistent?
5. Aké credentials, network a host resources môže job získať?
6. Ako sa identifikujú a pinujú images a toolchain?
7. Ktorý shared state existuje medzi jobs?
8. Aké resource a concurrency limity platia?
9. Ako funguje cleanup a disposal?
10. Aké failure triedy možno retryovať?
11. Ako sa pool upgraduje a rollbackuje?
12. Ako sa runner decommissionuje alebo izoluje pri incidente?

## 32. Kontrolný checklist

- untrusted a privileged jobs používajú oddelené pools;
- runner scope a tags zodpovedajú trust modelu;
- protected runner nie je jediná ochrana;
- privileged mode a host socket sú zakázané alebo izolované;
- workers majú resource a egress limits;
- credentials sú krátkodobé a scoped;
- runner, helper a job images sú identifikované;
- workspace a processes sa po jobe čistia;
- caches sú oddelené podľa trustu;
- cleanup failure je viditeľný;
- autoscaled workers sa spoľahlivo odstránia;
- observability rozlišuje queue, provisioning, script a cleanup;
- runner compromise má runbook a credential-rotation plán.

## 33. Kontrolné otázky

1. Aký je rozdiel medzi runnerom, managerom, workerom a executorom?
2. Prečo runner scope nie je úplná security boundary?
3. Prečo tags samy osebe neautorizujú citlivý job?
4. Ktoré jobs majú byť oddelené do samostatných trust pools?
5. Prečo Docker socket typicky znamená host-level privilege?
6. Aké riziká prináša Kubernetes executor v shared clusteri?
7. Kedy je shell executor prijateľný?
8. Čo musí obsahovať secure autoscaling lifecycle?
9. Ako workload identity znižuje blast radius credentials?
10. Ktoré shared states môžu kontaminovať ďalší job?
11. Ako sa rozlišuje job failure od runner system failure?
12. Čo treba urobiť pri kompromitácii runnera?

## Summary

GitLab Runner je privilegovaná execution boundary, nie neutrálna výpočtová kapacita. Bezpečný návrh klasifikuje jobs podľa trustu, oddeľuje pools, používa primeraný executor, krátkodobé identities, obmedzený egress, resource limits a explicitný cleanup. Dôveryhodný pipeline výsledok musí byť spätne viazaný na runner, worker, image, toolchain a execution policy. Ephemeral runtime znižuje cross-job riziko, ale iba vtedy, keď je bezpečný aj bootstrap, shared storage a disposal lifecycle.

## Glossary impact

Relevantné pojmy: GitLab Runner, runner manager, worker, runner scope, runner tag, protected runner, executor, Docker executor, Kubernetes executor, Shell executor, autoscaling executor, ephemeral runner, helper image, runner system failure, runner pool a workload identity.

## Oficiálna dokumentácia

- [Executors](https://docs.gitlab.com/runner/executors/)
- [Docker executor](https://docs.gitlab.com/runner/executors/docker/)
- [Kubernetes executor](https://docs.gitlab.com/runner/executors/kubernetes/)
- [Shell executor](https://docs.gitlab.com/runner/executors/shell/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: GitLab CI/CD syntax](gitlab-ci-cd-syntax.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Variables a secrets →](variables-and-secrets.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
