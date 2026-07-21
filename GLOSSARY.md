# Glossary

Rýchly referenčný index technických pojmov používaných v Knowledge Hube. Glossary nenahrádza plné kapitoly: každé heslo obsahuje stručnú definíciu a odkaz na autoritatívny článok, ak už existuje.

## A/B testing

Kontrolovaný produktový experiment porovnávajúci výsledok kontrolnej a experimentálnej skupiny podľa vopred definovanej hypotézy a metrík. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Abort criterion

Vopred definovaná podmienka, pri ktorej sa rollout alebo experiment okamžite zastaví, pretože dopad prekročil prijateľnú hranicu. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md) a [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Acceptance test

Test overujúci, či systém spĺňa dohodnuté business alebo používateľské acceptance criteria. Môže bežať na API, UI alebo inej vrstve. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## ACL — Access Control List

Rozšírený model oprávnení nad rámec owner/group/other mode bits. Pozri [Users, groups, permissions, sudo a PAM](docs/01-linux-and-systems/users-groups-permissions-sudo-pam.md).

## Advanced function — PowerShell

PowerShell function s `[CmdletBinding()]`, common parameters, parameter binding a cmdlet-like error/output správaním. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Advisory gate

Quality gate, ktorý reportuje výsledok, ale neblokuje ďalší delivery krok. Používa sa pri zavádzaní alebo kalibrácii kontroly. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Alias — YAML

YAML referencia na node označený anchorom. Znižuje duplicitu, ale môže komplikovať tooling a čitateľnosť. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Allowed failure

Pipeline stav, pri ktorom zlyhanie jobu zostane viditeľné, ale neblokuje definovaný downstream alebo celkový pipeline result. Musí mať explicitný dôvod a ownership. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## ALPN — Application-Layer Protocol Negotiation

TLS extension, ktorou klient a server počas handshake dohodnú aplikačný protokol, napríklad `http/1.1` alebo `h2`. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Ambient capability

Linux capability, ktorú môže proces za presných podmienok zachovať pri `execve()` neprivilegovaného programu. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Anchor — YAML

YAML mechanizmus pomenovania node, na ktorý môže odkazovať alias. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Annotated tag

Git tag reprezentovaný samostatným tag objectom s targetom, taggerom, časom, message a voliteľným kryptografickým podpisom. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Anycast

Routing model, v ktorom viac lokalít oznamuje rovnakú IP adresu a routing privedie klienta k topologicky preferovanému endpointu. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## API contract

Dohoda o observable API behavior zahŕňajúca paths, methods, schemas, status codes, errors, authentication, compatibility a ďalšie semantics. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## API test

Runtime test verejného API rozhrania overujúci response, semantics, authorization a side effects. Jeho scope môže byť component, integration alebo E2E. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## AppArmor profile

Mandatory Access Control profil definujúci povolené paths, execute transitions, capabilities, network operations a ďalšie správanie programu. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Approval — CI/CD

Explicitné rozhodnutie oprávnenej identity, ktoré povoľuje merge, promotion, deployment alebo release na základe definovaného rizika a dostupnej evidence. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## ARP — Address Resolution Protocol

IPv4 protokol mapujúci lokálnu next-hop IP adresu na MAC adresu. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Artifact

Jednoznačne identifikovateľný výstup build procesu určený na testovanie alebo distribúciu. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Artifact — CI/CD

Versionovaný a identifikovateľný výstup pipeline určený na ďalšie overenie, distribúciu alebo deployment. Na rozdiel od cache môže byť súčasťou correctness a release evidence. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Artifact digest

Content-derived immutable identifikátor artifactu, napríklad SHA-256 digest container image, používaný na presnú väzbu medzi buildom, evidence, promotion a deploymentom. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Artifact promotion

Presun už vytvoreného a overeného immutable artifactu medzi environmentmi alebo release stages bez jeho opätovného rebuildovania. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Artifact version

Logical identifier artifactu používaný na komunikáciu release identity alebo compatibility významu. Má byť mapovateľný na konkrétny immutable content digest. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Asymmetric routing

Stav, keď forward a return traffic rovnakého flow používajú rozdielne network paths. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Asyncio

Python framework pre cooperative asynchronous I/O založený na event loop-e, coroutines a tasks. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Atomic write

Zápis cez dočasný súbor, validáciu a atomický rename/replace tak, aby consumer nevidel čiastočný obsah. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md) a [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Attack surface

Súbor rozhraní, vstupov, identities a trust boundaries, cez ktoré môže aktér ovplyvniť systém. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Automated canary analysis

Automatizované vyhodnotenie canary verzie voči baseline podľa technických a business metrík, sample size, observation window a promotion/abort policy. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Automated promotion

Policy-driven rozhodnutie posunúť artifact alebo rollout do ďalšej fázy bez manuálneho approvalu na základe testov, provenance, health a risk signálov. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Automatic rollback

Automatizovaný návrat na predchádzajúcu kompatibilnú verziu po detekcii spoľahlivého failure signálu. Nie je bezpečný pri každej stateful alebo nevratnej zmene. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Automation

Prevod opakovateľného postupu na deterministický, auditovateľný a opakovane vykonateľný mechanizmus. Pozri [Automation Mindset](docs/00-foundations/automation-mindset.md).

## AVC — Access Vector Cache

SELinux decision a auditný kontext opisujúci povolenie alebo zamietnutie operácie medzi source a target security contexts. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Backfill

Riadené doplnenie alebo transformácia existujúcich dát, typicky v bounded batches s checkpointingom, rate limitom, validáciou a možnosťou pause/resume. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Backoff

Časová stratégia medzi opakovanými pokusmi, často exponenciálne rastúca a doplnená jitterom. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Backport

Prenesenie opravy alebo zmeny z novšej vývojovej línie do staršej podporovanej release branch, často pomocou cherry-picku a samostatnej validácie. Pozri [Cherry-pick a stash](docs/03-git-and-automation/cherry-pick-and-stash.md).

## Backpressure

Mechanizmus, ktorým pomalší consumer obmedzí alebo signalizuje producerovi, aby nevytváral neobmedzený buffer a rastúcu latency. Pozri [REST APIs a WebSockets](docs/02-networking-and-web/rest-apis-and-websockets.md).

## Bare repository

Git repository bez working tree, používaný typicky ako serverový alebo integračný endpoint. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Batch size

Množstvo zmien spracovaných alebo nasadených naraz. Menšie batches znižujú blast radius a skracujú feedback. Pozri [Three Ways of DevOps](docs/00-foundations/three-ways.md).

## BDD — Behavior-Driven Development

Collaboration a discovery prístup používajúci príklady správania a spoločný jazyk na spresnenie požiadaviek; Gherkin je iba jedna možná reprezentácia. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Behavioral equivalence — environment

Miera, do akej nižší environment zachováva produkčne relevantné protokoly, konfiguráciu, topology, limits a security behavior aj bez úplnej veľkostnej parity. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Blast radius

Maximálny rozsah používateľov, trafficu, dát, komponentov alebo failure domains, ktoré môže zmena, incident alebo experiment ovplyvniť. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Blob — Git object

Nemenný Git object obsahujúci bytes jedného súboru bez filename a path metadata. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Block device

Kernelové zariadenie poskytujúce blokovo adresovaný storage. Pozri [Storage, mounty a filesystems](docs/01-linux-and-systems/storage-mounts-and-filesystems.md).

## Blocking gate

Quality gate, ktorého neúspech zastaví merge, promotion alebo deployment. Má sa používať pre spoľahlivý signál spojený s neprijateľným rizikom. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Blue-green deployment

Deployment stratégia s dvoma oddelenými produkčne relevantnými targetmi, kde sa nová verzia pripraví v neaktívnej farbe a následne sa na ňu riadene presmeruje traffic. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Bounding set — capability bounding set

Horná hranica Linux capabilities, ktoré proces a jeho potomkovia môžu získať. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Branch coverage

Podiel výsledkov rozhodovacích vetiev vykonaných test suite. Poskytuje jemnejší signál než samotná line coverage. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Branch — Git branch

Pohyblivý ref pod `refs/heads/`, ktorý ukazuje na tip commit. Branch nie je samostatný kontajner súborov ani commitov. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Branch protection

Serverová policy obmedzujúca aktualizáciu dôležitej branch pomocou controls ako required reviews, CI checks, zákaz force pushu alebo merge queue. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## Broadcast domain

L2 oblasť, v ktorej sa šíri Ethernet broadcast. Typicky ju oddeľuje router alebo VLAN boundary. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Broken main

Stav, keď hlavná integračná branch nespĺňa povinné build alebo quality gates a nemá byť považovaná za dôveryhodný integračný základ. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Build

Proces transformujúci zdrojové vstupy na spustiteľný alebo distribuovateľný artifact. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Build metadata — SemVer

Informácie za znakom `+` v Semantic Versioning verzii, napríklad build number alebo commit SHA. Neovplyvňujú SemVer version precedence. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Build once

Princíp vytvoriť pre konkrétny source commit jeden immutable artifact a ten istý artifact následne testovať a promovať medzi prostrediami. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Build once, promote many

Delivery princíp, pri ktorom sa source zostaví raz do immutable artifactu a rovnaký digest sa overuje a promotionuje cez všetky environments. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Build Verification Test

Krátky smoke test nad novým buildom overujúci, či je artifact spustiteľný a vhodný na drahšie testovanie. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## Cache — CI/CD

Odstrániteľná optimalizácia pipeline na znovupoužitie dependencies alebo intermediate build dát. Pipeline musí zostať korektná aj pri cache miss alebo eviction. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Cache-Control

HTTP response/request header definujúci freshness, revalidation, storage a shared/private cache policy. Pozri [HTTP](docs/02-networking-and-web/http.md).

## Cache key

Identifikátor cache odvodený zo všetkých významných vstupov, napríklad OS, architecture, toolchain version, lockfile hash a build configuration. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Cache poisoning

Stav, keď nedôveryhodný alebo chybný pipeline uloží cache, ktorú neskôr použije dôveryhodnejší workflow, čím môže ovplyvniť build alebo spustiť škodlivý obsah. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Calendar versioning

Versioning schéma odvodená primárne z kalendárneho dátumu alebo release cadence, napríklad `2026.07.21`. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## CALMS

DevOps rámec Culture, Automation, Lean, Measurement a Sharing. Pozri [CALMS framework](docs/00-foundations/calms.md).

## Canary analysis

Automatizované alebo riadené porovnanie novej verzie s baseline či kontrolnou skupinou podľa technických a business metrík počas obmedzeného rollout-u. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Canary cohort

Stabilná skupina requestov, používateľov, tenantov alebo instances vystavená novej verzii pred širšou promotion. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Canary deployment

Deployment stratégia postupne zvyšujúca produkčnú exposure novej verzie pri súbežnom porovnávaní so stable baseline a explicitných promotion/abort kritériách. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Canary release

Postupné sprístupnenie novej verzie malej časti trafficu alebo používateľov s porovnávaním technických a business signálov pred širšou promotion. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Capability — Linux capability

Samostatná časť tradičných root oprávnení, napríklad `CAP_NET_BIND_SERVICE`. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Capacity test

Performance test hľadajúci maximálny udržateľný workload pri definovaných SLO a bezpečnostnej rezerve. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Capturing group — regex

Časť regular expression uzavretá v zátvorkách, ktorá zachytáva matched substring pre ďalšie spracovanie. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Catastrophic backtracking

Patologické správanie backtracking regex engine-u, pri ktorom ambiguous nested pattern spôsobí extrémny čas spracovania non-matching vstupu. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Certificate

X.509 objekt viažuci public key na identity claims, validity interval, usage a issuer signature. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Certificate chain

Postupnosť leaf a intermediate certificates, ktorú klient overuje smerom k dôveryhodnému root CA v trust store. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## cgroup — Control group

Kernel mechanizmus na hierarchické zoskupovanie procesov a riadenie ich CPU, memory, I/O a process-count resources. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## cgroup v2

Unified cgroup hierarchy s konzistentnejším modelom controllerov a delegácie než cgroup v1. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## Change fail rate

Podiel deploymentov, ktoré spôsobia degradáciu služby a vyžadujú nápravu. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Change lead time

Čas od vzniku sledovanej zmeny po jej úspešný deployment do produkcie. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Changelog

Dlhodobý chronologický záznam významných zmien produktu alebo komponentu naprieč releases. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Chaos engineering

Disciplína formulovania a vykonávania kontrolovaných experimentov, ktoré overujú schopnosť systému zachovať prijateľné správanie pri poruchách a neistote. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Chaos testing

Praktická forma riadeného fault experimentu overujúca konkrétnu steady-state hypotézu v definovanom scope s bezpečnostnými kontrolami. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Cherry-pick

Operácia, ktorá aplikuje zmenu vybraného commitu na aktuálny tip a vytvorí nový commit s novým parentom a object ID. Pozri [Cherry-pick a stash](docs/03-git-and-automation/cherry-pick-and-stash.md).

## Child pipeline

Samostatný pipeline run vytvorený parent pipelineom pre component, matrix časť alebo dynamicky generovaný workflow, s explicitnými input/output a failure-propagation pravidlami. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## CIDR — Classless Inter-Domain Routing

Zápis IP prefixu pomocou adresy a počtu network bitov, napríklad `192.0.2.0/24`. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## `CLOSE-WAIT`

TCP state, v ktorom remote peer poslal FIN, ale lokálna aplikácia ešte nezavrela socket. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Closed workload model

Model, v ktorom fixný počet virtual users generuje ďalšiu operáciu až po dokončení predchádzajúcej. Spomalenie systému preto môže znížiť generovaný arrival rate. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Cmdlet

PowerShell command implementovaný podľa jednotného Verb-Noun, parameter binding, object pipeline a error-stream modelu. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Code coverage

Metrika určujúca, ktorá časť kódu bola vykonaná počas testov. Nedokazuje správnosť assertions ani business behavior. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Code freeze

Časovo alebo rozsahovo obmedzená policy, ktorá pred release povoľuje iba vybrané zmeny. Nemá nahrádzať automatizované kontroly, malé batches a recovery schopnosť. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Cohort assignment

Deterministické priradenie subjektu do rollout alebo experiment skupiny pomocou stabilnej identity a versionovaného pravidla. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md) a [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Collision domain

Oblasť zdieľaného Ethernet média, v ktorej môžu transmissions kolidovať. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Color-specific telemetry

Metrics, logs a traces označené blue/green environmentom a artifact verziou tak, aby bolo možné analyzovať cutover a porovnať správanie oboch farieb. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Command injection

Zraniteľnosť, pri ktorej neoverený vstup zmení syntax alebo spustí dodatočný príkaz. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md) a [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Commit object

Git object obsahujúci root tree snapshotu, parent commits, author/committer metadata a commit message. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Compatibility matrix — deployment

Explicitná tabuľka určujúca, ktoré application, client, event a schema verzie môžu bezpečne koexistovať počas rollout-u a rollback window. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Complain mode

AppArmor režim, v ktorom sa porušenia profilu logujú, ale neblokujú. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Component test

Test celého deployovateľného komponentu cez jeho verejné rozhranie, pričom externé dependencies môžu byť nahradené controlled doubles. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Condition-based wait

Čakanie na explicitnú podmienku s deadline namiesto pevného sleepu. Znižuje timing flakiness a zrýchľuje test pri rýchlom výsledku. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Condition coverage

Coverage metrika sledujúca, či jednotlivé boolean podmienky nadobudli relevantné true a false výsledky. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Congestion control

Transportný mechanizmus upravujúci množstvo dát in flight podľa odhadovanej kapacity a congestion signálov network pathu. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Connection draining

Postup, pri ktorom sa backendu prestane posielať nový traffic, ale existujúce requests alebo connections dostanú čas na dokončenie. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Conntrack

State table sledujúca network flows pre stateful firewall a NAT rozhodnutia. Pozri [NAT](docs/02-networking-and-web/nat.md) a [Firewally](docs/02-networking-and-web/firewalls.md).

## Consistent hashing

Hashing model minimalizujúci množstvo remapovaných keys pri pridaní alebo odstránení backendu. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Consumer-driven contract

Kontrakt definovaný consumerom podľa interactions, ktoré reálne potrebuje, a overovaný providerom v jeho pipeline. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## Content-addressable storage

Storage model, v ktorom je identita objektu odvodená z jeho typu a obsahu. Git používa tento model pre blobs, trees, commits a tags. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Content digest

Content-derived immutable identifikátor konkrétnych bytes artifactu, typicky kryptografický hash. Na rozdiel od logical version alebo mutable tagu presne určuje nasadený obsah. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Content negotiation

HTTP mechanizmus, ktorým klient deklaruje preferované representations a server vyberie formát, jazyk alebo encoding. Pozri [HTTP](docs/02-networking-and-web/http.md).

## Context manager — Python

Objekt alebo generator riadiaci vstup a výstup z lifecycle scope, napríklad otvorenie a bezpečné zatvorenie súboru, locku alebo session. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Context switch

Prechod CPU z vykonávania jedného threadu na iný. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Continuous Delivery

Schopnosť udržiavať systém a jeho artifacty v stave pripravenom na bezpečný, opakovateľný a auditovateľný produkčný deployment na požiadanie. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Continuous Deployment

Delivery model, v ktorom každá zmena spĺňajúca automatizované quality a policy podmienky pokračuje bez manuálneho release approvalu do produkcie. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Continuous Integration

Pracovný a technický model častej integrácie malých zmien do spoločnej hlavnej línie s automatizovaným buildom, kontrolami a rýchlym feedbackom. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Contract drift

Rozdiel medzi správaním test double alebo dokumentovaného kontraktu a skutočnou dependency. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Contract test

Test kompatibility producer/consumer rozhrania bez potreby spustiť celý distribuovaný systém. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## Control group — experiment

Skupina používateľov, requestov alebo systémových instances, ktorá nedostane experimentálnu zmenu a poskytuje súbežnú baseline na porovnanie. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Control plane

Časť systému vytvárajúca stav, podľa ktorého data plane rozhoduje. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## Control variant

Referenčný variant experimentu reprezentujúci existujúce alebo baseline správanie, voči ktorému sa hodnotí treatment. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Controller

Komponent porovnávajúci desired state s aktuálnym stavom a vykonávajúci korekčné akcie. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## Cookie

HTTP state token, ktorý server nastaví cez `Set-Cookie` a klient následne posiela podľa domain, path, security a SameSite scope. Pozri [HTTP](docs/02-networking-and-web/http.md).

## Coordinated omission

Skreslenie performance merania, pri ktorom load generator počas spomalenia neposiela requests, ktoré by v reálnom arrival-rate modeli prišli. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## CORS — Cross-Origin Resource Sharing

Browser-enforced HTTP policy určujúca, ktoré origins môžu čítať responses alebo odosielať vybrané cross-origin requests. Pozri [HTTP](docs/02-networking-and-web/http.md).

## CPU quota

Cgroup limit maximálneho CPU času v danom period. Po vyčerpaní môže byť workload throttled. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## Critical path — pipeline

Najdlhšia dependency cesta od triggeru po požadovaný výsledok pipeline. Určuje minimálnu možnú duration pri danom grafe bez ohľadu na súčet všetkých job durations. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Cron

Časový scheduler spúšťajúci príkazy podľa crontab pravidiel. Pozri [Cron a systemd timers](docs/01-linux-and-systems/cron-and-systemd-timers.md).

## CSR — Certificate Signing Request

Podpísaná žiadosť obsahujúca public key a požadované certificate identity attributes pre CA. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Cutover window

Časový interval, v ktorom sa traffic alebo ownership práce presúva zo starej deployment farby na novú a intenzívne sa sledujú promotion a abort signály. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## DAC — Discretionary Access Control

Model oprávnení založený najmä na UID/GID, mode bits a ACL. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Daemon

Dlhšie bežiaci proces poskytujúci systémovú alebo aplikačnú službu bez priamej interaktívnej session. Pozri [systemd, services a daemons](docs/01-linux-and-systems/systemd-services-daemons.md).

## DAG — CI/CD

Directed Acyclic Graph vyjadrujúci explicitné dependencies medzi jobs. Umožňuje spustiť job hneď po dokončení jeho skutočných upstream dependencies. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Dark launch

Nasadenie capability do produkčného prostredia bez jej priameho sprístupnenia používateľom, používané na overenie integrácie, capacity alebo prevádzkového správania. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## DAST — Dynamic Application Security Testing

Security testovanie bežiacej aplikácie zvonka cez jej runtime rozhrania. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Data plane

Časť systému spracúvajúca konkrétne frames alebo packets podľa existujúceho forwarding a policy stavu. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## Dataclass — Python

Deklaratívny Python model generujúci metódy pre dátovo orientovanú class, napríklad constructor, equality a representation. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Declarative configuration

Konfigurácia opisujúca požadovaný výsledný stav, nie sekvenciu krokov. Pozri [Declarative vs. Imperative Approach](docs/00-foundations/declarative-vs-imperative.md).

## Default deny

Security policy, pri ktorej sa povoľuje iba explicitne definovaný traffic alebo operácie a všetko ostatné sa zamietne. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Default route

Najmenej špecifická route `0.0.0.0/0` alebo `::/0`, použitá ak neexistuje presnejšia route. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Dependency lock

Presne vyriešený zoznam versions priamych a transitívnych dependencies určený na reprodukovateľnú inštaláciu. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Deployable state

Stav, v ktorom existuje dôveryhodný immutable artifact, potrebné dôkazy, kompatibilná konfigurácia, deployment automation, observability a recovery plán umožňujúci bezpečný deployment. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Deployment

Technická operácia umiestnenia verzie aplikácie alebo konfigurácie do cieľového prostredia. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Deployment downtime

Čas, počas ktorého deployment spôsobí úplnú alebo neprijateľnú nedostupnosť služby. Pri recreate zahŕňa shutdown, deployment, startup, migrations, readiness a routing. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## Deployment frequency

Ako často služba úspešne nasadzuje zmeny do produkcie. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Deployment lock

Mechanizmus serializujúci alebo koordinujúci mutations jedného environmentu, aby sa paralelné deploymenty navzájom neprepísali alebo nevytvorili nekonzistentný stav. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Deployment marker

Časovo a verziou označená udalosť v observability systéme umožňujúca korelovať zmenu error rate, latency alebo business metrík s konkrétnym deploymentom. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Deployment pipeline

Automatizovaný tok od source zmeny cez build, testy, artifact, environment deployment a validáciu až po produkčne pripraveného alebo nasadeného kandidáta. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Deployment record

Auditovateľný záznam spájajúci environment, artifact digest, configuration revision, pipeline run, identity, čas a výsledok konkrétneho deploymentu. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Deployment rework rate

Podiel deploymentov, ktoré sú neplánovanou opravou predchádzajúceho deploymentu. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Deployment ring

Stabilná rollout skupina používateľov, tenantov, zariadení alebo regiónov s definovaným risk profilom, membershipom a promotion contractom. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Deserialized object — PowerShell

Prenesená reprezentácia vzdialeného PowerShell objektu, ktorá typicky zachováva properties, ale nie live methods a pôvodné runtime správanie. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Desired state

Požadovaný stav systému deklarovaný používateľom alebo automatizačným nástrojom. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## Detached HEAD

Stav, v ktorom `HEAD` ukazuje priamo na commit namiesto symbolického odkazu na branch. Nové commits treba zachytiť branch refom, inak môžu zostať unreachable. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Deterministic serialization

Serializácia, pri ktorej rovnaký logický vstup vytvára stabilný byte alebo textový výstup podľa definovaných pravidiel. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## DevOps

Kultúrne princípy, organizačné praktiky a technické mechanizmy na rýchle a bezpečné dodávanie zmien. Pozri [DevOps](docs/00-foundations/devops.md).

## DHCP — Dynamic Host Configuration Protocol

Protokol na prideľovanie IP configuration, lease a ďalších network parameters klientom. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## DHCP lease

Časovo obmedzené oprávnenie klienta používať pridelenú adresu a konfiguráciu. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## DHCP relay

Komponent forwardujúci DHCP komunikáciu medzi klientskym broadcast domainom a serverom v inom subnete. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## DHCP reservation

Centrálne DHCP-managed mapovanie identity klienta na stabilnú IP adresu. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## DHCP snooping

Switchová ochrana povoľujúca DHCP server responses iba na trusted portoch. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## Diff coverage

Coverage vypočítaná iba pre nový alebo zmenený kód voči zvolenému merge base. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## DNAT — Destination NAT

Preklad destination adresy alebo portu, používaný napríklad pri publikovaní internej služby. Pozri [NAT](docs/02-networking-and-web/nat.md).

## DNS — Domain Name System

Distribuovaný hierarchický systém mapujúci mená na resource records. Pozri [DNS](docs/02-networking-and-web/dns.md).

## DNS resolver

Komponent vykonávajúci alebo sprostredkujúci DNS resolution. Pozri [DNS](docs/02-networking-and-web/dns.md).

## DNS TTL

Čas, počas ktorého môže resolver cacheovať DNS resource record. Pozri [DNS](docs/02-networking-and-web/dns.md).

## DNSSEC

Rozšírenie DNS poskytujúce kryptografické overenie autenticity a integrity DNS dát cez chain of trust. Pozri [DNS](docs/02-networking-and-web/dns.md).

## Document stream — YAML

YAML stream obsahujúci jeden alebo viac documents oddelených markerom `---`. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## DORA metrics

Metriky software delivery performance sledujúce throughput a instability delivery systému. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Drift

Rozdiel medzi deklarovaným a skutočným stavom systému. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## Drop — firewall action

Tiché zahodenie packetu bez explicitnej odpovede klientovi. Typickým symptómom je timeout. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Dual stack

Prevádzka IPv4 aj IPv6 na rovnakom hoste alebo službe. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Dual write

Dočasný migration model, v ktorom application zapisuje rovnakú logickú zmenu do starej aj novej reprezentácie alebo store. Vyžaduje idempotency, authoritative source a reconciliation. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Dummy — test double

Hodnota potrebná iba na vyplnenie parametra bez aktívneho použitia v testovanom scenári. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Early feedback

Informácia o kvalite alebo riziku získaná v najskoršom bode, v ktorom má kontrola dostatočnú fidelity a diagnostickú hodnotu. Pozri [Shift-left](docs/04-testing-and-quality/shift-left.md).

## eBPF — extended Berkeley Packet Filter

Kernel technológia na spúšťanie overeného bytecode na definovaných hooks, používaná aj na observability a profiling. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Effective capability set

Množina Linux capabilities aktuálne používaná kernelom pri privilege checks procesu. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Encapsulation

Proces, pri ktorom každá sieťová vrstva pridá svoje metadata okolo payloadu vyššej vrstvy. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## End-to-end test

Test workflow prechádzajúci cez viac produkčne relevantných vrstiev alebo procesných hraníc od vstupu po observable výsledok. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Enforcing mode

Režim SELinux alebo AppArmor policy, v ktorom sa zakázané operácie blokujú. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Environment drift

Rozdiel medzi deklarovaným desired state environmentu a jeho skutočným runtime stavom, napríklad po manuálnej config alebo infrastructure zmene. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Environment parity — deployment

Miera, do akej blue a green alebo iné deployment targety zachovávajú rovnaké produkčne relevantné konfigurácie, topológiu, permissions, limits a dependencies. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Environment promotion

Riadený posun rovnakého artifactu do ďalšieho prostredia na základe dôkazov, policy a compatibility podmienok. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Environment variable

Pomenovaná hodnota odovzdaná procesu v jeho environment bloku. Pozri [Environment variables](docs/01-linux-and-systems/environment-variables.md).

## Ephemeral port

Dočasný source port typicky pridelený klientskemu socketu. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md).

## Ephemeral port exhaustion

Stav, keď host alebo NAT nemá voľný transportný port pre nový flow. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md) a [NAT](docs/02-networking-and-web/nat.md).

## ETag

HTTP validator reprezentácie používaný na cache revalidation a optimistic concurrency cez conditional requests. Pozri [HTTP](docs/02-networking-and-web/http.md).

## Ethernet frame

Link-layer jednotka obsahujúca source a destination MAC, EtherType, payload a kontrolné metadata. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Evidence freshness

Pravidlá určujúce, či test result, scan, review alebo approval stále patrí k aktuálnemu commitu, artifactu, policy a environment state. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Exception chaining — Python

Zachovanie pôvodnej exception ako príčiny novej kontextovej exception cez `raise ... from ...`. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Executable specification

Príklad alebo pravidlo zapísané vo forme, ktorú možno automaticky spustiť ako dôkaz behavior. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Executor — CI/CD

Mechanizmus použitý runnerom na vykonanie jobu, napríklad host shell, container, virtual machine alebo Kubernetes pod. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Exit status

Číselný výsledok ukončeného procesu alebo shell príkazu. Pozri [Shell, Bash, pipes, redirection a exit codes](docs/01-linux-and-systems/shell-bash-pipes-redirection-exit-codes.md).

## Expand-contract

Viacfázový model databázovej alebo contract zmeny: najprv sa pridá kompatibilná nová štruktúra, migrujú readers/writers a dáta, a až po rollback window sa odstráni stará štruktúra. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Experiment contract

Explicitný popis hypotézy, steady state, faultu, scope, blast radiusu, trvania, abort criteria, recovery, ownershipu a dôkazov chaos experimentu. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Experiment unit

Entita randomizovaná do variantu experimentu, napríklad používateľ, tenant, device, session alebo región. Musí zodpovedať hranici možného treatment efektu. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Exposure event

Telemetry udalosť dokazujúca, že subjekt reálne dostal konkrétny experiment alebo feature variant; assignment bez exposure nemusí znamenať ovplyvnenie. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Fail closed — gate policy

Policy, pri ktorej chýbajúca alebo nedostupná evidence spôsobí blokovanie operácie. Používa sa pri kontrolách, ktorých obídenie predstavuje neprijateľné riziko. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Fail open — gate policy

Policy, pri ktorej nedostupná kontrola neblokuje operáciu, ale vytvorí viditeľný degraded signal. Je vhodná iba tam, kde riziko nedostupnosti gate prevyšuje riziko pokračovania. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Failed deployment recovery time

Čas potrebný na obnovenie služby po zlyhaní spôsobenom deploymentom. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Failure artifact

Diagnostický dôkaz zachovaný pri zlyhaní testu, napríklad screenshot, trace, log, packet capture, request ID alebo environment metadata. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Fake — test double

Zjednodušená, ale funkčná implementácia dependency používaná v teste, napríklad in-memory repository alebo fake clock. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## False negative — testing

Výsledok, pri ktorom test prejde, hoci systém obsahuje chybu relevantnú pre testovaný risk. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## False positive — testing

Výsledok, pri ktorom test hlási chybu, hoci testované správanie je správne. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## Fan-in — pipeline

Bod pipeline grafu, v ktorom downstream job čaká na výsledky viacerých upstream jobs alebo shards. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Fan-out — pipeline

Rozdelenie jedného vstupu, artifactu alebo test suite do viacerých paralelných jobs. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Fast-forward

Aktualizácia refu, pri ktorej je starý tip ancestor nového tipu, takže sa ref iba posunie bez odstránenia existujúcej ancestry. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Fault injection

Kontrolované zavedenie konkrétneho failure condition, napríklad latency, process termination, resource pressure alebo dependency erroru. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Feature branch

Dočasná branch určená na izolovaný vývoj jednej zmeny. Pri trunk-based modeli má byť krátkodobá a často integrovaná. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## Feature flag

Konfiguračný mechanizmus oddeľujúci deployment kódu od sprístupnenia funkcionality konkrétnym používateľom, cohortám alebo percentu trafficu. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Feedback loop

Cesta od vykonanej zmeny k informácii o jej výsledku. Pozri [Feedback Loops](docs/00-foundations/feedback-loops.md).

## File capability

Capability metadata uložené na executable súbore v extended attribute. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## File descriptor

Malé celé číslo v procese odkazujúce na kernelom spravovaný otvorený objekt. Pozri [Shell, Bash, pipes, redirection a exit codes](docs/01-linux-and-systems/shell-bash-pipes-redirection-exit-codes.md).

## Filesystem

Štruktúra mapujúca pathname na metadata a dátové bloky. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## First-attempt pass rate

Podiel testov, ktoré prejdú na prvý pokus bez retry. Je citlivejším signálom flakiness než finálna pass rate po opakovaniach. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Flag debt

Kumulovaná komplexita starých feature flags, paralelných code paths, kombinácií stavov, testov a prevádzkových rozhodnutí po prekročení plánovaného lifecycle. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Flag evaluation

Runtime rozhodnutie o variante alebo hodnote feature flagu na základe flag verzie, identity, environmentu a targeting pravidiel. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Flaky test

Test, ktorý pri rovnakom kóde a deklarovaných vstupoch nedeterministicky prechádza alebo zlyháva. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Flow control

TCP mechanizmus chrániaci receiver pred odosielaním väčšieho množstva dát, než dokáže prijať. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Force-with-lease

Bezpečnejšia forma force pushu, ktorá aktualizuje remote ref iba vtedy, keď stále zodpovedá očakávanej hodnote. Stále ide o history rewrite. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Forward-fix migration

Nová databázová migration opravujúca chybný alebo neúplný aktuálny stav bez pokusu mechanicky vrátiť predchádzajúcu schema. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Forward proxy

Proxy zastupujúci klienta pri komunikácii s externými servermi. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## Forward secrecy

Vlastnosť ephemeral key agreementu, pri ktorej neskorší únik dlhodobého private key automaticky neodhalí staré TLS sessions. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Game day

Plánované tímové resilience cvičenie kombinujúce technické faults, observability, incident response, komunikáciu a následné learning actions. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Git index

Binárna dátová štruktúra predstavujúca pripravovaný snapshot nasledujúceho commitu; obsahuje paths, modes, object IDs a pri konfliktoch viac stages. Pozri [Working tree, staging area a repository](docs/03-git-and-automation/working-tree-staging-repository.md).

## Git ref

Pomenovaný ukazovateľ na Git object ID, typicky commit. Príkladmi sú branches, remote-tracking refs a tags. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Globbing

Shell expansion, ktorá nahrádza wildcard pattern paths zodpovedajúcimi filesystem entries. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Golden path

Podporovaný a automatizovaný spôsob vývoja a delivery poskytujúci bezpečné defaults, reusable tooling, observability a policy guardrails. Pozri [Shift-left](docs/04-testing-and-quality/shift-left.md).

## Graceful degradation

Schopnosť systému pri nedostupnosti časti dependencies zachovať obmedzenú, ale stále užitočnú a bezpečnú funkcionalitu namiesto úplného zlyhania. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Graceful shutdown

Riadené ukončenie, pri ktorom proces prestane prijímať novú prácu, bezpečne spracuje alebo preruší rozpracovaný stav, uvoľní resources a vráti správny status. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Gratuitous ARP

ARP announcement používaný napríklad na aktualizáciu neighbor caches po presune virtual IP. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Greedy quantifier — regex

Regex quantifier, ktorý najprv spotrebuje najväčší možný rozsah a podľa potreby backtrackuje. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Guardrail metric

Metrika chrániaca experiment alebo rollout pred neprijateľným vedľajším dopadom, aj keď primary metric vyzerá pozitívne. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Hard link

Ďalší directory entry odkazujúci na ten istý inode. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## HEAD — Git

Špeciálny ref reprezentujúci aktuálnu checkout pozíciu. Typicky symbolicky ukazuje na current branch, ale môže ukazovať priamo na commit. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Health check

Aktívny alebo pasívny test určujúci, či backend môže prijímať nový traffic. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Hermetic test

Test, ktorý kontroluje všetky významné vstupy a nespolieha sa na nepredvídateľný externý stav. Môže používať disposable reálne dependencies. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## History rewrite

Operácia vytvárajúca nové commit objects a meniaca branch-visible ancestry, napríklad rebase, amend alebo reset publikovanej branch. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## Hop limit

IPv6 field znižovaný na každom router hop-e; IPv4 ekvivalentom je TTL. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Host key — SSH host key

Kryptografický kľúč, ktorým SSH server preukazuje svoju identitu klientovi. Pozri [SSH](docs/01-linux-and-systems/ssh.md).

## HSTS — HTTP Strict Transport Security

Browser policy oznamujúca, že doména sa má používať iba cez HTTPS počas definovaného času. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## HTTP

Aplikačný request-response protokol s methods, status codes, headers a representation semantics. Pozri [HTTP](docs/02-networking-and-web/http.md).

## HTTP/2

HTTP verzia používajúca binary framing a multiplexované streams nad jedným TCP connection. Pozri [HTTP](docs/02-networking-and-web/http.md).

## HTTP/3

HTTP verzia používajúca QUIC nad UDP s nezávislejším stream loss recovery modelom. Pozri [HTTP](docs/02-networking-and-web/http.md).

## Hypercare

Dočasne zvýšená prevádzková a support pozornosť po významnom release, vrátane posilneného monitoringu, owner dostupnosti a rýchleho rozhodovacieho pathu. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## IaC scanning

Statická alebo plan-level kontrola Infrastructure as Code proti syntax, schema, security a policy pravidlám. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## IAST — Interactive Application Security Testing

Security analýza využívajúca runtime informácie z instrumentovanej aplikácie počas testov. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Idempotencia

Vlastnosť operácie, pri ktorej opakovanie s rovnakým vstupom vedie k rovnakému výslednému stavu. Pozri [Idempotency](docs/00-foundations/idempotency.md).

## Idempotency key

Client-generated identifikátor umožňujúci serveru rozpoznať opakovaný ne-idempotentný request a vrátiť konzistentný výsledok. Pozri [REST APIs a WebSockets](docs/02-networking-and-web/rest-apis-and-websockets.md).

## Immutable infrastructure

Model, v ktorom sa existujúce inštancie zásadne neupravujú, ale nahrádzajú novými. Pozri [Immutable vs. Mutable Infrastructure](docs/00-foundations/immutable-vs-mutable-infrastructure.md).

## Immutable tag

Registry alebo repository tag, ktorého mapping na artifact content sa po publikovaní nesmie zmeniť. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Imperative approach

Prístup opisujúci konkrétnu sekvenciu krokov. Pozri [Declarative vs. Imperative Approach](docs/00-foundations/declarative-vs-imperative.md).

## Implicit typing — YAML

Automatická interpretácia plain scalaru ako boolean, number, date alebo null podľa YAML schema a parser implementácie. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Index stages

Viac verzií jednej path uložených v Git indexe počas konfliktu: stage 1 je merge base, stage 2 ours a stage 3 theirs. Pozri [Konflikty](docs/03-git-and-automation/merge-conflicts.md).

## Inode

Filesystem objekt obsahujúci metadata a odkazy na dátové bloky. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## Integration test

Test reálnej spolupráce komponentov alebo systému s technickou dependency, napríklad databázou, brokerom, filesystemom alebo cloud API. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Interaction-based testing

Testovanie, ktoré overuje komunikáciu a side effects medzi objektmi alebo komponentmi, napríklad volanie gateway s konkrétnymi argumentmi. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## IP packet

Network-layer jednotka obsahujúca source a destination IP adresu a payload vyššej vrstvy. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## IPv4 private ranges

Adresy `10.0.0.0/8`, `172.16.0.0/12` a `192.168.0.0/16`, ktoré nie sú globálne routované vo verejnom Internete. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## IPv6 link-local address

IPv6 adresa z `fe80::/10` platná v lokálnom linkovom scope. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Jitter

Náhodná odchýlka pridaná k retry delay, ktorá znižuje synchronizované opakovanie veľkého množstva klientov. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Job — CI/CD

Najmenšia samostatne plánovaná execution unit pipeline s vlastným runtime, inputs, permissions, commands, timeoutom, resultom a outputs. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## journald

Systémová logging služba systemd sprístupnená cez `journalctl`. Pozri [journald a logging](docs/01-linux-and-systems/journald-and-logging.md).

## JSON Schema

Deklaratívny schema jazyk na validáciu štruktúry, typov a vybraných constraints JSON dát. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Kernel space

Privilegovaná časť systému, v ktorej kernel spravuje procesy, memory, devices, filesystems a networking. Pozri [Kernel a user space](docs/01-linux-and-systems/kernel-and-user-space.md).

## Kill switch

Technický mechanizmus umožňujúci rýchlo zastaviť fault injection, experiment alebo feature exposure pri prekročení bezpečných hraníc. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## L4 load balancing

Rozdelenie transportných flows podľa IP, portu, protokolu a connection state bez interpretácie aplikačného obsahu. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## L7 load balancing

Rozdelenie requestov podľa aplikačných údajov, napríklad HTTP hostu, pathu alebo headerov. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Last known good

Presne identifikovaný artifact, configuration a compatibility stav s overenou produkčnou evidence, ktorý možno použiť ako recovery target. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Latency

Čas potrebný na dokončenie operácie alebo requestu. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Line coverage

Podiel vykonaných source riadkov počas testov. Vysoká hodnota sama osebe nedokazuje správnosť testov. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Listening socket

Socket čakajúci na nové TCP spojenia. Po `accept()` vzniká samostatný connected socket. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md).

## Little's Law

Queueing vzťah `concurrency = throughput × time in system`. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Load average

Priemerný počet runnable tasks a určitých tasks v uninterruptible sleep. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Load shedding

Riadené odmietanie alebo obmedzenie časti práce pri preťažení, aby systém chránil kritické workflow a zabránil úplnému kolapsu. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Load test

Performance test overujúci očakávaný workload a splnenie latency, throughput, error-rate a resource kritérií. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Logical version

Ľudsky alebo procesne významná verzia, napríklad `2.8.1`, ktorá komunikuje release alebo compatibility význam, ale sama nemusí identifikovať konkrétne bytes bez väzby na digest. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Longest-prefix match

Routing pravidlo, podľa ktorého vyhráva zhodná route s najväčším počtom prefix bitov. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Lookaround — regex

Zero-width regex assertion overujúca text pred alebo za aktuálnou pozíciou bez jeho zahrnutia do matchu. Nie je podporovaná vo všetkých engines. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## MAC address

Link-layer identifikátor interface používaný na Ethernet forwarding v lokálnom broadcast domain. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## MAC — Mandatory Access Control

Bezpečnostná politika vynútená systémom nad rámec rozhodnutí ownera objektu. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Mainline

Spoločná integračná línia, typicky `main`, reprezentujúca najaktuálnejší dôveryhodný integrovaný stav projektu. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Maintenance mode

Kontrolovaný runtime režim používaný počas deploymentu na blokovanie alebo obmedzenie operácií, prípadne na poskytovanie informačnej response používateľom. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## Maintenance window

Vopred definovaný časový interval, počas ktorého je povolená plánovaná údržba alebo akceptovaný znížený service level. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## MAJOR version

Prvá časť SemVer verzie, ktorá sa zvyšuje pri nekompatibilnej zmene deklarovaného public API alebo compatibility contractu. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Matrix pipeline

Pipeline model generujúci viac jobs z kombinácie dimensions ako OS, architecture, runtime version alebo deployment target. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Maximum surge

Limit dočasnej capacity nad desired replica count, ktorú môže rolling update vytvoriť na zachovanie dostupnosti a zrýchlenie rollout-u. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Maximum unavailable

Limit počtu alebo percenta desired instances, ktoré môžu byť počas rolling update nedostupné. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## `memory.high`

Cgroup v2 memory hranica vyvolávajúca reclaim pressure a throttling. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## `memory.max`

Cgroup v2 hard memory limit, ktorého prekročenie môže viesť ku cgroup-local OOM. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## Merge base

Najlepší spoločný ancestor dvoch commitov používaný ako base pri three-way merge a pri výpočte divergence. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## Merge commit

Commit s dvoma alebo viacerými parents, ktorý explicitne zaznamenáva integráciu rozdielnych ancestry vetiev. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## Merge queue

Mechanizmus, ktorý testuje a integruje pull requests v plánovanom poradí proti aktuálnemu alebo predpokladanému stavu main branch. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## Minimum detectable effect

Najmenšia zmena outcome metriky, ktorú má experiment pri zvolenej sample size a power spoľahlivo detegovať. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## MINOR version

Druhá časť SemVer verzie, ktorá sa zvyšuje pri backward-compatible pridaní capability do deklarovaného public API. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Mixed-version deployment

Obdobie rollout-u, počas ktorého stará a nová application verzia súčasne obsluhujú traffic alebo pracujú nad spoločným stavom. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Mock — test double

Test double s explicitnými očakávaniami na interakcie. Je vhodný, keď komunikácia sama tvorí relevantný kontrakt. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Monorepo

Repository obsahujúci viac služieb, knižníc alebo projektov so spoločným object graphom a možnosťou atomických cross-project zmien. Pozri [Monorepo vs. multirepo](docs/03-git-and-automation/monorepo-vs-multirepo.md).

## Mount

Pripojenie filesystemu alebo iného mountable objektu do spoločného filesystem stromu. Pozri [Storage, mounty a filesystems](docs/01-linux-and-systems/storage-mounts-and-filesystems.md).

## Mount namespace

Namespace poskytujúci samostatný pohľad na mount table a propagation. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## MSS — Maximum Segment Size

Maximálny TCP payload segmentu deklarovaný endpointom, typicky odvodený od MTU mínus IP a TCP headers. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## mTLS — Mutual TLS

TLS model autentifikujúci server aj klienta pomocou certificates. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## MTU — Maximum Transmission Unit

Maximálna veľkosť L3 packetu preneseného interfaceom bez fragmentácie. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Multirepo

Model, v ktorom sú služby alebo projekty rozdelené medzi viac repositories a integrujú sa cez versioned artifacts a explicitné contracts. Pozri [Monorepo vs. multirepo](docs/03-git-and-automation/monorepo-vs-multirepo.md).

## Mutable infrastructure

Model, v ktorom sa existujúce stroje priebežne menia na mieste. Pozri [Immutable vs. Mutable Infrastructure](docs/00-foundations/immutable-vs-mutable-infrastructure.md).

## Mutable tag

Registry alebo repository tag, ktorého mapping možno prepísať na iný artifact content, napríklad `latest`. Nie je spoľahlivou deployment identity bez zachovaného digestu. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Mutation score

Podiel zámerných code mutations, ktoré test suite odhalí zlyhaním. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Mutation testing

Technika zámerne meniaca produkčný kód a overujúca, či test suite tieto zmeny zachytí. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Namespace — Linux namespace

Kernel objekt poskytujúci procesu izolovaný pohľad na vybranú kategóriu systémového stavu. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## NAT — Network Address Translation

Mechanizmus meniaci source alebo destination IP adresy a často ports pri prechode packetu. Pozri [NAT](docs/02-networking-and-web/nat.md).

## NAT64/DNS64

Prechodový model, v ktorom DNS64 syntetizuje IPv6 odpoveď a NAT64 prekladá traffic IPv6-only klienta na IPv4 server. Pozri [NAT](docs/02-networking-and-web/nat.md).

## NDP — Neighbor Discovery Protocol

IPv6 mechanizmus pre neighbor resolution, router discovery a prefix discovery. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Negative DNS caching

Cacheovanie negatívnej DNS odpovede, napríklad `NXDOMAIN`. Pozri [DNS](docs/02-networking-and-web/dns.md).

## Network ACL

Network policy aplikovaná typicky na subnet alebo segment boundary; v cloud prostredí býva často stateless. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Network namespace

Namespace s vlastnými interfaces, addresses, routes, sockets a firewall state. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## `no_new_privs`

Kernel flag zabraňujúci zvýšeniu privilege cez `execve()`. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Non-terminating error — PowerShell

PowerShell error record, pri ktorom command môže pokračovať; na zachytenie cez `catch` sa často používa `-ErrorAction Stop`. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## NUL-delimited stream

Textovo-binárny stream používajúci NUL byte ako oddeľovač, vhodný napríklad pre bezpečný prenos filesystem paths obsahujúcich whitespace alebo newline. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Object ID — Git

Hash-based identifikátor Git objectu odvodený z typu a obsahu objektu. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Object pipeline — PowerShell

Pipeline prenášajúca .NET objekty s properties a methods namiesto iba formátovaných textových riadkov. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## OCSP — Online Certificate Status Protocol

Protokol na zisťovanie revocation statusu certificate; server môže status poskytovať cez OCSP stapling. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Online schema change

Databázová schema operácia navrhnutá tak, aby minimalizovala blocking a downtime počas aktívnej prevádzky; jej skutočné správanie závisí od engine, verzie a dátového objemu. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## OOM killer

Kernel mechanizmus poslednej možnosti ukončujúci proces pri memory exhaustion. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Open workload model

Model, v ktorom requests prichádzajú podľa arrival rate nezávisle od aktuálnej response time systému. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Operational acceptance testing

Overenie, že systém je prevádzkovateľný: má monitoring, recovery, backup/restore, capacity, runbooks, access controls a deployment/rollback mechanizmy. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Option injection

Situácia, keď hodnota začínajúca `-` je príkazom interpretovaná ako option namiesto dátového argumentu. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## OSI model

Sedemvrstvový konceptuálny model sieťovej komunikácie. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## Over-specification — testing

Test anti-pattern, pri ktorom assertions overujú nepodstatné interné poradie alebo implementačné detaily a blokujú bezpečný refactoring. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Package manager

Nástroj na inštaláciu, upgrade a odstránenie balíkov vrátane dependencies a lokálnej evidencie. Pozri [Package management](docs/01-linux-and-systems/package-management.md).

## Packfile

Kompaktný Git storage formát ukladajúci viac objektov s možnou delta kompresiou, bez zmeny logického snapshot modelu. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Page cache

RAM používaná kernelom na cache file-backed dát. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Page fault

Udalosť, pri ktorej požadované virtuálne mapovanie nie je okamžite dostupné. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## PAM — Pluggable Authentication Modules

Framework na skladanie authentication, account, session a password policy. Pozri [Users, groups, permissions, sudo a PAM](docs/01-linux-and-systems/users-groups-permissions-sudo-pam.md).

## Partial clone

Clone režim, ktorý odloží prenos vybraných objects a načíta ich podľa potreby, napríklad s `--filter=blob:none`. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## PAT — Port Address Translation

NAT model, v ktorom viac interných flows zdieľa jednu externú adresu a rozlišuje sa preloženými portmi. Pozri [NAT](docs/02-networking-and-web/nat.md).

## PATCH version

Tretia časť SemVer verzie, ktorá sa zvyšuje pri backward-compatible oprave deklarovaného behavioru. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Path traversal

Zraniteľnosť, pri ktorej vstup s prvkami ako `..` alebo absolútnou cestou unikne z povoleného adresára. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Performance test

Test časových a kapacitných vlastností systému pri explicitnom workload modeli, prostredí a success criteria. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Permissive mode

SELinux režim, v ktorom sa policy denials auditujú, ale nevynucujú. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Pester

PowerShell test framework pre assertions, mocks, setup/teardown a test discovery. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## PID namespace

Namespace poskytujúci samostatné process ID číslovanie a process tree. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## PID — Process Identifier

Číselný identifikátor procesu v konkrétnom PID namespace. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## PIDs controller

Cgroup controller obmedzujúci počet procesov alebo threadov cez `pids.max`. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## `pipefail`

Shell option, ktorá spôsobí, že pipeline vráti nenulový status pri zlyhaní ktoréhokoľvek člena, nie iba posledného príkazu. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Pipeline as Code

Správa delivery workflowu ako versionovaného, reviewovateľného, testovateľného a policy-validovaného zdrojového kódu. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Pipeline cache

Dočasné znovupoužiteľné dáta určené na zrýchlenie pipeline, napríklad dependencies alebo compiler outputs. Cache nie je release artifact ani source of truth. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Pipeline — CI/CD

Runtime inštancia versionovaného delivery workflowu vytvorená konkrétnym triggerom a viazaná na commit, event context, variables, jobs, artifacts a results. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Pipeline — shell

Reťaz procesov, v ktorej stdout jedného procesu smeruje do stdin ďalšieho. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## PKI — Public Key Infrastructure

Systém certificate authorities, policies, trust stores, issuance, validation, rotation a revocation pre public-key identities. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Policy as Code

Strojovo vyhodnotiteľná bezpečnostná alebo prevádzková policy spravovaná ako verzovaný kód s testami a exception lifecycle. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Policy routing

Routing model, ktorý môže vyberať table podľa source address, marku, ingress interface alebo ďalších selectors. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Port

16-bit transportný identifikátor socket endpointu. Port sám neurčuje aplikačný protokol. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md).

## PowerShell provider

Abstraction layer sprístupňujúca datasources ako filesystem, registry, certificates alebo environment cez jednotné cmdlets a drives. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Pre-release identifier

SemVer časť za pomlčkou, napríklad `rc.1`, označujúca verziu s nižšou precedence než zodpovedajúci final release. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Process

Bežiaca inštancia programu s adresným priestorom, file descriptormi, credentials a ďalším kernel stavom. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## Production-derived test data

Testovacie dáta odvodené z produkcie, ktoré vyžadujú data minimization, anonymizáciu, access control a retention policy. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Production validation

Overenie technického, funkčného a business výsledku zmeny v skutočnom produkčnom kontexte po deploymente alebo počas kontrolovaného rollout-u. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Profile — performance profile

Vzorka alebo agregácia stackov ukazujúca, kde proces trávi CPU čas, čaká alebo alokuje memory. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Progressive delivery

Delivery model, ktorý postupne zvyšuje exposure novej verzie alebo funkcionality podľa observability, experimentálnych metrík a automatizovaných promotion či rollback pravidiel. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Promotion evidence

Súbor výsledkov a metadata viazaných na konkrétny artifact digest, ktoré odôvodňujú jeho postup do ďalšieho environmentu. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Protected environment

Environment s obmedzenou deployment identitou, approval alebo policy pravidlami a auditom, používaný najmä pre produkciu a citlivé stages. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Provenance attestation

Strojovo overiteľné tvrdenie o pôvode artifactu, jeho source, build procese, vstupoch a builder identity. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Provider state

Deterministicky pripravený stav providera potrebný na overenie konkrétnej consumer-driven contract interaction. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## Proxy

Sprostredkovateľ ukončujúci jednu komunikáciu a vytvárajúci samostatnú komunikáciu k ďalšiemu endpointu. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## PSI — Pressure Stall Information

Metriky času, počas ktorého tasks čakali pre nedostupnosť CPU, memory alebo I/O kapacity. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## PSS — Proportional Set Size

Odhad memory procesu, pri ktorom sa zdieľané pages pomerne rozdelia medzi procesy. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## PSScriptAnalyzer

Static analysis nástroj pre PowerShell scripts a modules, ktorý kontroluje conventions, compatibility a vybrané security patterns. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Public API — versioning

Deklarovaná compatibility boundary zahŕňajúca nielen programové interfaces, ale podľa produktu aj konfiguráciu, CLI, schemas, events, file formats a operational behavior. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Quality gate

Automatizovaný alebo kombinovaný rozhodovací bod, ktorý vyhodnotí versionovanú policy nad konkrétnou evidence a povolí, zablokuje alebo eskaluje ďalší krok delivery. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Quarantine — testing

Dočasné vyradenie nestabilného testu z blocking suite pri zachovaní pravidelného spúšťania, ownera, issue a expiry. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## QUIC

Transportný protokol nad UDP implementujúci reliable streams, congestion control, loss recovery a TLS 1.3 integráciu. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Ratcheting — quality

Model, ktorý povoľuje iba zachovanie alebo zlepšenie predchádzajúceho akceptovaného quality baseline. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Read compatibility

Schopnosť starej aj novej application verzie správne interpretovať dáta v aktuálnom schema a semantic stave. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Readiness

Stav vyjadrujúci, či instance má prijímať nový traffic. Nie je totožný s liveness. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Real User Monitoring — RUM

Zber performance a error telemetry zo skutočných používateľských klientov a sessions s možnosťou segmentácie podľa zariadenia, browsera, regiónu alebo journey. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Rebase

Operácia, ktorá replayuje commits na nový base a vytvára nové commit objects s novými IDs. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## Reconciliation

Proces porovnania a opravy rozdielov medzi dvoma reprezentáciami alebo stores, napríklad počas dual write migration. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Recovery package

Predpripravený súbor identity, kompatibility informácií, workflows a rozhodovacích podkladov potrebných na rollback, roll-forward alebo restore konkrétneho release. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Recreate deployment

Deployment stratégia, ktorá ukončí starú version fleet pred spustením a pripravenosťou novej, čo typicky vytvára downtime alebo výrazný capacity dip. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## ReDoS — Regular Expression Denial of Service

Denial-of-service riziko spôsobené regexom s patologickou runtime complexity nad útočníkom kontrolovaným vstupom. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Reflog

Lokálna evidencia pohybov refs a `HEAD`, použiteľná na recovery commitov po reset, rebase alebo zmazaní branch pred expiráciou záznamov. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Refspec

Pravidlo mapujúce source ref na destination ref pri fetch alebo push operácii. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Regex dialect

Konkrétna syntax a semantics regular expression engine-u, napríklad POSIX ERE, .NET, Python, PCRE alebo RE2. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Regression test

Test chrániaci existujúce funkčné alebo nefunkčné správanie pred nechcenou zmenou. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## Release

Produktové alebo procesné rozhodnutie sprístupniť funkcionalitu používateľom. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Release branch

Branch určená na stabilizáciu a podporu konkrétnej release line, často s backportmi a explicitným lifecycle. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release cadence

Pravidlo určujúce frekvenciu a časovanie releases, napríklad on-demand, fixed schedule, release train alebo continuous release. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release candidate

Immutable artifact považovaný za potenciálny final release, ktorý musí byť testovaný a promotionovaný bez rebuildu pod rovnakou release identity. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release management

Disciplína riadenia release identity, readiness, approvals, communication, rollout, recovery a support lifecycle od pripraveného artifactu po používateľsky dostupnú zmenu. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release manifest

Versionovaný dokument mapujúci koordinovaný release na immutable digests komponentov a relevantné configuration, infrastructure a schema revisions. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release notes

Kurátorovaná komunikácia konkrétneho release pre používateľov, administrátorov, integrátorov alebo support, zahŕňajúca dopad, breaking changes, migráciu a known issues. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release record

Auditovateľný záznam spájajúci release version, artifacts, source, config, migrations, evidence, approvals, rollout a výsledok. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release train

Cadence model, v ktorom zmeny pripravené do definovaného cutoffu vstúpia do spoločného release termínu a ostatné čakajú na ďalší vlak. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release unit

Presne definovaná množina artifactov, configov, migrations alebo koordinovaných komponentov, ktoré sa schvaľujú a release-ujú ako jeden celok. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Remote-tracking ref

Lokálny ref pod `refs/remotes/` reprezentujúci stav remote branch pri poslednom fetchi. Nie je to živý pohľad na server. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Reproducible build

Build proces, pri ktorom rovnaké explicitné vstupy a toolchain vytvoria rovnaký alebo ekvivalentný výsledný artifact. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Requirement traceability

Väzba od business potreby a požiadavky cez risk a control až po test a dôkaz výsledku. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## Rerere

Git mechanizmus `reuse recorded resolution`, ktorý zaznamená riešenie konfliktu a môže ho znovu aplikovať pri opakovanom konflikte. Pozri [Konflikty](docs/03-git-and-automation/merge-conflicts.md).

## Rerun-until-green

Anti-pattern opakovania zlyhaného testu dovtedy, kým náhodne neprejde, bez riešenia príčiny alebo zachovania prvého failure signálu. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Resilience engineering

Disciplína navrhovania a zlepšovania schopnosti sociotechnického systému predvídať, absorbovať, zotaviť sa a učiť sa z porúch a variability. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Resolved pipeline configuration

Výsledná pipeline definícia po spracovaní includes, templates, inheritance, parameters, rules a generated configu; predstavuje konfiguráciu, ktorú platforma skutočne vykoná. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## REST

Architectural style pre distributed hypermedia systems založený na constraints ako statelessness, cacheability a uniform interface. Pozri [REST APIs a WebSockets](docs/02-networking-and-web/rest-apis-and-websockets.md).

## Retransmission

Opätovné odoslanie transportných dát po detekcii straty alebo nedostatočného potvrdenia. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Reusable pipeline

Versionovaný pipeline component alebo workflow s explicitným input, output, permissions a failure contractom určený na použitie vo viacerých projects. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Reverse proxy

Proxy zastupujúci serverové služby voči klientom a vykonávajúci napríklad TLS termination, routing alebo caching. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## Ring deployment

Progressive rollout cez stabilné deployment rings s rastúcou reprezentatívnosťou alebo kritickosťou a samostatnými entry, observation a promotion podmienkami. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Risk-based deployment

Rollout policy, ktorá mení exposure, observation window, approval alebo recovery mechanizmus podľa business criticality, blast radiusu a compatibility rizika konkrétnej zmeny. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Roll-forward

Recovery stratégia nasadzujúca nový opravný artifact alebo migration namiesto návratu na starú verziu, často pre nekompatibilný alebo už zmenený shared state. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Rollback

Návrat k predchádzajúcej verzii aplikácie alebo konfigurácie. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Rollback — deployment

Recovery stratégia obnovujúca predchádzajúci kompatibilný artifact, konfiguráciu, traffic target alebo infraštruktúrny state. Neznamená automaticky návrat dát a external side effects. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Rollback window

Obdobie, počas ktorého sa zámerne zachováva schema, configuration, artifact a operational kompatibilita potrebná na bezpečný návrat na predchádzajúcu verziu. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Rolling rollback

Postupné nahrádzanie chybnej novej version fleet predchádzajúcim artifactom pri zachovaní rolling update mechanizmu a jeho compatibility obmedzení. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Rolling update

Deployment stratégia postupne nahrádzajúca staré instances novými pri zachovaní časti dostupnej capacity a dočasnej koexistencii versions. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Rollout contract

Versionovaný popis artifactu, configu, targetu, cohort, krokov, metrics, observation windows, promotion/abort policy, recovery actions a ownera progressive rollout-u. Pozri [Progressive delivery](docs/05-ci-cd-and-release/progressive-delivery.md).

## Route

Pravidlo určujúce next hop, interface a ďalšie parametre pre destination prefix. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Route summarization

Reprezentácia viacerých menších prefixes jedným väčším aggregate prefixom. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Routing rollback

Recovery operácia, ktorá po neúspešnom blue-green cutover-e presmeruje traffic späť na pôvodnú farbu. Nevracia automaticky data state. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## RPO — Recovery Point Objective

Maximálne prijateľné množstvo dát vyjadrené časovým bodom, ktoré môže byť pri obnove po katastrofe stratené. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## RSS — Resident Set Size

Množstvo pages procesu aktuálne resident v RAM. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## RTO — Recovery Time Objective

Maximálny prijateľný čas na obnovenie služby alebo business capability po katastrofickom zlyhaní. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Runner — CI/CD

Agent alebo execution capacity, ktorá prijme job od CI control plane a vykoná ho prostredníctvom zvoleného executora. Runner je zároveň capacity a security boundary. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Runner isolation

Oddelenie CI jobov, workspace, credentials, cache a execution environmentov tak, aby sa obmedzil cross-project contamination a persistence nedôveryhodného stavu. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Runner pool

Oddelená skupina runners s definovanými capabilities, trust levelom, network accessom a scaling policy. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Runspace — PowerShell

Izolovaný PowerShell execution environment s vlastným session state, používaný aj pri paralelnom spracovaní. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Safe loader — YAML

Parser režim, ktorý načítava základné dátové typy bez povolenia nebezpečnej language-specific object deserializácie. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Sample ratio mismatch

Významný rozdiel medzi plánovaným a reálnym pomerom experimentálnych variantov, ktorý môže signalizovať assignment, exposure, crash, logging alebo eligibility problém. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Sanity test

Krátka cielená kontrola konkrétnej zmeny alebo opravy. Význam sa medzi tímami líši, preto musí mať explicitný scope. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## SAST — Static Application Security Testing

Statická bezpečnostná analýza source, bytecode alebo intermediate representation bez spustenia celej aplikácie. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Saturation

Stav, keď resource nestačí okamžite obslúžiť všetku prácu a vzniká queueing alebo throttling. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## SCA — Software Composition Analysis

Analýza third-party dependencies, transitívneho graphu, licencií a známych vulnerabilities. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Scalability test

Performance test overujúci, ako sa kapacita a SLO menia po pridaní alebo odobratí resources. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Scalar — YAML

YAML node reprezentujúci jednu hodnotu, napríklad string, number, boolean alebo null. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Schema compatibility

Schopnosť aktívnych application a data consumers fungovať s aktuálnou sadou tables, columns, constraints, types a indexov počas deploymentu. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Schema validation

Overenie dát voči deklarovaným typom, required fields a constraints. Neoveruje automaticky všetky business a runtime podmienky. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## SDLC — Software Development Life Cycle

Riadený životný cyklus softvéru od potreby po vyradenie. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## SELinux security context

Label subjectu alebo objektu obsahujúci SELinux user, role, type a prípadne level/range. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Semantic compatibility — data

Zachovanie rovnakého alebo explicitne transformovaného business významu hodnôt naprieč application a schema verziami. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Semantic Versioning

Versioning kontrakt vo formáte `MAJOR.MINOR.PATCH`, ktorý komunikuje význam zmien voči deklarovanému public API. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Separation of duties

Rozdelenie právomocí tak, aby citlivú zmenu nevytvorila, neschválila a nenasadila bez nezávislej kontroly jediná identita; môže byť implementované automatizovanými policy a approvals. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Service virtualization

Nahradenie externého systému kontrolovaným simulátorom alebo sandboxom tak, aby bol test deterministickejší a lacnejší. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Session affinity

Load-balancing policy smerujúca klienta alebo key opakovane na rovnaký backend. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Shadow deployment

Deployment, ktorý spracúva kópiu produkčného workloadu bez autoritatívnej response a s blokovanými alebo izolovanými side effects. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).

## Shadow read

Neautoritatívne čítanie z novej schema alebo store vykonané popri primárnom čítaní na porovnanie výsledkov pred prepnutím. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Shadow traffic

Kópia reálneho produkčného trafficu posielaná novému systému bez použitia jeho response ako výsledku pre používateľa; vyžaduje kontrolu side effects a citlivých dát. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Shallow clone

Clone s obmedzenou ancestry históriou, typicky vytvorený cez `--depth`. Znižuje prenos, ale obmedzuje operácie závislé od plného commit graphu. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Shell expansion

Fáza, v ktorej shell spracuje parameter, command a arithmetic expansion, word splitting a pathname expansion pred spustením príkazu. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Shift-left

Presun vhodných rozhodnutí, kontrol a feedbacku do skorších fáz delivery, kde možno riziko zachytiť lacnejšie bez neprimeranej straty fidelity. Pozri [Shift-left](docs/04-testing-and-quality/shift-left.md).

## Shift-right

Rozšírenie validácie, observability a experimentovania do deploymentu a produkcie s kontrolovaným blast radiusom a jasnými rozhodovacími kritériami. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## `ShouldProcess` — PowerShell

PowerShell mechanizmus podporujúci `-WhatIf` a `-Confirm` pre vedome označené mutation operácie. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## SLAAC — Stateless Address Autoconfiguration

IPv6 mechanizmus, ktorým host vytvára adresu z prefixu oznamovaného Router Advertisement. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Smoke test

Krátky široký test overujúci, či je build alebo deployment dostatočne funkčný na pokračovanie ďalších kontrol alebo prevádzky. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## SNAT — Source NAT

Preklad source adresy alebo portu, používaný typicky pri outbound komunikácii. Pozri [NAT](docs/02-networking-and-web/nat.md).

## SNI — Server Name Indication

TLS extension prenášajúca hostname, aby server alebo proxy vybral správny certificate a virtual host. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Soak test

Dlhodobý performance test hľadajúci memory leaks, resource leaks, queue growth a kumulatívne zlyhania. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Socket

Kernel endpoint komunikácie sprístupnený procesu cez file descriptor. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md).

## Spike test

Performance test prudkej zmeny trafficu, ktorý overuje autoscaling, queues, caches, connection pools a recovery. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Splatting — PowerShell

Odovzdanie kolekcie named alebo positional parameters príkazu pomocou hashtable alebo array. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Split-horizon DNS

DNS model, v ktorom rovnaké meno vracia rozdielne odpovede podľa resolvera, siete alebo klientského contextu. Pozri [DNS](docs/02-networking-and-web/dns.md).

## Spy — test double

Test double alebo wrapper zaznamenávajúci uskutočnené interakcie na neskoršie assertions. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Squash merge

Integrácia, ktorá vytvorí jeden výsledný commit bez merge ancestry na feature tip. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## SSH agent

Proces vykonávajúci podpisové operácie pomocou odomknutých private keys v pamäti. Pozri [SSH](docs/01-linux-and-systems/ssh.md).

## Stable bucketing

Deterministické mapovanie subjektov do percentuálnych rollout alebo experiment buckets tak, aby sa variant nemenil náhodne medzi requestmi. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Stage — CI/CD

Logická skupina jobs alebo broad ordering barrier v pipeline. Stage nie je samostatná execution unit a pri presnom DAG modeli nemusí určovať všetky dependencies. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Staging area

Používateľský názov pre Git index ako pripravovaný snapshot ďalšieho commitu. Pozri [Working tree, staging area a repository](docs/03-git-and-automation/working-tree-staging-repository.md).

## Stash — Git

Lokálny Git stav uchovávajúci dočasné working-tree a index changes pod `refs/stash`. Nie je náhradou remote backupu. Pozri [Cherry-pick a stash](docs/03-git-and-automation/cherry-pick-and-stash.md).

## State-based testing

Testovanie výsledného outputu alebo stavu namiesto detailného overovania interných interakcií. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Stateful firewall

Firewall udržiavajúci connection/flow state a používajúci ho pri rozhodovaní o packets. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Stateless firewall

Firewall posudzujúci každý packet podľa explicitných pravidiel bez connection state. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Static analysis

Analýza source alebo jeho reprezentácie bez vykonania celej aplikácie, napríklad linting, type checking alebo data-flow analysis. Pozri [Static analysis, linting a type checking](docs/04-testing-and-quality/static-analysis-linting-type-checking.md).

## Steady state — chaos engineering

Merateľné používateľské alebo prevádzkové správanie, ktoré má systém počas definovaného faultu zachovať v prijateľných hraniciach. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## `strace`

Nástroj na sledovanie system calls, ich výsledkov a trvania. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Stress test

Performance test nad plánovanou kapacitou zameraný na failure mode, ochranné mechanizmy a recovery. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Stub — test double

Kontrolovaná náhrada dependency vracajúca vopred pripravené odpovede pre riadenie testovacieho scenára. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Subnet

Časť IP address space definovaná prefixom a použitá ako logická routing alebo topology jednotka. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Subshell

Oddelený shell execution context, ktorého zmeny premenných a working directory sa nemusia preniesť späť do parent shellu. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Supported version policy

Pravidlá určujúce, ktoré release lines dostávajú opravy, security updates a podporu a kedy dosiahnu end of life. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Swap

Storage-backed priestor pre niektoré anonymné memory pages. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Symbolic link

Filesystem objekt obsahujúci textovú cestu na iný objekt. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## Synthetic merge commit

Dočasný commit reprezentujúci výsledok zlúčenia source branch so súčasným target branch, používaný na testovanie budúceho mainline stavu. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Synthetic monitoring

Pravidelné spúšťanie kontrolovaného produkčného scenára z definovanej lokality na overenie používateľskej cesty. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## Synthetic test data

Umelo generované testovacie dáta bez priameho kopírovania reálnych osobných alebo citlivých záznamov. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## system call

Kontrolovaný prechod z user space do kernel space. Pozri [Kernel a user space](docs/01-linux-and-systems/kernel-and-user-space.md).

## systemd timer

`.timer` unit aktivujúca inú unit podľa calendar alebo monotonic pravidla. Pozri [Cron a systemd timers](docs/01-linux-and-systems/cron-and-systemd-timers.md).

## systemd unit

Deklaratívny objekt spravovaný systemd, napríklad `.service`, `.socket` alebo `.timer`. Pozri [systemd, services a daemons](docs/01-linux-and-systems/systemd-services-daemons.md).

## T-shaped engineer

Inžinier so širokou orientáciou a hlbokou expertízou aspoň v jednej oblasti. Pozri [T-shaped engineer](docs/00-foundations/t-shaped-engineer.md).

## Tabletop exercise

Simulované incident alebo disaster-recovery cvičenie bez technického fault injection, ktoré overuje rozhodovanie, prístupy, runbooky, komunikáciu a ownership. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Tag — Git tag

Ref používaný typicky na stabilné označenie konkrétneho release commitu alebo iného objektu. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Tail latency

Latency najpomalšej časti request distribúcie, typicky p95 alebo p99. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Taint analysis

Statická analýza sledujúca nedôveryhodné dáta od source cez transformácie po citlivý sink. Pozri [Static analysis, linting a type checking](docs/04-testing-and-quality/static-analysis-linting-type-checking.md).

## TCP connection

Transportný byte stream identifikovaný source/destination IP adresami a portmi. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## TCP handshake

Výmena SYN, SYN-ACK a ACK, ktorá synchronizuje sequence numbers a vytvorí TCP connection state. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## TCP/IP model

Praktický vrstvený model Application, Transport, Internet a Link používaný na opis Internet stacku. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## Template contract — CI/CD

Versionované pravidlá reusable template definujúce inputs, defaults, outputs, artifacts, permissions, supported scenarios, failure semantics a compatibility policy. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Terminating error — PowerShell

PowerShell error, ktorý zastaví aktuálnu operáciu alebo scope a môže byť zachytený cez `try/catch`. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Test data factory

Programový builder vytvárajúci minimálne validné testovacie objekty so stabilnými defaults a explicitnými overrides. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Test double

Kontrolovaná náhrada dependency používaná v teste; zahŕňa dummy, stub, fake, spy a mock. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Test fidelity

Miera, do akej test zachováva produkčne relevantné komponenty, protokoly, konfiguráciu a failure modes. Pozri [Test pyramid](docs/04-testing-and-quality/test-pyramid.md).

## Test isolation

Vlastnosť testu, pri ktorej jeho výsledok nezávisí od poradia, paralelných testov ani zdieľaného mutable state. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Test oracle

Mechanizmus alebo pravidlo rozhodujúce, či je pozorovaný test result správny. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## Test pyramid

Model test portfolio s veľkou vrstvou rýchlych úzkych kontrol, menšou integračnou vrstvou a obmedzeným počtom drahých E2E testov. Pozri [Test pyramid](docs/04-testing-and-quality/test-pyramid.md).

## Test sharding

Rozdelenie test suite medzi paralelné jobs podľa súborov, test IDs alebo historical duration s následnou validáciou úplnosti a agregáciou reportov. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Test trophy

Alternatívny model zvýrazňujúci static checks a integration tests ako hlavný zdroj hodnoty, s menšou unit a E2E vrstvou. Pozri [Test pyramid](docs/04-testing-and-quality/test-pyramid.md).

## Thread

Plánovateľná vykonávacia jednotka v rámci procesu. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## Threat model

Štruktúrovaný opis assets, trust boundaries, aktérov, attack surfaces, abuse cases a mitigations. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Throughput

Množstvo práce dokončenej za jednotku času. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Time to first feedback

Čas od vzniku alebo odoslania zmeny po prvý relevantný a diagnostikovateľný výsledok pipeline. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## `TIME-WAIT`

TCP state držaný po aktívnom close na ochranu pred starými segments a opätovným použitím rovnakého tuple. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## TLS termination

Ukončenie TLS spojenia na proxy alebo load balanceri, ktorý následne vytvorí samostatné upstream spojenie. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## TLS — Transport Layer Security

Protokol poskytujúci šifrovanie, integritu a autentifikáciu komunikácie. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Toil

Manuálna, opakujúca sa, automatizovateľná a nízko hodnotná prevádzková práca. Pozri [Toil and Technical Debt](docs/00-foundations/toil-and-technical-debt.md).

## Traffic cutover

Riadené presmerovanie nových requestov alebo connections zo starej deployment farby na novú. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Traffic mirroring

Kopírovanie produkčných requestov do shadow systému bez použitia jeho response na primary request path. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).

## Trap — shell

Shell handler spustený pri definovanom signále alebo pseudo-signále ako `EXIT` či `ERR`. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Treatment variant

Experimentálny variant obsahujúci testovanú zmenu, ktorého outcome sa porovnáva s control variantom. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Trigger — CI/CD

Udalosť alebo explicitný pokyn, ktorý vytvorí pipeline run a určí jeho commit, event payload, actor identity, variables a permission context. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Trunk-based development

Branching model založený na častej integrácii malých zmien do jednej hlavnej branch, podporený krátkodobými branches, CI a feature flags. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## TTL — Time To Live

IPv4 field znižovaný na každom router hop-e; pri nule sa packet zahodí. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Type checking

Statická kontrola konzistencie typových kontraktov a operácií. Nenahrádza runtime validáciu nedôveryhodných vstupov. Pozri [Static analysis, linting a type checking](docs/04-testing-and-quality/static-analysis-linting-type-checking.md).

## Type enforcement

SELinux policy model založený na source type, target type, object class a permissions. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Type hint — Python

Anotácia očakávaného typu používaná static analysis nástrojmi a IDE; sama osebe nie je runtime validáciou. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## UAT — User Acceptance Testing

Acceptance activity vykonaná alebo schválená reprezentatívnym business používateľom či stakeholderom na overenie fitu s reálnym procesom. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## UDP datagram

Samostatná transportná správa bez zabudovanej garancie doručenia, poradia alebo retransmission. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Unit test

Rýchly test malej izolovanej jednotky správania s úzkym diagnostickým scope-om. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Upstream branch

Remote-tracking alebo iný ref priradený lokálnej branch ako default comparison a synchronization target pre status, pull a push. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## URI — Uniform Resource Identifier

Identifikátor resource; URL je typ URI, ktorý zároveň opisuje spôsob alebo miesto prístupu. Pozri [HTTP](docs/02-networking-and-web/http.md).

## USE method

Performance metodika kontrolujúca utilization, saturation a errors každého resource. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## User namespace

Namespace izolujúci UID/GID mapping a capability scope. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## User space

Menej privilegované prostredie, v ktorom bežia aplikácie a systémové procesy. Pozri [Kernel a user space](docs/01-linux-and-systems/kernel-and-user-space.md).

## Utilization

Miera použitia dostupnej kapacity resource. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Validation — testing

Overenie, či systém rieši správny používateľský alebo business problém v reálnom kontexte. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## Value stream

Celý tok práce a informácií od potreby po hodnotu doručenú používateľovi. Pozri [Value Stream Mapping](docs/00-foundations/value-stream-mapping.md).

## Verification — testing

Overenie, či systém alebo artifact zodpovedá explicitnej špecifikácii, kontraktu alebo pravidlu. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## Version-level telemetry

Metrics, logs a traces označené konkrétnou application alebo artifact verziou, ktoré umožňujú porovnať old a new behavior počas rollout-u. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Version precedence

SemVer pravidlá určujúce poradie versions podľa MAJOR, MINOR, PATCH a pre-release identifiers; build metadata sa pri precedence ignorujú. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Version range

Constraint vyjadrujúci množinu akceptovaných dependency versions, ktorého konkrétna syntax a význam závisia od package ecosystemu. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Virtual environment — Python

Izolované Python prostredie s vlastným interpreter contextom a nainštalovanými packages. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Virtual memory

Abstrakcia, pri ktorej má proces vlastný virtuálny adresný priestor mapovaný kernelom na RAM, files alebo swap. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## VLAN — Virtual LAN

Logicky oddelený Ethernet broadcast domain, často prenášaný cez 802.1Q tagging. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## VSZ — Virtual Set Size

Veľkosť virtuálneho adresného priestoru procesu. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Vulnerability reachability

Posúdenie, či je zraniteľný component a code path skutočne prítomný, dostupný a využiteľný v konkrétnom runtime kontexte. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## WAF — Web Application Firewall

L7 security control vyhodnocujúci HTTP requests podľa aplikačných pravidiel; nie je totožný s L3/L4 firewallom. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Warm standby — blue-green

Pôvodná deployment farba ponechaná po cutover-e v pripravenom a priebežne health-checkovanom stave pre rýchly routing rollback. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## WebSocket

Protokol poskytujúci dlhodobý full-duplex message channel po HTTP upgrade alebo ekvivalentnom transportnom mechanizme. Pozri [REST APIs a WebSockets](docs/02-networking-and-web/rest-apis-and-websockets.md).

## Word splitting

Shell rozdelenie nequoted expansion výsledku na viac slov podľa `IFS`. Je častým zdrojom chýb pri paths a argumentoch. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Workflow template

Versionovaný reusable opis viacerých jobs, dependencies a policy hooks poskytujúci štandardnú delivery capability pre viaceré projects. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Working tree

Filesystem materialization aktuálne checkoutnutého Git snapshotu, ktorú používateľ a nástroje priamo menia. Pozri [Working tree, staging area a repository](docs/03-git-and-automation/working-tree-staging-repository.md).

## Write compatibility

Schopnosť každej súčasne aktívnej application verzie zapisovať dáta, ktoré ostatné aktívne verzie bezpečne prečítajú a interpretujú. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## `X-Forwarded-For`

De facto HTTP header prenášajúci client IP cez proxy chain. Je dôveryhodný iba pri kontrolovanom chain-e a správnom prepisovaní. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## YAML mapping

YAML kolekcia key-value párov, analogická objectu alebo dictionary. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## YAML sequence

Usporiadaná YAML kolekcia hodnôt, analogická array alebo listu. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Zombie process

Ukončený proces, ktorého exit status parent ešte neprevzal cez `wait`. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).
