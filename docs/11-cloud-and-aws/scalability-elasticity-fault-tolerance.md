# Scalability, elasticity a fault tolerance

Scalability, elasticity a fault tolerance nie sú tri názvy pre rovnakú vlastnosť. Scalability opisuje, či sa bezpečná kapacita systému dokáže zväčšiť. Elasticity riadi, kedy sa kapacita pridáva alebo odoberá. Fault tolerance určuje, či business outcome pokračuje po strate komponentu alebo failure domainu.

Kapitola používa jeden dominantný lifecycle:

```text
business demand a availability objective
→ workload unit a end-to-end capacity model
→ bottleneck a failure-domain inventory
→ scaling/failover policy
→ provisioning alebo traffic redistribution
→ readiness a serving-capacity realization
→ downstream saturation a failure behavior
→ user/business outcome
→ scale-in, recovery a control tuning
```

## 1. Exact capacity subject

Atlas Payments prevádzkuje release `PAY-4.2.0` v AWS Region `eu-central-1`. Subject kapacitného rozhodnutia obsahuje:

```text
service = payments-api
release/image generation = PAY-4.2.0 / I57
traffic cohort = ALB target group TG-PAY-42
compute fleet = Auto Scaling group ASG-PAY-42
Availability Zones = eu-central-1a/1b/1c
scaling-policy generation = SP-19
metric contract = valid checkout requests per ready target
minimum/desired/maximum capacity = 6/6/30
warm-up and drain budgets = 180 s / 60 s
critical downstream = ledger database writer DB-P42
business outcome = payment authorized exactly once within p99 800 ms
```

Bez tejto identity sa ľahko porovnáva metric jednej fleet generation s capacity alebo business resultom inej.

## 2. Capacity je celý critical path

Compute replicas nie sú automaticky business capacity. Bezpečný throughput určuje najužší relevantný článok:

```text
arrival rate
→ load balancer a connection acceptance
→ ready application workers
→ thread/connection pools
→ queue alebo cache
→ database writer a external payment API
→ durable exactly-once result
```

Ak databáza zvládne 3 000 validných writes/s, pridanie application instances nad túto hranicu môže iba zvýšiť počet connections, retries a timeoutov. Scalability test preto musí merať, ako sa s kapacitou menia throughput, latency, error rate, backlog, downstream pressure a jednotkové náklady.

## 3. Scalability

Scalability je schopnosť zvýšiť alebo znížiť bezpečnú spracovateľskú kapacitu bez neprimeraného zhoršenia reliability, latency, operability alebo cost per successful operation.

### Vertical scaling

Vertical scaling zväčšuje jeden resource. Je vhodné, keď je distributed coordination drahšia než väčší uzol alebo keď workload ešte neprekročil praktický limit jedného writera. Neprináša však automaticky fault tolerance a môže zväčšiť blast radius.

### Horizontal scaling

Horizontal scaling pridáva workers, replicas, shards alebo partitions. Reálnu kapacitu vytvorí iba vtedy, keď:

- traffic alebo work možno bezpečne rozdeliť;
- state ownership je explicitný;
- operations sú idempotentné alebo deduplikované;
- downstream má headroom;
- nové replicas dosiahnu skutočnú serving readiness;
- scale-in dokončí, checkpointne alebo bezpečne vráti prácu.

### Scaling limit

Každá architektúra potrebuje známy limit. Môže ním byť database writer, počet queue partitions, account quota, subnet IP space, external API quota, KMS throughput, connection pool alebo serializovaný lock.

## 4. Elasticity ako control loop

Elasticity pridáva nad scalability riadiacu slučku:

```text
metric source a dimensions
→ aggregation window a freshness
→ policy evaluation
→ desired capacity
→ AWS control-plane operation
→ instance/container/function provisioning
→ initialization a health registration
→ serving capacity
→ nový metric a business result
```

Každý krok má latency a failure mode. Náhly burst môže skončiť skôr, než nová EC2 instance stihne vzniknúť, načítať image, warmnúť cache a vstúpiť do target groupu.

### Metric contract

Scaling signal musí obsahovať:

- presnú pracovnú jednotku;
- measurement point;
- dimensions a tenant scope;
- aggregation window;
- freshness a no-data semantics;
- vzťah medzi pridanou kapacitou a očakávanou zmenou signalu.

CPU môže byť vhodný pre CPU-bound service. Pre queue consumer je často lepší backlog age voči processing rate. Pre Payments je vhodnejší počet validných requestov na ready target a queueing latency než raw request count zahŕňajúci retries.

### Desired capacity nie je serving capacity

```text
desired capacity
→ launched instances
→ healthy instances
→ registered targets
→ ready application processes
→ targets prijímajúce traffic
→ business capacity
```

Autoscaling success sa neuzatvára na `DesiredCapacity=18`.

## 5. Fault tolerance

Fault tolerance znamená, že definovaný outcome pokračuje alebo sa obnoví v povolenom čase po strate komponentu alebo failure domainu.

Mechanizmy zahŕňajú:

- redundantnú kapacitu v nezávislých failure domains;
- health checks viazané na schopnosť bezpečne obslúžiť traffic;
- load balancing a bounded failover;
- stateless processing alebo replikovaný/fenced state;
- retry budgets, idempotenciu a circuit breaking;
- queues a backpressure;
- staticky stabilnú minimálnu kapacitu, ktorá nezávisí od control-plane scale-outu počas incidentu.

Fault tolerance nie je existencia troch instances. Ak sú všetky v jednej AZ, používajú jednu NAT Gateway, jeden write leader bez failoveru alebo jeden chybný deployment, spoločný failure mode zostáva.

## 6. Connected walkthrough — autoscaling zhoršuje incident

### Symptom

Po marketingovej kampani rastie p99 latency z 450 ms na 2,8 s. ASG sa škáluje zo 6 na 24 instances, ale timeout rate a databázové connections ďalej rastú.

### Competing hypotheses

1. Fleet scale-out je príliš pomalý.
2. ALB nerozdeľuje traffic rovnomerne.
3. Nové instances nie sú skutočne ready.
4. Scaling metric zahŕňa retry amplification.
5. Database writer je bottleneck.
6. External payment provider throttle-uje.
7. Jedna AZ alebo subnet nemá capacity/IP headroom.
8. Deploynutá release generation má connection leak.

### Discriminating observations

| Observation | Čo rozlišuje |
|---|---|
| valid origin requests verzus internal retries | skutočný demand od amplification |
| desired/launched/healthy/registered/ready targets | control-plane scaling od serving realization |
| requests a latency per target/AZ | uneven routing alebo degraded cohort |
| DB connections, waiters, lock time a commit throughput | compute shortage od database saturation |
| application connection-pool generation | downstream pressure spôsobený release configom |
| subnet available IPs a EC2 launch failures | policy decision od provisioning capacity |
| provider throttle/request IDs | internal bottleneck od external quota |
| exactly-once ledger a duplicate count | availability od business correctness |

### Finding

Metric `RequestCount` zahŕňala originálne requests aj automatické retries. Každá nová instance otvorila 40 databázových connections. Database writer dosiahol commit limit; latency vytvorila ďalšie retries, HPA/ASG vyhodnotili vyšší „demand“ a scale-out zosilnil connection pressure.

```text
DB saturation
→ latency a timeouty
→ retries
→ vyššia scaling metric
→ viac instances a connections
→ ešte väčšia DB saturation
```

### Containment

- zastaviť ďalší nekontrolovaný scale-out na bezpečnom maxime;
- obmedziť retries a zapnúť bounded backpressure;
- chrániť database connection budget;
- zachovať per-instance, ALB a DB evidence;
- neodstraňovať health checks ani nezvyšovať timeouty naslepo;
- zachovať presne-once operation IDs pre reconciliation.

### Recovery

1. Zmeniť metric na valid origin requests per ready target a queueing latency.
2. Zaviesť shared/proxy connection envelope a per-instance limit.
3. Opraviť retry budget a jitter.
4. Overiť database headroom pri maximálnej serving cohort.
5. Vykonať staged rollout scaling policy `SP-20`.
6. Load-testovať burst, provisioning latency, scale-in a zonal failure.

### Verification

Recovery je prijatá až keď:

- p99 je pod 800 ms;
- successful payment throughput rastie s ready capacity;
- DB connections zostávajú v rozpočte;
- retry ratio je bounded;
- scale-in nestráca ani neduplikuje operations;
- strata jednej AZ zachová minimálnu business capacity;
- duplicate authorization zostáva forbidden outcome.

## 7. Scale-in je samostatný failure boundary

Odoberaná kapacita môže držať keep-alive connections, queue claims, local cache ownership alebo rozpracované transactions. Bez drain contractu môže elasticity pri poklese demandu vytvoriť väčší incident než samotný scale-out.

Scale-in contract definuje:

```text
termination selection
→ odstránenie z nového trafficu
→ connection/work drain
→ checkpoint alebo claim release
→ final business commit
→ instance termination
→ evidence a reconciliation
```

## 8. Failure-domain a capacity model

Pre každú vrstvu eviduj:

| Vrstva | Capacity unit | Provisioning latency | Failure domain | Bezpečný minimum |
|---|---|---:|---|---:|
| ALB/targets | ready target | minúty vrátane warmupu | target/AZ | podľa zonal loss |
| EC2 fleet | healthy instance | minúty | host/AZ | pre surviving AZs |
| subnet | available IP | provisioning | subnet/AZ | surge + replacement |
| database | commits/connections | scale/failover podľa služby | instance/AZ/Region | SLO headroom |
| queue | partitions/throughput | service-specific | partition/Region | backlog deadline |
| external API | quota | často manuálna | provider/Region | retry/circuit budget |

## 9. Testing a earlier controls

Pred production použitím over:

- load test cez celý critical path;
- burst a sustained-demand scenár;
- provisioning a readiness latency;
- metric loss/no-data behavior;
- quota a subnet-IP exhaustion;
- scale-in s long-running workom;
- zonal failure pri špičke;
- downstream saturation;
- retry amplification;
- business correctness a forbidden duplicates.

Earlier controls:

- versionovaný capacity model;
- explicitný service quota inventory;
- staticky stabilná minimálna kapacita;
- per-AZ capacity headroom;
- immutable launch artifact;
- metric provenance a freshness alarms;
- connection/retry budgets;
- pravidelné fault-injection a load tests.

## 10. Kontrolné otázky

1. Aký je rozdiel medzi scalability, elasticity a fault tolerance?
2. Ktorý exact subject sa práve škáluje?
3. Aký je prvý end-to-end bottleneck?
4. Čo odlišuje desired od serving capacity?
5. Ako scaling metric reaguje na retries a downstream saturation?
6. Aký je provisioning a warm-up čas?
7. Čo sa stane pri scale-in-e?
8. Ktorý failure domain systém toleruje?
9. Dokáže surviving capacity obslúžiť peak load?
10. Aký business a forbidden outcome uzatvára test?

## Glossary impact

Relevantné pojmy: capacity lifecycle subject, workload unit, safe capacity, serving-capacity realization, scaling signal contract, provisioning latency, statically stable capacity, retry amplification loop, downstream capacity envelope, scale-in drain contract, zonal capacity headroom a capacity acceptance verdict.

## Oficiálna dokumentácia

- [AWS Well-Architected Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
- [Test scalability and performance requirements](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_testing_resiliency_test_non_functional.html)
- [Rely on the data plane during recovery](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_withstand_component_failures_avoid_control_plane.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shared responsibility model](shared-responsibility-model.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: High availability a disaster recovery →](high-availability-disaster-recovery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
