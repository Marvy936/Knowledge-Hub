# Internal Developer Platform

Internal Developer Platform (IDP) je vnútorný productized system capabilities, interfaces a workflows, ktorý umožňuje application tímom bezpečne vytvárať, meniť, prevádzkovať a ukončovať software bez toho, aby každý tím musel ručne skladať celý cloud, Kubernetes, CI/CD, security, observability a compliance toolchain.

IDP nie je jeden webový portal ani iba repository template. Portal môže byť vstupné používateľské rozhranie. Skutočná platforma pokračuje za formulárom: validuje identity a intent, vytvorí durable operation, orchestruje authoritative systems, presadí policy, sleduje partial outcomes, publikuje ownership metadata a overí, že požadovaná capability je reálne použiteľná.

## 1. Dominantný model

Dominantný model sleduje request ako durable platform operation, nie ako synchronný portal click. Každá transition mení authoritative state v inom systeme a môže skončiť úspešne, zlyhať, zostať partial alebo mať unknown outcome.

Repository creation, cloud resource readiness, GitOps reconciliation a developer-functional verification sú samostatné dôkazy. Platform ich musí korelovať cez rovnaký operation subject, inak optimistický portal status zakryje neúplný alebo nefunkčný resource graph.

```text
developer alebo team capability need
→ exact platform request subject
→ discoverable product/capability contract
→ authenticated self-service request
→ schema, policy, quota a ownership validation
→ durable idempotent platform operation
→ orchestration cez Git, IaC, cloud, CI/CD a runtime controllers
→ provisioned effective capability a software metadata
→ developer-functional a operational verification
→ feedback, support, evolution, deprecation a second-request closure
```

IDP acceptance verdict sa nerobí podľa toho, že portal zobrazil zelenú hlášku alebo vytvoril Git repository. Musí preukázať, že všetky required outputs existujú v authoritative systems, sú navzájom korelované, owner ich môže používať, guardrails sú účinné a platforma vie bezpečne retry, update, rollback, repair aj decommission.

## 2. Platform engineering, IDP a developer portal

Tieto tri pojmy opisujú disciplínu, výsledný capability system a používateľské rozhranie. Ich zamieňanie vedie k tool-first návrhu: organizácia nainštaluje portal, ale nezavedie authoritative API, durable workflows, ownership, policy enforcement ani lifecycle.

Rozlíšenie je praktické aj pri incidente. Portal môže byť dostupný a zobrazovať cached projection, zatiaľ čo platform control plane alebo execution systems zlyhali; platform capability môže naopak fungovať cez API aj pri výpadku portal UI.

### Platform engineering

Platform engineering je disciplína navrhovania, budovania a prevádzkovania shared internal platform capabilities pre software delivery a operations. Zahŕňa technical architecture aj product/operating model.

### Internal Developer Platform

IDP skladá capabilities do konzistentného product contractu. Nie všetky organizácie potrebujú každý capability domain, ale tie, ktoré platforma deklaruje, musia zdieľať identity, policy, operation-state a support model namiesto izolovaných automatizačných skriptov.

Zoznam capability domains preto nie je feature checklist. Každý z nich predstavuje časť developer journey a zároveň authority boundary, ktorú platforma musí bezpečne orchestrate-nuť a následne pozorovať.

IDP je výsledný capability system. Môže zahŕňať:

- service/application provisioning;
- repository a pipeline bootstrap;
- environment a infrastructure provisioning;
- deployment a promotion workflows;
- secrets, identity a policy integration;
- observability a operational readiness;
- software catalog a ownership metadata;
- support, lifecycle a decommissioning.

### Internal developer portal

Portal je experience a aggregation layer. Môže zobrazovať catalog, documentation, templates, operations a links na underlying tools. Portal sám nemusí provisionovať nič; môže iba volať platform APIs alebo vytvárať Git changes.

Vzťah:

```text
developer portal
→ UI/API entrypoint a discoverability

IDP
→ portal + platform APIs + workflows + controllers + policies + operational model
```

Backstage je framework na tvorbu developer portalov. Jeho Software Catalog, Templates, TechDocs a plugins môžu byť súčasťou IDP, ale nainštalovanie Backstage samo osebe nevytvorí bezpečnú a spoľahlivú platformu.

## 3. Problém, ktorý IDP rieši

Problémom nie je iba počet nástrojov, ale počet rozhodnutí a neviditeľných dependencies, ktoré musí každý application tím opakovane správne poskladať. Rovnaká business potreba tak vytvára odlišné security, lifecycle a failure semantics podľa lokálneho skriptu alebo znalostí konkrétneho človeka.

Uvedené symptómy sa navzájom posilňujú. Duplicated automation vedie k inconsistent implementations, tie zvyšujú support toil a central ticket queues následne ešte viac oddeľujú developera od mechanizmu, ktorý jeho service prevádzkuje.

Cloud-native delivery skladá veľa specialized systems:

```text
source control
+ CI
+ artifact registry
+ IaC
+ cloud APIs
+ Kubernetes
+ GitOps
+ secrets
+ networking
+ observability
+ security policy
+ incident/support tooling
```

Bez platformovej vrstvy každý application tím potrebuje poznať interné detaily a kompatibility všetkých nástrojov. Vzniká:

- vysoká cognitive load;
- inconsistent implementations;
- security controls aplikované neskoro alebo nerovnomerne;
- ticket queues pre rutinné provisioning úlohy;
- skryté ownership a support gaps;
- duplicated automation;
- rozdielne lifecycle a cleanup semantics;
- failure diagnosis naprieč množstvom UI a credentials.

IDP tento problém nerieši tým, že všetku moc presunie na central team. Rieši ho poskytnutím jasných capability contracts a self-service boundaries, v ktorých application team zostáva ownerom svojho service outcome-u a platform team vlastní shared platform mechanisms.

## 4. Exact platform request subject

Platform request je semantic command nad existujúcim resource graphom. Exact subject umožňuje rozhodnúť, či ide o nový service, update tej istej capability alebo conflicting request a poskytuje idempotency identity pre downstream systems.

Každý rozmer subjectu mení provisioning, policy alebo support consequence. Preto sa nemá ukladať iba vo form fields; musí byť versionovaný v durable operation a prenesený do authoritative resources a catalog relations.

Request `vytvor production-ready service` musí byť rozložený na presný subject:

- requester identity a team ownership;
- business/system/domain context;
- requested capability a version;
- service name a globally unique identity;
- data classification a compliance profile;
- runtime model, regiony a availability tier;
- repository, language a build profile;
- environment a promotion topology;
- network exposure a dependency requirements;
- data stores, queues a secret needs;
- SLO/operational tier a on-call ownership;
- cost center, quota a lifecycle/expiry;
- policy bundle a platform contract version;
- idempotency key a expected outputs.

Bez exact subjectu retry môže vytvoriť druhý repository, druhú database alebo conflicting DNS name. Rovnako sa nedá rozhodnúť, či update request mení existujúci service alebo vytvára nový.

## 5. Capability contract

Capability contract je produktový aj technický záväzok medzi platform teamom a consumerom. Musí byť dostatočne high-level, aby skryl incidental provider complexity, ale dostatočne explicitný, aby developer rozumel failure, cost, security a lifecycle dôsledkom svojich choices.

Guarantees, defaults, consumer choices, policies, observability, support a deletion semantics sa vyhodnocujú spolu. Create action bez upgrade a decommission contractu je neúplný product, aj keď initial provisioning prejde.

Platform capability má byť definovaná ako contract, nie ako nejasné tlačidlo.

Príklad `Managed PostgreSQL` capability:

```text
inputs
→ engine/version class
→ region
→ availability tier
→ storage/performance bounds
→ backup retention
→ data classification
→ owner/cost center

outputs
→ stable database identity
→ endpoint/reference
→ workload identity binding
→ secret reference
→ backup/PITR policy
→ dashboards/alerts
→ support/SLO
→ deletion/restore contract
```

Contract musí vysvetliť:

- čo platforma garantuje;
- ktoré decisions sú fixed defaults;
- ktoré choices môže consumer meniť;
- ktoré constraints sú policy;
- aký je expected provisioning time;
- ako sa capability pozoruje;
- kto rieši incidenty;
- ako sa upgrade-ne, migruje a odstráni;
- čo platforma negarantuje.

UI form bez verziovaného capability contractu vedie k implicitným semantics, ktoré sa pri platform update-e nepredvídateľne menia.

## 6. Platform API a resource model

Silná IDP má machine-readable API alebo declarative resource model. Portal, CLI aj automation potom používajú rovnaký contract.

Napríklad:

```yaml
apiVersion: platform.example.io/v1
kind: Service
metadata:
  name: settlement-api
spec:
  owner: team-payments
  runtime:
    profile: kubernetes-standard
  delivery:
    profile: gitops-promoted
  data:
    - capability: postgres-ha
      name: settlements
  operations:
    tier: critical
```

Platform API nie je iba convenience wrapper. Je authority boundary nad platform intentom. Controller alebo workflow preloží high-level request na Git repositories, cloud resources, policies, catalog entities a runtime objects.

Dôležitý trade-off je abstraction leakage. Príliš nízka abstraction núti developera poznať provider detaily. Príliš vysoká abstraction môže skryť capacity, failure, cost alebo lifecycle decisions, ktoré application owner potrebuje rozumieť.

## 7. Control plane, orchestration a execution planes

Rozdelenie planes chráni authority a vysvetľuje, kde vzniká ktorý dôkaz. Experience plane prijíma intent a prezentuje projection, control plane drží operation state a decisions, execution planes vykonávajú mutations a workload plane poskytuje reálny application outcome.

Ak sa tieto vrstvy zlúčia do portal processu, UI response sa ľahko zamení za infrastructure alebo business success. Samostatné planes umožňujú aj to, aby portal mohol bezpečne zlyhať bez straty durable operation a aby backend policy nebola obídená priamym API clientom.

IDP možno rozdeliť:

### Experience plane

Portal, CLI, API documentation, catalog a status views. Získava request a prezentuje result.

### Platform control plane

Validuje intent, udržiava operation state, vyhodnocuje policy, orchestruje workflows a koreluje resources.

### Execution planes

Git providers, CI runners, IaC engines, cloud control planes, Kubernetes, GitOps controllers, secret managers a observability systems.

### Workload/data plane

Reálne application requests, databases, queues, network traffic a business operations.

Zelený experience plane nesmie nahradiť evidence z execution a workload plane-u.

## 8. Durable platform operation

Jedna self-service action je často distributed saga:

```text
reserve service identity
→ create repository
→ write catalog entity
→ create environment desired state
→ provision cloud resources
→ configure workload identity
→ configure secrets
→ install pipeline
→ reconcile runtime
→ verify service
```

Žiadna spoločná ACID transaction neobsiahne GitHub, cloud provider, Kubernetes a DNS. Platform potrebuje durable operation record:

```text
operation ID
subject fingerprint
requested capability/version
current step
per-system resource IDs
attempts a timestamps
partial outcomes
compensation eligibility
final verdict
```

Ak portal process spadne po repository creation, worker musí pokračovať alebo bezpečne kompenzovať. Nemá začať celý workflow od nuly bez read-backu.

## 9. Idempotency a identity reservation

Identity reservation serializuje semantic creation skôr, než workflow vykoná drahé alebo ťažko vratné side effects. Stable service identity potom slúži ako lookup key pri retry a umožňuje odlíšiť existujúci equivalent resource od collision s iným contractom.

Bez reservation sa duplicate repositories, namespaces, cloud IDs, DNS a IAM objects stanú rozdielnymi authority candidates. Neskoršia deduplikácia je nebezpečná, pretože každý z nich už môže mať vlastné data, permissions alebo users.

Platform request musí mať stable semantic identity. Príklad:

```text
team-payments + service settlement-api + capability service-v1
→ operation key
```

Prvý step často rezervuje global identity. Táto reservation zabraňuje, aby concurrent retries vytvorili:

- dve repositories s podobnými názvami;
- duplicate catalog entities;
- overlapping namespaces;
- druhé cloud resources s novými IDs;
- conflicting DNS alebo IAM roles.

Idempotency neznamená iba „HTTP POST vráti rovnakú odpoveď“. Každý downstream adapter musí vedieť read-before-create alebo používať provider idempotency token a potom overiť semantic equivalence existujúceho resource-u.

## 10. Authoritative systems a writer boundaries

IDP zvyčajne nevlastní všetok state priamo. Musí definovať authority graph:

```text
service identity a ownership
→ catalog alebo platform API authority

deployment desired state
→ environment Git repository

cloud resource desired state
→ platform API/IaC state

live Kubernetes reconciliation
→ GitOps controller

secret value
→ external secret authority/KMS

runtime status
→ Kubernetes/cloud/provider APIs
```

Portal database nesmie byť nezdokumentovaný druhý source of truth. Môže držať operation state a projections, ale authoritative identifiers a desired state musia byť explicitné.

Skrytý direct writer, napríklad portal meniaci cluster ConfigMap mimo GitOps, vytvára rovnaký multi-writer problém ako CI s production kubeconfigom.

## 11. Templates a scaffolding

Software template môže vytvoriť repository skeleton, CI config, catalog metadata a deployment manifests. Je užitočná pre first creation, ale template output sa po vytvorení typicky stáva copy.

Dva lifecycle models:

### Fire-and-forget template

```text
template version 1
→ generated repository
→ team vlastní divergence
```

Platform nevie automaticky propagovať neskoršiu opravu do všetkých repositories.

### Managed contract

Managed contract oddeľuje stable consumer interface od evolvujúcej platform implementation. Generated repository nemusí dostať každý nový file, ak zostáva napojený na versionovaný reusable pipeline, platform API alebo controller, ktorý platform team môže bezpečne upgradovať.

Aby táto väzba nebola hidden lock-in, contract musí byť pozorovateľný, testovateľný a migrovateľný. Input schema, version, output inventory, permission boundaries a migration strategy spolu určujú, či platforma vie meniť implementation bez tichého behavior driftu.

Generated repository odkazuje na versioned reusable components alebo platform API. Platform môže aktualizovať shared implementation pri zachovaní compatibility contractu.

Templates musia mať:

- input schema a validation;
- version identity;
- output inventory;
- secret-safe rendering;
- dry-run/preview;
- idempotent actions;
- permission boundaries;
- migration/deprecation strategy;
- tests nad positive aj forbidden inputs.

Template, ktorá iba vytvorí „best practice“ files, nie je trvalý guardrail.

## 12. Software catalog a ownership metadata

Catalog je projection software ecosystemu, nie automaticky authoritative runtime inventory. Jeho hodnota vzniká až vtedy, keď owner, API a resource relations možno korelovať s reálnymi Git, platform a runtime identities a keď stale alebo orphan entries vyvolajú remediation.

Otázky v tejto sekcii preto nie sú iba discovery convenience. Odpovede sa používajú pri impact analysis, incidente, deprecation, cost attribution a decommission-e a musia mať definovaný source a freshness.

Catalog modeluje components, APIs, resources, systems, domains, owners a relations. Jeho účelom nie je byť iba zoznamom odkazov.

Catalog metadata môže odpovedať:

- ktorý tím vlastní service;
- ktoré APIs implementuje a konzumuje;
- ktoré runtime resources mu patria;
- kde je source, documentation a dashboards;
- aký lifecycle a operational tier má;
- ktoré dependencies a risks existujú;
- či je orphaned alebo deprecated.

Catalog freshness je zásadná. YAML entity existujúca v Git-e nemusí znamenať, že service reálne existuje. Naopak cloud resource môže existovať bez catalog ownera. IDP potrebuje ingestion, reconciliation a orphan detection.

Nasledujúca samostatná kapitola o service catalogu rozoberie model detailnejšie; tu je catalog chápaný ako jedna z platformových state a discovery vrstiev.

## 13. Policy a guardrails

IDP má znižovať cognitive load bez odstránenia bezpečnostných boundaries. Policy sa môže presadiť:

```text
request schema
→ allowed choices a defaults

platform API admission
→ identity, quota, classification a topology constraints

Git/CI validation
→ rendered configuration a supply-chain evidence

cloud/Kubernetes admission
→ target effective enforcement

runtime controls
→ network, IAM, quotas a monitoring
```

UI-only validation nie je control. Request možno poslať cez API alebo underlying system. Critical guardrail musí existovať na authoritative mutation boundary.

Guardrail zároveň potrebuje vysvetlenie a remediation path. Nejasné `policy denied` vedie k bypassom a ticketom.

## 14. Self-service nie je unrestricted privilege

Self-service automatizuje vopred schválený action contract, nie prenos underlying administrator rights na každého requestera. Platform identity môže byť silnejšia než user identity, preto musí konať iba nad resource subjectom odvodeným z validovaných inputs a tenant policy.

Zakázané examples ukazujú, kde by abstraction prestala byť bounded capability. Arbitrary provider code, IAM role alebo production mutation by z platformy urobili confused deputy a odstránili audit, idempotency a recovery semantics.

Self-service znamená, že approved action možno vykonať bez manuálneho central ticketu v rámci vopred definovaného contractu.

```text
authenticated requester
+ team ownership
+ approved capability
+ bounded inputs
+ quota/policy
→ automated operation
```

Neznamená:

- cluster-admin pre každého developera;
- arbitrary Terraform execution;
- možnosť zvoliť ľubovoľnú IAM role;
- direct production mutation;
- cross-tenant secret access;
- obídenie cost alebo data controls.

Platform identity má vykonať iba actions odvodené z validovaného requestu a viazané na tenant scope.

## 15. Async UX a pravdivý status

Provisioning môže trvať minúty. HTTP request preto často iba vytvorí operation:

```http
POST /platform/services
→ 202 Accepted
→ operationId: op-8841
```

Status musí rozlišovať:

```text
RequestAccepted
Validating
Provisioning
WaitingForReconciliation
Verifying
Succeeded
```

A failures:

```text
Rejected
Blocked
Failed
PartiallySucceeded
Unknown
Compensating
ManualInterventionRequired
```

`202 Accepted` nie je service creation success. Portal má zobrazovať step, blocker, owner a actionable evidence. Optimistická zelená hláška po prvom downstream API call-e vytvára false-success contract.

## 16. Partial failure a compensation

Partial failure je normálny stav distributed platform operation, pretože Git, cloud, DNS a Kubernetes nemajú spoločnú transaction. Control plane musí vedieť, ktoré steps sa už stali authoritative, ktoré majú unknown outcome a ktoré možno bezpečne zopakovať.

Compensation nie je automatické vymazanie všetkého. Každý step potrebuje preconditions, pretože repository už môže obsahovať user commits, database data alebo DNS traffic a destructive rollback by mohol spôsobiť väčšiu škodu než zachovaný partial state.

Predstavme si:

```text
repository created
catalog entity created
database provisioning failed
```

Možnosti:

### Retry forward

Ak request je stále validný a failure transientný, workflow pokračuje od database step-u.

### Compensate

Odstráni repository a catalog entity, ak ešte neboli používané a deletion je safe.

### Preserve partial state

Resource zostane pre diagnostiku alebo manuálne dokončenie. Operation je explicitne partial.

Compensation nie je generický rollback. Deletion môže byť destructive, external email už mohol byť odoslaný a repository mohol dostať commits. Každý step potrebuje compensation eligibility a preconditions.

## 17. Verification vrstvy

Platform verification musí oddeliť existenciu resource-u od jeho integrácie a použiteľnosti. Provider môže reportovať available database, ale workload identity nemusí mať access; GitOps môže byť Ready, ale developer nemusí vedieť nasadiť prvú zmenu.

Preto sa provisioning, integration, developer-functional, operational a business evidence skladajú postupne. Každá vrstva uzatvára iný failure boundary a až ich kombinácia umožňuje označiť capability za usable.

Platform operation má viac oracles:

### Provisioning verification

Provider resource existuje a jeho observed state dosiahol required condition.

### Integration verification

IAM binding, secret reference, DNS, pipeline a GitOps source sú navzájom prepojené.

### Developer-functional verification

Owner sa vie autentizovať, pushnúť zmenu, deploynuť sample alebo pripojiť k capability.

### Operational verification

Logs, metrics, alerts, backup a support ownership fungujú.

### Business/application verification

Vytvorený service vykoná intended test journey.

Platforma môže byť technicky provisioned, ale nepoužiteľná pre developera pre chýbajúcu permission alebo nedokumentovaný output.

## 18. Platform observability

Platform observability musí odpovedať na dve odlišné otázky: či control plane spracúva operations spoľahlivo a či consumers dostávajú usable capabilities v sľúbenom čase. Samotné CPU, HTTP latency alebo successful task count neodhalia partial resources, stale projections ani developer journey failure.

Signály v zozname sledujú request lifecycle aj product outcome. Ich kombinácia umožňuje odlíšiť insufficient worker capacity, downstream throttling, poison request, policy friction, reconciliation lag, lifecycle debt a adoption problém.

IDP potrebuje observability podľa operation a capability subjectu:

- request rate, latency a rejection reasons;
- queue depth a oldest operation age;
- per-step success/failure/retry;
- downstream API latency a throttling;
- duplicate/idempotency conflict rate;
- partial/unknown operations;
- reconciliation lag;
- policy denials a common remediation gaps;
- time-to-first-successful-deploy;
- capability adoption a abandonment;
- support incidents a toil;
- orphan resources a failed decommissions;
- cost per capability/tenant.

Technical dashboard bez developer outcome môže optimalizovať nesprávnu vec. Rýchle repository creation nie je hodnotné, ak first production deployment trvá týždeň.

## 19. Platform SLO a dependency budgets

Platform SLO môže merať:

```text
valid request
→ usable capability within X time
```

Musí definovať exclusions a dependency behavior. Git provider outage, cloud API throttling alebo cluster incident môže ovplyvniť provisioning. Platform potrebuje timeout, retry a backpressure, aby dependency outage nevytvoril retry storm.

Queue admission môže prioritizovať recovery a production incident operations pred low-priority preview environments. Bez capacity controls môže masové self-service spustenie vyčerpať cloud API quota alebo controller workers.

## 20. Lifecycle: update, migrate a deprecate

Platform capability je dlhodobý contract, preto create predstavuje iba prvú transition. Existing consumers potrebujú version-aware updates, ownership transfer, credential rotation, migration a safe decommission bez straty identity alebo data.

Deprecation list opisuje riadený closure proces. Replacement, inventory, tooling, deadlines, evidence a final gate musia zostať prepojené, aby platforma nevypla capability na základe neúplného self-reportingu alebo ponechala permanentné exceptions.

IDP nie je iba creation engine. Musí podporovať:

```text
create
→ adopt
→ update
→ scale/change tier
→ rotate credentials
→ migrate capability version
→ transfer ownership
→ suspend
→ decommission
```

Capability version update potrebuje compatibility a migration plan. Platform API `v1` nemôže potichu zmeniť backup retention alebo network exposure pre existing resources.

Deprecation obsahuje:

- announced replacement;
- affected consumer inventory;
- migration tooling;
- deadlines a exceptions;
- progress evidence;
- final disable/delete gate;
- rollback alebo restore plan.

Platform, ktorá vie resources vytvárať, ale nie bezpečne odstraňovať, produkuje orphan cost a attack surface.

## 21. Multi-tenancy

Platform tenant identity musí prežiť prechod z requester session cez durable operation až do Git, cloud, secret a runtime resources. UI filter ani catalog owner label nie sú authorization; každý execution adapter musí znovu presadiť tenant-bound scope.

Identity, API, accounts, Git, IAM, secret paths, network, logs a cost attribution tvoria jeden isolation chain. Slabá jediná vrstva môže z platform identity urobiť confused deputy alebo umožniť noisy-neighbor tenantovi vyčerpať shared workers a quotas.

IDP tenant subject môže byť team, business unit, project alebo environment. Isolation musí existovať cez:

- identity a group membership;
- API authorization;
- namespace/account/project boundaries;
- Git repository permissions;
- cloud IAM a quotas;
- secret provider paths;
- network policies;
- catalog visibility;
- operation logs a support tooling;
- cost attribution.

Portal filter `show only my services` nie je authorization. Backend a underlying systems musia odmietnuť cross-tenant action.

Shared platform components potrebujú noisy-neighbor controls. Jeden tenant s tisíckami requests nesmie blokovať production recovery iného.

## 22. Security threat model

IDP je privileged automation control plane, preto threat model sleduje, ako untrusted request alebo compromised plugin využije platform identity. Každý threat sa posudzuje podľa vstupnej boundary, získanej authority, possible side effectu a evidence potrebnej na detection a containment.

Scenáre pokrývajú requester identity, template execution, third-party tokens, egress, distributed retries a projections. Spoločnou otázkou je, či platforma môže vykonať action, ktorú samotný používateľ vykonať nesmie, a ak áno, čo ju viaže na schválený operation subject.

IDP je high-value control plane, pretože dokáže vytvárať identities, repositories, cloud resources a production desired state.

Threats:

- compromised developer account požiada o privilege escalation;
- malicious template input vykoná command alebo path injection;
- plugin získa broad third-party token;
- workflow logs secret;
- confused deputy použije platform identity na cudzí tenant;
- stale approval sa aplikuje na zmenený request;
- SSRF alebo arbitrary URL source umožní exfiltration;
- compromised platform worker zmení Git/cluster mimo operation;
- catalog metadata odhalí sensitive topology;
- duplicate retry vytvorí unmanaged resources.

Controls musia pokryť request authorization, template sandboxing, egress, token scoping, audit, policy, supply chain a runtime isolation.

## 23. Backstage ako portal framework

Backstage poskytuje composable experience a integration primitives, ale neurčuje autoritatívny resource model ani distributed transaction semantics celej platformy. Každý plugin alebo scaffolder action môže volať underlying API s vlastným tokenom a failure behaviorom.

Preto treba rozlíšiť Backstage task completion od IDP capability acceptance. Portal framework môže vytvoriť proposal alebo resource, no durable control plane musí ďalej sledovať reconciliation, runtime a developer-functional outcome.

Backstage poskytuje composable building blocks:

### Software Catalog

Centralizuje metadata a relations software ecosystemu.

### Software Templates

Scaffolder vykonáva template steps a môže vytvárať repositories alebo ďalšie resources.

### TechDocs

Publikuje docs-as-code spojené s component ownershipom.

### Plugins

Integrujú CI/CD, Kubernetes, cloud, security a ďalšie systems do jednotného UX.

Backstage architektúra nepredpisuje celý IDP control plane. Custom actions a plugins môžu robiť direct side effects; organizácia musí doplniť durable operation, authorization, idempotency, secrets a failure handling. Template task `completed` môže znamenať, že steps skončili, nie že GitOps workload je business accepted.

## 24. Connected incident `GITOPS-PAY-62`

LaunchPad workflow treba analyzovať ako distributed operation, ktorej UI task log zachytil iba skoré side effects. Každý vykonaný step vytvoril state v inom authoritative systeme, ale portal nemal persisted resource IDs a completion oracle, ktorý by ich spojil s Flux runtime a business canary.

Repository a catalog creation boli úspešné local outcomes, no direct ConfigMap write a promotion PR zároveň zaviedli hidden authority a ešte nepreukázali usable production capability. Označenie `Completed` preto bolo false-success verdictom, nie iba nepresným textom v UI.

LaunchPad mal developerovi umožniť:

```text
choose payments-service template
→ create repository
→ register catalog entity
→ create staging/prod environment desired state
→ configure Flux
→ configure SOPS/KMS
→ promote release
→ verify production
→ mark operation complete
```

Actual workflow:

1. vytvoril repository;
2. zapísal catalog entity;
3. vytvoril shared cluster ConfigMap `launchpad-runtime`;
4. otvoril promotion PR;
5. po úspešnej GitHub API odpovedi označil task `Completed`.

Workflow nemal durable operation beyond portal task log. Pri timeout-e používateľ klikol `Retry`, čím vznikla druhá operation. Repository create bolo náhodou idempotentné podľa názvu, ale ConfigMap update a promotion PR neboli viazané na rovnaký semantic operation.

Portal zároveň použil `launchpad-runtime` ako `postBuild.substituteFrom` pre production Flux Kustomization. Tým sa portal stal hidden desired-state writerom mimo Git-u.

LaunchPad zobrazoval:

```text
Service: settlement-api
Environment: production
Status: Ready
Release: pay910a
```

Skutočný state bol:

```text
catalog metadata:       pay910a requested
promotion approval:     pay910a / route 1850
Flux render:            pay910b / route 1849
running workload:       pay910b / loaded secret pv-42
provider authority:     pv-43
business canary:        failed/not executed by portal
```

### IDP root cause

Portal task completion bol zamenený za platform capability acceptance. Platform nemala durable cross-system operation subject, portal database obsahovala neautoritatívnu release projection, critical ConfigMap bola direct-written mimo Git a retry nebol end-to-end idempotentný.

### Redesign

Redesign presúva authority z portal tasku do declarative platform resource-u a durable controller operation. Portal prijme request a zobrazuje projection; control plane udržiava step state, downstream IDs a recovery a GitOps/runtime systems poskytujú acceptance evidence.

Operation sa môže bezpečne resume-nuť po process alebo provider failure. Rovnaký operation ID zabráni duplicate resources a status `Succeeded` vznikne až po developer-functional a business verification, nie po prvom úspešnom API call-e.

```text
LaunchPad request op-8841
→ validate team/service/capability/version
→ reserve service identity
→ create declarative PlatformService resource
→ platform controller creates Git PRs a provider requests
→ persist exact downstream IDs
→ GitOps observes authoritative commits
→ runtime exposes artifact/config/secret generations
→ production canary
→ catalog projection updated from authoritative evidence
→ operation op-8841 Succeeded
```

Critical desired state sa mení iba Git/Platform API authority. Portal je client a projection layer, nie direct cluster writer.

## 25. IDP acceptance verdict

IDP acceptance hodnotí platformu ako distributed product system. Musí byť súčasne bezpečná pre tenantov, spoľahlivá pri partial a unknown outcomes a použiteľná pre developera; úspech iba jednej z týchto osí nestačí.

Verdict spája request identity, durable operation, authoritative writers, effective resources a user outcome. Jeho rozhodujúcim testom je opakovaný rovnaký request po controller restarte alebo dependency failure, ktorý musí obnoviť ten istý resource graph a pravdivý status.

IDP design je prijatý, keď:

- capability contracts, versions, inputs, outputs a boundaries sú explicitné;
- portal, platform API, control plane a execution planes sú oddelené;
- every request má exact subject, owner, tenant a idempotency key;
- distributed workflow používa durable operation state a downstream resource IDs;
- retries vykonávajú read-back a semantic idempotency;
- authoritative systems a writer boundaries sú zdokumentované;
- portal projections nemožno zameniť za desired alebo live authority;
- templates sú versionované, testované, secret-safe a majú migration model;
- policy je enforced na authoritative boundaries, nie iba v UI;
- self-service permissions sú least-privilege a tenant-scoped;
- async status rozlišuje accepted, provisioning, partial, unknown a verified;
- compensation je per-step bounded a non-destructive by default;
- technical, developer-functional, operational a business verification sú oddelené;
- catalog ownership a resource relationships sú reconciled a orphan-detectable;
- update, migration, ownership transfer a decommission sú first-class lifecycles;
- platform SLO meria usable outcome a chráni dependencies backpressure-om;
- compromised account, malicious input, duplicate retry, downstream timeout, stale status, partial failure, controller restart a second-request tests prejdú;
- hidden direct writer, cross-tenant action, false-success portal state a orphan resource outcomes sú odmietnuté.

## 26. Troubleshooting flow

Troubleshooting začína exact operation ID a semantic requestom, pretože portal status alebo resource name nemusia identifikovať všetky retries a partial side effects. Z operation ledgeru sa postupuje do jednotlivých authoritative systems a porovnáva sa intended output inventory s read-back evidence.

Recovery sa volí podľa prvého neuzavretého boundary: workflow možno resume-nuť, bezpečne compensate-nuť alebo odovzdať manual ownerovi. Po oprave sa zopakuje developer-functional test aj identický request, aby sa preukázala end-to-end idempotency.

```text
Portal tvrdí success, ale capability nefunguje
→ exact requester/team/capability/operation ID
→ request schema/policy/version
→ durable step state a attempts
→ downstream Git/cloud/IaC/Kubernetes IDs
→ authoritative desired-state commits
→ controller observed revisions a runtime resources
→ identity/secret/network integration
→ developer-functional test
→ operational/business oracle
→ projection freshness a writer inventory
→ resume/compensate/repair
→ second identical request validation
```

## 27. Anti-patterny

### Nainštalujeme Backstage a máme IDP

Backstage môže byť portal framework. IDP potrebuje capabilities, APIs, orchestration, policies, lifecycle, support a outcome verification.

### Template je golden path navždy

Generated copy diverguje. Bez managed contracts a migrations sa best practice prestane propagovať.

### Portal status je source of truth

Portal často drží projection. Authority musí zostať v explicitnom Git, platform API, provider alebo runtime state-e.

### Self-service znamená odstrániť approvals a limits

Self-service automatizuje approved bounded actions. Neznamená unrestricted production privilege.

### Keď jeden step zlyhá, vymažeme všetko

Blind compensation môže odstrániť resource, ktorý už používateľ alebo ďalší workflow používa. Potrebné sú preconditions.

### Retry spustí workflow od začiatku

Bez semantic idempotency vytvorí duplicates a conflicting side effects.

### Platform vytvára resources, lifecycle je hotový

Update, ownership transfer, rotation, migration a decommission sú rovnako dôležité ako create.

### Všetky tímy musia používať jednu abstraction

Platform má ponúkať bounded paths podľa potrieb. Universal abstraction môže byť príliš rigidná alebo skryť relevantné trade-offy.

## 28. Kontrolné otázky

1. Ako sa platform engineering, IDP a developer portal líšia?
2. Čo tvorí exact platform request subject?
3. Aké vlastnosti musí mať capability contract?
4. Prečo platform API nie je iba wrapper nad provider API?
5. Ako sa experience, control, execution a workload planes odlišujú?
6. Prečo self-service workflow potrebuje durable operation state?
7. Ako semantic idempotency zabraňuje duplicate resources?
8. Kde majú zostať authoritative desired-state writers?
9. Prečo template output po čase diverguje?
10. Ako catalog metadata pomáha ownershipu a kde môže byť stale?
11. Prečo UI validation nie je dostatočný guardrail?
12. Ako sa `202 Accepted` líši od successful capability creation?
13. Kedy retry forward, compensation a manual intervention dávajú zmysel?
14. Aké verification vrstvy musí IDP oddeliť?
15. Prečo LaunchPad v `GITOPS-PAY-62` vytvoril false-success stav?
16. Čo musí overiť second identical request po controller restarte?

## Glossary impact

Relevantné pojmy: platform engineering, Internal Developer Platform, internal developer portal, platform capability, capability contract, platform request subject, platform API, experience plane, platform control plane, execution plane, durable platform operation, platform idempotency, identity reservation, platform authority graph, scaffolding template, catalog projection, self-service boundary, platform compensation, developer-functional verification, platform SLO, capability lifecycle a IDP acceptance verdict.

## Primárne zdroje

- [CNCF — Platforms for Cloud Native Computing](https://www.cncf.io/blog/2023/04/11/announcing-a-white-paper-on-platforms-for-cloud-native-computing/)
- [CNCF — Platform Engineering Maturity Model](https://www.cncf.io/blog/2023/11/20/announcing-the-platform-engineering-maturity-model/)
- [Backstage — What is Backstage?](https://backstage.io/docs/overview/what-is-backstage/)
- [Backstage — Technical Overview](https://backstage.io/docs/overview/technical-overview/)
- [Backstage — Software Catalog](https://backstage.io/docs/features/software-catalog/)
- [Backstage — Software Templates](https://backstage.io/docs/features/software-templates/)
- [Backstage — Security and Threat Model](https://backstage.io/docs/overview/threat-model/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: GitOps secrets](gitops-secrets.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
