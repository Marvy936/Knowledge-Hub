# DevOps Anti-patterns

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [DevOps](devops.md), [Systems Thinking](systems-thinking.md), [Ownership Mindset](ownership-mindset.md)
- Súvisiace témy: team topology, platform engineering, CI/CD, SRE, continuous improvement

## 1. Definícia

Anti-pattern je opakovane sa vyskytujúce riešenie alebo spôsob práce, ktorý pôsobí rozumne lokálne alebo krátkodobo, ale systematicky vytvára nežiaduce výsledky.

DevOps anti-patterny často vznikajú vtedy, keď organizácia prevezme nástroj alebo názov roly bez zmeny ownershipu, toku práce, spätnej väzby a rozhodovacích hraníc.

## 2. Tool-first transformation

Organizácia začne transformáciu nákupom alebo nasadením nástrojov:

```text
GitLab + Kubernetes + Terraform + monitoring
```

Proces však zostáva:

```text
vývoj → ticket → infra tím → ticket → security → ticket → operations
```

Výsledkom je modernejšia technológia obsluhujúca rovnaké fronty a handoffs.

### Symptómy

- úspech sa meria počtom migrovaných pipeline,
- nástroje nemajú jasný problém, ktorý riešia,
- tímy používajú platformu iba cez centrálnych administrátorov,
- automatizuje sa existujúci proces bez jeho zjednodušenia.

### Náprava

Najprv zmapovať value stream, ownership a constraints. Nástroj vybrať až podľa požadovanej capability.

## 3. DevOps ako premenovaný Ops tím

Vznikne centrálne oddelenie s názvom DevOps, ktorému vývoj odovzdá aplikáciu na build, deployment a prevádzku.

```text
Developers → DevOps ticket queue → production
```

Silo sa nepodarilo odstrániť; iba dostalo nový názov.

### Dôsledky

- centrálny tím sa stane bottleneckom,
- vývoj nemá produkčný feedback,
- prevádzkový tím nesie zodpovednosť bez kontroly nad návrhom aplikácie,
- platform knowledge sa koncentruje u malej skupiny.

### Lepší model

Platform alebo enablement tím vytvára self-service capabilities a guardrails. Produktové tímy zachovávajú ownership svojich služieb v jasne definovanom rozsahu.

## 4. You build it, you run it bez podpory

Vývojárom sa pridelí on-call a produkčná zodpovednosť bez:

- observability,
- runbookov,
- školenia,
- bezpečných deployment mechanizmov,
- SLO,
- kapacity na reliability prácu,
- podpory platformy.

Výsledkom nie je ownership, ale presunutie stresu.

Ownership potrebuje právomoc meniť systém a investovať do jeho zlepšenia.

## 5. Ticket-driven operations

Každá infraštruktúrna alebo prevádzková požiadavka prechádza manuálnym ticketom:

- vytvor namespace,
- pridaj DNS,
- vytvor databázu,
- zmeň limit,
- nasad aplikáciu.

Ticket je vhodný na evidenciu výnimky alebo komplexnej služby. Je slabým runtime API pre opakovateľné štandardné požiadavky.

### Náprava

Stabilné opakovateľné operácie presunúť do:

- version-controlled konfigurácie,
- self-service portálu alebo API,
- automatizovaných workflow,
- policy-as-code,
- štandardizovaných templates.

## 6. Pipeline ako cieľ

Tím vytvorí rozsiahlu pipeline s desiatkami stages a považuje tým CI/CD za dokončené.

### Symptómy

- pipeline je pomalšia než pôvodný proces,
- joby existujú bez jasnej failure policy,
- nikto nevie, ktoré kontroly poskytujú hodnotu,
- retry je štandardný spôsob úspechu,
- deployment zostáva manuálny a neauditovateľný.

Pipeline je mechanizmus spätnej väzby a delivery, nie cieľ transformácie.

## 7. Automate everything

Automatizácia sa hodnotí ako dobrá sama osebe.

Problémy:

- automatizuje sa nestabilný proces,
- jednorazová úloha dostane zložitý framework,
- údržba automatizácie je drahšia než ušetrená práca,
- zlyhanie skriptu nemá ownera ani monitoring,
- ľudia prestanú rozumieť mechanizmu pod automatizáciou.

Automatizovať treba prioritne opakovateľnú, stabilnú a hodnotnú prácu.

## 8. Hero culture

Systém závisí od niekoľkých expertov, ktorí riešia incidenty, poznajú manuálne kroky a obchádzajú štandardné procesy.

Krátkodobo hero obnoví službu. Dlhodobo organizácia odmeňuje individuálne zachraňovanie namiesto odstránenia systémovej príčiny.

### Symptómy

- bus factor je nízky,
- dokumentácia je v hlavách ľudí,
- incidenty sa riešia cez súkromné správy,
- opakované zásahy sa nepremenia na runbook alebo automatizáciu,
- expert nemá čas na preventívnu prácu.

## 9. Shared responsibility bez jasného ownershipu

„Všetci sú zodpovední“ sa môže zmeniť na „nikto nie je accountable“.

Zdieľaná spolupráca potrebuje explicitne určiť:

- ownera služby,
- ownera platform capability,
- escalation path,
- hranice supportu,
- rozhodovacie práva,
- kto udržiava runbook, dashboard a SLO.

Ownership neznamená izoláciu. Znamená jasnú poslednú zodpovednosť za výsledok.

## 10. DevSecOps ako finálna security gate

Security tím vykoná kontrolu tesne pred produkciou a môže zmenu zastaviť.

Dôsledky:

- feedback prichádza neskoro,
- oprava je drahá,
- security je vnímaná ako blokátor,
- tímy obchádzajú proces pri urgentných zmenách.

Shift-left neznamená preniesť všetku bezpečnostnú zodpovednosť na vývojárov. Znamená poskytnúť skoré kontroly, bezpečné defaults, threat modeling a jasnú podporu expertov.

## 11. One-size-fits-all platform

Platforma vynúti rovnaký deployment, runtime a observability model pre všetky workloads bez ohľadu na ich riziko a charakter.

Výsledok:

- jednoduché služby nesú zbytočnú komplexitu,
- špecifické workloads platformu obchádzajú,
- paved road sa stane povinnou diaľnicou bez výjazdu,
- centrálna platforma spomaľuje experimenty.

Dobrý golden path je preferovaný, podporovaný a bezpečný, ale má definovaný escape hatch.

## 12. Copy-paste Infrastructure as Code

Tímy kopírujú celé Terraform moduly, Helm charty alebo pipeline templates a lokálne ich upravujú.

### Dôsledky

- opravy sa nedajú distribuovať,
- verzie sa nekontrolovane rozchádzajú,
- rovnaká chyba existuje v mnohých kópiách,
- vlastníctvo template nie je jasné.

### Náprava

Používať verziované reusable modules s jasným kontraktom, changelogom, testami a upgrade procesom. Abstrakcia však nesmie skryť dôležité platformové správanie.

## 13. Environment snowflakes

Development, test a production vznikajú odlišnými procesmi a majú nezdokumentované rozdiely.

Typická veta:

```text
„V teste to fungovalo, produkcia je však trochu iná.“
```

Náprava:

- rovnaké artifacts,
- Infrastructure as Code,
- environment-specific dáta oddelené od spoločnej definície,
- automatizované parity kontroly,
- explicitné a odôvodnené rozdiely.

Úplná identita prostredí nie je vždy možná, ale rozdiely musia byť známe.

## 14. Big-bang releases

Veľa zmien sa integruje a nasadzuje naraz v dlhých intervaloch.

Dôsledky:

- veľký blast radius,
- komplikovaný rollback,
- dlhý feedback loop,
- náročné hľadanie príčiny,
- koordinácia veľkého počtu tímov,
- rastúci stres release okna.

Menšie batches, trunk-based development, automatické testy a progressive delivery znižujú počet súčasne menených premenných.

## 15. Change approval theater

Manuálne schválenie existuje pre každú zmenu bez ohľadu na riziko. Schvaľovateľ často nemá technický kontext a iba potvrdí formulár.

To vytvára delay bez reálneho zníženia rizika.

Lepší model:

- automatizované dôkazy z pipeline,
- preddefinované risk classes,
- policy-based approval,
- manuálny review pri vysokorizikových výnimkách,
- audit trail každej zmeny.

## 16. Vanity metrics

Tím sleduje čísla, ktoré vyzerajú dobre, ale neriadia výsledok:

- počet commitov na developera,
- počet pipeline jobov,
- počet vytvorených automatizácií,
- percento využitia všetkých ľudí,
- počet uzavretých ticketov bez hodnotenia dopadu.

Vyťaženosť a aktivita nie sú to isté ako flow, kvalita alebo hodnota.

## 17. DORA metrics ako leaderboard

Tímy sa zoradia podľa deployment frequency alebo lead time bez zohľadnenia kontextu. Metriky sa použijú na hodnotenie ľudí a rozpočtov.

Výsledkom je gaming:

- umelé deploymenty,
- rozdelenie zmien bez hodnoty,
- nepriznané incidenty,
- zmena definície úspechu,
- presúvanie problematických deploymentov mimo meraného systému.

DORA metriky majú slúžiť na zlepšovanie konkrétnej služby v čase.

## 18. No-blame ako no-accountability

Blameless postmortem neznamená, že sa ignorujú rozhodnutia alebo zodpovednosť.

Správny prístup:

- nehľadá vinníka ako jednoduché vysvetlenie,
- skúma podmienky, ktoré robili rozhodnutie rozumným,
- pomenúva chybné procesy a technické mechanizmy,
- prideľuje konkrétne nápravné actions a ownerov.

Bez následných actions je postmortem iba dokumentácia incidentu.

## 19. Permanent emergency mode

Urgentná výnimka sa stane bežným delivery procesom:

- priame zmeny v produkcii,
- vypnuté testy,
- zdieľané admin účty,
- ručné hotfixy bez spätného zápisu,
- neustále presúvanie preventívnej práce.

Emergency proces musí byť rýchly, auditovateľný a následne uzavretý reconciliation krokmi.

## 20. Ako anti-pattern analyzovať

Pri každom podozrivom procese sa pýtaj:

1. Aký lokálny problém riešenie pôvodne riešilo?
2. Aké správanie motivuje?
3. Kde vytvára queue alebo handoff?
4. Kto nesie zodpovednosť bez právomoci?
5. Aký feedback sa stráca alebo prichádza neskoro?
6. Ako sa systém správa pri raste?
7. Ktorá metrika môže ukázať skutočný dopad?
8. Aký malý experiment vie hypotézu overiť?

## 21. Kontrolné otázky

1. Prečo samotné zavedenie Kubernetes nevytvára DevOps model?
2. Ako sa líši platform tím od centrálneho ticketového DevOps tímu?
3. Prečo môže povinné manuálne approval zvyšovať riziko namiesto jeho znižovania?
4. Aký je rozdiel medzi blameless culture a absenciou accountability?
5. Prečo hero culture blokuje continuous improvement?
6. Ako copy-paste IaC vytvára dlhodobý drift?
7. Prečo sa DORA metriky nemajú používať ako leaderboard?
8. Čo musí nasledovať po emergency hotfixe vykonanom priamo v produkcii?

## 22. Zhrnutie

DevOps anti-patterny sú najmä zlyhania socio-technického systému: nejasný ownership, dlhé handoffs, neskorý feedback, lokálna optimalizácia a automatizácia bez pochopenia procesu. Rozpoznať ich znamená sledovať celý tok hodnoty a výsledné správanie, nie názvy tímov ani počet používaných nástrojov.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DORA metrics](dora-metrics.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Kernel a user space →](../01-linux-and-systems/kernel-and-user-space.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
