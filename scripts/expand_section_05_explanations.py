from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRANCH = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
if not BRANCH:
    raise SystemExit("Unable to resolve pull request branch")


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=REPO, check=True)


run("git", "fetch", "origin", BRANCH)
run("git", "checkout", "-B", BRANCH, f"origin/{BRANCH}")

blocks: dict[str, str] = {
    "continuous-integration.md": r'''## Doplnenie výkladu: integration candidate a stale evidence

Continuous Integration neznamená iba to, že sa po pushi spustí test job. Jej hlavným subjectom je **integration candidate**: presný snapshot, ktorý vznikne spojením navrhovanej zmeny s aktuálnym cieľovým stavom.

Pri pull requeste existujú minimálne tri rozdielne identity:

```text
feature branch tip
cieľová branch tip
synthetic merge candidate
```

Feature branch môže byť zelená voči starému `main`, no po integrácii s novším `main` vznikne iný tree. Hosting platforma alebo merge queue preto často vytvorí dočasný commit, ktorý má ako parents feature a cieľový tip. Testy nad týmto synthetic merge commitom poskytujú evidence pre budúci integrated snapshot.

Príkazy:

```bash
feature_sha=$(git rev-parse HEAD)
target_sha=$(git rev-parse origin/main)
merge_base=$(git merge-base HEAD origin/main)
printf 'feature=%s target=%s base=%s\n' \
  "$feature_sha" "$target_sha" "$merge_base"
```

`rev-parse` resolve-ne refs na commit IDs. `merge-base` nájde spoločného predka používaného na porovnanie zmien. Tieto hodnoty ešte nevytvárajú merge candidate; iba presne identifikujú vstupy.

CI evidence musí viazať:

```text
source commit
+ target commit
+ výsledný candidate tree alebo merge commit
+ workflow generation
+ dependency/build inputs
```

Ak sa target branch po úspešnom teste posunie, pôvodný verdict môže byť **stale**. Neznamená to, že test klamal; znamená to, že platil pre iný subject. Merge queue tento problém rieši sériou alebo skupinou kandidátov testovaných v poradí budúcej integrácie.

Zelená CI teda preukazuje, že konkrétny candidate prešiel konkrétnymi checks. Nepreukazuje, že všetky required checks skutočne existovali, že runner bol trusted, že artifact neskôr vznikol z rovnakých bytes alebo že produkcia používa tento candidate.

''',
    "continuous-delivery.md": r'''## Doplnenie výkladu: čo znamená deployable a prečo delivery nekončí buildom

Continuous Delivery udržiava systém v stave, v ktorom je možné vydať overenú release jednotku na požiadanie. Slovo **deployable** neznamená iba „artifact existuje“. Znamená, že artifact má známu identitu, complete evidence, kompatibilnú konfiguráciu a pripravenú deployment/recovery cestu.

Delivery chain preto oddeľuje:

```text
buildable source
→ verified artifact
→ release candidate
→ promotable release manifest
→ environment-ready deployment plan
```

Manuálny krok v Continuous Delivery nie je manuálne prepisovanie príkazov. Môže ísť o explicitné business alebo risk rozhodnutie „promote this exact release subject“. Po approval sa vykoná už pripravená automatizovaná transition.

Príklad release manifestu:

```yaml
releaseId: payments-10.0.0-rc.4
sourceSha: d94e1c6
artifacts:
  api: registry.example/payments-api@sha256:abc
  migrations: object://releases/migrations@sha256:def
configurationSchema: 7
evidenceBundle: sha256:789
```

Manifest viaže viac outputs do jednej release identity. Samotný image digest nehovorí, ktorú migration alebo config generation treba použiť.

Delivery readiness má explicitné gates:

```text
required tests complete
artifact publication immutable
security/license evidence complete
migration compatibility potvrdená
target prerequisites známe
rollback/roll-forward eligibility vyhodnotená
```

Ak je posledný deployment krok manuálny, stále ide o Continuous Delivery, pokiaľ release candidate priebežne zostáva pripravený a deployment je reprodukovateľný. Ak tím po každom release ručne skladá config, hľadá správny artifact a improvizuje runbook, nejde o continuous delivery capability, aj keby CI bola zelená.

''',
    "continuous-deployment.md": r'''## Doplnenie výkladu: automatický release ako uzavretý feedback loop

Continuous Deployment automaticky posúva každú zmenu, ktorá splní policy, až do production exposure. Nejde iba o odstránenie approval tlačidla. Automatizácia musí vytvoriť uzavretý control loop:

```text
candidate
→ evidence verdict
→ deployment mutation
→ controller convergence
→ runtime verification
→ business outcome
→ promote, stop alebo recover
```

Ak pipeline vykoná `kubectl apply` a označí job za successful, automatizovala iba mutation request. Continuous Deployment potrebuje aj read-back desired/live generation, rollout completion a outcome oracle.

Automatická policy musí rozlíšiť tri stavy:

```text
PASS
→ evidence potvrdzuje požadovaný subject

FAIL
→ test alebo policy našli porušenie

ERROR/MISSING
→ evidence sa nevytvorila alebo nedá vyhodnotiť
```

Fail-open preloží chýbajúci scanner report alebo nefunkčný analysis service na PASS. Pri required controls je bezpečnejší fail-closed alebo explicitný degraded decision s ownerom a časovým limitom.

Continuous Deployment zvyšuje požiadavky na batch size, observability, idempotenciu a recovery. Malá zmena sa ľahšie lokalizuje a roll-forwardne. Veľký batch s databázovou, aplikačnou a config zmenou vytvára viac recovery combinations.

Automatický rollback nie je univerzálna poistka. Ak nová verzia zapísala nekompatibilné dáta, publikovala eventy alebo vykonala external side effects, návrat image-u môže zhoršiť stav. Deployment policy preto pred exposure hodnotí per-layer rollback eligibility a môže namiesto rollbacku zvoliť feature disable, roll-forward alebo compensation.

''',
    "pipeline-stage-job-runner.md": r'''## Doplnenie výkladu: pipeline graph, job isolation a runner

**Pipeline** je jedna konkrétna execution instance vytvorená z versionovanej definície a eventu. **Stage** je logická skupina alebo ordering barrier. **Job** je jednotka execution s vlastnými commands, environmentom a výsledkom. **Runner** je agent, ktorý job prijme a spustí cez executor, napríklad shell, container alebo VM.

Tieto pojmy opisujú odlišné vrstvy:

```text
pipeline definition
→ resolved job graph
→ scheduler rozhodne readiness
→ runner vyberie job
→ executor vytvorí execution environment
→ commands vrátia exit statuses a artifacts
```

Stage-based pipeline často čaká, kým všetky jobs v predchádzajúcom stage skončia. DAG pipeline môže cez dependencies spustiť job skôr. Poradie v YAML preto nemusí byť reálne execution poradie.

Job success typicky vznikne z process exit statusu. Ak shell pipeline zakryje failure skoršieho commandu, CI systém vidí nulu a označí job green. Runner nevie, že business validation zlyhala.

Runner identity je trust boundary. Persistent shell runner môže zachovať workspace, credentials alebo cache medzi jobs. Ephemeral container znižuje residue, ale host daemon, mounted socket alebo privileged mode môžu stále poskytovať širokú authority.

Pri pending jobe kontroluj:

```text
job tags a protected status
→ dostupní runners
→ runner online/paused state
→ executor capacity
→ project/group eligibility
```

Successful job preukazuje execution na konkrétnom runneri a návratový stav commands. Nepreukazuje čistotu workspace, kompletnosť outputs ani dôveryhodnosť runner hosta bez ďalšej evidence.

''',
    "trigger-artifact-cache.md": r'''## Doplnenie výkladu: trigger, artifact a cache sú tri odlišné kontrakty

**Trigger** určuje, prečo a s akým security contextom pipeline vznikla. Push, pull request, tag, schedule, API call a upstream pipeline môžu mať odlišné permissions a vstupy. Rovnaký YAML preto nemusí vytvoriť rovnaký graph.

**Artifact** je output určený na ďalšie použitie ako evidence alebo release input. Má producer job, identity, retention a integrity contract. **Cache** je performance optimalizácia; jej obsah môže chýbať, byť starý alebo byť znovu vytvorený bez zmeny correctness.

```text
artifact:
required output, napríklad binary alebo test report

cache:
reusable acceleration, napríklad package download directory
```

Cache key určuje namespace obsahu. Key iba podľa branch name môže zdieľať nekompatibilné dependencies po zmene lockfile-u. Bezpečnejší key zahŕňa toolchain a dependency fingerprint.

```yaml
cacheKey: npm-${os}-${nodeVersion}-${lockfileSha}
```

Restore cache nepreukazuje provenance jednotlivých files. Untrusted fork nesmie zapisovať do cache namespace-u, ktorý trusted release job automaticky používa ako executable input.

Artifact hand-off potrebuje checksum/digest a producer identity. Ak downstream job iba stiahne `build.zip`, nevie, či pochádza z očakávaného candidate-u. Manifest môže viazať artifact digest na source a build job.

Trigger trust sa vyhodnocuje pred poskytnutím secrets alebo privileged runnera. Pull request z fork-u môže bezpečne spustiť read-only checks, ale nemá automaticky dostať production credentials. Event name samostatne nestačí; dôležitý je actor, repository/ref protection a resolved workflow source.

''',
    "environment-and-promotion.md": r'''## Doplnenie výkladu: environment identity a build-once promotion

Environment nie je iba názov `dev`, `staging` alebo `prod`. Je to konkrétny target subject:

```text
cloud account/subscription
+ region/cluster/namespace
+ configuration generation
+ data dependencies
+ credentials a policy
```

Dva clustre s rovnakým labelom `production` sú odlišné environments. Deployment evidence musí uviesť immutable target identity, nie iba human name.

**Promotion** znamená schválenie a presun tej istej release identity do ďalšieho exposure contextu. Pri build-once-promote-many sa artifact nerebuildí. Mení sa deployment record a environment configuration, nie aplikačné bytes.

```text
artifact digest A
→ staging deployment A
→ staging acceptance evidence pre A
→ production deployment A
```

Ak production job znovu buildne source, vznikne digest B. Aj pri rovnakom commite môžu timestamps, dependencies alebo builder vytvoriť odlišné bytes. Staging evidence pre A sa automaticky nevzťahuje na B.

Promotion record má viazať:

```text
release manifest digest
source environment evidence
cieľový environment identity/config generation
approval/policy generation
deployment operation ID
```

Environment protection riadi, kto alebo čo smie transition vykonať. Neoveruje automaticky, že live runtime načítal správny digest alebo config. Po promotion nasleduje target read-back a acceptance.

''',
    "quality-gates-and-approvals.md": r'''## Doplnenie výkladu: gate je rozhodovacia policy nad evidence

Quality gate nie je test. Je to policy, ktorá z viacerých evidence items vytvorí decision, či subject môže pokračovať do ďalšieho stavu.

```text
exact subject
+ required evidence inventory
+ policy generation
→ PASS, FAIL, ERROR alebo MISSING
→ allow alebo block transition
```

Gate musí najprv overiť completeness. Nulový počet security findings môže znamenať bezpečný artifact alebo chýbajúci scanner report. Ak sa `MISSING` preloží na PASS, gate je false-green.

Approval je ľudský alebo externý policy verdict nad konkrétnym subjectom. Schválenie textu „release 10.0“ je slabé, ak tag môže zmeniť digest. Approval má obsahovať release manifest digest, target environment a evidence snapshot.

Approval freshness sa invaliduje pri zmene subjectu alebo relevantnej policy. Nový commit, rebuilt artifact, zmenený deployment plan alebo force-push môže vyžadovať nové schválenie. UI status „approved“ bez subject bindingu je nedostatočný.

Separation of duties znamená, že rovnaká osoba alebo identity nemá nekontrolovane vytvoriť change, meniť evidence a schváliť production transition. Automatizácia môže presadzovať reviewer independence a protected environment roles, no emergency break-glass potrebuje audit, expiry a následnú reconciliation.

Gate failure musí byť diagnostický: čo chýba, ktoré pravidlo zlyhalo, pre aký subject a aký owner má reagovať. Neurčité „quality gate failed“ predlžuje feedback a podporuje obchádzanie.

''',
    "pipeline-as-code.md": r'''## Doplnenie výkladu: source YAML nie je resolved pipeline

Pipeline as Code ukladá workflow definition do versionovaného source-u, ale execution systém najprv vykoná ďalšie kroky: načíta includes/templates, aplikuje inheritance/defaults, vyhodnotí rules a vytvorí resolved graph.

```text
root pipeline file
+ included templates a versions
+ variables a event context
+ rules/conditions
→ resolved jobs, dependencies a permissions
```

Review jedného YAML file-u preto nemusí ukázať effective pipeline. Mutable include na `main` môže medzi dvoma runs zmeniť graph bez zmeny aplikačného commitu.

Syntax validation preukazuje iba parse a schema:

```bash
yamllint .gitlab-ci.yml
```

Linter nevie, ktoré jobs vzniknú pre tag, fork alebo schedule. Platformový compiled/config view alebo dry-run graph je silnejší read-back.

Pipeline source je executable authority. Zmena workflow môže získať secrets, meniť artifacts alebo deployovať. Untrusted pull request nemá používať vlastnú zmenenú workflow definition s production credentials. Trusted workflow source a untrusted application source sa niekedy oddeľujú.

Reproducibility vyžaduje pinned actions/images/templates a zaznamenaný resolved graph. Tag `v4` môže byť convenience locator, ale commit digest je presnejšia dependency identity.

Pipeline as Code neodstraňuje platform runtime state: runner config, protected variables, environment policy a scheduler behavior zostávajú mimo repository a musia sa read-backnúť.

''',
    "reusable-and-parallel-pipelines.md": r'''## Doplnenie výkladu: fan-out, shard manifest a fan-in

Parallel pipeline rozdelí prácu na viac jobs alebo matrix combinations. **Fan-out** vytvorí shards; **fan-in** zhromaždí ich outputs a rozhodne o complete výsledku.

```text
candidate
→ linux/windows/macos alebo test shard 1..N
→ per-shard result a artifact
→ fan-in completeness check
→ aggregate verdict
```

Zelený agregátor nie je dôveryhodný, ak nevie, koľko shards sa očakávalo. Potrebuje **shard manifest** obsahujúci exact inventory, napríklad platform, dependency version a test partition.

Matrix expression môže vytvoriť nula jobs pri chybnom filtri. Pipeline potom vyzerá green, hoci required platform sa nevykonala. Fan-in preto porovná expected a observed shard IDs.

Fail-fast zruší ostatné jobs po prvom failure. Šetrí čas, ale môže znížiť diagnostic evidence. Pri compatibility matrix môže byť vhodné nechať všetky shards dobehnúť a uložiť kompletný failure obraz.

Reusable workflow je versionovaný contract s inputs, outputs, secrets a permissions. Caller musí pinovať verziu a chápať defaults. Zmena template môže zmeniť runner image alebo gate behavior pre mnoho repositories naraz.

Outputs z parallel jobs potrebujú unikátne names a checksums. Ak všetky shards uploadnú `report.xml`, posledný môže prepísať ostatné. Aggregate report bez jedného shardu je `INCOMPLETE`, nie legitímne nižšie coverage.

''',
    "artifact-versioning.md": r'''## Doplnenie výkladu: checksum, hash, digest, signature a provenance

**Hash function** vezme ľubovoľné bytes a deterministicky z nich vypočíta hodnotu pevnej dĺžky. SHA-256 vytvára 256-bitový výsledok, ktorý sa zvyčajne zapisuje ako 64 hexadecimálnych znakov. Malá zmena vstupu vytvorí odlišný hash.

Pojmy **checksum** a **digest** sa v praxi prekrývajú. Checksum sa často používa pre hodnotu uloženú vedľa file-u na kontrolu poškodenia pri prenose. Digest zdôrazňuje content identity v registry alebo release manifeste. Kryptografický SHA-256 digest je vhodný na integrity kontrolu; jednoduché checksums ako CRC sú určené skôr na náhodné chyby, nie na odolnosť voči úmyselnej manipulácii.

Príkaz:

```bash
sha256sum dist/payments-migrations-10.0.0-rc.4.tar.gz \
  > dist/payments-migrations-10.0.0-rc.4.tar.gz.sha256
```

`sha256sum` otvorí archive, číta jeho bytes a vypočíta SHA-256. Shell redirection vytvorí checksum file obsahujúci hex digest a filename. Ak archive neexistuje alebo sa nedá čítať, command vráti non-zero; prázdny alebo partial output sa nemá publikovať ako validný checksum.

```bash
sha256sum --check \
  dist/payments-migrations-10.0.0-rc.4.tar.gz.sha256
```

`--check` načíta očakávaný digest a filename z checksum file-u, znovu vypočíta hash aktuálnych bytes a porovná hodnoty. `OK` preukazuje, že local archive zodpovedá tomuto checksum file-u.

Nevyriešená je otázka: kto vytvoril checksum file? Útočník, ktorý nahradí archive aj `.sha256`, dosiahne successful check. Preto sa trusted release manifest alebo checksum file podpisuje, prípadne sa digest viaže do cryptographic provenance.

Rozdiel:

```text
checksum/digest
→ identita a integrity bytes

signature
→ private key podpísal subject; verifier overí key/policy

provenance
→ tvrdenie o source, builderi a build inputs viazané na subject
```

Ani validný podpis nepreukazuje, že archive je bezpečný. Pred extraction treba kontrolovať allowed file paths, symlinks, ownership, permissions a content policy; tar archive môže obsahovať `../` path traversal alebo nečakané executable files.

''',
    "semantic-versioning.md": r'''## Doplnenie výkladu: SemVer je contract o kompatibilite, nie dôkaz kvality

Semantic Versioning zapisuje verziu ako `MAJOR.MINOR.PATCH` pre software s definovaným **public API**. Public API nie je iba HTTP endpoint. Môže zahŕňať package symbols, CLI flags, config schema, event payloads alebo behavior, na ktorý sa consumers spoliehajú.

```text
MAJOR
→ nekompatibilná zmena public contractu

MINOR
→ backward-compatible nová funkcionalita

PATCH
→ backward-compatible oprava
```

Version `2.4.1` sama nepreukazuje, že zmena je správne klasifikovaná. Tím musí vedieť, čo public contract zahŕňa a aké consumers existujú.

Pre-release:

```text
2.4.0-alpha.1 < 2.4.0-beta.1 < 2.4.0-rc.1 < 2.4.0
```

Pre-release versions majú nižšiu precedence než final release. Build metadata za `+`, napríklad `2.4.0+build.17`, nemení SemVer precedence a nemá sa používať ako jediná immutable artifact identity.

Breaking change môže byť skrytý v semantics: pole zostane string, ale zmení význam; timeout default sa skráti; event ordering sa zmení. Schema diff preto nemusí stačiť.

SemVer je komunikácia pre dependency resolver a používateľov. Nezaručuje security, support duration, artifact immutability ani deployment compatibility so zmenenou databázou. Release manifest stále potrebuje digest a compatibility metadata.

Ak sa už publikovaná version ukáže chybná, neprepisuje sa novými bytes. Vydá sa nová PATCH alebo ďalšia pre-release version. Rovnaké číslo s dvoma digestmi rozbíja resolver, cache aj audit.

''',
    "release-management.md": r'''## Doplnenie výkladu: release candidate, release record a lifecycle

Release management koordinuje technickú release identity, komunikáciu, support a recovery. **Release candidate** je konkrétna potenciálna release jednotka určená na finálne overenie; nie je to pohyblivá branch alebo priečinok `latest`.

Release record typicky obsahuje:

```text
release ID a logical version
source/candidate identity
artifact digests
configuration a schema contracts
evidence inventory
known risks a compatibility
owner, approval a timestamps
```

Changelog opisuje používateľsky alebo operatívne významné zmeny. Nie je automaticky generovaný zoznam commit messages. Release notes majú uviesť breaking changes, migration, feature flags, rollback limits a support dopady.

Release freeze obmedzuje transitions počas citlivého obdobia, ale nemá nahradiť readiness. Emergency exception potrebuje explicitný owner, scope, expiry a post-release review.

Publication, deployment a exposure sú odlišné udalosti. Artifact môže byť publikovaný, ale nikde nenasadený. Deployment môže existovať bez trafficu. Feature môže byť nasadená, ale disabled flagom.

Retirement zahŕňa koniec supportu, odstránenie artifactov podľa retention policy, revocation credentials a cleanup flags/config paths. Zmazanie tagu bez inventory running digests môže poškodiť recovery.

Release management sa uzatvára až vtedy, keď je známy outcome a evidence je archivovaná. Successful release job samostatne nepreukazuje user impact ani absenciu delayed side effects.

''',
    "recreate-deployment.md": r'''## Doplnenie výkladu: recreate ako explicitná downtime state machine

Recreate deployment najprv ukončí starú generation a až potom spustí novú. Výhodou je, že sa nemiešajú dve aplikačné verzie. Nevýhodou je obdobie bez dostupnej capacity.

```text
old serving
→ stop/drain old
→ zero serving capacity
→ start new
→ readiness
→ traffic resumes
```

Downtime nie je iba process startup time. Zahŕňa termination grace, volume detach/attach, scheduling, image pull, initialization, migration a readiness. Ak DNS alebo proxy cacheuje staré endpointy, user-visible failure môže trvať dlhšie.

Recreate je vhodný pre singleton workload, development prostredie alebo systém, kde mixed versions nie sú možné a downtime je prijateľný. Nie je automaticky bezpečný pre stateful service; nový process môže očakávať nekompatibilnú schema.

Precondition zahŕňa backup/recovery, capacity a exact target. Po stopnutí starej generation rollback už nemusí byť okamžitý, pretože staré Pods/processes boli zničené.

Readiness musí overovať schopnosť prijímať reálnu prácu. Process running alebo open port nepreukazuje načítanú config a dependency readiness. Acceptance pridáva business smoke a druhú operáciu.

''',
    "rolling-update.md": r'''## Doplnenie výkladu: surge, unavailable a dve súbežné cohorts

Rolling update postupne nahrádza staré replicas novými. Počas transition existujú minimálne dve cohorts s odlišnou generation.

`maxUnavailable` určuje, koľko desired replicas môže byť nedostupných. `maxSurge` určuje, koľko replicas nad desired count môže dočasne vzniknúť. Percentá sa prepočítavajú a zaokrúhľujú podľa controller contractu, preto malé deploymenty môžu mať prekvapivé absolútne hodnoty.

Pri desired `10`, `maxUnavailable=20%` a `maxSurge=30%` môže controller cieliť približne na minimálne 8 available a maximálne 13 total replicas. Existing unavailable baseline znižuje reálnu rezervu.

Readiness odstraňuje nový Pod z unavailable countu, ale nepreukazuje stabilitu počas observation window. Pod môže byť ready pred warm-upom alebo pred načítaním všetkých routes.

Traffic počas rolloutu smeruje na old aj new cohort. Session, cache, events a database musia byť mixed-version compatible. Ak nová verzia zapisuje formát, ktorý stará nevie čítať, samotné replica poradie problém nevyrieši.

Termination potrebuje drain: odstrániť endpoint eligibility, počkať na in-flight requests a až potom ukončiť process. Príliš krátky grace period vytvára reset connections.

Rollback controllera vytvorí ďalší rolling transition. Nie je instantný návrat a nemusí byť data-compatible.

''',
    "blue-green-deployment.md": r'''## Doplnenie výkladu: dve environments a samostatný traffic switch

Blue-green udržiava dve samostatné application generations. Jedna obsluhuje production traffic, druhá je candidate. Deployment a exposure sú oddelené transitions.

```text
blue active
→ deploy green
→ warm-up a verification green
→ traffic switch
→ observe
→ retire alebo ponechať blue na recovery
```

Farba nemá stabilný význam; po ďalšom release sa role môžu vymeniť. Evidence preto používa generation/digest, nie iba `green`.

Traffic switch môže byť load balancer target, Service selector, route weight alebo DNS. DNS zmena nie je okamžitá kvôli TTL a resolver caches, takže cohorts môžu určitý čas koexistovať.

Ak obe environments zdieľajú databázu, blue-green nie je plná izolácia. Candidate môže vykonať migration alebo side effect ovplyvňujúci active generation. Pre-release tests používajú read-only alebo izolované operácie, prípadne explicitný data compatibility contract.

Rollback trafficu je rýchly iba ak old environment zostáva healthy a kompatibilný so shared state. Dlhé ponechanie old environmentu zvyšuje cost a config drift; retirement má časový contract.

Switch response môže byť lost/unknown. Pred retryom sa read-backne effective route a active generation, aby sa traffic neprepol dvakrát alebo na nesprávny target.

''',
    "canary-deployment.md": r'''## Doplnenie výkladu: stabilná cohorta, baseline a analysis oracle

Canary vystaví novú generation obmedzenej časti trafficu alebo users a porovná outcome s baseline. Percento trafficu samo o sebe nevytvára kvalitný experiment.

Cohorta musí byť stabilná podľa user, tenant alebo request identity. Náhodné assignment per request môže poslať jednu session medzi versions a skryť stateful defects.

Canary analysis porovnáva compatible populations:

```text
old vs new generation
rovnaký región a request mix
rovnaké dependency conditions
rovnaký observation interval
```

Technical metrics zahŕňajú errors, latency, saturation a restarts. Business oracle zahŕňa final completion, correctness a forbidden side effects. Rýchle failed requests môžu znížiť latency, preto sa metrics segmentujú podľa result class.

Malá cohorta nemusí mať dostatok sample pre zriedkavé chyby. Absencia failure pri 100 requests nepreukazuje error rate 0.01 %. Analysis policy potrebuje minimálny sample alebo čas a confidence podľa rizika.

Automatic promotion musí rozlíšiť no-data od pass. Ak telemetry query zlyhá alebo canary nedostane traffic, verdict je `MISSING/ERROR`, nie green.

Abort zastaví ďalšie exposure a podľa eligibility odstráni canary. Potom sa overí, že route weight je nula, cohort nebeží a business backlog je reconciled.

''',
    "a-b-testing.md": r'''## Doplnenie výkladu: experiment, randomizácia a kauzálny výsledok

A/B test je experiment určený na odhad kauzálneho vplyvu variantu na outcome. Nie je to iba rollout na dve verzie.

Najprv sa definuje hypotéza, primary metric, guardrails a **unit of assignment**. Unit môže byť user, tenant alebo session. Musí zodpovedať tomu, kde vzniká interference a opakované správanie.

Randomizácia vytvára porovnateľné skupiny v priemere. Assignment sa má uložiť stabilne; per-request randomization mieša experience a porušuje assumptions.

**Sample Ratio Mismatch** znamená, že observed počet participants v A/B sa významne líši od očakávaného pomeru. Môže signalizovať chybu assignmentu, filtering alebo telemetry loss a diskvalifikuje causal interpretation.

Primary metric sa vyberá pred experimentom. Hľadanie ľubovoľnej zlepšenej metriky po výsledkoch zvyšuje false discoveries. Guardrails chránia napríklad error rate, latency, fraud alebo support contacts.

Statistical significance neznamená praktickú významnosť. Malý efekt pri obrovskom sample môže byť štatisticky presný, ale business bezvýznamný. Report uvádza effect size a interval neistoty.

A/B test neslúži ako jediný safety gate. Variant musí prejsť technickými controls pred experimentom. Experiment rozhoduje o value, nie o základnej correctness alebo security.

''',
    "shadow-deployment.md": r'''## Doplnenie výkladu: duplikovaný traffic bez authoritative side effectu

Shadow deployment posiela kópiu production inputu candidate systému, ale primary response používateľovi pochádza zo súčasnej active path. Cieľom je pozorovať behavior pri realistickom trafficu bez exposure výsledku.

```text
primary request
→ active system → authoritative response/side effect
↘ shadow copy → candidate observation only
```

Najväčšie riziko je side-effect suppression. Candidate nesmie chargeovať kartu, posielať email alebo publikovať authoritative event. Nestačí zahodiť HTTP response; side effects môžu vzniknúť hlbšie.

Shadow input môže obsahovať PII alebo secrets. Kopírovanie do iného environmentu potrebuje data classification, masking a retention policy. Produkčné credentials sa nemajú automaticky preniesť.

Porovnanie outputs musí normalizovať nondeterministické fields, timestamps a IDs. Rozdiel neznamená automaticky defect; candidate môže mať vedome nový behavior. Comparator potrebuje domain rules.

Shadow lag a dropped copies sú evidence. Ak mirror posiela iba 60 % requestov alebo sa oneskoruje, coverage je neúplná. Shadow success nepreukazuje user-facing latency, pretože response nie je na critical path.

Cleanup odstráni mirroring rules, shadow data a temporary credentials. Candidate nemá zostať ako skrytý permanentný consumer.

''',
    "ring-deployment.md": r'''## Doplnenie výkladu: ring ako stabilná risk cohorta

Ring deployment rozdeľuje populáciu do postupných cohort podľa rizika a reprezentatívnosti. Ring 0 môže byť interný tím, ďalší vybraní tenants a posledný všeobecná populácia.

Membership musí byť stabilné a auditovateľné. Ak sa users medzi rings presúvajú počas observation window, evidence sa mieša. Assignment môže používať tenant ID, account allowlist alebo region.

Rings nie sú iba percentá. Každý ring môže mať iný risk profil, support readiness a rollback capability. Interní users nemusia reprezentovať high-volume alebo regulated tenants, preto postupnosť zahŕňa rozmanité cohorts.

Promotion contract:

```text
ring subject a size
→ minimum observation/sample
→ technical a business criteria
→ explicit promotion
→ next ring
```

Failure v jednom ring-u zastaví ďalšie exposure. Recovery musí znížiť membership alebo disable behavior pre exact cohort a overiť, že membership cache sa aktualizovala.

Ring deployment sa môže kombinovať s canary, ale pojmy sa neprekrývajú úplne. Canary často hodnotí novú generation na malej traffic vzorke; rings sú dlhodobejšie named cohorts s ownershipom a support modelom.

''',
    "feature-flags.md": r'''## Doplnenie výkladu: flag evaluation je samostatný runtime control plane

Feature flag oddeľuje deployment bytes od behavior exposure. Aplikácia pri rozhodovacom bode vyhodnotí key, targeting context a flag generation.

```text
source default
+ remote flag state
+ targeting rules
+ SDK cache
+ user/tenant attributes
→ effective variant
```

Configured value v dashboarde nemusí byť loaded value v process-e. SDK polling, streaming outage alebo cache TTL môže udržať starú generation. Runtime telemetry má publikovať flag key/variant/generation bez citlivých attributes.

Typy flags:

- release flag dočasne skrýva novú funkcionalitu;
- experiment flag prideľuje variants;
- operational kill switch vypína rizikový path;
- permission/entitlement flag riadi produktový access, no nemá nahrádzať security authorization.

Fail-open alebo fail-closed behavior pri nedostupnom flag service je business a safety rozhodnutie. Kill switch pre nebezpečný write path môže failnúť closed; read-only cosmetic feature možno defaultovať inak.

Flags vytvárajú kombinatorický stav. Testovať všetky combinations nie je možné, preto sa obmedzuje počet súčasných flags a definujú forbidden combinations.

Flag má ownera a retirement date. Po plnom rolloute sa stará branch a config odstránia. Long-lived stale flags komplikujú reasoning a môžu náhodne znovu aktivovať nepodporovaný code path.

''',
    "progressive-delivery.md": r'''## Doplnenie výkladu: viac control planes a postupný verdict

Progressive delivery automatizuje alebo riadi postupné exposure podľa evidence. Môže kombinovať deployment cohorts, traffic weights, rings a feature flags. Každá os má vlastnú generation.

```text
application generation
traffic route generation
feature-flag generation
configuration/schema generation
```

Verdict musí vedieť, ktorá kombinácia bola pozorovaná. „Canary 10 %“ je neúplné, ak polovica canary cohorty mala flag off.

Controller vykonáva state machine: nastaví exposure, čaká na convergence, zbiera metrics, vyhodnotí analysis a rozhodne promote/hold/abort. Timeout alebo lost response môže zanechať unknown route state; pred ďalšou mutation sa vykoná read-back.

Analysis template je code/policy. Query musí mať správne labels, denominator a no-data semantics. Green dashboard screenshot nie je reprodukovateľný verdict.

Step duration musí pokryť warm-up a delayed outcomes. Príliš rýchle promotion môže prejsť skôr, než sa objavia queue, memory leak alebo business reconciliation failures.

Progressive delivery znižuje blast radius, nie pravdepodobnosť všetkých defectov. Shared database migration môže ovplyvniť 100 % users aj pri 1 % traffic canary.

''',
    "rollback-and-roll-forward.md": r'''## Doplnenie výkladu: recovery sa rozhoduje po vrstvách

Rollback znamená návrat určitej vrstvy na staršiu generation. Roll-forward znamená nasadenie novej opravy. Ani jeden pojem sám nehovorí, čo sa stalo s dátami, eventmi alebo external side effects.

Recovery matrix:

```text
application bytes
configuration
schema/data
events/messages
traffic/flags
external operations
```

Application rollback je vhodný iba ak stará verzia dokáže pracovať s aktuálnym shared state-om. Po destructive migration alebo novom event formáte môže byť nebezpečný.

Roll-forward býva lepší, keď je root cause známy a oprava malá, no vyžaduje čas na build/test/deploy. Feature disable môže rýchlo zastaviť nový path bez zmeny bytes. Compensation vytvorí business inverse operation, napríklad refund; nie je to technické zmazanie histórie.

Restore obnovuje dáta z recovery generation a môže stratiť novšie legitímne writes. Potrebuje reconciliation s external systems a RPO/RTO decision.

Unknown outcome sa nerieši blind retryom. Najprv sa query-ne operation ID, live route, deployment generation alebo provider ledger.

Recovery prejde až po overení original operation, forbidden duplicate path, adjacent cohorts a druhej novej operácie.

''',
    "database-compatibility-during-deployment.md": r'''## Doplnenie výkladu: expand/contract a mixed-version window

Počas rolling alebo progressive deploymentu stará a nová application version často používajú rovnakú databázu. Schema zmena preto musí byť kompatibilná počas **mixed-version window**.

Expand/contract pattern:

```text
expand:
pridať nový nullable column/table/index bez odstránenia starého contractu

migrate:
nová verzia dual-write/dual-read alebo backfilluje dáta

switch:
consumers prejdú na nový contract po overení completeness

contract:
odstrániť starý column/path až keď ho žiadna supported verzia nepoužíva
```

`ALTER TABLE` success nepreukazuje, že operation bola online alebo že replicas/backfill sú complete. DDL môže držať lock, prepísať table alebo zvýšiť replication lag. Plan zahŕňa engine/version a dataset size.

Backfill je production workload. Potrebuje batches, checkpoint, rate limit, idempotenciu a verification query. Stale backfill nesmie prepísať novší live write; používa conditional update alebo version comparison.

Dual-write môže vytvoriť partial outcome, ak jeden write uspeje a druhý zlyhá. Transaction alebo reconciliation contract musí určiť authority.

Schema version v migration table preukazuje, že migration runner zaznamenal krok. Nepreukazuje data completeness ani to, že všetky processes načítali nový model.

Contract removal je samostatný release po telemetry dôkaze, že starý field/path sa nepoužíva. Rollback eligibility sa posudzuje pred každou fázou.

''',
    "ci-cd-practical-walkthrough.md": r'''## Doplnenie výkladu: ako čítať artifact, digest a atomic promotion v walkthroughu

Praktický walkthrough používa deterministic artifact preto, aby rovnaké vstupy vytvorili stabilné bytes. Tar archive môže inak obsahovať timestamps, owner IDs alebo nestabilné file ordering. Digest potom identifikuje presný výsledok, nie iba source commit.

Keď sa vykoná:

```bash
sha256sum "$artifact" > "$artifact.sha256"
sha256sum --check "$artifact.sha256"
```

prvý command vytvorí digest aktuálnych bytes a druhý overí local equality. Trusted release flow uloží digest aj do release manifestu a viaže na build subject; samotný `.sha256` file sa dá nahradiť spolu s artifactom.

Staging a production promotion kopírujú alebo referencujú ten istý digest. Rebuild nie je promotion. Ak nový build vytvorí iný digest, potrebuje nové testy a approval.

Atomic active-generation switch v local modeli môže používať symlink alebo rename. Atomic znamená, že readers vidia starý alebo nový pointer, nie partial text. Neznamená to, že všetky running processes okamžite načítali nový target. Runtime read-back a business verification zostávajú potrebné.

Lost response po switchi vytvára unknown outcome. Správny postup je prečítať active pointer, candidate directory a ledger operation ID. Opakovanie switch commandu bez read-backu môže prepísať novšiu transition.

Walkthrough preto oddeľuje:

```text
artifact integrity
release manifest authority
deployment mutation
active generation
loaded runtime
business outcome
```

Každý successful command preukazuje iba svoju vrstvu.

''',
}

section_dir = REPO / "docs/05-ci-cd-and-release"
anchor_re = re.compile(
    r"(?m)^## (?:\d+\.\s*)?(?:Worked failure|Connected incident|Incident|Atlas incident|Troubleshooting flow|Zhrnutie|Anti-patterny)"
)

for filename, block in blocks.items():
    path = section_dir / filename
    text = path.read_text(encoding="utf-8")
    marker = block.splitlines()[0]
    if marker in text:
        raise RuntimeError(f"Expansion already present in {filename}")
    match = anchor_re.search(text)
    if match:
        text = text[: match.start()] + block + text[match.start() :]
    else:
        nav = "<!-- KNOWLEDGE-NAVIGATION:START -->"
        if nav not in text:
            raise RuntimeError(f"No insertion anchor in {filename}")
        text = text.replace(nav, block + nav, 1)
    path.write_text(text, encoding="utf-8")

readme_path = section_dir / "README.md"
readme = readme_path.read_text(encoding="utf-8")
anchor = "## Cieľ zvládnutia\n"
block = r'''## Rozšírený výklad pojmov, príkazov a release dôkazov

Všetkých 24 kapitol teraz pri kľúčových pojmoch a ukážkach explicitne vysvetľuje, čo mechanizmus znamená, načo sa používa, ako sa príkaz alebo controller transition vyhodnotí a čo jeho successful výsledok preukazuje alebo nepreukazuje. Doplnenia zachovávajú existujúce authoritative lifecycle, incidenty, commands a konfigurácie.

Rozšírenie pokrýva integration candidate a stale evidence, delivery/deployment readiness, pipeline graph a runner trust, trigger/artifact/cache hranice, immutable promotion, gate/approval subject, resolved Pipeline as Code, fan-out/fan-in, checksum/hash/digest/signature/provenance, SemVer a release lifecycle, state machines deployment stratégií, experiment/cohort/flag control planes, progressive delivery, per-layer recovery, database expand/contract a detailné čítanie end-to-end walkthroughu.

'''
if anchor not in readme:
    raise RuntimeError("Section 05 README anchor missing")
if "## Rozšírený výklad pojmov, príkazov a release dôkazov" not in readme:
    readme = readme.replace(anchor, block + anchor, 1)
readme_path.write_text(readme, encoding="utf-8")

ledger_path = REPO / "DOCUMENTATION-REVIEW-STATUS.md"
ledger = ledger_path.read_text(encoding="utf-8")
lines = ledger.splitlines()
replacement = "| `05-ci-cd-and-release` — CI/CD and Release Engineering | 24/24 prose-first practical and explanation-depth revalidation | Ready for user review | 2026-08-01 | Všetkých 24 kapitol zachováva pôvodný release-engineering lifecycle a dopĺňa mechanické vysvetlenie pojmov, príkazov, controller transitions a evidence verdictov. Rozšírenie pokrýva integration candidate, delivery/deployment, pipeline/runner, trigger/artifact/cache, promotion, gates, resolved pipelines, fan-out/fan-in, checksum/hash/digest/signature/provenance, SemVer, release lifecycle, deployment strategies, canary/experiment/shadow/rings/flags, progressive delivery, per-layer recovery, database expand/contract a praktický walkthrough. Navigation, glossary a full documentation audit boli synchronizované. |"
found = False
for index, line in enumerate(lines):
    if line.startswith("| `05-ci-cd-and-release`"):
        lines[index] = replacement
        found = True
        break
if not found:
    raise RuntimeError("Section 05 ledger row missing")
ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

run("python", "scripts/update_glossary.py", "--write")
run("python", "scripts/update_navigation.py", "--write")
run("python", "scripts/audit_learning_depth.py", "--all-docs")

workflow_path = REPO / ".github/workflows/knowledge-navigation.yml"
workflow = workflow_path.read_text(encoding="utf-8")
step = '''      - name: Expand Section 05 explanations
        if: github.event_name == 'pull_request'
        shell: bash
        run: |
          set -euo pipefail
          "$PYTHON_BIN" scripts/expand_section_05_explanations.py

'''
if workflow.count(step) != 1:
    raise RuntimeError("Temporary Section 05 workflow step missing")
workflow_path.write_text(workflow.replace(step, "", 1), encoding="utf-8")
Path(__file__).unlink()

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run("git", "add", "docs/05-ci-cd-and-release", "DOCUMENTATION-REVIEW-STATUS.md", "GLOSSARY.md", "glossary", "DOCUMENTATION-AUDIT.md", "documentation-audit.json", ".github/workflows/knowledge-navigation.yml", "scripts")
run("git", "commit", "-m", "docs(release): deepen explanations across Section 05")
run("git", "push", "origin", f"HEAD:{BRANCH}")
