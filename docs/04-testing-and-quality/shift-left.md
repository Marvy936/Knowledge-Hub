# Shift-left

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

## 1. Definícia

Shift-left znamená presun vhodných kontrol, rozhodnutí a spätnej väzby do skorších fáz vývoja, kde je chyba lacnejšia, bezpečnejšia a rýchlejšia na opravu.

Neznamená „všetko testovať lokálne“ ani „presunúť zodpovednosť na developerov“. Ide o návrh delivery systému tak, aby sa relevantné riziká odhaľovali v najskoršom bode, v ktorom ich možno spoľahlivo posúdiť.

```text
požiadavka
→ návrh
→ implementácia
→ commit
→ build
→ test
→ deployment
→ produkcia
```

Shift-left sa pýta:

> Ktorý dôkaz vieme získať skôr bez neprimeranej straty fidelity?

## 2. Prečo vznikol

Neskoré odhalenie chyby zvyšuje:

- množstvo rozpracovanej práce,
- počet závislých zmien,
- náklady na koordináciu,
- čas diagnostiky,
- blast radius,
- tlak na manuálne výnimky,
- riziko incidentu.

Chyba v požiadavke odhalená pri návrhu je lacnejšia než rovnaká chyba odhalená po produkčnom deploymente.

Shift-left skracuje feedback loop, ale iba vtedy, keď skorá kontrola dáva relevantný a dôveryhodný signál.

## 3. Shift-left nie je jedna technológia

Patria sem napríklad:

- spresnenie acceptance criteria pred implementáciou,
- threat modeling pri návrhu,
- architecture decision review,
- pre-commit formatter a linter,
- local unit tests,
- type checking,
- secret scanning,
- dependency a license checks,
- IaC validation a policy checks,
- contract tests,
- ephemeral test environments,
- testovanie databázových migrácií,
- performance test kritického algoritmu pred systémovým testom.

Spoločnou vlastnosťou je skoršie získanie použiteľného dôkazu.

## 4. Ekonomika skorého feedbacku

Užitočná kontrola má vyvážiť:

```text
čas spustenia
+ náklady na údržbu
+ false-positive rate
+ fidelity
+ pokryté riziko
+ diagnostickú hodnotu
```

Najskoršia kontrola nie je automaticky najlepšia.

Príklad:

- schema validácia môže odhaliť chýbajúci field lokálne,
- integration test musí overiť správanie reálnej databázy,
- produkčná observability musí overiť skutočný traffic pattern.

Cieľom je posunúť doľava iba to, čo možno skoršie overiť dôveryhodne.

## 5. Shift-left v requirements a dizajne

Najväčší efekt často nevzniká v CI, ale pred napísaním kódu.

Kontroly:

- jasné acceptance criteria,
- explicitné failure modes,
- compatibility requirements,
- security boundaries,
- data classification,
- recovery expectations,
- capacity assumptions,
- operability requirements.

Príklad slabej požiadavky:

```text
API má byť rýchle.
```

Lepší kontrakt:

```text
Pri 500 requests/s má p95 latency zostať pod 250 ms,
error rate pod 0,5 % a služba sa musí zotaviť po strate jednej instance.
```

Takýto kontrakt vytvára testovateľný oracle ešte pred implementáciou.

## 6. Developer feedback loop

Lokálna alebo editorová vrstva má poskytovať rýchle kontroly:

- formatting,
- linting,
- type checking,
- focused unit tests,
- schema validation,
- compile/build,
- pre-commit hooks.

Dobrá developer kontrola:

- trvá sekundy až nízke minúty,
- má nízky noise,
- vysvetlí failure,
- reprodukuje sa mimo CI,
- používa rovnaké versions a rules ako pipeline.

Zlý stav vzniká, keď lokálny tool a CI používajú rozdielne konfigurácie.

## 7. Shift-left v CI

Typické poradie lacných až drahších kontrol:

```text
syntax/format
→ lint/type check
→ unit tests
→ targeted integration
→ contract tests
→ build/package
→ security scans
→ broader integration
→ E2E/performance
```

Pipeline má failnúť rýchlo pri lacnom deterministickom probléme.

Nedáva zmysel spúšťať 40-minútový E2E suite pred kontrolou neplatného YAML alebo compile erroru.

## 8. Test selection

Shift-left neznamená spustiť všetko pri každej zmene.

Použiteľné mechanizmy:

- affected-project detection,
- dependency graph,
- changed-file mapping,
- test impact analysis,
- risk tags,
- diff coverage,
- contract ownership.

Cieľ:

```text
malá zmena
→ malý, rýchly a relevantný feedback
```

Full regression zostáva potrebná v iných bodoch pipeline.

## 9. Security shift-left

Security kontroly možno posúvať doľava cez:

- threat modeling,
- secure defaults,
- SAST,
- secret scanning,
- SCA,
- IaC policy,
- container scanning,
- pre-commit checks,
- abuse-case tests.

Riziká zlej implementácie:

- tisíce findings bez prioritizácie,
- blokovanie vývoja low-confidence kontrolami,
- ignorovanie runtime exploitability,
- presun zodpovednosti zo security tímu na developerov bez podpory.

Security shift-left potrebuje:

- curated rules,
- remediation guidance,
- ownership,
- exception lifecycle,
- platformové guardrails.

## 10. Infrastructure shift-left

Pre infraštruktúru:

```text
format
→ syntax
→ validate
→ policy
→ plan
→ integration test
→ runtime verification
```

Kontroly môžu overiť:

- zakázané public endpoints,
- encryption settings,
- required tags,
- IAM privilege,
- destructive changes,
- unsupported versions,
- resource limits.

Plan však stále nie je runtime dôkaz. Provider behavior, quotas a external state sa môžu prejaviť až pri apply.

## 11. Databázové zmeny

Databázová migrácia má byť testovaná pred produkciou proti realistickému schema a dátovému objemu.

Kontroluj:

- backward compatibility,
- lock duration,
- runtime,
- disk growth,
- rollback alebo roll-forward,
- aplikáciu starej aj novej verzie,
- expand-contract postup,
- reštart a retry behavior.

Samotné úspešné vykonanie migrácie na prázdnej databáze je slabý dôkaz.

## 12. Shift-left observability

Observability sa navrhuje pred produkciou.

Už počas vývoja definuj:

- structured log fields,
- request/correlation ID,
- metrics a labels,
- traces a spans,
- health/readiness semantics,
- SLI events,
- alertable failure states.

To neznamená simulovať produkciu lokálne. Znamená to vytvoriť aplikáciu, ktorú možno v produkcii pozorovať.

## 13. Platform engineering a golden paths

Shift-left funguje lepšie ako platformová capability než ako zoznam manuálnych povinností.

Golden path môže poskytovať:

- repository template,
- reusable CI pipeline,
- standard linter/type checker,
- dependency update automation,
- test environment provisioning,
- policy checks,
- artifact signing,
- observability bootstrap.

Developer dostáva bezpečný default bez ručného skladania každej kontroly.

## 14. Riziko lokálnych hooks

Pre-commit hook je dobrý pre rýchly feedback, ale nie je autoritatívny gate:

- používateľ ho môže obísť,
- nemusí byť nainštalovaný,
- lokálne prostredie môže byť odlišné,
- jeho výsledok nemusí byť auditovaný.

Autoritatívna kontrola musí existovať aj v dôveryhodnej CI vrstve.

## 15. Anti-patterny

### Všetko musí bežať pred commitom

Developer feedback sa stane príliš pomalý a kontroly sa obchádzajú.

### Shift-left ako presun práce na developerov

Bez tooling-u, dokumentácie a supportu rastie kognitívna záťaž.

### Stopercentné blokovanie findings

Low-confidence scanner paralyzuje delivery a vytvorí kultúru výnimiek.

### Fake production lokálne

Komplexná lokálna simulácia môže byť drahá a stále nereprezentatívna.

### Skorý test nahrádza produkčnú validáciu

Nie všetky failure modes možno reprodukovať pred deploymentom.

## 16. Metriky

Sleduj napríklad:

- čas do prvého užitočného feedbacku,
- median/p95 pipeline duration,
- failure stage distribution,
- defect escape rate,
- false-positive rate,
- local-to-CI mismatch rate,
- mean time to repair broken checks,
- počet a vek výnimiek,
- podiel failures zachytených pred merge.

Počet spustených scannerov nie je cieľová metrika.

## 17. Rozhodovací rámec

Pre každú kontrolu:

1. Aké riziko pokrýva?
2. Aký je najskorší bod s dostatočnou fidelity?
3. Aký je runtime a maintenance cost?
4. Aká je false-positive/false-negative charakteristika?
5. Je failure reprodukovateľný lokálne?
6. Je kontrola blocking alebo advisory?
7. Kto ju vlastní?
8. Ako funguje exception a expiry?
9. Čo ostáva overiť neskôr?
10. Aký dôkaz sa uchová?

## 18. Kontrolné otázky

1. Čo presne znamená shift-left?
2. Prečo neznamená presun všetkých testov lokálne?
3. Ktoré kontroly patria už do requirements a dizajnu?
4. Ako vyhodnotíš ekonomiku kontroly?
5. Prečo pre-commit hook nie je autoritatívny gate?
6. Ako shift-left súvisí s test selection?
7. Ako má vyzerať security shift-left bez zahltenia findings?
8. Prečo IaC plan nie je runtime dôkaz?
9. Ako shift-left podporuje observability?
10. Čo musí zostať pre shift-right?

## Glossary impact

Relevantné pojmy: shift-left, early feedback, golden path, affected-project detection, test impact analysis, secure default, pre-commit hook, developer feedback loop a policy guardrail.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Flaky tests a test data](flaky-tests-and-test-data.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Shift-right →](shift-right.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
