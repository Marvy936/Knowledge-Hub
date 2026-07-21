# Helm testing a troubleshooting

Helm troubleshooting musí oddeľovať chart source, dependency graph, values, template rendering, Kubernetes API validation, release storage, live resources a application behavior. Príkaz `helm install` alebo `helm upgrade` môže zlyhať pred vytvorením jediného resource-u, počas hooku, pri API admission-e, počas rollout-u alebo až pri application smoke teste. Každá vrstva potrebuje iné evidence.

## 1. Testovacia pyramída pre Helm chart

Od najlacnejšej po najrealistickejšiu vrstvu:

```text
chart structure a metadata
→ dependency resolution
→ values schema
→ template render
→ YAML/Kubernetes schema
→ policy a security checks
→ server-side dry-run
→ ephemeral cluster install
→ Helm test hooks
→ workload readiness
→ end-to-end application test
```

Jedna úspešná vrstva nepreukazuje nasledujúcu.

## 2. Static chart checks

Základ:

```bash
helm lint ./chart
helm dependency list ./chart
helm show chart ./chart
helm show values ./chart
```

Kontroluj:

- povinné chart metadata,
- chart type a version,
- dependency declarations,
- duplicate alebo neplatné templates,
- values schema,
- deprecated alebo nepodporované fields podľa Helm verzie.

`helm lint` nie je Kubernetes runtime test.

## 3. Values matrix

Chart netestuj iba s default values.

Minimálna matrix:

- defaults,
- production-like values,
- feature zapnutá,
- feature vypnutá,
- subchart enabled/disabled,
- explicitné `false`, `0` a empty string,
- minimálne a maximálne replicas/resources,
- alternative Service/Ingress/Gateway mode,
- IPv4/IPv6 alebo platform-specific variant podľa scope-u.

Príklad:

```bash
for file in values-ci/*.yaml; do
  helm lint ./chart -f "$file"
  helm template test ./chart -f "$file" > /tmp/rendered.yaml
  kubectl apply --dry-run=client -f /tmp/rendered.yaml >/dev/null
done
```

## 4. Render debugging

```bash
helm template payments ./chart \
  -f values-production.yaml \
  --namespace production \
  --debug
```

Užitočné flags a techniky závisia od Helm major verzie, ale typicky zahŕňajú:

- render jedného template súboru,
- debug output,
- explicitné API/Kubernetes version capabilities,
- zahrnutie CRDs,
- show-only filter,
- server-connected dry-run pri `lookup`.

Pri render failure hľadaj:

- template file a line,
- nil pointer/scope,
- wrong values type,
- missing required key,
- invalid function arguments,
- helper collision,
- malformed YAML po renderi.

## 5. Debug helper scope

Časté chyby:

```text
can't evaluate field Values in type string
nil pointer evaluating interface
wrong type for value; expected map
```

Postup:

1. zisti aktuálny význam `.`,
2. skontroluj `range`, `with`, `include` alebo `template` scope,
3. zachovaj root v `$`,
4. pri helperi odovzdaj explicitný `dict`,
5. dočasne vypíš type/value iba bez secretov.

Debug output nesmie zverejniť credentials.

## 6. YAML troubleshooting

Template môže byť syntakticky validný, ale výsledný YAML nie.

Časté príčiny:

- nesprávny `indent`/`nindent`,
- trim marker odstráni potrebný newline,
- string bez quotes sa interpretuje ako bool/number,
- multi-line block má chybnú indentation,
- dva documents sa zlúčia,
- prázdny helper vytvorí neplatný key.

Over:

```bash
helm template test ./chart -f values.yaml > rendered.yaml
yamllint rendered.yaml
kubectl apply --dry-run=client -f rendered.yaml
```

## 7. Kubernetes server validation

Client-side parse nestačí:

```bash
helm template test ./chart -f values.yaml \
  | kubectl apply --dry-run=server -f -
```

Server-side dry-run môže zachytiť:

- chýbajúcu API version,
- schema validation,
- immutable alebo invalid fields pri update simulácii podľa workflowu,
- RBAC,
- quota a LimitRange,
- Pod Security,
- validating/mutating admission,
- CRD conversion.

Potrebuje kompatibilný a dostupný cluster.

## 8. Capabilities a `lookup`

Local `helm template` môže mať iný výsledok než install/upgrade, ak chart používa:

- `.Capabilities.APIVersions`,
- Kubernetes version branching,
- `lookup`,
- cluster-dependent CRDs,
- live release state.

Pre deterministic CI preferuj explicitné capabilities a minimalizuj live lookup. Ak lookup potrebuješ, testuj aj proti ephemeral alebo staging clusteru.

## 9. Policy a security testing

Rendered manifests analyzuj cez organizáciou zvolený policy stack.

Kontroluj:

- privileged containers,
- host namespaces a hostPath,
- root user a capabilities,
- missing requests/limits,
- broad RBAC,
- mutable image tags,
- plaintext Secrets,
- missing NetworkPolicy/PDB podľa platform contractu,
- cluster-scoped resources,
- untrusted hooks a dependencies.

Policy musí byť versionovaná a reprodukovateľná.

## 10. Unit testing templates

Template unit test framework môže porovnávať rendered fields alebo snapshots bez clusteru.

Vhodné assertions:

- resource exists/does not exist,
- exact labels a selectors,
- image reference,
- securityContext,
- values mapping,
- dependency condition,
- checksum annotation,
- helper output.

Limity:

- neoverí admission,
- neoverí controller behavior,
- neoverí readiness ani networking,
- snapshot môže schváliť veľký diff bez semantic review.

## 11. Ephemeral cluster test

Pre významný chart vytvor ephemeral cluster cez schválený nástroj a vykonaj:

```text
cluster bootstrap
→ install CRDs/controllers dependencies
→ helm install
→ wait/rollout
→ helm test
→ application smoke test
→ helm upgrade
→ rollback alebo uninstall
→ cleanup
```

Testuj rovnakú Kubernetes minor verziu a relevantné admission/security policy ako production, pokiaľ je to realistické.

## 12. Chart tests

Chart test je template resource označený hook annotation pre test lifecycle. Spúšťa sa:

```bash
helm test payments -n production --logs
```

Dobrý test overuje konkrétny release invariant:

- DNS resolution Service-u,
- TCP/HTTP response,
- authentication s test identity,
- database connectivity cez application path,
- read-only smoke operáciu,
- schema compatibility endpoint.

Test musí mať:

- explicitný exit code,
- timeout/deadline,
- minimum privileges,
- resources,
- žiadne deštruktívne side effects,
- logs dostupné pred cleanupom.

## 13. Test hooks nie sú end-to-end monitoring

`helm test` je point-in-time release validation. Neoveruje:

- dlhodobú availability,
- production load,
- všetky user journeys,
- disaster recovery,
- multi-zone failover,
- SLO v čase.

Používaj ho spolu s monitoringom a synthetic tests.

## 14. Install troubleshooting

### Release sa nenájde

Over:

```bash
helm list -A
kubectl config current-context
kubectl config view --minify
```

Helm releases sú namespace-scoped. Nesprávny namespace je častá príčina.

### Chart sa nedá stiahnuť

Over:

- repository/OCI reference,
- registry login,
- TLS/CA,
- proxy,
- chart version,
- repository index/cache,
- credentials scope.

### Dependency chýba

```bash
helm dependency list ./chart
helm dependency build ./chart
```

Over `Chart.lock`, `charts/`, repository access a digest.

## 15. Release status troubleshooting

```bash
helm status payments -n production
helm history payments -n production
helm get all payments -n production
helm get values payments -n production --all
helm get manifest payments -n production
helm get hooks payments -n production
```

Status vrstva odpovedá:

- aká je posledná revision,
- aký status Helm zapísal,
- aký manifest a values pozná,
- aké hooks patria release-u.

Neodpovedá automaticky, či application funguje.

## 16. Pending states

Pri `pending-install`, `pending-upgrade` alebo `pending-rollback`:

1. skontroluj hooks a Jobs,
2. skontroluj API a network connectivity,
3. zisti, či iný Helm process stále beží,
4. over release Secret revision/status,
5. zachovaj logs a Events,
6. nepoužívaj ručné mazanie release Secrets ako prvý krok.

Recovery musí rešpektovať konkrétnu Helm verziu.

## 17. Hook troubleshooting

```bash
helm get hooks payments -n production
kubectl get jobs,pods -n production
kubectl get events -n production --sort-by=.metadata.creationTimestamp
kubectl logs job/<hook-job> -n production
```

Rozlišuj:

- render failure,
- API admission failure,
- scheduling/image pull,
- runtime exit,
- active deadline,
- Helm timeout,
- cleanup, ktorý odstránil evidence.

## 18. Workload troubleshooting po úspešnom Helme

Helm success neznamená application success.

Použi Kubernetes chain:

```bash
kubectl get deploy,rs,pod -n production
kubectl rollout status deployment/payments -n production
kubectl describe pod <pod> -n production
kubectl logs <pod> -c <container> -n production --previous
kubectl get service,endpointslice -n production
```

Over:

- image pull,
- config/Secret,
- probes,
- resources,
- scheduling,
- PVC,
- Service selector/targetPort,
- NetworkPolicy,
- external dependencies.

## 19. Drift analysis

Porovnaj tri stavy:

```text
last release manifest
proposed rendered manifest
live Kubernetes object
```

Zdroje driftu:

- manual edit,
- mutating admission,
- HPA,
- operator,
- GitOps controller,
- defaulting,
- external secrets/config reloader,
- emergency change.

Pred opravou urč authoritative writer.

## 20. Secrets a debug output

Rizikové commands:

- `helm get all`,
- `helm get values --all`,
- `helm template --debug`,
- install/upgrade dry-run,
- CI artifacts,
- release Secret inspection.

Sanitizuj output a obmedz access. Dry-run môže renderovať Secret manifests.

## 21. CRD troubleshooting

Problémy:

- CRD ešte neexistuje pri render/apply,
- CRD existuje, ale controller nie,
- version nie je served,
- conversion webhook nefunguje,
- chart očakáva upgrade CRD, ktorý Helm nespraví,
- custom resource je invalid podľa novej schema.

Postup:

```bash
kubectl get crd
kubectl get apiservices
kubectl api-resources
kubectl describe crd <name>
```

CRD lifecycle testuj oddelene od bežného application chartu.

## 22. Uninstall troubleshooting

```bash
helm uninstall payments -n production
```

Ak visí:

- pre-delete hook,
- finalizer,
- API discovery/webhook,
- namespace termination,
- external controller.

Po uninstall-e skontroluj:

- PVC/PV,
- CRDs/custom resources,
- retained resources,
- hook Jobs,
- external LB/DNS/IAM,
- namespace,
- backups.

## 23. CI pipeline

Odporúčaný chart pipeline:

```text
format/lint source
→ dependency lock verification
→ values schema tests
→ render matrix
→ YAML/Kubernetes schema
→ unit/snapshot tests
→ policy/security scan
→ package + provenance/SBOM podľa modelu
→ ephemeral cluster install
→ helm test
→ upgrade/rollback/uninstall scenario
→ publish immutable chart artifact
```

Testuj artifact, ktorý sa bude promovať, nie nový rebuild v každom prostredí.

## 24. Troubleshooting decision tree

```text
Helm command zlyhal?
├─ chart fetch/dependency
├─ values/schema
├─ template/render
├─ Kubernetes API/admission
├─ hook
├─ release storage/concurrency
└─ wait/timeout

Helm command uspel, workload nefunguje?
├─ controller rollout
├─ Pod/runtime/config
├─ storage
├─ Service/DNS/network
├─ policy/RBAC
└─ external dependency
```

## 25. Anti-patterny

### Iba `helm lint`

Neoverí server, policy ani runtime.

### Debug output uložený bez sanitizácie

Môže obsahovať Secrets a effective values.

### Test iba default values

Production kombinácie ostanú neoverené.

### Snapshot test bez semantic review

Veľký chybný diff sa jednoducho schváli.

### `helm test` bez timeoutu/resources

Test blokuje release workflow alebo poškodí Node.

### Ručné mazanie release Secrets

Môže poškodiť históriu a Helm state machine.

### Helm error riešený iba cez Kubernetes dashboard

Chýba release revision, values, manifest a hook evidence.

## 26. Praktický checklist

```text
[ ] správny context a namespace
[ ] Helm version a chart version/digest
[ ] dependency lock a charts directory
[ ] effective values a schema
[ ] lint a render matrix
[ ] server-side dry-run
[ ] policy/security checks
[ ] release status/history/get evidence
[ ] hooks, Jobs, Events a logs
[ ] workload rollout a probes
[ ] Service/EndpointSlice/DNS/network
[ ] PVC/storage a external dependencies
[ ] Secrets sanitizované
[ ] post-fix Helm test a SLI validation
```

## 27. Kontrolné otázky

1. Aké vrstvy má Helm testovacia pyramída?
2. Čo `helm lint` nepreukazuje?
3. Prečo treba testovať values matrix?
4. Ako odlíšiš template failure od API admission failure?
5. Čo je dobrý Helm test hook?
6. Prečo `helm test` nie je monitoring?
7. Ktoré commands ukážu release evidence?
8. Ako analyzuješ drift medzi Helm a live objektom?
9. Prečo sú debug/dry-run outputs citlivé?
10. Aký je rozdiel medzi Helm troubleshooting a Kubernetes workload troubleshooting?

## Glossary impact

Relevantné pojmy: Helm test pyramid, values test matrix, render validation, server-side chart validation, template unit test, chart test hook, release evidence, pending release state, Helm drift triage, Helm troubleshooting decision tree, ephemeral chart test cluster a chart CI pipeline.

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
