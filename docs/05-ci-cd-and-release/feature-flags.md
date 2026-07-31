# Feature flags

Feature flag je versionovaný runtime control, ktorý oddeľuje nasadenie code pathu od aktivácie konkrétneho behavioru. Application obsahuje minimálne dve možné cesty a distributed evaluation system rozhoduje, ktorú použije konkrétny user, tenant, request alebo workload. Flag preto nie je iba boolean v ConfigMape. Je to policy subject s identity, type, targeting, defaults, distribution, cache, audit, failure a retirement lifecycle-om.

Feature flags umožňujú bounded exposure, kill switch, operational tuning a experiments. Zároveň vytvárajú nový control plane. Ak flag service, SDK cache a application instances používajú rozdielne generations, deployment môže byť stabilný a behavior rozdelený neplánovaným spôsobom. Safe default a loaded-generation observability sú rovnako dôležité ako UI toggle.

## 1. Dominantný intent-to-evaluation model

```text
business alebo operational intent
→ versionovaný flag contract a owner
→ code paths a safe default
→ targeting/rule generation
→ publication do flag authority
→ SDK/provider distribution a cache
→ request evaluation context
→ effective variant alebo value
→ behavior a business outcome
→ audit, rollback a retirement
```

Existencia flagu v control plane nepreukazuje, že application ho načítala. Evaluation result nepreukazuje, že code path výsledok správne použil. Každá boundary potrebuje read-back.

## 2. Exact flag subject

```yaml
flagSubject:
  key: settlement-review-v2
  type: boolean
  owner: payments-product
  purpose: release
  default: false
  failureDefault: false
  createdAt: 2026-07-15
  expiresAt: 2026-08-31
  codeIntroducedIn: payments-10.0.0
  targetingGeneration: flag-pay-882
  rules:
    - match: ring == "ring1"
      value: true
    - match: account_id in emergency_allowlist
      value: true
  prerequisites:
    - provider-routing-v18 == true
  forbiddenContexts:
    - regulatory_critical == true
  telemetry:
    exposeEvaluationReason: true
```

Flag key bez type, owner a expiry sa stáva permanentnou nezdokumentovanou configuration. Failure default sa musí zvoliť podľa risku; fail-open môže byť vhodný pre cosmetic behavior a nebezpečný pre privileged alebo financial path.

## 3. Flag types a semantics

Boolean flag je najjednoduchší, ale multi-variant string, integer limit alebo structured configuration môžu byť vhodnejšie. Type zmena je breaking contract pre SDK a application code.

```text
boolean
→ zapni/vypni path

string variant
→ control/treatment/algorithm-v3

integer
→ concurrency alebo sample percentage

structured value
→ versioned bounded configuration object
```

Flag nemá niesť arbitrary unvalidated config. Application validuje range, enum a schema a má safe fallback pri invalid value.

## 4. Evaluation context a privacy

Targeting používa context fields ako tenant, ring, Region, client version alebo account type. Context musí mať stable identity a privacy classification. Email alebo raw personal data nemá byť default targeting key.

```json
{
  "targetingKey": "acct-4811",
  "tenantType": "enterprise",
  "ring": "ring1",
  "region": "eu-central-1",
  "clientVersion": "6.4.2",
  "regulatoryCritical": false
}
```

Context object preukazuje values, ktoré caller poskytol evaluatoru. Nepreukazuje ich authoritative origin ani freshness. Security-sensitive attribute sa nesmie dôverovať iba client-supplied headeru.

## 5. Evaluation a OpenFeature example

Application používa provider-neutral API a explicitný default:

```python
from openfeature import api

client = api.get_client("payments-api")
value = client.get_boolean_value(
    "settlement-review-v2",
    False,
    evaluation_context={
        "targeting_key": account_id,
        "ring": ring,
        "region": region,
    },
)
```

Returned value preukazuje decision SDK/provider pathu pre daný context a moment. Nepreukazuje, že provider mal fresh generation ani že downstream code path vykonal intended behavior. Evaluation details s reason, variant a provider metadata sa logujú bounded spôsobom.

## 6. Distribution, cache a convergence

Flag authority publikuje generation. SDK môže používať streaming, polling alebo local cache. Network outage preto nemusí okamžite zastaviť evaluation; application používa last-known-good alebo default podľa policy.

```text
control-plane generation 882
→ provider publication
→ SDK instances observe 882
→ local cache loaded
→ requests evaluate generation 882
```

Application health endpoint môže publikovať loaded flag generation bez všetkých flag values:

```bash
curl --fail https://payments-api.internal/management/config-generation | jq '{release,flagGeneration,providerState,lastSyncAt}'
```

Output preukazuje application-declared loaded state. Nepreukazuje correctness provider SDK alebo all instances. Fleet sampling a evaluation telemetry rozlišujú split generation.

## 7. Targeting precedence

Multiple rules, prerequisites a overrides potrebujú deterministic ordering. Emergency allowlist môže shadowovať ring rule. Global kill switch môže mať vyššiu precedence než experiment assignment. Precedence musí byť dokumentovaná a testovaná.

```text
global safety deny
→ regulatory exclusions
→ explicit emergency override
→ ring/release rules
→ experiment assignment
→ default
```

UI reorder rule je production code change. Potrebuje review, audit, preview a rollback.

## 8. Safe failure behavior

Pri provider outage sú možnosti:

```text
last-known-good
→ zachová doterajší behavior, ale môže byť stale

static default
→ predictable, no môže vypnúť urgentný kill switch

fail-open
→ availability, ale risk activation

fail-closed
→ safety, ale možný outage
```

Choice sa viaže na flag purpose. Kill switch cache TTL a emergency propagation SLO musia byť kratšie než tolerované harm window.

## 9. Flag a deployment compatibility

Old release nemusí poznať nový flag. New release môže vyžadovať prerequisite code path. Flag activation sa smie uskutočniť až keď eligible fleet coverage a mixed-version compatibility sú známe.

```text
code deployed dark
→ loaded-generation coverage confirmed
→ bounded target activation
→ business validation
→ broad activation
→ old path cleanup v neskoršom release
```

Flag-off rollback nie je safe, ak old path už nevie pracovať s current data alebo external state.

## 10. Audit a authorization

Flag mutation môže mať produkčný blast radius podobný deploymentu. Potrebuje scoped roles, environment boundaries, change reason, actor, previous/new generation a approval podľa risku.

```yaml
flagChange:
  flag: settlement-review-v2
  previousGeneration: flag-pay-881
  newGeneration: flag-pay-882
  actor: release-controller
  reason: enable ring1 after canary acceptance
  expectedPopulation: ring1
  rollbackGeneration: flag-pay-881
```

Audit record preukazuje control-plane mutation. Nepreukazuje runtime convergence. Change closure zahŕňa loaded/effective population read-back.

## 11. Telemetry a cardinality

Evaluation metrics majú bounded labels: flag key, variant, reason, release, environment. Account ID nepatrí do Prometheus labels. Per-account correlation môže zostať v sampled logs alebo analytics store s privacy controls.

Sleduje sa evaluation error rate, default/fallback usage, generation lag, variant distribution a business outcome. High evaluation volume nesmie zaplaviť telemetry backend.

## 12. Flag debt a retirement

Každý temporary release/experiment flag má expiry a cleanup ownera:

```text
choose permanent variant
→ remove targeting rules
→ remove old code path
→ remove flag SDK calls
→ delete control-plane flag
→ verify no evaluation traffic
→ close documentation/tests
```

Zmazanie flagu pred code cleanup môže poslať application na default, ktorý nemusí byť chosen variant. Cleanup ordering je súčasť lifecycle-u.

## 13. Connected incident `REL-PAY-70`

Atlas nasadil new settlement path dark. Flag authority mala generation 882 s 2 % ring1 targetingom. Polovica Pods však stratila streaming connection a používala cached generation 879, kde emergency override povoľoval feature všetkým enterprise accounts. SDK failure mode bol last-known-good a healthcheck sledoval iba provider connection, nie loaded generation.

```text
control plane 882
→ split SDK caches 879/882
→ ring1 intended exposure
→ enterprise broad exposure na stale Pods
→ mixed code paths počas jednej journey
```

New path používal production provider side effect a pri timeout-e retryoval bez reconciliation. 31 duplicate authorizations vzniklo mimo intended cohort. Dashboard control-plane ukazoval správne 2 % targeting.

Root cause bol configured-versus-loaded flag state a stale precedence, nie samotný boolean.

## 14. Redesign a acceptance verdict

Redesign publikuje loaded generation per instance, používa maximum-staleness fail-closed pre financial flag, central stable account assignment a hard global deny vyššej precedence. Activation gate vyžaduje fleet convergence a actual variant distribution.

Feature flag je prijatý iba vtedy, keď:

```text
flag contract, type, owner a expiry sú explicitné
+ context fields majú authoritative origin
+ targeting precedence je deterministic
+ publication a loaded generations sú observed
+ failure default zodpovedá risku
+ mixed-version code/data compatibility je potvrdená
+ mutations sú authorized a audited
+ actual variant population zodpovedá intentu
+ forbidden stale-generation broad exposure je testovaná
+ retirement odstráni rule, code aj telemetry debt
```

## 15. Troubleshooting flow

```text
flag contract a intended generation
→ control-plane rules/precedence
→ provider distribution
→ SDK loaded cache per instance
→ evaluation context a result/reason
→ selected code path
→ data/external effects
→ telemetry population
```

Competing hypotheses môžu byť wrong rule, stale cache, context mismatch, prerequisite, invalid value, provider outage, code ignoring result, split fleet alebo feature/data incompatibility. Control-plane screenshot nie je effective-state proof.

## 16. Anti-patterny

### Flag ako permanentná configuration bez ownera

Bez expiry a cleanup sa runtime graph neustále komplikuje.

### Fail-open pre high-risk financial path

Provider outage potom môže aktivovať behavior mimo schválenej cohorty.

### UI targeting ako jediný evidence

Configured rules nepreukazujú loaded generation ani actual population.

### Account ID v metric labels

Vytvára cardinality a privacy risk.

### Zmazanie flagu pred code cleanup

Application spadne na default, ktorý nemusí byť permanentný chosen behavior.

## 17. Kontrolné otázky

1. Čo tvorí exact flag subject?
2. Prečo flag nie je iba boolean?
3. Ako sa validujú structured values?
4. Ktoré context fields možno dôverovať?
5. Čo preukazuje SDK evaluation result a čo nie?
6. Aký rozdiel je medzi published a loaded generation?
7. Ako sa volí failure default?
8. Prečo targeting precedence potrebuje tests?
9. Kedy flag-off nie je safe rollback?
10. Čo sa pokazilo v `REL-PAY-70`?
11. Ako sa overí actual variant population?
12. Aký je správny flag retirement order?

## Glossary impact

Relevantné pojmy: feature flag, flag subject, flag type, evaluation context, targeting key, rule precedence, provider generation, loaded flag generation, last-known-good, failure default, kill switch, flag mutation audit, variant distribution, flag debt a flag retirement.

## Primárne zdroje

- [OpenFeature specification](https://openfeature.dev/specification/)
- [OpenFeature Python SDK](https://openfeature.dev/docs/reference/technologies/server/python/)
- [CNCF Feature Flag Management principles](https://github.com/cncf/tag-app-delivery)
- [NIST SP 800-53 Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ring deployment](ring-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Progressive delivery →](progressive-delivery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
