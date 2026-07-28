# CloudOps domain review a timed reasoning

CloudOps domain review trénuje decision protocol pre AWS Certified CloudOps Engineer – Associate `SOA-C03`. Scenario question nie je hádanka o názve služby. Je to časovo obmedzený architecture alebo operations decision nad konkrétnym subjectom, constraints a failure boundary. Správna odpoveď musí vytvoriť complete path a zároveň odmietnuť možnosti, ktoré sú síce technicky možné, ale porušujú scope, operational-effort, security, reliability alebo cost contract.

## 1. Dominantný model: question-to-verdict lifecycle

```text
exact question a option generation
→ requested business/operational outcome
→ explicit a implicit constraints
→ scope, responsibility a failure boundary
→ required control/data/recovery path
→ candidate-answer mechanisms
→ completeness a trade-off evaluation
→ distractor elimination
→ provisional answer a confidence
→ time-budget decision
→ post-set error provenance a model remediation
```

Keyword môže pomôcť nájsť oblasť, ale nesmie nahradiť path reasoning. Ak otázka spomenie CloudWatch, správnou odpoveďou môže byť CloudTrail, Config alebo service-specific log, pretože skutočný outcome je audit, configuration history alebo packet evidence.

## 2. Exact question subject

Pri review nezapisuj iba číslo otázky a správne písmeno. Zachovaj:

```text
practice source/version:
question ID a generation:
SOA-C03 domain/task:
question type: single-response | multiple-response
requested outcome:
positive constraints:
negative constraints:
scope/account/Region/AZ/resource:
control/data/recovery boundary:
selected answer(s):
confidence: H | M | L
time spent:
answer mechanism:
distractor failure reason:
error provenance:
authoritative chapter/lab/drill:
```

Ak practice provider otázku neskôr upraví, stará explanation bez generation identity už nemusí patriť k rovnakému stemu alebo options.

## 3. Intake protocol: najprv outcome, nie služba

Prvé čítanie má odpovedať na šesť otázok:

1. Aký stav musí byť po zmene alebo recovery pravdivý?
2. Ktoré stavy musia zostať zakázané?
3. Aký je scope: resource, AZ, Region, account, organization alebo multi-Region?
4. Ide o create/configure, observe, troubleshoot, optimize, contain alebo recover?
5. Ktorá vrstva je customer-owned a ktorá service-managed?
6. Ktorý qualifier rozhoduje medzi viacerými funkčnými možnosťami?

Až potom sa mapujú AWS services.

## 4. Constraint extraction

Constraints majú mechanický dopad na odpoveď:

- **least operational overhead** preferuje presnú managed capability pred custom fleetom;
- **most cost-effective** vyžaduje splniť outcome, nie iba vybrať najnižšiu unit price;
- **without downtime** vylučuje destructive replacement bez parallel generation alebo failover pathu;
- **automatically** vyžaduje event/signal, target, authorization, execution a validation chain;
- **near real time** môže vylúčiť lagged billing alebo batch reporting data;
- **private connectivity** vylučuje general internet path aj vtedy, keď je šifrovaný;
- **least privilege** vylučuje broad wildcard alebo AdministratorAccess remediation;
- **meet RPO/RTO** vyžaduje recovery frequency aj realizovateľný restore/cutover time;
- **retain evidence** môže vylúčiť immediate delete/restart/reset;
- **resilient to one AZ failure** vyžaduje, aby dependent zonal components neboli spoločným single pointom.

Technicky funkčná odpoveď, ktorá poruší qualifier, je distractor.

## 5. Scope a subject identity

AWS názvy sa opakujú medzi scopes. Preto otázku prelož na exact subject:

```text
payer/organization/account
→ Region
→ VPC/AZ/subnet
→ resource ARN/ID/generation
→ listener/route/policy/key/backup/secret version
→ workload request alebo recovery operation
```

Príklady scope chyby:

- AMI ID je regionálny; existence v jednom Regione nepreukazuje existence v druhom;
- EBS volume aj EC2 attachment sú zonálne;
- ACM certificate pre CloudFront potrebuje service-specific Region contract;
- KMS key a Secrets Manager secret sú regionálne resources;
- SCP je organization guardrail, nie identity permission grant;
- Security Group je ENI/resource boundary, NACL subnet boundary.

## 6. Control plane, data plane a recovery plane

### Control plane

API, configuration, policy, deployment alebo management operation. Príklad: `UpdateStack` zlyhá na `iam:PassRole`, hoci existujúca aplikácia stále obsluhuje traffic.

### Data plane

Reálny request, packet, storage I/O, database transaction alebo message processing. Príklad: EC2 API funguje, ale HTTPS request timeoutuje pre route alebo return-path failure.

### Recovery plane

Výber recovery pointu, restore authorization, dependency recreation, data validation, fencing a cutover. Príklad: backup job je `COMPLETED`, ale restore nemá KMS access alebo business state je nekonzistentný.

Odpoveď musí zasiahnuť správnu rovinu. Zmena CloudFormation template nevyrieši current packet drop, ak data-plane route zostáva chybná. Reštart databázy nevyrieši nesprávny restore subject.

## 7. Complete-path test

Pred výberom odpovede rozlož požadovanú capability na kroky.

### Automated remediation

```text
correct signal/event identity
→ evaluation alebo pattern match
→ authorized target invocation
→ bounded/idempotent execution
→ target mutation
→ outcome validation
→ failure/dead-letter/escalation evidence
```

### Private AWS-service access

```text
client subnet a DNS
→ correct gateway/interface endpoint type
→ route alebo endpoint ENI
→ SG/NACL
→ endpoint policy
→ service/resource policy
→ IAM/KMS authorization
```

### Highly available private IPv4 egress

```text
private workload in each AZ
→ AZ-local private route table
→ healthy public NAT Gateway in same AZ
→ public-subnet route to IGW
→ SG/NACL/DNS
→ third-party destination
→ return path
```

### Recoverable database

```text
RPO/RTO contract
→ capture/replication generation
→ retained clean point
→ KMS/restore permissions
→ restore capacity/network/config
→ application/schema validation
→ reconciliation
→ cutover/failback
```

Option, ktorá rieši iba jeden box, nie je complete answer pre celý outcome.

## 8. Candidate-answer evaluation

Každú možnosť posúď samostatne:

1. **Mechanism:** Ako presne vytvorí požadovaný outcome?
2. **Scope:** Operuje v správnom account/Region/AZ/resource boundary?
3. **Completeness:** Obsahuje všetky potrebné dependencies?
4. **Constraint fidelity:** Spĺňa explicitné qualifiers?
5. **Failure model:** Odstraňuje požadovaný failure alebo iba symptom?
6. **Trade-off:** Nepridáva nepožadovaný cost, toil, exposure alebo single point?
7. **Forbidden outcome:** Nevytvára public path, broad permission, data loss alebo unbounded automation?

Pri multiple-response otázke musí zvolená kombinácia tvoriť complete chain. Dve samostatne pravdivé options nemusia byť správna dvojica.

## 9. Worked question: resilient private egress

### Stem

Atlas Payments prevádzkuje settlement workers na EC2 instances v private subnetoch v `eu-central-1a` a `eu-central-1b`. Workers volajú externého payment providera cez IPv4. Nesmú mať public IPv4 addresses ani inbound internet path. Failure jednej Availability Zone nesmie prerušiť outbound connectivity workerov v druhej AZ. Tím požaduje managed riešenie s najnižším operational overheadom.

Ktorá architektúra spĺňa požiadavky?

### Options

A. Jeden public NAT Gateway v `eu-central-1a`; oba private subnety smerujú default route na tento NAT Gateway.

B. Jeden NAT instance v `eu-central-1a` s Auto Recovery; oba private subnety smerujú cez túto instance.

C. Public NAT Gateway v každej AZ; každý private subnet používa AZ-local NAT Gateway a každý public subnet má route na Internet Gateway.

D. Internet Gateway pripojený k VPC; instances dostanú public IPv4 addresses, ale inbound Security Group rules zostanú prázdne.

E. Egress-only Internet Gateway a IPv6-only default route pre workers.

### Outcome a constraints

```text
outcome: outbound IPv4 k external providerovi
positive constraints: managed, AZ-resilient, no inbound internet
negative constraints: no public IPv4 on workers
scope: two AZs in one Region
failure boundary: loss of either AZ
```

### Path analysis

Option A poskytne outbound IPv4, ale `eu-central-1b` závisí od NAT Gateway v AZ `a`. Failure AZ `a` odstráni egress aj zdravým workerom v AZ `b`. Navyše vytvára cross-AZ traffic path.

Option B používa custom EC2 appliance. Auto Recovery nerobí z jednej zonálnej NAT instance multi-AZ service a pridáva patching, scaling, connection tracking a failover ownership. Porušuje least operational overhead.

Option C vytvára dve nezávislé zonálne egress paths. Worker nemá public address; NAT Gateway vytvára outbound translation a local route obmedzuje cross-AZ dependency. To je complete path pre stated failure model.

Option D môže blokovať unsolicited inbound cez Security Group, ale explicitne porušuje zákaz public IPv4 a mení private workload boundary.

Option E rieši outbound IPv6, nie požadované IPv4 volanie. Je správnou capability pre iný address-family contract.

### Verdict

Správna odpoveď je **C**. Dôvod nie je iba „NAT Gateway je managed“. Rozhodujúca je kombinácia AZ-local dependency, IPv4 translation, absence public addressing na workers a zachovanie connectivity pri strate jednej AZ.

### Forbidden validation

Pri praktickom overení nestačí, že HTTPS request funguje. Musí platiť aj:

- worker nemá public IPv4;
- subnet `a` nepoužíva NAT v `b` a opačne;
- po izolovaní egress pathu AZ `a` zostane AZ `b` funkčná;
- neexistuje inbound listener path z internetu na workers.

## 10. Domain reasoning cez ten istý protocol

### Domain 1 — monitoring, analysis a remediation

Najprv urč question type: metric state, logs, API audit, configuration history, packet flow alebo performance bottleneck. Potom zostav signal-to-action path. CloudTrail odpovie „kto zmenil route table“; Flow Logs pomôžu zistiť accept/reject flow; CloudWatch metric ukáže NAT port allocation errors. Žiadny z týchto sources sám nepokrýva všetky tri otázky.

### Domain 2 — reliability a business continuity

Rozlišuj current availability od historical recovery. Multi-AZ znižuje zonálny outage risk, ale nerevertuje logical deletion. Replication skracuje RPO pre niektoré failures, ale môže preniesť corruption. Odpoveď musí spĺňať konkrétny RPO/RTO aj clean-state requirement.

### Domain 3 — deployment a automation

Rozlišuj desired-state source, execution engine a realized workload. CloudFormation change set ukazuje planned stack delta; nepreukazuje, že bootstrap, target health alebo business journey po update fungujú. Automation odpoveď potrebuje execution role, target scope, concurrency/error bounds a validation.

### Domain 4 — security a compliance

Pri `AccessDenied` rozbaľ caller, action/resource, explicit denies, required allows, trust/PassRole, boundary/session/SCP/RCP, resource policy, KMS a request conditions. IAM role s `kms:Decrypt` nemusí stačiť, ak key policy delegation alebo encryption-context condition nesedí.

### Domain 5 — networking a content delivery

Nakresli packet, DNS a return path. Public subnet nie je synonymom internet-reachable resource-u. ALB health, target SG, target port, application bind a health endpoint tvoria samostatné gates. CloudFront behavior match a cache key sú iný algorithm než Route 53 routing.

## 11. Distractor taxonómia

Najčastejšie distractors:

- **wrong scope** — account control použitý na organization problém alebo zonálny resource na multi-AZ contract;
- **half path** — route bez gateway, alarm bez action role, backup bez restore dependencies;
- **configured-not-effective** — resource existuje, ale runtime ho nepoužíva;
- **symptom repair** — restart alebo scale-up bez identifikácie bottlenecku;
- **security bypass** — broad permission alebo `0.0.0.0/0` namiesto exact fixu;
- **custom when managed is required** — vlastný fleet pri explicitnom least-overhead constraint-e;
- **HA/DR confusion** — replica alebo Multi-AZ ponúknuté na historical clean recovery;
- **wrong evidence source** — CloudWatch na actor audit alebo CloudTrail na packet payload;
- **stale capability assumption** — odpoveď založená na starom exam guide alebo retired service behavior;
- **locally optimal trade-off** — najnižší cost, ale nesplnené RTO, security alebo performance.

## 12. Multiple-response chain

Pri otázke „Select TWO“ postupuj takto:

```text
required path boxes
→ každá option mapovaná na box
→ odstráň options mimo scope
→ nájdi minimálnu kombináciu pokrývajúcu všetky boxes
→ over, že options si neprotirečia
→ over forbidden outcome
```

Napríklad central cross-account CloudTrail delivery do encrypted bucketu môže vyžadovať organization trail konfiguráciu **a** destination bucket/KMS policies. Dve monitoring služby nie sú správna dvojica, ak chýba delivery authorization.

## 13. Time-budget state machine

130 minút na 65 questions je priemer dve minúty na question, nie povinný limit každej otázky.

```text
read a classify
→ solve now | mark and defer
→ provisional answer + confidence
→ continue
→ second-pass deep reasoning
→ final consistency review
```

Praktický tréning:

- jasná single-response question: približne 45–75 sekúnd;
- stredný scenario path: približne 90–150 sekúnd;
- dlhá multiple-response question: bounded deep pass, potom defer;
- posledná časť: označené questions, negative qualifiers a accidental omissions.

Time collapse vzniká, keď jedna neistá otázka spotrebuje čas potrebný na viac riešiteľných questions. Defer nie je vzdanie sa; je to queue prioritization.

## 14. Confidence ako evidence

Po answer selection označ:

- `H` — mechanizmus aj distractors vieš vysvetliť;
- `M` — answer path je pravdepodobný, ale jeden detail nie je stabilný;
- `L` — elimination alebo guess bez plného modelu.

Interpretácia:

| Výsledok | Význam |
|---|---|
| correct + H | stabilný model, stále kontroluj source freshness |
| correct + L | náhodná alebo slabá schopnosť; potrebuje review |
| wrong + L | viditeľný knowledge gap |
| wrong + H | chybný mentálny model s vysokou remediation prioritou |

Confidence sa nesmie meniť spätne podľa toho, či answer vyšiel správne.

## 15. Post-set error provenance

Review musí nájsť failure mechanism:

```text
wrong answer
→ knowledge alebo reading?
→ missed exact qualifier?
→ wrong scope/plane?
→ incomplete path?
→ stale service assumption?
→ trade-off error?
→ time-pressure behavior?
→ authoritative model a practical drill
→ re-test na novom scenario
```

Kopírovanie správnej explanation do poznámok neuzatvára gap. Closure vyžaduje, aby kandidát vyriešil nový variant bez phrasing recognition.

## 16. Timed set progression

### Set A — 20 questions / 35 minút

Trénuje intake protocol, scope a základnú elimination. Po každej otázke môže nasledovať detailný review.

### Set B — 35 questions / 65 minút

Obsahuje domain mix a aspoň niekoľko multiple-response chains. Review sa robí až po dokončení setu.

### Set C — 65 questions / 130 minút

Plná simulácia podľa current blueprintu `22/22/22/16/18`. Používa neznámy set, exam-like interruption discipline a záverečný confidence/error report.

Progress sa nemeria iba score. Sleduj:

- unfinished questions;
- time by question class;
- wrong + high confidence;
- domain/task gaps;
- answer changes bez novej evidence;
- incomplete-path errors;
- practical evidence chýbajúce k danému modelu.

## 17. Question review record

```text
Question subject/generation:
Domain/task:
Outcome:
Allowed a forbidden outcomes:
Constraints:
Scope/plane:
Required path:
Selected answer(s):
Confidence/time:
Correct mechanism:
Distractor mechanisms:
Error provenance:
Authoritative chapter:
Lab/drill:
Re-test result:
```

## 18. Anti-patterny

### Service keyword matching

Vyberie službu spomenutú v stem-e bez overenia requested outcome-u.

### Najkomplexnejšia architektúra ako najlepšia

Viac components môže zvyšovať cost, toil a failure surface bez požadovaného benefitu.

### Lowest cost bez outcome flooru

Najlacnejšia možnosť, ktorá poruší availability alebo security, nie je cost-effective riešenie.

### Review odpovede iba podľa správneho písmena

Nevysvetlí mechanismus ani dôvod nesprávnosti distractorov.

### Zmena answer pre pocit neistoty

Answer sa má meniť iba po nájdení missed constraintu, scope correction alebo technical contradiction.

### Ignorovanie negative qualifiers

`without public internet`, `must retain evidence` alebo `must not interrupt production` často určuje celý design.

### Practice bank repetition ako progress

Recognition zvyšuje score bez zlepšenia transferu na nový scenario.

## 19. Kontrolné otázky

1. Čo tvorí exact question subject?
2. Prečo sa outcome identifikuje pred service keywordom?
3. Ako qualifier mení technicky funkčnú odpoveď na distractor?
4. Aký je rozdiel medzi control, data a recovery plane?
5. Čo je complete-path test?
6. Ako sa vyhodnocuje multiple-response kombinácia?
7. Prečo correct + low confidence potrebuje remediation?
8. Čo je wrong-scope distractor?
9. Kedy má kandidát question defer-nuť?
10. Ako sa error uzavrie na novom scenario?

## Glossary impact

Relevantné pojmy: question-decision subject, outcome-first parsing, constraint extraction, negative qualifier, scope verdict, control/data/recovery plane classification, complete-path test, candidate mechanism evaluation, distractor taxonomy, multiple-response chain, time-budget state machine, confidence evidence, high-confidence wrong answer a question-error closure.

## Oficiálne zdroje

- [SOA-C03 exam guide](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03.html)
- [Domain 1](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain1.html)
- [Domain 2](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain2.html)
- [Domain 3](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain3.html)
- [Domain 4](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain4.html)
- [Domain 5](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain5.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: AWS Certified CloudOps Engineer – Associate (SOA-C03)](cloudops-engineer-associate-soa-c03.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CloudOps hands-on labs →](cloudops-hands-on-labs.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
