# ServiceAccount

ServiceAccount je namespaced Kubernetes API objekt poskytujúci non-human identity pre Pods, system components a ďalšie workloads. ServiceAccount sám osebe neudeľuje oprávnenia. Authentication identita vzniká použitím jeho tokenu alebo federovanej identity a authorization rozhodnutie vykonáva RBAC alebo iný nakonfigurovaný authorizer.

## 1. Human a workload identity

Kubernetes rozlišuje najmä:

- human users alebo external identities,
- ServiceAccounts pre workloady a automation,
- Node identities,
- bootstrap a control-plane identities.

ServiceAccount identity má typický tvar:

```text
system:serviceaccount:<namespace>:<name>
```

Patrí aj do skupín ako:

```text
system:serviceaccounts
system:serviceaccounts:<namespace>
```

Tieto identity môžu byť použité v RBAC subjects, audit logs a policy decisions.

## 2. Namespaced object

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: payments-api
  namespace: production
```

ServiceAccount existuje iba vo svojom namespace. Rovnaké meno v inom namespace predstavuje inú identity.

Každý namespace štandardne dostane ServiceAccount s názvom `default`. To neznamená, že má mať application oprávnenia.

## 3. Priradenie k Podu

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: payments-api
  namespace: production
spec:
  serviceAccountName: payments-api
  containers:
    - name: app
      image: example/payments-api:1
```

Ak `serviceAccountName` neuvedieš, Pod používa `default` ServiceAccount daného namespace.

ServiceAccount identity je súčasťou Pod runtime contractu. Pri zmene ServiceAccountu sa bežne vytvára nový Pod; identita už bežiaceho procesu sa nemá meniť ad hoc.

## 4. Token projection

Moderný Kubernetes používa krátkodobejšie bound ServiceAccount tokens vytvorené cez TokenRequest API a projected do Podu.

Typická projection obsahuje:

```text
/var/run/secrets/kubernetes.io/serviceaccount/token
/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
/var/run/secrets/kubernetes.io/serviceaccount/namespace
```

Token môže mať:

- audience,
- expiration,
- väzbu na Pod alebo iný object,
- automatickú rotation zo strany kubeletu.

Application musí token z file-u znovu načítať a nesmie predpokladať, že hodnota zostane rovnaká počas celého process lifecycle-u.

## 5. `automountServiceAccountToken`

Token možno vypnúť na ServiceAccount alebo Pod úrovni:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: worker
automountServiceAccountToken: false
```

Alebo:

```yaml
spec:
  serviceAccountName: worker
  automountServiceAccountToken: false
```

Pod-level nastavenie má prednosť. Vypnutie token mountu je vhodné pre workload, ktorý nepotrebuje komunikovať s Kubernetes API ani používať identity integration závislú od projected tokenu.

ServiceAccount však stále zostáva Pod identity v API modeli; iba sa automaticky nemountne štandardný credential.

## 6. TokenRequest

Krátkodobý token možno vyžiadať explicitne:

```bash
kubectl create token payments-api \
  --namespace production \
  --audience https://kubernetes.default.svc
```

TokenRequest umožňuje definovať audience a duration v podporovanom limite. Je vhodnejší než manuálne vytváranie long-lived `kubernetes.io/service-account-token` Secretov.

Token neukladaj do Git-u, ticketu ani shell history. Po použití ho považuj za credential s rovnakým rizikom ako bearer token.

## 7. Audience

Audience určuje, pre ktorého recipienta je token vydaný.

Príklad:

```yaml
volumes:
  - name: identity-token
    projected:
      sources:
        - serviceAccountToken:
            path: token
            audience: vault.example.com
            expirationSeconds: 3600
```

Token pre external identity provider nemá byť automaticky akceptovaný Kubernetes API serverom a naopak. Audience validation znižuje replay credentialu medzi službami.

Chybná audience typicky vedie k authentication failure aj pri inak platnom podpise a neexpirovanom tokene.

## 8. ServiceAccount a RBAC

ServiceAccount nemá oprávnenia len preto, že existuje. Oprávnenia sa viažu cez RoleBinding alebo ClusterRoleBinding.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: config-reader
  namespace: production
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["payments-config"]
    verbs: ["get"]
---
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
  name: config-reader
```

Least privilege zahŕňa:

- správny namespace,
- minimálne verbs,
- minimálne resources/subresources,
- `resourceNames`, kde je to praktické,
- oddelenie read a write identity,
- zákaz zdieľania jedného ServiceAccountu nesúvisiacimi workloadmi.

## 9. Overenie oprávnení

```bash
kubectl auth can-i get configmap/payments-config \
  --namespace production \
  --as system:serviceaccount:production:payments-api
```

Ďalšie kontroly:

```bash
kubectl get rolebinding,clusterrolebinding -A
kubectl describe serviceaccount payments-api -n production
kubectl get pod <pod> -o jsonpath='{.spec.serviceAccountName}'
```

`kubectl auth can-i` overuje authorization pre danú verb/resource kombináciu. Neoveruje, či Pod skutočne má funkčný token, správnu audience alebo network connectivity k API serveru.

## 10. API access z Podu

Application potrebuje:

1. API server endpoint,
2. CA trust,
3. bearer token alebo inú autentifikáciu,
4. správnu audience,
5. network connectivity,
6. authorization.

Typický in-cluster endpoint:

```text
https://kubernetes.default.svc
```

Official client libraries používajú in-cluster configuration a dokážu pracovať s rotated token file-om. Vlastný HTTP klient musí korektne riešiť TLS, reload tokenu, timeouts, retries a API watch semantics.

## 11. Legacy long-lived token Secrets

Starší model vytváral long-lived token Secret viazaný na ServiceAccount. Moderný odporúčaný model používa TokenRequest a projected bound tokens.

Long-lived tokens zvyšujú:

- replay window,
- rotation náklady,
- leakage blast radius,
- množstvo statických credentials v API a backupoch.

Manuálny long-lived token používaj iba pri opodstatnenom kompatibilitnom use case s explicitnou expiry/rotation/revocation policy.

## 12. Workload identity federation

ServiceAccount môže byť mapovaný na external cloud alebo secret-manager identity.

Typický flow:

```text
Pod ServiceAccount token
→ OIDC/federation validation
→ short-lived external credential
→ cloud API alebo secret provider
```

Výhody:

- bez statického cloud access key v Kubernetes Secret-e,
- krátka platnosť,
- audience a subject binding,
- audit podľa workload identity.

Riziká:

- nesprávne široký trust policy,
- viac ServiceAccounts mapovaných na rovnakú external rolu,
- token theft počas validity,
- chýbajúce namespace/subject podmienky,
- závislosť od issuer discovery a external identity service.

## 13. `imagePullSecrets`

ServiceAccount môže deklarovať defaultné registry Secrets:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: payments-api
imagePullSecrets:
  - name: private-registry
```

Pods používajúce ServiceAccount môžu tieto references zdediť podľa admission behavior. Registry credential slúži kubeletu/runtime pri pull-e, nie application API authentication.

Nemiešaj:

- ServiceAccount token,
- image pull credential,
- application database credential,
- cloud workload identity.

Každý má odlišný issuer, audience, consumer a rotation model.

## 14. One ServiceAccount per workload boundary

Samostatný ServiceAccount je vhodný pre workload s vlastným:

- RBAC contractom,
- external identity mappingom,
- audit ownershipom,
- image pull policy,
- lifecycle a incident blast radiusom.

Nevytváraj automaticky nový ServiceAccount pre každý Pod replica. Identita zvyčajne patrí workloadu, nie konkrétnej ephemeral inštancii.

## 15. Default ServiceAccount

Bez explicitného `serviceAccountName` workload používa `default`.

Bezpečný namespace baseline:

- default ServiceAccount nemá broad RBAC,
- automatický token mount je vypnutý, ak ho väčšina workloadov nepotrebuje,
- každý API-using workload má explicitnú identity,
- admission/policy kontroluje chýbajúci `serviceAccountName`,
- ServiceAccount names nesú owner/purpose metadata.

## 16. Token rotation a process behavior

Projected token sa môže vymeniť pred expiry. Application má:

- čítať token z file-u pri requeste alebo ho bezpečne refreshovať,
- nereplikovať ho do environment variable,
- nepísať ho do logs,
- reagovať na `401` opätovným načítaním a nie nekonečným retry starého tokenu,
- používať bounded timeouty.

Copy tokenu do iného persistentného file-u obíde rotation a zvyšuje leakage window.

## 17. Audit

Audit event môže obsahovať username:

```text
system:serviceaccount:production:payments-api
```

Pre auditovateľnosť zachovaj:

- jednoznačný ServiceAccount owner,
- workload labels a namespace,
- oddelené identities pre deployment automation a runtime,
- zmenu RoleBindings v Git/evidence,
- external identity mapping revision,
- token issuer/audience configuration.

Zdieľaná identity medzi desiatkami aplikácií znemožňuje presné attribution.

## 18. Security hranice

Actor s právom vytvárať alebo meniť Pods môže často použiť ServiceAccount dostupný v namespace a získať jeho permissions.

Preto hodnotiť treba spoločne:

- RBAC nad ServiceAccounts,
- RBAC nad Pods/workload controllers,
- admission policy pre `serviceAccountName`,
- token automount,
- Secret access,
- `exec` a ephemeral-container permissions,
- node access,
- external federation trust.

ServiceAccount nie je tenant sandbox, ak actor môže vytvoriť ľubovoľný Pod s danou identity.

## 19. Troubleshooting

### Pod nemá token file

Over `automountServiceAccountToken` na Pode aj ServiceAccounte, projected volumes, admission mutation a kubelet events.

### API vracia `401 Unauthorized`

Over token expiry, signature/issuer, audience, CA/TLS, token reload a či request posiela správny bearer token.

### API vracia `403 Forbidden`

Authentication prešla, authorization zlyhala. Over username v audit/log response, RoleBinding subject namespace/name, verbs, API group, resource a subresource.

### `kubectl auth can-i` hovorí yes, application stále zlyháva

Over actual ServiceAccount Podu, token audience, endpoint, DNS/network, API resource path a request verb.

### External cloud federation nefunguje

Over issuer URL, JWKS/discovery, audience, subject claim, namespace/name condition, external role trust policy a clock skew.

### Image pull zlyhá

ServiceAccount API token nepomáha registry authentication. Over `imagePullSecrets`, registry host a Node connectivity.

## 20. Anti-patterny

### Všetky workloady používajú `default`

Oprávnenia a audit blast radius sa zlievajú.

### ClusterRoleBinding na širokú ServiceAccount skupinu

Môže udeliť cluster-wide práva každému ServiceAccountu v namespace alebo clustri.

### Long-lived token v CI variable bez expiry

Vzniká statický cluster credential mimo rotation modelu.

### Token skopírovaný z projected volume do image alebo persistentného volume

Obíde väzbu, expiry a rotation.

### ServiceAccount ako synonymum pre RBAC rolu

Identity a permissions sú oddelené objekty a lifecycle.

### Application token v environment variable

Zvyšuje leakage cez process inspection, dumps a support output.

## 21. Kontrolné otázky

1. Čo ServiceAccount poskytuje a čo neposkytuje?
2. Aký je canonical username ServiceAccount identity?
3. Ako sa bound projected token líši od legacy long-lived token Secretu?
4. Načo slúži audience?
5. Čo robí `automountServiceAccountToken`?
6. Ako sa ServiceAccount prepája s RBAC?
7. Aký je rozdiel medzi `401` a `403` pri API access-e?
8. Prečo je workload identity federation bezpečnejšia než statický cloud key?
9. Aký escalation path vzniká cez právo vytvárať Pods?
10. Prečo application musí vedieť znovu načítať rotated token?

## Glossary impact

Relevantné pojmy: ServiceAccount, workload identity, ServiceAccount username, default ServiceAccount, bound ServiceAccount token, TokenRequest, projected token, token audience, token rotation, `automountServiceAccountToken`, imagePullSecrets, workload identity federation a ServiceAccount impersonation boundary.

## Oficiálna dokumentácia

- [Service Accounts](https://kubernetes.io/docs/concepts/security/service-accounts/)
- [Configure Service Accounts for Pods](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/)
- [Managing Service Accounts](https://kubernetes.io/docs/reference/access-authn-authz/service-accounts-admin/)
- [Accessing the Kubernetes API from a Pod](https://kubernetes.io/docs/tasks/run-application/access-api-from-pod/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: ConfigMap a Secret](configmap-secret.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Service a EndpointSlice →](service-endpointslice.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
