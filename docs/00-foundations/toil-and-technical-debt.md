# Toil and Technical Debt

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Automation Mindset](automation-mindset.md), [Continuous Improvement](continuous-improvement.md)
- Súvisiace témy: SRE, automation, incident management, platform engineering, prioritization

## 1. Definícia

**Toil** je opakovaná prevádzková práca, ktorá je prevažne manuálna, automatizovateľná, reaktívna a rastie spolu s veľkosťou systému alebo počtom používateľov. Spotrebúva ľudskú kapacitu, ale sama nevytvára trvalú schopnosť, ktorá by potrebu ďalšieho opakovania znižovala.

**Technical debt** je budúci náklad vytvorený technickým alebo procesným rozhodnutím, zanedbanou údržbou alebo rastúcou komplexitou. Zvyšuje cenu ďalších zmien, incidentov, onboarding-u a prevádzky, aj keď sa v konkrétnom okamihu nemusí prejavovať ako manuálna práca.

## 2. Rozdiel medzi toil-om a dlhom

Toil opisuje spotrebu práce; technical debt opisuje vlastnosť systému, ktorá budúcu prácu predražuje alebo zvyšuje riziko. Jeden problém môže obsahovať oboje, ale tieto pojmy sa nesmú zamieňať.

```text
technical debt: deployment nemá automatizovaný rollback
→ incident vytvorí potrebu ručného rollbacku
→ opakovaný ručný rollback je toil
```

Dlh často toil vytvára a toil následne odoberá kapacitu potrebnú na odstránenie dlhu. Tak vzniká samoposilňujúca slučka, v ktorej tím trávi čoraz viac času reaktívnou prevádzkou a čoraz menej engineering zlepšeniami.

## 3. Ako rozpoznať toil

Práca nie je toil iba preto, že je manuálna alebo nepríjemná. Za toil ju možno považovať vtedy, keď sa kombinuje viacero vlastností a organizácia vie opísaný outcome dosiahnuť trvalejším mechanizmom.

- **Opakovanie —** rovnaký alebo veľmi podobný zásah sa vracia pravidelne; jeho frekvencia preto vytvára kumulatívnu spotrebu času.
- **Manuálna exekúcia —** človek vykonáva predvídateľné kroky, ktoré by mohol bezpečne vykonať systém alebo self-service rozhranie.
- **Reaktivita —** práca vzniká ako odpoveď na alert, ticket alebo poruchu namiesto plánovaného zlepšovania schopnosti.
- **Nulový trvalý efekt —** po dokončení zásahu zostáva systém rovnako závislý od ďalšieho ľudského zásahu pri nasledujúcom výskyte.
- **Lineárny rast —** počet manuálnych úkonov rastie približne s počtom zákazníkov, resources, deploymentov alebo incidentov.
- **Automatizovateľné pravidlá —** rozhodnutie možno vyjadriť stabilným contractom, validáciou a bezpečným failure modelom.

Prvé vyšetrovanie neznámeho incidentu nie je automaticky toil, pretože vytvára nové poznanie. Ak sa však rovnaký incident rieši desiatykrát rovnakým reštartom bez systémovej zmeny, pôvodne hodnotná diagnostika sa zmenila na reaktívny toil.

## 4. Typické zdroje toil-u

Toil často nevzniká z jednej chýbajúcej automation, ale z nejasného rozhrania, slabého ownershipu alebo systému, ktorý neposkytuje bezpečný self-service mechanizmus.

- **Manuálne prideľovanie accessu —** každý request vyžaduje operátora, hoci role, scope a approval pravidlá sú opakovateľné; riešením môže byť identity lifecycle a time-bound self-service workflow.
- **Obnovovanie certifikátov —** človek opakovane sleduje expiry a vykonáva renewal; trvalejšia schopnosť zahŕňa automatický renewal, validation a alert na zlyhanie procesu.
- **Deployment podľa checklistu —** kroky sú známe, ale závisia od pamäte a poradia operátora; pipeline môže vytvoriť auditovateľnú, validovanú a opakovateľnú exekúciu.
- **Pravidelné čistenie diskov —** zásah odstraňuje symptóm, no nie nebounded logging, chybnú retention alebo capacity policy.
- **Ručné reštarty —** služba sa obnoví, ale memory leak, deadlock alebo dependency failure zostáva a vytvára ďalší incident.
- **Kopírovanie údajov medzi systémami —** ľudia kompenzujú chýbajúcu integráciu alebo autoritatívny source of truth, pričom vznikajú chyby a stale data.

## 5. Práca, ktorá nie je automaticky toil

Niektoré činnosti sú manuálne, no vytvárajú nový model, rozhodnutie alebo znalosti, ktoré nemožno redukovať na stabilnú procedúru. Ich hodnotu treba posudzovať podľa výsledku, nie podľa toho, či ich vykonal človek.

- **Threat modeling —** vyžaduje kontext a tvorbu nových threat hypotheses; môže používať šablóny, ale samotné rozhodovanie nie je rutinná exekúcia.
- **Prvé incident investigation —** tím objavuje neznámy failure mode a vytvára nové evidence; toil vznikne až pri opakovanom rovnakom zásahu bez nápravy.
- **Architektonický návrh —** porovnáva trade-offy a budúce scenáre; automatizovať možno analýzu dát, nie zodpovednosť za rozhodnutie.
- **Komunikácia počas incidentu —** vyžaduje situačný úsudok, koordináciu a dôveru; automatizácia môže pripraviť kontext, ale nie úplne nahradiť rozhodovanie.
- **Jednorazová riziková migrácia —** môže potrebovať skripty a rehearsal, no nemusí sa z nej stať všeobecná platform capability.

## 6. Technical debt ako ekonomický záväzok

Technical debt možno chápať ako rozhodnutie, ktoré dnes znižuje cenu alebo čas, ale vytvára budúci „úrok“. Úrok sa prejavuje dlhším lead time-om, vyšším change failure rate, opakovanými incidentmi, náročnejším onboardingom alebo potrebou špecializovaných manuálnych zásahov.

Nie každý dlh je zlý. Vedome prijatý dlh môže byť primeraný, ak je jeho benefit väčší než očakávaný úrok a existuje owner, scope, trigger pre nápravu a viditeľnosť v plánovaní.

## 7. Vedome prijatý, nevedomý a zanedbaný dlh

Tieto tri kategórie opisujú odlišný governance problém. Dôležité nie je iba to, ako dlh vznikol, ale či organizácia rozumie jeho dopadu a aktívne ho riadi.

- **Vedome prijatý dlh —** tím zvolí jednoduchšie riešenie pre časovo kritický cieľ a zaznamená obmedzenia, ownera a podmienku návratu; ide o riadený trade-off.
- **Nevedomý dlh —** nové scale, security alebo reliability požiadavky odhalia, že pôvodný návrh už nestačí; tím potrebuje revidovať staré predpoklady bez hľadania vinníka.
- **Zanedbaný dlh —** známa dočasná skratka nemá ownera ani termín a ďalšie vrstvy ju obchádzajú ďalšími workaroundmi; úrok sa nekontrolovane kumuluje.

## 8. Typy technického dlhu

Dlh nie je iba nekvalitný aplikačný kód. Môže existovať v architektúre, platforme, delivery procese, dokumentácii, security aj organizačných rozhraniach.

- **Architektonický dlh —** coupling, single points of failure alebo neškálovateľný data model predražujú každú ďalšiu zmenu.
- **Testing debt —** chýbajúce alebo flaky testy znižujú dôveru a nútia tímy používať manuálne regresie a opakované retries.
- **Dependency debt —** zastarané runtime-y a libraries zvyšujú security exposure a neskôr vyžadujú veľký skok namiesto malých priebežných upgradeov.
- **Operational debt —** slabá observability, chýbajúce runbooky a neotestované recovery paths predlžujú incidenty.
- **Infrastructure debt —** nekonzistentné IaC, ručné resources a state drift komplikujú reprodukciu a recovery.
- **Security debt —** výnimky bez expirácie, broad permissions alebo staré trust roots zvyšujú blast radius aj náklady budúcej nápravy.
- **Organizačný dlh —** nejasný ownership a handoff-based proces vytvárajú queues, rework a „nie je to náš problém“ správanie.

## 9. Samoposilňujúca slučka

Technical debt vytvára incidenty a manuálne zásahy. Tie spotrebujú engineering kapacitu, takže tím odkladá patching, refactoring a automation a dlh sa ďalej zväčšuje.

```text
debt
→ viac failure modes a manuálnej práce
→ toil
→ menej času na engineering
→ viac odložených opráv
→ ďalší debt
```

Túto slučku nemožno zlomiť iba požiadavkou „pracovať efektívnejšie“. Tím potrebuje rezervovanú kapacitu, prioritizačný mechanizmus a meranie, ktoré ukáže cenu opakovaného toil-u.

## 10. Automatizovať, odstrániť alebo prijať

Nie každý toil sa má riešiť rovnakým spôsobom. Pred automatizáciou treba určiť, či je samotná činnosť potrebná, či je stabilná a či automatizácia nezväčší blast radius chybného pravidla.

- **Odstrániť príčinu —** najlepšia možnosť, keď možno zrušiť potrebu zásahu, napríklad opraviť memory leak namiesto automatického reštartu.
- **Zjednodušiť —** zredukovať variants, approvals alebo handoffs skôr, než sa proces zapíše do kódu.
- **Automatizovať —** vhodné pre stabilné, často opakované a overiteľné kroky s jasným ownerom a failure modelom.
- **Self-service —** presunúť bezpečnú exekúciu bližšie k používateľovi, pričom platforma vynúti policy, validáciu a audit.
- **Prijať —** ak je frekvencia nízka a cena automatizácie vyššia než dlhodobá manuálna cena, kontrolovaný runbook môže byť primeraný.

## 11. Symptóm verzus root cause

Automatizácia symptómu môže byť vhodná ako dočasná mitigácia, ale nesmie sa vydávať za odstránenie dlhu. Cron, ktorý maže logy, môže zabrániť okamžitému zaplneniu disku, no root cause môže byť chybná retention, unbounded debug logging alebo nedostatočná capacity.

```text
symptom control: automaticky uvoľni disk
root-cause change: správna log rotation + retention + central storage + capacity alert
```

Dočasná mitigácia potrebuje explicitný owner a exit condition. Bez nich sa rýchla ochrana stane trvalou architektúrou a vytvorí ďalší skrytý dlh.

## 12. Meranie toil-u

Meranie má ukázať, kde ľudská kapacita opakovane kompenzuje chýbajúcu systémovú schopnosť. Nemá sa používať na hodnotenie jednotlivcov, pretože ľudia často vykonávajú toil vytvorený architektúrou a prioritami organizácie.

- **Toil hours —** čas strávený opakovanou exekúciou za týždeň alebo mesiac; umožní odhadnúť kumulatívnu cenu.
- **Repeat ticket count —** počet requests s rovnakým patternom; vysoká frekvencia signalizuje chýbajúce self-service rozhranie alebo automatizáciu.
- **Manual steps per change —** ukazuje variability a handoff risk v deployment alebo provisioning procese.
- **Known-cause pages —** počet on-call zásahov pre failure mode, ktorý už tím pozná; odhaľuje neuzavreté incident learning.
- **Scaling coefficient —** ako operačná práca rastie pri raste customers alebo resources; lineárny rast je varovný signál.
- **Engineering-to-operations ratio —** pomer času na trvalé zlepšenia voči reaktívnej prevádzke; dlhodobý pokles signalizuje toil trap.

Samotný počet ticketov môže byť zavádzajúci, ak sa zmení spôsob evidencie. Metriky preto treba doplniť samplingom práce a kvalitatívnym review s ľuďmi, ktorí ju vykonávajú.

## 13. Evidencia technického dlhu

Položka dlhu musí byť dostatočne konkrétna, aby mohla súťažiť o prioritu s feature workom. Vágny záznam „refactor platform“ neukazuje dopad, urgency ani požadovaný outcome.

Dobrý záznam obsahuje:

- **Problém —** konkrétny mechanizmus, ktorý vytvára náklad alebo riziko, nie iba názov technológie.
- **Evidence —** incidenty, toil hours, latency, security finding alebo change failure, ktoré dokazujú aktuálny dopad.
- **Scope —** služby, tímy, tenants a failure domains, ktorých sa dlh týka.
- **Úrok —** ako sa cena zväčšuje pri ďalšom raste alebo odklade.
- **Navrhovaný outcome —** aká schopnosť alebo invariant má po náprave platiť.
- **Owner —** tím zodpovedný za rozhodnutie a ďalšie review, nie nevyhnutne jediný implementátor.
- **Trigger —** dátum, incident count, scale threshold alebo dependency deadline, pri ktorom sa položka musí znovu posúdiť.

## 14. Prioritizácia

Priorita dlhu nevzniká z toho, ktorý problém je technicky najzaujímavejší. Má vychádzať z používateľského dopadu, security a reliability rizika, frekvencie toil-u, blokovania ďalšej práce a rastu budúceho úroku.

Praktický model môže pracovať s týmito otázkami:

- **Ako často problém vzniká?** Opakovaný malý zásah môže ročne stáť viac než jeden veľký incident.
- **Aký je blast radius?** Dlh v shared identity alebo CI platforme môže ovplyvniť veľa tímov naraz.
- **Ako rýchlo rastie úrok?** End-of-support dependency alebo expirovaný certificate chain má časovo rastúce riziko.
- **Čo dlh blokuje?** Niektoré opravy odomknú viacero ďalších zmien alebo znížia celý delivery lead time.
- **Aká je reverzibilita nápravy?** Malý experiment môže byť vhodnejší než veľký jednorazový rewrite.
- **Aká je cena nečinnosti?** Porovnáva sa s implementačnou cenou, nie iba s veľkosťou backlog itemu.

## 15. Capacity allocation

Ak roadmapa obsahuje iba features, toil a debt sa riešia až počas incidentu. Organizácia preto potrebuje explicitne rezervovať kapacitu na reliability, maintenance, security a automation.

Model môže používať fixný podiel kapacity, error-budget policy, pravidelný debt review alebo limit toil-u, po ktorého prekročení sa feature work spomalí. Dôležité je, aby pravidlo malo reálnu rozhodovaciu silu a nebolo iba deklaráciou bez priority.

## 16. Ownership dlhu

Owner technického dlhu zodpovedá za jeho viditeľnosť, evidence a ďalšie rozhodnutie. Nemusí mať kapacitu odstrániť celý problém sám, ale musí zabezpečiť, že riziko sa nestratí medzi tímami.

Dlh v shared platforme môže potrebovať spoločný ownership platformy a consumers. Aplikačný tím má dodať evidence dopadu, platform tím navrhnúť capability a product alebo engineering leadership rozhodnúť o priorite voči ostatnej práci.

## 17. End-to-end príklad CI/CD

Pipeline trvá 70 minút, testy sú flaky a deployment potrebuje manuálne doplniť environment parameters. Vývojári preto sledujú jobs, opakovane klikajú retry a koordinujú release cez chat.

Technical debt tvorí neefektívny build graph, shared mutable test environment, chýbajúca parameter schema a nedeterministické test data. Toil tvorí každodenné čakanie, ručné retry, hľadanie správnych hodnôt a manuálne schválenie zmeny, ktorá spĺňa stabilné pravidlá.

Náprava nezačne automatickým retry každého testu. Najprv oddelí flaky testy, zmeria queue a execution time, zavedie deterministic environment a explicitnú deployment schema; až potom automatizuje bezpečné promotion pravidlá.

## 18. SRE kontext

SRE používa toil ako prevádzkový budget, pretože neobmedzená opakovaná práca vytlačí engineering. Cieľom nie je dosiahnuť nulu, ale udržať toil pod hranicou, pri ktorej tím stále dokáže zlepšovať reliability systému.

On-call incident s novým failure mode môže byť hodnotná engineering práca. Ak však rovnaký alert pravidelne vedie k rovnakému runbook kroku, vzniká kandidát na automatizáciu, self-healing alebo odstránenie root cause-u.

## 19. Observability a reporting

Toil a debt potrebujú spoločné reporting rozhranie s delivery a reliability dátami. Samostatný backlog bez väzby na incidenty a kapacitu sa rýchlo stane nedôveryhodný.

Dashboard môže spájať repeat incidents, toil hours, debt items podľa risku, time-to-remediation a trend engineering capacity. Kvalitatívny review musí vysvetliť príčinu trendu; pokles ticketov môže znamenať automatizáciu, ale aj to, že ľudia prestali toil evidovať.

## 20. Anti-patterny

### Hero culture

Skúsený človek opakovane zachraňuje systém manuálnym zásahom a organizácia odmeňuje viditeľnú obnovu. Root cause, automation a knowledge sharing sa však nefinancujú, takže bus factor aj toil zostávajú vysoké.

### Automatizácia bez ownershipu

Skript zníži okamžitú manuálnu prácu, ale nemá testy, telemetry ani lifecycle. Po zmene API začne ticho zlyhávať a vytvorí nový prevádzkový dlh.

### Nekonečný debt backlog

Položky sa evidujú bez evidence, ownera a triggera. Backlog potom neovplyvňuje plánovanie a slúži iba ako archív známych problémov.

### Toil sa normalizuje ako „operational excellence“

Opakovaná manuálna práca sa považuje za znak obetavosti. Organizácia prestane spochybňovať, prečo je zásah potrebný a prečo jeho objem rastie.

### Rewrite ako univerzálna náprava

Tím navrhne kompletný prepis bez merania dominantného dlhu a migračného rizika. Veľká zmena môže vytvoriť nový dlh skôr, než odstráni pôvodný.

### Automatizácia symptómu bez exit condition

Dočasný cron alebo auto-restart stabilizuje službu, ale nemá ownera ani termín odstránenia. Mitigácia sa stane trvalou a zakryje rastúci root-cause risk.

## 21. Kontrolné otázky

1. Prečo nie je každá manuálna práca toil?
2. Aký je rozdiel medzi spotrebou toil-u a vlastnosťou technical debt?
3. Ako technical debt vytvára samoposilňujúcu toil slučku?
4. Kedy je opakovaný incident investigation ešte learning a kedy už toil?
5. Prečo automatizácia symptómu nemusí znížiť technický dlh?
6. Ktoré metriky ukážu, že operačná práca rastie lineárne so systémom?
7. Čo musí obsahovať prioritizovateľný debt record?
8. Ako sa líši vedome prijatý dlh od zanedbaného dlhu?
9. Prečo fixný feature-only roadmap model vedie k toil trap?
10. Kedy je prijatie manuálneho runbooku lepšie než vývoj platformy?
11. Ako hero culture zvyšuje bus factor aj technický dlh?
12. Ako overíš, že automatizácia toil skutočne odstránila a iba ho nepresunula?

## 22. Zhrnutie

Toil je opakovaná spotreba ľudskej kapacity bez trvalého zlepšenia. Technical debt je vlastnosť systému, ktorá zvyšuje budúcu cenu, riziko a náročnosť zmien; často vytvára toil a následne sa cez nedostatok engineering kapacity ďalej zväčšuje.

Silný operating model toil meria, rozlišuje symptom od root cause-u, eviduje debt s konkrétnym dopadom a rezervuje kapacitu na nápravu. Cieľom nie je automatizovať každú manuálnu úlohu, ale systematicky vytvárať schopnosti, ktoré znižujú potrebu opakovanej reaktívnej práce.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Immutable vs. mutable infrastructure](immutable-vs-mutable-infrastructure.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Value stream mapping →](value-stream-mapping.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
