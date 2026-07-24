# Shift-right

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

## 1. Definícia

Shift-right rozširuje verification, validation a experimentovanie do deploymentu a produkčnej prevádzky. Jeho cieľom je získať dôkaz o správaní systému v prostredí, kde pôsobí skutočný traffic, reálne identity, objemy dát, externé služby, používateľské správanie a distribuované failure modes.

Neznamená to „testovať až v produkcii“. Shift-right nadväzuje na skoré kontroly a používa kontrolovanú expozíciu, observability a bezpečné rozhodovacie mechanizmy.

```text
shift-left
→ prevencia, skorý a diagnostický feedback

shift-right
→ reálna environment fidelity a prevádzkové učenie
```

Dobrý delivery systém používa obe strany. Shift-left znižuje počet predvídateľných chýb, ktoré sa dostanú k používateľovi. Shift-right odhaľuje vlastnosti, ktoré nemožno úplne reprodukovať pred produkciou, a premieňa ich na nové skoršie kontroly.

## 2. Mental model: kontrolovaná expozícia

Shift-right nie je pasívne sledovanie dashboardu po release. Je to riadený lifecycle:

```text
hypotéza a riziko
→ immutable artifact
→ cieľová cohort/exposure
→ zber signálov
→ porovnanie s baseline alebo control
→ rozhodnutie
→ promote / pause / rollback / roll-forward
→ učenie a trvalá kontrola
```

Každý krok musí byť identifikovateľný. Bez znalosti verzie artifactu, konfigurácie, feature flags, cohorty a času expozície nemožno spoľahlivo pripísať pozorovanú zmenu konkrétnemu release-u.

## 3. Prečo predprodukčné prostredie nestačí

Staging môže byť technicky podobný produkcii, ale zvyčajne nereprodukuje všetky relevantné podmienky:

- **Traffic mix —** produkcia obsahuje reálne kombinácie operácií, payloadov, session patterns a retry behavior.
- **Objem a distribúcia dát —** veľkosť tabuliek, hot keys, tenant skew a historický stav ovplyvňujú výkon aj correctness.
- **Identity a authorization —** federation, claims, role mappings a revocation môžu byť v stagingu zjednodušené.
- **Sieť a regióny —** latency, packet loss, DNS, peering a CDN behavior sa líšia.
- **Quotas a shared dependencies —** produkčné limity a konkurencia medzi workloadmi nemusia existovať v test prostredí.
- **Používateľské správanie —** ľudia používajú systém inak než scripted testy a vytvárajú nečakané sekvencie.
- **Dlhodobý tlak —** memory leaks, queue growth, cache churn a storage accumulation sa prejavia až v čase.
- **Emergent behavior —** distribuované interakcie môžu vytvoriť failure, ktorý nie je vlastnosťou jedného komponentu.

Preto úspešný deployment znamená iba to, že orchestrátor dokončil plánovanú operáciu. Neznamená, že zmena je technicky, funkčne alebo businessovo prijateľná.

## 4. Predpoklady bezpečného shift-right

Produkčná validácia je bezpečná iba vtedy, keď existujú základné controls:

- **Immutable artifact identity —** vieme presne určiť build, digest, commit a provenance.
- **Configuration identity —** vieme, ktoré flags, secrets references a runtime settings boli aktívne.
- **Blast-radius control —** expozíciu možno obmedziť podľa trafficu, tenantov, regiónu alebo identity.
- **Observability —** technický aj business výsledok je merateľný a korelovateľný.
- **Rollback alebo roll-forward —** existuje overená cesta návratu alebo rýchlej opravy.
- **Abort criteria —** vopred je jasné, ktorý signál rollout zastaví.
- **Owner —** konkrétna osoba alebo tím sleduje rozhodnutie a reaguje na failure.
- **Safe data handling —** experiment rešpektuje privacy, retention a test-data pravidlá.
- **Communication —** relevantné tímy vedia, čo prebieha a ako sa incident eskaluje.

Bez týchto controls sa shift-right mení na nekontrolované prenášanie testovacích nákladov na používateľov.

## 5. Tri vrstvy produkčnej validácie

Produkčný oracle sa skladá z viacerých vrstiev. Jedna zelená metrika nestačí.

### Technická validácia

Overuje, či infraštruktúra a komponenty fungujú v požadovanom rozsahu:

- instance sú ready a prijímajú správny traffic,
- error rate a retry rate nevytvárajú regresiu,
- latency distribúcia zostáva v limite,
- CPU, memory, I/O, pools a queues nie sú saturované,
- dependencies a externé služby odpovedajú,
- logs a traces neukazujú nový failure pattern,
- autoscaling a health-control loops reagujú správne.

### Funkčná validácia

Overuje observable správanie systému:

- kritický request vráti správny obsah, nie iba status,
- side effect vznikne presne podľa kontraktu,
- event sa publikuje a spracuje bez duplicity alebo straty,
- authorization a tenant isolation fungujú,
- dáta zostanú konzistentné,
- retry, timeout a cancellation majú správny výsledok.

### Business validácia

Overuje, či zmena plní skutočný účel:

- používateľ dokončí kritický journey,
- conversion alebo completion rate sa nezhorší,
- payment, order alebo support workflow dosiahne správny koniec,
- počet manuálnych zásahov alebo chýb klesne podľa hypotézy,
- zmena nepoškodí relevantnú skupinu používateľov.

Technický pass môže existovať spolu s business failure. Systém môže vracať HTTP 200, ale zobrazovať nesprávnu cenu alebo znižovať completion rate.

## 6. Observability ako kompozitný oracle

V produkcii je oracle zvyčajne kombináciou signálov:

```text
metrics
+ logs
+ traces
+ structured events
+ synthetics
+ RUM
+ business KPIs
+ support/user feedback
```

Signály sa musia dať prepojiť s release dimenziami:

- artifact version alebo digest,
- deployment ID,
- region/zone,
- tenant alebo cohort,
- feature flag variant,
- request/trace ID,
- timestamp a rollout stage.

Bez týchto dimenzií sa zmena v metrike nedá spoľahlivo pripísať novému release-u.

Dôležitá je aj signal latency. Niektoré chyby sa prejavia okamžite, iné až po minútach alebo hodinách. Promotion window musí rešpektovať čas potrebný na zber dostatočného dôkazu.

## 7. Baseline a control group

Absolútna metrika bez kontextu môže byť zavádzajúca. Canary môže mať vyššiu latency preto, že dostal ťažších používateľov alebo iný región, nie preto, že nový kód je pomalší.

Porovnanie môže používať:

- **Súbežnú control group —** stará verzia beží v rovnakom čase a podobných podmienkach.
- **Historický baseline —** vhodný iba pri stabilnom a sezónne porovnateľnom workloade.
- **Pred/po okno —** jednoduché, ale citlivé na globálne zmeny trafficu.
- **Matched cohort —** skupiny sú vyrovnané podľa regiónu, tenant type, device alebo behavioru.
- **Synthetic baseline —** identický kontrolovaný journey sa spúšťa proti starej aj novej verzii.

Control group musí byť porovnateľná. Randomizácia alebo routing policy nesmie systematicky posielať odlišný workload do canary vetvy.

## 8. Synthetic monitoring

Synthetic monitoring pravidelne vykonáva kontrolovaný scenár z definovaného observation pointu. Je vhodný na overenie dostupnosti a kritických workflowov aj vtedy, keď momentálne nie je reálny používateľský traffic.

Príklady:

- DNS resolution a TLS handshake z vybraných regiónov,
- login test dedikovanou identitou,
- read-only API journey,
- vytvorenie a bezpečné zrušenie testovacej objednávky,
- overenie multi-region failover endpointu,
- kontrola externého identity alebo payment sandboxu.

Synthetic test potrebuje:

- **Izolovanú identitu —** credentials majú minimálne práva, rotáciu a audit.
- **Označené dáta —** test traffic a side effects sa dajú odlíšiť od reálnych používateľov.
- **Bezpečnú semantiku —** operácia je read-only, idempotentná alebo má spoľahlivý cleanup.
- **Relevantný path —** probe ide cez DNS, CDN, ingress a auth vrstvu, ktorú má overovať.
- **Deadline a alert policy —** failure má jasný dopad a ownera.
- **Rate control —** monitor neprekračuje quotas ani nevytvára vlastný incident.

Synthetic monitoring neposkytuje distribúciu reálnych zariadení, dát a behavioru. Preto dopĺňa RUM, nie ho nahrádza.

## 9. Real User Monitoring

Real User Monitoring meria skutočné používateľské sessions a klientské prostredie. Môže zachytiť problémy, ktoré server-side metrics nevidia, napríklad pomalý frontend, device-specific failure alebo regionálnu sieťovú degradáciu.

Typické signály:

- page load a interaction latency,
- frontend exceptions,
- Core Web Vitals,
- API latency z klienta,
- browser, device a region segmenty,
- journey completion a abandonment,
- feature variant alebo release cohort.

RUM má obmedzenia:

- **Sampling bias —** časť používateľov alebo zariadení nemusí byť zahrnutá.
- **Client blockers —** ad blockers alebo privacy controls môžu telemetry vypnúť.
- **Clock a network variability —** klientské meranie má vlastnú nepresnosť.
- **Cardinality —** nekontrolované dimensions zvyšujú náklady a znižujú použiteľnosť.
- **Privacy —** session data, URLs, input fields a replay môžu obsahovať osobné alebo citlivé informácie.
- **Consent a retention —** zber musí mať právny a organizačný základ.

RUM instrumentation musí minimalizovať dáta, redigovať citlivé polia a explicitne definovať sampling a retention.

## 10. Canary release

Canary release vystaví nový artifact obmedzenej časti trafficu. Primárnym účelom je znížiť technický blast radius a získať porovnateľný produkčný dôkaz pred plnou expozíciou.

Príklad rollout state machine:

```text
0 % — deployed, no user traffic
→ 1 % — initial health and synthetic checks
→ 5 % — technical comparison
→ 25 % — functional and business signal
→ 50 % — broader capacity validation
→ 100 % — full promotion
```

Percentá nie sú univerzálne. Každý krok musí definovať:

- minimálnu observation duration,
- minimálny počet requests alebo sessions,
- success a guardrail metrics,
- acceptable delta voči control,
- abort criteria,
- maximálnu signal latency,
- zodpovedného ownera,
- rollback alebo roll-forward akciu.

Promotion nemá byť iba timer. Ak nie je dostatok vzoriek alebo telemetry je neúplná, správny výsledok môže byť „inconclusive“, nie automatický pass.

## 11. Canary analysis a štatistická opatrnosť

Malá canary skupina môže mať vysokú variabilitu. Jedna chyba môže vyzerať ako veľký percentuálny nárast a zriedkavý failure sa nemusí objaviť vôbec.

Pri analýze sleduj:

- absolútny počet udalostí aj percentá,
- confidence alebo aspoň stabilitu v čase,
- porovnateľnosť cohort,
- viacnásobné metrics a riziko náhodného alarmu,
- sezónnosť a traffic shifts,
- sample size a minimálnu expozíciu,
- oneskorené business a async výsledky.

Automatická analýza má vedieť vrátiť:

- **Promote —** dôkaz spĺňa kritériá.
- **Rollback/abort —** kritický guardrail je porušený.
- **Pause —** treba viac času alebo manuálnu analýzu.
- **Inconclusive —** chýba dostatok dát alebo je telemetry neúplná.

## 12. Rollback a roll-forward safety

Rollback nie je bezpečný automaticky. Nová verzia mohla vykonať nevratnú migráciu, publikovať events alebo zmeniť dáta, ktorým stará verzia nerozumie.

Pred shift-right rolloutom over:

- databázovú backward compatibility,
- súbeh starej a novej verzie,
- event/schema compatibility,
- feature-flag behavior po návrate,
- cache a serialized-state compatibility,
- idempotency opakovanej deployment operácie,
- rollback time a jeho observation,
- roll-forward cestu, ak rollback nie je možný.

Rollback decision musí byť spojený s user impactom. Pri data corruption môže byť potrebné najprv zastaviť writes alebo izolovať feature, nie iba znížiť percento novej verzie.

## 13. Feature flags

Feature flag oddeľuje nasadenie kódu od aktivácie behavioru. Umožňuje postupný rollout, interné testovanie, cohort experiment a rýchle vypnutie konkrétnej capability bez redeployu.

Targeting môže byť podľa:

- interných používateľov,
- percenta stabilného hashovania identity,
- tenanta alebo customer tier,
- regiónu,
- capability alebo device typu,
- experimentálnej cohorty.

Riziká:

- **Stale flags —** dočasný branch v kóde zostane trvalý.
- **Kombinatorická explózia —** kombinácie flags vytvárajú netestovaný state space.
- **Nekonzistentní clients —** frontend, backend a mobile môžu vyhodnotiť flag rozdielne.
- **Flag-service dependency —** outage alebo stale cache mení behavior.
- **Security misuse —** flag nesmie byť jedinou authorization kontrolou.
- **Auditability —** zmena flagu môže byť produkčný release a potrebuje history a approval.

Každý dočasný flag potrebuje ownera, intended default, fail-open/fail-closed semantics, removal criteria a deadline.

## 14. Dark launch

Dark launch nasadí capability do produkčného prostredia bez jej sprístupnenia bežným používateľom. Môže overiť startup, dependency wiring, cache warming, schema compatibility alebo background spracovanie.

Dark launch neoveruje celý user outcome, pretože reálna interakcia ešte nie je aktívna. Je to medzikrok medzi deployment verification a release validation.

Riziká:

- skrytý kód stále môže spotrebúvať resources,
- background jobs môžu vytvárať side effects,
- neaktívna cesta nemusí mať reálny traffic mix,
- feature môže neúmyselne uniknúť cez API alebo permissions.

## 15. Shadow traffic

Shadow traffic kopíruje produkčné requests do novej verzie bez použitia jej response pre používateľa. Umožňuje porovnať compatibility, výkon a output pri realistickom request mixe.

Bezpečnostné požiadavky:

- shadow path nesmie vykonať reálne externé side effects,
- writes musia byť izolované, simulované alebo smerované do disposable state,
- secrets a osobné dáta musia byť minimalizované a chránené,
- downstream kapacita musí počítať s duplicitným loadom,
- response diff musí normalizovať nondeterministické polia,
- shadow timeout nesmie spomaliť primárny request,
- sampling a retention musia byť explicitné.

Shadow behavior nie je úplne identický s primárnym trafficom. Timing, cache state a side-effect isolation môžu zmeniť výsledok.

## 16. Traffic replay

Production-derived traffic možno replayovať v izolovanom prostredí alebo počas kontrolovaného testu. Replay poskytuje realistickejšiu distribúciu requestov než ručne vytvorený scenár, ale vyžaduje dátový lifecycle.

Kontroluj:

- anonymizáciu a re-identification riziko,
- odstránenie tokens, cookies a secrets,
- zachovanie alebo modelovanie časovej distribúcie,
- referential integrity medzi requestmi,
- side effects a externé calls,
- retention a prístupové práva,
- právny a organizačný súhlas,
- verziu capture a replay toolu.

Replay nie je dôkaz identického produkčného behavioru. Neobsahuje vždy server-side state, klientské rozhodovanie alebo reálne concurrency interleavings.

## 17. A/B testing

A/B test meria produktovú alebo behaviorálnu hypotézu medzi experimentálnou a kontrolnou skupinou. Canary primárne riadi technické release riziko; A/B test primárne skúma, či variant zlepšuje definovaný outcome.

Experiment contract obsahuje:

- hypotézu,
- unit of randomization,
- primary metric,
- guardrail metrics,
- eligibility a exclusion rules,
- sample-size alebo duration plán,
- exposure consistency,
- novelty a seasonality riziká,
- stopping a decision rules,
- privacy a consent požiadavky.

Nevyberaj víťaza priebežným sledovaním náhodného výkyvu bez vopred definovaného rozhodovacieho modelu. Technický guardrail môže experiment zastaviť aj vtedy, keď business metric krátkodobo rastie.

## 18. Progressive delivery

Progressive delivery automatizuje kontrolovanú expozíciu a rozhodovanie:

```text
immutable artifact
→ obmedzená expozícia
→ zber a analýza signálov
→ policy rozhodnutie
→ širšia expozícia alebo návrat
```

Automatizácia percent nie je sama osebe vyspelá progressive delivery. Systém potrebuje:

- porovnateľnú control group,
- kvalitné SLI a business metrics,
- ochranu pred neúplnou telemetry,
- jasné inconclusive správanie,
- audit rozhodnutí,
- override s risk ownerom,
- overený rollback/roll-forward,
- ochranu pred súbežnými nezávislými zmenami, ktoré komplikujú atribúciu.

## 19. Error budgets a release policy

Error budget spája reliability cieľ s delivery rozhodovaním. Ak služba spotrebúva budget príliš rýchlo, nový rollout môže zväčšiť riziko alebo sťažiť diagnostiku.

Príklad policy:

```text
budget healthy
→ štandardný automatizovaný rollout

budget pod warning hranicou
→ menší canary a dlhšie observation window

budget rýchlo klesá alebo je vyčerpaný
→ release freeze, iba reliability alebo urgentné zmeny
```

Error budget nie je trest ani izolovaná metrika. Musí byť založený na relevantnom SLI a interpretovaný spolu s business prioritou, incidentom a change riskom.

## 20. Resilience validation

Shift-right môže overovať reálne control loops a degradation behavior:

- retry a timeout interakciu,
- circuit breaker,
- admission control a load shedding,
- failover medzi instances, zones alebo regiónmi,
- autoscaling latency a oscillation,
- queue backlog recovery,
- dependency degradation,
- certificate alebo credential rotation,
- graceful shutdown a connection draining.

Takáto validácia sa prekrýva s chaos testingom. Potrebuje explicitnú steady-state hypotézu, blast radius, abort criteria, observation plan a recovery dôkaz.

## 21. Produkčná verification verzus validation

Aj v produkcii je užitočné oddeliť verification a validation.

- **Produkčná verification —** správny artifact je nasadený, config a routing zodpovedajú plánu, policy je enforced a technické kontrakty platia.
- **Produkčná validation —** používatelia dosahujú zamýšľaný outcome a systém zostáva prevádzkovo prijateľný pri reálnom workloade.

Príklad:

```text
Verification: 5 % trafficu ide na digest X a authorization policy je aktívna.
Validation: checkout completion a payment correctness sa nezhoršili.
```

Obe vrstvy potrebujú samostatné oracles a môžu mať odlišnú signal latency.

## 22. Privacy, bezpečnosť a etika

Shift-right pracuje s produkčnými dátami a ľuďmi. Experiment alebo telemetry nesmie prekročiť účel, na ktorý má organizácia oprávnenie.

Kontroluj:

- data minimization,
- osobné a citlivé polia,
- consent alebo právny základ,
- sampling a retention,
- access control k raw telemetry,
- redaction v logs a traces,
- session replay masking,
- oddelenie test identities,
- zákaz nebezpečných experimentov na zraniteľných skupinách,
- audit feature targetingu a variantov.

„Produkcia už dáta má“ nie je oprávnenie kopírovať ich do ďalšieho experimentálneho systému alebo dlhodobo uchovávať detailný replay.

## 23. False rollback a false promotion

Rozhodovací systém môže urobiť dva typy závažnej chyby:

- **False rollback —** zdravá zmena je zastavená pre šum, neporovnateľnú cohortu alebo chybnú telemetry.
- **False promotion —** chybná zmena pokračuje pre slabý oracle, malú vzorku alebo oneskorený signal.

Ochrany:

- kombinovať absolútne limity a delta voči control,
- používať viac nezávislých signálov,
- definovať minimálnu vzorku a observation duration,
- zastaviť promotion pri neúplnej telemetry,
- merať false decision rate,
- uchovať evidence pre spätnú analýzu,
- kalibrovať rules na historických rolloutoch.

## 24. Feedback späť doľava

Shift-right bez uzavretej learning slučky je iba monitoring. Každý významný produkčný poznatok má viesť k trvalému zlepšeniu.

Možné výsledky:

- nový regression alebo contract test,
- spresnenie acceptance criteria,
- nový SLI alebo business oracle,
- lepšia telemetry a failure artifact,
- zmena timeout/retry/backpressure policy,
- bezpečnejší platformový default,
- nová IaC alebo security policy,
- nový chaos experiment,
- zmena rollout guardrailu,
- aktualizovaný runbook a recovery drill.

```text
production evidence
→ root-cause learning
→ backlog a owner
→ skoršia kontrola alebo bezpečný default
→ overenie v ďalšom release
```

Cieľom nie je iba opraviť konkrétny incident, ale zachytiť triedu failure v najnižšej spoľahlivej vrstve.

## 25. Metriky účinnosti

Sleduj, či shift-right skracuje expozíciu a zlepšuje učenie:

- **Release-to-validation time —** čas od nasadenia po dostatočný dôkaz prijateľnosti.
- **Mean exposure before detection —** koľko trafficu alebo používateľov bolo vystavených pred detekciou chyby.
- **Canary abort/rollback rate —** koľko rolloutov bolo zastavených a z akého dôvodu.
- **False rollback rate —** zdravé zmeny zastavené nespoľahlivým signálom.
- **False promotion/escape rate —** chyby, ktoré prešli cez progressive gate.
- **Synthetic a RUM coverage —** ktoré kritické journeys a segmenty majú použiteľný signal.
- **Telemetry completeness —** percento requests alebo rolloutov s artifact/cohort identitou.
- **Stale feature flags —** počet a vek dočasných flags po deadline.
- **Feedback closure rate —** podiel produkčných poznatkov premenených na test, policy alebo platformový fix.
- **Rollback readiness —** čas a úspešnosť reálne overených rollback/roll-forward postupov.

## 26. Diagnostický postup pri zlyhanom rolloute

1. **Zastav expozíciu —** podľa abort policy pause-ni rollout, vypni flag alebo izoluj cohortu.
2. **Over atribúciu —** artifact, config, cohort, región, čas a súbežné zmeny.
3. **Skontroluj signal quality —** chýbajúce dáta, sampling, control comparability a alert rule.
4. **Rozlíš typ failure —** technický, funkčný, business, dependency alebo telemetry failure.
5. **Urči user impact —** počet používateľov, trvanie, dáta a finančný/prevádzkový dopad.
6. **Vyber recovery —** rollback, roll-forward, flag-off, traffic shift alebo write freeze.
7. **Over recovery —** metrics, synthetics a business stav musia potvrdiť návrat.
8. **Uchovaj evidence —** logs, traces, rollout decisions, config a timestamps.
9. **Vykonaj root-cause analýzu —** zahŕňa aj prečo guardrail zlyhal alebo uspel neskoro.
10. **Uzavri learning loop —** vytvor ownera, test/policy zmenu a overenie v ďalšom release.

## 27. Typické anti-patterny

### „Testujeme až v produkcii“

Chýbajú skoré checks a používatelia znášajú náklady bežných chýb. Shift-right má overovať zostávajúce predpoklady, nie základnú syntax alebo unit logiku.

### Dashboard bez rozhodnutia

Metriky existujú, ale nie je definované, čo rollout zastaví, kto reaguje a aká akcia nasleduje.

### Canary bez control group

Nie je jasné, či delta vznikla novou verziou alebo globálnou zmenou workloadu.

### Promotion iba podľa času

Rollout pokračuje aj bez dostatočnej vzorky alebo pri neúplnej telemetry.

### Rollback bez compatibility dôkazu

Návrat starej verzie môže poškodiť dáta alebo zlyhať na novej schéme.

### Feature flag bez lifecycle

Dočasná vetva sa stane trvalou, zvyšuje state space a komplikuje incidenty.

### Shadow traffic s reálnymi side effects

Kópia requestu môže vytvoriť duplicitnú platbu, správu alebo zápis.

### RUM bez privacy dizajnu

Telemetry alebo session replay zachytáva citlivé dáta bez minimalizácie, retention a prístupových pravidiel.

### Produkčný experiment bez inconclusive stavu

Systém automaticky promovuje alebo rollbackuje aj vtedy, keď nemá dostatok dôkazov.

## 28. Praktický rozhodovací rámec

Pred shift-right validáciou odpovedz:

1. Ktorý predpoklad nemožno dostatočne overiť pred produkciou?
2. Aký technický, funkčný alebo business oracle ho potvrdí?
3. Aká je artifact, config a cohort identity?
4. Aká control group alebo baseline je porovnateľná?
5. Aký je maximálny blast radius a exposure duration?
6. Aká je signal latency a minimálna vzorka?
7. Aké sú promotion, pause, abort a inconclusive criteria?
8. Je rollback kompatibilný s dátami a súbežnými verziami?
9. Aký je roll-forward plán?
10. Obsahuje test side effects alebo citlivé dáta?
11. Ako sa chránia credentials, privacy a retention?
12. Kto sleduje rollout a kto má rozhodovaciu právomoc?
13. Ako sa uchová evidence a audit trail?
14. Aký poznatok sa má presunúť späť do shift-left kontroly?

## 29. Kontrolný checklist

Pred produkčným rolloutom over:

- artifact a configuration provenance sú jednoznačné,
- telemetry obsahuje release a cohort dimensions,
- control group je porovnateľná,
- synthetics používajú bezpečné identity a dáta,
- RUM rešpektuje privacy a sampling kontrakt,
- rollout má minimálnu vzorku aj observation duration,
- telemetry failure neznamená pass,
- existuje inconclusive stav,
- feature flags majú fail semantics a removal deadline,
- shadow traffic nemá reálne side effects,
- rollback/roll-forward bol testovaný,
- database a event schemas sú kompatibilné,
- abort criteria a owner sú explicitné,
- evidence sa uchováva,
- learning sa vracia do požiadaviek, testov alebo policies.

## 30. Kontrolné otázky

1. Čo shift-right dopĺňa a čo nenahrádza?
2. Prečo deployment success nie je production validation?
3. Aké tri vrstvy produkčnej validácie treba rozlišovať?
4. Prečo musí telemetry obsahovať artifact a cohort identitu?
5. Aký je rozdiel medzi synthetic monitoringom a RUM?
6. Kedy je historický baseline slabší než súbežná control group?
7. Aké výsledky okrem promote/rollback má mať canary analysis?
8. Prečo rollback nemusí byť bezpečný?
9. Ako feature flags oddeľujú deployment od release a aké vytvárajú riziká?
10. Ako bezpečne používať shadow traffic?
11. Aký je rozdiel medzi canary release a A/B testom?
12. Ako error budget mení release policy?
13. Čo je false rollback a false promotion?
14. Ako privacy ovplyvňuje RUM, replay a experimenty?
15. Ako sa produkčný poznatok premení na trvalú shift-left kontrolu?

## Summary

Shift-right je riadený proces získavania produkčného dôkazu cez kontrolovanú expozíciu, observability, porovnateľnú baseline a bezpečné rollout rozhodnutia. Zahŕňa synthetics, RUM, canary, feature flags, dark launch, shadow traffic, A/B experimenty, progressive delivery a resilience validation. Bez artifact identity, signal-quality kontroly, blast-radius limitu, rollback kompatibility, privacy a learning closure sa z neho stáva iba riskantné testovanie na používateľoch. Jeho výsledok sa musí vracať do požiadaviek, testov, policies a platformových defaults.

## Glossary impact

Relevantné pojmy: shift-right, production validation, controlled exposure, canary release, control group, cohort, feature flag, dark launch, shadow traffic, traffic replay, A/B testing, progressive delivery, Real User Monitoring, guardrail metric, abort criterion, inconclusive result, false rollback a false promotion.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shift-left](shift-left.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Chaos testing →](chaos-testing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->