# Documentation Audit

Tento ledger eviduje sekcie, ktoré prešli úplným manuálnym auditom a prepracovaním podľa aktuálneho dokumentačného štandardu Knowledge Hubu.

## Auditný štandard

Sekcia je označená ako **Ready for user review** iba vtedy, keď:

- všetky kapitoly v odporúčanom poradí boli manuálne prečítané;
- konceptuálne časti vysvetľujú mechanizmus, nie iba jednovetovú definíciu;
- významné zoznamy a tabuľky majú vysvetlený význam, dôsledky a hranice použitia;
- kapitoly obsahujú praktické príklady, failure modes, diagnostiku a kontrolné otázky;
- terminológia je konzistentná v článkoch, README a navigácii;
- metadata a `KNOWLEDGE-NAVIGATION` bloky zostali zachované;
- odkazy medzi prvou, poslednou a susednými sekciami boli overené;
- zmeny boli commitnuté na `main`;
- sekcia ešte nie je označená ako používateľom schválená, kým ju používateľ neskontroluje.

## Stav sekcií

| Sekcia | Kapitoly | Stav | Záverečný audit | Poznámka |
|---|---:|---|---|---|
| `00-foundations` | 20/20 | Ready for user review | Dokončený | Procesné a mentálne DevOps základy sú prepracované v jednotnom L2 štandarde. |
| `01-linux-and-systems` | 19/19 | Ready for user review | Dokončený | Overený prechod z Foundations a do Networking sekcie; terminológia a navigácia zjednotené. |
| `02-networking-and-web` | 16/16 | Ready for user review | Dokončený 2026-07-24 | Overený celý path od OSI/L2 a adresovania cez transport, DNS, NAT, proxy, HTTP/TLS a API až po evidence-driven troubleshooting; posledná kapitola odkazuje na Git object model. |
| `03-git-and-automation` | 0/? | Not started in hard audit | — | Nasledujúca sekcia na prepracovanie. |

## Networking and Web Fundamentals — záverečný výsledok

Audit sekcie `docs/02-networking-and-web/` potvrdil:

- 16 z 16 kapitol je kompletne prepracovaných;
- odporúčané poradie v `README.md` zodpovedá navigačnému reťazcu;
- prvá kapitola nadväzuje na `Linux networking` a posledná pokračuje na `Git object model`;
- L2/L3, transport, naming, translation, policy, proxy, application a security vrstvy sú terminologicky oddelené;
- diagnostické kapitoly používajú model `symptom → scope → flow identity → observation point → hypothesis → evidence → mitigation → verification`;
- NAT nie je zamieňaný s firewallom, port so službou, TLS s HTTP ani transportný úspech s business úspechom;
- HTTP, TLS, REST a WebSocket kapitoly obsahujú lifecycle, state ownership, timeouty, retry, backpressure, rotation a recovery semantics;
- sekcia je pripravená na používateľskú kontrolu.

## Audit history

| Dátum | Sekcia | Výsledok |
|---|---|---|
| 2026-07-24 | `00-foundations` | Ready for user review |
| 2026-07-24 | `01-linux-and-systems` | Ready for user review |
| 2026-07-24 | `02-networking-and-web` | Ready for user review |
