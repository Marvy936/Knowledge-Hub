# CKA timed execution and troubleshooting terminology

## CKA exam subject

Versionovaný certification a environment contract obsahujúci exam delivery model, čas, Kubernetes minor version, domain weights, povolené referencie a dátum overenia oficiálnych pravidiel.

## Timed-lab generation

Konkrétna verzia tréningového prostredia, task setu, fault injectors, scoring rules, hard validations a reset procedúr.

## Task subject — CKA

Exact kombinácia cluster contextu, namespace-u alebo hostu, resource/component identity, current generation, požadovanej zmeny, constraints, forbidden changes a validation criterion.

## Task intake protocol

Krátky pre-mutation záznam contextu, namespace-u, subjectu, desired change, hard constraints, forbidden changes, validation a časového budgetu.

## Current-state observation — CKA

Minimálna evidence potrebná na odlíšenie initial state-u od zadania pred prvým write operation.

## Execution path — CKA

Najkratšia bezpečná séria generatorov, editácií, client/server validations a mutations vedúca k požadovanému state-u.

## Hard validation — CKA

Explicitný dôkaz, že resource/controller/runtime/application outcome spĺňa zadanie; object existence alebo jeden green status nestačia.

## Forbidden outcome — CKA

Stav, ktorý riešenie nesmie vytvoriť, napríklad zmena identity, broad authorization, vypnutie policy, strata availability alebo druhý storage writer.

## Score closure

Uzavretie tasku po hard validation, forbidden-outcome checku a zaznamenaní partial-credit alebo penalty evidence.

## Skip-and-return trigger

Vopred definovaná podmienka, pri ktorej kandidát zastaví neefektívnu alebo rizikovú úlohu, zachová subject/evidence/next observation a vráti sa neskôr.

## Unknown operation outcome — CKA

Stav po timeout-e alebo prerušení write operation, keď nie je známe, či API alebo external side effect prebehol; pred retry sa vyžaduje read-back.

## Domain-weighted lab blueprint

Rozdelenie taskov a bodov podľa aktuálnych CKA domain weights bez zredukovania cross-domain incidentov na izolované katalógy.

## CKA troubleshooting subject

Exact cluster/object/process/data/flow identity, ku ktorej patria symptóm, scope, timeline, owner graph, evidence a expected outcome.

## Expected-state contract — drill

Versionovaný initial a desired state vrátane fault injectionu, misleading evidence, forbidden changes, hard validation a reset procedúry.

## Failure-domain narrowing

Postup zmenšujúci možné príčiny podľa scope-u: container, Pod, workload, Node, request class alebo cluster.

## Evidence preservation — CKA

Zachovanie object YAML, status/conditions, Events, current/previous logs, host/runtime state a časovej identity pred restartom, delete alebo force zásahom.

## Competing hypothesis set — CKA

Malý súbor realistických kauzálnych vysvetlení viazaných na rovnaký incident subject.

## Discriminating observation — CKA

Pozorovanie alebo test, ktorý významne odlíši competing hypotheses bez zmeny viacerých vrstiev naraz.

## Containment — CKA drill

Dočasné obmedzenie blast radiusu a ďalších writerov pri zachovaní evidence a funkčnej healthy cohorty.

## Authoritative repair — CKA

Minimálna zmena na skutočnom source-of-truth alebo owner boundary, po ktorej môže systém znovu skonvergovať.

## Reconvergence verdict

Dôkaz, že controller, kubelet/runtime, dataplane alebo external system po repair-e dosiahli požadovanú current generation.

## Adjacent-cohort verification — CKA

Overenie, že oprava funguje aj na relevantných Nodes, Pods, endpoints alebo failure domains mimo jediného testovaného subjectu.

## Contributing control failure — CKA

Sekundárny problém, ktorý zhoršil detekciu, blast radius alebo recovery, ale nebol primárnym root cause-om.

## Fault-injection generation

Versionovaný mechanizmus vytvárajúci jednu presnú authoritative chybu s deterministickým apply/reset a známym expected state-om.

## Drill score closure

Vyhodnotenie root-cause accuracy, minimal repair, validation, evidence safety a času ako oddelených výsledkov.

## Targeted follow-up drill

Nový drill odvodený z konkrétnej chyby, napríklad pomalého scope narrowing, context omylu, nebezpečného repairu alebo slabej validation.
