# Automation Mindset

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Continuous Improvement](continuous-improvement.md), [Ownership Mindset](ownership-mindset.md)
- Súvisiace témy: idempotency, Infrastructure as Code, CI/CD, scripting, platform engineering, toil

Metadata zaraďuje automation mindset za ownership a continuous improvement. Automatizácia nie je cieľom sama osebe; je to spôsob premeny stabilného, hodnotného a pochopeného procesu na bezpečne vykonateľnú capability.

## 1. Definícia

Automation mindset je spôsob uvažovania, pri ktorom sa opakovateľná práca navrhuje s explicitnými vstupmi, výstupmi, failure semantics, evidence a ownershipom. Človek sa nespolieha na neformálnu pamäť, ručné poradie krokov a individuálne prostredie tam, kde stroj môže proces vykonať konzistentnejšie.

Automation mindset neznamená automatizovať všetko. Rozlišuje činnosti vhodné pre deterministic execution, decisions vyžadujúce ľudský context a hybridné flows, v ktorých automation pripraví evidence a človek urobí risk decision.

## 2. Problém manuálnych procesov

Manuálny proces môže byť primeraný pri jednorazovej alebo nejasnej úlohe, no pri opakovaní vytvára variabilitu a skrytú dependence na skúsenosti konkrétneho operátora. Rovnaký checklist môže byť vykonaný iným poradím, s inou environment configuration alebo bez verification posledného kroku.

Typický manuálny deployment vyzerá jednoducho:

```text
prihlásiť sa na server
→ stiahnuť package
→ upraviť configuration
→ reštartovať service
→ pozrieť log
```

Každý krok však skrýva decisions: ktorý package digest, aký configuration source, čo sa stane pri partial download-e, či restart preruší traffic a ktorý log line potvrdzuje user outcome. Automatizácia musí tieto implicitné assumptions najprv zviditeľniť.

## 3. Riziká manuálnej práce

Manuálnosť nie je problém iba preto, že trvá dlhšie. Vytvára viac druhov prevádzkového risku:

- **Variabilita — rovnaký intent vytvára rozdielny výsledok**: operátori používajú iné commandy, poradie alebo local defaults.
- **Pamäťová závislosť — critical knowledge nie je executable ani reviewovateľný**: odchod alebo nedostupnosť experta zablokuje change a recovery.
- **Neúplný audit — dôvod, inputs a vykonané kroky sa nedajú spätne rekonštruovať**: incident review nevie spojiť runtime state s konkrétnym actorom a revisionom.
- **Skipped verification — proces skončí po execution**: service môže bežať, ale neposkytovať správny user outcome.
- **Nízka scale — práca rastie s počtom environments a services**: rovnaký počet ľudí spravuje čoraz viac opakovaných tasks a toil vytlačí improvement work.
- **Inconsistent security — permissions a secrets sa riešia ad hoc**: broad access a copy-paste credentials vytvárajú compromise a leakage risk.

## 4. Mentálny model automation lifecycle-u

Automatizácia je produkt s vlastným lifecycle-om. Začína pozorovaním opakovanej práce, pokračuje štandardizáciou a končí prevádzkou, meraním, údržbou alebo retirementom capability.

```text
opakovaná práca a evidence o toil-e
→ pochopenie outcome-u a failure modes
→ odstránenie nepotrebných krokov
→ explicitný input/output contract
→ automation implementation
→ tests, guardrails a telemetry
→ bounded rollout a adoption
→ maintenance, versioning a decommission
```

Preskočenie prvých krokov vedie k „automation of chaos“. Systém vykonáva nejasný proces rýchlejšie, ale failure zostáva ťažšie pochopiteľný a blast radius môže byť väčší.

## 5. Kedy je úloha dobrý kandidát

Silný kandidát má stabilný behavior a merateľný výsledok. Viacero charakteristík zvyšuje hodnotu automation, ale žiadna jednotlivá vlastnosť nie je absolútna podmienka.

- **Vysoká frekvencia — opakovaný cumulative cost**: aj krátky manuálny krok môže spotrebovať veľkú kapacitu pri stovkách vykonaní.
- **Stabilné pravidlá — možnosť explicitného decision contractu**: vstupy a outcomes sa dajú formalizovať bez neustáleho human judgmentu.
- **Náchylnosť na ľudskú chybu — variabilita poradia alebo hodnoty**: machine execution znižuje skipped steps a typo risk.
- **Významný waiting alebo coordination time — odstránenie queue**: self-service môže skrátiť dva dni ticketového čakania na minúty.
- **Audit requirement — potreba preukázať actor, input a result**: versioned workflow zachováva evidence pre incident a compliance.
- **Environment consistency — rovnaký desired outcome vo viacerých scopes**: automation znižuje configuration drift a snowflake state.
- **Vysoký failure impact — potreba guardrails a verification**: controlled workflow môže obmedziť destructive operation a vyžadovať relevantné evidence.
- **Automaticky overiteľný výsledok — schopnosť uzavrieť loop**: smoke, query alebo state comparison odlíši execution od úspešného outcome-u.

## 6. Typické automation domains

Príklady nie sú iba zoznamom populárnych nástrojov. Každá doména má konkrétny opakovaný contract:

- **Build a test — reprodukovateľná transformácia source-u na evidence a artifact**: workflow pinne dependencies, uchová logs a priradí výsledok revisionu.
- **Infrastructure provisioning — desired resources a policy**: plan a apply nahrádzajú console clicks a podporujú review a recovery.
- **Deployment — riadená zmena runtime state-u**: ordering, health, rollout a rollback znižujú variabilitu production change-u.
- **Certificate rotation — time-bound identity lifecycle**: automation obnoví credential pred expiráciou, distribuuje ho a overí nový trust path.
- **Backup verification — pravidelný recovery dôkaz**: nestačí vytvoriť copy; workflow vykoná restore a application validation.
- **Policy validation — konzistentný control na definovanej boundary**: známe nepovolené configuration sa zablokujú pri source, plan alebo admission kroku.
- **Environment vending — self-service standardized scope**: používateľ deklaruje potrebu a platforma aplikuje identity, network, cost a cleanup guardrails.
- **Dependency scanning a updates — lifecycle známych components**: automation identifikuje findings alebo vytvorí bounded update, ale človek môže stále posúdiť compatibility a risk.

## 7. Kedy automatizácia nemusí byť vhodná

Nie každá práca má dostatočne stabilný contract alebo opakovateľnosť. Automatizácia môže vytvoriť väčší cost a rigidity než pôvodná manuálna operácia.

- **Jednorazový nejasný task — learning je ešte dominantný**: najprv môže byť vhodný dokumentovaný a auditovaný script alebo manual procedure.
- **Rýchlo sa meniace pravidlá — interface nie je stabilný**: general framework by vyžadoval neustálu údržbu a komplikovaný abstraction layer.
- **High-context decision — risk závisí od neštruktúrovaných informácií**: automation má pripraviť evidence, nie predstierať deterministic judgment.
- **Neprimeraný implementation cost — návratnosť je slabá**: development, testing, support a incident risk môžu prevýšiť ušetrený toil.
- **Neoveriteľný outcome — chýba autoritatívny signal**: automation môže skončiť `success`, ale nevie preukázať, že cieľový systém je správny.
- **Príliš veľký blast radius — jedna chyba zasiahne mnoho scopes**: najprv treba partitioning, canary, rate limit a kill switch.

Jednorazová migration môže stále používať automation kvôli auditovateľnosti a retry. Nemusí sa však premeniť na permanentnú multi-tenant platformu.

## 8. Cost model

Automation má počiatočný aj priebežný cost. Rozhodnutie musí zahŕňať ownership a lifecycle, nie iba odhad času na prvý script.

```text
automation cost =
analysis + implementation + testing + security + operation + support + maintenance + migration + retirement
```

Manuálny process má tiež širšiu cenu:

```text
manual cost =
frequency × active time + waiting + coordination + error impact + audit effort + opportunity cost
```

Najväčší benefit môže vzniknúť odstránením waitingu a risku, nie iba úsporou operator minutes. Self-service environment môže ušetriť desať minút execution a zároveň dva dni queue latency.

## 9. Break-even a sensitivity

Jednoduchý break-even odhad porovná investíciu s opakovanou úsporou. Musí však zohľadniť neistotu frekvencie, maintenance a error costu.

```text
break-even runs ≈ initial automation cost / average saving per run
```

Ak sa proces vykoná iba päťkrát, robustná platforma nemusí dávať zmysel. Ak destructive chyba raz za rok spôsobí veľký incident, automation s guardrails môže byť hodnotná aj pri nízkej frekvencii.

Sensitivity analysis skúma, čo sa stane pri nižšej adoption, vyššom support coste alebo zmene API. Automation decision nemá byť založený iba na najoptimistickejšom scenári.

## 10. Úrovne automation

Automation môže dozrievať podľa opakovateľnosti a počtu consumers. Vyššia úroveň nie je automaticky lepšia; zvyšuje interface, compatibility a support povinnosti.

### Dokumentovaný manuálny proces

Dokumentovaný process explicitne zachytáva steps, preconditions a verification. Stále závisí od človeka, ale znižuje knowledge silo a poskytuje základ na pozorovanie variability.

Je vhodný pri novom alebo zriedkavom tasku. Dokument musí byť testovaný, pretože neaktuálny checklist poskytuje falošnú dôveru.

### Script

Script automatizuje bounded sekvenciu pre konkrétny use case. Môže dramaticky znížiť typo risk a execution time, ale často má úzky input contract a slabší multi-user lifecycle.

Production-critical script potrebuje repository, tests, ownera, logging a versioning. Osobný súbor v home directory nie je organization capability.

### Pipeline alebo workflow

Pipeline koordinuje viac steps, artifacts, gates a environments. Poskytuje shared execution, audit, concurrency a secrets integration, ale potrebuje failure isolation a diagnosability.

Pipeline stage nemá existovať iba preto, že ho podporuje tool. Každý krok musí pridať evidence, transformation alebo risk decision.

### Reusable component

Shared action, module alebo template znižuje duplicitu medzi tímami. Vytvára však versioned interface a compatibility obligation voči consumers.

Reusable component potrebuje release notes, deprecation a test matrix. Breaking change v shared workflow môže zastaviť desiatky repositories naraz.

### Self-service platform capability

Platform capability umožňuje používateľovi deklarovať potrebu a bezpečne vykoná komplexný process cez stable API alebo portal. Je to interný produkt s users, SLO, roadmapou, supportom a security modelom.

Platform level má zmysel pri mnohých opakovaných consumers. Premature platform abstraction môže zmeniť jeden use case na drahý organization-wide dependency.

## 11. Imperative automation

Imperative model opisuje poradie commands potrebných na zmenu state-u. Je vhodný pri procedural workflow, migration alebo operation, kde sequence a intermediate state majú význam.

```text
vytvor network
→ vytvor subnet
→ vytvor VM
→ nainštaluj package
→ spusti service
```

Imperative automation musí sledovať, ktoré kroky už prebehli a ako sa zotaví po partial failure. Opakované spustenie bez state awareness môže vytvoriť duplicates alebo zmeniť správny state nesprávnym spôsobom.

## 12. Declarative automation

Declarative model opisuje požadovaný výsledný state a controller porovná desired a observed state. Reconciliation opakovane vykonáva potrebnú korekciu, kým sa stav nepriblíži deklarácii alebo nevznikne explicitný failure.

```text
existuje network, subnet, VM a service s definovanými properties
```

Deklaratívny model podporuje drift detection a safe re-execution, ale nie je bez complexity. Controller potrebuje authoritative state, provider behavior, dependency graph a jasné semantics pre resources, ktoré nemožno meniť in-place.

## 13. Idempotency

Idempotentná operation pri opakovaní rovnakého intentu vedie k rovnakému požadovanému výslednému state-u. Neznamená, že interné execution je identické alebo že nevznikne žiadny side effect; znamená, že caller bezpečne opakuje request bez nekontrolovanej duplicity.

```text
ensure user alice exists
prvé spustenie  → user sa vytvorí
druhé spustenie → automation zistí zhodu a nevytvorí ďalšiu identity
```

Idempotency je kritická pri timeout-e. Caller nemusí vedieť, či server operation nevykonal alebo vykonal a stratil response; retry preto potrebuje stable operation identity alebo state comparison.

## 14. Partial failure

Complex automation môže uspieť v prvých krokoch a zlyhať neskôr. Binary `success/failed` bez uloženého progressu a reconciliation pathu nehovorí, ktorý state zostal v cieľovom systéme.

Partial failure strategy môže použiť:

- **Resume — pokračovanie od bezpečného checkpointu**: vyžaduje versioned state a overenie, že predchádzajúce kroky sú stále validné.
- **Reconcile — porovnanie desired a observed state-u**: controller vykoná iba chýbajúce alebo odlišné operations.
- **Rollback — návrat predchádzajúceho state-u**: funguje iba pri reverzibilných zmenách a compatible data.
- **Compensation — opačný business side effect**: pri distribuovanej transakcii môže zrušiť rezerváciu namiesto technického undo všetkých krokov.
- **Manual escalation — kontrolovaný vstup človeka**: používa sa pri ambiguous alebo high-risk state-e s dostatočným evidence.

## 15. Error classification

Automation musí rozlíšiť, či chyba je transientná, permanentná, policy-related alebo neznáma. Rovnaký retry behavior pre všetky classes vytvára noise, delay alebo amplification.

- **Invalid input — permanentný caller problem**: workflow má rýchlo zlyhať s field-level vysvetlením a nesmie slepo retryovať.
- **Authentication alebo authorization failure — identity alebo policy problem**: retry bez zmeny credentialu alebo policy iba predlžuje queue.
- **Rate limit alebo temporary unavailability — možný transient failure**: bounded exponential backoff a jitter môžu umožniť recovery.
- **Partial success — ambiguous target state**: pred ďalším pokusom sa musí zistiť, čo už bolo vykonané.
- **Invariant violation — system state nie je bezpečný pre pokračovanie**: workflow sa zastaví a zachová evidence pre human decision.
- **Unknown error — neklasifikovaný failure contract**: nemá sa automaticky považovať za transient; potrebuje safe default a ownera.

## 16. Retry contract

Retry je vhodný iba vtedy, keď ďalší pokus môže uspieť a opakovanie je bezpečné. Musí byť ohraničený časom alebo počtom attempts a zosúladený s celkovým deadline-om workflowu.

Bezpečný retry používa:

- **Error allowlist — presné retryable classes**: permanentné syntax, permission a validation failures sa rýchlo ukončia.
- **Exponential backoff — rastúci interval**: dependency dostane čas na recovery a nie je zahltená okamžitými attempts.
- **Jitter — rozloženie clients v čase**: tisíce workflows nereagujú na outage v rovnakom okamihu.
- **Attempt a time budget — limit amplification**: workflow neblokuje queue nekonečne a caller dostane deterministický výsledok.
- **Idempotency alebo deduplication — ochrana side effects**: retry nevytvorí duplicate account, payment alebo deployment.
- **Final evidence — zachovanie poslednej chyby a state-u**: operator vie, prečo retries skončili a čo zostalo vykonané.

## 17. Validation

Input validation kontroluje syntax, types, ranges, relationships a policy ešte pred destructive execution. Čím bližšie k vstupu sa chyba odhalí, tým menší cost a blast radius vytvorí.

Validation nesmie predstierať úplné guarantees. Terraform plan môže ukázať intended changes, ale cloud capacity, race alebo external policy sa môžu zmeniť pred apply; workflow preto potrebuje aj runtime verification.

## 18. Dry-run, plan a preview

Dry-run alebo plan zobrazí zamýšľanú zmenu bez plného vykonania. Je hodnotný iba vtedy, keď reprezentuje skutočný target state a reviewer rozumie diffu a risku.

Plan môže zastarať medzi review a apply. High-risk workflow preto môže viazať approval na konkrétny plan digest, krátku validity window a unchanged inputs.

Preview nie je náhradou rollbacku. Niektoré side effects alebo provider behavior sa prejavia až počas execution.

## 19. Guardrails

Automation zrýchľuje správne aj nesprávne actions a môže zväčšiť blast radius. Guardrails musia byť navrhnuté podľa konkrétneho threatu alebo failure boundary.

- **Input validation — blokovanie neplatného intentu pred execution**: zabraňuje destructive alebo inconsistent parameters.
- **Least privilege — obmedzenie možných actions a resources**: compromise alebo bug nemôže meniť celý organization scope.
- **Environment protection — odlišné risk boundaries**: production apply môže vyžadovať silnejšiu identity, plan a rollout než ephemeral test.
- **Policy as code — repeatable organization controls**: známe rules sa vyhodnotia konzistentne a report vysvetlí porušenie.
- **Rate a concurrency limits — kontrola systemic loadu**: automation nevytvorí API storm alebo paralelnú mutáciu rovnakého state-u.
- **Canary alebo staged rollout — obmedzený exposure**: zmena sa overí na malom scope-e pred rozšírením.
- **Audit log — reconstruction actor, input a decisionu**: incident review vie spojiť workflow s runtime outcome-om.
- **Kill switch — okamžité zastavenie ďalšieho execution**: používa sa pri nepredvídanom behavior-e a musí byť dostupný nezávisle od failed pathu.

## 20. Human in the loop

Human approval má hodnotu pri ambiguous alebo high-impact decisione, ktoré nemožno bezpečne vyjadriť policy. Človek má posudzovať risk a exception, nie mechanicky potvrdzovať každý green plan.

```text
automation vytvorí immutable plan a risk context
→ reviewer posúdi affected resources, policy exceptions a rollback
→ approval sa viaže na konkrétny input digest
→ system vykoná apply
→ automated verification potvrdí outcome
```

Approval bez contextu je formálny gate a vytvára diffusion of responsibility. Reviewer musí mať čas, expertise a authority zmenu odmietnuť alebo žiadať úpravu.

## 21. Human override a break-glass

Incident môže vyžadovať odlišný path než bežný workflow. Override musí byť explicitný, auditovaný, časovo obmedzený a nasledovaný reviewom a návratom do managed state-u.

Break-glass nemá znamenať ručné zmeny, ktoré automation neskôr nepozná. Po urgentnom zásahu treba reconcile source of truth, zachovať evidence a rozhodnúť, či sa override zmení na supported capability alebo odstráni.

## 22. Observability automation

Automation je production system a potrebuje vlastnú telemetry. Exit code alebo zelený UI status nestačí na diagnosis ani measurement value.

- **Run ID — jednoznačná execution identity**: spája logs, artifacts, approvals a target changes.
- **Structured step events — čas a outcome jednotlivých phases**: ukazujú bottleneck a failure boundary.
- **Input a version metadata — presný execution contract**: operator vie, ktorý revision, parameters a dependency versions boli použité.
- **Retry a queue metrics — backpressure a instability**: vysoký retry môže maskovať provider outage alebo flaky step.
- **Result artifacts — plan, report, manifest alebo state reference**: evidence zostáva dostupné pre audit a verification.
- **Actor a authorization context — kto a s akou role spustil workflow**: incident analysis rozlišuje user intent, automation identity a delegated action.
- **Success a failure rate — reliability capability**: owner vidí, či workflow dlhodobo znižuje toil alebo vytvára ďalší support load.
- **End-to-end outcome — skutočná hodnota**: environment exists and passes smoke, nie iba `apply` exit code 0.

## 23. Security automation

Automation identity často vlastní powerful permissions a spracúva secrets, artifacts a production configuration. Security design musí oddeliť user intent, workflow identity a target authorization.

Dôležité controls:

- **Short-lived credentials — zníženie leak windowu**: workflow získava scoped session pre konkrétny run namiesto statického access keyu.
- **Input trust — ochrana pred untrusted code alebo parameters**: pull request z fork-u nesmie automaticky získať production secret.
- **Artifact integrity — overenie toho, čo sa vykonáva**: pinned actions, signed images a digest references znižujú supply-chain substitution.
- **Secret redaction — ochrana logs a errors**: structured telemetry nesmie kopírovať tokens alebo sensitive payload.
- **Separation of duties — high-risk decision a execution boundaries**: podľa risku môže iný actor schváliť plan, pričom automation vykoná deterministický apply.
- **Audit immutability — ochrana evidence**: workflow s production rights nemá zároveň nekontrolovanú možnosť odstrániť vlastný audit trail.

## 24. State management

Automation potrebuje vedieť, čo už vykonala a aký state je autoritatívny. Bez state modelu sa pri retry alebo concurrency opiera o náhodné pozorovanie a môže prepísať legitímnu zmenu.

State môže byť uložený v Terraform backend-e, workflow database, Kubernetes API alebo target resource metadata. Musí mať locking alebo optimistic concurrency, backup, access control a recovery plan primeraný criticality.

State drift vzniká, keď cieľ zmení iný actor alebo manual override. Automation má drift reportovať a reconcile-nuť podľa policy, nie ho neviditeľne prepísať bez contextu.

## 25. Concurrency a locking

Dve automation executions meniace rovnaký resource môžu vytvoriť race, stale plan alebo conflicting side effects. Concurrency control preto patrí do workflow designu.

- **Global alebo resource lock — serializácia critical state mutation**: znižuje race, ale môže vytvoriť queue a potrebuje stale-lock recovery.
- **Optimistic concurrency — compare version before write**: umožňuje paralelné reads a zlyhá, ak sa state medzitým zmenil.
- **Partitioned ownership — paralelné independent scopes**: jobs pre odlišné accounts alebo clusters sa neblokujú, ak nemajú shared dependency.
- **Deduplication key — zlúčenie rovnakého intentu**: opakované eventy nespustia duplicate deployment alebo environment create.

## 26. Versioning a compatibility

Automation code, configuration, runtime, APIs a consumers sa menia nezávisle. Reusable capability potrebuje versioned interface a migration strategy.

Breaking update shared pipeline môže zastaviť mnoho repositories. Safe rollout používa semantic alebo explicitné versions, canary consumers, deprecation window a compatibility tests.

Pinning navždy nie je riešenie. Stará version accumuluje vulnerabilities a incompatibility; platform owner potrebuje inventory adopcie a controlled upgrade path.

## 27. Ownership a support

Každá production automation potrebuje ownera. Owner riadi roadmapu, incidenty, dependencies, security findings, support, metrics a retirement.

Ownership contract má obsahovať:

- **Supported use cases — čo capability garantuje**: zabraňuje nekonečnému extension cez hidden special cases.
- **SLO alebo response expectation — reliability a support boundary**: consumers vedia, čo robiť pri outage.
- **Change a deprecation process — lifecycle interface-u**: upgrade nepríde ako nekomunikovaný breaking change.
- **Incident a escalation — kto vedie recovery**: workflow failure sa nepresúva medzi tool, cloud a product tímom bez lead ownera.
- **Adoption a value metrics — či automation rieši pôvodný toil**: existence scriptu nie je dôkazom používania alebo výsledku.

## 28. End-to-end príklad environment vendingu

Pôvodný process používa ticket a wiki. Administrátor po dvoch dňoch ručne vytvorí VM, network rules a accounts, pričom environmenty sa odlišujú podľa človeka.

Automation lifecycle:

```text
Git alebo portal request s typed parameters
→ schema a policy validation
→ Terraform plan viazaný na input digest
→ production risk approval podľa scope-u
→ apply s locked remote state
→ configuration a secret delivery
→ smoke a security verification
→ inventory, owner a expiry registration
→ telemetry a automatic cleanup
```

Každý krok odstraňuje inú medzeru. Typed input znižuje ambiguity, plan poskytuje decision evidence, locked state chráni concurrency a inventory s expiry zabraňuje orphaned resources.

## 29. Build, buy alebo platform decision

Pred vlastným riešením treba posúdiť existujúcu capability, managed service, open-source component, shared internal module a bounded script. Výber sa opiera o differentiating value, compliance, integration, lifecycle a total cost.

- **Built-in alebo managed capability — menší ownership scope**: provider preberá časť maintenance, no customer stále vlastní configuration, access a outcome.
- **Open-source tool — kontrola a community ecosystem**: organization vlastní deployment, security patching, integration a support risk.
- **Internal shared component — reuse s menším product surface**: vhodný pri stabilnom common contracte bez potreby full self-service platformy.
- **One-off script — bounded audit a repeatability**: primeraný pri malej migration, ak má ownera a safe execution.
- **Internal platform — organization product**: oprávnený pri mnohých consumers a strategic workflowe, ale potrebuje dedicated roadmap a support.

## 30. Automation adoption

Capability bez adoption neznižuje toil. Users ju môžu obchádzať pre zlý interface, dlhú latency, chýbajúci use case alebo nedôveru v failure behavior.

Adoption evidence zahŕňa percentage relevantných flows, time saved, support volume, bypass rate a user feedback. Mandatory use môže skryť dissatisfaction a vytvoriť shadow scripts, preto platform team potrebuje product discovery a explicitný exception path.

## 31. Retirement automation

Automation sa má odstrániť, keď source process zanikne, capability nahradí platforma alebo maintenance cost prevýši value. Orphaned workflow môže držať broad credentials, outdated dependencies a confusing alternative path.

Retirement zahŕňa inventory consumers, migration, removal schedules, credential revocation, state archival a documentation update. Vypnutie jobu bez cleanup-u môže ponechať resources a ownership gaps.

## 32. Anti-patterny

### Automation zlého procesu

Komplexný approval workflow sa presunie do pipeline bez overenia, ktoré decisiony sú skutočne potrebné. Execution je elektronický, ale wait time a diffusion of responsibility zostanú.

### Script bez ownera

Critical tool existuje v osobnom repository alebo serveri a nikto nevie jeho dependencies a failure behavior. Pri odchode autora sa z automation stane incident risk.

### Premature abstraction

Jeden use case sa generalizuje do frameworku s množstvom configuration options. Product surface, tests a support rastú skôr, než existuje druhý stabilný consumer.

### Hidden manual step

Pipeline vyzerá automated, ale vyžaduje console change alebo local file mimo source of truth. Audit a reproducibility sa prerušia na najcitlivejšej boundary.

### Automation sprawl

Tímy vytvoria rozdielne scripts pre rovnaký process. Security, behavior a ownership sa rozídu a incident responder nevie, ktorý path je authoritative.

### Success without verification

Workflow skončí exit code 0 po API acknowledgement-e, ale neoverí resulting state ani user outcome. Execution success sa zamieňa za operation success.

### Infinite retry

Permanentný invalid input blokuje queue a opakuje side effect. Retry policy nemá error classification, budget ani dead-letter path.

### Platform as universal answer

Organization vytvorí internal product pre malú alebo nestabilnú potrebu. Roadmap a support cost následne prevýšia ušetrenú manuálnu prácu.

## 33. Troubleshooting automation systému

Pri failure najprv urč, či problém vznikol v inpute, workflow execution, dependency alebo target verification. Neopakuj celý run bez poznania partial state-u.

- **Workflow zlyháva po update-e — version alebo compatibility boundary**: porovnaj runtime, action, API a consumer versions a použité immutable references.
- **Retry vytvára duplicates — chýba idempotency alebo deduplication**: identifikuj stable operation key a server-side result state.
- **Runs čakajú v queue — concurrency alebo capacity constraint**: rozlíš runner shortage, global lock a long-running blocked job.
- **Apply je green, service nefunguje — verification gap**: doplň application smoke, dependency a business outcome signal.
- **Users automation obchádzajú — product interface alebo latency problem**: analyzuj bypass paths, support tickets a missing use cases.
- **State sa nezhoduje so source-om — drift alebo competing actor**: zisti authoritative state, manual changes a locking pred reconcile.
- **Automation incident má veľký blast radius — scope a guardrail gap**: pridaj partitioning, canary, rate limits, least privilege a kill switch.

## 34. Kontrolné otázky

1. Prečo automation mindset neznamená automatizovať všetko?
2. Aké vlastnosti robia process dobrým automation kandidátom?
3. Ako sa porovnáva total manual cost s automation lifecycle costom?
4. Kedy je vhodný script a kedy self-service platform capability?
5. Aký je rozdiel medzi imperative a declarative automation?
6. Prečo idempotency rieši ambiguous timeout behavior?
7. Aké strategies existujú pri partial failure?
8. Prečo retry potrebuje error classification, backoff, jitter a budget?
9. Čo musí človek reálne posudzovať pri human-in-the-loop approvale?
10. Aké guardrails znižujú automation blast radius?
11. Ktoré telemetry potrebuje production workflow?
12. Ako state management a locking chránia concurrent execution?
13. Prečo shared automation potrebuje versioning a deprecation?
14. Ako sa meria adoption a skutočná hodnota automation?
15. Kedy a ako sa automation bezpečne retire-ne?

## 35. Zhrnutie

Automation mindset začína pochopením outcome-u, variability, failure modes a total costu. Až potom štandardizuje a automatizuje process s explicitným input contractom, idempotency, error handlingom, guardrails, security a verification.

Automation je production product s ownerom, versioningom, telemetry, supportom a retirementom. Jej cieľom je znižovať toil, waiting a risk bez vytvorenia neprimeraného blast radiusu, rigidnej platformy alebo skrytých manuálnych boundaries.

## Glossary impact

Relevantné pojmy: automation mindset, automation candidate, break-even, automation level, imperative automation, declarative automation, idempotency, partial failure, compensation, retry contract, dry-run, guardrail, human in the loop, break-glass, workflow state, concurrency control, deduplication, automation product a adoption.

## Primárne zdroje

- [Google SRE — Eliminating Toil](https://sre.google/sre-book/eliminating-toil/)
- [Google Cloud — DevOps capabilities](https://cloud.google.com/architecture/devops)
- [NIST Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: You build it, you run it](you-build-it-you-run-it.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Declarative vs. imperative prístup →](declarative-vs-imperative.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
