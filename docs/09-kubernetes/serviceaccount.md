# ServiceAccount

ServiceAccount je namespaced Kubernetes identity anchor pre workload. Nie je to rola ani statický password. Bezpečný model spája konkrétny workload, ServiceAccount objekt, vydaný credential, jeho audience a lifetime, authorization policy, external federation a auditovaný operation outcome.

Dominantný lifecycle:

```text
workload identity intent a consumer inventory
→ ServiceAccount UID a namespace
→ Pod template, admission a effective identity
→ bound projected token alebo federated credential request
→ token audience, object binding a expiry
→ process-loaded credential a reload behavior
→ authentication
→ RBAC alebo external trust-policy authorization
→ auditovaný API/cloud/secret-manager operation
→ rotation, revocation, Pod replacement a incident closure
```

Kapitola používa Atlas Payments. Release 4.2.0 beží pod ServiceAccountom `payments-api` v namespace `production`. Workload potrebuje:

- čítať jediný ConfigMap `payments-policy` z Kubernetes API;
- vymeniť samostatný projected token s audience `vault.prod.example` za krátkodobý database credential;
- nemať právo listovať Secrets, meniť Deployments ani používať cloud administrátorskú rolu.

## 1. Identity subject musí byť presný

ServiceAccount identity nie je iba meno `payments-api`. Pri diagnostike a acceptance fixuj:

```text
cluster identity
namespace
ServiceAccount name a UID
Pod UID a admitted serviceAccountName
token issuer, audience, expiry a object binding
process-loaded token generation alebo fingerprint
RoleBinding/ClusterRoleBinding generations
external federation trust-policy generation
operation resource, verb a external action
```

Canonical Kubernetes username má tvar:

```text
system:serviceaccount:<namespace>:<name>
```

Rovnaké meno v inom namespace je iná identity. Zmazanie a znovuvytvorenie ServiceAccountu s rovnakým menom vytvorí nový object UID a nový lifecycle subject.

## 2. ServiceAccount nie je authorization policy

ServiceAccount pomenúva workload identity. Oprávnenia vznikajú až cez authorizer, typicky RBAC.

```text
ServiceAccount
→ authentication credential
→ authenticated username a groups
→ authorization decision pre konkrétny request
```

Pre Atlas Payments môže byť Role úzka:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: payments-policy-reader
  namespace: production
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["payments-policy"]
    verbs: ["get"]
```

RoleBinding viaže túto policy na presnú ServiceAccount identity:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: payments-policy-reader
  namespace: production
subjects:
  - kind: ServiceAccount
    name: payments-api
    namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: payments-policy-reader
```

Dôsledok: `401 Unauthorized` a `403 Forbidden` patria do odlišných boundaries. `401` znamená, že authentication credential nebol prijatý. `403` znamená, že identity bola rozpoznaná, ale request nemá povolenie.

## 3. Pod template a admitted identity

Pod používa ServiceAccount cez:

```yaml
spec:
  serviceAccountName: payments-api
```

Ak field chýba, Pod používa `default` ServiceAccount namespace-u. To môže byť technicky funkčné, ale zlieva identity, audit ownership a blast radius.

Effective identity overuj na admitted Pode, nie iba v source manifeste:

```bash
kubectl get pod <pod> -n production \
  -o jsonpath='{.metadata.uid}{"\n"}{.spec.serviceAccountName}{"\n"}'
```

Admission môže Pod mutovať. Identity acceptance preto potrebuje source-to-admitted diff a Pod UID, nie iba Git commit.

## 4. Bound projected token lifecycle

Moderný Pod typicky dostane krátkodobý ServiceAccount token cez TokenRequest a projected volume.

```text
ServiceAccount + Pod subject
→ TokenRequest
→ signed token s issuerom, audience, expiry a bindingom
→ kubelet projection do Podu
→ process token načíta
→ verifier skontroluje claims a object lifecycle
```

Štandardná projection môže byť dostupná pod:

```text
/var/run/secrets/kubernetes.io/serviceaccount/
```

Credential je bearer token. Kto ho získa počas validity, môže ho použiť v rozsahu jeho audience a authorization policy.

## 5. Audience je recipient boundary

Jeden token nemá byť univerzálny credential pre Kubernetes API, Vault a cloud provider.

Atlas Payments používa oddelené token subjects:

```text
TK-API-52
  audience: Kubernetes API
  purpose: get payments-policy

TK-VLT-52
  audience: vault.prod.example
  purpose: exchange za database credential
```

Custom projection:

```yaml
volumes:
  - name: vault-identity
    projected:
      sources:
        - serviceAccountToken:
            path: token
            audience: vault.prod.example
            expirationSeconds: 3600
```

Platný podpis a neexpirovaný token nestačia. Recipient musí akceptovať issuer, audience, subject a ďalšie trust conditions.

## 6. Object binding a identity continuity

Bound token môže byť viazaný na Pod alebo iný Kubernetes object. To obmedzuje použiteľnosť credentialu po zániku jeho subjectu.

Rozlišuj:

```text
ServiceAccount logical identity
Pod UID
issued token instance
process-loaded token instance
external session alebo derived credential
```

Zánik Podu neznamená, že všetky už vydané external sessions okamžite zmizli. Vault alebo cloud credential má vlastnú expiry, revoke a audit lifecycle.

## 7. Process-loaded credential je samostatný state

Kubelet môže projected token rotovať pred expiry. Application však môže:

- načítať token iba pri štarte;
- skopírovať ho do environment variable;
- držať ho v klientskom objekte bez reloadu;
- po `401` retryovať stále ten istý token;
- pokračovať cez už vydanú external session.

Preto oddeľuj:

```text
projected token file generation
≠ process-loaded token generation
≠ current external credential generation
```

Bezpečný klient token z file-u znovu načíta alebo používa knižnicu s podporou rotation. Token sa nekopíruje do image-u, PersistentVolume ani debug outputu.

## 8. `automountServiceAccountToken`

Workload, ktorý nepotrebuje API ani token-based federation, nemá automaticky dostávať API credential.

```yaml
spec:
  serviceAccountName: batch-renderer
  automountServiceAccountToken: false
```

Pod-level nastavenie má prednosť pred ServiceAccount-level nastavením. Vypnutie automountu nemení Pod identity v API modeli; mení automatic credential delivery.

Dôležitá failure boundary: federation sidecar alebo CSI provider môže potrebovať vlastnú explicitnú token projection aj pri vypnutom štandardnom API token mount-e.

## 9. Workload identity federation

ServiceAccount token môže byť dôkazom identity pre external trust system.

```text
Pod-bound token
→ OIDC issuer/JWKS validation
→ namespace, ServiceAccount, audience a claim policy
→ krátkodobý external credential
→ Vault, cloud alebo iný provider operation
```

Provider trust policy musí obmedziť aspoň:

- issuer;
- audience;
- namespace;
- ServiceAccount name;
- prípadné cluster alebo environment claims;
- cieľovú external rolu a allowed actions.

Mapovanie všetkých ServiceAccountov z namespace-u na jednu administrátorskú rolu ruší workload isolation aj audit attribution.

## 10. Identity, registry a application credentials sú odlišné

Nemixuj:

```text
ServiceAccount API token
image pull credential
Vault/cloud federated credential
database credential
TLS private key
```

Každý má vlastný issuer, consumer, audience, lifetime a revocation mechanismus.

`imagePullSecrets` používa kubelet/runtime pri image pull-e. Neudeľuje application procesu Kubernetes API práva a nie je database credential.

## 11. Pod-create permission je identity delegation boundary

Actor nemusí mať priamy `get secrets` alebo impersonation verb, aby získal workload authority. Ak môže vytvoriť Pod s privilegovaným ServiceAccountom, môže spustiť process pod jeho identity a použiť projected credential.

Preto sa ServiceAccount access graph skladá z:

```text
RBAC nad ServiceAccountmi a bindings
+ create/update Pods, Jobs a controllers
+ admission nad serviceAccountName
+ exec/ephemeral-container práva
+ node a kubelet access
+ token request a impersonation práva
+ external federation trust
```

ServiceAccount nie je tenant sandbox, ak tenant môže ľubovoľne vybrať ServiceAccount v namespace-e.

## 12. Default ServiceAccount baseline

Bezpečný namespace baseline:

- `default` ServiceAccount nemá application-specific RBAC;
- token automount je vypnutý, ak ho väčšina workloadov nepotrebuje;
- každý API-using workload má explicitný ServiceAccount;
- admission odmieta forbidden identities a chýbajúce ownership metadata;
- runtime a deployment automation používajú odlišné identities;
- bindings majú ownera, review a expiry pri dočasnom prístupe.

## 13. Auditovaný operation outcome

Identity acceptance nekončí pri `kubectl auth can-i`.

Pre Atlas request sleduj:

```text
Pod UID P52
→ token fingerprint TK-API-52
→ authenticated username system:serviceaccount:production:payments-api
→ get /api/v1/namespaces/production/configmaps/payments-policy
→ RBAC allow
→ response resourceVersion C52
→ process načíta policy generation C52
```

Pre Vault:

```text
P52
→ TK-VLT-52 audience vault.prod.example
→ trust policy TP17
→ derived credential DB08
→ database session audit
```

Audit musí spájať identity s konkrétnym operation outcome-om, nie iba s existenciou tokenu.

## 14. Worked failure: shared default identity zväčšila blast radius

Namespace obsahoval desať workloadov pod `default` ServiceAccountom. Jedna legacy RoleBinding povoľovala čítať všetky ConfigMaps a Secrets.

```text
shared default identity
→ nejasný owner
→ jeden kompromitovaný Pod použije rovnaké permissions
→ audit ukáže iba spoločný username
→ nemožno rýchlo oddeliť legitímnych consumerov
```

Recovery nebola iba odstránenie bindingu. Bolo potrebné vytvoriť per-workload ServiceAccounts, rolloutovať Pody, overiť loaded identities, rotovať odhalené credentials a potvrdiť forbidden access tests.

## 15. Worked failure: audience mismatch

Payments Pod dostal token s audience `vault.prod.example`, ale použil ho proti Kubernetes API.

```text
podpis validný
expiry validná
audience pre iného recipienta
→ API authentication zlyhá
```

Pridanie RBAC oprávnenia by chybu nevyriešilo, pretože request sa nedostal do authorization boundary.

## 16. Worked failure: stale process token po rotation

Projected token file sa vymenil, ale application klient držal starý token v memory. Po jeho expiry začal API vracať `401`.

```text
kubelet projection TK2
process stále používa TK1
TK1 expiruje
→ 401
→ retry loop používa TK1
→ API load rastie
```

Fix bol token reload pri requeste alebo na `401`, bounded retry a telemetry nad loaded token epoch. Samotný Pod restart bol containment, nie trvalá náprava klienta.

## 17. Worked failure: federation trust bol príliš široký

External trust policy akceptovala všetky ServiceAccounts z `production` namespace-u pre rolu s write prístupom k payment secrets.

Unrelated Job mohol získať rovnakú external rolu. Kubernetes RBAC bolo úzke, ale external authorization boundary bola široká.

Recovery vyžadovala zúžiť trust na presný ServiceAccount subject, rotovať derived credentials, skontrolovať provider audit a overiť denied exchange z cudzieho workloadu.

## 18. Causal troubleshooting walkthrough: `can-i=yes`, ale workload po hodinách dostáva `401`

Symptóm:

```text
Pod P52 je Running a Ready
kubectl auth can-i pre payments-api vracia yes
prvé hodiny API calls fungovali
neskôr všetky calls vracajú 401
restart Podu dočasne pomôže
```

### 1. Zafixuj subject a pôvodný outcome

Zaznamenaj bez plaintext tokenu:

```text
cluster a API endpoint
ServiceAccount name/UID
Pod UID, creation time a admitted serviceAccountName
automount a projected-volume config
token issuer, audience, expiry a bezpečný fingerprint
file mtime/inode a process-loaded fingerprint
client library/version a reload behavior
API audit username/result
RoleBinding generations
pôvodný operation: get payments-policy generation C52
```

### 2. Konkurenčné hypotézy

1. process cacheuje expirovaný token;
2. token má nesprávnu audience;
3. issuer/JWKS alebo clock validation zlyháva;
4. Pod nemá správnu projection alebo kubelet ju nerotuje;
5. request ide na nesprávny API endpoint alebo CA;
6. authentication prejde a skutočný výsledok je `403`;
7. network/TLS chyba je application mapovaná na `401`;
8. admission priradila iný ServiceAccount;
9. external proxy používa vlastný stale credential.

### 3. Diskriminačné observation points

- porovnaj token-file fingerprint s process-loaded fingerprintom;
- dekóduj iba necitlivé claims bezpečným nástrojom bez logovania tokenu;
- porovnaj `aud`, `iss`, expiry a Pod/ServiceAccount binding;
- skontroluj API audit: je request vôbec autentifikovaný a pod akým username?
- porovnaj nový request s tokenom z aktuálneho file-u;
- skontroluj kubelet/projected-volume Events;
- rozlíš HTTP status, TLS a network error;
- over presný verb/resource/subresource cez audit a `can-i`.

### 4. Containment

- zastav nekonečné retries;
- nezapisuj token do ticketu, logu ani shell history;
- odober failing Pod z trafficu, ak identity failure ovplyvňuje request correctness;
- zachovaj metadata, audit a token fingerprints;
- nereaktivuj long-lived legacy token ako rýchlu opravu;
- pri možnom leakage zúž RBAC/trust a rotuj derived credentials.

### 5. Authoritative recovery

Pri stale process token-e:

1. oprav klienta tak, aby načítaval rotated token;
2. pridaj bounded retry po jednom refreshi;
3. vydaj novú Pod generation s immutable image digestom;
4. over loaded token epoch;
5. zruš alebo nechaj expirovať staré derived credentials podľa policy;
6. odstráň dočasné identity exceptions.

### 6. Over pôvodný a forbidden outcome

Potvrď:

- P53 používa správny ServiceAccount UID a token audience;
- API audit ukazuje správny username;
- `get payments-policy` vráti accepted generation C52 alebo novšiu;
- Vault exchange vráti credential z trust policy TP17;
- starý/nesprávny token je odmietnutý;
- cudzí ServiceAccount nedokáže rovnaký API ani Vault operation;
- application request cez Payments Service prejde bez identity retry stormu;
- ďalšia token rotation prebehne bez restartu.

### 7. Posuň control skôr

Pridaj:

- explicitný ServiceAccount v každom Pod template;
- admission allowlist pre identity selection;
- per-workload RBAC a federation trust tests;
- token audience/rotation integration test;
- loaded credential epoch metric bez secret value;
- `401`/`403` oddelené telemetry;
- Pod-create escalation review;
- short-lived break-glass identity s expiry a auditom.

## 19. Observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Intent | workload identity contract | consumers, operations, forbidden actions |
| Kubernetes identity | ServiceAccount UID | namespace, owner, automount default |
| Pod binding | Pod UID | admitted serviceAccountName, projected volumes |
| Credential | token instance | issuer, audience, expiry, object binding, fingerprint |
| Process | loaded token generation | reload behavior, client cache, request fingerprint |
| Authentication | request identity | audit username, issuer/audience verdict |
| Authorization | RBAC request subject | verb, group, resource, namespace, binding generation |
| Federation | trust-policy generation | subject conditions, derived role, expiry |
| External access | derived credential/session | provider audit, operation, revocation |
| Business | request/operation ID | correct policy/data access, forbidden outcome |

## 20. Referenčné príkazy

```bash
kubectl get serviceaccount payments-api -n production -o yaml
kubectl get pod <pod> -n production -o yaml
kubectl auth can-i get configmap/payments-policy \
  -n production \
  --as system:serviceaccount:production:payments-api
kubectl get role,rolebinding -n production -o yaml
kubectl get clusterrolebinding -o yaml
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Pri token diagnostike pracuj s metadata a bezpečnými fingerprintmi. Plaintext bearer token nevypisuj do dokumentácie, logs ani odpovede.

## 21. Referenčné pravidlá

- ServiceAccount je identity anchor, nie RBAC rola.
- Namespace a object UID patria do identity subjectu.
- Pod source manifest nemusí byť admitted identity.
- Token audience je recipient boundary.
- Projected token file a process-loaded token sú odlišné states.
- Token rotation neznamená rotation už vydaného external credentialu.
- `401` je authentication boundary; `403` authorization boundary.
- `automountServiceAccountToken: false` vypína automatic credential delivery, nie Pod identity.
- `imagePullSecrets` nie sú application API credentials.
- Pod-create a controller-create práva môžu delegovať ServiceAccount authority.
- External federation trust môže byť širšia než Kubernetes RBAC.
- Recovery musí overiť legitímny operation aj forbidden access.

## 22. Kontrolné otázky

1. Aký lifecycle spája workload identity intent s auditovaným operation outcome-om?
2. Prečo ServiceAccount sám neudeľuje permissions?
3. Ako sa líši ServiceAccount object, Pod UID a token instance?
4. Prečo audience patrí do token subjectu?
5. Ako sa líši projected token generation od process-loaded generation?
6. Čo mení `automountServiceAccountToken`?
7. Prečo `can-i=yes` nevysvetľuje `401`?
8. Ako môže Pod-create permission delegovať workload identity?
9. Čo musí external federation trust policy obmedziť?
10. Čo musí ServiceAccount acceptance verdict overiť?

## Glossary impact

Relevantné pojmy: workload identity lifecycle subject, ServiceAccount object identity, admitted workload identity, bound token subject, token audience boundary, object-bound credential, process-loaded token generation, ServiceAccount authorization subject, federation trust-policy generation, derived credential subject, Pod-create identity delegation boundary, identity operation outcome, workload identity observation matrix a ServiceAccount acceptance verdict.

## Oficiálna dokumentácia

- [Service Accounts](https://kubernetes.io/docs/concepts/security/service-accounts/)
- [Configure Service Accounts for Pods](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/)
- [Managing Service Accounts](https://kubernetes.io/docs/reference/access-authn-authz/service-accounts-admin/)
- [Using RBAC Authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: ConfigMap a Secret](configmap-secret.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Service a EndpointSlice →](service-endpointslice.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
