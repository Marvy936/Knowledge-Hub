# Platform as a Product

Platform as a Product je operating model, v ktorom interná platforma nie je posudzovaná podľa počtu nasadených nástrojov, vytvorených templátov alebo uzavretých infraštruktúrnych ticketov. Je posudzovaná ako dlhodobo spravovaný produkt pre interných používateľov: musí riešiť konkrétne jobs-to-be-done, poskytovať zrozumiteľné capability contracts, preukazovať použiteľný outcome, získavať dôveru a vyvíjať sa podľa evidence.

Tento prístup nemení platformu na komerčný SaaS ani application tím na externého zákazníka bez zodpovednosti. Mení rozhodovací mechanizmus platformového tímu. Namiesto modelu „vybudovali sme centralizovaný tool, preto ho musia používať všetci“ používa model „poznáme používateľský problém, definovali sme value hypothesis, dodali sme bezpečnú capability, overili sme end-to-end výsledok a podľa adopcie, friction a business impactu rozhodujeme, čo ďalej“.

## 1. Dominantný model

Dominantný model sleduje platform capability od pozorovaného používateľského problému až po udržateľný product outcome. Každá transition má iný dôkaz: interview alebo journey telemetry dokazuje problém, product decision autorizuje investíciu, capability contract definuje sľub, platform operation realizuje službu a adopcia s developer/business výsledkom overuje hodnotu.

Platform product acceptance preto nevzniká pri release platformového komponentu. Release je iba zmena ponuky. Skutočný verdict vyžaduje, aby relevantný user segment dokázal capability objaviť, pochopiť, bezpečne použiť, prevádzkovať a opakovane získať očakávaný outcome bez neprimeranej podpory alebo skrytého presunu toil-u.

```text
observed developer alebo product-team problem
→ exact user segment, journey a job-to-be-done
→ product outcome a falsifikovateľná value hypothesis
→ prioritized roadmap decision a capability contract
→ bounded implementation a release
→ discoverability, onboarding a supported adoption
→ usable developer, operational a business outcome
→ telemetry, qualitative feedback a support evidence
→ product decision: improve, expand, maintain, migrate alebo retire
→ second-cohort a second-change validation
```

Platform as a Product acceptance verdict musí korelovať product intent, capability generation, target segment, adoption, end-to-end success, support burden, reliability, cost a business effect. Vysoký počet portal klikov alebo úspešných scaffolder taskov môže existovať súčasne s nízkou dôverou, vysokým abandonmentom a pomalým časom k prvému production outcome-u.

## 2. Platform project, platform service a platform product

Tieto pojmy sa môžu technicky prekrývať, ale majú odlišný lifecycle a decision model. Ich rozlíšenie zabraňuje tomu, aby dočasný implementačný projekt alebo prevádzkovaná infraštruktúrna služba boli automaticky považované za produkt, ktorý rieši potreby interných používateľov.

### Platform project

Platform project je časovo ohraničená iniciatíva, napríklad zavedenie GitOps, migrácia na nový registry alebo vytvorenie prvého developer portalu. Projekt má scope, termín a delivery outputs. Môže sa úspešne skončiť, hoci výsledná capability nemá adopciu, support model ani bezpečný upgrade path.

### Platform service

Platform service je prevádzkovaná technická služba, napríklad managed Kubernetes cluster, secret broker, artifact registry alebo CI runner fleet. Jej availability a security sú nevyhnutné, ale samy nehovoria, či používateľ dokáže službu nájsť, správne integrovať a použiť v reálnom delivery journey.

### Platform product

Platform product skladá services, interfaces, documentation, workflows, policy a support do používateľsky zrozumiteľnej capability. Má product ownerstvo, segmenty používateľov, roadmapu, service expectations, feedback loop, adoption stratégiu a lifecycle od introduction po retirement.

Vzťah možno zhrnúť takto:

```text
project
→ vytvorí alebo zmení časť platformy

service
→ prevádzkuje technickú capability

product
→ zabezpečuje, že súbor capabilities rieši opakovaný používateľský problém
   a zostáva použiteľný, bezpečný a udržateľný počas celého lifecycle-u
```

## 3. Exact platform-product subject

Platformový tím nemôže vyhodnotiť „úspešnosť platformy“ ako jeden agregovaný stav. Potrebuje exact product subject, ktorý viaže konkrétnu capability generation na konkrétny user segment, journey, environment a meraný outcome. Bez tejto identity sa do jednej metriky zmiešajú greenfield tímy, regulované workloads, legacy systémy aj experimentálne use cases s úplne odlišnými constraints.

Exact subject je zároveň hranicou pre roadmap decisions a incident analysis. Keď jedna capability funguje pre stateless web service, neznamená to, že rovnaký verdict platí pre stateful payment worker alebo multi-region regulated API.

Platform-product subject zahŕňa:

- **Product alebo capability identity a version** — určuje, ktorú contract generation používateľ hodnotí a oddeľuje nový release od starého správania.
- **User segment a ownership context** — identifikuje typ tímu, technickú zrelosť, business doménu a support model, pre ktoré má capability vytvárať hodnotu.
- **Job-to-be-done a journey boundary** — pomenúva outcome, napríklad „vytvoriť production-ready regulovaný service“, nie iba lokálnu action „vytvoriť repository“.
- **Entry interface a request channel** — odlišuje portal, API, CLI, Git change alebo IDE flow, pretože rovnaká capability môže mať rozdielnu friction podľa rozhrania.
- **Environment, tenancy a compliance scope** — určuje policy, identity, data, availability a audit constraints, ktoré menia reálnu náročnosť journey.
- **Required capability graph** — identifikuje repository, pipeline, runtime, identity, data, networking, observability, documentation a support outputs potrebné na usable outcome.
- **Adoption cohort a time window** — oddeľuje pilot, forced migration, mature users a nových používateľov a zabraňuje skresleniu pri organizačnej zmene.
- **Outcome, SLO a evidence definition** — určuje, čo znamená úspech, aké observation points ho dokazujú a aké forbidden outcomes ho invalidujú.
- **Product owner, service owners a escalation boundary** — priraďuje decision authority, runtime zodpovednosť a support path namiesto anonymného „platform team“.
- **Cost a capacity context** — umožňuje vyhodnotiť, či platforma vytvára hodnotu bez neudržateľného support toil-u alebo skrytého cloud spendu.

## 4. Používateľ nie je abstraktný developer

Interná platforma má viac skupín používateľov s odlišnými jobs, constraints a riskom. Aplikačný developer chce rýchly feedback a bezpečné defaults. Tech lead potrebuje architecture choices, ownership a migration path. SRE potrebuje pozorovateľnosť a recovery. Security alebo compliance potrebuje účinné controls a evidence. Product owner potrebuje predvídateľný lead time a business outcome.

Platformový tím preto nemá optimalizovať pre jednu personu vytvorenú podľa organizačného názvu. Segmentácia musí vychádzať z rozdielov, ktoré menia product contract. Relevantné segmenty môžu byť greenfield oproti brownfield tímom, stateless oproti stateful workloads, nízky oproti vysokému compliance profilu alebo centralizovaný oproti federovanému ownership modelu.

Používateľský výskum má kombinovať viac evidence sources:

- **Priame pozorovanie journey** — ukazuje, kde používateľ prepína nástroje, čaká, vytvára workaround alebo potrebuje nezdokumentovanú pomoc.
- **Interview a contextual inquiry** — vysvetľujú motiváciu, neistotu a lokálne constraints, ktoré telemetry sama neodhalí.
- **Support a incident evidence** — ukazujú opakovaný toil, nejasné ownership hranice a failure modes, ktoré platformový tím presunul na konzumentov.
- **Funnel a abandonment telemetry** — odlišujú objavenie capability, začatie requestu, dokončenie operation, prvé použitie a dlhodobú adopciu.
- **Repository a runtime inventories** — odhaľujú forks, bypass paths, stale generations a custom riešenia, ktoré signalizujú chýbajúci product fit.
- **Business a delivery outcomes** — prepájajú platform experience s lead time, reliability, compliance alebo nákladmi namiesto iba merania interakcie s portalom.

Výskum neznamená, že platformový tím implementuje každý individuálny request. Jeho úlohou je nájsť opakované problémy s dostatočným organizačným dopadom a navrhnúť capability, ktorá rieši spoločné jadro bez zničenia potrebnej flexibility.

## 5. Job-to-be-done a value hypothesis

Feature request „pridajte button na databázu“ nie je ešte product problem. Job-to-be-done opisuje situáciu, požadovaný pokrok a constraints: napríklad „application tím potrebuje bezpečne pripojiť production service k managed PostgreSQL bez čakania na tri manuálne handoffy a bez získania broad cloud credentials“.

Z jobu vzniká value hypothesis. Tá musí byť falsifikovateľná a viazaná na celý journey, nie iba na rýchlosť jedného platformového kroku.

```text
Pre regulované application tímy,
ktoré dnes čakajú na koordináciu repository, identity, database a GitOps zmien,
poskytne capability Regulated Service v4
production-ready service contract cez jeden durable request,
čím zníži median time-to-first-production-outcome z dní na hodiny
bez zvýšenia change-failure rate, security exceptions alebo support toil-u.
```

Hypothesis obsahuje target segment, current problem, proposed mechanism, expected outcome a guard conditions. Ak platforma zrýchli repository creation, ale zvýši počet manuálnych opráv alebo production incidentov, hypothesis neprešla.

## 6. Product outcome tree

Roadmap nemá byť iba zoznam technických komponentov. Product outcome tree prepája organizačný cieľ, používateľské outcomes, opportunity areas a experiments. Tým sa zabráni tomu, aby sa „nainštalovať Backstage plugin“ alebo „migrovať na nový orchestrator“ považovalo za hodnotu bez preukázaného používateľského efektu.

Príklad:

```text
business outcome
→ kratší a spoľahlivejší čas dodania regulovanej capability

user outcomes
→ tím vie nájsť podporovaný path
→ vie pochopiť contract a constraints
→ vie získať usable environment bez ticketu
→ vie bezpečne meniť a diagnostikovať service

opportunities
→ nejednotné onboarding požiadavky
→ skryté quota a network dependencies
→ nejasný operation status
→ chýbajúca upgrade cesta

experiments
→ journey prototype s troma pilotnými tímami
→ durable operation endpoint
→ preflight policy a quota check
→ managed template update channel
```

Outcome tree sa musí aktualizovať podľa evidence. Ak experiment ukáže, že hlavný delay je approval policy mimo platformy, ďalší portal widget problém nevyrieši.

## 7. Prioritizácia a roadmap authority

Platform roadmap je alokácia obmedzenej engineering a operational capacity. Potrebuje explicitnú decision policy, inak ju ovládne najhlasnejší stakeholder, najnovší incident alebo technická preferencia platformového tímu.

Rozhodnutie má posudzovať minimálne:

- **User reach a frequency** — koľko relevantných tímov problém zažíva a ako často blokuje ich journey.
- **Outcome impact** — aký delivery, reliability, security, cost alebo business efekt vznikne odstránením problému.
- **Confidence evidence** — či ide o opakovaný pozorovaný problém, alebo iba hypotézu jedného stakeholdera.
- **Implementation a lifecycle cost** — zahŕňa nielen build, ale aj availability, support, migration, upgrade a retirement.
- **Risk reduction alebo creation** — hodnotí controls, blast radius, lock-in a nové shared dependencies.
- **Strategic fit** — overuje, či capability podporuje definované platformové segmenty a operating model.
- **Opportunity cost** — ukazuje, ktoré iné outcomes sa neposunú, ak kapacita pôjde na danú iniciatívu.

Roadmap musí byť viditeľná a vysvetliteľná používateľom. Transparentnosť neznamená záväzok implementovať každý request; znamená, že tím vie, aký problém sa rieši, podľa akej evidence a čo sa považuje za úspech.

## 8. Capability contract ako produktový sľub

Capability contract spája používateľský interface s technickými a prevádzkovými guarantees. Má vysvetliť, čo používateľ poskytne, čo platforma vytvorí alebo zmení, aké constraints presadí, aké states môže operation nadobudnúť a kto vlastní výsledný resource.

Dobrý contract zahŕňa:

- **Input schema a eligibility** — definuje required identity, ownership, classification a environment context a odmietne request skôr, než vznikne partial state.
- **Outputs a authoritative locations** — uvádza repositories, catalog entities, cloud resources, GitOps declarations a credentials, ktoré vzniknú, vrátane ich stable identities.
- **Default a selectable decisions** — oddeľuje bezpečné platform defaults, používateľské choices a zakázané kombinácie.
- **SLO a operation semantics** — vysvetľuje accepted, planned, running, waiting, partial, failed, cancelled a succeeded stavy aj spôsob read-backu.
- **Security a compliance guarantees** — pomenúva presadené controls, evidence a residual risk, nie iba všeobecné tvrdenie „compliant by default“.
- **Ownership a support** — rozdeľuje application outcome, shared platform mechanism a underlying provider responsibility.
- **Change a compatibility policy** — určuje versioning, migration window, deprecation a spôsob, akým sa managed capability aktualizuje.
- **Cost a quota model** — ukazuje chargeback alebo allocation, capacity boundaries a správanie pri vyčerpaní quota.
- **Exit a escape contract** — vysvetľuje, ako používateľ capability opustí, exportuje state alebo zvolí exception bez hidden fork-u.

Product sľub je prijatý až vtedy, keď effective implementation zodpovedá contractu. Dokumentácia sľubujúca production-ready service pri workflowe, ktorý vytvorí iba repository a namespace, je false product interface.

## 9. Adoption nie je rollout mandate

Adoption znamená, že relevantní používatelia capability objavia, zvolia, úspešne použijú a zostanú na podporovanej ceste, pretože im prináša hodnotu. Povinné používanie môže zvýšiť počet requestov, ale skryť nízku dôveru, workaroundy a shadow platformy.

Adoption funnel má oddeľovať:

```text
target users
→ awareness
→ discovery
→ eligible users
→ request started
→ operation completed
→ first usable outcome
→ first production outcome
→ repeat use
→ retained managed generation
```

Každý prechod má vlastný dôvod drop-offu. Nízke discovery môže byť dokumentačný problém. Vysoký počet completed taskov a nízky usable outcome signalizuje false success semantics. Vysoký first-use a nízky retention môže znamenať upgrade, reliability alebo support problém.

Mandate má zmysel iba tam, kde ide o nevyhnutný control alebo organizačný standard, a aj vtedy musí platforma preukázať capability parity, migration path a bounded exceptions. Donútiť tímy na neúplnú platformu presúva riziko do forks a emergency bypassov.

## 10. Product discovery, delivery a operations

Platform as a Product neoddeľuje discovery od engineering reality. Product discovery skúma problém a testuje solution assumptions. Delivery vytvára versionovaný capability contract a implementation. Operations overuje, že shared service zostáva dostupná, bezpečná a podporovateľná. Všetky tri slučky sa musia prepájať.

```text
discovery evidence
→ product decision
→ delivery experiment alebo release
→ operational a adoption evidence
→ updated discovery
```

Platformový tím, ktorý robí discovery bez runtime evidence, môže optimalizovať preferencie deklarované v interview a prehliadnuť skutočný abandonment. Tím, ktorý robí iba delivery, sa stáva feature factory. Tím, ktorý robí iba operations, stabilizuje current service bez overenia, či ešte rieši dôležitý problém.

## 11. Funding, capacity a cost model

Interná platforma spotrebúva engineering, cloud, security a support capacity. Product model vyžaduje, aby náklady boli viditeľné a prepájané s hodnotou. Bez toho môže centralizácia vyzerať lacno iba preto, že toil application tímov, migration alebo incident cost nie sú započítané.

Cost model má rozlišovať:

- **Fixed platform cost** — control plane, shared services, core team a baseline support existujú aj pri nízkej spotrebe.
- **Marginal capability cost** — nový environment, database, build minute alebo telemetry volume rastie podľa adopcie.
- **Consumer integration cost** — čas tímu na onboarding, migration, exceptions a lokálne changes je súčasťou total cost.
- **Operational externality** — shared dependency incident alebo zlá default policy môže vytvoriť náklad naprieč mnohými tímami.
- **Avoided duplication a risk** — zdieľaná capability môže znížiť opakovaný build, audit effort a incident probability, ale tento benefit treba preukázať.

Chargeback alebo showback môže pomôcť, no nesmie sa stať jedinou value metrikou. Lacná capability, ktorú tímy obchádzajú alebo ktorá spomaľuje critical delivery, nie je úspešný produkt.

## 12. Ownership a operating model

Product ownerstvo neznamená, že jedna osoba rozhoduje o všetkých technických detailoch. Znamená, že existuje accountable authority za používateľský problém, capability contract, roadmap a outcome. Service owners zároveň nesú runtime reliability a security jednotlivých components.

Operating model má pomenovať:

```text
platform product owner
→ user outcomes, roadmap a adoption

capability/service owners
→ technical contract, reliability a lifecycle

application teams
→ service business outcome a správne použitie contractu

security/compliance
→ policy intent, assurance a exception authority

underlying providers
→ provider service contract a failure boundary
```

Nejasný model vedie k ping-pongu: portal team tvrdí, že task prešiel, cloud team vidí provider failure a application team zostáva bez usable capability. Product operation potrebuje end-to-end escalation a incident ownership aj pri cross-team dependencies.

## 13. Meranie platformového produktu

Jedna metrika nemôže reprezentovať celý product system. Potrebná je vyvážená evidence, ktorá oddeľuje demand, usability, delivery, reliability, trust, cost a business effect. Metriky musia byť segmentované podľa capability generation a user cohortu.

### Demand a adoption

Sleduje sa počet eligible tímov, discovery, request starts, first-use, repeat use, retention, forks, bypasses a deprecation compliance. Vysoký demand môže byť výsledkom mandate, preto sa musí korelovať s voluntary reuse a support behaviorom.

### Journey a developer outcome

Meria sa time-to-first-usable a time-to-first-production outcome, waiting time, handoffs, retries, abandonment a manual interventions. Portal task duration je iba jedna podfáza.

### Reliability a operability

Sleduje sa availability platform API, operation success podľa end-to-end contractu, partial/unknown outcomes, recovery time, stale resources a shared dependency incidents. Green frontend uptime neznamená funkčnú platformu.

### Quality a safety

Meria sa policy effectiveness, exception rate, security findings, change failure, rollback alebo repair, version compliance a forbidden outcomes. Nulový počet exceptions môže znamenať aj skrytý bypass.

### Satisfaction, cognitive load a trust

Používateľské survey a interviews zisťujú, či tímy rozumejú platforme, vedia predvídať výsledok, dôverujú statusu a dokážu diagnostikovať failure. Tieto percepčné signály nemožno spoľahlivo odvodiť iba z clickstreamu.

### Business a organizational impact

Platforma sa prepája s lead time, reliability, audit effort, time spent on new capability, cost efficiency a schopnosťou onboardovať ďalšie tímy. Korelácia však nie je automaticky kauzalita; zmena musí mať baseline, matched cohort alebo experimentálny design.

## 14. Feedback closure a product experiments

Feedback nie je backlog položka bez odpovede. Closure znamená, že platformový tím signál klasifikuje, spojí s journey a capability generation, rozhodne o action alebo non-action, komunikuje dôvod a neskôr overí výsledok.

Bezpečný experiment má:

```text
explicit hypothesis
→ target cohort
→ current baseline
→ bounded platform change
→ expected positive a forbidden outcomes
→ instrumentation a qualitative feedback
→ decision threshold
→ rollback alebo continuation
→ learning record
```

Príkladom je pilot pre tri regulované tímy, nie okamžité zapnutie nového golden pathu pre celú organizáciu. Experiment má overiť nielen completion rate, ale aj first production outcome, support potrebu, security exceptions a schopnosť vykonať druhú zmenu.

## 15. Lifecycle: introduce, grow, maintain a retire

Platform capability má lifecycle podobne ako externý produkt. Introduction potrebuje beta contract, support a bounded cohort. Growth potrebuje capacity, migration tooling a stabilné interfaces. Maintenance potrebuje compatibility, security a cost decisions. Retirement potrebuje consumer inventory, replacement a verifikované odstránenie.

Retirement flow:

```text
retirement intent a owner
→ exact affected consumer inventory
→ supported replacement a parity assessment
→ migration tooling a cohort plan
→ deadline, exceptions a escalation
→ usage a runtime verification
→ old write path disabled
→ old resources/data safely removed
→ residual consumers a business outcome verified
```

Oznámenie v chate nie je deprecation contract. Ak platforma nevie identifikovať consumers alebo poskytnúť migration path, retirement vytvára shadow dependencies a emergency extensions.

## 16. Connected incident `GITOPS-PAY-63`

Atlas po technickom redizajne z `GITOPS-PAY-62` spustil platform product `Regulated Service v4`. Executive cieľ znel: každý nový payment service má byť production-ready do 60 minút bez infraštruktúrneho ticketu. LaunchPad portal kombinoval Backstage template, Git repositories, reusable pipeline, Flux bootstrap, database request, workload identity, dashboards a catalog registration.

Platformový tím definoval success ako úspešné dokončenie portal tasku. User research prebehol iba s dvoma greenfield tímami; regulované stateful workloads, private provider connectivity a incident-recovery journeys neboli v discovery scope. Adoption bol po štyroch týždňoch vyhlásený za povinný.

Observed product evidence počas prvých šiestich týždňov:

```text
platform requests:                       64
portal tasks marked Succeeded:           61  (95%)
requests with first usable environment:  39  (61%)
first production business outcome:       27  (42%)
requests requiring manual ticket:        28  (44%)
template forks alebo detached copies:    19  (30%)
manual platform bypasses:                 8  (13%)
median portal task duration:              9 min
median time-to-first-production:          3.8 dňa
```

Critical request `LP-8841` mal vytvoriť `settlement-repair-api`, ktorý bol potrebný na automatizované riešenie provider-ledger rozdielov. Portal za 7 minút vytvoril repository, catalog entity a environment pull request a označil operation ako `Succeeded`. Database private endpoint však čakal na regionálnu quota, workload identity neobsahovala provider reconciliation permission a generated runbook nepopisoval unknown provider outcome.

Tím zistil neúplný capability graph až pri prvom end-to-end teste. Nasledovali tri manuálne tickety, emergency IAM exception a fork generated pipeline. Service dosiahol prvý production reconciliation po 19 hodinách. Počas delayu zostalo `8 412` settlements v manual reconciliation queue a `73` prekročilo interný 24-hodinový resolution objective.

### Platform-as-a-Product root cause

Product authority optimalizovala output „portal task succeeded“, nie job „tím bezpečne prevádzkuje regulovaný service“. Roadmap vznikla z executive deadline-u a technického component planu bez segment-specific discovery, value hypothesis a end-to-end acceptance. Mandate zvýšil request count, ale zakryl nízky usable-outcome rate a rastúci support toil.

### Amplifiers

Golden path bol kopírovaný snapshot bez managed upgrade contractu, self-service operation sa uzavrela pred downstream readiness a developer-experience dashboard neobsahoval waiting, manual intervention, trust ani time-to-business-outcome. Chýbajúci consumer a version inventory zároveň skomplikoval opravu už vytvorených services.

### Product redesign

Redesign začína zmenou product subjectu a success oracle-u:

```text
regulated-service user segment + settlement-repair job
→ observed journey a baseline
→ capability contract RSP-4.1
→ pilot cohort troch tímov
→ durable request cez repository, identity, network, database, GitOps a observability
→ first usable environment verification
→ first production settlement-reconciliation canary
→ second change a incident drill
→ adoption, support, trust a business evidence
→ staged expansion alebo ďalšia product iteration
```

Platform roadmap teraz prioritizuje private connectivity pre regulovaný segment, preflight quota, exact operation states, managed golden-path updates a developer-visible diagnostics. Povinná migrácia je pozastavená, kým capability neprejde parity a second-cohort gate-om.

## 17. Platform-as-a-Product acceptance verdict

Acceptance verdict je product-level rozhodnutie, nie technický release status. Musí preukázať, že platforma pozná používateľský problém, poskytuje explicitný contract, dosahuje target outcome a dokáže sa bezpečne vyvíjať bez rastúceho skrytého toil-u.

Platform as a Product design je prijatý, keď:

- **User segments a jobs sú explicitné** — roadmapa vie, komu capability slúži, aký pokrok umožňuje a ktoré constraints menia contract.
- **Value hypothesis je falsifikovateľná** — expected outcome, baseline, guard metrics a decision threshold sú definované pred rolloutom.
- **Capability contract je úplný** — inputs, outputs, states, SLO, ownership, security, cost, compatibility a exit semantics sú zrozumiteľné.
- **Roadmap používa evidence a transparentnú prioritizáciu** — decisions nie sú iba reakciou na executive mandate, tool preference alebo najhlasnejší request.
- **Adoption je meraná ako usable a retained outcome** — request count, clicks alebo forced migration sa nezamieňajú s dôverou a hodnotou.
- **Journey telemetry pokrýva end-to-end tok** — waiting, handoffs, partial states, manual intervention, first production outcome a repeat use sú pozorovateľné.
- **Qualitative feedback má closure** — interview, support a survey signály sú korelované s capability generation a vedú k rozhodnutiu alebo vysvetlenému non-action.
- **Reliability, security a cost sú product qualities** — nie sú presunuté na underlying service owners bez spoločného acceptance verdictu.
- **Funding a capacity sú udržateľné** — platforma pozná fixed, marginal, integration a support cost a vie obhájiť investíciu business outcome-om.
- **Lifecycle je spravovaný** — introduction, upgrade, migration, deprecation a retirement majú consumer inventory a recovery path.
- **Mandate má parity a exception contract** — required adoption nevynucuje neúplnú capability ani nevytvára nekontrolované forks.
- **Second-cohort a second-change tests prejdú** — product funguje mimo pôvodného pilotu a po upgrade, failure alebo ownership zmene.

## 18. Troubleshooting flow

Platform product troubleshooting začína používateľským outcome-om a postupne zužuje, či zlyhala discovery, contract, implementation, adoption alebo measurement. Kontrola portal statusu je iba jeden observation point.

```text
Platforma má nízku dôveru, adopciu alebo neprináša očakávaný outcome
→ exact capability generation, segment, cohort a journey
→ baseline a value hypothesis
→ awareness/discovery/eligibility funnel
→ request a durable operation states
→ capability outputs a effective readiness
→ first-use, first-production a repeat-use evidence
→ support, forks, bypasses a qualitative feedback
→ reliability, security, cost a business outcomes
→ competing product a technical hypotheses
→ bounded experiment alebo authoritative remediation
→ second-cohort a second-change verification
```

Ak je request completion vysoký, ale first-production nízky, hypotéza „používatelia nerozumejú portalu“ musí súperiť s hypotézami partial orchestration, chýbajúci capability contract, external waiting alebo false status. Diskriminačný dôkaz pochádza z per-step operation timeline-u a journey observation, nie z agregovaného CSAT.

## 19. Anti-patterny

### Platformu musia používať všetci, inak sa investícia nevráti

Mandate môže byť potrebný pre kritické controls, ale bez capability parity a migration evidence vytvorí forks, exceptions a shadow platformy. Produktová hodnota sa má dokazovať outcome-om a retained adoption, nie iba compliance s príkazom.

### Interní developeri nie sú zákazníci, nemusia byť spokojní

Interný používateľ má stále alternatívy: manuálny ticket, fork, bypass, vlastný tool alebo spomalenie delivery. Ignorovanie experience neodstráni tieto voľby, iba ich presunie mimo visibility platformového tímu.

### Roadmapu určuje architecture board

Architecture a security constraints sú vstupy, nie úplný product decision. Roadmap musí prepájať organizačný intent s pozorovaným user problemom, costom, riskom a overiteľným outcome-om.

### Veľa requests znamená product-market fit

Requests môžu byť povinné alebo automaticky generované. Product fit vyžaduje usable outcome, repeat use, nízky neplánovaný support a dôveru v capability.

### Platform team vlastní všetko za portalom

Platform team vlastní shared contract a mechanisms, application team svoj business service a underlying providers svoje boundaries. Produktový model potrebuje explicitnú kompozíciu zodpovedností, nie nekonečné centralizovanie.

## 20. Kontrolné otázky

1. Čím sa platform product líši od platform projectu a prevádzkovanej platform service?
2. Prečo musí exact platform-product subject obsahovať user segment, journey a capability generation?
3. Ako sa job-to-be-done mení na falsifikovateľnú value hypothesis?
4. Prečo portal task completion nie je dostatočná platform product metrika?
5. Ako adoption funnel odlíši discovery, usable outcome a retained use?
6. Kedy môže byť povinná adopcia oprávnená a aké gates musí mať?
7. Ako product discovery, delivery a operations vytvárajú jednu feedback slučku?
8. Ktoré náklady musí platform product zahrnúť okrem cloud spendu?
9. Prečo `GITOPS-PAY-63` vykazoval 95 % success, ale iba 42 % first-production outcome?
10. Aký experiment by odlíšil chýbajúci product fit od slabého onboarding rozhrania?
11. Ako sa má platform capability bezpečne deprecate-nuť a odstrániť?
12. Čo musí obsahovať platform-as-a-product acceptance verdict?

## Glossary impact

Relevantné pojmy: platform product subject, internal user segment, platform job-to-be-done, platform value hypothesis, product outcome tree, capability contract, platform adoption funnel, first usable outcome, first production outcome, retained managed adoption, platform product owner, product feedback closure, platform product experiment, capability parity gate, platform product acceptance verdict.

## Primárne zdroje

- [CNCF TAG App Delivery — Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/)
- [CNCF TAG App Delivery — Platform Engineering Maturity Model](https://tag-app-delivery.cncf.io/wgs/platforms/maturity-model/readme/)
- [CNCF Contributors — Platform Engineering Technical Community Group](https://contribute.cncf.io/community/tcgs/platform-engineering/)
- [Backstage — What is Backstage?](https://backstage.io/docs/overview/what-is-backstage/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Internal Developer Platform](internal-developer-platform.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Golden paths a paved road →](golden-paths-and-paved-road.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
