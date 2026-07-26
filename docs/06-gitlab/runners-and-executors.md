# Runners a executors

## Metadata

- Status: Learning
- Level: L2
- Domain: GitLab

GitLab Runner je privilegovaná execution boundary. Pipeline job nie je abstraktný príkaz: scheduler ho priradí konkrétnemu runner poolu, executor vytvorí runtime, runner vloží source, artifacts, cache a identity, job vykoná arbitrary code a po skončení musí runtime aj credentials bezpečne odstrániť.

```text
job trust contract
→ runner eligibility a selection
→ worker provisioning
→ effective runtime identity
→ source/artifact/cache preparation
→ user script a side effects
→ report/artifact publication
→ cleanup a credential revocation
→ worker disposal alebo overený reuse
```

Dôveryhodný job verdict preto musí patriť nielen source SHA a pipeline konfigurácii, ale aj konkrétnemu runnerovi, executorovi, worker image-u, toolchainu, credentials a cleanup outcome-u.

## 1. Nosný model: trusted execution state machine

Runner lifecycle má odlišné observation boundaries:

```text
CREATED
→ ELIGIBLE
→ ASSIGNED
→ PROVISIONING
→ PREPARING
→ EXECUTING
→ PUBLISHING
→ CLEANING
→ DISPOSED alebo REUSABLE
```

Failure v každom stave znamená niečo iné:

- `ELIGIBLE` bez assignu: scope, tags, protected context alebo capacity;
- provisioning failure: cloud/Kubernetes/Docker/runtime problém;
- preparing failure: image, checkout, artifact, cache, helper alebo TLS;
- executing failure: user script alebo dependency behavior;
- publishing failure: verdict môže byť známy, ale evidence chýba;
- cleanup failure: outputs môžu existovať, ale trust boundary ostala otvorená.

Generic `job failed` tieto mechanizmy zlieva a vedie k nesprávnym retries.

## 2. Nosný scenár: Atlas Payments runner pools

Atlas rozdeľuje pipeline do štyroch trust classes:

```text
MR_VALIDATE
→ untrusted code, bez secrets, ephemeral Kubernetes pool

TRUSTED_BUILD
→ protected main, pinned toolchain, ephemeral Docker/VM pool

RELEASE_PUBLISH
→ immutable artifact input, signing/publish identity, isolated pool

PRODUCTION_DEPLOY
→ approved release manifest, environment OIDC identity, isolated pool
```

Pre release `3.12.0` vznikne execution record:

```text
pipeline P812
job build_release attempt 1
source SHA S42
resolved config C19
runner pool trusted-build-v5
runner manager RM7
worker W991
executor docker-autoscaler
worker image digest I18
helper image H6
architecture linux/amd64
artifact digest D42
cleanup verdict complete
```

Publish job nesmie rebuildovať D42. Dostane ho ako explicitný artifact input a beží v inom, užšom pool-e s publish-only identity.

## 3. Runner, manager, worker a executor sú odlišné identity

- **Runner software** komunikuje s GitLabom a vykonáva execution protocol.
- **Runner manager** dlhšie žije, prijíma jobs a vytvára workers.
- **Worker** je konkrétny container, pod, VM alebo shell workspace pre job.
- **Executor** určuje, ako sa worker vytvorí a izoluje.

Pri autoscalingu môže byť manager dôveryhodný, ale konkrétny worker vzniknúť z driftujúceho image-u. Pri shell executore sú manager, worker, filesystem a procesný priestor často ten istý host, takže cleanup failure ovplyvní ďalší job.

Execution provenance musí rozlišovať všetky štyri vrstvy.

## 4. Eligibility nie je authorization celého jobu

Scheduler vyhodnocuje najmä:

```text
runner scope
+ tags
+ protected-ref eligibility
+ online/paused state
+ executor/job constraints
+ concurrency a capacity
→ candidate runner set
```

Tag `production` je label pre matching, nie dôkaz isolation alebo cloud authorization. Protected runner filtruje ref context, ale nechráni pred škodlivým kódom, ktorý sa dostal na protected ref, mutable include-om ani príliš širokou host identitou.

Po schedulingu musí ďalšia vrstva overiť:

```text
pipeline/source trust
→ resolved job definition
→ runner pool trust class
→ injected identities
→ allowed network a side effects
```

## 5. Pool boundary vychádza z job capability

Atlas nezdružuje jobs iba podľa operačného systému. Rozdeľuje ich podľa toho, čo môžu ovplyvniť:

- untrusted test môže kompromitovať vlastný ephemeral runtime, nie release namespace;
- trusted build môže publikovať iba candidate artifact do staging storage;
- publish job môže zapísať immutable release version, ale nemôže deployovať;
- deploy job môže mutovať konkrétny environment, ale nemá signing key;
- cleanup/policy administration má oddelenú identity.

Ak jeden pool vykonáva fork MRs aj signing, runner compromise spája nedôveryhodný source s release supply chainom.

## 6. Executor určuje skutočnú isolation boundary

### Docker executor

Job container oddeľuje filesystem a process namespace, ale zdieľa host kernel. Privileged mode, host volumes alebo Docker socket môžu jobu dať host-level capability.

### Kubernetes executor

Každý job môže mať vlastný pod, no isolation závisí od effective pod specu, service accountu, namespace-u, NetworkPolicy, node placementu, admission mutations a host mounts.

### Shell executor

Job beží priamo na hoste. Je vhodný iba pre úzke trusted workloads na dedikovanom a dôsledne rebuildovanom hoste.

### Autoscaling alebo instance executor

Znižuje cross-job reuse, ale pridáva bootstrap, image provenance, cloud identity, stale-worker a deprovisioning failure boundaries.

`Ephemeral` je lifecycle vlastnosť, nie automatická bezpečnosť. Worker môže zdieľať kompromitovaný base image, cache volume alebo širokú network identity.

## 7. Effective runtime subject

Pred scriptom Atlas zaznamená:

```text
source/candidate SHA
resolved CI config digest
job name + attempt
runner manager a pool
worker ID a image digest
executor a architecture
helper image
cache/artifact inputs
predefined variable context
OIDC/job-token subject
network policy a resource limits
```

Tento subject vysvetľuje, prečo rovnaký script môže lokálne prejsť, na jednom runneri zlyhať a na inom vytvoriť odlišné bytes.

Mutable worker image alebo helper môže zmeniť build bez diffu v aplikácii.

## 8. Prepare phase je súčasť correctness

Runner pred user scriptom typicky:

```text
provisionuje runtime
→ vloží predefined context
→ checkoutne source
→ obnoví cache
→ stiahne artifacts
→ vytvorí service containers
→ vloží credentials
```

Checkout, cache a artifact chyby nie sú product-test failures. Retry je bezpečný iba ak prepare operation je idempotentná a partial state sa odstráni alebo izoluje.

Release build nesmie nevedome použiť workspace z predchádzajúceho jobu ako skrytý input.

## 9. Identity a network sa viažu na job účel

Silný model:

```text
GitLab job ID token
→ provider overí issuer, audience, project, ref, environment a job účel
→ vydá krátkodobý credential
→ credential povoľuje jednu triedu operácie
→ po jobe expiruje
```

Runner host nemá držať univerzálny cloud key. Untrusted validation pool nemá network path k production API, signing service ani cloud metadata endpointu.

Egress je rovnako dôležitý ako credential scope: job s tajomstvom a neobmedzeným internetom má jednoduchý exfiltration path.

## 10. Resource model chráni celý pool

Atlas plánuje CPU, memory, disk/inodes, image-pull bandwidth, cache throughput, IP adresy, pod quotas, external API limits a concurrency.

Príliš vysoká concurrency:

```text
viac jobs
→ CPU/I/O contention
→ dlhšie execution a timeouts
→ retries
→ ešte viac queue/workloadu
```

Resource limit failure musí byť klasifikovaný ako OOM, quota, disk pressure alebo timeout. Všeobecný exit code vedie k slepému retry a ďalšiemu tlaku.

## 11. Publish a cleanup sú súčasť verdictu

Po scripte runner:

```text
zozbiera reports/artifacts
→ uploadne outputs
→ prípadne zapíše cache
→ odstráni file secrets a credentials
→ ukončí services/procesy
→ vyčistí workspace
→ dispose-ne worker
```

Možné verdicty:

- script passed, outputs complete, cleanup complete;
- script passed, report upload failed — evidence incomplete;
- script failed, diagnostics published, cleanup complete;
- script outcome known, cleanup incomplete — security incident boundary;
- worker lost — unknown partial publication alebo side effects.

Zelený script bez required reportu alebo s orphaned workerom nie je plne dôveryhodný job result.

## 12. Worked failure: untrusted MR otrávil persistentný build host

Atlas mal project Docker runner s tagom `linux-build`. Používal persistentný host a mount Docker socketu. Rovnaký runner vykonával MR tests aj protected release builds.

Útočný MR job:

```text
získa Docker socket
→ vytvorí host-mounted privileged container
→ zapíše wrapper do shared toolchain pathu
→ MR job skončí
→ workspace cleanup odstráni iba repository directory
→ neskorší protected build spustí modifikovaný wrapper
→ release artifact D43 obsahuje vložený payload
```

### Príčina

Runner scope a protected-ref filter sa považovali za úplnú trust boundary. Shared host a Docker socket však umožnili cross-job persistence mimo workspace-u.

### Dôsledok

Release build mal trusted source aj zelenú pipeline, ale builder environment už nebol dôveryhodný. Všetky artifacts vytvorené po compromise windowe bolo nutné považovať za podozrivé.

### Trvalá náprava

```text
untrusted a release pools oddelené
→ žiadny host socket pre MR jobs
→ ephemeral workers z immutable image
→ build provenance s worker image/pool identity
→ periodic clean-room rebuild comparison
→ compromise runbook zahŕňajúci artifacts, registry a credentials
```

## 13. Worked failure: autoscaled worker zostal aktívny po jobe

Deploy worker získal 15-minútový cloud credential a job úspešne nasadil D42. Deprovision API timeoutol, ale pipeline evidovala iba script success.

```text
job script success
→ artifact/runtime verification prejde
→ cleanup začne
→ cloud worker delete má unknown outcome
→ worker ostane bežať s workspace a ešte platným credentialom
→ manager stratí lokálny tracking po reštarte
```

### Príčina

Disposal nebolo súčasťou job verdictu a chýbal reconciliation inventory managera voči cloud instances.

### Recovery

Atlas zablokoval pool, revokoval workload session, vyhľadal workers podľa generation/tagov, odstránil orphan a auditoval všetky jeho network calls.

### Trvalá náprava

- worker generation a idempotency key;
- cloud inventory reconciliation;
- cleanup-incomplete verdict;
- credential lifetime kratšia než maximálne cleanup okno;
- alert na orphan, stale registration a worker bez owning jobu.

## 14. Worked failure: release job skončil na nesprávnej architektúre

Runner tag `release` matchoval amd64 aj arm64 pool. Job nemal explicitnú architecture požiadavku a build tool vytvoril platform-specific binary.

```text
scheduler vyberie arm64 worker
→ script prejde
→ artifact sa pomenuje payments-linux.zip
→ downstream publish predpokladá amd64
→ zákaznícky runtime binary nespustí
```

### Príčina

Artifact subject ani runner selection contract neobsahovali architecture. Human-friendly filename zakryl platform identity.

### Náprava

Architecture sa stala explicitným matrix dimensionom, artifact manifest obsahuje platformu a digest a fan-in odmieta missing, duplicate alebo nesprávne varianty.

## 15. Kauzálny diagnostický walkthrough

Symptom: release artifact vytvorený z rovnakého source SHA má iný digest než predchádzajúci clean rebuild.

### Krok 1 — stabilizuj oba execution subjects

```text
source SHA S42
resolved config C19
job build_release
attempts A1 a A2
runner pools/pool revisions
worker image a helper digests
architecture
toolchain/cache inputs
```

### Krok 2 — formuluj konkurenčné hypotézy

```text
H1: source alebo resolved CI config sa líši
H2: worker/helper image alebo toolchain driftoval
H3: cache/workspace priniesli skrytý input
H4: build je intrinsically nondeterministic
H5: artifact patrí inému job attemptu alebo platforme
H6: runner host bol kompromitovaný
```

### Krok 3 — vyber diskriminačné observation points

- source/config digests testujú H1;
- worker/helper/toolchain inventory testuje H2;
- clean build bez cache a nový worker testujú H3;
- opakované clean builds na rovnakom subjecte testujú H4;
- artifact manifest, attempt a architecture testujú H5;
- host integrity, audit a cross-job timeline testujú H6.

Atlas zistí, že A1 bežal na persistentnom pool-e s mutable toolchain image-om, A2 na pinned ephemeral workerovi. Clean rebuild na A2 je stabilný; H2/H3 sú podporené.

### Krok 4 — contain-ni supply-chain boundary

Publication a deployment D42 sa zastavia. Persistentný pool sa pause-ne a artifacts z affected windowu sa označia ako nedôveryhodné.

### Krok 5 — obnov dôveryhodný outcome

Release sa znovu buildne z rovnakého source a resolved configu na clean pinned workerovi. Tests, SBOM, provenance a podpis sa viažu na nový digest.

### Krok 6 — vráť learning

Finding sa mení na required runner-image provenance, clean-build comparison, zákaz mutable release poolu a gate, ktorý odmietne artifact bez execution subjectu.

## 16. Runner upgrade a decommissioning

Upgrade:

```text
pin novú runner/helper/worker revision
→ canary pool
→ reprezentatívne jobs každej trust class
→ porovnanie failure signatures a digests
→ rollout po vlnách
→ rollback image/config
```

Decommissioning:

```text
stop new jobs
→ drain/cancel active jobs
→ revoke runner token a workload identities
→ odstráň workers, caches a volumes
→ zachovaj audit
→ over, že runner už nie je eligible
```

Vypnutá VM bez revokácie a cloud cleanupu nie je dokončený decommissioning.

## 17. Diagnostický runbook

1. Urči pipeline, job, attempt a source/config subject.
2. Rozlíš inclusion, eligibility, assignment a execution failure.
3. Zostav runner scope, tags, protection a candidate pool inventory.
4. Identifikuj manager, worker, executor, image, helper a architecture.
5. Urči posledný úspešný lifecycle state: provisioning, prepare, script, publish alebo cleanup.
6. Over cache/artifact inputs, credentials, network a resource limits.
7. Formuluj selection, capacity, environment, script a cleanup hypotézy.
8. Retry povoľ iba po klasifikácii a cleanup/reconciliation.
9. Over output aj disposal a credential expiry.
10. Zmeň finding na pool, provenance, resource alebo lifecycle control.

## 18. Referenčné pravidlá

- Runner je security a execution boundary, nie neutrálna compute kapacita.
- Scope a tags vytvárajú candidate set, nie úplnú authorization policy.
- Pooly sa oddeľujú podľa job capability a trustu.
- Executor určuje isolation, shared state a cleanup failure modes.
- Ephemeral worker je bezpečný iba pri dôveryhodnom bootstrap-e a disposal-e.
- Worker, helper a toolchain identity patria do build provenance.
- Protected runner nechráni pred trusted-ref code alebo mutable include compromise-om.
- Script success bez outputs alebo cleanupu môže byť incomplete verdict.
- Retry nasleduje po failure klasifikácii a reconciliation.
- Compromise response zahŕňa artifacts, credentials, registry aj deployments.

## 19. Časté omyly

### „Container runner izoluje host“

Shared kernel, privileged mode, host mounts a socket môžu isolation zrušiť.

### „Protected runner je bezpečný pre secrets“

Stále závisí od pipeline kódu, includes, hosta, identity a egressu.

### „Ephemeral znamená clean“

Worker môže vzniknúť z kompromitovaného image-u alebo zdieľať volume.

### „Job prešiel, cleanup už nie je dôležitý“

Orphan runtime alebo credential ponecháva otvorenú capability.

### „Tag `release` garantuje správny pool“

Treba overiť celý eligible set a effective worker properties.

## 20. Zhrnutie

Dôveryhodný Atlas runner lifecycle je:

```text
job trust class
→ presný eligible pool
→ identified manager/worker/executor
→ pinned effective runtime subject
→ explicitné source/artifact/cache/identity inputs
→ bounded execution
→ complete outputs
→ verified cleanup a disposal
→ provenance a lifecycle learning
```

Runner troubleshooting sa nekončí otázkou, či je worker online. Musí nájsť prvý state transition, ktorý sa neuskutočnil správne, oddeliť user-code failure od execution-boundary failure a overiť nielen výsledok scriptu, ale aj dôveryhodnosť outputs a uzavretie runtime capability.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: GitLab CI/CD syntax](gitlab-ci-cd-syntax.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Variables a secrets →](variables-and-secrets.md)
<!-- KNOWLEDGE-NAVIGATION:END -->