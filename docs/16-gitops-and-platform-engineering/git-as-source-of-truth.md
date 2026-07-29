# Git ako source of truth

Git ako source of truth neznamená iba to, že v repozitári existujú YAML súbory. Znamená to, že presne definovaný, versionovaný a auditovateľný desired-state subject je jedinou autoritou pre zmenu riadených vlastností systému.

Git pritom nie je autoritou nad všetkým runtime state-om. Databázové records, controller status, ephemeral leases, metrics alebo skutočný provider outcome sú observed alebo operational state. Git má byť autoritou nad tým, čo má byť deklaratívne riadené a reprodukovateľné.

## 1. Dominantný model

```text
business alebo platform intent
→ exact desired-state subject a ownership boundary
→ declarative source + pinned inputs
→ validation, review a policy evidence
→ authoritative ref/commit transition
→ agent resolution a deterministic render
→ apply/reconcile do target environmentu
→ effective-state a business verification
→ drift, rollback a second-change closure
```

Source-of-truth verdict sa nerobí podľa existencie repozitára. Musí byť možné preukázať, ktorá immutable generation opisovala intended state, kto ju mohol zmeniť, ako ju controller vyrenderoval a ktoré runtime fields skutočne vlastnila.

## 2. Exact desired-state subject

GitOps desired-state subject obsahuje minimálne:

- repository identity a trust boundary;
- path, branch/tag/ref a resolved commit SHA;
- environment, cluster, namespace a application identity;
- manifest, Helm chart, Kustomize overlay alebo generator generation;
- image, chart, module a policy digests;
- values, parameters, overlays a external inputs;
- secret references a key/secret generation contract;
- field ownership a allowed runtime writers;
- validation, approval, signature a provenance evidence;
- controller, destination a reconciliation policy;
- rollback, retention a decommissioning contract.

Tvrdenie `production je v Git-e` je neúplné, ak nie je jasné, či production controller sleduje branch, tag alebo commit; či existujú parameter overrides; či image používa mutable tag; alebo či iný writer môže meniť rovnaké fields mimo Git-u.

## 3. Git authority a runtime truth

Treba rozlíšiť tri vrstvy:

```text
Git desired state
→ čo má byť podľa schválenej deklarácie

controller-resolved desired state
→ exact commit + render inputs + overrides + generated manifests

live/observed state
→ čo target API a runtime skutočne držia a vykonávajú
```

Git môže byť korektný a live state nesprávny pre:

- failed alebo partial reconciliation;
- stale controller cache;
- direct runtime mutation;
- mutating admission webhook;
- operator/controller-owned fields;
- missing secret alebo external dependency;
- wrong target cluster;
- health failure po úspešnom apply;
- business incompatibility.

Naopak live system môže dočasne fungovať, hoci Git neobsahuje reprodukovateľný desired state. To je operational debt, nie dôkaz správneho GitOps modelu.

## 4. Declarative desired state

Declarative source opisuje intended outcome, nie iba sekvenciu príkazov.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: settlement-api
spec:
  replicas: 24
  template:
    spec:
      containers:
        - name: settlement-api
          image: registry.example/settlement-api@sha256:pay900a
```

Deklarácia stále potrebuje mechanizmus, ktorý:

1. resolve-ne exact source generation;
2. porovná ju s live state-om;
3. vykoná bounded mutation;
4. overí convergenciu a health;
5. proces zopakuje po drift-e alebo ďalšej zmene.

Imperatívny skript môže byť súčasťou implementácie controllera alebo hooku, ale jeho intended effect musí byť reprezentovaný, identifikovaný a recoverable v desired-state contracte.

## 5. Versioned a immutable neznamená iba Git repository

Git commit object má immutable content identity, ale bežné refs sú mutable pointers:

```text
refs/heads/prod
→ commit A
→ neskôr commit B
```

Podobne tag možno retagovať, branch force-pushnúť a release manifest môže obsahovať mutable dependencies:

```yaml
image: registry.example/payments:latest
```

Aj keď manifest commit zostáva rovnaký, `latest` môže neskôr resolve-nuť na iný digest. Effective desired state preto nie je reprodukovateľný.

Versioned desired state vyžaduje:

- immutable commit identity;
- pinned artifacts a dependencies;
- retained history;
- chránené authoritative refs;
- zákaz alebo kontrolu force pushu a retaggingu;
- identifikáciu generator/toolchain generation;
- read-back toho, čo controller skutočne resolve-ol.

## 6. Authoritative ref a promotion

Commit môže existovať bez toho, aby bol schválený pre production. Autorita vzniká až explicitným promotion decisionom:

```text
candidate commit
→ tests a policy evidence
→ approval
→ production environment ref/manifest update
→ controller observation
→ rollout a verification
```

Možné modely:

- environment branch;
- environment directory na jednej branch;
- immutable release manifest odkazujúci na commit/digests;
- promotion PR medzi overlays;
- controller pinned na commit SHA;
- signed tag alebo release object, ak tag mutation policy je kontrolovaná.

Neexistuje univerzálne správny layout. Musí však byť zrejmé, ktorá transition je authoritative promotion a ako sa odlíši od obyčajného source commit-u.

## 7. Application source, environment source a generated source

Bežné repository boundaries:

### Application repository

Obsahuje source code, build definition a často base deployment metadata.

### Configuration alebo environment repository

Obsahuje environment-specific desired state, napríklad image digest, replicas, routes a policy references.

### Platform repository

Obsahuje shared controllers, cluster baseline, policies a platform capabilities.

Rozdelenie môže zlepšiť ownership, ale vytvára cross-repository generation graph:

```text
application digest
+ chart commit
+ environment values commit
+ policy bundle digest
+ secret reference generation
→ effective production manifests
```

Ak controller číta viac sources, acceptance evidence musí obsahovať všetky resolved revisions. Jeden Git SHA už nemusí identifikovať celý desired state.

## 8. Render boundary

Git často neobsahuje final Kubernetes objects. Obsahuje inputs pre Helm, Kustomize alebo plugin:

```text
repo URL
+ commit
+ path
+ values
+ chart dependencies
+ plugin image/config
→ rendered manifest set
```

Reproducibility vyžaduje:

- pinned chart/plugin/tool versions;
- deterministic inputs;
- no hidden environment variables;
- no uncontrolled network fetch;
- captured render errors;
- manifest count a object identity inventory;
- sensitive output handling;
- comparison controller renderu s CI validation renderom.

CI green nad inou Helm alebo Kustomize generation než používa controller nie je production render evidence.

## 9. Overrides mimo Git-u

Parameter override je druhý desired-state writer.

```text
Git values: image.digest = pay900a
Argo override: image.digest = pay899hf7
resolved desired state = pay899hf7
```

Ak override nie je uložený a reviewovaný rovnakým authority processom, Git už nie je úplný source of truth.

Inventory musí pokrývať:

- Argo CD parameter overrides;
- Helm release values uložené v clusteri;
- CLI flags;
- environment variables v controlleri alebo plugin-e;
- admission mutation;
- external secret injection;
- image policy automation;
- runtime feature flags;
- HPA alebo operator-owned fields.

Nie každý external input je zakázaný. Musí však mať explicitnú authority, version identity a merge/precedence contract.

## 10. Desired spec a observed status

Git typicky vlastní desired `spec`. Runtime controllers produkujú `status` a ďalšie observed fields.

```text
Git: desired replicas = 24
Deployment controller: availableReplicas = 22
```

Commitovať volatile status späť do desired source vytvára feedback loop a merge noise. Status patrí do telemetry alebo controller API, pokiaľ nie je zámerne transformovaný na nový schválený intent.

Princíp:

```text
observed state
→ evidence alebo proposal
→ explicitný decision
→ nový desired-state commit
```

Nie:

```text
observed field
→ automaticky prepíše authoritative intent bez policy
```

## 11. Writer a field ownership

GitOps systém musí inventarizovať writers nad každým critical fieldom:

```text
Deployment image
→ GitOps controller only

Deployment replicas
→ HPA podľa explicitného ownership contractu

Secret data
→ External Secrets controller

status
→ Kubernetes controller
```

Dvaja reconcilers môžu byť každý lokálne idempotentní a spolu vytvárať oscillation:

```text
GitOps nastaví replicas=24
→ HPA nastaví replicas=40
→ GitOps nastaví replicas=24
→ ...
```

Riešením nie je broad ignore všetkého. Riešením je presný field ownership, úzky diff policy a acceptance test oboch writerov.

## 12. Change governance

Source-of-truth repository potrebuje controls primerané jeho authority:

- protected branches alebo equivalent rule;
- required review a status checks;
- CODEOWNERS alebo explicitný owner graph;
- signed commits/tags tam, kde je to required assurance;
- policy-as-code nad manifests a resolved dependencies;
- secret scanning;
- provenance a immutable artifacts;
- auditable automation identity;
- break-glass path s expiry a reconciliation;
- retention a restore test repository history.

PR approval sám o sebe negarantuje bezpečný desired state. Review musí vidieť rendered/effective delta, target scope a risk.

## 13. Source of truth nie je source of every fact

Do Git-u typicky nepatrí:

- customer transactions;
- current database leader;
- ephemeral leases;
- queue offsets;
- controller status;
- runtime metrics;
- unencrypted plaintext secrets;
- provider operation outcome;
- rapidly changing autoscaling observation.

Git môže obsahovať policy a configuration pre tieto mechanizmy, nie ich aktuálny operational state.

## 14. Connected incident `GITOPS-PAY-61`

Atlas Payments zaviedol production GitOps pre release `payments 9.0`.

Intended transition:

```text
release manifest commit 9f31c2a
→ reviewed production ref update
→ Argo CD resolves exact inputs
→ deterministic render
→ sync 63 resources
→ workload health
→ settlement canary a business acceptance
```

Git commit deklaroval:

```text
image digest:                 sha256:pay900a
route policy generation:     1842
replicas:                     24
termination grace:           45 s
```

Effective writers však boli:

```text
Git environment repository
+ Argo CLI parameter override z predchádzajúceho hotfixu
+ CI kubectl apply po merge
+ on-call kubectl patch
+ HPA a admission mutation
```

Konkrétne:

- Argo parameter override držal image digest `sha256:pay899hf7` a mal precedence nad Git values;
- CI použila production kubeconfig a po merge aplikovala render s `ROUTE_POLICY_GENERATION=1841`;
- on-call patchla live Deployment na `sha256:pay900b` bez Git commit-u;
- system-wide `ignoreDifferences` ignorovalo celý `/spec/template/spec/containers` subtree;
- automated sync bol zapnutý, ale `selfHeal` nie;
- production branch povoľovala force push a bola na 7 minút presunutá späť na starší commit.

Po 38 minútach existovali tri odlišné generations:

```text
Git declared:        pay900a / route 1842
Argo resolved:       pay899hf7 / route 1842
live Deployment:     pay900b / route 1841
```

Argo UI zobrazovalo Application ako `Synced`, pretože critical container differences boli ignorované. `Healthy` Deployment iba dokazoval required ready Pods, nie intended image alebo route-policy generation.

Dôsledky:

- `18` Podov bežalo na `pay900b`, `6` na `pay899hf7` počas stalled rollout-u;
- `3 214` settlements použilo route policy generation `1841` namiesto `1842`;
- `96` operations vyžadovalo provider-ledger reconciliation;
- Git diff ani Argo sync status nevedeli samostatne vysvetliť effective production state;
- rollback branch-e neodstránil CLI override ani live-only fields.

### Causal boundaries

- **Source-of-truth root cause:** critical desired fields mali viac authoritative writers a controller-resolved desired state obsahoval override mimo Git-u.
- **Immutability failure:** production ref a dependency/override graph neidentifikovali jednu reprodukovateľnú generation.
- **Governance failure:** CI a break-glass identities mali direct write access bez mandatory Git reconciliation.
- **Amplifiers:** broad ignore rule, self-heal disabled, floating branch, incomplete writer inventory a acceptance založená na `Synced/Healthy` labels.

### Recovery

```text
fence CI a human direct writers
→ export Git, Application spec, overrides, controller cache a live managedFields
→ identify exact operation/resource cohorts
→ establish one authoritative production generation
→ remove parameter override
→ narrow ignore rules
→ commit intended image/policy generation
→ sync a verify rendered/live digests
→ reconcile affected settlements
→ test direct drift, failed sync, rollback a second promotion
```

## 15. Acceptance verdict

Git source-of-truth design je prijatý, keď:

- exact repository/path/ref/commit a target subject sú explicitné;
- desired state je declarative, versioned a reproducible;
- artifacts, charts, plugins a external dependencies sú pinned alebo majú explicitný resolution contract;
- authoritative promotion transition je identifikovaná;
- branch/tag mutation policy zodpovedá assurance requirements;
- controller-resolved inputs a final rendered object inventory sú evidované;
- parameter overrides a external writers sú odstránené alebo explicitne governed;
- field ownership medzi GitOps, autoscalers, operators a secret controllers je definovaný;
- direct mutation má bounded break-glass lifecycle a povinné reconciliation;
- Git desired, controller desired a live state sú pozorovateľné oddelene;
- rollback obnoví celý effective desired-state graph, nie iba jeden ref;
- second-change, force-push, mutable dependency, direct-drift a controller-restart tests prejdú;
- forbidden hidden override, multi-writer oscillation, stale artifact a false-synced outcomes sú odmietnuté.

## 16. Troubleshooting flow

```text
Git tvrdí A, controller alebo runtime vykonáva B
→ exact application/environment subject
→ repository, path, ref a resolved commit
→ artifact/dependency/plugin generations
→ Application/controller parameters a overrides
→ rendered desired manifest set
→ live objects, managedFields a tracking identity
→ writer/precedence inventory
→ diff/ignore/normalization policy
→ health a business outcome
→ authoritative repair a second reconciliation
```

## 17. Anti-patterny

### Všetko je v Git-e

Nie, ak image tag, parameter override, secret input alebo plugin output môže zmeniť effective desired state bez nového commit-u.

### Main branch je production

Branch názov neurčuje authority. Potrebný je explicitný promotion, protection a target contract.

### Git history je immutable

Commit content je immutable, ale refs možno meniť. Force push a retagging menia authoritative pointer.

### Controller píše status späť do Git-u

Observed state sa nemá bez decision boundary automaticky meniť na nový intent.

### Break-glass patch opravíme neskôr

Bez expiry, ownera a reconciliation gate-u sa temporary writer stáva permanentným druhým source of truth.

### Synced znamená zhodu s Git-om

Môže ísť o zhodu s controller-resolved desired state po overrides a ignore rules, nie s tým, čo reader vidí v repository.

## 18. Kontrolné otázky

1. Čo tvorí exact desired-state subject?
2. Ako sa Git desired state líši od controller-resolved desired state?
3. Prečo branch alebo tag nie sú immutable identity?
4. Ako mutable image tag porušuje reproducibility?
5. Čo je authoritative promotion transition?
6. Ktoré external inputs môžu meniť render?
7. Ako sa desired spec líši od observed statusu?
8. Prečo field ownership patrí do GitOps contractu?
9. Kedy je parameter override druhý source of truth?
10. Prečo `GITOPS-PAY-61` ostal `Synced`?
11. Čo musí obnoviť úplný rollback?
12. Čo overuje source-of-truth acceptance verdict?

## Glossary impact

Relevantné pojmy: desired-state subject, source-of-truth boundary, authoritative ref, resolved desired state, immutable desired generation, promotion transition, environment repository, render boundary, pinned dependency, parameter override, writer inventory, field ownership, break-glass writer, Git desired state, controller desired state, live state a source-of-truth acceptance verdict.

## Primárne zdroje

- [OpenGitOps Principles](https://opengitops.dev/)
- [Git — gitrevisions](https://git-scm.com/docs/gitrevisions)
- [Argo CD — Tracking and Deployment Strategies](https://argo-cd.readthedocs.io/en/stable/user-guide/tracking_strategies/)
- [Argo CD — Parameter Overrides](https://argo-cd.readthedocs.io/en/release-3.2/user-guide/parameters/)
