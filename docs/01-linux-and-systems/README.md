# Linux and Systems

Táto sekcia vysvetľuje Linux od hranice kernel/user space cez procesy, filesystémy, identity a shell až po správu služieb, resources, bezpečnostné hranice a systematický troubleshooting. Cieľom nie je memorovať príkazy, ale rozumieť tomu, ktorú vrstvu systému príkaz pozoruje alebo mení.

## Predpoklady

Odporúča sa najprv dokončiť [DevOps Foundations](../00-foundations/README.md), najmä systems thinking, automation mindset, idempotenciu a desired state.

## Authoritative poradie

1. [Kernel a user space](kernel-and-user-space.md)
2. [Procesy, thready, PID a signals](processes-threads-pid-signals.md)
3. [Filesystem hierarchy, inodes a links](filesystem-hierarchy-inodes-links.md)
4. [Users, groups, permissions, sudo a PAM](users-groups-permissions-sudo-pam.md)
5. [Shell, Bash, pipes, redirection a exit codes](shell-bash-pipes-redirection-exit-codes.md)
6. [Environment variables](environment-variables.md)
7. [systemd, services a daemons](systemd-services-daemons.md)
8. [Package management](package-management.md)
9. [journald a logging](journald-and-logging.md)
10. [Storage, mounty a filesystems](storage-mounts-and-filesystems.md)
11. [CPU a memory fundamentals](cpu-and-memory-fundamentals.md)
12. [Linux networking](linux-networking.md)
13. [SSH](ssh.md)
14. [Cron a systemd timers](cron-and-systemd-timers.md)
15. [Namespaces](namespaces.md)
16. [cgroups](cgroups.md)
17. [Linux capabilities](linux-capabilities.md)
18. [SELinux a AppArmor](selinux-and-apparmor.md)
19. [Performance a troubleshooting](performance-and-troubleshooting.md)

Po tejto sekcii nasleduje samostatná oblasť Networking and Web Fundamentals, ktorá rozšíri Linux packet-path základ o protokoly, subnetting, DNS, HTTP, TLS, proxies a load balancing.

## Spôsob spracovania sekcie

Sekcia používa jeden prose-first runtime chain od kernel/user-space boundary cez process, filesystem a identity state až po service management, packages, logging, storage, resources, networking, remote access, scheduling, isolation a systematický troubleshooting. Každá kapitola začína priamo vysvetlením mechanizmu; legacy `Metadata`, `Learning` a `L2` scaffold sa už nepoužíva.

Nosný section model je:

```text
user alebo service intent
→ process identity a execution context
→ system call a kernel subsystem
→ resource, filesystem alebo network state
→ policy a isolation decision
→ runtime evidence
→ application/user outcome
→ diagnosis, recovery a second-scenario validation
```

Príkazy sú observation alebo mutation tools nad konkrétnou vrstvou. Text preto pri outputoch oddeľuje requested, configured, loaded, effective a user-visible state. Zoznamy zostávajú pri command/field references, porovnaniach a troubleshooting inventories; nenahrádzajú základný mechanistický výklad. Aktuálny authoritative stav sekcie je **19/19 · Ready for user review** po odstránení legacy štruktúry a chapter-by-chapter explanation-depth passe.

## Cieľ zvládnutia

Po dokončení sekcie má byť možné:

- rozlíšiť kernel space a user space a vysvetliť system call,
- analyzovať životný cyklus procesu a správanie threadov,
- vysvetliť, ako pathname vedie k inode a dátovým blokom,
- diagnostikovať identity, vlastníctvo a oprávnenia,
- bezpečne skladať shell pipeline a pracovať s exit statusom,
- vysvetliť dedenie environmentu,
- čítať a diagnostikovať stav služieb cez systemd,
- rozlíšiť repository metadata, dependency solver a lokálnu package database,
- používať structured journal fields, boot scope a retention pri diagnostike,
- sledovať cestu od block device cez filesystem po mount point,
- interpretovať CPU usage, load average, virtual memory, page cache, swap a OOM,
- diagnostikovať Linux packet path od DNS a route po socket a application protocol,
- bezpečne používať SSH host keys, user keys, bastion a port forwarding,
- navrhnúť idempotentný scheduled job s lockingom, observability a failure semantics,
- vysvetliť, ako namespaces izolujú pohľad na PID, mounts, network a identities,
- interpretovať cgroup v2 CPU, memory, I/O a PIDs controls,
- navrhnúť least-privilege capability sets namiesto plného root procesu,
- diagnostikovať DAC, capability a SELinux/AppArmor zamietnutia po jednotlivých vrstvách,
- viesť výkonový incident od používateľského symptómu cez testovateľnú hypotézu až po overenú nápravu.
