# Helm testing a troubleshooting

Helm testing nemá dokazovať iba to, že chart sa dá vyrenderovať alebo nainštalovať. Má vytvoriť dôkaz, že konkrétny immutable release subject prešiel od source artifactu cez render, API a Kubernetes reconciliation až po očakávaný runtime a business outcome.

Troubleshooting používa rovnaký model opačným smerom. Začína symptómom, identifikuje presný release/render/live/runtime subject a hľadá prvú boundary, kde sa očakávaný stav odlišuje od pozorovaného.

## 1. Dominantný evidence lifecycle

```text
release risk a acceptance contract
→ immutable test subject
→ expected evidence inventory
→ chart/dependency/values validation
→ deterministic render a semantic assertions
→ API/admission/policy validation
→ install/upgrade/rollback/uninstall execution
→ Kubernetes reconciliation evidence
→ Helm test a application synthetics
→ business acceptance
→ incident subject a competing hypotheses
→ discriminating observation
→ containment a recovery
→ regression control a closure
```

Jedna zelená vrstva nepreukazuje nasledujúcu:

```text
lint success
≠ valid render pre production values
≠ API acceptance
≠ controller convergence
≠ správny serving cohort
≠ process-loaded configuration
≠ business correctness
```

## 2. Atlas test subject

Pre ďalší Atlas Payments release používame:

```text
release: payments-prod
source revision: 22
target revision: 23
chart artifact: CH59
dependency lock: D59
values bundle: V59
rendered manifest: M59
image digest: I59
credential target epoch: SE10
cluster generation: K136
```

Test subject musí obsahovať aj:

```text
Helm version a deployment engine
target context a namespace
expected resource inventory
expected hooks a operation IDs
expected image/config/credential generations
expected technical, security a business outcomes
```

Bez immutable subjectu sa výsledky `helm lint`, ephemeral installu a production `helm test` nemusia týkať rovnakého artifactu.

## 3. Expected evidence inventory

Pred vykonaním testov definuj, ktoré dôkazy musia vzniknúť:

```text
chart metadata a artifact digest
dependency lock/digests
effective values digest
rendered manifest digest
schema a helper assertions
server/admission verdict
release revision/status
hook operation results
live object UIDs/generations
Pod image a process-loaded config/credential epochs
EndpointSlice serving cohort
application synthetic result
business ledger/result
forbidden-outcome tests
```

Green pipeline bez očakávaného reportu alebo bez väzby na promoted artifact nie je complete evidence.

## 4. Testovacia pyramída

```text
chart structure a metadata
→ dependency lock a supply chain
→ values schema a values matrix
→ template/helper unit tests
→ deterministic full render
→ YAML/Kubernetes schema
→ policy a security controls
→ server-side dry-run a admission
→ ephemeral cluster install
→ upgrade z supported previous revision
→ rollback/roll-forward/uninstall scenarios
→ helm test
→ workload/runtime acceptance
→ external business synthetic
```

Lacnejšie vrstvy majú rýchlo zachytiť chyby blízko source-u. Realistickejšie vrstvy overujú mechanizmy, ktoré local render nevie simulovať.

## 5. Chart artifact a dependency gate

Over:

```bash
helm show chart ./chart
helm dependency list ./chart
helm dependency build ./chart
helm lint ./chart
```

Dôkaz musí potvrdiť:

- expected chart name/version/type;
- exact `Chart.lock`;
- resolved first-level aj transitive dependencies;
- source registry/repository identity;
- packaged chart digest;
- žiadny unreviewed hook, CRD, RBAC alebo image reference;
- artifact použitý v ďalších testoch je rovnaký ako publikovaný artifact.

`helm dependency update` v test/release kroku môže zmeniť graph a vytvoriť iný subject než reviewovaný source.

## 6. Values schema a matrix

Chart netestuj iba s defaults.

Minimálna matrix:

```text
default values
production-like values
feature on/off
explicit false, 0, empty a null
subchart enabled/disabled
internal/external dependency mode
minimum/maximum replicas a resources
alternate ingress/gateway/service mode
supported Kubernetes/API variants
upgrade values z current production revision
```

Každý matrix case potrebuje očakávaný render verdict. Nestačí iba „render nezlyhal“.

Príklady assertions:

```text
feature=false → resource absent a process flag false
externalDatabase=true → internal DB subchart absent
serviceAccount.create=false → exact external SA reference
credentialEpoch=SE10 → Pod template generation sa zmení
```

## 7. Deterministic render gate

```bash
helm template payments-prod ./chart \
  -f values-production.yaml \
  --namespace production > rendered.yaml
```

Over:

- rovnaké inputs produkujú rovnaký manifest digest;
- žiadne neplánované `lookup`, `now` alebo random outputs;
- helper name/scope/output contracts;
- correct YAML typing;
- stable selectors a resource identities;
- image digests;
- expected hooks a lifecycle points;
- explicit configuration generations.

Pri `lookup` alebo cluster-dependent `Capabilities` local render nemusí byť representative. Test subject musí zaznamenať capabilities a identity server-connected renderu.

## 8. Template a helper assertions

Unit/golden testy sú vhodné pre fields s vysokým blast radiusom:

- resource names;
- selectors a Pod labels;
- Service ports/targetPorts;
- image references;
- ServiceAccount/RBAC;
- security context;
- hook annotation/weight/delete policy;
- rollout checksum/epoch annotations;
- dependency enablement;
- CRD/API version branching.

Snapshot test nie je semantic oracle. Review musí vysvetliť, prečo sa každý identity, selector, authority alebo data-bearing field zmenil.

## 9. YAML, API a admission boundaries

Local YAML parse:

```bash
helm template payments-prod ./chart -f values-production.yaml \
  | kubectl apply --dry-run=client -f -
```

Server-side validation:

```bash
helm template payments-prod ./chart -f values-production.yaml \
  | kubectl apply --dry-run=server -f -
```

Server môže odhaliť:

- nepodporovanú API version;
- OpenAPI/schema failure;
- admission mutation alebo denial;
- RBAC;
- ResourceQuota/LimitRange;
- Pod Security;
- CRD conversion;
- namespace-specific policy.

Dry-run stále nepreukazuje controller behavior, scheduling, volume attach, CNI, readiness ani business path.

## 10. Policy a security evidence

Rendered manifests analyzuj podľa versionovanej policy generation.

Kontroluj minimálne:

```text
privileged/host authority
runAs/seccomp/capabilities
RBAC a workload-create escalation
mutable images
plaintext Secret material
hook authority a external credentials
requests/limits
NetworkPolicy/PDB podľa platform contractu
cluster-scoped resources
untrusted dependencies a post-renderers
```

Policy verdict musí byť viazaný na manifest digest `M59`, nie iba na source directory.

## 11. Ephemeral cluster lifecycle test

```text
representative cluster bootstrap
→ required CRDs/controllers/policies
→ install target chart artifact
→ wait a runtime verification
→ helm test
→ application smoke
→ upgrade z current supported revision
→ failure injection alebo rollback/roll-forward
→ uninstall/decommission checks
→ evidence export a cleanup
```

Ephemeral cluster má zodpovedať production v relevantných boundaries:

- Kubernetes minor/API versions;
- admission a Pod Security;
- CNI/CSI/DNS assumptions;
- default StorageClass;
- LimitRange/Quota;
- external integration stubs alebo test identities.

## 12. Upgrade path je samostatný test

Fresh install success nepreukazuje upgrade.

Upgrade test musí začať zo supported previous production-like state-u:

```text
revision 22 + data/config/credential generations
→ target revision 23
→ hooks a migrations
→ rollout
→ mixed-version compatibility
→ business acceptance
```

Testuj tiež:

- stored legacy values;
- renamed/removed keys;
- immutable fields;
- retained PVC/data;
- old/new application overlap;
- pending/timeout recovery;
- rollback eligibility;
- external side effects.

## 13. Helm test contract

Chart test sa spustí cez:

```bash
helm test payments-prod -n production --logs
```

Dobrý test hook má:

```text
exact release a expected generation
least-privilege identity
bounded deadline a resources
explicit exit status
read-only alebo idempotent operation
logs zachované pred cleanupom
original aj forbidden outcome
```

Môže overiť:

- Service DNS a request path;
- authentication;
- schema compatibility endpoint;
- read-only transaction;
- expected image/config/credential epoch;
- dependency reachability cez application path.

`helm test` je point-in-time evidence. Nie monitoring, load test ani complete multi-cohort validation.

## 14. Cohort a repeated-observation tests

Jeden úspešný request môže náhodne zasiahnuť zdravý backend.

Pre replicated workload over:

```text
všetky serving Pod UIDs
image digest každej repliky
process-loaded config/credential epoch
EndpointSlice targetRef cohort
repeated request distribution
zone/Node/failure-domain coverage
```

Test, ktorý nepozná cohort, môže byť green pri partial rollout-e alebo stale process state-e.

## 15. Release evidence

Pri incidente zachovaj:

```bash
helm status payments-prod -n production
helm history payments-prod -n production
helm get values payments-prod -n production --all
helm get manifest payments-prod -n production
helm get hooks payments-prod -n production
```

Release evidence odpovedá na:

```text
akú revision Helm pozná
aké values a manifest uložil
aký status zapísal
aké hooks vyrenderoval
```

Neodpovedá automaticky, ktorý process prijíma traffic ani či business operation prešla.

## 16. Troubleshooting domains

Začni podľa prvej boundary, kde sa symptom objaví:

```text
artifact/dependency fetch
values/schema
render/helper/YAML
API/admission
hook/external operation
release storage/concurrency
Kubernetes reconciliation/runtime
Service/network/storage
application/external dependency
business outcome
```

Neskáč priamo na Pod logs pri render failure a nemaž release Secrets pri runtime probléme.

## 17. Incident subject protocol

Pred hypotézami fixuj:

```text
cluster/context/namespace
release name a source/target/current revision
chart/dependency/values/manifest digests
live resource UIDs/generations
Pod/container/image identities
config/credential/data generations
request alebo transaction ID
timeline a recent change
```

Bez subject identity sa evidence z rôznych revisions alebo clusterov ľahko zmieša.

## 18. Worked incident — Helm aj test sú green, polovica requests má 401

Atlas Payments revision 23 mení external database credential z epoch SE09 na SE10.

Target intent:

```text
Secret provider reference → SE10
application credentialEpoch → SE10
provider overlap window → SE09 aj SE10 validné počas rollout-u
po acceptance → revoke SE09
```

Release sa nainštaluje. Helm status je `deployed`. `helm test` vykoná jeden request a prejde. Po revokácii SE09 však približne polovica production requests vracia `401` z database proxy.

### Exact subject

```text
release payments-prod revision 23
chart CH59 / lock D59 / values V59 / manifest M59
Secret object generation: SE10
four serving Pod UIDs: P59a, P59b, P59c, P59d
EndpointSlice cohort: všetky štyri Pody
request IDs s 200 a 401
provider accepted epochs po revokácii: iba SE10
```

### Konkurenčné hypotézy

1. target values stále odkazujú na SE09;
2. rendered manifest M59 obsahuje nesprávny provider reference;
3. external secret controller nepublikoval SE10;
4. Kubernetes Secret je current, ale projection je stale;
5. mounted file je current, ale process credential nere-loadol;
6. časť serving Podov patrí starej release cohort-e;
7. provider revokoval aj SE10 alebo používa iný tenant;
8. Service/EndpointSlice alebo network path smeruje na inú backend identity;
9. `helm test` trafil iba healthy cohortu.

### Diskriminačné observation points

```text
archived V59 a M59
live Secret resourceVersion a safe epoch metadata
per-Pod mounted-file fingerprint
per-process loaded credential epoch telemetry
Pod UID/image/restart inventory
EndpointSlice targetRef UIDs
provider authentication audit
repeated request → backend Pod correlation
```

Finding:

```text
V59 a M59 správne požadujú SE10
Secret object aj mounted files obsahujú SE10
P59a/P59b procesy reloadli SE10
P59c/P59d procesy stále používajú SE09
všetky štyri Pody sú Ready a serving
helm test trafil P59a
SE09 revocation spôsobuje 401 iba na stale process cohort-e
```

Root cause:

```text
chart zmenil external Secret reference
→ Pod template sa nezmenil
→ application reload bol best-effort
→ readiness neoverovala loaded credential epoch
→ single-request Helm test neoveril celú serving cohortu
→ provider revokoval SE09
```

### Containment

- pozastaviť ďalšiu credential automation;
- vyradiť P59c/P59d z trafficu alebo vykonať bounded restart;
- zachovať per-Pod epoch a provider audit evidence;
- nevracať chart ani Secret naslepo;
- ak security policy dovoľuje, použiť krátky kontrolovaný overlap SE09 iba počas drain-u.

### Recovery

1. pridať explicitný non-secret `credentialEpoch: SE10` do Pod template annotation;
2. vytvoriť novú Deployment generation;
3. rolloutovať Pods po bounded cohorts;
4. readiness overí process-loaded epoch SE10;
5. release test enumeruje všetky serving Pod UIDs alebo opakuje request s backend correlation;
6. po complete cohort acceptance revokovať SE09;
7. overiť provider audit aj business transactions.

### Verification

```text
každý serving Pod hlási SE10
EndpointSlice neobsahuje stale Pod UID
opakované synthetics prejdú cez všetky cohorts
SE09 authentication preukázateľne zlyhá
SE10 authentication prejde
payment P-884 má jednu úspešnú ledger transakciu
forbidden: žiadne 401 z credential epoch mismatch
```

### Earlier controls

- explicitný rollout epoch v values schema;
- process-loaded generation telemetry;
- readiness via local credential usability, nie shared dependency health;
- per-cohort chart test;
- staged credential overlap/revocation state machine;
- ephemeral upgrade test SE09 → SE10.

## 19. Failure boundaries

### Lint green, production matrix broken

Defaults sa vyrenderujú, ale `externalDatabase=true` s disabled subchartom vytvorí missing Service reference.

### Local render green, server denial

Representative admission policy odmietne broad hook RBAC alebo privileged security context.

### Ephemeral install green, upgrade broken

Fresh cluster nemá stored legacy values, old selectors, retained PVC ani mixed data generation.

### Helm status failed, rollout dokončí neskôr

Timeout ukončí klienta, Kubernetes controllers pokračujú. Retry bez live-state observation vytvorí nový transition nad zmeneným state-om.

### Helm test green, external route broken

Test beží cez ClusterIP a neoverí DNS/TLS/Gateway/edge path používateľa.

### Debug output leakne Secrets

`helm get all`, dry-run alebo CI artifact obsahuje rendered Secret/effective values. Evidence collection musí mať redaction a access boundary.

### Ručné zmazanie release Secretu

Odstráni alebo poškodí Helm state evidence bez opravy runtime root cause-u.

## 20. Recovery hierarchy

Preferované poradie:

```text
opraviť source/effective values a vyrenderovať novú revision
→ dokončiť alebo zopakovať idempotentný hook
→ roll-forward kompatibilnou opravou
→ rollback iba pri preukázanej eligibility
→ compensation external side effectu
→ restore iba pri skutočnej data/control-plane recovery potrebe
```

Každá recovery musí overiť pôvodný symptom a forbidden outcomes.

## 21. Chart CI pipeline

```text
source formatting a metadata
→ locked dependencies
→ values schema a matrix
→ helper/semantic assertions
→ deterministic render
→ YAML/API schema
→ policy/security
→ package immutable chart
→ ephemeral install
→ upgrade z supported previous revision
→ helm test a business synthetic
→ rollback/roll-forward/uninstall scenarios
→ publish/promotion rovnakého artifactu
```

Generated reports musia byť viazané na artifact digest a zachované podľa evidence policy.

## 22. Troubleshooting closure checklist

```text
[ ] exact release a runtime subject
[ ] scope, timeline a recent change
[ ] current, target a live-state comparison
[ ] competing hypotheses
[ ] discriminating observation point
[ ] volatile evidence preserved
[ ] containment bounded
[ ] authoritative source fixed
[ ] original outcome verified
[ ] forbidden outcome verified
[ ] adjacent cohorts/failure domains checked
[ ] second render/retry/reconcile is stable
[ ] regression test added at earliest reliable boundary
```

## 23. Kontrolné otázky

1. Čo tvorí immutable Helm test subject?
2. Prečo jedna zelená testovacia vrstva nepreukazuje nasledujúcu?
3. Ktoré cases musí obsahovať values matrix?
4. Prečo fresh install test nenahrádza upgrade test?
5. Čo `helm test` preukazuje a čo nie?
6. Ako odlíšiš release evidence od live/runtime evidence?
7. Prečo treba korelovať requests s backend Pod UID?
8. Aký je rozdiel medzi mounted a process-loaded credential generation?
9. Prečo ručné mazanie release Secrets nie je bežná recovery?
10. Ako sa incident finding premení na skorší regression control?

## Glossary impact

Relevantné pojmy: Helm evidence lifecycle, immutable chart test subject, expected Helm evidence inventory, values matrix oracle, deterministic render evidence, upgrade-path test, cohort-aware Helm test, release/runtime evidence boundary, Helm incident subject, symptom-to-release translation, Helm recovery hierarchy, forbidden outcome test a Helm troubleshooting closure.

## Oficiálna dokumentácia

- [helm lint](https://helm.sh/docs/helm/helm_lint/)
- [helm template](https://helm.sh/docs/helm/helm_template/)
- [helm test](https://helm.sh/docs/helm/helm_test/)
- [helm status](https://helm.sh/docs/helm/helm_status/)
- [Chart Tests](https://helm.sh/docs/topics/chart_tests/)
- [Debugging Templates](https://helm.sh/docs/chart_template_guide/debugging/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Upgrade a rollback](upgrade-rollback.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CKA timed labs →](cka-timed-labs.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
