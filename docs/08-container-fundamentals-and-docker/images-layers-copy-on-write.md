# Images, layers a copy-on-write

Container image je immutable, content-addressed artifact zložený z metadata a ordered filesystem layers. Pri spustení container runtime nad image pridá samostatnú writable vrstvu pre konkrétnu runtime inštanciu. Tento model umožňuje zdieľanie obsahu, rýchle vytváranie containers a efektívny distribution, ale vytvára aj špecifické performance, persistence a security trade-offy.

## 1. Image nie je container

Image je read-only template. Container je runtime inštancia vytvorená z image plus:

- process configuration,
- namespaces a cgroups,
- networking,
- mounts a volumes,
- secrets/configuration,
- writable layer,
- runtime identity a lifecycle metadata.

Viac containers môže používať rovnaký image content, ale každý má vlastný process state a writable layer.

## 2. Layered filesystem model

Image layers reprezentujú postupné filesystem changesets:

```text
layer 1: base userspace
layer 2: runtime dependencies
layer 3: application files
layer 4: configuration defaults
```

Výsledný root filesystem je merged view týchto read-only layers. Runtime používa union/overlay filesystem alebo snapshotter implementation, ktorá prezentuje jeden strom.

## 3. Content-addressed storage

Layer a manifest identity sa odvodzuje z digestu obsahu. Výhody:

- integrity verification,
- deduplication,
- cache reuse,
- immutable identity,
- bezpečnejší promotion podľa digestu.

Ak dve images odkazujú na rovnaký layer digest, registry a runtime ho môžu ukladať iba raz.

## 4. Copy-on-write

Copy-on-write (CoW) znamená, že read-only lower content sa pri prvom zápise neprepíše priamo. Zmenený file sa skopíruje alebo reprezentuje v upper writable layeri a ďalšie reads vidia novšiu verziu.

Zjednodušenie:

```text
read file
→ nájdi najvyššiu viditeľnú verziu v layer stacku

write lower-layer file
→ copy-up do writable layeru
→ zmeň writable kópiu
```

CoW znižuje diskovú duplicitu, ale prvý write môže byť drahší a writable layer nie je vhodný ako jediný persistent storage.

## 5. Overlay model

Pri overlay-style filesysteme rozlišuj:

- **lowerdir** — read-only image layers,
- **upperdir** — writable layer containeru,
- **workdir** — interný pracovný adresár,
- **merged** — výsledný pohľad použitý containerom.

Konkrétna implementácia závisí od runtime, kernelu a storage drivera alebo snapshottera.

## 6. Whiteouts

Image layer nemôže fyzicky odstrániť file z predchádzajúceho immutable layeru. Namiesto toho vytvorí whiteout marker, ktorý pri merged view skryje lower-layer path.

Dôsledok:

```dockerfile
RUN create-large-file
RUN delete-large-file
```

nemusí zmenšiť image, pretože bytes zostávajú v staršom layeri. Vytvorenie a odstránenie v jednom build step-e môže zabrániť ich zachovaniu vo výslednom layeri.

## 7. Image history vs. layer content

Build history opisuje instructions a metadata, ale nie je úplným bezpečnostným alebo filesystem auditom. Niektoré instructions môžu vytvoriť empty layers, niektoré build metadata môžu odhaliť sensitive arguments a layer obsah môže zachovať files odstránené v neskoršom kroku.

Pri vyšetrovaní používaj:

- manifest a config,
- layer digests,
- unpacked filesystem analysis,
- SBOM,
- build provenance,
- history iba ako doplnkový signál.

## 8. Layer ordering

Poradie instructions ovplyvňuje cache aj výsledný image.

Stabilné a zriedka sa meniace kroky dávaj pred často meniace sa kroky:

```text
base image
→ system dependencies
→ application dependency metadata
→ dependency install
→ application source
```

Zmena skorého layeru invaliduje downstream cache chain podľa build engine semantics.

## 9. Cache nie je correctness mechanizmus

Build cache môže zrýchliť build, ale nesmie byť jediným zdrojom dependencies alebo dôkazom reproducibility.

Riziká:

- mutable package indexes,
- unpinned versions,
- stale cache,
- cross-branch contamination,
- secret leakage,
- platform-specific cache records.

Correctness vyžaduje pinned inputs, lock files, verified sources a deterministický build contract.

## 10. Writable container layer

Writable layer zachytáva runtime mutations root filesystemu, napríklad:

- generated files,
- temporary caches,
- application writes,
- package installation vykonanú za behu,
- log files bez external loggingu.

Je typicky viazaná na konkrétny container. Pri jeho odstránení môže zmiznúť.

Runtime mutation navyše vytvára rozdiel medzi deklarovaným image a skutočným runtime stavom.

## 11. Persistence boundary

Dáta, ktoré musia prežiť replacement, patria do explicitného persistence modelu:

- volume,
- bind mount,
- object storage,
- database,
- external service,
- orchestration-managed persistent volume.

Writable layer je vhodná pre ephemeral state. Nie je vhodná ako jediná kópia business dát, audit trailu alebo recovery artifactu.

## 12. Read-only root filesystem

Read-only root filesystem:

- obmedzuje runtime mutation,
- znižuje persistence malware alebo attacker changes,
- odhaľuje nejasné writable paths,
- podporuje immutable deployment model.

Aplikácia však môže potrebovať samostatné writable mounts pre:

- `/tmp`,
- runtime sockets,
- caches,
- uploaded data,
- PID alebo state files.

Tieto paths musia mať explicitný lifecycle, size limit a permissions.

## 13. Layer size a image size

Rozlišuj:

- compressed transfer size,
- uncompressed layer size,
- shared content size,
- per-container writable usage,
- snapshot metadata a filesystem overhead.

CLI-reported „image size“ nemusí presne znamenať disk space uvoľnený po deletion, pretože layers môžu byť zdieľané ďalšími images alebo containers.

## 14. Base image selection

Base image je supply-chain a runtime dependency. Hodnoť:

- provenance a ownera,
- update cadence,
- package manager a debugging needs,
- libc a runtime compatibility,
- architecture support,
- vulnerability surface,
- CA certificates a timezone data,
- support lifecycle.

Menší image nie je automaticky bezpečnejší. Minimalizácia znižuje surface, ale chýbajúce observability/debug tools môžu skomplikovať incident response.

## 15. Scratch a distroless images

`FROM scratch` alebo distroless-style image môže znížiť userspace surface. Workload však musí explicitne obsahovať potrebné:

- dynamic libraries,
- CA certificates,
- timezone data,
- user/group metadata,
- DNS/runtime dependencies,
- debugging alebo support strategy.

Production debugging nemusí znamenať inštalovanie shellu do image; možno použiť ephemeral debug container, host tooling alebo observability.

## 16. Multi-stage build súvis

Multi-stage build oddeľuje build environment od runtime image. Build tools a source artifacts nemusia skončiť v final stage.

Výhody:

- menší runtime surface,
- menej secrets a build tools,
- jasnejší artifact handoff,
- lepšia reproducibility.

Podrobne sa rieši v samostatnej kapitole, ale layered model je jeho základ.

## 17. Runtime mutation anti-pattern

Ručné spustenie package managera v bežiacom containeri:

- zmenu nezachytí Dockerfile ani image digest,
- replacement ju odstráni,
- incident evidence je slabšia,
- vzniká snowflake container,
- security scanning image ju nemusí vidieť.

Oprava má vzniknúť novým buildom a deploymentom immutable image.

## 18. Image garbage collection

Runtime/registry musí riadiť:

- referenced a unreferenced manifests,
- shared blobs,
- stopped containers,
- snapshots,
- build cache,
- retention a deletion races.

Deletion tagu nemusí okamžite uvoľniť blobs. Garbage collection potrebuje bezpečne určiť, ktorý content už nemá references.

## 19. Security layers

Secrets nesmú byť zapísané do image layeru. Aj keď sa v neskoršom kroku odstránia, starší layer ich môže stále obsahovať.

Rizikové vstupy:

- copied credential files,
- package registry tokens,
- SSH keys,
- `.env` files,
- build arguments uložené v history,
- private source archives.

Používaj secret mounts alebo build-system secret mechanisms, scoped credentials a final-image scanning.

## 20. Reproducibility

Reproducible image build vyžaduje kontrolu:

- base image digestu,
- source commitu,
- dependency locks,
- package repositories,
- build toolchain,
- timestamps a nondeterministic metadata,
- architecture,
- network inputs,
- build arguments.

Rovnaký Dockerfile bez pinned externých vstupov nemusí vytvoriť rovnaký image.

## 21. Troubleshooting

### Image je veľký aj po odstránení súboru

Súbor vznikol v skoršom layeri a deletion ho iba skryl whiteoutom. Reorganizuj build steps alebo multi-stage handoff.

### Zmena jedného source file invaliduje dependency cache

Poradie `COPY` instructions vložilo source pred dependency install. Oddeľ dependency metadata od application source.

### Container po replacement-e stratil dáta

Dáta boli iba vo writable layeri. Presuň ich do explicitného persistent storage.

### Disk sa neuvoľnil po odstránení image tagu

Blobs môžu byť referencované inými manifests, containers, snapshots alebo build cache. Over content references a GC behavior.

### Secret bol odstránený, ale scanner ho stále nájde

Secret zostal v staršom layeri alebo build metadata. Rebuildni image z clean history a credential okamžite rotuj.

## 22. Kontrolné otázky

1. Aký je rozdiel medzi image a containerom?
2. Ako funguje merged layer view?
3. Čo je copy-up?
4. Na čo slúži whiteout?
5. Prečo neskoršie odstránenie nezmenší starší layer?
6. Prečo writable layer nie je persistent storage?
7. Čo poskytuje read-only root filesystem?
8. Ako layer ordering ovplyvňuje cache?
9. Prečo menší image nie je automaticky bezpečný?
10. Prečo rovnaký Dockerfile nemusí vytvoriť rovnaký digest?

## Glossary impact

Relevantné pojmy: image layer, filesystem changeset, copy-on-write, copy-up, lower layer, upper layer, merged filesystem, whiteout, content-addressed storage, writable container layer, read-only root filesystem, base image, scratch image, distroless image, build cache, runtime mutation a snowflake container.

## Oficiálna dokumentácia

- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [Docker storage drivers](https://docs.docker.com/engine/storage/drivers/)
- [Images and layers](https://docs.docker.com/get-started/docker-concepts/building-images/understanding-image-layers/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OCI image a runtime standards](oci-image-runtime-standards.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Registries →](registries.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
