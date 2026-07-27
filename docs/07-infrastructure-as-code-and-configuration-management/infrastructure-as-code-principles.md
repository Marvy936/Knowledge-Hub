# Infrastructure as Code principles

Infrastructure as Code (IaC) je change-control a reconciliation model nad vzdialeným systémom. Kód nepredstavuje infraštruktúru sám osebe. Predstavuje schválený **desired state**, ktorý sa musí spojiť so správnym toolchainom, vstupmi, state snapshotom, target identitou a remote observation, aby vznikol dôveryhodný plan a bezpečná mutation.

Táto kapitola používa jeden priebežný scenár: tím Atlas Payments pripravuje produkčný environment `prod-eu` pre release `3.14.0`. Zmena má vytvoriť sieť, private subnets, load balancer, runtime service a súvisiace identity bez toho, aby sa zamieňal source, state, target alebo runtime outcome.

## 1. Dominantný model

Dôveryhodný IaC lifecycle je:

```text
change intent a ownership
→ immutable configuration a resolved inputs
→ target + state identity
→ refresh a saved plan
→ risk/policy decision
→ serialized scoped apply
→ remote reconciliation + state commit
→ independent runtime verification
→ drift, recovery a evidence closure
```

Každý krok odpovedá na inú otázku:

- **Intent:** aký business alebo operational outcome sa mení a kto ho vlastní?
- **Configuration:** aký desired state a ktoré presné dependencies ho definujú?
- **State/target:** nad ktorou infra boundary sa plánuje a aplikuje?
- **Plan:** aké mutations nástroj predikuje nad konkrétnym snapshotom?
- **Decision:** je change risk prijateľný pre tento subject?
- **Apply:** ktoré remote operácie skutočne prebehli?
- **Verification:** zodpovedá runtime pôvodnému outcome-u?
- **Closure:** je state konzistentný, drift vyriešený a recovery capability zachovaná?

IaC nie je bezpečný preto, že konfigurácia je deklaratívna. Bezpečný je až vtedy, keď celý lifecycle zachová identitu zmeny a odlíši predikciu, remote mutation, state evidence a runtime realitu.

## 2. Atlas change subject

Atlas označí zmenu ako `CHG-314-EU`. Jej subject obsahuje:

```text
repository revision       C71
Terraform CLI             T1
provider lock digest      P6
module revisions          M12
non-secret input set      V31
backend/state key         atlas/prod-eu/platform
state lineage + serial    L9 / S208
target account            atlas-prod
region                    eu-central-1
workload identity         iac-prod-apply
saved plan                PL412
```

Bez tohto subjectu veta „Terraform plan bol schválený“ nie je auditovateľná. Nie je jasné, ktorú konfiguráciu, state, provider behavior, target a variable set approval pokrýval.

## 3. Desired, known a actual state

IaC pracuje minimálne s troma stavmi:

- **Desired state** — configuration a vstupy požadujú napríklad tri private subnets a šesť service replicas.
- **Known state** — backend eviduje resource addresses, remote IDs, lineage, serial a posledné známe attributes.
- **Actual remote state** — cloud API reálne obsahuje siete, identity, routovanie a runtime objekty.

```text
configuration C71
       +
state L9/S208
       +
provider observations nad atlas-prod/eu-central-1
       ↓
saved plan PL412
       ↓
remote mutations
       ↓
actual state + nový state serial
```

Tieto vrstvy sa môžu rozísť. Configuration môže stále deklarovať subnet, state ho môže mapovať na staré ID a cloud API môže objekt už nepoznať. Diagnostika preto nezačína ďalším apply, ale určením, ktorá vrstva stratila pravdivosť.

## 4. Authoritative ownership

Pre každý mutable attribute musí existovať jeden jasný writer contract.

Atlas napríklad definuje:

```text
network CIDR a routes        → Terraform
runtime replica count        → deployment platform
emergency WAF deny rule      → incident controller, časovo obmedzené
DNS health failover          → DNS controller
```

Ak Terraform, operátor a security controller menia ten istý firewall rule bez spoločného ownership modelu, nevzniká „drift“, ale konflikt troch desired states.

Repository je authoritative pre deklaráciu, nie automaticky pre:

- remote object identity,
- secrets,
- runtime health,
- incidentný stav,
- cloud-side organization policy,
- data recovery.

Ownership transfer musí byť explicitný. `ignore_changes` bez takéhoto transferu iba skryje konflikt.

## 5. Deklaratívnosť a reconciliation

Deklaratívna konfigurácia opisuje požadovaný objektový stav. Engine a provider z rozdielu medzi configuration, state a observation odvodia graph operácií.

```hcl
resource "example_network" "prod" {
  cidr = "10.40.0.0/16"
}
```

To neznamená, že systém nemá poradie alebo side effects. Tie sa presunuli do:

- dependency graphu,
- provider CRUD a polling behavioru,
- lifecycle pravidiel,
- remote API semantics,
- state update-u.

Terraform typicky reconciliuje počas explicitného `plan` a `apply`. Ak sa pipeline nespustí, remote drift sa sám neopraví ani nemusí byť viditeľný. Scheduled refresh/plan je preto samostatná control vrstva.

## 6. Idempotencia, convergence a reproducibility

Tieto vlastnosti treba odlišovať:

- **Idempotencia:** opakovanie už úspešnej operácie nevytvorí ďalšiu zmenu.
- **Convergence:** opakované reconciliation približuje actual state k desired state.
- **Reproducibility:** rovnaké explicitné vstupy a toolchain vytvoria porovnateľný plan a výsledok.

Atlas očakáva:

```text
apply C71 nad S208 → vytvorí prod-eu platform
refresh + plan C71 nad S209 → no changes
```

To môže rozbiť mutable provider alebo module source, timestamp v managed argumente, nestabilná API normalizácia, skrytý environment variable, data source vyberajúci „latest“ alebo druhý writer.

Preto sa pinujú CLI, providers, modules, policies a release artifacts a uchováva sa resolved input manifest.

## 7. Plan je predikcia viazaná na subject

Plan `PL412` vzniká z kombinácie:

```text
C71 + P6 + M12 + V31 + L9/S208
+ refreshed remote observations
+ target atlas-prod/eu-central-1
+ plan identity a permissions
```

Plan nie je všeobecné povolenie „aplikovať túto branch“. Invaliduje sa napríklad pri zmene:

- configuration alebo variables,
- provider/module/policy revision,
- state serial alebo lineage,
- target account/region,
- remote objectu relevantného pre decision,
- approval alebo security statusu,
- release artifactu.

Apply, ktorý si po approvale ticho prepočíta nový plan, nevykonáva pôvodne schválené rozhodnutie. Saved plan potrebuje digest, subject metadata, kontrolovaný transfer a freshness gate.

## 8. Risk nie je počet plan actions

Atlas klasifikuje change podľa mechanizmu a následku:

```text
20 tag updates
→ nízke runtime riziko

1 route-table replacement
→ možný výpadok celého environmentu

1 IAM policy update
→ privilege expansion

1 database replacement
→ data a identity risk
```

Risk decision zohľadňuje:

- create/update/replace/destroy,
- stateful a identity-bearing resources,
- network a IAM exposure,
- data migration,
- reversibility,
- shared dependencies,
- environment a blast radius,
- novelty a incident history.

Policy as Code môže rozhodnutie podporiť, ale potrebuje versionovanie, tests, vysvetliteľné findings a exception lifecycle. Tool error alebo nevyhodnotiteľný plan nie je pass.

## 9. Apply nie je jedna transakcia

Infra API neposkytujú jednu ACID transakciu pre celý graph. Počas apply môže:

- resource vzniknúť, ale response sa stratiť,
- remote operácia pokračovať po timeout-e,
- časť graphu uspieť a časť zlyhať,
- state write zlyhať po úspešnej remote mutation,
- provider vidieť eventual-consistency 404,
- externý side effect zostať bez state reprezentácie.

Preto apply verdict musí odlíšiť:

```text
no mutation
known partial mutation
unknown remote outcome
mutation complete, state commit failed
state committed, runtime verification failed
complete success
```

Slepý retry je bezpečný iba vtedy, keď je predchádzajúci outcome známy alebo reconciliation preukáže idempotentný stav.

## 10. State je identity a recovery boundary

State viaže Terraform address na remote identity:

```text
module.network.example_subnet.private["az-a"]
→ subnet-123
```

State môže obsahovať sensitive attributes, dependencies, provider metadata, lineage a serial. Nie je iba performance cache.

Backend preto potrebuje:

- encryption,
- least-privilege access,
- locking,
- atomic write semantics,
- versioning a backup,
- audit,
- testovaný restore.

State boundary zároveň určuje blast radius, lock contention, apply permissions, ownership a recovery scope. Príliš veľký state spája nesúvisiace failure domains; príliš malé states vytvárajú množstvo cross-state contracts.

Atlas oddeľuje `prod-eu` od developmentu samostatným accountom, backend keyom, identity, policy a recovery plánom. Environment nie je iba variable `environment = "prod"`.

## 11. Worked failure: break-glass containment bolo automaticky revertované

Počas incidentu security engineer manuálne zablokoval škodlivý CIDR v produkčnom firewall-e. Emergency action mala ownera, ale nebola zaznamenaná do dočasného desired-state override-u. O desať minút scheduled Terraform apply použil pôvodnú configuration.

```text
incident controller pridá deny rule
→ actual state sa vedome odchýli
→ scheduled plan klasifikuje rozdiel iba ako drift
→ automatický apply rule odstráni
→ attack traffic sa vráti
```

### Príčina

Automation nepoznala intent ani dočasný ownership transfer. Drift policy zamieňala neautorizovanú zmenu s aktívnym incidentným controlom.

### Náprava

Atlas zaviedol break-glass lifecycle:

```text
authenticated emergency mutation
→ incident record + owner + expiry
→ pause conflicting reconciliation
→ capture remote diff
→ encode temporary alebo permanent desired state
→ reviewed reconciliation
→ revoke emergency capability
```

Skorší control nie je zákaz všetkých manuálnych zásahov, ale schopnosť rozpoznať ich intent a uzavrieť ich späť do authoritative workflowu.

## 12. Worked failure: remote create uspel, state commit zlyhal

Apply `PL412` vytvoril NAT gateway. Následne runner stratil prístup k backendu ešte pred zápisom nového state serialu.

```text
cloud create request accepted
→ NAT gateway ngw-77 vznikne
→ backend write zlyhá
→ state S208 objekt nepozná
→ job skončí failed
```

Slepý retry by mohol vytvoriť ďalší platený gateway alebo zlyhať na duplicate constraint-e.

### Správny recovery

1. zastaviť ďalšie applies nad týmto state;
2. zachovať provider logs a cloud request ID;
3. overiť remote objekt cez read-only observation;
4. zálohovať state a potvrdiť lineage/serial;
5. vytvoriť nový refresh/plan bez mutation;
6. importovať alebo opraviť binding iba po potvrdení identity;
7. overiť runtime routing a nový state serial;
8. zaznamenať unknown-outcome failure ako osobitnú triedu.

## 13. Kauzálny diagnostický walkthrough

Symptom: nový plan navrhuje vytvoriť druhý production network, hoci cloud console už zobrazuje sieť `atlas-prod-eu`.

### Krok 1 — stabilizuj subject

```text
configuration          C71
backend/state key      atlas/prod-eu/platform
lineage/serial         L9/S208
workspace              prod-eu
target account/region  atlas-prod/eu-central-1
provider lock          P6
predchádzajúci apply   PL412
```

### Krok 2 — formuluj konkurenčné hypotézy

```text
H1: pipeline používa nesprávny backend alebo workspace
H2: configuration address sa zmenila bez moved/import contractu
H3: remote create uspel, ale state write zlyhal
H4: cloud objekt vytvoril iný owner mimo Terraformu
H5: console ukazuje iný account alebo region
H6: provider refresh je stale pre eventual consistency
H7: state bol obnovený zo starého snapshotu
```

### Krok 3 — vyber diskriminačné observation points

- backend key, lineage a serial testujú H1/H7;
- resource addresses a Git diff testujú H2;
- provider logs, cloud audit request ID a timestamps testujú H3/H4;
- caller identity, account a region testujú H5;
- priame read API a opakovaný refresh po propagation window testujú H6;
- state version history ukáže, či novší serial existoval a bol prepísaný.

Atlas nájde úspešný cloud create request z apply identity, ale žiadny následný state write. H3 je potvrdená.

### Krok 4 — contain-ni mutation boundary

State pipeline sa uzamkne a ďalšie applies sa zastavia. Nespúšťa sa destroy ani create.

### Krok 5 — obnov dôveryhodný outcome

Remote network sa identifikuje podľa request ID, accountu, regionu, CIDR a tags. Po backup-e state sa objekt importuje na správnu address, vytvorí sa nový plan a overí sa `no duplicate create`.

### Krok 6 — over pôvodný outcome

```text
state address → správne remote ID
plan → no duplicate network
routing a subnets → zdravé
state serial → nový a auditovaný
runtime critical journey → prejde
```

### Krok 7 — vráť learning

Finding sa zmení na backend availability gate, unknown-outcome verdict, cloud request-ID evidence a runbook pre state-commit failure.

## 14. Drift lifecycle

Drift môže byť:

- **remote drift** — objekt zmenil iný writer;
- **configuration drift** — environments alebo branches sa neúmyselne rozchádzajú;
- **state drift** — binding alebo snapshot nezodpovedá remote realite;
- **provider drift** — nová verzia interpretuje rovnaký objekt inak;
- **dependency drift** — mutable module alebo external data zmenili plan;
- **ownership drift** — nový controller začal meniť atribút bez aktualizácie contractu.

Riadený flow je:

```text
scheduled refresh/plan
→ classify drift + intent
→ determine authoritative owner
→ revert | adopt | repair | transfer ownership
→ update code/state
→ verify runtime
→ close exception
```

Automaticky adoptovať všetko legitimizuje ClickOps. Automaticky revertovať všetko môže zrušiť incidentný containment.

## 15. Identity, secrets a separation of duties

Atlas oddeľuje:

- validation identity,
- plan/read identity,
- production apply identity,
- state-recovery identity,
- break-glass identity.

Preferovaný model je short-lived workload identity viazaná na repository, ref, environment, backend a job purpose. Jedna permanentná admin credential pre všetky states ruší blast-radius kontrolu.

`sensitive` alebo redaction obmedzuje presentation. Nezaručuje, že hodnota nie je v state, provider requeste alebo job memory. Secrets patria do external secret/identity lifecycle-u a state backend sa chráni ako citlivý systém.

## 16. Recovery sa navrhuje pred apply

Pred high-risk change treba poznať:

- last compatible configuration a artifacts,
- state backup a restore postup,
- replace/destroy behavior,
- data a identity preservation,
- rollback verzus roll-forward limity,
- compensating operations,
- external side effects,
- runtime oracle a RPO/RTO.

Git revert zmení desired configuration. Automaticky nevráti remote infraštruktúru, dáta ani state binding. Nový plan môže navrhnúť ďalšiu replacement, preto sa recovery vždy odvodzuje z aktuálneho state-delta inventory.

## 17. Evidence closure

Dôveryhodný Atlas change record prepája:

```text
CHG-314-EU
→ source C71 + resolved inputs P6/M12/V31
→ backend L9/S208
→ saved plan PL412 + policy verdict
→ approval subject
→ apply identity + provider request IDs
→ nový state serial
→ runtime verification
→ drift/recovery outcome
```

Evidence sa uchováva podľa support, rollback a compliance potreby. Green apply bez runtime oracle alebo bez potvrdeného state commit-u je neúplný verdict.

## 18. Diagnostický runbook

1. Urči change, configuration, toolchain, target a state subject.
2. Oddeľ desired, known a actual remote state.
3. Over authoritative ownera každého sporného atribútu.
4. Skontroluj saved plan digest, freshness a approval väzbu.
5. Identifikuj posledný úspešný apply transition a remote request IDs.
6. Rozlíš no-op, partial mutation, unknown outcome, state-write failure a runtime failure.
7. Pred retry refreshni observations bez neuváženej mutation.
8. Zvoľ import, state repair, rollback, roll-forward, compensation alebo restore podľa actual delta.
9. Over state binding aj pôvodný runtime/business outcome.
10. Zmeň finding na ownership, identity, plan, backend alebo recovery control.

## 19. Referenčné pravidlá

- Repository je authoritative pre desired configuration, nie automaticky pre remote reality.
- Plan je subject-bound predikcia, nie garancia.
- Apply nie je jedna transakcia.
- State je identity a recovery boundary, nie iba cache.
- Environment potrebuje samostatný target, backend a identity contract.
- Risk sa odvodzuje z mechanizmu a následku, nie z počtu actions.
- Break-glass je platný iba s expiry, reconciliation a revokáciou.
- Drift sa najprv klasifikuje podľa intentu a ownershipu.
- Retry nasleduje po outcome reconciliation.
- Apply success vyžaduje state commit aj runtime verification.

## 20. Časté omyly

### „Deklaratívne znamená bez side effects“

Poradie a side effects zostávajú v graph-e, providerovi a remote API.

### „Plan je bezpečný, lebo je zelený“

Môže byť stale, pre nesprávny target alebo bez úplnej policy evidence.

### „Failed apply nič nezmenil“

Remote mutation mohla uspieť pred timeoutom alebo state write failure.

### „Git revert je rollback infraštruktúry“

Je to nový desired state, ktorý potrebuje nový plan a compatibility decision.

### „Každý drift treba automaticky revertovať“

Drift môže reprezentovať aktívny incidentný control alebo ownership transfer.

## 21. Zhrnutie

Dôveryhodný IaC lifecycle je:

```text
intent a ownership
→ immutable desired-state subject
→ správny target a state snapshot
→ čerstvý saved plan
→ risk decision
→ serialized scoped apply
→ remote/state reconciliation
→ runtime verification
→ drift a recovery closure
```

IaC troubleshooting nehľadá iba chybu v HCL. Rekonštruuje identitu configuration, state, targetu, provider operácií a runtime outcome-u a určuje prvú hranicu, na ktorej sa desired, known a actual state rozišli.

## Oficiálna dokumentácia

- [Terraform language overview](https://developer.hashicorp.com/terraform/language)
- [Terraform state](https://developer.hashicorp.com/terraform/language/state)
- [Create a Terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [Apply a Terraform plan](https://developer.hashicorp.com/terraform/cli/commands/apply)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Security scanning](../06-gitlab/security-scanning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Terraform providers, resources a data sources →](terraform-providers-resources-data-sources.md)
<!-- KNOWLEDGE-NAVIGATION:END -->