# Guardrails

Guardrail je mechanizmus, ktorý udržiava zmenu alebo runtime správanie v explicitnom bezpečnom priestore bez toho, aby centralizoval každé rozhodnutie do manuálneho ticketu. Môže poskytovať safe default, upozornenie, audit, automatickú opravu alebo tvrdé odmietnutie. Jeho hodnotu však neurčuje počet policy súborov. Určuje ju to, či správne identifikuje chránený invariant, vyhodnotí exact subject na authoritative boundary a preukáže effective outcome bez neprimeraného blokovania legitímnej práce.

Guardrail nie je synonymum pre admission webhook, CI lint ani security scanner. Tie sú iba možné enforcement points. Jeden invariant môže mať skorú advisory kontrolu v IDE, reprodukovateľný test v CI, authoritative admission enforcement a runtime detective scan. Ak sa výsledky týchto vrstiev rozchádzajú, organizácia potrebuje vedieť, ktorá vrstva rozhoduje a ktorá iba poskytuje feedback.

## 1. Dominantný model

Guardrail lifecycle začína rizikom alebo invariantom, nie policy jazykom. Najprv sa definuje, akému nežiaducemu effective stavu sa má zabrániť, pre aký subject, s akou toleranciou a na ktorej authority boundary je možné rozhodnutie spoľahlivo presadiť. Až potom sa volí policy engine, rule representation a rollout action.

Policy evaluation sama osebe ešte nie je outcome. Request môže prejsť CI a byť zmenený admission mutation-om. Admission môže request odmietnuť, no existujúce resources ostanú necompliant. Background scan môže nájsť violation, ale bez ownera a remediation pathu sa risk nemení. Guardrail acceptance preto spája request-time decision, stored object, controller-resolved state, runtime behavior a exception lifecycle.

```text
risk, obligation alebo platform invariant
→ exact protected subject a unacceptable outcome
→ authoritative enforcement a observation boundaries
→ versioned policy, parameters, binding a dependencies
→ pre-deployment test a impact analysis
→ staged action: observe, warn, audit, mutate, generate alebo deny
→ request evaluation a decision provenance
→ persisted/effective state read-back
→ runtime, security a business verification
→ violation alebo exception remediation
→ policy evolution, rollback a retirement
→ second-policy a second-tenant validation
```

Verdict musí niesť policy generation, binding/parameter generation, evaluated subject, principal, operation, matched rule set, action, exception identity a effective result. „Policy controller je Ready“ ani „zero denials“ nie sú dostatočné dôkazy.

## 2. Guardrail, gate, default a control

Tieto pojmy sa často používajú zameniteľne, ale majú odlišný účel. Default znižuje decision load a vytvára bezpečný počiatočný stav, no používateľ ho môže zmeniť. Gate zastaví konkrétnu transition, kým nie je splnená podmienka. Control je širší risk-reduction mechanismus, ktorý môže byť technický, procesný alebo organizačný. Guardrail tvorí hranicu povoleného priestoru a môže kombinovať defaults, gates aj detective controls.

```text
safe default
→ odporúčaná hodnota, ktorá znižuje pravdepodobnosť chyby

quality alebo approval gate
→ podmienka pre konkrétnu transition

security/compliance control
→ mechanizmus znižujúci definovaný risk

guardrail
→ systematická hranica, ktorá povoľuje autonómiu iba v prijateľnom priestore
```

Golden path môže poskytovať defaults a supported composition. Guardrail musí aj pri obídení golden pathu odmietnuť zakázaný outcome na authoritative boundary. Scorecard môže ukázať vzdialenosť od štandardu, ale bez enforcement contractu nie je tvrdým guardrailom.

## 3. Exact guardrail subject

Policy name `require-owner` nestačí. Exact subject zahŕňa policy generation, binding, parameters, match constraints, request operation, resource identity, principal a environment. Rovnaká expression môže byť advisory v staging a deny v production. Rovnaký Pod manifest môže byť vyhodnotený pred a po mutation odlišne.

```text
guardrail subject
= policy identity a immutable generation
+ binding a parameter generation
+ enforcement point a engine version
+ request principal, operation a target identity
+ pre-mutation a post-mutation object digest
+ exception identity
+ decision a effective-state observation
```

Pri GitOps treba rozlišovať rendered manifest subject od live admission requestu. CI môže testovať chart render pre jednu values matrix, zatiaľ čo controller aplikuje inú source revision alebo admission pridá fields. Evidence sa nesmie preniesť medzi týmito subjects bez identity continuity.

## 4. Invariant a threat/risk model

Dobrá policy vyjadruje organizáciou pochopený invariant. `containers must runAsNonRoot` je technické pravidlo; underlying invariant môže byť „tenant workload nesmie získať host-level privilege cez root process a privilege escalation“. Jedno field check nemusí invariant plne pokryť, pretože image môže vyžadovať root, user namespace môže meniť význam UID a privileged capability môže obísť očakávanie.

Risk model určuje protected asset, actor, action, precondition, unacceptable outcome a tolerované exceptions. Pri cost guardraile je asset capacity a budget; pri tenant guardraile je asset isolation; pri reliability guardraile je asset availability alebo recoverability. Bez tohto modelu sa policy library zmení na zbierku syntaktických preferencií.

Policy author má vysvetliť aj hranice. Admission nemôže overiť budúce runtime správanie, external dependency availability ani business correctness. Preto sa invariant rozkladá na najskorší spoľahlivý feedback a poslednú authoritative kontrolu.

## 5. Enforcement points a vrstvený feedback

Guardrails môžu pôsobiť v source authoringu, schema validation, CI, artifact publication, Git merge, deployment controlleri, Kubernetes admission, cloud control plane, runtime alebo periodic audit. Každý bod vidí iný subject a má inú latency, authority a failure mode.

Skorá kontrola znižuje feedback time a umožňuje opravu pred drahou mutation. Nemá však nahradiť authoritative enforcement, pretože lokálny tool možno obísť, inputs sa môžu zmeniť a execution path môže používať iný render. Naopak iba runtime deny poskytne silnú boundary, ale môže blokovať produkčný incident alebo odhaliť problém príliš neskoro.

| Boundary | Viditeľný subject | Typická úloha | Limit |
|---|---|---|---|
| IDE alebo pre-commit | source fragment | syntax a rýchle vysvetlenie | obíditeľné, nepozná final composition |
| CI/pull request | resolved render a evidence bundle | impact, tests, policy preview | nemusí byť actual deployed generation |
| Artifact registry | immutable image/attestation | signature, provenance a vulnerability decision | nepozná celý workload a tenant context |
| GitOps render | exact source/dependency graph | policy nad final desired manifestom | nepozná admission mutation a runtime |
| API admission | authenticated request a current cluster context | authoritative allow/deny/mutate | request-time view, availability coupling |
| Controller reconciliation | desired a observed resource graph | generate/correct a dependency handling | controller môže mať broad authority |
| Background audit | stored/live resources | detect pre-existing a drift violations | detective, nie okamžitá prevencia |
| Runtime/observability | effective process, traffic a business effect | verify outcome a detect behavioral risk | neskorší feedback a zložitejšia atribúcia |

Layering má používať rovnaký invariant a korelovateľné policy generations. Inak CI hovorí pass, admission deny a scorecard warning bez vysvetlenia rozdielu.

## 6. Policy definition, parameter a binding

Kubernetes ValidatingAdmissionPolicy oddeľuje abstract policy logic, optional parameter resource a binding, ktorý policy aktivuje a scope-uje. Toto rozdelenie je dôležité aj mimo Kubernetes. Rule bez bindingu nemá effect. Binding bez správneho parameter subjectu môže aplikovať staging limit na production alebo úplne vynechať tenant segment.

Policy generation preto nie je iba hash expression. Zahŕňa match rules, namespace/object selectors, exclusions, parameters, validation actions a failure policy. Ak sa parameter `maxReplicas` zmení, effective guardrail sa zmenil aj bez editácie policy objectu.

Viac matching bindings sa môže skladať. Consumer potrebuje vedieť, či všetky musia prejsť, aká je precedence mutation a ako sa riešia conflicting defaults. Hidden cluster-wide binding je rovnaký authority problém ako hidden Helm override.

## 7. Validation actions a enforcement semantics

Validation môže mať action `Deny`, `Warn` alebo `Audit`. Deny zastaví request; Warn ho dovolí a vráti client warning; Audit zaznamená result do audit eventu. Tieto actions predstavujú odlišný risk decision, nie iba log level.

Warn a Audit sú vhodné pre discovery impactu a staged rollout, ale nechránia invariant pred novým violation. Zero denials pri warn-only policy je tautológia, nie success. Dashboard musí reportovať matched requests, pass/fail/error/skip, warning delivery, exception use a residual effective violations.

`failurePolicy` určuje, čo sa stane pri policy evaluation error alebo nedostupnom webhooku. Fail-open môže zachovať API availability, ale vpustí neoverené requests. Fail-closed chráni invariant, ale policy outage sa stáva control-plane outage-om. Rozhodnutie sa robí per risk class a musí mať capacity, timeout, circuit a emergency design.

## 8. Mutation a defaulting

Mutation môže znížiť cognitive load a automaticky pridať safe fields. Zároveň mení subject po tom, čo používateľ odoslal intent. Ak viac mutators píše rovnaké fields, vzniká precedence, convergence a ownership problém. Mutation, ktorá ticho zmení image registry, service account alebo node placement, môže mať zásadný security a tenant dôsledok.

Safe mutation má byť deterministic, idempotentná a transparentná. User má vidieť preview alebo effective diff. Mutated field potrebuje ownera a compatibility contract. Controller alebo ďalšia mutation nesmie hodnotu donekonečna prepisovať a vytvoriť hot loop.

Pre critical invariant je často vhodnejší default v golden path + validation na admission boundary. Mutation sa použije tam, kde existuje jednoznačný bezpečný canonical form, nie ako náhrada nejasného product decisionu.

## 9. Generation a corrective guardrails

Generate policy môže vytvoriť NetworkPolicy, ResourceQuota, RoleBinding alebo observability baseline pri vzniku namespace. To znižuje missing-control risk, ale zavádza controller s authority nad tenant resources. Treba rozhodnúť, či generated object zostáva controller-owned, či tenant môže editovať vybrané fields a čo sa stane pri policy update.

Corrective guardrail môže patchnúť drift alebo vytvoriť chýbajúci resource. Automatická oprava je bezpečná iba pri jednoznačnom desired state a bounded blast radius. Pri data retention, IAM alebo network rules môže slepá correction prerušiť službu alebo rozšíriť access. Najprv treba read-back a conflict detection.

Generate/corrective lifecycle musí pokryť creation, update, deletion, orphan cleanup a controller outage. Namespace delete nemá nechať cluster-scoped RoleBinding alebo cloud credential. Policy retirement nemá automaticky odstrániť resource, ktorý už získal ďalších consumers.

## 10. Image, provenance a artifact guardrails

Image policy môže vyžadovať immutable digest, signature, trusted issuer a attestation. Digest pinning zabraňuje tomu, aby mutable tag neskôr ukazoval na iný obsah. Signature overuje väzbu na identitu alebo key authority; attestation môže niesť build provenance, SBOM alebo scan result.

Každý evidence document musí byť viazaný na exact artifact digest a platform. „Image je signed“ neznamená, že bola built trusted pipeline-om alebo že vulnerability decision je aktuálny. Policy musí rozlíšiť signature validity, signer authorization, attestation predicate, subject digest, freshness a revocation.

Registry outage a key-provider outage vytvárajú failure-policy decision. Cached verified digest môže byť prijateľný pre existing workload restart, ale nie pre nový neznámy artifact. Emergency exception musí zostať subject-bound a expirovateľná.

## 11. Background audit a existing resources

Admission kontroluje nové CREATE/UPDATE requests. Neopraví automaticky resources, ktoré existovali pred policy, ani runtime drift mimo API mutation. Background scan vyhodnocuje stored resources a vytvára policy reports alebo violations.

Current-state report však nie je historický audit log. Resource delete môže odstrániť report entry a denied admission nemusí byť reprezentovaný v current resource reportoch. Incident analysis preto potrebuje admission metrics, Kubernetes audit/events a policy-controller logs.

Existing violation potrebuje remediation class. Niektoré možno automaticky opraviť, iné vyžadujú migration, restart alebo exception. Okamžité enforce bez inventory a ownera môže zablokovať budúce updates kritickej služby a vytvoriť unmaintainable frozen resource.

## 12. Policy rollout ako migration

Policy rollout je distributed change nad veľkým consumer setom. Najprv sa zmeria expected scope a dry-run impact, potom sa policy testuje na representative fixtures, nasadí v Audit/Warn režime, opraví existing debt a až následne prejde na Deny. Každá fáza má exit criteria a expiry.

```text
invariant a expected subject inventory
→ offline tests a final-render evaluation
→ audit-only matched-coverage baseline
→ owner routing a remediation
→ narrow exceptions s expiry
→ staged warn pre selected cohorts
→ enforce pre low-risk alebo compliant cohorts
→ progressive fleet enforcement
→ residual violation closure
→ second-policy/update rollback test
```

Audit phase sa nesmie stať trvalým pseudo-controlom. Ak risk toleruje iba krátky migration window, deadline a accountable owner sú súčasťou policy contractu. Ak policy nie je schopná bezpečne prejsť do enforce, možno je invariant zle modelovaný alebo enforcement point nemá potrebný context.

## 13. Exceptions a break-glass

Exception je explicitná dočasná zmena risk decisionu. Musí identifikovať policy, exact subject, reason, owner, approver, start, expiry, compensating controls a closure evidence. Selector `namespace has migration=true` bez resource identities a expiry je alternate policy, nie exception.

Exception nesmie byť prenosná na nový artifact, tenant alebo environment bez nového rozhodnutia. Zmena subjectu invaliduje evidence. Renewal musí znovu overiť risk a remediation progress; automatické nekonečné renewal odstráni guardrail.

Break-glass je urgentný exception path s vyššou observability a následnou reconciliation. Nemá vypnúť celý policy engine, ak stačí narrow operation. Po incidente sa overí effective state, odstránia residual privileges a uzavrie root cause.

## 14. Policy testing a validation

Policy code potrebuje unit-like expression tests, schema tests, positive/negative fixtures, binding/selector tests a integration test proti actual engine version. Final-render tests zachytia composition; admission tests zachytia defaulting, mutation a live cluster context.

Test matrix musí obsahovať aj no-match cases. Najčastejší false green nie je policy expression, ktorá vráti nesprávny pass, ale binding, ktorý sa na intended subject vôbec neaplikuje. Preto sa overuje expected subject inventory a match coverage.

Upgrade engine-u alebo policy API môže zmeniť syntax, libraries, ordering alebo report semantics. Compatibility evidence sa viaže na engine version. Rollback policy musí byť testovaný rovnako ako rollout, najmä ak stored resources už závisia od generated defaults.

## 15. Observability a guardrail SLO

Guardrail observability potrebuje denominator. Počet violations bez počtu matching requests neukáže coverage ani trend. Zero failures môže znamenať perfektnú compliance, nesprávny selector, vypnutý webhook alebo unavailable report controller.

| Signal | Identity | Význam |
|---|---|---|
| Expected subject inventory | policy scope generation | koľko resources alebo requests má policy pokryť |
| Match rate | policy/binding + operation | či selector a rules zasahujú intended subjects |
| Pass/fail/warn/error/skip | policy generation + subject | evaluation outcome a engine health |
| Deny rate | rule + tenant/environment | blocked unsafe changes a adoption friction |
| Exception use | exception + subject + expiry | accepted residual risk a bypass concentration |
| Evaluation latency/timeout | engine + rule | impact na control-plane availability |
| Background violations | resource generation | existing a drift debt |
| Mutation diff | pre/post digest + field owners | hidden change a conflict risk |
| Effective compliance | runtime/resource read-back | či stored a running state spĺňa invariant |
| Business/security guard outcome | incident/cost/data metric | či policy znižuje pôvodný risk |

SLO môže napríklad vyžadovať, aby 99.99 % production admission requests pre critical tenant-isolation policies bolo vyhodnotených bez erroru do definovaného latency budgetu a aby žiadny accepted request neviedol k cross-tenant effective access. Latency SLI bez correctness a coverage je neúplná.

## 16. Policy ownership a product model

Guardrail má policy ownera, risk ownera a platform operatora. Policy owner udržiava rule a tests, risk owner rozhoduje o tolerancii a exceptions, platform operator zabezpečuje engine availability a rollout. Application owner opravuje konkrétny violation, ale nemá sám meniť global invariant.

Policy backlog sa riadi podľa risk reduction a developer friction. Opakované exceptions môžu znamenať chýbajúci golden-path capability alebo príliš hrubý invariant. Guardrail tím nemá iba pridávať deny rules; má analyzovať false positives, time-to-remediate a bypass root causes.

Documentation musí vysvetliť, prečo rule existuje, ako ju splniť, ako diagnostikovať failure a kedy je legitímna exception. Nezrozumiteľný deny message presúva cognitive load do support queue a motivuje obchádzanie.

## 17. Connected incident `GITOPS-PAY-64`

Guardrail program `GP-7` mal chrániť tenant isolation pre `settlement-export-api`. Policy set obsahoval required tenant labels, default-deny NetworkPolicy, zákaz cross-namespace credential references, image verification a restricted-profile node placement. Platform tím však vyhodnotil rollout ako úspešný, pretože admission dashboard zobrazoval `0 denied requests`.

Effective policy graph bol odlišný:

```text
CI policy generation:                gp7-rc3
admission policy generation:         gp7-rc2
validation actions:                  Warn, Audit
namespace binding selector:          isolation-profile=restricted
actual namespace label:              isolation-profile=standard
PolicyException selector:            platform.atlas.io/migration=true
exception expiry:                    none
background report controller:        healthy
denied requests:                     0
matched cross-tenant rule requests:  0
```

Catalog stale projection spôsobila nesprávny standard profil, takže restricted binding sa vôbec nematchol. Širšia cluster policy síce cross-namespace `credentialRef.namespace` rozpoznala, ale migration exception ju preskočila. Report ukazoval `skip`, no dashboard agregoval iba `deny`. Policy controller, webhook aj report controller boli technicky healthy.

Request na `SettlementConnection` preto prešiel. Cluster-scoped operator s broad credentialom načítal Secret z Orion namespace a vytvoril connection pre Vega workload. Guardrail zlyhal v troch rôznych miestach: nesprávny subject classification, no-match binding a unbounded exception. Expression samotná bola správna.

### Guardrail redesign

Redesign viaže policy na tenant registry a catalog critical generation, nie iba na mutable namespace labels. Vending operation vytvorí immutable `IsolationProfileBinding`, ktorého tenant ID a profile generation overuje admission proti namespace UID. Missing alebo stale binding je Deny pre privileged custom resources.

Policy rollout dashboard reportuje expected inventory, match coverage, evaluation results a exceptions. `Warn/Audit` má deadline a exit criteria; critical cross-tenant reference policy ide priamo do enforce po negative tests. Exception potrebuje exact resource UID, credential target, owner, expiry a compensating block a nemôže byť vybraná broad namespace selectorom.

```text
tenant/isolation contract generation
→ policy + binding + parameter generation
→ expected namespace/resource inventory
→ preflight and final-render test
→ admission match proof
→ Deny cross-tenant reference
→ operator-side tenant authorization
→ stored object and generated connection read-back
→ network/credential negative canary
→ policy report and exception closure
```

Guardrail teda nekončí admission response-om. Operator, network a credential authorities musia overiť rovnaký tenant invariant na svojich boundaries.

## 18. Guardrail acceptance verdict

Acceptance verdict musí dokázať, že guardrail chráni konkrétny invariant na správnej boundary a že legitimate workflows zostávajú použiteľné. Policy syntax pass alebo controller readiness nestačí. Potrebný je expected subject inventory, match proof, decision provenance, effective-state verification a evidence pôvodného risk outcome-u.

Verdict zahŕňa failure behavior. Testuje sa engine outage, timeout, missing parameter, selector mismatch, exception expiry, policy rollback, existing resource a second tenant. Pri mutácii sa overí field ownership a convergence; pri generation sa overí lifecycle; pri deny sa overí recovery path a zrozumiteľný feedback.

Guardrail je prijatý, keď:

- **Invariant je explicitný** — protected asset, unacceptable outcome, scope a tolerancia sú zdokumentované.
- **Subject je exact** — policy, binding, parameter, engine, principal, operation a resource generation sú korelovateľné.
- **Authority boundary je vhodná** — skoré checks dopĺňajú, ale nenahrádzajú final enforcement.
- **Match coverage je dokázaná** — denominator pochádza z expected subject inventory a no-match je viditeľný.
- **Actions majú správnu semantics** — Warn/Audit nie sú vydávané za prevention a Deny má recovery contract.
- **Failure policy je risk-based** — fail-open/fail-closed rozhodnutie má availability a security evidence.
- **Mutation/generation konverguje** — writes sú deterministic, idempotentné a majú lifecycle ownership.
- **Effective compliance je overená** — stored object, controller output a runtime outcome zodpovedajú invariant-u.
- **Exceptions sú bounded** — exact subject, owner, reason, expiry, compensating control a closure sú povinné.
- **Rollout je migration** — audit, remediation, warn a enforce fázy majú exit criteria.
- **Observability je complete** — match, pass/fail/error/skip, exception, latency a residual violations sú viditeľné.
- **Second-policy a second-tenant test prešiel** — composition, update, rollback a isolation zostali správne.

## 19. Troubleshooting flow

Guardrail troubleshooting nezačína editáciou expression. Najprv sa určí, či policy mala subject vôbec vyhodnotiť, aká binding a parameter generation bola effective a či exception alebo failure policy zmenila action. Potom sa sleduje persisted a runtime state.

```text
unsafe request prešiel alebo legitímny request bol zablokovaný
→ exact principal, operation, resource a pre/post-mutation digest
→ expected policy/binding/parameter generation
→ match rules, selectors a exclusions
→ exception a failure-policy evaluation
→ engine logs, audit event a policy report
→ admission decision
→ stored object a field ownership
→ controller/runtime effective state
→ containment alebo safe recovery
→ policy, binding, parameter alebo capability remediation
→ second request a negative test
```

Pri unsafe accepted requeste treba fence downstream controller alebo credential authority; samotná zmena admission policy nevráti už vytvorený resource. Pri false deny treba zachovať request a policy evidence, použiť narrow emergency path a opraviť root cause bez global vypnutia guardrailu.

## 20. Anti-patterny

Guardrail anti-patterny vznikajú pri zámene policy activity za effective risk reduction. Každý z nasledujúcich vzorov treba sledovať od expected subjectu cez decision až po stored a runtime outcome.

### Policy count ako maturity metric

Sto rules môže vytvoriť viac konfliktov, exceptions a outage risku než desať dobre modelovaných invariantov. Maturity sa meria coverage, correctness, remediation a risk outcome-om. Policy portfolio bez retirement a ownershipu iba akumuluje neznáme interactions.

### CI pass ako production enforcement

CI hodnotí konkrétny render a možno iný policy bundle. Direct apply, iný values input alebo admission mutation môže zmeniť subject. Final authoritative boundary musí invariant znovu overiť.

### Warn/Audit vydávaný za protection

Warn a Audit sú feedback a discovery actions. Ak risk vyžaduje prevention, rollout musí mať enforce transition alebo iný authoritative control. Trvalý audit-only stav musí byť explicitne prijatý ako residual risk, nie prezentovaný ako hotový guardrail.

### Zero denials ako success

Zero môže znamenať zero violations alebo zero matches. Bez expected inventory a match rate je metrika neinterpretovateľná. Rovnaký false green vznikne pri broad exception, disabled webhooku alebo report pipeline, ktorá nezachytáva denied requests.

### Broad namespace exception

Selector-based bypass bez resource identity a expiry sa stáva alternate policy. Výnimka má byť narrow, expirovateľná a viazaná na remediation. Jej použitie sa musí objaviť v decision evidence a residual-risk dashboarde.

### Mutation bez preview a field ownershipu

Tichá zmena service accountu, image alebo placementu znižuje dôveru a môže konfliktovať s GitOps controllerom. Safe default patrí do pathu a authoritative mutation potrebuje transparentný diff.

### Fail-open alebo fail-closed ako univerzálne pravidlo

Security a availability risks sa líšia podľa invariantov. Jedna global voľba vytvorí buď bypass, alebo control-plane outage. Failure semantics sa navrhujú per policy class. Rozhodnutie potrebuje test timeoutu, dependency outage-u a recovery, nie iba konfiguračnú hodnotu.

### Guardrail bez supported pathu

Deny rule, ktorý neponúka kompatibilný spôsob splnenia, vytvára ticket queue a obchádzanie. Guardrail a platform capability sa musia vyvíjať spolu. Opakované exceptions sú product evidence, že supported path alebo invariant model je neúplný.

## 21. Kontrolné otázky

1. Ako sa líši guardrail, gate, default a control?
2. Čo tvorí exact guardrail subject?
3. Prečo policy expression nie je celý effective guardrail?
4. Ako sa rozdeľuje feedback medzi IDE, CI, GitOps render, admission a runtime?
5. Akú úlohu majú policy, parameter a binding?
6. Prečo Warn/Audit nie sú preventívny verdict?
7. Ako failurePolicy mení security a availability contract?
8. Kedy je mutation bezpečná a prečo potrebuje field ownership?
9. Ako sa rollout policy podobá distributed migration?
10. Čo musí obsahovať policy exception?
11. Prečo `GITOPS-PAY-64` ukazoval zero denials, hoci cross-tenant request prešiel?
12. Čo musí obsahovať guardrail acceptance verdict?

## Glossary impact

Relevantné pojmy: guardrail, guardrail subject, protected invariant, enforcement boundary, policy generation, policy binding generation, policy parameter generation, match coverage, validation action, guardrail failure policy, policy mutation ownership, generated guardrail resource, background policy audit, policy rollout migration, policy exception subject, effective compliance, guardrail acceptance verdict.

## Primárne zdroje

Zdroje pokrývajú Kubernetes admission semantics, declarative policies, actions, failure behavior a súčasné policy-engine mechanisms pre validation, mutation, generation, reports, exceptions a image verification. Kapitola z nich odvodzuje všeobecný guardrail lifecycle, ale konkrétny risk a rollout contract zostáva organizačným rozhodnutím.

Tieto dokumenty sú primárnymi zdrojmi pre API a engine semantics, nie hotovým organizačným risk modelom. Konkrétna platforma musí navyše určiť protected invariants, expected subject inventory, failure-policy class, exception authority a rollout exit criteria. Pri výbere mechanismu treba overiť aktuálnu API maturity a deprecations; napríklad policy typy a report behavior sa medzi verziami engine-u menia a evidence musí zostať viazaná na deployed generation.

- [Kubernetes — Validating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/)
- [Kubernetes — Admission Control](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)
- [Kubernetes — Manifest-Based Admission Control](https://kubernetes.io/docs/reference/access-authn-authz/manifest-admission-control/)
- [OPA Gatekeeper — Documentation](https://open-policy-agent.github.io/gatekeeper/website/docs/)
- [OPA Gatekeeper Library](https://open-policy-agent.github.io/gatekeeper-library/website/)
- [Kyverno — Policy Types Overview](https://kyverno.io/docs/policy-types/overview/)
- [Kyverno — Applying Policies](https://kyverno.io/docs/guides/applying-policies/)
- [Kyverno — Policy Reports](https://kyverno.io/docs/guides/reports/)
- [Kyverno — Policy Exceptions](https://kyverno.io/docs/guides/exceptions/)
- [Kyverno — ImageValidatingPolicy](https://kyverno.io/docs/policy-types/image-validating-policy/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Service catalog](service-catalog.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Multi-tenancy →](multi-tenancy.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
