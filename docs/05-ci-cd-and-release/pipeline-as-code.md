# Pipeline as Code

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Pipeline as Code spravuje delivery workflow ako privilegovaný software systém. Source YAML alebo DSL je iba vstup. Skutočné runtime správanie vznikne až po includes, template resolution, parameter binding, inheritance, policy evaluation a graph construction. Dôveryhodný model preto hodnotí resolved pipeline graph, jeho permissions, runner boundaries, artifacts a deployment paths — nie iba jednotlivé source fragmenty.

```text
versionované source fragments
→ include/template resolution
→ typed input a variable binding
→ render/merge/inheritance
→ resolved configuration digest
→ policy na effective graph-e
→ trusted a untrusted execution boundaries
→ jobs, artifacts, gates a deployments
→ runtime evidence
→ pipeline-change rollout a rollback
```

## 1. Cieľ kapitoly

Nosný model kapitoly je pipeline-compiler-and-trust lifecycle:

```text
pipeline change
→ source a dependency identity
→ parse/schema/include resolution
→ resolved graph a effective permissions
→ policy enforcement mimo nedôveryhodnej zmeny
→ self-validation a sandbox execution
→ canary rollout pipeline verzie
→ production execution evidence
→ rollback/migration a learning
```

Cieľom nie je písať kratší YAML. Cieľom je vedieť, čo platforma skutočne vykoná, aké authority workflow získava a ako sa bezpečne mení systém, ktorý kontroluje build, signing a deployment ostatného kódu.

## 2. Nosný scenár: Atlas delivery template 4.2

Atlas platform tím pripravuje reusable template 4.2 pre Orders 3.10.1. Zmena:

- pridáva release-manifest fan-in;
- mení build image;
- zavádza OIDC production deployment;
- generuje jobs podľa affected components;
- vynucuje required security a migration gates;
- mení cache namespace a artifact outputs.

Application repository obsahuje entrypoint:

```text
atlas-orders/.ci/pipeline.yml
→ include platform template @ immutable revision T
→ bind service manifest a inputs
→ organization policy revision P
→ resolved pipeline graph G
```

Review musí overiť G, nie iba lokálny entrypoint alebo template source samostatne.

## 3. Pipeline source verzus runtime graph

Pipeline source môže pochádzať z:

- application repository;
- central template repository;
- reusable workflow registry;
- dynamic generatora;
- organization policy a platform defaults;
- UI/project/environment variables.

Runtime graph vzniká kombináciou všetkých vrstiev. Dve pipeline s rovnakým application commitom môžu mať odlišné správanie, ak sa zmení floating template, runner image, policy alebo hidden variable.

## 4. Compiler phases

```text
parse
→ syntax dátového formátu

schema validation
→ povolené fields, types a references

include resolution
→ pinované templates/actions/workflows

parameter binding
→ typed inputs, defaults, event metadata

render/merge
→ inheritance, overrides, matrix a generated config

policy evaluation
→ permissions, runners, required jobs a environments

graph construction
→ DAG, outputs, conditions a failure propagation

runtime
→ scheduling, credentials, job execution a side effects
```

Platný YAML dokazuje iba parse. Neplatný alebo nebezpečný resolved graph môže vzniknúť až v neskoršej fáze.

## 5. Resolved configuration ako audit artifact

Resolved configuration obsahuje:

- všetky jobs a dependency edges;
- effective conditions a triggers;
- runner/executor requirements;
- container/action/template digests;
- effective token a secret permissions;
- environment targets;
- artifacts, reports a caches;
- timeouts, retries, cancellation a cleanup;
- template/policy revisions.

Atlas vytvorí digest:

```text
workflow source revisions
+ include/template revisions
+ typed non-secret inputs
+ variable source identities
+ policy revision
→ resolved config digest G
```

Secret values sa neukladajú do manifestu; zachovávajú sa reference/version identities.

## 6. Bootstrap trust paradox

Pipeline kontroluje kód, ale branch môže meniť pipeline. Treba určiť, ktorá authority validuje zmenu validátora.

Atlas oddeľuje:

```text
untrusted branch path
→ branch code a pipeline návrh
→ read-only verification bez production secrets
→ resolved-config/static/sandbox evidence

trusted delivery path
→ protected main/release workflow
→ overí artifact, policy a resolved graph
→ short-lived environment identity
→ signing a deployment
```

Branch pipeline nesmie sama rozhodnúť, že je trusted, vybrať privileged runner alebo odstrániť required organization policy.

## 7. Workflow revision semantics

Pri pull requeste môže platforma použiť:

- source-branch workflow;
- target-branch workflow;
- synthetic merge workflow;
- trusted wrapper, ktorý vykoná branch scripts ako data/code input.

Atlas používa trusted wrapper pre security-critical orchestration. Source branch môže testovať novú pipeline definíciu v sandboxe, ale production authority ostáva mimo jej trust domainu.

Run evidence zaznamenáva source aj effective workflow revision.

## 8. Typed inputs a variable provenance

Každý input má:

- typ a required/default semantics;
- allowlist alebo range;
- sensitivity a redaction;
- precedence a source identity;
- environment/ref scope;
- validation pred použitím.

```text
organization default
→ project config
→ environment overlay
→ workflow typed input
→ job-local derived value
```

Hidden UI override bez provenance môže zmeniť runner, artifact name alebo deployment target bez repository diffu. Atlas resolved metadata ukazuje source každej non-secret effective value.

## 9. Permission graph

Pipeline review zahŕňa authority flow:

```text
verify job
→ read source, no secrets

build job
→ read pinned dependencies, publish candidate artifact

sign/fan-in job
→ read verified artifacts/evidence, signing authority

deploy job
→ read eligible manifest, environment-scoped role
```

Jedna job, ktorá vykoná untrusted build, podpis a production deploy, spája nezlučiteľné trust boundaries.

Permission diff zahŕňa repository token, registry, signing, cloud IAM, network, runner pool, environment secrets a approval bypass.

## 10. Runner selection je policy decision

Pipeline as Code určuje executor a runner pool. Atlas policy hodnotí:

- hosted/self-hosted a ephemeral/persistent model;
- shell/container/VM/Kubernetes isolation;
- privileged mode, host mounts a Docker socket;
- network reachability;
- permitted repositories a trigger classes;
- architecture a build image;
- cleanup a attestation.

Label `trusted` nie je security boundary. Authorization, separated pools a environment policy musia vynútiť, kto môže pool použiť.

## 11. External dependencies a immutable pinning

Pipeline dependency môže bežať s plnými permissions jobu:

- action/plugin;
- reusable workflow;
- central template;
- container/runner image;
- downloaded binary alebo script;
- remote API/tool.

Runtime references sú pinované immutable identity: commit SHA, artifact digest, checksum alebo signed internal version. Floating branch, `latest` alebo mutable major tag môžu zmeniť delivery behavior bez repository diffu.

`curl URL | shell` nemá stable content identity ani independent verification. Bezpečný flow stiahne pinovanú verziu, overí checksum/signature, uloží provenance a spustí ju s minimálnymi permissions.

## 12. Template contract

Reusable template 4.2 deklaruje:

```text
inputs:
- component_manifest
- build_profile
- deployment_strategy

outputs:
- release_manifest_digest
- evidence_manifest_digest

permissions:
- verification scope
- artifact publication scope

failure semantics:
- required, advisory, incomplete
```

Breaking change je aj zmena defaultu, permission requirementu, artifact namingu, outputu alebo failure semantics. Template potrebuje versioning, compatibility fixtures, migration guide, deprecation a rollback version.

## 13. Include a override semantics

Resolver musí určiť:

- allowed sources a immutable revisions;
- authentication a failure behavior;
- recursion/cycle limits;
- merge order;
- map/array/null semantics;
- fields, ktoré child môže iba zužovať;
- či required jobs možno odstrániť.

Hlboká inheritance skrýva effective behavior. Resolved preview a policy nad výsledkom sú povinné.

## 14. Dynamic generation

Atlas generator číta component manifest a dependency graph a vytvára affected jobs:

```text
candidate/base SHA
+ graph revision
+ changed components
→ generated pipeline Gc
```

Generated graph evidence obsahuje:

- analyzovaný component set;
- zvolený base/candidate;
- graph version;
- generated a skipped jobs s dôvodmi;
- required global gates;
- producers/consumers artifact edges;
- acyclicity a matrix limits;
- digest generated configu.

Generator je compiler a trust boundary. User-controlled názvy a paths sa validujú ako structured data, nie raw YAML alebo shell.

## 15. Policy na resolved graph-e

Organization policy vynucuje:

- povolené runner pools a images;
- minimálne permissions;
- required security/provenance jobs;
- protected deployment entrypoints;
- cache trust boundaries;
- timeout/cleanup requirements;
- zákaz privileged/unpinned dependencies.

Policy sa aplikuje na resolved graph G/Gc mimo repository, ktoré kontroluje. Source-level scan môže prehliadnuť job odstránený override-om alebo permission pridanú template-om.

## 16. Pipeline testing

Atlas používa vrstvy:

```text
source syntax/schema
→ include a resolved-config tests
→ policy allow/deny fixtures
→ template contract tests
→ generator unit/completeness tests
→ sandbox CI project
→ canary repositories
→ staged organization rollout
```

Failure tests pokrývajú missing include, registry outage, invalid secret reference, runner termination, partial artifact upload, cancellation a cleanup.

## 17. Self-validation

Neplatná nová pipeline nemusí vedieť spustiť vlastnú validáciu. Atlas používa target-branch trusted validator:

```text
PR obsahuje pipeline change
→ trusted existing workflow načíta branch config ako data
→ parse/render/policy/sandbox tests
→ required status nezávislý od novej config schopnosti spustiť sa
```

Tak sa zabráni tomu, aby rozbitý alebo zámerne vypnutý workflow odstránil vlastný required check.

## 18. Pipeline change rollout

Central template 4.2 sa rolloutuje ako produkt:

```text
static/unit/contract evidence
→ sandbox repository
→ canary services
→ representative compatibility matrix
→ opt-in cohort
→ staged default rollout
→ deprecation 4.1
```

Sleduje failure classes, duration/queue, permissions, artifact reproducibility, support incidents a rollback frequency.

Mutable central template prepnutý naraz pre všetky repositories je organization-wide single point of failure.

## 19. Worked failure: floating template zmenil production permissions

Atlas repositories používali include `platform-template@v4`, kde `v4` bol mutable branch. Platform tím pridal debug upload a širší cloud permission:

```text
application repository bez diffu
→ ďalší run resolve-ol nový v4 content
→ deploy job získal širšiu role
→ debug artifact obsahoval rendered secret reference metadata
→ delivery behavior sa zmenil bez lokálneho review
```

### Root cause

Runtime dependency nebola immutable pinovaná a resolved-config/permission diff sa neuchovával ako required evidence.

### Náprava

- repositories pinujú immutable template revision;
- update bot vytvára reviewovateľný version bump;
- resolved config digest a permission diff sú artifacts;
- template rollout používa canary repositories;
- environment policy limituje maximálne permissions nezávisle od template-u;
- debug outputs majú schema a redaction controls.

## 20. Worked failure: generated graph odstránil required migration gate

Generator vyhodnotil zmenu v `db/schema/` ako dokumentáciu, pretože dependency graph neobsahoval rename edge:

```text
PR zmenil migration file rename + content
→ generator nevytvoril migration-validation job
→ source-level policy videla required rule v template
→ resolved graph job neobsahoval
→ release manifest bol publikovaný bez migration evidence
```

### Root cause

Policy sa aplikovala na source template, nie na generated resolved graph. Generator nemal completeness manifest ani conservative fallback pre unknown rename.

### Náprava

- generated graph sa uloží a digestuje;
- organization policy kontroluje required jobs na resolved graph-e;
- generator deklaruje analyzed/skipped components;
- rename/root/unknown zmeny spúšťajú širší fallback;
- fan-in očakáva migration evidence podľa release manifestu;
- incident pridá graph contract regression fixture.

## 21. Pipeline rollback a runtime effects

Rollback template-u alebo YAML neodstráni artifacts, deployments, migrations ani credentials, ktoré predchádzajúca verzia už vytvorila.

Pipeline rollback plan obsahuje:

- predchádzajúcu workflow/template revision;
- input/output a artifact compatibility;
- behavior rozbehnutých runs;
- emergency pin/freeze;
- cleanup/reconciliation už vykonaných side effects;
- migration guide pre consumers.

## 22. Reprodukovateľnosť a audit

Pre každý run Atlas uchová:

```text
application candidate SHA
workflow/source revisions
resolved config digest
include/action/image digests
policy revision a verdicts
effective permissions
runner/executor identity
input a variable provenance
artifact/evidence digests
deployment a approval records
attempt/cancel/cleanup history
```

Pipeline as Code je predpoklad reprodukovateľnosti. Floating dependencies, hidden UI state a mutable runners ju môžu stále zničiť.

## 23. Diagnostický postup

1. Potvrď application, workflow a target revisions.
2. Načítaj resolved config artifact a digest.
3. Porovnaj include/template/action/image immutable identities.
4. Skontroluj typed inputs, precedence a hidden overrides.
5. Porovnaj effective permissions, secret scopes, runner a network.
6. Over DAG, conditions, generated jobs a required gate completeness.
7. Zisti, či organization policy bežala na resolved graph-e.
8. Porovnaj aktuálnu pipeline version s canary/rollout cohortou.
9. Pri rollbacku analyzuj už vykonané runtime side effects.
10. Oprav source, template contract, generator alebo external policy a pridaj regression fixture.

## 24. Referenčné pravidlá

- Pipeline source nie je runtime pipeline.
- Resolved graph a effective permissions sú autoritatívny review subject.
- Resolved config má immutable digest a retention.
- Branch nemôže meniť enforcement root, ktorý ju kontroluje.
- Trusted deployment entrypoint je oddelený od untrusted validation.
- Inputs sú typed a variable provenance je viditeľná.
- Permissions sa deklarujú minimálne per job.
- Runner selection je security decision.
- External dependencies sa pinujú immutable identity.
- Template má explicitný compatibility a failure contract.
- Dynamic generator dokazuje graph completeness.
- Central policy sa aplikuje na resolved graph mimo repository.
- Pipeline zmeny sa self-validujú a canary rolloutujú.
- Pipeline rollback neruší automaticky runtime side effects.

## 25. Časté omyly

### „Pipeline as Code znamená YAML v Gite“

Bez resolved graphu, dependency pinning-u a runtime evidence zostáva veľká časť behavioru skrytá.

### „Source review ukazuje všetky permissions“

Template, inheritance, UI variable alebo policy mutation môžu zmeniť effective authority.

### „Branch musí mať production secrets, aby otestovala deploy“

Deployment contract možno overiť v sandboxe; privileged entrypoint patrí trusted boundary.

### „Central template znižuje všetko riziko“

Znižuje drift, ale zvyšuje globálny blast radius chyby.

### „Generated pipeline je iba optimalizácia“

Je to compiler, ktorý rozhoduje, ktoré controls existujú.

### „Rollback YAML-u vráti systém“

Už vykonané mutations zostávajú a potrebujú samostatnú recovery.

## 26. Zhrnutie

Dôveryhodný Atlas Pipeline as Code model je:

```text
versioned pipeline source a immutable dependencies
→ parse/include/bind/render
→ resolved graph digest
→ external policy nad effective permissions a jobs
→ trusted/untrusted execution separation
→ self-validation a sandbox
→ canary rollout pipeline zmeny
→ runtime evidence
→ version rollback + side-effect reconciliation
```

Pipeline as Code spravuje privilegovaný program. Bez kontroly resolved graphu môže syntakticky správny YAML stále odstrániť gate, rozšíriť credentials alebo zmeniť release bytes bez viditeľného application diffu.

## 27. Kontrolné otázky

1. Prečo source YAML nie je runtime pipeline?
2. Aké compiler phases vedú k resolved graphu?
3. Čo obsahuje resolved configuration digest?
4. Čo je bootstrap trust paradox?
5. Ako trusted wrapper oddeľuje branch validation od deployment authority?
6. Prečo variable provenance ovplyvňuje reprodukovateľnosť?
7. Čo má obsahovať permission diff?
8. Prečo runner selection patrí do security policy?
9. Ako sa pinujú external actions a templates?
10. Čo tvorí template compatibility contract?
11. Prečo sa policy aplikuje na resolved graph?
12. Ako generator dokazuje completeness?
13. Ako sa pipeline change self-validuje?
14. Prečo central template potrebuje canary rollout?
15. Ako floating template zmenil Atlas permissions bez repo diffu?
16. Prečo migration gate zmizol z generated graphu?
17. Prečo pipeline rollback neruší deployment side effects?

## Glossary impact

Relevantné pojmy: Pipeline as Code, pipeline compiler, source workflow, resolved pipeline configuration, resolved config digest, bootstrap trust paradox, trusted deployment entrypoint, workflow revision semantics, typed pipeline input, variable provenance, permission graph, immutable dependency pinning, template contract, include/override semantics, dynamic pipeline generator, generated graph completeness, external resolved-graph policy, pipeline self-validation, pipeline canary rollout a pipeline rollback.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Quality gates a approvals](quality-gates-and-approvals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Reusable a parallel pipelines →](reusable-and-parallel-pipelines.md)
<!-- KNOWLEDGE-NAVIGATION:END -->