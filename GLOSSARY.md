# Glossary

Rýchly referenčný index technických pojmov používaných v Knowledge Hube. Glossary nenahrádza plné kapitoly: každé heslo obsahuje stručnú definíciu a podľa možnosti odkaz na autoritatívny článok s mechanizmom, príkladmi a troubleshooting kontextom.

## ACL — Access Control List

Rozšírený model oprávnení, ktorý umožňuje priradiť práva ďalším používateľom alebo skupinám nad rámec základných owner/group/other mode bits. Pozri [Users, groups, permissions, sudo a PAM](docs/01-linux-and-systems/users-groups-permissions-sudo-pam.md).

## ARP — Address Resolution Protocol

IPv4 protokol, ktorým host v lokálnom linku zisťuje link-layer adresu zodpovedajúcu next-hop IP adrese. Pozri [Linux networking](docs/01-linux-and-systems/linux-networking.md).

## Artifact

Nemenný alebo jednoznačne identifikovateľný výstup build procesu určený na testovanie, distribúciu alebo deployment, napríklad binárny súbor, balík, container image alebo Helm chart. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Automation

Prevod opakovateľného postupu na deterministický, auditovateľný a opakovane vykonateľný mechanizmus. Dobrá automatizácia odstraňuje variabilitu; nemá iba zrýchliť nepochopený proces. Pozri [Automation Mindset](docs/00-foundations/automation-mindset.md).

## Batch size

Množstvo zmien spracovaných alebo nasadených naraz. Menšie batches znižujú blast radius, skracujú spätnú väzbu a uľahčujú diagnostiku. Pozri [Three Ways of DevOps](docs/00-foundations/three-ways.md).

## Block device

Kernelové zariadenie poskytujúce blokovo adresovaný storage, napríklad disk, partition, LVM logical volume alebo virtualizovaný cloud volume. Pozri [Storage, mounty a filesystems](docs/01-linux-and-systems/storage-mounts-and-filesystems.md).

## Build

Proces, ktorý transformuje zdrojové vstupy na spustiteľný alebo distribuovateľný artifact. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## CALMS

Rámec DevOps schopností: Culture, Automation, Lean, Measurement a Sharing. Slúži na posúdenie, či transformácia rieši celý socio-technický systém, nie iba nástroje. Pozri [CALMS framework](docs/00-foundations/calms.md).

## Capability — Linux capability

Jemnejšie rozdelená časť tradičných root oprávnení, napríklad `CAP_NET_BIND_SERVICE`. Umožňuje udeliť procesu konkrétnu privilegovanú schopnosť bez plného root prístupu. Pozri [Users, groups, permissions, sudo a PAM](docs/01-linux-and-systems/users-groups-permissions-sudo-pam.md).

## cgroup — Control group

Kernel mechanizmus na zoskupovanie procesov a riadenie alebo meranie ich CPU, memory a I/O zdrojov. systemd používa cgroups na sledovanie celého stromu procesov služby. Pozri [systemd, services a daemons](docs/01-linux-and-systems/systemd-services-daemons.md).

## Change fail rate

Podiel deploymentov, ktoré spôsobia degradáciu služby a vyžadujú nápravu. Je jednou z DORA instability metrík. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Change lead time

Čas od vzniku sledovanej zmeny, často od commitu, po jej úspešný deployment do produkcie. Definícia začiatku a konca musí byť v organizácii konzistentná. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Context switch

Prechod CPU z vykonávania jedného threadu na iný vrátane uloženia a obnovenia execution contextu. Veľký počet switchov môže byť normálny, ale aj indikovať lock contention alebo nadmerný počet threadov. Pozri [CPU and Memory Fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Controller

Komponent, ktorý pozoruje aktuálny stav, porovnáva ho s desired state a vykonáva korekčné akcie. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## Cron

Časový scheduler, ktorý podľa crontab pravidiel spúšťa príkazy v neinteraktívnom a typicky minimálnom prostredí. Pozri [Cron a systemd timers](docs/01-linux-and-systems/cron-and-systemd-timers.md).

## Daemon

Dlhšie bežiaci proces poskytujúci systémovú alebo aplikačnú službu bez priamej interaktívnej session. V modernom systemd modeli typicky beží vo foregrounde a jeho lifecycle riadi service manager. Pozri [systemd, services a daemons](docs/01-linux-and-systems/systemd-services-daemons.md).

## Declarative configuration

Konfigurácia opisujúca požadovaný výsledný stav systému, nie presnú sekvenciu krokov potrebných na jeho dosiahnutie. Pozri [Declarative vs. Imperative Approach](docs/00-foundations/declarative-vs-imperative.md).

## Deployment

Technická operácia umiestnenia konkrétnej verzie aplikácie alebo konfigurácie do cieľového prostredia. Deployment nie je automaticky release. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Deployment frequency

Ako často služba úspešne nasadzuje zmeny do produkcie. Je jednou z DORA throughput metrík. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Deployment rework rate

Podiel deploymentov, ktoré sú neplánovanou opravou predchádzajúceho deploymentu. Je jednou z aktuálnych DORA instability metrík. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Desired state

Požadovaný stav systému deklarovaný používateľom alebo automatizačným nástrojom. Controller ho porovnáva s aktuálnym stavom a vykonáva korekcie. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## DevOps

Súbor kultúrnych princípov, organizačných praktík a technických mechanizmov na rýchle, bezpečné a opakovateľné dodávanie zmien s krátkou spätnou väzbou. Pozri [DevOps](docs/00-foundations/devops.md).

## DNS — Domain Name System

Distribuovaný systém mapujúci mená na resource records, napríklad IP adresy. Úspešné DNS resolution samo osebe nedokazuje network ani application dostupnosť. Pozri [Linux networking](docs/01-linux-and-systems/linux-networking.md).

## DORA metrics

Metriky software delivery performance sledujúce throughput a instability delivery systému. Aktuálny model zahŕňa change lead time, deployment frequency, failed deployment recovery time, change fail rate a deployment rework rate. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Drift

Rozdiel medzi deklarovaným alebo evidovaným stavom a skutočným stavom systému, často spôsobený manuálnymi zmenami mimo riadeného procesu. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## Environment variable

Pomenovaná hodnota odovzdaná procesu v jeho environment bloku. Environment sa typicky dedí pri vytvorení procesu, ale nie je globálnou databázou systému. Pozri [Environment variables](docs/01-linux-and-systems/environment-variables.md).

## Exit status

Číselný výsledok ukončeného procesu alebo shell príkazu. Hodnota `0` typicky znamená úspech; nenulová hodnota reprezentuje chybu alebo iný stav definovaný programom. Pozri [Shell, Bash, pipes, redirection a exit codes](docs/01-linux-and-systems/shell-bash-pipes-redirection-exit-codes.md).

## Failed deployment recovery time

Čas potrebný na obnovenie služby po zlyhaní spôsobenom deploymentom. Je jednou z aktuálnych DORA throughput metrík. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Feedback loop

Cesta od vykonanej zmeny k informácii o jej výsledku. Kratší loop znižuje množstvo práce postavenej na nesprávnom predpoklade. Pozri [Feedback Loops](docs/00-foundations/feedback-loops.md).

## File descriptor

Malé celé číslo v procese odkazujúce na kernelom spravovaný otvorený objekt, napríklad súbor, pipe, socket alebo device. Štandardné deskriptory sú stdin `0`, stdout `1` a stderr `2`. Pozri [Shell, Bash, pipes, redirection a exit codes](docs/01-linux-and-systems/shell-bash-pipes-redirection-exit-codes.md).

## Filesystem

Štruktúra a pravidlá, ktorými operačný systém mapuje pathname na metadata a dátové bloky. Filesystem je pripojený do spoločného stromu cez mount point. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## Hard link

Ďalší directory entry odkazujúci na ten istý inode. Nie je to odkaz na názov súboru; oba názvy sú rovnocenné odkazy na ten istý objekt. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## Host key — SSH host key

Dlhodobý kryptografický kľúč, ktorým SSH server preukazuje svoju identitu klientovi. Klient si dôveryhodný fingerprint alebo public key eviduje v `known_hosts`. Pozri [SSH](docs/01-linux-and-systems/ssh.md).

## Idempotencia

Vlastnosť operácie, pri ktorej opakované vykonanie s rovnakým vstupom vedie k rovnakému výslednému stavu bez neželaných vedľajších účinkov. Pozri [Idempotency](docs/00-foundations/idempotency.md).

## Immutable infrastructure

Prevádzkový model, v ktorom sa existujúce inštancie zásadne neupravujú. Nová verzia sa nasadí vytvorením nových inštancií a nahradením starých. Pozri [Immutable vs. Mutable Infrastructure](docs/00-foundations/immutable-vs-mutable-infrastructure.md).

## Imperative approach

Prístup opisujúci konkrétnu sekvenciu krokov, ktoré sa majú vykonať. Je vhodný na procedurálne operácie, ale môže byť citlivejší na počiatočný stav a poradie. Pozri [Declarative vs. Imperative Approach](docs/00-foundations/declarative-vs-imperative.md).

## Inode

Filesystem objekt obsahujúci metadata a odkazy na dátové bloky. Názov súboru je uložený v directory entry, nie v inode. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## journald

Systémová logging služba systemd, ktorá prijíma štruktúrované záznamy zo služieb, kernelu a ďalších zdrojov a sprístupňuje ich cez `journalctl`. Pozri [journald a logging](docs/01-linux-and-systems/journald-and-logging.md).

## Kernel space

Privilegovaná časť systému, v ktorej beží kernel a spravuje procesy, memory, devices, filesystems a networking. Pozri [Kernel a user space](docs/01-linux-and-systems/kernel-and-user-space.md).

## Load average

Priemerný počet tasks, ktoré sú runnable alebo v určitom uninterruptible sleep. Nie je to percento CPU a interpretuje sa voči počtu CPUs a charakteru čakania. Pozri [CPU and Memory Fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Mount

Operácia pripojenia filesystemu alebo iného mountable objektu do konkrétneho bodu spoločného filesystem stromu. Pozri [Storage, mounty a filesystems](docs/01-linux-and-systems/storage-mounts-and-filesystems.md).

## MTU — Maximum Transmission Unit

Maximálna veľkosť L3 paketu, ktorú interface prenesie bez fragmentácie. Nesúlad MTU môže spôsobiť, že malé prenosy fungujú a väčšie timeoutujú. Pozri [Linux networking](docs/01-linux-and-systems/linux-networking.md).

## Mutable infrastructure

Model, v ktorom sa existujúce stroje alebo inštancie priebežne aktualizujú a menia na mieste. Je flexibilný, ale zvyšuje riziko driftu a historických rozdielov. Pozri [Immutable vs. Mutable Infrastructure](docs/00-foundations/immutable-vs-mutable-infrastructure.md).

## NDP — Neighbor Discovery Protocol

IPv6 mechanizmus na neighbor discovery, router discovery a ďalšie lokálne linkové funkcie. Pozri [Linux networking](docs/01-linux-and-systems/linux-networking.md).

## OOM killer

Kernel mechanizmus poslednej možnosti, ktorý pri nedostatku memory vyberie proces na ukončenie. Je reakciou na memory exhaustion, nie automaticky jeho root cause. Pozri [CPU and Memory Fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Package manager

Nástroj, ktorý rieši inštaláciu, upgrade a odstránenie balíkov vrátane závislostí, verifikačných metadata a evidencie vlastníctva súborov. Pozri [Package management](docs/01-linux-and-systems/package-management.md).

## Page cache

RAM používaná kernelom na cache file-backed dát. Znižuje storage I/O a je reclaimable pri memory pressure, preto vysoká cache nie je automaticky problém. Pozri [CPU and Memory Fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Page fault

Udalosť, pri ktorej požadované virtuálne mapovanie nie je okamžite dostupné. Minor fault nevyžaduje storage I/O; major fault typicky áno. Pozri [CPU and Memory Fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## PAM — Pluggable Authentication Modules

Framework, cez ktorý služby skladajú autentifikačné, account, session a password politiky z modulov. Pozri [Users, groups, permissions, sudo a PAM](docs/01-linux-and-systems/users-groups-permissions-sudo-pam.md).

## PID — Process Identifier

Číselný identifikátor procesu v konkrétnom PID namespace. PID sa môže po ukončení procesu znovu použiť. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## Process

Bežiaca inštancia programu s vlastným adresným priestorom, file descriptormi, credentials, environmentom a ďalším kernel stavom. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## PSI — Pressure Stall Information

Linux metriky vyjadrujúce čas, počas ktorého tasks čakali pre nedostupnosť CPU, memory alebo I/O kapacity. Merajú dopad resource pressure, nie iba utilization. Pozri [CPU and Memory Fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## PSS — Proportional Set Size

Odhad memory procesu, pri ktorom sa zdieľané pages pomerne rozdelia medzi procesy. Je vhodnejší na atribúciu než jednoduché sčítanie RSS. Pozri [CPU and Memory Fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Reconciliation

Opakovaný proces porovnávania desired state so skutočným stavom a vykonávania krokov, ktoré odchýlku zmenšujú. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## Release

Produktové alebo procesné rozhodnutie sprístupniť konkrétnu funkcionalitu používateľom. Release môže byť oddelený od deploymentu napríklad feature flagom. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Rollback

Návrat k predchádzajúcej verzii aplikácie alebo konfigurácie. Nemusí byť bezpečný po nekompatibilnej zmene dát alebo externého kontraktu. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Roll-forward

Náprava zlyhania nasadením novej opravnej verzie namiesto návratu na starú verziu. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Route

Pravidlo určujúce next hop, interface a ďalšie parametre pre packet smerujúci do destination prefixu. Kernel typicky vyberá najšpecifickejšiu zodpovedajúcu route. Pozri [Linux networking](docs/01-linux-and-systems/linux-networking.md).

## RSS — Resident Set Size

Množstvo pages procesu aktuálne resident v RAM. Zdieľané pages sa pri jednoduchom sčítaní RSS môžu započítať viackrát. Pozri [CPU and Memory Fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## SDLC — Software Development Life Cycle

Riadený životný cyklus softvéru od vzniku potreby cez návrh, implementáciu, testovanie, delivery a prevádzku až po vyradenie. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Shell

Program, ktorý interpretuje príkazový jazyk, vykonáva expanziu, redirection, pipelines a spúšťa ďalšie procesy. Pozri [Shell, Bash, pipes, redirection a exit codes](docs/01-linux-and-systems/shell-bash-pipes-redirection-exit-codes.md).

## Signal

Asynchrónna notifikácia doručená procesu alebo threadu, napríklad `SIGTERM`, `SIGINT` alebo `SIGKILL`. Niektoré signály možno zachytiť alebo ignorovať; `SIGKILL` a `SIGSTOP` nie. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## Socket

Kernel endpoint komunikácie sprístupnený procesu cez file descriptor. Môže reprezentovať listening endpoint, established connection alebo connectionless komunikáciu. Pozri [Linux networking](docs/01-linux-and-systems/linux-networking.md).

## SSH agent

Proces, ktorý drží odomknuté private keys v pamäti a vykonáva podpisové operácie pre SSH klienta bez odovzdania private key aplikácii. Pozri [SSH](docs/01-linux-and-systems/ssh.md).

## Swap

Storage-backed priestor, do ktorého môže kernel presunúť niektoré anonymné memory pages. Samotné použitie swapu nie je incident; problémom je aktívne thrashing a vysoká latency. Pozri [CPU and Memory Fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Symbolic link

Samostatný filesystem objekt obsahujúci textovú cestu na iný objekt. Na rozdiel od hard linku môže smerovať cez filesystems a môže zostať dangling. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## system call

Kontrolovaný prechod z user space do kernel space, ktorým proces žiada kernel o operáciu, napríklad otvorenie súboru, vytvorenie procesu alebo sieťovú komunikáciu. Pozri [Kernel a user space](docs/01-linux-and-systems/kernel-and-user-space.md).

## systemd timer

`.timer` unit, ktorá podľa kalendárneho alebo monotonic pravidla aktivuje inú unit, najčastejšie `.service`. Pozri [Cron a systemd timers](docs/01-linux-and-systems/cron-and-systemd-timers.md).

## systemd unit

Deklaratívny objekt spravovaný systemd, napríklad `.service`, `.socket`, `.timer`, `.mount` alebo `.target`. Unit nie je to isté ako jeden proces. Pozri [systemd, services a daemons](docs/01-linux-and-systems/systemd-services-daemons.md).

## TCP state

Stav TCP socketu v connection lifecycle, napríklad `LISTEN`, `SYN-SENT`, `ESTAB`, `CLOSE-WAIT` alebo `TIME-WAIT`. Pozri [Linux networking](docs/01-linux-and-systems/linux-networking.md).

## Thread

Plánovateľná vykonávacia jednotka v rámci procesu. Thready typicky zdieľajú adresný priestor a file descriptory, ale majú vlastný stack a execution context. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## Toil

Manuálna, opakujúca sa, automatizovateľná a nízko hodnotná prevádzková práca, ktorá rastie spolu so systémom. Pozri [Toil and Technical Debt](docs/00-foundations/toil-and-technical-debt.md).

## T-shaped engineer

Inžinier so širokou orientáciou naprieč viacerými oblasťami a hlbokou expertízou aspoň v jednej z nich. Pozri [T-shaped engineer](docs/00-foundations/t-shaped-engineer.md).

## User space

Menej privilegované prostredie, v ktorom bežia aplikácie a systémové procesy. Prístup ku kernel resources vykonávajú cez system calls. Pozri [Kernel a user space](docs/01-linux-and-systems/kernel-and-user-space.md).

## Value stream

Celý tok práce a informácií od potreby po hodnotu doručenú používateľovi vrátane čakania, handoffov, kontrol a prevádzky. Pozri [Value Stream Mapping](docs/00-foundations/value-stream-mapping.md).

## Virtual memory

Abstrakcia, pri ktorej má proces vlastný virtuálny adresný priestor a kernel mapuje jeho pages na fyzickú RAM, file-backed data, swap alebo neprítomné mapovania. Pozri [CPU and Memory Fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## VSZ — Virtual Set Size

Veľkosť virtuálneho adresného priestoru procesu. Zahŕňa aj rezervované a mapované oblasti, ktoré nemusia byť resident v RAM. Pozri [CPU and Memory Fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Zombie process

Ukončený proces, ktorého exit status ešte parent proces neprevzal cez `wait`. Nevykonáva kód, ale zaberá položku v process table. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).
