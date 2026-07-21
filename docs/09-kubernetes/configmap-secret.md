# ConfigMap a Secret

ConfigMap a Secret sú namespaced Kubernetes API objekty, ktoré oddeľujú runtime configuration od container image-u a Pod template-u. ConfigMap je určený pre necitlivé konfiguračné dáta. Secret je určený pre citlivé hodnoty, ale samotné uloženie do Secret objektu automaticky neznamená šifrovanie, bezpečnú distribúciu ani správny lifecycle credentials.

## 1. Prečo configuration oddeliť od image-u

Rovnaký immutable image má byť použiteľný vo viacerých prostrediach. Prostredie dodáva:

- endpointy a feature configuration,
- log level a runtime flags,
- certificates a trust bundles,
- credentials alebo references na external secret provider,
- environment-specific files.

Bez oddelenia configuration vzniká:

- rebuild image-u pri každej environment zmene,
- environment drift medzi artifacts,
- vyššie riziko vloženia secretov do image layers,
- nejasný rollout a rollback configuration.

ConfigMap a Secret sú API resources, nie iba YAML fragments. Majú vlastnú identity, resourceVersion, RBAC a lifecycle.

## 2. ConfigMap

ConfigMap uchováva necitlivé key/value dáta.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-config
  namespace: production
data:
  LOG_LEVEL: info
  app.yaml: |
    server:
      port: 8080
    featureX: false
binaryData:
  banner.bin: AAEC
```

ConfigMap nemá bežné pole `spec`. Obsahuje najmä:

- `data` — UTF-8 string hodnoty,
- `binaryData` — base64 reprezentované binary hodnoty,
- `immutable` — voliteľný immutable contract.

ConfigMap nie je vhodný pre passwords, private keys, bearer tokens ani iné hodnoty, ktorých disclosure predstavuje bezpečnostný incident.

## 3. Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: database-credentials
  namespace: production
type: Opaque
stringData:
  username: app
  password: replace-me
```

Relevantné polia:

- `data` — base64-encoded bytes,
- `stringData` — write convenience pre stringy; API server ich prevedie do `data`,
- `type` — význam alebo očakávaná štruktúra Secretu,
- `immutable` — zákaz neskoršej zmeny dát.

Base64 je encoding, nie encryption. Ktokoľvek s read prístupom k Secret objektu môže hodnoty dekódovať.

## 4. Secret types

Bežné typy:

- `Opaque` — všeobecné secret dáta,
- `kubernetes.io/tls` — typicky `tls.crt` a `tls.key`,
- `kubernetes.io/dockerconfigjson` — registry authentication,
- `kubernetes.io/basic-auth`,
- `kubernetes.io/ssh-auth`,
- bootstrap alebo service-account-related typy pre platformové mechanizmy.

`type` nie je plnohodnotný schema validator pre každú business hodnotu. Application stále potrebuje validovať obsah, formát, certifikát, expiry a vzájomnú konzistenciu fields.

## 5. Spôsoby použitia v Pode

ConfigMap alebo Secret môže byť použitý cez:

1. jednotlivé environment variables,
2. `envFrom`,
3. command/args interpolation cez environment,
4. mounted volume files,
5. projected volume spolu s ďalšími sources,
6. image pull authentication pri Secret-e.

### Jednotlivá environment variable

```yaml
spec:
  containers:
    - name: app
      image: example/app:1
      env:
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: web-config
              key: LOG_LEVEL
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: password
```

### `envFrom`

```yaml
spec:
  containers:
    - name: app
      envFrom:
        - configMapRef:
            name: web-config
        - secretRef:
            name: database-credentials
```

`envFrom` je stručné, ale zväčšuje implicitný configuration surface. Collision názvov, neplatné environment names a nejasný ownership sa diagnostikujú horšie. Pre kritické fields preferuj explicitné mappingy.

### Volume projection

```yaml
spec:
  volumes:
    - name: app-config
      configMap:
        name: web-config
        items:
          - key: app.yaml
            path: app.yaml
    - name: database-secret
      secret:
        secretName: database-credentials
        defaultMode: 0400
  containers:
    - name: app
      volumeMounts:
        - name: app-config
          mountPath: /etc/example
          readOnly: true
        - name: database-secret
          mountPath: /run/secrets/database
          readOnly: true
```

Volume files umožňujú:

- zachovať file-oriented application contract,
- oddeliť citlivé hodnoty od environment dumpov,
- pozorovať aktualizácie cez filesystem podľa kubelet projection semantics,
- nastaviť filenames a modes.

Mount read-only nezabráni procesu hodnotu prečítať alebo exfiltrovať.

## 6. Environment updates

Environment variables sú skopírované pri vytvorení container procesu. Zmena ConfigMapu alebo Secretu:

- nezmení environment už bežiaceho procesu,
- typicky vyžaduje nový Pod alebo restart/recreate workloadu,
- nemusí byť application okamžite viditeľná ani pri mounted file, ak application nereaduje file znovu.

Pre Deployment sa často používa checksum annotation nad configuration contentom:

```yaml
spec:
  template:
    metadata:
      annotations:
        config.example.com/checksum: "<hash>"
```

Zmena hashu zmení Pod template a vytvorí riadený rollout. Hash musí byť deterministický a nesmie zverejniť secret value.

## 7. Mounted-file updates

Kubelet periodicky synchronizuje projected ConfigMap/Secret volume content. Aktualizácia nie je instantná a application potrebuje explicitný reload model.

Dôležité hranice:

- file projection sa môže zmeniť až po kubelet sync/cache intervale,
- application môže mať file otvorený alebo content cachovaný,
- mount cez `subPath` typicky nedostáva priebežné projection updates,
- atomic symlink-based update môže mať odlišné filesystem event semantics než in-place write,
- multi-file configuration môže potrebovať application-level transactional reload.

Najbezpečnejší model je často versionovaný rollout nových Podov namiesto nepozorovaného hot reloadu.

## 8. Immutable ConfigMap a Secret

```yaml
immutable: true
```

Výhody:

- zabráni accidental in-place mutation,
- znižuje počet watch/update operácií pre kubelet pri veľkom množstve references,
- podporuje versioned-name a immutable rollout model.

Zmenu vykonáš vytvorením nového objektu, napríklad:

```text
web-config-v17
```

Potom zmeníš Pod template reference a rolloutuješ workload. Starý objekt odstráň až po overení, že ho nič nepoužíva a rollback window skončilo.

## 9. Optional references

ConfigMap/Secret source alebo konkrétny key môže byť označený ako optional. To je vhodné iba tam, kde application má jednoznačný bezpečný fallback.

Chýbajúci required object/key spôsobí, že Pod alebo container nemôže korektne začať. Events typicky ukážu missing ConfigMap/Secret/key.

Tichý fallback na insecure alebo production-nevhodný default je horší než explicitný startup failure.

## 10. File modes a ownership

`defaultMode` používa Unix permission bits zapisované v YAML ako octal-style hodnota podľa parsera a manifest formátu.

```yaml
defaultMode: 0400
```

Permissions treba vyhodnotiť spolu s:

- runtime UID/GID,
- `fsGroup`,
- container security contextom,
- read-only root filesystemom,
- SELinux/AppArmor policy,
- application userom.

Secret volume nie je automaticky dostupný iba rootovi. Over výsledné ownership a permissions v reálnom runtime prostredí.

## 11. Secret storage v etcd

Secret objekty sú Kubernetes API dáta. Bez explicitnej encryption-at-rest konfigurácie môžu byť hodnoty v underlying etcd uložené bez aplikačného šifrovania.

Defense-in-depth model:

- zapni encryption at rest pre Secrets a ďalšie citlivé resources,
- chráň etcd transport a disk,
- obmedz API read/list/watch cez RBAC,
- obmedz prístup k etcd backupom,
- audituj Secret access,
- rotuj encryption provider keys podľa testovaného postupu,
- chráň kubelet/node filesystem a memory,
- používaj external secret provider alebo workload identity tam, kde je to vhodné.

Encryption at rest nerieši disclosure cez API, Pod memory, logs, `exec`, debug tooling alebo kompromitovaný Node.

## 12. RBAC a least privilege

Read prístup k Secretu je prístup k plaintext významu jeho dát.

Vyhýbaj sa:

- cluster-wide `get/list/watch secrets` pre application identity,
- broad edit právam nad Podmi v namespace, pretože actor môže vytvoriť Pod, ktorý Secret mountne,
- zdieľaniu jedného Secretu medzi nesúvisiacimi workloadmi,
- ukladaniu secretov do annotations alebo ConfigMaps.

Posudzuj nielen priame Secret verbs, ale aj escalation paths cez Pods, Deployments, Jobs, admission alebo node access.

## 13. Secret delivery alternatívy

Možnosti:

- Kubernetes Secret synchronizovaný z external secret managera,
- CSI Secrets Store alebo obdobná node projection integrácia,
- application runtime fetch cez workload identity,
- short-lived dynamic credentials,
- sidecar/agent s controlled refresh contractom.

Trade-offy:

- availability external providera,
- startup dependency,
- cache a rotation behavior,
- audit trail,
- blast radius identity,
- secret presence v Kubernetes API,
- behavior počas network partition.

## 14. Rotation

Credential rotation nie je iba update Secret objektu.

Potrebuješ:

1. vytvoriť alebo aktivovať nový credential,
2. distribuovať ho workloadom,
3. overiť, že nové Pods/processes ho používajú,
4. zachovať krátke overlap obdobie, ak systém podporuje dual credentials,
5. zrušiť starý credential,
6. overiť, že starý credential už nefunguje,
7. odstrániť staré API objects, caches a backups podľa retention policy.

Pri environment injection musí rotation typicky vytvoriť nové Pods.

## 15. Registry credentials

```yaml
spec:
  imagePullSecrets:
    - name: registry-auth
```

`imagePullSecrets` používa kubelet/runtime pri image pull-e. Neodovzdáva automaticky credentials application procesu.

Riziká:

- credential s príliš širokým registry scope,
- long-lived password namiesto short-lived identity,
- Secret v nesprávnom namespace,
- prepojenie cez ServiceAccount bez jasného ownershipu,
- leakage do support bundle alebo Git-u.

## 16. TLS Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: web-tls
type: kubernetes.io/tls
data:
  tls.crt: <base64>
  tls.key: <base64>
```

Typický consumer môže byť Ingress/Gateway controller alebo application Pod. Over:

- certificate chain,
- private-key match,
- SAN names,
- expiry,
- key algorithm support,
- reload/rotation behavior,
- namespace/reference policy.

Kubernetes type nekontroluje celý PKI trust contract.

## 17. Configuration versioning

Odporúčaný GitOps model:

- necitlivé ConfigMaps sú generované z versionovaného source-u,
- secret values nie sú plaintext v Git-e,
- object names alebo Pod annotations nesú content version/hash,
- rollout je explicitný,
- rollback zahŕňa application aj configuration compatibility,
- staré verzie majú retention a cleanup policy.

ConfigMap update bez workload rollout evidence vytvára ťažko auditovateľný runtime mix.

## 18. Observability

```bash
kubectl get configmap web-config -o yaml
kubectl get secret database-credentials -o yaml
kubectl describe pod <pod>
kubectl get events --field-selector involvedObject.name=<pod>
kubectl exec <pod> -- ls -l /etc/example /run/secrets/database
kubectl rollout status deployment/<name>
```

Pri Secret-e nevypisuj hodnoty do incident ticketu alebo logs. Zaznamenaj:

- object name a UID,
- resourceVersion,
- key names bez hodnôt,
- consumer workload revision,
- mount/env source,
- rollout time,
- credential version alebo external reference.

## 19. Troubleshooting

### Pod hlási missing ConfigMap alebo Secret

Over namespace, name, key, optional flag, admission a workload Pod template.

### ConfigMap sa zmenil, application používa starú hodnotu

Zisti, či ide o environment alebo volume. Pri environment vytvor nový Pod. Pri volume over kubelet sync, `subPath`, application cache/reload a mounted path.

### Secret file má `permission denied`

Over runtime UID/GID, mode, `fsGroup`, security context, LSM policy a mount path.

### Deployment sa po zmene configuration nereštartoval

ConfigMap/Secret object nie je automaticky súčasťou Pod template hash-u. Použi versioned reference, checksum annotation alebo explicitný rollout mechanismus.

### Image pull zlyhá napriek existujúcemu Secretu

Over Secret type/content, namespace, `imagePullSecrets`, ServiceAccount linkage, registry host match, credential scope, TLS a Node-to-registry connectivity.

### Secret sa nedá bezpečne rotovať

Application možno nepodporuje reload alebo dual credentials. Navrhni recreate rollout, overlap window a revoke verification.

## 20. Anti-patterny

### Secret v Git-e zakódovaný base64

Base64 nemení plaintext threat model.

### Jeden shared Secret pre celý namespace

Zväčšuje blast radius a komplikuje rotation/audit.

### `envFrom` pre desiatky nesúvisiacich fields

Vytvára implicitný, collision-prone contract.

### Mutable ConfigMap bez rollout mechanizmu

Bežia rôzne configuration verzie bez jasnej revision identity.

### Hot reload bez validation a rollbacku

Application môže prejsť do čiastočne platného stavu.

### Secret values v logs alebo health endpointoch

Kubernetes Secret neposkytuje ochranu po načítaní application procesom.

### Broad `list/watch secrets`

Umožňuje hromadnú exfiltráciu v namespace alebo clustri.

## 21. Kontrolné otázky

1. Aký je rozdiel medzi ConfigMapom a Secretom?
2. Prečo base64 nie je encryption?
3. Ako sa líši environment injection od volume projection pri aktualizácii?
4. Prečo `subPath` komplikuje live update configuration?
5. Načo slúži `immutable: true`?
6. Prečo zmena ConfigMapu automaticky nespustí Deployment rollout?
7. Aké escalation paths existujú aj bez priameho `get secrets` oprávnenia?
8. Čo všetko musí zahŕňať credential rotation?
9. Prečo encryption at rest nerieši runtime disclosure?
10. Ako diagnostikuješ workload, ktorý používa starú configuration verziu?

## Glossary impact

Relevantné pojmy: ConfigMap, Secret, `data`, `binaryData`, `stringData`, immutable ConfigMap/Secret, environment injection, volume projection, projected configuration update, `subPath` update limitation, configuration checksum, Secret encryption at rest, secret rotation, imagePullSecret, TLS Secret a external secret provider.

## Oficiálna dokumentácia

- [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Good practices for Kubernetes Secrets](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
- [Encrypting confidential data at rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
