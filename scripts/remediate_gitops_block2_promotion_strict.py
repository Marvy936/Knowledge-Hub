from pathlib import Path

path = Path('docs/16-gitops-and-platform-engineering/application-promotion.md')
text = path.read_text(encoding='utf-8')


def add(heading: str, prose: str, marker: str) -> None:
    global text
    if marker in text:
        return
    needle = heading + '\n\n'
    if needle not in text:
        raise SystemExit(f'Missing heading: {heading}')
    text = text.replace(needle, needle + prose.rstrip() + '\n\n', 1)


def repl(old: str, new: str) -> None:
    global text
    if new in text:
        return
    needle = old + '\n'
    if needle not in text:
        raise SystemExit(f'Missing line: {old}')
    text = text.replace(needle, new + '\n', 1)

add('### Invariant release contract', '''Invariant fields describe capabilities and compatibility assumptions encoded by the artifact. Ak sa environment overlay od nich odchýli bez explicitného release decisionu, runtime už nevykonáva contract, ktorý prešiel candidate evidence.

Každá položka preto musí zostať versionovaná spolu s artifactom alebo byť overená policy ako compatible range. Promotion nemá dovoliť, aby environment-specific convenience potichu zmenila event, schema, route alebo secret contract.''', 'Invariant fields describe capabilities')
for old, new in [
('- schema/event compatibility version;', '- **Schema a event compatibility version** — určuje, ktoré database a message formats candidate dokáže bezpečne čítať a zapisovať počas mixed-version rollout-u.'),
('- required API capabilities;', '- **Required API capabilities** — pomenúvajú endpointy, protocol features a provider semantics, bez ktorých artifact síce môže štartovať, ale nevykoná intended behavior.'),
('- route-policy minimum;', '- **Route-policy minimum** — viaže application behavior na najnižšiu podporovanú routing generation a zabraňuje promotion k stale policy, ktorá mení business destination.'),
('- secret key names a formats;', '- **Secret key names a formats** — definujú interface medzi workloadom a secret materialization; zmena názvu, encodingu alebo credential formátu vyžaduje coordinated release.'),
('- migration generation;', '- **Migration generation** — identifikuje required schema/data transition a určuje, ktoré application versions zostávajú compatible pred a po jej vykonaní.'),
('- feature-code compatibility.', '- **Feature-code compatibility** — určuje, ktoré feature-flag states sú implementované a bezpečné, aby runtime flag nemohol aktivovať code path neoverený candidate evidence-om.'),
]: repl(old, new)

add('### Environment-owned configuration', '''Environment-owned fields vyjadrujú legitímne differences v capacity, topology a exposure. Ich ownerom je target environment, ale values musia zostať v bounded schema a nesmú meniť invariant application contract.

Promotion review preto nevyžaduje identickú configuration medzi stagingom a production. Vyžaduje vysvetlený delta, policy limits a target-specific evidence tam, kde environment value mení load, dependency alebo security behavior.''', 'Environment-owned fields vyjadrujú legitímne differences')
for old, new in [
('- replicas a resource sizing;', '- **Replicas a resource sizing** — odrážajú target load a availability tier, no musia rešpektovať application concurrency, startup a dependency-capacity assumptions.'),
('- regional endpoints;', '- **Regional endpoints** — smerujú workload na target-specific dependencies a vyžadujú TLS, authorization, latency a data-residency validation.'),
('- tenant IDs;', '- **Tenant IDs** — viažu deployment na správny business a authorization scope; wrong value môže vytvoriť cross-tenant data alebo billing incident.'),
('- exposure percentage;', '- **Exposure percentage** — určuje rollout cohort a risk budget a musí byť koordinované s observability a automatic abort policy.'),
('- alert thresholds;', '- **Alert thresholds** — môžu byť target-specific podľa trafficu a SLO, ale nesmú skryť release regression zmenou oracle-u počas promotion.'),
('- environment-specific secret references.', '- **Environment-specific secret references** — odkazujú na target credential authority bez kopírovania plaintextu a musia spĺňať artifactom požadovaný key/version contract.'),
]: repl(old, new)

add('### Runtime-owned state', '''Runtime-owned fields sú observations alebo controller decisions vznikajúce po promotion. Environment Git môže určovať policy pre ich vznik, ale promotion nesmie commitovať volatile hodnoty ako authoritative release input.

Ak by promotion kopírovala runtime state medzi environmentmi, vytvorila by stale feedback loop: current HPA decision, lease alebo provider outcome by sa zmenili na nový intended state bez samostatného business rozhodnutia.''', 'Runtime-owned fields sú observations')
for old, new in [
('- controller status;', '- **Controller status** — opisuje observed convergence a conditions konkrétneho targetu; je evidence, nie portable desired configuration.'),
('- HPA current replicas;', '- **HPA current replicas** — je momentálny autoscaling outcome odvodený z target metrics, nie promotion value, ktorú treba kopírovať zo stagingu.'),
('- dynamic leases;', '- **Dynamic leases** — majú krátku validity a authority v runtime coordination systeme; commitnutie do Git-u by obnovovalo expirovaný operational state.'),
('- queue offsets;', '- **Queue offsets** — identifikujú consumer progress a patria broker/consumer group authority, nie release manifestu.'),
('- provider operation outcomes.', '- **Provider operation outcomes** — sú read-back evidence external side effectu a nesmú sa zameniť za desired request alebo opakovať cez promotion.'),
]: repl(old, new)

add('## 11. Database a stateful compatibility', '''Stateful gate musí modelovať, že code a data sa nevracajú rovnakým mechanizmom. Application digest možno zmeniť novým Git commitom, ale už vykonaná migration, backfill alebo event publication môže zostať nezvratná.

Preto gate skúma reader/writer matrix, rollout order a recovery pre partial outcomes. Jednotlivé otázky nižšie rozhodujú, či je bezpečný rollback, roll-forward alebo iba compensation a data reconciliation.''', 'Stateful gate musí modelovať')
for old, new in [
('- ktoré application versions čítajú a zapisujú ktoré schema variants;', '- **Reader/writer matrix** — mapuje každú active application version na schema variants, ktoré číta a zapisuje, a odhaľuje nekompatibilný mixed-version cohort.'),
('- či migration je online, blocking alebo destructive;', '- **Migration execution class** — online, blocking alebo destructive behavior určuje required capacity, lock budget, maintenance window a rollback boundary.'),
('- či rollback old artifactu zostáva compatible;', '- **Rollback compatibility** — overuje, či old code po schema alebo data transitione ešte rozumie novému state-u a nevytvorí ďalšiu korupciu.'),
('- či background jobs alebo event consumers zaostávajú;', '- **Lagging background consumers** — môžu po promotion stále spracúvať old schema/event generation a zmeniť data podľa starého contractu.'),
('- či regiony/rings používajú mixed versions;', '- **Regional a ring version inventory** — ukazuje, kde ešte existujú old readers/writers a kedy možno bezpečne vykonať contract cleanup.'),
('- ako sa opraví partial alebo unknown migration outcome.', '- **Partial alebo unknown migration recovery** — vyžaduje operation identity, read-back a repair/compensation plan namiesto blind retry potentially non-idempotent migration.'),
]: repl(old, new)

add('## 13. Promotion graph a concurrency', '''Promotion graph je state machine nad viacerými evidence a authority branches. Každá edge určuje, ktorý predecessor result je potrebný a každý join musí definovať, či paralelné výsledky patria tej istej candidate generation.

Concurrency preto nie je iba problém Git merge conflictu. Dve syntakticky merge-nuteľné changes môžu vytvoriť semantic release kombináciu, ktorá nikdy neprešla spoločným testom ani approvalom.''', 'Promotion graph je state machine')
for old, new in [
('- predecessor evidence requirements;', '- **Predecessor evidence requirements** — definujú, ktorý exact environment result a candidate generation oprávňujú vstup do ďalšieho node-u.'),
('- parallel branches;', '- **Parallel branches** — umožňujú regionálne, performance alebo compliance validation súbežne, ale každý result musí zostať viazaný na rovnaký immutable subject.'),
('- merge/join podmienky;', '- **Merge a join podmienky** — určujú, či sú required všetky branches, quorum alebo target-specific subset a ako sa invaliduje stale branch result.'),
('- environment-specific blockers;', '- **Environment-specific blockers** — zachytávajú target outage, capacity, freeze alebo compliance condition bez nesprávneho označenia candidate-u za globálne chybný.'),
('- expiry dôkazu;', '- **Evidence expiry** — zabraňuje promotion na základe starého resultu po zmene dependencies, policy database alebo target contextu.'),
('- rollback propagation;', '- **Rollback propagation** — určuje, či recovery jedného node-u blokuje alebo vracia downstream rings a ako sa zabráni opätovnému neskorému promotion-u stale candidate-u.'),
('- whether a later environment may skip predecessor.', '- **Skip policy** — explicitne rozhoduje, kedy možno environment preskočiť, ktoré equivalent evidence ho nahrádza a kto nesie residual risk.'),
]: repl(old, new)

add('## 17. Rollback, roll-forward a supersession', '''Recovery decision musí rozložiť release na vrstvy s odlišnou reversibility. Vrátenie image digestu je iba jedna mutation; route, schema, credential, provider registration a data side effects môžu vyžadovať samostatný transition alebo zostať nezvratné.

Nasledujúci inventory slúži na eligibility analysis. Pre každú vrstvu sa určuje current authority, backward compatibility, already-produced side effects a oracle, ktorý potvrdí recovery.''', 'Recovery decision musí rozložiť release')
for old, new in [
('- application artifact;', '- **Application artifact** — možno zvyčajne vrátiť immutable digestom, iba ak old code zostáva compatible s current schema, config a external contracts.'),
('- configuration;', '- **Configuration** — rollback musí obnoviť celý effective values/overlay graph a nesmie ponechať hidden override z novšej release generation.'),
('- route/exposure;', '- **Route a exposure** — traffic možno presunúť na old cohort, ale sessions, caches a in-flight operations potrebujú drain a cohort-aware verification.'),
('- feature flags;', '- **Feature flags** — vypnutie capability môže obmedziť impact, no už vykonané writes alebo events tým nie sú automaticky kompenzované.'),
('- schema;', '- **Schema** — destructive alebo contracted migration často nie je safely reversible; expand/contract design rozhoduje, či old code možno obnoviť.'),
('- secret generation;', '- **Secret generation** — old credential môže byť revoked alebo compromised, takže recovery nesmie slepo obnoviť historical secret reference.'),
('- provider registration;', '- **Provider registration** — remote route, webhook alebo credential state má vlastnú authority a môže vyžadovať read-back, compensation alebo new operation.'),
('- data side effects.', '- **Data side effects** — settlements, messages a writes sa nevracajú Git commitom; potrebujú idempotent repair, reconciliation alebo business compensation.'),
]: repl(old, new)

add('## 19. Connected incident `GITOPS-PAY-62`', '''Incident ukazuje promotion race, v ktorom approval subject zostal statický iba v UI. Shared base a cluster-local substitution sa medzi evidence a merge zmenili, takže final authoritative commit nepredstavoval tested staging generation.

Každý bod nižšie mení inú časť transitive release graphu. Ich spoločným následkom je, že promotion proposal prestal byť fresh a mal byť invalidovaný pred merge-om.''', 'Incident ukazuje promotion race')
for old, new in [
('- image automation zmenila shared base z `pay910a` na `pay910b`;', '- **Shared image base sa zmenila** — automation nahradila tested `pay910a` digestom `pay910b`, takže candidate bytes už nezodpovedali staging evidence.'),
('- LaunchPad zmenil route substitution z `1850` na `1849`;', '- **Cluster-local route input sa zmenil** — LaunchPad prepísal substitution na `1849` mimo Git reviewu a z rovnakého source commit-u vytvoril iný effective render.'),
('- staging evidence `E-778` zostala viazaná na `pay910a/1850`;', '- **Evidence zostala viazaná na old subject** — `E-778` dokazovala behavior `pay910a/1850`, nie kombináciu, ktorá sa neskôr dostala do production.'),
('- merge automation rebase-la PR bez re-renderu a revalidácie;', '- **Rebase neinvalidoval approval** — merge automation zmenila target base a transitive content bez final renderu, policy rerunu a nového reviewer decisionu.'),
('- production commit preto neidentifikoval skutočný effective configuration graph.', '- **Production commit nebol úplný release coordinate** — nepinoval hidden substitution a nedokázal reprodukovať image/route/secret combination vykonanú Fluxom.'),
]: repl(old, new)

add('### Redesign', '''Redesign zavádza immutable release manifest ako jediný promoted subject. Staging aj production referencujú rovnaký contract object a environment PR mení iba jeho reference, takže shared-base alebo hidden substitution drift už nemôžu ticho zmeniť candidate.

Final-merge render, target-base compare-and-swap a runtime generation endpoint uzatvárajú tri rozdielne races: zmenu Git graphu, zmenu target base-u a rozdiel medzi desired a actually loaded generation.''', 'Redesign zavádza immutable release manifest')
add('## 21. Troubleshooting flow', '''Troubleshooting porovnáva identity v poradí, v akom release získavala authority a bola materializovaná. Prvá odlišná generation ukazuje, či ide o stale evidence, proposal race, controller resolution, runtime rollout alebo business exposure failure.

Recovery vytvorí nový authoritative transition, nie edit historického promotion recordu. Po oprave sa opakuje final render, controller reconciliation aj business canary a second promotion musí prejsť bez zdedených stale approvals alebo locks.''', 'Troubleshooting porovnáva identity')

path.write_text(text, encoding='utf-8', newline='\n')
