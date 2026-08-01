# Release management

Release management riadi immutable release unit od definície scope-u cez candidate, evidence, deployment a používateľskú exposure až po support, revocation a retirement. Build vytvorí artifact. Deployment umiestni desired generation do runtime. Release sprístupní konkrétnu capability alebo behavior používateľom či business procesom a prijme zodpovednosť za jeho support a recovery.

Release preto nie je Git tag, changelog ani jeden image. Môže obsahovať viac services, migrations, configuration, feature contracts, documentation a support obligations. Exact release identity musí vysvetliť, ktoré artifacts a contracts tvoria podporovanú kombináciu a ktoré production cohorts ich skutočne používajú.

## 1. Dominantný scope-to-lifecycle model

```text
business capability a release scope
→ exact source candidate a compatibility decision
→ immutable multi-artifact release manifest
→ complete a fresh evidence inventory
→ eligibility a timing decision
→ deployment a controlled exposure
→ technical, functional a business acceptance
→ support, incident a security lifecycle
→ supersession, revocation alebo retirement
```

Release lifecycle nekončí po full trafficu. Delayed failures, security findings, consumer migrations a recovery retention pokračujú. Release manager alebo automation musí vedieť, čo je current, supported, vulnerable, revoked a safe na rollback.

## 2. Exact release subject

```yaml
releaseSubject:
  product: atlas-payments
  releaseId: payments-10.0.0-rc.4
  semanticVersion: 10.0.0-rc.4
  releaseManifestDigest: sha256:release1000rc4
  sourceCandidateSha: d94e1c6
  artifacts:
    api: registry.atlas.example/payments-api@sha256:pay1000api
    worker: registry.atlas.example/payments-worker@sha256:pay1000worker
    migrations: object://releases/payments-migrations@sha256:mig1000
    chart: oci://registry.atlas.example/charts/payments@sha256:chart1000
  configurationContractSha: 71ac290
  compatibility:
    database: settlement-schema-v42-expand
    events: settlement-events-v18-compatible
    publicApi: v8
  evidenceBundleDigest: sha256:evidence1000rc4
  support:
    owner: payments-platform
    severityChannel: payments-oncall
    recoveryReference: recovery-payments-10.0-rc4
```

Release ID je human locator. Manifest digest je immutable authority. Semantic version komunikuje compatibility. Všetky tri hodnoty majú odlišný účel a musia zostať korelované.

## 3. Release scope a change inventory

Scope má byť dostatočne malý na diagnosis a recovery, ale complete voči dependencies. „Payments release“ bez inventory môže skryť schema, event consumer, IAM alebo provider routing changes.

Release change inventory zahŕňa:

```text
application artifacts
+ database migrations a compatibility phases
+ event/API schemas
+ configuration a feature contracts
+ infrastructure/policy dependencies
+ external provider changes
+ documentation a operational procedures
+ support/deprecation commitments
```

Scope freeze neznamená zákaz urgentnej opravy. Znamená, že každá zmena po freeze vytvára novú candidate generation a invaliduje relevantné evidence.

## 4. Candidate a release states

Atlas používa explicitný state machine:

```text
DRAFT
→ CANDIDATE_BUILT
→ EVIDENCE_COMPLETE
→ ELIGIBLE
→ DEPLOYING
→ PARTIALLY_EXPOSED
→ FULLY_EXPOSED
→ ACCEPTED
→ SUPPORTED
→ SUPERSEDED
→ RETIRED
```

Alternate states:

```text
REJECTED
PAUSED
RECOVERING
REVOKED
WITHDRAWN
```

`DEPLOYED` a `RELEASED` nie sú synonymá. New Pods môžu byť nasadené bez trafficu. Feature flag môže release vystaviť bez nového deploymentu. Release record sleduje všetky relevantné exposure axes.

## 5. Signed release tag a manifest

Git tag môže byť reference k source candidate-u, ale nesmie nahradiť artifact manifest. Signed tag pomáha overiť source release intent:

```bash
git tag -s payments-10.0.0-rc.4 "$CANDIDATE_SHA" \
  -m 'Atlas Payments 10.0.0 release candidate 4'
git show --show-signature payments-10.0.0-rc.4
```

Signature preukazuje tag object a signer podľa configured trust. Nepreukazuje artifact bytes, build provenance ani production deployment. Release manifest viaže source k artifacts a evidence.

Manifest integrity možno chrániť detached signature:

```bash
cosign sign-blob \
  --bundle release-manifest.sigstore.json \
  release-manifest.json

cosign verify-blob \
  --bundle release-manifest.sigstore.json \
  --certificate-identity-regexp='^https://github.com/atlas/payments/' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  release-manifest.json
```

Successful verification preukazuje blob identity a signer policy. Nepreukazuje pravdivosť manifest claims; artifact registry a evidence store read-backs ich musia potvrdiť.

## 6. Release evidence package

Evidence package nie je ZIP všetkého, čo pipeline vyprodukovala. Je to indexed set required evidence s validity a raw references:

```yaml
evidencePackage:
  subjectDigest: sha256:release1000rc4
  required:
    - candidate-ci
    - api-event-compatibility
    - sbom-signature-provenance
    - vulnerability-policy
    - migration-rehearsal
    - rollback-rehearsal
    - staging-business-canary
    - production-bounded-canary
  passed:
    - candidate-ci
    - api-event-compatibility
    - sbom-signature-provenance
    - vulnerability-policy
    - migration-rehearsal
    - rollback-rehearsal
    - staging-business-canary
  pending:
    - production-bounded-canary
```

Candidate môže byť eligible na 2 % canary, ale ešte nie accepted na full release. Evidence states sa viažu na transition, nie na jeden globálny green label.

## 7. Release timing a change coordination

Continuous Delivery umožňuje release on demand, no business timing môže byť relevantný. Partner maintenance, regulatory window, support coverage alebo high-risk calendar môžu ovplyvniť transition. Timing decision nesmie meniť artifact ani evidence; iba rozhodne, kedy eligible subject vstúpi do ďalšieho state-u.

Koordinácia má exact dependencies a ownerov. Broad „freeze“ bez risk modelu môže zvyšovať batch size a nebezpečne odkladať security fixes. Emergency release path má menší scope, nie nižšiu identity a evidence disciplínu.

## 8. Deployment, exposure a release acceptance

Release record koreluje:

```text
manifest digest
→ environment deployment revisions
→ runtime artifact/config generations
→ route/ring/feature exposure
→ observed cohorts
→ acceptance evidence
```

Praktický runtime inventory:

```bash
kubectl -n payments get pods -l app.kubernetes.io/part-of=atlas-payments \
  -o json | jq '[.items[]|{uid:.metadata.uid,release:.metadata.labels["atlas.example/release"],images:[.status.containerStatuses[].imageID]}]'
```

Output preukazuje selected Pod UIDs, release labels a runtime image IDs. Nepreukazuje traffic share, loaded application config alebo business success. Release acceptance potrebuje route/flag read-back a authoritative operation sampling.

## 9. Release notes a communication contract

Release notes majú byť odvodené z release subjectu, nie iba commit list. Obsahujú:

- user-visible changes a compatibility impact;
- required migrations a ordering;
- deprecated/removed contracts;
- configuration a operational changes;
- known issues a active exceptions;
- rollout/exposure scope;
- rollback alebo recovery constraints;
- support owner a relevant deadlines.

Security-sensitive detail sa nemusí publikovať verejne pred remediation, ale internal operators potrebujú presný risk a affected artifact identity.

## 10. Support a ownership

Supported release má ownera, severity response, observability a recovery artifacts. On-call musí vedieť mapovať user symptom na release, runtime cohort a manifest. Ak release ID nie je v logs, metrics alebo events, diagnosis sa spolieha na časovú koreláciu a mutable deployment history.

Support policy definuje:

```text
supported release lines
→ security/bug-fix policy
→ minimum platform/dependency versions
→ end-of-support date
→ migration path
→ artifact/evidence retention
```

Superseded release môže zostať supported. Revoked release sa nesmie ďalej promovať ani považovať za validný recovery target.

## 11. Emergency release

Emergency neznamená preskočiť source, artifact alebo subject identity. Skracuje breadth evidence podľa risku a používa preddefinovaný fast path:

```text
incident a exact defect subject
→ minimal compatible change
→ focused candidate/evidence
→ immutable emergency manifest
→ bounded canary
→ recovery fallback
→ post-release full validation
→ merge-back a support closure
```

Hotfix branch musí byť propagovaný späť do mainline a ďalších supported lines. Inak sa defect alebo fix stratí pri ďalšom release.

## 12. Rollback a withdrawal semantics

Release withdrawal zastaví ďalšiu exposure alebo adoption. Binary rollback je iba jedna recovery možnosť. Manifest musí uviesť per-layer compatibility s current data/event/external state.

Release record po incident-e zachová:

```text
what was exposed
+ which business operations occurred
+ which artifacts/configs/data generations remain
+ which recovery action was applied
+ whether release is withdrawn, revoked or superseded
```

Tag delete alebo UI status `failed` nevráti external side effects a neodstráni already issued events.

## Ako sa candidate zmení na podporovaný release

Release management riadi lifecycle od candidate-u po podporovaný, komunikovaný a neskôr vyradený release. Candidate je presná kombinácia source, artifacts, configuration contractu a evidence, ktorá ešte nemusí byť schválená na všeobecnú expozíciu. Publication vytvorí immutable release manifest a sprístupní artifacts; deployment a traffic activation sú ďalšie samostatné transitions.

Release manifest je authority pre to, čo version obsahuje. Viaže API, worker, migrations, chart, schema a evidence digests. Release notes sú ľudská komunikácia, nie náhrada manifestu. Podpora potrebuje vedieť, ktoré versions sú active, deprecated, revoked a dostupné pre recovery.

Go/no-go rozhodnutie vychádza z risku, compatibility, operability a recovery eligibility. Calendar alebo deadline môže ovplyvniť priority, ale nemá meniť chýbajúce evidence na pass. Exception musí mať bounded scope, explicitný residual risk, ownera a follow-up.

Release nekončí production deploymentom. Tím sleduje adoption, incidents, support signals a business outcomes. Last-known-good artifacts, configuration a database compatibility sa udržiavajú počas deklarovaného recovery window. Revocation musí blokovať ďalšiu promotion a podľa rizika aj runtime admission; delete tagu samotný bežiace digests nezastaví.

Retirement uzatvára dependency a support lifecycle. Pred odstránením starej version sa overia consumeri, rollback claims, data formats a backlog. Release management tak spája technickú identity s komunikáciou, supportom a bezpečným ukončením používania.

## 13. Connected incident `REL-PAY-68`

Atlas release `9.10.0` zahŕňal API image, worker, migration a event schema. Release automation vytvorila notes z commit labels a manifest ukladal iba mutable tags. Reusable workflow vynechal arm64 shard; SemVer policy označila breaking event/idempotency/platform changes ako MINOR.

Po retry bol API tag prepísaný na nový index digest. Staging a production preto používali rozdielne artifacts pod rovnakým release ID. Release dashboard zobrazoval `9.10.0 deployed`, no nevedel identifikovať per-platform digests, database contract ani consumer compatibility.

```text
release scope neúplný
→ version verdict chybný
→ mutable artifact locators
→ evidence pre iný graph
→ production exposure
→ support bez exact manifestu
```

Incident zasiahla arm64 cohortu, old event consumers a PostgreSQL 14 environment. Recovery sa spomalila, pretože „9.10.0“ nebolo jednoznačné.

## 14. Recovery a acceptance verdict

Containment withdraw-ne release, zmrazí tags, inventarizuje runtime digests a zachová release/evidence records. Recovery vytvorí `10.0.0-rc.1` s exact manifestom, correct compatibility verdictom, tolerant consumers a bounded rollout. Chybný release subject sa revokuje, nie prepíše.

Release management je prijaté iba vtedy, keď:

```text
release scope obsahuje všetky artifacts a contracts
+ manifest digest je immutable a signed
+ version decision zodpovedá public compatibility
+ evidence package je transition-specific a complete
+ deployment a exposure sú oddelené
+ runtime cohorts sa mapujú na release subject
+ notes/support/recovery používajú ten istý manifest
+ emergency path zachová identity a merge-back
+ withdrawn/revoked release sa nedá ďalej promovať
+ second environment a second platform resolve-nú rovnakú release unit
```

## 15. Troubleshooting flow

Pri release incidente sleduj:

```text
release ID/version
→ manifest digest a source candidate
→ artifact/config/schema graph
→ evidence a eligibility decision
→ deployments a exposure controls
→ runtime cohort identities
→ business outcomes
→ support/revocation/recovery state
```

Competing hypotheses môžu byť wrong manifest, mutable tag, incomplete scope, stale evidence, wrong version, target drift, partial exposure, feature mismatch alebo unsupported dependency. Release notes samostatne nie sú authoritative inventory.

## 16. Anti-patterny

### Git tag ako celý release

Tag identifikuje source reference, nie built artifacts, configuration a runtime exposure.

### Release notes z commit titles iba

Commit labels nepreukazujú user impact, compatibility ani operational requirements.

### `Deployed` ako `Released`

Runtime môže existovať bez user exposure alebo business acceptance.

### Emergency ako evidence-free cesta

Rýchlosť sa má dosiahnuť pripraveným bounded pathom, nie stratou identity a recovery.

### Prepísanie chybnej release version

Historický consumer a environment potom dostanú nejednoznačné bytes.

## 17. Kontrolné otázky

1. Aký rozdiel je medzi buildom, deploymentom a release-om?
2. Čo tvorí exact release subject?
3. Prečo Git tag nenahrádza release manifest?
4. Ako sa evidence viaže na release transition?
5. Kedy je candidate eligible, exposed a accepted?
6. Čo majú obsahovať release notes?
7. Ako support policy súvisí s artifact retention?
8. Aký je rozdiel medzi superseded, withdrawn a revoked release?
9. Ako emergency path zachová audit a compatibility?
10. Prečo `9.10.0` nebolo jednoznačné v `REL-PAY-68`?
11. Ako sa mapuje runtime cohort na release manifest?
12. Ako sa overí second-environment release identity?

## Glossary impact

Relevantné pojmy: release unit, release subject, release manifest digest, release scope, candidate state, exposure state, acceptance state, evidence package, release timing decision, release notes contract, supported release line, emergency release, release withdrawal, release revocation a lifecycle closure.

## Primárne zdroje

- [Semantic Versioning 2.0.0](https://semver.org/)
- [SLSA specification](https://slsa.dev/spec/)
- [in-toto Attestation Framework](https://github.com/in-toto/attestation)
- [Sigstore Cosign documentation](https://docs.sigstore.dev/cosign/)
- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [Google SRE — Release Engineering](https://sre.google/sre-book/release-engineering/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Semantic Versioning](semantic-versioning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Recreate deployment →](recreate-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
