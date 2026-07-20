# Linux and Systems

Táto sekcia vysvetľuje Linux od hranice kernel/user space cez procesy, filesystémy, identity a shell až po správu služieb. Cieľom nie je memorovať príkazy, ale rozumieť tomu, ktorú vrstvu systému príkaz pozoruje alebo mení.

## Predpoklady

Odporúča sa najprv dokončiť [DevOps Foundations](../00-foundations/README.md), najmä systems thinking, automation mindset, idempotenciu a desired state.

## Odporúčané poradie

1. [Kernel a user space](kernel-and-user-space.md)
2. [Procesy, thready, PID a signals](processes-threads-pid-signals.md)
3. [Filesystem hierarchy, inodes a links](filesystem-hierarchy-inodes-links.md)
4. [Users, groups, permissions, sudo a PAM](users-groups-permissions-sudo-pam.md)
5. [Shell, Bash, pipes, redirection a exit codes](shell-bash-pipes-redirection-exit-codes.md)
6. [Environment variables](environment-variables.md)
7. [systemd, services a daemons](systemd-services-daemons.md)

Ďalšie plánované kapitoly: package management, journald a logging, storage a mounty, CPU a memory, Linux networking, SSH, cron a systemd timers, namespaces, cgroups, capabilities, SELinux/AppArmor a system troubleshooting.

## Cieľ zvládnutia

Po dokončení sekcie má byť možné:

- rozlíšiť kernel space a user space a vysvetliť system call,
- analyzovať životný cyklus procesu a správanie threadov,
- vysvetliť, ako pathname vedie k inode a dátovým blokom,
- diagnostikovať identity, vlastníctvo a oprávnenia,
- bezpečne skladať shell pipeline a pracovať s exit statusom,
- vysvetliť dedenie environmentu,
- čítať a diagnostikovať stav služieb cez systemd.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Kernel a user space | Learning | L2 |
| Procesy, thready, PID a signals | Learning | L2 |
| Filesystem hierarchy, inodes a links | Learning | L2 |
| Users, groups, permissions, sudo a PAM | Learning | L2 |
| Shell, Bash, pipes, redirection a exit codes | Learning | L2 |
| Environment variables | Learning | L2 |
| systemd, services a daemons | Learning | L2 |
