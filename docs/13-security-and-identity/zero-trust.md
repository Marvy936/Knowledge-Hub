# Zero Trust

Zero Trust je resource-centric security architecture, ktorá neudeľuje implicitnú dôveru iba podľa network location, organizational ownership alebo predchádzajúceho loginu. Každý access sa viaže na exact principal, action, resource a context; rozhodnutie sa presadí na všetkých relevantných paths, session zostáva bounded a zmena identity, posture, policy, threat alebo incident state-u môže existujúcu dôveru zrušiť.

Zero Trust nie je synonymum MFA, VPN replacement, service mesh ani microsegmentation. Tieto mechanizmy môžu byť súčasťou architecture, ale výsledok závisí od identity assurance, resource-specific authorization, complete enforcement coverage, continuous evidence a revocation. Platná WebAuthn session alebo mTLS certificate nie je všeobecná dôvera pre všetky resources.

## Resource-access lifecycle

Zero Trust rozhodnutie je časovo bounded verdict nad exact principalom, action, resource a current contextom. Lifecycle preto oddeľuje identity assurance, posture, enforcement coverage, continuous re-evaluation a revocation existing sessions.

```text
business operation a protected resource
→ human/workload/device identities a assurance
→ exact action, data a environment scope
→ posture, policy, threat a resource context
→ resource-specific decision
→ bounded session alebo communication path
→ enforcement na každej access ceste
→ continuous evidence a re-evaluation
→ revocation, containment a trust recovery
→ allowed, forbidden, bypass a second-operation validation
```

Authentication vytvorí principal. Zero Trust decision stále potrebuje current eligibility a resource context. Network location je signal, nie authority. Session issuance je začiatok, nie koniec access lifecycle-u.

## Exact access subject SEC-PAY-51

Access subject spája human a workload identity, device posture, policy generation, bypass path a exact runtime digest. Toto rozlíšenie ukazuje, že validná authentication a internal network location nepreukazujú current resource authorization.

```yaml
incident: SEC-PAY-51
humanPrincipal: urn:atlas:human:7421
humanAuthentication: WebAuthn
humanSessionLifetime: 8h
humanDevice: LAPTOP-7421
devicePostureGeneration: EDR-POSTURE-771
postureEventDeliveryDelay: 47m
workloadPrincipal: spiffe://atlas.example/ns/releases/sa/atlas-release-controller
workloadAuthentication: mTLS
resource: production image deployment
requestedAction: deploy
networkContext: corporate-vpn-and-internal-cluster
policyExpected: POL-IMG-18
policyLoaded: POL-IMG-16
bypassPath: AtlasRelease custom controller
selectedRuntimeDigest: sha256:pay7240-arm
```

Subject ukazuje, že všetky principals mali platné authenticators. Incident napriek tomu vznikol cez broad sessions, stale context a incomplete enforcement.

## Resource-centric authorization

Decision subject má formu:

```text
principal + action + resource + context + policy generation
```

Resource nie je iba service hostname. Pri deployment-e je to exact environment, cluster, namespace, workload, platform digest a release generation. Action `deploy` môže znamenať create release request, mutate desired state, approve promotion alebo create Pod; každá capability má inú authority.

Resource-specific token alebo session má narrow audience a scope. Broad bearer token `atlas-internal` s osemhodinovou lifetime umožní replay naprieč APIs. High-risk deployment môže vyžadovať audience `release-api`, action `release.promote`, exact release subject, recent phishing-resistant step-up, healthy managed device, JIT approval a current policy.

## Identity assurance nie je identity existence

Human identity zahŕňa authoritative employment state, authenticator assurance, session generation, device binding a privileged/JIT context. Workload identity zahŕňa trust domain, namespace, ServiceAccount, deployment generation, node/runtime attestation a token/certificate lifetime.

mTLS preukazuje control private key-u a trusted certificate chain. Nehovorí, že workload smie každý resource. SPIFFE-style identity môže byť stabilná, no authorization stále viaže exact action/environment. Certificate vydaný pred compromise môže zostať platný, ak revocation alebo short lifetime nefunguje.

## Device a workload posture

Posture je decision input, nie permanentný label `managed=true`. Môže zahŕňať OS/security-patch state, disk protection, EDR health, secure boot, compromise/quarantine event a attestation freshness. Posture authority, timestamp a failure semantics sú explicitné.

Stale posture je unknown, nie healthy. Ak EDR event pipeline zaostáva 47 minút, session nemusí byť re-evaluovaná. Policy môže pre high-risk action vyžadovať posture younger than 5 minutes a online quarantine check; pre low-risk read môže povoliť bounded stale window.

Workload posture analogicky zahŕňa signed artifact, runtime digest, node attestation, policy generation, namespace/tenant a service identity. „Pod beží v production clusteri“ nie je assurance.

## Policy decision a continuous evaluation

```rego
package atlas.zerotrust.release

default allow := false

allow if {
  input.action == "release.promote"
  input.resource.environment == "production"
  input.principal.assurance == "phishing-resistant"
  input.principal.jit.active
  input.device.posture == "healthy"
  time.parse_rfc3339_ns(input.context.now) - time.parse_rfc3339_ns(input.device.observed_at) < 300000000000
  input.release.selected_platform_digest == input.release.signed_platform_digest
  input.policy.loaded_generation == "POL-IMG-18"
  not input.release.quarantined
}

deny contains reason if {
  input.policy.loaded_generation != "POL-IMG-18"
  reason := "stale enforcement generation"
}

deny contains reason if {
  input.device.posture == "quarantined"
  reason := "device quarantine requires session revocation"
}
```

Policy source preukazuje intended decision. Nepreukazuje posture authority, event freshness, PEP coverage, loaded bundle alebo revocation existing channelu. Runtime metrics a canaries musia potvrdiť all paths.

Local fixture:

```bash
opa eval \
  --data policy/zero-trust-release.rego \
  --input testdata/quarantined-device.json \
  'data.atlas.zerotrust.release'
```

Výstup preukazuje decision pre konkrétnu input/policy generation. Nepreukazuje, že EDR quarantine event dorazí do production PDP do objective-u alebo že existing API/websocket session sa po deny ukončí.

## Bounded sessions a sender binding

Access token/session lifetime sa volí podľa risku, revocation capability a user/workload experience. Dlhá bearer session znižuje authorization-server dependency, ale predlžuje stale trust. Krátka session bez reliable renewal môže vytvoriť availability incident.

Sender-constrained token, device-bound session alebo mTLS-bound workload token znižuje replay z ukradnutej value. Nezabráni attackerovi ovládajúcemu legitímne zariadenie alebo workload. Continuous posture a behavior evidence preto dopĺňajú cryptographic binding.

High-risk action môže vyžadovať step-up a transaction confirmation. Step-up sa viaže na exact operation, nie iba obnoví všeobecnú osemhodinovú admin session.

## Enforcement coverage

Zero Trust policy musí byť presadená na každej relevantnej access path-e: public API, internal API, background worker, custom controller, batch/recovery tool, admin UI, direct cloud/Kubernetes path a service-to-service channel. Network path môže obísť gateway; privileged controller môže obísť human PEP.

Coverage inventory obsahuje expected operations a PEP. Canary testuje allowed aj forbidden request cez každú cestu. Service mesh authorization chráni proxied traffic, nie host-network process, direct storage credential alebo cloud control-plane API.

## Network ako signal a containment vrstva

Microsegmentation znižuje reachable paths a blast radius. Default deny a resource-specific flows sú užitočné, ale network identity sa môže zmeniť cez proxy/NAT a internal location nepreukazuje principal. VPN access nie je application authorization.

Príklad Kubernetes NetworkPolicy:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: release-controller-egress
  namespace: releases
spec:
  podSelector:
    matchLabels:
      app: atlas-release-controller
  policyTypes: ["Egress"]
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: policy-system
      ports:
        - protocol: TCP
          port: 8443
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: registry-proxy
      ports:
        - protocol: TCP
          port: 443
```

Manifest preukazuje intended egress graph pre selected Pods. Nepreukazuje CNI enforcement, DNS path, hostNetwork bypass, cloud API egress ani Resource Server authorization. Network control dopĺňa identity/policy, nenahrádza ich.

## Continuous diagnostics a revocation

Re-evaluation triggers zahŕňajú identity mover/leaver, device quarantine, workload digest change, signer revocation, policy generation, threat intelligence, impossible travel alebo incident declaration. Event pipeline má freshness objective a replay/recovery semantics.

Revocation musí zasiahnuť tokens, cookies, mTLS channels, workload credentials, cached decisions a existing long-lived streams. Odstránenie usera z group bez session invalidation nie je continuous trust. Admission deny nezastaví už bežiaci malicious workload.

Decision cache je viazaná na principal/session, exact resource/action, policy generation, posture generation, quarantine state a expiration. Cache na „user is admin“ je broad a stale.

## Visibility a privacy

Zero Trust potrebuje telemetry pre identity, device, workload, policy, PEP a resource events. Zber všetkého nie je automaticky bezpečný; posture a behavior data sú sensitive. Telemetry má purpose, minimization, retention, access control a integrity. Chýbajúca signal sa odlišuje od healthy resultu.

Audit zachová original actor, workload/service identity, device/posture generation, policy revision, exact resource, decision, reason a side effect. Correlation nesmie spoliehať na mutable IP alebo display name.

## Incident SEC-PAY-51

Human principal mal validnú WebAuthn session a bol na corporate VPN. Workload controller mal validný mTLS identity. Human bearer token bol broad a platil osem hodín. EDR quarantine event prišiel do PDP o 47 minút neskôr. Admission používal stale `POL-IMG-16` a custom `AtlasRelease` controller mal exempt path.

Compromised arm64 artifact preto prešiel cez controller napriek tomu, že exact selected digest nemal signature. Valid identities a internal network vytvorili implicit trust. Root cause bol incomplete resource-access/enforcement/revocation contract; broad token, stale posture, policy skew a controller bypass boli amplifiers.

Competing hypotheses boli stolen identity, mTLS compromise, registry mutation, policy cache, EDR delay a custom-controller bypass. Authentication logs preukázali valid principals; policy generation, event timestamps, decision cache a audit path ukázali stale context a missing PEP.

## Containment a trust recovery

Containment revoke-ne human session a workload credential, quarantinuje selected digest, zastaví custom controller path, invaliduje decision caches a zachová identity, posture, policy, controller a runtime evidence. Network isolation obmedzí blast radius, ale nie je jediná remediation.

Recovery nasadí short-lived device-bound JIT human session, audience-bound workload identity, event-driven posture/signer/policy revocation, immutable `POL-IMG-18`, complete native/custom PEP coverage a resource-specific decision. Running old digest sa nahradí a rollback path sa zablokuje.

Acceptance vyžaduje allowed legitimate promotion s healthy fresh posture a signed selected digest; deny quarantined device, stale posture, wrong audience, stale policy, unsigned platform a custom-controller bypass. Existing sessions/channels musia po quarantine skončiť v objective-e. Druhá release operation a druhý posture-change event musia vyvolať fresh decision bez 47-minútového stale windowu.

## Maturity a migration

Zero Trust sa zavádza podľa resource/risk, nie big-bang produktom. Najprv inventory principals/resources/paths, potom explicitné identity a policy, bounded sessions, complete enforcement, continuous evidence a automated revocation. Legacy resources môžu dočasne používať gateway alebo segmented access, ale exception má ownera a retirement plan.

Maturity sa meria coverage exact resources a operations, revocation latency, stale-decision rate, bypass inventory, policy generation convergence a negative canary success. Počet nasadených agents alebo MFA coverage sám nepreukazuje resource protection.

## Kontrolné otázky

1. Prečo WebAuthn, mTLS alebo VPN samostatne nevytvárajú Zero Trust?
2. Ako resource-specific decision presahuje role/scope check?
3. Prečo stale posture musí byť unknown, nie healthy?
4. Ktoré fields patria do decision cache key-u?
5. Ako NetworkPolicy dopĺňa, ale nenahrádza authorization?
6. Prečo admission deny nezastaví running workload?
7. Ktoré second-operation tests uzatvárajú continuous revocation?

## Referencie

- [NIST SP 800-207 Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final)
- [CISA Zero Trust Maturity Model](https://www.cisa.gov/resources-tools/resources/zero-trust-maturity-model)
- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [SPIFFE specifications](https://spiffe.io/docs/latest/spiffe-about/overview/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Policy as Code](policy-as-code.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Reliability, availability a durability →](../14-sre-and-operations/reliability-availability-durability.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
