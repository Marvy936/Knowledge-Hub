# Namespaces, cgroups a capabilities

Linux container nevzniká jedným prepínačom. Runtime skladá jeho hranicu z viacerých kernelových mechanizmov, pričom každý rieši inú časť problému. Namespaces menia to, čo proces vidí. Cgroups riadia, koľko zdrojov môže spotrebovať a ako sa jeho spotreba účtuje. Credentials a capabilities určujú, ktoré privilegované operácie smie vykonať. Seccomp filtruje syscalls a SELinux alebo AppArmor rozhodujú, či môže konkrétny proces pracovať s konkrétnym objektom.

Túto kapitolu budeme sledovať na containere `payments-api`. Aplikácia potrebuje počúvať na porte `8080`, zapisovať do jedného volume-u a komunikovať s databázou. Nepotrebuje spravovať sieťové rozhrania, mountovať filesystems, čítať hostiteľské procesy ani pristupovať k zariadeniam. Z toho vyplýva, že správna runtime policy má byť úzka: non-root user, oddelené namespaces, cgroup limity, odstránené capabilities, read-only root filesystem a explicitné writable mounts.

## 1. Kernel stále rozhoduje nad procesom

Docker CLI pracuje s objektom nazvaným container, ale kernel nakoniec rozhoduje nad konkrétnym procesom. Relevantný stav procesu možno čítať cez `/proc`:

```bash
cat /proc/1/status
cat /proc/1/cgroup
readlink /proc/1/ns/pid
readlink /proc/1/ns/mnt
readlink /proc/1/ns/net
```

Vo vnútri containeru môže hlavný proces vidieť seba ako PID 1. Hostiteľ ho však vidí pod iným PID. Process môže mať UID `65532` v user namespace, ale na hoste môže byť mapovaný na úplne iné číslo. Rovnako môže mať vlastný network namespace, no pakety aj tak prechádzajú hostiteľským routingom, firewallom a NAT pravidlami.

Preto nestačí veta „container je izolovaný“. Potrebujeme vedieť, ktoré namespaces používa, v ktorej cgroup beží, aké capabilities má, či je zapnuté `no_new_privs`, aký seccomp profil sa aplikuje a aké mounts alebo zariadenia dostal.

## 2. Namespaces menia pohľad na systém

Namespace nevytvára nový kernel. Vytvára oddelený pohľad na vybranú časť kernelového state-u. PID namespace mení process tree a PID čísla. Mount namespace mení mount table. Network namespace poskytne vlastné interfaces, routes, sockets a port space. UTS namespace mení hostname. IPC namespace oddeľuje System V IPC a POSIX message queues. User namespace mapuje UID a GID a mení scope capabilities.

Najjednoduchší spôsob, ako si namespace predstaviť, je porovnať dva procesy, ktoré sa pozerajú na ten istý hostiteľský kernel cez iné okno. Jeden proces vidí host process tree, druhý iba procesy vo svojom PID namespace. Jeden vidí host `eth0`, druhý iba loopback a virtuálne `eth0` pripojené cez veth pair.

Pri Dockeri možno namespace identity zobraziť cez hostiteľský PID containeru:

```bash
container_id="$(docker run -d --rm --name ns-demo alpine:3.22 sleep 300)"
host_pid="$(docker inspect ns-demo --format '{{.State.Pid}}')"

printf 'host PID: %s\n' "$host_pid"
ls -l "/proc/$host_pid/ns"
```

`ls -l` zobrazí symlinky s namespace inode identitami. Dva procesy s rovnakou hodnotou pri `net:[...]` sú v tom istom network namespace. To je praktickejší dôkaz než názov containeru.

## 3. PID namespace a význam PID 1

Hlavný proces nového PID namespace-u vidí seba ako PID 1. To nie je iba kozmetické prečíslovanie. PID 1 má špecifické správanie pri signáloch a musí zbierať ukončené child procesy.

Chybný shell wrapper môže vyzerať takto:

```sh
#!/bin/sh
/usr/local/bin/payments-api serve
```

Shell zostane PID 1 a aplikácia bude jeho child. Keď runtime pošle `SIGTERM`, dostane ho shell. Ak ho neforwarduje, aplikácia nemusí korektne ukončiť rozpracované requesty. Bezpečnejšia verzia používa `exec`:

```sh
#!/bin/sh
exec /usr/local/bin/payments-api serve
```

Po `exec` sa shell nahradí aplikáciou a aplikácia sa stane PID 1. Pri priamom exec-form Dockerfile entrypointe shell vôbec nevznikne:

```dockerfile
ENTRYPOINT ["/usr/local/bin/payments-api"]
CMD ["serve"]
```

Runtime stav overíš takto:

```bash
docker top payments-api -eo pid,ppid,user,args
docker inspect payments-api --format '{{json .Config.Entrypoint}} {{json .Config.Cmd}}'
```

Zelený `docker stop` ešte nepreukazuje, že aplikácia dokončila všetky business side effects. Preukazuje iba process-level termination. Pri payments službe treba navyše overiť, že rozpracovaný request bol commitnutý, bezpečne prerušený alebo idempotentne zopakovateľný.

## 4. Mount namespace a root filesystem

Mount namespace určuje, ktoré filesystem mounts proces vidí. Runtime typicky zostaví výsledný pohľad z image layers, zapisovateľnej container layer, `proc`, `sysfs`, `tmpfs`, bind mountov a volumes.

```text
read-only image layers
+ per-container writable layer
+ /proc, /dev a ďalšie runtime mounts
+ named volumes alebo bind mounts
+ tmpfs
→ výsledný mount namespace
```

Read-only root filesystem je užitočný, pretože aplikácia nemôže náhodne alebo po kompromitácii meniť image filesystem. Potrebné writable paths sa pridajú explicitne:

```bash
docker run --rm \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --mount type=volume,source=payments-data,target=/var/lib/atlas-payments \
  IMAGE
```

Takýto príkaz zároveň dokumentuje, kde sa očakáva zápis. Ak aplikácia skúsi zapisovať do `/etc` alebo `/usr/local`, zlyhanie je signál, že runtime contract a aplikácia sa rozchádzajú.

Mount namespace však nie je automaticky bezpečný. Writable bind mount hostiteľského `/` alebo `/etc` dá procesu priamu cestu k host state-u. Mount `/var/run/docker.sock` poskytne prístup k Docker API a často prakticky aj schopnosť vytvoriť nový privileged container. Preto sa každý host mount posudzuje ako samostatná trust boundary, nie iba ako „ďalší adresár“.

## 5. Network namespace a bind address

Network namespace má vlastné interfaces, routes, ARP alebo neighbor state, firewall hooks a port space. Pri bežnom Docker bridge modeli dostane container virtuálne `eth0`, ktoré je cez veth pair pripojené k bridge-u na hoste.

```text
payments-api process
→ container eth0
→ veth pair
→ Docker bridge
→ host routing/firewall/NAT
→ externá sieť
```

Loopback `127.0.0.1` patrí vždy konkrétnemu network namespace. Ak aplikácia počúva iba na `127.0.0.1:8080` vo vnútri containeru, lokálny healthcheck môže prejsť, ale pakety prichádzajúce cez container `eth0` sa k listeneru nedostanú.

Rozdiel sa dá reprodukovať jednoduchým serverom:

```bash
docker run --rm -d --name loopback-demo \
  -p 127.0.0.1:18080:8080 \
  python:3.14-alpine \
  python -m http.server 8080 --bind 127.0.0.1
```

Process vo vnútri containeru počúva, ale host request na publikovaný port zlyhá. Oprava je bind na `0.0.0.0` alebo `:8080`, nie pridanie ďalšieho port mappingu.

## 6. User namespace a rozdiel medzi container root a host root

User namespace môže mapovať UID a GID z containeru na iný rozsah hostiteľských ID. Container UID 0 tak nemusí byť host UID 0.

```text
container UID 0
→ host UID 231072
```

Docker `userns-remap` a rootless mode používajú túto vlastnosť na zníženie dopadu kompromitácie. Process môže mať capabilities vo svojom user namespace, ale nemá automaticky rovnakú authority v parent alebo initial user namespace hosta.

Mapovanie možno čítať cez:

```bash
cat /proc/self/uid_map
cat /proc/self/gid_map
```

User namespace však prináša praktické dôsledky. Bind-mounted host file môže mať ownership, ktorý sa po mapovaní javí ako neprístupný. Niektoré zariadenia alebo mount operácie vyžadujú authority v parent namespace. Rootless runtime má obmedzenia pri low ports, cgroups alebo vybraných network operáciách podľa host konfigurácie.

Preto tvrdenie „beží to ako root v containere“ nie je úplný security verdict. Potrebujeme vedieť, či sa používa user namespace, aké je mapovanie a ktoré host objects sú pripojené do mount namespace-u.

## 7. Cgroups riadia zdroje a účtovanie

Namespaces hovoria, čo proces vidí. Cgroups hovoria, koľko môže spotrebovať a kde sa jeho spotreba účtuje. Na moderných systémoch sa používa cgroup v2 s unified hierarchy.

Docker flags sa premietnu do cgroup policy:

```bash
docker run --rm -d --name constrained \
  --cpus 0.50 \
  --memory 256m \
  --pids-limit 128 \
  alpine:3.22 sleep 300
```

Stav možno pozorovať cez Docker API:

```bash
docker inspect constrained --format '{{json .HostConfig}}' | jq '{NanoCpus,Memory,PidsLimit}'
docker stats --no-stream constrained
```

Na hoste možno podľa konfigurácie systemd a Docker Engine nájsť cgroup path cez `/proc/<pid>/cgroup`. Konkrétne názvy adresárov sa líšia podľa cgroup drivera, preto nie je bezpečné hardcodovať jednu cestu bez read-backu.

## 8. CPU: weight, quota a throttling

CPU weight vyjadruje relatívnu prioritu pri contention. Neznamená rezerváciu konkrétneho jadra. CPU quota obmedzuje, koľko CPU času môže cgroup spotrebovať v určitej perióde.

Pri `--cpus 0.50` dostane workload približne polovicu jedného CPU času. Keď aplikácia spotrebuje kvótu pred koncom periódy, kernel ju throttluje. To sa môže prejaviť zvýšenou latenciou aj vtedy, keď host na prvý pohľad nemá 100 % CPU utilisation.

Pozorovanie má spájať runtime a aplikáciu:

```bash
docker stats --no-stream payments-api
cat /proc/pressure/cpu
```

Na hostiteľskej cgroup možno sledovať `cpu.stat`, najmä throttling counters. Samotná vysoká CPU hodnota však ešte nie je problém. Rozhoduje, či workload prekračuje SLO, či je throttlovaný a či sa problém objavil po zmene trafficu, limitu alebo aplikačného release-u.

## 9. Memory limit a cgroup OOM

Memory limit nie je iba upozornenie. Keď cgroup prekročí `memory.max` a kernel nevie tlak vyriešiť reclaimom, môže ukončiť proces v danej cgroup.

Docker potom často ukáže exit code `137` alebo `OOMKilled=true`:

```bash
docker inspect payments-api \
  --format 'exit={{.State.ExitCode}} oom={{.State.OOMKilled}} error={{.State.Error}}'
```

Exit `137` však sám osebe nepreukazuje cgroup OOM. Môže vzniknúť aj po manuálnom `SIGKILL`. Rozhodujúci je kombinovaný stav Engine-u, kernelových udalostí, cgroup counters a časovej osi.

Pri memory incidente rozlišuj application leak, legitímny burst, page cache, host-level pressure a nesprávne nízky limit. Sleduj aj memory pressure pred samotným OOM, pretože workload môže byť výrazne pomalý ešte pred ukončením procesu.

## 10. PID limit a thread explosion

Cgroup `pids.max` obmedzuje počet tasks, čo zahŕňa procesy aj threads podľa kernelového modelu. Aplikácia, ktorá nekontrolovane vytvára workers, môže naraziť na limit a dostať `EAGAIN` alebo hlášku `Resource temporarily unavailable`.

```bash
docker run --rm --pids-limit 32 IMAGE
```

To je useful containment proti fork bomb alebo chybnému thread poolu. Zároveň však príliš nízky limit môže rozbiť jazykový runtime, ktorý legitímne vytvára viac threads. Limit preto musí vychádzať z pozorovaného workload modelu a testovať sa pod záťažou.

## 11. Capabilities rozdeľujú tradičné root oprávnenia

Linux root historicky predstavoval veľmi širokú authority. Capabilities ju rozdeľujú na samostatné oprávnenia, napríklad `CAP_NET_BIND_SERVICE`, `CAP_CHOWN`, `CAP_SETUID`, `CAP_NET_ADMIN` alebo veľmi širokú `CAP_SYS_ADMIN`.

Pre bežnú HTTP službu je vhodný model:

```bash
docker run --rm \
  --user 65532:65532 \
  --cap-drop ALL \
  --security-opt no-new-privileges=true \
  IMAGE
```

Port `8080` nevyžaduje `CAP_NET_BIND_SERVICE`, takže aplikácia nepotrebuje žiadnu capability. Ak by musela počúvať na low porte, lepšie je často publikovať host port `443` na container port `8443` alebo `8080`, než pridávať ďalšiu authority do workloadu.

Effective capabilities možno zobraziť cez `/proc/<pid>/status` alebo nástroj `capsh`, ak je v debug image-i:

```bash
grep '^Cap' /proc/1/status
```

Capabilities existujú v niekoľkých sets: permitted, effective, inheritable, bounding a ambient. Bounding set je horná hranica, ktorú proces po spustení nevie prekročiť. Preto `--cap-drop ALL` nie je iba kozmetika; odstráni možnosť získať capabilities späť cez bežný exec transition.

## 12. `no_new_privs`, seccomp a LSM

`no_new_privs` zakáže procesu a jeho descendants získať nové privileges cez `execve`, napríklad pomocou setuid binary alebo file capabilities. Neodstráni však oprávnenia, ktoré proces už má, ani nezruší prístup cez otvorené file descriptors alebo mounts.

Seccomp filtruje syscalls. Docker používa default profil, ktorý povoľuje bežné syscalls a blokuje vybrané rizikové operácie. Keď syscall prejde seccomp filtrom, stále môže zlyhať na capability, namespace, filesystem permissions alebo LSM policy.

SELinux a AppArmor pridávajú object-level confinement. Unix mode môže povoľovať zápis, ale SELinux label combination ho odmietne. Pri chybe `permission denied` preto nie je správne okamžite spustiť container s `--privileged`. Najprv treba zistiť, ktorá vrstva denial vytvorila.

Praktický troubleshooting začína read-backom runtime policy:

```bash
docker inspect payments-api | jq '.[0] | {
  User: .Config.User,
  CapDrop: .HostConfig.CapDrop,
  CapAdd: .HostConfig.CapAdd,
  SecurityOpt: .HostConfig.SecurityOpt,
  ReadonlyRootfs: .HostConfig.ReadonlyRootfs,
  Mounts: .Mounts
}'
```

Potom sa skontrolujú application logs, host audit logs a konkrétny path alebo syscall. Dočasné vypnutie policy môže byť diagnostický experiment v izolovanom prostredí, ale nie produkčná oprava.

## 13. Prečo je `--privileged` kolaps boundary

Privileged mode výrazne rozširuje capabilities, devices a ďalšie runtime oprávnenia. V kombinácii s host PID namespace-om, host mounts alebo Docker socketom sa container stáva prakticky host-admin workloadom.

```bash
docker run --rm -it --privileged \
  --pid host \
  -v /:/host \
  -v /var/run/docker.sock:/var/run/docker.sock \
  alpine:3.22 sh
```

Takýto príkaz je vhodný skôr ako ukážka toho, čomu sa vyhnúť. Ak nástroj potrebuje čítať jeden log adresár, má dostať narrow read-only bind mount. Ak potrebuje jednu capability, pridá sa iba tá. Ak skutočne potrebuje host-level authority, má mať dedicated node alebo VM a explicitný operational trust model.

## 14. Incident: zelený container nevedel zapisovať do volume-u

Po hardeningu `payments-api` prešla na non-root UID `65532`, read-only root filesystem a `cap-drop ALL`. Container sa spustil, process existoval a `/healthz` vracal `200`. Payment request však končil `permission denied`.

Failure chain bol:

```text
named volume vznikol ako root:root
→ runtime beží ako UID 65532
→ healthcheck testuje iba process a HTTP loopback
→ container je označený healthy
→ POST /payments otvorí data file
→ kernel odmietne write podľa ownershipu a mode
```

Správna diagnostika nezačala pridaním `--privileged`. Tím porovnal `.Config.User`, `.Mounts`, volume identity a ownership data pathu pomocou controlled debug containeru. Oprava zaviedla explicitný one-shot initializer, ktorý pripravil adresár pre UID `65532`, a readiness endpoint začal testovať write capability na tom istom data path-e.

Tento incident ukazuje, prečo sa jednotlivé vrstvy nesmú zlúčiť. Namespace izolácia fungovala. Cgroup limity fungovali. Capability policy fungovala. Chyba bola v contracte medzi numeric identity a persistentným filesystem objectom.

## 15. Systematický postup pri `permission denied`

Pri permission chybe si najprv zafixuj proces, objekt a operáciu. Potrebuješ vedieť, ktorý UID/GID proces používa, aké capabilities má, ktorý path otvára, odkiaľ je path mountnutý a či je root filesystem alebo mount read-only.

```bash
docker inspect CONTAINER
docker logs --timestamps CONTAINER
docker top CONTAINER -eo pid,ppid,user,args
docker volume inspect VOLUME
```

Následne vytvor competing hypotheses: Unix ownership, read-only mount, chýbajúca capability, seccomp denial, SELinux/AppArmor denial, user namespace mapping alebo mount obscuring. Každá hypotéza má iný observation point. `docker inspect` ukáže runtime konfiguráciu, audit log môže ukázať LSM denial a debug workload s rovnakým volume-om môže ukázať reálny ownership.

Recovery je uzavretá až vtedy, keď prejde pôvodná operácia aj zakázaná kontrola. `payments-api` musí vedieť zapisovať iba do svojho volume-u, ale stále nesmie zapisovať do `/etc`, používať host devices alebo získať broad capabilities.

## Čo si z kapitoly odniesť

Namespaces, cgroups a capabilities nie sú tri synonymá pre container isolation. Namespaces menia pohľad procesu, cgroups riadia resources a accounting a capabilities rozdeľujú privilegované operácie. Seccomp a LSM policy pridávajú ďalšie rozhodovacie vrstvy.

Bezpečný runtime vzniká ich konzistentnou kompozíciou: správny user a user mapping, oddelené namespaces, pravdivé resource limity, minimum capabilities, `no_new_privs`, vhodný seccomp profil, explicitné mounts a overené filesystem labels. Keď operácia zlyhá, treba nájsť konkrétnu vrstvu denialu, nie boundary plošne vypnúť.

## Primárne zdroje

- [Docker Engine security](https://docs.docker.com/engine/security/)
- [Running containers](https://docs.docker.com/engine/containers/run/)
- [Runtime metrics](https://docs.docker.com/engine/containers/runmetrics/)
- [Resource constraints](https://docs.docker.com/engine/containers/resource_constraints/)
- [User namespace remapping](https://docs.docker.com/engine/security/userns-remap/)
- [Rootless mode](https://docs.docker.com/engine/security/rootless/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Containers vs. virtual machines](containers-vs-virtual-machines.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OCI image a runtime standards →](oci-image-runtime-standards.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
