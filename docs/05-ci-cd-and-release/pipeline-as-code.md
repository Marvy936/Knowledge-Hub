# Pipeline as Code

Pipeline as Code znamená, že delivery workflow, jeho dependencies, permissions, policy hooks a významné runtime contracts sú definované vo versionovanom, reviewovateľnom a automaticky validovanom formáte. Nejde iba o YAML uložený v repository. Pipeline definícia je privilegovaný program, ktorý rozhoduje, aký kód sa vykoná, na akom runneri, s akými credentials, aký artifact vznikne a čo sa môže nasadiť do konkrétneho environmentu.

## 1. Mental model: pipeline ako privilegovaný program

Pipeline má podobný lifecycle ako compiler a runtime:

```text
source fragments
→ includes/templates
→ parsing a schema validation
→ parameter binding
→ rendering/merge
→ policy evaluation
→ execution graph
→ scheduling
→ job execution
→ artifacts, evidence a deployments
```

Každá fáza môže zmeniť výsledné správanie. Source YAML môže vyzerať bezpečne, ale include, default, UI variable alebo policy mutation môže vytvoriť odlišný resolved graph.

## 2. Prečo Pipeline as Code

Bez versionovanej definície vzniká:

- neauditovateľná UI konfigurácia,
- zmena delivery bez code review,
- drift medzi projektmi,
- nejasný ownership,
- nereprodukovateľný starší run,
- pipeline závislá od jedného administrátora,
- slabý rollback workflow logiky,
- skryté permission a secret zmeny.

Pipeline as Code poskytuje:

- históriu a diff,
- review a ownership,
- testovanie,
- versionované dependencies,
- reuse,
- policy as code,
- traceability od definície po runtime run,
- možnosť riadeného rollout-u a rollbacku pipeline zmeny.

## 3. Deklaratívnosť a imperatívna logika

Pipeline definícia typicky deklaruje desired execution graph:

```yaml
stages:
  - verify
  - build
  - deploy

build:
  stage: build
  image: example/builder@sha256:...
  script:
    - ./scripts/build.sh
```

Deklaratívnosť neznamená absenciu skriptov. Znamená, že orchestration, dependencies, permissions, timeouts, artifacts a decision points sú explicitné.

Praktické rozdelenie:

```text
pipeline definition
→ orchestration, trust boundaries a contracts

scripts alebo tools
→ komplexná build/deployment logika
```

Dlhý inline shell je ťažko testovateľný a náchylný na quoting, error-handling a platformové rozdiely.

## 4. Source of truth

Autoritatívna pipeline definícia môže byť:

- v application repository,
- v centrálnom template repository,
- v reusable workflow katalógu,
- v generátore,
- v kombinácii lokálneho entrypointu a pinovaného template-u.

Musí byť jasné:

- ktorý source fragment je autoritatívny,
- aká verzia template-u sa použila,
- ktoré UI nastavenia môžu definíciu dopĺňať,
- aká centrálna policy ju môže obmedziť alebo mutovať,
- kde sa zobrazí resolved configuration.

Viac rovnocenných zdrojov vytvára drift. UI override má byť zakázaný alebo auditovateľný ako samostatná configuration revision.

## 5. Pipeline compiler phases

### Parse

Overuje syntax formátu. Platný YAML znamená iba to, že parser vytvoril dátovú štruktúru.

### Schema validation

Overuje povolené keys, typy, required fields a základné constraints.

### Include resolution

Načíta templates, reusable workflows, anchors alebo child definitions.

### Parameter binding

Dosadí typed inputs, defaults, event metadata a variables.

### Render/merge

Aplikuje inheritance, overrides, matrix expansion a dynamic rules.

### Policy evaluation

Overí alebo obmedzí permissions, runners, images, deployment targets a required jobs.

### Graph construction

Vytvorí DAG jobs a dependencies.

### Runtime execution

Scheduler priradí runners, vydá credentials a vykoná job commands.

Validácia iba prvej fázy neposkytuje dôkaz o výslednom execution graph-e.

## 6. Resolved pipeline configuration

Resolved configuration je finálna definícia po includes, defaults, inheritance, parameters, rules a policy mutations.

Má obsahovať alebo umožniť zistiť:

- všetky jobs a steps,
- dependency graph,
- runner requirements,
- container/image digests,
- effective permissions,
- secret scopes,
- environment targets,
- triggers a conditions,
- artifacts a caches,
- timeouts, retries a failure semantics,
- template a policy versions.

Resolved config je kľúčový audit artifact. Source fragment bez výsledného renderu nemusí vysvetliť, čo sa skutočne vykonalo.

## 7. Resolved-config identity

Pre reprodukciu pipeline runu zachovaj digest resolved configuration.

```text
source workflow revision
+ included template revisions
+ typed inputs
+ non-secret variable identities
+ policy revision
→ resolved config digest
```

Secret values sa do digest manifestu nemajú ukladať v plaintext forme. Zachovaj iba reference/version identity podľa bezpečnostnej policy.

## 8. Pipeline definícia pri aplikačnej zmene

Výhoda pipeline súboru v rovnakom repository:

```text
application change
+ test change
+ pipeline change
→ jeden commit a review
```

Riziko: branch code môže meniť vlastný bezpečnostný kontrolný systém. Autor pull requestu môže skúsiť odstrániť scan, rozšíriť token permissions alebo presmerovať deployment.

Preto repository-level pipeline code nie je jediná security boundary.

## 9. Bootstrap a trust paradox

Pipeline validuje kód, ale jej definícia je sama kód. Treba rozhodnúť:

- ktorá workflow revision validuje pull request,
- či source branch môže meniť permissions,
- či môže vybrať privileged runner,
- či môže dostať secrets,
- či môže meniť protected environment,
- či môže načítať vlastný external template,
- kto validuje zmenu validátora.

Bezpečný model kombinuje:

- branch pipeline s minimálnymi permissions,
- server-side protected environment rules,
- centrally enforced policy,
- trusted production deployment entrypoint,
- pinované reusable components,
- required review pre citlivé paths.

## 10. Trusted deployment entrypoint

Nedôveryhodný pull request nemá definovať alebo priamo vykonať production deployment.

Model:

```text
untrusted branch pipeline
→ build/test bez production credentials
→ immutable artifact candidate

trusted default-branch/release workflow
→ overí digest, provenance a gates
→ získa environment-scoped identity
→ vykoná deployment
```

Production deploy workflow môže byť spustený až po merge alebo cez protected reusable workflow, ktorého privileged časti branch nevie meniť.

## 11. Workflow revision semantics

Platforma môže pri pull requeste použiť:

- workflow zo source branchu,
- workflow z target branchu,
- kombináciu trusted wrapperu a branch scripts,
- synthetic merge-result revision.

Každý model má trade-off:

- source workflow testuje budúcu pipeline zmenu, ale je nedôveryhodný;
- target workflow je bezpečnejší, ale nemusí validovať nový pipeline syntax/behavior;
- wrapper model oddeľuje trusted orchestration od testovaného kódu.

Správanie musí byť dokumentované a evidence má zaznamenať použitú workflow revision.

## 12. Syntax a schema validation

Pred runtime over:

- syntax,
- schema,
- required fields,
- type constraints,
- references,
- duplicate alebo shadowed definitions,
- cycles v DAG,
- neexistujúce dependencies,
- neplatné conditions,
- forbidden capabilities.

Platný YAML nie je platná pipeline a platná pipeline nie je bezpečná pipeline.

## 13. Static analysis pipeline kódu

Linter alebo policy analyzer môže odhaliť:

- mutable images alebo actions,
- unpinned includes,
- secrets v source,
- shell injection,
- široké token permissions,
- privileged runner/executor,
- chýbajúce timeouty,
- deployment bez protected environmentu,
- artifact bez retention,
- cache sharing cez trust boundary,
- `curl | shell`,
- nevalidovaný manual input,
- missing cleanup.

Finding musí byť viazaný na resolved config tam, kde source-level analýza nestačí.

## 14. Variables a typed inputs

Rozlišuj:

- repository non-secret config,
- group/organization config,
- environment config,
- protected variables,
- manual/API inputs,
- event metadata,
- derived values,
- secrets.

Pre každú hodnotu definuj:

- typ,
- required/optional,
- default,
- allowlist/range,
- sensitivity,
- scope,
- precedence,
- source identity,
- validation,
- redaction.

Free-form string používaný ako shell command, path alebo environment name je nebezpečný interface.

## 15. Variable precedence

Platformy často skladajú values z viacerých vrstiev:

```text
organization default
→ project variable
→ environment override
→ workflow input
→ job value
→ runtime derived value
```

Precedence musí byť explicitná. Skrytý UI override môže zmeniť správanie bez repository diffu.

Resolved configuration alebo run metadata má ukázať zdroj každej non-secret effective value.

## 16. Secrets

Pipeline source nemá obsahovať secret values. Preferuj:

- workload identity/OIDC,
- secret-manager references,
- environment-scoped short-lived credentials,
- per-job secret injection,
- protected variables iba pri trusted refs.

Masking logu nie je bezpečnostná boundary. Secret môže uniknúť cez:

- artifact alebo cache,
- process arguments,
- environment dump,
- crash report,
- encoding/transformáciu,
- network exfiltration,
- persistent runner filesystem.

## 17. Permission model

Permissions deklaruj explicitne per job.

```text
verify
→ read source, no secrets

publish
→ read verified workspace, write artifact registry

deploy
→ read immutable artifact, environment-scoped deploy role
```

Review pipeline zmeny musí zahrnúť permission diff:

- repository token scopes,
- registry access,
- cloud IAM,
- network reachability,
- runner pool,
- environment secrets,
- signing keys,
- approval bypass capability.

Default write-all token je slabý model.

## 18. Runner a executor trust

Pipeline as Code určuje, kde sa job vykoná. Runner selection je security decision.

Kontroluj:

- hosted/self-hosted,
- ephemeral/persistent,
- shell/container/VM/Kubernetes executor,
- network access,
- host mounts a Docker socket,
- privileged mode,
- architecture a image,
- cleanup a attestation,
- permitted repositories/triggers.

Label `trusted` nie je dostatočný control. Potrebné sú oddelené pools, authorization a environment policy.

## 19. Externé dependencies pipeline

Pipeline dependencies zahŕňajú:

- container images,
- actions/plugins,
- reusable workflows,
- templates,
- package managers,
- downloaded scripts,
- runner images,
- remote APIs.

Každá dependency môže bežať s permissions jobu a má supply-chain dopad.

## 20. Immutable pinning

Preferované identities:

- container digest,
- commit SHA,
- signed artifact digest,
- immutable internal template version,
- checksum-verifikovaný binary.

Mutable references ako `latest`, branch alebo floating major version môžu zmeniť pipeline behavior bez repository diffu.

Human-readable version možno zachovať ako komentár alebo metadata, ale runtime resolve má byť immutable.

## 21. External actions a plugins

Pred použitím posúď:

- ownera a source,
- pinned revision,
- permissions,
- code size a dependencies,
- network access,
- release/signing process,
- vulnerability history,
- update policy,
- možnosť interného mirroru,
- attestation alebo checksum.

Jednoriadkové použitie action môže vykonať veľký privilegovaný program.

## 22. Download-and-execute

Nebezpečný pattern:

```bash
curl https://example/script.sh | bash
```

Bezpečnejší lifecycle:

1. stiahnuť pinovanú verziu;
2. overiť checksum/signature;
3. uložiť alebo mirrorovať artifact;
4. spustiť s minimálnymi permissions;
5. zachovať version/provenance v run evidence.

Aj HTTPS chráni transport, nie nemennosť alebo dôveryhodnosť budúceho obsahu URL.

## 23. Includes a reusable templates

Template môže poskytovať:

- štandardný build,
- security gates,
- artifact publication,
- deployment workflow,
- observability metadata,
- compliance controls.

Template potrebuje:

- versionovaný contract,
- typed inputs a outputs,
- changelog,
- compatibility policy,
- deprecation lifecycle,
- test suite,
- ownera a support model,
- rollback version.

## 24. Include resolution

Include resolver musí definovať:

- allowed sources/domains/repositories,
- authentication,
- immutable revision,
- recursion limit,
- cycle detection,
- merge order,
- failure pri nedostupnosti,
- cache/freshness semantics.

Remote include bez pinning-u je vzdialený privileged code execution path.

## 25. Merge a override semantics

Pri inheritance/templates treba vedieť:

- či arrays nahrádzajú alebo spájajú values,
- ako sa správajú maps,
- či `null` odstraňuje inherited field,
- ktoré permissions možno iba zužovať,
- ako sa dedičia conditions,
- či child môže odstrániť required job,
- aký je precedence order.

Príliš hlboká inheritance skrýva effective behavior. Preferuj malý počet vrstiev a rendered preview.

## 26. Template contract a version negotiation

Consumer template-u má deklarovať kompatibilnú version range alebo presnú verziu.

Príklad:

```text
template v2 contract:
inputs: language, artifact_name, test_command
outputs: artifact_digest, evidence_manifest
```

Breaking zmeny:

- zmena input type/default,
- zmena permission requirement,
- odstránenie job outputu,
- zmena artifact naming,
- nový povinný environment,
- zmena failure semantics.

Template release potrebuje semantic contract aj migration guide.

## 27. Centrálne template-y a globálny blast radius

Centralizácia znižuje copy-paste drift, ale zvyšuje blast radius template chyby.

Bezpečný rollout:

- immutable template versions,
- canary repositories,
- representative compatibility matrix,
- opt-in upgrade,
- staged organization rollout,
- telemetry,
- rollback na predchádzajúcu verziu,
- emergency pin/freeze.

Mutable central template prepnutý naraz pre všetky projekty je organizačný single point of failure.

## 28. Scripts verzus inline commands

Komplexnú logiku presuň do testovateľného nástroja, keď obsahuje:

- argument parsing,
- retries a timeouty,
- state reconciliation,
- API interaction,
- plan/apply/verify,
- destructive operations,
- rollback,
- viac platforiem.

Pipeline YAML má orchestráciu zviditeľniť, nie ukrývať stovky riadkov business logiky.

## 29. Dynamic pipeline generation

Generator môže vytvoriť jobs podľa dependency graphu, changed components alebo manifestu.

Výhody:

- selective CI,
- matrix expansion,
- monorepo škálovanie,
- dynamické child pipelines.

Riziká:

- generator je compiler a trust boundary,
- filenames/event metadata môžu vytvoriť injection,
- generated config sa ťažšie reviewuje,
- graph môže byť neúplný,
- policy sa môže aplikovať iba na source, nie generated output,
- traceability je nejasná.

## 30. Generated graph completeness

Generator musí preukázať:

- ktoré komponenty analyzoval,
- aký base/merge SHA použil,
- aký dependency graph version použil,
- ktoré jobs vygeneroval,
- ktoré components preskočil a prečo,
- že required global gates zostali prítomné,
- že graph je acyklický a všetky artifacts majú producers.

Generated config ulož ako evidence artifact s digestom.

## 31. Dynamic input bezpečnosť

Názvy súborov, branch names, manifest fields a API payloady sú nedôveryhodné inputs.

Generator má:

- používať structured serialization,
- validovať identifiers,
- neprodukovať raw shell z input stringov,
- canonicalizovať paths,
- limitovať veľkosť/matrix cardinality,
- odmietnuť neznámy component type,
- oddeliť generation od privileged execution.

## 32. Policy as Code

Organizačná policy môže vynucovať:

- allowed runner pools,
- minimálne token permissions,
- pinované images/actions,
- required security jobs,
- protected deployment entrypoints,
- artifact signing/provenance,
- secret restrictions,
- timeout/cleanup requirements,
- zákaz privileged executorov.

Policy musí byť:

- versionovaná,
- testovaná allow/deny fixtures,
- aplikovaná na resolved graph,
- auditovateľná,
- chránená mimo repository, ktoré kontroluje,
- vybavená exception lifecycle.

## 33. Policy mimo repository

Ak pull request môže meniť policy aj pipeline, môže si odstrániť vlastné obmedzenia. Kritické controls majú byť enforced platformou, organization policy alebo chráneným repository s oddeleným ownershipom.

Repository môže obsahovať deklaráciu intentu, ale enforcement root musí byť mimo trust domainu nedôveryhodnej zmeny.

## 34. Code ownership

Citlivé paths potrebujú špecializovaný review:

```text
/.ci/**                 @platform-team
/deploy/**              @platform-team @service-owner
/security-policy/**     @security-team
/migrations/**          @database-owner
```

Ownership má byť risk-based. Platform tím nemusí schvaľovať každú aplikačnú zmenu, ale má kontrolovať zmeny triggerov, permissions, runners, templates, artifacts a deployments.

## 35. Pipeline testing

### Static tests

- syntax/schema,
- resolved-config validation,
- policy lint,
- forbidden patterns,
- DAG a required jobs.

### Unit tests nástrojov

- argument parsing,
- rendering,
- plan generation,
- edge cases,
- error semantics,
- cleanup.

### Contract tests templates

- inputs/outputs,
- permissions,
- artifact naming,
- compatibility fixtures,
- deprecated behavior.

### Component tests

- disposable runner,
- fake registry/cloud API,
- artifact flow,
- timeout/retry/cancel.

### Integration tests

- sandbox CI project,
- reálna platforma,
- protected test environment,
- identity federation,
- approval a deployment record.

### Failure tests

- registry outage,
- missing include,
- invalid secret reference,
- runner termination,
- partial deployment,
- cleanup failure.

## 36. Pipeline definition self-validation

Pri pipeline zmene treba zabrániť paradoxu, že neplatný nový workflow nedokáže spustiť vlastnú validáciu.

Možnosti:

- platform-native config validation pred runom,
- trusted parent workflow, ktorý validuje branch config,
- local CLI validator,
- separate required check z target-branch workflowu,
- sandbox child pipeline.

## 37. Pipeline change rollout

Pipeline zmena môže ovplyvniť delivery všetkých služieb. Použi:

```text
unit/static validation
→ sandbox project
→ canary repositories
→ opt-in adopters
→ staged rollout
→ default version
→ deprecation starej verzie
```

Sleduj:

- run success/failure classes,
- duration a queue impact,
- permission changes,
- artifact reproducibility,
- support incidents,
- rollback frequency.

## 38. Pipeline rollback

Rollback pipeline logiky môže byť komplikovaný, ak nová verzia zmenila artifact format, variable contract alebo environment state.

Pred rolloutom definuj:

- predchádzajúcu template/workflow revision,
- compatibility artifacts a inputs,
- migration path pre consumers,
- emergency pin,
- behavior rozbehnutých runs,
- rollback policy pre centrally enforced rules.

Rollback workflow definície nevráti automaticky deployments, ktoré už vykonala.

## 39. Reprodukovateľnosť

Na reprodukciu runu potrebuješ:

- application/source SHA,
- workflow source revision,
- resolved config digest,
- template/include revisions,
- policy version,
- runner image a executor identity,
- container/action digests,
- typed inputs,
- non-secret variable provenance,
- secret references/version identities,
- artifact/cache state,
- external service versions.

Pipeline as Code je predpoklad, nie záruka reprodukovateľnosti.

## 40. Artifact a evidence lifecycle

Pipeline definícia má explicitne určiť:

- čo je autoritatívny artifact,
- ako vzniká digest,
- kto ho môže publikovať,
- ktoré reports patria digestu,
- retention,
- signing/provenance,
- promotion eligibility,
- behavior pri partial upload alebo missing evidence.

Artifact path bez identity a retention je slabý contract.

## 41. Cache lifecycle

Pipeline code má definovať:

- cache purpose,
- key inputs,
- trust namespace,
- read/write permissions,
- fallback semantics,
- invalidáciu,
- write timing,
- cold-run behavior.

Branch pipeline nesmie kontaminovať privileged cache iba preto, že používa rovnaký key string.

## 42. Timeouts, retries a cancellation

Každý významný job potrebuje:

- command/job timeout,
- retry iba pre transient failure classes,
- cancellation semantics,
- always-run diagnostics/cleanup,
- idempotentné mutations,
- supersession policy.

Implicitný nekonečný wait alebo blanket retry môže zablokovať runners alebo maskovať reálny failure.

## 43. Observability a audit

Uchovaj:

- pipeline source revision,
- resolved config digest a artifact,
- template/action/image digests,
- policy decisions,
- effective permissions,
- runner/executor identity,
- non-secret input provenance,
- evidence/artifact digests,
- deployment records,
- approvals/waivers,
- cancellation/retry history.

Pipeline platforma potrebuje metrics pre queue, duration, failures, template versions a policy violations.

## 44. Review checklist pipeline zmeny

Pri review sa pýtaj:

- mení sa trigger alebo event trust?
- mení sa workflow revision source?
- pribúda secret alebo permission?
- mení sa runner pool/executor/network?
- pribúda external action/template?
- je dependency pinovaná?
- mení sa artifact identity alebo retention?
- mení sa cache trust namespace?
- odstraňuje sa required gate?
- mení sa environment/approval/release path?
- existujú timeouty, cleanup a recovery?
- je zmena testovaná a rollbackovateľná?
- je resolved graph zrozumiteľný?

## 45. Diagnostický postup

### Pipeline sa zmenila bez repository diffu

Over floating templates, mutable images/actions, runner image, UI variables, organization policy a external service.

### Include zmenil job nečakane

Pozri resolved config, include revision, merge/override semantics a template changelog.

### Branch pipeline získala production secret

Ide o trust-boundary failure. Over workflow revision, protected variables, environment rules, runner pool a token issuance claims.

### Config je validná, ale job chýba

Skontroluj conditions, event context, matrix generation, include overrides a rendered graph.

### Required gate bol preskočený

Over applicability, dynamic generator, policy application na resolved graph a `allow_failure`/skip semantics.

### Pipeline zlyháva iba v jednom projekte po template upgrade

Porovnaj input contract, repository structure, runner capability, language/toolchain a deprecated template behavior.

### Rollback template-u nepomohol

Nová pipeline mohla zmeniť artifacts, variables, environment alebo policy state. Skontroluj runtime effects, nie iba source revision.

## 46. Typické anti-patterny

### YAML ako neobmedzený programovací jazyk

Komplexná templating logika je nečitateľná a netestovateľná.

### Copy-paste pipeline per repository

Security fixes, artifact semantics a permissions driftujú.

### Jeden mutable central template

Jedna zmena môže okamžite rozbiť celú organizáciu.

### Pipeline s permanentnými admin credentials

Repository write access sa môže zmeniť na cloud admin prístup.

### Branch definuje vlastný privileged deploy

Nedôveryhodná zmena ovláda boundary, ktorá ju má kontrolovať.

### External action pinovaná iba major tagom

Behavior sa môže zmeniť bez repository diffu.

### UI variables ako skrytý source of truth

Run sa nedá reprodukovať z versionovaných súborov.

### Policy sa aplikuje iba na source YAML

Generated alebo included resolved graph môže policy obísť.

### Generated config sa neuchováva

Nie je možné dokázať, ktoré jobs a permissions sa vykonali.

### Pipeline rollback sa považuje za deployment rollback

Vrátenie workflow súboru neodstráni už vykonané side effects.

## 47. Praktický checklist

Pred označením Pipeline as Code modelu za dôveryhodný over:

- autoritatívny source je explicitný,
- workflow revision semantics sú zdokumentované,
- branch pipeline nemá privileged deployment boundary,
- resolved config sa generuje a uchováva,
- resolved config má digest,
- syntax, schema, DAG a policy sa validujú,
- typed inputs a precedence sú explicitné,
- secrets sú short-lived a environment-scoped,
- permissions sú minimálne per job,
- runners/executors sú trust-segmentované,
- external dependencies sú immutable pinované,
- includes majú allowlist a version contract,
- template changes majú canary rollout a rollback,
- dynamic generator je testovaný a output auditovaný,
- central policy sa aplikuje mimo nedôveryhodného repository,
- pipeline scripts majú unit/component tests,
- artifact/cache lifecycle je explicitný,
- timeouts, retries, cancellation a cleanup sú definované,
- audit trail spája source, resolved graph, runner, evidence a deployment.

## 48. Kontrolné otázky

1. Prečo Pipeline as Code nie je iba YAML v repository?
2. Aké fázy má pipeline compiler/runtime lifecycle?
3. Čo je resolved pipeline configuration?
4. Prečo má resolved config vlastný digest?
5. Čo je bootstrap/trust paradox?
6. Aké workflow revision modely môže platforma používať pri pull requeste?
7. Prečo branch pipeline nemá priamo ovládať production deployment?
8. Ako variable precedence ovplyvňuje reprodukovateľnosť?
9. Prečo masking nie je dostatočná ochrana secretu?
10. Čo musí zahŕňať pipeline permission diff?
11. Prečo runner selection patrí do security review?
12. Ako sa bezpečne pinujú external actions a images?
13. Prečo `curl | bash` nie je dôveryhodný dependency lifecycle?
14. Čo tvorí versionovaný template contract?
15. Ako include merge semantics môžu zmeniť permissions alebo jobs?
16. Ako sa bezpečne rolloutuje central template?
17. Prečo je dynamic generator compiler a trust boundary?
18. Čo musí dokazovať generated graph completeness?
19. Prečo sa critical policy aplikuje mimo repository?
20. Aké vrstvy testovania Pipeline as Code poznáš?
21. Ako sa self-validuje zmena, ktorá môže rozbiť vlastný workflow?
22. Prečo pipeline rollback nemusí odstrániť runtime side effects?
23. Aké metadata sú potrebné na reprodukciu starého runu?
24. Prečo je resolved configuration dôležitejšia než jednotlivé source fragments pri audite?

## Summary

Pipeline as Code spravuje delivery workflow ako privilegovaný software systém. Dôveryhodný model pozná parse, include, render, policy a graph phases, uchováva resolved configuration s digestom a oddeľuje nedôveryhodnú branch validáciu od privileged deployment entrypointu. External actions, templates, images a runners sú supply-chain a trust dependencies, preto potrebujú immutable pinning, permissions a rollout lifecycle. Central policy sa musí aplikovať na resolved graph mimo repository, ktoré kontroluje. Pipeline zmeny sa testujú, canary rolloutujú, auditujú a rollbackujú s vedomím, že už vykonané runtime side effects zostávajú samostatným problémom.

## Glossary impact

Relevantné pojmy: Pipeline as Code, pipeline compiler, resolved pipeline configuration, resolved config digest, workflow revision, bootstrap trust paradox, trusted deployment entrypoint, typed pipeline input, variable precedence, pipeline permission boundary, external action, immutable pinning, reusable template, template contract, include resolution, override semantics, dynamic pipeline generator, generated graph completeness, policy as code, pipeline canary rollout a pipeline rollback.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Quality gates a approvals](quality-gates-and-approvals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Reusable a parallel pipelines →](reusable-and-parallel-pipelines.md)
<!-- KNOWLEDGE-NAVIGATION:END -->