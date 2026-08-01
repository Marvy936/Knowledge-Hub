# Docker networks a port publishing

Docker network object, container endpoint a published host port sú tri rozdielne veci. Network object definuje driver a network-wide configuration. Container endpoint predstavuje pripojenie konkrétneho containeru do tejto siete. Port publishing vytvára samostatnú cestu z host address a portu na container port.

Táto separácia vysvetľuje bežné situácie: container môže byť pripojený do správnej network, ale aplikácia počúva iba na loopbacku. Port môže byť publikovaný, ale host firewall ho blokuje. Service môže fungovať cez Compose DNS a zároveň byť zámerne nedostupná z hosta, pretože nemá žiadny published port.

Budeme používať dve služby: `payments-api` a `verifier`. Obe budú v user-defined network `atlas-backend`. Iba API dostane host publication `127.0.0.1:18080:8080`.

## 1. Network object

Vytvor sieť:

```bash
docker network create atlas-backend
```

Inspect:

```bash
docker network inspect atlas-backend
```

Výstup obsahuje driver, subnet alebo IPAM configuration, options, labels a pripojené containers. Pri default bridge driveri Docker vytvorí L2/L3 dataplane na jednom Engine hoste.

Network name je user-facing identity. Interný network ID je presnejší pri diagnostike, pretože rovnaké meno môže existovať na inom Docker contexte alebo po delete/recreate označovať nový object.

```bash
docker network inspect atlas-backend --format '{{.Id}}'
```

## 2. Endpoint vznikne pri pripojení containeru

Spusti API:

```bash
docker run -d --rm \
  --name payments-api \
  --network atlas-backend \
  atlas/payments-api:1.0.0
```

Engine vytvorí endpoint, pridelí IP a pridá DNS records pre meno containeru. Observed state:

```bash
docker inspect payments-api \
  --format '{{json .NetworkSettings.Networks}}' | jq .
```

Container môže byť pripojený k viacerým networks. Každé pripojenie má samostatný endpoint, adresu a aliases.

```bash
docker network connect monitoring payments-api
docker network disconnect monitoring payments-api
```

Dynamic connect nemení image ani container ID, ale mení effective runtime network state. Declarative automation má túto zmenu zachytiť, inak po recreate zmizne.

## 3. Embedded DNS a aliases

Na user-defined network Docker poskytuje name resolution. Verifier môže volať API podľa mena:

```bash
docker run --rm \
  --network atlas-backend \
  curlimages/curl:8.10.1 \
  curl -fsS http://payments-api:8080/readyz
```

Network alias možno pridať pri spustení:

```bash
docker run -d --rm \
  --name payments-v1 \
  --network atlas-backend \
  --network-alias payments-api \
  atlas/payments-api:1.0.0
```

Alias patrí endpointu v konkrétnej network. Rovnaký container môže mať iný alias v inej sieti.

DNS odpoveď neznamená, že endpoint je ready. Docker DNS pozná runtime membership, nie application health. Client musí zvládnuť connection failure a replacement.

## 4. `EXPOSE`, `expose` a `ports`

Dockerfile:

```dockerfile
EXPOSE 8080
```

pridá image metadata. Compose `expose` dokumentuje alebo sprístupňuje container ports v model semantics, ale nevytvára host publication.

```yaml
services:
  api:
    expose:
      - "8080"
```

Host path vznikne cez `ports` alebo `--publish`:

```yaml
services:
  api:
    ports:
      - target: 8080
        published: "18080"
        host_ip: 127.0.0.1
        protocol: tcp
```

Tieto tri mechanizmy sa nemajú zamieňať. Internal service-to-service communication používa container port a network DNS. Host client používa published host port.

## 5. Short publish syntax a broad bind

Príkaz:

```bash
docker run -p 18080:8080 IMAGE
```

neuvádza host IP. Docker publikuje port podľa platform defaultu, často na všetkých host addresses. To môže neplánovane vystaviť development service do LAN alebo internetu, ak host firewall traffic povoľuje.

Bezpečnejší local-only bind:

```bash
docker run -p 127.0.0.1:18080:8080 IMAGE
```

IPv6 bind má vlastnú syntax a platformové správanie. Pri exposure audite skontroluj observed mapping, nie iba source Compose file:

```bash
docker port payments-api
docker inspect payments-api \
  --format '{{json .NetworkSettings.Ports}}' | jq .
```

## 6. Host port a container port nemusia byť rovnaké

```text
127.0.0.1:18080
→ host publication
→ container endpoint:8080
```

Aplikácia nemusí vedieť, že host používa port `18080`. Vo svojom namespace počúva na `8080`. External clients používajú host port.

To umožňuje spustiť viac instances s rozdielnymi host ports:

```bash
docker run -d --name api-1 -p 127.0.0.1:18081:8080 IMAGE
docker run -d --name api-2 -p 127.0.0.1:18082:8080 IMAGE
```

Nie je to automatický load balancer. Clients alebo reverse proxy musia vedieť o oboch endpoints.

## 7. Ephemeral host port

Ak host port nešpecifikuješ, Docker môže prideliť voľný port:

```bash
docker run -d --name payments-random -P IMAGE
```

Zisti ho:

```bash
docker port payments-random 8080
```

Ephemeral publication je vhodná pre paralelné tests. Test harness musí read-backnúť observed port. Hardcoded očakávanie vytvára race a collision.

Pri Compose long syntax možno `published` vynechať podľa podporovaného modelu a zistiť allocation cez `docker compose port`.

## 8. Application bind musí zodpovedať endpointu

Port publishing smeruje traffic na container interface. Ak process počúva iba na container loopbacku, host path zlyhá.

```text
LISTEN_ADDRESS=127.0.0.1:8080
```

je vhodné iba pre clients v rovnakom network namespace. Pre bridge service:

```text
LISTEN_ADDRESS=:8080
```

alebo `0.0.0.0:8080` umožní IPv4 traffic cez `eth0`.

Over tri rôzne paths:

```bash
# local health vo vnútri containeru
docker exec payments-api /usr/local/bin/payments-api healthcheck

# service DNS z iného containeru
docker run --rm --network atlas-backend curlimages/curl:8.10.1 \
  curl -fsS http://payments-api:8080/readyz

# host publication
curl -fsS http://127.0.0.1:18080/readyz
```

Jeden PASS nenahrádza ostatné.

## 9. `internal` network

Compose network môže byť označená `internal`:

```yaml
networks:
  backend:
    internal: true
```

Engine vytvorí externally isolated network podľa driver semantics. Services v nej môžu komunikovať medzi sebou, ale nemajú štandardný external route cez túto network.

Ak container potrebuje aj egress, môže byť pripojený k druhej network. To vytvára multi-homed workload a treba rozhodnúť, ktorá route je defaultná a ktoré peers sú dostupné.

`internal: true` nie je náhrada host firewallu, application authentication alebo cloud network policy. Je to jedna Docker network vlastnosť.

## 10. Default network v Compose

Compose project bez explicitnej network vytvorí default project network. Service names sa v nej resolve-nú automaticky.

```yaml
services:
  api:
    image: atlas/payments-api:1.0.0
  verifier:
    image: curlimages/curl:8.10.1
```

Môže vzniknúť napríklad `atlas_default`. Project name je súčasť resource identity. Dve pipelines s rovnakým project name môžu používať rovnakú network a navzájom meniť endpoints.

Production-like Compose má explicitné project naming a networks:

```yaml
name: atlas-payments

services:
  api:
    networks:
      - backend

networks:
  backend:
    internal: true
```

## 11. `network_mode`

`network_mode: host` používa host network stack a obchádza bežné bridge endpointy. `network_mode: none` vytvorí workload bez bežného network pripojenia. `network_mode: service:api` môže zdieľať network namespace s inou service.

Zdieľanie network namespace-u znamená spoločný loopback a port space. Verifier v `network_mode: service:api` môže úspešne volať `127.0.0.1`, ale tým netestuje service DNS ani bridge path.

Network mode má byť explicitný a nesmie sa používať ako rýchla oprava nepochopeného bridge problému.

## 12. Firewall a Docker rules

Na Linux hoste Docker programuje firewall alebo packet filtering rules podľa daemon configuration a backendu. Port publication môže obísť očakávanie používateľa, ktorý kontroluje iba jednu host firewall chain.

Presné interné rules sa menia podľa nftables/iptables backendu a Docker verzie. Pri platform policy používaj dokumentované Docker integration points a testuj allowed aj denied paths.

Host port existence:

```bash
ss -lntp | grep 18080
```

nemusí pri každej implementácii ukázať tradičný userspace listener; dataplane môže byť realizovaný NAT rules. Rozhodujúci je end-to-end packet test a Docker inspect.

## 13. Port collision

Dva containers nemôžu na rovnakom host IP/protocol/port vytvoriť rovnakú publication.

```bash
docker run -d --name api-1 -p 127.0.0.1:18080:8080 IMAGE
docker run -d --name api-2 -p 127.0.0.1:18080:8080 IMAGE
```

Druhý príkaz zlyhá. Pri Compose parallel CI jobs vzniká collision, ak používajú rovnaký fixed host port. Riešením je unikátny project/port allocation alebo testy cez internal service network bez host publication.

## 14. UDP a protocol identity

Publication má aj protocol:

```bash
docker run -p 127.0.0.1:15353:53/udp DNS_IMAGE
```

TCP a UDP port `53` sú odlišné sockets. Inspect a firewall audit musia uvádzať protocol. Test TCP spojenia nepreukazuje UDP flow.

Compose:

```yaml
ports:
  - target: 53
    published: "15353"
    host_ip: 127.0.0.1
    protocol: udp
```

## 15. Incident: development API bolo vystavené do LAN

Developer použil:

```bash
docker run -p 8080:8080 payments-api
```

Predpokladal, že port je dostupný iba cez `localhost`. Host bol pripojený do office LAN a firewall povoľoval inbound traffic. API nemalo authentication, pretože išlo o local mock.

Observed mapping bol `0.0.0.0:8080`. Služba bola dostupná z iného zariadenia.

Oprava zmenila default local command na:

```bash
-p 127.0.0.1:8080:8080
```

A security test overoval connection failure z non-loopback interface. Dokumentácia začala vždy uvádzať host IP, nie iba port pair.

## 16. Incident: verifier vytvoril falošný network PASS

Compose verifier používal:

```yaml
network_mode: service:api
```

A volal `http://127.0.0.1:8080`. Test prešiel, hoci API bolo bindnuté iba na loopback. V production orchestrátore mal verifier samostatný network namespace a traffic zlyhal.

Oprava pripojila verifier do rovnakej user-defined network ako samostatný endpoint a volala `http://payments-api:8080`. Host port mal ďalší nezávislý test.

## 17. Systematický Docker network audit

Pre jednu service zachovaj:

```bash
docker inspect payments-api > container.json
docker network inspect atlas-backend > network.json
docker port payments-api
```

Skontroluj image `EXPOSE`, effective application bind, endpoint IP, aliases, routes, published host address, protocol a host firewall. Pri Compose navyše:

```bash
docker compose config > compose-resolved.yaml
docker compose ps
docker compose port api 8080
```

Ak internal path funguje a host path nie, sústreď sa na publication, bind address a host dataplane. Ak DNS zlyhá, skontroluj network membership a alias. Ak connect prejde, ale request timeoutuje, pokračuj application a return-path analýzou.

## Čo si z kapitoly odniesť

Docker network object definuje network. Container endpoint je pripojenie konkrétnej runtime generation. Port publishing vytvára host-to-container path. `EXPOSE` a Compose `expose` nevytvárajú host listener.

Service DNS funguje iba v relevantnej user-defined alebo Compose network. Container IP nie je stabilná service identity. Host publication má explicitne uvádzať host IP, port a protocol. Local health, service DNS a host port sú tri samostatné testy. Network modes, aliases a dynamic connect menia effective runtime state a musia byť read-backnuté, nie iba predpokladané zo source YAML.

## Primárne zdroje

- [Docker network drivers](https://docs.docker.com/engine/network/drivers/)
- [Bridge driver](https://docs.docker.com/engine/network/drivers/bridge/)
- [Port publishing](https://docs.docker.com/engine/network/port-publishing/)
- [Compose networks](https://docs.docker.com/reference/compose-file/networks/)
- [Compose ports](https://docs.docker.com/reference/compose-file/services/#ports)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Volumes a bind mounts](volumes-bind-mounts.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Environment variables a health checks →](environment-variables-health-checks.md)
<!-- KNOWLEDGE-NAVIGATION:END -->