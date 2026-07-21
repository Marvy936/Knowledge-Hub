# OCI image a runtime standards

Open Container Initiative (OCI) definuje otvorené contracts pre packaging, execution a distribution container artifacts. OCI nie je jeden runtime ani registry produkt. Je to súbor špecifikácií, ktoré umožňujú interoperabilitu medzi build tools, registries, container engines a low-level runtimes.

## 1. Tri hlavné OCI špecifikácie

OCI aktuálne pokrýva tri samostatné oblasti:

| Špecifikácia | Rieši |
|---|---|
| Image Specification | image manifest, index, configuration a filesystem layers |
| Runtime Specification | runtime bundle a lifecycle container processu |
| Distribution Specification | registry HTTP API pre blobs, manifests a related artifacts |

Tieto contracts sa prepájajú, ale nie sú totožné. Runtime nemusí vedieť buildovať image a registry nemusí vedieť spúšťať container.

## 2. End-to-end model

Zjednodušený tok:

```text
source + build instructions
→ OCI-compatible image
→ registry/distribution API
→ pull by digest
→ unpacked root filesystem
→ OCI runtime bundle
→ low-level runtime
→ isolated process
```

Každý krok má vlastné identity, metadata, trust a failure boundary.

## 3. OCI image

OCI image je content-addressed graph artifacts. Typicky obsahuje:

- image manifest,
- image configuration,
- ordered filesystem layers,
- media types,
- digests a sizes,
- optional annotations,
- prípadne image index pre viac platforiem.

Image nie je jeden tar súbor s implicitným významom. Manifest explicitne odkazuje na config a layers cez descriptors.

## 4. Descriptor

Descriptor identifikuje content pomocou:

- `mediaType`,
- `digest`,
- `size`,
- optional URLs, annotations alebo platform metadata podľa kontextu.

Digest chráni identity a integrity contentu. Tag je mutable human-friendly pointer; descriptor digest je content identity.

## 5. Image manifest

Manifest spája:

- jednu image configuration,
- ordered list filesystem layers,
- media-type metadata.

Poradie layers je významné. Root filesystem vzniká aplikovaním changesets v deklarovanom poradí.

Manifest digest sa často používa ako deployment identity:

```text
registry.example/app@sha256:...
```

## 6. Image configuration

Image config obsahuje runtime defaults a history metadata, napríklad:

- architecture a OS,
- environment variables,
- entrypoint a command,
- working directory,
- user,
- exposed ports ako metadata,
- labels,
- root filesystem diff IDs,
- build history.

Config neobsahuje host kernel. Runtime musí použiť kompatibilný host alebo virtualization/sandbox vrstvu.

## 7. Image index a multi-platform images

Image index môže odkazovať na viac manifests pre rozdielne platformy:

- OS,
- architecture,
- variant,
- ďalšie platform metadata.

Príklad logiky:

```text
tag: v1.4.0
→ image index
  → linux/amd64 manifest
  → linux/arm64 manifest
```

Pull client vyberie platform-specific manifest. Rovnaký tag preto nemusí znamenať rovnaký manifest digest na každej platforme.

## 8. Filesystem layer

Layer je compressed alebo uncompressed filesystem changeset. Obsahuje napríklad:

- pridané files,
- zmenené metadata,
- directories,
- whiteouts reprezentujúce deletion.

Layer nie je samostatný plný filesystem. Výsledný rootfs vzniká skladaním všetkých layers.

## 9. Diff ID a blob digest

Rozlišuj:

- **distribution digest** — digest prenášaného blobu, často compressed,
- **diff ID** — digest uncompressed layer contentu používaný v image config rootfs chain.

Rovnaký uncompressed changeset môže mať odlišný compressed blob pri inom compression formáte alebo encodingu.

## 10. OCI artifact

OCI image/distribution model sa používa aj pre artifacts, ktoré nie sú runnable container images. Príklady:

- SBOM,
- signatures,
- provenance attestations,
- Helm charts,
- WebAssembly artifacts,
- policy bundles.

`artifactType`, `subject` a referrers model umožňujú previazať metadata artifact s konkrétnym subject digestom.

## 11. Runtime bundle

OCI Runtime Specification pracuje s filesystem bundle obsahujúcim:

- directory `rootfs`,
- `config.json` s runtime configuration.

Runtime config definuje napríklad:

- process arguments a environment,
- user,
- root filesystem,
- mounts,
- namespaces,
- capabilities,
- resource controls,
- hooks,
- hostname a ďalšie platform-specific nastavenia.

Image artifact a runtime bundle nie sú rovnaká forma. Engine alebo vyššia runtime vrstva image pullne, overí, unpackne a vytvorí bundle/configuration.

## 12. Low-level a high-level runtime

Prakticky rozlišuj:

### Low-level runtime

Vytvorí a spustí izolovaný process podľa OCI runtime bundle, spravuje namespaces, mounts, capabilities a process lifecycle.

### High-level runtime alebo container engine

Rieši širší lifecycle:

- image pull a unpack,
- snapshots,
- networking,
- metadata,
- container records,
- restart policy,
- API,
- orchestration integration.

OCI Runtime Specification štandardizuje low-level execution contract, nie celý engine behavior.

## 13. Container lifecycle states

Runtime specification definuje lifecycle operácie a states okolo create/start/kill/delete modelu. Dôležitý je rozdiel:

- **create** pripraví container a jeho isolation bez spustenia user processu,
- **start** spustí definovaný process,
- **kill** doručí signal,
- **delete** odstráni runtime state po ukončení.

Vyššie vrstvy môžu pridávať vlastné states, restart policies alebo sandbox concepts.

## 14. Runtime hooks

Hooks umožňujú spustiť host-side alebo namespace-aware actions v určitých lifecycle bodoch. Sú silným extension bodom a zároveň supply-chain/security rizikom.

Hooks potrebujú:

- explicitný owner,
- pinned executable identity,
- controlled environment,
- timeout,
- audit logs,
- failure semantics.

Nedôveryhodný image by nemal svojvoľne definovať privileged host hook.

## 15. OCI Distribution API

Distribution Specification definuje registry API pre:

- blob upload/download,
- manifest push/pull,
- tags,
- content discovery,
- cross-repository blob mounting podľa implementácie a permissions,
- referrers capability podľa podporovanej verzie/modelu.

Registry je content store a metadata API. Build, vulnerability scanning, signing alebo retention sú nadstavbové capabilities produktu alebo workflowu.

## 16. Tags a digests

```text
repository:tag
```

je human-readable reference. Tag môže byť prepísaný.

```text
repository@sha256:digest
```

identifikuje konkrétny manifest content.

Bezpečný promotion model zachováva digest naprieč environments a mení iba schválené references alebo deployment records.

## 17. Media types

Media type určuje semantic formu blobu alebo manifestu. Consumer nesmie predpokladať, že každý registry object je Docker-style runnable image.

Pri interoperabilite over:

- podporované media types,
- compression formáty,
- schema compatibility,
- artifact/referrer support,
- platform selection.

## 18. Docker a OCI

Docker image a registry ecosystem významne ovplyvnili vznik OCI. Moderné Docker/container tools typicky pracujú s OCI-compatible alebo príbuznými formátmi, ale konkrétny product môže pridávať vlastné metadata, APIs a behavior.

Preto rozlišuj:

- OCI standard,
- implementation,
- Docker CLI/Engine behavior,
- registry product features,
- orchestrator abstractions.

## 19. Compatibility

OCI compliance negarantuje:

- application compatibility s host kernelom,
- rovnaký security profile,
- rovnaký networking model,
- rovnakú storage implementáciu,
- rovnaký restart behavior,
- podporu všetkých optional features.

Interoperability contract je užší než „spustí sa rovnako všade“.

## 20. Trust a verification

Pri pull/deploy workflowe overuj:

1. registry a repository identity,
2. manifest digest,
3. platform selection,
4. signature alebo trust policy,
5. provenance a builder identity,
6. SBOM a vulnerability evidence,
7. runtime policy,
8. deployment record.

Digest dokazuje content identity, nie dôveryhodnosť autora alebo bezpečnosť obsahu.

## 21. Troubleshooting

### `no matching manifest for platform`

Image index neobsahuje požadovanú OS/architecture/variant kombináciu alebo client vybral nesprávnu platformu.

### Digest sa líši medzi platformami

Tag ukazuje na image index a jednotlivé platform manifests majú vlastné digests.

### Registry prijme image, runtime ju nespustí

Distribution compatibility neznamená runtime/platform compatibility. Over media types, architecture, config, filesystem a runtime features.

### Signature alebo SBOM sa po copy stratili

Copy workflow nepreniesol related OCI artifacts/referrers alebo destination registry tento model nepodporuje rovnakým spôsobom.

### Runtime config funguje v jednom engine a nie v inom

Over optional OCI fields, implementation-specific defaults, kernel support, LSM/seccomp policy a higher-level engine behavior.

## 22. Kontrolné otázky

1. Aký je rozdiel medzi Image, Runtime a Distribution Specification?
2. Čo obsahuje OCI descriptor?
3. Ako sa líši manifest a image config?
4. Na čo slúži image index?
5. Aký je rozdiel medzi blob digestom a diff ID?
6. Ako vzniká runtime bundle z image?
7. Čo robí low-level runtime a čo container engine?
8. Prečo tag nie je immutable identity?
9. Čo je OCI artifact a subject/referrer vzťah?
10. Čo OCI compliance negarantuje?

## Glossary impact

Relevantné pojmy: OCI, OCI Image Specification, OCI Runtime Specification, OCI Distribution Specification, descriptor, image manifest, image configuration, image index, multi-platform image, layer blob, diff ID, OCI artifact, subject, referrer, runtime bundle, low-level runtime a media type.

## Oficiálna dokumentácia

- [Open Container Initiative](https://opencontainers.org/)
- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec)
- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)
