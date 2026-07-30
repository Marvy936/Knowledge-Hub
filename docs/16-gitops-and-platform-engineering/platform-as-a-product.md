# Platform as a Product

Platform as a Product je operating model, v ktorom interná platforma nie je hodnotená podľa počtu nástrojov, templates, portal clicks alebo uzavretých ticketov. Je to dlhodobo spravovaný produkt pre konkrétne interné user segments. Musí riešiť opakovaný job-to-be-done, poskytovať zrozumiteľný capability contract, vytvárať merateľný usable outcome a vyvíjať sa podľa evidence, nie podľa povinnej adopcie alebo technickej roadmapy platformového tímu.

```text
observed user segment a job
→ falsifikovateľná value hypothesis
→ versioned capability contract
→ prioritized product investment
→ discoverable onboarding a adoption
→ usable technical, operational a business outcome
→ support, reliability, cost a trust evidence
→ improve, expand, maintain, migrate alebo retire
→ second cohort a second journey
```

Release platformového komponentu je iba zmena ponuky. Product success vzniká až vtedy, keď relevantný tím dokáže capability nájsť, pochopiť, použiť, meniť a prevádzkovať bez neprimeraného toil-u alebo skrytých manuálnych handoffov.

## 1. Project, service a product

Platform project je časovo ohraničená iniciatíva, napríklad zavedenie GitOps alebo developer portalu. Môže dodať plánované outputs a napriek tomu nevytvoriť udržateľnú hodnotu. Platform service je technicky prevádzkovaná capability, napríklad runner fleet, Kubernetes cluster alebo secret broker. Jej availability a security sú potrebné, no nehovoria, či ju application tím vie bezpečne integrovať a používať.

Platform product skladá services, APIs, workflows, documentation, policy, support a lifecycle do jedného používateľsky zrozumiteľného contractu. Má product ownerstvo, target segments, roadmapu, service expectations, feedback loop a retirement plan.

```text
project
→ vytvorí alebo zmení časť platformy

service
→ prevádzkuje technical mechanismus

product
→ zabezpečuje opakovaný user outcome počas celého lifecycle-u
```

Tool alebo portal sa preto nestáva produktom len tým, že je centralizovaný a povinný.

## 2. Exact platform-product subject

Tvrdenie `platforma je úspešná` je príliš široké. Exact subject musí identifikovať capability a jej version, user segment, job a journey boundary, environment a compliance context, entry interface, required capability graph, adoption cohort a časové okno, outcome/SLO definition, product a service owners, support model, cost a capacity context.

Rovnaká capability môže fungovať pre stateless greenfield API a zlyhať pre regulated stateful worker. Priemer naprieč oboma skupinami zakryje, že jedna z nich potrebuje private networking, database capacity, provider-reconciliation permission a 24-hodinový operational objective.

Product verdict sa preto viaže na konkrétnu kombináciu:

```text
capability Regulated Service 4.1
+ regulated payment teams
+ create first production-ready service
+ production EU tenant
+ six-week cohort
+ usable environment a first business canary
```

## 3. User segment a job-to-be-done

Používateľ nie je abstraktný `developer`. Application developer potrebuje rýchly feedback a bezpečné defaults. Tech lead potrebuje architecture a lifecycle choices. SRE potrebuje recovery a version-aware telemetry. Security potrebuje účinné controls a evidence. Segmentácia má vychádzať z differences, ktoré menia product contract: greenfield/brownfield, stateless/stateful, nízky/vysoký compliance profil, novice/mature platform user alebo central/federated ownership.

Job-to-be-done opisuje situáciu, desired progress a constraints. Feature request `pridajte button na databázu` nie je úplný job. Lepší subject je: `regulated application tím potrebuje dostať nový service do production s repository, workload identity, private network, managed database, GitOps a observability bez troch neštruktúrovaných ticketov a bez broad cloud credentials`.

Evidence pre problem discovery má kombinovať journey observation, interviews, support a incident records, funnel/abandonment telemetry, runtime/repository inventory a delivery/business outcomes. Najhlasnejší stakeholder ani generický survey nie sú dostatočný product oracle.

## 4. Value hypothesis a guard conditions

Value hypothesis musí byť falsifikovateľná. Pomenúva segment, current problem, proposed mechanism, expected improvement a outcomes, ktoré sa nesmú zhoršiť.

```text
Pre regulated service teams
Regulated Service 4.1 poskytne jeden durable capability request,
ktorý zníži time-to-first-production z dní na hodiny,
bez zvýšenia change-failure rate, security exceptions,
manual support toil-u alebo orphan resources.
```

Zrýchlenie repository creation o desať minút hypotézu nepotvrdí, ak database ostane blocked, network sa rieši ticketom a prvý production deploy príde o tri dni neskôr. Guard metrics chránia pred lokálnou optimalizáciou: reliability, security, support load, cost, abandonment, bypasses a lifecycle debt.

## 5. Capability contract a product lifecycle

Capability contract uvádza supported jobs, eligibility, inputs, outputs, guarantees, constraints, expected timing, cost, ownership, support, observability, upgrade a decommission semantics. Contract version nie je marketingový label. Určuje schema requestu, dependency graph, managed components a migration policy pre existing consumers.

Platform product nekončí create flowom:

```text
introduce a pilotovať
→ onboardovať a adoptovať
→ používať a meniť
→ podporovať a recoverovať
→ upgrade-nuť alebo migrovať
→ transferovať ownership
→ deprecate a retire
```

Existing consumer inventory musí vedieť, kto používa ktorú generation. Bez managed upgrade channelu sa template outputs odpoja, security fixes sa šíria ručne a platforma nevie odlíšiť supported, deprecated a detached consumers.

## 6. Roadmap ako outcome decision

Roadmap nemá byť zoznam `install Backstage`, `upgrade Kubernetes` alebo `add plugin`. Technické investments sú mechanisms. Prioritizácia má vychádzať z user reach, frequency, outcome impact, confidence evidence, lifecycle cost, risk reduction/creation, support toil a strategic necessity.

Outcome tree prepája business outcome, user outcomes, opportunities a experiments:

```text
kratšie a spoľahlivejšie dodanie regulated capability
→ nájsť supported path
→ získať usable environment bez hidden ticketu
→ bezpečne vykonať druhú zmenu a incident recovery
→ odstrániť capacity preflight gap
→ pridať durable operation a managed upgrade channel
```

Ak hlavný delay spôsobuje private-network approval alebo database capacity, ďalší portal widget nie je správna investícia.

## 7. Adoption, choice a trust

Adoption nie je počet registrovaných users ani mandate coverage. Silný signál je opakované použitie capability, úspešná druhá zmena, nízky abandonment, menší support burden a ochota tímov zostať na managed path. Povinné používanie môže vytvoriť vysoké request counts a zároveň forks, bypasses a shadow automation.

Platform môže presadzovať safety guardrails, no product value sa stále meria. Tímy môžu byť povinné používať signed artifacts a workload identity, ale preferovaná cesta má byť jednoduchšia než compliant custom implementation. Exceptions a escape paths majú explicitný owner, responsibilities, expiry a návratový alebo detach contract.

Dôvera vzniká z truthful statusu, predictable outcomes, actionable failures, stable interfaces a dobre zvládnutých incidentov. Portal, ktorý hlási `Succeeded` pred usable outcome-om, poškodzuje trust viac než pomalší, ale pravdivý workflow.

## 8. Measurement bez output a survivorship biasu

Product measurement potrebuje funnel od eligible demandu po retained outcome:

```text
eligible request
→ started
→ accepted
→ technically provisioned
→ first usable environment
→ first production outcome
→ second change
→ retained managed adoption
```

Do denominatora patria failures, waiting, abandonment, manual intervention a bypass. Survey iba users, ktorým task prešiel, vytvára survivorship bias. Portal task duration má zmysel iba ako component metric; nemá nahradiť time-to-first-usable alebo time-to-first-production.

Quantitative evidence sa dopĺňa kvalitatívnym výskumom. Delivery metrics, support toil a business outcome chránia pred tým, aby spokojnosť s UI zakryla slabú reliability. Qualitative feedback zase vysvetlí, prečo ľudia forkli template alebo otvorili tri tickety, čo aggregate telemetry sama nevie.

## 9. Connected incident `GITOPS-PAY-63`

Atlas zaviedol povinný `Regulated Service v4` cez LaunchPad a Backstage. Executive promise bol `production-ready service do 60 minút bez ticketu`; platform tím však definoval success ako terminal scaffolder task.

Skutočný path používal template tag `regulated-service-v4`, custom actions image `latest`, Terraform module `main`, copied pipeline fragments, manuálny private-network ticket a žiadny managed upgrade channel. Portal označoval success po repository alebo PR outputs a survey oslovoval iba successful task cohort.

Za šesť týždňov vzniklo `64` requests. `61` portal tasks bolo `Succeeded` (`95 %`), ale iba `39` requests dosiahlo first usable environment (`61 %`) a iba `27` first production business outcome (`42 %`). `28` requests potrebovalo manuálny ticket (`44 %`), `19` vytvorilo fork alebo detached copy (`30 %`) a `8` platformu obišlo (`13 %`). Median portal task bol `9 minút`, no median time-to-first-production bol `3.8 dňa`.

Request `LP-8841` pre `settlement-repair-api` bol zelený po `7 minútach`. Database ostala `WaitingCapacity`, private endpoint nebol súčasťou pathu a workload identity nemala provider-reconciliation permission. Retry vytvoril druhý environment PR, tím otvoril tri tickety a fork-ol pipeline. Prvá production reconciliation prišla po `19 hodinách`; `8 412` settlements ostalo v manual queue a `73` prekročilo interný 24-hodinový resolution objective.

Root cause bola output-driven product definition a forced adoption bez capability parity. Platform optimalizovala lokálny scaffolder completion, nie segment-specific job, usable outcome, support toil a business effect.

## 10. Authoritative redesign a acceptance paths

Redesign definuje `Regulated Service 4.1` pre exact segment a journey. Capability contract zahŕňa repository, identity, private network, database capacity, GitOps, observability, first production canary, second change a incident drill. Mutable actions a modules sú pinned; consumer-version inventory a managed upgrade channel odlišujú supported a detached state.

Positive path overí first usable environment, business canary a second change. Waiting path ukáže capacity blocker, ownera a SLO bez false successu. Recovery path resume-ne durable operation po dependency alebo controller failure. Product path meria complete cohort vrátane abandonmentu, tickets a forks. Forbidden path odmietne mandatory rollout bez capability parity, task-output success, successful-only survey, mutable unversioned dependencies a roadmap riadenú iba tool outputs.

## 11. Troubleshooting a anti-patterny

Pri slabej adopcii alebo false successu sa mapuje exact segment/job, capability generation, funnel denominator, expected output graph, operation states, manual handoffs, support timeline, first usable/production outcome, second-change success, forks/bypasses a business impact. Potom sa formuluje causal hypothesis a bounded experiment, nie ďalší všeobecný feature request.

Anti-patterny sú: `platforma je povinná, takže product fit netreba`, `portal clicks = adoption`, `61/64 tasks passed = platform success`, `survey successful users = DevEx`, `template release = lifecycle complete` a `roadmapa je zoznam technických komponentov`.

## Glossary impact

Relevantné pojmy: platform product subject, user segment, job-to-be-done, value hypothesis, capability contract, outcome roadmap, adoption funnel, retained managed adoption, mandatory-adoption bias, usable platform outcome, platform product lifecycle a Platform-as-a-Product acceptance verdict.

## Primárne zdroje

- [CNCF Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/)
- [CNCF Platform Engineering Maturity Model](https://tag-app-delivery.cncf.io/whitepapers/platform-eng-maturity-model/)
- [DORA — Platform engineering capability](https://dora.dev/capabilities/platform-engineering/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Internal Developer Platform](internal-developer-platform.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Golden paths a paved road →](golden-paths-and-paved-road.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
