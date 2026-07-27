# Upgrade a rollback

Helm upgrade je riadený prechod z jednej release generation do druhej. Nevymieňa iba image tag. Mení kombináciu chart artifactu, dependency graphu, effective values, rendered manifests, hooks, Kubernetes objects a často aj durable alebo external state.

Rollback je ďalší release transition. Nie je to návrat času. Vie znovu použiť historický Helm release state, ale automaticky nevracia databázu, queue, CRD storage, external API side effects, DNS, IAM ani obsah PVC.

## 1. Dominantný lifecycle

```text
change intent a recovery objective
→ current release subject
→ target release subject
→ compatibility a side-effect inventory
→ effective values a target render
→ semantic diff a precondition gate
→ hooks a release mutation
→ Kubernetes reconciliation
→ technical a business acceptance
→ rollback/roll-forward/compensation/restore decision
→ recovery verification
→ revision evidence a old-state retirement
```

Upgrade je bezpečný iba vtedy, keď vieš odpovedať:

```text
čo sa mení
kto je authoritative writer
ktoré side effects sú durable
ktorý predchádzajúci stav je ešte kompatibilný
ako sa overí pôvodný business outcome
```

## 2. Atlas revision subjects

Po úspešnom dokončení predchádzajúceho hook incidentu je current state:

```text
release: payments-prod
current revision: 19
chart artifact: CH57
dependency lock: D57
values bundle: V57
rendered manifest: M57
image digest: I57
database schema: S13
event contract: E1
```

Target upgrade:

```text
target revision: 20
chart artifact: CH58
dependency lock: D58
values bundle: V58
rendered manifest: M58
image digest: I58
database schema target: S14
event contract target: E2
cluster generation: K136
```

Release transition subject:

```text
payments-prod
+ source revision 19
+ target revision 20
+ source/target chart, dependency, values a manifest digests
+ source/target image digests
+ hook operation IDs
+ data/schema/event generations
+ target cluster/context/namespace
+ deployment engine a Helm version
```

Samotné číslo revision nestačí na recovery rozhodnutie.

## 3. Release revision model

Helm history môže obsahovať stavy ako:

- `deployed`;
- `superseded`;
- `failed`;
- `pending-install`;
- `pending-upgrade`;
- `pending-rollback`;
- `uninstalling`.

```bash
helm history payments-prod -n production
helm status payments-prod -n production
```

Helm revision nie je:

```text
Git commit
chart version
application version
Deployment revision
database schema generation
event contract generation
```

Koreláciu vytvor cez labels, annotations, artifact digests, operation IDs a deployment evidence.

## 4. Upgrade input closure

Výsledok upgrade-u môže závisieť od:

```text
chart artifact a digest
dependency lock a packaged dependencies
default values
previous release values
new values files a CLI overrides
values merge mode
release name/namespace/revision context
Capabilities a live lookup
post-renderer
Helm version a plugins
target API/admission state
```

Reprodukovateľný upgrade potrebuje immutable input closure. Príkaz bez zachovaných inputs nie je release evidence.

## 5. Values transition

### Explicitný values contract

Preferovaný production model:

```bash
helm upgrade payments-prod oci://registry.example.com/charts/payments \
  --version 1.6.0 \
  -f values/common.yaml \
  -f values/production.yaml \
  --namespace production
```

Effective values bundle `V58` má byť archivovaný bez plaintext secrets a viazaný na source revisions.

### `--reuse-values`

Reuse prenáša predchádzajúce release values a pridáva nové overrides. To môže ponechať:

- odstránené legacy keys;
- staré boolean flags;
- staré subchart enablement;
- values, ktoré nový chart už nezdokumentuje;
- cluster-history-dependent configuration.

### Reset modes

Reset môže naopak odstrániť historické customizations. Presné flags a merge semantics viaž na používanú Helm major/minor verziu.

Pred upgrade vždy porovnaj:

```text
current stored effective values
new chart defaults
explicit target overrides
resulting target effective values
```

## 6. Current, target a live state

Pred zmenou zachovaj tri baseline-y:

```text
current Helm release manifest
current live Kubernetes objects
proposed target rendered manifest
```

Príkazy:

```bash
helm get values payments-prod -n production --all
helm get manifest payments-prod -n production
helm get hooks payments-prod -n production
helm status payments-prod -n production
kubectl get deployment,replicaset,pod,service,endpointslice,pvc -n production
```

Rozdiel medzi release manifestom a live objectom môže pochádzať z:

- server-side defaulting;
- mutating admission;
- HPA;
- operatora;
- GitOps controllera;
- manual emergency change;
- external secret/config reload controlleru.

Pred rollbackom urči authoritative writer pre každý relevantný field.

## 7. Precondition a recovery gate

Production upgrade nezačína renderom. Začína eligibility rozhodnutím:

```text
cluster/API health
+ release writer lock
+ capacity a failure-domain headroom
+ current SLO
+ compatible backup/recovery evidence
+ dependency a external-system health
+ target artifact availability
+ rollback/roll-forward eligibility
```

Ak prebieha incident, backup je neoverený alebo rollback target už nie je kompatibilný, upgrade nemá bezpečný recovery envelope.

## 8. Render a semantic diff

Minimálny chain:

```bash
helm dependency build ./chart
helm lint ./chart -f values-production.yaml
helm template payments-prod ./chart \
  -f values-production.yaml \
  --namespace production > rendered.yaml
kubectl apply --dry-run=server -f rendered.yaml
```

Semantic review musí odhaliť zmeny v:

- resource identity a names;
- selectors a ownership labels;
- image digestoch;
- ConfigMap/Secret references;
- Service ports a traffic policy;
- PVC, StorageClass a volume identity;
- RBAC a security context;
- hooks a external side effects;
- CRDs a controller compatibility;
- requests, limits, probes a rollout budgets.

Textový YAML diff sám nepreukazuje admission-resolved ani runtime state.

## 9. Upgrade execution chain

```text
target render M58
→ pre-upgrade hook operations
→ API create/update/delete requests
→ release object/status transition
→ Kubernetes controllers reconcile
→ Pods, volumes, network a endpoints realize
→ post-upgrade hooks/tests
→ technical acceptance
→ business acceptance
```

Každá boundary má vlastný failure model. Ak upgrade zlyhá pred API write-om, recovery je iná než po schema migration, partial rollout-e alebo external event publication.

## 10. Wait a timeout semantics

Wait contract musí definovať:

```text
ktoré resources sa sledujú
čo znamená ready
či sa čaká na Jobs
aký je operation timeout
aký application-level test nasleduje
```

Helm wait success nepreukazuje:

- správny image digest na každom serving Pode;
- process-loaded configuration;
- Service/edge traffic cohort;
- schema alebo event compatibility;
- user journey;
- absence duplicate side effects.

Timeout je observation deadline. Nie je root cause ani dôkaz, že operácia neprebehla.

## 11. Automatic failure recovery

Moderné Helm command surfaces môžu ponúkať automatic rollback behavior, napríklad version-dependent `--atomic` alebo `--rollback-on-failure` model.

Takáto funkcia môže:

- aplikovať predchádzajúci release manifest;
- vytvoriť ďalšiu rollback revision;
- vykonať rollback hooks;
- odstrániť vybrané newly-created resources podľa flags.

Neobnoví automaticky:

- database schema/data;
- queue messages;
- emitted events;
- external API transactions;
- CRD stored objects;
- PVC content;
- DNS/IAM/cloud resources mimo release;
- credentials už načítané consumerom.

Automatic rollback je bezpečný iba po preukázaní compatibility predchádzajúcej application generation s current durable state-om.

## 12. Manual rollback subject

```bash
helm history payments-prod -n production
helm rollback payments-prod 19 -n production --wait --timeout 15m
```

Rollback vytvorí novú revision. Cieľový subject musí obsahovať:

```text
target historical release revision
chart/dependency/values/manifest identity
referenced images a ich availability
expected hooks
API/CRD compatibility
current data/schema/event generation
current Secrets/certificates/external APIs
```

Historická revision je len kandidát. Nie automaticky validný recovery state.

## 13. Rollback compatibility matrix

Pred rollbackom zostav minimálne:

```text
old app × current schema
old app × current event backlog
old app × current external API
old app × current credential epoch
old manifests × current Kubernetes APIs
old controller × current CRD storage version
```

Verdict môže byť:

- **eligible** — predchádzajúci stav je kompatibilný;
- **eligible with compensation** — potrebuje external cleanup alebo data reconciliation;
- **not eligible** — rollback by poškodil alebo nedokázal spracovať current state;
- **unknown** — chýba evidence, preto rollback nie je bezpečný default.

## 14. Roll-forward, compensation a restore

### Rollback

Vhodný, keď:

- current durable state je backward-compatible;
- side effects sú nulové alebo reverzibilné;
- artifacts a dependencies sú dostupné;
- návrat je najmenší bezpečný change.

### Roll-forward

Vhodný, keď:

- schema alebo event contract už nie je backward-compatible;
- external migration dokončila;
- malý fix obnoví správny desired state;
- rollback hooks alebo old application predstavujú väčšie riziko.

### Compensation

Použi pri external side effecte, ktorý sa nedá „rollbacknúť“ manifestom:

```text
duplicate message
external registration
payment authorization
DNS/IAM change
```

### Restore

Restore je disaster-recovery operácia nad dátami alebo control plane-om. Nie je synonymum Helm rollbacku a vyžaduje vlastný RPO/RTO, fencing a reconciliation model.

## 15. Force replacement boundary

Delete/recreate alebo `--force`-like behavior môže zmeniť identity a spustiť external side effects.

Rizikové subjects:

- Service/LB identity;
- StatefulSet a PVC;
- immutable selectors;
- CRDs;
- resources s finalizers;
- objects sledované external controllerom;
- webhook alebo APIService.

Immutable-field failure je požiadavka na explicitný migration/decommission flow, nie signál na univerzálny force.

## 16. CRD a controller transition

CRD lifecycle nie je automaticky symetrický s Helm release history.

Over:

```text
served versions
storage version
conversion webhook
stored-version migration
controller version skew
custom resource backup
rollback eligibility
```

Old chart rollback môže nasadiť controller, ktorý current stored objects alebo schema už nevie čítať.

## 17. Stateful a data-bearing resources

Helm revision nevlastní obsah PVC ani application membership.

Pred transition analyzuj:

- data generation;
- writer/fencing epoch;
- quorum a version skew;
- storage snapshot a restore test;
- protocol/schema compatibility;
- ordered/partitioned rollout;
- retained PVC a rollback semantics.

Manifest rollback pri stále aktívnom novom writeri môže vytvoriť split-brain alebo stale writer.

## 18. Pending operation a unknown outcome

`pending-upgrade` alebo `pending-rollback` môže znamenať:

- klient bol prerušený;
- API response sa stratila;
- hook stále beží;
- release storage write zlyhal;
- iný writer spustil operáciu;
- resource mutation prebehla iba čiastočne.

Recovery:

1. zachovaj release storage a hook evidence;
2. identifikuj source a target revision subjects;
3. over, či Helm process alebo hook stále beží;
4. porovnaj release manifest, live objects a external state;
5. urč completed, partial alebo unknown operations;
6. až potom vykonaj rollback, roll-forward alebo compensation.

Ručná editácia release Secrets je posledný version-specific recovery krok, nie prvá oprava.

## 19. Concurrent writers

Možní writers:

```text
Helm CLI/pipeline
GitOps controller
kubectl apply/patch
operator
HPA/VPA
external secret/config controller
```

Definuj authoritative ownership na úrovni fields a lifecycle operations. Inak rollback môže prepísať legitímnu novšiu zmenu alebo GitOps okamžite vráti rollback späť.

## 20. Worked incident — technický rollback, business failure

Atlas Payments prechádza z revision 19 na 20.

Target changes:

```text
image I57 → I58
schema S13 → S14 cez expand migration
outbound event E1 → E2
new consumer config generation C58
```

Pre-upgrade migration dokončí S14. Časť nových Podov začne publikovať E2. Rollout sa potom zastaví, pretože C58 neobsahuje required endpoint pre fraud service. Automatic failure recovery obnoví manifests revision 19.

Helm status novej rollback revision je `deployed`, no payment backlog rastie.

### Subject

```text
source release revision 19
failed target revision 20
rollback revision 21
hook operation schema-expand/20
current schema S14
queue contains E1 aj E2
serving application cohort I57
```

### Konkurenčné hypotézy

1. rollback manifest sa neaplikoval;
2. old image I57 nie je dostupný;
3. Pody revision 19 neprešli readiness;
4. old app nevie pracovať so schema S14;
5. old consumer nevie dekódovať E2 backlog;
6. Service/EndpointSlice stále smeruje na I58 cohortu;
7. rollback hook znovu spustil side effect;
8. queue lag pochádza z nezávislého broker incidentu.

### Diskriminačné observation points

```text
helm history a manifests revisions 19/20/21
Pod UIDs a image digests
EndpointSlice targetRef cohort
schema generation a migration ledger
queue event-version distribution
effective consumer config
application decode errors a broker health
```

Finding:

```text
revision 21 manifests a Pody I57 sú current
EndpointSlice smeruje iba na I57
schema S14 je backward-compatible
E2 backlog nie je kompatibilný s I57 consumerom
broker je healthy
```

Helm rollback bol technicky úspešný. Recovery state však nebol business-compatible.

### Containment

- zastaviť ďalšie automatic retries/rollbacks;
- pozastaviť E2 producers;
- zachovať mixed queue evidence;
- nevymazávať E2 messages;
- udržať payment API v degradovanom, ale konzistentnom režime;
- zablokovať contract schema cleanup.

### Recovery decision

Rollback nie je eligible kvôli E2 backlogu. Zvolený je roll-forward:

1. opraviť missing fraud endpoint v C58;
2. vytvoriť I58.1 s tolerantným E1/E2 consumerom;
3. renderovať a server-validate revision 22;
4. nasadiť bounded cohortu;
5. drainovať mixed backlog;
6. overiť idempotency a payment ledger;
7. rozšíriť rollout;
8. až potom retirement I57/E1 compatibility.

### Verification

```text
release revision 22 deployed
serving image digest I58.1
schema S14
queue lag sa vracia na baseline
E1 aj E2 events sú spracované presne raz
payment P-884 má jednu ledger transakciu
forbidden: žiadny E2 decode failure
forbidden: žiadna duplicate authorization
```

### Earlier controls

- event expand/contract compatibility;
- old/new application × old/new event contract matrix;
- canary s reálnou queue cohortou;
- automatic rollback eligibility gate;
- rollout stop pred E2 exposure;
- business SLI a queue-version telemetry.

## 21. Failure boundaries

### `--reuse-values` zachová legacy behavior

Source chart odstráni key, ale stored release values ho cez compatibility helper stále aktivujú. Target render sa líši od Git-intent.

### Helm timeout, rollout neskôr dokončí

Release je failed, no Kubernetes controller pokračuje. Retry bez kontroly live generation môže vytvoriť ďalší revision transition nad už zmeneným state-om.

### Rollback target odkazuje na odstránený image

Historický manifest existuje, artifact nie. Rollback nie je reprodukovateľný.

### CRD rollback bez storage compatibility

Old controller sa spustí, ale nevie dekódovať current custom resources.

### GitOps vráti rollback

Helm rollback zmení live object, GitOps authoritative desired state ho okamžite znovu nastaví na failed target revision.

## 22. Release transition evidence

Pre každú production zmenu archivuj:

```text
source a target release subjects
effective values
target rendered manifest a digest
semantic diff
hooks a operation IDs
server/admission validation
current/target image digests
schema/event/config generations
technical a business acceptance
recovery eligibility verdict
final revision a closure evidence
```

Release history v clustri nie je jediný disaster-recovery source.

## 23. Kontrolné otázky

1. Čo tvorí immutable source a target release subject?
2. Prečo rollback vytvára novú revision namiesto návratu histórie?
3. Aký je rozdiel medzi stored release values a explicitným target values contractom?
4. Čo Helm wait preukazuje a čo nepreukazuje?
5. Ako sa určuje rollback eligibility?
6. Prečo manifest rollback nevracia schema, queue alebo PVC state?
7. Kedy je bezpečnejší roll-forward?
8. Prečo pending operation predstavuje unknown outcome?
9. Ako concurrent writer mení rollback semantics?
10. Ktoré original a forbidden outcomes musí recovery overiť?

## Glossary impact

Relevantné pojmy: Helm release transition subject, source release generation, target release generation, upgrade input closure, recovery eligibility gate, rollback compatibility matrix, technical rollback, business-compatible recovery, pending operation unknown outcome, release compensation, Helm roll-forward a release transition closure.

## Oficiálna dokumentácia

- [helm upgrade](https://helm.sh/docs/helm/helm_upgrade/)
- [helm rollback](https://helm.sh/docs/helm/helm_rollback/)
- [helm history](https://helm.sh/docs/helm/helm_history/)
- [helm status](https://helm.sh/docs/helm/helm_status/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Hooks](hooks.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Helm testing a troubleshooting →](helm-testing-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
