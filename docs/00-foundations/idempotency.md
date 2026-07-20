# Idempotency

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Declarative vs. Imperative Approach](declarative-vs-imperative.md)
- Súvisiace témy: retries, Ansible, Terraform, Kubernetes, APIs, configuration management

## 1. Definícia

Operácia je **idempotentná**, ak jej opakované vykonanie s rovnakým vstupom vedie k rovnakému výslednému stavu ako jedno vykonanie.

Formálne:

```text
f(f(x)) = f(x)
```

Idempotencia neznamená, že sa pri druhom spustení nič interne nevykoná. Znamená, že výsledný pozorovateľný stav sa ďalej nemení nežiaducim spôsobom.

## 2. Problém, ktorý rieši

Distribuované systémy a automatizácia musia počítať s:

- timeoutmi,
- prerušenými spojeniami,
- nejasným výsledkom predchádzajúceho pokusu,
- opakovaným spustením pipeline,
- retry mechanizmami,
- čiastočným zlyhaním.

Ak nevieme bezpečne zopakovať operáciu, každé opakovanie môže vytvoriť ďalší resource, duplicitnú platbu, opakovaný zápis alebo nepredvídateľný stav.

## 3. Mentálny model

```text
Požadovaný výsledok: adresár /opt/app existuje

Prvé spustenie  → adresár sa vytvorí
Druhé spustenie → adresár už existuje, výsledok zostáva rovnaký
Tretie spustenie → výsledok zostáva rovnaký
```

Kontrast:

```text
Prvé spustenie  → pridaj riadok do súboru
Druhé spustenie → pridaj rovnaký riadok znova
Tretie spustenie → pridaj ho tretíkrát
```

Druhá operácia nie je idempotentná, ak duplicity nie sú požadovaným stavom.

## 4. Shell príklad

Neidempotentné:

```bash
echo "server 10.0.0.10" >> /etc/app/servers.conf
```

Každé spustenie pridá ďalší riadok.

Idempotentnejšia verzia:

```bash
grep -qxF "server 10.0.0.10" /etc/app/servers.conf \
  || echo "server 10.0.0.10" >> /etc/app/servers.conf
```

Skript najprv overí stav a mutáciu vykoná iba vtedy, keď je potrebná.

Ešte robustnejší prístup je spravovať celý súbor zo šablóny, pretože výsledný obsah je explicitný a ľahšie auditovateľný.

## 5. Ansible príklad

```yaml
- name: Ensure nginx is installed
  ansible.builtin.package:
    name: nginx
    state: present
```

Modul nehovorí „spusti inštaláciu“. Hovorí „balík má byť prítomný“. Pri ďalšom spustení modul zistí, že stav už platí, a nevykoná zbytočnú zmenu.

Kontrastom je:

```yaml
- name: Install nginx manually
  ansible.builtin.shell: apt-get install -y nginx
```

Príkaz môže skončiť úspešne opakovane, ale Ansible nevie spoľahlivo modelovať, či sa stav zmenil. Použitie špecializovaného modulu poskytuje lepšiu idempotenciu aj observability.

## 6. Terraform a Kubernetes

Terraform sa snaží dosiahnuť stav deklarovaný v konfigurácii. Ak konfigurácia a reálny stav zodpovedajú, plán neobsahuje zmenu.

Kubernetes controllers opakovane porovnávajú desired state s observed state. Opakovaná reconciliation nemá vytvárať ďalšie nezávislé kópie mimo deklarovaného počtu.

V oboch prípadoch idempotencia závisí aj od implementácie providerov, controllerov a externých API.

## 7. Idempotencia a HTTP

HTTP metódy sa často rozlišujú podľa očakávanej idempotencie:

- `GET` má iba čítať,
- `PUT` typicky nahrádza resource konkrétnym stavom a má byť idempotentný,
- `DELETE` má byť idempotentný z pohľadu výsledného stavu,
- `POST` často vytvára nový resource a spravidla nie je idempotentný.

Praktická implementácia však musí túto vlastnosť naozaj zabezpečiť. Samotný názov metódy nestačí.

## 8. Idempotency key

Pri operáciách, ktoré prirodzene vytvárajú nový záznam, môže klient poslať jedinečný idempotency key:

```text
POST /payments
Idempotency-Key: order-8472-payment-1
```

Server uloží výsledok prvého spracovania. Ak príde retry s rovnakým kľúčom, neuskutoční platbu znova, ale vráti pôvodný výsledok.

Tento mechanizmus je dôležitý pri at-least-once delivery, kde správa alebo request môže byť doručený viackrát.

## 9. Idempotencia nie je to isté ako deterministickosť

Deterministická funkcia dáva pre rovnaký vstup rovnaký výstup. Idempotentná operácia môže pracovať so stavom, ale jej opakovanie už výsledný stav nemení.

```text
Deterministickosť: rovnaký vstup → rovnaký výstup
Idempotencia: opakovanie operácie → rovnaký výsledný stav
```

## 10. Idempotencia nie je to isté ako read-only

`DELETE` môže byť idempotentný, hoci pri prvom volaní systém mení. Druhé volanie už resource nenájde, ale výsledný stav „resource neexistuje“ zostáva rovnaký.

## 11. Čiastočné zlyhanie

Predstav si operáciu:

```text
1. vytvor VM,
2. vytvor DNS záznam,
3. pošli notifikáciu.
```

Ak proces zlyhá po kroku 1, retry nesmie vytvoriť druhú VM. Každý krok potrebuje:

- stabilný identifikátor,
- kontrolu existujúceho stavu,
- bezpečný retry mechanizmus,
- prípadne compensating action.

Idempotencia celej workflow je náročnejšia než idempotencia jedného príkazu.

## 12. Side effects

Najčastejšie problémy spôsobujú side effects:

- odoslanie e-mailu,
- vytvorenie ticketu,
- inkrementácia počítadla,
- finančná transakcia,
- publikovanie správy,
- spustenie externého jobu.

Tieto operácie potrebujú deduplication, stabilné event ID alebo explicitnú evidenciu spracovania.

## 13. Časté omyly

### „Príkaz skončil úspešne aj druhýkrát, takže je idempotentný“

Úspešný exit code nič nehovorí o výslednom stave. Operácia mohla vytvoriť duplicitu.

### „Deklaratívny nástroj je vždy idempotentný“

Nie automaticky. Provider alebo custom resource môže mať ne-idempotentné side effects.

### „Idempotencia znamená, že druhé spustenie je no-op“

Nie nevyhnutne. Systém môže čítať stav, obnoviť chýbajúcu časť alebo opätovne zapísať rovnakú hodnotu.

## 14. Praktický checklist

Pri návrhu operácie skontroluj:

1. Má request stabilný identifikátor?
2. Vieme zistiť, či už bol spracovaný?
3. Čo sa stane pri retry po timeoute?
4. Môžu vzniknúť duplicity?
5. Je kontrola a zápis atómová alebo môže vzniknúť race condition?
6. Ako dlho sa uchováva deduplication záznam?
7. Ktoré side effects sa nedajú jednoducho vrátiť späť?

## 15. Kontrolné otázky

1. Prečo `echo value >> file` typicky nie je idempotentné?
2. Ako idempotencia pomáha pri retry po timeoute?
3. Aký je rozdiel medzi idempotenciou a deterministickosťou?
4. Prečo môže byť `DELETE` idempotentný?
5. Ako by si zabránil dvojitému vytvoreniu platby pri opakovanom requeste?
6. Prečo je špecializovaný Ansible modul vhodnejší než všeobecný shell task?

## 16. Zhrnutie

Idempotencia robí opakovanie bezpečnejším. Je základom spoľahlivej automatizácie, retry mechanizmov, configuration managementu a reconciliation systémov. Nestačí kontrolovať, či operácia prebehla; treba kontrolovať, aký výsledný stav po nej zostal.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Declarative vs. imperative prístup](declarative-vs-imperative.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Desired state a reconciliation →](desired-state-and-reconciliation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
