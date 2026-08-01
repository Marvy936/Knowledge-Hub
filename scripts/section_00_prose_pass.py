from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "00-foundations"

OPENINGS: dict[str, str] = {
    "sdlc.md": """Software Development Life Cycle nie je iba zoznam fáz medzi požiadavkou a nasadením. Je to riadený chain rozhodnutí a stavov, v ktorom sa musí dať preukázať, prečo zmena vznikla, ktorá verzia požiadavky a návrhu bola implementovaná, aký artifact z nej vznikol, kde bol nasadený a či priniesol zamýšľaný používateľský alebo prevádzkový výsledok.

Užitočný mentálny model preto nezačína slovami `plan → code → deploy`, ale exact change subjectom a evidence chainom:

```text
potreba a očakávaný outcome
→ versionovaná požiadavka a acceptance contract
→ návrh a risk boundaries
→ source change a review
→ build artifact a verification evidence
→ release a deployment generation
→ runtime exposure
→ user/business observation
→ maintenance, recovery alebo retirement
```

Každá šípka predstavuje state transition, ktorá môže uspieť, zlyhať či skončiť s neznámym výsledkom. Zelený build napríklad preukazuje iba vlastnosti konkrétneho build subjectu; nepreukazuje, že produkcia načítala rovnaký artifact ani že používateľ dokončil svoj workflow. SDLC je preto uzavretý feedback system, nie jednosmerná výrobná linka.""",
    "devops.md": """DevOps je socio-technický operating model pre rýchle a spoľahlivé premieňanie zmien na prevádzkový výsledok. Nevzniká tým, že organizácia pomenuje tím `DevOps`, kúpi CI nástroj alebo presunie deployment skripty k vývojárom. Vzniká až vtedy, keď delivery a operations zdieľajú outcome, evidence, rozhodovacie práva a následky svojich technických rozhodnutí.

Mechanizmus možno čítať ako regulačný loop:

```text
business alebo user potreba
→ malá verzovaná zmena
→ automatizované a manuálne dôkazy
→ bounded release decision
→ produkčný outcome a telemetry
→ incident, feedback alebo learning
→ zmena produktu, procesu alebo platformy
```

Flow bez spätnej väzby iba zrýchľuje produkciu chýb. Feedback bez ownershipu vytvára reporty bez nápravy. Automation bez bezpečných boundaries škáluje nesprávny proces. DevOps preto spája kultúru, architektúru, platformu, delivery controls a prevádzkové učenie do jedného systému, ktorého kvalita sa posudzuje podľa lead time, reliability, recovery a schopnosti meniť sa bez heroického zásahu.""",
    "devops-lifecycle.md": """DevOps lifecycle opisuje opakujúci sa tok od zámeru po overený runtime outcome. Názvy fáz ako Plan, Code, Build, Test, Release, Deploy, Operate a Monitor sú orientačné observation points; nie sú to samostatné oddelenia ani povinný lineárny workflow. Jedna zmena sa môže medzi nimi vracať, zastaviť na gate-e alebo byť po produkčnom pozorovaní úplne preformulovaná.

Dôležitejšie než názvy fáz je sledovať identitu a stav tej istej zmeny:

```text
change intent
→ candidate source tree
→ build inputs a artifact
→ verification evidence
→ release manifest
→ environment mutation
→ loaded runtime generation
→ traffic alebo feature exposure
→ business result
```

Ak sa identita medzi krokmi stratí, lifecycle vytvára false-green verdicty. Testy môžu patriť commitu A, artifact commitu B a produkčný tag môže ukazovať na ďalší digest. Continuous lifecycle preto potrebuje traceability, immutable alebo presne versionované subjects, explicitné failure semantics a feedback, ktorý sa vracia k ownerovi schopnému zmeniť systém.""",
    "calms.md": """CALMS je diagnostický rámec pre päť navzájom závislých schopností: Culture, Automation, Lean, Measurement a Sharing. Nie je to maturity checklist, v ktorom organizácia samostatne „splní“ päť položiek. Každá dimenzia mení správanie ostatných a slabá hranica v jednej oblasti môže znehodnotiť zvyšok systému.

Automation napríklad zrýchli deployment, ale bez culture bezpečného priznania chyby sa incidenty skryjú. Measurement vytvorí veľa dashboardov, ale bez Lean práce s WIP a bottleneckmi sa metriky nepremenia na rozhodnutie. Sharing rozšíri runbooky, no bez ownershipu a reálnych rehearsals zostanú neaktuálnou dokumentáciou.

CALMS sa preto používa nad konkrétnym value streamom. Najprv sa určí user alebo business outcome, následne sa sleduje tok práce, rozhodnutia, automation boundaries, dostupné evidence a spôsob učenia. Výsledkom nie je skóre samo osebe, ale hypotéza o tom, ktorý systémový constraint bráni bezpečnejšiemu a rýchlejšiemu flowu.""",
    "three-ways.md": """Three Ways vysvetľujú tri dynamické vlastnosti delivery systému. First Way zlepšuje flow od potreby k používateľovi. Second Way skracuje a spresňuje feedback opačným smerom. Third Way vytvára podmienky pre experimentovanie, učenie a pravidelné zlepšovanie samotného systému práce.

Tieto cesty sa nedajú zaviesť oddelene. Rýchlejší flow bez kvalitného feedbacku zvyšuje defect escape a incident load. Veľmi prísny feedback bez obmedzenia WIP môže iba vytvoriť ďalšie fronty a approvals. Experimentovanie bez bounded blast radiusu a recovery mechanizmu premieňa učenie na nekontrolované riziko.

Praktický model je uzavretý loop:

```text
zmenši batch a obmedz WIP
→ skráť čas k relevantnému pozorovaniu
→ vráť dôkaz k správnemu ownerovi
→ uprav produkt, architektúru alebo proces
→ štandardizuj zlepšenie
→ opakuj s novou hypotézou
```

Three Ways teda nie sú motivačné heslá. Sú návrhom control systemu, v ktorom sa optimalizuje celý value stream, nie lokálna rýchlosť jedného tímu.""",
    "systems-thinking.md": """Systems thinking skúma výsledok ako správanie celého prepojeného systému, nie ako súčet izolovaných komponentov. Systém má boundary, actors, stocks, flows, constraints, delays a feedback loops. Zmena jedného prvku preto môže vytvoriť vzdialený alebo oneskorený dôsledok, ktorý lokálna metrika neukáže.

Pri delivery systéme môže tím zrýchliť coding throughput, no ak security review alebo environment provisioning zostane úzkym miestom, celkový lead time sa nezlepší. Vyšší počet rozpracovaných zmien navyše zväčší queues, context switching a rework. Lokálne „zlepšenie“ tak môže zhoršiť globálny outcome.

Analýza musí pomenovať exact system boundary a jednotku toku, napríklad jednu produkčnú zmenu od prijatej potreby po overené použitie. Potom sa sleduje, kde sa hromadí práca, ktoré rozhodnutia majú delay, čo je authoritative evidence a aké reinforcing alebo balancing loops vznikajú. Systems thinking neznamená analyzovať všetko naraz; znamená zvoliť dostatočne širokú hranicu, aby náprava nepresunula problém do susednej časti systému.""",
    "feedback-loops.md": """Feedback loop je mechanizmus, ktorý z pozorovaného výsledku vytvorí korekciu budúceho správania. Potrebuje sensor alebo observation point, interpretáciu voči očakávaniu, ownera rozhodnutia a actuator, ktorý vie zmeniť systém. Samotný dashboard alebo notifikácia ešte feedback loop nevytvára.

```text
zmena alebo disturbance
→ pozorovanie
→ porovnanie s cieľom alebo invariantom
→ rozhodnutie
→ korekčná akcia
→ nové pozorovanie
```

Kvalitu loopu určujú najmä latency, signal fidelity, scope a authority. Rýchly, ale nesprávny test môže poskytovať škodlivý feedback. Presný incident report doručený o tri mesiace neskôr už nemusí ovplyvniť pôvodné rozhodnutie. Alert bez ownera vytvára noise, zatiaľ čo automatický controller bez safety limits môže zosilniť chybný signál.

Balancing loop smeruje systém k cieľu, napríklad autoscaler pridávajúci kapacitu pri raste queue age. Reinforcing loop sám seba zosilňuje, napríklad timeouty vyvolávajúce retries, ktoré ešte viac preťažia dependency. Diagnostika preto musí rozlíšiť, aký typ loopu pozorujeme a kde možno bezpečne zmeniť jeho gain, delay alebo boundary.""",
    "continuous-improvement.md": """Continuous improvement je disciplinovaný spôsob meniť systém práce na základe explicitnej hypotézy a merateľného výsledku. Neznamená neustále zavádzať nové nástroje ani udržiavať nekonečný backlog „improvements“. Každá zmena musí mať pomenovaný problém, baseline, ownera, bounded experiment a pravidlo, podľa ktorého sa prijme, upraví alebo vráti späť.

Praktický lifecycle je:

```text
pozorovaný problém alebo constraint
→ baseline a causal hypothesis
→ malá bezpečná zmena
→ leading a outcome evidence
→ porovnanie s baseline
→ standardize, iterate alebo revert
→ overenie po čase
```

Bez baseline nemožno odlíšiť zlepšenie od prirodzenej variability. Bez causal hypothesis vzniká change theater: vykoná sa školenie, reorganizácia alebo nový pipeline, no nie je jasné, ktorý mechanizmus mal zmeniť výsledok. Bez následného read-backu sa lokálne úspešný pilot môže pri širšom používaní zmeniť na nový bottleneck.

Continuous improvement preto zahŕňa aj odstránenie neúspešnej zmeny, aktualizáciu štandardu a sledovanie vedľajších účinkov. Cieľom nie je maximalizovať počet iniciatív, ale zvyšovať schopnosť systému učiť sa bez neprimeraného rizika.""",
    "t-shaped-engineer.md": """T-shaped, I-shaped a π-shaped profily opisujú rozloženie odbornosti, nie hodnotu človeka ani pevné pracovné pozície. Vertikálna časť predstavuje hĺbku potrebnú na samostatné riešenie náročných problémov. Horizontálna časť predstavuje dostatočné porozumenie susedných domén na komunikáciu, návrh hraníc a bezpečný handoff.

I-shaped engineer má veľkú hĺbku v jednej oblasti, ale môže mať slabšiu schopnosť orientovať sa mimo nej. T-shaped engineer kombinuje jednu dominantnú hĺbku s praktickým rozhľadom. π-shaped profil má dve výrazné hĺbky, napríklad application engineering a distributed systems. Žiadny profil automaticky nerieši ownership, mentoring ani tímovú redundanciu.

Organizačný význam vzniká až pri mapovaní capability na tím. Ak jediný človek rozumie production database recovery, vzniká key-person risk bez ohľadu na jeho profil. Ak všetci poznajú všetko iba povrchne, tím nemá hĺbku na diagnostiku zložitých failure modes. Cieľom je komplementárna topológia: dostatočná expert depth, spoločný jazyk na hraniciach a mechanizmy, ktoré prenášajú znalosti cez pairing, review, runbooks a rehearsals.""",
    "ownership-mindset.md": """Ownership mindset znamená niesť zodpovednosť za výsledok počas celého relevantného lifecycle-u, nie iba dokončiť pridelenú aktivitu. Owner potrebuje jasný subject, decision rights, rozhrania voči ostatným tímom a evidence, podľa ktorého vie posúdiť, či systém funguje. Bez týchto právomocí sa „ownership“ mení na morálnu požiadavku bez možnosti konať.

Rozdiel je viditeľný pri incidente. Activity ownership končí vetou „deployment job bol zelený“. Outcome ownership pokračuje otázkami, ktorá generation beží, aký traffic ju používa, či business operation dokončuje a ako sa riešia unknown outcomes. Owner neznamená, že všetku prácu vykoná sám; znamená, že zabezpečí koordináciu, rozhodnutie a closure.

Zdravé ownership boundaries zároveň bránia hero culture. Tím vlastní službu alebo capability, nie konkrétny človek 24 hodín denne. Potrebuje shared on-call, dokumentované dependencies, bezpečný escalation path a platform capabilities. Ownership sa preukazuje opakovateľným výsledkom a učením, nie osobnou obetavosťou.""",
    "you-build-it-you-run-it.md": """Princíp `you build it, you run it` spája design a implementation decisions s reálnymi prevádzkovými dôsledkami. Tím, ktorý rozhoduje o architektúre, dependencies, telemetry a rollout-e, má zostať zapojený aj do reliability, supportu a recovery. Tým sa skracuje feedback medzi technickou voľbou a jej dopadom.

Princíp však neznamená, že každý developer musí samostatne spravovať hardware, Kubernetes control plane alebo 24/7 pager. Platform, security, network a database tímy môžu vlastniť shared capabilities, pokiaľ sú ich boundaries a service contracts explicitné. Application tím stále vlastní business behavior, operability svojho workloadu a rozhodnutie, ako reagovať na failure dependency.

Dobrý model oddeľuje vrstvy:

```text
platform owner → bezpečná a podporovaná runtime capability
service owner → application, configuration a business outcome
shared incident command → koordinácia naprieč hranicami
```

Ak sa prevádzka odovzdá bez kontextu, vzniká ticket queue a pomalý learning. Ak sa všetka infraštruktúrna komplexita prenesie na každý product tím, vzniká duplicita a nekonzistentná bezpečnosť. Cieľom je lifecycle accountability s rozumnými platform boundaries, nie zrušenie špecializácie.""",
    "automation-mindset.md": """Automation mindset začína otázkou, ktorý opakovateľný decision alebo state transition má byť bezpečnejší, nie otázkou, ktorý skript napísať. Automatizácia musí mať presný input contract, authoritative state, plánovanú mutáciu, read-back, failure semantics a recovery path. Inak iba zrýchľuje manuálny postup bez kontroly jeho predpokladov.

```text
observe current state
→ validate inputs a identity
→ calculate plan alebo intended action
→ apply bounded mutation
→ read back effective state
→ verify technical a business outcome
→ reconcile, compensate alebo escalate
```

Skript, ktorý skončí exit code `0`, preukazuje iba to, že jeho vlastný execution path neohlásil chybu. Nemusí preukazovať, že vzdialené API operáciu dokončilo, že controller konvergoval alebo že spotrebiteľ načítal novú konfiguráciu. Robustná automation preto rozlišuje request acceptance, persisted state, effective runtime a user outcome.

Automatizovať treba aj forbidden paths, concurrency, retries, partial completion a retirement. Proces bez ownera, merania adoptionu a maintenance plánu sa po čase stane ďalším zdrojom toil-u alebo nebezpečným stale runbookom zakódovaným do pipeline.""",
    "declarative-vs-imperative.md": """Imperatívny prístup opisuje konkrétnu sekvenciu operácií. Deklaratívny prístup opisuje požadovaný výsledný stav a ponecháva mechanizmu, aby vypočítal potrebné zmeny. Rozdiel teda nie je iba syntaktický; mení, kde sa nachádza decision logic, kto vlastní current state a ako sa rieši drift.

Imperatívny postup môže povedať `vytvor server, nainštaluj package, prepíš config a reštartuj službu`. Deklarácia môže povedať `služba má bežať v tejto generation s týmto configuration contractom`. Controller následne porovná desired a observed state, vytvorí plan a opakuje reconciliation, kým systém nedosiahne prijateľnú konvergenciu alebo explicitne nezlyhá.

Deklaratívny model nie je automaticky bezpečnejší. Nesprávny desired state môže controller spoľahlivo rozšíriť na celý fleet. Hidden defaults, mutable dependencies alebo viac writers môžu spôsobiť, že deklarácia nie je úplným source of truth. Imperatívny krok je naopak vhodný pre jednorazové externé side effects, ak má idempotency, journaling a recovery. Voľba preto závisí od state modelu, authority a failure contractu, nie od preferencie YAML verzus shell.""",
    "idempotency.md": """Idempotencia znamená, že opakované vykonanie tej istej logickej operácie má po prvom úspešnom effecte rovnaký relevantný výsledný stav. Neznamená, že request sa vykoná iba raz, že odpoveď bude vždy byte-identická ani že operácia nemá žiadne vedľajšie effects. Rozhodujúce je, ako systém identifikuje jednu logical operation a ktorý effect považuje za autoritatívny.

```text
stable operation identity
+ semantic request fingerprint
+ atomic claim alebo existing-result lookup
→ jeden authoritative effect
→ opakované requesty vracajú kompatibilný outcome
```

Najväčšiu hodnotu má idempotencia pri retries a unknown outcomes. Klient môže stratiť odpoveď po tom, čo server commitol platbu. Blind retry s novým identifierom môže vytvoriť druhý effect; retry s rovnakým keyom umožní serveru nájsť pôvodnú operáciu. Samotný key však nestačí, ak sa dá znovu použiť s iným payloadom, ak vyprší skôr než retry window alebo ak claim a business write nie sú atómové.

Idempotentný API contract musí preto definovať scope identity, retention, concurrency, conflict behavior, response replay a reconciliation s externými systémami. Test zahŕňa paralelný duplicate, retry po stratenej odpovedi, rovnaký key s odlišným payloadom a opakovanie po recovery.""",
    "desired-state-and-reconciliation.md": """Desired state je explicitný opis toho, ako má vybraný subject vyzerať. Observed state je to, čo controller alebo operátor v danom observation point-e skutočne vidí. Reconciliation je opakovaný control loop, ktorý rozdiel vyhodnotí a vykoná bounded action smerujúcu ku konvergencii.

```text
desired generation
→ observe current generation
→ normalize a compare
→ calculate action
→ apply
→ read back
→ repeat alebo report failure
```

Controller nesmie predpokladať, že úspešná API odpoveď znamená dosiahnutý stav. Vytvorenie Deployment objektu napríklad nepreukazuje ready Pods, správny image digest, funkčný dataplane ani business request. Každá vrstva potrebuje vlastný convergence a acceptance oracle.

Reconciliation zároveň rieši drift, ale iba v boundaries, ktoré controller vlastní. Ak rovnaké pole mení GitOps controller, autoscaler aj človek, systém môže oscilovať alebo drift ignorovať. Bez liveness limitu môže controller retryovať navždy; bez safety constraints môže pri oprave odstrániť legitímny state. Dobrý reconciliation model preto definuje authority, field ownership, retry/backoff, terminal conditions, deletion semantics a spôsob recovery po partial alebo unknown apply.""",
    "immutable-vs-mutable-infrastructure.md": """Mutable infrastructure sa mení in place: existujúci server alebo instance dostáva package updates, configuration mutations a ručné opravy. Immutable model vytvorí novú versionovanú generation, overí ju a starú generation nahradí alebo vyradí. Rozdiel je v lifecycle-e identity a recovery, nie v tom, že by immutable systém nikdy nemenil žiadny stav.

```text
mutable:   instance A → patch 1 → patch 2 → emergency edit
immutable: image A → image B → validated replacement → retire A
```

Immutable replacement znižuje configuration drift a uľahčuje reprodukciu, pretože runtime sa viaže na build artifact a deklarovanú konfiguráciu. Zároveň potrebuje externalizovaný durable state, capacity na súbežné generations, bezpečný rollout a kompatibilitu s database či event schema. Databáza, queue alebo filesystem state nemôžu byť bezmyšlienkovite nahradené spolu s compute vrstvou.

Mutable zmena môže byť vhodná pri firmware, veľkých stateful systémoch alebo urgentnom containment-e. Potrebuje však authoritative change record, read-back a následné zosúladenie source of truth, inak vznikne snowflake. Praktická voľba je často hybridná: immutable application compute, deklaratívna konfigurácia a kontrolované mutable data transitions.""",
    "toil-and-technical-debt.md": """Toil a technical debt sú príbuzné, ale odlišné javy. Toil je opakovaná operational práca s nízkou trvalou hodnotou, ktorá je manuálna, reaktívna, automatizovateľná a rastie so službou. Technical debt je budúci náklad vytvorený designovým alebo implementačným rozhodnutím, ktoré zvyšuje cenu ďalších zmien, reliability alebo recovery.

Technical debt môže generovať toil, napríklad chýbajúca idempotencia vytvára každodenné manuálne reconciliation. Nie každý toil však vzniká z dlhu a nie každý dlh okamžite vytvára manuálnu prácu. Povinný audit v regulovanom procese môže byť enduring operational work, zatiaľ čo zastaraná knižnica je debt aj bez aktuálneho incidentu.

Rozhodovanie potrebuje demand model:

```text
frequency × touch time × interruption × risk × growth
→ root operational demand
→ eliminate, redesign, automate, self-service alebo accept
→ verify durable reduction
```

Automatizácia symptómu bez odstránenia root demandu môže iba zrýchliť nebezpečnú operáciu. Splatenie debt-u bez merania outcome-u môže byť technicky príjemné, ale bez business hodnoty. Priorita preto vychádza z dopadu na flow, reliability, security, cost a budúcu schopnosť meniť systém.""",
    "value-stream-mapping.md": """Value stream mapping zobrazuje end-to-end tok jednej jednotky hodnoty od vzniku potreby po overený výsledok. Jeho cieľom nie je nakresliť organizačný proces, ale oddeliť process time od waiting time, odhaliť queues, handoffs, rework, approvals a information gaps, ktoré určujú skutočný lead time.

Najprv sa musí zvoliť stabilná flow unit, napríklad jedna production change určitej triedy. Ak mapa zmieša urgentný hotfix, veľký projekt a rutinnú configuration change, priemery skryjú rozdielne paths a constraints. Pre každý krok sa zaznamenáva vstup, owner, elapsed time, active work, queue, defect/rework a evidence potrebné na pokračovanie.

```text
request
→ waiting
→ analysis
→ waiting
→ implementation
→ review/test queue
→ release decision
→ deployment
→ production verification
```

Najväčší potenciál často neleží v zrýchlení codingu, ale v znížení batch size, WIP, approval latency alebo failure demandu. Po zmene sa mapa vytvorí znovu nad rovnakou population a obdobím; inak nemožno preukázať, že sa zlepšil celý stream namiesto jedného lokálneho kroku.""",
    "dora-metrics.md": """DORA metrics opisujú delivery performance cez Deployment Frequency, Lead Time for Changes, Change Failure Rate a Time to Restore Service alebo Failed Deployment Recovery Time podľa použitej metodiky a dátového contractu. Ich hodnota nevzniká samotným číslom, ale konzistentnou definíciou eventov, population a observation window.

Deployment musí znamenať production change pre definovaný service boundary, nie každý pipeline job. Lead time potrebuje stabilný začiatok a koniec, napríklad commit alebo merge až po successful production deployment. Change failure rate potrebuje explicitne určiť, ktoré deployments vyvolali rollback, fix-forward alebo incident. Recovery metric musí merať obnovenie user capability, nie iba ukončenie incident ticketu.

Metriky tvoria systém trade-offov. Vyššia deployment frequency bez stability nie je úspech; nízky failure rate dosiahnutý obrovskými batchmi a zriedkavými releases môže skrývať veľký risk. DORA metriky sú outcome signals pre trend a segmentáciu, nie individuálne KPI ani automatický dôkaz causality. Zmenu treba porovnávať v rámci rovnakej service/change cohorty a doplniť kvalitatívnym vysvetlením mechanizmu, ktorý trend spôsobil.""",
    "devops-anti-patterns.md": """DevOps anti-pattern je opakujúca sa štruktúra rozhodnutí, ktorá lokálne pôsobí rozumne, ale systematicky zhoršuje flow, feedback, reliability alebo ownership. Nejde iba o zoznam zlých praktík. Anti-pattern sa udržiava reinforcing loopom: problém vyvolá reakciu, reakcia zosilní pôvodnú príčinu a organizácia následne pridá ešte viac tej istej kontroly.

Príkladom je centralizovaná deployment queue. Incident vedie k ďalšiemu approvalu, approval predĺži lead time a zväčší batch, väčší batch zvyšuje risk a ďalší incident legitimizuje ešte prísnejšiu queue. Podobne hero culture krátkodobo zachráni outage, ale obíde dokumentáciu, automation a shared capability, čím sa závislosť od hero človeka ďalej zväčší.

Diagnostika preto začína causal loopom, nie pomenovaním symptómu:

```text
pozorovaný outcome
→ local incentive alebo constraint
→ opakované rozhodnutie
→ system-level consequence
→ feedback, ktorý správanie posilňuje
```

Náprava musí zmeniť mechanizmus: ownership a decision rights, batch/WIP, platform capability, evidence quality alebo incentive. Nahradenie jedného toolu druhým bez zmeny loopu anti-pattern iba prefarbí. Closure vyžaduje opakované meranie flowu, failure demandu, reliability a správania tímov po tom, čo počiatočná pozornosť transformačného programu opadne.""",
}


def remove_legacy_metadata(text: str, path: Path) -> str:
    if "## Metadata" not in text:
        return text

    pattern = re.compile(
        r"\A(?P<title># [^\n]+\n)\n## Metadata\n.*?(?=\n## (?:1\.|[^\n]+))",
        re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise RuntimeError(f"Unable to locate metadata block in {path}")

    return match.group("title") + "\n" + text[match.end() :].lstrip("\n")


def insert_opening(path: Path, opening: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = remove_legacy_metadata(text, path)
    title, separator, remainder = text.partition("\n")
    if not separator:
        raise RuntimeError(f"Missing body in {path}")

    if opening in remainder:
        return

    updated = f"{title}\n\n{opening.strip()}\n\n{remainder.lstrip()}"
    path.write_text(updated.rstrip() + "\n", encoding="utf-8")


def update_section_readme() -> None:
    path = SECTION / "README.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("## Odporúčané poradie", "## Authoritative poradie")

    status_pattern = re.compile(
        r"\n## Stav\n\n\| Téma \| Status \| Úroveň \|\n\|---\|---\|---\|\n(?:\|.*\|\n?)+",
        re.MULTILINE,
    )
    text, count = status_pattern.subn("\n", text)
    if count != 1:
        raise RuntimeError(f"Expected one legacy status table in {path}, found {count}")

    marker = "## Cieľ zvládnutia"
    if marker not in text:
        raise RuntimeError(f"Missing mastery marker in {path}")

    explanation = """## Spôsob spracovania sekcie

Sekcia používa jeden prose-first learning chain od software lifecycle-u cez DevOps flow, feedback a systems thinking až po ownership, automation, state convergence, infrastructure lifecycle a meranie delivery outcome-u. Každá kapitola začína priamo vysvetlením mechanizmu; legacy `Metadata`, `Learning` a `L2` scaffold sa už nepoužíva.

Nosný section model je:

```text
business alebo user potreba
→ versionovaná zmena a value stream
→ flow, feedback a learning controls
→ ownership a automation boundary
→ desired/effective state transition
→ delivery a reliability evidence
→ system-level improvement alebo recovery
```

Príklady a zoznamy sumarizujú už vysvetlený model. Príkaz, metrika alebo procesný krok sa nepovažuje za dôkaz sám osebe; text oddeľuje vykonanú aktivitu, authoritative state, effective runtime a používateľský alebo business outcome. Aktuálny authoritative stav sekcie je **20/20 · Ready for user review** po odstránení legacy štruktúry a chapter-by-chapter explanation-depth passe.

"""
    if "## Spôsob spracovania sekcie" not in text:
        text = text.replace(marker, explanation + marker, 1)

    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def update_review_ledger() -> None:
    path = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
    text = path.read_text(encoding="utf-8")
    replacement = (
        "| `00-foundations` — DevOps Foundations | 20/20 integrated prose and explanation-depth revalidation | "
        "Ready for user review | 2026-08-01 | Všetkých 20 authoritative kapitol už nepoužíva legacy `Metadata`, "
        "`Status: Learning`, `Úroveň: L2` ani section-level Learning/L2 tabuľku. Každá kapitola začína priamo "
        "subject-specific prose vysvetlením problému, mechanizmu, state/evidence boundary a praktického dôsledku. "
        "Sekcia drží jeden chain od SDLC a DevOps operating modelu cez flow, feedback, systems thinking, continuous "
        "improvement, capability topology a lifecycle ownership až po safe automation, declarative/imperative state, "
        "idempotency, reconciliation, infrastructure generations, toil/debt, value-stream evidence, DORA metrics a "
        "causal anti-pattern loops. Silný existujúci odborný obsah a worked scenáre zostali zachované; nový výklad je "
        "integrovaný pred pôvodné podkapitoly a zoznamy zostávajú iba ako summary alebo reference. README ordering, "
        "navigation, glossary a full documentation audit boli synchronizované. Sekcia je pripravená na používateľskú "
        "kontrolu, nie automaticky Accepted, Verified ani Stable. |"
    )

    pattern = re.compile(r"^\| `00-foundations`.*$", re.MULTILINE)
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"Expected one Section 00 ledger row in {path}, found {count}")

    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def validate() -> None:
    expected = set(OPENINGS)
    actual = {path.name for path in SECTION.glob("*.md") if path.name != "README.md"}
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise RuntimeError(f"Section 00 inventory mismatch; missing={missing}, extra={extra}")

    forbidden = ("## Metadata", "Status: Learning", "Úroveň: L2")
    for name, opening in OPENINGS.items():
        text = (SECTION / name).read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                raise RuntimeError(f"Legacy token {token!r} remains in {name}")
        if opening not in text:
            raise RuntimeError(f"Integrated opening missing in {name}")

    readme = (SECTION / "README.md").read_text(encoding="utf-8")
    if "## Stav" in readme or "| Learning | L2 |" in readme:
        raise RuntimeError("Legacy Section 00 status table remains")
    if "## Spôsob spracovania sekcie" not in readme:
        raise RuntimeError("Section 00 README explanation standard missing")


def main() -> None:
    for name, opening in OPENINGS.items():
        insert_opening(SECTION / name, opening)

    update_section_readme()
    update_review_ledger()
    validate()


if __name__ == "__main__":
    main()
