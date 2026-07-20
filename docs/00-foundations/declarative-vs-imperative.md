# Declarative vs. Imperative Approach

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Automation Mindset](automation-mindset.md)
- Súvisiace témy: idempotencia, desired state, reconciliation, Infrastructure as Code, Kubernetes, Ansible

## 1. Definícia

**Imperatívny prístup** opisuje konkrétne kroky, ktoré má systém vykonať. **Deklaratívny prístup** opisuje výsledný stav, ktorý má systém dosiahnuť, pričom mechanizmus vykonania rieši príslušný nástroj alebo controller.

```text
Imperatívne: Urob A, potom B, potom C.
Deklaratívne: Výsledok má vyzerať takto.
```

## 2. Problém, ktorý riešia

Oba prístupy sú spôsoby riadenia zmeny. Rozdiel je v tom, kde sa nachádza rozhodovanie o postupe:

- pri imperatívnom prístupe je postup explicitne v skripte alebo v príkazoch,
- pri deklaratívnom prístupe nástroj porovná požadovaný a aktuálny stav a vypočíta potrebné operácie.

Deklaratívny model je vhodný najmä tam, kde potrebujeme opakovateľnosť, detekciu driftu, auditovateľnosť a konvergenciu k známemu stavu.

## 3. Mentálny model

```text
Imperatívny model
operátor → zoznam príkazov → systém

Deklaratívny model
požadovaný stav → porovnanie → plán zmien → systém
                         ↑               ↓
                         └─ aktuálny stav ┘
```

Imperatívny skript vie, **čo má vykonať**. Deklaratívny engine vie, **aký stav má platiť**.

## 4. Imperatívny príklad

```bash
aws ec2 run-instances ...
aws ec2 create-tags ...
aws elbv2 register-targets ...
```

Poradie je súčasťou postupu. Autor musí riešiť:

- či resource už existuje,
- čo sa stane pri prerušení uprostred vykonávania,
- ako sa pokračuje po chybe,
- ako sa zistí rozdiel medzi očakávaným a reálnym stavom,
- ako sa zmena vráti späť.

## 5. Deklaratívny príklad

```hcl
resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = "t3.micro"

  tags = {
    Name = "web"
  }
}
```

Terraform načíta konfiguráciu, providerom zistí aktuálny stav, vytvorí dependency graph a pripraví plán operácií potrebných na dosiahnutie požadovaného výsledku.

## 6. Kubernetes príklad

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.27
```

Manifest nehovorí:

1. vytvor tri procesy,
2. vyber nodes,
3. prideľ IP adresy,
4. reštartuj zlyhaný proces.

Deklaruje tri repliky. Kubernetes controllers priebežne pracujú na tom, aby observed state zodpovedal desired state.

## 7. Deklaratívne neznamená „bez poradia“

Aj deklaratívny systém musí vykonať konkrétne operácie v určitom poradí. Rozdiel je v tom, že poradie odvodzuje engine zo závislostí a stavu namiesto toho, aby ho používateľ kompletne naprogramoval.

Terraform napríklad vytvorí dependency graph. Kubernetes používa viacero nezávislých reconciliation loops. Deklarácia teda neodstraňuje procedurálne vykonanie; presúva jeho riadenie do platformy.

## 8. Deklaratívne neznamená automaticky idempotentné

Deklaratívny jazyk môže obsahovať resources alebo hooks s nebezpečnými side effects. Naopak dobre napísaný imperatívny skript môže byť idempotentný.

Tieto osi treba oddeľovať:

```text
Ako opisujeme zámer: deklaratívne / imperatívne
Ako sa správa opakovanie: idempotentne / ne-idempotentne
```

## 9. Kedy je vhodný imperatívny prístup

Imperatívny prístup je vhodný pri:

- jednorazovej diagnostike,
- procedurálnych dátových migráciách,
- explicitných recovery krokoch,
- sekvenciách, kde každý krok závisí od výstupu predchádzajúceho,
- algoritmoch a transformáciách, ktoré sa prirodzene opisujú ako postup.

Problém nie je imperatívnosť sama. Problém vzniká, keď sa dlhodobý stav infraštruktúry spravuje iba neauditovanými príkazmi.

## 10. Kedy je vhodný deklaratívny prístup

Deklaratívny prístup je silný pri:

- Infrastructure as Code,
- Kubernetes resources,
- GitOps,
- policy konfigurácii,
- opakovanej konfigurácii veľkého počtu systémov,
- správe stavu, ktorý sa má priebežne udržiavať.

## 11. Trade-offs

| Vlastnosť | Imperatívny | Deklaratívny |
|---|---|---|
| Kontrola krokov | Priama | Delegovaná enginu |
| Čitateľnosť výsledného zámeru | Závisí od skriptu | Zvyčajne vysoká |
| Opakovanie | Treba explicitne ošetriť | Často prirodzená vlastnosť modelu |
| Drift detection | Treba doprogramovať | Často súčasť nástroja |
| Debugging | Viditeľná sekvencia krokov | Treba rozumieť plánovaču/controllerom |
| Flexibilita procedúry | Vysoká | Obmedzená modelom nástroja |

## 12. Časté omyly

### „Deklaratívny systém vždy sám opraví drift“

Nie. Terraform vykonáva reconciliation iba pri `plan/apply`. Kubernetes controllers bežia priebežne. Frekvencia a mechanizmus reconciliation závisia od konkrétneho nástroja.

### „YAML je deklaratívny“

YAML je iba dátový formát. Deklaratívnosť vzniká zo sémantiky systému, ktorý YAML interpretuje.

### „Imperatívne príkazy nemajú miesto v DevOps“

Majú. Diagnostika, migrácie a recovery sú často procedurálne. Dôležité je vedieť, ktoré operácie menia dlhodobý stav a ako sa auditujú.

## 13. Praktické posúdenie

Pri návrhu automatizácie si polož otázky:

1. Potrebujem opísať cieľ alebo presnú procedúru?
2. Existuje authoritative source of truth?
3. Ako systém zistí aktuálny stav?
4. Ako sa správa pri opakovanom spustení?
5. Kto rieši drift?
6. Čo sa stane pri čiastočnom zlyhaní?

## 14. Kontrolné otázky

1. Kde sa pri deklaratívnom modeli nachádza logika rozhodujúca o vykonaných krokoch?
2. Prečo samotný YAML nerobí systém deklaratívnym?
3. Prečo môže byť imperatívny skript idempotentný?
4. Aký je rozdiel medzi Terraform `apply` a kontinuálnou Kubernetes reconciliation loop?
5. Ktorý prístup by si zvolil pre jednorazovú databázovú migráciu a prečo?

## 15. Zhrnutie

Imperatívny model opisuje cestu. Deklaratívny model opisuje cieľ. Moderné DevOps platformy často používajú deklaratívne rozhranie, ale pod ním stále vykonávajú imperatívne operácie. Správna voľba závisí od typu problému, požadovanej opakovateľnosti a spôsobu riadenia stavu.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Automation mindset](automation-mindset.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Idempotencia →](idempotency.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
