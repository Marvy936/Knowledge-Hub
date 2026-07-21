# Docker troubleshooting

Docker troubleshooting musí postupovať po vrstvách. Rovnaký symptom môže vzniknúť v application procese, image artifacte, runtime configuration, containerd/OCI runtime, Docker daemone, host kernel, filesysteme, networke, registry alebo Compose modeli. Náhodné reštarty a `prune` príkazy často odstránia evidence bez odstránenia príčiny.

## 1. Diagnostický model

Používaj poradie:

```text
symptom a čas
→ Docker context/client
→ daemon a runtime
→ container state
→ application process
→ image/config
→ mounts/storage
→ network/DNS
→ host kernel/resources
→ external dependencies
```

Najprv odpovedz:

1. Čo presne zlyhalo?
2. Kedy sa to začalo?
3. Čo sa zmenilo?
4. Je problém na jednom containeri, hoste, image digeste alebo environment-e?
5. Je failure reprodukovateľný?
6. Aké evidence zmiznú po restart/delete/prune?

## 2. Evidence pred zásahom

Pred zmenou alebo odstránením containeru zachovaj:

```bash
docker version
docker info
docker context show
docker ps -a --no-trunc
docker inspect <container>
docker logs --timestamps --tail=500 <container>
docker events --since 30m
docker stats --no-stream
docker system df -v
```

Podľa incidentu aj:

- daemon logs,
- kernel journal a OOM events,
- network rules/routes/conntrack,
- filesystem capacity a inodes,
- Compose resolved config,
- image digest a history,
- volume/network inspect,
- application metrics/traces.

Output môže obsahovať secrets. Ukladaj ho do chráneného incident artifactu s retention policy.

## 3. Over Docker context

```bash
docker context ls
docker context show
docker info --format '{{.Name}}'
```

Častá chyba:

- CLI je lokálny,
- aktívny context smeruje na remote host,
- operator diagnostikuje alebo maže nesprávne resources.

Pri CI zaznamenaj endpoint identity bez vypísania credentials.

## 4. Client a server compatibility

```bash
docker version
```

Rozlišuj:

- client version,
- server/Engine version,
- API versions,
- containerd version,
- OCI runtime version,
- Docker Desktop version.

Novší client môže vyjednať staršiu API verziu, ale konkrétna feature môže zostať nepodporovaná.

## 5. `Cannot connect to the Docker daemon`

Možné príčiny:

- daemon nebeží,
- nesprávny context alebo `DOCKER_HOST`,
- socket neexistuje,
- user nemá permission,
- remote SSH/TLS endpoint je nedostupný,
- Docker Desktop VM/backend nebeží,
- daemon startup zlyhal na configuration konflikte.

Kontrola:

```bash
docker info
systemctl status docker
journalctl -u docker.service --since "30 min ago"
ls -l /var/run/docker.sock
printf '%s\n' "$DOCKER_HOST"
```

Neopravuj socket permissions cez world-writable mode. Členstvo v Docker group je privilegovaný host access.

## 6. Daemon startup failure

Skontroluj:

- `daemon.json` syntax,
- rovnakú option zadanú flagom aj config file-om,
- storage driver a data-root,
- registry certificates/mirrors,
- firewall/backend configuration,
- cgroup support,
- disk a inode capacity,
- plugin/runtime paths.

Validuj JSON a čítaj prvý relevantný startup error, nie iba následné dependency failures.

Manuálne spustenie `dockerd` s iným environmentom môže zmeniť správanie oproti systemd service. Používaj ho iba ako kontrolovaný diagnostický krok.

## 7. Daemon logs a debug

Na systemd Linux hoste:

```bash
journalctl -u docker.service --since "1 hour ago"
journalctl -xu docker.service
```

Docker daemon debug možno dočasne povoliť cez podporovanú daemon configuration. Debug logging:

- zvyšuje objem logov,
- môže zachytiť citlivé metadata,
- potrebuje časovo obmedzené použitie,
- po incidente ho vypni.

Ak je daemon na Linuxe zablokovaný, `SIGUSR1` môže zapísať goroutine/thread stack trace do daemon logu bez jeho ukončenia:

```bash
sudo kill -SIGUSR1 "$(pidof dockerd)"
```

Použi iba podľa platformovej dokumentácie a incident postupu.

## 8. Container state

```bash
docker ps -a --no-trunc
docker inspect --format '{{json .State}}' <container>
```

Dôležité fields:

- status,
- running/paused/restarting,
- exit code,
- error,
- started/finished time,
- OOMKilled,
- health status,
- restart count podľa dostupných inspect dát.

`Exited (0)` môže byť správny one-shot job alebo chybný service command, ktorý okamžite skončil úspešne.

## 9. Exit codes

Bežná interpretácia:

- `0` — process skončil úspešne,
- application-specific non-zero — application error,
- `126` — command existuje, ale nemožno ho vykonať,
- `127` — command sa nenašiel,
- `128 + signal` — process skončil signalom,
- `137` — často `SIGKILL`, napríklad OOM alebo forced stop,
- `143` — často `SIGTERM` pri graceful stop path.

Exit code nie je úplná root cause. Koreluj ho s kernel, daemon a application logs.

## 10. Container restart loop

```bash
docker inspect <container>
docker logs --timestamps <container>
docker events --filter container=<container>
```

Over:

- restart policy,
- command/entrypoint,
- missing configuration alebo secret,
- dependency startup,
- write permissions,
- health/remediation controller,
- OOM,
- application crash,
- migration failure.

Dočasné vypnutie restart policy môže pomôcť zachovať failure state, ale mení desired behavior; zaznamenaj zásah.

## 11. Logs

```bash
docker logs --timestamps --since 30m <container>
docker logs -f --tail=200 <container>
```

`docker logs` funguje podľa logging drivera a jeho read supportu. Application má logovať na stdout/stderr, nie iba do ephemeral file-u v writable layeri.

Over:

```bash
docker inspect --format '{{.HostConfig.LogConfig.Type}}' <container>
docker info --format '{{.LoggingDriver}}'
```

Riziká:

- unbounded `json-file` logs zaplnia disk,
- multiline stack traces sa zle parsujú,
- secrets v logs vyžadujú rotation a audit,
- remote logging outage môže podľa drivera ovplyvniť application behavior.

## 12. `docker inspect`

Inspection poskytuje resolved runtime configuration:

```bash
docker inspect <container>
docker inspect <image>
docker inspect <network>
docker inspect <volume>
```

Kontroluj:

- image ID/digest,
- command a entrypoint,
- environment bez nebezpečného zverejnenia,
- user a working directory,
- mounts,
- networks/IPs/aliases,
- ports a bind addresses,
- resource limits,
- security options,
- healthcheck,
- labels a Compose project metadata.

Porovnávaj actual inspect s versionovaným desired modelom.

## 13. Process inspection

```bash
docker top <container>
docker exec <container> ps aux
docker exec <container> sh
```

Minimal/distroless image nemusí mať shell ani `ps`. Alternatívy:

- `docker top`,
- `docker inspect`,
- host namespace tools,
- debug image alebo toolbox container,
- application diagnostic endpoint,
- runtime-specific namespace entry podľa oprávnení.

Nepridávaj shell do production image iba kvôli incidentu bez zváženia attack surface.

## 14. PID 1 a signals

Symptómy:

- container sa dlho zastavuje,
- Docker po timeout-e použije `SIGKILL`,
- child processes zostávajú alebo sa nereapujú,
- application nedokončí request/flush.

Over:

- exec vs. shell form,
- wrapper script a `exec`,
- application signal handler,
- stop signal,
- stop timeout,
- child process lifecycle.

Test:

```bash
time docker stop <container>
docker events --filter container=<container>
```

## 15. Resource pressure

```bash
docker stats --no-stream
docker inspect <container>
```

Host evidence:

```bash
journalctl -k --since "30 min ago"
dmesg -T | grep -i -E 'oom|killed process'
cat /proc/pressure/cpu
cat /proc/pressure/memory
cat /proc/pressure/io
```

Rozlišuj:

- cgroup memory limit,
- host-wide OOM,
- CPU throttling,
- I/O pressure,
- PID limit,
- open-file/socket limits,
- disk quota.

Vysoké CPU percento môže znamenať useful work, busy loop alebo throttling. Potrebuješ application a cgroup metrics.

## 16. OOMKilled

```bash
docker inspect --format '{{.State.OOMKilled}} {{.State.ExitCode}}' <container>
```

Over:

- memory limit,
- working set a cache,
- application heap settings,
- host memory pressure,
- swap policy,
- concurrent workload spike,
- kernel OOM log.

Zvýšenie limitu bez analýzy môže iba presunúť incident na host level.

## 17. Disk a inodes

```bash
docker system df
docker system df -v
df -h
df -i
```

Docker disk používajú:

- images a layers,
- container writable layers,
- local volumes,
- build cache,
- container logs,
- content/snapshot stores,
- temporary pull/build data.

Disk môže mať voľné GB, ale vyčerpané inodes. Alebo naopak.

Pred `docker system prune` identifikuj ownera a retention. Prune môže odstrániť build cache, stopped containers, unused networks alebo images podľa options, ale nemusí vyriešiť growing volume/application logs.

## 18. Image pull failure

Symptómy:

- authentication denied,
- manifest unknown,
- platform mismatch,
- TLS/certificate error,
- rate limit,
- digest mismatch,
- timeout.

Over:

```bash
docker pull registry.example.com/example/app@sha256:...
docker image inspect <reference>
docker manifest inspect <reference>
```

Skontroluj:

- registry/repository spelling,
- credentials a scope,
- tag vs. digest,
- target platform,
- proxy/DNS/CA trust,
- registry availability,
- local stale tag.

## 19. `exec format error`

Typické príčiny:

- image alebo binary pre inú architecture,
- invalid shebang,
- Windows line endings v script-e,
- chýbajúci interpreter,
- binary bez executable permission.

Kontrola:

```bash
docker image inspect <image>
file ./binary
head -n 1 ./entrypoint.sh
```

Pri multi-platform image over platform-specific manifest, nie iba index tag.

## 20. `no such file or directory`, hoci file existuje

Často chýba:

- dynamic linker,
- shared library,
- interpreter zo shebang-u,
- správny architecture loader.

```bash
file ./binary
ldd ./binary
readelf -l ./binary
```

Minimal/scratch image nemusí obsahovať `/bin/sh`, CA certificates, timezone data alebo NSS files.

## 21. Permission denied

Rozlišuj:

- Unix mode/ownership,
- runtime UID/GID,
- user namespace mapping,
- read-only root filesystem,
- volume/bind permissions,
- SELinux/AppArmor denial,
- capability/seccomp restriction,
- noexec mount,
- device cgroup policy.

Kontrola:

```bash
docker inspect <container>
namei -l /host/path
ls -ln /host/path
journalctl -k | grep -i -E 'denied|apparmor|avc'
```

`chmod 777` nie je root cause analysis.

## 22. Mount problems

```bash
docker inspect --format '{{json .Mounts}}' <container>
docker volume inspect <volume>
```

Symptómy:

- image files „zmizli“ — mount prekryl path,
- prázdny bind mount — nesprávny host/context path,
- data sa stratili — boli vo writable layeri alebo inom project volume,
- permission denied — UID/GID/LSM,
- stale data — pripojený iný volume.

Pri remote Docker context-e sa bind source nachádza na daemon hoste, nie nevyhnutne na client machine.

## 23. Network troubleshooting

Začni od application listen socketu:

```bash
docker exec <container> ss -lntup
docker port <container>
docker inspect <container>
docker network inspect <network>
```

Potom:

- service name/DNS,
- container route,
- bridge/veth,
- host bind address,
- NAT/firewall,
- upstream route/security group,
- external client path.

`localhost` v containeri označuje ten istý container network namespace.

## 24. Published port nefunguje

Over:

1. process počúva na správnom container porte,
2. process nepočúva iba na nesprávnej loopback/interface adrese,
3. mapping je `HOST_PORT:CONTAINER_PORT`,
4. host bind je `127.0.0.1` alebo `0.0.0.0` podľa zámeru,
5. port nie je v collision,
6. host firewall/forwarding/NAT,
7. external route a security controls,
8. application health.

```bash
docker port <container>
ss -lntp
curl -v http://127.0.0.1:<host-port>
```

## 25. DNS failure

```bash
docker exec <container> cat /etc/resolv.conf
docker exec <container> getent hosts <service>
docker network inspect <network>
```

Rozlišuj:

- Docker embedded DNS,
- upstream resolver,
- service alias,
- network membership,
- search domain,
- application DNS cache,
- VPN/split DNS,
- IPv4/IPv6 preference.

Container IP nepoužívaj ako trvalú opravu.

## 26. MTU a partial connectivity

Symptómy:

- malé requests fungujú,
- TLS alebo veľké payloady timeoutujú,
- problém iba cez VPN/overlay,
- retransmissions.

Over packet path MTU, PMTUD a firewall ICMP behavior:

```bash
ip link
ip route
tracepath <target>
ping -M do -s <size> <target>
```

## 27. Compose troubleshooting

```bash
docker compose config
docker compose config --environment
docker compose ps -a
docker compose logs --timestamps --tail=500
docker compose images
docker compose top
```

Over:

- project name,
- resolved merge/override,
- image digest,
- environment precedence,
- dependency condition,
- network/volume names,
- orphan resources,
- health status.

Zlyhanie jednej service môže byť následok inej dependency. Zoradiť logs iba podľa service niekedy skryje časovú koreláciu.

## 28. Build troubleshooting

```bash
docker buildx ls
docker buildx inspect --bootstrap
docker buildx build --progress=plain .
docker buildx du
```

Rozlišuj:

- context transfer,
- Dockerfile/frontend parse,
- base image pull,
- cache import,
- `RUN` execution,
- secret/SSH mount,
- platform/emulation,
- output export/push.

Build môže uspieť, ale image nemusí byť v local store, ak nebol použitý `--load` alebo vhodný exporter.

## 29. Cache problems

### Cache sa nepoužíva

Over:

- builder/driver,
- cache ref a auth,
- platform,
- changed inputs,
- BuildKit/frontend version,
- cache retention.

### Cache používa stale remote data

Instruction text a local inputs sa nezmenili, ale package repository áno. Použi explicitný dependency/update policy a kontrolovaný rebuild.

### Clean build zlyhá

Build mal skrytú dependency na local/cache state. To je correctness defect.

## 30. Docker Desktop

Na Windows/macOS over:

- Desktop backend/VM stav,
- WSL2 alebo virtualization support,
- allocated CPU/memory/disk,
- file sharing,
- proxy/VPN/DNS integration,
- Desktop logs a diagnostics,
- Windows vs. Linux container mode.

Bind mount path a `localhost` môžu prechádzať virtualizačnou vrstvou. Nepredpokladaj identické správanie ako native Linux Engine.

## 31. Events

```bash
docker events --since 1h
```

Events pomáhajú korelovať:

- create/start/die/restart,
- health status zmeny,
- image pull/tag/delete,
- network connect/disconnect,
- volume events,
- daemon reload.

Event history je obmedzená a nie je dlhodobý audit systém. Streamuj ju do centralizovanej observability, ak ju potrebuješ pre incidenty.

## 32. Controlled reproduction

Reprodukčný postup:

1. pinni image digest,
2. exportuj resolved runtime configuration bez secrets,
3. izoluj network a volume data,
4. zníž workload na minimálny failing command,
5. zachovaj rovnakú platformu/kernel/runtime,
6. zmeň iba jednu premennú,
7. zaznamenaj výsledok.

„Funguje po rebuild/restart“ nie je root cause, pokiaľ nevieš, ktorý state sa zmenil.

## 33. Remediation hierarchy

Preferuj:

1. opraviť versionovaný source/config,
2. buildnúť nový immutable artifact,
3. otestovať ho,
4. nahradiť runtime instance,
5. overiť health a SLI,
6. zdokumentovať root cause a prevention.

Ručná oprava vo vnútri bežiaceho containeru môže byť núdzový diagnostický krok, ale nesmie zostať authoritative state.

## 34. Anti-patterny

### Reštart ako prvý krok

Môže odstrániť transient evidence a iba dočasne vyčistiť pressure/state.

### `docker system prune -a --volumes` bez analýzy

Môže zmazať rollback images, cache a persistent data.

### Diagnostika iba application logs

Ignoruje daemon, kernel, cgroups, storage a network.

### `docker exec` a ručný package install v production containeri

Vytvára neversionovaný drift.

### Privileged mode alebo host network ako oprava

Odstraňuje security boundary namiesto identifikácie chýbajúcej capability alebo network rule.

### Použitie mutable tagu pri reprodukcii

Pri rovnakom názve môžeš testovať iný image digest.

### Vypísanie celého environmentu

Incident log môže obsahovať secrets.

### Preskočenie restore testu

Existencia volume snapshotu nepreukazuje obnoviteľnosť.

## 35. Praktický checklist

```text
[ ] Presný symptom, čas a dopad
[ ] Aktívny Docker context a host identity
[ ] Client/server/Buildx versions
[ ] Container state, exit code, OOM a health
[ ] Application a daemon logs
[ ] Inspect image/config/mount/network/resources
[ ] Docker events
[ ] Host CPU/memory/I/O/PID pressure
[ ] Disk capacity a inodes
[ ] Registry/image digest/platform
[ ] DNS, routes, firewall, NAT, MTU, conntrack
[ ] Volume identity, ownership, backup
[ ] Compose resolved model a project name
[ ] Posledná zmena a reprodukcia
[ ] Evidence uložená pred restart/delete/prune
```

## 36. Kontrolné otázky

1. Prečo sa Docker incident diagnostikuje po vrstvách?
2. Ktoré evidence treba zachovať pred restartom?
3. Ako odlíšiš client/context problém od daemon failure?
4. Čo ti poskytne `docker inspect`?
5. Prečo exit code `137` nie je automaticky dôkaz cgroup OOM?
6. Ako odlíšiš disk capacity a inode exhaustion?
7. Prečo môže file existovať, ale process hlási `no such file or directory`?
8. Aký je správny postup pri nefunkčnom published porte?
9. Ako zistíš resolved Compose configuration?
10. Prečo clean build failure odhaľuje skrytú cache dependency?

## Glossary impact

Relevantné pojmy: Docker diagnostic baseline, daemon log, container exit code, OOMKilled, restart loop, Docker event, resolved runtime configuration, Docker disk usage, inode exhaustion, platform mismatch, runtime dependency failure, controlled reproduction, evidence preservation a container drift.

## Oficiálna dokumentácia

- [Troubleshoot the Docker daemon](https://docs.docker.com/engine/daemon/troubleshoot/)
- [Read daemon logs](https://docs.docker.com/engine/daemon/logs/)
- [Docker logging](https://docs.docker.com/engine/logging/)
- [`docker system df`](https://docs.docker.com/reference/cli/docker/system/df/)
- [`docker events`](https://docs.docker.com/reference/cli/docker/system/events/)
- [Docker Desktop troubleshooting](https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/)
