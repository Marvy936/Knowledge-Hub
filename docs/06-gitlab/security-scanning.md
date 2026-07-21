# Security scanning

GitLab security scanning integruje viac typov detekcie do CI/CD, merge requestov a vulnerability-management workflowu. Jediný scanner nepokrýva celý attack surface. Potrebný je vrstvený model pre source code, dependencies, secrets, container images, Infrastructure as Code a runtime behavior.

Dostupnosť konkrétnych analyzers, UI reports, policies a governance funkcionality závisí od GitLab verzie, offeringu a tieru. Pri produkčnom návrhu over aktuálnu oficiálnu dokumentáciu.

## 1. Security scanning lifecycle

```text
source/dependency/image/application
→ scanner job alebo push-time kontrola
→ machine-readable report artifact
→ merge-request a pipeline feedback
→ vulnerability record alebo finding
→ triage
→ remediation/exception
→ verification
```

Scanner output nie je automaticky risk decision. Potrebuje kontext, ownership a lifecycle.

## 2. Typy skenovania

Bežné vrstvy:

- SAST,
- dependency scanning,
- secret detection,
- container scanning,
- DAST,
- API security testing,
- Infrastructure as Code scanning,
- SBOM generation a analysis,
- license/compliance controls podľa dostupnej funkcionality.

## 3. SAST

Static Application Security Testing analyzuje source code bez potreby útoku na bežiacu aplikáciu.

Môže hľadať napríklad:

- injection paths,
- insecure deserialization,
- path traversal,
- weak cryptography,
- unsafe APIs,
- authorization mistakes podľa analyzera,
- taint flow.

SAST má obmedzenia:

- false positives,
- language/framework coverage,
- build/generated-code requirements,
- neúplný runtime context,
- custom frameworks,
- konfigurácia mimo repository.

## 4. Basic a advanced SAST

GitLab môže podľa tieru poskytovať základné analyzers a pokročilejšiu cross-file/cross-function analýzu.

Návrhový princíp:

- over supported languages,
- sleduj analyzer lifecycle,
- pinuj alebo riadene aktualizuj templates/analyzers,
- testuj scan completeness,
- nezamieňaj absence findings za absence vulnerabilities.

## 5. Dependency scanning

Dependency scanning identifikuje známe vulnerabilities v direct a transitive dependencies.

Potrebné vstupy:

- manifest,
- lockfile,
- resolved dependency graph,
- SBOM,
- advisory database.

GitLab aktuálne smeruje dependency scanning k SBOM-first workflowu. Legacy analyzers môžu mať deprecation lifecycle, preto pravidelne over aktuálnu odporúčanú metódu.

## 6. SBOM

Software Bill of Materials eviduje components, versions a vzťahy.

SBOM pomáha pri:

- vulnerability matching,
- incident response,
- release evidence,
- dependency inventory,
- continuous rescanning,
- supplier risk.

SBOM nie je dôkaz bezpečnosti ani provenance. Chybný alebo neúplný build môže vytvoriť neúplný SBOM.

## 7. Container scanning

Container scanning analyzuje image obsah, najmä OS packages a podľa capability aj ďalšie dependencies.

Scan musí byť viazaný na digest:

```text
image@sha256:...
```

Tag sa môže zmeniť a znehodnotiť evidence.

Rozlišuj:

- vulnerabilities v application dependencies,
- vulnerabilities v OS packages,
- base-image findings,
- packages prítomné iba v build stage,
- runtime image obsah.

## 8. Dependency vs. container scanning

Tieto kontroly sa dopĺňajú.

Dependency scanning pracuje primárne z project dependency declarations alebo SBOM modelu. Container scanning vidí obsah výsledného image.

Rozdiel môže odhaliť:

- package nainštalovaný mimo lockfile,
- build-stage dependency neprítomnú v runtime image,
- OS package vulnerability,
- nesprávny alebo neúplný SBOM.

## 9. Secret detection

Secret detection hľadá credential-like hodnoty v repository a podľa dostupných features aj pri pushi alebo v UI obsahu.

Vrstvy môžu zahŕňať:

- client-side detection,
- push protection,
- pipeline secret detection,
- automatic response pre podporované secret types.

Ak bol real secret commitnutý, okamžitá reakcia je:

1. revokovať,
2. rotovať,
3. identifikovať exposure window,
4. auditovať použitie,
5. až potom čistiť history podľa potreby.

## 10. DAST

Dynamic Application Security Testing testuje bežiacu aplikáciu prostredníctvom requests a simulated attacks.

Potrebuje:

- stabilný test target,
- seed/authentication,
- scope,
- rate limits,
- safe test data,
- cleanup,
- ochranu pred scanom production side effects.

DAST nenahrádza SAST. Vidí runtime behavior, ale nemusí pokryť neaktivované paths alebo internú logiku.

## 11. API security testing

API scanner potrebuje machine-readable alebo explicitný API surface, napríklad OpenAPI, GraphQL schema alebo recorded traffic podľa nástroja.

Testuj:

- authentication,
- authorization,
- input validation,
- object-level access,
- rate limiting,
- schema deviations,
- error leakage.

Použi test identity s minimálnymi permissions.

## 12. IaC scanning

Infrastructure-as-Code scanning analyzuje deklarácie pre cloud, containers alebo orchestration.

Môže hľadať:

- public exposure,
- weak encryption,
- excessive IAM,
- insecure security groups,
- privileged workloads,
- missing logging,
- risky defaults.

Static IaC scan nevidí automaticky runtime drift, inherited organization policy alebo manually changed resources.

## 13. Scan execution

Scans môžu bežať:

- pri pushi,
- v merge-request pipeline,
- na default branch,
- podľa schedule,
- manuálne,
- cez security policy.

Rôzne contexts riešia rozdielne potreby:

- MR scan — skorý feedback,
- default branch — vulnerability baseline,
- scheduled rescan — nové advisories,
- on-demand DAST — cielená runtime validácia.

## 14. Security report artifacts

Analyzers publikujú machine-readable report artifacts, ktoré GitLab môže spracovať do MR alebo vulnerability UI.

Over:

- job reálne dobehol,
- report vznikol,
- report schema je podporovaná,
- artifact neexpiroval pred downstream spracovaním,
- scanner nepoužil neaktuálny image alebo ruleset.

Zelený pipeline s preskočeným scannerom nie je úspešný security scan.

## 15. Findings vs. vulnerabilities

Finding je detekovaný výsledok konkrétneho scanu. Vulnerability record reprezentuje spravovaný security problém v dlhšom lifecycle.

Lifecycle môže zahŕňať:

- needs triage,
- confirmed,
- dismissed,
- resolved,
- re-detected.

Dismissal musí mať dôvod, ownera a podľa policy expiry alebo review.

## 16. Merge request feedback

MR feedback má ukázať nové alebo zmenené findings relevantné pre diff.

Nezakladaj gate iba na celkovom počte vulnerabilities. Rozlišuj:

- existing baseline,
- newly introduced,
- severity,
- reachability/validity podľa dostupnosti,
- exploitability,
- component exposure,
- fix availability.

## 17. Vulnerability report

Default-branch scan results môžu tvoriť vulnerability inventory. Potrebné sú:

- ownership,
- SLA podľa severity/risk,
- deduplication,
- false-positive handling,
- remediation tracking,
- exceptions,
- export/reporting.

Scanner dashboard bez procesu opráv je iba backlog generator.

## 18. Security policies

GitLab security policies môžu podľa dostupnej funkcionality vynucovať:

- execution scanner jobs,
- scheduled scans,
- approval behavior,
- project/group scope,
- vulnerability-management actions.

Policy repository je citlivá governance boundary. Chráň jeho permissions, merge process a audit.

## 19. Gate design

Blocking gate má používať stabilný a nízko-noise signal.

Príklad policy:

```text
new critical reachable vulnerability
→ block

existing accepted medium finding
→ visible, neblokuje

scanner infrastructure outage
→ fail-open alebo fail-closed podľa rizika a fallbacku
```

Nejasný „block all highs“ model môže viesť k bypass kultúre.

## 20. Exceptions

Exception musí obsahovať:

- finding/vulnerability identity,
- business a technical dôvod,
- compensating controls,
- ownera,
- expiration,
- review interval,
- remediation plan.

Permanent dismissal bez evidence vytvára skrytý risk debt.

## 21. Analyzer supply chain

Scanner image a template sú executable dependencies.

Chráň:

- pinned versions alebo controlled update channels,
- registry trust,
- analyzer provenance,
- template ownership,
- runner isolation,
- outbound network,
- access k source a secrets.

Security scanner s privileged runnerom môže mať väčší blast radius než aplikácia, ktorú skenuje.

## 22. Scan performance

Optimalizuj:

- affected-component selection,
- parallel execution,
- scanner cache podľa trust modelu,
- separate fast MR a deep scheduled scans,
- DAST scope,
- analyzer timeout,
- artifact size.

Nevypínaj scanner iba preto, že je pomalý. Najprv zisti critical path a coverage trade-off.

## 23. False positives a false negatives

### False positive

Scanner hlási problém, ktorý v reálnom context-e nie je exploitable alebo prítomný.

### False negative

Scanner problém nezachytí.

Znižuj ich cez:

- ruleset tuning,
- better build context,
- threat modeling,
- runtime tests,
- manual review,
- incident-derived regression tests,
- multi-layer scanning.

## 24. Continuous rescanning

Nová vulnerability môže byť zverejnená po release bez zmeny source. Potrebné je:

- aktualizovať advisory data,
- znovu vyhodnotiť SBOM/images,
- identifikovať nasadené digests,
- prioritizovať exposed services,
- rebuildnúť a redeploynúť patched artifacts.

„Pipeline bola zelená pred tromi mesiacmi“ nie je aktuálny risk signal.

## 25. Security telemetry

Sleduj:

- scan coverage podľa projektu/jazyka/artifactu,
- scanner success rate,
- missing reports,
- time to triage,
- time to remediate,
- exception age,
- reopened findings,
- false-positive rate,
- vulnerabilities v deployed versions,
- percent releases so SBOM a scan evidence.

## 26. Troubleshooting

### Security job sa nevytvoril

Over `rules`, pipeline source, include/template version, supported language/files a policy scope.

### Job je zelený, report chýba

Scanner nemusel nájsť input, report path/schema je chybná alebo artifact nebol publikovaný.

### MR neukazuje findings

Over tier/feature availability, MR pipeline context, target branch baseline a úspešné spracovanie reportu.

### Container scan analyzuje zlý image

Porovnaj digest v build outpute, scanner inpute a registry.

### Secret finding bol dismissed, ale token funguje

Dismissal nie je revokácia. Okamžite token revoke/rotate a audituj použitie.

### DAST poškodzuje test environment

Scan používa mutation paths bez safe data alebo scope. Zastav scan, obnov environment a uprav authentication, exclusions a rate limits.

## 27. Kontrolné otázky

1. Aký attack surface pokrýva SAST?
2. Prečo dependency a container scanning nie sú rovnaké?
3. Čo poskytuje SBOM a čo neposkytuje?
4. Ako reagovať na reálny leaked secret?
5. Aké riziká má DAST?
6. Aký je rozdiel medzi findingom a vulnerability recordom?
7. Kedy má security gate blokovať?
8. Čo musí obsahovať exception?
9. Prečo analyzers predstavujú supply-chain dependency?
10. Ako odhaliť, že security scan vôbec neprebehol?

## Glossary impact

Relevantné pojmy: GitLab SAST, dependency scanning, container scanning, secret detection, secret push protection, DAST, API security testing, security report artifact, vulnerability record, security policy, continuous rescanning a scan coverage.

## Oficiálna dokumentácia

- [Application security testing](https://docs.gitlab.com/user/application_security/)
- [SAST](https://docs.gitlab.com/user/application_security/sast/)
- [Dependency scanning](https://docs.gitlab.com/user/application_security/dependency_scanning/)
- [Container scanning](https://docs.gitlab.com/user/application_security/container_scanning/)
- [Secret detection](https://docs.gitlab.com/user/application_security/secret_detection/)
- [DAST](https://docs.gitlab.com/user/application_security/dast/)
- [Security policies](https://docs.gitlab.com/user/application_security/policies/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Environments, deployments a releases](environments-deployments-releases.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
