# DevOps Knowledge Hub

Osobný docs-as-code repozitár na systematické štúdium DevOps, cloudových platforiem, kontajnerov, Kubernetes a súvisiacich oblastí.

Cieľom nie je vytvoriť zbierku izolovaných definícií. Každá dôležitá téma má vysvetliť:

- aký problém rieši,
- ako funguje interne,
- ako súvisí s ostatnými časťami systému,
- ako sa používa v praxi,
- ako sa pozoruje a diagnostikuje,
- aké rozhodnutia a trade-offy prináša.

## Základné princípy

1. Témy sa študujú v poradí od fundamentov k vyšším vrstvám.
2. Teória, spustiteľné príklady, laby a troubleshooting scenáre sú oddelené.
3. Príkazy a konfigurácie musia mať vysvetlený účel a mechanizmus.
4. Funkčné príklady dopĺňajú realistické a zámerne chybné scenáre.
5. Hlavným cieľom je praktické porozumenie a schopnosť diagnostiky, nie memorovanie.
6. Technické názvy zostávajú v angličtine; vysvetlenia sú primárne v slovenčine.

## Štruktúra repozitára

```text
Knowledge-Hub/
├── docs/               # Teória, mechanizmy a mentálne modely
├── examples/           # Samostatne použiteľné manifesty, konfigurácie a skripty
├── labs/               # Praktické úlohy a experimenty
├── troubleshooting/    # Poruchové scenáre, diagnostika a root cause
├── templates/          # Jednotné šablóny dokumentov
├── ROADMAP.md          # Odporúčané poradie učenia
├── GLOSSARY.md         # Rýchle definície pojmov
└── REVIEW.md           # Stav zvládnutia a opakovanie
```

## Oblasti

Plánované hlavné domény:

- DevOps foundations a SDLC
- Linux a systems engineering
- Networking a web fundamentals
- Git a source control
- Testing a software quality
- CI/CD a release engineering
- GitLab
- Terraform a Infrastructure as Code
- Ansible a configuration management
- Containers a Docker
- Kubernetes a CKA
- Helm
- Cloud fundamentals a AWS
- Observability
- Security, IAM a supply-chain security
- SRE a operations
- Databases
- Distributed systems
- GitOps a platform engineering
- Automation a scripting

Kompletné poradie je v [ROADMAP.md](ROADMAP.md).

## Úrovne zvládnutia

| Úroveň | Význam |
|---|---|
| L0 | Tému nepoznám. |
| L1 | Viem ju presne definovať. |
| L2 | Rozumiem mechanizmu a závislostiam. |
| L3 | Viem ju prakticky použiť. |
| L4 | Viem diagnostikovať zlyhania. |
| L5 | Viem navrhnúť a technicky obhájiť riešenie. |

Pre hlavné DevOps oblasti je cieľom minimálne L4. Pri témach, ktoré priamo navrhujem alebo prevádzkujem, je cieľom L5.

## Stav témy

Stav dokumentu a úroveň zvládnutia sú oddelené:

- `Not Started`
- `Learning`
- `Practicing`
- `Understood`
- `Needs Review`

Príklad:

```text
Status: Needs Review
Level: L4
```

To znamená, že téma bola prakticky zvládnutá, ale potrebuje zopakovanie.

## Prvé kapitoly

1. [Software Development Life Cycle](docs/00-foundations/sdlc.md)
2. [DevOps](docs/00-foundations/devops.md)

## Pravidlá pre citlivé údaje

Do repozitára nepatria reálne heslá, tokeny, privátne kľúče, interné hostname, zákaznícke dáta ani proprietárne firemné konfigurácie. Ani private repository nie je secret manager.
