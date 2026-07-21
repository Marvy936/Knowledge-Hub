# Container a package registry

GitLab integruje source repository, CI/CD a registries. Container Registry distribuuje OCI/container images. Package Registry poskytuje package-manager a generic package workflows. Registry nie je iba storage: je súčasť artifact identity, access control, dependency governance, retention a software supply chain.

## 1. Registry model

Typický tok:

```text
source commit
→ CI build
→ test a scan
→ immutable package/image
→ registry publish
→ promotion alebo consumer install
→ deployment/runtime
```

Registry artifact musí byť spätne mapovateľný na source, build a release evidence.

## 2. Container Registry

GitLab Container Registry je integrovaný registry pre container images. Project má registry namespace odvodený od project pathu.

Predefined variables typicky poskytujú:

- registry host,
- image repository path,
- job-scoped authentication údaje.

Presné variables a permissions over podľa aktuálnej GitLab dokumentácie.

## 3. Image identity

Rozlišuj:

- repository,
- tag,
- manifest,
- manifest list/index,
- content digest,
- platform variant.

Príklad:

```text
registry.example.com/team/app:2.4.1
registry.example.com/team/app@sha256:...
```

Tag je ľudský pointer. Digest je immutable content identity.

## 4. Tagging strategy

Užitočné tags:

- release version, napríklad `2.4.1`,
- commit SHA,
- branch alebo channel tag,
- release candidate,
- environment alias.

Mutable tags ako `latest`, `main` alebo `stable` sú discovery aliases. Deployment record musí zachovať digest.

## 5. Build once, promote many

Správny model:

```text
build image once
→ publish digest
→ scan/test digest
→ promotion rovnakého digestu
→ deploy digest
```

Rebuild rovnakého tagu pre staging a production vytvára rozdielne bytes a ruší predchádzajúcu evidence.

## 6. Authentication

CI job môže použiť job-scoped registry credentials. Ďalšie identity môžu byť:

- deploy token,
- project/group access token,
- personal access token,
- cloud/runtime workload identity podľa integration modelu.

Preferuj non-human, scoped a expirovateľnú identity. Personal token vývojára nemá byť production pull credential.

## 7. Push a pull permissions

Oddeľ:

- kto smie publishovať,
- kto smie pullovať,
- kto smie mazať,
- kto spravuje retention,
- ktorý pipeline context smie vytvoriť release tag.

Untrusted merge-request pipeline nemá pushovať do production release namespace.

## 8. Image build security

Build job môže mať vysoké oprávnenia. Zváž:

- rootless BuildKit/Buildah/Kaniko podľa platformy,
- dedicated ephemeral runner,
- zákaz host Docker socketu,
- pinned base images,
- dependency verification,
- network egress policy,
- provenance a signature.

Container build context nesmie obsahovať secrets. `.dockerignore` je dôležitá, ale nie jediná kontrola.

## 9. Base images

Pinovanie iba tagu môže viesť k nepozorovanej zmene base image.

Možnosti:

- digest pinning,
- controlled update bot,
- rebuild cadence,
- vulnerability monitoring,
- approved base-image catalog,
- provenance policy.

Starý digest je reprodukovateľný, ale môže obsahovať známe vulnerabilities. Reproducibility a patching treba riadiť spolu.

## 10. Multi-platform images

OCI index môže odkazovať na viac platform manifests:

```text
linux/amd64
linux/arm64
windows/amd64
```

Testuj každú podporovanú platformu. Tag na manifest list nie je dôkaz, že všetky variants boli vytvorené rovnakým source a policy.

## 11. Container scanning

Scan má byť viazaný na konkrétny digest. Sleduj:

- OS packages,
- language packages podľa capability scanneru,
- base image,
- severity,
- exploitability/reachability podľa dostupných dát,
- fix version,
- exceptions.

Image môže byť po publishnutí znovu vyhodnotený pri aktualizácii vulnerability databázy.

## 12. Signing a verification

High-assurance workflow môže vyžadovať:

- image signature,
- provenance attestation,
- SBOM,
- policy verification pred deploymentom.

Signing key nesmie byť dostupný v untrusted pipeline. Preferuj workload identity, isolated signing service alebo keyless model podľa platformy.

## 13. Cleanup policy

Registry cleanup chráni storage pred nekonečným rastom.

Policy musí zachovať:

- production digests,
- supported releases,
- rollback candidates,
- active release candidates,
- compliance artifacts,
- manifests referencované ďalšími tags.

Regex založené čistenie bez referenčného inventára môže odstrániť potrebný recovery image.

## 14. Garbage collection

Odstránenie tagu nemusí okamžite odstrániť underlying blobs. Skutočné uvoľnenie storage závisí od registry garbage-collection a deployment modelu.

Pri Self-Managed GitLabe koordinuj cleanup a GC podľa aktuálnej administrátorskej dokumentácie.

## 15. Package Registry

GitLab Package Registry podporuje viac package ecosystems a generic packages. Použitie:

- interné libraries,
- CLI binaries,
- application packages,
- Maven/NuGet/npm/PyPI a ďalšie ekosystémy,
- generic release bundles,
- Terraform modules podľa príslušného registry modelu.

Podporované formats a features sa menia; over aktuálnu dokumentáciu.

## 16. Package coordinates

Package identity typicky obsahuje:

- registry/project/group scope,
- package name,
- version,
- variant/classifier,
- checksum.

Version má byť immutable. Prepísanie už publikovanej verzie poškodzuje dependency reproducibility.

## 17. Publish workflow

Publish job má overiť:

1. protected ref alebo release policy,
2. version ešte neexistuje,
3. source a artifact identity,
4. test/scan evidence,
5. package metadata,
6. checksum/signature,
7. release record.

Publishing nemá implicitne rebuildovať release artifact.

## 18. Dependency Proxy

Dependency Proxy môže cacheovať upstream images alebo packages podľa GitLab capability.

Výhody:

- nižší upstream rate-limit dopad,
- rýchlejšie pulls,
- centralizovaný endpoint,
- menšia závislosť na krátkodobej upstream dostupnosti.

Nie je automaticky trust verifier. Stále kontroluj digest, provenance a allowed sources.

## 19. Virtual registry

Virtual registry môže agregovať, proxyovať alebo cacheovať external package sources podľa dostupnej GitLab functionality.

Governance otázky:

- ktoré upstream registries sú povolené,
- ako sa rieši namespace confusion,
- ako sa cache invaliduje,
- ktoré packages sa mirrorujú,
- ako sa zaznamenáva pôvod.

## 20. Dependency confusion

Ak interný package name existuje aj vo verejnom registry, nesprávna resolver policy môže stiahnuť škodlivý external package.

Ochrany:

- scoped namespaces,
- explicit registry priority,
- private package reservation,
- lockfiles a checksums,
- egress control,
- dependency allowlist.

## 21. Job token access

Cross-project package alebo registry access cez job token má mať explicitný allowlist a minimum scope.

Over:

- source project identity,
- target project permissions,
- protected ref,
- token lifetime,
- audit trail.

## 22. Retention a support lifecycle

Package retention sa riadi podľa:

- supportovaných versions,
- downstream consumers,
- legal/compliance požiadaviek,
- rollback window,
- vulnerability response,
- storage cost.

Pred odstránením package verzie zisti, či ju stále používajú builds alebo production deployments.

## 23. Registry availability

Registry je delivery dependency. Sleduj:

- push/pull latency,
- error rate,
- storage capacity,
- object storage health,
- authentication failures,
- replication podľa topology,
- backup/restore,
- certificate expiry.

Runtime nemá byť závislý na okamžitom pull-e mutable image pri každom requeste.

## 24. Troubleshooting

### `unauthorized` pri push/pull

Over token type, scopes, project path, registry login host, expiration a protected context.

### Image tag existuje, ale deployment používa iný obsah

Tag bol mutable alebo klient použil cached manifest. Porovnaj digest v registry, deployment recorde a runtime.

### Multi-platform pull zlyhá

Požadovaná platform variant chýba alebo manifest/index je chybný.

### Package publish hlási conflict

Version už existuje. Neprepisuj immutable release; vytvor novú version alebo oprav publish policy.

### Cleanup odstránil rollback image

Policy nezohľadnila active deployment digests. Obnov z backup/mirroru a zaveď referenčný inventory.

### Upstream dependency sa náhle zmenila

Používal sa mutable version/tag alebo chýbal lock/checksum. Obnov pinned dependency a audituj build provenance.

## 25. Kontrolné otázky

1. Aký je rozdiel medzi image tagom a digestom?
2. Ako funguje build once, promote many pre registry?
3. Ktorá identity má pushovať release image?
4. Aké riziká má Docker socket pri image build-e?
5. Ako navrhnúť multi-platform image pipeline?
6. Prečo container scan musí byť viazaný na digest?
7. Kedy použiť job artifacts a kedy package registry?
8. Ako vzniká dependency confusion?
9. Čo musí cleanup policy zachovať?
10. Ako overiť, čo je reálne nasadené v produkcii?

## Glossary impact

Relevantné pojmy: GitLab Container Registry, GitLab Package Registry, OCI digest, image tag, multi-platform image, registry cleanup policy, dependency proxy, virtual registry, dependency confusion a generic package.

## Oficiálna dokumentácia

- [Packages and registries](https://docs.gitlab.com/user/packages/)
- [Container Registry](https://docs.gitlab.com/user/packages/container_registry/)
- [Package Registry](https://docs.gitlab.com/user/packages/package_registry/)
- [Dependency Proxy](https://docs.gitlab.com/user/packages/dependency_proxy/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Artifacts a cache](artifacts-and-cache.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Environments, deployments a releases →](environments-deployments-releases.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
