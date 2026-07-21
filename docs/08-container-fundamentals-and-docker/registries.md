# Registries

Container registry je distribution a storage služba pre manifests, blobs a súvisiace OCI artifacts. Registry nie je iba „miesto pre Docker images“. Je to content-addressed artifact systém s repository namespaces, authentication, authorization, retention, replication a supply-chain controls.

## 1. Registry, repository, image a reference

Rozlišuj:

- **registry** — server alebo služba poskytujúca distribution API,
- **repository** — logical namespace pre príbuzné manifests a tags,
- **manifest** — metadata odkazujúca na config a layers,
- **blob** — content-addressed object,
- **tag** — mutable human-readable pointer,
- **digest** — immutable content identity.

Príklad:

```text
registry.example.com/platform/api:v1.4.2
│                    │            └─ tag
│                    └────────────── repository
└─────────────────────────────────── registry
```

Digest reference:

```text
registry.example.com/platform/api@sha256:...
```

## 2. Push workflow

Typický push:

1. client zistí, ktoré blobs už registry má,
2. chýbajúce blobs uploadne,
3. uploadne config,
4. publikuje manifest alebo image index,
5. priradí tag,
6. prípadne publikuje signatures, SBOM a provenance artifacts.

Manifest by sa mal publikovať až po dostupnosti všetkých referenced blobs. Inak môže vzniknúť neúplný artifact.

## 3. Pull workflow

Typický pull:

1. resolve tag na manifest alebo index,
2. over digest a media type,
3. vyber platform manifest,
4. stiahni config a chýbajúce layers,
5. over digests,
6. unpackni content,
7. aplikuj trust a security policy.

Pull podľa tagu a deployment podľa digestu sú rozdielne rozhodnutia. Tag možno použiť na discovery, ale deployment record má zachytiť resolved digest.

## 4. Authentication a authorization

Registry access typicky používa bearer token flow alebo product-specific identity integration.

Rozlišuj scopes:

- pull,
- push,
- delete,
- tag mutation,
- repository administration,
- retention/GC administration,
- signature alebo artifact publication.

CI build identity nemá automaticky potrebovať delete/admin oprávnenia. Production runtime má typicky potrebovať iba pull pre konkrétne repositories.

## 5. Repository naming a tenancy

Repository namespace model má vyjadrovať:

- organization alebo team ownership,
- application alebo component,
- environment separation iba ak je vedomá,
- access boundary,
- retention a replication policy.

Kopírovanie rovnakého image do `dev`, `stage` a `prod` repository môže zmeniť digest iba v prípade transformácie; ideálne sa promotuje ten istý content a menia sa deployment references alebo registry-side trusted copies bez rebuild-u.

## 6. Tags

Tags sú užitočné pre:

- release names,
- channels,
- branch builds,
- compatibility aliases.

Riziká mutable tags:

- race medzi scanom a deploymentom,
- nejasný rollback,
- cache inconsistency,
- audit trail bez content identity,
- prepísanie release tagu.

Odporúčanie:

```text
immutable release tag + manifest digest + deployment record
```

`latest` je iba konvenčný tag, nie špeciálna alebo bezpečná verzia.

## 7. Multi-platform artifacts

Tag môže smerovať na image index, ktorý odkazuje na viac platform manifests. Registry musí zachovať celý graph.

Pri promotion alebo mirroringu prenes:

- index,
- všetky potrebné platform manifests,
- referenced configs a layers,
- related signatures/SBOM/provenance podľa policy.

Partial copy môže fungovať na jednej architecture a zlyhať na druhej.

## 8. OCI artifacts a referrers

Registry môže ukladať artifacts previazané so subject digestom, napríklad:

- SBOM,
- signature,
- provenance,
- vulnerability report,
- policy attestation.

Security workflow musí vedieť, či destination registry a copy tool zachovávajú referrers. Samotné skopírovanie image manifestu nemusí preniesť všetku evidence.

## 9. Immutability policy

Registry môže blokovať prepísanie vybraných tags alebo repositories.

Immutability chráni:

- release identity,
- deployment reproducibility,
- scan evidence,
- audit trail.

Nechráni pred:

- kompromitovaným buildom pred pushom,
- zlým artifactom publikovaným prvýkrát,
- krádežou pull credentials,
- deletion adminom,
- zraniteľnosťou objavenou neskôr.

## 10. Retention

Retention policy má rozlišovať:

- release artifacts,
- active deployment digests,
- rollback window,
- branch/PR builds,
- untagged manifests,
- signatures a SBOM,
- legal/audit retention.

„Delete untagged after 7 days“ môže odstrániť digest používaný deploymentom, ak deployment nepoužíva tag alebo registry nevie o runtime references.

## 11. Garbage collection

Garbage collection odstraňuje blobs, ktoré už nie sú reachable z retained manifests alebo iných references.

Bezpečný GC potrebuje:

- konzistentný repository graph,
- koordináciu s concurrent pushes/deletes,
- ochranu related artifacts,
- backup/recovery model,
- dry-run alebo report,
- audit deletion.

Tag deletion a blob deletion nie sú rovnaká operácia.

## 12. Replication a mirroring

Registry replication môže byť:

- synchronous alebo asynchronous,
- push-based alebo pull-through,
- regionálny mirror,
- air-gapped promotion,
- disaster-recovery replica.

Overuj:

- digest consistency,
- lag,
- delete propagation,
- tags vs. immutable content,
- referrer transfer,
- access policy parity.

Replica bez pravidelného restore/failover testu nie je dokázaná recovery capability.

## 13. Pull-through cache

Pull-through cache alebo dependency proxy znižuje:

- latency,
- external rate limits,
- repeated downloads,
- dostupnostnú závislosť od upstreamu.

Zároveň vytvára:

- cache freshness policy,
- trust boundary,
- malware/vulnerability retention,
- storage a eviction behavior,
- potrebu pinovať upstream digest.

Cacheovanie mutable tagu bez digest evidence môže viesť k rozdielnemu contentu medzi buildmi.

## 14. Signing a provenance

Signature viazaná na digest môže dokazovať, že konkrétna identity schválila alebo podpísala konkrétny content. Provenance môže opisovať builder, source, inputs a build process.

Trust policy má definovať:

- kto smie podpisovať,
- ktoré issuer/identity claims sú povolené,
- ktoré repositories a environments policy pokrýva,
- expiration/revocation,
- offline alebo keyless model,
- behavior pri nedostupnej verification službe.

Podpis neznamená, že artifact je bez zraniteľností.

## 15. Vulnerability scanning

Registry scanning môže analyzovať uložené images pri pushi alebo opakovane po zmene vulnerability databázy.

Dôležité rozdiely:

- scan time vs. deploy time,
- OS packages vs. language dependencies,
- image content vs. runtime reachability,
- fixed version availability,
- accepted risk a expiration,
- platform-specific manifest coverage.

Scan report musí byť viazaný na digest, scanner/version a database timestamp.

## 16. Secrets a credentials

Registry credentials chráň pomocou:

- short-lived tokens,
- workload identity,
- repository-scoped access,
- credential helpers,
- secret managers,
- audit a rotation.

Neukladaj plaintext auth do image, source repository ani world-readable runtime config. Docker-style config môže obsahovať bearer/auth material alebo helper references a musí mať správne permissions.

## 17. Availability a failure modes

Registry je deployment dependency. Failure môže zasiahnuť:

- nové node pulls,
- autoscaling,
- rollback na image, ktorý už nie je cached,
- build pipelines,
- vulnerability evidence,
- disaster recovery.

Mitigácie:

- regionálne mirrors,
- node/content cache,
- digest pinning,
- capacity planning,
- backup a restore,
- retention rollback artifacts,
- rate-limit monitoring.

## 18. Air-gapped workflow

Air-gapped promotion potrebuje export/import contract pre:

- image graph,
- platform manifests,
- signatures a attestations,
- vulnerability evidence,
- approval record,
- malware scanning,
- destination verification.

Ručné prenesenie tar súboru bez digest ledgeru a chain of custody oslabuje auditovateľnosť.

## 19. Observability

Sleduj:

- push/pull latency a error rate,
- storage usage a growth,
- GC reclaimed bytes,
- replication lag,
- auth failures,
- rate limits,
- scan backlog,
- unsigned/unscanned artifact count,
- stale tags,
- active deployments odkazujúce na expiring content.

## 20. Troubleshooting

### `manifest unknown`

Reference neexistuje, bola odstránená, klient používa zlý repository path alebo replica ešte nie je synchronizovaná.

### `unauthorized` alebo `denied`

Rozlíš authentication failure od chýbajúceho repository/action scope-u.

### Pull funguje na amd64, nie na arm64

Tag/index neobsahuje arm64 manifest alebo promotion preniesol iba jednu platformu.

### Tag ukazuje na iný digest než pri schválení

Tag bol mutable alebo vznikol race. Deployment má používať schválený digest.

### Registry storage rastie po mazaní tags

Blobs sú stále referenced alebo GC neprebehol. Over retention, manifests, referrers a running upload state.

## 21. Kontrolné otázky

1. Aký je rozdiel medzi registry a repository?
2. Prečo digest a tag nie sú ekvivalentné?
3. Ako prebieha push a pull graphu?
4. Čo musí preniesť multi-platform promotion?
5. Ako referrers súvisia so SBOM a signatures?
6. Prečo tag deletion neuvoľní automaticky blob?
7. Aké riziká má pull-through cache?
8. Čo podpis dokazuje a čo nie?
9. Ako navrhnúť runtime pull permissions?
10. Ako registry outage ovplyvní autoscaling a rollback?

## Glossary impact

Relevantné pojmy: container registry, repository, tag, digest reference, immutable tag, manifest pull, blob upload, registry scope, pull-through cache, registry mirror, replication lag, registry retention, garbage collection, OCI referrer, artifact signature, build provenance a air-gapped promotion.

## Oficiálna dokumentácia

- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)
- [Docker Registry overview](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-registry/)
