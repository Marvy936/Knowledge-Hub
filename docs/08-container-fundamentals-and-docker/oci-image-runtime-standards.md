# OCI image a runtime standards

Open Container Initiative nevytvára jeden container engine ani jeden príkazový riadok. Definuje spoločné formáty a rozhrania, vďaka ktorým môže image vytvorený jedným build nástrojom uložiť registry, stiahnuť iný runtime a spustiť low-level OCI runtime. Najdôležitejšie je pochopiť, že „OCI image“ a „OCI runtime“ označujú dve rozdielne vrstvy.

Image Specification opisuje, ako sa aplikačný filesystem a jeho metadata ukladajú do content-addressed graphu. Distribution Specification opisuje, ako klient komunikuje s registry pri pushi a pulle manifestov a blobs. Runtime Specification opisuje bundle, z ktorého low-level runtime vytvorí a spustí proces. Medzi image-om v registry a bežiacim procesom preto prebieha niekoľko transformácií.

Budeme sledovať `payments-api` od publikovaného image reference až po proces. Tým sa ukáže, kde vzniká index digest, platform manifest, image config, layers, runtime bundle a konečná process configuration.

## 1. Jeden reference, viac objektov

Produkcia môže používať reference:

```text
registry.example.com/atlas/payments-api@sha256:<index-digest>
```

Na prvý pohľad ide o jeden image. V registry však digest môže označovať image index, ktorý odkazuje na viac platform-specific manifestov:

```text
image index
├── linux/amd64 manifest
└── linux/arm64 manifest
```

Každý platform manifest následne odkazuje na image config a na ordered zoznam filesystem layers:

```text
platform manifest
├── config descriptor → image config blob
├── layer descriptor 1 → compressed layer blob
├── layer descriptor 2 → compressed layer blob
└── layer descriptor 3 → compressed layer blob
```

Descriptor obsahuje najmä media type, digest a size. Digest identifikuje presné bytes cieľového objektu. Registry alebo runtime môže objekt stiahnuť a vypočítať jeho hash. Ak sa bytes nezhodujú s descriptor digestom, objekt nie je ten, ktorý manifest deklaroval.

## 2. Content-addressing a význam digestu

Digest je content identity, nie ľudská verzia. Pri SHA-256 vyzerá napríklad takto:

```text
sha256:9dd27c99f4f78d9d8b7c...
```

Zmena jedného bajtu vytvorí iný digest. Vďaka tomu môže registry deduplikovať blobs, klient overiť integritu a release manifest odkazovať na immutable content.

Tag `1.4.2` funguje inak. Je to pomenovaný pointer v repository. Registry policy môže jeho prepísanie zakázať, ale samotný tag formát nie je content-addressed. Preto:

```text
payments-api:1.4.2
```

môže v jednom čase ukazovať na index digest `D1` a po prepísaní na `D2`. Reference s `@sha256:...` ukazuje na konkrétny manifest alebo index.

Digest však nepreukazuje bezpečnosť ani funkčnosť obsahu. Preukazuje iba identitu bytes. Zraniteľný, chybný alebo nesprávne nakonfigurovaný image má rovnako stabilný digest ako dobrý image.

## 3. Image index a platform selection

Multi-platform image používa image index, v Docker terminológii často nazývaný aj manifest list. Index obsahuje descriptors pre dostupné platform manifests. Descriptor môže niesť platform metadata, napríklad OS, architecture a variant.

Zjednodušený index:

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.index.v1+json",
  "manifests": [
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "digest": "sha256:<amd64-manifest>",
      "size": 1234,
      "platform": {
        "os": "linux",
        "architecture": "amd64"
      }
    },
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "digest": "sha256:<arm64-manifest>",
      "size": 1240,
      "platform": {
        "os": "linux",
        "architecture": "arm64",
        "variant": "v8"
      }
    }
  ]
}
```

Keď Linux amd64 node pullne index, runtime vyberie amd64 manifest. Arm64 node vyberie arm64 manifest. Oba nodes môžu používať rovnaký index digest, ale skutočne spustené platform manifests, configs a layers sú odlišné.

Preto musí multi-platform release evidence rozlišovať index a platform artifacts. Scan iba amd64 manifestu nepreukazuje stav arm64 image-u. Smoke test pod emuláciou nemusí nahradiť native runtime test, ak aplikácia používa architecture-specific libraries alebo kernel features.

Registry read-back možno vykonať cez Buildx:

```bash
docker buildx imagetools inspect \
  registry.example.com/atlas/payments-api:1.4.2
```

Raw index:

```bash
docker buildx imagetools inspect \
  registry.example.com/atlas/payments-api:1.4.2 \
  --raw > image-index.json
```

A platform inventory:

```bash
jq -r '.manifests[] | [.platform.os, .platform.architecture, .digest] | @tsv' \
  image-index.json
```

Tento výstup dokazuje registry-visible index generation v čase read-backu. Ak production reference používa mutable tag, neskôr môže tag ukazovať na iný index.

## 4. Platform manifest

Platform manifest spája image config s filesystem layers. Zjednodušená podoba:

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "config": {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "digest": "sha256:<config-digest>",
    "size": 1920
  },
  "layers": [
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "digest": "sha256:<layer-1>",
      "size": 3120000
    },
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "digest": "sha256:<layer-2>",
      "size": 8200000
    }
  ]
}
```

Poradie layers je významové. Runtime alebo snapshotter ich aplikuje od prvého po posledný. Neskoršia layer môže pridať, zmeniť alebo odstrániť path vytvorený skoršou layer.

Manifest nie je filesystem sám. Je to graph metadata. Ak chýba blob, descriptor ukazuje na neexistujúci content alebo registry nemá oprávnenie blob poskytnúť, pull zlyhá aj pri platnom JSON manifeste.

## 5. Image config

Image config obsahuje runtime defaults a root filesystem metadata. Môže niesť environment variables, usera, working directory, entrypoint, command, exposed ports, labels a históriu build krokov.

```json
{
  "architecture": "amd64",
  "os": "linux",
  "config": {
    "User": "65532:65532",
    "Env": [
      "LISTEN_ADDRESS=:8080",
      "LOG_LEVEL=info"
    ],
    "Entrypoint": [
      "/usr/local/bin/payments-api"
    ],
    "Cmd": [
      "serve"
    ],
    "WorkingDir": "/home/nonroot"
  },
  "rootfs": {
    "type": "layers",
    "diff_ids": [
      "sha256:<uncompressed-layer-1>",
      "sha256:<uncompressed-layer-2>"
    ]
  }
}
```

Manifest descriptors typicky identifikujú compressed blobs. `rootfs.diff_ids` identifikujú uncompressed filesystem changesets. Preto compressed layer digest a DiffID nemusia byť rovnaké.

Image config je default contract, nie konečný runtime verdict. Docker alebo Compose môže prepísať usera, command, environment a working directory. Mount môže zakryť path, ktorý je v image filesysteme. Security options, cgroup limity a network configuration sa do image configu bežne neukladajú; patria runtime create requestu.

## 6. Filesystem layers a whiteouts

Layer je tar archive filesystem changesetu. Nejde o kompletnú kópiu root filesystemu. Jedna layer môže pridať `/usr/local/bin/payments-api`, ďalšia pridať certificate bundle a ďalšia zmeniť configuration template.

Odstránenie súboru z predchádzajúcej layer sa reprezentuje whiteout záznamom. Staré bytes môžu stále existovať v skoršej layer, hoci výsledný merged filesystem path neukazuje. To je dôvod, prečo secret skopírovaný do image-u a odstránený v neskoršom `RUN` kroku nemusí byť skutočne odstránený z image history.

Bezpečný build preto nepoužíva tento model:

```dockerfile
COPY private-key.pem /tmp/private-key.pem
RUN sign-artifact /tmp/private-key.pem && rm /tmp/private-key.pem
```

Private key sa dostane do layer vytvorenej `COPY`. Neskoršie odstránenie iba zmení výsledný filesystem view. BuildKit secret mount drží secret mimo image layer:

```dockerfile
RUN --mount=type=secret,id=signing_key \
    sign-artifact /run/secrets/signing_key
```

Aj tu treba auditovať output build programu. Secret mount zabráni automatickému zahrnutiu secret file-u do layer, ale škodlivý script môže secret skopírovať do outputu alebo odoslať po sieti.

## 7. OCI image layout

OCI Image Specification definuje aj filesystem layout, v ktorom možno image graph uložiť mimo registry. Typická štruktúra:

```text
oci-layout
index.json
blobs/
└── sha256/
    ├── <index-or-manifest-content>
    ├── <config-content>
    └── <layer-content>
```

`oci-layout` deklaruje verziu layoutu. `index.json` je vstupný index do uložených artifacts. `blobs` obsahuje content-addressed objekty.

Takýto layout je užitočný pri air-gapped transporte, lokálnej analýze alebo interoperability testoch. Samotné skopírovanie adresára však ešte nepreukazuje, že všetky referencované blobs sú prítomné, že artifact bol podpísaný alebo že cieľový runtime podporuje deklarovanú platformu a media types.

## 8. Distribution Specification a registry komunikácia

Registry nie je iba webový adresár so súbormi. Implementuje API pre repository content. Klient typicky overí existenciu blobs, uploadne chýbajúce blobs a napokon publikuje manifest alebo index.

Zjednodušený push:

```text
resolve repository a authorization scope
→ over alebo uploadni config blob
→ over alebo uploadni layer blobs
→ PUT platform manifest
→ PUT image index alebo tag association
→ read-back digestu
```

Blobs sú content-addressed a možno ich deduplikovať. Tag mutation je samostatná repository operácia. Ak push request timeoutne po tom, čo registry mutation vykonala, výsledok je unknown. Blind retry nemusí poškodiť immutable blob content, ale môže zmeniť tag alebo vytvoriť nejasný release record.

Správna reakcia je read-back:

```bash
docker buildx imagetools inspect \
  registry.example.com/atlas/payments-api:1.4.2
```

A porovnanie observed digestu s digestom, ktorý release pipeline očakáva.

## 9. Runtime Specification a OCI bundle

Runtime Specification začína bližšie k procesu. Low-level runtime, napríklad `runc`, dostane bundle. Bundle typicky obsahuje `config.json` a root filesystem directory.

```text
bundle/
├── config.json
└── rootfs/
```

`config.json` opisuje proces a isolation nastavenia. Zjednodušený fragment:

```json
{
  "ociVersion": "1.2.0",
  "process": {
    "terminal": false,
    "user": {
      "uid": 65532,
      "gid": 65532
    },
    "args": [
      "/usr/local/bin/payments-api",
      "serve"
    ],
    "cwd": "/home/nonroot",
    "env": [
      "LISTEN_ADDRESS=:8080"
    ]
  },
  "root": {
    "path": "rootfs",
    "readonly": true
  },
  "linux": {
    "namespaces": [
      {"type": "pid"},
      {"type": "mount"},
      {"type": "network"}
    ]
  }
}
```

Toto nie je image config. Je to konkrétnejší runtime request. Vyššia vrstva, napríklad Docker Engine a containerd, musí image rozbaliť, pripraviť snapshot, spojiť image defaults s runtime overrides, pripojiť mounts a sieť a vytvoriť bundle alebo ekvivalentný low-level runtime input.

## 10. Docker Engine, containerd a `runc`

Pri Docker Engine lifecycle možno vrstvy zjednodušiť takto:

```text
Docker CLI
→ Docker Engine API a dockerd
→ image, network, volume a container object management
→ containerd
→ snapshot a runtime task lifecycle
→ runtime shim
→ OCI runtime, napríklad runc
→ Linux process
```

Presné interné komponenty a zodpovednosti sa môžu meniť medzi verziami, ale architektonická hranica zostáva užitočná. Docker CLI nie je runtime. Registry nie je runtime. `runc` typicky nerieši image pull, service discovery ani dlhodobé API management. Dostane pripravený bundle a vykoná create/start/delete operácie nad procesom podľa OCI Runtime Specification.

Pri chybe preto záleží na vrstve. `manifest unknown` vzniká pred process create. `no matching manifest` vzniká pri platform resolution. Chýbajúci dynamic loader sa prejaví až pri exec procesu. Seccomp denial vzniká počas syscall execution. Všetky chyby môžu byť používateľom vnímané ako „container sa nespustil“, ale ich dôkazy a opravy sú rozdielne.

## 11. Attestations nie sú obyčajné filesystem layers

Moderný build môže publikovať provenance a SBOM attestations. Tieto artifacts sa môžu pripojiť k image indexu alebo manifestu pomocou ďalších manifest objects a annotations. Neznamená to, že SBOM je súbor v root filesysteme containeru.

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --provenance=mode=max \
  --sbom=true \
  --push \
  -t registry.example.com/atlas/payments-api:1.4.2 .
```

Po publikovaní treba overiť, ku ktorému subject digestu attestations patria. Tag-based scanner alebo podpis, ktorý sa neskôr nekoreluje s deployed digestom, nevytvára dôveryhodnú supply-chain väzbu.

## 12. Incident: amd64 bol overený, arm64 nebol

Atlas publikoval `payments-api:1.4.2` ako multi-platform index. Pipeline spustila testy a scanner nad lokálnym amd64 image-om. Potom Buildx vytvoril amd64 aj arm64 platform branches a publikoval jeden index.

Na arm64 node container skončil s `exec format error`. Registry a index boli validné. Index správne uvádzal arm64 manifest, ale build stage skopíroval amd64 binary aj do arm64 runtime stage-u pre chybný cache key.

```text
source test na amd64
→ amd64 runtime image overený
→ multi-platform build vytvorí index
→ arm64 manifest obsahuje amd64 binary
→ registry digesty a media types sú validné
→ arm64 kernel odmietne exec
```

Digest integrity fungovala presne: identifikovala nesprávny artifact bez jeho zmeny. Chýbala semantic a platform validation.

Recovery vytvorila nový index digest. Pipeline pridala per-platform binary inspection, native arm64 smoke test a väzbu test reportu na platform manifest digest. Starý tag sa prestal používať v produkcii; deployment prešiel na immutable index digest.

## 13. Praktická diagnostika image graphu

Pri image incidente najprv zisti, či reference ukazuje na index alebo priamo na platform manifest. Potom rozlíš index digest, selected manifest digest, config digest a layer digests.

```bash
docker buildx imagetools inspect IMAGE

docker buildx imagetools inspect IMAGE --raw \
  | jq .
```

Lokálne image metadata:

```bash
docker image inspect IMAGE
```

Filesystem history:

```bash
docker image history --no-trunc IMAGE
```

Tieto nástroje odpovedajú na rozdielne otázky. Registry inspect ukazuje registry-visible graph. `docker image inspect` ukazuje object v konkrétnom local image store-i. History približuje build layer metadata, ale nemusí rekonštruovať všetky BuildKit interné operácie ani attestations.

Ak runtime hlási `no such file or directory` pri existujúcom binary, skontroluj nielen path, ale aj shebang interpreter alebo ELF dynamic loader. Kernel môže nájsť executable file, no nenájsť loader uvedený v binary headeri. To je runtime compatibility problém, nie chýbajúci manifest.

## Čo si z kapitoly odniesť

OCI image nie je jeden tarball a OCI runtime nie je registry client. Image graph sa skladá z descriptorov, indexov, platform manifestov, image configu a filesystem layers. Distribution API prenáša a publikuje tieto content-addressed objekty. Runtime Specification opisuje konkrétny process bundle a isolation konfiguráciu.

Index digest, platform manifest digest, config digest a layer digest označujú rozdielne objekty. Tag je pointer, nie content identity. Platný digest dokazuje integritu a identitu bytes, nie funkčnosť, bezpečnosť alebo kompatibilitu. Dôveryhodný release preto viaže testy, scan, SBOM, provenance a deployment na správny index a všetky očakávané platform manifests.

## Primárne zdroje

- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec)
- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)
- [Docker image digests](https://docs.docker.com/dhi/core-concepts/digests/)
- [Buildx imagetools inspect](https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/)
- [Image attestations](https://docs.docker.com/build/metadata/attestations/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Namespaces, cgroups a capabilities](namespaces-cgroups-capabilities.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Images, layers a copy-on-write →](images-layers-copy-on-write.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
