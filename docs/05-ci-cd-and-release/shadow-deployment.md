# Shadow deployment

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Shadow deployment vykonáva kópiu reálneho produkčného vstupu v novej implementácii, ale jej response ani mutations nesmú byť autoritatívne pre používateľa alebo business state. Hodnota shadowingu vzniká z vysokej fidelity workloadu; bezpečnosť vzniká iba vtedy, keď delivery, isolation a comparison contracts zabránia tomu, aby neautoritatívna execution ovplyvnila primary systém.

```text
primary input
→ versionované mirror rozhodnutie
→ capture, sanitizácia a korelácia
→ bounded delivery
→ isolated shadow execution
→ side-effect firewall
→ normalized output a runtime evidence
→ classified comparison
→ valid / inconclusive / abort
→ canary alebo remediation
```

Zahodená shadow response nie je safety mechanizmus. Payment, email, queue publication alebo shared-resource interference môžu vzniknúť ešte pred vytvorením response.

## 1. Nosný model: jedna autoritatívna a jedna neautoritatívna execution

Shadow systém má tri samostatné contracts:

```text
delivery contract
→ ktoré inputs sa mirrorujú, s akou úplnosťou, lagom, orderingom a retry semantics

safety contract
→ ktoré writes, credentials, dependencies a resource budgets sú zakázané alebo izolované

comparison contract
→ ktoré outputs sa majú zhodovať, ktoré rozdiely sú očakávané a čo znamená missing evidence
```

Primary path ostáva jediným zdrojom používateľskej response a business mutations. Shadow path je zdrojom evidence, nie rozhodovacej authority.

Ak sa tieto contracts zmiešajú, môže byť nejasné, či mismatch vznikol novým code-om, odlišným inputom, stale state-om, mirror delivery chybou alebo diff nástrojom.

## 2. Nosný scenár: Atlas Risk Engine v2

Atlas Orders chce nahradiť existujúci risk engine. Nový engine `Risk v2` má iný model a query plán, ale pred user-facing canary potrebuje dôkaz nad reálnym mixom objednávok.

Experiment subject:

```text
primary digest D_risk_v1
shadow digest D_risk_v2
primary config C_old
shadow config C_shadow17
mirror policy MP4
mirror point = Orders API po authentication a schema validation
sample policy = všetky high-risk orders + 5 % ostatných
normalization/diff revision Q8
shadow identity I_shadow_ro
```

Flow:

```text
validovaný CreateOrder command
→ primary Risk v1 vytvorí autoritatívne decision
→ sanitized mirror event ide do bounded queue
→ Risk v2 načíta read-only snapshot
→ vypočíta shadow decision a intended action plan
→ result sa spojí correlation ID
→ comparison klasifikuje rozdiel
```

Risk v2 nesmie blokovať primary request, meniť order, rezervovať inventory, emitovať customer event ani kontaktovať externý fraud provider s mutačným operation mode-om.

## 3. Mirror point určuje, čo experiment dokáže a čo obchádza

Atlas zrkadlí command po authentication a input schema validation. Tým zachová reálny business payload a tenant context, ale shadow už netestuje edge routing, TLS handshake ani invalid unauthenticated requests.

Skorší mirror point zachová viac pôvodného request contextu, ale zvyšuje privacy, credential a body-capture risk. Neskorší mirror point umožňuje sanitizáciu a stabilný domain input, ale poskytuje užší dôkaz.

Experiment record preto explicitne uvádza mirror point a excluded boundaries. Shadow pass nemožno interpretovať ako dôkaz vrstvy, ktorú mirror obišiel.

## 4. Capture a delivery nesmú poškodiť primary SLO

Atlas používa asynchronous bounded queue:

```text
primary command accepted
→ best-effort mirror enqueue s krátkym timeoutom
→ pri plnej queue drop + reason telemetry
→ primary pokračuje bez čakania na shadow execution
```

Delivery contract definuje:

- attempted, enqueued, delivered a completed identity;
- at-least-once delivery do shadow consumera;
- max lag;
- duplicate handling;
- queue depth a drop policy;
- ordering scope;
- sampling pred enqueue;
- maximum payload size.

Missing shadow result nie je equivalent result. Comparison najprv overí, či pre sample inventory existuje platný paired execution.

Synchronous mirror by zjednodušil koreláciu, ale môže preniesť shadow latency a outage do primary requestu. Použiť ho možno iba s hard timeoutom a failure isolationom, ktorý chráni primary SLO.

## 5. Input identity musí zostať semanticky porovnateľná

Nie každý request možno bez zmeny zopakovať. Atlas normalizuje:

- current time cez zachytený evaluation timestamp;
- generated IDs cez explicitné input values;
- read-once alebo veľké body cez bounded capture;
- user token na privacy-safe tenant a capability claims;
- volatile resource references cez snapshot revision;
- nondeterministický seed podľa comparison contractu.

Sanitizácia odstráni credentials, osobné identifikátory a nepotrebné fields, ale nesmie zničiť vlastnosti potrebné pre risk decision. Ak sa napríklad odstráni tenant-size alebo order-country context, shadow input už nereprezentuje primary execution.

Každý skip má reason, aby 100 % „úspešných“ výsledkov nebolo založených iba na ľahkých requestoch, ktoré capture zvládol.

## 6. Shadow identity a side-effect firewall sú enforcement boundaries

Risk v2 používa samostatnú workload identity s read-only prístupom. Output adapters sú nahradené sinkmi:

```text
database writes → zakázané policy
queue publications → shadow topic
email/SMS → null adapter
external fraud commands → sandbox/read-only endpoint
inventory reservation → intended-action record bez execution
```

Application flag `shadow_mode=true` je užitočný, ale nestačí. Ak nový code zabudne skontrolovať flag na jednej ceste, infraštruktúrne permissions a izolované adapters stále blokujú mutation.

Defense in depth:

```text
least-privilege identity
+ network egress policy
+ isolated outputs
+ application shadow mode
+ side-effect block telemetry
```

Idempotency key nie je side-effect firewall. Scope, expiry alebo downstream implementation môžu povoliť druhú mutáciu.

## 7. Read-only execution môže nepriamo ovplyvniť produkciu

Shadow môže spotrebovať shared resources:

- database connections a buffer pool;
- cache capacity;
- broker throughput;
- external API quotas;
- CPU, memory a IPs;
- logging/storage cardinality;
- autoscaler capacity.

Atlas preto stanoví budgets:

```text
shadow DB connections <= limit
mirror queue lag <= limit
primary p99 overhead <= limit
shadow compute a telemetry cost <= budget
```

Pri prekročení sa sample automaticky znižuje alebo mirror vypne. Non-authoritative execution nesmie dostať prednosť pred primary trafficom.

## 8. Comparison začína validáciou paired evidence

Pre každý sample vzniká record:

```text
mirror event ID
primary request/execution ID
shadow execution ID
primary/shadow digests a configs
captured state revision
mirror lag
primary result
shadow result
normalization revision
diff category
```

Diff taxonomy:

- equivalent;
- expected product/model difference;
- acceptable nondeterminism;
- likely primary defect;
- likely shadow defect;
- input mismatch;
- state/timing mismatch;
- missing shadow result;
- comparison-tool failure.

Jedno agregované `mismatch_rate` číslo nevysvetľuje mechanizmus. Nový risk model má byť v niektorých prípadoch odlišný; dôležitá je kvalita a safety výsledku, nie slepá byte equality.

## 9. Workload representatívnosť je súčasť validity

Atlas mirroruje všetky high-risk orders a 5 % ostatných. Sleduje sample inventory podľa:

- route a operation;
- tenant-size tier;
- regionu;
- payload size;
- risk category;
- client version;
- dependency path;
- capture skip reason.

Random sample môže podreprezentovať rare, ale kritické operácie. Naopak oversampling high-risk orders treba zohľadniť pri agregovaní výsledku, aby experiment nepredstieral produkčnú distribúciu.

## 10. Worked failure: shadow odoslal reálnu notification

Risk v2 mal nový branch pre manual review. Hlavné database writes boli read-only, ale notification adapter zostal produkčný.

```text
primary order vyhodnotená Risk v1
→ shadow Risk v2 zvolí manual review
→ application vytvorí intended notification
→ produkčný adapter odošle email zákazníkovi
→ používateľ dostane správu o stave, ktorý autoritatívny order nemá
```

### Príčina

Tím považoval read-only database credentials a discarded response za úplný safety contract. External side effect neprechádzal databázovým permission boundary.

### Dôsledok

Shadow experiment spôsobil user-facing incident napriek tomu, že jeho response nebola použitá.

### Recovery a trvalá náprava

```text
mirror kill switch
→ revoke shadow identity a egress
→ zastaviť notification adapter
→ identifikovať affected correlation IDs
→ customer correction/compensation
→ všetky adapters mapovať na explicitný intended-action sink
→ side-effect firewall contract test
```

## 11. Worked failure: mirror queue drop skryl najťažšie requesty

Queue mala nízky payload limit. Veľké multi-item orders sa nedoručili do shadowu.

```text
small orders sa mirrorujú a porovnávajú
→ large orders sú dropped pri enqueue
→ dashboard počíta mismatch iba z completed pairs
→ Risk v2 vyzerá equivalent a rýchly
→ canary odhalí timeouty na large orders
```

### Príčina

Sample inventory neobsahoval attempted → delivered → completed funnel ani skip reasons. Missing results boli implicitne odstránené z denominatora a interpretované ako success.

### Náprava

Atlas pridal expected sample inventory, payload-size segmentáciu, explicitný `missing/inconclusive` verdict a samostatný bounded capture path pre large orders.

## 12. Kauzálny diagnostický walkthrough

Symptom: po zvýšení shadow sample z 5 % na 30 % stúpla primary p99 latency, hoci shadow execution je asynchronous.

### Krok 1 — stabilizuj subject a timeline

```text
primary D_risk_v1
shadow D_risk_v2
mirror policy MP4 revision 12
sample transition 5 % → 30 % o 14:05
queue a DB budgets B7
```

### Krok 2 — formuluj konkurenčné hypotézy

```text
H1: primary release má nezávislú code regresiu
H2: enqueue path synchronne blokuje pri queue backpressure
H3: shadow reads saturujú shared DB connections alebo buffer pool
H4: zvýšený production traffic náhodou koreluje s mirror zmenou
H5: telemetry aggregation iba skreslila p99
```

### Krok 3 — použi observation points

- primary deployment/config timeline testuje H1;
- enqueue duration, queue depth a drop rate testujú H2;
- shadow connection count, DB wait a ostatné DB clients testujú H3;
- incoming workload normalizovaný podľa route testuje H4;
- raw latency traces a histogram pipeline testujú H5.

Atlas zistí:

```text
primary code bez zmeny
enqueue duration stabilná
queue nie je plná
shadow DB connections 4× vyššie
DB wait rastie pre primary aj shadow
traffic mix porovnateľný
```

H3 vysvetľuje symptom.

### Krok 4 — containment musí zasiahnuť shared-resource mechanizmus

Atlas zníži mirror sample, aplikuje shadow connection limit a oddelí read replica budget. Restart primary instances by nevyriešil shared DB contention.

### Krok 5 — over recovery

Recovery je potvrdená, keď primary p99 a DB wait klesnú, shadow throughput zostane v novom budgete a sample inventory je stále dostatočný.

### Krok 6 — vráť learning do návrhu

Incident vytvorí automatický primary-overhead abort guardrail, per-identity DB quota a load test shadow sample transitionu.

## 13. Shadow evidence má jasný fidelity limit

Shadow dokáže silno overiť:

- parser a protocol compatibility po mirror pointe;
- workload mix;
- query a dependency pattern;
- performance/resource profile;
- decision alebo response difference;
- observability novej verzie.

Neoveruje plne:

- client reaction na response;
- autoritatívne writes;
- session evolution;
- external side effects v skutočnom režime;
- dlhodobý business outcome.

Preto promotion ladder pokračuje:

```text
offline fixtures
→ replay
→ shadow
→ bounded user-facing canary
→ širší rollout
```

Shadow pass je dôkaz pre konkrétne boundaries, nie všeobecné release approval.

## 14. Diagnostický runbook

1. Potvrď primary/shadow digest, config, mirror policy a comparison revision.
2. Urči mirror point a boundaries, ktoré experiment obchádza.
3. Porovnaj attempted, enqueued, delivered, completed a paired counts.
4. Over lag, duplicates, ordering, capture skips a sample distribution.
5. Validuj sanitizáciu, state snapshot a input normalization.
6. Skontroluj shadow identity, egress a side-effect firewall.
7. Porovnaj shared-resource load a primary overhead pred/po sample zmene.
8. Klasifikuj diffs na code, input, state/timing, missing a tool failure.
9. Pri primary impacte vypni alebo obmedz mirror mechanizmus.
10. Pri side effecte spusti containment, compensation a security review.

## 15. Referenčné pravidlá

- Shadow má jednu autoritatívnu a jednu neautoritatívnu execution.
- Delivery, safety a comparison sú samostatné contracts.
- Mirror point určuje fidelity aj privacy boundary.
- Primary SLO má prednosť pred shadow completeness.
- Missing shadow result nie je success.
- Sanitizácia musí zachovať semantiku testovaného behavioru.
- Application shadow mode nenahrádza least privilege a izolované adapters.
- Read-only shadow môže poškodiť primary cez shared resources.
- Diff potrebuje correlation, normalization a taxonomy.
- Shadow pass neoprávňuje preskočiť user-facing canary.

## 16. Časté omyly

### „Response zahodíme, takže shadow je bezpečný“

Side effects a resource interference vznikajú pred response.

### „Read-only credentials riešia všetko“

Notifications, queues a external APIs môžu mutovať mimo databázy.

### „Completed pairs reprezentujú celý sample“

Drop alebo capture skip môže odstrániť najrizikovejšie inputs.

### „Každý mismatch je shadow regresia“

Môže ísť o očakávanú zmenu, nondeterminism, state lag alebo primary defect.

### „Shadow je úspešný, môžeme ísť na 100 %“

Client behavior a autoritatívny state ešte neboli overené.

## 17. Zhrnutie

Atlas shadow lifecycle je:

```text
versionovaný mirror subject
→ semanticky validný capture a sanitizácia
→ bounded primary-isolated delivery
→ least-privilege shadow execution
→ technický side-effect firewall
→ paired correlation a normalized comparison
→ classified evidence + resource/safety guardrails
→ canary alebo remediation
```

Shadow deployment je hodnotný preto, že prináša reálny workload pred používateľskou expozíciou. Je bezpečný iba vtedy, keď „neautoritatívny“ nie je zámer v kóde, ale vynútená vlastnosť identity, dependencies, outputs a resource budgets.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: A/B testing](a-b-testing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ring deployment →](ring-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
