# Shift-right

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

## 1. Definícia

Shift-right znamená rozšírenie validácie, observability a experimentovania do deploymentu a produkčnej prevádzky, kde možno overiť skutočné správanie systému, reálny traffic, používateľské workflow a failure modes, ktoré sa pred produkciou nedajú úplne reprodukovať.

Neznamená „testovať až v produkcii“. Shift-right dopĺňa shift-left.

```text
shift-left
→ prevencia a skorý feedback

shift-right
→ reálna validácia a prevádzkový feedback
```

## 2. Prečo je potrebný

Predprodukčné prostredia nedokážu úplne napodobniť:

- skutočný traffic mix,
- reálne objemy dát,
- používateľské správanie,
- regionálnu a sieťovú variabilitu,
- produkčné quotas,
- dlhodobý resource pressure,
- interakcie s externými systémami,
- emergent behavior distribuovaného systému.

Preto delivery nekončí úspešným deploymentom. Potrebuje dôkaz, že zmena funguje pre používateľa a nepoškodila prevádzku.

## 3. Základný model

```text
release
→ controlled exposure
→ observe
→ compare
→ decide
→ continue / pause / rollback / roll-forward
```

Shift-right je bezpečný iba vtedy, keď existujú:

- dostatočná observability,
- blast-radius control,
- rollback alebo roll-forward,
- jasné success criteria,
- ownership,
- rýchla reakcia na failure.

## 4. Produkčná validácia

Po deploymente overuj viac než process health.

### Technická validácia

- instances sú healthy a ready,
- error rate je stabilný,
- latency neprekročila limit,
- saturation nerastie,
- dependencies fungujú,
- logs neobsahujú nové failure patterns.

### Funkčná validácia

- kritické API workflow vracia správny výsledok,
- side effects vznikajú presne raz,
- dáta sú konzistentné,
- autorizácia funguje,
- events sú publikované a spracované.

### Business validácia

- checkout možno dokončiť,
- používateľ sa prihlási,
- platba sa zaúčtuje,
- objednávka prejde správnym stavom,
- conversion alebo completion rate sa nezhoršil.

## 5. Observability ako test oracle

V produkcii sa oracle často skladá z viacerých signálov:

```text
metrics
+ logs
+ traces
+ events
+ synthetics
+ business KPIs
+ user feedback
```

Jeden signal nestačí.

Príklad:

- HTTP 200 neznamená správny business výsledok,
- nízky error rate neznamená správnu autorizáciu,
- healthy pod neznamená dostupný checkout,
- stabilný CPU neznamená správne spracovanie events.

## 6. Synthetic monitoring

Synthetic test pravidelne vykonáva kontrolovaný scenár v produkcii.

Príklady:

- DNS resolution a TLS handshake,
- login test účtom určeným na synthetics,
- read-only API journey,
- vytvorenie a následné zrušenie testovacej objednávky,
- overenie multi-region endpointu.

Požiadavky:

- bezpečný a idempotentný scenár,
- jasne označené test dáta,
- cleanup,
- oddelené credentials,
- primeraná frekvencia,
- alerting podľa používateľského dopadu.

Synthetic monitoring nie je náhrada reálneho user telemetry.

## 7. Real User Monitoring

RUM meria skutočné používateľské sessions, napríklad:

- page load,
- frontend errors,
- Core Web Vitals,
- API latency z klienta,
- device/browser/region segmenty,
- journey completion.

Výhoda:

- zachytáva reálne prostredia a traffic mix.

Riziká:

- privacy,
- sampling bias,
- ad blockers,
- client clock,
- cardinality,
- interpretácia business contextu.

## 8. Canary release

Canary sprístupní novú verziu malej časti trafficu alebo používateľov.

```text
1 % trafficu
→ observe
→ 5 %
→ 25 %
→ 50 %
→ 100 %
```

Promotion criteria môžu zahŕňať:

- error-rate delta,
- latency delta,
- resource saturation,
- business success rate,
- support incidents,
- log anomaly,
- dependency impact.

Porovnávaj canary s kontrolnou skupinou v rovnakom čase. Absolútna metrika bez baseline môže byť zavádzajúca.

## 9. Feature flags

Feature flag oddeľuje deployment od release.

Použitie:

- interní používatelia,
- percentuálny rollout,
- konkrétny tenant,
- región,
- capability alebo experiment cohort.

Riziká:

- stale flags,
- kombinatorická explózia stavov,
- nejasná ownership,
- nekonzistentné clients,
- flag service ako dependency,
- bezpečnostná kontrola implementovaná iba flagom.

Každý dočasný flag potrebuje ownera a removal date.

## 10. Dark launch a shadow traffic

### Dark launch

Nová capability je nasadená, ale používateľovi ešte nie je dostupná.

### Shadow traffic

Kópia produkčných requestov sa posiela novému systému bez použitia jeho response ako používateľského výsledku.

Použitie:

- compatibility,
- performance porovnanie,
- capacity behavior,
- response diffing.

Riziká:

- duplicitné side effects,
- citlivé dáta,
- dvojnásobný downstream load,
- odlišný timing,
- nesprávne anonymizovanie.

Shadow request musí mať side effects zakázané alebo bezpečne izolované.

## 11. A/B testing

A/B test overuje produktovú hypotézu medzi kontrolnou a experimentálnou skupinou.

Nie je totožný s canary release:

- canary primárne riadi technické riziko,
- A/B test primárne meria produktový alebo behaviorálny výsledok.

A/B experiment potrebuje:

- hypotézu,
- primary metric,
- guardrail metrics,
- randomizáciu,
- sample-size plán,
- definovanú dĺžku,
- kontrolu novelty a seasonality effects.

## 12. Progressive delivery

Progressive delivery kombinuje:

- automatizovaný rollout,
- observability,
- policy,
- experimentálne skupiny,
- promotion/rollback rozhodnutia.

```text
artifact
→ small exposure
→ analysis
→ policy decision
→ wider exposure
```

Dôležité je analyzovať kvalitu signálu, nie iba automatizovať percentá rollout-u.

## 13. Production traffic replay

Zachytený alebo synteticky odvodený traffic možno replayovať v izolovanom prostredí.

Kontroluj:

- anonymizáciu,
- tokeny a secrets,
- časovú distribúciu,
- side effects,
- referential integrity,
- retention,
- súhlas a compliance.

Replay nie je presná produkcia, ale môže odhaliť realistickejší request mix než ručne vytvorený load test.

## 14. Resilience validation

Shift-right môže overovať:

- retry behavior,
- circuit breaker,
- failover,
- autoscaling,
- zone/region degradation,
- queue backlog recovery,
- dependency timeout,
- graceful degradation.

Takéto overenie musí mať experiment contract a safety controls. Tu sa shift-right prepája s chaos testingom.

## 15. Error budgets a release decisions

Error budget môže ovplyvniť rollout policy.

Príklad:

```text
budget healthy
→ povolený štandardný rollout

budget rýchlo klesá
→ menší canary, manuálny approval alebo freeze
```

Error budget nie je trest. Je to mechanizmus vyvažovania reliability a delivery velocity.

## 16. Feedback späť do vývoja

Shift-right bez učenia je iba monitoring.

Produkčný signal má viesť k:

- novému regression testu,
- spresneniu acceptance criteria,
- novému SLI,
- lepšiemu alertu,
- zlepšeniu runbooku,
- zmene timeoutu alebo retry policy,
- novému chaos experimentu,
- oprave platformového defaultu.

```text
production evidence
→ learning
→ backlog/change
→ shift-left control
```

## 17. Bezpečnosť experimentov

Pred produkčným experimentom definuj:

- hypothesis,
- steady-state metrics,
- blast radius,
- target cohort,
- duration,
- abort criteria,
- rollback,
- ownera,
- communication plan,
- evidence retention.

Nevykonávaj experiment iba preto, že tool ho technicky umožňuje.

## 18. Anti-patterny

### Testujeme až v produkcii

Chýbajú skoré kontroly a používateľ nesie náklady bežných chýb.

### Dashboard bez rozhodnutia

Metriky existujú, ale nikto nevie, čo má rollout zastaviť.

### Canary bez kontrolnej skupiny

Nie je jasné, či zmena metriky súvisí s novou verziou alebo s globálnou udalosťou.

### Feature flag bez lifecycle

Vzniká trvalý komplexný stav systému.

### Synthetics s produkčnými side effects

Test môže vytvárať reálnu finančnú alebo používateľskú škodu.

### Produkčný experiment bez abort criteria

Tím reaguje improvizovane až po probléme.

## 19. Metriky

Sleduj napríklad:

- post-deploy defect detection time,
- canary rollback rate,
- mean exposure before detection,
- synthetic success rate,
- real-user error rate,
- release-to-validation time,
- stale feature flags,
- percent rolloutov s automatickými criteria,
- false rollback rate,
- defect feedback converted to automated controls.

## 20. Rozhodovací rámec

1. Ktoré riziko nemožno dostatočne overiť pred produkciou?
2. Aký produkčný signal bude oracle?
3. Aká je kontrolná skupina alebo baseline?
4. Aký je maximálny blast radius?
5. Ako rýchlo vieme rollbacknúť alebo roll-forwardnúť?
6. Aké sú abort criteria?
7. Obsahuje experiment side effects alebo citlivé dáta?
8. Kto experiment sleduje a vlastní?
9. Ako sa výsledok premení na trvalé zlepšenie?
10. Ktorá kontrola sa po poznatku posunie doľava?

## 21. Kontrolné otázky

1. Čo znamená shift-right?
2. Prečo nenahrádza shift-left?
3. Aký je rozdiel medzi synthetic monitoring a RUM?
4. Aký je rozdiel medzi canary a A/B testom?
5. Načo slúži kontrolná skupina?
6. Aké riziká má shadow traffic?
7. Ako feature flags oddeľujú deployment od release?
8. Čo je progressive delivery?
9. Ako error budget ovplyvňuje rollout?
10. Ako sa produkčný poznatok vracia do pre-release kontrol?

## Glossary impact

Relevantné pojmy: shift-right, production validation, canary release, control group, feature flag, dark launch, shadow traffic, A/B testing, progressive delivery, Real User Monitoring, guardrail metric a abort criterion.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shift-left](shift-left.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Chaos testing →](chaos-testing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
