# Automation Mindset

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Continuous Improvement](continuous-improvement.md), [Ownership Mindset](ownership-mindset.md)
- Súvisiace témy: idempotency, Infrastructure as Code, CI/CD, scripting, platform engineering, toil

Metadata zaraďuje automation mindset za ownership a continuous improvement. Automatizácia nie je cieľom sama osebe; je to spôsob, ako z opakovanej a pochopenej práce vytvoriť bezpečne opakovateľnú capability s explicitným contractom, evidence a ownerom.

## 1. Definícia

Automation mindset je spôsob uvažovania, pri ktorom človek najprv rozloží opakovanú prácu na vstupy, rozhodnutia, zmeny state-u, failure boundaries a dôkaz výsledku. Až potom rozhoduje, ktoré časti má vykonať stroj, ktoré zostanú ľudským rozhodnutím a aký lifecycle bude mať výsledná capability.

Neznamená to automatizovať všetko. Nejasná jednorazová úloha môže byť vhodnejšia pre dokumentovaný manuálny postup, zatiaľ čo stabilný a často opakovaný proces môže odôvodniť script, pipeline, reusable component alebo self-service platformu.

## 2. Priebežný scenár: environment cez ticket a wiki

Predstav si tím, ktorý potrebuje nové testovacie prostredie. Developer vyplní ticket, administrátor podľa wiki ručne vytvorí VM, network rules, účty a configuration a po dvoch dňoch pošle IP adresu späť.

```text
request v ticket-e
→ čakanie na administrátora
→ ručné vytvorenie network a VM
→ ručná configuration a secrets
→ neformálny smoke test
→ odovzdanie environmentu
```

Proces funguje, ale každý execution obsahuje skryté rozhodnutia. Nie je jasné, ktorý image a package version sa použili, ktoré network rules sú povolené, čo sa stane po partial failure ani čo presne znamená „environment je hotový“.

Ak sa tento postup iba prepíše do dlhého scriptu, chaos sa zrýchli, ale nezmizne. Automation mindset preto začína modelom procesu, nie výberom nástroja.

## 3. Problém, ktorý automatizácia rieši

Manuálnosť nie je problém iba preto, že je pomalšia. Pri opakovaní vytvára variability, waiting, neúplný audit a závislosť od pamäte konkrétneho človeka.

V environment scenári vznikajú štyri dominantné riziká:

- **Variabilita výsledku — rovnaký intent vytvára odlišný environment**: administrátori používajú iné defaults, package versions alebo network rules.
- **Waiting — execution trvá minúty, ale queue dni**: hlavný lead time nevzniká technickou prácou, ale ticketovým handoffom.
- **Knowledge dependency — critical path žije v hlave operátora**: wiki nezachytáva všetky exceptions a recovery decisions.
- **Verification gap — execution sa zamieňa za outcome**: vytvorená VM ešte nepreukazuje, že application path, access a cleanup fungujú.

Automatizácia má hodnotu iba vtedy, keď tieto mechanizmy skutočne zmení. Elektronický formulár pred rovnakou manuálnou queue nie je výrazné systémové zlepšenie.

## 4. Mentálny model automation lifecycle-u

Automation je produkt s vlastným lifecycle-om. Vzniká z pozorovanej práce, mení current state cieľového systému a musí zostať prevádzkovateľná až do svojho retirementu.

```text
pozorovať reálny manuálny proces
→ definovať outcome a authoritative state
→ odstrániť zbytočné kroky
→ vytvoriť input, plan, apply, verify a recovery contract
→ implementovať bounded automation
→ testovať a obmedziť blast radius
→ nasadiť, merať adoption a support load
→ verziovať, udržiavať alebo retire-nuť capability
```

Každá fáza odpovedá na inú otázku. Observation ukáže, čo ľudia skutočne robia. Contract určí, čo má systém garantovať. Implementation vykoná state change. Verification uzavrie feedback loop a ownership zabezpečí, že capability po prvom release-i nezostane bez údržby.

## 5. Najprv pozoruj skutočný proces

Pred automatizáciou treba sledovať reálne executions vrátane workaroundov a failures. Wiki často opisuje iba happy path, zatiaľ čo operátor pri každom treťom requeste manuálne opravuje DNS, čaká na IP pool alebo obchádza neaktuálny image.

V environment scenári treba zistiť:

```text
aký je vstup requestu
→ ktoré rozhodnutia robí administrátor
→ ktoré systémy sa menia
→ kde vzniká waiting
→ ktoré failures sú bežné
→ ako sa overuje výsledok
→ ako sa environment neskôr zruší
```

Tento krok oddeľuje stabilný proces od tacitného expert judgmentu. Stabilné pravidlá možno automatizovať; nejasné decisions treba najprv spresniť alebo ponechať človeku s lepším evidence.

## 6. Je proces vhodný na automatizáciu?

Environment provisioning je silný kandidát, pretože sa opakuje, má podobné vstupy, vytvára merateľný state a jeho manuálna variabilita je drahá. Dôležitý je však celý cost model, nie iba počet minút execution.

```text
automation cost =
analysis + implementation + testing + security + operation + support + maintenance + retirement

manual cost =
frequency × active time + waiting + coordination + error impact + audit effort + opportunity cost
```

V scenári môže administrátor pracovať iba tridsať minút, ale developer čaká dva dni. Najväčšou hodnotou self-service preto nie je úspora tridsiatich minút, ale odstránenie queue a vytvorenie konzistentného, auditovateľného výsledku.

Automatizácia nemusí byť vhodná, ak je request jednorazový, pravidlá sa každý týždeň menia, výsledok nemožno overiť alebo by jedna chyba zasiahla príliš veľký scope. V takom prípade môže byť správnym medzikrokom dokumentovaný script s human reviewom, nie okamžitá organization-wide platforma.

## 7. Definuj outcome a authoritative state

Slabý cieľ znie „vytvoriť VM“. Silnejší outcome znie „poskytnúť izolovaný test environment s definovanou sieťou, identitou, expiry, ownerom a úspešným application smoke testom“.

Automation potrebuje vedieť, ktorý systém je autoritatívny pre jednotlivé časti state-u:

- request a owner môžu byť uložené v portal-e alebo Git-e;
- infrastructure state môže vlastniť Terraform backend alebo cloud API;
- secrets má vlastniť secret manager;
- inventory a expiry má vlastniť service catalog alebo environment registry;
- application readiness má potvrdiť smoke alebo synthetic test.

Bez authoritative state-u sa pri retry alebo manuálnej zmene nedá rozhodnúť, či automation pokračuje, opravuje drift alebo prepisuje legitímny zásah iného actor-a.

## 8. Automation contract: input → plan → apply → verify → recover

Environment vending capability potrebuje jeden súvislý contract.

```text
typed request
→ validation
→ deterministic plan
→ bounded apply
→ postcondition verification
→ structured result
→ recovery alebo cleanup
```

**Input** určuje environment name, ownera, expiry, veľkosť, region a povolený network profile. Hodnoty sa validujú skôr než workflow získa production credentials.

**Plan** vysvetlí, ktoré resources vzniknú, ktoré policies sa použijú a aký scope sa zmení. Pri high-risk requeste sa approval viaže na konkrétny plan a input digest, nie na mutable branch alebo neurčitý ticket.

**Apply** vykonáva zmeny s explicitným actorom, timeoutom a concurrency policy. Nemá skrývať ručný console krok mimo source of truth.

**Verify** kontroluje výsledný state. Nestačí API response `created`; environment musí mať správny access, DNS, secrets, application smoke a inventory record.

**Recover** definuje, čo sa stane po partial failure. Workflow môže pokračovať, reconcile-nuť stav, rollbacknúť reverzibilnú časť alebo eskalovať ambiguous state človeku.

## 9. Vyber primeranú úroveň automatizácie

Automation môže dozrievať spolu so stabilitou contractu a počtom používateľov.

```text
dokumentovaný manuálny proces
→ bounded script
→ shared pipeline
→ reusable component
→ self-service platform capability
```

Dokumentovaný proces je vhodný, keď sa tím ešte učí reálne variants. Script odstraňuje opakované typo a poradie krokov pre jeden use case. Pipeline pridáva shared execution, audit, secrets a concurrency. Reusable component vytvára versioned interface pre viac tímov. Platform capability má zmysel až vtedy, keď existuje stabilný spoločný contract, viac consumers a owner schopný poskytovať support a roadmapu.

Vyššia úroveň nie je automaticky lepšia. Premature platforma môže pre jeden nestabilný use case vytvoriť drahý API, compatibility a support surface.

## 10. Imperatívny a deklaratívny model v tom istom scenári

Imperatívna automation opisuje poradie operácií:

```text
vytvor network
→ vytvor subnet
→ vytvor VM
→ nastav identity
→ nainštaluj application
```

Je vhodná, keď sequence a intermediate state majú business alebo migration význam. Musí však vedieť, ktoré kroky už prebehli a ako pokračovať po failure.

Deklaratívny model opisuje požadovaný výsledok:

```text
existuje environment E
s network profilom N,
ownerom O,
expiry T
a application health = ready
```

Controller porovná desired a observed state a vykoná potrebné korekcie. Tento model podporuje drift detection a safe re-execution, ale stále potrebuje provider semantics, dependency ordering a explicitné správanie pri resources, ktoré nemožno meniť in-place.

V praxi sa modely kombinujú. Terraform môže deklaratívne spravovať infraštruktúru, zatiaľ čo databázová migration alebo bootstrap zostáva riadenou imperatívnou sekvenciou.

## 11. Idempotency a stabilná identita operácie

Predstav si, že workflow po vytvorení VM stratí network connection a caller nedostane response. Výsledok je nejasný: request mohol zlyhať pred execution alebo mohol uspieť a stratiť iba odpoveď.

Naivný retry vytvorí druhú VM. Idempotentný model používa stabilnú environment identity, napríklad `team-a-pr-142`, a pred mutation načíta observed state.

```text
request environment team-a-pr-142
→ state neexistuje: vytvor
→ timeout
→ retry s rovnakou identity
→ state už existuje: pokračuj vo verification
```

Idempotency neznamená, že sa pri každom pokuse vykonajú rovnaké interné kroky. Znamená, že opakovanie rovnakého intentu nevedie k nekontrolovanej duplicite ani k poškodeniu správneho výsledného state-u.

## 12. Partial failure a recovery

Environment vzniká cez viac externých systémov. Network môže byť vytvorená, VM môže existovať a secret delivery môže zlyhať. Binary status `failed` nehovorí, čo zostalo aktívne ani čo je bezpečné opakovať.

Recovery decision vychádza z observed state-u:

- **Resume** pokračuje od overeného checkpointu, ak predchádzajúce kroky zostávajú validné.
- **Reconcile** porovná desired a observed state a vykoná iba chýbajúce zmeny.
- **Rollback** odstráni reverzibilné resources, ak návrat nevytvorí data alebo dependency problém.
- **Compensation** vykoná opačný business side effect, keď technické undo nie je možné.
- **Manual escalation** zastaví automatické zásahy pri ambiguous alebo high-risk state-e a poskytne človeku presné evidence.

Najhorší model je automaticky spustiť celý workflow od začiatku bez znalosti partial state-u.

## 13. Error classification a retry

Retry má zmysel iba vtedy, keď ďalší pokus môže uspieť a opakovanie je bezpečné. Invalid input, chýbajúce permission alebo policy deny sa bez zmeny podmienok nezlepšia.

```text
invalid input
→ fail fast s field-level vysvetlením

authorization deny
→ fail a ukáž identity/policy boundary

transient provider outage
→ bounded backoff + jitter

unknown partial result
→ najprv discover observed state
```

Retry contract potrebuje presný allowlist retryable errors, exponential backoff, jitter, attempt alebo deadline budget a idempotency alebo deduplication. Bez týchto controls môže outage vyvolať retry storm a zhoršiť recovery providera.

## 14. Concurrency a locking

Dva runs môžu súčasne meniť rovnaký environment alebo shared network. Oba vytvoria plan z rovnakého starého state-u a následne sa navzájom prepíšu.

Automation preto potrebuje concurrency model:

- resource lock serializuje mutation rovnakého scope-u;
- optimistic concurrency porovná version pred zápisom a zlyhá pri zmene;
- partitioning dovolí paralelné runs pre nezávislé accounts alebo environments;
- deduplication key zlúči opakované eventy s rovnakým intentom.

Lock nie je bez nákladov. Môže vytvoriť queue a potrebuje timeout, ownership metadata a recovery stale locku.

## 15. Guardrails a security boundary

Automation vykonáva zmeny rýchlo a často s výkonnou identity. Rovnaká vlastnosť zvyšuje hodnotu aj blast radius chyby.

Environment vending workflow preto používa viac vrstiev ochrany:

```text
schema validation
→ policy nad requestom a planom
→ short-lived scoped credential
→ environment/resource limit
→ locked state
→ staged rollout capability
→ postcondition verification
→ immutable audit
```

Least privilege obmedzí accounts, regions a resource types, ktoré workflow smie meniť. Untrusted pull request nesmie získať production secret. Artifacty, actions a image references majú byť pinned alebo overené digestom. Logs musia redigovať credentials a audit identity nesmie mať nekontrolovanú možnosť odstrániť vlastný trail.

Kill switch musí vedieť zastaviť nové executions nezávisle od zlyhávajúceho workflow pathu.

## 16. Human in the loop

Človek má rozhodovať tam, kde je potrebný širší risk context, nie mechanicky potvrdzovať každý green plan.

Nízko-riskový ephemeral environment môže prejsť automaticky v rámci policy. Environment s public ingressom, vysokým costom alebo production data accessom môže vyžadovať explicitný review.

```text
automation vytvorí immutable plan a risk context
→ reviewer posúdi exception, blast radius a recovery
→ approval sa viaže na konkrétny digest
→ apply vykoná automation
→ verification potvrdí outcome
```

Approval bez relevantného contextu iba pridáva waiting a diffusion of responsibility. Reviewer musí mať expertise, authority a možnosť zmenu odmietnuť.

Break-glass path je určený pre incident alebo control-plane outage. Musí byť auditovaný, časovo obmedzený a po zásahu sa manual state musí reconcile-nuť späť do managed source of truth.

## 17. Observability automation systému

Automation je production system. Zelený UI status alebo exit code 0 nestačia na diagnosis ani na meranie hodnoty.

Každý run potrebuje:

- jednoznačný run ID;
- input a workflow version;
- actor a authorization context;
- structured phase events pre validation, plan, apply a verify;
- retry, queue a lock metrics;
- result artifacts a target state reference;
- end-to-end outcome, napríklad `environment ready and smoke passed`.

Ak apply skončí úspešne, ale smoke zlyhá, workflow musí reportovať verification failure, nie successful environment creation.

## 18. Diagnostika worked failure-u

Developer spustí environment request. Workflow po cloud API timeout-e retryuje a neskôr skončí chybou `resource already exists`. V inventory sú dve VM a žiadny environment nemá správne secrets.

Diagnostika sleduje lifecycle namiesto náhodného opakovania:

```text
1. Input
   bol environment key stabilný a rovnaký pri retry?

2. Plan
   obsahoval create alebo ensure semantics?

3. Apply
   ktorý API call dostal timeout a aký request ID mal provider?

4. State
   čo už existuje v cloud API a Terraform/workflow state-e?

5. Retry
   bola chyba klasifikovaná ako bezpečne opakovateľná?

6. Verify
   prečo workflow nezistil chýbajúce secrets pred success/failure výsledkom?
```

Root cause nie je iba timeout. Systém nemal stabilnú operation identity, po ambiguous result-e nevykonal discovery a retry opakoval create side effect. Náprava preto zahŕňa idempotency key, reconcile pred retry, state lock a explicitnú verification fázu.

## 19. Rollout a adoption automation capability

Nový workflow sa nemá okamžite vynútiť pre všetky tímy. Najprv sa použije na obmedzenom scope-e, kde možno porovnať duration, queue time, failure rate, support load a výslednú konzistenciu s manuálnym baseline-om.

Adoption je súčasť výsledku. Capability, ktorú users obchádzajú pre dlhú latency, nejasný error alebo chýbajúci use case, neznižuje toil. Mandatory use môže iba skryť shadow scripts.

Platform owner preto sleduje:

```text
relevant flows cez automation
+ bypass rate
+ time-to-ready
+ failure a retry rate
+ support volume
+ user feedback
+ cost per environment
```

Tieto signály ukážu, či automation rieši pôvodný problem alebo iba presunula prácu z administrátora na support tím platformy.

## 20. Versioning, support a retirement

Shared automation vytvára interface voči consumers. Zmena input schema, workflow runtime, provider API alebo default policy môže byť breaking change.

Safe lifecycle používa explicitné versions, compatibility tests, canary consumers, deprecation window a inventory adopcie. Pinning starej verzie navždy nie je bezpečné, pretože dependencies a security requirements sa menia.

Capability potrebuje ownera, support boundary, incident path, roadmap a retirement plan. Environment workflow sa retire-ne, keď ho nahradí iná platforma alebo pôvodný proces zanikne. Retirement zahŕňa migration consumers, credential revocation, state archival, cleanup resources a odstránenie alternatívneho execution pathu.

## 21. Anti-patterny

### Automation zlého procesu

Ticketový approval chain sa iba prepíše do pipeline. Execution je elektronický, ale waiting a nejasné decision rights zostanú.

### Script bez ownera

Critical tool žije v osobnom repository alebo na jednom serveri. Po odchode autora nikto nepozná jeho dependencies, permissions ani recovery path.

### Premature platform

Jeden nestabilný use case sa zmení na organization-wide framework s desiatkami options. Support a compatibility cost vzniknú skôr než stabilný common contract.

### Hidden manual step

Workflow vyžaduje console change alebo lokálny súbor mimo source of truth. Reproducibility a audit sa prerušia práve na najcitlivejšej boundary.

### Success bez verification

API prijme request a job skončí green, ale resulting environment nemá správny access alebo application health. Execution success sa zamieňa za outcome success.

### Infinite retry

Permanentný invalid input alebo permission failure blokuje queue a opakuje side effects bez error classification a budgetu.

### Platform bez adoption

Capability technicky existuje, ale users ju obchádzajú. Tím meria počet features platformy namiesto odstráneného waitingu, toil-u a variability.

## 22. Troubleshooting automation systému

Pri incidente najprv urč, v ktorej fáze lifecycle-u sa dôkaz odchýlil:

```text
input
→ validation
→ plan
→ apply
→ dependency response
→ state persistence
→ verification
→ result delivery
```

Typické symptom-to-boundary mapovanie:

- workflow zlyháva po update-e: porovnaj workflow, runtime, provider API a consumer versions;
- retry vytvára duplicates: over stable identity, idempotency a server-side result state;
- runs čakajú v queue: odlíš runner capacity, global lock a blocked dependency;
- apply je green, service nefunguje: verification neoveruje application outcome;
- source a runtime state sa líšia: hľadaj manual actor, drift alebo stale state;
- users workflow obchádzajú: analyzuj interface, latency, missing use cases a failure trust;
- incident má veľký blast radius: skontroluj partitioning, least privilege, rate limits, staged rollout a kill switch.

## 23. Kontrolné otázky

1. Prečo automation mindset nezačína výberom scripting jazyka alebo platformy?
2. Ktoré časti manuálneho environment procesu treba pozorovať pred automatizáciou?
3. Ako sa odlišuje execution success od outcome success?
4. Kedy je vhodný dokumentovaný process, script, pipeline a self-service platforma?
5. Aký je rozdiel medzi imperatívnym a deklaratívnym modelom?
6. Prečo ambiguous timeout vyžaduje discovery state-u pred retry?
7. Ako stable operation identity podporuje idempotency?
8. Aké recovery možnosti existujú pri partial failure?
9. Prečo retry potrebuje error classification, backoff, jitter a budget?
10. Ako concurrency control chráni shared state?
11. Čo má človek reálne posudzovať pri approvale?
12. Ktoré security boundaries vznikajú pri automation identity?
13. Aké telemetry odlišujú workflow failure od target verification failure-u?
14. Ako sa meria adoption a skutočná hodnota automation?
15. Čo musí obsahovať retirement automation capability?

## 24. Zhrnutie

Automation mindset premieňa opakovanú prácu na explicitný lifecycle. Najprv odhalí reálny proces a outcome, potom definuje authoritative state a contract `input → plan → apply → verify → recover` a až následne vyberie primeranú úroveň automation.

Bez idempotency, state discovery, error classification, guardrails a verification môže automation iba zrýchliť chaos a zväčšiť blast radius. Zdravá capability je versionovaný produkčný produkt s ownerom, telemetry, adoption evidence, supportom a retirementom.

## Glossary impact

Relevantné pojmy: automation mindset, automation candidate, authoritative state, automation contract, imperative automation, declarative automation, idempotency, partial failure, compensation, retry contract, dry-run, guardrail, human in the loop, break-glass, workflow state, concurrency control, deduplication, automation product a adoption.

## Primárne zdroje

- [Google SRE — Eliminating Toil](https://sre.google/sre-book/eliminating-toil/)
- [Google Cloud — DevOps capabilities](https://cloud.google.com/architecture/devops)
- [NIST Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: You build it, you run it](you-build-it-you-run-it.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Declarative vs. imperative prístup →](declarative-vs-imperative.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
