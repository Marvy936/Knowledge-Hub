# Monorepo vs. multirepo

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Branching strategies](branching-strategies.md), [Value Stream Mapping](../00-foundations/value-stream-mapping.md)
- Súvisiace témy: repository boundaries, ownership, CI graph, dependency management, platform engineering

## 1. Cieľ kapitoly

Voľba medzi monorepom a multirepom nie je súťaž dvoch Git štýlov. Je to rozhodnutie, **kde systém vytvorí hranicu zmeny**.

Repository boundary ovplyvňuje:

```text
čo možno zmeniť jedným commitom
→ čo možno reviewnuť v jednom kontexte
→ ktoré checks sa spustia
→ kto môže čítať a schvaľovať source
→ ako sa zmena prenesie do artifacts a deploymentov
```

Nevhodná hranica coupling neodstráni. Iba ho presunie:

```text
spoločný source commit
alebo
cross-repo versions, contracts, rollout a koordinácia
```

Cieľom preto nie je minimalizovať počet repositories ani vložiť všetko do jedného repo. Cieľom je umiestniť hranicu tam, kde minimalizuje celkový coordination cost bez porušenia bezpečnostnej, vlastníckej alebo release izolácie.

## 2. Nosný scenár: Atlas Commerce

Atlas prevádzkuje objednávkový flow:

```text
web checkout
  ↓
orders API
  ↓
pricing library
  ↓
payments adapter
  ↓
deployment configuration
```

Pôvodný stav je multirepo:

```text
atlas-web
atlas-orders
atlas-pricing
atlas-payments
atlas-deploy
```

Tím potrebuje zaviesť nový atribút `price_source`, ktorý musí:

1. vzniknúť v pricing modeli;
2. prejsť cez Orders API;
3. zobraziť sa vo web checkoute;
4. byť zaznamenaný v payment audite;
5. dostať sa do deployment configu a observability.

Na prvý pohľad ide o päť malých zmien. V skutočnosti ide o jeden business intent rozdelený cez päť repository boundaries.

Tento scenár budeme používať na rozhodnutie, či majú komponenty zostať oddelené, zlúčiť sa do monorepa alebo vytvoriť menší domain monorepo.

## 3. Centrálny rozhodovací model

Repository topology vyberaj cez tento lifecycle:

```text
pozoruj reálne business changes
  ↓
zmeraj change a release coupling
  ↓
oddeľ repository, build, deployment a security boundaries
  ↓
navrhni source-change lifecycle pre obe alternatívy
  ↓
navrhni artifact, CI a rollout mechanizmus
  ↓
porovnaj coordination cost a failure modes
  ↓
zvoľ boundary a zaznamenaj predpoklady
  ↓
meraj výsledok a boundary pravidelne prehodnocuj
```

Dôležité je porovnávať **celý lifecycle zmeny**, nie iba pohodlie pri clone alebo počet pull requestov.

## 4. Štyri hranice, ktoré nie sú totožné

### Repository boundary

Určuje spoločný commit graph, refs, branch policy, review context a základnú permission hranicu.

### Build boundary

Určuje, čo sa kompiluje, testuje alebo balí ako jeden target.

### Deployment boundary

Určuje, čo možno nasadiť a rollbacknúť nezávisle.

### Security a ownership boundary

Určuje, kto môže source čítať, meniť, schvaľovať a prevádzkovať.

Tieto hranice sa môžu prekrývať, ale nemusia.

Atlas môže mať Orders, Pricing a Payments v jednom monorepe, pričom každý komponent:

- vytvára vlastný artifact;
- má vlastný deployment;
- má samostatný owner tím;
- používa samostatné production credentials.

Monorepo teda neznamená jeden service, build ani release. Multirepo zase negarantuje runtime nezávislosť.

## 5. Prvý signál: change coupling

Change coupling vyjadruje, ako často komponenty musia byť zmenené pre jeden business intent.

Pri Atlas scenári sa ukáže:

```text
price_source change
→ pricing model
→ Orders contract
→ web rendering
→ payment audit
→ deployment telemetry
```

Ak podobný pattern vzniká pri väčšine produktových zmien, repository boundaries pravidelne pretínajú prirodzenú change unit.

Silný coupling sa prejavuje merateľne:

- jeden ticket vytvára sériu závislých pull requestov;
- consumer čaká na vydanie provider artifactu;
- rovnaký refactoring sa opakuje v niekoľkých repos;
- integrácia zlyháva až po spojení samostatne zelených pipelines;
- rollback jedného componentu vyžaduje koordinovaný rollback ďalších.

Naopak, samotné spoločné vlastníctvo alebo rovnaký programovací jazyk nie sú dostatočným dôvodom na monorepo. Komponenty môžu patriť jednému tímu a pritom mať stabilné contracts a nezávislé release lifecycles.

## 6. Ako vyzerá Atlas zmena v multirepe

V multirepe nemožno vytvoriť jeden Git commit cez všetky komponenty. Bezpečný change flow musí nahradiť source atomicitu kompatibilitou:

```text
1. Pricing pridá backward-compatible field.
2. Pricing publikuje immutable artifact.
3. Orders adoptuje novú version, ale starý field stále podporuje.
4. Web a Payments postupne adoptujú nový contract.
5. Deployment manifest zaznamená kompatibilnú kombináciu.
6. Telemetry potvrdí, že starý contract už nikto nepoužíva.
7. Až potom sa stará cesta odstráni.
```

Mechanizmus je expand-and-contract.

Výhodou je nezávislosť repository a release lifecycle-u. Nákladom je explicitná orchestration vrstva:

```text
source repo
→ immutable artifact
→ registry
→ consumer version update
→ contract/integration validation
→ environment release manifest
```

Ak táto vrstva neexistuje, multirepo iba skrýva coupling za mutable dependencies a manuálne poradie nasadení.

## 7. Ako vyzerá rovnaká zmena v monorepe

V monorepe môže jeden pull request obsahovať:

```text
pricing model
+ Orders contract
+ web consumer
+ payment audit
+ tests
+ deployment metadata
```

Jeden commit môže reprezentovať konzistentný source snapshot. Review vidí celý intent a CI môže testovať presnú kombináciu source.

To však nerobí deployment atomickým.

Ak sa artifacts nasadzujú samostatne, produkcia môže počas rollout-u obsahovať:

```text
nový Orders + starý Web
starý Orders + nový Pricing
nový Payments + starý deployment config
```

Aj monorepo preto potrebuje:

- backward-compatible contracts;
- explicitné artifacts;
- rollout ordering;
- readiness a observability;
- rollback kompatibilitu.

Monorepo znižuje source coordination cost. Neodstraňuje distributed-system lifecycle.

## 8. Source atomicita verzus runtime kompatibilita

Toto je kľúčový rozdiel:

```text
source atomicita
= jeden commit obsahuje konzistentný source snapshot

deployment atomicita
= všetky runtime časti prejdú do nového stavu naraz
```

Prvá vlastnosť je prirodzená v monorepe. Druhá je pri nezávislých službách zriedkavá bez samostatného deployment transaction mechanizmu.

Pre Atlas musí byť `price_source` rollout bezpečný aj pri zmiešaných verziách. Inak monorepo iba presunie chybu z merge fázy do produkčného rollout-u.

Repository topology teda nesmie nahrádzať contract design.

## 9. Dependency graph je jadrom škálovateľného monorepa

Keď Atlas zlúči komponenty do monorepa, naivná pipeline môže robiť:

```text
každý commit
→ build a test všetkého
```

To je spočiatku jednoduché, ale s rastom predlžuje feedback.

Škálovateľný model potrebuje autoritatívny graph:

```text
zmenené inputs
  ↓
affected targets
  ↓
potrebné builds a tests
  ↓
cache a parallel execution
  ↓
povinné globálne checks
```

Pri zmene pricing schema musí graph vedieť, že sú ovplyvnené Orders, Web aj Payments.

Ak chýba dependency edge:

```text
pricing schema sa zmení
→ Web nie je označený ako affected
→ Web tests sa nespustia
→ pull request je zelený
→ nekompatibilita sa objaví po deploymente
```

To je false green spôsobený chybným modelom systému, nie náhodným CI problémom.

Affected detection preto musí používať:

- explicitné target dependencies;
- conservative fallback pri neznámych inputs;
- periodické full builds;
- porovnanie selective a full výsledkov;
- vlastníctvo spoločných build rules.

Bez tejto investície sa veľké monorepo mení na centralizovaný bottleneck.

## 10. Artifact graph je jadrom bezpečného multirepa

V multirepe je source graph rozdelený. Prepojenie musí niesť artifact identity:

```text
atlas-pricing commit
→ pricing package 4.7.0 / digest
→ atlas-orders dependency update
→ Orders artifact
→ environment release manifest
```

Nebezpečný model:

```text
consumer build
→ stiahni latest z main iného repo
```

Výsledok nie je reprodukovateľný. Rovnaký consumer commit môže v rôznom čase vytvoriť iný artifact.

Bezpečný multirepo contract používa:

- immutable versions alebo digests;
- lockfiles a dependency pinning;
- provenance k source commitu;
- contract tests;
- automated dependency update pull requests;
- deprecation policy;
- environment manifest reálne nasadených versions.

Multirepo nie je voľnejšie samo osebe. Nezávislosť vzniká až vtedy, keď contracts a artifacts umožňujú komponenty meniť bez distribuovanej manuálnej transakcie.

## 11. Ownership nie je automaticky security boundary

Monorepo môže používať path ownership:

```text
/services/orders/      @orders-team
/libraries/pricing/    @pricing-team
/services/payments/    @payments-team
/build/                @developer-platform
```

To pomáha s review a zodpovednosťou. Typický `CODEOWNERS` však nebráni používateľovi s prístupom do private repository čítať ostatné paths.

Ak payment adapter obsahuje source dostupný iba need-to-know skupine, samostatné repo môže byť nevyhnutné.

Silné dôvody na oddelenie:

```text
odlišná read-access hranica
externý partner alebo právna entita
customer-specific source
export-control alebo compliance
samostatná retention policy
```

Naopak, oddeliť každý component „pre bezpečnosť“ bez konkrétneho threat modelu môže vytvoriť:

- viac long-lived tokens;
- duplicate CI konfigurácie;
- neprehľadné dependency permissions;
- širšiu supply-chain attack surface.

Security boundary musí riešiť konkrétny prístupový invariant, nie iba vytvoriť viac repositories.

## 12. Release topology musí byť explicitná v oboch modeloch

Atlas má päť source komponentov, ale production release potrebuje presne vedieť, čo je nasadené.

Monorepo môže vytvoriť:

```yaml
source_commit: abc123
artifacts:
  orders: sha256:...
  web: sha256:...
  payments: sha256:...
```

Multirepo môže vytvoriť:

```yaml
release: "2026.07.26.1"
components:
  orders:
    source_commit: abc123
    artifact: sha256:...
  web:
    source_commit: def456
    artifact: sha256:...
  payments:
    source_commit: 789abc
    artifact: sha256:...
```

V oboch prípadoch musí deployment record obsahovať artifact identity, nie iba branch alebo mutable tag.

Repository topology a release topology sú oddelené. Bez release manifestu nemožno spoľahlivo reprodukovať environment ani vysvetliť incident.

## 13. Rozhodnutie pre Atlas

Pozorovanie ukázalo:

- Orders, Pricing a Web sa menia spolu vo väčšine business changes;
- ich source je dostupný rovnakým interným tímom;
- používajú spoločný toolchain a contract tests;
- samostatné package releases neprinášajú významnú nezávislosť;
- Payments má prísnejší read-access a compliance lifecycle;
- deploymenty zostávajú nezávislé.

Výsledná boundary:

```text
atlas-commerce monorepo
├── web
├── orders
├── pricing
├── shared schemas
└── deployment metadata

atlas-payments repo
└── restricted adapter a audit logic
```

Toto nie je kompromis pre kompromis. Je to domain monorepo:

- zoskupuje vysoko coupled komponenty;
- zachováva samostatnú security boundary Payments;
- znižuje cross-repo change transakcie;
- nepredstiera jeden spoločný deployment.

Hybridný model je často presnejší než globálne „monorepo alebo multirepo“.

## 14. Worked failure: monorepo pipeline je zelená, produkcia nie

Po migrácii Atlas zmení shared schema generator. Orders sa otestuje, Web nie.

Symptóm:

```text
pull request green
deployment úspešný
checkout UI nevie spracovať nový field
```

Diagnostika:

1. Identifikuj source commit a artifacts.
2. Over, ktoré targets pipeline označila ako affected.
3. Porovnaj deklarovaný dependency graph so skutočným importom alebo generated outputom.
4. Spusť full validation na rovnakom commite.
5. Potvrď, že Web test zlyhá iba vo full run-e.
6. Nájde sa chýbajúca hrana:

```text
schema-generator
→ generated web client
→ web tests
```

Root cause nie je „monorepo je príliš veľké“. Root cause je neúplný dependency graph, ktorý zmenil required validation contract bez dôkazu correctness.

Náprava:

- doplniť graph edge;
- pridať graph conformance test;
- pri generator changes použiť conservative fallback;
- dočasne spúšťať shadow full build;
- sledovať false-green incidents.

Rozdelenie repository by tento implicitný dependency problém nevyriešilo. Iba by ho presunulo do package publishingu.

## 15. Worked failure: multirepo release drift

Pred migráciou Orders očakáva Pricing 4.7, ale production používa 4.5. Web už predpokladá nový field.

Symptóm:

```text
všetky jednotlivé pipelines boli zelené
environment má nekompatibilnú kombináciu artifacts
```

Diagnostika:

1. Zostav manifest reálne nasadených versions a digestov.
2. Porovnaj ho s deklarovanými dependency constraints.
3. Over, ktorý consumer adoptoval nový contract.
4. Skontroluj, či Pricing artifact bol immutable a či Orders update prešiel.
5. Over rollout ordering a rollback compatibility.
6. Zisti, že deployment pipeline používala mutable `latest`.

Mechanizmus:

```text
samostatne správne repos
+ mutable artifact identity
+ chýbajúci release manifest
→ nereprodukovateľná systémová kombinácia
```

Náprava:

- zakázať mutable release references;
- pinovať digesty;
- zaviesť compatibility matrix a contract tests;
- automatizovať dependency adoption;
- vytvoriť environment release manifest;
- sledovať producer-to-consumer adoption lead time.

Ani tu nie je root cause samotné multirepo. Je ním chýbajúci artifact a release contract.

## 16. Kedy je monorepo silný kandidát

Monorepo je silný kandidát, keď jeden business change pravidelne prekračuje existujúce repository boundaries a súčasne platí:

- read access môže byť spoločný;
- build graph možno explicitne modelovať;
- platform tím vlastní CI a cache mechanizmus;
- source-level refactoring má vysokú hodnotu;
- samostatné repository releases neprinášajú reálnu autonómiu.

Rozhodujúci signál nie je „máme veľa microservices“. Je ním vysoký coordination cost vytvorený hranicou.

## 17. Kedy je multirepo silný kandidát

Multirepo je silný kandidát, keď komponenty majú:

- stabilný versioned contract;
- nízky change coupling;
- skutočne nezávislý release lifecycle;
- odlišnú confidentiality alebo compliance hranicu;
- externých contributors alebo partnerov;
- samostatný product lifecycle.

Rozdelenie má hodnotu iba vtedy, keď nezávislosť existuje aj v artifacts, contracts a deploymente. Inak vznikne distribuovaný monolit s viacerými Git repos.

## 18. Migration decision nie je prvá náprava

Pomalé monorepo CI nemusí znamenať zlú repository boundary. Môže ísť o:

```text
nepresný dependency graph
nízku cache hit rate
nehermetické targets
runner queue
build outputs uložené v Git
```

Multirepo release drift nemusí automaticky vyžadovať monorepo. Môže chýbať:

```text
immutable artifact
dependency automation
contract testing
release manifest
```

Najprv diagnostikuj mechanizmus. Migrácia topology je drahá zmena s vlastným blast radiusom a nemá nahrádzať opravu build alebo release systému.

## 19. Prehodnocovanie boundary

Po rozhodnutí sleduj, či pôvodné predpoklady stále platia:

- koľko pull requestov potrebuje jeden business change;
- koľko času trvá adoption novej dependency;
- ako často vznikajú emergency coordination releases;
- aký je CI feedback time a false-green rate;
- koľko duplicated tooling alebo policy configov existuje;
- ako dlho trvá cross-component refactoring;
- či approval alebo ownership boundary vytvára queue;
- či sa zmenili security a partner access požiadavky.

Metrika sama neprikazuje migráciu. Ukazuje, kde hranica vytvára náklad a či je náklad vyšší než izolácia, ktorú boundary poskytuje.

## 20. Architecture decision record

Rozhodnutie má explicitne zaznamenať:

```text
Kontext:
Ktoré business changes a incidents ukázali problém?

Observed coupling:
Ktoré komponenty sa menia, releaseujú a rollbackujú spolu?

Požadované boundaries:
Ktorý read access, ownership, compliance a release isolation je nevyhnutný?

Zvolený model:
Monorepo, multirepo alebo domain hybrid?

Mechanizmy correctness:
Ako funguje dependency graph, artifact identity, contract testing a release manifest?

Failure modes:
Ako vznikne false green, release drift alebo príliš široký blast radius?

Re-evaluation triggers:
Ktoré metriky alebo organizačné zmeny rozhodnutie znovu otvoria?
```

Bez týchto predpokladov sa topology časom zmení na dogmu.

## 21. Praktický rozhodovací postup

Pre kandidátnu hranicu urob jeden konkrétny change walkthrough:

1. Vyber poslednú reálnu cross-component zmenu.
2. Nakresli source, artifact a deployment kroky.
3. Označ čakacie body, manuálne koordinácie a kompatibilitné fázy.
4. Zisti, ktoré kroky by monorepo odstránilo a ktoré by zostali.
5. Zisti, ktoré security alebo release boundaries by monorepo oslabilo.
6. Navrhni CI graph pre monorepo alternatívu.
7. Navrhni artifact a contract flow pre multirepo alternatívu.
8. Simuluj rollback a incident diagnosis.
9. Porovnaj celkový lifecycle, nie iba počet pull requestov.
10. Zaznamenaj rozhodnutie a re-evaluation trigger.

## 22. Časté omyly

### „Monorepo znamená jeden release“

Nie. Jeden source snapshot môže vytvoriť viac nezávislých artifacts a deploymentov.

### „Multirepo znamená loose coupling“

Nie. Coupling môže zostať a prejaviť sa ako koordinované package updates, rollout poradie a incident drift.

### „Atomický commit znamená atomický deployment“

Nie. Runtime stále môže obsahovať zmiešané versions.

### „CODEOWNERS je security boundary“

Nie. Riadi review, nie typicky čítanie paths.

### „Rozdelenie repo automaticky zrýchli CI“

Môže zmenšiť lokálne pipelines, ale pridať duplicate setup, publishing a cross-repo integration latency.

### „Monorepo odstráni potrebu versionovať interné dependencies“

Source dependency stále potrebuje contract, ownera a build graph. Runtime artifact stále potrebuje identity a provenance.

### „Jedna služba má mať jedno repo“

Je to konvencia, nie invariant. Boundary má nasledovať change, security a lifecycle mechanizmy.

## 23. Zhrnutie

Repository topology je umiestnenie hranice zmeny.

Monorepo prirodzene poskytuje:

```text
spoločný source snapshot
+ jeden review context
+ source-level dependency graph
```

Multirepo prirodzene poskytuje:

```text
samostatný commit/ref policy
+ repository-level access boundary
+ nezávislý source a release lifecycle
```

Ani jeden model automaticky neposkytuje runtime nezávislosť, správnu architektúru alebo bezpečný rollout.

Rozhodujúca otázka je:

```text
Kde dnes platíme coordination cost
a aký mechanizmus ho po presunutí boundary nahradí?
```

Dobrá voľba zoskupí vysoko coupled zmeny, zachová nevyhnutnú izoláciu a spraví dependency, artifact a release graph explicitným.

## 24. Kontrolné otázky

1. Aký je rozdiel medzi repository, build, deployment a security boundary?
2. Prečo vysoký change coupling podporuje spoločnú repository boundary?
3. Čo poskytuje source-atomický commit a čo negarantuje?
4. Ako multirepo nahrádza source atomicitu?
5. Prečo monorepo potrebuje autoritatívny dependency graph?
6. Ako vznikne false green pri affected detection?
7. Prečo multirepo potrebuje immutable artifacts a release manifest?
8. Kedy je samostatné repo nevyhnutnou security boundary?
9. Prečo môže byť domain monorepo lepšie než globálny monorepo alebo repo-per-service?
10. Ako rozlíšiš topology problém od zlého build alebo release mechanizmu?
11. Aké metriky ukážu, že repository boundary treba prehodnotiť?
12. Ako by si pre Atlas navrhol rollback pri zmiešaných versions?

## Glossary impact

Relevantné pojmy: monorepo, multirepo, repository boundary, build boundary, deployment boundary, security boundary, source atomicity, deployment atomicity, change coupling, affected-target detection, dependency graph, artifact graph, contract testing, release manifest, domain monorepo, expand-and-contract.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Branching strategies](branching-strategies.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Bash automation →](bash-automation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
