# SecurityContext a Pod Security

Kubernetes `securityContext` definuje runtime privilege a filesystem identity pre Pod alebo konkrétny container. Pod Security Standards (PSS) definujú štandardizované policy profily a Pod Security Admission (PSA) ich môže vynucovať na namespace úrovni. Tieto mechanizmy sú defense in depth; nenahrádzajú bezpečný image, kernel patching, runtime sandbox, RBAC, NetworkPolicy ani secret management.

## 1. Pod-level a container-level security context

Pod-level príklad:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 20001
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: web
      image: example/web:1
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
```

Pod-level fields sa aplikujú na Pod alebo poskytujú default pre containers podľa konkrétneho field-u. Container-level hodnota má pri prekrývajúcich sa fields typicky prednosť pre daný container.

## 2. `runAsUser`, `runAsGroup` a `runAsNonRoot`

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  runAsGroup: 10001
```

- `runAsUser` nastavuje numeric UID procesu,
- `runAsGroup` primary GID,
- `runAsNonRoot` odmietne startup, ak runtime nevie potvrdiť non-root identity alebo image smeruje na root.

`runAsNonRoot: true` je policy guard, nie náhrada za explicitne pripravený non-root image.

## 3. Image user a numeric identity

Dockerfile môže obsahovať:

```dockerfile
USER 10001:10001
```

Kubernetes security context môže hodnotu prepísať. Runtime však stále potrebuje:

- čitateľné application files,
- zapisovateľné explicitné paths,
- správny ownership volumes,
- možnosť bindnúť potrebné ports,
- kompatibilný entrypoint.

Numeric UID/GID znižuje ambiguity oproti menu, ktoré nemusí existovať v minimalistickom image-i.

## 4. `fsGroup`

`fsGroup` ovplyvňuje group ownership alebo access na podporovaných mounted volumes:

```yaml
spec:
  securityContext:
    fsGroup: 20001
    fsGroupChangePolicy: OnRootMismatch
```

Kubelet alebo CSI driver môže upraviť group ownership/permissions podľa volume typu a driver capabilities.

Riziká:

- rekurzívna zmena veľkého volume-u spomalí Pod startup,
- shared volume môže dostať širší group access,
- nie každý driver/filesystem implementuje rovnaké semantics,
- `fsGroup` nie je application locking ani tenant isolation.

## 5. Supplemental groups

Pod môže definovať ďalšie groups pre filesystem access. Široké alebo implicitne zlúčené groups môžu sprístupniť files, ktoré workload nemá čítať.

Pri platformách podporujúcich prísnejšie supplemental-group policy over:

- Kubernetes verziu,
- feature gate/stability,
- runtime support,
- image `/etc/group` behavior.

Nezakladaj bezpečnostný model na neoverenom implicitnom group membership-e.

## 6. Linux capabilities

Root privileges možno rozdeliť na capabilities.

```yaml
securityContext:
  capabilities:
    drop:
      - ALL
    add:
      - NET_BIND_SERVICE
```

Odporúčaný model:

1. drop `ALL`,
2. pridaj iba capability, ktorú aplikácia reálne potrebuje,
3. over effective capabilities v runtime,
4. odstráň capability po zmene application designu.

Capability je významná kernel privilege. `NET_ADMIN`, `SYS_ADMIN`, `SYS_PTRACE` a podobné capabilities môžu výrazne rozšíriť attack surface.

## 7. `allowPrivilegeEscalation`

```yaml
securityContext:
  allowPrivilegeEscalation: false
```

Na Linuxe súvisí s `no_new_privs` a bráni procesu získať viac privileges cez mechanizmy ako setuid binaries.

Nemusí mať očakávaný efekt pri privileged containeri alebo pri capabilities, ktoré menia runtime semantics. Over výsledný OCI/runtime config.

## 8. Privileged container

```yaml
securityContext:
  privileged: true
```

Privileged container získava veľmi široký prístup k host kernelu, devices a security controls. Je často prakticky host-root-equivalent podľa ďalších mounts a namespace nastavení.

Použitie musí byť výnimočné, auditované a izolované. Bežná aplikácia privileged mode nepotrebuje.

## 9. Read-only root filesystem

```yaml
securityContext:
  readOnlyRootFilesystem: true
```

Aplikácia potom potrebuje explicitné writable mounts:

```yaml
volumeMounts:
  - name: tmp
    mountPath: /tmp
volumes:
  - name: tmp
    emptyDir: {}
```

Read-only root filesystem:

- znižuje runtime mutation,
- komplikuje persistence malware-u,
- odhaľuje skryté write dependencies,
- nenahrádza image integrity ani volume access control.

## 10. Seccomp

```yaml
securityContext:
  seccompProfile:
    type: RuntimeDefault
```

Seccomp obmedzuje dostupné Linux syscalls.

Typy zahŕňajú:

- `RuntimeDefault`,
- `Localhost`,
- `Unconfined`.

`RuntimeDefault` závisí od runtime implementation a verzie. Local profiles potrebujú distribúciu na Nodes a lifecycle management.

Pri seccomp denial sleduj runtime, kernel audit a application behavior; obyčajný exit code nemusí jasne ukázať blokovaný syscall.

## 11. AppArmor

AppArmor profile obmedzuje file, capability, network a ďalšie operations podľa host podpory a profile configuration.

Moderný Kubernetes API model môže používať security context fields podľa podporovanej verzie; staršie integrácie používali annotations. Pri authoringu vždy over cluster verziu a runtime/Node support.

AppArmor profile musí existovať na Node-e alebo byť spravovaný platformovou distribúciou. Inak môže Pod zlyhať alebo bežať s iným profilom podľa policy.

## 12. SELinux

SELinux security options môžu nastaviť label context:

```yaml
securityContext:
  seLinuxOptions:
    type: container_t
```

Reálny význam závisí od host policy, runtime a storage labels. Nesprávny SELinux context sa často prejaví ako `permission denied` aj pri správnych Unix mode bits.

Nepoužívaj globálne vypnutie SELinux ako bežnú opravu; analyzuj audit denial a oprav policy alebo mount labeling.

## 13. Sysctls

```yaml
securityContext:
  sysctls:
    - name: net.ipv4.ip_local_port_range
      value: "1024 65535"
```

Kubernetes rozlišuje safe a unsafe sysctls podľa namespacingu a Node konfigurácie. Unsafe sysctls môžu ovplyvniť host alebo iné workloads a vyžadujú explicitné kubelet povolenie.

Sysctl patrí do platformového contractu, nie do náhodného application tuningu bez load testu.

## 14. Host namespaces

Citlivé Pod fields:

```yaml
spec:
  hostNetwork: true
  hostPID: true
  hostIPC: true
```

Dôsledky:

- zdieľanie host network namespace,
- viditeľnosť host procesov,
- zdieľanie IPC resources,
- menšia isolation a väčší lateral-movement potenciál.

Host namespace access povoľuj iba systémovým workloadom s jasným dôvodom.

## 15. `hostPath`, devices a runtime sockets

`hostPath` môže sprístupniť host filesystem:

```yaml
volumes:
  - name: host-data
    hostPath:
      path: /var/lib/example
      type: Directory
```

Rizikové paths:

- `/`,
- `/etc`,
- `/var/lib/kubelet`,
- runtime sockets,
- container image stores,
- `/proc`, `/sys`, `/dev`,
- cloud credentials alebo host logs.

Read-only mount stále môže sprístupniť credentials alebo citlivé host informácie.

## 16. Proc mount a masked paths

Runtime štandardne maskuje alebo nastavuje read-only vybrané `/proc` a system paths. Uvoľnenie `procMount` alebo related controls môže sprístupniť host/kernel informácie a escape primitives.

Použitie musí prejsť security review a Pod Security policy kontrolou.

## 17. Windows workloads

Mnohé Linux-specific fields nemajú na Windows rovnaký význam:

- Linux capabilities,
- seccomp,
- SELinux,
- AppArmor,
- UID/GID a `fsGroup`.

Windows používa vlastné identity a host-process controls. Pod Security Standards majú OS-aware pravidlá, ale policy a manifests musia explicitne zohľadniť `spec.os.name` a cluster verziu.

## 18. Pod Security Standards

Kubernetes definuje tri profily:

### Privileged

Takmer bez obmedzení; určený pre dôveryhodné systémové workloads.

### Baseline

Blokuje známe nebezpečné privilege escalations a host access, pričom zachováva širšiu kompatibilitu.

### Restricted

Silnejší hardening profil, ktorý vyžaduje non-root model, seccomp a obmedzené capabilities podľa aktuálnej verzie štandardu.

PSS je versionovaný policy contract. `latest` sa môže pri cluster upgrade sprísniť, preto produkčné namespaces často pinujú verziu a upgrade testujú.

## 19. Pod Security Admission

PSA je built-in admission controller. Namespace labels určujú režim:

```yaml
metadata:
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: v1.36
    pod-security.kubernetes.io:audit: restricted
    pod-security.kubernetes.io/audit-version: v1.36
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: v1.36
```

Režimy:

- `enforce` — odmietne nevyhovujúci Pod admission,
- `audit` — zaznamená violation do audit annotations,
- `warn` — vráti warning klientovi.

Verziu v príklade prispôsob reálnej podporovanej verzii clusteru.

## 20. Rollout Pod Security policy

Bezpečný postup:

1. inventarizuj workloads,
2. zapni `warn` a `audit`,
3. oprav manifests a images,
4. testuj controller-generated Pods, Jobs a upgrades,
5. pinuj standard version,
6. zapni `enforce`,
7. monitoruj denied admissions,
8. pravidelne posúvaj policy version.

Priamy prechod na Restricted môže odstaviť system DaemonSets, storage/network plugins alebo legacy aplikácie.

## 21. Namespace výnimky

Niektoré platformové workloads potrebujú privileged access. Izoluj ich do samostatných namespaces s:

- prísnym RBAC,
- obmedzeným repository/deployment accessom,
- NetworkPolicy,
- auditom,
- dedicated Nodes podľa threat modelu,
- explicitným ownerom a exception expiry.

`privileged` namespace nesmie byť všeobecné miesto na obchádzanie policy.

## 22. PodSecurityPolicy je odstránené

Legacy `PodSecurityPolicy` API bolo deprecated a odstránené z Kubernetes. Moderný model používa Pod Security Admission alebo external admission policy engines.

Pri migrácii treba oddeliť:

- štandardné PSS controls,
- custom image/registry/hostPath/capability policy,
- mutation/defaulting,
- exceptions a audit.

PSA nie je plná náhrada každého historického PSP use case-u.

## 23. Custom admission policy

PSS nepokrýva všetky organizational controls, napríklad:

- povolené registries,
- digest pinning,
- mandatory resource requests,
- zákaz konkrétnych `hostPath`,
- workload identity labels,
- TLS alebo backup policy.

Doplniť ich možno cez:

- ValidatingAdmissionPolicy,
- validating/mutating admission webhooks,
- policy engines.

Admission dependency musí mať HA, timeout, fail-open/fail-closed rozhodnutie a upgrade compatibility.

## 24. RuntimeClass a sandbox

SecurityContext a PSS neznamenajú silný tenant sandbox. Pre nedôveryhodný code zváž:

- sandboxed runtime,
- microVM,
- dedicated Nodes,
- oddelený cluster,
- hardware/VM isolation.

RuntimeClass vyberá runtime handler, ale potrebuje scheduling, overhead a Node support model.

## 25. Debugging a ephemeral containers

Ephemeral debug container môže mať prístup k Pod namespaces a mounted data podľa konfigurácie. Prístup k `pods/ephemeralcontainers` je citlivá RBAC capability.

Debugging nesmie automaticky obísť:

- Pod Security,
- image allowlist,
- audit,
- production change control,
- secret handling.

Minimalistický production image neospravedlňuje permanentný privileged debug sidecar.

## 26. Observability

```bash
kubectl get pod -n production <pod> -o yaml
kubectl describe pod -n production <pod>
kubectl get events -n production --sort-by=.metadata.creationTimestamp
kubectl get namespace production --show-labels
kubectl auth can-i create pods -n production
```

Na Node-e sleduj podľa prístupu:

- kubelet/runtime logs,
- kernel audit log,
- seccomp/AppArmor/SELinux denials,
- effective UID/GID/capabilities,
- mount options a file labels.

## 27. Troubleshooting

### `runAsNonRoot` odmietne image

Image používa root alebo runtime nevie určiť non-root user. Nastav numeric `USER` a explicitný `runAsUser`.

### Read-only root filesystem rozbije aplikáciu

Identifikuj write paths a pripoj bounded `emptyDir`, volume alebo tmpfs. Nevracaj celý root filesystem na writable bez analýzy.

### Volume má `permission denied`

Over UID/GID, `fsGroup`, CSI behavior, ownership, SELinux/AppArmor a read-only mount.

### Pod je rejected PSA

Prečítaj admission warning/error, porovnaj namespace labels a PSS version, oprav konkrétny field; nepresúvaj workload automaticky do privileged namespace.

### Capability drop rozbije bind port

Použi vyšší port alebo pridaj iba `NET_BIND_SERVICE`, ak je to skutočne potrebné.

### Seccomp spôsobí runtime failure

Získaj syscall/audit evidence, over runtime default profile a application dependency. Neprepínaj plošne na `Unconfined`.

## 28. Anti-patterny

### `privileged: true` ako rýchla oprava permissions

Odstraňuje veľkú časť isolation namiesto opravy ownershipu alebo capability.

### `runAsUser: 0` s `runAsNonRoot: true`

Manifest si protirečí a admission/runtime ho odmietne.

### `chmod 777` na volume

Maskuje identity a policy chybu a zvyšuje write exposure.

### Read-only root bez explicitných writable paths

Aplikácia zlyhá pri logs, cache, PID alebo temp files.

### PSS `latest` bez upgrade testov

Nová minor verzia môže zmeniť policy výsledok.

### Privileged namespace dostupný application tímom

Výnimka sa stane trvalým bypassom security governance.

### SecurityContext považovaný za VM isolation

Containers stále zdieľajú host kernel.

## 29. Kontrolné otázky

1. Aký je rozdiel medzi Pod a container security contextom?
2. Čo rieši `runAsNonRoot` a čo nerieši?
3. Načo slúži `fsGroup`?
4. Prečo je vhodné dropnúť všetky capabilities?
5. Čo mení `allowPrivilegeEscalation: false`?
6. Ako sa líši seccomp, AppArmor a SELinux?
7. Aké sú tri Pod Security Standards profily?
8. Ako sa líši `enforce`, `audit` a `warn` v PSA?
9. Prečo PSS version pinning patrí do upgrade stratégie?
10. Kedy shared-kernel container potrebuje silnejší sandbox alebo VM boundary?

## Glossary impact

Relevantné pojmy: Kubernetes SecurityContext, `runAsNonRoot`, `runAsUser`, `runAsGroup`, `fsGroup`, supplemental groups, Linux capabilities, `allowPrivilegeEscalation`, privileged container, read-only root filesystem, seccomp profile, AppArmor profile, SELinux options, safe sysctl, host namespace, Pod Security Standards, Privileged/Baseline/Restricted profile, Pod Security Admission, enforce/audit/warn mode, policy version pinning a privileged namespace exception.

## Oficiálna dokumentácia

- [Configure a Security Context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
- [Enforcing Pod Security Standards](https://kubernetes.io/docs/setup/best-practices/enforcing-pod-security-standards/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: RBAC](rbac.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: ResourceQuota a LimitRange →](resourcequota-limitrange.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
