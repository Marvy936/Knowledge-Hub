# Chart dependencies

Helm dependency nie je samostatný release. Parent chart a všetky enabled application alebo library dependencies sa resolve-nú, zabalia, vyrenderujú a aplikujú ako jeden release subject. Dependency graph preto mení source code, values scope, global helper namespace, Kubernetes resources, hooks, CRDs, RBAC, images, data lifecycle aj rollback blast radius.

Hlavná otázka nie je „ako pridám subchart“, ale:

```text
ktorý component má patriť do tohto release ownershipu
→ z akého immutable artifactu pochádza
→ ako sa jeho verzia resolve-ne a uzamkne
→ aký render/runtime surface pridáva
→ ako sa upgrade, failure a decommission koordinujú
```

## 1. Dominantný lifecycle

```text
component ownership a lifecycle intent
→ dependency declaration a source trust
→ constraint resolution
→ locked artifact graph
→ values, alias, condition a global contract
→ single-release aggregate render
→ CRD/hook/API/admission execution
→ workload a business acceptance
→ dependency upgrade/recovery
→ retirement alebo oddelenie lifecycle-u
```

Dependency je bezpečná iba vtedy, keď je exact resolved graph reprodukovateľný a celý jeho output patrí do vedome prijatého release failure domainu.

## 2. Atlas dependency subject

Atlas Payments používa:

```text
parent chart: atlas-payments 2.7.0 / CH57
release: payments-prod revision 18
cluster: K136
dependency declaration: Chart.yaml C57
dependency lock: Chart.lock / D57
packaged graph: PG57
rendered manifest: M57
```

Dependency graph:

```text
atlas-payments
├── atlas-platform library chart
│   └── common security/label helpers
└── atlas-payment-metrics application chart
    └── exporter image a ServiceMonitor resources
```

Každý node graphu potrebuje:

- declared name a alias;
- source repository/OCI identity;
- constraint;
- resolved version a digest;
- publisher/trust evidence;
- values scope;
- templates/helpers/CRDs/hooks/RBAC inventory;
- transitive dependencies;
- lifecycle owner a support status.

## 3. Dependency declaration

Chart API v2 deklaruje dependencies v `Chart.yaml`:

```yaml
apiVersion: v2
name: atlas-payments
version: 2.7.0

dependencies:
  - name: atlas-platform
    version: "~1.6.0"
    repository: oci://registry.example.com/helm

  - name: atlas-payment-metrics
    version: "3.4.1"
    repository: oci://registry.example.com/helm
    condition: metrics.enabled
```

Declaration je intent, nie resolved artifact graph.

```text
constraint ~1.6.0
≠ exact version 1.6.3
≠ exact chart digest LD58
≠ verified publisher/provenance
```

Production subject potrebuje resolved identity.

## 4. Application vs. library dependency

### Application dependency

Renderuje Kubernetes resources a vstupuje do spoločného release manifestu. Je vhodná iba vtedy, keď parent release skutočne vlastní jej lifecycle.

### Library dependency

Poskytuje named templates a primitives. Sama typicky nevytvára workload resources, ale jej source code môže zmeniť parent rendered manifests.

Library chart preto nie je „bezpečnejšia, lebo nič nenasadzuje“. Môže meniť:

- resource names;
- selectors;
- labels;
- images;
- securityContext;
- RBAC fragments;
- checksums;
- API variants;
- hook templates.

Oba typy patria do supply-chain a compatibility reviewu.

## 5. Ownership test: dependency alebo samostatný release

Component patrí do dependency graphu, ak:

```text
rovnaký owner
+ rovnaký deployment cadence
+ rovnaký rollback boundary
+ rovnaký namespace/tenant lifecycle
+ prijateľný spoločný blast radius
+ žiadny nezávislý durable data/SLO contract
```

Samostatný release je vhodnejší, ak component má:

- nezávislého ownera alebo support window;
- vlastný SLO a scaling lifecycle;
- shared použitie viacerými applications;
- cluster-scoped CRDs/controllers;
- vlastný persistent data a backup contract;
- odlišnú upgrade/rollback cadence;
- oddelené privileges alebo failure domain.

Shared production database alebo cluster-wide operator zvyčajne nemá byť náhodne vlastnený jedným application release-om.

## 6. Subchart values scope

Parent values:

```yaml
atlas-payment-metrics:
  enabled: true
  serviceMonitor:
    enabled: true
```

V subcharte sa nesting key odstráni. Subchart číta:

```gotemplate
{{ .Values.enabled }}
```

nie:

```gotemplate
{{ .Values.atlas-payment-metrics.enabled }}
```

Values scope je samostatný contract. Parent môže override-nuť child values, ale child nemá implicitný prístup k ľubovoľným parent values.

## 7. Global values

```yaml
global:
  imageRegistry: registry.example.com
  environment: production
```

`global` je cross-chart API. Použi ho pre úzke spoločné identity:

- registry prefix;
- organization/tenant identity;
- cluster domain;
- shared external ServiceAccount alebo secret reference;
- common labels, ak majú stabilný contract.

Broad `global` tree vytvára implicitné coupling:

```text
parent mení jeden key
→ viac subcharts ho interpretuje odlišne
→ rendered diff sa rozšíri
→ ownership effective value-u je nejasný
```

Každý global key potrebuje ownera, schema a consumer inventory.

## 8. Constraint resolution

Exact constraint:

```yaml
version: "1.6.2"
```

Range:

```yaml
version: "~1.6.0"
```

Range je discovery policy. Umožňuje controlled update vybrať novšiu compatible verziu. Release build však nemá opakovane vyjednávať graph.

```text
reviewed declaration
→ controlled resolve
→ reviewed lock
→ reproducible build
```

SemVer compatibility je publisher claim, nie dôkaz, že rendered Kubernetes identity, CRD, data alebo helper contract zostali compatible.

## 9. `helm dependency update`

```bash
helm dependency update ./atlas-payments
```

`update`:

1. načíta constraints;
2. kontaktuje configured repositories/registries;
3. vyberie aktuálne matching versions;
4. stiahne artifacts;
5. aktualizuje `charts/`;
6. vytvorí alebo zmení `Chart.lock`.

Je to graph mutation command.

```text
rovnaký Chart.yaml
+ neskorší repository state
→ iný resolved dependency
→ iný packaged chart
→ iný manifest
```

Nepoužívaj ho ako skrytý production release step bez review lock diffu a artifact evidence.

## 10. `helm dependency build`

```bash
helm dependency build ./atlas-payments
```

Pri existujúcom validnom `Chart.lock` rekonštruuje `charts/` podľa uzamknutého graphu bez nového version negotiation.

Release pattern:

```text
reviewed Chart.yaml + Chart.lock D57
→ dependency build
→ verify downloaded artifact digests
→ package CH57
→ render/test M57
```

Ak lock chýba, workflow nesmie ticho prejsť do update-like behavioru. CI má explicitne zlyhať alebo používať samostatnú controlled dependency-update pipeline.

## 11. `Chart.lock` ako graph evidence

`Chart.lock` zachytáva resolved dependency versions a digest metadata podľa Helm formátu.

Pri dependency zmene:

```text
uprav declaration
→ controlled dependency update
→ review declaration + lock diff
→ verify artifacts a source
→ semantic render diff
→ upgrade/data/security tests
→ commit declaration a lock spolu
```

Lock file nie je publisher signature ani kompletný SBOM. Je však základný resolution contract.

Ručná editácia locku ničí dôveru v resolver output a môže vytvoriť graph, ktorý Helm nevie reprodukovať.

## 12. Packaged graph a `charts/`

Dependency môže byť v `charts/` ako:

- packaged `.tgz`;
- unpacked directory;
- vendored chart;
- artifact rekonštruovaný počas build-u.

Repository policy musí rozhodnúť:

```text
čo je source of truth
kde sa overuje digest
či sa archives commitujú
ako sa rieši offline build
kto vlastní retention/mirror
ako sa skenuje vendored content
```

`Chart.lock` + nedostupný upstream artifact bez mirror/retention policy nie je kompletný reproducibility model.

## 13. Repository a OCI source identity

Dependency source môže byť HTTP chart repository alebo OCI registry.

Source trust zahŕňa:

```text
registry/repository endpoint
TLS a authentication
publisher identity
namespace ownership
artifact version/digest
provenance/signature policy
retention a deletion policy
mirror/air-gap path
```

OCI transport neposkytuje automaticky publisher trust. Mutable tag alebo retagged chart môže stále zmeniť content.

Production release má package-núť alebo pinovať exact chart artifacts a podporiť read-back verification.

## 14. Alias ako local dependency identity

```yaml
dependencies:
  - name: redis
    alias: primaryCache
    version: "20.6.2"
    repository: oci://registry.example.com/helm

  - name: redis
    alias: sessionCache
    version: "20.6.2"
    repository: oci://registry.example.com/helm
```

Values:

```yaml
primaryCache:
  architecture: replication

sessionCache:
  architecture: standalone
```

Alias rieši values a dependency identity, nie automaticky resource uniqueness.

Over:

- fullname helpers;
- Services;
- selectors;
- PVC names;
- ports;
- ServiceAccounts/RBAC;
- hooks;
- external resources.

Subchart s hard-coded names nemusí podporovať dve inštancie v jednom release/namespace-e.

## 15. `condition` a `tags`

Condition:

```yaml
condition: metrics.enabled
```

Tags môžu skupinovo prepínať viac dependencies.

Enable/disable rozhodnutie mení rendered graph:

```text
boolean/tag verdict
→ dependency templates prítomné alebo neprítomné
→ resources create/update/delete diff
→ data a external lifecycle
```

Disabled dependency môže zanechať:

- PVC/PV;
- CRDs;
- hook-created resources;
- external DNS/LB/IAM;
- credentials;
- stale application references.

Boolean nie je decommission plan. Schema a release logic musia validovať, že parent application nepoužíva disabled Service alebo config.

## 16. `import-values`

Child môže exportovať explicitný values subtree a parent ho importovať.

To je configuration interface, nie runtime service discovery.

Riziká:

- key collision;
- nejasný authoritative source;
- breaking child export;
- zložitejšia precedence;
- parent behavior sa zmení po dependency update.

Importuj iba stabilný, versionovaný contract a testuj old/new child outputs.

## 17. Transitive graph

```text
atlas-payments
→ atlas-payment-metrics
  → common-observability-library
```

Parent release nepriamo získava templates, helpers, images, hooks, RBAC a supply-chain riziko transitive dependencies.

Review musí enumerovať celý graph, nie iba first-level entries.

Evidence:

```bash
helm dependency list ./chart
helm show chart <artifact>
helm show values <artifact>
```

Doplň artifact digests, packaged content inventory a rendered source comments.

## 18. Single-release failure domain

Parent a enabled dependencies vytvárajú jeden release:

```text
one release name
one namespace/storage history
one aggregate render
one revision sequence
one upgrade/rollback command
```

Dôsledky:

- dependency API error môže zlyhať celý release;
- dependency hook môže zablokovať upgrade;
- dependency helper môže zmeniť parent resource;
- dependency CRD môže rozšíriť cluster-scoped blast radius;
- dependency nemožno samostatne rollbacknúť ako inú release revision;
- partial update môže zasiahnuť parent aj child resources.

Release boundary musí zodpovedať ownership boundary.

## 19. Resource ordering nie je readiness orchestration

Helm agreguje a zoradí resources podľa svojho install/update behavioru. API create order však nepreukazuje, že dependency je ready pre parent application.

```text
Service created
≠ endpoints ready

Deployment created
≠ application initialized

CRD created
≠ controller/webhook ready

Job created
≠ durable migration safe
```

Použi probes, controllers, Jobs s idempotentným contractom, explicitné staged releases alebo external orchestration podľa skutočnej dependency.

## 20. CRDs v dependency graph-e

CRD je cluster-scoped schema a upgrade boundary.

Dependency môže pridať:

- CRD source;
- conversion webhook;
- controller;
- custom resources;
- storage-version migration.

Rollback parent application manifestu nemusí rollbacknúť CRD schema ani stored objects.

Shared operator/CRD často patrí do samostatného platform release-u s vlastným lifecycle-om.

Pred prijatím dependency over:

```text
CRD owner
served/storage versions
controller compatibility
conversion availability
install/upgrade/delete behavior
existing consumers
rollback a decommission boundary
```

## 21. Hooks v dependency graph-e

Dependency hook môže vykonať:

- database migration;
- backup;
- registration do external API;
- certificate generation;
- RBAC/bootstrap operáciu;
- cleanup.

Hook resource a jeho side effects patria do release incident subjectu aj vtedy, keď helper/application subchart vyzerá „voliteľne“.

Review-ni:

- lifecycle point a weight;
- ServiceAccount/RBAC;
- idempotency key;
- unknown-operation handling;
- delete policy a evidence retention;
- timeout;
- external/durable side effects;
- rollback/compensation.

## 22. Dependency upgrade lifecycle

```text
current locked graph D56
→ target declaration change
→ resolve target graph D57
→ old/new artifact and default comparison
→ aggregate render diff
→ CRD/hook/data/security analysis
→ install + upgrade + rollback tests
→ canary release
→ production acceptance
→ old artifact retirement
```

Dependency bump môže meniť:

- default values;
- helper definitions;
- names/selectors;
- APIs/CRDs;
- RBAC/SecurityContext;
- images;
- hooks;
- PVC/data model;
- probes/metrics;
- transitive graph.

Changelog je vstup, nie dôkaz compatibility.

## 23. Worked failure: release build znovu resolve-ne library chart

Parent declaration:

```yaml
- name: atlas-platform
  version: "~1.6.0"
  repository: oci://registry.example.com/helm
```

Reviewed development render používal atlas-platform `1.6.1`. `Chart.lock` však nebol commitnutý. Production CI pred každým release vykonávalo:

```bash
helm dependency update ./chart
```

Medzitým registry publikovalo `1.6.3` s helperom `common.selectorLabels`, ktorý kolidoval s parent helperom.

### Exact dependency subject

```text
parent source commit C57
Chart.yaml constraint ~1.6.0
missing reviewed lock
resolver time/repository index state
resolved dependency version 1.6.3
dependency artifact digest LD58
packaged graph PG57
helper collision subject common.selectorLabels
rendered manifest M57
release payments-prod revision 18
```

### Competing hypotheses

1. Parent chart templates zmenili selector.
2. Values override zmenil name/labels.
3. CI použilo stale vendored dependency.
4. Dependency range resolve-ol novú version.
5. Registry tag/version content bol mutable.
6. Transitive dependency pridala helper definition.
7. Alias alebo condition aktivovali iný chart path.
8. Admission zmenila live selector.
9. Helm major/apply behavior spôsobil update failure bez render zmeny.

### Discriminating observation points

| Hypotéza | Observation |
|---|---|
| parent source | diff packaged parent templates proti reviewed commit |
| values | exact V57 a render s pinned old dependency |
| stale vendoring | `charts/` artifact digest vs. declared/lock graph |
| new resolution | CI dependency command, repository response a resolved version |
| mutable artifact | version/tag read-back digest a registry audit |
| transitive helper | enumerate definitions across full packaged graph |
| alias/condition | effective values a dependency enablement inventory |
| admission | server dry-run/live managedFields |
| apply semantics | same old/new manifests applied with pinned client mode |

### Finding

Production build nebol reprodukovateľný:

```text
missing Chart.lock
→ dependency update re-resolve-ne range
→ atlas-platform 1.6.3 vstúpi do package PG57
→ global helper collision zmení selector output
→ API odmietne immutable Deployment selector
→ Helm release zlyhá po časti API/hook operations
```

Root cause nie je iba „chybný helper“. Release control dovolil nepreskúmanú dependency generation bez source/lock change-u.

### Containment

- zastav release a dependency-update jobs;
- zachovaj Chart.yaml, resolved artifacts, registry digests, packaged chart, M57 a Helm history;
- ponechaj fungujúci Deployment;
- neforce-ni resource replacement;
- over, či dependency hooks alebo cluster-scoped resources už vytvorili side effects;
- blokuj ďalšiu promotion PG57.

### Authoritative recovery

1. vyber reviewed atlas-platform version a digest;
2. oprav helper global names/contracts;
3. vykonaj controlled `helm dependency update`;
4. commitni `Chart.lock` D58 s declaration;
5. mirror-ni artifacts do controlled registry;
6. v release CI používaj `helm dependency build` a digest verification;
7. pridaj full graph duplicate-helper a semantic-render diff;
8. testuj upgrade proti existujúcej release revision;
9. vytvor nový parent chart artifact CH58.

### Verify original a forbidden outcomes

- opakovaný clean build z C58 + D58 vytvorí rovnaký PG58 a chart digest;
- žiadny network/repository timing nemení graph;
- full dependency inventory zodpovedá locku;
- duplicate global helper names sú nulové alebo explicitne approved;
- Deployment selector zostáva stable;
- dependency hooks/CRDs/RBAC zodpovedajú approved inventory;
- release rollout a payment journey uspejú;
- disabled dependencies nezanechajú neznámy state;
- druhý build a render sú deterministic.

### Earlier controls

- lock-required CI gate;
- oddelený dependency-update workflow;
- exact artifact digest/read-back;
- repository mirror a retention;
- full graph scanner/SBOM;
- helper collision test;
- aggregate semantic diff;
- install/upgrade/rollback test z previous production revision;
- component-to-release ownership review.

## 24. Supply-chain controls

Každá dependency pridáva executable render logic a často ďalšie images alebo cluster privileges.

Controls:

```text
approved publisher a source
exact resolved version/digest
reviewed lock
artifact retention/mirror
provenance/signature verification
chart content scan
full rendered-manifest policy
image digest policy
CRD/RBAC/hook inventory
transitive graph inventory
EOL/vulnerability monitoring
controlled update cadence
```

Dependency artifact musí byť možné vyhľadať aj po incidente a rollback reviewe.

## 25. Air-gapped model

Offline release potrebuje mirrorovať:

- parent chart;
- all first-level a transitive chart artifacts;
- container images;
- provenance/signature metadata;
- CRDs/controllers;
- relevant repository/index metadata.

```text
internet source
→ controlled import a verification
→ internal immutable mirror
→ locked build
→ offline render/deploy
```

Žiadny production fallback na verejný internet nemá obchádzať approved graph.

## 26. Test matrix

```text
clean dependency build z locku
repeated deterministic package digest
all dependencies enabled
all optional dependencies disabled
condition + tags combinations
aliases a multiple instances
global values effects
full helper definition inventory
resource-name/selector collisions
CRD/controller compatibility
hook execution/idempotency
RBAC/security policy
server-side install validation
upgrade z current production revision
rollback/roll-forward boundary
disabled dependency decommission
air-gapped mirror-only build
```

## 27. Troubleshooting workflow

```text
fix parent release a source commit
→ inspect Chart.yaml constraint
→ inspect Chart.lock a charts/ artifacts
→ verify source registry/digests
→ enumerate full dependency graph
→ resolve enablement/alias/global values
→ compare aggregate rendered manifest
→ inspect hooks/CRDs/RBAC
→ map failure na single-release operation
→ recover graph v authoritative source
→ verify deterministic rebuild a business outcome
```

Príkazy:

```bash
helm dependency list ./chart
helm dependency build ./chart
helm lint ./chart
helm template payments-prod ./chart -f values-prod.yaml
```

`helm dependency update` používaj počas troubleshooting-u iba v controlled workspace, keď zámerom je vedome vytvoriť nový graph. Nespúšťaj ho nad incident artifactom, ktorý chceš reprodukovať.

## 28. Anti-patterny

- component s independent lifecycle vložený do application dependency;
- range bez reviewed `Chart.lock`;
- `helm dependency update` pri každom release;
- dependency artifact identifikovaný iba version tagom;
- broad global values bez consumer ownershipu;
- alias považovaný za automatickú resource isolation;
- boolean condition považovaný za decommission;
- first-level review bez transitive graphu;
- library chart považovaný za neškodný source;
- CRD/operator vložený do náhodného application release-u;
- dependency hook bez idempotency a external-state evidence;
- release ordering považovaný za readiness orchestration;
- manual edit vendored archive;
- air-gap build s hidden internet fallbackom;
- dependency failure riešený force delete/replace bez graph opravy.

## 29. Kontrolné otázky

1. Kedy component patrí do dependency a kedy do samostatného release-u?
2. Ako sa líši declaration constraint od resolved artifact identity?
3. Prečo `dependency update` a `dependency build` nie sú zameniteľné?
4. Čo `Chart.lock` preukazuje a čo nepreukazuje?
5. Ako subchart values scope a `global` menia ownership configuration?
6. Prečo alias nezaručuje resource uniqueness?
7. Aké side effects môže mať disabled dependency?
8. Ako transitive dependency rozširuje render a security surface?
9. Prečo jeden dependency helper môže zlyhať parent release?
10. Ktoré dôkazy uzatvárajú reprodukovateľný dependency upgrade?

## Glossary impact

Relevantné pojmy: dependency graph subject, dependency ownership test, dependency declaration generation, resolved dependency artifact, locked packaged graph, lock-required release gate, dependency enablement generation, single-release failure domain, library-chart source injection, transitive render surface, dependency decommission subject a deterministic dependency rebuild verdict.

## Oficiálna dokumentácia

- [Charts — Dependencies](https://helm.sh/docs/topics/charts/#chart-dependencies)
- [Dependencies Best Practices](https://helm.sh/docs/chart_best_practices/dependencies/)
- [Subcharts and Global Values](https://helm.sh/docs/chart_template_guide/subcharts_and_globals/)
- [`helm dependency build`](https://helm.sh/docs/helm/helm_dependency_build/)
- [`helm dependency update`](https://helm.sh/docs/helm/helm_dependency_update/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Named templates](named-templates.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Hooks →](hooks.md)
<!-- KNOWLEDGE-NAVIGATION:END -->