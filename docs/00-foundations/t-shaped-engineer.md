# T-shaped, I-shaped a π-shaped Engineer

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [DevOps](devops.md), [Systems Thinking](systems-thinking.md)
- Súvisiace témy: skill matrix, ownership, platform engineering, career development, team topology

Metadata zaraďuje kapitolu medzi organizačné a profesijné základy. Skill-shape model nie je hodnotenie osobnosti ani požiadavka naučiť sa všetky technológie; opisuje rozloženie pracovnej šírky a expertnej hĺbky.

## 1. Definícia

T-shaped engineer má dostatočne široký systémový prehľad na spoluprácu cez technické boundaries a zároveň hlbokú expertízu v jednej oblasti, v ktorej dokáže diagnostikovať, navrhovať a obhajovať riešenia. Horizontála vytvára spoločný jazyk a vertikála poskytuje expertízu potrebnú pri komplexnom probléme.

```text
šírka pracovného porozumenia
────────────────────────────────────────────
                 │
                 │ hlboká expertíza
                 │
                 │
```

Model nehovorí, že každý engineer musí mať rovnakú šírku alebo tú istú vertikálu. Je užitočný najmä pri návrhu kolektívnych schopností tímu, kariérneho rozvoja a escalation paths.

## 2. Problém, ktorý skill-shape model rieši

Moderný incident často prekračuje hranice jedného nástroja. Kubernetes Pod môže zlyhávať pre DNS, cloud route, TLS trust, database connection pool, resource limits, secret delivery alebo application behavior.

Čisto úzka expertíza môže viesť k lokálnej optimalizácii a množstvu handoffov. Čisto široký profil môže identifikovať affected layers, ale nemusí mať hĺbku na bezpečný redesign control plane-u, database recovery alebo multi-account identity modelu.

Skill-shape model pomáha odlíšiť tri schopnosti:

- **Orientácia — určenie relevantnej vrstvy**: engineer vie, aké components a evidence patria do problem space-u.
- **Spolupráca — komunikácia cez boundary**: dokáže formulovať symptóm, hypotheses a požadovaný input pre špecialistu bez neurčitého ticketu.
- **Expert resolution — hlboká práca v doméne**: rozumie internému state-u, failure modes a trade-offs natoľko, aby navrhol a overil nápravu.

## 3. Šírka a hĺbka ako odlišné druhy znalosti

Šírka neznamená poznať syntax desiatok produktov. Znamená mať použiteľný mentálny model susedných disciplín a vedieť rozpoznať, keď je symptom iba prejavom problému na inej boundary.

Hĺbka nie je množstvo zapamätaných príkazov. Prejavuje sa schopnosťou vysvetliť interný mechanismus, predvídať failure behavior, diagnostikovať ambiguous evidence a obhájiť návrh proti alternatívam.

## 4. Použiteľná horizontálna šírka

Pri susednej oblasti má engineer vedieť viac než definíciu. Potrebuje minimum, ktoré podporuje end-to-end reasoning:

- **Účel oblasti — aký systémový problem rieši**: napríklad DNS mapuje names na records a ovplyvňuje service discovery, nie iba „prekladá adresy“.
- **Hlavné actors a state — kto komunikuje a kde je authoritative informácia**: pri IAM treba rozlíšiť principal, credential, policy a resource decision.
- **Inputs a outputs — čo prechádza cez boundary**: certificate, token, packet, artifact alebo query majú odlišný trust a lifecycle contract.
- **Bežné failure modes — ako sa problém prejaví**: timeout, deny, stale data, saturation alebo integrity error smerujú diagnosis na inú vrstvu.
- **Evidence sources — čo môže hypotézu potvrdiť**: logs, metrics, packet capture, audit event alebo database state majú rozdielnu autoritu a completeness.
- **Escalation threshold — kedy potrebuje špecialistu**: engineer má vedieť bezpečne zastaviť vlastný zásah pred poškodením state-u alebo trust boundary.

## 5. Príklad šírky v databázovej oblasti

DevOps engineer nemusí navrhovať query optimizer, ale databázová šírka musí byť prevádzkovo použiteľná. Pri application latency má vedieť odlíšiť connection acquisition, lock wait, slow query, storage saturation a replication lag.

Relevantné koncepty majú konkrétnu úlohu:

- **Transaction — atomicita a consistency boundary**: určuje, ktoré writes sa commitnú spolu a čo sa stane pri partial failure.
- **Connection pool — obmedzená concurrency vrstva**: saturation poolu môže vytvárať application timeout aj pri zdravej CPU databázy.
- **Index — read performance a write cost trade-off**: nesprávny alebo chýbajúci index mení query plan, storage a maintenance behavior.
- **Lock — koordinácia concurrent accessu**: blocking chain môže vytvoriť tail latency a deadlock bez vysokého resource utilization.
- **Replication — availability a read-scale mechanismus**: lag ovplyvňuje stale reads, failover data loss a recovery decision.
- **Backup a restore — ochrana authoritative state-u**: backup success nestačí bez decryption, application consistency a recovery testu.

## 6. Dôkaz vertikálnej hĺbky

Hlboká expertíza sa preukazuje na zložitejších úlohách, nie self-ratingom. Expert vie prejsť od symptom-u k internému state-u, vyhodnotiť viac hypotheses a navrhnúť riešenie s explicitnými trade-offs.

Hĺbka zahŕňa:

- **Internal mechanisms — state machines, control loops a data structures**: umožňujú predvídať behavior mimo happy pathu.
- **Failure modes — očakávané aj neobvyklé zlyhania**: expert vie, ktoré evidence odlišuje podobné symptoms.
- **Performance characteristics — limits a nonlinearities**: rozumie queueing, caching, contention a scale boundaries.
- **Security boundaries — identity, authority a trust**: vie, kde sa control presadzuje a čo nezaručuje.
- **Lifecycle — upgrade, migration, rollback a retirement**: návrh počíta s budúcou zmenou state-u, nie iba prvým deploymentom.
- **Design trade-offs — porovnanie alternatív podľa constraints**: dokáže vysvetliť, prečo jednoduchšie riešenie môže byť vhodnejšie než technicky pokročilejšie.
- **Teaching and review — schopnosť preniesť model**: expert znižuje bus factor a zlepšuje decision quality tímu.

## 7. Úrovne znalosti

Úroveň má opisovať behavior, ktorý možno pozorovať a overiť. Pomenovanie technológie v životopise alebo absolvovaný kurz nie sú samostatným dôkazom praktickej schopnosti.

```text
L0 — tému nepoznám alebo ju neviem spoľahlivo rozpoznať
L1 — viem pojem definovať a odlíšiť od susedného konceptu
L2 — rozumiem actors, state-u, flowu a hlavným failure modes
L3 — viem mechanizmus samostatne použiť v bounded scenári
L4 — viem diagnostikovať ambiguous failure a obnoviť systém
L5 — viem navrhnúť, obhájiť, migrovať a učiť riešenie
```

Rovnaký človek môže mať v jednej oblasti L5 a v susednej L2. Model pomáha vybrať ďalší praktický dôkaz, nie vytvoriť jeden celkový „seniority score“.

## 8. I-shaped engineer

I-shaped engineer má hlbokú expertízu v jednej doméne a obmedzenejší pracovný prehľad mimo nej. Je mimoriadne hodnotný pri problémoch, kde je potrebné rozumieť interným detailom, formal correctness alebo špecializovanému hardware a protocolu.

Výhody a riziká vychádzajú z rovnakého tvaru:

- **Vysoká doménová hĺbka — riešenie expert-only problemov**: tím má človeka schopného analyzovať interný state a neštandardný failure.
- **Silná review capability — ochrana critical designu**: expert odhalí trade-off alebo compatibility risk, ktorý všeobecný reviewer nevidí.
- **Obmedzená cross-boundary orientácia — viac handoffov**: symptom môže zostať nesprávne priradený vlastnej doméne alebo sa vracať medzi tímami.
- **Local optimization risk — najlepší výsledok pre component**: solution môže poškodiť flow, operability alebo cost celého systému.

I-shaped profil nie je „horší“. Potrebuje doplňujúci tímový interface a dostatočnú spoločnú horizontálu na efektívnu spoluprácu.

## 9. T-shaped engineer

T-shaped engineer kombinuje jednu hlbokú vertikálu s pracovným porozumením celého relevantného system pathu. Vie viesť diagnosis cez viac vrstiev a zároveň prevziať expert ownership vo svojej doméne.

Rizikom je falošná šírka. Ak človek venuje čas veľkému počtu produktov bez laboratórnej alebo production skúsenosti, môže vedieť terminology, ale nie boundaries ani failure evidence.

## 10. π-shaped a comb-shaped profil

π-shaped engineer má dve hlboké oblasti spojené spoločnou horizontálou. Profil je silný, keď vertikály tvoria dôležitú boundary, napríklad Kubernetes a cloud networking alebo application runtime a observability.

Comb-shaped profil má viac expert vertikál vybudovaných počas dlhšieho obdobia. Jeho rizikom je maintenance cost: technológie a standards sa menia a nie je realistické udržať L5 hĺbku vo veľkom počte aktívnych oblastí bez pravidelnej praxe.

Tvar preto nie je statická identita. Vertikála môže časom slabnúť, rozšíriť sa alebo presunúť podľa roly, produktu a organization needs.

## 11. Kolektívny T-shaped tím

Najdôležitejší je profil tímu, nie hero jednotlivca. Členovia môžu zdieľať základnú horizontálu a mať rozdielne vertikály, ktoré pokrývajú kritické service boundaries.

```text
Engineer A — Kubernetes a orchestration
Engineer B — application runtime a performance
Engineer C — networking, identity a security
Engineer D — database a data recovery

Spoločná horizontála — SDLC, Git, delivery, observability, incident response
```

Kolektívny model prináša konkrétne výhody:

- **Menší knowledge silo — viac ľudí rozumie interface-u**: expert nie je jediný, kto dokáže identifikovať alebo eskalovať failure.
- **Nižší bus factor — zastupiteľnosť critical capability**: dovolenka alebo odchod jedného človeka nevyradí recovery a change path.
- **Kvalitnejší design review — viac perspektív**: security, runtime a data trade-offs vstupujú do návrhu pred production failure-om.
- **Menej slepých handoffov — presnejší shared language**: tím dokáže odovzdať evidence a hypothesis, nie iba symptom.

## 12. Skill coverage a critical paths

Tím nemá budovať vertikály podľa popularity technológií. Má mapovať critical user a operational paths a zistiť, kde chýba diagnosis, design alebo recovery capability.

Ak služba používa Kubernetes, managed database, OIDC a Kafka, kritické vertikály sa viažu na orchestration, data, identity a messaging. Ďalší frontend framework nemusí byť najväčšou capability medzerou pre on-call a recovery.

Coverage sa posudzuje aj podľa času. Musí existovať niekto schopný reagovať počas incidentu, nie iba externý expert dostupný o niekoľko dní.

## 13. Vzťah k DevOps a ownershipu

DevOps potrebuje cross-boundary feedback a shared service outcome. T-shaped profil pomáha engineerovi rozumieť, ako jeho zmena ovplyvní build, deployment, runtime, security a user experience.

Praktická hodnota horizontály sa prejavuje takto:

- **Impact reasoning — identifikácia downstream consequences**: configuration change sa posudzuje aj cez rollout, recovery a cost.
- **Shared language — presná komunikácia so špecialistom**: ticket obsahuje evidence, timestamps a hypotheses namiesto „nefunguje sieť“.
- **Root-cause localization — rozlíšenie vrstiev**: engineer vie, kedy je Pod symptomom DNS alebo database saturation.
- **Escalation — zapojenie správnej expertízy**: ownership znamená zabezpečiť resolution, nie osobne vykonať každý zásah.
- **Lifecycle design — operability od planningu**: expertíza sa premieta do tests, telemetry a migration, nie až do incident response.

## 14. Budovanie horizontálnej šírky

Šírka sa buduje cez fundamenty a interfaces, nie cez memorovanie UI. Každá oblasť má dosiahnuť minimálne mechanistické porozumenie a bounded praktický dôkaz.

DevOps horizontála typicky zahŕňa:

- **SDLC a DevOps — tok zmeny a ownership**: engineer chápe build, release, deployment, feedback a production outcome.
- **Linux a systems — process, memory, storage a permissions**: umožňujú diagnosis host a container runtime behavioru.
- **Networking a DNS — packet path a name resolution**: timeout sa analyzuje cez route, policy, transport a application boundary.
- **Git a source control — change identity a collaboration**: history, branching a review podporujú audit a safe integration.
- **Testing a CI/CD — evidence a promotion**: rozlišuje test boundaries, artifact identity, gates a rollout.
- **Security a identity — trust a authorization**: principal, credential, policy, encryption a audit sa posudzujú cez threat boundary.
- **Containers a Kubernetes — packaging a reconciliation**: engineer rozumie image, scheduling, probes, services, storage a control loopom.
- **Cloud — responsibility a failure domains**: services sa vyberajú podľa ownershipu, scope-u, costu a recovery.
- **Observability — evidence a correlation**: metrics, logs a traces sa používajú na hypothesis-driven diagnosis.
- **Databases a messaging — state, consistency a delivery**: transaction, replication, queue a idempotency ovplyvňujú correctness.
- **SRE a incident management — reliability a recovery**: SLO, alerting, mitigation a learning prepájajú runtime s engineering backlogom.

## 15. Budovanie vertikálnej hĺbky

Hĺbka vzniká opakovaným kontaktom s interným mechanismom a následkami rozhodnutí. Čítanie vytvorí vocabulary a model, ale diagnosis a design vyžadujú labs, failures, migrations a review reálnych riešení.

```text
teória a source documentation
→ minimálna implementácia
→ controlled failure a troubleshooting
→ production-like scale a lifecycle
→ porovnanie alternatív
→ vysvetlenie, review a teaching
→ zložitejší scenár
```

Najväčší rast často vzniká pri zlyhaní hypothesis. Engineer, ktorý vie iba opakovať úspešný tutorial, ešte nemá evidence o behavior-e pri partial state, upgrade alebo dependency outage.

## 16. Skill matrix

Skill matrix mapuje capability na pozorovateľný dôkaz. Jej cieľom nie je vytvoriť ranking ľudí, ale identifikovať team coverage, single points a ďalší praktický krok.

| Oblasť | Aktuálny behavior | Cieľový behavior | Dôkaz |
|---|---|---|---|
| Linux | samostatná základná diagnosis procesu | analyzovať CPU, memory a I/O contention | zdokumentovaný failure lab a recovery |
| Networking | rozumie DNS a routes | izolovať packet, TLS a policy boundary | end-to-end packet-path troubleshooting |
| Terraform | spravuje resources a modules | navrhnúť multi-account state a recovery | architecture review, import a recovery exercise |
| Kubernetes | prevádzkuje workloads | diagnostikovať scheduling, network a storage failure | CKA-style drills a production incident evidence |
| Databases | pozná základné queries | rozumie transactions, pooling, locks a restore | lab s contention, backup a application validation |

Self-rating sa má doplniť reviewom a artifactom. Certifikát môže byť jeden dôkaz, ale nepreukazuje automaticky production design a recovery capability.

## 17. Learning plan a priority

Rozvoj nemá rovnakú prioritu pre všetky oblasti. Horizontála sa zvyšuje tam, kde chýba schopnosť lokalizovať incident alebo spolupracovať, a vertikála tam, kde tím nemá expert coverage pre critical path.

Praktický learning goal má formu behavioru: „dokážem diagnostikovať DNS timeout od Podu po authoritative resolver“ je lepší než „naučím sa DNS“. Definuje scope, evidence a completion condition.

## 18. End-to-end troubleshooting príklad

Aplikácia v Kubernetes nedokáže komunikovať s databázou. Nástrojový prístup reštartuje Pod, ale T-shaped reasoning najprv rozdelí path na hypotheses.

```text
application configuration a timeout
→ Secret a runtime environment
→ DNS resolution
→ Pod a Node networking
→ NetworkPolicy, firewall a security group
→ TLS handshake a trust
→ database listener a authentication
→ connection pool, limits a locks
→ correlated logs, metrics a audit
```

Šírka umožní určiť failure boundary a získať správne evidence. Hĺbka database alebo network experta potom rieši interný state, ak problém prekročí bounded capability aplikačného tímu.

## 19. Anti-patterny

### Checklist collector

Engineer zbiera názvy tools a certifikáty bez mechanistickej alebo praktickej väzby. Profil vyzerá široko, ale pri incidente nevie určiť evidence ani boundaries.

### Expert silo

Jeden človek rieši všetky kritické failures a decisions. Tím nezískava horizontálu, documentation ani zastupiteľnosť a expert sa stáva bottleneckom.

### Forced generalist

Organizácia očakáva, že každý bude produkčný expert na všetko, a ruší špecializované roly. Výsledkom je povrchný design, stress a nebezpečné zásahy mimo kompetencie.

### Skill matrix ako performance ranking

Úrovne sa používajú na porovnávanie ľudí namiesto plánovania coverage a learningu. Ľudia potom nadhodnocujú score a skrývajú neistotu.

### Hĺbka bez lifecycle-u

Engineer pozná setup a syntax, ale nie upgrade, rollback, security a recovery. Expertíza funguje iba pri prvom happy-path deployment-e.

## 20. Kontrolné otázky

1. Aký rozdiel je medzi horizontálnou šírkou a vertikálnou hĺbkou?
2. Prečo šírka neznamená iba poznať názvy technológií?
3. Aké behaviorálne evidence dokazujú hlbokú expertízu?
4. Kedy je I-shaped profil pre tím veľmi hodnotný a aké interface potrebuje?
5. Ako sa T-shaped, π-shaped a comb-shaped profily líšia?
6. Prečo je kolektívny skill shape dôležitejší než profil jedného človeka?
7. Ako sa mapujú vertikály na critical service paths?
8. Akú horizontálnu database znalosť potrebuje DevOps engineer?
9. Prečo certifikát alebo self-rating nie je dostatočný dôkaz úrovne?
10. Ako navrhneš learning goal, ktorý má pozorovateľný completion condition?

## 21. Zhrnutie

Skill-shape model spája pracovnú šírku s expert hĺbkou. Šírka podporuje system orientation, collaboration a správnu escalation, zatiaľ čo hĺbka umožňuje diagnosis, design a lifecycle ownership v komplexnej doméne.

Cieľom nie je vytvoriť univerzálneho jednotlivca. Zdravý tím má spoločnú horizontálu, dopĺňajúce sa vertikály, zastupiteľnosť a learning plán odvodený od critical paths a reálnych evidence medzier.

## Glossary impact

Relevantné pojmy: I-shaped engineer, T-shaped engineer, π-shaped engineer, comb-shaped engineer, horizontal breadth, vertical depth, skill matrix, behavior evidence, collective capability, bus factor a critical-path coverage.

## Primárne zdroje

- [Team Topologies](https://teamtopologies.com/)
- [Google Cloud — DevOps capabilities](https://cloud.google.com/architecture/devops)
- [DORA — Research program](https://dora.dev/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Continuous improvement](continuous-improvement.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ownership mindset →](ownership-mindset.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
