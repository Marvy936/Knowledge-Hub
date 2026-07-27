# RBAC

Kubernetes RBAC nevyhodnocuje názov role izolovane. Authorizer dostane už autentifikovaný request subject, verb, API group, resource/subresource, namespace a ďalšie request attributes. Potom vytvorí efektívny allow graph zo všetkých matching RoleBindings, ClusterRoleBindings, group memberships a agregovaných ClusterRoles. RBAC je aditívne: jeden užší binding neodoberie permission udelenú inou cestou.

Táto kapitola používa jeden dominantný lifecycle:

```text
operation intent a threat model
→ authenticated subject, groups a credential generation
→ exact API request attributes
→ Roles/ClusterRoles a aggregation generation
→ RoleBindings/ClusterRoleBindings a scope
→ effective allow graph a authorizer verdict
→ admission/runtime/indirect capability consequences
→ auditovaný operation a business outcome
→ revocation, credential rotation a verification
→ skorší control
```

## 1. Atlas Payments authorization subject

ServiceAccount `system:serviceaccount:production:atlas-release-controller` má vykonávať iba release operácie v namespace `production`:

```text
get/list/watch Pods a ReplicaSets
get pods/log
get/patch Deployments
get/patch deployments/scale iba ak to nevlastní HPA
create/get/watch presne definovaných migration Jobs
žiadne Secrets
žiadne pods/exec alebo portforward
žiadna tvorba ľubovoľných Pods
žiadne RBAC management permissions
žiadny cluster-scoped write
```

Pri incidente fixuj:

```text
credential/token generation a audience
authenticated user, groups a extra attributes
verb, API group, resource/subresource, namespace a resourceName
Role/ClusterRole UID, generation a resolved rules
RoleBinding/ClusterRoleBinding UID, subject a roleRef
aggregated ClusterRole membership
authorizer chain a verdict
audit event a response code
indirect workload/controller capability
business operation a forbidden outcome
```

Názov ServiceAccount alebo jediný RoleBinding nie je efektívny permission subject.

## 2. Authentication, authorization a admission sú rozdielne boundaries

API request prechádza:

```text
credential
→ authentication
→ user/groups/extras
→ authorization
→ admission
→ storage/controller/runtime effect
```

`401 Unauthorized` typicky znamená, že request nemá prijateľnú autentifikovanú identitu. `403 Forbidden` znamená, že identita je známa, ale autorizačný verdict request nepovolil.

RBAC success ešte nepreukazuje admission success. Caller môže mať `create pods`, ale Pod Security, quota alebo validating policy objekt odmietne. Naopak povolené vytvorenie workloadu môže po admission viesť k ďalším nepriamym credentials, network a runtime capabilities.

## 3. Request attributes musia byť exact

RBAC pravidlo porovnáva najmä:

```text
subject a groups
verb
API group
resource alebo non-resource URL
subresource
namespace
resourceName, ak je použiteľné
```

Príklady rozdielnych requests:

```text
get pods
get pods/log
create pods/exec
patch deployments
patch deployments/scale
update deployments/status
```

Permission na parent resource automaticky neznamená permission na subresource. `kubectl logs` potrebuje `pods/log`; `kubectl exec` sa autorizuje ako operácia na `pods/exec`, typicky s verbom `create`.

Kind v manifeste nie je resource name v RBAC. `Deployment` patrí k resource `deployments` v API group `apps`.

## 4. Štyri objekty tvoria reusable rules a scope

### Role

Namespaced ruleset. Môže obsahovať permissions na resources použiteľné v danom namespace.

### ClusterRole

Cluster-scoped ruleset. Môže obsahovať cluster-scoped resources, reusable namespaced permissions a non-resource URLs.

### RoleBinding

Viaže Role alebo ClusterRole na subjects v jednom namespace. Ak odkazuje na ClusterRole, namespaced permissions sa uplatnia iba v namespace RoleBindingu.

### ClusterRoleBinding

Viaže ClusterRole na subjects cluster-wide.

`roleRef` je stabilná reference na ruleset. Ak potrebuješ zmeniť referencovanú rolu, binding lifecycle musí zostať auditovateľný; nemeniteľnosť `roleRef` bráni tichej transformácii existujúceho bindingu na úplne inú autoritu.

## 5. Subjects a group membership sú súčasť effective graphu

Binding subject môže byť:

- `User`;
- `Group`;
- `ServiceAccount`.

Human users/groups typicky vlastní external identity provider. ServiceAccount má namespaced API identity a pri autentifikácii patrí aj do štandardných skupín, napríklad namespace-wide service-account groupy a authenticated groupy.

Efektívna permission cesta preto môže byť:

```text
ServiceAccount explicitne v RoleBindingu
alebo
ServiceAccount namespace group v ClusterRoleBindingu
alebo
širšia authenticated group v inom bindingu
```

Revokácia explicitného bindingu nemusí zrušiť access, ak zostáva group-based cesta.

## 6. RBAC je union allow graph bez explicitného deny

Výsledok možno modelovať:

```text
všetky bindings matching subject alebo group
→ referenced Roles/ClusterRoles
→ resolved aggregated rules
→ union všetkých matching allow rules
→ allow, ak aspoň jedna cesta matchuje request
```

Prísnejšia Role neodoberie širšiu permission. Poradie bindings neexistuje. Effective access review musí agregovať všetky paths.

Ak potrebuješ deny, kontextové podmienky alebo object-content policy, použi vhodnú kombináciu admission, ďalšieho authorizera, namespace/trust-domain rozdelenia a external governance. Neimplementuj deny vytvorením „prázdnej“ Role.

## 7. Namespaced scope nie je automaticky malý blast radius

RoleBinding obmedzuje namespaced resources na konkrétny namespace, ale samotné permissions môžu byť veľmi silné:

- create/update Pods alebo workload controllers;
- read Secrets;
- `pods/exec`, `pods/attach`, `pods/portforward`;
- create Jobs, ktoré použijú privilegovaný ServiceAccount;
- update workload image alebo command;
- proxy k Services/Pods;
- patch scale/status subresources.

Kto môže vytvoriť alebo meniť workload, môže často nepriamo:

```text
vybrať ServiceAccount
→ dostať projected token a mounted data
→ použiť internal network identity
→ spustiť image/command
→ získať capabilities povolené admission/runtime policy
```

RBAC preto musí byť hodnotené spolu so ServiceAccount, Pod Security, NetworkPolicy, Secret a Node/runtime boundaries.

## 8. Least privilege je operation contract, nie zoznam pohodlných verbs

Pre každú identitu definuj:

```text
business operation
→ exact API requests
→ exact namespaces/resources/subresources
→ read/write/scale/status ownership
→ čas a environment scope
→ forbidden operations
```

Preferuj:

- samostatný ServiceAccount per workload/controller;
- RoleBinding namiesto ClusterRoleBinding, ak stačí namespace;
- explicitné API groups, resources a verbs;
- oddelené read, deploy, debug a break-glass roles;
- krátkodobé human grants;
- permission tests pre allowed aj forbidden requests;
- audit a usage-based review.

`resourceNames` môže zúžiť niektoré existing-object requests, ale nie je všeobecná object-level authorization vrstva. `create`, `list/watch` a `deletecollection` majú odlišné semantics a limity; pri silnej object-content policy použi admission alebo iný boundary.

## 9. Wildcards a budúce API surface

```yaml
apiGroups: ["*"]
resources: ["*"]
verbs: ["*"]
```

Wildcard neznamená iba dnešné API. Môže automaticky zahrnúť budúce resources/subresources po upgrade alebo inštalácii CRD. Review musí hodnotiť expected future expansion a extension controllers, nie iba current `kubectl api-resources` output.

Aj read-only wildcard môže odhaliť nové credential-like CRD data alebo status fields. Write wildcard môže ovládať controller, ktorý vytvára cloud, backup alebo identity resources mimo clusteru.

## 10. Aggregated ClusterRoles menia resolved ruleset

ClusterRole môže mať aggregation rule alebo patriť do agregovanej používateľskej role cez labels. Operator/CRD install alebo upgrade môže pridať nový ClusterRole do existujúceho `view`, `edit` alebo `admin`-like rulesetu.

```text
binding sa nezmení
→ aggregated member role sa pridá alebo zmení
→ resolved ClusterRole rules sa rozšíria
→ existujúce subjects získajú novú capability
```

Audituj resolved rules a aggregation members. Pôvodný Git manifest parent role nemusí obsahovať všetky effective permissions.

## 11. Špeciálne privilege-escalation verbs

### `bind`

Umožňuje vytvoriť binding na referencovanú rolu aj mimo bežnej ochrany, ktorá vyžaduje, aby caller už mal udeľované permissions.

### `escalate`

Umožňuje vytvoriť alebo zmeniť Role/ClusterRole s permissions nad vlastný current permission set.

### `impersonate`

Umožňuje poslať request ako iný user, group, ServiceAccount alebo identity attribute. Impersonation permissions sú cluster-scoped a musia byť úzko ohraničené a auditované.

### CSR create/approve

Kombinácia vytvorenia CertificateSigningRequest, approval permission a citlivého signer contractu môže vydať nový klientsky credential.

Tieto verbs nie sú administratívne detaily. Sú explicitné edges v privilege-escalation graph-e.

## 12. Proxy, exec a debug subresources sú runtime authority

Citlivé permissions zahŕňajú:

```text
pods/exec
pods/attach
pods/portforward
pods/proxy
services/proxy
nodes/proxy
pods/log
```

`pods/log` môže obsahovať secrets alebo tenant data. `pods/exec` môže čítať mounted tokeny a volať internal Services. `nodes/proxy` alebo kubelet access môže obísť niektoré bežné API/admission observation paths.

Debug access preto potrebuje samostatný časovo obmedzený role, user attribution, audit a incident handling; nemá byť automatickou súčasťou deploy identity.

## 13. Worked failure: odstránený binding, permission zostala

Po incidente tím odstránil RoleBinding, ktorý povoľoval release controlleru `get secrets`. Očakávanie bolo okamžité odobratie accessu.

Stav:

```text
explicitný RoleBinding odstránený
→ existujúci projected token stále autentifikuje rovnaký ServiceAccount
→ kubectl auth can-i get secrets --as=... stále vracia yes
→ audit log ukazuje úspešný get secrets
```

Root cause bol starý ClusterRoleBinding:

```text
subject Group: system:serviceaccounts:production
→ ClusterRole atlas-bootstrap-operators
→ rules obsahujú get/list secrets
```

Permission nebola stale cache ani vlastnosť tokenu. RBAC union graph stále obsahoval group-based allow path. Samotná rotácia tokenu bez odstránenia bindingu by vydala novému tokenu rovnakú autoritu.

## 14. Causal troubleshooting walkthrough

### Exact subject a request

Fixuj token/credential generation, autentifikovaný user/groups, verb, API group, resource/subresource, namespace/resourceName, response code, audit event ID a čas. Nepoužívaj iba display meno pipeline alebo Kubernetes object name.

### Competing hypotheses

1. authentication zlyháva alebo token má nesprávnu audience;
2. request používa inú ServiceAccount/namespace než očakávanie;
3. explicitný RoleBinding má nesprávny subject alebo roleRef;
4. ďalší RoleBinding povoľuje request;
5. ClusterRoleBinding povoľuje subject priamo;
6. group membership vytvára inú allow path;
7. aggregated ClusterRole rozšíril rules;
8. subresource potrebuje iný verb/resource;
9. `resourceNames`/list/watch semantics nezodpovedajú klientovi;
10. iný authorizer než RBAC povoľuje alebo odmieta request;
11. admission blokuje request po RBAC allow;
12. workload create permission poskytuje indirect capability;
13. credential mohol byť exfiltrovaný a používaný inde;
14. audit/query porovnáva iný request generation.

### Discriminating observations

```bash
kubectl auth can-i get secrets \
  --as=system:serviceaccount:production:atlas-release-controller \
  --namespace production

kubectl auth can-i --list \
  --as=system:serviceaccount:production:atlas-release-controller \
  --namespace production

kubectl get rolebindings -A -o yaml
kubectl get clusterrolebindings -o yaml
kubectl get roles,clusterroles -o yaml
```

Použi SubjectAccessReview pre exact request a audit log pre actual authenticated user/groups. Zostroj permission paths:

```text
subject/group
→ binding
→ roleRef
→ resolved rule/aggregation member
→ request match
```

Over aj authorizer configuration, admission denial a indirect controller effects. `kubectl auth can-i` je authorization observation, nie dôkaz celej runtime/business cesty.

### Containment

Pozastav kompromitovanú pipeline/workload, zablokuj ďalšie secret reads a zachovaj audit logs, binding/rules snapshots a token issuance metadata. Ak credential mohol uniknúť, zruš jeho použiteľnosť a rotuj downstream secrets; samotné odstránenie RBAC path nevráti už prečítané credentials.

### Authoritative recovery

- odstráň všetky direct aj group-based broad bindings;
- vytvor dedicated ServiceAccount a explicitný namespaced ruleset;
- oddeľ deploy, migration, debug a break-glass permissions;
- odstráň `create pods`, Secrets, exec/proxy a RBAC management, ak nie sú nevyhnutné;
- oprav aggregated role labels alebo nepoužívaj broad parent rolu;
- rotuj exfiltrované tokeny/secrets a redeployni consumers;
- versionuj a aplikuj nový access graph;
- vykonaj exact allowed aj forbidden request tests.

### Verify original a forbidden outcomes

Over:

1. release controller vie vykonať schválený deployment;
2. nevie `get/list/watch` Secrets;
3. nevie `create pods`, `pods/exec`, `portforward` ani proxy;
4. nevie bind/escalate/impersonate alebo meniť RBAC;
5. nemá cluster-wide write;
6. old credential a downstream secrets sú neplatné;
7. audit eventy korelujú s dedicated identity;
8. iná ServiceAccount alebo namespace group nezdieľa permission;
9. GitOps/release workflow neobchádza access cez iný controller;
10. admission/runtime boundaries stále blokujú forbidden workload capabilities.

### Earlier controls

Použi permission-as-code tests, explicitný subject/group inventory, zákaz broad service-account group bindings, aggregated-role diff gate, workload-create escalation review, quarterly usage review, short-lived credentials, audit alerty na Secrets/exec/RBAC a oddelený break-glass workflow.

## 15. Ďalšie failure boundaries

### `get pods` funguje, `logs` nie

`pods/log` je subresource. Oprav exact rule; nepridávaj wildcard na všetky Pod subresources.

### `exec` je forbidden

Over `create` na `pods/exec`, ale najprv potvrď, či deploy identita má vôbec mať runtime shell authority.

### RoleBinding na ClusterRole je širší než očakávanie

Namespace scope obmedzí namespaced resources, ale ruleset môže obsahovať citlivé subresources. Prečítaj resolved ClusterRole, nie iba názov.

### Permission vznikla po operator upgrade

Skontroluj aggregated ClusterRole members, nové CRDs a external controller semantics. Binding sa nemusel zmeniť.

### Caller môže vytvoriť Pod, ale nemôže čítať Secret API

Môže vytvoriť workload, ktorý Secret mountne alebo použije ServiceAccount s vyššou autoritou, ak admission a secret policy tomu nebránia. Hodnoť indirect capability graph.

### `resourceNames` nefunguje pri list/watch

Klient a request musia používať kompatibilný field selector; object-name rule nie je všeobecný filter všetkých collection operations.

### Revokácia RBAC neukončila external access

Credential už mohol byť prečítaný a použitý mimo Kubernetes API. Potrebná je provider-side revokácia a downstream rotácia.

## 16. Referenčný katalóg

### Objekty a scope

| Objekt | Ruleset/binding | Scope |
|---|---|---|
| Role | rules | namespace |
| ClusterRole | rules | cluster object; rules môžu byť cluster alebo namespaced |
| RoleBinding | subjects → Role/ClusterRole | jeden namespace |
| ClusterRoleBinding | subjects → ClusterRole | cluster-wide |

### Bežné verbs

- `get`, `list`, `watch`;
- `create`, `update`, `patch`;
- `delete`, `deletecollection`;
- špeciálne `bind`, `escalate`, `impersonate` a API-specific actions.

### Authorization review APIs

- SelfSubjectAccessReview;
- SubjectAccessReview;
- LocalSubjectAccessReview;
- SelfSubjectRulesReview.

Rules review môže byť neúplný pri kombinácii authorizerov; exact access review a actual audit request zostávajú dôležité.

### Access evidence matrix

```text
authenticated subject/groups
exact request attributes
all binding paths
resolved role rules a aggregation
RBAC/other authorizer verdict
admission verdict
runtime/controller effect
audit a business outcome
```

## 17. Anti-patterny

- `cluster-admin` pre CI/CD alebo GitOps;
- jedna zdieľaná ServiceAccount pre všetky aplikácie;
- wildcard pre budúcu pohodlnosť;
- Role považovaná za deny policy;
- `edit`/`admin` názov považovaný za stabilný pri CRD aggregation;
- create workload permissions bez indirect escalation analýzy;
- permanentný exec/debug access v deploy role;
- ručná editácia defaultných `system:` rolí;
- revokácia bindingu bez group-path a credential rotation kontroly;
- authorization success považovaný za business operation success.

## 18. Kontrolné otázky

1. Ktoré exact request attributes RBAC porovnáva?
2. Ako sa líši Role, ClusterRole, RoleBinding a ClusterRoleBinding?
3. Prečo je ServiceAccount group membership súčasť permission graphu?
4. Prečo užšia Role neodoberie access z iného bindingu?
5. Ako sa líši `pods`, `pods/log` a `pods/exec` authorization?
6. Ako aggregated ClusterRole zmení permissions bez zmeny bindingu?
7. Prečo create Pod permission môže byť privilege escalation?
8. Akú autoritu poskytujú `bind`, `escalate` a `impersonate`?
9. Prečo odstránenie RBAC path nemusí uzavrieť secret incident?
10. Ako overíš allowed aj forbidden business outcomes po recovery?

## Glossary impact

Relevantné pojmy: authorization request subject, credential generation, request-attribute identity, effective RBAC graph, permission path, group-derived permission, additive allow verdict, resolved ClusterRole rules, aggregation generation, subresource authority, scale-field permission, indirect workload capability, RBAC revocation subject, credential-after-revocation risk, forbidden-operation verification a subject-bound authorization closure.

## Oficiálna dokumentácia

- [Using RBAC Authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [RBAC Good Practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
- [Authorization Overview](https://kubernetes.io/docs/reference/access-authn-authz/authorization/)
- [User Impersonation](https://kubernetes.io/docs/reference/access-authn-authz/user-impersonation/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: HPA a autoscaling](hpa-autoscaling.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: SecurityContext a Pod Security →](securitycontext-pod-security.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
