# Ring deployment

Ring deployment riadi release cez stabilné production cohorts s odlišným risk profilom, workloadom, support modelom a recovery schopnosťou. Ring nie je iba percento trafficu ani dočasný canary step. Je to dlhšie žijúca release boundary, ktorá udržiava explicitnú informáciu o tom, kto používa ktorú release generation a aký entry, observation a exit contract musí release splniť.

Typické rings môžu začínať internými users a synthetic workloads, pokračovať low-risk tenants alebo jedným Regionom a skončiť všeobecnou populáciou. Poradie sa nemá odvodzovať iba od veľkosti. Prvý ring má poskytovať rýchly a kvalitný signal pri malom blast radiuse; ďalšie rings pridávajú nové workload, dependency a support dimensions.

## 1. Dominantný ring-promotion model

```text
immutable release subject
→ versionované ring membership a inventory
→ ring-specific entry contract
→ deployment a stable assignment
→ technical, business a support evidence
→ ring acceptance alebo recovery
→ next-ring eligibility
→ full adoption
→ previous release/ring retirement
```

Release môže byť accepted v jednom ring-u a rejected v ďalšom, pretože nový ring obsahuje iné clients, Regions, provider routes alebo scale. „Prešlo ring 1“ nie je globálny release verdict.

## 2. Exact ring subject

```yaml
ringSubject:
  releaseManifestDigest: sha256:release1000rc4
  ringProgramGeneration: payments-rings-v12
  rings:
    ring0:
      membershipGeneration: ring0-184
      population: internal-and-synthetic
      maximumAccounts: 200
      support: platform-engineering
    ring1:
      membershipGeneration: ring1-205
      population: low-risk-eu-standard
      maximumAccounts: 5000
      support: payments-oncall
    ring2:
      membershipGeneration: ring2-117
      population: enterprise-eu
      maximumAccounts: 800
      support: payments-plus-enterprise
    ring3:
      membershipGeneration: ring3-88
      population: general-availability
  assignmentUnit: account_id
  assignmentSaltGeneration: payments-ring-salt-12
```

Ring name bez membership generation je mutable. Account môže byť medzi rings presunutý počas incidentu alebo contract change. Evidence musí zachovať population, ktorá bola počas window-u skutočne exposed.

## 3. Ring design a risk ordering

Ring progression má pridávať konkrétnu risk dimension:

```text
ring 0
→ execution/basic integration, synthetic a internal users

ring 1
→ real low-risk traffic, common clients a provider routes

ring 2
→ enterprise scale, long-lived sessions, specialized workflows

ring 3
→ full diversity a general availability
```

Ak ring 0 používa len synthetic read-only requesty, neoverí write side effects. Ak ring 1 obsahuje iba jeden Region, neoverí global routing. Entry contract má pomenovať, čo nový ring pridáva a ktoré previous evidence sa reuse-ne.

## 4. Membership authority

Membership môže byť deklarovaná v versionovanom confige alebo service catalogu, ale runtime assignment musí mať one authoritative evaluator. Multiple writers — portal, application DB a feature platform — môžu vytvoriť split cohort.

```json
{
  "programGeneration": "payments-rings-v12",
  "membershipGeneration": "ring1-205",
  "accountId": "acct-4811",
  "ring": "ring1",
  "effectiveFrom": "2026-07-31T12:00:00Z",
  "reason": "standard-release-program"
}
```

Runtime operation logs majú zaznamenať effective ring aj release. Membership record preukazuje intended assignment; actual request evidence preukazuje enforcement.

## 5. Stable release assignment

Ring assignment má byť sticky počas business journey. Account s cached session alebo long-running workflow nemá meniť release uprostred operation. New membership generation môže platiť iba pre nové sessions alebo operations podľa explicitného cutover contractu.

Stable hashing je vhodné pre broad rings, explicit allowlist pre ring 0 alebo high-touch tenants. Pri explicit membership treba riešiť joiner/mover/leaver a stale cache invalidation.

## 6. Entry gate

Pred vstupom release do ring-u sa overí:

```text
previous-ring acceptance
+ current release manifest a evidence
+ ring membership snapshot
+ ring-specific platform/dependency readiness
+ support/on-call coverage
+ capacity a recovery budget
+ known issues a exclusions
→ entry verdict
```

Ring entry môže vyžadovať enterprise support notification alebo provider quota check, ktoré ring 1 nepotreboval. Approval je subject-bound na release a membership generation.

## 7. Ring deployment a read-back

Ring môže byť implementovaný traffic policy, feature flagom, dedicated environmentom alebo release channelom. Mechanizmus sa nesmie skrývať za ring label.

```bash
kubectl -n payments get trafficassignment payments-rings -o json | jq '{generation:.metadata.generation,observed:.status.observedGeneration,rings:.status.effectiveRings}'
```

Output preukazuje controller effective rings. Nepreukazuje actual assignment v edge/application caches. Sampled request logs a business operations sa agregujú podľa release+ring+membership generation.

## 8. Ring-specific observation

Global SLO môže skryť ring regression. Každý ring má minimum volume/duration a relevantné dimensions. Ring 2 enterprise traffic môže mať nízky count, ale vysoký financial exposure; acceptance preto môže používať account-level journey a reconciliation, nie iba statistical thresholds.

Support contacts a manual operations sú dôležitý signal. Ring program má explicitne rozlíšiť technical health, business correctness a operational burden.

## 9. Promotion a freeze

Next-ring promotion nesmie meniť current membership počas observation window-u tak, aby vyhodila failed accounts z denominatora. Membership changes počas incidentu sa evidujú ako new generation a analysis rozdelí periods.

Promotion state:

```text
NOT_ENTERED
→ DEPLOYING
→ OBSERVING
→ ACCEPTED / PAUSED / REJECTED / RECOVERING
→ NEXT_RING_ELIGIBLE
```

Release môže zostať dlhšie v ring-u ako supported channel. Vtedy patch/security lifecycle musí byť jasný; stale ring nesmie zostať navždy na zraniteľnej version.

## 10. Recovery a cohort rollback

Recovery môže vrátiť iba affected ring, zatiaľ čo previous ring zostane na new release, ak evidence preukazuje ring-specific failure. To znižuje blast radius, ale vytvára dlhšie mixed-release obdobie. API, data, events a support musia túto kombináciu zvládať.

Membership rollback nesmie presunúť in-flight operations medzi releases bez reconciliation. Account-level release pinning môže byť potrebné do ukončenia workflowu.

## Ako stabilné rings riadia expozíciu release-u

Ring deployment rozdeľuje population alebo infraštruktúru do vopred definovaných skupín a release postupuje od menšieho, lepšie pozorovateľného ringu k širšiemu. Ring môže predstavovať interných users, vybrané tenants, jeden región alebo určitú fleet. Jeho membership musí byť stabilný a versionovaný, inak sa počas observation window mení samotný subject experimentu.

Poradie rings vyjadruje risk model. Prvý ring má nízky blast radius a kvalitnú telemetry, ale nemusí reprezentovať production workload. Ďalšie rings pridávajú scale, dependency alebo tenant diversity. Promotion criteria preto nie sú identické pre každý krok; neskorší ring môže vyžadovať vyšší sample a odlišné business oracles.

Assignment sa robí podľa identity relevantnej pre celý workflow. Ak account počas release-u preskočí medzi rings, jeho multi-step operácia môže používať zmiešané generations. Membership changes sa preto plánujú mimo observation window alebo sa viažu na novú assignment generation.

Každý ring step má exact artifact, configuration, exposed population, start time, evidence a abort path. No-data v malom ringu môže znamenať nedostatočnú reprezentatívnosť, nie success. Pred promotion sa overí aj forbidden outcome a backlog.

Po full rollout-e sa temporary ring rules a overrides odstránia alebo sa stanú explicitnou dlhodobou policy. Ring deployment nie je iba zoznam prostredí; je to state machine expozície s kontrolovaným prechodom a recovery na každom kroku.

## 11. Connected incident `REL-PAY-70`

Atlas ring program mal membership v LaunchPad portali a application feature store. Počas ring 1 observation support tím presunul problematické accounts späť do ring 0 cez portal; feature store cache však zmenu načítala iba v polovici instances. Dashboard generoval denominator z current membership, takže failed accounts zmizli z ring 1 historical population.

```text
multiple membership writers
→ partial cache convergence
→ accounts split medzi releases
→ current-membership denominator prepísal history
→ ring 1 vyzeral green
→ promotion do enterprise ring 2
```

Ring 2 používal provider route s nižším quota limitom a new retry policy vytvorila overload. 418 enterprise settlements potrebovalo manual handling.

Root cause bol membership generation a historical cohort contract, nie iba retry policy.

## 12. Redesign a acceptance verdict

Redesign používa one authoritative membership service, append-only assignment history, release pinning per operation a explicitný membership cache generation. Ring evidence používa population snapshot v čase exposure. Každý ring pridáva documented risk dimensions a gate.

Ring deployment je prijatý iba vtedy, keď:

```text
release a ring-program generations sú exact
+ membership authority je jedna a historická
+ assignment je stable pre journey/operation
+ runtime enforcement sa read-backne
+ každý ring pridáva explicitný risk dimension
+ entry/exit gates sú ring-specific
+ denominator používa exposure-time membership
+ recovery zachová in-flight operation identity
+ forbidden cross-ring split assignment je testovaný
+ second ring a security patch lifecycle prejdú
```

## 13. Troubleshooting flow

```text
release a ring program
→ membership authority/generation
→ cache/evaluator convergence
→ actual request/operation assignment
→ ring-specific dependencies a capacity
→ observations and denominator history
→ promotion decision
→ cohort recovery
```

Competing hypotheses môžu byť wrong membership, cache lag, multiple writers, biased current-state denominator, route difference, low sample, support intervention alebo release-specific failure. Current ring table bez history nevysvetľuje past exposure.

## 14. Anti-patterny

### Ring ako percento trafficu

Percento nehovorí, kto je exposed a aký risk dimension sa testuje.

### Current membership ako historical denominator

Moveri môžu spätne zmeniť interpretation experimentu alebo rollout evidence.

### Viac membership writers

Split authority vedie k inconsistent cohorts a nejasnej recovery.

### Ring promotion bez new-risk contractu

Ďalší ring potom iba zväčší blast radius bez nového learningu.

### Permanent old release ring bez support policy

Dlhšie mixed versions zvyšujú security a compatibility debt.

## 15. Kontrolné otázky

1. Čím sa ring odlišuje od canary percentage step-u?
2. Čo tvorí exact ring subject?
3. Ako sa určuje risk ordering rings?
4. Prečo membership potrebuje generation a history?
5. Ako sa zachová stable assignment pre long journey?
6. Čo musí obsahovať ring entry gate?
7. Ako sa overí runtime enforcement?
8. Prečo current membership nesmie byť historical denominator?
9. Ako sa recovery jedného ring-u líši od global rollbacku?
10. Čo sa pokazilo v `REL-PAY-70`?
11. Ako sa rieši security patch pre dlhšie žijúce rings?
12. Čo musí pridať second ring do evidence?

## Glossary impact

Relevantné pojmy: ring deployment, ring program generation, membership generation, ring authority, stable ring assignment, exposure-time membership, ring entry contract, ring exit verdict, release channel, cohort rollback, mixed-release ring a ring retirement.

## Primárne zdroje

- [Google SRE — Release Engineering](https://sre.google/sre-book/release-engineering/)
- [Microsoft — Safe Deployment Practices](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments)
- [OpenFeature specification](https://openfeature.dev/specification/)
- [Argo Rollouts documentation](https://argo-rollouts.readthedocs.io/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shadow deployment](shadow-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Feature flags →](feature-flags.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
