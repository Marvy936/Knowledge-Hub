# Images, layers a copy-on-write

Container image nie je jeden adresár zabalený do jedného archívu. Je to ordered graph filesystem changesetov a metadata. Keď runtime image spustí, nespojí všetky súbory do novej fyzickej kópie pre každý container. Vytvorí read-only pohľad na image layers a nad ne pridá zapisovateľnú vrstvu konkrétnej container instance.

Tento model vysvetľuje viacero Docker javov, ktoré inak pôsobia nesúvisiaco: prečo sa images medzi containers zdieľajú, prečo je vytvorenie ďalšieho containeru rýchle, prečo zmena veľkého súboru môže spotrebovať nečakane veľa miesta, prečo odstránenie secretu v neskoršom Dockerfile kroku neodstráni jeho bytes zo staršej layer a prečo dáta uložené iba do container writable layer zmiznú po odstránení containeru.

Budeme sledovať image `payments-api`, ktorý vzniká z troch významových vrstiev: minimálny runtime base, certificate bundle a aplikačný binary. Pri spustení pridá runtime samostatnú writable layer a named volume pre business dáta.

## 1. Layer je zmena, nie kompletný filesystem

Každá image layer opisuje zmenu voči predchádzajúcemu stavu. Môže pridať nový súbor, zmeniť metadata existujúceho pathu alebo označiť path ako odstránený.

Zjednodušený build môže vytvoriť tento graph:

```text
layer 1: runtime base filesystem
layer 2: CA certificates
layer 3: /usr/local/bin/payments-api
layer 4: metadata a ďalšie filesystem zmeny
```

Výsledný root filesystem je pohľad vytvorený aplikovaním layers v správnom poradí. Neskoršia layer môže zakryť súbor zo skoršej layer, ale staršia layer sa tým neprepíše. Je stále samostatným content-addressed blobom.

Približnú históriu lokálneho image-u možno zobraziť:

```bash
docker image history --no-trunc atlas/payments-api:1.0.0
```

History ukáže veľkosť a metadata jednotlivých build krokov. Nie je však úplným záznamom BuildKit graphu, cache rozhodnutí ani secret mountov. Je to pohľad na výslednú image history.

## 2. Prečo sa layers zdieľajú

Ak desať containers používa rovnaký image digest, runtime nemusí desaťkrát ukladať všetky read-only image layers. Content-addressed blobs a unpacked snapshots sa môžu zdieľať.

```text
payments container C1 ─┐
payments container C2 ─┼→ spoločné read-only image layers
payments container C3 ─┘
```

Každý container dostane iba vlastnú runtime konfiguráciu, mount namespace a writable layer. To znižuje diskovú spotrebu a zrýchľuje create lifecycle.

Zdieľanie však neznamená, že containers majú spoločný writable filesystem. Zápis do `/tmp/file` v containere C1 sa neobjaví automaticky v C2. Ak oba containers mountnú rovnaký named volume, zdieľanie vzniká cez volume, nie cez image layer.

## 3. Copy-on-write pri prvom zápise

Keď process iba číta súbor z image layer, runtime môže obslúžiť čítanie zo shared read-only snapshotu. Keď ho chce zmeniť, storage driver musí vytvoriť zapisovateľnú verziu pre konkrétny container. Tento proces sa často označuje ako copy-up.

```text
read /etc/payments/default.yaml
→ čítanie z read-only lower layer

write /etc/payments/default.yaml
→ copy-up do writable upper layer
→ zmena iba pre konkrétny container
```

Pri malom konfiguračnom súbore je overhead zanedbateľný. Pri veľkom databázovom alebo logovom súbore môže prvý zápis vyvolať kopírovanie veľkého objektu a výraznú I/O latenciu. Writable layer preto nie je vhodná ako univerzálny persistentný data store.

V Docker Engine možno veľkosť writable layer približne zobraziť:

```bash
docker ps --size
```

Tento údaj nevysvetľuje všetku spotrebu image store-u ani volume-u, ale pomáha rozlíšiť rast container layer od rastu external storage.

## 4. Odstránenie súboru a whiteout

Ak neskoršia layer odstráni súbor zo skoršej layer, nemôže spätne zmeniť immutable blob. Namiesto toho vytvorí whiteout, ktorý hovorí výslednému filesystem view-u, že path sa má považovať za odstránený.

To je dôležité pri secrets. Nasledujúci Dockerfile je chybný:

```dockerfile
COPY production.pem /tmp/production.pem
RUN use-key /tmp/production.pem && rm /tmp/production.pem
```

Prvá instruction uloží key do layer. Druhá layer pridá whiteout alebo zmenu, ktorá key skryje vo výslednom filesysteme. Bytes však zostávajú v skoršej layer a možno ich extrahovať z image graphu.

Správny model používa BuildKit secret mount:

```dockerfile
RUN --mount=type=secret,id=production_key \
    use-key /run/secrets/production_key
```

Secret file sa nestane bežným build-context file-om ani image layerom. Stále však treba dôverovať programu `use-key`; môže secret vložiť do outputu alebo ho odoslať po sieti.

## 5. Dockerfile instruction a layer nie sú vždy jedna k jednej

Pri klasickom mentálnom modeli sa každá filesystem-mutating Dockerfile instruction spája s layer. BuildKit však vykonáva graph a môže používať cache, bind mounts, cache mounts alebo metadata-only instructions. `ENV`, `CMD`, `ENTRYPOINT`, `USER` a `LABEL` menia image config, ale nemusia vytvoriť významný filesystem changeset.

```dockerfile
FROM alpine:3.22
RUN apk add --no-cache ca-certificates
COPY payments-api /usr/local/bin/payments-api
USER 65532:65532
ENTRYPOINT ["/usr/local/bin/payments-api"]
CMD ["serve"]
```

`RUN` a `COPY` menia filesystem. `USER`, `ENTRYPOINT` a `CMD` definujú runtime defaults v image configu. Pri analýze image-u preto treba kontrolovať filesystem layers aj config object.

```bash
docker image inspect IMAGE \
  --format '{{json .Config}}' | jq .
```

## 6. Prečo poradie Dockerfile krokov ovplyvňuje cache

Build cache môže reuse-nuť výsledok kroku iba vtedy, keď sa jeho inputs nezmenili podľa cache key modelu. Ak sa application source skopíruje pred dependency downloadom, každá source zmena môže invalidovať aj drahý dependency krok.

Menej výhodné poradie:

```dockerfile
COPY . .
RUN go mod download
RUN go build -o /out/payments-api ./cmd/payments-api
```

Lepšie poradie:

```dockerfile
COPY go.mod go.sum ./
RUN go mod download
COPY cmd ./cmd
RUN go build -o /out/payments-api ./cmd/payments-api
```

`go mod download` teraz závisí najmä od module files. Zmena `main.go` nemusí invalidovať dependency cache.

Cache však nie je correctness authority. Build musí fungovať aj bez nej. Clean-room kontrola môže použiť:

```bash
docker buildx build --no-cache --progress=plain .
```

No-cache build dokazuje, že instruction cache nebola potrebná. Neodstraňuje network mutability, mutable base tags ani nedeklarované package mirrors.

## 7. Container writable layer má kratší lifecycle

Keď process v containere vytvorí súbor bez volume-u alebo bind mountu, zapisuje do container writable layer.

```bash
docker run --name layer-demo alpine:3.22 \
  sh -c 'echo important > /var/lib/important.txt && sleep 300'
```

Súbor možno prečítať:

```bash
docker exec layer-demo cat /var/lib/important.txt
```

Po odstránení containeru:

```bash
docker rm -f layer-demo
```

writable layer zanikne. Nový container z rovnakého image-u začne z čistého image filesystemu.

To je správne správanie. Container instance nie je implicitný persistentný data owner. Business dáta patria do volume-u, databázy, object storage alebo iného explicitného state systému.

## 8. Volume zakryje image path

Mount sa aplikuje nad výsledný image filesystem view. Ak image obsahuje súbor v path-e a runtime na rovnaký path pripojí volume, mount zakryje pôvodný obsah.

Image môže obsahovať:

```text
/var/lib/atlas-payments/default.json
```

Runtime potom mountne prázdny volume:

```bash
docker run --rm \
  --mount type=volume,source=payments-data,target=/var/lib/atlas-payments \
  IMAGE
```

Z pohľadu procesu je path obsahom volume-u. Súbor z image layer je stále v image-i, ale v danom mount namespace nie je viditeľný.

To vysvetľuje incidenty, pri ktorých „file existuje v image inspect alebo exporte, ale aplikácia ho nevidí“. Problém nemusí byť v build-e; runtime mount ho zakryl. `docker inspect` a `.Mounts` sú preto rovnako dôležité ako image filesystem kontrola.

## 9. Export containeru a save image-u nie sú to isté

`docker export` vytvorí tar výsledného container filesystem view-u. Nezachová image history, config ani layer graph ako image artifact.

```bash
container_id="$(docker create IMAGE)"
docker export "$container_id" > rootfs.tar
docker rm "$container_id"
```

`docker save` naopak exportuje image repository data a layers pre neskorší `docker load`:

```bash
docker save IMAGE > image.tar
```

Tieto operácie majú rozdielny účel. Exportovaný rootfs nie je plnohodnotná náhrada pôvodného OCI image graphu. Import rootfs vytvorí nový image bez pôvodnej history a configu, pokiaľ sa metadata znovu nedodajú.

## 10. Disková spotreba nie je iba súčet tagov

Docker host môže ukladať compressed registry blobs, unpacked snapshots, build cache, container writable layers a volumes. Tag removal nemusí okamžite uvoľniť disk, ak content stále referencuje iný tag, container alebo build cache.

Prehľad:

```bash
docker system df -v
```

Príkaz pomáha rozlíšiť images, containers, local volumes a build cache. Pred `prune` operáciou však treba vedieť, ktoré resources sú skutočne nepoužívané a či cache alebo volume nie je súčasťou recovery alebo active build flowu.

```bash
docker image prune
docker builder prune
docker volume prune
```

Každý príkaz má inú destructive boundary. Volume prune môže odstrániť dáta, ktoré nepatria žiadnemu aktuálnemu containeru, ale stále sú potrebné pre budúci restart alebo manuálnu recovery.

## 11. Incident: image sa zmenšil iba na papieri

Atlas mal image s veľkým build toolchainom. Dockerfile ho nainštaloval, skompiloval aplikáciu a v neskoršom kroku package manager files odstránil.

```dockerfile
RUN apk add build-base
RUN make build
RUN apk del build-base
```

Výsledný filesystem už toolchain neukazoval, ale skoršie layers ho stále obsahovali. Image pull bol veľký a scanner naďalej nachádzal packages zo starších layers podľa scanner modelu.

Trvalá oprava použila multi-stage build:

```dockerfile
FROM golang:1.25-alpine AS build
WORKDIR /src
COPY . .
RUN go build -o /out/payments-api ./cmd/payments-api

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/payments-api /usr/local/bin/payments-api
ENTRYPOINT ["/usr/local/bin/payments-api"]
```

Build toolchain ostal v build stage image graphu, ale nebol parentom final runtime filesystemu. Final image dostal iba binary a potrebné runtime artifacts.

## 12. Incident: 20 GB dát zostalo v odstránenom containeri

Export worker ukladal dočasné archívy do writable layer. Container bol zastavený, ale nie odstránený. Dashboard ukazoval nulový application traffic, no host disk zostal takmer plný.

```bash
docker ps -a --size
docker system df -v
```

ukázali veľkú writable layer zastaveného containeru. Tím pôvodne skúšal mazať image tags, čo neuvoľnilo relevantné miesto. Skutočný owner dát bol container object.

Recovery zachovala potrebné archívy, odstránila starý container a presunula temporary export path do bounded tmpfs alebo explicitného volume-u s retention policy. Prevencia nebola „pravidelne spusti prune“, ale zadefinovať, kam workload zapisuje a aký lifecycle má každý path.

## 13. Ako analyzovať nečakanú filesystem zmenu

Keď file v containere chýba alebo má inú verziu, postupuj od image-u k runtime-u:

```bash
docker image inspect IMAGE
docker image history --no-trunc IMAGE
container_id="$(docker create IMAGE)"
docker export "$container_id" | tar -tf - | grep PATH
docker rm "$container_id"
docker inspect RUNNING_CONTAINER | jq '.[0].Mounts'
```

Najprv over, či file patrí final image filesystemu. Potom skontroluj, či runtime mount path nezakrýva. Nakoniec porovnaj writable layer a running process view. Pri live incidente zachovaj container inspect a filesystem evidence pred odstránením alebo recreate operáciou.

## Čo si z kapitoly odniesť

Image layers sú ordered filesystem changesets. Výsledný root filesystem je merged view, nie jedna fyzická kópia. Containers zdieľajú read-only layers a každý dostáva vlastnú writable layer. Prvý zápis do existujúceho file-u môže vyvolať copy-up.

Odstránenie súboru v neskoršej layer nevymaže bytes zo skoršej layer. Container writable layer má lifecycle container objectu a nie je persistentný business data store. Mount môže zakryť image content. Pri veľkosti, secrets, cache alebo chýbajúcom file-i treba analyzovať celý layer a mount model, nie iba výsledný adresár v jednom running containere.

## Primárne zdroje

- [Docker storage drivers](https://docs.docker.com/engine/storage/drivers/)
- [Images and layers](https://docs.docker.com/get-started/docker-concepts/building-images/understanding-image-layers/)
- [Dockerfile best practices](https://docs.docker.com/build/building/best-practices/)
- [Build secrets](https://docs.docker.com/build/building/secrets/)
- [Docker system df](https://docs.docker.com/reference/cli/docker/system/df/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OCI image a runtime standards](oci-image-runtime-standards.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Registries →](registries.md)
<!-- KNOWLEDGE-NAVIGATION:END -->