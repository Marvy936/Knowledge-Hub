from pathlib import Path

path = Path('docs/16-gitops-and-platform-engineering/internal-developer-platform.md')
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

for old, new in [
('- service/application provisioning;', '- **Service a application provisioning** — vytvára stable service identity, repository/catalog relationships a runtime contract namiesto jednorazového skeletonu bez ownera.'),
('- repository a pipeline bootstrap;', '- **Repository a pipeline bootstrap** — nastavuje source permissions, branch protections, reusable delivery components a provenance boundary, ktoré zostávajú spravovateľné po prvom commite.'),
('- environment a infrastructure provisioning;', '- **Environment a infrastructure provisioning** — transformuje capability intent na cloud/Kubernetes resources s explicitným state, quota, cost a deletion lifecycle-om.'),
('- deployment a promotion workflows;', '- **Deployment a promotion workflows** — oddeľujú candidate build od environment authority a sledujú desired, controller-resolved, runtime a business verdict.'),
('- secrets, identity a policy integration;', '- **Secrets, identity a policy integration** — viaže workload na least-privilege credentials a presadzuje tenant, data a compliance controls na authoritative boundaries.'),
('- observability a operational readiness;', '- **Observability a operational readiness** — poskytujú version-aware telemetry, alerts, SLO, runbooks a ownership potrebné na diagnostiku a recovery.'),
('- software catalog a ownership metadata;', '- **Software catalog a ownership metadata** — prepájajú service, API, resources, ownera a lifecycle a umožňujú impact, orphan a deprecation analysis.'),
('- support, lifecycle a decommissioning.', '- **Support, lifecycle a decommissioning** — definujú escalation, upgrades, migrations, ownership transfer a bezpečné odstránenie resources aj data.'),
]: repl(old, new)

for old, new in [
('- vysoká cognitive load;', '- **Vysoká cognitive load** — developer musí rozumieť provider, Kubernetes, CI/CD, IAM, networking a operations detailom ešte pred implementáciou business capability.'),
('- inconsistent implementations;', '- **Inconsistent implementations** — rovnaká potreba sa rieši odlišnými templates, permissions a lifecycle semantics a výsledok sa ťažko audituje a podporuje.'),
('- security controls aplikované neskoro alebo nerovnomerne;', '- **Neskoré alebo nerovnomerné security controls** — policy sa objaví až pri review alebo incidente a teams ju obchádzajú custom automationou.'),
('- ticket queues pre rutinné provisioning úlohy;', '- **Ticket queues pre rutinné provisioning** — central team sa stáva serial execution bottleneckom a developer stráca okamžitý feedback o constraints a výsledku.'),
('- skryté ownership a support gaps;', '- **Skryté ownership a support gaps** — resource existuje bez jasného service ownera, operational tieru alebo escalation pathu a incident sa presúva medzi tímami.'),
('- duplicated automation;', '- **Duplicated automation** — každý tím kopíruje scripts a pipelines, ktoré postupne divergujú v dependencies, retry a security behavior-e.'),
('- rozdielne lifecycle a cleanup semantics;', '- **Rozdielne lifecycle a cleanup semantics** — create je jednoduchý, ale update, migration, expiry a delete nemajú konzistentné preconditions a zanechávajú orphan resources.'),
('- failure diagnosis naprieč množstvom UI a credentials.', '- **Fragmentovaná diagnosis** — operation identity a evidence sú rozdelené medzi portal, Git, cloud, CI, cluster a provider, takže local green status zakrýva partial failure.'),
]: repl(old, new)

for old, new in [
('- requester identity a team ownership;', '- **Requester identity a team ownership** — určujú, kto request autorizuje, kto nesie application outcome a do ktorého tenant boundary patria outputs.'),
('- business/system/domain context;', '- **Business, system a domain context** — prepájajú service s architecture, data a dependency relations a umožňujú policy podľa business kritickosti.'),
('- requested capability a version;', '- **Requested capability a version** — identifikujú contract a implementation generation, podľa ktorých control plane validuje inputs a plánuje migration.'),
('- service name a globally unique identity;', '- **Service name a globally unique identity** — tvoria stable key pre repositories, namespaces, DNS, catalog a idempotent read-back bez kolízie s iným requestom.'),
('- data classification a compliance profile;', '- **Data classification a compliance profile** — menia allowed regions, encryption, retention, audit, network a operator-access controls.'),
('- runtime model, regiony a availability tier;', '- **Runtime model, regions a availability tier** — určujú topology, failure domains, capacity a recovery objective namiesto iba výberu veľkosti compute.'),
('- repository, language a build profile;', '- **Repository, language a build profile** — určujú scaffolding, dependency, test, artifact a supply-chain contract, ktorý platforma bude spravovať.'),
('- environment a promotion topology;', '- **Environment a promotion topology** — definuje desired-state authorities, predecessor evidence, approvals, rollout rings a recovery flow.'),
('- network exposure a dependency requirements;', '- **Network exposure a dependency requirements** — určujú ingress/egress, DNS, TLS, service identity a policy relationships s ďalšími systems.'),
('- data stores, queues a secret needs;', '- **Data stores, queues a secret needs** — deklarujú stateful capabilities, durability, schema/event a credential lifecycle, ktoré musia byť provisioned a verified.'),
('- SLO/operational tier a on-call ownership;', '- **SLO, operational tier a on-call ownership** — nastavujú observability, alerting, support hours, error budget a escalation expectations.'),
('- cost center, quota a lifecycle/expiry;', '- **Cost center, quota a lifecycle/expiry** — viažu consumption na budget a limit a poskytujú autoritu pre review, suspension a cleanup.'),
('- policy bundle a platform contract version;', '- **Policy bundle a platform contract version** — zachytávajú exact decision logic a guarantees, aby retry alebo audit nereinterpretovali historický request novými pravidlami.'),
('- idempotency key a expected outputs.', '- **Idempotency key a expected output inventory** — umožňujú resume/read-back rovnakého semantic requestu a odhaliť missing, duplicate alebo foreign resources.'),
]: repl(old, new)

for old, new in [
('- čo platforma garantuje;', '- **Guarantees** — pomenúvajú availability, security, backup, delivery a support outcomes, za ktoré platform team nesie zodpovednosť.'),
('- ktoré decisions sú fixed defaults;', '- **Fixed defaults** — znižujú cognitive load a vytvárajú supportable baseline; zmena defaultu potrebuje versioning a impact na existing consumers.'),
('- ktoré choices môže consumer meniť;', '- **Consumer choices** — dávajú flexibilitu iba tam, kde platforma vie validovať a prevádzkovať všetky povolené variants.'),
('- ktoré constraints sú policy;', '- **Policy constraints** — odlišujú bezpečnostné alebo compliance boundaries od opinionated convenience a musia byť enforced mimo UI.'),
('- aký je expected provisioning time;', '- **Expected provisioning time** — vytvára latency/SLO contract a určuje, kedy je operation slow, blocked alebo failed.'),
('- ako sa capability pozoruje;', '- **Observability contract** — definuje status, metrics, logs, operation IDs a developer-facing evidence potrebné na troubleshooting.'),
('- kto rieši incidenty;', '- **Incident ownership** — rozdeľuje platform mechanism failure, consumer configuration a application business failure a definuje escalation.'),
('- ako sa upgrade-ne, migruje a odstráni;', '- **Upgrade, migration a deletion lifecycle** — chráni existing data a consumers a zabraňuje tomu, aby create-only automation produkovala permanentný debt.'),
('- čo platforma negarantuje.', '- **Explicit non-guarantees** — odhaľujú residual responsibilities a limity, aby consumer nepovažoval abstraction za neexistujúcu end-to-end garanciu.'),
]: repl(old, new)

for old, new in [
('- dve repositories s podobnými názvami;', '- **Duplicate repositories** — rozdelia source a permissions medzi dva candidate identities a znemožnia jednoznačne určiť authoritative codebase.'),
('- duplicate catalog entities;', '- **Duplicate catalog entities** — vytvoria conflicting owner, API a lifecycle projections a pokazia impact a support routing.'),
('- overlapping namespaces;', '- **Overlapping namespaces alebo runtime scopes** — umožnia dvom operations meniť rovnaké resources a prelomia tenant a cleanup ownership.'),
('- druhé cloud resources s novými IDs;', '- **Second cloud resources s novými IDs** — vytvoria unmanaged cost, data a credentials, ktoré pôvodný operation ledger nepozná.'),
('- conflicting DNS alebo IAM roles.', '- **Conflicting DNS alebo IAM identities** — môžu presmerovať traffic alebo privilege na nesprávny resource graph aj keď jednotlivé create calls uspeli.'),
]: repl(old, new)

for old, new in [
('- input schema a validation;', '- **Input schema a validation** — určujú allowed request space, typy, constraints a semantic cross-field rules skôr, než action vykoná side effect.'),
('- version identity;', '- **Template/contract version identity** — viaže generated output a support behavior na exact implementation a umožňuje migration inventory.'),
('- output inventory;', '- **Output inventory** — zaznamenáva repositories, files, resources a relationships vytvorené operationou pre read-back, update a decommission.'),
('- secret-safe rendering;', '- **Secret-safe rendering** — zabraňuje vloženiu plaintext credentials do files, task logs, SCM diffs alebo generated documentation.'),
('- dry-run/preview;', '- **Dry-run a preview** — ukazujú effective files, permissions a downstream resource plan bez predstierania, že preview je authoritative apply.'),
('- idempotent actions;', '- **Idempotent actions** — používajú stable identities a read-before-create, aby retry obnovil rovnaký output namiesto duplicates.'),
('- permission boundaries;', '- **Permission boundaries** — limitujú template action tokens, allowed destinations a tenant scope a bránia confused-deputy abuse.'),
('- migration/deprecation strategy;', '- **Migration a deprecation strategy** — prenáša existing generated consumers na new contract bez manuálneho copy-paste a permanentných old variants.'),
('- tests nad positive aj forbidden inputs.', '- **Positive a forbidden-input tests** — dokazujú expected output aj to, že path injection, arbitrary URLs, privilege escalation a cross-tenant targets sú odmietnuté.'),
]: repl(old, new)

for old, new in [
('- ktorý tím vlastní service;', '- **Service owner** — určuje decision, on-call a lifecycle zodpovednosť a musí vychádzať z authoritative team identity, nie stale text labelu.'),
('- ktoré APIs implementuje a konzumuje;', '- **Provided a consumed APIs** — umožňujú compatibility a impact analysis pri change-i, deprecation alebo incidente.'),
('- ktoré runtime resources mu patria;', '- **Runtime resource relations** — prepájajú catalog entity s cluster, cloud, database a queue identities pre cost, drift a orphan detection.'),
('- kde je source, documentation a dashboards;', '- **Source, documentation a dashboards** — poskytujú navigation, ale links musia byť generated alebo health-checked, aby catalog nebol collection stale bookmarks.'),
('- aký lifecycle a operational tier má;', '- **Lifecycle a operational tier** — menia support, SLO, compliance, deprecation a deletion policy a nesmú byť iba marketingovým statusom.'),
('- ktoré dependencies a risks existujú;', '- **Dependencies a risks** — ukazujú blast radius, critical paths a accepted exceptions a potrebujú freshness z authoritative systems.'),
('- či je orphaned alebo deprecated.', '- **Orphaned alebo deprecated state** — spúšťa ownership remediation alebo migration/closure workflow namiesto pasívnej catalog značky.'),
]: repl(old, new)

for old, new in [
('- cluster-admin pre každého developera;', '- **Cluster-admin pre developera** — obchádza platform subject, policy a audit a dáva callerovi právo meniť unrelated tenants a shared control plane.'),
('- arbitrary Terraform execution;', '- **Arbitrary Terraform execution** — umožní requestu zvoliť provider, module, backend a side effects mimo versioned capability contractu.'),
('- možnosť zvoliť ľubovoľnú IAM role;', '- **Ľubovoľná IAM role** — mení platform service na privilege-escalation deputy a oddeľuje requested capability od granted cloud authority.'),
('- direct production mutation;', '- **Direct production mutation** — vytvára hidden writer mimo environment Git/controller reconciliation a komplikuje rollback a drift evidence.'),
('- cross-tenant secret access;', '- **Cross-tenant secret access** — porušuje isolation aj vtedy, keď portal UI zobrazuje iba vlastné services; provider a backend musia odmietnuť request.'),
('- obídenie cost alebo data controls.', '- **Obídenie cost alebo data controls** — umožní unlimited spend, wrong region alebo prohibited storage bez review a attribution.'),
]: repl(old, new)

for old, new in [
('- request rate, latency a rejection reasons;', '- **Request rate, latency a rejection reasons** — ukazujú demand, user-facing responsiveness a či schema/policy friction blokuje validné journeys.'),
('- queue depth a oldest operation age;', '- **Queue depth a oldest operation age** — odlišujú burst backlog od stuck operation a odhaľujú porušenie provisioning SLO skôr než priemerná latency.'),
('- per-step success/failure/retry;', '- **Per-step success, failure a retry** — lokalizujú Git, cloud, IAM, GitOps alebo verification boundary a odhaľujú hot-loop amplification.'),
('- downstream API latency a throttling;', '- **Downstream API latency a throttling** — vysvetľujú platform delay a umožňujú backpressure namiesto aggressive retry stormu.'),
('- duplicate/idempotency conflict rate;', '- **Duplicate a idempotency conflict rate** — odhaľuje unstable semantic keys, provider token mismatch a resources vytvorené mimo operation inventory.'),
('- partial/unknown operations;', '- **Partial a unknown operations** — predstavujú explicitný recovery queue a nesmú sa stratiť v aggregate failed count-e.'),
('- reconciliation lag;', '- **Reconciliation lag** — meria čas medzi authoritative desired mutation a observed/effective resource state-om.'),
('- policy denials a common remediation gaps;', '- **Policy denials a remediation gaps** — ukazujú, či guardrail vysvetľuje actionable fix alebo vytvára tickets a bypass behavior.'),
('- time-to-first-successful-deploy;', '- **Time to first successful deploy** — meria end-to-end developer outcome od requestu po usable delivery, nie iba rýchlosť scaffoldingu.'),
('- capability adoption a abandonment;', '- **Capability adoption a abandonment** — odhaľujú, či contract rieši reálnu potrebu alebo users odchádzajú pri configuration/support friction.'),
('- support incidents a toil;', '- **Support incidents a toil** — identifikujú abstractions s vysokou hidden complexity a manuálne steps, ktoré treba productizovať.'),
('- orphan resources a failed decommissions;', '- **Orphan resources a failed decommissions** — merajú lifecycle debt, cost a attack surface po partial delete alebo ownership loss.'),
('- cost per capability/tenant.', '- **Cost per capability a tenant** — umožňuje capacity, quota a product decisions a koreluje spend s ownerom a useful outcome-om.'),
]: repl(old, new)

for old, new in [
('- announced replacement;', '- **Announced replacement** — poskytuje supported successor, compatibility a decision rationale namiesto iba dátumu vypnutia.'),
('- affected consumer inventory;', '- **Affected consumer inventory** — identifikuje exact services, versions, owners a runtime resources, ktoré ešte závisia od deprecated capability.'),
('- migration tooling;', '- **Migration tooling** — automatizuje preview, change a verification a musí byť idempotentné a recovery-aware pre partial consumers.'),
('- deadlines a exceptions;', '- **Deadlines a exceptions** — určujú enforcement timeline a bounded waiver s ownerom, riskom a expiry namiesto permanentného odkladu.'),
('- progress evidence;', '- **Progress evidence** — meria authoritative usage a successful migrations, nie iba self-reported ticket completion.'),
('- final disable/delete gate;', '- **Final disable a delete gate** — overuje zero required consumers, backup/restore, data retention a owner approval pred irreversible action.'),
('- rollback alebo restore plan.', '- **Rollback alebo restore plan** — definuje, ako sa capability dočasne obnoví alebo consumer repairne, ak hidden dependency vznikne po closure.'),
]: repl(old, new)

for old, new in [
('- identity a group membership;', '- **Identity a group membership** — autentizujú requestera a authoritative team relation a nesmú sa spoliehať na user-supplied owner string.'),
('- API authorization;', '- **API authorization** — presadzuje action, capability, environment a resource scope na backend-e pre portal, CLI aj automation clients.'),
('- namespace/account/project boundaries;', '- **Namespace, account a project boundaries** — oddeľujú runtime, quotas, provider resources a administrative blast radius medzi tenants.'),
('- Git repository permissions;', '- **Git repository permissions** — obmedzujú source a environment desired-state writes a chránia branch, CODEOWNERS a promotion authority.'),
('- cloud IAM a quotas;', '- **Cloud IAM a quotas** — viažu platform execution role na tenant resources a bránia cross-account mutation a noisy-neighbor consumption.'),
('- secret provider paths;', '- **Secret provider paths** — zabezpečujú, že tenant-controlled request nevie cez shared platform identity čítať cudzie credentials.'),
('- network policies;', '- **Network policies** — obmedzujú east-west a egress reachability podľa service identity a nesmú byť iba generated documentation.'),
('- catalog visibility;', '- **Catalog visibility** — chráni sensitive topology a metadata a zároveň nesmie byť považovaná za underlying resource authorization.'),
('- operation logs a support tooling;', '- **Operation logs a support tooling** — filtrujú tenant data a secrets a presadzujú reader scope aj počas incident escalation.'),
('- cost attribution.', '- **Cost attribution** — viaže resources na tenant a ownera a umožňuje quota, chargeback, anomaly a orphan decisions.'),
]: repl(old, new)

for old, new in [
('- compromised developer account požiada o privilege escalation;', '- **Compromised developer account** — môže poslať syntakticky validný request na higher tier alebo foreign ownera; backend authorization a policy musia odmietnuť escalation.'),
('- malicious template input vykoná command alebo path injection;', '- **Malicious template input** — môže uniknúť z workspace, prepísať generated paths alebo ovplyvniť shell/tool arguments; actions potrebujú typed inputs a sandboxing.'),
('- plugin získa broad third-party token;', '- **Broad plugin token** — kompromitovaný plugin môže čítať alebo meniť repositories, cloud alebo CI mimo current operation subjectu.'),
('- workflow logs secret;', '- **Workflow secret logging** — prenesie credential do portal task history, observability alebo support systems s odlišnou retention a reader graphom.'),
('- confused deputy použije platform identity na cudzí tenant;', '- **Confused-deputy request** — platform identity vykoná inak nepovolenú action, ak downstream adapter neverifikuje tenant ownership resource coordinate-u.'),
('- stale approval sa aplikuje na zmenený request;', '- **Stale approval** — autorizuje old subject, no retry/rebase/template update zmení effective outputs bez nového reviewer decisionu.'),
('- SSRF alebo arbitrary URL source umožní exfiltration;', '- **SSRF alebo arbitrary URL source** — platform worker pristúpi k internal metadata, credentials alebo private endpoints v mene untrusted requestu.'),
('- compromised platform worker zmení Git/cluster mimo operation;', '- **Compromised platform worker** — zneužije broad tokens na mutations bez durable operation ID, takže prevention potrebuje scoped credentials a detection potrebuje writer audit.'),
('- catalog metadata odhalí sensitive topology;', '- **Catalog metadata disclosure** — odhalí internal endpoints, owners, data classification alebo dependency graph actorovi bez business need-to-know.'),
('- duplicate retry vytvorí unmanaged resources.', '- **Duplicate retry** — vytvorí second repository, cloud object alebo permission set mimo original inventory a ponechá cost, data a attack surface bez ownera.'),
]: repl(old, new)

add('## 24. Connected incident `GITOPS-PAY-62`', '''Incident sequence treba čítať ako päť partial outcomes, nie jeden dokončený task. Každý step zmenil iný system a posledný portal status nevykonal read-back ani nečakal na downstream acceptance.

Preto sa jednotlivé steps nižšie popisujú podľa authority a chýbajúceho closure-u. Ich lokálny úspech nevytvoril usable production capability a retry navyše nebol viazaný na rovnaký resource graph.''', 'Incident sequence treba čítať ako päť partial outcomes')
for old, new in [
('1. vytvoril repository;', '1. **Repository create uspel** — source identity vznikla, ale workflow ešte nemal runtime, secrets, promotion ani business evidence.'),
('2. zapísal catalog entity;', '2. **Catalog projection vznikla** — metadata tvrdili existenciu service-u skôr, než authoritative execution systems preukázali usable capability.'),
('3. vytvoril shared cluster ConfigMap `launchpad-runtime`;', '3. **Portal priamo vytvoril shared ConfigMap** — LaunchPad sa stal hidden production desired-state writerom mimo Git a tenant-scoped platform API.'),
('4. otvoril promotion PR;', '4. **Promotion proposal vznikol** — PR bol iba request na authority transition a ešte nepreukazoval merge, Flux reconciliation ani runtime generation.'),
('5. po úspešnej GitHub API odpovedi označil task `Completed`.', '5. **Portal označil task `Completed` po GitHub API odpovedi** — local API success nahradil durable end-to-end acceptance a skryl pending aj later failed states.'),
]: repl(old, new)

path.write_text(text, encoding='utf-8', newline='\n')
