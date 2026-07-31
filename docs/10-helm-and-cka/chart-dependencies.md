# Chart dependencies

Helm dependency nie je samostatný release. Parent chart a všetky enabled application alebo library dependencies sa resolve-nú, zabalia, vyrenderujú a aplikujú ako jeden aggregate release subject. Dependency preto nepridáva iba ďalší directory s templates. Mení source code, values scope, global helper namespace, Kubernetes inventory, hooks, CRDs, RBAC, images, data lifecycle, rollback boundary a supply-chain trust celého release-u.

Základná otázka nie je „ako pridám subchart“. Je to ownership rozhodnutie: má mať component rovnakého ownera, cadence, namespace, rollback a failure domain ako parent application? Ak nie, dependency iba skrýva nezávislý systém pod jedným Helm revision sequence-om.

## 1. Dominantný dependency lifecycle

Dependency lifecycle začína component ownershipom a končí až runtime a decommission dôkazom. Declaration v `Chart.yaml` vyjadruje intent a version constraint, nie exact artifact. Resolver vyberie konkrétnu verziu, lock ju zachytí, build vytvorí packaged graph a až tento graph vstupuje do aggregate renderu.

```text
component ownership a failure-domain decision
→ dependency declaration a source trust
→ controlled version resolution
→ reviewed lock a immutable artifacts
→ packaged first-level a transitive graph
→ values/alias/global/condition contracts
→ aggregate render vrátane helpers, hooks, CRDs a RBAC
→ one-release mutation a runtime convergence
→ business acceptance
→ dependency upgrade, recovery alebo lifecycle separation
```

Dependency je bezpečná iba vtedy, keď sa graph dá reprodukovať bez závislosti od času, registry state-u alebo skrytého internet fallbacku. Zároveň musí byť vedome prijaté, že failure child chartu môže zablokovať alebo čiastočne zmeniť celý parent release.

## 2. Exact Atlas dependency subject

Atlas Payments používa parent chart `atlas-payments 2.7.0` s digestom `CH57`, release `payments-prod` revision 18 v clustri `K136`, declaration z commit-u `C57`, lock `D57`, packaged graph `PG57` a aggregate manifest `M57`.

Graph obsahuje library chart `atlas-platform`, ktorý poskytuje security a label helpers, a application chart `atlas-payment-metrics`, ktorý pridáva exporter image a ServiceMonitor resources. Každý node subjectu musí byť identifikovaný declared name/aliasom, source repository alebo OCI namespace-om, version constraintom, resolved version a digestom, publisher/trust evidence, values scope-om, template/helper/CRD/hook/RBAC inventory, transitive dependencies a lifecycle ownerom.

Tieto údaje umožnia vysvetliť, prečo sa manifest zmenil aj keď parent source zostal rovnaký. Samotná verzia `1.6.3` nestačí, ak registry umožňuje mutable content alebo incident potrebuje presný digest a retained bytes.

## 3. Declaration, resolution a lock

Chart API v2 deklaruje dependencies v `Chart.yaml`. Version môže byť exact alebo range ako `~1.6.0`; repository určuje discovery source a `condition`, `tags` alebo `alias` menia local behavior. Declaration je však iba pravidlo výberu.

```text
constraint ~1.6.0
≠ resolved 1.6.3
≠ artifact digest LD58
≠ verified publisher
≠ complete transitive graph
```

`helm dependency update` číta constraints, kontaktuje repositories, vyberie aktuálne matching versions, stiahne artifacts a zmení `Chart.lock` aj `charts/`. Je to graph mutation command. Rovnaký `Chart.yaml` môže pri neskoršom registry state-e vytvoriť iný package a manifest.

`helm dependency build` pri validnom locku rekonštruuje `charts/` podľa uzamknutého graphu bez nového version negotiation. Produkčný pattern preto používa samostatný controlled update workflow, review declaration aj lock diffu a v release pipeline `dependency build` plus digest read-back. Ak lock chýba, pipeline má zlyhať, nie ticho vyjednať nový graph.

`Chart.lock` nie je signature ani kompletný SBOM, ale je základným resolution contractom. Ručná editácia locku ničí väzbu na resolver. Lock tiež nestačí bez artifact retention alebo mirroru; reprodukovateľnosť vyžaduje, aby exact bytes zostali dostupné aj po incidente alebo rollback reviewe.

## 4. Application a library dependencies

Application dependency renderuje vlastné Kubernetes resources do spoločného manifestu. Je vhodná iba vtedy, keď parent release skutočne vlastní jej deployment, support, data a rollback lifecycle. Shared database, cluster-wide operator alebo platform controller s vlastným SLO zvyčajne patrí do samostatného release-u.

Library dependency spravidla nevytvára workload resources, ale poskytuje named templates. Jej blast radius môže byť širší, pretože zmení parent names, selectors, images, securityContext, RBAC, checksums, API variants alebo hooks bez zmeny parent call sites. Library chart je executable source-code dependency aggregate renderu, nie neškodný formatting balík.

Ownership test porovnáva ownera, cadence, rollback boundary, namespace/tenant lifecycle, privileges, persistent data, support window a failure domain. Ak component potrebuje samostatné scaling, backup, security alebo decommission rozhodnutia, single release ho zväčša spája nesprávne.

## 5. Values scope, globals a aliases

Subchart dostáva vlastný values subtree. Parent môže child values override-nuť pod dependency name alebo aliasom, ale child nemá implicitný prístup k arbitrary parent values. Tento scope contract znižuje coupling a musí byť zahrnutý v schema a compatibility tests.

`global` vytvára cross-chart API. Je vhodný pre úzke stabilné identities ako approved image registry, organization/tenant coordinate, cluster domain alebo shared external ServiceAccount reference. Broad global tree robí z jedného keyu hidden multi-consumer writer. Každý global field preto potrebuje ownera, type/schema, consumer inventory a old/new behavior test.

Alias umožní použiť rovnaký chart viackrát s rozdielnymi local values, napríklad `primaryCache` a `sessionCache`. Nezaručuje však resource uniqueness. Subchart fullname helpers, Service names, selectors, PVCs, ports, ServiceAccounts, hooks a external resources musia podporovať multiple instances. Hard-coded name môže spôsobiť collision aj pri správnych aliases.

## 6. Conditions, tags a import contracts

`condition` alebo `tags` rozhodujú, či dependency templates vstúpia do aggregate renderu. Boolean verdict preto nie je iba UI toggle. Mení create/update/delete diff a môže zanechať PVC/PV, CRD, hook-created resource, DNS/LB/IAM object, credential alebo stale parent reference.

Disabled dependency potrebuje decommission contract. Parent application nesmie naďalej odkazovať na jej Service alebo config. Data a external resources sa riešia podľa retention a ownership pravidiel; boolean `false` sám nič bezpečne nemaže.

`import-values` prenáša versionovaný child export do parent configuration. Nie je to runtime discovery. Import môže vytvoriť key collision, nejasnú precedence alebo breaking parent behavior po child upgrade. Používa sa iba pre explicitný stable interface a testuje sa proti old aj new child outputu.

## 7. Packaged a transitive graph

Dependency artifacts môžu byť vendored alebo rekonštruované z mirroru, no repository policy musí určiť source of truth, digest verification, archive retention, offline build a scanning. `Chart.lock` s nedostupným upstream artifactom nie je complete recovery model.

Review enumeruje celý transitive graph. Parent môže cez first-level metrics chart nepriamo získať observability library helpers, images, hooks alebo RBAC. First-level inventory preto nestačí; package evidence zahŕňa všetky chart digests, definition inventory, rendered source mapping a downstream images.

OCI registry rieši transport a storage, nie automaticky publisher trust. Source contract zahŕňa endpoint/TLS/authentication, namespace ownership, artifact digest, provenance/signature policy, retention a mirror path. Production release má vedieť exact artifact read-backnuť a po incidente získať rovnaké bytes.

## 8. Single-release failure domain

Parent a enabled dependencies zdieľajú release name, namespace/storage history, aggregate render, revision sequence a upgrade/rollback command. Dependency API error môže zlyhať celý release; hook môže zablokovať upgrade; helper môže zmeniť parent object; CRD môže rozšíriť cluster-scoped blast radius a partial mutation môže zasiahnuť parent aj child resources.

Helm resource ordering nie je readiness orchestration. Vytvorená Service neznamená ready endpoints, vytvorený Deployment neznamená initialized application a vytvorená CRD neznamená dostupný conversion webhook. Reálne dependency requirements sa riešia probes, controllers, idempotent Jobs, generation-aware health alebo oddelenými staged releases.

Release boundary preto musí zodpovedať ownership a recovery boundary. Ak child nemožno bezpečne rollbacknúť spolu s parentom alebo jeho outage nemá zastaviť parent release, samostatná release identity je čistejší model.

## 9. CRDs a hooks v dependency graph-e

CRD je cluster-scoped schema a data compatibility boundary. Dependency môže priniesť CRD, conversion webhook, controller, custom resources a storage-version migration. Rollback parent manifestu nemusí vrátiť schema ani stored objects. Shared operator a CRDs preto často patria do platform release-u s vlastným consumer inventory a upgrade planom.

Hook môže vykonať migration, backup, external registration, certificate generation, bootstrap RBAC alebo cleanup. Jeho side effect patrí do parent incident subjectu aj pri optional child charte. Review obsahuje lifecycle point/weight, execution identity a RBAC, idempotency key, timeout, unknown-outcome read-back, evidence retention, delete policy a rollback/compensation boundary.

Dependency upgrade bez tohto inventory môže vyzerať ako harmless template bump a pritom zmeniť durable database alebo external system skôr, než parent rollout začne.

## 10. Dependency upgrade lifecycle

Upgrade začína current locked graphom a target declaration zmenou. Controlled resolver vytvorí nový lock, old/new artifacts a defaults sa porovnajú, aggregate render diff sa analyzuje a samostatne sa posúdia helper contracts, names/selectors, APIs/CRDs, RBAC, hooks, PVC/data model, probes, images a transitive graph.

```text
D56 current graph
→ target declaration
→ D57 resolved graph
→ artifact/default/helper inventory diff
→ aggregate semantic render diff
→ install, upgrade, rollback a data tests
→ canary consumer/release
→ production acceptance
→ old artifact retirement
```

Changelog a SemVer sú vstupy, nie dôkaz compatibility. Consumer test musí ukázať behavior nad current production revision a forbidden outcomes, napríklad selector replacement, privilege expansion alebo orphan data.

## 11. Connected incident: CI znovu resolve-ol library chart

Parent deklaroval `atlas-platform` range `~1.6.0`. Reviewed development render používal version 1.6.1, ale `Chart.lock` nebol commitnutý. Production CI pred každým release spúšťalo `helm dependency update`. Medzitým registry publikovalo 1.6.3 s helperom `common.selectorLabels`, ktorý kolidoval s parent helperom.

Exact subject zahŕňal commit `C57`, constraint, missing reviewed lock, resolver time a repository state, resolved version 1.6.3, artifact `LD58`, packaged graph `PG57`, helper collision, manifest `M57` a revision 18.

Hypotézy zahŕňali parent source alebo values change, stale vendoring, new range resolution, mutable artifact, transitive helper, alias/condition change, admission mutation a Helm apply behavior. Packaged parent diff a exact V57 vylúčili parent change. CI command a registry response dokázali new resolution. Definition inventory v full graph-e našiel collision ešte pred admission.

```text
missing reviewed Chart.lock
→ production dependency update re-resolve-ne range
→ atlas-platform 1.6.3 / LD58 vstúpi do PG57
→ global helper collision zmení selector
→ API odmietne immutable Deployment update
→ revision zlyhá po možných skorších API/hook side effects
```

Root cause nebol iba chybný helper. Release control dovolil nepreskúmanú dependency generation bez source alebo lock transitionu.

Containment zastavilo release aj dependency-update jobs, zachovalo declaration, registry digests, packaged graph, M57 a Helm history, ponechalo fungujúci Deployment a preverilo hooks/cluster-scoped side effects. `--force` sa nepoužil, pretože by skryl graph chybu replacementom identity.

Recovery vybrala reviewed dependency digest, opravila global helper names, vytvorila controlled lock `D58`, mirrorovala artifacts, zmenila release CI na `dependency build` s digest verification a pridala full-graph duplicate-helper scan, semantic diff a upgrade test. Nový parent artifact `CH58` vznikol z commit-u `C58` a graphu `PG58`.

Acceptance vyžadovala repeated clean build s rovnakým package digestom, nulový vplyv repository timing-u, complete lock/inventory zhodu, stable Deployment selector, approved hooks/CRDs/RBAC, successful payment journey a deterministic second build/render. Disabled dependency path zároveň nesmel ponechať neznámy state.

## 12. Supply-chain, air-gap a troubleshooting

Každá dependency pridáva executable render logic a často image alebo privilege surface. Controls zahŕňajú approved publisher, exact version/digest, reviewed lock, retained mirror, provenance/signature verification, chart scan, full rendered policy, image digest enforcement, CRD/RBAC/hook inventory, transitive SBOM a EOL/vulnerability monitoring.

Air-gapped release mirroruje parent aj všetky transitive charts, images, provenance metadata, CRDs/controllers a potrebné index metadata. Import path overí identity a uloží immutable artifacts. Production nemá hidden fallback na verejný internet, pretože ten by mohol vytvoriť iný graph alebo obísť approved source.

Troubleshooting začína parent release a source commitom, pokračuje constraintom, lockom, `charts/` digests, registry identity, full graphom, enablement/alias/global values a aggregate render diffom. Potom sa kontrolujú hooks, CRDs, RBAC a partial release state. Recovery sa vykonáva v authoritative source/locku; `helm dependency update` sa nad incident artifactom nespúšťa, pokiaľ zámerom nie je vedome vytvoriť nový graph.

Najčastejšie anti-patterny sú independent component v application dependency, range bez locku, update pri každom release, version bez digestu, broad globals, alias považovaný za isolation, condition považovaná za decommission, first-level-only review, library chart považovaný za harmless, CRD/operator v náhodnom application release a dependency failure riešený force replacementom.

## Kontrolné otázky

1. Kedy component patrí do dependency a kedy do samostatného release-u?
2. Ako sa declaration, resolved artifact, lock a packaged graph líšia?
3. Prečo `dependency update` nie je bezpečný implicitný release krok?
4. Ako globals, aliases a conditions menia effective graph a lifecycle?
5. Prečo library chart môže mať väčší blast radius než application subchart?
6. Ktoré CRD a hook boundaries musí upgrade reviewovať?
7. Ako preukážeš complete transitive graph a artifact trust?
8. Čo uzatvára deterministic build a business acceptance?

## Executable lab: `Chart.yaml`, `Chart.lock`, `update` a reprodukovateľný `build`

Dependency declaration je range alebo exact-version intent. Reprodukovateľný build vznikne až vtedy, keď reviewnutý `Chart.lock` a packaged dependency archives zodpovedajú tomuto intentu.

Parent `Chart.yaml` môže obsahovať interný library chart:

```yaml
apiVersion: v2
name: atlas-payments
version: 0.3.0
dependencies:
  - name: atlas-library
    version: 1.6.3
    repository: oci://registry.example.com/helm
  - name: redis
    version: 2.4.1
    repository: oci://registry.example.com/helm
    condition: redis.enabled
```

Values explicitne rozhodnú, či optional runtime dependency patrí do renderu:

```yaml
redis:
  enabled: false
```

Pri vedomom dependency upgrade-e použi:

```bash
helm dependency update ./atlas-payments
helm dependency list ./atlas-payments
git diff -- atlas-payments/Chart.lock
```

`update` resolve-ne dependencies podľa `Chart.yaml`, stiahne packages do `charts/` a môže zmeniť `Chart.lock`. Preto patrí do samostatnej reviewnutej dependency-change operácie, nie do každého production build-u.

V bežnom CI build-e odstráň lokálny cache adresár a obnov ho z locku:

```bash
rm -rf atlas-payments/charts
helm dependency build ./atlas-payments
sha256sum atlas-payments/charts/*.tgz
```

`build` používa existujúci `Chart.lock`; nemá potichu vyberať novšie compatible versions. Po príkaze musí platiť:

```bash
git diff --exit-code -- atlas-payments/Chart.lock
```

Ak sa lock zmenil, build nebol čistou materializáciou schváleného dependency graphu. Samotný nezmenený lock však stále nepreukazuje provenance alebo dôveryhodnosť stiahnutého package-u. CI má navyše uchovať digesty package archives, registry identity a prípadné signature/provenance verification podľa supply-chain contractu.

Optional dependency test vykonaj dvakrát:

```bash
helm template payments-dev ./atlas-payments \
  --set redis.enabled=false > /tmp/without-redis.yaml

helm template payments-dev ./atlas-payments \
  --set redis.enabled=true > /tmp/with-redis.yaml

grep -n 'kind: StatefulSet' /tmp/without-redis.yaml || true
grep -n 'kind: StatefulSet' /tmp/with-redis.yaml
```

Prvý render nesmie obsahovať Redis workload; druhý ho má obsahovať. Tento test preukazuje condition wiring v renderi. Nepreukazuje, že subchart je runtime kompatibilný s parent application, že storage class existuje alebo že upgrade zachová dáta.

## Glossary impact

Relevantné pojmy: Helm dependency subject, declaration constraint, resolved chart artifact, dependency lock, packaged graph, transitive graph, dependency ownership test, global values contract, dependency enablement verdict, single-release failure domain, dependency upgrade generation a mirror-only reproducibility.

## Primárne zdroje

- [Helm — Chart Dependencies](https://helm.sh/docs/topics/charts/#chart-dependencies)
- [Helm — Dependency Commands](https://helm.sh/docs/helm/helm_dependency/)
- [Helm — Subcharts and Global Values](https://helm.sh/docs/chart_template_guide/subcharts_and_globals/)
- [Helm — Library Charts](https://helm.sh/docs/topics/library_charts/)
- [Helm — Registries](https://helm.sh/docs/topics/registries/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Named templates](named-templates.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Hooks →](hooks.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
