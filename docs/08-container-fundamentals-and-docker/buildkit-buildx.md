# BuildKit a Buildx

BuildKit je build execution engine. Dockerfile alebo iný frontend preloží na dependency graph, vyhodnotí jeho vstupy, vykoná potrebné nodes, použije alebo vytvorí cache a výsledok exportuje ako image, OCI layout, local files alebo iný podporovaný output. Buildx je Docker CLI vrstva, cez ktorú vyberáme builder instance, driver, nodes, platformy, cache backends, secrets a exportery.

Rozdiel oproti starému lineárnemu mentálnemu modelu je zásadný. BuildKit nečíta Dockerfile iba ako zoznam príkazov, ktoré musia vždy prebehnúť zhora nadol. Vytvorí graph a vykoná iba vetvy potrebné pre zvolený target. Nezávislé nodes môže vykonávať paralelne. Cached result môže reuse-nuť podľa identity vstupov. Final image preto vzniká z konkrétnej kombinácie source contextu, Dockerfile frontendu, buildera, platformy, build arguments, cache a exporter semantics.

Budeme sledovať release `payments-api`, ktorý má podporovať `linux/amd64` a `linux/arm64`. Unit test target sa vykoná samostatne, final image sa publikuje do registry spolu s provenance a SBOM a po pushi sa read-backne image index a platform inventory.

## 1. Builder nie je iba lokálny Docker daemon

Buildx pracuje s builder instances. Aktuálny inventory zobrazíš:

```bash
docker buildx ls
```

Detail vybraného buildera:

```bash
docker buildx inspect --bootstrap
```

Výstup ukáže driver, nodes, BuildKit verziu, status a podporované platformy. To sú build execution inputs. Rovnaký Dockerfile môže na inom builderi použiť inú BuildKit verziu, inú platform capacity, odlišnú cache a odlišný network alebo secret trust domain.

Pre release vytvoríme pomenovaný builder:

```bash
docker buildx create \
  --name atlas-release \
  --driver docker-container \
  --use

docker buildx inspect atlas-release --bootstrap
```

Driver `docker-container` spustí BuildKit v samostatnom containeri. Výsledok sa po build-e automaticky nemusí objaviť v local Docker image store-i; to závisí od zvoleného outputu. Preto je dôležité explicitne používať `--load`, `--push` alebo iný exporter.

## 2. Drivers menia execution boundary

Buildx podporuje viac builder modelov. `docker` driver používa BuildKit integrovaný v Docker Engine-i. Je jednoduchý pre local buildy, ale má odlišné možnosti konfigurácie a exporterov. `docker-container` používa samostatný BuildKit container a je bežný pre CI alebo advanced local buildy. `kubernetes` driver rozloží builder nodes do clusteru. `remote` sa pripája k existujúcemu BuildKit endpointu.

Nejde iba o výkon. Driver určuje, kde sa nachádza cache, kam sa pripájajú secrets, aký filesystem a network builder vidí a kto má oprávnenie meniť jeho konfiguráciu.

```text
local developer builder
→ pohodlie a rýchla spätná väzba

untrusted pull-request builder
→ bez production credentials a bez release cache write

protected release builder
→ pinned configuration, short-lived registry identity a audit
```

Jeden shared privileged builder pre untrusted pull requests aj production release zväčšuje supply-chain blast radius.

## 3. Frontend preloží Dockerfile na build graph

Directive:

```dockerfile
# syntax=docker/dockerfile:1
```

určuje Dockerfile frontend. Frontend parse-ne source a vytvorí low-level build graph, ktorý BuildKit vykoná. Frontend verzia preto patrí k build identity. Nová verzia môže priniesť nové instructions alebo zmeniť validáciu.

Zjednodušený graph `payments-api`:

```text
resolve build base
→ copy go.mod a go.sum
→ download dependencies
→ copy source
├── run unit tests
└── compile amd64 alebo arm64 binary
    → resolve runtime base
    → copy binary
    → export image manifest a layers
```

BuildKit môže dependency download vykonať raz a výsledok reuse-nuť pre test aj build branch. Test branch sa však nevykoná pri runtime targete, ak na nej runtime graph nezávisí.

Plain progress ukáže nodes:

```bash
docker buildx build \
  --builder atlas-release \
  --target test \
  --progress=plain \
  --output=type=cacheonly \
  .
```

Výstup je vhodný pre CI evidence, pretože ukáže, ktoré operations boli cached a ktoré sa vykonali. Log však stále potrebuje väzbu na source, frontend, builder a platform.

## 4. Test target a final target sú samostatné verdicts

Dockerfile môže mať:

```dockerfile
FROM source AS test
RUN go test ./...

FROM source AS build
RUN go build -o /out/payments-api ./cmd/payments-api

FROM runtime-base AS runtime
COPY --from=build /out/payments-api /usr/local/bin/payments-api
```

Runtime stage nemá dependency na `test`. CI preto vykoná test explicitne:

```bash
docker buildx build \
  --builder atlas-release \
  --target test \
  --platform linux/amd64 \
  --progress=plain \
  --output=type=cacheonly \
  .
```

A final local build samostatne:

```bash
docker buildx build \
  --builder atlas-release \
  --target runtime \
  --platform linux/amd64 \
  --build-arg VERSION=1.0.0 \
  --build-arg VCS_REF="$(git rev-parse --short=12 HEAD)" \
  --tag atlas/payments-api:1.0.0 \
  --load \
  .
```

PASS test targetu preukazuje vykonanie konkrétneho test graphu. Final build vytvorí image z runtime graphu. Pipeline musí zachovať, že oba používali rovnaký source SHA, Dockerfile content, bases, args a relevantný builder trust domain.

## 5. `--load` a local image store

`--load` je skratka pre Docker image exporter do local Engine image store-u a je vhodná najmä pre single-platform image:

```bash
docker buildx build \
  --platform linux/amd64 \
  --load \
  -t atlas/payments-api:1.0.0 \
  .
```

Po úspechu:

```bash
docker image inspect atlas/payments-api:1.0.0
```

Local tag je mutable a `RepoDigests` môže byť prázdne, pokiaľ image nebol pushnutý alebo pullnutý pod registry reference. `--load` nie je multi-platform registry publication model. Klasický local Docker image store nemusí reprezentovať celý multi-platform index ako jeden runnable local object.

## 6. `--push` a registry exporter

Release build používa registry exporter:

```bash
docker buildx build \
  --builder atlas-release \
  --target runtime \
  --platform linux/amd64,linux/arm64 \
  --build-arg VERSION=1.0.0 \
  --build-arg VCS_REF="$(git rev-parse --short=12 HEAD)" \
  --tag registry.example.com/atlas/payments-api:1.0.0 \
  --provenance=mode=max \
  --sbom=true \
  --push \
  .
```

BuildKit vytvorí platform branches, publikuje configs a layers, platform manifests a image index. `--push` je output operation; nevytvára automaticky production deployment.

Pri strate response môže publication outcome zostať unknown. Pred retry alebo rebuildom read-backni registry:

```bash
docker buildx imagetools inspect \
  registry.example.com/atlas/payments-api:1.0.0
```

Release manifest má uložiť observed index digest, nie iba tag.

## 7. Ďalšie exportery

Local exporter uloží filesystem output do directory:

```bash
docker buildx build \
  --target artifact \
  --output type=local,dest=./dist \
  .
```

Tar exporter vytvorí tar stream alebo file podľa invocation. OCI a Docker exporters vytvoria image layout alebo tar vhodný pre transport a import. `type=cacheonly` vykoná graph bez exportu bežného artifactu a je vhodný pre test target.

Exporter je súčasť build contractu. Rovnaký graph exportovaný ako local files a registry image nemá rovnakú metadata ani consumption cestu. Pipeline musí presne vedieť, ktorý output je release artifact.

## 8. Multi-platform: emulácia, native nodes a cross-compilation

BuildKit môže vytvárať viac platforiem troma hlavnými spôsobmi.

Emulácia používa binfmt a QEMU, takže foreign-architecture binaries sa vykonávajú na inom host CPU. Je pohodlná, ale compiler-heavy build môže byť pomalý a emulácia nemusí odhaliť všetky native runtime rozdiely.

Native multi-node builder má amd64 a arm64 nodes. Každý platform branch môže bežať na natívnom hardvéri. To zvyšuje operational complexity, ale poskytuje reprezentatívnejšie execution prostredie.

Cross-compilation spustí compiler na `BUILDPLATFORM` a vytvorí output pre `TARGETOS` a `TARGETARCH`:

```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.25-alpine AS build
ARG TARGETOS
ARG TARGETARCH

RUN CGO_ENABLED=0 \
    GOOS="$TARGETOS" \
    GOARCH="$TARGETARCH" \
    go build -o /out/payments-api ./cmd/payments-api
```

Pri CGO alebo native dependencies môže byť potrebný cross toolchain alebo native node. Platform label v manifest-e sa musí zhodovať s binary a runtime libraries.

## 9. Builder node inventory

```bash
docker buildx inspect atlas-release --bootstrap
```

ukáže nodes a platforms. Pri multi-node builderi zaznamenaj, ktorý node vykonal ktorú platform branch. Nodes môžu mať odlišné kernel, BuildKit, network, credentials alebo cache state.

Build, ktorý prešiel na amd64 node a zlyhal na arm64, nemusí mať application source defect. Môže ísť o platform-specific dependency, node drift alebo cache contamination.

Native smoke test nad exact platform manifestom je silnejší než iba index metadata:

```bash
docker pull --platform linux/arm64 \
  registry.example.com/atlas/payments-api@sha256:<index-digest>
```

Na amd64 hoste pull neznamená native execution. Testovanie musí zodpovedať zvolenej strategy.

## 10. Cache export a import

Registry cache:

```bash
docker buildx build \
  --cache-from type=registry,ref=registry.example.com/atlas/payments-api:buildcache \
  --cache-to type=registry,ref=registry.example.com/atlas/payments-api:buildcache,mode=max \
  --push \
  -t registry.example.com/atlas/payments-api:1.0.0 \
  .
```

`mode=max` exportuje širší graph inventory než minimum potrebné pre final image. Cache môže obsahovať výsledky intermediate stages.

Cache zrýchľuje build, ale producer trust je podstatný. Untrusted branches nemajú zapisovať do protected release cache. Platform-specific cache keys a namespaces znižujú riziko cross-platform reuse nesprávneho outputu.

Pri pochybnosti vytvor nový clean builder a build bez external cache. Clean build je diagnostický a assurance gate, nie každodenná náhrada dobre navrhnutej cache.

## 11. Secret a SSH mounts

Build secret:

```bash
docker buildx build \
  --secret id=npmrc,src="$HOME/.npmrc" \
  .
```

Dockerfile:

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci
```

SSH forwarding:

```bash
docker buildx build --ssh default .
```

Dockerfile:

```dockerfile
RUN --mount=type=ssh \
    git clone git@github.com:example/private-module.git
```

Tieto mounts sú dostupné iba pre konkrétny `RUN` a nemajú sa automaticky stať image contentom. Build program ich však môže zneužiť. Secrets a SSH agent sa poskytujú iba trusted source-u a builderu s úzkym network a log policy.

## 12. Network modes a entitlements

Build operations môžu potrebovať network access. BuildKit podporuje network modes a vybrané entitlements. Host networking alebo security-insecure entitlement výrazne mení build isolation.

Broad entitlement nemá byť default pre všetky jobs. Ak build potrebuje package registry, povoľ úzky egress a pinned repository. Ak test potrebuje service dependency, použi explicitné test environment namiesto host network accessu bez hraníc.

Build network je supply-chain boundary. Remote package server, DNS a proxy môžu zmeniť output aj pri rovnakom Git source-u.

## 13. Provenance

Provenance attestation opisuje, ako artifact vznikol: builder identity, source a ďalšie build metadata podľa mode a implementation.

```bash
docker buildx build \
  --provenance=mode=max \
  --push \
  -t registry.example.com/atlas/payments-api:1.0.0 \
  .
```

Provenance nie je automaticky dôveryhodná iba preto, že existuje. Producer musí byť trusted, subject digest sa musí zhodovať s published artifactom a policy musí overiť relevantné fields.

Citlivé build arguments alebo environment nemajú byť bez rozmyslu zahrnuté do metadata. Release pipeline musí rozumieť, čo konkrétny provenance mode publikuje.

## 14. SBOM

```bash
docker buildx build \
  --sbom=true \
  --push \
  -t registry.example.com/atlas/payments-api:1.0.0 \
  .
```

SBOM attestation inventarizuje components podľa scanner implementation. Pri multi-platform image môžu mať platform branches odlišné packages alebo binary dependencies. SBOM musí byť korelovaná s platform manifestom alebo správnym subject graphom.

SBOM nie je vulnerability verdict. Je to inventory input pre ďalšie analysis. Neúplný inventory, statically linked components alebo generated assets môžu vyžadovať doplnkové scanners.

## 15. Build metadata file

Buildx môže zapísať metadata o výsledku:

```bash
docker buildx build \
  --metadata-file evidence/build-metadata.json \
  --push \
  -t registry.example.com/atlas/payments-api:1.0.0 \
  .
```

Obsah závisí od exporter a Buildx verzie. Metadata file je useful hand-off medzi jobs, ale musí byť validovaný a viazaný na trusted producer. Downstream job nemá slepo veriť ručne vytvorenému JSON.

## 16. Build history a debugging

Plain progress je najprenosnejší diagnostic output:

```bash
docker buildx build --progress=plain . 2>&1 | tee build.log
```

Buildx a Docker Desktop môžu poskytovať ďalšie build history alebo inspection UI podľa verzie. Pri CI zachovaj logs, source SHA, Dockerfile checksum, builder inspect output, args, platformy, cache refs a exporter metadata.

Pri failure hľadaj prvý graph node s chybou. Neskoršie `failed to solve` je summary, nie root cause. Network timeout v dependency node, compiler error a exporter authorization failure sú tri odlišné vrstvy.

## 17. Incident: arm64 manifest obsahoval amd64 binary

Build script používal `GOARCH=amd64` hardcoded a ignoroval `TARGETARCH`. Buildx vytvoril dva platform manifests podľa requested platforms, ale oba obsahovali amd64 binary. Registry graph a digests boli validné.

Arm64 runtime skončil `exec format error`.

Oprava použila automatic platform args, pridala artifact inspection v každej branch a native arm64 smoke test. Pipeline viazala test report na platform manifest digest. Starý index zostal immutable ako incident evidence a nový release dostal nový index digest.

## 18. Incident: release použil cache z pull requestu

Protected release builder importoval shared registry cache, do ktorej mohli zapisovať fork jobs. Škodlivý pull request vytvoril cached generated asset, ktorý sa pri release graph node-e reuse-nul podľa zhodných inputs. Content integrity bola správna; producer bol nedôveryhodný.

Containment zablokoval publication a cache write credentials. Cache namespaces sa rozdelili podľa trust domainu. Release build importoval iba protected cache a pravidelne prechádzal clean-room buildom.

## 19. Od build requestu po overený digest

Referenčný tok:

```bash
source_sha="$(git rev-parse HEAD)"
image_ref="registry.example.com/atlas/payments-api:1.0.0"

docker buildx inspect atlas-release --bootstrap \
  > evidence/builder.txt

sha256sum Dockerfile .dockerignore go.mod go.sum \
  > evidence/build-inputs.sha256

docker buildx build \
  --builder atlas-release \
  --target test \
  --platform linux/amd64 \
  --progress=plain \
  --output=type=cacheonly \
  . 2>&1 | tee evidence/test.log

docker buildx build \
  --builder atlas-release \
  --target runtime \
  --platform linux/amd64,linux/arm64 \
  --build-arg VERSION=1.0.0 \
  --build-arg VCS_REF="$source_sha" \
  --provenance=mode=max \
  --sbom=true \
  --metadata-file evidence/build-metadata.json \
  --tag "$image_ref" \
  --push \
  .

docker buildx imagetools inspect "$image_ref"
docker buildx imagetools inspect "$image_ref" --raw \
  > evidence/image-index.json
```

Tento flow zachová viac evidence, ale acceptance stále potrebuje per-platform runtime test, scan/policy a deployment correlation.

## Čo si z kapitoly odniesť

BuildKit vykonáva dependency graph a Buildx spravuje builder instances, drivers, nodes, platforms, cache a outputs. Builder a frontend sú súčasť build identity. `--load`, `--push`, local a OCI exporters vytvárajú rozdielne outputs.

Multi-platform build môže používať emuláciu, native nodes alebo cross-compilation. Platform metadata musí zodpovedať skutočnému binary a libraries. Cache je performance a supply-chain input, nie source of truth. Secrets a SSH mounts sa poskytujú iba trusted build programu. Provenance a SBOM musia patriť published digestu a byť samostatne validované. Build končí až registry read-backom a runtime evidence, nie iba hláškou `exporting to image done`.

## Primárne zdroje

- [BuildKit](https://docs.docker.com/build/buildkit/)
- [Buildx](https://docs.docker.com/build/buildx/)
- [`docker buildx build`](https://docs.docker.com/reference/cli/docker/buildx/build/)
- [Build drivers](https://docs.docker.com/build/builders/drivers/)
- [Multi-platform builds](https://docs.docker.com/build/building/multi-platform/)
- [Cache backends](https://docs.docker.com/build/cache/backends/)
- [Build secrets](https://docs.docker.com/build/building/secrets/)
- [Attestations](https://docs.docker.com/build/metadata/attestations/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Docker Compose](docker-compose.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Praktický Docker projekt od prázdneho adresára po overený Compose runtime →](docker-practical-walkthrough.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
