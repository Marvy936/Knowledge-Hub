# Progressive delivery

Progressive delivery je riadený systém postupného sprístupňovania zmeny na základe produkčnej evidence. Spája deployment stratégie, feature flags, segmentáciu, observability, automatizované analysis a recovery do jedného kontrolovaného rollout procesu.

## 1. Základný model

```text
immutable artifact
→ deploy without full exposure
→ expose limited cohort
→ collect technical and business evidence
→ promote, pause, abort or remediate
→ repeat until intended release state
```

Nejde o jedinú techniku. Canary, rings, blue-green, feature flags, A/B testing a shadow traffic sú stavebné prvky.

## 2. Deployment vs. release control

Progressive delivery oddeľuje:

- **artifact promotion** — ktorý immutable artifact je v environment-e,
- **traffic promotion** — koľko requestov smeruje na novú verziu,
- **audience promotion** — ktoré cohorts capability používajú,
- **feature promotion** — ktoré behavior paths sú aktívne,
- **release decision** — či je zmena považovaná za produkčne prijatú.

Tieto osi nemusia postupovať súčasne.

## 3. Delivery controller

Controller môže riadiť:

- rollout steps,
- traffic weights,
- ring membership,
- feature flags,
- observation windows,
- metric queries,
- promotion a abort policy,
- rollback alebo roll-forward action,
- auditný release record.

Controller je produkčný control plane. Jeho permissions a configuration majú rovnakú kritickosť ako deployment pipeline.

## 4. Progressive delivery contract

Každý rollout má mať explicitný kontrakt:

```text
artifact digest
+ config revision
+ target environment
+ rollout strategy
+ cohort definition
+ promotion metrics
+ abort metrics
+ observation windows
+ max blast radius
+ recovery actions
+ owner
```

Bez immutable identity nemožno spojiť evidence s nasadeným obsahom.

## 5. Strategies

### Canary

Postupné percento trafficu s baseline porovnaním.

### Rings

Stabilné cohorts s rastúcou kritickosťou alebo reprezentatívnosťou.

### Blue-green

Oddelený target a traffic cutover s možnosťou routing rollbacku.

### Feature flags

Runtime exposure capability nezávislá od artifact deploymentu.

### Shadow

Reálny workload bez autoritatívnej response a bez povolených side effects.

### A/B experiment

Porovnanie variantov podľa produktového outcome, nie iba safety.

## 6. Promotion evidence

Evidence môže zahŕňať:

- artifact integrity a provenance,
- pre-deployment test results,
- runtime health,
- SLI/SLO a error-budget burn,
- latency, errors a saturation,
- business success rate,
- security anomalies,
- support alebo user feedback,
- sample size a confidence,
- compatibility checks,
- change-management metadata.

Promotion policy má používať najmenší dostatočný súbor dôkazov, nie neobmedzený dashboard checklist.

## 7. Technical vs. business metrics

Technické metrics odpovedajú, či systém funguje stabilne. Business metrics odpovedajú, či zmena prináša správny outcome.

Príklad:

```text
HTTP success rate = stable
latency = stable
checkout completion = -8 %
```

Technický rollout môže byť zdravý, ale release neúspešný.

## 8. Observation window

Observation window musí pokryť čas, za ktorý sa prejaví relevantný risk:

- okamžité request failures,
- cache warm-up,
- autoscaling,
- long transactions,
- queue backlog,
- scheduled jobs,
- delayed business outcomes,
- retention alebo churn.

Jedna univerzálna duration pre všetky kroky je slabá policy.

## 9. Risk-based rollout

Rozsah kontroly možno odvodiť z:

- business criticality,
- changed components,
- IAM alebo database zmien,
- reversibility,
- blast radius,
- novelty,
- incident history,
- observability quality,
- test evidence,
- dependency scope.

Nízko-riziková zmena môže postupovať rýchlejšie. Vysoko-riziková potrebuje menšie kroky, dlhšie windows alebo manuálny checkpoint.

## 10. Pause, abort a resume

Stavy rollout-u musia byť explicitné:

- `progressing`,
- `paused`,
- `degraded`,
- `aborted`,
- `rolled_back`,
- `rolled_forward`,
- `completed`.

Resume po pause musí overiť, že artifact, policy, environment a evidence sú stále aktuálne.

## 11. Missing alebo delayed telemetry

Policy musí rozhodnúť:

- ktoré signály fail closed,
- ktoré fail open s warningom,
- ako dlho sa čaká,
- čo je minimálna completeness,
- ako sa deteguje stale query,
- ako sa odlíši nula udalostí od chýbajúcich dát.

Absencia errorov pri nefunkčnej telemetry nie je úspech.

## 12. Automated analysis

Automatická analysis môže používať:

- threshold rules,
- baseline ratio,
- trend detection,
- anomaly detection,
- statistical tests,
- composite score,
- error-budget burn policy.

Model musí byť vysvetliteľný a testovateľný. Komplexný score bez možnosti vysvetliť abort znižuje dôveru operátorov.

## 13. Manual checkpoints

Manuálny approval má zmysel pri:

- právnom alebo business rozhodnutí,
- neautomatizovateľnej evidence,
- vysokom a nevratnom dopade,
- emergency risk acceptance,
- nejednoznačnom signále.

Approval nemá nahrádzať automatické overenie identity, testov, policy a runtime health.

## 14. Error budgets

Error-budget stav môže meniť rollout policy:

```text
healthy budget
→ normal progression

high burn
→ smaller steps, longer windows or freeze
```

Použi user-facing reliability signal, nie všeobecný zákaz zmien po každom incidente.

## 15. Recovery hierarchy

Možnosti:

1. zastaviť ďalšiu promotion,
2. znížiť exposure,
3. vypnúť feature flag,
4. route traffic na stable target,
5. rollback artifactu,
6. roll-forward s opravou,
7. compensating action,
8. restore dát podľa recovery plánu.

Najrýchlejšia bezpečná akcia závisí od state compatibility.

## 16. Database a shared-state constraints

Progressive rollout predlžuje coexistence starých a nových verzií. Vyžaduje:

- backward-compatible schema,
- tolerant readers,
- compatible writers,
- event schema evolution,
- cache/session versioning,
- idempotent migrations,
- cleanup až po rollback window.

Traffic control nevyrieši nekompatibilný shared state.

## 17. Multi-service releases

Pri viacerých services je potrebné:

- dependency graph,
- compatibility matrix,
- independent deployability,
- release manifest,
- coordinated flags,
- per-service telemetry,
- partial rollout recovery.

Big-bang promotion všetkých services znižuje hodnotu progressive delivery.

## 18. Governance a audit

Zachovaj:

- kto vytvoril rollout,
- artifact a config identity,
- policy version,
- každú zmenu exposure,
- metric snapshots alebo query references,
- approvals a exceptions,
- abort/rollback reason,
- final release state.

Audit má byť generovaný mechanizmom, nie ručne rekonštruovaný z chatu.

## 19. Metriky procesu

Sleduj:

- rollout duration,
- pause a abort rate,
- false abort rate,
- exposure before detection,
- automatic vs. manual decisions,
- rollback/roll-forward success,
- stale rollout count,
- policy override rate,
- time to full release,
- change fail rate podľa stratégie.

Rýchlejší rollout nie je automaticky lepší, ak rastie blast radius alebo false confidence.

## 20. Troubleshooting

### Rollout sa zasekol v pause

Over ownera, expiry, missing evidence, stale approval a recovery condition. Pause bez lifecycle vytvára version skew.

### Controller promotionoval bez trafficu

Metric query vrátila nulu namiesto missing data alebo nebola overená sample size.

### Feature flag a traffic weight sa rozchádzajú

Zaveď jeden rollout contract a koreláciu oboch control planes.

### Automatický rollback zhoršil incident

State nebol backward-compatible alebo rollback signal bol noisy. Zastav automatiku a prehodnoť recovery policy.

### Final release stále obsahuje starý path

Chýbal cleanup owner/expiry. Progressive delivery lifecycle nie je dokončený pri 100 % exposure.

## 21. Anti-patterny

### Progressive delivery = pomalý rolling update

Chýba evidence-driven promotion a explicitný exposure control.

### Rovnaká policy pre každú zmenu

Ignoruje rozdielnu reversibility a business kritickosť.

### Nekonečný canary

Dočasný stav sa stane permanentným a zvyšuje version skew.

### Automatizácia bez explainability

Operátor nevie, prečo controller promotionoval alebo abortoval.

### Rollout bez cleanup fázy

Flags, staré versions a dočasné configy zostávajú ako dlh.

## 22. Kontrolné otázky

1. Čo je progressive delivery?
2. Aké osi promotion možno riadiť nezávisle?
3. Čo obsahuje rollout contract?
4. Ako sa líšia technické a business metrics?
5. Ako zvoliť observation window?
6. Ako má policy reagovať na missing telemetry?
7. Kedy má zmysel manuálny checkpoint?
8. Ako error budget mení rollout policy?
9. Prečo shared-state compatibility zostáva kritická?
10. Kedy je progressive rollout skutočne dokončený?

## Glossary impact

Relevantné pojmy: progressive delivery, rollout controller, rollout contract, evidence-driven promotion, progressive exposure, rollout pause, rollout abort, policy override, exposure before detection, automated analysis a cleanup phase.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Feature flags](feature-flags.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Rollback a roll-forward →](rollback-and-roll-forward.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
