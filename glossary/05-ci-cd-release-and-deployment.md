# CI/CD release and deployment glossary entries

## Artifact version

Logical identifier artifactu používaný na komunikáciu release identity alebo compatibility významu. Má byť mapovateľný na konkrétny immutable content digest. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Blue-green deployment

Deployment stratégia s dvoma oddelenými produkčne relevantnými targetmi, kde sa nová verzia pripraví v neaktívnej farbe a následne sa na ňu riadene presmeruje traffic. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Build metadata — SemVer

Informácie za znakom `+` v Semantic Versioning verzii, napríklad build number alebo commit SHA. Neovplyvňujú SemVer version precedence. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Calendar versioning

Versioning schéma odvodená primárne z kalendárneho dátumu alebo release cadence, napríklad `2026.07.21`. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Changelog

Dlhodobý chronologický záznam významných zmien produktu alebo komponentu naprieč releases. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Code freeze

Časovo alebo rozsahovo obmedzená policy, ktorá pred release povoľuje iba vybrané zmeny. Nemá nahrádzať automatizované kontroly, malé batches a recovery schopnosť. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Color-specific telemetry

Metrics, logs a traces označené blue/green environmentom a artifact verziou tak, aby bolo možné analyzovať cutover a porovnať správanie oboch farieb. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Compatibility dimension

Jedna z vrstiev, v ktorých sa hodnotí backward compatibility, napríklad source, binary, schema, behavior, operational, security, data alebo performance contract. Version bump musí vychádzať z affected dimensions a consumer evidence, nie iba zo syntaktického diffu. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Content digest

Content-derived immutable identifikátor konkrétnych bytes artifactu, typicky kryptografický hash. Na rozdiel od logical version alebo mutable tagu presne určuje nasadený obsah. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Cutover transaction

CAS-chránený a auditovaný prechod autoritatívneho routingu zo starej deployment farby na novú, viazaný na očakávanú routing revision, immutable release subject a idempotentné failure semantics. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Cutover window

Časový interval, v ktorom sa traffic alebo ownership práce presúva zo starej deployment farby na novú a intenzívne sa sledujú promotion a abort signály. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Deployment downtime

Čas, počas ktorého deployment spôsobí úplnú alebo neprijateľnú nedostupnosť služby. Pri recreate zahŕňa shutdown, deployment, startup, migrations, readiness a routing. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## Environment parity — deployment

Miera, do akej blue a green alebo iné deployment targety zachovávajú rovnaké produkčne relevantné konfigurácie, topológiu, permissions, limits a dependencies. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Exclusive runtime slot

Recreate deployment model, v ktorom môže konkrétny service alebo writer ownership v jednom okamihu patriť iba starej generácii, prázdnemu maintenance stavu alebo novej generácii. Odstraňuje mixed-version overlap za cenu capacity gapu. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## Functional readiness

Dôkaz, že instance alebo nová generácia dokáže bezpečne vykonať kritický service outcome vrátane relevantnej identity, dependency, read/write a idempotency cesty. Je prísnejšia než process start, liveness alebo otvorený port. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md) a [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Hypercare

Dočasne zvýšená prevádzková a support pozornosť po významnom release, vrátane posilneného monitoringu, owner dostupnosti a rýchleho rozhodovacieho pathu. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Immutable tag

Registry alebo repository tag, ktorého mapping na artifact content sa po publikovaní nesmie zmeniť. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Logical version

Ľudsky alebo procesne významná verzia, napríklad `2.8.1`, ktorá komunikuje release alebo compatibility význam, ale sama nemusí identifikovať konkrétne bytes bez väzby na digest. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## MAJOR version

Prvá časť SemVer verzie, ktorá sa zvyšuje pri nekompatibilnej zmene deklarovaného public API alebo compatibility contractu. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Maintenance mode

Kontrolovaný runtime režim používaný počas deploymentu na blokovanie alebo obmedzenie operácií, prípadne na poskytovanie informačnej response používateľom. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## Maintenance window

Vopred definovaný časový interval, počas ktorého je povolená plánovaná údržba alebo akceptovaný znížený service level. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## Maximum surge

Limit dočasnej capacity nad desired replica count, ktorú môže rolling update vytvoriť na zachovanie dostupnosti a zrýchlenie rollout-u. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Maximum unavailable

Limit počtu alebo percenta desired instances, ktoré môžu byť počas rolling update nedostupné. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## MINOR version

Druhá časť SemVer verzie, ktorá sa zvyšuje pri backward-compatible pridaní capability do deklarovaného public API. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Mixed-version compatibility

Schopnosť starej a novej application generácie bezpečne koexistovať nad spoločným trafficom a mutable state-om vrátane database, events, queues, cache, sessions, workers a client contractov. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Mixed-version deployment

Obdobie rollout-u, počas ktorého stará a nová application verzia súčasne obsluhujú traffic alebo pracujú nad spoločným stavom. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Mutable tag

Registry alebo repository tag, ktorého mapping možno prepísať na iný artifact content, napríklad `latest`. Nie je spoľahlivou deployment identity bez zachovaného digestu. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## PATCH version

Tretia časť SemVer verzie, ktorá sa zvyšuje pri backward-compatible oprave deklarovaného behavioru. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Pre-release identifier

SemVer časť za pomlčkou, napríklad `rc.1`, označujúca verziu s nižšou precedence než zodpovedajúci final release. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Provenance attestation

Strojovo overiteľné tvrdenie o pôvode artifactu, jeho source, build procese, vstupoch a builder identity. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Public API — versioning

Deklarovaná compatibility boundary zahŕňajúca nielen programové interfaces, ale podľa produktu aj konfiguráciu, CLI, schemas, events, file formats a operational behavior. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Recreate deployment

Deployment stratégia, ktorá ukončí starú version fleet pred spustením a pripravenosťou novej, čo typicky vytvára downtime alebo výrazný capacity dip. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## Recovery eligibility

Aktuálny dôkaz, že konkrétny predchádzajúci release možno bezpečne použiť na rollback alebo inú recovery: artifacts sú dostupné a dôveryhodné, config a secrets existujú, shared data a events zostávajú kompatibilné a post-recovery validation je pripravená. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md) a [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release branch

Branch určená na stabilizáciu a podporu konkrétnej release line, často s backportmi a explicitným lifecycle. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release candidate

Immutable artifact považovaný za potenciálny final release, ktorý musí byť testovaný a promotionovaný bez rebuildu pod rovnakou release identity. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release cadence

Pravidlo určujúce frekvenciu a časovanie releases, napríklad on-demand, fixed schedule, release train alebo continuous release. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release management

Disciplína riadenia release identity, readiness, approvals, communication, rollout, recovery a support lifecycle od pripraveného artifactu po používateľsky dostupnú zmenu. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release manifest

Versionovaný dokument mapujúci koordinovaný release na immutable digests komponentov a relevantné configuration, infrastructure a schema revisions. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release notes

Kurátorovaná komunikácia konkrétneho release pre používateľov, administrátorov, integrátorov alebo support, zahŕňajúca dopad, breaking changes, migráciu a known issues. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release record

Auditovateľný záznam spájajúci release version, artifacts, source, config, migrations, evidence, approvals, rollout a výsledok. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release state machine

Auditovateľný lifecycle immutable release unit od draftu a candidate assembly cez evidence, eligibility, deployment, exposure a validation po support, closure, deprecation, revocation alebo end of life. Každý transition má subject, preconditions, evidence a ownera. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release train

Cadence model, v ktorom zmeny pripravené do definovaného cutoffu vstúpia do spoločného release termínu a ostatné čakajú na ďalší vlak. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release unit

Presne definovaná množina artifactov, configov, migrations alebo koordinovaných komponentov, ktoré sa schvaľujú a release-ujú ako jeden celok. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Rolling rollback

Postupné nahrádzanie chybnej novej version fleet predchádzajúcim artifactom pri zachovaní rolling update mechanizmu a jeho compatibility obmedzení. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Rolling update

Deployment stratégia postupne nahrádzajúca staré instances novými pri zachovaní časti dostupnej capacity a dočasnej koexistencii versions. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Routing rollback

Recovery operácia, ktorá po neúspešnom blue-green cutover-e presmeruje traffic späť na pôvodnú farbu. Nevracia automaticky data state. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Runtime identity — release

Effective runtime subject tvorený release manifestom spolu s rendered configuration, secret references, infrastructure a IAM revision, database/event stavom, feature flags, traffic exposure a target environmentom. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Semantic Versioning

Versioning kontrakt vo formáte `MAJOR.MINOR.PATCH`, ktorý komunikuje význam zmien voči deklarovanému public API. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Supersession — release

Explicitný prechod, pri ktorom nový immutable candidate nahradí starší candidate. Supersession record zachová delta scope a určí, ktoré evidence, approvals a rollout rozhodnutia zostávajú platné a ktoré sa invalidujú. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Supported version policy

Pravidlá určujúce, ktoré release lines dostávajú opravy, security updates a podporu a kedy dosiahnu end of life. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Traffic cutover

Riadené presmerovanie nových requestov alebo connections zo starej deployment farby na novú. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Version precedence

SemVer pravidlá určujúce poradie versions podľa MAJOR, MINOR, PATCH a pre-release identifiers; build metadata sa pri precedence ignorujú. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Version range

Constraint vyjadrujúci množinu akceptovaných dependency versions, ktorého konkrétna syntax a význam závisia od package ecosystemu. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Version-level telemetry

Metrics, logs a traces označené konkrétnou application alebo artifact verziou, ktoré umožňujú porovnať old a new behavior počas rollout-u. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Warm standby — blue-green

Pôvodná deployment farba ponechaná po cutover-e v pripravenom a priebežne health-checkovanom stave pre rýchly routing rollback. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Write-once publication

Publication contract, pri ktorom už vydaná logical version alebo candidate identity nemožno prepísať iným digestom. Collision s odlišným contentom je hard failure a unknown outcome sa rieši reconciliation podľa idempotency key. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).