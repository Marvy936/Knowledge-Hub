# Source control a environments

Source control v n8n prenáša workflow definitions a súvisiace configuration artifacts medzi instances cez Git, ale nevytvára automaticky identický runtime. Effective production state závisí aj od branch, pull generation, saved a published workflow verzie, credentials, variables, project permissions, sub-workflow references, node versions a external dependencies.

Táto kapitola uzatvára incident `AGENT-N8N-08`. Development instance pushla opravený parent a child workflow do Git. Production pull načítal saved definitions, no workflowy neboli samostatne publikované, lokálny credential stub bol namapovaný na širší tenant credential a jedna variable zostala na starej hodnote. Git commit bol správny, ale effective runtime naďalej používal zmiešanú generation.

Nosný promotion lifecycle je:

```text
business change a composed dependency inventory
→ saved workflow definitions v development instance
→ source-control push do exact branch a commit
→ external review, tests a merge policy
→ target-instance pull a conflict/deletion decision
→ local credential, variable a dependency binding
→ publish alebo activate intended workflow versions
→ loaded/effective state read-back
→ canary business validation a rollback proof
```

## 1. Source control purpose

Git poskytuje históriu, diff, review context a promotion channel pre workflow definitions. Umožňuje oddeliť authoring od production a reprodukovať, aký deklarovaný obsah bol schválený.

Git však nie je runtime database ani secret manager. Commit nepreukazuje, že target instance obsah načítala, publikovala a vykonáva s intended local bindings.

## 2. Environments

Environment je samostatný execution context, typicky development, staging alebo production, s vlastnou instance configuration, credentials, variables, data, users a external endpoints. Izolácia znižuje riziko, že test mutation zasiahne production resource.

Environment labels samy osebe nič nepresadzujú. Každá instance potrebuje network, identity, data a provider-side boundaries zodpovedajúce svojmu účelu.

## 3. Git branch binding

n8n instance sa pri source-control setup-e viaže na Git repository a branch podľa zvoleného patternu. Branch je desired-state channel pre túto instance, nie automaticky deployment lock.

Branch protection, pull requests a required checks sa typicky presadzujú v Git providerovi. n8n push/pull mechanizmus nenahrádza externý review a merge process.

## 4. Multi-instance, multi-branch pattern

Development a production instances môžu byť viazané na odlišné branches. Change sa pushne do development branch, prejde pull requestom a až potom sa production branch pullne do production instance.

Tento model pridáva explicitný promotion gate a podporuje viac environments. Zvyšuje však počet branch synchronization krokov a riziko, že target pull alebo publish zostane zabudnutý.

## 5. Multi-instance, single-branch pattern

Viac instances môže sledovať jednu branch a každá si z nej pullne rovnaký deklarovaný obsah. Model je jednoduchší, ale accidental push môže byť rýchlejšie dostupný production automatizácii.

Bez samostatnej branch gate musí organizácia posilniť review, protected instance a deployment automation. Rovnaká branch stále neznamená rovnaké local credentials a variables.

## 6. One-way promotion

n8n odporúča navrhnúť flow tak, aby instance prevažne buď pushovala do Git, alebo pullovala z Git, nie oboje. Jednosmerný tok znižuje conflicts a accidental overwrite.

Development je authoring authority a production deployment target. Emergency production edit sa eviduje ako break-glass, exportuje a následne reconciliuje späť do source authority namiesto trvalého obojsmerného chaosu.

## 7. Saved workflow state

Saved state je posledná definícia uložená v instance editori. Obsahuje nodes, connections, parameters a settings, ktoré source-control push prenáša podľa aktuálnych n8n semantics.

Saved neznamená automaticky published alebo active runtime. Reviewer musí vedieť, či hodnotí draft, release candidate alebo skutočne nasadenú version.

## 8. Published workflow state

Published version je tá, ktorú production triggers a calls používajú podľa n8n workflow lifecycle. Aktuálna oficiálna dokumentácia upozorňuje, že source-control push prenáša current saved version, nie automaticky published version.

Po pull-e do remote instance sa intended workflow verzie publikujú samostatne. Bez tohto kroku môže Git a saved UI ukazovať opravu, zatiaľ čo runtime stále vykonáva staršiu version.

## 9. Effective runtime state

Effective state je kombinácia published workflowu, resolved credentials, variables, sub-workflows, node implementations, environment configuration a worker generation. Je to jediný state, ktorý skutočne vykonáva business operations.

Promotion sa preto uzatvára runtime read-backom a canary execution. Commit SHA je necessary evidence, nie sufficient outcome proof.

## 10. Push operation

Push vyberie zmenené workflows a ďalšie podporované artifacts a vytvorí Git commit na pripojenej branch. Commit message vysvetľuje business zmenu a target scope.

Pred pushom sa kontroluje, že saved definitions neobsahujú test endpoints, pinned sensitive data, disabled safety nodes alebo neúmyselné unrelated changes. Git diff musí byť čitateľný a reviewable.

## 11. Pull operation

Pull načíta zmeny z branch do target instance. Operátor alebo deployment automation vyhodnotí new, modified a deleted resources a následné local configuration requirements.

Pull success znamená import deklarácie, nie business readiness. Target instance môže stále chýbať credential values, variables, publication alebo compatible node package.

## 12. Pull conflict

Ak target instance obsahuje lokálne edits, pull môže prepísať alebo konfliktne zmeniť saved state podľa platform semantics. Preto production nemá byť bežným authoring miestom.

Pred pullom sa zachová current inventory a execution impact. Konflikt sa rieši v source authority alebo controlled recovery, nie náhodným výberom „novšej“ UI verzie.

## 13. Deletion semantics

Resource odstránený z repository nemusí byť v každom promotion flow automaticky bezpečne odstránený z target instance bez explicitného rozhodnutia. Deletion môže ovplyvniť executions, callers, credentials, tags a audit history.

Delete manifest obsahuje dependency analysis, backup a rollback plan. Stale workflow, ktorý zostane published cez starú route, je drift; príliš agresívne delete môže odstrániť evidence.

## 14. Private repository

Workflow JSON môže odhaliť business logic, endpoints, resource names, variable names a credential stubs. Repository je preto private, ak organizácia výslovne nechce tento obsah zverejniť.

Private repository neospravedlňuje vloženie plaintext secretov. Access sa riadi least privilege, deploy keys alebo tokens sa rotujú a branch audit sa uchováva.

## 15. Git authentication

Instance sa pripája cez podporovaný SSH alebo HTTPS model a potrebuje scoped Git credential. Write access je potrebný pre push instance, read access môže stačiť pre pull-only target podľa konkrétneho setupu.

Deploy key alebo token je samostatný secret s ownerom, expiry a repository scope. Nemá sa zdieľať medzi nesúvisiacimi instances alebo repositories.

## 16. Roles a source-control authority

Dostupnosť source-control funkcie a push/pull oprávnenia závisia od n8n edition a role modelu. Current documentation rozlišuje instance owner/admin authority a obmedzenejšie project-level možnosti.

Design musí overiť exact plan a permissions. Runbook, ktorý predpokladá pull právo pre rolu bez tejto capability, zlyhá počas incidentu alebo promotion.

## 17. Protected production instance

Protected instance obmedzuje priame workflow edits v production a podporuje jednosmerný deployment model. Znižuje accidental drift a obchádzanie review.

Protection nie je kompletná isolation. Admin, API, credentials, variables a external provider configuration stále môžu meniť effective state a potrebujú audit.

## 18. Credential stubs

Source control prenáša credential stubs alebo references, nie plaintext secret values. Target environment musí mať lokálny credential object a explicitný mapping k intended workflow nodeu.

Stub equality nepreukazuje rovnaký provider tenant, scope alebo secret generation. Promotion kontroluje effective credential ID a provider-side principal.

## 19. Variable stubs a values

Variables môžu byť reprezentované v source-control promotion flowe, ale target environment potrebuje správne local values. Rovnaký variable name môže mať odlišnú hodnotu pre development a production.

Variable sa klasifikuje ako configuration input s ownerom, type, sensitivity a allowed environment scope. Missing value nesmie defaultovať na test alebo production endpoint bez explicitnej policy.

## 20. Tags a organizational metadata

Tags pomáhajú klasifikovať workflows, ownership a lifecycle a n8n ich môže prenášať v source-control scope. Tag však nie je enforcement point ani release approval.

Runtime policy sa nespolieha iba na tag `production` alebo `approved`. Machine-enforced controls čítajú exact manifest a permissions.

## 21. Data tables a runtime data

Niektoré n8n source-control flows môžu zahŕňať supported data-table definitions alebo selections, ale business runtime data a external datastore contents majú vlastný migration a backup lifecycle. Definícia schema nie je obsah ani correctness proof.

Promotion musí rozlíšiť configuration data, reference data a mutable business records. Git nie je všeobecný database replication mechanismus.

## 22. Sub-workflow references

Parent workflow reference na child workflow môže byť environment-specific dependency. Pull oboch JSON files nestačí, ak target IDs alebo logical mapping nezodpovedajú.

Deployment manifest a post-pull validator vytvoria dependency graph a overia, že každý caller smeruje na intended child generation. Missing dependency blokuje publish.

## 23. Error workflow references

Workflow settings môžu odkazovať na centrálne error workflow. Target environment potrebuje existujúci a správne oprávnený handler, inak failure reporting nebude fungovať podľa návrhu.

Promotion test úmyselne vyvolá safe failure a overí dispatch, redaction a notification. Visual setting v source JSON nie je runtime evidence.

## 24. Credential mapping

Environment mapping viaže logical credential role, napríklad `ticketing_refund_writer`, na local credential ID a provider tenant. Mapping je explicitne schválený a auditovaný.

Name-based auto-selection je nebezpečný pri kolíziách alebo copied instances. Wrong credential binding môže vytvoriť validný, ale cross-tenant authorized call.

## 25. Node a community package versions

Workflow JSON odkazuje na node types a type versions, no effective implementation závisí od n8n release a installed community/custom nodes. Rovnaký workflow commit môže mať odlišné runtime behavior v dvoch instances.

Promotion manifest eviduje n8n version, node package digests a relevant feature flags. Compatibility test prebehne pred production publishom.

## 26. Environment configuration

Queue mode, concurrency, timeouts, execution retention, timezone, webhook base URL, task runners a encryption key nie sú plne reprezentované jedným workflow commitom. Menia execution behavior a recovery.

Infrastructure a application configuration majú vlastný source of truth. Composed release spája Git workflow commit s deployment/config generations.

## 27. Branch protection a review

Git provider presadzuje required reviews, status checks, signed commits alebo environment approvals podľa organizational policy. n8n source control poskytuje transport a diff, ale PR discipline vzniká mimo editoru.

Reviewer hodnotí workflow graph, credential bindings, variables, side-effect class, contract changes a rollback. JSON line diff bez rendered alebo semantic review môže skryť významnú zmenu.

## 28. Automated validation

CI validuje JSON syntax, forbidden nodes, dangling references, contract versions, environment-specific literals, secret patterns a documentation. Integration tests importujú candidate do isolated instance alebo test harnessu podľa možností.

Validation nepublikuje automaticky high-impact workflow bez gate. Passing static checks nepreukazuje provider authorization ani business outcome.

## 29. Promotion manifest

Manifest viaže Git commit na všetky runtime-relevantné dependencies. Obsahuje target instance, branch, workflows, saved/published versions, child/error references, credentials, variables, n8n release a approval.

Bez composed manifestu sa rollback často vráti iba workflow JSON, ale ponechá new credential, variable alebo node version. To vytvorí hybrid state.

## 30. Publish ordering

Po pull-e sa najprv overia local bindings a dependencies, potom sa publikuje child a backward-compatible shared capabilities a nakoniec callers. Ordering znižuje okno nekompatibility.

Breaking change používa expand-migrate-contract. Bulk publish všetkého bez dependency graphu môže aktivovať parent pred child alebo new mapping pred policy.

## 31. Activation a trigger registration

Webhook, schedule a event triggers môžu vyžadovať activation alebo publication behavior a external registration. Promotion kontroluje production URL, provider subscription a duplicate trigger state.

Old a new endpoints nesmú súčasne spracúvať rovnaký event bez shared idempotency. Trigger green v UI nepreukazuje, že provider posiela traffic na správnu route.

## 32. Drift detection

Drift je rozdiel medzi approved Git/composed release a saved, published alebo effective target state. Môže vzniknúť local editom, missed pullom, unpublished workflowom, changed credentialom alebo runtime upgradeom.

Detector číta target instance a porovná stable digests a mappings. Drift sa klasifikuje a buď reconciliuje, alebo dočasne schváli expiring exception.

## 33. Rollback

Rollback vyberá known-good composed release, nie iba predchádzajúci Git commit. Obnovuje compatible workflow definitions, publications, bindings a dependency versions.

Pred rollbackom sa reconciliujú in-flight a unknown external outcomes. Návrat k starému workflowu nesmie opakovať side effects alebo stratiť items vytvorené novou verziou.

## 34. Backup verzus source control

Git uchováva deklarované workflow artifacts, ale nie je úplný backup n8n instance. Recovery potrebuje database, encryption key, credentials alebo external-secret references, variables, binary data, execution/audit evidence a infrastructure configuration podľa scope.

Restore drill kombinuje repository a backup artifacts. Schopnosť checkoutnúť JSON neznamená schopnosť obnoviť funkčnú a bezpečnú automation platformu.

## 35. Shared incident `AGENT-N8N-08`

Development push obsahoval opravený refund parent, child contract a error route. Pull do production prešiel a Git commit bol označený ako deployed, ale current saved workflow nebol publikovaný a old published parent zostal active.

Credential stub sa lokálne viazal na organization-wide OAuth credential a variable `REFUND_API_BASE` ukazovala na legacy endpoint bez idempotency. Effective runtime tak kombinoval nový child saved state, starý parent published state a širšiu authority.

## 36. Competing failure hypotheses

Prvá hypotéza je missed pull, druhá pull bez publishu, tretia wrong credential mapping, štvrtá stale variable a piata incompatible n8n/node generation. Všetky môžu existovať pri rovnakom Git commit-e.

Evidence porovná repository commit, pull audit, saved/published digests, workflow references, variable values, credential IDs/scopes, instance version a actual execution trace. GitHub merge success nevylučuje runtime drift.

## 37. Evidence preservation

Zachová sa branch a commit, PR approvals, push/pull events, target instance inventory pred a po promotion, saved/published versions, local mappings, node/runtime versions a canary executions. Secret values sa neredigovane nekopírujú.

Current state po oprave sa uloží ako correction snapshot. Incident reconstruction potrebuje point-in-time effective graph, nie iba latest repository.

## 38. Containment

Affected workflow sa deaktivuje alebo route prepne na safe intake bez mutations. Trigger subscriptions a duplicate endpoints sa skontrolujú a unknown executions sa reconciliujú.

Production local edits sa zmrazia. Deployment owner určí authoritative composed release a zabráni ďalším pull/publish pokusom, kým scope nie je známy.

## 39. Recovery

Target instance pullne reviewed commit, explicitne vyrieši credential/variable mappings, overí child a error dependencies a publikuje workflows v správnom poradí. Runtime read-back vytvorí loaded manifest.

Canary používa sandbox alebo low-risk operation a následne representative production operation s idempotency. Drift monitor ostáva zvýšený počas observation window.

## 40. Positive acceptance

Target saved digest zodpovedá Git commit-u, intended published version je active a execution trace používa expected child, credential tenant, variable values a node generation. Provider-side outcome je správny.

PR, pull, publish a canary evidence tvoria jeden causal chain. Operátor vie preukázať, čo je desired, loaded aj effective.

## 41. Forbidden acceptance

Merge alebo pull success sa nesmie označiť ako deployment completion bez publish a runtime verification. Neprípustné sú plaintext secrets v Git, name-only credential mapping a priame production edits bez reconciliation.

Rovnaký workflow JSON na dvoch instances nie je parity proof, ak sa líšia credentials, variables, node versions alebo infrastructure settings.

## 42. Recovery acceptance

Rollback drill vráti known-good composed release a overí, že old/new trigger routes nevytvárajú duplicate events. In-flight operations sa uzatvoria podľa idempotency ledgeru.

Restore drill vytvorí isolated instance z Git a backup dependencies a preukáže decryption, mappings, publication a safe execution. Chýbajúci artifact spôsobí explicitné failed recovery.

## 43. Second-environment acceptance

Staging a production pullnú rovnaký reviewed artifact, ale každá používa vlastné tenant-scoped credentials, variables a endpoints. Test preukáže, že staging nemôže vykonať production mutation.

Promotion do druhého environmentu nespolieha na manual knowledge prvého operátora. Manifest a validation sú reprodukovateľné.

## 44. Praktický promotion manifest

Manifest uzatvára medzeru medzi Git desired state a n8n effective state. Neobsahuje plaintext secrets, ale stable references a digests.

```yaml
n8n_promotion:
  release_id: refund-automation/5.3.0
  git:
    repository: automation-private
    branch: production
    commit: 7c31e4a
  target_instance: n8n-prod-eu-1
  workflows:
    - logical_id: wf_refund_batch
      saved_digest: sha256:aa11...
      published_version: 42
    - logical_id: wf_refund_executor
      saved_digest: sha256:bb22...
      published_version: 18
  dependencies:
    error_workflow: wf_ops_error_handler@v9
    credential_mapping: refund_writer_acme@v17
    variables_digest: sha256:cc33...
    n8n_version: 2.x-pinned
  approval: change-2841
  validation: canary-execution-991
```

## 45. Prevádzkové metriky

Sledujú sa commits čakajúce na pull, pulled-but-unpublished workflows, saved/published drift, local edits, unresolved stubs, mapping changes, promotion failures, rollback time a environment parity. Metrics sa segmentujú podľa target instance a risk tieru.

Nulový drift alert nie je dôkaz, ak detector číta iba saved state. Coverage musí zahŕňať published a effective dependencies.

## 46. Primárne zdroje

- [n8n Docs — Source control and environments](https://docs.n8n.io/source-control-environments/)
- [n8n Docs — Tutorial: Create environments with source control](https://docs.n8n.io/source-control-environments/create-environments/)
- [n8n Docs — Git in n8n](https://docs.n8n.io/source-control-environments/understand/git/)
- [n8n Docs — Branch patterns](https://docs.n8n.io/source-control-environments/understand/branch-patterns/)
- [n8n Docs — Push and pull](https://docs.n8n.io/source-control-environments/using/push-pull/)
- [n8n Docs — Workflow history](https://docs.n8n.io/workflows/history/)
- [n8n Docs — Workflow settings](https://docs.n8n.io/workflows/settings/)
- [n8n Docs — Source-control environment variables](https://docs.n8n.io/hosting/configuration/environment-variables/source-control/)

## 47. Zhrnutie

Source control vytvára authoritative promotion channel pre workflow definitions, ale production safety závisí od rozdielu medzi saved, published a effective state. Git commit bez target bindingov a runtime read-backu je iba deklarácia.

Bezpečný environment model používa jednosmerný flow, externý review, explicitné credential a variable mappings, dependency-aware publish, composed release manifest, drift detection a rollback. Accepted deployment preukazuje nielen správny commit, ale aj loaded workflow graph, provider identity a business outcome v druhom environment-e.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Sub-workflows a reusable workflow contracts](sub-workflows-reusable-workflow-contracts.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
