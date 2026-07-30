# Developer experience

Developer experience (DevEx alebo DX) je to, ako developeri vnímajú a vykonávajú celý systém práce potrebný na dodanie a prevádzku software. Zahŕňa tools, platform capabilities, processes, documentation, feedback, ownership, collaboration, interruptions, cognitive load, dôveru a recovery. Nie je to iba spokojnosť s portalom ani synonymum pre pipeline latency.

DevEx je systémová vlastnosť. Lokálne rýchly scaffolder môže zhoršiť celý journey, ak vytvorí hidden waiting, duplicate retries a operational toil. Potrebný guardrail môže pridať krok a zároveň zlepšiť experience tým, že je predictable, actionable a zabráni neskorému incidentu.

```text
user segment a developer goal
→ exact end-to-end journey a context
→ decisions, handoffs, waits a feedback loops
→ lived friction a cognitive load
→ complete quantitative a qualitative evidence
→ falsifikovateľná causal hypothesis
→ bounded intervention
→ changed behavior, trust a outcome
→ delivery, quality, operational a business validation
→ second cohort a second change
```

## 1. Experience, productivity, activity a satisfaction

Experience opisuje friction, clarity, confidence, flow a feedback. Productivity opisuje, ako team alebo system premieňa effort na hodnotný outcome pri quality a risk constraints. Satisfaction je percepčný signál. Activity sú actions ako commits, builds alebo portal tasks.

```text
activity
≠ output
≠ outcome
≠ productivity
≠ good experience
```

Viac commits môže znamenať flow alebo rework. Kratší task time môže znamenať lepšiu platformu alebo predčasne ukončený oracle. Preto sa DevEx nemeria jedným číslom. SPACE framework zdôrazňuje viac dimenzií vrátane satisfaction, performance, activity, communication/collaboration a efficiency/flow; practical platform measurement ich kombinuje s delivery, reliability a business evidence.

## 2. Exact DevEx subject

Tvrdenie `DevEx sa zlepšil` potrebuje cohort, goal/journey, platform a toolchain generation, service/environment context, time window, expected outcome a guard constraints, measurement instruments, interruptions/dependencies, support context a privacy purpose.

Novice greenfield team môže mať inú experience než senior regulated brownfield team. Priemer môže byť zelený, kým kritický segment čaká na private-network ticket. Platform rollout cohort musí byť oddelený od previous generation. Incident window, seasonality a forced migration môžu meniť activity aj perceptions.

Measurement purpose má byť explicitný. DevEx telemetry a surveys slúžia na zlepšovanie systemu, nie na individuálne performance ranking. Ak developeri očakávajú punitive use, odpovede aj behavior sa skreslia a dôvera k platforme klesne.

## 3. Journey a momenty pravdy

DevEx sa mapuje podľa používateľského goal-u, nie podľa tool ownerov. Journey `vytvoriť prvý regulated service a spraviť production change` prechádza discovery, accessom, repository, local feedback, review, CI, platform requestom, environmentom, promotion, runtime verification a supportom.

```text
understand supported path
→ request capability
→ receive preflight a plan
→ wait alebo repair blockers
→ get usable environment
→ build, promote a deploy
→ verify business outcome
→ perform second change
→ diagnose first failure alebo incident
```

Momenty pravdy majú disproporčný vplyv na trust: onboarding, prvá chyba, first production, first upgrade a first incident. Happy-path task môže byť rýchly, no generic failure bez operation ID a ownera naučí tím obchádzať platformu.

Journey map obsahuje actions, decisions, tools, waits, interruptions, handoffs, evidence, ownera a emotional/confidence signals. Má vzniknúť kombináciou observation, operation timelines a interviews, nie iba z process diagramu platformového tímu.

## 4. Feedback loops, cognitive load a flow

Feedback loop sa hodnotí podľa latency, relevance, trustworthiness a actionability. Dvojminútový generic `failed` môže byť horší než päťminútový result s exact subjectom, evidence a local remediation. Total feedback time zahŕňa preparation, queue, execution, publication a time-to-understand.

Cognitive load sa delí na intrinsic complexity problému a extraneous complexity spôsobenú nekonzistentnými interfaces, hidden dependencies, policy jargon a tribal knowledge. Platforma má odstrániť opakované incidental decisions, no zachovať kontext potrebný pre data, security a recovery trade-offs. Nový portal alebo DSL je oprávnený iba vtedy, ak odstráni viac concepts a handoffs, než pridá.

Flow je schopnosť udržať sústredenú prácu s jasným cieľom a včasným feedbackom. CI queues, flaky tests, approval waits, meeting load a context switching ho narúšajú. Keď developer počas čakania otvorí tri ďalšie tasks, rastie work-in-progress, rework a time-to-completion aj pri relatívne krátkej jednotlivnej latency.

## 5. Friction taxonomy a valuable friction

Friction je odpor medzi intentom a outcome-om. Waiting friction vzniká pri queues, approvals, capacity a supporte. Interaction friction pri redundantnom zadávaní, copy/paste a tool switching. Decision friction pri nejasných defaults a consequences. Feedback friction pri pomalom, flaky alebo nekorelovanom result-e. Access/dependency friction pri identity, network, data a quota blockers. Operational friction pri upgrade, recovery a decommission. Organizational friction pri ownership gaps a approval theater.

Nie všetka friction je škodlivá. Review, policy alebo destructive confirmation môžu chrániť high-value invariant. Valuable friction je risk-proportionate, predictable, vysvetlená a vedie k rozhodnutiu. Waste friction je redundantná, neactionable, hidden alebo nevytvára relevantný risk reduction.

Optimalizovať počet klikov bez rozlíšenia týchto classes môže odstrániť safety context a zhoršiť outcome.

## 6. Instrumentovaný end-to-end timeline

Platform DevEx potrebuje common operation a journey identities, ktoré spájajú portal, Git, cloud, CI, GitOps, support a runtime evidence. Bez nich každý tool ukáže lokálnu latency a nikto nevie vysvetliť 3.8-dňový time-to-production.

```text
request started
→ accepted
→ waiting capacity
→ repository/PR
→ environment usable
→ first deploy
→ production canary
→ second change
```

Pre každú transition sa meria active processing, queue/wait, retries, manual intervention, owner a outcome. P50 bez tails nestačí; regulated outliers môžu mať business impact. Success denominator zahŕňa všetky eligible/started requests, nie iba terminal successful tasks.

Bot activity a generated commits sa nemajú miešať s human delivery activity bez classification. Automatizácia môže zvýšiť commit/deploy count bez zlepšenia user outcome-u. Rovnako portal cache a local task state nesmú byť považované za authoritative runtime evidence.

## 7. Quantitative a qualitative evidence

Quantitative measures môžu zahŕňať discover-to-start conversion, preflight rejection quality, task/queue/wait times, time-to-first-usable environment, time-to-first-production, failure/partial/unknown rate, manual ticket rate, retry/duplicate rate, second-change success, upgrade success, abandonment, forks/bypasses, support toil a delivery/reliability outcomes.

Qualitative evidence vysvetľuje perceptions a causes: clarity, confidence, cognitive load, trust in status, quality of error messages, ownership understanding a perceived productivity. Survey sa viaže na exact journey a cohort a dopĺňa interviews alebo contextual observation.

Survivorship bias vzniká, keď survey dostanú iba users po successful tasku. Failure, waiting a abandonment cohort musí byť zahrnutý samostatným kontaktom a privacy-safe designom. Generic satisfaction score bez journey identity nevie povedať, čo zmeniť.

## 8. Causal hypothesis a experiment

Dashboard correlation nie je príčina. Pred intervention sa formuluje hypotéza:

```text
Regulated teams čakajú na first production,
pretože private-network a database-capacity blockers
nie sú v preflight-e ani operation timeline-e,
čo vytvára manual tickets, retries a platform forks.
```

Experiment môže pridať capacity reservation, private-network capability a truthful waiting state pre pilot cohort. Success sa hodnotí time-to-usable, ticket/bypass rate, support toil, security/reliability guards a qualitative trust. Portal redesign bez zmeny underlying dependency flow hypotézu netestuje.

Rollout potrebuje baseline, comparable cohort, time window, confounder inventory a stop conditions. Improvement v median-e pri zhoršení failure tailu alebo incident rate nie je acceptance.

## 9. Connected incident `GITOPS-PAY-63`

Atlas dashboard vykazoval `61/64` successful portal tasks (`95 %`) a median task duration `9 minút`. Executive report preto tvrdil, že platforma spĺňa promise `production-ready service do 60 minút bez ticketu`.

Complete cohort však ukázal iba `39/64` first usable environments (`61 %`) a `27/64` first production business outcomes (`42 %`). `28` requests vyžadovalo ticket (`44 %`), `19` vytvorilo fork/detached copy (`30 %`) a `8` platformu obišlo (`13 %`). Median time-to-first-production bol `3.8 dňa`.

Dashboard vylučoval waiting, failed, abandoned a manual-intervention paths. Survey sa posielal iba successful task cohortu. Delivery activity obsahovala bot-generated commits a PRs. Support tickets neboli korelované s operation timeline. Výsledok bol selection a survivorship bias: rýchlosť lokálneho UI tasku sa vydávala za experience celého journey.

`LP-8841` bol portalom green po `7 minútach`, no tím čakal `19 hodín` na first production reconciliation, otvoril tri tickety a fork-ol pipeline. `8 412` settlements ostalo v manual queue a `73` prekročilo 24-hodinový objective. Generic survey po green tasku tento operational a business cost nezachytil.

## 10. Authoritative redesign a acceptance paths

DevEx model pre `Regulated Service 4.1` sleduje všetkých `64` eligible/started requests cez task, waiting, usable environment, production outcome, second change a retained adoption. Operation ID spája portal, tickets, PRs, Flux a business canary. Dashboard oddeľuje human a bot activity a publikuje median aj tails.

Quantitative funnel sa dopĺňa journey-specific surveyom pre successful, waiting, failed a abandoned cohorts a interviews s teams, ktoré forkli alebo bypassli path. Improvement hypothesis sa testuje po pridaní complete preflight-u, private network capability, durable waiting state a managed upgrade channel.

Positive path zlepší usable a production outcomes bez zhoršenia reliability. Failure path ostane zahrnutý v denominator-e. Recovery path meria trust a time-to-repair pri first incident. Second-change path overí managed lifecycle. Forbidden path odmietne portal-task proxy ako sole metric, successful-only survey, individual ranking, bot-inflated activity, aggregate bez cohorts a intervention bez causal hypothesis.

## 11. Troubleshooting a anti-patterny

Pri rozpore medzi dashboardom a lived experience sa kontroluje exact cohort/journey, denominator, inclusion/exclusion rules, platform generation, timestamps naprieč systems, queue/wait/manual time, support joins, bot classification, survey sampling/non-response, quality/reliability guards a business outcome. Potom sa overí, či metric motivuje gaming alebo lokálnu optimalizáciu.

Anti-patterny sú: `developer productivity = commits`, `DevEx = satisfaction score`, `portal latency = time-to-production`, `survey iba úspešných`, `priemer bez segmentov`, `čo nemeriame v portali neexistuje`, `guardrail je automaticky bad friction` a `dashboard correlation = root cause`.

## Glossary impact

Relevantné pojmy: DevEx subject, developer journey, moment of truth, feedback quality, cognitive load, flow, friction taxonomy, valuable friction, complete journey denominator, survivorship bias, bot activity classification, causal DevEx hypothesis, second-change experience a DevEx acceptance verdict.

## Primárne zdroje

- [Microsoft Research — The SPACE of Developer Productivity](https://www.microsoft.com/en-us/research/publication/the-space-of-developer-productivity-theres-more-to-it-than-you-think/)
- [DORA — Platform engineering capability](https://dora.dev/capabilities/platform-engineering/)
- [DORA — Choosing measurement frameworks](https://dora.dev/research/2025/measurement-frameworks/)
- [CNCF Platform Engineering Maturity Model](https://tag-app-delivery.cncf.io/whitepapers/platform-eng-maturity-model/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Self-service](self-service.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Service catalog →](service-catalog.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
