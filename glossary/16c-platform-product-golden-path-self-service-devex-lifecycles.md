# Platform product, golden path, self-service a developer-experience lifecycles

## Platform product subject

Exact platform capability/version, internal user segment, job-to-be-done, journey, interface, environment, outcome, ownership, adoption cohort, cost a lifecycle scope jedného product decisionu. Pozri [Platform as a Product](../docs/16-gitops-and-platform-engineering/platform-as-a-product.md).

## Internal user segment — Platform

Skupina platform consumers s podobnými jobs, constraints, riskom a support potrebami, pre ktorú možno definovať jeden zmysluplný capability contract a outcome. Pozri [Platform as a Product](../docs/16-gitops-and-platform-engineering/platform-as-a-product.md).

## Platform job-to-be-done

Konkrétny pokrok, ktorý application alebo product team potrebuje dosiahnuť v danom kontexte, napríklad bezpečne vytvoriť production-ready regulovaný service, nie iba vykonať lokálnu portal action. Pozri [Platform as a Product](../docs/16-gitops-and-platform-engineering/platform-as-a-product.md).

## Platform value hypothesis

Falsifikovateľné tvrdenie spájajúce target segment, current problem, platform capability, očakávaný developer/business outcome a guard conditions. Pozri [Platform as a Product](../docs/16-gitops-and-platform-engineering/platform-as-a-product.md).

## Platform product outcome tree

Decision model prepájajúci business outcome, user outcomes, observed opportunities a bounded experiments tak, aby roadmapa nebola iba zoznam technických outputs. Pozri [Platform as a Product](../docs/16-gitops-and-platform-engineering/platform-as-a-product.md).

## Platform capability contract

Versionovaný product sľub definujúci inputs, outputs, states, defaults, constraints, SLO, security, ownership, cost, compatibility, support a exit semantics platformovej capability. Pozri [Platform as a Product](../docs/16-gitops-and-platform-engineering/platform-as-a-product.md).

## Platform adoption funnel

Generation-aware postup od target users cez awareness, discovery, eligibility, request, usable outcome, production outcome a repeat use po retained managed adoption. Pozri [Platform as a Product](../docs/16-gitops-and-platform-engineering/platform-as-a-product.md).

## First usable platform outcome

Prvý stav, v ktorom owner dokáže platformou vytvorenú capability reálne použiť podľa integration a developer-functional contractu, nie iba pozorovať existenciu resources. Pozri [Platform as a Product](../docs/16-gitops-and-platform-engineering/platform-as-a-product.md) a [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## First production platform outcome

Prvý verified production business alebo operational výsledok dosiahnutý cez konkrétnu platform capability generation a journey. Pozri [Platform as a Product](../docs/16-gitops-and-platform-engineering/platform-as-a-product.md).

## Retained managed adoption

Dlhodobé používanie podporovanej capability generation bez detached forks, hidden bypassov alebo neudržateľného manual supportu. Pozri [Platform as a Product](../docs/16-gitops-and-platform-engineering/platform-as-a-product.md).

## Platform product owner

Accountable authority za user problem, capability contract, roadmap, adoption, feedback closure a product outcome; nepreberá automaticky runtime ownership každého underlying componentu. Pozri [Platform as a Product](../docs/16-gitops-and-platform-engineering/platform-as-a-product.md).

## Platform product feedback closure

Proces, ktorý koreluje user signal s journey a capability generation, určí action alebo vysvetlený non-action, komunikuje rozhodnutie a neskôr overí outcome. Pozri [Platform as a Product](../docs/16-gitops-and-platform-engineering/platform-as-a-product.md).

## Capability parity gate

Dôkaz, že nová alebo povinne migrovaná platform capability pokrýva required current journeys, controls, lifecycle a recovery pre target segment pred uzavretím starej cesty. Pozri [Platform as a Product](../docs/16-gitops-and-platform-engineering/platform-as-a-product.md).

## Platform-as-a-Product acceptance verdict

Dôkaz, že explicitný segment, job, value hypothesis, capability contract, adoption, reliability, cost, feedback a lifecycle vytvárajú udržateľný interný produkt s overeným outcome-om. Pozri [Platform as a Product](../docs/16-gitops-and-platform-engineering/platform-as-a-product.md).

## Golden-path subject

Exact path identity/version, target segment a job, input decisions, resolved executable dependencies, authoritative outputs, ownership, upgrade, exception a acceptance scope. Pozri [Golden paths a paved road](../docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md).

## Paved-road contract

Organizačne preferovaný a podporovaný journey contract, do ktorého platforma investuje reliability, security, documentation a lifecycle, pričom zachováva explicitné alternatívy a odchýlky. Pozri [Golden paths a paved road](../docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md).

## Golden cage

Path, ktorý je povinný alebo technicky uzamknutý bez capability parity, extension, exception alebo detached ownership modelu a preto presúva legitimate potreby do forks a bypassov. Pozri [Golden paths a paved road](../docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md).

## Path decision architecture

Klasifikácia golden-path decisions na fixed invariants, defaults, required explicit choices, derived values, unsupported combinations a supported extension points. Pozri [Golden paths a paved road](../docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md).

## Progressive disclosure — Platform

Experience model, ktorý pri bežnom toku ukazuje jednoduchý intent a outcome, pri decisione consequences a pri failure underlying state, identity, evidence a recovery. Pozri [Golden paths a paved road](../docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md).

## Bootstrap template

Template, ktorý vytvorí počiatočné files alebo resources, no po copy nemusí zachovať managed upgrade, compatibility alebo runtime contract. Pozri [Golden paths a paved road](../docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md).

## Managed path component

Versionovaný reusable pipeline, module, chart, policy alebo controller contract konzumovaný cez stabilný interface a spravovaný aj po prvom bootstrap-e. Pozri [Golden paths a paved road](../docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md).

## Path composition graph

Dependency a ownership graph repositories, pipelines, artifacts, runtime, data, identity, policy, observability, catalog a support outputs tvoriacich jeden end-to-end golden path. Pozri [Golden paths a paved road](../docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md).

## Supported path extension

Versionovaný extension point umožňujúci custom behavior bez modifikácie alebo forku interného golden-path implementation graphu. Pozri [Golden paths a paved road](../docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md).

## Time-bounded path exception

Schválená dočasná odchýlka s exact scope-om, riskom, compensating controls, ownerom, expiry a návratovým plánom. Pozri [Golden paths a paved road](../docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md).

## Detached path ownership

Explicitný lifecycle stav, v ktorom team opustí managed path a preberie definované security, upgrade, operations a audit responsibilities. Pozri [Golden paths a paved road](../docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md).

## Path upgrade channel

Mechanizmus consumer inventory, compatibility diffu, reviewed alebo automated change-u, rollout-u, rollback-u a residual closure pri prechode na novú golden-path generation. Pozri [Golden paths a paved road](../docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md).

## Path generation compliance

Dôkaz, že effective repository, managed components, runtime a policies stále zodpovedajú podporovanej path generation; historické použitie template-u samo nestačí. Pozri [Golden paths a paved road](../docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md).

## Golden-path acceptance verdict

Dôkaz, že exact reprodukovateľná path generation pokrýva lifecycle, ownership, extension, security, testing, upgrade a end-to-end developer/business outcome bez skrytého cage alebo detached driftu. Pozri [Golden paths a paved road](../docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md).

## Self-service request subject

Exact requester/owner, capability version, target identity, action, environment, classification, dependency context, expected current state, idempotency a outcome scope jedného self-service intentu. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Self-service eligibility

Current policy decision, či daný principal, team, service a environment smú použiť capability vzhľadom na ownership, classification, prerequisites, quota a target scope. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Platform preflight

Read-only alebo reservation-aware fáza, ktorá pred mutation overí identity, conflicts, policy, quota, dependencies, compatibility a current-state freshness a vytvorí vysvetliteľný plán. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Subject-bound platform plan

Predicted mutation a output graph viazaný na exact request digest, policy version a expected base state, ktorého zmena invaliduje approval alebo execution eligibility. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Delegated platform execution identity

Least-privilege short-lived principal, ktorým platforma vykonáva autorizované mutations v mene upstream requestera bez vydania broad provider alebo cluster credentials používateľovi. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Durable self-service operation

Persistovaný state machine record requestu, child operations, transitions, outputs a recovery, ktorý prežije process timeout, restart a asynchronous provider behavior. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Platform waiting state

Ne-terminálny operation state s explicitným dôvodom, ownerom, deadline-om a wake-up mechanismom, napríklad WaitingApproval, WaitingCapacity alebo WaitingExternal. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Partial platform outcome

Stav, v ktorom časť authoritative mutations alebo outputs existuje, ale complete capability contract nebol splnený a systém musí retry, compensate alebo vyžiadať structured intervention. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Unknown platform outcome

Stav po strate acknowledgementu alebo neúplnom evidence, keď mutation mohla alebo nemusela nastať a pred retry je povinný authoritative read-back. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Semantic request idempotency

Mechanizmus viažuci retries na rovnaký business/platform intent a desired generation tak, aby sa vrátil existing result alebo konflikt namiesto duplicate side effectu. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Child operation identity

Stable ID downstream Git, cloud, identity, runtime alebo provider operation uložené pri parent platform requeste pre polling, read-back, retry a audit correlation. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Platform compensation

Best-effort alebo contract-defined reverzná operácia, ktorá po partial failure odstráni, revokuje alebo neutralizuje už vykonané effects a následne overí residual state. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Self-service backpressure

Admission, queue, fairness, quota, priority a bounded-retry mechanizmy chrániace platform control plane a downstream providers pred overloadom a retry amplification. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Usable capability outcome

Verified stav, v ktorom required resources, integrations, permissions a developer-functional behavior umožňujú ownerovi vykonať intended job, nie iba pozorovať successful create response. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Self-service acceptance verdict

Dôkaz, že discoverable bounded request cez exact authorization, preflight, durable idempotent operation, truthful states, capacity, recovery a lifecycle vedie k usable outcome-u bez unrestricted privilege. Pozri [Self-service](../docs/16-gitops-and-platform-engineering/self-service.md).

## Developer-experience subject

Exact developer/team cohort, goal, journey, tool/platform generation, repository/environment context, time window, outcome constraints, measurement instruments a privacy scope. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).

## Developer journey

End-to-end sekvencia actions, decisions, tools, handoffs, waiting a evidence od developer goalu po delivery, operational alebo business outcome. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).

## Developer feedback-loop quality

Kombinácia latency, relevance, dôveryhodnosti, actionability, subject identity a reproducibility informácie medzi developer action a poznaním výsledku. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).

## Developer cognitive load

Mentálna kapacita potrebná na pochopenie a vykonanie software tasku vrátane intrinsic problem complexity a extraneous complexity vytvorenej nekonzistentnými interfaces, skrytými dependencies alebo tribal knowledge. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).

## Extraneous developer load

Cognitive load, ktorá nevychádza z business alebo technického problému, ale z nejasných tools, policies, handoffs, duplicate inputs, hidden state a potreby pamätať si workaroundy. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).

## Developer flow state

Sústredená práca s jasným cieľom, primeranou výzvou a minimom zbytočných interruptions, waiting a context switching, hodnotená v kontexte team outcome-u. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).

## Developer friction taxonomy

Klasifikácia waiting, interaction, decision, feedback, access/dependency, operational a organizational friction podľa mechanismu a consequence v developer journey. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).

## Developer moment of truth

Journey bod s disproporčným vplyvom na dôveru a adopciu, napríklad prvý onboarding, prvá failure, prvý production deploy, incident alebo upgrade. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).

## Time-to-understand

Čas od dostupnosti feedbacku alebo incident signálu po schopnosť developera správne klasifikovať príčinu a zvoliť action, odlišný od samotného execution time-u. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).

## DevEx mixed-method evidence

Kombinácia system telemetry, survey, interview, observation, support a outcome dát použitá na pochopenie developer experience a jej mechanizmu. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).

## Developer experience sampling

Krátke context-bound zisťovanie perception blízko konkrétneho workflow eventu, ktoré znižuje recall bias a viaže feedback na exact journey a generation. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).

## DevEx counterbalanced metrics

Súbor speed, quality, experience/effectiveness, reliability, safety a business-impact measures, ktorý bráni optimalizácii jednej activity metriky na úkor celého systému. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).

## Developer-outcome guard metric

Quality, security, reliability, cost, collaboration alebo well-being signal, ktorý musí zostať v povolenom rozsahu počas DevEx intervention. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).

## DevEx feedback closure

Proces korelácie friction signálu s cohortom a journey, vytvorenia causal hypothesis, priradenia ownera, bounded intervention a overenia developer aj business výsledku. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).

## Developer-experience acceptance verdict

Dôkaz, že reprezentatívna mixed-method evidence a counterbalanced outcomes potvrdzujú zlepšenie exact journey-u cez vysvetlený mechanismus bez punitive measurement alebo presunu toil-u a risku. Pozri [Developer experience](../docs/16-gitops-and-platform-engineering/developer-experience.md).
