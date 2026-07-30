# Disaster recovery

Disaster recovery — DR — je riadené obnovenie kritickej business capability po disruption, pri ktorom pôvodné failure domain, control plane alebo business state nemožno bezpečne ďalej používať. Nie je to existencia druhého Regionu, databázovej repliky ani dokumentu s poradím príkazov. Recovery je dokončená až vtedy, keď alternate generation prevezme presne ohraničenú writer a traffic authority, spracúva nové aj affected historical operations podľa business contractu a nezanecháva split brain, skrytý backlog alebo neuzavretý unknown outcome.

DR nadväzuje na high availability, incident response, backup/restore a RPO/RTO, ale nenahrádza ich. High availability absorbuje bežný component alebo failure-domain výpadok v existujúcom operating modeli. Incident response koordinuje impact a recovery. Backup poskytuje recovery artifacts. DR skladá tieto mechanizmy s identity, network, provider, capacity, communication a business reconciliation do jedného scenario-specific recovery graphu.

## 1. Dominantný scenario-to-business-recovery lifecycle

Recovery plán vzniká z business impactu a konkrétneho disruption scenára. Najprv sa určí capability, consistency group a recovery objectives, potom complete dependency graph, activation authority a alternate target. Samotný failover alebo restore je iba transition; acceptance vyžaduje business read-back, reconciliation a bezpečný steady state alebo failback.

```text
business capability, BIA a disruption scenario
→ exact DR subject, objectives a consistency group
→ strategy, alternate target a recovery graph
→ current release/data/identity/network/provider generations
→ objective activation trigger a decision authority
→ evidence preservation, old-writer fencing a stabilization
→ control-plane, data-plane a dependency recovery
→ business canary a bounded traffic/writer cutover
→ backlog, post-point a external-effect reconciliation
→ degraded/normal service acceptance
→ adopted recovery steady state alebo controlled failback
→ alternate-scenario a second-responder exercise
```

Každá šípka je samostatná failure boundary. Promoted database nemusí mať usable key, active application nemusí mať provider path a green HTTP endpoint nemusí dokazovať final settlement completion. DR claim preto patrí exact end-to-end subjectu, nie najzdravšiemu komponentu.

## 2. Exact DR subject a activation class

Tvrdenie `máme DR v eu-west-1` sa nedá reprodukovať. Exact subject zachováva business capability a critical journeys, disruption scenario, primary a recovery locations, application/data/dependency consistency group, strategy, RPO/RTO a maximum tolerable disruption, release/configuration/data generations, identity/key/network/DNS generations, provider contracts, traffic a writer authority, plan/runbook generation, activation authority, degraded mode a failback contract.

```text
subject: DR-PAY-55-v4
capability: merchant settlement completion
scenario: prod-eu1 network/control-plane unavailable > 10 min
primary: eu-central-1 / prod-eu1
recovery: eu-west-1 / prod-euw1
strategy: warm standby
RPO: 5 min business-consistent
RTO: 45 min safe merchant-facing completion
release: payments 7.26.1
consistency group: PostgreSQL + outbox + broker checkpoint
                   + provider correlation + customer projection
traffic authority: DNS-PAY-18
writer authority: FENCE-PAY-7
```

Activation class sa odlišuje od emocionálneho labelu. Pod replacement alebo strata jednej AZ, ktorú absorbuje local redundancy, patrí HA. Koordinovaný outage v pôvodnom Regione môže zostať incident response. DR sa aktivuje, keď primary environment alebo state nie je v objective time-e bezpečne použiteľný a treba alternate environment, clean recovery alebo zásadnú rekonštrukciu service graphu.

## 3. Business impact a výber recovery stratégie

Strategy sa odvodzuje od business impact analysis, nie od preferovanej cloud služby. BIA určuje financial, contractual, security, legal a data-integrity impact, customer tolerance, maximum disruption a divergence, degraded operations, dependency criticality, staffing/vendor availability a cost/complexity.

Backup-and-restore má nízke steady-state náklady, ale dlhší activation a reconstruction time. Pilot light drží critical data a minimálny control plane, pričom compute a traffic path sa aktivujú počas recovery. Warm standby udržiava zmenšenú service generation a potrebuje scale-up a dependency activation. Active-passive drží pripravený standby, ale writer authority je na jednej strane. Active-active znižuje activation time, no výrazne zvyšuje consistency, routing, conflict a split-brain complexity.

Label stratégie nie je evidence. Warm standby bez current secrets, provider allowlistu, callback route-u, broker checkpointu, on-call pathu a failure-mode capacity je iba čiastočne provisioned environment. Každý tier musí mať explicitný operating a recovery contract.

## 4. Recovery graph a hidden dependencies

DR sa modeluje ako directed dependency graph. Customer path typicky vedie cez DNS/routing, edge/TLS/WAF, workload runtime a service discovery, identity/secrets/KMS, database a durable logs, broker/queues, provider network/credentials/callbacks, observability/audit a nakoniec support, reconciliation a business operations.

Pre každý node a edge sa zachová authority, current generation, recovery mechanismus, dependency order, owner, capacity/quota, validation oracle, forbidden outcome a fallback. Database replica bez functional provider pathu neobnoví settlement capability; provider credential bez callback routing nevytvorí uzavretý business workflow.

Graph musí obsahovať data plane aj control plane. Data plane zahŕňa business records, event/message state, consumer offsets, idempotency a correlation records. Control plane zahŕňa infrastructure definitions, cluster/deployment controllers, DNS/certificates, identity/policies/keys, artifacts/registry, feature flags, observability a recovery approvals. Ak je DR plan, credential alebo artifact dostupný iba v compromised primary account-e, recovery graph je sám závislý od failure domainu, ktorý má prežiť.

## 5. Current replica, clean point a scenario classification

Physical alebo regional failure môže ponechať current replicated state business-valid. Logical corruption, ransomware, malicious writer alebo incompatible schema však môžu current replica urobiť unsafe. Activation preto najprv klasifikuje disruption a až potom vyberá replicated failover, point-in-time clean restore, partial extraction, event replay, compensation alebo rebuild from authority.

Replication znižuje lag, ale faithful kopíruje aj logical delete, invalid configuration a compromised policy effect. Recovery candidate potrebuje clean-point a consistency verdict. Pri external provider operation sa local data porovnáva s idempotency ledgerom; unknown outcome nemožno automaticky replayovať.

```text
regional infrastructure loss
→ current replicated state môže byť validný
→ fence primary → promote standby

logical corruption alebo compromise
→ current replica môže byť unsafe
→ select clean point → isolated restore → merge/reconcile
```

Scenario classification je preto súčasť activation decisionu. Nesprávna stratégia môže vytvoriť väčší incident než pôvodný disruption.

## 6. Writer fencing, epochs a traffic authority

Pred aktiváciou alternate writera musí byť old writer efektívne fenced. Vydaný stop command alebo nefunkčný monitoring nie je dôkaz, že primary nemôže znova prijať writes. Fencing môže používať database promotion generation, lease/epoch token, consensus, network isolation, credential revocation, write endpoint rotation, broker ownership generation a explicitnú traffic/writer authority.

```text
primary partially reachable
+ recovery writer activated bez effective fencing
→ divergent writes
→ ambiguous external effects
→ nebezpečný failback a reconciliation
```

Traffic cutover a writer cutover sú odlišné transitions. DNS môže smerovať browser traffic na recovery Region, kým callbacks, long-lived connections alebo background consumers stále používajú primary. Každá route potrebuje generation a active-path read-back. Bounded ramp sa riadi business completion SLI, nie iba DNS API successom.

## 7. Activation decision pod neistotou

Plan definuje objective triggers, decision authority, required consultations, maximum waiting time, degraded-mode conditions, evidence cutoff, communication cadence, cost/regulatory consequences a abort alebo alternate strategy. Triggerom môže byť primary Region unavailable dlhšie než desať minút, projected RTO breach, confirmed integrity compromise, unsafe primary recovery path alebo provider-declared extended regional impact.

Čakanie na absolútnu istotu spotrebuje RTO. Predčasný cutover bez fencing a consistency verdictu môže vytvoriť split brain. Decision contract preto určuje, ktoré facts musia byť potvrdené, ktoré uncertainty možno akceptovať a kedy sa volí degraded mode namiesto full activation.

Declaration spúšťa roles, change freeze, vendor paths a authoritative recovery state. IC drží business objective; technical recovery owners obnovujú graph nodes; communications oddeľuje confirmed facts od hypotheses; business/data owners rozhodujú o unknown external outcomes a risk acceptance.

## 8. Recovery phases a degraded service

Po declaration sa stabilizuje impact, preserve-nú volatile evidence, zastavia unrelated changes a fenced writers/destructive automation. Recovery environment sa overí cez account/Region access, network, compute, release, keys, secrets, certificates, quotas a control-plane readiness. Data a dependencies sa obnovia alebo promote-nú podľa scenario verdictu, potom sa aktivujú provider egress, credentials, callbacks a broker ownership.

Pred customer trafficom prejde synthetic alebo internal business canary. Traffic sa rampuje po cohorts s entry, success, abort a observation criteria. Work recovery následne drainuje backlog, reconciliuje post-point operations, obnovuje batch/reporting a odstraňuje temporary overrides.

Degraded mode môže prijímať durable intents bez okamžitého provider submissionu, poskytovať read-only history alebo prioritizovať critical tenants. Musí však mať user-visible semantics, durability a queue limits, maximum duration, ownera, exit criteria, capacity model a reconciliation path. Silent `202`, keď systém nevie garantovať bounded completion, nie je degraded mode, ale nepravdivé acknowledgement.

## 9. Connected incident `SRE-PAY-55`

Atlas používal warm standby `prod-euw1`. Catalog deklaroval RPO päť minút, RTO 45 minút, plan `DR-PAY-55-v3` a posledný test 18. marca 2026. Dňa 29. júla o `07:12 UTC` primary Region stratil podstatnú časť network a control-plane connectivity.

Standby database zaostávala iba 32 sekúnd, application release bola current a configured capacity predstavovala 70 % primary. Recovery graph však nebol current: runtime role nemala KMS decrypt grant, provider povoľoval iba eu-central-1 NAT IPs, callback route smerovala na primary, broker checkpoint bol naposledy overený pred 27 minútami, runbook patril broker architecture v3 a health oracle kontroloval `/healthz`, nie provider-confirmed completion.

Database bola promoted o `07:41`; `/healthz` prešiel o `07:53` a DNS weight sa presunul. API začala vracať `202`, ale provider credential nebolo decryptovateľné, egress nebol allowlisted, callback route bola chybná, stale broker checkpoint vytvoril mixed `never-sent` a `sent-unknown` cohort a worker scale prekročil DB pool guardrail.

Regional failure bol trigger. Root cause bol warm-standby design a plan, ktoré nepredstavovali versionovaný end-to-end business recovery graph a neboli rehearsed na current identity, provider, broker, routing a capacity generation. Component readiness a front-door health vytvorili false recovery verdict.

## 10. Evidence-preserving recovery a measured outcome

IC zastavil ďalší unbounded cutover, zmrazil non-DR changes, zachoval DNS/KMS/broker/provider/deployment evidence, zastavil nové provider submissions, bounded prijímal durable intents a fenced primary aj standby consumer ownership. Traffic bol obmedzený na `900 unique intents/s`.

Recovery manifest `REC-PAY-55-1` obnovil KMS grant a decrypt canary, provider recovery IP allowlist, callback routing, authoritative broker checkpoint a epoch fencing. Operations sa rozdelili na `never-sent`, `sent-unknown` a `completed`; consumers sa aktivovali s bounded concurrency a traffic sa rampoval podľa completion SLI a DB/provider saturation.

Safe merchant-facing recovery nastala o `09:31 UTC`, teda `2 h 19 min` po disruption. RTO 45 minút zlyhalo. Permanentná strata acknowledged intents bola nula, ale `318` operations vyžadovalo provider-ledger reconciliation. Recovery Region zostal dočasným primary, kým sa pripravil controlled failback.

## 11. Failback ako nová risky transition

Failback nie je automatický návrat po obnove primary Regionu. Vyžaduje current authoritative writer identity, reverse replication alebo merge, post-point/conflict manifest, obnovené primary dependencies a capacity, bounded traffic ramp, abort criteria, retirement old active generation a nové RPO/RTO measurement.

Často je bezpečnejšie ponechať recovery Region ako temporary primary a vykonať rebalancing neskôr. Failback počas neuzavretého incidentu môže zopakovať route, key alebo checkpoint failure. Acceptance preto testuje aj fallback/failback, nie iba one-way activation.

## 12. DR exercises a evidence scope

Tabletop overuje decisions, roles a assumptions. Component test overuje restore, key, DNS alebo dependency. Parallel recovery aktivuje alternate environment bez customer trafficu. Partial-traffic exercise používa bounded cohort. Full regional exercise pokrýva service graph, traffic, data, provider path, business validation a work recovery.

Plan bez current-generation exercise-u je hypothesis. Exercise meria declaration, fencing, access/environment activation, recovered point, technical service, business validation, reconciliation, actual RPO/RTO, manual steps a second-responder reproducibility. Evidence sa nesmie použiť na širší claim než testovaný subject: Pod replacement nepreukazuje regional DR.

## 13. DR acceptance contract

Positive path preukáže, že current alternate generation je accessible, correctly configured, capacity-ready a business-complete. Regional-failure path musí fence primary, obnoviť current replicated state, aktivovať provider/broker/DNS paths a splniť objectives. Corruption path musí odmietnuť current bad replica a použiť clean restore/reconciliation. Degraded path musí pravdivo obmedziť capability. Failback path musí zachovať single-writer authority a post-point state.

Forbidden paths musia zlyhať: wrong Region, stale key alebo runbook, provider path bez allowlistu, broker checkpoint bez authority, health-only cutover, traffic pred fencing, RTO zastavené pri DNS API a failback bez divergence manifestu.

```text
positive:
current recovery graph → canary → bounded traffic → business completion

failure:
primary Region loss → fence → activate → reconcile within objectives

corruption:
unsafe replica denied → clean point → side-by-side recovery

forbidden:
split brain
HTTP green without completion
unknown provider outcome replay
stale generation accepted
unbounded failback
```

Verdict patrí exact scenario, plan, release, identity, dependency a exercise generation. Alternate responder a second disruption overujú, že recovery nie je jednorazový heroický výkon.

## 14. Troubleshooting DR activation

Pri zlyhaní activation sleduj exact capability/scenario/plan, declaration authority, writer fencing, recovery account/Region access, release/control plane, identity/key/certificates, network/DNS/provider paths, data clean point alebo checkpoint, capacity/quotas, business oracle, traffic ramp, reconciliation a actual objective time.

```text
DR activation alebo exercise zlyháva
→ subject/scenario/generation
→ declaration a fencing
→ control-plane access
→ identity/key/network/provider
→ data/checkpoint/consistency group
→ capacity a dependency readiness
→ business canary
→ traffic/reconciliation
→ RPO/RTO a failback closure
```

Database promoted alebo DNS changed sú intermediate observations. Diagnostika končí až business capability a writer authority verdictom.

## 15. Anti-patterny

DR anti-patterny zamieňajú existenciu komponentu alebo minulého testu za current end-to-end recoverability.

- **Druhý Region existuje —** nemusí obsahovať current accessible release, identity, provider a capacity generation.
- **Database replica je DR —** ignoruje control plane, broker, network, provider, callbacks a reconciliation.
- **Healthcheck je green —** process/front door môže fungovať bez final business outcome-u.
- **Failover bez fencing —** vytvára split brain a divergentné external effects.
- **DR test bez trafficu alebo provider pathu —** neoveruje reálnu capability ani work recovery.
- **Runbook bol testovaný minulý rok —** architecture, credentials, contacts, quotas a dependencies sa zmenili.
- **RTO končí pri DNS cutover-e —** ignoruje route propagation, completion, backlog a reconciliation.
- **Failback hneď po návrate primary —** pridáva risky transition pred stabilizáciou a divergence closure.

## 16. Kontrolné otázky

1. Ako sa HA, incident response, backup a DR líšia?
2. Čo tvorí exact DR subject a consistency group?
3. Ako BIA určuje recovery strategy?
4. Prečo warm standby label nie je acceptance evidence?
5. Ako recovery graph odhaľuje hidden dependencies?
6. Kedy použiť current replica a kedy clean point?
7. Prečo traffic a writer fencing sú oddelené?
8. Čo musí obsahovať activation decision contract?
9. Ako sa degraded mode navrhne pravdivo a bounded?
10. Prečo `SRE-PAY-55` vrátilo `202`, ale nie settlement capability?
11. Prečo failback potrebuje samostatný plan a verdict?
12. Ktoré positive, failure, corruption a forbidden paths patria do acceptance?

## Glossary impact

Relevantné pojmy: disaster-recovery subject, activation class, recovery strategy, recovery graph, recovery environment generation, current-vs-clean recovery state, writer fencing, traffic authority, DR activation contract, degraded recovery mode, work recovery, failback generation, DR exercise evidence scope a DR acceptance contract.

## Primárne zdroje

- [NIST SP 800-34 Rev. 1 — Contingency Planning Guide](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final)
- [NIST CSRC — Contingency plan](https://csrc.nist.gov/glossary/term/contingency_plan)
- [Google SRE — Emergency Response](https://sre.google/sre-book/emergency-response/)
- [Google SRE — Data Integrity](https://sre.google/sre-book/data-integrity/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: RPO a RTO](rpo-and-rto.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Chaos engineering →](chaos-engineering.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
