# Environment a promotion

Environment nie je iba názov ako `dev`, `staging` alebo `production`. Je to identifikovateľný runtime kontext so svojím desired state, effective state, konfiguráciou, identitou, dátami, sieťou, dependencies, policy, observability a deployment históriou. Promotion je riadená zmena deployment state, pri ktorej ten istý immutable artifact postupuje do ďalšieho environmentu spolu s presne viazaným evidence bundle.

## 1. Mental model

Environment a promotion možno chápať ako dve navzájom prepojené state machines:

```text
environment lifecycle
planned
→ provisioned
→ configured
→ ready
→ active
→ degraded/drifted
→ reconciling
→ retired
→ destroyed

artifact promotion lifecycle
eligible
→ approved/policy-authorized
→ deploying
→ verifying
→ promoted/released
→ paused/failed
→ rolled back/rolled forward
```

Promotion nesmie meniť bytes artifactu. Mení iba to, kde artifact beží, s akou configuration revision, identity a traffic policy.

## 2. Čo tvorí environment

Environment typicky zahŕňa:

- **Compute —** VM, containers, clusters, serverless runtime alebo managed platform.
- **Network —** VPC/VNet, subnets, routing, firewalls, ingress, egress, DNS a service discovery.
- **Runtime configuration —** non-secret settings, feature flags, limits a endpoint references.
- **Secrets a identities —** workload identity, trust roots, certificates, keys a secret versions.
- **Backing services —** databázy, queues, caches, object storage a external APIs.
- **Data state —** schema version, dataset, replication, retention a migrations.
- **Observability —** metrics, logs, traces, synthetics, dashboards a alerting.
- **Policy —** admission, compliance, deployment windows, approvals a retention.
- **Deployment history —** artifact digest, config revision, actor, result a release exposure.
- **Ownership —** support tím, on-call, cost owner a escalation path.

Dva environmenty s rovnakým application digestom sa môžu správať odlišne pre inú konfiguráciu, identity, topology, data distribution alebo external dependency.

## 3. Environment identity

Názov `production` nie je dostatočná identity. Dôveryhodný deployment record potrebuje jednoznačne identifikovať:

- organization/account/subscription,
- region a cluster,
- namespace alebo runtime boundary,
- environment ID,
- infrastructure revision,
- configuration revision,
- secret references alebo versions,
- active artifact digests,
- feature-flag snapshot alebo revision,
- traffic policy,
- schema/migration state.

Environment alias môže byť mutable. Deployment automation musí pred mutation overiť resolved environment identity a protection level.

## 4. Desired state verzus effective state

**Desired state** je deklarovaný stav v IaC, deployment manifests, config repository alebo control plane. **Effective state** je to, čo platforma a dependencies reálne vykonávajú po defaults, mutations, controllers a manuálnych zásahoch.

Príklad:

```text
Desired state:
replicas = 3
image = digest A
network policy = deny-by-default

Effective state:
2 ready replicas
image A
mutating webhook pridal sidecar
jedna egress cesta je povolená platformovou výnimkou
```

Promotion musí podľa rizika overiť obe vrstvy. Git diff alebo deployment plan nepreukazuje plný runtime efekt.

## 5. Environment typy podľa účelu

Bežné environmenty:

- **Local/developer —** rýchly feedback a izolovaný vývoj; nízka fidelity voči produkčnej topológii.
- **Integration —** interakcie komponentov a reálnych dependencies.
- **Ephemeral preview —** izolované overenie konkrétnej zmeny alebo pull requestu.
- **Staging/pre-production —** vyššia behavioral equivalence, release rehearsal a širšie validation gates.
- **Performance/resilience —** kontrolovaná kapacita, fault injection a dlhšie experimenty.
- **Production —** reálny používateľský a business kontext.
- **Disaster-recovery environment —** restore, failover a recovery validation.

Počet prostredí nie je cieľ. Každé musí mať explicitný risk a dôkaz, ktorý inde nie je lacnejšie alebo spoľahlivejšie dostupný.

## 6. Ephemeral environment

Ephemeral environment sa vytvorí pre branch, pull request, test alebo experiment a po skončení sa odstráni.

Výhody:

- izoluje paralelné zmeny,
- znižuje shared-state konflikty,
- umožňuje realistické component/E2E testy,
- uľahčuje reprodukciu konkrétneho artifactu,
- poskytuje kontrolovaný cleanup a cost attribution.

Riziká:

- provisioning latency,
- quota a cost pressure,
- secret/identity sprawl,
- cleanup failures,
- neúplné external dependencies,
- nereprezentatívne data a capacity,
- DNS alebo certificate lifecycle.

Potrebné controls:

- stable environment ID a owner,
- TTL a hard expiry,
- cost/ownership tags,
- environment-scoped short-lived identity,
- idempotentný create/reconcile/destroy,
- data classification,
- cleanup report,
- ochrana pred zmazaním nesprávneho environmentu.

## 7. Long-lived environment

Dlhodobo existujúci staging alebo produkčný environment akumuluje históriu a drift. Potrebuje:

- pravidelnú reconciliation,
- inventory,
- patch a upgrade lifecycle,
- secret rotation,
- capacity management,
- drift detection,
- cleanup deprecated resources,
- disaster-recovery test,
- deployment history a ownership.

Long-lived environment nemá byť „pet“, do ktorého sa ručne opravujú nezdokumentované problémy.

## 8. Parity verzus behavioral equivalence

Úplná identita stagingu a produkcie je často nepraktická. Dôležitá je equivalence vlastností relevantných pre testované riziko.

Príklady:

- rovnaký artifact digest,
- rovnaký deployment mechanizmus,
- rovnaká config schema,
- rovnaký identity a authorization model,
- podobná network path a TLS termination,
- kompatibilné managed-service versions,
- realistické resource limits,
- reprezentatívna data distribution,
- rovnaké admission a security policies.

Staging s jednou replikou neoverí rolling update, leader election alebo race medzi instances. Menší dataset neoverí query plan a migration locking. Fidelity musí byť viazaná na konkrétny risk, nie na všeobecné tvrdenie „staging je podobný produkcii“.

## 9. Artifact a configuration separation

Preferovaný model:

```text
artifact digest: rovnaký vo všetkých environmentoch
configuration: environment-specific, versionovaná
secret references: environment-specific
identity: environment-specific
traffic/release policy: environment-specific
```

Build-time vloženie production endpointu alebo credentials vytvára environment-specific artifact a ruší build-once/promote-many model.

Výnimky musia byť explicitné. Napríklad platform-specific binary môže byť samostatný artifact variant, ale každý variant potrebuje vlastný digest a evidence.

## 10. Configuration contract

Aplikácia a environment potrebujú versionovaný config contract:

- required a optional fields,
- types, ranges a allowed values,
- defaults a deprecated fields,
- secret-reference semantics,
- feature-flag dependencies,
- compatibility s artifact version,
- startup a reload behavior,
- fail-open/fail-closed semantics,
- validation pred mutation,
- redaction a audit pravidlá.

Config change môže mať rovnaký blast radius ako code deployment. Preto musí mať review, evidence, rollout a rollback lifecycle.

## 11. Configuration identity a provenance

Deployment record má zachovať:

- config repository a commit,
- rendered config digest,
- environment overlays,
- template/tool version,
- policy decisions,
- secret reference versions,
- feature-flag revision,
- timestamp a actor.

Nestačí logovať „config updated“. Pri incidente treba reprodukovať presný effective input.

## 12. Promotion

Promotion znamená, že konkrétny artifact digest sa stane eligible a následne deployed v ďalšom environment-e bez rebuildu.

```text
artifact digest A
+ evidence pre A
+ target environment state
+ promotion policy
→ deployment decision
```

Promotion je zmena assignmentu a deployment state. Nemá meniť source, package, image layers ani generated binary.

## 13. Promotion eligibility

Artifact je eligible iba ak:

- existuje v dôveryhodnej registry,
- digest je immutable,
- provenance a podpis spĺňajú policy,
- povinné build/test/scan evidence je úplné,
- evidence patrí presnému digestu,
- findings a exceptions sú v platnom stave,
- artifact nie je revoked,
- config a schema sú kompatibilné s targetom,
- podporovaná platforma/architecture zodpovedá environmentu,
- rollback alebo roll-forward cesta existuje.

Eligibility je snapshot rozhodnutie. Pri novom kritickom CVE, revocation alebo environment drifte sa môže zmeniť pred samotným deploymentom.

## 14. Evidence freshness

Nie všetky dôkazy majú neobmedzenú platnosť.

Príklady:

- unit test výsledok viazaný na immutable digest môže zostať platný dlho;
- vulnerability scan môže vyžadovať refresh po aktualizácii databázy;
- environment health je platný iba krátko;
- approval môže expirovať po zmene configu alebo incident stave;
- performance evidence nemusí platiť po zmene capacity alebo dependency.

Promotion policy má definovať freshness podľa evidence typu. Expired evidence má viesť k refresh, pause alebo novému rozhodnutiu, nie k implicitnému passu.

## 15. Artifact transfer medzi registries

Niektoré organizácie kopírujú artifacts medzi trust zónami alebo registries.

Bezpečný transfer:

1. source digest a signature verification;
2. copy bez rebuild alebo repackaging zmeny obsahu;
3. destination digest verification;
4. zachovanie provenance a SBOM väzby;
5. registry audit log;
6. immutable destination reference;
7. policy check pred promotion.

Ak packaging proces zmení bytes, vznikol nový artifact s novým digestom a potrebuje nové evidence podľa scope zmeny.

## 16. Release manifest

Komplexný release môže obsahovať viac komponentov:

```text
release manifest
- api image digest
- web image digest
- migration bundle digest
- Helm chart digest
- config schema version
- SBOM/provenance references
```

Manifest musí byť immutable a versionovaný. Promotion celého systému sa viaže na manifest digest, nie na voľnú kombináciu mutable tags.

## 17. Deployment verzus release exposure

Deployment odpovedá, kde artifact beží. Release odpovedá, komu a v akom rozsahu je behavior dostupný.

```text
deploy digest A do production
→ feature disabled
→ internal cohort
→ 5 % trafficu
→ selected tenants
→ 100 % release
```

Deployment record a release exposure record sú odlišné, ale musia byť korelovateľné.

## 18. Protected environment

Protected environment je policy boundary, ktorá obmedzuje:

- povolené refs a artifacts,
- deployment identities,
- required approvals,
- deployment windows,
- concurrency,
- change risk policy,
- secret access,
- manual overrides,
- audit evidence.

Protection musí byť enforced server-side alebo control-plane policy. Názov jobu `deploy-production` sám o sebe nič nechráni.

## 19. Environment-scoped identity

Preferovaný model:

```text
pipeline job identity
→ workload federation/OIDC
→ policy over repository, ref, workflow, artifact a environment
→ short-lived environment role
→ minimálne permissions
```

Výhody:

- žiadny dlhodobý cloud key v CI,
- credentials expirovali po jobe,
- scope je viazaný na konkrétny environment,
- audit rozlišuje jednotlivé deployments,
- jednoduchšia revocation.

Build job nemá mať production permissions. Deploy job nemá automaticky právo meniť artifact registry alebo signing policy.

## 20. Separation of duties

Rozlišuj práva:

- build artifact,
- podpis alebo attestation,
- review findings,
- promotion do test/staging,
- production deployment,
- release exposure,
- rollback alebo emergency override.

Separation of duties nemusí znamenať ručné kopírovanie. Môže byť implementované nezávislou policy, approvalom nad evidence a oddelenými workload identities.

## 21. Deployment concurrency

Dva deploymenty do rovnakého environmentu môžu vytvoriť lost update alebo nejasný state.

Príklad:

```text
A začne deploy v1
B začne deploy v2
B dokončí v2
A neskôr dokončí a prepíše časť state na v1
```

Ochrany:

- environment lock alebo lease,
- deployment queue,
- compare-and-swap nad environment revision,
- optimistic version check,
- serializácia mutable-state operácií,
- cancellation superseded deploymentu iba pred unsafe mutation,
- state reconciliation po failure.

## 22. Lock a lease semantics

Lock potrebuje:

- environment identity,
- owner/run ID,
- acquire timestamp,
- lease expiry,
- heartbeat alebo renewal,
- safe release,
- stale-lock recovery,
- audit log.

Neobmedzený lock bez expiry môže zablokovať environment po runner failure. Príliš krátka lease môže vypršať počas platného deploymentu a povoliť súbeh.

## 23. Deployment state machine

Deployment nemá byť jeden shell command. Dôveryhodný lifecycle:

```text
precheck
→ acquire lock
→ verify artifact/evidence
→ resolve target state
→ apply mutation
→ wait for readiness
→ run post-deploy verification
→ record result
→ release lock
```

Failure stavy:

- rejected pred mutation,
- partial apply,
- readiness timeout,
- verification failure,
- lock loss,
- cleanup failure,
- rollback/roll-forward started,
- state inconclusive.

Každý stav musí mať recovery alebo reconciliation postup.

## 24. Partial deployment

Partial deployment môže znamenať:

- časť replík na novom digeste,
- infra resource vytvorený, ale nie nakonfigurovaný,
- migration aplikovaná, application rollout zlyhal,
- routing prepnuto iba v jednom regióne,
- config update bez úspešného restartu.

Automation musí vedieť zistiť effective state, nie iba posledný úspešný command. Retry má byť idempotentný alebo používať reconcile model.

## 25. Deployment record

Pre každý pokus uchovaj:

- environment ID,
- artifact/release manifest digest,
- source commit,
- config a infrastructure revision,
- secret references,
- workflow/pipeline run,
- actor/workload identity,
- lock/lease ID,
- start/end timestamps,
- strategy a rollout stage,
- precheck a verification evidence,
- výsledok a failure class,
- rollback/roll-forward relation,
- release exposure.

Deployment history je prevádzkový zdroj pravdy a musí zahŕňať aj neúspešné pokusy.

## 26. Environment inventory

Inventory odpovedá „čo reálne beží“:

```text
environment ID
→ artifact digests
→ config revision
→ infrastructure revision
→ schema/migration state
→ secret references
→ feature flags
→ traffic policy
→ deployment status
```

Inventory má byť automaticky aktualizovaný a porovnateľný s desired state. Manuálny spreadsheet rýchlo zastará.

## 27. Environment drift

Drift je rozdiel medzi expected a effective state.

Kategórie:

- **Configuration drift —** manuálna alebo mimo-pipeline zmena settings.
- **Infrastructure drift —** resource zmenený priamo v cloud console/API.
- **Binary drift —** mutable tag alebo host package update zmenil bytes.
- **Identity drift —** role, certificate alebo secret binding sa zmenil.
- **Policy drift —** admission, firewall alebo approval pravidlo sa zmenilo.
- **Data/schema drift —** migration alebo dataset nezodpovedá očakávaniu.
- **Operational drift —** alert, dashboard alebo runbook už nereflektuje systém.

Promotion pri neznámom drifte môže byť rejected, paused alebo doplnená o reconciliation podľa policy.

## 28. Drift detection a reconciliation

Lifecycle:

1. načítaj desired state;
2. zmeraj effective state;
3. normalizuj platform defaults;
4. klasifikuj rozdiel;
5. posúď risk a ownera;
6. reconcile automaticky alebo schváľ výnimku;
7. uchovaj evidence;
8. over výsledok.

Blind auto-reconcile môže byť nebezpečný pri emergency hotfixe alebo data resource. Drift policy musí rozlišovať bezpečne opraviteľné a high-risk mutations.

## 29. Databáza ako shared mutable state

Databázu nemožno promotionovať ako immutable image. Viac aplikačných verzií môže súčasne používať rovnaký state.

Bezpečný expand-contract lifecycle:

1. pridať backward-compatible schema;
2. nasadiť code kompatibilný so starým aj novým stavom;
3. vykonať online migration/backfill;
4. overiť completeness a performance;
5. prepnúť reads/writes;
6. odstrániť starých consumers;
7. až potom odstrániť starý kontrakt.

Promotion policy kontroluje schema compatibility, migration progress, locks, rollback eligibility a RPO/recovery.

## 30. Event a queue state

Promotion consumerov a producerov musí zohľadniť:

- schema compatibility,
- staré správy v backlogu,
- replay a retention,
- duplicate/out-of-order handling,
- poison messages,
- consumer checkpointy,
- rollback na staršiu verziu,
- partition/routing semantics.

Artifact môže byť rollback-eligible pre stateless HTTP, ale nie pre queue s novou nekompatibilnou event schema.

## 31. Secrets medzi environmentmi

Secrets sa nepromotionujú z testu do produkcie. Promotion prenáša requirement alebo secret reference, nie value.

Každý environment má vlastné:

- secret values,
- trust roots,
- issuers a identities,
- rotation lifecycle,
- access policy,
- audit a break-glass proces.

Pipeline má validovať existenciu a kompatibilitu reference bez vypísania secretu do logu alebo artifactu.

## 32. Data medzi environmentmi

Test data sa nemajú presúvať do produkcie. Production-derived data do nižšieho prostredia vyžadujú:

- právny a organizačný základ,
- data minimization,
- anonymization/pseudonymization,
- re-identification risk review,
- encryption,
- access control,
- retention a deletion,
- audit prenosu.

Synthetic datasets sú preferovaný default.

## 33. Promotion gates

Príklad evidence progression:

```text
build
→ static/unit evidence
→ component/integration environment
→ contract a security evidence
→ staging
→ acceptance/performance/release rehearsal
→ production policy/approval
→ progressive rollout
→ post-deploy validation
```

Každý gate má pridávať nový druh dôkazu alebo vyššiu fidelity. Opakovanie rovnakého unit testu v piatich prostrediach bez nového risku iba predlžuje lead time.

## 34. Approval freshness

Approval má byť viazaný na:

- artifact digest,
- config revision,
- target environment,
- evidence snapshot,
- risk classification,
- deployment strategy,
- expiry.

Approval sa invaliduje pri zmene digestu, configu, kritického findingu, environment drifte alebo významnom incidente. „Schválené včera“ nemusí byť platné pre dnešný stav.

## 35. Deployment window a freeze

Policy môže obmedziť deployment podľa:

- support coverage,
- business calendar,
- peak traffic,
- regulatory window,
- error-budget state,
- aktívneho incidentu,
- dependency maintenance.

Freeze nie je náhrada bezpečného delivery systému. Dlhý freeze zväčšuje batch size a divergence po jeho skončení. Emergency zmena potrebuje osobitný auditovateľný override, nie skrytý bypass.

## 36. Rollback eligibility

Predchádzajúci artifact je rollback-eligible iba ak:

- je stále dostupný a dôveryhodný,
- config je kompatibilný,
- database a event state mu rozumejú,
- external contracts neboli nevratne zmenené,
- feature flags možno vrátiť,
- cache/serialization formát je kompatibilný,
- traffic migration je reverzibilná,
- recovery bol otestovaný.

Rollback eligibility sa môže meniť počas rollout-u. Deployment record ju má explicitne sledovať.

## 37. Roll-forward a feature disable

Pri stateful alebo nevratnej zmene môže byť bezpečnejšie:

- vypnúť feature flag,
- zastaviť writes,
- izolovať cohort alebo región,
- nasadiť compatible hotfix,
- vykonať compensation/reconciliation,
- pokračovať roll-forwardom.

Recovery decision má byť založený na data integrity a user impacte, nie iba na rýchlosti technického návratu.

## 38. Environment teardown

Teardown je privilegovaná destructive operácia.

Bezpečný lifecycle:

1. over stable environment ID, nie iba user-provided názov;
2. skontroluj protection flag a environment type;
3. zastav traffic a scheduled jobs;
4. exportuj evidence alebo dáta podľa retention;
5. revoke credentials a identities;
6. odstráň compute/network/DNS/resources;
7. vyrieš finalizers a dependencies;
8. uvoľni locks;
9. odstráň monitoring targets;
10. over, že nič nezostalo orphaned;
11. zapíš destroy record.

Production alebo shared environment musí byť explicitne denylisted z automatického TTL cleanupu.

## 39. Observability environment lifecycle

Sleduj:

- provisioning a readiness time,
- environment availability,
- promotion lead time,
- deployment queue a lock wait,
- deployment success/failure classes,
- drift count a age,
- stale/expired ephemeral environments,
- cleanup failure rate,
- config-related incidents,
- secret/identity failures,
- rollback/roll-forward time,
- evidence expiry a approval wait.

Environment platforma je produkčný systém a potrebuje SLO, ownership a capacity management.

## 40. Diagnostický postup

### Staging funguje, production nie

Porovnaj v tomto poradí:

1. artifact digest;
2. rendered config digest;
3. secret/identity references;
4. infrastructure revision;
5. network path a policy;
6. dependency versions;
7. schema/data state;
8. capacity a topology;
9. traffic mix;
10. feature flags a release exposure.

### Promotion použila iný artifact

Skontroluj mutable tag, rebuild, registry copy, release manifest a destination digest verification.

### Deployment čaká

Over environment lock/lease, queue, approval expiry, protected policy, deployment window, quota a starší active deployment.

### Deployment je partial

Zmeraj effective state, migration state, replica digests, routing, readiness a lock ownership. Nespúšťaj slepý retry bez reconcile plánu.

### Ephemeral environment zostal visieť

Over TTL controller, cleanup job, finalizers, dependent resources, destroy identity permissions, stale lock a protection tag.

### Environment driftuje po každom deploymente

Porovnaj desired state s platform defaults, mutating controllers a out-of-band automation. Nie každý opakovaný diff je manuálny drift.

## 41. Typické anti-patterny

### Environment je iba namespace

Namespace je technická boundary, ale nepopisuje identity, data, config, policy, dependencies ani ownership.

### Staging je automaticky „malá produkcia“

Bez explicitnej behavioral equivalence môže mať inú topology, scale, traffic a security model.

### Promotion znamená rebuild

Produkcia potom nedostane testované bytes.

### Jeden CI admin token pre všetky environmenty

Kompromitovaný build job má maximálny blast radius.

### Approval nie je viazaný na digest a config

Po zmene vstupov ostáva starý approval zdanlivo platný.

### Lock bez lease a recovery

Runner failure môže zablokovať environment na neurčito.

### Rollback sa považuje za univerzálny

Shared mutable state a external side effects ho môžu znemožniť.

### Ephemeral cleanup používa nevalidovaný názov

Destructive path môže zasiahnuť nesprávny environment.

### Drift sa automaticky prepíše bez klasifikácie

Emergency alebo business-critical zmena môže byť odstránená bez posúdenia.

## 42. Praktický checklist

Pred promotion over:

- target environment má stable identity,
- desired a effective state sú známe,
- artifact digest je immutable a eligible,
- evidence je úplná a čerstvá,
- config contract je kompatibilný,
- rendered config a infrastructure revision sú zaznamenané,
- secrets sú iba references s environment scope,
- drift je klasifikovaný,
- environment lock/lease je dostupný,
- deployment identity má minimálne permissions,
- database/event compatibility je overená,
- post-deploy validation má oracle a timeout,
- rollback eligibility alebo roll-forward plan je explicitný,
- approval patrí digestu, configu a targetu,
- release exposure je oddelená od deploymentu,
- cleanup a deployment records sú auditovateľné.

## 43. Kontrolné otázky

1. Čo tvorí environment okrem compute platformy?
2. Aký je rozdiel medzi desired a effective state?
3. Prečo názov `production` nie je dostatočná identity?
4. Aký je rozdiel medzi parity a behavioral equivalence?
5. Prečo sa artifact a configuration oddeľujú?
6. Čo musí obsahovať configuration provenance?
7. Čo znamená promotion eligibility?
8. Prečo evidence potrebuje freshness policy?
9. Kedy registry copy vytvorí nový artifact?
10. Aký je rozdiel medzi deploymentom a release exposure?
11. Ako protected environment vynucuje trust boundary?
12. Ako funguje environment-scoped workload identity?
13. Prečo deployment potrebuje lock alebo lease?
14. Ako sa rozpozná partial deployment?
15. Aké typy environment driftu existujú?
16. Prečo sa databáza nepromotionuje ako image?
17. Kedy je predchádzajúci artifact rollback-eligible?
18. Ako bezpečne zničiť ephemeral environment?
19. Prečo approval musí byť viazaný na digest a config revision?
20. Ako diagnostikuješ rozdiel medzi staging a production behaviorom?

## Summary

Environment je runtime a policy boundary s vlastnou identitou, desired/effective state, configuration, secrets, dependencies, data a deployment históriou. Promotion presúva immutable artifact a jeho evidence do konkrétneho environmentu bez rebuildu. Dôveryhodný model potrebuje eligibility, freshness, environment-scoped identity, locks, drift detection, partial-failure recovery, shared-state kompatibilitu, rollback eligibility a auditovateľný teardown. Deployment a release exposure sú oddelené state transitions a musia byť vzájomne korelovateľné.

## Glossary impact

Relevantné pojmy: environment, environment identity, desired state, effective state, ephemeral environment, long-lived environment, environment parity, behavioral equivalence, configuration contract, configuration provenance, promotion, promotion eligibility, evidence freshness, release manifest, protected environment, environment-scoped identity, deployment lock, lease, deployment state machine, partial deployment, environment drift, rollback eligibility a release exposure.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Trigger, artifact a cache](trigger-artifact-cache.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Quality gates a approvals →](quality-gates-and-approvals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
