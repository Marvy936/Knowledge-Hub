# Idempotency

Idempotencia znamená, že opakované vykonanie tej istej logickej operácie má po prvom úspešnom effecte rovnaký relevantný výsledný stav. Neznamená, že request sa vykoná iba raz, že odpoveď bude vždy byte-identická ani že operácia nemá žiadne vedľajšie effects. Rozhodujúce je, ako systém identifikuje jednu logical operation a ktorý effect považuje za autoritatívny.

```text
stable operation identity
+ semantic request fingerprint
+ atomic claim alebo existing-result lookup
→ jeden authoritative effect
→ opakované requesty vracajú kompatibilný outcome
```

Najväčšiu hodnotu má idempotencia pri retries a unknown outcomes. Klient môže stratiť odpoveď po tom, čo server commitol platbu. Blind retry s novým identifierom môže vytvoriť druhý effect; retry s rovnakým keyom umožní serveru nájsť pôvodnú operáciu. Samotný key však nestačí, ak sa dá znovu použiť s iným payloadom, ak vyprší skôr než retry window alebo ak claim a business write nie sú atómové.

Idempotentný API contract musí preto definovať scope identity, retention, concurrency, conflict behavior, response replay a reconciliation s externými systémami. Test zahŕňa paralelný duplicate, retry po stratenej odpovedi, rovnaký key s odlišným payloadom a opakovanie po recovery.

## 1. Definícia

Operácia je **idempotentná**, ak jej opakované vykonanie s rovnakým logickým vstupom vedie k rovnakému pozorovateľnému výslednému stavu ako jedno vykonanie. Prvé vykonanie môže systém zmeniť, no ďalšie opakovania nesmú vytvárať ďalšie neželané side effects.

Formálny zápis `f(f(x)) = f(x)` zachytáva základnú vlastnosť, ale pri distribuovaných systémoch treba vždy určiť aj scope pozorovania. Operácia môže byť idempotentná voči databázovému záznamu a súčasne ne-idempotentná voči odoslaným e-mailom alebo audit eventom.

## 2. Prečo je idempotencia potrebná

Klient často nevie, či predchádzajúci pokus neuspel, alebo či server operáciu vykonal a iba sa stratila odpoveď. Timeout preto nevytvára dôkaz neúspechu; vytvára **neistý výsledok**, pri ktorom je retry bezpečný iba vtedy, keď systém rozpozná opakovanie.

Idempotencia chráni najmä tieto situácie:

- **Network timeout —** server mohol zmenu dokončiť, hoci klient odpoveď nedostal; opakovanie nesmie vytvoriť druhý resource alebo druhú platbu.
- **At-least-once delivery —** message broker môže správu doručiť viackrát, preto consumer potrebuje rozpoznať už spracované event ID.
- **Pipeline rerun —** job sa môže spustiť po páde runnera znova; ďalší run má dokončiť alebo potvrdiť požadovaný stav, nie duplikovať predchádzajúce kroky.
- **Controller reconciliation —** controller opakovane vyhodnocuje ten istý objekt; každá iterácia musí bezpečne konvergovať k desired state-u.
- **Čiastočný workflow failure —** niektoré kroky už mohli mať side effect, kým neskorší krok zlyhal; retry musí vedieť pokračovať z reálneho stavu.

## 3. Mentálny model: intent, identity, state a result

Idempotentný návrh potrebuje viac než kontrolu „existuje alebo neexistuje“. Musí spojiť stabilnú identity operácie, požadovaný intent, autoritatívny state a uložený výsledok prvého spracovania.

```text
logical operation identity + normalized input
→ lookup existujúceho výsledku alebo state-u
→ vykonanie iba chýbajúcej zmeny
→ atómové uloženie výsledku
→ rovnaká odpoveď pri retry
```

Bez stabilnej identity systém nevie odlíšiť retry od novej legitímnej požiadavky. Bez uloženého výsledku zase môže vedieť, že operácia prebehla, ale nemusí vedieť klientovi reprodukovať pôvodnú odpoveď.

## 4. Jednoduchý stavový príklad

Požiadavka „adresár `/opt/app` má existovať“ sa prirodzene opisuje stavom. Prvé vykonanie adresár vytvorí a ďalšie vykonania iba overia, že požadovaný stav už platí.

```text
prvý run  → adresár neexistuje → vytvorí sa
ďalší run → adresár existuje    → stav sa nemení
```

Operácia „pridaj riadok na koniec súboru“ má inú semantiku. Každé opakovanie vytvára ďalší záznam, preto nie je idempotentná, pokiaľ duplicity tvoria legitímnu súčasť požadovaného výsledku.

## 5. Check-then-act a race condition

Bežný pokus o idempotenciu najprv skontroluje stav a potom vykoná zmenu. Tento pattern však nie je bezpečný pri concurrency, pretože dva workers môžu súčasne zistiť, že záznam neexistuje, a oba ho vytvoriť.

```text
worker A: lookup → nič
worker B: lookup → nič
worker A: create
worker B: create → duplicita
```

Kontrola a zápis preto potrebujú databázový unique constraint, compare-and-swap, conditional write, transakciu alebo iný atómový mechanizmus. Aplikačná kontrola bez storage-level invariantu znižuje pravdepodobnosť duplicity, ale negarantuje idempotenciu.

## 6. Shell a configuration management

Príkaz `echo "server 10.0.0.10" >> file` vždy pridá nový riadok a jeho výsledok závisí od počtu vykonaní. Kontrola cez `grep` je lepšia, ale stále môže mať race condition a nemusí riešiť staré alebo konfliktné hodnoty.

Robustnejší configuration-management model spravuje celý deklarovaný blok alebo celý súbor. Nástroj potom vie porovnať observed content s požadovaným contentom, ukázať diff a vykonať iba potrebnú korekciu.

```yaml
- name: Ensure nginx is installed
  ansible.builtin.package:
    name: nginx
    state: present
```

Špecializovaný Ansible modul pozná resource semantics a vie oznámiť, či nastala zmena. Všeobecný shell task môže byť technicky opakovateľný, no orchestrator z neho často nevie spoľahlivo odvodiť desired state, changed status ani recovery behavior.

## 7. Terraform a Kubernetes

Terraform porovnáva konfiguráciu, recorded state a dáta načítané providerom. Keď všetky tri pohľady zodpovedajú požadovanému výsledku, nový plan nemá obsahovať mutáciu; idempotencia však závisí od správnej implementácie providera a stabilnej identity resource-u.

Kubernetes controllery opakovane porovnávajú desired state objektov s observed state clusteru. Controller môže v každej iterácii vykonať reads a updates, ale nesmie pri každom reconcile vytvoriť nový externý resource bez väzby na stabilnú identity Kubernetes objektu.

Deklaratívne rozhranie teda podporuje idempotenciu, ale negarantuje ju automaticky. Custom controller, provisioner alebo hook môže mať ne-idempotentný side effect aj v deklaratívnom systéme.

## 8. HTTP metódy a výsledný stav

HTTP označuje niektoré metódy ako idempotentné z pohľadu zamýšľanej semantiky, nie z pohľadu toho, že server pri opakovaní neurobí žiadnu internú prácu. Implementácia musí túto semantiku zachovať aj v prítomnosti retries, concurrency a downstream side effects.

- **`GET` —** má čítať reprezentáciu bez business mutácie; interné logging alebo cache updates nemenia zamýšľaný resource state.
- **`PUT` —** typicky nastavuje resource na konkrétnu reprezentáciu; opakovaný rovnaký request má ponechať rovnaký výsledný resource.
- **`DELETE` —** prvý request resource odstráni a ďalší ponechá stav „resource neexistuje“; HTTP status sa môže líšiť, no resource state ostáva rovnaký.
- **`POST` —** často vytvára novú serverom pridelenú identity alebo vykonáva command, preto potrebuje osobitný deduplication contract, ak má podporovať bezpečný retry.

Samotný názov metódy nie je ochrana. `PUT`, ktorý pri každom volaní odošle ďalšiu notifikáciu alebo vytvorí nový auditovaný business event, môže byť idempotentný pre resource a ne-idempotentný pre širší workflow.

## 9. Idempotency key

Pri operácii typu `POST /payments` klient vytvorí stabilný idempotency key pre jednu logickú platbu. Server key uloží spolu s fingerprintom requestu, stavom spracovania a výslednou odpoveďou.

```text
Idempotency-Key: order-8472-payment-1
```

Pri retry s rovnakým keyom a rovnakým payloadom server vráti pôvodný výsledok alebo pokračuje v tom istom spracovaní. Rovnaký key s iným payloadom musí byť odmietnutý ako conflict; inak by klient mohol omylom priradiť dve rozdielne intentions k jednej identity.

## 10. Scope a vlastníctvo keyu

Idempotency key musí mať jasný namespace. Key `123` môže byť unikátny pre jedného zákazníka, ale nie globálne, preto sa lookup často viaže na tenant, caller identity, endpoint a operation type.

Príliš široký scope môže spôsobiť falošné konflikty medzi nezávislými requests. Príliš úzky scope umožní rovnakému business action prejsť cez iný endpoint alebo identity a deduplication obísť.

## 11. Retention a expiry

Deduplication record sa nemôže vždy uchovávať navždy, no jeho odstránením sa starý retry môže opäť správať ako nový request. Retention preto musí byť dlhšia než maximálne realistické retry, redelivery a client-offline okno.

Pri finančnej alebo regulačne citlivej operácii môže byť business transaction ID trvalejšou ochranou než krátkodobá cache idempotency keyov. Expiry je súčasťou contractu a klient musí vedieť, čo sa po jej uplynutí stane.

## 12. In-progress, completed a failed state

Server potrebuje rozlišovať request, ktorý ešte nevidel, request práve spracovávaný a request s uloženým výsledkom. Bez `in-progress` state-u môžu dva súbežné requests s rovnakým keyom vykonať side effect skôr, než sa uloží finálny result.

```text
new → processing → completed
               ↘ recoverable failure
               ↘ terminal failure
```

Prechod do `processing` musí byť atómový. Pri páde workera je potrebné lease, timeout alebo recovery pravidlo, ktoré určí, či môže ďalší worker bezpečne pokračovať alebo musí najprv overiť downstream state.

## 13. Timeout po úspešnom side effecte

Najkritickejší scenár vzniká, keď downstream platbu vykoná, ale application zlyhá pred uložením výsledku. Retry potom nemôže slepo zavolať downstream znova ani slepo tvrdiť, že operácia uspela.

Riešením môže byť downstream idempotency key, query podľa stabilného transaction ID alebo reconciliation job, ktorý neurčitý stav overí. Lokálna idempotencia nestačí, ak ne-idempotentný downstream systém nemá spôsob lookupu alebo deduplikácie.

## 14. Workflow a čiastočný úspech

Workflow „vytvor VM → vytvor DNS → pošli notifikáciu“ nemá jednu atómovú transaction boundary. Každý krok preto potrebuje vlastnú stabilnú identity, zaznamenaný stav a pravidlo pokračovania po retry.

- **VM creation —** používa deterministic name alebo client token, aby opakovanie našlo už vytvorenú VM.
- **DNS record —** nastavuje konkrétnu hodnotu cez upsert, takže retry konverguje k rovnakému recordu.
- **Notification —** používa event ID alebo outbox record, aby sa rovnaká business udalosť neposlala nekontrolovane viackrát.
- **Compensation —** ak workflow nemožno dokončiť, explicitne určuje, či sa už vytvorená VM odstráni alebo ostane na neskoršie pokračovanie.

Idempotencia jednotlivých krokov je potrebná, ale sama negarantuje správnosť celého workflowu. Orchestrator musí vedieť, ktoré kroky boli potvrdené a ktorý business outcome sa považuje za dokončený.

## 15. Side effects a outbox pattern

Side effects ako e-mail, message publishing alebo spustenie externého jobu sa často vykonávajú mimo databázovej transakcie aplikácie. Pri zápise business state-u a následnom páde pred publishom sa event stratí; pri publishi a páde pred označením výsledku sa môže publikovať dvakrát.

Transactional outbox uloží business zmenu aj záznam na publikovanie v jednej databázovej transakcii. Samostatný publisher outbox opakovane číta a posiela, pričom consumer stále používa event ID, pretože transport môže zostať at-least-once.

## 16. Idempotent consumer

Consumer uloží identifier spracovanej správy alebo zapíše business invariant tak, aby opakované doručenie nevytvorilo ďalší efekt. Deduplication check a business update musia patriť do jednej transaction boundary alebo byť chránené unique constraintom.

Ak consumer najprv zapíše `processed=true` a až potom vykoná business zmenu, crash medzi krokmi môže správu navždy preskočiť. Ak poradie otočí bez atómovej transakcie, crash môže naopak vytvoriť duplicitný side effect.

## 17. Idempotencia, deterministickosť a read-only

Deterministickosť znamená, že rovnaký vstup vytvorí rovnaký výstup. Idempotencia znamená, že opakovanie jednej logickej operácie ďalej nemení definovaný výsledný stav; operácia pritom môže čítať čas, komunikovať so storage alebo vykonať internú prácu.

Read-only operácia stav nemení, zatiaľ čo idempotentná mutácia ho pri prvom vykonaní meniť môže. `DELETE` alebo nastavenie konfigurácie na konkrétnu hodnotu preto môže byť idempotentné bez toho, aby bolo read-only.

## 18. Idempotencia nie je exactly-once execution

Distribuovaný systém zvyčajne nevie lacno garantovať, že handler fyzicky prebehne presne raz. Vie však dosiahnuť **effectively-once outcome** tým, že retries a redeliveries rozpozná a ich výsledný business efekt deduplikuje.

Tvrdenie „exactly once“ treba vždy rozložiť na transport delivery, handler execution a business side effect. Broker môže garantovať transakčné spracovanie vo vlastnom scope-e, no externý e-mail alebo payment API môže stále vyžadovať samostatný idempotency contract.

## 19. Security hranice

Idempotency store ovplyvňuje authorization a data isolation. Útočník nesmie vedieť uhádnuť cudzí key a získať pôvodnú odpoveď, ani použiť rovnaký key na blokovanie legitímnej operácie iného tenanta.

Key lookup preto musí byť viazaný na autentizovaný principal alebo tenant a uložená odpoveď nesmie obísť aktuálne access pravidlá. Citlivý payload alebo response potrebuje rovnakú ochranu, retention a audit ako primárne business dáta.

## 20. Observability

Systém má rozlišovať nové spracovanie, deduplicated retry, conflict payload, stale key a recovery po uncertain outcome. Bez týchto signálov sa opakované requests môžu javiť ako bežný traffic a skryť network incident alebo chybný client retry loop.

Užitočné telemetry zahŕňajú dedup hit rate, počet in-progress konfliktov, vek pending operácií, downstream reconciliation failures a počet key-reuse conflictov. Alert sa má viazať na stuck alebo nejednoznačný business state, nie na samotnú existenciu retries.

## 21. End-to-end príklad platby

Klient vytvorí `payment_intent_id` a odošle ho ako idempotency key spolu s order ID a amountom. Server v jednej transakcii vytvorí processing record alebo nájde existujúci record a overí, že fingerprint requestu zodpovedá.

Server zavolá payment provider s rovnakou stabilnou identity. Ak response príde, uloží provider transaction ID a výsledok; ak nastane timeout, lookupne provider transaction podľa ID a až potom rozhodne, či pokračovať, vrátiť pending alebo retryovať.

```text
client key
→ atomic claim
→ provider call s rovnakou identity
→ persist result
→ retry vráti ten istý business outcome
```

Týmto modelom sa nepredstiera, že sieť nezlyháva. Neistota sa explicitne reprezentuje a recovery ju rieši pomocou autoritatívneho downstream state-u.

## 22. Troubleshooting

Pri duplicite najprv urči, či vznikli dve rozdielne logical identities alebo či deduplication zlyhala pre tú istú identity. Potom sleduj key scope, atomic claim, payload fingerprint, retention, downstream transaction ID a čas crashu.

- **Dve platby s rovnakým keyom —** over concurrent claim a unique constraint; samotný aplikačný lookup mohol mať race condition.
- **Retry vracia conflict —** porovnaj normalized payload; klient mohol znovu použiť key pre inú sumu alebo order.
- **Operácia ostala `processing` —** over lease expiry a downstream lookup; worker mohol zlyhať po vykonaní side effectu.
- **Duplicitná notifikácia —** over outbox event ID a consumer deduplication, nie iba idempotenciu primárneho API.
- **Starý retry vytvoril nový efekt —** retention okno bolo kratšie než reálne redelivery alebo offline-client okno.

## 23. Anti-patterny

### Úspešný exit code sa považuje za dôkaz

Exit code opisuje konkrétny pokus, nie výsledný business state. Druhý úspešný run mohol vytvoriť ďalší resource alebo opakovať nevratný side effect.

### Check-then-act bez storage invariantu

Aplikačná kontrola `if not exists` nie je atómová. Pri concurrency musí duplicite zabrániť unique constraint, conditional write alebo transakčný claim.

### Key bez payload fingerprintu

Rovnaký key použitý pre rozdielne vstupy nesmie ticho vrátiť starý výsledok. Systém potrebuje uložiť normalized request fingerprint a konflikt explicitne odmietnuť.

### Nekonečný retry pending operácie

Pending stav po uncertain outcome sa nemá riešiť slepým opakovaním. Najprv sa musí overiť autoritatívny downstream state alebo spustiť riadená reconciliation.

### Idempotentné API, ne-idempotentný vedľajší efekt

Resource môže mať správny stav, ale zákazník dostane tri e-maily alebo downstream tri jobs. Scope idempotencie musí zahŕňať všetky business-relevant side effects.

## 24. Kontrolné otázky

1. Prečo timeout neznamená, že operácia neprebehla?
2. Aký je rozdiel medzi logical operation identity a jednotlivým network requestom?
3. Prečo `check then create` bez unique constraintu nie je bezpečne idempotentné?
4. Čo musí server urobiť, keď rovnaký idempotency key príde s iným payloadom?
5. Ako retention deduplication záznamu ovplyvňuje bezpečnosť starých retries?
6. Prečo lokálna idempotencia nestačí pri ne-idempotentnom downstream payment API?
7. Ako transactional outbox rieši medzeru medzi business commitom a publishom eventu?
8. Prečo idempotencia neznamená exactly-once execution?
9. Ako navrhneš idempotent consumer bez race medzi business update a dedup recordom?
10. Ktoré telemetry odhalia stuck alebo nesprávne deduplikované operácie?

## 25. Zhrnutie

Idempotencia je contract bezpečného opakovania, nie iba vlastnosť syntaxe alebo HTTP metódy. Potrebuje stabilnú identity, správny scope, atómový claim, autoritatívny state, payload conflict rules, primeranú retention a explicitné riešenie všetkých side effects.

Najdôležitejší scenár je timeout po možnom úspechu. Kvalitný systém neistotu neskrýva; zaznamená ju, overí downstream stav a zabezpečí, aby retry viedol k jednému konzistentnému business výsledku.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Declarative vs. imperative prístup](declarative-vs-imperative.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Desired state a reconciliation →](desired-state-and-reconciliation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
