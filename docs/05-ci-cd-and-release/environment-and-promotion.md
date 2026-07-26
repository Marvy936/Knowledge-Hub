# Environment a promotion

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Environment je identifikovateľný runtime a policy context. Obsahuje artifacty, configuration, infrastructure, identities, secrets references, data/shared state, network, dependencies, observability a deployment history. Promotion je riadené rozhodnutie nasadiť ten istý immutable release manifest do konkrétneho environmentu bez rebuildu a overiť jeho effective runtime výsledok.

```text
immutable release manifest
+ versioned configuration/infrastructure
+ resolved target environment identity
+ current effective/shared state
+ complete a fresh evidence
+ promotion policy
→ locked deployment transition
→ post-deploy verification
→ exposure, recovery alebo reconciliation
```

## 1. Cieľ kapitoly

Nosný model kapitoly je environment-promotion lifecycle:

```text
target environment identity
→ desired a effective state observation
→ drift a compatibility classification
→ artifact/config eligibility
→ lock a preconditions
→ deployment mutation
→ readiness a functional verification
→ release exposure
→ deployment record
→ rollback, roll-forward alebo reconciliation
```

Cieľom nie je memorovať názvy `dev`, `staging` a `production`. Cieľom je vedieť, ktoré runtime assumptions každý environment dokazuje, čo sa pri promotion reálne mení a ako sa zabráni zámene rovnakého artifactu za rovnaké správanie.

## 2. Nosný scenár: Atlas Orders 3.10.1

Predchádzajúca kapitola vytvorila release manifest:

```text
R = {
  orders-api digest A,
  payment-worker digest B,
  migration bundle digest M,
  config schema S,
  provenance a evidence references
}
```

Atlas má tri relevantné environmenty:

```text
ephemeral integration E1
→ overuje wiring, PostgreSQL/broker contracts a migration rehearsal

staging E2
→ overuje deployment topology, identity federation, ingress a operational acceptance

production E3
→ reálny shared state, quotas, tenant skew a controlled exposure
```

Promotion nemení A, B ani M. Mení assignment manifestu R k environmentu, configuration revision, effective deployment state a neskôr traffic exposure.

## 3. Environment identity

Alias `production` nestačí. Atlas environment identity obsahuje:

- account/subscription a region;
- cluster a namespace/runtime boundary;
- stable environment ID;
- infrastructure revision;
- rendered configuration digest;
- secret/identity references;
- active release manifest a component digests;
- schema/migration state;
- feature-flag a traffic-policy revision;
- protection level a ownera.

Deployment pred mutation overuje resolved stable ID. User-controlled názov nesmie byť jediným vstupom destructive deploy alebo teardown operácie.

## 4. Desired state verzus effective state

Desired state je deklarovaný intent. Effective state je výsledok po platform defaults, controllers, mutations, runtime failures a out-of-band zásahoch.

```text
desired:
manifest R
replicas 4
DB pool 80
network deny-by-default

observed effective:
3 ready replicas
manifest R na troch podoch, starý digest na jednom
admission sidecar pridaný
DB pool override 160 z UI configu
platformová egress výnimka aktívna
```

Promotion decision potrebuje obe vrstvy. Git diff alebo IaC plan nepreukazuje, čo environment skutočne vykonáva.

## 5. Behavioral equivalence podľa rizika

Úplná parity stagingu a produkcie je často nepraktická. Potrebná je equivalence boundary, ktorú testujeme.

| Riziko | Potrebná equivalence |
|---|---|
| deployment a readiness | rovnaký orchestrator, probes, sidecars a routing |
| identity/authorization | rovnaký federation a policy model |
| migration locking | rovnaký DB engine/version a reprezentatívna distribúcia dát |
| rolling compatibility | viac replík a mixed-version topology |
| external provider quotas | reálny alebo contract-faithful limit model |
| tenant-skew capacity | produkčný canary segment |

Staging s jednou replikou nepreukazuje rolling update. Malý uniformný dataset nepreukazuje production query plan a lock behavior.

## 6. Artifact, configuration a secrets

Atlas oddeľuje:

```text
release manifest R
→ rovnaký vo všetkých environments

rendered configuration K(E)
→ environment-specific a versionovaná

secret references I(E)
→ environment-specific identity/version references

traffic policy F(E)
→ environment-specific exposure state
```

Configuration je release input. Má schema, provenance, validation, compatibility, fail-open/fail-closed semantics, rollback state a audit. Secret values sa nepremiestňujú zo stagingu do produkcie; promotion nesie requirement/reference contract, nie hodnotu.

## 7. Promotion contract

Atlas promotion subject nie je iba image digest. Je to deployment tuple:

```text
release manifest R
+ target environment ID E
+ rendered config digest K
+ infrastructure revision I
+ shared-state compatibility snapshot D
+ policy version P
```

Promotion eligibility vyžaduje:

- immutable a dôveryhodný manifest;
- complete/fresh evidence viazanú na R;
- config kompatibilný so schema a artifactmi;
- environment health a known drift;
- database/event compatibility;
- dostupnú deployment identity a lock;
- recovery path;
- neexpirovaný approval alebo automated decision.

Zmena R, K, I, E alebo relevantného D invaliduje predchádzajúce rozhodnutie.

## 8. Evidence freshness

Evidence neexpiruje rovnako:

```text
unit/build evidence pre immutable R
→ platí, kým sa nemení subject alebo policy

vulnerability evidence
→ refresh po threat-database/policy zmene

environment health a drift snapshot
→ krátke pre-deploy okno

approval
→ platí iba pre R + K + E + strategy + risk snapshot

canary evidence
→ platí pre konkrétnu cohortu a rollout stage
```

Expired evidence vedie k revalidation, pause alebo novému approval, nie k implicitnému passu.

## 9. Protected environment a identity

Protected production environment vynucuje server-side:

- povolené refs a release manifests;
- deployment workflow identity;
- environment-scoped short-lived role;
- required policy/approval;
- concurrency a deployment window;
- secret access;
- manual override a break-glass audit.

Build job nemá production permission. Deploy job číta schválený manifest a dostane krátkodobé práva iba pre environment E3. Job name ani runner label nie sú authorization controls.

## 10. Lock, lease a compare-and-swap

Environment je shared mutable resource. Atlas deployment používa:

```text
acquire lease pre E + observed revision V
→ prechecks
→ compare current revision stále = V
→ apply mutation
→ heartbeat/renew lease
→ verify
→ record new revision V+1
→ release lease
```

Lease obsahuje owner/run ID, expiry, heartbeat a stale-lock recovery. Príliš krátka lease môže povoliť overlap počas platného deploymentu; neobmedzený lock môže po runner failure zablokovať environment.

## 11. Deployment state machine

```text
requested
→ target resolved
→ eligibility verified
→ lock acquired
→ desired/effective state observed
→ mutation applied
→ rollout/readiness observing
→ functional/business verification
→ completed / paused / failed / inconclusive
→ exposure decision
→ recovery/reconciliation
→ record and unlock
```

`orchestrator success` nie je finálny verdict. Post-deploy oracle potvrdzuje správny digest/config, routing, critical journey, migration state, telemetry a business invariant.

## 12. Partial state a retry

Partial deployment môže znamenať:

- mix starého a nového digestu;
- migration commitnutú pred application failure;
- config zmenený bez úspešného restartu;
- routing prepnutý iba v regióne;
- infra resource vytvorený bez identity bindingu.

Retry najprv pozoruje effective state. Mutation je idempotentná alebo reconciliuje desired verzus observed stav. Slepé zopakovanie commandu pri unknown outcome môže zdvojiť migráciu, prepísať novší rollout alebo poškodiť data.

## 13. Shared data a event state

Database a queue sa nepromotionujú ako image. Atlas používa expand-contract:

```text
additive schema/event contract
→ tolerant readers/writers
→ deploy mixed-compatible versions
→ bounded migration/backfill
→ completeness a integrity verification
→ switch behavior
→ remove old consumers
→ destructive cleanup neskôr
```

Rollback eligibility závisí od aktuálneho schema, data a retention state. Starý stateless API artifact môže byť dostupný, ale starý worker nemusí rozumieť eventom už v queue.

## 14. Deployment verzus release exposure

```text
deploy R do production s flag off
→ synthetic/internal validation
→ internal tenant
→ 5 % matched cohort
→ broader rings
→ 100 % release
```

Deployment record odpovedá, čo beží. Exposure record odpovedá, kto behavior používa. Oba záznamy sa korelujú cez environment, manifest, config/flag revision a čas.

## 15. Environment drift a reconciliation

Drift categories:

- binary/release drift;
- configuration drift;
- infrastructure drift;
- identity/secret drift;
- policy/network drift;
- data/schema drift;
- observability drift.

Lifecycle:

```text
desired state
→ effective observation
→ normalize expected platform defaults
→ classify delta a risk
→ block, reconcile alebo accept expiring exception
→ verify a record
```

Blind auto-reconcile môže odstrániť emergency mitigation. Drift potrebuje ownera a context-aware policy.

## 16. Worked failure: rovnaký artifact, odlišná production configuration

Staging aj production používali digest A. Staging prešlo, ale production API saturovalo DB:

```text
staging config K1: concurrency 20, DB pool 80
production hidden UI override K2: concurrency 120, DB pool 80
→ rovnaké bytes
→ production worker vytvoril connection contention
→ latency a queue age rástli
```

### Root cause

Tím považoval rovnaký artifact za rovnaký release input. UI override nebol vo versionovanej config provenance ani approval packet-e.

### Náprava

- rendered config má digest a source precedence report;
- UI overrides sú zakázané alebo auditované ako revision;
- promotion subject zahŕňa R + K + E;
- config schema/policy kontroluje concurrency budget;
- canary guardrails sledujú DB wait a queue age;
- staging test používa production-relevantný config profile.

## 17. Worked failure: vypršaná lease dovolila dva deploymenty

Deployment A bol pomalý počas migration verification. Jeho lease vypršala, hoci runner pokračoval. Deployment B získal nový lock:

```text
A aplikuje manifest R1 a migration phase
→ lease bez heartbeat vyprší
→ B nasadí R2 a zapíše environment revision V2
→ A dokončí a prepíše časť config/routingu na R1
→ inventory ukazuje mixed, nejasný state
```

### Root cause

Lock chránil iba začiatok jobu. Chýbal heartbeat, compare-and-swap pred ďalšou mutation a stale-owner fencing.

### Náprava

- lease sa obnovuje a mutation overuje fencing token;
- environment revision používa compare-and-swap;
- superseded deployment prestane mutovať po strate lease;
- reconciliation obnoví manifest/config consistency;
- deployment record zachová oba attempts a partial states;
- post-deploy verification kontroluje všetky component digests a routing.

## 18. Rollback, roll-forward a teardown

Rollback je možný iba ak:

- last-known-good artifacts stále existujú;
- config a infrastructure sú kompatibilné;
- database/event state rozumie starej verzii;
- external side effects sú reverzibilné alebo reconciled;
- traffic a flags možno bezpečne vrátiť.

Inak Atlas použije flag-off, write freeze, containment, compatible roll-forward alebo data reconciliation.

Ephemeral teardown je samostatná destructive state machine: stable ID, protection check, traffic stop, retention export, credential revocation, dependency-aware deletion, finalizer handling, lock cleanup a orphan verification. Production/shared environments sú denylisted z TTL cleanupu.

## 19. Deployment record a inventory

Deployment record zachová:

```text
R + K + I + E
actor/workload identity
policy/approval snapshot
lock/lease/fencing identity
observed pre-state
mutation timeline
post-state a verification
exposure relation
recovery relation
```

Inventory priebežne odpovedá, čo reálne beží. Neúspešné a partial attempts sú súčasťou histórie, nie iba pipeline logs na krátku retention.

## 20. Diagnostický postup

1. Potvrď stable environment ID a protection level.
2. Porovnaj release manifest/component digests.
3. Porovnaj rendered config digest a variable precedence.
4. Over infrastructure, identity/secret a policy revisions.
5. Zmeraj effective state: replicas, routing, sidecars a resource state.
6. Skontroluj schema, migration, queue/backlog a event compatibility.
7. Over lease owner, heartbeat, fencing token a environment revision.
8. Rozlíš precheck rejection, partial apply, readiness, verification a cleanup failure.
9. Vyber reconcile, rollback, roll-forward, flag-off alebo containment podľa shared stateu.
10. Potvrď post-recovery technical, functional a data-integrity oracle.
11. Aktualizuj drift/config/promotion control, ktorý failure prepustil.

## 21. Referenčné pravidlá

- Environment je runtime, data, identity a policy boundary, nie iba namespace.
- Promotion presúva rovnaký immutable manifest bez rebuildu.
- Promotion subject zahŕňa artifact, config, target a relevantný shared state.
- Desired state sa musí porovnať s effective state.
- Behavioral equivalence sa odvodzuje od konkrétneho rizika.
- Config change má vlastný provenance a rollout lifecycle.
- Protected environment sa vynucuje server-side.
- Deployment identity je short-lived a environment-scoped.
- Locks potrebujú lease, heartbeat, fencing a stale recovery.
- Retry pozoruje partial state pred mutation.
- Database/event compatibility určuje rollback eligibility.
- Deployment a release exposure sú oddelené, ale korelované.
- Drift sa klasifikuje pred reconciliation.
- Deployment record obsahuje aj neúspešné attempts.

## 22. Časté omyly

### „Environment je namespace“

Namespace nepopisuje config, identities, data, dependencies, policy ani history.

### „Staging je menšia produkcia“

Iba ak zachová boundaries relevantné pre konkrétny risk.

### „Rovnaký digest znamená rovnaké správanie“

Configuration, identity, data, topology a traffic môžu behavior zásadne zmeniť.

### „Promotion znamená rebuild pre nový environment“

Rebuild vytvára nový artifact a invaliduje pôvodnú evidence.

### „Lock stačí bez lease a fencing“

Runner failure alebo expiry môže povoliť súbežné mutations.

### „Rollback je vždy dostupný“

Shared mutable state môže starú verziu urobiť nekompatibilnou.

## 23. Zhrnutie

Dôveryhodná Atlas promotion je:

```text
stable target identity
→ desired/effective state a drift snapshot
→ immutable manifest + config/infra/shared-state subject
→ complete/fresh eligibility
→ scoped identity, lock a fencing
→ state-aware deployment
→ runtime verification a exposure
→ deployment record
→ compatible recovery alebo reconciliation
```

Environment nie je pasívny cieľ. Je meniaci sa runtime state, ktorého identita, compatibility a drift priamo určujú, či je promotion bezpečná.

## 24. Kontrolné otázky

1. Čo tvorí environment identity?
2. Ako sa líši desired a effective state?
3. Prečo sa behavioral equivalence viaže na risk?
4. Čo tvorí Atlas promotion subject?
5. Prečo rovnaký artifact nestačí bez config provenance?
6. Ako evidence freshness závisí od typu signálu?
7. Čo chráni protected environment?
8. Prečo deployment potrebuje lease, heartbeat a fencing?
9. Ako sa diagnostikuje partial deployment?
10. Prečo database a queue určujú rollback eligibility?
11. Aký je rozdiel medzi deploymentom a exposure?
12. Ako drift lifecycle odlišuje platform defaults od nebezpečnej zmeny?
13. Ako vznikol Atlas config failure medzi stagingom a production?
14. Ako súbežné deploymenty vytvorili mixed state?

## Glossary impact

Relevantné pojmy: environment identity, desired state, effective state, behavioral equivalence, rendered configuration digest, promotion subject, promotion eligibility, protected environment, environment-scoped identity, deployment state machine, deployment lock, lease, fencing token, partial deployment, environment revision, environment drift, deployment record, rollback eligibility a release exposure.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Trigger, artifact a cache](trigger-artifact-cache.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Quality gates a approvals →](quality-gates-and-approvals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
