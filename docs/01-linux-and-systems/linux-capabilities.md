# Linux capabilities

Linux capabilities rozdeľujú tradičné root privileges na jemnejšie operation classes, napríklad bind na privileged port, zmenu network configuration alebo obídenie vybraných DAC checks. Capability nie je role priradená userovi navždy; kernel vyhodnocuje capability sets konkrétneho threadu pri konkrétnej operácii.

Process pracuje s permitted, effective, inheritable, bounding a ambient sets. Pri `execve()` sa nové sets vypočítajú z parent state-u, file capabilities, bounding setu, `no_new_privs` a user-namespace contextu. Container configuration typu `cap_add` preto ešte nepreukazuje, že capability je effective v bežiacom procese ani že pôsobí voči host resource.

Least privilege znamená identifikovať konkrétny kernel check a ponechať iba potrebnú capability v správnom scope-e. Pridanie `CAP_SYS_ADMIN` alebo `privileged` často skryje skutočný denial a výrazne rozšíri attack surface. Overenie musí zahŕňať allowed operation, forbidden adjacent operation, effective sets po exec a MAC/seccomp boundary.

## 1. Definícia

Linux capabilities rozdeľujú tradičné root oprávnenia na menšie samostatné právomoci. Proces tak môže dostať napríklad právo bindnúť port pod `1024` bez toho, aby získal všetky právomoci UID `0`.

Capability model nie je jednoduchý zoznam zapnutých oprávnení. Kernel pri každej privilegovanej operácii vyhodnocuje capability v konkrétnom user namespace a proces drží viac capability sets, ktoré ovplyvňujú aktuálne práva aj budúce `execve()` prechody.

```text
process credentials
  + effective capability set
  + user namespace scope
  + bounding/no_new_privs boundaries
  + DAC/ACL/LSM/seccomp/mount policy
  → výsledok operácie
```

Capabilities zmenšujú privilege scope, ale samy osebe negarantujú least privilege. Široká capability, nebezpečný executable alebo kombinácia viacerých právomocí môže byť prakticky ekvivalentná plnému root prístupu.

## 2. Prečo capability model existuje

Mnohé programy potrebujú iba úzky privilegovaný krok. Web server potrebuje otvoriť port `80`, časový daemon upraviť clock a debugger inspectovať vybraný proces.

Spustenie celej aplikácie ako root zväčšuje blast radius:

- parser vulnerability môže viesť k zápisu do ľubovoľných súborov,
- plugin alebo child process zdedí zbytočné oprávnenia,
- kompromitovaná služba môže meniť sieť, identities alebo kernel settings,
- incident response nevie ľahko rozlíšiť legitímnu potrebu od privilege abuse.

Capability model umožňuje oddeliť konkrétnu kernelovú právomoc od celej root identity. Dobrý návrh však stále kombinuje neprivilegovaný UID, úzky capability set, read-only filesystem policy, seccomp a LSM pravidlá.

## 3. Capability check nie je jediná bezpečnostná vrstva

Capability môže obísť alebo povoliť určitú kernelovú kontrolu, ale výsledná operácia môže stále zlyhať na inej vrstve.

```text
pathname lookup
  ↓
DAC / ACL
  ↓
capability-specific bypass alebo privilege check
  ↓
mount flags
  ↓
SELinux/AppArmor
  ↓
seccomp alebo subsystem-specific policy
  ↓
operation
```

Napríklad proces s `CAP_NET_BIND_SERVICE` môže bindnúť privilegovaný port, ale SELinux policy mu môže konkrétny port type zakázať. Proces s `CAP_DAC_OVERRIDE` môže obísť časť mode-bit kontrol, ale read-only mount mu stále nedovolí zápis.

Preto `EPERM` alebo `EACCES` neznamená automaticky „chýba capability“. Treba identifikovať presný syscall a decision layer.

## 4. Dôležité capabilities

| Capability | Typická právomoc | Hlavné riziko |
|---|---|---|
| `CAP_NET_BIND_SERVICE` | bind na porty pod `1024` | zvyčajne úzky scope, ale stále umožňuje obsadiť citlivý endpoint |
| `CAP_NET_ADMIN` | interfaces, routes, firewall a network policy | môže presmerovať alebo odpočúvať traffic v príslušnom network namespace |
| `CAP_NET_RAW` | raw a packet sockets | umožňuje packet crafting a širšie network observation |
| `CAP_CHOWN` | meniť owner súborov | môže narušiť filesystem ownership boundary |
| `CAP_DAC_OVERRIDE` | obísť väčšinu DAC read/write/execute checks | približuje sa k širokému filesystem prístupu |
| `CAP_DAC_READ_SEARCH` | obísť read a directory search checks | umožňuje čítať veľkú časť filesystemu |
| `CAP_SETUID` | meniť UID a manipulovať s UID credentials | môže prejsť na inú lokálnu identitu |
| `CAP_SETGID` | meniť GID a groups | môže získať group-based prístup |
| `CAP_SYS_PTRACE` | širší ptrace/process inspection | môže čítať secrets a meniť procesy v scope policy |
| `CAP_SYS_CHROOT` | volať `chroot()` | chroot sám nie je sandbox a môže byť súčasťou escape chainu |
| `CAP_MKNOD` | vytvárať device nodes | nebezpečné pri dostupných host devices |
| `CAP_SYS_TIME` | meniť systémový čas | naruší TLS, log koreláciu a distributed systems |
| `CAP_SYS_MODULE` | načítať kernel modules | prakticky priama cesta k ovládnutiu kernelu |
| `CAP_SYS_RAWIO` | raw I/O a citlivé hardware operácie | môže obísť vysoké systémové hranice |
| `CAP_SYS_ADMIN` | široká množina administratívnych operácií | často sa správa ako „takmer root“ a výrazne oslabuje kontajnerovú izoláciu |

Názov capability neodhaľuje celý scope. Autoritatívny význam je v kernel capability documentation a konkrétnych syscall/subsystem checks.

## 5. Capability sets procesu

Proces nemá jednu capability množinu. Kernel udržiava viac sets s odlišnou úlohou pri aktuálnom vykonávaní a `execve()` prechode.

```text
Permitted   → čo môže process potenciálne aktivovať
Effective   → čo kernel aktuálne používa pri checks
Inheritable → kandidáti na dedenie cez file inheritable mechanizmus
Bounding    → absolútna horná hranica získateľných capabilities
Ambient     → capabilities zachované cez neprivilegovaný exec
```

Aktuálne masky:

```bash
grep '^Cap' /proc/<pid>/status
capsh --print
```

Dekódovanie hex masky:

```bash
capsh --decode=0000000000000400
```

Sets treba interpretovať spolu. Capability v permitted, ale nie effective sete, nemusí byť aktuálne použitá; capability mimo bounding setu nemožno bežne získať späť v descendant process tree.

## 6. Permitted set

Permitted set je horná hranica capabilities, ktoré môže proces presunúť do effective setu alebo zachovať podľa capability rules. Capability mimo permitted setu proces nemôže jednoducho aktivovať interným prepínačom.

Permitted nie je dôkaz, že kernel ju práve používa pri checks. Aplikácia môže mať capability pripravenú, ale dočasne ju odstrániť z effective setu a aktivovať iba okolo úzkej privilegovanej operácie.

Takýto privilege bracketing znižuje časové okno, ale zvyšuje implementačnú komplexitu. Chyba v prepínaní alebo multi-threaded procese môže vytvoriť nejasný security state.

## 7. Effective set

Effective set obsahuje capabilities, ktoré kernel aktuálne zohľadňuje pri privilegovaných checks. Keď proces potrebuje `CAP_NET_BIND_SERVICE`, capability musí byť effective v čase `bind()` kontroly.

Effective set môže byť užší než permitted set. To umožňuje programu držať capability ako potenciálne dostupnú, ale nemať ju stále aktívnu.

Pri incidentnej diagnostike je `CapEff` najdôležitejší prvý pohľad, ale nestačí. Treba skontrolovať bounding, ambient, user namespace a LSM context.

## 8. Inheritable set

Inheritable set sa podieľa na `execve()` transformácii spolu s file inheritable mask. Je to explicitný kanál, ktorým proces označuje capabilities, ktoré môže preniesť cez vhodne označený executable.

Nie je to všeobecné „všetky child procesy zdedia capability“. Bežný neprivilegovaný executable bez file capability metadata nemusí z inheritable setu automaticky dostať effective privilege.

Inheritable mechanizmus sa používa menej intuitívne než ambient capabilities a ľahko sa nesprávne interpretuje. Pri service hardeningu je vhodnejšie explicitne kontrolovať bounding a ambient set cez systemd, než sa spoliehať na skrytú inheritable chain.

## 9. Bounding set

Bounding set je horná hranica capabilities, ktoré môže proces a jeho descendants získať cez neskorší `execve()` a file capability mechanizmy. Capability odstránená z bounding setu sa v danom process tree typicky nedá získať späť bez novej nadradenej privilege boundary.

Systemd príklad allowlistu:

```ini
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
```

Explicitné odobratie:

```ini
CapabilityBoundingSet=~CAP_SYS_ADMIN CAP_SYS_MODULE CAP_SYS_RAWIO
```

Úzky bounding set je dôležitejší než iba momentálne prázdny effective set. Aj keď aplikácia teraz capability nepoužíva, široký bounding set môže umožniť neskoršiemu helper executable získať privilege.

## 10. Ambient set

Ambient capabilities umožňujú zachovať vybrané capabilities pri `execve()` bežného neprivilegovaného executable bez file capability metadata. Boli zavedené najmä pre service launch modely, kde neprivilegovaný proces potrebuje úzku capability aj po exec transition.

Capability môže byť ambient iba ak je zároveň permitted a inheritable. Ak sa z týchto sets odstráni, kernel ju odstráni aj z ambient setu.

Ambient set sa vymaže pri spustení privileged executable, napríklad programu so setuid alebo file capabilities. Tým sa zabráni nekontrolovanej kombinácii dvoch privilege transition modelov.

Rizikom je transitívne dedenie. Ak aplikácia s ambient capability spustí shell, plugin alebo helper, tento program môže capability zdediť, hoci pôvodný návrh s tým nepočítal.

## 11. File capabilities

Executable môže niesť capability metadata v extended attribute `security.capability`.

```bash
getcap /path/to/program
sudo setcap cap_net_bind_service=ep /path/to/program
sudo setcap -r /path/to/program
```

Zápis:

```text
cap_net_bind_service=ep
```

znamená, že capability je vo file permitted maske a effective flag žiada, aby novo vypočítané permitted capabilities boli po `execve()` aj effective.

File capability patrí konkrétnemu executable artifactu. Ak deployment súbor nahradí novým inode, metadata sa nemusia zachovať a capability môže zmiznúť alebo zostať na starej verzii.

## 12. Filesystem a deployment dôsledky file capabilities

File capabilities používajú extended attributes. Ich zachovanie závisí od filesystemu, mount policy, archivačného formátu a deployment nástroja.

Rizikové situácie:

- **Copy bez xattrs** — nový executable funguje bez capability a zlyhá až pri runtime privilegovanej operácii.
- **Package upgrade** — package manager nahradí inode a nastaví capability podľa package metadata, nie podľa ručnej zmeny.
- **Container image build** — build storage driver alebo rootless mapping nemusí zachovať xattr tak, ako sa očakáva.
- **Backup/restore** — archive bez xattr supportu obnoví obsah, ale nie security metadata.
- **Network filesystem** — backing filesystem nemusí capability xattrs podporovať alebo ich môže filtrovať.

Capability treba po deploymente validovať ako súčasť artifact verification, nie iba raz pri prvotnej konfigurácii.

## 13. `execve()` capability transformácia

Pri `execve()` kernel nevytvorí capability state jednoduchým skopírovaním parenta. Nové sets vypočíta z process state, file metadata a bezpečnostných boundaries.

Zjednodušený model:

```text
parent permitted/inheritable/ambient
+ file permitted/inheritable/effective flag
∩ bounding set
∩ user namespace authority
+ securebits a UID transition rules
+ no_new_privs restriction
→ child permitted/effective/ambient
```

Presné rovnice sú implementačne detailné, ale praktický dôsledok je zásadný: capability môže po exec zmiznúť, aktivovať sa alebo byť zablokovaná podľa executable metadata a process boundaries.

Pri troubleshooting-u treba pozorovať capability sets **po spustení cieľového procesu**, nie iba v launcher shelli.

## 14. UID 0 a capability fixup

V initial user namespace má UID `0` tradične špeciálne capability správanie. Prechody na alebo z UID `0` môžu capability sets upraviť podľa securebits a kernel rules.

Daemon často štartuje ako root, vykoná privilegovanú inicializáciu a potom zmení UID. Ak pred zmenou explicitne nenastaví keep-caps mechanizmus alebo správne sets, capabilities môže stratiť.

Naopak, zlé securebits alebo privilege-drop poradie môže ponechať viac práv, než aplikácia očakáva. Bezpečnejšie je neštartovať ako root vôbec, ak service manager vie dodať presnú ambient capability priamo neprivilegovanému účtu.

## 15. Securebits

Securebits sú process flags, ktoré menia capability správanie okolo UID `0`, capability retention a exec transitions. Patria sem mechanizmy ako keep-caps alebo zákaz automatického root fixupu.

```bash
capsh --print
```

Niektoré securebits možno zamknúť pre descendants. Locknutie je bezpečnostná hranica, pretože child ich nemôže znovu uvoľniť.

Securebits sú pokročilý mechanizmus. V bežnej prevádzke ich má nastavovať service manager alebo dobre auditovaný privilege-dropping launcher, nie ad hoc shell wrapper.

## 16. `no_new_privs`

Flag `no_new_privs` garantuje, že `execve()` nezvýši privilege procesu cez setuid, setgid alebo file capabilities. Proces a descendants si môžu privilege znížiť, ale nový executable im ho nemá navýšiť.

Systemd:

```ini
NoNewPrivileges=yes
```

Kontrola:

```bash
grep '^NoNewPrivs' /proc/<pid>/status
```

`no_new_privs` je silný hardening control a je základom bezpečného používania niektorých seccomp modelov. Môže však rozbiť program, ktorý legitímne očakáva setuid helper alebo file-capability transition.

Dôležitá nuansa: capability už prítomná v ambient/effective sete nemusí byť „nová privilege“. Preto treba `NoNewPrivileges` kombinovať s úzkym bounding a ambient setom.

## 17. Capability scope a user namespaces

Capability je vždy vyhodnocovaná vo vzťahu ku konkrétnemu user namespace. Proces môže mať `CAP_NET_ADMIN` v child user namespace, ale nie v initial host user namespace.

```text
CAP_NET_ADMIN v container user namespace
  → správa network namespace vlastneného týmto user namespace

CAP_NET_ADMIN v initial host user namespace
  → hostová network authority
```

Tento scope umožňuje rootless kontajnery. Namespace root môže konfigurovať vlastný network alebo mount kontext bez získania rovnakej authority nad hostom.

Pri diagnostike samotný názov capability nestačí. Treba porovnať `/proc/<pid>/ns/user`, UID mapping a namespace, nad ktorým sa vykonáva operácia.

## 18. Root v kontajneri

Kontajnerový UID `0` môže byť:

- host UID `0` v rovnakom user namespace,
- mapovaný na neprivilegovaný host UID v child user namespace,
- obmedzený runtime capability allowlistom,
- ďalej obmedzený seccomp, LSM a read-only mountmi.

Tieto modely majú výrazne odlišný blast radius. „Kontajner beží ako root“ preto nie je dostatočný opis privilege.

Host-root kontajner s `CAP_SYS_ADMIN`, host mountom a device access môže prakticky obísť väčšinu izolácie. Rootless kontajner s prázdnym capability setom a user-ID mappingom má podstatne užšiu authority.

## 19. Systemd capability policy

Systemd vie spustiť neprivilegovanú službu s presne definovanou capability policy:

```ini
[Service]
User=web
Group=web
ExecStart=/usr/local/bin/web
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE
NoNewPrivileges=yes
PrivateDevices=yes
ProtectSystem=strict
ProtectHome=yes
```

Význam:

- **`User=`** — proces nepoužíva UID `0` ako základnú identitu.
- **`CapabilityBoundingSet=`** — žiadna iná capability sa nemôže neskôr objaviť cez exec chain.
- **`AmbientCapabilities=`** — executable dostane potrebnú capability bez file xattr.
- **`NoNewPrivileges=`** — helper program nemôže získať dodatočné setuid/file-cap privilege.
- **Filesystem/device hardening** — znižuje dopad aj v prípade zneužitia povolenej capability.

Efektívna konfigurácia:

```bash
systemctl show web.service \
  -p User \
  -p CapabilityBoundingSet \
  -p AmbientCapabilities \
  -p NoNewPrivileges
```

## 20. Service startup: root then drop verzus direct least privilege

Tradičný daemon štartuje ako root, otvorí port alebo device a potom zmení UID. Tento model funguje, ale privilege transition logika zostáva v aplikácii.

Moderný service-manager model môže:

1. vytvoriť socket alebo dodať capability,
2. spustiť aplikáciu priamo pod neprivilegovaným UID,
3. odstrániť všetky ostatné capabilities,
4. aplikovať sandbox pred prvou aplikačnou inštrukciou.

Direct least privilege znižuje množstvo privilege-dropping kódu v aplikácii. Nie je však vždy možný pri daemonoch, ktoré potrebujú dynamicky vykonávať viac privilegovaných operácií počas lifecycle.

## 21. Socket activation ako alternatíva capability

Aplikácia nemusí mať `CAP_NET_BIND_SERVICE`, ak listening socket otvorí systemd `.socket` unit a file descriptor odovzdá službe. Privilegovaný bind sa tak presunie do service managera.

```text
systemd socket unit
  ↓ bind port 80
listening FD
  ↓ odovzdanie
unprivileged application
```

Tento model úplne odstraňuje network-bind capability z aplikácie. Vyžaduje však podporu socket activation alebo vhodný wrapper.

Least privilege často znamená odstrániť potrebu capability architektonickou zmenou, nie iba zmenšiť capability set.

## 22. File capabilities verzus setuid

Setuid executable mení effective UID na ownera súboru, často root. Program potom dostáva širokú identity authority a musí sám bezpečne obmedziť operácie.

File capability executable dostane iba konkrétne capability masks. To zvyčajne znižuje scope, ale nie automaticky blast radius.

Ak program s `CAP_DAC_OVERRIDE` prijíma ľubovoľný pathname alebo podporuje plugin loading, útočník môže capability zneužiť na široký filesystem prístup. Security závisí od programu, argumentov, environmentu a child exec chainu, nie iba od počtu capabilities.

## 23. Containers: default drop model

Container runtime typicky vytvorí default capability allowlist a niektoré nebezpečné capabilities odstráni. Default však nie je univerzálne bezpečný pre každý workload.

Bezpečný model:

```text
drop ALL
  ↓
pridaj iba capability dokázanú syscall/use-case analýzou
  ↓
kombinuj s runAsNonRoot, no_new_privs, seccomp a LSM
```

Docker-like príklad:

```bash
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE image
```

Kubernetes:

```yaml
securityContext:
  runAsNonRoot: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
    add:
      - NET_BIND_SERVICE
```

`allowPrivilegeEscalation: false` sa typicky mapuje na `no_new_privs`, ale exact runtime správanie treba overiť podľa platformy.

## 24. `privileged` kontajner

`privileged: true` alebo ekvivalent typicky pridá veľmi široké capability sets, uvoľní device policy a zmení ďalšie runtime protections. Nie je to skratka pre „pridaj jednu chýbajúcu capability“.

Privileged kontajner často získava authority nad hostovými devices a kernel interfaces. V kombinácii s host namespaces alebo filesystem mounts môže byť prakticky host-root process s kontajnerovým packagingom.

Pri probléme sa nemá použiť privileged mode ako diagnostický konečný stav. Dočasný test môže potvrdiť security-layer involvement, ale následne treba nájsť presnú capability, mount, device alebo LSM requirement.

## 25. Capability leakage cez child proces

Capability pridelená aplikácii môže prejsť do helpera alebo shellu. Riziko závisí od effective, permitted, ambient a file capability transition rules.

Príklady leakage:

- aplikácia s ambient capability spustí shell hook,
- plugin framework načíta nedôveryhodný kód v tom istom procese,
- executable hľadá helper cez manipulovateľný `PATH`,
- writable wrapper script je spustený service managerom s capability,
- interpreter dostane capability a následne vykoná ľubovoľný script.

Least privilege sa preto musí hodnotiť pre celý transitive execution graph, nie iba pre názov main binary.

## 26. Interpreters a scripts

File capabilities na scripts sú problematické a kernel ich nemusí aplikovať spôsobom, ktorý používateľ očakáva. Pri shebang exec chain sa privilegovaný objekt a interpreter interaction líšia od bežného native executable.

Bezpečnejší model je:

- capability na malom auditovanom native helperi,
- helper vykoná jednu presne validovanú privilegovanú operáciu,
- hlavná aplikácia komunikuje cez úzky interface,
- helper nespúšťa shell ani pluginy.

Prideliť širokú capability všeobecnému interpreteru, napríklad Pythonu alebo Bashi, je prakticky pridelenie tejto capability ľubovoľnému kódu spustenému interpreterom.

## 27. Capability revocation

Capability možno odstrániť z effective alebo permitted setu počas runtime, z bounding setu pre future exec chain alebo z file xattr. Tieto operácie majú odlišný scope.

- **Drop effective** — capability sa aktuálne nepoužíva, ale môže zostať permitted.
- **Drop permitted** — proces ju už nevie znovu aktivovať bez nového privilege transition.
- **Drop bounding** — descendants ju nemôžu získať cez file capability.
- **Remove file xattr** — budúce execs tohto artifactu ju nedostanú, ale už bežiaci proces sa nemení.

Revocation konfigurácie nie je revocation bežiaceho procesu. Po zmene systemd unit alebo container manifestu treba workload nahradiť alebo reštartovať a overiť nové `/proc/<pid>/status` sets.

## 28. Audit capability state

Hostový audit:

```bash
getcap -r /usr/bin /usr/sbin /usr/local/bin 2>/dev/null
find / -xdev -perm /6000 -type f 2>/dev/null
```

Procesný audit:

```bash
grep -E '^(Uid|Gid|Cap|NoNewPrivs)' /proc/<pid>/status
capsh --decode=<CapEff-hex>
readlink /proc/<pid>/ns/user
cat /proc/<pid>/uid_map
```

Service audit:

```bash
systemctl cat example.service
systemctl show example.service \
  -p CapabilityBoundingSet \
  -p AmbientCapabilities \
  -p NoNewPrivileges
```

Audit má kontrolovať desired config aj runtime state. Zmena unit bez restartu alebo zastaraný kontajner môže stále bežať so starou capability policy.

## 29. Troubleshooting: bind na port 80 zlyhá

Aplikácia dostane `EACCES` alebo `EPERM` pri `bind()` na port `80`.

1. **Potvrď syscall a errno** — `strace -e trace=bind` odlíši bind failure od skoršej DNS alebo socket chyby.
2. **Skontroluj effective capability** — proces musí mať `CAP_NET_BIND_SERVICE` v správnom user namespace.
3. **Skontroluj bounding a permitted set** — capability mohla byť odrezaná ešte pred exec.
4. **Over systemd/container desired state** — ambient capability v config nemusí byť aplikovaná na už bežiaci proces.
5. **Over user namespace scope** — capability v child namespace nemusí platiť nad host network namespace.
6. **Skontroluj SELinux/AppArmor** — port type alebo profile môže bind blokovať.
7. **Skontroluj, či port už niekto drží** — `EADDRINUSE` je odlišný failure mode.
8. **Zváž socket activation** — capability možno úplne odstrániť z aplikácie.

## 30. Troubleshooting: capability zmizla po deploymente

1. **Porovnaj inode a artifact version** — deployment mohol executable nahradiť.
2. **Spusti `getcap` na aktuálnom path** — xattr môže chýbať.
3. **Over filesystem a mount support** — extended attributes môžu byť filtrované.
4. **Skontroluj package metadata alebo image build** — ručné `setcap` nemusí byť reprodukovateľné.
5. **Skontroluj `no_new_privs` a bounding set launcheru** — file capability môže byť zámerne zablokovaná.
6. **Pozri runtime `CapPrm` a `CapEff`** — file metadata sama nedokazuje výsledok exec transition.

Oprava má patriť do source of truth build/deployment procesu. Ručné `setcap` na jednom hoste vytvára drift.

## 31. Troubleshooting: kontajner funguje iba s `privileged`

`privileged` mení viac bezpečnostných vrstiev naraz, takže úspech nepotvrdzuje, že chýba konkrétna capability.

Postup:

1. **Porovnaj syscalls a errno** — identifikuj presnú zakázanú operáciu.
2. **Skontroluj runtime capabilities** — `CapEff`, `CapBnd` a container security context.
3. **Skontroluj seccomp denial** — syscall mohol byť filtrovaný nezávisle od capability.
4. **Skontroluj LSM logs** — SELinux/AppArmor môže blokovať path alebo operation.
5. **Skontroluj devices a mounts** — privileged mode mení aj device access a mount policy.
6. **Pridávaj jednu kontrolu naraz** — minimálna capability alebo explicitný device/mount rule.
7. **Po nájdení requirementu znovu dropni ALL** — over, že workload funguje s úzkym allowlistom.

## 32. Časté omyly

### „Capability je bezpečná, lebo nie je root“

Nie automaticky. `CAP_SYS_ADMIN`, `CAP_SYS_MODULE` alebo kombinácia filesystem a namespace capabilities môže poskytnúť veľmi širokú authority.

### „Proces má capability, keď je v permitted sete“

Kernel pri bežnom checku používa effective set. Permitted určuje potenciál, nie nevyhnutne aktuálnu aktiváciu.

### „Child vždy zdedí capabilities parenta“

`execve()` sets prepočíta podľa file metadata, bounding, ambient, UID a securebits rules. Capability môže zmiznúť alebo byť zablokovaná.

### „File capability zostane po každom deploymente“

Executable replacement vytvorí nový inode a xattr sa zachová iba ak to deployment proces explicitne zabezpečí.

### „Root v kontajneri má všetky host capabilities“

Capability scope závisí od user namespace, runtime allowlistu a ďalších security layers.

### „`NoNewPrivileges=yes` odstráni všetky existujúce capabilities“

Nie. Bráni zvýšeniu privilege cez budúci exec, ale už pridelené ambient/effective capabilities treba obmedziť samostatne.

### „`privileged` iba pridá capabilities“

Privileged mode typicky mení capabilities, devices, LSM a ďalšie runtime hranice. Jeho blast radius je podstatne širší.

## 33. Kontrolné otázky

1. Prečo capabilities nie sú jednoduchý binárny prepínač root/non-root?
2. Aký je rozdiel medzi permitted a effective setom?
3. Načo slúži bounding set?
4. Za akých podmienok môže capability zostať v ambient sete?
5. Prečo sa capability state po `execve()` nemusí rovnať parent state?
6. Ako file capability súvisí s executable inode a extended attributes?
7. Čo presne garantuje `no_new_privs`?
8. Prečo capability treba interpretovať vo vzťahu k user namespace?
9. Ako socket activation môže odstrániť potrebu `CAP_NET_BIND_SERVICE`?
10. Prečo je capability na všeobecnom interpreteru nebezpečná?
11. Aký je rozdiel medzi odobratím effective, permitted a bounding capability?
12. Prečo úspech s privileged kontajnerom neurčuje root cause?

## 34. Zhrnutie

Linux capabilities rozdeľujú root privilege na samostatné kernelové právomoci, ale výsledná authority závisí od viacerých process sets, `execve()` transformácie, bounding a `no_new_privs` boundaries, user namespace scope a ďalších access-control vrstiev.

Least privilege znamená nielen pridať čo najmenej capabilities, ale minimalizovať celý transitívny execution graph, odstrániť zbytočnú potrebu privilege architektúrou a overiť runtime state po každom deploymente. Capabilities sú účinný nástroj, ak sú kombinované s neprivilegovaným UID, úzkym bounding setom, seccomp, LSM a bezpečnými filesystem/device pravidlami.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: cgroups](cgroups.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: SELinux a AppArmor →](selinux-and-apparmor.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
