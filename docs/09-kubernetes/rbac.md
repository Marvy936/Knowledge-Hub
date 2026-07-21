# RBAC

Kubernetes Role-Based Access Control (RBAC) rozhoduje, či už autentifikovaná identita smie vykonať konkrétnu akciu nad API resource-om alebo non-resource URL. RBAC je authorization vrstva, nie authentication mechanizmus. Identita môže pochádzať z používateľského certifikátu, OIDC, ServiceAccount tokenu, Node identity alebo iného authenticatora.

## 1. Request authorization model

Zjednodušený request flow:

```text
request
→ authentication
→ user, groups a extra attributes
→ authorization
→ admission
→ API operation
```

RBAC hodnotí najmä:

- subject identity,
- verb,
- API group,
- resource a subresource,
- namespace,
- resource name podľa pravidla,
- non-resource URL.

## 2. Štyri hlavné objekty

### Role

Namespaced pravidlá:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: config-reader
  namespace: production
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list", "watch"]
```

### ClusterRole

Cluster-scoped ruleset. Môže obsahovať:

- cluster-scoped resources,
- namespaced resources použiteľné vo viacerých namespaces,
- non-resource URLs.

### RoleBinding

Viaže Role alebo ClusterRole na subjects v jednom namespace.

### ClusterRoleBinding

Viaže ClusterRole cluster-wide.

## 3. RoleBinding na ClusterRole

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: config-reader
  namespace: production
subjects:
  - kind: ServiceAccount
    name: web
    namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: config-reader
```

ClusterRole definuje reusable ruleset, ale RoleBinding obmedzí účinok namespaced permissions na namespace bindingu.

## 4. Subjects

Binding môže odkazovať na:

- `User`,
- `Group`,
- `ServiceAccount`.

ServiceAccount subject musí mať namespace:

```yaml
subjects:
  - kind: ServiceAccount
    name: web
    namespace: production
```

Human users a groups nie sú bežné persistent Kubernetes API objekty. Ich lifecycle typicky vlastní external identity provider.

## 5. API groups a resources

Core API group sa zapisuje ako prázdny string:

```yaml
apiGroups: [""]
resources: ["pods", "configmaps"]
```

Named API group:

```yaml
apiGroups: ["apps"]
resources: ["deployments"]
```

Resource meno je plural API resource, nie Kind:

```text
Kind: Deployment
resource: deployments
```

## 6. Verbs

Bežné verbs:

- `get`,
- `list`,
- `watch`,
- `create`,
- `update`,
- `patch`,
- `delete`,
- `deletecollection`.

Špeciálne authorization verbs zahŕňajú napríklad:

- `bind`,
- `escalate`,
- `impersonate`,
- `approve` alebo signer-specific činnosti podľa API.

`get` jedného objektu nie je to isté ako `list` všetkých objektov v namespace.

## 7. Subresources

Subresource sa v RBAC zapisuje cez lomku:

```yaml
rules:
  - apiGroups: [""]
    resources: ["pods/log"]
    verbs: ["get"]
  - apiGroups: [""]
    resources: ["pods/exec"]
    verbs: ["create"]
```

Citlivé subresources:

- `pods/exec`,
- `pods/attach`,
- `pods/portforward`,
- `pods/proxy`,
- `services/proxy`,
- `nodes/proxy`,
- `deployments/scale`,
- resource `/status` subresources.

Prístup k Pod exec môže viesť k čítaniu mounted credentials, network accessu alebo control-plane tokenu.

## 8. `resourceNames`

```yaml
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["public-settings"]
    verbs: ["get", "update"]
```

Obmedzenie podľa mena má limity:

- pri `create` ešte objekt nemá existujúcu identity autorizovateľnú rovnakým spôsobom,
- `list`/`watch` vyžadujú zodpovedajúci field selector a klientsku podporu,
- `deletecollection` nemožno bezpečne zúžiť na jedno meno.

Pre silnú object-level policy môže byť potrebná admission policy alebo oddelenie namespaces.

## 9. Non-resource URLs

ClusterRole môže povoliť URL mimo resource API:

```yaml
rules:
  - nonResourceURLs: ["/healthz", "/readyz"]
    verbs: ["get"]
```

Non-resource URL pravidlá sú cluster-scoped a viažu sa cez ClusterRoleBinding.

## 10. RBAC je aditívne

Kubernetes RBAC nemá explicitný deny rule. Výsledné oprávnenia sú union všetkých matching bindings.

To znamená:

- prísnejšia Role neodoberie permission udelenú iným bindingom,
- odstránenie jedného bindingu nemusí odobrať prístup,
- audit musí agregovať všetky role bindings a group memberships.

Deny alebo kontextové policy typicky riešia admission, webhook authorizer, external identity/governance alebo oddelenie trust domains.

## 11. Least privilege

Navrhuj permissions podľa konkrétneho use case:

```yaml
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["web-runtime"]
    verbs: ["get"]
```

Preferuj:

- explicitné resources,
- explicitné verbs,
- namespace RoleBinding,
- oddelené read a write roles,
- samostatný ServiceAccount pre každý workload,
- krátkodobé human access grants,
- pravidelný access review.

## 12. Wildcards

```yaml
apiGroups: ["*"]
resources: ["*"]
verbs: ["*"]
```

Wildcard udeľuje aj prístup k budúcim resources alebo subresources pridaným po upgrade. Je preto výrazne širší než aktuálny zoznam.

Cluster-admin-like wildcard permissions patria iba úzko kontrolovaným break-glass alebo platformovým identitám.

## 13. Aggregated ClusterRoles

ClusterRoles môžu byť automaticky agregované podľa labels do vyšších rolí.

Príklad ecosystem extension môže pridať CRD permissions do používateľskej role `view`, `edit` alebo `admin` prostredníctvom aggregation labels.

Riziko:

- nová CRD môže rozšíriť význam existujúcej role,
- malicious alebo nesprávne labelovaný ClusterRole môže zvýšiť oprávnenia širokej skupine,
- upgrade operatora môže zmeniť agregovaný ruleset.

Sleduj resolved rules, nie iba pôvodný manifest role.

## 14. Default ClusterRoles

Kubernetes vytvára defaultné ClusterRoles a bindings s prefixom `system:` a používateľskými rolami ako `view`, `edit`, `admin`, `cluster-admin`.

Niektoré defaultné objekty sú automaticky reconciled API serverom. Neupravuj ich bez pochopenia auto-reconciliation a upgrade dôsledkov; preferuj vlastné role a bindings.

## 15. Privilege escalation cez RBAC

Niektoré permissions sú nepriamo ekvivalentné širšiemu prístupu.

### Vytváranie workloadov

Kto môže vytvoriť Pod/Deployment v namespace, môže často:

- použiť ServiceAccount daného namespace,
- mountnúť Secrets dostupné workloadu,
- pristupovať k Services a internal networku,
- využiť povolené host mounts alebo privileged fields, ak admission neblokuje.

### Čítanie Secrets

Bearer tokens a credentials môžu umožniť impersonáciu workloadov alebo external access.

### `bind`

Umožňuje vytvoriť binding na role s permissions, ktoré caller sám nemusí mať podľa bežnej escalation protection.

### `escalate`

Umožňuje vytvoriť alebo upraviť role s právami nad vlastný aktuálny permission set.

### `impersonate`

Umožňuje vydávať requesty ako iný user, group, ServiceAccount alebo extra identity attribute.

### CSR approval

Kombinácia create/approve nad CertificateSigningRequest a citlivým signerom môže viesť k novému klientskemu certifikátu.

## 16. Node a proxy permissions

Citlivé sú najmä:

- `nodes/proxy`,
- kubelet API access,
- `pods/exec`,
- `pods/attach`,
- `pods/portforward`,
- access k metrics alebo debug endpoints.

Node proxy môže obísť niektoré bežné audit a admission cesty a sprístupniť workload data alebo exec capabilities podľa kubelet konfigurácie.

## 17. ServiceAccount token a RBAC

ServiceAccount token autentifikuje workload. RBAC určuje, čo smie robiť.

```bash
kubectl auth can-i get secrets \
  --as=system:serviceaccount:production:web \
  --namespace production
```

Vypnutie automatického token mountu znižuje credential exposure, ale neodoberá RBAC bindings identity. Pod môže dostať custom projected token alebo iný credential.

## 18. Diagnostika `401` a `403`

### `401 Unauthorized`

Authentication zlyhala:

- token chýba alebo expiroval,
- nesprávna audience,
- certifikát alebo issuer nie je dôveryhodný,
- request nemá platný credential.

### `403 Forbidden`

Identita bola rozpoznaná, ale authorization nepovolila verb/resource/namespace.

Audituj user a groups uvedené v chybe alebo audit logu.

## 19. `kubectl auth can-i`

```bash
kubectl auth can-i list pods -n production
kubectl auth can-i --list -n production
kubectl auth can-i create pods/exec -n production
kubectl auth can-i get secrets \
  --as=system:serviceaccount:production:web \
  -n production
```

Výsledok odráža aktuálnu authorization konfiguráciu a impersonation oprávnenie caller-a. Nie je náhradou za test celej admission a runtime cesty.

## 20. `SelfSubjectRulesReview` a access reviews

Kubernetes poskytuje review APIs na vyhodnotenie permissions:

- `SelfSubjectAccessReview`,
- `SubjectAccessReview`,
- `LocalSubjectAccessReview`,
- `SelfSubjectRulesReview`.

External controllers a UI ich používajú na authorization checks. Odpoveď môže byť neúplná pri niektorých authorizeroch alebo dynamickej policy, preto nepredpokladaj, že export rules je vždy absolútny dôkaz všetkých možností.

## 21. Multi-tenancy

RBAC samo osebe nevytvára bezpečný tenant boundary. Potrebuješ kombináciu:

- namespaces,
- Pod Security a admission policy,
- NetworkPolicy,
- ResourceQuota,
- secret a workload identity isolation,
- node/runtime isolation podľa threat modelu,
- audit a policy enforcement.

Tenant, ktorý môže vytvárať privileged Pod alebo používať cudziu ServiceAccount identity, môže RBAC namespace boundary obísť cez runtime vrstvu.

## 22. GitOps a RBAC

GitOps controller má často široký write prístup. Obmedz:

- sledované repositories a branches,
- cieľové namespaces/clustre,
- povolené resource kinds,
- impersonation model,
- secret access,
- cluster-scoped resource management,
- drift remediation permissions.

Repository write access môže byť nepriamo production cluster write access.

## 23. Audit a revízia

Pravidelne kontroluj:

```bash
kubectl get roles,rolebindings -A
kubectl get clusterroles,clusterrolebindings
kubectl describe rolebinding -n production <name>
kubectl auth can-i --list --as=<identity> -n production
```

Hľadaj:

- wildcard rules,
- bindings na `system:authenticated` alebo široké groups,
- cluster-wide bindings tam, kde stačí namespace scope,
- nepoužívané ServiceAccounts,
- permissions na Secrets, exec, proxy, CSR a RBAC management,
- orphan bindings po odstránení identity provider group.

## 24. Anti-patterny

### `cluster-admin` pre CI/CD

Compromise pipeline poskytne úplnú kontrolu nad clusterom.

### Jedna zdieľaná ServiceAccount pre všetky aplikácie

Nemožno izolovať, auditovať ani bezpečne rotovať permissions.

### Wildcard pre budúcu pohodlnosť

Upgrade alebo nový CRD automaticky rozšíri prístup.

### Role považovaná za deny policy

Iný binding môže permission znovu udeliť.

### `view` považované za automaticky bezpečné pre všetky CRDs

Aggregated role a CRD semantics môžu sprístupniť citlivé dáta.

### Povolenie create Pods bez Pod Security

Caller môže získať ďalšie credentials, host alebo network capability.

### Ručná editácia defaultných `system:` rolí

Auto-reconciliation alebo upgrade môže zmenu prepísať alebo vytvoriť nejasný drift.

## 25. Troubleshooting

### Binding existuje, ale access je forbidden

Over namespace bindingu, subject namespace/name, roleRef kind/name, API group, resource plural a subresource.

### `get pods` funguje, `kubectl logs` nie

Potrebuješ permission na `pods/log`.

### `kubectl exec` je forbidden

Over verb `create` na `pods/exec`, nie iba `get` na Pods.

### RoleBinding na ClusterRole dáva viac, než sa čakalo

Namespaced permissions sú obmedzené na namespace, ale over všetky rules a subresources ClusterRole-u.

### Permission zostalo po odstránení bindingu

Hľadaj ďalšie RoleBindings, ClusterRoleBindings a group memberships; RBAC je aditívne.

## 26. Kontrolné otázky

1. Aký je rozdiel medzi authentication a authorization?
2. Ako sa líši Role a ClusterRole?
3. Ako sa líši RoleBinding a ClusterRoleBinding?
4. Prečo môže RoleBinding odkazovať na ClusterRole?
5. Ako sa zapisuje RBAC permission na `pods/log` a `pods/exec`?
6. Prečo RBAC nemá explicitný deny?
7. Aké riziko majú wildcard pravidlá?
8. Ako môže create Pod permissions viesť k privilege escalation?
9. Aký je rozdiel medzi `401` a `403`?
10. Ako overíš permissions konkrétnej ServiceAccount identity?

## Glossary impact

Relevantné pojmy: Kubernetes RBAC, Role, ClusterRole, RoleBinding, ClusterRoleBinding, RBAC subject, API verb, subresource permission, non-resource URL, `resourceNames`, additive authorization, aggregated ClusterRole, `bind`, `escalate`, `impersonate`, SubjectAccessReview, least privilege, wildcard permission a RBAC privilege escalation.

## Oficiálna dokumentácia

- [Using RBAC Authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [RBAC Good Practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
- [Authorization Overview](https://kubernetes.io/docs/reference/access-authn-authz/authorization/)
