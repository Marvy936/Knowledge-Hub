# Volumes a bind mounts

Docker runtime musí oddeliť ephemeral container filesystem od dát, ktoré majú prežiť replacement containeru alebo ktoré pochádzajú z hosta. Docker poskytuje viac mount typov; najdôležitejšie sú **volumes**, **bind mounts** a **tmpfs**. Majú odlišný ownership, portability, security a backup model.

## 1. Writable layer nestačí

Každý container má writable layer nad image layers. Je vhodná pre:

- dočasné runtime files,
- process-local cache,
- krátkodobé scratch dáta,
- files, ktoré sa môžu stratiť pri replacement-e.

Nie je vhodná ako jediný storage pre:

- databázové dáta,
- user uploads,
- audit records,
- dlhodobé application state,
- artifacts potrebné po zmazaní containeru.

Container replacement typicky vytvorí novú writable layer.

## 2. Mount prekryje image content

Ak mountneš volume alebo bind mount na path, ktorý už obsahuje image files, mount ich v runtime view prekryje.

Príklad:

```bash
docker run --mount type=volume,src=example-data,dst=/var/lib/example example:1
```

Ak `/var/lib/example` obsahoval files v image, process po mountnutí vidí content volume-u. To môže vyzerať ako strata files, hoci zostali v lower image layer.

## 3. Docker volume

Volume je storage object spravovaný Docker daemon-om.

```bash
docker volume create example-data

docker run --mount type=volume,src=example-data,dst=/var/lib/example example:1
```

Vlastnosti:

- má vlastné meno a lifecycle,
- nie je automaticky zmazaný s containerom,
- host path spravuje Docker/driver,
- možno ho pripojiť k viacerým containers podľa storage semantics,
- môže používať local alebo external volume driver.

Volume nie je automaticky remote, replicated ani backed up.

## 4. Anonymous a named volumes

### Named volume

```bash
docker run --mount type=volume,src=example-data,dst=/data example:1
```

Má explicitnú identity a je vhodnejší pre lifecycle automation.

### Anonymous volume

```bash
docker run -v /data example:1
```

Docker vytvorí generované volume name. Dáta môžu prežiť container, ale ownership a cleanup sú menej čitateľné.

Preferuj named volumes pre intentional persistence.

## 5. Bind mount

Bind mount sprístupní konkrétny host path do containeru:

```bash
docker run \
  --mount type=bind,src=/srv/example/config,dst=/etc/example,ro \
  example:1
```

Vlastnosti:

- závisí od existencie a semantics host pathu,
- používa host filesystem permissions a labels,
- znižuje portability,
- môže sprístupniť citlivý host content,
- container môže pri write mount-e meniť host files.

Bind mount je vhodný napríklad pre:

- development source tree,
- explicitný read-only config file,
- host-generated certificates alebo sockets pri presnom threat modeli,
- integration s host toolingom.

## 6. `--mount` vs. `-v`

Moderný explicitný zápis:

```bash
docker run --mount type=bind,src=/host/path,dst=/container/path,ro image
```

Kratší zápis:

```bash
docker run -v /host/path:/container/path:ro image
```

`--mount` je čitateľnejší a presnejšie odlišuje:

- type,
- source,
- destination,
- read-only flag,
- propagation a ďalšie options.

Pri bind mount-e môže `-v` v niektorých prípadoch vytvoriť chýbajúci source directory, čo môže maskovať typo. `--mount` typicky zlyhá explicitnejšie.

## 7. Read-only mount

```bash
docker run --mount type=bind,src=/srv/config,dst=/etc/example,readonly example:1
```

Read-only znižuje write blast radius, ale process môže stále:

- čítať secrets,
- exfiltrovať content,
- používať citlivé sockets,
- ovplyvniť external system cez credentials v files.

Read-only nie je access-control náhrada za správny scope zdroja.

## 8. tmpfs

```bash
docker run --mount type=tmpfs,dst=/run/example,tmpfs-size=64m example:1
```

Tmpfs:

- uchováva dáta v memory-backed filesysteme,
- neprežije container stop/recreate alebo host reboot podľa lifecycle,
- je vhodný pre ephemeral secrets alebo runtime scratch podľa rizika,
- spotrebúva memory a potrebuje limit.

Tmpfs nezaručuje, že plaintext nikdy nebude swapnutý alebo zachytený v memory dump-e; závisí od host konfigurácie.

## 9. Initial population volume-u

Pri prvom mountnutí prázdneho volume-u na image directory môže Docker pri určitom volume workflowe skopírovať existujúci image content do volume-u. Toto behavior nesmie byť nejasným migration mechanizmom.

Preferuj explicitný initialization alebo migration proces s:

- versionou schema,
- idempotenciou,
- ownershipom,
- error handlingom,
- rollback/recovery postupom.

## 10. UID, GID a permissions

Container process zapisuje podľa kernel UID/GID a filesystem permissions.

Problém:

- image používa UID `10001`,
- volume files vlastní root alebo iný host UID,
- application dostane `permission denied`.

Možnosti:

- pripraviť ownership pred spustením,
- použiť init/migration job,
- nastaviť vhodný UID/GID contract,
- použiť filesystem ACL podľa potreby,
- zohľadniť user namespace mapping,
- na SELinux hoste nastaviť správny label.

Nepoužívaj `chmod 777` ako univerzálnu opravu.

## 11. SELinux a AppArmor

Na SELinux systéme nestačia tradičné Unix permissions. Bind-mounted content potrebuje vhodný security label.

Docker volume/bind syntax môže podporovať relabel options podľa platformy, ale ich použitie musí zodpovedať tomu, či je content zdieľaný alebo exkluzívny.

AppArmor typicky riadi process access podľa profilu; pri mountoch treba rozlišovať filesystem permissions, namespace view a LSM policy.

## 12. Bind propagation

Mount propagation určuje, či nested mounts vzniknuté na jednej strane mount boundary budú viditeľné na druhej strane.

Režimy ako `rprivate`, `rshared` alebo `rslave` sú potrebné iba pri špecifických use cases, napríklad nested container/storage tooling.

Široká shared propagation zväčšuje host coupling a attack surface. Default nemen bez jasnej potreby.

## 13. Devices a sockets nie sú bežné files

Bind mount Docker socketu:

```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock image
```

často dá containeru kontrolu nad host daemon-om.

Podobne citlivé sú:

- host `/dev` devices,
- SSH agent socket,
- cloud metadata proxy socket,
- system D-Bus,
- kubelet/runtime sockets,
- database Unix sockets.

Mount access posudzuj podľa capability zdroja, nie iba podľa read/write flagu.

## 14. Docker Desktop path model

Na Windows/macOS Linux containers typicky bežia vo VM. Bind mount host pathu prechádza file-sharing vrstvou.

Dôsledky:

- odlišná path syntax,
- case-sensitivity rozdiely,
- UID/GID translation,
- filesystem event/watch behavior,
- nižší výkon pri veľkom množstve malých files,
- potreba explicitného file-sharing povolenia.

Development workload môže mať iný bind-mount performance profil než production Linux host.

## 15. Volume drivers

Volume driver môže integrovať:

- network filesystem,
- block storage,
- cloud volume service,
- encrypted storage,
- vendor appliance.

Driver neurčuje automaticky application correctness. Potrebuješ poznať:

- access modes,
- attach/detach semantics,
- failover a fencing,
- latency a throughput,
- consistency,
- snapshots/backups,
- encryption,
- topology restrictions.

## 16. Viac containers a shared volume

To, že Docker dovolí mountnúť volume do viacerých containers, neznamená, že application alebo filesystem podporuje concurrent writers.

Over:

- single-writer vs. multi-writer contract,
- file locking,
- database clustering semantics,
- host/node locality,
- leader election/fencing,
- failure recovery.

Shared filesystem nezmení single-node databázu na cluster.

## 17. Backup

Backup musí definovať:

- čo je authoritative data set,
- crash-consistent alebo application-consistent model,
- encryption a access,
- retention,
- off-host/off-account kópiu,
- restore target,
- RPO/RTO,
- pravidelné restore testy.

Kopírovanie live database directory bez koordinácie nemusí vytvoriť použiteľný backup.

## 18. Migration a schema lifecycle

Container image a data schema majú odlišný lifecycle.

Pri release:

1. over kompatibilitu novej image so starou schema,
2. vykonaj versionovanú migration,
3. zaznamenaj migration status,
4. zachovaj rollback window podľa compatibility modelu,
5. neviaž migration iba na náhodný startup race viacerých replicas.

Volume nesmie skrývať neversionovaný mutable state.

## 19. Compose volumes

Príklad:

```yaml
services:
  db:
    image: postgres:17
    volumes:
      - type: volume
        source: db-data
        target: /var/lib/postgresql/data

  app:
    image: example:1
    volumes:
      - type: bind
        source: ./config/app.yaml
        target: /etc/example/app.yaml
        read_only: true

volumes:
  db-data:
```

Top-level volume deklaruje storage object. Service mount určuje, kde a ako sa použije.

## 20. Cleanup

```bash
docker volume ls
docker volume inspect example-data
docker volume rm example-data
docker volume prune
```

Pred cleanupom over:

- ktorý container/service volume používa,
- owner a environment,
- backup/retention,
- external driver semantics,
- či ide o orphan alebo stále authoritative state.

`docker compose down -v` môže odstrániť Compose-managed volumes a tým aj dáta.

## 21. Anti-patterny

### Databáza iba vo writable layeri

Replacement odstráni jedinú kópiu dát.

### Bind mount host root filesystemu

Container získava široký host read/write access.

### Relative bind path bez kontroly working directory

Pipeline alebo operator mountne nesprávny directory.

### Anonymous volumes bez ownershipu

Vznikajú orphan dáta a nejasný cleanup.

### `chmod 777` na shared storage

Maskuje identity a policy problém.

### Backup považovaný za hot copy directory

Výsledok nemusí byť application-consistent.

### Mount Docker socketu ako jednoduchá integrácia

Prakticky odovzdáva host-control capability.

## 22. Troubleshooting

### Files z image „zmizli“

Mount prekryl destination path. Skontroluj mount list cez `docker inspect`.

### `permission denied`

Over process UID/GID, volume ownership, user namespaces, read-only flag a SELinux/AppArmor denial.

### Bind mount source je prázdny

Over host path, Docker context/remote daemon, Docker Desktop file sharing a relative-path resolution.

### Volume prežilo `docker rm`

Je to očakávané pri oddelenom volume lifecycle. Over volume name a retention.

### Databáza po restore nenabehne

Over application-consistency, WAL/journal, version compatibility, ownership a restore postup.

### Performance je zlá iba na Desktop bind mount-e

Over file-sharing backend, množstvo malých files, watcher behavior a presun dependency/cache data do Docker volume-u.

## 23. Kontrolné otázky

1. Prečo writable layer nie je vhodná pre authoritative state?
2. Aký je rozdiel medzi volume a bind mountom?
3. Čo sa stane, keď mount prekryje image directory?
4. Prečo je named volume vhodnejší než anonymous volume?
5. Čo read-only mount rieši a čo nerieši?
6. Kedy je vhodný tmpfs?
7. Prečo vznikajú UID/GID problémy?
8. Aké riziko má Docker socket mount?
9. Prečo shared volume neznamená podporu multi-writer aplikácie?
10. Čo odlišuje backup od snapshotu alebo live file copy?

## Glossary impact

Relevantné pojmy: Docker volume, named volume, anonymous volume, Docker bind mount, tmpfs mount, mount obscuring, volume initialization, bind propagation, volume driver, storage access mode, Docker Desktop file sharing a orphan volume.

## Oficiálna dokumentácia

- [Docker storage](https://docs.docker.com/engine/storage/)
- [Volumes](https://docs.docker.com/engine/storage/volumes/)
- [Bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)
- [Compose volumes](https://docs.docker.com/reference/compose-file/volumes/)
