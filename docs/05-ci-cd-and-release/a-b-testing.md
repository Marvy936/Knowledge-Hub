# A/B testing

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

A/B testing porovnáva súbežné varianty na kontrolovane priradených skupinách a snaží sa odhadnúť kauzálny dopad treatmentu na vopred definovaný outcome. Traffic split vytvára dve skupiny; dôveryhodný experiment vzniká až vtedy, keď assignment, exposure, measurement a decision contract umožnia rozlíšiť treatment effect od biasu alebo chyby merania.

```text
kauzálna hypotéza
→ experiment contract a immutable treatment identity
→ eligibility a správna randomization unit
→ stabilný assignment
→ reálna exposure
→ outcome a guardrail observation
→ validity checks
→ effect a uncertainty
→ product decision
→ bezpečný rollout alebo removal
→ cleanup a learning
```

A/B test nie je deployment stratégia. Canary sa primárne pýta, či je release bezpečné rozširovať. A/B experiment sa pýta, či treatment spôsobil prakticky významný rozdiel pre definovanú populáciu.

## 1. Nosný model: cesta od assignmentu ku kauzálnemu tvrdeniu

Experiment chce porovnať dva hypotetické výsledky toho istého subjektu:

```text
outcome subjektu s controlom
versus
outcome toho istého subjektu s treatmentom
```

V realite možno pozorovať iba jeden z nich. Random assignment vytvára skupiny, ktoré majú byť pred treatmentom porovnateľné, takže rozdiel outcomes možno za splnených podmienok pripísať variantu.

Dôveryhodnosť sa môže zlomiť na viacerých hraniciach:

```text
population boundary
→ kto bol eligible

assignment boundary
→ kto bol priradený kam

exposure boundary
→ kto treatment skutočne dostal

measurement boundary
→ ako vznikol outcome

decision boundary
→ ako sa uncertainty zmenila na rozhodnutie
```

Pozitívny dashboard výsledok nemá hodnotu, ak assignment alebo measurement boundary nie sú platné.

## 2. Nosný scenár: Atlas Orders review panel

Atlas chce zistiť, či nový order-review panel znižuje počet nedokončených objednávok. Treatment zobrazuje zákazníkovi jasnejšie vysvetlenie risk kontroly a odporúčaný ďalší krok. Backend release je už prevádzkovo overený canary rolloutom; teraz sa testuje produktový účinok UI a workflowu.

Experiment `order-review-v3` má contract:

```text
population
→ oprávnení prihlásení používatelia vytvárajúci novú order

randomization unit
→ tenant, nie user

control A
→ pôvodný review panel

treatment B
→ nový panel s risk explanation

primary outcome
→ order completion do 24 hodín od prvej exposure

guardrails
→ duplicate orders, support contacts, authorization errors, p99 latency

minimum practical effect
→ vopred definované zlepšenie completion bez guardrail regresie

experiment horizon
→ minimálne celý pracovný týždeň plus dozretie 24-hodinových outcomes
```

Tenant je randomization unit, pretože členovia jedného tímu zdieľajú order a navzájom vidia jej stav. User-level randomizácia by miešala control a treatment v jednom collaboration workflowe.

## 3. Experiment subject musí byť immutable a vysvetliteľný

Výsledok patrí konkrétnej verzii experimentu:

```text
experiment key a version
+ treatment payload revision
+ eligibility revision
+ assignment salt
+ application/client versions
+ primary a guardrail metric definitions
+ attribution window
+ start/stop timestamps
```

Ak Atlas počas experimentu zmení wording, layout alebo eligibility, nevzniká „malá úprava“. Mení sa treatment alebo population a musí vzniknúť nová experiment version alebo explicitná fáza.

Bez identity možno v jednej analýze zmiešať používateľov, ktorí dostali odlišný treatment, a výsledok už nereprezentuje jednu kauzálnu otázku.

## 4. Hypotéza určuje, čo sa bude merať

Atlas hypotéza znie:

> Pre oprávnené tenants nový review panel zvýši 24-hodinovú order completion o prakticky významnú hodnotu bez nárastu duplicate orders, support contacts, authorization errors alebo latency.

Obsahuje:

- populáciu;
- treatment;
- mechanizmus;
- primary outcome;
- časový horizont;
- prakticky významný efekt;
- safety guardrails.

Secondary metrics môžu testovať mechanizmus, napríklad kliknutie na vysvetlenie alebo čas do ďalšieho kroku. Nesmú sa po výsledku svojvoľne povýšiť na primary metric len preto, že vyšli priaznivo.

## 5. Eligibility predchádza assignmentu

Atlas najprv určí, či tenant môže vstúpiť do experimentu:

```text
supported client version
+ relevant workflow
+ povolená jurisdikcia
+ žiadny opt-out
+ žiadny konfliktujúci experiment
→ eligible
```

Až potom stabilne priradí tenant do variantu:

```text
bucket = hash(experiment_version + tenant_id + salt) mod N
```

Poradie chráni sample ratio. Ak by sa niektoré eligibility pravidlo aplikovalo až po assignment-e iba v treatment path-e, jedna skupina by stratila viac subjektov a randomizácia by sa narušila.

## 6. Assignment a exposure sú odlišné udalosti

Assignment znamená, že tenant patrí do B. Exposure znamená, že konkrétny používateľ treatment skutočne videl v relevantnom workflowe.

Exposure event obsahuje:

```text
experiment/version
variant
privacy-safe tenant key
application/client version
treatment payload revision
workflow a request correlation
timestamp
```

Primárna intention-to-treat analýza zahŕňa všetkých assigned tenants a zachováva randomizáciu. Exposed-only analýza môže vysvetliť mechanizmus, ale môže byť biased: treatment sám môže ovplyvniť, či sa používateľ dostane na obrazovku, ktorá exposure zaznamená.

## 7. Metric contract zabraňuje tomu, aby rovnaký názov znamenal iné číslo

`order_completion_24h` presne definuje:

```text
numerator
→ orders dokončené do 24 h od prvej validnej exposure

denominator
→ eligible assigned orders s dozretým 24-hodinovým oknom

deduplication
→ logical order ID a idempotency key

late events
→ spracované podľa versionovaného watermark pravidla

attribution
→ k variantu tenant assignmentu pri začiatku order journey

internal/bot traffic
→ vylúčený
```

Dashboard, ktorý používa „completion v kalendárny deň“, môže ukázať iný výsledok než experiment query. Metric definition a query revision sú súčasťou evidence.

## 8. Validity checks majú prednosť pred effect estimation

Atlas interpretuje primary outcome až po tomto poradí:

```text
1. experiment subject a treatment identity
2. eligibility a assignment integrity
3. Sample Ratio Mismatch
4. assignment → exposure funnel
5. metric pipeline a query health
6. population a segment comparability
7. concurrent experiment interference
8. sample maturity a delayed outcomes
9. guardrail safety
10. effect estimate a practical significance
```

Ak experiment očakáva 50/50 a pozoruje výrazne iný pomer, vznikol integrity incident. Možné mechanizmy zahŕňajú assignment bug, treatment-specific crash, exposure logging loss, client incompatibility alebo eligibility aplikovanú asymetricky.

Výsledok sa nesmie „opraviť“ váhovaním bez pochopenia príčiny.

## 9. Sample a stopping contract chránia pred náhodným víťazom

Pred spustením Atlas určí:

- baseline completion a variance;
- minimálny prakticky významný efekt;
- potrebnú sample size alebo decision rule;
- maximum duration;
- 24-hodinové dozretie outcome;
- planned segment analyses;
- fixed-horizon alebo validný sequential design.

Priebežné pozeranie a ukončenie pri prvom priaznivom výsledku mení false-positive behavior. Safety guardrail môže experiment okamžite zastaviť, ale product-win decision musí rešpektovať analytický plán.

Štatisticky rozlíšiteľný, ale zanedbateľný efekt nemusí odôvodniť rollout, support cost ani permanentnú komplexitu.

## 10. Interference určuje správnu randomization unit

Pri Atlas Orders sa členovia jedného tenanta ovplyvňujú:

```text
user A začne order s treatmentom
→ user B ju otvorí cez control
→ obaja vidia a menia ten istý shared workflow
```

User-level assignment by porušil jednoduchý predpoklad izolovaných treatmentov. Tenant-level assignment zachováva konzistentný workflow, hoci znižuje počet nezávislých jednotiek a mení sample výpočet.

Pri marketplace, social graph alebo regionálnom systéme môže byť potrebná cluster randomizácia, geo experiment alebo switchback. Randomization unit sa vyberá podľa hranice treatment účinku, nie podľa najľahšie dostupného ID.

## 11. Worked failure: treatment-specific client crash vytvoril falošné SRM

Po spustení experimentu Atlas očakával 50/50 assigned tenants, ale exposure events ukazovali 50/43.

```text
assignment 50/50 je správny
→ treatment payload obsahuje pole nepodporované starším klientom
→ klient B spadne pred exposure eventom
→ treatment má menej exposures aj outcomes
→ exposed-only dashboard ukazuje vysokú completion medzi preživšími
→ treatment vyzerá ako víťaz
```

### Príčina

Assignment bol zdravý, ale treatment-specific crash prerušil exposure a measurement funnel. Exposed-only population stratila najviac postihnutých používateľov, takže výpočet porovnával selektovanú skupinu.

### Dôsledok

Pozitívny effect estimate bol neplatný. Experiment sa klasifikoval ako invalid, nie ako inconclusive product result.

### Trvalá náprava

```text
assignment count oddelený od exposure count
→ crash telemetry podľa experiment version a variantu
→ client capability v eligibility
→ A/A a payload-compatibility fixture
→ intention-to-treat ako primary analysis
```

## 12. Worked failure: user-level randomizácia skryla tenant interference

Prvá verzia experimentu randomizovala jednotlivých používateľov. V treatment skupine rástla completion, ale support hlásil nekonzistentné workflowy.

```text
user A dostane nový panel
→ upraví order podľa treatment guidance
→ user B z rovnakého tenanta otvorí starý panel
→ control UI nepozná nový intermediate state
→ user B vytvorí paralelnú order alebo kontaktuje support
→ tenant outcome ovplyvnia oba varianty
```

### Príčina

Randomization unit bola užšia než hranica treatment účinku. Control a treatment si navzájom kontaminovali outcomes cez shared tenant state.

### Náprava

Atlas ukončil experiment ako invalid, prešiel na tenant-level assignment, pridal tenant-consistency invariant a prepočítal sample plán s cluster efektom.

## 13. Kauzálny diagnostický walkthrough

Symptom: treatment ukazuje vyššiu completion, ale zároveň vznikol Sample Ratio Mismatch a nižší exposure rate.

### Krok 1 — stabilizuj subject

```text
experiment order-review-v3 version 2
payload B17
eligibility E9
assignment salt S4
metric query Q12
client versions 8.2–8.5
```

Bez tejto identity by sa mohli miešať staršie payloads alebo eligibility rules.

### Krok 2 — formuluj konkurenčné hypotézy

```text
H1: treatment naozaj zvyšuje completion
H2: assignment systém priraďuje menej subjektov do B
H3: B spôsobuje crash alebo nedokončenú exposure telemetry
H4: outcome query asymetricky zahŕňa varianty
H5: populácie sa líšia pre eligibility alebo concurrent experiment
```

### Krok 3 — vyber diskriminačné observation points

- raw assignment ledger testuje H2;
- assignment → app start → exposure → outcome funnel podľa variantu testuje H3;
- query execution, numerator/denominator a dedup audit testujú H4;
- eligibility a population distributions testujú H5;
- treatment effect možno interpretovať až po odmietnutí H2–H5.

Atlas zistí, že assignment ledger je presne 50/50, rozdiel vzniká medzi app startom a exposure iba na client 8.2 a crash signature patrí B payloadu. H3 vysvetľuje SRM.

### Krok 4 — containment a verdict

Treatment exposure sa zastaví pre nepodporovaný client. Experiment sa označí `INVALID`, nie `B WINS`. Výsledky sa nepoužijú na product decision.

### Krok 5 — over opravu

Po capability gate a novej experiment version Atlas najprv spustí A/A/instrumentation check. Pokračuje až keď assignment, exposure a crash funnel nemajú variant-specific rozdiel.

### Krok 6 — zachovaj learning

Incident vytvorí payload compatibility test, experiment-platform guardrail na assignment/exposure divergence a povinnú client-capability eligibility kontrolu.

## 14. Decision record oddeľuje evidence od product voľby

Možné výsledky:

- ship treatment;
- keep control;
- iterate a spustiť nový experiment;
- inconclusive pre nedostatočnú sample alebo uncertainty;
- invalid pre porušenú experiment integrity;
- stop for harm;
- no practical benefit napriek štatistickému rozdielu.

Víťazný treatment sa neaktivuje automaticky na 100 %. Nasleduje reliability/capacity review, progressive rollout, support readiness a post-promotion observation. Experiment na čiastočnej populácii nemusí dokazovať správanie pri plnej záťaži.

## 15. Cleanup uzatvára experiment lifecycle

Po rozhodnutí Atlas:

```text
nastaví finálny behavior
→ bezpečne rolloutne alebo odstráni treatment
→ odstráni assignment a exposure logiku
→ odstráni obsolete code path a flag
→ archivuje contract, queries, evidence a decision
→ aplikuje privacy retention
```

Experiment bez expiry a cleanupu sa zmení na permanentný, slabo zdokumentovaný branch.

## 16. Diagnostický runbook

1. Potvrď experiment version, treatment payload, eligibility a metric query.
2. Over raw assignment counts pred exposure filteringom.
3. Testuj Sample Ratio Mismatch a lokalizuj prvý divergence point vo funnel-e.
4. Porovnaj assignment, app/runtime health, exposure a outcome podľa variantu.
5. Validuj metric contract, deduplication, attribution a query execution.
6. Skontroluj population mix, randomization unit a concurrent interference.
7. Over sample maturity, stopping rule a delayed outcomes.
8. Rozlíš planned segment analysis od post hoc data mining.
9. Skontroluj guardrails, privacy a operational incidents.
10. Klasifikuj experiment ako valid, inconclusive alebo invalid pred product decisionom.

## 17. Referenčné pravidlá

- A/B test odhaduje kauzálny treatment effect; nie je to obyčajný traffic split.
- Experiment subject zahŕňa treatment, eligibility, assignment a metric revisions.
- Randomization unit zodpovedá hranici treatment účinku.
- Eligibility predchádza assignmentu.
- Assignment a exposure sú samostatné observation points.
- Primary metric a attribution sú versionované pred spustením.
- Validity checks majú prednosť pred effect estimate.
- Sample Ratio Mismatch je integrity incident.
- Safety abort a product-win stopping používajú odlišnú logiku.
- Štatistická významnosť nenahrádza praktickú hodnotu, guardrails ani etiku.
- Víťazný variant stále potrebuje bezpečný rollout a cleanup.

## 18. Časté omyly

### „B má vyššie číslo, takže vyhralo“

Najprv treba overiť assignment, exposure, metric pipeline a sample maturity.

### „Randomizujeme users, lebo máme user ID“

Shared tenant alebo network effect môže vyžadovať širšiu unit.

### „Exposed-only je vždy presnejšie“

Exposure môže byť treatment-dependent a vytvoriť selection bias.

### „SRM stačí opraviť váhou“

Bez root cause môže SRM signalizovať crash, logging loss alebo asymetrickú eligibility.

### „Experiment skončil, flag môže zostať“

Bez removal-u vzniká flag, code a analytický debt.

## 19. Zhrnutie

Atlas A/B lifecycle je:

```text
kauzálna hypotéza
→ immutable experiment contract
→ eligibility + správna randomization unit
→ stabilný assignment
→ exposure a metric provenance
→ integrity a maturity checks
→ effect + uncertainty + practical significance
→ product decision
→ progressive rollout alebo removal
→ cleanup
```

Experiment je dôveryhodný iba vtedy, keď vie vysvetliť celý chain od eligible population po outcome. Pozitívny výsledok pri neplatnom assignment, exposure alebo measurement systéme nie je slabý dôkaz; nie je to dôkaz o treatment efekte.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Canary deployment](canary-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Shadow deployment →](shadow-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
