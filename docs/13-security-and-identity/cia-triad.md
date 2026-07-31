# CIA triáda

CIA triáda — **Confidentiality, Integrity a Availability** — nie je zoznam troch všeobecných vlastností systému. Je to spôsob, ako pre konkrétny business proces pomenovať neprijateľné straty, priradiť ich k presnej trust boundary a následne dokázať, že ochranný mechanizmus funguje aj v runtime stave. Rovnaký asset môže mať odlišnú prioritu pre každú os: verejný release artifact má nízku požiadavku na confidentiality, ale veľmi vysokú požiadavku na integrity; incidentný audit môže vyžadovať vysokú integrity aj availability, hoci jeho čítanie zostáva striktne obmedzené.

Preto sa CIA nehodnotí otázkou „máme encryption, backup a RBAC?“. Správna otázka znie: ktorý subject chránime, čo smie a nesmie nastať, ktorý principal alebo failure path môže cieľ porušiť, kde sa rozhodnutie presadzuje a aký read-back preukáže výsledok bez zamieňania configured, loaded a effective state-u.

## Security-objective lifecycle

Každá bezpečnostná požiadavka prechádza rovnakým kauzálnym reťazcom. Najprv vznikne business capability a presný asset; potom sa určia trust boundaries, threat a acceptable impact. Až následne sa vyberie control, nasadí sa jeho konkrétna generation a overí sa, či sa presadil na všetkých relevantných cestách.

```text
business capability a chránený asset
→ exact security subject a trust boundaries
→ confidentiality, integrity a availability objectives
→ threat, vulnerability, exposure a impact
→ required assurance a control owner
→ configured control generation
→ loaded a effective enforcement state
→ allowed a forbidden runtime test
→ audit evidence a business verdict
→ containment, authoritative recovery a residual risk
```

Tento model oddeľuje tri odlišné tvrdenia:

```text
control existuje v source/configuration
≠ control bol načítaný správnym enforcement pointom
≠ chránený business outcome je preukázateľne zachovaný
```

„Encryption enabled“, „role removed“, „backup successful“ alebo „identity provider healthy“ sú iba technické medzistavy. Security acceptance vznikne až vtedy, keď povolená operácia funguje, zakázaná operácia zlyhá, audit zachytí oba verdicty a recovery obnoví dôveryhodný business stav.

## Exact subject SEC-PAY-47

Spoločný incident prvého bloku používa Atlas Payments final-settlement workflow. Subject nie je iba názov služby; zahŕňa identity graph, workload capability, konfiguráciu, secret generation aj business stav.

```yaml
subject: SEC-PAY-47
businessCapability: enterprise-final-settlement
release: 7.24.0
environment: production
region: eu-central-1
cluster: atlas-prod-euc1
namespace: payments-prod
humanPrincipal: urn:atlas:human:7421
idpIssuer: https://id.atlas.example
claimedGroup: prod-payment-operators
kubernetesBinding: payments-prod-operators
workloadPrincipal: system:serviceaccount:payments-prod:settlement-debug
providerCredentialGeneration: 34
approvedRouteGeneration: SETTLEMENT-ROUTE-91
auditGeneration: AUDIT-SEC-28
```

Tento manifest je evidence anchor. Preukazuje, ktoré identity a generations incident analyzuje; nepreukazuje, že IdP claim je aktuálny, binding je effective, workload secret skutočne použil alebo business settlement zlyhal. Každá z týchto hraníc potrebuje samostatný read-back.

## Confidentiality ako control nad čítaním aj použitím capability

Confidentiality chráni informácie a capabilities pred neautorizovaným disclosure alebo použitím. Principal nemusí exportovať private key, aby porušil confidentiality. Ak dokáže vytvoriť Pod s privileged ServiceAccountom a nechať ho vykonať mTLS handshake, získal citlivú cryptographic capability aj bez zobrazenia key bytes.

Pre provider credential preto objective znie: iba schválený settlement workload smie získať alebo použiť generation 34; human principal ju nesmie čítať, mountnúť do arbitrary workloadu ani vyvolať neobmedzenú podpisovú operáciu. Encryption at rest chráni ciphertext v storage boundary, ale nebráni autorizovanému API serveru premietnuť secret do Podu, ktorý vytvoril príliš silný principal.

Praktický negative test sa vykonáva s presnou impersonovanou identitou:

```bash
kubectl auth can-i get secret/provider-a-mtls \
  --namespace payments-prod \
  --as=urn:atlas:human:7421

kubectl auth can-i create pods \
  --namespace payments-prod \
  --as=urn:atlas:human:7421
```

Prvý príkaz testuje direct Secret authorization. Druhý odhaľuje indirect path: aj keď direct `get secrets` vráti `no`, `create pods` môže dovoliť výber ServiceAccountu, volume projection a následné použitie secretu. Výstup preukazuje Kubernetes authorization verdict pre zadaný request; nepreukazuje IdP session validity, admission-policy coverage ani to, že custom controller neponúka alternatívnu cestu.

## Integrity ako autorizovaná a overiteľná state transition

Integrity znamená, že dáta, konfigurácia a operácie zostanú správne, úplné a zmenené iba oprávneným mechanizmom nad správnou generation. Samotný hash dokazuje zhodu s konkrétnym obsahom, nie jeho dôveryhodný pôvod. Silnejší chain spája digest, signer alebo actor identity, provenance, policy decision, runtime read-back a business reconciliation.

Pre routing config je authoritative source `SETTLEMENT-ROUTE-91`. Ak runtime ukazuje generation 92, integrity verdict nie je „ConfigMap existuje“, ale „loaded state sa odchýlil od signed source a neexistuje approved transition“. Policy môže explicitne odmietnuť workload, ktorý sa pokúsi používať iný ServiceAccount alebo neapproved route generation:

```rego
package atlas.security.settlement

default allow := false

allow if {
  input.request.kind.kind == "Pod"
  input.request.namespace == "payments-prod"
  input.request.object.spec.serviceAccountName == "settlement-worker"
  input.request.userInfo.username == "system:serviceaccount:gitops:payments-reconciler"
  input.request.object.metadata.labels["atlas.example/route-generation"] == "SETTLEMENT-ROUTE-91"
}

deny contains msg if {
  input.request.namespace == "payments-prod"
  input.request.object.spec.serviceAccountName == "settlement-debug"
  msg := "settlement-debug service account is forbidden in production"
}
```

Táto Rego policy preukazuje intended decision logic. Nepreukazuje, že jej bundle bol publikovaný, konkrétny admission controller načítal správnu revision alebo všetky create/update paths prechádzajú týmto enforcement pointom. Acceptance preto vyžaduje loaded-policy identity, denied fixture a audit event s rovnakým policy revision ID.

## Availability ako dostupnosť správnej capability

Availability nie je process uptime. Settlement API môže vracať HTTP `200`, no business capability je nedostupná, ak workers sú scale-nuté na nulu, provider credential generation je revoke-nutá bez pripraveného nástupcu, DNS smeruje na nesprávny endpoint alebo authorization path odmieta legitímneho operatora počas incidentu.

Objective pre Atlas Payments znie: validná enterprise settlement operácia sa musí dokončiť do 2.5 sekundy a platforma musí vedieť obnoviť poslednú dôveryhodnú routing generation do 15 minút. Availability control nesmie fail-open-nuť confidentiality alebo integrity. Break-glass prístup preto potrebuje presný scope, krátku lifetime, two-party approval, audit a automatickú revocation; „dočasný cluster-admin“ bez expiration je nový security incident.

CIA objectives sa zapisujú ako odlišné acceptance conditions:

| Asset alebo proces | Confidentiality | Integrity | Availability |
|---|---|---|---|
| Provider credential | nesmie byť exportovaný ani použitý mimo approved workloadu | iba schválená generation a rotation actor | capability dostupná healthy workers bez fail-open bypassu |
| Route config | need-to-know read | iba signed GitOps generation | last-known-good obnova do 15 minút |
| Final settlement | bez cross-tenant disclosure | reconciled exactly-once business outcome | 99.9 % valid operations do 2.5 s |
| Security audit | obmedzené query access | actor, delegated identity, policy revision a result zachované | critical events queryovateľné počas incidentu |

## Incident: jedna stale access cesta narušila všetky tri osi

Dňa 29. júla 2026 o 12:14 UTC začal settlement-completion SLO prudko páliť. Runtime ukázal 12 desired workers, ale 0 available; loaded route bola generation 92, zatiaľ čo Git obsahoval approved generation 91. Súčasne audit zaznamenal nový Pod `settlement-debug-7f91` a použitie provider credentialu workload principalom `system:serviceaccount:payments-prod:settlement-debug`.

Principal `urn:atlas:human:7421` bol ráno presunutý z Payments Operations do Finance Analytics. HR source zmenu evidoval správne, ale mover synchronizácia bola add-only. Direct group sa odstránila, no nested path `finance-emea → legacy-shared-operations → prod-payment-operators` zostala a existujúca WebAuthn browser session nebola revoke-nutá.

Hypotézy zahŕňali provider outage, chybný GitOps rollout, kompromitovaný workload, legitímny drill a stale human access. Diskriminačný dôkaz spojil session actor, nested group claim, ClusterRoleBinding, `create pods`, výber ServiceAccountu, následný Secret mount, config patch a scale-to-zero. Git source sa nezmenil. Root cause preto nebola authentication failure ani GitOps source; bola to incomplete mover reconciliation. Broad operator role vytvorila causal amplifier.

Confidentiality bola porušená použitím provider private-key capability. Integrity bola porušená neapproved route generation. Availability bola porušená scale-to-zero a zastavením final settlement. Append-oriented audit zostal dostupný, takže bolo možné rekonštruovať human-to-workload delegation chain.

## Evidence-preserving containment a authoritative recovery

Containment najprv zastaví ďalší impact bez zničenia identity a runtime evidence. Revoke-ne session a odvodené tokeny, suspenduje principal, zablokuje affected binding, izoluje malicious Pod a zachová IdP events, group graph, Kubernetes audit, Secret-access evidence, GitOps diff a settlement timeline. Broad restart control planes alebo okamžité zmazanie Podu by odstránili volatilný dôkaz bez odstránenia alternate access pathu.

Authoritative recovery potom odstráni príčinu a obnoví business state:

```text
complete entitlement reconciliation
→ revoke stale sessions a workload descendants
→ rotate provider generation 34 na 35
→ restore signed route generation 91
→ reconcile 12 settlement workers
→ classify known a unknown provider outcomes
→ reconcile ledger a provider state
→ replace broad operator role JIT capability
→ repeat negative a second-session tests
```

Blind retry nie je prijateľný recovery krok. Operácie s unknown provider acknowledgementom sa musia najprv reconciliovať, inak availability remediation vytvorí integrity incident cez duplicate authorization.

Acceptance verdict vyžaduje, aby validná settlement operácia opäť prešla do 2.5 sekundy, generation 35 bola jediná akceptovaná provider credential, loaded route zodpovedala signed generation 91 a principal 7421 neuspel cez direct, nested, existing-session ani fresh-login path. Legitímny JIT operator musí stále vykonať presne povolenú recovery akciu; security control, ktorý zablokuje všetkých, nie je úspešná CIA ochrana.

## Kontrolné otázky

1. Prečo encryption at rest nebráni zneužitiu secretu cez authorized Pod projection?
2. Čo odlišuje configured, loaded a effective security control?
3. Prečo direct `get secret = no` neuzatvára confidentiality verdict?
4. Aké dôkazy spájajú content integrity s dôveryhodným pôvodom a runtime stavom?
5. Prečo fail-open break-glass môže zlepšiť availability a súčasne zničiť C aj I?
6. Ktorý dôkaz odlíšil stale entitlement od chybného GitOps source-u?
7. Prečo recovery musí klasifikovať unknown provider outcomes pred retryom?

## Referencie

- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [NIST SP 800-53 Security and Privacy Controls](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [Kubernetes authorization](https://kubernetes.io/docs/reference/access-authn-authz/authorization/)
- [Open Policy Agent policy language](https://www.openpolicyagent.org/docs/latest/policy-language/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cardinality](../12-observability/cardinality.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Authentication, authorization a auditing →](authentication-authorization-auditing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->