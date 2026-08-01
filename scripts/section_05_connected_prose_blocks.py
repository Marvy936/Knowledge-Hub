from __future__ import annotations

BLOCKS: dict[str, str] = {
    "docs/05-ci-cd-and-release/continuous-integration.md": r'''## Ako vzniká dôveryhodný integration candidate

Continuous Integration neoveruje izolovanú feature branch, ale konkrétny candidate, ktorý by po integrácii existoval v cieľovej histórii. Keď sa target branch medzi spustením testov a mergeom zmení, starý zelený výsledok môže byť stale. Dve branches môžu byť jednotlivo zelené a napriek tomu vytvoriť nekompatibilnú kombináciu.

Candidate preto potrebuje exact identity. Merge queue alebo CI systém môže vytvoriť synthetic merge commit, ktorý spája aktuálny feature tip s aktuálnym targetom. Test evidence sa viaže na commit alebo tree tohto kandidáta, resolved workflow generation, build inputs a runner trust boundary. Samotný názov branch alebo pull requestu nie je stabilný subject.

Build má začať z čistého workspace-u a z deklarovaných dependencies. Warm runner, generated files alebo shared cache môžu vložiť bytes, ktoré nie sú súčasťou candidate tree-u. Cache môže zrýchliť dependency resolution, ale nesmie byť autoritou pre release output. Reprodukovateľný build zaznamená compiler, base image, lock files a build script generation.

CI verdict vznikne až po complete fan-in požadovaných kontrol. Zelený unit shard nepreukazuje, že integration, security alebo platform matrix prešli. Missing shard nie je success; pipeline má rozlišovať `FAIL`, `ERROR` a `MISSING`. Výsledok platí iba pre candidate, nad ktorým sa kontroly skutočne vykonali.

Po mergei sa môže vyžadovať ďalšia validácia, ak publish alebo release používa inú workflow generation, credentials či runner class. Continuous Integration tak nie je synonymom pre „všetky branches sú zelené“, ale mechanizmom, ktorý udržiava hlavný integračný subject v známom a reprodukovateľnom stave.

''',
    "docs/05-ci-cd-and-release/continuous-delivery.md": r'''## Ako sa artifact stane pripraveným na release

Continuous Delivery znamená, že každý akceptovaný candidate môže prejsť do releasable stavu opakovateľným a kontrolovaným procesom. Neznamená automatické nasadenie do production. Delivery pipeline vytvára immutable artifact, viaže k nemu complete evidence a pripravuje promotion tak, aby release nevyžadoval nový build alebo nezdokumentovanú manuálnu úpravu.

Deployable artifact musí mať presnú content identity, podporovanú configuration contract a známe runtime požiadavky. Zelené testy nad source revision nestačia, ak deployment neskôr zostaví iné bytes. Build-once-promote-many preto oddeľuje vytvorenie artifactu od jeho expozície v prostrediach. Staging a production majú dostať rovnaký digest; meniť sa môže environment-specific configuration, ktorej generation sa zaznamená samostatne.

Release readiness je rozhodnutie nad subject-bound evidence. Zahŕňa testy, security findings, provenance, compatibility a recovery eligibility. Manual approval môže byť súčasťou policy, ale človek nemá schvaľovať iba názov version. Approval sa viaže na exact artifact, release manifest, target environment a evidence generation. Ak sa ktorýkoľvek z týchto vstupov zmení, approval je stale.

Delivery pipeline pripravuje aj rollback alebo roll-forward cestu, retention last-known-good artifacts a runbook pre unknown outcomes. To, že candidate je „ready to deploy“, nepreukazuje, že production mutation už prebehla ani že runtime loaded state a business outcome sú správne. Tieto dôkazy patria do deployment a post-deployment lifecycle-u.

''',
    "docs/05-ci-cd-and-release/continuous-deployment.md": r'''## Ako funguje automatický production feedback loop

Continuous Deployment automaticky posúva candidate do production, keď prejde definovanými gates. Automatizácia neodstraňuje rozhodovanie; premieňa ho na versionovanú policy nad presným subjectom a evidence. Ak policy nevie odlíšiť chýbajúci report od zeleného výsledku, automatický deployment iba zrýchli false-green transition.

Production release je viac než úspešné API volanie na deployment controller. Pipeline najprv publikuje alebo vyberie immutable artifact, potom zmení desired state, čaká na controller convergence, overí loaded runtime identity a až následne vyhodnotí traffic a business outcome. Každý krok môže skončiť successom, failure alebo unknown outcome-om.

Automatický feedback loop potrebuje bounded exposure a abort policy. Pri canary alebo progressive rollout-e sa traffic zvyšuje iba po splnení technických a business oraclov. No-data, telemetry error alebo nedostatočný sample nesmie byť interpretovaný ako pass. Pri zlyhaní sa zastaví nová expozícia a zvolí recovery podľa application, configuration, data a external side-effect state-u.

Rollback nie je univerzálna odpoveď. Stará application môže byť po schema alebo event zmene nekompatibilná a timeout počas route transition môže mať neznámy výsledok. Automation preto najprv observe-ne effective state a až potom rozhodne o rollbacku, roll-forwarde, flag disable, compensation alebo restore.

Continuous Deployment je dôveryhodný iba vtedy, keď uzatvára celý reťazec od immutable candidate-u po verifikovaný production outcome a druhú operáciu. Zelená pipeline bez runtime a business read-backu je iba úspešná orchestrácia, nie potvrdený release.

''',
    "docs/05-ci-cd-and-release/pipeline-stage-job-runner.md": r'''## Ako sa pipeline mení na reálne procesy na runneri

Pipeline je versionovaný execution graph. Stage zoskupuje jobs podľa dependency alebo policy, job je konkrétna jednotka práce a runner je runtime, ktorý ju skutočne vykoná. Graf v YAML nepreukazuje, že job dostal očakávaný image, credentials, filesystem alebo network path. Resolved graph a runner environment sú samostatné evidence.

Scheduler vyberá runner podľa labels, capacity a protection rules. Persistent runner môže zachovať workspace, containers alebo credentials z predchádzajúceho jobu; ephemeral runner znižuje tento drift, ale stále potrebuje pinned image a bootstrap. Privileged Docker socket alebo broad cloud role rozširujú trust boundary pipeline-u a musia byť viazané na trusted triggers.

Job success je odvodený z exit statusov jednotlivých steps a z pravidiel shellu. Pipeline môže byť zelená, ak validator zlyhá v pipeline bez `pipefail`, ak script prehltne exception alebo ak native command exit code nie je skontrolovaný. Machine-readable result a diagnostics majú oddelené streams, aby ďalší job neparsoval progress text ako artifact.

Artifacts prenášajú výstup medzi jobs a musia mať digest, producer identity a retention. Workspace alebo cache nie je spoľahlivý hand-off, pretože môže byť mutable a neúplný. Downstream job má overiť manifest a checksum skôr, než výstup použije.

Pri diagnóze sa postupuje od resolved graphu cez scheduler decision, runner identity, checkout subject, environment a process exit až po publikované evidence. Zelená stage ikona bez týchto detailov nehovorí, ktorý kód a runtime skutočne vytvorili výsledok.

''',
    "docs/05-ci-cd-and-release/trigger-artifact-cache.md": r'''## Ako odlíšiť trigger, artifact a cache

Trigger je udalosť, ktorá vytvorí pipeline run. Push, pull request, tag, schedule alebo manual dispatch majú odlišný trust a data contract. Fork pull request nemá automaticky dostať production credentials iba preto, že používa rovnaký workflow file. Pipeline musí explicitne rozhodnúť, ktorý source revision a workflow generation sa pri danom evente vykonajú.

Artifact je výstup, ktorý má byť predmetom ďalšieho overovania, promotion alebo deploymentu. Musí mať immutable identity, producer metadata a integrity check. Cache je iba optimalizácia pre drahé, znovu použiteľné vstupy, napríklad dependency download alebo compiler cache. Cache hit nepreukazuje správnosť a cache miss nesmie meniť semantic výsledok buildu.

Cache key určuje, kedy sa obsah môže zdieľať. Príliš široký key umožní nekompatibilným branches alebo nedôveryhodnému triggeru obnoviť poisoned output. Key preto zahŕňa relevantný lockfile, toolchain a trust namespace. Generated release artifact sa nemá publikovať iba tým, že bol nájdený v cache; musí prejsť trusted build alebo explicitnú provenance kontrolu.

Artifacts a caches majú odlišnú retention a failure semantics. Chýbajúci artifact blokuje downstream transition, pretože evidence alebo bytes nie sú kompletné. Chýbajúca cache iba spomalí job a vedie k čistému recompute. Ak pipeline tieto stavy zlieva, môže pri cache restore pokračovať s neovereným outputom.

Pri incident-e sa preto sleduje trigger identity, resolved workflow, cache key a writer, artifact manifest a downstream digest. Rovnaký filename alebo tag nie je dôkaz, že ide o rovnaké bytes alebo trusted producer.

''',
    "docs/05-ci-cd-and-release/environment-and-promotion.md": r'''## Ako funguje immutable promotion medzi prostrediami

Environment nie je iba názov `staging` alebo `production`. Je to konkrétny account, region, cluster, namespace, configuration generation, identity a dependency set. Promotion rozhoduje, že už overený artifact môže byť použitý v ďalšom environment subjecte. Nemá vytvárať nový build ani meniť artifact pod rovnakou version.

Build-once-promote-many zachováva content digest naprieč prostrediami. Staging evidence potom patrí tým istým bytes, ktoré neskôr dostane production. Environment-specific configuration zostáva samostatným inputom; release manifest viaže artifact digest s configuration schema a target identity. Ak staging používa inú feature alebo dependency contract než production, tento rozdiel musí byť explicitný v acceptance.

Promotion record obsahuje source environment alebo evidence bundle, target environment, artifact, config generation, policy a approval identity. Manual copy alebo tag rewrite bez tohto subjectu ničí audit. Ak registry replication prekopíruje image, destination digest sa musí porovnať so source a podľa platformy treba overiť celý manifest graph.

Successful deployment response ešte nepreukazuje promotion outcome. Read-back overí controller revision, runtime image ID, loaded configuration, route alebo traffic state a business synthetic. Pri unknown outcome-e sa mutation neopakuje naslepo; najprv sa prečíta target environment a release ledger.

Promotion sa uzatvára až po evidence closure a retention. Last-known-good artifact a jeho configuration musia zostať dostupné počas recovery window. Environment label bez presnej identity nestačí na podporu ani rollback.

''',
    "docs/05-ci-cd-and-release/quality-gates-and-approvals.md": r'''## Ako gate a approval rozhodujú nad presným subjectom

Quality gate je automatizované policy rozhodnutie nad evidence. Gate nevytvára kvalitu sám; interpretuje test results, findings, coverage, provenance alebo runtime metrics pre konkrétny subject. Preto musí poznať artifact alebo candidate identity, policy generation, complete evidence inventory a target transition.

Verdict má viac stavov než zelený a červený. `FAIL` znamená, že subject porušil kontrolu. `ERROR` znamená, že kontrola sa nevedela korektne vykonať. `MISSING` znamená, že povinná evidence nebola dodaná. Pre required control sa error ani missing nesmie preložiť na pass, inak outage scanneru alebo stratený artifact otvorí release cestu.

Approval je ľudské rozhodnutie nad rovnakým presným subjectom. Reviewer potrebuje vidieť artifact digest, release manifest, target environment, zmenu risku a relevantné evidence. Schválenie názvu `10.0.0` alebo pipeline URL bez content identity je nejednoznačné. Zmena artifactu, configu, policy alebo environment generation musí approval invalidovať.

Separation of duties môže vyžadovať iného autora a approvera, ale počet kliknutí nie je bezpečnostný dôkaz. Approval má jasné rozhodovacie kritériá a audit trail. Emergency override potrebuje bounded scope, dôvod, expiry a následnú reconciliáciu, nie permanentný bypass required gates.

Po gate alebo approval success sa ešte overuje, že downstream transition použil schválený subject. Ak deployment job znovu resolve-ne mutable tag, môže nasadiť iné bytes než tie, ktoré boli testované. Gate preto musí byť viazaný na immutable release manifest, nie iba na poradie jobov.

''',
    "docs/05-ci-cd-and-release/pipeline-as-code.md": r'''## Ako sa source pipeline zmení na resolved execution graph

Pipeline as Code ukladá orchestration contract do versionovaného source-u, ale runner nevykonáva iba jeden YAML file. Systém spracuje includes, templates, reusable workflows, variables, conditions a matrix expansion a vytvorí resolved execution graph. Tento resolved graph je skutočný plán jobov, dependencies, images, permissions a rules pre konkrétny run.

Mutable include alebo action ref môže zmeniť graph bez zmeny aplikačného commit-u. Preto sa externé templates a actions pinujú na immutable revision a ich identity patria do release evidence. Review lokálneho YAML nepreukazuje, čo platforma po expanzii vykoná; pipeline compiler alebo platform API má vedieť zobraziť resolved formu.

Validation prebieha na viacerých vrstvách. Syntax check potvrdí, že YAML sa dá parse-nuť. Schema alebo platform lint overí podporované keys. Policy kontroluje permissions, untrusted triggers a secret exposure. Dry-run alebo graph inspection overí dependencies a conditions. Až reálny run potvrdí runner, network a tool behavior.

Pipeline code je súčasťou trusted build inputs. Pull request, ktorý mení workflow, môže meniť spôsob testovania aj publication. Untrusted change nemá dostať release credentials skôr, než trusted revision workflowu znovu overí candidate. Oddelenie source change a privileged execution je kľúčová supply-chain hranica.

Pri troubleshootingu sa porovná source pipeline revision, resolved graph, runtime job metadata a artifacts. Zelený run podľa inej template generation nemôže byť automaticky použitý ako evidence pre nový graph.

''',
    "docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md": r'''## Ako fungujú fan-out, shardy a fan-in

Reusable pipeline oddeľuje spoločný workflow contract od konkrétnej aplikácie. Caller poskytuje versionované inputs a callee definuje jobs, permissions a outputs. Reuse znižuje duplicitu, ale vytvára dependency: mutable ref alebo nekompatibilná zmena template môže zmeniť veľa pipelines naraz. Caller preto pinne callee revision a evidence zaznamená resolved template.

Parallelizácia rozdelí kontrolu na shardy podľa platformy, test suite, regiónu alebo package-u. Každý shard potrebuje rovnaký candidate a kompatibilný toolchain, ale má vlastnú identity a output. Fan-out znižuje čas, nie požiadavku na úplnosť. Zelených deväť shardov z desiatich nepredstavuje deväťdesiatpercentný pass.

Fan-in job načíta manifest očakávaných shardov a porovná ho s prijatými artifacts. Kontroluje candidate SHA, workflow generation, shard key, status, report digest a producer. Missing, duplicate alebo stale shard vedie k `INCOMPLETE`, nie k successu. Retry jedného shardu nesmie zmiešať output z dvoch candidate generations.

Matrix include/exclude rules sú súčasťou resolved graphu. Chybná condition môže ticho odstrániť arm64 alebo security variant. Preto sa očakávaný shard inventory generuje nezávisle od samotných results a review zobrazuje, ktoré dimensions boli pokryté.

Reusable a parallel pipeline je dôveryhodná až vtedy, keď sa dá spätne preukázať complete graph od caller inputov cez všetky shardy po jediný fan-in verdict a immutable artifact.

''',
    "docs/05-ci-cd-and-release/artifact-versioning.md": r'''## Ako checksum, digest, podpis a provenance chránia artifact

Hash function číta bytes a deterministicky z nich vypočíta hodnotu pevnej dĺžky. SHA-256 vytvára 256-bitový výsledok, ktorý sa bežne zapisuje ako 64 hexadecimálnych znakov. Aj malá zmena vstupu vedie k inému hashu. Keď sa táto hodnota používa na identifikáciu obsahu, hovoríme často o **digest-e**; názov **checksum** sa používa najmä pri kontrole, či sa file počas prenosu alebo uloženia nezmenil.

Pre migration archive možno vytvoriť checksum file:

```bash
sha256sum dist/payments-migrations-10.0.0-rc.4.tar.gz \
  > dist/payments-migrations-10.0.0-rc.4.tar.gz.sha256

sha256sum --check \
  dist/payments-migrations-10.0.0-rc.4.tar.gz.sha256
```

Prvý command otvorí archive, vypočíta SHA-256 a shell uloží digest spolu s filename-om. Druhý command načíta očakávanú hodnotu, znovu vypočíta hash aktuálnych bytes a porovná ich. Výsledok `OK` preukazuje zhodu archive-u s daným checksum file-om. Nepreukazuje však, kto checksum vytvoril. Útočník, ktorý nahradí archive aj `.sha256`, môže dosiahnuť rovnaký success.

**Signature** pridáva kryptografické tvrdenie, že konkrétny subject podpísal držiteľ private key alebo identity akceptovanej verifier policy. **Provenance** opisuje source revision, build definition, buildera a vstupy, z ktorých artifact vznikol. Podpis môže viazať provenance k digestu, ale verifier stále musí skontrolovať obsah claims a dôveryhodnosť identity.

Ani platný digest a podpis nepreukazujú, že archive je bezpečný na extraction alebo funkčne správny. Tar môže obsahovať `../` path traversal, symlink mimo targetu, nečakané permissions alebo executable files. Content policy, sandbox extraction a testy dopĺňajú integrity a authenticity.

Logical version pomáha ľuďom hovoriť o kompatibilite, no exact bytes identifikuje digest. Release manifest preto viaže version, artifacts, platform manifests, configuration contract, SBOM, signature a provenance do jednej immutable release unit.

''',
    "docs/05-ci-cd-and-release/semantic-versioning.md": r'''## Ako čítať Semantic Versioning ako compatibility contract

Semantic Versioning zapisuje version ako `MAJOR.MINOR.PATCH` a vyjadruje tvrdenie o zmene verejného contractu. `PATCH` má byť backward-compatible oprava, `MINOR` backward-compatible rozšírenie a `MAJOR` breaking change. Schéma nemeria kvalitu ani veľkosť diffu; komunikuje očakávania consumerom a dependency resolverom.

Najťažšia časť nie je zvýšiť číslo, ale definovať **public API**. Do contractu môžu patriť HTTP fields, events, CLI flags, configuration keys, database schema pre externých consumerov alebo behavior a error semantics. Zmena enum hodnoty či default timeoutu môže byť breaking, hoci function signature zostane rovnaká.

Pre-release identifikátor, napríklad `10.0.0-rc.4`, má nižšiu precedence než final version a signalizuje nestabilný candidate. Build metadata za `+` nemení precedence a nemá sa používať na rozlíšenie dvoch podporovaných obsahov pod rovnakou version. Exact bytes stále identifikuje digest.

Automation môže navrhnúť bump z conventional commits alebo diffu schémy, ale final verdict potrebuje ownera verejného contractu. Tool nevie automaticky poznať všetkých hidden consumerov alebo business semantics. Compatibility tests a deprecation policy poskytujú dôkaz, ktorý samotný názov version nemá.

Ak dva buildy publikujú rovnakú logical version s odlišnými digestmi, vzniká collision. Správna reakcia je zastaviť publication a vyšetriť inputs, nie prepísať starý artifact. SemVer zostáva komunikačný contract; immutable content identity a release manifest zostávajú technickou autoritou.

''',
    "docs/05-ci-cd-and-release/release-management.md": r'''## Ako sa candidate zmení na podporovaný release

Release management riadi lifecycle od candidate-u po podporovaný, komunikovaný a neskôr vyradený release. Candidate je presná kombinácia source, artifacts, configuration contractu a evidence, ktorá ešte nemusí byť schválená na všeobecnú expozíciu. Publication vytvorí immutable release manifest a sprístupní artifacts; deployment a traffic activation sú ďalšie samostatné transitions.

Release manifest je authority pre to, čo version obsahuje. Viaže API, worker, migrations, chart, schema a evidence digests. Release notes sú ľudská komunikácia, nie náhrada manifestu. Podpora potrebuje vedieť, ktoré versions sú active, deprecated, revoked a dostupné pre recovery.

Go/no-go rozhodnutie vychádza z risku, compatibility, operability a recovery eligibility. Calendar alebo deadline môže ovplyvniť priority, ale nemá meniť chýbajúce evidence na pass. Exception musí mať bounded scope, explicitný residual risk, ownera a follow-up.

Release nekončí production deploymentom. Tím sleduje adoption, incidents, support signals a business outcomes. Last-known-good artifacts, configuration a database compatibility sa udržiavajú počas deklarovaného recovery window. Revocation musí blokovať ďalšiu promotion a podľa rizika aj runtime admission; delete tagu samotný bežiace digests nezastaví.

Retirement uzatvára dependency a support lifecycle. Pred odstránením starej version sa overia consumeri, rollback claims, data formats a backlog. Release management tak spája technickú identity s komunikáciou, supportom a bezpečným ukončením používania.

''',
    "docs/05-ci-cd-and-release/recreate-deployment.md": r'''## Ako funguje recreate deployment state machine

Recreate deployment najprv ukončí starú generation a až potom spustí novú. Jeho hlavnou vlastnosťou je explicitný interval bez aplikačnej kapacity. Táto stratégia môže byť vhodná pri single-writer workload-e, nekompatibilnom local state alebo systéme, kde mixed-version prevádzka nie je možná, ale downtime musí byť súčasťou schváleného contractu.

Pred zastavením starej generation sa overí, že nový artifact a configuration sú dostupné, migrácie majú známu eligibility a existuje recovery cesta. Drain musí uzavrieť alebo presmerovať nové requests, dokončiť či bezpečne uložiť in-flight prácu a zachovať operation identities. Process stop bez business drainu môže zanechať unknown side effects.

Po vypnutí sa read-backom potvrdí, že staré procesy, endpoints a writers naozaj zmizli. Až potom sa vykoná migration alebo spustí nová generation. Startup success a readiness nie sú final verdict; služba musí prejsť reálnou route, loaded configuration a business synthetic.

Ak nový release zlyhá, rollback je možný iba vtedy, keď stará application zostala kompatibilná s aktuálnymi dátami a external effects. Ak migration už contractla schema alebo nový writer emitoval neznámy event, recovery môže vyžadovať roll-forward, restore alebo compensation.

Recreate je jednoduchý v počte cohort, ale náročný na správne modelovanie downtime a state-u. Jeho bezpečnosť nevzniká z príkazu „stop all, start all“, ale z preconditions, drainu, explicitnej outage komunikácie a overeného recovery postupu.

''',
    "docs/05-ci-cd-and-release/rolling-update.md": r'''## Ako funguje rolling update počas mixed-version intervalu

Rolling update postupne nahrádza staré repliky novými, takže určitý čas bežia obe generations súčasne. Tento **mixed-version interval** je hlavná compatibility boundary. Staré a nové processes musia spolupracovať s rovnakou databázou, eventmi, caches a klientmi, kým posledná stará replika neodíde.

`maxSurge` určuje, koľko nových replík možno vytvoriť nad desired count. `maxUnavailable` určuje, koľko požadovaných replík môže byť dočasne nedostupných. Percentá sa prepočítavajú na absolútne hodnoty a musia sa hodnotiť spolu s existujúcim unhealthy baseline-om. Ak je kapacita porušená už pred rolloutom, ďalšie odstránenie starej batch môže spôsobiť outage aj pri syntakticky validnej stratégii.

Readiness má odpovedať, či konkrétna nová replika dokáže bezpečne dostať traffic v aktuálnom shared state-e. Process health alebo otvorený port nestačí. Controller status a EndpointSlice dokazujú deployment a routing eligibility, ale business synthetic musí potvrdiť reálnu operáciu. Pomer replík navyše nemusí zodpovedať pomeru requestov pri sticky sessions alebo nerovnomernom load balancingu.

Pred odstránením ďalšej starej batch sa sleduje capacity, error/latency, queue a compatibility. Terminating Pod potrebuje drain a grace period; in-flight writes a background jobs sa musia dokončiť alebo odovzdať bez duplication.

Rollback vytvorí ďalší rolling transition a je bezpečný iba pri zachovanej backward compatibility. Ak nová generation už zmenila schema alebo event semantics, návrat image-u nemusí obnoviť systém. Rolling update je preto state machine nad application aj shared state-om, nie iba poradie Podov.

''',
    "docs/05-ci-cd-and-release/blue-green-deployment.md": r'''## Ako funguje blue-green prepnutie

Blue-green deployment udržiava dve oddelené application generations. Jedna obsluhuje production traffic a druhá sa pripravuje a overuje bez všeobecnej expozície. Názvy farieb nie sú identity; release manifest musí presne povedať, ktorý artifact, configuration a environment predstavujú active a candidate stranu.

Candidate potrebuje kapacitu, dependencies a data access porovnateľné s active prostredím. Warm-up, cache a background jobs sa musia navrhnúť tak, aby candidate nevykonával duplicitné side effects ešte pred prepnutím. Ak obe strany zdieľajú databázu, schema a event contracts musia byť kompatibilné pre obe generations.

Traffic switch je samostatná mutation route, load balancera alebo DNS. API success pri zmene konfigurácie nepreukazuje effective traffic. Read-back sleduje route generation, actual request distribution a business synthetics. Pri DNS treba rátať s cache a TTL; pri proxy s existing connections a session affinity.

Rollback môže byť rýchly, ak staré prostredie zostalo warm a kompatibilné. Nie je však automaticky bezpečný po data migration, new events alebo external side effects. Unknown outcome počas switchu sa rieši observation-first: najprv sa zistí effective route a in-flight cohort, potom sa vykoná ďalšia mutation.

Po stabilizácii sa old environment nevypína okamžite bez retention a recovery decisionu. Blue-green kupuje oddelenie a rýchly traffic reversal za dvojnásobnú kapacitu a potrebu riadiť shared state. Jeho hodnota závisí od presného switch a compatibility contractu.

''',
    "docs/05-ci-cd-and-release/canary-deployment.md": r'''## Ako vyhodnocovať canary cohortu

Canary vystaví novú generation obmedzenej časti users alebo trafficu a porovná jej outcome so stable baseline. Percento replík alebo route weight samo o sebe nevytvára dôveryhodnú cohortu. Assignment musí byť stabilný podľa identity, ktorá zodpovedá workflowu, napríklad account alebo tenant. Náhodné rozhodnutie pri každom requeste môže jednu session rozdeliť medzi versions a skryť stateful defect.

Porovnanie potrebuje compatible populations. Stable a canary majú mať rovnaký región, request mix, dependency route a observation interval. Ak canary dostane iba low-volume tenantov alebo inú provider cestu, rozdiel nemožno pripísať samotnému release-u.

Technical oracle sleduje errors, latency, saturation a restarts. Business oracle sleduje final completion, correctness a forbidden side effects. Rýchle failures môžu znížiť priemernú latency, preto sa výsledky segmentujú podľa result class. Denominator má pochádzať z authoritative admitted operations, nie iba z requestov, ktoré dosiahli úspešnú instrumentation path.

Malý sample nevie vylúčiť zriedkavý defect. Analysis policy preto stanoví minimálny počet operácií alebo čas a rozlišuje `PASS`, `FAIL`, `MISSING` a `INCONCLUSIVE`. No-data pri nulovom trafficu alebo pokazenej query nie je success.

Abort zastaví novú expozíciu, ale musí zachovať identity a reconciliovať in-flight canary work. Route weight nula nepreukazuje, že pending alebo unknown operations boli bezpečne uzavreté. Promotion pokračuje až po technickom aj business verdikte a druhom stabilnom observation windowe.

''',
    "docs/05-ci-cd-and-release/a-b-testing.md": r'''## Ako A/B test oddeľuje release safety od causal inference

A/B test je experiment, ktorý odhaduje kauzálny vplyv variantu na používateľský alebo business outcome. Canary sa primárne pýta, či je release bezpečný; A/B test sa pýta, či zmena spôsobila rozdiel. Tieto otázky môžu používať podobnú traffic infraštruktúru, ale potrebujú odlišný assignment a analysis contract.

Experiment unit musí byť stabilná, napríklad user alebo account. Randomizácia raz priradí unit do control alebo treatment a assignment generation sa zachová počas celej journey. Per-request randomization mieša skúsenosť a porušuje nezávislosť observations. Sample-ratio mismatch môže odhaliť chybu v routingu, eligibility alebo telemetry ešte pred interpretáciou výsledkov.

Primary metric sa vyberá pred experimentom a opisuje hypothesized outcome. Guardrails sledujú bezpečnosť, napríklad errors, fraud alebo support contacts. Veľké množstvo post-hoc metrík zvyšuje riziko náhodného „víťazstva“. Analysis potrebuje sample size, observation window a pravidlá pre delayed outcomes.

Štatistická významnosť nie je automaticky business význam. Malý merateľný rozdiel môže byť prevádzkovo bezcenný, zatiaľ čo široký confidence interval môže znamenať, že experiment nemá dostatok dát. Segmenty a exclusions musia byť deklarované vopred, aby tím nevyberal iba cohortu s priaznivým výsledkom.

A/B test nesmie obchádzať release safety. Treatment artifact a runtime musia najprv prejsť technickými gates a mať abort mechanizmus. Po rozhodnutí sa experiment config, assignment a temporary instrumentation odstránia alebo prevedú na dlhodobý product control.

''',
    "docs/05-ci-cd-and-release/shadow-deployment.md": r'''## Ako shadow deployment kopíruje traffic bez business side effects

Shadow deployment posiela kópiu reálneho requestu kandidátovi, zatiaľ čo primary response a autoritatívny business outcome zostávajú na stable systéme. Cieľom je pozorovať parsing, performance alebo decision output nad realistickým trafficom bez priamej expozície používateľov.

Kópia requestu musí mať jasný privacy a data-minimization contract. Secrets, osobné údaje alebo regulated payloads sa môžu pred shadowingom redigovať alebo tokenizovať. Shadow environment potrebuje capacity a izoláciu, aby nezvýšil latency primary cesty ani nevyčerpal shared dependency.

Najdôležitejšia hranica sú side effects. Kandidát nesmie vykonať payment, odoslať email, commitnúť autoritatívny row alebo publikovať production event. Používa sandbox adapters, dry-run režim alebo write suppression s explicitným auditom. Ak iba ignorujeme jeho odpoveď, side effect sa môže aj tak vykonať.

Porovnanie stable a shadow outputu potrebuje correlation ID, normalizáciu nedeterministických fields a pravidlá pre acceptable difference. Shadow result nie je používateľský outcome a nemôže sám potvrdiť authorization alebo final business correctness, ak používa iné dependencies či potlačené writes.

Po teste sa cleanup-ne duplicated data, temporary routes a telemetry. Shadowing je diagnostický a compatibility nástroj, nie automatický promotion oracle. Candidate stále potrebuje controlled exposure a reálny business acceptance pred production authority.

''',
    "docs/05-ci-cd-and-release/ring-deployment.md": r'''## Ako stabilné rings riadia expozíciu release-u

Ring deployment rozdeľuje population alebo infraštruktúru do vopred definovaných skupín a release postupuje od menšieho, lepšie pozorovateľného ringu k širšiemu. Ring môže predstavovať interných users, vybrané tenants, jeden región alebo určitú fleet. Jeho membership musí byť stabilný a versionovaný, inak sa počas observation window mení samotný subject experimentu.

Poradie rings vyjadruje risk model. Prvý ring má nízky blast radius a kvalitnú telemetry, ale nemusí reprezentovať production workload. Ďalšie rings pridávajú scale, dependency alebo tenant diversity. Promotion criteria preto nie sú identické pre každý krok; neskorší ring môže vyžadovať vyšší sample a odlišné business oracles.

Assignment sa robí podľa identity relevantnej pre celý workflow. Ak account počas release-u preskočí medzi rings, jeho multi-step operácia môže používať zmiešané generations. Membership changes sa preto plánujú mimo observation window alebo sa viažu na novú assignment generation.

Každý ring step má exact artifact, configuration, exposed population, start time, evidence a abort path. No-data v malom ringu môže znamenať nedostatočnú reprezentatívnosť, nie success. Pred promotion sa overí aj forbidden outcome a backlog.

Po full rollout-e sa temporary ring rules a overrides odstránia alebo sa stanú explicitnou dlhodobou policy. Ring deployment nie je iba zoznam prostredí; je to state machine expozície s kontrolovaným prechodom a recovery na každom kroku.

''',
    "docs/05-ci-cd-and-release/feature-flags.md": r'''## Ako feature flag vytvára samostatný runtime control plane

Feature flag oddeľuje deployment kódu od aktivácie správania. Aplikácia načíta flag configuration a podľa evaluation contextu vyberie old alebo new path. Tento control plane má vlastnú generation, distribúciu, cache a failure semantics; nie je automaticky synchronizovaný s image rolloutom.

Evaluation context môže obsahovať user, account, tenant, region alebo operation attributes. Pravidlá musia byť deterministické a stabilné pre celý workflow. Ak sa flag vyhodnocuje náhodne pri každom requeste, multi-step journey môže prepínať behavior. Loaded flag generation sa preto zaznamenáva v telemetry a business operation state-e.

Fail-open a fail-closed voľba závisí od rizika. Pri security alebo payment control-e môže outage flag služby nesmie povoliť neoverený path. Lokálna cache a default musia byť explicitné a testované. Control-plane success nepreukazuje, že všetky processes načítali rovnakú hodnotu; runtime read-back alebo cohort metrics overia effective state.

Flag disable môže byť rýchly containment, ale nevráti data, events ani external side effects. Recovery musí posúdiť, čo už new path vykonal. Dlhodobo otvorené flags zvyšujú kombinatorický test space a cognitive load, preto každý flag potrebuje ownera, purpose, created/expiry date a cleanup plan.

Feature flag nie je náhradou versioning alebo deployment safety. Kód oboch paths musí byť kompatibilný s aktuálnym shared state-om a release manifest má uviesť podporovanú flag generation.

''',
    "docs/05-ci-cd-and-release/progressive-delivery.md": r'''## Ako progressive delivery spája rollout a evidence

Progressive delivery automatizuje postupnú expozíciu release-u a rozhoduje o ďalšom kroku podľa evidence. Nejde o synonymum canary toolu. Release môže meniť application generation, traffic weights, feature flags a database schema, pričom každý control plane má vlastný observed state a recovery eligibility.

Rollout contract definuje kroky expozície, cohort identity, minimálny sample, metrics, business oracle, no-data behavior a abort criteria. Controller mutation je iba začiatok kroku. Read-back musí potvrdiť actual replicas alebo route, loaded configuration a to, že relevantné operations naozaj patria do analyzovanej cohorty.

Analysis kombinuje technical a business evidence. Error rate a p95 môžu byť green, kým async completion alebo data correctness zlyháva. Delayed outcomes preto vyžadujú dostatočné observation window a authoritative denominator. Telemetry outage vedie k zastaveniu alebo inconclusive stavu, nie automatickej promotion.

Pri failure sa freeze-ne ďalšia expozícia a zachová sa evidence. Recovery môže znamenať route reversal, flag disable, roll-forward alebo compensation. Controller nemá naslepo vrátiť image, ak schema alebo events už zmenili shared state. In-flight operations sa inventarizujú a reconciliujú podľa operation identity.

Progressive delivery je uzavretá až po full exposure, stabilnom observation windowe, odstránení temporary controls a overení druhej business operácie. Automatizácia zrýchľuje bezpečné rozhodovanie iba vtedy, keď modeluje všetky relevantné generations a outcomes.

''',
    "docs/05-ci-cd-and-release/rollback-and-roll-forward.md": r'''## Ako vybrať rollback, roll-forward, compensation alebo restore

Recovery rozhodnutie sa robí po vrstvách. Application bytes možno vrátiť na starý digest, configuration na starú generation a traffic na stable route. Databázové rows, eventy a external provider side effects však nemusia byť reverzibilné rovnakým príkazom. „Rollback release“ preto nie je jedna univerzálna operácia.

Rollback je vhodný, keď stará generation zostala kompatibilná s aktuálnym shared state-om a návrat neporuší in-flight work. Roll-forward používa nový artifact alebo config, ktorý defect opraví bez návratu na nekompatibilný contract. Feature disable obmedzí behavior, compensation vytvorí domain operation rušiacu predchádzajúci side effect a restore obnoví data z recovery pointu s explicitnou stratou a reconciliáciou.

Timeout alebo stratená odpoveď vytvára unknown outcome. Blind retry môže vykonať druhú mutation. Najprv sa číta controller, route, database journal alebo provider operation status podľa stabilnej identity. Až observation určí, či treba pokračovať, kompenzovať alebo iba uzavrieť evidence.

Recovery eligibility sa má vyhodnotiť pred release-om. Manifest uvádza schema/event compatibility, last-known-good artifacts, restore assumptions a operations, ktoré nemožno automaticky vrátiť. Runbook potom nie je improvizovaný počas incidentu.

Verdikt sa uzatvára technickým, functional a business read-backom. Overí sa pôvodný failure, forbidden duplicate/loss outcome, backlog a druhá operácia. Návrat deployment statusu na green bez business reconciliation nie je dokončená recovery.

''',
    "docs/05-ci-cd-and-release/database-compatibility-during-deployment.md": r'''## Ako expand/contract chráni mixed-version databázu

Počas rolling alebo progressive deploymentu stará a nová application generation používajú spoločnú databázu. Schema a data protocol preto musia byť kompatibilné počas celého mixed-version intervalu. Expand/contract rozdelí zmenu na viac release-ov namiesto okamžitého premenovania alebo odstránenia contractu.

V **expand** fáze sa pridá nový nullable column, table, index alebo event field bez zrušenia starej cesty. Nová application začne podľa potreby dual-write alebo čítať s fallbackom. **Migrate** fáza backfilluje existujúce dáta a porovnáva old/new representations. Po potvrdení completeness sa **switch** presunie na nový read path. Až **contract** fáza odstráni starý field alebo constraint, keď žiadny podporovaný consumer starú formu nepoužíva.

DDL success nepreukazuje, že operation bola online alebo že replicas a backfill sú complete. Engine, dataset size, lock a replication behavior patria do planu. Migration journal iba hovorí, čo tool zaznamenal; catalog a data queries musia potvrdiť effective state.

Backfill je production workload. Potrebuje batches, checkpoint, rate limit a idempotenciu. Stale batch nesmie prepísať novší live write, preto používa row version alebo conditional update. Dual-write môže mať partial outcome, ak jeden zápis uspeje a druhý zlyhá; authority a reconciliation musia byť explicitné.

Contract removal je samostatné rozhodnutie po telemetry dôkaze, že starí readers/writers a backlog zmizli. Rollback eligibility sa mení v každej fáze. Návrat application image-u po destructive cleanup-e nemusí byť možný, preto recovery môže vyžadovať roll-forward alebo data restore a business reconciliation.

''',
}
