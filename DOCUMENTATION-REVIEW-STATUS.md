# Documentation section review status

Tento súbor je ručne udržiavaný ledger section-level reviewov. Eviduje, ktoré hlavné sekcie boli kapitolu po kapitole preverené podľa aktuálneho learning-depth a authoring štandardu a sú pripravené na používateľskú kontrolu.

Nie je náhradou za [`DOCUMENTATION-AUDIT.md`](DOCUMENTATION-AUDIT.md). Ten je generovaný skriptom `scripts/audit_learning_depth.py`, obsahuje heuristické findings na úrovni článkov a pri ďalšom spustení sa celý prepíše. Ručný stav preto patrí do tohto samostatného súboru.

## Význam stavov

- **In progress** — sekcia sa práve prepracúva alebo ešte neprešla záverečným prísnym section-level passom.
- **Ready for user review** — všetky authoritative kapitoly sekcie prešli prísnym pedagogickým aj technickým reviewom a bol overený ich ordering, navigation chain, terminology a prechod do susedných sekcií.
- **User reviewed** — používateľ sekciu následne skontroloval a explicitne ju akceptoval alebo boli zapracované jeho pripomienky.

## Stav sekcií

| Sekcia | Dokončené kapitoly | Stav | Posledný manuálny pass | Poznámka |
|---|---:|---|---|---|
| `00-foundations` — DevOps Foundations | 20/20 strict revalidation | Ready for user review | 2026-07-25 | Všetkých 20 authoritative kapitol bolo znovu prečítaných podľa prísneho narrative/mechanism/scenario gate-u. Kapitoly používajú konzistentný chain od SDLC a DevOps regulačného modelu cez flow, feedback, systems thinking, ownership a automation až po state transitions, idempotency, reconciliation, infrastructure lifecycle, toil, VSM a DORA. `Automation mindset` bola kompletne prepísaná okolo environment-vending lifecycle-u `observe → authoritative state → input–plan–apply–verify–recover → adoption/retirement`. `DevOps anti-patterns` bola kompletne prepísaná okolo jedného neúspešného transformačného programu Atlas a reinforcing loopu medzi tool-first zmenou, central queue, approval theater, slabým ownershipom, hero culture a metric gamingom. Ostatných 18 kapitol prešlo bez obsahovej zmeny na základe dominantného modelu, worked scenárov a mechanistického troubleshootingu. README ordering, všetky navigation väzby a prechod z poslednej kapitoly na `01-linux-and-systems/kernel-and-user-space.md` boli overené. Sekcia je pripravená na používateľskú kontrolu, nie automaticky používateľsky schválená. |
| `01-linux-and-systems` — Linux and Systems | 19/19 strict revalidation | Ready for user review | 2026-07-25 | Všetkých 19 authoritative kapitol bolo znovu prečítaných podľa prísneho narrative/mechanism/scenario gate-u a nevyžadovalo obsahový rewrite. Sekcia drží konzistentný runtime chain od privilege boundary, procesov, pathname/inode a process credentials cez shell execution, environment snapshots, systemd a package transakcie až po logging, storage, CPU/memory, packet path, SSH, scheduled jobs, namespaces, cgroups a security enforcement. Záverečný blok prešiel na základe troch odlíšených mechanizmov: capabilities ako `process sets + execve transformácia + bounding/no_new_privs + user-namespace scope`; SELinux/AppArmor ako MAC decision nad process/object identity, operation a audit evidence; a performance troubleshooting ako `user symptom → scope/timeline → observation point → falsifikovateľná hypotéza → bezpečný experiment → overený outcome`. Worked failures pokrývajú chýbajúcu capability po deploymente, službu fungujúcu iba s `privileged`, nesprávny SELinux label alebo AppArmor transition, CPU throttling, cgroup-local OOM, storage/network waits a descriptor či lock contention. README ordering, všetky navigation väzby, prechod z `00-foundations/devops-anti-patterns.md` a obojsmerná väzba na `02-networking-and-web/osi-and-tcp-ip-model.md` boli overené. Sekcia je pripravená na používateľskú kontrolu, nie automaticky používateľsky schválená. |
| `02-networking-and-web` — Networking and Web Fundamentals | 4/16 strict revalidation | In progress | 2026-07-25 | Prísne preverený úvodný packet-path chain `OSI a TCP/IP model → Ethernet, MAC a ARP → IPv4, IPv6 a subnetting → Routing a default gateway`. Kapitoly prešli bez obsahového zásahu. OSI/TCP-IP kapitola používa HTTPS request ako spoločný journey cez encapsulation, hop-by-hop a end-to-end boundaries, observation points a timeout budget. Ethernet kapitola drží lokálny-hop model `route decision → next-hop IP → ARP/neighbor state → destination MAC → switch forwarding` a odvodzuje z neho gateway, duplicate-IP aj VIP-failover diagnostiku. IPv4/IPv6 kapitola viaže prefix matematiku na connected route, ARP/NDP, source selection, dual stack, sumarizáciu a renumbering; referenčné tabuľky nenesú hlavný výklad. Routing kapitola používa decision chain `policy rule → routing table → longest-prefix match → source/next hop → neighbor → forward a return path` a rozlišuje control-plane state od reálneho packet movementu. Blok `NAT → Firewally → Proxy/reverse proxy → Load balancing` zostáva explicitne určený na rewrite v neskoršom passe. Zostáva 12 kapitol. |
| `03-git-and-automation` — Git and Automation Basics | 0/14 strict revalidation | In progress | 2026-07-25 | Predchádzajúci priebežný pass 12/14 sa nepovažuje za finálny. Celá sekcia sa po novom hodnotí rovnakým prísnym gateom od prvej kapitoly. |
| `04-testing-and-quality` — Testing and Software Quality | 0/15 strict revalidation | In progress | 2026-07-25 | Starší technický pass je iba historický. Nový prísny pedagogický consistency pass ešte nezačal. |
| `05-ci-cd-and-release` — CI/CD and Release Engineering | 0/23 strict revalidation | In progress | 2026-07-25 | Starší technický pass je iba historický. Nový pass preverí dominantný source-to-release príbeh, kauzálny výklad a oddelenie učebného jadra od referenčných kontrol. |
| `06-gitlab` — GitLab | 2/10 rewrite candidates, strict revalidation pending | In progress | 2026-07-25 | Prvé dve kapitoly boli pedagogicky prepísané, ale celá sekcia vrátane nich ešte musí prejsť finálnym prísnym consistency gateom. |
| `07-infrastructure-as-code` — Infrastructure as Code and Configuration Management | 1/19 initial rewrite, strict revalidation pending | In progress | 2026-07-25 | Prvá kapitola bola prepracovaná, no ďalšia práca zostáva pozastavená, kým sekcie 00–06 neprejdú jednotným prísnym auditom. |

## Section-level completion criteria

Sekcia sa označí ako **Ready for user review** až po splnení všetkých bodov:

1. Každá authoritative kapitola uvedená v section `README.md` bola manuálne prečítaná celá a podľa potreby kompletne prepracovaná.
2. Kapitola má jeden dominantný mentálny model, lifecycle alebo end-to-end scenár, ktorý spája jej hlavné koncepty; samotná tematická úplnosť alebo dĺžka nestačí.
3. Bežné konceptuálne sekcie obsahujú prepojené vysvetlenie príčina → mechanizmus → dôsledok, nie iba definíciu, taxonómiu alebo zoznam hesiel.
4. Významné bullets sumarizujú už vysvetlený model. Nesmú niesť hlavnú učebnú záťaž kapitoly.
5. Každý hlavný concept cluster obsahuje konkrétny worked scenario alebo packet/change/request journey a aspoň jednu failure boundary odvodenú z rovnakého modelu.
6. Troubleshooting musí vychádzať z predchádzajúceho mechanizmu a observation points; všeobecný zoznam nástrojov alebo kontrol nie je dostatočný.
7. Referenčné katalógy, controls a checklisty sú oddelené od hlavného učebného výkladu a nesmú ho objemovo ani štruktúrne nahradiť.
8. Kapitola neprejde iba preto, že obsahuje veľa detailov, state taxonómií, bezpečnostných controls, failure modes alebo kontrolných otázok.
9. Metadata a `KNOWLEDGE-NAVIGATION` footer zostali zachované, ak ich článok používa.
10. Poradie v section `README.md` sa zhoduje s `Predchádzajúca` a `Nasledujúca` navigáciou.
11. Prvá a posledná kapitola správne nadväzujú na susedné hlavné sekcie.
12. Terminológia, úroveň detailu a troubleshooting metodika sú v rámci sekcie konzistentné.
13. Stav znamená pripravenosť na používateľskú kontrolu, nie automatické používateľské schválenie.