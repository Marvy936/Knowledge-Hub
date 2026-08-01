# Semantic Versioning

Semantic Versioning je compatibility communication contract. Číslo `MAJOR.MINOR.PATCH` nevzniká podľa veľkosti diffu, počtu commitov ani subjektívneho pocitu autora. Vzniká porovnaním observable change s explicitne deklarovaným public API a s tým, čo existujúci consumer smie očakávať.

SemVer nepreukazuje, že release je bez defectov. `PATCH` môže obsahovať vážnu regresiu a `MAJOR` môže byť technicky kvalitný. Version decision vyjadruje intended compatibility boundary. Dôveryhodný release system musí túto boundary definovať, testovať a komunikovať cez source, artifacts, schemas, behavior a support policy.

## 1. Dominantný contract-to-version model

```text
declared public contract a supported consumers
→ exact candidate change
→ observable API/behavior/schema delta
→ compatibility analysis v relevantných dimensions
→ consumer a migration evidence
→ PATCH, MINOR alebo MAJOR verdict
→ immutable artifact/release publication
→ adoption, deprecation a support lifecycle
```

Version nie je property Git diffu. Internal refactor bez observable zmeny môže byť PATCH. Jeden riadok, ktorý odstráni enum value alebo zmení default retry behavior, môže byť MAJOR pre consumerov.

## 2. Exact compatibility subject

Atlas Payments definuje version decision record:

```yaml
compatibilitySubject:
  component: settlement-events
  previousRelease: 9.9.3
  previousManifestDigest: sha256:release993
  candidateRelease: 10.0.0-rc.4
  candidateManifestDigest: sha256:release1000rc4
  publicContracts:
    - openapi/payments-v7.yaml
    - protobuf/settlement/v18
    - event-schema/SettlementCreated-v18.json
    - cli/paymentsctl-v4
    - configuration/schema-v7.json
    - operational-metrics-contract-v3
  supportedConsumers:
    - payments-web-6.x
    - settlement-worker-9.x
    - partner-api-v7
    - reporting-consumer-v18
  decisionPolicySha: compat-policy-31
```

Public API môže zahŕňať viac než HTTP endpoints. Event schemas, CLI flags, config keys, database extension interfaces, exit codes, metric names a default behavior môžu byť compatibility surface, ak consumers na nich závisia.

## 3. SemVer pravidlá

Pre stable public API `1.0.0` a vyššie:

- **PATCH** — backward-compatible bug fix, ktorý nemení intended public contract;
- **MINOR** — backward-compatible functionality; existing supported consumers majú pokračovať bez povinnej zmeny;
- **MAJOR** — incompatible public API change.

Pre `0.y.z` SemVer povoľuje nestabilnejší model, ale organizácia stále potrebuje vlastnú compatibility policy. „Je to pre-1.0“ nie je ospravedlnenie pre nekomunikované breaking changes v production dependency.

Pre-release identifiers ako `10.0.0-rc.4` majú nižšiu precedence než stable `10.0.0`. Build metadata ako `+build.1844` nemení precedence a nemá byť používaná ako náhrada content digestu.

## 4. Public API inventory

SemVer funguje iba ak existuje inventory toho, čo je public. Atlas rozlišuje:

```text
protocol shape
→ endpoints, methods, fields, types, enums, events

behavior contract
→ defaults, ordering, retry, idempotency, error semantics

operational contract
→ config keys, CLI flags, exit codes, metrics a health semantics

extension contract
→ plugins, hooks, schemas a integration points

support contract
→ supported platforms, runtimes a dependency versions
```

Nie každý internal symbol je public. Naopak undocumented behavior môže byť de facto public, ak ho podporovaní consumers používajú a provider to dlhodobo toleruje. Consumer telemetry a support incidents pomáhajú inventory spresniť.

## 5. Structural API diff

OpenAPI diff môže odhaliť odstránený endpoint, required field alebo zmenu type-u:

```bash
oasdiff breaking \
  contracts/previous/openapi.yaml \
  contracts/candidate/openapi.yaml
```

Successful command bez findings preukazuje, že tool podľa svojej version a rules nenašiel podporované structural breaking changes. Nepreukazuje behavioral compatibility, correct examples, authorization semantics ani runtime implementation.

Pre Protobuf:

```bash
buf breaking proto \
  --against 'https://github.com/atlas/payments.git#branch=main,subdir=proto'
```

Tool môže odhaliť wire/source breaking changes podľa configured rules. Nepreukazuje, že event meaning, ordering alebo default behavior zostali kompatibilné.

## 6. Behavioral compatibility

Schema môže zostať rovnaká a behavior sa môže zlomiť. Príklady:

- API začne vracať položky v inom ordering-u;
- retryable error sa zmení na terminal;
- timeout default klesne z 30 s na 5 s;
- idempotency key scope sa zmení z tenant+operation na operation;
- event vznikne pred DB commitom namiesto po commite;
- config default povolí novú feature.

Behavioral contract potrebuje executable tests nad previous consumers alebo recorded interactions. Atlas spúšťa previous stable client proti candidate serveru a candidate client proti previous stable serveru tam, kde podporuje mixed-version interval.

```text
old client → new server
new client → old server
old event consumer → new producer payload
new consumer → historical payload corpus
```

Green compatibility test preukazuje tested scenarios a fixtures, nie všetkých external consumers. Risk decision zohľadňuje coverage a consumer inventory.

## 7. Additive changes nemusia byť compatible

Optional field môže zlomiť strict deserializer. Nová enum value môže zlomiť exhaustive switch. Nový event môže zvýšiť load alebo spustiť unknown handler. Nový response field môže ovplyvniť signature/canonicalization. `MINOR` preto nie je automaticky každá additive schema zmena.

Provider má navrhovať tolerant readers a explicitné unknown-value semantics. Consumer contract tests overujú, že supported clients ignorujú alebo bezpečne spracujú additions.

## 8. Dependency a platform compatibility

Public contract zahŕňa supported runtime, OS, architecture, database alebo Kubernetes versions, ak release ich mení. Drop support pre Java 17 alebo PostgreSQL 14 je breaking pre consumerov, aj keď application API ostalo rovnaké.

Release notes a machine-readable metadata majú uviesť:

```yaml
support:
  operatingSystems:
    - linux-amd64
    - linux-arm64
  database:
    postgresql: ">=15 <18"
  kubernetes: ">=1.32 <1.36"
  clients:
    payments-web: ">=6.4"
```

Range je intended contract. Actual compatibility stále potrebuje test evidence pre representative matrix.

## 9. Deprecation lifecycle

Breaking change sa nemá objaviť prvýkrát v MAJOR release bez migration pathu, ak ecosystem potrebuje koordináciu. Deprecation lifecycle:

```text
announce deprecated element
→ publish replacement a migration guide
→ instrument usage
→ warning period
→ consumer outreach
→ removal eligibility
→ MAJOR release
→ old line support/retirement
```

Deprecation bez usage visibility môže odstrániť skrytého consumera. Warning bez deadline-u sa stane permanentným debtom.

## 10. Version decision a automation

Automation môže navrhnúť required bump podľa contract diffu a conventional metadata, ale human alebo policy authority musí riešiť behavioral a support semantics. Commit message `feat:` nie je dôkaz backward compatibility.

Version gate môže vyhodnotiť:

```json
{
  "declaredVersion": "9.10.0",
  "minimumRequiredBump": "MAJOR",
  "reasons": [
    "removed event enum value SETTLEMENT_PENDING_REVIEW",
    "changed idempotency scope",
    "dropped PostgreSQL 14 support"
  ]
}
```

Gate odmietne under-versioned release. Over-versioning je menej nebezpečné pre compatibility, ale zvyšuje migration cost a oslabuje význam MAJOR signálu.

## 11. SemVer a distributed systems

Producer a consumer sa neupgradujú atomicky. Version decision musí počítať s mixed-version intervalom, retries, queued events a rollbackom. Aj keď new producer a new consumer tvoria compatible pár, rollout môže byť breaking, ak old consumer ešte spracúva backlog.

```text
old producer + old consumer
→ new tolerant consumer
→ old aj new producer payloads
→ producer switch
→ backlog drain
→ old consumer retirement
→ contract cleanup v neskoršej MAJOR boundary
```

SemVer release label nenahrádza deployment compatibility plan.

## Ako čítať Semantic Versioning ako compatibility contract

Semantic Versioning zapisuje verziu ako `MAJOR.MINOR.PATCH` pre software s definovaným **public API**. Public API nie je iba HTTP endpoint. Môže zahŕňať package symbols, CLI flags, config schema, event payloads alebo behavior, na ktorý sa consumers spoliehajú.

```text
MAJOR
→ nekompatibilná zmena public contractu

MINOR
→ backward-compatible nová funkcionalita

PATCH
→ backward-compatible oprava
```

Version `2.4.1` sama nepreukazuje, že zmena je správne klasifikovaná. Tím musí vedieť, čo public contract zahŕňa a aké consumers existujú.

Pre-release:

```text
2.4.0-alpha.1 < 2.4.0-beta.1 < 2.4.0-rc.1 < 2.4.0
```

Pre-release versions majú nižšiu precedence než final release. Build metadata za `+`, napríklad `2.4.0+build.17`, nemení SemVer precedence a nemá sa používať ako jediná immutable artifact identity.

Breaking change môže byť skrytý v semantics: pole zostane string, ale zmení význam; timeout default sa skráti; event ordering sa zmení. Schema diff preto nemusí stačiť.

SemVer je komunikácia pre dependency resolver a používateľov. Nezaručuje security, support duration, artifact immutability ani deployment compatibility so zmenenou databázou. Release manifest stále potrebuje digest a compatibility metadata.

Ak sa už publikovaná version ukáže chybná, neprepisuje sa novými bytes. Vydá sa nová PATCH alebo ďalšia pre-release version. Rovnaké číslo s dvoma digestmi rozbíja resolver, cache aj audit.

## 12. Connected incident `REL-PAY-68`

Atlas pridal enum value `PROVIDER_REVIEW` do `SettlementStatus`, zmenil idempotency scope a dropol PostgreSQL 14. Source diff bol označený `feat`, automation navrhla `9.10.0`. OpenAPI diff bol green, pretože enum bol v event schema a behavior idempotency nebol v OpenAPI.

Reusable pipeline navyše neexecutla jeden historical event shard. Release manifest s version `9.10.0` sa publikoval pod mutable multi-platform tagom.

```text
incomplete public-contract inventory
→ structural HTTP diff green
→ behavioral/event/platform changes nehodnotené
→ MINOR verdict
→ old consumers pokračovali bez migration
→ runtime failures
```

Old reporting consumer použil exhaustive enum mapping a posielal nové events do dead-letter queue. Client retries s old idempotency assumption vytvorili 31 duplicate provider effects. PostgreSQL 14 environment zlyhal pri migration syntax.

Root cause bol compatibility subject. SemVer policy sledovala iba HTTP schema a commit label, nie supported consumers a behavioral/platform contracts.

## 13. Recovery a acceptance verdict

Containment zastaví rollout a producer emission novej value cez feature control, zachová failed payloads a reconciliuje duplicates. Recovery pripraví tolerant consumer, migration guide, new idempotency contract a PostgreSQL support decision. Release sa republikuje ako `10.0.0` s immutable manifestom; predchádzajúca chybná candidate version sa revokuje.

SemVer contract je prijatý iba vtedy, keď:

```text
public API inventory je explicitný
+ previous a candidate release subjects sú immutable
+ structural, behavioral, event a platform dimensions sa hodnotia
+ supported consumer matrix je známa
+ additive changes majú tolerant-reader evidence
+ declared bump spĺňa minimum policy
+ deprecation má usage, deadline a migration path
+ mixed-version deployment je kompatibilný
+ under-versioned release je forbidden
+ second consumer a historical backlog prejdú
```

## 14. Troubleshooting flow

Pri „compatible“ release incidente sleduj:

```text
declared public contracts
→ previous/candidate artifact manifests
→ structural diffs
→ behavioral/default/error changes
→ consumer/runtime/platform inventory
→ compatibility tests a missing shards
→ version decision policy
→ rollout order a backlog
→ actual consumer failures
```

Competing hypotheses môžu byť undocumented contract, tool coverage gap, fixture gap, consumer strictness, support-range change, wrong release manifest, stale version decision alebo mixed-version sequencing. Version number samostatne nie je diagnostic evidence.

## 15. Anti-patterny

### Bump podľa veľkosti diffu

Compatibility závisí od observable contractu, nie počtu zmenených riadkov.

### `feat` automaticky znamená MINOR

Commit label nepreukazuje backward compatibility.

### Additive field je vždy safe

Strict consumers, enums, canonicalization a load môžu addition zlomiť.

### OpenAPI ako celý public API

Events, behavior, config, CLI a platform support môžu byť rovnako záväzné.

### MAJOR bez migration lifecycle-u

Číslo komunikuje breaking change, ale nevyrieši koordináciu consumerov a backlogu.

## 16. Kontrolné otázky

1. Čo Semantic Versioning komunikuje a čo negarantuje?
2. Ako sa definuje public API inventory?
3. Prečo Git diff neurčuje version bump?
4. Čo preukazuje structural API diff a čo nie?
5. Ako sa testuje behavioral compatibility?
6. Prečo optional field alebo enum addition môže byť breaking?
7. Ako platform support vstupuje do SemVer?
8. Čo musí obsahovať deprecation lifecycle?
9. Prečo mixed-version interval mení compatibility verdict?
10. Ktoré contract dimensions chýbali v `REL-PAY-68`?
11. Ako sa blokuje under-versioned release?
12. Prečo build metadata nenahrádza digest?

## Glossary impact

Relevantné pojmy: Semantic Versioning, public API inventory, observable compatibility, structural compatibility, behavioral compatibility, event compatibility, platform support contract, minimum required bump, pre-release identifier, build metadata, deprecation lifecycle, tolerant reader, mixed-version interval a under-versioned release.

## Primárne zdroje

- [Semantic Versioning 2.0.0](https://semver.org/)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [Protocol Buffers — Updating a Message Type](https://protobuf.dev/programming-guides/proto3/#updating)
- [Buf Breaking Change Detection](https://buf.build/docs/breaking/)
- [Kubernetes API deprecation policy](https://kubernetes.io/docs/reference/using-api/deprecation-policy/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Artifact versioning](artifact-versioning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Release management →](release-management.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
