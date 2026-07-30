# Application promotion

Application promotion je riadená zmena authority: presne identifikovaný release candidate získava oprávnenie stať sa desired generation konkrétneho environmentu. Nie je to opätovný build, spustenie rovnakého jobu s parametrom `production` ani samotný merge pull requestu. Promotion musí zachovať identity continuity od testovaného artifactu cez schválený environment delta až po runtime a business outcome.

```text
immutable candidate a release contract
→ subject-bound evidence
→ target-specific eligibility
→ fresh promotion proposal
→ policy a approval
→ final-merge revalidation
→ authoritative environment transition
→ GitOps reconciliation
→ runtime generation a business acceptance
→ recovery a second promotion
```

Kľúčový invariant znie: artifact a configuration contract, ktoré prešli staging evidence, musia byť tie isté, ktoré production controller vyrenderuje a workload skutočne načíta. Ak sa medzitým zmení shared base, route policy, chart, schema, secret reference alebo target base commit, pôvodné approval už neautorizuje current subject.

## 1. Build, deploy, promote, release a expose

Build transformuje source a pinned inputs na immutable artifact s digestom, provenance a test evidence. Deploy mení desired alebo live state environmentu, aby sa generation pokúsila bežať. Promote mení environment authority. Release je širší operational/product contract vrátane migrations, supportu a recovery. Expose mení traffic alebo používateľský cohort.

Tieto states sa nesmú zlúčiť:

```text
artifact built
≠ candidate eligible
≠ production desired
≠ reconciled
≠ healthy
≠ exposed
≠ business accepted
```

Production Git commit môže byť merged a Flux môže ešte zlyhať. Deployment môže byť healthy, ale traffic stále používa old ring. Feature exposure môže prejsť, no provider alebo data outcome môže byť incorrect. Promotion ledger preto potrebuje samostatné states pre proposal, validation, approval, authoritative transition, reconciliation, technical readiness, exposure a business acceptance.

## 2. Exact promotion subject

Promotion subject nie je image tag. Obsahuje service a source commit, immutable image/chart/package digests, provenance a SBOM identities, environment repository a current target base revision, values a overlay generation, route a policy generations, schema/event/API compatibility, secret-reference contract, target cluster/region/tenant, rollout a rollback boundaries, evidence snapshot, policy version, approver authority a final runtime/business evidence.

Praktická release coordinate môže vyzerať takto:

```text
release manifest R-910a
→ image sha256:pay910a
→ chart sha256:chart91
→ route policy minimum 1850
→ schema compatibility 42..44
→ event contract settlement.v3
→ provider credential interface pv-42+
→ policy bundle P-185
```

Environment-specific replicas, endpoints alebo exposure percentage sa môžu líšiť. Musia však zostať v povolenom compatibility envelope. Overlay nesmie potichu zmeniť artifact invariant, napríklad required event version alebo minimálnu route-policy generation, a potom stále používať staging evidence nad iným behaviorom.

## 3. Build once a promote the same bytes

Silný model buildne artifact raz a medzi environmentmi mení iba jeho authority:

```text
source/build inputs
→ digest D
→ CI evidence pre D
→ staging desired D
→ staging runtime D
→ production proposal D
→ production runtime D
```

Rebuild per environment vytvára nový subject. Rovnaký source commit môže pri mutable base image, package repository, compileri, clocku alebo architecture vyprodukovať digest `Ds` v stagingu a `Dp` v production. Staging tests potom nedokazujú production artifact.

Build-once pravidlo neznamená identickú environment configuration. Znamená explicitné oddelenie immutable application/release contractu od target-owned values a dokazovanie, že ich kombinácia zostáva compatible.

## 4. Evidence bundle a freshness

Evidence je decision input viazaný na presný subject, nie kolekcia zelených odkazov. Každý výsledok potrebuje candidate digest, environment a fidelity, test/policy generation, timestamp a expiry alebo invalidation rules. Signature dokazuje signer a subject, nie functional correctness. Staging canary dokazuje konkrétnu running image/config combination, nie mutable tag alebo neskorší shared-base tip.

Promotion policy môže používať provenance, SBOM/vulnerability verdict, unit/integration/contract/component/E2E tests, migration matrix, staging reconciliation revision, running digests, load/capacity evidence, operational readiness a business canary. Dôkazy však nie sú voľne zameniteľné. Mock-provider test nenahrádza target provider compatibility. Staging dataset nenahrádza production-scale migration lock evidence. Scan nad tagom nenahrádza scan nad exact digestom.

Evidence sa invaliduje, keď sa zmení candidate, transitive dependency, environment revision, route/schema/secret contract, policy version, target base alebo required external condition. Approval bez freshness contractu je iba historický názor.

## 5. Promotion PR ako optimistic transaction

Pull request môže byť promotion transactionom, ak reviewer vidí exact candidate, current target base, final rendered delta, transitive changes, evidence a recovery consequences. Syntaktická zmena `tag: 9.0 → 9.1` nestačí.

Review subject je:

```text
expected candidate release manifest
+ expected source/staging revision
+ expected target base commit
+ rendered production delta
+ evidence snapshot
+ policy version
+ approval identities
```

Approval je optimistické rozhodnutie nad týmto snapshotom. Automatický rebase alebo nový commit mení transaction subject. Final merge preto potrebuje compare-and-swap preconditions a opakovaný render/policy gate. Ak target base pokročil alebo shared dependency zmenila resolved content, proposal sa vracia do validation; nemá sa ticho rebase-nuť a merge-nuť.

## 6. Stale promotion a transitive dependency race

Typický race vznikne medzi staging evidence a final merge:

```text
T1 candidate A prejde stagingom
T2 proposal A vznikne
T3 shared base alebo target sa zmení na B
T4 old proposal je schválený
T5 final merge vyrenderuje A + časť B
```

Ochranné preconditions sú expected source environment commit, candidate/release-manifest digest, target base commit, policy/evidence versions a transitive dependency graph. Final-merge render musí byť porovnaný s reviewed renderom. Semantic conflict môže existovať aj bez Git text conflictu: dve promotions môžu meniť odlišné files, ale spolu aktivovať netestovanú schema/consumer combination.

Serialization, merge queue alebo semantic conflict detection preto patria do production promotion, najmä pri shared routes, policies, schemas, secrets a platform components.

## 7. Stateful compatibility a rollback

Code artifact sa dá zmeniť novým desired-state commitom; data, schema, events alebo external effects sa nemusia vrátiť rovnakým mechanizmom. Promotion gate musí poznať reader/writer matrix, migration ordering, mixed-version cohorts, rollback compatibility a unknown side-effect recovery.

Bezpečný expand/contract chain je:

```text
expand schema alebo protocol
→ old aj new versions compatible
→ promote new readers/writers
→ bounded backfill a convergence
→ verify old consumers absent
→ contract cleanup
```

Rollback image digestu po destructive migration nemusí byť bezpečný. Recovery môže vyžadovať roll-forward, compensation alebo reconciliation. Promotion record preto uchováva per-layer rollback eligibility, nie jedno generické tlačidlo `rollback`.

## 8. Automation a operation state

Candidate discovery, proposal creation, policy approval, merge, GitOps reconciliation a exposure môžu byť automatizované, ale každý krok má inú authority. Image automation vyberajúca registry digest nemá automaticky právo meniť production desired state. Portal, ktorý vytvorí PR, nevykonal deployment. GitOps controller, ktorý syncne resources, nepotvrdil business outcome.

End-to-end operation potrebuje stable ID a durable states:

```text
Proposed
→ Validating
→ Approved
→ Authoritative
→ Reconciling
→ TechnicallyReady
→ Exposing
→ BusinessAccepted
```

Vedľajšie states zahŕňajú `Blocked`, `Superseded`, `Failed`, `UnknownOutcome`, `RollingBack` a `ReconciliationRequired`. Lost response po merge alebo controller timeout sa rieši read-backom Git ref-u, controller operation a runtime generation. Blind retry nesmie vytvoriť druhý promotion PR alebo znovu spustiť non-idempotent hook.

## 9. Connected incident `GITOPS-PAY-62`

Staging evidence `E-778` potvrdila `pay910a`, route generation `1850` a credential contract `pv-42`. Production proposal `P-441` však čítala tri independently mutable inputs: staging path na commit-e `S1`, shared base `main` a cluster-local LaunchPad substitution ConfigMap.

Kým proposal čakala na approval, image automation zmenila shared base na `pay910b` a LaunchPad zmenil route substitution na `1849`. Merge automation návrh rebase-la bez final-render a evidence revalidation. Production artifact `b71f203` preto viedol k:

```text
approved evidence: pay910a / route 1850 / pv-42 contract
promotion UI:      pay910a / route 1850
Flux render:       pay910b / route 1849 / Secret pv-42
runtime:           pay910b / route 1849 / loaded pv-42
provider later:    pv-43 active, pv-42 revoked
```

Root cause bola promotion decision bez compare-and-swap nad immutable candidate a target base state-om. Approval autorizoval subject A, ale final merge a Flux vykonali subject B. `2 746` settlements použilo stale route `1849`; následná credential divergence spôsobila `61` failed calls a `14` unknown outcomes.

## 10. Authoritative redesign

Redesign zavádza immutable release manifest `R-910a` ako jediný promoted subject. Manifest pinne application artifact a všetky decision-critical compatibility coordinates. Staging evidence sa viaže na `R-910a` a exact staging environment revision. Production PR mení iba reference na `R-910a` a nesie expected target base commit.

```text
R-910a candidate
→ staging desired/reference
→ staging runtime a canary evidence
→ production proposal + target-base CAS
→ final-merge render/policy revalidation
→ authoritative production commit
→ Flux observed revision
→ runtime generation endpoint
→ production business canary
→ ledger BusinessAccepted
```

Critical substitutions mimo Git sú odstránené. Runtime endpoint reportuje artifact, route/config a secret generations. Promotion operation sa neoznačí completed po PR merge; končí target-specific acceptance alebo explicitným failed/unknown verdictom.

## 11. Acceptance paths, troubleshooting a anti-patterny

Positive path zachová candidate identity od build-u po business canary. Stale-proposal path invaliduje approval po zmene candidate-u, transitive dependency alebo target base-u. Recovery path po lost merge response-e read-backne authoritative ref a pokračuje bez duplicate transitionu. Stateful path odmietne unsafe rollback. Forbidden path odmietne mutable tag ako subject, rebuild per environment, hidden configuration, auto-rebase bez revalidation, concurrent lost update a false completion po merge.

Troubleshooting porovnáva candidate digest, staging desired/runtime generation, evidence freshness, proposal source/target commits, rendered delta, final merge commit, GitOps resolved revision, live artifact/config/secret/schema generations, exposure cohort a business outcome. Prvá odlišná generation určuje failure boundary.

Anti-patterny sú: „staging bolo zelené, approval platí navždy“, „merge znamená successful promotion“, „skopíruj celý staging overlay“, „rollback je iba starý image digest“ a „dve merge-nuteľné PR sú automaticky semantically compatible“.

## Glossary impact

Relevantné pojmy: promotion subject, immutable candidate, release manifest, build-once promotion, subject-bound evidence, evidence freshness, target-base compare-and-swap, final-merge revalidation, semantic promotion conflict, promotion ledger, superseded proposal, unknown promotion outcome a promotion acceptance verdict.

## Primárne zdroje

- [OpenGitOps — Principles](https://opengitops.dev/)
- [Flux — Repository structure](https://fluxcd.io/flux/guides/repository-structure/)
- [Flux — Image update automation](https://fluxcd.io/flux/guides/image-update/)
- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [SLSA — Provenance](https://slsa.dev/spec/v1.1/provenance)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Flux](flux.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: GitOps secrets →](gitops-secrets.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
