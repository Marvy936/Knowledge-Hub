# Flux

Flux je GitOps toolkit zložený zo spolupracujúcich Kubernetes controllerov. Nevykonáva jednu neurčitú operáciu „nasadiť z Git-u“. Najprv získa a identifikuje source artifact, potom z neho vypočíta desired state, aplikuje ho cez konkrétnu identitu, spravuje inventory a až následne čaká na technický health. Business outcome a skutočne načítaná configuration alebo secret generation zostávajú samostatným acceptance dôkazom.

```text
approved environment intent
→ exact source object a resolved artifact
→ Kustomization alebo HelmRelease generation
→ decryption, substitution a render
→ service-account-scoped mutation
→ inventory, prune a health
→ workload-loaded generations
→ business outcome
→ drift, recovery a second reconciliation
```

Táto postupnosť je rozhodujúca pri diagnostike. `GitRepository Ready=True` znamená dostupný source artifact, nie úspešný render. `Kustomization Ready=True` môže znamenať aplikované a healthy Kubernetes resources, nie správnu route policy, načítaný provider credential alebo úspešný settlement.

## 1. Controller graph a jeho authority boundaries

`source-controller` získava content z Git, OCI, Helm alebo bucket source-u a publikuje artifact s resolved revision a digestom. Downstream controller nekonzumuje abstraktný branch name; konzumuje konkrétnu artifact generation. Mutable selector ako `main` je preto iba pravidlo výberu. Incident a release evidence musia uvádzať výsledný commit a artifact digest.

`kustomize-controller` číta artifact, vyberie path, prípadne dešifruje SOPS dokumenty, vykoná substitutions a Kustomize build, validuje objects a použije server-side apply. Vedie inventory, z ktorého pri `prune: true` odvodzuje, ktoré predtým vlastnené objects už chýbajú v desired set-e. `helm-controller` podobne spravuje `HelmRelease`, no jeho state machine zahŕňa Helm install, upgrade, test, rollback, uninstall a remediation. Source success teda neuzatvára apply ani Helm action.

`notification-controller` prenáša events a prijíma webhook receivers. Webhook zrýchľuje observation, ale periodická reconciliation zostáva autoritou pre eventual convergence. Image reflector a image automation controllery zase sledujú registry metadata a zapisujú návrh novej image generation do Git-u. Nevykonávajú bezpečnú production promotion samy od seba; sú automatizovaným Git writerom, ktorý potrebuje scope, branch policy, candidate evidence a promotion boundary.

## 2. Exact Flux subject

Tvrdenie „Flux nasadil payments“ je overiteľné až vtedy, keď identifikuje celý subject: Flux installation a controller versions, source object UID a generation, configured ref, resolved revision, artifact digest, `Kustomization` alebo `HelmRelease` UID a generation, path, dependencies, decryption a substitution inputs, target cluster a namespace, apply service account, inventory, prune policy, health timeout a runtime acceptance oracle.

Tieto údaje nie sú administratívne detaily. Rovnaký Git commit môže vytvoriť iný effective desired state, ak sa zmení cluster-local `substituteFrom` ConfigMap, mutable Helm values source alebo decryption/retrieval input. Rovnaké manifests môžu byť aplikované do iného namespace-u alebo inou service account s odlišným privilege envelope. Rovnaký Deployment môže byť ready, hoci staré Pods používajú predchádzajúcu environment alebo Secret snapshot.

Pre produkčný verdict sa preto koreluje aspoň:

```text
source UID/generation
+ resolved revision/artifact digest
+ reconciler UID/generation
+ render-input generations
+ apply identity/destination
+ inventory revision
+ live object UIDs
+ running artifact/config/secret generations
+ business canary result
```

## 3. Source artifact nie je hotový release

Source lifecycle prechádza cez authentication, remote fetch, revision selection, optional authenticity verification, artifact packaging, digest calculation a publication. `Ready=True` na source objekte dokazuje, že artifact je dostupný. Nedokazuje, že downstream path existuje, SOPS decryption uspeje, manifests sú validné, target RBAC dovolí mutation, health checks convergujú alebo workload načíta novú configuration.

Retencia je tiež súčasťou reproducibility. Branch môže byť force-pushnutá a starý artifact môže existovať iba do garbage collection alebo controller recovery. Dôkaz postavený len na texte `stored artifact for main` preto nestačí. Potrebný je immutable commit, digest, timestamps a downstream `lastAppliedRevision` alebo equivalent observed revision.

Pri source outage-i má controller rozlíšiť unavailable source od úspešne potvrdenej current generation. Nemá interpretovať failed fetch alebo empty render ako príkaz zmazať celý inventory. Destructive prune musí vychádzať z úspešne zostaveného, jednoznačného desired set-u.

## 4. Kustomization ako state machine

Flux `Kustomization` Custom Resource nie je súbor `kustomization.yaml`. Je to reconciliation contract nad source artifactom a targetom. Typický flow je:

```text
source artifact change alebo Kustomization generation
→ artifact download a path selection
→ SOPS decryption
→ postBuild substitutions a patches
→ Kustomize build
→ API/schema validation
→ server-side apply
→ inventory update
→ eligible prune
→ health assessment
→ status a events
```

Každá boundary má vlastný failure dôkaz. Source fetch môže byť zelený a decryption zlyhať. Render môže prejsť a server-side apply naraziť na authorization alebo field conflict. Apply môže prejsť a health timeout vypršať. Health môže prejsť, no proces stále používa starý credential načítaný pri štarte.

`spec.interval` riadi periodické prehodnotenie a `retryInterval` častejšie retry po chybe. Príliš krátky retry pri permanentne invalidnom manifeste vytvorí hot loop nad Git serverom, KMS, API serverom a admission webhookmi. Manual reconcile iba zopakuje current pipeline; nemení broken desired state ani nenúti application process reloadnúť Secret.

## 5. Hidden render inputs a deterministic desired state

`postBuild.substitute` je explicitný input uložený v `Kustomization` spec. `substituteFrom` môže čítať ConfigMap alebo Secret. Ak critical substitution object vzniká mimo authoritative Git flow, stáva sa druhým desired-state writerom:

```text
Git commit b71f203
+ cluster-local ConfigMap route=1849
→ effective render B

rovnaký Git commit b71f203
+ ConfigMap route=1850
→ effective render A
```

Source revision už neidentifikuje effective desired state. Flux môže správne reconcile-nuť zakaždým inú kombináciu a stále reportovať `Ready=True`. Critical image, route, policy, schema alebo secret-reference inputs preto musia byť immutable, versionované v rovnakom release graph-e alebo aspoň identifikované presnou external generation a policy-bound precedence contractom.

Substitution má mať fail-closed behavior pre required variables. Empty alebo default fallback nesmie potichu zmeniť business route. Acceptance evidence musí zachytiť final render digest alebo inventory a hodnoty bezpečných generation identifiers, nie iba source commit.

## 6. Apply identity, field ownership a multi-tenancy

Flux môže aplikovať resources cez controller identity alebo impersonovanú `serviceAccountName`. Produkčný multi-tenant model preferuje environment- alebo tenant-scoped service accounts, target namespace a resource policy. Controller-global cluster-admin identity mení jeden compromised Kustomization, plugin alebo controller process na cross-tenant mutation path.

Server-side apply vytvára field ownership. Ak Flux a iný controller menia rovnaký field, môže vzniknúť apply conflict, oscillation alebo silent overwrite podľa force/ownership policy. HPA môže legitímne vlastniť replicas, External Secrets controller Secret data a Flux Pod template. Táto hranica musí byť explicitná; broad ignore alebo forced ownership nie sú náhradou za field contract.

Cross-namespace source references, remote bases, shared decryption keys a broad provider roles rozširujú trust graph. Namespace izolácia nestačí, ak production Kustomization dokáže decryptovať staging payload alebo tenant-controlled object vie zneužiť shared controller ako confused deputy.

## 7. Inventory, prune a dependencies

Inventory je Flux evidence o resources vlastnených konkrétnou reconciliation generation. Prune smie odstrániť object iba po úspešnom renderi, potvrdenom tracking/ownership vzťahu a deletion-eligibility rozhodnutí. Path rename, resource move medzi Kustomizations, controller deletion alebo failed dependency nesmú vytvoriť delete storm.

`dependsOn` vyjadruje readiness ordering medzi Flux objects. Nevykonáva distributed transaction cez database migration, provider credential a application rollout. Dependency môže byť `Ready=True` podľa technického oracle-u, hoci downstream vyžaduje konkrétnu schema alebo policy generation. Pre critical chain treba generation-aware health alebo explicitný readiness expression a následný business oracle.

Pri controller restarte musí byť možné rekonštruovať source artifact, inventory, field ownership a pending reconciliation z durable cluster state-u. In-memory knowledge nesmie byť jedinou ochranou pred duplicate hookom alebo unsafe prune.

## 8. HelmRelease a image automation

`HelmRelease` má odlišný lifecycle od Kustomization apply. Upgrade môže vytvoriť hooks, migrations alebo external side effects. Automatický rollback/remediation nie je bezpečný, ak database migration je nevratná alebo provider operation má unknown outcome. Helm success, tests a release history sa musia viazať na exact chart, values, source artifact a target state.

Image automation používa registry observation a policy na vytvorenie Git commit-u:

```text
registry tags/digests
→ ImagePolicy selection
→ ImageUpdateAutomation commit
→ Git review/promotion boundary
→ source artifact
→ reconciliation
```

Ak automation zapisuje do shared base-u konzumovaného stagingom aj production, jeden registry event môže obísť environment promotion. Bez immutable release manifestu a target-specific evidence sa image automation stáva skrytou production authority.

## 9. Connected incident `GITOPS-PAY-62`

Pre release `payments 9.1` mala staging evidence potvrdiť `pay910a`, route generation `1850` a credential contract `pv-42`. Kým promotion čakala na approval, image automation prepísala shared base na `pay910b` a LaunchPad zmenil cluster-local substitution ConfigMap na route `1849`. Merge automation proposal rebase-la bez final-render a evidence revalidation.

Timeline bola presná:

```text
10:02:11 image automation commitne pay910a
10:08:44 staging canary prejde na route 1850
10:11:03 promotion načíta staging evidence
10:12:17 shared base sa zmení na pay910b
10:13:04 LaunchPad zmení route substitution na 1849
10:14:22 promotion PR merge
10:15:01 production source artifact b71f203
10:15:09 Flux aplikuje pay910b + route 1849
10:16:31 Kustomization Ready=True
```

Flux lokálne vykonal svoj contract: resolve-ol artifact, vyrenderoval current inputs, aplikoval objects a získal technical readiness. Root cause bol neúplný Flux subject. Artifact `b71f203` neidentifikoval critical cluster-local substitution ani shared-base generation, a health oracle nekontroloval runtime route, loaded credential ani settlement canary.

Výsledkom bolo `2 746` settlements cez stale route `1849`. Po neskoršej revokácii `pv-42` zlyhalo `61` provider calls a `14` unknown outcomes vyžadovalo reconciliation. `Ready=True` teda nebolo nepravdivé ako controller condition; bolo nesprávne použité ako end-to-end release verdict.

## 10. Authoritative redesign a acceptance paths

Redesign používa immutable release manifest `R-910a`, ktorý pinne image, chart, policy, schema a secret-reference contract. Staging aj production odkazujú na rovnaký release subject, no každé prostredie má vlastný immutable source coordinate, scoped apply identity a environment-specific decryption identity. Critical substitutions sú v authoritative environment source, nie v cluster-local ConfigMap-e.

```text
R-910a + exact environment revision
→ Flux artifact digest
→ deterministic final render
→ namespace-scoped apply
→ inventory a health
→ runtime generation endpoint
→ settlement canary
→ accepted operation
```

Positive path potvrdí rovnaký release manifest, render a runtime generations. Recovery path po source, KMS alebo API outage-i obnoví controller a preukáže second reconciliation bez duplicate side effectu. Drift path opraví direct Git-owned mutation bez zásahu do HPA-owned fields. Failure path odmietne prune pri failed alebo ambiguous renderi. Forbidden path odmietne hidden substitution, shared decryption authority, cross-tenant apply, stale promotion, false-Ready a image automation obchádzajúcu promotion.

## 11. Troubleshooting a kontrolné otázky

Pri wrong generation sa postupuje od source authority k materializovanému outcome-u:

```text
installation/controller generation
→ source UID, ref, resolved revision a artifact digest
→ Kustomization/HelmRelease observed revision
→ path, decryption, substitutions a dependencies
→ apply service account, managedFields a API result
→ inventory, prune a health
→ ReplicaSet/Pod artifact generation
→ loaded config/secret/provider generation
→ business canary
```

Kontrolné otázky: Prečo source readiness nie je deployment readiness? Ktoré inputs menia final render mimo source artifactu? Čo dokazuje inventory a čo ešte nedokazuje? Ako sa `dependsOn` líši od atomic dependency transitionu? Kedy je image automation iba candidate writer a kedy production authority? Ako overíš controller restart, second reconcile a forbidden cross-tenant mutation?

## Glossary impact

Relevantné pojmy: Flux subject, source artifact, resolved revision, Kustomization reconciliation, HelmRelease lifecycle, observed revision, hidden substitution, Flux inventory, prune eligibility, apply identity, server-side apply ownership, generation-aware dependency, image automation writer, false-Ready a Flux acceptance verdict.

## Primárne zdroje

- [Flux — Components](https://fluxcd.io/flux/components/)
- [Flux — Source Controller](https://fluxcd.io/flux/components/source/)
- [Flux — Kustomization](https://fluxcd.io/flux/components/kustomize/kustomizations/)
- [Flux — Helm Controller](https://fluxcd.io/flux/components/helm/)
- [Flux — Image Automation](https://fluxcd.io/flux/components/image/)
- [Flux — Security best practices](https://fluxcd.io/flux/security/best-practices/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Argo CD](argo-cd.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Application promotion →](application-promotion.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
