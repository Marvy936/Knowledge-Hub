# Automation Mindset

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Continuous Improvement](continuous-improvement.md), [Ownership Mindset](ownership-mindset.md)
- Súvisiace témy: idempotencia, Infrastructure as Code, CI/CD, scripting, platform engineering, toil

## 1. Definícia

Automation mindset je spôsob uvažovania, pri ktorom sa opakovateľná technická alebo procesná práca navrhuje tak, aby bola vykonateľná konzistentne, auditovateľne a s minimálnou závislosťou od manuálneho zásahu.

Neznamená automatizovať všetko. Znamená systematicky rozlišovať, čo má vykonávať človek, čo stroj a kde je potrebná kontrolovaná spolupráca oboch.

## 2. Problém manuálnych procesov

Manuálny proces býva:

- pomalší,
- variabilný,
- ťažšie auditovateľný,
- závislý od individuálnej pamäte,
- náchylný na preskočenie krokov,
- náročný na škálovanie.

Príklad manuálneho deploymentu:

```text
Prihlásiť sa na server
→ stiahnuť balík
→ upraviť konfiguráciu
→ reštartovať službu
→ skontrolovať log
```

Aj keď je postup zdokumentovaný, výsledok závisí od správneho vykonania každého kroku a od aktuálneho stavu servera.

## 3. Mentálny model

Automatizácia premieňa implicitné ľudské know-how na explicitný vykonateľný systém:

```text
Opakovaná manuálna činnosť
  ↓
Pochopenie vstupov, výstupov a failure modes
  ↓
Štandardizácia procesu
  ↓
Automatizovaná implementácia
  ↓
Validácia, telemetry a guardrails
  ↓
Priebežná údržba
```

Najprv treba proces pochopiť a zjednodušiť. Automatizovať nepochopený chaos znamená reprodukovať chaos rýchlejšie.

## 4. Čo je vhodné automatizovať

Silný kandidát má viacero z týchto vlastností:

- vykonáva sa často,
- má stabilné pravidlá,
- je náchylný na ľudskú chybu,
- spotrebúva významný čas,
- potrebuje audit trail,
- musí byť konzistentný medzi prostrediami,
- jeho chyba má vysoký dopad,
- jeho výsledok sa dá automaticky overiť.

Príklady:

- build a test,
- provisioning infraštruktúry,
- deployment,
- rotácia certifikátov,
- backup verification,
- policy validation,
- vytváranie štandardných prostredí,
- dependency scanning.

## 5. Čo nemusí byť vhodné automatizovať

Automatizácia môže byť nevhodná, ak:

- úloha je jednorazová,
- pravidlá sa často menia,
- rozhodnutie vyžaduje vysoký kontext,
- cena implementácie a údržby prevyšuje úsporu,
- neexistuje spôsob bezpečného overenia výsledku,
- automatizácia by zvýšila blast radius chyby.

Jednorazová migrácia môže stále potrebovať skript kvôli opakovateľnosti a auditu, ale nemusí z nej vzniknúť všeobecná platforma.

## 6. Cost model

Automatizácia má počiatočné aj priebežné náklady:

```text
Celková cena automatizácie =
analýza + implementácia + testovanie + prevádzka + údržba + incidenty
```

Manuálny proces má cenu:

```text
Celková manuálna cena =
frekvencia × čas × počet ľudí + cena chýb + koordinácia
```

Rozhodnutie nemá stáť iba na tom, či sa dá úloha skriptovať. Treba porovnať dlhodobý systémový dopad.

## 7. Úrovne automatizácie

### Dokumentovaný manuálny proces

Prvý krok k štandardizácii. Stále závisí od človeka.

### Skript

Automatizuje konkrétnu sekvenciu, často pre jeden tím alebo prostredie.

### Pipeline

Spája viacero automatizovaných kontrol a krokov do riadeného toku.

### Reusable component

Modul, template alebo shared workflow používaný viacerými tímami.

### Self-service platform capability

Používateľ deklaruje potrebu a platforma bezpečne vykoná komplexný proces.

Nie každá automatizácia musí dosiahnuť platformovú úroveň. Abstrakcia má zodpovedať reálnej opakovateľnosti.

## 8. Declarative a imperative automatizácia

### Imperative

Opisuje presnú sekvenciu krokov:

```text
vytvor sieť
vytvor subnet
vytvor VM
nainštaluj balík
spusti službu
```

### Declarative

Opisuje požadovaný výsledný stav:

```text
Má existovať sieť, subnet, VM a spustená služba.
```

Deklaratívny systém potrebuje mechanizmus, ktorý porovná desired state s observed state a vykoná potrebnú korekciu.

Imperatívny prístup poskytuje presnú kontrolu toku. Deklaratívny prístup lepšie podporuje reconciliation, drift detection a opakované vykonanie.

## 9. Idempotencia

Idempotentná operácia vedie pri opakovanom vykonaní s rovnakým vstupom k rovnakému výslednému stavu.

```text
Prvé vykonanie: vytvorí používateľa.
Druhé vykonanie: zistí, že používateľ existuje, a nezlyhá ani nevytvorí duplikát.
```

Idempotencia je dôležitá, pretože distribuované systémy, pipeline a konfiguračné nástroje musia často bezpečne opakovať operáciu po timeout-e alebo čiastočnom zlyhaní.

## 10. Error handling

Automatizácia musí explicitne riešiť:

- neplatné vstupy,
- timeout,
- čiastočný úspech,
- retry,
- rollback alebo compensating action,
- duplicitné vykonanie,
- nedostupnú závislosť,
- nedostatok oprávnení,
- bezpečné ukončenie.

Happy-path skript bez failure modelu nie je produkčná automatizácia.

## 11. Retry a bezpečnosť opakovania

Retry má význam iba pri dočasnom zlyhaní.

Vhodné:

- krátkodobá nedostupnosť API,
- rate limit s backoff,
- transient network error.

Nevhodné:

- neplatná konfigurácia,
- chýbajúce oprávnenie,
- syntax error,
- invariant violation.

Slepé retry môže znásobiť škodu alebo zakryť root cause. Preto treba kombinovať retry limit, exponential backoff, jitter a idempotentné operácie.

## 12. Guardrails

Automatizácia zvyšuje rýchlosť aj blast radius. Potrebuje ochranné mechanizmy:

- input validation,
- dry-run alebo plan,
- approval pre vysokorizikové operácie,
- least privilege,
- environment protection,
- policy as code,
- rate limits,
- canary alebo staged rollout,
- audit log,
- kill switch.

Cieľom approval nie je manuálne potvrdiť každý krok. Má chrániť konkrétne rizikové hranice.

## 13. Human in the loop

Niektoré procesy majú automatizovanú exekúciu, ale ľudské rozhodnutie:

```text
Automatizácia vytvorí plan
→ človek posúdi riziko
→ schváli
→ systém vykoná apply
→ systém automaticky overí výsledok
```

Dôležité je, aby človek dostal kvalitný kontext. Approval bez pochopenia diffu je iba formálny gate.

## 14. Observability automatizácie

Automatizovaný proces musí byť pozorovateľný:

- jednoznačný run ID,
- štruktúrované logy,
- status jednotlivých krokov,
- trvanie,
- retry count,
- výsledné artefakty,
- auditovaný autor a vstupy,
- metriky úspešnosti a zlyhania.

Ak automatizácia zlyhá bez vysvetlenia, presúva toil z exekúcie do diagnostiky.

## 15. Praktický príklad: provisioning prostredia

### Manuálny stav

Tím otvorí ticket a čaká dva dni. Administrátor vytvorí VM, sieťové pravidlá a účty podľa wiki.

### Prvý krok

Vytvoriť štandardný checklist a odstrániť nepotrebné varianty.

### Automatizácia

```text
Git request
→ validácia parametrov
→ Terraform plan
→ policy checks
→ approval pri produkcii
→ apply
→ konfigurácia cez Ansible
→ smoke test
→ zápis výsledku do inventory
```

### Výsledok

Automatizácia znižuje waiting time, variabilitu a manuálnu prácu. Jej kvalita však závisí od testov, state managementu, secrets a ownershipu.

## 16. Build vs. buy vs. platform

Pred vytvorením vlastnej automatizácie treba zvážiť:

- existujúcu schopnosť nástroja,
- cloud managed service,
- open-source riešenie,
- interný shared component,
- jednorazový skript.

Vlastná platforma vytvára dlhodobý produkt, ktorý potrebuje roadmapu, support, security a lifecycle. Nemá vzniknúť iba preto, že tím vie programovať.

## 17. Anti-patterny

### Automatizácia zlého procesu

Komplexný approval workflow sa prepisuje do pipeline bez otázky, či sú všetky schválenia potrebné.

### Skript bez vlastníka

Kritická automatizácia existuje v osobnom adresári a nikto nevie, ako funguje.

### Premature abstraction

Jednorazový use case sa zmení na univerzálny framework s vysokou cenou údržby.

### Hidden manual step

Pipeline vyzerá automatizovane, ale závisí od ručnej úpravy mimo Gitu.

### Automation sprawl

Viacero tímov vytvorí rozdielne skripty na rovnaký problém bez štandardu a lifecycle.

### Success without verification

Proces skončí exit code 0, ale neoverí skutočný stav cieľového systému.

## 18. Kontrolné otázky

1. Prečo automatizácia nepochopeného procesu môže situáciu zhoršiť?
2. Ktoré vlastnosti robia úlohu vhodnou na automatizáciu?
3. Aký je rozdiel medzi skriptom a platform capability?
4. Prečo je idempotencia dôležitá pri retry?
5. Kedy je human approval hodnotný a kedy iba formálny?
6. Aké telemetry má produkčná automatizácia poskytovať?

## 19. Zhrnutie

- Automatizovať treba stabilnú, opakovanú a hodnotnú prácu.
- Najprv sa proces chápe a štandardizuje, potom automatizuje.
- Produkčná automatizácia potrebuje error handling, idempotenciu, guardrails a observability.
- Nie každá automatizácia má byť univerzálna platforma.
- Cieľom je znižovať toil a variabilitu bez nekontrolovaného rastu blast radiusu.