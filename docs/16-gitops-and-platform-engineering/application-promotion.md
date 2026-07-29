# Application promotion

Application promotion je riadený prechod jednej presne identifikovanej release generation do ďalšieho environment authority boundary. Neznamená to iba spustiť rovnaký deployment job s parametrom `production`. Promotion rozhoduje, či immutable application artifact a jeho compatible configuration/dependency contract získali dostatočný dôkaz a oprávnenie stať sa desired state-om konkrétneho target environmentu.

Kľúčový rozdiel je medzi vytvorením candidate-u a jeho povolením pre environment. CI môže zostaviť artifact `sha256:pay910a`, podpísať ho a otestovať. Production však nezačne používať tento digest preto, že artifact existuje. Potrebuje authoritative promotion transition, ktorú GitOps controller následne pozoruje a reconcile-ne.

## 1. Dominantný model

```text
source change a immutable build
→ exact release candidate identity
→ candidate evidence a compatibility envelope
→ environment-specific eligibility evaluation
→ fresh promotion proposal
→ policy, review a approval decision
→ authoritative environment desired-state transition
→ target GitOps reconciliation
→ technical, workload a business verification
→ promotion record, recovery a next-environment closure
```

Promotion acceptance verdict musí dokazovať identity continuity. Artifact, ktorý prešiel testami, musí byť ten istý artifact, ktorý je uvedený v production desired state-e a ktorý workload skutočne vykonáva. Ak sa medzi staging testom a production deploymentom zmení image digest, chart dependency, feature flag, schema contract, secret generation alebo route policy, nejde o promotion overenej generation, ale o iný release subject.

## 2. Deploy, promote, release a expose

Tieto transitions spolu súvisia, ale nie sú synonymá.

### Build

Build transformuje source a pinned dependencies na immutable artifact:

```text
source commit + build definition + dependencies
→ artifact digest + provenance + test evidence
```

### Deploy

Deployment mení desired alebo live state environmentu tak, aby sa artifact alebo configuration pokúsili bežať v targete. Deployment môže byť opakovaný pre tú istú generation a nemusí meniť jej promotion status.

### Promote

Promotion mení authority: candidate získava oprávnenie byť desired generation v konkrétnom environment-e. V GitOps modeli je promotion často commit alebo pull request, ktorý zmení environment manifest z digestu A na digest B.

### Release

Release je širší product/operational state. Môže obsahovať artifact, dokumentáciu, support policy, rollout plan, migration, feature flags a rollback contract. Release môže existovať pred production exposure.

### Expose

Exposure mení, kto a aký traffic alebo capability skutočne používa. Canary, ring alebo feature flag môže držať production artifact nasadený, ale ešte nie plne exposed.

Preto:

```text
promoted
≠ successfully deployed
≠ healthy
≠ fully exposed
≠ business accepted
```

## 3. Exact promotion subject

Promotion subject musí obsahovať viac než image tag:

- application/release identity — service, version, source commit a build run;
- immutable artifact coordinates — image, chart, package, SBOM a provenance digest;
- environment source identity — repository, path, current commit a target ref;
- configuration generation — values, overlays, routes, flags a resource policy;
- schema/data compatibility envelope — supported database, event a API versions;
- secret/reference contract — required names, versions, leases alebo credential generations bez plaintextu;
- platform dependencies — CRDs, operators, runtime, policies a shared services;
- candidate evidence — tests, scans, signatures, staging outcome a operational checks;
- target environment identity — account, cluster, namespace, region, tenant a exposure scope;
- approval subject a freshness — kto schválil čo, na základe ktorého evidence snapshotu a dokedy;
- reconciliation a acceptance evidence — resolved desired generation, live workload generation a business result.

Promotion request `payments 9.1 to prod` je neúplný, ak nie je jasné, či ide o digest `pay910a` alebo neskorší `pay910b`, ktorú route-policy generation vyžaduje a či production schema podporuje jeho write behavior.

## 4. Build once, promote the same artifact

Silný promotion model vytvára artifact raz a medzi environmentmi presúva jeho authority, nie jeho bytes.

```text
build artifact D
→ verify D in CI
→ deploy D to integration
→ promote D to staging
→ verify D in staging
→ promote D to production
```

Rebuild per environment porušuje identity continuity:

```text
same source tag
→ staging build digest Ds
→ production build digest Dp
```

Aj keď source commit vyzerá rovnako, build môže závisieť od mutable base image, package repository, clocku, architecture, compiler version alebo environment variables. Staging evidence nad `Ds` potom nie je dôkazom pre `Dp`.

Build once neznamená, že configuration musí byť identická. Environmenty prirodzene používajú iné endpoints, capacities, credentials a exposure. Musí však byť explicitné, čo je invariant artifact a čo je environment-specific desired state.

## 5. Candidate identity a evidence bundle

Candidate evidence nie je iba zelená pipeline. Potrebuje identity binding:

```text
candidate digest
+ source/provenance
+ test subject
+ result
+ environment/fidelity
+ timestamp
+ policy version
→ reusable promotion evidence
```

Evidence bez subject bindingu môže byť stale alebo patriť inému artifactu. Napríklad security scan nad tagom `payments:9.1` nemusí patriť digestu, ktorý tag ukazuje pri promotion. Contract test nad mock providerom nepreukazuje production provider compatibility. Staging canary nad route generation `1850` nepreukazuje candidate pri route `1849`.

Evidence bundle môže obsahovať:

- build provenance a artifact signature;
- SBOM a vulnerability decision;
- unit, integration, contract, component a E2E results;
- migration compatibility a rollback eligibility;
- staging reconciliation revision a exact running digests;
- load/capacity evidence pri relevantnej configuration;
- operational readiness a monitoring coverage;
- business canary result;
- unresolved exceptions, expiry a ownera.

Nie každý environment potrebuje zopakovať každý test. Promotion policy rozhoduje, ktorý dôkaz je reusable a ktorý musí byť znovu získaný v target-specific context-e.

## 6. Environment authority model

Environment desired state môže byť organizovaný viacerými spôsobmi:

### Environment directories na jednej branch

```text
clusters/staging/payments
clusters/production/payments
```

Promotion je commit alebo PR kopírujúci exact candidate coordinate medzi paths. Výhodou je jednoduchý cross-environment diff. Rizikom je shared repository write scope a accidental multi-environment change v jednom PR.

### Environment branches

```text
refs/heads/staging
refs/heads/production
```

Promotion je merge alebo controlled ref transition. Rizikom sú long-lived divergence, merge conflicts, force push a nejednoznačnosť pri tom, ktoré commits boli skutočne promoted.

### Repository per environment

Promotion kopíruje release manifest medzi repositories. Zlepšuje access isolation, ale sťažuje atomic visibility a vytvára cross-repository provenance graph.

### Immutable release manifests

Environment ref odkazuje na signed manifest obsahujúci všetky artifact a config coordinates. Tento model zlepšuje reproducibility, ale vyžaduje tooling na generation, validation, retention a human-readable diff.

Layout nie je sám o sebe promotion control. Authority vzniká kombináciou protected write pathu, policy, approvals, immutable coordinates a controller target bindingu.

## 7. Pull request ako promotion transaction

Promotion PR môže fungovať ako decision boundary:

```text
current production desired generation
+ proposed candidate generation
+ rendered/effective delta
+ evidence bundle
+ policy result
+ reviewers
→ merge alebo reject
```

PR musí ukázať viac než zmenu `tag: 9.0 → 9.1`. Review potrebuje:

- digest a provenance identity;
- environment-specific rendered delta;
- resource, policy, route a secret-reference changes;
- migration a compatibility implications;
- exposure/rollback plan;
- evidence freshness;
- current target base revision.

PR approval je optimistic decision nad base state-om. Ak target branch alebo candidate evidence pokročia, approval môže byť stale. Merge queue alebo revalidation musí znovu overiť policy nad final merge commitom.

## 8. Stale promotion race

Typický race:

```text
T1 staging generation A prejde
T2 promotion proposal A vznikne
T3 staging alebo shared base sa zmení na B
T4 reviewer schváli starý proposal
T5 merge vyrenderuje A + časť B
```

Promotion musí používať compare-and-swap-like preconditions:

- expected source environment commit;
- expected candidate digest;
- expected target environment base commit;
- expected policy/evidence versions;
- no unreviewed transitive dependency change;
- re-render final merge result.

Ak precondition neplatí, promotion sa má znovu vyhodnotiť, nie automaticky „rebase and merge“.

## 9. Configuration promotion

Artifact promotion a configuration promotion môžu mať odlišnú cadence. Production môže používať ten istý digest ako staging, ale iné replicas, endpointy alebo feature flags.

Konfiguráciu treba rozdeliť:

### Invariant release contract

Fields, ktoré musia zostať spojené s artifactom:

- schema/event compatibility version;
- required API capabilities;
- route-policy minimum;
- secret key names a formats;
- migration generation;
- feature-code compatibility.

### Environment-owned configuration

Fields legitímne odlišné podľa targetu:

- replicas a resource sizing;
- regional endpoints;
- tenant IDs;
- exposure percentage;
- alert thresholds;
- environment-specific secret references.

### Runtime-owned state

Fields, ktoré nemá promotion prepisovať:

- controller status;
- HPA current replicas;
- dynamic leases;
- queue offsets;
- provider operation outcomes.

Chybný overlay môže prepísať invariant field ako environment detail. Promotion validation preto potrebuje schema a policy určujúcu, ktoré fields smú byť overridden.

## 10. Dependency graph promotion

Application generation je často graph:

```text
image digest
+ Helm chart version
+ environment values commit
+ policy bundle digest
+ database schema capability
+ event consumer compatibility
+ secret reference generation
→ effective release
```

Promotion jedného node-u bez graph compatibility môže zlyhať. Napríklad nový producer začne emitovať event v3, ale production consumer podporuje iba v2. Image je healthy, no system contract je poškodený.

Promotion record má identifikovať všetky decision-critical nodes. Nemusí pinovať volatile runtime status, ale musí pinovať alebo policy-bound resolve-nuť všetko, čo mení intended behavior.

## 11. Database a stateful compatibility

Stateful promotion je asymetrická. Artifact rollback nemusí obnoviť schema alebo data state.

Bezpečný model:

```text
expand schema
→ old aj new application compatible
→ promote new writer/readers
→ bounded backfill
→ verify old consumer absence
→ contract cleanup
```

Promotion gate musí vedieť:

- ktoré application versions čítajú a zapisujú ktoré schema variants;
- či migration je online, blocking alebo destructive;
- či rollback old artifactu zostáva compatible;
- či background jobs alebo event consumers zaostávajú;
- či regiony/rings používajú mixed versions;
- ako sa opraví partial alebo unknown migration outcome.

„Staging migration prešla“ nie je dostatočné, ak production dataset, lock duration alebo hidden consumers sú iné.

## 12. Promotion cez automation

Automation môže pripraviť alebo vykonať promotion. Rozlišujme:

### Candidate discovery automation

Pozoruje registry a navrhne nový digest.

### Proposal automation

Vytvorí branch alebo PR s exact delta a evidence links.

### Approval automation

Policy engine schváli low-risk update podľa explicitných pravidiel.

### Merge automation

Po splnení required checks zmení authoritative environment source.

### Reconciliation automation

GitOps controller aplikuje merged desired state.

### Exposure automation

Progressive-delivery controller zvyšuje traffic podľa runtime evidence.

Spojenie všetkých krokov do jedného bota môže byť efektívne, ale znižuje separáciu authority a komplikuje containment. Každý transition potrebuje operation identity a audit.

## 13. Promotion graph a concurrency

Nie každá organizácia má lineárny tok dev → staging → production. Môže existovať:

```text
integration
├── regional staging EU
├── regional staging US
└── performance
     ↓
production ring 0
→ ring 1
→ ring 2
```

Promotion graph určuje:

- predecessor evidence requirements;
- parallel branches;
- merge/join podmienky;
- environment-specific blockers;
- expiry dôkazu;
- rollback propagation;
- whether a later environment may skip predecessor.

Dve concurrent promotions do rovnakého targetu môžu vytvoriť lost update. Promotion service potrebuje serialization, merge queue alebo semantic conflict detection nad effective desired-state graphom.

## 14. Approval a separation of duties

Approval nie je dekoratívny checkbox. Má autorizovať presný risk-bearing transition.

Dobrý approval record obsahuje:

```text
actor identity
+ role/authority
+ exact candidate and target
+ rendered delta
+ evidence snapshot
+ policy version
+ decision and timestamp
+ expiry/revocation
```

Separation of duties môže vyžadovať, aby author candidate-u nebol jediný production approver. Pri low-risk automatizovaných patch updates môže policy nahradiť human approval, ak je risk model explicitný a existuje bounded rollback.

Broad rule „two approvals“ môže vytvoriť approval theater, ak revieweri nevidia artifact identity, transitive changes ani target outcome.

## 15. Promotion status a ledger

Promotion je distributed workflow. Stav môže byť:

```text
Proposed
→ Validating
→ Approved
→ Authoritative
→ Reconciling
→ Technically Ready
→ Business Accepted
```

Failure alebo recovery states:

```text
Rejected
Stale
Blocked
Failed
Partially Applied
Unknown
Rolled Back
Rolled Forward
Superseded
```

Git commit history zaznamenáva desired-state mutation, ale nemusí obsahovať všetky workflow states, evidence, target operation IDs a business outcome. Promotion ledger má korelovať Git, controller a runtime evidence bez toho, aby sa stal druhým desired-state writerom.

## 16. Unknown outcome

Promotion automation môže timeoutnúť po merge requeste alebo Git pushi. Timeout neznamená, že mutation nenastala.

```text
request sent
→ response lost
→ outcome unknown
```

Blind retry môže vytvoriť duplicate PR, duplicate commit, druhý exposure operation alebo conflicting rollback. Recovery:

```text
stable promotion operation ID
→ read authoritative Git/ref state
→ read controller observed revision
→ classify applied/not applied/partial/unknown
→ resume alebo compensate
```

Idempotency key musí identifikovať semantic promotion subject, nie iba HTTP request.

## 17. Rollback, roll-forward a supersession

Rollback v GitOps modeli je nový desired-state transition. Musí rozhodnúť, ktoré vrstvy možno vrátiť:

- application artifact;
- configuration;
- route/exposure;
- feature flags;
- schema;
- secret generation;
- provider registration;
- data side effects.

Ak schema alebo provider contract už nie je backward-compatible, artifact rollback môže zhoršiť incident. Roll-forward na opravený digest alebo compensation môže byť bezpečnejší.

Supersession nastáva, keď candidate B nahradí pending candidate A. Systém musí zastaviť alebo označiť A ako stale; inak neskorý merge A môže prebiť B.

## 18. Promotion observability

Evidence musí spájať transition od candidate-u po business outcome:

| Observation point | Required identity | Otázka |
|---|---|---|
| Build | source commit, build run, artifact digest | Čo bolo vytvorené? |
| Candidate registry | digest, signature, SBOM | Je artifact immutable a trusted? |
| Evidence store | subject digest, test/policy version | Čo bolo nad týmto subjectom preukázané? |
| Promotion PR | source/target commits, rendered delta | Čo sa navrhuje zmeniť? |
| Git merge | final environment commit | Kedy sa proposal stal authoritative? |
| GitOps controller | resolved revision, operation | Čo controller skutočne reconcile-ol? |
| Kubernetes/runtime | Pods, loaded generations | Čo reálne vykonáva workload? |
| Business canary | release cohort, operation IDs | Poskytuje release správny outcome? |

Dashboard, ktorý zobrazuje iba `production = 9.1`, zahadzuje identity a intermediate states potrebné pri incidente.

## 19. Connected incident `GITOPS-PAY-62`

Intended promotion:

```text
pay910a staging artifact
→ route 1850 + credential contract pv-42
→ staging canary evidence E-778
→ production proposal P-441
→ exact digest/config copy
→ Flux reconciliation
→ production canary
```

Promotion service však vytvorila proposal z troch independently mutable inputs:

```text
staging path at commit S1
+ shared base branch main
+ cluster-local LaunchPad substitution ConfigMap
```

Kým proposal čakal na approval:

- image automation zmenila shared base z `pay910a` na `pay910b`;
- LaunchPad zmenil route substitution z `1850` na `1849`;
- staging evidence `E-778` zostala viazaná na `pay910a/1850`;
- merge automation rebase-la PR bez re-renderu a revalidácie;
- production commit preto neidentifikoval skutočný effective configuration graph.

Promotion UI tvrdilo:

```text
candidate: pay910a
staging: passed
production: approved
```

Controller a runtime vykonali:

```text
source artifact: b71f203
image:           pay910b
route:           1849
secret object:   pv-42
provider active: pv-43 po rotation
```

### Promotion root cause

Promotion decision nebola compare-and-swap transition nad immutable candidate a target base state-om. Approval zostal platný po zmene transitive shared base-u a hidden substitution inputu. Promotion record preto autorizoval subject A, ale merge a Flux vyrenderovali subject B.

### Redesign

```text
candidate release manifest R-910a
→ pins image/chart/policy/schema/secret-reference contract
→ staging desired state references R-910a
→ staging evidence bound to R-910a + environment revision
→ production PR changes only release-manifest reference
→ final-merge render and policy revalidation
→ target base CAS
→ merge creates authoritative production generation
→ Flux observed revision
→ exact runtime generation endpoint
→ business canary
→ promotion ledger Accepted
```

Promotion service už nesmie označiť operation completed pri vytvorení alebo merge PR-u. Completion znamená target-specific acceptance alebo explicitný failed/unknown state.

## 20. Promotion acceptance verdict

Application promotion design je prijatý, keď:

- candidate je immutable a jednoznačne identifikovaný;
- ten istý artifact prechádza environmentmi bez uncontrolled rebuild-u;
- artifact invariants a environment-owned configuration sú oddelené;
- evidence je subject-bound, target-relevant, fresh a policy-versioned;
- promotion proposal identifikuje source a target base revisions;
- final merge result sa znovu renderuje a validuje;
- approvals autorizujú exact delta a po zmene subjectu sa invalidujú;
- transitive dependencies, schema, events, secrets a policies sú v compatibility graph-e;
- concurrent promotions sú serialized alebo semantic-conflict checked;
- automation identities a scopes sú explicitné;
- authoritative environment transition je oddelená od controller reconciliation;
- deployment, health, exposure a business acceptance majú samostatné states;
- unknown outcome recovery používa operation identity a read-back;
- rollback/roll-forward rozhoduje per layer a rešpektuje stateful compatibility;
- stale proposal, mutable tag, rebuild drift, hidden config, lost update, duplicate promotion a false-success tests prejdú;
- second promotion po failed/rolled-back candidate nezdedí stale evidence alebo locks.

## 21. Troubleshooting flow

```text
Production nebeží na tom, čo prešlo stagingom
→ exact release/promotion operation subject
→ candidate digest + provenance
→ staging environment revision + running generation
→ evidence subject/freshness
→ promotion proposal source/target base commits
→ transitive dependency/render delta
→ final merge commit
→ GitOps resolved revision
→ live workload/config/secret/schema generations
→ exposure a business cohort
→ stale/race/override writer identification
→ authoritative repair + second promotion
```

## 22. Anti-patterny

### Buildneme to znovu pre production

Nový build je nový artifact. Staging evidence sa naň automaticky neprenáša.

### Tag `9.1` je promotion subject

Tag môže byť mutable a neidentifikuje chart, config, schema ani policy graph.

### Merge PR znamená successful promotion

Merge iba mení authoritative desired state. Reconciliation, runtime a business acceptance ešte môžu zlyhať.

### Staging bolo zelené, approval zostáva platný

Iba ak candidate, dependencies, staging evidence a target base zostali nezmenené podľa explicitných freshness rules.

### Skopírujeme celý staging overlay do production

Tým sa môžu preniesť environment-specific endpoints, credentials, capacities alebo unsafe debug controls. Promotion má kopírovať release contract, nie slepo celý environment.

### Dve production PR sa nejako merge-nú

Bez serialization alebo semantic conflict detection môže neskorší proposal prepísať skorší alebo zložiť netestovanú combination.

### Rollback je zmena image digestu späť

Nie pri schema, secret, route, flag alebo external side-effect changes. Recovery musí posúdiť celý state delta.

## 23. Kontrolné otázky

1. Ako sa promotion líši od deploymentu, release-u a exposure?
2. Čo tvorí exact application promotion subject?
3. Prečo build once chráni identity continuity?
4. Ktoré configuration fields sú artifact invariants a ktoré environment-owned?
5. Ako sa evidence viaže na immutable candidate?
6. Prečo approval môže po rebase alebo shared-base change-u zostarnúť?
7. Ako compare-and-swap precondition chráni promotion?
8. Aké riziká majú environment directories, branches a separate repositories?
9. Ako sa promotuje compatibility graph, nie iba image?
10. Prečo stateful migration mení rollback eligibility?
11. Kedy môže automation bezpečne schvaľovať production promotion?
12. Aké states potrebuje promotion ledger?
13. Ako sa rieši unknown Git push alebo merge outcome?
14. Prečo `GITOPS-PAY-62` autorizoval inú generation než Flux vykonal?
15. Čo musí final-merge revalidation skontrolovať?
16. Ako overíš second promotion po stale alebo superseded proposal-e?

## Glossary impact

Relevantné pojmy: application promotion, promotion subject, release candidate identity, build-once promotion, artifact invariant, environment-owned configuration, candidate evidence bundle, promotion authority, promotion proposal, promotion freshness, stale promotion, promotion compare-and-swap, environment desired-state transition, dependency promotion graph, promotion ledger, superseded promotion, promotion unknown outcome a promotion acceptance verdict.

## Primárne zdroje

- [OpenGitOps — Principles](https://opengitops.dev/)
- [Flux — Repository Structure](https://fluxcd.io/flux/guides/repository-structure/)
- [Flux — Image Update Automation](https://fluxcd.io/flux/guides/image-update/)
- [Flux — ImageUpdateAutomation API](https://fluxcd.io/flux/components/image/imageupdateautomations/)
- [Argo CD — Tracking and Deployment Strategies](https://argo-cd.readthedocs.io/en/stable/user-guide/tracking_strategies/)
- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [SLSA — Provenance](https://slsa.dev/spec/v1.1/provenance)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Flux](flux.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: GitOps secrets →](gitops-secrets.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
