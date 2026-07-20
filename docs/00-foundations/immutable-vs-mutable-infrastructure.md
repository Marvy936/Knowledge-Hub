# Immutable vs. Mutable Infrastructure

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Desired State and Reconciliation](desired-state-and-reconciliation.md)
- Súvisiace témy: images, configuration management, containers, deployments, rollback, drift

## 1. Definícia

**Mutable infrastructure** sa počas životnosti priebežne mení na mieste. **Immutable infrastructure** sa pri významnej zmene nevylepšuje priamo; vytvorí sa nová verzia resource a pôvodná verzia sa nahradí.

```text
Mutable:   existujúci server → patch → zmena konfigurácie → ďalší patch
Immutable: image v1 → vytvor nové instances v2 → presmeruj traffic → odstráň v1
```

Immutable neznamená fyzicky nezmeniteľné. Znamená, že prevádzkový model preferuje replacement pred in-place modification.

## 2. Problém, ktorý rieši immutable model

Dlhodobo menené servery akumulujú rozdiely:

- rôzne poradie patchov,
- manuálne zásahy,
- nezdokumentované konfigurácie,
- zvyšky starých verzií,
- odlišný runtime stav medzi nodes.

Tento configuration drift spôsobuje, že dva údajne rovnaké servery sa správajú rozdielne. Immutable model presúva konfiguráciu do reprodukovateľného build procesu.

## 3. Mutable workflow

```text
Vytvor VM
  ↓
Nainštaluj balíky
  ↓
Nasadzuj nové verzie aplikácie na tú istú VM
  ↓
Patchuj OS
  ↓
Upravuj konfiguráciu
  ↓
Rieš drift a históriu zmien
```

Výhoda je menšia potreba nahrádzať celý resource. Nevýhodou je rastúca závislosť od presnej histórie zmien.

## 4. Immutable workflow

```text
Source code + konfigurácia
          ↓
       build image
          ↓
        test image
          ↓
  vytvor nové resources
          ↓
 health checks / canary
          ↓
  presmeruj traffic
          ↓
 odstráň starú verziu
```

Artifact prechádzajúci prostrediami má stabilnú identitu. Produkcia nedostáva iný ručne upravený build než testovacie prostredie.

## 5. Príklad s VM image

Mutable model:

```text
SSH na server
apt upgrade
uprav config
reštartuj službu
```

Immutable model:

```text
Packer alebo image pipeline vytvorí AMI v2
Auto Scaling Group spustí nové instances
Load balancer overí health checks
staré instances sa ukončia
```

Zmena je súčasťou image build procesu, nie ručnej histórie konkrétneho servera.

## 6. Kontajnery

Kontajnerový image je typický immutable artifact. Bežiaci kontajner môže mať zapisovateľnú vrstvu, ale aplikácia by nemala závisieť od manuálnych úprav tejto vrstvy.

```text
Zlá oprava: exec do kontajnera a uprav súbor
Správny tok: uprav source alebo Dockerfile → build nový image → rollout
```

Ručná oprava zmizne pri reschedulingu a nevytvorí auditovateľný source of truth.

## 7. Kubernetes rollout

Deployment pri zmene image typicky vytvorí nové Pody a staré odstráni. Nemodifikuje bežiaci container filesystem tak, aby z neho vznikla nová aplikačná verzia.

To umožňuje:

- rolling update,
- canary,
- rollback na predchádzajúci image,
- konzistentné repliky,
- jednoduchšie horizontálne škálovanie.

## 8. Externý stav

Immutable compute musí oddeliť stav, ktorý má prežiť replacement:

- databázové dáta,
- persistent volumes,
- object storage,
- message queues,
- secrets,
- externé konfigurácie podľa zvoleného modelu.

Ak aplikácia ukladá kritické dáta iba na lokálny disk nahraditeľnej VM alebo Podu, replacement ich môže zničiť.

## 9. Rollback

Immutable model zjednodušuje rollback aplikačného artifactu:

```text
v2 zlyhá → presmeruj traffic späť na v1
```

Rollback však nie je automaticky jednoduchý pri:

- nekompatibilnej databázovej migrácii,
- zmene message formátu,
- externom side effecte,
- nevratnej transformácii dát.

Preto musí byť deployment a dátová migrácia navrhnutá ako jeden kompatibilný systém.

## 10. Patchovanie a bezpečnosť

Pri mutable modeli patchujeme existujúce stroje. Pri immutable modeli vytvoríme nový patched image a instances nahradíme.

Replacement model má výhodu reprodukovateľnosti, ale potrebuje:

- rýchlu build pipeline,
- inventory všetkých image verzií,
- automatický rollout,
- kontrolu, že staré resources naozaj zanikli,
- riešenie dlhodobo bežiacich alebo stateful komponentov.

## 11. Configuration management

Ansible a podobné nástroje sa často používajú na mutable infraštruktúru, ale môžu byť súčasťou immutable image build procesu.

```text
Ansible proti produkčnej VM → mutable configuration
Ansible počas buildovania image → immutable deployment artifact
```

Nástroj sám neurčuje architektonický model. Rozhodujúci je lifecycle resource.

## 12. Hybridný model

V praxi systémy často kombinujú oba prístupy:

- aplikačné kontajnery sa nahrádzajú immutable spôsobom,
- databáza sa upgraduje kontrolovaným mutable procesom,
- konfigurácia sa mení deklaratívne,
- emergency zásah môže byť imperatívny, ale musí sa následne preniesť do source of truth.

Nie všetko má rovnakú cenu replacementu.

## 13. Trade-offs

| Vlastnosť | Mutable | Immutable |
|---|---|---|
| Rýchla lokálna oprava | Jednoduchšia | Oprava vyžaduje nový artifact |
| Drift | Vyššie riziko | Nižšie pri správnom procese |
| Auditovateľnosť | Závisí od automatizácie | Build a rollout tvoria stopu |
| Rollback aplikácie | Často komplikovaný | Často návrat na starý artifact |
| Spotreba kapacity počas rollout | Nižšia | Dočasne vyššia |
| Stateful systémy | Prirodzenejšie | Potrebujú oddelenie dát a compute |
| Reprodukcia prostredia | Náročnejšia | Silná stránka modelu |

## 14. Anti-patterny

### Golden server

Jeden server sa roky ručne upravuje a následne slúži ako nezdokumentovaný vzor. Jeho stav sa nedá spoľahlivo reprodukovať.

### SSH hotfix bez spätného zápisu

Incident sa opraví priamo na serveri, ale zmena sa neprenesie do kódu, image alebo konfigurácie. Pri ďalšom replacement sa chyba vráti.

### `latest` bez identity artifactu

Immutable model stráca hodnotu, ak rovnaký tag ukazuje na meniaci sa obsah a nie je možné určiť, čo bolo reálne nasadené.

### Immutable compute so skrytými lokálnymi dátami

Resource sa považuje za nahraditeľný, ale aplikácia ukladá nenahradené dáta lokálne.

## 15. Rozhodovací checklist

1. Ktoré časti systému sú stateful?
2. Vieme resource automaticky reprodukovať?
3. Ako dlho trvá build a replacement?
4. Je artifact jednoznačne verziovaný?
5. Ako prebehne traffic switch?
6. Ako sa overí health novej verzie?
7. Sú dátové zmeny spätne kompatibilné?
8. Ako sa odstránia staré a zraniteľné resources?

## 16. Kontrolné otázky

1. Prečo immutable neznamená fyzicky read-only?
2. Ako immutable model znižuje configuration drift?
3. Prečo ručná úprava bežiaceho kontajnera nie je trvalá oprava?
4. Ktorý stav musí byť oddelený od nahraditeľného compute?
5. Prečo rollback image nemusí vyriešiť nekompatibilnú databázovú migráciu?
6. Ako možno Ansible použiť v mutable aj immutable modeli?

## 17. Zhrnutie

Mutable infraštruktúra sa vyvíja zmenami na mieste. Immutable infraštruktúra sa vyvíja nahrádzaním verziovaných resources. Immutable model znižuje drift a zlepšuje reprodukovateľnosť, ale vyžaduje automatizovaný build, rollout, externalizovaný stav a správne navrhnutú dátovú kompatibilitu.