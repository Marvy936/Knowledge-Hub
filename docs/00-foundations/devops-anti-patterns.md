# DevOps Anti-patterns

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [DevOps](devops.md), [Systems Thinking](systems-thinking.md), [Ownership Mindset](ownership-mindset.md)
- Súvisiace témy: team topology, platform engineering, CI/CD, SRE, continuous improvement

Táto záverečná kapitola nespája anti-patterny iba do katalógu varovaní. Sleduje jeden neúspešný transformačný program a ukazuje, ako lokálne rozumné rozhodnutia vytvoria fronty, stratu feedbacku, nejasný ownership a metriky, ktoré následne posilňujú rovnaké správanie.

## 1. Čo je anti-pattern

Anti-pattern je opakovane používané riešenie alebo spôsob práce, ktorý má zrozumiteľný lokálny dôvod, ale pri opakovaní systematicky poškodzuje širší výsledok. Nejde iba o chybu jednotlivca. Pattern býva stabilizovaný organizačnými hranicami, incentívami, rozpočtom, nástrojmi alebo spôsobom merania úspechu.

DevOps anti-pattern preto analyzuj ako príčinnú slučku:

```text
lokálny tlak alebo legitímna obava
→ zdanlivo rozumné riešenie
→ zmena ownershipu, frontu alebo feedbacku
→ horší end-to-end outcome
→ ďalší tlak na pôvodné riešenie
```

Ak sa opraví iba viditeľný nástroj alebo názov tímu, systémový mechanizmus zostane a anti-pattern sa objaví v inej forme.

## 2. Priebežný scenár: transformácia spoločnosti Atlas

Spoločnosť Atlas prevádzkuje desiatky aplikačných služieb. Produkčné nasadenia sú mesačné, často trvajú večer niekoľko hodín a pri incidente sa problém presúva medzi development, operations a security tímom.

Leadership stanoví cieľ „urobiť DevOps transformáciu“. Program začne nákupom GitLabu, Kubernetes platformy, Terraformu a observability nástroja. Vytvorí sa nový centrálny DevOps tím, ktorý má migrovať aplikácie, vytvoriť pipeline a zrýchliť deploymenty.

Po roku má Atlas viac automatizácie a modernejší runtime, ale lead time zostáva dlhý, deploymenty sú stále veľké a centrálny tím má rastúcu ticket queue. Product tímy nevidia produkčnú telemetry, on-call je preťažený a incidenty sa opakujú.

```text
moderný toolchain
+ nezmenené decision rights
+ rovnaké handoffy
+ lokálne activity metrics
= starý delivery systém s novým execution layerom
```

Nasledujúce anti-patterny nie sú nezávislé chyby. V scenári Atlasu vznikajú ako jednotlivé fázy jednej zlyhávajúcej transformácie.

## 3. Fáza 1: tool-first transformation

Atlas začne nástrojmi, pretože ich nákup, inštalácia a migrácia vytvárajú viditeľné míľniky. Program dokáže reportovať počet clusterov, pipeline a presunutých repositories, hoci ešte nepozná dominantné čakanie ani failure mechanizmus pôvodného value streamu.

Lokálna logika je pochopiteľná: bez technickej platformy nemožno zaviesť moderné delivery. Systémová chyba vzniká v poradí rozhodnutí. Nástroj sa vyberie skôr, než je definovaná capability, ktorú má vytvoriť, jej používateľ, ownership a merateľný outcome.

```text
cieľ: „nasadiť Kubernetes a GitLab"
→ optimalizácia migrácie workloadov
→ pôvodné approvals a ticketové handoffy zostanú
→ lead time sa významne nezmení
→ program žiada ešte viac migrácie a štandardizácie
```

Korekcia nezačína ďalším produktom. Najprv sa zmapuje konkrétny flow, napríklad zmena od merge po overený produkčný výsledok, a vyberie sa constraint, ktorý má platform capability odstrániť.

## 4. Fáza 2: DevOps ako premenovaný Ops tím

Centrálny tím prevezme build, deployment, Kubernetes, Terraform aj incidentnú podporu. Krátkodobo to zníži chaos, pretože experti vytvoria jednotný execution path. Product tímy však začnú každú zmenu odovzdávať novému tímu podobne, ako ju predtým odovzdávali Operations.

```text
product tím vytvorí application zmenu
→ DevOps ticket na pipeline alebo deployment
→ čakanie na central queue
→ central tím rieši runtime failure bez business contextu
→ product tím dostane oneskorený incidentný symptom
```

Nový názov tímu nezmenil ownership loop. Centrálny tím nesie dôsledky rozhodnutí, ktoré nevie prioritizovať ani meniť, a product tím nevidí produkčný feedback potrebný na zlepšenie designu.

Zdravšia hranica oddeľuje platform capability od service ownershipu. Platform tím vlastní reusable execution mechanizmus, bezpečné defaults, API, SLO a support. Service tím vlastní application semantics, test contract, rollout signals a používateľský outcome.

## 5. Fáza 3: ticket-driven operations

Atlas zachová tickety pre namespace, DNS, databázu, secret, resource limit aj deployment. Ticket poskytuje auditnú stopu, preto sa javí ako bezpečný control. Súčasne však funguje ako pomalé, neštruktúrované API, ktorého vstup závisí od textu a ktorého výsledok sa líši podľa operátora.

Pri raste počtu tímov vzniká front:

```text
opakovaný štandardný request
→ manuálna interpretácia
→ operátor vykoná rovnaké kroky
→ výsledok sa odovzdá bez machine-readable state-u
→ ďalší podobný request začína od začiatku
```

Ticket zostáva vhodný pre neštandardnú konzultáciu alebo výnimku. Stabilný request má prejsť do typed self-service workflowu, verzovanej konfigurácie alebo policy-controlled API, ktoré poskytne validation, audit, idempotency a verification.

## 6. Fáza 4: pipeline a approval theater

Atlas vytvorí pipeline s mnohými stages a povinným manuálnym approvalom. Počet jobov sa začne používať ako dôkaz maturity. Niektoré kroky však iba opakujú rovnakú kontrolu, poskytujú neurčitý error a čakajú na človeka, ktorý nemá ďalší risk context.

Pipeline theater vzniká, keď workflow vyzerá automatizovane, ale nerozhoduje na základe evidence:

```text
build
→ niekoľko redundantných scanov
→ manuálne potvrdenie green výsledkov
→ ticket na environment
→ ďalší approval bez risk segmentácie
→ manuálny production execution
```

Každý gate má znižovať pomenované riziko, mať failure semantics a poskytovať akčný dôkaz. Low-risk zmena môže prejsť automaticky pri splnení policy. Človek má posudzovať neautomatizovateľnú výnimku, blast radius alebo residual risk, nie mechanicky potvrdzovať statusy, ktoré už systém vyhodnotil.

## 7. Fáza 5: DevSecOps ako neskorá bezpečnostná brána

Security tím vstupuje tesne pred production release-om. Tento model chráni organizáciu pred neoverenou zmenou, ale feedback prichádza po strate contextu a po veľkej investícii do implementácie.

Architektonický finding potom vytvorí rozsiahly rework a security tím je vnímaný ako blokátor. Reakciou býva ešte formálnejší approval, čím sa front ďalej predĺži.

Korekčný model rozdelí bezpečnostný feedback podľa boundary:

- threat modeling a data classification vstupujú pri návrhu;
- bezpečné defaults a policy-as-code kontrolujú opakovateľné pravidlá;
- dependency, secret a artifact checks poskytujú skoré technické evidence;
- expert review zostáva pre nejasné alebo vysokorizikové rozhodnutie.

Cieľom nie je odstrániť security authority, ale presunúť opakovateľné kontroly k vzniku zmeny a zachovať človeka tam, kde pridáva kontextové rozhodnutie.

## 8. Fáza 6: one-size-fits-all platform

Centrálny tím chce znížiť support surface, preto vytvorí jeden povinný template pre všetky workloady. Štandardizácia je lokálne správna: menej variantov znižuje maintenance, training a security cost.

Anti-pattern vznikne, keď platforma ignoruje rozdielny state model, kritickosť alebo compliance. Jednoduché služby nesú zbytočnú komplexitu a špecifické workloady začnú používať shadow scripts a manuálne výnimky.

Golden path má byť preferovaný a dobre podporovaný, nie predstieraný ako univerzálny zákon. Potrebuje:

```text
jasný podporovaný use case
+ bezpečné defaults
+ stabilný interface
+ feedback od používateľov
+ explicitný escape hatch
+ risk a ownership contract výnimky
```

Ak tímy platformu obchádzajú, prvou hypotézou nemá byť nedostatok disciplíny. Treba overiť task success, latency, chýbajúci use case a kvalitu failure feedbacku.

## 9. Fáza 7: automate everything a copy-paste reuse

Pod tlakom na rýchlosť vznikajú dva opačné, ale súvisiace patterns. Jednorazový proces sa predčasne zmení na univerzálnu platformu, zatiaľ čo iné tímy kopírujú existujúce moduly a pipeline, aby nemuseli čakať na central ownera.

Premature abstraction vytvára veľký configuration a support surface bez stabilného common contractu. Copy-paste zase umožní rýchly začiatok, ale verzie sa rozídu a opravu nemožno distribuovať.

Rozhodnutie má postupovať podľa zrelosti potreby:

```text
nový alebo nejasný proces
→ dokumentovaný bounded postup
→ script pre stabilnú sekvenciu
→ reusable versioned component pre opakovaný contract
→ platform product až pri viacerých consumers a trvalom ownershipu
```

Reuse potrebuje versioning, compatibility tests, changelog a migration path. Automatizácia potrebuje ownera, telemetry a retirement. Inak sa z riešenia toil-u stane nový technický dlh.

## 10. Fáza 8: you build it, you run it bez podpory

Leadership neskôr presunie pager na product tímy. Formálne tým uzavrie ownership, ale neposkytne observability, runbooky, production access, safe delivery ani roadmap capacity na reliability prácu.

```text
pager duty bez capabilities
→ pomalá a neistá diagnosis
→ strach z deploymentu
→ väčšie a zriedkavejšie release-y
→ väčší incidentný dopad
→ vyššia on-call záťaž
```

Princíp `you build it, you run it` funguje iba s operating contractom. Tím potrebuje user-oriented signals, akčné alerty, rollback alebo mitigation authority, platform support, escalation k expertom a financovaný priestor na permanent fixes.

Pager bez týchto podmienok neuzatvára feedback; iba presúva toil a stres.

## 11. Fáza 9: hero culture a permanent emergency mode

Niekoľko expertov dokáže incident rýchlo obnoviť pomocou neformálnych prístupov a ručných zásahov. Organizácia ich odmeňuje, pretože viditeľná obnova má okamžitú hodnotu. Expert však nemá čas premeniť poznanie na test, guardrail, platform capability alebo odstránenie root cause-u.

Opakované emergency zmeny vytvoria ďalšiu slučku:

```text
krehký systém
→ incident
→ heroický break-glass zásah
→ služba obnovená bez convergence do source of truth
→ ďalší drift a knowledge dependency
→ ešte krehkejší systém
```

Emergency path je potrebný, ale má byť užší než bežná cesta, auditovaný a následne reconciliovaný. Rovnaký opakovaný zásah sa má evidovať ako toil a vytvoriť engineering action.

Kolektívny on-call, pairing, runbooky, game days a automatizované guardrails premieňajú individuálnu expertízu na tímovú schopnosť.

## 12. Fáza 10: no-blame bez accountability

Po incidente Atlas zavedie blameless postmortems. Tím sa vyhne hľadaniu vinníka, ale actions zostanú neurčité alebo bez ownera, termínu a effectiveness review. Dokument opisuje udalosť, no systém sa nemení.

Blameless analysis a accountability nie sú protiklady:

- blameless analysis hľadá podmienky, incentives, controls a interfaces, ktoré umožnili failure;
- accountability priraďuje nápravnému rozhodnutiu ownera, termín a overenie výsledku;
- vedomé porušenie policy možno riešiť bez redukcie systémovej analýzy na `human error`.

Postmortem je uzavretý až vtedy, keď learning zmení budúce správanie a evidence potvrdí účinok.

## 13. Fáza 11: vanity metrics a DORA leaderboard

Transformačný program potrebuje dokázať progres, preto sleduje počet pipeline, commitov, ticketov, clusterov a utilization ľudí. Neskôr zoradí tímy podľa deployment frequency a lead time.

Aktivita sa začne optimalizovať namiesto outcome-u. Tímy môžu vytvárať umelé deploymenty, meniť klasifikáciu incidentov alebo skrývať manual hotfixy, aby zlepšili score.

DORA metrics sú určené na diagnostiku konkrétneho value streamu a jeho trendu. Musia sa interpretovať spolu ako throughput a instability a doplniť reliability a business contextom. Nemajú byť individuálnym KPI ani leaderboardom neporovnateľných služieb.

Metrika je zdravá iba vtedy, keď podporuje rozhodnutie a jej zlepšenie nemožno jednoducho dosiahnuť poškodením širšieho outcome-u.

## 14. Fáza 12: observability ako dashboard factory

Atlas vytvorí veľa dashboardov a alertov, pretože ich existencia je ľahko merateľná. Telemetry však nie je naviazaná na user outcome, release identity, ownera ani action path.

Výsledkom je noise a pomalá diagnosis. Dashboard bez rozhodnutia je pasívne zobrazenie dát a nepoužívaný alert je maintenance cost.

Observability capability musí podporovať konkrétny loop:

```text
user alebo service signal
→ correlation s release a dependency
→ hypothesis a rozhodnutie
→ mitigation alebo code change
→ rovnakým signalom overená recovery
```

Počet panelov nie je relevantný outcome. Podstatná je schopnosť zodpovedať otázku a bezpečne konať.

## 15. Ako sa anti-patterny navzájom posilňujú

V Atlase nevznikol jeden izolovaný problém. Jednotlivé patterns vytvorili reinforcing loop:

```text
tool-first program
→ centrálny DevOps tím
→ ticketové handoffy a approval queues
→ dlhý lead time a veľké batchy
→ väčší deployment risk
→ viac centralizovaných controls
→ slabší product ownership a neskorší feedback
→ viac incidentov a heroických zásahov
→ menej kapacity na platform improvement
→ ešte väčšia závislosť od centrálneho tímu
```

Preto zmena jedného názvu alebo nástroja nestačí. Napríklad self-service portal bez automatizovaného provisioning backendu skráti iba vytvorenie ticketu. Pager presunutý na developerov bez accessu a telemetry presunie iba bolesť. Policy-as-code bez jasného exception lifecycle-u môže automatizovať rovnaký approval bottleneck.

## 16. Audit anti-patternu cez jeden symptóm

Začni jedným opakovaným symptómom, nie workshopom o celej kultúre. Atlas vyberie dlhý production lead time pre bežnú aplikačnú zmenu.

Audit sleduje tento causal path:

```text
symptóm
→ konkrétny value stream a timestamps
→ dominantný wait, rework alebo failure boundary
→ lokálne rozhodnutie, ktoré ho vytvára
→ incentive a owner rozhodnutia
→ súčasná capability alebo chýbajúci interface
→ malá korekčná hypotéza
→ end-to-end evidence
```

Príklad:

```text
symptóm: median lead time 12 dní

VSM:
review wait             1 deň
shared test environment 3 dni
security approval       5 dní
deployment              18 minút

mechanizmus:
nízkoriziková zmena čaká na rovnaký central review ako výnimka

hypotéza:
risk classification + policy evidence + manual review iba pre exception
znížia approval wait pod 8 hodín bez rastu change fail rate
```

Ak sa po zmene front presunie do test environmentu, experiment nebol úplným end-to-end úspechom. Mapa a hypotéza sa aktualizujú podľa nového constraintu.

## 17. Korekčný model

Zdravá náprava sa nepokúša zaviesť všetky DevOps praktiky naraz. Mení konkrétny mechanizmus a zachováva feedback.

1. **Definuj outcome a boundary.** Urči službu alebo value stream, používateľský výsledok a začiatok a koniec merania.
2. **Zmeraj current state.** Oddeľ process time, waiting, rework, incidents a toil; nespoliehaj sa iba na oficiálny diagram.
3. **Identifikuj constraint a ownership gap.** Zisti, kto môže rozhodnutie vykonať, kto nesie jeho dôsledky a ktoré capabilities chýbajú.
4. **Navrhni bounded capability alebo boundary change.** Môže ísť o self-service, risk-based policy, platform interface, service ownership alebo odstránenie nepotrebného kroku.
5. **Definuj guardrails a failure semantics.** Rýchlejší flow nesmie skryť security, reliability ani data risk.
6. **Spusti malý experiment.** Obmedz scope, stanov baseline, success a abort conditions.
7. **Over celý outcome.** Sleduj, či sa waiting alebo toil nezmenil iba na inú frontu alebo support load.
8. **Štandardizuj learning.** Potvrdený výsledok sa premietne do platformy, policy, ownershipu, dokumentácie a metrík.

## 18. Kedy podobný pattern nemusí byť chybou

Anti-pattern nemožno určiť iba podľa vonkajšieho tvaru. Central operations, manuálny approval alebo mutable emergency zásah môžu byť správne podľa kritickosti a contextu.

- Central NOC môže byť efektívny first-line model, ak zachová service context, response SLO a feedback k ownerovi.
- Manuálny approval môže byť primeraný pri neautomatizovateľnom vysokom riziku, ak reviewer dostane konkrétne evidence a authority.
- Ticket môže byť vhodný pre výnimku, konzultáciu alebo jednorazový nejasný request.
- One-size default môže znižovať complexity, ak má jasne definovaný supported scope a escape hatch.
- Break-glass zásah môže byť najbezpečnejšia incidentná mitigácia, ak je auditovaný a vrátený do managed state-u.

Rozhodujúci je mechanizmus a outcome, nie slogan alebo použitý organizačný tvar.

## 19. Troubleshooting transformačného programu

Ak program neprináša očakávané výsledky, nezačni ďalšou veľkou reorganizáciou. Sleduj, kde sa rozchádza deklarovaná zmena so skutočným behaviorom.

- **Viac nástrojov, rovnaký lead time:** zmapuj waiting a handoffs; toolchain pravdepodobne nezmenil decision path.
- **Platform team má rastúcu queue:** odlíš chýbajúci self-service interface od legitímnej expertnej konzultácie a zmeraj repeat request patterns.
- **Tímy obchádzajú golden path:** over task success, unsupported use cases, latency, feedback a exception process.
- **On-call load rastie po presune ownershipu:** skontroluj readiness, access, alert actionability, platform support a roadmap capacity.
- **Metriky sa zlepšujú, incidenty nie:** over event taxonomy, out-of-band changes, gaming a väzbu metrík na user outcome.
- **Postmortems neprinášajú zmenu:** skontroluj actions, ownerov, termíny a effectiveness review.
- **Emergency path sa používa bežne:** analyzuj, prečo normálny flow nedokáže bezpečne reagovať, a odstráň opakovaný constraint.

## 20. Kontrolné otázky

1. Prečo anti-pattern môže byť lokálne rozumným rozhodnutím?
2. Ako tool-first transformácia zachová pôvodný handoff a approval model?
3. Aký rozdiel je medzi central DevOps queue a platform productom?
4. Kedy ticket funguje ako vhodná výnimka a kedy ako slabé API?
5. Ako pipeline alebo approval theater vytvára waiting bez novej risk evidence?
6. Prečo neskorý security gate zvyšuje rework a organizačný konflikt?
7. Ako one-size platforma vytvára shadow workflows?
8. Prečo automation bez ownershipu môže vytvoriť nový technical debt?
9. Aké capabilities potrebuje `you build it, you run it` pred presunom pagera?
10. Ako hero culture a permanent emergency mode vytvárajú reinforcing loop?
11. Prečo blameless analysis stále potrebuje accountability?
12. Ako DORA leaderboard alebo vanity metric mení správanie tímov?
13. Čo odlišuje observability capability od dashboard factory?
14. Ako audit jedného symptómu odhalí underlying anti-pattern?
15. Aké evidence dokazujú, že korekcia zmenila systém a iba nepresunula frontu?

## 21. Zhrnutie

DevOps anti-patterny nevznikajú iba zo zlých nástrojov alebo chybných ľudí. Vznikajú v socio-technickom systéme, ktorý lokálne odmeňuje správanie poškodzujúce end-to-end flow, reliability alebo learning.

Najdôležitejší diagnostický model je `lokálny tlak → rozumné riešenie → zmena boundary alebo feedbacku → systémový dôsledok → posilnenie pôvodného tlaku`. Náprava preto musí meniť capability, decision rights, ownership, incentive alebo tok práce a jej úspech sa musí potvrdiť na rovnakom end-to-end outcome-e, ktorý anti-pattern pôvodne poškodzoval.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DORA metrics](dora-metrics.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Kernel a user space →](../01-linux-and-systems/kernel-and-user-space.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
