# Helm release testing and CKA glossary entries

## Automatic rollback — Helm

Release behavior, pri ktorom Helm po failed upgrade-e vytvorí rollback na predchádzajúcu úspešnú revision podľa version-specific flags; nevracia automaticky databázové ani external side effects. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## CKA

Certified Kubernetes Administrator, performance-based Linux Foundation/CNCF certifikácia overujúca praktickú správu a troubleshooting Kubernetes clusterov. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## CKA troubleshooting drill

Časovo ohraničený fault-injection scenár merajúci root-cause accuracy, minimálnu opravu a hard validation Kubernetes failure-u. Pozri [CKA troubleshooting drills](docs/10-helm-and-cka/cka-troubleshooting-drills.md).

## Chart CI pipeline — Helm

Versionovaný validačný workflow od dependency locku, values schema, render matrix a policy checks cez ephemeral cluster install, `helm test`, upgrade/rollback scenár až po publikovanie immutable chart artifactu. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Chart test hook — Helm

Helm test resource spúšťaný príkazom `helm test`, ktorý overuje konkrétny release invariant a reportuje výsledok cez exit status. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Command fluency — CKA

Schopnosť rýchlo a presne používať kubectl, shell, editor a cluster administration commands bez zbytočného hľadania syntaxe. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Diagnosis time — CKA drill

Čas od začiatku troubleshooting scenára po správne pomenovanie root cause na základe dôkazov. Pozri [CKA troubleshooting drills](docs/10-helm-and-cka/cka-troubleshooting-drills.md).

## Domain-weighted lab — CKA

Timed lab, ktorého bodové rozdelenie zodpovedá aktuálnym oficiálnym CKA curriculum doménam namiesto rovnomerného alebo náhodného mixu tém. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Effective release values — Helm

Výsledná values konfigurácia po zlúčení chart defaults, predchádzajúceho release state-u podľa zvolenej stratégie, values files a CLI overrides. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Ephemeral chart test cluster

Dočasný Kubernetes cluster používaný na realistické install, upgrade, rollback, test a uninstall overenie chart artifactu. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Exam simulation — CKA

Plný časovo a pravidlami ohraničený tréning napodobňujúci performance-based exam workflow bez používania dôverných reálnych exam otázok. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Expand/contract migration

Backward-compatible database alebo API migration pattern, ktorý najprv pridá nový model, následne rolloutne kompatibilný software a až v neskoršom kroku odstráni starú kompatibilitu. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Failure-domain narrowing — CKA

Postupné zužovanie incidentu z clusteru, Node-u, workloadu, Podu alebo containeru na konkrétny owner component a failure layer. Pozri [CKA troubleshooting drills](docs/10-helm-and-cka/cka-troubleshooting-drills.md).

## Fault injection — CKA lab

Kontrolované zavedenie jednej alebo viacerých známych porúch do disposable lab prostredia na tréning diagnostiky a recovery. Pozri [CKA troubleshooting drills](docs/10-helm-and-cka/cka-troubleshooting-drills.md).

## Hard validation — CKA

Explicitný command alebo observable criterion dokazujúci, že úloha spĺňa požadovaný stav a constraints, nie iba že resource existuje. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Helm drift triage

Porovnanie posledného release manifestu, navrhovaného renderu a live Kubernetes objectu na identifikáciu authoritative writera a zdroja rozdielu. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm rollback

Operácia vytvárajúca novú release revision podľa historickej revision; nepredstavuje automatický návrat durable alebo external state-u. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Helm test pyramid

Viacvrstvový chart validation model od metadata, schema a render checks cez server validation až po ephemeral cluster, test hooks a application end-to-end testy. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm troubleshooting decision tree

Rozdelenie Helm incidentu na fetch/dependency, values/schema, render, API/admission, hook, release-state, wait alebo následný Kubernetes workload failure. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm upgrade

Operácia vytvárajúca novú release revision z chartu, dependencies, effective values a render contextu a aplikujúca výsledný manifest do clusteru. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Imperative skeleton — CKA

Rýchlo vygenerovaný Kubernetes manifest cez imperative kubectl command s `--dry-run=client -o yaml`, ktorý sa následne deklaratívne upraví a aplikuje. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Pending rollback — Helm

Release status signalizujúci nedokončenú rollback operáciu, typicky prebiehajúcu alebo prerušenú pri hooku, API requeste, wait-e alebo release storage update. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Pending upgrade — Helm

Release status signalizujúci nedokončenú upgrade operáciu; pred recovery vyžaduje kontrolu hooks, Jobs, client concurrency, live resources a release evidence. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Release evidence — Helm

Súbor dôkazov zahŕňajúci release history, status, values, rendered manifest, hooks, artifact identity a live Kubernetes stav. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Release history retention — Helm

Policy určujúca počet a dobu uchovania Helm revisions s trade-offom medzi rollback targets, forensic evidence, Secret exposure a etcd storage. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Roll-forward

Recovery stratégia nasadzujúca novú opravenú revision namiesto návratu na starú, vhodná najmä pri nereverzibilných alebo už dokončených durable side effects. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Rollback compatibility

Schopnosť predchádzajúcej application/chart revision bezpečne fungovať s aktuálnou databázovou schema, CRDs, Secrets, APIs, storage a external state-om. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Self-grading — CKA

Hodnotenie lab úloh cez explicitné validation commands, partial-credit criteria, čas a bezpečnosť namiesto subjektívneho dojmu. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Skip-and-return strategy — CKA

Time-management postup, pri ktorom kandidát preskočí úlohu bez jasnej rýchlej cesty, označí ju a vráti sa po získaní jednoduchších bodov. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Task intake protocol — CKA

Krátky parsing úlohy na cluster/context, namespace, resource identity, požadovanú zmenu, constraints a validation criterion pred vykonaním commandov. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Timed lab — CKA

Praktický Kubernetes lab vykonávaný s pevným časovým limitom, bodovaním a povinnou validáciou na tréning exam execution schopností. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Upgrade health gate — Helm

Súbor pre-upgrade a post-upgrade podmienok nad clusterom, workloadom, dependencies, capacity, backups a observability, ktoré musia byť splnené pred pokračovaním release-u. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Values test matrix — Helm

Sada reprezentatívnych values kombinácií vrátane defaults, production variantov, enabled/disabled features a explicitných empty hodnôt používaná na chart render a policy testovanie. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Verification pass — CKA

Vyhradená záverečná časť timed labu, počas ktorej sa všetky úlohy znovu overia cez hard validation a context kontrolu. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).
