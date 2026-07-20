# Linux and Systems

Táto sekcia vysvetľuje Linux od hranice kernel/user space cez procesy, filesystémy, identity a shell až po správu služieb, resources, bezpečnostné hranice a systematický troubleshooting. Cieľom nie je memorovať príkazy, ale rozumieť tomu, ktorú vrstvu systému príkaz pozoruje alebo mení.

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
8. [Package management](package-management.md)
9. [journald a logging](journald-and-logging.md)
10. [Storage, mounty a filesystems](storage-mounts-and-filesystems.md)
11. [Memory a CPU fundamentals](cpu-and-memory-fundamentals.md)
12. [Linux networking](linux-networking.md)
13. [SSH](ssh.md)
14. [Cron a systemd timers](cron-and-systemd-timers.md)
15. [Namespaces](namespaces.md)
16. [cgroups](cgroups.md)
17. [Linux capabilities](linux-capabilities.md)
18. [SELinux a AppArmor](selinux-and-apparmor.md)
19. [Performance a troubleshooting](performance-and-troubleshooting.md)

Po tejto sekcii nasleduje samostatná oblasť Networking and Web Fundamentals, ktorá rozšíri Linux packet-path základ o protokoly, subnetting, DNS, HTTP, TLS, proxies a load balancing.

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
| Package management | Learning | L2 |
| journald a logging | Learning | L2 |
| Storage, mounty a filesystems | Learning | L2 |
| Memory a CPU fundamentals | Learning | L2 |
| Linux networking | Learning | L2 |
| SSH | Learning | L2 |
| Cron a systemd timers | Learning | L2 |
| Namespaces | Learning | L2 |
| cgroups | Learning | L2 |
| Linux capabilities | Learning | L2 |
| SELinux a AppArmor | Learning | L2 |
| Performance a troubleshooting | Learning | L2 |
