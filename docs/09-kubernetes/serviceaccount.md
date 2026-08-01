# ServiceAccount

ServiceAccount je Kubernetes workload identity. Pod ho používa pri autentizácii voči API serveru a podľa platformy môže byť previazaný aj na external cloud alebo secret-management identity. ServiceAccount však sám neprideľuje oprávnenia. Authorization vzniká cez RBAC alebo inú integračnú policy a skutočný token má audience, expiry a väzbu na konkrétny runtime.

`payments-api` nepotrebuje čítať všetky Kubernetes objekty. Potrebuje iba vlastný ConfigMap metadata endpoint alebo v ideálnom prípade vôbec nepotrebuje API prístup. Jeho ServiceAccount preto nesmie zdediť broad namespace rolu len preto, že sa deployment nachádza v production namespace.

## ServiceAccount v Pod template

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: payments-api
  namespace: production
automountServiceAccountToken: false
```

Pod:

```yaml
spec:
  serviceAccountName: payments-api
  automountServiceAccountToken: false
```

Ak aplikácia Kubernetes API nepotrebuje, token projection možno vypnúť. Tým sa znižuje credential exposure pri kompromitovanom process-e.

Ak sidecar alebo aplikácia API prístup potrebuje, token možno povoliť explicitne a RBAC zúžiť na konkrétne verbs a resources.

## Bound token projection

Moderný Pod token je krátkodobý, audience-bound a viazaný na runtime identity podľa TokenRequest mechanizmu. Kubelet token projectuje do Podu a priebežne ho obnovuje.

Explicitná projection:

```yaml
volumes:
  - name: api-token
    projected:
      sources:
        - serviceAccountToken:
            path: token
            audience: https://kubernetes.default.svc
            expirationSeconds: 3600
```

```yaml
volumeMounts:
  - name: api-token
    mountPath: /var/run/secrets/tokens
    readOnly: true
```

Aplikácia nemá token načítať iba raz na začiatku a držať ho navždy v pamäti. Klient musí zvládnuť rotation súboru a expiry.

Audience obmedzuje, pre ktorú relying party je token určený. Token pre Kubernetes API sa nemá používať ako generic bearer credential vo vlastnom internom API.

## API autentizácia nie je autorizácia

Token potvrdí ServiceAccount identity, napríklad:

```text
system:serviceaccount:production:payments-api
```

RBAC potom rozhodne, čo identita smie.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: payments-api-config-reader
  namespace: production
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["payments-api-runtime-metadata"]
    verbs: ["get"]
```

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: payments-api-config-reader
  namespace: production
subjects:
  - kind: ServiceAccount
    name: payments-api
    namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: payments-api-config-reader
```

Overenie:

```bash
kubectl auth can-i get configmap/payments-api-runtime-metadata \
  -n production \
  --as=system:serviceaccount:production:payments-api

kubectl auth can-i list secrets \
  -n production \
  --as=system:serviceaccount:production:payments-api
```

Prvý outcome má byť `yes`, druhý `no`.

## Namespace a ServiceAccount identity

ServiceAccount meno je namespaced. `production/payments-api` a `staging/payments-api` sú rozdielne identities. RoleBinding subject musí obsahovať správny namespace.

ClusterRole možno bindnúť cez RoleBinding do jedného namespace-u. ClusterRoleBinding poskytuje oprávnenie v celom cluster scope podľa rules a je výrazne širšie.

Broad `cluster-admin` pre aplikačný ServiceAccount je prakticky cluster compromise path pri application RCE.

## Default ServiceAccount

Každý namespace má `default` ServiceAccount. Pod bez explicitného `serviceAccountName` ho použije. To je ľahko prehliadnuteľná implicitná identita.

Production policies môžu vyžadovať explicitný ServiceAccount a zakázať automount na default identity. Tým sa workload identity stane súčasťou reviewovaného template contractu.

```bash
kubectl get pod -n production <pod-name> \
  -o jsonpath='{.spec.serviceAccountName}{"\n"}'
```

## Token nie je tajomstvo s neobmedzenou životnosťou

Staršie modely používali dlhodobé token Secrets. Bound tokens sú vhodnejšie, pretože expirujú a sú viazané na audience a object lifetime. Stále však ide o bearer credential: kto ho získa v platnom okne a spĺňa audience, môže vystupovať ako daný ServiceAccount.

Token sa nemá kopírovať do CI variables, chatov alebo statických config files. Pre manuálny krátkodobý token možno použiť:

```bash
kubectl create token payments-api -n production --duration=10m
```

Skutočná povolená dĺžka a audience závisia od API servera a policy.

## Workload identity voči cloudu

Managed Kubernetes platformy často prepájajú ServiceAccount s cloud IAM identity cez OIDC federation alebo platform-specific mechanizmus.

```text
Pod bound token
→ OIDC issuer a claims
→ cloud trust policy
→ krátkodobé cloud credentials
→ konkrétna cloud operation
```

Kubernetes RBAC a cloud IAM sú dve samostatné authorization roviny. ServiceAccount môže mať nulové Kubernetes oprávnenia, ale široké cloud oprávnenia. Audit musí kontrolovať obe.

Trust policy má viazať minimálne issuer, audience, namespace a ServiceAccount subject. Broad wildcard pre celý cluster alebo namespace zväčšuje blast radius.

## Image pull identity je iná vec

ServiceAccount môže referencovať `imagePullSecrets`, ale runtime registry autentizácia nie je to isté ako aplikačný API token.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: payments-api
  namespace: production
imagePullSecrets:
  - name: registry-pull
```

Image pull vykonáva kubelet/runtime na Node-e. Secret musí byť v rovnakom namespace a správne dostupný. Po stiahnutí image-u aplikácia nemá automaticky prístup k registry credential, pokiaľ ho Pod samostatne nemountuje.

## ServiceAccount zmena vytvára nový Pod contract

Zmena `serviceAccountName` v Deployment template vytvorí novú revision. Existujúce Pods si identity nemenia in-place.

```text
Pod P1 používa ServiceAccount old-api
→ Deployment template sa zmení na payments-api
→ nový Pod P2 dostane nový token a identity
→ P1 zostáva na starej identite do termination
```

Počas rolling overlapu môžu bežať obe identity. External IAM rotation alebo revocation musí rešpektovať toto okno.

## Debug, exec a impersonation

Identita s právom `pods/exec` môže spustiť command v existujúcom Pode a použiť jeho mounted token alebo cloud credential. Právo vytvárať Pods môže vytvoriť workload s ľubovoľným povoleným ServiceAccountom, ak admission neobmedzuje túto väzbu.

Právo `impersonate` nad users, groups alebo serviceaccounts je veľmi silné. Audit least privilege preto nesmie kontrolovať iba priamy `get secrets`.

## Incident: aplikácia získala cluster-admin cez default ServiceAccount

Legacy namespace mal RoleBinding, ktoré bindovalo `default` ServiceAccount na broad ClusterRole kvôli starému deployment toolu. Nový `payments-api` Pod nemal explicitný `serviceAccountName`, takže zdedil default identity aj automaticky mountnutý token.

Application SSRF/RCE by umožnila meniť workloads v celom namespace a cez ďalšie permissions eskalovať vyššie. Oprava vytvorila explicitný ServiceAccount bez tokenu, odstránila legacy binding a zaviedla admission policy zakazujúcu default ServiceAccount pre production workloads.

## Incident: cloud identity bola širšia než RBAC

RBAC audit ukázal, že `payments-api` nevie čítať Secrets ani meniť objekty. Napriek tomu mohla aplikácia mazať production object-storage bucket, pretože cloud federation trust mapovala celý namespace na jednu admin rolu.

Kubernetes authorization bola správna, cloud authorization nie. Oprava zaviedla per-ServiceAccount cloud role, explicitný audience/subject trust a bucket-level permissions.

## Incident: token rotation rozbila custom klienta

Aplikácia načítala service-account token pri štarte a držala ho v pamäti. Po expiry začali API calls vracať `401`, hoci projected token file už obsahoval novú hodnotu.

Oprava použila klientskú knižnicu, ktorá token file znovu číta, a pridala metrics pre auth failures bez logovania tokenu. Readiness sa nezmenila na závislosť od API, pretože API prístup nebol kritický pre payment serving path.

## Model, ktorý si treba odniesť

ServiceAccount identifikuje workload v Kubernetes. Bound token je krátkodobý bearer credential s audience a runtime väzbou. RBAC, admission, exec/debug/create-Pod permissions a external cloud federation určujú skutočnú authority. Workload bez API potreby nemá token automaticky mountovať; workload s API potrebou má dostať explicitný, minimálny a overiteľný permission contract.

## Referencie

- [Service Accounts](https://kubernetes.io/docs/concepts/security/service-accounts/)
- [Configure Service Accounts for Pods](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/)
- [Using RBAC Authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Bound Service Account Token Volume](https://kubernetes.io/docs/reference/access-authn-authz/service-accounts-admin/)
