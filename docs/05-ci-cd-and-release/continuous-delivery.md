# Continuous Delivery

Continuous Delivery je schopnosť udržiavať každý akceptovaný integration candidate v stave, v ktorom možno jeho exact immutable artifacts bezpečne, opakovateľne a na požiadanie nasadiť do produkcie. Produkčný release nemusí byť automatický. Manuálne rozhodnutie však smie vyberať iba z už technicky pripravených a auditovateľných release candidates; nesmie spúšťať ručné skladanie bytes, nezdokumentovanú migráciu ani improvizovaný deployment postup.

Delivery preto nie je vlastnosť jedného pipeline jobu. Je to end-to-end deployability contract medzi artifactom, configuration generation, target platformou, shared data state-om, deployment automation, promotion policy a recovery mechanizmom. Image môže byť kryptograficky dôveryhodný a stále nemusí byť deployable, ak nová verzia nevie coexistovať so starou schema alebo ak target environment nemá potrebnú identity, capacity či dependency generation.

## 1. Dominantný artifact-to-deployability model

Continuous Delivery začína až po CI verdict-e nad exact candidate-om. Ten istý artifact sa potom pohybuje cez risk-specific evidence boundaries. Environmenty nepridávajú nové bytes; pridávajú dôkaz, že rovnaký release subject funguje v relevantnom runtime, identity, data a operational context-e.

```text
CI-accepted candidate a immutable artifacts
→ release subject a expected evidence inventory
→ artifact integrity, provenance a policy verification
→ environment/configuration/shared-state subject
→ deployment plan a preconditions
→ bounded mutation a convergence
→ technical, functional a business read-back
→ promotable alebo rejected verdict
→ release decision
→ recovery eligibility a tested fallback
```

Deployability nie je binárny label uložený na mutable tagu. Je to odvodený verdict platný pre konkrétnu artifact/configuration/platform/data combination a konkrétnu policy generation.

## 2. Exact delivery subject

Atlas Payments modeluje release candidate ako immutable manifest:

```yaml
releaseCandidate:
  releaseId: payments-10.0-rc.4
  sourceCandidateSha: d94e1c6
  artifacts:
    api:
      indexDigest: sha256:pay1000api
      amd64Digest: sha256:pay1000api-amd64
      arm64Digest: sha256:pay1000api-arm64
    worker:
      indexDigest: sha256:pay1000worker
    migrationBundle:
      digest: sha256:pay1000migration
  configuration:
    schemaVersion: 7
    environmentOverlaySha: 71ac290
    featureContractSha: 8b11f20
  sharedState:
    databaseContract: settlement-schema-v42-expand
    eventContract: settlement-events-v18-compatible
  workflow:
    deliverySha: 1e20d55
    policyBundleSha: 66cf902
  requiredEvidence:
    - integration-contract
    - staging-deployment
    - migration-rehearsal
    - rollback-rehearsal
    - production-canary
```

Tento manifest oddeľuje logical release ID od artifact digestov. Zachováva per-platform identity, pretože image index digest samostatne nehovorí, ktorý platform manifest runtime stiahne. Shared-state contracts sú súčasťou subjectu: rovnaký image môže byť deployable pred destructive migration a nekompatibilný po nej.

## 3. Build once, promote the same subject

Delivery pipeline nemá rebuildovať application pre každý environment. Má overiť a promovať rovnaký content-addressed subject:

```bash
api_ref='registry.atlas.example/payments-api@sha256:pay1000api'
worker_ref='registry.atlas.example/payments-worker@sha256:pay1000worker'

crane digest "$api_ref"
crane digest "$worker_ref"
cosign verify "$api_ref" --certificate-identity-regexp='^https://github.com/atlas/payments/' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com'
```

`crane digest` nad digest reference potvrdí, že registry vie resolve-núť daný content subject. `cosign verify` môže potvrdiť signature a signer policy. Ani jeden príkaz nepreukazuje, že staging alebo production použije rovnaký digest, že všetky platform manifests majú správne evidence ani že application je kompatibilná s target data state-om.

Kopírovanie do environment-specific registry sa musí overiť:

```bash
crane copy \
  registry.build.example/payments-api@sha256:pay1000api \
  registry.prod.example/payments-api@sha256:pay1000api

src="$(crane digest registry.build.example/payments-api@sha256:pay1000api)"
dst="$(crane digest registry.prod.example/payments-api@sha256:pay1000api)"
test "$src" = "$dst"
```

Rovnosť digestov preukazuje content identity indexu. Nepreukazuje preservation signatures a attestations, ak ich registry copy mechanism nespracoval. Evidence referrers treba inventarizovať a overiť samostatne.

## 4. Environment nie je iba názov

Environment je exact operational subject: account alebo cluster, Region, namespace, network, identity, dependency endpoints, secret references, policy generations a data state. Názov `staging` môže zostať rovnaký, hoci sa zmenil Kubernetes cluster, database engine alebo admission policy. Promotion evidence musí preto uviesť generation, nad ktorou vzniklo.

```yaml
environmentSubject:
  name: staging-eu
  clusterUid: 46b8d944
  region: eu-central-1
  namespace: payments
  platformRelease: platform-2026.31
  ingressPolicySha: a18d2cf
  workloadIdentityPolicySha: 12c6be0
  databaseEndpointGeneration: pg-staging-42
  secretReferences:
    providerCredential: pv-43
```

Dashboard label `staging healthy` nepreukazuje, že release candidate bol overený proti tejto generation. Evidence musí byť invalidované pri zmene relevantného environment subjectu.

## 5. Risk-specific fidelity

Každé environment má zodpovedať konkrétnej otázke. Ephemeral integration môže overiť wiring a reálne protocol contracts. Staging môže overiť deployment topology, identity, ingress, migration a operability. Performance environment potrebuje representative traffic shape, quotas a data distribution. Production canary pridáva real users, provider limits a skutočný business mix.

Parity neznamená rovnaký počet nodes alebo rovnaké citlivé dáta. Znamená zachovať vlastnosti, ktoré ovplyvňujú testovaný risk. Ak staging používa iný authentication path, iný database engine a obchádza admission, jeho zelený výsledok nepreukazuje production deployability.

## 6. Configuration a rendered-state evidence

Configuration source môže byť validný a rendered output chybný kvôli merge precedence, defaults alebo templating. Delivery preto validuje source, resolved render aj effective runtime state.

```bash
helm dependency build deploy/chart
helm template payments deploy/chart \
  --namespace payments \
  --values environments/staging.yaml \
  --set-string image.digest='sha256:pay1000api' \
  > rendered.yaml

kubectl apply --server-side --dry-run=server -f rendered.yaml -o yaml > admitted.yaml
```

`helm template` preukazuje client-side render pre dané inputs. Nepreukazuje cluster defaults, admission mutations ani authorization. Server-side dry-run preukazuje, že API server prijme object a ukáže admission result v čase requestu. Nepreukazuje, že controller vytvorí healthy runtime ani že live apply bude používať rovnakú external dependency generation.

Pred promotion sa porovná intended image digest a admitted workload:

```bash
yq -e '
  .spec.template.spec.containers[] |
  select(.name == "api") |
  .image == "registry.prod.example/payments-api@sha256:pay1000api"
' admitted.yaml
```

Tento check overuje jednu field hodnotu v admitted manifeste. Neoveruje mutáciu init containers, environment variables, volumes ani policy fields, ktoré môžu zmeniť behavior. Critical field inventory má byť explicitný.

## 7. Deployment automation ako state machine

Delivery-ready deployment pozná current state, desired state, partial completion a unknown outcome. Nesmie predpokladať, že jeden successful CLI exit code znamená dokončený release.

```text
preflight a environment lock
→ artifact/config/policy verification
→ migration expand phase
→ workload desired-state mutation
→ controller convergence
→ eligibility a traffic verification
→ functional/business canary
→ completed, paused alebo failed verdict
→ recovery action
→ cleanup a old-generation retirement
```

Idempotency závisí od operácie. Opakované declarative apply môže byť bezpečné, ale opakovanie external payment requestu alebo non-transactional migration nie. Automation musí rozlíšiť „request sa nevykonal“ od „vykonal sa a response sa stratila“.

## 8. Read-back po deployment-e

Po apply Atlas nečíta iba deployment command output. Overí desired, controller a runtime generation:

```bash
kubectl -n payments rollout status deployment/payments-api --timeout=10m
kubectl -n payments get deployment payments-api \
  -o jsonpath='{.metadata.generation}{" "}{.status.observedGeneration}{"\n"}'
kubectl -n payments get pods -l app=payments-api \
  -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.status.containerStatuses[0].imageID}{"\n"}{end}'
```

Rovnosť `generation` a `observedGeneration` preukazuje, že controller spracoval latest Deployment spec. `rollout status` preukazuje controller rollout condition. `imageID` preukazuje runtime-resolved image pre konkrétny container. Ani tieto outputy nepreukazujú loaded application configuration, database contract ani settlement outcome. Preto nasleduje capability canary.

```bash
curl --fail-with-body \
  -H 'Idempotency-Key: delivery-rc4-canary-001' \
  -H 'X-Test-Tenant: atlas-canary' \
  https://staging.atlas.example/api/settlements/canary
```

HTTP success preukazuje iba response contract daného requestu. Business acceptance musí korelovať authoritative settlement state, outbox event, provider sandbox record a absence duplicate effectu.

## 9. Promotion gate a evidence expiry

Promotion rozhodnutie má vstupy, policy a output. Manuálny approval je legitimate, ak posudzuje residual risk nad pripraveným candidate-om. Nie je legitimate, ak schvaľovateľ ručne rozhoduje, ktoré commands spustiť alebo ktoré artifacty vybrať.

Promotion record obsahuje release subject, target environment generation, complete evidence inventory, findings/exceptions, actor identity a recovery reference. Evidence môže expirovať pri zmene target clusteru, policy bundle-u, dependency endpointu alebo shared-state contractu.

```text
candidate evidence complete
+ target generation stále zodpovedá evidence
+ exceptions sú platné a scoped
+ recovery eligibility je potvrdená
→ promotable
```

Mutable label `approved` bez týchto väzieb je iba annotation.

## 10. Delivery versus Deployment

Continuous Delivery garantuje, že candidate možno bezpečne nasadiť. Continuous Deployment navyše automaticky vykoná produkčný transition, keď policy a evidence dovolia. Rozdiel nie je v kvalite build-u ani v počte testov. Je v automatizácii posledného production release decisionu.

Organizácia môže mať Continuous Delivery a manuálne business timing rozhodnutie. Ak však produkčný deploy vyžaduje ručný shell postup, rebuild alebo ručné DB kroky, nejde o Continuous Delivery bez ohľadu na existenciu pipeline.

## 11. Connected incident `REL-PAY-66`

Atlas pipeline prevzala CI label `green`, rebuildla image s tagom `10.0-rc4` a staging nasadila digest `sha256:pay1000a`. Po staging validácii base image tag a dependency mirror zmenili obsah. Production rebuild vytvoril `sha256:pay1000b`, no approval UI stále zobrazovalo rovnaký release ID a staré staging evidence.

Súčasne production environment prešlo na novú admission policy, ktorá pridala sidecar s outbound proxy. Application Pods boli Ready, ale provider TLS path používal inú truststore. Deployment dashboard označil release za successful; settlement completion rate klesla o 38 %.

```text
staging artifact A + evidence E(A, env42)
→ mutable release tag
→ production rebuild B
→ changed environment generation env43
→ approval reused E
→ rollout green
→ business failure
```

Root cause bol false deployability subject. Artifact bytes, environment generation a evidence boli oddelené, no promotion ich prezentovala ako jeden release.

## 12. Recovery a acceptance

Containment zastaví ďalšie promotions, zafixuje traffic na last-known-good cohort a zachová release manifest, admission render, image IDs a canary evidence. Recovery nepoužije starý tag; vyberie exact compatible digest, obnoví truststore/policy generation alebo vykoná nový candidate so všetkými evidence.

Delivery je prijatá iba vtedy, keď:

```text
CI candidate má immutable artifact manifest
+ staging a production používajú ten istý intended digest
+ rendered/admitted/live/runtime generations sú korelované
+ shared-state compatibility je explicitná
+ promotion evidence patrí target generation
+ deployment zvládne partial a unknown outcome
+ business canary overí authoritative effect
+ rollback/roll-forward preconditions sú testované
+ forbidden rebuild počas promotion je odmietnutý
+ second promotion používa rovnaký mechanizmus bez ručného kroku
```

## 13. Troubleshooting flow

Pri symptóme „release bol deployable, ale produkcia zlyhala“ mapuj chain:

```text
release manifest
→ artifact digest a attestations
→ evidence subject
→ target environment/config generation
→ rendered a admitted state
→ deployment mutation
→ controller convergence
→ runtime image/config/dependency state
→ business outcome
```

Competing hypotheses môžu byť wrong digest, expired evidence, stale overlay, admission mutation, secret generation mismatch, incompatible schema, environment drift, partial migration alebo incomplete canary. Evidence-preserving containment má zachovať všetky generations pred rollbackom alebo re-apply.

## 14. Anti-patterny

### Rebuild per environment

Každý rebuild vytvára nový artifact a ruší väzbu na predchádzajúce evidence.

### Staging ako ceremoniálny krok

Environment bez definovanej risk otázky a relevantnej fidelity iba predlžuje lead time.

### Approval nad release názvom

Schválenie musí vidieť digest, target generation, evidence, exceptions a recovery; názov alebo tag nestačí.

### Rollout success ako business acceptance

Controller health nepreukazuje loaded configuration, dependency outcome ani správny settlement effect.

### Runbook-only production deploy

Ak bezpečný release závisí od neopakovateľných human steps, deployability nie je continuous.

## 15. Kontrolné otázky

1. Prečo immutable image samostatne nie je deployable candidate?
2. Čo tvorí exact delivery subject?
3. Čo preukazuje digest equality pri registry copy a čo nie?
4. Kedy environment change invaliduje evidence?
5. Aký je rozdiel medzi renderom, admission outputom a runtime state-om?
6. Prečo successful apply nie je deployment completion?
7. Aký dôkaz pridáva production canary?
8. Kedy je manuálny approval kompatibilný s Continuous Delivery?
9. Prečo rebuild v production zrušil validity staging evidence v `REL-PAY-66`?
10. Ako sa overí forbidden rebuild path?
11. Čo musí obsahovať recovery eligibility?
12. Ako sa odlišuje Continuous Delivery od Continuous Deployment?

## Glossary impact

Relevantné pojmy: deployability contract, release candidate manifest, environment subject, risk-specific fidelity, artifact promotion, evidence expiry, rendered state, admitted state, observedGeneration, runtime imageID, capability canary, promotable verdict, unknown deployment outcome a build-once-promote-many.

## Primárne zdroje

- [Continuous Delivery](https://continuousdelivery.com/)
- [SLSA specification](https://slsa.dev/spec/)
- [Sigstore Cosign documentation](https://docs.sigstore.dev/cosign/)
- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)
- [Helm documentation — helm template](https://helm.sh/docs/helm/helm_template/)
- [Kubernetes documentation — Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes documentation — Server-Side Apply](https://kubernetes.io/docs/reference/using-api/server-side-apply/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Continuous Integration](continuous-integration.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Continuous Deployment →](continuous-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
