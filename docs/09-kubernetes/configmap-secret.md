# ConfigMap a Secret

ConfigMap a Secret sú namespaced API objekty pre runtime configuration. ConfigMap je určený pre necitlivé dáta. Secret označuje citlivé bytes, ale sám osebe negarantuje encryption, least privilege, bezpečnú distribúciu, rotation ani revocation.

Configuration change je distribuovaný lifecycle. Update API objektu ešte neznamená, že nový obsah bol doručený, načítaný, validovaný a prijatý každým processom.

Dominantný lifecycle:

```text
configuration alebo credential intent
→ owner, consumer a schema inventory
→ versionovaný ConfigMap/Secret subject
→ Pod template reference a delivery method
→ kubelet projection alebo environment snapshot
→ process-loaded configuration/credential epoch
→ validation, reload alebo Pod replacement
→ readiness a business acceptance
→ credential revocation a rollback retention
→ cleanup, audit a incident closure
```

Kľúčová diagnostická otázka nie je „aká hodnota je v Secret-e?“, ale:

```text
Ktorý object UID/resourceVersion alebo immutable name bol určený pre ktorý Pod UID?
Aké bytes kubelet doručil a akú generation process reálne načítal?
Bola nová configuration prijatá a starý credential zrušený?
```

## 1. Atlas scenár

Atlas Payments release `4.2.0` používa:

```text
ConfigMap: production/payments-config-v52
configuration generation: C52
Secret: production/payments-db-se08
credential epoch: SE08
Deployment: production/payments-api generation 12
Pod replicas: 6
image digest: PAY420
```

Acceptance contract:

- rovnaký immutable image beží vo všetkých prostrediach;
- každý accepted Pod načítal presne C52 a SE08;
- config schema, endpointy a feature flags sú validné;
- žiadny Pod nepoužíva staging dependency;
- nový credential funguje a starý SE07 je po overlap window revoked;
- config/secret values sa nezobrazujú v logs, Events ani tickets;
- rollback references zostávajú dostupné počas schváleného okna;
- business synthetic prejde cez každú Pod cohortu.

## 2. Configuration subject

Pre každú zmenu zaznamenaj:

```text
source repository/secret-provider version
owner a approved intent
ConfigMap/Secret namespace, name, UID a resourceVersion
immutable flag a content digest bez plaintext secretu
key schema, required/optional fields a compatibility
consumer Deployment/StatefulSet/Job UID a generation
Pod template reference alebo checksum
Pod UIDs a creation times
delivery method: env, envFrom, volume, subPath, API fetch alebo external provider
kubelet projection generation
process-loaded configuration/credential epoch
readiness/business acceptance
old-version retention a credential revocation verdict
```

Object name bez UID/resourceVersion alebo content digest nemusí odlíšiť in-place mutation. Pod reference bez process-loaded evidence nepreukazuje effective state.

## 3. ConfigMap a Secret boundary

ConfigMap je pre necitlivé values, napríklad:

- endpoint references;
- log level;
- feature configuration;
- structured application files;
- trust bundle, ak jeho disclosure nie je citlivý.

Secret je pre citlivé bytes, napríklad:

- passwords a bearer tokens;
- private keys;
- registry credentials;
- TLS private key material;
- short-lived bootstrap credentials.

Base64 v `.data` je encoding, nie encryption. Actor s API read accessom získa plaintext význam. Secret type poskytuje čiastočný format contract, nie úplnú business alebo cryptographic validation.

## 4. Source, API object, projection a process state

Rozlišuj štyri vrstvy:

```text
source generation
→ API object generation
→ Pod-delivered generation
→ process-loaded generation
```

Príklad:

```text
external secret provider: SE08
Kubernetes Secret: payments-db-se08 UID S8
Pod P42 mount: files z S8
process metric: loaded_secret_epoch=SE07
```

Kubernetes objekty a mount sú správne, ale application stále používa cached credential SE07. Incident patrí do reload/process boundary, nie do Secret persistence boundary.

## 5. Versioned immutable model

Preferovaný production pattern:

```text
vytvor payments-config-v52 a payments-db-se08
→ validuj schema a references
→ zmeň Pod template reference/checksum
→ vytvor nové Pods
→ over loaded C52/SE08
→ prijmi rollout
→ revoke-ni SE07
→ po rollback window odstráň staré objects
```

`immutable: true` chráni object pred in-place data mutation a podporuje jednoznačný rollout subject. Nechráni pred:

- referenciou na nesprávny object;
- chybným obsahom;
- broad RBAC;
- exfiltráciou procesom;
- predčasným deletion starého rollback subjectu;
- stale external provider credentialom.

## 6. Environment injection

Pri `env`, `envFrom`, `configMapKeyRef` alebo `secretKeyRef` sa values vložia pri vytvorení container processu.

```text
Pod create
→ kubelet načíta referenced object/key
→ runtime vytvorí process environment
→ process má immutable environment snapshot
```

Neskorší update ConfigMapu alebo Secretu nemení environment existujúceho procesu. Potrebný je container/Pod replacement alebo application-specific fetch mechanizmus.

`envFrom` zväčšuje implicitný surface:

- collisions medzi keys;
- nejasný owner variables;
- nechcené sprístupnenie secretu každému containeru;
- ťažšia schema validation;
- environment dump leakage.

Pre kritické fields používaj explicitné mappings.

## 7. Volume projection

ConfigMap alebo Secret môže byť projected ako files:

```yaml
volumes:
  - name: config
    configMap:
      name: payments-config-v52
  - name: db-secret
    secret:
      secretName: payments-db-se08
containers:
  - name: payments
    volumeMounts:
      - name: config
        mountPath: /etc/payments
        readOnly: true
      - name: db-secret
        mountPath: /run/secrets/db
        readOnly: true
```

Kubelet synchronizuje projection podľa svojho change-detection a sync modelu. Aktualizácia môže byť oneskorená. Atomic directory/symlink update tiež nemusí vyvolať rovnaké filesystem events ako in-place write.

Rozlišuj:

- file bytes na mount-e;
- open file descriptor processu;
- parsed/cached application object;
- active connection alebo credential session;
- readiness a loaded-generation telemetry.

Read-only mount bráni zápisu cez daný mount. Nebráni procesu Secret prečítať, logovať alebo exfiltrovať.

## 8. `subPath` boundary

File mount cez `subPath` typicky nedostáva priebežné projected updates rovnakým spôsobom ako celý ConfigMap/Secret volume.

Hot-reload design nesmie predpokladať update, ak:

- používa `subPath`;
- application drží starý file descriptor;
- application načíta config iba pri štarte;
- watcher sleduje nesprávny inode;
- kubelet projection ešte nebola obnovená.

Pri kritických changes býva explicitný versioned Pod rollout jednoduchší a auditovateľnejší než implicitný hot reload.

## 9. Multi-file atomicity

Configuration môže obsahovať viac súborov alebo keys, ktoré musia tvoriť jednu generation:

```text
app.yaml
routes.yaml
trust.pem
feature-flags.json
```

Kubelet môže projected directory aktualizovať atomicky na filesystem úrovni, ale application môže:

- čítať files v rôznych časoch;
- cache-ovať iba časť;
- reloadnúť jeden parser a druhý nie;
- otvoriť nové connections so starým credentialom;
- prejsť readiness pred úplným validation.

Application reload protocol má načítať celú generation, validovať ju, vykonať atomic swap effective configu a reportovať loaded version.

## 10. Optional references a fallback

Optional object alebo key je bezpečný iba s explicitným fallback contractom.

Nebezpečný príklad:

```text
missing PAYMENT_ENV
→ application defaultne použije staging
→ Pod je Ready
→ production traffic ide na staging dependency
```

Pre identity, endpoints, credentials a safety flags je fail-closed startup často lepší než tichý fallback.

## 11. Permissions a container access

Secret file access závisí od:

```text
file mode
+ runtime UID/GID
+ fsGroup a supplemental groups
+ mount path ownership
+ SELinux/AppArmor
+ container-level security context
+ sidecar mount inventory
```

`defaultMode: 0400` neznamená automaticky „iba správny application process“. Over effective UID, ownership a ktoré containers majú volumeMount.

Multi-container Pod má shared Pod lifecycle, ale Secret mount môže byť obmedzený iba na konkrétny container. Nedávaj Secret sidecaru, ktorý ho nepotrebuje.

## 12. API, etcd a backup exposure

Secret je API object. Bez encryption-at-rest konfigurácie môže byť underlying etcd content uložený bez aplikačného šifrovania. Defense in depth zahŕňa:

- encryption at rest;
- TLS a access controls pre etcd;
- obmedzený API `get/list/watch`;
- ochranu etcd snapshots a support bundles;
- audit Secret accessu;
- key rotation a restore test;
- node/kubelet/runtime hardening;
- workload identity alebo external secret provider, ak je vhodný.

Encryption at rest nechráni Secret po autorizovanom API read-e, projection do Podu, načítaní do memory, výpise do logu alebo compromise Node-u.

## 13. RBAC a indirect access paths

Priamy `get secrets` nie je jediná cesta k plaintextu. Actor môže mať capability:

- vytvoriť alebo editovať Pod, ktorý Secret mountne;
- meniť Deployment/Job template;
- používať `exec` alebo debug container;
- čítať node filesystem alebo memory;
- meniť admission/webhook;
- čítať backup alebo external secret cache;
- editovať ServiceAccount s imagePullSecrets.

Authorization review musí posudzovať effective access graph, nie iba Secret verbs.

## 14. External secret delivery

Možnosti:

- synchronizovať external provider value do Kubernetes Secretu;
- CSI alebo node projection;
- runtime fetch cez workload identity;
- sidecar/agent s reload contractom;
- short-lived dynamic credential.

Pre každý model definuj:

```text
provider identity a availability
cache a offline behavior
Kubernetes API presence alebo absence
Pod startup dependency
refresh interval a loaded-state signal
rotation overlap
revocation
node compromise blast radius
audit a recovery
```

External provider odstráni časť static Secret managementu, ale pridáva runtime dependency a cache consistency problém.

## 15. Credential rotation lifecycle

Rotation nie je update jedného API objektu.

```text
vytvor/aktivuj SE08
→ distribuuj SE08
→ processy načítajú SE08
→ over nové connections a business operations
→ ponechaj bounded overlap so SE07
→ revoke-ni SE07 u authoritative providera
→ over, že SE07 zlyhá
→ odstráň staré references/caches/objects
→ audituj backup a retention
```

Ak application používa environment injection, nový Secret vyžaduje Pod replacement. Ak používa mounted file, update nestačí bez application reloadu a connection/session obnovy.

Revocation je samostatný authoritative transition. Kubernetes deletion Secretu nezruší credential u database, cloud alebo external API providera.

## 16. TLS a registry credentials

TLS Secret type nepokrýva celý PKI contract. Over:

- certificate chain a SANs;
- private-key match;
- expiry a algorithm;
- consumer namespace/reference policy;
- loaded certificate generation;
- session/reload behavior;
- old certificate/key revocation podľa PKI modelu.

`imagePullSecrets` používa kubelet/runtime pri image pull-e. Nie je to application credential. Diagnostika musí odlíšiť:

```text
registry auth subject
application runtime secret subject
ServiceAccount/API identity subject
```

## 17. Configuration rollout

ConfigMap/Secret update nie je automaticky súčasťou Deployment Pod template hash-u. Rollout trigger môže byť:

- versioned immutable object name;
- deterministic checksum annotation;
- explicit template version field;
- operator/controller, ktorý vytvára novú workload generation.

Checksum musí byť deterministický a nesmie publikovať secret plaintext. Rollout evidence má korelovať:

```text
config/secret digest
→ Deployment generation
→ Pod UIDs
→ process-loaded generation
→ readiness/business outcome
```

## 18. Rollback a retention

Application rollback môže potrebovať starú config generation, ale starý credential môže byť z bezpečnostných dôvodov revoked.

Preto odlišuj:

- application/config rollback compatibility;
- credential rollback eligibility;
- external schema/protocol compatibility;
- object retention;
- provider-side credential state;
- emergency break-glass subject.

Nevytváraj recovery plán založený na znovuaktivovaní kompromitovaného alebo expirovaného credentialu.

## 19. Worked failure: Secret sa zmenil, ale process ostal na starej epoch

Secret `payments-db` bol mutovaný in place zo SE07 na SE08. Deployment Pods používali environment injection.

```text
Secret resourceVersion sa zmení
→ existing Pod environment sa nemení
→ dashboard ukazuje nový Secret
→ application sessions stále používajú SE07
→ provider revoke-ne SE07
→ všetky staré Pods stratia database access
```

Root cause nie je iba „Pod sa nereštartoval“. Chýbal versioned credential rollout a loaded-state verification pred revocation.

## 20. Worked failure: hot reload vytvoril mixed configuration

ConfigMap obsahoval `routes.yaml` a `trust.pem`. Application watcher reloadol routes, ale TLS client držal starý trust object.

```text
filesystem projection C52
→ route parser používa C52
→ TLS layer používa C51
→ readiness kontroluje iba local listener
→ časť downstream calls zlyháva
```

File generation nie je process generation. Multi-component application potrebuje atomic reload verdict alebo Pod replacement.

## 21. Worked failure: old Secret object bol zmazaný pred rollback window

Release 4.2.0 používal `payments-db-se08`. Po rolloute automation okamžite zmazala SE07. Následný application rollback vyžadoval starý protocol client, ktorý nebol kompatibilný s SE08 credential scope.

Deletion starého Kubernetes objektu odstránilo rollback input, ale provider-side SE07 už aj tak nemusel byť bezpečný na reaktiváciu. Správny recovery design mal oddeliť artifact/config compatibility od credential rotation a pripraviť nový kompatibilný credential subject.

## 22. Worked failure: broad Pod edit permission obišlo Secret RBAC

Support role nemala `get secrets`, ale mohla vytvoriť Job v production namespace. Vytvorila Pod, ktorý mountol `payments-db-se08`, a prečítala jeho obsah.

```text
no direct Secret read
+ create Pod/Job with arbitrary volumes
→ indirect Secret materialization
```

Secret authorization musí posudzovať workload creation a debug/exec paths.

## 23. Causal troubleshooting walkthrough: polovica Podov používa SE07, polovica SE08

Po credential rotation sú tri Payments Pods funkčné a tri vracajú database authentication errors. Secret object ukazuje SE08 a Deployment je `Available=True`.

### 1. Zafixuj subject a outcome

Zaznamenaj:

```text
ConfigMap/Secret names, UIDs, resourceVersions a digests
provider credential IDs a active/revoked state
Deployment UID/generation a Pod template references/checksum
všetky Pod UIDs, creation times a imageIDs
delivery method per key: env, volume, subPath, external fetch
kubelet projection/file metadata per Node
process-loaded C/SE epoch per Pod
connection pool/session creation times
readiness a EndpointSlice targetRef UIDs
business request IDs per backend Pod
```

Secret values nevkladaj do logs alebo incident ticketu.

### 2. Competing hypotheses

1. Staré Pods používajú environment snapshot SE07.
2. Mounted volume je na niektorých Nodes ešte stale.
3. `subPath` mount nedostal update.
4. Application file watcher alebo reload zlyhal.
5. Connection pool drží sessions vytvorené so SE07.
6. Deployment rollout nebol vyvolaný, pretože checksum/reference sa nezmenili.
7. Rollout je partial a starý ReplicaSet stále prijíma traffic.
8. Admission zmenila Secret reference.
9. Niektoré Pods používajú Secret s rovnakým menom v inom namespace/clusteri.
10. External provider/CSI cache vydáva odlišnú epoch.
11. Provider revoke-ol SE07 pred loaded-state convergence.
12. Readiness neoveruje database identity ani loaded epoch.
13. Dashboard číta latest API object a nesleduje per-Pod process state.

### 3. Discriminating observation points

- live admitted Pod specs a owner revisions;
- Pod creation times vs. Secret update/rotation timeline;
- environment source metadata bez výpisu values;
- mounted file inode/symlink/mtime a digest bezpečne vypočítaný v Pode;
- `subPath` inventory;
- application loaded-generation metric;
- reload logs a validation result;
- connection/session epoch;
- external provider audit a cache version;
- EndpointSlice UIDs a per-Pod authentication failures;
- Deployment old/new ReplicaSet counts.

Observation `Secret obsahuje SE08` nepreukazuje process-loaded SE08. Observation `file digest je nový` nepreukazuje, že application ho parsovala a aktivovala.

### 4. Containment

- zastav ďalšie Secret mutation a cleanup;
- ak je bezpečné, obnov bounded overlap SE07/SE08, ale nereaktivuj kompromitovaný credential;
- odstráň failing Pods z trafficu cez readiness/EndpointSlice, nie náhodným deletion-om;
- pozastav rollout a provider revocation automation;
- zachovaj object metadata, Pod specs, reload logs a provider audit;
- neexportuj plaintext secrets;
- obmedz nové sessions a zabráň staging fallbacku.

### 5. Recovery podľa boundary

- env snapshot → vytvor reviewovaný Pod rollout na versioned Secret;
- projection lag → obnov kubelet path alebo replace-ni Pod podľa runbooku;
- subPath → zmeň delivery model alebo rollout-ni nový Pod;
- reload failure → validuj celú generation a vykonaj atomic activation;
- stale connections → drain/recreate pool po loaded credential transition;
- partial rollout → dokonči alebo rollback-ni konkrétnu Pod cohortu;
- wrong reference/admission → oprav authoritative template a admitted diff;
- external provider cache → obnov cache/identity a verify provider epoch;
- premature revocation → vytvor nový compatible credential, nie slepú reaktiváciu starého.

### 6. Over pôvodný outcome

Potvrď:

- každý accepted Pod reportuje C52 a SE08;
- Pod template, object UID/digest a process-loaded epoch tvoria jeden chain;
- všetky nové database sessions používajú SE08;
- SE07 je revoked a autentizácia s ním zlyhá;
- EndpointSlice obsahuje iba accepted Pod UIDs;
- payment authorization prejde cez každú Pod cohortu;
- žiadny Pod nepoužíva staging endpoint alebo insecure fallback;
- rollback a retention inventory je explicitný;
- žiadne plaintext secret values neunikli počas incidentu.

### 7. Posuň control skôr

Pridaj:

- immutable versioned ConfigMap/Secret names;
- schema a compatibility validation;
- deterministic rollout digest;
- per-Pod loaded config/credential epoch metric;
- readiness gate pre critical loaded state;
- rotation state machine s overlap a revoke verification;
- RBAC escalation review cez Pod/Job/debug capabilities;
- secret-safe incident tooling;
- stale `subPath` a reload integration test;
- cleanup gate podľa consumer a rollback inventory.

## 24. Observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Source | config repo/provider generation | approval, schema, credential state |
| API | ConfigMap/Secret UID/version | name, resourceVersion, immutable, digest |
| Template | workload generation | reference, checksum, admitted spec |
| Pod delivery | Pod UID + delivery method | env snapshot, mount, subPath, provider cache |
| Process | loaded config/credential epoch | parser/reload, sessions, effective values |
| Security | access graph | RBAC, Pod create, exec, node, backups |
| Rotation | old/new credential subjects | overlap, loaded state, revoke result |
| Readiness | Pod UID/EndpointSlice | accepted generation, traffic cohort |
| Cleanup | object/provider retention | consumers, rollback, deletion/revocation |
| Business | request/operation ID | endpoint, auth, invariant, forbidden fallback |

## 25. Referenčné príkazy

```bash
kubectl get configmap <name> -n <namespace> -o yaml
kubectl get secret <name> -n <namespace> -o yaml
kubectl get pod <pod> -n <namespace> -o yaml
kubectl describe pod <pod> -n <namespace>
kubectl get deployment <name> -n <namespace> -o yaml
kubectl get endpointslice -n <namespace> -o yaml
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Pri Secret diagnostike preferuj metadata, digests, versions a provider IDs. Plaintext nevypisuj do logs ani odpovede.

## 26. Referenčné pravidlá

- ConfigMap je pre necitlivé dáta; Secret označuje citlivé bytes.
- Base64 nie je encryption.
- Source, API object, Pod-delivered a process-loaded generation sú odlišné states.
- Environment injection je process-create snapshot.
- File projection update nepreukazuje application reload.
- `subPath` komplikuje live updates.
- Immutable versioned objects zlepšujú rollout identity, nie content correctness.
- Encryption at rest nechráni authorized runtime disclosure.
- Secret access graph zahŕňa Pod create, exec, node a backup capabilities.
- Rotation nie je dokončená bez loaded-state verification a old-credential revocation.
- Kubernetes deletion Secretu nezruší provider credential.
- Rollback configu a rollback credentialu majú odlišnú eligibility.
- Recovery musí overiť process-loaded state, traffic cohort a forbidden old/fallback outcomes.

## 27. Kontrolné otázky

1. Aký lifecycle spája configuration intent s process-loaded effective state-om?
2. Ako sa líšia ConfigMap a Secret z pohľadu threat modelu?
3. Prečo update Secretu nemení environment existujúceho procesu?
4. Čo file projection update preukazuje a čo nie?
5. Prečo `subPath` nie je vhodný pre očakávaný hot reload?
6. Aké indirect access paths môžu odhaliť Secret bez `get secrets`?
7. Čo musí obsahovať credential rotation state machine?
8. Prečo deletion Secret objektu nie je revocation?
9. Ako odlíšiš API object generation od process-loaded generation?
10. Čo musí configuration/secret acceptance verdict overiť?

## Glossary impact

Relevantné pojmy: configuration lifecycle subject, ConfigMap generation subject, Secret credential subject, configuration source generation, Pod-delivered configuration, process-loaded configuration epoch, environment-snapshot boundary, projection generation, subPath staleness boundary, atomic configuration reload, configuration rollout digest, secret access graph, credential rotation subject, credential revocation verdict, rollback credential eligibility, configuration observation matrix a configuration acceptance verdict.

## Oficiálna dokumentácia

- [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Good practices for Kubernetes Secrets](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
- [Encrypting confidential data at rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Job a CronJob](job-cronjob.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: ServiceAccount →](serviceaccount.md)
<!-- KNOWLEDGE-NAVIGATION:END -->