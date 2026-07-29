# SRE reliability, SLO, error-budget and toil lifecycle glossary entries

## Reliability subject

Exact business capability, user/cohort, required function, stated conditions, environment/release generation, period alebo opportunities, dependencies, acknowledgement boundary, data/recovery scope a evidence authority analyzovanej reliability vlastnosti. Pozri [Reliability, availability a durability](docs/14-sre-and-operations/reliability-availability-durability.md).

## Required function — reliability

Konkrétny user alebo business outcome, ktorý má systém vykonať bez failure-u za definovaných conditions a počas definovaného obdobia. Pozri [Reliability, availability a durability](docs/14-sre-and-operations/reliability-availability-durability.md).

## Stated conditions — reliability

Explicitný traffic, data, dependency, environment, failure-assumption a time/opportunity context, v ktorom sa reliability tvrdenie vyhodnocuje. Pozri [Reliability, availability a durability](docs/14-sre-and-operations/reliability-availability-durability.md).

## Event-based availability

Podiel good eligible service events voči všetkým eligible events, vhodný pre partial a traffic-weighted request alebo workflow availability. Pozri [Reliability, availability a durability](docs/14-sre-and-operations/reliability-availability-durability.md).

## Time-based availability

Podiel času, počas ktorého je exact service capability usable, voči celému eligible service window-u. Pozri [Reliability, availability a durability](docs/14-sre-and-operations/reliability-availability-durability.md).

## Partial availability

Stav, keď service capability funguje iba pre časť cohorts, Regions, tenants, operations, data shapes alebo release generations a aggregate metric môže impact skryť. Pozri [Reliability, availability a durability](docs/14-sre-and-operations/reliability-availability-durability.md).

## Durability subject

Exact acknowledged data alebo business-state identity, commit boundary, required retention interval, copies/logs, mutation/deletion rules, key dependencies, backup lineage a reconstructability contract. Pozri [Reliability, availability a durability](docs/14-sre-and-operations/reliability-availability-durability.md).

## Acknowledgement boundary — reliability

State transition, po ktorej service callerovi tvrdí, že operation alebo intent bol prijatý, committed alebo dokončený a preto musí mať definované retry, durability a recovery semantics. Pozri [Reliability, availability a durability](docs/14-sre-and-operations/reliability-availability-durability.md).

## Durable intent

Acknowledged business command alebo state, ktorý zostáva bezpečne vykonateľný, deduplikovateľný a reconstructable počas required lifecycle-u aj po process, dependency alebo storage failure-i. Pozri [Reliability, availability a durability](docs/14-sre-and-operations/reliability-availability-durability.md).

## Logical durability failure

Strata alebo poškodenie acknowledged business state-u spôsobené validnou application, administrative alebo malicious mutation, ktorá sa môže správne replikovať do všetkých online copies. Pozri [Reliability, availability a durability](docs/14-sre-and-operations/reliability-availability-durability.md).

## Reconstructability

Schopnosť z authoritative production alebo approved recovery lineage znovu vytvoriť complete a business-consistent acknowledged state vrátane dependencies a identity semantics. Pozri [Reliability, availability a durability](docs/14-sre-and-operations/reliability-availability-durability.md).

## Reliability acceptance verdict

Dôkaz, že exact capability spĺňa availability, correctness, latency a durability contract, acknowledgement patrí durable transitionu, recovery obnoví business state a forbidden lost/duplicate/silent-success paths zlyhajú. Pozri [Reliability, availability a durability](docs/14-sre-and-operations/reliability-availability-durability.md).

## Second-failure validation

Opakovaný controlled dependency alebo component failure po remediation, ktorý overuje, že obnovená reliability nevznikla iba jednorazovým manuálnym zásahom. Pozri [Reliability, availability a durability](docs/14-sre-and-operations/reliability-availability-durability.md).

## Service-level subject

Versionovaný service, capability, cohort, operation, valid-event population, expected outcome, observation point, threshold, compliance window, exclusions, measurement generation a owner jedného SLI/SLO contractu. Pozri [SLI, SLO a SLA](docs/14-sre-and-operations/sli-slo-sla.md).

## Valid-event population — SLI

Exact denominator events oprávnené vstúpiť do SLI vrátane explicitných rules pre invalid requests, retries, duplicates, cancellations, maintenance a missing outcomes. Pozri [SLI, SLO a SLA](docs/14-sre-and-operations/sli-slo-sla.md).

## Good event — SLI

Eligible event, ktorý splnil definovaný user alebo business outcome vrátane required correctness, latency, scope a completion semantics. Pozri [SLI, SLO a SLA](docs/14-sre-and-operations/sli-slo-sla.md).

## SLI observation point

Boundary, na ktorej sa service outcome meria, napríklad client, edge, server, business ledger alebo recovery canary, spolu s explicitnými visibility limitations. Pozri [SLI, SLO a SLA](docs/14-sre-and-operations/sli-slo-sla.md).

## Measurement-generation identity — SLI

Versionovaný source, instrumentation/schema, collection, ingestion, classification, deduplication, query a correction contract vytvárajúci konkrétny SLI verdict. Pozri [SLI, SLO a SLA](docs/14-sre-and-operations/sli-slo-sla.md).

## SLO compliance window

Časové alebo eventové okno, nad ktorým sa SLI porovnáva s targetom, napríklad rolling 28 dní alebo calendar month. Pozri [SLI, SLO a SLA](docs/14-sre-and-operations/sli-slo-sla.md).

## SLO safety margin

Rozdiel medzi prísnejším interným reliability objective-om a voľnejším external alebo contractual commitmentom, ktorý poskytuje priestor na remediation pred SLA breachom. Pozri [SLI, SLO a SLA](docs/14-sre-and-operations/sli-slo-sla.md).

## Exclusion contract — SLO

Explicitné, bounded a auditovateľné pravidlá určujúce, ktoré events alebo intervals nevstupujú do SLI/SLO alebo SLA population a prečo. Pozri [SLI, SLO a SLA](docs/14-sre-and-operations/sli-slo-sla.md).

## Provisional outcome — SLI

Dočasná klasifikácia async eventu pred uplynutím completion deadline-u alebo príchodom authoritative final evidence. Pozri [SLI, SLO a SLA](docs/14-sre-and-operations/sli-slo-sla.md).

## Finalization delay — SLI

Čas vyhradený na late evidence a reconciliation pred uzavretím measurement generation bez spätného vymazania už vzniknutého deadline violation-u. Pozri [SLI, SLO a SLA](docs/14-sre-and-operations/sli-slo-sla.md).

## SLO acceptance verdict

Dôkaz, že user-centered population, good-event rule, observation point, measurement coverage, target, window, exclusions a consequences vytvárajú reprodukovateľný allowed aj bad-event verdict. Pozri [SLI, SLO a SLA](docs/14-sre-and-operations/sli-slo-sla.md).

## Error-budget subject

Exact SLI/SLO/policy revision, service, cohort, window, eligible population, exclusions, measurement generation a owner, ku ktorým patrí tolerovaný failure budget. Pozri [Error budgets](docs/14-sre-and-operations/error-budgets.md).

## Error-budget generation

Konkrétny výpočet allowed, observed, remaining a consumed bad events pre versionovaný SLO a compliance window. Pozri [Error budgets](docs/14-sre-and-operations/error-budgets.md).

## Allowed bad events

Maximálny počet alebo podiel eligible events, ktoré môžu porušiť SLO v danom okne bez jeho prekročenia. Pozri [Error budgets](docs/14-sre-and-operations/error-budgets.md).

## Error-budget burn rate

Pomer aktuálnej bad-event rate voči rate, ktorá by error budget rovnomerne minula presne na konci compliance window-u. Pozri [Error budgets](docs/14-sre-and-operations/error-budgets.md).

## Fast burn

Krátkodobá vysoká error-budget consumption indikujúca závažný incident a potrebu urgentnej reakcie. Pozri [Error budgets](docs/14-sre-and-operations/error-budgets.md).

## Slow burn

Dlhodobejšia mierne zvýšená error-budget consumption indikujúca chronic degradation alebo systematický reliability debt. Pozri [Error budgets](docs/14-sre-and-operations/error-budgets.md).

## Multi-window burn-rate alert

Alert kombinujúci krátke citlivé a dlhšie potvrdzujúce evaluation windows na odhalenie rýchleho aj pomalého budget burnu bez nadmerného noise-u. Pozri [Error budgets](docs/14-sre-and-operations/error-budgets.md).

## Error-budget policy

Schválený governance contract mapujúci budget state a burn rate na release, incident, reliability-work, exception, escalation a návrat-do-normal-mode decisions. Pozri [Error budgets](docs/14-sre-and-operations/error-budgets.md).

## Discretionary change — error budget

Zmena prinášajúca voliteľnú product alebo operational hodnotu, ktorú možno pri vyčerpanom budgete odložiť bez blokovania security, recovery alebo root-cause remediation. Pozri [Error budgets](docs/14-sre-and-operations/error-budgets.md).

## Recurrence gate — error budget

Podmienka vyžadujúca uzavretie root-cause a regression evidence pred obnovením normal release mode-u aj vtedy, keď sa calendar alebo rolling budget formálne obnovil. Pozri [Error budgets](docs/14-sre-and-operations/error-budgets.md).

## Error-budget acceptance verdict

Dôkaz, že budget je reprodukovateľný, burn-rate a missing-data semantics sú správne, policy consequence sa presadila a reset, stale-query alebo duplicate-event paths neobídu reliability governance. Pozri [Error budgets](docs/14-sre-and-operations/error-budgets.md).

## Toil subject

Exact service, operational workflow, trigger, actor, steps, frequency, touch time, wait time, interruption cost, privilege, error risk, scale driver, owner a measurement window analyzovaného toil-u. Pozri [Toil](docs/14-sre-and-operations/toil.md).

## Operational demand — toil

Incident, request, alert, maintenance alebo process condition vytvárajúca opakovanú human operational prácu. Pozri [Toil](docs/14-sre-and-operations/toil.md).

## Human touch time

Aktívny čas, počas ktorého človek musí workflow pozorovať, rozhodovať alebo vykonávať, oddelený od celkového elapsed wait time-u automation alebo dependency. Pozri [Toil](docs/14-sre-and-operations/toil.md).

## Toil reinforcing loop

Slučka, v ktorej rast incidentov a manuálnej práce znižuje engineering capacity, čím sa odkladajú root-cause fixes a vzniká ešte viac operational demandu. Pozri [Toil](docs/14-sre-and-operations/toil.md).

## Root-demand elimination

Redesign služby alebo procesu, ktorý odstráni príčinu operational workflowu namiesto automatizácie jeho posledného manuálneho kroku. Pozri [Toil](docs/14-sre-and-operations/toil.md).

## Residual toil

Human operational work, ktorý zostáva po reduction iniciatíve pre novel exceptions, risk judgment alebo zámerne neautomatizované boundaries. Pozri [Toil](docs/14-sre-and-operations/toil.md).

## Toil shift

Presun manual alebo repetitive práce na iný tím, používateľa alebo support channel bez skutočného zníženia end-to-end operational demandu. Pozri [Toil](docs/14-sre-and-operations/toil.md).

## Toil-reduction acceptance verdict

Dôkaz, že measured workflow demand a human touch sa trvalo znížili, automation je bounded a bezpečná, reliability sa nezhoršila a práca nebola iba skrytá alebo presunutá inde. Pozri [Toil](docs/14-sre-and-operations/toil.md).
