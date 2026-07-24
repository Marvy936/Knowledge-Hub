# DORA Metrics

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Value Stream Mapping](value-stream-mapping.md), [Continuous Improvement](continuous-improvement.md)
- Súvisiace témy: CI/CD, deployment strategies, SRE, observability, flow metrics
- Model: aktuálny päťmetrikový model DORA

## 1. Čo DORA metriky merajú

DORA software delivery performance metrics merajú schopnosť tímu dodávať softvérové zmeny rýchlo a bezpečne. Aktuálny model používa päť metrík rozdelených na throughput a instability.

```text
Throughput
├── Change lead time
├── Deployment frequency
└── Failed deployment recovery time

Instability
├── Change fail rate
└── Deployment rework rate
```

Historický pojem „Four Keys“ už nevystihuje celý model. Deployment rework rate pridáva pohľad na kapacitu spotrebovanú neplánovanými opravnými deploymentmi a recovery metrika sa presnejšie viaže na zlyhanie spôsobené deploymentom.

## 2. Prečo nestačí jedna metrika

Delivery systém môže zrýchliť deploymenty za cenu vyššieho failure rate, alebo znížiť počet incidentov tým, že prestane nasadzovať. Preto sa throughput a instability musia vyhodnocovať spoločne.

Metriky nepredstavujú cieľ samy osebe. Sú outcome signals, ktoré ukazujú, že systém sa správa určitým spôsobom; príčinu treba hľadať cez value stream, pipeline, architecture a operational evidence.

## 3. Event contract

Každá metrika potrebuje stabilnú definíciu udalostí, času, scope-u a klasifikácie. Bez event contractu môžu dva tímy vypočítať rovnaký názov metriky úplne odlišne.

Minimálny model prepája zmenu s artifactom, deploymentom a prípadným incidentom:

```text
commit_sha
→ build_id a artifact_digest
→ deployment_id a service
→ user impact
→ remediation deployment alebo recovery
```

## 4. Scope merania

DORA metriky sa majú primárne počítať pre konkrétnu službu alebo homogénny value stream. Agregácia experimentálneho interného nástroja a regulovanej platobnej služby môže vytvoriť priemer, ktorý neopisuje ani jeden systém.

Najhodnotnejšie je sledovať trend rovnakej služby v čase a interpretovať ho spolu s kontextom kritickosti, architektúry a release modelu. Benchmark môže poskytnúť orientáciu, ale nemá nahradiť vlastný improvement target.

## 5. Change lead time

**Change lead time** je čas od commitu zmeny do version control po jej úspešné nasadenie do produkcie. Meria software delivery časť value streamu, nie celý produktový čas od nápadu po používateľa.

```text
change lead time = successful production deployment time - commit time
```

Lead time zahŕňa review queue, CI, čakanie na runner, schválenia, packaging, deployment a rework pred úspešným nasadením. Preto krátky build job automaticky neznamená krátky delivery flow.

## 6. Event pravidlá pre change lead time

Začiatok musí byť konzistentne viazaný na commit alebo inú presne definovanú version-control udalosť. Pri merge commit, squash merge a viacerých commitoch v jednom deploymente treba určiť, či sa používa najstarší commit, merge timestamp alebo iný dohodnutý bod.

Koniec nastáva až pri úspešnom produkčnom nasadení definovaného artifactu. Vytvorenie release tagu alebo dokončenie staging deploymentu nie je production outcome.

## 7. Čo dlhý lead time odhaľuje

Dlhý lead time často vzniká vo frontoch, nie počas aktívneho výpočtu. Review wait, environment provisioning, manuálne approvals a veľké batchy môžu dominovať aj v technicky rýchlej pipeline.

Metrika preto vedie k diagnostickým otázkam: ktorá fáza obsahuje najviac wait time, kde vzniká rework a či sa práca pohybuje v príliš veľkých dávkach. Odpoveď poskytuje VSM, nie samotná DORA hodnota.

## 8. Deployment frequency

**Deployment frequency** vyjadruje, ako často tím nasadzuje zmeny do produkcie alebo ich sprístupňuje používateľom podľa dohodnutého release modelu. Môže sa vyjadriť počtom deploymentov za obdobie alebo časom medzi deploymentmi.

```text
deployment frequency = počet kvalifikovaných production deploymentov / obdobie
```

Vyššia frekvencia často signalizuje malé dávky a automatizovaný tok, ale iba vtedy, keď jednotlivé deploymenty predstavujú reálne zmeny a nie umelo vytvorené technické udalosti.

## 9. Čo sa počíta ako deployment

Nová verzia artifactu, konfigurácie alebo infraštruktúry, ktorá mení produkčné správanie, typicky predstavuje deployment. Automatický rescheduling rovnakého Podu alebo restart bez zmeny deklarovaného release state-u sa zvyčajne nepočíta.

Pri feature flags treba explicitne rozhodnúť, či release používateľom tvorí samostatnú udalosť. Deployment a release môžu byť oddelené, preto event contract musí zodpovedať tomu, čo organizácia skutočne chce merať.

## 10. Failed deployment recovery time

**Failed deployment recovery time** je čas od používateľského dopadu zlyhaného deploymentu po obnovenie definovaného service outcome-u. Nejde iba o čas spustenia rollback príkazu.

```text
failed deployment recovery time = verified service restored time - deployment impact time
```

Recovery môže prebehnúť rollbackom, roll-forwardom, hotfixom, zmenou konfigurácie alebo deaktiváciou feature flagu. Koniec sa má potvrdiť používateľským alebo service-level evidence, nie iba zeleným pipeline jobom.

## 11. Prečo nejde o všeobecné MTTR

Táto DORA metrika sa viaže na zlyhania spôsobené software deploymentom. Výpadok externého providera, fyzickej infraštruktúry alebo útok bez väzby na deployment patrí do širšieho incident-management modelu.

Miešanie všetkých incidentov do jednej recovery metriky znižuje schopnosť posúdiť delivery systém. Organizácia môže paralelne sledovať všeobecný incident recovery time, ale musí udržať odlišný denominator a scope.

## 12. Čo dlhý recovery time odhaľuje

Dlhý recovery time môže odhaliť slabú observability, nejasný ownership, chýbajúci rollback alebo nekompatibilnú databázovú migráciu. Často tiež ukazuje, že emergency path má rovnaké pomalé approvals ako bežný release.

Diagnostika má rozdeliť recovery na detection, triage, decision, remediation, deployment a validation. Až potom je možné určiť, či dominantný problém predstavuje technický mechanizmus alebo organizačné rozhodovanie.

## 13. Change fail rate

**Change fail rate** je podiel produkčných deploymentov, ktoré spôsobia degradáciu a vyžadujú bezprostrednú nápravu.

```text
change fail rate = failed deployments / všetky kvalifikované deployments × 100 %
```

Denominator je kritický. Štyri zlyhania pri tisíc deploymentoch opisujú iný systém než štyri zlyhania pri ôsmich deploymentoch.

## 14. Klasifikácia failed deploymentu

Failed deployment musí byť definovaný podľa používateľského alebo service-level dopadu. Samotný neúspešný pipeline job pred produkciou nie je change failure, pretože ochranný mechanizmus zmenu správne zastavil.

Za failure sa typicky považuje deployment vyžadujúci rollback, urgentný hotfix, konfiguráciu alebo inú neplánovanú mitigáciu. Minor bug bez okamžitej nápravy môže patriť do defect metriky, ale nemusí spĺňať dohodnutú DORA klasifikáciu.

## 15. Čo vysoký change fail rate odhaľuje

Vysoká hodnota môže súvisieť s veľkými batchmi, slabými testami, environment driftom, chýbajúcim canary overením alebo nebezpečnými migráciami. Môže tiež odhaliť, že deployment eventy sa klasifikujú nekonzistentne.

Zníženie fail rate zákazom deploymentov nie je zlepšenie. Metriku treba posudzovať spolu s deployment frequency a lead time, aby sa stabilita nedosahovala stagnáciou.

## 16. Deployment rework rate

**Deployment rework rate** je podiel deploymentov, ktoré nepredstavujú plánovanú hodnotovú zmenu, ale neplánovanú opravu používateľsky viditeľnej chyby.

```text
deployment rework rate = corrective deployments / všetky kvalifikované deployments × 100 %
```

Metrika zviditeľňuje kapacitu spotrebovanú opravovaním predchádzajúcej práce. Jeden failed deployment môže vytvoriť viac opravných deploymentov, preto rework rate zachytáva iný aspekt instability než change fail rate.

## 17. Planned a corrective classification

Každý deployment potrebuje klasifikáciu plánovanej hodnotovej zmeny alebo neplánovaného corrective work. Klasifikáciu nemožno spoľahlivo odvodiť iba z názvu branche; mala by vychádzať z release alebo incident eventu a byť auditovateľná.

Ak tímy označia každý hotfix ako plánovanú zmenu, rework zmizne iba z reportu. Stabilná taxonomy a občasný sample review znižujú gaming a neúmyselné rozdiely medzi tímami.

## 18. Throughput a instability spolu

Throughput opisuje schopnosť dostať zmenu do produkcie a obnoviť službu po zlyhaní. Instability opisuje, akú časť zmien a deploymentov tvorí failure alebo corrective work.

```text
rýchly flow + nízka instability
→ malé zmeny, skorý feedback a efektívny recovery

rýchly flow + vysoká instability
→ systém dodáva a opravuje problémy vysokou rýchlosťou

pomalý flow + nízka instability
→ stabilita môže byť výsledkom zriedkavých zmien
```

## 19. Zdroje dát

Version control poskytuje commit identity, CI/CD systém build a deployment events a artifact registry stabilnú identitu nasadeného výstupu. Incident systém poskytuje impact a recovery timestamps, zatiaľ čo feature-flag platforma môže doložiť oddelený release používateľom.

Tieto zdroje sa musia prepájať spoločnými identifikátormi. Manuálne párovanie podľa názvu služby alebo času je náchylné na chyby a s rastom objemu sa stáva neudržateľné.

## 20. Minimálny dátový model

```text
deployment_id: deploy-2026-00482
service: payments-api
commit_sha: a12bc34
artifact_digest: sha256:...
started_at: 10:00
completed_at: 10:08
user_impact_at: 10:05
restored_at: 10:22
classification: failed
remediation: rollback
planned_change: true
```

Dátový model musí zachytiť aj source system, environment a versioning taxonomy. Bez nich nie je možné spätne overiť, prečo bol deployment zahrnutý alebo vylúčený.

## 21. Data-quality failure modes

Chýbajúci artifact digest môže spojiť incident s nesprávnou verziou. Nesynchronizované hodiny môžu vytvoriť záporný duration a nejednotné názvy služieb rozdelia jeden value stream na viac zdanlivo nezávislých systémov.

Ďalším problémom je survivorship bias: úspešné deploymenty sa automaticky zaznamenajú, ale manuálne hotfixy mimo pipeline chýbajú. Audit musí preto hľadať aj emergency a out-of-band paths.

## 22. Percentily a distribúcie

Pri duration metrikách nestačí iba priemer. Median ukazuje typický tok, zatiaľ čo p90 alebo p95 odhaľuje dlhý chvost zmien, ktoré čakajú extrémne dlho.

Segmentácia podľa service, change type alebo risk class môže byť užitočná, ak zostane stabilná. Príliš jemné delenie však znižuje počet pozorovaní a vytvára nestabilné trendy.

## 23. DORA ako diagnostický trigger

DORA metrika ukazuje zmenu výsledku, ale nie root cause. Dlhý lead time má viesť k VSM; vysoký change fail rate k analýze batch size, test coverage, migrations a progressive-delivery evidence.

Doplnkové diagnostické metriky zahŕňajú review wait, pipeline duration, queue time, flaky-test rate, batch size, rollback success a approval wait. Tieto metriky sa vyberajú podľa hypotézy, nie ako univerzálny dashboard všetkého.

## 24. Reliability a delivery performance

DORA metriky nemerajú kompletnú reliability služby. SLI, SLO, error budgets, latency, correctness a durability zostávajú potrebné na posúdenie runtime outcome-u.

Tím môže mať kvalitný deployment proces a pritom zle navrhnutú službu. Naopak spoľahlivá služba môže mať pomalý delivery systém, ktorý bráni bezpečným opravám a evolúcii.

## 25. Anti-gaming pravidlá

### Nemerať jednotlivcov

Delivery performance je vlastnosť socio-technického systému. Individuálne targety motivujú k umelému deleniu commitov, skrývaniu zlyhaní a optimalizácii viditeľnej aktivity namiesto hodnoty.

### Neoptimalizovať jednu metriku

Deployment frequency bez fail rate môže odmeňovať nebezpečnú rýchlosť. Change fail rate bez throughputu môže odmeňovať nulovú zmenu.

### Nemeníť definície podľa výsledku

Event contract a taxonomy musia byť verzované a zmeny spätne zdokumentované. Inak trend odráža zmenu výpočtu, nie zmenu systému.

### Nepoužívať benchmark ako univerzálny cieľ

Kritickosť, release model a architektúra ovplyvňujú vhodný target. Cieľom je zlepšenie vlastného value streamu, nie leaderboard medzi neporovnateľnými službami.

## 26. Praktický lab

Pre jednu službu zozbieraj za posledných 30 dní všetky production deployment events, ich commit a artifact identity a prípadné failed-deployment incidents. Explicitne označ corrective deploymenty.

Vypočítaj všetkých päť metrík, pri duration metrikách uveď median a p95. Potom vyber jednu zhoršujúcu sa metriku, vytvor value-stream alebo incident breakdown a navrhni jednu testovateľnú hypotézu.

## 27. Troubleshooting merania

Ak deployment frequency vyzerá neprirodzene vysoká, skontroluj restarty, rescheduling a automatické infra udalosti. Ak change fail rate vyzerá príliš nízka, porovnaj incidenty a emergency changes s deployment datasetom.

Ak recovery time chýba, problém môže byť v neprepojenom incidentnom systéme alebo v absencii jednoznačného restored eventu. Najprv oprav data contract; nepresné číslo nie je lepšie než transparentne neúplné meranie.

## 28. Kontrolné otázky

1. Prečo sa DORA metriky musia vyhodnocovať spoločne?
2. Aký event contract potrebuje change lead time?
3. Čo sa nemá počítať ako production deployment?
4. Prečo failed deployment recovery time nie je všeobecné MTTR?
5. Prečo je denominator change fail rate kritický?
6. Ako sa deployment rework rate líši od change fail rate?
7. Prečo artifact identity zlepšuje kvalitu merania?
8. Ako sa DORA dopĺňa s VSM a SLO?
9. Aké gaming správanie môže vyvolať individuálny target?

## 29. Zhrnutie

DORA metriky poskytujú spoločný outcome model pre throughput a instability software delivery systému. Ich hodnota závisí od stabilných event definitions, kvalitnej identity zmeny, správneho scope-u a následnej diagnostiky mechanizmov, ktoré výsledok vytvárajú.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Value stream mapping](value-stream-mapping.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: DevOps anti-patterny →](devops-anti-patterns.md)
<!-- KNOWLEDGE-NAVIGATION:END -->