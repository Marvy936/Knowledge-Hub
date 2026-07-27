# Helm hook, upgrade and testing lifecycle glossary entries

## Business-compatible recovery — Helm

Recovery verdict, pri ktorom technical release state, durable data, event/contracts, external integrations a pôvodný business outcome tvoria vzájomne kompatibilný celok. Technicky úspešný manifest rollback bez spracovateľného backlogu nie je business-compatible recovery. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Cohort-aware Helm test

Release test, ktorý neoveruje iba jeden náhodný request, ale identifikuje všetky serving Pod alebo backend cohorts, ich image/configuration generations a rozloženie opakovaných requests. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Deterministic render evidence — Helm

Dôkaz, že rovnaký chart artifact, dependency lock, effective values, release context a capabilities vytvárajú rovnaký rendered-manifest digest bez neplánovaného live, časového alebo random inputu. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Durable operation ledger — Helm

Autoritatívny persistentný záznam hook operácií podľa operation ID, source/target state-u, checksumu a výsledku, ktorý umožňuje rozlíšiť complete, partial, failed a unknown outcome aj po odstránení Job resource-u. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Expected Helm evidence inventory

Vopred definovaný zoznam dôkazov, ktoré musia vzniknúť pre konkrétny immutable release subject: artifact a lock digests, effective values, rendered manifest, admission verdict, hook results, live generations, runtime cohorts a business/forbidden outcomes. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## External side-effect commit — Helm

Bod, v ktorom hook durable zmení databázu, queue, external API alebo inú autoritatívnu vrstvu bez ohľadu na to, či Helm následne zaznamená successful hook alebo release status. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Forbidden outcome test — Helm

Negatívne acceptance overenie pre release alebo recovery, napríklad že starý credential je odmietnutý, duplicate authorization nevznikla, stale Pod UID neprijíma traffic alebo destructive hook sa nezopakoval. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm evidence lifecycle

Chain `release risk/contract → immutable subject → expected evidence → source/render/API/runtime/business observations → verdict → incident diagnosis → regression closure`, ktorý viaže všetky testy a findings na rovnaký release artifact. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm hook operation subject

Exact identity hook operácie tvorená release name, source/target revision, lifecycle pointom, rendered hook digestom, Job/Pod UIDs, operation ID a source/target durable state generation. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Helm incident subject

Presný troubleshooting subject obsahujúci cluster/context/namespace, release revision, chart/dependency/values/manifest digests, live object a process identities, configuration/data generations, request alebo transaction ID a timeline. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm recovery hierarchy

Preferované poradie recovery od opravy authoritative source a novej revision cez dokončenie idempotentného hooku, roll-forward, eligible rollback a compensation až po restore pri skutočnej data/control-plane recovery potrebe. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm release transition subject

Immutable source-to-target identity upgrade-u alebo rollbacku zahŕňajúca release revisions, chart/dependency/values/manifest digests, image digests, hook operation IDs, data/schema/event generations, cluster target a Helm/deployment-engine verziu. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Helm roll-forward

Recovery transition, ktorý nasadí novú opravenú a current-state-compatible revision namiesto návratu k historickej revision, najmä keď durable schema, event backlog alebo external side effects už nie sú backward-compatible. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Helm troubleshooting closure

Incident closure verdict vyžadujúci opravený authoritative source, overený pôvodný aj forbidden outcome, kontrolu adjacent cohorts, stabilný druhý render/retry/reconcile a regression test na najskoršej spoľahlivej boundary. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Hook evidence-retention contract — Helm

Pravidlá určujúce, ktoré hook Job/Pod resources, logs, audit records a durable operation results prežijú success, failure, delete policy a TTL dostatočne dlho na diagnostiku a recovery. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook execution attempt — Helm

Jedna konkrétna Job/Pod alebo container execution generation hooku, identifikovaná resource UID, Pod UID, container ID, retry countom a operation ID; nie je totožná s logical external operation. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook fencing — Helm

Lock, compare-and-set, advisory lock, epoch alebo iný control zabraňujúci concurrent hook attempts vykonať konfliktujúce durable side effects nad rovnakým target state-om. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook readiness boundary — Helm

Rozdiel medzi API loadom non-workload hook resource-u, completion Job/Pod hooku, durable external side-effect commitom a Helm release statusom; každý bod poskytuje iný dôkaz. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook recovery verdict — Helm

Rozhodnutie založené na operation ledger-e, target state-e a release evidence, či hook treba považovať za complete no-op, bezpečne resume-nuť, kompenzovať alebo zastaviť pre unknown outcome. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Immutable chart test subject

Exact testovaný Helm artifact a environment contract vrátane chart/dependency/values/manifest digests, Helm/deployment-engine verzie, target clusteru a očakávaných runtime/data generations. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Pending operation unknown outcome — Helm

Stav, keď release metadata alebo klient nevie potvrdiť výsledok upgrade-u, rollbacku alebo hooku, hoci niektoré Kubernetes alebo external mutations mohli prebehnúť; vyžaduje observation pred retry. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Release compensation — Helm

Cielená nápravná operácia nad external alebo durable side effectom, ktorý sa nedá vrátiť historickým rendered manifestom, napríklad duplicate message, API registration, authorization alebo DNS/IAM zmena. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Release/runtime evidence boundary — Helm

Rozdiel medzi Helm-stored revision, values, manifestom a hook inventory na jednej strane a live object, process-loaded configuration, serving cohort a business outcome evidence na druhej strane. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Release transition closure — Helm

Konečný verdict upgrade/recovery, ktorý viaže final Helm revision na live Kubernetes generations, durable data/contracts, business acceptance, forbidden outcomes a retirement starej alebo nekompatibilnej generation. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Recovery eligibility gate — Helm

Pre-change alebo incident-time rozhodnutie, či konkrétny rollback, roll-forward, compensation alebo restore candidate je kompatibilný s current artifacts, APIs, data, events, credentials a external systems. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Rendered hook inventory

Complete set hook resources vyrenderovaných z parent chartu aj enabled dependencies vrátane lifecycle points, weights, names, images, RBAC, arguments, timeouts, operation IDs a cleanup policies. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Rollback compatibility matrix — Helm

Explicitné overenie historickej application/release generation voči current schema, event backlogu, external API, credential epoch, Kubernetes API a CRD storage generation pred vykonaním rollbacku. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Source release generation — Helm

Current release revision a jej immutable chart/dependency/values/manifest, image a durable-state identities, z ktorých začína plánovaný transition. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Subchart hook authority

RBAC, credentials a external side-effect capability pridaná dependency hookom do spoločného single-release execution surface-u, aj keď parent application runtime tieto oprávnenia nepotrebuje. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Symptom-to-release translation — Helm

Proces prekladu user alebo business symptómu na exact release, render, hook, live object, process, data a request identities pred formulovaním troubleshooting hypotéz. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Target release generation — Helm

Navrhovaná release revision so všetkými target chart/dependency/values/manifest, image, hook a durable-state generations, ktoré majú po transitione tvoriť accepted state. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Technical rollback — Helm

Rollback, pri ktorom Helm úspešne obnoví historický rendered manifest a vytvorí deployed revision, ale ešte nie je preukázaná kompatibilita runtime-u s current durable alebo external state-om. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Unknown hook outcome

Stav, keď hook side effect mohol commitnúť, ale Helm/Job completion alebo response evidence chýba; ďalší attempt musí najprv pozorovať durable operation state. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Upgrade input closure — Helm

Úplný versionovaný súbor inputs rozhodujúcich o target renderi a operation behavior-e: chart artifact, dependency lock, effective values, release context, Capabilities/lookup state, post-renderer, Helm/plugins a target API/admission environment. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Upgrade-path test — Helm

Test, ktorý začína zo supported previous release s realistickými stored values, objects, retained data a external state-om a overuje target hooks, mixed-version transition, acceptance a recovery; fresh install ho nenahrádza. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Values matrix oracle — Helm

Pre každý relevantný values case explicitne definovaný očakávaný resource, field, absence/presence a runtime effect, nie iba požiadavka, že render má skončiť bez chyby. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).
