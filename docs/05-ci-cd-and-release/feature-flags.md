# Feature flags

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Feature flag je versionovaný runtime control, ktorý oddeľuje nasadenie kódu od aktivácie konkrétneho behavioru. Aplikácia obsahuje viac ciest a distribuovaný evaluation systém rozhoduje, ktorú cestu použije konkrétny request, tenant, device alebo workload.

```text
flag contract
→ obidve code paths so safe defaultom
→ versionovaný publish
→ distribúcia a local snapshot
→ context + precedence evaluation
→ behavior a exposure
→ observation a runtime change
→ final default
→ obsolete path a flag cleanup
```

Flag nie je boolean uložený mimo kódu. Je to privilegovaný distribuovaný control plane s vlastnou consistency, security, failure a lifecycle semantics.

## 1. Nosný model: distribuované rozhodnutie nad versionovaným contextom

Jedno runtime rozhodnutie vzniká z:

```text
application version
+ flag key a configuration revision
+ evaluation context
+ rule precedence
+ local/remote snapshot state
+ SDK semantics
→ resolved variant a evaluation reason
```

Dve instances môžu krátko vyhodnotiť iný výsledok, ak používajú odlišnú config revision, stale cache alebo SDK schema. Incident preto nemožno rekonštruovať iba z hodnoty `true`; treba poznať celý evaluation subject.

Flag platforma má dve roviny:

```text
control plane
→ authoring, approval, versioning, publish, audit

data plane
→ distribution, cache, evaluation, behavior, exposure telemetry
```

Control-plane outage, distribučný lag a data-plane evaluation failure sú odlišné mechanizmy.

## 2. Nosný scenár: Atlas `risk-decision-v2`

Atlas Orders nasadil nový risk engine path, ale chce ho aktivovať postupne. Release flag `risk-decision-v2` má contract:

```text
owner = Orders team
purpose = oddeliť deploy M2 od runtime exposure
variants = old | new
code default = old
remote default = old
targeting = ring + tenant eligibility
expiry = po final rollout a rollback windowe
success = technical + functional + business guardrails
cleanup = odstrániť old path a evaluation
```

Evaluation precedence:

```text
emergency kill override
→ explicit tenant containment
→ ring rule
→ percentage rollout
→ remote default
→ code default
```

Každý result zaznamená config revision, matched rule, application version, ring, tenant key a cache age.

## 3. Typ flagu určuje lifecycle a failure default

Atlas rozlišuje:

- release flag — dočasný deploy/release separation;
- experiment flag — stabilný control/treatment assignment;
- operational flag — kill switch alebo runtime tuning;
- migration flag — riadi read/write či dependency fázu;
- entitlement — dlhodobý business contract;
- UI discovery flag — môže skryť capability, ale nenahrádza authorization.

Rovnaké `true/false` rozhranie neznamená rovnaký risk. Kill switch môže potrebovať rýchly lokálny safe snapshot. Entitlement alebo security-sensitive behavior používa konzervatívny default a autoritatívny server-side enforcement.

## 4. Flag contract predchádza implementácii

Každý flag definuje:

```text
key a type
owner a expiry
variants a payload schema
allowed environments
targeting context
code default a remote default
outage/staleness behavior
approval policy
telemetry a guardrails
final intended state
rollback window a cleanup order
```

Bez contractu vzniká anonymná mutable production config. Nikto nevie, či `false` znamená bezpečný default, kill state, neaktívny experiment alebo starý migration phase.

## 5. Publish je immutable revision, nie edit živej hodnoty

Atlas zmenu publikuje ako revision `F22`:

```text
previous F21
→ validácia schema a invariants
→ approval podľa risku
→ CAS publish expected F21, new F22
→ signed/versioned distribution
→ propagation observation
```

Compare-and-swap zabraňuje lost update pri dvoch súbežných edits. Multi-flag invariant sa publikuje v jednej transaction revision alebo cez compatible dvojfázový transition.

Emergency override má ownera, reason, expiry a explicitný návratový stav. Inak sa dočasná incidentná zmena stane neviditeľným permanentným defaultom.

## 6. Distribution je postupný state transition

Pri local evaluation SDK sťahuje config a rozhoduje bez network callu per request. Výhodou je nízka latency; cenou je dočasná staleness.

Atlas sleduje:

```text
publish revision F22
→ control plane accepted
→ distribution stream
→ SDK received
→ SDK validated
→ local snapshot activated
→ evaluation F22
```

Observation points:

- percent instances/clients na F22;
- propagation lag;
- stale cache age;
- out-of-order alebo rejected update;
- reconnect behavior;
- startup bez snapshotu;
- SDK payload compatibility.

Remote evaluation môže centralizovať rules, ale pridáva runtime dependency a latency. Hybrid používa local snapshot s definovaným maximum staleness.

## 7. Evaluation context a precedence musia byť vysvetliteľné

Context môže obsahovať tenant ID, ring, region, client version, entitlement alebo capability. Používa sa iba minimálny privacy-safe set potrebný na rozhodnutie.

Atlas percentage assignment:

```text
bucket = hash(flag_key + flag_version + tenant_id + salt) mod N
```

Stabilný tenant key chráni celý Orders workflow pred variant hoppingom. Rule engine vráti:

```text
variant = new
reason = ring-2-percentage
matched rule = R7
config revision = F22
```

Ak services používajú inú precedence alebo subject identity, rovnaký tenant môže dostať new API path a old worker path. Debug telemetry preto nesie resolved reason, nie iba final value.

## 8. Failure defaults sú súčasť behavior contractu

Pre `risk-decision-v2` Atlas definuje správanie pri:

- chýbajúcej config;
- timeout-e alebo control-plane outage;
- stale cache;
- invalid payload;
- neznámom variante;
- startup bez snapshotu;
- SDK schema mismatch.

Release flag má safe code default `old`. Operational kill switch však potrebuje posledný dôveryhodný disabled snapshot aj pri výpadku control plane. Entitlement fail-open by mohol neoprávnene sprístupniť capability; security authorization sa preto vôbec nespolieha iba na flag.

## 9. Feature flag nepredstavuje authorization boundary

Client-side config je používateľovi viditeľná a manipulovateľná. Aj server-side flag môže byť obídený iným endpointom alebo starším clientom.

Atlas oddeľuje:

```text
flag
→ či sa nový workflow zobrazí alebo použije

authorization policy
→ či identity smie vykonať resource operation

entitlement source
→ či má zákazník business nárok
```

Server overí authorization nezávisle od variantu. Flag payload neobsahuje secrets.

## 10. Multi-flag dependencies rozširujú stavový priestor

Atlas pôvodne používal:

```text
new-risk-api
new-risk-worker
new-risk-ui
```

Invariant:

```text
new-risk-ui requires new-risk-api
new-risk-worker requires schema S_expand
```

Samostatné updates môžu vytvoriť neplatný medzistav. Preto Atlas používa release manifest alebo atomic revision a application-side invariant validation.

Hlboké dependency trees sú zle troubleshootovateľné. Flag dependency musí byť explicitná, acyklická, testovaná a mať cleanup order.

## 11. Migration flag riadi fázu, nevytvára kompatibilitu

Migration flow môže byť:

```text
read old
→ shadow read new
→ dual write
→ verify/reconcile
→ read new
→ stop old write
→ contract old state
```

Flag prepína fázu, ale old/new readers, writers a data formats musia byť kompatibilné počas overlapu. Disable flagu po nekompatibilných writes nevráti database state.

Release a migration flags sa preto viažu na schema phase a rollback eligibility, nie iba na application version.

## 12. Kill switch musí ovládať celý failure path

Atlas kill switch pre Risk v2 má zastaviť:

```text
nové API evaluation
new worker consumption
external risk commands
new event publication
```

Ak jeden code path flag nevyhodnocuje alebo používa stale snapshot, `off` v control plane nemusí znamenať containment.

Kill switch potrebuje:

- low-latency distribúciu;
- nezávislosť od failure domainu feature;
- auditované oprávnenia;
- test freshness;
- explicitné side-effect boundaries;
- degraded-control-plane behavior;
- telemetry potvrdzujúcu skutočný effective off state.

## 13. Worked failure: kill switch vypol API, ale worker pokračoval

Risk v2 začal vytvárať duplicate review events. On-call prepol flag na `old`.

```text
API instances prijmú F23 a vrátia sa na old path
→ worker fleet používa 20-minútový polling interval a stale F22
→ worker ďalej spracúva new-risk queue
→ duplicate events a notifications pokračujú
→ control plane ukazuje flag off
```

### Príčina

Tím zamieňal desired config s effective runtime state-om. Kill switch nemal propagation SLO, per-component effective-state telemetry ani external producer stop.

### Dôsledok

Containment bol iba čiastočný. Už vzniknuté side effects vyžadovali queue pause, fencing workerov a reconciliation.

### Trvalá náprava

```text
component-level effective revision telemetry
→ push distribution pre operational flags
→ maximum stale age
→ worker hard-stop override mimo feature pathu
→ kill-switch game day
→ containment verdict až po potvrdení všetkých evaluators
```

## 14. Worked failure: neatomická multi-flag zmena vytvorila invalid combination

Pipeline najprv zapla `new-risk-ui`, potom o niekoľko sekúnd `new-risk-api`.

```text
clients dostanú nový UI flow
→ API ešte používa old response contract
→ UI odošle field, ktoré old API odmietne
→ order completion klesne
→ o chvíľu sa API flag zapne a symptom zmizne
→ aggregate dashboard incident takmer skryje
```

### Príčina

Dva flags tvorili jeden runtime invariant, ale boli publikované ako nezávislé mutable updates. Nebola transakčná revision ani application-side prerequisite enforcement.

### Náprava

Atlas zaviedol atomic config bundle, explicitný prerequisite a transition test všetkých intermediate states.

## 15. Kauzálny diagnostický walkthrough

Symptom: po zapnutí Risk v2 časť tenantov používa new path a časť old, hoci target je 100 %.

### Krok 1 — stabilizuj evaluation subject

```text
application M2
flag risk-decision-v2
published revision F22
expected rule R7 = 100 % ring 2
SDK versions 5.1 a 4.8
```

### Krok 2 — formuluj konkurenčné hypotézy

```text
H1: distribution lag alebo stale cache
H2: rozdielna tenant identity medzi services
H3: rule precedence prepisuje percentage explicitným override-om
H4: staršia SDK odmieta payload schema F22
H5: niektorý code path flag vôbec nevyhodnocuje
```

### Krok 3 — vyber observation points

- effective config revision a cache age per instance testujú H1;
- hashed subject key a evaluation context testujú H2;
- matched rule/reason testuje H3;
- config rejection a SDK schema logs testujú H4;
- traces bez evaluation eventu testujú H5.

Atlas zistí, že instances so SDK 4.8 odmietli nový structured payload a zostali na F21. H4 vysvetľuje rozdiel; control-plane publish bol úspešný, no data-plane activation nie.

### Krok 4 — containment a recovery

Promotion sa pause-ne. F22 sa nenahradí nekompatibilnou hot editáciou; Atlas publikuje backward-compatible F23 alebo upgraduje SDK cohort. Target sa považuje za 100 % až po effective-revision coverage a outcome evidence.

### Krok 5 — over pôvodný outcome

```text
všetky eligible instances používajú supported revision
matched rule je R7
tenant assignment je konzistentný
technical/functional/business guardrails sú zdravé
```

### Krok 6 — vráť learning

Incident vytvorí config-schema compatibility gate, SDK inventory precondition a explicitný `published ≠ effective` dashboard.

## 16. Flag lifecycle končí odstránením branchu

Release flag lifecycle:

```text
create contract
→ deploy old + new path so safe defaultom
→ limited exposure
→ final behavior accepted
→ new behavior sa stane code defaultom
→ odstráni sa evaluation
→ odstráni sa old path a test matrix
→ metadata sa zmažú po rollback windowe
```

`100 % on` nie je cleanup. Kód stále obsahuje dve paths, evaluation dependency, dashboards a kombinácie s inými flags.

Cleanup musí rešpektovať supported old artifacts, client skew, schema phase a rollback window. Príliš skoré odstránenie flag metadata môže rozbiť rollback staršieho artifactu.

## 17. Diagnostický runbook

1. Potvrď application version, flag key a published config revision.
2. Zisti effective revision, cache age a SDK version na affected evaluatoroch.
3. Porovnaj expected context s actual subject identity.
4. Over matched rule, precedence a evaluation reason.
5. Skontroluj distribution lag, rejection a startup fallback.
6. Validuj payload schema, prerequisites a atomic multi-flag invariant.
7. Nájdite code paths bez evaluation alebo s lokálnym override-om.
8. Pri incidente over skutočný effective kill state a vzniknuté side effects.
9. Posúď old artifact/data compatibility pred rollbackom.
10. Aktualizuj inventory, expiry a cleanup action podľa root cause.

## 18. Referenčné pravidlá

- Feature flag je distribuovaný production control plane.
- Published config a effective runtime state sú odlišné observation points.
- Každá evaluation má subject, revision, rule a reason.
- Code a remote defaults majú explicitnú failure semantiku.
- Assignment používa stabilnú identity naprieč workflowom.
- Rule precedence musí byť konzistentná a vysvetliteľná.
- Client-side flag nie je authorization.
- Multi-flag invariant potrebuje atomic alebo compatible transition.
- Migration flag riadi fázu, nie data compatibility.
- Kill switch je účinný až po potvrdení effective state-u všetkých relevantných paths.
- `100 % on` nie je koniec lifecycle.

## 19. Časté omyly

### „Control plane ukazuje off, incident je zastavený“

Evaluators môžu mať stale snapshot alebo flag nevyhodnocovať.

### „Flag je iba jednoduchý boolean“

Context, precedence, revision a SDK semantics tvoria effective behavior.

### „Flagom môžeme riadiť authorization“

Client alebo iný server path môže evaluation obísť.

### „Tri flags zapneme postupne“

Intermediate kombinácie môžu porušiť runtime invariant.

### „100 % on znamená hotovo“

Old path, tests, config a operational debt stále existujú.

## 20. Zhrnutie

Atlas feature-flag lifecycle je:

```text
versionovaný flag contract
→ old/new paths so safe defaults
→ validated CAS publish
→ pozorovateľná distribúcia
→ deterministic context + precedence evaluation
→ behavior/exposure a guardrails
→ effective-state containment alebo promotion
→ final code default
→ branch, metadata a dependency cleanup
```

Feature flags znižujú release coupling, ale pridávajú nový distribuovaný stav. Sú bezpečné iba vtedy, keď organizácia vie vysvetliť nielen požadovanú hodnotu, ale aj to, ktorú revision každý evaluator skutočne použil, prečo zvolil variant a či zmena ovládla celý failure path.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ring deployment](ring-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Progressive delivery →](progressive-delivery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->