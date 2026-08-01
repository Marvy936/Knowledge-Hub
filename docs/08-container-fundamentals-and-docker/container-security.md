# Container security

Container security nevzniká pridaním jedného flagu ani úspešným image scanom. Je to súvislý trust lifecycle od source code-u cez build, registry a deployment až po process authority na hostiteľskom kerneli. Každá vrstva môže predchádzajúcu ochranu posilniť alebo obísť.

Bezpečný image môže byť spustený ako privileged container s Docker socketom. Hardenovaný runtime môže spustiť image vytvorený z kompromitovaného source-u. Non-root process môže dostať writable host secret mount. Registry môže uchovávať správne podpísaný artifact, no deployment môže stále používať mutable tag, ktorý neskôr ukáže na iný digest.

Budeme sledovať `payments-api`. Služba potrebuje prijímať HTTP requesty, čítať konfiguráciu a zapisovať do jedného data volume-u. Nepotrebuje root, host namespaces, zariadenia, Docker socket ani broad outbound network. Táto znalosť umožňuje navrhnúť konkrétnu policy a následne overiť, že povolené aj zakázané cesty sa správajú podľa očakávania.

## 1. Threat model pred hardening flags

Security návrh začína tým, čo chránime a pred kým. Pri `payments-api` sú hlavnými assets payment dáta, service credentials, signing alebo TLS keys, runtime host a dostupnosť služby. Útočník môže získať remote code execution v aplikácii, kompromitovať dependency, vložiť škodlivý build krok, ukradnúť registry credential alebo zneužiť príliš široký runtime mount.

Z toho vyplývajú odlišné controls:

```text
source compromise
→ review, branch protection, dependency a secret controls

build compromise
→ trusted builder, pinned inputs, provenance a isolated credentials

registry compromise alebo tag mutation
→ digest pinning, signatures, immutability a read-back

application RCE
→ non-root, capability drop, seccomp, LSM, read-only rootfs

credential theft
→ short-lived identity, secret mounts a narrow egress

host escape
→ kernel/runtime patching, user namespaces, sandbox alebo VM boundary
```

Bez threat modelu sa tím ľahko sústredí na viditeľné flags a prehliadne najkratšiu attack path.

## 2. Source a dependency boundary

Dockerfile je program spúšťaný builderom. `RUN` commands môžu čítať files, pristupovať na sieť a vytvárať output, ktorý sa stane súčasťou image-u. Pull request meniaci Dockerfile preto nie je iba zmena packagingu; môže meniť build authority.

```dockerfile
RUN curl -fsSL https://example.invalid/install.sh | sh
```

Takýto krok používa mutable remote input, ktorý nie je zachytený v repository ani lockfile. Lepší model používa pinned package alebo artifact digest a overenie:

```dockerfile
ARG TOOL_SHA256=<expected-sha256>
RUN curl -fsSLo /tmp/tool.tgz https://example.invalid/tool-1.2.3.tgz \
    && echo "$TOOL_SHA256  /tmp/tool.tgz" | sha256sum -c - \
    && tar -xzf /tmp/tool.tgz -C /usr/local/bin \
    && rm /tmp/tool.tgz
```

Checksum preukazuje content identity stiahnutého súboru. Nepreukazuje, že artifact je bezpečný alebo že očakávaný hash nebol škodlivo zmenený v tom istom pull requeste. Review a trusted source zostávajú potrebné.

Dependencies majú byť versionované a locknuté podľa ekosystému. Network access v release build-e má byť čo najužší. Untrusted pull request nemá dostať production registry, signing alebo cloud credentials.

## 3. Base image je inherited trust

`FROM` importuje filesystem, config a package inventory z iného artifactu. Tag ako `alpine:3.22` je čitateľný, ale môže sa posunúť. Digest pinning zachová exact base manifest:

```dockerfile
FROM alpine:3.22@sha256:<verified-digest>
```

Pinning však neznamená automatické patchovanie. Keď base image dostane security update, application image treba vedome rebuildnúť, otestovať a znovu nasadiť s novým digestom.

```text
nový base digest
→ application rebuild
→ tests a scan
→ nový application digest
→ staged deployment
→ runtime verification
→ odstránenie starého digestu
```

Minimal base znižuje package a tool surface, ale „distroless“ nie je magická bezpečnosť. Aplikácia a jej libraries stále môžu obsahovať zraniteľnosti. Chýbajúci shell sťažuje niektoré post-exploitation kroky, no zároveň mení debugging workflow.

## 4. Build secrets nesmú byť image content

Secret dodaný cez `ARG`, environment alebo `COPY` sa môže objaviť v image history, layer alebo build logs.

Chybný model:

```dockerfile
ARG NPM_TOKEN
RUN npm config set //registry.npmjs.org/:_authToken "$NPM_TOKEN" \
    && npm ci
```

BuildKit secret mount:

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci
```

CLI:

```bash
docker buildx build \
  --secret id=npmrc,src="$HOME/.npmrc" \
  .
```

Secret mount sa nestane automaticky image layerom. Stále však dôverujeme programu spustenému v `RUN`; môže secret vypísať, skopírovať alebo odoslať. Build logs a network egress preto patria do trust modelu.

## 5. Image identity, scan a evidence

Scanner potrebuje presný subject. Scan tagu bez uloženia resolved digestu je časovo nestabilný. Multi-platform image potrebuje inventory všetkých platform manifests.

```bash
docker buildx imagetools inspect \
  registry.example.com/atlas/payments-api@sha256:<index-digest>
```

Security evidence môže zahŕňať vulnerability scan, SBOM, provenance, signature a policy verdict. Každý report musí uvádzať digest, platform, producer a čas alebo database generation.

Scan PASS neznamená „image je bezpečný“. Znamená, že scanner pre daný subject a vulnerability database nenašiel finding porušujúci policy. Logic flaw, malicious behavior, runtime misconfiguration a zero-day môžu zostať.

## 6. Non-root runtime

Bežná HTTP služba nepotrebuje root. Dockerfile môže nastaviť numeric UID a GID:

```dockerfile
USER 65532:65532
```

Numeric identity je jednoznačná aj v minimal image-i bez `/etc/passwd`. Runtime read-back:

```bash
docker image inspect IMAGE --format '{{.Config.User}}'
docker inspect CONTAINER --format '{{.Config.User}}'
```

Obe hodnoty sú dôležité, pretože `docker run --user` alebo Compose `user` môže image default prepísať.

Non-root znižuje dopad mnohých chýb, ale nevyrieši broad file permissions, capabilities, host mounts ani Docker socket. Process môže byť non-root a stále čítať secret, ak mu mount alebo ACL prístup povolí.

## 7. Read-only root filesystem a explicitné writable paths

Aplikácia nemá meniť vlastný binary ani system files. Read-only root filesystem zmení tento intent na runtime enforcement:

```bash
docker run --rm \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --mount type=volume,source=payments-data,target=/var/lib/atlas-payments \
  IMAGE
```

Výnimky sú explicitné. `/tmp` je bounded tmpfs a payment data path je volume. Ak aplikácia neočakávane zapisuje do `/home/nonroot` alebo `/etc`, zlyhanie odhalí skrytý runtime assumption.

`noexec` na tmpfs znižuje jednu execution cestu, ale process môže stále načítať script cez interpreter alebo použiť memory execution podľa dostupných syscalls a policy. Je to defense-in-depth, nie absolútna ochrana.

## 8. Capability drop a `no_new_privs`

Docker poskytuje default capability set. Pre `payments-api` nie je potrebná žiadna Linux capability, preto runtime môže použiť:

```bash
--cap-drop ALL
--security-opt no-new-privileges=true
```

`no_new_privs` zabráni získaniu nových privileges cez exec transition. Capability drop zúži current authority. Ak workload potrebuje jednu konkrétnu capability, pridá sa explicitne a testuje sa forbidden path.

Broad `CAP_SYS_ADMIN` sa často prirovnáva k „novému rootu“, pretože pokrýva veľa citlivých operácií. Pridávať ju kvôli nejasnému `permission denied` je takmer vždy nesprávny troubleshooting krok.

## 9. Seccomp a LSM

Seccomp obmedzuje syscalls. Docker default profil blokuje vybrané rizikové operácie a povoľuje bežný application runtime. Custom profil môže byť užší, ale musí zohľadniť jazykový runtime, architektúru a optional features.

SELinux alebo AppArmor pridávajú policy nad files, sockets, devices a ďalšími kernel objects. Pri bind mountoch môže byť potrebné správne labelovanie podľa platformy. Vypnutie LSM vyrieši symptóm, ale odstráni celú enforcement vrstvu.

Pri denial incidente zachovaj application log, container inspect a host audit evidence. Rozlišuj Unix ownership, read-only mount, capability, seccomp a LSM. Všetky môžu používateľovi vyzerať ako `permission denied`.

## 10. Docker daemon a socket sú privilegovaná boundary

Docker daemon typicky spravuje host namespaces, mounts, networks a containers. Klient s právom ovládať daemon môže často vytvoriť privileged container alebo mountnúť host filesystem.

Preto membership v host skupine `docker` nie je obyčajné právo spúšťať aplikácie. Je to high-impact platform authority.

Mount socketu do application containeru:

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

umožní processu volať Docker API podľa daemon authorization modelu. Application RCE sa môže zmeniť na host compromise. Socket proxy s allowlistom môže zúžiť API, ale potrebuje vlastný threat model a nesmie slepo forwardovať všetky endpoints.

Rootless Docker znižuje authority daemonu a containers voči hostu, no má platformové obmedzenia a nemení potrebu application hardeningu.

## 11. Privileged mode, host namespaces a devices

Nasledujúce runtime voľby zásadne oslabujú izoláciu:

```text
--privileged
--pid host
--network host
--ipc host
writable host root mount
raw block device
KVM alebo ďalšie citlivé devices
Docker/containerd socket
```

Každá môže mať legitímny low-level use case, ale nie pre bežnú business API. Ak monitoring agent potrebuje host PID namespace, jeho image, identity, capabilities a node placement sa posudzujú ako host-level software, nie ako obyčajný application container.

## 12. Secrets pri runtime

Environment variables sú pohodlné, ale môžu byť viditeľné cez inspect, process environment, crash dump alebo debug tooling.

```bash
docker inspect CONTAINER --format '{{json .Config.Env}}'
```

Citlivé hodnoty je často lepšie dodávať cez mounted secret file s úzkymi permissions alebo cez workload identity a runtime retrieval. Aplikácia má podporovať refresh alebo rotation bez logovania hodnoty.

Secret rotation nie je iba zmena secret store-u:

```text
nový credential vytvorený
→ application ho načíta
→ loaded generation sa overí
→ starý credential sa zruší
→ old sessions alebo caches sa uzavrú
```

Zelený container restart nepreukazuje, že process načítal nový secret ani že starý už nefunguje.

## 13. Network segmentation a egress

Container hardening zahŕňa aj network. `payments-api` potrebuje ingress na HTTP port a egress k databáze a telemetry. Nepotrebuje arbitrary internet egress ani prístup k cloud metadata endpointu.

User-defined networks oddeľujú lokálne projecty, ale nie sú kompletnou enterprise network policy. Host firewall, orchestrator network policy, cloud security controls a application TLS stále rozhodujú.

Egress obmedzenie znižuje dopad RCE a dependency compromise. Zároveň musí povoľovať DNS, certificate revocation alebo package access iba tam, kde je to súčasť runtime contractu.

## 14. Resource limits ako availability security

Memory, CPU a PID limity chránia host a susedné workloady pred runaway processom. Príliš nízke limity však môžu vytvoriť self-inflicted outage.

```bash
docker run --rm \
  --memory 256m \
  --cpus 0.50 \
  --pids-limit 128 \
  IMAGE
```

Limity sa nastavujú podľa load testov a SLO, nie náhodne. Monitorujú sa throttling, OOM, PID exhaustion a queue growth. Availability útok alebo bug môže využiť aj disk, inode, network connection alebo log volume, preto resource policy nekončí pri memory.

## 15. Logging a audit bez secret leakage

Application logs majú obsahovať request correlation, release a configuration generation a relevantný error context. Nemajú obsahovať access tokens, passwords, payment card data alebo celé environment dumps.

Docker logs zachytávajú stdout a stderr podľa logging drivera:

```bash
docker logs --timestamps payments-api
```

Log driver môže mať local retention alebo forwardovať do central systému. Bez rotation môže container log storage zaplniť host disk. Central logging potrebuje transport, redaction, access control a retention policy.

Security audit má korelovať image digest, container ID, runtime configuration, identity a host. Samotný application log často nevie, že container bol spustený s nebezpečným mountom.

## 16. Patching a replacement

Running container sa nemá ručne opravovať inštaláciou package alebo editáciou binary. Taká zmena nie je v image digest-e, po recreate zmizne a scanner ju nemusí evidovať.

Správny tok:

```text
vulnerability alebo defect
→ source/base update
→ nový build
→ test, scan a provenance
→ nový digest
→ staged replacement
→ runtime a business verification
→ odstránenie starého digestu
```

Kernel alebo runtime vulnerability vyžaduje patch alebo replacement hosta. Application image rebuild zdieľaný kernel neopraví.

## 17. Incident: read-only non-root container kompromitoval host

Atlas internal deployment tool bežal ako UID `65532`, s read-only root filesystemom a `cap-drop ALL`. Security review ho označil za hardenovaný. Container však mal Docker socket mount, aby mohol spúšťať deployment jobs.

Útočník využil command injection v API a zavolal Docker API cez socket. Vytvoril nový privileged container s bind mountom host `/`.

```text
application RCE
→ prístup k docker.sock
→ create privileged helper
→ mount host root
→ host compromise
```

Všetky visible container hardening flags fungovali, ale najkratšia attack path ich obišla cez daemon authority.

Containment odpojil socket, izoloval node a rotoval host a registry credentials. Trvalá oprava presunula deployment operácie do samostatnej control-plane služby s narrow API, short-lived identity a explicitným allowlistom operations. Application container už nedostal priamy daemon access.

## 18. Incident: secret zmizol z filesystemu, ale ostal v layer

Developer skopíroval private package token do image-u, spustil dependency install a v ďalšom kroku token odstránil. Final container path token neobsahoval, preto manual kontrola prešla.

Image layer analysis však ukázala token v skoršom blob-e. Registry mal image dostupný širšiemu teamu.

Recovery zrušila token, odstránila alebo zablokovala compromised digest a rebuildla image s BuildKit secret mountom. Pipeline pridala secret scanning build contextu a image layers. Dôležitá hranica bola, že odstránenie pathu v neskoršej layer neodstránilo bytes z content graphu.

## 19. Referenčný hardenovaný runtime

Pre lokálny `payments-api` môže baseline vyzerať takto:

```bash
docker run --detach \
  --name payments-api \
  --user 65532:65532 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --cap-drop ALL \
  --security-opt no-new-privileges=true \
  --memory 256m \
  --cpus 0.50 \
  --pids-limit 128 \
  --mount type=volume,source=payments-data,target=/var/lib/atlas-payments \
  --publish 127.0.0.1:18080:8080 \
  registry.example.com/atlas/payments-api@sha256:<digest>
```

Tento príkaz nie je univerzálna production policy. Ukazuje, ako sa workload intent preloží do enforcement options. Po spustení treba read-backnúť `docker inspect`, overiť process usera, mounts, capabilities, health a business write/read.

Forbidden tests majú potvrdiť, že process nevie zapisovať do `/etc`, nemá Docker socket, nemá host namespaces a nemôže vykonať operáciu vyžadujúcu odstránenú capability.

## Čo si z kapitoly odniesť

Container security je defense-in-depth cez celý lifecycle. Source, dependencies, Dockerfile, builder, registry, image digest, runtime user, mounts, capabilities, seccomp, LSM, network, secrets a host patching patria do jedného trust modelu.

Non-root, read-only root filesystem a capability drop sú dôležité, ale môžu byť obídené broad mountom alebo daemon socketom. Scan musí byť viazaný na immutable digest a všetky platform manifests. Runtime policy treba read-backnúť a overiť positive aj forbidden outcomes. Pri incidente sa opravuje authoritative source alebo runtime model a workload sa nahrádza novou generation, nie ručne patchuje.

## Primárne zdroje

- [Docker Engine security](https://docs.docker.com/engine/security/)
- [Running containers and capabilities](https://docs.docker.com/engine/containers/run/)
- [Rootless mode](https://docs.docker.com/engine/security/rootless/)
- [Build secrets](https://docs.docker.com/build/building/secrets/)
- [Docker Scout and image analysis](https://docs.docker.com/scout/)
- [Content trust and signing concepts](https://docs.docker.com/engine/security/trust/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Container storage](container-storage.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Docker architecture →](docker-architecture.md)
<!-- KNOWLEDGE-NAVIGATION:END -->