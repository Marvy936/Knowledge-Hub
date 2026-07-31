# Namespaces, cgroups a capabilities

Linux container nevzniká jedným kernel prepínačom. Runtime vytvorí host process a jeho boundary poskladá z viacerých nezávislých mechanizmov. Namespaces menia, čo process vidí a v akom kernel context-e operuje. Cgroups určujú accounting, limits a scheduling pressure. UID/GID, capabilities, `no_new_privs`, seccomp, SELinux/AppArmor, devices a mount policy určujú, čo process smie vykonať nad konkrétnym objektom. Žiadna z týchto vrstiev samostatne netvorí plnú container isolation.

Kapitola pokračuje incidentom `CTR-PAY-80`. Atlas Payments dostane memory limit 2 GiB, `pids.max=512` a minimum capabilities. Diagnostický variant však zdedí host network namespace, pridá `CAP_SYS_ADMIN` a bindne writable `/sys`. Aplikácia zároveň používa shell wrapper ako PID 1. Pri memory pressure container skončí, ale tím vidí iba exit code `137`; pri termination sa SIGTERM nedostane k serveru a host-level diagnostický container má podstatne širšiu authority než jeho image naznačuje.

## 1. Dominantný policy-to-kernel-enforcement lifecycle

```text
workload a host threat model
→ runtime process/user subject
→ namespace create/join decisions
→ rootfs a mount/device assembly
→ cgroup placement a controller values
→ capability/no_new_privs/seccomp/LSM policy
→ exec PID 1
→ kernel resource/security events
→ signal/termination a cleanup
→ forbidden operation a second-container verification
```

Každá vrstva odpovedá na inú otázku:

```text
namespaces
→ ktorý view globálneho kernel resource-u process dostane?

cgroups
→ koľko resource spotrebuje, ako sa účtuje a čo sa stane pri hranici?

credentials/capabilities
→ aké privileged kernel operations môže žiadať?

seccomp
→ ktoré syscalls a argument classes smie volať?

SELinux/AppArmor
→ smie tento process vykonať túto operation nad týmto objectom?
```

OCI Linux runtime configuration tieto mechanizmy modeluje oddelene. Ak namespace type nie je v OCI confige uvedený, process môže inherit-nuť runtime namespace daného typu; preto „container“ label nepreukazuje, že každý namespace je nový. citeturn973841search0

## 2. Exact kernel process subject

```yaml
isolationSubject:
  containerId: 2d9f...
  hostPid: 48291
  namespacePid: 1
  imageManifest: sha256:amd104
  user:
    containerUid: 10001
    containerGid: 10001
    hostUid: 2010001
    userNamespace: user:[4026533001]
  namespaces:
    pid: pid:[4026533002]
    mount: mnt:[4026533003]
    network: net:[4026533004]
    uts: uts:[4026533005]
    ipc: ipc:[4026533006]
    cgroup: cgroup:[4026533007]
  cgroupPath: /system.slice/docker-2d9f.scope
  capabilities:
    bounding: [NET_BIND_SERVICE]
    effective: [NET_BIND_SERVICE]
  noNewPrivileges: true
  seccomp: runtime-default
  appArmor: atlas-payments
  mountsGeneration: M44
```

Praktický host-side read-back:

```bash
container_pid="$(docker inspect -f '{{.State.Pid}}' atlas-payments)"

printf 'host_pid=%s\n' "$container_pid"
ls -l "/proc/$container_pid/ns/"
cat "/proc/$container_pid/status"
cat "/proc/$container_pid/cgroup"
findmnt -N "$container_pid"
nsenter -t "$container_pid" -n ip address
```

Namespace symlink inodes preukazujú namespace membership v čase observation. `status` ukazuje credentials/capability hex masks a seccomp mode. `cgroup` ukáže membership path. Nepreukazujú samy, že policy je bezpečná alebo že process nemá nebezpečný inherited file descriptor.

## 3. Namespace je view, nie automatická policy

Namespace obalí globálny kernel resource abstrakciou, takže members vidia vlastnú instance alebo zvolený shared context. Linux namespace typy zahŕňajú PID, mount, network, IPC, UTS, user, cgroup a time. citeturn973841search5turn973841search0

Samostatný network namespace stále môže mať route do production database. Samostatný mount namespace môže obsahovať writable host root mount. PID namespace môže byť zdieľaný s ďalším workloadom. Preto acceptance nekontroluje iba „namespace existuje“, ale aj jeho obsah a sharing contract.

Porovnanie namespace membershipu:

```bash
readlink /proc/1/ns/net
readlink "/proc/$container_pid/ns/net"
readlink /proc/1/ns/mnt
readlink "/proc/$container_pid/ns/mnt"
```

Rovnaký inode znamená shared namespace instance pre daný type. Rozdielny inode preukazuje iný view, nie bezpečnú route alebo mount policy.

## 4. PID namespace a PID 1

Host môže process vidieť ako PID `48291`, zatiaľ čo v containeri je PID `1`.

```bash
docker top atlas-payments -eo pid,ppid,user,stat,args
nsenter -t "$container_pid" -p -m ps -eo pid,ppid,user,stat,args
```

PID 1 má špeciálne signal semantics a zodpovednosť za orphaned children. Linux PID namespace init process môže ignorovať signals s default action, pokiaľ pre ne nemá handler; Docker preto ponúka `--init`, ktorý forwarduje signals a reaps child processes. citeturn973841search4turn973841search16

Rizikový wrapper:

```sh
#!/bin/sh
/opt/atlas/bin/server
```

Shell zostane PID 1 a application je child. Bez `exec` alebo signal trap nemusí dostať SIGTERM.

Správny jednoduchý wrapper:

```sh
#!/bin/sh
set -eu
exec /opt/atlas/bin/server "$@"
```

Termination test:

```bash
start="$(date +%s)"
docker stop --time 30 atlas-payments
end="$(date +%s)"
printf 'stop_duration_seconds=%s\n' "$((end-start))"
```

Graceful stop time a application logs preukazujú observed termination behavior. Nepreukazujú, že všetky in-flight transactions boli reconciled; to potrebuje business-side query.

## 5. Mount namespace a root filesystem

Runtime skladá process filesystem view:

```text
unpacked read-only image snapshots
+ container writable snapshot
+ /proc, /dev, /sys masks
+ named volumes, bind mounts a tmpfs
+ propagation a read-only flags
→ mount namespace view
```

Praktická inspection:

```bash
docker inspect atlas-payments \
  --format '{{json .Mounts}}' | jq .

nsenter -t "$container_pid" -m findmnt -R /
```

Docker mount metadata preukazuje daemon-configured mounts. `findmnt` v namespace ukáže effective mount tree. Nepreukazuje application-level data ownership ani host path trust.

High-risk paths:

```text
/var/run/docker.sock
/
/proc
/sys
/dev
host credential directories
container runtime state directories
```

Read-only rootfs znižuje mutation surface, ale workload potrebuje explicitné writable paths:

```yaml
read_only: true
tmpfs:
  - /tmp:size=128m,mode=1777
volumes:
  - atlas-cache:/var/cache/atlas
```

## 6. Mount propagation

Bind mount propagation určuje, či child/parent mount events prechádzajú medzi namespaces. Shared propagation môže umožniť, aby mount vytvorený v container context-e ovplyvnil host alebo opačne. Defaulty sa líšia podľa runtime a platformy; policy má používať private/slave semantics, pokiaľ explicitne nepotrebuje propagation.

`findmnt -o TARGET,PROPAGATION` a `/proc/<pid>/mountinfo` sú relevantné evidence. Mount namespace manual popisuje peer groups a propagation behavior. citeturn973841search15

## 7. Network namespace

Network namespace izoluje interfaces, routes, firewall state, sockets a port space. Bežný bridge path:

```text
container eth0
↔ veth pair
↔ host veth
↔ bridge
↔ host routing/firewall/NAT
↔ external network
```

```bash
nsenter -t "$container_pid" -n ip -details address
nsenter -t "$container_pid" -n ip route
nsenter -t "$container_pid" -n ss -lntup
ip link show type veth
```

Network namespace docs potvrdzujú vlastnú network stack vrstvu vrátane devices a sockets. citeturn973841search20

Samostatný namespace nepreukazuje isolation od hosta. `--network host` ho odstráni; published ports a host firewall môžu stále sprístupniť service external clients.

## 8. User namespace a UID mapping

User namespace umožňuje mapovať container UID/GID na iný host range:

```text
container UID 0
→ host UID 2000000
```

Process môže mať capabilities vo svojom user namespace bez rovnakej authority v initial user namespace. User namespaces sú základ rootless a user-remapping modelu. citeturn973841search21turn973841search12

Observation:

```bash
cat "/proc/$container_pid/uid_map"
cat "/proc/$container_pid/gid_map"
stat -c '%u:%g %n' /host/path/used/by/container
```

Mapping preukazuje numeric translation. Nepreukazuje, že bind-mounted filesystem permissions, ACLs a idmapped mount semantics umožnia intended operation.

## 9. Cgroup v2 subject

Cgroup v2 používa unified hierarchy. Relevantné controller files môžu zahŕňať:

```text
cpu.max
cpu.weight
cpu.stat
memory.current
memory.high
memory.max
memory.events
pids.current
pids.max
pids.events
io.stat
cgroup.procs
```

Kernel cgroup v2 dokumentácia definuje controller semantics a hierarchical accounting. citeturn973841search3

Host read-back:

```bash
cgroup_rel="$(awk -F: '$1=="0" {print $3}' "/proc/$container_pid/cgroup")"
cgroup_dir="/sys/fs/cgroup${cgroup_rel}"

printf 'cgroup=%s\n' "$cgroup_dir"
cat "$cgroup_dir/cgroup.procs"
cat "$cgroup_dir/cpu.max"
cat "$cgroup_dir/cpu.stat"
cat "$cgroup_dir/memory.current"
cat "$cgroup_dir/memory.max"
cat "$cgroup_dir/memory.events"
cat "$cgroup_dir/pids.current"
cat "$cgroup_dir/pids.max"
```

Tieto files preukazujú effective cgroup values a counters pre daný cgroup subject. Nepreukazujú business SLO ani complete historical pressure bez telemetry retention.

## 10. CPU weight, quota a throttling

`cpu.weight` je relative share pri contention. `cpu.max` môže nastaviť hard quota/period, napríklad:

```text
200000 100000
→ približne maximum 2 CPU-seconds na 100 ms period
```

`cpu.stat` môže ukázať `nr_throttled` a `throttled_usec`. Rast pri application latency testuje CPU quota hypothesis. Neznamená automaticky, že limit je chybný; workload môže legitímne prekračovať dohodnutý budget.

Docker `--cpus=2` je high-level runtime input; effective kernel cgroup file je read-back. Docker resource documentation opisuje CPU limit semantics a dostupné controls. citeturn973841search14

## 11. Memory high, max a OOM

```text
memory.high
→ pressure/reclaim/throttling boundary

memory.max
→ hard upper limit
```

Pri prekročení hard limitu môže kernel zabiť process v cgroup. `memory.events` rozlišuje counters ako `high`, `max`, `oom` a `oom_kill` podľa kernel version/semantics.

```bash
cat "$cgroup_dir/memory.events"
journalctl -k --since '10 minutes ago' | grep -Ei 'oom|killed process|memory cgroup'
```

Exit code `137` je compatible so SIGKILL, ale sám nepreukazuje OOM. Kernel/cgroup events odlíšia manual kill, daemon timeout a OOM.

## 12. PID limits

`pids.max` limituje počet kernel tasks v cgroup. Threads sa tiež počítajú podľa kernel task modelu.

```text
thread/process growth
→ pids.current reaches pids.max
→ clone/fork returns EAGAIN
```

Docker môže hlásiť `Resource temporarily unavailable`; Docker run reference uvádza failure pri PID limite. citeturn973841search16

Application thread pool, process supervisors a sidecars musia byť započítané do limit designu.

## 13. Capabilities

Linux capabilities rozdeľujú časť tradičnej root authority. Capability sets zahŕňajú permitted, effective, inheritable, bounding a ambient. citeturn973841search12

Minimum model:

```text
drop ALL
→ add only exact required capability
→ verify forbidden operation still fails
```

Docker example:

```bash
docker run --rm \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  --user 10001:10001 \
  registry.example/atlas/payments@sha256:amd104
```

Process inspection:

```bash
grep '^Cap' "/proc/$container_pid/status"
nsenter -t "$container_pid" -m -p capsh --print
```

Hex masks/capsh output preukazujú current capability sets. Nepreukazujú all effective authority because filesystem permissions, user namespace, open FDs, devices and LSM matter too.

`CAP_SYS_ADMIN` je veľmi široká a často signalizuje, že workload boundary je zle navrhnutá.

## 14. `no_new_privs`

`no_new_privs` bráni processu a descendants získať nové privileges cez `execve`, napríklad setuid binary alebo file capabilities. Neodstraňuje už existujúce capabilities ani inherited file descriptors.

```bash
grep '^NoNewPrivs' "/proc/$container_pid/status"
```

Docker/OCI runtime policy má túto value explicitne viazať k workload class-e.

## 15. Seccomp

Seccomp filter hodnotí syscalls a môže allow, return errno, trap alebo kill. Povolený syscall môže stále zlyhať na capability, namespace, LSM alebo object permission.

Practical evidence:

```bash
grep '^Seccomp' "/proc/$container_pid/status"
journalctl -k --since '10 minutes ago' | grep -i seccomp
```

`EPERM` nie je automaticky seccomp proof. Audit record, syscall name/number, architecture a profile identity sú potrebné. Profile musí byť testovaný pre actual language runtime a features, nie genericky vypnutý pri prvom denial.

## 16. SELinux a AppArmor

LSM policy pridáva subject–object–operation decision.

```bash
cat "/proc/$container_pid/attr/current"
docker inspect atlas-payments \
  --format 'AppArmor={{.AppArmorProfile}} SecurityOpt={{json .HostConfig.SecurityOpt}}'

ausearch -m AVC,USER_AVC -ts recent 2>/dev/null || true
```

Unix permissions môžu povoľovať write a SELinux ho odmietne. AppArmor môže zablokovať path/capability behavior. LSM vypnutie nie je root-cause fix; najprv treba overiť profile a volume labeling.

## 17. Devices a runtime socket

Device access otvára host kernel subsystem. Docker socket poskytuje daemon API, cez ktoré caller môže vytvoriť privileged container, mountnúť host paths a získať host-level authority.

Forbidden runtime assertions:

```bash
docker inspect atlas-payments | jq -e '
  .[0].HostConfig.Privileged == false
  and (.[0].HostConfig.Binds // [] | all(contains("docker.sock") | not))
  and (.[0].HostConfig.Devices // [] | length == 0)
'
```

Tento check preukazuje listed Docker configuration fields. Nepreukazuje absence equivalent daemon access cez TCP socket alebo inherited host FD.

## 18. Privileged a namespace-sharing collapse

High-risk switches:

```text
--privileged
--pid=host
--network=host
--ipc=host
--cgroupns=host
broad --cap-add
writable /proc or /sys
host root bind mount
runtime socket
```

Každý mení inú isolation layer. „Privileged“ nie je jedna capability; prakticky uvoľňuje viac runtime controls. Legitímne low-level workloady potrebujú dedicated node/VM boundary, exact device/capability inventory a stronger monitoring.

## 19. Worked incident `CTR-PAY-80`: diagnostics variant

Diagnostics container použil:

```yaml
network_mode: host
privileged: true
volumes:
  - /sys:/sys
  - /var/run/docker.sock:/var/run/docker.sock
```

Mechanizmus:

```text
host network view
+ broad capability/device access
+ writable kernel interface
+ daemon admin API
→ container boundary no longer matches ordinary workload threat model
```

Recovery treats node as compromised:

1. cordon/isolate node;
2. preserve container, daemon and kernel evidence;
3. revoke node/workload credentials;
4. rebuild node from trusted image;
5. replace diagnostics with narrow read-only API;
6. test policy rejection of host namespaces/socket/privileged mode.

## 20. Worked incident: exit 137 misclassified

Container stopped with code 137. Operator raised memory limit without evidence. Actual cause was daemon stop timeout followed by SIGKILL because shell PID 1 did not forward SIGTERM.

Competing evidence:

```text
memory.events oom_kill unchanged
+ daemon stop event
+ application received no SIGTERM log
+ shell remains PID 1
→ forced termination, not OOM
```

Fix is exec-form process/init and graceful termination test, not arbitrary memory increase.

## 21. Competing hypotheses pri `permission denied`

```text
H1: UID/GID or file mode/ACL
H2: user namespace mapping
H3: missing capability
H4: no_new_privs/setuid transition
H5: seccomp denial
H6: SELinux/AppArmor denial
H7: read-only mount/rootfs
H8: device cgroup/runtime restriction
H9: wrong namespace/path view
H10: host filesystem feature mismatch
```

Evidence order:

```bash
id
namei -om /target/path
findmnt /target/path
grep -E '^(Uid|Gid|Cap|NoNewPrivs|Seccomp)' "/proc/$container_pid/status"
cat "/proc/$container_pid/attr/current"
journalctl -k --since '10 minutes ago'
```

Test lowest relevant layer first. Do not use `--privileged` as diagnosis because it changes many hypotheses simultaneously and destroys discrimination.

## 22. Acceptance a forbidden paths

```text
all namespace sharing decisions are explicit
+ host PID and namespace IDs are recorded
+ cgroup path/process membership is correct
+ CPU/memory/PID limits are effective and observable
+ capability set is minimal
+ no_new_privs/seccomp/LSM are active as designed
+ runtime socket/host root/devices are absent
+ PID 1 handles signals and reaps children
+ OOM and forced-kill paths are distinguishable
+ forbidden syscall/capability/mount tests fail
+ second container gets same effective policy
```

## 23. Kontrolné otázky

1. Prečo namespace nie je automatický security verdict?
2. Ako overíš, či container zdieľa host network alebo PID namespace?
3. Aké povinnosti má PID 1?
4. Prečo read-only rootfs nestačí bez mount inventory?
5. Čo user namespace mapping mení?
6. Čo preukazuje cgroup membership a controller files?
7. Ako sa CPU throttling líši od CPU shortage?
8. Prečo exit 137 nie je automaticky OOM?
9. Ako capability sets dopĺňajú UID model?
10. Čo `no_new_privs` chráni a čo nie?
11. Ako odlíšiš seccomp, LSM a filesystem denial?
12. Prečo privileged mode nie je vhodný diagnostický experiment?

## Glossary impact

Relevantné pojmy: Linux namespace, namespace inode, PID namespace, mount namespace, network namespace, user namespace, UID mapping, cgroup v2, CPU quota, memory.high, memory.max, OOM kill, pids.max, Linux capability, bounding set, ambient capability, no_new_privs, seccomp, SELinux, AppArmor, device access a privileged mode.

## Primárne zdroje

- [OCI Linux container configuration](https://github.com/opencontainers/runtime-spec/blob/main/config-linux.md)
- [Linux namespaces](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [Linux capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Linux cgroup v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
- [Docker resource constraints](https://docs.docker.com/engine/containers/resource_constraints/)

<!-- KNOWLEDGE-NAVIGATION:START -->
[← Predchádzajúca: Containers vs. virtual machines](containers-vs-virtual-machines.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OCI image a runtime standards →](oci-image-runtime-standards.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
