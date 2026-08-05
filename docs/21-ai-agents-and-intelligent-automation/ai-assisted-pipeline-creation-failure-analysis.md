# AI-assisted pipeline creation a failure analysis

AI-assisted pipeline engineering skracuje návrh, editáciu a diagnostiku CI/CD konfigurácie, ale nemení pipeline na dôveryhodnú len preto, že YAML prešiel schema validáciou alebo že model našiel presvedčivú príčinu zlyhania. Authoritative predmetom zostáva konkrétna pipeline generation, jej závislosti, execution, artefakty a následný business outcome.

Táto kapitola otvára incident `AGENT-DELIVERY-12`. DevOps Agent vytvoril build a deployment pipeline z prirodzeného jazyka. Po prvom zlyhaní Error Analyzer navrhol YAML opravu, ktorú používateľ prijal. Oprava odstránila chybne umiestnený step, ale zároveň presunula verification za podmienku, ktorá sa v produkčnom input sete nikdy nevyhodnotila ako true. Pipeline sa následne zobrazila ako úspešná, hoci release nemal health ani business verification.

Nosný lifecycle je:

```text
business change intent
→ exact repository, branch, pipeline a environment subject
→ AI-generated proposal
→ schema, policy a semantic validation
→ human review a immutable accepted diff
→ authorized save a publication
→ execution s pinned inputs a dependencies
→ step, stage, artifact a deployment evidence
→ effective-state a business verification
→ failure hypotheses, containment a recovery
→ second-execution acceptance
```

## 1. Pipeline ako versioned program

Pipeline nie je iba vizuálny graf. Je to program, ktorý kombinuje steps, stages, expressions, connectors, secrets, delegates, failure strategies, input sets, templates a environment bindings.

Každá analýza preto eviduje pipeline identifier, saved alebo Git-backed revision, template revisions, input-set generation a execution ID. Tvrdenie „pipeline bola rovnaká“ nemá význam bez týchto subjectov.

## 2. Natural-language intent

Používateľský prompt je neformálny intent, nie úplná špecifikácia. Výraz „nasadiť službu bezpečne“ neurčuje artifact identity, rollout strategy, timeout, verification source, approval ani rollback podmienky.

Agent musí nejasnosti zviditeľniť ako assumptions alebo unresolved fields. Nesmie ich potichu doplniť produkčne nebezpečnými defaults.

## 3. Scope a authority

Agent môže navrhovať iba resources, ktoré patria do aktuálneho account, organization a project scope. Authenticated user a jeho RBAC zostávajú authority pre čítanie a zápis.

Modelom odvodený project identifier alebo environment name nie je authorization. Server-side resource resolution musí overiť exact scope pred save aj pred execution.

## 4. Generation manifest

Proposal manifest viaže model, system instructions, AI Rules, pipeline schema, modules, templates a connectors. Zmena ktoréhokoľvek inputu vytvára novú proposal generation.

Bez manifestu sa nedá rozlíšiť model regression od zmeny template, pravidla alebo platform schema. Reprodukcia musí používať rovnaký composed input.

## 5. Harness AI Rules

Harness AI Rules poskytujú reusable context pre generovanie a editáciu resource. Pomáhajú agentovi dodržať názvoslovie, štandardné stages alebo cost a security conventions.

Rule je guidance pred save. Deterministic enforcement patrí do schema validation, RBAC, Policy as Code, branch rules a runtime gates.

## 6. Schema validation

Schema validation overí povolené typy, required fields a syntaktické vzťahy. Nevie potvrdiť, že connector smeruje na správny účet, expression sa pri reálnom inpute vyhodnotí správne alebo failure strategy zachová bezpečný outcome.

Schema-valid pipeline môže vynechať testy, používať mutable image tag alebo pokračovať po neúspešnej verifikácii. Semantic validation je samostatný gate.

## 7. Semantic validation

Semantic validator kontroluje business invariants: build musí produkovať immutable digest, production deployment musí mať approval a verification a destructive operation nesmie používať implicitný target.

Validator pracuje nad fully resolved pipeline graphom vrátane templates a input sets. Kontrola iba lokálneho YAML fragmentu môže prehliadnuť inherited failure strategy alebo expression override.

## 8. Policy enforcement

OPA alebo iný policy engine hodnotí normalized resource proti versioned policy bundle. Policy result obsahuje rule ID, bundle digest, subject a decision evidence.

AI môže Rego navrhnúť, ale policy sa aktivuje až po testoch, review a controlled promotion. Generated policy nesmie sama schváliť pipeline, ktorú má kontrolovať.

## 9. Step a stage construction

Agent môže vytvárať steps, stages a multi-module pipelines, no každý node má explicitný purpose, inputs, outputs a failure behavior. „Run shell command“ bez bounded scriptu a identity má široký blast radius.

Pipeline review hodnotí aj poradie a dependency edges. Správne jednotlivé steps môžu vytvoriť nesprávny outcome, ak verification alebo artifact publication beží v nesprávnej vetve.

## 10. Expressions a runtime inputs

Expression je program vyhodnotený až v konkrétnom execution contexte. Validator preto testuje representative input sets, null values, absent outputs a forbidden tenant alebo environment kombinácie.

Default, fallback a ternary expressions sú častým zdrojom confused-deputy chyby. Security-sensitive subject sa nemá získavať z voľného textu alebo model outputu.

## 11. Connector a secret stubs

Agent môže vytvoriť connector configuration, no Harness dokumentácia oddeľuje connector metadata od skutočného credential secretu. Secret value sa neposiela modelu a často sa doplní manuálne.

Acceptance overí effective provider identity. Existencia connectoru nepreukazuje, že credential patrí správnemu cloud accountu, clusteru alebo SCM organization.

## 12. Failure strategy

Failure strategy mapuje konkrétnu error condition na action, napríklad retry, ignore, manual intervention, rollback alebo abort. Scope stage a step strategy musí byť jasný, pretože step-level pravidlo môže overrideovať širšie očakávanie.

`Ignore Failure` môže udržať pipeline zelenú, ale nesmie zmeniť neznámy business outcome na success. Critical verification a mutation steps používajú fail-closed správanie.

## 13. Conditional execution

Conditional execution sa testuje proti reálnym runtime values. Branch, trigger type, service, environment a output expression môžu spôsobiť, že safety step nikdy nebeží.

Coverage matrix dokazuje, že každý production path obsahuje požadované approval, scan, verification a rollback preparation. Iba vizuálna prítomnosť step-u nestačí.

## 14. Pipeline summary

AI summary pomáha orientácii, ale nie je executable specification. Môže vynechať inherited template behavior, dynamic expressions alebo zriedkavú failure branch.

Review začína resolved graphom a diffom; summary je sekundárny index. Rozpor medzi summary a YAML sa rieši v prospech authoritative configuration.

## 15. Execution identity

Každý run má execution ID, trigger, actor, pipeline revision, input-set revision a resolved variables. Retry pôvodného runu a nový run aktuálnej pipeline sú rozdielne experiments.

Failure analysis nesmie porovnávať logy z jednej execution s YAML z inej saved generation. Evidence bundle viaže všetky artefakty na exact execution.

## 16. Error Analyzer

Harness Error Analyzer koreluje recent changes, dependencies, historical patterns a failing command a vytvára prioritized recommendations. Ide o hypothesis generator a evidence organizer.

Similarity score alebo confident explanation nie je root-cause proof. Hypotéza sa potvrdí reprodukciou, counterfactual testom alebo recovery evidence.

## 17. Change-impact correlation

Recent pipeline a code changes sú silný signál, ale časová blízkosť nie je kauzalita. Súbežne sa mohli zmeniť secret, delegate, provider quota alebo external dependency.

Triage vytvorí competing hypotheses a pre každú vyžiada diskriminačný dôkaz. Agent nesmie uzavrieť incident po nájdení prvého plausibilného diffu.

## 18. Dependency status

Dependency check zahŕňa connector validation, delegate connectivity, cloud API, registry, secret provider, artifact store a target cluster. Green vendor status page nepokrýva tenant-specific authentication alebo rate limits.

Read-back sa vykonáva s rovnakou identity a network path ako pipeline step. Lokálny test operátora nemusí reprodukovať execution environment.

## 19. Historical pattern matching

Past failure môže urýchliť diagnózu, ale podobný log text môže mať inú príčinu. Pattern record preto obsahuje exact signature, environment, fix a acceptance evidence.

Historický workaround sa nepoužije automaticky, ak sa zmenila pipeline, runtime alebo provider generation. Agent musí preukázať applicability.

## 20. Log completeness

Harness logy majú platform limits a môžu byť orezané. Chýbajúci začiatok logu môže odstrániť prvú chybu, pričom zostane iba sekundárny timeout.

Evidence bundle zaznamená truncation, line count, export source a checksum. Absencia message v incomplete logu nie je dôkazom, že event nenastal.

## 21. Root cause oproti triggeru

Trigger je prvý pozorovaný failure event; root cause je podmienka, ktorej odstránenie zabráni opakovaniu v relevantnom scope. Chybný command môže byť iba symptom neplatného inputu.

RCA obsahuje causal chain a counterfactual: pri rovnakých inputs a dependencies opravená generation prejde, zatiaľ čo pôvodná zlyhá kontrolovaným spôsobom.

## 22. Automated YAML repair

Harness môže zobraziť problem, solution a before/after YAML a po `Accept` aplikovať návrh. Accept znamená súhlas s konkrétnym diffom, nie validáciu výsledného behavioru.

Pred save sa rerunú schema, policy, semantic a path-coverage checks. Bez immutable diff digestu sa nedá neskôr dokázať, čo používateľ schválil.

## 23. Repair blast radius

Malá YAML zmena môže ovplyvniť templates, failure handling, parallelism alebo output references. Blast-radius analysis identifikuje všetky executions a environments, ktoré resource používajú.

High-risk oprava sa najprv aplikuje na isolated branch alebo cloned pipeline. Priama production editácia sa obmedzuje na emergency postup s auditom.

## 24. Generated diff review

Review zobrazuje semantic diff: zmena step type, connector, secret reference, condition, failure strategy a target. Textový diff s veľkým formátovacím šumom môže skryť podstatnú zmenu.

Reviewer vidí assumptions, unresolved bindings a expected impact. Skryté defaults a implicitné environment inheritance sú forbidden.

## 25. Save, publish a effective state

Accepted proposal, saved pipeline a execution-effective pipeline sú rozdielne states. Git-backed pipeline môže vyžadovať commit alebo PR; runtime môže stále používať starú template revision.

Acceptance zaznamená commit, Harness resource revision a execution-resolved graph. Iba úspešná save API response nestačí.

## 26. Test execution

Candidate sa spúšťa s representative success, failure a recovery scenarios. Test používa neprodukčné credentials a reversible resources, ale rovnaké policy, templates a runtime class.

Pre pipeline generation sa testuje aj druhý run bez cache a s alternate input setom. Jednorazový pass môže byť výsledkom warm cache alebo skipped branch.

## 27. Artifact evidence

Build success sa viaže na immutable artifact digest, provenance a test results. Mutable tag alebo filename bez checksumu neidentifikuje presný release subject.

Downstream stage musí konzumovať digest vytvorený v tom istom authorized execution alebo release manifest-e. Model nesmie doplniť „latest“.

## 28. Deployment verification

Deployment step success znamená prijatie mutation alebo skončenie orchestration, nie zdravú službu. Verification používa target-specific metrics, logs, synthetic transaction a business invariant.

No-data stav je explicitný `unknown` a môže failnúť gate. Nesmie sa zmeniť na healthy len preto, že analyzer nemal vstup.

## 29. Positive acceptance

Positive test vytvorí candidate pipeline, prejde schema, policy a semantic checks, vykoná build, publikuje pinned artifact a overí deployment aj business canary.

Evidence spája prompt, accepted diff, resource revision, execution ID, artifact digest, target a verification window. Druhý run potvrdí rovnaký contract.

## 30. Forbidden acceptance

Forbidden test skúsi vynechať verification, použiť production connector v test pipeline, vložiť mutable tag, nastaviť `Ignore Failure` na critical gate alebo odvodiť target z model outputu.

Očakáva sa pre-save alebo pre-execution rejection a nulová external mutation. Samotné warning UI nestačí.

## 31. Recovery acceptance

Po chybnej AI oprave sa pipeline zablokuje, affected executions sa inventarizujú a known-good revision sa obnoví. Ak mohli prebehnúť side effects, vykoná sa provider a business reconciliation.

Recovery test spustí pôvodný failure scenario na corrected pipeline a alternate scenario na susednom path-e. Tým sa overí, že oprava nevytvorila nový silent skip.

## 32. Practical validation record

Praktický record uchováva normalized decision a evidence, nie celý prompt s citlivými dátami:

```yaml
pipeline_candidate:
  pipeline_id: payments-release
  base_revision: 4d91c2a
  proposal_digest: sha256:7d4f...
  accepted_diff_digest: sha256:51b2...
  policy_bundle: release-policy@sha256:10c3...
  test_executions:
    - id: exec-success-1042
      expected: verified
    - id: exec-forbidden-1043
      expected: rejected-before-mutation
  artifact_digest: sha256:9ae1...
  production_verification: not-executed
```

Tento záznam môže preukázať dokumentovaný candidate a test intent. Neoznačuje produkčný outcome, kým neexistuje authoritative runtime evidence.

## 33. Primary sources

Aktuálna Harness dokumentácia opisuje DevOps Agent pre tvorbu a editáciu pipelines, schema validation, Error Analyzer, change-impact correlation, prioritized recommendations, YAML preview a explicitný `Accept`. Harness dokumentácia zároveň opisuje failure strategies, pipeline logs a Continuous Verification.

Primárne zdroje:

- https://developer.harness.io/3k-docs/ai/devops-agent/
- https://developer.harness.io/docs/continuous-integration/troubleshoot-ci/ai/
- https://developer.harness.io/docs/platform/pipelines/failure-handling/define-a-failure-strategy-on-stages-and-steps/
- https://developer.harness.io/docs/continuous-delivery/manage-deployments/deployment-logs-and-limitations/
- https://developer.harness.io/docs/continuous-delivery/verify/continuous-verification-faqs/

## Zhrnutie

AI-assisted pipeline creation je bezpečná iba vtedy, keď model proposal zostáva oddelený od deterministic validation, authorization a runtime proofu. Error analysis zrýchľuje hypotheses, no root cause vzniká až po reprodukcii a recovery acceptance.

V incidente `AGENT-DELIVERY-12` nebola hlavnou chybou samotná AI oprava. Zlyhal control chain, ktorý dovolil, aby accepted YAML diff obišiel semantic path coverage a aby zelená pipeline nahradila chýbajúcu deployment verification.
