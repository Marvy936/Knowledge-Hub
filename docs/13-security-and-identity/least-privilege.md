# Least privilege

Least privilege znamená, že human alebo workload principal dostane iba capabilities potrebné na presne definovanú úlohu, nad najmenším potrebným resource a data scope-om, v správnom environment-e, za požadovaných podmienok a iba na potrebný čas. Nie je to jednorazové zmenšenie role ani súťaž o najkratší policy dokument. Je to lifecycle od business tasku cez privilege engineering, aktiváciu a effective-state verification až po revocation, access review a incident recovery.

Praktický cieľ nie je „minimum permissions za každú cenu“. Príliš úzka rola, ktorá znemožní bezpečnú recovery, vedie k ad-hoc cluster-admin bypassu. Cieľom je najmenší preukázateľne funkčný capability envelope, ktorý podporuje povolený workflow a zároveň explicitne odmieta privilege escalation, alternate paths a nebezpečné fallbacky.

## Task-to-revocation lifecycle

Least privilege začína opisom práce, nie zoznamom existujúcich API verbs. Pre každú úlohu sa rozloží požadovaná action, resource, data, environment, time a approval context. Z toho vznikne capability contract, ktorý sa implementuje, aktivuje a testuje v runtime stave.

```text
business task a owner
→ required actions, resources, data a failure boundaries
→ capability envelope a forbidden outcomes
→ standing alebo JIT activation model
→ policy generation a approval
→ loaded effective access
→ positive, negative a escalation tests
→ audited use a session descendants
→ expiration, revocation a access review
→ second-use a recurrence validation
```

Standing privilege existuje nepretržite. Just-in-time privilege sa aktivuje iba pre konkrétny task a krátku lifetime. Just-enough administration poskytuje úzky sprostredkovaný príkaz namiesto všeobecného shellu alebo administrátorskej role. Tieto mechanizmy riešia odlišné osi: JIT redukuje čas exposure, JEA redukuje action a resource scope.

## Exact privilege subject

Incident `SEC-PAY-47` odhalil, že rola `payments-prod-operator` nebola navrhnutá podľa tasku. Umožňovala vytvárať ľubovoľné Pody, vybrať ľubovoľný ServiceAccount, patchovať konfiguráciu a scale-nuť workload. Legitímna potreba bola podstatne užšia: počas incidentu overiť jednu settlement operation, získať diagnostický stav a prípadne bezpečne requeue-nuť jeden reconciled item.

```yaml
subject: PRIV-PAY-47
principalClass: payments-oncall
businessTask: reconcile-and-requeue-one-settlement
resourceScope:
  namespace: payments-prod
  operation: op-884
actions:
  - settlement.read-status
  - settlement.reconcile-provider
  - settlement.requeue-one
conditions:
  assurance: phishing-resistant
  approval: two-party
  maxDuration: 30m
  incidentId: SEC-PAY-47
forbidden:
  - create-arbitrary-pod
  - choose-service-account
  - read-provider-secret
  - patch-routing-config
  - scale-workload-globally
```

Tento contract vysvetľuje, čo má principal dosiahnuť. Samotný YAML ešte nie je enforcement. Potrebujeme mapovanie na konkrétnu API capability, loaded-policy identity, expiration a audit read-back.

## Päť osí privilege scope-u

Action scope určuje, ktoré operácie sú povolené. Resource scope určuje konkrétny namespace, object, tenant alebo API route. Data scope odlišuje metadata od payloadu, jeden settlement od všetkých records a read od exportu. Environment scope oddeľuje production, staging a recovery boundary. Time a context scope viažu privilege na incident, assurance, device/workload posture, approval a expiration.

Permission `patch deployments` je preto nedostatočne presný popis. Môže znamenať zmenu image, environment variables, ServiceAccountu, replicas alebo security contextu. Ak business task potrebuje iba bounded restart, sprostredkovaná API operácia `rollout.restart` je bezpečnejšia než raw patch capability.

## Kubernetes: role, ktorá vyzerá úzko, ale nie je

Nasledujúca rola je zdanlivo namespaced, no capability je stále veľmi široká:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: payments-debug-unsafe
  namespace: payments-prod
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["create", "get", "list", "delete"]
  - apiGroups: ["apps"]
    resources: ["deployments", "deployments/scale"]
    verbs: ["get", "patch", "update"]
```

Namespaced scope nebráni principalovi vytvoriť Pod s privileged ServiceAccountom, mountnúť dostupné Secrets alebo meniť image a security context. Kubernetes RBAC navyše nemá všeobecné deny pravidlá; ak iný binding pridá permission, výsledok je additive allow graph.

Bezpečnejší model presunie citlivú action do mediated controllera. Human principal dostane iba create na úzky custom resource a controller vykoná server-side validation, provider reconciliation a idempotentný requeue:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: settlement-requeue-requester
  namespace: payments-prod
rules:
  - apiGroups: ["operations.atlas.example"]
    resources: ["settlementrequeues"]
    verbs: ["create", "get"]
```

Táto rola znižuje raw Kubernetes capability. Nepreukazuje však, že CRD admission kontroluje operation scope, controller autorizuje original requester, ServiceAccount controllera je úzky alebo downstream provider operation je idempotentná. Least privilege sa musí analyzovať cez celý delegated chain.

Effective access sa overuje pozitívne aj negatívne:

```bash
kubectl auth can-i create settlementrequeues.operations.atlas.example \
  --namespace payments-prod \
  --as=urn:atlas:human:legitimate-oncall

kubectl auth can-i create pods \
  --namespace payments-prod \
  --as=urn:atlas:human:legitimate-oncall

kubectl auth can-i bind clusterroles.rbac.authorization.k8s.io \
  --as=urn:atlas:human:legitimate-oncall
```

Očakávaný výsledok je `yes`, `no`, `no`. Príkazy preukazujú loaded RBAC verdict pre presné requests. Nepreukazujú custom admission, controller behavior, identity-provider eligibility ani permission získanú cez inú group, impersonation alebo external cloud role.

## Indirect privilege a capability graph

Access review, ktorý kontroluje iba direct role assignments, je neúplný. Effective capability môže vzniknúť cez nested group, composite role, ServiceAccount selection, pod creation, secret projection, workload identity, `bind`, `escalate`, `impersonate`, CI runner, cloud instance profile alebo custom controller.

Pre `SEC-PAY-47` bol kritický graph:

```text
human session
→ stale nested IdP group
→ ClusterRoleBinding
→ create Pod
→ choose settlement-debug ServiceAccount
→ mount provider credential
→ use provider capability
```

Human principal nemal direct `get secret`, ale dosiahol rovnaký výsledok. Least privilege preto hodnotí reachable capability, nie iba syntaktické permissions. Graph musí zahŕňať delegated principals a resources, ktoré principal dokáže vytvoriť alebo ovládať.

## Separation of duties a approval

Separation of duties znižuje riziko, že jedna identita pripraví, schváli a vykoná nebezpečnú zmenu. Pri provider credential rotation môže jeden owner pripraviť novú generation, druhý schváliť cutover a runtime controller vykonať bounded transition. Dvaja approvers nad rovnakou kompromitovanou shared session však neposkytujú nezávislosť.

Two-party approval musí byť viazané na immutable request subject: incident ID, exact operation, resource, requested capability, lifetime a policy revision. Approval „payments admin na 30 minút“ je príliš široký; approval „reconcile a requeue op-884 v SEC-PAY-47 do 13:00 UTC“ je kontrolovateľný contract.

## Break-glass bez permanentného bypassu

Break-glass účet alebo role je recovery mechanism, nie pohodlná alternatíva k JIT. Potrebuje oddelený authenticator, secure custody, explicitný trigger, krátku session, two-party activation podľa rizika, real-time alert, post-use credential rotation a test, že normal path sa obnovil.

Fail-open policy pri výpadku identity provideru môže zlepšiť availability, ale vytvorí confidentiality a integrity exposure. Bezpečnejší návrh používa lokálne overiteľnú, úzko scoped a časovo obmedzenú emergency capability; neudeľuje všeobecný cluster-admin len preto, že central PDP nie je dostupný.

## Incident: privilege creep po mover zmene

Principal 7421 prešiel z Payments Operations do Finance Analytics. Desired business task už nevyžadoval production settlement capability, no nested group zachovala broad operator role a existujúca session prežila. Rola umožnila vytvoriť debug Pod, vybrať ServiceAccount, použiť provider secret, patchnúť routing config a scale-nuť workers na nulu.

Root cause nebola iba „príliš široká rola“. Systém mal tri spojené chyby: mover workflow nerobil complete desired-state reconciliation, role bola navrhnutá podľa technického pohodlia namiesto tasku a revocation neodstraňovala session descendants. Broad privilege preto prežila organizačnú zmenu a z jednej stale identity path vytvorila C, I aj A incident.

Containment odstráni affected binding a session, izoluje workload a zachová audit. Recovery nahradí broad role mediated JIT capability, pridá expiry a approval subject, odstráni indirect ServiceAccount path a zavádza graph-based access review.

## Acceptance matrix

Positive test preukáže, že legitímny on-call s active JIT grantom vytvorí jeden `SettlementRequeue` request a controller po provider reconciliation vykoná presne jednu bezpečnú action. Negative test preukáže, že rovnaký principal nevytvorí Pod, nevyberie ServiceAccount, nečíta Secret, nemení route a nescaluje Deployment. Expiration test preukáže, že capability po 30 minútach zanikne bez manuálneho cleanupu. Mover test preukáže, že zmena role odstráni direct aj nested entitlement a revoke-ne existujúcu session. Escalation test skúsi `bind`, `escalate`, `impersonate`, custom controller a workload-mediated paths.

Úspech sa nehodnotí počtom zmazaných permissions. Hodnotí sa tým, že povolený task zostal funkčný, forbidden capabilities zlyhali a druhé použitie po expiration alebo mover zmene nevytvorilo stale access.

## Kontrolné otázky

1. Prečo namespaced `create pods` nie je automaticky least privilege?
2. Aký rozdiel je medzi JIT a just-enough administration?
3. Prečo direct-role access review neodhalí všetky effective capabilities?
4. Čo musí obsahovať immutable approval subject?
5. Ktoré tri `kubectl auth can-i` testy odlišujú task capability od escalation?
6. Prečo break-glass potrebuje second-use a post-recovery validation?
7. Ako mover workflow súvisí s privilege revocation?

## Referencie

- [NIST SP 800-53 Access Control](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Kubernetes authorization](https://kubernetes.io/docs/reference/access-authn-authz/authorization/)
- [Microsoft just-in-time privileged access](https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Authentication, authorization a auditing](authentication-authorization-auditing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: IAM a RBAC →](iam-rbac.md)
<!-- KNOWLEDGE-NAVIGATION:END -->