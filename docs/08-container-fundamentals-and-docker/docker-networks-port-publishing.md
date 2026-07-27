# Docker networks a port publishing

Docker network object, container endpoint a published host port sú tri rozdielne identity. Container môže byť pripojený k správnej network a stále nebyť dostupný, ak process počúva iba na loopbacku. Port môže byť publikovaný a stále nedosiahnuteľný cez firewall alebo upstream route. Naopak, krátky zápis `-p 8080:80` môže neplánovane vystaviť službu na všetkých host interfaces.

Dominantný lifecycle:

```text
communication intent a allowed graph
→ Docker project/network identity
→ endpoint allocation a attach
→ DNS/alias generation
→ process socket bind
→ internal direct path alebo host publication subject
→ forwarding/NAT/firewall a upstream path
→ reverse path a conntrack
→ readiness, exposure a client-path verification
→ endpoint replacement, drain a cleanup
```

Diagnostika musí sledovať konkrétny flow a konkrétnu exposure generation. `docker ps` alebo existencia network objectu samy osebe nepreukazujú funkčný ani bezpečný packet path.

## 1. Atlas scenár

Atlas Payments používa Compose project `atlas-payments-prod`:

```text
frontend network: atlas-payments-prod_frontend
backend network: atlas-payments-prod_backend
api endpoint ID: EP-API-44
api service DNS: api
api container address: 172.24.0.8
api listen socket: 0.0.0.0:8080
host publication: 127.0.0.1:18080/tcp → 172.24.0.8:8080
proxy client: host-local reverse proxy
DB service DNS: db:5432 iba v backend network
network generation: NG-118
```

Povolený communication graph:

```text
local reverse proxy → host 127.0.0.1:18080 → api:8080
api → db:5432
external client → production proxy/DNS → local reverse proxy
external client ↛ db
```

Úspech znamená, že každý expected flow funguje z reálneho source observation pointu a každý forbidden flow je blokovaný.

## 2. Network a endpoint subject

Docker network subject obsahuje:

```text
Docker daemon/context a host
project a network name/ID
driver a options
subnet/gateway/IPAM
internal/attachable flags
endpoint inventory a aliases
DNS generation
firewall/NAT generation
MTU a address family
lifecycle owner
```

Container endpoint subject obsahuje:

```text
container/service identity
network ID
endpoint ID
MAC/IP addresses
aliases
veth/interface identity
route a DNS config
attach/detach generation
readiness eligibility
```

Container IP je runtime detail. Stable caller identity je service name alebo explicitný alias v správnej network boundary.

## 3. User-defined bridge lifecycle

```bash
docker network create atlas-backend

docker run -d --name db --network atlas-backend postgres:17
docker run -d --name api --network atlas-backend payments-api@sha256:I44
```

User-defined bridge poskytuje explicitný object lifecycle, embedded DNS a izoláciu od unrelated networks. Zjednodušený path:

```text
api process
→ api network namespace/interface
→ veth pair
→ Linux bridge
→ db veth/interface
→ db process socket
```

Pre internú komunikáciu používaj `db:5432`, nie host-published port. Host publication pridáva ďalší NAT/firewall coupling a zbytočne rozširuje exposure.

## 4. Socket bind predchádza Docker forwarding

Port publication nevytvorí application listener. Process musí bindnúť správny address/port vo svojom namespace-e:

```text
127.0.0.1:8080 v containeri
→ dostupné iba z rovnakého network namespace-u

0.0.0.0:8080 alebo specific container address
→ dostupné cez container interface podľa policy
```

`EXPOSE 8080` je image metadata. Nevytvára socket, firewall rule ani host publication.

Observation points:

```bash
docker exec api ss -lntp
docker inspect api
docker network inspect atlas-backend
```

## 5. Port publication subject

Explicitný mapping:

```bash
docker run -p 127.0.0.1:18080:8080 payments-api@sha256:I44
```

Subject obsahuje:

```text
host address family a bind address
host port a protocol
container endpoint generation
container address/port
forwarding/NAT/proxy implementation
host firewall generation
upstream route/security policy
owner a intended clients
```

Bez host IP môže Docker podľa configuration publikovať na všetkých host interfaces:

```bash
docker run -p 18080:8080 image
```

Pre local-only službu explicitne bindni loopback. Firewall je ďalší control, nie náhrada správneho publication scope-u.

## 6. Internal direct path verzus published path

```text
container-to-container:
api namespace → db service DNS → db endpoint:5432

host/external path:
client → host bind address:port → forwarding/NAT → api endpoint:8080
```

Tieto flows majú odlišné tuples, policy layers a failure boundaries. Test úspešného `curl localhost:18080` na hoste nepreukazuje, že iný stroj dosiahne službu. Internal `api → db` zase nepreukazuje host publication.

## 7. Project identity a DNS boundary

Compose vytvára project-scoped networks. Zmena project name môže vytvoriť paralelnú network:

```text
atlas-payments-prod_backend
atlas-payments_backend
```

Services v rozdielnych project networks si nemusia resolve-nuť mená ani routovať traffic, hoci majú rovnaké YAML service names.

DNS subject preto zahŕňa:

- project/network generation;
- service a alias ownership;
- endpoint set a readiness;
- address TTL/cache;
- replacement/draining state;
- application connection pool generation.

Hardcoded container IP obchádza tento lifecycle a môže po replacement-e smerovať na stale alebo recyklovanú adresu.

## 8. Aliases a collision

Alias je meno v konkrétnej network:

```bash
docker network connect --alias database atlas-backend db
```

Viac endpoints môže dostať rovnaký alias. Caller potom potrebuje poznať load distribution a connection-pool behavior. Alias collision alebo nejasný owner môže poslať traffic na nesprávnu service.

## 9. Host firewall, NAT a reverse path

Published flow môže prejsť:

```text
client packet
→ host ingress interface
→ pre-routing/DNAT alebo proxy
→ forwarding policy
→ bridge/veth
→ container socket
→ reply
→ conntrack/reverse translation
→ client
```

Preto kontrola iba host `INPUT` chainu nemusí vysvetliť verdict. Observation musí zodpovedať reálnemu backendu a pathu:

- Docker-managed iptables/nftables rules;
- forwarding policy;
- cloud/security-group ACL;
- route a reverse-path filtering;
- conntrack entry;
- host proxy podľa platformy.

## 10. Rootless a Docker Desktop boundary

Pri rootless Docker alebo Docker Desktop môže publication prechádzať userspace forwarderom alebo VM/network translation vrstvou:

```text
client host
→ Desktop/rootless proxy
→ Linux VM alebo user namespace
→ Docker bridge
→ container endpoint
```

`localhost`, source address preservation, IPv6 a firewall observation points sa môžu líšiť od rootful Linux Engine. Zaznamenaj platformu a effective dataplane, nie iba CLI syntax.

## 11. Host network mode

```bash
docker run --network host image
```

Process binduje priamo v host network namespace-e. Dôsledky:

- žiadna samostatná container IP;
- host port collisions;
- slabšia network isolation;
- `-p` nemá bežný mapping význam;
- application môže vidieť host interfaces a sockets.

Host mode nie je všeobecná oprava connectivity problému. Odstraňuje boundary, ktorú treba najprv diagnostikovať.

## 12. `none`, macvlan a ipvlan

`none` poskytuje typicky iba loopback. Workload stále môže komunikovať cez mounted sockets alebo shared filesystem, takže „bez networku“ neznamená bez všetkých communication paths.

Macvlan/ipvlan menia L2/L3 endpoint model. Potrebujú explicitný IPAM, upstream switch/cloud support, host-to-container path a policy/observability model. Nepoužívaj ich iba preto, aby container pôsobil ako VM.

## 13. IPv4, IPv6 a bind ambiguity

`0.0.0.0` je IPv4 unspecified address, `::` IPv6 unspecified address. Dual-stack behavior závisí od application socket options, Engine a host policy.

Publication a verification musia uviesť:

```text
address family
host bind address
container listen addresses
DNS A/AAAA answers
firewall rules pre obe families
client selection
```

Služba môže byť blokovaná cez IPv4 a neplánovane dostupná cez IPv6 alebo opačne.

## 14. MTU a partial connectivity

Path môže zahŕňať veth, bridge, VPN, overlay a cloud tunnel. Nesprávna MTU alebo blokovaný Path MTU Discovery vytvorí typický pattern:

```text
TCP connect alebo malý request funguje
→ väčší TLS/request packet potrebuje fragmentáciu/PMTU
→ feedback je blokovaný alebo MTU je nesprávna
→ retransmissions a timeout
```

Testuj z relevantného namespace-u a source pathu, nie iba host pingom.

## 15. Conntrack a ephemeral ports

NAT/stateful firewall potrebuje connection state. Pri vyčerpaní:

- nové connections padajú;
- existujúce pokračujú;
- problém rastie s concurrency;
- restart alebo timeout dočasne uvoľní stav.

Observation zahŕňa host conntrack table, ephemeral port range, NAT tuples, application pools a retry amplification.

## 16. Worked failure: service používa `localhost` pre databázu

API config obsahoval `DATABASE_HOST=localhost`. Developer očakával, že Compose prepojí `localhost` s `db` service.

```text
API process resolve-ne localhost
→ 127.0.0.1 v API network namespace-e
→ connection ide späť na API container
→ DB počúva v inom namespace-e
→ connection refused
```

Oprava je použiť service identity `db:5432` v spoločnej backend network, nie host publication ani host network mode.

## 17. Worked failure: skrátený mapping vystavil admin port

Development override obsahoval:

```yaml
ports:
  - "9090:9090"
```

Na production hoste sa mapping bindol na všetky interfaces. Admin endpoint nemal authentication, pretože mal byť local-only.

```text
chýba explicitný host address
→ Engine vytvorí broad publication
→ upstream firewall port povoľuje
→ endpoint je internet-accessible
```

Recovery:

1. odstráň publication alebo bindni `127.0.0.1`;
2. zablokuj port upstream policy;
3. rotate credentials/tokens dostupné cez endpoint;
4. audituj access logs;
5. oprav resolved Compose policy a exposure tests.

## 18. Worked failure: project rename rozdelil service discovery

API bolo spustené v projekte `atlas-payments-prod`, DB po manual command-e v projekte `atlas-payments`. Obe services sa volali rovnako ako predtým, ale boli v rozdielnych networks.

```text
service names sú rovnaké
→ project-scoped network IDs sú rozdielne
→ embedded DNS endpoint inventory je oddelený
→ api nevie resolve-nuť alebo dosiahnuť db
```

Kontroluj project/network IDs a endpoint membership, nie iba service names.

## 19. Causal walkthrough: port je publikovaný, ale remote klient sa nepripojí

### Symptóm

`docker ps` ukazuje `0.0.0.0:18080->8080/tcp`. `curl 127.0.0.1:18080` na hoste funguje, ale klient z iného stroja timeoutuje.

### Zafixuj flow subject

```text
client IP/interface
host IP/interface a address family
host port/protocol
pre/post-NAT tuple
container endpoint generation
container listen socket
firewall/NAT generation
upstream route/security policy
timestamp
```

### Competing hypotheses

1. application počúva iba na container loopbacku, pričom local test trafí inú path;
2. host publication je loopback-only alebo iba IPv6/IPv4;
3. host firewall blokuje forwarding path;
4. cloud/security group nepovoľuje port;
5. upstream route alebo return path chýba;
6. Docker Desktop/rootless proxy počúva iba local host;
7. mapping smeruje na nesprávny container port;
8. service je unhealthy a local response pochádza z iného processu;
9. conntrack alebo ephemeral resources sú vyčerpané;
10. packet je príliš veľký a path má MTU black hole.

### Discriminating observation points

- `ss -lntp` na hoste a v containeri;
- `docker port`, inspect publication a endpoint ID;
- packet capture na client, host ingress, bridge a container interface;
- firewall/nftables/iptables counters;
- conntrack tuple a state;
- cloud/network ACL logs;
- route a reverse path;
- health/readiness a exact response identity;
- MTU/PMTU test pri size-dependent failure.

### Containment

Neotváraj broad firewall alebo host network mode bez identifikácie pathu. Ak exposure scope je nejasný, dočasne bindni loopback a vyraď service z external trafficu.

### Recovery

- wrong socket bind → oprav application listen contract;
- wrong mapping → publikuj correct container port;
- host/upstream policy → pridaj narrow source/destination rule;
- Desktop/rootless limitation → použi podporovaný forwarding model;
- conntrack exhaustion → obmedz retry/concurrency, uprav capacity a timeouts;
- MTU → zosúlaď interface/tunnel MTU a povoľ potrebný PMTU feedback;
- wrong endpoint generation → recreate/drain a obnov discovery.

### Over pôvodný outcome

Over local host path, remote client path, forbidden source path a application-level request. Potvrď aj source IP/identity, ktorú application reálne vidí.

### Posuň control skôr

Pridaj resolved publication inventory, policy nad `0.0.0.0`/`::`, per-flow synthetic tests, project/network identity checks, endpoint generation audit a firewall counters v deployment evidence.

## 20. Referenčný driver katalóg

| Driver/model | Boundary | Typický use case | Hlavné riziko |
|---|---|---|---|
| User-defined bridge | single-host namespace/bridge | bežný Compose stack | host NAT/firewall a project coupling |
| Host | host network namespace | úzky performance/network use case | port collision a isolation loss |
| None | loopback-only network namespace | offline workload | alternate mounted communication paths |
| Overlay | multi-host virtual network | podporovaný orchestrator | control-plane/MTU/encryption complexity |
| Macvlan | L2 endpoint | legacy L2 integration | host connectivity a switch policy |
| Ipvlan | L2/L3 endpoint | controlled IP integration | IPAM/routing/observability |

## 21. Praktické controls

- definuj allowed communication graph;
- používaj explicitné project a network identities;
- pripájaj service iba k potrebným networks;
- používaj service DNS, nie container IP;
- publikuj iba ports potrebné pre host/external clients;
- explicitne uvádzaj host bind address a address family;
- testuj socket bind pred firewallom;
- koreluj endpoint generation s DNS a readiness;
- audituj host aj upstream policy na reálnom packet path-e;
- sleduj conntrack, ephemeral ports a MTU;
- nepoužívaj host network ako diagnostický bypass;
- overuj allowed aj forbidden flows z reálnych source points.

## 22. Kontrolné otázky

1. Ako sa líši Docker network object, endpoint a port-publication subject?
2. Prečo `EXPOSE` ani `-p` nevytvoria application listener?
3. Prečo internal service traffic nemá používať host-published port?
4. Ako Compose project name mení DNS a network identity?
5. Čo znamená mapping `127.0.0.1:18080:8080`?
6. Prečo kontrola iba host `INPUT` policy nemusí vysvetliť published flow?
7. Ako sa mení path pri Docker Desktop alebo rootless Engine?
8. Ako sa prejaví conntrack exhaustion a MTU black hole?
9. Prečo host network mode nie je všeobecná oprava?
10. Ktoré observation points odlíšia socket, mapping, firewall a upstream route failure?

## Glossary impact

Relevantné pojmy: Docker network subject, Docker endpoint subject, Docker DNS generation, service alias ownership, host-publication subject, internal direct path, publication exposure generation, project-network split, Docker forwarding path, address-family publication contract a endpoint replacement proof.

## Oficiálna dokumentácia

- [Docker networking overview](https://docs.docker.com/engine/network/)
- [Port publishing and mapping](https://docs.docker.com/engine/network/port-publishing/)
- [Bridge network driver](https://docs.docker.com/engine/network/drivers/bridge/)
- [Docker container run](https://docs.docker.com/reference/cli/docker/container/run/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Volumes a bind mounts](volumes-bind-mounts.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Environment variables a health checks →](environment-variables-health-checks.md)
<!-- KNOWLEDGE-NAVIGATION:END -->