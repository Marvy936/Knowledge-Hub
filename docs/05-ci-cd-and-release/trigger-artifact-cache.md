# Trigger, artifact a cache

Trigger, artifact a cache patria do jedného delivery provenance chainu, ale majú úplne odlišnú autoritu. Trigger vytvára pipeline instance a určuje event, source a permission context. Artifact je autoritatívny immutable output, ktorý sa môže testovať, podpisovať a promovať. Cache je odstrániteľná výkonová optimalizácia. Ak cache začne rozhodovať o correctness alebo release identity, stala sa skrytým source of truth.

Najčastejšie incidents vznikajú pri zámene týchto rolí. Autentizovaný webhook ešte neznamená, že event má právo publikovať alebo deployovať. Úspešný cache restore neznamená, že obnovený obsah patrí current candidate-u. Artifact s názvom `release.zip` nie je immutable, pokiaľ nemá content identity, provenance a retention contract.

## 1. Dominantný event-to-artifact model

```text
authenticated event alebo authorized manual request
→ event deduplication a trust classification
→ exact source, target, candidate a workflow subject
→ permissions a runner trust selection
→ cache lookup alebo cold recompute
→ build a verification
→ immutable artifact publication
→ artifact-bound reports, SBOM, signature a provenance
→ retention, promotion, revocation alebo garbage collection
```

Trigger rozhoduje, prečo sa run začal a v akom trust contexte. Artifact rozhoduje, ktoré bytes sa ďalej používajú. Cache nesmie nahradiť ani jednu z týchto identít.

## 2. Exact trigger subject

Event subject má zachovať producer, delivery ID, event type, actor, source ref, target ref, received time a trust class:

```yaml
triggerSubject:
  provider: github
  eventType: pull_request
  deliveryId: 4d0a2b1f-8ef4-4c0a-a6ce-32aa27f72cb1
  actor: external-contributor
  sourceRepository: fork-user/payments
  sourceRef: refs/heads/fix-timeout
  sourceSha: 8e21b8d
  targetRepository: atlas/payments
  targetRef: refs/heads/main
  targetSha: 53d92af
  receivedAt: 2026-07-31T12:18:03Z
  trustClass: untrusted-fork
  workflowSha: 18ab442
```

`pull_request`, `push`, `schedule`, `workflow_dispatch`, tag a upstream trigger majú rozdielne security semantics. Fork PR môže obsahovať nedôveryhodný source. Tag môže byť mutable alebo vytvorený neautorizovaným actorom. Schedule nemusí reprezentovať current release candidate. Manual dispatch potrebuje identity, parameters a reason.

## 3. Event authentication, authorization a deduplication

Webhook signature dokazuje, že payload vytvoril držiteľ shared secretu alebo trusted provider. Nehovorí, či event smie publikovať artifact alebo deployovať production. Po cryptographic authentication nasleduje authorization podľa repository, actor, ref, environment a event type.

Pri diagnostike sa event payload parsuje bez vypisovania secretu:

```bash
jq '{action, repository:.repository.full_name, actor:.sender.login, sourceSha:.pull_request.head.sha, targetSha:.pull_request.base.sha}' event.json
```

Výstup preukazuje fields v prijatom JSON-e. Nepreukazuje, že payload prešiel signature validation ani že SHA stále existuje v trusted repository. Pipeline má fetch-núť exact objects a nepoužívať mutable branch checkout.

Delivery ID alebo vlastný idempotency key bráni duplicate pipeline creation:

```text
provider delivery ID
+ event type
+ repository
→ unique trigger record
```

Deduplication nesmie zlúčiť dva odlišné events s rovnakým source SHA, ak sa zmenil target, workflow alebo policy generation.

## 4. Trigger permissions a trust downgrade

Pipeline permission context sa nesmie odvodzovať iba z workflow file-u, pretože untrusted source môže workflow meniť. Bezpečný model vyberá trusted workflow revision z target repository a poskytne minimálne permissions podľa event classu.

```text
fork PR
→ read source, no secrets, no package write, no production network

internal PR
→ read source, bounded test resources

protected main push
→ candidate artifact publication

protected release tag alebo promotion record
→ environment-scoped deployment identity
```

Event z untrusted source sa nesmie „povýšiť“ tým, že maintainer pridá label, ak downstream job následne vykoná source-controlled script s production credentialom. Approval musí fixovať exact source/candidate a trusted execution plan.

## 5. Artifact ako immutable release output

Artifact má content identity a provenance. Môže byť OCI image, package, binary archive, migration bundle, SBOM, deployment manifest alebo signed release manifest. Filename alebo mutable tag je locator, nie identity.

```bash
sha256sum dist/payments-api.tar.gz > dist/payments-api.tar.gz.sha256
artifact_sha="$(cut -d' ' -f1 dist/payments-api.tar.gz.sha256)"
printf 'artifact_sha256=%s\n' "$artifact_sha"
```

Checksum preukazuje bytes konkrétneho local file-u. Nepreukazuje source, builder, platform ani absence malicious content. Provenance musí spojiť digest s candidate, build definition, dependencies a builder identity.

Pre OCI artifact:

```bash
ref='registry.atlas.example/payments-api:candidate-d94e1c6'
digest="$(crane digest "$ref")"
printf '%s@%s\n' "${ref%:*}" "$digest"
```

Resolved digest preukazuje current registry mapping v čase query. Mutable tag sa môže neskôr zmeniť; promotion record má ukladať digest reference.

## 6. Artifact publication a unknown outcome

Registry push alebo object upload môže dokončiť server-side a klient môže stratiť response. Blind retry môže vytvoriť duplicate metadata, prepis mutable tagu alebo rozdielne attestations. Po timeout-e sa najprv vykoná read-back podľa digestu alebo idempotency key-u.

```text
upload request
→ server may persist bytes
→ acknowledgement lost
→ client state UNKNOWN
→ query content digest a publication record
→ conclude committed / absent / conflicting
→ retry iba podľa verdictu
```

Successful upload response stále nepreukazuje, že všetky platform manifests, SBOM a signatures boli publikované. Release evidence inventory má explicitne uviesť expected referrers.

## 7. Cache ako odstrániteľná optimalizácia

Cache zrýchľuje dependency download, compilation alebo test preparation. Correctness contract musí platiť aj pri cache miss. Cache key obsahuje všetky inputs, ktoré ovplyvňujú obnovený obsah:

```text
operating system a architecture
+ toolchain digest
+ dependency lock digest
+ build flags
+ relevant source/config digest
+ cache schema version
→ cache key
```

Príklad:

```bash
lock_sha="$(sha256sum package-lock.json | cut -d' ' -f1)"
key="npm-linux-amd64-node22-${lock_sha}-v3"
printf 'cache_key=%s\n' "$key"
```

Key preukazuje, ktoré hodnoty script zahrnul. Nepreukazuje, že zoznam inputs je complete ani že cache backend vráti trusted content. Untrusted a trusted runs majú oddelené namespaces a write permissions.

## 8. Cache poisoning a trust direction

Ak fork PR môže zapísať cache, ktorú neskôr obnoví privileged release job, cache vytvára trust escalation. Content hash key nepomôže, ak attacker pozná key a backend povoľuje overwrite alebo prefix restore.

Bezpečný model používa:

- read-only trusted cache pre untrusted jobs alebo úplne oddelené namespace;
- immutable cache entries, ak backend podporuje;
- exact keys namiesto broad fallback prefixov pre privileged build;
- validation obnoveného obsahu;
- periodic cold builds;
- žiadne credentials, signed outputs ani final artifacts v cache.

Cache archive môže obsahovať symlinks, executable scripts alebo absolute paths. Restore mechanism musí chrániť workspace boundary.

## 9. Artifact versus cache versus report

Artifact je output určený na ďalší trusted lifecycle. Cache možno zahodiť. Report je evidence o execution a má vlastný subject. Jeden object sa nemá nazývať cache v build jobe a potom bez zmeny trust contractu promovať ako release artifact.

```text
cache
→ recomputable, best effort, no release authority

artifact
→ immutable, retained, provenance-bound, promotable alebo revocable

report
→ evidence producer + subject + oracle + result
```

Artifact retention a garbage collection sa viažu na release/support/recovery. Cache eviction smie ovplyvniť iba duration. Report retention musí podporovať audit a incident diagnosis.

## 10. Trigger loops a storm control

Pipeline môže sama commitovať generated file alebo tag, čo vyvolá ďalší trigger. Upstream pipeline môže retryovať webhook a vytvoriť duplicate downstream runs. Storm control potrebuje provenance-aware filtering, deduplication a rate limits.

```text
workflow-generated commit
→ marker alebo actor identity
→ trigger policy rozpozná expected automation
→ run iba relevantného graphu
```

Broad rule „ignore bot commits“ môže skryť legitímnu supply-chain mutation. Lepšie je rozlišovať operation type, changed paths a expected automation identity.

## 11. Connected incident `REL-PAY-67`

Fork PR zmenil code generator a CI cache key zostal založený iba na `package-lock.json`. Untrusted job zapísal generated client do shared prefix cache `payments-generated-*`. Neskorší protected tag pipeline obnovil najnovšiu prefix match, spustil build na trusted runneri a publikoval signed image.

```text
untrusted fork trigger
→ shared cache write
→ poisoned generated output
→ protected tag trigger
→ privileged cache restore
→ signed artifact publication
→ production promotion
```

Signature bola validná, pretože trusted builder skutočne podpísal bytes, ktoré vytvoril. Provenance tiež ukazovala trusted workflow, ale neobsahovala cache source a generated output lineage. Artifact bol kryptograficky dôveryhodný a obsahovo kompromitovaný.

Root cause bol nesprávny trust direction: odstrániteľná cache sa stala vstupom privileged artifact authority.

## 12. Recovery a acceptance verdict

Containment revokuje affected digest, zastaví promotions, zachová cache metadata a publication records a oddelí runner/cache credentials. Recovery vytvorí cold candidate build z pinned inputs, porovná generated output s reviewed source generatorom, publikuje nový digest a redeployuje po business canary.

Trigger/artifact/cache contract je prijatý iba vtedy, keď:

```text
event je authenticated, authorized a deduplicated
+ trust class určuje workflow a permissions
+ source/target/workflow subjects sú immutable
+ cache miss nemení correctness
+ untrusted write nevstupuje do trusted build namespace-u
+ artifact má digest, provenance a expected evidence inventory
+ publication timeout sa rieši read-backom
+ mutable tag sa nepoužíva ako promotion identity
+ revocation blokuje ďalší deploy
+ cold second build reprodukuje contract outcome
```

## 13. Troubleshooting flow

Pri podozrivom artifacte sleduj:

```text
trigger delivery a trust class
→ resolved source/target/workflow
→ runner permissions
→ cache key, namespace, writer a restored object
→ build inputs a output digest
→ publication acknowledgement/read-back
→ signature/provenance/report subjects
→ promotions a runtime digests
```

Competing hypotheses môžu byť spoofed event, duplicate delivery, wrong ref, mutable tag race, poisoned cache, stale fallback restore, artifact overwrite, incomplete multi-platform publication alebo report mismatch. Evidence-preserving containment nemá okamžite vymazať cache backend; metadata môže byť jediný dôkaz cross-run contamination.

## 14. Anti-patterny

### Každý trigger používa rovnaké permissions

Event type a source trust zásadne menia bezpečný capability set.

### Cache key iba podľa branch name

Branch je mutable a nezachytáva dependencies, toolchain ani flags.

### Release artifact uložený iba ako pipeline ZIP

Bez immutable identity, provenance a retention contractu sa nedá bezpečne promovať ani obnoviť.

### Validná signature ako proof čistého buildu

Signature potvrdzuje signer a subject. Ak trusted build spotreboval poisoned input, podpíše kompromitovaný artifact.

### Blind retry po upload timeout-e

Unknown outcome potrebuje read-back, inak môže retry prepísať locator alebo vytvoriť conflicting metadata.

## 15. Kontrolné otázky

1. Aký rozdiel je medzi trigger authentication a authorization?
2. Prečo source SHA bez target/workflow SHA nestačí?
3. Čo je authority artifactu a čo cache?
4. Čo preukazuje checksum a čo nepreukazuje?
5. Ako vzniká unknown publication outcome?
6. Ktoré inputs patria do cache key-u?
7. Prečo prefix restore môže byť nebezpečný?
8. Ako untrusted cache write kompromitoval trusted artifact v `REL-PAY-67`?
9. Prečo validná signature incident neodhalila?
10. Ako sa modeluje trigger deduplication?
11. Kedy artifact evidence expirovalo alebo sa revokuje?
12. Ako sa overí, že cold build nemení correctness?

## Glossary impact

Relevantné pojmy: trigger subject, delivery ID, event trust class, trigger authorization, trigger deduplication, immutable artifact, artifact locator, artifact provenance, publication unknown outcome, cache key, cache namespace, prefix restore, cache poisoning, cold recompute, report subject a artifact revocation.

## Primárne zdroje

- [GitHub Docs — Webhook events and payloads](https://docs.github.com/en/webhooks/webhook-events-and-payloads)
- [GitHub Docs — Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [GitLab Docs — CI/CD cache](https://docs.gitlab.com/ci/caching/)
- [GitLab Docs — Job artifacts](https://docs.gitlab.com/ci/jobs/job_artifacts/)
- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)
- [SLSA specification](https://slsa.dev/spec/)
- [Sigstore Cosign documentation](https://docs.sigstore.dev/cosign/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Pipeline, stage, job a runner](pipeline-stage-job-runner.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Environment a promotion →](environment-and-promotion.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
