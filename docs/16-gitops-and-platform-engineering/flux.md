# Flux

Flux je GitOps toolkit zložený z viacerých Kubernetes controllerov. Jeho úlohou nie je iba „sledovať Git a spustiť `kubectl apply`“. Flux vytvára reťaz oddelených reconciliation slučiek: jedna získava a identifikuje source artifact, ďalšia z neho zostaví desired manifests, ďalšia riadi Helm release a voliteľné image controllery zapisujú nový návrh desired state-u späť do Git-u.

Toto rozdelenie je dôležité pre diagnostiku aj bezpečnosť. Keď workload nebeží na očakávanej generation, nestačí skontrolovať, že `GitRepository` je `Ready`. Source môže byť správne stiahnutý, ale `Kustomization` môže zlyhať pri decryption, build-e, validation, apply alebo health checku. Rovnako môže byť `Kustomization` `Ready`, hoci business request stále používa stale runtime configuration, ktorú proces načítal iba pri štarte.

## 1. Dominantný model

```text
approved application alebo platform intent
→ exact Flux source a reconciliation subject
→ source-controller authentication a revision resolution
→ immutable in-cluster source artifact
→ Kustomization alebo HelmRelease desired-state calculation
→ decryption, substitution, build a API validation
→ service-account-scoped apply alebo Helm action
→ inventory, garbage collection a health assessment
→ effective workload a business verification
→ periodic drift correction, recovery a second-reconcile closure
```

Flux acceptance verdict preto nie je `Ready=True` na jednom Custom Resource. Musí korelovať exact source revision, artifact digest, controller generation, rendered object inventory, apply identity, live resources, workload generation a business outcome.

## 2. Flux nie je jeden controller

Flux používa GitOps Toolkit API a samostatné controllery s úzkymi responsibilities. Toto je odlišný mentálny model od jedného monolitického deployment procesu.

### `source-controller`

`source-controller` získava content z Git, OCI, Helm alebo bucket source-u. Overí source definition, autentizuje sa, resolve-ne revision podľa branch, tag, commit alebo SemVer policy, vytvorí artifact a publikuje jeho identity a availability v `status`.

Source artifact je významná boundary:

```text
remote source
→ authenticated fetch
→ resolved revision
→ packaged artifact
→ in-cluster consumer
```

Downstream controller nemusí sám implementovať Git alebo registry clienta. Konzumuje artifact identifikovaný source revision a digestom.

### `kustomize-controller`

`kustomize-controller` sleduje `Kustomization` resources. Z referencovaného source artifactu vyberie path, prípadne dešifruje SOPS content, vykoná Kustomize build alebo zostaví plain manifests, validuje ich proti Kubernetes API a použije server-side apply. Udržiava inventory, podľa ktorého vie identifikovať resources patriace danej Kustomization a pri `prune: true` odstrániť objects, ktoré už v desired inventory nie sú.

### `helm-controller`

`helm-controller` sleduje `HelmRelease`. Z chart source-u a values vypočíta desired Helm release, vykonáva Helm install, upgrade, test, rollback, uninstall a remediation actions. Helm release history a Helm storage sú ďalšia state vrstva; úspešný source artifact ešte neznamená úspešný Helm action.

### `notification-controller`

`notification-controller` spracúva events a outbound notifications a prijíma webhook receivers. Webhook môže urýchliť source observation, ale nenahrádza interval-based reconciliation. Stratený webhook nesmie znamenať trvalú stratu convergencie.

### Image automation controllery

`image-reflector-controller` číta registry metadata a vyhodnocuje dostupné image versions. `image-automation-controller` podľa `ImagePolicy` upraví označené fields v Git repository, vytvorí commit a pushne ho na definovanú branch.

Tým vzniká dôležitá authority zmena:

```text
registry observation
→ image policy decision
→ Git mutation
→ nový authoritative desired-state commit
→ source-controller artifact
→ workload reconciliation
```

Image automation teda nie je direct deployment. Je to automatizovaný Git writer, ktorý musí mať vlastnú identity, branch scope, review alebo promotion contract a ochranu pred stale alebo nekompatibilným update-om.

## 3. Exact Flux subject

Pri tvrdení „Flux nasadil release“ musí byť identifikované minimálne:

- Flux installation identity a controller versions — určujú, ktorý control plane a ktoré API semantics vykonali reconciliation;
- source object identity — napríklad namespace, name, UID a generation `GitRepository` alebo `OCIRepository`;
- configured source selector — URL, branch, tag, commit, SemVer range alebo digest;
- resolved source revision a artifact digest — určujú bytes, ktoré downstream controller reálne konzumoval;
- `Kustomization` alebo `HelmRelease` UID a generation — určujú reconciliation policy a values;
- path, dependencies, substitutions, decryption inputs a external references — menia final desired state;
- service account a target cluster/namespace — určujú authorization a destination;
- inventory, prune a field-management policy — určujú ownership a deletion behavior;
- health, timeout, retry a remediation policy — určujú, kedy sa transition považuje za technicky úspešnú;
- workload a business oracle — určujú, či nasadený system poskytuje zamýšľaný outcome.

Bez týchto údajov sa môže zameniť source readiness, apply success, controller readiness a reálny release success.

## 4. Source resolution a artifact lifecycle

Príklad source objectu:

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: payments-env
  namespace: payments-prod
spec:
  interval: 1m
  url: ssh://git@example.internal/platform/payments-env.git
  ref:
    commit: b71f2037a98c4c6e8e4c2a4d5baf93b82cb739a1
  secretRef:
    name: payments-env-read
```

`spec.ref.commit` tu identifikuje immutable Git commit. Ak by objekt sledoval `branch: main`, branch by bola iba mutable pointer; `status.artifact.revision` musí ukázať commit, na ktorý bola v danom observation cykle resolve-nutá.

Source lifecycle:

```text
Source spec generation
→ queue/reconcile
→ credential resolution
→ remote fetch
→ revision selection
→ optional authenticity verification
→ include/ignore processing
→ artifact packaging
→ digest calculation
→ artifact publication
→ Ready condition a downstream event
```

Source `Ready=True` znamená, že artifact je dostupný. Neznamená, že:

- path použitá downstream Kustomization existuje;
- decryption key je dostupný;
- manifests sú syntakticky alebo schema-valid;
- target API povoľuje apply;
- health checks prejdú;
- workload načítal správnu runtime generation;
- business canary prešiel.

### Artifact retention a cache

Artifact je lokálna reprezentácia remote source-u. Controller restart, garbage collection, source outage alebo credential rotation môžu ovplyvniť, či sa artifact dá znovu vytvoriť. Production evidence preto nemá uchovávať iba status text `stored artifact for revision X`; má zachytiť source revision, digest, timestamps a downstream observed revision.

Ak remote branch bola force-pushnutá, starý artifact môže dočasne stále existovať, ale nový controller alebo garbage collection môže vyžadovať refetch. Reproducibility preto vyžaduje retained commit/artifact, nie iba mutable ref.

## 5. `Kustomization` reconciliation pipeline

Flux `Kustomization` nie je to isté ako súbor `kustomization.yaml`. Custom Resource opisuje reconciliation pipeline, zatiaľ čo Kustomize file opisuje transformáciu manifestov v source path.

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: payments
  namespace: payments-prod
spec:
  interval: 5m
  retryInterval: 1m
  timeout: 8m
  path: ./clusters/prod/payments
  sourceRef:
    kind: GitRepository
    name: payments-env
  serviceAccountName: payments-reconciler
  targetNamespace: payments
  prune: true
  wait: true
  decryption:
    provider: sops
    serviceAccountName: payments-sops
  postBuild:
    substitute:
      ENVIRONMENT: production
```

Reconciliation prebieha približne takto:

```text
Kustomization generation alebo source artifact change
→ sourceRef resolution
→ artifact download
→ path selection
→ decryption
→ Kustomize build / plain manifest accumulation
→ substitutions a patches
→ object validation
→ server-side apply
→ inventory update
→ prune eligible stale objects
→ health assessment
→ status/conditions/events
```

Každá transition môže zlyhať inak. `ArtifactFailed` poukazuje na source acquisition boundary, `BuildFailed` na render boundary, `ReconciliationFailed` na validation alebo apply boundary a `HealthCheckFailed` na post-apply readiness boundary. Rovnaký používateľský symptóm „release nie je live“ preto vyžaduje zistenie poslednej úspešnej transition, nie náhodné opakovanie apply.

## 6. Interval, events, retry a manual reconcile

`spec.interval` určuje periodické prehodnotenie desired/live state-u. Je to lower-bound-like scheduling contract s možným jitterom, nie hard real-time deadline. Source revision change môže vyvolať okamžitejšiu downstream reconciliation cez controller events.

`spec.retryInterval` umožňuje odlíšiť normálny observation interval od častejšieho retry po zlyhaní. Príliš krátky retry môže pri persistentnom invalid manifeste vytvoriť hot loop a zaťažiť API, KMS, Git server alebo admission webhooks. Príliš dlhý retry predlžuje recovery po transientnom výpadku.

Manual reconcile cez annotation alebo `flux reconcile` iba vloží nový reconciliation request. Nemení authoritative desired state. Ak je source alebo spec chybný, manual reconcile zopakuje tú istú chybu.

## 7. Server-side apply a field ownership

`kustomize-controller` používa server-side apply. Kubernetes API preto eviduje field managers a rozhoduje o ownership/conflicts na schema field úrovni.

Flux annotations môžu meniť apply behavior:

- `kustomize.toolkit.fluxcd.io/ssa: Override` — Flux presadzuje fields definované v desired manifests;
- `Merge` — zachová fields pridané inými managers, pokiaľ sa neprekrývajú s Flux desired fields;
- `IfNotPresent` — resource sa vytvorí iba ak neexistuje, čo je vhodné pre resources ďalej vlastnené iným controllerom;
- `Ignore` — resource je súčasťou source-u, ale Flux ho neaplikuje;
- `kustomize.toolkit.fluxcd.io/force: Enabled` — pri immutable-field change môže resource znovu vytvoriť;
- `kustomize.toolkit.fluxcd.io/prune: Disabled` — resource sa vynechá z garbage collection deletion.

Tieto options nie sú náhradou za ownership design. `Merge` nevyrieši atomic list, ktorú Kubernetes schema prideľuje jednému managerovi. `Force` na StatefulSet môže spôsobiť disruptive recreation a data risk. `IfNotPresent` zase znamená, že neskorší desired update Flux nepresadí.

Správna otázka nie je „ktorú annotation použiť, aby diff zmizol“, ale:

```text
Kto je authoritative owner tohto field-u?
→ ktorý controller ho mení?
→ ako API schema modeluje ownership?
→ čo sa má stať pri konflikte?
→ ktorý evidence potvrdí effective behavior?
```

## 8. Inventory a garbage collection

Po apply Flux ukladá inventory aplikovaných objects. Pri ďalšej reconciliation porovná nový desired inventory s predchádzajúcim a pri `prune: true` odstráni objects, ktoré už source neobsahuje.

Prune safety závisí od troch identít:

```text
previously managed object identity
+ current desired inventory
+ current Kustomization ownership
→ deletion eligibility
```

Nebezpečné situácie:

- source path sa omylom vyrenderuje na prázdny set;
- resource bol presunutý medzi Kustomizations bez ownership handoffu;
- dve Kustomizations riadia rovnaký object;
- namespace alebo CRD sa odstráni skôr než dependents;
- generated name alebo target namespace sa zmení;
- Kustomization deletion spustí garbage collection podľa deletion policy.

`prune: false` znižuje riziko accidental deletion, ale vytvára orphan drift. Bez explicitného decommission workflow zostanú obsolete Services, RBAC, webhooks alebo cloud-controller resources aktívne.

## 9. Dependencies a readiness

`spec.dependsOn` blokuje Kustomization, kým dependency nie je `Ready`. Je to ordering/readiness contract medzi Flux objects, nie všeobecný distributed transaction.

```text
platform CRDs/controller Ready
→ tenant policy Ready
→ secret declaration Ready
→ application manifests apply
```

Failure boundaries:

- circular dependency — žiadna Kustomization nemôže prejsť do apply;
- false readiness — dependency controller je Ready, ale external API alebo credential nie;
- stale readiness — dependent číta posledný `Ready=True`, hoci nová dependency generation ešte nie je accepted;
- version mismatch — dependency je Ready na inej generation než dependent očakáva;
- external side effect — database migration alebo provider registration nemusí mať Kubernetes readiness model.

`readyExpr` môže doplniť generation alebo version-aware podmienku, ale chybný CEL expression môže blokovať rollout alebo vytvoriť false readiness. Expression potrebuje positive aj negative tests.

## 10. Health assessment

`wait: true` vykonáva health assessment všetkých reconciled resources podporovaných kstatus modelom. `healthChecks` vyberá explicitné resources. Custom `healthCheckExprs` môže definovať CEL-based stav pre vlastné CRDs.

Health verdict má rozsah:

```text
resource generation observed
→ controller-specific readiness
→ Ready/Healthy condition
```

Neoveruje automaticky:

- exact container digest vo všetkých running Pods;
- loaded configuration alebo secret generation v process memory;
- network route cez všetky intermediaries;
- database schema compatibility;
- provider-side effect;
- customer journey alebo settlement correctness.

Preto sa Flux `Ready=True` nesmie zameniť s business acceptance.

## 11. Decryption boundary

Flux Kustomization podporuje SOPS decryption. Pipeline sa tým mení:

```text
encrypted source artifact
→ decryption identity a key/KMS authorization
→ plaintext v controller memory
→ manifest build
→ Kubernetes Secret apply
→ API/etcd/runtime secret exposure boundary
```

Git repository neobsahuje plaintext secret, ale kustomize-controller musí mať právo dešifrovať. Ak používa broad global key alebo cluster-admin identity, compromise jedného tenant source-u môže rozšíriť blast radius. `decryption.serviceAccountName` a cloud workload identity umožňujú viazať KMS authorization na konkrétnu Kustomization/namespace boundary.

Decryption success tiež neznamená rotation success. Workload konzumujúci Secret ako environment variable načíta value pri vytvorení containeru. Zmena Kubernetes Secretu sama o sebe nereštartuje Pod ani nezmení už načítanú process memory.

## 12. `postBuild` substitution a hidden inputs

`postBuild.substitute` je deklarovaný v Kustomization spec. `substituteFrom` môže čítať `ConfigMap` alebo `Secret`. Tieto values menia rendered desired state po source fetchi.

```text
Git artifact
+ Kustomization spec
+ substituteFrom object
→ final manifests
```

Ak `substituteFrom` object mení portal, CI alebo human mimo authoritative Git processu, Flux source artifact už nie je úplný source of truth. Status musí korelovať external input generation, inak dva reconciles rovnakého Git commit-u môžu vyrenderovať odlišné resources.

Optional substitution reference môže zlyhanie skryť tak, že missing input preskočí. To je vhodné iba vtedy, ak absent value má bezpečne definovaný meaning. Critical production route, tenant ID alebo credential reference nemá ticho spadnúť na default.

## 13. Helm reconciliation

`HelmRelease` opisuje desired Helm release:

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: settlement-api
  namespace: payments-prod
spec:
  interval: 5m
  timeout: 10m
  serviceAccountName: payments-reconciler
  chart:
    spec:
      chart: settlement-api
      version: 9.1.4
      sourceRef:
        kind: OCIRepository
        name: settlement-api-chart
  values:
    image:
      digest: sha256:pay910a
  upgrade:
    remediation:
      retries: 2
      strategy: rollback
  test:
    enable: true
```

Helm lifecycle obsahuje vlastný state machine:

```text
HelmRelease generation + chart artifact + values
→ desired Helm action
→ install/upgrade
→ hooks a resource waiting
→ Helm tests
→ release storage/history
→ Ready alebo remediation
```

Remediation retry nie je bezrizikové „skús znova“. Hook môže mať external side effect, migration môže byť non-reversible a timeout môže znamenať unknown outcome. Pred automatic rollbackom musí byť overená application, schema a data compatibility.

Helm release `Ready=True` znamená, že Helm controller považuje release za up-to-date a successful podľa svojho contractu. Stále to nie je business acceptance.

## 14. Image automation ako Git writer

Image automation pozostáva z troch decisions:

```text
ImageRepository
→ ktoré registry metadata sa pozorujú

ImagePolicy
→ ktorý tag/digest je eligible a preferred

ImageUpdateAutomation
→ ktoré Git fields sa prepíšu, kam sa commitne a kam sa pushne
```

Automatizácia môže podporiť staging delivery, ale production promotion vyžaduje explicitný authority model. Ak automation zapisuje priamo do production pathu na základe širokého SemVer range, registry publish sa prakticky stáva production promotion decisionom.

Bezpečnejší model môže byť:

```text
registry candidate
→ staging automation commit
→ staging reconciliation a acceptance evidence
→ promotion PR kopírujúci exact digest
→ production approval
→ production Flux reconciliation
```

Flux commit message a Git history poskytujú audit, ale nepreukazujú, že candidate prešiel stagingom ani že approval zostal fresh po ďalšej zmene.

## 15. Multi-tenancy a impersonation

Flux controllery môžu defaultne bežať s veľmi širokými cluster permissions. V trusted single-team clusteri je to jednoduché, ale tenant môže prostredníctvom Flux CRD požiadať controller, aby vykonal actions v jeho mene.

Multi-tenant hardening zahŕňa:

- namespace segmentation a Kubernetes RBAC;
- `spec.serviceAccountName` na Kustomizations a HelmReleases;
- controller default service account bez permissions, ak explicitný account chýba;
- zákaz cross-namespace source references;
- zákaz remote Kustomize bases;
- oddelené source credentials a decryption identities;
- resource quotas a admission policies pre tenant-created Flux objects;
- platform-admin reconciliation oddelenú od tenant reconciliation.

Impersonation znamená, že controller pri target actions použije tenant service account. Neznamená to automaticky, že source fetch, KMS decryption, notification alebo controller cache sú tenant-isolated; každá boundary potrebuje samostatný threat model.

## 16. Suspension a break-glass

`spec.suspend: true` zastaví reconciliation daného source-u, Kustomization, HelmRelease alebo image automation objektu podľa jeho API. Suspension je control-plane state, nie rollback.

Pri incidente môže byť použité:

```text
incident detection
→ suspend relevant writer
→ preserve source/status/live evidence
→ contain workload alebo external effect
→ update authoritative desired state
→ resume reconciliation
→ verify convergence a business recovery
```

Ak human patchne live resource počas suspension a potom iba nastaví `suspend: false`, Flux môže patch okamžite revertovať. Pred resume musí byť rozhodnuté, či live change patrí do Git-u, má byť odstránená alebo má ownership iný controller.

## 17. Observability

Flux evidence vzniká vo viacerých vrstvách:

| Vrstva | Evidence | Čo dokazuje | Čo nedokazuje |
|---|---|---|---|
| Source | `status.artifact`, revision, digest, conditions, events | ktorý source artifact bol získaný | že downstream build/apply prešiel |
| Kustomization | observed generation, last applied revision, inventory, conditions | ktorý artifact/spec bol vyrenderovaný a aplikovaný | business correctness |
| HelmRelease | release revision, conditions, history, remediation state | Helm action outcome | exact customer journey |
| Controller | logs, reconciliation duration, error reason, queue metrics | interný failure point a retries | úplnosť source authority |
| Kubernetes | objects, managedFields, ReplicaSets, Pods, events | live API a rollout state | loaded secret/config a provider state |
| Application | version endpoint, config generation, traces, business canary | effective runtime outcome | source provenance bez correlation |

Diagnostika musí spájať identities. Log `reconciliation finished` bez namespace/name/UID/generation/revision nestačí.

## 18. Connected incident `GITOPS-PAY-62`

Atlas Payments po incidente s Argo CD zaviedol Flux a interný portal LaunchPad. Release `payments 9.1` mal prejsť:

```text
immutable image sha256:pay910a
→ staging image-update commit
→ staging Flux artifact a reconciliation
→ provider credential generation pv-42
→ staging settlement canary
→ promotion PR kopírujúci exact image/config/secret contract
→ production Flux reconciliation
→ production canary
→ LaunchPad operation completion
```

Skutočný model však obsahoval:

```text
Git environment repository
+ Flux ImageUpdateAutomation writer
+ LaunchPad substituteFrom ConfigMap writer
+ shared SOPS age decryption key
+ human emergency Secret rotation
```

Konkrétne:

- staging aj production source sledovali mutable `main`;
- image automation zapisovala do shared base a mohla meniť oba environmenty;
- production Kustomization používala `postBuild.substituteFrom` ConfigMap `launchpad-runtime`, ktorú portal menil priamo v clusteri;
- `dependsOn` čakal iba na secret Kustomization `Ready`, nie na required provider credential generation;
- SOPS age private key bol uložený v shared `flux-system` Secret-e a kustomize-controller používal broad identity;
- provider credential sa z `pv-42` rotoval na `pv-43`, ale Pods čítali Secret cez environment variables a rollout sa nespustil;
- LaunchPad označil request ako successful po vytvorení promotion PR, nie po production reconciliation a business canary.

Timeline:

```text
10:02:11 image automation commitne pay910a do staging
10:08:44 staging canary prejde na route generation 1850
10:11:03 promotion request načíta staging evidence
10:12:17 image automation prepíše shared base na pay910b
10:13:04 LaunchPad zmení cluster ConfigMap route=1849
10:14:22 promotion PR merge
10:15:01 production source artifact b71f203
10:15:09 Flux apply: pay910b + route 1849
10:16:31 Kustomization Ready=True
10:19:18 provider credential rotovaný na pv-43
10:23:47 first provider authentication failures
10:31:02 incident potvrdený
```

Production preto nebola promoted staging generation. Používala:

```text
approved evidence:       pay910a / route 1850 / credential pv-42
Flux rendered desired:   pay910b / route 1849 / Secret pv-42
running process state:   pay910b / route 1849 / loaded pv-42
provider authority:      credential pv-43
```

Dôsledky:

- `2 746` settlements bolo routovaných cez stale route generation `1849`;
- `61` provider calls zlyhalo po revocation `pv-42`;
- retries vytvorili `14` unknown outcomes vyžadujúcich provider reconciliation;
- LaunchPad zobrazoval operation ako completed 17 minút pred potvrdením production failure;
- rovnaký Git source revision sa pri zmene cluster ConfigMap-u renderoval odlišne;
- shared decryption identity zväčšila blast radius jedného controller compromise-u.

### Flux root cause

Flux controllery vykonali configured reconciliation. Root cause bol neúplný Flux subject a authority graph: shared Git writer, hidden substitution input, broad decryption identity, readiness bez required secret generation a acceptance založená na Kustomization `Ready`.

### Redesign

```text
environment-specific immutable source coordinate
→ staging-only image automation branch
→ exact digest promotion PR
→ generation-bound staging evidence
→ no cluster-local critical substitutions
→ namespace-scoped reconciliation service account
→ workload-identity SOPS KMS key per environment
→ secret generation contract + rollout trigger
→ Flux inventory/health evidence
→ application version/config/credential generation endpoint
→ production settlement canary
→ durable LaunchPad operation completion
```

## 19. Flux acceptance verdict

Flux design je prijatý, keď:

- source object, resolved revision, artifact digest a retention sú explicitné;
- Kustomization/HelmRelease generation a controller versions sú evidované;
- source, decryption, substitution, build, apply, inventory, prune a health boundaries sú pozorovateľné;
- branch/tag/range semantics nezakrývajú immutable effective generation;
- `postBuild`, valuesFrom a external inputs majú authoritative version a precedence contract;
- service-account impersonation a target RBAC obmedzujú tenant scope;
- cross-namespace references, remote bases a shared credentials zodpovedajú threat modelu;
- field ownership a server-side apply policy nevedú k oscillation alebo silent ignore;
- prune a deletion policy sú testované na move, rename, empty render a controller deletion;
- dependencies sú generation-aware a bez circularity;
- health verdict je oddelený od workload a business acceptance;
- Helm remediation rešpektuje side effects, schema/data compatibility a unknown outcomes;
- image automation je governed Git writer, nie hidden production promoter;
- source outage, KMS outage, controller restart, stale artifact, direct drift, failed health, prune a second-reconcile tests prejdú;
- forbidden cross-tenant apply, shared-key decryption, hidden substitution, stale promotion a false-Ready outcomes sú odmietnuté.

## 20. Troubleshooting flow

```text
Flux resource nie je Ready alebo workload používa wrong generation
→ exact cluster/installation/controller generation
→ source object UID/generation/ref
→ resolved revision + artifact digest
→ downstream observed source revision
→ path/decryption/substitution/build inputs
→ service account + API authorization
→ SSA conflicts + managedFields
→ inventory/prune decision
→ dependency/readiness/timeout/remediation state
→ Deployment/ReplicaSet/Pod generation
→ loaded config/secret/provider generation
→ business outcome
→ authoritative fix + second reconciliation
```

## 21. Anti-patterny

### `GitRepository Ready` znamená deployment ready

Source artifact availability nepreukazuje build, apply, health ani runtime outcome.

### Všetky environmenty môžu sledovať `main`

Môžu, ale promotion authority potom musí byť reprezentovaná environment path transitionom a review policy. Samotný názov branch-e neoddeľuje staging od production.

### `dependsOn` je distributed transaction

Nie. Vyjadruje Flux readiness ordering, nie atomicitu external migrations, credentials alebo provider state-u.

### `wait: true` je acceptance test

Je to resource health assessment. Nevykonáva automaticky business journey ani exact generation correlation.

### Shared SOPS key je jednoduchší

Je jednoduchší operatívne, ale spája tenant a environment blast radius. Decryption identity je production credential a potrebuje least privilege, rotation a audit.

### Image automation môže zapisovať priamo do production

Technicky môže. Bez promotion evidence a policy však registry selection automaticky mení production authority.

### `suspend` je rollback

Suspension iba zastaví reconciliation. Neobnovuje predchádzajúcu desired alebo runtime generation.

### Manual reconcile opraví stale workload

Iba zopakuje current desired-state pipeline. Workload, ktorý nereaguje na Secret update, potrebuje explicitný rollout/rotation mechanismus.

## 22. Kontrolné otázky

1. Prečo je Flux lepšie chápať ako sieť controllerov než ako jeden deployment tool?
2. Čo tvorí exact Flux source a reconciliation subject?
3. Aký význam má source artifact medzi `source-controller` a downstream controllermi?
4. Ako sa `GitRepository Ready` líši od `Kustomization Ready` a business accepted?
5. Ktoré kroky obsahuje Kustomization reconciliation pipeline?
6. Ako server-side apply mení field ownership a conflict semantics?
7. Podľa čoho Flux rozhoduje o prune eligibility?
8. Čo `dependsOn` garantuje a čo negarantuje?
9. Prečo môže `postBuild.substituteFrom` vytvoriť hidden desired-state writera?
10. Ako sa Helm remediation môže stať nebezpečnou pri external side effects?
11. Kedy sa ImageUpdateAutomation stáva production promotion authority?
12. Ako service-account impersonation znižuje multi-tenant blast radius?
13. Prečo SOPS decryption success nepreukazuje secret rotation success?
14. Ktoré evidence odlišujú source, apply, workload a business failure?
15. Prečo bol `GITOPS-PAY-62` technicky `Ready`, ale nebol accepted?
16. Čo musí overiť Flux acceptance verdict po controller restarte a druhom reconcile?

## Glossary impact

Relevantné pojmy: Flux subject, GitOps Toolkit, source-controller, source artifact, source revision, kustomize-controller, Flux Kustomization, HelmRelease, notification-controller, image-reflector-controller, image-automation-controller, observed source revision, Flux inventory, prune eligibility, server-side apply policy, Flux dependency, readiness expression, Flux health verdict, postBuild substitution, decryption identity, Flux impersonation, Flux suspension, image automation writer a Flux acceptance verdict.

## Primárne zdroje

- [Flux — Source Controllers](https://fluxcd.io/flux/components/source/)
- [Flux — Kustomize Controller](https://fluxcd.io/flux/components/kustomize/)
- [Flux — Kustomization](https://fluxcd.io/flux/components/kustomize/kustomizations/)
- [Flux — Helm Controller](https://fluxcd.io/flux/components/helm/)
- [Flux — HelmRelease](https://fluxcd.io/flux/components/helm/helmreleases/)
- [Flux — Image Automation Controllers](https://fluxcd.io/flux/components/image/)
- [Flux — ImageUpdateAutomation](https://fluxcd.io/flux/components/image/imageupdateautomations/)
- [Flux — Multi-tenancy](https://fluxcd.io/flux/installation/configuration/multitenancy/)
- [Flux — Security](https://fluxcd.io/flux/security/)
- [Flux — Repository Structure](https://fluxcd.io/flux/guides/repository-structure/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Argo CD](argo-cd.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Application promotion →](application-promotion.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
