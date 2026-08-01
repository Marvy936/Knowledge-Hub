# Build context a layer cache

Dockerfile nemá automaticky prístup k celému host filesystemu. Builder dostane explicitný build context a z neho vytvorí inventory vstupov, ktoré môžu používať `COPY`, `ADD` a ďalšie build operácie. `.dockerignore` tento inventory zúži ešte pred tým, než sa context odošle builderu.

Build cache potom nerozhoduje podľa jednoduchého pravidla „riadok Dockerfile-u sa nezmenil“. Cache key môže zahŕňať instruction, parent result, files a metadata z contextu, build arguments, mounts, platformu a frontend semantics. Keď sa niektorý relevantný input zmení, daný graph node a jeho descendants sa musia znovu vykonať.

Budeme sledovať build `payments-api`, pri ktorom chceme dve vlastnosti: zmena `main.go` nemá zbytočne sťahovať všetky dependencies a clean build bez cache musí vytvoriť rovnaký funkčný contract ako warm build.

## 1. Posledný argument build príkazu je context

Príkaz:

```bash
docker buildx build -f Dockerfile .
```

používa `.` ako build context root. Dockerfile môže byť v inom path-e, ale `COPY` source paths sa stále interpretujú voči context rootu.

Predstavme si repository:

```text
atlas-payments/
├── Dockerfile
├── go.mod
├── go.sum
├── cmd/
│   └── payments-api/
│       └── main.go
└── docs/
    └── architecture.pdf
```

Build z repository rootu:

```bash
docker buildx build -f Dockerfile .
```

umožní `COPY go.mod ./` a `COPY cmd ./cmd`. Build z `cmd/payments-api` contextu by `go.mod` nevidel, aj keby Dockerfile path smeroval na root Dockerfile.

```bash
docker buildx build \
  -f ../../Dockerfile \
  ./cmd/payments-api
```

Dockerfile location a context root sú dve rozdielne identity.

## 2. Prečo sa context odosiela builderu

Pri local builderi sa rozdiel nemusí javiť dôležitý. Pri `docker-container`, remote alebo cloud builderi však builder beží v inom procese alebo na inom hoste. Potrebuje dostať explicitný set files.

```text
client filesystem
→ context inventory
→ ignore rules
→ transfer alebo content resolution
→ builder
→ COPY/ADD operations
```

Veľký context spomaľuje build a rozširuje trust boundary. Ak repository obsahuje `.git`, test data, logs, local secrets alebo veľké artifacts, builder ich môže dostať aj vtedy, keď ich Dockerfile nikdy nekopíruje.

Build progress často ukáže context transfer:

```bash
docker buildx build --progress=plain .
```

Nečakane veľká hodnota pri `transferring context` je signál, že `.dockerignore` alebo context root nie sú správne navrhnuté.

## 3. `.dockerignore` je input filter

Príklad:

```dockerignore
.git
.env
.env.*
!.env.example
coverage/
dist/
tmp/
*.log
*.pem
*.key
compose.override.yaml
```

`.dockerignore` znižuje context, zabraňuje náhodnému `COPY . .` vyzdvihnutiu local files a znižuje cache invalidation spôsobenú nerelevantnými zmenami.

Nie je to plná security boundary. Dockerfile a build program stále môžu pristupovať na sieť, čítať secret mounts alebo generovať citlivý output. Ignore file iba určuje, ktoré primary context files sa builderu sprístupnia.

Negation rule:

```dockerignore
.env.*
!.env.example
```

najprv vylúči environment files a potom vráti example file. Poradie patterns je významové.

## 4. Over, čo je v contexte

Pri citlivom build-e je užitočné vytvoriť explicitný inventory ešte pred Docker buildom:

```bash
find . -type f \
  -not -path './.git/*' \
  -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  > evidence/source-files.sha256
```

Tento shell inventory nemusí presne reprodukovať `.dockerignore` semantics, ale pomáha zachovať source evidence. Presnejší audit môže používať BuildKit metadata alebo nástroj, ktorý aplikuje rovnaký ignore parser.

Minimálne skontroluj, že context neobsahuje secrets:

```bash
git ls-files -co --exclude-standard \
  | grep -E '(\.pem$|\.key$|^\.env$)' \
  && { echo 'sensitive file candidate found'; exit 1; } \
  || true
```

Taká kontrola je heuristic. Secret môže mať iný názov alebo byť vložený priamo v source file-i.

## 5. `COPY . .` je pohodlné, ale široké

Jednoduchý Dockerfile často používa:

```dockerfile
COPY . .
```

Tým sa všetky neignorované context files stanú inputom jedného graph node-u. Zmena README, test reportu alebo local configu môže invalidovať ďalšie build kroky. Navyše je ťažšie z review zistiť, čo final stage skutočne potrebuje.

Pre `payments-api` je čitateľnejšie:

```dockerfile
COPY go.mod go.sum ./
RUN go mod download

COPY cmd ./cmd
```

Dependency metadata a source majú oddelené cache boundaries. Dokumentácia alebo Compose files sa do build stage-u vôbec nemusia kopírovať.

## 6. Cache key a parent chain

Každý build node závisí od parent resultu. Ak sa invaliduje skorý krok, všetky descendants musia byť prehodnotené.

```text
FROM base digest B
→ COPY go.mod/go.sum
→ RUN go mod download
→ COPY cmd
→ RUN go build
```

Zmena `main.go` invaliduje `COPY cmd` a `RUN go build`, ale dependency download môže zostať cached. Zmena `go.sum` invaliduje dependency download aj všetky nasledujúce steps. Zmena base digestu mení parent celého graphu.

Cache hit preto neznamená, že builder „preskočil kontrolu“. Znamená, že našiel result s cache key zodpovedajúcim relevantným inputs podľa konkrétneho frontend a BuildKit modelu.

## 7. File metadata a cache invalidation

Pri `COPY` cache rozhodnutí sa hodnotí content a vybrané metadata. Mtime nemusí mať rovnaký význam ako pri klasickom `make`, ale permissions, ownership alebo path inventory môžu výsledok ovplyvniť.

Ak build generuje files pred contextom, nondeterministic timestamps alebo order môžu meniť cache a artifact bytes. Reproducible build potrebuje stabilizovať generated inputs, archive ordering, timestamps a toolchain.

```bash
SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"
export SOURCE_DATE_EPOCH
```

Podpora `SOURCE_DATE_EPOCH` závisí od build nástrojov. Samotné nastavenie environment variable nezaručuje reproducibility.

## 8. Build arguments ako cache inputs

`ARG` použitý v `RUN` mení command environment a typicky aj cache key.

```dockerfile
ARG VERSION
RUN go build -ldflags="-X main.version=$VERSION" -o /out/payments-api ./cmd/payments-api
```

Build `VERSION=1.0.0` a `VERSION=1.0.1` majú vytvoriť odlišný binary a odlišný build result.

```bash
docker buildx build --build-arg VERSION=1.0.0 .
docker buildx build --build-arg VERSION=1.0.1 .
```

Argument, ktorý Dockerfile nepoužíva, nemusí invalidovať relevantný node. Preto build manifest má zachovať effective args aj spôsob, akým sa používajú.

Secrets nemajú byť bežné `ARG`, pretože môžu vstúpiť do cache key, history alebo logs.

## 9. Cache mount nie je image layer

BuildKit cache mount poskytne mutable cache directory počas `RUN`:

```dockerfile
RUN --mount=type=cache,target=/go/pkg/mod,sharing=locked \
    go mod download
```

Obsah cache mountu sa automaticky nepridá do output layer. Command musí skopírovať required artifacts do bežného stage filesystemu alebo ich znovu vytvoriť.

Cache môže byť prázdna, čiastočná alebo garbage-collected. Build nesmie byť správny iba vtedy, keď cache obsahuje hidden file z predchádzajúceho jobu.

Clean test:

```bash
docker buildx build \
  --no-cache \
  --target test \
  --output=type=cacheonly \
  --progress=plain \
  .
```

`--no-cache` obíde instruction cache, ale cache mounts môžu mať vlastné správanie podľa definície. Pre úplný clean-room test použi nový builder alebo oddelený cache namespace.

## 10. External cache

CI môže exportovať a importovať cache z registry alebo iného backendu:

```bash
docker buildx build \
  --cache-from type=registry,ref=registry.example.com/atlas/payments-api:buildcache \
  --cache-to type=registry,ref=registry.example.com/atlas/payments-api:buildcache,mode=max \
  --push \
  -t registry.example.com/atlas/payments-api:1.0.0 \
  .
```

External cache zrýchľuje ephemeral runners. Zároveň je supply-chain input. Untrusted branch nemá mať write access do cache, ktorú protected release build bez overenia importuje.

Cache reference by mala byť rozdelená podľa trust domainu, platformy a prípadne dependency generation. Jeden shared mutable cache tag pre všetky branches vytvára poisoning a race boundary.

## 11. Cache poisoning

Predstavme si, že fork pipeline môže pushovať do `payments-api:buildcache`. Útočník vytvorí cache result pre node, ktorý sa v release build-e javí ako zhodný. Ak cache identity alebo BuildKit trust model dovolí reuse, release môže použiť output vytvorený nedôveryhodným jobom.

Moderný BuildKit content-addressing a cache metadata poskytujú silné integrity vlastnosti, ale trust v producerovi cache stále záleží. Cache môže obsahovať správne hashované škodlivé outputy.

Bezpečný model:

```text
untrusted PR cache
→ read/write iba untrusted namespace

protected branch cache
→ write protected identity

release cache
→ import iba schválené namespaces alebo clean build gate
```

Najcitlivejší artifact možno pred publication buildnúť bez untrusted external cache a porovnať contract outcome.

## 12. Git context

Buildx môže používať Git URL alebo repository context. Builder potom resolve-ne commit a vytvorí context bez klasického local directory transferu.

```bash
docker buildx build \
  'https://github.com/example/atlas-payments.git#<commit-sha>'
```

Použitie immutable commit SHA je dôležitejšie než branch name. Branch sa môže posunúť medzi review a buildom.

Git context môže mať odlišné správanie pre `.git` directory a submodules. Build, ktorý potrebuje `git describe`, musí explicitne riešiť VCS metadata, namiesto predpokladu, že `.git` je v contexte.

Private Git access používa SSH alebo secret credentials a patrí do trusted build boundary.

## 13. Named contexts

Named contexts umožňujú pridať ďalšie deklarované sources bez rozšírenia primary contextu.

```bash
docker buildx build \
  --build-context docs=./docs \
  --build-context runtime_base=docker-image://alpine:3.22@sha256:<digest> \
  .
```

Dockerfile môže named context použiť podobne ako stage podľa podporovanej syntax:

```dockerfile
COPY --from=docs / /usr/share/doc/atlas/
```

Named context musí mať vlastnú identity a trust. Remote Git context, image context a local directory majú odlišné mutation a authentication vlastnosti.

## 14. Multi-platform cache

Platform-specific build môže mať spoločné a odlišné nodes. Source copy alebo dependency metadata môže byť platform-neutral, zatiaľ čo compiler output musí byť viazaný na `TARGETOS` a `TARGETARCH`.

```dockerfile
ARG TARGETOS
ARG TARGETARCH
RUN GOOS="$TARGETOS" GOARCH="$TARGETARCH" \
    go build -o /out/payments-api ./cmd/payments-api
```

Ak build script ignoruje target arguments alebo cache key nezachytí platform-specific input, arm64 branch môže reuse-nuť amd64 artifact. Final native smoke test a binary inspection majú potvrdiť platformu.

```bash
file payments-api
```

Vo final minimal image-i možno binary analyzovať v samostatnom artifact alebo debug stage-i.

## 15. Diagnostika nečakaného cache hitu alebo missu

Plain progress zobrazí graph nodes a `CACHED` výsledky:

```bash
docker buildx build --progress=plain . 2>&1 | tee build.log
```

Pri nečakanom miss-e hľadaj prvý node, ktorý sa znovu vykonal. Skontroluj parent digest, context files, build args, frontend, platformu a cache import.

Pri podozrivom hit-e vykonaj clean build na novom builderi:

```bash
docker buildx create --name atlas-clean --driver docker-container --use
docker buildx inspect --bootstrap

docker buildx build \
  --builder atlas-clean \
  --no-cache \
  --progress=plain \
  --output type=local,dest=./clean-output \
  .
```

Output porovnaj s warm buildom podľa relevantného contractu alebo digestu. Bit-identická reproducibility môže vyžadovať ďalšie toolchain controls.

## 16. Incident: README zmena rebuildla celý image

Repository používalo:

```dockerfile
COPY . .
RUN go mod download
RUN go test ./...
RUN go build -o /out/payments-api ./cmd/payments-api
```

Každá zmena dokumentácie invalidovala broad `COPY`, takže dependency download, testy aj build sa vykonali znovu. CI trvala dvakrát dlhšie a developers začali test joby obchádzať.

Oprava zúžila context cez `.dockerignore` a rozdelila copy boundaries. Dependency files sa kopírovali pred source. Dokumentácia nebola build inputom. Build sa zrýchlil bez zníženia correctness.

## 17. Incident: warm cache skrývala chýbajúci generated step

Build stage očakával generated client v `/src/generated`. Starší CI job ho vytvoril v cache mount directory a nesprávny script ho skopíroval do outputu iba pri warm cache. Clean runner zlyhal.

```text
warm cache obsahuje generated client
→ build prejde
clean cache je prázdna
→ file chýba
```

Cache sa stala hidden correctness dependency.

Recovery pridala explicitný generation command zo source schema a output sa stal bežným stage artifactom. CI zaviedla pravidelný clean builder run a test, že generated output zodpovedá source-u.

## Čo si z kapitoly odniesť

Build context je explicitný input inventory, nie celý host filesystem. Context root a Dockerfile path sú rozdielne. `.dockerignore` znižuje transfer, accidental inclusion a nerelevantnú cache invalidation, ale nie je kompletná security boundary.

Cache reuse závisí od graph node-u, parent resultu a relevantných inputs. Cache mount je performance aid, nie image layer ani source of truth. External cache je supply-chain input a musí byť oddelená podľa trustu a platformy. Build má prejsť aj v clean prostredí a nečakaný cache hit alebo miss sa diagnostikuje od prvého odlišného graph node-u.

## Primárne zdroje

- [Build context](https://docs.docker.com/build/building/context/)
- [`.dockerignore`](https://docs.docker.com/build/building/context/#dockerignore-files)
- [Build cache](https://docs.docker.com/build/cache/)
- [Cache optimization](https://docs.docker.com/build/cache/optimize/)
- [Cache storage backends](https://docs.docker.com/build/cache/backends/)
- [Named contexts](https://docs.docker.com/build/building/context/#named-contexts)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Dockerfile](dockerfile.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Multi-stage builds →](multi-stage-builds.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
