# Upgrade a rollback

Helm upgrade nie je iba zmena image tagu. Vytvorí novú release revision z konkrétneho chart artifactu, effective values, dependency graphu, capabilities a render behavioru. Následne sa pokúsi zosúladiť live Kubernetes resources s novým rendered manifestom. Rollback vytvorí ďalšiu revision podľa historického release stavu; nevracia automaticky databázu, externé API, persistentné dáta ani side effects hookov.

## 1. Release revision model

Helm release má históriu revisions:

```bash
helm history payments -n production
helm status payments -n production
```

Revision môže mať stav napríklad:

- `deployed`,
- `superseded`,
- `failed`,
- `pending-install`,
- `pending-upgrade`,
- `pending-rollback`,
- `uninstalling`.

Helm revision nie je:

- Git commit,
- chart version,
- application version,
- Deployment revision,
- databázová schema version.

Pre audit koreluj všetky identity cez annotations, labels a deployment metadata.

## 2. Upgrade inputs

Výsledok upgrade-u závisí od:

- chart artifactu alebo directory contentu,
- chart version/digest,
- dependency locku a vendored dependencies,
- values defaults,
- predchádzajúcich release values,
- nových values files a CLI overrides,
- Kubernetes API capabilities,
- live `lookup` výsledkov,
- post-renderera,
- Helm major/minor behavioru,
- target clusteru, contextu a namespace-u.

Reprodukovateľný upgrade musí všetky rozhodujúce inputs versionovať alebo zaznamenať.

## 3. Basic upgrade flow

```bash
helm upgrade payments oci://registry.example.com/charts/payments \
  --version 1.5.0 \
  -f values-production.yaml \
  --namespace production
```

Zjednodušený flow:

1. Helm načíta chart a dependencies.
2. Zostaví effective values.
3. Validuje values schema.
4. Renderuje templates.
5. Vykoná pre-upgrade hooks.
6. Aplikuje zmeny resources.
7. Podľa flags čaká na readiness/Jobs.
8. Vykoná post-upgrade hooks.
9. Zapíše release revision a status.

Failure môže nastať v každej vrstve a každá má iný rollback model.

## 4. Values pri upgrade

Najčastejšia chyba je nejasná values stratégia.

### Explicitné values files

Preferovaný release contract:

```bash
helm upgrade payments ./chart \
  -f values/common.yaml \
  -f values/production.yaml \
  --namespace production
```

Poradie je dôležité; neskorší file prepisuje skorší.

### Reuse values

```bash
helm upgrade payments ./chart \
  --reuse-values \
  --set image.tag=1.5.0
```

`--reuse-values` prenesie predchádzajúce release values a zlúči nové overrides. Riziká:

- staré keys zostanú aktívne,
- nové chart defaults sa nemusia aplikovať podľa očakávania,
- odstránené alebo premenované values vytvoria neviditeľný legacy state,
- výsledok závisí od cluster release history, nie iba od Git-u.

Production workflow má preferovať explicitný versionovaný effective configuration contract.

### Reset values

`--reset-values` začne od defaults nového chartu a aplikuje nové overrides. To môže odstrániť historické customizations.

Pred upgrade porovnaj:

```bash
helm get values payments -n production --all
helm show values <chart-reference>
```

## 5. Pre-upgrade evidence

Pred zmenou zachovaj:

```bash
helm status payments -n production
helm history payments -n production
helm get values payments -n production --all > current-values.yaml
helm get manifest payments -n production > current-manifest.yaml
helm get hooks payments -n production > current-hooks.yaml
kubectl get all,cm,secret,pvc -n production -l app.kubernetes.io/instance=payments
```

Ďalej zaznamenaj:

- aktuálny chart artifact digest,
- image digests,
- Git revision,
- databázovú schema version,
- current SLI/SLO stav,
- active incidents a capacity,
- backup status.

Release history v clustri nie je jediný disaster-recovery source.

## 6. Render a diff pred upgrade

Minimálny validation chain:

```bash
helm dependency build ./chart
helm lint ./chart -f values-production.yaml
helm template payments ./chart \
  -f values-production.yaml \
  --namespace production > rendered.yaml
kubectl apply --dry-run=server -f rendered.yaml
```

Ďalej porovnaj:

- current release manifest,
- proposed rendered manifest,
- live objects,
- immutable fields,
- selector changes,
- PVC/StorageClass zmeny,
- Service type/port changes,
- RBAC a security context,
- hooks a CRDs.

Textový YAML diff nie je plná semantic analýza. Server defaulting, admission a controller mutations môžu výsledok zmeniť.

## 7. Wait, timeout a Jobs

Podľa Helm major verzie sa konkrétne flags a wait strategy môžu líšiť. Všeobecný production contract musí definovať:

- na ktoré resources Helm čaká,
- čo znamená ready,
- či čaká na Jobs,
- operation timeout,
- application-level post-deploy validation.

Príklad pre podporovaný Helm variant:

```bash
helm upgrade payments ./chart \
  -f values-production.yaml \
  --namespace production \
  --wait \
  --wait-for-jobs \
  --timeout 15m
```

Timeout nesmie byť náhodne vysoký. Odvodzuj ho z:

- rollout strategy,
- startup probes,
- image pull času,
- hook Jobs,
- migration deadline,
- storage attach/mount času,
- capacity a autoscaling latency.

Helm wait success stále nepreukazuje end-to-end user path ani business correctness.

## 8. Automatic rollback behavior

Niektoré Helm verzie používajú `--atomic`, novšie command surfaces môžu používať explicitnejší rollback-on-failure model. Pred použitím over dokumentáciu konkrétnej Helm major verzie.

Automatický rollback môže:

- obnoviť predchádzajúci rendered manifest,
- vytvoriť rollback revision,
- odstrániť niektoré nové resources podľa flags,
- znovu spustiť rollback hooks.

Neobnoví automaticky:

- databázovú schema alebo dáta,
- messages odoslané do queue,
- external API side effects,
- DNS alebo IAM zmeny vytvorené mimo release,
- objekty vytvorené operatorom,
- manual drift,
- CRD schema/data migrácie.

Pre stateful upgrade je automatický rollback bezpečný iba pri preukázanej backward compatibility.

## 9. Manual rollback

```bash
helm history payments -n production
helm rollback payments 7 -n production --wait --timeout 15m
```

Rollback na revision `7` vytvorí novú revision. História sa neprepíše späť.

Pred rollbackom over:

- chart a values obsiahnuté v cieľovej revision,
- image availability,
- API compatibility,
- DB schema compatibility,
- Secret/certificate validity,
- hook behavior,
- či resources alebo CRDs už neboli odstránené,
- či external dependency stále podporuje starú aplikáciu.

## 10. Rollback nie je time travel

Príklad:

```text
revision 7: app 1.4 + schema 12
revision 8: pre-upgrade hook zmení schema na 13
revision 8: application rollout zlyhá
rollback: manifests sa vrátia na app 1.4
schema: zostáva 13
```

Starý application binary musí vedieť pracovať so schema 13 alebo rollback zlyhá funkčne, hoci Helm status bude `deployed`.

Používaj expand/contract migration:

```text
expand kompatibilnú schema
→ rollout novej aplikácie
→ migrácia/backfill
→ overenie
→ odstránenie starej kompatibility v neskoršom release
```

## 11. Force replacement

Flag typu `--force` môže nahradiť resource delete/recreate stratégiou. Je rizikový pri:

- Services s meniacou sa identity,
- PVC/PV,
- StatefulSets,
- immutable selectors,
- CRDs,
- resources s external controller side effects,
- objects s finalizers.

Nepoužívaj force ako univerzálnu opravu immutable-field failure. Najprv navrhni explicitný migration/decommission flow.

## 12. Cleanup on failure

Cleanup flag môže odstrániť resources vytvorené počas failed upgrade alebo rollbacku. Nevyrieši však:

- modified existing resources,
- hook side effects,
- resources bez release ownershipu,
- operators/external controllers,
- external cloud resources,
- storage data.

Cleanup scope musí byť známy pred automatizáciou.

## 13. Hooks pri rollbacku

Rollback môže spustiť:

- `pre-rollback`,
- bežné resource reconciliation,
- `post-rollback`.

Hook musí byť:

- idempotentný,
- bezpečný pri partial previous execution,
- kompatibilný s aktuálnym aj cieľovým state-om,
- auditovateľný,
- časovo ohraničený.

`--no-hooks` môže zmeniť recovery semantics. Použi ho iba vtedy, keď presne vieš, ktoré side effects tým obídeš.

## 14. CRDs a rollback

CRDs v `crds/` majú samostatný lifecycle. Helm ich bežne neupgradeuje ani bezpečne nerollbackuje ako application manifests.

Pri CRD/controller upgrade rieš:

- served/storage API versions,
- conversion webhook,
- stored-version migration,
- controller compatibility,
- rollback path,
- custom resource data backup,
- deletion policy.

Rollback chartu bez CRD compatibility môže odstaviť controller alebo znemožniť čítanie custom resources.

## 15. Stateful workloads

Pred upgrade StatefulSetu analyzuj:

- ordered/parallel rollout,
- quorum a leader election,
- version skew replík,
- PVC retention,
- storage snapshot/backup,
- schema/protocol compatibility,
- partitioned rollout,
- fencing a failover.

Helm revision nevlastní contents PVC.

## 16. Deployment rollout a Helm status

Helm upgrade a Kubernetes Deployment rollout sú dve vrstvy.

```bash
helm status payments -n production
kubectl rollout status deployment/payments -n production
kubectl get events -n production --sort-by=.metadata.creationTimestamp
```

Release môže byť failed kvôli timeoutu, hoci rollout neskôr dokončí. Alebo Helm môže command úspešne dokončiť bez plnej business readiness, ak wait contract nie je dostatočný.

## 17. Pending release states

`pending-upgrade` alebo `pending-rollback` môže vzniknúť po:

- prerušení klienta,
- Helm process crashi,
- API/network timeout-e,
- hook Job failure,
- release storage conflict-e,
- súbežnej Helm operácii.

Postup:

1. zachovaj release Secret/metadata evidence,
2. zisti poslednú úspešnú revision,
3. over live resources a hooks,
4. zisti, či operácia stále beží,
5. nepremenuj alebo nemaž release Secrets naslepo,
6. vykonaj dokumentovaný rollback alebo recovery.

Ručná editácia Helm release storage je posledná možnosť s backupom a presným version-specific postupom.

## 18. Concurrent writers

Helm, GitOps controller, manual `kubectl apply`, operator a HPA môžu meniť rovnaké resources.

Definuj:

- authoritative writer pre každý field,
- GitOps/Helm integration model,
- scaling ownership,
- admission mutation expectations,
- emergency change workflow,
- drift detection.

Rollback môže prepísať legitímnu novšiu zmenu iného writera.

## 19. Release history retention

History retention ovplyvňuje:

- dostupné rollback targets,
- namespace Secret count,
- forensic evidence,
- sensitive values/manifests exposure,
- etcd storage.

Neobmedzená história nie je automaticky správna. Zachovaj externý source chartov, values a deployment evidence aj mimo release storage.

## 20. CI/CD upgrade workflow

Odporúčaný flow:

```text
pin chart/dependencies/images
→ render všetky environment values
→ lint/schema/policy/security checks
→ server-side dry-run v kompatibilnom clustri
→ staging install/upgrade
→ Helm tests a application smoke tests
→ production canary alebo bounded rollout
→ SLI observation
→ promotion alebo explicitný rollback/roll-forward
```

Release artifact má byť rovnaký medzi prostrediami; meniť sa majú iba explicitné environment inputs.

## 21. Roll-forward vs. rollback

Preferuj rollback, keď:

- predchádzajúci stav je stále kompatibilný,
- side effects sú nulové alebo reverzibilné,
- image/artifacts sú dostupné,
- recovery je rýchlejšia a bezpečnejšia než oprava.

Preferuj roll-forward, keď:

- database/schema už nie je backward-compatible,
- external migration dokončila,
- rollback by znovu spustil nebezpečné hooks,
- stará image už nie je bezpečná alebo dostupná,
- malá oprava obnoví správny desired state s menším blast radiusom.

Rozhodnutie musí byť súčasťou release runbooku, nie improvizácia počas incidentu.

## 22. Post-upgrade validation

Over minimálne:

```bash
helm status payments -n production
helm get values payments -n production --all
kubectl rollout status deployment/payments -n production
kubectl get pods,endpointslice -n production
kubectl get events -n production --sort-by=.metadata.creationTimestamp
helm test payments -n production --logs
```

Ďalej:

- application SLI,
- error rate/latency,
- queue lag,
- DB migration status,
- resource saturation,
- security/policy denials,
- external integration.

## 23. Anti-patterny

### `--reuse-values` bez auditu

Staré hodnoty prežijú chart refactor a vytvoria neviditeľný configuration drift.

### Automatický rollback považovaný za databázový rollback

Manifests sa vrátia, durable state nie.

### `--force` na immutable-field problém

Delete/recreate môže zmeniť identity a poškodiť stateful workload.

### Upgrade bez zachovania current manifestu a values

Pri incidente chýba porovnávací baseline.

### Rollback na revision bez kontroly image availability

Starý manifest odkazuje na zmazaný alebo mutable artifact.

### Zvýšenie timeoutu ako univerzálna oprava

Skryje probe, scheduling, hook alebo capacity problém.

### Súbežný Helm a GitOps writer

Vzniká oscillation a nejasný ownership.

## 24. Troubleshooting

### Upgrade zlyhá na immutable field

Identifikuj resource a field. Navrhni migration/recreate flow s explicitným identity a data modelom; nepoužívaj force naslepo.

### Release je `pending-upgrade`

Over release history, Helm process, hooks, Jobs a release Secret. Najprv zachovaj evidence, potom vykonaj version-specific recovery.

### Rollback je successful, aplikácia nefunguje

Over database/schema, Secrets, external APIs, PVC state, image availability a rollback hooks.

### `--wait` timeoutuje

Zisti konkrétny resource: Pod readiness, PVC, Service/load balancer, Job/hook, scheduling alebo quota. Timeout je symptóm.

### Nové chart defaults sa neaplikovali

Over `--reuse-values`, predchádzajúce effective values a renamed/deprecated keys.

### Rollback zlyhá na chýbajúcom resource

Porovnaj release manifests, current live state, resource ownership a Helm version-specific behavior.

## 25. Kontrolné otázky

1. Čo tvorí input Helm upgrade-u?
2. Aký je rozdiel medzi chart version, release revision a Deployment revision?
3. Aké riziká má `--reuse-values`?
4. Čo preukazuje `--wait` a čo nepreukazuje?
5. Prečo rollback nevie automaticky vrátiť databázu?
6. Kedy je vhodný expand/contract migration model?
7. Aké riziká má force replacement?
8. Ako sa riešia CRDs pri rollbacku?
9. Kedy preferovať roll-forward namiesto rollbacku?
10. Aké evidence zachováš pred production upgrade-om?

## Glossary impact

Relevantné pojmy: Helm upgrade, effective release values, release revision, Helm rollback, rollback target, automatic rollback, pending upgrade, pending rollback, release history retention, force replacement, cleanup on failure, upgrade health gate, expand/contract migration, roll-forward a rollback compatibility.

## Oficiálna dokumentácia

- [helm upgrade](https://helm.sh/docs/helm/helm_upgrade/)
- [helm rollback](https://helm.sh/docs/helm/helm_rollback/)
- [helm history](https://helm.sh/docs/helm/helm_history/)
- [helm status](https://helm.sh/docs/helm/helm_status/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Hooks](hooks.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Helm testing a troubleshooting →](helm-testing-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
