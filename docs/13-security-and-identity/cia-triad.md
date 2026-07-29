# CIA triáda

CIA triáda — **Confidentiality, Integrity a Availability** — je model bezpečnostných cieľov nad konkrétnym assetom a business procesom. Nie je to zoznam troch produktových vlastností ani univerzálna priorita `C > I > A`. Použiteľný security návrh musí určiť, čo presne sa chráni, aká strata je neprijateľná, ktorý threat a vulnerability ju môžu spôsobiť, kde sa control presadzuje a aký dôkaz preukáže jeho účinnosť.

## 1. Dominantný lifecycle

```text
business capability a chránený asset
→ exact security subject a trust boundaries
→ confidentiality, integrity a availability objectives
→ threat, vulnerability, exposure a impact
→ risk a required assurance
→ preventive, detective, response a recovery controls
→ configured, loaded a effective control state
→ security event alebo control test
→ containment a authoritative recovery
→ allowed, forbidden a residual-risk validation
→ skorší control alebo architecture change
```

Tento lifecycle oddeľuje tri výroky, ktoré sa často zamieňajú:

```text
control je nakonfigurovaný
≠ control sa presadil na skutočnej boundary
≠ business asset je preukázateľne chránený
```

Encryption enabled, role assignment, backup success alebo healthy identity provider sú iba čiastkové technické stavy. Security acceptance vzniká až vtedy, keď sa povolený outcome zachová, zakázaný outcome zlyhá a recovery obnoví dôveryhodný business stav.

## 2. Exact security subject

CIA sa nikdy nehodnotí iba pre názov služby. Pre connected Atlas Payments incident používame:

```text
security subject: SEC-PAY-47
business capability: enterprise final settlement
release generation: 7.24.0
environment: production
Region: eu-central-1
Kubernetes cluster: atlas-prod-euc1
namespace: payments-prod
human principal: urn:atlas:human:7421
IdP issuer: https://id.atlas.example
active IdP group claim: prod-payment-operators
Kubernetes binding: payments-prod-operators
workload identity: system:serviceaccount:payments-prod:settlement-debug
provider secret: provider-a-mtls generation 34
routing config: SETTLEMENT-ROUTE-91
audit generation: AUDIT-SEC-28
```

Chránené assets nie sú iba dáta. Subject zahŕňa:

- provider client certificate a private key;
- settlement routing policy;
- worker capacity a queue progress;
- final settlement correctness;
- human a workload identity graph;
- audit evidence potrebnú na reconstruction a recovery.

## 3. Confidentiality

Confidentiality znamená, že informácie a capabilities sú sprístupnené iba autorizovaným principals za určených podmienok.

Otázka:

```text
Kto smie asset čítať, odvodiť, exportovať alebo použiť
v ktorom environment-e, tenant-e, čase a trust boundary?
```

Confidentiality loss zahŕňa napríklad:

- prečítanie secretu alebo private key-u;
- cross-tenant disclosure;
- broad database alebo object-store read;
- logovanie tokenu, PII alebo interného payloadu;
- export dát do menej chráneného lifecycle-u;
- použitie capability bez priameho zobrazenia jej hodnoty.

Posledný bod je dôležitý. Principal nemusí prečítať private key, aby ju zneužil. Ak môže vyvolať neobmedzenú signing alebo decryption operáciu, získal citlivú capability.

Typické controls:

- identity proofing, authentication a session assurance;
- authorization, least privilege a tenant isolation;
- encryption a key separation;
- secret minimization a redaction;
- network a workload boundaries;
- data classification, retention a secure deletion;
- immutable alebo oddelený audit prístupu.

Encryption sama nestačí. Po dešifrovaní v application memory môže broad principal, chybný object-level authorization alebo kompromitovaný workload stále získať plaintext.

## 4. Integrity

Integrity znamená zachovanie správnosti, úplnosti, authenticity a povoleného poradia zmien dát, konfigurácie a operácií.

Otázka:

```text
Ako preukážeme, že asset alebo state transition
vytvoril oprávnený actor, správnym mechanizmom,
nad správnou generáciou a bez neautorizovanej zmeny?
```

Integrity loss zahŕňa:

- zmenu routing policy alebo deployment konfigurácie;
- modified artifact alebo dependency;
- duplicate payment či message processing;
- neautorizovaný policy alebo role assignment;
- corrupted backup;
- falšovanie alebo odstránenie audit evidence;
- nesprávnu automatizovanú alebo agentickú action.

Hash preukazuje zhodu s konkrétnym obsahom, nie automaticky jeho dôveryhodný pôvod. Silnejší chain je:

```text
content digest
+ trusted signer identity
+ provenance
+ authorization policy
+ runtime read-back
+ business reconciliation
```

Typické controls:

- immutable a versionované sources;
- signatures a provenance;
- transactions, constraints a idempotency;
- separation of duties;
- policy review a admission;
- reconciliation na authoritative state;
- audit trail s actorom a policy revision;
- restore a tamper validation.

## 5. Availability

Availability znamená, že autorizovaný používateľ alebo business proces môže capability použiť v požadovanom čase, kvalite a failure scope-e.

Otázka:

```text
Je správny asset alebo business journey dostupný
pre oprávnený cohort v rámci latency, freshness, RTO a RPO contractu?
```

Availability nie je iba process uptime. Služba môže vracať `200`, ale byť nepoužiteľná pre vysokú latency, stale data, nefunkčnú authentication cestu, vyčerpanú quota alebo chýbajúcu kritickú operation.

Typické controls:

- fault isolation a redundancy;
- capacity, quotas a rate limits;
- failover a graceful degradation;
- credential, key a DNS availability;
- tested backup/restore;
- incident response a break-glass access;
- dependency a queue recovery;
- observability dostupná počas incidentu.

Availability control nesmie automaticky fail-open-nuť confidentiality alebo integrity boundary. Núdzový bypass musí mať explicitný threat model, scope, expiration a audit.

## 6. Security objectives a impact thresholds

CIA objective musí byť merateľný a viazaný na asset. Príklad pre `SEC-PAY-47`:

| Asset alebo process | Confidentiality objective | Integrity objective | Availability objective |
|---|---|---|---|
| Provider private key | nikdy exportovateľný mimo approved workload boundary | iba approved generation a rotation actor | signing/auth capability dostupná pre healthy settlement workers |
| Settlement route config | čitateľná iba payment/platform owners | zmena iba cez signed GitOps release a approved policy | last-known-good generation obnoviteľná do 15 minút |
| Final settlement | tenant data bez cross-tenant disclosure | exactly-once business outcome a reconciled provider state | 99.9 % valid settlements do 2.5 s |
| Security audit | need-to-know query access | append-oriented, actor a policy revision zachované | critical events queryovateľné počas incidentu |

Impact sa klasifikuje samostatne pre každú os. Public artifact môže mať low confidentiality, ale high integrity. Audit môže mať moderate confidentiality a high integrity aj availability.

## 7. Threat, vulnerability, exposure, impact a risk

Tieto pojmy netvoria synonymá:

- **threat** — actor, event alebo failure schopný spôsobiť škodu;
- **vulnerability** — slabina, ktorú možno využiť;
- **exposure** — konkrétna reachable alebo usable cesta k slabine;
- **impact** — následok straty CIA vlastnosti;
- **risk** — kombinácia pravdepodobnosti, podmienok, blast radiusu a impactu;
- **control** — safeguard znižujúci pravdepodobnosť alebo následok;
- **residual risk** — risk po zohľadnení effective controls.

Pre worked incident:

```text
threat: ukradnutá existujúca browser session
vulnerability: mover workflow ponechal starú nested-group membership
exposure: group claim mapovaný na broad Kubernetes operator binding
amplifier: create Pod + výber privileged ServiceAccountu
impact: secret disclosure + config mutation + settlement outage
```

## 8. Control system

Robustná security architektúra nepoužíva iba prevention:

```text
prevent
→ obmedziť vznik alebo využitie failure pathu

detect
→ zachytiť zmenu, pokus alebo stratu evidence

respond
→ zastaviť pokračujúci impact a zachovať dôkaz

recover
→ obnoviť dôveryhodnú generation a reconciled business state

learn
→ odstrániť systémovú príčinu a skrátiť budúce exposure window
```

Controls možno klasifikovať ako management, operational, technical alebo physical a podľa funkcie ako preventive, detective, corrective, recovery, deterrent či compensating. Kategória však nenahrádza exact boundary a ownera.

## 9. Assurance a effective control state

Assurance sú grounds for confidence, že security objectives sú v konkrétnej implementácii splnené.

```text
policy source existuje
→ validná generation bola publikovaná
→ controller alebo verifier ju načítal
→ PEP ju presadzuje na každej relevantnej ceste
→ allowed test funguje
→ forbidden test zlyhá
→ audit zachytí oba verdicts
→ recovery test obnoví business outcome
```

Dôkazy môžu zahŕňať:

- configuration a runtime read-back;
- positive a negative authorization tests;
- signature/provenance verification;
- tenant-isolation test;
- restore rehearsal;
- session revocation test;
- audit canary;
- incident history a recurrence controls.

`Backups enabled` nie je restore assurance. `MFA required` nie je dôkaz, že stale privileged session bola revoke-nutá. `Role removed` nie je dôkaz, že nested group, token cache a workload credential už neumožňujú alternate path.

## 10. Worked incident: jedna stale access cesta narušila C, I aj A

### Symptom

Dňa `2026-07-29` o `12:14 UTC` settlement-completion SLO začne prudko páliť. Súčasne security alert hlási čítanie `provider-a-mtls` secretu nezvyčajným Podom.

```text
final settlement failures: 8.2 %
settlement workers desired/available: 12/0
routing config loaded: SETTLEMENT-ROUTE-92
approved source generation: SETTLEMENT-ROUTE-91
new Pod: settlement-debug-7f91
```

### Recent identity change

Principal `urn:atlas:human:7421` bol o 08:00 presunutý z Payments Operations do Finance Analytics. HR source zmenu zaznamenal správne, ale identity synchronizácia bola add-only:

```text
removed direct group: payments-oncall
remaining nested path:
finance-emea
→ legacy-shared-operations
→ prod-payment-operators
```

Existujúca browser session navyše ostala platná.

### Competing hypotheses

1. provider outage spôsobil settlement failure;
2. GitOps rollout načítal chybnú route generation;
3. external attacker zneužil application API;
4. compromised workload prečítal secret nezávisle od human identity;
5. ukradnutá human session využila stale effective access;
6. audit event patrí legitimate incident drillu;
7. controller omylom scale-nul workers pri autoscaling-u.

### Discriminating evidence

```text
IdP authentication: WebAuthn success, session SESSION-771
session actor: urn:atlas:human:7421
HR mover state: Finance Analytics
IdP token claim: prod-payment-operators stále present
Kubernetes access path:
  subject
  → nested IdP group
  → payments-prod-operators ClusterRoleBinding
  → payments-prod-operator ClusterRole
allowed actions:
  create pods
  select serviceAccountName settlement-debug
  patch configmaps
  patch deployments/scale
Pod audit actor: urn:atlas:human:7421
Pod workload principal: system:serviceaccount:payments-prod:settlement-debug
secret read audit: workload principal
config patch audit: human principal
GitOps source: stále SETTLEMENT-ROUTE-91
```

Root cause je incomplete mover reconciliation. Broad operator role je causal amplifier. Authentication protocol fungoval; authorization a identity lifecycle už nereprezentovali aktuálnu pracovnú funkciu.

### CIA impact

**Confidentiality:** Pod získal provider client certificate a private-key capability.

**Integrity:** actor patchol settlement route na neapproved generation `92`.

**Availability:** actor znížil settlement workers na nulu a zastavil final completion.

Audit platforma zostala dostupná a append-oriented, preto bolo možné prepojiť human actor, vytvorený workload a následné secret use.

### Evidence-preserving containment

1. zablokovať session `SESSION-771` a všetky odvodené tokens;
2. suspendovať principal a odstrániť stale group path;
3. zastaviť nové Pod creates a config mutations pre affected binding;
4. izolovať malicious Pod bez mazania jeho metadata a runtime evidence;
5. zachovať IdP events, group graph, Kubernetes audit, Secret access, GitOps diff a settlement timeline;
6. nevymazať audit, nerestartovať všetky control planes a neudeliť broad emergency admin;
7. zastaviť provider-side použitie compromised certificate podľa dohodnutého incident contractu.

### Authoritative recovery

```text
revoke human sessions a stale entitlements
→ rotate provider credential generation 34 → 35
→ restore route config z signed source SETTLEMENT-ROUTE-91
→ reconcile Deployment na 12 workers
→ drain/reconcile pending settlement outcomes
→ overiť provider a ledger state
→ odstrániť broad operator role
→ zaviesť JIT mediated capability
```

Recovery musí rozlíšiť payments, ktoré zlyhali pred provider callom, payments s known failure a unknown acknowledgement outcomes. Blind retry môže vytvoriť duplicate authorization a integrity incident.

### Acceptance verdict

Incident možno uzavrieť, keď:

- valid enterprise settlement opäť prejde do 2.5 s;
- unknown outcomes sú reconciled bez duplicate provider authorization;
- generation `35` je jediná prijímaná provider credential;
- loaded route je zhodná so signed source generation `91`;
- principal `7421` nedokáže create Pod, read Secret, patch config ani scale Deployment;
- stará session, nový login a alternate nested-group path sú odmietnuté;
- legitimate JIT operator dokáže vykonať iba approved requeue/diagnostic task;
- audit chain zachová human actora, delegated workload, actions a policy revisions;
- druhý identity sync a druhý Kubernetes authorization test neobnovia stale access.

## 11. Earlier controls odvodené z incidentu

- mover reconciliation musí byť remove-before-add alebo transactional podľa entitlement graphu;
- entitlement source potrebuje complete desired state, nie add-only sync;
- privileged group change musí revoke-nuť sessions a short-lived claims;
- Kubernetes role engineering musí považovať workload creation za indirect escalation boundary;
- production support má používať mediated JIT capability, nie standing Pod/Secret access;
- policy CI musí testovať forbidden nested-group paths;
- session a entitlement canary má overiť leaver/mover revocation;
- audit musí korelovať human actor → delegated workload → downstream use;
- provider credentials musia byť rotation-ready a scoped na workload identity.

## 12. Trade-offy medzi C, I a A

Security decision často posilní jednu os a oslabí inú:

- strict deny môže chrániť confidentiality, ale znížiť availability bez break-glass modelu;
- replication zvyšuje availability, ale rozmnožuje confidentiality exposure a replikuje logical corruption;
- immutable retention chráni audit integrity, ale komplikuje privacy deletion;
- encryption chráni data at rest, ale strata key-u môže zničiť availability;
- broad emergency access môže obnoviť službu, ale poškodiť confidentiality, integrity a accountability.

Trade-off musí byť explicitný, bounded a validovaný. „Security first“ nie je ospravedlnenie pre nefunkčný systém; „availability first“ nie je ospravedlnenie pre fail-open nad citlivým assetom.

## 13. Security incident troubleshooting cez CIA

```text
business symptom a timeline
→ exact asset/process/security subject
→ narušená C, I a A vlastnosť
→ affected a unaffected cohorts
→ active threat a remaining exposure
→ volatile evidence
→ competing hypotheses
→ containment bez zničenia dôkazu
→ authoritative identity/data/config recovery
→ allowed, forbidden a adjacent validation
→ residual risk a closure
```

Neuzatváraj incident po obnovení availability. Compromised credential môže po scale-up-e stále čítať dáta alebo meniť state.

## 14. Anti-patterny

### CIA ako checkbox

Tri písmená sa uvedú v dokumente bez assets, impactu, controls a evidence.

### Encryption = confidentiality solved

Ignoruje plaintext use, authorization, exporty a key-use capabilities.

### Uptime = availability

Ignoruje latency, correctness, identity path, freshness a cohort-specific failure.

### Control existence = assurance

Configured policy alebo backup nie je effective-state ani recovery dôkaz.

### Restore availability bez integrity reconciliation

Služba sa spustí, ale spracuje unknown alebo stale business state nesprávne.

### Maximalizácia jednej osi

Broad fail-open, permanent lockout alebo nekonečná retention môžu poškodiť ostatné security a business objectives.

## 15. Kontrolné otázky

1. Čo tvorí exact CIA security subject?
2. Prečo je CIA vlastnosť vždy viazaná na asset a outcome?
3. Ako sa líši threat, vulnerability, exposure, impact a risk?
4. Prečo configured control nie je assurance?
5. Ako confidentiality zahŕňa aj použitie capability bez exportu secretu?
6. Ako integrity súvisí s identity, provenance a reconciliation?
7. Prečo availability nie je iba uptime?
8. Ako môže jeden stale entitlement narušiť všetky tri osi?
9. Čo musí zachovať evidence-preserving containment?
10. Prečo sa credential incident neuzatvára po obnovení služby?
11. Aké forbidden outcomes musí recovery testovať?
12. Ktoré earlier controls vyplývajú z incidentu `SEC-PAY-47`?

## Glossary impact

Relevantné pojmy: CIA security subject, confidentiality objective, integrity objective, availability objective, asset-impact matrix, capability confidentiality, control generation, effective security control, security assurance verdict, residual-risk verdict, evidence-preserving security containment, authoritative security recovery, identity-to-workload audit chain a CIA acceptance verdict.

## Primárne zdroje

- [NIST — Confidentiality, Integrity and Availability](https://csrc.nist.gov/glossary/term/confidentiality_integrity_availability)
- [NIST — Information Security](https://csrc.nist.gov/glossary/term/information_security)
- [NIST — Security Control](https://csrc.nist.gov/glossary/term/security_control)
- [NIST — Security Assurance](https://csrc.nist.gov/glossary/term/security_assurance)
- [NIST SP 800-53 Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cardinality](../12-observability/cardinality.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Authentication, authorization a auditing →](authentication-authorization-auditing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
