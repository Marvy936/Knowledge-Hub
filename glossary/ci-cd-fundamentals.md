# CI/CD fundamentals glossary entries

## Artifact promotion

Presun už vytvoreného a overeného immutable artifactu medzi environmentmi alebo release stages bez jeho opätovného rebuildovania. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Automated promotion

Policy-driven rozhodnutie posunúť artifact alebo rollout do ďalšej fázy bez rutinného manuálneho approvalu na základe complete evidence, risku a environment health. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Automatic rollback

Automatizovaný návrat na predchádzajúcu kompatibilnú verziu po detekcii spoľahlivého failure signálu. Nie je bezpečný pri každej stateful alebo nevratnej zmene. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Broken main

Stav, keď hlavná integračná branch nespĺňa povinné build alebo quality gates a nemá byť považovaná za dôveryhodný integračný základ. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Build once

Princíp vytvoriť pre konkrétny candidate jeden immutable artifact a ten istý artifact následne testovať a promovať medzi prostrediami. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Canary analysis

Automatizované alebo riadené porovnanie novej verzie s baseline či kontrolnou skupinou podľa technických, funkčných a business metrík počas obmedzeného rollout-u. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Candidate integration state

Presný výsledný source tree, ktorý by po integrácii vznikol, typicky reprezentovaný synthetic merge alebo merge-queue SHA a overovaný proti aktuálnemu targetu. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Complete evidence

Stav, pri ktorom sa vykonali všetky required controls a existujú všetky očakávané reports, shards, artifacts a tool statusy pre presný candidate. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Continuous Delivery

Schopnosť udržiavať systém a jeho artifacty v stave pripravenom na bezpečný, opakovateľný a auditovateľný produkčný deployment na požiadanie. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Continuous Deployment

Delivery model, v ktorom každá zmena spĺňajúca automatizovanú promotion policy pokračuje bez rutinného manuálneho release approvalu do produkčného rollout-u. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Continuous Integration

Pracovný a technický model častej integrácie malých zmien do spoločnej hlavnej línie s automatizovaným verdictom nad presným candidate integration stateom. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Deployability invariant

Trvalá vlastnosť systému, pri ktorej immutable artifact, evidence, configuration, shared-state compatibility, deployment automation, observability a recovery umožňujú bezpečný deployment bez stabilizačného projektu. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Deployable state

Stav, v ktorom existuje dôveryhodný immutable artifact, potrebné dôkazy, kompatibilná konfigurácia, deployment automation, observability a recovery plán umožňujúci bezpečný deployment. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Deployment marker

Časovo a verziou označená udalosť v observability systéme umožňujúca korelovať zmenu error rate, latency alebo business metrík s konkrétnym deploymentom. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Deployment pipeline

Automatizovaný tok od source zmeny cez build, artifact, risk-specific validation a environment promotion až po produkčne pripraveného alebo nasadeného kandidáta. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Evidence completeness

Kontrola, že pre presný candidate existuje celý očakávaný manifest required testov, scanov, shardov, reports a tool execution statusov. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Evidence freshness

Pravidlá určujúce, či evidence stále patrí k aktuálnemu candidate, artifactu, policy a target environment stateu a ešte neprekročila definovanú expiráciu. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Integration decision

Autoritatívne rozhodnutie, či sa konkrétny candidate integration state môže bezpečne pridať k aktuálnej mainline na základe complete a fresh evidence. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Mainline

Spoločná integračná línia, typicky `main`, reprezentujúca najaktuálnejší dôveryhodný integrovaný stav projektu. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Merge queue

Mechanizmus vytvárajúci a overujúci kandidátov proti predpokladanému budúcemu mainline stavu v kontrolovanom poradí, aby zabránil stale-green merge race-u. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Merge-result pipeline

Pipeline overujúca synthetic alebo reálny výsledok spojenia source zmeny s aktuálnym targetom namiesto samotného source branch tipu. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Pipeline cache

Dočasné znovupoužiteľné dáta určené na zrýchlenie pipeline, napríklad dependencies alebo compiler outputs. Cache nie je release artifact ani source of truth. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Promotable artifact

Immutable artifact, ktorého identity, evidence, configuration compatibility a recovery preconditions spĺňajú promotion policy pre ďalší environment. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Protected environment

Environment s obmedzenou deployment identitou, approval alebo policy pravidlami a auditom, používaný najmä pre produkciu a citlivé stages. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Reproducible build

Build proces, pri ktorom rovnaké explicitné vstupy a toolchain vytvoria rovnaký alebo ekvivalentný výsledný artifact. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Risk-based deployment

Rollout policy, ktorá mení exposure, observation window, human boundary alebo recovery mechanizmus podľa business criticality, blast radiusu a compatibility rizika konkrétnej zmeny. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Rollout state machine

Explicitné produkčné rollout states a povolené transitions od candidate eligibility cez bounded exposure po promotion, pause, abort a recovery. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Runner isolation

Oddelenie CI jobov, workspace, credentials, cache a execution environmentov tak, aby sa obmedzil cross-project contamination a persistence nedôveryhodného stavu. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Separation of duties

Rozdelenie právomocí tak, aby citlivú zmenu nevytvorila, neschválila a nenasadila bez nezávislej kontroly jediná identita; môže byť implementované automatizovanými policy a approvals. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Time to first useful feedback

Čas od vzniku alebo odoslania zmeny po prvý relevantný, diagnostikovateľný a akčný výsledok pipeline. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).