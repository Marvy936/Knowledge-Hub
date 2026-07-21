# Canary deployment

Canary deployment postupne vystavuje novú verziu obmedzenej časti produkčného trafficu alebo používateľov. Cieľom nie je iba nasadzovať pomalšie, ale znížiť blast radius a získať produkčný dôkaz pred širšou promotion.

## 1. Základný model

```text
stable version
→ deploy canary instances
→ pošli malý podiel trafficu
→ porovnaj technické a business signály
→ promote, pause alebo abort
→ rozširuj expozíciu po krokoch
```

Canary je rollout stratégia. Nie je to automaticky A/B experiment ani náhrada testov pred deploymentom.

## 2. Deployment, release a exposure

Rozlišuj:

- **deployment** — nová verzia fyzicky existuje v runtime,
- **release** — capability je sprístupnená používateľom,
- **exposure** — aký podiel alebo segment trafficu novú verziu reálne používa.

Canary môže riadiť exposure routingom, feature flagom alebo kombináciou oboch.

## 3. Výber canary segmentu

Možnosti:

- náhodné percento requestov,
- stabilný hash používateľa alebo tenant ID,
- interní používatelia,
- konkrétny región alebo availability zone,
- nízkorizikový customer segment,
- vybrané API routes,
- konkrétna device alebo client verzia.

Segment musí byť reprezentatívny pre testovaný risk. Canary iba na interných používateľoch nemusí odhaliť produkčný workload, scale alebo data distribution problémy.

## 4. Stabilita zaradenia

Pri stateful workflow má používateľ zostať počas session alebo experimentu v rovnakej skupine.

Použi napríklad:

```text
bucket = hash(stable_subject_id + experiment_salt) mod 10000
```

Nestabilné random routing rozhodnutie pri každom requeste môže miešať verzie v jednom workflow a skresliť výsledky.

## 5. Rollout steps

Príklad:

```text
1 % → 5 min observation
5 % → 15 min observation
20 % → 30 min observation
50 % → 60 min observation
100 %
```

Kroky nemajú byť univerzálne. Závisia od:

- request rate,
- času potrebného na prejavenie chyby,
- dĺžky business workflow,
- batch a scheduled jobs,
- cache warm-up,
- blast radiusu,
- schopnosti rollbacku.

Pri nízkom trafficu môže 1 % znamenať príliš málo vzoriek.

## 6. Baseline a control

Canary sa má porovnávať so stabilnou verziou v rovnakom čase a podobných podmienkach.

Dôležité je odlíšiť:

- regresiu novej verzie,
- všeobecný incident,
- zmenu workloadu,
- regionálny alebo dependency problém,
- sezónnosť.

Historický priemer bez súbežnej control group môže byť zavádzajúci.

## 7. Promotion criteria

Promotion policy môže zahŕňať:

- error rate a error budget burn,
- latency percentiles,
- saturation,
- restart alebo crash rate,
- dependency failures,
- queue lag,
- resource efficiency,
- business conversion alebo success rate,
- authorization a security anomalies,
- počet vzoriek a confidence.

Každé kritérium musí byť naviazané na konkrétnu verziu a segment.

## 8. Abort criteria

Abort musí byť explicitný pred rolloutom:

```text
p99 latency > limit počas 5 min
OR error-budget burn > threshold
OR payment success rate klesne o definovanú hodnotu
→ zastav promotion
→ odober canary traffic
→ vyber rollback alebo roll-forward
```

Neurčité pravidlo „pozrieme dashboard“ vytvára pomalé a nekonzistentné rozhodovanie.

## 9. Automatická canary analysis

Automatizovaný controller môže:

1. nasadiť canary,
2. nastaviť traffic weight,
3. čakať observation window,
4. načítať metrics,
5. porovnať canary s baseline,
6. vyhodnotiť policy,
7. promotionovať alebo abortovať.

Controller musí riešiť missing telemetry, delayed data, noisy metrics a nedostupnosť analytickej služby. Pre kritické signály je bezpečnejšie fail closed alebo explicitne pause.

## 10. Sample size a confidence

Percento trafficu samo osebe neurčuje kvalitu dôkazu. Sleduj:

- počet relevantných requestov,
- počet business udalostí,
- variabilitu metric,
- minimálny detectable effect,
- observation duration,
- opakované rozhodovanie nad rovnakými dátami.

Príliš agresívna automatická promotion pri malej vzorke vytvára false confidence.

## 11. Version-level telemetry

Každý signal musí obsahovať aspoň:

- artifact digest alebo release version,
- environment,
- deployment ID,
- canary/stable cohort,
- region/zone,
- route alebo operation,
- tenant alebo segment podľa privacy pravidiel.

Bez version labelov nemožno spoľahlivo priradiť regresiu ku canary.

## 12. Capacity a autoscaling

Canary instances musia mať dosť trafficu na zmysluplný test, ale nesmú byť preťažené iba preto, že majú príliš malú fleet.

Over:

- requests per instance,
- autoscaling behavior,
- connection pool limits,
- cache hit rate,
- warm-up,
- zone distribution,
- pod disruption a scheduling.

Porovnávaj normalizované metriky, nie iba absolútne hodnoty celej fleet.

## 13. Stateful systémy

Canary komplikuje:

- sessions,
- cache schema,
- databázové writes,
- queue consumers,
- background jobs,
- event schemas,
- long-lived connections.

Stará a nová verzia musia byť počas overlapu kompatibilné. Routing rollback nevráti databázový stav.

## 14. Long-lived connections

WebSockets, streaming a keep-alive connections môžu zostať na starej verzii dlho po zmene weightu.

Potrebné sú:

- connection draining,
- max connection age,
- reconnect policy,
- version-aware telemetry,
- oddelené promotion criteria pre nové a existujúce connections.

## 15. Security a privacy

Segmentácia nesmie vytvárať diskriminačné alebo neauditovateľné zaobchádzanie. Chráň:

- cohort assignment,
- customer identifiers,
- experiment metadata,
- privileged internal cohorts,
- logované business výsledky.

Canary routing pravidlá sú produkčná policy a musia byť reviewované a auditované.

## 16. Failure scenáre

### Canary vyzerá zdravá, po promotion zlyhá

Možné príčiny:

- nereprezentatívny segment,
- príliš malá vzorka,
- problém sa prejaví až pri vyššej concurrency,
- cache alebo dependency threshold,
- scheduled job sa ešte nespustil,
- observation window bola krátka.

### Canary je horšia iba v jednej zóne

Oddeľ version effect od zone capacity, network a dependency problému.

### Metrics chýbajú

Nepovažuj absenciu dát za úspech. Pause alebo fail podľa kritickosti signálu.

### Rollback nezastavil dopad

Nová verzia už vytvorila nekompatibilné dáta alebo side effects. Potrebný môže byť roll-forward, compensating action alebo restore.

## 17. Anti-patterny

### Canary = jeden pod bez riadeného trafficu

Existencia jednej novej instance nie je canary stratégia bez cohort, metrics a rozhodovacej policy.

### Promotion iba podľa CPU

Technická stabilita nedokazuje správny business výsledok.

### 1 % na dve minúty

Môže byť štatisticky aj prevádzkovo bezvýznamné.

### Automatický rollback na noisy alert

Spôsobuje oscillation a môže zhoršiť incident.

### Canary používa iný config než final fleet

Evidence sa nevzťahuje na skutočný production target.

## 18. Rozhodovací rámec

1. Aký failure risk má canary odhaliť?
2. Ktorý cohort je reprezentatívny a eticky prijateľný?
3. Ako stabilne priraďujeme používateľov?
4. Aká minimálna vzorka a observation window je potrebná?
5. Ktoré technické a business metrics rozhodujú?
6. Čo sa stane pri missing telemetry?
7. Aké sú promotion, pause a abort criteria?
8. Je stará a nová verzia state-compatible?
9. Aký je recovery plán po nekompatibilnom write?
10. Ako sa výsledok a rozhodnutie auditujú?

## 19. Kontrolné otázky

1. Aký je rozdiel medzi canary deploymentom a A/B testom?
2. Prečo percento trafficu nestačí na určenie sample size?
3. Prečo je stabilné cohort assignment dôležité?
4. Aký význam má súbežná baseline?
5. Čo patrí do promotion a abort criteria?
6. Ako autoscaling skresľuje canary porovnanie?
7. Aké problémy prinášajú long-lived connections?
8. Prečo routing rollback nie je data rollback?
9. Ako má controller reagovať na chýbajúce metrics?
10. Kedy je canary segment nereprezentatívny?

## Glossary impact

Relevantné pojmy: canary deployment, canary cohort, stable cohort, traffic weight, cohort assignment, observation window, promotion criterion, abort criterion, automated canary analysis, version-level telemetry, sample size a progressive exposure.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Blue-green deployment](blue-green-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: A/B testing →](a-b-testing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
