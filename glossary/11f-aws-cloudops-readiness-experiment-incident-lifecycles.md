# AWS CloudOps readiness, experiment and incident glossary entries

## SOA-C03 capability contract

Versionovaný súbor role outcomes, exam domains, task statements, service scope a reasoning expectations, ktoré má kandidát pre aktuálnu AWS Certified CloudOps Engineer – Associate exam generation preukázať. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Exam-guide generation — SOA-C03

Konkrétna revision AWS SOA-C03 exam guide-u s publication date, domain/task obsahom a in-scope/out-of-scope service inventory, ku ktorej musí byť viazaný study a readiness evidence. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Certification readiness subject

Exact kombinácia exam-guide generation, practice source/set identity, domain distribution, score, confidence profile, timing a linked practical evidence používaná pre readiness decision. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Authoritative knowledge mapping — SOA-C03

Mapovanie current exam task statements na authoritative Knowledge Hub kapitoly a ich lifecycle/failure models namiesto vytvárania paralelných skrátených service definícií. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Practical evidence inventory — SOA-C03

Versionovaný zoznam dokončených labov, fault drills, CLI/API evidence, pozitívnych a forbidden-outcome tests pre jednotlivé exam domains a capability boundaries. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Weighted domain gap — SOA-C03

Readiness medzera posudzovaná podľa domain weightu, severity mental-model chyby, practical-evidence coverage a time stability, nie iba podľa počtu nesprávnych odpovedí. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Domain floor — certification readiness

Minimálna akceptovateľná capability úroveň v každej významnej domain, ktorá bráni silnému celkovému priemeru skryť kritický security, recovery, automation alebo networking gap. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## High-confidence wrong model

Nesprávna odpoveď alebo operational decision vykonaná s vysokou confidence, indikujúca stabilný chybný mentálny model s vyššou remediation prioritou než neistý knowledge gap. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Error provenance — certification

Klasifikácia mechanizmu chyby, napríklad stale guide assumption, missed constraint, wrong scope, incomplete path, policy error, trade-off error alebo time-budget failure. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Readiness state machine — SOA-C03

Riadený prechod `Not mapped → Knowledge mapped → Practiced → Timed → Evidence reviewed → Ready`, kde každý stav vyžaduje explicitný evidence gate. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Readiness acceptance contract — SOA-C03

Podmienky pre interný ready verdict zahŕňajúce current guide, stable simulations, domain floor, explainability, remediation high-confidence errors, practical evidence a time stability. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Exam-version staleness

Stav, keď study material, question explanation alebo service assumption vychádza zo staršej exam generation a už nemusí zodpovedať current task alebo service scope-u. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Question-decision subject — CloudOps

Exact practice question generation spolu s outcome, constraints, scope, plane, options, confidence, time a post-answer error evidence. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Outcome-first parsing — CloudOps

Question intake discipline, pri ktorej sa pred service keywordom identifikuje požadovaný stav, zakázané stavy, scope, operation type a rozhodujúce qualifiers. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Negative qualifier — exam reasoning

Explicitná podmienka ako `without public internet`, `must retain evidence` alebo `without downtime`, ktorá vylučuje inak technicky funkčné candidate solutions. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Scope verdict — CloudOps question

Rozhodnutie, či je subject a požadovaný control resource-, AZ-, Region-, account-, organization- alebo multi-Region scoped. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Control/data/recovery plane classification — AWS

Klasifikácia question alebo incidentu podľa toho, či zlyháva API/configuration path, runtime traffic/state path alebo clean-point/restore/cutover path. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Complete-path test — CloudOps

Overenie, že candidate answer pokrýva všetky required mechanism boxes od source/authorization cez realization po validation, nie iba jeden component. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Candidate mechanism evaluation

Posúdenie answer option podľa mechanizmu, scope-u, completeness, constraint fidelity, failure modelu, trade-offu a forbidden outcomes. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Distractor taxonomy — CloudOps

Kategórie nesprávnych options ako wrong scope, half path, configured-not-effective, symptom repair, security bypass, HA/DR confusion alebo locally optimal trade-off. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Multiple-response chain — CloudOps

Minimálna konzistentná kombinácia answer options, ktorá spoločne realizuje všetky required path boxes bez contradiction alebo forbidden outcome-u. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Time-budget state machine — CloudOps exam

Question workflow `read/classify → solve alebo defer → provisional answer/confidence → second pass → consistency review`, ktorý chráni celý exam queue pred time collapse. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Confidence evidence — question review

Confidence označená pri answer selection pred známym výsledkom a používaná na rozlíšenie stable capability, guessing, knowledge gapu a high-confidence wrong modelu. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Question-error closure

Uzavretie reasoning chyby až po oprave autoritatívneho modelu a úspešnom vyriešení nového scenario variantu bez phrasing recognition. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## CloudOps lab subject

Exact lab identity zahŕňajúca outcome, forbidden outcomes, account/Region, caller, source generation, expected resources, cost guardrails, expiry a evidence destinations. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Lab generation — CloudOps

Jedna versionovaná realizácia lab manifestu, resources, configuration, fault a evidence, oddelená od predchádzajúcich alebo paralelných pokusov. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Financial safety boundary — AWS lab

Kombinácia sandbox isolation, bounded permissions/quotas, budget signals, TTL, cost-driver observation a cleanup contractu obmedzujúca finančný blast radius experimentu. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Expected resource manifest — CloudOps lab

Vopred deklarovaný inventory resource names/ARNs, Regions/AZs, dependencies, retained evidence a expected cost drivers používaný pri validation a cleanup-e. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Baseline contract — CloudOps lab

Dôkaz, že exact lab generation, data/control paths, telemetry, security negative tests a cleanup path fungujú pred fault injection. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Controlled fault generation

Jedna zámerná versionovaná mutation s expected affected scope, symptom, observation points, abort condition a reset/recovery pathom. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Lab abort condition

Vopred definovaný impact, spend, exposure alebo control-loss threshold, pri ktorom sa experiment zastaví a prejde na containment/recovery. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Discriminating lab observation

Metric, event, API field, log alebo request result, ktorý odlíši minimálne dve plausible hypotheses o vloženom failure mechanizme. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Forbidden-outcome test — CloudOps lab

Explicitný test, že remediation nevytvorila public exposure, broad permission, duplicate side effect, missing audit alebo inú zakázanú capability. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Cleanup graph — AWS lab

Dependency-aware poradie retention decisions, resource deletions a asynchronous observations potrebné na odstránenie celej lab generation. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Cleanup residue

Resource, attachment, data, policy, subscription alebo recurring charge, ktorý nečakane prežil deklarovaný lab cleanup. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Cost closure — AWS lab

Dôkaz po cleanup-e, že expected retained evidence zostalo, chargeable lab resources boli odstránené a nasledujúce cost data neukazuje neočakávaný residue. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Composite CloudOps lab

Časovo ohraničený experiment pokrývajúci viac SOA-C03 domains, unknown failure diagnosis, bounded recovery, negative validation a full cleanup bez krokového návodu. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Lab replay verdict

Rozhodnutie po evidence review, či lab generation prešla, potrebuje nový variant, musí zopakovať rovnaký failure alebo odhalila prerequisite gap. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## CloudOps incident subject

Exact incident identity zahŕňajúca account/Region/AZ, release/artifact, resource/config generations, business/data correlation, timeline a affected/unaffected cohorts. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Symptom-to-closure lifecycle — CloudOps

Incident model od user/business symptómu cez exact subject, hypotheses, discriminating evidence, containment a authoritative recovery po original/forbidden/adjacent validation a recurrence control. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Impact/scope classification — CloudOps

Počiatočné určenie severity, trendu a affected boundary incidentu pred root-cause diagnosis a remediation priority. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Recent-change correlation — AWS incident

Versionované prepojenie symptómu s deploymentom, policy, route, rotation, failover, patchom, automation alebo capacity transition v relevantnom time windowe. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Volatile AWS evidence

Logs, process/task state, target health, controller events, request IDs alebo configuration snapshots, ktoré môže restart, replacement, rollback alebo retention rýchlo odstrániť. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Causal CloudOps hypothesis

Falsifiable tvrdenie `cause → mechanism → predicted observations`, ktoré vysvetľuje exact incident subject a možno ho odlíšiť od konkurujúcich hypotéz. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Discriminating observation — CloudOps

Observation point, ktorého výsledok podporuje jednu causal hypothesis a zároveň oslabuje alebo vylučuje inú. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Evidence-preserving containment — CloudOps

Dočasná bounded action zastavujúca rast dopadu pri zachovaní forensic, rollback a recovery options. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Authoritative cloud recovery

Obnova cez opravený desired-state/source contract, last-known-good generation alebo clean recovery manifest namiesto manual snowflake mutation. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Causal amplifier — CloudOps incident

Sekundárny configuration alebo automation factor, ktorý nezaložil primary defect, ale zväčšil jeho scope, duration alebo business impact. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Reconvergence validation — CloudOps

Overenie, že controllers, runtime processes, data state a traffic sa po recovery ustálili na authoritative generation a neoscilujú späť. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Adjacent-cohort validation — CloudOps

Overenie recovery na relevantnej susednej AZ, instance, account, tenant, Region alebo release cohort-e mimo pôvodného affected subjectu. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Second-operation verification — CloudOps

Zopakovanie controller alebo business operácie po oprave, napríklad ďalší replacement, retry, deployment, copy alebo refresh, aby sa preukázala stabilita mimo prvého manual testu. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## CloudOps closure verdict

Rozhodnutie, že original outcome, forbidden outcomes, adjacent cohorts, second operation, evidence, earlier controls a residual risk spĺňajú incident acceptance contract. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Earlier operational control

Preventive, detective alebo recovery control odvodený z potvrdeného incident mechanismu a pridaný do build, deployment, policy, telemetry alebo runbook lifecycle-u. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).