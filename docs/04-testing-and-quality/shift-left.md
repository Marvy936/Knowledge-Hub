# Shift-left

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

## 1. Definícia

Shift-left je návrhový princíp, podľa ktorého sa konkrétny dôkaz o kvalite, bezpečnosti alebo prevádzkovej pripravenosti získava v najskoršom bode delivery toku, kde ho možno získať dostatočne spoľahlivo. Cieľom nie je presunúť všetky testy na lokálny počítač ani preniesť zodpovednosť špecializovaných tímov na vývojára. Cieľom je skrátiť čas medzi vytvorením chyby a použiteľnou spätnou väzbou bez neprimeranej straty fidelity.

Zjednodušený delivery tok:

```text
potreba
→ požiadavka
→ návrh
→ implementácia
→ commit
→ build
→ integrácia
→ deployment
→ produkcia
```

Shift-left sa pri každom riziku pýta:

```text
Aký je najskorší bod,
v ktorom vieme získať dôkaz dostatočný na rozhodnutie?
```

Dôležité je slovo „dostatočný“. Skorší, ale nepresný signál môže vytvoriť false confidence alebo zablokovať správnu zmenu. Niektoré vlastnosti preto zostávajú zámerne v neskorších vrstvách alebo v produkčnej validácii.

## 2. Mental model: presun dôkazu, nie iba testu

Shift-left sa často zjednodušuje na „spusti testy skôr“. Presnejší model je presun rozhodovacieho dôkazu. Dôkazom môže byť test, ale aj formálnejšia požiadavka, type check, threat model, schema, policy, compatibility analýza, plan alebo experiment.

Príklady:

- **Neplatný dátový tvar —** JSON Schema alebo typový model môže chybu zachytiť pri editácii alebo v pull requeste namiesto runtime zlyhania.
- **Cross-tenant prístup —** authorization matrix a negatívne API testy môžu vzniknúť už z threat modelu, nie až po penetračnom teste.
- **Breaking API zmena —** contract diff a provider verification môžu zablokovať nekompatibilný build pred spoločným integračným prostredím.
- **Deštruktívna infra zmena —** policy nad Terraform planom môže odhaliť replacement databázy pred apply.
- **Neobnoviteľný backup —** túto vlastnosť nemožno dôveryhodne potvrdiť iba staticky; restore drill zostáva dynamickou a neskoršou kontrolou.

Shift-left teda nevytvára jedinú vrstvu. Vytvára reťaz dôkazov s rastúcou fidelity.

## 3. Prečo je skorý feedback hodnotný

Čím neskôr sa chyba odhalí, tým väčší býva stav systému, ktorý už na chybnom predpoklade závisí. Rastie work in progress, počet dotknutých ľudí, veľkosť batchu, náklady na reprodukciu aj riziko výnimky pod časovým tlakom.

Typický mechanizmus neskorého feedbacku:

```text
chybný predpoklad
→ ďalší kód a testy na ňom závisia
→ artifact sa integruje s ďalšími zmenami
→ chyba sa prejaví v širokom systéme
→ root cause má mnoho kandidátov
→ oprava vyžaduje koordináciu a rollback
```

Skorá kontrola zužuje diagnostický scope. Compile error pri konkrétnom riadku je lacnejší než runtime chyba v distribuovanom workflowe. Neplatný kontrakt odhalený v pull requeste je lacnejší než incident starého consumera po deploymente providera.

Hodnota shift-left sa však stráca, keď kontrola:

- poskytuje chronicky hlučný výsledok,
- trvá tak dlho, že ju používatelia obchádzajú,
- nereprodukuje sa mimo centrálnej pipeline,
- používa neaktuálnu konfiguráciu alebo iný toolchain,
- kontroluje iba formu a vydáva sa za runtime dôkaz,
- nemá ownera ani jasnú remediation cestu.

## 4. Evidence-placement model

Každá kontrola má prirodzené miesto určené šiestimi vlastnosťami:

- **Riziko —** aký failure mode alebo nesprávne rozhodnutie má kontrola odhaliť.
- **Fidelity —** ako presne testovacie podmienky reprezentujú relevantnú produkčnú vlastnosť.
- **Latencia feedbacku —** ako rýchlo po zmene dostane autor výsledok.
- **Diagnostikovateľnosť —** ako úzko možno z failure určiť príčinu.
- **Cena —** runtime, infra náklady, maintenance a kognitívna záťaž.
- **Autorita —** či výsledok iba radí, alebo je auditovateľným gate-om.

Praktický princíp:

```text
vyber najnižšiu a najskoršiu vrstvu,
ktorá ešte zachytí reálny failure mode
s prijateľným false-negative rizikom
```

Príklady vhodného umiestnenia:

| Riziko | Najskorší spoľahlivý dôkaz | Neskorší doplnkový dôkaz |
|---|---|---|
| Syntax chyba | editor/compiler | CI build |
| Neplatná enum hodnota | schema/unit test | API test |
| SQL constraint | test s reálnou DB | component/E2E |
| API compatibility | contract diff/verifier | staging integration |
| Verejne otvorený port | IaC policy/plan | runtime connectivity test |
| Nesprávna regionálna latency | model a targeted benchmark | produkčný canary/RUM |
| Obnova po výpadku zóny | návrhový review a chaos plán | game day alebo produkčný experiment |

## 5. Shift-left začína pri požiadavke

Najlacnejšia chyba je tá, ktorá sa nestane súčasťou návrhu. Preto shift-left začína skôr než pri kóde. Nejasná požiadavka nevytvára stabilný test oracle a následné testy môžu presne overovať nesprávny výsledok.

Požiadavka by mala pomenovať:

- **Pozorovateľný výsledok —** čo má používateľ, systém alebo operátor vidieť.
- **Hranice —** na ktoré identity, tenanta, regióny, dáta alebo verzie sa správanie vzťahuje.
- **Negatívne správanie —** čo musí byť odmietnuté alebo bezpečne degradované.
- **Časové vlastnosti —** deadline, latency, RPO, RTO alebo expiráciu.
- **Kompatibilitu —** ktoré staršie verzie alebo súbežné deploymenty musia fungovať.
- **Dôkaz —** ktorý test, metric, audit record alebo experiment potvrdí splnenie.

Slabá požiadavka:

```text
API má byť rýchle a bezpečné.
```

Silnejší kontrakt:

```text
Pri 500 requests/s musí p95 úspešných odpovedí zostať pod 250 ms,
error rate pod 0,5 %, klient bez scope `orders:write` musí dostať 403
a rovnaký idempotency key nesmie vytvoriť dve objednávky.
```

Takýto kontrakt vytvára testovateľné oracles ešte pred implementáciou.

## 6. Shift-left v návrhu a architektúre

Design review je shift-left kontrola vtedy, keď identifikuje konkrétne riziko a vytvorí následný dôkaz. Samotné stretnutie bez rozhodnutí a vlastníctva nie je kontrola.

V návrhu sa posudzujú najmä:

- **Trust boundaries —** kde sa mení úroveň dôvery a kde musí existovať autentifikácia, autorizácia alebo validácia.
- **Failure modes —** čo sa stane pri timeout-e, duplicite, partial write, retry, stale read alebo nedostupnej dependency.
- **Data lifecycle —** klasifikácia, retention, encryption, backup, deletion a audit.
- **Compatibility —** rolling deployment, expand-contract migrácie, event schema a staré clients.
- **Operability —** metrics, logs, traces, health semantics, runbook a recovery ownership.
- **Capacity assumptions —** pracovný profil, bottleneck kandidáti, quotas a scaling latency.

Výstup návrhovej kontroly má byť prepojený na implementačný alebo testovací artefakt. Napríklad rozhodnutie „consumer musí tolerovať nové optional fields“ sa má prejaviť v contract teste. Rozhodnutie „queue musí byť bounded“ sa má prejaviť v stress alebo component teste.

## 7. Developer feedback loop

Lokálna vrstva má poskytovať rýchly a vysoko diagnostický feedback. Jej cieľom je zabrániť tomu, aby autor čakal na vzdialenú pipeline kvôli chybe, ktorú možno odhaliť za sekundy.

Typické kontroly:

```text
formatter
→ syntax/compiler
→ linter
→ type checker
→ focused unit tests
→ schema a policy checks
→ targeted integration podľa potreby
```

Dobrá lokálna kontrola:

- **Používa rovnaký toolchain —** verzia nástroja a konfigurácia zodpovedajú CI.
- **Je reprodukovateľná —** existuje jeden dokumentovaný príkaz alebo task runner target.
- **Má nízky noise —** failure je spravidla akčný a stabilný.
- **Je inkrementálna —** pri malej zmene nevyžaduje celý enterprise test stack.
- **Neukrýva autoritatívnosť —** lokálny výsledok pomáha, ale CI zostáva dôveryhodnou enforcement boundary.

Pre-commit hook je vhodný ako ergonomická optimalizácia, nie ako jediný gate. Používateľ ho môže obísť, nemusí ho mať nainštalovaný a jeho beh nemusí zanechať auditný dôkaz.

## 8. Autoritatívna CI vrstva

CI opakuje kritické skoré kontroly v dôveryhodnom a zaznamenanom prostredí. Lokálny zelený výsledok nie je dostatočný, keď nepoznáme tool version, environment alebo úplnosť spustených kontrol.

Typické poradie fail-fast pipeline:

```text
repository a dependency validation
→ format/syntax/schema
→ lint/type/static analysis
→ unit tests
→ targeted integration a contracts
→ build/package
→ artifact a security verification
→ širšie integration/E2E/performance kontroly
```

Poradie nie je absolútne. Niektoré kroky sa môžu paralelizovať. Zmyslom je neplatiť za drahú kontrolu, keď lacný deterministický gate už dokazuje, že zmena nemôže pokračovať.

CI musí rozlišovať minimálne tieto výsledky:

- **Pass —** kontrola sa kompletne vykonala a požadovaný kontrakt bol splnený.
- **Finding/failure —** kontrola sa vykonala a našla porušenie.
- **Incomplete —** časť vstupov, shardov alebo reportov chýba.
- **Tool/infrastructure failure —** runner, cache, registry alebo analyzátor nefungoval.
- **Skipped by policy —** kontrola sa zámerne nespustila a dôvod je auditovateľný.

Tool failure nesmie byť automaticky interpretovaný ako pass.

## 9. Test selection a false-negative riziko

Shift-left neznamená spustiť celý testovací vesmír pri každom editovaní. Znamená vybrať najmenší dostatočný súbor kontrol. Selection však sama vytvára riziko, pretože chybný dependency graph alebo path mapping môže vynechať relevantný test.

Mechanizmy selection:

- **Changed-file mapping —** mapuje súbor na testy, ale môže prehliadnuť generované alebo runtime väzby.
- **Dependency graph —** zahŕňa downstream komponenty, ak je graf úplný a správne invalidovaný.
- **Test Impact Analysis —** používa historickú execution stopu, ale nemusí poznať nový typ interakcie.
- **Risk tags —** explicitne označujú kritické oblasti, no vyžadujú governance a ownership.
- **Contract ownership —** spúšťa consumer/provider kontroly pri zmene rozhrania.
- **Diff coverage —** upozorní na neotestované nové vetvy, ale nenahrádza test rizika.

Bezpečná selection policy používa vrstvy:

```text
rýchly affected set pri PR
+ periodický širší beh
+ full alebo risk-based suite pred relevantným release rozhodnutím
```

Sleduj false-green incidenty spôsobené selection mechanizmom. Ak zmena prešla preto, že relevantný test nebol zvolený, problémom nie je iba chýbajúci test, ale aj model závislostí.

## 10. Security shift-left

Security shift-left premieňa threat model a secure design na rýchle, akčné a opakovateľné kontroly. Neznamená spustiť každý scanner pri každom commite ani odovzdať celý security program vývojárom.

Vrstva môže obsahovať:

- **Threat modeling —** pomenúva assets, boundaries, abuse cases a controls ešte pred implementáciou.
- **Secure defaults —** templates a libraries nastavujú bezpečný stav bez ručného rozhodovania.
- **Secret scanning —** blokuje nové credentials v source a artefaktoch; nález zároveň spúšťa rotation workflow.
- **SAST a taint analysis —** hľadajú konkrétne source-to-sink paths, nie iba nebezpečné názvy funkcií.
- **SCA —** analyzuje dependency graph, provenance, reachability a policy.
- **IaC policy —** odmieta verejný exposure, privilege expansion alebo chýbajúce encryption controls.
- **Abuse-case tests —** overujú negatívne authorization a input-handling scenáre.

Aby security signal fungoval:

- pravidlá musia byť kurátorované podľa stacku a threat modelu,
- severity musí odrážať kontext, reachability a impact,
- finding musí mať remediation guidance,
- scanner/tool failure musí byť viditeľný,
- exception musí mať risk ownera a expiráciu,
- security tím musí poskytovať platformové guardrails a podporu.

Tisíce neroztriedených findings neposúvajú bezpečnosť doľava. Posúvajú iba šum do skoršej fázy.

## 11. Infrastructure shift-left

Infrastructure as Code umožňuje analyzovať plánovanú zmenu predtým, než zasiahne reálny control plane. Dôkaz sa vrství:

```text
format
→ syntax a schema
→ module/unit test
→ policy nad source
→ rendered manifest alebo plan
→ sandbox apply
→ runtime verification
```

Každá vrstva odpovedá na inú otázku:

- **Syntax/schema —** je vstup parsovateľný a zodpovedá formálnemu modelu.
- **Source policy —** porušuje deklarácia známe pravidlo ešte pred renderovaním.
- **Plan policy —** čo sa reálne vytvorí, nahradí, zmaže alebo privileguje.
- **Sandbox apply —** aké sú provider/API semantics, quotas a dependencies.
- **Runtime verification —** aký je efektívny stav po defaults, mutations a externom drifte.

IaC plan nie je runtime dôkaz. Môže neobsahovať správanie admission controllerov, managed-service defaults, eventual consistency alebo externé identity bindings.

## 12. Databázové zmeny a compatibility

Databázová migrácia je oblasť, kde neskoré zlyhanie býva veľmi drahé. Shift-left preto neznamená iba spustiť migration syntax check. Potrebuje realistický compatibility a operational test.

Kontroluj:

- **Expand-contract poradie —** najprv pridať kompatibilný stav, potom migrovať consumers a až nakoniec odstrániť starý kontrakt.
- **Starú a novú aplikáciu —** počas rolling deploymentu môžu obe verzie pristupovať k jednej schéme.
- **Locking —** migration môže byť syntakticky správna, ale zablokovať kritickú tabuľku.
- **Objem dát —** prázdna databáza neodhalí runtime, disk growth ani query-plan správanie.
- **Restart/retry —** partial execution a opakovaný beh musia mať definovanú semantiku.
- **Rollback alebo roll-forward —** nie každú schema zmenu možno bezpečne revertovať.
- **Backup/restore —** pri kritickej zmene musí existovať overená recovery cesta.

Dôkaz by mal používať anonymizovaný alebo syntetický dataset s reprezentatívnou distribúciou a veľkosťou.

## 13. Observability shift-left

Observability sa nedá plnohodnotne overiť bez runtime, ale dá sa navrhnúť a čiastočne testovať skôr. Aplikácia bez stabilných telemetry kontraktov vytvára v produkcii slepé miesto.

Už pri návrhu a implementácii definuj:

- **Correlation identity —** request, trace, workflow alebo job ID prepája udalosti.
- **Structured logs —** polia majú stabilný význam, typ a redaction pravidlá.
- **Metrics —** názov, jednotka, labels a cardinality budget sú súčasťou kontraktu.
- **Traces —** významné boundaries a failures vytvárajú spans a status.
- **Health semantics —** startup, readiness a liveness odpovedajú na rozdielne otázky.
- **SLI events —** úspech, chyba, latency a business completion sú merateľné.

Skoré testy môžu overiť prítomnosť correlation ID, redaction secrets, schema log eventu alebo povinné metrics. Produkcia stále musí potvrdiť užitočnosť signálu pri reálnom incidente.

## 14. Performance shift-left

Nie každý performance dôkaz vyžaduje celý produkčný stack. Skoršie vrstvy môžu zachytiť algoritmickú regresiu, nebounded memory growth, serialization overhead alebo nevhodný query pattern.

Príklady:

- microbenchmark kritického algoritmu,
- query plan a index test s realistickou distribúciou,
- component load test jednej služby,
- memory allocation profil pri parseri,
- queue capacity a backpressure test,
- startup-time regression build artefaktu.

Microbenchmark však nemôže potvrdiť end-to-end capacity. Výsledok musí byť neskôr doplnený systémovým workloadom a produkčnými signálmi.

## 15. Platform engineering a golden paths

Shift-left škáluje vtedy, keď je zabudovaný do platformy a bežného workflowu. Zoznam manuálnych povinností zvyšuje cognitive load a vedie k nekonzistentným implementáciám.

Golden path môže poskytovať:

- **Repository template —** základné ownership, dependency a policy súbory.
- **Reusable pipeline —** autoritatívne gates s pinovanými nástrojmi.
- **Local task runner —** rovnaké príkazy lokálne aj v CI.
- **Secure libraries —** authentication, logging, retry a secret access so správnymi defaults.
- **Ephemeral environments —** štandardný spôsob spustenia reálnych dependencies.
- **Artifact lifecycle —** build, SBOM, podpis, provenance a immutable promotion.
- **Observability bootstrap —** štandardné telemetry fields, dashboards a alerts.
- **Self-service remediation —** konkrétna dokumentácia a automatické fixy pri náleze.

Golden path nemá byť neauditovaný black box. Tím musí poznať jeho kontrakty, verzie, escape hatch a ownership.

## 16. Blocking verzus advisory feedback

Nie každý skorý signál má okamžite blokovať merge. Nová alebo hlučná kontrola má často začať ako advisory, zbierať baseline a prejsť tuningom.

Blocking kontrola je vhodná, keď:

- chráni relevantné a významné riziko,
- výsledok je presný a reprodukovateľný,
- failure má jasnú remediation,
- runtime je primeraný bodu pipeline,
- tool a jeho dependencies sú stabilné,
- exception proces je auditovateľný.

Advisory kontrola je vhodná, keď:

- sa kalibruje nové pravidlo,
- signál je trendový alebo probabilistický,
- legacy baseline ešte nie je spracovaný,
- failure vyžaduje ľudské posúdenie,
- kontrola má vyšší false-positive rate.

Advisory stav potrebuje ownera a rozhodnutie, či sa stane blocking, zostane trendovým signálom alebo sa odstráni.

## 17. Failure ownership a remediation

Kontrola bez ownera vytvára frontu, nie feedback loop. Každý gate alebo platformová kontrola musí mať:

- **Rule ownera —** vlastní správnosť pravidla, tuning a toolchain.
- **Code/resource ownera —** rieši konkrétne porušenie vo svojom scope.
- **Runbook —** vysvetľuje reprodukciu, interpretáciu a remediation.
- **Escalation —** určuje postup pri false positive, tool outage alebo urgentnom release.
- **Exception lifecycle —** obsahuje dôvod, risk ownera, compensating control, expiráciu a návrat do súladu.

Ak vývojári musia opakovane hádať, čo kontrola znamená, kontrola je zle navrhnutá aj vtedy, keď technicky nachádza reálne problémy.

## 18. Vzťah shift-left a shift-right

Shift-left a shift-right nie sú konkurenčné stratégie. Tvoria uzavretý feedback systém.

```text
návrh a skoré kontroly
→ release a produkčná validácia
→ pozorované failure modes
→ nové požiadavky, tests a guardrails
```

Shift-left poskytuje rýchly, kontrolovaný a diagnostický dôkaz. Shift-right poskytuje vysokú environment fidelity, skutočné workloady a ľudské správanie. Produkčný incident alebo canary failure má viesť k trvalému skoršiemu testu, policy alebo bezpečnému defaultu tam, kde je to možné.

Niektoré dôkazy nemožno presunúť úplne doľava:

- skutočné regionálne sieťové podmienky,
- produkčné quotas a identity federation,
- reálny traffic mix a používateľské správanie,
- emergentné distribuované interakcie,
- účinnosť recovery pri veľkom reálnom stave,
- business outcome a conversion.

Cieľom je znížiť počet prekvapení vpravo, nie predstierať, že pravá strana už nie je potrebná.

## 19. Metriky účinnosti

Počet nástrojov alebo spustených kontrol nie je cieľ. Meraj, či feedback systém skutočne skracuje učenie a znižuje uniknuté chyby.

Užitočné metriky:

- **Time to first useful feedback —** čas od pushu alebo zmeny po prvý akčný výsledok.
- **Failure-stage distribution —** kde sa chyby zachytávajú; trend môže ukázať presun z produkcie do PR vrstvy.
- **Local-to-CI mismatch rate —** ako často lokálny pass zlyhá v CI pre rozdiel toolchainu alebo prostredia.
- **False-positive rate —** koľko findings alebo failures bolo vyhodnotených ako neplatných.
- **Defect escape rate —** ktoré triedy chýb unikajú za konkrétny gate.
- **Mean time to repair check —** ako dlho zostáva broken alebo flaky kontrola nedôveryhodná.
- **Selection miss rate —** incidenty alebo regressions spôsobené vynechaním relevantnej kontroly.
- **Exception count a age —** či sa dočasné waivery menia na trvalý bypass.
- **Developer wait time —** koľko času sa stráca v queue a pomalých feedback cykloch.

Metriky interpretuj spolu. Skrátenie pipeline za cenu rastu defect escape rate nie je zlepšenie.

## 20. Diagnostický postup pri zlom feedback loope

Keď shift-left kontrola spôsobuje vysoký lead time alebo nízku dôveru, analyzuj ju ako produkčný systém.

1. **Urči riziko —** akú triedu chyby má kontrola zachytiť.
2. **Zmeraj signál —** failure rate, false positives, first-pass stabilitu a runtime.
3. **Over vstupy —** tool version, config, cache, merge base, dependency graph a artifact identity.
4. **Rozlíš failure typ —** nález, neúplný beh, tool bug, infra outage alebo flaky test.
5. **Skontroluj placement —** či kontrola nie je príliš skoro bez fidelity alebo príliš neskoro bez dôvodu.
6. **Skontroluj selection —** či affected model nevynecháva nepriame dopady.
7. **Skontroluj remediation —** či výstup vysvetľuje konkrétnu opravu.
8. **Zhodnoť gate režim —** blocking, advisory, quarantine alebo dočasné vypnutie s incidentom.
9. **Odstráň root cause —** oprav pravidlo, test, platformu alebo workflow; nezavádzaj permanentný rerun.
10. **Over výsledok —** sleduj stabilitu a defect escapes po zmene.

## 21. Typické anti-patterny

### „Všetko musí bežať pred commitom“

Feedback sa stane pomalým a vývojári ho začnú obchádzať. Lokálne majú byť najmä rýchle a vysoko diagnostické kontroly; autoritatívny širší beh patrí do CI.

### Shift-left ako presun práce na developerov

Bez platformy, templates, dokumentácie a špecializovanej podpory rastie cognitive load. Zodpovednosť za bezpečnosť alebo kvalitu ostáva zdieľaná.

### Scanner count ako metrika vyspelosti

Viac nástrojov môže znamenať duplicitné a protichodné findings. Dôležitá je coverage rizík, presnosť a remediation.

### Skorá kontrola ako náhrada runtime dôkazu

Schema, mock alebo plan môže byť zelený, hoci reálny provider, sieť alebo workload zlyhá. Každý dôkaz má explicitnú hranicu platnosti.

### Pre-commit ako jediný enforcement

Lokálny hook sa dá obísť a výsledok nemusí byť auditovaný. Kritická policy musí byť zopakovaná v dôveryhodnej CI vrstve.

### Full suite pri každej malej zmene

Zvyšuje queue time a lead time bez primeranej hodnoty. Použi bezpečnú selection a širšie periodické alebo release gates.

### Selection bez overenia úplnosti

Chybný dependency graph vytvára false green. Selection mechanizmus musí byť testovaný a jeho missy analyzované.

### Permanentné výnimky

Dočasná waiver bez expirá­cie a risk ownera sa stáva novým nezdokumentovaným defaultom.

## 22. Praktický rozhodovací rámec

Pre každú navrhovanú kontrolu odpovedz:

1. Aké konkrétne riziko alebo failure mode chráni?
2. Aký dôkaz je potrebný na rozhodnutie?
3. Ktorá najskoršia vrstva poskytne dostatočnú fidelity?
4. Čo táto vrstva nedokáže overiť a zostáva neskôr?
5. Aké sú false-positive a false-negative dôsledky?
6. Aký je runtime, infra a maintenance cost?
7. Dá sa failure reprodukovať lokálne alebo v ephemeral prostredí?
8. Je kontrola blocking, advisory alebo periodická?
9. Kto vlastní pravidlo, tool a remediation?
10. Ako funguje selection, cache a invalidácia?
11. Aký auditný dôkaz sa uchová?
12. Ako sa výnimka schváli, sleduje a ukončí?
13. Ktoré produkčné signály overia zostávajúce predpoklady?
14. Ako sa incident alebo shift-right poznatok vráti do skoršej vrstvy?

## 23. Kontrolný checklist

Pred zavedením shift-left kontroly over:

- riziko a boundary sú explicitné,
- kontrola má jasný oracle,
- toolchain a konfigurácia sú versionované,
- lokálny a CI príkaz používajú rovnaký kontrakt,
- failure je akčný a obsahuje remediation,
- tool failure sa neinterpretuje ako pass,
- selection má konzervatívny fallback,
- cache invalidácia zahŕňa config a dependencies,
- blocking režim je podložený stabilitou,
- existuje owner a runbook,
- waiver má expiráciu a compensating control,
- metriky sledujú feedback latency aj defect escapes,
- neskoršie integračné a produkčné dôkazy zostávajú zachované.

## 24. Kontrolné otázky

1. Čo sa pri shift-left presúva: test, zodpovednosť alebo dôkaz?
2. Prečo najskorší možný test nemusí byť najlepší test?
3. Ako súvisia fidelity, diagnostikovateľnosť a feedback latency?
4. Ktoré chyby možno odstrániť už spresnením požiadavky?
5. Prečo pre-commit hook nie je autoritatívny gate?
6. Aké stavy okrem pass/fail má rozlišovať CI kontrola?
7. Ako môže affected-test selection vytvoriť false green?
8. Čo odlišuje užitočný security shift-left od skoršieho scanner noise?
9. Prečo IaC plan nenahrádza runtime verification?
10. Ako sa testuje compatibility databázovej migrácie počas rolling deploymentu?
11. Ako platform engineering znižuje cognitive load shift-left kontrol?
12. Kedy má nová kontrola zostať advisory?
13. Ako sa produkčný incident premení na trvalú skoršiu kontrolu?
14. Ktoré vlastnosti musia zostať pre shift-right?
15. Aké metriky dokazujú, že feedback loop sa reálne zlepšil?

## Summary

Shift-left je riadené umiestnenie dôkazu do najskoršej vrstvy, ktorá ešte spoľahlivo zachytí konkrétne riziko. Zahŕňa požiadavky, návrh, lokálny feedback, CI gates, contract a infrastructure checks, security, database compatibility aj observability design. Úspech sa nemeria počtom skorých kontrol, ale kratším časom k akčnému výsledku, nižším počtom uniknutých chýb a stabilnou dôverou v delivery systém. Shift-left nenahrádza shift-right; produkčné poznatky sa musia vracať späť do požiadaviek, testov, policies a bezpečných defaults.

## Glossary impact

Relevantné pojmy: shift-left, early feedback, evidence placement, feedback latency, test selection, affected-project detection, golden path, secure default, policy guardrail, advisory gate, blocking gate, local-to-CI mismatch, selection miss a remediation loop.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Flaky tests a test data](flaky-tests-and-test-data.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Shift-right →](shift-right.md)
<!-- KNOWLEDGE-NAVIGATION:END -->