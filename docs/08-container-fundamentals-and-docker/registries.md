# Registries

Container registry je content-addressed distribution systém, ktorý spája build producerov, security evidence, deployment controllers a runtime consumers. Nie je to iba miesto, kam sa „pushne Docker image“.

Dominantný lifecycle:

```text
immutable build subject
→ complete OCI artifact graph
→ authenticated repository publication
→ digest, tags a related evidence
→ policy/retention/replication state
→ consumer authorization a reference resolution
→ exact graph pull a verification
→ runtime/deployment correlation
→ rescanning, rollback retention a safe garbage collection
```

Registry workflow je kompletný až vtedy, keď exact content schválený pri publication zostáva dostupný, overiteľný a korelovateľný s platform-specific artifactom, ktorý runtime skutočne spustil.

## 1. Atlas release subject

Atlas Payments publikuje release `3.13.0`:

```text
source commit: C417
builder identity: atlas-build-prod
OCI index digest: IDX313
linux/amd64 manifest: MAMD313
linux/arm64 manifest: MARM313
SBOM subject: SBOM313
provenance subject: PROV313
signature subject: SIG313
source registry: registry.build.example/atlas/payments
production registry: registry.prod.example/atlas/payments
release tag: 3.13.0
channel tag: stable
```

Deployment record nesmie obsahovať iba `stable`. Potrebuje aspoň:

```text
registry + repository
index digest
selected platform manifest digest
platform
verification policy/verdict
promotion generation
deployment/runtime identity
```

## 2. Registry, repository a content graph

Rozlišuj:

- **registry** — distribution API, identity a storage boundary;
- **repository** — namespace pre manifests, tags a access policy;
- **descriptor** — edge obsahujúci media type, digest a size;
- **manifest alebo index** — graph root;
- **blob** — content-addressed config alebo layer;
- **tag** — mutable human-readable pointer;
- **digest** — immutable content identity;
- **referrer** — subject-bound related artifact, napríklad signature alebo SBOM.

Reference:

```text
registry.prod.example/atlas/payments:3.13.0
registry.prod.example/atlas/payments@sha256:IDX313
```

Tag a digest majú odlišné lifecycle-y. Tag môže meniť mapping; digest identifikuje konkrétny manifest content.

## 3. Complete artifact graph

Release nie je jeden manifest. Multi-platform graph môže obsahovať:

```text
IDX313
├── MAMD313
│   ├── config AMD
│   └── layer blobs
├── MARM313
│   ├── config ARM
│   └── layer blobs
├── SIG313
├── SBOM313
└── PROV313
```

Complete publication contract definuje:

- required platform manifests;
- configs a layers reachable z každého manifestu;
- signatures, SBOM a provenance;
- media types a compression support;
- policy verdicty;
- read-back verification;
- promotion a retention scope.

Green push jedného manifestu nie je dôkaz complete release-u.

## 4. Publication lifecycle

Bezpečný push:

```text
producer authenticates
→ repository/action authorization
→ upload missing blobs
→ verify blob digest a size
→ publish platform manifests
→ publish index
→ publish subject-bound evidence
→ assign immutable release tag
→ read back exact graph
→ create publication record
```

Manifest sa publikuje až po dostupnosti referenced blobs. Producer má potvrdiť read-after-write podľa consistency modelu registry alebo replica vrstvy.

Publication identity nemá automaticky dostať delete, retention-admin alebo registry-admin oprávnenia.

## 5. Authentication a authorization

Registry access rozhoduje nad:

```text
principal
+ registry/repository
+ action
+ token audience/scope
+ trust boundary
+ time
```

Typické actions:

- pull;
- push/blob upload;
- manifest/tag mutation;
- related-artifact publication;
- delete;
- policy/retention administration.

Odporúčané oddelenie:

```text
build identity → push konkrétneho repository
promotion identity → read source + push destination
production node identity → pull konkrétneho repository
audit/scanner identity → read manifests/blobs/referrers
registry admin → výnimočné policy a recovery operácie
```

Long-lived shared password v každom node-e rozširuje blast radius a sťažuje revocation.

## 6. Tag resolution a approval subject

Tag môže slúžiť na discovery:

```text
3.13.0 → IDX313
```

Approval však musí byť viazaný na digest subject. Inak vzniká TOCTOU race:

```text
scan tag stable → IDX313
→ tag sa prepíše na IDX314
→ deploy stable
→ runtime spustí neschválený content
```

Safe transition:

```text
resolve tag once
→ record digest
→ verify evidence pre digest
→ deploy exact digest
```

Release tag immutability znižuje race, ale nenahrádza digest v deployment recorde.

## 7. Platform selection

Pri indexe musí consumer zachytiť obe identity:

```text
index digest IDX313
→ platform selection linux/arm64
→ selected manifest MARM313
```

Scanner, runtime a incident query môžu pracovať s rozdielnymi graph nodes. Bez explicitného edge-u index → selected manifest môže vulnerability correlation zlyhať.

Platform contract zahŕňa viac než `os/architecture`: variant, CPU features, kernel/runtime compatibility a podporované media/compression formats.

## 8. Pull a consumption lifecycle

Runtime pull:

```text
consumer workload identity
→ repository pull authorization
→ resolve exact index/manifest digest
→ select platform manifest
→ fetch config a missing layers
→ verify digest a size
→ verify signatures/provenance/policy
→ unpack do snapshotteru
→ create runtime subject
→ record deployed index + platform digest
```

Pull success neznamená unpack, runtime create alebo application readiness success. Registry evidence končí na distribution boundary; ďalšie chapters pokračujú snapshot a runtime lifecycle-om.

## 9. Promotion

Promotion má preniesť ten istý schválený content, nie ho rebuildnúť:

```text
verified source graph
→ destination authorization
→ copy all required manifests/blobs/referrers
→ verify destination digests
→ evaluate destination policy
→ publish promotion record
```

Ak destination používa transformáciu, napríklad recompression meniacu manifest digest, promotion potrebuje explicitný source-to-destination mapping a nové evidence. Tvrdenie „rovnaký image“ bez digest relation nestačí.

## 10. Referrers a trust evidence

Signature, SBOM, provenance a vulnerability report majú vlastnú identity a freshness.

Trust verdict môže vyžadovať:

```text
subject digest matches
+ signer/issuer identity allowed
+ provenance source a builder allowed
+ required platform inventory complete
+ report schema valid
+ scanner/database freshness acceptable
+ exception valid and unexpired
```

Digest dokazuje content identity, nie dôveryhodnosť, bezpečnosť alebo application readiness.

Copy tool alebo destination registry môže image preniesť bez referrers. Promotion pipeline musí kontrolovať expected evidence inventory, nie iba manifest availability.

## 11. Scanning a continuous reassessment

Scan subject:

```text
platform manifest digest
+ artifact graph
+ scanner/version
+ vulnerability database generation
+ scope
+ report/verdict
```

Multi-platform release potrebuje coverage všetkých podporovaných manifests. Scan iba amd64 variantu nehovorí nič o arm64 layers.

Nová CVE môže vzniknúť po deploymente. Registry alebo security platforma preto potrebuje:

```text
new advisory/database
→ identify affected stored digests
→ correlate deployed platform manifests
→ risk decision
→ rebuild/redeploy/revoke support
```

## 12. Repository a tenancy boundary

Repository naming má vyjadrovať ownership a authorization, nie iba estetiku.

Contract:

```text
organization/team
application/component
producer identities
consumer identities
retention/replication policy
trust policy
incident owner
```

Environment-specific repositories môžu byť legitímne, ak tvoria odlišnú authorization alebo air-gap boundary. Nemajú však ospravedlniť rebuild rovnakého release-u pre každý environment.

## 13. Replication a mirrors

Replica/mirror má vlastný state:

```text
source generation
→ replication queue
→ destination manifests/blobs/referrers
→ policy/access parity
→ read availability
```

Sleduj:

- replication lag;
- digest consistency;
- partial graph;
- tag a delete propagation;
- referrer support;
- authorization parity;
- failover a failback behavior.

Replica bez restore/failover testu je nepotvrdená recovery hypotéza.

## 14. Pull-through cache

Cache pridáva ďalšiu resolution boundary:

```text
client reference
→ cache lookup
→ cached tag/digest mapping alebo upstream fetch
→ cached graph
→ client pull
```

Mutable tag môže mať rozdielny obsah v rôznych cache locations. Bezpečný build/deploy používa upstream digest identity a zaznamenáva, odkiaľ bol content získaný.

Cache musí mať policy pre:

- freshness a revalidation;
- upstream trust;
- eviction;
- malicious/stale content;
- rate limits;
- vulnerability rescanning;
- audit.

## 15. Retention a rollback inventory

Retention nemá rozhodovať iba podľa tags. Digest môže byť:

- aktívne deployed;
- potrebný pre rollback;
- referencovaný indexom;
- subjectom signatures/SBOM;
- auditne alebo právne retained;
- používaný air-gapped environmentom;
- lokálne cached, ale nie bezpečne obnoviteľný.

Safe deletion input:

```text
registry reachability graph
+ active deployment inventory
+ rollback/support window
+ referrer relationships
+ replication/air-gap dependencies
+ legal retention
```

Policy „delete untagged after 7 days“ môže odstrániť digest-only deployment, ak registry nemá external deployment inventory.

## 16. Garbage collection

GC transition:

```text
freeze alebo coordinate writers
→ build consistent reachability graph
→ identify unreachable blobs/manifests
→ protect uploads, leases a referrers
→ dry-run/report
→ delete
→ verify retained subjects a rollback pull
→ audit reclaimed content
```

Tag deletion odstráni pointer. Blob deletion nastáva až vtedy, keď content nie je reachable podľa platného graphu a policy.

Concurrent push/GC bez coordination môže odstrániť blob, ktorý ešte nebol pripojený k manifestu.

## 17. Availability a disaster recovery

Registry outage môže zastaviť:

- nový node pull;
- autoscaling;
- rollout;
- rollback na necached digest;
- build/promotion;
- trust evidence lookup;
- incident rebuild.

Recovery plan obsahuje:

- retained immutable release inventory;
- regionálne replicas alebo export;
- backup metadát a content store-u;
- key/identity recovery;
- clean restore test;
- DNS/client failover;
- post-failover digest a policy verification.

Node cache je performance/availability layer, nie registry backup.

## 18. Air-gapped promotion

Air-gap package potrebuje:

```text
complete platform graph
+ subject-bound signatures/SBOM/provenance
+ vulnerability/policy evidence
+ source and destination digest ledger
+ chain of custody
+ malware scanning
+ destination read-back verification
```

Ručný tar bez graph manifestu môže stratiť platform variant, referrers alebo provenance.

## 19. Worked failure: release tag bol prepísaný po approval

Security schválila `stable → IDX313`. Build identity mala stále právo tag prepísať a nastavila `stable → IDX314`.

```text
approval subject = tag snapshot v čase T1
→ mutable mapping sa zmení
→ deployment resolve v čase T2
→ runtime spustí IDX314
→ approval evidence patrí IDX313
```

Root cause je tag použitý ako immutable decision subject. Recovery: zastaviť rollout, zistiť running platform digests, overiť alebo odstrániť IDX314, obnoviť exact approved digest a zaviesť immutable release tags plus digest deployment.

## 20. Worked failure: promotion preniesla iba amd64

Copy job preniesol `MAMD313` a priradil mu tag `3.13.0`, ale nepreniesol index ani arm64 manifest.

```text
amd64 pull succeeds
→ arm64 node resolveuje reference
→ required platform manifest chýba
→ autoscaling zlyhá iba v arm64 poole
```

Promotion acceptance musí kontrolovať expected platform inventory a complete graph, nie jeden successful pull.

## 21. Worked failure: referrers sa stratili

Image graph sa preniesol do production registry, ale signature a SBOM zostali v build registry.

```text
content digest exists
→ production trust policy hľadá subject-bound evidence
→ evidence inventory je prázdny
→ operator policy dočasne vypne
→ unsigned deployment prejde
```

Missing evidence je fail-closed alebo explicitný incomplete verdict, nie dôvod policy obísť.

## 22. Worked failure: GC odstránilo rollback digest

Release `3.12.4` bol deployed podľa digestu bez tagu. Retention job vyhodnotil manifest ako untagged a GC odstránilo jeho unique blobs.

```text
runtime stále beží z local snapshotu
→ incident vyžaduje nový node alebo rollback
→ registry digest už nie je pullable
→ recovery capacity je nižšia než deployment inventory tvrdí
```

GC potrebuje external active/rollback inventory a post-GC pull verification reprezentatívnych retained digests.

## 23. Causal troubleshooting walkthrough: autoscaling nodes hlásia `manifest unknown`

Existujúce Atlas instances bežia. Nové nodes nevedia pullnúť release `IDX313`; časť regiónov funguje a časť vracia `manifest unknown`.

### 1. Zafixuj registry subject

Zaznamenaj:

- registry/repository a endpoint/region;
- requested tag alebo digest;
- index a platform manifest digests;
- client platform;
- authentication principal, token audience/scope;
- replication generation/lag;
- retention/GC timeline;
- expected graph a referrers;
- existing node content/snapshot identity.

### 2. Súťažiace hypotézy

1. Client používa nesprávny repository path.
2. Tag chýba, ale digest existuje.
3. Index existuje, no platform manifest alebo blob chýba.
4. Replica ešte nie je synchronizovaná.
5. GC odstránilo unreachable content.
6. Promotion preniesla iba jednu platformu.
7. Pull-through cache drží stale negative result.
8. Authz skrýva object ako `not found`.
9. Media type/referrer policy odmieta subject.
10. Existing nodes bežia iba z local cache po registry deletion.

### 3. Diskriminačné observation points

- HEAD/GET exact digest na source a každej replica;
- tag-to-digest mapping;
- index descriptors a expected platform inventory;
- blob existence, size a digest;
- token scope a registry audit;
- replication queue/generation;
- retention/GC deletion report;
- cache freshness/negative cache;
- existing runtime selected manifest a local content store.

### 4. Containment

Pozastav scale-down existujúcich healthy instances a ďalší GC. Zastav rollout, ktorý by vyžadoval unavailable content. Zachovaj registry audit a local cached artifacts.

### 5. Recovery

- wrong path/reference → oprav deployment contract;
- partial graph → republish z trusted source a read-back verify;
- replication lag → route na complete region alebo dokonči replication;
- GC deletion → restore exact digest z verified replica/export, nie rebuild pod rovnakou identity;
- authz → oprav least-privilege pull scope;
- stale cache → invalidate/revalidate exact digest;
- missing platform → publish successor complete index a update approved subject.

### 6. Over pôvodný outcome

Na clean reprezentatívnych amd64 aj arm64 nodes over exact digest pull, trust policy, unpack, runtime start, readiness a deployment-record correlation. Potvrď rollback digest inventory.

### 7. Posuň control skôr

Pridaj complete-graph read-back gate, replication SLO, clean-node pull tests, active/rollback digest inventory a GC preconditions.

## 24. Referenčné pravidlá

- Registry je content graph, identity a policy boundary.
- Repository namespace je authorization a ownership contract.
- Tag je mutable pointer; deployment/approval subject je digest.
- Index a selected platform manifest sú samostatné identity.
- Green push neznamená complete multi-platform graph.
- Promotion prenáša exact content a subject-bound evidence.
- Missing trust evidence nie je clean pass.
- Scan report je digest-, platform-, scanner- a time-bound evidence.
- Runtime pull identity má byť narrow a short-lived.
- Replica/mirror potrebuje integrity, lag a failover verification.
- Cache nesmie byť jediný source of truth pre mutable tag.
- Retention potrebuje active deployment a rollback inventory.
- Tag deletion nie je blob deletion.
- GC je coordinated reference-graph mutation.
- Registry backup/recovery musí byť testovaný exact pullom.

## 25. Kontrolné otázky

1. Čo tvorí registry publication subject?
2. Ako sa líši tag, index digest a platform manifest digest?
3. Čo znamená complete OCI artifact graph?
4. Prečo build, promotion a runtime identity potrebujú odlišné scopes?
5. Ako sa overí, že promotion zachovala referrers?
6. Prečo scan jedného platform manifestu nepokrýva celý index?
7. Aké external informácie potrebuje retention a GC?
8. Prečo existing running container nedokazuje registry availability?
9. Ako sa líši replica, mirror a pull-through cache failure?
10. Aké observation points lokalizujú `manifest unknown` medzi reference, authz, replication a GC?

## Glossary impact

Relevantné pojmy: registry publication subject, repository authorization boundary, complete OCI artifact graph, tag-resolution boundary, selected platform manifest, subject-bound evidence inventory, promotion generation, registry consumer subject, active deployment digest inventory, rollback digest inventory, replication generation, negative cache, GC reachability snapshot a registry recovery pull test.

## Oficiálna dokumentácia

- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)
- [Docker Registry overview](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-registry/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Images, layers a copy-on-write](images-layers-copy-on-write.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Container networking →](container-networking.md)
<!-- KNOWLEDGE-NAVIGATION:END -->