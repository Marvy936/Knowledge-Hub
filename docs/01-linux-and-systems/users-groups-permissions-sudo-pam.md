# Users, groups, permissions, sudo a PAM

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Filesystem hierarchy, inodes a links](filesystem-hierarchy-inodes-links.md)
- Súvisiace témy: process credentials, SSH, capabilities, SELinux, containers

## 1. Identity v Linuxe

Linux kernel rozhoduje o prístupe podľa číselných identít a credentials procesu. Používateľské mená a názvy skupín sú user-space mapovania na UID a GID.

```text
username ── NSS lookup ──→ UID
 groupname ─ NSS lookup ──→ GID
```

Súbor na filesystéme vlastní číselný UID a GID. Ak účet odstrániš, súbor nestratí owner ID; nástroje môžu namiesto mena zobrazovať číslo.

## 2. Databázy účtov

Lokálne identity typicky používajú:

- `/etc/passwd` — meno, UID, primary GID, home, shell,
- `/etc/group` — skupiny a supplementary membership,
- `/etc/shadow` — password hashes a aging metadata,
- `/etc/gshadow` — group security metadata.

NSS — Name Service Switch — určuje zdroje lookupov v `/etc/nsswitch.conf`. Identity preto môžu pochádzať aj z LDAP, SSSD, systemd-resolved kompatibilných modulov alebo iných providers.

```bash
getent passwd alice
getent group platform
id alice
```

`getent` je vhodnejší než priame grepovanie `/etc/passwd`, pretože rešpektuje NSS konfiguráciu.

## 3. Real, effective a saved IDs

Proces môže mať viac identít:

- real UID — pôvodný používateľ,
- effective UID — identita používaná pri väčšine permission checks,
- saved set-user-ID — umožňuje kontrolované prepínanie privilege,
- filesystem UID — špecifická Linux vrstva pre filesystem checks.

Podobný model existuje pre GID. Bežný proces má často všetky hodnoty rovnaké, ale setuid programy alebo privilege-dropping daemons ich môžu používať rozdielne.

## 4. Primary a supplementary groups

Používateľ má jednu primary group a môže patriť do viacerých supplementary groups.

Pri login session sa group list načíta do process credentials. Pridanie používateľa do skupiny preto nemusí ovplyvniť už bežiaci shell; často treba novú session.

```bash
id
groups
getent group docker
```

Členstvo v privilegovanej skupine môže byť ekvivalentné rozsiahlemu systémovému prístupu. Napríklad prístup k Docker daemon socketu typicky umožňuje ovládnuť hosta.

## 5. Mode bits

Klasické Unix permissions majú tri triedy:

```text
owner | group | other
  rwx |   rwx |   rwx
```

Význam pre regular file:

- `r` — čítanie obsahu,
- `w` — zmena obsahu,
- `x` — execution.

Význam pre directory:

- `r` — čítanie zoznamu entries,
- `w` — vytváranie a odstraňovanie entries,
- `x` — search/traverse cez directory.

Kernel vyberá jednu triedu: owner, inak matching group, inak other. Permissions sa nesčítavajú naprieč triedami.

## 6. Numerická notácia

```text
r = 4
w = 2
x = 1
```

Príklady:

```bash
chmod 640 config.yaml
chmod 750 script.sh
```

`640` znamená:

```text
owner: rw-
group: r--
other: ---
```

Symbolická forma je často bezpečnejšia pri cielenej zmene:

```bash
chmod g+w directory
chmod o-rwx secret
chmod u+x script.sh
```

## 7. Vlastníctvo a umask

```bash
chown user:group file
chgrp group file
```

`umask` neurčuje výsledné permissions priamo. Odoberá bity z mode požadovaného aplikáciou.

Typicky:

```text
regular file request: 666
directory request:    777
umask:                 027
výsledok file:         640
výsledok directory:    750
```

Aplikácia môže po vytvorení permissions ďalej meniť. ACL a default ACL môžu výsledok tiež ovplyvniť.

## 8. Special mode bits

### setuid

Na executable môže spôsobiť, že proces získa effective UID ownera súboru. Používa sa pri úzko kontrolovaných programoch, napríklad pri operáciách vyžadujúcich privilege.

### setgid

Na executable ovplyvňuje effective GID. Na directory spôsobí, že nové entries typicky zdedia group directory, čo je užitočné pre zdieľané pracovné adresáre.

### sticky bit

Na zdieľanom zapisovateľnom directory, napríklad `/tmp`, obmedzuje odstraňovanie entries na ownera súboru, ownera directory alebo privilegovaný proces.

```bash
find / -xdev -perm /6000 -type f 2>/dev/null
```

Setuid/setgid binaries treba auditovať, pretože chyba v nich môže viesť k privilege escalation.

## 9. POSIX ACL

ACL umožňujú detailnejšie permissions než owner/group/other.

```bash
getfacl shared.txt
setfacl -m u:alice:rw shared.txt
setfacl -m d:g:platform:rwx shared-directory
```

ACL mask obmedzuje efektívne permissions named users, named groups a owning group. To je častý zdroj prekvapenia: entry môže zobrazovať `rwx`, ale efektívne oprávnenie je kvôli maske užšie.

## 10. Root a capabilities

UID 0 má tradične rozsiahle privilege, ale moderný Linux rozdeľuje časť právomocí na capabilities.

Príklady:

- `CAP_NET_BIND_SERVICE` — bind na privilegované porty,
- `CAP_NET_ADMIN` — správa sieťových nastavení,
- `CAP_SYS_ADMIN` — veľmi široká capability,
- `CAP_CHOWN` — obídenie ownership obmedzení pri chown.

```bash
getcap -r /usr/bin /usr/sbin 2>/dev/null
capsh --print
```

Least privilege znamená udeliť konkrétnu potrebnú capability namiesto plného root prístupu, ak to threat model a aplikácia umožňujú.

## 11. sudo

`sudo` vykoná príkaz podľa policy, typicky z `/etc/sudoers` a `/etc/sudoers.d/`.

Bezpečná editácia:

```bash
visudo
visudo -f /etc/sudoers.d/platform
```

Príklad úzko definovaného pravidla:

```text
%platform ALL=(root) /usr/bin/systemctl restart example.service
```

Riziká:

- wildcardy môžu povoliť viac, než vyzerá,
- povolený editor, shell alebo interpreter často umožní arbitrary command execution,
- zapisovateľný script spúšťaný cez sudo je privilege escalation path,
- environment variables môžu meniť správanie programu.

`sudo` nie je len „prepni sa na root“. Je policy enforcement, audit a credential transition mechanizmus.

## 12. PAM

PAM — Pluggable Authentication Modules — poskytuje skladateľný authentication framework pre služby ako login, sudo, SSH alebo display manager.

Typické skupiny modulov:

| Typ | Úloha |
|---|---|
| `auth` | overenie identity alebo credential |
| `account` | kontrola, či účet môže službu použiť |
| `password` | zmena a politika credential |
| `session` | kroky pri otvorení a zatvorení session |

Konfigurácia býva v `/etc/pam.d/`. Control flags ako `required`, `requisite`, `sufficient` a `optional` určujú, ako výsledok modulu ovplyvní celý stack.

Chybná PAM konfigurácia môže zablokovať všetky loginy. Zmenu treba validovať s otvorenou recovery session a jasným rollbackom.

## 13. Permission check nie je jediná vrstva

Aj keď mode bits povoľujú operáciu, prístup môže blokovať:

- ACL,
- SELinux alebo AppArmor,
- read-only mount,
- immutable file attribute,
- namespace alebo id mapping,
- capability model,
- application-level authorization.

Diagnostika musí identifikovať presnú vrstvu, nie iba meniť `chmod`.

## 14. Diagnostické príkazy

```bash
id <user>
getent passwd <user>
getent group <group>
namei -l /path/to/object
stat /path/to/object
getfacl /path/to/object
findmnt -T /path/to/object
sudo -l -U <user>
lsattr /path/to/object
```

Pri procese:

```bash
cat /proc/<pid>/status | grep -E '^(Uid|Gid|Groups|Cap)'
```

## 15. Časté omyly

### „chmod 777 vyrieši permission problém“

Môže zmeniť symptóm, ale ničí least privilege a nemusí vyriešiť ACL, mount alebo LSM policy.

### „Root môže vždy všetko“

Capabilities, namespaces, read-only mounts, LSM policy a ďalšie mechanizmy môžu root proces obmedziť.

### „Pridanie do skupiny platí okamžite všade“

Nie pre už existujúce process credentials. Nová login session načíta nový group list.

### „sudo pravidlo na jeden program je automaticky bezpečné“

Program môže poskytovať shell escape, načítavať pluginy, konfiguráciu alebo environment-controlled code.

## 16. Troubleshooting scenár

Používateľ patrí do skupiny `platform`, ale stále nevie zapisovať do zdieľaného directory.

1. Over group membership cez `id` v aktuálnej session.
2. Over owner, group a mode bits na každom path komponente cez `namei -l`.
3. Over ACL a ACL mask.
4. Over mount flags a read-only stav.
5. Over SELinux/AppArmor denial.
6. Over, či aplikácia beží pod očakávaným UID/GID.

## 17. Kontrolné otázky

1. Prečo kernel pracuje primárne s UID/GID a nie s menami?
2. Ako sa líši execute bit na súbore a adresári?
3. Ako umask ovplyvní vytvorenie súboru s request mode `666`?
4. Prečo môže sudo pravidlo na editor predstavovať plný root prístup?
5. Akú úlohu majú `auth`, `account` a `session` moduly v PAM?
