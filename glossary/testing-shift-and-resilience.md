# Shift and resilience glossary entries

## Abort criterion

Vopred definovaná podmienka, pri ktorej sa rollout alebo experiment okamžite zastaví, pretože dopad prekročil prijateľnú hranicu. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md) a [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## A/B testing

Kontrolovaný produktový experiment porovnávajúci výsledok kontrolnej a experimentálnej skupiny podľa vopred definovanej hypotézy a metrík. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Blast radius

Maximálny rozsah používateľov, trafficu, dát, komponentov alebo failure domains, ktoré môže zmena, incident alebo experiment ovplyvniť. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Brownout

Čiastočné alebo premenlivé zlyhanie dependency, pri ktorom služba odpovedá pomaly, iba niektorým requestom alebo s neúplným výsledkom namiesto úplného outage-u. Brownout často drží resources a spúšťa retry amplification. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Canary release

Postupné sprístupnenie novej verzie malej časti trafficu alebo používateľov s porovnávaním technických a business signálov pred širšou promotion. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Chaos engineering

Disciplína formulovania a vykonávania kontrolovaných experimentov, ktoré overujú schopnosť systému zachovať prijateľné správanie pri poruchách a neistote. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Chaos testing

Praktická forma riadeného fault experimentu overujúca konkrétnu steady-state hypotézu v definovanom scope s bezpečnostnými kontrolami. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Control group — experiment

Skupina používateľov, requestov alebo systémových instances, ktorá nedostane experimentálnu zmenu a poskytuje súbežnú baseline na porovnanie. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Controlled exposure

Riadené sprístupňovanie release-u alebo feature obmedzenej cohrte s explicitnou artifact, configuration a routing identitou, guardrails a rozhodovacími kritériami. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Dark launch

Nasadenie capability do produkčného prostredia bez jej priameho sprístupnenia používateľom, používané na overenie integrácie, capacity alebo prevádzkového správania. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Early feedback

Informácia o kvalite alebo riziku získaná v najskoršom bode, v ktorom má kontrola dostatočnú fidelity a diagnostickú hodnotu. Pozri [Shift-left](docs/04-testing-and-quality/shift-left.md).

## Evidence placement

Rozhodnutie, v ktorej najskoršej vrstve delivery možno získať dostatočne spoľahlivý dôkaz bez odstránenia relevantnej failure boundary. Pozri [Shift-left](docs/04-testing-and-quality/shift-left.md).

## Experiment contract

Explicitný popis hypotézy, steady state, faultu, scope, blast radiusu, trvania, abort criteria, recovery, ownershipu a dôkazov chaos experimentu. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Experiment validity

Vlastnosť experimentu, pri ktorej baseline, target, fault, workload a observation zodpovedajú deklarovanému contractu natoľko, aby výsledok mohol potvrdiť alebo vyvrátiť hypotézu. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Fault injection

Kontrolované zavedenie konkrétneho failure condition, napríklad latency, process termination, resource pressure alebo dependency erroru. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Feature flag

Konfiguračný mechanizmus oddeľujúci deployment kódu od sprístupnenia funkcionality konkrétnym používateľom, cohortám alebo percentu trafficu. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Game day

Plánované tímové resilience cvičenie kombinujúce technické faults, observability, incident response, komunikáciu a následné learning actions. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Golden path

Podporovaný a automatizovaný spôsob vývoja a delivery poskytujúci bezpečné defaults, reusable tooling, observability a policy guardrails. Pozri [Shift-left](docs/04-testing-and-quality/shift-left.md).

## Graceful degradation

Schopnosť systému pri nedostupnosti časti dependencies zachovať obmedzenú, ale stále užitočnú a bezpečnú funkcionalitu namiesto úplného zlyhania. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Guardrail metric

Metrika chrániaca experiment alebo rollout pred neprijateľným vedľajším dopadom, aj keď primary metric vyzerá pozitívne. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Kill switch

Technický mechanizmus umožňujúci rýchlo zastaviť fault injection, experiment alebo feature exposure pri prekročení bezpečných hraníc. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Load shedding

Riadené odmietanie alebo obmedzenie časti práce pri preťažení, aby systém chránil kritické workflow a zabránil úplnému kolapsu. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Matched cohort

Experimentálna alebo kontrolná skupina zostavená tak, aby bola porovnateľná podľa významných vlastností, napríklad tenant size, regiónu, zariadenia alebo workloadu. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Post-promotion watch

Observation obdobie po dosiahnutí plnej expozície, ktoré sleduje oneskorené, kumulatívne alebo segmentovo zriedkavé failures pred uzavretím release rozhodnutia. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Progressive delivery

Delivery model, ktorý postupne zvyšuje exposure novej verzie alebo funkcionality podľa observability, experimentálnych metrík a automatizovaných promotion či rollback pravidiel. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Production validation

Overenie technického, funkčného a business výsledku zmeny v skutočnom produkčnom kontexte po deploymente alebo počas kontrolovaného rollout-u. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Real User Monitoring — RUM

Zber performance a error telemetry zo skutočných používateľských klientov a sessions s možnosťou segmentácie podľa zariadenia, browsera, regiónu alebo journey. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Recovery observation

Samostatná fáza resilience experimentu po odstránení faultu, ktorá overuje backlog drain, reconciliation, návrat resources a splnenie recovery deadline. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Resilience engineering

Disciplína navrhovania a zlepšovania schopnosti sociotechnického systému predvídať, absorbovať, zotaviť sa a učiť sa z porúch a variability. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Retry amplification

Násobenie pôvodného workloadu, keď client, proxy a služby nezávisle retryujú rovnaké zlyhanie a vytvoria viac pokusov na jednu business operáciu. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Rollout state machine

Explicitné stavy produkčnej expozície s povolenými transitions, observation window, success criteria, abort thresholds a rollback alebo roll-forward akciami. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## RPO — Recovery Point Objective

Maximálne prijateľné množstvo dát vyjadrené časovým bodom, ktoré môže byť pri obnove po katastrofe stratené. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## RTO — Recovery Time Objective

Maximálny prijateľný čas na obnovenie služby alebo business capability po katastrofickom zlyhaní. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Safety state machine

Riadený lifecycle fault experimentu od prechecks cez fault activation a removal až po recovery a cleanup, pričom každý stav má povolené transitions, timeouty a safety guardrails. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Shadow traffic

Kópia reálneho produkčného trafficu posielaná novému systému bez použitia jeho response ako výsledku pre používateľa; vyžaduje kontrolu side effects a citlivých dát. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Shift-left

Presun vhodných rozhodnutí, kontrol a feedbacku do skorších fáz delivery, kde možno riziko zachytiť lacnejšie bez neprimeranej straty fidelity. Pozri [Shift-left](docs/04-testing-and-quality/shift-left.md).

## Shift-right

Rozšírenie validácie, observability a experimentovania do deploymentu a produkcie s kontrolovaným blast radiusom a jasnými rozhodovacími kritériami. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Signal latency

Čas medzi vznikom zmeny alebo failure a dostupnosťou dostatočne úplného signálu pre rollout či experiment decision. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Steady state — chaos engineering

Merateľné používateľské alebo prevádzkové správanie, ktoré má systém počas definovaného faultu zachovať v prijateľných hraniciach. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Tabletop exercise

Simulované incident alebo disaster-recovery cvičenie bez technického fault injection, ktoré overuje rozhodovanie, prístupy, runbooky, komunikáciu a ownership. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).