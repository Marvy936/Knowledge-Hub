# IAM a RBAC

Identity and Access Management je lifecycle disciplína pre identities, accounts, authenticators, federation, entitlements, privileged access, authorization, review, revocation a audit. Role-Based Access Control je iba jeden authorization model v tomto širšom systéme. Rola sama nevyrieši identity proofing, mover a leaver zmenu, session revocation, trusted attributes, delegated workload identities ani explainability effective accessu.

IAM sa preto správa ako reconciler medzi authoritative identity a ownership state-om a effective permissions naprieč identity providerom, applications, cloudom, Kubernetesom, databázami a CI/CD. Ak synchronizácia iba pridáva nové skupiny, ale neodstraňuje staré paths a session descendants, systém nie je reconciler; je to privilege accumulator.

## Identity-to-effective-access lifecycle

Každý entitlement musí mať pôvod, ownera, scope, dôvod a zánik. Joiner event vytvorí minimálny baseline. Mover event vypočíta nový complete desired set namiesto aditívneho pridania. Leaver event zruší accounts, sessions, tokens, workload descendants a recovery paths v poradí, ktoré neumožní ďalšie použitie starého oprávnenia.

```text
authoritative identity, employment a ownership state
→ joiner, mover, leaver alebo privileged-access event
→ desired account a entitlement generation
→ role/group/attribute graph reconciliation
→ federation a session/token projection
→ policy evaluation a effective access
→ audit a access review
→ revoke, remove a retire descendants
→ second-sync a second-login validation
```

IAM source of truth môže byť HR systém pre employment state, service catalog pre workload ownera a resource registry pre tenant alebo environment scope. Žiadny z nich však automaticky nepozná celý effective access graph. Reconciliation musí spojiť authoritative intent s platform-specific groups, roles, policies, bindings, sessions a caches.

## Exact IAM subject

Pre incident `SEC-PAY-47` je dôležité odlíšiť desired identity state od effective accessu:

```yaml
identity: urn:atlas:human:7421
employmentGeneration: HR-EMP-9081
currentDepartment: finance-analytics
previousDepartment: payments-operations
desiredEntitlements:
  - finance-analytics-read
forbiddenEntitlements:
  - prod-payment-operators
  - payments-prod-operator
observedPaths:
  - directGroup: payments-oncall
    state: removed
  - nestedPath: finance-emea/legacy-shared-operations/prod-payment-operators
    state: present
sessionDescendants:
  - SESSION-771
  - access-token-884
kubernetesBinding: payments-prod-operators
```

Tento subject vysvetľuje, prečo veta „direct group bola odstránená“ nepreukazuje revocation. Effective access stále vzniká nested membershipom, session claimom a Kubernetes bindingom.

## Joiner, mover a leaver ako state replacement

Joiner workflow začína eligibility a vytvára iba baseline potrebný pre prvú pracovnú funkciu. Mover workflow nevykonáva `add(new-role)`; vypočíta complete desired set a odstráni všetko, čo doň nepatrí. Leaver workflow musí zohľadniť propagation a descendants: account disable bez session revocation môže ponechať hodinový token, cloud role session alebo Kubernetes credential.

Desired-state payload môže vyzerať takto:

```json
{
  "subject": "urn:atlas:human:7421",
  "generation": "IAM-DESIRED-551",
  "employment_state": "active",
  "department": "finance-analytics",
  "entitlements": [
    {
      "name": "finance-analytics-read",
      "scope": "tenant:finance-eu",
      "expires_at": null
    }
  ],
  "forbidden": [
    "prod-payment-operators",
    "payments-prod-operator"
  ],
  "revoke_sessions_older_than_generation": "HR-EMP-9081"
}
```

Payload preukazuje intended generation a negative requirements. Nepreukazuje, že každý target systém vykonal remove, nested graph sa prepočítal, session bola zrušená alebo cache vypršala. Reconciler potrebuje per-target acknowledgement a effective-state read-back.

## Role engineering bez role explosion

Role má reprezentovať stabilný job alebo capability pattern, nie každú kombináciu usera, tenant-a a environment-u. Ak každá výnimka vytvorí novú rolu, vznikne role explosion a review sa stane nečitateľný. Ak jedna rola obsahuje všetky environment-y a actions, vznikne toxic super-role.

Praktický model kombinuje RBAC a trusted attributes. Rola určí typ capability, napríklad `settlement-requeue-requester`; ABAC conditions obmedzia environment, tenant, incident, assurance a expiration. Relationship alebo object-level authorization následne overí, že operation patrí povolenému tenant-u a workflow-u.

Role design začína task inventory, nie kopírovaním permissions existujúceho administrátora. Každá permission má consumera a use case; unused alebo nevysvetliteľná permission je defect. Role owner zodpovedá za semantics, resource owner za scope a IAM platform za propagation a review evidence.

## Kubernetes RBAC ako additive graph

Kubernetes používa Role a ClusterRole na definovanie pravidiel a RoleBinding alebo ClusterRoleBinding na priradenie subjects. Permissions sú additive; všeobecné deny pravidlá v RBAC neexistujú. Preto negative requirement musí presadiť užší allow graph, admission policy alebo oddelená architecture boundary.

Úzka namespaced capability môže vyzerať takto:

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
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: payments-jit-requeue
  namespace: payments-prod
subjects:
  - kind: Group
    name: atlas:jIT:payments-requeue
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: settlement-requeue-requester
  apiGroup: rbac.authorization.k8s.io
```

Manifest preukazuje intended binding. Nepreukazuje, že group claim je aktuálny, binding je loaded na intended clusteri, iný ClusterRoleBinding nepridáva širší access alebo custom controller bezpečne spracuje request.

Effective access sa kontroluje z viacerých uhlov:

```bash
kubectl auth can-i --list \
  --namespace payments-prod \
  --as=urn:atlas:human:7421

kubectl auth can-i create pods \
  --namespace payments-prod \
  --as=urn:atlas:human:7421

kubectl auth can-i create settlementrequeues.operations.atlas.example \
  --namespace payments-prod \
  --as-group=atlas:jIT:payments-requeue \
  --as=urn:atlas:human:legitimate-oncall
```

`--list` poskytuje snapshot recognized permissions pre subject v danom namespace. Nezachytáva všetky non-resource URLs, admission constraints, external authorization, cloud permissions, ServiceAccount selection ani alternatívne identities. Druhý a tretí príkaz testujú konkrétne requests a preto sú vhodnejšie ako všeobecný zoznam, ale stále nepreukazujú end-to-end business authorization.

## Effective access graph a indirect paths

Explainability vyžaduje graph:

```text
authoritative identity
→ direct a nested groups
→ federated claims
→ local groups a roles
→ bindings/policies
→ delegated identities a resources
→ reachable capabilities
```

Pri incidente bol path `finance-emea → legacy-shared-operations → prod-payment-operators → ClusterRoleBinding → create Pod → settlement-debug ServiceAccount → provider Secret`. Review iba direct group membershipu by hlásil false-safe stav. Rovnako review iba Kubernetes bindings by nevysvetlil, prečo IdP stále emitoval group claim.

Capability graph musí analyzovať `bind`, `escalate`, `impersonate`, workload creation, pass-role alebo ServiceAccount selection, CI execution, secret projection a custom resource controllers. Indirect path môže byť silnejší než všetky direct permissions principalu.

## Access reviews, exceptions a break-glass

Access review nie je potvrdenie zoznamu accountov. Reviewer potrebuje business task, current ownera, effective paths, posledné použitie, standing/JIT stav, session descendants a toxic combinations. Approval „stále potrebuje admin“ bez evidence iba predlžuje privilege creep.

Exception má exact subject, risk ownera, compensating controls, expiration a removal trigger. Permanentná výnimka bez revalidation je druhý authoritative policy source. Break-glass sa kontroluje oddelene: credential custody, activation, real-time alert, scoped session, post-use rotation a second test po návrate normal pathu.

## Incident `SEC-PAY-47`: add-only mover sync

HR source správne presunul principal 7421 do Finance Analytics. IAM workflow odstránil direct `payments-oncall`, ale neprepočítal nested group graph, neodstránil `prod-payment-operators` a nerevoke-nul session `SESSION-771`. Token preto ďalej niesol privileged claim a Kubernetes binding zostal effective.

Root cause bol add-only mover model. Broad Kubernetes role a delegated ServiceAccount path zväčšili blast radius, ale nevytvorili stale entitlement. Diskriminačný dôkaz porovnal HR generation, desired entitlement manifest, nested graph, token claim, loaded binding a audit side effects.

Containment suspenduje principal, revoke-ne sessions, odstráni affected nested path a dočasne zablokuje binding bez vymazania audit evidence. Recovery zmení reconciler na complete desired-state replacement, pridá per-target remove acknowledgement, session-generation invalidation a negative access fixtures. Broad role sa nahradí mediated JIT capability.

## Acceptance a second-sync closure

Recovery prejde iba vtedy, keď direct aj nested entitlement zmiznú, existing session zlyhá, fresh login neobsahuje privileged claim a Kubernetes direct aj indirect paths sú denied. Legitímny JIT group musí stále získať iba `settlementrequeues` capability. Potom sa vykoná druhá mover zmena alebo opakovaný sync bez ďalšej mutácie. Tento second-sync test odhalí add-only alebo oscillating reconciler, ktorý prvý pass iba náhodne opravil.

IAM success teda nie je počet synchronizovaných accounts. Je to zhoda authoritative desired state-u, effective access graphu, session state-u a business authorization po opakovanom reconciliation cykle.

## Kontrolné otázky

1. Prečo RBAC nie je celý IAM systém?
2. Čím sa mover state replacement líši od `add(new-role)`?
3. Prečo direct group removal nepreukazuje revocation?
4. Čo `kubectl auth can-i --list` nevidí?
5. Ako sa RBAC a ABAC dopĺňajú bez role explosion?
6. Ktoré indirect permissions musia byť súčasťou capability graphu?
7. Prečo je second-sync test dôležitý pre reconciler?

## Referencie

- [NIST SP 800-53 Identity and Access Management controls](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [Kubernetes RBAC authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Kubernetes authorization overview](https://kubernetes.io/docs/reference/access-authn-authz/authorization/)
- [SCIM protocol](https://www.rfc-editor.org/rfc/rfc7644)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Least privilege](least-privilege.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Active Directory →](active-directory.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
