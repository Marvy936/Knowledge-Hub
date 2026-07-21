# Pipeline as Code

Pipeline as Code znamená, že delivery workflow, jeho dependencies, policy hooks a významné runtime nastavenia sú definované vo versionovanom, reviewovateľnom a automaticky validovanom zdrojovom formáte. Nejde iba o uloženie YAML súboru v repository; cieľom je spravovať delivery mechanizmus rovnakou disciplínou ako produkčný kód.

## 1. Prečo Pipeline as Code

Bez versionovanej definície vzniká:

- neauditovateľná UI konfigurácia,
- nejasný ownership,
- manuálny drift medzi projektmi,
- zmeny bez code review,
- ťažká reprodukcia staršieho runu,
- slabý rollback pipeline logiky.

Pipeline as Code poskytuje:

- históriu,
- diff a review,
- branch workflow,
- testovanie,
- reuse,
- automatizované policy checks,
- traceability od pipeline zmeny po runtime run.

## 2. Deklaratívna definícia

Typická definícia opisuje desired workflow:

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

Platforma z definície vytvorí execution graph. Deklaratívnosť však neznamená, že pipeline nemá imperatívne scripts. Znamená, že orchestration a contracts sú explicitne popísané a versionované.

## 3. Source of truth

Je potrebné určiť, kde je autoritatívna definícia:

- priamo v application repository,
- v central template repository,
- v generated configuration,
- v kombinácii lokálneho entrypointu a versionovaného reusable template.

Viac rovnocenných zdrojov vytvára drift. UI override má byť zakázaný alebo minimálne viditeľný a auditovaný.

## 4. Pipeline definícia patrí k zmene

Výhoda definície v rovnakom repository:

```text
application change
+ test change
+ pipeline change
→ jeden commit a review
```

Nevýhoda: project pipeline môže ovplyvniť privileged execution. Preto musí platforma rozlišovať nedôveryhodnú branch definíciu od trusted default-branch konfigurácie.

## 5. Bootstrap a trust paradox

Pipeline validuje code, ale pipeline definícia je sama code. Otázky:

- kto validuje pipeline zmenu,
- ktorá verzia definície sa použije na pull request,
- môže branch zmeniť runner labels alebo secrets,
- môže zmeniť deployment target,
- môže načítať nedôveryhodný template?

Bezpečný model často používa:

- obmedzené permissions pre branch pipeline,
- protected environment rules mimo repository,
- centrally enforced policy,
- trusted deploy workflow z default branch,
- signed/pinned reusable components.

## 6. Pipeline schema validation

Pred vytvorením runtime graphu validuj:

- syntax,
- schema,
- references,
- required fields,
- type constraints,
- cycles v DAG,
- neznáme jobs alebo dependencies,
- forbidden capabilities.

Platný YAML ešte neznamená platnú pipeline.

## 7. Lint a static analysis pipeline definície

Kontroly môžu odhaliť:

- mutable images,
- unpinned external actions,
- secrets v plaintexte,
- shell injection risk,
- príliš široké permissions,
- chýbajúce timeouts,
- privileged runners,
- artifacts bez retention,
- deployment bez protected environmentu.

Pipeline linter je shift-left control pre delivery platformu.

## 8. Version pinning

Externé dependencies pipeline zahŕňajú:

- container images,
- reusable actions/plugins,
- templates,
- package managers,
- scripts stiahnuté zo siete,
- base runner image.

Preferuj immutable identity:

```text
container image digest
commit SHA
signed release digest
versioned internal template
```

Mutable `latest` alebo floating major version znižuje reprodukovateľnosť a môže meniť správanie bez repository diffu.

## 9. External actions a plugins

Third-party pipeline action beží s permissions jobu. Je to software supply-chain dependency.

Posúď:

- source a ownership,
- pinned revision,
- release process,
- permissions,
- network access,
- update policy,
- known vulnerabilities,
- možnosť interného mirroru.

Jednoriadkové použitie action môže predstavovať stovky riadkov privileged code.

## 10. Scripts vs. inline commands

Krátke glue commands môžu byť inline. Komplexná logika patrí do testovateľného scriptu alebo nástroja:

```text
pipeline YAML
→ orchestration a contracts

scripts/tooling
→ business a deployment logic
```

Dlhý inline shell je ťažko testovateľný, zle reusable a citlivý na quoting chyby.

## 11. Reprodukovateľnosť

Na reprodukciu runu potrebuješ poznať:

- pipeline definition revision,
- source commit,
- included template revisions,
- runner image/version,
- container digests,
- input variables,
- policy version,
- artifacts a caches,
- external service versions.

Pipeline as Code zlepšuje reprodukovateľnosť, ale sama ju negarantuje.

## 12. Variables a configuration

Rozlišuj:

- repository-level non-secret config,
- environment config,
- protected variables,
- runtime inputs,
- derived metadata,
- secrets.

Pre každú premennú definuj:

- type,
- default,
- required/optional,
- allowed scope,
- sensitivity,
- validation,
- precedence.

Nejasná precedence medzi UI, group, project a job variables vedie k ťažko diagnostikovateľnému správaniu.

## 13. Secrets

Pipeline definition nemá obsahovať reálne secrets. Použi:

- secret manager references,
- environment-scoped secrets,
- short-lived workload identity,
- masked/protected variables iba tam, kde sú potrebné.

Masking logu nie je bezpečnostná boundary. Secret môže uniknúť cez artifact, process list, network request alebo encoding.

## 14. Least privilege

Permissions deklaruj explicitne per job:

```text
verify job
→ read source

publish job
→ write artifact registry

deploy job
→ environment-scoped deployment role
```

Default write-all token je slabý model. Pipeline code review musí zahŕňať permission diff.

## 15. Includes a templates

Central template môže poskytovať:

- štandardné build jobs,
- security gates,
- artifact publication,
- deployment patterns,
- observability metadata.

Template musí mať:

- versioned contract,
- changelog,
- compatibility policy,
- deprecation proces,
- test suite,
- ownera.

Centralizácia bez versioningu vytvára globálny breaking change.

## 16. Inheritance a hidden jobs

Mnohé platformy podporujú inheritance alebo anchors. Príliš hlboká hierarchia komplikuje výslednú pipeline.

Preferuj:

- malý počet explicitných layers,
- jasné parameters,
- rendered configuration preview,
- dokumentovaný merge/override model.

Developer musí vedieť zistiť, aká job definícia sa skutočne vykoná.

## 17. Dynamic pipeline generation

Pipeline môže generovať child configuration podľa repository graphu alebo zmenených komponentov.

Výhody:

- selective CI,
- dynamické matrix jobs,
- veľké monorepo.

Riziká:

- generator sa stáva critical compilerom,
- generated config je ťažšie reviewovateľný,
- injection cez filenames/metadata,
- nejasná traceability.

Generator musí byť versionovaný, testovaný a výsledná konfigurácia uložená ako artifact/evidence.

## 18. Pipeline testing

Testovacie vrstvy:

### Static validation

- syntax a schema,
- policy lint,
- forbidden patterns,
- dependency graph.

### Unit tests scripts/tooling

- argument parsing,
- plan generation,
- edge cases,
- error handling.

### Component tests

- pipeline job v disposable runner environment-e,
- fake registry/cloud endpoint,
- artifact flow.

### Integration tests

- sandbox repository/project,
- reálna CI platforma,
- protected environment bez produkčného dopadu.

## 19. Pipeline change rollout

Pipeline zmena môže zastaviť delivery celej organizácie. Použi:

- canary projects,
- opt-in template version,
- compatibility matrix,
- staged migration,
- rollback revision,
- telemetry.

Central template nemá byť prepnutý globálne bez overenia representative projects.

## 20. Policy as Code

Organizácia môže vynucovať:

- allowed runner pools,
- pinned images,
- required security jobs,
- restricted production deployment,
- artifact signing,
- forbidden secret patterns.

Policy má byť versionovaná, testovaná, auditovateľná a musí mať exception lifecycle.

## 21. Code ownership

Pipeline súbor potrebuje CODEOWNERS alebo ekvivalent pre relevantné paths:

```text
/.ci/**                 @platform-team
/deploy/**             @platform-team @service-owner
/security-policy/**    @security-team
```

Ownership nemá znamenať, že platform tím schvaľuje každú aplikačnú zmenu. Má sa zamerať na citlivé pipeline capabilities.

## 22. Review pipeline zmeny

Review checklist:

- mení sa trigger alebo permissions,
- pribúda external dependency,
- používa sa mutable reference,
- zvyšuje sa network/secret access,
- mení sa artifact identity,
- obchádza sa gate,
- mení sa environment alebo approval,
- existuje timeout a cleanup,
- je zmena testovateľná a rollbackovateľná.

## 23. Observability a audit

Uchovaj:

- resolved pipeline configuration,
- template versions,
- policy decisions,
- runner identity,
- input variables bez secret values,
- job permissions,
- artifacts a deployment records.

Resolved configuration je často dôležitejšia než jednotlivé source fragments.

## 24. Anti-patterny

### YAML ako programovací jazyk bez hraníc

Komplexná logika, loops a string templating v YAML znižujú čitateľnosť a testovateľnosť.

### Copy-paste pipeline per repository

Opravy a security controls driftujú.

### Jeden mutable central template

Každá zmena môže okamžite rozbiť všetky projects.

### Pipeline s permanentnými admin credentials

Repository write access sa môže zmeniť na infrastructure admin access.

### Download-and-execute z internetu

```bash
curl https://example/script.sh | bash
```

Bez pinning-u, integrity verification a review je to supply-chain riziko.

## 25. Troubleshooting

### Pipeline sa správa inak bez zmeny repository

Over floating templates, mutable images/actions, runner image update, UI variables a policy version.

### Include zmenil job nečakane

Pozri resolved config a template merge/override semantics. Pin template version.

### Branch pipeline získala production secret

Ide o trust-boundary failure. Over protected variable rules, trigger context, environment policy a token permissions.

### Pipeline config je validná, ale job neexistuje

Dynamic rules alebo conditions mohli job odstrániť. Skontroluj rendered execution graph a event context.

## 26. Kontrolné otázky

1. Čo Pipeline as Code poskytuje nad rámec YAML súboru?
2. Kde môže byť autoritatívny source pipeline definície?
3. Čo je bootstrap/trust paradox pipeline?
4. Prečo treba pinovať external actions a images?
5. Kedy presunúť inline logiku do scriptu alebo nástroja?
6. Aké vrstvy testovania pipeline poznáš?
7. Aké riziká má dynamic generation?
8. Ako bezpečne rolloutovať central template zmenu?
9. Čo má obsahovať review pipeline permission diffu?
10. Prečo je resolved configuration dôležitá pre audit?

## Glossary impact

Relevantné pojmy: Pipeline as Code, resolved pipeline configuration, pipeline schema, reusable template, template pinning, dynamic pipeline, child pipeline, policy as code, workload identity, pipeline permission boundary a canary template rollout.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Quality gates a approvals](quality-gates-and-approvals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Reusable a parallel pipelines →](reusable-and-parallel-pipelines.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
