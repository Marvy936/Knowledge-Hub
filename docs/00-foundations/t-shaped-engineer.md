# T-shaped Engineer

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [DevOps](devops.md)
- Súvisiace témy: skill matrix, systems thinking, ownership, platform engineering, career development

## 1. Definícia

T-shaped engineer má široký pracovný prehľad naprieč viacerými disciplínami a zároveň hlbokú expertízu v jednej alebo niekoľkých oblastiach.

```text
Šírka znalostí
────────────────────────────────────────────
        │
        │
        │ Hĺbka expertízy
        │
        │
```

Horizontálna časť písmena T umožňuje rozumieť celému systému a spolupracovať naprieč rolami. Vertikálna časť umožňuje riešiť komplexné problémy do potrebnej hĺbky.

## 2. Problém, ktorý rieši

Moderné systémy prekračujú hranice jednej technológie. Incident v Kubernetes môže mať koreňovú príčinu v:

- DNS,
- TLS,
- Linux cgroups,
- cloud networkingu,
- databáze,
- CI/CD konfigurácii,
- aplikačnom kóde.

Čisto úzka špecializácia môže viesť k tomu, že odborník rozumie svojej vrstve, ale nevie správne lokalizovať problém v širšom systéme. Čisto široký profil zasa môže chýbať hĺbka potrebná na návrh alebo diagnostiku náročných riešení.

T-shaped model kombinuje obe potreby.

## 3. T-shaped profil DevOps engineera

Príklad horizontálnej šírky:

```text
SDLC
Git
Linux
Networking
Security
CI/CD
Cloud
Containers
Kubernetes
Observability
Databases
Automation
SRE
```

Príklad vertikálnej hĺbky:

```text
Kubernetes platforma
  ├── control plane
  ├── networking
  ├── storage
  ├── scheduling
  ├── security
  ├── upgrades
  └── troubleshooting
```

Iný DevOps engineer môže mať rovnakú šírku, ale hĺbku v AWS networkingu, Terraform platforme alebo CI/CD architektúre.

## 4. Šírka neznamená povrchnosť

Šírka má vytvoriť použiteľný systémový model. Pri susednej oblasti by mal engineer minimálne vedieť:

- čo táto oblasť rieši,
- aké má hlavné komponenty,
- aké sú jej vstupy a výstupy,
- ako sa prejavuje zlyhanie,
- kde nájsť dôkazy,
- kedy je potrebný špecialista.

Napríklad pri databázach DevOps engineer nemusí vedieť navrhovať komplexný query planner, ale mal by rozumieť:

- transakciám,
- connection poolingu,
- indexom,
- locks,
- replikácii,
- backupu a restore,
- prevádzkovým metrikám.

Takáto šírka umožňuje správne rozpoznať hranice problému.

## 5. Hĺbka neznamená izoláciu

Hlboká expertíza nie je iba poznanie syntaxe. Zahŕňa:

- interné mechanizmy,
- failure modes,
- tradeoffs,
- performance charakteristiky,
- bezpečnostné hranice,
- produkčný lifecycle,
- troubleshooting,
- návrh a obhajobu riešenia.

Príklad hĺbky v Terraform:

```text
L1: viem definovať resource
L2: rozumiem desired state a dependency graphu
L3: viem vytvoriť modul a remote backend
L4: viem riešiť drift, import a state recovery
L5: viem navrhnúť bezpečný multi-account workflow a obhájiť tradeoffs
```

Vertikálna hĺbka má byť napojená na širší kontext delivery systému.

## 6. Porovnanie profilov

### I-shaped engineer

I-shaped engineer má hlbokú expertízu v jednej oblasti, ale obmedzený prehľad mimo nej.

```text
        │
        │
        │
        │
        │
```

Výhody:

- vysoká technická hĺbka,
- schopnosť riešiť špecializované problémy,
- silná doménová expertíza.

Riziká:

- slabšia spolupráca cez systémové hranice,
- lokálna optimalizácia,
- závislosť na handoffoch,
- ťažšia diagnostika multi-layer problémov.

### T-shaped engineer

```text
────────────────────────
          │
          │
          │
```

Výhody:

- systémové porozumenie,
- jedna hlboká expertíza,
- lepšia spolupráca,
- schopnosť lokalizovať problémy.

Riziko:

- príliš široký scope môže spomaliť budovanie skutočnej hĺbky.

### π-shaped engineer

π-shaped engineer má široký prehľad a dve hlboké oblasti.

```text
────────────────────────
     │             │
     │             │
     │             │
```

Príklad:

- hĺbka v Kubernetes,
- hĺbka v AWS networkingu.

Takýto profil môže byť veľmi hodnotný, ak sa dve expertízy vzájomne dopĺňajú.

### Comb-shaped engineer

Comb-shaped profil má viacero hlbokých vertikál. V praxi vzniká dlhodobým rozvojom, nie snahou naučiť sa všetko naraz.

```text
────────────────────────
  │    │      │     │
  │    │      │     │
```

Rizikom je rozptýlenie a neudržateľná snaha udržať expertnú hĺbku vo veľkom počte rýchlo sa meniacich oblastí.

## 7. T-shaped tím, nie iba jednotlivec

Nie je potrebné, aby každý člen tímu mal rovnakú hĺbku. Dôležité je, aby sa vertikály členov dopĺňali.

```text
Engineer A: Kubernetes
Engineer B: Application runtime
Engineer C: Networking and security
Engineer D: Data platform

Spoločná horizontála:
SDLC, Git, delivery, observability, incident response
```

Tím má potom širšiu kolektívnu schopnosť než ktorýkoľvek jednotlivec.

T-shaped tím znižuje:

- knowledge silos,
- bottleneck jedného experta,
- počet slepých handoffov,
- bus factor.

## 8. Vzťah k DevOps

DevOps vyžaduje spoluprácu naprieč vývojom, prevádzkou, bezpečnosťou a business kontextom. T-shaped profil túto spoluprácu podporuje, pretože engineer dokáže:

- chápať dopad svojej zmeny na ďalšie vrstvy,
- formulovať problém v jazyku iného tímu,
- rozlíšiť symptóm od root cause,
- zapojiť správneho špecialistu,
- navrhnúť riešenie s ohľadom na celý lifecycle.

T-shaped model však neznamená, že každý musí vedieť vykonávať všetky roly.

## 9. Ako budovať horizontálnu šírku

Šírka sa buduje cez fundamenty a rozhrania medzi systémami.

Odporúčaný základ pre DevOps:

1. SDLC a DevOps princípy
2. Linux
3. Networking a DNS
4. Git
5. Testing a CI/CD
6. Security a identity
7. Containers
8. Kubernetes
9. Cloud
10. Observability
11. Databases
12. SRE a incident management

Pri každej oblasti je cieľom L2 až L3:

- rozumiem mechanizmu,
- viem použiť základné nástroje,
- viem identifikovať bežné failure modes.

## 10. Ako budovať vertikálnu hĺbku

Hĺbka vzniká opakovaným cyklom:

```text
Teória
  ↓
Praktická implementácia
  ↓
Zlyhanie a troubleshooting
  ↓
Produkčné tradeoffs
  ↓
Vysvetlenie a obhajoba
  ↓
Opakovanie na zložitejšom scenári
```

Samotné čítanie dokumentácie zvyčajne vytvorí L1 alebo L2. Hĺbka L4 a L5 vyžaduje diagnostiku, návrh a skúsenosť s následkami rozhodnutí.

## 11. Skill matrix

Skill matrix pomáha odlíšiť pocit znalosti od konkrétnej schopnosti.

Príklad:

| Oblasť | Aktuálna úroveň | Cieľ | Dôkaz |
|---|---:|---:|---|
| Linux | L3 | L4 | diagnostika CPU, memory a process problémov |
| Networking | L2 | L3 | samostatný DNS a routing lab |
| Terraform | L4 | L5 | návrh multi-environment workflow |
| Kubernetes | L3 | L4 | CKA a troubleshooting labs |
| Databases | L1 | L2 | transakcie, backup a connection pooling |

Dôkaz je dôležitejší než subjektívne označenie „poznám“.

## 12. Prepojenie s týmto Knowledge Hubom

Knowledge Hub používa úrovne:

```text
L0 — tému nepoznám
L1 — viem ju definovať
L2 — rozumiem mechanizmu
L3 — viem ju prakticky použiť
L4 — viem ju diagnostikovať
L5 — viem navrhnúť a obhájiť riešenie
```

Horizontálna časť T profilu má pri kľúčových susedných témach dosiahnuť približne L2 až L3.

Vertikálna časť má v jednej alebo niekoľkých strategických oblastiach smerovať k L4 až L5.

## 13. Príklad scenára

Symptóm: aplikácia v Kubernetes nedokáže komunikovať s databázou.

Čisto nástrojový prístup:

```text
Pod nefunguje → reštartovať Pod
```

T-shaped prístup skúma vrstvy:

```text
Aplikácia
  ├── správny connection string?
  ├── timeout alebo authentication error?
Kubernetes
  ├── Secret a environment?
  ├── NetworkPolicy?
DNS
  ├── resolvuje hostname?
Network
  ├── routing, firewall, security group?
TLS
  ├── certifikát a trust chain?
Database
  ├── listener, user, connection limit, locks?
Observability
  └── logs, metrics, traces a časová korelácia?
```

Engineer nemusí byť expert v každej vrstve. Šírka mu však umožní vytvoriť správny diagnostický strom a nevykonávať náhodné zásahy.

## 14. T-shaped profil a pohovor

Cieľom T-shaped učenia nie je memorovať odpovede. Pri technickej diskusii sa prejaví schopnosť:

- začať presným mentálnym modelom,
- vysvetliť mechanizmus,
- pomenovať závislosti,
- identifikovať failure modes,
- navrhnúť spôsob overenia,
- uviesť tradeoffs.

Takýto profil je obhájiteľný aj bez toho, aby bola každá technológia hlavnou expertízou.

## 15. Anti-patterny osobného rozvoja

### Tutorial hopping

Človek prechádza veľa kurzov, ale nevytvára hlboké projekty, labs ani troubleshooting skúsenosť.

### Tool collector

Zoznam nástrojov rastie, ale chýbajú fundamenty a porozumenie, prečo sa nástroje používajú.

### Syntax-first learning

Učenie sa sústreďuje na príkazy a YAML bez pochopenia objektového modelu, state transitions a failure modes.

### Nekonečná šírka

Človek stále začína nové témy a odkladá výber oblasti, v ktorej bude budovať hĺbku.

### Jedna technológia ako identita

Engineer viaže svoju hodnotu na konkrétny produkt. Keď sa architektúra alebo nástroj zmení, chýba prenositeľný systémový model.

### Certifikácia bez praktického dôkazu

Certifikácia môže štruktúrovať učenie, ale sama nepreukazuje troubleshooting ani návrhovú schopnosť.

## 16. Produkčný kontext

V produkčnom tíme sa T-shaped schopnosti podporujú cez:

- pairing,
- rotáciu on-call,
- code a infrastructure review,
- spoločné incidenty a postmortems,
- interné technical talks,
- communities of practice,
- dokumentované service ownership,
- labs a game days,
- rozumnú rotáciu úloh.

Rotácia bez mentoringu môže vytvoriť iba povrchnosť. Hĺbka potrebuje stabilný čas, ownership a reálne problémy.

## 17. Praktický plán osobného rozvoja

### Krok 1 — Urči horizontálny baseline

Pre každú hlavnú DevOps doménu stanov aktuálnu úroveň L0 až L5.

### Krok 2 — Vyber vertikálu

Vertikála má zodpovedať:

- pracovným potrebám,
- dlhodobému záujmu,
- dostupnosti praktických projektov,
- hodnote pre tím.

### Krok 3 — Definuj dôkaz zvládnutia

Napríklad:

```text
Nie: „Prečítal som Kubernetes networking.“
Áno: „Vytvoril som lab s chybným Service selectorom,
      DNS problémom a NetworkPolicy a diagnostikoval som ich.“
```

### Krok 4 — Prepájaj témy

Každá hlboká téma má odkazovať na susedné fundamenty. Kubernetes networking napríklad prepája Linux network namespaces, CNI, DNS, routing a network policy.

### Krok 5 — Pravidelne aktualizuj profil

T-shaped profil nie je statický. Potreby organizácie aj technológie sa menia.

## 18. Časté omyly

### „T-shaped znamená byť expert na všetko“

Nie. Horizontála je pracovné porozumenie, vertikála je skutočná hĺbka.

### „Špecialisti už nie sú potrební“

Nie. Komplexné systémy potrebujú hlbokých špecialistov. T-shaped model zlepšuje ich systémový kontext a spoluprácu.

### „Každý DevOps engineer má mať rovnakú vertikálu“

Nie. Tím je silnejší, keď sa vertikály dopĺňajú.

### „Certifikácia automaticky vytvorí vertikálnu hĺbku“

Nie. Certifikácia môže pokryť syllabus, ale hĺbka zahŕňa failure modes, prevádzku a návrhové tradeoffs.

### „Šírka sa dá získať iba rokmi v každej roli“

Nie. Základný systémový model možno budovať cielene cez labs, incident analysis, dokumentáciu a spoluprácu. Produkčná skúsenosť však zostáva dôležitá pre vyššie úrovne.

## 19. Kontrolné otázky

1. Čo predstavuje horizontálna a vertikálna časť písmena T?
2. Aký je rozdiel medzi I-shaped a T-shaped profilom?
3. Čo znamená π-shaped engineer?
4. Prečo šírka neznamená znalosť iba definícií?
5. Aký dôkaz by preukázal L4 úroveň v Kubernetes?
6. Prečo je T-shaped tím dôležitejší než identické profily jednotlivcov?
7. Ako môže prílišná šírka poškodiť rozvoj?
8. Prečo syntax-first learning nevytvára hlbokú expertízu?
9. Aké oblasti by mali tvoriť horizontálny baseline DevOps engineera?
10. Ktorú oblasť chceš mať ako svoju hlavnú vertikálu a aký praktický dôkaz ju potvrdí?

## 20. Zhrnutie

- T-shaped engineer kombinuje široký systémový prehľad s hlbokou expertízou.
- Horizontála umožňuje spoluprácu, lokalizáciu problémov a chápanie závislostí.
- Vertikála umožňuje riešiť komplexné problémy, diagnostikovať a navrhovať riešenia.
- I-shaped profil má jednu hĺbku bez výraznej šírky; π-shaped profil má dve hĺbky.
- Tím má mať spoločnú horizontálu a dopĺňajúce sa vertikály.
- Hĺbka vzniká cez implementáciu, zlyhania, troubleshooting a obhajobu tradeoffov.
- Knowledge Hub má budovať horizontálu naprieč DevOps a L4 až L5 hĺbku vo vybraných oblastiach.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Continuous improvement](continuous-improvement.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ownership mindset →](ownership-mindset.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
