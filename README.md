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
7. Každý nový obsahový blok priebežne udržiava aj `GLOSSARY.md`.

## Štruktúra repozitára

```text
Knowledge-Hub/
├── docs/               # Teória, mechanizmy a mentálne modely
├── examples/           # Samostatne použiteľné manifesty, konfigurácie a skripty
├── labs/               # Praktické úlohy a experimenty
├── troubleshooting/    # Poruchové scenáre, diagnostika a root cause
├── templates/          # Jednotné šablóny dokumentov
├── scripts/            # Generátory a validátory dokumentácie
├── ROADMAP.md          # Odporúčané poradie učenia
├── GLOSSARY.md         # Rýchle definície pojmov
└── REVIEW.md           # Stav zvládnutia a opakovanie
```

## Oblasti

Aktívne sekcie:

1. [DevOps Foundations](docs/00-foundations/README.md)
2. [Linux and Systems](docs/01-linux-and-systems/README.md)
3. [Networking and Web Fundamentals](docs/02-networking-and-web/README.md)
4. [Git and Automation Basics](docs/03-git-and-automation/README.md)
5. [Testing and Software Quality](docs/04-testing-and-quality/README.md)
6. [CI/CD and Release Engineering](docs/05-ci-cd-and-release/README.md)

Plánované hlavné domény:

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

Kompletné poradie a stav spracovania je v [ROADMAP.md](ROADMAP.md).

## Navigácia

Každá aktívna sekcia má vlastný `README.md` s očíslovaným poradím článkov. Toto poradie je jediným zdrojom pre lineárnu navigáciu.

Na konci učebných článkov sa generuje footer:

```text
← Predchádzajúca · ↑ Obsah sekcie · Nasledujúca →
```

Synchronizácia:

```bash
python scripts/update_navigation.py --write
```

Validácia bez zmeny súborov:

```bash
python scripts/update_navigation.py --check
```

GitHub Actions po zmene na `main` synchronizuje footery a klikateľné odkazy v roadmape. Pri pull requeste zlyhá kontrola, keď poradie, footery alebo roadmapa nie sú konzistentné.

Laby a troubleshooting scenáre nepoužívajú globálne Previous/Next poradie. Ich footer smeruje späť na súvisiacu učebnú kapitolu a lokálny index danej praktickej oblasti.

## Glossary maintenance

`GLOSSARY.md` je priebežne udržiavaný referenčný index, nie jednorazový dokument.

Pri každej novej kapitole alebo obsahovom bloku sa musí vyhodnotiť:

- ktoré nové pojmy sa budú opakovane používať aj v ďalších témach,
- ktoré existujúce definície treba spresniť,
- na ktorú kapitolu má heslo odkazovať ako na autoritatívny kontext,
- či nevznikli synonymá alebo duplicitné heslá s odlišným významom.

Glossary sa aktualizuje v rovnakom pracovnom bloku ako články. Nepatria doň všetky názvy príkazov a konfiguračných polí; patria tam stabilné koncepty potrebné na orientáciu naprieč doménami.

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

## Pravidlá pre citlivé údaje

Do repozitára nepatria reálne heslá, tokeny, privátne kľúče, interné hostname, zákaznícke dáta ani proprietárne firemné konfigurácie. Ani private repository nie je secret manager.
