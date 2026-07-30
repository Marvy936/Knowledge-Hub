# Service catalog

Service catalog je riadený model softvérového a platformového ekosystému, ktorý spája identitu entity, vlastníctvo, lifecycle, rozhrania, závislosti, runtime koreláciu a prevádzkový kontext. Nie je to iba vyhľadávacia stránka nad zoznamom repozitárov. Ak má byť použitý pre self-service, incident routing, policy scoping alebo decommission, musí presne rozlišovať authoritative metadata, odvodenú catalog projection a aktuálny effective runtime stav.

Najnebezpečnejší catalog nie je prázdny catalog. Je to presvedčivý catalog so stale ownerom, neplatným tenant scope-om alebo lifecycle hodnotou, ktorú ďalšia automatizácia nesprávne považuje za autoritatívnu. Preto sa kvalita catalogu neposudzuje podľa počtu zaregistrovaných entít ani podľa toho, či sa otvorí detail služby. Posudzuje sa podľa toho, či konkrétna entity generation korektne reprezentuje dohodnuté authority contracts a či downstream rozhodnutie vie odhaliť neúplnosť, staleness a konflikt.

## 1. Dominantný model

Catalog lifecycle začína identitou opisovaného objektu, nie YAML súborom. Jedna služba môže mať source repository, release artifacty, deploymenty, API, databázy, on-call rota a business capability. Catalog musí vedieť, ktoré z týchto objektov sú samostatné entity, ktoré sú iba relations a ktoré informácie pochádzajú z externého observovaného systému.

Spracovanie zároveň nie je jednorazový import. Entity provider alebo registrovaná location dodá raw entity, policies a processors ju validujú a obohatia, stitching vytvorí výslednú projection a API ju sprístupní používateľom a pluginom. Downstream consumer potrebuje vedieť, ku ktorej source a processing generation sa projection vzťahuje. V opačnom prípade „entity existuje“ zamení za „critical metadata je aktuálne a dôveryhodné“.

```text
real software, platform alebo organizational object
→ stable entity identity a authority map per field
→ source descriptor alebo provider snapshot
→ ingestion s source generation a observation time
→ schema, policy a semantic processing
→ emitted relations, statuses a derived metadata
→ stitched catalog entity generation
→ discoverability a downstream consumption
→ correlation s Git, runtime, ownership a operational systems
→ freshness, conflict a orphan evaluation
→ lifecycle transition, migration alebo removal
→ second-source a second-change validation
```

Catalog acceptance preto koreluje entity reference, source revision alebo provider generation, processor/policy generation, stitched result, relation graph, freshness budget a downstream outcome. Detail stránky, ktorý sa úspešne vykreslí zo starej poslednej validnej entity, nie je dôkazom aktuálnosti.

## 2. Inventory, registry, CMDB a service catalog

Tieto pojmy sa prekrývajú, ale ich decision contract je odlišný. Inventory odpovedá predovšetkým na otázku, čo bolo objavené alebo evidované. Registry poskytuje riadený zápis a lookup určitého typu objektu. CMDB tradične modeluje configuration items, ich attributes a relations pre change a operations procesy. Service catalog sa sústreďuje na softvér, capabilities, owners, lifecycle a používateľské cesty.

Rozdiel nie je v názve produktu. Rovnaký backend môže plniť viac úloh, pokiaľ jasne označuje authority a freshness každého poľa. Problém vzniká, keď catalog UI zjednotí údaje z Git-u, cloudu, identity systému a runtime telemetry bez toho, aby consumer vedel, čo je deklarácia, čo discovery a čo historický snapshot.

```text
inventory
→ observed alebo evidovaný set objektov

registry
→ authoritative lookup a registration contract pre konkrétny typ

CMDB
→ configuration-item model pre change, dependency a operational management

service catalog
→ software/platform entity graph pre ownership, discovery, lifecycle a developer operations
```

Catalog môže používať inventory ako vstup a CMDB relation ako enrichment. Nemal by však automaticky povýšiť observed cloud tag na authoritative ownera ani repozitárový label na dôkaz, že workload v production používa správny tenant profile.

## 3. Exact catalog-entity subject

Názov `payments-api` nie je dostatočný subject. Môže existovať rovnaký component name v rôznych namespaces, organizáciách, clusteroch alebo catalog instances. Exact subject potrebuje canonical entity reference a generation identity.

Minimálny subject obsahuje `apiVersion`, `kind`, namespace a name. Pre audit a automatizáciu potrebuje navyše source identity, source revision alebo provider cursor, processing generation a observation time. Ak catalog reprezentuje runtime deployment, relation musí niesť exact cluster/environment/resource identity namiesto voľného textu `production`.

```text
catalog subject
= catalog instance
+ apiVersion/kind/namespace/name
+ source authority
+ source revision alebo provider generation
+ processor/policy generation
+ stitched entity generation
+ observation time a freshness class
```

Zmena ownera bez zmeny entity name je nová metadata generation. Presun repozitára, ktorý nechá starú registered location, môže vytvoriť orphan alebo stale projection. Rename komponentu môže byť identity migration, nie obyčajná textová úprava. Catalog musí tieto transitions modelovať, inak vzniknú duplicate entity, dangling relations alebo policy rozhodnutia nad bývalou identitou.

## 4. Entity model a hranice abstrakcie

Praktický software catalog potrebuje malý, stabilný core model a kontrolované extensions. Backstage modeluje najmä Components, APIs a Resources a používa ďalšie entity ako Systems, Domains, Groups, Users, Locations a Templates. Ich význam však nevzniká iba z `kind`; vzniká z organizačnej taxonómie a relation contracts.

Component má reprezentovať samostatne vlastnený software unit, nie každý Kubernetes Deployment alebo každý repozitár. API je kontrakt alebo boundary, nie len URL. Resource je infraštruktúrna alebo dátová závislosť, ale nemusí byť catalogom autoritatívne provisionovaná. System zoskupuje components a resources do vyššieho funkčného celku; Domain spája systems s business oblasťou.

Príliš jemný model vytvorí tisíce entít bez vlastníctva a vysoký maintenance cost. Príliš hrubý model skryje runtime a dependency boundaries. Rozhodnutie sa preto viaže na jobs-to-be-done: incident routing môže potrebovať workload-to-service correlation, API governance potrebuje producer/consumer graph a decommission potrebuje resource dependencies a data-retention ownera.

## 5. Authority map per field

Catalog entity nie je automaticky authority pre všetky svoje fields. `spec.owner` môže byť riadený v repozitári, on-call rota v incident-management systéme, runtime version v deployment inventory a data classification v governance registry. Catalog je hub, ktorý tieto values sprístupní, ale musí zachovať provenance.

Authority map určuje pre každé kritické pole writera, source identity, update mechanismus, validation a conflict policy. Bez nej môžu Git descriptor, org provider a manual UI edit súčasne tvrdiť iného ownera. Last-write-wins potom nie je reconciliation; je to náhodná strata významu.

| Field alebo relation | Typická authority | Catalog rola | Zakázaná skratka |
|---|---|---|---|
| Entity identity a source repo | versionovaný descriptor alebo repository registry | ingest a projection | odvodiť identity iba z repository name |
| Team ownership | org/ownership authority alebo reviewed descriptor | resolve relation a zobraziť provenance | manual free-text owner bez resolvable entity |
| Lifecycle | service owner s governance contractom | validation, search a workflow trigger | automaticky označiť production podľa existencie Deploymentu |
| Runtime deployment | cluster/deployment inventory | observed relation a freshness | považovať catalog annotation za live-state proof |
| Data classification | governance authority | policy input iba s generation/freshness gate-om | odvodiť z názvu namespace |
| On-call rota | incident-management authority | operational projection | kopírovať rota string bez expiry |
| Tenant boundary | tenant registry/platform contract | lifecycle a isolation input | použiť stale catalog projection ako jediný admission oracle |

Critical automation má čítať iba fields, ktorých authority, freshness a error semantics pozná. Catalog môže byť discovery interface pre mnoho údajov, ale privilege alebo tenant decision nesmie závisieť od neoznačeného enrichmentu.

## 6. Descriptor, provider a ingestion

Descriptor uložený pri kóde je vhodný pre metadata, ktoré vlastní software tím a ktoré majú prechádzať reviewom spolu so zmenou služby. Entity provider je vhodný pre systematický import z autoritatívneho externého systému, napríklad identity directory, cloud inventory alebo organization registry. Manual registration je bootstrap mechanismus, nie automaticky dlhodobý ownership model.

Pri ingestion treba zachovať source coordinate. Pre Git descriptor to zahŕňa repository, path a resolved revision. Pre provider snapshot to môže byť tenant, provider generation, cursor alebo observed-at timestamp. Ak entity vznikne z mutable branch bez uloženia resolved revision, neskoršie vyšetrovanie nevie reprodukovať raw input.

Ingestion error musí mať explicitnú semantics. Backstage processing môže pri chybe ponechať predchádzajúcu bezchybnú final entity, aby krátkodobý source outage nezničil catalog. To je rozumná availability vlastnosť, ale downstream consumer musí vidieť, že aktuálny source sa nespracoval a displayed values sú stale. Availability poslednej dobrej projection nesmie byť interpretovaná ako freshness critical metadata.

## 7. Processing, policies a stitching

Processing pipeline validuje základný tvar entity, aplikuje catalog policies, vykonáva processors, emituje relations a statuses a následne stitchuje výsledok. Processor môže napríklad resolve-núť owner reference, načítať API definition, pridať repository annotations alebo vytvoriť relation `dependsOn`.

Každý extension point rozširuje trust boundary. Processor s broad credentials môže čítať citlivé systémy alebo vložiť do catalogu nesprávne odvodené fields. Plugin, ktorý predpokladá neexistujúcu relation semantics, môže zobraziť falošný dependency graph. Preto treba versionovať processor set, testovať output schema a zaznamenávať processing errors per entity.

Stitching vytvára convenient final view, ale môže zlúčiť data s rôznou freshness. Entity owner z org provideru môže byť aktuálny, runtime deployment relation stará päť minút a security scorecard stará deň. Jedna generická zelená ikonka preto nie je dostatočný verdict. Critical fields potrebujú vlastný status, observation time a stale policy.

## 8. Relations a catalog graph

Relation je directional edge so source entity, relation type a target reference. `ownedBy` nie je to isté ako `ownerOf`; `dependsOn` nie je automaticky runtime traffic; `providesApi` neznamená, že API je v production dostupné. Semantics musí byť explicitná pre autorov aj consumers.

Graph umožňuje blast-radius analysis, ownership navigation a decommission planning. Je však iba taký presný ako source relations a ich freshness. Dangling relation môže byť legitímna počas migration, ale musí byť viditeľná. Cyklus v `dependsOn` môže odhaliť reálnu distributed dependency alebo nesprávne modelovanie. Catalog nemá bez dôkazu inferovať critical runtime path len preto, že dve entity zdieľajú system.

Pri decommission sa graph používa ako hypothesis generator. Pred odstránením API alebo database treba korelovať catalog consumers s runtime telemetry, access logs, data contracts a business owners. Absencia catalog relation nie je dôkazom absencie závislosti.

## 9. Ownership ako operational contract

Owner nie je dekoratívny label. Je to resolvable organizational entity s authority a zodpovednosťou za konkrétny scope. Service owner môže rozhodovať o lifecycle a change-i, platform owner o capability contracte, data owner o retention a incident commander o dočasnom recovery rozhodnutí. Catalog by mal rozlišovať tieto role namiesto jedného nejasného poľa.

Ownership relation musí prežiť reorganizáciu. Väzba na stabilnú Group entity je odolnejšia než free-text team name. Org provider musí riešiť rename, merge a deletion. Keď team zanikne, komponent nemá potichu zostať s ownerom, ktorý sa už nedá resolve-núť. Potrebuje explicitný orphan-owner stav, fallback governance ownera a remediation workflow.

Operational routing musí overiť, že owner relation je aktuálna a že existuje reachable escalation path. Catalog detail so starým ownerom môže predĺžiť incident aj vtedy, keď všetky deploymenty fungujú správne.

## 10. Lifecycle, support tier a deprecation

Lifecycle taxonomy má byť malá, organizáciou definovaná a spojená s povinnými dôsledkami. Hodnota `experimental`, `production` alebo `deprecated` bez support a change semantics je iba kategória. Production môže vyžadovať on-call coverage, SLO, vulnerability remediation, backup, owner a decommission plan. Deprecated môže vyžadovať replacement, consumer inventory a sunset date.

Support tier je iná dimenzia než lifecycle. Interný production batch môže mať business-critical tier, zatiaľ čo verejný experiment môže mať obmedzenú podporu. Data classification a tenant isolation profile sú ďalšie samostatné dimensions. Ich zlepenie do jedného `tier: gold` vytvorí implicitné pravidlá a ťažko testovateľné policy branching.

Lifecycle transition je authoritative decision. Deployment v production nemá automaticky meniť `spec.lifecycle` na production, pretože technická existencia nepreukazuje owner acceptance ani operational readiness. Naopak, catalog deprecation musí viesť k runtime a consumer closure; textová hodnota bez migrácie nič neodstráni.

## 11. Freshness, staleness a completeness

Catalog freshness nie je jedno globálne číslo. Každý source má vlastnú update frequency, outage semantics a tolerated staleness. Owner z identity authority môže mať hodinový budget, runtime digest minútový a compliance attestation denný. Consumer potrebuje vedieť, či jeho decision vyžaduje fresh read alebo môže použiť cache.

Completeness sa meria proti expected inventory, nie proti počtu úspešne spracovaných entít. Ak provider prestane emitovať celý tenant, catalog môže ukazovať 100 % validitu zvyšných entít a pritom stratiť kritický segment. Denominator má pochádzať z repository inventory, cloud accounts, tenant registry alebo iného explicitného authority setu.

Freshness contract obsahuje observation time, successful processing time, source generation, error state a stale action. Pre discovery môže stale owner vyvolať warning. Pre namespace vending alebo privileged exception má staleness viesť k fail-closed alebo human-reviewed recovery, nie k tichému použitiu poslednej hodnoty.

## 12. Catalog ako projection, nie runtime oracle

Catalog môže zobraziť deploymenty, health, alerts a versions, ale tieto údaje sú projections externých systémov. `production: healthy` nemá byť uložená statická annotation v descriptor-e. Má byť computed view s exact cluster, namespace, resource UID, observed generation, workload artifact a observation time.

Rovnako catalog registration nie je deployment. Component môže existovať bez runtime instance, mať viac environment deployments alebo byť retired pri zachovanom historickom zázname. Runtime plugin musí korelovať stable service identity s concrete deployment identity; name-only lookup môže spojiť nesprávny namespace alebo cluster.

Catalog môže poskytovať navigáciu k source of truth a sumarizovať evidence. Acceptance rozhodnutie má zostať pri authoritative control plane alebo explicitnom business oracle. Tým sa zabráni tomu, aby zelená catalog card maskovala stale workload, chýbajúci secret reload alebo cross-tenant configuration.

## 13. Scorecards a standards evidence

Scorecard je súbor questions alebo checks nad catalog entities a externými evidence. Môže ukazovať owner completeness, documentation, SLO, dependency updates, security findings alebo golden-path generation. Nie je však automaticky guardrail. Často je detective a advisory.

Každý check potrebuje exact subject, evidence source, observation time, rule generation a interpretation. `Has runbook` založené na existencii URL nepreukazuje, že runbook je aktuálny alebo vykonateľný. `Uses golden path` podľa template annotation nepreukazuje, že service zostal na managed generation. `Policy compliant` podľa včerajšieho reportu nepreukazuje admission outcome dnešnej zmeny.

Scorecard má podporovať product discovery a remediation prioritization. Ak sa zmení na individuálny ranking tímov alebo povinné skóre bez root-cause kontextu, bude motivovať metadata gaming a skryté exceptions.

## 14. Catalog-driven automation

Catalog-driven automation je bezpečná iba vtedy, keď catalog value nesie authority a freshness contract vhodný pre danú mutation. Nízko-riziková automatizácia môže podľa owner relation poslať reminder. Namespace provisioning, IAM grant alebo tenant isolation profile však potrebuje exact source generation, policy validation a read-back z cieľového systému.

Dôležitý je compare-and-swap model. Request môže byť plánovaný nad entity generation `g41`; ak owner, lifecycle alebo tenant classification prejde na `g42`, starý plan sa musí invalidovať. Bez precondition môže delayed workflow aplikovať privilege podľa bývalého ownera.

```text
catalog-triggered operation
→ exact entity reference a source/stitched generation
→ required-field authority a freshness validation
→ target-specific plan
→ policy a approval nad rovnakým subjectom
→ bounded mutation
→ authoritative target read-back
→ catalog projection refresh
→ effective outcome a second-reconcile verification
```

Catalog sa po mutation aktualizuje ako projection výsledku. Nemá sa označiť za success len preto, že workflow odoslal request. To isté platí pre decommission: removal entity bez revocation credentials, DNS, data a billing je false closure.

## 15. Orphans, duplicates a deletion

Orphan znamená, že entity stratila parent/provider edge alebo registered source, nie automaticky že software neexistuje. Automatické odstránenie orphanov znižuje clutter, ale môže skryť stále bežiaci workload. Retention orphanov zlepšuje forensic visibility, ale bez ownera a expiry vytvára trvalý neporiadok.

Duplicate entities vznikajú pri rename, presune descriptoru, viacnásobnom provider-ingeste alebo rozdielnej normalizácii references. Deduplication podľa name je nebezpečná; dve entity môžu mať rovnaký display name a odlišný scope. Migration potrebuje old-to-new alias, relation rewiring, consumer update a explicitné retirement starej identity.

Delete catalog entity má byť posledná projection transition, nie prvý decommission krok. Pred ňou sa overuje runtime inventory, dependencies, retention, secrets, alerts, repositories, domains a ownership closure. Historický audit môže zostať mimo active catalogu.

## 16. Security a privacy boundary

Catalog agreguje citlivý organizational a operational kontext. Ownership graph, repository locations, vulnerabilities, production dependencies a tenant classifications môžu pomôcť útočníkovi. Access control preto nemá byť automaticky „všetci vidia všetko“ ani plugin credentials nemajú mať broad write authority.

Input processing musí brániť schema abuse, unsafe URL fetch, secret leakage v annotations a processor confusion. Descriptor je untrusted team-controlled input, aj keď leží v internom Git-e. Plugin alebo template nemá vykonávať privileged action iba podľa user-supplied catalog reference bez server-side authorization.

Audit má zachytiť entity reads citlivých fields, registrations, mutations, provider changes, processing errors a downstream privileged decisions. Privacy contract určuje purpose, retention a audience org údajov. Catalog nemá byť skrytý monitoring systém na ranking jednotlivcov.

## 17. Observability a catalog SLO

Catalog SLO má rozlišovať API availability, processing latency, data freshness, expected-inventory coverage, relation integrity a downstream decision correctness. Vysoká API availability pri stale critical fields je partial failure.

| Signal | Exact identity | Čo dokazuje | Typické false green |
|---|---|---|---|
| Ingestion success | provider/location + source generation | raw input bol prijatý | provider emitoval iba časť expected inventory |
| Processing success | entity + processor/policy generation | raw entity prešla pipeline-om | zobrazuje sa predchádzajúca final entity po novej chybe |
| Stitch freshness | entity generation + timestamps | projection je nová vzhľadom na source budget | jedna fresh annotation maskuje stale ownera |
| Relation integrity | source/target refs + relation type | graph edge je resolvable a aktuálny | dangling relation sa ignoruje v aggregate |
| Ownership reachability | owner entity + escalation generation | owner sa dá kontaktovať a má scope | group existuje, ale službu už nevlastní |
| Runtime correlation | service + deployment UID/generation | projection smeruje na správny runtime subject | name-only lookup spojí iný cluster |
| Inventory coverage | expected set generation | nechýba celý segment | percento sa počíta iba z ingested entities |
| Downstream decision | operation + entity generation | automation použila fresh authorized metadata | workflow loguje len entity name |

Incident response potrebuje timeline source observation, processing, stitching a consumption. Bez nej sa nevie, či nesprávne rozhodnutie vzniklo v authority, providerovi, processore, cache alebo consumerovi.

## 18. Connected incident `GITOPS-PAY-64`

Atlas po `GITOPS-PAY-63` doplnil LaunchPad o catalog-driven isolation profiles a povinné guardrails. Nový service `settlement-export-api` mal patriť tenantovi `vega-regulated`, používať dedicated-node profile a spracúvať restricted settlement data. Repository sa presunulo z `payments-core` do `tenant-services` a nový descriptor zmenil ownera, tenant boundary aj data classification.

Nový custom field v descriptor-e však neprešiel starou processor schema generation. Catalog zachoval poslednú bezchybnú stitched entity, ktorá stále tvrdila:

```text
entity generation:          catalog-g118
owner:                      group:default/orion-payments
tenant boundary:            shared-internal
data classification:        internal
isolation profile:          standard
source revision displayed:  6f914c2
latest source revision:     9ba771e  (processing error)
```

LaunchPad čítal iba final entity fields a nekontroloval processing error, source revision ani freshness. Namespace `vega-settlement-export` preto dostal labels pre shared-internal profil. Guardrail binding `GP-7` bol stále vo `Warn,Audit` rollout-e; dashboard meral iba denied requests a ukazoval nulu. Široká `PolicyException` s selectorom `platform.atlas.io/migration=true` nemala expiry a preskočila cross-namespace credential-reference rule.

Flux zároveň povoľoval cross-namespace source references a tenant Kustomization používala service account s právom vytvárať `SettlementConnection` resources. Cluster-scoped operator mal broad secret-read permission a akceptoval field `credentialRef.namespace` bez tenant validation. Vega workload tak vytvoril connection na `orion-payments/provider-settlement`, ktorú admission iba varovala a operator materializoval.

```text
10:02:11 → descriptor revision 9ba771e merged
10:03:07 → catalog processing error, catalog-g118 zostáva visible
10:06:42 → LaunchPad plan používa catalog-g118
10:08:13 → namespace vytvorený so shared-internal labels
10:11:26 → Flux Kustomization Ready=True
10:12:04 → SettlementConnection cross-namespace warning, request allowed
10:12:19 → operator načíta Orion provider credential
10:15:44 → prvý Vega export cez Orion provider identity
10:43:08 → Orion team dostane nesprávny incident page
10:57:31 → tenant mismatch potvrdený
```

Počas 45 minút bolo cez nesprávny provider context čitateľných `2 184` settlement records a `312` records bolo exportovaných do Vega workspace pred containmentom. Catalog poslal page nesprávnemu ownerovi a predĺžil triage o 26 minút. Guardrail dashboard zostal zelený, pretože reportoval zero denials, nie matched subjects, warnings, skipped exceptions a effective violations.

Catalog root cause nebol iba schema bug. Critical automation použila available final entity ako authority bez generation/freshness gate-u. Last-good projection bola správna availability stratégia pre discovery UI, ale nebola platným inputom pre tenant a privilege decision.

### Catalog redesign

Catalog contract zaviedol field-level provenance a critical status. Tenant boundary, data classification a isolation profile sú prijaté iba z exact reviewed descriptor revision a kompatibilnej processor generation. Processing error označí critical fields ako `StaleForDecision`; UI môže naďalej zobraziť poslednú dobrú entity, ale LaunchPad plan failne closed a vytvorí explicitnú remediation operation.

```text
source revision 9ba771e
→ schema/processor generation cat-policy-12
→ exact entity processing
→ owner/tenant/classification relation resolution
→ stitched entity catalog-g119
→ critical-field freshness and completeness gate
→ namespace/isolation plan bound to catalog-g119
→ policy and tenant boundary verification
→ target read-back
→ catalog runtime projection
```

Owner, runtime, guardrail a tenant fields zostávajú oddelené podľa authority. Catalog už nemôže sám udeliť cross-tenant access; poskytuje subject a provenance, ktoré downstream policy overí proti tenant registry a target state-u.

## 19. Service-catalog acceptance verdict

Acceptance verdict musí dokázať viac než úplnosť formulára. Catalog musí reprezentovať expected software inventory, zachovať authority per field, signalizovať processing a freshness failures a viesť používateľa k správnemu source a ownerovi. Downstream privileged consumer musí viazať svoj plan na exact entity generation a odmietnuť stale critical metadata.

Verdict je end-to-end. Zmena descriptoru musí prejsť ingestion, processing, relation resolution a stitching; následne sa overí discovery, operational routing a aspoň jedna catalog-driven operation. Second-change test zahŕňa owner transfer, source move alebo lifecycle transition. Failure test zahŕňa provider outage, schema error, orphan, duplicate a stale runtime relation.

Service catalog je prijatý, keď sú splnené tieto podmienky:

- **Entity subject je exact** — kind, namespace, name, catalog instance, source a stitched generation sú korelovateľné.
- **Authority je field-specific** — critical metadata má writera, source, validation, conflict a freshness contract.
- **Processing stav je viditeľný** — last-good projection nemaskuje novú ingestion alebo processor chybu.
- **Inventory denominator je explicitný** — coverage sa meria proti expected repository, tenant alebo runtime setu.
- **Relations majú semantics a integrity** — directional edges sú resolvable, freshness-aware a vhodné pre daný use case.
- **Ownership je operational** — owner je resolvable group s reachable escalation a jasným scope-om.
- **Lifecycle má dôsledky** — production, deprecated a retired stavy spúšťajú definované support a closure obligations.
- **Runtime je projection** — deployment, health a version fields nesú concrete identity a observation time.
- **Automation používa CAS** — privileged plan je viazaný na entity generation a invaliduje sa pri critical zmene.
- **Orphan a delete lifecycle je bezpečný** — catalog cleanup nepredbieha runtime, data, identity a dependency closure.
- **Security a privacy sú explicitné** — access, plugin credentials, input trust a retention sú riadené.
- **Second-source a second-change test prešiel** — catalog funguje pri source presune, provider chybe a owner/lifecycle transition.

## 20. Troubleshooting flow

Catalog troubleshooting začína downstream symptomom a exact entity reference. „Catalog ukazuje zlého ownera“ sa rozloží na authority, source, ingestion, processing, stitching, cache a consumer timeline. Najprv sa zachová raw descriptor/provider snapshot, processing errors, final entity, relations a request, ktorý metadata použil.

```text
nesprávna alebo stale catalog informácia
→ exact entity a downstream decision subject
→ expected field authority a source generation
→ ingestion/provider observation
→ policy/processor generation a errors
→ emitted relations/statuses
→ stitched entity a cache generation
→ freshness/completeness verdict
→ consumer plan a target mutation
→ containment downstream privilege alebo routing
→ source/processor/catalog remediation
→ target read-back a second processing cycle
```

Ak final entity zostala stará po processor chybe, oprava nie je ručne prepísať catalog database. Treba opraviť source alebo processor compatibility, znovu spracovať entity, overiť relations a invalidovať všetky pending operations viazané na starú generation. Ak downstream mutation už prebehla, catalog fix sám nevráti runtime alebo IAM stav; potrebuje samostatnú reconciliation a business verification.

## 21. Anti-patterny

Catalog anti-patterny vznikajú najmä vtedy, keď organizácia zamieňa dostupnú projection za autoritatívny a aktuálny model. Nasledujúce vzory treba diagnostikovať podľa ich downstream rozhodnutí, nie iba podľa vzhľadu catalog UI.

### Catalog ako ručne udržiavaný spreadsheet s pekným UI

Centralizované editovanie môže krátkodobo zvýšiť completeness, ale oddelí metadata od owner workflow-u a source review-u. Výsledkom je vysoká deklarovaná coverage a nízka freshness. Oprava je authority map, automated providers tam, kde existuje externá authority, a owner-managed descriptors tam, kde tím skutočne vlastní význam.

### Entity existuje, teda je production-ready

Registration dokazuje iba to, že catalog pozná entity. Neoveruje deployment, on-call, SLO, backup, security ani business outcome. Production lifecycle musí byť explicitná decision s evidence contractom.

### Jeden owner field pre všetko

Software, platform, data a incident authority môžu patriť rôznym groups. Jeden string vedie k nesprávnym approvalom a pages. Model potrebuje role-specific relations alebo jasne definovaný owner scope.

### Last-good entity bez stale semantics

Zachovanie poslednej validnej entity zvyšuje availability catalogu. Bez error a freshness propagation však vytvára false authority. Discovery môže fungovať degraded; privileged automation musí failnúť alebo vyžiadať fresh review.

### Catalog ako autorita runtime health

Statické annotations alebo periodický plugin snapshot nemajú nahradiť deployment controller, observability a business canary. Catalog má korelovať a navigovať, nie vydávať unsupported green verdict. Ak consumer potrebuje release acceptance, musí prejsť k exact runtime a business evidence namiesto preberania catalog farby.

### Scorecard ako guardrail

Scorecard môže odhaliť debt a viesť remediation, ale často neblokuje mutation a môže byť stale. Ak organizácia potrebuje invariant, musí ho presadiť na authoritative boundary a scorecard použiť ako supporting evidence.

### Delete entity ako decommission

Odstránenie catalog recordu nezruší DNS, credential, data, cost ani consumer dependency. Bez closure graphu iba odstráni viditeľnosť problému. Decommission operation sa uzatvára až po residual scan-e a catalog removal je následná projection transition.

## 22. Kontrolné otázky

1. Ako sa líši inventory, registry, CMDB a service catalog?
2. Čo tvorí exact catalog-entity subject a generation?
3. Prečo catalog entity nie je automaticky authority pre všetky fields?
4. Ako fungujú ingestion, processing a stitching a čo znamená last-good projection?
5. Prečo relation graph nie je automaticky runtime dependency truth?
6. Ako sa owner relation mení na operational contract?
7. Prečo lifecycle a support tier nemajú byť jedna hodnota?
8. Ako sa meria freshness a completeness proti správnemu denominatoru?
9. Kedy je catalog-driven automation bezpečná a prečo potrebuje compare-and-swap?
10. Ako sa líši orphan catalog entity od decommissioned software?
11. Prečo `GITOPS-PAY-64` zostal catalog dostupný, ale nebol platný pre tenant decision?
12. Čo musí obsahovať service-catalog acceptance verdict?

## Glossary impact

Relevantné pojmy: service catalog, catalog entity subject, field authority map, source generation, stitched entity generation, last-good catalog projection, catalog freshness budget, expected catalog inventory, catalog relation integrity, orphan entity, catalog-driven operation, catalog compare-and-swap, runtime projection, catalog processing error, operational ownership relation, service-catalog acceptance verdict.

## Primárne zdroje

Nasledujúce zdroje dokumentujú core Backstage entity model, ingestion/processing/stitching lifecycle a relation semantics, z ktorých kapitola odvodzuje catalog authority a freshness model. Organizačné taxonomy, field authorities a acceptance contracts musia byť napriek tomu explicitne definované konkrétnou platformou.

Tieto dokumenty sú technickými primárnymi zdrojmi pre default entity envelope, processing lifecycle a relation graph. Neurčujú automaticky organizačnú definíciu ownera, lifecycle, support tieru ani tenant authority; tie musí platforma doplniť ako versionované contracts a overiť na vlastných workflows. Pri implementácii treba vždy čítať dokumentáciu verzie, ktorú organizácia skutočne prevádzkuje, a testovať provider, processor a plugin compatibility na representative entities.

- [Backstage — Software Catalog](https://backstage.io/docs/features/software-catalog/)
- [Backstage — The Life of an Entity](https://backstage.io/docs/features/software-catalog/life-of-an-entity/)
- [Backstage — System Model](https://backstage.io/docs/features/software-catalog/system-model/)
- [Backstage — Descriptor Format of Catalog Entities](https://backstage.io/docs/features/software-catalog/descriptor-format/)
- [Backstage — Well-known Relations](https://backstage.io/docs/features/software-catalog/well-known-relations/)
- [Backstage — Creating the Catalog Graph](https://backstage.io/docs/features/software-catalog/creating-the-catalog-graph/)
- [Backstage — Extending the Model](https://backstage.io/docs/features/software-catalog/extending-the-model/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Developer experience](developer-experience.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Guardrails →](guardrails.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
