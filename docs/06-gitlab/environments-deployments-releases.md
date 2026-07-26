# Environments, deployments a releases

## Metadata

- Status: Learning
- Level: L2
- Domain: GitLab

GitLab environment, deployment a Release opisujú tri rozdielne vrstvy delivery systému:

```text
environment = pomenovaná runtime boundary
deployment = pokus zmeniť konkrétny runtime subject v tejto boundary
release = distribuovaný a podporovaný produktový subject
```

Dôveryhodný lifecycle ich spája, ale nezamieňa:

```text
immutable release subject
→ deployment eligibility
→ desired runtime change
→ GitLab deployment record
→ controller alebo deploy execution
→ effective runtime verification
→ release exposure a acceptance
→ support / deprecation / revocation
→ cleanup a recovery evidence
```

Najdôležitejší rozdiel je medzi tým, čo bolo požadované, čo GitLab zaznamenal a čo reálne beží.

## 1. Nosný model: desired, recorded a effective state

Pre každý deployment rozlišuj:

- **Desired state:** čo pipeline, manifest alebo GitOps commit požaduje.
- **Recorded state:** čo GitLab deployment objekt a job evidujú.
- **Effective state:** artifact, config, routing, feature a shared-state kombinácia reálne aktívna v targete.

```text
job exit 0
≠ controller reconciliation complete
≠ správny target
≠ správny runtime digest
≠ zdravý business outcome
```

Rozdiel vzniká pri asynchrónnom controlleri, partial mutation, manuálnom zásahu, stale pipeline, nesprávnom environment name, routing drift-e alebo neúplnej telemetry.

## 2. Nosný scenár: Atlas Payments release 3.13.0

Atlas publikuje release `3.13.0` pre Payments API a worker.

Release manifest `RM313` obsahuje:

```text
api image digest      D_api_313
worker image digest   D_worker_313
rendered config       C44
infrastructure rev    I19
schema phase          S_expand
feature policy        F37
SBOM/provenance       E313
support state         candidate
```

GitLab model:

```text
project: atlas/payments
static environment: production-eu
review environment: review/842
protected deploy job: deploy_production
release record: 3.13.0 → RM313
```

Plánovaný chain:

```text
build a publish RM313
→ deploy do review/842
→ verify a teardown review app
→ approve production subject RM313 + production-eu
→ zapíš desired GitOps revision G88
→ controller reconciliuje D_api_313/D_worker_313
→ over effective digest, config, routing a business journey
→ označ deployment succeeded
→ promotionuj exposure
→ release 3.13.0 accepted a supported
```

Tento scenár spája environment identity, deployment record, GitOps reconciliation, runtime verification, review-app cleanup a release lifecycle.

## 3. Environment je runtime boundary, nie voľný názov

Environment identity musí jednoznačne mapovať:

```text
GitLab project/release unit
environment name a tier
cloud account/subscription
cluster a namespace
region
data a configuration boundary
owner
protection a approval policy
runtime identity
```

`production`, `Production`, `prod-new` a `production/eu` sú pre GitLab odlišné subjects. Ak dva názvy smerujú na rovnaký cluster, no iba jeden je protected, vzniká authorization bypass.

Atlas preto používa kanonický contract:

```text
environment.name = production-eu
tier = production
cloud account = atlas-prod
cluster = eu-prod-01
namespace = payments
workload identity audience = deploy:payments:production-eu
```

Environment name je security-relevant input. Nesmie byť voľne odvodený z nedôveryhodnej variable.

## 4. Static a dynamic environment majú odlišný lifecycle

### Static environment

`production-eu` má stabilný owner, data boundary, deployment history a support contract. Nezaniká po jednom pipeline run-e.

### Dynamic environment

`review/842` vzniká pre konkrétny MR a má bounded lifetime:

```text
MR/pipeline subject
→ isolated namespace, URL a test identity
→ deploy immutable digest
→ validation
→ stop request
→ workloads/DNS/storage/identity cleanup
→ nulový external inventory
→ environment closed
```

GitLab status `stopped` je iba recorded state. Cleanup je complete až po nezávislom overení cloud resources, volumes, DNS a credentials.

## 5. Deployment subject musí byť immutable a úplný

Deployment subject pre `production-eu` je:

```text
release manifest RM313
+ config C44
+ infra I19
+ schema phase S_expand
+ feature policy F37
+ target production-eu
+ rollout generation G313
```

Samotný commit SHA alebo tag nestačí. Rovnaký source môže vytvoriť rozdielne artifacts podľa toolchainu a platformy; rovnaký image môže bežať s rozdielnym configom a schema phase.

Approval, runtime verification aj recovery musia odkazovať na rovnaký subject.

## 6. Deployment state machine

Atlas používa:

```text
created
→ prerequisites checked
→ approved/eligible
→ queued
→ executing desired-state mutation
→ reconciling
→ verifying effective state
→ succeeded / failed / blocked / inconclusive
→ accepted / recovered / superseded
```

Verdicty:

- `blocked` — chýba permission, approval, lock alebo prerequisite;
- `failed` — známy deployment mechanizmus zlyhal;
- `inconclusive` — mutation mohla prebehnúť, ale effective outcome nie je dokázaný;
- `superseded` — novší desired subject nahradil starší;
- `succeeded` — effective state a required outcomes boli overené;
- `accepted` — observation window a release criteria sú splnené.

GitLab job, ktorý iba commitne GitOps manifest, nemá označiť celý deployment za succeeded bez controller feedbacku.

## 7. Eligibility pred executionom

Pred production mutation Atlas overí:

```text
RM313 a všetky digests existujú a sú immutable
required test/security evidence je complete a fresh
approval patrí RM313 + C44 + production-eu
release nie je revoked
schema a rollback compatibility sú platné
freeze/incident policy povoľuje transition
job beží z trusted resolved configu
workload identity claims matchujú target
current environment generation umožňuje G313
```

Dlhé čakanie na manual job môže z pôvodne eligible subjectu vytvoriť stale deployment. Eligibility sa preto prehodnocuje tesne pred mutation.

## 8. Manual job nie je approval

`when: manual` poskytuje trigger point. Approval je risk decision nad presným subjectom.

```text
manual play permission
≠ oprávnenie akceptovať risk
≠ dôkaz freshness
≠ separation of duties
```

Approval packet obsahuje release manifest, config/infra revision, target, evidence, rollout plán, recovery eligibility, known exceptions a expiry.

## 9. Workload identity a runtime authorization

Production job nepoužíva shared static cloud key.

```text
trusted GitLab job
→ ID token s project/ref/environment claims
→ cloud provider overí issuer, audience a subject
→ vydá short-lived credential pre production-eu
→ deployment API mutation
→ credential expiruje
```

Cloud-side policy musí overiť skutočný job context. GitLab environment protection bez external runtime authorization nie je úplná boundary.

## 10. Concurrency, generation a supersession

Dva deployments na rovnaký environment môžu vytvoriť stale overwrite:

```text
G312 začne rollout a čaká
→ G313 sa nasadí a overí
→ G312 pokračuje
→ production sa vráti na starší subject
```

Atlas kombinuje:

- environment resource group alebo lease;
- monotonickú desired generation;
- compare-and-set pred každou mutation fázou;
- superseded-run cancellation;
- revalidation po čakaní;
- runtime-side controller fencing.

Serialization bez generation checku iba zoradí jobs. Nezaručuje, že starší subject je stále žiaduci.

## 11. GitOps: request a deployment sú dva eventy

CI pri Atlas GitOps flowe:

```text
RM313
→ commit G88 do desired-state repository
→ GitLab zaznamená configuration request
→ controller načíta G88
→ admission/render/apply/reconcile
→ runtime inventory ukáže D_api_313 + D_worker_313 + C44
→ deployment record dostane effective verdict
```

Potrebná korelácia:

```text
source pipeline
↔ release manifest
↔ config commit G88
↔ controller reconciliation ID
↔ cluster/namespace
↔ runtime digests
↔ deployment record
```

Bez nej „deploy job passed“ znamená iba úspešný zápis požiadavky.

## 12. Post-deployment verification

Atlas overuje:

### Identity a convergence

- API a worker digests;
- config a feature revision;
- replica count a rollout completion;
- schema phase;
- controller generation.

### Runtime health

- readiness a healthy capacity;
- error rate, latency a saturation;
- dependency a queue health;
- routing a exposure.

### Functional a business outcome

- payment authorization synthetic;
- idempotent retry;
- žiadne duplicate captures;
- reconciliation a settlement invariants.

Telemetry je dimenzovaná podľa deployment ID, digestu, configu, regionu a cohorty. Global aggregate môže skryť chybu iba v novej generation.

## 13. Release object, deployment a exposure sú samostatné states

Release `3.13.0` môže byť:

- publikovaný, ale nikde nenasadený;
- nasadený iba v review alebo staging environment-e;
- nasadený v produkcii, ale bez trafficu;
- vystavený iba jednému ringu;
- revoked pre nové použitie, ale stále aktívny na starom runtime;
- podporovaný, deprecated alebo end-of-life.

Preto Atlas eviduje zvlášť:

```text
distribution state
deployment state
exposure state
support state
security/revocation state
```

Jedna GitLab Release karta nemôže byť autoritou pre všetky tieto stavy.

## 14. Release manifest a durable assets

GitLab Release nevyrába nové bytes. Odkazuje na už overené immutable outputs:

```text
3.13.0
→ RM313
→ api D_api_313
→ worker D_worker_313
→ config C44
→ infra I19
→ SBOM, provenance a signatures
→ support a compatibility metadata
```

Release asset nemá smerovať iba na expirovateľný job artifact. Dlhodobé outputs patria do container/package/generic registry s digestom alebo checksumom.

Mutable `latest` môže byť discovery alias. Release record musí zachovať immutable identity.

## 15. Release lifecycle a freshness

```text
candidate
→ published
→ accepted
→ supported
→ deprecated
→ end-of-life
→ archived alebo revoked
```

Nová vulnerability môže zmeniť security stav bez source zmeny. Pôvodný zelený pipeline zostáva historickou evidence, nie večným verdictom.

Pri revocation treba:

```text
identifikovať affected release digests
→ blokovať nové deploymenty/pully podľa policy
→ nájsť active runtime inventory
→ publikovať opravený release
→ redeploynúť a overiť
→ aktualizovať support/advisory state
```

## 16. Worked failure: GitLab evidoval úspech, runtime ostal na starej verzii

Pipeline úspešne commitla desired-state revision G88 a deployment job skončil zeleno.

```text
CI zapíše G88
→ GitLab deployment record = succeeded
→ GitOps controller odmietne manifest pre admission policy
→ runtime zostane na D_api_312
→ release dashboard tvrdí 3.13.0
```

### Príčina

Deployment success bol viazaný na zápis požiadavky, nie na controller reconciliation a effective runtime verification.

### Dôsledok

Support a incident response používali nesprávny release inventory. Rollback 3.13.0 nemal význam, pretože 3.13.0 nikdy reálne nebežal.

### Náprava

- oddeliť configuration-request a effective-deployment record;
- korelovať controller reconciliation ID;
- označiť stav `reconciling` alebo `failed`, nie `succeeded`;
- runtime digest a critical journey ako required postcondition;
- alert pri desired/recorded/effective divergence.

## 17. Worked failure: review app bola stopped, ale jej cloud state prežil

Stop job odstránil Kubernetes namespace a GitLab environment označil ako stopped. Managed database, DNS record a federated cloud role však ostali.

```text
namespace delete uspeje
→ stop job exit 0
→ environment stopped
→ DB/DNS/role inventory nie je kontrolovaný
→ resources ostanú bez ownera a s nákladom/attack surface
```

### Príčina

Cleanup sa hodnotil podľa jedného orchestration kroku, nie podľa desired-zero inventory všetkých external resources.

### Náprava

```text
resource manifest s ownerom/expiry
→ idempotentný teardown každej vrstvy
→ revoke identity
→ external inventory reconciliation
→ TTL garbage collector
→ environment closed až pri nulovom inventári
```

## 18. Worked failure: Release odkazoval na mutable a expirovateľný output

GitLab Release `3.13.0` obsahoval link na `app-latest.zip` z job artifacts s `expire_in: 30 days`.

Po mesiaci:

```text
job artifact expiruje
→ release download nefunguje
→ mutable alias latest už ukazuje 3.14.0
→ support nevie reprodukovať 3.13.0
→ rollback package chýba
```

### Príčina

Release record nemal immutable durable asset ani manifest-bound checksum.

### Náprava

Publikovať versioned generic package alebo image digest, zachovať RM313 ako retention root a overovať release asset availability počas support lifecycle-u.

## 19. Kauzálny diagnostický walkthrough

Symptom: GitLab tvrdí, že production deployment `3.13.0` succeeded, ale používateľ stále vidí behavior `3.12.0`.

### Krok 1 — stabilizuj subjects

```text
release = 3.13.0 / RM313
desired config = G88
recorded deployment = DEP-913 succeeded
target = production-eu
expected digest = D_api_313
```

### Krok 2 — konkurenčné hypotézy

```text
H1: controller G88 ešte nereconcilioval alebo zlyhal
H2: job zasiahol iný cluster/namespace
H3: runtime digest je nový, ale traffic ostal na old generation
H4: feature/config policy ponecháva starý behavior
H5: starší deployment prepísal novší state
H6: telemetry alebo support údaj je stale
H7: release manifest alebo deployment record ukazuje nesprávny digest
```

### Krok 3 — diskriminačné observation points

- config repository commit a controller events testujú H1;
- cloud account, cluster, namespace a workload identity audit testujú H2;
- live replicas, service routing a traffic weights testujú H3;
- effective config/flag revision testuje H4;
- generation a deployment timeline testujú H5;
- direct synthetic a runtime response headers testujú H6;
- registry digest a RM313 mapping testujú H7.

Atlas zistí admission rejection pre G88. Runtime stále používa D_api_312; target, routing aj telemetry sú správne. H1 vysvetľuje symptom.

### Krok 4 — containment a recovery

Atlas pause-ne ďalšiu promotion, opraví manifest policy, vytvorí novú desired revision G89 pre rovnaký RM313 a zachová failed reconciliation evidence. Nepoužije falošný rollback na 3.12.0, pretože runtime už na 3.12.0 je.

### Krok 5 — over pôvodný outcome

```text
controller reconciled G89
runtime digest = D_api_313
config = C44
critical payment journey prejde
GitLab deployment record = succeeded
release exposure state je aktualizovaný
```

### Krok 6 — skorší control

Finding sa mení na controller callback, effective-state gate, divergence alert a zákaz označiť GitOps request ako deployment success.

## 20. Recovery a drift

Pri divergence medzi recorded a effective state-om:

```text
pause ďalšie mutations
→ zachovaj actual inventory a timeline
→ urči desired authority
→ contain traffic/feature/identity podľa mechanizmu
→ reconcile, rollback alebo roll-forward
→ over runtime a business outcome
→ oprav GitLab record
```

GitLab UI sa nemá „opraviť“ bez runtime nápravy. Rovnako runtime hotfix bez desired-state update-u vytvára opakovaný drift.

## 21. Diagnostický runbook

1. Urči release manifest, deployment subject a environment identity.
2. Oddeľ desired, recorded a effective state.
3. Over pipeline/job actor, resolved config, approval a workload identity.
4. Pri GitOps-e koreluj config commit s controller reconciliation.
5. Over runtime digests, config, routing, schema a feature state.
6. Skontroluj generation, lock, supersession a manuálne zásahy.
7. Pri dynamic environment-e over external inventory a credential cleanup.
8. Pri release probléme over durable immutable assets a support/revocation state.
9. Zvoľ containment a recovery podľa skutočne zmeneného state-u.
10. Over pôvodný user/business outcome a aktualizuj lifecycle controls.

## 22. Referenčné pravidlá

- Environment je runtime boundary, nie iba YAML string.
- Deployment subject zahŕňa artifact, config, infra, shared-state phase a target.
- Manual trigger nie je risk approval.
- GitOps request nie je effective deployment.
- Serialization potrebuje generation a stale-subject revalidation.
- `Succeeded` vyžaduje nezávislú effective-state verification.
- Review app je closed až po nulovom external inventory.
- Release job nerebuildí artifacts.
- Release asset musí byť immutable a durable počas support/rollback lifecycle-u.
- Distribution, deployment, exposure, support a revocation sú samostatné states.

## 23. Časté omyly

### „Deploy job je zelený, produkcia je správna“

Job mohol iba odoslať asynchrónny request alebo zasiahnuť nesprávny target.

### „Environment je len názov pre UI“

Názov ovplyvňuje protection, variables, metrics a cleanup.

### „Stopped review app nemá resources“

GitLab status nemusí reflektovať DB, DNS, storage alebo cloud identity.

### „Release tag identifikuje všetko“

Potrebný je immutable multi-component manifest a runtime digest inventory.

### „Release bol raz zelený, je stále bezpečný“

Nová intelligence môže zmeniť support alebo revocation state.

## 24. Zhrnutie

Dôveryhodný GitLab release-to-runtime lifecycle je:

```text
immutable release manifest
→ canonical environment a scoped identity
→ fresh deployment eligibility
→ generation-aware desired-state mutation
→ controller/executor reconciliation
→ independent effective-state verification
→ deployment acceptance a exposure
→ release support a continuous risk state
→ recoverable cleanup a audit
```

GitLab records majú hodnotu iba vtedy, keď zostávajú korelované s immutable artifacts, skutočným targetom a runtime telemetry. Deployment sa nekončí zápisom požiadavky a Release sa nekončí vytvorením tagu.

## Oficiálna dokumentácia

- [Environments](https://docs.gitlab.com/ci/environments/)
- [Deployments](https://docs.gitlab.com/ci/environments/deployments/)
- [Releases](https://docs.gitlab.com/user/project/releases/)
- [Review apps](https://docs.gitlab.com/ci/review_apps/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Container a package registry](container-and-package-registry.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Security scanning →](security-scanning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->