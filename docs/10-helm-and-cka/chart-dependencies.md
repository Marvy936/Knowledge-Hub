# Chart dependencies

Helm chart môže skladať application z ďalších charts. Dependency nie je samostatný Helm release: templates parent chartu a všetkých enabled dependencies sa agregujú do jedného rendered manifest setu a jedného release lifecycle. Dependency graph preto ovplyvňuje values scope, resource ownership, upgrade blast radius, supply chain aj rollback.

## 1. Dependency declaration

Pre chart API `v2` sa dependencies deklarujú v `Chart.yaml`:

```yaml
apiVersion: v2
name: payments
version: 1.4.0

dependencies:
  - name: redis
    version: 20.6.2
    repository: https://charts.example.com
```

Základné fields:

- `name` — chart name,
- `version` — exact version alebo SemVer constraint,
- `repository` — chart repository alebo podporovaný dependency source,
- `alias` — local dependency identity,
- `condition` — values path pre enable/disable,
- `tags` — skupinové prepínanie,
- `import-values` — prenos vybraných child values do parent scope.

## 2. Application chart a library chart

### Application dependency

Renderuje Kubernetes resources a je súčasťou release manifestu.

### Library dependency

Poskytuje reusable named templates a primitives, ale sama nevytvára application release resources ako bežný application chart.

Library chart je vhodný na organization-wide helpers. Application dependency je vhodná, keď parent release skutočne vlastní lifecycle danej komponenty.

## 3. Subchart je stand-alone

Application subchart:

- má vlastné `Chart.yaml`, values a templates,
- nemá implicitný prístup k parent values,
- môže byť testovaný samostatne,
- parent môže override-nuť jeho values,
- všetky charts môžu čítať `global` values.

Subchart nemá byť napísaný tak, že funguje iba pri konkrétnom parent chart-e, pokiaľ ide o reusable application dependency.

## 4. Values scope

Parent defaults:

```yaml
redis:
  architecture: standalone
  auth:
    enabled: true
```

Subchart číta:

```gotemplate
{{ .Values.architecture }}
```

Nie:

```gotemplate
{{ .Values.redis.architecture }}
```

Parent nesting key sa pri vstupe do subchart scope odstráni.

## 5. Global values

```yaml
global:
  imageRegistry: registry.example.com
  environment: production
```

`global` values sú dostupné parentu aj subcharts:

```gotemplate
{{ .Values.global.imageRegistry }}
```

Používaj ich iba pre skutočne cross-chart contracts, napríklad:

- registry prefix,
- organization labels,
- shared cluster domain,
- common identity reference.

Nedávaj do `global` celý environment configuration tree. Vznikne implicitné coupling a key collision.

## 6. Version constraints

Exact version:

```yaml
version: 20.6.2
```

Range:

```yaml
version: ~20.6.0
```

Range umožňuje `helm dependency update` vybrať najnovšiu verziu spĺňajúcu constraint. Release build však má používať commitnutý lock file a kontrolovaný dependency update workflow.

Trade-off:

- exact constraint zvyšuje explicitnosť,
- range zjednodušuje patch discovery,
- `Chart.lock` fixuje resolved verziu pre reprodukovateľný build,
- update automation musí stále vykonávať testy a review changelogu.

## 7. `helm dependency update`

```bash
helm dependency update ./payments-chart
```

Command:

1. načíta constraints z `Chart.yaml`,
2. vyberie kompatibilné dependency versions,
3. stiahne charts do `charts/`,
4. odstráni niektoré neaktuálne managed dependencies podľa command semantics,
5. vytvorí alebo aktualizuje `Chart.lock`.

`dependency update` **re-resolve-ne** dependency graph. Nepoužívaj ho ako implicitný krok production release bez review zmeneného locku.

## 8. `helm dependency build`

```bash
helm dependency build ./payments-chart
```

Pri existujúcom `Chart.lock` rekonštruuje `charts/` podľa uzamknutých versions bez nového dependency negotiation.

CI/release pattern:

```text
reviewed Chart.yaml + committed Chart.lock
→ helm dependency build
→ verify/package/lint/test
```

Ak lock neexistuje, behavior môže prejsť na update-like resolution. Preto lock file validuj explicitne.

## 9. `Chart.lock`

Lock file zachytáva resolved dependency graph a digest metadata podľa Helm formátu.

Commituj ho spolu s `Chart.yaml`, keď dependencies spravuješ deklaratívne.

Pri zmene dependency:

1. uprav `Chart.yaml`,
2. spusti controlled `helm dependency update`,
3. review-ni nový `Chart.lock`,
4. skontroluj stiahnuté charts,
5. renderuj a testuj celý release,
6. commitni declaration a lock spolu.

Ručná editácia lock file-u je anti-pattern.

## 10. `charts/` directory

Dependency chart môže byť v `charts/` ako:

- packaged `.tgz`,
- unpacked chart directory,
- manually vendored dependency.

Rozhodni repository policy:

### Commitnuté dependency archives

Výhody:

- offline build,
- menšia závislosť od repository availability,
- jednoduchšia artifact inspection.

Nevýhody:

- binárny diff,
- repository size,
- duplicita lock + archive,
- nutnosť supply-chain skenu vendored obsahu.

### Necommitnuté `charts/`

CI ho rekonštruuje cez `helm dependency build`.

Výhody:

- menší Git repository,
- lock je source of resolution.

Nevýhody:

- release závisí od registry/repository availability,
- air-gap potrebuje mirror/cache,
- remote artifact môže zmiznúť bez retention policy.

## 11. Repository identity

Dependency source môže používať:

```yaml
repository: https://charts.example.com
```

alebo repository alias:

```yaml
repository: "@internal"
```

Alias závisí od local Helm repository configuration. Pre CI musí byť bootstrap aliasu explicitný.

Source contract musí definovať:

- TLS validation,
- authentication,
- immutable artifact retention,
- repository ownership,
- provenance/signature policy,
- availability a mirror strategy.

## 12. OCI dependencies

Helm charts možno distribuovať cez OCI registry. Pri dependency source dodrž:

- registry authentication,
- immutable version/tag policy,
- namespace ownership,
- content retention,
- provenance/signature workflow,
- air-gapped mirror.

OCI registry support neznamená automatické trust verification. Artifact identity, publisher a policy musia byť overené osobitne.

## 13. `condition`

```yaml
dependencies:
  - name: redis
    version: 20.6.2
    repository: https://charts.example.com
    condition: redis.enabled
```

Values:

```yaml
redis:
  enabled: false
```

Condition riadi, či sa dependency načíta/renderuje.

Riziká:

- disabled dependency môže zanechať staré release resources podľa upgrade diff/lifecycle,
- application môže stále očakávať jej Service,
- PVC alebo external data lifecycle sa nesmie spoliehať iba na boolean,
- schema má validovať dependent configuration.

## 14. Tags

```yaml
dependencies:
  - name: redis
    tags:
      - cache
  - name: memcached
    tags:
      - cache
```

Parent values:

```yaml
tags:
  cache: false
```

Tags umožňujú skupinové prepínanie. Condition je spravidla presnejší per-dependency contract. Pri kombinácii tags a conditions dokumentuj precedence a testuj všetky relevantné kombinácie.

## 15. Alias

Rovnaký chart možno použiť viackrát:

```yaml
dependencies:
  - name: redis
    alias: primaryCache
    version: 20.6.2
    repository: https://charts.example.com

  - name: redis
    alias: sessionCache
    version: 20.6.2
    repository: https://charts.example.com
```

Values sa viažu na alias:

```yaml
primaryCache:
  architecture: replication

sessionCache:
  architecture: standalone
```

Over resource naming, selectors, Services, PVCs a port collisions. Subchart musí podporovať viac inštancií v jednom namespace/release.

## 16. `import-values`

Dependency môže exportovať vybraný values contract:

```yaml
exports:
  service:
    port: 6379
```

Parent dependency declaration môže tento subtree importovať.

Použitie je vhodné iba pri stabilnom explicitnom interface. Import values nemení rendered Kubernetes resources a nie je service discovery mechanizmus.

Riziká:

- key collision v parent scope,
- nejasný source effective value,
- breaking change child exports,
- zložitejší values precedence model.

## 17. Transitive dependencies

Dependency môže mať vlastné dependencies:

```text
parent chart
→ database chart
  → metrics exporter chart
```

Parent release tak nepriamo vlastní aj transitive resources a hooks.

Pri review analyzuj celý graph:

```bash
helm dependency list ./chart
helm show chart <dependency>
helm show values <dependency>
```

Security a compatibility audit nesmie skončiť pri first-level dependencies.

## 18. Jeden release, nie viac releases

Parent a subcharts vytvárajú jeden Helm release.

Dôsledky:

- spoločná release revision,
- spoločný upgrade/rollback blast radius,
- aggregate manifest ordering,
- shared namespace podľa templates,
- subchart resource failure môže zlyhať celý release,
- dependency nemožno samostatne rollbacknúť ako release.

Komponent s nezávislým SLO, ownerom alebo lifecycle môže patriť do samostatného release-u, nie do dependency.

## 19. Install a update ordering

Helm agreguje resources parentu a dependencies, zoradí ich podľa resource kind a name rules a následne ich vytvára/aktualizuje.

Na poradie medzi aplikáciami sa nespoliehaj ako na readiness orchestration. Kubernetes API acceptance neznamená, že database, webhook alebo controller je pripravený.

Použi:

- readiness/startup probes,
- init/migration Jobs s explicitným contractom,
- `--wait` podľa release modelu,
- controllers a reconciliation,
- oddelené release stages, ak je dependency skutočne sekvenčná.

## 20. CRDs v dependencies

CRDs v dependency `crds/` môžu byť nainštalované pred templates v release lifecycle podľa Helm behavioru.

Riziká:

- CRD je cluster-scoped a môže byť shared,
- Helm CRD upgrade/delete behavior má osobitné hranice,
- dependency uninstall nesmie odstrániť shared schema bez migration analýzy,
- CRD/controller version compatibility musí byť explicitná,
- rollback application resources nemusí rollbacknúť schema.

Shared operator/CRD často patrí do samostatného platform release-u.

## 21. Hooks v dependencies

Hooks deklarované v subcharts sa tiež vykonávajú. Parent chart ich nevie všeobecne vypnúť iba tým, že ich ignoruje.

Pred prijatím dependency skontroluj:

- pre/post install/upgrade/delete hooks,
- hook RBAC a ServiceAccount,
- Jobs a external side effects,
- delete policy a TTL,
- hook timeout/failure behavior,
- compatibility s GitOps alebo restricted clusterom.

## 22. Dependency upgrade

Dependency version bump môže meniť:

- resource names,
- selectors,
- labels,
- APIs,
- CRDs,
- default values,
- PVC/data model,
- hooks,
- RBAC,
- security context,
- container images,
- metrics a probes.

Postup:

1. prečítaj changelog a migration guide,
2. porovnaj old/new chart defaults,
3. renderuj oba effective manifests,
4. vykonaj semantic diff,
5. over deprecated APIs,
6. testuj install aj upgrade path,
7. over rollback/data compatibility,
8. update-ni lock po review.

## 23. Dependency supply chain

Každá dependency pridáva:

- maintainer trust,
- chart templates ako executable render logic,
- images a external downloads,
- RBAC a cluster-scoped resources,
- hooks a Jobs,
- transitive dependencies.

Controls:

- approved sources,
- exact resolved versions,
- lock file,
- provenance/signature verification podľa platformy,
- artifact mirroring,
- chart content scanning,
- rendered-manifest policy,
- image digest policy,
- periodic update a end-of-life monitoring.

## 24. Air-gapped model

Pre offline cluster potrebuješ mirrorovať:

- chart dependencies,
- container images,
- provenance/signature metadata,
- CRD/controller artifacts,
- package indexes podľa workflowu.

Prepíš dependency repositories a image registries kontrolovaným values alebo packaging procesom. Nepoužívaj ad hoc internet fallback z production clusteru.

## 25. Testing dependency graphu

Minimálne testy:

```bash
helm dependency build ./chart
helm dependency list ./chart
helm lint ./chart
helm template test ./chart -f values-ci.yaml
helm template test ./chart -f values-all-disabled.yaml
helm template test ./chart -f values-all-enabled.yaml
```

Ďalej over:

- duplicate resource names,
- selector collisions,
- disabled dependency cleanup,
- alias combinations,
- global value effects,
- CRD/API compatibility,
- hooks,
- server-side validation,
- upgrade z predchádzajúcej production revision.

## 26. Anti-patterny

### `helm dependency update` pri každom release bez review locku

Release môže získať novú dependency bez source zmeny.

### Dependency pre platform-shared database

Application release náhodne vlastní kritický shared stateful service.

### Broad `global` configuration

Subcharts sú implicitne previazané a values ownership je nejasný.

### Range bez commitnutého `Chart.lock`

Build nie je reprodukovateľný.

### Ignorovanie transitive hooks a RBAC

Dependency môže vykonať privilegovaný cluster-side code.

### Podmienenie dependency bez data decommission modelu

Boolean disable odstráni workload, ale zostanú alebo sa stratia dáta nejasným spôsobom.

### Manual edit dependency archive

Artifact už nezodpovedá publisherovi, locku ani provenance.

## 27. Troubleshooting

### Dependency nie je v `charts/`

Spusti `helm dependency build`, over `Chart.lock`, repository auth a network/TLS.

### `Chart.lock` nie je synchronizovaný

`Chart.yaml` sa zmenil bez controlled `dependency update`. Regeneruj lock a review-ni diff.

### Subchart values sa neaplikujú

Over dependency name/alias, nesting v parent values, values precedence a schema.

### Disabled dependency sa stále renderuje

Over exact `condition` path, boolean type, tags a effective values cez `helm get values` alebo local render.

### Dve dependencies vytvárajú rovnaký resource

Over alias support, fullname overrides, namespace a hard-coded names v subcharte.

### Upgrade zlyhá na hooku dependency

Použi `helm get hooks`, inspect-ni Job/Pod logs, RBAC, timeout a delete policy.

### Air-gapped build sa pokúša o internet

Skontroluj všetky first-level aj transitive repositories a image references.

## 28. Kontrolné otázky

1. Prečo dependency nevytvára samostatný Helm release?
2. Aký je rozdiel medzi `dependency update` a `dependency build`?
3. Načo slúži `Chart.lock`?
4. Ako parent override-ne values subchartu?
5. Kedy sú vhodné global values?
6. Čo riešia `condition`, `tags` a `alias`?
7. Prečo môže dependency hook zlyhať celý release?
8. Kedy má byť komponent samostatný release namiesto subchartu?
9. Aké riziko predstavujú CRDs v dependency graph-e?
10. Ako zabezpečíš reprodukovateľný air-gapped dependency build?

## Glossary impact

Relevantné pojmy: Helm chart dependency, Helm subchart, dependency constraint, `Chart.lock`, `helm dependency update`, `helm dependency build`, vendored chart, dependency condition, dependency tag, dependency alias, global value — Helm, `import-values`, transitive chart dependency a single-release dependency graph.

## Oficiálna dokumentácia

- [Charts — Chart Dependencies](https://helm.sh/docs/topics/charts/#chart-dependencies)
- [Dependencies Best Practices](https://helm.sh/docs/chart_best_practices/dependencies/)
- [Subcharts and Global Values](https://helm.sh/docs/chart_template_guide/subcharts_and_globals/)
- [`helm dependency build`](https://helm.sh/docs/helm/helm_dependency_build/)
- [`helm dependency update`](https://helm.sh/docs/helm/helm_dependency_update/)
