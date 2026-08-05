# Policy generation a policy validation

Policy-as-code premieňa organizačné pravidlo na executable decision, ale agentický generátor nemení prirodzený jazyk automaticky na správnu bezpečnostnú hranicu. Model môže vytvoriť syntakticky platný Rego modul, ktorý testuje nesprávny input shape, používa nesprávny event alebo v praxi iba varuje. Authority preto nevzniká modelovým textom, ale až z versioned policy subjectu, negatívnych testov, policy-set bindingu, enforcement mode-u a pozorovaného decision outcome-u.

Incident `AGENT-GOV-13` začal požiadavkou: „Produkčný deployment povoľ iba pri immutable image digest-e a dvoch nezávislých schváleniach.“ Agent vytvoril Rego, ktoré prešlo jedným sample testom, no čítalo `input.image` namiesto resolved deployment inputu. Policy set bol pripojený iba na `On Save` a nastavený na `Warn and Continue`; staré services sa po zavedení policy automaticky neprehodnotili. Pipeline preto prešla s mutable tagom a jedným self-approvalom, hoci dashboard ukazoval úspešné policy evaluation.

Nosný lifecycle je:

```text
business control objective
→ exact governed subject a event
→ normalized input contract
→ AI-generated policy proposal
→ syntax, type a package validation
→ positive, negative, boundary a mutation tests
→ policy-set scope, severity a enforcement binding
→ immutable bundle generation
→ runtime decision a decision evidence
→ effective resource read-back
→ drift, exception a rollback handling
→ second-subject acceptance
```

## 1. Control objective

Policy nezačína kódom, ale kontrolným cieľom, ktorý pomenúva chránený outcome, risk, subject a ownera. „Použi bezpečné images“ je príliš neurčité; kontrola musí povedať, že production workload môže referencovať iba OCI digest z dôveryhodného registry namespace-u.

Control objective zároveň definuje cenu false positive a false negative. Blocking policy pre produkčný credential má inú toleranciu než advisory naming rule.

## 2. Governed subject

Policy subject je konkrétny resource alebo execution generation: pipeline YAML, resolved service input, connector, environment, artifact manifest alebo security result. Rovnaký názov resource nestačí, pretože policy musí vedieť, ktorú verziu a scope hodnotí.

Policy evidence obsahuje account, organization, project, entity ID, revision, event a input digest. Bez týchto fields sa rozhodnutie nedá reprodukovať.

## 3. Event boundary

Harness policy sets viažu policies na entity a events, napríklad `On Save`, `On Run` alebo `On Step Start`. Rovnaká policy môže pri inom evente vidieť iný input a chrániť inú fázu lifecycle-u.

`On Save` kontroluje deklaráciu, nie nutne resolved runtime values. `On Run` a policy step môžu vyhodnocovať execution-time data, ale iba ak je payload úplný a binding skutočne enforced.

## 4. Existing resources

Nová policy sa nemusí automaticky aplikovať na už existujúce entities. Harness dokumentácia pri viacerých resource typoch uvádza, že policy sa aktivuje až pri ďalšom save alebo run evente.

Rollout preto potrebuje inventory a re-evaluation plan. „Policy je zapnutá“ neznamená, že celý fleet už prešiel novou kontrolou.

## 5. Input contract

Rego rozhoduje nad `input`, takže schema inputu je bezpečnostný contract. Field names, types, null semantics, resolved expressions, redaction a default values musia byť explicitné.

Agent nesmie hádať input shape zo sample screenshotu. Contract sa exportuje z authoritative engine-u a versionuje spolu s fixtures.

## 6. Normalization

Rôzne producers môžu reprezentovať digest, environment alebo identity odlišne. Normalization prebehne pred policy evaluation v deterministic vrstve, nie implicitne v prompt-e.

Canonical input odstráni aliasy, normalizuje case, rozlíši absent od empty a zachová raw source reference. Policy potom rozhoduje nad stabilným modelom.

## 7. Policy proposal

AI môže z control objective vytvoriť prvý Rego návrh, test matrix a vysvetlenie assumptions. Tento output je návrh, nie enforced authority.

Proposal record viaže model, prompt, retrieved examples, tool generation a source objective. Zmena modelu alebo contextu vytvára novú proposal generation.

## 8. Rego semantics

Syntakticky platné Rego môže mať opačný význam než požiadavka. Rizikové sú default rules, negation, undefined values, set membership, partial rules a neúplné quantifiers.

Reviewer číta decision semantics, nie iba natural-language explanation. Pri deny modeloch sa overí, čo znamená empty deny set; pri allow modeloch sa overí default deny.

## 9. Default deny

High-impact authorization a deployment gates preferujú explicitný deny-by-default alebo equivalent fail-closed contract. Undefined alebo evaluation error sa nesmie premeniť na allow bez schválenej exception policy.

Fail-closed neznamená, že každý telemetry outage musí zastaviť všetko. Availability policy môže mať explicitný degraded mode, ale ten je samostatne navrhnutý a auditovaný.

## 10. Syntax a formatting

`opa fmt` a parser checks odstránia syntaktické chyby a canonicalize source. Neoverujú však input semantics, business intent ani enforcement binding.

Generated policy sa nikdy nepromuje iba preto, že sa kompiluje. Syntax je prvá gate, nie finálna acceptance.

## 11. Unit tests

OPA poskytuje native policy testing. Testy používajú explicitné inputs a očakávané decisions, aby sa zmena pravidla dala overiť automatizovane.

Každý allow case má zodpovedajúci deny case. Test bez negatívnej dvojice často iba potvrdzuje happy-path fixture.

## 12. Boundary tests

Boundary tests pokrývajú absent fields, null, empty list, mixed-case environment, unknown registry, malformed digest, duplicate approvals a expired approval.

Agent generuje boundary inventory, ale domain owner potvrdí, ktoré hrany sú relevantné. Test matrix je versioned artifact.

## 13. Mutation tests

Policy mutation test cielene invertuje operator, odstráni clause alebo zmení field path. Test suite musí takú chybu zachytiť.

Ak všetky tests prejdú aj po odstránení kľúčovej condition, suite nepreukazuje control objective. Mutation score je signál kvality, nie automatická production approval.

## 14. Differential tests

Pri nahrádzaní policy generation sa stará a nová policy spustia nad rovnakým corpusom. Rozdiely sa klasifikujú ako intended, regression alebo unknown.

Agent môže zoskupiť diff, no owner schvaľuje zmenu behavioru. Silent decision drift je zakázaný.

## 15. Golden corpus

Golden corpus obsahuje reálne anonymizované inputs, historické incidents a synthetic edge cases. Každý record má expected decision a rationale.

Corpus musí pokrývať tenant, environment a resource variants. Jeden sample z policy editoru je demo, nie production evidence.

## 16. Policy set

Harness policies sú enforced až po pridaní do policy setu. Policy set určuje entity type, event, scope, severity a action.

Existencia Rego súboru bez policy-set bindingu nepredstavuje aktívnu kontrolu. Audit evidence musí ukázať aj policy-set generation.

## 17. Scope

Account-level policy môže ovplyvniť všetky organizations a projects; project-level policy iba konkrétny scope. Nesprávne umiestnenie môže vytvoriť blind spot alebo nečakaný blast radius.

Promotion preto explicitne uvádza scope a child inheritance. Negative test overí susedný project, ktorý policy nesmie ovplyvniť.

## 18. Severity a action

Harness rozlišuje `Warn and Continue` a `Error and Exit`. Warning je observation, nie prevention.

Control objective musí určiť, ktoré findings blokujú. Dashboard „policy failed“ môže koexistovať s úspešným save alebo runom, ak action ostala warning.

## 19. Enforcement state

Policy set môže existovať a nebyť enforced. Effective-state read-back preto kontroluje enabled state, event binding, scope, policy revisions a severity.

Configuration screenshot nie je dostatočný. Automatizovaný verifier číta authoritative API alebo export.

## 20. Bundle generation

OPA bundles spájajú policies a data do distribuovateľnej generation. Bundle digest, revision a activation status identifikujú effective policy set na každej OPA instance.

Mutable URL alebo branch bez resolved digest nevytvára reprodukovateľný decision subject. Promotion pinne immutable bundle identity.

## 21. Distribution status

OPA status reporting môže potvrdiť download a activation alebo uviesť chybu. Control plane success sa porovná s každou relevantnou evaluator instance.

Partial rollout je samostatný stav. Ak polovica fleet-u používa novú policy a polovica starú, aggregate success je zakázaný.

## 22. Decision evidence

Runtime decision record obsahuje input digest, policy bundle revision, result, reason codes, evaluation time a evaluator identity. Sensitive input sa rediguje podľa policy.

Natural-language explanation modelu nie je authoritative decision log. Explanation môže odkazovať na decision ID a presné violated rules.

## 23. Error semantics

Parser error, missing data, timeout a evaluator unavailable sú oddelené od explicitného allow alebo deny. Unknown sa nesmie mapovať na allow bez control-specific rule.

Monitoring sleduje decision errors a stale bundle age. Zelený business metric nemôže zakryť vypnutú policy enforcement vrstvu.

## 24. Exceptions

Exception má subject, ownera, rationale, expiry, approved scope a compensating controls. Globálne vypnutie policy nie je ekvivalent jednej výnimky.

Expired exception failuje closed alebo eskaluje podľa control designu. Agent môže pripraviť request, ale nemôže si výnimku schváliť.

## 25. Policy changes

Každá zmena policy prechádza code review, tests, corpus comparison a staged rollout. Generated diff sa hodnotí na decision behavior, nie na počet changed lines.

High-risk policy má two-person approval a oddeleného evaluator ownera. Model identity sa nezapočítava ako ľudský reviewer.

## 26. Shadow evaluation

Nová policy môže najprv bežať v shadow mode a zaznamenávať hypothetical decisions bez blokovania. Shadow výsledky odhaľujú false positives a blind spots.

Shadow success nepreukazuje enforcement. Promotion record musí explicitne prepnúť action a potvrdiť effective state.

## 27. Canary enforcement

Enforcement sa aktivuje na vybranom project-e alebo cohort-e. Sledujú sa denial rate, error rate, latency, exception requests a missed known-bad inputs.

Canary sa zastaví pri unexpected deny alebo evaluation error. Rozšírenie scope-u je nová change operation.

## 28. Performance

Policy evaluation je na critical path save alebo execution. OPA poskytuje benchmarking a profiling, ale latency budget musí zodpovedať platform SLO.

Optimization nesmie meniť semantics. Before/after corpus sa porovná decision-by-decision.

## 29. Policy drift

Drift vzniká medzi Git source, Harness policy editorom, policy setom, bundle-om a evaluator instance. Každá vrstva má vlastnú generation.

Reconciliation porovnáva expected a effective revisions. Manual hotfix sa buď commitne späť do source of truth, alebo automaticky revertne.

## 30. Incident containment

Pri podozrení na false allow sa zastaví promotion, freeze-ne mutation surface a uloží decision evidence. Nie je bezpečné iba prepísať prompt a spustiť rovnaký execution.

Affected resources sa identifikujú podľa decision logs a event window. Následne sa overí ich effective state.

## 31. Recovery

Recovery môže aktivovať predchádzajúci known-good bundle, opraviť input adapter alebo zmeniť policy-set binding. Každý variant má vlastný rollback subject.

Po rollbacku sa opakuje known-bad input, known-good input a druhý project. Obnova enforcementu sa preukáže decision evidence a resource read-backom.

## 32. Positive acceptance

Test vytvorí production deployment s immutable digestom, dvoma oprávnenými approvals a správnym environment scope-om. Policy rozhodne allow nad exact bundle revision a execution pokračuje.

Druhý test s mutable tagom failne `Error and Exit`. Decision log, policy set a resource state sa zhodujú.

## 33. Forbidden acceptance

Test použije chýbajúci field, stale approval, self-approval, nesprávny project a policy-set warning mode. Systém nesmie deklarovať control satisfied.

AI-generated policy s jediným positive sample testom nesmie byť promoted. Unknown evaluation nesmie skončiť allow.

## 34. Recovery acceptance

Do fleet-u sa nasadí chybný bundle a canary odhalí false allow. Promotion sa zastaví, previous bundle sa aktivuje a affected execution zostane quarantined.

Po oprave prejde differential corpus, mutation test a second-subject test. Exception a incident records ostanú auditovateľné.

## 35. Practical policy envelope

Policy envelope spája control objective, exact input contract, source a bundle generation, policy-set binding a acceptance evidence. Bez tohto envelope-u sa Rego text nedá bezpečne zameniť za aktívnu kontrolu.

Nasledujúci príklad zámerne uvádza blocking action a negatívne fixtures. `generated_by` je provenance, nie authority:

```yaml
policy:
  id: prod-image-and-approval
  source_commit: 4f2d...
  bundle_digest: sha256:9c31...
  generated_by:
    model: model-generation-17
    prompt_digest: sha256:18aa...
  input_schema: deployment-input-v4
  policy_set:
    scope: account/org/project
    entity: pipeline
    event: OnRun
    action: ErrorAndExit
    enforced: true
  acceptance:
    positive:
      - digest-and-two-independent-approvers.json
    negative:
      - mutable-tag.json
      - self-approval.json
      - expired-approval.json
      - missing-field.json
    mutation_score_required: 1.0
```

Envelope sa uloží spolu s test results a effective-state read-backom. Samotný modelový návrh sa nikdy neoznačí ako enforced.

## 36. Primary sources

Harness Policy As Code overview na https://developer.harness.io/docs/platform/governance/policy-as-code/harness-governance-overview/ je authority pre OPA service, policy sets, entity/event binding, scope a `Warn and Continue` verzus `Error and Exit`. Resource-specific dokumentácia, napríklad https://developer.harness.io/docs/platform/governance/policy-as-code/policy-as-code-for-environments/ a https://developer.harness.io/docs/platform/governance/policy-as-code/policy-as-code-for-services/, vysvetľuje, že existing resources sa neprehodnotia automaticky mimo príslušného save alebo run eventu.

OPA policy testing je popísané na https://www.openpolicyagent.org/docs/policy-testing a performance validation na https://www.openpolicyagent.org/docs/policy-performance. Distribúciu a activation evidence podporujú OPA status a discovery dokumenty na https://www.openpolicyagent.org/docs/management-status a https://www.openpolicyagent.org/docs/management-discovery. Tieto zdroje definujú mechanizmy; správnosť konkrétneho business controlu musí preukázať vlastný corpus, enforcement binding a runtime decision evidence.

## Zhrnutie

AI môže zrýchliť authoring policy, testov a vysvetlení, ale authority vzniká až z presného subjectu, input contractu, negatívnych testov, blocking policy-set bindingu a effective decision evidence. Najnebezpečnejší stav nie je syntax error, ale policy, ktorá vyzerá enforced a v skutočnosti hodnotí nesprávny input alebo iba varuje.

Ďalšia kapitola rozšíri tento model o human approval, audit a rollback.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Incident triage a evidence collection](incident-triage-evidence-collection.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Human approval, audit a rollback →](human-approval-audit-rollback.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
