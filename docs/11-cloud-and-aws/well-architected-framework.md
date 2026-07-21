# Well-Architected Framework

AWS Well-Architected Framework poskytuje konzistentný spôsob hodnotenia workloadu voči cloudovým best practices. Nie je to certifikát, jednorazový audit ani checklist garantujúci bezpečnosť. Je to opakovateľný review a improvement proces, ktorý prepája business požiadavky, architektúrne rozhodnutia, operational evidence, riziká a konkrétne nápravné kroky.

## 1. Mentálny model

```text
business outcome a constraints
→ workload boundary
→ architecture a operational evidence
→ pillar questions a best practices
→ risks a trade-offs
→ prioritized improvement plan
→ implementation
→ validation
→ milestone
→ ďalší review
```

Dôležitá otázka nie je „Používame AWS službu X?“, ale „Spĺňa workload požadované reliability, security, performance, operations, cost a sustainability outcomes a vieme to preukázať?“

## 2. Workload boundary

Workload je súbor komponentov, ľudí, procesov a technológií, ktoré spoločne poskytujú business value.

Boundary má zahŕňať:

- používateľov a business ownera,
- application a data components,
- AWS accounts a Regions,
- external dependencies,
- identity a security boundaries,
- CI/CD a operational tooling,
- backup a recovery,
- observability,
- support a on-call model,
- compliance a cost ownership.

Ak sa review obmedzí iba na diagram AWS resources, ignoruje významnú časť reálneho workloadu.

## 3. Šesť pilierov

AWS Well-Architected Framework používa šesť pilierov:

1. Operational Excellence
2. Security
3. Reliability
4. Performance Efficiency
5. Cost Optimization
6. Sustainability

Piliere sa navzájom ovplyvňujú. Zmena zameraná na jeden môže zlepšiť alebo zhoršiť iný.

## 4. Operational Excellence

Operational Excellence je schopnosť efektívne podporovať development a prevádzku, získavať insight do systému a priebežne zlepšovať procesy a postupy.

Témy:

- organizácia tímov a ownership,
- operations as code,
- malé reverzibilné zmeny,
- observability,
- incident response,
- runbooks a playbooks,
- operational readiness,
- learning from failures,
- continuous improvement.

Dôkazy:

- definovaní owners,
- deployment a rollback proces,
- telemetry a alarms,
- on-call a escalation,
- postmortems,
- change metrics,
- testované runbooks.

## 5. Security

Security chráni dáta, systémy a assets pri zachovaní business schopnosti.

Témy:

- identity foundation,
- traceability,
- infrastructure protection,
- data protection,
- threat detection,
- vulnerability management,
- incident response,
- application security.

Dôkazy:

- federated access a MFA,
- least privilege,
- CloudTrail a security logs,
- encryption a key governance,
- network segmentation,
- patching,
- security findings a response,
- tested containment.

Security sa nemá „vymeniť“ za nižší cost alebo rýchlejší release bez explicitného risk acceptance procesu.

## 6. Reliability

Reliability je schopnosť workloadu vykonávať požadovanú funkciu správne a konzistentne v očakávanom čase.

Témy:

- foundations a quotas,
- workload architecture,
- change management,
- failure management,
- backup a recovery,
- capacity a scaling,
- dependency isolation.

Dôkazy:

- SLO a capacity model,
- Multi-AZ/Region decisions,
- health checks,
- retry/timeout/circuit-breaker policy,
- tested failover,
- restore tests,
- quota monitoring,
- dependency failure drills.

Redundancy bez testovaného failoveru nie je preukázaná reliability.

## 7. Performance Efficiency

Performance Efficiency je efektívne používanie compute resources na splnenie system requirements a udržanie efektivity pri zmene demandu a technológií.

Témy:

- správny resource type,
- compute/storage/database/network selection,
- serverless a managed services,
- measurement,
- scaling,
- performance trade-offs,
- review nových capabilities.

Dôkazy:

- load tests,
- latency/throughput/error metriky,
- saturation,
- rightsizing,
- architecture benchmark,
- performance budget,
- capacity forecast.

Najdrahší resource nemusí byť najvýkonnejší pre konkrétny workload pattern.

## 8. Cost Optimization

Cost Optimization je schopnosť poskytovať business value pri najnižšom rozumnom total cost počas lifecycle-u.

Témy:

- financial management,
- expenditure awareness,
- cost-effective resources,
- supply-demand management,
- optimization over time.

Dôkazy:

- cost allocation,
- budgets a anomaly detection,
- unit economics,
- utilization,
- commitment coverage/utilization,
- lifecycle a deletion controls,
- optimization backlog.

Najnižší mesačný účet nie je cieľ, ak zvyšuje outage risk, toil alebo time-to-market viac než ušetrená suma.

## 9. Sustainability

Sustainability sa zameriava na minimalizovanie environmentálneho dopadu cloud workloads.

Témy:

- Region a service selection,
- utilization,
- demand matching,
- data lifecycle,
- software efficiency,
- hardware a accelerator selection,
- process a culture.

Praktické opatrenia sa často prekrývajú s cost a performance optimalizáciou:

- odstránenie idle resources,
- autoscaling,
- efektívnejší code,
- managed services,
- data retention podľa potreby,
- novšie efektívnejšie instance families.

Sustainability však nie je iba synonymum pre cost reduction.

## 10. Trade-offs medzi piliermi

Príklady:

- viac redundantnej capacity zvyšuje reliability, ale aj cost,
- dlhšia retention zlepšuje recovery/compliance, ale zvyšuje storage cost a data exposure,
- aggressive caching znižuje latency a origin cost, ale môže zhoršiť consistency,
- centralizácia znižuje duplication, ale môže zväčšiť shared blast radius,
- strict security control môže znížiť usability, ale odstránenie kontroly môže vytvoriť kritické riziko.

Review má trade-off explicitne zaznamenať vrátane ownera a akceptácie rizika.

## 11. AWS Well-Architected Tool

AWS Well-Architected Tool pomáha:

- definovať workload,
- aplikovať Framework Lens a ďalšie lenses,
- odpovedať na review questions,
- identifikovať high-risk a medium-risk issues,
- vytvoriť improvement plan,
- ukladať milestones,
- generovať reports,
- zdieľať workload review podľa access modelu.

Tool nenahrádza technické overenie. Odpoveď bez evidence môže vytvoriť falošne pozitívny výsledok.

## 12. Lenses

Lens je sada questions, best practices a improvement guidance pre konkrétny domain alebo technology scope.

Typy:

- AWS Well-Architected Framework Lens,
- AWS-provided domain lenses,
- custom lenses podľa organization requirements.

Lens môže pokrývať napríklad serverless, SaaS, machine learning, financial services alebo organization-specific controls podľa aktuálnej ponuky.

Custom lens nemá kopírovať všetky interné policies bez prioritizácie. Má spájať konkrétne questions s evidence a remediation.

## 13. Review participants

Kvalitný review potrebuje viac perspektív:

- business owner,
- solution/application architect,
- development,
- platform/cloud operations,
- security,
- SRE/on-call,
- data owner,
- finance/FinOps,
- compliance podľa potreby.

Review vykonaný iba jedným administrátorom môže prehliadnuť business, application alebo operational dependencies.

## 14. Evidence-driven review

Ku každej významnej odpovedi zachovaj dôkaz:

- architecture diagrams,
- IaC alebo configuration,
- CloudWatch/observability dashboards,
- CloudTrail/audit evidence,
- policy definitions,
- deployment history,
- restore/failover test,
- incident/postmortem,
- cost report,
- capacity/load test,
- ownership a runbooks.

Evidence musí mať timestamp a scope. Starý diagram nie je dôkaz aktuálneho production stavu.

## 15. High-risk a medium-risk issues

Risk issue reprezentuje odchýlku od best practices s relevantným dopadom.

Pri triage zaznamenaj:

- pillar a question,
- affected workload/component,
- failure scenario,
- likelihood,
- impact,
- existing controls,
- ownera,
- remediation,
- target date,
- validation,
- accepted residual risk.

Počet high-risk issues nie je vhodný ako vanity metric bez kontextu. Dôležitá je ich závažnosť, vek a reálne odstránenie.

## 16. Improvement plan

Improvement plan má premeniť review na vykonateľný backlog.

Každá položka potrebuje:

- konkrétny problem statement,
- business/technical impact,
- ownera,
- priority,
- dependencies,
- estimated effort/cost,
- target state,
- validation criteria,
- rollback alebo safe-change model.

Vágne položky typu „zlepšiť monitoring“ nie sú dostatočné. Lepšie:

> Definovať SLO pre checkout, pridať latency/error-rate dashboard, burn-rate alarmy a on-call runbook; overiť fault injection testom.

## 17. Prioritizácia

Použi kombináciu:

- business criticality,
- security/compliance severity,
- outage/recovery impact,
- likelihood,
- blast radius,
- effort,
- reversibility,
- dependency order,
- quick wins oproti structural changes.

High-risk issue nemusí byť vždy prvý, ak jeho oprava závisí od identity, networking alebo ownership foundation.

## 18. Milestones

Milestone zachytáva stav workloadu v určitom čase.

Vytvor milestone:

- po baseline review,
- pred production launchom,
- po významnej architecture change,
- po odstránení improvement items,
- po major incident alebo DR test,
- pred/po migration.

Milestone umožňuje merať zmenu rizika a rozhodnutí. Nemá byť iba administratívny snapshot bez porovnania.

## 19. Review cadence

Review vykonávaj:

- pri návrhu nového workloadu,
- pred go-live,
- periodicky podľa criticality,
- po veľkej zmene,
- po incidente,
- pri novom compliance alebo business requirement,
- pri významnom raste cost/demandu.

Annual review môže byť príliš zriedkavý pre rýchlo sa meniaci workload. Časť controls je vhodné automaticky priebežne overovať.

## 20. Continuous Well-Architected

Framework možno integrovať do delivery lifecycle-u:

```text
architecture decision
→ IaC/policy validation
→ deployment checks
→ observability a SLO
→ cost/security findings
→ periodic review
→ improvement backlog
```

Automatizovať možno napríklad:

- configuration compliance,
- backup coverage,
- encryption,
- public exposure,
- cost anomalies,
- SLO health,
- stale resources.

Nie všetky questions sa dajú spoľahlivo vyriešiť automatickým scannerom. Ownership, business trade-offs a recovery readiness potrebujú ľudské posúdenie.

## 21. Architecture Decision Records

ADR zachytáva:

- context,
- decision,
- alternatives,
- consequences,
- trade-offs,
- review date.

Well-Architected review identifikuje risk; ADR vysvetľuje, prečo bol konkrétny trade-off prijatý. Accepted risk bez ADR alebo ownera sa ľahko stane neviditeľným permanentným dlhom.

## 22. Operational readiness review

Pred go-live over:

- ownership a support hours,
- SLO a alarms,
- dashboards a logs,
- deployment/rollback,
- capacity a quotas,
- backups a restore,
- security controls,
- dependencies,
- on-call/runbooks,
- cost guardrails,
- failure drills.

Well-Architected review je širší než production checklist, ale operational readiness z neho môže priamo čerpať.

## 23. Review workloadu s managed services

Managed service posúva responsibility boundary, ale neodstraňuje customer decisions.

Stále treba posúdiť:

- configuration,
- identity,
- encryption,
- network exposure,
- capacity/quotas,
- backup/restore,
- version lifecycle,
- observability,
- cost,
- service limits a regional availability.

„AWS to spravuje“ nie je odpoveď na customer-owned configuration risk.

## 24. Review serverless a container workloads

### Serverless

- concurrency a downstream protection,
- retries/idempotency,
- event age a DLQ,
- cold start/performance,
- cost per invocation,
- IAM per function,
- observability.

### Containers

- image supply chain,
- orchestration/control-plane responsibility,
- capacity a autoscaling,
- service discovery/networking,
- secrets,
- deployment/rollback,
- node/runtime lifecycle,
- cluster cost allocation.

## 25. Multi-account a multi-Region review

Over:

- account/OU boundaries,
- SCPs a delegated administration,
- centralized logging/security,
- cross-account access,
- network topology,
- Region guardrails,
- data residency,
- backup/recovery accounts,
- failover ownership,
- cost allocation.

Viac accounts alebo Regions automaticky nezaručuje isolation ani recovery.

## 26. Cost a Well-Architected

Cost pillar sa má hodnotiť spolu s:

- reliability cost of failure,
- security/compliance controls,
- operational toil,
- engineering time,
- licensing,
- data transfer,
- commitments,
- sustainability/utilization.

Odporúčanie „vypnúť redundancy“ môže byť finančne nesprávne, ak zvýši očakávaný outage loss.

## 27. SOA-C03 mapovanie

- **Domain 1** — operational insight, metrics/logs, remediation a performance reviews,
- **Domain 2** — reliability, backup, failure management a business continuity,
- **Domain 3** — operations as code, repeatable deployment, change a automation,
- **Domain 4** — security controls, evidence, compliance a incident readiness,
- **Domain 5** — networking, DNS, connectivity, edge a failure isolation.

SOA-C03 kandidát má vedieť vybrať riešenie nielen podľa service feature, ale aj podľa operational, reliability, security a cost trade-offov.

## 28. Troubleshooting review procesu

### Odpovede bez evidence

Požiadaj o live configuration, metric, test alebo policy. Neakceptuj iba predpoklad.

### Review nevytvoril zmenu

Over ownerov, priority, budget a integration do delivery backlogu.

### Stále rovnaké high-risk issues

Over structural dependency, risk acceptance, leadership ownership a reálnu validation opráv.

### Review scope je príliš malý

Doplň external dependencies, people/process, CI/CD, data, identity a recovery.

### Tool ukazuje starý stav

Vytvor nový review/milestone a porovnaj s aktuálnou architektúrou.

## 29. Anti-patterny

### Checklist compliance

Zaškrtáva odpovede bez dôkazu a bez pochopenia risku.

### Review iba pred auditom

Nevstupuje do engineering lifecycle-u.

### Všetko označené „not applicable“

Maskuje chýbajúce ownership alebo nedostatočný scope.

### Tool ako scanner

AWS WA Tool neobjaví všetky configuration problems automaticky.

### Improvement plan bez ownerov

Riziká ostanú otvorené.

### Optimalizácia jedného piliera izolovane

Môže poškodiť iný pillar alebo business outcome.

### Accepted risk bez expirácie

Dočasná výnimka sa zmení na permanentný neviditeľný stav.

## 30. Praktický review template

```text
Workload:
Business owner:
Technical owner:
Criticality:
Users a outcome:
Accounts/Regions:
Data classification:
SLO/RTO/RPO:
Top dependencies:
Top failure modes:

Pillar finding:
Evidence:
Risk:
Impact:
Likelihood:
Existing controls:
Decision:
Owner:
Target date:
Validation:
Residual risk:
Milestone:
```

## 31. Kontrolné otázky

1. Čo je workload boundary?
2. Ktorých šesť pilierov Framework používa?
3. Prečo review musí byť evidence-driven?
4. Aký je rozdiel medzi findingom, improvement itemom a accepted riskom?
5. Na čo slúži milestone?
6. Ako sa používajú lenses?
7. Prečo Well-Architected Tool nie je automatický scanner?
8. Ako sa review integruje do delivery lifecycle-u?
9. Ako sa prioritizujú high-risk issues?
10. Prečo sa piliere nemajú optimalizovať izolovane?

## Glossary impact

Relevantné pojmy: AWS Well-Architected Framework, workload boundary, Operational Excellence pillar, Security pillar, Reliability pillar, Performance Efficiency pillar, Cost Optimization pillar, Sustainability pillar, AWS Well-Architected Tool, lens, custom lens, high-risk issue, improvement plan, milestone, evidence-driven review, continuous Well-Architected, architecture decision record a operational readiness review.

## Oficiálna dokumentácia

- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
- [AWS Well-Architected Tool](https://docs.aws.amazon.com/wellarchitected/latest/userguide/intro.html)
- [The pillars of the framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/the-pillars-of-the-framework.html)
- [Using lenses](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses.html)
- [Milestones](https://docs.aws.amazon.com/wellarchitected/latest/userguide/milestones.html)
- [Implement and track improvements](https://docs.aws.amazon.com/wellarchitected/latest/userguide/implement-and-track-improvements.html)
