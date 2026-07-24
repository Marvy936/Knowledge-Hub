# Security a infrastructure tests

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

Security testing overuje, či systém odoláva konkrétnym hrozbám a či bezpečnostné kontroly fungujú pri pozitívnych aj negatívnych scenároch. Infrastructure testing overuje, či deklarovaná aj efektívna infraštruktúra spĺňa technické, bezpečnostné a prevádzkové invariants.

```text
threat alebo infrastructure risk
→ control
→ test
→ evidence
→ remediation alebo risk decision
```

Scanner output ani syntakticky platný manifest nie sú samy osebe dôkazom bezpečnosti. Dôveryhodná stratégia prepája threat model, control ownership, viac vrstiev testov, runtime enforcement a riadený lifecycle findings.

## 1. Mentálny model

Security a infrastructure test má odpovedať na päť otázok:

1. Aký asset alebo prevádzkový výsledok chránime?
2. Pred akým actorom, failure alebo misconfiguration?
3. Ktorá kontrola má riziko znížiť?
4. Aký test dokáže, že kontrola funguje alebo zlyhá?
5. Aké rozhodnutie a remediation nasledujú z výsledku?

Bez týchto otázok organizácia často spúšťa veľa nástrojov, ale nevie, ktoré riziká sú reálne pokryté a ktoré zostávajú bez dôkazu.

## 2. Security verzus infrastructure testing

Security test sa primárne pýta, či možno systém zneužiť, obísť kontrolu alebo získať neprípustný prístup. Infrastructure test sa pýta, či je desired a effective state správny, stabilný a prevádzkyschopný.

Príklad jednej oblasti z dvoch pohľadov:

```text
Infrastructure test:
security group povoľuje iba definované CIDR a porty

Security test:
neautorizovaný source sa na management port skutočne nepripojí
```

Statická konfigurácia a dynamický enforcement dôkaz sa dopĺňajú.

## 3. Threat-informed testing

Security test selection má vychádzať z threat modelu:

```text
assets
→ actors
→ entry points
→ trust boundaries
→ attack paths a abuse cases
→ controls
→ residual risk
→ evidence plan
```

Threat model nemusí byť rozsiahly diagram. Musí však zachytiť, čo má hodnotu, kde sa mení dôvera, kto môže útočiť a aký dopad má úspešný útok.

## 4. Assets a security properties

Asset nie je iba databáza alebo server. Assetom môže byť:

- customer data,
- identity a authorization decision,
- signing key,
- CI runner,
- release artifact,
- availability kritického workflowu,
- auditná stopa,
- infrastructure control plane,
- backup a recovery capability.

Pre každý asset definuj požadované properties: confidentiality, integrity, availability, authenticity, accountability a podľa potreby privacy.

## 5. Trust boundaries

Trust boundary je miesto, kde sa mení identity, ownership, privilege alebo dôveryhodnosť vstupu. Typické boundaries:

- internet → edge proxy,
- user session → backend authorization,
- service → service,
- tenant → shared storage,
- CI job → cloud account,
- workload → metadata service,
- cluster namespace → node,
- control plane → managed resource,
- backup system → restore environment.

Security testy majú prioritizovať práve prechody cez boundaries, pretože lokálne správne komponenty môžu vytvoriť zraniteľnú integráciu.

## 6. Abuse cases

Abuse case opisuje zámerne škodlivé alebo neprípustné použitie systému. Napríklad:

```text
Actor: autentifikovaný používateľ tenanta A
Goal: načítať objednávku tenanta B
Path: zmeniť resource ID v API requeste
Control: object-level authorization a tenant-scoped query
Evidence: negatívny API a database integration test
```

Taký scenár je presnejší než všeobecná požiadavka „testovať authorization“.

## 7. Control-to-evidence mapa

Pre významné riziká udržiavaj mapu:

| Riziko | Preventívna kontrola | Detekčná kontrola | Test | Runtime dôkaz |
|---|---|---|---|---|
| Cross-tenant access | tenant-scoped authorization | audit anomaly | API a DB negative test | audit logs |
| Public storage | IaC policy | cloud config monitoring | plan a runtime test | inventory finding |
| Tampered artifact | signature verification | provenance audit | deploy admission test | deployment record |
| Credential theft | short-lived identity | unusual login alert | expiry/revocation test | identity logs |

Mapa odhaľuje kontroly, ktoré existujú iba na papieri alebo majú test bez runtime pozorovateľnosti.

## 8. Statické a dynamické security vrstvy

Žiadna vrstva nepokrýva všetky triedy problémov. Kombinuj:

- source a data-flow analysis,
- dependency a artifact analysis,
- configuration a IaC policy,
- runtime API a protocol testy,
- identity a authorization testy,
- cloud a platform enforcement testy,
- manual review a penetration testing,
- produkčné detection a response validation.

Cieľom nie je maximalizovať počet scannerov, ale znížiť relevantné residual risk.

## 9. SAST

Static Application Security Testing analyzuje source, bytecode alebo intermediate representation bez potreby spustiť aplikáciu.

Môže hľadať:

- source-to-sink injection flow,
- unsafe deserialization,
- insecure cryptographic API,
- hardcoded credentials,
- path manipulation,
- authorization checks chýbajúce v známom pattern-e,
- memory-safety alebo concurrency chyby podľa jazyka.

SAST môže analyzovať neaktivované code paths, ale často nevie presne runtime configuration, reachability a business intent. Výsledok potrebuje triage.

## 10. DAST

Dynamic Application Security Testing testuje bežiace rozhranie zvonka. Vie odhaliť observable behavior ako injection, session chyby, security headers, authentication bypass alebo nebezpečné error responses.

DAST nevidí automaticky všetky code paths a kvalita závisí od crawl-u, authentication setupu, test data a API definition. Neautentifikovaný scan verejnej landing page neposkytuje dôkaz o chránených business API.

## 11. IAST a runtime instrumentation

Interactive Application Security Testing kombinuje runtime test s internou instrumentáciou. Počas vykonania môže sledovať data flow, používanie knižníc a konkrétny sink.

IAST poskytuje viac kontextu než black-box DAST, no pokrýva iba paths vykonané test suite. Slabá funkčná coverage znamená slabú bezpečnostnú coverage.

## 12. SCA

Software Composition Analysis vytvára dependency graph a porovnáva components so známymi vulnerabilities, licenses a policy.

Dôveryhodná SCA musí rozlišovať:

- direct a transitive dependency,
- build-time a runtime component,
- package version a artifact digest,
- fixed version dostupnosť,
- reachable a nereachable vulnerable path,
- exploit prerequisites,
- environment exposure,
- compensating controls.

Závažnosť CVE nie je automaticky rovná organizačnému riziku, ale nejasná reachability nesmie byť dôvodom nález ignorovať bez analýzy.

## 13. Vulnerability, exposure a exploitability

Risk triage môže používať model:

```text
vulnerability
+ component presence
+ reachable code path
+ attacker access
+ required privileges
+ control bypass
+ business impact
= contextual risk
```

Absencia verejného exploit-u znižuje niektoré pravdepodobnosti, ale nedokazuje bezpečnosť. Naopak vysoké CVSS v nepoužitom build-time nástroji môže mať menšie runtime riziko než stredne hodnotená authorization chyba v internetovom API.

## 14. Secret scanning

Secret scanning kontroluje source, Git history, commits, logs, artifacts, image layers, fixtures, backups a konfigurácie.

Nález secretu vyžaduje incidentný postup:

1. overiť, či hodnota je reálna,
2. okamžite ju revoke-nuť alebo rotovať,
3. zistiť exposure interval a access logs,
4. odstrániť secret zo súčasného source,
5. podľa potreby prečistiť históriu a distribuované kópie,
6. opraviť spôsob provisioning-u,
7. pridať prevention a regression control.

Vymazanie stringu z posledného commitu nestačí, ak credential zostáva platný alebo v histórii.

## 15. Supply-chain testing

Supply-chain testy overujú cestu od source po deployment:

```text
source identity
→ reviewed commit
→ dependency resolution
→ trusted build environment
→ artifact digest
→ SBOM a provenance
→ signature
→ registry
→ admission a deployment
```

Kontroluj lockfiles, registry source, dependency confusion, typosquatting, runner trust, build isolation, mutable tags, artifact signing a verification pred nasadením.

## 16. SBOM

Software Bill of Materials eviduje components v konkrétnom artefakte. Test SBOM má overiť:

- SBOM patrí k rovnakému artifact digestu,
- obsahuje direct aj relevantné transitive components,
- formát sa dá parsovať,
- package identity a version sú dostatočné pre vulnerability matching,
- generovanie je súčasťou trusted build procesu,
- SBOM sa uchováva s release evidence.

SBOM je inventory dôkaz, nie automatické potvrdenie bezpečnosti.

## 17. Provenance a signature verification

Podpis má význam iba vtedy, keď verifier pozná dôveryhodnú identity, policy a lifecycle kľúča. Testuj:

- validný artifact je prijatý,
- nepodpísaný artifact je odmietnutý,
- podpis inej identity je odmietnutý,
- zmenený artifact neprejde,
- expired alebo revoked identity má definované semantics,
- admission decision je auditované.

Kontrola, ktorá iba generuje podpis, ale deployment ho neoveruje, neposkytuje enforcement.

## 18. Authentication tests

Authentication testuje dôkaz identity a lifecycle credentials. Negatívne scenáre:

- chýbajúci credential,
- nesprávny formát,
- invalid signature,
- neznámy issuer,
- nesprávny audience,
- expired alebo not-yet-valid token,
- revoked session,
- replay tam, kde je zakázaný,
- neplatný MFA alebo step-up stav,
- certificate mimo trust chain.

Test musí overiť aj bezpečné error semantics bez úniku interných detailov.

## 19. Authorization tests

Authorization testuje, či správna identity smie vykonať konkrétnu action nad konkrétnym resource v danom kontexte.

Vytvor maticu:

```text
subject × action × resource × context → allow alebo deny
```

Context môže obsahovať tenant, ownership, environment, network, čas, resource state a delegated role.

## 20. Object-level a function-level authorization

Overuj oddelene:

- **object-level access —** používateľ nemôže zmeniť ID a načítať cudzí resource,
- **function-level access —** používateľ bez admin role nemôže volať privilegovanú operáciu,
- **field-level access —** response neobsahuje sensitive fields pre nesprávnu rolu,
- **tenant isolation —** query, cache, event a export ostávajú v správnom tenant scope,
- **indirect access —** background worker a generated report zachovávajú rovnakú policy.

UI skrytie buttonu nie je authorization kontrola.

## 21. Privilege escalation a confused deputy

Testuj horizontálnu aj vertikálnu escalation:

- z používateľa na iného používateľa,
- z tenant A do tenant B,
- z bežnej role na admin,
- zo service accountu na cloud control plane,
- cez zneužitie služby s vyšším privilege.

Confused-deputy scenár vzniká, keď privilegovaná služba vykoná operáciu v mene neautorizovaného caller-a bez správneho contextu.

## 22. Input security tests

Testuj vstupy podľa parsera a sinku, nie generickým zoznamom payloadov:

- SQL, command, LDAP a template injection,
- path traversal a archive extraction,
- SSRF a URL parsing,
- unsafe deserialization,
- file upload type, size a storage path,
- header injection a request smuggling boundaries,
- oversized alebo deeply nested payload,
- duplicate keys a parser differentials,
- Unicode a normalization edge cases.

Najsilnejší oracle overuje nielen status, ale aj neprítomnosť side effectu a zachovanie authorization boundary.

## 23. Output a browser security tests

Overuj:

- context-appropriate output encoding,
- Content Security Policy podľa threat modelu,
- cookie flags a session scope,
- clickjacking protection,
- CORS allowlist,
- cache-control pre sensitive response,
- redirect validation,
- leakage v error pages a source maps.

Security header scanner je užitočný, ale nenahrádza behavior test konkrétneho browserového toku.

## 24. Fuzzing

Fuzzing generuje veľké množstvo neočakávaných vstupov a sleduje crashes, hangs, invariant violations alebo nebezpečné behavior.

Definuj:

- target parser alebo API,
- input grammar alebo seed corpus,
- sanitizers a runtime instrumentation,
- resource limits,
- deduplication crashes,
- minimalizáciu reprodukčného inputu,
- regression uloženie nájdeného prípadu.

Fuzzer bez vhodného oracle môže merať iba to, že proces nespadol.

## 25. Infrastructure as Code testovacie vrstvy

IaC má viac transformačných hraníc:

```text
source modules a values
→ templated alebo rendered configuration
→ syntax a schema
→ policy
→ plan alebo change set
→ apply
→ provider/platform mutation
→ effective runtime state
→ operational behavior
```

Každá vrstva môže zlyhať iným spôsobom a potrebuje vlastný dôkaz.

## 26. Syntax a schema

Prvá vrstva odhaľuje parse chyby, chýbajúce required fields a neplatné typy. Príklady zahŕňajú `terraform validate`, Helm render/lint, Kubernetes schema validation a cloud-template validation.

Syntax-valid input stále môže byť nebezpečný, prevádzkovo chybný alebo semanticky nekompatibilný.

## 27. Module a rendering tests

Testuj outputs a invariants reusable modulov:

- naming a tags,
- defaults,
- optional branches,
- dependency wiring,
- rendered resource count,
- environment overrides,
- deterministic output.

Snapshot renderu môže pomôcť, ale kritické security a lifecycle vlastnosti majú mať explicitné assertions.

## 28. Static policy tests

Policy môže vyžadovať:

- storage nie je public,
- management port nie je otvorený širokému internetu,
- encryption je zapnuté,
- production deletion protection je aktívna,
- workload nebeží privileged,
- image je pinovaný digestom,
- required ownership a data-classification tags existujú.

Policy potrebuje pozitívne aj negatívne fixtures. Testuj, že bezpečný input prejde a nebezpečný je odmietnutý správnym pravidlom.

## 29. Plan a change-set testing

Plan testuje konkrétny zamýšľaný rozdiel, nie iba source template. Overuj:

- neočakávané destroys a replacements,
- privilege expansion,
- public exposure,
- zmenu encryption alebo retention,
- resource count a cost skok,
- provider change,
- drift correction s veľkým blast radius,
- ordering a migration prerequisites.

Plan môže obsahovať unknown values; policy musí mať definované správanie pre neistotu a nesmie neznáme automaticky považovať za bezpečné.

## 30. Apply v sandboxe

Ephemeral alebo izolovaný sandbox overí provider API, runtime defaults, dependencies a skutočnú vytvoriteľnosť resources.

Sandbox musí používať:

- oddelený account, project alebo subscription,
- least-privilege test identity,
- resource prefix a tags,
- cost a quota limits,
- cleanup aj pri partial failure,
- zákaz pripojenia k produkčným dátam,
- retention artifacts pri zlyhaní.

## 31. Effective runtime state

Po apply over efektívny stav. Provider defaults, admission mutácie, inherited IAM, organization policy a externý drift môžu zmeniť výsledok oproti source.

Príklady runtime verification:

- bucket public access je reálne blokovaný,
- TLS endpoint používa očakávaný certificate a protocol,
- IAM principal nemôže vykonať zakázanú action,
- network path je z nepovolenej zóny nedostupný,
- workload beží s očakávaným UID a capabilities,
- audit log skutočne vzniká.

## 32. Policy as Code lifecycle

Dobrá policy obsahuje:

- názov a bezpečnostný dôvod,
- scope a applicability,
- allow aj deny examples,
- severity a blocking semantics,
- ownera,
- versioning,
- exception proces,
- remediation message,
- auditovaný výsledok.

Policy bez testov môže vytvoriť false positive alebo tichý bypass. Zmena policy je produkčná zmena a potrebuje review a regression fixtures.

## 33. Enforcement test

Nestačí overiť, že policy súbor existuje. Potrebný je negatívny enforcement test:

```text
predlož zakázaný workload
→ admission alebo CI gate ho odmietne
→ dôvod zodpovedá očakávanej policy
→ bypass nie je dostupný bežnej identity
→ event je auditovaný
```

Taký test odhaľuje policy, ktorá je nainštalovaná, ale nie je priradená správnemu scope-u alebo beží iba v audit režime.

## 34. Cloud IAM tests

Overuj effective permissions, nie iba jednotlivý policy document. Výsledok môže ovplyvniť role inheritance, resource policy, organization controls, permission boundary, session policy a explicit deny.

Test matrix má obsahovať:

- povolenú action,
- zakázanú action,
- access k cudziemu resource,
- privilege delegation,
- credential expiry a revocation,
- cross-account trust,
- workload identity binding,
- audit event.

## 35. Network security tests

Testuj povolené aj zakázané cesty z relevantných source locations:

- ingress a egress,
- IPv4 a IPv6,
- DNS resolution,
- public a private load balancer,
- east-west segmentation,
- management interfaces,
- metadata endpoint,
- mTLS identity,
- certificate rotation,
- stateful return path.

Port scan ukazuje exposure, ale nedokazuje application authorization. Naopak API test z nesprávnej siete môže potvrdiť defense in depth.

## 36. Kubernetes a container tests

Staticky a runtime overuj:

- image digest a trusted registry,
- non-root user,
- read-only root filesystem,
- minimal capabilities,
- seccomp, AppArmor alebo SELinux enforcement,
- host namespace a privileged zákaz,
- resource requests a limits,
- service-account token scope,
- NetworkPolicy,
- secret mounts a file permissions,
- probes a graceful termination,
- admission policy,
- node a runtime configuration.

Manifest s `runAsNonRoot: true` nie je dostatočný dôkaz, ak image vyžaduje root alebo runtime policy nie je enforced.

## 37. Configuration a compliance testing

Compliance requirement prelož na:

```text
requirement
→ technical control
→ machine-testable assertion
→ runtime evidence
→ retention a reviewer
```

Príklady zahŕňajú encryption, retention, audit logging, patch level, time synchronization, backup frequency, access review a separation of duties.

Compliance checkbox bez testu účinnosti je administratívny záznam, nie dôkaz kontroly.

## 38. Backup a restore tests

Existencia úspešného backup jobu dokazuje iba vytvorenie backup artifactu. Recovery test musí overiť:

- restore do izolovaného prostredia,
- dostupnosť encryption keys,
- integrity a completeness,
- application a transaction consistency,
- schema a version compatibility,
- access controls,
- RPO a RTO,
- spustenie aplikácie nad obnovenými dátami,
- audit a cleanup restore prostredia.

Restore drill je zároveň infrastructure, security aj operational acceptance test.

## 39. Resilience a failure security scenáre

Infrastructure a security sa stretávajú pri scenároch:

- expired certificate,
- revoked credential,
- KMS alebo secret-manager outage,
- DNS alebo identity-provider failure,
- disk full,
- denied cloud API,
- rate limit,
- node alebo zone failure,
- prerušený deployment,
- audit pipeline outage.

Test overuje nielen availability, ale aj to, že systém pri degradácii nezlyhá otvorene a neobíde authorization alebo encryption.

## 40. Destructive test safety

Destructive alebo intrusive test potrebuje:

- explicitný target allowlist,
- environment identity assertion,
- maximálny blast radius,
- time a cost limit,
- least-privilege test identity,
- syntetické dáta,
- observability a abort criteria,
- rollback alebo cleanup,
- ownera a komunikačný plán.

Ak target nie je jednoznačne testovací, experiment má zlyhať zatvorene.

## 41. Test identities

Používaj viac identities s minimálnymi oprávneniami podľa scenára. Jeden univerzálny admin účet zakrýva authorization chyby a vytvára neprimeraný incidentný dopad.

Test credentials majú mať krátku expiráciu, audit trail, rotáciu a bezpečný secret provider. Nemajú byť uložené v repository, pipeline outpute ani screenshots.

## 42. Test data a privacy

Testovacie prostredie môže byť bezpečnostným rizikom. Kontroluj:

- zákaz nekontrolovaných produkčných kópií,
- anonymizáciu a reidentifikačné riziko,
- data minimization,
- retention a cleanup,
- access logs,
- encryption,
- export a sharing restrictions,
- secrets a tokens v fixtures.

„Nie je to produkcia“ neznamená, že dáta nie sú citlivé.

## 43. Manual penetration testing

Manuálny penetration test je užitočný pre chained attack paths, business logic, neštandardné protokoly a kreatívne abuse cases, ktoré automatický scanner nepozná.

Potrebuje scope, rules of engagement, test accounts, zakázané actions, reporting, retest a koordináciu s operations. Periodický pentest dopĺňa kontinuálne kontroly; nenahrádza ich.

## 44. Detection a response validation

Security control nie je úplná bez detekcie a reakcie. Testuj:

- relevantný audit event vznikne,
- event obsahuje identity, resource, action a čas,
- pipeline ho doručí bez neprijateľného delay,
- alert má primeranú severity,
- on-call dostane actionable context,
- runbook a containment sú vykonateľné,
- evidence sa uchová podľa policy.

Purple-team alebo game-day scenár môže overiť celý detection-to-response lifecycle.

## 45. Findings triage

Security finding má obsahovať:

1. affected asset, version a environment,
2. presnú evidence a reprodukciu,
3. preconditions a attack path,
4. business a technical impact,
5. severity, confidence a exploitability,
6. existing controls,
7. ownera a remediation,
8. deadline alebo risk acceptance,
9. retest result,
10. väzbu na release alebo exception decision.

Scanner line bez asset contextu a attack pathu nie je pripravený remediation ticket.

## 46. False positives a false negatives

False positive blokuje bezpečnú zmenu a degraduje dôveru v gate. False negative povoľuje rizikový stav a vytvára falošný pocit bezpečnosti.

Meraj:

- confirmed finding rate,
- suppression rate,
- reopen a recurrence,
- defect escape,
- scan coverage,
- mean time to triage,
- exception age.

Tuning nesmie iba znižovať počet findings; musí zachovať citlivosť na relevantné riziká.

## 47. Security quality gates

Blocking gate je vhodný, keď:

- signál má dostatočnú presnosť,
- asset a impact sú známe,
- finding je reprodukovateľný,
- remediation alebo bezpečný exception proces existuje,
- výsledok je dostupný pred chráneným rozhodnutím,
- tool failure má explicitné fail-open alebo fail-closed semantics.

Nový scanner najprv baseline-ni a tune-ni. Okamžitý globálny gate bez ownershipu vytvorí bypass kultúru.

## 48. Tool failure semantics

Rozlišuj:

- scan completed, no findings,
- scan completed with findings,
- scan incomplete,
- rules alebo vulnerability feed sú stale,
- artifact nebol analyzovaný,
- tool alebo license service je unavailable.

`Scanner failed` nesmie byť interpretované ako `no vulnerabilities`. Pipeline musí vedieť, či pri neznámom dôkaze zlyhá zatvorene alebo použije auditovanú výnimku.

## 49. Exceptions a risk acceptance

Exception musí obsahovať:

- konkrétny finding alebo policy,
- asset a scope,
- business dôvod,
- risk ownera,
- compensating controls,
- expiry,
- remediation plán,
- approval,
- periodický review.

Permanentný globálny suppression bez expirácie je obchádzanie kontroly, nie risk management.

## 50. Retest a closure

Finding sa nezatvára iba commitom opravy. Potrebný je retest na správnom artefakte a prostredí.

Over:

- pôvodná reprodukcia už nefunguje,
- nevznikol alternate bypass,
- regression test chráni failure class,
- deployment obsahuje fix,
- temporary compensating control možno odstrániť,
- evidence je pripojená k closure.

## 51. Security test report

Report má obsahovať:

- scope a excluded areas,
- testovaný artifact a environment,
- threat alebo control mapu,
- použité tools a versions,
- authentication a test identities,
- findings s evidence,
- coverage a limity,
- tool failures,
- remediation a retest status,
- residual risk a decision.

Zelený summary bez scope-u a limitation notes je slabý dôkaz.

## 52. Diagnostika nálezu

1. Potvrď artifact, component a version.
2. Over, že finding nie je parser alebo inventory chyba.
3. Zisti runtime presence a reachability.
4. Rekonštruuj attacker preconditions a trust boundary.
5. Over exposure a existing controls.
6. Reprodukuj najbezpečnejším dostatočným spôsobom.
7. Urči impact a blast radius.
8. Rozhodni remediation, mitigation alebo risk acceptance.
9. Pridaj regression test a runtime detection podľa potreby.
10. Retestuj nasadený fix.

## 53. Diagnostika IaC a policy failure

1. Identifikuj source, rendered output a plan.
2. Urči, na ktorej transformačnej vrstve vznikla chyba.
3. Zobraz presnú resource path a effective value.
4. Rozlíš source default, environment override, provider default a platform mutation.
5. Over policy scope, mode a exception.
6. Pri runtime rozdiele skontroluj drift a inherited controls.
7. Oprav najvyšší autoritatívny source, nie iba efektívny resource ručne.
8. Pridaj allow aj deny regression fixture.

## 54. Časté anti-patterny

### Scanner prešiel, systém je bezpečný

Každý tool pokrýva iba časť attack surface a môže mať false negatives.

### CVE severity je naše riziko

Chýba runtime presence, reachability, exposure a business impact.

### Validné IaC znamená bezpečný deployment

Syntax neoveruje policy, plan, effective state ani behavior.

### Policy existuje, preto je enforced

Potrebný je negatívny admission alebo runtime test.

### Podpis sa generuje, ale neoveruje

Supply-chain kontrola nemá enforcement boundary.

### Všetky testy používajú admin účet

Authorization matrix sa v skutočnosti netestuje.

### Pentest raz ročne stačí

Source, dependencies, configuration a exposure sa menia kontinuálne.

### Test environment môže obsahovať produkčné dáta

Nechránená kópia môže vytvoriť rovnaký alebo väčší privacy incident.

### Scanner outage znamená zelený gate

Neznámy dôkaz sa nesmie vydávať za úspech.

## 55. Prevádzkový checklist

Pred zaradením security alebo infrastructure testu do gate over:

- test má väzbu na threat, invariant alebo compliance control,
- asset a trust boundary sú známe,
- scope a excluded paths sú zdokumentované,
- artifact a environment provenance sa ukladajú,
- authentication a test identities sú bezpečné,
- pozitívne aj negatívne scenáre existujú,
- IaC sa testuje od source po effective state,
- policy enforcement je overený zakázaným inputom,
- destructive tests majú allowlist a abort,
- findings majú ownera, deadline a retest,
- tool failure semantics sú explicitné,
- exceptions majú scope a expiry,
- secrets a osobné dáta sa neukladajú do artifacts,
- výsledok podporuje jasné release alebo risk rozhodnutie.

## 56. Zhrnutie

Security a infrastructure testing je systém dôkazov, nie kolekcia scannerov. Začína threatom alebo desired-state invariantom, mapuje ho na preventívne a detekčné kontroly a overuje source, dependencies, artifact, plan, runtime enforcement aj operational response. Dôveryhodný proces kontextualizuje exploitability, chráni test identities a dáta, bezpečne riadi destructive experiments, triaguje findings, časovo obmedzuje exceptions a zatvára nález až po reteste nasadeného fixu.

## 57. Kontrolné otázky

1. Ako threat model riadi výber security testov?
2. Aký je rozdiel medzi SAST, DAST, IAST a SCA?
3. Prečo CVE severity nie je automaticky organizačné riziko?
4. Čo musí overiť SBOM a provenance test?
5. Ako navrhneš subject-action-resource-context authorization maticu?
6. Prečo UI skrytie nie je authorization kontrola?
7. Aké vrstvy má IaC testovací lifecycle?
8. Prečo plan test nenahrádza effective runtime verification?
9. Ako dokážeš, že Policy as Code je reálne enforced?
10. Aké guardrails potrebuje destructive infrastructure test?
11. Kedy má security finding blokovať pipeline?
12. Ako sa líši scanner failure od úspešného scan-u bez findings?
13. Čo musí obsahovať risk exception?
14. Kedy možno finding považovať za uzavretý?

## Glossary impact

Relevantné pojmy: threat model, asset, trust boundary, abuse case, control-to-evidence map, SAST, DAST, IAST, SCA, vulnerability reachability, exploitability, secret scanning, SBOM, artifact provenance, object-level authorization, Policy as Code, effective runtime state, admission enforcement, security finding, risk acceptance a retest.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Performance, load a stress tests](performance-load-stress-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Static analysis, linting a type checking →](static-analysis-linting-type-checking.md)
<!-- KNOWLEDGE-NAVIGATION:END -->