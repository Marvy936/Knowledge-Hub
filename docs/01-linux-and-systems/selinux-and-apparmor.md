# SELinux and AppArmor

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Users, groups, permissions, sudo a PAM](users-groups-permissions-sudo-pam.md), [Linux Capabilities](linux-capabilities.md), [Filesystem hierarchy, inodes a links](filesystem-hierarchy-inodes-links.md)
- Súvisiace témy: mandatory access control, least privilege, containers, systemd hardening, audit logging

## 1. Definícia

SELinux a AppArmor sú Linux Security Modules, ktoré implementujú Mandatory Access Control — MAC.

MAC pridáva bezpečnostnú politiku nad tradičný model UID/GID, mode bits a ACL. Operácia musí prejsť všetkými relevantnými kontrolami; úspech v discretionary access control vrstve neznamená automatické povolenie v MAC vrstve.

## 2. Problém, ktorý riešia

Tradičné oprávnenia odpovedajú najmä na otázku:

```text
Môže tento používateľ alebo proces pristúpiť k tomuto objektu?
```

Ak je proces kompromitovaný, používa oprávnenia svojho účtu. MAC politika môže jeho správanie ďalej obmedziť podľa identity programu, labelu, profilu a typu operácie.

Príklad:

- web server beží ako `www-data`,
- vlastní alebo vie čítať niektoré súbory,
- DAC by prístup povolil,
- MAC politika stále môže zakázať čítanie SSH keys alebo zápis mimo povolených paths.

## 3. Vrstvený permission model

```text
system call
  ↓
namespace a mount context
  ↓
DAC: UID/GID, mode bits, ACL
  ↓
capability checks
  ↓
LSM: SELinux alebo AppArmor
  ↓
ďalšie kontroly: seccomp, read-only mount, application policy
```

Ak ktorákoľvek povinná vrstva operáciu zamietne, výsledok môže byť `EACCES` alebo `EPERM`.

Preto „permissions vyzerajú správne“ nie je úplná diagnostika.

## 4. SELinux mentálny model

SELinux je label-based MAC systém. Subjects a objects majú security context.

Typický context:

```text
system_u:system_r:httpd_t:s0
```

Časti:

- user,
- role,
- type,
- level/range pri MLS/MCS.

V bežnom serverovom policy modeli je najdôležitejší **type enforcement**.

```text
process type httpd_t
  + file type httpd_sys_content_t
  + operation read
  → policy decision
```

SELinux nehodnotí iba pathname. Politika pracuje primárne s labels a classes objektov.

## 5. SELinux režimy

```bash
getenforce
sestatus
```

Režimy:

- `Enforcing` — zamietnutia sa vynucujú a auditujú,
- `Permissive` — zamietnutia sa auditujú, ale globálne sa nevynútia,
- `Disabled` — SELinux nie je aktívny.

Permissive mode je diagnostický nástroj, nie cieľový produkčný stav.

Možno použiť aj per-domain permissive policy namiesto vypnutia ochrany pre celý host.

## 6. SELinux contexts a labels

Zobrazenie:

```bash
ls -Z /var/www/html
ps -eZ | grep httpd
id -Z
```

Dočasná zmena labelu:

```bash
sudo chcon -t httpd_sys_content_t /srv/site/index.html
```

`chcon` mení aktuálny xattr, ale relabel alebo `restorecon` môže zmenu prepísať.

Trvalejší policy mapping pathu:

```bash
sudo semanage fcontext -a -t httpd_sys_content_t '/srv/site(/.*)?'
sudo restorecon -Rv /srv/site
```

Mentálny model:

```text
semanage fcontext
  → upraví očakávané file-context pravidlo
restorecon
  → zosúladí aktuálny label s pravidlom
```

## 7. SELinux policy decisions

Politika typicky definuje pravidlá typu:

```text
allow source_type target_type:object_class permissions;
```

Príklad konceptu:

```text
allow httpd_t httpd_sys_content_t:file { open read getattr };
```

V skutočnej policy sú pravidlá kompilované a spravované modulmi. Bežný administrátor nemá riešiť každý problém vytvorením širokého custom `allow` pravidla.

Najprv treba zistiť, či:

- súbor má správny label,
- proces beží v očakávanom domain,
- existuje určený boolean,
- path nie je netypický bez fcontext mappingu,
- aplikácia nevykonáva neočakávanú operáciu.

## 8. SELinux booleans

Booleans umožňujú zapnúť podporovaný variant policy bez kompilácie vlastného modulu.

```bash
getsebool -a | grep httpd
sudo setsebool -P httpd_can_network_connect on
```

`-P` zapíše persistentnú zmenu.

Boolean treba zapnúť iba vtedy, keď jeho rozsah zodpovedá požadovanému správaniu. Názov môže byť širší, než sa na prvý pohľad zdá.

## 9. SELinux audit a diagnostika

Typické zdroje:

```bash
sudo ausearch -m AVC,USER_AVC -ts recent
sudo journalctl -t setroubleshoot
sudo journalctl --since '10 minutes ago' | grep -i avc
```

AVC znamená Access Vector Cache decision.

Dôležité fields:

- `scontext` — source process context,
- `tcontext` — target object context,
- `tclass` — object class,
- denied permissions,
- process command,
- path alebo inode metadata.

Príklad diagnostického toku:

1. reprodukuj problém,
2. nájdi časovo zodpovedajúci AVC denial,
3. over source a target contexts,
4. porovnaj s očakávanou distribučnou politikou,
5. oprav label, boolean alebo application design,
6. custom policy vytvor až po potvrdení legitímnej potreby.

## 10. `audit2allow` riziko

```bash
audit2allow -a
```

vie navrhnúť policy pravidlo z audit logov. Nevie však posúdiť, či zamietnutá operácia bola bezpečná a zámerná.

Nebezpečný postup:

```text
incident
→ zhromaždi všetky denials
→ automaticky vytvor allow policy
→ nasadiť
```

Tým možno zakódovať exploit attempt alebo chybnú konfiguráciu ako trvalé povolenie.

Správny postup začína root cause analýzou.

## 11. AppArmor mentálny model

AppArmor je profile-based MAC systém. Profil je typicky viazaný na executable path a definuje povolené paths, capabilities, network operácie a ďalšie správanie.

```text
/usr/sbin/example
  → AppArmor profile
  → povolené file paths, capabilities a network rules
```

AppArmor sa často opisuje ako path-based, ale implementácia a pravidlá majú viac detailov než jednoduchý string match. Rename, mounts, aliases a namespaces môžu ovplyvniť výsledok.

## 12. AppArmor režimy

Profily môžu byť:

- `enforce` — porušenia sa blokujú,
- `complain` — porušenia sa logujú bez blokovania,
- unloaded — profil sa neuplatňuje.

Stav:

```bash
sudo aa-status
```

Zmena režimu:

```bash
sudo aa-complain /usr/sbin/example
sudo aa-enforce /usr/sbin/example
```

Complain mode má slúžiť na učenie a diagnostiku. Nemá nahradiť dokončenú policy.

## 13. AppArmor profil

Zjednodušený príklad:

```text
#include <tunables/global>

/usr/local/bin/example {
  #include <abstractions/base>

  /usr/local/bin/example mr,
  /etc/example/** r,
  /var/lib/example/** rwk,
  /var/log/example/** rw,

  network inet stream,
  capability net_bind_service,

  deny /home/** rwklx,
}
```

Pravidlá rozlišujú typ operácie, napríklad:

- read,
- write,
- memory map,
- execute transition,
- lock,
- link.

Presná syntax a abstractions závisia od distribúcie a AppArmor verzie.

## 14. AppArmor tools a logs

Typické nástroje:

```bash
sudo apparmor_parser -r /etc/apparmor.d/usr.local.bin.example
sudo aa-logprof
sudo aa-genprof /usr/local/bin/example
sudo aa-status
```

Logy:

```bash
journalctl -k | grep -i apparmor
journalctl | grep 'apparmor="DENIED"'
```

Dôležité fields:

- profile,
- operation,
- requested mask,
- denied mask,
- name/path,
- process identity.

`aa-logprof` pomáha vytvárať pravidlá, ale administrátor musí rozhodnúť, či je požadovaný access legitímny.

## 15. SELinux vs. AppArmor

| Vlastnosť | SELinux | AppArmor |
|---|---|---|
| Primárny model | labels a type enforcement | profiles viazané typicky na executable/path rules |
| Identita objektu | security context | pravidlá podľa paths a ďalších atribútov |
| Policy ekosystém | rozsiahle distribučné policies, booleans, modules | profily, abstractions, parser tools |
| Diagnostika | AVC/audit logs, contexts | kernel audit logs, profile a operation |
| Bežné distribúcie | Fedora/RHEL rodina a ďalšie | Ubuntu/SUSE rodina a ďalšie |

Nie je korektné tvrdiť, že jeden systém je všeobecne „lepší“. Rozhoduje distribučná integrácia, policy maturity, operational model a tímová znalosť.

## 16. Containers

Container proces môže byť súčasne obmedzený:

- host DAC,
- user namespace,
- capabilities,
- seccomp,
- SELinux type/MCS labels alebo AppArmor profilom,
- read-only mounts.

SELinux pri kontajneroch často používa oddelené MCS categories, aby dva containers s rovnakým všeobecným type nemohli čítať navzájom označené dáta.

Bind mount na SELinux hoste môže potrebovať správny relabeling model. Runtime options typu `:z` alebo `:Z` majú rozdielny sharing význam a nesmú sa používať naslepo.

Kubernetes môže vyberať SELinux options alebo AppArmor profiles cez security context a platform policy. Presné API závisí od Kubernetes verzie.

## 17. MAC a systemd

Systemd môže spustiť službu s dodatočnými security nastaveniami, ale nenahrádza LSM policy.

Relevantné properties môžu zahŕňať:

```ini
[Service]
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
AppArmorProfile=example-profile
SELinuxContext=system_u:system_r:example_t:s0
```

Podpora konkrétnych directives závisí od build a verzie systemd. Pri bežnej službe sa často používa distribučná policy a labels namiesto manuálneho nastavovania contextu v unit.

## 18. Troubleshooting scenár: správne UNIX permissions, stále denied

Aplikácia nevie čítať `/srv/app/config.yaml`.

### Krok 1: DAC

```bash
namei -l /srv/app/config.yaml
getfacl /srv/app/config.yaml
sudo -u app cat /srv/app/config.yaml
```

### Krok 2: process a MAC stav

SELinux:

```bash
ps -eZ | grep app
ls -Z /srv/app/config.yaml
ausearch -m AVC -ts recent
```

AppArmor:

```bash
aa-status
journalctl -k | grep -i apparmor
```

### Krok 3: oprava

- nesprávny SELinux label → `semanage fcontext` + `restorecon`,
- podporovaný variant → vhodný boolean,
- AppArmor profil chýba path rule → úzka oprava profilu,
- aplikácia číta neočakávaný path → oprava konfigurácie alebo designu.

Nevypínaj globálne MAC iba preto, že operácia po vypnutí funguje. To iba potvrdzuje vrstvu, nie správnu nápravu.

## 19. Troubleshooting scenár: služba funguje ručne, nie cez systemd

Možné rozdiely:

- iný SELinux domain pri systemd transition,
- AppArmor profil viazaný na executable,
- iný path alebo symlink resolution,
- systemd sandboxing navyše,
- rozdielne environment a working directory.

Porovnaj:

```bash
ps -eZ
systemctl cat example.service
systemctl show example.service
journalctl -u example.service
journalctl -k
```

## 20. Bezpečná práca s policy

1. Reprodukuj presný use case.
2. Identifikuj subject, object a operation.
3. Over, či je súčasný access legitímny.
4. Preferuj distribučný label, boolean alebo abstraction.
5. Zúž pravidlo na minimálny scope.
6. Otestuj normálny aj zakázaný scenár.
7. Udržuj policy vo version control.
8. Monitoruj nové denials po nasadení.

## 21. Časté omyly

### „chmod 777 vyrieši permission denied“

Nie pri MAC zamietnutí. Navyše zbytočne oslabí DAC.

### „SELinux/AppArmor stačí vypnúť“

Tým sa odstráni bezpečnostná hranica a zakryje root cause.

### „Permissive alebo complain je bezpečný produkčný režim“

Je primárne diagnostický. Operácie sa neblokujú.

### „audit2allow alebo aa-logprof vie rozhodnúť, čo je bezpečné“

Nástroj vidí požadované operácie, nie business a threat kontext.

### „SELinux rozhoduje podľa pathname“

Primárne rozhoduje podľa security labels a policy.

### „AppArmor je iba jednoduchý file allowlist“

Profily zahŕňajú execute transitions, capabilities, network a ďalšie pravidlá.

## 22. Kontrolné otázky

1. Aký je rozdiel medzi DAC a MAC?
2. Čo znamená SELinux type enforcement?
3. Aký je rozdiel medzi `chcon` a `semanage fcontext` + `restorecon`?
4. Načo slúžia SELinux booleans?
5. Prečo je automatické použitie `audit2allow` rizikové?
6. Aký je rozdiel medzi AppArmor enforce a complain mode?
7. Ako sa líši mentálny model SELinux a AppArmor?
8. Prečo `chmod 777` nemusí vyriešiť denied operáciu?
9. Ako by si diagnostikoval službu, ktorá funguje ručne, ale nie pod systemd?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Linux Capabilities](linux-capabilities.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Linux Performance and Troubleshooting →](performance-and-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
