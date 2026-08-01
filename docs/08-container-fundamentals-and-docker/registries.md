# Registries

Container registry je distribučný systém pre content-addressed artifacts. Build pipeline doň publikuje manifests, image indexes, configs a layer blobs. Runtime ich neskôr resolve-ne, stiahne a overí podľa digestov. Security nástroje môžu k rovnakému subjectu pripojiť SBOM, provenance, podpis alebo vulnerability report. Registry preto nie je iba „server, kam sa pushne Docker image“. Je to spojovací bod medzi buildom, release rozhodnutím a produkčným runtime-om.

Budeme sledovať repository `registry.example.com/atlas/payments-api`. Vývojár používa tag `1.4.2`, pipeline vytvorí multi-platform index a produkcia nakoniec konzumuje immutable digest. Na tomto toku sa ukáže rozdiel medzi registry, repository, tagom, manifestom, blobom a release identity.

## 1. Registry a repository nie sú to isté

Registry je služba alebo deployment, ktorý obsluhuje distribution API. V jednej registry môže existovať veľa repositories:

```text
registry.example.com
├── atlas/payments-api
├── atlas/orders-worker
├── platform/debug-tools
└── base-images/go-runtime
```

Repository je namespace pre tags a manifests konkrétneho artifact family. Reference:

```text
registry.example.com/atlas/payments-api:1.4.2
```

obsahuje hostname registry, repository path a tag. Reference s digestom:

```text
registry.example.com/atlas/payments-api@sha256:<digest>
```

viaže repository na konkrétny manifest alebo image index content.

Rovnaký digest blobu môže registry fyzicky deduplikovať naprieč repositories, ale authorization a retention sa stále často rozhodujú na repository alebo project hranici.

## 2. Čo sa pri pushi skutočne publikuje

Buildx multi-platform push nevytvára jeden veľký súbor. Publikuje graph:

```text
image index
├── amd64 manifest
│   ├── image config
│   └── layers
└── arm64 manifest
    ├── image config
    └── layers
```

Klient najprv overuje, ktoré blobs registry už má. Chýbajúce blobs uploadne. Potom publikuje platform manifests a napokon image index alebo tag association.

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag registry.example.com/atlas/payments-api:1.4.2 \
  --provenance=mode=max \
  --sbom=true \
  --push \
  .
```

Úspešný exporter verdict znamená, že BuildKit dokončil publication flow podľa svojho pozorovania. Pri timeout-e alebo strate response však môže byť výsledok unknown. Registry mohla mutation vykonať, hoci klient nedostal potvrdenie. Správna ďalšia operácia je read-back, nie automaticky nový build.

```bash
docker buildx imagetools inspect \
  registry.example.com/atlas/payments-api:1.4.2
```

## 3. Tag je pomenovaný pointer

Tag pomáha ľuďom a automation pracovať s názvami ako `1.4.2`, `main` alebo `stable`. Samotný tag však nie je content identity. Ak registry policy dovolí mutation, tag možno presmerovať na iný digest.

```text
čas T1: 1.4.2 → digest D1
čas T2: 1.4.2 → digest D2
```

Pipeline môže naskenovať D1, ale production pull o hodinu neskôr získa D2. Všetky joby pritom môžu v logoch používať rovnaký text `payments-api:1.4.2`.

Bezpečnejší release tok používa tag ako discovery alebo user-friendly metadata, ale zachová observed digest:

```bash
image_ref="registry.example.com/atlas/payments-api:1.4.2"
docker buildx imagetools inspect "$image_ref"
```

Release manifest potom uloží:

```yaml
image:
  repository: registry.example.com/atlas/payments-api
  tag: 1.4.2
  indexDigest: sha256:<exact-index-digest>
```

Deployment používa repository s digestom. Tag môže zostať pre navigáciu, ale runtime identity je immutable.

## 4. Authentication a authorization

Registry authentication odpovedá na otázku, kto klient je. Authorization rozhoduje, čo smie vykonať nad konkrétnym repository. Typické oprávnenia sú pull, push a delete.

Release builder potrebuje write do úzkeho repository. Production runtime potrebuje iba pull. Scanner môže potrebovať pull a publication reportov do samostatného evidence repository. Developer laptop nemá automaticky dostať delete alebo production push.

```text
untrusted PR job
→ bez registry push credentials

protected build job
→ push iba do candidate namespace

release promotion identity
→ tag alebo manifest mutation v production repository

production runtime identity
→ read-only pull

registry administrator
→ policy, retention a recovery
```

Long-lived shared password zvyšuje blast radius. Preferované sú short-lived alebo workload-bound credentials a repository-scoped permissions. Credential v Docker config file je citlivý secret a nemá sa commitovať ani ukladať do build contextu.

## 5. TLS a registry trust

Registry prenáša executable artifacts a metadata, preto musí klient overiť server identity. Private registry s internou CA vyžaduje správne distribuovaný trust chain.

Vypnutie TLS verification alebo označenie registry ako insecure môže vyriešiť lokálny test, ale odstraňuje ochranu proti man-in-the-middle a nesprávnemu endpointu. Trvalá oprava je správny certificate, hostname a trust distribution.

Pri pull chybe rozlišuj:

```text
DNS alebo routing failure
TLS hostname/CA failure
authentication failure
authorization scope failure
manifest unknown
blob unknown
rate limit
platform selection failure
```

Jedna všeobecná hláška v orchestrátore môže skrývať viac vrstiev. Priamo testuj registry endpoint a exact reference z rovnakého network a identity contextu ako runtime.

## 6. Immutability policy

Registry môže zakázať prepísanie vybraných tags alebo deletion artifacts. Immutability znižuje riziko, že už schválená verzia začne označovať iné bytes.

Dobrý model môže byť:

```text
candidate tags
→ mutable počas build flowu

release tags 1.4.2
→ immutable po publication

production deployment
→ digest-pinned
```

Aj immutable tag však nie je náhradou za digest evidence. Registry administrator môže policy zmeniť, artifact možno skopírovať do inej registry a multi-platform platform manifests treba stále explicitne inventarizovať.

## 7. Retention a garbage collection

Registry storage obsahuje manifests a blobs s referenciami medzi objektmi. Odstránenie tagu nemusí okamžite odstrániť manifest ani layer blobs. Retention policy môže odstrániť untagged manifests až po určitej dobe. Garbage collection potom uvoľní blobs, ktoré už nemajú živé referencie podľa implementácie registry.

Nebezpečná policy môže odstrániť artifact, ktorý už nemá tag, ale production ho stále používa digestom. Registry preto potrebuje deployment inventory alebo minimálnu retention dobu zodpovedajúcu rollback a incident-recovery oknu.

Pred destructive cleanupom treba vedieť:

```text
ktoré digesty sú nasadené
ktoré digesty sú rollback candidates
ktoré artifacts patria otvoreným incidentom
ktoré SBOM/provenance/signature objects na ne odkazujú
ktoré mirrors alebo air-gapped prostredia ich potrebujú
```

Retention podľa veku tagu bez týchto väzieb môže zničiť schopnosť reprodukovať alebo obnoviť starší release.

## 8. Replication a mirroring

Viac registry locations môže znižovať latency, podporovať disaster recovery alebo air-gapped prostredia. Replication však pridáva ďalšiu generation boundary.

```text
source registry digest D1
→ replication request
→ destination blobs a manifests
→ destination read-back D1
→ consumer switch
```

Úspešný replication job nepreukazuje, že destination tag ukazuje na správny digest ani že všetky attached artifacts boli prenesené. Overuj destination index digest a platform inventory.

Pri air-gapped promotion sa nesmie rebuildovať „rovnaký source“ v cieľovom prostredí, ak cieľom je promotion už overeného artifactu. Rebuild môže použiť inú base image, dependencies alebo builder. Prenáša sa exact image graph a jeho evidence.

## 9. Signatures, SBOM a provenance

Security evidence musí byť viazaná na immutable subject. Podpis tagu bez zachovania digestu je slabý, pretože tag sa môže presunúť. SBOM musí patriť konkrétnemu image alebo platform manifestu. Provenance má identifikovať source, builder a build inputs pre artifact, ktorý runtime skutočne používa.

```text
source commit C
→ builder B vytvorí image index D
→ provenance subject D
→ SBOM pre platform manifests
→ signature alebo attestation
→ policy decision nad D
→ deployment digest D
```

Ak scanner spracuje iba amd64 manifest, evidence inventory musí explicitne označiť chýbajúci arm64 verdict. Absencia reportu nie je PASS.

Attestations môžu byť uložené v registry ako ďalšie OCI artifacts pripojené k image subjectu. Registry retention a replication preto musia zachovať nielen root image, ale aj relevantný evidence graph.

## 10. Pull lifecycle na runtime node

Keď Docker Engine dostane digest-pinned reference, najprv resolve-ne manifest alebo index. Pri indexe vyberie platform manifest pre aktuálny node. Potom stiahne chýbajúci config a layers, overí digesty, unpackne snapshot a až následne môže vytvoriť container.

```text
reference
→ registry authorization
→ index alebo manifest
→ platform selection
→ config a layer blobs
→ digest verification
→ unpack/snapshot
→ container create
```

`ImagePullBackOff` alebo pull failure preto vzniká ešte pred process startom. Application logs nemusia existovať. Diagnostika sa sústreďuje na reference, credentials, registry connectivity, platform a local image store.

## 11. Incident: scanner bol zelený, produkcia stiahla iný image

Atlas publikoval tag `payments-api:1.4.2`. Scanner okamžite resolve-nul digest `D1` a vydal PASS. O desať minút neskôr rebuild job prepísal rovnaký tag na `D2`, pretože base image tag sa posunul. Production deployment stále používal tag.

```text
scan tagu → D1 → PASS
rebuild tagu → D2
production pull tagu → D2
```

Dashboard ukazoval zelený scan pre `1.4.2`, ale evidence a runtime nemali rovnaký subject. D2 obsahoval zraniteľnú knižnicu a odlišné arm64 manifest metadata.

Containment zastavil tag mutation a rollout. Tím read-backol registry history, identifikoval D1 a D2 a zistil deployed platform manifests. Nový release flow uložil digest hneď po publication, scanner a policy pracovali nad digestom a deployment používal `repository@digest`. Release tag sa stal immutable.

## 12. Incident: garbage collection odstránila rollback artifact

Produkcia používala digest D7, no tag `1.3.9` bol odstránený po vydaní `1.4.0`. Registry cleanup považoval untagged manifest za nepoužívaný a po krátkej retention ho odstránil. Keď nový release zlyhal, deployment controller nedokázal znovu pullnuť D7 na nahradený node.

Rollback plan predpokladal existenciu artifactu, ale registry lifecycle s tým nebol zosúladený. Oprava pridala deployed-digest inventory, explicitný rollback retention window a pravidlo, že artifact sa nesmie garbage-collectnuť, kým je nasadený alebo patrí podporovanému release-u.

## 13. Praktický registry audit

Pri audite jedného release-u začni immutable reference a platform inventory:

```bash
image="registry.example.com/atlas/payments-api@sha256:<index-digest>"
docker buildx imagetools inspect "$image"
docker buildx imagetools inspect "$image" --raw > index.json
jq -r '.manifests[] | [.platform.os,.platform.architecture,.digest] | @tsv' index.json
```

Potom porovnaj:

```text
publikovaný index digest
scan subject digests
SBOM/provenance subject digests
signature subject
deployment desired reference
runtime observed image digest
registry retention status
```

Pri mutable tagu vždy zaznamenaj čas read-backu. Výrok „tag ukazuje na D1“ je observation pre konkrétny okamih, nie trvalá vlastnosť.

## Čo si z kapitoly odniesť

Registry ukladá a distribuuje content-addressed graph manifests, configs, layers a ďalších OCI artifacts. Repository organizuje artifacts a authorization scope. Tag je pomenovaný pointer. Digest je immutable content identity.

Dôveryhodný release používa úzke credentials, TLS, registry read-back, immutable release subject a deployment correlation. Retention, garbage collection, replication a mirroring musia rešpektovať nasadené a rollback digesty aj pripojené evidence. Zelený push alebo scan bez väzby na deployed digest nie je production proof.

## Primárne zdroje

- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)
- [Docker Registry API](https://docs.docker.com/reference/api/registry/latest/)
- [Image digests](https://docs.docker.com/dhi/core-concepts/digests/)
- [Buildx imagetools inspect](https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/)
- [Docker login](https://docs.docker.com/reference/cli/docker/login/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Images, layers a copy-on-write](images-layers-copy-on-write.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Container networking →](container-networking.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
