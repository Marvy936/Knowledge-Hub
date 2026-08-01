from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "01-linux-and-systems"

OPENINGS: dict[str, str] = {
    "kernel-and-user-space.md": """Linux rozdeľuje execution do privilegovaného kernel space a obmedzeného user space, aby jeden proces nemohol priamo meniť spoločnú pamäť, device state, routing ani credentials iných procesov. Hranicu vynucuje CPU privilege model, page-table protection a kernelové access checks; nie je to iba konvencia medzi programátormi.

Keď user-space program potrebuje službu kernelu, request prejde cez presne definovanú boundary:

```text
application alebo runtime
→ library wrapper
→ system call ABI
→ kernel subsystem
→ driver, filesystem, scheduler alebo network stack
→ return value a errno
```

Úspešný system call preukazuje iba výsledok danej kernelovej operácie pre konkrétny process context. Nepreukazuje, že vyšší application workflow uspel. Pri diagnostike treba preto oddeliť library behavior, syscall result, kernel log, device response a business outcome; rovnaký používateľský symptóm môže vzniknúť v každej z týchto vrstiev.""",
    "processes-threads-pid-signals.md": """Proces je runtime container pre address space, credentials, file descriptors, signal dispositions a ďalší kernel state. Thread je samostatne schedulovateľný task, ktorý zdieľa vybrané resources s ostatnými threadmi procesu. PID je identifikátor v konkrétnom PID namespace, nie globálna a navždy stabilná identita workloadu.

Lifecycle možno čítať ako state machine:

```text
create/fork/clone
→ runnable alebo sleeping task
→ scheduled execution
→ block, wake-up, stop alebo signal handling
→ exit
→ parent wait a resource reaping
```

Signal nie je priamy remote function call. Kernel ho eviduje ako pending event, vyhodnotí masku a disposition a doručí ho v bezpečnom execution point-e; `SIGKILL` a `SIGSTOP` nemožno zachytiť. Úspešné odoslanie signalu iba znamená, že kernel prijal request pre matching task. Nepreukazuje, že process vykonal zamýšľaný graceful shutdown, flushol dáta alebo že service manager už vytvoril náhradnú generation.""",
    "filesystem-hierarchy-inodes-links.md": """Linux filesystem model oddeľuje pathname od objektu, na ktorý meno ukazuje. Pathname sa pri každom lookup-e rozkladá cez mount namespace, directory entries a permissions až k inode; inode drží metadata a odkazy na data blocks, nie pôvodný názov súboru.

```text
pathname
→ mount a directory traversal
→ dentry
→ inode
→ open-file description
→ process file descriptor
→ data alebo device operation
```

Hard link vytvára ďalšie directory meno pre rovnaký inode. Symbolic link je samostatný inode obsahujúci ďalšiu path, ktorá sa pri použití znovu vyhodnotí. Zmazanie mena preto nemusí odstrániť otvorený obsah: process môže ďalej držať file descriptor a disk space sa uvoľní až po poslednom linku a poslednej open reference. Pri troubleshooting treba rozlíšiť path visibility, inode identity, mount view, open handles a skutočnú storage alokáciu.""",
    "users-groups-permissions-sudo-pam.md": """Linux access decision nezačína názvom používateľa v `/etc/passwd`, ale credentials aktuálneho procesu. Kernel pri operácii vyhodnocuje effective UID/GID, supplementary groups, filesystem ownership a mode bits, ACLs, capabilities a podľa systému aj MAC policy. User name je user-space mapovanie čísla UID na čitateľný label.

```text
login alebo service identity
→ PAM a credential establishment
→ process UID/GID/groups/capability sets
→ object owner, mode a ACL
→ kernel DAC decision
→ optional SELinux/AppArmor decision
→ allow alebo errno
```

`sudo` nevypína permissions. Po policy, authentication a environment rozhodnutí vytvorí nový process s inými credentials a audit contextom. Úspešný `sudo` command preto nepreukazuje, že pôvodná service identity má potrebný least-privilege access. Diagnostika musí čítať identity procesu, celý pathname, ACLs, mount flags, capabilities a MAC denial namiesto automatického riešenia cez `chmod 777` alebo permanentný root.""",
    "shell-bash-pipes-redirection-exit-codes.md": """Shell je parser a process orchestrator, nie iba miesto na zapisovanie príkazov. Bash najprv rozpozná syntax, následne vykoná parameter, command, arithmetic a pathname expansions, aplikuje quoting a word splitting, nastaví redirections a až potom spustí builtin alebo externý program. Malá zmena úvodzoviek preto môže zmeniť počet argumentov skôr, než cieľový command vôbec začne.

Pipeline vytvára viac procesov a file descriptors:

```text
producer stdout
→ pipe buffer
→ consumer stdin
→ jednotlivé exit statuses
→ shell pipeline status
```

Bez `pipefail` typicky rozhoduje posledný command, takže `producer | tee file` môže byť zelený aj po zlyhaní producer-a. Redirection sa navyše môže vytvoriť pred execution a zanechať prázdny alebo partial output. Robustný skript musí rozumieť parseru, arrays, `"$@"`, file descriptors, `PIPESTATUS`, traps, signal forwarding a atomic replacementu; samotné `set -e` nie je úplný error model.""",
    "environment-variables.md": """Environment je množina stringových `name=value` položiek pripojená ku konkrétnemu procesu. Nie je to globálna tabuľka operačného systému. Parent pri vytvorení child procesu odovzdá snapshot environmentu a neskoršia zmena v parentovi automaticky neprepíše už bežiace children.

```text
shell alebo service manager environment
→ expansion a override rules
→ fork/execve environment vector
→ application parsing
→ loaded runtime configuration
```

Export v shelli iba označí shell variable na dedenie do budúcich externých procesov. Súbor `.env`, systemd `EnvironmentFile=` alebo Kubernetes Secret je zase source input; application môže hodnotu načítať iba pri štarte, cacheovať ju alebo vôbec nepoužiť. Pri overovaní preto treba odlíšiť declared value, environment procesu a effective application state. Environment je tiež slabá secret boundary: hodnoty môžu uniknúť cez process inspection, crash dump, debug log alebo child proces.""",
    "systemd-services-daemons.md": """systemd je service manager a dependency/job engine, ktorý prekladá unit configuration na runtime procesy, cgroups, sockets, mounts a lifecycle actions. Unit file je source configuration; loaded unit, queued job, active state, main PID a skutočná service readiness sú odlišné stavy.

```text
unit files a drop-ins
→ manager load a dependency graph
→ start/stop/reload job
→ process creation a cgroup
→ activation/readiness notification
→ restart, timeout alebo failure handling
```

`systemctl start` s úspešným exit statusom preukazuje, že manager dokončil svoj job podľa unit semantics. Pri `Type=simple` to môže znamenať iba úspešný fork/exec, nie funkčný listener alebo pripravenú databázovú dependency. Diagnostika preto kombinuje `systemctl show/status`, resolved unit cez `systemctl cat`, journal, process/cgroup state, sockets a application-level probe. Ručný štart binary mimo systemd môže fungovať s iným userom, environmentom, limits a namespaces a nie je dôkazom správnej unit configuration.""",
    "package-management.md": """Package manager koordinuje repository metadata, dependency solving, cryptographic trust, download, unpacking, maintainer scripts a lokálnu package database. Príkaz `apt install` alebo `dnf upgrade` preto nie je iba kopírovanie binary; je to transakcia meniaca files, services, alternatives, triggers a niekedy aj boot artifacts.

```text
configured repositories a trust roots
→ metadata refresh
→ dependency/version solution
→ package download a verification
→ unpack/configure scripts
→ local database a service effects
→ runtime read-back
```

Úspešná transakcia preukazuje, že package manager dokončil deklarované kroky. Nepreukazuje, že daemon používa nové libraries, že pending reboot nie je potrebný ani že application contract zostal kompatibilný. Repository freshness, pinning, holds, partial transactions a script failures môžu vytvoriť rozdiel medzi requested, installed a loaded version. Bezpečný upgrade preto zahŕňa plan/read-back, service restart alebo replacement, functional verification a recovery strategy.""",
    "journald-and-logging.md": """Log je event record vytvorený konkrétnym producerom v konkrétnom observation point-e. journald prijíma messages zo stdout/stderr services, syslog socketu, kernelu a audit-adjacent sources, dopĺňa trusted metadata a ukladá ich do volatile alebo persistent journal files podľa configuration a dostupnosti storage.

```text
system occurrence
→ application/kernel log emission
→ transport do journald
→ trusted a producer fields
→ journal storage/rotation
→ query, forwarding alebo alert
```

Neexistujúci log nie je dôkazom, že udalosť nenastala. Producer mohol crashnúť pred zápisom, rate limit mohol message dropnúť, boot scope mohol byť nesprávny alebo retention mohla záznam odstrániť. Naopak prítomný text `started` nepreukazuje service readiness. Diagnostika musí viazať journal na boot ID, unit, PID, monotonic/realtime timestamp a runtime generation a následne korelovať record s kernel, network alebo business evidence.""",
    "storage-mounts-and-filesystems.md": """Storage path v Linuxe skladá viac nezávislých vrstiev. Application zapisuje cez VFS do mounted filesystemu; ten môže ležať na partition, device mapper targete, LVM logical volume, encrypted mappingu, RAID-e alebo virtual block device. Každá vrstva má vlastnú identity, capacity, failure a persistence semantics.

```text
application file operation
→ pathname a mount namespace
→ filesystem a page cache
→ block layer a queues
→ mapper/LVM/RAID/encryption
→ physical alebo virtual device
→ durable media acknowledgement
```

`df` meria filesystem allocation, `du` prechádza reachable pathnames a `lsblk` zobrazuje block topology; preto môžu ukazovať rozdielne hodnoty bez chyby. Mount point môže byť prekrytý ďalším mountom, deleted-open file môže držať space a úspešný `write()` môže znamenať iba prijatie do page cache. Prevádzkové overenie potrebuje rozlíšiť visibility, capacity, I/O completion, flush/durability, filesystem consistency a schopnosť obnovy.""",
    "cpu-and-memory-fundamentals.md": """CPU a memory telemetry opisuje odlišné resources a časy. CPU utilization ukazuje, koľko scheduling time-u tasky spotrebovali; nehovorí sama o sebe, či workload čaká v run queue, je throttled cgroupou alebo blokuje na I/O. Load average zahŕňa runnable a vybrané uninterruptible tasks a nie je percento CPU.

Memory model spája virtual address spaces, page tables, anonymous pages, file-backed page cache, reclaim, swap a cgroup accounting. `free` memory blízka nule môže byť zdravá, ak je väčšina RAM reclaimable cache. Problém vzniká pri sustained pressure, vysokých major faults, reclaim/compaction cost, swap thrash alebo OOM decisione.

```text
user symptom
→ task/cgroup/host scope
→ utilization, saturation a pressure
→ scheduler alebo memory-state hypothesis
→ discriminating observation
→ bounded change
→ latency/throughput a forbidden-outcome validation
```

Výkonová diagnóza preto nevyvodzuje root cause z jednej vysokej hodnoty. Musí zistiť effective quota/limit, workload concurrency, run-queue alebo allocation path a následne preukázať, že náprava zlepšila user outcome bez presunutia bottlenecku.""",
    "linux-networking.md": """Linux networking prepája application socket s namespace-local interfaces, addresses, routes, neighbor cache, netfilter hooks, qdisc a device driverom. DNS resolution, TCP connect a application protocol sú samostatné transitions; úspech jedného nepreukazuje ďalší.

```text
name resolution
→ destination address
→ socket bind/connect
→ route a source-address selection
→ firewall/NAT hooks
→ neighbor resolution
→ interface/qdisc/driver
→ remote path
→ transport a application response
```

`ping` používa ICMP a nemusí testovať rovnakú policy ani port ako application. `ss` ukazuje local socket state, `ip route get` kernelový routing decision a packet capture observation point, nie automaticky end-to-end truth. Namespaces, policy routing, reverse-path filtering, conntrack a NAT môžu spôsobiť asymetriu. Systematický troubleshooting ide od exact flow tuple a namespace cez route/socket/firewall evidence až po remote listener a application semantics.""",
    "ssh.md": """SSH vytvára šifrovaný a autentifikovaný transport medzi clientom a serverom, ale kombinuje viac oddelených trust decisions. Client najprv overuje host identity, následne strany dohodnú algorithms a session keys, server overí user alebo workload identity a až potom vznikajú channels pre shell, command, forwarding alebo subsystem.

```text
TCP connection
→ protocol a key exchange
→ server host-key verification
→ user authentication
→ authorization a session setup
→ channel operation
```

Private user key nie je heslo posielané serveru; client podpisuje challenge a server overuje public key podľa `authorized_keys`, certificate authority alebo iného backendu. Ak client slepo prijme zmenený host key, encryption stále funguje, ale môže byť ukončená u útočníka. Bastion a agent forwarding pridávajú ďalšie trust boundaries. Bezpečné overenie preto zahŕňa known-host policy, key scope/rotation, server-side restrictions, effective sshd configuration a command/channel behavior.""",
    "cron-and-systemd-timers.md": """Scheduler neurčuje iba čas spustenia; vytvára opakovaný lifecycle operácie s environmentom, identity, concurrency a failure semantics. Cron spustí command podľa kalendárneho matchu v obmedzenom environment-e. systemd timer aktivuje unit a môže použiť monotonic triggers, persistence po missed run-e a service-manager observability.

```text
schedule generation
→ trigger eligibility
→ process identity a environment
→ lock alebo concurrency decision
→ idempotent operation
→ durable output/checkpoint
→ exit a runtime evidence
→ retry, alert alebo next run
```

Úspešný scheduler trigger nepreukazuje úspech jobu a úspešný exit nemusí preukazovať expected business effect. Overlap dvoch behov môže poškodiť state; missed run po vypnutom hoste môže zostať navždy neuskutočnený; retry po lost response môže duplikovať external action. Robustný scheduled job potrebuje locking, stable operation identity, bounded timeout, atomic output, logging/metrics a druhý-run convergence test.""",
    "namespaces.md": """Linux namespace mení pohľad procesu na vybraný kernel resource. PID, mount, network, UTS, IPC, user, cgroup a time namespaces nevirtualizujú celý kernel; vytvárajú samostatné identity alebo lookup contexts nad zdieľanými kernel subsystems.

```text
process
→ namespace membership per resource type
→ namespace-specific lookup a identity
→ shared kernel enforcement
→ host alebo peer namespace boundary
```

Process môže mať PID `1` vo svojom namespace a iný PID na hoste, vidieť vlastné mounty a interfaces, no stále používa ten istý kernel. User namespace môže mapovať namespace root na neprivilegované host UID, ale capabilities platia iba voči resources v zodpovedajúcom user-namespace scope-e. Namespace preto nie je kompletná security boundary. Potrebuje cgroups, capabilities, seccomp, LSM, filesystem a device controls a pri silnejšom threat modeli aj VM isolation.""",
    "cgroups.md": """Control groups organizujú processes do hierarchie pre resource accounting, limits, prioritization a pressure control. V cgroup v2 má každý process jedno miesto v unified hierarchy a controllers distribuujú CPU, memory, I/O a PIDs policy cez parent-child boundaries.

```text
service/container identity
→ cgroup placement
→ inherited a local controller configuration
→ effective quota/weight/limit
→ runtime consumption a pressure
→ throttle, reclaim, OOM alebo admission failure
```

Configured hodnota nie je automaticky effective capacity. CPU quota sa interpretuje spolu s periodou a konkurenciou, memory limit spolu s page cache, swap a reclaim a I/O control závisí od device mappingu. Host môže mať voľné resources, kým workload je lokálne throttled alebo dostane cgroup OOM. Diagnostika preto číta `/proc/<pid>/cgroup`, effective files v `cgroup.controllers` hierarchy, pressure stall information a workload outcome namiesto iba host-wide utilization.""",
    "linux-capabilities.md": """Linux capabilities rozdeľujú tradičné root privileges na jemnejšie operation classes, napríklad bind na privileged port, zmenu network configuration alebo obídenie vybraných DAC checks. Capability nie je role priradená userovi navždy; kernel vyhodnocuje capability sets konkrétneho threadu pri konkrétnej operácii.

Process pracuje s permitted, effective, inheritable, bounding a ambient sets. Pri `execve()` sa nové sets vypočítajú z parent state-u, file capabilities, bounding setu, `no_new_privs` a user-namespace contextu. Container configuration typu `cap_add` preto ešte nepreukazuje, že capability je effective v bežiacom procese ani že pôsobí voči host resource.

Least privilege znamená identifikovať konkrétny kernel check a ponechať iba potrebnú capability v správnom scope-e. Pridanie `CAP_SYS_ADMIN` alebo `privileged` často skryje skutočný denial a výrazne rozšíri attack surface. Overenie musí zahŕňať allowed operation, forbidden adjacent operation, effective sets po exec a MAC/seccomp boundary.""",
    "selinux-and-apparmor.md": """SELinux a AppArmor sú Linux Security Modules poskytujúce Mandatory Access Control nad rámec klasického DAC. Kernel najprv vyhodnotí bežné identity a permissions a následne LSM policy pre subject, object, operation a context. Root alebo capability preto nemusia obísť MAC denial.

SELinux používa labels a type-enforcement rules; AppArmor primárne viaže profile na executable a path-oriented access. Obe platformy majú policy generation, loaded kernel state, enforcement mode a audit evidence. Súbor s opravenými Unix mode bits môže byť stále blokovaný nesprávnym SELinux type-om alebo AppArmor profile transitionom.

Bezpečný troubleshooting zachová denial evidence, identifikuje exact process/object/action a opraví label, transition alebo policy pri správnej boundary. Vypnutie enforcementu alebo broad allow rule iba potvrdí, že MAC vrstva mala vplyv; nepreukazuje správnu least-privilege nápravu. Acceptance testuje pôvodný povolený flow aj zakázaný susedný flow po reload/restart generation.""",
    "performance-and-troubleshooting.md": """Performance troubleshooting je evidence-driven proces premeny používateľského symptómu na testovateľnú príčinu. Začína presným outcome-om, časovým oknom a affected cohortou, nie príkazom `top`. Každý nástroj pozoruje iba jednu vrstvu a jeho hodnota musí byť interpretovaná voči workloadu, limits a dependencies.

```text
user-visible symptom
→ exact scope, timeline a baseline
→ request/process/resource/data path
→ competing hypotheses
→ discriminating observation
→ evidence-preserving containment
→ authoritative repair
→ original, forbidden a adjacent-scenario validation
```

Vysoké CPU môže byť expected productive work, runaway loop, spinlock alebo consequence retry stormu. Nízke CPU môže sprevádzať lock contention, storage latency, network timeout alebo cgroup throttling. Memory growth môže byť cache, leak alebo backlog. Preto sa najprv oddeľuje utilization od saturation, host od cgroup scope-u a correlation od causality.

Náprava nie je uzavretá poklesom jednej metriky. Musí zlepšiť latency, throughput alebo completion outcome, zachovať correctness a overiť druhú load alebo failure situáciu. Inak sa bottleneck iba presunie alebo sa symptóm potlačí bez odstránenia mechanizmu.""",
}


def remove_legacy_metadata(text: str, path: Path) -> str:
    if "## Metadata" not in text:
        return text

    pattern = re.compile(
        r"\A(?P<title># [^\n]+\n)\n## Metadata\n.*?(?=\n## (?:1\.|[^\n]+))",
        re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise RuntimeError(f"Unable to locate metadata block in {path}")

    return match.group("title") + "\n" + text[match.end() :].lstrip("\n")


def insert_opening(path: Path, opening: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = remove_legacy_metadata(text, path)
    title, separator, remainder = text.partition("\n")
    if not separator:
        raise RuntimeError(f"Missing body in {path}")
    if opening in remainder:
        return

    path.write_text(
        f"{title}\n\n{opening.strip()}\n\n{remainder.lstrip()}".rstrip() + "\n",
        encoding="utf-8",
    )


def update_section_readme() -> None:
    path = SECTION / "README.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("## Odporúčané poradie", "## Authoritative poradie")

    status_pattern = re.compile(
        r"\n## Stav\n\n\| Téma \| Status \| Úroveň \|\n\|---\|---\|---\|\n(?:\|.*\|\n?)+",
        re.MULTILINE,
    )
    text, count = status_pattern.subn("\n", text)
    if count != 1:
        raise RuntimeError(f"Expected one legacy status table in {path}, found {count}")

    marker = "## Cieľ zvládnutia"
    if marker not in text:
        raise RuntimeError(f"Missing mastery marker in {path}")

    explanation = """## Spôsob spracovania sekcie

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

"""
    if "## Spôsob spracovania sekcie" not in text:
        text = text.replace(marker, explanation + marker, 1)

    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def update_review_ledger() -> None:
    path = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
    text = path.read_text(encoding="utf-8")
    replacement = (
        "| `01-linux-and-systems` — Linux and Systems | 19/19 integrated prose and explanation-depth revalidation | "
        "Ready for user review | 2026-08-01 | Všetkých 19 authoritative kapitol už nepoužíva legacy `Metadata`, "
        "`Status: Learning`, `Úroveň: L2` ani section-level Learning/L2 tabuľku. Každá kapitola začína priamo "
        "subject-specific prose vysvetlením kernel alebo user-space boundary, owned state-u, internal pathu, evidence "
        "boundary a failure consequence. Sekcia drží jeden runtime chain od system callov, task lifecycle-u, pathname/inode "
        "a process credentials cez Bash execution, environment snapshots, systemd jobs, package transactions, journal "
        "delivery a layered storage až po CPU/memory pressure, packet path, SSH trust, scheduled-operation semantics, "
        "namespaces, cgroup v2, capability execve transformáciu, SELinux/AppArmor MAC a evidence-driven performance "
        "troubleshooting. Existujúce command walkthroughy, worked failures a recovery modely zostali zachované; nový výklad "
        "explicitne oddeľuje requested/configured/loaded/effective/runtime/user states a vysvetľuje, čo command output "
        "preukazuje a čo nie. README ordering, navigation, glossary a full documentation audit boli synchronizované. "
        "Sekcia je pripravená na používateľskú kontrolu, nie automaticky Accepted, Verified ani Stable. |"
    )

    pattern = re.compile(r"^\| `01-linux-and-systems`.*$", re.MULTILINE)
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"Expected one Section 01 ledger row in {path}, found {count}")

    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def validate() -> None:
    expected = set(OPENINGS)
    actual = {path.name for path in SECTION.glob("*.md") if path.name != "README.md"}
    if actual != expected:
        raise RuntimeError(
            f"Section 01 inventory mismatch; missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
        )

    forbidden = ("## Metadata", "Status: Learning", "Úroveň: L2")
    for name, opening in OPENINGS.items():
        text = (SECTION / name).read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                raise RuntimeError(f"Legacy token {token!r} remains in {name}")
        if opening not in text:
            raise RuntimeError(f"Integrated opening missing in {name}")

    readme = (SECTION / "README.md").read_text(encoding="utf-8")
    if "## Stav" in readme or "| Learning | L2 |" in readme:
        raise RuntimeError("Legacy Section 01 status table remains")
    if "## Spôsob spracovania sekcie" not in readme:
        raise RuntimeError("Section 01 README explanation standard missing")


def main() -> None:
    for name, opening in OPENINGS.items():
        insert_opening(SECTION / name, opening)

    update_section_readme()
    update_review_ledger()
    validate()


if __name__ == "__main__":
    main()
