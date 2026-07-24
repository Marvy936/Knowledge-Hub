# Package Management

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Filesystem hierarchy, inodes a links](filesystem-hierarchy-inodes-links.md), [Users, groups, permissions, sudo a PAM](users-groups-permissions-sudo-pam.md)
- Súvisiace témy: repositories, dependency resolution, supply-chain security, immutable infrastructure

## 1. Čo package management skutočne riadi

Package management je systém, ktorý premieňa repository policy a požadovaný software stav na kontrolovanú transakciu nad lokálnym systémom. Nejde iba o rozbalenie archívu; package manager rozhoduje o verzii, architektúre, dependencies, conflicts, trust policy, lifecycle scripts a evidencii vlastníctva súborov.

Balík preto obsahuje viac vrstiev:

- **payload súborov —** executable, knižnice, unit files, dokumentáciu a ďalšie dáta, ktoré sa majú umiestniť do filesystemu,
- **identity balíka —** názov, verzia, release, architektúra a package format, podľa ktorých solver rozlišuje kandidátov,
- **dependency metadata —** požadované capabilities, version constraints, conflicts, provides a obsoletes vzťahy,
- **integrity metadata —** checksums a podpisové informácie, ktoré spájajú artifact s repository trust chain,
- **lifecycle scripts —** kód spustený pred alebo po install, upgrade či remove, ktorý môže meniť aj runtime stav systému,
- **local database records —** evidencia, ktoré súbory a metadata patria konkrétnej nainštalovanej verzii.

## 2. High-level a low-level vrstva

Bežná distribúcia oddeľuje orchestration od lokálnej package database.

```text
APT / DNF / Zypper
  ├── repository policy
  ├── metadata cache
  ├── candidate selection
  ├── dependency solver
  └── transaction orchestration
              ↓
DPKG / RPM database
  ├── local package state
  ├── file ownership
  ├── unpack/configure phases
  └── lifecycle scripts
```

`dpkg -i package.deb` alebo `rpm -i package.rpm` pracuje najmä s konkrétnym lokálnym artifactom. High-level manager navyše prehľadá repositories, vyberie kompatibilné verzie a zostaví konzistentný dependency graph.

Toto rozlíšenie vysvetľuje, prečo lokálny install môže skončiť v stave „balík rozbalený, ale dependencies chýbajú“. Low-level nástroj pozná lokálnu transakciu, no nemusí mať policy ani vzdialené metadata potrebné na doplnenie celého graphu.

## 3. Repository je policy boundary

Repository nie je iba webový adresár s balíkmi. Obsahuje indexy, verzie, architektúry, signatures a často aj distribution component alebo release channel, ktoré určujú, z akého trust a compatibility priestoru môže package manager vyberať.

```bash
sudo apt update
sudo apt install nginx
```

`apt update` obnoví lokálnu cache repository metadata. Nenainštaluje nové verzie; pripraví aktuálny pohľad, z ktorého ďalšia transakcia vyberá kandidátov.

Ak je cache stará, package manager môže rozhodovať podľa verzií, ktoré už repository neposkytuje, alebo nevidieť novú security opravu. Synchronizácia metadata je preto samostatná fáza od samotného installu či upgrade.

## 4. End-to-end tok transakcie

```text
repository configuration
      ↓
metadata download a signature verification
      ↓
candidate version selection
      ↓
dependency solving
      ↓
transaction plan
      ↓
package download a checksum verification
      ↓
lock local database
      ↓
unpack / configure / scripts
      ↓
update local package state
      ↓
post-transaction runtime effects
```

Každá fáza má vlastný failure model. Metadata download môže zlyhať na trust alebo network vrstve, solver na nekompatibilnom grafe, unpack na nedostatku miesta a lifecycle script na aplikačnej alebo service chybe.

Preto hlásenie „package install failed“ nestačí. Diagnostika musí identifikovať, v ktorej fáze transakcia skončila a aký čiastočný stav po nej zostal.

## 5. Dependency solver hľadá konzistentný výsledný stav

Dependency nie je iba meno ďalšieho balíka. Môže požadovať minimálnu alebo maximálnu verziu, virtuálnu capability, konkrétnu architektúru alebo zároveň zakazovať konfliktujúci package.

Solver preto rieši constraint problem:

```text
požadovaný package
  + dostupné candidates
  + version policy
  + dependencies
  + conflicts
  + installed state
  = konzistentný transaction plan
```

Ak dva balíky vyžadujú navzájom nezlučiteľné verzie knižnice, nejde o „náhodnú chybu aptu“. Solver nedokáže nájsť výsledný stav spĺňajúci všetky constraints.

## 6. Package dependency a runtime dependency nie sú totožné

Package dependency je vzťah deklarovaný maintainerom a viditeľný solveru. Runtime dependency je čokoľvek, čo program skutočne potrebuje na fungovanie: shared library, executable, kernel feature, service endpoint, locale data alebo konfiguráciu.

Maintainer môže runtime dependency zabudnúť deklarovať alebo ju package format nemusí vedieť presne vyjadriť. Package manager potom úspešne dokončí transakciu, ale aplikácia môže pri štarte zlyhať.

Package installation teda preukazuje konzistenciu package graphu, nie funkčnosť celej služby.

## 7. Candidate version vzniká z precedence policy

Nainštalovaná verzia, najnovšia verzia v jednom repository a výsledná candidate verzia môžu byť tri odlišné hodnoty. Výber ovplyvňuje distribution release, repository priority, pinning, module stream, architecture a explicitný version request.

```bash
apt-cache policy nginx
dnf info nginx
```

Tieto príkazy pomáhajú vysvetliť, prečo solver vybral konkrétny artifact. Bez kontroly candidate policy môže administrátor omylom miešať packages z odlišných release channels alebo očakávať upstream verziu, ktorú distribúcia zámerne neponúka.

## 8. Pinning a version lock sú stability policy

Pin alebo version lock obmedzí, ktoré candidates solver smie zvoliť. Používa sa pri reprodukovateľnosti, compatibility contracte alebo postupnom rolloute, no zároveň môže blokovať security update alebo vytvoriť neudržateľný dependency graph.

Každý lock má preto potrebovať ownera, dôvod a review condition. „Držať package navždy“ bez sledovania advisories je technický dlh, nie bezpečnostná stratégia.

## 9. Update, upgrade a distribution upgrade riešia iné scope-y

Pri APT:

```bash
sudo apt update
sudo apt upgrade
sudo apt full-upgrade
```

`update` obnoví metadata cache. `upgrade` aktualizuje installed packages v konzervatívnejšom grafe. `full-upgrade` môže na vyriešenie dependencies packages aj pridať alebo odstrániť.

Major distribution upgrade je širšia migrácia repository sources, base packages, boot stacku a compatibility assumptions. Vyžaduje vlastný preflight, backup a recovery plán; nie je iba „väčší apt upgrade“.

## 10. Local package database je evidovaný installed state

Low-level database zaznamenáva, ktoré package versions sú installed, configured alebo v čiastočnom stave a ktoré paths vlastní každý package.

```bash
dpkg -S /usr/bin/ssh
dpkg -L openssh-client
rpm -qf /usr/bin/ssh
rpm -ql openssh-clients
```

Táto evidencia umožňuje odlíšiť package-managed súbor od manuálne pridaného artifactu. Ručná zmena package-owned súboru môže byť pri upgrade prepísaná, zachovaná ako konfiguračná výnimka alebo vyvolať conflict podľa pravidiel konkrétneho formátu.

Local database je source of truth package managera, nie úplná source of truth celého filesystemu. Súbory môžu vzniknúť aj mimo nej cez aplikácie, administrátora alebo build tooling.

## 11. Unpack a configure môžu byť oddelené fázy

Najmä v DPKG modeli môže byť package rozbalený, ale ešte nenakonfigurovaný. Payload už existuje na disku, no post-install script, dependency configuration alebo service integration neprebehli úspešne.

To vytvára čiastočný stav, v ktorom súbory existujú, ale package manager transakciu nepovažuje za dokončenú. Recovery príkazy ako `dpkg --configure -a` preto nedownloadujú všetko odznova; pokúšajú sa dokončiť pending configuration fázu.

## 12. Lifecycle scripts sú privilegované side effects

Package scripts môžu vytvoriť usera, rebuildnúť cache, reloadnúť systemd, migrovať dáta alebo reštartovať službu. Inštalácia teda môže meniť runtime stav aj vtedy, keď administrátor očakáva iba nové súbory.

Pred produkčným rolloutom treba vedieť:

- **či skript vyžaduje interakciu —** automatizácia musí nastaviť non-interactive policy alebo failnúť kontrolovane,
- **či sa služba automaticky reštartuje —** update knižnice môže aktivovať nový runtime skôr, než je pripravené maintenance window,
- **či skript mení dáta —** databázová migrácia môže byť nevratná aj pri downgrade package,
- **či je operácia idempotentná —** recovery po prerušení môže script spustiť znova,
- **aké externé dependencies používa —** DNS, network alebo service outage môže zablokovať konfiguráciu package.

## 13. Package install a service activation sú rozdielne operácie

Balík môže nainštalovať systemd unit, ale to neznamená, že služba je enabled, started alebo healthy. Naopak package script ju môže podľa distribution policy automaticky spustiť.

Po transakcii treba explicitne overiť:

```text
package state
→ unit definition loaded
→ service runtime state
→ application readiness
```

Package manager potvrdí software state. `systemd` potvrdí unit lifecycle a aplikačný health check potvrdí funkčný outcome.

## 14. Trust chain overuje pôvod a integritu

Typická trust chain vyzerá takto:

```text
trusted repository key
      ↓ verifies
repository metadata
      ↓ names checksum/version
package artifact
      ↓ installed into
local package state
```

Podpis preukazuje, že metadata alebo artifact zodpovedajú držiteľovi dôveryhodného kľúča a neboli zmenené mimo povoleného procesu. Nepreukazuje, že package nemá zraniteľnosť ani že dôveryhodný maintainer neurobil chybu.

Pridanie third-party repository preto rozširuje execution trust na jeho maintainera a signing infrastructure. Package scripts typicky bežia s vysokými privileges, takže kompromitovaný repository key je priamy supply-chain risk.

## 15. Checksums a signatures riešia rozdielne otázky

Checksum odpovedá, či bytes zodpovedajú očakávanej hodnote v metadata. Signature odpovedá, či metadata alebo artifact schválila identita dôveryhodná podľa lokálnej policy.

Checksum bez dôveryhodne podpísaného source možno útočníkom nahradiť spolu s artifactom. Signature bez správnej key lifecycle policy môže dôverovať zastaranému alebo kompromitovanému kľúču.

## 16. Lock chráni transakčnú konzistenciu

Package database sa pri mutácii zamyká, aby dve súbežné transakcie nemenili rovnaké records a filesystem state v nekompatibilnom poradí.

Ak sa zobrazí lock error, správny postup je identifikovať držiteľa a jeho stav. Automatický update môže legitímne pracovať; násilné zmazanie lock file neukončí proces ani neopraví rozpracovanú transakciu.

```text
lock conflict
→ identifikuj owner process
→ zisti, či transakcia napreduje
→ počkaj alebo kontrolovane ukonči
→ audituj partial state
→ spusti recovery
```

## 17. Prerušená transakcia zanecháva vrstvený stav

Failure môže nastať po download, počas unpacku alebo v lifecycle scripte. Recovery preto závisí od poslednej úspešnej fázy.

Na Debian/Ubuntu:

```bash
dpkg --audit
sudo dpkg --configure -a
sudo apt --fix-broken install
```

`dpkg --audit` hľadá nekonzistentné package states. `--configure -a` dokončuje pending configuration a `--fix-broken install` sa pokúša zostaviť konzistentný dependency graph.

Na RPM/DNF systémoch:

```bash
dnf check
dnf history
dnf history info <ID>
rpm -Va
```

`dnf history` poskytuje transakčný kontext a `rpm -Va` porovnáva filesystem attributes s package metadata. Verification difference však nemusí byť chyba; konfiguračný súbor mohol byť zámerne zmenený.

## 18. Rollback package transakcie má limity

Downgrade artifactu nemusí vrátiť celý systém. Lifecycle script mohol migrovať databázu, odstrániť starý formát konfigurácie alebo reštartovať service s novým state.

Skutočný recovery model preto musí rozlišovať:

- **package rollback —** návrat binaries a package metadata,
- **configuration rollback —** návrat kompatibilného config contractu,
- **data rollback —** obnova alebo forward migration dát,
- **service rollback —** kontrolovaný runtime transition a health verification.

Immutable replacement často zjednoduší compute rollback, ale stateful dependencies zostávajú samostatným problémom.

## 19. Security updates a upstream version numbers

Distribúcie často backportujú security fix do staršej upstream verzie bez zmeny major version stringu. Porovnanie iba s posledným release na upstream webe preto môže nesprávne označiť patched distribution package za zastaraný.

Autoritatívne sú distribution advisory, changelog a package release metadata. Security rozhodnutie musí vychádzať z konkrétneho build-u, nie iba z marketingového upstream čísla.

## 20. Produkčný update workflow

Bezpečný workflow spája package state s prevádzkovým outcome:

1. **Definuj schválené repositories a versions.** Repository a pinning policy musia byť verzované a auditovateľné.
2. **Vytvor transaction plan.** Zisti packages, removals, services a reboot-relevant components, ktoré sa zmenia.
3. **Testuj reprezentatívny systém.** Over install scripts, service startup, data compatibility a smoke tests.
4. **Rolloutni v malom batchi.** Canary host alebo nový image obmedzí blast radius.
5. **Over runtime outcome.** Package transaction success nestačí; skontroluj service health a používateľské signály.
6. **Zachovaj recovery path.** Cache artifactov, image replacement alebo snapshot musí zodpovedať aj configuration a data modelu.
7. **Odstráň zastaraný state.** Staré images, nepodporované repositories a hold výnimky potrebujú lifecycle.

## 21. Mutable a immutable model

V mutable modeli package manager mení existujúci host in-place. Výsledok závisí od jeho histórie, partial updates a lokálnych výnimiek.

V immutable modeli sa packages nainštalujú počas image build-u. Image sa otestuje a hosty sa nahradia, takže package transaction sa presunie z produkčného runtime do reprodukovateľnej build pipeline.

Package manager zostáva rovnaký mechanizmus, ale mení sa failure boundary a rollback stratégia.

## 22. Časté omyly

### „apt update aktualizuje systém“

Nie. Aktualizuje lokálnu repository metadata cache. Installed state sa zmení až samostatnou transaction operáciou.

### „Najvyššie version number je vždy najbezpečnejšie“

Nie. Distribution môže mať backportnutú opravu v nižšom upstream čísle. Rozhodujú konkrétne advisory a package release metadata.

### „Podpísaný package je bezpečný“

Podpis preukazuje pôvod a integritu podľa trust policy. Nehodnotí kvalitu kódu ani absenciu zraniteľností.

### „Zmazanie lock file opraví package manager“

Nie. Lock chráni aktívnu transakciu a jeho file nemusí byť samotným kernel lockom. Najprv treba vyriešiť owner process a partial state.

### „Úspešný install znamená funkčnú službu“

Nie. Package state, systemd state a application readiness sú tri samostatné vrstvy, ktoré treba overiť.

## 23. Kontrolné otázky

1. Aký je rozdiel medzi high-level package managerom a low-level package database?
2. Prečo `apt update` nemení installed package versions?
3. Čo presne rieši dependency solver?
4. Ako sa líši package dependency od runtime dependency?
5. Prečo môže package downgrade zlyhať ako úplný rollback?
6. Čo podpis repository metadata preukazuje a čo nepreukazuje?
7. Prečo sa lock file nemá mazať naslepo?
8. Ako by si overil, že package update skutočne zlepšil produkčný systém?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: systemd, services a daemons](systemd-services-daemons.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: journald a logging →](journald-and-logging.md)
<!-- KNOWLEDGE-NAVIGATION:END -->