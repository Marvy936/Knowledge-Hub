# Users, groups, permissions, sudo a PAM

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Filesystem hierarchy, inodes a links](filesystem-hierarchy-inodes-links.md)
- Súvisiace témy: process credentials, SSH, capabilities, SELinux, containers, service identity

## 1. Linux identity je číselný kernelový stav

Linux kernel pri väčšine access checks nepracuje s menami ako `alice` alebo `platform`. Pracuje s číselnými UID, GID, supplementary groups, capabilities a ďalšími credentials uloženými pri procese. Mená sú user-space reprezentácia, ktorú nástroje prekladajú cez NSS.

```text
username/group name
→ NSS lookup
→ UID/GID
→ process credentials
→ kernel authorization checks
```

Súbor na filesystéme vlastní UID a GID, nie textové meno. Ak účet odstrániš a neskôr vytvoríš nový účet s rovnakým UID, nový účet môže zdediť praktický prístup k starým súborom. UID reuse je preto lifecycle a security rozhodnutie, nie iba administratívna formalita.

## 2. Identity source a NSS

Lokálne účty typicky používajú `/etc/passwd`, `/etc/group`, `/etc/shadow` a `/etc/gshadow`. Tieto súbory však nemusia byť jediným zdrojom identity. Name Service Switch v `/etc/nsswitch.conf` určuje, či lookup pokračuje do lokálnych files, SSSD, LDAP, systemd modulov alebo iného provideru.

- **`/etc/passwd` — verejné account metadata.** Obsahuje meno, UID, primary GID, home directory a login shell. Password hash sa na moderných systémoch neukladá priamo sem.
- **`/etc/shadow` — chránené password a aging metadata.** Čitateľnosť je obmedzená, pretože hash je credential material použiteľný na offline cracking.
- **`/etc/group` — group names, GID a časť supplementary membership.** Reálny group list session môže vzniknúť aj z external identity provideru.
- **`/etc/nsswitch.conf` — poradie a zdroje lookupov.** Chybný alebo pomalý remote provider môže spomaliť `id`, login, `sudo` aj procesy, ktoré prevádzajú UID na meno.

```bash
getent passwd alice
getent group platform
id alice
```

`getent` používa nakonfigurovaný NSS path. Priame `grep /etc/passwd` odpovedá iba na otázku, či je účet v lokálnom súbore, nie či ho systém ako celok dokáže resolve-nuť.

## 3. Account identity a process credentials nie sú to isté

Účet je administratívny záznam. Bežiaci proces má snapshot credentials, ktoré získal pri vytvorení session, `fork/exec`, set-ID prechode alebo explicitnom privilege transition.

```text
account databáza
→ login/PAM alebo service manager
→ inicializácia groups a UID/GID
→ process credentials
→ child procesy dedia credentials
```

Ak administrátor pridá používateľa do skupiny, už existujúci shell nemusí nový supplementary group list dostať. Kernel neopravuje credentials všetkých bežiacich procesov podľa každej zmeny identity databázy. Nový login, nový service start alebo riadený `newgrp` vytvorí nový credential context.

## 4. Real, effective, saved a filesystem IDs

Proces môže mať viac UID/GID hodnôt, pretože Linux podporuje kontrolované získanie a odovzdanie privilege.

- **Real UID/GID — pôvod identity procesu.** Používa sa napríklad pri účtovaní alebo pri rozhodovaní, kto proces spustil.
- **Effective UID/GID — identita použitá pri väčšine authorization checks.** Setuid program môže mať real UID používateľa a effective UID ownera executable súboru.
- **Saved set-ID — uložená privilegovaná identita.** Program môže dočasne dropnúť effective privilege a neskôr ho kontrolovane obnoviť bez nového `exec`.
- **Filesystem UID/GID — Linux-specific hodnota pre vybrané filesystem checks.** Väčšina aplikácií ju nemení priamo, ale je dôležitá pri niektorých serverových a compatibility modeloch.

Privilege-dropping daemon môže začať ako root, otvoriť privilegovaný socket, zmeniť UID/GID na service account a pokračovať s menším blast radiusom. Bez dôsledného dropu supplementary groups a capabilities však môže nechtiac zachovať viac práv, než ukazuje samotné effective UID.

```bash
cat /proc/<pid>/status | grep -E '^(Uid|Gid|Groups|Cap)'
```

## 5. Primary a supplementary groups

Každý proces má primary GID a množinu supplementary groups. Primary group ovplyvňuje napríklad default group ownership nových objektov, kým supplementary groups rozširujú membership pri group permission checkoch.

```bash
id
id alice
groups
getent group docker
```

Členstvo v skupine nie je automaticky nízkorizikové. Prístup k `docker.sock`, libvirt management socketu, backup agentovi alebo privileged log readerovi môže umožniť čítať secrets, mountnúť host filesystem alebo spustiť privilegovaný workload. Group membership treba posudzovať podľa capability služby za socketom, nie podľa nenápadného názvu skupiny.

## 6. Klasické DAC mode bits

Discretionary Access Control používa owner, group a other triedu. Kernel pri konkrétnom inode zvolí jednu applicable triedu; permissions z owner, group a other sa nesčítavajú.

```text
owner | group | other
  rwx |   rwx |   rwx
```

Pre regular file majú bity tento význam:

- **`r` — proces môže čítať obsah.** Neudeľuje automaticky možnosť získať pathname; parent directories musia povoliť traversal.
- **`w` — proces môže meniť obsah existujúceho inode.** Odstránenie filename sa riadi permissions parent directory, nie write bitom samotného súboru.
- **`x` — kernel dovolí execute lookup executable objektu.** Úspešné spustenie ďalej závisí od mount `noexec`, formátu, interpreteru, LSM policy a dostupnosti loadera.

Pre directory sú semantics odlišné:

- **`r` — čítanie directory entries.** Umožní listovať mená, ale bez `x` nemožno entries normálne statovať alebo otvárať.
- **`w` — zmena directory entries.** Umožňuje vytvárať, premenovávať a odstraňovať mená, ak sú splnené traversal a sticky-bit pravidlá.
- **`x` — search/traversal.** Proces môže pristúpiť k známemu menu a pokračovať cez adresár.

To vysvetľuje, prečo používateľ môže zmazať read-only súbor v zapisovateľnom adresári: unlink mení parent directory entry, nie obsah súboru.

## 7. Ako kernel vyberá owner, group alebo other

Pri klasickom mode checku kernel najprv porovná effective/filesystem UID s owner UID inode. Ak sa zhodujú, použije owner bity a nepadá ďalej na výhodnejšie group alebo other permissions. Ak owner nesedí, kontroluje owning GID a supplementary groups; pri zhode použije group triedu. Až bez zhody použije other.

```text
UID matches owner?
├─ áno → owner bits
└─ nie
   GID alebo supplementary group matches?
   ├─ áno → group bits
   └─ nie → other bits
```

Owner môže mať paradoxne menej oprávnení než group trieda, ale kernel mu group bits nepripočíta. Pri troubleshootingu preto nestačí povedať „používateľ je v skupine“; treba zistiť, či je zároveň ownerom a ktorú triedu kernel skutočne vybral.

## 8. Numerická a symbolická notácia

Numerická forma skladá `r=4`, `w=2`, `x=1` pre owner, group a other. `chmod 640 config.yaml` nastaví owner `rw-`, group `r--` a other `---`.

Symbolická forma je často bezpečnejšia pri malej cielenej zmene, pretože zachová ostatné bity:

```bash
chmod g+w shared-directory
chmod o-rwx secret
chmod u+x deploy.sh
```

Pri automatizácii treba deklarovať celý požadovaný permission contract alebo presne vedieť, ktoré bity sa menia. Opakované ad-hoc `chmod` kroky môžu časom vytvoriť drift a nejasný source of truth.

## 9. Ownership a vytvorenie nového objektu

Nový súbor dostane owner UID procesu. Group ownership typicky vychádza z effective GID procesu alebo zo setgid parent directory podľa filesystem semantics. Aplikácia po vytvorení môže ownership a permissions ďalej upraviť, ak má potrebné privilege.

```bash
chown alice:platform file
chgrp platform file
stat file
```

`chown` môže z bezpečnostných dôvodov odstrániť setuid/setgid bits. Zmena ownera totiž mení trust principal, ktorého privilege by executable pri spustení získal.

## 10. Umask

Umask nie je default permission hodnota. Je to maska bitov, ktoré sa odstránia z mode požadovaného aplikáciou.

```text
requested file mode:      666
umask:                    027
result after masking:     640

requested directory mode: 777
umask:                    027
result after masking:     750
```

Aplikácia môže po `open(..., mode)` vykonať `chmod`, takže výsledok nemusí zodpovedať iba umask. Default ACL môže navyše upraviť inheritance model. Pri produkčnom probléme treba overiť umask konkrétneho procesu alebo systemd unit, nie iba interactive shell administrátora.

## 11. Setuid, setgid a sticky bit

Special mode bits menia execution alebo directory inheritance semantics.

### Setuid na executable

Pri podporovanom native executable môže setuid nastaviť effective UID procesu na owner UID súboru. Program tak vykoná úzko definovanú privilegovanú operáciu bez toho, aby používateľ získal všeobecný root shell.

Setuid na shell scriptoch Linux z bezpečnostných dôvodov typicky nerešpektuje tak ako na native binaries, pretože interpreter a pathname races by vytvárali nebezpečný model. Setuid binary musí minimalizovať input surface, sanitizovať environment a čo najskôr dropnúť nepotrebné privilege.

### Setgid

Na executable nastavuje effective GID podľa group ownera súboru. Na directory spôsobuje, že nové children typicky zdedia group directory, čo vytvára stabilnejší shared-workspace contract než náhodné primary groups jednotlivých používateľov.

### Sticky bit

Na world-writable directory, napríklad `/tmp`, obmedzí unlink/rename cudzích entries na ownera súboru, ownera directory alebo privilegovaného procesu. Sticky bit nebráni používateľovi čítať obsah, ak mode/ACL čítanie povoľujú; rieši najmä namespace mutation.

```bash
find / -xdev -perm /6000 -type f 2>/dev/null
```

Audit setuid/setgid binaries má posudzovať ownera, write permissions, package provenance a reálnu potrebu privilege. Zapisovateľný setuid executable alebo jeho načítavaná konfigurácia je kritická escalation path.

## 12. POSIX ACL

ACL rozširuje owner/group/other model o named users, named groups a default inheritance. Nepredstavuje druhý nezávislý allow systém; ACL entries a mask spolu určujú effective DAC permissions.

```bash
getfacl shared.txt
setfacl -m u:alice:rw shared.txt
setfacl -m g:platform:rwx shared.txt
setfacl -m d:g:platform:rwx shared-directory
```

ACL mask obmedzuje owning group, named users a named groups. Entry môže vizuálne obsahovať `rwx`, ale `getfacl` ukáže `#effective:r-x`, pretože mask nepovoľuje write. `chmod` môže mask zmeniť a tým nepriamo zúžiť alebo rozšíriť viac ACL entries naraz.

Default ACL na directory sa používa ako template pri vytváraní children. Nie je to runtime permission aplikovaná priamo na všetky existujúce descendants. Zmena default ACL preto neopraví automaticky staré súbory.

## 13. Access Control List decision model

Zjednodušený POSIX ACL lookup najprv kontroluje owner entry. Potom named-user entry, ak existuje. Následne vyhodnotí matching group entries a mask; bez zhody použije other.

```text
owner match?
→ owner permissions

named user match?
→ named-user permissions ∩ mask

group matches?
→ union matching group entries ∩ mask

inak
→ other permissions
```

Pri diagnostike je preto dôležité vidieť celý `getfacl` output, nie iba `ls -l`. Znak `+` pri mode stringu signalizuje extended ACL alebo ďalšie metadata, ale neukazuje ich konkrétny efekt.

## 14. Root a capabilities

Tradičný Unix model pripisoval UID 0 široké privilege. Linux capabilities rozdeľujú časť týchto právomocí na samostatné bity, ktoré môžu byť v process effective, permitted, inheritable, bounding a ambient sets alebo priradené executable súboru.

- **`CAP_NET_BIND_SERVICE` — bind portov pod tradičným privileged thresholdom.** Umožní web serveru počúvať na porte 80 bez plného root runtime.
- **`CAP_CHOWN` — obídenie časti ownership pravidiel.** Je podstatne užšie než všeobecný root, ale stále môže meniť trust boundary súborov.
- **`CAP_NET_ADMIN` — rozsiahle network administration.** Zahŕňa citlivé routing, interface a firewall operácie, preto je v kontajneri vysokoriziková.
- **`CAP_SYS_ADMIN` — mimoriadne široká zberná capability.** Často sa prirovnáva k „novému rootu“, preto jej udelenie ruší veľkú časť least-privilege výhod.

```bash
getcap -r /usr/bin /usr/sbin 2>/dev/null
capsh --print
getpcaps <pid>
grep '^Cap' /proc/<pid>/status
```

Capability sama nemusí stačiť. Bounding set, user namespace, seccomp, LSM policy, mount flags alebo kernel configuration môžu operáciu stále blokovať. Naopak root v user namespace nemusí mať host-level privilege, aj keď vo svojom namespace vidí UID 0.

## 15. User namespaces a ID mapping

User namespace môže mapovať namespace UID/GID na odlišné host IDs. Proces môže byť root vo vnútri namespace, ale na hoste zodpovedať neprivilegovanému UID.

```text
container UID 0
→ user namespace mapping
→ host UID 100000
```

Filesystem access závisí od mappingu, mount modelu a podpory idmapped mounts. Súbor vlastnený host UID 1000 nemusí byť zapisovateľný container rootom, pretože jeho host credential je iné číslo. Pri kontajnerovom permission probléme treba porovnať namespace mapy v `/proc/<pid>/uid_map` a `/proc/<pid>/gid_map`, nie iba `id` vo vnútri kontajnera.

## 16. Kompletný filesystem authorization path

Úspešný `openat()` alebo `execve()` zvyčajne prejde viacerými vrstvami. Povolenie v jednej vrstve neobchádza deny alebo obmedzenie v ďalšej.

```text
process credentials
→ pathname traversal
→ DAC mode/ACL
→ capability exceptions
→ mount flags a filesystem state
→ immutable attributes
→ SELinux/AppArmor LSM
→ seccomp pre syscall
→ application-level authorization
```

- **Path traversal** môže zlyhať na parent directory bez `x`.
- **DAC/ACL** môže zakázať cieľovú read/write/execute operáciu.
- **Capabilities** môžu niektoré DAC checks obísť, ale iba podľa konkrétneho capability modelu.
- **Mount flags** môžu blokovať write, execute, set-ID alebo device behavior.
- **Filesystem attributes** ako immutable flag môžu zakázať zmenu aj ownerovi.
- **LSM policy** môže deny-nuť operáciu, ktorú klasické permissions povoľujú.
- **Application authorization** môže po úspešnom otvorení socketu alebo súboru stále odmietnuť business operáciu.

Troubleshooting preto nemá začať náhodným rozšírením permissions. Má identifikovať presný syscall, objekt, credentials a prvú vrstvu, ktorá rozhodnutie odmietla.

## 17. `sudo` ako policy-controlled credential transition

`sudo` nie je iba skratka pre „spusti ako root“. Vyhodnotí policy, autentizáciu, target user/group, command path, arguments, environment, working directory a logging pravidlá, potom vytvorí nový process credential context.

```text
caller
→ sudoers policy match
→ PAM authentication/account checks
→ environment policy
→ target UID/GID a groups
→ exec povoleného programu
→ audit/logging
```

```bash
sudo -l
sudo -l -U alice
visudo
visudo -f /etc/sudoers.d/platform
```

Pravidlo musí byť posudzované podľa capability programu, nie iba podľa názvu binary:

```text
%platform ALL=(root) /usr/bin/systemctl restart example.service
```

Aj úzko vyzerajúci command môže byť nebezpečný, ak používateľ vie meniť unit file, `EnvironmentFile`, executable, drop-in alebo writable working directory služby. Sudo policy a ownership všetkých transitívne načítavaných vstupov tvoria jeden security contract.

## 18. Sudoers riziká

- **Wildcard arguments — shell glob semantics nemusia zodpovedať očakávaniu administrátora.** Pravidlo môže povoliť ďalšie argumenty, option injection alebo nečakané paths.
- **Editor, pager, shell alebo interpreter — často poskytuje escape k arbitrary command execution.** Povoliť `vim`, `less`, `python`, `bash` alebo flexibilný package manager ako root je prakticky broad privilege.
- **Writable script alebo config — caller môže zmeniť to, čo root následne vykoná alebo načíta.** Kontrola musí zahŕňať parent directories, symlinky a plugin paths.
- **Environment — variables ako loader, module, config alebo proxy settings môžu meniť code path.** `sudo` environment sanitizuje podľa policy, ale `SETENV` a `env_keep` treba používať opatrne.
- **Command identity — symlink alebo nahradený executable môže zmeniť realitu pravidla.** Package-managed immutable path a digest-aware controls sú bezpečnejšie než writable custom scripts.

`NOPASSWD` nie je automaticky chyba ani bezpečnosť. Znižuje authentication friction a umožňuje automatizáciu, ale pri kompromitácii session poskytuje okamžitý prechod. Rozhodnutie musí vychádzať z threat modelu, command scope-u a ďalších controls.

## 19. PAM architektúra

Pluggable Authentication Modules poskytuje službám spoločný framework pre authentication, account policy, password management a session lifecycle. Služba, napríklad `sshd`, `login` alebo `sudo`, vyberie PAM service name a spracuje stack z `/etc/pam.d/`.

- **`auth` — overenie credential alebo vytvorenie authentication contextu.** Môže kontrolovať password, MFA, smart card alebo nastaviť pomocné credentials.
- **`account` — rozhodnutie, či už autentizovaný účet smie službu použiť.** Kontroluje expiry, allowed time, access rules alebo account state.
- **`password` — zmena a kvalita credential.** Používa sa pri password update workflowe, nie pri každom bežnom login-e.
- **`session` — otvorenie a zatvorenie session.** Môže vytvoriť home, nastaviť limits, zaznamenať audit event alebo vykonať cleanup.

Authentication success teda ešte nemusí znamenať account authorization success. Platné heslo pre expirovaný alebo policy-blocked účet môže prejsť `auth`, ale zlyhať v `account` fáze.

## 20. PAM control flags

Control flag určuje, ako výsledok modulu ovplyvní výsledok celého stacku. Poradie modulov je súčasťou security semantics.

- **`required` — failure spôsobí celkové zlyhanie, ale stack typicky pokračuje.** Pokračovanie môže znížiť information leakage a vykonať ďalšie potrebné moduly.
- **`requisite` — failure ukončí stack okamžite.** Je vhodný, keď ďalšie moduly nemajú zmysel, ale môže meniť timing a error behavior.
- **`sufficient` — úspech môže dokončiť stack, ak predchádzajúci required modul nezlyhal.** Nesprávne poradie môže nečakane obísť zamýšľaný druhý faktor.
- **`optional` — výsledok býva relevantný iba ak stack nemá iný rozhodujúci modul.** Často sa používa pre session side effects, ale nie je synonymom „bezpečne ignorovateľné za každých okolností“.

Pokročilá bracket syntax umožňuje mapovať konkrétne PAM return codes na akcie. Je presná, ale ľahko vytvorí policy, ktorej správca nerozumie. Každá zmena potrebuje test normálneho loginu, failure paths, recovery accountu a rollback session.

## 21. PAM failure containment

Chybná PAM konfigurácia môže zablokovať SSH, `sudo`, konzolový login aj service authentication súčasne. Bezpečný rollout preto zachová otvorenú root/recovery session, validuje syntax a testuje nový paralelný login pred zatvorením existujúceho prístupu.

Pri remote systéme treba poznať out-of-band recovery: cloud serial console, hypervisor console, rescue environment alebo break-glass image. „Opravíme to cez sudo“ nie je recovery plán, ak práve PAM stack pre sudo zlyhal.

## 22. Service identity a systemd

Služba nemá bežať ako root iba preto, že ju štartuje systemd. Unit môže deklarovať `User=`, `Group=`, `SupplementaryGroups=`, `CapabilityBoundingSet=`, `AmbientCapabilities=`, `NoNewPrivileges=` a filesystem sandboxing.

```text
systemd manager privilege
→ pripraví namespaces, limits a credentials
→ exec service ako úzky service account
→ kernel vynucuje runtime boundaries
```

Service account má vlastniť iba potrebné state directories. systemd directives ako `StateDirectory=`, `RuntimeDirectory=` a `LogsDirectory=` môžu vytvoriť paths s konzistentným ownershipom a lifecycle namiesto ručných `mkdir/chown` krokov.

## 23. Diagnostické nástroje a otázky

```bash
id alice
getent passwd alice
getent group platform
namei -l /path/to/object
stat /path/to/object
getfacl /path/to/object
findmnt -T /path/to/object
lsattr /path/to/object
sudo -l -U alice
getcap /path/to/executable
cat /proc/<pid>/status
```

- **`id` — aké credentials má táto session alebo účet podľa NSS?** Pri bežiacej službe používaj `/proc/<pid>/status`, nie predpoklad podľa unit file.
- **`namei -l` — ktorý parent component blokuje traversal?** Permission problem môže byť nad cieľovým súborom.
- **`getfacl` — aké named entries a mask skutočne platia?** `ls -l` zobrazuje iba zjednodušený pohľad.
- **`findmnt -T` — povoľuje mount požadovanú operáciu?** `ro`, `noexec` alebo `nosuid` môžu meniť výsledok.
- **`sudo -l` — ktoré pravidlo sa na caller a command matchuje?** Test musí používať rovnakého používateľa, host a argumenty.
- **`getcap/getpcaps` — aké file alebo process capabilities existujú?** Effective privilege nemusí byť viditeľné iba z UID.

## 24. End-to-end príklad: zápis do shared directory

Používateľ `alice` chce vytvoriť `/srv/team/report.txt`. Shell má snapshot supplementary groups z loginu. Kernel pri `openat(..., O_CREAT)` postupne overí traversal cez `/`, `/srv` a `/srv/team`, potom write a execute permission na parent directory. ACL mask môže zúžiť named group entry. Setgid directory určí group nového súboru a default ACL vytvorí child ACL. Umask sa aplikuje na requested mode v kombinácii s inheritance semantics.

Ak SELinux policy zakazuje doméne shellu zapisovať do typu adresára, klasické permissions môžu vyzerať správne a operácia stále dostane `EACCES`. Ak je mount read-only, výsledkom bude `EROFS`. Presný errno, audit log a process credentials odlišujú tieto failure modes.

## 25. Troubleshooting: používateľ je v skupine, ale nevie zapisovať

1. **Over credentials aktuálneho procesu.** `id` v danej session ukáže, či nový group membership už platí; účet v `getent group` nestačí.
2. **Over celý pathname.** `namei -l /srv/team/file` nájde parent bez traversal alebo nesprávny owner/group.
3. **Over directory semantics.** Na vytvorenie entry treba `w+x` na parent directory; write bit na cieľovom neexistujúcom súbore nemá význam.
4. **Over ACL a mask.** `getfacl` môže ukázať group `rwx`, ale effective `r-x` kvôli maske.
5. **Over mount a attributes.** `findmnt -T` a `lsattr` odhalia read-only mount alebo immutable flag.
6. **Over LSM deny.** SELinux audit alebo AppArmor log môže identifikovať policy vrstvu.
7. **Over skutočný service UID/GID.** Aplikácia môže bežať pod iným accountom než interactive test.
8. **Po oprave over least privilege.** Nepoužívaj `chmod 777`; vytvor presný group/ACL a inheritance contract a otestuj vytvorenie, rename aj delete.

## 26. Troubleshooting: `sudo` pravidlo sa nematchuje

Najprv spusti `sudo -l` ako konkrétny caller a over target user. Porovnaj canonical command path, argumenty, host specification, group membership a prípadné include files. Shell quoting môže spôsobiť, že argument string sa líši od očakávania policy.

Ak policy matchuje, ale program zlyhá, oddeľ sudo transition od aplikačného problému. Použi audit/logs, target environment a working directory. Nemeň pravidlo na `ALL=(ALL) ALL` iba preto, že konkrétny command má nejasný failure.

## 27. Anti-patterny

### `chmod 777` ako diagnostika

Rozšíri DAC pre všetkých, ale nevysvetlí ACL mask, mount flags, immutable attribute ani LSM deny. Môže vytvoriť data-tampering alebo code-injection cestu a súčasne ponechať pôvodný problém.

### Root service bez dôvodu

Root runtime zväčší blast radius každej memory corruption, command injection a supply-chain chyby. Lepší model používa service account, úzke capabilities, systemd sandbox a explicitné writable directories.

### Sudo na flexibilný interpreter

Povoliť `python`, `bash`, editor alebo nástroj s plugin/shell escape funkcionalitou je prakticky arbitrary root execution. Policy musí limitovať capability, nie iba jeden názov programu.

### PAM zmena bez recovery session

Jedna syntakticky alebo logicky chybná línia môže zablokovať všetky administratívne vstupy. Rollout identity policy potrebuje paralelný test a out-of-band recovery rovnako ako firewall alebo routing zmena.

### Skupina ako nezdokumentovaný privilege boundary

Členstvo v `docker`, `libvirt`, backup alebo monitoring skupine môže znamenať host compromise capability. Group catalog má vysvetliť poskytovaný prístup, ownera, approval a review lifecycle.

## 28. Kontrolné otázky

1. Prečo sú UID/GID stabilnejšou kernelovou identitou než používateľské mená a aké riziko prináša UID reuse?
2. Prečo nový group membership neovplyvní automaticky už bežiaci shell?
3. Ako sa líšia real, effective, saved a filesystem IDs?
4. Prečo sa owner, group a other permissions nesčítavajú?
5. Aký je rozdiel medzi `r`, `w` a `x` na regular file a directory?
6. Ako umask, setgid directory a default ACL spolu ovplyvnia nový súbor?
7. Ako ACL mask zmení effective permissions named user alebo group entry?
8. Prečo root alebo capability-enabled proces nemusí mať prístup cez každú security vrstvu?
9. Aké riziko predstavuje sudo pravidlo na editor, interpreter alebo writable script?
10. Aký je rozdiel medzi PAM `auth`, `account`, `password` a `session` fázou?
11. Ako `required`, `requisite` a `sufficient` menia vyhodnotenie PAM stacku?
12. Ako by si diagnostikoval zápis do shared directory bez použitia `chmod 777`?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Filesystem hierarchy, inodes a links](filesystem-hierarchy-inodes-links.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Shell, Bash, pipes, redirection a exit codes →](shell-bash-pipes-redirection-exit-codes.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
