from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8", newline="\n")


def insert_after_heading(path: str, heading: str, prose: str) -> None:
    text = read(path)
    prose = prose.strip()
    if prose in text:
        return
    marker = f"{heading}\n\n"
    if marker not in text:
        raise RuntimeError(f"Heading not found in {path}: {heading}")
    text = text.replace(marker, f"{marker}{prose}\n\n", 1)
    write(path, text)


def replace_exact(path: str, old: str, new: str) -> None:
    text = read(path)
    if new.strip() in text:
        return
    if old not in text:
        raise RuntimeError(f"Exact block not found in {path}: {old[:80]!r}")
    write(path, text.replace(old, new, 1))


def replace_subsection(path: str, heading: str, next_heading: str, body: str) -> None:
    text = read(path)
    start_marker = f"{heading}\n\n"
    if start_marker not in text:
        raise RuntimeError(f"Subsection not found in {path}: {heading}")
    start = text.index(start_marker) + len(start_marker)
    end = text.index(f"\n{next_heading}", start)
    current = text[start:end].strip()
    replacement = body.strip()
    if current == replacement:
        return
    text = text[:start] + replacement + "\n" + text[end:]
    write(path, text)


def replace_row(path: str, starts_with: str, new_row: str) -> None:
    text = read(path)
    lines = text.splitlines()
    replaced = False
    for index, line in enumerate(lines):
        if line.startswith(starts_with):
            lines[index] = new_row
            replaced = True
            break
    if not replaced:
        raise RuntimeError(f"Row not found in {path}: {starts_with}")
    write(path, "\n".join(lines) + "\n")


# Projects, groups and permissions
path = "docs/06-gitlab/projects-groups-permissions.md"
insert_after_heading(
    path,
    "## 2. Exact namespace subject",
    """
Access sa nedá vyhodnotiť bez presného namespace subjectu. Potrebujeme vedieť nielen názov projektu, ale aj GitLab inštanciu, numeric IDs, aktuálny parent chain, ownership boundary a generation po transfere alebo policy zmene. Nasledujúci YAML je preto identity envelope pre authorization rozhodnutie, nie iba inventár názvov.
""",
)
replace_exact(
    path,
    """Access paths zahŕňajú:

- direct project membership;
- inherited parent-group membership;
- project alebo group sharing s inou group;
- invited external user;
- service account alebo bot;
- personal, project alebo group access token;
- deploy token a CI job token;
- custom role permissions;
- instance administrator alebo external authorization system.

Effective capability je union allowed paths obmedzená resource-specific policy. Expired direct role neodstráni access, ak user stále dedí vyššiu parent role.
""",
    """Access path je konkrétny mechanizmus, ktorým principal získa capability nad projectom alebo jeho resource-mi. Inventár musí pri každom path-e uviesť source authority, rolu alebo scopes, expiry, vlastníka a operation, ktorú path povoľuje:

- **Direct project membership** je explicitný member record v projekte. Je ľahko viditeľný, ale môže byť iba jedným z viacerých súbežných paths.
- **Inherited parent-group membership** vzniká z parent group alebo subgroup. Odstránenie direct project role ho nemení a project transfer môže pridať úplne nový inherited graph.
- **Project alebo group sharing** pozýva inú groupu s maximálnou rolou a voliteľnou expiráciou. Effective user access potom závisí aj od membershipu v zdieľanej groupe.
- **Invited external user** je stále human principal so session, tokenmi a možným accessom cez ďalšie groups. Atribút external sám nevytvára least privilege.
- **Service account alebo bot** je non-human principal. Musí mať systémového ownera, bounded purpose, credential lifecycle a samostatnú audit identity.
- **Personal, project alebo group access token** prenáša capability cez kombináciu principalu, role, scopes, target resource-u a expiry. Zmazanie member row nemusí zneplatniť všetky token paths.
- **Deploy token a CI job token** majú užší product contract, ale stále môžu čítať alebo publikovať repository/package subjects podľa effective allowlistu a job contextu.
- **Custom role permission** dopĺňa base access level o konkrétne operations. Názov roly nepreukazuje effective permission set ani resource policy.
- **Instance administrator alebo external authorization systém** môže vytvárať authority mimo project member graphu. Takýto path sa musí evidovať oddelene, pretože bežný project API ho nemusí ukázať.

Effective capability je union všetkých platných paths, ktorú následne obmedzujú protected-resource a operation-specific policies. Expired direct role teda neodstráni access, ak principal stále dedí vyššiu parent rolu, používa share alebo drží aktívny token. Review sa uzatvára až po positive operation teste a forbidden teste každého významného alternate pathu.
""",
)
insert_after_heading(
    path,
    "## 13. Troubleshooting flow",
    """
Troubleshooting nezačína otázkou „akú rolu ukazuje UI“, ale presnou operáciou, ktorá bola povolená alebo odmietnutá. Každý krok nižšie zužuje authority graph: najprv identita resource-u a principalu, potom všetky membership/token paths, resource policy a napokon audit konkrétneho requestu. Až discriminating operation test odlíši inherited access od tokenu, admin bypassu alebo stale session.
""",
)
replace_subsection(path, "### Project member list ako celý access inventory", "### Broad parent Maintainer pre convenience", """
Project member list zobrazuje iba časť authority graphu. Nezahŕňa spoľahlivo všetky inherited, shared, token, admin a external-authorization paths, preto zelený export direct members nemôže uzavrieť access review. Complete verdict potrebuje effective membership API, token inventory, protected-resource policies a bounded operation test.
""")
replace_subsection(path, "### Broad parent Maintainer pre convenience", "### Shared bot user", """
Broad Maintainer membership na parent groupe sa dedí do descendants a zväčšuje blast radius každej chyby alebo kompromitácie. Convenience rola navyše často povoľuje meniť CI, variables, runners alebo project settings mimo pôvodného use case-u. High-risk subgroup má používať explicitnú boundary, menšie role a pravidelný forbidden-path test.
""")
replace_subsection(path, "### Shared bot user", "### Token bez expiry", """
Shared bot user spája viac systémov a ľudí pod jednu audit identity. Pri incidente nemožno určiť actor-a, bezpečne vykonať leaver transition ani rotovať credential bez neplánovaného výpadku všetkých consumerov. Každá automatizácia má mať vlastný non-human principal, ownera, purpose a revocation contract.
""")
replace_subsection(path, "### Token bez expiry", "### Transfer bez before/after authority diffu", """
Token bez expiry prežíva zmenu tímu, projektu aj pôvodného účelu. Aj keď sa nepoužíva, zostáva aktívnym alternate authority pathom a môže byť uložený v runner cache, credential store alebo externom systéme. Expiry, last-use evidence, rotation a target-side revocation sú súčasťou token lifecycle-u.
""")
replace_subsection(path, "### Transfer bez before/after authority diffu", "## 15. Kontrolné otázky", """
Project transfer mení parent inheritance, shares, runners, variables, registry paths a policy context, aj keď numeric project ID zostane rovnaké. Bez before/after authority diffu tím nevie, ktoré capabilities pribudli alebo zanikli. Transfer gate preto predpovedá nový graph, po operácii ho read-backne a testuje aj forbidden old a newly inherited paths.
""")

# Merge requests and approvals
path = "docs/06-gitlab/merge-requests-and-approvals.md"
insert_after_heading(path, "## 1. Dominantný change-to-merge model", """
Lifecycle nižšie opisuje kompiláciu merge verdictu, nie iba poradie obrazoviek v GitLab UI. Každý transition mení subject alebo evidence, na ktoré sa approval viaže: source SHA, target SHA, synthetic candidate, diff version, policy generation alebo pipeline context. Ak sa ktorýkoľvek z nich zmení, predchádzajúci verdict sa musí explicitne invalidovať alebo znovu preukázať.
""")
insert_after_heading(path, "## 2. Exact merge-decision subject", """
Merge decision potrebuje identity envelope, ktorý umožní dokázať, aké bytes a aký target context reviewer a pipeline skutočne posudzovali. Branch name alebo MR IID sú iba locators; bez source, target, candidate a diff generation nemožno odlíšiť fresh approval od stale badge-u. YAML preto spája source, policy a evidence do jedného auditovateľného subjectu.
""")
insert_after_heading(path, "## 13. Troubleshooting flow", """
Pri nesprávnom merge verdict-e sa najprv rekonštruuje časová os subjectu. Diff versions, force-push, target movement, approval reset a pipeline type sa čítajú ako samostatné state transitions; až potom sa skúma, ktorý alternate merge alebo direct-push path policy obišiel. Aggregate green badge je iba index do týchto záznamov.
""")
replace_subsection(path, "### Approval ako permanentný branch property", "### Reviewer rovná sa approver", """
Approval patrí konkrétnej diff/candidate generation, nie názvu branchu. Force-push alebo target movement môže zmeniť výsledný tree bez zmeny MR URL, takže retained approval môže autorizovať bytes, ktoré reviewer nikdy nevidel. Policy musí definovať reset/revalidation trigger a acceptance test ho musí reprodukovať.
""")
replace_subsection(path, "### Reviewer rovná sa approver", "### Branch pipeline ako merge result", """
Reviewer participation je technical evidence; approver eligibility je authorization decision podľa konkrétneho rule-u. User môže komentovať alebo resolve-núť discussion bez toho, aby spĺňal required ownership, independence alebo role constraints. Verdict preto kontroluje approved_by proti effective rule evaluation, nie iba zoznam reviewerov.
""")
replace_subsection(path, "### Branch pipeline ako merge result", "### Code Owners file bez enforcement testu", """
Branch pipeline testuje source branch v jednom target context-e alebo bez neho. Nezahŕňa automaticky current target SHA ani concurrent changes, ktoré vytvoria final merge candidate. Pre high-risk integráciu sa evidence viaže na merged-results alebo merge-train candidate a po target movement-e sa znovu vytvorí.
""")
replace_subsection(path, "### Code Owners file bez enforcement testu", "### Emergency direct push bez reconciliation", """
CODEOWNERS je source declaration, nie samostatný enforcement verdict. Pattern môže nematchovať presunutý file, protected branch nemusí vyžadovať Code Owner approval alebo alternate merge path môže rule obísť. Test musí zmeniť reprezentatívny owned path a potvrdiť, že neeligible actor merge nedokončí.
""")
replace_subsection(path, "### Emergency direct push bez reconciliation", "## 15. Kontrolné otázky", """
Emergency direct push obchádza merge-decision subject, approval freshness a často aj iný pipeline graph. Ak je break-glass nevyhnutný, credential musí byť incident-scoped, short-lived a auditovaný a výsledný mainline/runtime state sa následne reconciliuje cez normálny source a release lifecycle. Bez tejto closure zostáva production na nepreukázanom alternate authority path-e.
""")

# Protected branches and environments
path = "docs/06-gitlab/protected-branches-and-environments.md"
insert_after_heading(path, "## 2. Exact protection subject", """
Protection verdict musí pomenovať source ref, rule generation, actor capability, deployment target a artifact policy naraz. Human-readable pattern ako `main` alebo `production/*` je iba locator; effective behavior závisí od overlapping rules, current namespace a exact environment name. Nasledujúci subject preto oddeľuje source enforcement od runtime enforcement a spája ich release digestom.
""")
insert_after_heading(path, "## 13. Troubleshooting flow", """
Pri bypass-e sa branch, tag a environment badges nesmú zliať do jedného tvrdenia „bolo to protected“. Investigation sleduje každú capability osobitne: kto mohol meniť ref, kto vytvoril tag, aký pipeline/ref context dostal credential, ktorý environment pattern matchol a aká external identity vykonala runtime mutation. Prvý divergentný verdict určí skutočný bypass.
""")
replace_subsection(path, "### Maintainer push ako no-bypass policy", "### Protected tag ako immutable release", """
Maintainer-only push stále povoľuje direct source mutation mimo MR, iba ju obmedzuje na silnejšiu rolu. Ak policy vyžaduje review, `allowed_to_push` musí byť prázdne alebo presne bounded break-glass path a forbidden push test musí preukázať odmietnutie. Samotný protected badge no-bypass semantics nedokazuje.
""")
replace_subsection(path, "### Protected tag ako immutable release", "### Production kubeconfig v variable", """
Protected tag chráni creation Git refu, nie bytes v registry ani dôkazy, ktoré pipeline neskôr vytvorí. Rovnaký tag-triggered job môže rebuildnúť odlišný image alebo publikovať mutable tag. Release authority preto patrí immutable digestu a subject-bound provenance, nie samotnému Git tagu.
""")
replace_subsection(path, "### Production kubeconfig v variable", "### Environment protection podľa nesprávneho mena", """
Long-lived kubeconfig v CI variable je reusable alternate authority priamo k runtime API. Môže prežiť job, byť skopírovaný do workspace-u a obísť protected-environment approval cez job bez environment declaration. Short-lived federation viazaná na exact project/ref/environment zmenšuje capability aj revocation window.
""")
replace_subsection(path, "### Environment protection podľa nesprávneho mena", "### Review app status `stopped` ako cleanup proof", """
Protected-environment policy sa vyhodnocuje nad effective environment name. Ak job použije `prod/eu` a rule chráni iba `production`, credential a approval path môžu byť úplne odlišné. Naming contract sa preto validuje v resolved pipeline a testuje sa reprezentatívny dynamic name aj forbidden variant.
""")
replace_subsection(path, "### Review app status `stopped` ako cleanup proof", "## 15. Kontrolné otázky", """
GitLab status `stopped` je workflow record, nie inventory external resources. DNS, database, storage, IAM identity alebo namespace môžu zostať po partial cleanup-e. Closure potrebuje ownership labels, independent reconciliation a read-back absencie na každom authoritative targete.
""")

# GitLab CI/CD syntax
path = "docs/06-gitlab/gitlab-ci-cd-syntax.md"
insert_after_heading(path, "## 1. Dominantný source-to-job model", """
Tento model treba čítať ako compiler pipeline. Root YAML ešte nie je executable graph: includes sa resolve-nú, inheritance zmení fields, rules rozhodnú o existencii pipeline a jobs a až validný DAG sa odovzdá scheduleru. Každý troubleshooting krok preto musí uviesť, ktorú kompilovanú vrstvu pozoruje.
""")
insert_after_heading(path, "## 2. Exact pipeline configuration subject", """
Pipeline configuration subject viaže event, source/target candidate, root a transitive dependencies, variable context a očakávaný job inventory. Pipeline ID bez týchto vstupov nehovorí, či retry alebo nová pipeline vykonali rovnaký graph. Nasledujúci envelope je preto reproducibility a evidence contract, nie iba metadata export.
""")
insert_after_heading(path, "## 14. Troubleshooting flow", """
Keď job chýba alebo vznikla nesprávna pipeline, script jobu ešte nemusel byť nikdy spustený. Investigation ide od eventu cez config resolution a rules k resolved jobs; až potom rieši runner execution. Tento ordering odlíši compile-time omission od scheduling alebo runtime failure.
""")
replace_subsection(path, "### `.gitlab-ci.yml` diff ako whole graph review", "### Broad final `when: always`", """
Root `.gitlab-ci.yml` je iba vstup do resolved graphu. Includes, components, defaults, `extends`, variables a GitLab evaluation môžu zmeniť image, scripts, credentials aj job existence bez viditeľného lokálneho diffu. Review preto potrebuje pinned dependency inventory a merged/resolved configuration pre konkrétny event.
""")
replace_subsection(path, "### Broad final `when: always`", "### Security job iba podľa narrow `changes`", """
Broad catch-all rule môže vytvoriť job v push, MR, schedule aj child pipeline contextoch, prípadne vytvoriť duplicate pipelines. Taký job môže dostať iné variables, runner alebo credentials než author očakával. Rules sa uzatvárajú explicitným `when: never` a testovacou maticou eventov.
""")
replace_subsection(path, "### Security job iba podľa narrow `changes`", "### Mutable include", """
Narrow `changes` optimalizácia môže odstrániť security evidence pri zmene CI konfigurácie, generated source, lockfile-u alebo rename, ktorý diff-base nevyhodnotí podľa očakávania. Missing analyzer job nie je pass. Gate porovnáva expected analyzer inventory s resolved jobs a každý skip má explicitný applicability verdict.
""")
replace_subsection(path, "### Mutable include", "### Latest successful pipeline bez subject checku", """
Mutable include znamená, že rovnaký application SHA môže neskôr resolve-núť iný privileged graph. Tým sa stráca reproducibility aj význam predchádzajúceho reviewu. Include alebo component sa pinne na immutable revision a transitívne dependencies sa evidujú v resolved subjecte.
""")
replace_subsection(path, "### Latest successful pipeline bez subject checku", "## 16. Kontrolné otázky", """
„Latest successful“ je časový locator, nie dôkaz správneho candidate-u. Môže označiť push pipeline, branch pipeline alebo starú target generation s odlišným job inventory. Merge/deploy gate kontroluje pipeline source, candidate SHA, resolved config digest a expected evidence, nie iba status a timestamp.
""")

# Runners and executors
path = "docs/06-gitlab/runners-and-executors.md"
insert_after_heading(path, "## 1. Dominantný job-to-cleanup model", """
Lifecycle opisuje celú execution lease od scheduler verdictu po odstránenie residual state-u. Job status uzatvára iba GitLab execution record; workspace, process, container, VM, cloud resource alebo credential môže prežiť mimo neho. Runner acceptance preto potrebuje creation aj teardown identity a independent cleanup read-back.
""")
insert_after_heading(path, "## 2. Exact runner execution subject", """
Runner ID je iba vstupný locator. Reálny subject zahŕňa manager instance, executor a image generation, job trust class, mounts, network a credential policy, pretože rovnaký logical runner môže po autoscale alebo upgrade vykonať job v inom boundary. YAML nižšie spája scheduling a runtime evidence do jedného execution subjectu.
""")
insert_after_heading(path, "## 15. Troubleshooting flow", """
Pri runner incidente sa najprv potvrdí, prečo scheduler vybral konkrétny pool, a potom sa rekonštruuje runtime generation a residual state. Tags alebo protected flag nevysvetlia host mounts, workspace, metadata access ani external side effects. Discriminating test preto pracuje s exact jobom a forbidden capability, nie iba s runner UI.
""")
replace_subsection(path, "### Container executor equals secure isolation", "### Protected runner equals trusted code", """
Container executor mení process packaging, nie automaticky trust boundary. Privileged mode, host mounts, devices, Docker socket alebo shared kernel umožňujú host escape alebo cross-job observation. Isolation verdict sa viaže na effective runtime config a forbidden capability probes.
""")
replace_subsection(path, "### Protected runner equals trusted code", "### Shared shell runner", """
Protected runner obmedzuje eligibility podľa ref/job contextu, ale nepreukazuje, že code na protected refe je dôveryhodný. Direct push, retained approval alebo mutable include môže dostať untrusted bytes do protected pipeline. Source policy a runner policy sa musia testovať ako dva samostatné boundaries.
""")
replace_subsection(path, "### Shared shell runner", "### Static cloud credentials on runner", """
Shell executor spúšťa arbitrary code priamo na persistent hoste. Workspace, process table, home directory, sockets a local credentials sa môžu preniesť medzi projektmi, takže jeden job kompromituje celý runner scope. Použiteľný je iba pre úzko trusted code na dedicated alebo disposable hoste s independent cleanupom.
""")
replace_subsection(path, "### Static cloud credentials on runner", "### Job success equals cleanup success", """
Static cloud credential na runneri nie je viazaný na jeden job ani pipeline subject. Prežíva cancellation, zhoršuje attribution a pri úniku vyžaduje broad rotation. Short-lived federation s exact claims a target-side auditom umožní bounded issuance a rýchle forbidden-old-session overenie.
""")
replace_subsection(path, "### Job success equals cleanup success", "## 17. Kontrolné otázky", """
Successful job znamená, že runner odovzdal výsledný status, nie že všetky descendants zanikli. Child process, pushed image, cloud VM alebo temp credential môže pokračovať po ukončení jobu. Teardown sa preto read-backne a external reconciler odstráni resources podľa immutable job labels a TTL.
""")

# Variables and secrets
path = "docs/06-gitlab/variables-and-secrets.md"
insert_after_heading(path, "## 1. Dominantný value-to-capability model", """
Model sleduje value od autoritatívneho source-u po capability, ktorú job alebo application reálne použije. GitLab variable record, resolved job value, file/process exposure, external session a loaded consumer generation sú odlišné states s vlastným ownerom a revocation mechanizmom. Bez tohto rozlíšenia sa „rotácia“ môže skončiť iba zmenou jedného UI field-u.
""")
insert_after_heading(path, "## 2. Exact variable/secret subject", """
Exact subject musí pomenovať purpose, authoritative provider, GitLab distribution reference, generation, consumers a target credential. Samotný key name je mutable a môže byť shadowovaný v inom scope. YAML nižšie umožní korelovať resolved job metadata s provider auditom a consumer-loaded state-om bez vypísania secret value.
""")
replace_exact(path, """Secrets môžu uniknúť cez:

- command echo and debug tracing;
- process arguments and `/proc`;
- files/workspace/cache/artifacts;
- Docker build args/layers/history;
- environment dumps and crash reports;
- child processes and service containers;
- network exfiltration;
- transformed values not masked;
- generated manifests or Terraform plans.

Jobs handling high-value secret use restricted egress, ephemeral runtime and no untrusted source-controlled tools.
""", """Secret exposure path je každé miesto, kde sa capability presunie mimo pôvodný provider alebo bounded process. Každý path má inú retention a observation boundary:

- **Command echo a debug tracing** môžu zapísať raw alebo expanded value do durable job logu. Masking závisí od podporovaného formátu a nemusí zachytiť transformáciu.
- **Process arguments a `/proc`** sprístupňujú hodnotu iným procesom alebo host administratorovi počas execution window-u. Preferované sú file descriptor, stdin alebo provider-native helper s krátkou lifetime.
- **Files, workspace, cache a artifacts** vytvárajú kópie s vlastným access a retention lifecycle-om. Cleanup jobu nemusí odstrániť distributed cache alebo už uploadnutý artifact.
- **Docker build args, layers a image history** môžu secret zabudovať do immutable image graphu. Build secret mount musí byť non-persistent a výsledný image sa kontroluje na leaked material.
- **Environment dumps a crash reports** zbierajú široký process context a môžu opustiť GitLab cez observability alebo support systémy. Redaction sa vykonáva pred export boundary.
- **Child processes a service containers** dedia environment, files alebo network capability a môžu prežiť hlavný script. Process tree a runtime teardown sú preto súčasťou acceptance.
- **Network exfiltration** nepotrebuje log ani file; untrusted tool môže secret okamžite odoslať. High-value job používa restricted egress a pinned tooling.
- **Transformed values** ako base64, URL encoding alebo rozdelené substringy nemusia byť masked. Masking je accidental-disclosure control, nie data-loss prevention.
- **Generated manifests, Terraform plans a diagnostic bundles** môžu vložiť resolved secret do ďalšieho artifactu s dlhšou retention. Každý generator potrebuje explicitný sensitive-data contract.

Jobs handling high-value capability používajú trusted reviewed code, ephemeral runtime, bounded egress a short-lived credential. Acceptance zahŕňa aj search v artifacts/cache/logoch a target-side revocation, nie iba absenciu plain textu v jednom job logu.
""")
replace_subsection(path, "### Masked equals secure", "### Static production secret in group variable", """
Masking je best-effort redaction pre podporované log patterns. Neizoluje process, neobmedzuje egress, neskracuje lifetime a po úniku nič nerevokuje. Bezpečný verdict stojí na trusted job boundary, least privilege, short lifetime a target-side audit/revocation.
""")
replace_subsection(path, "### Static production secret in group variable", "### ID token equals least privilege", """
Group variable môže byť distribuovaná do veľkého descendant graphu a prežiť zmenu vlastníctva projektu. Long-lived production value tak získava broad blast radius a nejasný consumer inventory. Preferovaná je external authority a job-time federation viazaná na exact project, ref a environment.
""")
replace_subsection(path, "### ID token equals least privilege", "### Rotation only in GitLab UI", """
ID token je podpísané tvrdenie o job context-e, nie samotný least-privilege verdict. External trust policy môže akceptovať príliš broad issuer, audience alebo namespace claims a vydať silnú session. Acceptance preto číta resulting principal a testuje forbidden project/ref/environment combination.
""")
replace_subsection(path, "### Rotation only in GitLab UI", "### Secret in cache/artifact for job transfer", """
Zmena GitLab variable reference nemusí zmeniť target credential, existujúce sessions ani value načítanú v dlhodobom procese. Rotation lifecycle pokračuje provider revokáciou, redeploy/reloadom consumerov a old-credential forbidden testom. Až druhá operácia s novou generation uzatvára transition.
""")
replace_subsection(path, "### Secret in cache/artifact for job transfer", "## 17. Kontrolné otázky", """
Cache a artifact vytvárajú durable, downloadovateľnú kópiu mimo secret managera. Ich access, retention a mirror lifecycle sa líšia od credential TTL a cleanup jobu. Medzi jobs sa prenáša iba non-secret reference alebo sa credential znovu získa cez short-lived identity.
""")

# Artifacts and cache
path = "docs/06-gitlab/artifacts-and-cache.md"
insert_after_heading(path, "## 1. Dominantný job-output model", """
Model má dve vetvy s odlišnou autoritou. Artifact/report branch prenáša identifikované bytes alebo evidence, ktoré downstream consumer musí overiť; cache branch prenáša odstrániteľný performance state, ktorého miss alebo eviction nesmie zmeniť correctness. Nasledujúci diagram preto nie je iba workflow, ale trust a retention contract.
""")
insert_after_heading(path, "## 2. Exact output subject", """
Output sa nedá identifikovať iba filename-om. Exact subject viaže bytes alebo report na project, pipeline, producer job, candidate SHA, digest, schema a retention class, aby consumer vedel odmietnuť output z iného execution contextu. YAML nižšie je lineage envelope pre build aj evidence outputs.
""")
insert_after_heading(path, "## 3. Artifact creation and checksum", """
Creation step najprv stabilizuje bytes a potom vytvorí samostatný integrity claim. Deterministic archive znižuje rozdiely spôsobené časom a ownership metadata; checksum následne umožní producerovi aj consumerovi porovnať presný byte stream. Ani jeden krok však sám nedokazuje, z akého source-u artifact vznikol alebo kto manifest autorizoval.
""")
insert_after_heading(path, "## 4. Artifact declaration and transfer", """
GitLab YAML deklaruje, ktoré paths má producer uploadnúť a ktorý consumer ich má cez DAG dostať. Toto je transfer intent, nie read-back uploadu ani autentifikácia obsahu. Consumer preto kontroluje producer identity, checksum/provenance a vlastný expected candidate pred použitím artifactu.
""")
insert_after_heading(path, "## 14. Troubleshooting flow", """
Artifact incident sa lokalizuje po jednom transitione: vznik lokálneho outputu, upload, platform processing, retention/access a downstream download. Cache sa analyzuje oddelene podľa key-u, writer trustu a restore pathu, pretože cache hit nie je lineage evidence. Takýto ordering odlíši missing report od cache poisoning alebo expirovaného artifactu.
""")
replace_subsection(path, "### Cache as job output", "### Generic artifact as processed report proof", """
Cache je best-effort performance state s eviction a fallback semantics. Neposkytuje required hand-off, retention ani producer lineage, preto correctness nesmie závisieť od cache hitu. Required output sa prenáša artifactom alebo registry subjectom a testuje sa cold run.
""")
replace_subsection(path, "### Generic artifact as processed report proof", "### Missing analyzer report equals zero findings", """
Generic archive môže obsahovať file s názvom reportu, ale GitLab ho nemusí parse-nuť podľa report schema ani pripojiť k MR/security evidence. Upload acknowledgement preto nie je processing verdict. Gate kontroluje report declaration, schema, ingestion status a expected producer identity.
""")
replace_subsection(path, "### Missing analyzer report equals zero findings", "### Release asset linked to expiring job artifact", """
Chýbajúci report neobsahuje tvrdenie „zero findings“; znamená, že očakávané pozorovanie nevzniklo. Analyzer mohol byť omitted rules, crashnúť alebo zlyhať pred uploadom. Fan-in porovnáva static expected inventory s valid received reports a pri rozdiele vracia `INCOMPLETE`.
""")
replace_subsection(path, "### Release asset linked to expiring job artifact", "### Broad cache fallback across trust classes", """
Expiring job artifact môže zmiznúť počas support alebo incident window-u a jeho URL nie je immutable release identity. Release manifest má odkazovať na durable package/container/object subject s vlastnou retention a checksum/provenance. Job artifact môže zostať krátkodobou evidence kópiou, nie jediným release byte source-om.
""")
replace_subsection(path, "### Broad cache fallback across trust classes", "## 16. Kontrolné otázky", """
Fallback key, ktorý prepája fork alebo untrusted MR writera s protected build consumerom, mení cache na supply-chain bridge. Privileged job môže restore-núť generated code alebo executable state, ktoré nikdy nevytvoril trusted producer. Cache namespace, writer policy a consumer validation musia zachovať jednosmerný trust.
""")

# Container and package registry
path = "docs/06-gitlab/container-and-package-registry.md"
insert_after_heading(path, "## 1. Dominantný build-to-runtime registry model", """
Registry lifecycle oddeľuje publication request, immutable content graph, evidence binding, promotion a runtime resolution. Tag alebo version môže meniť mapovanie, zatiaľ čo digest/checksum identifikuje bytes; preto sa každý transition overuje nad content subjectom a producer identity. Diagram nižšie ukazuje, kde môže úspešný push zostať iba partial publication.
""")
replace_exact(path, """Cleanup policy must not delete:

- supported release artifacts;
- deployed digests;
- last-known-good recovery subjects;
- artifacts under incident/legal hold;
- evidence referenced by release manifest.

Tag-based cleanup can delete untagged but deployed digests if runtime uses digest and tag was removed. Runtime inventory and release catalog must protect content.
""", """Cleanup policy rozhoduje nad reachability a lifecycle subjectom, nie iba nad vekom tagu. **Supported release artifacts** zostávajú dostupné počas support window-u, pretože rollback, reprodukcia a zákaznícka diagnostika potrebujú presné bytes. **Deployed digests** sa chránia podľa runtime inventory; tag môže byť odstránený, hoci Pods alebo iný platform consumer stále používa digest.

**Last-known-good recovery subjects** zostávajú, kým nie je otestovaný náhradný recovery candidate. **Incident alebo legal hold** dočasne prepisuje bežnú retention, pretože registry events, manifests a evidence môžu byť forenzným subjectom. **Evidence referenced by release manifestom** sa maže až spolu s release lifecycle-om; oddelené odstránenie SBOM, provenance alebo signature bundle by zneplatnilo neskorší verification.

Tag-only cleanup môže zmazať untagged, ale nasadený digest alebo platform manifest, ktorý stále referencuje OCI index. Safe collector preto vytvorí protect set z release catalogu, runtime image IDs, mirrors, support policy a holds, potom vykoná preview, deletion a post-delete read-back. Cleanup success neznamená iba HTTP delete acknowledgement, ale aj zachovanie všetkých protected subjects a odstránenie intended unreachable contentu.
""")
replace_subsection(path, "### Mutable release tag", "### Successful push as complete publication", """
Mutable tag umožňuje, aby rovnaká verzia časom pomenovala iný index alebo package bytes. Predchádzajúce tests, signatures a deployment records sa potom viažu na neurčitý locator. Release publication používa write-once version policy a environmenty referencujú immutable digest.
""")
replace_subsection(path, "### Successful push as complete publication", "### Rebuild per environment", """
Push acknowledgement môže potvrdiť iba prijatie časti uploadov alebo manifestu. Multi-platform descriptors, referrers, SBOM, provenance alebo mirror replication môžu chýbať. Publication closure enumeruje celý graph, overí evidence binding a vykoná fresh registry read-back.
""")
replace_subsection(path, "### Rebuild per environment", "### Cleanup by tag only", """
Rebuild pre staging a production vytvára odlišné content subjects aj pri rovnakom source SHA. Staging evidence potom neplatí pre production bytes a environment-specific dependency drift sa skryje za rovnakú verziu. Build-once promotion kopíruje alebo referencuje exact digest a samostatne mení iba environment configuration.
""")
replace_subsection(path, "### Cleanup by tag only", "### Delete tag as revocation", """
Tag inventory neobsahuje všetky runtime alebo release references. Digest môže byť nasadený priamo, zrkadlený alebo držaný ako recovery subject aj po odstránení tagu. Cleanup protect set sa preto skladá z runtime, release, support a hold evidence, nie iba z current tags.
""")
replace_subsection(path, "### Delete tag as revocation", "## 17. Kontrolné otázky", """
Odstránenie tagu zruší jeden locator, ale deployed digest, mirror a local node cache zostávajú použiteľné. Revocation je samostatný policy record, ktorý blokuje nové promotion/admission a spúšťa runtime inventory a redeployment. Closure nastane až po odstránení alebo izolovaní všetkých affected cohorts.
""")

# Environments, deployments and releases
path = "docs/06-gitlab/environments-deployments-releases.md"
insert_after_heading(path, "## 1. Dominantný request-to-runtime model", """
Lifecycle oddeľuje request, GitLab workflow record, external controller convergence, runtime state a business acceptance. Tieto transitions môžu skončiť v rôznych časoch a s rôznym verdictom; job success preto nesmie automaticky nastaviť production success. Diagram nižšie je correlation contract medzi GitLabom a authoritative targetom.
""")
insert_after_heading(path, "## 2. Exact environment/deployment subject", """
Environment name je policy locator, nie úplná target identity. Exact subject musí pridať environment ID a generation, cluster/namespace alebo controller context, release manifest, deployment request a expected runtime digests. Bez toho sa rovnaké meno môže po migrácii alebo recreate viazať na iný target.
""")
insert_after_heading(path, "## 3. Environment declaration", """
`environment:` block pripája job ku GitLab environment recordu a ovplyvňuje protection, variables, deployment tracking a stop lifecycle. Je to source declaration, ktorú treba porovnať s resolved jobom a effective environment patternom. Samotný YAML nevie potvrdiť cluster context ani úspešnú external mutation.
""")
insert_after_heading(path, "## 14. Troubleshooting flow", """
False-green deployment sa rieši koreláciou jednej operation identity naprieč GitLab recordom, deploy jobom, external controllerom a runtime workloadom. Každý krok odpovedá na inú otázku: čo bolo požadované, čo bolo prijaté, čo sa convergovalo a čo reálne obsluhuje traffic. Až business probe uzatvára pôvodný outcome.
""")
replace_subsection(path, "### Deployment job success equals production success", "### GitLab environment name as exact target identity", """
Successful deploy job môže dokazovať iba API acknowledgement alebo Git commit. Controller môže neskôr zlyhať, rollout zostať partial alebo traffic smerovať na starú cohort. Production verdict potrebuje controller observed state, runtime digest/config read-back a business acceptance.
""")
replace_subsection(path, "### GitLab environment name as exact target identity", "### Release linked to expiring artifact", """
Rovnaký environment name môže po migrácii ukazovať na iný cluster, namespace, account alebo policy generation. Name preto zostáva locatorom a approval inputom, kým exact subject pridáva target IDs a generation. Deploy script aj read-back musia používať ten istý target envelope.
""")
replace_subsection(path, "### Release linked to expiring artifact", "### Environment stopped before cleanup proof", """
Release asset URL na job artifact môže expirovať alebo zmeniť access semantics počas support window-u. GitLab Release má odkazovať na immutable durable registry/package subject a release manifest. Pipeline artifact zostáva doplnkovou execution evidence, nie jediným distribučným zdrojom.
""")
replace_subsection(path, "### Environment stopped before cleanup proof", "### Fixed branch equals fixed production", """
Environment record môže byť označený `stopped` skôr, než sa odstránia DNS, IAM, storage, database alebo workload resources. Taký status vytvorí false-green lifecycle a orphan cost/security exposure. Cleanup closure vyžaduje independent inventory a read-back absencie pred finálnym stavom.
""")
replace_subsection(path, "### Fixed branch equals fixed production", "## 16. Kontrolné otázky", """
Fix na default branchi mení source subject, nie automaticky deployed artifact ani runtime. Build, scan, promotion, controller convergence a workload replacement môžu stále chýbať. Remediation sa uzatvára až keď production image/config identity zodpovedá fixed release manifestu a vulnerable cohort je odstránená.
""")

# Security scanning
path = "docs/06-gitlab/security-scanning.md"
insert_after_heading(path, "## 1. Dominantný attack-surface-to-runtime model", """
Security verdict vzniká až po spojení coverage a subject identity. Najprv sa z attack surface-u odvodí, ktoré analyzers a layers sú povinné; potom sa overí execution, report processing, risk decision a napokon nasadenie fixed artifactu alebo revokácia credentialu. Diagram preto oddeľuje „scanner bežal“ od „affected runtime je napravený“.
""")
insert_after_heading(path, "## 2. Exact scan subject", """
Scan subject musí uviesť, či evidence patrí source candidate-u, build artifactu, configuration generation alebo deployed runtime-u. Tieto subjects sa môžu líšiť aj v jednej pipeline a jeden čistý layer nepreukazuje ostatné. YAML nižšie spája expected analyzers, artifact/platform digests a deployed targets s policy generation.
""")
insert_after_heading(path, "## 16. Troubleshooting flow", """
Pri chýbajúcom alebo podozrivo čistom security verdicte sa najprv porovná expected a actual analyzer inventory. Potom sa pre každý analyzer sleduje execution, report schema/upload/ingestion a exact scanned subject; až následne sa hodnotí finding decision a deployment closure. Tento postup odlíši zero findings od zero evidence.
""")
replace_subsection(path, "### Successful analyzer job equals valid evidence", "### No report equals no findings", """
Analyzer process môže skončiť nula, hoci report nevznikol, je prázdny, schema-invalidný alebo ho GitLab nespracoval. Job status je iba execution verdict. Evidence gate kontroluje expected report, producer/scanner generation, schema, subject a ingestion status.
""")
replace_subsection(path, "### No report equals no findings", "### Source scan equals artifact scan", """
Absencia reportu neobsahuje žiadne bezpečnostné tvrdenie. Job mohol byť omitted rules, zlyhať pred artifact uploadom alebo scanovať unsupported target. Verdict je `INCOMPLETE`, kým expected inventory nemá validný report alebo explicitne schválený non-applicable dôvod.
""")
replace_subsection(path, "### Source scan equals artifact scan", "### Secret removed from Git equals revoked", """
Build môže pridať OS packages, generated code, vendored binaries alebo configuration, ktoré source analyzer nevidí. Artifact scan musí používať exact immutable digest a pri multi-platform image pokryť každý supported manifest. Lineage potom spája source a artifact evidence bez ich zámeny.
""")
replace_subsection(path, "### Secret removed from Git equals revoked", "### Fixed main equals fixed production", """
Odstránenie secretu z current Git tree nezneplatní provider key, sessions ani kópie v history, artifacts, cache a logs. Najprv sa revokuje target capability, potom sa rotujú consumers a vykoná old-key forbidden test. History cleanup rieši distribúciu kópie, nie revocation.
""")
replace_subsection(path, "### Fixed main equals fixed production", "## 18. Kontrolné otázky", """
Default branch môže obsahovať opravu, zatiaľ čo production stále beží na starom digest-e alebo config generation. Remediation potrebuje fixed immutable artifact, deployment/controller convergence, runtime read-back a odstránenie vulnerable cohortu. Dashboard source status bez tejto korelácie je false closure.
""")

# Practical walkthrough
path = "docs/06-gitlab/gitlab-pipeline-practical-walkthrough.md"
replace_exact(path, """Nedokazuje:

- že rollout controller vytvorí ready Pods;
- že image sa dá pull-núť;
- že Service selector nájde backendy;
- že aplikácia načíta správnu konfiguráciu;
- že business request prejde.

Preto po dry-run nasleduje reálny apply a runtime read-back.
""", """Server-side dry-run má presnú dôkaznú hranicu. API server overil object schema, admission a caller authorization pre daný request, ale nevytvoril novú persisted generation a nespustil controller lifecycle.

Dry-run preto nepreukazuje, že Deployment controller vytvorí ready Pods ani že scheduler, kubelet a registry dokážu image pull-nuť. Nevykoná Service selector/EndpointSlice convergence, takže neukazuje, či traffic nájde backendy. Application process nevznikol, a preto nemohol načítať ConfigMap, Secret ani environment-specific configuration. Napokon neprebehol žiadny request cez reálnu route, takže business outcome zostáva úplne neoverený.

Po dry-run nasleduje reálny apply, controller/runtime read-back, exact image/config identity, Service/EndpointSlice kontrola a business probe. Ak dry-run zlyhá, mutation sa nesmie vykonať; ak prejde, je to iba povolenie pokračovať do ďalších acceptance vrstiev.
""")

# GitLab troubleshooting
path = "docs/06-gitlab/gitlab-troubleshooting.md"
replace_exact(path, """Pre incident „green pipeline, old production image“ postupuj:

1. Ulož project/pipeline/job/deployment IDs a UTC timeline.
2. Zisti pipeline source, candidate SHA a resolved job inventory.
3. Over build producer a artifact/image digest, nie tag.
4. Over, ktorý pipeline a job vytvoril deployment record.
5. Read-backni target identity a live runtime digest.
6. Porovnaj route/serving cohort s workload generation.
7. Vykonaj business probe so stabilným request ID.
8. Až potom zvoľ retry, redeploy toho istého digestu, rollout recovery alebo nový release.
""", """Pri incidente „green pipeline, old production image“ sa najprv vytvorí immutable evidence envelope. Project ID, pipeline ID, job ID a deployment ID identifikujú GitLab records; UTC timeline umožní zoradiť source push, pipeline creation, artifact publication, deployment request a runtime observation bez lokálnych timezone nejasností. Tieto identifikátory sa uložia skôr, než retry alebo cleanup zmenia volatile state.

Potom sa určí execution subject. Pipeline source odlíši push, merge request, tag, schedule alebo parent/child context; candidate SHA pomenúva testovaný integrated commit a resolved job inventory ukáže aj jobs, ktoré chýbajú. Build producer sa viaže na artifact alebo OCI digest, nie na mutable tag, aby sa dalo preukázať, ktoré bytes scanner a deploy job skutočne použili.

Deployment record sa následne koreluje s producer pipeline/jobom a release manifestom. Na authoritative targete sa read-backne cluster/account/namespace identity, desired workload image a runtime `imageID`. Route a serving cohort sa porovnajú s workload generation, pretože healthy nový Deployment nemusí byť cohortou, ktorá prijíma používateľský traffic.

Až potom sa vykoná business probe so stabilným request ID alebo operation ID. Probe musí overiť client response aj durable business outcome a nesmie pri unknown outcome slepo vytvoriť druhú mutáciu. Podľa prvého divergentného transitionu sa zvolí retry bezpečnej read operation, redeploy toho istého immutable digestu, controller/rollout recovery alebo nový release; voľba nie je založená iba na zelenom alebo červenom UI statuse.
""")

# README and ledger
path = "docs/06-gitlab/README.md"
insert_after_heading(path, "## Aktuálny stav revalidácie", """
Step 2 chapter-by-chapter explanation-depth pass zachoval všetkých dvanásť existujúcich lifecycle a incident modelov a doplnil chýbajúce prose transitions. Každý code-first lifecycle/exact-subject/troubleshooting blok teraz najprv vysvetľuje, čo je subject, ako sa mení state a čo nasledujúci diagram alebo YAML dokazuje. Bare inventories pre effective access, secret exposure, artifact/cache authority, registry retention, dry-run hranicu a preserve-first troubleshooting boli nahradené mechanistickým výkladom; jednovetové anti-patterny teraz uvádzajú failure mechanism, dôsledok a acceptance boundary.
""")
replace_row("DOCUMENTATION-REVIEW-STATUS.md", "| `06-gitlab` — GitLab |", "| `06-gitlab` — GitLab | 12/12 chapter-by-chapter explanation-depth revalidation | Ready for user review | 2026-08-01 | Všetkých 12 authoritative kapitol bolo znovu prečítaných podľa namespace/change/pipeline/runner/capability/artifact/deployment/finding subjectu, state transitionu, read-backu, failure a recovery štandardu. Existujúce `GL-PAY-72/73/74`, API/CLI/YAML príklady, end-to-end pipeline walkthrough a preserve-first troubleshooting zostali zachované. Cielený pass doplnil mentálne modely pred lifecycle diagramami, exact-subject YAML a troubleshooting flows; rozvinul effective membership paths, secret-exposure mechanisms, artifact/report/cache lineage, registry retention reachability, deployment/runtime correlation a security evidence completeness; praktický dry-run a incident walkthrough teraz explicitne oddeľujú request, platform processing, runtime a business outcome. Jednovetové anti-patterny boli nahradené mechanizmom, dôsledkom a acceptance hranicou. README, review ledger, navigation, glossary a full audit boli synchronizované. Sekcia je Ready for user review, nie automaticky GitLab-runtime Verified ani používateľsky Accepted. |")

print("Section 06 explanation-depth transformation applied.")
