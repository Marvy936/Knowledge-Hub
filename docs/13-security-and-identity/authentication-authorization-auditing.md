# Authentication, authorization a auditing

Authentication, authorization a auditing sú tri samostatné bezpečnostné funkcie v jednom access lifecycle-e. Authentication vytvorí dôveryhodný principal a session context. Authorization rozhodne o jednej konkrétnej action nad jedným resource-om v konkrétnom context-e. Auditing zachová vstup, policy generation, delegated identities, enforcement verdict a side effect tak, aby bolo možné vysvetliť allow, deny aj neúspešný alebo čiastočne vykonaný request.

Platná authentication nie je všeobecné povolenie. Platne podpísaný token nepreukazuje správny audience, tenant, object ownership ani aktuálny employment state. Rovnako audit event nie je úplný, ak zachová iba effective workload a stratí human actora, alebo naopak zaznamená iba usera a nezachytí ServiceAccount, ktorý vykonal downstream operation.

## Access-decision lifecycle

Použiteľný access model musí sledovať celý reťazec od identity authority až po business side effect. Ak sa analýza zastaví pri „login bol úspešný“ alebo „RBAC vrátil allow“, nevie vysvetliť, či request prišiel od správnej session, či sa policy presadila na správnom resource a či aplikácia nevykonala širšiu operáciu, než authorization verdict povoľoval.

```text
identity proofing a eligibility
→ authenticator enrollment a authentication event
→ principal, assurance a session/token generation
→ principal–action–resource–context request
→ policy information a policy generation
→ PDP decision
→ PEP enforcement
→ downstream operation a side effect
→ audit event s actorom a delegated identities
→ revocation, reconciliation a second-session validation
```

Identity, account, credential, authenticator, principal, session a token nie sú synonymá. Identity opisuje entitu. Account je jej reprezentácia v systéme. Credential alebo authenticator preukazuje kontrolu nad identity claimom. Principal je security subject použitý pri requeste. Session a token sú časovo obmedzené authorization snapshots, ktoré môžu prežiť zmenu authoritative identity state-u.

## Exact access subject

Incident `SEC-PAY-47` používa konkrétnu access chain:

```yaml
humanIdentity: urn:atlas:human:7421
employmentState: finance-analytics
authenticationEvent:
  method: WebAuthn
  sessionId: SESSION-771
  assurance: phishing-resistant
idpClaim:
  group: prod-payment-operators
kubernetesSubject: urn:atlas:human:7421
binding: payments-prod-operators
requestedAction: create
requestedResource: pods
requestedNamespace: payments-prod
delegatedWorkload: system:serviceaccount:payments-prod:settlement-debug
downstreamCapability: provider-a-mtls generation 34
auditGeneration: AUDIT-SEC-28
```

Tento subject oddeľuje authentication success od authorization correctness. WebAuthn môže korektne preukázať, že request ovláda session patriacu principalovi 7421, zatiaľ čo stale group claim a broad binding stále vytvoria nesprávny access verdict.

## Authentication: dôveryhodný principal, nie business oprávnenie

Authentication začína eligibility a identity proofingom, pokračuje enrollmentom authenticatora a končí session alebo tokenom s konkrétnou assurance úrovňou. Human a workload authentication majú odlišné lifecycle-y. Human principal typicky používa phishing-resistant authenticator a krátkodobú session; workload používa platform identity, mTLS alebo signed assertion viazanú na deployment a audience.

Pri token-based systéme sa musí odlíšiť syntaktické prečítanie claims od cryptographic a semantic validation. Nasledujúci príkaz iba dekóduje JWT payload:

```bash
TOKEN_PAYLOAD="$(printf '%s' "$ACCESS_TOKEN" | cut -d. -f2 | tr '_-' '/+' | base64 -d 2>/dev/null)"
printf '%s' "$TOKEN_PAYLOAD" | jq '{iss, sub, aud, exp, iat, groups}'
```

Výstup môže ukázať issuer, subject, audience a group claim, ale **nepreukazuje** signature, trusted issuer bootstrap, key validity, expiration, nonce, sender binding ani revocation. Production verifier musí validovať cryptography a semantics v jednej transakcii a následne vytvoriť lokálny principal z immutable identity key, napríklad `issuer + subject`, nie z emailu alebo display name-u.

Authentication failure sa diagnostikuje podľa boundary: enrollment a authenticator state, identity-provider policy, protocol transaction, token issuance, token validation a local session creation. Reset hesla neopraví wrong audience ani stale derived session.

## Authorization: jedna action nad jedným resource-om

Authorization request má minimálne štyri osi:

```text
principal + action + resource + context
```

Context zahŕňa tenant, environment, time, assurance, device alebo workload posture, network boundary, JIT grant a current resource state. Policy Administration Point spravuje policy, Policy Information Point dodáva trusted attributes, Policy Decision Point vypočíta verdict a Policy Enforcement Point ho musí presadiť na každej access ceste.

Kubernetes impersonation ukáže direct effective verdict:

```bash
kubectl auth can-i create pods \
  --namespace payments-prod \
  --as=urn:atlas:human:7421

kubectl auth can-i patch deployments/scale \
  --namespace payments-prod \
  --as=urn:atlas:human:7421
```

Tieto príkazy preukazujú authorization decision pre konkrétny API request a aktuálne loaded RBAC state. Nepreukazujú, že IdP smie daný principal mapovať na tento subject, že admission policy obmedzí `serviceAccountName`, že custom controller nemá inú cestu alebo že request už nevykonal downstream side effect.

Najnebezpečnejšie permissions sú často nepriame. `create pods` môže sprostredkovať použitie ServiceAccountu, Secretu, node identity alebo network trustu. `bind`, `escalate`, `impersonate`, workload creation a policy mutation preto vyžadujú capability analysis, nie iba zoznam API verbs.

Authorization policy pre incident môže vyžadovať current JIT grant a zakázať debug ServiceAccount:

```rego
package atlas.authz.payments

default allow := false

allow if {
  input.principal == "urn:atlas:human:7421"
  input.action == "settlement.requeue.one"
  input.resource.namespace == "payments-prod"
  input.context.jit_grant.active == true
  input.context.jit_grant.expires_at > input.context.now
  input.context.assurance == "phishing-resistant"
}

deny contains reason if {
  input.resource.service_account == "settlement-debug"
  reason := "production debug service account is forbidden"
}
```

Source policy preukazuje intended rule. Loaded-policy ID, PIP freshness, PEP coverage, decision log a negative runtime test sú samostatné dôkazy. Policy, ktorú API gateway používa, ale custom controller obchádza, neposkytuje complete authorization.

## Auditing: vysvetliteľný decision a side effect

Audit record musí umožniť rekonštruovať, kto čo požadoval, na základe ktorej identity a policy generation, ktorý PEP rozhodol, aký resource bol zasiahnutý a čo sa reálne stalo. Pri delegation zachová pôvodného actora aj effective workload.

```json
{
  "event_id": "AUD-88421",
  "timestamp": "2026-07-29T12:14:09Z",
  "actor": "urn:atlas:human:7421",
  "session_id": "SESSION-771",
  "authentication_assurance": "phishing-resistant",
  "delegated_principal": "system:serviceaccount:payments-prod:settlement-debug",
  "action": "create",
  "resource": "pods/settlement-debug-7f91",
  "namespace": "payments-prod",
  "policy_revision": "RBAC-PAY-44",
  "decision": "allow",
  "result": "created",
  "correlation_id": "SEC-PAY-47"
}
```

Tento event je užitočný iba vtedy, ak event pipeline zachová ordering, actor fields, immutable identifiers a retention počas incidentu. „User X accessed Secret“ bez session, delegation, resource UID a policy revision neodlíši direct read od Pod-mediated use. Audit availability je tiež security objective; pri výpadku identity alebo cluster control plane-u musí zostať queryovateľný independent evidence path.

Praktická kontrola incidentného exportu môže vyhľadať všetky descendant actions:

```bash
jq -c 'select(
  .correlation_id == "SEC-PAY-47" or
  .actor == "urn:atlas:human:7421" or
  .delegated_principal == "system:serviceaccount:payments-prod:settlement-debug"
) | {timestamp, actor, delegated_principal, action, resource, decision, result, policy_revision}' \
  /evidence/audit-2026-07-29.jsonl
```

Výstup preukazuje udalosti prítomné v konkrétnom exporte. Nepreukazuje completeness pipeline-u, správnosť clocku, neprítomnosť zmazaných events ani koreláciu s provider a ledger stavom; na to sú potrebné source counters, delivery acknowledgement a business reconciliation.

## Failure `SEC-PAY-47`: authentication správna, authorization zastaraná

Principal 7421 bol presunutý do Finance Analytics. HR authority zmenu zapísala, ale mover workflow odstránil iba direct group. Nested path cez `legacy-shared-operations` ponechal claim `prod-payment-operators` a session `SESSION-771` nebola revoke-nutá. WebAuthn authentication bola správna: request skutočne ovládal platnú session. Nesprávny bol authorization context, pretože derived group a session nereprezentovali aktuálnu pracovnú funkciu.

Binding dovolil create Pod, vybrať `settlement-debug` ServiceAccount, patchovať config a scale. Human actor vytvoril workload; workload potom použil provider Secret. Audit musel zachovať oba principals, inak by incident vyzeral buď ako čisto human config change, alebo ako izolovaný workload compromise.

Competing hypotheses zahŕňali stolen credential, IdP claim mapping bug, Kubernetes RBAC drift, custom-controller bypass a legitímny break-glass grant. Diskriminačný dôkaz spojil fresh HR state, stale nested membership, existing session, loaded binding a exact audit descendants. Root cause bola incomplete entitlement reconciliation; broad role a dlhá session boli amplifiers.

## Containment, recovery a acceptance

Containment revoke-ne session a refresh descendants, suspenduje principal, zablokuje binding a izoluje vytvorený Pod bez zmazania audit evidence. Nevykoná broad identity-provider restart ani globálny deny, ktorý by odstrihol legitímny incident response.

Authoritative recovery opraví joiner-mover-leaver reconciliation tak, aby desired entitlement set nahrádzal starý graph, odstráni direct aj nested access, revoke-ne derived sessions a workload credentials, zúži operator capability na mediated JIT action a rotuje kompromitovanú provider generation. Business recovery obnoví route a workers a reconciliuje unknown settlement outcomes.

Acceptance má štyri samostatné testy. Existing session musí zlyhať. Fresh login principalu 7421 nesmie získať privileged claim. Alternate nested path musí byť odstránená. Legitímny JIT operator musí vykonať iba scoped recovery action a audit musí zachovať allow aj forbidden deny s current policy revision. Až táto kombinácia preukazuje authentication, authorization, auditing aj revocation closure.

## Kontrolné otázky

1. Prečo platná WebAuthn authentication nevylučuje authorization incident?
2. Čo presne preukazuje `kubectl auth can-i` a ktoré enforcement boundaries nepokrýva?
3. Prečo je `create pods` potenciálne secret-use capability?
4. Aký rozdiel je medzi actorom a delegated principalom v audite?
5. Prečo JWT payload decode nie je token validation?
6. Ako PIP freshness ovplyvní správny PDP aj PEP?
7. Ktoré štyri testy uzatvárajú revocation po mover incidente?

## Referencie

- [NIST Digital Identity Guidelines](https://pages.nist.gov/800-63-4/)
- [Kubernetes authentication](https://kubernetes.io/docs/reference/access-authn-authz/authentication/)
- [Kubernetes authorization](https://kubernetes.io/docs/reference/access-authn-authz/authorization/)
- [Kubernetes auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)
- [Open Policy Agent](https://www.openpolicyagent.org/docs/latest/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CIA triáda](cia-triad.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Least privilege →](least-privilege.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
