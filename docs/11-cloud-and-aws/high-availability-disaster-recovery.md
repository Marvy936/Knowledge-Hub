# High availability a disaster recovery

High availability (HA) a disaster recovery (DR) riešia odlišné failure scopes. HA udržiava alebo automaticky obnovuje business outcome pri očakávateľnom lokálnom zlyhaní. DR obnovuje business capability po strate primárneho prostredia, dát alebo trust modelu podľa explicitných RTO a RPO.

Dominantný lifecycle:

```text
business capability a impact analysis
→ dependency, state a trust inventory
→ failure a disaster scenarios
→ availability/RTO/RPO contract
→ HA a DR strategy
→ backup/replication/isolation evidence
→ detection a declaration
→ recovery point selection a environment activation
→ data/application/identity reconciliation
→ traffic cutover a business validation
→ failback, evidence a improvement
```

## 1. Exact recovery subject

Atlas Payments používa recovery subject `REC-PAY-42`:

```text
business capability = authorize and settle payment exactly once
primary Region = eu-central-1
recovery Region = eu-west-1
release generation = PAY-4.2.0
primary data generation = ledger checkpoint L842 + event offset E91
recovery artifact set = chart/image/IaC/PKI/secret generations R57
backup generation = B2026-07-28T0030Z
replication checkpoint = RC-842991
RTO = 45 min
RPO = 5 min
minimum recovered capacity = 40 % peak with settlement queue preserved
recovery owner = Payments Incident Commander
forbidden outcomes = duplicate authorization, settlement loss, stale credential reuse
```

RTO alebo RPO bez presného capability a state subjectu nie sú overiteľné.

## 2. Availability je user outcome

Process, instance alebo load balancer môže byť healthy, ale platba nemusí byť autorizovaná. Availability preto definuje:

- measurement point;
- oprávneného clienta;
- úspešný outcome;
- latency/error boundary;
- scope a failure domains;
- partial degradation;
- forbidden business result.

```text
availability = successful valid operations / all valid operations
```

HA sa uzatvára na tomto outcome-e, nie na počte running resources.

## 3. High availability lifecycle

```text
healthy redundant capacity
→ component/AZ failure detection
→ traffic alebo leadership withdrawal
→ surviving-capacity check
→ state failover/fencing
→ client retry alebo reconnect
→ business outcome verification
→ failed component replacement
→ redundancy restoration
```

HA design musí uviesť tolerovaný scope. Multi-AZ nerieši automaticky Region outage, logical corruption, account compromise, KMS deletion ani chybný deployment aplikovaný do všetkých AZ.

### Statically stable recovery

Pri výpadku control plane-u nemusí byť možné rýchlo launchovať novú kapacitu. Kritická služba preto potrebuje minimálnu už pripravenú data-plane kapacitu schopnú prežiť definovaný failure, nie iba presvedčenie, že Auto Scaling ju počas incidentu doplní.

## 4. HA nie je DR

HA typicky používa aktuálny production state. DR môže vyžadovať starší dôveryhodný recovery point a nové prostredie.

Replication znižuje RPO, ale prenáša aj deletion, ransomware alebo logical corruption. Backup zachová starší point, ale restore môže mať vyššie RTO. Robustný model kombinuje replication, versionované izolované backupy a testovanú application recovery.

## 5. Business Impact Analysis, RTO a RPO

### Business Impact Analysis

BIA určuje:

- kritické capabilities a dependencies;
- maximum tolerable downtime;
- tolerovanú data loss;
- právne a bezpečnostné povinnosti;
- manuálne workaroundy;
- poradie obnovy;
- minimálnu funkčnú kapacitu.

### RTO

RTO zahŕňa celý čas:

```text
detection
+ escalation/declaration
+ provisioning alebo promotion
+ restore/replay
+ application startup
+ validation
+ traffic cutover
= recovery time actual
```

### RPO

RPO určuje maximálnu tolerovanú stratu state-u. Posledný dokončený backup job ešte nepreukazuje použiteľný recovery point. Potrebný je decryptable, integrity-valid a application-consistent point s preukázaným restore pathom.

### RTA a RPA

Recovery Time Actual a Recovery Point Actual sú dôkazom, či architektúra a proces reálne spĺňajú cieľ.

## 6. Recovery-set contract

Obnoviteľná služba potrebuje viac než databázový snapshot:

```text
data a transaction logs
+ IaC a account/network baseline
+ immutable application artifacts
+ configuration a secrets
+ KMS/PKI recovery path
+ DNS/certificates
+ IAM a organization guardrails
+ external integration state
+ observability a runbooks
+ owners a approvals
= recovery set
```

Každá položka má version, ownera, location, retention, encryption a restore dependency.

## 7. DR stratégie

| Stratégia | Prepared state | Typický trade-off |
|---|---|---|
| Backup and restore | backupy a IaC, minimálna active infra | najnižší steady cost, najvyššie RTO |
| Pilot light | kritický state layer beží | nižšie RTO, riziko scale-up/capacity driftu |
| Warm standby | zmenšená funkčná kópia | priebežné testy, vyšší cost |
| Multi-site active-active | viac lokalít obsluhuje traffic | najnižšie RTO, najťažšia consistency a failback |

Stratégia sa vyberá podľa BIA, nie podľa prestíže architektúry.

## 8. Connected walkthrough — Region je healthy, ale recovery je nepoužiteľná

### Symptom

Security incident kompromituje primary account a deployment credentials. Incident commander deklaruje DR do `eu-west-1`. Database restore a application startup prebehnú za 28 minút, ale payment traffic nemožno bezpečne otvoriť ani po 90 minútach.

### Competing hypotheses

1. Backup je poškodený.
2. Recovery KMS key alebo policy neumožňuje decrypt.
3. Recovery Region nemá quota/subnet capacity.
4. DNS alebo certificate cutover nie je pripravený.
5. Secrets sú iba replikované z kompromitovaného source-u.
6. Restored ledger a queue offsets patria k rozdielnym recovery points.
7. External payment provider nepovoľuje recovery egress identity.
8. Starý primary writer stále beží.
9. Recovery runbook počítal iba database restore, nie trust recovery.

### Discriminating observations

| Observation | Čo rozlišuje |
|---|---|
| backup manifest, checksum a restore logs | byte integrity od application validity |
| KMS key/account/policy generation | data availability od decrypt authorization |
| ledger checkpoint a queue offset | konzistentný state od mixed recovery points |
| primary writer fencing evidence | single-writer recovery od split brainu |
| recovery secret provenance a issuance time | čistý trust state od kompromitovanej repliky |
| quotas, subnet IPs a launch failures | artifact/data problem od capacity problemu |
| DNS/certificate generations a client TLS | running app od reachable trusted service |
| provider allowlist/request IDs | internal readiness od external integration blocku |

### Finding

Database snapshot bol validný, ale recovery Secrets Manager replica obsahovala credentials vydané pred compromise a provider ich zablokoval. Ledger snapshot `L842` bol navyše spárovaný s queue offsetom z neskoršieho checkpointu. Technický restore bol zelený, recovery set však nebol konzistentný ani dôveryhodný.

### Containment

- neotvárať production traffic;
- hard-fence primary writers a revoke kompromitované credentials;
- zachovať backup/replication/KMS/IAM/CloudTrail evidence;
- izolovať recovery account od compromised automation;
- zastaviť automatické prepisovanie recovery configu source stavom.

### Recovery

1. Vybrať canonical recovery point s viazaným ledger/queue manifestom.
2. Obnoviť do izolovaného recovery accountu/Regionu.
3. Vydať nové credentials a certificates z čistého trust rootu.
4. Reconciliovať external provider, pending operations a exactly-once ledger.
5. Spustiť minimum capacity a synthetic payment bez real charge side effectu.
6. Otvárať traffic po bounded cohorts.
7. Merať RTA/RPA a deklarovať odchýlku od RTO/RPO.

### Verification

Recovery je prijatá až keď:

- payment authorization a settlement fungujú end-to-end;
- old credentials sú odmietnuté;
- primary writer je preukázateľne fenced;
- ledger a queue state sú konzistentné;
- pending operations sú reconciled bez duplicít;
- recovery capacity spĺňa minimum;
- monitoring, audit a incident access fungujú;
- duplicate payment zostáva forbidden outcome.

## 9. Failover a failback

Failover určuje presun authority a trafficu do recovery prostredia. Failback nie je jednoduché prepnutie DNS späť.

```text
stabilizácia recovery prostredia
→ určenie authoritative state-u
→ synchronizácia alebo export delta
→ kompatibilita primary environmentu
→ controlled traffic shift
→ single-writer verification
→ retirement temporary recovery paths
```

Bez authority a data-generation contractu môže failback vytvoriť stratu alebo split brain.

## 10. Recovery testing

Test musí zahŕňať:

- detection a declaration latency;
- access pri nedostupnom primary identity plane;
- clean-account/Region provisioning;
- quota a capacity;
- KMS/PKI/Secrets recovery;
- application-consistent restore;
- DNS a certificate cutover;
- external integrations;
- business transaction a forbidden outcomes;
- failback;
- evidence retention a cleanup.

Tabletop bez restore nie je recovery test. Restore bez business validation tiež nie.

## 11. Earlier controls

- versionovaný BIA a dependency map;
- recovery-set manifest;
- off-account/off-Region immutable backup;
- oddelené recovery identities a keys;
- pravidelné restore a game-day testy;
- static minimum recovery capacity;
- explicitný fencing a single-writer protocol;
- pre-approved DNS/certificate/provider paths;
- merané RTA/RPA;
- post-test improvement owners a deadlines.

## 12. Kontrolné otázky

1. Aký failure scope rieši HA a aký DR?
2. Ktorý business capability a state generation sa obnovuje?
3. Čo presne znamenajú RTO a RPO v end-to-end čase?
4. Je recovery point application-consistent?
5. Sú backups oddelené od production identity a failure domainu?
6. Ktoré credentials a trust roots treba obnoviť?
7. Ako sa preukáže single writer?
8. Aká minimálna capacity musí existovať bez control-plane scale-outu?
9. Ako sa overí external integration a exactly-once outcome?
10. Ako prebehne bezpečný failback?

## Glossary impact

Relevantné pojmy: business recovery subject, recovery-set manifest, recovery authority, RTA, RPA, application-consistent recovery point, clean trust generation, statically stable recovery capacity, disaster declaration boundary, traffic-reopen verdict, single-writer recovery a failback authority transfer.

## Oficiálna dokumentácia

- [Disaster recovery options in the cloud](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)
- [Disaster recovery objectives](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/disaster-recovery-dr-objectives.html)
- [Plan for disaster recovery](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/plan-for-disaster-recovery-dr.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Scalability, elasticity a fault tolerance](scalability-elasticity-fault-tolerance.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: AWS Organizations a accounts →](aws-organizations-accounts.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
