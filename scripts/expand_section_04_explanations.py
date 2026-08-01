from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRANCH = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
if not BRANCH:
    raise SystemExit("Unable to resolve pull request branch")


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(args), flush=True)
    return subprocess.run(args, cwd=REPO, check=check, text=True)


run("git", "fetch", "origin", BRANCH)
run("git", "checkout", "-B", BRANCH, f"origin/{BRANCH}")

blocks: dict[str, str] = {
    "verification-vs-validation.md": r'''## Doplnenie výkladu: oracle, verdict a hranica dôkazu

Pojem **test oracle** je dôležitý preto, že samotné vykonanie testu ešte nevytvára rozhodnutie. Test runner vie spustiť kód, zachytiť návratovú hodnotu alebo odmerať čas, ale až oracle určí, ktoré pozorovanie sa považuje za správne. Oracle môže byť jednoduchý assertion, schéma, invariant, referenčný model, business pravidlo alebo prevádzkový limit.

Pri jednoduchom deterministickom teste je oracle priamo viditeľný:

```python
result = calculate_total([100, 250], tax_rate=0.20)
assert result == 420
```

Prvý riadok vytvorí **observed result**. Druhý riadok porovná pozorovanie s očakávanou hodnotou `420`. Ak assertion prejde, dôkaz platí iba pre túto implementáciu, tento vstup, túto konfiguráciu a tento výpočet. Nepreukazuje správnosť všetkých vstupov ani to, že sadzba `0.20` zodpovedá reálnemu business pravidlu. Prvá otázka patrí verification; druhá môže vyžadovať validation s vlastníkom domény.

Oracle môže byť chybný dvoma základnými spôsobmi. **False positive** v testovacom kontexte znamená, že kontrola nahlási problém, hoci požadované správanie je správne. **False negative** znamená, že test prejde, hoci defect existuje. Napríklad assertion iba na HTTP `200` je slabý oracle: endpoint môže vrátiť `200`, ale uložiť nesprávnu sumu, vynechať audit event alebo vykonať side effect dvakrát.

Silnejší oracle preto rozkladá výsledok:

```text
transport outcome
+ response schema
+ business values
+ persisted state
+ počet side effects
+ authorization boundary
+ audit evidence
```

Nie každý test musí kontrolovať všetky vrstvy. Musí však jasne povedať, ktorú z nich kontroluje. Verification verdict `PASS` teda znamená „pozorovanie sa zhodovalo s týmto konkrétnym oraclom“, nie „systém je všeobecne správny“.

Validation pridáva otázku reprezentatívnosti. Aj dokonale implementovaný test môže používať nereálny workflow, používateľskú skupinu alebo workload. Preto sa pri validation vždy pýtaj:

```text
Kto systém používa?
Aký cieľ sa snaží dosiahnuť?
V akom prostredí a pod akými obmedzeniami?
Aká metrika opisuje úspešný výsledok pre používateľa alebo business?
```

Dôkaz má na konci uvádzať subject a scope. Veta „testy prešli“ je neúplná. Presnejší verdict je napríklad: „Contract testy pre commit `abc123`, schema generation 7 a mockovaného providera prešli; reálny provider, produkčná konfigurácia a business completion neboli týmto testom overené.“

''',
    "test-pyramid.md": r'''## Doplnenie výkladu: čo pyramída skutočne optimalizuje

Test pyramid nie je predpis na pevný počet unit, integration a E2E testov. Je to model **feedback economics**: čím väčší scope test spúšťa, tým viac reálnych hraníc môže overiť, ale spravidla rastie čas, cena setupu, počet failure príčin a náročnosť diagnostiky.

Pojem **scope** označuje časť systému zahrnutú do jedného testu. Unit test môže spustiť jednu funkciu v jednom procese. Integration test môže pridať reálnu databázu. E2E test môže zahrnúť browser, API gateway, služby, broker a databázu. Väčší scope nie je automaticky lepší; prináša vyššiu **fidelity**, teda podobnosť testovacieho prostredia s reálnym systémom, ale zároveň viac neznámych.

Prakticky si každý test predstav ako kombináciu:

```text
subject
+ zahrnuté hranice
+ nahradené hranice
+ setup cost
+ execution time
+ oracle
+ failure localization
```

Napríklad test objednávky môže mať tri podoby:

```text
unit:
pricing function + in-memory inputs

integration:
orders repository + reálna PostgreSQL schema

E2E:
HTTP request + identity + orders service + database + event broker
```

Unit test rýchlo vysvetlí chybu vo výpočte. Integration test odhalí chybný SQL typ alebo transaction behavior. E2E test odhalí, že route, credentials alebo serialization medzi komponentmi nefungujú. Žiadna vrstva nenahrádza ostatné, pretože každá pozoruje iný failure mode.

Pyramída sa pokazí, keď sa všetko overuje cez hornú vrstvu. Jeden E2E failure potom môže znamenať defect v UI, DNS, identity, API, databáze, test data alebo samotnom teste. Naopak príliš veľa izolovaných unit testov môže vytvoriť zelenú suite nad systémom, ktorého komponenty sa nevedia spojiť.

Pri návrhu testu preto nezačínaj otázkou „na ktorú vrstvu patrí?“, ale:

```text
Aké riziko chceme zachytiť?
Ktorá najnižšia vrstva ho dokáže pozorovať s dostatočnou fidelity?
Ktoré reálne hranice musia zostať v teste?
Aký failure artifact umožní rýchlu diagnózu?
```

**Test diamond**, **trophy** alebo iné tvary nie sú konkurenčné pravdy. Vyjadrujú inú architektúru, tooling a rizikový profil. Frontend s lacnými component tests môže mať viac strednej vrstvy. Data pipeline môže potrebovať viac integration testov. Dôležitá je výsledná feedback latency a pokrytie failure modes, nie vizuálny pomer.

''',
    "unit-integration-component-tests.md": r'''## Doplnenie výkladu: subject, process boundary a reálna dependency

Rozdiel medzi unit, integration a component testom sa nedá spoľahlivo určiť podľa názvu frameworku. Rozhoduje **system under test**, teda presný subject, ktorý test vykonáva, a hranice, ktoré sú reálne alebo nahradené.

**Unit test** drží subject úzky a kontroluje jeho dependencies. Unit nemusí znamenať jednu metódu; môže to byť malá coherent business jednotka. Dôležité je, že failure sa dá lokalizovať bez štartu databázy, siete alebo ďalšieho procesu.

```python
def test_discount_is_not_applied_below_threshold():
    policy = DiscountPolicy(threshold=1000, percent=10)
    assert policy.apply(900) == 900
```

Test vytvorí objekt s explicitnými vstupmi a overí jedno business pravidlo. Neoveruje serializáciu, databázu ani konfiguráciu aplikácie. Jeho hodnota je rýchla a presná diagnóza logiky.

**Integration test** ponechá aspoň jednu významnú reálnu hranicu. Pri databáze nejde iba o to, že query „nejako prejde“. Test overuje driver, schema, constraints, transaction isolation, encoding a mapping medzi aplikačným a databázovým modelom.

```text
application repository code
→ database driver
→ reálna database engine
→ migration generation
→ read-back a invariant
```

Ak test používa SQLite namiesto produkčnej PostgreSQL, ide stále o dynamický test, ale fidelity voči SQL dialektu, locking-u a typom je obmedzená. Toto obmedzenie musí byť viditeľné vo verdicte.

**Component test** spustí väčší komponent cez jeho verejnú hranicu, často ako samostatný process alebo container, no externé dependencies nahradí kontrolovanými implementáciami. Napríklad Orders API môže bežať s reálnym HTTP serverom a databázou, ale provider platieb je fake server.

Rozlišuj tiež **in-process** a **out-of-process** boundary. Priame volanie controller function neoveruje HTTP routing, middleware a serialization. Request cez socket na reálny server ich už zahŕňa, aj keď oba testy používajú rovnaký jazyk.

Setup a cleanup sú súčasťou dôkazu. Transaction rollback po každom teste znižuje kontamináciu, ale môže skryť behavior, ktorý nastáva až pri commit-e. Container vytvorený pre suite môže zrýchliť testy, no shared state môže spôsobiť order dependency. Preto má test explicitne uviesť:

```text
čo sa vytvára pre každý test
čo sa zdieľa v suite
ako sa generuje jedinečná identita dát
ako sa overí cleanup
```

Ak test prejde s fake dependency, preukazuje správanie voči contractu fake-u. Nepreukazuje, že fake presne reprezentuje reálnu dependency. Túto medzeru uzatvára contract test alebo samostatný integration test s reálnym systémom.

''',
    "contract-and-api-tests.md": r'''## Doplnenie výkladu: contract nie je iba JSON schema

**Contract** je dohoda medzi producerom a consumerom o tom, ako sa rozhranie používa. Môže zahŕňať endpoint, method, status codes, headers, authentication, schema, význam polí, error model, ordering, idempotenciu a compatibility pravidlá. JSON Schema alebo OpenAPI zachytí významnú časť tvaru, ale nemusí vyjadriť všetky behaviorálne semantics.

Pri HTTP requeste rozlišuj:

```text
request contract
→ method, path, headers, identity, body

response contract
→ status, headers, body schema, business semantics

interaction contract
→ retries, idempotency, ordering, side effects, timeout behavior
```

Jednoduchý API test môže vyzerať takto:

```bash
response_file=$(mktemp)
status=$(curl --silent --show-error \
  --output "$response_file" \
  --write-out '%{http_code}' \
  --header 'Content-Type: application/json' \
  --data '{"orderId":"ord-42","amount":500}' \
  http://127.0.0.1:8080/orders)

test "$status" = '201'
jq -e '.orderId == "ord-42" and .status == "accepted"' "$response_file"
```

`curl --output` oddelí body od statusu. `--write-out` vráti HTTP status ako text; samotný exit code `curl` opisuje transport/tool failure, nie business status. `test` overí status `201` a `jq -e` vytvorí nenulový exit pri nepravdivom výraze. Tento test stále neoveruje počet databázových zápisov, audit event ani správanie pri opakovaní rovnakého `orderId`.

**Provider contract test** overuje, že provider dokáže splniť publikovaný contract. **Consumer-driven contract test** začína interakciami, ktoré konkrétny consumer potrebuje, a provider ich verifikuje proti vlastnej implementácii. Tým sa znižuje riziko, že producer zmení pole, ktoré síce považuje za nepodstatné, ale consumer ho používa.

Contract test nie je plný E2E test. Môže overiť kompatibilitu bez nasadenia všetkých služieb. Je rýchlejší a presnejší, ale nemusí zachytiť gateway rewrite, reálnu identity policy alebo environment routing.

Pri compatibility rozlišuj:

```text
syntactic compatibility
→ dokument sa dá parse-nuť

structural compatibility
→ povinné polia a typy sedia

semantic compatibility
→ rovnaké hodnoty znamenajú rovnakú vec

operational compatibility
→ timeout, retry, ordering a side effects zostávajú použiteľné
```

Pridanie optional field je často backward compatible, ale zmena jeho významu nemusí byť. Preto contract evidence potrebuje exact producer version, consumer version, contract generation a verifier result.

''',
    "end-to-end-and-acceptance-tests.md": r'''## Doplnenie výkladu: čo znamená „od konca po koniec“

End-to-end test musí pomenovať, kde jeho „end“ začína a kde končí. Pre browser workflow môže byť začiatkom používateľský click a koncom potvrdený business stav v backend-e. Pre event pipeline môže byť začiatkom prijatý event a koncom materializovaný read model. Bez tejto definície môže test nazývaný E2E v skutočnosti obísť identity, gateway alebo databázu.

Praktický E2E subject vyzerá napríklad takto:

```text
browser alebo API client
→ DNS/TLS/routing
→ identity
→ application services
→ database a broker
→ business completion oracle
```

**Acceptance test** vyjadruje podmienku, za ktorej stakeholder prijme správanie. Môže byť E2E, ale nemusí. Business acceptance pravidlo pre cenu sa dá overiť component testom, ak nepotrebuje celý systém. Naopak technický E2E smoke test nemusí dokazovať, že funkcionalita spĺňa používateľskú potrebu.

Pri UI teste rozlišuj action a oracle:

```python
page.get_by_role("button", name="Submit order").click()
expect(page.get_by_test_id("order-status")).to_have_text("Accepted")
```

Prvý riadok vykoná používateľskú akciu. Druhý čaká na konkrétny UI stav. Ak aplikácia zobrazí `Accepted` ešte pred durable backend commitom, oracle je príliš blízko prezentácii. Silnejší test môže cez podporované API alebo audit read-back potvrdiť exact `orderId` a final state.

Selectors sú súčasť stability testu. CSS selector viazaný na layout sa rozbije pri vizuálnom refactore bez zmeny správania. Role, accessible name alebo explicitný test ID lepšie reprezentujú používateľský alebo stabilný kontrakt. Test ID však nesmie nahradiť accessibility verification.

Test data setup musí vytvoriť známy počiatočný stav. „Použi existujúceho usera test@example“ vytvára shared mutable dependency. Lepší setup vygeneruje jedinečnú identitu, uloží ju do evidence a cleanup vykoná podľa owner contractu. Pri failure sa data nemajú okamžite zmazať, ak sú potrebné na diagnózu.

E2E suite býva pomalšia, preto sa delí na kritické journeys, širšiu regression sadu a experimentálne scenáre. Retry celého testu môže odlíšiť infra noise od deterministického defectu iba vtedy, ak sa zachová prvý attempt. Zelený retry nesmie prepísať screenshot, trace, network log a backend correlation ID z pôvodného failure-u.

Verdict musí uviesť aj nevykonané hranice. Test proti staging fake payment providerovi nepreukazuje produkčnú provider integráciu. Test cez API nepreukazuje browser behavior. E2E označenie samo osebe nevytvára úplný dôkaz.

''',
    "smoke-and-regression-tests.md": r'''## Doplnenie výkladu: smoke je výber rizík, regression je účel

**Smoke test** je malá sada rýchlych kontrol, ktorá zisťuje, či má zmysel pokračovať v hlbšom testovaní alebo exposure. Názov pochádza z hardvérového „zapni a over, či sa z toho nedymí“; v softvéri však smoke nemá byť iba process-alive check.

Dobrá smoke sada vyberá niekoľko kritických capabilities:

```text
artifact sa spustil
+ správna version/config generation je načítaná
+ request prejde reálnou cestou
+ kritická dependency je použiteľná
+ jedna bezpečná business operácia skončí správne
```

Príkaz:

```bash
curl --fail --silent --show-error \
  http://payments.staging.example/ready
```

preukazuje iba to, že HTTP request dostal 2xx/3xx podľa `curl --fail` contractu a transport nezlyhal. Nepreukazuje správny image digest, database write ani business outcome. Preto sa k nemu často pridá version endpoint a idempotentný synthetic request.

**Regression test** nie je samostatná technická vrstva. Je to test, ktorého účelom je zabrániť návratu už známeho defectu alebo porušenia contractu. Regression test môže byť unit, integration, contract alebo E2E. Po incidente sa má vytvoriť na najnižšej vrstve, ktorá defect spoľahlivo reprodukuje, a podľa rizika aj na vyššej hranici.

Príklad životného cyklu:

```text
incident: duplicate payment pri timeout retry
→ minimal reproducible test
→ server-side idempotency fix
→ unit test deduplication logiky
→ integration test transaction/constraint
→ E2E forbidden test s timeout-after-commit
```

Prvý test lokalizuje logiku, posledný overuje celú nebezpečnú cestu. „Pridali sme regression test“ bez pomenovania reprodukovaného failure mode-u je slabý closure.

Smoke sada musí byť stabilná a malá, ale nie nemenná. Keď sa zmení architektúra alebo kritická business cesta, smoke inventory sa upraví. Zároveň sa nemá zväčšiť na kompletnú regression suite, inak stratí rýchly rozhodovací význam.

Pri failure smoke testu pipeline alebo rollout zvyčajne zastaví ďalší krok. To je gate policy, nie vlastnosť samotného testu. Výsledok potrebuje artifact, environment, configuration, timestamp a correlation evidence; inak nie je jasné, čo vlastne zlyhalo.

''',
    "performance-load-stress-tests.md": r'''## Doplnenie výkladu: workload, percentile a saturation

Performance test nie je „pošli veľa requestov a pozri priemer“. Je to kontrolovaný experiment s definovaným workloadom a oraclom.

Základné pojmy:

- **latency** je čas jednej operácie od zvoleného začiatku po zvolený koniec;
- **throughput** je počet dokončených operácií za jednotku času;
- **concurrency** je počet operácií rozpracovaných naraz;
- **saturation** znamená, že resource alebo queue už nemá voľnú kapacitu a práca čaká;
- **error rate** musí mať explicitný denominator, napríklad failed logical orders / all logical orders.

Pri percentile `p95` zoradíme pozorované latencies a hľadáme hranicu, pod ktorou skončilo približne 95 % operácií. Neznamená to „95 % času bol systém taký rýchly“ ani „najhorších 5 % malo presne túto hodnotu“. Pri malom sample je percentile nestabilný; pri zmiešaných cohorts môže skryť problém jednej route alebo AZ.

Workload model musí popísať:

```text
arrival rate alebo počet virtuálnych používateľov
request mix
payload distribution
session/think time
warm-up
trvanie steady window
cache state
external dependency behavior
```

**Load test** overuje očakávaný alebo peak workload. **Stress test** zvyšuje tlak za očakávanú hranicu a sleduje failure mode a recovery. **Spike test** skúma náhly skok. **Soak test** trvá dlho a hľadá leak, backlog alebo postupnú degradáciu.

Ukážka s k6:

```javascript
export const options = {
  scenarios: {
    orders: {
      executor: 'constant-arrival-rate',
      rate: 100,
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 50,
      maxVUs: 300,
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<400'],
  },
};
```

`constant-arrival-rate` sa snaží začínať 100 iterations za sekundu. VUs sú workers potrební na udržanie arrival rate; ak operácie spomalia a `maxVUs` nestačí, generator nedokáže vytvoriť požadovaný workload. Threshold je oracle, nie samotné meranie. `p(95)<400` platí pre metriku a tags zahrnuté v query; môže miešať rôzne endpointy, ak ich nerozdelíme.

Pozor na **coordinated omission**: closed-loop generator čaká na dokončenie pomalého requestu a počas stall-u neposiela ďalšie. Tým vynechá operácie, ktoré by v reálnom arrival modeli čakali, a nameria príliš dobrú latency. Arrival-rate model alebo korekcia histogramu lepšie reprezentuje frontu.

Performance verdict musí spojiť client measurements so server-side CPU, memory, queue, pool, database waits a errors. Rýchly client result bez potvrdenia dokončeného business outcome-u môže merať iba accepted request, nie celú operáciu.

''',
    "security-and-infrastructure-tests.md": r'''## Doplnenie výkladu: threat, control a tri úrovne evidence

Security test má začínať **threatom alebo abuse case-om**, nie iba zoznamom scannerov. Threat opisuje, kto alebo čo môže vykonať nežiaducu akciu, cez akú hranicu a s akým dopadom. Control je mechanizmus, ktorý má akciu zabrániť, obmedziť alebo zaznamenať.

Príklad:

```text
Threat: neautentizovaný caller číta cudziu objednávku.
Control: authentication + tenant-scoped authorization query.
Positive test: owner objednávku prečíta.
Forbidden test: iný tenant dostane 403/404 a žiadne dáta.
Audit test: pokus vytvorí správny security event bez secretov.
```

Pri infraštruktúre rozlišuj tri evidence vrstvy:

```text
source/static
→ čo deklaruje HCL/YAML a policy

plan/resolved
→ čo nástroj po variables, modules a defaults navrhuje vytvoriť

runtime/effective
→ čo cloud, cluster, kernel alebo sieť skutočne presadzuje
```

Policy test nad Terraform source môže prehliadnuť hodnotu pridanú module defaultom. Policy nad plan JSON vidí resolved resource graph, ale nepreukazuje, že apply prebehne v správnom account-e ani že runtime policy nebude zmenená iným writerom.

Príklad plan kontroly:

```bash
terraform show -json tfplan > tfplan.json
conftest test tfplan.json --policy policy/
```

Prvý príkaz serializuje saved plan do JSON. Druhý vyhodnotí policy rules nad týmto konkrétnym dokumentom. PASS znamená, že pravidlá nenašli porušenie v analyzovanom plane. Nepreukazuje úplnosť policy, bezpečnosť provider implementation ani effective stav po apply.

Security test musí obsahovať aj **negative/forbidden path**. Pozitívny test „admin dokáže deployovať“ nepreukazuje least privilege. Forbidden test „read-only principal nedokáže meniť production“ overuje enforcement hranicu. Pri takom teste sa používa izolovaný test principal a bezpečný target, aby experiment nevytvoril reálny incident.

Scanner finding je hypotéza alebo evidence item, nie automaticky exploitable defect. Severity, reachability, runtime exposure, compensating controls a asset criticality ovplyvňujú rozhodnutie. Naopak nulový report môže znamenať chýbajúci scanner job alebo neparsovaný report. Gate preto overuje aj completeness: očakávaný tool, target, ruleset, timestamp a successful report ingestion.

''',
    "static-analysis-linting-type-checking.md": r'''## Doplnenie výkladu: parser, pravidlo a statický verdict

Statická analýza pracuje bez vykonania cieľového programu. Nástroj najprv načíta source alebo bytecode, vytvorí tokeny, syntax tree, type graph alebo control/data-flow model a potom vyhodnotí pravidlá. Rozdiel medzi formatterom, linterom, type checkerom a analyzátorom je najmä v hĺbke modelu.

- **formatter** mení alebo kontroluje prezentáciu source podľa deterministických pravidiel;
- **linter** hľadá syntaktické, štýlové a vybrané correctness patterny;
- **type checker** overuje kompatibilitu typov a kontraktov;
- **SAST/data-flow analyzátor** sleduje možné cesty dát alebo control flow, napríklad source-to-sink tok.

Príkazy:

```bash
ruff check .
mypy src/
```

Exit code `0` typicky znamená, že zapnuté rules pre analyzované files nevytvorili blocking finding. Neznamená to, že program je bez defectov. Výsledok závisí od configu, excluded paths, rule versions, type stubs a suppressions.

Type hint:

```python
def total(amounts: list[int]) -> int:
    return sum(amounts)
```

pomáha checkeru odhaliť caller, ktorý odovzdá `list[str]`. Runtime Python však annotations sám nevynucuje. Ak data prichádzajú z JSON, treba ich parse-nuť a validovať; zelený type checker nepreukazuje runtime typ external inputu.

Suppression ako `# noqa`, `//nolint` alebo `# type: ignore` je zmena policy. Má byť úzka, viazaná na konkrétny rule a odôvodnenie. Globálne vypnutie pravidla môže vytvoriť false-green. Audit preto sleduje nielen počet findings, ale aj config generation, exclusions a trend suppressions.

Statický finding môže byť false positive, pretože analyzátor nemá celý runtime kontext. Oprava však nemá automaticky znamenať suppression. Najprv sa potvrdí path, input controllability a sink semantics. False negative vznikne, ak pravidlo daný pattern nemodeluje, file sa neanalyzuje alebo dynamické správanie uniká statickému modelu.

Static checks sú vhodné skoro v feedback chain-e, pretože sú rýchle a reprodukovateľné. Dynamic testy ich dopĺňajú tam, kde rozhoduje runtime configuration, concurrency, dependency alebo business outcome.

''',
    "code-coverage-and-quality-gates.md": r'''## Doplnenie výkladu: denominator coverage a význam gate-u

Coverage je pomer pozorovaných programových prvkov k zvolenému denominatoru. **Line coverage** sleduje vykonané riadky, **branch coverage** výsledky podmienok, **function coverage** volané funkcie a **condition coverage** jednotlivé boolean časti. Hodnota 80 % bez uvedenia typu, scope a exclusions je neúplná.

Príklad:

```python
def classify(amount: int) -> str:
    if amount <= 0:
        return "invalid"
    if amount > 1000:
        return "review"
    return "accepted"
```

Jeden test s `amount=100` vykoná väčšinu riadkov, ale neoverí `invalid` ani `review` branch. Vysoká line coverage preto nemusí znamenať silný oracle. Test môže riadok vykonať bez assertion na jeho výsledok.

Coverage report odpovedá „čo testy vykonali“, nie „čo správne overili“. Chýbajúca coverage je užitočná mapa nepozorovaného kódu; prítomná coverage nie je dôkaz correctness.

**Mutation testing** skúša silu testov tak, že nástroj úmyselne zmení program, napríklad `>` na `>=` alebo odstráni volanie, a sleduje, či testy zlyhajú. Preživší mutant naznačuje slabý alebo chýbajúci oracle, ale nie každý mutant je významný alebo neekvivalentný.

Quality gate je policy decision nad evidence:

```text
coverage delta
+ blocking findings
+ test results
+ risk/ownership pravidlá
→ allow alebo block transition
```

Gate `coverage >= 80 %` môže motivovať bezcenné testy alebo trestať generated code. Lepší gate môže sledovať coverage zmeneného rizikového kódu, branch coverage a zakázaný pokles, pričom kritické paths majú explicitné tests nezávisle od percenta.

Pri pull requeste rozlišuj absolute a differential gate. Absolute gate hodnotí celý repository. Differential gate hodnotí novú zmenu. Oba potrebujú stabilný baseline; ak sa base branch medzitým zmenila, porovnanie sa môže stať stale.

Gate failure neznamená automaticky product defect. Môže ísť o missing report, parser error alebo policy service outage. Fail-open prekladá chýbajúce evidence na PASS a je nebezpečný pri required controls. Pipeline má odlíšiť `FAIL`, `ERROR` a `MISSING`, aby owner vedel, či opraviť kód, test alebo evidence path.

''',
    "mocks-stubs-fakes.md": r'''## Doplnenie výkladu: rozdiel medzi stubom, fake-om, mockom a spy

Test double je náhradná implementácia dependency používaná v teste. Jednotlivé názvy opisujú odlišný účel:

- **stub** vracia pripravené odpovede; test sa pýta na výsledok subjectu;
- **fake** má zjednodušenú, ale funkčnú implementáciu, napríklad in-memory repository;
- **mock** obsahuje očakávania na interakcie a test verifikuje, že boli splnené;
- **spy** zaznamenáva volania reálnej alebo náhradnej implementácie na neskoršie assertions;
- **dummy** iba vypĺňa parameter a test ho nepoužíva.

Stub príklad:

```python
class ExchangeRateStub:
    def get_rate(self, currency: str) -> float:
        return 1.10
```

Test s ním overí pricing behavior pre fixnú sadzbu. Neoverí HTTP client, timeout ani parser skutočného provider response.

Mock príklad:

```python
mailer.send.assert_called_once_with(
    recipient="user@example.com",
    template="order-confirmed",
)
```

Assertion kontroluje interaction contract. Je vhodný, ak samotné volanie je dôležitý side effect. Ak test mockuje každý interný call, začne kopírovať implementáciu a zlyhá pri refactore bez zmeny behavioru.

Fake repository môže zrýchliť component tests, ale musí priznať rozdiel oproti reálnej databáze. Python dictionary nemá SQL constraints, isolation ani collation. Ak fake dovolí stav, ktorý produkčná databáza odmietne, zelený test je false confidence. Contract suite môže byť spustená proti fake-u aj reálnej implementácii a overiť spoločné behavior pravidlá.

Dôležité je, kto double vlastní. Consumer-defined stub môže postupne driftovať od providera. Generated client alebo provider contract verification znižuje túto medzeru. Pri externom API sa fake server má viazať na versionovaný contract a podporovať aj chybové odpovede, latency a retry-relevant behavior.

Test double nesmie z testu odstrániť presne tú hranicu, ktorej riziko chceme overiť. Ak rizikom je transaction isolation, in-memory fake nie je vhodný. Ak rizikom je čisto rozhodovacia logika po prijatí provider statusu, stub môže byť najnižší a najlepší scope.

''',
    "flaky-tests-and-test-data.md": r'''## Doplnenie výkladu: nondeterminizmus, seed a first-attempt evidence

Flaky test dáva pri nezmenenom relevantnom subjecte rozdielne verdicty. Príčina môže byť v produkte, teste alebo prostredí. Označenie „flaky“ preto nie je diagnóza; je to pozorovanie nestability.

Typické zdroje:

```text
čas a timezone
random input bez zachovaného seed-u
race a scheduling
shared mutable data
poradie testov
network/dependency noise
eventual consistency
resource exhaustion
```

Pri random teste sa seed uloží do failure outputu:

```python
seed = int(os.environ.get("TEST_SEED", "20260801"))
rng = random.Random(seed)
```

Rovnaký seed umožní znovu vytvoriť pseudonáhodnú sekvenciu. Nepreukazuje úplnú reprodukovateľnosť, ak sú prítomné threads, clock alebo external services.

Čas sa v unit teste injectuje namiesto čítania wall clocku. Assertion typu `sleep(2); assert ready` je krehký, pretože háda timing. Pri eventual consistency je lepšie bounded polling:

```python
deadline = time.monotonic() + 10
while time.monotonic() < deadline:
    if read_state(order_id) == "complete":
        break
    time.sleep(0.2)
else:
    raise AssertionError("order did not become complete within 10 s")
```

Polling používa monotonic clock a explicitný deadline. Stále treba zachovať posledný observed state a correlation ID, inak timeout nepomôže diagnóze.

Retry policy testu nesmie zahodiť prvý failure. Ak prvý attempt zlyhá a druhý prejde, výsledok je „unstable“, nie čistý PASS. Ulož screenshot, trace, logs, seed, worker, timing a dependency state z prvého pokusu.

Test data potrebuje identity a ownership. Shared účet alebo pevné `order-1` spôsobí kolízie pri parallel runoch. Jedinečný prefix viazaný na run ID znižuje konflikt. Cleanup sa vykoná iba nad dátami vytvorenými testom; pri failure môže byť odložený podľa retention policy pre investigation.

Quarantine je dočasné oddelenie nestabilného testu, nie odstránenie problému. Musí mať ownera, issue, dátum a zachované signalovanie. Ak sa flaky test iba ignoruje, suite prestáva pokrývať príslušné riziko.

''',
    "shift-left.md": r'''## Doplnenie výkladu: skorší feedback nie je presun všetkého do unit testov

Shift-left znamená dostať relevantný feedback bližšie k momentu, keď vzniká rozhodnutie alebo chyba. „Left“ je metafora časovej osi delivery. Neznamená to, že všetky production, integration alebo security kontroly sa majú nahradiť statickým checkom.

Mechanizmus je:

```text
neskorý drahý failure
→ identifikácia jeho skoršie pozorovateľného signálu
→ lacnejší control pri source/design/build hranici
→ zachovanie vyššej runtime kontroly pre zvyškové riziko
```

Ak produkčný incident spôsobila chýbajúca database column, skorší control môže byť migration compatibility test v CI. Runtime smoke však zostáva, pretože CI nepreukáže správny target database ani oprávnenia.

Príklady shift-left:

- threat modeling pred implementáciou namiesto iba penetračného testu na konci;
- schema/contract review pred consumer deploymentom;
- local formatter, linter a unit test pred remote pipeline;
- Terraform plan policy pred apply;
- ephemeral integration environment pred production rolloutom.

Každý skorší model má fidelity limit. Mockovaný provider nedokáže potvrdiť reálnu TLS alebo quota policy. Preto sa shift-left kombinuje so shift-right, nie stavia proti nemu.

Dôležitá je aj developer experience. Gate, ktorý beží skoro, ale trvá 40 minút alebo dáva neurčitý output, vytvára obchádzanie. Skorý control má byť rýchly, lokálne reprodukovateľný a diagnostický. Ak potrebuje drahé prostredie, môže sa spustiť asynchrónne, ale merge policy musí jasne povedať, či je evidence required.

Shift-left success sa nemeria počtom pridaných tools. Meria sa napríklad skrátením času od zavedenia defectu po detekciu, nižším počtom escaped defects a menšou opravnou náročnosťou bez neprimeraného nárastu false positives.

''',
    "shift-right.md": r'''## Doplnenie výkladu: kontrolované učenie z reálneho runtime

Shift-right používa post-deployment a production-like evidence, pretože niektoré vlastnosti vzniknú až v reálnom trafficu, topológii, dátach a závislostiach. Neznamená to testovať nebezpečné hypotézy priamo na všetkých používateľoch.

Typické mechanizmy:

- synthetic transaction pravidelne vykonáva bezpečnú známu cestu;
- canary alebo ring vystaví novú generation malej stabilnej cohorte;
- feature flag oddelí deployment od behavior exposure;
- runtime verification číta loaded version, config a business outcome;
- production telemetry odhaľuje neznáme kombinácie a dlhodobé trendy.

Synthetic request potrebuje stabilnú operation identity a cleanup. Ak vytvára reálne objednávky bez označenia, znečisťuje business dáta. Ak používa úplne obídenú test route, nemusí reprezentovať user path.

Canary verdict musí porovnávať compatible cohorts:

```text
nová a stará generation
+ rovnaký región, tenant class a request mix
+ stabilné assignment pravidlo
+ dostatočné observation window
+ technical aj business metrics
```

Zelené CPU a HTTP 5xx môžu prehliadnuť nesprávne ceny alebo duplicate side effects. Preto shift-right oracle zahŕňa final business completion a forbidden outcomes.

Feature flag je runtime control plane. Source default, remote flag value, targeting rules, SDK cache a loaded process state môžu byť odlišné generations. Test „flag je off v UI“ nepreukazuje, že všetky processes správanie vypli. Read-back a telemetry majú publikovať effective generation bez secretov.

Experiment musí mať blast radius, ownera, abort podmienku a recovery. Pozorovanie production failure bez vopred pripravenej akcie nie je bezpečný shift-right. Rovnako monitoring bez rozhodovacieho contractu iba zhromažďuje dáta.

Shift-right dôkaz je časovo ohraničený. Canary prešiel pri určitej záťaži a dependency state; nepreukazuje správanie pri budúcom peak-u alebo inom regióne. Výsledok sa viaže na cohort, interval, release a configuration generation.

''',
    "chaos-testing.md": r'''## Doplnenie výkladu: hypothesis, steady state a fault injection

Chaos testing je riadený experiment nad odolnosťou systému. Nejde o náhodné vypínanie komponentov. Experiment začína **hypotézou**: konkrétnym tvrdením o observable business alebo service outcome-e počas definovaného zlyhania.

Príklad:

```text
Hypotéza:
Ak jedna z troch API replík zanikne,
úspešnosť idempotentných objednávok zostane >= 99.9 %
a p95 completion latency zostane < 800 ms.
```

**Steady state** je merateľný normálny stav pred experimentom. Môže obsahovať success rate, queue depth, reconciliation lag alebo business invariant. Nie je to všeobecná veta „systém je zdravý“. Pred fault injection sa overí, že steady-state podmienky platia; inak experiment nevie odlíšiť existujúci problém od vyvolaného efektu.

**Fault injection** je kontrolovaná mutation, napríklad ukončenie procesu, latency, packet loss, dependency error alebo resource pressure. Fault musí mať exact target identity a trvanie. `kill random pod` bez zaznamenania Pod UID, Node, generation a ownera vytvára slabý experiment.

Experiment flow:

```text
hypotéza a risk
→ exact target a blast radius
→ steady-state baseline
→ observability a abort oracle
→ fault injection
→ system response a user/business outcome
→ fault removal
→ recovery a backlog reconciliation
→ lessons a permanent control
```

Abort condition chráni systém. Napríklad experiment sa zastaví pri error rate > 2 %, queue > 10 000 alebo strate redundantnej druhej AZ. Automation musí mať nezávislú cestu na zastavenie faultu; nemá závisieť iba od systému, ktorý práve poškodzuje.

Príkaz ako:

```bash
kubectl delete pod payments-api-abc123 -n payments
```

preukazuje prijatie delete requestu pre konkrétny object. Nepreukazuje, že Pod naozaj zanikol, že controller vytvoril náhradu alebo že traffic zostal úspešný. Read-back potrebuje Deployment/ReplicaSet/Pod convergence, EndpointSlice a business synthetic result.

Chaos experiment prejde iba vtedy, keď sa potvrdí hypotéza a systém sa po odstránení faultu vráti do akceptovaného stavu. Ak používateľské requests uspeli, ale backlog zostal nekonečne rásť, experiment odhalil latentný failure. Recovery a druhá operácia sú rovnako dôležité ako správanie počas faultu.

''',
}

section_dir = REPO / "docs/04-testing-and-quality"
anchor_re = re.compile(
    r"(?m)^## (?:\d+\.\s*)?(?:Connected incident|Incident|Atlas incident|Zhrnutie|Troubleshooting flow|Anti-patterny)"
)

for filename, block in blocks.items():
    path = section_dir / filename
    text = path.read_text(encoding="utf-8")
    marker = block.splitlines()[0]
    if marker in text:
        raise RuntimeError(f"Expansion already present in {filename}")
    match = anchor_re.search(text)
    if match:
        text = text[: match.start()] + block + text[match.start() :]
    else:
        nav = "<!-- KNOWLEDGE-NAVIGATION:START -->"
        if nav not in text:
            raise RuntimeError(f"No insertion anchor in {filename}")
        text = text.replace(nav, block + nav, 1)
    path.write_text(text, encoding="utf-8")

readme_path = section_dir / "README.md"
readme = readme_path.read_text(encoding="utf-8")
readme_anchor = "## Čo má čitateľ po sekcii vedieť\n"
readme_block = r'''## Rozšírený výklad pojmov, kódu a výsledkov

Všetkých pätnásť kapitol teraz pri kľúčových pojmoch a ukážkach explicitne vysvetľuje, čo daný pojem znamená, prečo sa používa, aký subject a scope kontrola zahŕňa, ako sa príkaz alebo test vyhodnotí a čo jeho PASS/FAIL výsledok preukazuje alebo nepreukazuje. Doplnenia zachovávajú pôvodný prose flow, incidenty a príklady; nepridávajú paralelný syllabus.

Sekcia osobitne rozoberá oracle a false verdicty, test scope a fidelity, unit/integration/component boundaries, API contract semantics, E2E a acceptance hranice, smoke a regression účel, workload a percentily, security threat/control evidence, static-analysis model, coverage denominator a mutation testing, test doubles, flakiness a test data, shift-left/right a chaos hypothesis/steady state/fault injection.

'''
if readme_anchor not in readme:
    raise RuntimeError("Section 04 README anchor missing")
if "## Rozšírený výklad pojmov, kódu a výsledkov" not in readme:
    readme = readme.replace(readme_anchor, readme_block + readme_anchor, 1)
readme_path.write_text(readme, encoding="utf-8")

ledger_path = REPO / "DOCUMENTATION-REVIEW-STATUS.md"
ledger = ledger_path.read_text(encoding="utf-8")
lines = ledger.splitlines()
replacement = "| `04-testing-and-quality` — Testing and Software Quality | 15/15 integrated full prose and explanation-depth revalidation | Ready for user review | 2026-08-01 | Všetkých 15 kapitol zachováva pôvodný odborný prose flow a dopĺňa mechanické vysvetlenie pojmov, test setupu, assertions, metrík a verdictov. Doplnenia pokrývajú oracle a false verdicty, scope/fidelity, test boundaries, contract semantics, E2E/acceptance, smoke/regression, workload/percentily/saturation, threat/control evidence, static analysis, coverage/mutation testing, test doubles, flakiness/test data, shift-left/right a chaos experiment. Navigation, glossary a full documentation audit boli synchronizované. |"
found = False
for index, line in enumerate(lines):
    if line.startswith("| `04-testing-and-quality`"):
        lines[index] = replacement
        found = True
        break
if not found:
    raise RuntimeError("Section 04 ledger row missing")
ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

run("python", "scripts/update_glossary.py", "--write")
run("python", "scripts/update_navigation.py", "--write")
run("python", "scripts/audit_learning_depth.py", "--all-docs")

workflow_path = REPO / ".github/workflows/knowledge-navigation.yml"
workflow = workflow_path.read_text(encoding="utf-8")
step = '''      - name: Expand Section 04 explanations
        if: github.event_name == 'pull_request'
        shell: bash
        run: |
          set -euo pipefail
          "$PYTHON_BIN" scripts/expand_section_04_explanations.py

'''
if workflow.count(step) != 1:
    raise RuntimeError("Temporary Section 04 workflow step missing")
workflow_path.write_text(workflow.replace(step, "", 1), encoding="utf-8")
Path(__file__).unlink()

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run("git", "add", "docs/04-testing-and-quality", "DOCUMENTATION-REVIEW-STATUS.md", "GLOSSARY.md", "glossary", "DOCUMENTATION-AUDIT.md", "documentation-audit.json", ".github/workflows/knowledge-navigation.yml", "scripts")
run("git", "commit", "-m", "docs(testing): deepen explanations across Section 04")
run("git", "push", "origin", f"HEAD:{BRANCH}")
