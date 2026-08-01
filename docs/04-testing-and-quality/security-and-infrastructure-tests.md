# Security a infrastructure tests

Security testing overuje, či definované threats a abuse cases sú blokované alebo detegované. Infrastructure testing overuje deklarovaný a effective stav infraštruktúry, policy a runtime boundaries. Ani jedno nie je jeden scanner ani jednorazový audit.

Threat-informed prístup začína assetom, actorom, trust boundary a možným dopadom:

```text
asset
→ threat actor a capability
→ attack path
→ preventive alebo detective control
→ test oracle
→ evidence
```

Application security môže zahŕňať authentication, authorization, input handling, session lifecycle a business abuse. Supply-chain tests kontrolujú dependencies, artifacts, signatures a provenance. Infrastructure tests pokrývajú IAM, network exposure, encryption, secrets, runtime privileges a drift.

IaC potrebuje viac vrstiev evidence:

```text
syntax a parse
→ schema a provider validation
→ policy nad desired state-om
→ plan/change review
→ apply result
→ runtime effective-state verification
```

Zelený Terraform plan nepreukazuje, že cloud resource je reachable iba povolenou cestou. Runtime probe a platform read-back sú odlišné dôkazy.

SAST analyzuje source alebo intermediate representation bez spusteného systému. DAST testuje bežiacu aplikáciu zvonka. SCA identifikuje známe dependency riziká. Artifact a container scanning kontroluje výsledný deliverable. Finding potrebuje triage podľa reachability, exploitability, environmentu a impactu.

Neutrálny authorization test: user A vytvorí resource a user B sa ho pokúsi prečítať a zmeniť. Oracle musí overiť denial aj absenciu side effectu alebo information leak-u. Pozitívny test usera A nestačí.

Security testy potrebujú safe scope, test identities a cleanup. Destruktívny alebo production test musí mať blast-radius a abort contract. Controls sa overujú positive aj negative cestou: legitímna operácia musí prejsť a zakázaná musí zlyhať správnym spôsobom.

Exception vo quality gate musí mať ownera, dôvod, expiry a compensating control. Trvalé ignorovanie findingu bez lifecycle-u premieňa scanner na noise generator.

## 1. Cieľ kapitoly

Nosný model kapitoly je:

```text
asset a požadovaná property
→ actor/failure a trust boundary
→ abuse case alebo zakázaný state
→ preventívna a detekčná kontrola
→ source/artifact/plan/runtime evidence
→ negatívny enforcement test
→ finding a contextual risk
→ remediation alebo expirovateľná exception
→ retest nasadeného fixu
```

Nástroje ako SAST, SCA, policy engine, DAST alebo cloud scanner sú observation mechanisms v tomto lifecycle-e. Nemajú nahradiť threat model a control-to-evidence väzbu.

## 2. Nosný scenár: Atlas Orders 3.9.0

Atlas Orders je multi-tenant služba. Release 3.9.0 pridáva export objednávok a mení deployment workerov.

Chránené assets:

- zákaznícke a objednávkové dáta;
- tenant authorization decision;
- auditná stopa;
- release artifact a deployment identity;
- cloud control plane;
- dostupnosť `CreateOrder` a export workflowu.

Dve kritické riziká:

```text
R1: používateľ tenanta A získa objednávky tenanta B
R2: management endpoint workerov sa stane verejne dostupný
```

Evidence chain release-u:

```text
threat/invariant
→ code a policy controls
→ dependency/artifact evidence
→ rendered IaC a plan
→ sandbox apply
→ effective permissions/network state
→ negative API/network tests
→ audit a alert evidence
→ release decision
```

## 3. Security verzus infrastructure pohľad

Jedna kontrola sa posudzuje z dvoch strán:

```text
Infrastructure verification
→ security group a NetworkPolicy deklarujú iba povolené sources/ports

Security enforcement test
→ request z nepovolenej siete sa reálne nedostane na management endpoint
```

Rovnako pri tenant isolation:

```text
Infrastructure/data control
→ DB rola, schema a query path podporujú tenant scope

Security behavior
→ tenant A nedokáže čítať, exportovať ani odvodiť dáta tenanta B
```

Deklarovaný state a negatívny runtime dôkaz sa dopĺňajú.

## 4. Threat-informed test contract

Pre každé významné riziko pomenuj:

1. asset a požadovanú property;
2. actor alebo failure source;
3. entry point a trust boundary;
4. abuse path alebo zakázaný effective state;
5. preventívnu kontrolu;
6. detekčnú kontrolu;
7. testovanú boundary a oracle;
8. artifact/environment scope;
9. reakciu na failure;
10. residual risk a blind spots.

Všeobecné „spusti security scan“ nenahrádza tento contract.

## 5. Atlas abuse case: cross-tenant export

```text
Actor: autentifikovaný používateľ tenanta A
Goal: získať export objednávok tenanta B
Entry point: POST /exports s resource/tenant identitou
Trust boundaries:
- user token → API authorization
- API → export event
- worker identity → database/object storage
Controls:
- tenant odvodený z authenticated contextu
- object-level authorization
- tenant-scoped query
- event obsahuje immutable tenant context
- worker DB rola nemá globálny read bez policy
- storage key a download authorization sú tenant-scoped
Detection:
- audit event a cross-tenant anomaly signal
```

Test musí sledovať celý abuse path, nie iba jednu API response.

## 6. Control-to-evidence mapa

| Riziko | Preventívna kontrola | Negatívny test | Runtime/detekčný dôkaz |
|---|---|---|---|
| Cross-tenant export | tenant-scoped auth, event a query | tenant A žiada resource B | audit a anomaly event |
| Public management port | IaC policy, SG a NetworkPolicy | connect z internet source | flow/access logs |
| Tampered artifact | signature/admission policy | modified alebo unsigned digest | deployment admission record |
| Stolen credential | short-lived identity a least privilege | expired/revoked token | identity audit |

Mapa odhaľuje controls, ktoré existujú iba v source, ale nemajú enforcement alebo detection evidence.

## 7. Vrstvy bezpečnostného dôkazu

Dôkaz sa vrství podľa failure boundary:

```text
source
→ static correctness a risky data flows

dependencies/artifact
→ presné components, provenance a known risks

configuration/IaC
→ syntax, schema, policy a plánovaný rozdiel

sandbox/runtime
→ provider defaults, identity, network a admission enforcement

behavior
→ authn/authz, abuse cases a zakázané side effects

detection/response
→ audit, alert, containment a runbook
```

Žiadna vrstva sama nepreukazuje celý security outcome.

## 8. Source, dependency a artifact evidence

### Source analysis

SAST alebo compiler/data-flow kontrola môže nájsť injection flow, unsafe deserialization, hardcoded secret alebo chýbajúci authorization pattern. Výsledok potrebuje runtime a business context.

### Dependency analysis

SCA potvrdí, že konkrétny package/version je v dependency alebo artifact graphe. Contextual risk závisí od:

```text
component presence
+ runtime reachability
+ attacker access
+ required privileges
+ existing controls
+ business impact
```

### Artifact identity

SBOM, signature a provenance musia patriť k rovnakému digestu, ktorý sa nasadzuje. Test overí:

- validný podpísaný artifact je prijatý;
- nepodpísaný alebo zmenený artifact je odmietnutý;
- podpis nesprávnej identity neprejde;
- admission decision je auditovaný.

Generovanie podpisu bez deployment verification nie je control enforcement.

## 9. IaC evidence lifecycle

Atlas infra zmena prechádza:

```text
source modules a values
→ rendered configuration
→ syntax a schema
→ static policy
→ plan/change set
→ sandbox apply
→ provider/platform mutation
→ effective runtime state
→ behavior a operational outcome
```

Každá transformačná vrstva môže zmeniť výsledok.

### Source/render

Testuje defaults, overrides, resource identity a deterministic rendering.

### Policy

Overuje zakázané vlastnosti, napríklad public management port, broad IAM alebo unsigned image. Potrebuje allow aj deny fixtures.

### Plan

Overuje konkrétne create/update/delete, replacement, privilege expansion, public exposure, encryption a blast radius. Unknown value sa nesmie automaticky považovať za bezpečnú.

### Apply

Izolovaný sandbox overí provider API, credentials, quotas, defaults a skutočnú vytvoriteľnosť resources.

### Effective state

Runtime test overí to, čo skutočne platí po inherited policies, admission mutations a provider defaults.

## 10. Enforcement test

Policy existence sa dokazuje negatívnym scenárom:

```text
predlož zakázanú konfiguráciu alebo request
→ control ju odmietne
→ dôvod zodpovedá očakávanej policy
→ bežná identity nemá bypass
→ failure nevytvorí zakázaný side effect
→ decision je auditovaný
```

Pozitívny test navyše potvrdí, že legitímny workload nie je blokovaný noisy pravidlom.

## 11. Authentication a authorization matrix

Authentication testuje dôkaz identity a credential lifecycle:

- missing, malformed alebo invalid signature;
- wrong issuer/audience;
- expired alebo not-yet-valid token;
- revoked credential;
- user verzus workload identity;
- safe error a log behavior.

Authorization test používa maticu:

```text
subject × action × resource × context → allow alebo deny
```

Context zahŕňa tenant, ownership, environment, resource state a delegated role.

Atlas negatívne testy pokrývajú:

- tenant A číta order B;
- tenant A spustí export pre B;
- bežný user volá admin function;
- pagination alebo bulk export obíde tenant filter;
- worker spracuje event s podvrhnutým tenant contextom;
- odmietnutá operácia nevytvorí event, object ani audit gap.

UI skrytie tlačidla nie je authorization control.

## 12. Input a parser boundaries

Security test sa odvodzuje z parsera, sinku a side effectu:

- injection;
- path traversal a archive extraction;
- SSRF a URL parsing;
- unsafe deserialization;
- oversized/deep payload;
- duplicate keys a parser differential;
- Unicode normalization;
- file upload identity a storage path.

Silný oracle nekontroluje iba status. Overuje neprítomnosť zakázaného side effectu, zachovanie tenant boundary a bezpečný error contract.

Regexový payload list bez väzby na parser a sink je slabý test design.

## 13. Fuzzing ako doplnkový experiment

Fuzzing je vhodný pre parser, protocol alebo state machine. Definuje:

- target a input grammar/corpus;
- runtime instrumentation;
- resource a time limits;
- crash/hang/invariant oracle;
- deduplication a minimalizáciu inputu;
- regression uloženie nájdeného failure.

„Proces nespadol“ nemusí byť dostatočný oracle pre authorization alebo data-integrity risk.

## 14. Network a workload infrastructure tests

Pre management endpoint Atlas overuje:

```text
source location
→ DNS/route
→ firewall/SG/NetworkPolicy
→ listener
→ authentication
→ authorization
```

Testy obsahujú:

- povolenú internú admin path;
- zakázanú internetovú path;
- IPv4 aj IPv6 podľa supportu;
- stateful return path;
- east-west segmentation;
- metadata endpoint protection;
- mTLS/certificate rotation;
- flow/access log evidence.

Port scan ukáže exposure. Neoverí však application authorization.

## 15. Kubernetes a runtime identity

Manifest a runtime evidence sa porovnávajú pre:

- immutable image digest a trusted registry;
- non-root user a effective UID;
- read-only filesystem;
- capabilities a seccomp/MAC profile;
- privileged/host namespace zákaz;
- service-account token scope;
- resource limits;
- secret mounts a permissions;
- NetworkPolicy a admission;
- graceful termination.

`runAsNonRoot: true` nie je dôkaz, ak workload v skutočnosti neštartuje alebo admission policy nie je enforced.

## Doplnenie výkladu: threat, control a tri úrovne evidence

Security test má začínať **threatom alebo abuse case-om**, nie iba zoznamom scannerov. Threat opisuje, kto alebo čo môže vykonať nežiaducu akciu, cez akú hranicu a s akým dopadom. Control je mechanizmus, ktorý má akciu zabrániť, obmedziť alebo zaznamenať.

Príklad:

```text
Threat: neautentizovaný caller číta cudziu objednávku.
Control: authentication + tenant-scoped authorization query.
Positive test: owner objednávku prečíta.
Forbidden test: iný tenant dostane 403/404 a žiadne dáta.
Audit test: pokus vytvorí správny security event bez secretov.
```

Pri infraštruktúre rozlišuj tri evidence vrstvy:

```text
source/static
→ čo deklaruje HCL/YAML a policy

plan/resolved
→ čo nástroj po variables, modules a defaults navrhuje vytvoriť

runtime/effective
→ čo cloud, cluster, kernel alebo sieť skutočne presadzuje
```

Policy test nad Terraform source môže prehliadnuť hodnotu pridanú module defaultom. Policy nad plan JSON vidí resolved resource graph, ale nepreukazuje, že apply prebehne v správnom account-e ani že runtime policy nebude zmenená iným writerom.

Príklad plan kontroly:

```bash
terraform show -json tfplan > tfplan.json
conftest test tfplan.json --policy policy/
```

Prvý príkaz serializuje saved plan do JSON. Druhý vyhodnotí policy rules nad týmto konkrétnym dokumentom. PASS znamená, že pravidlá nenašli porušenie v analyzovanom plane. Nepreukazuje úplnosť policy, bezpečnosť provider implementation ani effective stav po apply.

Security test musí obsahovať aj **negative/forbidden path**. Pozitívny test „admin dokáže deployovať“ nepreukazuje least privilege. Forbidden test „read-only principal nedokáže meniť production“ overuje enforcement hranicu. Pri takom teste sa používa izolovaný test principal a bezpečný target, aby experiment nevytvoril reálny incident.

Scanner finding je hypotéza alebo evidence item, nie automaticky exploitable defect. Severity, reachability, runtime exposure, compensating controls a asset criticality ovplyvňujú rozhodnutie. Naopak nulový report môže znamenať chýbajúci scanner job alebo neparsovaný report. Gate preto overuje aj completeness: očakávaný tool, target, ruleset, timestamp a successful report ingestion.

## 16. Worked failure: policy existovala iba v audit režime

Atlas policy repository obsahovalo pravidlo:

```text
management port 9090 nesmie byť otvorený 0.0.0.0/0
```

Unit fixtures policy prešli. Deployment však vytvoril public security-group rule.

```text
rendered IaC obsahovalo 0.0.0.0/0:9090
→ policy controller zaznamenal violation
→ mode bol audit, nie enforce
→ apply pokračoval
→ external connect na port uspel
```

### Root cause

Tím testoval policy logic, ale nie jej priradenie, mode a runtime enforcement.

### Náprava

- CI deny fixture testuje policy decision;
- admission/enforcement integration test predloží zakázaný resource;
- plan gate blokuje public management port;
- post-apply network test skúsi zakázaný source;
- policy mode a scope sú verzované a auditované;
- scanner/tool failure má fail-closed alebo explicitnú exception policy.

## 17. Worked failure: API authorization bola zelená, export leakol

Atlas API správne odmietlo priame `GET /orders/{id}` pre iný tenant. Export flow však používal event:

```text
API autorizovalo export request pre tenant A
→ event obsahoval user-provided tenantId B
→ worker používal broad DB rolu
→ CSV obsahovalo tenant B orders
→ download object bol viazaný iba na export ID
```

### Root cause

Authorization test končil na API response a neoveril immutable tenant context cez event, worker query, storage key a download boundary.

### Náprava

- tenant ID sa odvodzuje z authenticated contextu;
- event schema a contract označia tenant context ako server-owned;
- worker používa tenant-scoped query/DB control;
- component/E2E abuse test overí celý export;
- audit a anomaly detection korelujú requester, event a output tenant;
- regression test overí neprítomnosť cross-tenant rows aj side effects.

## 18. Detection a response evidence

Preventívna kontrola môže zlyhať. Atlas testuje, že:

```text
abuse alebo policy violation
→ audit event
→ pipeline ingestion
→ detection rule
→ alert s actionable contextom
→ owner/on-call
→ containment a runbook
→ retained evidence
```

Purple-team alebo game-day scenár môže overiť celý detection-to-response lifecycle. Alert bez identity, assetu a odporúčanej akcie je slabý operational control.

## 19. Findings a contextual risk

Finding obsahuje:

- affected artifact, asset a environment;
- reprodukciu a evidence;
- attacker preconditions a trust boundary;
- runtime presence/reachability;
- technical a business impact;
- confidence a severity;
- existing/compensating controls;
- ownera, remediation a deadline;
- release/risk decision;
- retest result.

Scanner line bez asset contextu a attack pathu nie je hotový remediation ticket.

## 20. Tool failure semantics

Pipeline rozlišuje:

```text
scan completed, no findings
scan completed, findings present
scan incomplete
rules/feed stale
artifact nebol analyzovaný
tool alebo license service unavailable
```

`Scanner failed` nikdy neznamená `no findings`. Neznámy dôkaz musí viesť k fail-closed rozhodnutiu alebo k auditovanej, časovo obmedzenej exception.

## 21. Exceptions a risk acceptance

Exception obsahuje:

- konkrétny finding/control;
- asset a scope;
- business dôvod;
- risk ownera;
- residual risk a compensating controls;
- remediation plan;
- expiry;
- approval a review cadence.

Permanentný globálny suppression nie je risk management.

## 22. Retest a closure

Finding sa nezatvára commitom. Closure vyžaduje:

```text
fix v source
→ nový immutable artifact
→ deployment do relevantného environmentu
→ pôvodná reprodukcia už nefunguje
→ alternate bypass sa skontroluje
→ runtime/detection evidence je správna
→ regression test zostáva
→ temporary mitigation sa odstráni
```

Evidence sa viaže na nasadený digest a prostredie.

## 23. Failure artifacts a diagnostika

Security/infrastructure failure uchová:

- source, rendered output a plan;
- policy/rule version a mode;
- artifact digest, SBOM/provenance identity;
- test identity a source location;
- exact request/configuration s redaction;
- effective permissions/network state;
- audit, flow a application logs;
- finding/reproduction a environment revision;
- tool completeness/freshness status.

Diagnostický postup:

1. Potvrď artifact, asset, environment a test identity.
2. Urči threat/invariant a očakávaný control.
3. Nájdite transformačnú alebo trust boundary, kde evidence prestala súhlasiť.
4. Rozlíš source, render, plan, provider default, inherited policy a runtime drift.
5. Over reachability, exposure a business impact.
6. Reprodukuj najbezpečnejším dostatočným scenárom.
7. Oprav autoritatívny source/control, nie iba runtime symptom.
8. Pridaj pozitívny aj negatívny regression test.
9. Retestuj nasadený fix a detection path.
10. Uzavri finding alebo vytvor expirovateľnú risk exception.

## 24. Referenčné pravidlá

- Security test začína threatom alebo abuse case-om.
- Infrastructure test sleduje source až po effective behavior.
- Scanner je observation tool, nie security verdict.
- CVE severity potrebuje runtime a business context.
- SBOM, signature a provenance sa viažu na rovnaký digest.
- Policy testuje allow aj deny a následne enforcement.
- Authorization matrix pokrýva subject, action, resource a context.
- Negatívny test overuje aj absenciu side effectu.
- Admin identity nesmie byť univerzálnou test identity.
- Destruktívny test používa allowlist, blast-radius a abort criteria.
- Tool outage nie je zelený výsledok.
- Exception má ownera, scope a expiry.
- Finding sa zatvára až po reteste nasadeného fixu.

## 25. Časté omyly

### „Scanner prešiel, systém je bezpečný“

Scanner pokrýva iba časť attack surface a má blind spots.

### „Validné IaC znamená bezpečný deployment“

Syntax neoveruje policy, plan, effective state ani behavior.

### „Policy existuje, preto je enforced“

Potrebný je negatívny admission alebo runtime test.

### „API authorization test chráni všetky background flows“

Worker, event, cache, export a storage môžu meniť trust boundary.

### „CVE severity je naše riziko“

Chýba presence, reachability, exposure a business impact.

### „Scanner outage znamená no findings“

Znamená neúplný dôkaz.

### „Fix je commitnutý, finding možno zavrieť“

Potrebný je retest artifactu, ktorý je skutočne nasadený.

## 26. Zhrnutie

Dôveryhodný security a infrastructure evidence chain pre Atlas je:

```text
asset/threat/invariant
→ control design
→ source a artifact evidence
→ rendered IaC a plan
→ sandbox apply
→ effective runtime state
→ negative abuse/enforcement test
→ audit a response evidence
→ contextual finding
→ remediation/exception
→ retest nasadeného fixu
```

Cieľom nie je maximalizovať počet scannerov. Cieľom je preukázať, že konkrétne controls znižujú konkrétne riziká na reálnych trust a infrastructure boundaries.

## 27. Kontrolné otázky

1. Aký lifecycle spája threat, control, test a rozhodnutie?
2. Ako sa security test líši od infrastructure verification?
3. Čo musí obsahovať threat-informed test contract?
4. Ako vyzerá Atlas cross-tenant export abuse case?
5. Prečo SAST alebo SCA finding potrebuje runtime context?
6. Aké vrstvy má IaC evidence lifecycle?
7. Ako negatívny enforcement test dokazuje policy?
8. Čo obsahuje authorization matrix?
9. Prečo API-only test neodhalil Atlas export leak?
10. Ako policy v audit režime vytvorila false green?
11. Čo musí znamenať scanner/tool failure?
12. Aké náležitosti má risk exception?
13. Kedy je finding skutočne uzavretý?
14. Ako detection-to-response test dopĺňa prevention?

## Glossary impact

Relevantné pojmy: threat model, asset, trust boundary, abuse case, control-to-evidence map, SAST, DAST, IAST, SCA, reachability, exploitability, SBOM, artifact provenance, signature verification, Infrastructure as Code testing, effective state, Policy as Code, enforcement test, authorization matrix, object-level authorization, security finding, tool failure semantics, risk acceptance a retest.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Performance, load a stress tests](performance-load-stress-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Static analysis, linting a type checking →](static-analysis-linting-type-checking.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
