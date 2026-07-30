# Golden paths a paved road

Golden path je podporovaný end-to-end spôsob, ako konkrétny user segment vykoná opakovaný developer journey s bezpečnými defaults, integrovanými capabilities a zrozumiteľným supportom. Paved road je širší operating model: organizácia investuje do cesty, ktorá je jednoduchšia, spoľahlivejšia a lacnejšia na prevádzku než individuálne skladanie toolchainu, no zachováva explicitné extension, exception a detach semantics.

Golden path nie je repository template. Template môže vytvoriť počiatočné files, ale cesta pokračuje cez identity, pipeline, infrastructure, GitOps, secrets, observability, upgrades, incidents a decommissioning.

```text
target job, segment a risk
→ versioned path contract a eligibility
→ pinned dependency graph
→ inputs, defaults, constraints a extension points
→ durable instantiate alebo adopt operation
→ managed delivery/runtime resource graph
→ first usable a production outcome
→ supported second change, upgrade a incident recovery
→ exception, contribution alebo detach state
→ second generation a second cohort
```

Path acceptance sa uzatvára až vtedy, keď vzniknutý service zostáva na spravovateľnom lifecycle-e a tím dokáže vykonať ďalšiu zmenu bez ručného forku alebo tribal knowledge.

## 1. Golden path, paved road, template a guardrail

Golden path je user journey a capability contract pre konkrétny job. Paved road je preferovaný organizational direction, do ktorého platforma investuje reliability, documentation, support a cost optimization. Template je jeden bootstrap alebo transformation mechanismus. Guardrail je enforced invariant na authoritative boundary.

```text
golden path
→ podporovaný journey

paved road
→ preferovaná investovaná cesta

template
→ artifact alebo workflow step

guardrail
→ povinný safety/policy verdict
```

Zameniť golden path za template vytvára copy-and-forget debt. Zameniť paved road za nezdokumentovaný zákaz vytvára golden cage. Bezpečnostný invariant môže byť povinný, ale opinionated implementation má mať odôvodnený extension alebo exception model.

## 2. Exact golden-path subject

Path subject identifikuje path name, version a contract digest, target segment a job, input schema a selected choices, resolved template/actions/modules/charts/policies, output inventory, ownership graph, compatibility a upgrade channel, extension points, exception alebo detach state, support tier a acceptance evidence.

Mutable tag `regulated-service-v4` nie je complete identity, ak custom action používa image `latest` a Terraform module branch `main`. Rovnaký template name môže v dvoch dňoch vytvoriť odlišné repositories, permissions a infrastructure. Reproduction a incident analysis preto potrebujú resolved revisions a output provenance.

```text
path RSP-4.1
+ action digest A17
+ Terraform module digest T42
+ pipeline contract P9
+ selected regulated/EU/stateful options
→ exact instantiated service graph
```

## 3. Journey, nie iba create artifact

Kompletný golden path pokrýva discovery, onboarding, local development, build/test, environment provisioning, deployment/promotion, operation, scale/change, credential rotation, incident recovery, path upgrade, ownership transfer a decommission.

Nie každý krok musí mať rovnakú automatizáciu. Každý však potrebuje supported interface, authority, status a recovery. Ak repository vznikne za sedem minút, ale private network a database sa riešia tromi ticketmi, create experience nie je end-to-end golden path.

Momentmi pravdy sú prvý usable environment, prvý failure, prvý production canary, druhá bežná zmena, prvý upgrade a incident. Path testovaný iba na fresh repository happy path-e nepreukazuje dlhodobú použiteľnosť.

## 4. Decision architecture a progressive disclosure

Golden path znižuje extraneous cognitive load presunom opakovaných decisions do bezpečných defaults. Nemá však skrývať choices, ktoré menia data, cost, security alebo recovery contract.

Decision môže byť fixed invariant, default s bounded override, required explicit choice, value derived z authoritative contextu, unsupported combination alebo supported extension point. Výber `multi-region` musí vysvetliť replication, failover, cost a operational responsibilities; nemá byť iba checkbox.

Rozhranie používa progressive disclosure:

```text
normal path
→ jednoduchý intent, defaults a predicted outcome

decision point
→ constraints, trade-offs a effect

failure
→ operation ID, underlying boundary a repair path

advanced need
→ supported extension alebo lower-level API
```

Dobrá abstraction odstráni provider syntax, ale zachová stable resource identities, ownership a debugging evidence.

## 5. Bootstrap copy verzus managed lifecycle

Application business code prirodzene patrí tímu. Security-sensitive pipeline logic, policies, modules a operational contracts však často potrebujú managed update channel. Golden path preto rozdeľuje output na application-owned source, referenced managed components, deterministically regenerable files, platform-owned runtime resources a explicitné local extension points.

Copy model vytvára divergence debt. Po prvom commite sa každá generated pipeline vyvíja samostatne a security fix vyžaduje inventory všetkých forks, conflict resolution a ručné PR. Managed component znižuje tento cost, ale zvyšuje shared blast radius a potrebuje semantic versioning, compatibility tests, staged rollout, rollback a consumer inventory.

Service musí mať stav vzhľadom na path:

```text
ManagedCurrent
ManagedUpdateAvailable
Migrating
ExceptionActive
DetachedOwnedByTeam
Deprecated
Retired
```

Detached nie je neviditeľný failure. Je to explicitný ownership transition, pri ktorom tím preberá upgrade, security, support a audit responsibilities.

## 6. Composition graph a supply-chain identity

Golden path skladá service identity, repository a branch policy, pipeline/provenance, environment Git, runtime namespace, workload identity, data/network dependencies, secrets, policies, telemetry, catalog relations a lifecycle contract. Integration correctness je property celého graphu.

Path generation má pinovať alebo policy-bound resolve-nuť executable dependencies: Backstage template, custom action image, Terraform/OpenTofu module, chart, pipeline component, policy bundle a documentation schema. `latest` a `main` vytvárajú hidden rollout bez path version transitionu.

Template authorization a input validation sú potrebné, no custom action je privileged execution boundary. Potrebuje typed inputs, sandbox a egress policy, scoped credentials, secret-safe logs, idempotency a read-back. Backstage scaffolder task môže byť experience entrypoint, ale durable platform operation má pokračovať mimo task processu.

## 7. Preflight, instantiate a adopt

Pred mutation sa kontroluje user/team eligibility, capability version, name conflicts, quota/capacity, required private networking, identity permissions, data classification, provider dependencies a current target state. Validation bez reservation negarantuje, že capacity ostane dostupná; plan má preto rozlišovať checked, reserved a runtime-dependent preconditions.

Instantiate operation vytvára stable service identity a expected output inventory. Každý child resource nesie operation/path metadata a je read-backnuteľný po timeout-e. Adopt flow pre existujúci service je rovnako dôležitý: inventarizuje current resources, porovnáva path contract, navrhne non-destructive migration a explicitne označí unsupported deviations.

Path nie je iba greenfield generator. Bez adoption a migration modelu núti brownfield teams k rebuild-u alebo permanentnému bypassu.

## 8. Upgrades, extensions a exceptions

Path update môže meniť managed pipeline, policy, module alebo runtime contract. Platforma potrebuje consumer-version inventory, compatibility rules, preview diff, staged rollout a migration evidence. Automatický update nesmie prepísať application-owned fields alebo zmeniť behavior bez relevantného approvalu.

Extension point má stabilný interface a bounded scope, napríklad extra pipeline step, additional egress dependency alebo custom deployment probe. Editovanie generated internal file-u bez provenance nie je extension; je fork.

Exception flow zaznamenáva exact invariant alebo implementation, od ktorej sa tím odchyľuje, dôvod, risk, ownera, alternative controls, expiry a review trigger. Niektoré safety guardrails nemajú exception. Pri implementation preference môže byť detach správny, ak responsibilities sú transparentné.

## 9. Connected incident `GITOPS-PAY-63`

`Regulated Service v4` bol organizáciou označený za povinný golden path. Skutočná implementation bola Backstage template tag `regulated-service-v4`, custom actions image `latest`, Terraform module `main` a copied pipeline fragments. Private network vyžadovala manual ticket a neexistoval managed upgrade channel.

Za šesť týždňov vzniklo `64` requests, no `19` services vytvorilo template fork alebo detached copy (`30 %`) a `8` platformu obišlo (`13 %`). `28` requests stále potrebovalo manual ticket (`44 %`). Tieto výsledky neboli iba resistance to standardization; boli evidence, že path nepokrýval celý job a generated outputs neostávali managed.

`LP-8841` pre `settlement-repair-api` bol `Succeeded` po `7 minútach`, ale database čakala na capacity, private endpoint chýbal a workload identity nemala provider-reconciliation permission. Retry vytvoril druhý environment PR. Tím otvoril tri tickety a fork-ol pipeline, aby dokončil chýbajúce steps. Prvý production reconcile nastal po `19 hodinách`.

Root cause bolo zamieňanie bootstrap template za managed lifecycle. Chýbal immutable dependency graph, complete capability composition, upgrade channel, extension model a explicitný detach state.

## 10. Authoritative redesign a acceptance paths

`Regulated Service 4.1` má immutable path manifest s pinned action/module/pipeline generations. Preflight kontroluje database capacity, private endpoint a workload permissions pred vytvorením false-complete outputu. Durable operation vytvára complete resource graph a status čaká na usable environment a business canary.

Managed components majú upgrade channel a inventory. Application-owned code zostáva nedotknutý. Extension points riešia legitimate provider-reconciliation customization bez forku celej pipeline. Detach prejde explicitným ownership a risk handoffom.

Positive path overí first creation, first production a second change. Upgrade path migruje existing consumer s preview a rollbackom. Recovery path pokračuje po partial operation bez duplicate PR. Exception path je bounded a auditovateľný. Forbidden path odmietne mutable executable dependency, copied untracked pipeline, hidden ticket, automatic overwrite local ownership, permanent exception a forced path bez capability parity.

## 11. Troubleshooting a anti-patterny

Pri fork/bypass spike-u sa mapuje exact path generation, resolved dependencies, target segment/job, selected inputs, expected a actual output inventory, manual handoffs, ownership, extension demand, consumer version, support events a second-change/upgrade outcome. Fork môže byť symptom chýbajúceho extension pointu, stale dependency alebo unsupported segmentu, nie automaticky neposlušnosť tímu.

Anti-patterny sú: `template = golden path`, `mandatory = adopted`, `copy pipeline a neskôr ju patchneme`, `všetky teams musia mať rovnaký path`, `exception cez Slack`, `upgrade znamená nový template pre nové services` a `first create success = path acceptance`.

## Glossary impact

Relevantné pojmy: golden-path subject, paved road, path contract, decision architecture, managed component, path composition graph, instantiate operation, adoption path, consumer-version inventory, extension point, exception state, detached ownership a golden-path acceptance verdict.

## Primárne zdroje

- [CNCF Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/)
- [CNCF Platform Engineering Maturity Model](https://tag-app-delivery.cncf.io/whitepapers/platform-eng-maturity-model/)
- [Backstage — Software Templates](https://backstage.io/docs/features/software-templates/)
- [Backstage — Authorizing scaffolder tasks and actions](https://backstage.io/docs/features/software-templates/authorizing-scaffolder-template-details/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Platform as a Product](platform-as-a-product.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Self-service →](self-service.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
