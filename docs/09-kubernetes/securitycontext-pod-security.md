# SecurityContext a Pod Security

Kubernetes security nie je jeden boolean `non-root`. Je to chain medzi threat modelom, image identity, admission policy, resolved Pod a container konfiguráciou, OCI runtime state-om, kernel enforcementom, mount/device authority a skutočným application outcome-om. Pod Security Admission môže Pod odmietnuť, ale prijatý Pod stále môže mať nesprávny filesystem access, nebezpečný socket alebo príliš širokú runtime autoritu.

Táto kapitola používa jeden dominantný lifecycle:

```text
workload threat model a required capability inventory
→ image user/filesystem/runtime assumptions
→ namespace PSS/PSA a custom admission generation
→ admitted Pod a container security contract
→ OCI/runtime credentials, namespaces a capabilities
→ seccomp/AppArmor/SELinux a no_new_privs enforcement
→ mounts, devices, host namespaces a filesystem identity
→ process execution a application behavior
→ security aj business verification
→ exception expiry, remediation a credential rotation
```

## 1. Atlas Payments security subject

Payments API 5.4.0 má spracúvať autorizácie bez host authority. Reviewed contract:

```text
namespace: payments-production
PSS: restricted, pinned na podporovanú minor verziu
Pod UID + image digest: exact runtime subject
UID/GID: 10001:10001
root filesystem: read-only
writable paths: /tmp a /var/run/atlas cez bounded emptyDir
capabilities: drop ALL
privilege escalation: disabled
seccomp: RuntimeDefault
host namespaces/devices/runtime sockets: forbidden
persistent volume: iba retry-ledger claim
ServiceAccount: bez API tokenu, ak ho workload nepotrebuje
```

Security acceptance neznamená iba `Pod Running`. Musí potvrdiť:

1. admitted object zodpovedá reviewed policy generation;
2. runtime process má očakávané UID, GID, groups a capabilities;
3. zakázané host paths, devices a namespaces nie sú dostupné;
4. povolené writable paths fungujú bez globálneho `chmod 777`;
5. kernel policy neblokuje legitímny operation ani nepovoľuje zakázaný;
6. application dokončí payment journey;
7. forbidden escape, secret-read a host-control operations zlyhajú.

## 2. Štyri odlišné security subjects

Pri diagnostike oddeľuj:

```text
source manifest
→ admitted Pod spec
→ OCI/runtime configuration
→ effective process a kernel authority
```

Source YAML môže byť zmenený defaultingom alebo mutating admissionom. Admitted Pod môže byť korektný, ale Node runtime, local security profiles alebo mounted volume labels môžu vytvoriť inú effective authority.

Exact subject obsahuje minimálne:

- cluster a namespace;
- Pod UID a container ID;
- image digest a declared image user;
- Pod/container `securityContext` po admission-e;
- PSS level, mode a pinned version;
- RuntimeClass a Node generation;
- UID, GID, supplemental groups a capabilities;
- seccomp, AppArmor a SELinux profile/label;
- mount, device a host-namespace inventory;
- ServiceAccount a projected credential inventory.

Názov Deploymentu ani status `Running` túto identitu nenahrádza.

## 3. Admission boundary: PSS a PSA

Pod Security Standards definujú tri policy levels:

- `Privileged` — takmer bez štandardných obmedzení;
- `Baseline` — blokuje známe privilege-escalation paths pri širšej kompatibilite;
- `Restricted` — silnejší hardening contract pre bežné application workloads.

Pod Security Admission aplikuje level na namespace cez:

- `enforce` — odmietne nevyhovujúci Pod;
- `audit` — zapíše violation do audit evidence;
- `warn` — vráti warning klientovi.

Policy version je súčasťou admission subjectu. Produkčný model často používa pinned `enforce` version a `audit`/`warn` voči novšiemu štandardu, aby upgrade ukázal budúce violations skôr než ich začne blokovať.

PSA hodnotí Pod pri admission-e. Nemení už bežiace Pody retroaktívne a nie je plnou náhradou custom controls ako approved registry, digest pinning, mandatory requests, presný `hostPath` allowlist alebo sandbox requirement.

## 4. Runtime identity a filesystem contract

### UID, GID a non-root

`runAsNonRoot: true` je guard. Bez explicitného numeric image usera alebo `runAsUser` môže runtime nevedieť potvrdiť, že process nebude root.

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
```

Non-root process stále potrebuje správne ownership a permissions pre image files, sockets, logs, temp paths a mounted data.

### Volume identity

`fsGroup` môže pri podporovanom volume/driveri pridať group access. Nie je to application lock ani tenant isolation. Effective access závisí od:

```text
process UID/GID/groups
+ Unix mode/ACL
+ mount read-only state
+ CSI ownership behavior
+ SELinux/AppArmor policy
+ user-namespace mapping
```

Rekurzívna ownership zmena veľkého volume-u môže výrazne predĺžiť startup. `fsGroupChangePolicy` a CSI delegation musia byť testované na konkrétnom storage stacku.

### Read-only root filesystem

Read-only root odhaľuje skryté write dependencies. Potrebné paths deklaruj explicitne:

```yaml
volumeMounts:
  - name: runtime
    mountPath: /var/run/atlas
volumes:
  - name: runtime
    emptyDir:
      sizeLimit: 64Mi
```

Nevracaj celý root filesystem na writable iba preto, že application zapisuje PID, cache alebo temp file na nesprávne miesto.

## 5. Process privilege contract

### Capabilities

Preferovaný model:

```yaml
securityContext:
  capabilities:
    drop: ["ALL"]
  allowPrivilegeEscalation: false
```

Capability pridaj iba po identifikácii exact kernel operationu. `SYS_ADMIN`, `NET_ADMIN`, `SYS_PTRACE` a podobné capabilities výrazne menia threat boundary.

### `allowPrivilegeEscalation`

Na Linuxe sa typicky realizuje cez `no_new_privs`. Bráni získaniu nových privileges cez setuid alebo file capabilities, ale neodoberá authority, ktorú process už dostal cez UID, capabilities, mounts, devices alebo privileged mode.

### Privileged a host authority

`privileged: true`, host namespaces, host devices, broad `hostPath` alebo container-runtime socket môžu zmeniť container na prakticky host-admin subject. Read-only runtime socket mount môže stále poskytovať control API authority.

Hodnoť capability graph, nie iba jednotlivý YAML field:

```text
Pod create permission
→ privileged/host-mounted workload
→ runtime alebo host filesystem access
→ Node a ostatné workloads
```

## 6. Kernel enforcement profiles

### Seccomp

Seccomp filtruje syscalls. `RuntimeDefault` je bezpečný východiskový profil, ale jeho exact obsah patrí runtime a verzii. `Localhost` profile potrebuje distribúciu, versioning a Node coverage.

Pri denial-e porovnaj:

- Pod/container profile declaration;
- runtime-resolved profile;
- blocked syscall a errno;
- kernel/runtime audit evidence;
- rozdiel medzi Nodes a runtime generations.

Neprepínaj plošne na `Unconfined` bez určenia operationu, ktorý application potrebuje.

### AppArmor a SELinux

AppArmor viaže process na host profile. SELinux rozhoduje podľa process a object labels. Unix `rwx` bits preto nemusia vysvetliť `permission denied`.

Profily a labels musia mať vlastný deployment lifecycle. Pod môže byť admitted správne, ale zlyhať iba na Node-e, kde profile chýba, má inú verziu alebo volume dostalo nesprávny label.

## 7. User namespaces, sandbox a OS boundary

SecurityContext a PSS stále používajú shared host kernel. Nedôveryhodný code môže potrebovať:

- user namespaces;
- sandboxed RuntimeClass;
- microVM;
- dedicated Nodes;
- samostatný cluster alebo VM trust domain.

Tieto mechanizmy majú vlastné scheduling, resource-overhead, CNI/CSI a upgrade contracts.

Linux-specific fields ako capabilities, UID/GID, seccomp, AppArmor a SELinux nemajú rovnaký význam na Windows. Policy generation musí zohľadniť `spec.os.name`, runtime a Node support.

## 8. Exception lifecycle

System CNI, CSI alebo node agents môžu potrebovať authority nad bežný Restricted profil. Výnimka musí obsahovať:

```text
owner
exact namespace a workload identity
required host capability
threat justification
approved image digest/source
Node a network scope
RBAC a deployment writers
monitoring a audit
expiry a removal condition
```

`privileged` namespace bez deployment a identity boundary je trvalý bypass. Výnimka sa uzatvára až po overení, že bežné application identity v ňom nemôžu vytvárať workloady.

## 9. Causal walkthrough: Pod funguje iba po nebezpečnom bypass-e

### Symptom

Payments 5.4.0 je po zapnutí Restricted policy odmietnutý. Operator presunie workload do `platform-exceptions`, kde Pod beží. Neskôr audit zistí, že release ServiceAccount môže cez debug sidecar ovládať container runtime na Node-e.

### Exact subject

Fixuj:

- namespace labels a PSS version;
- Deployment/ReplicaSet/Pod UID a image digest;
- všetky init, application, sidecar a ephemeral containers;
- resolved security contexts;
- host namespaces, devices a mounts;
- runtime socket path a API authority;
- ServiceAccount/RBAC identity;
- Node a RuntimeClass generation;
- audit request a exact forbidden operation.

### Competing hypotheses

1. application legitímne potrebuje host runtime socket;
2. socket je read-only, preto nie je nebezpečný;
3. iba init container potrebuje root a po štarte authority zmizne;
4. PSS version zmenila pravidlo neočakávane;
5. custom admission pridalo mount alebo sidecar;
6. release controller používa inú ServiceAccount;
7. runtime socket neposkytuje write/control operations;
8. Node isolation robí host access prijateľný;
9. `allowPrivilegeEscalation=false` blokuje zneužitie socketu;
10. broad namespace exception sprístupnila capability iným workload writerom.

### Discriminating observations

Porovnaj source a admitted Pod, namespace labels, admission warnings/audit, owner references, image digests, effective mounts, `id`, capabilities, `no_new_privs`, seccomp/AppArmor/SELinux state, RBAC na Pod/ephemeral-container creation a actual runtime API request.

Finding:

```text
legacy metrics sidecar
→ mount /run/containerd/containerd.sock
→ namespace musí byť Privileged
→ release ServiceAccount smie meniť Pod template
→ sidecar alebo exec subject volá runtime API
→ host workloads a credentials sú dostupné
```

Read-only filesystem flag ani `allowPrivilegeEscalation=false` neodoberajú authority poskytovanú control socketom.

### Containment

- pozastav rollout a debug access;
- izoluj affected Nodes/workload podľa incident scope-u;
- zachovaj admitted specs, audit logs a runtime events;
- odober release writerovi možnosť vytvárať nové privileged Pods;
- rotuj credentials, ku ktorým mohol host-access subject pristúpiť;
- nemaž Pod/Node evidence skôr než je zachytená.

### Authoritative recovery

- odstráň legacy sidecar alebo nahraď runtime-socket dependency bounded metrics endpointom;
- vráť workload do Restricted namespace-u;
- nastav explicitný non-root/read-only/capability/seccomp contract;
- vytvor iba potrebné writable mounts;
- oddeľ platform exception deploy identity od application identity;
- zaveď custom admission pre runtime sockets, hostPath a privileged workloads;
- redeployni novú Pod generation a rotuj exposed secrets.

### Verify original a forbidden outcomes

Over:

1. payment journey funguje;
2. Pod prejde pinned Restricted policy;
3. process používa expected UID/GID/capabilities;
4. legitímne writable paths a volume access fungujú;
5. runtime socket, host filesystem, devices a host namespaces nie sú dostupné;
6. application ServiceAccount nevie vytvoriť privileged/debug bypass;
7. old credentials sú neplatné;
8. replacement na inom Node-e má rovnaký security verdict.

### Earlier controls

Použi security-contract test na admitted Pod, permission/capability diff gate, exception expiry, forbidden host-mount policy, runtime-profile conformance test, break-glass audit a pravidelný replacement test na každej Node generation.

## 10. Ďalšie failure boundaries

### `runAsNonRoot` odmietne image

Image nemá jednoznačný non-root user alebo effective UID je 0. Oprav image a explicitný runtime contract; nevypínaj guard.

### Volume má `permission denied`

Rozlišuj UID/GID, `fsGroup`, ACL, read-only mount, CSI ownership, SELinux/AppArmor denial a user-namespace mapping. `chmod 777` ničí diagnostickú aj security boundary.

### Read-only root rozbije startup

Zachyť exact write path a účel. Pridaj bounded ephemeral/persistent mount, nie writable root.

### Capability drop rozbije application

Identifikuj syscall a kernel permission. Preferuj redesign alebo vyšší port; ak capability musí zostať, pridaj iba jednu a testuj forbidden operations.

### Seccomp/AppArmor profile chýba iba na jednom Node-e

Pod admission môže uspieť, ale runtime vytvorenie alebo operation zlyhá. Porovnaj profile distribution a Node generation.

### PSA `enforce` blokuje controller-generated Pod

Validuj resolved Pod template všetkých workload controllers, Jobs a upgrade hooks. Presun do privileged namespace-u nie je automatická remediation.

## 11. Referenčný katalóg

### Identity a authority controls

- `runAsUser`, `runAsGroup`, `runAsNonRoot`;
- `fsGroup` a supplemental groups;
- capabilities a `allowPrivilegeEscalation`;
- `privileged`, host namespaces, devices a `hostPath`;
- read-only root a explicitné writable mounts;
- seccomp, AppArmor a SELinux;
- RuntimeClass, user namespaces a sandbox.

### PSS/PSA evidence

```text
namespace policy level/mode/version
admitted Pod spec
warning/audit/enforce verdict
runtime-resolved security config
process/kernel authority
allowed a forbidden operation tests
```

## 12. Anti-patterny

- `privileged: true` ako oprava permissions;
- `chmod 777` na volume;
- runtime socket považovaný za neškodný read-only file;
- PSS `latest` bez upgrade rehearsal;
- privileged namespace dostupný application writerom;
- seccomp/AppArmor/SELinux vypnuté bez evidence;
- non-root považovaný za úplný sandbox;
- permanentný privileged debug sidecar;
- policy success považovaný za dôkaz bezpečného runtime-u.

## 13. Kontrolné otázky

1. Ktoré štyri security subjects musíš odlíšiť od source manifestu po process authority?
2. Prečo `runAsNonRoot` nestačí bez image a filesystem contractu?
3. Ako sa líši capability, `no_new_privs` a privileged mode?
4. Prečo read-only runtime socket môže byť host-control capability?
5. Ako sa líši PSS policy level od PSA mode a version?
6. Prečo Unix mode bits nemusia vysvetliť SELinux/AppArmor denial?
7. Kedy `fsGroup` mení startup latency a access boundary?
8. Prečo Restricted Pod stále nemusí byť vhodný pre nedôveryhodný code?
9. Ako uzavrieš privileged namespace exception?
10. Ktoré forbidden outcomes musí overiť security recovery?

## Glossary impact

Relevantné pojmy: Kubernetes security lifecycle subject, admitted security contract, runtime authority generation, process credential subject, capability inventory, host-control mount, kernel enforcement generation, filesystem access verdict, PSS policy generation, PSA admission verdict, privileged exception subject, sandbox boundary, security evidence matrix a forbidden-authority verification.

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
