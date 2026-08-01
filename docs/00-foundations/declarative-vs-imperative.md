# Declarative vs. Imperative Approach

Imperatívny prístup opisuje konkrétnu sekvenciu operácií. Deklaratívny prístup opisuje požadovaný výsledný stav a ponecháva mechanizmu, aby vypočítal potrebné zmeny. Rozdiel teda nie je iba syntaktický; mení, kde sa nachádza decision logic, kto vlastní current state a ako sa rieši drift.

Imperatívny postup môže povedať `vytvor server, nainštaluj package, prepíš config a reštartuj službu`. Deklarácia môže povedať `služba má bežať v tejto generation s týmto configuration contractom`. Controller následne porovná desired a observed state, vytvorí plan a opakuje reconciliation, kým systém nedosiahne prijateľnú konvergenciu alebo explicitne nezlyhá.

Deklaratívny model nie je automaticky bezpečnejší. Nesprávny desired state môže controller spoľahlivo rozšíriť na celý fleet. Hidden defaults, mutable dependencies alebo viac writers môžu spôsobiť, že deklarácia nie je úplným source of truth. Imperatívny krok je naopak vhodný pre jednorazové externé side effects, ak má idempotency, journaling a recovery. Voľba preto závisí od state modelu, authority a failure contractu, nie od preferencie YAML verzus shell.

## 1. Definícia

Imperatívny prístup opisuje operácie a ich poradie: vytvor resource, zmeň configuration, reštartuj service a over výsledok. Autor workflowu priamo riadi transition path a musí explicitne riešiť preconditions, partial state, retries a recovery.

Deklaratívny prístup opisuje vlastnosti požadovaného výsledného stavu. Engine alebo controller pozoruje aktuálny stav, vypočíta rozdiel a vykoná operácie potrebné na convergence.

```text
imperatívne  → vykonaj A, potom B a potom C
deklaratívne → výsledný state má spĺňať X, Y a Z
```

Oba modely nakoniec používajú konkrétne procedurálne operations. Rozdiel je v tom, či ich poradie a rozhodovanie vlastní caller, alebo ich odvodzuje platforma zo state-u, dependencies a vlastných reconciliation pravidiel.

## 2. Problém, ktorý modely riešia

Každá automation musí dostať systém zo stavu A do stavu B. Pri jednoduchom jednorazovom postupe môže byť najpresnejšie opísať sequence krokov; pri dlhodobo spravovanom resource-e je často dôležitejšie neustále vedieť, aký state má platiť.

Voľba ovplyvňuje audit, debugging aj ownership. Imperatívny workflow musí sám uchovávať progress a rozhodovať, čo opakovať po zlyhaní, zatiaľ čo deklaratívny engine potrebuje dôveryhodný desired state, observed state a pravidlá pre bezpečnú convergence.

## 3. Spoločný state-transition model

Oba prístupy možno zjednotiť do rovnakého všeobecného toku. Rozdiel je v tom, ktorá vrstva vypočíta transition plan a ako dlho sa ho snaží udržiavať.

```text
intent
→ prečítanie alebo predpoklad aktuálneho state-u
→ výpočet transition
→ vykonanie operations
→ pozorovanie výsledku
→ ďalšia korekcia alebo ukončenie
```

Imperatívny script môže aktuálny stav čítať a rozhodovať podmienkami. Deklaratívny controller môže pod kapotou vykonávať množstvo imperatívnych API calls; deklaratívnosť teda nie je absencia procedúry, ale presun jej ownershipu.

## 4. Imperatívny prístup

Imperatívny workflow explicitne určuje, čo sa má vykonať a v akom poradí. Je vhodný tam, kde samotná sequence nesie business alebo recovery význam a jednotlivé transitions nemožno spoľahlivo odvodiť iba z konečného state-u.

Príklad:

```bash
aws ec2 run-instances ...
aws ec2 create-tags ...
aws elbv2 register-targets ...
```

Autor musí vysvetliť viac než command names:

- **Precondition — stav potrebný pred krokom**: registrácia targetu nemá začať, kým instance nemá správnu network reachability a application readiness.
- **Input identity — presné resources a versions**: workflow nesmie zameniť novovytvorenú instance za starý resource s podobným tagom.
- **Ordering — prečo krok nasleduje až po predchádzajúcom**: dependency môže byť technická, bezpečnostná alebo businessová.
- **Checkpoint — čo už bolo potvrdene dokončené**: po prerušení musí workflow vedieť, odkiaľ bezpečne pokračovať.
- **Failure action — retry, compensation alebo stop**: každý error class potrebuje odlišné správanie.
- **Verification — dôkaz skutočného outcome-u**: API acknowledgement nemusí znamenať, že application prijíma traffic.

## 5. Imperatívny state a recovery

Imperatívny script často potrebuje vlastný state alebo musí spoľahlivo rekonštruovať target state pred každým krokom. Bez toho môže po timeout-e nevedomky zopakovať už vykonanú destructive alebo non-idempotent operation.

Recovery môže pokračovať od checkpointu, vykonať compensating action alebo zastaviť a vyžiadať human decision. Výber závisí od reversibility: vytvorený temporary resource možno odstrániť, ale odoslanú externú platbu alebo destructive data migration nemusí byť možné technicky „undo“.

## 6. Deklaratívny prístup

Deklaratívna configuration vyjadruje invariants a properties, ktoré majú platiť. Engine získava observed state z API alebo vlastného state store-u, vytvára dependency graph či work queue a vykonáva korekcie.

Terraform configuration napríklad opisuje EC2 resource:

```hcl
resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = "t3.micro"

  tags = {
    Name = "web"
  }
}
```

Configuration sama instance nevytvorí. Terraform Core vyhodnotí configuration a state, provider prečíta cloud API, plan určí create/update/replace actions a apply ich vykoná.

## 7. Desired, observed a last-known state

Deklaratívny systém potrebuje rozlišovať viac state representations. Ich zámennosť vedie k chybným planom alebo falošnému presvedčeniu, že configuration zodpovedá runtime-u.

- **Desired state — deklarovaný intent**: opisuje properties, ktoré chce owner presadzovať.
- **Observed state — aktuálne zistená realita**: pochádza z target API, agents alebo controller cache a môže byť stale alebo neúplná.
- **Recorded state — posledná známa mapa ownershipu a outputs**: napríklad Terraform state prepája logical address s remote resource identity.
- **Effective state — behavior vzniknutý kombináciou viacerých controls**: runtime môže ovplyvniť default, admission mutation, external controller alebo manual override.

Engine musí definovať freshness, authority a conflict semantics týchto zdrojov. Ak target API nie je dostupné, plan založený na starom state-e môže byť nebezpečný alebo sa musí odmietnuť.

## 8. Kubernetes reconciliation príklad

Kubernetes Deployment deklaruje tri replicas, image a Pod template. Manifest nepredpisuje konkrétne Nodes ani command sequence potrebnú na vytvorenie a nahradenie Pods.

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

Viac controllerov spolupracuje cez API state:

- **Deployment controller — spravuje rollout intent**: vytvára alebo upravuje ReplicaSets podľa Pod template a strategy.
- **ReplicaSet controller — udržiava požadovaný počet Pods**: vytvára chýbajúce objects, ale neurčuje ich Node placement.
- **Scheduler — priraďuje unscheduled Pod k Node-u**: používa requests, constraints, topology a dostupné resources.
- **Kubelet — vytvára lokálny runtime state**: pullne image, spustí containers a publikuje status a probe results.

Deklarácia „replicas: 3“ preto aktivuje distribuovaný reconciliation systém. Ak Pod zostáva Pending, samotná deklarácia je správna, ale convergence blokuje capacity, scheduling constraint alebo ďalšia dependency.

## 9. Event-driven a periodic reconciliation

Controller môže reagovať na event, pravidelne resyncovať alebo kombinovať oba modely. Event znižuje latency, ale môže sa stratiť, zdvojiť alebo prísť v inom poradí; periodický resync opravuje vynechanú udalosť a drift za cenu ďalšieho loadu.

Reconciliation musí byť bezpečná pri opakovaní. Queue item môže byť spracovaný viackrát a observed state sa môže zmeniť medzi read a write, preto controller používa idempotentný intent, optimistic concurrency a ďalšie retry.

## 10. Deklaratívne neznamená bez poradia

Deklaratívna platforma stále vykonáva dependency-aware sequence. Terraform graph napríklad zabezpečí, že subnet vznikne pred resource-om, ktorý potrebuje jeho ID, ale implicitnú dependency nemusí rozpoznať, ak sa values prepájajú iba mimo configuration graphu.

Kubernetes nepoužíva jeden globálny plan. Nezávislé controllers priebežne reagujú na shared API state, takže dočasné intermediate states sú normálnou súčasťou convergence.

Poradie je teda delegované platforme a jej modelu. Používateľ musí rozumieť, ktoré dependencies engine pozná a ktoré treba vyjadriť explicitne alebo riešiť kompatibilným designom.

## 11. Deklaratívne neznamená automaticky idempotentné

Syntax deklarácie neurčuje behavior všetkých side effects. Resource provider môže pri každom update vytvárať nový external object, hook môže odoslať notification a poorly designed controller môže opakovane vykonať non-idempotent action.

Naopak imperatívny script môže najprv porovnať state a používať stable idempotency key. Dve osi sa preto posudzujú samostatne:

```text
spôsob vyjadrenia intentu → deklaratívny alebo imperatívny
správanie pri opakovaní   → idempotentné alebo ne-idempotentné
```

## 12. Drift

Drift je rozdiel medzi intended alebo recorded state-om a target reality. Môže vzniknúť manual change-om, external controllerom, provider defaultom, failed partial operation alebo zmenou mimo spravovaného scope-u.

Deklaratívny model musí určiť reakciu:

- **Report only — zviditeľnenie bez automatickej zmeny**: vhodné pri citlivom state-e, kde correction potrebuje review.
- **Reconcile — návrat k desired state-u**: vhodné pri jednoznačnom ownershipu a bezpečnej opakovateľnej action.
- **Adopt/import — uznanie existujúceho resource-u**: prepája reality s managed source bez jeho recreation.
- **Ignore specific field — explicitné zdieľanie ownershipu**: zabraňuje controller conflictu, ale môže skryť relevantnú odchýlku.
- **Escalate conflict — zastavenie pri nejasnej autorite**: bezpečnejšie než prepis state-u, ktorý spravuje iný system.

Automatická oprava každého driftu môže viesť k controller fightu. Dva systems s odlišným desired state-om budú prepisovať rovnaké fieldy a vytvoria oscillation alebo API load.

## 13. Source of truth a ownership

Deklaratívna configuration má byť autoritatívna iba pre jasne vymedzené fields a resources. Git repository, Terraform state a Kubernetes API môžu byť súčasne source of truth pre odlišné časti lifecycle-u.

GitOps repository môže vlastniť intended manifest, Kubernetes API observed a effective runtime state a external secret manager hodnotu citlivého secretu. Tvrdenie „Git je source of truth“ je preto neúplné bez field ownershipu, generated data a reconciliation directionu.

## 14. Partial failure v deklaratívnom systéme

Deklaratívny apply môže vytvoriť časť resources a zlyhať pri ďalšom API call-e. Engine následne potrebuje aktualizovať recorded state a pri ďalšom run-e znovu vypočítať rozdiel.

Continuous controller môže zostať v stave „progressing“ alebo opakovane retryovať. Produkčný contract musí vysvetliť retry budget, backoff, terminal conditions, status reporting a whether failed convergence blokuje ďalšie changes.

Desired state nie je transakcia. Distribuovaný system môže určitý čas obsahovať mixed versions alebo iba časť deklarovaných components, preto design potrebuje compatibility a safe intermediate states.

## 15. Imperatívny prístup: vhodné scenáre

Imperatívny model je vhodný, keď postup a intermediate decisions tvoria jadro úlohy:

- **Diagnostika — adaptívne získavanie evidence**: ďalší command závisí od výsledku predchádzajúcej hypothesis a nemá trvalo presadzovať state.
- **Data migration — procedurálny a často jednosmerný transition**: batches, checkpoints, validation a cutover majú explicitné poradie a compensation.
- **Incident recovery — bounded runbook so safety decisions**: responder volí kroky podľa aktuálneho damage a authoritative state-u.
- **Workflow s external side effects — sequence a deduplication**: payment, notification alebo vendor operation potrebuje business state machine, nie iba konečný infrastructure shape.
- **Algorithmic transformation — výsledok vzniká výpočtom nad inputs**: procedúra je prirodzenou a čitateľnou reprezentáciou intentu.

Imperatívnosť nie je anti-pattern. Rizikom je používanie neauditovaných jednorazových commands ako jediného dlhodobého management modelu.

## 16. Deklaratívny prístup: vhodné scenáre

Deklaratívny model je silný, keď má určitý state dlhodobo platiť a platforma ho dokáže bezpečne pozorovať a korigovať:

- **Infrastructure as Code — resource topology a configuration**: source, plan a state umožňujú review, drift analysis a reproducible environment.
- **Kubernetes workloads — priebežné udržiavanie runtime shape-u**: controllers nahrádzajú failed instances a vykonávajú rollout podľa deklarovaného template-u.
- **GitOps — pull-based promotion intended state-u**: reconciler porovná repository revision s cluster scope-om a publikuje convergence status.
- **Policy configuration — stabilné rules a defaults**: policy engine aplikuje versioned intent na opakované decisions.
- **Fleet configuration — konzistentný state mnohých Nodes**: configuration management odhaľuje a opravuje odchýlky podľa ownershipu.

Model je vhodný iba vtedy, keď desired state možno presne vyjadriť a observed state je dostatočne dôveryhodný. Nejasná business procedúra sa nestane jednoduchšou tým, že sa zapíše do YAML.

## 17. Hybridný model

Produkčné systems často kombinujú deklaratívnu platformu s imperatívnym workflowom. Terraform môže deklarovať infrastructure, pipeline imperatívne vykoná plan, approval, apply a verification a application migration použije vlastnú state machine.

Kubernetes controller deklaratívne udržiava replicas, ale operator môže počas incidentu imperatívne pozastaviť rollout alebo spustiť recovery command. Po urgentnom zásahu treba reconcile-nuť source of truth, inak vznikne skrytý drift.

Hybridný design je správny, ak má každá vrstva jasný ownership a transition contract. Problémom nie je miešanie modelov, ale nejasnosť, ktorý system má posledné slovo.

## 18. Porovnanie trade-offov

Tabuľka sumarizuje rozdiely, ale každý riadok vychádza z odlišného ownershipu procedurálnej logiky.

| Oblasť | Imperatívny model | Deklaratívny model | Praktický dôsledok |
|---|---|---|---|
| Vyjadrenie intentu | sequence commands a conditions | properties desired state-u | imperatívny model zvýrazňuje cestu, deklaratívny výsledok |
| Transition logic | vlastní workflow author | vlastní engine/controller | debugging vyžaduje iný source a expertise |
| State | checkpointy alebo explicitné queries | desired, observed a často recorded state | oba modely musia riešiť stale a partial state |
| Opakovanie | bezpečnosť treba navrhnúť v krokoch | reconciliation prirodzene opakuje intent | žiadny model negarantuje idempotency side effects automaticky |
| Drift | detection a correction treba doprogramovať | často prirodzená capability enginu | automatic correction potrebuje field ownership a safe action |
| Poradie | explicitné a čitateľné v procedure | odvodené z graphu alebo controller interactions | hidden dependency môže zlyhať v oboch modeloch |
| Flexibilita | vysoká pre procedural branches | obmedzená schema a semantics platformy | deklaratívna jednoduchosť rastie s kvalitou abstraction |
| Recovery | checkpoint, rollback alebo compensation | ďalšia convergence alebo terminal condition | irreversible data a business actions vyžadujú osobitný model |

## 19. Bezpečnosť

Deklaratívny engine často vlastní široké permissions, pretože musí meniť mnoho resources podľa configuration. Compromise repository, pipeline alebo controller identity môže rýchlo presadiť škodlivý desired state vo veľkom scope-e.

Imperatívny workflow môže používať užšie per-step permissions, ale human commands a long-lived credentials znižujú auditovateľnosť. Oba modely potrebujú least privilege, protected source, reviewed changes, immutable execution references a audit log.

Plan alebo diff je security evidence iba vtedy, keď reviewer rozumie effective changes a apply používa rovnaké inputs. Mutation medzi approvalom a executionom ruší význam kontroly.

## 20. Observability a debugging

Pri imperatívnom modeli sleduj command sequence, input/output, checkpoint a target side effects. Pri deklaratívnom modeli treba navyše pozorovať controller queue, desired/observed difference, conditions, retries a ownership conflicts.

Diagnostický tok:

```text
intent a version
→ authoritative desired state
→ observed/recorded state
→ computed plan alebo controller decision
→ API operation a response
→ target runtime behavior
→ convergence status a user outcome
```

Status `applied` alebo `Ready` môže byť iba lokálny signal. Application business validation zostáva potrebná bez ohľadu na model.

## 21. Anti-patterny

### YAML sa považuje za deklaratívnosť

YAML je serializačný formát. Súbor je deklaratívny iba vtedy, keď consuming system interpretuje jeho fields ako desired properties a má mechanizmus ich udržiavania.

### Deklaratívny model sa považuje za automatickú bezpečnosť

Controller môže presadiť chybný intent konzistentne a rýchlo. Review, policy, blast-radius controls a recovery zostávajú potrebné.

### Imperatívny command sa používa ako trvalá správa state-u

Manual changes nie sú zachytené v authoritative source a ďalší operator nevie reprodukovať ani bezpečne zmeniť prostredie.

### Dva controllers vlastnia rovnaké fieldy

Odlišné desired values vytvoria oscillation a neustále updates. Field ownership a integration contract musia byť explicitné.

### Reconciliation sa považuje za okamžitú transakciu

Convergence trvá a môže zlyhať v intermediate state-e. Application a rollout design musia tolerovať mixed versions a partial availability.

### Human hotfix sa nevráti do source of truth

Incident sa vyrieši, ale ďalší reconciliation hotfix prepíše alebo environment zostane v nezdokumentovanom drifte.

## 22. Návrhové a troubleshooting otázky

Otázky majú určiť state ownership a recovery, nie iba preferovaný syntax style:

1. **Opisujem požadovaný state alebo významnú procedúru?** — určuje prirodzené miesto transition logiky.
2. **Kde je authoritative intent a kto ho môže meniť?** — chráni governance a audit.
3. **Ako sa získava observed state a aká je jeho freshness?** — zabraňuje planu nad neúplnou realitou.
4. **Kto vlastní recorded state a remote identity mapping?** — kritické pri import, rename a recovery.
5. **Ako sa vyjadrujú dependencies a safe intermediate states?** — chráni partial rollout a replacement.
6. **Ako sa správa opakovanie a ambiguous timeout?** — odhaľuje potrebu idempotency a deduplication.
7. **Ako sa deteguje a rieši drift?** — rozlišuje report, reconcile, adopt a conflict.
8. **Čo sa stane pri partial failure?** — definuje checkpoint, retry, terminal condition a human escalation.
9. **Ako sa validuje business outcome?** — execution status sa nesmie zameniť za funkčnú službu.
10. **Ako sa odstráni alebo zmení controller ownership?** — lifecycle zahŕňa migration a retirement automation.

## 23. Kontrolné otázky

1. Kde sa nachádza transition logika v imperatívnom a deklaratívnom modeli?
2. Aký je rozdiel medzi desired, observed, recorded a effective state-om?
3. Prečo YAML sám osebe nie je deklaratívny?
4. Ako Terraform a Kubernetes používajú odlišný reconciliation model?
5. Prečo deklaratívnosť negarantuje idempotency side effects?
6. Ako môže vzniknúť controller fight a oscillation?
7. Kedy je imperatívny model vhodnejší pre data migration alebo recovery?
8. Kedy deklaratívny model poskytuje hodnotnú drift a convergence capability?
9. Čo musí design riešiť pri partial declarative apply?
10. Ako hybridný model rozdelí infrastructure, workflow a application migration ownership?
11. Aké security riziko vytvára široko oprávnený reconciler?
12. Prečo execution alebo convergence status ešte nepreukazuje business outcome?

## 24. Zhrnutie

Imperatívny prístup explicitne vlastní postup a jeho intermediate decisions. Deklaratívny prístup opisuje desired state a deleguje výpočet a opakovanie transition operácií enginu alebo controllerom.

Správna voľba závisí od state ownershipu, významu poradia, reversibility, driftu a failure modelu. Produkčné automation často kombinuje oba prístupy; rozhodujúce je presne vedieť, ktorý system vlastní intent, state, execution a recovery.

## Glossary impact

Relevantné pojmy: imperative approach, declarative approach, desired state, observed state, recorded state, effective state, transition plan, dependency graph, reconciliation, convergence, drift, field ownership, controller fight, compensation a hybrid automation model.

## Primárne zdroje

- [Kubernetes — Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)
- [Terraform — Core workflow](https://developer.hashicorp.com/terraform/intro/core-workflow)
- [Terraform — State](https://developer.hashicorp.com/terraform/language/state)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Automation mindset](automation-mindset.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Idempotencia →](idempotency.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
