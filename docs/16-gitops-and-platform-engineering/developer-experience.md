# Developer experience

Developer experience (DevEx alebo DX) je to, ako developeri vnímajú a prežívajú celý systém práce potrebný na dodanie a prevádzku software. Zahŕňa nástroje, platformy, procesy, documentation, feedback, ownership, spoluprácu, interruptions, cognitive load, dôveru a schopnosť dostať sa do produktívneho flow. Nie je to iba spokojnosť s editorom ani synonymum pre rýchlosť pipeline.

DevEx je systémová vlastnosť. Lokálne rýchly tool môže zhoršiť celkový journey, ak vytvorí viac nejasných rozhodnutí, neskoré failures alebo skrytý operational toil. Naopak, bezpečný guardrail môže pridať jeden krok, ale zlepšiť predvídateľnosť a znížiť incidenty. Preto treba experience merať end-to-end a kombinovať lived experience so system evidence a business výsledkom.

## 1. Dominantný model

Dominantný model sleduje developer goal cez pracovný journey, jednotlivé interaction a feedback loops až po outcome a následné zlepšenie. Friction sa nehodnotí podľa počtu klikov, ale podľa toho, ako ovplyvňuje pochopenie, čakanie, flow, kvalitu rozhodnutia a schopnosť recovery.

DevEx acceptance verdict nevzniká pri zvýšení jednej activity metriky. Musí dokázať, že konkrétny cohort pri konkrétnom journey dosahuje lepší outcome s nižšou zbytočnou cognitive load a friction bez zhoršenia quality, reliability, security, collaboration alebo well-being.

```text
developer alebo team goal
→ exact journey, cohort a working context
→ current workflow a expected outcome
→ interactions, decisions, handoffs a feedback loops
→ observed flow, cognitive load a friction
→ system, qualitative a outcome evidence
→ causal hypothesis o bottlenecku
→ bounded technical, process alebo organizational intervention
→ changed developer behavior a experience
→ delivery, quality, operational a business verification
→ feedback closure a second-cohort validation
```

## 2. Developer experience, productivity a satisfaction

Developer experience a productivity sú prepojené, ale nie totožné. Experience opisuje, ako developer vníma a vykonáva prácu. Productivity opisuje účinnosť, s akou team alebo system premieňa effort na hodnotné outcomes. Satisfaction je jedna percepčná dimenzia a môže byť dôležitým signálom, no vysoká spokojnosť sama nedokazuje quality alebo business impact.

Praktické rozlíšenie:

```text
experience
→ friction, clarity, flow, confidence, cognitive load a feedback

productivity
→ hodnotný outcome vzhľadom na čas, effort, kvalitu a constraints

satisfaction/well-being
→ subjektívny vzťah k práci, nástrojom a prostrediu

activity
→ pozorované actions, napríklad commits, builds alebo deploys
```

Activity nie je automaticky output a output nie je automaticky outcome. Zvýšenie commits môže znamenať lepší flow, ale aj viac reworku. Rýchlejší code generation môže zrýchliť lokálnu task, ale zvýšiť review burden alebo production defects. DevEx measurement preto potrebuje viac dimenzií a guard metrics.

## 3. Exact developer-experience subject

Organizačné tvrdenie „DevEx sa zlepšil“ je príliš neurčité. Experience sa líši podľa teamu, seniority, workflowu, repository, platform generation, lokality, on-call contextu a času. Exact subject zabraňuje tomu, aby aggregate priemer zakryl skupinu s kritickou friction alebo aby sa zmena v jednom journey pripísala celej platforme.

DevEx subject zahŕňa:

- **Developer alebo team cohort** — identifikuje role, skúsenosť, ownership, location alebo workload segment, ktoré menia knowledge a constraints.
- **Goal a journey** — pomenúva konkrétny outcome, napríklad „prvá production zmena nového service“, nie abstraktné „používanie platformy“.
- **Toolchain a platform generation** — viaže experience na exact versions, configurations, policies a supported path, pretože zmena rollout cohortu môže vytvoriť rozdielne správanie.
- **Repository, service a environment context** — oddeľuje monorepo, legacy service, regulated workload, local development, CI alebo incident response.
- **Time window a change boundary** — umožňuje porovnať baseline, intervention a post-change obdobie a kontrolovať sezónnosť alebo incident.
- **Expected outcome a quality constraints** — definuje, čo developer potrebuje dosiahnuť a ktoré security, reliability alebo correctness výsledky sa nesmú zhoršiť.
- **Experience dimensions a instruments** — určujú survey items, interviews, telemetry a observation points použité na hodnotenie.
- **Interruptions, waiting a external dependencies** — zachytávajú faktory mimo samotného toolu, ktoré formujú flow a lead time.
- **Support a organizational context** — zahŕňajú ownership clarity, review model, on-call, meeting load a access k expertíze.
- **Privacy a measurement purpose** — vysvetľujú, kto dáta používa, na aké rozhodnutia a prečo neslúžia na individuálne performance ranking.

## 4. Tri hlavné DevEx dimensions

Výskum DevEx často používa tri praktické dimensions: feedback loops, cognitive load a flow state. Nejde o jediné možné členenie, ale poskytuje mechanistický model, ktorý spája technické a organizačné faktory.

### Feedback loops

Feedback loop je čas a kvalita informácie medzi action a poznaním výsledku. Developer potrebuje rýchlo zistiť, či code kompiluje, test prešiel, policy sa splnila, deployment používa správnu generation a user outcome funguje.

Rýchlosť sama nestačí. Feedback musí byť relevantný, dôveryhodný, actionable a viazaný na exact subject. Pipeline, ktorá za dve minúty vráti generic `failed`, môže mať horšiu experience než päťminútová kontrola s presným root cause a local reproduction.

### Cognitive load

Cognitive load je mentálna kapacita potrebná na pochopenie a vykonanie tasku. Intrinsic complexity patrí k problemu, napríklad distributed transaction. Extraneous load vzniká z nekonzistentných interfaces, skrytých dependencies, nejasných policies a potreby pamätať si tribal knowledge.

Platforma nemá odstrániť kontext potrebný na bezpečné rozhodnutie. Má odstrániť opakovanú extraneous complexity a prezentovať decisions v správnom čase s consequences.

### Flow state

Flow je sústredená práca s jasným cieľom, primeranou výzvou a minimom zbytočných interruptions. Tool latency, flaky tests, meetings, context switching, waiting approvals alebo incident alerts môžu flow rozbiť. Flow však nie je izolácia od collaboration; kvalitná synchronizácia a review sú súčasťou hodnotného outcome-u.

## 5. Developer journey a momenty pravdy

DevEx sa má mapovať podľa skutočného journey, nie podľa organizačných hraníc tool owners. Jeden developer goal často prechádza cez editor, build, review, CI, artifact, platform, deployment, telemetry a support.

Príklad journey:

```text
understand change
→ obtain repository a environment access
→ modify code a configuration
→ run local feedback
→ open change a receive review
→ CI a policy feedback
→ build immutable artifact
→ promote a deploy
→ verify runtime a business outcome
→ observe, support a learn
```

Momenty pravdy sú body, ktoré disproporčne ovplyvňujú dôveru: prvý onboarding, prvá failure, prvý production deploy, incident a upgrade. Happy path môže pôsobiť dobre, ale ak prvá chyba neukáže operation identity ani recovery, developer si vytvorí vlastný bypass.

Journey map má obsahovať actions, tools, decisions, waiting, emotions, evidence, ownera a handoffs. Má sa vytvárať z observation a telemetry, nie iba z process diagramu platformového tímu.

## 6. Friction taxonomy

Friction je odpor medzi developer intentom a hodnotným outcome-om. Nie všetka friction je zlá. Review, test alebo approval môžu byť potrebné controls. Problémom je zbytočná, nepredvídateľná alebo neactionable friction, ktorá neprináša primeranú hodnotu.

### Waiting friction

Developer čaká na build, review, environment, approval, capacity alebo support. Dôležité je odlíšiť active processing od queue a external waitu a ukázať ownera a expected next transition.

### Interaction friction

Rozhranie vyžaduje redundantné údaje, tool switching, manuálny copy/paste alebo nejasné kroky. Počet klikov je iba proxy; rozhodujúce je, či interakcia zvyšuje error risk alebo cognitive load.

### Decision friction

Používateľ nevie, ktorú možnosť zvoliť, pretože defaults, trade-offs alebo policy consequences nie sú vysvetlené. Príliš veľa flexibility bez guidance môže byť horšie než opinionated path.

### Feedback friction

Výsledok je pomalý, flaky, generic alebo nekorelovaný s action. Developer opakuje experimenty bez istoty, či failure patrí code-u, platforme alebo environmentu.

### Access a dependency friction

Chýbajú permissions, network, data, identity alebo owner response. Manual access ticket môže byť symptóm chýbajúceho self-service alebo legitímnej high-risk boundary s nejasným SLO.

### Operational friction

Service sa ľahko vytvorí, ale ťažko diagnostikuje, upgraduje, obnovuje alebo odstráni. Create-only experience presúva cost do on-call a maintenance.

### Organizational friction

Nejasný ownership, conflicting priorities, meeting load, approval layers alebo slabá psychologická bezpečnosť blokujú flow aj pri rýchlych tooloch.

## 7. Feedback-loop architecture

Feedback loop má source, trigger, processing, result, delivery a action. Diagnostika pomalého feedbacku musí nájsť konkrétnu boundary.

```text
developer action
→ source snapshot a exact subject
→ local alebo remote execution admission
→ queue a compute
→ test/policy/tool processing
→ result classification
→ message, evidence a remediation guidance
→ developer decision
```

Celkový feedback time možno rozložiť na local preparation, queue, execution, result publication a time-to-understand. Zrýchlenie execution o 30 sekúnd nepomôže, ak queue trvá 20 minút alebo error vyžaduje ďalšiu hodinu investigation.

Dôveryhodnosť sa meria false positive, false negative, flaky behavior, reproducibility a correlation s production. Developer, ktorý nevie veriť zelenému testu alebo červenému policy resultu, vytvára retries a bypasses.

## 8. Cognitive load a platform boundaries

Platforma znižuje extraneous load štandardizáciou, managed integrations a progressive disclosure. Môže ju však zvýšiť, ak pridá vlastný DSL, portal, abstraction a status model bez odstránenia underlying tools.

Cognitive load inventory má skúmať:

- **Počet concepts potrebných pre bežný task** — koľko systems, identifiers a ownership boundaries musí developer pochopiť.
- **Consistency interfaces** — či rovnaký intent používa podobné patterns naprieč capabilities alebo každý plugin zavádza inú logiku.
- **Visibility state-u** — či developer vidí current desired, operation a effective state bez mentálneho skladania dashboardov.
- **Decision consequences** — či input vysvetľuje security, cost, availability a lifecycle effect.
- **Exception complexity** — či odchýlka má supported flow alebo vyžaduje znalosť interného platform kódu.
- **Learning a documentation cost** — či examples a docs zodpovedajú current generation a reálnym failure cases.
- **Memory a tribal knowledge** — či úspech závisí od konkrétneho človeka, hidden Slack message alebo ručného sequence.

Nová abstraction je oprávnená, keď odstráni viac complexity, než vytvorí, a zachová debugging escape. Toto treba overiť s novice aj experienced cohortom.

## 9. Flow, interruptions a work-in-progress

Flow ovplyvňuje technická latency aj pracovný systém. Keď developer čaká na CI, môže začať ďalšiu task, čím rastie work-in-progress a context switching. Krátke delays sa preto môžu multiplikovať do dlhého cycle time a reworku.

Relevantné signály zahŕňajú:

- **Uninterrupted focus time** — dlhšie bloky bez neplánovaných handoffs, alerts alebo tool waitu podporujú komplexnú prácu.
- **Context switches** — počet súbežných changes, repositories, incidents alebo approval threads zvyšuje reorientation cost.
- **Work-in-progress age** — staré otvorené changes signalizujú waiting, dependency alebo scope problém.
- **Review a response latency** — feedback od ľudí je súčasťou flow a musí sa segmentovať podľa timezone, ownership a risku.
- **Build/test turnaround** — local aj CI loop ovplyvňujú batch size a willingness testovať často.
- **Unplanned work a toil** — incidenty, flakes, access opravy a platform workaroundy vytláčajú product work.

Cieľom nie je maximalizovať nepretržitú individuálnu aktivitu. Collaboration, pairing a incident response môžu prerušiť local flow, ale zlepšiť team outcome. Preto sa flow interpretuje v kontexte goalu.

## 10. Documentation, discoverability a learning experience

Developer experience začína pred použitím toolu. Používateľ potrebuje nájsť správnu capability, pochopiť contract a vytvoriť mentálny model. Search result bez version a ownership môže viesť k stale pathu alebo nebezpečnému workaroundu.

Documentation experience má:

- **Task-oriented entry** — začína developer goalom a supported journey, nie internou štruktúrou platformového tímu.
- **Version a applicability** — uvádza platform generation, environment, segment a prerequisites.
- **Mechanism explanation** — opisuje state, authority, side effects, retry a failure boundaries, aby používateľ vedel diagnostikovať.
- **Executable examples** — examples sú testované, secret-safe a používajú current interfaces.
- **In-context links** — error, operation alebo catalog entity vedú na relevantný section a ownera.
- **Feedback a update path** — používateľ vie nahlásiť nejasnosť a dokumentácia má accountable ownera a freshness signal.

Docs page views nepreukazujú pochopenie. Relevantnejšie je task success, search refinement, repeated support question a qualitative evidence.

## 11. Measurement architecture

DevEx potrebuje mixed-method measurement. System telemetry ukazuje, čo sa stalo a kedy. Surveys a interviews ukazujú, ako developer vnímal clarity, effort, trust a friction. Outcome metrics ukazujú, či zmena podporila hodnotnú delivery bez zhoršenia quality.

### Percepčné measures

Validated alebo konzistentné survey items môžu merať satisfaction, cognitive load, flow, feedback quality, documentation, autonomy a trust. Majú byť viazané na recent konkrétny journey, nie všeobecnú náladu bez contextu.

### Behavioral a system measures

Telemetry môže merať queue, build, review, deployment, retries, abandonment, manual interventions, tool switching alebo operation failures. Musí byť normalizovaná podľa teamu, workloadu a automation/bot aktivity.

### Outcome measures

Sledujú cycle time, first production outcome, change failure, reliability, rework, innovation allocation alebo support burden. Nemajú sa interpretovať ako individuálna performance bez kauzálneho contextu.

### Qualitative evidence

Interviews, diary studies, observation a support transcripts odhaľujú mechanisms a coping strategies. Malý počet hlbokých pozorovaní môže vysvetliť pattern, ktorý agregovaný dashboard iba ukazuje.

### Privacy a trust

Measurement purpose, access, retention a rozhodnutia musia byť transparentné. DevEx telemetry použitá na ranking jednotlivcov mení behavior, podporuje gaming a ničí dôveru aj validity dát.

## 12. Counterbalanced metrics a Goodhart risk

Jedna metrika sa po naviazaní na target môže stať zlým measure. Developer môže zvýšiť commits rozdelením práce, skrátiť review schválením bez hĺbky alebo znížiť ticket count presunom otázok do private chatu.

Balanced system má spájať:

```text
speed
+ quality
+ developer effectiveness/experience
+ business impact
+ reliability a safety guard metrics
```

Príklad intervention „zrýchliť CI“ môže sledovať p50/p95 feedback, queue, flake rate, local reproducibility, developer trust, change failure a compute cost. Zlepšenie p50 pri horšom p95 alebo vyššej flaky retry rate nemusí zlepšiť experience.

Metrics sa používajú na diagnosis a improvement, nie na univerzálny score. Aggregation má zachovať distributions a cohorts; priemer zakryje long tail, ktorý často vytvára najhoršiu friction.

## 13. Baseline, cohort a causal inference

Before/after graf bez control contextu môže pripísať platforme efekt sezóny, team reorganization, release freeze alebo zmeny workload mixu. DevEx intervention potrebuje baseline a jasnú change boundary.

Silnejší design používa:

- **Matched cohorts** — porovná podobné tímy alebo repositories s a bez intervention a kontroluje workload context.
- **Staggered rollout** — zavádza zmenu po skupinách a sleduje trend pred a po každom rollout-e.
- **Within-subject journey** — rovnakí developeri vykonajú comparable task na starej a novej path generation.
- **Experience sampling** — zbiera krátky feedback blízko konkrétneho eventu a znižuje recall bias.
- **Qualitative follow-up** — overí mechanismus zmeny a odhalí, či metric improvement nevznikol workaroundom.
- **Guard outcomes** — sleduje quality, security, reliability, well-being a cost, aby local speed nevytvorila externality.

Nie každá organizácia potrebuje formálny experiment, ale každá by mala explicitne uviesť assumptions a alternatívne vysvetlenia.

## 14. DevEx a platform product feedback loop

Developer experience je jeden z hlavných evidence streams pre Platform as a Product. Nemá byť vlastnený izolovaným „developer productivity“ tímom bez authority meniť platform, proces alebo organization.

Closure flow:

```text
friction signal
→ exact journey, cohort a generation
→ evidence bundle zo survey, telemetry, support a observation
→ causal hypothesis
→ owner podľa technical/process/organizational boundary
→ prioritized intervention
→ rollout a guard metrics
→ developer a business verification
→ communicated learning a backlog closure
```

Ak developer repeatedly hlási pomalý deploy, root cause môže byť CI queue, broad test scope, approval policy, unreliable environment alebo nejasný status. Správny owner sa určí až po evidence, nie podľa tool názvu v sťažnosti.

## 15. DevEx počas incidentu a on-call

Operational experience je súčasť DevEx. Platforma, ktorá je príjemná pri create, ale nečitateľná počas incidentu, prenáša cost do najrizikovejšieho momentu.

Incident experience potrebuje:

- **Exact subject a timeline** — on-call vidí release, config, secret, operation a cohort bez manuálneho spájania desiatich dashboardov.
- **Actionable signals** — alert uvádza affected outcome, ownera, evidence a safe first action namiesto generic resource symptomu.
- **Authority a break-glass clarity** — používateľ vie, čo môže meniť, kto schvaľuje výnimku a ako sa live change reconcile-ne.
- **Runbook a tooling freshness** — instructions zodpovedajú current generation a commands vysvetľujú observation a mutation.
- **Cognitive load control** — incident interface redukuje noise, duplicate pages a conflicting statusy a zachováva decision log.
- **Recovery verification** — closure zahŕňa business outcome, backlog drain, reconciliation a second observation, nie iba green alert.

On-call toil, alert fatigue a time-to-understand sú DevEx signály aj reliability risks.

## 16. AI-assisted development ako DevEx intervention

AI coding tool môže znížiť time-to-first-draft alebo vysvetliť unfamiliar code, ale jeho outcome závisí od context quality, review, security a learning. Zvýšenie generated code activity nepreukazuje vyššiu productivity alebo lepšiu experience.

Evaluation má viazať exact tool/model/policy generation na task cohort a sledovať:

- **Task completion a time-to-understand** — či developer dosiahne správny outcome a rozumie výsledku.
- **Review a rework burden** — či lokálna speed nevytvára viac kontroly, opráv alebo code ownership problémov.
- **Quality a security** — correctness, tests, vulnerabilities a policy violations sú guard metrics.
- **Cognitive load a trust** — či tool znižuje search a boilerplate alebo pridáva verification a uncertainty.
- **Learning a skill retention** — či používateľ zostáva schopný diagnostikovať a meniť generated code.
- **Data a IP boundary** — context, prompts, outputs a retention spĺňajú organizational policy.

AI je teda ďalší component developer journey, nie náhrada za jeho end-to-end measurement.

## 17. Connected incident `GITOPS-PAY-63`

LaunchPad dashboard označil `Regulated Service v4` za úspešný DevEx program. Report ukazoval 95 % successful templates, median task 9 minút a rastúci počet nových services. Leadership preto vynútil adoption a uzavrel starý onboarding path.

Measurement subject bol však nesprávny:

```text
merané:
→ Backstage scaffolder task od submit po terminal status

nemerané:
→ eligibility a discovery
→ waiting approvals/quota/network
→ manual tickets a support
→ first usable environment
→ first production business outcome
→ template forks a bypasses
→ developer trust a cognitive load
→ update, incident a decommission journey
```

Survey sa pýtal všeobecne „Ako ste spokojní s LaunchPad?“ a bol poslaný iba používateľom, ktorých task skončil `Succeeded`. Abandoned a failed cohorts nedostali otázku. System metrics navyše započítali bot-generated PR ako developer delivery activity.

Pre `LP-8841` developer zažil 7-minútový green task, potom 19 hodín waiting, tri tool changes, tri manual tickets, duplicate PR po retry a undocumented IAM repair. Dashboard napriek tomu zaznamenal úspešný request a rýchly onboarding.

Observed end-to-end evidence po reanalýze:

```text
portal completion rate:                    95%
first usable environment rate:             61%
first production outcome rate:             42%
median time-to-first-production:            3.8 dňa
requests with manual intervention:          44%
cohort reporting high status trust:         34%
cohort able to diagnose first failure:      29%
services with fork/bypass behavior:         38%
```

### Developer-experience root cause

Measurement optimalizoval lokálnu platform activity a vylúčil neúspešných používateľov. Neexistoval exact journey subject, mixed-method evidence ani counterbalanced quality a business outcomes. Green metric preto priamo maskovala waiting, cognitive load, low trust a operational friction.

### Redesign

DevEx program definuje journey `regulated service request → first production settlement canary → second change`. Telemetry koreluje portal, durable operation, Git, provider, Flux, runtime a support events. Experience sampling sa spúšťa pri success, failure, abandonment aj manual intervention a interview cohorts zahŕňajú greenfield, brownfield a on-call používateľov.

```text
journey baseline
→ rollout capability RSP-4.1 pre pilot cohort
→ system telemetry + short event survey
→ observation prvého requestu a prvého failure
→ quality/security/reliability guard metrics
→ weekly evidence triage
→ bounded improvement
→ first-production a second-change verification
→ transparent learning report
```

## 18. Developer-experience acceptance verdict

Acceptance verdict musí dokázať zlepšenie konkrétneho developer journey a vysvetliť mechanismus. Nemôže byť založený na jednej activity metrike, voluntary survey úspešných používateľov alebo priemere bez cohortov.

Verdict preto koreluje tri vrstvy. Experience evidence ukazuje, či používateľ rozumel stavu, dôveroval systému a zvládol rozhodnutie bez neprimeranej cognitive load. Flow evidence meria waiting, handoffs, rework a čas k usable outcome-u. Guard outcomes dokazujú, že zdanlivé zrýchlenie nezvýšilo incidenty, security exceptions, support toil alebo downstream business chyby. Zlepšenie je prijaté iba vtedy, keď sa tieto vrstvy vzťahujú na rovnaký cohort, journey generation a časové okno.

Mechanistické vysvetlenie odlišuje koreláciu od príčiny. Ak time-to-first-production klesne po novom path-e, treba ukázať, ktorú wait alebo decision boundary path odstránil, či sa nezmenila zložitosť workloadov a či benefit pretrval pri druhom tíme, prvom failure a druhej zmene. Bez tejto triangulácie môže dashboard pripísať platforme sezónne ľahší workload alebo vylúčiť abandoned requests a vytvoriť false-positive DevEx verdict.

Developer-experience design je prijatý, keď:

- **DevEx subject je exact** — cohort, journey, platform/tool generation, environment, time window a outcome sú explicitné.
- **Feedback, cognitive load a flow sú vysvetlené mechanisticky** — intervencia vie, ktorú boundary mení a aký dôsledok očakáva.
- **Journey je end-to-end** — discovery, access, local work, review, CI, deployment, operations a support nie sú izolované podľa tool owners.
- **Mixed-method evidence je reprezentatívna** — system data, survey, interview a observation zahŕňajú success, failure, abandonment a relevantné segmenty.
- **Metrics sú counterbalanced** — speed alebo activity sú spojené s quality, reliability, security, experience a business impactom.
- **Distribution a cohorts zostávajú viditeľné** — p95, long tail, novice, brownfield, regulated a on-call experience sa nestratia v priemere.
- **Measurement je privacy-safe a non-punitive** — účel, access a retention sú transparentné a dáta sa nepoužívajú na naivný individual ranking.
- **Causal hypothesis je testovateľná** — baseline, change boundary, alternative explanations a guard outcomes sú definované.
- **Feedback má ownera a closure** — signal vedie k action, explicitnému non-action alebo ďalšiemu experimentu a používateľ pozná výsledok.
- **Operational experience je zahrnutá** — first failure, incident, upgrade a decommission sú súčasťou journey, nie externalita.
- **Improvement prejde second-cohort testom** — benefit sa nepotvrdí iba na expert pilot tíme alebo happy-path deme.
- **Business a developer outcomes sa nerozchádzajú** — lepšia experience nevzniká presunutím risku, toil-u alebo reworku na inú skupinu.

## 19. Troubleshooting flow

DevEx troubleshooting začína konkrétnym goalom a cohortom. Všeobecné tvrdenie „developer productivity klesla“ sa rozloží na journey, feedback, cognitive load, flow a outcome evidence.

```text
Developeri hlásia friction alebo metrics ukazujú slabý outcome
→ exact cohort, journey, generation a time window
→ current process a authoritative event timeline
→ feedback-loop decomposition
→ waiting, interaction, decision, access, operational a organizational friction
→ cognitive-load a context-switch evidence
→ survey/interview/observation + system telemetry
→ quality, reliability, security a business guard outcomes
→ competing causal hypotheses
→ bounded intervention a staged rollout
→ developer behavior, experience a end-to-end outcome verification
```

Ak CI latency klesla, ale satisfaction a cycle time sa nezlepšili, hypotézy zahŕňajú review wait, flaky trust, batch size, environment delay alebo unrelated meeting load. Diskriminačný dôkaz potrebuje journey decomposition, nie ďalšie optimalizovanie už rýchlej execution fázy.

## 20. Anti-patterny

### DevEx je developer happiness

Satisfaction je dôležitá, ale DevEx zahŕňa feedback, cognitive load, flow, trust, ownership a schopnosť dosiahnuť kvalitný outcome. Príjemný tool s false statusom má zlú experience.

### Productivity zmeriame commits alebo lines of code

Activity measures sú ľahko gameable a ignorujú complexity, quality, collaboration a business impact. Môžu byť diagnostickým signálom v context-e, nie individuálnym verdictom.

### Survey je subjektívna, používajme iba system data

Perception, cognitive load a trust nie sú plne pozorovateľné z logov. System data zas korigujú recall bias a ukazujú reálny timeline. Potrebné sú oba typy evidence.

### Platforma zrýchlila task, preto zlepšila DevEx

Local task môže byť rýchlejší a celý journey pomalší pre waiting, rework alebo operations. Zmena sa hodnotí od goalu po outcome a s guard metrics.

### DevEx team opraví všetky friction problémy

Root cause môže patriť platforme, application architecture, review modelu, security policy alebo organization. DevEx funkcia potrebuje evidence a routing authority, nie paralelný backlog bez owners.

## 21. Kontrolné otázky

1. Ako sa developer experience líši od productivity, satisfaction a activity?
2. Prečo exact DevEx subject potrebuje cohort, journey a tool/platform generation?
3. Ako feedback loops, cognitive load a flow vysvetľujú technické aj organizačné friction?
4. Kedy je friction potrebný control a kedy zbytočný odpor?
5. Ako rozložíš feedback time na queue, execution, publication a understanding?
6. Prečo nová abstraction môže zvýšiť cognitive load?
7. Ako system metrics a qualitative evidence navzájom dopĺňajú svoje limity?
8. Prečo sa DevEx metrics nemajú používať na naivný ranking jednotlivcov?
9. Ako matched cohort alebo staggered rollout zlepšia causal confidence?
10. Prečo `GITOPS-PAY-63` vykazoval green DevEx dashboard pri 42 % first-production outcome?
11. Ako operational a incident experience patrí do developer journey?
12. Čo musí obsahovať developer-experience acceptance verdict?

## Glossary impact

Relevantné pojmy: developer-experience subject, developer journey, feedback-loop quality, developer cognitive load, extraneous cognitive load, developer flow state, developer friction taxonomy, moment of truth, time-to-understand, DevEx mixed-method evidence, experience sampling, DevEx counterbalanced metrics, developer-outcome guard metric, DevEx feedback closure, developer-experience acceptance verdict.

## Primárne zdroje

- [Greiler, Storey, Noda — An Actionable Framework for Understanding and Improving Developer Experience](https://arxiv.org/abs/2205.06352)
- [Fagerholm, Münch — Developer Experience: Concept and Definition](https://arxiv.org/abs/1312.1452)
- [Forsgren et al. — The SPACE of Developer Productivity](https://doi.org/10.1145/3454122.3454124)
- [Google Research — Developer Productivity for Humans](https://research.google/pubs/developer-productivity-for-humans-a-human-centered-approach-to-developer-productivity/)
- [Google Research — Measuring Flow and Friction for Developers](https://research.google/pubs/measuring-flow-and-friction-for-developers-part-6-measuring-flow-and-friction-for-developers/)
- [CNCF TAG App Delivery — Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/)
- [CNCF TAG App Delivery — Platform Engineering Maturity Model](https://tag-app-delivery.cncf.io/wgs/platforms/maturity-model/readme/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Self-service](self-service.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Service catalog →](service-catalog.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
