# CKA timed labs

CKA timed lab nie je zoznam príkazov vykonaný proti náhodnému clusteru. Je to meraný execution lifecycle, v ktorom kandidát musí správne identifikovať task subject, pozorovať current state, zvoliť minimálnu bezpečnú zmenu, zachovať explicitné constraints a preukázať exact outcome v časovom limite.

Tento materiál obsahuje originálne tréningové úlohy. Neobsahuje ani nereprodukuje dôverné otázky zo skutočnej skúšky. Cieľom je trénovať prenositeľný diagnosis a execution model, nie zapamätať si konkrétne názvy resource-ov alebo root causes.

## 1. Dominantný timed-task lifecycle

Každá úloha prechádza rovnakou state machine. Najprv sa fixne exam/lab generation, context, namespace a resource alebo host identity. Potom sa zistí current state a rozdiel voči zadaniu. Až následne sa zvolí najkratšia bezpečná execution path, vykoná bounded mutation a overí controller, runtime aj forbidden outcomes.

```text
exam/lab generation a časový budget
→ task intake a exact context/resource subject
→ current-state observation
→ hypothesis alebo desired-state delta
→ najkratšia bezpečná execution path
→ client/server validation
→ bounded mutation
→ controller/runtime convergence
→ hard validation požadovaného outcome-u
→ forbidden-change check
→ task closure, skip alebo návrat
```

Correctness, execution efficiency a verification discipline sa hodnotia spolu. Rýchla zmena bez dôkazu nie je uzavretá úloha. Správny manifest v nesprávnom context-e je chybný výsledok. Resource, ktorý funguje iba po odstránení požadovanej affinity, security alebo availability constraint, je partial alebo nesprávne riešenie.

## 2. Aktuálny exam subject

K 30. júlu 2026 je CKA online proctored performance-based skúška s trvaním dve hodiny a environmentom Kubernetes v1.35. Oficiálny blueprint uvádza domény Troubleshooting 30 %, Cluster Architecture, Installation and Configuration 25 %, Services and Networking 20 %, Workloads and Scheduling 15 % a Storage 10 %.

Exam generation je temporálne premenlivý subject. Linux Foundation aktualizuje environment a policies; pred reálnou skúškou sa preto znovu overujú certification page, curriculum, Candidate Handbook a Exam Tips. Tréningový blueprint má uvádzať dátum overenia a Kubernetes minor, aby staré API alebo domain assumptions neprežili potichu.

Timed labs nesmú kopírovať iba doménové percentá. Reálny incident často prechádza workloadom, schedulingom, networkingom, storage a Node execution naraz. Váhy riadia rozdelenie bodov a tréningového času, nie poradie diagnosis krokov.

## 3. Lab generation a scoring contract

Reprodukovateľný lab subject obsahuje lab ID/generation, cluster image a Kubernetes minor, initial-state checksum, fault-injection manifest, tasks a body, časový limit, povolené references, per-task validation, partial-credit pravidlá a destructive-change penalties.

Bez exact initial state-u nie je možné odlíšiť chybu kandidáta od broken lab prostredia. Bez hard validation sa self-grading zmení na subjektívny pocit, že „resource vyzerá dobre“.

Bodovanie oddeľuje context/subject correctness, desired-state correctness, preservation constraints, convergence, hard validation a bezpečnosť/čas. Napríklad rollout task môže udeliť body za correct context a Deployment identity, exact image, strategy zachovávajúcu availability, converged rollout a explicitné overenie image aj available replicas. Kandidát tak vidí, či stratil body pre knowledge, execution alebo closure gap.

## 4. Task intake a context discipline

Pred prvým write príkazom sa z textu úlohy extrahuje cluster/context, namespace, exact resource alebo host, požadovaná zmena, hard constraints, forbidden changes, validation criterion a časový budget.

Context je súčasť task subjectu, nie stav UI. Na začiatku úlohy sa potvrdí current context a minified cluster/namespace. Pri host-level úlohe sa overí hostname a Node role. Stav terminálu z predchádzajúceho tasku sa nepovažuje za dôveryhodný.

Tento krátky intake zabraňuje jednej z najdrahších chýb: korektnej zmene vykonanej na rovnomennom resource-e v inom clustri alebo namespace. Shell prompt s contextom pomáha, ale nenahrádza explicitný read-back pred prvou mutáciou.

## 5. Observation pred mutation

Minimum evidence závisí od failure layeru. Pri existujúcom Kubernetes resource sa číta live YAML, describe a relevantné Events. Pri workloade sa zachová UID/generation, selector, owner graph, current image, strategy, Service relation, storage a security constraints.

Pri troubleshooting tasku sa pred editom pomenuje hypothesis alebo aspoň prvá divergentná boundary. Ak Pod nebeží, kandidát najprv odlíši scheduling, image pull, config, mount, runtime alebo probe failure. Zmena viacerých vrstiev naraz síce môže Pod rozbehnúť, ale zničí root-cause evidence a často poruší zadanie.

Observation má byť bounded. Timed exam nevyžaduje kompletný incident report; vyžaduje najmenší evidence set, ktorý diskriminuje pravdepodobné príčiny a chráni fungujúci state.

## 6. Execution path: imperative skeleton a declarative finish

Imperative príkazy sú efektívne, keď presne mapujú požadovanú zmenu: `set image`, `scale`, `label`, `taint`, `expose` alebo dry-run generátory. Pri multi-field resource-e je často rýchlejšie vytvoriť validný YAML skeleton, doplniť ho a použiť client a server dry-run pred apply.

Voľba nástroja sa odvodzuje od risku a complexity. Jednoduchý patch je vhodný pre exact field. Declarative file je vhodný, keď treba kontrolovať viac fields, zachovať evidence alebo opravu zopakovať. Pri Node/control-plane úlohe môže byť správna cesta systemd, static Pod manifest, certificate alebo etcd command namiesto Kubernetes object mutation.

Najkratšia cesta nie je tá s najmenším počtom znakov. Je to cesta s najnižším očakávaným časom vrátane opravy chýb a hard validation. Nečitateľný JSON patch, ktorý kandidát nevie okamžite skontrolovať, môže byť pomalší než krátky YAML edit.

## 7. Hard validation podľa vrstvy

Workload task sa uzatvára rollout statusom, live template image, ReplicaSet/Pod cohortou a required availability. Service task kontroluje selector, EndpointSlices a actual request; existencia ClusterIP nestačí. Storage task overuje PV/PVC relation, mount a podľa zadania read/write behavior; `Bound` nie je dôkaz funkčného volume v Pode.

RBAC validation používa positive aj negative `kubectl auth can-i`. Ak subject môže čítať Pody, forbidden check overí, že nemôže zapisovať alebo čítať Secrets, ak to zadanie nepovoľuje. NetworkPolicy testuje allowed aj denied source population. Scheduling test kontroluje assigned Node a zachovanie labels, taints, affinity/tolerations.

Node/control-plane task kombinuje cluster observation s host evidence ako kubelet status/logs, runtime containers, static Pod manifests alebo `/readyz`. Node `Ready` nepreukazuje, že konkrétna capability alebo fixed component funguje podľa zadania.

Hard validation číta live a effective state, nie iba local file alebo successful command exit code. API timeout po write-e vyžaduje read-back generation pred retry.

## 8. Časový control loop

Pre 120-minútový lab je vhodný krátky environment/context scan, prvý priechod cez high-confidence/high-value tasks, návrat k označeným úlohám a záverečné hard validations. Časové hranice nie sú dogma; ich účelom je zabrániť tomu, aby jedna nejasná úloha spotrebovala body dostupné inde.

Skip-and-return trigger nastáva, keď do približne 60–90 sekúnd nie je jasný execution path, environment sa odlišuje od contractu, operation outcome je unknown, ďalší pokus by bol deštruktívny alebo chýba prerequisite, ku ktorému sa dá vrátiť. Pred odchodom sa zaznamená subject, posledná evidence a ďalší diskriminačný command.

Návrat tak nezačína od nuly. Task sa dokončí alebo vedome nechá s partial creditom; chaotické opakované pokusy sú najhorší časový model.

## 9. Connected walkthrough: correct command v nesprávnom contexte

Úloha v lab-e `CKA-MIXED-42` generation `L42` požaduje v contexte `workload-a`, namespace `payments`, aktualizovať Deployment `api` generation 17 na image `I58`, nastaviť `maxUnavailable=1` a zachovať aspoň tri available replicas zo štyroch. Selector ani Service identity sa nesmú zmeniť.

Po rollout commande sa očakávaný resource nemení. Hypotézy sú wrong context, wrong namespace, GitOps/field writer reverting, blocked rollout alebo iný `api` workload. Prvý diskriminačný krok kontroluje current context a exact Deployment UID/generation/image.

Finding je, že terminál zostal v contexte `storage-b`, kde existoval Deployment rovnakého mena. Rollout diagnosis v `workload-a` preto zatiaľ nebol relevantný. Containment zastaví ďalšie changes v storage-b, zaznamená a bezpečne vráti neúmyselnú mutáciu podľa initial-state evidence a prepne na correct context.

V `workload-a` sa read-backne subject, pripraví exact image/strategy patch, vykoná server dry-run, apply a rollout observation. Closure potvrdí I58, `maxUnavailable=1`, rollout complete a available replicas aspoň tri. Forbidden check potvrdí, že storage-b resource, production selector a Service identity nezostali zmenené.

Earlier control je povinný context/task-intake read-back pred prvou mutation a context v shell prompt-e. Drill teda netrénuje iba `set image`, ale ochranu subject identity pod časovým tlakom.

## 10. Failure boundaries pri timed labs

Correct object môže mať wrong effective generation po admission alebo controller rewrite-e. Service môže existovať bez endpoints; PVC môže byť Bound bez mountu; RoleBinding môže splniť positive access a zároveň povoliť forbidden Secrets access. Minimálna oprava môže odstrániť affinity, toleration, request alebo policy, ktoré zadanie vyžaduje zachovať.

Unknown API outcome sa nereaguje blind retryom. Resource sa read-backne podľa UID/generation a až potom sa rozhodne o ďalšom write-e. Destructive shortcuts ako delete/recreate sú prípustné iba ak task explicitne umožňuje identity replacement a kandidát pozná následky.

Lab nesmie byť zapamätateľný podľa names/root causes. Generátor rotuje contexts, namespaces, resource identities, images, policies, symptoms a competing causes. Inak sa netrénuje diagnosis, ale pattern matching.

## 11. Domain-weighted blueprint a progresia

Full 100-point blueprint používa current domain weights, ale tasks sú kombinované. Originálne sety zahŕňajú rollout, ConfigMap projection, Service discovery, NetworkPolicy, PVC, RBAC, Node placement, zero-endpoint troubleshooting, control-plane inspection, previous logs, CronJob, HPA, StatefulSet/headless Service, ImagePullBackOff, hostNetwork DNS, drain, Gateway/Ingress a etcd snapshot.

Každá úloha má initial-state validation a hard-validation script. Laby postupujú od command fluency bez timeru cez krátke single-domain sprinty a mixed labs až po full 120-minute simulation. Posledná fáza minimalizuje nápovedu a reprodukuje exam time pressure bez kopírovania exam questions.

## 12. Self-grading a learning loop

Po lab-e sa každá strata bodov klasifikuje: knowledge gap, syntax, context/namespace, YAML/type, subject misidentification, unverified assumption, diagnosis delay, repair delay, missing validation, destructive attempt alebo time-management failure.

Action item je konkrétny drill. Context mistake vedie k sérii tasks s rovnakými resource names v rôznych clustroch. Missing validation vedie k positive/forbidden closure drillom. Slow diagnosis vedie k symptom-to-observation sprints. „Viac sa učiť“ nie je merateľná náprava.

Sledujú sa score percent, body za minútu, median task time, diagnosis/repair/verification time, skip-and-return success, context mistakes, invalid writes, tasks bez hard validation, forbidden violations a documentation lookup time. Cieľom je stabilná correctness pod časom, nie jeden výnimočný run.

## Kontrolné otázky

1. Čo tvorí exact timed-lab a task subject?
2. Prečo correct resource name nestačí bez context, UID a generation identity?
3. Ktoré facts sa extrahujú pred prvým write command-om?
4. Kedy je imperative command bezpečnejší než YAML a naopak?
5. Ako sa client/server validation líši od outcome validation?
6. Kedy task preskočiť a akú evidence zachovať?
7. Ako overiť positive aj forbidden outcome pre workload, network, storage a RBAC?
8. Ako sa výsledok labu premení na targeted drill?

## Praktické laby

Rozšírený vykonávací protokol a tréningové sety patria do [CKA labs](../../labs/cka/README.md).

## Glossary impact

Relevantné pojmy: CKA exam subject, timed-lab generation, task subject, intake protocol, current-state observation, execution path, hard validation, forbidden outcome, score closure, skip-and-return trigger, unknown operation outcome, domain-weighted blueprint a targeted drill.

## Primárne zdroje

- [Linux Foundation — Certified Kubernetes Administrator](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/)
- [Linux Foundation — CKA Program Changes and Domains](https://training.linuxfoundation.org/certified-kubernetes-administrator-cka-program-changes/)
- [Kubernetes — Tasks](https://kubernetes.io/docs/tasks/)
- [Kubernetes — kubectl reference](https://kubernetes.io/docs/reference/kubectl/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Helm testing a troubleshooting](helm-testing-troubleshooting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CKA troubleshooting drills →](cka-troubleshooting-drills.md)
<!-- KNOWLEDGE-NAVIGATION:END -->