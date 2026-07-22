# CIA triáda

CIA triáda — **Confidentiality, Integrity a Availability** — je základný model bezpečnostných cieľov informačných systémov. Nepredstavuje konkrétnu technológiu ani kompletný security framework. Poskytuje systematický spôsob, ako pomenovať, čo musí byť chránené, aký typ straty hrozí a aké controls majú dané riziko znižovať.

## 1. Mentálny model

```text
asset a business process
→ threats a failure modes
→ strata confidentiality, integrity alebo availability
→ dopad na používateľov, organizáciu a prevádzku
→ preventívne, detekčné a recovery controls
→ residual risk a validation
```

Bezpečnostný návrh nemá začínať zoznamom produktov. Má začínať assets, data flows, trust boundaries a očakávaným dopadom straty jednotlivých vlastností.

## 2. Confidentiality

Confidentiality znamená zachovanie autorizovaných obmedzení prístupu a disclosure.

Otázka:

```text
Kto smie tieto dáta alebo capability vidieť a za akých podmienok?
```

### Príklady straty confidentiality

- uniknuté credentials alebo API tokeny,
- verejný object-storage bucket,
- broad database read access,
- logovanie secrets alebo osobných údajov,
- cross-tenant data exposure,
- nešifrovaný network traffic,
- backup dostupný neoprávnenému účtu,
- prompt alebo agent tool output obsahujúci interné dáta.

### Typické controls

- authentication,
- authorization a least privilege,
- encryption at rest a in transit,
- secrets management,
- network segmentation,
- data classification,
- masking, tokenization a redaction,
- tenant isolation,
- secure disposal,
- audit accessu,
- key management.

### Confidentiality nie je iba šifrovanie

Encryption chráni dáta pred určitými threat scenármi, ale nerieši napríklad:

- oprávneného používateľa s príliš širokými právami,
- application bug vracajúci cudzie dáta,
- compromise po dešifrovaní v memory,
- logovanie plaintextu,
- zlé IAM policy,
- secret uložený v Git-e.

## 3. Integrity

Integrity znamená ochranu pred neautorizovanou alebo nesprávnou zmenou a zachovanie accuracy, completeness, authenticity a správneho processingu.

Otázka:

```text
Ako vieme, že dáta, konfigurácia a vykonaná operácia sú správne a neboli neautorizovane zmenené?
```

### Príklady straty integrity

- útočník upraví artifact alebo container image,
- chybný deployment prepíše production konfiguráciu,
- SQL injection zmení dáta,
- message sa spracuje dvakrát,
- backup je poškodený,
- DNS record bol neautorizovane zmenený,
- CI pipeline použije neoverenú dependency,
- telemetry bola sfalšovaná alebo odstránená,
- agent vykoná nesprávnu alebo neautorizovanú tool action.

### Typické controls

- hashes a cryptographic signatures,
- code review a protected branches,
- artifact signing a provenance,
- database constraints a transactions,
- immutability,
- input validation,
- separation of duties,
- audit trail,
- versioning,
- idempotency,
- integrity checks a reconciliation,
- backup validation.

### Integrity a authenticity

Hash môže odhaliť zmenu, ale bez dôveryhodného source-u nemusí dokazovať, kto artifact vytvoril.

Preto sa často kombinuje:

```text
hash
+ digital signature
+ trusted identity
+ provenance
+ policy verification
```

## 4. Availability

Availability znamená včasný a spoľahlivý prístup k informáciám a službám pre autorizovaných používateľov.

Otázka:

```text
Je systém použiteľný vtedy, keď ho oprávnený používateľ alebo business process potrebuje?
```

### Príklady straty availability

- výpadok služby,
- DDoS,
- vyčerpanie quota alebo disk capacity,
- expired certificate,
- dependency outage,
- ransomware,
- DNS failure,
- deadlock alebo resource saturation,
- neobnoviteľný backup,
- administratívne zablokovaný account,
- chybná security policy blokujúca legitímny traffic.

### Typické controls

- redundancy a fault isolation,
- autoscaling a capacity planning,
- backups a tested restore,
- disaster recovery,
- load balancing,
- rate limiting a DDoS protection,
- failover,
- monitoring a incident response,
- patching a lifecycle management,
- graceful degradation,
- quotas a resource protection.

### Availability nie je iba uptime

Systém môže byť technicky dostupný, ale prakticky nepoužiteľný pre:

- extrémnu latency,
- stale alebo neúplné dáta,
- chýbajúcu kritickú funkciu,
- nefunkčnú authentication cestu,
- nedostupnosť iba v jednej lokalite alebo pre jednu tenant skupinu.

Availability contract musí odrážať user journey a business potrebu.

## 5. Vzťah medzi C, I a A

Bezpečnostné rozhodnutia často zlepšujú jednu vlastnosť a zhoršujú inú.

Príklady:

### Encryption

- zvyšuje confidentiality,
- môže podporiť integrity,
- pri strate keys môže zničiť availability.

### Strict access policy

- zvyšuje confidentiality,
- môže znížiť availability legitímnym používateľom.

### Replication

- zvyšuje availability,
- zväčšuje počet kópií a confidentiality exposure,
- môže šíriť logical corruption a poškodiť integrity.

### Caching

- zvyšuje availability a performance,
- môže servovať stale data a poškodiť integrity,
- môže rozšíriť exposure citlivých dát.

### Immutable backups

- zvyšujú integrity a recoverability,
- môžu komplikovať deletion a privacy requirements,
- potrebujú správnu key a access availability.

Security architecture je riadenie trade-offov, nie maximalizácia jednej osi bez kontextu.

## 6. Assets

CIA sa vždy hodnotí voči konkrétnemu assetu.

Assets:

- business data,
- credentials a keys,
- source code,
- artifacts,
- infrastructure configuration,
- identities a permissions,
- telemetry a audit evidence,
- backups,
- availability kritickej služby,
- reputation a regulatory records.

Rovnaký asset môže mať odlišnú prioritu jednotlivých vlastností.

Príklady:

- public marketing web: availability a integrity môžu dominovať nad confidentiality,
- password database: confidentiality a integrity sú kritické,
- audit trail: integrity a availability dôkazu sú kľúčové,
- public package repository: integrity je kritická aj pri verejnom obsahu.

## 7. Data lifecycle

CIA analyzuj počas celého lifecycle-u:

```text
create
→ process
→ store
→ transmit
→ copy/backup
→ archive
→ restore
→ delete
```

Príklad confidentiality failure:

- production database je správne šifrovaná,
- ale export CSV zostáva v otvorenom shared storage.

Príklad integrity failure:

- source data je správne,
- ale ETL pipeline nesprávne transformuje hodnoty.

Príklad availability failure:

- backup existuje,
- ale restore procedure nie je funkčná.

## 8. Data states

### Data at rest

- database,
- filesystem,
- object storage,
- backup,
- snapshot,
- artifact registry.

### Data in transit

- client-server traffic,
- service-to-service traffic,
- replication,
- telemetry export,
- message queues.

### Data in use

- process memory,
- CPU/GPU processing,
- temporary files,
- decrypted payload,
- model context alebo prompt.

Controls sa líšia podľa state-u. Encryption at rest nechráni plaintext po načítaní aplikáciou.

## 9. Threat, vulnerability, risk a impact

### Threat

Potenciálna príčina neželaného incidentu.

Príklady:

- attacker,
- insider,
- human error,
- hardware failure,
- natural disaster,
- software bug.

### Vulnerability

Slabina, ktorú môže threat využiť.

Príklady:

- public access,
- chýbajúci patch,
- broad IAM role,
- single point of failure,
- nevalidovaný input.

### Impact

Následok straty confidentiality, integrity alebo availability.

### Risk

Kombinácia pravdepodobnosti, exploitability, impactu a kontextu organizácie.

CIA pomáha klasifikovať dopad, ale sama nevypočíta celý risk.

## 10. Security controls

Security control je safeguard alebo countermeasure navrhnutá na zníženie risku.

### Podľa funkcie

- preventive,
- detective,
- corrective,
- recovery,
- deterrent,
- compensating.

### Podľa typu

- management,
- operational,
- technical,
- physical.

Jeden control môže chrániť viac CIA vlastností.

Príklad audit logu:

- podporuje integrity vyšetrovania,
- pomáha detegovať confidentiality breach,
- musí byť dostupný počas incidentu.

## 11. Prevent, detect, respond a recover

Robustný návrh nepredpokladá, že prevention nikdy nezlyhá.

```text
prevent
→ znížiť pravdepodobnosť

detect
→ rýchlo odhaliť stratu vlastnosti

respond
→ obmedziť blast radius

recover
→ obnoviť dôveryhodný stav

learn
→ odstrániť systematickú príčinu
```

Príklad ransomware:

- prevent: least privilege, patching, segmentation,
- detect: anomaly a audit alerts,
- respond: isolation a credential revocation,
- recover: immutable tested backups,
- learn: post-incident control improvements.

## 12. Assurance

Control existuje ≠ control je účinný.

Assurance vzniká cez dôkazy:

- testy,
- configuration review,
- audit,
- penetration testing,
- restore rehearsal,
- access review,
- monitoring,
- formal verification podľa potreby,
- incident history.

Príklad:

```text
„Backups are enabled“
```

nie je rovnaké ako:

```text
„Aplikácia bola obnovená v izolovanom prostredí do RTO a validovaná voči RPO.“
```

## 13. Authentication, authorization a auditing

CIA súvisí s AAA:

- Authentication určuje, kto alebo čo sa prihlasuje.
- Authorization určuje, čo smie vykonať.
- Auditing zaznamenáva, čo sa vykonalo.

Confidentiality a integrity často zlyhajú cez zlú authorization, nie cez slabú encryption.

Audit podporuje accountability a investigation, ale musí mať vlastnú integrity a availability ochranu.

## 14. Privacy oproti confidentiality

Privacy a confidentiality sa prekrývajú, ale nie sú totožné.

Confidentiality rieši neautorizované disclosure.

Privacy rieši širšie otázky:

- či sa dáta vôbec majú zbierať,
- na aký účel,
- ako dlho,
- s akým právnym základom,
- aké práva má dotknutá osoba,
- ako sa dáta zdieľajú a mažú.

Dáta môžu byť confidential, ale stále spracúvané neprimerane alebo bez oprávneného účelu.

## 15. Safety a reliability

Availability sa prekrýva s reliability, ale security model zahŕňa aj malicious disruption.

Integrity sa môže prekrývať so safety:

- nesprávne dáta môžu fyzicky alebo finančne poškodiť používateľa,
- automatizácia môže vykonať nebezpečnú akciu,
- AI agent môže zmeniť production state bez dostatočného approvalu.

Pri high-impact systémoch nestačí tradičná IT availability; treba analyzovať safety constraints a fail-safe behavior.

## 16. Cloud shared responsibility

V cloude sa CIA zodpovednosť delí medzi provider-a a zákazníka podľa service modelu.

Príklad managed database:

Provider typicky chráni:

- physical infrastructure,
- hypervisor/platform,
- časť service availability.

Zákazník stále riadi:

- identities a permissions,
- network exposure,
- data classification,
- encryption configuration,
- backup/restore policy,
- application integrity,
- monitoring.

Managed service neodstraňuje customer CIA responsibility.

## 17. Kubernetes príklad

### Confidentiality

- Secrets access,
- RBAC,
- etcd encryption,
- network policies,
- workload identity.

### Integrity

- signed images,
- admission policy,
- immutable tags/digests,
- GitOps reconciliation,
- audit logs.

### Availability

- replicas,
- topology spread,
- PDB,
- resource requests,
- backup/restore,
- control-plane a data-plane resilience.

Control môže vytvoriť trade-off: príliš strict NetworkPolicy môže zablokovať legitímny traffic a znížiť availability.

## 18. CI/CD a supply chain príklad

### Confidentiality

- pipeline secrets,
- private source code,
- protected logs a artifacts.

### Integrity

- protected branches,
- review,
- pinned dependencies,
- signed artifacts,
- provenance,
- isolated runners.

### Availability

- redundant runners,
- registry availability,
- dependency mirrors,
- rollback artifacts,
- recovery runbooks.

Supply-chain incident často kombinuje confidentiality breach a integrity compromise.

## 19. Observability príklad

Telemetry sama je security asset.

### Confidentiality

- logs a traces môžu obsahovať PII, tokens a internú topology.

### Integrity

- útočník môže falšovať alebo mazať evidence.

### Availability

- telemetry musí byť dostupná počas incidentu, aj keď production platforma zlyháva.

Preto audit a security telemetry často potrebuje oddelený tenant, account alebo failure domain.

## 20. AI a agentické systémy

### Confidentiality

- prompt leakage,
- retrieval cez neoprávnené dáta,
- tool output exposure,
- model provider data handling.

### Integrity

- prompt injection,
- poisoned knowledge source,
- malicious tool result,
- neautorizovaná agent action.

### Availability

- provider outage,
- rate limits,
- token exhaustion,
- runaway agent loop,
- dependency failure.

Agent identity, tool permissions, approval a audit musia byť navrhnuté podľa rovnakých bezpečnostných cieľov.

## 21. Security categorization

Pre každý asset alebo system urči impact straty:

- low,
- moderate,
- high,

samostatne pre confidentiality, integrity a availability.

Príklad:

```text
System: public package registry
Confidentiality impact: low
Integrity impact: high
Availability impact: moderate/high
```

Výsledok ovplyvňuje výber controls, assurance a recovery requirements.

## 22. CIA matrix

Praktická šablóna:

| Asset/process | Confidentiality loss | Integrity loss | Availability loss | Controls | Evidence | Owner |
|---|---|---|---|---|---|---|
| Production DB | data breach | wrong transactions | service outage | IAM, TLS, constraints, backups | access review, restore test | Data team |
| CI artifacts | source leakage | supply-chain compromise | blocked releases | signed artifacts, registry HA | signature verification | Platform |
| Audit logs | sensitive metadata exposure | attacker hides actions | no incident evidence | separate account, immutability | audit test | Security |

Matrix musí byť konkrétna pre systém, nie generic checklist.

## 23. Validation

Confidentiality testy:

- access-control tests,
- secret scanning,
- data-exposure review,
- tenant-isolation tests,
- encryption verification.

Integrity testy:

- signature verification,
- tamper test,
- transaction/constraint tests,
- reconciliation,
- provenance validation.

Availability testy:

- load a stress test,
- failure injection,
- failover,
- backup restore,
- quota exhaustion,
- dependency outage.

## 24. Troubleshooting security incident cez CIA

```text
čo sa stalo?
→ ktorý asset?
→ ktorá CIA vlastnosť je narušená?
→ je narušených viac vlastností?
→ aký je blast radius?
→ stále prebieha compromise?
→ aké containment je bezpečné?
→ aké evidence treba zachovať?
→ ako obnoviť dôveryhodný stav?
```

Príklad compromised credential:

- confidentiality: attacker mohol čítať dáta,
- integrity: mohol ich meniť,
- availability: revocation alebo destructive action môže spôsobiť outage.

Nehodnoť incident iba podľa prvého viditeľného symptómu.

## 25. Anti-patterny

### CIA ako checkbox

Model sa uvedie v dokumente, ale neaplikuje sa na konkrétne assets a controls.

### Encryption = security

Ignoruje authorization, integrity, availability a operational failure modes.

### Availability bez security constraints

Fail-open môže zlepšiť dostupnosť, ale odhaliť alebo poškodiť dáta.

### Security control bez validation

Existencia policy nepreukazuje jej účinnosť.

### Backup iba ako availability control

Backup musí mať confidentiality, integrity a recoverability ochranu.

### Absolútna maximalizácia jednej osi

Môže zničiť použiteľnosť alebo ďalšie bezpečnostné ciele.

## 26. Kontrolné otázky

1. Čo znamenajú Confidentiality, Integrity a Availability?
2. Prečo šifrovanie samo nestačí na confidentiality?
3. Ako sa líši integrity od authenticity?
4. Prečo replication môže poškodiť confidentiality alebo integrity?
5. Ako sa CIA aplikuje na data lifecycle?
6. Aký je rozdiel medzi threat, vulnerability, impact a risk?
7. Čo je security control a assurance?
8. Ako CIA súvisí s authentication, authorization a auditing?
9. Ako sa líši confidentiality a privacy?
10. Ako by vyzerala CIA matrix pre tvoju službu?
11. Ako validovať controls pre každú os?
12. Ako CIA pomáha počas incident response?

## Glossary impact

Relevantné pojmy: CIA triad, confidentiality, integrity, availability, asset, threat, vulnerability, impact, security risk, security control, preventive control, detective control, corrective control, recovery control, compensating control, assurance, authenticity, accountability, non-repudiation, data at rest, data in transit, data in use a security categorization.

## Primárne zdroje

- [NIST — Confidentiality, Integrity and Availability](https://csrc.nist.gov/glossary/term/confidentiality_integrity_availability)
- [NIST — Information Security](https://csrc.nist.gov/glossary/term/information_security)
- [NIST — Security Control](https://csrc.nist.gov/glossary/term/security_control)
- [NIST SP 800-53 Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cardinality](../12-observability/cardinality.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
