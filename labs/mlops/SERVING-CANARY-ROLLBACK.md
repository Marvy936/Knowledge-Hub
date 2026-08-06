# MLOps serving, canary a rollback control-plane contract

Tento blok vytvára immutable subjects potrebné pred živým HTTP servingom. Neštartuje ešte container ani neposiela sieťový traffic. Oddeľuje však deployment identitu, routing state a rollback od mutable MLflow aliasu.

```text
release manifest
+ Registry evidence s exact numeric version
+ image digest
→ immutable deployment manifest
→ stable routing state
→ canary routing state
→ deterministic request assignment
→ compare-before-change update
→ rollback na exact predchádzajúci deployment
```

## Deployment manifest

Deployment manifest spája:

- canonical `release_id`,
- `candidate_id`, dataset a evaluation digest,
- exact source revision,
- model SHA-256,
- MLflow model name a numeric version,
- exact URI `models:/<name>/<version>`,
- Registry evidence ID,
- container image reference,
- immutable `sha256:<digest>`,
- service a generation identity.

`deployment_id` je SHA-256 canonical payloadu. Ak sa zmení Registry version, model digest, image digest, source revision alebo generation, vznikne iný deployment subject.

Mutable URI `models:/<name>@<alias>` je zakázané. Alias môže byť použitý iba počas control-plane rozhodnutia pred vytvorením deployment manifestu. Runtime a rollback používajú exact numeric version a digest.

## Routing state

Routing state obsahuje iba exact deployment IDs:

```text
stable_deployment_id
canary_deployment_id alebo null
canary_basis_points 0–10000
previous_routing_state_id
routing_state_id
```

Každá zmena je compare-before-change operácia. Caller musí uviesť `expected_current_state_id`. Ak medzitým routing zmenil iný actor, update sa odmietne bez vytvorenia nového authoritative state-u.

Canary weight používa basis points:

- `100` = 1 %,
- `1000` = 10 %,
- `2500` = 25 %,
- `10000` = 100 %.

Canary deployment bez nenulového trafficu a canary traffic bez deployment subjectu sú neplatné stavy.

## Deterministic routing

Request sa priradí podľa SHA-256 routing key:

```text
bucket = first_32_bits(sha256(routing_key)) mod 10000
bucket < canary_basis_points → canary
inak → stable
```

Rovnaký routing state a rovnaký key vždy vytvoria rovnaký výsledok. Výstup vracia:

- `routing_state_id`,
- hash routing key, nie jeho plaintext,
- bucket,
- stable/canary role,
- exact `deployment_id`, generation a `release_id`,
- model SHA-256,
- image digest.

Tento contract neimplementuje session affinity cookie, proxy, service mesh ani load balancer. Definuje deterministické rozhodnutie, ktoré tieto vrstvy môžu vykonať a auditovať.

## Rollback

Rollback nevykonáva nové MLflow alias resolution. Caller poskytne:

- current routing state,
- exact target stable deployment manifest,
- exact expected current routing-state ID.

Výsledný state nastaví target deployment ako stable, odstráni canary traffic a uloží previous routing-state ID. Stale rollback sa odmietne.

Rollback control-plane state ešte nepreukazuje, že workload, cache, schema alebo downstream side effects boli fyzicky obnovené. Živý serving blok musí doplniť health, traffic a prediction read-back.

## Testovaná hranica

Unit tests pokrývajú:

- deterministic deployment ID,
- exact Registry version a image digest,
- release/Registry candidate mismatch,
- canonical tamper detection,
- deterministic 10 % canary assignment nad 10 000 keys,
- stale routing update refusal,
- rollback na exact deployment subject,
- refusal chýbajúceho deployment manifestu.

## Ďalší blok

Na uzavretie serving gates ešte treba:

1. container image s exact artifact a dependency contractom,
2. image build a skutočný OCI digest,
3. dve lokálne HTTP serving generations,
4. positive a forbidden inference requests,
5. deterministic proxy alebo test driver používajúci routing state,
6. canary evidence pre obe generácie,
7. rollback a read-back, že traffic už nesmeruje na failed generation,
8. cleanup containers, images a runtime state.

Dovtedy Practical v1 položky `containerized inference`, `canary` a `rollback` zostávajú otvorené.
