# End-to-end a acceptance tests

End-to-end test a acceptance test odpovedajú na dve odlišné otázky. E2E opisuje šírku vykonanej technickej cesty; acceptance opisuje, či pozorovaný výsledok spĺňa dohodnutú používateľskú, business alebo prevádzkovú potrebu.

```text
E2E scope
→ cez ktoré reálne boundaries test prešiel?

Acceptance purpose
→ aké kritérium prijateľnosti tento dôkaz podporuje?
```

Jeden test môže byť súčasne E2E aj acceptance testom, ale nie každý acceptance test musí používať celý systém a nie každý E2E test poskytuje dostatočný dôkaz business prijateľnosti.

## 1. Mentálny model: journey, boundaries, oracle a rozhodnutie

Užitočný E2E alebo acceptance test musí explicitne definovať štyri veci:

- **journey —** používateľský alebo systémový tok od počiatočného stavu po pozorovateľný výsledok,
- **boundaries —** procesy, služby, siete, identity, storage a externé systémy, ktoré sú v teste reálne zahrnuté,
- **oracle —** pravidlo, ktoré rozhodne, či výsledok spĺňa technický aj business kontrakt,
- **decision —** rozhodnutie, ktoré test podporuje, napríklad merge, deployment, release alebo prevádzkové prijatie.

Bez tejto štvorice vzniká drahý systémový scenár, ktorého failure sa ťažko interpretuje a ktorého zelený výsledok nemusí dokazovať nič podstatné.

## 2. End-to-end test

E2E test vykonáva tok cez viac produkčne relevantných vrstiev. Typický webový journey môže vyzerať takto:

```text
browser
→ DNS a TLS
→ reverse proxy alebo load balancer
→ frontend
→ API
→ databáza
→ message broker
→ worker
→ externý sandbox
→ výsledok v UI alebo verejnom API
```

Rozsah musí byť pomenovaný presne. Test, ktorý používa reálny frontend a API, ale fake databázu a stub externého providera, je stále hodnotný systémový test, no nedokazuje produkčné SQL, transakčné ani providerové správanie.

## 3. Acceptance test

Acceptance test overuje konkrétne kritérium prijateľnosti. Kritérium má vyjadrovať pozorovateľný výsledok, nie interný spôsob implementácie.

```gherkin
Given zákazník má aktívny účet a produkt je dostupný
When odošle objednávku s unikátnym idempotency key
Then objednávka je prijatá presne raz
And skladová rezervácia je vytvorená
And zákazník vidí potvrdenie
And auditná stopa obsahuje identitu a correlation ID
```

Acceptance test môže byť vykonaný na unit, API, component, E2E alebo manuálnej úrovni. Rozhodujúca je väzba na requirement a acceptance oracle, nie použitý framework.

## 4. E2E verzus acceptance

| Otázka | E2E test | Acceptance test |
|---|---|---|
| Primárny význam | technický scope toku | prijateľnosť výsledku |
| Typický oracle | systémový stav a verejné rozhranie | business alebo prevádzkové kritérium |
| Typická cena | vysoká | závisí od scope |
| Typický vlastník | engineering alebo QA | product, business, operations a engineering |
| Hlavné riziko | wiring, deployment a cross-boundary failure | vytvorenie nesprávneho alebo neprevádzkovateľného riešenia |

Silná stratégia často implementuje väčšinu acceptance pravidiel na nižších vrstvách a iba kritické journeys opakuje cez E2E cestu.

## 5. User Acceptance Testing

User Acceptance Testing, skrátene UAT, poskytuje dôkaz, že systém zodpovedá reálnemu používateľskému alebo organizačnému procesu. Vykonáva ho alebo formálne schvaľuje business používateľ, product owner, doménový expert alebo reprezentatívny stakeholder.

UAT môže overovať napríklad:

- **workflow fit —** kroky zodpovedajú reálnej práci a nevytvárajú neudržateľné obchádzky,
- **business rules —** výpočty, rozhodnutia a výnimky zodpovedajú doménovým pravidlám,
- **reporting —** výsledné výstupy majú správny význam, úplnosť a auditnú stopu,
- **usability —** používateľ vie dosiahnuť cieľ bez neprimeranej podpory alebo nejasných krokov,
- **regulačné očakávania —** workflow uchováva potrebné schválenia, evidenciu a segregation of duties.

UAT nemá byť náhradou technickej QA. Stakeholder nemá manuálne objavovať chyby schémy, validácie, authorization alebo retry logiky, ktoré mali byť automatizované skôr.

## 6. Operational Acceptance Testing

Operational Acceptance Testing, skrátene OAT, overuje, či je systém prevádzkovateľný počas normálnej prevádzky aj failure scenárov.

OAT zahŕňa najmä:

- **observability —** logs, metrics, traces, dashboards a alerts umožňujú odhaliť a lokalizovať problém,
- **deployment —** rollout používa známy artifact, má health gates a neporušuje kompatibilitu,
- **rollback alebo roll-forward —** recovery cesta je vykonateľná v požadovanom čase,
- **backup a restore —** dáta sa dajú obnoviť a výsledok je použiteľný,
- **failover —** redundantná cesta prevezme workload bez neprijateľného dopadu,
- **capacity —** systém zvláda očakávané zaťaženie s definovanou rezervou,
- **access a support —** on-call rola má oprávnenia, runbooky a jasný escalation path,
- **maintenance —** patching, certificate rotation a dependency lifecycle majú bezpečný postup.

Funkčne správna aplikácia bez použiteľného alertingu, recovery a ownershipu nie je pripravená na produkčné prijatie.

## 7. Výber kritických journeys

E2E suite nemá kopírovať všetky kombinácie business logiky. Má chrániť malé množstvo ciest, ktorých zlyhanie má vysoký dopad alebo ktoré prechádzajú rizikovými boundaries.

Kandidát journey posudzuj podľa:

1. business kritickosti,
2. finančného, bezpečnostného alebo regulačného dopadu,
3. frekvencie použitia,
4. počtu integračných boundaries,
5. historickej poruchovosti,
6. zložitosti recovery,
7. možnosti zachytiť rovnaké riziko lacnejším testom.

Typické kritické journeys sú login s federovanou identitou, checkout a platba, tenant isolation, vytvorenie a asynchrónne spracovanie objednávky, reset hesla, administratívne schválenie, compliance export a disaster-recovery tok.

## 8. Journey inventory a coverage mapa

Pre každý kritický journey eviduj:

```text
journey ID
→ business owner
→ vstupný stav
→ kroky a boundaries
→ očakávané side effects
→ oracle
→ environment
→ trigger
→ blocking/advisory význam
→ failure artifacts
```

Takáto mapa odhaľuje duplicitu, nepokryté kritické cesty a scenáre, ktoré sa označujú ako E2E, hoci obchádzajú rozhodujúcu vrstvu.

## 9. Black-box, gray-box a white-box systémové testy

### Black-box E2E

Black-box test používa iba verejné rozhrania a pozorovateľné výsledky. Poskytuje vysokú fidelity používateľskej cesty, ale setup a diagnostika bývajú drahšie.

### Gray-box E2E

Gray-box test vykonáva verejný journey, no používa kontrolované interné rozhranie na prípravu dát, zrýchlenie času alebo získanie diagnostického stavu. Tento kompromis je vhodný, pokiaľ helper neobchádza behavior, ktorý test deklaruje ako predmet dôkazu.

### White-box systémový test

White-box test pozná interné komponenty a môže overovať koordináciu, interné events alebo stav. Je užitočný pre technickú verifikáciu, no jeho assertiony nemajú byť zamieňané za používateľský acceptance dôkaz.

## 10. Artifact a environment identity

E2E výsledok je dôveryhodný iba vtedy, keď je známe, čo presne bolo testované. Test run má zaznamenať:

- source commit alebo release tag,
- immutable artifact digest,
- deployment manifest alebo environment revision,
- databázovú schema verziu,
- feature-flag snapshot,
- kritické dependency versions,
- browser, runtime a test framework version,
- čas a identity test runu.

Bez provenance môže zelený test patriť inému buildu než artifact, ktorý bol neskôr nasadený.

## 11. Environment fidelity

Produkčne podobné prostredie nemusí mať identickú kapacitu, ale musí zachovať vlastnosti relevantné pre testované riziko.

Pre identity journey je kritická rovnaká federácia, token semantics a authorization policy. Pre databázový tok je kritická kompatibilná engine verzia, constraints a migration state. Pre deployment test sú rozhodujúce rovnaké image, entrypoint, probes, proxy a network policy.

Fidelity má byť zdokumentovaná ako explicitná matica:

```text
vlastnosť
→ produkcia
→ test environment
→ rozdiel
→ riziko rozdielu
→ kompenzačný dôkaz
```

## 12. Environment lifecycle a ownership

E2E prostredie môže byť:

- **ephemeral per change —** poskytuje silnú izoláciu, ale startup a provisioning zvyšujú feedback time,
- **pooled ephemeral —** zrýchľuje testy, no vyžaduje reset a lease mechanizmus,
- **shared persistent —** znižuje provisioning cost, ale zvyšuje drift, contention a ownership problémy,
- **production canary —** poskytuje najvyššiu fidelity, ale potrebuje blast-radius guardrails.

Každý model musí definovať provision, readiness, exclusive alebo shared use, reset, cleanup, retention artifacts a ownera pri zlyhaní infraštruktúry.

## 13. Test data contract

E2E dáta musia byť identifikovateľné, izolované, opakovateľne vytvoriteľné a bezpečne odstrániteľné. Každý run má používať unikátny namespace, tenant, correlation prefix alebo resource tag.

Test data nesmú obsahovať reálne osobné alebo produkčné secrets. Pri potrebe realistických dát sa používa syntetický alebo riadne anonymizovaný dataset s kontrolou reidentifikačného rizika.

## 14. Príprava stavu bez obchádzania testu

Predpríprava cez verejné API poskytuje vyššiu fidelity, ale môže výrazne predĺžiť test. Gray-box fixture API alebo priama databázová príprava môže byť prijateľná, pokiaľ:

1. fixture nevytvára nemožný stav,
2. rešpektuje relevantné invariants,
3. neobchádza vrstvu, ktorú journey testuje,
4. je versioned spolu s aplikáciou,
5. má jasný cleanup a bezpečnostnú hranicu.

Ak test overuje vytvorenie objednávky, priame vloženie finálnej objednávky do databázy by odstránilo hlavný predmet testu.

## 15. Stateful a destructive journeys

Testy, ktoré vykonávajú platbu, delete, email, export alebo infraštruktúrnu mutation, potrebujú kontrolovaný sandbox a jednoznačný cleanup. Destruktívne kroky musia používať test-only accounts, resource tags a environment allowlist.

Bezpečnostná podmienka má zlyhať zatvorene:

```text
ak environment identity nie je explicitne testovacia
→ destructive journey sa nespustí
```

## 16. Synchronné a asynchrónne oracles

Synchronný tok môže overiť okamžitú response a stav. Asynchrónny journey potrebuje eventual-consistency kontrakt:

```text
udalosť sa má prejaviť do 30 sekúnd
→ polluj pozorovateľnú podmienku
→ používaj bounded interval a deadline
→ pri failure zachovaj posledný stav a correlation ID
```

Pevný `sleep` buď čaká zbytočne dlho, alebo zlyhá pri pomalšom, ale stále platnom spracovaní. Condition-based waiting dáva rýchlejší úspech a lepší diagnostický dôkaz.

## 17. Čas ako testovateľná dependency

Workflow s expiry, scheduled jobom alebo retry delay nemá čakať reálne hodiny. Použi controllable clock, test-only time advancement alebo kratší explicitný environment contract.

Časová manipulácia nesmie obísť scheduler, TTL alebo persistence behavior, ktoré sú predmetom testu. Preto treba pomenovať, ktorá časová vrstva je simulovaná a ktorá ostáva reálna.

## 18. Browser automation

UI test má používať selectors založené na stabilnom používateľskom kontrakte:

- semantic role,
- accessible name,
- form label,
- explicitný test ID tam, kde význam nemožno vyjadriť semanticky.

Krehké selectors podľa generovanej CSS class, DOM pozície alebo vizuálnej hierarchie viažu test na implementáciu. Test musí čakať na pozorovateľný stav aplikácie, nie na pevný čas.

## 19. Page, screen a domain models

Page object centralizuje selectors a technické interakcie. Domain-oriented test API navyše vyjadruje používateľský zámer:

```text
customer.sign_in()
customer.place_order(product)
customer.wait_for_confirmation()
```

Abstrakcia má skrývať mechanický detail, nie business význam. Page object, ktorý obsahuje rozsiahlu rozhodovaciu logiku alebo automaticky prehltne failures, sťažuje diagnostiku a vytvára druhú implementáciu aplikácie.

## 20. Service virtualization a externé systémy

Externé závislosti možno nahradiť payment sandboxom, email catcherom, fake identity providerom alebo protokolovým simulátorom. Tým sa zlepší determinism a kontrola failure scenárov, ale zníži sa fidelity voči reálnemu providerovi.

Kritická integrácia preto potrebuje kombináciu:

- contract testu,
- deterministického component alebo E2E testu so simulátorom,
- periodického testu proti oficiálnemu sandboxu,
- produkčného synthetic signálu a monitoring-u skutočných volaní.

## 21. Acceptance criteria a oracle design

Silné acceptance kritérium je pozorovateľné, jednoznačné, merateľné a viazané na výsledok.

Slabé:

```text
Systém má byť používateľsky prívetivý.
```

Silnejšie:

```text
Používateľ s platnými údajmi dokončí registráciu bez podpory,
do 2 minút dostane potvrdenie a vznikne jedna auditovaná identita.
```

Automatizovaný oracle môže overiť čas, potvrdenie a identitu. Skutočnú zrozumiteľnosť workflowu môže stále potrebovať usability validation s používateľmi.

## 22. Business a technické assertions

Journey nemá končiť assertionom „stránka sa zobrazila“. Pre kritický tok overuj primeranú kombináciu:

- verejný výsledok pre používateľa,
- business invariant,
- persistentný stav,
- počet a identitu side effects,
- authorization a tenant scope,
- event alebo audit trail,
- observability metadata,
- neprítomnosť zakázaného vedľajšieho efektu.

Assertions musia zostať na správnej hranici. Priame čítanie každej internej tabuľky môže urobiť E2E test krehkým voči bezpečnému refaktoringu.

## 23. BDD a executable specification

Behavior-Driven Development používa scenáre `Given`, `When`, `Then` na discovery a zdieľaný jazyk medzi productom, QA a engineeringom. Hodnota vzniká v objasnení pravidiel, príkladov a výnimiek, nie v samotnej Gherkin syntaxi.

Anti-patternom je scenár, ktorý opisuje každé kliknutie, kopíruje implementáciu alebo obsahuje desiatky technických krokov. Taký text nie je stabilnou business špecifikáciou.

## 24. Segmentácia suite podľa rozhodnutia

E2E testy rozdeľ podľa rozhodnutia a časového rozpočtu:

- **PR critical path —** krátka blocking sada chráni najdôležitejšie journeys pred merge,
- **deployment smoke —** overí nový artifact a základný wiring po deploymente,
- **full regression —** širšia sada pokrýva významné historické riziká,
- **compatibility matrix —** cielené behy overujú browser, device alebo podporovanú verziu,
- **pre-release acceptance —** poskytuje formálny dôkaz pre release rozhodnutie,
- **scheduled resilience journey —** overuje dlhšie recovery alebo cross-system scenáre.

Každá skupina musí mať trigger, time budget, ownera, blocking význam a retention artifacts.

## 25. Parallelizácia a sharding

E2E suite sa môže deliť podľa historického trvania alebo journey skupín. Paralelizácia vyžaduje izolované tenants, účty, queues, files, ports a resource names.

Riziká zahŕňajú spoločné rate limits, environment saturation, poradie dependent tests a cleanup collision. Ak paralelizácia sama vytvára náhodné failures, test suite prestáva merať aplikáciu a začína merať vlastnú contention chybu.

## 26. Failure artifacts

Pri každom failure uchovaj minimálne:

- presný test a krok,
- screenshot alebo relevantný response payload,
- browser trace, video alebo network archive podľa typu testu,
- console output,
- request, correlation a trace ID,
- server-side logs a event timeline,
- artifact digest a environment revision,
- test-data identifiers,
- timestampy v jednotnej timezone,
- posledný pozorovaný stav pri polling-u.

Artifacts musia byť redigované, aby neobsahovali passwords, tokens alebo osobné údaje.

## 27. Diagnostika failure podľa observation pointu

Pri failure postupuj od symptómu k jednotlivým observation points:

```text
runner a test framework
→ browser alebo klient
→ DNS/TLS/network
→ proxy a routing
→ application logs a traces
→ databáza a broker
→ externý sandbox
→ business state
```

Najprv rozlíš test-code failure, environment failure a product failure. Iba product failure má priamo blokovať release bez potreby ďalšej infraštruktúrnej interpretácie; environment failure však stále potrebuje ownera a opravu, inak gate nie je spoľahlivý.

## 28. Flaky výsledok a rerun semantics

Rerun je diagnostický nástroj, nie spôsob, ako premeniť červený výsledok na zelený.

Systém má evidovať:

- first-attempt result,
- počet pokusov,
- výsledok každého pokusu,
- failure signature,
- environment a worker identity,
- klasifikáciu product/test/environment,
- issue a ownera pri quarantine.

Blocking rozhodnutie má používať explicitnú policy. Napríklad známy quarantined test môže byť advisory, ale nový neznámy failure nesmie byť automaticky ignorovaný po úspešnom rerune.

## 29. Produkčná validation

Niektoré vlastnosti možno dôveryhodne potvrdiť až s reálnou federáciou identity, traffic distribúciou, regionálnou latency, provider quotas alebo používateľským správaním.

Používajú sa:

- synthetic transactions,
- canary releases,
- feature flags,
- SLI/SLO guardrails,
- real-user monitoring,
- business metrics,
- kontrolované experimenty.

Produkčný test musí používať bezpečné test data, malý blast radius, kill switch a jasný rollback alebo abort mechanizmus.

## 30. Operational acceptance príklad

Pred release payment služby môže OAT scenár vyzerať takto:

```text
1. nasadiť konkrétny artifact digest,
2. vykonať syntetickú autorizáciu v sandboxe,
3. potvrdiť trace cez proxy, API a worker,
4. simulovať timeout providera,
5. overiť bounded retry bez duplicity,
6. skontrolovať alert a runbook link,
7. vykonať rollback,
8. potvrdiť obnovu služby a konzistenciu dát.
```

Taký test neposudzuje iba funkciu, ale aj prevádzkovú pripravenosť a recovery.

## 31. Časté anti-patterny

### Každá kombinácia cez browser

Kombinatorická business logika patrí do unit, property-based alebo API testov. E2E má chrániť reprezentatívne kritické cesty.

### Zelený test bez artifact provenance

Nie je jasné, či sa testoval build, ktorý sa bude releasovať.

### Shared admin account

Paralelné testy si menia permissions a stav, čo vytvára order dependency a bezpečnostné riziko.

### Priama databázová skratka cez predmet testu

Fixture obíde validation alebo workflow, ktorý mal journey dokázať.

### Pevné sleeps

Test je pomalý a zároveň flaky, pretože nečaká na konkrétnu podmienku.

### UAT až na konci projektu

Business neistota sa odhalí neskoro. Acceptance examples majú vznikať už počas discovery a refinementu.

### Rerun-until-green

Prvý failure sa stratí a suite prestane poskytovať dôveryhodný gate.

## 32. Diagnostický workflow

1. Identifikuj testovaný artifact, environment revision a feature flags.
2. Potvrď, že setup vytvoril očakávaný počiatočný stav.
3. Lokalizuj prvý odlišný observation point, nie posledný viditeľný symptóm.
4. Koreluj klientsky čas, request ID, trace a serverové events.
5. Rozlíš product, test-code, data a environment failure.
6. Over eventual-consistency deadline a posledný pozorovaný stav.
7. Reprodukuj najmenším scope-om, ktorý zachováva failure boundary.
8. Zachovaj artifacts pred cleanupom environmentu.
9. Oprav root cause alebo dočasne quarantine s ownerom a deadline.
10. Po oprave over first-attempt pass a odstráň dočasnú výnimku.

## 33. Prevádzkový checklist

Pred zaradením E2E alebo acceptance testu do gate over:

- journey a acceptance criterion sú explicitné,
- scope a nahradené dependencies sú zdokumentované,
- artifact a environment identity sa ukladajú,
- setup nevytvára nemožný stav,
- test data sú izolované a bezpečné,
- čakanie je condition-based a bounded,
- assertions overujú business aj technický výsledok,
- failure artifacts sú dostatočné a redigované,
- test je samostatne spustiteľný a paralelizovateľný alebo má deklarovaný lock,
- rerun a quarantine policy sú explicitné,
- test má ownera, time budget a jasný rozhodovací význam.

## 34. Zhrnutie

E2E test poskytuje dôkaz o spolupráci produkčne relevantných boundaries. Acceptance test poskytuje dôkaz, že výsledok spĺňa dohodnutú potrebu. Silná stratégia vyberá iba kritické journeys, viaže ich na immutable artifact a známe prostredie, kontroluje test data a čas, zhromažďuje diagnostické artifacts a dopĺňa predprodukčné dôkazy bezpečnou produkčnou validation.

## 35. Kontrolné otázky

1. Aký je rozdiel medzi E2E scope-om a acceptance účelom?
2. Prečo acceptance test nemusí byť E2E testom?
3. Ktoré kritériá určujú výber kritického journey?
4. Čo musí obsahovať artifact a environment provenance?
5. Kedy je gray-box setup legitímny a kedy obchádza predmet testu?
6. Ako sa testuje eventual consistency bez pevného sleepu?
7. Aký je rozdiel medzi UAT a Operational Acceptance Testing?
8. Ako service virtualization mení fidelity?
9. Ktoré artifacts sú potrebné pri E2E failure?
10. Prečo rerun-until-green ničí dôveryhodnosť gate-u?
11. Ako bezpečne vykonávať produkčný synthetic journey?
12. Ako odlíšiš product failure od environment failure?

## Glossary impact

Relevantné pojmy: end-to-end test, acceptance test, User Acceptance Testing, Operational Acceptance Testing, critical journey, black-box test, gray-box test, environment fidelity, artifact provenance, eventual consistency, service virtualization, synthetic transaction, failure artifact a quarantine.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Contract a API tests](contract-and-api-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Smoke a regression tests →](smoke-and-regression-tests.md)
<!-- KNOWLEDGE-NAVIGATION:END -->