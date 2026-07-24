# Immutable vs. Mutable Infrastructure

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Desired State and Reconciliation](desired-state-and-reconciliation.md)
- Súvisiace témy: images, configuration management, containers, deployments, rollback, drift

## 1. Definícia

**Mutable infrastructure** sa počas životnosti mení priamo na mieste. Existujúci server, VM alebo appliance dostáva nové balíky, konfiguráciu a application verzie, pričom jeho aktuálny stav je výsledkom celej histórie predchádzajúcich zmien.

**Immutable infrastructure** preferuje replacement. Pri významnej zmene sa vytvorí nový verziovaný artifact alebo resource, ten sa otestuje, nasadí vedľa starej verzie a po overení prevezme traffic alebo workload.

```text
Mutable:   server → patch → config change → ďalší patch
Immutable: artifact v1 → artifact v2 → nové instances → cutover → odstránenie v1
```

Immutable neznamená, že resource je fyzicky read-only. Znamená, že jeho podporovaný lifecycle nepovažuje nezdokumentovanú in-place modifikáciu za normálny spôsob release-u.

## 2. Prečo tento rozdiel existuje

Mutable resource časom akumuluje history-dependent state. Dva servery vytvorené z rovnakého image sa môžu po mesiacoch líšiť, pretože dostali patch v inom poradí, jeden prežil manuálny hotfix a druhý bol počas maintenance nedostupný.

Immutable model presúva zmenu do reprodukovateľného build a rollout procesu. Namiesto otázky „aké príkazy už na tomto serveri prebehli?“ sa systém pýta „z akého artifact digestu bol tento resource vytvorený a aká deklarovaná konfigurácia mu bola priradená?“

## 3. Mentálny model: artifact, instance, state a traffic

Kvalitný immutable návrh oddeľuje štyri veci. Artifact obsahuje verziovaný software baseline, instance je konkrétne spustenie artifactu, durable state prežíva replacement a traffic routing určuje, ktorá verzia obsluhuje používateľov.

```text
source + dependencies + build configuration
→ immutable artifact identity
→ disposable compute instances
→ external durable state
→ health validation
→ traffic promotion
```

Ak sa durable state alebo kritická konfigurácia skryto nachádza iba vo writable vrstve instance, compute v skutočnosti nie je bezpečne nahraditeľný. „Immutable“ potom opisuje iba spôsob deploymentu, nie reálnu recoverability systému.

## 4. Mutable lifecycle

Mutable lifecycle vytvorí resource a následne ho udržiava sériou in-place zmien. Configuration management môže tento proces silno štandardizovať, no výsledný server stále nesie históriu predchádzajúcich operations a partial failures.

```text
provision VM
→ configure baseline
→ deploy application v1
→ patch OS
→ deploy v2
→ emergency hotfix
→ ďalšia configuration convergence
```

Výhodou je, že netreba pri každej zmene nahradiť celý resource. Nevýhodou je náročnejšia reprodukcia, rollback a dokazovanie, že všetky instances prešli rovnakou sekvenciou úspešne.

## 5. Immutable lifecycle

Immutable lifecycle vytvorí nový artifact pre konkrétnu zmenu a starý runtime nemení. Nová verzia prejde testovaním, provisioningom, readiness a controlled traffic shiftom skôr, než sa predchádzajúca verzia odstráni.

```text
source revision
→ reproducible build
→ signed/versioned artifact
→ test
→ create new capacity
→ readiness a smoke validation
→ canary alebo traffic switch
→ retire old capacity
```

Replacement je úspešný až po odstránení starej verzie a potvrdení nového effective state-u. Ak staré zraniteľné instances ostanú bežať mimo load balancera, rollout síce zmenil traffic, ale patch lifecycle nie je dokončený.

## 6. Artifact identity

Immutable model stojí na jednoznačnej identity artifactu. Container tag `latest`, prepísateľný package name alebo VM image bez build provenance neumožňuje spoľahlivo určiť, čo bolo testované a čo reálne beží.

Použiteľná identity môže byť container digest, AMI ID, package checksum alebo podpísaná release verzia. Promotion má presúvať ten istý artifact medzi prostrediami; rebuild pre production vytvára nový vstup, na ktorý sa staging dôkazy nevzťahujú.

## 7. Build reproducibility

Replacement model presúva riziko do build pipeline. Ak build používa nepinned dependencies, pohyblivé base images alebo nedokumentované externé vstupy, rovnaký source commit môže vytvoriť rozdielny artifact.

Reprodukčný contract má definovať source revision, dependency lock, base artifact digest, toolchain, build parameters a výsledný checksum. Úplná bit-for-bit reprodukovateľnosť nemusí byť vždy praktická, ale všetky významové vstupy musia byť identifikované a auditovateľné.

## 8. Bootstrapping a runtime configuration

Image nemá nevyhnutne obsahovať všetku environment configuration. Často obsahuje stabilný software baseline a pri štarte načíta environment-specific values, identity alebo secrets z autorizovaného source-u.

Rozhranie medzi build-time a runtime configuration musí byť presné:

- **Build-time content —** aplikácia, OS packages a runtime dependencies; zmena vyžaduje nový artifact a nový rollout.
- **Runtime configuration —** environment endpointy, feature settings alebo resource limits; musí byť versioned, validovaná a kompatibilná s artifactom.
- **Secrets —** načítavajú sa cez identity-bound delivery a nesmú sa piecť do všeobecne distribuovaného image.
- **Bootstrap logic —** má byť bounded a pozorovateľný; ak pri každom štarte vykonáva rozsiahle nepinned inštalácie, výhoda immutable image sa stráca.

Príliš tenký image s neobmedzeným startup scriptom iba presunie mutable provisioning do boot času. Výsledné instances potom nemusia byť identické, hoci používajú rovnaké image ID.

## 9. Configuration drift

Mutable drift vzniká, keď jednotlivé resources dostávajú rozdielne zmeny alebo keď niektorý krok zlyhá iba na časti fleet-u. Configuration-management agent môže drift detegovať a opravovať, no musí mať autoritatívny desired state a pravidelne dokazovať convergence.

Immutable model drift znižuje tým, že instances jednej verzie vznikajú z rovnakého artifactu a neudržiavajú sa individuálne. Drift však môže stále vzniknúť v runtime configuration, attached policies, network rules, mounted volumes alebo manuálne zmenených cloud attributes.

## 10. VM images

Pri VM replacement modeli image pipeline vytvorí nový AMI alebo ekvivalentný template, spustí test instance a po schválení aktualizuje launch template. Auto Scaling Group alebo deployment orchestrator následne vytvára nové instances a staré kontrolovane odoberá.

```text
patched source image
→ image build
→ vulnerability a boot test
→ launch template revision
→ instance refresh
→ health validation
→ old instance termination
```

Image success nie je dôkaz fleet success. Rollout musí sledovať launch errors, capacity, warm-up, load-balancer registration a percento starých instances, ktoré ešte zostávajú.

## 11. Containers

Container image je immutable artifact, no bežiaci container má zvyčajne writable layer. Táto vrstva je určená pre dočasný runtime state, nie pre manuálne opravovanie application verzie.

`exec` hotfix môže dočasne obnoviť službu, ale po reschedulingu zmizne a ďalšie replicas ho nemajú. Incidentná zmena sa preto musí preniesť do source, Dockerfile alebo deklarovanej konfigurácie a následne prejsť normálnym build a rollout procesom.

## 12. Kubernetes rollout

Kubernetes Deployment pri zmene Pod template vytvorí nový ReplicaSet a postupne nahrádza Pody. Rollout stratégie určujú, koľko starej a novej kapacity môže existovať súčasne a ako sa reaguje na unavailable alebo unready replicas.

- **Rolling update —** postupne mieša starú a novú verziu; vyžaduje ich dočasnú kompatibilitu s trafficom aj shared data modelom.
- **Canary —** vystaví novú verziu obmedzenej časti trafficu alebo workloadu; potrebuje merateľné promotion criteria.
- **Blue-green —** drží samostatnú starú a novú fleet-u a prepína routing; spotrebuje viac kapacity, ale poskytuje jasnejšiu rollback path.
- **Recreate —** najprv odstráni starú verziu a potom vytvorí novú; môže byť potrebné pri nekompatibilnom exclusive resource, no vytvára downtime.

Kubernetes nahrádza Pody, ale external data a migration semantics zostávajú zodpovednosťou aplikácie. Image rollback nedokáže automaticky vrátiť nevratnú databázovú zmenu.

## 13. Externý durable state

Nahraditeľný compute nesmie byť jediným vlastníkom dát, ktoré musia prežiť jeho zánik. Durable state sa preto presúva do databázy, persistent volume, object storage, queue alebo iného systému s explicitnou durability a recovery politikou.

- **Databázové dáta —** potrebujú transakčný a backup model nezávislý od application instances.
- **Uploaded files —** patria do persistent alebo object storage, nie iba na lokálny filesystem Podu.
- **Queue state —** musí prežiť replacement consumera a zachovať acknowledgement alebo lease semantics.
- **Sessions —** pri nahraditeľných replicas sa externalizujú alebo používajú cryptographically self-contained tokens podľa security modelu.
- **Runtime cache —** môže byť lokálna iba vtedy, ak je obnoviteľná a jej strata neporuší correctness.

Externalizácia state-u nevyrieši availability sama. Stateful dependency sa stáva samostatnou kritickou vrstvou s vlastným patching, scaling, backup a failover lifecycle-om.

## 14. Stateful systems

Databázu alebo message broker nemožno vždy bezpečne nahradiť rovnakým spôsobom ako stateless web server. Replacement môže vyžadovať replication, leader transfer, data rebalancing, schema compatibility a kontrolovaný membership change.

Immutable princíp sa tu často aplikuje na software image alebo node baseline, zatiaľ čo data state sa migruje mutable protokolom. Nový database node sa vytvorí z nového image, pripojí sa ako replica, dobehne replication a až potom prevezme rolu starého node-u.

## 15. Patching

Mutable patching aplikuje update na existujúci resource a overuje jeho výsledok. Je vhodné tam, kde replacement trvá neprimerane dlho, resource má komplexný local state alebo vendor podporuje iba in-place upgrade.

Immutable patching vytvorí nový patched artifact a nahradí fleet-u. Tento model zlepšuje reprodukovateľnosť a rollback software baseline-u, ale potrebuje rýchly image pipeline, dostatočnú spare capacity a inventory, ktoré odhalí stale resources.

Patch SLA musí merať čas do odstránenia poslednej zraniteľnej aktívnej instance, nie iba čas vytvorenia nového image. Neaktualizovaný autoscaling template môže po incidente znovu vytvoriť starú verziu.

## 16. Rollback a roll-forward

Immutable rollout často umožní vrátiť routing na predchádzajúci artifact. Táto výhoda platí iba vtedy, keď stará verzia zostáva kompatibilná s aktuálnym data a protocol state-om.

Rollback môže byť blokovaný týmito zmenami:

- **Databázová migrácia —** starý application code nemusí rozumieť novej schema alebo zmazanému stĺpcu.
- **Message format —** nová verzia mohla publikovať event, ktorý starý consumer nevie spracovať.
- **Externý side effect —** odoslanú platbu alebo e-mail nemožno vrátiť iba zmenou image.
- **Security revocation —** rollback na artifact so zraniteľnosťou alebo kompromitovaným keyom nie je prípustný.
- **Configuration contract —** stará verzia nemusí podporovať nové mandatory values.

Expand-contract migrácie, versioned protocols a backward-compatible changes rozširujú rollback window. Ak návrat nie je bezpečný, deployment potrebuje overený roll-forward alebo compensation plán.

## 17. Traffic cutover

Replacement potrebuje mechanizmus, ktorý rozhodne, kedy nová verzia smie obsluhovať workload. Health check má overovať schopnosť prijímať traffic, nie iba existenciu procesu.

Cutover model rieši readiness, connection draining, session affinity, DNS alebo load-balancer propagation a in-flight requests. Pri scale-in sa stará instance najprv vyradí z routingu, dokončí alebo odovzdá rozpracovanú prácu a až potom sa ukončí.

## 18. Capacity a quotas počas rollout-u

Immutable rollout dočasne potrebuje starú aj novú kapacitu. Pri blue-green môže byť potrebná takmer dvojnásobná compute, IP, load-balancer target alebo database-connection capacity.

Ak subnet nemá voľné IP adresy alebo account narazí na quota, nová fleet-a nevznikne a stará sa nesmie odstrániť. Deployment preto musí rezervu a quotas validovať pred destructive krokom.

## 19. Emergency changes

Pri incidente môže byť najrýchlejšou mitigáciou kontrolovaná mutable zmena. Taký zásah nie je automaticky nesprávny, ale musí mať ownera, audit, bounded scope a plán návratu do source of truth.

```text
break-glass mitigation
→ zaznamenať presný diff
→ stabilizovať službu
→ implementovať trvalú source zmenu
→ build a rollout
→ odstrániť dočasnú mutáciu
→ overiť convergence
```

Ak sa hotfix nezapíše späť, ďalší replacement incident obnoví. Ak sa source upraví bez odstránenia live odchýlky, môžu sa dve implementácie neskôr stretnúť v nepredvídateľnom stave.

## 20. Configuration management v oboch modeloch

Ansible, Puppet alebo podobný nástroj neurčuje, či je infraštruktúra mutable alebo immutable. Rozhodujúce je, či nástroj pravidelne mení production instances alebo pripravuje artifact pred ich vytvorením.

- **Mutable použitie —** agent alebo playbook konverguje existujúce servers k desired configuration; musí riešiť drift, partial fleet failure a rollback.
- **Image build použitie —** configuration logic vytvorí AMI alebo image; production rollout následne používa replacement.
- **Bootstrap použitie —** pri štarte doplní environment-specific minimum; príliš rozsiahly bootstrap však znovu vytvára history-dependent instances.

Hybrid je bežný a legitímny. Potrebné je jasne určiť, ktorá vrstva sa mení akým lifecycle-om a kde je jej source of truth.

## 21. Security a supply-chain dôsledky

Immutable artifact možno skenovať, podpisovať a viazať na provenance pred deploymentom. Runtime policy potom povoľuje iba schválené digests, čím sa znižuje priestor pre neauditované zmeny.

Tento model však presúva vysokú dôveru do build pipeline, registry a signing keys. Kompromitovaný builder môže konzistentne distribuovať malicious artifact do celej fleet-y, preto replacement potrebuje supply-chain controls a staged rollout.

## 22. Inventory a garbage collection

Organizácia musí vedieť, ktoré artifact verzie existujú, kde bežia a či sú stále podporované. Bez inventory sa staré images, stopped VMs, snapshots a nepoužívané launch templates stávajú security aj cost dlhom.

Garbage collection nesmie odstrániť poslednú použiteľnú rollback alebo recovery verziu pred uplynutím policy okna. Retention má vyvažovať bezpečný rollback, incident forensics, storage cost a povinnosť odstrániť zraniteľné artifacts.

## 23. Kedy je mutable model primeraný

Mutable model je vhodný, keď replacement nie je podporovaný, je extrémne drahý alebo by vyvolal väčšie riziko než kontrolovaný in-place update. Typickým príkladom môže byť stateful appliance, veľká databáza alebo legacy systém s vendor upgrade procedúrou.

Primeraný mutable model potrebuje rovnakú disciplínu: declarative baseline, idempotent automation, inventory, canary patching, pre/post validation, rollback alebo recovery a pravidelný rebuild test. „Mutable“ nesmie znamenať ručné a nezdokumentované SSH zásahy.

## 24. Hybridný architektonický model

Reálny systém často kombinuje immutable application compute s mutable stateful services a dynamickou deklaratívnou konfiguráciou. Každá časť má inú replacement cost a consistency boundary.

```text
container image       → immutable replacement
Kubernetes manifests  → declarative reconciliation
database schema       → controlled compatible migration
persistent data       → replicated a backed-up mutable state
incident mitigation   → temporary audited imperative action
```

Kvalita hybridu závisí od rozhraní. Application rollout, schema migration a message compatibility musia byť koordinované tak, aby počas transition existovala funkčná kombinácia starých aj nových komponentov.

## 25. Observability

Deployment telemetry má rozlišovať artifact identity, desired fleet version, skutočne bežiace versions a traffic share. Samotný status rollout jobu neodhalí stale instance mimo orchestration scope-u.

Sleduj najmä percento capacity podľa digestu, readiness time, replacement failures, old-instance age, bootstrap errors, configuration drift a počet emergency mutations. Inventory query musí vedieť odpovedať, kde ešte beží zraniteľná alebo nepodporovaná verzia.

## 26. End-to-end príklad

Webová služba používa container image, Kubernetes Deployment a managed database. Pipeline vytvorí image digest, vykoná testy a podpis, staging aj production promujú ten istý digest.

Production rollout vytvorí canary replicas, overí technical aj business metrics a následne zvýši traffic. Databázová zmena používa expand-contract: najprv pridá backward-compatible schema, potom sa nasadí nový code a až po rollback window sa odstráni staré pole.

Ak canary zlyhá pred destructive migration fázou, routing sa vráti na predchádzajúci digest. Ak bol problém spôsobený dátovým side effectom, image rollback sa nepovažuje za úplnú recovery a spustí sa samostatný reconciliation alebo compensation postup.

## 27. Troubleshooting

Pri rozdielnom správaní replicas najprv porovnaj artifact digest, runtime configuration a attached state. Rovnaký tag alebo application version string nemusí znamenať rovnaký obsah.

- **Nové instances neštartujú —** over image permissions, architecture, bootstrap dependencies, secrets a launch-template revision.
- **Rollout stojí bez progresu —** over capacity, subnet IPs, quotas, readiness a max surge/unavailable policy.
- **Časť fleet-y ostala stará —** over orchestration scope, detached instances, autoscaling template a replacement cancellation.
- **Rollback nepomohol —** skontroluj database schema, message state, external side effects a configuration compatibility.
- **Po replacement zmizli dáta —** aplikácia používala skrytý local state alebo volume s nesprávnym lifecycle-om.
- **Instances s rovnakým image sa líšia —** hľadaj mutable bootstrap, environment drift alebo manuálne runtime zásahy.

## 28. Anti-patterny

### Golden server

Jeden dlhodobo ručne upravovaný server slúži ako nezdokumentovaný vzor. Jeho stav nemožno spoľahlivo reprodukovať, testovať ani bezpečne nahradiť.

### Pohyblivý artifact tag

Tag `latest` alebo rovnaká verzia ukazuje na meniaci sa obsah. Audit, rollout aj rollback strácajú jednoznačnú identity a nemožno dokázať, čo bolo nasadené.

### SSH hotfix bez convergence

Incidentná oprava ostane iba na jednej instance a ďalší rollout ju odstráni. Zmena sa musí preniesť do source of truth a temporary mutation sa následne zruší.

### Immutable compute so skrytým local state-om

Architektúra predpokladá replacement, no application drží kritické uploads, sessions alebo queues iba lokálne. Zlyhanie alebo scale-in potom spôsobí data loss.

### Rebuild per environment

Každé prostredie si vytvorí vlastný artifact. Testované bits nie sú identické s production bits a rozdiel môže vzniknúť v dependency resolution alebo build environment-e.

### Staré resources sa neodstraňujú

Nová verzia prevezme traffic, ale stará fleet-a, launch template alebo image ostáva použiteľná. Patching a security closure preto nie sú dokončené.

## 29. Kontrolné otázky

1. Prečo mutable resource závisí od histórie vykonaných zmien?
2. Aký je rozdiel medzi immutable artifactom a disposable instance?
3. Prečo pohyblivý tag ruší auditovateľnosť immutable modelu?
4. Ktoré údaje musia byť externalizované pred bezpečným replacementom compute-u?
5. Ako bootstrap script môže znovu zaviesť mutability do immutable image modelu?
6. Prečo patch SLA nekončí vytvorením nového image?
7. Kedy image rollback nedokáže obnoviť predchádzajúci business state?
8. Ako expand-contract migrácia predlžuje rollback window?
9. Prečo immutable rollout potrebuje capacity a quota headroom?
10. Ako sa má incidentný mutable hotfix vrátiť do source of truth?
11. Kedy je kontrolovaný mutable model primeranejší než replacement?
12. Aké telemetry dokazujú, že stará verzia už nikde aktívne nebeží?

## 30. Zhrnutie

Mutable a immutable infrastructure nie sú súboj nástrojov, ale rozdielne resource lifecycle-y. Mutable model mení existujúci resource a musí kontrolovať históriu, drift a partial fleet state; immutable model vytvára verziovaný artifact, nahrádza compute a potrebuje externalizovaný durable state, bezpečný traffic cutover a dôslednú garbage collection.

Silný produkčný návrh býva hybridný. Každej vrstve priradí lifecycle podľa jej state, replacement costu a failure semantics a potom explicitne navrhne kompatibilitu medzi application artifactom, konfiguráciou, dátami a migration procesom.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Desired state a reconciliation](desired-state-and-reconciliation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Toil a technical debt →](toil-and-technical-debt.md)
<!-- KNOWLEDGE-NAVIGATION:END -->