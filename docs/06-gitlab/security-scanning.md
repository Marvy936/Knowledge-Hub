# Security scanning

## Metadata

- Status: Learning
- Level: L2
- Domain: GitLab

## 1. Definícia

GitLab security scanning prepája analyzers, CI/CD jobs, machine-readable reporty, merge-request feedback, vulnerability records a security policies. Jeho cieľom nie je iba „spustiť scanner“, ale vytvoriť dôveryhodný lifecycle:

```text
attack surface a subject
→ applicable scanners
→ valid execution a reporty
→ findings
→ risk triage
→ gate alebo remediation decision
→ verification
→ continuous rescanning nasadených artifacts
```

Žiadny scanner nepokrýva celý systém. Dôveryhodný program vrství source, dependencies, secrets, container images, API/runtime behavior a Infrastructure as Code a zároveň explicitne eviduje, čo nebolo skenované.

Konkrétne GitLab analyzers, templates, UI a policy capabilities sa menia podľa verzie, offeringu a tieru. Návrh preto nesmie stáť iba na predpoklade, že určitá karta v UI existuje; musí definovať subject, evidence, verdict a failure semantics nezávisle od produktu.

## 2. Mental model: coverage, evidence a decision

Security scanning má tri samostatné otázky:

1. **Coverage —** ktoré časti attack surface boli skutočne analyzované?
2. **Evidence —** prebehli relevantné analyzers kompletne a vytvorili validné reporty pre správny subject?
3. **Decision —** aký risk findings predstavujú a čo policy povoľuje?

```text
0 findings
```

môže znamenať:

- subject je čistý,
- scanner nepodporuje daný jazyk,
- job bol vylúčený cez `rules`,
- scanner nenašiel build input,
- report sa nevytvoril,
- report schema nebola spracovaná,
- analyzoval sa nesprávny image tag,
- vulnerability databáza bola neaktuálna.

Absencia findings je bezpečnostný dôkaz iba vtedy, keď je coverage a execution validita známa.

## 3. Security subject identity

Každý scan musí byť viazaný na presný subject.

Možné subjects:

- source commit alebo merged-result SHA,
- dependency graph/lockfile revision,
- SBOM digest,
- container image digest,
- package version a checksum,
- IaC source alebo rendered plan,
- API schema revision,
- environment URL plus deployment digest/config,
- GitLab Release manifest.

Tag, branch alebo URL bez immutable revision je slabá identity. Container scan nad `app:latest` nemusí analyzovať bytes, ktoré sa neskôr nasadia.

## 4. Attack-surface a scanner coverage model

Vytvor explicitnú mapu:

| Attack surface | Primárna kontrola | Doplnková kontrola | Typický limit |
|---|---|---|---|
| Source data flow | SAST | review, tests, DAST | framework/runtime context |
| Dependencies | dependency scanning/SBOM | container scan | neúplný resolution graph |
| Committed secrets | secret detection/push protection | provider audit | neznáme custom formats |
| Runtime image | container scan | signature/provenance policy | packages mimo databázy |
| Web/API runtime | DAST/API testing | manual pentest | route/auth coverage |
| IaC deklarácia | IaC scanning | plan/runtime policy | effective cloud drift |
| Licenses/supply chain | SBOM/license policy | supplier review | metadata kvalita |

Coverage model má byť prispôsobený jazykom, build systému, deployment architektúre a threat modelu projektu.

## 5. Expected scanner inventory

Pre každý project alebo release class definuj očakávané scanners, napríklad:

```text
backend service:
- SAST
- dependency/SBOM
- secret detection
- container scanning
- API scan v stagingu
- IaC scan pre deployment manifests
```

Pipeline má vedieť dokázať:

- ktoré scanners boli applicable,
- ktoré jobs vznikli,
- ktoré sa dokončili,
- ktoré reporty boli prijaté,
- ktoré boli zámerne skipped,
- ktoré zlyhali technicky,
- ktoré neboli podporované.

Chýbajúci expected scanner je `incomplete evidence`, nie čistý výsledok.

## 6. Scan execution contexts

Scans môžu bežať v rôznych kontextoch:

- **Pre-commit/push protection —** okamžitá prevencia vybraných secret alebo policy chýb.
- **Merge-request pipeline —** diff-oriented feedback pred merge.
- **Merged-results alebo merge-train pipeline —** evidence nad kandidátnym integračným stavom.
- **Default-branch pipeline —** autoritatívny baseline po integrácii.
- **Artifact/release pipeline —** scan výsledného package alebo image digestu.
- **Scheduled scan —** nové advisories a hlbšie pravidlá bez source zmeny.
- **Environment/DAST scan —** runtime behavior konkrétneho deploymentu.
- **Continuous rescan —** prehodnotenie SBOM alebo image inventory podľa novej intelligence.

Výsledky z rôznych contexts nie sú automaticky zameniteľné. Source scan feature branchu nie je scan release image digestu.

## 7. Execution validity

Scanner job je platný iba ak:

- dostal očakávaný subject,
- mal potrebné source/build metadata,
- analyzer image a ruleset sú známe,
- vulnerability/advisory data boli dostupné,
- job dokončil analýzu bez skrytého fallbacku,
- report vznikol,
- report schema je podporovaná,
- report bol uploadnutý a spracovaný,
- všetky shards alebo components sú zahrnuté.

Rozlišuj verdicty:

- **Clean —** platný scan nenašiel findings v deklarovanom coverage.
- **Findings —** platný scan našiel výsledky.
- **Incomplete —** chýba subject, component, shard alebo report.
- **Invalid —** scan bežal nad nesprávnym inputom alebo nepoužiteľným configom.
- **Tool error —** analyzer, registry, runner alebo advisory service zlyhal.
- **Unsupported —** attack surface nemá podporovaný analyzer.
- **Skipped by policy —** zámerné vynechanie s dôvodom a ownerom.

## 8. Security report artifacts

GitLab analyzers publikujú machine-readable reporty. Report je kontrakt medzi scannerom a GitLab processing vrstvou.

Report evidence má obsahovať alebo umožniť odvodiť:

- scanner a version,
- ruleset/config revision,
- subject identity,
- scan timestamp,
- report schema version,
- component inventory,
- finding identifiers a locations,
- execution status,
- artifact checksum.

Zelený job s neprijatým reportom nesmie byť interpretovaný ako úspešný security gate.

## 9. SAST

Static Application Security Testing analyzuje source alebo build representation bez útoku na bežiaci systém. Môže používať syntax, AST, data-flow, call graph alebo taint analysis.

SAST typicky hľadá:

- injection flows,
- path traversal,
- insecure deserialization,
- nebezpečné API použitie,
- hardcoded cryptography alebo weak algorithms,
- source-to-sink taint,
- niektoré authorization a validation chyby.

Limity:

- nepodporovaný jazyk/framework,
- chýbajúci generated code alebo build context,
- dynamické dispatch a metaprogramming,
- konfigurácia mimo repository,
- custom sanitizers,
- runtime identity a deployment policy.

SAST coverage eviduj podľa languages, directories, excluded paths a analyzer applicability.

## 10. Dependency scanning

Dependency scanning hľadá známe vulnerabilities v direct a transitive dependencies.

Dôveryhodný input je resolved dependency graph, nie iba voľný manifest. Potrebné môžu byť:

- lockfile,
- package-manager metadata,
- vendored components,
- generated dependency graph,
- SBOM,
- advisory database revision.

Kontroluj:

- či sa analyzovali production aj relevantné build dependencies,
- private registries,
- platform-specific variants,
- optional a peer dependencies,
- monorepo workspaces,
- package aliases a overrides.

## 11. SBOM

Software Bill of Materials eviduje components, versions, package identifiers a relationships.

SBOM pomáha pri:

- vulnerability matching,
- incident response,
- release evidence,
- supplier inventory,
- continuous rescanning,
- dependency a license governance.

SBOM nie je dôkaz bezpečnosti ani provenance. Musí byť:

- viazaný na konkrétny artifact digest,
- generovaný z relevantného build alebo final image contextu,
- kontrolovaný na completeness,
- chránený pred neautorizovanou zmenou,
- doplnený build provenance.

Dva SBOM-y pre rovnaký source môžu byť rozdielne pre rôzne platformy alebo build variants.

## 12. Container scanning

Container scanning má analyzovať konkrétny OCI image digest alebo platform manifest.

Rozlišuj:

- OS packages,
- language dependencies vo final image,
- base-image lineage,
- packages iba v build stage,
- static binaries a embedded libraries,
- multi-platform variants.

Pri multi-platform image musí expected inventory potvrdiť, že každý podporovaný manifest bol analyzovaný alebo má explicitne zdokumentované coverage.

Tag môže slúžiť na lookup, ale report a policy musia byť viazané na digest.

## 13. Dependency verzus container scanning

Tieto kontroly odpovedajú na odlišné otázky:

- dependency scan skúma deklarovaný/resolved software graph,
- container scan skúma obsah výsledného runtime artifactu.

Rozdiely odhaľujú:

- dependency pridanú mimo lockfile,
- package odstránený multi-stage buildom,
- OS-level vulnerability,
- neúplný SBOM,
- rozdiel build a runtime variantu.

Release gate môže vyžadovať obe evidence, ak sa distribuuje container image.

## 14. Secret detection

Secret detection hľadá credential-like patterns v source history, diff-e alebo ďalších podporovaných contexts.

Vrstvenie:

- IDE/pre-commit kontrola,
- push protection,
- MR/default-branch scan,
- historical scan,
- provider-side usage/anomaly monitoring.

Pri reálnom secre­te:

```text
revoke alebo disable
→ rotate
→ identifikuj exposure window
→ audituj použitie
→ oprav source/config
→ vyčisti history podľa potreby
→ pridaj prevention/regression
```

Dismissal findingu nie je revokácia credentialu. Vymazanie z posledného commitu neruší kópie v histórii, artifacts, logs alebo klonoch.

## 15. DAST

Dynamic Application Security Testing posiela requests na bežiacu aplikáciu a pozoruje runtime behavior.

DAST contract obsahuje:

- presný environment a deployment digest,
- allowed scope a routes,
- test identity a role,
- seed/test data,
- authentication lifecycle,
- rate a concurrency limits,
- povolené mutation typy,
- cleanup,
- abort criteria,
- network origin,
- evidence retention.

DAST nesmie neúmyselne testovať produkčné payments, emaily alebo deštruktívne operácie. Environment musí byť pripravený na scan workload.

## 16. API security testing

API security test potrebuje explicitný surface:

- OpenAPI alebo GraphQL schema,
- route inventory,
- recorded traffic podľa nástroja,
- authentication contexts,
- object/tenant test data.

Overuje napríklad:

- authentication,
- object-level a function-level authorization,
- tenant isolation,
- input a schema validation,
- rate limits,
- error leakage,
- unexpected methods alebo fields.

Jedna privileged test identity nemôže potvrdiť authorization matrix. Potrebné sú identity s rozdielnymi scopes a negatívne scenáre.

## 17. Infrastructure as Code scanning

IaC scan analyzuje deklarácie pre cloud, Kubernetes, containers alebo automation.

Typické findings:

- public exposure,
- excessive IAM,
- weak encryption,
- privileged workloads,
- chýbajúce logging controls,
- permissive security groups,
- risky defaults.

Source scan nevidí vždy:

- rendered plan,
- inherited organization policy,
- admission mutations,
- provider defaults,
- runtime drift,
- manuálne resources.

Pre kritickú infra zmenu vrstvi source scan, plan policy a runtime verification.

## 18. License a compliance evidence

License alebo compliance kontrola závisí od presného component inventory a policy.

Potrebné je rozlišovať:

- deklarovanú versus skutočne distribuovanú dependency,
- direct a transitive packages,
- source a binary distribution,
- package version a license metadata kvalitu,
- schválené exceptions.

Neúplný SBOM môže vytvoriť false compliance pass.

## 19. Finding identity a deduplication

Finding identity môže byť odvodená z kombinácie:

- scanner/rule identifier,
- component/package identity,
- file/location alebo data-flow fingerprint,
- vulnerability identifier,
- subject revision.

Slabá deduplication vytvára duplicitný backlog. Príliš agresívna deduplication môže zlúčiť odlišné paths alebo artifacts.

Pri presune kódu, dependency upgrade alebo scanner rule update zachovaj traceability medzi starým a novým findingom.

## 20. Finding verzus vulnerability record

- **Finding —** výsledok konkrétneho scanu konkrétneho subjectu.
- **Vulnerability record —** dlhšie žijúci spravovaný security problém s ownerom, stavom, SLA, exception a remediation históriou.

Lifecycle môže zahŕňať:

```text
needs triage
→ confirmed
→ remediation planned
→ resolved
→ verified
→ re-detected
```

Dismissal musí mať kategóriu, dôvod, approvera, scope a podľa rizika expiráciu.

## 21. Triage a contextual risk

Severity nie je kompletný risk model. Triage zohľadňuje:

- reachability,
- exploitability,
- internet alebo tenant exposure,
- privilege a data sensitivity,
- deployed status,
- available fix,
- compensating controls,
- business impact,
- active exploitation,
- confidence scanneru.

Nová critical vulnerability v nepoužitom test tooli môže mať iné priority než high vulnerability v internet-facing runtime dependency.

## 22. Baseline a merge-request delta

MR feedback má odlíšiť:

- existing baseline,
- newly introduced finding,
- changed severity alebo reachability,
- resolved finding,
- scanner/ruleset-induced reclassification.

Baseline musí byť čerstvý voči aktuálnemu target branchu. Stará alebo chýbajúca default-branch evidence môže nesprávne označiť finding ako nový alebo ho prehliadnuť.

Merged-results alebo merge-train context môže byť potrebný, ak scan závisí od integrácie source a target stavu.

## 23. Security gate verdicts

Gate nemá používať iba `job passed/failed`. Potrebuje rozlíšiť:

- evidence complete a clean,
- evidence complete s blocking findings,
- evidence complete s advisory findings,
- incomplete scanner inventory,
- invalid subject/report,
- analyzer/tool failure,
- stale baseline alebo intelligence,
- exception/waiver,
- inconclusive human triage.

Príklad:

```text
new reachable critical in deployed component
→ block

existing accepted medium s platnou exception
→ visible, neblokuje

required scanner chýba
→ incomplete, nepromovať

advisory database outage
→ policy-defined pause alebo break-glass
```

## 24. Policy composition

Security policy môže určovať:

- ktoré scanners sa musia spustiť,
- pre ktoré projects/branches/environments,
- blocking thresholds,
- required approvers,
- exception rules,
- schedule rescans,
- vulnerability-management actions.

Pri viacerých policies over:

- applicability,
- precedence alebo kombináciu,
- group/project inheritance,
- policy repository revision,
- effective resolved policy,
- fallback pri nevyhodnotiteľnom stave.

Policy repository je privileged governance boundary a potrebuje chránený merge proces a audit.

## 25. Blocking verzus advisory režim

Blocking gate je vhodný, keď:

- coverage je dostatočne známa,
- signal je stabilný,
- finding identity a baseline fungujú,
- remediation je akčná,
- tool failure semantics sú definované,
- exception proces je dostupný.

Nový alebo hlučný scanner môže začať advisory režimom s baseline a tuningom. Advisory však potrebuje ownera a plán, či sa stane blocking, zostane trendovým signalom alebo sa odstráni.

## 26. Exceptions a dismissals

Exception obsahuje:

- finding/vulnerability identity,
- affected subject/component,
- technický a business dôvod,
- contextual risk,
- compensating controls,
- ownera,
- approvera,
- expiration/review date,
- remediation plan,
- evidence odkazy.

Exception musí byť prehodnotená pri:

- novom release,
- zmene exposure,
- novej exploit intelligence,
- ruleset alebo finding zmene,
- vypršaní compensating controlu.

## 27. Analyzer supply chain

Analyzer image, CI template, ruleset a vulnerability database sú supply-chain dependencies.

Chráň:

- immutable alebo riadene versionované analyzer images,
- template refs,
- registry provenance,
- signatures/checksums,
- update ownership,
- runner isolation,
- source a secret access,
- outbound network,
- advisory database integrity.

Scanner často dostáva celý source a niekedy build credentials. Kompromitovaný analyzer môže exfiltrovať viac než aplikácia, ktorú skúma.

## 28. Analyzer update lifecycle

Aktualizácia analyzera môže zmeniť:

- findings,
- severity,
- fingerprints,
- supported language coverage,
- report schema,
- runtime a memory nároky,
- false-positive rate.

Bezpečný rollout:

1. pinuj current version,
2. otestuj novú verziu na fixture projektoch,
3. porovnaj report delta,
4. vyhodnoť performance a compatibility,
5. rolloutuj canary skupine projektov,
6. aktualizuj baseline/policy,
7. monitoruj invalid a tool-error rate.

## 29. Scanner compromise response

Pri podozrení na kompromitovaný analyzer/template:

- zastav affected jobs alebo odpoj credentials,
- revokuj runner/cloud/registry tokens dostupné scanneru,
- identifikuj projekty a pipelines, kde bežal,
- audituj outbound traffic, logs a artifacts,
- označ evidence za nedôveryhodnú,
- obnov trusted analyzer a ruleset,
- znovu skenuj release subjects,
- prehodnoť artifacts podpísané alebo publikované v tom istom trust contexte.

## 30. Continuous rescanning

Nová vulnerability môže vzniknúť bez source zmeny. Continuous rescan potrebuje inventory:

```text
SBOM/package/image digest
→ release manifest
→ deployments/environments
→ service owner
→ exposure a criticality
```

Pri novej advisory:

1. identifikuj dotknuté component versions,
2. nájdi release artifacts a deployed digests,
3. zohľadni reachability a exposure,
4. vytvor vulnerability record a ownera,
5. rebuildni patched immutable artifact,
6. over a redeploy,
7. aktualizuj support/revocation stav.

Skenovanie iba default branchu nestačí, ak produkcia stále používa starší release digest.

## 31. Deployed-artifact correlation

Security dashboard má vedieť odpovedať:

- ktorý vulnerable digest je publikovaný,
- ktorý je súčasťou podporovaného release,
- kde je nasadený,
- aký traffic/cohort ho používa,
- či existuje fix,
- kto je owner,
- či platí exception.

Source vulnerability po oprave v main môže zostať aktívna v produkcii, kým sa nevytvorí a nenasadí nový artifact.

## 32. Scan performance a selection

Optimalizácie:

- affected-component selection,
- parallel scanners,
- shallow/deep scan profily,
- scheduled full scans,
- scanner cache v oddelenom trust namespace,
- reuse SBOM pri rovnakom immutable artifacte,
- DAST scope a sampling.

Selection vytvára false-negative riziko. Zmena shared build image, template, lock resolution alebo generated code môže ovplyvniť komponenty mimo path diffu. Periodický full scan overuje selection assumptions.

## 33. DAST a destructive-test safety

Runtime scan potrebuje safety state machine:

```text
prechecks
→ authenticate
→ scope validation
→ scan active
→ guardrail monitoring
→ stop/abort
→ cleanup
→ environment validation
```

Abort criteria môžu zahŕňať:

- error alebo latency limit,
- neplánovaný external side effect,
- scan mimo allowlist routes,
- rate-limit impact,
- test-data leakage,
- environment instability.

## 34. Security telemetry

Sleduj:

- expected verzus executed scanner coverage,
- scanner success/tool-error/incomplete rate,
- missing alebo invalid reports,
- scan duration a critical path,
- findings podľa subject a exposure,
- time to triage a remediate,
- exception count a age,
- re-detected findings,
- false-positive a selection-miss rate,
- percent release artifacts so SBOM/provenance/scans,
- deployed vulnerable digests,
- continuous-rescan latency,
- analyzer version drift.

Počet findings bez coverage a remediation kontextu nie je dobrá metrika bezpečnosti.

## 35. Diagnostický postup

Keď security výsledok chýba alebo je podozrivý:

1. **Urči subject —** commit, image digest, package, plan alebo environment.
2. **Urči expected scanners —** podľa languages, artifacts a attack surface.
3. **Over pipeline creation —** `workflow`, job `rules`, policy applicability a tier/capability.
4. **Over execution —** analyzer image, inputs, exit status, logs a advisory data.
5. **Over report —** path, schema, checksum, upload a GitLab processing.
6. **Over baseline —** target-branch freshness a merged-result context.
7. **Over identity —** report sa vzťahuje na správny digest/version.
8. **Rozlíš verdict —** clean, findings, incomplete, invalid alebo tool error.
9. **Skontroluj policy —** effective rules, exceptions a approver eligibility.
10. **Skontroluj deployment correlation —** či affected subject reálne beží.
11. **Uchovaj evidence —** analyzer/ruleset version, reporty a timeline.
12. **Oprav systémovo —** coverage, config, policy, scanner alebo remediation lifecycle.

## 36. Typické anti-patterny

### Zelený pipeline = bez vulnerabilities

Scanner mohol byť skipped, unsupported alebo nevytvoriť report.

### Jeden scanner pre celý attack surface

SAST nevidí runtime image, DAST nevidí všetok source a IaC scan nevidí effective drift.

### Scan tagu namiesto digestu

Evidence môže patriť iným bytes než deployment.

### Gate podľa celkového počtu findings

Legacy baseline blokuje každú zmenu alebo motivuje k permanentným bypassom.

### `Block all high` bez kontextu

Ignoruje reachability, exposure, confidence, fix a compensating controls.

### Dismissal bez expirácie

Dočasné risk rozhodnutie sa stane neviditeľným permanentným debtom.

### Security template na mutable branch

Scanner behavior sa mení bez zmeny consumer repository a bez auditovateľného rollout-u.

### Continuous rescan iba nad main

Staršie produkčné releases zostávajú mimo vulnerability inventory.

### DAST proti produkcii bez safe scope

Scanner môže vytvoriť skutočné side effects alebo incident.

## 37. Praktický rozhodovací rámec

Pre každý security control odpovedz:

1. Aký attack surface a threat chráni?
2. Aký je immutable scan subject?
3. Kedy je scanner applicable a čo nepokrýva?
4. Aký expected scanner/report inventory sa vyžaduje?
5. Ako sa rozlíši clean, incomplete, invalid a tool error?
6. Aký baseline sa používa pre MR delta?
7. Ako sa zohľadňuje severity, reachability a exposure?
8. Kedy je gate blocking a kedy advisory?
9. Čo sa stane pri scanner outage alebo stale intelligence?
10. Kto vlastní finding a remediation SLA?
11. Ako funguje exception a expirácia?
12. Ako sa scanner/template bezpečne aktualizuje?
13. Ako sa findings mapujú na release a deployed digest?
14. Ako sa nové advisories spracujú bez source zmeny?
15. Aký incident postup existuje pri kompromitovanom analyzeri?

## 38. Kontrolný checklist

- attack-surface coverage mapa existuje;
- expected scanners sú definované podľa project/release class;
- scan subject je immutable;
- scanner jobs používajú trusted pinned/controlled dependencies;
- report schema a upload sa validujú;
- missing scanner/report je incomplete evidence;
- MR baseline je čerstvý;
- container/SBOM results sa viažu na digest;
- multi-platform variants majú kompletný inventory;
- secret finding spúšťa revoke/rotate workflow;
- DAST má safe target, identity, scope a cleanup;
- policy rozlišuje findings, tool error a unsupported coverage;
- exceptions majú ownera a expiráciu;
- vulnerability records majú remediation SLA;
- deployed-artifact correlation funguje;
- continuous rescanning zahŕňa podporované releases;
- analyzer update a compromise postup sú testované;
- telemetry sleduje coverage aj remediation, nie iba počet findings.

## 39. Kontrolné otázky

1. Aké tri otázky oddeľuje model coverage, evidence a decision?
2. Prečo nula findings nemusí znamenať čistý subject?
3. Čo tvorí security scan subject?
4. Ako expected scanner inventory odhalí skipped job?
5. Aký je rozdiel medzi incomplete, invalid a tool-error scanom?
6. Prečo dependency a container scanning nie sú zameniteľné?
7. Čo SBOM poskytuje a čo neposkytuje?
8. Ako reagovať na reálne commitnutý secret?
9. Čo musí obsahovať bezpečný DAST contract?
10. Aký je rozdiel medzi findingom a vulnerability recordom?
11. Ako baseline freshness ovplyvňuje MR feedback?
12. Prečo severity nestačí na risk decision?
13. Ako sa skladajú security policies?
14. Čo musí obsahovať exception?
15. Prečo analyzer predstavuje supply-chain boundary?
16. Ako continuous rescanning nájde problém v staršom release?
17. Prečo oprava v main neznamená opravenú produkciu?
18. Ako sa diagnostikuje zelený job bez reportu?

## Summary

GitLab security scanning je lifecycle od attack-surface modelu cez applicable analyzers a validné reporty až po contextual risk decision, remediation a continuous rescanning. Dôveryhodný systém viaže scan na immutable source, package, image, plan alebo deployment subject, rozlišuje clean, findings, incomplete, invalid a tool-error stavy a eviduje očakávanú coverage. Findings sa menia na spravované vulnerability records s ownerom a exception lifecycle. Security policy musí pracovať s čerstvým baseline, reachability a exposure a continuous rescan musí mapovať nové advisories na podporované releases a skutočne nasadené digests. Analyzers a templates sú samostatná supply-chain boundary.

## Glossary impact

Relevantné pojmy: GitLab SAST, dependency scanning, container scanning, secret detection, DAST, API security testing, IaC scanning, security report artifact, expected scanner inventory, scan subject, scan coverage, finding, vulnerability record, security policy, exception, continuous rescanning, deployed-artifact correlation a analyzer supply chain.

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

[← Predchádzajúca: Environments, deployments a releases](environments-deployments-releases.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Infrastructure as Code principles →](../07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md)
<!-- KNOWLEDGE-NAVIGATION:END -->