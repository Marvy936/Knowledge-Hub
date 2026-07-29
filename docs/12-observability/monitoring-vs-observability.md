# Monitoring vs. observability

Monitoring a observability nie sú dve konkurenčné platformové funkcie. Sú to dve časti jedného operational evidence systému. Monitoring priebežne vyhodnocuje vopred definované podmienky nad známym subjectom. Observability určuje, či má responder po detekcii dostatočný, korelovateľný a dôveryhodný dôkaz na položenie nových otázok, lokalizovanie mechanizmu a overenie nápravy.

Observability preto nemožno odvodiť z počtu dashboardov, uložených terabajtov ani z nákupu konkrétneho backendu. Vzniká až vtedy, keď system behavior, instrumentation, telemetry pipeline, query model, ownership a decision workflow tvoria jeden testovaný contract.

## 1. Dominantný lifecycle

```text
business alebo operational otázka
→ exact observed subject a expected outcome
→ známa monitorovacia podmienka alebo nová investigation otázka
→ signal-generation a coverage contract
→ collection, delivery, processing a storage
→ monitoring verdict alebo investigation evidence
→ cross-signal correlation a causal explanation
→ bounded operational decision
→ recovery alebo improvement
→ original, forbidden a telemetry-outcome validation
→ skoršia detection/instrumentation/control zmena
```

Tento lifecycle oddeľuje tri výsledky, ktoré sa často zamieňajú:

```text
monitoring condition je green
≠ používateľský outcome je správny
≠ systém je dostatočne observable na vysvetlenie neznámeho failure
```

Green dashboard môže byť správny pre svoju úzku otázku a zároveň zavádzajúci pre širší business outcome. Rovnako môže byť služba zdravá, ale telemetry pipeline nefunkčná. Neprítomnosť erroru v backende preto nie je automaticky dôkazom neprítomnosti erroru v produkcii.

## 2. Exact observed subject

Pred každým alertom, dashboardom alebo investigation urč, čo je skutočne pozorovaný subject. Názov služby nestačí. Subject musí viazať business outcome na konkrétnu release, operation a evidence generation.

Pre Atlas Payments používame:

```text
observability subject: OBS-PAY-43
business capability: CAP-PAY-42
journey: enterprise payment settlement
logical operation: settle(payment_id)
entry operation: POST /payments/{id}/settle
release generation: 7.19.0
provider-adapter config generation: PROVIDER-CFG-34
telemetry generation: OTEL-PAY-12
environment: production
Region: eu-central-1
AZ cohorts: eu-central-1a, eu-central-1b
SLO: 99.9 % valid settlements completed do 2.5 s za 28 dní
```

Tento subject umožňuje rozlíšiť, či sa dôkaz týka HTTP acceptance, provider authorization, durable ledger commit, async completion, konkrétnej release alebo iba všeobecného process healthu.

## 3. Monitoring ako vopred definovaný decision contract

Monitoring začína známou otázkou a dopredu určeným verdictom. Napríklad:

```text
settlement completion SLI za 5 minút
→ burn-rate expression
→ threshold + duration
→ firing alebo healthy verdict
→ page route
→ owner a runbook
```

Monitoring je silný vtedy, keď podmienka reprezentuje stav vyžadujúci action. Je vhodný pre dostupnosť, SLO burn, missed completion, queue age, capacity headroom, failed backup, expiring certificate alebo stratu telemetry canary.

Threshold sám osebe nie je monitorovací contract. Potrebuje measurement boundary, validný numerator a denominator, no-data semantics, expected traffic, ownera, severity, recovery condition a spôsob overenia, že alert skutočne dorazí.

CPU nad 90 % môže byť normálny efektívny stav, leading capacity signal alebo príčina degradácie. Bez väzby na workload a outcome je to iba observation, nie automaticky page-worthy incident.

## 4. Observability ako schopnosť odpovedať na nové otázky

Po detekcii často nie je vopred známe, ktorá kombinácia release, AZ, dependency, tenant class, queue path alebo configuration generation vytvorila failure. Observability je schopnosť vytvoriť diskriminačné queries nad už existujúcim dôkazom bez nasadenia novej diagnostickej verzie počas incidentu.

Užitočná observability umožní prejsť:

```text
business alebo SLO symptom
→ presný time window a affected cohort
→ release/configuration correlation
→ request alebo workflow path
→ failing dependency alebo state transition
→ mechanizmus
→ owner a bezpečná remediation
```

Neznamená to uložiť každý payload a každý request navždy. Potrebný je dostatočný context pri bounded cardinality, sampling, retention, privacy a cost modeli.

## 5. Monitoring a observability sa navzájom podmieňujú

Monitoring bez observability vytvorí page, ale responder nevie odlíšiť root cause od náhodnej korelácie. Observability bez monitoringu môže umožniť detailnú post-hoc analýzu, no incident zostane neodhalený, kým ho nenahlási používateľ.

Správny operating model je:

```text
monitoring deteguje a prioritizuje
→ observability lokalizuje a vysvetľuje
→ recovery obnoví outcome
→ monitoring aj observability overia closure
```

Po incidente sa observability finding môže zmeniť na nový monitorovací contract. Nie každá investigation dimension však patrí do permanentného alertu alebo metric labelu. Detail s vysokou cardinality môže zostať v traces alebo logs a alert používať bounded agregáciu.

## 6. Telemetry coverage contract

Telemetry sú records o správaní systému. Coverage contract určuje, ktoré časti critical journey musia byť pozorovateľné a aký dôkaz očakávame pri success, failure a neprítomnosti signalu.

Pre settlement journey potrebujeme aspoň:

```text
client alebo black-box outcome
→ edge/service acceptance
→ logical-operation identity
→ provider attempt a response
→ ledger commit alebo rollback
→ queue acknowledgement/redelivery
→ final business completion
```

Ak telemetry existuje iba pri HTTP acceptance, nedokáže vysvetliť failure po odpovedi `202`. Ak existuje iba na workerovi, nemusí preukázať, že client dostal správny výsledok. Coverage musí kopírovať business transaction a failure boundaries, nie organizačný zoznam služieb.

Coverage má tiež negatívny contract. Napríklad žiadny raw token, card data alebo nekontrolovaný customer identifier nesmie prejsť do logs, baggage ani indexed attributes.

## 7. White-box, black-box a business-outcome observation

White-box signals opisujú interné správanie: request rate, pool wait, GC, queue depth, exporter drops alebo database connections. Black-box signals pozorujú službu zvonka cez DNS, TLS, HTTP a user-like synthetics.

Ani jedna perspektíva automaticky nepreukazuje business completion. Atlas môže mať healthy ALB targety a úspešný `202`, hoci provider authorization alebo ledger reconciliation zlyháva o niekoľko sekúnd neskôr.

Pre kritický journey preto spájaj:

```text
black-box reachability a latency
+ white-box service/dependency state
+ business completion a correctness
```

Platform health je dôležitý mechanistický dôkaz. Business outcome je acceptance oracle.

## 8. Signal nie je automaticky evidence

Metric, log alebo trace sa stane evidence až po určení identity, významu, coverage a integrity. Pri každom významnom signale over:

- kto ho produkuje a pri akej state transition;
- či reprezentuje logical operation, technical attempt alebo sampled subset;
- ktorú release, resource a instrumentation generation nesie;
- ako sa doručuje, filtruje, agreguje a uchováva;
- aké no-data a stale-data stavy sú možné;
- kto ho používa na aké rozhodnutie.

Signal bez týchto vlastností môže byť užitočný hint, ale nie autoritatívny verdict.

## 9. Correlation chain

Korelácia nemá byť iba ručné porovnanie timestampov. Queue delay, clock skew, retry a async fan-out môžu vytvoriť nesprávny príbeh. Stabilný correlation contract používa trace/span context, logical-operation ID a versionované resource metadata.

Typický investigation chain:

```text
SLO burn alebo business-completion alert
→ affected operation a bounded cohort
→ exemplar alebo trace ID
→ service a dependency spans
→ structured logs s rovnakým trace/logical-operation contextom
→ deployment/configuration event
→ audit actor alebo controller action
→ recovery validation
```

Request ID, trace ID ani payment ID nepatria automaticky do metric labels. Môžu byť vhodné v sampled traces alebo protected logs. Metrics používajú bounded dimensions ako operation, result class, release channel, Region alebo AZ.

## 10. Telemetry pipeline je production systém

Observed application a observability platforma sú dva rozdielne systémy. Pipeline môže zlyhať v ktorejkoľvek vrstve:

```text
operation
→ instrumentation
→ local SDK/agent buffer
→ collector receiver
→ processors, sampling a redaction
→ exporter/network/auth
→ backend ingestion/index
→ query/time range/tenant
→ dashboard alebo rule
```

Preto monitoruj accepted, refused, queued, retried a dropped records, exporter failures, ingestion lag, scrape health, config generation a end-to-end telemetry canaries.

Dôležitý absent-evidence verdict znie:

```text
signal chýba, pretože udalosť nenastala
alebo
signal chýba, pretože zlyhala emission/delivery/query boundary?
```

Bez tejto otázky môže telemetry outage vyzerať ako zázračné uzdravenie produkcie.

## 11. SLO, ownership a operational decisions

SLO určuje, ktoré outcomes majú prioritu a akú presnosť telemetry potrebuje. Instrumentation by mala vzniknúť z user journey a failure modelu, nie z dostupných widgetov.

Každý critical signal potrebuje ownera. Owner zodpovedá za semantics, schema migration, alert/query consumers, cost, privacy a retirement. Neowned telemetry sa časom mení na drahý a nedôveryhodný tok.

Decision-oriented observability odpovedá nielen „čo sa zmenilo“, ale aj:

- ktorého subjectu sa zmena týka;
- či je impact user-visible;
- ktorá hypotéza je evidence-backed;
- aká action je bezpečná;
- ako sa preukáže recovery a forbidden outcome.

## 12. Cost, retention a security

Observability cost vzniká pri emission, CPU/memory overheade, network transfere, ingestion, cardinality, indexovaní, query a retention. Cost control je súčasť signal designu, nie neskoršie slepé vypínanie logs.

Retention vychádza z detection latency, SLO windows, incident recurrence, audit/compliance a recovery potrieb. Security a audit evidence môže potrebovať odlišný account, access model a immutable retention než application diagnostics.

Telemetry môže obsahovať credentials, authorization headers, query text, customer identifiers, topology alebo payload fragments. Minimalizácia a redaction musia prebehnúť čo najbližšie k producerovi; odstránenie field-u až v dashboard UI nezabráni jeho exportu a uloženiu.

## 13. Worked incident: monitoring green na nesprávnej boundary

### Symptom

Dňa `2026-07-29` o `09:18 UTC` Atlas settlement-completion SLO spustí fast-burn page. Celkový HTTP dashboard je green:

```text
POST /payments/{id}/settle
HTTP 202 success: 99.98 %
handler p95: 84 ms
CPU: 46 %
healthy targets: 24/24
```

Používatelia enterprise merchantov však dostávajú settlement confirmation oneskorene alebo vôbec.

### Exact incident subject

```text
OBS-PAY-43
release 7.19.0
logical operation settle(payment_id)
merchant.class = enterprise
provider route = provider-a/high-value
AZ cohort = eu-central-1b
provider config = PROVIDER-CFG-34
telemetry generation = OTEL-PAY-12
incident window = 09:12–09:31 UTC
```

### Prečo monitoring nebol v rozpore

HTTP monitor meral acceptance boundary. Request bol prijatý do async workflowu a korektne vrátil `202`. Business SLI meral final settlement completion. Oba signals boli správne, ale odpovedali na rozdielne otázky.

### Competing hypotheses

1. settlement completion metric alebo pipeline je nefunkčná;
2. provider-a má globálny outage;
3. release 7.19.0 zlyháva pre všetky requests;
4. problém je iba v jednom AZ alebo config cohort-e;
5. queue consumer laguje alebo neacknowledguje messages;
6. enterprise route používa neplatný mTLS trust bundle;
7. ledger commit je úspešný, ale completion event sa stráca.

### Discriminating evidence

```text
black-box enterprise synthetic
→ completion metric podľa merchant.class/AZ/version
→ trace exemplar logical operation
→ provider-adapter span events
→ correlated structured log
→ deployment/config generation event
→ task loaded-state inventory
```

Evidence ukáže:

- standard merchant class je zdravá;
- enterprise failures sú iba na release `7.19.0` v `eu-central-1b`;
- queue age je nízka a messages sa spracúvajú;
- trace končí na provider-adapter mTLS handshake;
- logs nesú `tls.alert=unknown_ca` a `config.generation=PROVIDER-CFG-34`;
- tasks v `eu-central-1a` načítali `PROVIDER-CFG-35`, cohort v `1b` zostal na starej generation;
- provider health a ledger path pre úspešný cohort sú zdravé.

Root cause je stale loaded trust-bundle generation na jednej release/AZ cohort-e. Aggregate HTTP monitoring ho skryl, pretože acceptance prebehla pred downstream settlementom a enterprise traffic tvoril malý podiel celkového volume-u.

### Evidence-preserving containment

- zastaviť rollout a ďalšiu automatickú replacement slučku;
- odobrať affected `1b/7.19.0/CFG-34` cohort z enterprise routing-u;
- zachovať trace IDs, config inventory, task-definition generation a provider logs;
- nezvýšiť plošne timeouts ani retries, ktoré by zosilnili provider load;
- ponechať standard cohort a healthy AZ v prevádzke.

### Authoritative recovery

1. vytvoriť immutable config generation `PROVIDER-CFG-35` s kompletným CA bundle;
2. canary task musí preukázať loaded generation, nie iba desired configuration;
3. vykonať enterprise settlement synthetic cez provider-a;
4. rozšíriť rollout po AZ-bounded waves;
5. znovu povoliť enterprise routing až po business completion evidence;
6. doplniť config-loaded generation do resource metadata a release acceptance.

### Acceptance verdict

Incident je uzavretý až keď:

- enterprise settlement completion SLI sa obnoví;
- `202` acceptance aj final settlement majú správny pomer a latency;
- všetky production cohorts reportujú `PROVIDER-CFG-35` ako loaded state;
- provider authorization a ledger obsahujú exactly one business outcome;
- forbidden stale-config cohort nevstupuje do routing-u;
- telemetry canary pre metric, trace a log correlation prejde;
- rovnaká query neodhalí susedný AZ alebo version cohort s driftom.

### Earlier controls

Postmortem vytvorí:

- business-completion monitoring oddelený od HTTP acceptance;
- bounded dimensions `merchant.class`, AZ a release channel;
- release gate nad loaded configuration generation;
- enterprise synthetic po každej provider trust-bundle zmene;
- correlation link z SLO alertu na trace a config inventory;
- no-data alert pre settlement-completion signal a telemetry canary.

## 14. Troubleshooting observability gapu

Keď signal alebo vysvetlenie chýba, začni exact subjectom a dvoma konkurenčnými vetvami: systém je zdravý alebo evidence path zlyhala.

```text
producer vykonal očakávanú operation?
→ instrumentation vytvorila record?
→ resource/operation identity je správna?
→ context sa preniesol cez všetky boundaries?
→ sampling/filtering/redaction record zachovali?
→ agent/collector record prijal a odoslal?
→ backend ho ingestoval a indexoval?
→ správny tenant, Region, schema, time range a time zone?
→ dashboard/rule používa current generation?
```

Zachovaj sample operation ID, timestamps, source config, collector self-telemetry, exporter errors, backend ingestion evidence a exact query. Reštart collectora bez dôkazu môže odstrániť queue/drop state a znemožniť root-cause analýzu.

## 15. Anti-patterny

### Observability je kúpený produkt

Backend bez správnej instrumentation, contextu, coverage a ownershipu iba ukladá dáta.

### Green dashboard znamená healthy business

Dashboard môže merať inú boundary, stale generation alebo neúplný cohort.

### Chýbajúce errors znamenajú žiadne errors

Emission, delivery, sampling, retention alebo query failure môže odstrániť evidence.

### Logovať všetko

Zvyšuje noise, cost a privacy riziko bez garantovanej diagnostickej hodnoty.

### Alertovať každú internú anomáliu

Troubleshooting signal bez user impactu alebo action contractu vytvára fatigue.

### Korelácia iba timestampom

Retry, async queue a clock skew vytvárajú falošnú causalitu.

### Observability dependency blokuje business request

Telemetry outage sa zmení na production outage, ak export nemá bounded failure behavior.

## 16. Kontrolné otázky

1. Aký je rozdiel medzi monitorovacím verdictom a observability capability?
2. Čo musí obsahovať exact observed subject?
3. Prečo green HTTP dashboard nepreukazuje business completion?
4. Ako rozlíšiš neprítomnosť udalosti od telemetry gapu?
5. Akú úlohu má SLO pri návrhu telemetry?
6. Prečo nestačí korelácia iba podľa timestampu?
7. Ako sa líši white-box, black-box a business-outcome evidence?
8. Kedy je signal iba hint a kedy autoritatívny dôkaz?
9. Ako monitoruješ observability pipeline ako production systém?
10. Aký acceptance verdict uzavrel incident `OBS-PAY-43`?

## Glossary impact

Relevantné pojmy: observed subject, monitoring condition contract, observability question contract, telemetry coverage contract, business-outcome observation, absent-evidence verdict, correlation chain, loaded-state telemetry, observability acceptance verdict, instrumentation gap, telemetry canary a decision-oriented observability.

## Primárne zdroje

- [OpenTelemetry observability primer](https://opentelemetry.io/docs/concepts/observability-primer/)
- [OpenTelemetry signals](https://opentelemetry.io/docs/concepts/signals/)
- [OpenTelemetry instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/)
- [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Prometheus instrumentation practices](https://prometheus.io/docs/practices/instrumentation/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CloudOps troubleshooting drills](../11-cloud-and-aws/cloudops-troubleshooting-drills.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Metrics, logs, traces a events →](metrics-logs-traces-events.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
