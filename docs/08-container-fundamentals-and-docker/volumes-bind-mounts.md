# Volumes a bind mounts

Docker mount spája konkrétny storage source s pathom v mount namespace-e containeru. Z pohľadu aplikácie môže named volume aj bind mount vyzerať ako obyčajný adresár. Z prevádzkového pohľadu však majú úplne inú identitu, portability, ownership a cleanup lifecycle.

Named volume spravuje Docker Engine a referencuje sa menom. Bind mount referencuje konkrétny host path. Tmpfs nemá persistentný diskový source. Pri incidente preto nestačí vedieť, že aplikácia zapisuje do `/var/lib/atlas-payments`. Musíme vedieť, čo je na tento path skutočne mountnuté na konkrétnom Docker daemone.

Budeme pracovať s `payments-api`, ktorá beží ako UID `65532` a zapisuje JSONL ledger do `/var/lib/atlas-payments/payments.jsonl`.

## 1. `--mount` ukazuje celý contract

Docker podporuje short `-v` syntax aj explicitnejší `--mount`. Pre výklad a automation je `--mount` čitateľnejší:

```bash
docker run --rm \
  --mount type=volume,source=payments-data,target=/var/lib/atlas-payments \
  IMAGE
```

Príkaz explicitne hovorí, že source je Docker volume `payments-data` a target je path v containere.

Bind mount:

```bash
docker run --rm \
  --mount type=bind,source="$PWD/local-data",target=/var/lib/atlas-payments \
  IMAGE
```

Tu je source konkrétny path na hoste Docker daemonu. Pri remote Docker contexte to nemusí byť filesystem laptopu, z ktorého sa CLI spustilo. Je to filesystem remote hosta.

## 2. Named volume identity

Vytvor volume:

```bash
docker volume create payments-data
```

Inspect:

```bash
docker volume inspect payments-data
```

Výstup ukáže driver, mountpoint alebo driver options, labels a scope. Mountpoint pri local driveri je implementačný detail spravovaný Dockerom. Aplikácia ani bežná automation sa nemajú viazať na internú host cestu pod Docker data rootom.

Volume možno pripojiť viacerým containers:

```bash
docker run --rm \
  --mount type=volume,source=payments-data,target=/data \
  alpine:3.22 \
  sh -c 'echo pay-100 > /data/ledger.txt'

docker run --rm \
  --mount type=volume,source=payments-data,target=/data,readonly \
  alpine:3.22 \
  cat /data/ledger.txt
```

Druhý container používa rovnaký source object. Read-only mount chráni pred zmenou z tohto containeru, ale prvý writer alebo host administrator dáta stále môže meniť.

## 3. Anonymous volume

Dockerfile môže deklarovať:

```dockerfile
VOLUME ["/var/lib/atlas-payments"]
```

Ak runtime nepriradí named source, Docker môže vytvoriť anonymous volume s generovaným menom. Dáta prežijú container removal podľa konkrétneho cleanup príkazu, ale identity sa spravuje ťažšie.

```bash
docker inspect CONTAINER | jq '.[0].Mounts'
```

ukáže skutočné volume name. Anonymous volumes môžu zostať orphaned a zaberať disk. Pre business dáta je explicitné meno alebo orchestrator-managed persistent identity čitateľnejšia.

Dockerfile `VOLUME` navyše nevie určiť production driver, backup policy alebo access mode. Tieto rozhodnutia patria deployment vrstve.

## 4. Bind mount a host coupling

Bind mount používa presný host path. Je vhodný pri local development:

```bash
docker run --rm \
  --mount type=bind,source="$PWD/config",target=/etc/atlas,readonly \
  IMAGE
```

Aplikácia okamžite vidí zmenu host config file-u. To je pohodlné, ale production image a runtime sa stávajú závislé od host layoutu a file semantics.

Pri remote daemon-e:

```bash
docker context use remote-prod
docker run --mount type=bind,source=/srv/payments,target=/data IMAGE
```

`/srv/payments` sa hľadá na `remote-prod`, nie na client hoste. Neexistujúci source môže spôsobiť chybu alebo pri legacy `-v` syntax vzniknúť ako prázdny directory podľa použitia, čo môže zakryť chybu.

Preto je `--mount` preferované: pri chýbajúcom bind source typicky zlyhá explicitne.

## 5. Read-only a recursive semantics

Bind alebo volume možno mountnúť read-only:

```bash
--mount type=bind,source="$PWD/config",target=/etc/atlas,readonly
```

Read-only sa týka mountu z pohľadu containeru. Host process s oprávnením môže source meniť a container zmenu uvidí.

Pri bind mountoch s nested mounts závisí recursive správanie a read-only enforcement od kernel a Docker možností. Broad host tree s nested mounts môže do containeru preniesť viac objects, než review očakáva.

Mount source preto má byť čo najužší. Namiesto `/srv` mountni `/srv/atlas/payments/config.yaml`, ak aplikácia potrebuje jeden file.

## 6. Mount obscuring

Mount zakryje image content v target path-e. Ak image obsahuje default configuration:

```text
/etc/atlas/config.yaml
```

a runtime mountne directory na `/etc/atlas`, process vidí obsah mount source-u. Default file z image-u je zakrytý.

```bash
docker inspect CONTAINER --format '{{json .Mounts}}' | jq .
```

Pri diagnostike porovnaj image bez mountu:

```bash
id="$(docker create IMAGE)"
docker export "$id" | tar -tf - | grep 'etc/atlas/config.yaml'
docker rm "$id"
```

Ak file je v image-i, ale nie v running containere, mount obscuring je silná hypotéza.

## 7. Volume copy-up pri prvom použití

Pri prázdnom Docker volume mountnutom na non-empty image directory môže Docker podľa volume semantics skopírovať existujúci directory content do volume-u. To je pohodlné pre default data, ale môže byť prekvapivé a pri veľkom obsahu pomalé.

Option `volume-nocopy` môže copy-up potlačiť:

```bash
--mount type=volume,source=payments-data,target=/var/lib/atlas-payments,volume-nocopy
```

Aplikácia potom musí volume inicializovať explicitne. Explicitný initializer je čitateľnejší, keď potrebujeme schema version, ownership a idempotentný migration contract.

## 8. UID/GID a permissions

Docker volume nemá automaticky application user ownership. `payments-api` ako UID `65532` potrebuje write access.

Initializer:

```bash
docker run --rm \
  --user 0:0 \
  --mount type=volume,source=payments-data,target=/data \
  busybox:1.36.1 \
  sh -ec 'mkdir -p /data && chown 65532:65532 /data && chmod 0750 /data'
```

Potom application container:

```bash
docker run --rm \
  --user 65532:65532 \
  --mount type=volume,source=payments-data,target=/var/lib/atlas-payments \
  IMAGE
```

Pri bind mountoch ownership pochádza z host filesystemu. Docker Desktop môže používať translation alebo file-sharing mechanizmus, ktorý sa správa inak než native Linux. Produkčný test má preto prebehnúť na reprezentatívnom filesysteme.

## 9. SELinux labels

Na SELinux hoste môže bind mount zlyhať aj pri správnych Unix permissions. Docker short syntax podporuje `:z` alebo `:Z` relabel semantics pre vybrané use cases:

```bash
docker run --rm \
  -v "$PWD/local-data:/data:Z" \
  IMAGE
```

`Z` typicky nastaví private label pre jeden container, zatiaľ čo `z` umožňuje shared content podľa Docker/SELinux modelu. Relabel broad alebo system path môže byť nebezpečný. Nepoužívaj ho naslepo na `/home`, `/var` alebo host root.

Pri denial analyzuj audit log a konkrétne labels namiesto vypnutia SELinux.

## 10. Bind propagation

Mount propagation určuje, či mounts vytvorené pod source alebo target pathom prechádzajú medzi hostom a containerom. Default private semantics sú bezpečnejšie pre bežné applications.

Shared propagation je potrebná pre niektoré low-level storage alebo container-in-container tools, ale rozširuje host interaction. `payments-api` ju nepotrebuje.

Ak workload žiada `rshared` iba preto, že bez toho „volume nefunguje“, treba najprv pochopiť, ktoré nested mounts chce prenášať a prečo.

## 11. Compose volume names

Compose bez explicitného name vytvára project-scoped volume:

```yaml
services:
  api:
    volumes:
      - payments-data:/var/lib/atlas-payments

volumes:
  payments-data: {}
```

Pri project name `atlas-dev` môže vzniknúť `atlas-dev_payments-data`. Zmena project name vytvorí iný volume a aplikácia uvidí prázdne dáta.

Ak data identity má zostať stabilná naprieč project rename, nastav explicitné meno:

```yaml
volumes:
  payments-data:
    name: atlas-payments-data
```

To zároveň znamená, že viac Compose projects môže používať rovnaký volume. Ownership a collision sa musia riadiť vedome.

External volume:

```yaml
volumes:
  payments-data:
    external: true
    name: atlas-payments-data
```

Compose ho nevytvorí a očakáva, že existuje. To je vhodné, keď storage lifecycle vlastní iný provisioning systém.

## 12. Bind mount v Compose

Long syntax:

```yaml
services:
  api:
    volumes:
      - type: bind
        source: ./config
        target: /etc/atlas
        read_only: true
      - type: volume
        source: payments-data
        target: /var/lib/atlas-payments
```

Relative bind source sa interpretuje podľa Compose project/file pravidiel. Pri remote deployment a non-local platforms nemusí byť supported rovnako. `docker compose config` ukáže resolved paths a model:

```bash
docker compose config > compose-resolved.yaml
```

Pred `up` skontroluj, že source path a volume name zodpovedajú očakávanému daemon hostu.

## 13. Backup volume-u

Pre jednoduchý zastavený file workload:

```bash
mkdir -p backups

docker run --rm \
  --mount type=volume,source=payments-data,target=/data,readonly \
  --mount type=bind,source="$PWD/backups",target=/backup \
  alpine:3.22 \
  tar -C /data -czf /backup/payments-data.tgz .
```

Restore do nového volume-u:

```bash
docker volume create payments-data-restore

docker run --rm \
  --mount type=volume,source=payments-data-restore,target=/data \
  --mount type=bind,source="$PWD/backups",target=/backup,readonly \
  alpine:3.22 \
  tar -C /data -xzf /backup/payments-data.tgz
```

Potom spusti aplikáciu s restore volume-om a over business read. Tar exit code nie je recovery acceptance.

Pri database files používaj database-native backup alebo coordinated snapshot.

## 14. Cleanup

Container removal named volume štandardne neodstráni:

```bash
docker rm -f payments-api
docker volume inspect payments-data
```

Explicitné odstránenie:

```bash
docker volume rm payments-data
```

Compose:

```bash
docker compose down
```

ponechá named volumes, zatiaľ čo:

```bash
docker compose down --volumes
```

ich odstráni. Pred destructive command over data owner, backup a active consumers.

## 15. Incident: staging mountlo production directory

Compose override používal environment interpolation:

```yaml
volumes:
  - type: bind
    source: ${PAYMENTS_DATA_DIR}
    target: /var/lib/atlas-payments
```

Staging shell mal zdedenú premennú `PAYMENTS_DATA_DIR=/srv/payments-prod`. Staging container dostal write access k production files.

`docker compose config` by ukázal resolved source, ale pipeline ho nekontrolovala. Incident vznikol ešte pred application startom.

Oprava odstránila broad host bind, prešla na environment-specific named volumes a pridala policy, ktorá odmietla host paths mimo staging rootu. Production data dostali samostatný owner a backup flow.

## 16. Incident: opravou permissions sa zmenil cudzí dataset

Initializer používal:

```sh
chown -R 65532:65532 /data
```

Volume bol omylom shared s analytics exporterom. Recursive chown zmenil ownership miliónov files a druhá aplikácia stratila access.

Recovery obnovila ownership z manifestu a zastavila writers. Trvalá oprava rozdelila volumes podľa ownera a initializer menil iba konkrétny application directory. Volume sharing sa stalo explicitným interface contractom.

## 17. Systematický mount troubleshooting

Pri chybe najprv identifikuj actual mount:

```bash
docker inspect CONTAINER | jq '.[0].Mounts'
docker volume inspect VOLUME
docker context show
```

Potom over source na správnom daemon hoste, target path, read-only flag, UID/GID, mode, ACL, SELinux/AppArmor a available capacity.

Competing hypotheses pri prázdnom adresári sú často: nový volume, iný Compose project name, bind na nesprávny host path, mount obscuring alebo initializer, ktorý pracoval s iným source objectom.

Pred recreate alebo cleanup zachovaj inspect a volume metadata. Nový container môže dostať inú mount identity a skryť pôvodnú chybu.

## Čo si z kapitoly odniesť

Named volume je Docker-managed data object. Bind mount je prepojenie na konkrétny host path. Anonymous volume má generovanú identity a horšie sa spravuje. Mount target môže zakryť image content.

Pri každom mounte treba poznať source, daemon context, target, read/write mode, UID/GID, labels, lifecycle a cleanup ownera. Compose project name ovplyvňuje generated volume names. Backup sa overuje restore testom a `down --volumes` alebo `volume prune` sú data-destructive operácie, nie bežná údržba bez inventory.

## Primárne zdroje

- [Docker volumes](https://docs.docker.com/engine/storage/volumes/)
- [Bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)
- [Storage overview](https://docs.docker.com/engine/storage/)
- [Compose volumes](https://docs.docker.com/reference/compose-file/volumes/)
- [Compose `down`](https://docs.docker.com/reference/cli/docker/compose/down/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Multi-stage builds](multi-stage-builds.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Docker networks a port publishing →](docker-networks-port-publishing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->