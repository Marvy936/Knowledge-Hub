# Containers vs. virtual machines

Container a virtual machine sú dve odlišné odpovede na otázku, kde má byť runtime isolation boundary. Virtual machine dostane virtualizovaný hardware, vlastný guest kernel a vlastný OS lifecycle. Linux container zostáva host processom alebo skupinou procesov, ktoré zdieľajú host kernel, ale dostanú odlišné namespace views, cgroup resource controls, credentials, capabilities, mounts a security policy. Container preto nie je „ľahká VM“. Je to iný execution a failure model.

Kapitola otvára incident `CTR-PAY-80`. Atlas Payments publikuje release `10.4` ako multi-platform OCI image a nasadí ho do worker VM fleet. Aplikácia je technicky zabalená v containeri, ale support sidecar beží privileged, mountuje Docker socket a host root filesystem. Tím predpokladá, že container stále chráni node. Pri compromise sidecaru však útočník získa host-level control a ovplyvní všetky workloads, ktoré zdieľajú kernel a daemon boundary.

## 1. Dominantný workload-to-isolation lifecycle

```text
business workload a threat model
→ required isolation, portability a recovery boundary
→ VM image a/alebo container image subject
→ host/hypervisor/guest-kernel/runtime placement
→ namespace, cgroup, capability a device policy
→ network, storage, identity a secret attachment
→ process start, PID 1 a readiness
→ runtime, kernel a business verification
→ patch, rebuild, replace, restore alebo isolation escalation
```

Rozhodnutie medzi containerom a VM sa nemá robiť iba podľa startup času alebo density. Musí zahrnúť:

- kto zdieľa kernel a host daemon;
- čo sa stane pri kernel/runtime escape;
- či workload potrebuje vlastný kernel alebo OS family;
- ako sa spravujú persistent data;
- ako sa patchuje application userspace a kernel;
- čo je replaceable runtime unit;
- aké trust levels sa smú zdieľať na jednom node;
- aký evidence a recovery lifecycle je potrebný.

## 2. Exact workload subject

Atlas production subject:

```yaml
workloadSubject:
  service: atlas-payments
  release: 10.4.0
  image:
    indexDigest: sha256:index104
    platform: linux/amd64
    manifestDigest: sha256:amd104
    configDigest: sha256:cfg104
  runtime:
    engineHost: worker-node-17
    daemonContext: payments-prod
    runtimeClass: runc
    containerId: 2d9f...
    configGeneration: C44
  node:
    vmId: i-node-17
    vmImage: node-os-2026.07.3
    guestKernel: 6.12.x
  isolation:
    user: "10001:10001"
    privileged: false
    capabilities: [NET_BIND_SERVICE]
    seccompProfile: runtime-default
    appArmorProfile: atlas-payments
  resources:
    cpus: 2
    memory: 2GiB
    pids: 512
  persistence:
    businessDataOwner: managed-postgresql/db17
  secretEpoch: SE-2026-07-31-02
```

„Container `payments` beží“ nie je dostatočná identity. Potrebujeme exact image platform, node/kernel, runtime configuration, security profile, mounts, network a data owners.

Praktický read-back:

```bash
docker context show
docker inspect atlas-payments > container-inspect.json
docker image inspect registry.example/atlas/payments@sha256:amd104 > image-inspect.json
uname -a
docker info > docker-info.txt
```

Tieto výstupy preukazujú observed CLI context, container/image metadata a host kernel/daemon properties dostupné danému callerovi. Nepreukazujú, že image signature je dôveryhodná, že business traffic smeruje na tento container ani že runtime policy je dostatočná pre threat model.

## 3. Bežný process, container a VM

### Bežný host process

Process má vlastný virtual address space, file descriptors, credentials a execution state. Bez ďalších isolation controls však zdieľa host process view, mount tree, network stack a resource pool.

### Linux container

Container runtime skladá execution context:

```text
OCI image root filesystem
+ process args, env a working directory
+ namespaces
+ cgroup placement a limits
+ UID/GID a capabilities
+ seccomp a LSM profile
+ mounts, devices a network
→ host-kernel process tree
```

Z pohľadu kernelu sú to stále processes hosta. Image typicky neobsahuje kernel ani bootloader.

### Virtual machine

Hypervisor poskytne virtual hardware:

```text
physical CPU/memory/devices
→ hypervisor
→ virtual CPU, memory, disk, NIC
→ guest kernel boot
→ init/system services
→ application alebo container runtime
```

Guest VM môže mať vlastnú kernel version, modules a OS lifecycle oddelený od hosta.

## 4. Isolation boundary

Container isolation používa Linux kernel primitives. OCI runtime specification pre Linux explicitne modeluje namespaces, cgroups, capabilities, mounts, devices a filesystem restrictions. Ak runtime configuration namespace nepožaduje, process môže inherit-nuť runtime namespace daného typu, čo zásadne mení isolation boundary. citeturn973841search0

Shared-kernel dôsledok:

```text
container compromise
→ attacker stále potrebuje prekonať runtime/kernel/security policy
→ úspešný kernel/runtime/daemon escape zasiahne node
→ ostatné workloads na node zdieľajú blast radius
```

VM pridáva ďalšiu guest-kernel a hypervisor boundary:

```text
application compromise
→ guest OS compromise
→ ďalší krok pre hypervisor/host escape
```

Ani VM nie je automaticky bezpečná. Guest image, virtual devices, hypervisor, cloud management identity a network musia byť hardenované.

## 5. Containers vo VMs

Bežný cloud model kombinuje obe vrstvy:

```text
physical host
→ hypervisor
→ worker VM
→ Linux guest kernel
→ container runtime
→ application containers
```

VM určuje node/tenant/kernel failure domain. Container je replaceable application deployment unit. Výsledkom sú dva oddelené patch lifecycles:

```text
application/base-image vulnerability
→ rebuild a replace container image

kernel/runtime vulnerability
→ patch alebo replace worker VM/node
```

Rebuild application image neopraví guest kernel. Node patch neopraví vulnerable package zapečený v image.

## 6. Packaging identity

VM image typicky obsahuje bootovateľný OS stack. Container image obsahuje application userspace a runtime defaults:

```text
filesystem layers
image config
user
entrypoint/command
environment defaults
working directory
labels
OS/architecture metadata
```

Running container je:

```text
exact image/platform manifest
+ runtime command/env/user
+ mounts/secrets/network
+ resource/security policy
+ writable snapshot
+ process state
```

Dva containers z rovnakého digestu preto môžu mať odlišný effective runtime state.

## 7. Portability contract

Container image neštandardizuje celý machine environment. Runtime compatibility závisí od:

- OS/kernel family;
- CPU architecture a variant;
- required syscalls a kernel features;
- libc/dynamic linker;
- devices;
- seccomp/LSM policy;
- mount/filesystem semantics;
- network a storage capabilities.

Linux image na macOS alebo Windows typicky beží cez Linux VM vrstvu:

```text
macOS/Windows host
→ Docker Desktop Linux VM
→ Linux kernel
→ container runtime
→ Linux container
```

Docker Desktop dokumentácia uvádza, že Engine beží v lightweight Linux VM, takže host a container network/filesystem boundaries sa líšia od native Linux Engine. citeturn888444search14

„Runs anywhere“ teda znamená iba v rámci explicitného platform contractu.

## 8. Startup a readiness

VM startup:

```text
virtual hardware
→ firmware/bootloader
→ guest kernel
→ init/services
→ application
```

Container startup:

```text
resolve image
→ prepare rootfs snapshot
→ namespaces/cgroups/mounts/network
→ exec PID 1
```

Container môže začať rýchlejšie, ale process existence nie je readiness. Atlas po štarte ešte:

- načíta secret epoch;
- otvorí database pool;
- overí schema compatibility;
- začne počúvať;
- zahreje cache;
- prejde payment smoke transaction.

Rozlišuj:

```text
created → started → alive → ready → serving → healthy under load
```

## 9. PID 1 a termination

PID 1 v PID namespace má špeciálne signal a child-reaping semantics. Docker `--init` môže vložiť lightweight init, ktorý forwarduje signals a zbiera child processes; Docker dokumentácia zároveň upozorňuje, že PID 1 je Linuxom spracovaný špeciálne. citeturn973841search4turn973841search16

Praktická kontrola:

```bash
docker inspect atlas-payments \
  --format 'Path={{.Path}} Args={{json .Args}} Init={{.HostConfig.Init}} StopSignal={{.Config.StopSignal}}'

docker top atlas-payments -eo pid,ppid,user,stat,args
```

Výstup preukazuje Docker metadata a observed process tree. Nepreukazuje, že application pri SIGTERM dokončí in-flight transactions. To sa testuje controlled terminationom a business reconciliation.

## 10. Resource model

Container používa cgroups na resource accounting/control. VM má virtual CPU/memory pridelené hypervisorom, ale môže trpieť overcommitom alebo storage/network contention.

Container limit nie je vždy reservation. Napríklad CPU quota obmedzuje maximálny time budget, memory limit môže vyvolať cgroup OOM a PID limit môže blokovať fork. Docker podporuje CPU, memory a ďalšie resource constraints, ale ich outcome sa musí čítať spolu s kernel cgroup evidence. citeturn973841search3turn973841search14

```bash
docker inspect atlas-payments \
  --format 'Memory={{.HostConfig.Memory}} NanoCPUs={{.HostConfig.NanoCpus}} PidsLimit={{.HostConfig.PidsLimit}}'

docker stats --no-stream atlas-payments
```

`docker stats` je current telemetry snapshot. Nepreukazuje historical throttling, peak memory ani OOM root cause bez cgroup events/kernel logs.

## 11. Persistence boundary

Container writable layer je runtime-instance state. Je vhodná pre temporary data a disposable cache, nie ako jediný owner business dát.

```text
container delete/recreate
→ writable layer removed
→ image layers remain immutable
```

Stateful workload môže bežať v containeri, ale data identity musí byť externalizovaná do volume, block/network storage, database alebo object store s backup/restore lifecycle-om.

VM disk môže prežiť process restart, ale machine snapshot nie je automaticky application-consistent database backup.

## 12. Patch a recovery model

Container model preferuje:

```text
source/config fix
→ build exact image
→ test/scan/sign
→ publish digest
→ replace runtime instances
→ verify
→ retire old digest
```

Interactive `docker exec` patch vytvára snowflake:

```text
running filesystem changed
≠ image digest
→ replacement stráca fix
→ scanner/provenance fix nevidia
```

VM môže používať image replacement alebo in-place patching, ale aj tam musí byť versionovaný desired state a tested rollback/recovery.

## 13. Density a failure domains

Containers majú menší per-instance overhead, preto umožňujú vyššiu density. Vyššia density však môže zväčšiť node blast radius:

```text
jeden node kernel/runtime incident
→ mnoho workloads naraz
```

VM isolation môže znížiť počet workloads v jednom boundary. Rozhodnutie zohľadňuje:

- tenant trust;
- regulatory boundary;
- workload sensitivity;
- kernel attack surface;
- device requirements;
- noisy-neighbor risk;
- recovery time a replacement capacity.

## 14. Kedy shared-kernel boundary nestačí

Zváž dedicated VM, microVM alebo sandboxed runtime, keď:

- spúšťaš nedôveryhodný alebo multi-tenant code;
- kompromitácia jedného workloadu nesmie ohroziť ostatné;
- workload potrebuje iný kernel/OS;
- vyžaduje broad devices/capabilities;
- používa kernel modules alebo privileged operations;
- policy/regulácia vyžaduje silnejšiu boundary;
- runtime socket/host mounts sú nevyhnutné a risk nemožno zúžiť.

Sandboxed runtime môže zachovať container image workflow, ale pridať VM-like isolation. Musí sa overiť compatibility, performance a observability tradeoff.

## 15. Worked incident `CTR-PAY-80`: privileged support container

Support sidecar mal:

```yaml
privileged: true
volumes:
  - /:/host
  - /var/run/docker.sock:/var/run/docker.sock
```

Mechanizmus:

```text
broad devices/capabilities
+ writable host filesystem
+ root-equivalent daemon API
→ sidecar compromise
→ attacker creates new privileged container
→ host/node control
→ every container on node shares blast radius
```

Recovery:

1. isolate node z workload scheduling/trafficu;
2. preserve daemon, audit, container a host evidence;
3. revoke node/workload credentials;
4. rebuild node z trusted VM image;
5. redeploy exact application digests;
6. replace sidecar model narrow read-only log/API capabilityou;
7. verify forbidden Docker-socket/host-root mounts policy.

Restart compromised container nestačí, pretože host trust je stratený.

## 16. Worked incident: data vo writable layeri

Export worker ukladal pending reconciliation ledger do `/var/lib/atlas/pending` bez volume.

```text
8 000 pending records
→ node drain deletes container
→ writable layer disappears
→ replacement has empty ledger
→ external export and database diverge
```

Recovery rekonštruuje ledger z authoritative events/database a vykoná reconciliation. Skorší control je data-ownership inventory a destructive replacement test.

## 17. Worked incident: running zamieňané s ready

Container process začal za dve sekundy, ale database compatibility check trval 40 sekúnd. Load balancer pridal instance podľa process state-u.

```text
PID exists
→ traffic arrives
→ dependency not ready
→ payment requests fail
```

Readiness oracle musí testovať relevantnú capability a platform musí odobrať instance pri neskoršej readiness loss, nie iba pri štarte.

## 18. Competing hypotheses pri „funguje vo VM, zlyhá v containeri“

```text
H1: wrong OS/architecture alebo dynamic linker
H2: missing filesystem path/mount
H3: non-root UID/GID permission
H4: dropped capability
H5: seccomp/SELinux/AppArmor denial
H6: read-only root filesystem
H7: cgroup memory/PID limit
H8: PID 1/signal wrapper
H9: different network/DNS/port binding
H10: wrong effective env/secret
```

Diskriminačné evidence:

```bash
docker inspect atlas-payments
docker logs --timestamps atlas-payments
docker top atlas-payments -eo pid,ppid,user,stat,args
docker stats --no-stream atlas-payments
dmesg --ctime | tail -n 200
journalctl -k --since '15 minutes ago'
```

`inspect` testuje configured runtime subject, process/logs runtime behavior a kernel audit OOM/LSM/seccomp hypotheses. Žiadny výstup sám nepreukazuje business outcome.

## 19. Evidence-preserving containment

Pred restartom, delete alebo node replacementom zachovaj:

- container/image IDs a digests;
- `docker inspect`, context a daemon info;
- process tree a exit state;
- logs/events;
- cgroup/resource evidence;
- namespace/mount/network evidence;
- kernel/audit logs;
- writable-layer/data ownership;
- exact node identity a workload credentials.

Destructive `docker rm`, daemon restart alebo prune môže odstrániť najlepší root-cause dôkaz.

## 20. Acceptance a forbidden paths

Isolation blok je prijatý, keď:

```text
workload/image/platform/node subject je exact
+ shared-kernel threat boundary je explicitná
+ privileged/socket/host-root paths sú forbidden alebo justified
+ PID 1 handles termination
+ cgroup limits a OOM/throttling sú observable
+ business data nie sú vo writable layeri
+ process/readiness/business states sú oddelené
+ application aj node patch lifecycles sú testované
+ second container from same subject behaves identically
+ high-risk workload is rejected from insufficient isolation class
```

Forbidden tests:

- Docker socket mount;
- writable host root mount;
- privileged mode bez approved exception;
- data write iba do writable layer;
- traffic pred readiness;
- wrong kernel/runtime capability node.

## 21. Kontrolné otázky

1. Prečo container nie je malá VM?
2. Čo presadzuje container isolation?
3. Aký rozdiel je medzi image a running container subjectom?
4. Prečo architecture equality nestačí na portability?
5. Čo PID 1 musí robiť pri termination?
6. Prečo resource limit nie je automaticky reservation?
7. Kde majú žiť business dáta?
8. Prečo `docker exec` patch nie je recovery?
9. Ako sa patch lifecycle application image líši od node kernelu?
10. Kedy shared-kernel boundary nestačí?
11. Aké evidence treba zachovať pred delete/restartom?
12. Ako sa overí forbidden privileged path a second-container outcome?

## Glossary impact

Relevantné pojmy: container, virtual machine, shared kernel, guest kernel, hypervisor, isolation boundary, workload subject, container image, runtime configuration, PID 1, readiness, cgroup limit, writable layer, persistent data owner, node blast radius, microVM, sandboxed runtime a immutable replacement.

## Primárne zdroje

- [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec)
- [OCI Linux runtime configuration](https://github.com/opencontainers/runtime-spec/blob/main/config-linux.md)
- [Docker running containers](https://docs.docker.com/engine/containers/run/)
- [Docker resource constraints](https://docs.docker.com/engine/containers/resource_constraints/)
- [Linux PID namespaces](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
[← Predchádzajúca: Terraform vs. Ansible](../07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Namespaces, cgroups a capabilities →](namespaces-cgroups-capabilities.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
