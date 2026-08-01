from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = "docs/07-infrastructure-as-code-and-configuration-management"


def p(name: str) -> Path:
    return ROOT / BASE / name


def read(name: str) -> str:
    return p(name).read_text(encoding="utf-8")


def write(name: str, text: str) -> None:
    p(name).write_text(text, encoding="utf-8", newline="\n")


def level(heading: str) -> int:
    m = re.match(r"^(#+) ", heading)
    if not m:
        raise RuntimeError(f"Invalid heading: {heading}")
    return len(m.group(1))


def span(text: str, heading: str) -> tuple[int, int]:
    marker = heading + "\n"
    h = text.find(marker)
    if h < 0:
        raise RuntimeError(f"Heading not found: {heading}")
    start = h + len(marker)
    current_level = level(heading)
    pos = start
    for line in text[start:].splitlines(keepends=True):
        m = re.match(r"^(#+) ", line)
        if m and len(m.group(1)) <= current_level:
            return start, pos
        pos += len(line)
    return start, len(text)


def replace_section(name: str, heading: str, body: str) -> None:
    text = read(name)
    start, end = span(text, heading)
    replacement = "\n" + body.strip() + "\n\n"
    if text[start:end] == replacement:
        return
    write(name, text[:start] + replacement + text[end:])


def prepend_section(name: str, heading: str, prose: str) -> None:
    text = read(name)
    start, _ = span(text, heading)
    prose = prose.strip()
    if prose in text[start:start + len(prose) + 20]:
        return
    write(name, text[:start] + "\n" + prose + "\n\n" + text[start:].lstrip("\n"))


# Ansible architecture
replace_section(
    "ansible-architecture.md",
    "## 3. Control node ako privilegovaná boundary",
    """Control node alebo automation controller resolve-ne `ansible.cfg`, execution runtime, inventory, variables, content paths a host pattern a následne vytvára per-host task contexts. Otvára connections alebo vykonáva local/API actions a zhromažďuje results, notifications a callback evidence. Preto je súčasne compilerom execution graphu, credential brokerom a často sieťovým pivotom k veľkej časti fleet-u.

Immutable execution-environment digest stabilizuje `ansible-core`, Python/system libraries a helper tools. Pinned collections stabilizujú modules a plugins; read-only source checkout bráni jobu prepísať approved content. Short-lived credentials, restricted egress a oddelené untrusted-validation/production-execution pools obmedzujú blast radius. Audit callback musí zachovať per-host/task identity bez vypísania secrets.

Tieto controls sa overujú cez effective image digest, collection manifest, plugin/search paths, resulting target identity a forbidden egress/credential probes. Samotný controller job status nepreukazuje, že runtime graph alebo credential boundary boli tie, ktoré reviewer schválil.""",
)
replace_section(
    "ansible-architecture.md",
    "## 5. Content graph: playbook, play, task, module, plugin",
    """Playbook je ordered orchestration viacerých plays. Každý play viaže host pattern na variables, privilege, strategy, batch a failure policy. Task potom vytvára samostatnú invocation pre každý eligible host a volá module/action alebo mení control flow.

Module implementuje observation a bounded mutation unit a vracia structured result. Action plugin môže časť logiky vykonať na controlleri, connection plugin určuje transport, inventory plugin vytvára target graph a callback plugin spracúva evidence. Collection všetky tieto executable prvky distribuuje ako versionovaný artifact.

FQCN, napríklad `ansible.builtin.template`, znižuje namespace ambiguity, ale neidentifikuje exact collection bytes ani execution environment. Run subject preto zachováva FQCN spolu s collection/image digestom a per-host dynamic include pathom. Vďaka tomu možno odlíšiť rovnaký YAML s odlišným plugin behaviorom.""",
)
replace_section(
    "ansible-architecture.md",
    "## 10. Strategy, forks a serial",
    """`strategy` určuje, ako hosts postupujú ordered tasks a či rýchlejší host môže predbehnúť ostatných. `forks` obmedzuje controller concurrency naprieč hosts, `serial` rozdeľuje play na rollout batches a `throttle` môže ešte užšie obmedziť konkrétnu task alebo block.

```yaml
- name: Rolling configuration rollout
  hosts: payments_app:&production
  serial: 4
  max_fail_percentage: 0
  tasks:
    - name: Configure host
      ansible.builtin.include_role:
        name: atlas.payments.runtime
```

`serial: 4` definuje intended batch size, ale nevytvára readiness gate. Playbook musí po každom batchi overiť loaded version, local health, load-balancer membership a capacity pred pokračovaním. `forks` ani `throttle` nenahrádzajú external API idempotency alebo distributed lock.

Evidence preto obsahuje expected batch manifest, attempted/converged hosts a synchronization point medzi batches. Partial batch alebo host removed from play nie je úspešný rollout iba preto, že ďalšie hosts skončili green.""",
)
replace_section(
    "ansible-architecture.md",
    "## 18. Competing hypotheses pri mixed fleet",
    """Symptóm „controller job success, dva hosts používajú starú konfiguráciu“ môže vzniknúť pred executionom, počas task/handler flowu alebo až v serving vrstve. H1–H3 testujú target completeness: host mohol chýbať v resolved inventory, byť vylúčený patternom/limitom alebo skončiť connection failureom, ktorý workflow nesprávne ignoroval.

H4/H5 testujú configuration transition. Variable precedence mohla vyrenderovať staré bytes alebo file change neviedol k handler executionu. Per-host vars, rendered checksum, notification event, process PID/start time a loaded config version tieto možnosti rozlíšia.

H6/H7 testujú observation path. Load balancer môže stále routovať old backend alebo verifier môže čítať stale cache/jediný host. LB member inventory, backend identity, direct per-host request a timestamps preto dopĺňajú controller recap. Hypotéza je prijatá iba vtedy, keď predpovie konkrétny rozdiel medzi týmito observation points.""",
)
replace_section(
    "ansible-architecture.md",
    "## 19. Evidence-preserving containment a recovery",
    """Atlas najprv zastaví ďalší batch a zachová inventory JSON, execution-environment manifest, run events, per-host results, rendered checksums a handler notifications. Z expected/resolved/attempted/converged manifestov vytvorí presný mixed-state inventory a unverified hosts odoberie z trafficu.

Recovery opraví prvý divergentný transition: cache/target contract, variable source, connection, handler alebo serving membership. Targeted rerun používa reviewed immutable host manifest a nesmie sa opierať o rovnaký stale dynamic query. Host sa vracia do trafficu až po process, endpoint a LB health verification.

Closure tvorí fleet-level business journey a complete second converge run nad fresh inventory. `changed=0` je prijaté iba pri complete host coverage, správnej loaded generation a nulovom residual recovery sete.""",
)
replace_section(
    "ansible-architecture.md",
    "## 20. Acceptance a forbidden paths",
    """Architecture acceptance viaže pinned execution environment a collections na complete target a runtime evidence. Expected a resolved host manifests sa musia zhodovať, per-host effective identity/variables musia byť auditovateľné a delegated API task musí read-backnúť target account/region. Serial batch má explicitný health gate a handler completion sa overuje cez process generation.

Forbidden fixtures zahŕňajú undersized inventory, wrong controller API identity, unsupported check-mode task, missing handler a omitted host. Každý musí skončiť `INCOMPLETE` alebo failure, nie success bez task attempts.

Po positive rollout-e nasleduje full-fleet second run a payment journey. Tým sa dokazuje convergence aj to, že green controller recap patrí správnej serving cohort-e.""",
)

# Inventory
replace_section(
    "inventory.md",
    "## 5. Worked failure: recyklovaná IP",
    """Static inventory stále mapoval `payments-app-b2` na `10.40.12.44`, hoci pôvodný production host bol odstránený a IP neskôr dostal test host v peered networke. Vypnuté host-key checking odstránilo posledný independent identity control, takže platný automation credential zasiahol nesprávny asset.

```text
stale logical mapping
+ recyklovaná IP
+ credential accepted na test hoste
+ bez host identity verification
→ production play vykoná správne tasks na nesprávnom objecte
```

Containment zastaví run a zachová inventory source, resolved hostvars, SSH handshake/host-key evidence a cloud audit. Cloud instance ID, account/region a host certificate sa porovnajú s expected manifestom; až potom sa odstráni stale entry a obnoví authoritative dynamic mapping.

Recovery auditne mutation test hosta a pridá forbidden fixture s rovnakou IP, ale odlišným immutable asset ID/host keyom. Play musí zlyhať pred prvou mutáciou.""",
)
replace_section(
    "inventory.md",
    "## 10. Source order a duplicate identities",
    """Viac inventory sources môže publikovať rovnaký `inventory_hostname`. Ansible ich zloží podľa load a precedence rules, ale výsledný host record môže spájať logical name z jedného source-u, `ansible_host` z druhého a environment/role z tretieho.

Gate preto porovná duplicate logical names s immutable instance IDs, connection addresses, environment, role a source ownerom. Odlišný instance ID alebo target environment je hard conflict; rovnaká hodnota z dvoch sources je stále ownership ambiguity, ktorú treba odstrániť.

Critical semantics sa nesmú spoliehať na alphabetic filename order. Resolved host record sa publikuje s provenance a forbidden fixture zámerne vytvorí konflikt, ktorý musí pre-run validation odmietnuť.""",
)
prepend_section(
    "inventory.md",
    "## 16. Constructed groups a missing metadata",
    """Constructed group rule je policy nad raw metadata. Missing field nesmie byť ticho interpretovaný ako production alebo iná privileged cohorta; unknown values patria do quarantine group a mutation run sa zastaví, kým source alebo asset owner metadata neopraví.""",
)
prepend_section(
    "inventory.md",
    "## 20. Worked incident: stale cache vynechala dva hosts",
    """Tento incident vznikol ešte pred prvou task invocation. Green results na desiatich hosts preto nehovoria nič o dvoch omitted assets. Recovery musí zachovať cache generation aj direct API result a viazať targeted rerun na exact replacement IDs.""",
)
replace_section(
    "inventory.md",
    "## 21. Competing hypotheses pri chýbajúcom hoste",
    """H1/H2 porovnávajú direct source API s cached inventory a určujú, či asset chýba už v authority response alebo iba v stale cache. H3 testuje raw metadata a filter logic; H4 porovná resolved inventory s `--list-hosts`, aby odhalil pattern alebo `--limit` exclusion.

H5 hľadá duplicate `inventory_hostname` a porovnáva immutable instance IDs. H6 číta group graph a quarantine/maintenance membership. H7 read-backne caller account/region a plugin target, pretože presný filter v nesprávnom account-e môže legitímne vrátiť nulu.

Každá hypotéza má iný first divergent transition. Až po jeho potvrdení sa refreshuje cache, opravuje metadata, pattern alebo source identity; blind rerun nad rovnakým inventory subjectom je forbidden.""",
)

# Modules, tasks, plays and playbooks
prepend_section(
    "modules-tasks-plays-playbooks.md",
    "## 1. Dominantný intent-to-per-host-transition lifecycle",
    """Lifecycle sa číta ako rozklad jedného rollout intentu na host-scoped state machines. Play vyberie target a policy, task vytvorí per-host invocation, module vráti structured result a handler/rescue mení ďalší flow. Fleet verdict vzniká až po agregácii complete per-host postconditions a runtime observation.""",
)
replace_section(
    "modules-tasks-plays-playbooks.md",
    "## 6. Play ako target a execution policy",
    """Play viaže host pattern na celý execution contract. Určuje, či sa zbierajú facts, akou connection a privilege identity sa tasks vykonajú, aká strategy/batch policy sa použije a ktoré variables, roles, pre/tasks, post/tasks a handlers tvoria content graph.

```yaml
- name: Roll out payments configuration
  hosts: payments_app:&production:!maintenance
  gather_facts: true
  become: true
  serial: 2
  max_fail_percentage: 0
  any_errors_fatal: true
  roles:
    - atlas.payments.runtime
```

`serial: 2` iba rozdelí target set. Readiness gate musí byť explicitný a failure thresholds sa interpretujú nad current batchom a resolved host countom. Broad `become: true` rozširuje privilege na celý play, preto sa pri mixed tasks preferuje užší block/task scope.

Review subject obsahuje resolved host manifest aj effective play policy. Rovnaký YAML s iným inventory alebo `--limit` nie je rovnaký rollout.""",
)
replace_section(
    "modules-tasks-plays-playbooks.md",
    "## 13. Delegation a shared API fan-out",
    """Delegated task sa stále instancuje pre každý inventory host. Dvanásť hosts preto môže vytvoriť dvanásť controller-side API calls, aj keď všetky menia jeden shared listener alebo deployment object.

Ak API podporuje host-scoped idempotent member operation, každý call používa immutable host ID a stable idempotency key. Pri shared manifest-e sa items najprv agregujú do jednej reviewed mutation. `throttle`, `serial` alebo samostatný orchestration play obmedzujú concurrency, ale nenahrádzajú server-side operation identity.

External controller je vhodný, keď shared object potrebuje vlastný reconciliation lifecycle. Evidence vždy oddeľuje inventory host, controller credential/account a remote object identity; `delegate_to: localhost` nie je distributed lock.""",
)
replace_section(
    "modules-tasks-plays-playbooks.md",
    "## 17. Competing hypotheses pri mixed runtime",
    """H1/H2 sledujú content eligibility: condition, dynamic include alebo tags mohli preskočiť task, prerequisite či handler definition. H3/H4 porovnávajú actual file mutation, `changed` result, notification a handler execution. H5 skúma partial state po failure/rescue.

H6 overuje exact verifier host manifest a endpoint, H7 porovnáva process command line/loaded path s destination file-om a H8 porovnáva expected a resolved inventory. Per-host event timeline spája tieto observations s jedným run ID.

Takto sa odlíši omitted host od false-changed, handler failure alebo stale observation. Aggregate process status bez per-host subjectu nedokáže žiadnu z hypotéz potvrdiť.""",
)
replace_section(
    "modules-tasks-plays-playbooks.md",
    "## 18. Evidence-preserving containment a recovery",
    """Ďalšie batches sa pozastavia a zachová sa target manifest, task path, vars fingerprints, per-host results, file checksums a notifications. Unverified hosts sa odstránia z trafficu a klasifikujú ako skipped, false-changed, handler-failed, rescued-partial alebo omitted.

Recovery je najmenšia operation, ktorá uzavrie konkrétny host transition: dokončenie prerequisite, obnova file-u, explicitný handler alebo oprava inventory. Host sa vracia do trafficu až po loaded version a LB health.

Full-fleet business journey a second complete converge run dokazujú, že targeted recovery nevytvorila alternate workflow a že všetky expected hosts dosiahli rovnaký successor subject.""",
)
replace_section(
    "modules-tasks-plays-playbooks.md",
    "## 19. Acceptance a forbidden paths",
    """Execution acceptance vyžaduje pinned module/collection identity, known task path, complete per-host results a pravdivý `changed` signal. Config mutation musí byť korelovaná s handler executionom a loaded process generation; rescued alebo ignored failure nesmie byť complete success.

Forbidden tests pokrývajú `--tags config` bez prerequisite, false `changed_when`, wrong delegated account, handler failure, rescue-as-pass a `run_once` migration bez external locku. Každý musí zlyhať pred fleet closure.

Po positive batch flow nasleduje second full run bez unintended mutation a business verifier cez serving path.""",
)

# Variables, facts and templates
replace_section(
    "variables-facts-templates.md",
    "## 16. Worked failure: stale extra var smeruje do staging DB",
    """Recovery job template ponechal `atlas_database_endpoint: db.stage.internal:5432` ako extra var. Extra var mala vyššiu precedence než production inventory, template bola syntakticky validná a process sa úspešne pripojil do staging databázy. Parser ani service health preto chybu neodhalili.

Containment odoberie affected hosts z trafficu a zachová job metadata, variable provenance, rendered files, process environment/command line a database audit. Security/data owner posúdi cross-environment access skôr, než sa logs alebo sessions odstránia.

Autoritatívna oprava odstráni stale override, definuje allowed source policy pre endpoint a pridá assertion `database_environment == prod-eu`. Host sa re-renderuje, handler reloadne process a runtime endpoint aj DB identity probe potvrdia production target. Forbidden fixture so staging extra-varom musí zlyhať pred file mutation.""",
)
replace_section(
    "variables-facts-templates.md",
    "## 20. Competing hypotheses pri wrong endpoint na jednom hoste",
    """H1/H3 porovnávajú inventory host/group provenance a duplicate membership. H2 číta controller job metadata a explicitné extra vars. H4 overuje fact timestamp a branch, ktorá z factu odvodila endpoint.

H5/H6 auditujú `hostvars` selection a lookup path/credential, pretože controller mohol načítať správny key z nesprávneho environment store-u. H7 porovná destination file s process command line a loaded runtime fields. H8 používa filesystem audit timeline na odhalenie druhého writera po run-e.

Každý dôkaz je host-scoped a časovo korelovaný. Až po potvrdení source-u sa opravuje precedence, cache, lookup alebo writer ownership; jednoduché re-renderovanie môže nesprávnu hodnotu iba zopakovať.""",
)
replace_section(
    "variables-facts-templates.md",
    "## 21. Recovery a acceptance",
    """Host zostáva mimo trafficu, kým sa nezachová a nevyhodnotí run/value/fact/template evidence a neurčí prvý nesprávny source alebo stale observation. Oprava mení autoritatívnu value, cache alebo lookup contract, potom vykoná deterministic render, parser validation a handler transition.

Loaded config endpoint musí potvrdiť release aj environment a fleet manifest musí ukázať complete coverage. Second no-change run dokazuje stabilitu template inputs a absenciu second writera. Acceptance zároveň vyžaduje, aby extra-var wrong endpoint a timestamp fixture skončili failureom alebo no-op podľa explicitného contractu.""",
)

# Handlers, loops and conditionals
prepend_section(
    "handlers-loops-conditionals.md",
    "## 1. Dominantný eligibility-to-runtime lifecycle",
    """Lifecycle je per-host a per-item state machine. Condition rozhoduje eligibility nad typed inputs, loop vytvára complete item inventory, každý item vracia vlastný mutation verdict a handler je až následný synchronization transition do loaded runtime-u. Failure v strede loopu preto môže zanechať partial artifacts bez handlera.""",
)
replace_section(
    "handlers-loops-conditionals.md",
    "## 20. Worked incident: duplicate deployment POST",
    """Prvý delegated POST vytvoril deployment record a server ho commitol, ale response sa stratila. Controller vyhodnotil timeout ako `not applied` a retry bez stabilnej idempotency identity vytvoril druhý record; dva rollout controllers začali spravovať rovnakú cohortu.

Containment zastaví oba controllers a zachová request IDs, audit events, body hash a cohort membership. Remote API sa queryuje podľa immutable run/cohort identity a owner vyberie authoritative record; duplicate sa cancelne až po kontrole, ktorý controller vykonal side effects.

Recovery pridá server-side idempotency key stabilný cez retries jednej logical operation a unknown-outcome lookup pred opakovaním. Acceptance simuluje lost response a musí skončiť presne jedným deployment recordom a jednou active cohort authority.""",
)
replace_section(
    "handlers-loops-conditionals.md",
    "## 21. Competing hypotheses pri files-new/process-old",
    """H1–H3 skúmajú eligibility a item completeness: condition mohla skipnúť items, input type mohol byť chybný alebo loop skončil partial failureom. Per-item results a expected item manifest určia, ktoré artifacts vznikli.

H4/H5 porovnávajú actual mutation, `changed` signal, notification topic a resolved handler definition. H6/H7 čítajú host task timeline a synchronization point, aby odlíšili host failure pred handler phase od príliš skorého flushu.

H8 porovná active symlink, open files a process-loaded config; H9 overuje direct process observation a cache timestamps. Recovery sa vyberá až po zistení, či je problém v artifact set-e, notification alebo observation path-e.""",
)
replace_section(
    "handlers-loops-conditionals.md",
    "### „force_handlers dokončí partial rollout“",
    """`force_handlers` môže vykonať queued handler aj po neskoršom task failure, ale nepreukazuje, že celý artifact set je complete a valid. Reload partial directory môže incident zhoršiť. Handler je povolený až po complete-set validation; inak sa host izoluje a vykoná restore alebo reviewed roll-forward.""",
)

# Roles and collections
prepend_section(
    "roles-and-collections.md",
    "## 1. Dominantný capability-to-runtime lifecycle",
    """Role/collection lifecycle spája source, distribution artifact, execution environment a expanded host behavior. FQCN a semantic version sú locators; exact implementation tvoria artifact digest, transitive dependencies a image/plugin paths. Runtime verdict sa preto viaže na celý resolved dependency graph.""",
)
replace_section(
    "roles-and-collections.md",
    "## 2. Kedy vzniká role boundary",
    """Role boundary má zmysel, keď capability má jasný purpose a non-goals, verejné inputs/defaults a vlastné tasks, templates a handlers. Contract musí pomenovať privilege, package a network dependencies, podporované platformy, idempotency/recovery behavior a ownera s release lifecycle-om.

Dvojriadkový task file nemusí byť role, ak nemá samostatnú capability ani consumer contract. Jedna mega-role pre celý server naopak mieša odlišné ownership, failure a release domains. Boundary sa vyberá podľa coherent behavioru a support lifecycle-u, nie podľa directory template-u.

Reusable role má viac consumerov alebo opakovateľné použitie a jej public topics, facts a generated artifacts sa verziujú. Upgrade fixture musí preukázať, že existing host prejde na successor bez hidden dependency alebo perpetual change.""",
)
replace_section(
    "roles-and-collections.md",
    "## 15. Supply-chain review",
    """External collection je executable supply-chain artifact. Review overuje publisher a source repository, release/maintenance históriu, artifact provenance/integrity a direct aj transitive dependencies. Osobitne sa kontrolujú controller-side action, lookup, inventory a callback plugins, pretože pracujú s credentials, filesystemom a networkom ešte pred remote module executionom.

Shell/command usage, logging/secret behavior, privilege/network requirements a supported `ansible-core`/Python/system matrix určujú blast radius a compatibility. Download count alebo populárny namespace nie sú trust verdict.

Adoption gate pinne artifact a execution-environment digest, generuje SBOM/provenance a vykoná forbidden egress/secret fixture. Upgrade sa posudzuje ako explicitná dependency change s consumer integration a second-converge testom.""",
)
replace_section(
    "roles-and-collections.md",
    "## 17. Compatibility policy",
    """Breaking change nie je iba odstránenie variable. Rename/type/default zmena, nový required privilege, handler topic rename, generated-config format change, package replacement, published fact/result schema alebo supported runtime matrix môžu zmeniť consumer behavior bez playbook source diffu.

Semantic version je owner claim. Evidence poskytuje consumer upgrade fixture nad existing hostom, handler integration a loaded-runtime test. Compatibility policy definuje supported predecessor versions, deprecation window a migration aliasy/topics.

Consumer inventory je potrebný na bezpečné retirement. Bez neho nemožno vedieť, či old topic alebo result field ešte používa production repository.""",
)
replace_section(
    "roles-and-collections.md",
    "## 20. Competing hypotheses pri local/controller rozdiele",
    """H1 porovná collection artifact/version/digest; H2 execution image SBOM a Python/system dependencies. H3 číta FQCN, collection/search path a plugin resolution, pretože rovnaké meno môže resolve-núť iný content.

H4 porovná static/dynamic invocation a handler visibility. H5/H7 čítajú role source checksums a effective values/target inventory. H6 skúma controller cache path a timestamps.

Dôkazy sa viažu na rovnaký run subject. Obnova lokálneho `requirements.yml` bez kontroly controller image-u nemusí zmeniť effective bytes a preto nie je recovery closure.""",
)
replace_section(
    "roles-and-collections.md",
    "## 21. Evidence-preserving containment a recovery",
    """Rollout sa pozastaví a zachovajú sa local aj controller image/collection manifests, task/handler graph a affected host evidence. Exact breaking change sa identifikuje na artifact, dependency, topic alebo result-schema úrovni.

Containment môže pinne obnoviť known-good execution image alebo publikovať compatible fix s aliasom. Canary musí preukázať file mutation, handler execution, loaded version a second converge. Až potom sa aktualizuje consumer inventory a deprecation/retirement policy.""",
)

# Vault
prepend_section(
    "vault.md",
    "## 1. Dominantný secret-to-revocation lifecycle",
    """Vault lifecycle nezačína ciphertextom, ale logical credentialom, ownerom a consumer inventory. Encryption chráni repository state; po decryption vzniká nový plaintext exposure graph a po publication musí nasledovať process reload, target-side revocation a forbidden-old-credential test.""",
)
replace_section(
    "vault.md",
    "## 3. Čo Vault chráni a čo nechráni",
    """Vault šifruje variable alebo file content at rest v repository a automation artifacts. Tým obmedzuje náhodné čítanie source-u bez Vault password materialu. Nechráni však plaintext po autorizovanom dešifrovaní.

Controller memory, temporary files, rendered target files, module arguments, registered results, validator stderr, callbacks a debug logs sú samostatné exposure boundaries. Malicious collection/plugin s decrypt accessom môže value exfiltrovať a credential uniknutý pred encryption zostáva kompromitovaný.

Vault zároveň nevykonáva target credential lifecycle. Rekey mení wrapper key, nie database password alebo API token. Old credential bez provider-side revocation môže fungovať aj po perfektnom re-encryption. Dôkaz preto oddeľuje repository confidentiality, runtime plaintext confidentiality a revocation completion.""",
)
replace_section(
    "vault.md",
    "## 5. Vault ID",
    """Vault ID v headeri, napríklad `prod-database`, je routing label, ktorý vyberá password source pri decryption. Nie je samostatnou authorization policy, logical secret identity ani credential epoch.

Vault domains sa navrhujú podľa environmentu, ownera, consumer scope-u, rotation lifecycle-u, blast radiusu a decryption authorization. Jeden password pre dev a prod znamená, že compromise jednej boundary umožní decrypt druhej.

Execution subject preto zachováva vault ID aj workload identity a logical secret/epoch. Forbidden test musí potvrdiť, že non-production controller alebo untrusted source nedokáže použiť production password client.""",
)

# Ansible idempotency
prepend_section(
    "ansible-idempotency.md",
    "## 1. Dominantný subject-to-convergence lifecycle",
    """Convergence sa posudzuje nad immutable run subjectom a complete target/item inventory. Observation, mutation result, handler/runtime transition a external side effects musia patriť tým istým identities; až potom má second-run `changed=0` význam.""",
)
replace_section(
    "ansible-idempotency.md",
    "## 2. Idempotencia, convergence, reproducibility a correctness",
    """Pre jednu operation formálne platí `f(f(S)) = f(S)`: po dosiahnutí výsledku ďalšie opakovanie nevytvorí nový side effect. Configuration management však potrebuje aj convergence, teda schopnosť priblížiť partial alebo drifted system k desired state-u.

Reproducibility znamená, že rovnaký explicitný source, execution environment, inventory, variables, secret epoch a dependency graph vedú k porovnateľnému behavioru. Correctness je ešte vyššia vrstva: desired state musí byť správny pre business a security intent.

Production host môže stabilne používať staging DB. Druhý run bude `changed=0`, takže task je technicky idempotentný a converged, ale výsledok je business nesprávny. Acceptance preto kombinuje no-change signal s target identity a runtime/business oracle-om.""",
)
replace_section(
    "ansible-idempotency.md",
    "## 5. State-aware module contract",
    """State-aware module musí explicitne pozorovať attributes, ktoré tvrdí, že vlastní, porovnať ich s requested state-om a mutovať iba rozdiel. Contract definuje význam `changed`, check-mode support, normalization a vedľajšie side effects.

```yaml
- name: Ensure Atlas Payments service is enabled and running
  ansible.builtin.service:
    name: atlas-payments
    enabled: true
    state: started
```

Pre konkrétnu module/version/platform kombináciu treba poznať aj failure a unknown-outcome semantics. Service `started` nemusí overovať loaded config alebo business readiness. Custom `changed_when` nesmie prepisovať actual mutation iba kvôli potlačeniu noise.

Module name preto nie je idempotency proof. First/second run sa dopĺňa independent state a runtime observationom a forbidden drift fixture-om.""",
)
replace_section(
    "ansible-idempotency.md",
    "## 14. Partial failure a resumability",
    """Partial run môže zanechať nový package, nový config file a starý process alebo remote API record bez local response. Nasledujúci run nesmie predpokladať all-applied ani all-rolled-back; musí znovu pozorovať každý owned state component a operation identity.

Resumability potrebuje stable artifact/remote IDs, pre-validation, per-step postconditions, explicitný partial/unknown verdict, recoverable handler a bounded cleanup. Marker alebo recap status nie sú sufficient ledgerom.

Acceptance reprodukuje failure medzi file mutation a handlerom a overí, že ďalší run bezpečne dokončí transition bez duplicate external side effectu.""",
)
replace_section(
    "ansible-idempotency.md",
    "## 19. Competing hypotheses pri perpetual restartoch",
    """H1–H4 porovnávajú exact before/after bytes a metadata: timestamp, random, unstable ordering, mutable lookup alebo owner/mode/ACL oscillation. H5 číta module/version normalization a current-state output. H6/H7 používajú filesystem audit na odhalenie application alebo druhého automation writera.

H8 porovná `changed` result s actual mutation. Task môže reportovať change bez byte/state rozdielu alebo naopak zmenu zatajiť. Každá hypotéza sa testuje na canary s rovnakým immutable subjectom a zachovaným diffom.

Recovery odstráni nondeterministic input alebo ownership conflict a potom vyžaduje runtime correctness aj second no-change run; potlačenie handlera nie je oprava.""",
)
replace_section(
    "ansible-idempotency.md",
    "## 21. Acceptance a forbidden paths",
    """Acceptance vyžaduje complete immutable run subject, fresh current-state observation, truthful results, deterministic artifacts a stable external idempotency identity. Unknown remote outcome sa queryuje pred retry a partial run musí byť resumable.

Forbidden fixtures pokrývajú marker pred completion, mutating task s `changed_when: false`, timestamp template, duplicate POST retry, omitted host a dvoch writerov s opposing values. Každý musí odhaliť neúplnosť alebo konflikt.

Second complete run bez unintended changes je prijatý iba pri complete target coverage a správnom loaded/business outcome-e.""",
)

# Ansible practical walkthrough
prepend_section(
    "ansible-practical-walkthrough.md",
    "## 11. Role tasks: complete rolling host transition",
    """Role task graph musí uzavrieť celý host transition: drain, package/config mutation, complete validation, handler, loaded-state check a návrat do trafficu. Jedna správna template task nie je rolling rollout; nasledujúci blok sa preto číta ako transaction-like workflow s explicitnými partial outcomes.""",
)
replace_section(
    "ansible-practical-walkthrough.md",
    "## 28. Diagnostický walkthrough pri mixed fleet",
    """Diagnostika najprv porovná expected, resolved a attempted host manifests. Tým testuje H1–H3: omitted inventory host, pattern/limit exclusion alebo connection failure. Per-host variable fingerprints a rendered checksums testujú H4, teda odlišný effective config.

Callback events, notification/handler result a systemd process start time testujú H5/H6: file mohol byť nový, ale handler neprebehol alebo host skončil partial. Load-balancer member inventory a backend identity testujú H7, pretože healthy host nemusí byť serving cohortou.

Direct per-host request a timestamps testujú H8 a odlišujú stale aggregated verifier od reálneho loaded state-u. Recovery sa viaže na prvý divergentný transition a targeted manifest; full-fleet second converge a business journey potom uzatvoria mixed-state incident.""",
)

# Terraform vs Ansible
prepend_section(
    "terraform-vs-ansible.md",
    "## 1. Dominantný capability-to-combined-outcome lifecycle",
    """Combined lifecycle oddeľuje resource provisioning, readiness a host convergence. Handoff medzi nástrojmi je versionovaný capability contract; ani Terraform output, ani Ansible inventory nesmú implicitne prenášať interný state layout alebo shared writer authority.""",
)
replace_section(
    "terraform-vs-ansible.md",
    "## 2. Dva odlišné state stroje",
    """Terraform skladá configuration, provider target, persistent address-to-remote bindings a refresh observations do dependency graphu a saved planu. Jeho dominantný problém je resource lifecycle: create, update, replacement, destruction, state commit a binding recovery.

Ansible pri každom run-e skladá playbook/execution environment, resolved inventory, variables/facts a ordered per-host tasks. Jeho dominantný problém je fleet configuration a orchestration: eligibility, module results, handlers, partial batches a loaded-runtime convergence.

Nástroje sa môžu dotýkať rovnakého API, ale nesmú implicitne vlastniť rovnaký mutable attribute. Handoff musí pomenovať producer generation, stable object/host identities, readiness a consumer schema. Second Terraform plan aj second Ansible run potom overia, že boundary neosciluje.""",
)
replace_section(
    "terraform-vs-ansible.md",
    "## 10. Readiness ako samostatný state",
    """Terraform apply success môže potvrdiť existenciu VM a state binding, ale nie cloud-init completion, stabilný host certificate, management route, SSH identity, required Python/runtime ani bezpečnosť konfigurácie. Tieto conditions vznikajú po resource creation a často ich vlastní bootstrap alebo platform controller.

```text
resource created
→ boot/cloud-init complete
→ management identity published
→ route/firewall verified
→ host-key/certificate verified
→ bootstrap capability probe
→ contract status ready
```

Readiness je versionovaný state v host contracte s timestampom/generation a bounded observationom. Fixed sleep iba odhaduje čas; nepreukazuje condition a pri failure nezachová dôvod. Ansible inventory prijíma iba hosts z ready generation a forbidden test odmietne exists-but-not-ready VM.""",
)
prepend_section(
    "terraform-vs-ansible.md",
    "## 19. Worked incident: image a runtime package dual ownership",
    """Tento incident ukazuje attribute-level dual ownership. Immutable image a runtime package manager môžu byť oba idempotentné, ale každý deklaruje inú package version; fleet potom prestane zodpovedať image identity a replacement znovu vráti staršiu verziu.""",
)
replace_section(
    "terraform-vs-ansible.md",
    "## 21. Competing hypotheses pri Terraform green / Ansible unreachable",
    """H1/H2/H8 porovnávajú VM lifecycle, cloud-init/bootstrap logs a readiness assertion. H3/H9 čítajú host contract generation, management address, environment a immutable instance ID. H4 porovná inventory cache s producer contractom.

H5 testuje route/firewall z controller networku, H6 host key/certificate a H7 connection/become credential. H10 oddeľuje controller-wide network incident od host-specific failure pomocou alternate known-good targetu.

Terraform green je iba premise, že jeho state/remote transition skončil podľa vlastného oracle-u. Recovery sa vyberá podľa first divergent boundary; VM replacement je zakázaný, kým evidence nepotvrdí resource lifecycle defect.""",
)
replace_section(
    "terraform-vs-ansible.md",
    "## 23. Acceptance a forbidden paths",
    """Combined acceptance vyžaduje jedného authoritative writera pre každý mutable attribute, no shared implicit state layout a explicitný readiness handoff. Host contract musí byť schema-validný, fresh a obsahovať unique immutable IDs; Ansible resolved inventory sa s ním zhoduje.

Forbidden tests pokrývajú second writer security-group mutation, consumer závislý od Terraform address layoutu, exists-but-not-ready host a package version spravovanú image aj Ansible role-om. Starému writerovi sa po handoffe revokuje permission a test potvrdí odmietnutie.

Closure zahŕňa Terraform second no-op plan, Ansible second no-change run a combined business transaction cez current serving cohort.""",
)

print("Ansible explanation-depth pass applied.")
