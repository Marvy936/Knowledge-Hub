# Recreate deployment

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Recreate deployment používa jeden exkluzívny runtime slot. Stará generácia musí slot úplne opustiť skôr, než ho prevezme nová. Stratégia tým odstraňuje mixed-version obdobie, ale zámerne vytvára capacity gap, počas ktorého systém neposkytuje plnú službu.

```text
old active
→ maintenance a zastavenie nového worku
→ drain a potvrdenie nulového writer ownershipu
→ old stopped
→ migration a deployment
→ new functional readiness
→ riadené obnovenie trafficu/worku
→ observation a recovery closure
```

Bezpečnosť recreate preto nezávisí od toho, či platforma vie „vymeniť container“. Závisí od downtime contractu, explicitného ownershipu mutable state-u a schopnosti rozhodnúť sa počas nulovej application capacity medzi pokračovaním, rollbackom a roll-forwardom.

## 1. Nosný model: exkluzívny slot a outage budget

Recreate má tri zásadné stavy:

```text
slot = old
→ slot = empty/maintenance
→ slot = new
```

V stave `empty/maintenance` neexistuje stará fallback capacity. Každá ďalšia minúta diagnostiky preto spotrebúva businessovo dohodnutý outage budget.

Celkový outage nie je iba startup time:

```text
total outage
= routing withdrawal
+ request a worker drain
+ old shutdown
+ migration
+ artifact/config activation
+ startup
+ functional readiness
+ traffic restoration
+ prvé potvrdenie business recovery
```

Z toho vyplýva hlavný trade-off:

```text
nižšia orchestration a mixed-version zložitosť
za cenu úplného cutover blast radiusu a časovo kritickej recovery
```

## 2. Nosný scenár: Atlas Orders reconciliation 3.11.0

Atlas Orders používa regionálny reconciliation worker, ktorý uzatvára objednávky a zapisuje účtovné výsledky. V každom regióne smie existovať iba jeden aktívny writer, pretože vlastní leader lease a spracúva partition, ktorú nemožno bezpečne rozdeliť medzi dve nekompatibilné generácie.

Release manifest `M2` obsahuje:

```text
worker artifact digest D_worker
migration bundle D_migration
rendered config C17
leader protocol revision L3
previous release manifest M_prev
```

Business akceptuje sedemminútové maintenance window. Deployment plan je:

```text
00:00 maintenance a stop intake
00:45 queue intake potvrdený ako paused
01:30 active work drained a checkpointovaný
02:00 old worker fenced a stopped
02:15 migration apply
03:30 new worker start
04:30 functional readiness
05:00 bounded queue resume
06:30 reconciliation invariants healthy
07:00 maintenance close
```

Každá fáza má hard timeout a failure action. Ak sa old writer nepodarí bezpečne zastaviť do `02:00`, deployment sa nezačne. Ak migration skončí s neznámym outcome, nový worker sa nespustí, kým sa stav nereconciliuje.

## 3. Preconditions určujú, či je slot bezpečné vyprázdniť

Pred zapnutím maintenance Atlas overí:

```text
release identity M2 je immutable
→ M_prev, jeho config a bytes sú dostupné
→ migration bola testovaná na reprezentatívnom objeme
→ maintenance a recovery control path nebežia v nasadzovanej službe
→ queue pause, leader fencing a checkpoint sú funkčné
→ observability a business synthetic sú dostupné
→ dependency health a quotas sú v baseline
```

Tieto checks nie sú administratívny checklist. Každý chráni konkrétnu hranicu:

- dostupný `M_prev` chráni binary recovery;
- schema compatibility chráni data recovery;
- nezávislý maintenance endpoint chráni control plane počas outage-u;
- fencing chráni pred dvoma writermi;
- functional synthetic chráni pred false readiness;
- dependency baseline umožňuje odlíšiť release chybu od externého incidentu.

Ak niektorá precondition chýba, najbezpečnejšie rozhodnutie je nevyprázdniť slot.

## 4. Maintenance musí zastaviť work, nie iba používateľský HTTP traffic

Atlas najprv zablokuje nové mutácie a poskytne retry guidance. Potom zastaví všetky zdroje worku:

```text
HTTP commands
queue intake
scheduled reconciliation
webhooks
administratívne mutations
retry workers
```

Poradie je dôležité. Ak sa zastaví iba ingress, queue consumer môže ďalej meniť databázu počas migration. Ak sa consumer vypne bez checkpointu, neacknowledged položky sa po štarte vrátia a môžu zopakovať side effect.

Dôkazom write freeze nie je „maintenance page je zapnutá“, ale:

```text
new command rate = 0
queue ownership odovzdaný alebo paused
active transactions = 0 alebo bounded
leader lease starej generácie revoked
last processed offset/checkpoint uložený
```

## 5. Drain a fencing vytvárajú hranicu medzi old a empty stavom

Bezpečný shutdown má dve samostatné úlohy:

```text
drain
→ dokonči alebo bezpečne odlož existujúcu prácu

fencing
→ zabráň starej generácii znovu mutovať state
```

Atlas najprv prestane prijímať work, checkpointuje in-flight položky a flushne telemetry. Následne revokuje leader lease a vydá novú fencing generation. Nový worker prijme ownership iba s novšou generation.

Samotné ukončenie procesu fencing nenahrádza. Starý proces môže zostať izolovaný od control plane, no stále mať sieťový prístup k databáze. Fencing token je posledná ochrana pred split-brain zápisom.

## 6. Migration je samostatný state transition

Po potvrdení `old stopped` pipeline vykoná migration bundle `D_migration`.

```text
pre-migration state S0
→ apply step 1
→ checkpoint M1
→ apply step 2
→ postconditions
→ migration state S1
```

Každý krok musí mať:

- idempotency alebo rozpoznanie už vykonaného stavu;
- jednoznačný checkpoint;
- timeout klasifikovaný ako known failure alebo unknown outcome;
- postcondition nad schema aj dátovým invariantom;
- rollback alebo roll-forward pravidlo.

Timeout po commitnutí kroku nie je dôkaz, že sa krok nevykonal. Blind retry môže zmeniť či poškodiť state. Pipeline najprv načíta migration history, schema a invariants a až potom rozhodne o pokračovaní.

## 7. Process health nie je functional readiness

Nový worker prejde viacerými observation points:

```text
process started
→ config a secret references loaded
→ schema revision accepted
→ database a queue connectivity
→ leader ownership acquired
→ synthetic item spracovaný presne raz
→ reconciliation invariant potvrdený
```

Port, PID alebo liveness dokazujú iba existenciu procesu. Atlas považuje worker za ready až vtedy, keď spracuje kontrolnú položku, zapíše očakávaný outcome a nevytvorí duplicitný side effect.

Readiness failure má pevný decision deadline. Po jeho prekročení sa tím nerozhoduje podľa pocitu, ale podľa state compatibility:

- migration nezmenila nekompatibilne state: rollback na `M_prev`;
- migration je nevratná, ale stav je konzistentný: roll-forward fix;
- stav je neznámy: pokračuje containment a reconciliation, nie traffic restore.

## 8. Traffic a work sa obnovujú riadene

Aj recreate môže obnoviť záťaž postupne:

```text
internal synthetic
→ queue resume na 10 % rate limitu
→ 25 % bežného intake
→ 100 % intake
→ delayed reconciliation watch
```

Tým sa obmedzí thundering herd. Po outage-e sa totiž súčasne môžu:

- otvoriť všetky connection pools;
- vyprázdňovať retry backlog;
- zahrievať caches;
- pripájať clients;
- obnovovať schedulers;
- zvyšovať downstream request rate.

Počet healthy instances preto nie je jediný capacity signal. Atlas sleduje DB connection pressure, queue age, retry rate a completion latency počas každého restore kroku.

## 9. Worked failure: maintenance zastavila API, nie queue writerov

Pri predchádzajúcom release Atlas zapol maintenance na HTTP ingress-e, ale zabudol zastaviť retry consumer.

```text
HTTP writes = 0
→ retry consumer ďalej aktualizuje order rows
→ offline migration prepisuje rovnaký status stĺpec
→ niektoré rows dostanú nový format, iné starý
→ migration postcondition zlyhá
→ old worker už je vypnutý a outage pokračuje
```

### Príčina

Tím zamieňal používateľský traffic za všetok work intake. Recreate model nemal explicitný writer inventory ani dôkaz nulového mutation rate.

### Dôsledok

Rollback binary nepomohol, pretože databáza už obsahovala mixed data state. Recovery musela zostať v maintenance, zastaviť consumer, klasifikovať rows podľa migration checkpointu a roll-forwardnúť normalizačný krok.

### Trvalá náprava

```text
writer inventory v release manifeste
→ machine-readable pause acknowledgements
→ database mutation-rate guard
→ fencing pre všetkých worker owners
→ migration precondition: writer_count = 0
→ postcondition a reconciliation fixture v preprodukcii
```

## 10. Worked failure: proces bol green, ale obnovenie worku saturovalo databázu

Nový worker prešiel liveness aj jednoduchý queue ping. Pipeline preto otvorila celý backlog naraz.

```text
new worker started
→ všetky pools otvorené súčasne
→ retry backlog sa okamžite rozbehol
→ DB connections dosiahli limit
→ ack latency vzrástla
→ visibility timeout vrátil položky do queue
→ duplicate attempts znásobili load
```

Proces zostal green, no business completion klesala a backlog rástol.

### Príčina

Readiness neoverovala kritický write path pod bounded loadom a traffic restoration nemala rate state machine. Health endpoint neposkytoval dôkaz o dependency headroome ani idempotency behavior-e pri retry.

### Recovery

Atlas znovu zapol maintenance pre work intake, nezastavil však healthy nový worker. Znížil concurrency, predĺžil visibility timeout, postupne drainoval backlog a overil invariant `jeden settlement outcome na order`.

## 11. Kauzálny diagnostický walkthrough

Symptom: po obnovení worku rastie queue age a completion rate klesá, pričom procesy sú healthy.

### Krok 1 — stabilizuj skúmaný subject

Najprv potvrď:

```text
release manifest M2
config C17
migration state S1
restore step = 100 % intake
worker generation = new only
```

Bez toho by sa mohli miešať metrics starej generácie, iného configu alebo skoršieho restore kroku.

### Krok 2 — vytvor konkurenčné hypotézy

```text
H1: nový code path je pomalší
H2: databáza alebo broker má nezávislý incident
H3: restore burst prekročil capacity, hoci steady-state code je správny
H4: duplicate retries vytvárajú self-amplifying load
```

### Krok 3 — vyber observation points, ktoré hypotézy rozlíšia

- baseline dependency health pred deploymentom testuje H2;
- requests/work per worker a DB connections testujú H3;
- attempt count na logical item a visibility timeout testujú H4;
- latency jedného bounded synthetic itemu bez backlogu testuje H1.

Atlas zistí, že bounded synthetic je normálny, externé DB signály mimo Orders sú zdravé, ale connection count a duplicate attempts rastú presne po `100 % intake` transitione. H3 a H4 vysvetľujú symptom lepšie než H1 alebo H2.

### Krok 4 — zastav mechanizmus, nie iba alarm

Zníženie intake zastaví nový burst. Predĺženie visibility timeoutu a idempotency guard zabránia opätovnému zaradeniu položiek. Samotný restart workerov by znovu otvoril pools a problém zosilnil.

### Krok 5 — over recovery na pôvodnom outcome

Recovery je potvrdená až keď:

```text
queue age klesá
DB connections sú pod headroom limitom
duplicate attempts sa nezvyšujú
business completion sa vráti k baseline
data invariant zostáva zachovaný
```

### Krok 6 — vráť learning do skoršej vrstvy

Failure sa mení na:

- functional readiness test s bounded write loadom;
- rate-controlled restore contract;
- queue visibility a retry-amplification guardrail;
- pre-release capacity test nad reprezentatívnym backlogom.

## 12. Rollback a roll-forward sú rozhodnutia nad current state

Rollback na `M_prev` je eligible iba ak:

```text
M_prev bytes a config existujú
+ starý worker rozumie schema S1
+ nové rows a events sú čitateľné
+ leader ownership možno bezpečne vrátiť
+ post-rollback invariant test existuje
```

Ak migration alebo external side effects tieto podmienky porušili, bezpečnejší je roll-forward, feature disable, work freeze alebo data reconciliation.

„Máme starý image“ nie je recovery capability.

## 13. Diagnostický runbook

Po vysvetlení modelu možno použiť krátky runbook:

1. Urči aktuálny recreate state a zostávajúci outage budget.
2. Potvrď release, config, migration, writer a environment identity.
3. Porovnaj skutočný čas jednotlivých fáz s hard timeoutmi.
4. Over nulový nový work, in-flight drain a fencing starej generácie.
5. Pri migration chybe urč checkpoint, partial state a postconditions.
6. Pri readiness chybe odlíš process health od kritického outcome-u.
7. Pri restore regresii segmentuj startup, dependency burst, retries a business completion.
8. Rozhodni rollback alebo roll-forward podľa data a side-effect compatibility.
9. Po recovery over business aj data invariants.
10. Preveď root cause na precondition, test alebo guardrail.

## 14. Referenčné pravidlá

- Recreate používa jeden exkluzívny runtime slot.
- Downtime je explicitný contract a rozkladá sa na merateľné fázy.
- Maintenance musí zastaviť všetky writers a work intake, nie iba ingress.
- Drain chráni in-flight prácu; fencing chráni pred návratom starého ownera.
- Migration timeout môže znamenať unknown outcome, nie nevykonanie.
- Functional readiness dokazuje kritický outcome, nie iba process health.
- Traffic a queue restore majú vlastnú bounded state machine.
- Rollback eligibility zahŕňa artifact, config, schema, events a external side effects.
- Recovery sa overuje business a data invariantmi.
- Diagnostika postupuje od identity a state-u cez hypotézy k diskriminačným observation points.

## 15. Časté omyly

### „Recreate je jednoduchý stop a start“

Jednoduchší orchestration neodstraňuje write freeze, migration ani recovery state.

### „Maintenance page znamená, že systém je read-only“

Consumers, cron a webhooks môžu ďalej zapisovať.

### „Proces je healthy, môžeme otvoriť traffic“

Health nepreukazuje kritický write path, dependency headroom ani business outcome.

### „Rollback znamená spustiť starý artifact“

Stará verzia musí byť kompatibilná s aktuálnym mutable state-om.

### „Po obnovení môžeme pustiť celý backlog“

Cold pools, retries a queue redelivery môžu vytvoriť thundering herd.

## 16. Zhrnutie

Atlas recreate lifecycle je:

```text
immutable release a downtime contract
→ maintenance a úplný writer inventory
→ drain + checkpoint + fencing
→ old generation stopped
→ migration s reconciliovateľnými checkpointmi
→ functional readiness novej generácie
→ bounded work restoration
→ business/data observation
→ rollback alebo roll-forward podľa current state
```

Recreate je správna stratégia tam, kde je prijateľný outage a hodnotnejšie je odstrániť mixed-version obdobie. Je bezpečná iba vtedy, keď prázdny runtime slot nie je neznámy stav, ale presne riadená a časovo ohraničená fáza release state machine.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Release management](release-management.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Rolling update →](rolling-update.md)
<!-- KNOWLEDGE-NAVIGATION:END -->