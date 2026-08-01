# RBAC

Kubernetes RBAC rozhoduje, či autentizovaná identita smie vykonať konkrétny verb nad konkrétnym API resource-om v konkrétnom scope. Neurčuje, kto identita je; to patrí authentication vrstve. Nechráni ani všetky external systémy, ku ktorým workload pristupuje cez cloud identity. RBAC je jedna authorization rovina v širšom identity a privilege modeli.

Pre `payments-api` chceme minimálny workload ServiceAccount bez práva čítať Secrets alebo meniť workloads. Release pipeline smie server-side apply-nuť Deployment a Service v namespace `production`, ale nesmie vytvárať ClusterRoleBinding ani meniť admission webhooks. Platform operator má širšie práva, no používa samostatnú identitu a audit.

## Role a ClusterRole

Namespaced Role:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: payments-config-reader
  namespace: production
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["payments-api-runtime-metadata"]
    verbs: ["get"]
```

Role platí v jednom namespace. ClusterRole je cluster-scoped definition rules. Možno ju použiť pre cluster-scoped resources alebo ju cez RoleBinding sprístupniť iba v jednom namespace pre namespaced resources.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: namespace-deployment-reader
rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch"]
```

Samotná Role alebo ClusterRole nikomu práva nepridelí. Potrebný je binding.

## RoleBinding a ClusterRoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: payments-config-reader
  namespace: production
subjects:
  - kind: ServiceAccount
    name: payments-api
    namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: payments-config-reader
```

RoleBinding prideľuje rules v namespace bindingu. Môže odkazovať aj na ClusterRole, no stále obmedzí namespaced access na svoj namespace.

ClusterRoleBinding prideľuje rules cluster-wide podľa rule scope. Je vhodný iba pre identity, ktoré skutočne potrebujú cluster-wide authority.

```yaml
kind: ClusterRoleBinding
```

Rozdiel jedného slova môže zmeniť blast radius z jedného namespace na celý cluster.

## Verbs a resources

Bežné verbs:

```text
get, list, watch
create, update, patch, delete
use, bind, escalate, impersonate
```

`get` číta jeden objekt. `list` môže čítať všetky objekty daného typu v scope. `watch` poskytuje priebežné zmeny a často vyžaduje rovnakú citlivosť ako list.

`patch` môže byť širšie, než vyzerá. Právo patchovať Deployment template umožňuje spustiť ľubovoľný image alebo zmeniť ServiceAccount, volumes a security context v hraniciach admission policies.

## API groups a subresources

Pods sú v core group `""`, Deployments v `apps`, RBAC resources v `rbac.authorization.k8s.io`.

Subresources majú vlastné rules:

```yaml
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]

- apiGroups: [""]
  resources: ["pods/exec"]
  verbs: ["create"]
```

Právo čítať Pod objekt automaticky nemusí povoľovať logs. `pods/exec` je výrazne silnejšie než read: umožňuje spustiť process v existujúcom runtime a získať jeho credentials alebo data.

Scale subresource:

```yaml
- apiGroups: ["apps"]
  resources: ["deployments/scale"]
  verbs: ["get", "update", "patch"]
```

HPA potrebuje scale contract bez práva meniť celý Pod template.

## `resourceNames`

`resourceNames` môže zúžiť `get`, `update`, `patch` alebo delete na konkrétne mená podľa verb/resource semantics.

```yaml
resourceNames:
  - payments-api-runtime-metadata
```

Nejde o univerzálny filter pre `list` alebo `create`. Pri každom pravidle over, či API request vôbec nesie resource name v authorization attributes.

## Wildcards a budúce resources

```yaml
apiGroups: ["*"]
resources: ["*"]
verbs: ["*"]
```

Wildcard nie je iba prístup k dnešným objektom. Môže automaticky zahrnúť nové API groups, CRDs alebo subresources pridané v budúcnosti. Broad roly preto časom rastú bez explicitného review.

Built-in `cluster-admin` je break-glass alebo platform-admin authority, nie aplikačný default.

## Agregované ClusterRoles

Kubernetes môže agregovať ClusterRoles podľa labels do rolí ako `admin`, `edit` alebo `view`. Inštalovaný CRD môže pridať rules do agregovanej roly.

To zlepšuje integráciu, ale mení effective permissions po inštalácii nového operatora. Audit nemá čítať iba pôvodný YAML roly; musí čítať resolved rules.

```bash
kubectl get clusterrole <name> -o yaml
```

## Kontrola permissions

```bash
kubectl auth can-i get configmap/payments-api-runtime-metadata \
  -n production \
  --as=system:serviceaccount:production:payments-api

kubectl auth can-i list secrets \
  -n production \
  --as=system:serviceaccount:production:payments-api
```

Pre inventár:

```bash
kubectl auth can-i --list \
  -n production \
  --as=system:serviceaccount:production:payments-api
```

`can-i` vyhodnocuje authorization policy API servera. Nemusí zachytiť následné admission odmietnutie ani external cloud permissions. Je to permission test, nie end-to-end operation verdict.

## `bind` a `escalate`

API server chráni vytváranie rolí a bindingov pred privilege escalation. Identita bez `escalate` nemá vytvoriť rolu obsahujúcu permissions, ktoré sama nemá. Identita bez `bind` nemá bindnúť rolu s vyššími právami, než smie prideliť.

Explicitné `bind` alebo `escalate` rules sú veľmi silné a majú byť obmedzené na platform automation s reviewom.

```text
právo vytvoriť RoleBinding
≠ právo bindnúť ľubovoľný cluster-admin roleRef
```

Presné enforcement závisí od requestu a caller permissions; testuj forbidden path.

## Impersonation

Právo `impersonate` môže umožniť request ako iný user, group alebo ServiceAccount.

```bash
kubectl get pods -n production \
  --as=system:serviceaccount:production:payments-api
```

Použitie funguje iba ak caller smie impersonovať daný subject. Broad impersonation je prakticky privilege-escalation mechanismus a potrebuje audit.

## Workload creation ako nepriama authority

Identita, ktorá smie vytvárať Pods, môže:

- vybrať povolený ServiceAccount,
- mountnúť dostupný Secret,
- použiť hostPath alebo privileged context, ak admission dovolí,
- spustiť image s vlastným kódom,
- pristúpiť k network a cloud metadata podľa platformy.

Preto „nemá get secrets“ nemusí znamenať „nevie získať secret“. Admission, ServiceAccount use policy, Pod Security a node isolation musia doplniť RBAC.

## Update workloadu ako code execution

Právo patchovať Deployment často znamená code execution v príslušnom namespace. Caller môže zmeniť image na vlastný, pridať command alebo mount.

Release pipeline s týmto právom je high-value identity. Potrebuje short-lived credentials, protected branch, immutable artifact policy, admission a audit. Nemá zároveň spravovať RBAC alebo secrets bez dôvodu.

## Namespaces nie sú automatická tenant isolation

RoleBinding v namespace obmedzuje namespaced API resources. Cluster-scoped resources, Nodes, PVs, webhooks, CRDs a shared controllers zostávajú mimo. Network a storage isolation sú samostatné.

Multi-tenant cluster potrebuje kombináciu:

```text
RBAC
+ admission
+ Pod Security
+ NetworkPolicy
+ quota
+ node/runtime isolation
+ secret a cloud identity boundaries
+ audit
```

## Auto-reconciliation built-in roles

Kubernetes môže pri štarte API servera obnovovať niektoré default ClusterRoles a bindings podľa bootstrap policy. Ručná editácia built-in system roles môže byť prepísaná alebo poškodiť control plane.

Vlastné permissions je bezpečnejšie pridávať cez samostatné role než mutovať `system:` objekty bez explicitného platform dôvodu.

## Audit a permission drift

RBAC objekty sú desired policy. Skutočný request audit ukazuje, ktorá identita a groups boli použité a aký verdict vznikol.

Pravidelne kontroluj:

```text
subjects bez ownera
bindings na deleted ServiceAccounts
wildcard rules
cluster-wide bindings
pods/exec a impersonate
bind/escalate
aggregate role growth
workload creation + secret/cloud paths
```

Permission review má byť viazaný na business capability, nie iba na technický zoznam verbs.

## Incident: read-only rola umožnila čítať Secrets

Tím použil agregovanú ClusterRole `view` rozšírenú custom CRD balíkom. Vendor ClusterRole s aggregation labelom omylom obsahovala `get,list` na Secrets. Effective `view` sa rozšírila v celom clustri.

Source bindingy sa nezmenili, no permissions áno. Oprava odstránila chybnú aggregation rolu, rotovala exposed credentials podľa audit evidence a pridala resolved-rule diff do addon upgrade gate-u.

## Incident: CI nemalo RBAC admin, ale eskalovalo cez Deployment

Pipeline mohla patchovať Deployment v production. Zmenila image a pridala mount existujúceho high-privilege ServiceAccount tokenu cez workload, pretože admission neobmedzovala použitie ServiceAccountu. Následne získala API authority širšiu než vlastná CI identita.

RBAC pipeline identity bolo úzke iba na prvý pohľad. Oprava oddelila deployable ServiceAccounts, zaviedla admission policy na serviceAccountName a vypínala token automount tam, kde nebol potrebný.

## Incident: RoleBinding bolo vytvorené v nesprávnom namespace

RoleBinding v `staging` odkazovalo na ServiceAccount `payments-api` v `production`, ale subject namespace bol omylom `staging`. Production Pod nemal permission a staging Pod ju dostal.

Meno ServiceAccountu bolo rovnaké. Oprava explicitne overila subject namespace a pridala permission tests pre allowed production a forbidden staging identity.

## Model, ktorý si treba odniesť

RBAC spája autentizovaný subject, verb, API group, resource, subresource a scope. Role rules sa aktivujú až bindingom. Effective authority zahŕňa aj workload creation, exec/debug, bind/escalate, impersonation, aggregated roles, admission a external cloud identity. Least privilege sa dokazuje allowed aj forbidden requestmi a auditom, nie iba čítaním jedného YAML-u.

## Referencie

- [Using RBAC Authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Authorization Overview](https://kubernetes.io/docs/reference/access-authn-authz/authorization/)
- [Auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)
