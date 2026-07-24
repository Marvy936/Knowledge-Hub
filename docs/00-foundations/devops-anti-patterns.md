# DevOps Anti-patterns

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [DevOps](devops.md), [Systems Thinking](systems-thinking.md), [Ownership Mindset](ownership-mindset.md)
- Súvisiace témy: team topology, platform engineering, CI/CD, SRE, continuous improvement

## 1. Čo je anti-pattern

Anti-pattern je opakovane sa vyskytujúce riešenie alebo spôsob práce, ktorý pôsobí rozumne lokálne alebo krátkodobo, ale systematicky vytvára nežiaduce výsledky. Na rozdiel od obyčajnej chyby býva anti-pattern stabilizovaný incentívami, organizačnými hranicami alebo nástrojmi.

DevOps anti-patterny často vznikajú vtedy, keď organizácia prevezme názov roly alebo technológiu bez zmeny ownershipu, toku práce a spätnej väzby. Preto ich nemožno opraviť iba výmenou nástroja.

## 2. Ako anti-pattern analyzovať

Pri každom anti-patterne treba rozlíšiť štyri vrstvy: lokálny dôvod, systémový mechanizmus, pozorovateľné signály a korekčný model. Samotné označenie „zlá kultúra“ neposkytuje použiteľnú diagnózu.

```text
lokálny tlak alebo incentíva
→ zdanlivo rozumné riešenie
→ front, strata feedbacku alebo nejasný ownership
→ zhoršený end-to-end výsledok
```

## 3. Tool-first transformation

Organizácia začne transformáciu nasadením GitLabu, Kubernetes, Terraformu alebo nového monitoringu. Nástroj je viditeľný, ľahko sa nakupuje a jeho zavedenie možno prezentovať ako konkrétny míľnik.

Proces však zostane založený na ticketoch, ručných schváleniach a odovzdávkach. Výsledkom je modernejšia technológia obsluhujúca rovnaké fronty a rovnaký nejasný ownership.

Typickým signálom je meranie úspechu počtom migrovaných pipeline alebo clusterov namiesto lead time, reliability a používateľského výsledku. Náprava začína zmapovaním value streamu a výberom capability, ktorú má technológia podporiť.

## 4. DevOps ako premenovaný Ops tím

Centrálne oddelenie dostane názov DevOps a preberie build, deployment, infraštruktúru aj prevádzku za aplikačné tímy. Krátkodobo to zjednotí expertízu a môže znížiť chaos.

Dlhodobo vznikne nový ticket queue a aplikačné tímy stratia produkčný feedback. Centrálny tím nesie zodpovednosť za systémy, ktorých architektúru nemôže ovplyvniť, a stáva sa bottleneckom pre každú zmenu.

Lepší model oddeľuje platform capability od service ownershipu. Platform tím poskytuje self-service rozhrania a guardrails, zatiaľ čo produktový tím vlastní správanie služby v jasne definovanom rozsahu.

## 5. You build it, you run it bez podpory

Vývojárom sa pridelí pager a produkčná zodpovednosť bez observability, runbookov, prístupov a kapacity na reliability prácu. Organizácia tým formálne presunie ownership, ale neposkytne decision rights ani capabilities potrebné na jeho vykonanie.

Výsledkom je únava, pomalá diagnostika a odpor voči zmenám. Zdravý model potrebuje operational readiness, akčné alerty, platform support, tréning a explicitný priestor v roadmap-e na odstránenie opakovaných failure modes.

## 6. Ticket-driven operations

Štandardné požiadavky ako namespace, DNS record, databáza alebo zmena limitu sa vykonávajú manuálnym ticketom. Ticket poskytuje auditnú stopu, ale funguje ako veľmi pomalé a neštruktúrované API.

Pri raste organizácie vznikajú fronty, nekonzistentné výsledky a skryté priority. Opakovateľné požiadavky majú prejsť do verzovanej konfigurácie, self-service workflowu alebo policy-controlled API; ticket zostáva vhodný pre výnimku a konzultáciu.

## 7. Pipeline ako cieľ

Tím vytvorí pipeline s veľkým počtom stages a považuje tým delivery problém za vyriešený. Komplexita pipeline sa začne zamieňať s kvalitou procesu.

Ak joby nemajú jasnú failure policy, spätná väzba je pomalá a deployment zostáva manuálny, pipeline iba automatizovala časť handoff modelu. Každý krok má existovať preto, že znižuje konkrétnu neistotu alebo riziko a poskytuje akčný dôkaz.

## 8. Automate everything

Automatizácia sa považuje za hodnotu samu osebe. Jednorazová úloha dostane univerzálny framework, nestabilný proces sa zakóduje a skripty vzniknú bez ownera, testov a observability.

Mechanizmom zlyhania je rast maintenance costu a blast radiusu. Automatizovať treba stabilnú, opakovateľnú a hodnotnú prácu; pred automatizáciou sa má proces zjednodušiť a po nej overovať skutočný outcome.

## 9. Hero culture

Niekoľko expertov opakovane zachraňuje systém pomocou manuálnych zásahov a neformálnych znalostí. Krátkodobo je ich zásah efektívny, preto organizácia správanie odmeňuje.

Dlhodobo sa však incidenty nemenia na runbooky, testy ani architektonické opatrenia. Bus factor zostáva nízky a expert nemá kapacitu odstrániť príčinu potreby vlastného hrdinstva.

Korekčný model zahŕňa kolektívny on-call, dokumentáciu, pairing, game days a povinné sledovanie opakovaných zásahov ako toil-u. Cieľom nie je znížiť hodnotu expertízy, ale premeniť ju na schopnosť systému.

## 10. Shared responsibility bez accountability

Tvrdenie „všetci sú zodpovední“ môže znamenať, že nikto nemá poslednú zodpovednosť za výsledok. Pri incidente sa problém presúva medzi tímami a každý správne tvrdí, že vlastní iba časť systému.

Zdieľaná spolupráca potrebuje explicitný service owner, platform owner, escalation path a decision rights. Accountability neznamená, že owner všetko vykonáva osobne; znamená, že zabezpečí uzavretie outcome-u a koordináciu dependencies.

## 11. DevSecOps ako finálna security gate

Security review prebehne tesne pred produkciou a môže zastaviť release. Organizácia tým zachová expert control, ale feedback prichádza v najdrahšom možnom bode.

Architektonické riziko odhalené po mesiacoch implementácie vytvorí veľký rework a security tím začne byť vnímaný ako blokátor. Lepší model kombinuje skorý threat modeling, bezpečné defaults, policy-as-code a expert review pre skutočne vysokorizikové rozhodnutia.

## 12. One-size-fits-all platform

Platforma vynúti rovnaký runtime, deployment a observability model pre každý workload. Štandardizácia znižuje podporovaný variant space, preto je lokálne atraktívna.

Ak však ignoruje kritickosť, state model alebo compliance, jednoduché služby nesú zbytočnú komplexitu a špecifické workloady platformu obchádzajú. Golden path má byť preferovaný a podporovaný, ale potrebuje explicitný escape hatch s vlastným risk contractom.

## 13. Copy-paste Infrastructure as Code

Tímy kopírujú moduly, charty alebo pipeline templates a lokálne ich upravujú. Copy-paste umožní rýchly začiatok bez závislosti na central ownerovi.

Postupne sa však verzie rozídu, opravy sa nedajú distribuovať a rovnaká chyba existuje v mnohých kópiách. Reusable component potrebuje verziovaný kontrakt, testy, changelog a upgrade path; zároveň nesmie skryť behavior, ktorý konzument potrebuje chápať.

## 14. Environment snowflakes

Development, test a production vznikajú odlišnými procesmi a majú nezdokumentované rozdiely. Manuálne úpravy často riešia lokálny incident, ale nevstúpia späť do source of truth.

Výsledkom je strata dôvery v predprodukčné testovanie. Rovnaký artifact, IaC, parity checks a explicitne zdokumentované environment-specific values znižujú rozdiel medzi tým, čo bolo overené, a tým, čo bolo nasadené.

## 15. Big-bang releases

Veľa zmien sa integruje a nasadzuje naraz v dlhých intervaloch. Dlhé release okno môže pôsobiť efektívne, pretože koordinácia sa vykoná iba raz.

Veľký batch však zväčšuje blast radius, počet súčasne menených premenných a náročnosť rollbacku. Menšie koherentné zmeny, trunk-based development a progressive delivery skracujú feedback loop a zjednodušujú izoláciu príčiny.

## 16. Change approval theater

Každá zmena potrebuje manuálne schválenie bez ohľadu na riziko. Schvaľovateľ často vidí iba formulár a nemá evidence potrebné na technické rozhodnutie.

Proces vytvára wait time bez primeraného zníženia rizika. Risk-based model používa automatizované pipeline evidence, policy classes a manuálny review iba tam, kde je potrebné ľudské posúdenie neautomatizovateľného rizika.

## 17. Vanity metrics

Organizácia sleduje počet commitov, ticketov, pipeline jobov alebo percento využitia ľudí. Tieto čísla sú ľahko dostupné a vytvárajú dojem objektívneho riadenia.

Aktivita však nie je totožná s flow, kvalitou ani hodnotou. Metrika musí podporovať konkrétne rozhodnutie a byť spojená s outcome-om; inak motivuje k produkcii viditeľnej práce bez systémového zlepšenia.

## 18. DORA metrics ako leaderboard

Tímy sa zoradia podľa deployment frequency alebo lead time bez zohľadnenia služby a release modelu. Metrika určená na učenie sa zmení na nástroj hodnotenia a rozpočtovania.

Výsledkom je gaming: umelé deploymenty, nepriznané incidenty alebo zmena definície úspechu. DORA sa má používať na trend konkrétneho value streamu a spolu s instability, reliability a kontextom.

## 19. No-blame ako no-accountability

Blameless postmortem sa nesprávne interpretuje ako zákaz pomenovať zlé rozhodnutie alebo neprideliť nápravné opatrenie. Dokument potom opisuje incident, ale systém zostane nezmenený.

Blameless prístup odmieta jednoduchý záver „human error“ a skúma podmienky, ktoré rozhodnutie umožnili. Accountability zostáva zachovaná cez konkrétne actions, ownerov, termíny a overenie účinku.

## 20. Permanent emergency mode

Urgentná výnimka sa stane normálnym spôsobom práce. Každý problém obíde testy, štandardný review alebo plánovanie, pretože systém už nemá rezervnú kapacitu.

Emergency path je potrebný, ale musí byť užší, auditovaný a následne reconciliovaný so source of truth. Opakované použitie tej istej výnimky je signálom technického dlhu alebo nefunkčného normálneho procesu.

## 21. Observability ako dashboard factory

Tím vytvorí veľa dashboardov a alertov bez väzby na používateľský outcome, ownera alebo rozhodnutie. Viditeľnosť technických metrík sa zamieňa s observability capability.

Výsledkom je noise, alert fatigue a pomalá diagnostika. Telemetry má podporovať konkrétne otázky, SLI, release verification a incident workflow; nepoužívaný dashboard je maintenance cost, nie automaticky hodnota.

## 22. Platforma ako produkt iba podľa názvu

Platform tím sa označí za produktový, ale používateľské tímy nemajú možnosť ovplyvniť roadmapu a platforma nemeria adoption ani task success. Interný monopol sa iba premenoval na produkt.

Skutočný platform product má definovaných používateľov, podporované journeys, SLO, feedback mechanism a lifecycle. Self-service capability musí znižovať cognitive load bez skrývania kritických failure boundaries.

## 23. Ako vykonať audit anti-patternov

Vyber jeden opakovaný symptóm, napríklad dlhý deployment lead time alebo opakovaný nočný zásah. Zmapuj lokálnu motiváciu, kto nesie náklady, kde sa stráca feedback a ktoré metriky správanie odmeňujú.

Potom navrhni jednu zmenu boundary, capability alebo incentive a stanov evidence úspechu. Anti-pattern sa nepovažuje za odstránený zmenou názvu tímu; musí sa zmeniť pozorovateľné správanie systému.

## 24. Troubleshooting organizačnej zmeny

Ak nový proces neprináša zlepšenie, over, či sa front iba presunul do inej fázy. Self-service portal môže napríklad skrátiť ticket creation, ale provisioning zostane manuálny za rovnakým bottleneckom.

Ak ľudia obchádzajú golden path, nehľadaj automaticky problém v disciplíne. Porovnaj, či platforma podporuje ich use case, poskytuje dostatočný feedback a má primeraný escape-hatch proces.

## 25. Kontrolné otázky

1. Prečo anti-pattern často pôsobí lokálne rozumne?
2. Ako tool-first transformácia zachová starý handoff model?
3. Prečo centrálny DevOps tím môže vytvoriť nové silo?
4. Aké capabilities potrebuje you-build-it-you-run-it model?
5. Kedy je ticket vhodný a kedy funguje ako slabé API?
6. Prečo automatizácia môže zväčšiť blast radius?
7. Ako hero culture blokuje systémové učenie?
8. Prečo shared responsibility potrebuje explicitnú accountability?
9. Ako risk-based approval znižuje theater bez straty kontroly?
10. Prečo DORA leaderboard vedie ku gamingu?
11. Ako sa blameless analysis líši od no-accountability?
12. Aké evidence dokazuje, že anti-pattern bol skutočne odstránený?

## 26. Zhrnutie

DevOps anti-patterny nevznikajú iba zo zlých nástrojov alebo jednotlivých chýb. Vznikajú zo systému incentív, hraníc a feedback loops, ktorý lokálne odmeňuje správanie poškodzujúce end-to-end výsledok. Náprava preto musí meniť capability, ownership alebo tok práce a jej účinok sa musí overiť merateľným správaním systému.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DORA metrics](dora-metrics.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Kernel a user space →](../01-linux-and-systems/kernel-and-user-space.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
