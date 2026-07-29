# Golden paths a paved road

Golden path je podporovaný, dokumentovaný a automatizovaný spôsob, ako vykonať opakovaný developer journey s bezpečnými defaults a integrovanými organizačnými capabilities. Paved road je širší operating model: organizácia investuje do cesty, ktorá je jednoduchšia, spoľahlivejšia a lepšie podporovaná než individuálne skladanie toolchainu, ale zachováva explicitný mechanizmus pre legitímne odchýlky.

Golden path nie je iba repository template. Template môže vytvoriť počiatočné files, no cesta pokračuje cez identities, pipelines, infrastructure, GitOps, secrets, observability, ownership, upgrades, operations a decommissioning. Ak sa generated content po prvom commite odpojí od platformového contractu, vzniká snapshot, ktorý postupne diverguje a prenáša lifecycle cost na application tím.

## 1. Dominantný model

Dominantný model sleduje jeden developer intent cez výber podporovanej cesty, resolution jej versioned contractu, vytvorenie alebo zmenu managed resources a následnú prevádzku. Cesta musí vysvetliť nielen happy path, ale aj eligibility, decisions, escape, recovery, upgrade a retirement.

Golden-path acceptance nevzniká pri úspešnom scaffolding tasku. Musí preukázať, že výsledný service graph spĺňa path contract, application tím rozumie jeho ownershipu, platforma vie bezpečne aplikovať druhú zmenu a používateľ sa môže odchýliť bez skrytého bypassu alebo trvalého forku.

```text
developer job a workload context
→ discover supported path a eligibility
→ exact golden-path contract a generation
→ explicit inputs, defaults, constraints a extension points
→ preflight policy, quota a dependency validation
→ durable scaffolding alebo platform operation
→ managed repository, delivery, runtime a operational outputs
→ first usable a first production verification
→ supported changes, upgrades a incident recovery
→ exception, contribution alebo exit path
→ second-generation a second-cohort validation
```

Golden path je úspešná, keď preferred cesta znižuje rozhodovaciu a integračnú záťaž bez odstránenia potrebného kontextu a bez premeny platformových assumptions na neviditeľný lock-in.

## 2. Golden path, paved road, template a guardrail

Tieto pojmy riešia súvisiace, ale odlišné vrstvy. Ich zamieňanie vytvára buď príliš slabý model, kde golden path znamená iba README, alebo golden cage, kde sa recommendation presadzuje ako nezdokumentovaný zákaz.

### Golden path

Golden path je end-to-end supported journey pre konkrétny job a user segment. Kombinuje documentation, interfaces, automation, policies, defaults, observability a support. Môže používať viac technických implementácií, pokiaľ zachovávajú rovnaký capability contract.

### Paved road

Paved road je preferovaný organizačný smer, do ktorého platforma investuje reliability, security, documentation, cost optimalizáciu a support. Odchýlka je možná, ale tím preberá alebo explicitne dohodne dodatočné responsibilities a evidence.

### Template

Template je versionovaný vstup do journey. Môže generovať repository, manifests, pipeline alebo documentation. Sám osebe nezabezpečuje runtime readiness, upgrade, policy ani support a po copy môže stratiť väzbu na pôvodnú generation.

### Guardrail

Guardrail je control presadený na authoritative boundary. Môže byť súčasťou golden pathu, ale jeho účelom je vynútiť safety alebo policy invariant, nie iba odporučiť jednoduchšiu cestu. Guardrails budú rozpracované v samostatnej kapitole.

Vzťah:

```text
golden path
→ používateľský journey a podporovaný contract

paved road
→ organizačne preferovaná, investovaná cesta

template
→ jeden delivery mechanizmus alebo bootstrap artifact

guardrail
→ vynútený safety/policy invariant
```

## 3. Exact golden-path subject

Cesta sa nedá hodnotiť podľa názvu `service-template`. Potrebuje exact subject, ktorý identifikuje path generation, target workload, inputs, dependencies, outputs a ownership model. Rovnaký template commit môže pri mutable actions, modules alebo provider defaults vytvoriť odlišný výsledok.

Exact subject umožňuje reprodukovať scaffolding, diagnostikovať failure a rozhodnúť, či existujúci service je stále na managed path alebo už používa detached fork.

Golden-path subject zahŕňa:

- **Path identity, version a contract digest** — jednoznačne označujú podporovanú generation a bránia tomu, aby mutable template name zmenil význam bez auditovateľnej transition.
- **Target user segment a job** — určujú, pre koho a na aký journey je path navrhnutý; stateless API a regulated stateful worker nemusia mať rovnaký contract.
- **Input schema a selected options** — zachytávajú explicitné decisions, data classification, availability, dependencies a extension choices použité pri vytvorení.
- **Resolved template, actions a module revisions** — identifikujú executable supply chain vrátane custom actions, Terraform modules, charts, policies a images.
- **Authoritative output inventory** — uvádza repositories, catalog entities, environments, identities, resources, dashboards a documentation, ktoré path spravuje alebo vytvoril.
- **Ownership a field-authority graph** — oddeľuje platform-managed, team-managed, controller-managed a external fields a zabraňuje writer oscillation.
- **Compatibility a upgrade channel** — určuje, ako sa service dozvie o novej path generation, ktoré changes sú automatické a ktoré vyžadujú migration.
- **Escape alebo exception state** — zaznamenáva odchýlku, dôvod, ownera, expiry a responsibilities namiesto tichého forku.
- **Acceptance evidence** — viaže generated output na tests, policy, runtime readiness a business canary relevantný pre path.
- **Support a lifecycle state** — rozlišuje preview, supported, deprecated, retired a detached generations.

## 4. Cesta je journey, nie artifact

Najčastejšou chybou je redukovať golden path na „Create service“ template. Service lifecycle však pokračuje po repository creation. Používateľ potrebuje robiť zmeny, pridávať dependencies, meniť scale, rotovať secrets, riešiť incident, migrovať schema a nakoniec service odstrániť.

Kompletný journey môže vyzerať takto:

```text
discover path
→ understand contract
→ create service identity
→ develop locally
→ build a test artifact
→ provision environment dependencies
→ deploy a promote
→ observe a operate
→ change architecture alebo capacity
→ recover incident
→ upgrade path generation
→ transfer ownership
→ decommission
```

Path nemusí automatizovať každý krok rovnakou mierou. Musí však jasne definovať podporovaný mechanizmus, ownership a evidence. Ak create je self-service, ale každá zmena vyžaduje ručný platform ticket, journey nie je skutočne paved.

## 5. Opinionated defaults a decision architecture

Golden path redukuje cognitive load tým, že presúva opakované rozhodnutia do bezpečných, zdokumentovaných defaults. Nemá však skrývať decisions, ktoré zásadne menia business, data alebo reliability contract.

Rozhodnutia sa majú klasifikovať:

- **Fixed invariant** — platforma ho presadzuje, pretože chráni organization-wide property, napríklad artifact signing alebo workload identity bez static cloud keyov.
- **Default with override** — platforma ponúka najčastejšiu bezpečnú hodnotu, napríklad baseline resources, ale používateľ ju môže zmeniť v povolenom rozsahu.
- **Required explicit choice** — používateľ musí rozhodnúť, pretože platforma nemá dostatočný kontext, napríklad data classification alebo recovery tier.
- **Derived decision** — platforma hodnotu vypočíta z authoritative contextu, napríklad tenant namespace alebo policy profile podľa owning groupu.
- **Unsupported combination** — request sa odmietne s vysvetlením mechanizmu a alternatívy, nie iba generickou policy chybou.
- **Extension point** — path definuje stabilný interface pre custom behavior bez kopírovania alebo modifikácie celého implementation graphu.

Dobrá decision architecture odhaľuje consequences. Výber `multi-region` má vysvetliť data replication, cost, failover a operational responsibilities, nie iba zobraziť checkbox.

## 6. Abstraction bez straty kontextu

Abstraction je užitočná, keď znižuje počet detailov potrebných pre bežnú action, ale zachováva model potrebný na diagnostiku a zodpovedné rozhodnutie. Platforma nemá nútiť každého developera poznať provider API, no musí ukázať stable resource identity, operation status, ownership a relevantné failure boundaries.

Príliš nízka abstraction vystaví používateľovi raw Kubernetes, Terraform a IAM complexity. Príliš vysoká abstraction zobrazí iba zelený alebo červený status bez dôvodu, identity a repair pathu. Golden path potrebuje progressive disclosure:

```text
normal flow
→ simple intent a outcome

decision point
→ constraints, trade-offs a predicted effect

failure
→ underlying operation, resource identity, evidence a recovery

advanced use
→ supported extension alebo lower-level interface
```

Context sa zachováva aj dokumentáciou „under the hood“. Používateľ má vedieť, ktoré systems sa menia, kde je source of truth a čo sa stane pri retry alebo delete.

## 7. Bootstrap template verzus managed path

Bootstrap template skopíruje files do nového repository. Po vytvorení sa copies vyvíjajú samostatne. Tento model je vhodný pre application-specific code, ale rizikový pre security policy, pipeline logic, infrastructure modules a operational contracts, ktoré sa musia dlhodobo aktualizovať.

Managed path rozdeľuje content:

- **Application-owned source** — business code a domain configuration zostávajú pod ownershipom application tímu a platforma ich neprepisuje bez explicitnej transition.
- **Referenced managed components** — reusable pipeline, chart, module alebo policy sa konzumujú cez versionovaný interface a majú upgrade channel.
- **Generated but regenerable files** — output obsahuje provenance a deterministic regeneration mechanism, takže update možno bezpečne porovnať a aplikovať.
- **Platform-owned runtime resources** — controllers alebo platform APIs spravujú fields podľa explicitného ownership contractu.
- **Local extension points** — custom behavior sa pripája cez podporované interfaces, nie editáciou generated internals.

Copy model vytvára divergence debt. Každý security fix potom vyžaduje inventarizovať forks, porovnať lokálne úpravy a koordinovať stovky PR. Managed component môže znížiť tento cost, ale zvyšuje blast radius a potrebuje compatibility, rollout a rollback discipline.

## 8. Golden path ako composition graph

Reálny path skladá viac capabilities. Jeho výsledok nie je jeden repository, ale graph s dependencies a ownershipom.

```text
service identity
├── source repository a branch policy
├── build pipeline a artifact provenance
├── environment desired-state repository
├── runtime namespace a workload identity
├── network a data dependencies
├── secrets a policy bindings
├── observability, SLO a alerts
├── catalog relations a documentation
└── support, upgrade a decommission contract
```

Composition musí byť version-aware. Ak pipeline contract vyžaduje SBOM v2, ale promotion policy rozumie iba v1, path generation nie je kompatibilná. Path acceptance preto potrebuje dependency graph a integration tests, nie iba unit test templating syntaxe.

## 9. Backstage Software Templates ako implementačný mechanizmus

Backstage Software Templates môžu poskytovať discoverable formulár, review inputs a vykonať sériu scaffolder actions. Každá execution má task identity a steps s inputs a outputs. To je vhodný experience entrypoint, nie automaticky durable platform control plane.

Scaffolder action môže vytvoriť repository, otvoriť pull request alebo registrovať catalog entity. Custom action zároveň predstavuje executable trust boundary: prijíma user-controlled inputs, používa credentials a môže meniť external systems. Potrebuje schema validation, authorization, secret-safe logging, idempotency a read-back.

Bezpečný model:

```text
Backstage form a authorization
→ immutable template/action generation
→ platform API alebo durable orchestrator request
→ operation ID v outpute
→ async status a evidence links
→ catalog/resource projections
```

Rizikový model vykonáva všetky cloud a cluster mutations priamo v jedinom template tasku a po timeout-e odporučí „Start Over“. Blind restart môže vytvoriť duplicate repositories, identities alebo infrastructure.

## 10. Documentation ako executable contract companion

Documentation nie je doplnok po implementácii. Vysvetľuje eligibility, decisions, outputs, ownership, expected timing, failure states, costs, extension a exit. Má byť versionovaná spolu s path contractom a dostupná v kontexte, kde používateľ rozhoduje.

Dokumentácia musí pokrývať tri úrovne:

- **Quick path** — najmenší successful journey s vysvetlením, aký outcome vznikne a aké assumptions platia.
- **Mechanism a operations** — authoritative systems, identities, state transitions, telemetry, retry, recovery a lifecycle.
- **Decision a exception guidance** — kedy path nepoužiť, aké alternatívy existujú a ako sa schvaľuje alebo ukončuje odchýlka.

Docs-like-code môže zlepšiť freshness, ale iba ak release process overuje links, examples a contract compatibility. Stará dokumentácia je hidden interface drift.

## 11. Escape hatch, exception a contribution path

Paved road bez odchýlky sa stáva golden cage. Odchýlka však nemá znamenať neauditovaný bypass. Potrebuje explicitný model podľa dôvodu a dĺžky.

### Supported extension

Používateľ zostáva na path contracte a využije versionovaný extension point, napríklad additional policy rule, sidecar alebo pipeline stage. Platforma naďalej pozná výsledný graph a podporuje core capability.

### Time-bounded exception

Konkrétny invariant sa dočasne uvoľní po risk decisione. Exception má ownera, scope, compensating controls, expiry a návratový plán.

### Alternative paved path

Iný user segment môže mať vlastnú podporovanú cestu, napríklad batch/data workload oproti HTTP service. Nie každá odchýlka je exception.

### Detached ownership

Tím vedome opustí managed path a preberie definované security, upgrade, operations a audit responsibilities. Platforma túto zmenu eviduje, aby detached service nevyzeral ako compliant managed generation.

### Contribution upstream

Opakovaná potreba môže viesť k rozšíreniu product contractu. Contribution má design, compatibility a ownership review; nie každá lokálna úprava sa má automaticky stať global defaultom.

## 12. Versioning a upgrade lifecycle

Golden path potrebuje verziu, ale SemVer template-u samo nestačí. Contract graph obsahuje actions, modules, policies, runtime APIs a generated schema. Upgrade musí identifikovať source a target generation, compatibility a presný consumer inventory.

```text
new path generation
→ compatibility a migration assessment
→ affected consumer inventory
→ preview/diff pre konkrétny service
→ automated alebo reviewed change
→ integration a runtime validation
→ rollout po cohorts
→ old generation deprecation
→ residual consumer closure
```

In-place central update znižuje divergence, ale zvyšuje shared blast radius. Per-repository PR umožňuje review a rollout, ale môže uviaznuť a vytvoriť version spread. Voľba závisí od field ownershipu a risku; často sa kombinuje managed runtime component s reviewed application-level migration.

## 13. Testing golden pathu

Path testovanie musí pokryť viac než render skeletonu. Test subject má obsahovať exact generation a representative input matrix.

Jednotlivé testovacie vrstvy sledujú ten istý path subject cez odlišné failure boundaries. Schema test môže dokázať, že input vytvorí očakávané súbory, ale nevie preukázať, že delegated identity smie vytvoriť databázu, že composition nevytvorí konflikt ownershipu ani že výsledný workload vykoná business operáciu. Preto sa evidence skladá od lacného deterministického renderu cez sandbox mutation a complete composition až po developer journey a runtime canary.

Rozhodujúca je kontinuita identity: každý result musí uviesť path generation, resolved dependencies, input digest a output inventory. Bez nej môže upgrade testovať inú action image než produkčný scaffolder alebo happy-path demo nevedomky používať oprávnenia platform engineera, ktoré cieľový používateľ nemá. Failure v jednej vrstve preto neobchádza nižšie gates; zužuje presný boundary, na ktorom path contract neplatí.

Testing layers:

- **Schema a template tests** — overujú required inputs, conditions, expressions a generated file structure bez external mutation.
- **Action contract tests** — používajú controlled fakes alebo sandbox systems na idempotency, authorization, output schema, secret leakage a unknown outcome recovery.
- **Composition tests** — vytvoria celý capability graph v ephemeral alebo test environment-e a overia dependencies a ownership.
- **Policy a negative tests** — dokazujú, že forbidden region, identity, resource alebo data combination sa odmietne na správnej boundary.
- **Upgrade tests** — migrujú service zo starej generation a overia preserved application changes, compatibility a rollback.
- **Operational tests** — simulujú source outage, quota, partial create, controller restart, credential rotation a decommission.
- **Developer journey tests** — representative user vykoná create, first change, incident diagnosis a delete a poskytne qualitative feedback.
- **Business capability canary** — overí, že výsledný service vykoná reálny domain outcome, nie iba že Pods sú Ready.

Happy-path demo s platform engineerom je slabý oracle. Potrebný je second-user a second-change test, ktorý odhalí implicitné znalosti autora.

## 14. Supply-chain a security boundary

Golden path koncentruje authority. Kompromitovaný template, custom action alebo managed module môže zmeniť stovky services. Preto path artifacts potrebujú rovnakú supply-chain disciplínu ako application artifacts.

Supply-chain boundary začína pri zdroji path definície a končí až pri effective outpute v cieľových systémoch. Review template-u nestačí, ak template počas execution resolve-ne mutable action image, action získa broad cloud credential alebo output policy neoverí skutočne vytvorenú IAM role. Dôveryhodný chain preto viaže source commit, resolved dependency digests, execution identity, input digest, mutation operation IDs a read-back inventory do jednej provenance línie. Každá transition musí odmietnuť subject, ktorý nevie reprodukovateľne identifikovať alebo ktorého scope prekračuje capability contract.

Controls sa presadzujú na odlišných boundaries a navzájom sa nenahrádzajú. Protected review chráni authoring transition, pinning zabraňuje zmene executable bytes po review, least privilege obmedzuje blast radius počas mutation a output read-back odhaľuje confused-deputy alebo provider-defaulting rozdiel. Audit následne umožňuje nájsť všetkých consumers kompromitovanej generation a repair channel vytvorí nový bounded lifecycle namiesto ad-hoc hromadného patchovania. Napríklad podpísaný template stále nie je bezpečný, ak používa `latest` action s cluster-admin credentialom; source authenticity v takom prípade nedokazuje execution integrity ani správny output.

Controls zahŕňajú:

- **Trusted source a protected review** — template, actions a modules majú known owners, branch protections a required evidence.
- **Immutable resolved dependencies** — path generation pinne executable actions, modules, images a policy bundles namiesto mutable tags.
- **Least-privilege execution identity** — scaffolder alebo orchestrator môže meniť iba required resource scope a používa short-lived credentials.
- **Input sanitization a path isolation** — user values nesmú viesť k command, template, path alebo repository injection.
- **Secret-safe execution** — values sa neprenášajú do generated source, logs, outputs alebo catalog metadata bez explicitného secret contractu.
- **Output policy a read-back** — po mutation sa overí exact repository, permissions, resource identity a effective controls.
- **Audit a provenance** — operation spája requester, path generation, inputs, actions, outputs a result bez ukladania citlivého plaintextu.
- **Revocation a repair channel** — platforma vie identifikovať consumers kompromitovanej generation a aplikovať bounded remediation.

## 15. Observability a path health

Golden path health sa nesmie merať iba dostupnosťou portal page alebo success rate scaffolder tasku. Potrebný je journey funnel a generation-aware runtime evidence.

Observation points:

| Vrstva | Identity | Čo dokazuje | Typické zlyhanie |
|---|---|---|---|
| Discovery | path/version, user segment | používateľ našiel relevantnú cestu | path nie je discoverable alebo eligibility je nejasná |
| Request | operation ID, inputs digest | request bol validovaný a prijatý | duplicate alebo neautorizovaný request |
| Scaffolding | task/step/action generation | bootstrap actions vykonali expected mutations | timeout, partial output alebo secret leak |
| Authoritative outputs | repo/resource/catalog IDs | required graph existuje | chýbajúci dependency alebo wrong owner |
| Runtime | release/config/identity generations | workload používa intended contract | stale alebo detached generation |
| Journey | cohort, timestamps, interventions | používateľ dosiahol usable a production outcome | waiting, manual ticket alebo abandonment |
| Lifecycle | current/target path generation | service zostáva podporovaný a upgradeable | fork, stale module alebo blocked migration |

Path dashboard má ukazovať failures podľa step a root cause, no musí zachovať trace od user requestu po business outcome. Agregovaný green status bez residual partial operations vytvára false trust.

## 16. Connected incident `GITOPS-PAY-63`

`Regulated Service v4` bol prezentovaný ako golden path pre všetky nové payment services. Backstage template vytvoril source repository, reusable CI include, environment repository, catalog entity, namespace, database request, workload identity, dashboard a runbook.

Skutočný implementation model bol kombináciou copied a mutable inputs:

```text
Backstage template tag:          regulated-service-v4
custom actions image:            latest
Terraform module reference:      main
reusable pipeline include:       v4
runtime chart:                   ^4.0
policy bundle:                   cluster default
private-network capability:      manual ticket
upgrade channel:                 none
```

Path teda neidentifikoval reprodukovateľnú generation. Generated repositories obsahovali skopírované Terraform a pipeline fragments, ktoré sa po prvom commite odpojili od central changes. Teams upravovali generated internals, pretože extension points nepokrývali private provider connectivity, stateful migrations ani custom incident controls.

Pre request `LP-8841` template task úspešne vytvoril repository a otvoril infrastructure PR. Database request zostal waiting na quota a private endpoint nebol súčasťou pathu. Tím musel vytvoriť tri manual tickets a fork pipeline. Portal napriek tomu ukázal path ako complete a service ako „on golden path v4“.

Po šiestich týždňoch platform inventory ukázal:

```text
services vytvorené v4 template-om:       64
services na reprodukovateľnej v4 graph:   0
repositories s local template changes:   41
services s detached pipeline copy:       19
services vyžadujúce manual network step: 28
services so známou current path version: 17
services schopné automated upgrade diff:  0
```

### Golden-path root cause

Organizácia zamenila scaffolding template za managed end-to-end path. Path nemal immutable dependency graph, explicitné decisions, podporované extension points, upgrade channel ani escape state. Mandate zmenil chýbajúce capabilities na lokálne forks a tickety, ale catalog ich stále zobrazoval ako compliant v4 services.

### Redesign

`Regulated Service 4.1` je definovaný ako versioned capability contract:

```text
path contract digest RSP-4.1
→ pinned scaffolder actions a module versions
→ application-owned skeleton oddelený od managed components
→ provider-connectivity extension ako first-class option
→ preflight quota a eligibility
→ durable operation ID
→ generated output inventory a provenance
→ first production reconciliation canary
→ central upgrade advisory + per-service diff
→ supported extension/exception/detach states
→ second change a incident drill
```

Existujúce forks sa najprv klasifikujú. Compatible customizations sa presunú do extension points, opakované potreby do product backlogu a vedomé departures do detached ownership state-u. Catalog label sa odvádza z verified effective contractu, nie z historického template použitia.

## 17. Golden-path acceptance verdict

Acceptance verdict musí dokázať, že cesta je end-to-end supported, reprodukovateľná, bezpečne rozšíriteľná a udržateľná po prvom vytvorení. Samotný počet generated repositories alebo template task success nie je dostatočný.

Golden path a paved-road design je prijatý, keď:

- **Path má explicitný segment a job** — používateľ vie, pre ktorý workload a journey je cesta určená a kedy má zvoliť inú.
- **Exact generation je reprodukovateľná** — template, actions, modules, charts, policies a images sú resolved na immutable alebo policy-bounded coordinates.
- **Decision architecture je zrozumiteľná** — fixed invariants, defaults, explicit choices, derived values a unsupported combinations majú vysvetlené consequences.
- **Cesta pokrýva lifecycle** — create, change, operate, recover, upgrade, transfer a decommission majú supported mechanismus.
- **Managed a application-owned fields sú oddelené** — platform update neprepisuje business code a local change nevytvára hidden contract drift.
- **Extension a escape sú explicitné** — supported extension, exception, alternative path a detached ownership majú authority, evidence a support consequence.
- **Scaffolding používa durable operation semantics** — retry, partial a unknown outcomes sa riešia read-backom a idempotency, nie blind restartom.
- **Security supply chain je chránený** — executable actions a dependencies sú trusted, pinned, least-privilege a auditovateľné.
- **Testing pokrýva composition a upgrades** — representative inputs, negative cases, second-user, second-change, failure a migration tests prejdú.
- **Path status odráža effective state** — catalog alebo portal nezobrazuje service ako managed/compliant iba preto, že historicky použil template.
- **Upgrade a repair channel existuje** — consumer inventory, diff, rollout, rollback a residual closure sú funkčné.
- **Adopcia znižuje end-to-end friction** — time-to-usable, manual interventions, support, forks a business outcome potvrdzujú hodnotu.

## 18. Troubleshooting flow

Diagnostika začína otázkou, či zlyhalo objavenie cesty, jej contract resolution, execution, output graph, runtime alebo lifecycle. Template log je iba lokálny dôkaz.

```text
Golden path je pomalý, neúplný, diverguje alebo vytvára forks
→ exact path version, user segment a job
→ resolved template/actions/modules/policies
→ request inputs a durable operation ID
→ per-step mutations a authoritative output inventory
→ field ownership a effective runtime contract
→ manual steps, extensions, exceptions a detached changes
→ first-use a first-production journey
→ current consumer version a upgrade eligibility
→ competing hypothesis: missing capability, UX friction, reliability alebo wrong segment
→ bounded path change alebo consumer remediation
→ second-user, second-change a upgrade verification
```

Ak veľa tímov upravuje rovnaký generated file, nejde automaticky o „neposlušných používateľov“. Evidence môže ukazovať chýbajúci extension point alebo nesprávny invariant. Ak každý fork rieši iný business constraint, rozšírenie global pathu môže naopak zvýšiť complexity bez dostatočného reachu.

## 19. Anti-patterny

### Template je golden path

Template je iba jeden artifact v journey. Bez runtime, support, upgrade, exception a decommission contractu vytvára bootstrap, nie paved road.

### Golden path musí byť jediná cesta

Jedna cesta môže pokryť common segment, no odlišné workload contracts potrebujú alternative paths alebo explicitné detached ownership. Násilné zjednotenie vytvorí cage a shadow implementations.

### Abstraction má skryť všetky platform detaily

Používateľ nemusí ovládať provider internals, ale potrebuje resource identity, state, ownership a diagnostický evidence path. Úplné skrytie detailov znižuje schopnosť recovery a dôveru.

### Update-neme template a všetci sú opravení

Copied repositories sa automaticky nezmenia. Oprava vyžaduje consumer inventory, compatibility diff, rollout a verification alebo managed component, ktorý má vlastný versioned update channel.

### Escape hatch oslabuje štandardizáciu

Neauditovaný bypass ju oslabuje. Explicitný extension, exception alebo detach contract naopak udržiava visibility a umožňuje rozhodnúť, ktoré potreby patria do product roadmaps.

## 20. Kontrolné otázky

1. Čím sa golden path líši od paved road, template-u a guardrailu?
2. Prečo exact path subject musí zahŕňať dependencies a output inventory?
3. Ako decision architecture odlíši invariant, default, explicit choice a extension point?
4. Kedy abstraction znižuje cognitive load a kedy už skrýva potrebný kontext?
5. Aký je rozdiel medzi bootstrap copy a managed componentom?
6. Prečo Backstage scaffolder task nemusí byť durable platform operation?
7. Aké typy escape alebo deviation modelu má paved road podporovať?
8. Ako sa testuje second-change a upgrade behavior golden pathu?
9. Prečo je template supply chain vysoko citlivá trust boundary?
10. Čo spôsobilo, že všetkých 64 services v `GITOPS-PAY-63` nemalo reprodukovateľný path graph?
11. Ako sa má catalog status odvodiť z effective managed contractu?
12. Čo musí obsahovať golden-path acceptance verdict?

## Glossary impact

Relevantné pojmy: golden-path subject, paved-road contract, golden cage, path decision architecture, progressive disclosure, bootstrap template, managed path component, path composition graph, supported extension, time-bounded path exception, detached path ownership, path contribution flow, path upgrade channel, path generation compliance, golden-path acceptance verdict.

## Primárne zdroje

- [CNCF TAG App Delivery — Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/)
- [CNCF TAG App Delivery — Platform Engineering Maturity Model](https://tag-app-delivery.cncf.io/wgs/platforms/maturity-model/readme/)
- [Backstage — Software Templates](https://backstage.io/docs/features/software-templates/)
- [Backstage — Writing Templates](https://backstage.io/docs/features/software-templates/writing-templates/)
- [Backstage — Authorizing Scaffolder Tasks, Parameters, Steps and Actions](https://backstage.io/docs/features/software-templates/authorizing-scaffolder-template-details/)
- [Backstage — Software Catalog](https://backstage.io/docs/features/software-catalog/)
- [Backstage — Creating the Catalog Graph](https://backstage.io/docs/features/software-catalog/creating-the-catalog-graph/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Platform as a Product](platform-as-a-product.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Self-service →](self-service.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
