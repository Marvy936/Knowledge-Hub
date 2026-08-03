# Artifact stores

Artifact store je durable úložisko pre väčšie výstupy ML operácií: model weights, checkpoints, exported modely, evaluation reports, plots, datasets, resolved configuration, environment lockfiles alebo evidence bundles. Nie je to synonymum experiment trackeru ani Model Registry. Tracker a Registry typicky uchovávajú metadata a references; artifact store uchováva bytes, bez ktorých sa model nedá načítať, reprodukovať ani auditovať.

Atlas Payments pokračuje incidentom `MLOPS-PAY-91`. Training run bol v MLflow stave `FINISHED`, Registry version ukazovala na `runs:/.../model` a deployment pipeline dostala platný model URI. Pri canary štarte však tri Pody model načítali a dva zlyhali na chýbajúcom súbore `preprocessor.pkl`. Metadata backend bol konzistentný, ale artifact upload skončil po network timeout-e. Jeden worker mal kompletný lokálny cache, takže smoke test prešiel; remote artifact directory bola partial. Tím zamieňal existenciu run recordu za durability kompletného model package.

## 1. Dominantný artifact lifecycle

Artifact lifecycle začína v execution workspaci a končí až po durable publication, read-backu a retention closure. Zápis súboru na lokálny disk workera ešte nevytvára publikovaný artifact. Upload request môže skončiť neznámym výsledkom, object store môže prijať iba časť multi-file package a metadata pointer môže vzniknúť skôr než všetky bytes.

```text
training alebo evaluation operation
→ local temporary outputs
→ package manifest a checksums
→ upload do staging prefixu
→ object-level durability read-back
→ atomic publication pointer alebo committed manifest
→ tracker/registry reference
→ fresh-client download a load test
→ retention, replication, backup a garbage collection
```

Poradie je dôležité. Registry alebo tracker nemá publikovať candidate reference na nekompletný prefix. Pri multi-file modeli sa najprv uploadnú immutable objects, následne sa overia checksums a až potom sa zverejní committed manifest. Consumer číta manifest, nie zoznam objektov v mutable adresári.

## 2. Backend store oproti artifact store

MLflow rozdeľuje tracking state na backend store a artifact store. Backend store drží run ID, experiment, parameters, metrics, tags, timestamps a model metadata. Artifact store drží veľké files. SQL transaction v backend databáze nemôže atomicky commitnúť object upload v S3, Azure Blob alebo inom storage systéme. Vzniká distributed-operation boundary.

Run `FINISHED` môže teda existovať spolu s missing artifactom. Naopak, orphaned object môže zostať v artifact store po tom, čo metadata transaction zlyhala. Backup iba PostgreSQL databázy neobnoví model weights. Backup iba bucketu neobnoví experiment graph, aliases ani permissions.

```text
MLflow Tracking Server
├── backend store: experiments, runs, parameters, metrics, tags
└── artifact store: model directories, reports, files, checkpoints
```

Operational acceptance musí čítať obe authority. Metadata reference dokazuje intended location. Object HEAD/list a checksum dokazujú prítomnosť bytes. Model load smoke test dokazuje minimálnu použiteľnosť package. Inference parity dokazuje behavior v definovanej tolerance.

## 3. Exact artifact subject

Artifact subject potrebuje immutable identity, media/format contract, producer operation a complete manifest. Path ako `s3://ml-artifacts/models/payment-risk/latest/` je location pointer, nie artifact identity. Versionovaný path pomáha, ale až digest alebo storage-native immutable object version rozlišuje bytes.

```yaml
artifact_id: model-package-sha256:b8ae...7d22
artifact_type: mlflow-model-directory
producer_run_id: 6f7b8fa3b5ad4aaead859f1a5d771301
root_uri: s3://ml-artifacts-eu1/runs/6f7b.../model/
manifest_uri: s3://ml-artifacts-eu1/manifests/b8ae...7d22.json
manifest_digest: sha256:b8ae...7d22
files:
  - path: MLmodel
    size: 1842
    sha256: 15f2...aa10
  - path: model.pkl
    size: 18422031
    sha256: c028...37fa
  - path: preprocessor.pkl
    size: 418201
    sha256: 908e...62c1
  - path: requirements.txt
    size: 934
    sha256: e21a...1b40
encryption_key_generation: kms://ml-artifacts/key-v7
created_at: 2026-08-03T09:31:17Z
retention_class: production-candidate-24m
```

Root-directory digest musí používať canonical ordering a normalizované relative paths. Digest jedného weights file neidentifikuje celý inference package, ak preprocessing, code alebo dependencies žijú vedľa neho.

## 4. Artifact types a ich rozdielne guarantees

Model package je deployable unit s interface a environment metadata. Checkpoint je resumable training state a môže obsahovať optimizer, scheduler, scaler a RNG state. Evaluation report je evidence viazaná na model a dataset subject. Dataset artifact je väčšinou reference alebo bounded snapshot, nie automaticky vhodný obsah pre všeobecný tracking bucket. Plot je human-readable derivative, nie authoritative metric source.

Tieto typy majú rozdielne consumers a retention. Final production model môže potrebovať roky retention, intermediate checkpoints dni a debug logs týždne. Jeden globálny lifecycle rule môže zmazať artifact, ktorý Registry stále referencuje, alebo naopak držať obrovské HPO checkpoints bez business hodnoty.

Artifact metadata preto obsahuje `artifact_type`, ownera, lineage, sensitivity, retention a reachability class. Filename extension sama nestačí. Pickle file môže byť model aj arbitrary executable payload; consumer musí použiť approved loader a trust policy.

## 5. Local, shared filesystem a object storage

Local filesystem je jednoduchý pre single-user experimenty, ale worker-local path nie je shared durable authority. V containerized alebo autoscaled prostredí môže zmiznúť spolu s Podom. Shared NFS poskytuje POSIX semantics a jednoduché directory operations, no prináša shared bottleneck, permissions, locking a failure-domain trade-offs.

Object storage je bežný artifact backend pre scale a durability. Nemá sa však používať ako keby každý provider garantoval POSIX rename alebo atomic multi-file directory commit. Upload každého objectu je samostatná operation. Publication pattern preto používa immutable objects a manifest/pointer commit namiesto in-place update-u.

S3-compatible endpoint nemusí mať identické consistency, multipart, encryption alebo IAM semantics ako AWS S3. Compatibility test musí pokryť konkrétny provider, SDK a configuration, nie iba URI syntax `s3://`.

## 6. Proxied a direct artifact access

MLflow Tracking Server môže proxyovať artifact upload/download alebo klient môže pristupovať priamo k remote store podľa konfigurácie. Proxy mode centralizuje credentials a policy, no server nesie bandwidth, timeout a capacity. Direct mode škáluje data path mimo servera, ale training clients potrebujú storage credentials a network access.

```text
proxied:
client → Tracking Server → object store

direct:
client → Tracking Server pre metadata
client → object store pre artifact bytes
```

URI uložené pri experimente alebo modeli závisí od artifact-root konfigurácie v čase vytvorenia. Neskoršia zmena server configuration nemusí spätne presmerovať staré runs. Migration musí inventarizovať historical locations, skopírovať bytes, overiť checksums a aktualizovať references iba podporovaným spôsobom.

Credential boundary je odlišný. V proxy mode server identity potrebuje scoped access. V direct mode workload identity potrebuje write iba do vlastného staging prefixu a read podľa use case. Broad bucket credentials v notebooku zväčšujú blast radius aj exfiltration risk.

## 7. Atomic publication multi-file artifactu

Object store nemá jednu transaction pre celý model directory. Robustný writer používa staging prefix viazaný na operation ID, zapisuje objects idempotentne, vytvorí manifest, overí server-side metadata/checksum a až potom publikuje immutable commit object alebo Registry reference.

```text
staging/runs/<run-id>/<upload-id>/MLmodel
staging/runs/<run-id>/<upload-id>/model.pkl
staging/runs/<run-id>/<upload-id>/requirements.txt
commits/<package-digest>.json
```

Consumer nikdy nečíta `staging`. Najprv resolve-ne committed manifest a potom exact objects. Ak upload timeout-ne, writer read-backom zisťuje, ktoré objects existujú a zhodujú sa. Blind retry s rovnakým key a odlišnými bytes je zakázaný; buď je zápis idempotentný podľa digestu, alebo vznikne nový upload ID.

Pri multipart upload-e treba čistiť abandoned uploads, ale až po retention window pre incident evidence. Complete object existence sama nepreukazuje, že package manifest obsahuje všetky required files.

## 8. Checksums, integrity a authenticity

Transport TLS chráni connection, nie dlhodobú identity artifactu. Storage ETag nemusí byť univerzálny content hash, najmä pri multipart alebo provider-specific behavior. Platforma preto používa explicitný cryptographic digest nad každým fileom a canonical package manifestom.

Digest deteguje náhodnú alebo úmyselnú zmenu bytes, ale neidentifikuje dôveryhodného producera. Signature alebo provenance statement viaže digest na build/training identity, workflow a policy. Encryption at rest chráni confidentiality storage media; nie je integrity verdict ani authorization pre consumer.

Consumer overí manifest signature, allowed producer, artifact digest, expected format a interface pred deserializáciou. Pickle, cloudpickle a podobné formáty môžu vykonať code pri load-e, preto sa artifact z nedôveryhodného source nesmie načítať len preto, že checksum sedí s útočníkom publikovaným manifestom.

## 9. Encryption, identity a tenant isolation

Artifact store často obsahuje proprietary modely, training samples alebo evaluation slices s citlivými údajmi. Bucket alebo container policy musí oddeľovať writerov, read-only deployment identities, administrators a audit principals. Model serving workload nepotrebuje list alebo delete oprávnenie nad celým experiment bucketom.

Encryption key generation patrí do artifact metadata. Key rotation nesmie zmeniť logical artifact identity, ale musí zachovať decryptability počas retention. Cross-region replication potrebuje key a policy mapping; replika, ktorú disaster-recovery identity nevie decryptovať, nie je použiteľný recovery artifact.

Multi-tenant prefix bez enforcement nie je isolation. Authorization sa presadzuje storage policy, workload identity a prípadne brokered accessom. Presigned URL je dočasný bearer capability; jeho scope, expiry a logovanie musia zodpovedať sensitivity.

## 10. Retention, reachability a garbage collection

Artifact GC je graph problem. Object je reachable, ak ho referencuje active run, registered model, deployment release, rollback candidate, audit hold alebo incident. Delete podľa veku samotného runu môže odstrániť production model, ktorého Registry alias stále používa.

```text
Registry alias champion
→ model version 17
→ logged model / run
→ package manifest
→ artifact objects
```

GC najprv vytvorí immutable inventory a reachability graph, potom označí candidates, aplikuje grace period a až následne maže. Po delete sa vykoná negative read-back a kontrola, že active references nezostali dangling. Object-lock alebo legal hold môže delete odmietnuť; workflow musí tento výsledok zaznamenať, nie predstierať cleanup.

Caches nie sú root authority. Fresh-environment restore bez cache je povinný test. Inak chýbajúci remote artifact zostane skrytý, kým sa workload nepremiestni na nový node.

## 11. Backup, replication a disaster recovery

Provider durability nie je úplný DR plán. Accidental delete, credential compromise, application bug alebo region-wide dependency failure môže zneprístupniť artifacts. DR inventory musí zahrnúť backend metadata, artifact bytes, manifests, Registry state, keys, policies a DNS/endpoints.

Replication lag určuje RPO. Obnovený bucket musí zachovať object paths alebo podporovanú reference migration. Restore acceptance načíta konkrétny production a rollback model v isolated environment-e, overí digest, signature, dependencies a representative prediction. Počet obnovených objektov nie je business acceptance.

## 12. Failure walkthrough incidentu MLOPS-PAY-91

Atlas najprv videl tri healthy Pody a predpokladal transient node problém. Request-correlated logs však ukázali, že healthy Pody čítali model z local cache. Fresh Pod s prázdnym cache vždy zlyhal. MLflow backend evidoval run `FINISHED` a artifact URI, no remote list neobsahoval `preprocessor.pkl`.

Upload log skončil timeoutom po odoslaní weights. Client následne uzavrel run bez required-artifact read-backu. Registry pipeline overila iba existenciu `MLmodel`. Root cause bol neatomický multi-file publication contract a cache-dependent smoke test, nie model framework ani Kubernetes scheduling.

Containment zastavil rollout a zakázal scale-down healthy cached Podov, aby sa zachovala serving continuity aj evidence. Candidate alias sa vrátil na predchádzajúcu model version. Chýbajúci package sa nedopĺňal ručne pod rovnakým digestom; training/export workflow vytvoril nový committed package a nový model version.

## 13. Recovery a acceptance

Component recovery overí kompletný manifest, object checksums, permissions a fresh download. Journey recovery načíta model v clean image a vykoná representative inference bez lokálneho cache. Business recovery potvrdí, že rollout používa nový package digest a downstream predictions/actions zostali v guardrails.

Pozitívny test publikuje package a načíta ho z fresh identity. Forbidden test odmietne Registry candidate bez committed manifestu alebo s mutable pathom. Unknown-outcome test preruší upload a vyžaduje read-before-retry. Corruption test zmení jeden byte a očakáva digest failure. Second-operation test publikuje ďalší package bez prepísania prvého a následne preukáže rollback loadability.

```bash
python verify_artifact.py \
  --manifest s3://ml-artifacts-eu1/manifests/b8ae...7d22.json \
  --require-signature \
  --fresh-cache-dir "$(mktemp -d)"

mlflow models predict \
  --model-uri s3://ml-artifacts-eu1/runs/6f7b.../model \
  --input-path tests/requests.json \
  --content-type json
```

Prvý command je organizačný verification surface; jeho implementácia musí resolve-nuť exact objects a digests. Druhý dokazuje model load a prediction pre test input. Ani jeden sám nepreukazuje production feature parity alebo business outcome.

## 14. Kontrolné otázky

1. Prečo `FINISHED` run nepreukazuje kompletný artifact upload?
2. Aký je rozdiel medzi artifact URI, object existence, package digest a loadability?
3. Prečo multi-file model potrebuje committed manifest?
4. Ako cache zakrýva broken durability a ktorý test to odhalí?
5. Ktoré references musí GC zahrnúť pred zmazaním artifactu?

## 15. Primárne zdroje

- [MLflow Artifact Stores](https://mlflow.org/docs/latest/self-hosting/architecture/artifact-store/)
- [MLflow Backend Stores](https://mlflow.org/docs/latest/self-hosting/architecture/backend-store/)
- [MLflow Tracking architecture](https://mlflow.org/docs/latest/tracking/)
- [MLflow Models](https://mlflow.org/docs/latest/ml/model)

Artifact store je data-plane authority pre bytes, nie celý production verdict. Jeho guarantees musia byť spojené s lineage, Registry, packaging, serving read-backom a business evidence.
