# Security a infrastructure tests

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

## 1. Definícia

Security testing overuje, či systém odoláva definovaným hrozbám a či bezpečnostné kontroly fungujú podľa zámeru. Infrastructure testing overuje, či infraštruktúra, konfigurácia a platformové policies spĺňajú požadovaný stav, invariants a prevádzkové vlastnosti.

Obe oblasti sa prekrývajú, ale nie sú totožné:

- security test sa pýta, či je systém zneužiteľný alebo či kontrola zlyháva,
- infrastructure test sa pýta, či je deklarovaná infraštruktúra správna, konzistentná a prevádzkyschopná.

## 2. Threat-informed testing

Security test má vychádzať z threat modelu:

```text
assets
→ trust boundaries
→ actors
→ attack surfaces
→ abuse cases
→ controls
→ evidence
```

Bez threat modelu vzniká náhodný zoznam scannerov bez jasnej väzby na riziko.

## 3. Security test vrstvy

### SAST — Static Application Security Testing

Analyzuje source, bytecode alebo intermediate representation bez spustenia aplikácie. Hľadá napríklad:

- injection patterns,
- unsafe deserialization,
- hardcoded secrets,
- insecure API usage,
- tainted data flows.

### DAST — Dynamic Application Security Testing

Testuje bežiacu aplikáciu zvonka. Sleduje observable behavior, napríklad:

- authentication bypass,
- injection,
- insecure headers,
- session handling,
- authorization failures.

### IAST — Interactive Application Security Testing

Kombinuje runtime pozorovanie aplikácie s informáciou o internom data flow počas testov.

### SCA — Software Composition Analysis

Analyzuje third-party dependencies, transitive graph, licenses a známe vulnerabilities.

### Container a artifact scanning

Kontroluje image layers, OS packages, language dependencies, secrets, malware indicators a metadata.

### IaC scanning

Analyzuje Terraform, Kubernetes manifests, Helm output, cloud templates a policies pred apply.

## 4. Vulnerability vs. exploitability

Nález vo version databáze neznamená automaticky reálne riziko. Posudzuj:

- je vulnerable component prítomný v runtime artifacte,
- je zraniteľný code path reachable,
- je feature zapnutá,
- existuje exposure na attack surface,
- sú prítomné compensating controls,
- aký je business impact.

Na druhej strane absencia známeho CVE nedokazuje bezpečnosť.

## 5. Authentication a authorization tests

Overuj oddelene:

- authentication identity proof,
- session/token lifecycle,
- authorization decision,
- object-level access,
- function-level access,
- tenant isolation,
- privilege escalation,
- revocation a expiry.

Negatívne scenáre:

```text
bez credentials
invalid credentials
expired token
revoked token
správna identity, nesprávna role
správna role, cudzí resource
cross-tenant request
manipulated claims
```

HTTP 401 a 403 musia mať konzistentné semantics a nesmú odhaľovať citlivé informácie.

## 6. Input a output security tests

Testuj:

- command, SQL, LDAP a template injection,
- path traversal,
- SSRF,
- unsafe file upload,
- deserialization,
- XSS a output encoding,
- header injection,
- parser differentials,
- oversized a malformed payloads.

Fuzzing a property-based testing môžu generovať vstupy mimo ručne pripravených príkladov.

## 7. Secrets testing

Kontroluj:

- secrets v source a Git history,
- environment a config dumps,
- build logs,
- image layers,
- artifacts a backups,
- test fixtures,
- debug endpoints,
- overly broad secret access.

Secret scanner je detection control. Nenahrádza secret manager, rotáciu, short-lived credentials a least privilege.

## 8. Supply-chain tests

Overuj:

- dependency source a integrity,
- lockfiles,
- artifact provenance,
- signed commits/tags podľa policy,
- build isolation,
- trusted runners,
- immutable artifacts,
- SBOM generation,
- signature verification pred deployom,
- protection pred dependency confusion.

Security gate musí rozlišovať severity, reachability, exploit maturity a approved exception lifecycle.

## 9. Infrastructure as Code tests

IaC testovanie môže mať viac vrstiev:

### Syntax a schema

```text
terraform validate
helm lint
kubeconform
cloud template validation
```

### Static policy

Príklady invariants:

- storage nesmie byť public,
- security group nesmie povoľovať široký management access,
- workload nesmie bežať privileged,
- encryption musí byť zapnuté,
- required tags musia existovať,
- production deletion protection musí byť aktívna.

### Plan testing

Testuje rendered alebo planned change:

- počet vytváraných a mazaných resources,
- replacement kritických objektov,
- neočakávaný privilege expansion,
- public exposure,
- destructive drift correction.

### Runtime verification

Po apply over reálny stav, pretože provider defaults, platform mutation a externý drift môžu zmeniť výsledok.

## 10. Policy as Code

Policy as Code reprezentuje pravidlá strojovo vyhodnotiteľným spôsobom. Dobrá policy má:

- jasný názov a dôvod,
- scope,
- test fixtures pre allow aj deny,
- severity,
- ownera,
- exception proces,
- versioning,
- auditovateľný výsledok.

Policy bez testov môže blokovať legitímny change alebo povoliť zakázaný stav.

## 11. Configuration a compliance tests

Overuj efektívny runtime stav, nie iba deklarovaný input:

- TLS versions a ciphers,
- OS hardening,
- IAM bindings,
- network exposure,
- audit logging,
- backup policy,
- retention,
- encryption,
- patch level,
- time synchronization.

Compliance requirement treba preložiť na konkrétny technical control a dôkaz. Checkbox bez dôkazu účinnosti nie je test.

## 12. Kubernetes a container tests

Príklady:

- image nepoužíva `latest`,
- image digest je pinovaný,
- container nebeží ako root,
- read-only root filesystem,
- capabilities sú minimalizované,
- seccomp/AppArmor/SELinux policy,
- resource requests a limits,
- NetworkPolicy,
- liveness/readiness/startup probes,
- secrets nie sú v plaintext manifests,
- admission policy zamieta nebezpečný workload.

Runtime test musí overiť, že policy je skutočne enforced, nie iba deklarovaná.

## 13. Network security tests

Testuj:

- povolené a zakázané paths,
- ingress aj egress,
- IPv4 aj IPv6,
- DNS a service discovery,
- segmentation a lateral movement,
- firewall state,
- load balancer exposure,
- management interfaces,
- mTLS identity a certificate rotation.

Port scan ukazuje exposure, nie automaticky authorization alebo business exploitability.

## 14. Backup a recovery tests

Existencia backupu nie je recovery dôkaz. Testuj:

- restore do izolovaného prostredia,
- integrity a completeness,
- encryption keys,
- RPO a RTO,
- application consistency,
- schema compatibility,
- access controls,
- pravidelný restore drill.

Recovery test je zároveň infrastructure, security aj operational acceptance test.

## 15. Destructive a failure tests

Infrastructure test môže cielene overiť:

- node alebo zone failure,
- disk full,
- DNS failure,
- expired certificate,
- revoked credentials,
- denied IAM action,
- blocked network path,
- provider/API throttling,
- interrupted deployment.

Experiment musí mať scope, blast radius, rollback a observation plan.

## 16. Test environment a test accounts

Security testy nesmú používať neobmedzené production credentials. Používaj:

- dedikované test identities,
- minimálne permissions,
- syntetické dáta,
- izolované tenants,
- krátku expiráciu,
- audit trail,
- cleanup.

Test, ktorý potrebuje admin účet na každý scenár, môže zakrývať authorization chyby.

## 17. Findings management

Nález má obsahovať:

1. affected asset a version,
2. reprodukčné kroky alebo evidence,
3. precondition a attack path,
4. impact,
5. severity a confidence,
6. ownera,
7. remediation,
8. due date alebo risk acceptance,
9. retest výsledok.

Scanner output bez triage vytvára backlog šumu a false positives.

## 18. Quality gates

Blocking gate je vhodný, keď:

- signál má vysokú presnosť,
- nález má jasný impact,
- remediation je vykonateľná,
- exception proces existuje,
- tool je spoľahlivý a rýchly.

Nový scanner sa nemá okamžite zmeniť na globálny blocking gate bez baseline a tuning-u.

## 19. Typické omyly

### „Scanner prešiel, systém je bezpečný“

Scanner pokrýva iba vybrané triedy problémov.

### „CVE severity rovná sa naše riziko“

Chýba kontext reachability, exposure a impactu.

### „IaC je validné, deployment je bezpečný“

Syntax validation neoveruje policy ani runtime efekt.

### „Policy existuje, preto je enforced“

Treba negatívny test zamietnutia a runtime overenie.

### „Penetračný test raz ročne stačí“

Architektúra, dependencies a exposure sa menia kontinuálne.

### „Testovacie dáta nie sú citlivé“

Kópie produkčných dát môžu obsahovať PII, secrets a interné identifiers.

## 20. Kontrolné otázky

1. Aký je rozdiel medzi SAST, DAST, IAST a SCA?
2. Prečo CVE nález nemusí znamenať rovnaké riziko v každom systéme?
3. Ako navrhneš authorization negative tests?
4. Aké vrstvy má IaC testovanie?
5. Čo musí obsahovať testovaná Policy as Code?
6. Prečo plan test nenahrádza runtime verification?
7. Ako overíš enforcement admission alebo network policy?
8. Prečo backup bez restore testu nie je dostatočný dôkaz?
9. Kedy má security finding blokovať pipeline?
10. Ako spravovať exceptions bez trvalého obchádzania kontroly?

## Glossary impact

Relevantné pojmy: SAST, DAST, IAST, SCA, threat model, attack surface, abuse case, IaC scanning, Policy as Code, SBOM, artifact provenance, vulnerability reachability, security finding, risk acceptance, admission policy a restore drill.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Performance, load a stress tests](performance-load-stress-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Static analysis, linting a type checking →](static-analysis-linting-type-checking.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
