# Documentation section review status

Tento súbor je ručne udržiavaný ledger dokončených section-level reviewov. Eviduje, ktoré hlavné sekcie boli kapitolu po kapitole prepracované podľa aktuálneho learning-depth a authoring štandardu a sú pripravené na používateľskú kontrolu.

Nie je náhradou za [`DOCUMENTATION-AUDIT.md`](DOCUMENTATION-AUDIT.md). Ten je generovaný skriptom `scripts/audit_learning_depth.py`, obsahuje heuristické findings na úrovni článkov a pri ďalšom spustení sa celý prepíše. Ručný stav preto patrí do tohto samostatného súboru.

## Význam stavov

- **In progress** — sekcia sa práve prepracúva alebo ešte neprešla záverečným section-level passom.
- **Ready for user review** — všetky authoritative kapitoly sekcie boli manuálne prepracované a bol overený ich ordering, navigation chain, terminology a prechod do susedných sekcií.
- **User reviewed** — používateľ sekciu následne skontroloval a explicitne ju akceptoval alebo boli zapracované jeho pripomienky.

## Stav sekcií

| Sekcia | Dokončené kapitoly | Stav | Posledný manuálny pass | Poznámka |
|---|---:|---|---|---|
| `00-foundations` — DevOps Foundations | 20/20 | Ready for user review | 2026-07-25 | Opätovne preverených všetkých 20 kapitol podľa kalibrovaného pedagogického štandardu: súvislý mechanizmus, kauzálne príklady, vysvetlené zoznamy, failure boundaries a diagnostický kontext. Obsahové zásahy neboli potrebné; ordering, navigation a prechod do Linux and Systems ostávajú správne. |
| `01-linux-and-systems` — Linux and Systems | 19/19 | Ready for user review | 2026-07-25 | Opätovne preverených všetkých 19 kapitol podľa kalibrovaného pedagogického štandardu. Kernel, process, filesystem, identity, shell, service, storage, resource, networking a security témy používajú súvislé mechanizmy, vrstvové failure modely a hypotézami riadený troubleshooting; obsahové zásahy neboli potrebné. Ordering, navigation a prechod do Networking and Web Fundamentals ostávajú správne. |
| `02-networking-and-web` — Networking and Web Fundamentals | 16/16 | Ready for user review | 2026-07-25 | Opätovne preverených všetkých 16 kapitol podľa kalibrovaného pedagogického štandardu. Sekcia sleduje jeden end-to-end request cez link, routing, transport, sockets, DNS/DHCP, NAT/firewall, proxy/LB, HTTP, TLS/PKI, API/WebSocket lifecycle a hypothesis-driven troubleshooting. Obsahové zásahy neboli potrebné; ordering, mastery outcomes, navigation a prechod do Git and Automation Basics sú správne. |
| `03-git-and-automation` — Git and Automation Basics | 12/14 pedagogický re-pass | In progress | 2026-07-25 | Opätovne preverený Git object/state/synchronization, integration/recovery, repository-strategy a shell-automation chain: `Git object model → working tree/index/repository → commit/branch/tag/HEAD → clone/fetch/pull/push → merge/rebase → reset/revert/restore → cherry-pick/stash → conflicts → branching strategies → monorepo/multirepo → Bash → PowerShell`. Kapitoly používajú graph/state model, delivery a repository boundary trade-offy a explicitný parse/validate/plan/apply/verify automation lifecycle. Obsahové zásahy neboli potrebné. Zostávajú 2 kapitoly. |
| `04-testing-and-quality` — Testing and Software Quality | 0/15 pedagogický re-pass | In progress | 2026-07-25 | Starší technický pass je dokončený. Nový pedagogický consistency pass začne po uzavretí sekcie 03; dovtedy sa stav nepovažuje za finálne Ready for user review podľa aktuálneho štandardu. |
| `05-ci-cd-and-release` — CI/CD and Release Engineering | 0/23 pedagogický re-pass | In progress | 2026-07-25 | Starší technický pass je dokončený. Nový pedagogický consistency pass začne po sekciách 03 a 04; preverí súvislý source-to-release lifecycle, praktické scenáre a pomer výkladu k referenčným checklistom. |
| `06-gitlab` — GitLab | 2/10 pedagogický re-pass | In progress | 2026-07-25 | Používateľská kontrola odhalila príliš referenčný a list-heavy štýl. `Projects, groups a permissions` a `Merge requests a approvals` už prešli novým passom so súvislým mechanizmom, priebežným scenárom a kauzálnym výkladom; zostáva 8 kapitol. |
| `07-infrastructure-as-code` — Infrastructure as Code and Configuration Management | 1/19 počiatočný rewrite | In progress | 2026-07-25 | Prepracovaná bola prvá kapitola `Infrastructure as Code principles`; ďalšia práca je pozastavená, kým pedagogickým consistency passom neprejdú sekcie 03–06. Prvá kapitola bude pri návrate ešte overená proti finálnemu kalibrovanému štandardu. |

## Section-level completion criteria

Sekcia sa označí ako **Ready for user review** až po splnení všetkých bodov:

1. Každá authoritative kapitola uvedená v section `README.md` bola manuálne prečítaná a podľa potreby kompletne prepracovaná.
2. Bežné konceptuálne sekcie obsahujú prepojené vysvetlenie, nie iba definíciu alebo zoznam hesiel.
3. Významné bullets vysvetľujú význam, mechanizmus, dôsledok alebo rozhodovací kontext položky.
4. Kapitoly zahŕňajú mentálny model, mechanizmus, praktické príklady, failure modes, diagnostiku a kontrolné otázky tam, kde sú relevantné.
5. Metadata a `KNOWLEDGE-NAVIGATION` footer zostali zachované, ak ich článok používa.
6. Poradie v section `README.md` sa zhoduje s `Predchádzajúca` a `Nasledujúca` navigáciou.
7. Prvá a posledná kapitola správne nadväzujú na susedné hlavné sekcie.
8. Terminológia, úroveň detailu a troubleshooting metodika sú v rámci sekcie konzistentné.
9. Stav znamená pripravenosť na používateľskú kontrolu, nie automatické používateľské schválenie.
