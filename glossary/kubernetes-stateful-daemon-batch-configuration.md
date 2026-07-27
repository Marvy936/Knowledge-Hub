# Kubernetes stateful, DaemonSet, batch and configuration glossary entries

Tento section-specific doplnok rozširuje existujúce Kubernetes glossary súbory o identity, lifecycle a recovery pojmy použité pri strict revalidation kapitol StatefulSet, DaemonSet, Job a CronJob a ConfigMap a Secret.

## Application-aware readiness — stateful workload

Readiness verdict odvodený z application role, synchronization, membership, data generation a client-serving capability, nie iba z otvoreného portu alebo živého processu. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Batch acceptance verdict

Dôkaz, že logical run má canonical durable result, všetky work items majú explicitný stav, duplicate alebo partial side effects boli reconciled a nasledujúci run je bezpečný. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Batch fencing epoch

Monotónna alebo lease-based authority generation určujúca, ktorý worker smie konať nad konkrétnym logical runom alebo work itemom po retry, timeout-e alebo ownership transition. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Batch result ledger

Authoritative durable záznam logical runs, work items, operation IDs, checkpoints a accepted výsledkov, odlišný od Kubernetes Job statusu. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Bootstrap capability gate

Podmienka, ktorá drží nový Node mimo bežného workload scheduling-u, kým critical DaemonSet capabilities neprejdú node-local canary a acceptance testom. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Catch-up budget — CronJob

Policy obmedzujúca počet, concurrency a downstream load missed scheduled runs spustených po controller alebo control-plane recovery. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Checkpoint subject — batch

Versionovaný durable progress state jedného logical runu, partition alebo work itemu spolu s owner epoch, input generation a result lineage. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Completion-index mapping

Deterministická väzba Indexed Job completion indexu na business partition alebo work-item identity, typicky scoped logical run key-om. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Configuration acceptance verdict

Dôkaz, že správny ConfigMap/Secret subject bol doručený a processom načítaný, schema a business test prešli a forbidden old alebo fallback state už nie je aktívny. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Configuration lifecycle subject

Spoločná identita source generation, API object UID/version, workload template reference, Pod UID, delivery method, process-loaded generation a acceptance/cleanup state-u. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Configuration observation matrix

Mapovanie source, API object, Pod delivery, process state, security, rotation, readiness a business boundaries na ich subjects a observations. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Configuration rollout digest

Deterministická neplaintextová identity configuration contentu vložená do workload template-u alebo release manifestu s cieľom vytvoriť explicitnú Pod rollout generation. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Configuration source generation

Versionovaný approved input configuration pred vytvorením Kubernetes API objectu, napríklad Git commit, rendered manifest alebo external provider version. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Credential revocation verdict

Dôkaz, že nový credential je načítaný a funkčný, starý credential bol zrušený u authoritative providera a pokus o jeho použitie zlyhá. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Credential rotation subject

Identita old/new credentialov, provider state-u, Secret objects, consumer Pod generations, overlap window, loaded-state evidence a revocation/cleanup verdictu. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## DaemonSet acceptance verdict

Dôkaz, že každý eligible Node má správnu agent revision a effective authority, capability canary prešiel, misscheduled alebo stale host state neexistuje a workload outcome je správny. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## DaemonSet fleet-capability subject

Spoločná identita DaemonSet UID/generation, eligible Node inventory, per-Node Pods, host authority, node-local capability generations a fleet rollout verdictov. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## DaemonSet rollout ring

Bounded subset Nodes vybraný podľa poolu, zone alebo risk class pre staged rollout a capability/business verification pred rozšírením na ďalší fleet segment. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Data generation — stateful workload

Versionovaná identita on-disk alebo replicated data state-u vrátane cluster ID, snapshot/restore lineage, format version a replication position. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Eligible-Node inventory

Versionovaný zoznam Node UIDs a attributes, ktoré podľa aktuálnej DaemonSet placement a authorization policy majú dostať node-local Pod. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Environment-snapshot boundary

Prechod pri vytvorení container processu, keď ConfigMap/Secret values vložené cez environment tvoria nemenný process environment a neskorší API update ich nezmení. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Fencing epoch — stateful workload

Authority term alebo generation, ktorá odlišuje aktuálneho oprávneného writera/membera od stale processu s rovnakým ordinalom alebo storage identity. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Fleet observation matrix

Mapovanie DaemonSet fleet policy, placement, runtime, host authority, node capability, rollout, bootstrap a workload outcome boundaries na ich subjects. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Headless-Service discovery generation

Versionovaný inventory DNS records, Pod UIDs/IPs a publication state-u poskytovaný headless Service pre konkrétnu stateful workload generation. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Host-authority subject — DaemonSet

Effective kombinácia process credentials, capabilities, namespaces, host mounts/sockets, devices, RBAC, network egress a node/cloud identity dostupná node-agent Podu. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Logical batch run subject

Identita jednej finite business operation zahŕňajúca run key, schedule alebo trigger, Job UID, template/input generation, work inventory a canonical result. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Missed-schedule inventory

Zoznam CronJob scheduled timestamps, ktoré neboli vytvorené alebo dokončené, spolu s eligibility, deadline a catch-up rozhodnutím. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Node acceptance generation

Versionovaný verdict, že konkrétny Node UID po bootstrap-e, update-e alebo reboot-e poskytuje požadované DaemonSet capabilities a môže prijímať workload. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Node capability generation

Konkrétna per-Node verzia agent processu, host configuration, loaded programs/rules, sockets a registration state-u poskytujúca jednu platformovú capability. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Ordinal replacement subject

Old/new Pod UID, Node, IP, PVC/PV/backend volume, application member a fencing transitions pre jeden stabilný StatefulSet ordinal. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Ordinal slot — StatefulSet

Stabilná logical position identifikovaná ordinalom a predvídateľným Pod/DNS menom; replacement zachová slot, ale vytvorí nový Pod process subject. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Per-Node capability canary

End-to-end test node-local capability, napríklad sandbox create, Service flow, volume publish alebo telemetry delivery, ktorý je silnejší než agent liveness/readiness. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Per-Node placement subject

Väzba DaemonSet UID/generation, Node UID, Pod UID, admitted placement spec a current revision pre jeden eligible Node. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Per-ordinal storage identity

Väzba StatefulSet ordinalu na PVC UID, PV, backend volume, filesystem a data generation. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Pod-delivered configuration

Konkrétna environment alebo filesystem projection generation sprístupnená jednému Pod/container subjectu, odlišná od latest API objectu aj process-loaded state-u. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Process-loaded configuration epoch

Application-reported generation configuration alebo credentialu, ktorú process parsoval a aktívne používa pre nové operations alebo connections. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Projection generation

Konkrétna ConfigMap/Secret content generation materializovaná kubeletom v projected volume na jednom Node-e a Pode. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Replay identity — batch

Explicitná identita operátorského alebo recovery replay-u viazaná na pôvodný logical run bez kolízie so scheduled runom. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Result-commit invariant

Pravidlo, že process môže skončiť exit code 0 až po durable result commit-e a overení business invariantov. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Retained-PVC reuse boundary

Preflight rozhodnutie, či PVC zachovaný po StatefulSet scale-down-e obsahuje správny cluster/member/data state a môže byť bezpečne použitý pri scale-up-e. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Rollback credential eligibility

Verdikt, či credential požadovaný starou application/config generation ešte môže byť bezpečne použitý; je oddelený od artifact alebo configuration rollback eligibility. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Same-node coexistence contract

Dôkaz, že dve DaemonSet revisions môžu na jednom Node-e súčasne bezpečne zdieľať alebo koordinovať host ports, sockets, locks, devices a host state počas surge. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Scheduled-run identity

Jednoznačná identita CronJob schedule instance, typicky UTC timestamp alebo business interval spolu s CronJob UID/generation a logical run key. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Secret access graph

Inventory priamych aj nepriamych paths k Secret plaintextu cez API verbs, Pod/Job creation, workload edits, exec/debug, node access, backups a external caches. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Stateful acceptance verdict

Dôkaz správnej ordinal/Pod/storage/member väzby, fencing-u, quorum/synchronization, client endpoints, data lineage, backup/restore a business outcome-u. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stateful decommission subject

Versionovaný application-aware scale-down alebo removal transition zahŕňajúci leadership, traffic drain, membership, data redundancy, Pod termination a storage retention. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stateful membership subject

Identita application clusteru, member IDs, ordinal mappings, roles, leader term, quorum view, replication positions a fencing epochs. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stateful observation matrix

Mapovanie StatefulSet controller, ordinal, DNS, storage, membership, revision, readiness, retention a business boundaries na ich subjects a evidence. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stateful scale transition

Application-aware pridanie alebo odstránenie ordinalu spolu s membership join/leave, rebalance, leadership, quorum, Pod a PVC lifecycle-om. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## StatefulSet lifecycle subject

Spoločná identita StatefulSet UID/generation, revisions, ordinal slots, Pod UIDs, DNS, PVC/PV/backend data, application membership a acceptance state-u. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## `subPath` staleness boundary

Delivery boundary, pri ktorej file mount cez `subPath` typicky nesleduje priebežné ConfigMap/Secret projection updates a zostáva viazaný na pôvodný mounted file subject. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## TTL evidence gate — Job

Podmienka, že Kubernetes TTL cleanup sa môže vykonať až po externalizácii logs, result manifestu, checkpoints, operation IDs a incident evidence. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Unknown batch outcome

Stav, keď worker nevie, či external side effect neprebehol, prebehol čiastočne alebo uspel bez result commit-u; pred retry vyžaduje lookup podľa stable operation identity. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Work-item claim

Bounded ownership record jedného batch itemu s worker/run identity, lease alebo visibility timeoutom, fencing epoch a acknowledgment/checkpoint state-om. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).
