# Registries

Container registry je content-addressed distribution, authorization a retention boundary. Spája builders, release publishers, security evidence, deployment controllers, runtime nodes a incident recovery. Nie je to iba úložisko tagov. Dôveryhodná publikácia musí zachovať complete OCI graph, exact digests, platform inventory, signatures/SBOM/provenance, repository authorization a destination read-back. Dôveryhodný pull musí zaznamenať, ktorý index a platform manifest runtime skutočne vybral.

Kapitola otvára incident `CTR-PAY-81`. Atlas Payments promuje release `10.4` z build registry do production mirroru. Copy job prenesie amd64 manifest a shared blobs, ale nie index, arm64 manifest ani referrer artifacts. Mutable tag `stable` v mirror-e navyše ukazuje na staršiu generation. Existing amd64 nodes bežia z local cache, arm64 autoscaling nodes hlásia `no matching manifest` a production policy nenájde signature/SBOM, hoci source registry mala complete evidence.

## 1. Dominantný build-to-runtime distribution lifecycle

```text
immutable build/index/platform subjects
→ authenticated repository publication
→ blob/config/manifest/index/referrer graph
→ tag/channel mapping a promotion record
→ replication, retention a scan state
→ consumer token a repository scope
→ exact digest resolution a platform selection
→ content/trust verification a pull
→ runtime digest correlation
→ rollback retention, rescanning a safe garbage collection
```

## 2. Exact registry release subject

```yaml
registryReleaseSubject:
  sourceRepository: registry.build.example/atlas/payments
  destinationRepository: registry.prod.example/atlas/payments
  humanVersion: 10.4.0
  imageIndexDigest: sha256:index104
  platforms:
    linux/amd64:
      manifestDigest: sha256:amd104
      configDigest: sha256:cfg-amd104
    linux/arm64/v8:
      manifestDigest: sha256:arm104
      configDigest: sha256:cfg-arm104
  evidence:
    indexSignature: sha256:sig-index104
    amd64Sbom: sha256:sbom-amd104
    arm64Sbom: sha256:sbom-arm104
    provenance: sha256:prov104
  sourceRevision: 8f41a2c
  promotion:
    runId: promote-817
    identity: registry-promoter-prod
    destinationGeneration: eu-prod-replica-7
  tags:
    immutable: [10.4.0]
    channel: [stable]
```

Deployment record:

```yaml
deploymentImage:
  requestedIndex: sha256:index104
  nodePlatform: linux/arm64/v8
  selectedManifest: sha256:arm104
  verificationPolicy: container-prod-v8
  verificationVerdict: pass
```

Tag bez digestu nie je deployment subject.

## 3. Registry, repository, manifest a blob

Rozlišuj:

- **registry** — API, identity, metadata a content-store boundary;
- **repository** — namespace pre related manifests, tags a access policy;
- **manifest/index** — content graph roots;
- **blob** — content-addressed config/layer bytes;
- **tag** — mutable repository-local pointer;
- **digest** — immutable content identity;
- **referrer/related artifact** — signature, SBOM, provenance alebo report viazaný na subject.

OCI Distribution Specification štandardizuje push/pull behavior pre manifests a blobs a Docker Distribution API používa content digests pre integrity verification. citeturn559344search0turn559344search1turn559344search2

## 4. Complete artifact graph

```text
sha256:index104
├── sha256:amd104
│   ├── sha256:cfg-amd104
│   └── layer blobs
├── sha256:arm104
│   ├── sha256:cfg-arm104
│   └── layer blobs
├── signature/index evidence
├── SBOM/scan amd64
├── SBOM/scan arm64
└── provenance
```

Complete release contract definuje:

- required platforms a variants;
- reachable configs/layers;
- allowed media/compression types;
- signatures, SBOM, provenance and reports;
- schema/producer/freshness validity;
- destination repository and policy;
- retention/rollback window.

Successful push jedného manifestu nie je complete multi-platform release.

## 5. Publication ordering

```text
publisher authenticates
→ push/mount missing blobs
→ verify digest/size
→ publish platform manifests
→ publish index
→ publish subject-bound evidence
→ assign immutable release tag
→ optionally move channel tag
→ read back exact graph
→ create publication record
```

Manifest referencing unavailable blob vytvára incomplete content. Read-after-write overuje destination API, nie iba client-side push status.

Practical read-back:

```bash
docker buildx imagetools inspect \
  registry.prod.example/atlas/payments@sha256:index104 \
  --raw > prod-index.json

jq -r '.manifests[] | [.platform.os,.platform.architecture,(.platform.variant // ""),.digest] | @tsv' prod-index.json
```

Index JSON preukazuje descriptors, ktoré destination registry vydala pre digest. Nepreukazuje, že every referenced blob/referrer is fetchable alebo trusted.

## 6. Authentication a authorization

Registry authorization subject:

```text
principal
+ repository
+ action
+ token audience/scope
+ environment/trust class
+ expiry
```

Oddelené identities:

```text
builder
→ push candidate repository

promoter
→ pull source + push destination

production node
→ pull production repository only

scanner/auditor
→ read manifests/blobs/referrers

registry administrator
→ retention/delete/recovery
```

Node pull token nemá push/delete. Builder nemá production tag overwrite po promotion. Shared long-lived password na každom node zhoršuje revocation a attribution.

## 7. Mutable tags a TOCTOU

```text
scan stable at T1 → index104
→ tag moves
→ deploy stable at T2 → index105
```

Safe flow:

```text
resolve tag once
→ store index digest
→ verify evidence for digest
→ deploy digest
```

Immutable release tag znižuje accident risk, ale digest zostáva authoritative identity. Channel tags ako `stable` alebo `canary` sú discovery/control pointers a potrebujú audit.

## 8. Promotion bez rebuildu

Promotion má preniesť schválený content:

```text
source graph index104
→ destination copy
→ destination digests equal
→ destination evidence inventory complete
→ destination policy pass
```

Rebuild „pre production“ vytvorí nový artifact subject. Ak registry/tool recompression zmení manifest digests, pipeline musí zachovať explicitné source-to-destination mapping a nové evidence; tvrdenie „rovnaký image“ nestačí.

## 9. Platform completeness

Promotion verification:

```bash
expected='linux/amd64 linux/arm64/v8'
actual="$(jq -r '.manifests[] | .platform.os + "/" + .platform.architecture + (if .platform.variant then "/" + .platform.variant else "" end)' prod-index.json | sort | xargs)"
printf 'actual_platforms=%s\n' "$actual"
```

Exact assertion má porovnať normalized expected set. Jeden amd64 pull nepreukazuje arm64 availability.

## 10. Pull lifecycle

```text
node/workload identity
→ repository pull token
→ resolve exact digest
→ fetch index/manifest
→ select platform
→ verify signature/provenance/policy
→ fetch config/layers
→ verify digest/size
→ unpack snapshot
→ record selected manifest
```

Pull success končí na distribution/content boundary. Unpack, runtime create a application readiness sú ďalšie boundaries.

## 11. Mirror a replication state

```text
source generation
→ replication queue
→ destination manifests/blobs/referrers
→ tag/delete propagation
→ destination authorization/policy
```

Sleduj:

- replication lag;
- partial graph;
- stale tag mapping;
- missing referrers;
- media-type support;
- authorization parity;
- failover/failback generation.

Existing nodes môžu bežať z local snapshotu, takže registry failure sa prejaví iba pri autoscalingu, reschedule alebo rollbacku.

## 12. Pull-through cache

```text
client reference
→ cache tag/digest lookup
→ cached content alebo upstream fetch
→ client response
```

Mutable tag môže mať rozdielny content v rôznych caches. Digest request je jednoznačnejší, ale cache môže mať stale negative result, incomplete content alebo unavailable upstream. Cache identity a upstream source patria do troubleshooting subjectu.

## 13. Signatures, provenance, SBOM a scans

Trust verdict:

```text
subject digest matches
+ signer/issuer identity allowed
+ provenance source/builder allowed
+ expected platform inventory complete
+ every platform SBOM/scan valid
+ vulnerability database freshness acceptable
+ exception valid and unexpired
```

Index signature preukazuje signed platform inventory, nie runtime testing every platform. Platform scan preukazuje analyzer findings pre that manifest and database generation, nie future vulnerability state.

## 14. Continuous reassessment

```text
new CVE/advisory
→ identify affected stored platform manifests
→ correlate deployed selected manifests
→ risk/exception decision
→ rebuild new image
→ redeploy and retire old digest
```

Runtime inventory musí uchovávať selected platform manifest, nie iba index alebo tag.

## 15. Repository design

Repository boundary má odrážať ownership a authorization:

```yaml
repositoryContract:
  name: atlas/payments
  owners: [payments-platform]
  publishers: [payments-build-prod, registry-promoter-prod]
  consumers: [payments-prod-nodes]
  requiredPlatforms: [linux/amd64, linux/arm64/v8]
  releaseTagPolicy: immutable
  channelTagPolicy: audited-mutable
  retentionClass: tier-1
  rollbackWindowDays: 30
```

Environment-specific repository môže byť legitímna authorization/air-gap boundary. Nemá byť dôvodom rebuildovať artifact.

## 16. Retention a active deployment inventory

Digest môže byť:

- running in production;
- needed for rollback;
- referenced by image index;
- subject of signature/SBOM/provenance;
- retained for audit/legal reason;
- needed by air-gapped environment;
- locally cached but no longer pullable.

Tag-only retention nie je bezpečná pre digest deployments. Registry policy potrebuje external deployment/rollback inventory.

## 17. Garbage collection

Safe GC:

```text
coordinate/fence writers
→ build consistent manifest/referrer/deployment reachability graph
→ protect in-progress uploads and leases
→ dry-run candidate inventory
→ delete unreachable content
→ verify retained digest pulls and evidence
→ audit reclaimed bytes
```

Distribution documentation upozorňuje, že registry garbage collection sa má vykonávať read-only alebo so zastavenými writes, inak môže zmazať layer uploadnutý, ale ešte nereferencovaný manifestom. citeturn559344search8turn559344search22

`docker system prune` na node nie je registry GC a nerieši central retention.

## 18. Registry backup a restore

Registry DR zahŕňa:

- manifests/tags metadata;
- blob content store;
- repository authorization/configuration;
- signing/key dependencies;
- referrers/evidence;
- replication state;
- DNS/endpoints a client trust;
- testovaný clean restore.

Object-store versioning samo nepreukazuje registry-consistent restore. Restore test pullne representative multi-platform digest, overí evidence and launches runtime smoke.

## 19. Air-gapped transfer

Air-gap package:

```text
complete index/platform/config/layer graph
+ signatures/SBOM/provenance
+ vulnerability/policy record
+ manifest of digests/sizes/media types
+ chain of custody
+ destination import/read-back
```

Ručný single-platform `docker save` archive môže stratiť multi-platform/evidence semantics podľa tool workflow. Transfer contract musí byť explicitný.

## 20. Worked incident `CTR-PAY-81`: incomplete mirror

Source registry:

```text
index104 + amd104 + arm104 + signatures + SBOMs
```

Destination mirror:

```text
amd104 only
stable tag → index103
```

Outcome:

```text
existing amd64 node uses local snapshot and appears healthy
→ new amd64 pull may resolve stale stable
→ arm64 pull fails
→ policy lookup finds no evidence
```

Recovery:

1. freeze channel-tag mutation;
2. inventory running selected manifests;
3. compare source/destination graph and tag mappings;
4. copy complete graph by digest;
5. verify destination authorization and evidence;
6. publish new immutable promotion record;
7. pull/run both platforms on clean nodes;
8. remove stale channel mapping after audit.

## 21. Worked incident: auth failure masked as not found

Runtime token lacked repository pull scope. Registry returned response interpreted as `manifest unknown`.

```text
digest exists
+ principal cannot access repository
→ client sees not-found-like symptom
```

Do not conclude content deletion before testing exact endpoint, principal, token audience/scope and registry audit.

## 22. Worked incident: GC removed rollback

Release `10.3.7` ran by digest without tag. Retention marked it untagged and GC removed unique blobs.

```text
current containers continue from local snapshots
→ new node/rollback pull impossible
```

Recovery rebuilds/re-publishes only if source/build subject and trust evidence remain available; otherwise rollback capability was lost. Policy now consumes active/rollback digest inventory.

## 23. Competing hypotheses pri `manifest unknown`

```text
H1: wrong registry/repository path
H2: tag absent but digest exists
H3: index exists, selected platform missing
H4: referenced blob missing
H5: replica/mirror lag or stale negative cache
H6: GC/delete removed content
H7: token scope/auth hides object
H8: media type unsupported by client
H9: wrong explicit --platform
H10: existing nodes run only from local cache
```

Evidence:

```bash
docker context show
docker version
docker buildx imagetools inspect exact-reference --raw
docker image inspect local-reference
registry audit/replication/GC records
```

## 24. Evidence-preserving containment

Before repush/delete/tag repair:

- preserve source/destination index/manifests;
- capture tag mappings and timestamps;
- capture token identity/scope and audit;
- preserve replication queue and GC reports;
- inventory running index/platform digests;
- preserve signatures/SBOM/provenance subject mapping.

Re-pushing tag first can overwrite evidence about the mapping that caused incident.

## 25. Acceptance a forbidden paths

```text
publication graph is complete for every required platform
+ destination digests and evidence equal approved subject
+ deployment uses digest and records selected manifest
+ build/promotion/node/admin identities are least privilege
+ mirror lag and tag mapping are observable
+ GC consumes deployment/rollback/referrer inventory
+ clean-node pull succeeds for every platform
+ mutable-tag-only approval is rejected
+ incomplete-platform/evidence copy is rejected
+ second pull after failover selects same approved manifest
```

## 26. Kontrolné otázky

1. Prečo registry nie je iba image storage?
2. Aký rozdiel je medzi registry, repository, tag, digest a blob?
3. Čo tvorí complete multi-platform artifact graph?
4. Prečo tag nie je approval subject?
5. Aké identities treba oddeliť pri build/promotion/pull/admin?
6. Čo pull success preukazuje a čo nie?
7. Prečo mirror môže byť healthy a nekompletný?
8. Ako signatures/SBOM/scans viazať na index a platform manifests?
9. Prečo tag-only retention môže zmazať running digest?
10. Kedy je GC bezpečná?
11. Ako odlíšiš missing manifest od authorization failure?
12. Ako sa testuje forbidden incomplete promotion a second pull after failover?

## Glossary impact

Relevantné pojmy: container registry, repository, tag, digest, blob, manifest, image index, referrer, publication record, promotion, mirror, replication lag, pull-through cache, registry authorization, immutable release tag, channel tag, active digest inventory, retention, garbage collection a registry restore.

## Primárne zdroje

- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)
- [Docker Registry HTTP API V2](https://distribution.github.io/distribution/spec/api/)
- [Docker Registry authentication](https://distribution.github.io/distribution/spec/auth/token/)
- [Registry garbage collection](https://distribution.github.io/distribution/about/garbage-collection/)

<!-- KNOWLEDGE-NAVIGATION:START -->
[← Predchádzajúca: Images, layers a copy-on-write](images-layers-copy-on-write.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Container networking →](container-networking.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
