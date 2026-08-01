# GitOps troubleshooting

GitOps troubleshooting nie je hľadanie dôvodu, prečo dashboard neukazuje zelenú. Je to rekonštrukcia authority, source resolution, renderu, apply/reconciliation, live ownership a business outcome-u pre jednu presnú generation. `Synced`, `Ready=True` alebo successful reconciliation sú užitočné labels, ale každé patria inej vrstve a majú inú dôkaznú hranicu.

Preserve-first model:

```text
používateľský alebo platformový symptóm
→ Git/source/controller/cluster/application identity
→ exact revision a effective inputs
→ render generation
→ desired/live diff a ownership
→ apply/reconcile operation
→ controller a Kubernetes runtime state
→ serving cohort a business outcome
→ containment, Git recovery alebo ownership repair
→ druhá reconciliation a forbidden-path verification
```

## Minimálny incident manifest

Pred refreshom, syncom, suspendom alebo manuálnym patchom ulož:

```text
controller type, namespace a version
Application/Kustomization/GitRepository UID a generation
repository URL, source kind, ref selector a resolved commit/artifact digest
path/chart/values/Kustomize inputs a dependency revisions
cluster context, server UID, namespace a tenant/project
last attempted/applied/successful revision
sync/reconcile operation ID a timestamps
desired manifest checksum
live object UID/generation/resourceVersion/managedFields
workload imageID a loaded configuration generation
business request/operation identity
```

Argo CD:

```bash
kubectl -n argocd get application APP -o yaml > /tmp/app.yaml
argocd app get APP --hard-refresh
argocd app manifests APP > /tmp/desired.yaml
argocd app diff APP > /tmp/diff.txt || true
```

Flux:

```bash
flux get sources git -A
flux get kustomizations -A
kubectl -n NAMESPACE get gitrepository SOURCE -o yaml > /tmp/source.yaml
kubectl -n NAMESPACE get kustomization KS -o yaml > /tmp/kustomization.yaml
flux build kustomization KS --path ./PATH > /tmp/desired.yaml
```

Fresh refresh môže zmeniť controller status a volatile evidence. Najprv zachovaj current objects a logs, potom vyžiadaj refresh/reconcile.

## 1. Controller sleduje nesprávny source alebo revision

Najčastejšie sources používajú branch, tag, semver selector, commit, OCI artifact alebo Helm repository version. Mutable selector musí byť vždy spojený s resolved immutable revision.

Competing hypotheses:

```text
repo URL alebo path je nesprávny
branch/tag selector ukazuje inú generation
webhook neprišiel, ale polling ešte neprebehol
source cache alebo artifact je stale
credential nemá fetch capability
proxy/DNS/TLS blokuje source
submodule/LFS/large file chýba
multi-source alebo dependency používa inú revision
```

Argo:

```bash
jq '.spec.source,.spec.sources,.status.sync.revision,.status.reconciledAt' /tmp/app.json
kubectl -n argocd logs deploy/argocd-repo-server --since=30m
```

Flux:

```bash
kubectl -n flux-system get gitrepository SOURCE -o json | jq '{
  spec:.spec,
  artifact:.status.artifact,
  conditions:.status.conditions
}'
flux reconcile source git SOURCE --with-source
```

Reconcile command je mutation nad controller schedule, nie oprava source contractu. Ak mutable branch bola force-pushnutá, controller môže korektne resolve-nuť novú históriu, ktorá nemá audit continuity. Recovery potrebuje protected refs alebo immutable release manifest, nie častejší polling.

## 2. Repository authentication alebo trust zlyháva

Odlišuj:

```text
DNS/TCP/TLS reachability
server certificate trust
Git/OCI/Helm authentication
repository authorization
credential scope/expiry
known-host alebo SSH host-key trust
proxy/no_proxy behavior
```

Private repository secret môže byť správne uložený a stále používať nesprávny URL matching rule. Shared credential template môže nečakane rozšíriť blast radius. Pri incident evidence nevypisuj token alebo private key; zaznamenaj secret UID/resourceVersion, issuer, target URL, expiry a fingerprint verejnej časti.

Argo repository test alebo Flux Source condition dokazuje fetch capability v konkrétnom čase. Nepreukazuje, že Application/Kustomization používa rovnaký source object alebo desired path.

Po rotation over:

```text
nový credential je accepted
controller načítal source novou identity
starý credential je revoked
iné repository/tenant scopes nie sú dostupné
second fetch stále funguje
```

## 3. Source je ready, render zlyháva

Source artifact môže byť zdravý, ale Kustomize, Helm, Jsonnet alebo plugin render môže zlyhať. Failure classes:

```text
path alebo file chýba
syntax alebo schema
Kustomize resource/patch target mismatch
Helm values/type/template failure
chart dependency alebo plugin chýba
CRD/API capability mismatch
postBuild/substitution input chýba
custom plugin image/config/timeout
nondeterministic lookup/random/time input
```

Reproduce render s rovnakým toolchainom a inputs. Local `helm template` alebo `kubectl kustomize` nemusí zodpovedať controller version, flags, API capabilities alebo cluster-local substitution.

Argo desired manifest sa získava z repo-serveru:

```bash
argocd app manifests APP --source-position 1 > /tmp/desired.yaml
kubectl -n argocd logs deploy/argocd-repo-server --since=20m
```

Flux Kustomization môže používať `.spec.postBuild.substituteFrom`; critical ConfigMap/Secret input mimo versionovaného source-u znamená, že source revision sama neidentifikuje render. Troubleshooting musí pridať tieto objects a resourceVersions do render subjectu alebo ich presunúť do authoritative source.

## 4. Desired manifest je iný než operátor očakáva

Porovnaj source, effective render a controller-stored desired output. Nezačínaj live clusterom. Hidden inputs môžu zahŕňať:

```text
Argo parameter override
multiple values files a precedence
ApplicationSet generator values
multi-source value reference
Kustomize image/patch transformer
Flux substitution
HelmRelease valuesFrom
admission-independent post-renderer
custom config-management plugin
```

Pri Argo:

```bash
argocd app get APP -o json | jq '.spec.source,.spec.sources,.status.sourceType'
argocd app manifests APP > /tmp/controller-render.yaml
```

`helm get values` nie je Argo desired read-back, ak Helm CLI release vôbec nevlastní deployment. Každý controller má vlastný render/evidence model.

Recovery odstráni neautoritatívny override alebo ho presunie do Git-u. Blind Git revert nepomôže, ak vyššia-precedence parameter stále prepisuje hodnotu.

## 5. Application/Kustomization je OutOfSync alebo Ready=False

Najprv klasifikuj rozdiel:

```text
Git-owned drift
controller/default/admission normalization
legitimate delegated field owner
status alebo ephemeral field
untracked resource
failed apply/prune
stale comparison cache
```

Argo diff:

```bash
argocd app diff APP --local /tmp/render-root || true
kubectl get OBJECT -o yaml --show-managed-fields
```

Broad `ignoreDifferences` môže skryť image, environment alebo security context. Narrow exception musí pomenovať field, resource a legitimate owner. `RespectIgnoreDifferences` a diff-ignore semantics treba hodnotiť spolu s apply ownershipom; ignorovaný rozdiel nie je automaticky delegated ownership.

Flux používa server-side apply a field-management policies. ManagedFields pomôžu identifikovať writerov. Ak GitOps controller a HPA vlastnia `spec.replicas`, system môže oscillovať alebo jeden writer pravidelne prepisovať druhého. Oprava stanoví jedného authoritative writera alebo explicitnú delegation.

## 6. Sync/apply zlyháva

Apply failure môže byť:

```text
RBAC/authorization
admission deny alebo mutation
immutable field
missing CRD/API
namespace/destination restriction
server-side apply ownership conflict
object size/validation
quota/limit range
hook alebo wave failure
network/API timeout s unknown outcome
```

Argo operation:

```bash
kubectl -n argocd get application APP -o json | jq '.status.operationState'
argocd app get APP --show-operation
kubectl -n argocd logs statefulset/argocd-application-controller --since=30m
```

Flux:

```bash
kubectl -n NS get kustomization KS -o json | jq '.status.conditions,.status.inventory,.status.lastAppliedRevision,.status.lastAttemptedRevision'
flux logs --kind=Kustomization --name=KS --namespace=NS --since=30m
```

Timeout nevypovedá, že sa nič neaplikovalo. Read-backni object UIDs/generations a controller inventory pred retryom. Hook Job môže commitnúť migration alebo external side effect a následne status write zlyhá. Retry potrebuje stable operation identity.

## 7. Resource ostáva `Progressing` alebo `Degraded`

Rozlož runtime transition:

```text
Deployment spec accepted
→ controller observedGeneration
→ ReplicaSet generation
→ Pod scheduling
→ image pull
→ container start
→ probes
→ Service endpoints
→ request/business outcome
```

```bash
kubectl -n NS get deploy,rs,pods,endpointslices -l app=APP -o wide
kubectl -n NS describe deployment DEPLOYMENT
kubectl -n NS get events --sort-by=.lastTimestamp | tail -50
kubectl -n NS logs deploy/DEPLOYMENT --all-containers --tail=200
```

Argo custom health alebo Flux wait/healthChecks môže byť príliš plytký alebo príliš hlboký. Healthy Pods bez správneho image/config generation sú false green. Naopak dependency outage môže držať readiness false a controller timeoutnúť, hoci desired apply bolo správne.

## 8. Synced/Ready, ale business je chybný

To je najdôležitejší false-green cluster. Competing hypotheses:

```text
health oracle nekontroluje business path
Service alebo route smeruje na starú cohortu
Pody načítali starú config/secret generation
image tag resolve-ol iné bytes
cache/CDN odpovedá starým obsahom
migration/event schema nie je kompatibilná
retry vytvára duplicate side effects
external dependency alebo credential zlyháva
```

Correlate:

```text
source revision
→ rendered image/config/secret references
→ live Deployment/ReplicaSet
→ Pod imageID a loaded version endpoint
→ EndpointSlice/route
→ request ID
→ application a provider ledger
```

Business canary patrí do PostSync/verification flowu alebo samostatného rollout controlleru. Ak canary zlyhá, recovery mení Git desired generation alebo release/exposure state; status label sa nesmie ručne prepísať.

## 9. Self-heal nefunguje alebo prepisuje incident containment

Self-heal funguje iba pre differences, ktoré controller porovnáva a môže meniť. Neopraví external side effect, secret v provideri alebo field ignorovaný diff policy. Nemusí sa vykonať okamžite; controller má reconcile interval a queue.

Ak incident responder patchne Git-owned field, self-heal ho môže vrátiť. Break-glass postup preto potrebuje:

```text
incident owner a scope
controller suspend/auto-sync transition
preserved current desired/live evidence
časovo obmedzenú alternate authority
Git adoption alebo revert decision
controller resume
post-recovery drift test
credential revocation
```

Flux suspend:

```bash
flux suspend kustomization KS -n NS
flux resume kustomization KS -n NS
```

Argo auto-sync change sa má vykonať na authoritative Application/ApplicationSet source. Pri ApplicationSet-managed Application nemusí live edit child Application prežiť.

## 10. Prune, finalizers a deletion visia

Prune/delete failure môže byť spôsobený:

```text
Kubernetes finalizer
foreground dependency graph
admission/RBAC deny
namespace termination
APIService/CRD unavailable
resource protection annotation/sync option
controller inventory mismatch
orphan policy
external cleanup hook
```

```bash
kubectl get OBJECT -o json | jq '{deletionTimestamp:.metadata.deletionTimestamp,finalizers:.metadata.finalizers,ownerReferences:.metadata.ownerReferences}'
kubectl get namespace NS -o yaml
```

Finalizer nie je „stuck flag na odstránenie“. Predstavuje cleanup contract. Force removal môže orphanovať cloud load balancer, DNS, volume, identity alebo database resource. Najprv identifikuj controller ownera a external state.

Argo resources finalizer môže cascade-delete Application resources. `Prune=confirm`, `Prune=false`, `allowEmpty` a propagation policy menia deletion semantics. Troubleshooting musí čítať Application aj per-resource options.

## 11. Secret decryption alebo rotation

SOPS, External Secrets, Sealed Secrets alebo CSI driver majú odlišné authority paths. Rozlož:

```text
encrypted/reference source
→ controller decryption/fetch identity
→ target Secret generation
→ volume/env projection
→ application reload/rollout
→ loaded credential fingerprint
→ provider acceptance
→ old credential revocation
```

`Secret` updated neznamená, že env-var consumer načítal novú hodnotu. GitOps controller môže byť Synced a provider už odmietnuť starý credential. Rotation potrebuje overlap, consumer convergence a revocation evidence.

Shared decryption key medzi environmentmi alebo tenants zväčšuje blast radius. Repository encryption nechráni plaintext po decryption v controller memory, Kubernetes Secret alebo Pod.

## 12. Promotion používa stale evidence

Promotion proposal musí byť compare-and-swap decision nad immutable release manifestom, source base revision a environment evidence. Stale approval môže vzniknúť, keď sa po teste zmení shared base, chart dependency, image automation, valuesFrom alebo target branch.

Pred mergeom znovu renderuj final candidate a porovnaj:

```text
approved artifact/config/schema/secret contract
current target base
transitive dependency digests
final rendered manifest checksum
policy/admission evidence
```

Merge úspech je iba source transition. Production controller musí resolve-nuť rovnaký release subject a business verification musí patriť novej revision.

## 13. Multi-tenancy a controller scope

Pri cross-tenant incidente skontroluj:

```text
AppProject/source/destination/resource allowlist
Flux serviceAccountName a namespace scope
controller cluster role a impersonation
repository credential sharing
secret decryption scope
resource tracking identity
namespace and CRD ownership
network policy a runtime identity
```

Namespace nie je úplná tenant boundary, ak controller má cluster-admin a shared credentials. AppProject policy bez Kubernetes RBAC/admission/runtime isolation je iba jedna vrstva.

## Connected incident: Synced/Healthy, ale tri release generations

Atlas Application ukazovala `Synced/Healthy`. Git deklaroval image `I42`, Argo parameter override renderoval `I41`, on-call patchla live Deployment na `I43` a broad ignore rule ignorovala container subtree. CI zároveň priamo aplikovala ConfigMap generation 1841, zatiaľ čo Git deklaroval 1842.

Preserve-first evidence:

```text
Git commit a values
Application spec + parameter overrides
controller-rendered manifests
ignoreDifferences a sync options
live Deployment managedFields
ReplicaSet/Pod imageIDs
ConfigMap resourceVersion
/version loaded generations
settlement operation IDs
```

Recovery:

```text
fence CI a human writers
→ suspend automated mutation len ak potrebné
→ zachovať všetky generations
→ odstrániť hidden override a broad ignore
→ vybrať jeden autoritatívny release manifest
→ commitnúť exact image/config desired state
→ resume/reconcile
→ overiť Deployment, Pods, route a business ledger
→ testovať manual drift a second promotion
→ revoke break-glass capability
```

Root cause nebol Argo cache. Systém nemal jediného writera ani complete desired subject a health oracle neoveroval loaded generation.

## Closure gate

GitOps incident je uzatvorený až keď:

```text
source selector a resolved revision sú vysvetlené
render inputs sú úplné a immutable alebo versionované
controller desired manifest zodpovedá intentu
field ownership má jedného writera alebo explicitnú delegation
apply/prune operation outcome je read-backnutý
live objects a serving workload používajú očakávanú generation
secret/config consumers načítali nový state
business request a retry prejdú
forbidden direct writer alebo stará cohorta nie sú aktívne
ďalšia reconciliation nevytvorí drift ani oscillation
```

GitOps troubleshooting preto koreluje viac control planes. Git, controller status, Kubernetes API, runtime a business ledger sú samostatné sources evidence; žiadny z nich sám nereprezentuje celý release outcome.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Praktický GitOps projekt od Git revision po overený runtime](gitops-practical-walkthrough.md) · [↑ Obsah sekcie](README.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
