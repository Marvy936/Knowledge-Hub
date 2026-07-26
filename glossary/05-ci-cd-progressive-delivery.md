# Progressive delivery, experiments and recovery glossary entries

## A/B testing

Riadený experiment porovnávajúci control a treatment variant na súbežných skupinách používateľov podľa vopred definovaných outcome a guardrail metrík. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Assignment–exposure funnel

Observation chain od eligible population a variant assignmentu cez application/runtime survival po reálnu treatment exposure a následný outcome. Používa sa na lokalizáciu Sample Ratio Mismatch, treatment-specific crashu, logging lossu alebo selection biasu. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Automated canary analysis

Automatizované vyhodnotenie canary verzie voči baseline podľa technických a business metrík, sample size, observation window a promotion/abort policy. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Backfill

Riadené doplnenie alebo transformácia existujúcich dát, typicky v bounded batches s checkpointingom, rate limitom, validáciou a možnosťou pause/resume. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Canary cohort

Stabilná skupina requestov, používateľov, tenantov alebo instances vystavená novej verzii pred širšou promotion. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Canary deployment

Deployment stratégia postupne zvyšujúca produkčnú exposure novej verzie pri súbežnom porovnávaní so stable baseline a explicitných promotion/abort kritériách. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Canary experiment subject

Presná identity jedného canary decisionu tvorená stable a canary release manifestom, rendered configom, feature-flag revision, cohort policy a saltom, rollout krokom, metrics query revision, analysis policy a observation window. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Cohort assignment

Deterministické priradenie subjektu do rollout alebo experiment skupiny pomocou stabilnej identity a versionovaného pravidla. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md) a [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Compatibility matrix — deployment

Explicitná tabuľka určujúca, ktoré application, client, event a schema verzie môžu bezpečne koexistovať počas rollout-u a rollback window. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Contract proof — database

Strojovo aj manuálne overiteľná evidence, že starý databázový contract už nepoužíva žiadny aktívny reader, writer ani downstream consumer, migrácia a reconciliation sú dokončené a odstránenie old representation má pripravenú forward-repair alebo restore cestu. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Control variant

Referenčný variant experimentu reprezentujúci existujúce alebo baseline správanie, voči ktorému sa hodnotí treatment. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Dark launch

Nasadenie novej capability bez jej autoritatívneho sprístupnenia používateľovi, často s traffic mirroringom alebo skrytým runtime pathom. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).

## Deployment ring

Stabilná rollout skupina používateľov, tenantov, zariadení alebo regiónov s definovaným risk profilom, membershipom a promotion contractom. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Dual write

Dočasný migration model, v ktorom application zapisuje rovnakú logickú zmenu do starej aj novej reprezentácie alebo store. Vyžaduje idempotency, authoritative source a reconciliation. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Effective flag state

Flag revision, variant, matched rule, evaluation context, SDK/cache state a application version, ktoré konkrétny runtime evaluator skutočne použil. Môže sa líšiť od poslednej hodnoty zobrazenej v control plane počas propagation alebo rejection failure. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Expand-contract

Viacfázový model databázovej alebo contract zmeny: najprv sa pridá kompatibilná nová štruktúra, migrujú readers/writers a dáta, a až po rollback window sa odstráni stará štruktúra. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Experiment integrity

Platnosť assignment, exposure, measurement a population boundaries potrebná pred interpretáciou experimentálneho effect estimate-u. Porušenie môže zmeniť experiment na invalidný aj pri priaznivom primary outcome. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Experiment unit

Entita randomizovaná do variantu experimentu, napríklad používateľ, tenant, device, session alebo región. Musí zodpovedať hranici možného treatment efektu. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Exposure event

Telemetry udalosť dokazujúca, že subjekt reálne dostal konkrétny experiment alebo feature variant; assignment bez exposure nemusí znamenať ovplyvnenie. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Feature flag

Runtime control oddeľujúci deployment kódu od sprístupnenia capability pomocou versionovaného evaluation pravidla. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Flag debt

Kumulovaná komplexita starých feature flags, paralelných code paths, kombinácií stavov, testov a prevádzkových rozhodnutí po prekročení plánovaného lifecycle. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Flag evaluation

Runtime rozhodnutie o variante alebo hodnote feature flagu na základe flag verzie, identity, environmentu a targeting pravidiel. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Forward-fix migration

Nová databázová migration opravujúca chybný alebo neúplný aktuálny stav bez pokusu mechanicky vrátiť predchádzajúcu schema. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Last compatible state

Najnovší presne identifikovaný runtime subject, ktorý je technicky, dátovo, eventovo, klientsky a bezpečnostne kompatibilný s aktuálnym distributed state-om a možno ho použiť ako recovery target. Nemusí byť totožný s bezprostredne predchádzajúcim release-om. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Last known good

Presne identifikovaný artifact, configuration a compatibility stav s overenou produkčnou evidence, ktorý možno použiť ako recovery target. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Minimum detectable effect

Najmenšia zmena outcome metriky, ktorú má experiment pri zvolenej sample size a power spoľahlivo detegovať. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Mirror delivery contract

Versionované pravidlá určujúce shadow mirror point, sample inventory, delivery semantics, queue/drop/lag limity, duplicate a ordering behavior a primary-path isolation. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).

## Online schema change

Databázová schema operácia navrhnutá tak, aby minimalizovala blocking a downtime počas aktívnej prevádzky; jej skutočné správanie závisí od engine, verzie a dátového objemu. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Paired shadow evidence

Korelovaný primary a shadow execution record viazaný na rovnaký mirror event, input/state identity, artifact/config revisions, lag a normalization policy. Missing alebo neporovnateľný pair sa nesmie klasifikovať ako úspešná zhoda. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).

## Progressive delivery

Evidence-driven riadenie postupnej produkčnej exposure pomocou rollout stratégie, segmentácie, observability, promotion policy a recovery mechanizmov. Pozri [Progressive delivery](docs/05-ci-cd-and-release/progressive-delivery.md).

## Read compatibility

Schopnosť starej aj novej application verzie správne interpretovať dáta v aktuálnom schema a semantic stave. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Reconciliation

Proces porovnania a opravy rozdielov medzi dvoma reprezentáciami alebo stores, napríklad počas dual write migration. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Recovery package

Predpripravený súbor identity, kompatibility informácií, workflows a rozhodovacích podkladov potrebných na rollback, roll-forward alebo restore konkrétneho release. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Release inventory — ring

Auditovateľné mapovanie ring ID a membership revision na member/workload inventory, release manifest, rendered config, exposure state, observation verdict, support ownership a recovery eligibility. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Ring deployment

Progressive rollout cez stabilné deployment rings s rastúcou reprezentatívnosťou alebo kritickosťou a samostatnými entry, observation a promotion podmienkami. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Ring membership revision

Versionovaná production policy určujúca, do ktorého deployment ring-u patrí konkrétny subject. Musí byť konzistentná naprieč services, events, telemetry a support inventory. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Roll-forward

Recovery stratégia nasadzujúca nový opravný artifact alebo migration namiesto návratu na starú verziu, často pre nekompatibilný alebo už zmenený shared state. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Rollback — deployment

Recovery stratégia obnovujúca predchádzajúci kompatibilný artifact, konfiguráciu, traffic target alebo infraštruktúrny state. Neznamená automaticky návrat dát a external side effects. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Rollback window

Obdobie, počas ktorého sa zámerne zachováva schema, configuration, artifact a operational kompatibilita potrebná na bezpečný návrat na predchádzajúcu verziu. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Rollout contract

Versionovaný popis artifactu, configu, targetu, cohort, krokov, metrics, observation windows, promotion/abort policy, recovery actions a ownera progressive rollout-u. Pozri [Progressive delivery](docs/05-ci-cd-and-release/progressive-delivery.md).

## Rollout reconciliation loop

Controller lifecycle `observe actual multi-axis state → classify divergence → validate preconditions → apply jeden bounded transition → over effective state → vyhodnoť evidence → reconcile znovu`. Chráni pred predpokladom, že control-plane command automaticky vytvoril desired data-plane state. Pozri [Progressive delivery](docs/05-ci-cd-and-release/progressive-delivery.md).

## Sample ratio mismatch

Významný rozdiel medzi plánovaným a reálnym pomerom experimentálnych variantov, ktorý môže signalizovať assignment, exposure, crash, logging alebo eligibility problém. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Sample sufficiency — canary

Stav, keď canary krok nazbieral dostatočný počet relevantných requests, sessions alebo business outcomes, potrebné segmentové zastúpenie a observation čas primeraný failure latency. Percento trafficu samo tento stav nedokazuje. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Schema compatibility

Schopnosť aktívnych application a data consumers fungovať s aktuálnou sadou tables, columns, constraints, types a indexov počas deploymentu. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Semantic compatibility — data

Zachovanie rovnakého alebo explicitne transformovaného business významu hodnôt naprieč application a schema verziami. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Shadow deployment

Deployment, ktorý spracúva kópiu produkčného workloadu bez autoritatívnej response a s blokovanými alebo izolovanými side effects. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).

## Shadow read

Neautoritatívne čítanie z novej schema alebo store vykonané popri primárnom čítaní na porovnanie výsledkov pred prepnutím. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Side-effect firewall — shadow

Defense-in-depth boundary kombinujúca least-privilege identity, network/egress policy, isolated output adapters a application shadow mode tak, aby shadow execution nemohla vykonať autoritatívne writes alebo external side effects. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).

## Stable bucketing

Deterministické mapovanie subjektov do percentuálnych rollout alebo experiment buckets tak, aby sa variant nemenil náhodne medzi requestmi. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## State-delta inventory

Per-layer záznam toho, čo release zmenil v artifacte, confige, routingu, infrastructure, databáze, events, cache, external side effects a clients, spolu s current effective state-om a reversibility. Je vstupom pre recovery eligibility a voľbu rollbacku, roll-forwardu, compensation alebo restore. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Traffic mirroring

Kopírovanie produkčných requestov do shadow systému bez použitia jeho response na primary request path. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).

## Treatment variant

Experimentálny variant obsahujúci testovanú zmenu, ktorého outcome sa porovnáva s control variantom. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Version skew — ring

Obdobie, počas ktorého rôzne deployment rings používajú odlišné release alebo client verzie nad spoločnými APIs a mutable state-om. Potrebuje maximálny podporovaný rozsah, compatibility contract a deadline. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Write compatibility

Schopnosť každej súčasne aktívnej application verzie zapisovať dáta, ktoré ostatné aktívne verzie bezpečne prečítajú a interpretujú. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).