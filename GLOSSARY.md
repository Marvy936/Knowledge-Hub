# Glossary

Rýchly referenčný index technických pojmov používaných v Knowledge Hube. Glossary nenahrádza plné kapitoly: každé heslo obsahuje stručnú definíciu a odkaz na autoritatívny článok, ak už existuje.

## ACL — Access Control List

Rozšírený model oprávnení nad rámec owner/group/other mode bits. Pozri [Users, groups, permissions, sudo a PAM](docs/01-linux-and-systems/users-groups-permissions-sudo-pam.md).

## Advanced function — PowerShell

PowerShell function s `[CmdletBinding()]`, common parameters, parameter binding a cmdlet-like error/output správaním. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Alias — YAML

YAML referencia na node označený anchorom. Znižuje duplicitu, ale môže komplikovať tooling a čitateľnosť. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## ALPN — Application-Layer Protocol Negotiation

TLS extension, ktorou klient a server počas handshake dohodnú aplikačný protokol, napríklad `http/1.1` alebo `h2`. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Ambient capability

Linux capability, ktorú môže proces za presných podmienok zachovať pri `execve()` neprivilegovaného programu. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Anchor — YAML

YAML mechanizmus pomenovania node, na ktorý môže odkazovať alias. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Annotated tag

Git tag reprezentovaný samostatným tag objectom s targetom, taggerom, časom, message a voliteľným kryptografickým podpisom. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Anycast

Routing model, v ktorom viac lokalít oznamuje rovnakú IP adresu a routing privedie klienta k topologicky preferovanému endpointu. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## AppArmor profile

Mandatory Access Control profil definujúci povolené paths, execute transitions, capabilities, network operations a ďalšie správanie programu. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## ARP — Address Resolution Protocol

IPv4 protokol mapujúci lokálnu next-hop IP adresu na MAC adresu. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Artifact

Jednoznačne identifikovateľný výstup build procesu určený na testovanie alebo distribúciu. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Asymmetric routing

Stav, keď forward a return traffic rovnakého flow používajú rozdielne network paths. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Asyncio

Python framework pre cooperative asynchronous I/O založený na event loop-e, coroutines a tasks. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Atomic write

Zápis cez dočasný súbor, validáciu a atomický rename/replace tak, aby consumer nevidel čiastočný obsah. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md) a [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Automation

Prevod opakovateľného postupu na deterministický, auditovateľný a opakovane vykonateľný mechanizmus. Pozri [Automation Mindset](docs/00-foundations/automation-mindset.md).

## AVC — Access Vector Cache

SELinux decision a auditný kontext opisujúci povolenie alebo zamietnutie operácie medzi source a target security contexts. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Backoff

Časová stratégia medzi opakovanými pokusmi, často exponenciálne rastúca a doplnená jitterom. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Backport

Prenesenie opravy alebo zmeny z novšej vývojovej línie do staršej podporovanej release branch, často pomocou cherry-picku a samostatnej validácie. Pozri [Cherry-pick a stash](docs/03-git-and-automation/cherry-pick-and-stash.md).

## Backpressure

Mechanizmus, ktorým pomalší consumer obmedzí alebo signalizuje producerovi, aby nevytváral neobmedzený buffer a rastúcu latency. Pozri [REST APIs a WebSockets](docs/02-networking-and-web/rest-apis-and-websockets.md).

## Bare repository

Git repository bez working tree, používaný typicky ako serverový alebo integračný endpoint. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Batch size

Množstvo zmien spracovaných alebo nasadených naraz. Menšie batches znižujú blast radius a skracujú feedback. Pozri [Three Ways of DevOps](docs/00-foundations/three-ways.md).

## Blob — Git object

Nemenný Git object obsahujúci bytes jedného súboru bez filename a path metadata. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Block device

Kernelové zariadenie poskytujúce blokovo adresovaný storage. Pozri [Storage, mounty a filesystems](docs/01-linux-and-systems/storage-mounts-and-filesystems.md).

## Bounding set — capability bounding set

Horná hranica Linux capabilities, ktoré proces a jeho potomkovia môžu získať. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Branch — Git branch

Pohyblivý ref pod `refs/heads/`, ktorý ukazuje na tip commit. Branch nie je samostatný kontajner súborov ani commitov. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Branch protection

Serverová policy obmedzujúca aktualizáciu dôležitej branch pomocou controls ako required reviews, CI checks, zákaz force pushu alebo merge queue. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## Broadcast domain

L2 oblasť, v ktorej sa šíri Ethernet broadcast. Typicky ju oddeľuje router alebo VLAN boundary. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Build

Proces transformujúci zdrojové vstupy na spustiteľný alebo distribuovateľný artifact. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Cache-Control

HTTP response/request header definujúci freshness, revalidation, storage a shared/private cache policy. Pozri [HTTP](docs/02-networking-and-web/http.md).

## CALMS

DevOps rámec Culture, Automation, Lean, Measurement a Sharing. Pozri [CALMS framework](docs/00-foundations/calms.md).

## Capability — Linux capability

Samostatná časť tradičných root oprávnení, napríklad `CAP_NET_BIND_SERVICE`. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Capturing group — regex

Časť regular expression uzavretá v zátvorkách, ktorá zachytáva matched substring pre ďalšie spracovanie. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Catastrophic backtracking

Patologické správanie backtracking regex engine-u, pri ktorom ambiguous nested pattern spôsobí extrémny čas spracovania non-matching vstupu. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Certificate

X.509 objekt viažuci public key na identity claims, validity interval, usage a issuer signature. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Certificate chain

Postupnosť leaf a intermediate certificates, ktorú klient overuje smerom k dôveryhodnému root CA v trust store. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## cgroup — Control group

Kernel mechanizmus na hierarchické zoskupovanie procesov a riadenie ich CPU, memory, I/O a process-count resources. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## cgroup v2

Unified cgroup hierarchy s konzistentnejším modelom controllerov a delegácie než cgroup v1. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## Change fail rate

Podiel deploymentov, ktoré spôsobia degradáciu služby a vyžadujú nápravu. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Change lead time

Čas od vzniku sledovanej zmeny po jej úspešný deployment do produkcie. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Cherry-pick

Operácia, ktorá aplikuje zmenu vybraného commitu na aktuálny tip a vytvorí nový commit s novým parentom a object ID. Pozri [Cherry-pick a stash](docs/03-git-and-automation/cherry-pick-and-stash.md).

## CIDR — Classless Inter-Domain Routing

Zápis IP prefixu pomocou adresy a počtu network bitov, napríklad `192.0.2.0/24`. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## `CLOSE-WAIT`

TCP state, v ktorom remote peer poslal FIN, ale lokálna aplikácia ešte nezavrela socket. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Cmdlet

PowerShell command implementovaný podľa jednotného Verb-Noun, parameter binding, object pipeline a error-stream modelu. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Collision domain

Oblasť zdieľaného Ethernet média, v ktorej môžu transmissions kolidovať. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Command injection

Zraniteľnosť, pri ktorej neoverený vstup zmení syntax alebo spustí dodatočný príkaz. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md) a [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Commit object

Git object obsahujúci root tree snapshotu, parent commits, author/committer metadata a commit message. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Complain mode

AppArmor režim, v ktorom sa porušenia profilu logujú, ale neblokujú. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Congestion control

Transportný mechanizmus upravujúci množstvo dát in flight podľa odhadovanej kapacity a congestion signálov network pathu. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Connection draining

Postup, pri ktorom sa backendu prestane posielať nový traffic, ale existujúce requests alebo connections dostanú čas na dokončenie. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Conntrack

State table sledujúca network flows pre stateful firewall a NAT rozhodnutia. Pozri [NAT](docs/02-networking-and-web/nat.md) a [Firewally](docs/02-networking-and-web/firewalls.md).

## Consistent hashing

Hashing model minimalizujúci množstvo remapovaných keys pri pridaní alebo odstránení backendu. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Content-addressable storage

Storage model, v ktorom je identita objektu odvodená z jeho typu a obsahu. Git používa tento model pre blobs, trees, commits a tags. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Content negotiation

HTTP mechanizmus, ktorým klient deklaruje preferované representations a server vyberie formát, jazyk alebo encoding. Pozri [HTTP](docs/02-networking-and-web/http.md).

## Context manager — Python

Objekt alebo generator riadiaci vstup a výstup z lifecycle scope, napríklad otvorenie a bezpečné zatvorenie súboru, locku alebo session. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Context switch

Prechod CPU z vykonávania jedného threadu na iný. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Control plane

Časť systému vytvárajúca stav, podľa ktorého data plane rozhoduje. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## Controller

Komponent porovnávajúci desired state s aktuálnym stavom a vykonávajúci korekčné akcie. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## Cookie

HTTP state token, ktorý server nastaví cez `Set-Cookie` a klient následne posiela podľa domain, path, security a SameSite scope. Pozri [HTTP](docs/02-networking-and-web/http.md).

## CORS — Cross-Origin Resource Sharing

Browser-enforced HTTP policy určujúca, ktoré origins môžu čítať responses alebo odosielať vybrané cross-origin requests. Pozri [HTTP](docs/02-networking-and-web/http.md).

## CPU quota

Cgroup limit maximálneho CPU času v danom period. Po vyčerpaní môže byť workload throttled. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## Cron

Časový scheduler spúšťajúci príkazy podľa crontab pravidiel. Pozri [Cron a systemd timers](docs/01-linux-and-systems/cron-and-systemd-timers.md).

## CSR — Certificate Signing Request

Podpísaná žiadosť obsahujúca public key a požadované certificate identity attributes pre CA. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## DAC — Discretionary Access Control

Model oprávnení založený najmä na UID/GID, mode bits a ACL. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Daemon

Dlhšie bežiaci proces poskytujúci systémovú alebo aplikačnú službu bez priamej interaktívnej session. Pozri [systemd, services a daemons](docs/01-linux-and-systems/systemd-services-daemons.md).

## Data plane

Časť systému spracúvajúca konkrétne frames alebo packets podľa existujúceho forwarding a policy stavu. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## Dataclass — Python

Deklaratívny Python model generujúci metódy pre dátovo orientovanú class, napríklad constructor, equality a representation. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Declarative configuration

Konfigurácia opisujúca požadovaný výsledný stav, nie sekvenciu krokov. Pozri [Declarative vs. Imperative Approach](docs/00-foundations/declarative-vs-imperative.md).

## Default deny

Security policy, pri ktorej sa povoľuje iba explicitne definovaný traffic alebo operácie a všetko ostatné sa zamietne. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Default route

Najmenej špecifická route `0.0.0.0/0` alebo `::/0`, použitá ak neexistuje presnejšia route. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Dependency lock

Presne vyriešený zoznam versions priamych a transitívnych dependencies určený na reprodukovateľnú inštaláciu. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Deployment

Technická operácia umiestnenia verzie aplikácie alebo konfigurácie do cieľového prostredia. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Deployment frequency

Ako často služba úspešne nasadzuje zmeny do produkcie. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Deployment rework rate

Podiel deploymentov, ktoré sú neplánovanou opravou predchádzajúceho deploymentu. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Deserialized object — PowerShell

Prenesená reprezentácia vzdialeného PowerShell objektu, ktorá typicky zachováva properties, ale nie live methods a pôvodné runtime správanie. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Desired state

Požadovaný stav systému deklarovaný používateľom alebo automatizačným nástrojom. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## Detached HEAD

Stav, v ktorom `HEAD` ukazuje priamo na commit namiesto symbolického odkazu na branch. Nové commits treba zachytiť branch refom, inak môžu zostať unreachable. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Deterministic serialization

Serializácia, pri ktorej rovnaký logický vstup vytvára stabilný byte alebo textový výstup podľa definovaných pravidiel. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## DevOps

Kultúrne princípy, organizačné praktiky a technické mechanizmy na rýchle a bezpečné dodávanie zmien. Pozri [DevOps](docs/00-foundations/devops.md).

## DHCP — Dynamic Host Configuration Protocol

Protokol na prideľovanie IP configuration, lease a ďalších network parameters klientom. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## DHCP lease

Časovo obmedzené oprávnenie klienta používať pridelenú adresu a konfiguráciu. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## DHCP relay

Komponent forwardujúci DHCP komunikáciu medzi klientskym broadcast domainom a serverom v inom subnete. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## DHCP reservation

Centrálne DHCP-managed mapovanie identity klienta na stabilnú IP adresu. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## DHCP snooping

Switchová ochrana povoľujúca DHCP server responses iba na trusted portoch. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## DNAT — Destination NAT

Preklad destination adresy alebo portu, používaný napríklad pri publikovaní internej služby. Pozri [NAT](docs/02-networking-and-web/nat.md).

## DNS — Domain Name System

Distribuovaný hierarchický systém mapujúci mená na resource records. Pozri [DNS](docs/02-networking-and-web/dns.md).

## DNS resolver

Komponent vykonávajúci alebo sprostredkujúci DNS resolution. Pozri [DNS](docs/02-networking-and-web/dns.md).

## DNS TTL

Čas, počas ktorého môže resolver cacheovať DNS resource record. Pozri [DNS](docs/02-networking-and-web/dns.md).

## DNSSEC

Rozšírenie DNS poskytujúce kryptografické overenie autenticity a integrity DNS dát cez chain of trust. Pozri [DNS](docs/02-networking-and-web/dns.md).

## Document stream — YAML

YAML stream obsahujúci jeden alebo viac documents oddelených markerom `---`. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## DORA metrics

Metriky software delivery performance sledujúce throughput a instability delivery systému. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Drift

Rozdiel medzi deklarovaným a skutočným stavom systému. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## Drop — firewall action

Tiché zahodenie packetu bez explicitnej odpovede klientovi. Typickým symptómom je timeout. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Dual stack

Prevádzka IPv4 aj IPv6 na rovnakom hoste alebo službe. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## eBPF — extended Berkeley Packet Filter

Kernel technológia na spúšťanie overeného bytecode na definovaných hooks, používaná aj na observability a profiling. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Effective capability set

Množina Linux capabilities aktuálne používaná kernelom pri privilege checks procesu. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Encapsulation

Proces, pri ktorom každá sieťová vrstva pridá svoje metadata okolo payloadu vyššej vrstvy. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## Enforcing mode

Režim SELinux alebo AppArmor policy, v ktorom sa zakázané operácie blokujú. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Environment variable

Pomenovaná hodnota odovzdaná procesu v jeho environment bloku. Pozri [Environment variables](docs/01-linux-and-systems/environment-variables.md).

## Ephemeral port

Dočasný source port typicky pridelený klientskemu socketu. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md).

## Ephemeral port exhaustion

Stav, keď host alebo NAT nemá voľný transportný port pre nový flow. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md) a [NAT](docs/02-networking-and-web/nat.md).

## ETag

HTTP validator reprezentácie používaný na cache revalidation a optimistic concurrency cez conditional requests. Pozri [HTTP](docs/02-networking-and-web/http.md).

## Ethernet frame

Link-layer jednotka obsahujúca source a destination MAC, EtherType, payload a kontrolné metadata. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Exception chaining — Python

Zachovanie pôvodnej exception ako príčiny novej kontextovej exception cez `raise ... from ...`. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Exit status

Číselný výsledok ukončeného procesu alebo shell príkazu. Pozri [Shell, Bash, pipes, redirection a exit codes](docs/01-linux-and-systems/shell-bash-pipes-redirection-exit-codes.md).

## Failed deployment recovery time

Čas potrebný na obnovenie služby po zlyhaní spôsobenom deploymentom. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Fast-forward

Aktualizácia refu, pri ktorej je starý tip ancestor nového tipu, takže sa ref iba posunie bez odstránenia existujúcej ancestry. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Feature branch

Dočasná branch určená na izolovaný vývoj jednej zmeny. Pri trunk-based modeli má byť krátkodobá a často integrovaná. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## Feedback loop

Cesta od vykonanej zmeny k informácii o jej výsledku. Pozri [Feedback Loops](docs/00-foundations/feedback-loops.md).

## File capability

Capability metadata uložené na executable súbore v extended attribute. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## File descriptor

Malé celé číslo v procese odkazujúce na kernelom spravovaný otvorený objekt. Pozri [Shell, Bash, pipes, redirection a exit codes](docs/01-linux-and-systems/shell-bash-pipes-redirection-exit-codes.md).

## Filesystem

Štruktúra mapujúca pathname na metadata a dátové bloky. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## Flow control

TCP mechanizmus chrániaci receiver pred odosielaním väčšieho množstva dát, než dokáže prijať. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Force-with-lease

Bezpečnejšia forma force pushu, ktorá aktualizuje remote ref iba vtedy, keď stále zodpovedá očakávanej hodnote. Stále ide o history rewrite. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Forward proxy

Proxy zastupujúci klienta pri komunikácii s externými servermi. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## Forward secrecy

Vlastnosť ephemeral key agreementu, pri ktorej neskorší únik dlhodobého private key automaticky neodhalí staré TLS sessions. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Git index

Binárna dátová štruktúra predstavujúca pripravovaný snapshot nasledujúceho commitu; obsahuje paths, modes, object IDs a pri konfliktoch viac stages. Pozri [Working tree, staging area a repository](docs/03-git-and-automation/working-tree-staging-repository.md).

## Git ref

Pomenovaný ukazovateľ na Git object ID, typicky commit. Príkladmi sú branches, remote-tracking refs a tags. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Globbing

Shell expansion, ktorá nahrádza wildcard pattern paths zodpovedajúcimi filesystem entries. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Graceful shutdown

Riadené ukončenie, pri ktorom proces prestane prijímať novú prácu, bezpečne spracuje alebo preruší rozpracovaný stav, uvoľní resources a vráti správny status. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Gratuitous ARP

ARP announcement používaný napríklad na aktualizáciu neighbor caches po presune virtual IP. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Greedy quantifier — regex

Regex quantifier, ktorý najprv spotrebuje najväčší možný rozsah a podľa potreby backtrackuje. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Hard link

Ďalší directory entry odkazujúci na ten istý inode. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## HEAD — Git

Špeciálny ref reprezentujúci aktuálnu checkout pozíciu. Typicky symbolicky ukazuje na current branch, ale môže ukazovať priamo na commit. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Health check

Aktívny alebo pasívny test určujúci, či backend môže prijímať nový traffic. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## History rewrite

Operácia vytvárajúca nové commit objects a meniaca branch-visible ancestry, napríklad rebase, amend alebo reset publikovanej branch. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## Hop limit

IPv6 field znižovaný na každom router hop-e; IPv4 ekvivalentom je TTL. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Host key — SSH host key

Kryptografický kľúč, ktorým SSH server preukazuje svoju identitu klientovi. Pozri [SSH](docs/01-linux-and-systems/ssh.md).

## HSTS — HTTP Strict Transport Security

Browser policy oznamujúca, že doména sa má používať iba cez HTTPS počas definovaného času. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## HTTP

Aplikačný request-response protokol s methods, status codes, headers a representation semantics. Pozri [HTTP](docs/02-networking-and-web/http.md).

## HTTP/2

HTTP verzia používajúca binary framing a multiplexované streams nad jedným TCP connection. Pozri [HTTP](docs/02-networking-and-web/http.md).

## HTTP/3

HTTP verzia používajúca QUIC nad UDP s nezávislejším stream loss recovery modelom. Pozri [HTTP](docs/02-networking-and-web/http.md).

## Idempotencia

Vlastnosť operácie, pri ktorej opakovanie s rovnakým vstupom vedie k rovnakému výslednému stavu. Pozri [Idempotency](docs/00-foundations/idempotency.md).

## Idempotency key

Client-generated identifikátor umožňujúci serveru rozpoznať opakovaný ne-idempotentný request a vrátiť konzistentný výsledok. Pozri [REST APIs a WebSockets](docs/02-networking-and-web/rest-apis-and-websockets.md).

## Immutable infrastructure

Model, v ktorom sa existujúce inštancie zásadne neupravujú, ale nahrádzajú novými. Pozri [Immutable vs. Mutable Infrastructure](docs/00-foundations/immutable-vs-mutable-infrastructure.md).

## Imperative approach

Prístup opisujúci konkrétnu sekvenciu krokov. Pozri [Declarative vs. Imperative Approach](docs/00-foundations/declarative-vs-imperative.md).

## Implicit typing — YAML

Automatická interpretácia plain scalaru ako boolean, number, date alebo null podľa YAML schema a parser implementácie. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Index stages

Viac verzií jednej path uložených v Git indexe počas konfliktu: stage 1 je merge base, stage 2 ours a stage 3 theirs. Pozri [Konflikty](docs/03-git-and-automation/merge-conflicts.md).

## Inode

Filesystem objekt obsahujúci metadata a odkazy na dátové bloky. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## IP packet

Network-layer jednotka obsahujúca source a destination IP adresu a payload vyššej vrstvy. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## IPv4 private ranges

Adresy `10.0.0.0/8`, `172.16.0.0/12` a `192.168.0.0/16`, ktoré nie sú globálne routované vo verejnom Internete. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## IPv6 link-local address

IPv6 adresa z `fe80::/10` platná v lokálnom linkovom scope. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Jitter

Náhodná odchýlka pridaná k retry delay, ktorá znižuje synchronizované opakovanie veľkého množstva klientov. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## journald

Systémová logging služba systemd sprístupnená cez `journalctl`. Pozri [journald a logging](docs/01-linux-and-systems/journald-and-logging.md).

## JSON Schema

Deklaratívny schema jazyk na validáciu štruktúry, typov a vybraných constraints JSON dát. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Kernel space

Privilegovaná časť systému, v ktorej kernel spravuje procesy, memory, devices, filesystems a networking. Pozri [Kernel a user space](docs/01-linux-and-systems/kernel-and-user-space.md).

## L4 load balancing

Rozdelenie transportných flows podľa IP, portu, protokolu a connection state bez interpretácie aplikačného obsahu. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## L7 load balancing

Rozdelenie requestov podľa aplikačných údajov, napríklad HTTP hostu, pathu alebo headerov. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Latency

Čas potrebný na dokončenie operácie alebo requestu. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Listening socket

Socket čakajúci na nové TCP spojenia. Po `accept()` vzniká samostatný connected socket. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md).

## Little's Law

Queueing vzťah `concurrency = throughput × time in system`. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Load average

Priemerný počet runnable tasks a určitých tasks v uninterruptible sleep. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Longest-prefix match

Routing pravidlo, podľa ktorého vyhráva zhodná route s najväčším počtom prefix bitov. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Lookaround — regex

Zero-width regex assertion overujúca text pred alebo za aktuálnou pozíciou bez jeho zahrnutia do matchu. Nie je podporovaná vo všetkých engines. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## MAC address

Link-layer identifikátor interface používaný na Ethernet forwarding v lokálnom broadcast domain. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## MAC — Mandatory Access Control

Bezpečnostná politika vynútená systémom nad rámec rozhodnutí ownera objektu. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## `memory.high`

Cgroup v2 memory hranica vyvolávajúca reclaim pressure a throttling. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## `memory.max`

Cgroup v2 hard memory limit, ktorého prekročenie môže viesť ku cgroup-local OOM. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## Merge base

Najlepší spoločný ancestor dvoch commitov používaný ako base pri three-way merge a pri výpočte divergence. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## Merge commit

Commit s dvoma alebo viacerými parents, ktorý explicitne zaznamenáva integráciu rozdielnych ancestry vetiev. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## Merge queue

Mechanizmus, ktorý testuje a integruje pull requests v plánovanom poradí proti aktuálnemu alebo predpokladanému stavu main branch. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## Monorepo

Repository obsahujúci viac služieb, knižníc alebo projektov so spoločným object graphom a možnosťou atomických cross-project zmien. Pozri [Monorepo vs. multirepo](docs/03-git-and-automation/monorepo-vs-multirepo.md).

## Mount

Pripojenie filesystemu alebo iného mountable objektu do spoločného filesystem stromu. Pozri [Storage, mounty a filesystems](docs/01-linux-and-systems/storage-mounts-and-filesystems.md).

## Mount namespace

Namespace poskytujúci samostatný pohľad na mount table a propagation. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## MSS — Maximum Segment Size

Maximálny TCP payload segmentu deklarovaný endpointom, typicky odvodený od MTU mínus IP a TCP headers. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## mTLS — Mutual TLS

TLS model autentifikujúci server aj klienta pomocou certificates. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## MTU — Maximum Transmission Unit

Maximálna veľkosť L3 packetu preneseného interfaceom bez fragmentácie. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Multirepo

Model, v ktorom sú služby alebo projekty rozdelené medzi viac repositories a integrujú sa cez versioned artifacts a explicitné contracts. Pozri [Monorepo vs. multirepo](docs/03-git-and-automation/monorepo-vs-multirepo.md).

## Mutable infrastructure

Model, v ktorom sa existujúce stroje priebežne menia na mieste. Pozri [Immutable vs. Mutable Infrastructure](docs/00-foundations/immutable-vs-mutable-infrastructure.md).

## Namespace — Linux namespace

Kernel objekt poskytujúci procesu izolovaný pohľad na vybranú kategóriu systémového stavu. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## NAT — Network Address Translation

Mechanizmus meniaci source alebo destination IP adresy a často ports pri prechode packetu. Pozri [NAT](docs/02-networking-and-web/nat.md).

## NAT64/DNS64

Prechodový model, v ktorom DNS64 syntetizuje IPv6 odpoveď a NAT64 prekladá traffic IPv6-only klienta na IPv4 server. Pozri [NAT](docs/02-networking-and-web/nat.md).

## NDP — Neighbor Discovery Protocol

IPv6 mechanizmus pre neighbor resolution, router discovery a prefix discovery. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Negative DNS caching

Cacheovanie negatívnej DNS odpovede, napríklad `NXDOMAIN`. Pozri [DNS](docs/02-networking-and-web/dns.md).

## Network ACL

Network policy aplikovaná typicky na subnet alebo segment boundary; v cloud prostredí býva často stateless. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Network namespace

Namespace s vlastnými interfaces, addresses, routes, sockets a firewall state. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## `no_new_privs`

Kernel flag zabraňujúci zvýšeniu privilege cez `execve()`. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Non-terminating error — PowerShell

PowerShell error record, pri ktorom command môže pokračovať; na zachytenie cez `catch` sa často používa `-ErrorAction Stop`. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## NUL-delimited stream

Textovo-binárny stream používajúci NUL byte ako oddeľovač, vhodný napríklad pre bezpečný prenos filesystem paths obsahujúcich whitespace alebo newline. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Object ID — Git

Hash-based identifikátor Git objectu odvodený z typu a obsahu objektu. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Object pipeline — PowerShell

Pipeline prenášajúca .NET objekty s properties a methods namiesto iba formátovaných textových riadkov. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## OCSP — Online Certificate Status Protocol

Protokol na zisťovanie revocation statusu certificate; server môže status poskytovať cez OCSP stapling. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## OOM killer

Kernel mechanizmus poslednej možnosti ukončujúci proces pri memory exhaustion. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Option injection

Situácia, keď hodnota začínajúca `-` je príkazom interpretovaná ako option namiesto dátového argumentu. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## OSI model

Sedemvrstvový konceptuálny model sieťovej komunikácie. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## Package manager

Nástroj na inštaláciu, upgrade a odstránenie balíkov vrátane dependencies a lokálnej evidencie. Pozri [Package management](docs/01-linux-and-systems/package-management.md).

## Packfile

Kompaktný Git storage formát ukladajúci viac objektov s možnou delta kompresiou, bez zmeny logického snapshot modelu. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Page cache

RAM používaná kernelom na cache file-backed dát. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Page fault

Udalosť, pri ktorej požadované virtuálne mapovanie nie je okamžite dostupné. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## PAM — Pluggable Authentication Modules

Framework na skladanie authentication, account, session a password policy. Pozri [Users, groups, permissions, sudo a PAM](docs/01-linux-and-systems/users-groups-permissions-sudo-pam.md).

## Partial clone

Clone režim, ktorý odloží prenos vybraných objects a načíta ich podľa potreby, napríklad s `--filter=blob:none`. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## PAT — Port Address Translation

NAT model, v ktorom viac interných flows zdieľa jednu externú adresu a rozlišuje sa preloženými portmi. Pozri [NAT](docs/02-networking-and-web/nat.md).

## Path traversal

Zraniteľnosť, pri ktorej vstup s prvkami ako `..` alebo absolútnou cestou unikne z povoleného adresára. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Permissive mode

SELinux režim, v ktorom sa policy denials auditujú, ale nevynucujú. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Pester

PowerShell test framework pre assertions, mocks, setup/teardown a test discovery. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## PID namespace

Namespace poskytujúci samostatné process ID číslovanie a process tree. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## PID — Process Identifier

Číselný identifikátor procesu v konkrétnom PID namespace. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## PIDs controller

Cgroup controller obmedzujúci počet procesov alebo threadov cez `pids.max`. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## `pipefail`

Shell option, ktorá spôsobí, že pipeline vráti nenulový status pri zlyhaní ktoréhokoľvek člena, nie iba posledného príkazu. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Pipeline — shell

Reťaz procesov, v ktorej stdout jedného procesu smeruje do stdin ďalšieho. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## PKI — Public Key Infrastructure

Systém certificate authorities, policies, trust stores, issuance, validation, rotation a revocation pre public-key identities. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Policy routing

Routing model, ktorý môže vyberať table podľa source address, marku, ingress interface alebo ďalších selectors. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Port

16-bit transportný identifikátor socket endpointu. Port sám neurčuje aplikačný protokol. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md).

## PowerShell provider

Abstraction layer sprístupňujúca datasources ako filesystem, registry, certificates alebo environment cez jednotné cmdlets a drives. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Process

Bežiaca inštancia programu s adresným priestorom, file descriptormi, credentials a ďalším kernel stavom. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## Profile — performance profile

Vzorka alebo agregácia stackov ukazujúca, kde proces trávi CPU čas, čaká alebo alokuje memory. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Proxy

Sprostredkovateľ ukončujúci jednu komunikáciu a vytvárajúci samostatnú komunikáciu k ďalšiemu endpointu. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## PSI — Pressure Stall Information

Metriky času, počas ktorého tasks čakali pre nedostupnosť CPU, memory alebo I/O kapacity. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## PSS — Proportional Set Size

Odhad memory procesu, pri ktorom sa zdieľané pages pomerne rozdelia medzi procesy. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## PSScriptAnalyzer

Static analysis nástroj pre PowerShell scripts a modules, ktorý kontroluje conventions, compatibility a vybrané security patterns. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## QUIC

Transportný protokol nad UDP implementujúci reliable streams, congestion control, loss recovery a TLS 1.3 integráciu. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Readiness

Stav vyjadrujúci, či instance má prijímať nový traffic. Nie je totožný s liveness. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Rebase

Operácia, ktorá replayuje commits na nový base a vytvára nové commit objects s novými IDs. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## Reconciliation

Opakovaný proces porovnávania desired state so skutočným stavom a vykonávania korekcií. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## ReDoS — Regular Expression Denial of Service

Denial-of-service riziko spôsobené regexom s patologickou runtime complexity nad útočníkom kontrolovaným vstupom. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Reflog

Lokálna evidencia pohybov refs a `HEAD`, použiteľná na recovery commitov po reset, rebase alebo zmazaní branch pred expiráciou záznamov. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Refspec

Pravidlo mapujúce source ref na destination ref pri fetch alebo push operácii. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Regex dialect

Konkrétna syntax a semantics regular expression engine-u, napríklad POSIX ERE, .NET, Python, PCRE alebo RE2. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Release

Produktové alebo procesné rozhodnutie sprístupniť funkcionalitu používateľom. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Remote-tracking ref

Lokálny ref pod `refs/remotes/` reprezentujúci stav remote branch pri poslednom fetchi. Nie je to živý pohľad na server. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Rerere

Git mechanizmus `reuse recorded resolution`, ktorý zaznamená riešenie konfliktu a môže ho znovu aplikovať pri opakovanom konflikte. Pozri [Konflikty](docs/03-git-and-automation/merge-conflicts.md).

## REST

Architectural style pre distributed hypermedia systems založený na constraints ako statelessness, cacheability a uniform interface. Pozri [REST APIs a WebSockets](docs/02-networking-and-web/rest-apis-and-websockets.md).

## Retransmission

Opätovné odoslanie transportných dát po detekcii straty alebo nedostatočného potvrdenia. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Reverse proxy

Proxy zastupujúci serverové služby voči klientom a vykonávajúci napríklad TLS termination, routing alebo caching. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## Roll-forward

Náprava zlyhania nasadením novej opravnej verzie. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Rollback

Návrat k predchádzajúcej verzii aplikácie alebo konfigurácie. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Route

Pravidlo určujúce next hop, interface a ďalšie parametre pre destination prefix. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Route summarization

Reprezentácia viacerých menších prefixes jedným väčším aggregate prefixom. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## RSS — Resident Set Size

Množstvo pages procesu aktuálne resident v RAM. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Runspace — PowerShell

Izolovaný PowerShell execution environment s vlastným session state, používaný aj pri paralelnom spracovaní. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Safe loader — YAML

Parser režim, ktorý načítava základné dátové typy bez povolenia nebezpečnej language-specific object deserializácie. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Saturation

Stav, keď resource nestačí okamžite obslúžiť všetku prácu a vzniká queueing alebo throttling. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Scalar — YAML

YAML node reprezentujúci jednu hodnotu, napríklad string, number, boolean alebo null. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Schema validation

Overenie dát voči deklarovaným typom, required fields a constraints. Neoveruje automaticky všetky business a runtime podmienky. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## SDLC — Software Development Life Cycle

Riadený životný cyklus softvéru od potreby po vyradenie. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## SELinux security context

Label subjectu alebo objektu obsahujúci SELinux user, role, type a prípadne level/range. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Session affinity

Load-balancing policy smerujúca klienta alebo key opakovane na rovnaký backend. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Shallow clone

Clone s obmedzenou ancestry históriou, typicky vytvorený cez `--depth`. Znižuje prenos, ale obmedzuje operácie závislé od plného commit graphu. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Shell expansion

Fáza, v ktorej shell spracuje parameter, command a arithmetic expansion, word splitting a pathname expansion pred spustením príkazu. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## `ShouldProcess` — PowerShell

PowerShell mechanizmus podporujúci `-WhatIf` a `-Confirm` pre vedome označené mutation operácie. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## SLAAC — Stateless Address Autoconfiguration

IPv6 mechanizmus, ktorým host vytvára adresu z prefixu oznamovaného Router Advertisement. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## SNAT — Source NAT

Preklad source adresy alebo portu, používaný typicky pri outbound komunikácii. Pozri [NAT](docs/02-networking-and-web/nat.md).

## SNI — Server Name Indication

TLS extension prenášajúca hostname, aby server alebo proxy vybral správny certificate a virtual host. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Socket

Kernel endpoint komunikácie sprístupnený procesu cez file descriptor. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md).

## Splatting — PowerShell

Odovzdanie kolekcie named alebo positional parameters príkazu pomocou hashtable alebo array. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Split-horizon DNS

DNS model, v ktorom rovnaké meno vracia rozdielne odpovede podľa resolvera, siete alebo klientského contextu. Pozri [DNS](docs/02-networking-and-web/dns.md).

## Squash merge

Integrácia, ktorá vytvorí jeden výsledný commit bez merge ancestry na feature tip. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## SSH agent

Proces vykonávajúci podpisové operácie pomocou odomknutých private keys v pamäti. Pozri [SSH](docs/01-linux-and-systems/ssh.md).

## Staging area

Používateľský názov pre Git index ako pripravovaný snapshot ďalšieho commitu. Pozri [Working tree, staging area a repository](docs/03-git-and-automation/working-tree-staging-repository.md).

## Stash — Git

Lokálny Git stav uchovávajúci dočasné working-tree a index changes pod `refs/stash`. Nie je náhradou remote backupu. Pozri [Cherry-pick a stash](docs/03-git-and-automation/cherry-pick-and-stash.md).

## Stateful firewall

Firewall udržiavajúci connection/flow state a používajúci ho pri rozhodovaní o packets. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Stateless firewall

Firewall posudzujúci každý packet podľa explicitných pravidiel bez connection state. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## `strace`

Nástroj na sledovanie system calls, ich výsledkov a trvania. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Subnet

Časť IP address space definovaná prefixom a použitá ako logická routing alebo topology jednotka. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Subshell

Oddelený shell execution context, ktorého zmeny premenných a working directory sa nemusia preniesť späť do parent shellu. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Swap

Storage-backed priestor pre niektoré anonymné memory pages. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Symbolic link

Filesystem objekt obsahujúci textovú cestu na iný objekt. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## system call

Kontrolovaný prechod z user space do kernel space. Pozri [Kernel a user space](docs/01-linux-and-systems/kernel-and-user-space.md).

## systemd timer

`.timer` unit aktivujúca inú unit podľa calendar alebo monotonic pravidla. Pozri [Cron a systemd timers](docs/01-linux-and-systems/cron-and-systemd-timers.md).

## systemd unit

Deklaratívny objekt spravovaný systemd, napríklad `.service`, `.socket` alebo `.timer`. Pozri [systemd, services a daemons](docs/01-linux-and-systems/systemd-services-daemons.md).

## T-shaped engineer

Inžinier so širokou orientáciou a hlbokou expertízou aspoň v jednej oblasti. Pozri [T-shaped engineer](docs/00-foundations/t-shaped-engineer.md).

## Tag — Git tag

Ref používaný typicky na stabilné označenie konkrétneho release commitu alebo iného objektu. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Tail latency

Latency najpomalšej časti request distribúcie, typicky p95 alebo p99. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## TCP connection

Transportný byte stream identifikovaný source/destination IP adresami a portmi. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## TCP handshake

Výmena SYN, SYN-ACK a ACK, ktorá synchronizuje sequence numbers a vytvorí TCP connection state. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## TCP/IP model

Praktický vrstvený model Application, Transport, Internet a Link používaný na opis Internet stacku. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## Terminating error — PowerShell

PowerShell error, ktorý zastaví aktuálnu operáciu alebo scope a môže byť zachytený cez `try/catch`. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Thread

Plánovateľná vykonávacia jednotka v rámci procesu. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## Throughput

Množstvo práce dokončenej za jednotku času. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## `TIME-WAIT`

TCP state držaný po aktívnom close na ochranu pred starými segments a opätovným použitím rovnakého tuple. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## TLS termination

Ukončenie TLS spojenia na proxy alebo load balanceri, ktorý následne vytvorí samostatné upstream spojenie. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## TLS — Transport Layer Security

Protokol poskytujúci šifrovanie, integritu a autentifikáciu komunikácie. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Toil

Manuálna, opakujúca sa, automatizovateľná a nízko hodnotná prevádzková práca. Pozri [Toil and Technical Debt](docs/00-foundations/toil-and-technical-debt.md).

## Trap — shell

Shell handler spustený pri definovanom signále alebo pseudo-signále ako `EXIT` či `ERR`. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Trunk-based development

Branching model založený na častej integrácii malých zmien do jednej hlavnej branch, podporený krátkodobými branches, CI a feature flags. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## TTL — Time To Live

IPv4 field znižovaný na každom router hop-e; pri nule sa packet zahodí. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Type enforcement

SELinux policy model založený na source type, target type, object class a permissions. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Type hint — Python

Anotácia očakávaného typu používaná static analysis nástrojmi a IDE; sama osebe nie je runtime validáciou. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## UDP datagram

Samostatná transportná správa bez zabudovanej garancie doručenia, poradia alebo retransmission. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Upstream branch

Remote-tracking alebo iný ref priradený lokálnej branch ako default comparison a synchronization target pre status, pull a push. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## URI — Uniform Resource Identifier

Identifikátor resource; URL je typ URI, ktorý zároveň opisuje spôsob alebo miesto prístupu. Pozri [HTTP](docs/02-networking-and-web/http.md).

## USE method

Performance metodika kontrolujúca utilization, saturation a errors každého resource. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## User namespace

Namespace izolujúci UID/GID mapping a capability scope. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## User space

Menej privilegované prostredie, v ktorom bežia aplikácie a systémové procesy. Pozri [Kernel a user space](docs/01-linux-and-systems/kernel-and-user-space.md).

## Utilization

Miera použitia dostupnej kapacity resource. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Value stream

Celý tok práce a informácií od potreby po hodnotu doručenú používateľovi. Pozri [Value Stream Mapping](docs/00-foundations/value-stream-mapping.md).

## Virtual environment — Python

Izolované Python prostredie s vlastným interpreter contextom a nainštalovanými packages. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Virtual memory

Abstrakcia, pri ktorej má proces vlastný virtuálny adresný priestor mapovaný kernelom na RAM, files alebo swap. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## VLAN — Virtual LAN

Logicky oddelený Ethernet broadcast domain, často prenášaný cez 802.1Q tagging. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## VSZ — Virtual Set Size

Veľkosť virtuálneho adresného priestoru procesu. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## WAF — Web Application Firewall

L7 security control vyhodnocujúci HTTP requests podľa aplikačných pravidiel; nie je totožný s L3/L4 firewallom. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## WebSocket

Protokol poskytujúci dlhodobý full-duplex message channel po HTTP upgrade alebo ekvivalentnom transportnom mechanizme. Pozri [REST APIs a WebSockets](docs/02-networking-and-web/rest-apis-and-websockets.md).

## Word splitting

Shell rozdelenie nequoted expansion výsledku na viac slov podľa `IFS`. Je častým zdrojom chýb pri paths a argumentoch. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Working tree

Filesystem materialization aktuálne checkoutnutého Git snapshotu, ktorú používateľ a nástroje priamo menia. Pozri [Working tree, staging area a repository](docs/03-git-and-automation/working-tree-staging-repository.md).

## `X-Forwarded-For`

De facto HTTP header prenášajúci client IP cez proxy chain. Je dôveryhodný iba pri kontrolovanom chain-e a správnom prepisovaní. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## YAML mapping

YAML kolekcia key-value párov, analogická objectu alebo dictionary. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## YAML sequence

Usporiadaná YAML kolekcia hodnôt, analogická array alebo listu. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Zombie process

Ukončený proces, ktorého exit status parent ešte neprevzal cez `wait`. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).
