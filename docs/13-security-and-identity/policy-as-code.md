# Policy as Code

Policy as Code vyjadruje opakovateľné rozhodnutia o povolenom stave alebo operácii ako versionované, testovateľné a automaticky vyhodnocované rules. Policy file však nie je control. Control vznikne iba vtedy, keď exact input zachytí správny Policy Enforcement Point, decision engine používa intended policy a data generation, výsledok sa správne presadí a všetky bypass, exception, outage a recovery paths sú overené.

„Policy testy sú green“ nepreukazuje runtime coverage. „Admission webhook healthy“ nepreukazuje loaded revision. „Deny v audite“ nepreukazuje, že side effect nenastal cez iný controller. Policy engineering musí spájať intent, input schema, artifact identity, distribution, decision, enforcement a evidence.

## Intent-to-enforcement lifecycle

```text
business alebo security intent
→ exact decision subject a input contract
→ executable policy a supporting data
→ immutable policy artifact a generation
→ distribution a loaded state
→ structured decision a reason
→ authoritative enforcement na každej ceste
→ decision audit a runtime side-effect evidence
→ exception, rollout, rollback a revocation
→ bypass a second-decision validation
```

Policy môže rozhodovať pri CI, registry promotion, API admission, runtime requeste alebo periodic audit-e. Tieto observation points majú odlišnú authority a freshness. Shift-left check je rýchly feedback, ale nenahrádza final deployment PEP, kde sú známe resolved digest, environment a runtime identity.

## Exact policy subject SEC-PAY-51

Policy subject spája intended generation, loaded generation, input schema, cache a každý enforcement path. Bez tejto väzby môže správna rule rozhodovať nad neúplným inputom alebo zostať mimo custom-controller side effectu.

```yaml
incident: SEC-PAY-51
policyIntent: production may run only exact trusted multi-platform digests
sourcePolicyGeneration: POL-IMG-18
loadedAdmissionGeneration: POL-IMG-16
customControllerGeneration: CTRL-REL-9
inputContractExpected:
  - resolvedImageDigest
  - selectedPlatformDigest
  - signerIdentity
  - provenanceBuilder
  - sbomSubject
  - quarantineState
observedInput:
  - repository
  - mutableTag
failurePolicy: Ignore
cacheKey: repository-tag
bypassPath: AtlasRelease custom controller
```

Subject ukazuje tri rozdielne defects: revision skew, incomplete input a incomplete enforcement coverage.

## Policy input je security contract

Policy nemôže rozhodnúť o field-e, ktorý input neobsahuje alebo ktorému nemožno dôverovať. Admission input `image: payments:7.24.0` nevie rozlíšiť digest ani platform. User-supplied tenant label nie je trusted tenant identity. Claim `scanner=passed` nie je scan evidence.

Input contract definuje field names, types, authority, freshness, optional/error semantics a maximum size. Missing field sa nesmie potichu interpretovať ako safe default. Ak resolver nedokáže získať digest, policy rozhoduje „unknown“ podľa risk contractu, nie `allow`.

## Rego policy a structured decision

```rego
package atlas.images.production

default allow := false

allow if {
  input.environment == "production"
  startswith(input.resolved_image_digest, "sha256:")
  startswith(input.selected_platform_digest, "sha256:")
  input.signature.subject == input.selected_platform_digest
  input.signature.identity == "https://github.com/Marvy936/atlas-payments/.github/workflows/release.yml@refs/heads/main"
  input.provenance.subject == input.selected_platform_digest
  input.provenance.builder == "atlas-trusted-builder-v4"
  input.sbom.subject == input.selected_platform_digest
  not input.quarantine.denied
  input.policy_generation == "POL-IMG-18"
}

deny contains reason if {
  input.signature.subject != input.selected_platform_digest
  reason := "signature subject does not match selected platform digest"
}

deny contains reason if {
  input.loaded_policy_generation != "POL-IMG-18"
  reason := "enforcement point loaded stale policy generation"
}
```

Policy source preukazuje intended rules. Nepreukazuje signed policy artifact, loaded bundle, resolver correctness, complete PEP coverage ani absence race medzi decisionom a mutation.

Local evaluation:

```bash
opa eval \
  --data policy/images.rego \
  --input testdata/arm64-unsigned.json \
  'data.atlas.images.production'

conftest test testdata/arm64-unsigned.json \
  --policy policy
```

Výstup preukazuje decision konkrétnej policy/test-data generation. Nepreukazuje production input parity, external data freshness, admission timeout behavior alebo custom-controller enforcement.

## Policy artifact, distribution a loaded generation

Policy source sa buildne do immutable artifactu alebo bundle s digestom, schema version a supporting data references. Distribution môže používať GitOps, bundle server alebo controller reconciliation. Runtime musí publikovať loaded generation a last successful refresh.

Source commit `POL-IMG-18` pri loaded `POL-IMG-16` znamená stale enforcement, aj keď deployment controller hlási healthy. Readiness má závisieť od successful parse/compile a expected generation, nie iba process health.

Bundle signature chráni policy artifact integrity. Supporting data — signer allowlist, tenant mapping, quarantine list — má vlastnú generation a freshness. Policy artifact bez current data môže rozhodovať nesprávne.

## Enforcement points a bypass inventory

PEP musí byť na authority boundary pred side effectom. CI lint nemôže zabrániť direct API create. API gateway policy nechráni controller, ktorý volá backend interne. Kubernetes admission nevidí image spustený mimo API servera alebo custom path, ak controller vytvára resource s privileged identity a policy ho exemptuje.

Coverage inventory obsahuje native Deployment/Pod/Job/CronJob, custom resources/controllers, debug/ephemeral containers, node/bootstrap, recovery, import a break-glass paths. Každý path má expected decision canary.

Kubernetes CEL policy môže presadiť jednoduchý invariant bez external webhooku:

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: require-digest-images
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["pods"]
  validations:
    - expression: "object.spec.containers.all(c, c.image.contains('@sha256:'))"
      message: "production containers must use immutable digest references"
```

Manifest preukazuje intended Pod invariant. Nepreukazuje binding/parameter scope, loaded API-server capability, signature verification, custom CRD path alebo semantic correctness digestu. CEL je vhodné pre in-request fields; external provenance verification potrebuje trusted resolver/cache alebo iný controller.

## Decision, enforcement a audit

Structured decision obsahuje allow/deny/unknown, policy generation, input subject, matched rule, reason, exception ID a correlation. PEP musí vykonať verdict atomicky s mutation alebo preukázateľne zabrániť side effectu.

Decision log bez sensitive token/secret fields podporuje explainability. Audit porovná policy input digest, decision a created object/runtime state. Ak audit ukazuje deny, ale object vznikol, PEP alebo race zlyhali.

## Exceptions

Exception nie je comment ani namespace label `skip-policy=true`. Má exact subject, ownera, risk, compensating controls, start/expiry, allowed paths a removal trigger. Policy engine vyhodnotí exception ako versionovaný input a audit zachová jej použitie.

Broad permanentná exception pre controller ServiceAccount vytvára bypass, ktorý attacker môže zneužiť cez custom resource. Výnimka má obmedziť konkrétny action/resource/digest a čas.

## Failure behavior a dependency outages

`failurePolicy: Ignore` môže zachovať availability pri webhook outage, ale zmeniť policy na advisory práve počas incidentu. `Fail` chráni integrity, no môže zastaviť urgentný deployment. Voľba sa robí podľa threat modelu a recovery pathu.

Bezpečný návrh môže používať local verified cache, bounded emergency policy generation a pre-authorized recovery artifacts. Timeout sa odlišuje od explicitného deny. Metrics sledujú allow/deny/error/timeout, latency, generation a bypass use.

## Policy rollout a rollback

Policy change môže zablokovať existujúce workloads alebo povoliť forbidden path. Rollout používa test fixtures, audit/dry-run, representative canary, enforcement a runtime validation. Dry-run evidence musí byť complete pre expected population; silent no-match nie je safe result.

Rollback policy môže znovu povoliť known vulnerability. Recovery rozhodnutie porovná current impact a security regression a viaže old generation na short-lived exception, nie permanentný návrat.

## Incident SEC-PAY-51

Source obsahoval `POL-IMG-18`, ale production admission používal `POL-IMG-16`. Input niesol mutable tag a repository, nie selected arm64 digest. Cache key bol tag. Webhook mal fail-open timeout. Custom `AtlasRelease` controller bol exempt a vytváral workload cez privileged identity.

Validný amd64 podpis preto autorizoval repository/tag; arm64 digest prešiel bez exact signature. Pri timeout-e alebo custom-controller path-e sa policy vôbec nepresadila. Root cause bol incomplete intent-to-enforcement contract, nie chyba jednej Rego condition.

Competing hypotheses boli bad signature verifier, stale trust roots, registry mutation, policy revision skew, cache poisoning a controller bypass. Loaded generation metrics, decision input, cache entry a audit create path ukázali všetky tri defects.

## Containment a authoritative recovery

Containment zablokuje custom release path, invaliduje tag cache, prejde na fail-closed pre production image creates s approved recovery exception a zachová policy bundles, decisions, webhook errors a created objects. Needituje live policy ručne bez source closure.

Recovery publikuje immutable `POL-IMG-18`, readiness vyžaduje expected generation, input resolver dodá selected digest/platform/evidence/quarantine a cache sa viaže na digest+policy+trust generations. Custom controller prejde rovnakým decision service alebo vytvára objects, ktoré admission znovu overí bez exemption.

Acceptance vyžaduje allow trusted signed arm64, deny unsigned/wrong-subject/quarantined digest, deny stale policy generation, deny timeout bez approved exception a rovnaký verdict pre native aj custom-controller path. Druhý policy update musí načítať new generation a invalidovať cache bez bypass windowu.

## Kontrolné otázky

1. Prečo policy source nie je control?
2. Ako input authority a freshness ovplyvnia correct rule?
3. Čo local OPA test nepreukazuje?
4. Prečo loaded generation patrí do readiness?
5. Ako sa CEL admission a external evidence policy dopĺňajú?
6. Prečo `failurePolicy: Ignore` mení security semantics?
7. Ktorý second-decision test uzatvára cache a rollout recovery?

## Referencie

- [Open Policy Agent](https://www.openpolicyagent.org/docs/latest/)
- [Rego policy language](https://www.openpolicyagent.org/docs/latest/policy-language/)
- [Kubernetes ValidatingAdmissionPolicy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/)
- [Kyverno documentation](https://kyverno.io/docs/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Image signing](image-signing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Zero Trust →](zero-trust.md)
<!-- KNOWLEDGE-NAVIGATION:END -->