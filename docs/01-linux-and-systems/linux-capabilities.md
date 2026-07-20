# Linux Capabilities

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Users, groups, permissions, sudo a PAM](users-groups-permissions-sudo-pam.md), [Procesy, thready, PID a signals](processes-threads-pid-signals.md), [Linux Namespaces](namespaces.md)
- Súvisiace témy: least privilege, containers, systemd hardening, seccomp, SELinux/AppArmor

## 1. Definícia

Linux capabilities rozdeľujú tradičné root oprávnenia na samostatné privilegované schopnosti.

Namiesto binárneho modelu „root môže všetko, ostatní nič“ môže proces dostať iba konkrétnu právomoc, napríklad bind na nízky port alebo zmenu network configuration.

## 2. Problém, ktorý rieši

Mnohé aplikácie potrebujú iba malú časť root práv:

- web server potrebuje bind na port 80,
- network daemon potrebuje meniť interface alebo route,
- backup nástroj potrebuje čítať vybrané filesystems,
- debugger potrebuje inspectovať iný proces.

Spustiť celý proces ako root zväčšuje blast radius pri chybe alebo kompromitácii. Capabilities umožňujú oddeliť požadovanú schopnosť od plného root účtu.

## 3. Mentálny model

```text
root privileges
├── CAP_NET_BIND_SERVICE
├── CAP_NET_ADMIN
├── CAP_SYS_ADMIN
├── CAP_CHOWN
├── CAP_DAC_OVERRIDE
├── CAP_SYS_PTRACE
└── ...
```

Proces nemá jednu capability množinu, ale viac capability sets, ktoré určujú, čo môže aktuálne používať a čo môže získať pri `execve()`.

## 4. Dôležité capabilities

| Capability | Typický význam |
|---|---|
| `CAP_NET_BIND_SERVICE` | bind na privileged ports pod 1024 |
| `CAP_NET_ADMIN` | network configuration, routing, firewall operations |
| `CAP_CHOWN` | meniť owner súborov |
| `CAP_DAC_OVERRIDE` | obísť časť discretionary access checks |
| `CAP_SETUID` | meniť UID procesu |
| `CAP_SETGID` | meniť GID procesu |
| `CAP_SYS_PTRACE` | ptrace a inspectovanie procesov podľa policy |
| `CAP_SYS_CHROOT` | používať `chroot()` |
| `CAP_MKNOD` | vytvárať device nodes |
| `CAP_SYS_TIME` | meniť systémový čas |
| `CAP_SYS_ADMIN` | široká skupina administratívnych operácií |

`CAP_SYS_ADMIN` je veľmi široká capability a často sa prirovnáva k „novému root“. Udeliť ju iba preto, že iná konfigurácia nefunguje, je slabý least-privilege prístup.

## 5. Capability sets procesu

Proces má typicky tieto množiny:

### Permitted

Horná hranica capabilities, ktoré proces môže efektívne používať alebo presúvať do effective set.

### Effective

Capabilities, ktoré kernel aktuálne používa pri permission checks.

### Inheritable

Capabilities, ktoré sa môžu podieľať na dedení cez `execve()` spolu s file inheritable mask.

### Bounding

Horná hranica capabilities, ktoré proces a jeho potomkovia môžu získať. Odstránenie z bounding setu je typicky nevratné pre daný process tree.

### Ambient

Capabilities, ktoré sa môžu zachovať pri `execve()` neprivilegovaného programu za presne definovaných podmienok.

Pozorovanie:

```bash
cat /proc/self/status | grep '^Cap'
capsh --print
```

Výstup v `/proc/<PID>/status` používa bitové masky:

```text
CapInh
CapPrm
CapEff
CapBnd
CapAmb
```

Dekódovanie:

```bash
capsh --decode=<hex-mask>
```

## 6. Root a capabilities

Moderný kernel vykonáva mnohé privilege checks cez capability model. UID 0 typicky dostáva široké capability sets, ale správanie ovplyvňujú:

- securebits,
- user namespaces,
- file capabilities,
- bounding set,
- `no_new_privs`,
- LSM politika,
- container runtime configuration.

Root UID preto nie je jediný autoritatívny údaj o privilege. Treba pozerať effective capabilities a security context.

## 7. File capabilities

Executable file môže mať capability metadata v extended attribute.

```bash
getcap /usr/bin/ping
sudo setcap cap_net_raw=ep /path/to/program
getcap /path/to/program
```

Zápis:

```text
cap_net_raw=ep
```

znamená, že capability je v file permitted množine a effective flag žiada jej aktiváciu po `execve()`.

Odstránenie:

```bash
sudo setcap -r /path/to/program
```

File capabilities sú citlivé na:

- filesystem podporu extended attributes,
- kopírovanie a archiváciu,
- package upgrades,
- container image layers,
- user namespace mapping,
- mount options a security policy.

Bežné `cp` alebo deployment pipeline nemusia vždy zachovať xattrs podľa očakávania.

## 8. `execve()` a transformácia sets

Pri spustení nového programu kernel vypočíta nové capability sets z kombinácie:

- process permitted/inheritable/ambient sets,
- file permitted/inheritable metadata,
- bounding set,
- privileged-file pravidiel,
- UID transition,
- securebits a `no_new_privs`.

Presné rovnice sú komplexné. Dôležitý mentálny model:

```text
current process state
+ executable file metadata
+ global boundaries
→ capability state nového programu
```

Preto môže capability zmiznúť po spustení child commandu, hoci parent ju mal.

## 9. Ambient capabilities

Ambient set rieši bežný problém: proces chce spustiť neprivilegovaný executable a zachovať vybrané capabilities bez file capability metadata.

Capability môže byť v ambient set iba ak je zároveň v permitted a inheritable set.

Systemd príklad:

```ini
[Service]
User=app
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
NoNewPrivileges=yes
ExecStart=/usr/local/bin/app
```

To umožní neprivilegovanému userovi bind na port 80 bez plného root procesu.

## 10. Bounding set

Bounding set určuje maximálny capability priestor pre process tree.

Systemd:

```ini
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
```

Alebo explicitné odobratie:

```ini
CapabilityBoundingSet=~CAP_SYS_ADMIN CAP_SYS_PTRACE
```

Čím užší bounding set, tým menej capabilities môže proces neskôr získať cez file metadata alebo iné mechanizmy.

Pri hardeningu je bounding set často dôležitejší než iba momentálny effective set.

## 11. `NoNewPrivileges`

Kernel flag `no_new_privs` garantuje, že `execve()` nezvýši privilege procesu cez setuid, setgid alebo file capabilities.

Systemd:

```ini
NoNewPrivileges=yes
```

Je to silný hardening control, ale môže rozbiť programy, ktoré legitímne očakávajú privilege transition.

Kontrola procesu:

```bash
cat /proc/<PID>/status | grep NoNewPrivs
```

## 12. Capabilities a user namespaces

Capability je vždy vyhodnocovaná vo vzťahu k user namespace.

Proces môže mať `CAP_NET_ADMIN` vo svojom user namespace, ale nie v initial host user namespace. To mu môže umožniť spravovať network namespace, ktorý vlastní jeho user namespace, nie host networking.

```text
CAP_NET_ADMIN in container user namespace
≠
CAP_NET_ADMIN over host network namespace
```

Práve tento scope umožňuje rootless isolation, ale aj komplikuje interpretáciu „process má capability“.

## 13. Containers

Container runtime typicky začne so širšou množinou a odstráni capabilities podľa default policy.

Princíp:

```text
image process requirements
→ runtime default set
→ explicit drop
→ explicit add len výnimočne
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

`privileged: true` spravidla odstraňuje veľkú časť container isolation a nie je ekvivalentom pridania jednej capability.

## 14. systemd hardening

Príklad služby:

```ini
[Service]
User=web
ExecStart=/usr/local/bin/web
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE
NoNewPrivileges=yes
PrivateDevices=yes
ProtectSystem=strict
ProtectHome=yes
```

Overenie:

```bash
systemctl show web.service \
  -p CapabilityBoundingSet \
  -p AmbientCapabilities \
  -p NoNewPrivileges

systemd-analyze security web.service
```

Skóre z `systemd-analyze security` je orientačné. Nenahrádza threat model ani runtime test.

## 15. SUID vs. file capabilities

### SUID root executable

Program sa spustí s effective UID ownera, často root. Potom musí sám bezpečne dropnúť privileges.

### File capability

Executable dostane iba konkrétne capability podľa metadata.

File capabilities zvyčajne znižujú privilege scope, ale nie sú automaticky bezpečné. Program musí byť navrhnutý tak, aby capability nezneužil cez nebezpečný input, plugin alebo child process.

## 16. Capability-aware troubleshooting

Aplikácia dostáva:

```text
bind: Permission denied
```

pri porte 80.

Postup:

```bash
id
getcap /path/to/app
cat /proc/<PID>/status | grep '^Cap'
capsh --decode=<CapEff-mask>
systemctl show app.service -p AmbientCapabilities -p CapabilityBoundingSet
```

Otázky:

1. Má process `CAP_NET_BIND_SERVICE` effective?
2. Je capability v bounding set?
3. Nezablokoval ju `NoNewPrivileges` pri exec transition?
4. Beží process v inom user namespace?
5. Neblokuje operáciu SELinux/AppArmor alebo seccomp?

`EPERM` alebo `EACCES` nie je dôkaz, že chýba práve capability. Kernel permission môže zlyhať na inej vrstve.

## 17. Bezpečnostné riziká

### Široké capabilities

`CAP_SYS_ADMIN`, `CAP_SYS_MODULE`, `CAP_SYS_RAWIO`, `CAP_SYS_PTRACE` a niektoré ďalšie capabilities môžu výrazne oslabiť izoláciu.

### Capability leakage

Wrapper alebo shell môže spustiť ďalší program, ktorý zdedí ambient alebo effective privilege mimo pôvodného zámeru.

### Privileged helper

Aj úzky privileged helper musí striktne validovať input a minimalizovať API surface.

### Package upgrade

Upgrade môže nahradiť executable a odstrániť alebo zmeniť file capabilities.

## 18. Časté omyly

### „Capability znamená, že process je bezpečný non-root“

Nie. Niektoré capabilities sú veľmi silné a aplikácia môže mať ďalšie attack surfaces.

### „Root má vždy všetky capabilities“

Nie nevyhnutne. Bounding set, user namespace a hardening môžu privilege obmedziť.

### „File capability sa automaticky zachová pri kopírovaní“

Nie vždy. Extended attributes môžu byť stratené.

### „Keď capability pridám do permitted setu, process ju používa“

Kernel checks typicky používajú effective set.

### „Permission denied znamená chýbajúcu capability“

Môže ísť o DAC, ACL, SELinux/AppArmor, seccomp, namespace scope alebo read-only mount.

## 19. Kontrolné otázky

1. Prečo capabilities znižujú potrebu plného root procesu?
2. Aký je rozdiel medzi permitted a effective set?
3. Načo slúži bounding set?
4. Ako fungujú ambient capabilities?
5. Čo garantuje `NoNewPrivileges`?
6. Prečo capability v user namespace nemusí platiť nad host resource?
7. Aký je rozdiel medzi SUID executable a file capability?
8. Prečo je `CAP_SYS_ADMIN` problematická?
9. Ako by si diagnostikoval `Permission denied` pri bind na port 80?
