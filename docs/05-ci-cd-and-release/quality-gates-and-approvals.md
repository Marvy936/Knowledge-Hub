# Quality gates a approvals

Quality gate je rozhodovací mechanizmus, ktorý vyhodnotí exact subject proti očakávanému evidence inventory a versionovanej policy. Approval je rozhodnutie oprávnenej authority nad residual riskom alebo business contextom, ktorý nemožno spoľahlivo zredukovať na automatické pravidlo. Gate a approval sa nemajú zamieňať: human nesmie manuálne dopĺňať chýbajúci scanner result a automatický threshold nemá predstierať rozhodnutie o nevratnom business riziku, ktoré policy nepozná.

Zelený check bez subject identity, evidence completeness a policy generation je iba status. Dôveryhodný decision record musí ukázať, čo sa hodnotilo, ktoré dôkazy boli povinné, ktoré chýbali alebo expirovali, aká policy sa použila, kto rozhodol a ktorý delivery transition bol povolený.

## 1. Dominantný subject-to-decision model

```text
immutable candidate alebo release subject
→ expected evidence inventory a applicability
→ evidence collection, validation a freshness
→ versioned decision policy
→ automatic evaluation
→ optional human residual-risk approval
→ allow / deny / review / incomplete / expired / inconclusive / waived
→ bounded delivery transition
→ audit, expiry, revocation a post-outcome learning
```

Gate nie je iba `if score > 80`. Musí rozlišovať missing data, tool failure, non-applicable evidence, stale evidence, explicit exception a failed control. Inak sa technická neistota ticho premení na pass.

## 2. Exact gate-decision subject

Atlas Payments zachováva decision input ako immutable record:

```yaml
gateSubject:
  subjectType: release-candidate
  releaseManifestDigest: sha256:release1000rc4
  artifactDigests:
    - sha256:pay1000api
    - sha256:pay1000worker
  configurationSha: 71ac290
  targetEnvironmentGeneration: prod-eu-1844
  policyBundleSha: 66cf902
  expectedEvidence:
    - candidate-tests
    - api-compatibility
    - event-compatibility
    - image-vulnerability
    - sbom
    - signature
    - migration-rehearsal
    - rollback-rehearsal
    - staging-business-canary
  changeRisk:
    database: expand-only
    externalSideEffects: changed
    authentication: unchanged
  requestedTransition: production-canary-2-percent
```

Gate decision nesmie prežiť zmenu artifactu, environment generation alebo policy bundle-u. Approval nad `releaseId: 10.0` bez digestov je prenositeľný na iný subject a preto nie je dôveryhodný.

## 3. Expected evidence inventory

Evidence completeness sa definuje pred spustením pipeline. Inak môže failed job zmiznúť z graphu a final gate porovnať iba doručené reports.

```json
{
  "expected": [
    "candidate-tests",
    "api-compatibility",
    "event-compatibility",
    "image-vulnerability",
    "sbom",
    "signature",
    "migration-rehearsal",
    "rollback-rehearsal",
    "staging-business-canary"
  ],
  "received": [
    "candidate-tests",
    "api-compatibility",
    "event-compatibility",
    "sbom",
    "signature",
    "migration-rehearsal",
    "rollback-rehearsal",
    "staging-business-canary"
  ]
}
```

```bash
jq -e '
  (.expected | sort) == (.received | sort)
' evidence-inventory.json
```

Non-zero exit preukazuje mismatch zoznamov. Nepreukazuje, že received evidence je validné, fresh alebo subject-bound. Každý evidence object potrebuje schema, producer identity, subject digest, time window, result a integrity protection.

## 4. Evidence validity, applicability a freshness

Valid report môže byť nepoužiteľný pre dané rozhodnutie. Staging performance test nad iným architecture alebo provider quota nemusí platiť pre production. Vulnerability scan pred zmenou base image digestu je stale. Rollback rehearsal pred destructive schema contractom už nie je relevantná.

Evidence record môže vyzerať:

```yaml
evidence:
  type: staging-business-canary
  subjectDigest: sha256:release1000rc4
  environmentGeneration: staging-eu-920
  producer: canary-controller@sha256:canary17
  observedFrom: 2026-07-31T11:00:00Z
  observedUntil: 2026-07-31T11:20:00Z
  result: pass
  validFor:
    artifactDigest: sha256:pay1000api
    databaseContract: settlement-schema-v42-expand
  invalidatedBy:
    - artifact-change
    - database-contract-change
    - provider-route-change
```

Cryptographic integrity nepreukazuje applicability. Policy musí porovnať subject a assumptions.

## 5. Automatic gate policy

Policy má structured input a output. Rego príklad:

```rego
package release.gate

required := {
  "candidate-tests",
  "api-compatibility",
  "event-compatibility",
  "image-vulnerability",
  "sbom",
  "signature",
  "migration-rehearsal",
  "rollback-rehearsal",
  "staging-business-canary",
}

received := {e.type | e := input.evidence[_]; e.valid == true; e.fresh == true}

missing := required - received

allow if {
  count(missing) == 0
  input.findings.blocking == 0
  input.target.healthy == true
  input.recovery.eligible == true
}

decision := {
  "allow": allow,
  "missing": sort([x | x := missing[_]]),
  "policySha": input.policySha,
}
```

Evaluation:

```bash
opa eval \
  --data policy/ \
  --input gate-input.json \
  --format pretty \
  'data.release.gate.decision'
```

OPA output preukazuje decision podľa loaded policy/data a poskytnutého inputu. Nepreukazuje autenticitu inputu, že pipeline presadila output ani že policy bundle zodpovedá reviewed SHA. Decision log má zachovať bundle digest a enforcement transition ID.

## 6. Decision classes

Dôveryhodný gate používa viac stavov:

- **ALLOW** — complete valid evidence spĺňa policy;
- **DENY** — subject porušuje blocking requirement;
- **REVIEW** — automation nemá dostatok business alebo residual-risk contextu;
- **INCOMPLETE** — expected evidence chýba;
- **EXPIRED** — evidence alebo approval už neplatí;
- **INCONCLUSIVE** — control sa vykonal, ale observation contract nedal spoľahlivý verdict;
- **WAIVED** — explicitná scoped exception dočasne nahradila requirement;
- **REVOKED** — skoršie povolenie už nesmie byť použité.

Tool failure nie je `DENY` ani `ALLOW`; typicky vedie k `INCOMPLETE` alebo `INCONCLUSIVE` podľa contractu.

## 7. Human approval ako residual-risk decision

Human approval je vhodný pre business timing, coordinated partner change, regulatory evidence interpretation alebo akceptovanie explicitného residual risku. Nie je vhodný na ručné odhadnutie, či chýbajúci test „asi nevadí“.

Approver musí vidieť:

```text
exact subject a requested transition
+ complete evidence summary a raw references
+ policy decision a reasons
+ changed risk boundaries
+ active exceptions a expiry
+ target environment health
+ recovery eligibility a blast radius
+ business owner/technical owner responsibilities
```

Approval je viazaný na subject digest a expires pri zmene relevantného inputu. „Approve once, rerun later“ bez revalidation je stale authority.

## 8. Separation of duties a approval authority

Separation of duties nie je počet kliknutí. Dvaja approvers z rovnakého tímu s rovnakým conflictom nemusia priniesť independent judgment. Policy má definovať role a constraints:

```text
change author
≠ production risk approver

security exception requester
≠ exception approver

release operator
≠ policy administrator
```

Emergency path môže znížiť quorum, ale potrebuje incident ID, scoped subject, short expiry a mandatory retrospective review. Permanent „break-glass approved“ label ničí význam gate-u.

## 9. Exceptions a waivers

Exception má vlastný lifecycle:

```yaml
exception:
  id: EXC-2026-184
  requirement: image-vulnerability/CVE-2026-4411
  subjectDigest: sha256:pay1000api
  scope: production-canary-max-2-percent
  rationale: no reachable code path in current feature state
  compensatingControls:
    - feature flag disabled outside canary
    - WAF rule generation 981
  owner: payments-security
  approvedBy: security-duty-manager
  expiresAt: 2026-08-03T12:00:00Z
  remediationIssue: SEC-4411
```

Exception nie je zmazanie findingu. Gate musí stále zobrazovať original evidence, exception, scope a expiry. Pri artifact change sa waiver nemá automaticky preniesť, ak reachability alebo dependencies mohli byť iné.

## 10. Gate enforcement boundary

Decision engine a enforcement point sú odlišné. Pipeline môže správne vyhodnotiť `DENY`, ale downstream manual job môže stále deployovať. Alebo UI môže zobraziť approval, zatiaľ čo alternate API path approval nekontroluje.

Enforcement acceptance testuje všetky relevantné paths:

```text
standard pipeline
+ manual rerun
+ API trigger
+ scheduled job
+ emergency path
+ direct environment credential
```

Forbidden path sa testuje bezpečným dry-run alebo sandbox subjectom. Samotná existencia branch protection rule nepreukazuje, že environment mutation nemá iný credential path.

## 11. Gate telemetry a quality

Gate môže byť technicky dostupný a organizačne nefunkčný. Sledujú sa:

- allow/deny/incomplete/review distribution;
- missing-evidence frequency;
- false-positive a defect-escape rate;
- approval latency a queue;
- exception count, age a expiry breaches;
- overrides a break-glass usage;
- policy revision adoption;
- gate bypass attempts;
- correlation verdictu s production outcome.

Cieľ nie je maximalizovať deny rate. Gate má rýchlo a presne blokovať relevantný risk a poskytovať actionable reason.

## Doplnenie výkladu: gate je rozhodovacia policy nad evidence

Quality gate nie je test. Je to policy, ktorá z viacerých evidence items vytvorí decision, či subject môže pokračovať do ďalšieho stavu.

```text
exact subject
+ required evidence inventory
+ policy generation
→ PASS, FAIL, ERROR alebo MISSING
→ allow alebo block transition
```

Gate musí najprv overiť completeness. Nulový počet security findings môže znamenať bezpečný artifact alebo chýbajúci scanner report. Ak sa `MISSING` preloží na PASS, gate je false-green.

Approval je ľudský alebo externý policy verdict nad konkrétnym subjectom. Schválenie textu „release 10.0“ je slabé, ak tag môže zmeniť digest. Approval má obsahovať release manifest digest, target environment a evidence snapshot.

Approval freshness sa invaliduje pri zmene subjectu alebo relevantnej policy. Nový commit, rebuilt artifact, zmenený deployment plan alebo force-push môže vyžadovať nové schválenie. UI status „approved“ bez subject bindingu je nedostatočný.

Separation of duties znamená, že rovnaká osoba alebo identity nemá nekontrolovane vytvoriť change, meniť evidence a schváliť production transition. Automatizácia môže presadzovať reviewer independence a protected environment roles, no emergency break-glass potrebuje audit, expiry a následnú reconciliation.

Gate failure musí byť diagnostický: čo chýba, ktoré pravidlo zlyhalo, pre aký subject a aký owner má reagovať. Neurčité „quality gate failed“ predlžuje feedback a podporuje obchádzanie.

## 12. Connected incident `REL-PAY-67`

Atlas release `payments-10.0-rc4` mal chýbajúci image-vulnerability report, pretože scanner job zlyhal na infrastructure timeout. Final gate vytváral expected inventory z doručených reports, takže scanner sa v zozname neobjavil. Policy vrátila `ALLOW`.

Human approver videl release tag, zelené checks a poznámku „security passed“. Approval nebolo viazané na digest ani policy SHA. Po rerune build vytvoril nový digest z poisoned cache, no stale approval zostalo použiteľné. Deployment API navyše povoľovalo environment mutation service accountu mimo approval workflowu.

```text
scanner infra failure
→ dynamic expected inventory
→ false complete evidence
→ approval nad mutable release labelom
→ artifact digest sa zmenil
→ stale approval
→ alternate deploy path
```

Root cause bol decision subject a enforcement coverage. Ani automatic gate, ani human approval neboli viazané na exact bytes a complete expected controls.

## 13. Recovery a acceptance verdict

Containment revokuje promotion record, zablokuje alternate deploy identity, zachová gate input/output, approval a scanner logs a inventarizuje deployed digests. Recovery vytvorí nový release subject, rerun-ne scanner z trusted cold build-u, vyhodnotí fixed expected inventory a vyžiada fresh approval iba ak policy stále vráti `REVIEW`.

Gate/approval contract je prijatý iba vtedy, keď:

```text
subject je immutable a complete
+ expected evidence je definované pred execution
+ evidence validity/applicability/freshness sa overuje
+ policy bundle je versionovaný a loaded revision evidovaná
+ missing/tool failure nie je pass
+ human approval je subject-bound a expiring
+ exception je scoped, owned a dočasná
+ all mutation paths presadzujú decision
+ stale approval po artifact change je forbidden
+ druhý release prejde rovnakým mechanizmom bez manual bypassu
```

## 14. Troubleshooting flow

Pri false gate verdict-e sleduj:

```text
subject a requested transition
→ expected evidence inventory
→ producer/report validity
→ applicability a freshness
→ policy bundle/data/input
→ decision output
→ approval identity/scope/expiry
→ enforcement paths
→ actual deployment a outcome
```

Competing hypotheses môžu byť missing report, invalid schema, stale evidence, wrong subject digest, policy-data drift, undefined decision, broad exception, stale approval alebo bypass credential. Preserve raw evidence a policy bundle pred rerunom; nová execution generation môže incident zakryť.

## 15. Anti-patterny

### Gate podľa počtu zelených checks

Počet nevysvetľuje expected inventory ani chýbajúce controls.

### Human ako fallback scanner

Approver nemá nahrádzať chýbajúce technické evidence intuitívnym kliknutím.

### Permanent exception

Waiver bez expiry, scope a remediation sa stáva odstránením controlu.

### Approval viazané na tag

Mutable locator môže ukazovať na iný artifact než ten, ktorý approver posudzoval.

### Policy decision bez enforcement coverage

Správny `DENY` je neúčinný, ak alternate path stále deployuje.

## 16. Kontrolné otázky

1. Čo tvorí exact gate subject?
2. Prečo sa expected evidence definuje pred pipeline execution?
3. Aký je rozdiel medzi evidence validity a applicability?
4. Čo preukazuje `opa eval` a čo nie?
5. Prečo tool failure nemá byť pass?
6. Kedy je human approval vhodný?
7. Ako sa viaže approval na subject a expiry?
8. Čo musí obsahovať bezpečná exception?
9. Ako sa testuje enforcement coverage?
10. Prečo gate v `REL-PAY-67` považoval incomplete evidence za complete?
11. Ako artifact change invaliduje approval?
12. Ktoré metrics hodnotia kvalitu gate-u?

## Glossary impact

Relevantné pojmy: gate subject, expected evidence inventory, evidence validity, evidence applicability, evidence freshness, policy bundle generation, structured decision, incomplete verdict, inconclusive verdict, subject-bound approval, separation of duties, exception lifecycle, enforcement coverage, stale approval a gate defect escape.

## Primárne zdroje

- [Open Policy Agent documentation](https://www.openpolicyagent.org/docs/)
- [SLSA specification](https://slsa.dev/spec/)
- [NIST SP 800-53 Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)
- [GitHub Docs — Reviewing deployments](https://docs.github.com/en/actions/managing-workflow-runs/reviewing-deployments)
- [GitLab Docs — Deployment approvals](https://docs.gitlab.com/ci/environments/deployment_approvals/)
- [in-toto Attestation Framework](https://github.com/in-toto/attestation)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Environment a promotion](environment-and-promotion.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Pipeline as Code →](pipeline-as-code.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
