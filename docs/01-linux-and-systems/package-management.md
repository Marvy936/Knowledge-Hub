# Package Management

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Filesystem hierarchy, inodes a links](filesystem-hierarchy-inodes-links.md), [Users, groups, permissions, sudo a PAM](users-groups-permissions-sudo-pam.md)
- Súvisiace témy: repositories, dependency resolution, supply-chain security, immutable infrastructure

## 1. Definícia

Package management je systém na distribúciu, overovanie, inštaláciu, aktualizáciu a odstraňovanie softvéru spolu s jeho metadátami a závislosťami.

Balík nie je iba archív so súbormi. Typicky obsahuje:

- payload súborov,
- názov, verziu a architektúru,
- zoznam dependencies a conflicts,
- checksums a podpisové informácie,
- lifecycle scripts,
- ownership informáciu pre package database.

## 2. Dve vrstvy package managementu

Na bežnej distribúcii existujú dve odlišné vrstvy:

```text
High-level package manager
APT / DNF / Zypper
  ├── repositories
  ├── dependency solver
  ├── download a policy
  └── orchestration transakcie
            ↓
Low-level package database
DPKG / RPM
  ├── lokálna evidencia balíkov
  ├── rozbalenie payloadu
  ├── lifecycle scripts
  └── vlastníctvo súborov
```

Príklady:

| Rodina | High-level nástroj | Low-level formát/nástroj |
|---|---|---|
| Debian/Ubuntu | `apt` | `.deb`, `dpkg` |
| RHEL/Fedora | `dnf` | `.rpm`, RPM database |
| SUSE | `zypper` | `.rpm`, RPM database |

`dpkg -i package.deb` alebo `rpm -i package.rpm` pracuje primárne s konkrétnym lokálnym balíkom. Nemusí automaticky vyriešiť všetky vzdialené dependencies. High-level nástroj rieši celý dependency graph a repositories.

## 3. Repository a metadata

Repository obsahuje balíky a index metadát. Package manager najprv synchronizuje metadata a až potom podľa nich rozhoduje, ktorú verziu stiahne.

Pri APT:

```bash
sudo apt update
sudo apt install nginx
```

`apt update` neaktualizuje nainštalované balíky. Aktualizuje lokálnu kópiu repository metadata.

Pri DNF:

```bash
sudo dnf makecache
sudo dnf install nginx
```

Typický tok:

```text
Konfigurácia repositories
  ↓
Stiahnutie podpísaných metadata
  ↓
Výber kandidátnej verzie
  ↓
Dependency resolution
  ↓
Stiahnutie packages
  ↓
Overenie checksum/podpisu
  ↓
Transakcia nad lokálnou package database
  ↓
Rozbalenie súborov a lifecycle scripts
```

## 4. Dependency resolution

Dependencies môžu obsahovať:

- presný názov balíka,
- minimálnu alebo maximálnu verziu,
- virtuálnu capability,
- conflict alebo obsoletes vzťah,
- architektúru.

Solver hľadá konzistentný výsledný stav. Konflikt vznikne napríklad vtedy, keď dva balíky požadujú navzájom nezlučiteľné verzie jednej knižnice.

Dôležité rozlíšenie:

```text
Package dependency
  = vzťah evidovaný package managerom

Runtime dependency
  = čokoľvek, čo program reálne potrebuje pri behu
```

Program môže mať runtime dependency, ktorú maintainer balíka zabudol deklarovať. Package manager potom nemá informáciu potrebnú na jej automatické riešenie.

## 5. Verzie, candidates a pinning

Nainštalovaná verzia nemusí byť rovnaká ako kandidátna verzia v repositories.

Debian/Ubuntu:

```bash
apt-cache policy nginx
apt list --upgradable
```

RHEL/Fedora:

```bash
dnf info nginx
dnf check-update
```

Výber verzie ovplyvňuje:

- priorita repository,
- distribution release,
- module stream,
- pinning alebo version lock,
- architektúra,
- explicitne zadaná verzia.

Príklady explicitnej verzie:

```bash
sudo apt install nginx=1.24.0-2ubuntu7
sudo dnf install nginx-1.24.0
```

Presný syntax závisí od distribúcie a dostupných repository versions.

## 6. Update, upgrade a distribution upgrade

Pri APT:

```bash
sudo apt update
sudo apt upgrade
sudo apt full-upgrade
```

- `update` obnoví metadata,
- `upgrade` aktualizuje balíky bez niektorých deštruktívnejších zmien dependency graphu,
- `full-upgrade` môže na vyriešenie graphu pridať alebo odstrániť balíky.

Tieto operácie nie sú automaticky ekvivalentom upgrade celej distribúcie na nový major release. Distribution upgrade má vlastný proces, compatibility pravidlá a recovery plán.

## 7. Package database ako zdroj pravdy

Package manager eviduje, ktorý balík vlastní konkrétny súbor.

Debian/Ubuntu:

```bash
dpkg -S /usr/bin/ssh
dpkg -L openssh-client
dpkg -s openssh-client
```

RHEL/Fedora:

```bash
rpm -qf /usr/bin/ssh
rpm -ql openssh-clients
rpm -qi openssh-clients
```

To umožňuje odpovedať:

- odkiaľ súbor pochádza,
- či je spravovaný balíkom,
- ktorá verzia ho nainštalovala,
- ktoré súbory do balíka patria.

Ručná úprava package-managed súboru môže byť pri upgrade prepísaná alebo vyriešená distribution-specific mechanizmom pre config files.

## 8. Lifecycle scripts a vedľajšie efekty

Balíky môžu počas inštalácie alebo odstránenia spúšťať scripts. Tie môžu:

- vytvoriť používateľa,
- reloadnúť systemd,
- migrovať databázu,
- upraviť cache,
- spustiť alebo reštartovať službu.

Preto package installation nie je vždy iba kopírovanie súborov. Má potenciálne prevádzkové vedľajšie efekty.

V automatizácii treba vedieť:

- či môže dôjsť k interaktívnej otázke,
- či sa služba automaticky reštartuje,
- či transakcia potrebuje network access,
- či je operácia bezpečne opakovateľná,
- čo sa stane pri prerušení procesu.

## 9. Podpisy a trust chain

Package manager overuje, že repository metadata alebo packages pochádzajú z dôveryhodného kľúča a neboli zmenené.

Trust chain typicky vyzerá:

```text
Dôveryhodný repository key
  ↓ overí
Repository metadata
  ↓ obsahujú checksum
Package artifact
  ↓ nainštaluje
Lokálna package database
```

Podpis neznamená, že balík je bez zraniteľností. Znamená, že jeho pôvod a integrita zodpovedajú trust policy.

Riziká:

- pridanie neznámeho third-party repository,
- použitie zastaraného alebo kompromitovaného signing key,
- miešanie repositories pre inú distribution release,
- vypnutie signature verification,
- sťahovanie náhodných packages mimo package managera.

## 10. Locks a súbežné operácie

Package database sa počas zmeny zamyká. Dve súbežné transakcie by mohli poškodiť konzistenciu.

Typický symptóm:

```text
Could not get lock ...
Another app is currently holding the ... lock
```

Správny postup:

1. zisti, ktorý proces drží lock,
2. over, či ide o aktívny package manager alebo automatický update,
3. počkaj alebo kontrolovane ukonči chybný proces,
4. až potom oprav prípadne nedokončenú transakciu.

Neodstraňuj lock file naslepo. Lock file môže byť iba reprezentáciou aktívneho kernel locku a jeho zmazanie neopraví rozpracovanú databázu.

## 11. Diagnostika Debian/Ubuntu

```bash
apt-cache policy
dpkg --audit
sudo dpkg --configure -a
sudo apt --fix-broken install
apt-mark showhold
```

Význam:

- `dpkg --audit` hľadá nekonzistentné alebo čiastočne nainštalované balíky,
- `dpkg --configure -a` dokončí configuration fázu rozbalených balíkov,
- `apt --fix-broken install` sa pokúsi opraviť dependency state,
- `apt-mark showhold` ukáže balíky blokované pred upgrade.

Logy bývajú napríklad v:

```text
/var/log/apt/
/var/log/dpkg.log
```

## 12. Diagnostika RHEL/Fedora

```bash
dnf check
dnf history
dnf history info <ID>
rpm -Va
```

- `dnf check` kontroluje dependency problémy,
- `dnf history` zobrazuje transakcie,
- `rpm -Va` porovnáva nainštalované files s RPM metadata.

Verification output treba interpretovať opatrne: config file môže byť legitímne zmenený administrátorom.

## 13. Produkčný prístup

V produkcii je dôležité:

- používať schválené repositories,
- pinovať alebo kontrolovať verzie tam, kde je potrebná reprodukovateľnosť,
- testovať updates pred rolloutom,
- evidovať reboot-required zmeny,
- mať rollback alebo replacement stratégiu,
- sledovať security advisories,
- minimalizovať počet nainštalovaných balíkov.

Pri immutable infrastructure sa server často neaktualizuje in-place. Vytvorí sa nový image s novými packages, otestuje sa a nahradí staré instances. Package manager je stále použitý pri image build-e, ale nie ako hlavný produkčný deployment mechanizmus.

## 14. Časté omyly

### „apt update aktualizuje systém“

Nie. Aktualizuje repository metadata.

### „Najnovšia verzia je vždy najbezpečnejšia voľba“

Nie nevyhnutne. Distribution môže backportovať security fixes bez zmeny upstream major version. Dôležitý je distribution package changelog a advisory.

### „Podpísaný balík je bezpečný“

Podpis overuje pôvod a integritu, nie absenciu chýb alebo škodlivého správania v dôveryhodnom zdroji.

### „Ručne zmazaný package file sa automaticky obnoví“

Nie, kým nevykonáš reinstall alebo inú explicitnú transakciu.

### „Odstránenie lock file opraví package manager“

Nie. Môže zhoršiť súbežnú alebo nedokončenú transakciu.

## 15. Kontrolné otázky

1. Aký je rozdiel medzi APT/DNF a DPKG/RPM?
2. Prečo `apt update` neinštaluje nové verzie?
3. Čo package manager potrebuje na vyriešenie dependency graphu?
4. Aký je rozdiel medzi podpisom balíka a jeho bezpečnosťou?
5. Prečo môže package installation reštartovať službu?
6. Ako zistíš, ktorý package vlastní konkrétny súbor?
7. Prečo sa package database zamyká?
8. Ako sa package management mení pri immutable infrastructure?
