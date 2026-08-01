# Docker troubleshooting

Docker troubleshooting nie je séria náhodných restartov, rebuildov a `prune` príkazov. Je to hľadanie prvej vrstvy, na ktorej sa očakávaný stav prestal zhodovať s pozorovaným stavom. Docker request prechádza cez client context, Engine API, image resolution, container create configuration, storage a network preparation, OCI runtime, hlavný process, healthcheck a napokon application alebo business path. Každá vrstva má vlastné evidence a vlastnú failure semantics.

Najväčšou chybou pri incidente býva zničenie dôkazov skôr, než sa určí subject. `docker restart` zmení časovú os a process state. Recreate odstráni pôvodný PID, network endpoint a writable layer. `docker compose down` odstráni project resources. `prune` môže odstrániť image, build cache alebo volume potrebné na reprodukciu a recovery.

Budeme používať jeden referenčný incident: `payments-api` je podľa Dockeru running a healthy, ale klient nevie vytvoriť payment. Tento symptom môže mať príčinu v network bind-e, volume permissions, starej configuration generation, inom image digeste alebo external dependency. Cieľom je hypotézy rozlíšiť, nie ich všetky naraz „opraviť“.

## 1. Najprv urči Docker context a daemon

Prvý príkaz nemá byť restart. Najprv zisti, ktorý daemon pozoruješ:

```bash
docker context show
docker context inspect
docker version
docker info
```

Rovnaké meno `payments-api` môže existovať v local Docker Desktop, test remote hoste aj production Engine-i. Screenshot z nesprávneho contextu je platný dôkaz o inom systéme.

Zachovaj daemon identity, Engine verziu, OS, architecture, rootless/rootful model a Docker data root. Pri remote contextoch zaznamenaj endpoint a transport. Pri Docker Desktop navyše ber do úvahy vnútornú Linux VM.

## 2. Zafixuj container a image identity

Container name je mutable user-facing reference. Potrebujeme container ID, create timestamp a image ID:

```bash
container_id="$(docker inspect payments-api --format '{{.Id}}')"
image_id="$(docker inspect payments-api --format '{{.Image}}')"

printf 'container=%s\nimage=%s\n' "$container_id" "$image_id"
```

Zachovaj celý inspect:

```bash
mkdir -p incident
docker inspect "$container_id" > incident/container-inspect.json
docker image inspect "$image_id" > incident/image-inspect.json
```

Ak deployment používa registry reference, zachovaj aj index a platform manifest digest. Local image ID a registry digest nie sú vždy tá istá user-facing hodnota. Pri multi-platform image-i node spustí konkrétny platform manifest.

```bash
docker buildx imagetools inspect \
  registry.example.com/atlas/payments-api@sha256:<index-digest>
```

## 3. Vytvor časovú os

Docker events poskytujú mutation a lifecycle udalosti:

```bash
docker events \
  --since '30m' \
  --until '0s' \
  > incident/docker-events.log
```

Container timestamps:

```bash
jq '.[0].State | {
  Status,
  Running,
  OOMKilled,
  Dead,
  ExitCode,
  Error,
  StartedAt,
  FinishedAt,
  Health
}' incident/container-inspect.json
```

Application logs:

```bash
docker logs --timestamps "$container_id" \
  > incident/container.log 2>&1
```

Časová os má spojiť posledný image pull, create, start, health transitions, configuration zmenu a prvý business symptom. Bez času sa ľahko koreluje request s inou container generation.

## 4. Rozlíš create, start, running, healthy a serving

Docker state nie je jeden boolean. Container môže zostať v stave `created`, ak process ešte nebol spustený. Môže byť `running`, hoci health je `unhealthy`. Môže byť healthy podľa local endpointu a nedostupný cez host port. Môže úspešne servovať `/healthz`, ale zlyhávať pri payment write.

```text
created
→ process start request
→ running
→ health starting
→ healthy alebo unhealthy
→ application serving path
→ business outcome
```

Pozri stručný stav:

```bash
docker ps -a --filter id="$container_id"
docker inspect "$container_id" \
  --format 'status={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}} exit={{.State.ExitCode}}'
```

Keď `docker ps` ukazuje running, nevylučuje network, storage ani configuration problém.

## 5. Effective command a PID 1

```bash
docker inspect "$container_id" | jq '.[0] | {
  Path,
  Args,
  Entrypoint: .Config.Entrypoint,
  Cmd: .Config.Cmd,
  User: .Config.User,
  WorkingDir: .Config.WorkingDir
}'

docker top "$container_id" -eo pid,ppid,user,stat,args
```

Porovnaj image defaults s container overrides. `--entrypoint`, Compose `command`, `user` alebo wrapper script môžu zmeniť runtime bez zmeny image digestu.

Ak process okamžite exitol, logs a `.State.Error` môžu odhaliť invalid command, permission alebo loader chybu. Ak process daemonizuje a PID 1 skončí, container sa ukončí, hoci child process krátko prežil.

## 6. Interpretácia exit codes

Exit code je observation, nie úplná príčina.

Exit `0` znamená, že process oznámil úspešné ukončenie. Pri long-running service však môže byť nečakaný exit `0` stále incident.

Exit `1` je application-defined general failure. Potrebuje logs.

Exit `126` často znamená, že command bol nájdený, ale nebolo možné ho vykonať. Môže ísť o permissions, noexec mount alebo policy denial.

Exit `127` často znamená command alebo interpreter not found v shell context-e.

Exit `137` zodpovedá ukončeniu signalom 9, ale nemusí automaticky znamenať OOM. Skontroluj `.State.OOMKilled`, cgroup memory events a operator actions.

Exit `143` zodpovedá `SIGTERM` pri procesoch, ktoré signal nepreložia na vlastný clean exit. Môže byť očakávaný pri stop lifecycle.

Pri signal exit-e používaj:

```text
exit = 128 + signal number
```

ako orientačné pravidlo, ale vždy koreluj runtime state a logs.

## 7. OOM a resource pressure

```bash
docker inspect "$container_id" \
  --format 'oom={{.State.OOMKilled}} exit={{.State.ExitCode}}'
docker stats --no-stream "$container_id"
```

Current stats po reštarte nemusia ukazovať pressure pred pôvodným OOM. Potrebné sú historické metrics alebo host cgroup evidence.

Skontroluj effective limits:

```bash
jq '.[0].HostConfig | {
  Memory,
  MemoryReservation,
  MemorySwap,
  NanoCpus,
  CpuQuota,
  CpuPeriod,
  PidsLimit
}' incident/container-inspect.json
```

Pri memory incidente vytvor hypotézy: application leak, legitímny traffic burst, príliš nízky limit, page-cache pressure, host memory pressure alebo sidecar/debug process v rovnakej cgroup. Recovery môže byť limit increase ako containment, ale trvalá oprava potrebuje load a allocation dôkaz.

## 8. Environment a loaded configuration

Engine environment:

```bash
docker inspect "$container_id" \
  --format '{{json .Config.Env}}' | jq .
```

Compose resolved environment:

```bash
docker compose --env-file .env config --environment
docker compose --env-file .env config > incident/compose-resolved.yaml
```

Application loaded state:

```bash
curl -fsS http://127.0.0.1:18080/version | jq .
```

Ak desired generation je `cfg-101`, inspect aj `/version` ukazujú `cfg-100`, pravdepodobne sa vykonal restart namiesto recreate alebo sa použil iný env source. Ak inspect ukazuje `cfg-101`, ale application hlási `cfg-100`, parser hodnotu ignoroval, application reload zlyhal alebo request smeruje na inú generation.

Nikdy nevypisuj celý environment do ticketu bez redakcie; môže obsahovať secrets.

## 9. Mounts a data identity

```bash
docker inspect "$container_id" | jq '.[0].Mounts'
```

Pri payment write failure si zaznamenaj source volume name alebo bind path, destination, read/write mode a propagation. Volume metadata:

```bash
docker volume inspect atlas-payments-data \
  > incident/volume-inspect.json
```

Competing hypotheses pri `permission denied`:

```text
runtime UID/GID nemá filesystem access
mount je read-only
root filesystem je read-only a DATA_PATH smeruje mimo volume-u
SELinux/AppArmor odmieta operáciu
user namespace mapping mení host ownership
mount zakryl očakávaný directory
filesystem je full alebo bez inodes
```

Distroless image nemusí mať `ls` alebo `stat`. Použi controlled helper s rovnakým volume-om:

```bash
docker run --rm \
  --mount type=volume,source=atlas-payments-data,target=/data,readonly \
  busybox:1.36.1 \
  sh -c 'id; ls -ldn /data; ls -lan /data | head'
```

Read-only helper zachová dáta. Ak potrebuješ opravu ownershipu, najprv vytvor manifest a backup a až potom vykonaj bounded mutation.

## 10. Disk a inode exhaustion

Docker host môže zaplniť images, build cache, container writable layers, logs alebo volumes.

```bash
docker system df -v
df -h
df -i
```

`no space left on device` môže znamenať vyčerpané bytes alebo inodes. `docker image prune` nepomôže, ak disk vlastní veľký named volume alebo log file. `docker volume prune` môže zničiť dáta.

Najprv identifikuj ownera. Pri log growth skontroluj logging driver a rotation. Pri build cache použi builder-specific inventory a retention. Pri writable layer pozri `docker ps -a --size`.

## 11. Image pull a platform chyby

Ak container nevznikol, application logs nemusia existovať. Pri pull probléme skontroluj exact reference:

```bash
docker pull registry.example.com/atlas/payments-api@sha256:<digest>
```

Rozlišuj TLS, DNS, authentication, authorization, manifest unknown, blob unknown a platform selection.

```bash
docker buildx imagetools inspect IMAGE
```

`no matching manifest for linux/arm64` znamená, že index nemá vhodný platform descriptor. `exec format error` znamená, že manifest sa vybral a process exec našiel binary nekompatibilný s runtime architecture alebo formátom.

`no such file or directory` pri existujúcom executable môže znamenať chýbajúci shebang interpreter alebo ELF loader. Image export a binary inspection pomôžu:

```bash
id="$(docker create IMAGE)"
docker export "$id" > incident/rootfs.tar
docker rm "$id"
```

Analyzuj artifact v trusted debug prostredí.

## 12. Network cesta sa diagnostikuje po krokoch

Zachovaj network config:

```bash
docker inspect "$container_id" | jq '.[0].NetworkSettings'
docker network inspect atlas-payments_backend \
  > incident/network-inspect.json
docker port "$container_id"
```

Potom rozliš tri paths:

```text
container-local health
service DNS z iného containeru
host-published port
```

Local check:

```bash
docker exec "$container_id" \
  /usr/local/bin/payments-api healthcheck
```

Service DNS:

```bash
docker run --rm \
  --network atlas-payments_backend \
  curlimages/curl:8.10.1 \
  curl -v http://payments-api:8080/readyz
```

Host path:

```bash
curl -v http://127.0.0.1:18080/readyz
```

Ak local prejde a oba external paths zlyhajú, skontroluj application bind address. Ak service DNS prejde a host zlyhá, sústreď sa na published port a host firewall. Ak DNS zlyhá, over network membership a alias. Ak TCP connect prejde, ale väčšie requesty timeoutujú, analyzuj MTU, proxy a application timeouty.

## 13. DNS

V debug containeri:

```bash
cat /etc/resolv.conf
getent hosts payments-api
getent hosts database.example.internal
```

DNS result môže obsahovať IPv4 aj IPv6. Otestuj exact family:

```bash
curl -4 -v URL
curl -6 -v URL
```

DNS success iba mapuje meno na address. Neoveruje route, firewall, listener ani TLS. Pri intermittent DNS probléme zachovaj timestamps, query name, response records, TTL a network namespace.

## 14. Healthcheck diagnosis

Health definition:

```bash
docker inspect "$container_id" \
  --format '{{json .Config.Healthcheck}}' | jq .
```

Health history:

```bash
docker inspect "$container_id" \
  --format '{{json .State.Health.Log}}' | jq .
```

Výstup health commandu môže obsahovať presnú chybu. Skontroluj timeout a start period. Check môže zlyhávať, pretože v image-i chýba shell alebo `curl`, nie preto, že application nie je ready.

Naopak green health môže byť príliš plytký. Ak testuje iba `/healthz`, volume write alebo database dependency môže byť chybná. Health oracle sa posudzuje podľa intended serving contractu.

## 15. Compose problémy začínajú resolved modelom

```bash
docker compose version
docker compose --env-file .env config --environment
docker compose --env-file .env config > incident/compose-resolved.yaml
docker compose --env-file .env ps --all
docker compose --env-file .env logs --timestamps --no-color \
  > incident/compose.log
```

Source `compose.yaml` nemusí byť effective model. Overrides, profiles, shell environment a project name môžu zmeniť image, ports, mounts aj security options.

Zisti project identity:

```bash
docker compose ls
docker inspect "$(docker compose ps -q api)" \
  --format '{{json .Config.Labels}}' | jq .
```

Dve jobs s rovnakým project name môžu navzájom ovplyvniť resources. Zmena project name môže pripojiť nový project-scoped volume.

## 16. Build failure diagnosis

Pri BuildKit failure použi plain progress:

```bash
docker buildx build --progress=plain . 2>&1 \
  | tee incident/build.log
```

Zachovaj:

```bash
docker buildx inspect --bootstrap > incident/builder.txt
sha256sum Dockerfile .dockerignore > incident/build-files.sha256
```

Hľadaj prvý failing graph node. Summary `failed to solve` nie je root cause. Dependency download timeout, compiler error, missing context file, cache import failure a registry exporter authorization sú samostatné vrstvy.

Pri podozrivom cache behavior vytvor clean builder:

```bash
docker buildx create \
  --name incident-clean \
  --driver docker-container \
  --use

docker buildx inspect incident-clean --bootstrap

docker buildx build \
  --builder incident-clean \
  --no-cache \
  --progress=plain \
  .
```

Nepoužívaj `--no-cache` ako trvalú opravu, kým nevieš, ktorý input alebo cached result bol nesprávny.

## 17. Daemon a host layer

Keď CLI nevie kontaktovať daemon:

```bash
docker version
```

môže ukázať client informácie a server error. Na native Linux hoste:

```bash
systemctl status docker
journalctl -u docker --since '30 minutes ago'
systemctl status containerd
journalctl -u containerd --since '30 minutes ago'
```

Host kernel evidence:

```bash
dmesg --ctime | tail -n 200
journalctl -k --since '30 minutes ago'
```

Hľadaj OOM, filesystem, device, network, LSM a runtime errors. Reštart daemonu môže zastaviť alebo ovplyvniť workloads podľa konfigurácie a zničí časť volatile evidence. Najprv zachovaj logs a scope impactu.

## 18. Incident walkthrough: healthy API, payment write zlyháva

Symptom:

```text
Docker status: running
Docker health: healthy
GET /version: 200
POST /payments: 503 alebo permission denied
```

Najprv zafixujeme subject:

```bash
container_id="$(docker compose ps -q api)"
docker inspect "$container_id" > incident/api.json
docker logs --timestamps "$container_id" > incident/api.log 2>&1
docker volume inspect atlas-payments-data > incident/volume.json
```

Competing hypotheses sú: nesprávny UID/GID volume-u, read-only mount, DATA_PATH mimo volume-u, LSM denial, full filesystem alebo request smerujúci na inú container generation.

`docker inspect` ukáže UID `65532`, writable volume target a `DATA_PATH`. Logs ukážu `open data file: permission denied`. Read-only helper ukáže root directory `0:0` mode `0700`. Tým sa hypotézy výrazne zúžia na ownership.

Containment zastaví nové payment writes alebo presmeruje traffic na zdravú cohortu. Pred chown sa vytvorí backup a inventory. Bounded initializer opraví iba application directory:

```bash
docker run --rm \
  --user 0:0 \
  --mount type=volume,source=atlas-payments-data,target=/data \
  busybox:1.36.1 \
  sh -ec 'chown 65532:65532 /data && chmod 0750 /data'
```

Recovery nie je hotová pri green health. Zopakuje sa pôvodný POST, GET a recreate persistence test. Forbidden test potvrdí, že process stále nevie zapisovať mimo volume-u a nezískal broad privileges.

Skorší control je explicitný initializer, readiness write test a CI/Compose assertion nad runtime UID a volume identity.

## 19. Incident walkthrough: local health je green, host port timeoutuje

Subject evidence ukáže:

```text
healthcheck URL: 127.0.0.1:8080
LISTEN_ADDRESS: 127.0.0.1:8080
published port: 127.0.0.1:18080 → 8080/tcp
```

Local healthcheck prejde, pretože používa loopback v rovnakom namespace. Host packet smeruje na container interface address a listener tam nie je.

Service DNS test z iného containeru tiež zlyhá. Port mapping a firewall môžu byť správne.

Recovery vytvorí nový container s `LISTEN_ADDRESS=:8080`. Po zmene sa overia všetky tri paths: local health, service DNS a host port. Restart starého containeru by nepomohol, pretože environment je create-time state.

Skorší control je runtime integration test z oddeleného network namespace-u a explicitný host-published smoke test.

## 20. Unknown outcomes a retry

Niektoré Docker operácie môžu timeoutnúť po tom, čo mutation prebehla. Registry push, remote Engine create alebo Compose up môže mať unknown outcome.

Blind retry môže vytvoriť duplicate container, prepísať tag alebo zmiešať project generations. Najprv read-backni authoritative state:

```bash
docker ps -a --filter label=com.docker.compose.project=atlas-payments
docker buildx imagetools inspect IMAGE_REF
docker compose ps --all
```

Idempotentný retry potrebuje stable name alebo idempotency model a kontrolu existujúceho state-u. Pri external business side effecte Docker retry semantics nestačia; aplikácia potrebuje vlastný idempotency key a reconciliation.

## 21. Kedy použiť restart, recreate, rebuild alebo host replacement

Restart je vhodný, keď process alebo transient dependency potrebuje nový štart a create configuration aj image zostávajú správne.

Recreate je potrebný pri zmene environment, mounts, ports, security options alebo image reference containeru.

Rebuild je potrebný, keď sa mení source, dependency, Dockerfile, base image alebo runtime artifact.

Host replacement je potrebný pri kernel, runtime, storage driver alebo node compromise a pri neobnoviteľnom host drift-e.

```text
process state problém
→ restart môže stačiť

container config problém
→ recreate

image/artifact problém
→ rebuild + recreate

host/kernel problém
→ drain a replace host
```

Rozhodnutie sa robí podľa prvej chybnej authority vrstvy, nie podľa najľahšie dostupného príkazu.

## 22. Evidence pred deštruktívnou operáciou

Minimálny incident bundle:

```bash
docker context inspect > incident/context.json
docker version > incident/docker-version.txt
docker info > incident/docker-info.txt

docker inspect CONTAINER > incident/container.json
docker image inspect IMAGE > incident/image.json
docker logs --timestamps CONTAINER > incident/container.log 2>&1
docker diff CONTAINER > incident/container-diff.txt
docker events --since 30m --until 0s > incident/events.log

docker network inspect NETWORK > incident/network.json
docker volume inspect VOLUME > incident/volume.json
docker system df -v > incident/system-df.txt
```

Bundle môže obsahovať secrets v inspect alebo logs. Pred zdieľaním sa rediguje a chráni podľa incident policy.

Až potom sa rozhodne o stop, restart, recreate, rm, down alebo prune.

## 23. Closure po oprave

Incident sa neuzatvára vetou „container je green“. Potrebujeme overiť pôvodný outcome, forbidden outcome, adjacent cohort a druhú operáciu.

Pre `payments-api`:

```text
/version ukazuje správny image a config generation
/readyz je green
service DNS funguje
host port funguje
POST a GET payment prejdú
payment prežije recreate
process zostáva non-root a bez capabilities
zakázaný write mimo volume-u zlyhá
susedné services alebo platformy nie sú poškodené
druhý Compose up nevytvorí neočakávaný drift
```

Nakoniec sa control posunie skôr: Dockerfile check, resolved Compose policy, platform smoke test, volume initializer, loaded configuration telemetry alebo incident alert podľa root cause.

## Čo si z kapitoly odniesť

Docker incident sa diagnostikuje od exact contextu, containeru, image-u, configuration a data identity. Running, healthy a correct business outcome sú odlišné states. Evidence sa zachová pred restartom, recreate alebo cleanupom.

Pri každom symptóme sleduj vrstvu: client a daemon, image pull, create configuration, storage, network, runtime exec, process, health alebo application. Exit code, log alebo inspect field je observation, nie automatický root-cause verdict. Oprava sa aplikuje na authoritative vrstvu a overí sa pôvodnou aj forbidden cestou. Náhodný restart môže symptom dočasne skryť, ale nevytvára dôveryhodnú closure.

## Primárne zdroje

- [Docker Engine CLI reference](https://docs.docker.com/reference/cli/docker/)
- [Docker container inspect](https://docs.docker.com/reference/cli/docker/inspect/)
- [Docker events](https://docs.docker.com/reference/cli/docker/system/events/)
- [Runtime metrics](https://docs.docker.com/engine/containers/runmetrics/)
- [Docker networking](https://docs.docker.com/engine/network/)
- [Docker storage](https://docs.docker.com/engine/storage/)
- [BuildKit](https://docs.docker.com/build/buildkit/)
- [Compose troubleshooting](https://docs.docker.com/compose/support-and-feedback/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Praktický Docker projekt od prázdneho adresára po overený Compose runtime](docker-practical-walkthrough.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Kubernetes architecture →](../09-kubernetes/kubernetes-architecture.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
