# Desired State and Reconciliation

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Declarative vs. Imperative Approach](declarative-vs-imperative.md), [Idempotency](idempotency.md)
- Súvisiace témy: Kubernetes controllers, Terraform state, GitOps, drift, control loops

## 1. Definícia

**Desired state** vyjadruje stav, ktorý má podľa autoritatívneho zámeru platiť. **Observed state** je stav, ktorý controller alebo nástroj dokázal zistiť z cieľového systému, a **reconciliation** je opakovaný proces, ktorý rozdiel vyhodnotí a vykoná bezpečnú korekciu.

Tento model nepredpokladá, že jeden deployment udrží systém správny navždy. Počíta s tým, že procesy padajú, ľudia menia konfiguráciu, externé API zlyhávajú a runtime sa neustále odchyľuje od pôvodného zámeru.

## 2. Štyri pohľady na stav

Pri diagnostike nestačí hovoriť iba o desired a actual state. Produkčný systém často pracuje minimálne so štyrmi pohľadmi, ktoré sa môžu navzájom líšiť.

- **Desired state —** deklarovaný zámer, napríklad `replicas: 3`; určuje, čo sa má controller snažiť dosiahnuť.
- **Recorded state —** stav uložený v databáze nástroja, napríklad Terraform state; pomáha mapovať deklarované objekty na externé resources, ale nemusí presne zodpovedať realite.
- **Observed state —** informácia načítaná z cieľového API alebo runtime-u; môže byť neúplná, oneskorená alebo stale.
- **Effective state —** výsledné správanie z pohľadu používateľa, napríklad či tri ready replicas skutočne obsluhujú traffic; technicky existujúci resource ešte nemusí poskytovať očakávanú službu.

Reconciliation typicky pracuje s desired a observed state-om, no validácia musí sledovať aj effective outcome. Controller môže hlásiť úspech, zatiaľ čo downstream DNS, routing alebo application readiness zostáva nefunkčná.

## 3. Základný control loop

Reconciliation loop opakovane načíta intent, pozoruje realitu, vypočíta rozdiel, vykoná malý idempotentný krok a výsledok znovu overí. Jedna iterácia nemusí dosiahnuť celý cieľ; dôležité je, aby systém konvergoval a každá korekcia mala bounded scope.

```text
read desired state
→ observe current state
→ normalize a compare
→ choose bounded action
→ execute idempotently
→ record status a evidence
→ requeue alebo skonči do ďalšej udalosti
```

Loop potrebuje známy trigger. Môže reagovať na event, periodický resync, zmenu dependency, retry po chybe alebo explicitný reconcile request.

## 4. Prečo level-based model prežije stratené udalosti

Edge-based spracovanie reaguje na tvrdenie „udalosť sa stala“, napríklad `PodDeleted`. Ak sa event stratí alebo controller počas udalosti nebeží, samotný event log nemusí stačiť na opravu.

Level-based controller sa pýta „aký stav platí teraz?“. Ak desired count zostáva tri a observed count je dva, potrebnú akciu odvodí aj po reštarte, resynce alebo strate pôvodného eventu.

```text
edge:  zachyť PodDeleted → vytvor náhradu
level: desired=3, observed=2 → vytvor jednu repliku
```

Events sú užitočné na rýchle spustenie loopu, ale correctness má vychádzať zo state comparison. Tým sa controller stáva odolnejší voči restartom a at-least-once event delivery.

## 5. Kubernetes príklad

Deployment deklaruje počet replicas a rollout stratégiu. Deployment controller vytvorí alebo upraví ReplicaSet, ReplicaSet controller udržiava počet Podov, scheduler prideľuje Pody na nodes a kubelet realizuje lokálny container state.

```text
Deployment intent
→ Deployment controller
→ ReplicaSet intent
→ ReplicaSet controller
→ Pod objects
→ scheduler
→ kubelet a container runtime
→ ready endpoints
```

Žiadny z týchto componentov nevlastní celý outcome. Celkový stav vzniká skladaním viacerých loops, preto je dôležité sledovať, v ktorej vrstve sa intent prestal realizovať.

## 6. Controller ownership

Každý controller musí vlastniť presne definované polia alebo externé resources. Ak dva controllery považujú tú istú hodnotu za svoj desired state, môžu ju striedavo prepisovať a vytvoriť flapping.

Ownership môže byť vyjadrený schema pravidlom, field managementom, tagom, annotation, owner reference alebo internou resource mapou. Samotná dohoda v dokumentácii nestačí, ak platforma umožňuje paralelný zápis bez detekcie konfliktu.

## 7. Source of truth

Source of truth je miesto, z ktorého sa odvodzuje autoritatívny intent. Môže ním byť Git repository, Kubernetes API objekt, Terraform konfigurácia, databázový record alebo externý control plane.

- **Git —** poskytuje versioned a reviewovaný intent; controller však musí určiť, či manuálnu runtime zmenu revertne alebo iba reportuje.
- **Kubernetes API —** objekt `spec` je runtime intent pre controller; Git môže byť vyšší source of truth, ktorý tento objekt znova vytvára.
- **Terraform configuration a state —** konfigurácia opisuje intent a state mapuje resource identity; ani jeden pohľad sám osebe nemusí byť aktuálny observed state.
- **Aplikačná databáza —** môže držať business intent, napríklad subscription status; infra controller nesmie tento state svojvoľne odvodiť z neautoritatívnej cache.

Ak existuje viac sources of truth, musí byť definovaná hierarchia a synchronizačný smer. Obojsmerná synchronizácia bez conflict resolution vytvára slučku, v ktorej každý systém opravuje zmenu toho druhého.

## 8. Normalizácia a semantic diff

Raw text diff nemusí zodpovedať významovej zmene. API môže doplniť default hodnotu, zoradiť collection, zaokrúhliť číslo alebo vrátiť ekvivalentnú reprezentáciu iným formátom.

Controller preto potrebuje normalizovať hodnoty a porovnávať iba polia, ktoré vlastní. Ak porovnáva serialization namiesto semantics, môže pri každej iterácii zapisovať rovnakú hodnotu a vytvárať nekonečný update loop.

## 9. Drift

Drift je rozdiel medzi autoritatívnym intentom a relevantným observed state-om. Môže byť nežiaduci, očakávaný alebo dočasný; samotná existencia diffu ešte neurčuje správnu reakciu.

- **Manuálna zmena —** operátor upraví resource mimo source of truth; policy môže zmenu revertovať, importovať alebo iba eskalovať.
- **Runtime controller zmena —** autoscaler upraví replicas; GitOps controller nesmie túto hodnotu prepisovať, ak ownership patrí autoscaleru.
- **Provider default —** API doplní hodnotu, ktorú konfigurácia neuviedla; diff treba normalizovať alebo explicitne prijať.
- **Partial failure —** časť resource-u vznikne a časť nie; reconcile má pokračovať z observed state-u, nie zopakovať celý workflow naslepo.
- **Resource degradation —** deklarácia sa nezmenila, ale disk, node alebo dependency zlyhala; self-healing loop musí vytvoriť náhradu alebo označiť stav ako neobnoviteľný.

Drift policy má byť explicitná podľa field alebo resource class. Automatické revertovanie každej odchýlky môže zmazať incident mitigation alebo legitímny state iného controllera.

## 10. Convergence

Controller konverguje, keď opakované iterácie približujú systém k realizovateľnému desired state-u a po jeho dosiahnutí prestanú vytvárať zbytočné mutácie. Konvergencia vyžaduje idempotentné actions, stabilné vstupy a porovnanie, ktoré rozpozná ekvivalentný stav.

Flapping vzniká napríklad vtedy, keď controller A nastavuje replicas na tri a autoscaler B ich nastavuje na päť. Ďalšou príčinou môže byť náhodne generovaný názov, nestabilné poradie zoznamu alebo API, ktoré požadovanú hodnotu nikdy neprijme.

## 11. Eventual consistency a readiness

Prijatie desired state-u neznamená okamžité dosiahnutie runtime výsledku. Provisioning, scheduling, image pull, health checks, DNS propagation a cache invalidation môžu trvať sekundy až minúty.

Preto sa oddeľuje intent od statusu:

- **`spec` alebo intent —** čo používateľ alebo vyšší controller požaduje.
- **Observed generation —** ktorú verziu intentu controller už spracoval; zabraňuje čítaniu starého statusu ako výsledku novej zmeny.
- **Conditions —** či je resource progressing, ready, degraded alebo blocked a prečo.
- **Events a logs —** časová evidence jednotlivých pokusov, nie autoritatívny aktuálny stav.

Consumer musí vedieť, či potrebuje iba accepted intent alebo skutočne ready effective state. Pipeline, ktorá po API success okamžite pokračuje, môže používať resource skôr, než je pripravený.

## 12. Status ako vysvetlenie, nie druhý intent

Status má opisovať pozorovanie, priebeh a dôvod, nie obsahovať skrytý desired state, ktorý začne súperiť so `spec`. Controller by mal zapisovať stabilné conditions s jasným reason a message, aby používateľ vedel, či má čakať alebo konať.

Dobrý status odpovedá na tri otázky: čo controller pozoroval, ktorú generáciu intentu spracoval a čo bráni ďalšiemu pokroku. Samotné `Ready=false` bez reason, dependency identity alebo poslednej chyby nevytvára použiteľnú diagnostiku.

## 13. Retry, backoff a rate limiting

Reconciliation sa opakuje, no nemá agresívne zaťažovať nefunkčnú dependency. Transient failure typicky používa exponential backoff s jitterom, zatiaľ čo permanentná validation chyba čaká na zmenu intentu namiesto nekonečného retry.

- **Retry —** zopakuje bezpečnú idempotentnú operáciu pri dočasnej chybe.
- **Backoff —** zväčšuje interval medzi pokusmi, aby dependency dostala priestor na zotavenie.
- **Jitter —** rozloží pokusy viacerých controller instances v čase a znižuje retry storm.
- **Rate limiting —** chráni API a shared dependencies pred vysokou reconcile frekvenciou.
- **Terminal condition —** označí nerecoverable stav, napríklad neplatný parameter, ktorý musí opraviť používateľ.

Backoff nesmie skryť kritický stuck resource. Status a metrics majú ukázať počet pokusov, vek posledného úspechu a čas do ďalšieho retry.

## 14. Finalizers a deletion lifecycle

Delete request môže znamenať začiatok cleanupu, nie okamžité odstránenie objektu. Finalizer drží objekt v terminating stave, kým controller neuvoľní externý resource, DNS záznam, cloud volume alebo inú dependency.

```text
delete requested
→ deletion timestamp
→ controller cleanup
→ remove finalizer
→ object deletion
```

Finalizer handler musí byť idempotentný, pretože cleanup sa môže opakovať po timeoute alebo reštarte. Chybný finalizer môže resource zablokovať navždy, preto potrebuje status, retry policy a kontrolovaný break-glass postup.

## 15. External resource identity

Controller, ktorý vytvára cloud resource, potrebuje stabilne mapovať interný objekt na externú identity. Ak po crashi nevie nájsť už vytvorený load balancer, môže pri ďalšom reconcile vytvoriť druhý.

Mapovanie môže používať provider client token, deterministic name, external ID v statuse alebo tag s immutable owner UID. Názov čitateľný človekom nemusí byť dostatočný, ak sa objekt zmaže a neskôr vytvorí nový s rovnakým menom.

## 16. Partial failure a resumable workflow

Reconciliation workflow má pokračovať z observed state-u, nie predpokladať, že predchádzajúca iterácia neurobila nič. Ak sa vytvorila databáza, ale DNS záznam zlyhal, ďalší loop má databázu nájsť, overiť jej ownership a dokončiť iba DNS krok.

Každá fáza potrebuje explicitný invariant a evidence dokončenia. Kompenzácia sa používa iba vtedy, keď desired outcome už nemožno dosiahnuť alebo keď policy vyžaduje odstrániť partial resources.

## 17. GitOps reconciliation

GitOps controller načíta versioned intent z Gitu, renderuje alebo interpretuje ho a porovnáva s cluster state-om. Dôležité je odlíšiť Git commit, rendered manifest, live object a effective runtime outcome.

Policy môže používať tri základné režimy:

- **Detect —** controller iba reportuje drift; operátor rozhodne, či zmenu revertovať alebo importovať.
- **Reconcile —** controller automaticky vracia owned fields na Git intent; incidentné manuálne zmeny môžu rýchlo zmiznúť.
- **Prune —** controller odstraňuje resources, ktoré už v desired set-e neexistujú; chybný scope alebo path môže mať vysoký blast radius.

Promotion má používať immutable revision alebo digest, aby bolo jasné, ktorý intent controller realizoval. Pohyblivý branch alebo tag komplikuje audit a rollback.

## 18. Terraform reconciliation

Terraform vykonáva reconciliation počas explicitného `plan/apply`, nie nevyhnutne kontinuálne. Číta konfiguráciu, state a provider APIs, zostaví dependency graph a navrhne operácie.

State je mapovací a coordination artifact, nie neomylný source reality. Refresh môže odhaliť drift, import môže priradiť existujúci resource ku konfigurácii a state recovery môže byť potrebná po partial apply.

Periodický wrapper alebo GitOps platforma môže Terraform spúšťať opakovane, no musí riadiť locking, credentials, plan freshness a concurrent applies. Kontinuálna frekvencia sama osebe z Terraformu neurobí bezpečný controller.

## 19. Degraded control plane

Ak controller alebo source of truth nie je dostupný, runtime môže ďalej fungovať, ale systém stráca schopnosť opravovať drift, nahrádzať zlyhané resources alebo realizovať nový intent. To je odlišný failure mode než okamžitý data-plane outage.

Návrh musí definovať:

- **Runtime autonomy —** ktoré workloads pokračujú bez control plane-u a ako dlho.
- **Queued intent —** či sa nové zmeny odmietnu, uložia alebo sa môžu aplikovať inou cestou.
- **Status staleness —** ako consumer rozpozná, že posledné observed údaje už nie sú čerstvé.
- **Recovery order —** ktoré controllers, credentials a sources of truth sa obnovujú ako prvé.
- **Manual intervention —** ktoré break-glass zmeny controller po návrate zachová alebo revertne.

Control-plane availability preto patrí do reliability modelu aj vtedy, keď používateľský traffic cez incident naďalej prechádza.

## 20. Security hranice

Controller potrebuje oprávnenia na pozorovanie a korekciu resources, čo z neho robí privilegovaný automation principal. Least privilege musí zodpovedať jeho ownership scope-u; broad account administrator zvyšuje blast radius chyby alebo compromise.

Intent musí byť autorizovaný ešte pred realizáciou. Reconciliation nemá obchádzať admission, policy alebo change-control pravidlá iba preto, že request vykonáva interný controller.

## 21. Observability controlleru

Použiteľný controller publikuje metrics, structured logs a status evidence pre celý loop. Dôležité nie je iba koľko reconciles prebehlo, ale či resources konvergujú a ako dlho ostávajú v degraded alebo progressing stave.

Sleduj najmä reconcile duration, error rate podľa reason, queue depth, retry age, rate-limit events, stale status, počet finalizer-blocked objects a čas od novej generation po readiness. High reconcile count bez user impactu môže byť iba resync; stuck generation je podstatnejší signál.

## 22. End-to-end príklad

Custom controller spravuje managed database podľa Kubernetes objektu. `spec` obsahuje engine version a size, controller vytvorí cloud database so stabilným client tokenom a external ID zapíše do statusu.

Počas ďalších loops controller načíta cloud state, overí version a readiness a následne vytvorí connection Secret. Ak creation API timeoutne, najprv lookupne database podľa tokenu; nevytvorí slepo druhú.

Pri delete requeste finalizer zablokuje odstránenie objektu, kým policy nevykoná snapshot a database delete. Status priebežne ukazuje `Snapshotting`, `Deleting` alebo dôvod, prečo cleanup nemôže pokračovať.

## 23. Troubleshooting

Diagnostika má sledovať intent od source of truth po effective outcome a určiť prvú vrstvu, ktorá sa prestala približovať k cieľu.

```text
source revision
→ accepted desired state
→ controller generation
→ action attempt
→ external resource
→ status/conditions
→ effective service outcome
```

- **Intent je nový, status starý —** over controller queue, observed generation, leader election a permissions.
- **Controller stále zapisuje rovnakú zmenu —** over normalization, default values a field ownership; semantic state môže byť ekvivalentný, hoci raw diff nie.
- **Resource flappuje —** hľadaj druhý writer, autoscaler conflict alebo nestabilný input.
- **Resource ostal terminating —** identifikuj finalizer ownera, cleanup error a dostupnosť external API.
- **External duplicity —** over stable external identity a recovery po timeout-e.
- **Runtime nefunguje pri `Ready=true` —** status kontroluje príliš úzku boundary a nezahŕňa DNS, routing alebo business probe.

## 24. Anti-patterny

### API acceptance sa považuje za dokončenie

API server potvrdil uloženie intentu, nie realizovaný runtime outcome. Pipeline musí čakať na relevantnú condition a overiť effective behavior.

### Dva sources of truth zapisujú rovnaké pole

GitOps, autoscaler a manuálna automation môžu vytvoriť nekonečný konflikt. Ownership a synchronizačný smer musia byť technicky vynútené.

### Retry bez klasifikácie chyby

Permanentná validation chyba sa nekonečne retryuje a zahlcuje queue aj logs. Controller má rozlišovať transient, terminal a conflict failures.

### Status bez generation a reason

Consumer nevie, či status patrí k aktuálnemu intentu ani prečo resource nie je ready. Taký status vytvára falošnú istotu.

### Finalizer bez recovery pathu

Cleanup závisí od zmazaného credentialu alebo neexistujúcej dependency a objekt ostane terminating navždy. Finalizer potrebuje vlastníka, observability a break-glass postup.

## 25. Kontrolné otázky

1. Aký je rozdiel medzi desired, recorded, observed a effective state-om?
2. Prečo level-based controller prežije stratený event?
3. Ako môže raw serialization diff vytvoriť nekonečný update loop?
4. Prečo source of truth potrebuje aj jasný synchronizačný smer?
5. Čo znamená konvergencia a čo typicky spôsobuje flapping?
6. Načo slúži observed generation?
7. Ako sa líši transient failure od terminal validation chyby?
8. Prečo finalizer potrebuje idempotentný cleanup?
9. Ako controller zabráni vytvoreniu druhého externého resource-u po timeoute?
10. Aký failure vzniká pri výpadku control plane-u, keď data plane stále funguje?
11. Ako sa líši GitOps detect, reconcile a prune režim?
12. Prečo Terraform state nie je úplná reprezentácia runtime reality?

## 26. Zhrnutie

Desired state a reconciliation tvoria model nepretržitého riadenia odchýlok. Spoľahlivosť nevzniká iba deklaráciou cieľa, ale jasným source of truth, field ownershipom, semantic diffom, idempotentnými actions, status evidence a retry politikou, ktorá rešpektuje failure semantics.

Kvalitný controller nepredstiera okamžitú konzistenciu. Ukazuje, ktorú generáciu spracoval, kde sa proces nachádza, prečo nemôže pokračovať a ako sa po reštarte alebo partial failure bezpečne vráti k jednému autoritatívnemu výsledku.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Idempotencia](idempotency.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Immutable vs. mutable infrastructure →](immutable-vs-mutable-infrastructure.md)
<!-- KNOWLEDGE-NAVIGATION:END -->