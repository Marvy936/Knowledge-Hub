# SecurityContext a Pod Security

Kubernetes workload security nevzniká jedným fieldom `runAsNonRoot`. Pod a container SecurityContext skladajú process credentials, capabilities, seccomp, filesystem ownership, privilege escalation a host namespace exposure. Pod Security Admission potom kontroluje, či admitted Pod spĺňa namespace policy level. Skutočný runtime verdict ešte závisí od image, container runtime, kernel, SELinux/AppArmor a mountov.

Pre `payments-api` chceme non-root process, read-only root filesystem, žiadne Linux capabilities, default runtime seccomp a žiadne host namespaces alebo hostPath. Aplikácia smie zapisovať iba do bounded `emptyDir` a persistentného volume-u. Security contract musí prejsť admission aj runtime a zároveň nesmie rozbiť readiness alebo graceful termination.

## Pod-level SecurityContext

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 65532
    runAsGroup: 65532
    fsGroup: 65532
    seccompProfile:
      type: RuntimeDefault
```

Pod-level values poskytujú defaults pre containers a volume-related settings. Container-level SecurityContext môže vybrané hodnoty prepísať.

`runAsNonRoot: true` žiada runtime, aby odmietol spustenie ako UID 0. Ak image používa numeric non-root `USER`, contract je jednoznačnejší. Image s textovým userom alebo bez metadata môže viesť k runtime validácii, ktorú treba testovať.

## Container-level hardening

```yaml
containers:
  - name: api
    image: registry.example.com/atlas/payments-api@sha256:payments420
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
          - ALL
```

`allowPrivilegeEscalation: false` nastavuje `no_new_privs`-like boundary podľa runtime semantics a zabraňuje získaniu vyšších privileges cez exec transitions. Neodstraňuje už pridelené capabilities ani access k mountom.

`readOnlyRootFilesystem` chráni image rootfs pred runtime zápisom. Aplikácia musí dostať explicitné writable paths:

```yaml
volumeMounts:
  - name: tmp
    mountPath: /tmp
  - name: data
    mountPath: /var/lib/payments

volumes:
  - name: tmp
    emptyDir:
      medium: Memory
      sizeLimit: 64Mi
```

Read-only root bez pripraveného `/tmp`, cache alebo certificate path môže application rozbiť. Oprava nemá byť plošné vypnutie hardeningu, ale explicitný writable contract.

## Capabilities

Linux capabilities rozdeľujú časť root authority. Web aplikácia na porte 8080 typicky nepotrebuje žiadnu.

```yaml
capabilities:
  drop: ["ALL"]
```

Ak process musí bindovať privileged port podľa platform contractu, môže dostať úzku capability `NET_BIND_SERVICE`, ale jednoduchšie je často počúvať na vysokom porte a nechať Service mapovať port 80 na 8080.

`SYS_ADMIN` je mimoriadne široká capability a nemá byť generickým riešením pre mount alebo debug problém.

## Privileged container

```yaml
securityContext:
  privileged: true
```

Privileged mode výrazne oslabuje container boundary: sprístupňuje široké capabilities, devices a mení seccomp/LSM confinement podľa runtime. Je určený iba pre úzke trusted platform components, ktoré skutočne potrebujú host-level authority.

Application workload s privileged mode a hostPath alebo runtime socketom môže prakticky kompromitovať Node a všetky Pods na ňom.

## Host namespaces

```yaml
spec:
  hostNetwork: true
  hostPID: true
  hostIPC: true
```

Host network presúva Pod do Node network namespace-u. Port collisions a exposure sa menia. Host PID umožní vidieť host processes podľa ďalších permissions. Host IPC zdieľa IPC boundary.

Tieto fields nemajú byť použité ako rýchla oprava CNI alebo observability problému. Potrebujú explicitný platform dôvod, placement a policy.

## hostPath

```yaml
volumes:
  - name: host-log
    hostPath:
      path: /var/log
      type: Directory
```

hostPath viaže workload na Node filesystem a môže odhaliť citlivé host dáta. Writable mount `/`, `/etc`, `/var/lib/kubelet` alebo container runtime socket je node-admin path.

Aj read-only hostPath môže obsahovať credentials alebo osobné dáta. Pod Security Restricted ho typicky nepovoľuje.

## Seccomp

```yaml
seccompProfile:
  type: RuntimeDefault
```

RuntimeDefault používa default profil container runtime-u. Localhost profil odkazuje na profil dostupný na Node-i:

```yaml
seccompProfile:
  type: Localhost
  localhostProfile: profiles/payments-api.json
```

Localhost profil vytvára Node distribution a versioning problém. Každý eligible Node musí mať správnu generation pred schedulingom workloadu.

Seccomp deny sa môže prejaviť ako `EPERM`, signal alebo audit event podľa profile action. Rovnaký `permission denied` môže pochádzať aj z capabilities, filesystem mode alebo LSM, preto potrebujeme Node audit evidence.

## SELinux a AppArmor

SELinux používa labels a type enforcement. Kubernetes SecurityContext môže podľa platformy nastavovať SELinux options. Volume musí mať kompatibilný label a driver/runtime musí podporovať požadované semantics.

AppArmor profily sa viažu na containers podľa podporovaného API modelu a Node availability. Profil existujúci iba na polovici Nodes vytvorí scheduling/runtime inconsistency.

LSM policy je ďalšia vrstva nad Unix permissions. `chmod 777` nevyrieši SELinux deny a zároveň zhorší security.

## `fsGroup` a volumes

`fsGroup` pomáha sprístupniť podporované volumes skupine procesu. Kubelet alebo CSI driver môže meniť ownership/permissions pri mount-e.

Na veľkom volume môže recursive `chown` predĺžiť startup o minúty. `fsGroupChangePolicy: OnRootMismatch` môže obmedziť zbytočné prechody podľa podpory.

```yaml
securityContext:
  fsGroup: 65532
  fsGroupChangePolicy: OnRootMismatch
```

Nie každý volume typ alebo CSI driver reaguje rovnako. Read-back ownershipu v bežiacom Pode je potrebný.

## Supplemental groups

Process môže dostať supplemental groups z Pod SecurityContextu a podľa image `/etc/group` merge semantics. Novšie Kubernetes možnosti môžu poskytovať prísnejší model, ktorý zabráni neočakávaným image-defined groups.

Pri citlivom shared volume treba overiť effective groups procesu, nie iba YAML.

```bash
kubectl exec -n production <pod-name> -- id
```

Production distroless image nemusí mať `id`; controlled debug alebo application self-report môže poskytnúť bezpečný dôkaz.

## Pod Security Standards

Kubernetes definuje tri policy levels:

```text
Privileged
Baseline
Restricted
```

Restricted vyžaduje silnejší default pre application workloads: non-root, seccomp, obmedzené capabilities a zákaz vybraných host exposures. Presné requirements sa vyvíjajú s Kubernetes verziami, preto sa policy viaže na version.

## Pod Security Admission

Namespace labels môžu vynucovať, auditovať alebo varovať:

```yaml
metadata:
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

Použitie `latest` mení policy pri upgrade-e. Production platforma môže radšej pinovať známu verziu a upgradeovať policy vedome po dry-run a remediation.

`warn` a `audit` neblokujú request. `enforce` ho odmietne. Admission success nepreukazuje runtime behavior ani absenciu application vulnerability.

## Namespace exemptions

Control-plane configuration môže exemptovať vybrané users, RuntimeClasses alebo namespaces. Exemption je broad bypass a potrebuje ownera, expiry a audit. Celý platform namespace exemptovaný kvôli jednému privileged DaemonSetu môže umožniť ďalšie nebezpečné workloads.

Lepšie je izolovať privileged components do úzkeho namespace-u s obmedzeným write accessom.

## Admission a server-side dry-run

```bash
kubectl apply --dry-run=server -f deployment.yaml -o yaml
```

Dry-run overí Pod Security Admission a ďalšie policies bez persistovania. V CI treba testovať aj forbidden manifest, napríklad privileged Pod, a očakávať odmietnutie.

Policy test nesmie skončiť pri positive path. Zakázaný outcome je súčasťou dôkazu.

## RuntimeClass a silnejšia izolácia

RuntimeClass môže vybrať alternatívny runtime handler, napríklad sandboxed alebo microVM-like model podľa platformy.

```yaml
spec:
  runtimeClassName: sandboxed
```

RuntimeClass nie je prenositeľný názov bez cluster contractu. Môže meniť overhead, scheduling a supported devices. Citlivý workload potrebuje overiť actual runtime handler na Node-e.

## Secrets a process boundary

Non-root a restricted policy nezabránia aplikácii čítať Secret, ktorý jej Pod explicitne mountuje. SecurityContext obmedzuje process authority, nie business necessity secretu.

Least privilege preto spája:

```text
minimálny ServiceAccount
+ minimálne Secret mounts
+ NetworkPolicy
+ non-root runtime
+ read-only filesystem
+ admission
+ application authorization
```

## Incident: restricted policy prešla, image aj tak bežal ako root

Namespace enforce label bol omylom nastavený iba na `warn=restricted`, nie `enforce`. CI log zobrazil warning, ale pipeline ho ignorovala. Image nemala non-root USER a Pod template nemala `runAsNonRoot`.

Deployment vznikol a process bežal ako UID 0. Oprava nastavila enforce, pridala explicitný SecurityContext a CI spracovanie warnings. Runtime test overil effective UID a zakázaný privileged manifest.

## Incident: read-only root rozbil aplikáciu

Hardening rollout zapol `readOnlyRootFilesystem: true`. Aplikácia zapisovala compiled templates do `/app/cache`, ktorý nebol mountnutý. Pods crashovali pred readiness.

Bezpečná oprava nepridala writable root. Vytvorila bounded `emptyDir` na `/app/cache`, nastavila ownership a size limit a otestovala cleanup pri Pod replacement-e.

## Incident: seccomp deny bol mylne riešený privileged mode

Nová knižnica použila syscall blokovaný RuntimeDefault profilom. Operátor nastavil `privileged: true`, čím incident zmizol, ale otvoril Node boundary.

Audit ukázal konkrétny syscall. Tím overil, či je skutočne potrebný, aktualizoval runtime/profile cez versionovaný platform flow a privileged workaround odstránil. Forbidden capability a host access tests zostali súčasťou acceptance.

## Incident: `fsGroup` startup trval 20 minút

Stateful Pod mountol multi-terabyte filesystem a kubelet vykonal recursive ownership change pre každý restart. Pod bol `ContainerCreating` a rollout zastal.

Oprava zladila storage pre-provisioning ownership, použila podporovanú `fsGroupChangePolicy` a otestovala mount latency. Security požiadavka ostala zachovaná bez opakovaného full-tree chown.

## Model, ktorý si treba odniesť

SecurityContext skladá effective process a filesystem authority. Pod Security Admission kontroluje admitted Pod proti policy levelu. Runtime, kernel, LSM, image a mounts určujú skutočný výsledok. Bezpečný workload má explicitný non-root user, minimálne capabilities, no privilege escalation, seccomp, read-only root a úzke writable paths a zároveň prechádza positive aj forbidden runtime testmi.

## Referencie

- [Configure a Security Context for a Pod or Container](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
- [Seccomp and Kubernetes](https://kubernetes.io/docs/tutorials/security/seccomp/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: RBAC](rbac.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: ResourceQuota a LimitRange →](resourcequota-limitrange.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
