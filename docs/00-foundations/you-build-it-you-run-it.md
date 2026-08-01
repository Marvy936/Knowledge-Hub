# You Build It, You Run It

Princíp `you build it, you run it` spája design a implementation decisions s reálnymi prevádzkovými dôsledkami. Tím, ktorý rozhoduje o architektúre, dependencies, telemetry a rollout-e, má zostať zapojený aj do reliability, supportu a recovery. Tým sa skracuje feedback medzi technickou voľbou a jej dopadom.

Princíp však neznamená, že každý developer musí samostatne spravovať hardware, Kubernetes control plane alebo 24/7 pager. Platform, security, network a database tímy môžu vlastniť shared capabilities, pokiaľ sú ich boundaries a service contracts explicitné. Application tím stále vlastní business behavior, operability svojho workloadu a rozhodnutie, ako reagovať na failure dependency.

Dobrý model oddeľuje vrstvy:

```text
platform owner → bezpečná a podporovaná runtime capability
service owner → application, configuration a business outcome
shared incident command → koordinácia naprieč hranicami
```

Ak sa prevádzka odovzdá bez kontextu, vzniká ticket queue a pomalý learning. Ak sa všetka infraštruktúrna komplexita prenesie na každý product tím, vzniká duplicita a nekonzistentná bezpečnosť. Cieľom je lifecycle accountability s rozumnými platform boundaries, nie zrušenie špecializácie.

## 1. Definícia

You build it, you run it je operating princíp, podľa ktorého tím tvoriaci service nesie významnú zodpovednosť aj za jej production behavior, reliability a lifecycle. Tím preto pri design-e zohľadňuje deployment, telemetry, failure, recovery, capacity a dependency changes.

Princíp neodstraňuje platform, security, database ani SRE špecialistov. Mení interface: product tím nemôže úplne odovzdať consequences svojich application decisions a špecializovaný tím nemá byť permanentný vlastník cudzej business logiky.

## 2. Problém tradičného handoff modelu

V oddelenom modeli development dokončí application a operations ju prevezme. Produkčný feedback sa vracia cez incident ticket po strate contextu a operability sa často dopĺňa až pred release-om.

```text
development vytvorí zmenu
→ operations ju nasadí
→ support alebo operations prijme incident
→ diagnosis sa presúva cez tímy
→ development dostane oneskorený symptom
```

Model vytvára viac systémových problémov:

- **Late operability — telemetry a recovery po implementation**: service môže prejsť functional tests a stále byť nediagnostikovateľná v produkcii.
- **Decision-cost separation — autor nevidí runtime consequences**: architecture alebo dependency risk sa opakuje, pretože feedback rieši iná skupina.
- **Operations bottleneck — centralizované deploymenty a incidents**: jedna queue obmedzuje release aj recovery všetkých services.
- **Context loss — symptom sa prekladá cez tickety**: timestamps, change identity a hypotheses sa strácajú pri každom handoffe.
- **Conflicting incentives — feature throughput proti stability**: development dokončuje scope a operations znižuje risk blokovaním zmien.

## 3. Mentálny model uzavretého lifecycle-u

Princíp prepája celý service loop. Production nie je posledné oddelenie, ale autoritatívny zdroj evidence pre ďalší design a backlog.

```text
design
→ build a test
→ release a rollout
→ operate a observe
→ incident alebo user feedback
→ code, architecture alebo platform improvement
```

Tím nemusí vykonať každú underlying operáciu. Musí však zostať zodpovedný za to, že user outcome má ownera, evidence a recovery path cez všetky dependencies.

## 4. Čo znamená „build it“

„Build it“ presahuje písanie application code-u. Zahŕňa vytvorenie service contractu, testability, artifact identity, deployment configuration a runtime signals potrebných na bezpečnú zmenu.

Tím pri build lifecycle vlastní:

- **Functional behavior — business a API contract**: definuje success, failure a compatibility pre users a consumers.
- **Non-functional requirements — reliability, security a performance boundaries**: ovplyvňujú architecture a acceptance criteria ešte pred release-om.
- **Tests a release evidence — čo sa overuje pred exposure**: tím pozná coverage aj remaining uncertainty.
- **Instrumentation — signal o user a system outcome-e**: logs, metrics a traces vznikajú spolu s code-om, nie až po incidente.
- **Deployment semantics — configuration, migration a rollout**: service vie, ako sa bezpečne dostať z jednej verzie do druhej.

## 5. Čo znamená „run it“

„Run it“ nie je synonymom držania pagera. Zahŕňa všetky capabilities potrebné na udržanie služby, reakciu na zlyhanie a spätné zabudovanie learningu.

- **SLI a SLO — definícia user-oriented reliability**: tím vie, čo znamená úspešná valid operation a akú úroveň služby chce udržiavať.
- **Observability — evidence pre known aj unknown questions**: instrumentation a access umožnia prepojiť symptom s version, request a dependency.
- **Actionable alerting — správny page pri relevantnom impacte**: alert má ownera, context, runbook a bezpečnú response path.
- **On-call a incident participation — dostupná decision authority**: tím dokáže viesť alebo podporiť mitigation podľa service a platform boundary.
- **Rollback, roll-forward a degradation — recovery z chybnej zmeny**: strategy rešpektuje data compatibility a critical user outcome.
- **Capacity a cost management — dostatok resources a headroomu**: service pozná scaling signal, quotas a failover requirements.
- **Dependency lifecycle — upgrade, deprecation a failure contract**: external a shared services sa sledujú počas celého support windowu.
- **Backup a restore requirements — ochrana authoritative state-u**: owner definuje RPO/RTO a application validation, aj keď platforma vykonáva backup.
- **Post-incident improvement — odstránenie opakovania**: incident mení tests, guardrails, architecture alebo ownership, nie iba aktuálny runtime state.

## 6. Operating contract a explicitný scope

Slogan bez responsibility boundary vytvára chaos. Každá organization musí rozhodnúť, ktoré runtime activities vedie product tím, ktoré platform alebo SRE a kde je shared escalation.

Operating contract má definovať:

- **Primary owner — kto vedie user/service incident**: jedna skupina koordinuje outcome a communication.
- **Platform dependencies — kto obnovuje shared capability**: cluster, network, identity alebo telemetry majú samostatného ownera a SLO.
- **Access a authority — kto môže rollbacknúť, meniť traffic alebo aktivovať failover**: incident nesmie čakať na nejasný approval.
- **Support hours a on-call model — kedy je service krytá**: criticality a geography určujú response expectations.
- **Escalation path — kedy a ako vstúpi expert**: bounded expertise sa nerozširuje nebezpečným zásahom mimo kompetencie.
- **Follow-up ownership — kto financuje permanent fix**: incident action sa nestratí medzi platform a product backlogom.

## 7. Nie je to „každý robí všetko“

Moderná platforma obsahuje domény vyžadujúce hlbokú expertízu a organization-wide consistency. Od každého product tímu nemožno očakávať návrh cloud network backbone-u, database engine recovery alebo organization IAM governance.

Rozdelenie má zachovať service feedback:

- **Platform engineering — vlastní reusable platform product**: cluster, pipeline, secret alebo observability capability má API, SLO, support a roadmap.
- **Cloud infrastructure — vlastní shared account a network foundations**: product tím používa supported primitives a definuje workload requirements.
- **Security — vlastní organization controls a expert risk support**: application tím vlastní threats a secure use vlastnej business logiky.
- **Database engineering — vlastní data platform mechanics**: service tím vlastní schema, query behavior, data classification a application consistency.
- **SRE — poskytuje reliability methods alebo shared operations model**: service tím zostáva zapojený do incidents a permanent fixes.

## 8. Shared responsibility medzi service a platform tímom

Responsibility treba deliť podľa mechanismu a semantics, nie podľa neurčitého názvu technológie.

| Oblasť | Service tím | Platform alebo SRE tím | Interface |
|---|---|---|---|
| Business logic | definuje a vlastní behavior | neposkytuje business semantics | API a user outcome |
| Service SLO | vlastní target a error semantics | poskytuje framework a coaching | SLI schema, reporting a review |
| Application alerts | vlastní actionability a runbook | poskytuje alerting platformu | labels, routing a escalation |
| Deployment | konfiguruje strategy a validation | poskytuje controller a safe defaults | rollout API a supported patterns |
| Cluster control plane | používa supported capabilities | vlastní availability, upgrade a policy | platform SLO a incident path |
| Application incident | vedie impact a mitigation | podporuje pri shared dependency | joint evidence a escalation |
| Platform incident | validuje service impact a workaround | vedie platform recovery | status, client behavior a recovery |

## 9. Observability prerequisite

Tím nemôže prevádzkovať service, ktorú nevidí. Potrebuje prístup k signals a schopnosť korelovať user outcome, version, request a dependency path.

Observability prerequisite zahŕňa:

- **Stable service a version identity — priradenie signalov ku konkrétnemu release-u**: bez nej canary a incident diagnosis miešajú viac runtime verzií.
- **User-oriented metrics — business a SLI outcome**: CPU a Pod count nepreukazujú úspešný checkout alebo processing.
- **Structured logs — decision a error context**: event name, error type a correlation ID znižujú manual reconstruction.
- **Distributed traces — causal dependency path**: ukazujú latency, retries a broken propagation pre sampled operations.
- **Deployment events — change correlation**: recent rollout, config a feature flag zmeny vstupujú do incident hypothesis.
- **Access a retention — dostupnosť evidence počas incidentu**: team nepotrebuje čakať na export od iného ownera a data nezmiznú pred review.

## 10. Safe delivery prerequisite

Ak každá zmena vyžaduje rizikový big-bang deployment, priame ownership môže viesť k strachu z release-u alebo častým incidentom. Tím potrebuje automatizovaný a testovaný spôsob meniť runtime s obmedzeným blast radiusom.

Safe delivery poskytuje:

- **Immutable artifact identity — presný release a rollback target**: rovnaký digest sa promuje a koreluje s telemetry.
- **Progressive rollout — malý počiatočný exposure**: canary alebo cohort umožní zastaviť chybnú zmenu pred plným impactom.
- **Readiness a smoke validation — odlíšenie created od functioning**: runtime status sa doplní relevantným service outcome testom.
- **Data-compatible migration — zachovanie rollback alebo roll-forward pathu**: schema a application versions môžu bezpečne koexistovať počas transition.
- **Abort a rollback authority — rýchle rozhodnutie pri regresii**: team nemusí čakať na central approval pri known unsafe signal-e.

## 11. Runbooks a known failure paths

Runbook znižuje decision latency pri known incident class. Nemá byť zoznam príkazov bez vysvetlenia; prepája symptom, hypotheses, evidence, safety checks, mitigation a validation.

Kvalitný runbook uvádza, čo alert znamená a čo neznamená, ktoré dependencies overiť, aký zásah má blast radius a ako potvrdiť recovery. Game day alebo incident musí overiť jeho použiteľnosť a aktualizovať nepresné kroky.

## 12. Access a break-glass

Owner potrebuje least-privilege access na evidence a bounded remediation. Príliš slabé oprávnenie blokuje recovery, príliš broad permanent admin zvyšuje compromise a accidental-change risk.

Bežná cesta používa krátkodobé federované sessions a audited roles. Break-glass path rieši IdP alebo control-plane outage, má oddelené credentials, phishing-resistant MFA, alert pri použití a post-use rotation.

Access sa testuje pred incidentom. Runbook s commandmi, ktoré on-call role nemôže vykonať, nie je funkčný recovery mechanismus.

## 13. Capacity a roadmap prerequisite

On-call, upgrades, vulnerabilities, capacity a recovery tests spotrebúvajú reálnu engineering kapacitu. Ak product plan zahŕňa iba features, „run it“ sa stane neviditeľnou druhou prácou vykonávanou v noci alebo počas incidentov.

Reliability backlog sa prioritizuje podľa SLO, toil, incident a risk evidence. Tím potrebuje authority zastaviť nebezpečný rollout alebo investovať do recurring problemu, inak nesie accountability bez schopnosti meniť systém.

## 14. On-call

On-call je mechanizmus dostupnosti trained respondera pre definovaný čas a scope. Jeho cieľom je obnoviť critical outcome a koordinovať incident, nie držať človeka permanentne pripraveného na neakčné infra warnings.

Zdravý on-call model potrebuje:

- **Actionable pages — user impact alebo bezprostredný critical risk**: notification má konkrétnu response a neslúži ako všeobecný monitoring feed.
- **Primeranú rotáciu — udržateľné rozdelenie záťaže**: počet ľudí, timezone a service stability ovplyvňujú fatigue a coverage.
- **Documented escalation — vstup ďalšej expertízy**: responder vie, kedy aktivovať platform, security, database alebo vendor support.
- **Access a tools — schopnosť vidieť a ovplyvniť state**: pager bez oprávnení iba presúva incident k ďalšiemu tímu.
- **Compensation a recovery time — ochrana ľudskej kapacity**: nočný zásah má organizačný cost a nesmie sa ignorovať.
- **Toil a page review — odstránenie opakovaných zásahov**: recurring page vytvára engineering action alebo sa zmení alert semantics.
- **Load limit — hranica neprijateľnej záťaže**: prekročenie spúšťa reliability prioritu, nie iba rozšírenie rotácie.

## 15. Alert ownership

Alert má smerovať k actorovi, ktorý rozumie signal-u, má authority vykonať mitigation a vlastní permanent follow-up. Routing podľa repository alebo infra componentu môže byť nesprávny, ak user outcome a action vlastní iná skupina.

Alert `CPU high` bez saturation a impactu prenáša diagnosis toil. Lepší page môže hovoriť, že checkout latency rýchlo spaľuje error budget, uviesť affected version, recent deployment a link na dependency dashboard.

Owner alertu musí pravidelne overovať:

- **Signal semantics — čo numerator, denominator a scope merajú**;
- **Actionability — aký zásah môže responder bezpečne vykonať**;
- **Routing — či receiver má správne access a duty coverage**;
- **Runbook — či diagnosis a recovery stále zodpovedajú runtime-u**;
- **Noise — či grouping, threshold a no-data behavior zachovávajú dôveru**.

## 16. Operational readiness

Operational readiness review overuje, či je service pripravená nielen na prvý deployment, ale aj na degradáciu, upgrade a incident. Review má byť risk-based a používať evidence, nie mechanický checklist rovnaký pre každý workload.

Kritické capabilities majú vysvetlený účel:

- **Owner a escalation — zodpovednosť za outcome**: incident a lifecycle decision majú konkrétnu skupinu.
- **Health a readiness — bezpečný routing a rollout**: probes reprezentujú schopnosť prijímať traffic, nie iba process existence.
- **SLI, dashboards a alerts — runtime evidence a response**: user outcome, capacity a dependencies sú viditeľné a akčné.
- **Rollback, mitigation a degradation — recovery z chybnej zmeny**: tím pozná data compatibility a critical functionality.
- **Runbooks — known failure diagnosis**: response nie je závislá od pamäte jedného autora.
- **Capacity a quotas — headroom pre peak a failover**: scaling policy má reálny signal a provisioning boundary.
- **Backup a restore — ochrana state-u**: RPO/RTO a application validation sú testované.
- **Dependency map — shared failure a support paths**: owner vie, čo služba potrebuje na úplný user journey.
- **Security a lifecycle — trust, patch a deprecation**: credentials, vulnerabilities a end-of-support majú ownera a process.

## 17. SRE interaction models

SRE môže pomáhať product tímu rôznou mierou podľa criticality a maturity. Model sa musí vybrať explicitne a obsahovať entry, ongoing a exit criteria.

- **Product team primary on-call, SRE coaching — capability building**: SRE pomáha so SLO, alerting a resilience a service tím vedie bežnú prevádzku.
- **Shared on-call — spoločná responsibility po readiness gate-e**: SRE nevstupuje do neoperovateľnej služby bez documentation, telemetry a sustainable page loadu.
- **Temporary SRE engagement — stabilizácia critical service-u**: spoločný backlog odstráni reliability gaps a ownership sa následne vráti podľa plánu.
- **Platform SRE — reusable reliability capabilities**: automation a standards znižujú duplicitu, ale application semantics ostávajú service ownerovi.

SRE nemá byť permanentný odkladací tím pre services, ktorých product roadmap nefinancuje reliability.

## 18. Central NOC alebo Operations model

Princíp možno zachovať aj pri centralizovanom first-line monitoring-u. NOC môže prijímať broad events, vykonať known remediation a eskalovať podľa service catalogu.

Service tím však stále vlastní alert semantics, application diagnosis, permanent fix a feedback do designu. Central operations nesmie byť jediným miestom, kde sa production learning zastaví.

Model je vhodný pri veľkom počte services, 24/7 coverage alebo regulovaných procedures, ak handoff zachová context, authority a response SLO.

## 19. Criticality-based adaptation

Nie každá služba potrebuje rovnaký on-call a readiness depth. Interný best-effort report a payment authorization platform majú odlišný business impact, data risk a recovery requirement.

Faktory ovplyvňujú operating model:

- **Service criticality — dopad nedostupnosti alebo nesprávneho výsledku**: vyšší risk potrebuje kratšiu response a hlbšie recovery tests.
- **Team size a geography — udržateľnosť rotácie**: malý tím nemusí bezpečne pokryť 24/7 bez shared supportu.
- **Regulatory requirements — audit, segregation a response procedure**: decision authority môže vyžadovať formálnejší control.
- **Platform maturity — množstvo shared toil-u**: slabá self-service platforma robí priame operations ownership neprimerane drahé.
- **Incident frequency — aktuálny operational load**: recurring pages vyžadujú stabilization pred rozšírením feature scope-u.
- **Expert availability — bounded high-risk operations**: database alebo security action môže vyžadovať specialized escalation.

## 20. End-to-end migration incident príklad

Aplikácia po nasadení zlyháva pre nekompatibilnú database migration. Oddelený model umožní operations rollbacknúť Pod, database tím analyzovať locks a development dostať ticket až ďalší deň.

You build it, you run it mení design skôr než incident vznikne:

```text
service tím navrhne expand/contract migration
→ pipeline testuje old a new application version na reprezentatívnej schema
→ rollout začne canary cohortom
→ telemetry sleduje error ratio, query latency a lock wait
→ pri regresii owner zastaví rollout a zvolí compatible rollback alebo roll-forward
→ post-incident action mení migration template a tests
```

Rozdiel nie je v tom, kto fyzicky drží pager. Production risk ovplyvnil code, test, rollout aj permanent learning.

## 21. Healthy-model evidence

Zdravý model sa prejavuje behaviorom:

- **Tím pozná production SLI a business outcome**: incident a release decisions používajú service evidence, nie iba infrastructure health.
- **Pages sú akčné a udržateľné**: on-call nezískava stovky warnings ani permanentný nočný toil.
- **Rollback a recovery sú nacvičené**: response path má reálny access a data-compatible mechanismus.
- **Incidents menia system**: recurring failure vytvára test, guardrail, architecture alebo ownership improvement.
- **Reliability je súčasť plánovania**: product a operations work sú v jednom priority modeli.
- **Platforma poskytuje self-service**: product team nevykonáva každý infra detail, ale nemusí čakať v ticket queue.
- **Manual interventions dlhodobo klesajú**: learning a automation odstraňujú opakovaný toil namiesto rozširovania on-call rotácie.

## 22. Anti-patterny

### Pager bez podpory

Vývojári dostanú on-call bez telemetry, runbookov, accessu a školenia. Organization presunie bolesť, ale nevytvorí operating capability.

### Operations ako druhá práca

Tím má plnú feature roadmapu a reliability work sa očakáva navyše. Incident load rastie a permanent fixes sa odkladajú.

### Zrušenie špecialistov

Princíp sa interpretuje ako dôvod odstrániť Ops, SRE alebo database expertise. Product tímy potom vykonávajú high-risk zásahy bez dostatočnej hĺbky a organization duplikuje platform work.

### Alerting podľa infra metrík

Pager reaguje na CPU, Pod restart alebo disk percentage bez user-impact a action contractu. On-call sa stáva manuálnym monitoring processorom.

### Nejasný escalation path

Service tím je formálne owner, ale pri cluster, identity alebo database incidente nevie aktivovať správneho specialistu. Ownership sa mení na izoláciu.

### SRE ako permanentný dumping ground

Problematic service sa odovzdá SRE bez readiness a bez product follow-upu. SRE vlastní consequences decisions, ktoré nevie prioritizovať ani meniť.

### Run it bez learn it

Tím incident vyrieši, ale actions nevstúpia do tests, platformy ani backlogu. Pager poskytuje feedback, ktorý nemení budúci system.

## 23. Troubleshooting operating modelu

Pri zlyhávajúcom modeli nehľadaj iba chýbajúceho on-call človeka. Zmapuj service outcome, runtime evidence, access, authority, platform interface a roadmap capacity.

- **Page ping-pong — nejasný primary owner alebo dependency classification**: definuj incident lead, evidence handoff a shared escalation.
- **Tím nevie diagnozovať — chýba instrumentation, access alebo training**: doplň capabilities pred rozšírením response expectationu.
- **Reliability backlog sa nehýbe — incentives a capacity gap**: prepoj toil, SLO a incident cost s product prioritization.
- **Platform team rieši application errors — self-service a responsibility boundary sú slabé**: uprav interface, docs a routing namiesto pridania ďalšieho ticket template-u.
- **On-call load rastie — recurring failure sa neinštitucionalizuje**: zmeraj page sources a financuj removal najväčšieho toil constraintu.

## 24. Kontrolné otázky

1. Aký problem rieši you build it, you run it oproti tradičnému handoffu?
2. Čo zahŕňa „build it“ mimo application code-u?
3. Prečo „run it“ nie je synonymom pager duty?
4. Aké časti má explicitný operating contract?
5. Ako sa rozdeľuje service a platform responsibility?
6. Prečo observability a safe delivery sú prerequisites priameho ownershipu?
7. Čo robí on-call udržateľným a akčným?
8. Čo musí alert owner pravidelne overovať?
9. Ako operational readiness chráni failure lifecycle, nie iba deployment?
10. Kedy je vhodný shared SRE alebo central NOC model?
11. Prečo criticality mení hĺbku operating modelu?
12. Aké evidence dokazujú, že production feedback mení design?

## 25. Zhrnutie

You build it, you run it uzatvára feedback medzi tvorbou služby a jej produkčným behaviorom. Service tím vlastní outcome, application semantics, reliability a permanent learning, ale používa platform a expert capabilities namiesto správy všetkých vrstiev osobne.

Model funguje iba s observability, safe delivery, runbooks, accessom, sustainable on-call, explicitnými boundaries a financovanou reliability kapacitou. Pager bez týchto podmienok je presun toil-u; správny model mení design a delivery podľa reálnych production consequences.

## Glossary impact

Relevantné pojmy: you build it you run it, operating contract, service team, platform team, operational readiness, on-call, actionable alert, first-line operations, shared on-call, SRE engagement, break-glass access a criticality-based operations.

## Primárne zdroje

- [Google SRE — Introduction](https://sre.google/sre-book/introduction/)
- [Google SRE — Being On-Call](https://sre.google/sre-book/being-on-call/)
- [Team Topologies](https://teamtopologies.com/)
- [Google Cloud — DevOps capabilities](https://cloud.google.com/architecture/devops)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ownership mindset](ownership-mindset.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Automation mindset →](automation-mindset.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
