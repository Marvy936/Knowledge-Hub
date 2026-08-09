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
8. Konceptuálna sekcia nesmie zostať iba pri jednej vete a zozname. Musí vysvetliť definíciu, mechanizmus, význam nových pojmov a podľa kontextu aj príklad, hranicu alebo failure mode.
9. Odrážky sumarizujú už vysvetlený model; nenahrádzajú súvislý učebný výklad.

Podrobný štandard je v [AUTHORING-GUIDE.md](AUTHORING-GUIDE.md). Automatický audit hĺbky výkladu vytvára [DOCUMENTATION-AUDIT.md](DOCUMENTATION-AUDIT.md).

## Štruktúra repozitára

```text
Knowledge-Hub/
├── docs/                       # Teória, mechanizmy a mentálne modely
├── examples/                   # Samostatne použiteľné manifesty, konfigurácie a skripty
├── labs/                       # Praktické úlohy a experimenty
├── troubleshooting/            # Poruchové scenáre, diagnostika a root cause
├── templates/                  # Jednotné šablóny dokumentov
├── scripts/                    # Generátory, validátory a obsahový audit
├── AUTHORING-GUIDE.md          # Povinný štandard vysvetľovania konceptov
├── DOCUMENTATION-AUDIT.md      # Generovaný prioritizovaný audit učebnej hĺbky
├── ROADMAP.md                  # Odporúčané poradie učenia
├── GLOSSARY.md                 # Rýchle definície pojmov
└── REVIEW.md                   # Stav zvládnutia a opakovanie
```

## Oblasti

Aktívne sekcie:

1. [DevOps Foundations](docs/00-foundations/README.md)
2. [Linux and Systems](docs/01-linux-and-systems/README.md)
3. [Networking and Web Fundamentals](docs/02-networking-and-web/README.md)
4. [Git and Automation Basics](docs/03-git-and-automation/README.md)
5. [Testing and Software Quality](docs/04-testing-and-quality/README.md)
6. [CI/CD and Release Engineering](docs/05-ci-cd-and-release/README.md)
7. [GitLab](docs/06-gitlab/README.md)
8. [Infrastructure as Code and Configuration Management](docs/07-infrastructure-as-code-and-configuration-management/README.md)
9. [Container Fundamentals and Docker](docs/08-container-fundamentals-and-docker/README.md)
10. [Kubernetes](docs/09-kubernetes/README.md)
11. [Helm and CKA](docs/10-helm-and-cka/README.md)
12. [Cloud and AWS](docs/11-cloud-and-aws/README.md)
13. [Observability](docs/12-observability/README.md)
14. [Security and Identity](docs/13-security-and-identity/README.md)
15. [SRE and Operations](docs/14-sre-and-operations/README.md)
16. [Databases and Distributed Systems](docs/15-databases-and-distributed-systems/README.md)
17. [GitOps and Platform Engineering](docs/16-gitops-and-platform-engineering/README.md)
18. [Keycloak and Identity Platform](docs/17-keycloak-and-identity-platform/README.md)
19. [Machine Learning Fundamentals](docs/18-machine-learning-fundamentals/README.md)
20. [MLOps and ML Platforms](docs/19-mlops-and-ml-platforms/README.md)
21. [LLM and GenAI Engineering](docs/20-llm-and-genai-engineering/README.md)
22. [AI Agents and Intelligent Automation](docs/21-ai-agents-and-intelligent-automation/README.md)

Sekcie 00–17 boli používateľom schválené v aktuálnom rozsahu. Sekcie 18–21 majú dokončené authoritative inventory: Machine Learning Fundamentals **26/26**, MLOps and ML Platforms **34/34**, LLM and GenAI Engineering **37/37** a AI Agents and Intelligent Automation **62/62**. Všetky štyri sú `Ready for user review`; tento stav znamená dokončený dokumentačný pass, nie používateľské prijatie, runtime verifikáciu alebo production stability. Pôvodné rozhodnutia, plánované laby, troubleshooting drilly, flagship projekty a produktové tracky zostávajú v [FUTURE-IDENTITY-AI-ROADMAP.md](FUTURE-IDENTITY-AI-ROADMAP.md).

Kompletné poradie a stav spracovania je v [ROADMAP.md](ROADMAP.md).

## Practical v1 — offline/core quick start

Practical v1 spája Machine Learning, MLOps contracts, Knowledge Hub RAG, Keycloak resource-server contracts a bounded operations agenta do jedného deterministického core validation pathu. Tento path nepoužíva platený model provider, cloud account ani externý API key.

Dependency bootstrap môže pri prvej inštalácii potrebovať Python package index alebo lokálny package cache. Samotný core orchestrátor po nainštalovaní dependencies vykonáva iba repository-local contracty a disposable local state.

Podporovaný základ je Python 3.12. Z čistého checkoutu na Linuxe/WSL2:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install \
  -e 'labs/machine-learning[dev]' \
  -e 'labs/mlops[dev,registry,serving]' \
  -e 'labs/llm-rag[dev]' \
  -e 'labs/agent-ops[dev]' \
  -e 'labs/keycloak-ai-api[dev]'
```

Prečo sa packages inštalujú explicitne: každý flagship zostáva samostatný package boundary a jeho standalone CI job musí vedieť odhaliť skrytú sibling dependency. Až offline/core runner zámerne vytvorí combined environment, pretože overuje celý prepojený Practical v1 source surface.

Najprv sa dajú spustiť contracty samotného release tooling-u:

```bash
python -m pytest scripts/tests -q
```

Potom core orchestrátor:

```bash
rm -rf .runtime/practical-v1/core-run
rm -f .runtime/practical-v1-evidence.json

python scripts/practical_v1_core.py \
  --repo-root . \
  --work-root .runtime/practical-v1/core-run \
  --evidence .runtime/practical-v1-evidence.json
```

Orchestrátor odmietne dirty tracked worktree, aby `subject_sha` nemohol predstierať inú revíziu než source, ktorý sa reálne vykonáva. Stage chain je:

```text
compileall
→ repository link/JSON/import/artifact-integrity validation
→ Machine Learning contracts
→ MLOps contracts
→ LLM/RAG contracts
→ bounded-agent contracts
→ Keycloak AI API contracts
→ deterministic agent hard evaluation
→ disposable workroot cleanup read-back
```

`all_passed=true` vznikne iba ak sa vykoná presne celý stage set v očakávanom poradí a `cleanup_verified=true`. Zlyhanie sa nezmení na úspech tým, že sa ďalšie stages preskočia.

Evidence JSON zostáva zámerne mimo disposable workrootu, aby sa dal po rune prečítať. Obsahuje exact Git SHA, Python version, per-stage return code/duration, SHA-256 stdout/stderr, bounded log tails, agent hard-eval identity a canonical `evidence_id`.

Po kontrole evidence sa local output odstráni:

```bash
rm -f .runtime/practical-v1-evidence.json
rmdir .runtime/practical-v1 2>/dev/null || true
rmdir .runtime 2>/dev/null || true
```

Permanentný CI contract je v `.github/workflows/practical-v1-core.yml`. Kým issue #151 blokuje vytváranie repository Actions runov, existencia workflowu a runnera znamená iba source-level `Implemented`, nie `Runtime verified`.

Aktuálny praktický stav je v [PRACTICAL-STATUS.md](PRACTICAL-STATUS.md) a hard release gates v [PRACTICAL-V1-ROADMAP.md](PRACTICAL-V1-ROADMAP.md).

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

## Documentation learning-depth audit

Audit všetkých Markdown súborov pod `docs/`:

```bash
python scripts/audit_learning_depth.py --all-docs
```
