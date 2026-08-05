# DevOps Agent pre pipeline a resource operations

Harness DevOps Agent urýchľuje authoring a troubleshooting v UI, ale jeho bezpečná rola je navrhovať bounded changes nad explicitným scopeom. Identity, RBAC, policies, resource versions, secret handling, apply a read-back zostávajú deterministic platform operations.

V incidente `AGENT-HARNESS-11` bol návrh syntakticky validný a používateľ ho prijal. Agent však použil stale project context, guidance-only rule a connector s nekompletným secretom. Výsledok ukazuje, že conversation acceptance nie je resource acceptance.

Nosný lifecycle tejto kapitoly je:

```text
user intent a explicitný target scope
→ current resource generation a dependencies
→ effective AI Rules a deterministic policies
→ bounded proposal a semantic diff
→ schema, policy a permission validation
→ informed Accept nad immutable digestom
→ authorized save alebo Git mutation
→ effective resource a provider read-back
→ safe execution, rollback a second-change acceptance
```

## 1. DevOps Agent boundary

DevOps Agent je conversational authoring surface v Harness UI. Dokáže navrhovať a meniť pipeline steps, stages, pipelines, policies a vybrané resources, ale jeho output zostáva proposal pod platform RBAC a validation.

Agent nie je pipeline runtime worker. Conversation success sa nesmie zameniť za uložený resource, spustenú pipeline alebo potvrdený deployment.

## 2. Exact mutation subject

Každá operácia viaže account, organization, project, module, resource type, identifier, current generation a expected parent version. Prompt „uprav pipeline“ bez exact targetu je nebezpečný pri viacerých scopes.

Before-state read-back a optimistic concurrency zabránia prepísaniu novšej ľudskej zmeny návrhom vytvoreným zo stale conversation contextu.

## 3. Conversation context

Agent môže používať aktuálnu pipeline a ďalší platformový kontext. Kontext musí byť zobrazený alebo sumarizovaný tak, aby používateľ vedel, z čoho návrh vychádza.

Predchádzajúca konverzácia nesmie potichu určiť production environment alebo connector. Security-critical scope sa vyberá explicitne a zobrazuje v approval diff-e.

## 4. Create verzus edit

Create operation nemá existujúcu generation, preto musí overiť naming collision, scope a required dependencies. Edit operation musí viazať exact before generation a odmietnuť stale apply.

Upsert bez explicitnej semantics je zakázaný pre kritické resources. Inak nejasný prompt môže vytvoriť nový connector namiesto opravy existujúceho.

## 5. Step a stage generation

Agent môže vytvárať steps a stages naprieč podporovanými modules a nastavovať failure strategy, conditions alebo delegate selectors. Schema validation overí štruktúru, nie business správnosť hodnoty.

Review musí vysvetliť execution order, dependencies, side effects, credentials a rollback. Vygenerovaný stage s validným YAML môže stále deployovať nesprávny artifact do nesprávneho environmentu.

## 6. Pipeline orchestration

Pri multi-module pipeline sa kontroluje DAG, runtime inputs, templates, barriers, approvals a failure handling ako jeden composed graph. Agent nesmie hodnotiť izolovaný step bez jeho upstream a downstream semantics.

Pipeline diff obsahuje removed aj added paths. Hromadná zmena sa rozdelí, ak reviewer nedokáže rozumne posúdiť blast radius.

## 7. Schema validation

Harness schema validation zachytí neplatné fields, typy a combinations. Nepreukazuje, že connector patrí správnemu accountu, secret má hodnotu, environment je správny alebo policy intent bol splnený.

Validation report preto dopĺňajú semantic invariants a provider read-backs. Passing schema je necessary, nie sufficient gate.

## 8. AI Rules

AI Rules vkladajú account, organization, project alebo personal instructions do generation contextu. Pomáhajú štandardizovať naming, cost limits, tests alebo security guidance.

Rule priority, scope a effective snapshot sa evidujú pri proposal. Keď rules konfliktujú, agent nesmie ticho zvoliť menej prísnu; deterministic policy rozhodne pred save alebo execution.

## 9. OPA Rego generation

DevOps Agent môže generovať OPA Rego policies, no generated policy je source code so security impactom. Potrebuje review, unit tests, negative cases, bundle/version control a controlled enforcement.

Agent-generated allow rule sa nesmie nasadiť priamo do production. Testy zahŕňajú unknown fields, missing values, alternate stage types a bypass cez templates alebo runtime inputs.

## 10. Rules verzus Rego

AI Rule usmerňuje model pred vytvorením návrhu. Rego policy vyhodnocuje konkrétny resource alebo execution deterministicky. Ich roles sa neprekrývajú.

Incident nastal, keď „production musí mať approval“ bolo iba AI Rule. Agent vytvoril validnú pipeline bez gate; až OPA enforcement by poskytol authoritative deny.

## 11. Resource creation

Agent môže vytvárať Services, Environments, Connectors a Secrets podľa platform capability. Každý resource type má vlastné required fields, permission a post-create readiness.

Resource `created` neznamená `usable`. Service potrebuje valid deployment context, environment infra definition, connector working credentials a secret hodnotu.

## 12. Secret creation

Pri secret creation sa vytvorí secret object bez value a hodnota sa dopĺňa mimo AI model path. Review nesmie zobrazovať alebo požadovať secret plaintext v prompt-e.

Acceptance overí incomplete state ako explicitný blocker. Pipeline nesmie pokračovať len preto, že secret identifier existuje.

## 13. Connector creation

Connector proposal obsahuje type, endpoint, auth reference, delegate selectors a scope. Connection test sa spúšťa s redacted evidence a provider identity read-backom.

Generic `connection successful` bez endpoint fingerprintu môže potvrdiť nesprávny účet. Exact identity sa porovná s expected tenant alebo registry.

## 14. GitOps operations

DevOps Agent môže spravovať GitOps applications, ApplicationSets, clusters a repositories podľa permissions. Git desired state, Harness resource a target cluster state zostávajú samostatné authorities.

Write do Harness control plane nemusí znamenať Git commit alebo reconciliation. Acceptance sleduje commit SHA, agent sync revision a effective workload state.

## 15. Error Analyzer

Failure analysis používa execution graph, logs a zmeny na formulovanie hypotheses. Výstup je diagnostický návrh, nie root-cause proof.

Agent musí odlíšiť symptom, first failing boundary, competing hypotheses a confidence. Automated fix sa nepoužije, kým evidence neukáže, že nemení unrelated behavior.

## 16. Pipeline summarizer

Natural-language summary zjednodušuje review, ale nesmie nahradiť YAML, execution graph ani policy evidence. Summary môže vynechať conditional path alebo runtime input.

Reviewer používa summary ako navigáciu. Authoritative approval sa viaže na exact diff a resolved graph.

## 17. Accept a apply

Používateľské Accept alebo Apply musí viazať immutable proposal digest, target generation a actor. Medzi generation a apply sa znovu overí current resource generation a permissions.

Stale proposal sa nerebasuje automaticky modelom. Vráti sa conflict a vyžiada nový review nad aktuálnym before-state.

## 18. Human review quality

Review UI zobrazuje resource scope, before/after diff, removed controls, new connectors/secrets, policies a expected runtime impact. Pri veľkom diff-e sa vyžaduje rozdelenie návrhu.

Click bez viditeľného target scope nie je informed approval. Audit zaznamená proposal digest, actor a apply result.

## 19. RBAC enforcement

DevOps Agent používa permissions používateľa alebo platformou definovanú delegated boundary. Model suggestion nemôže prideliť sebe novú rolu.

Forbidden test skúsi create/edit/execute s view-only principalom a overí nulový write. Text „nemáte oprávnenie“ nestačí bez audit a resource read-backu.

## 20. Git-backed resources

Ak pipeline alebo template používa remote Git store, authoritative mutation môže byť commit alebo pull request, nie iba Harness database write. Agent musí rešpektovať branch protection a review flow.

Composed state viaže repo, branch, path, commit SHA, Harness resolved generation a publication. Rollback používa Git history a následný effective-state read-back.

## 21. Runtime inputs

Agent môže navrhnúť runtime inputs, defaults a expressions. Authority fields, production targets alebo privileged connectors nesmú mať nebezpečné implicitné defaults.

Input validation zahŕňa allowed values, requiredness, scope a type. Empty string sa nesmie transformovať na production alebo global scope.

## 22. Failure strategies

Generated failure strategy určuje retry, ignore, manual intervention alebo rollback semantics. Retry safe iba vtedy, keď step side effects používajú idempotency alebo read-back.

`Ignore Failure` môže vytvoriť zelenú pipeline s neuskutočneným business outcome. Policy obmedzuje jeho použitie na explicitne non-critical checks.

## 23. Delegate selectors

Delegate selector rozhoduje, kde step vykoná network a credential operations. Nesprávny selector môže meniť reachability, trust zone alebo target account.

Review porovná selector s connector a environment requirements. Forbidden test odmietne privileged production delegate v non-prod proposal.

## 24. Policy a compliance evidence

Generated pipeline prechádza policy evaluation nad resolved resource, nie iba source snippetom. Evidence obsahuje policy bundle generation, input document digest a decision.

Policy bypass cez template expansion, runtime expression alebo alternate module sa testuje negatívne. Rules a summaries nie sú compliance attestation.

## 25. Dry run a preview

Pred mutation sa podľa resource type použije preview, schema validate, plan alebo read-only API. Preview sa pinne na exact before-state a dependencies.

Dry run nie je outcome proof, ale zmenšuje riziko. Ak preview a apply používajú odlišné inputs alebo generations, acceptance je neplatná.

## 26. Canary

Low-risk pipeline alebo isolated project overí agent-generated pattern. Canary používa neprodukčný connector, synthetic secret a reversible resource.

Promotion do production vyžaduje second review nad environment-specific diffom. Copy-paste canary success sa nepovažuje za production acceptance.

## 27. Rollback

Každá accepted zmena má inverse plan: Git revert, resource generation restore, connector disable alebo pipeline rollback. Rollback nevymazáva audit evidence.

Po rollbacku sa overí effective resource, execution behavior a downstream state. Stará mutable agent alebo rule generation sa zablokuje.

## 28. Incident triage

Pri nesprávnom resource sa najprv identifikuje conversation, proposal digest, actor, scope, before/after generation, rules, policies a platform audit. Následne sa overia external writes.

Tím nemení prompt ako prvý krok. Prompt môže byť iba jedna z príčin vedľa stale contextu, wrong connectora, RBAC scope alebo policy gapu.

## 29. Competing hypotheses

Nesprávna pipeline môže vzniknúť z ambiguous promptu, stale contextu, wrong project, schema defaultu, rule conflictu, missing policy, connector identity alebo race s paralelnou editáciou. Každá hypothesis má vlastný dôkaz.

Root cause sa nepriraďuje modelu len preto, že návrh bol AI-generated. First authoritative divergence určí remediation ownera.

## 30. Positive acceptance

Agent vytvorí low-risk pipeline stage v isolated project-e. Proposal diff, rules snapshot, schema validation, OPA pass, actor permission, save result a resolved YAML sa zhodujú.

Pipeline sa potom spustí s safe inputom a business read-backom. Druhý prompt upraví iný step bez narušenia prvého.

## 31. Forbidden acceptance

Agent nesmie aplikovať stale proposal, cross-project target, secret plaintext, policy-bypassing stage ani privileged connector pre unauthorized actor. Každý test overí nulový resource write.

Deny musí byť konzistentný aj pri synonymnom prompt-e alebo bulk edit requeste. Model wording nesmie meniť security decision.

## 32. Recovery acceptance

Po simulovanom wrong-scope create sa resource quarantinuje, správny desired state sa obnoví a orphan resource sa odstráni cez schválený cleanup. Audit chain ostane zachovaný.

Second-operation test vytvorí nový resource v správnom scope a potvrdí, že stale conversation alebo proposal už nemožno znovu použiť.

## 33. Prevádzkové limity

Conversation a generation majú token, latency a operation limits. Bulk mutation má maximálny počet resources a vyžaduje explicitné potvrdenie.

Timeout po apply requeste vytvára unknown state. Retry najprv vykoná resource read-back podľa operation ID alebo target generation.

## 34. Čo DevOps Agent proof vyžaduje

Proof zahŕňa exact proposal, deterministic validation, informed approval, authorized mutation, effective resource read-back a business-safe execution. Samotná odpoveď „pipeline bola vytvorená“ nestačí.

Dokumentačná kontrola môže overiť model, ale nepreukazuje behavior konkrétneho Harness accountu alebo provider pathu.

## Primárne zdroje

- https://developer.harness.io/3k-docs/ai/devops-agent/
- https://developer.harness.io/docs/platform/harness-ai/harness-create-with-ai/
- https://developer.harness.io/docs/platform/harness-ai/harness-ai-rules/
- https://developer.harness.io/docs/platform/pipelines/harness-yaml-quickstart/
- https://developer.harness.io/docs/platform/role-based-access-control/rbac-in-harness/
- https://developer.harness.io/docs/platform/governance/audit-trail/

## Zhrnutie

Kapitola ukazuje, že devops agent pre pipeline a resource operations sa nesmie redukovať na dostupnosť AI funkcie alebo úspešný model response. Authoritative proof vzniká až spojením exact subjectu a generation, deterministic scope a identity, policy enforcementu, execution evidence, downstream read-backu, failure semantics a opakovateľného recovery testu.

## Navigácia

- Predchádzajúca kapitola: [Harness AI platform overview](harness-ai-platform-overview.md)
- Nasledujúca kapitola: [Worker Agents v pipelines](worker-agents-pipelines.md)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Harness AI platform overview](harness-ai-platform-overview.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Worker Agents v pipelines →](worker-agents-pipelines.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
