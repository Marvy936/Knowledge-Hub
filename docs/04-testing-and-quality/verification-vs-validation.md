# Verification vs. validation

Verification a validation odpovedajú na dve rozdielne otázky o kvalite systému:

```text
Verification: Vytvorili sme systém správne podľa špecifikácie?
Validation: Vytvorili sme správny systém pre reálnu potrebu používateľa?
```

Obe sú potrebné. Produkt môže byť technicky bezchybný voči nesprávnej požiadavke alebo môže riešiť správny problém implementáciou, ktorá porušuje kontrakty a bezpečnostné pravidlá.

## 1. Verification

Verification porovnáva výsledok s explicitným očakávaním:

- požiadavkou,
- API kontraktom,
- návrhom,
- schémou,
- bezpečnostnou policy,
- technickou špecifikáciou,
- akceptačným kritériom.

Príklady:

- funkcia pre rovnaký vstup vracia očakávaný výstup,
- JSON response zodpovedá schéme,
- Terraform plan neotvára verejný prístup,
- kontajner nebeží ako root,
- deployment manifest používa povinné labels,
- databázová migrácia zachová constraints.

Verification je často dobre automatizovateľná, pretože očakávanie je možné zapísať ako executable rule.

## 2. Validation

Validation overuje, či systém v reálnom kontexte rieši zamýšľaný problém.

Príklady:

- používateľ dokáže dokončiť objednávku bez nejasných krokov,
- alert vedie operátora ku konkrétnej akcii,
- recovery proces obnoví službu v požadovanom čase,
- API semantics zodpovedajú potrebám consumerov,
- autoscaling drží používateľskú latency pri realistickom traffic profile,
- nový workflow skutočne znížil lead time a nie iba počet manuálnych kliknutí.

Validation môže zahŕňať automatizované testy, ale často potrebuje aj:

- používateľský výskum,
- acceptance testing,
- produkčné metriky,
- experiment,
- observability,
- feedback od stakeholderov,
- game day alebo disaster-recovery cvičenie.

## 3. Prečo sa pojmy zamieňajú

V bežnej reči sa slovo „validácia“ používa aj pre kontrolu formátu vstupu. Napríklad JSON Schema validation je technicky verification voči schéme.

Terminológia závisí od kontextu, preto je dôležité vždy pomenovať:

```text
Čo je objekt kontroly?
Voči čomu ho porovnávame?
Aké rozhodnutie výsledok podporuje?
```

## 4. Statická a dynamická kontrola

### Statická verification

Nevyžaduje spustenie systému:

- code review,
- compiler checks,
- type checking,
- linting,
- schema validation,
- policy-as-code,
- dependency a secret scanning,
- analýza Terraform planu.

### Dynamická verification

Vyžaduje vykonanie kódu alebo systému:

- unit tests,
- integration tests,
- API tests,
- load tests,
- runtime security tests,
- deployment smoke tests.

Statické a dynamické metódy sa dopĺňajú. Statická analýza môže odhaliť zakázaný pattern vo všetkých cestách kódu, zatiaľ čo dynamický test overí konkrétne runtime správanie a integráciu.

## 5. Requirement traceability

Test bez väzby na riziko alebo požiadavku môže vytvárať falošný pocit pokrytia.

Traceability prepája:

```text
business need
→ requirement
→ risk
→ control alebo design decision
→ test
→ dôkaz výsledku
```

Nie každá požiadavka potrebuje samostatný test case, ale kritické požiadavky musia mať identifikovateľný dôkaz.

Príklad:

```text
Požiadavka: používateľ nesmie vidieť dáta iného tenanta
Riziko: cross-tenant data exposure
Kontroly: tenant-scoped query, authorization policy
Testy: unit policy tests, integration DB tests, API security tests
Produkčný dôkaz: audit logs a anomaly detection
```

## 6. Test oracle

Test oracle je mechanizmus, ktorý rozhoduje, či je výsledok správny.

Možné oracles:

- presná očakávaná hodnota,
- invariant,
- schema,
- referenčná implementácia,
- snapshot,
- historický baseline,
- business rule,
- property-based assertion.

Slabý oracle kontroluje iba to, že operácia „nespadla“. Silný oracle overuje význam výsledku.

Príklad slabého assertion:

```text
HTTP status je 200
```

Silnejší assertion:

```text
status je 200,
response zodpovedá schéme,
objednávka má správnu cenu,
bola vytvorená presne jedna platobná operácia,
audit event obsahuje správnu identitu
```

## 7. False positive a false negative

### False positive

Test hlási problém, hoci systém je správny.

Dôsledky:

- strata dôvery v test suite,
- ignorovanie alertov,
- zbytočné blokovanie pipeline,
- manuálne reruny.

### False negative

Test prejde, hoci systém obsahuje chybu.

Dôsledky:

- chybný release,
- falošný pocit bezpečnosti,
- incident zachytený až používateľom.

Kvalita testu preto nie je iba jeho existencia, ale aj citlivosť, špecificita a stabilita.

## 8. Verification v CI a validation v produkcii

Zjednodušený model:

```text
pred commitom
→ lint, types, unit tests

v CI
→ build, integration, contract, security tests

v stagingu
→ E2E, acceptance, performance checks

pri deploymente
→ smoke, readiness, synthetic transaction

v produkcii
→ SLI/SLO, business metrics, user feedback, experiments
```

Validation sa nekončí pred deploymentom. Reálny traffic, dependencies a ľudské správanie vytvárajú podmienky, ktoré test environment nemusí reprodukovať.

## 9. Quality gates

Quality gate má blokovať zmenu iba vtedy, keď:

- kontroluje relevantné riziko,
- výsledok je dostatočne spoľahlivý,
- failure má jasného ownera,
- existuje diagnostický výstup,
- čas kontroly zodpovedá feedback potrebe,
- výnimka je auditovateľná.

Gate bez ownershipu alebo s chronickými false positives sa mení na rituál.

## 10. Infrastructure a operations kontext

Verification a validation platia aj mimo aplikačného kódu.

### Infrastructure verification

- syntax a schema manifestu,
- policy compliance,
- plánované resource changes,
- idempotencia,
- security groups,
- encryption settings,
- backup configuration.

### Infrastructure validation

- služba je dosiahnuteľná z povolených sietí,
- zakázaná cesta je skutočne blokovaná,
- failover funguje pod realistickým failure scenárom,
- backup je obnoviteľný,
- observability umožní diagnostiku,
- kapacita zodpovedá workloadu.

Existencia backup jobu je verification konfigurácie. Úspešný restore test je validation použiteľnosti backupu.

## 11. Typické anti-patterny

### Testovanie implementácie namiesto správania

Test je previazaný na interné method calls a rozbije sa pri bezpečnom refaktoringu.

### Akceptačné kritérium bez merateľného výsledku

„Systém má byť rýchly“ nevytvára testovateľný kontrakt.

### Produkčný monitoring ako náhrada testov

Observability zachytáva skutočné správanie, ale nemá byť prvým miestom, kde sa objaví predvídateľná chyba.

### Testy bez negatívnych scenárov

Happy path neoverí authorization failure, invalid input, timeout, retry ani partial failure.

### Compliance checkbox

Kontrola existuje iba preto, aby bol vyplnený formulár, bez overenia účinnosti kontroly.

## 12. Praktický rozhodovací rámec

Pre každú významnú zmenu sa opýtaj:

1. Aký používateľský alebo prevádzkový výsledok má zmena priniesť?
2. Aké explicitné kontrakty musí dodržať?
3. Aké failure modes sú najrizikovejšie?
4. Ktoré kontroly môžu byť statické?
5. Ktoré potrebujú runtime?
6. Aký oracle rozhodne o úspechu?
7. Kde sa test spustí, aby dal najrýchlejší užitočný feedback?
8. Čo ostáva overiť až v stagingu alebo produkcii?
9. Aký dôkaz treba uchovať?
10. Kto reaguje na failure?

## 13. Kontrolné otázky

1. Aký je rozdiel medzi verification a validation?
2. Prečo technicky správna implementácia nemusí byť správny produkt?
3. Aký je rozdiel medzi statickou a dynamickou verification?
4. Čo je test oracle?
5. Aký je rozdiel medzi false positive a false negative?
6. Prečo HTTP 200 nie je dostatočný dôkaz správnosti?
7. Ako traceability prepája požiadavku, riziko a test?
8. Prečo sa validation často musí rozšíriť do produkcie?
9. Aký je rozdiel medzi existenciou backupu a overeným restore procesom?
10. Kedy má kontrola fungovať ako blocking quality gate?

## Glossary impact

Relevantné pojmy: verification, validation, test oracle, requirement traceability, false positive, false negative, static analysis, dynamic testing a quality gate.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: YAML, JSON a regular expressions](../03-git-and-automation/yaml-json-regular-expressions.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Test pyramid →](test-pyramid.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
