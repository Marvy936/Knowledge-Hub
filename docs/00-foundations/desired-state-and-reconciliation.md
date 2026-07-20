# Desired State and Reconciliation

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Declarative vs. Imperative Approach](declarative-vs-imperative.md), [Idempotency](idempotency.md)
- Súvisiace témy: Kubernetes controllers, Terraform state, GitOps, drift, control loops

## 1. Definícia

**Desired state** je požadovaný stav systému. **Observed state** je stav, ktorý systém aktuálne pozoruje. **Reconciliation** je proces porovnávania týchto stavov a vykonávania krokov, ktoré majú rozdiel odstrániť.

```text
Desired state - Observed state = Difference
Difference → reconciliation action
```

## 2. Problém, ktorý rieši

Reálne systémy sa od požadovaného stavu odchyľujú:

- proces zlyhá,
- node vypadne,
- používateľ vykoná manuálnu zmenu,
- externé API odmietne operáciu,
- resource sa vytvorí iba čiastočne,
- konfigurácia sa zmení mimo source of truth.

Jednorazový deployment nevie garantovať, že stav zostane správny. Reconciliation vytvára mechanizmus, ktorý odchýlku opakovane zisťuje a opravuje.

## 3. Mentálny model regulačnej slučky

```text
              ┌────────────────────────────┐
              │                            │
Desired state │    porovnanie stavov       │ Observed state
      ───────→│                            │←──────────────
              └─────────────┬──────────────┘
                            │ rozdiel
                            ↓
                     vykonaj korekciu
                            │
                            └────→ systém
```

Controller nevykoná jednorazový zoznam krokov a neskončí. Slučku opakuje, pretože svet sa môže kedykoľvek zmeniť.

## 4. Kubernetes príklad

Deployment deklaruje:

```yaml
spec:
  replicas: 3
```

Observed state ukazuje iba dve dostupné repliky. ReplicaSet controller zistí rozdiel a vytvorí ďalší Pod.

```text
Desired replicas: 3
Observed replicas: 2
Action: create 1 Pod
```

Ak neskôr jeden Pod zanikne, reconciliation loop znovu zistí rozdiel. Kubernetes teda nespravuje iba vytvorenie objektu; priebežne sa snaží zachovať deklarovaný stav.

## 5. Viac controllerov

Kubernetes nepoužíva jeden centrálny algoritmus pre všetko. Viac controllerov sleduje rôzne typy resources:

- Deployment controller riadi ReplicaSets,
- ReplicaSet controller riadi počet Podov,
- scheduler priraďuje neschedulované Pody na nodes,
- kubelet zabezpečuje lokálny stav Podov a kontajnerov,
- EndpointSlice controller prepája Services s backendmi.

Každý controller má užšiu zodpovednosť. Celkové správanie vzniká skladaním viacerých control loops.

## 6. Level-based vs. edge-based spracovanie

Robustný controller sa orientuje podľa aktuálneho stavu, nie iba podľa udalosti, ktorá nastala.

```text
Edge-based: „prišla udalosť PodDeleted“
Level-based: „počet Podov je 2, desired je 3“
```

Ak sa udalosť stratí alebo controller reštartuje, level-based model stále vie z aktuálneho stavu odvodiť potrebnú akciu.

## 7. Terraform

Terraform tiež porovnáva konfiguráciu s aktuálnym stavom a zostavuje plán. Nie je však automaticky kontinuálny controller.

```text
terraform plan/apply
  ↓
načítaj konfiguráciu
  ↓
načítaj state a údaje od providerov
  ↓
porovnaj
  ↓
vykonaj plán
  ↓
proces skončí
```

Ďalšia reconciliation nastane až pri ďalšom spustení. GitOps alebo automatizačná platforma môže Terraform spúšťať periodicky, ale samotný model sa líši od nepretržite bežiacich Kubernetes controllerov.

## 8. GitOps

V GitOps modeli je Git authoritative source of truth:

```text
Git desired state
      ↓
GitOps controller
      ↓
cluster observed state
      ↓
diff a reconciliation
```

Ak niekto manuálne zmení resource v clustri, controller môže:

- zmenu automaticky vrátiť,
- iba oznámiť drift,
- čakať na manuálne schválenie.

Správanie závisí od nastavenej policy.

## 9. Source of truth

Reconciliation potrebuje jasnú odpoveď na otázku: ktorý stav je autoritatívny?

Možnosti môžu byť:

- Git repository,
- Kubernetes API object,
- Terraform configuration a state,
- CMDB,
- databáza aplikácie,
- externý control plane.

Ak viac systémov považuje svoj stav za autoritatívny a zapisuje do rovnakého resource, vzniká konflikt controllerov.

## 10. Drift

Drift je rozdiel medzi deklarovaným a reálnym stavom. Môže vzniknúť:

- manuálnym zásahom,
- neúspešnou automatizáciou,
- zmenou defaultných hodnôt providera,
- externým procesom,
- automatickým scalingom,
- zánikom alebo degradáciou resource.

Nie každý rozdiel je nežiaduci. Reconciliation musí vedieť, ktoré polia vlastní a ktoré spravuje iný controller.

## 11. Convergence

Dobrý reconciliation proces má konvergovať:

```text
každá iterácia → systém bližšie k desired state
```

Ak controller stav neustále mení tam a späť, vzniká flapping. Príčiny môžu byť:

- dva controllery vlastnia rovnakú hodnotu,
- desired state nie je realizovateľný,
- controller používa nestabilné vstupy,
- porovnanie nesprávne vyhodnocuje ekvivalentné hodnoty,
- externý systém opakovane vracia zmenu.

## 12. Eventual consistency

Reconciliation často poskytuje eventual consistency. Po deklarovaní zmeny nemusí byť stav okamžite dosiahnutý.

```text
Accepted desired state ≠ okamžite ready runtime state
```

Preto systémy oddeľujú:

- `spec` alebo intent,
- `status` alebo pozorovaný výsledok,
- conditions a events vysvetľujúce priebeh.

## 13. Failure handling

Controller musí riešiť zlyhanie bez agresívneho nekonečného opakovania. Typické mechanizmy:

- retry,
- exponential backoff,
- rate limiting,
- idempotentné operácie,
- finalizers,
- stavové conditions,
- dead-letter alebo manuálny zásah pri neobnoviteľnej chybe.

## 14. Časté omyly

### „Keď API prijalo manifest, resource už funguje“

API server prijal desired state. Runtime komponenty ho ešte len musia realizovať.

### „Reconciliation vždy vráti manuálnu zmenu“

Iba ak controller dané pole spravuje a jeho policy prikazuje self-healing.

### „Terraform a Kubernetes fungujú úplne rovnako“

Oba porovnávajú stav, ale Kubernetes používa kontinuálne control loops. Terraform typicky vykoná reconciliation počas explicitného behu.

### „Viac automatizácie znamená viac istoty“

Ak viac controllerov zapisuje do rovnakého stavu bez jasného ownershipu, automatizácia môže vytvoriť nestabilitu.

## 15. Diagnostika reconciliation systému

Pri probléme kontroluj:

1. Aký je desired state?
2. Aký je observed state?
3. Ktorý controller vlastní danú zmenu?
4. Je controller spustený a má oprávnenia?
5. Čo hovoria status conditions a events?
6. Je požadovaný stav vôbec realizovateľný?
7. Nezapisuje iný systém opačnú hodnotu?
8. Opakuje sa chyba s backoffom?

## 16. Kontrolné otázky

1. Aký je rozdiel medzi desired a observed state?
2. Prečo je level-based controller robustnejší než spracovanie založené iba na udalostiach?
3. Prečo prijatie objektu API serverom negarantuje funkčný runtime stav?
4. Ako sa líši Terraform reconciliation od Kubernetes controller loop?
5. Čo môže spôsobiť flapping medzi dvoma stavmi?
6. Prečo je jasný source of truth kritický?

## 17. Zhrnutie

Desired state vyjadruje zámer, observed state realitu a reconciliation mechanizmus medzi nimi. Tento model je základom Kubernetes, GitOps a mnohých declarative platforiem. Spoľahlivosť závisí od idempotencie, jasného ownershipu, konvergencie a dobre pozorovateľného statusu.