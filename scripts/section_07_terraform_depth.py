from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = "docs/07-infrastructure-as-code-and-configuration-management"


def path(name: str) -> Path:
    return ROOT / BASE / name


def read(name: str) -> str:
    return path(name).read_text(encoding="utf-8")


def write(name: str, text: str) -> None:
    path(name).write_text(text, encoding="utf-8", newline="\n")


def heading_level(heading: str) -> int:
    match = re.match(r"^(#+) ", heading)
    if not match:
        raise RuntimeError(f"Invalid heading: {heading}")
    return len(match.group(1))


def section_span(text: str, heading: str) -> tuple[int, int]:
    marker = heading + "\n"
    start = text.find(marker)
    if start < 0:
        raise RuntimeError(f"Heading not found: {heading}")
    body_start = start + len(marker)
    level = heading_level(heading)
    pos = body_start
    for line in text[body_start:].splitlines(keepends=True):
        if line.startswith("#"):
            m = re.match(r"^(#+) ", line)
            if m and len(m.group(1)) <= level:
                return body_start, pos
        pos += len(line)
    return body_start, len(text)


def replace_section(name: str, heading: str, body: str) -> None:
    text = read(name)
    start, end = section_span(text, heading)
    normalized = "\n" + body.strip() + "\n\n"
    if text[start:end] == normalized:
        return
    write(name, text[:start] + normalized + text[end:])


def prepend_section(name: str, heading: str, prose: str) -> None:
    text = read(name)
    start, _ = section_span(text, heading)
    prose = prose.strip()
    if prose in text[start:start + len(prose) + 20]:
        return
    write(name, text[:start] + "\n" + prose + "\n\n" + text[start:].lstrip("\n"))


# Infrastructure as Code principles
prepend_section(
    "infrastructure-as-code-principles.md",
    "## 1. Dominantný intent-to-outcome lifecycle",
    """Lifecycle je kauzálny reťazec od business intentu po vzdialený a business outcome. Každý prechod má vlastný subject a dôkaz: source revision nie je resolved input, saved plan nie je remote mutation a provider success nie je state commit. Diagram preto slúži ako kontrolný model pre plánovanie, incident aj recovery, nie ako zoznam fáz, ktoré možno uzavrieť jedným zeleným pipeline statusom.""",
)
replace_section(
    "infrastructure-as-code-principles.md",
    "## 9. State boundary je zároveň blast-radius boundary",
    """State boundary určuje, ktoré remote bindings sa plánujú, zamykajú, zapisujú a obnovujú ako jedna change-control jednotka. Všetky resources v jednom state-e zdieľajú writer queue a lock, apply identity, dependency graph, saved-plan freshness, backup/restore históriu a incidentný blast radius. Zlyhanie backend write-u alebo chybná provider identity preto môže naraz ovplyvniť celý tento subject.

Module boundary je odlišná: organizuje reusable code a interface, ale jeho resources sa stále rozvinú do state-u caller root module-u. Samostatný state vzniká až samostatným root module-om, backend keyom, identity/policy a recovery lifecycle-om.

Atlas oddeľuje network, shared data platform a application runtime vtedy, keď majú rozdielne ownership, security domain, cadence alebo recovery objective. Príliš veľký state vyžaduje široké permissions, predlžuje lock a zväčšuje recovery unit. Príliš malé states vytvárajú implicitné cross-state dependencies a stale outputs. Boundary je teda architecture decision nad couplingom a failure domainom, nie stylistické rozdelenie adresárov.""",
)
replace_section(
    "infrastructure-as-code-principles.md",
    "## 10. Worked incident `IAC-PAY-75`",
    """Atlas pipeline mala meniť `prod-eu`, ale partial backend configuration zvolila `payments/prod-eu/platform-v2.tfstate` namiesto autoritatívneho `payments/prod-eu/platform.tfstate`. Nový key obsahoval prázdny state a default provider zdedil region `eu-west-1`, hoci intended target bol `eu-central-1`.

```text
správny source revision
+ nesprávny backend key
+ validná production identity
+ nesprávny default region
→ create graph nad prázdnym binding modelom
→ druhá VPC vznikne v eu-west-1
→ backend write zlyhá po remote create
→ job skončí failed bez state bindingu
```

HCL validation dokazovala iba syntaktický a schema contract. Platné credentials dokazovali, že caller smel mutovať effective account, nie že išlo o intended target. Absencia destroy actions nehovorila nič o duplicate create a úspešný cloud request neuzavrel state transition. Finálny failed job bol preto compatible s remote mutation, ktorá už prebehla.

Root cause bol chybný IaC subject: backend, region a predecessor state sa nezhodovali s approved intentom. Recovery musela najprv zastaviť writers, zachovať request IDs a state evidence, inventarizovať obe VPC a až potom rozhodnúť o importe, odstránení alebo kompenzácii.""",
)
replace_section(
    "infrastructure-as-code-principles.md",
    "## 12. Authoritative recovery",
    """Recovery nezačína ďalším apply. Najprv sa zmrazia všetci writers pre oba možné backend/state subjects a zachová sa source revision, saved plan, provider logs, request IDs, caller identity a recovery state snapshot. Read-only observations potom potvrdia backend key, lineage/serial, account/region a remote inventory.

Ak remote objekt vznikol a intended configuration ho má vlastniť, vytvorí sa explicitný binding recovery cez import alebo obnovenie správneho successor snapshotu. Ak vznikol v nesprávnom targete, owner rozhodne o bezpečnom cleanup-e až po kontrole dát, dependencies a trafficu. Ručná state surgery bez remote a ownership inventory je zakázaná, pretože môže iba presunúť neznalosť do ďalšieho snapshotu.

Po oprave sa vytvorí nový plan nad autoritatívnym backendom a exact provider targetom. Acceptance vyžaduje očakávaný remote object, správny state binding, runtime capability, forbidden duplicate/wrong-region path a druhý no-op plan. Recovery je uzavretá až vtedy, keď nová operation prežije nový state serial bez ad-hoc patchu.""",
)
replace_section(
    "infrastructure-as-code-principles.md",
    "### „Plan nemá destroy, takže je bezpečný“",
    """Absencia destroy action eliminuje iba jednu triedu mutation. Create môže vytvoriť duplicate databázu, verejný endpoint alebo objekt v nesprávnom account-e; update môže rozšíriť IAM alebo network exposure. Risk review preto hodnotí exact addresses, target identity, replacement paths a attribute-level effect, nie iba summary counter.""",
)
replace_section(
    "infrastructure-as-code-principles.md",
    "### „Apply failed, teda sa nič nezmenilo“",
    """Terraform apply nie je jedna ACID transakcia. Provider request mohol byť prijatý, remote objekt mohol vzniknúť a až state commit alebo runtime verification mohli zlyhať. Failed status preto spúšťa reconciliation cez request IDs, remote inventory a state serial; slepý retry je forbidden path.""",
)

# Providers, resources and data sources
replace_section(
    "terraform-providers-resources-data-sources.md",
    "## 1. Dominantný provider-to-object lifecycle",
    """Provider lifecycle prepája tri identity domains: executable dependency, effective API target a Terraform management address. Provider requirement vyberá plugin family, dependency lock stabilizuje konkrétnu package selection a provider configuration určuje endpoint, account, region a credentials. Až potom resource alebo data-source address vstupuje do graphu.

```text
provider source a version constraint
→ selected package a checksums
→ provider configuration a alias
→ workload identity, account a region
→ resource alebo data-source address
→ plan-time read alebo CRUD decision
→ remote API request a response
→ remote object identity
→ state binding alebo read-only value
→ downstream dependency a runtime verification
```

Resource address je Terraform ownership identity; remote ID je platform identity a state binding ich spája. Data source remote lifecycle nevlastní, ale jeho resolved value môže zmeniť graph alebo release. Syntakticky platná HCL preto môže zasiahnuť nesprávny target alebo vybrať inú immutable dependency bez source diffu.""",
)
replace_section(
    "terraform-providers-resources-data-sources.md",
    "## 12. Worked incident: alias sa nepreniesol",
    """Atlas chcel replica bucket v `eu-west-1`. Root configuration poznala `aws.replica`, ale child module nedeklaroval `configuration_aliases` a caller neposlal explicitný mapping. Child resource preto zdedil default provider a validná workload identity vytvorila bucket v `eu-central-1`.

```text
root pozná aws.replica
→ child resource dostane default aws
→ API request uspeje v primary regione
→ state binding je technicky konzistentný
→ replication capability je business nesprávna
```

Containment zastaví ďalšiu replication promotion a zachová plan, provider mapping a audit events. Remote inventory musí identifikovať oba buckets podľa accountu, regionu, ARN a data state-u; názov alebo tag nestačí. Až potom sa pridá explicitný alias contract a zvolí copy, import alebo recreate podľa obsahu a consumers.

Recovery sa uzatvára správnym provider mappingom v module graph-e, presným state bindingom, replication journey testom a forbidden fixture, ktorá zámerne vynechá alias a musí zlyhať pred mutation. Nesprávny bucket sa odstraňuje až po potvrdení, že nie je jediným nositeľom dát alebo active consumer dependency.""",
)
replace_section(
    "terraform-providers-resources-data-sources.md",
    "### „Alias je iba meno“",
    """Alias vyberá konkrétnu provider configuration a tým endpoint, account, region aj credential chain. Zmena alebo chýbajúci mapping môže vytvoriť správny resource type v nesprávnom targete. Provider relationship sa preto read-backuje cez resolved graph a testuje forbidden mappingom.""",
)
replace_section(
    "terraform-providers-resources-data-sources.md",
    "### „Data source nič nemení, takže je bez rizika“",
    """Data source priamo nevlastní remote lifecycle, ale jeho value môže vybrať image, subnet, policy alebo počet resource instances. Mutable query teda môže bez source diffu zmeniť plan a vyvolať replacement. Release-critical values sa pinujú ako immutable inputs a evidujú v resolved manifest-e.""",
)
replace_section(
    "terraform-providers-resources-data-sources.md",
    "### „Successful API response znamená správny objekt“",
    """API success dokazuje, že effective caller mohol vykonať operation v effective targete. Nehovorí, či account, region, remote ID alebo attribute set zodpovedali approved subjectu. Verdict dopĺňa target read-back, state binding a runtime/business test.""",
)

# Variables, locals and outputs
replace_section(
    "variables-locals-outputs.md",
    "## 4. Required values a bezpečné defaults",
    """Variable bez `default` vyžaduje explicitný caller intent. To je správny contract pre hodnoty, ktoré určujú production capacity, exposure, data retention alebo management identity.

```hcl
variable "replicas" {
  description = "Desired production service capacity."
  type        = number

  validation {
    condition     = var.replicas >= 2 && var.replicas <= 30
    error_message = "replicas must be between 2 and 30."
  }
}
```

Default je bezpečný iba vtedy, keď má rovnaký význam pre všetkých podporovaných callerov a jeho použitie neoslabuje security, availability ani compliance. Nesmie neočakávane meniť resource identity a musí byť pokrytý contract testom. Zmena defaultu je interface change s vlastnou compatibility policy, pretože caller bez source diffu môže dostať nový effective behavior.

Development convenience, napríklad `replicas = 1`, preto nepatrí do shared production module-u. Ak caller vynechá risk-significant hodnotu, plan má zlyhať namiesto tichého doplnenia lacného alebo menej bezpečného variantu.""",
)
replace_section(
    "variables-locals-outputs.md",
    "## 10. Sensitive nie je encryption ani revocation",
    """`sensitive = true` je presentation control v Terraform value propagation. Obmedzí bežné CLI zobrazenie, ale secret môže zostať v state-e alebo saved plane, provider ho môže zalogovať a oprávnený caller ho môže explicitne exportovať. Nechráni job memory, filesystem, artifacts ani backend recovery copies.

```hcl
variable "bootstrap_token" {
  type      = string
  sensitive = true
}
```

Flag tiež neurčuje lifetime a po exposure nevykoná provider-side revocation. Secret material preto vytvára citlivú boundary naprieč backendom, planom, logs a runnerom. Preferovaný interface prenáša secret-manager reference a workload získava krátkodobú hodnotu cez vlastnú identity.

```hcl
variable "secret_ref" {
  type        = string
  description = "Runtime secret-manager reference, not secret material."
}
```

Ak Terraform musí secret spravovať, lifecycle zahŕňa target revocation, consumer reload a old-credential forbidden test; redaction v CLI nie je closure.""",
)
replace_section(
    "variables-locals-outputs.md",
    "## 11. Locals ako normalizácia, nie druhý input systém",
    """Locals transformujú už resolved inputs do canonical interného modelu. Sú vhodné na stabilné naming, opakované expressions, normalizáciu collections, derived tags a dočasný compatibility adapter medzi versionovanými input shapes.

```hcl
locals {
  canonical_name = "atlas-payments-${var.environment}"
  common_tags = {
    Application = "payments"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
  normalized_subnets = {
    for key, subnet in var.subnets : key => {
      name = "${local.canonical_name}-${key}"
      cidr = subnet.cidr
      zone = subnet.zone
    }
  }
}
```

Local nemá vytvárať skrytý druhý policy alebo input systém. Keď nested conditionals menia počet, keys alebo identity resources, ide o graph decision, ktorý potrebuje explicitný contract test a resolved-key evidence. Ak taká logika rastie, vhodnejšia je menšia capability boundary alebo verejný typed input než ďalšia neviditeľná transformácia.""",
)
prepend_section(
    "variables-locals-outputs.md",
    "## 12. Stable keys sú management identity",
    """`for_each` key nie je len label v source. Stáva sa súčasťou resource address-y v state-e, a preto jeho zmena môže znamenať ownership migration alebo replacement. Pred nasledujúcim HCL príkladom treba najprv rozhodnúť, ktorá business identity má prežiť display-name a ordering changes.""",
)
replace_section(
    "variables-locals-outputs.md",
    "## 16. Interface versioning",
    """Module interface sa verzuje podľa effective behavioru a state identity, nie iba podľa syntaktickej kompatibility. Nový optional input s naozaj bezpečným defaultom, nový output alebo interná local transformácia bez zmeny external semantics môžu byť backward-compatible. Aj pri nich sa však testuje existing-state upgrade.

Premenovanie inputu/outputu, zmena type constraintu, default alebo `null` semantics, collection keys či sensitive behavioru je breaking alebo risk-significant transition. Rovnako nebezpečná je zmena immutable digest inputu na mutable tag, pretože mení release identity bez caller source diffu.

Version label je iba deklarácia autora. Dôkaz compatibility poskytuje consumer upgrade plan nad reprezentatívnym existing state-om, forbidden fixtures a druhý no-op plan. Support contract musí povedať, z ktorých verzií je upgrade podporovaný a aká migration je potrebná.""",
)
prepend_section(
    "variables-locals-outputs.md",
    "## 20. Acceptance a forbidden paths",
    """Acceptance spája interface contract s graph a secret behaviorom. Nestačí, že happy-path plan prejde; musí sa preukázať odmietnutie chýbajúceho production intentu, mutable release identity a nebezpečného secret exportu. Druhý plan potom overí stabilitu effective inputs a management keys.""",
)

# Expressions and dependency graph
replace_section(
    "expressions-and-dependency-graph.md",
    "## 5. Unknown values a hranica plan-time rozhodovania",
    """Unknown value znamená, že Terraform pozná type a dependency edge, ale konkrétnu hodnotu poskytne provider až počas apply. Taká hodnota môže bezpečne napĺňať argument existujúceho graph vertexu, napríklad DNS target vytvoreného load balancera.

Graph shape však musí byť známy pred remote mutation. `count`, `for_each` keys, module instance keys, provider configuration selection a resource addresses určujú, aké vertices Terraform plánuje a ktoré state identities vzniknú. Apply-time unknown value preto nesmie byť zdrojom ich identity.

```hcl
resource "example_monitor" "instance" {
  for_each = toset(aws_service.payments.generated_instance_names)
  name     = each.key
}
```

Ak names vzniknú až po create, Terraform nevie zostaviť complete inventory ani addresses monitorov. Riešením sú desired stable keys z configuration alebo samostatný discovery/controller lifecycle. Placeholder alebo `-target` graph deterministickým neurobí.""",
)
replace_section(
    "expressions-and-dependency-graph.md",
    "## 14. Prečo module-wide dependency znižuje plan precision",
    """`depends_on = [module.platform]` vytvorí edge na celý expanded upstream module, hoci consumer často potrebuje iba jeden subnet output alebo jednu readiness capability. Terraform potom musí konzervatívne čakať na všetky upstream resources, čo znižuje paralelizáciu a môže odložiť data-source reads.

Široký edge zároveň vytvorí viac unknown values a zväčší apparent plan blast radius. Reviewer vidí uncertainty aj pri resources, ktoré s reálnym contractom nesúvisia, a konkrétna chýbajúca dependency zostane skrytá.

Preferovaný model prenáša narrow output, napríklad `subnet_ids = module.platform.private_subnet_ids`, čím vznikne value aj dependency contract. Ak existuje behaviorálna dependency bez value-u, musí pomenovať konkrétny completion condition, failure bez edge-u a independent verifier; module-wide edge je posledná, nie prvá možnosť.""",
)
replace_section(
    "expressions-and-dependency-graph.md",
    "## 17. Cycles ako architecture signal",
    """Cycle `A → B → C → A` znamená, že graph nemá počiatočný vertex s dostatočne známymi inputs. Typicky provider configuration závisí od resource spravovaného tým istým providerom, dve security objects potrebujú navzájom computed IDs, module output sa vracia do vlastného lifecycle-u alebo locals vytvoria kruhový value chain.

Cycle sa neopravuje ďalším `depends_on`; ten pridáva edge a problém môže iba spraviť explicitnejším. Architecture musí oddeliť identity creation od attachments, rozdeliť bootstrap a steady-state lifecycle alebo zmeniť ownership/state boundary.

Acceptance po refaktore overí, že prvá fáza publikuje stabilný narrow contract a druhá ho spotrebuje bez reverse dependency. Druhý no-op plan dokazuje, že rozdelenie nevytvorilo oscilujúce transitions.""",
)
prepend_section(
    "expressions-and-dependency-graph.md",
    "## 21. Acceptance a forbidden paths",
    """Graph acceptance overuje stable identity aj dependency precision. Positive fixture vytvorí očakávané keys a order, forbidden fixture vloží alebo premenuje list item a musí odhaliť neplánovaný address transition. Broad module dependency a cycle sa nesmú maskovať `-target` alebo nízkou parallelism.""",
)

# Terraform state
replace_section(
    "terraform-state.md",
    "## 3. Desired, known a actual state",
    """Desired state je HCL, resolved variables a selected module/provider behavior. Known state je snapshot resource addresses, provider associations, remote IDs a posledných známych attributes. Actual state sú objekty a hodnoty, ktoré provider API práve pozoruje v konkrétnom account-e a regione.

```text
configuration C71
+ state lineage L-prod / serial 208
+ provider reads v account-e 7711
→ saved plan P209
```

Create action môže znamenať, že objekt naozaj neexistuje, ale aj chýbajúci binding, wrong backend/workspace, zmenený key/address, iného ownera, wrong target/permission alebo predchádzajúci remote success bez state commitu. Jeden symbol `+` tieto mechanizmy nerozlišuje.

Diagnostika preto spája state address a provider association s remote inventory a audit trailom. Plan je verdict nad konkrétnym desired/known/observed subjectom, nie globálne tvrdenie o cloude.""",
)
replace_section(
    "terraform-state.md",
    "## 5. Refresh mení observation model, nie desired intent",
    """Refresh použije state remote ID a effective provider target na Read operáciu a aktualizuje Terraform knowledge o remote attributes. Môže odhaliť manual firewall change, deletion, server-side normalization, attribute spravovaný iným controllerom, eventual-consistency stav alebo wrong-account `not found`.

Refresh tým nevytvára nový business intent. Až následný decision určí, či sa remote rozdiel revertuje, adoptuje configuration change-om, deleguje ownershipom alebo rieši ako binding recovery. `refresh-only apply` zapisuje nový known snapshot, ale desired HCL nemení.

Preto sa pred refresh-only commitom zachová predecessor lineage/serial a overí writer/intent. Inak môže operátor legitimizovať attacker alebo incidentný override iba tým, že ho zapíše do state knowledge.""",
)
prepend_section(
    "terraform-state.md",
    "## 9. Evidence-preserving containment",
    """Pri rozdiele medzi state a remote objektmi sa zastavia writers skôr, než ďalší refresh alebo apply prepíše volatile evidence. Zachová sa state snapshot, backend version ID, plan, provider request IDs a remote audit; až potom sa rozhoduje medzi restore, importom, moved transitionom alebo compensation.""",
)
replace_section(
    "terraform-state.md",
    "### „Najnovší timestamp je správny backup“",
    """Najnovšia object-store verzia môže patriť chybnému writerovi, wrong backend migration alebo už poškodenému successor snapshotu. Restore candidate sa vyberá podľa lineage, serial, writer/run identity a expected bindings a pred aktiváciou sa testuje offline planom a remote inventory.""",
)
replace_section(
    "terraform-state.md",
    "### „Import znamená, že configuration je správna“",
    """Import vytvorí address-to-remote-ID binding. Neoverí, že HCL opisuje current object, provider target je správny alebo ownership má byť v tomto state-e. Po importe musí fresh plan vysvetliteľne smerovať k no-op alebo reviewed update bez neplánovaného replacementu.""",
)

# Remote backend
prepend_section(
    "remote-backend-and-state-locking.md",
    "## 1. Dominantný backend-to-commit lifecycle",
    """Backend lifecycle je optimistic change-control transakcia nad jedným explicitným state subjectom. Lock, predecessor snapshot a conditional successor write dávajú zmysel iba vtedy, keď všetci writers používajú rovnaký endpoint/key/workspace. Diagram preto začína subject identity, nie samotným lock acquisitionom.""",
)
prepend_section(
    "remote-backend-and-state-locking.md",
    "## 8. Dvaja writers nad dvoma backendmi",
    """Tento failure je dôležitý, pretože oba locking systémy môžu fungovať bez chyby. Konflikt vzniká nad remote resource ownershipom, zatiaľ čo každý writer serializuje iba svoju vlastnú state históriu. Diagnostika preto musí korelovať backend registry, workload identities a remote IDs naprieč oboma lineages.""",
)
prepend_section(
    "remote-backend-and-state-locking.md",
    "## 20. Competing hypotheses pri stale locku",
    """Stale lock je iba jedna hypotéza. Rovnaký symptóm môže vytvoriť živý worker bez UI heartbeat-u, asynchronous provider operation, wrong backend key alebo nový writer čakajúci v inej queue. Každá H-hypotéza musí mať observation point, ktorý ju odlíši pred `force-unlock`.""",
)

# Modules
replace_section(
    "modules.md",
    "## 2. Root module verzus child module",
    """Root module je deployment a state owner. Vyberá backend/state subject, environment composition, provider configurations a credentials, top-level inputs, apply identity, queue, recovery a acceptance lifecycle. Jeho repository a pipeline preto určujú, nad akým remote subjectom sa reusable code vykoná.

Child module poskytuje versionovanú capability cez inputs, outputs, required providers, resources a migration semantics. Caller ho instancuje `module` blockom a jeho resources sa rozvinú do caller graphu a state-u, napríklad `module.payments_service.aws_lb.api`.

Child module teda automaticky nedostáva vlastný lock, permissions ani blast-radius isolation. Samostatná state boundary vzniká iba samostatným root module-om, backendom a execution lifecycle-om. Module boundary rieši code/interface coupling; root/state boundary rieši ownership a failure domain.""",
)
replace_section(
    "modules.md",
    "## 9. Module boundary podľa capability a coupling-u",
    """Primeraný module reprezentuje jednu koherentnú capability so známym ownerom, spoločným lifecycle-om a release cadence. Jeho public contract má stabilné inputs/outputs, zvládnuteľný state space a jasnú policy alebo abstraction hodnotu.

Mega-module pre celý account mieša nezávislé security domains a vytvára široký upgrade blast radius. Extrémne tenký wrapper iba premenúva provider arguments a zvyšuje nesting bez stabilizácie behavioru. Počet `.tf` files preto nie je boundary criterion.

Boundary sa vyberá podľa change coupling-u, ownershipu, failure/recovery jednotky a support lifecycle-u. Consumer musí vedieť capability otestovať a upgradovať bez neúmyselného prebratia unrelated resources.""",
)
replace_section(
    "modules.md",
    "## 11. Versioning ako compatibility promise",
    """Module version je promise o caller contracte a existing-state transitione. Nový optional input s bezpečným defaultom, nový output alebo interný refactor s úplným `moved` chainom môžu byť kompatibilné, ak nemenia effective identity, exposure ani behavior existujúcich callerov.

Zmena default/null semantics, provider requirements, instance keys alebo resource addresses je risk-significant. Rovnako breaking môže byť nový replacement/destroy behavior alebo privilege/exposure expansion, aj keď HCL caller zostane syntakticky platný.

Semantic version label je deklarácia, nie dôkaz. Dôveryhodný release publikuje compatibility matrix a consumer upgrade test nad reprezentatívnym state-om. Plan musí vysvetliť migrations a runtime canary musí potvrdiť capability; druhý no-op plan uzatvára stabilitu successor verzie.""",
)

# Lifecycle/import/moved
replace_section(
    "lifecycle-import-moved-blocks.md",
    "## 2. Tri transition classes",
    """Remote lifecycle change, ownership adoption a address refactor menia tri odlišné vrstvy identity. Pri remote lifecycle change zostáva management address, ale provider vykoná update alebo replacement a remote object môže dostať nové ID. Availability, data a downstream references preto patria do transition risku.

Ownership adoption používa import: existujúci remote object bez current bindingu sa pripojí ku konkrétnej Terraform address-e a provider configuration. Import nemení automaticky remote bytes ani HCL; vytvára knowledge/ownership transition, ktorú musí následný plan porovnať s configuration.

Address refactor používa `moved` mapping: existujúci binding prejde z old address na new address pri rovnakom remote ID. Je to configuration/state identity migration bez zamýšľanej remote mutation. Ak chain nie je úplný alebo caller preskočí verziu, plan môže stále navrhnúť destroy/create.

Import ani `moved` negarantujú no-op. Fresh plan musí preukázať správny provider target, remote ID a configuration compatibility a forbidden fixture musí zachytiť chýbajúci migration contract.""",
)
replace_section(
    "lifecycle-import-moved-blocks.md",
    "## 3. Replacement je identity a availability event",
    """Replacement nie je iba kombinácia `delete` a `create`. Môže zmeniť remote ID, IP/DNS endpoint, attached policies, encryption alebo data identity, sessions, traffic routing, downstream references a rollback možnosti. Poradie `destroy→create` alebo `create→destroy` mení availability a coexistence risk, nie samotný dôvod replacementu.

Plan JSON musí pomenovať address, actions a `replace_paths`; reviewer potom posúdi data, capacity, quota a naming constraints. `create_before_destroy` môže zlyhať, ak platforma nepovolí dve rovnaké names alebo ak downstream consumer nevie paralelne prijať starú a novú identity.

Acceptance zahŕňa successor remote ID, traffic/data migration, state binding a retirement predecessor-a. Zelený create bez týchto checks môže ponechať dva active objects alebo odstrániť jediný recovery subject.""",
)
prepend_section(
    "lifecycle-import-moved-blocks.md",
    "## 13. Worked failure: import do nesprávneho accountu",
    """Import command môže byť syntakticky úspešný a napriek tomu viazať address k objectu v nesprávnom provider targete. Pred importom sa preto read-backuje account/region a immutable remote ID a po importe sa porovná state show, remote API a fresh plan.""",
)
replace_section(
    "lifecycle-import-moved-blocks.md",
    "### moved block",
    """`moved` je versionovaný configuration contract, ktorý Terraform vie aplikovať pre každého caller-a prechádzajúceho podporovanou upgrade cestou. Zachováva remote ID pri address refaktore a je reviewovateľný spolu so source change-om. Musí zostať dostatočne dlho, aby pokryl podporované predecessor verzie.""",
)
replace_section(
    "lifecycle-import-moved-blocks.md",
    "### terraform state mv",
    """`terraform state mv` je imperative mutation jedného konkrétneho state snapshotu. Je vhodná pre bounded recovery alebo legacy migration, ale ďalší caller ju z configuration nezdedí. Vyžaduje backup, exclusive lock, exact source/destination identity a bezprostredný fresh plan; pri opakovateľnom refaktore je preferovaný `moved` block.""",
)

# Drift
replace_section(
    "drift.md",
    "## 1. Dominantný observation-to-reconciliation lifecycle",
    """Drift lifecycle začína subject verification, pretože diff nad nesprávnym backendom alebo targetom nie je evidence o production. Authoritative configuration a attribute ownership sa porovnajú s presným state lineage/serialom a current provider observation.

```text
authoritative configuration a ownership contract
+ exact backend/state/provider target
+ current remote observation
→ subject-verified difference
→ origin, intent, risk a writer classification
→ revert | adopt | transfer ownership | remove management | recover state
→ fresh reviewed plan
→ bounded transition
→ state, remote, runtime a business verification
→ second plan a exception closure
```

Detector musí pomenovať resource address/remote ID, writer, authorization/expiry a authoritative layer pre každý changed attribute. Až táto klasifikácia rozhodne, či sa rozdiel revertuje, adoptuje, deleguje alebo rieši ako lost binding. Automatický apply bez nej môže odstrániť incident containment alebo legitimizovať attacker mutation.""",
)
prepend_section(
    "drift.md",
    "## 5. Drift taxonomy podľa mechanizmu",
    """Taxonómia oddeľuje podobný plan diff podľa príčiny a správnej recovery. Remote drift, configuration divergence, binding drift, provider interpretation, dependency drift, delegated mutation a unmanaged asset majú odlišného ownera aj bezpečný next step; spoločný symbol `~` alebo `+` ich nerozlišuje.""",
)
replace_section(
    "drift.md",
    "## 12. Provider noise a signal integrity",
    """Perpetual diff môže vzniknúť zo server-side defaultov, unordered fields modelovaných ako list, transient timestamps, eventual consistency, provider normalization, mutable external data alebo unstable generated values. Každý mechanizmus má inú opravu: canonical configuration, správny set/list model, bounded read-after-write retry, provider fix/upgrade alebo immutable dependency pinning.

Noise nie je iba ergonomický problém. Keď reviewer rutinne ignoruje stovky známych diffs, znižuje sa pravdepodobnosť odhalenia novej IAM alebo network expansion. Suppression preto potrebuje ownera a independent guardrail; široké `ignore_changes` iba odstraňuje evidence.

Signal integrity sa overí tak, že rovnaký successor state vytvorí druhý no-op plan a zároveň external writer test stále vyvolá alert. Cieľom nie je nulový počet riadkov za každú cenu, ale vysoká diskriminačná hodnota každého zostávajúceho diffu.""",
)
prepend_section(
    "drift.md",
    "## 16. Authoritative recovery incidentu `IAC-PAY-77`",
    """Recovery musí najprv obnoviť incidentnú authority a až potom normálnu Terraform reconciliation. Scheduled auto-apply zostáva pozastavený, kým sa neuzavrie, či dočasná WAF rule bude adoptovaná alebo reviewed revertovaná; inak by rovnaký mechanismus znova odstránil containment.""",
)
prepend_section(
    "drift.md",
    "## 17. Acceptance a forbidden paths",
    """Drift acceptance testuje tri triedy rozdielu: harmful unauthorized mutation, authorized expiring override a provider noise. Systém ich musí rozlíšiť a nesmie automaticky adoptovať ani revertovať unknown writer. Po closure fresh aj druhý plan potvrdia successor state bez potlačenia budúcej detekcie.""",
)

# Terraform testing and policy
replace_section(
    "terraform-testing-and-policy.md",
    "## 4. Najlacnejšie vrstvy",
    """Najlacnejšie checks poskytujú rýchlu spätnú väzbu, ale každá vrstva má úzky oracle. Formatting overuje canonical presentation podľa pinned Terraform CLI. `terraform validate` overuje configuration consistency voči dostupným module a provider schemas a JSON output umožní machine-readable verdict.

Validation však nekontaktuje production authority: nepreukazuje credentials, organization policy, quotas, remote API behavior, apply-time unknowns, eventual consistency, runtime connectivity, data migration ani cleanup. Tieto otázky patria plan, apply a runtime vrstvám.

Static analyzer môže nájsť public exposure, unpinned dependency alebo secret pattern, ale report je platný iba so scanner version/rulesetom, complete scanned inventory, parse/unsupported statusom a findings/baseline subjectom. Nula findings bez coverage je `MISSING_OR_INVALID_EVIDENCE`, nie pass.

Portfólio preto postupuje od lacných parser/schema checks cez plan assertions a policy k isolated apply-u a independent runtime oracle-u. Vyššia vrstva nenahrádza nižšiu; odpovedá na inú otázku.""",
)
replace_section(
    "terraform-testing-and-policy.md",
    "## 8. Apply/integration tests",
    """Apply test vytvára reálne resources a môže pozorovať provider CRUD, IAM, organization policy, quota, API normalization a eventual consistency. Musí však bežať v explicitne izolovanom account-e alebo projecte s short-lived identity a unikátnym run namespace-om.

Cost, network a resource limits ohraničujú blast radius. Každý resource dostane immutable run labels, TTL a cleanup ownera; pri cleanup failure sa zachová state a remote inventory namiesto označenia jobu za úplne úspešný. Parallel runs nesmú zdieľať names ani state subject.

Provider output ako `available` je iba platform-visible condition. Po apply nasleduje independent application or network oracle a potom cleanup read-back. Test verdict preto rozlišuje capability pass, cleanup incomplete a external dependency outage.""",
)
prepend_section(
    "terraform-testing-and-policy.md",
    "## 20. Competing hypotheses pri „green“ pipeline a failed production apply",
    """Green pre-production pipeline a failed production apply môžu znamenať chýbajúcu real-policy coverage, odlišnú identity, quota, stale saved plan alebo neplatný/missing report. Každá hypotéza sa viaže na konkrétny subject a discriminating evidence; „testy prešli“ nie je jedna univerzálna premise.""",
)
prepend_section(
    "terraform-testing-and-policy.md",
    "## 21. Authoritative recovery incidentu `IAC-PAY-77`",
    """Recovery najprv preklasifikuje každý gate result na `PASS`, `VIOLATION`, `TOOL_OR_INFRA_FAILURE`, `MISSING_OR_SKIPPED`, `STALE_SUBJECT` alebo `INVALID_REPORT`. Chýbajúci policy output sa nesmie normalizovať na prázdny clean report a fix sa musí overiť nad exact production-equivalent identity a policy bundle.""",
)
prepend_section(
    "terraform-testing-and-policy.md",
    "## 22. Acceptance a forbidden paths",
    """Testing acceptance zahŕňa happy path, forbidden configuration, tool/report failure a cleanup failure. Gate musí odmietnuť missing evidence rovnako spoľahlivo ako policy violation a druhá operation musí potvrdiť, že fixed artifact a policy generation zostali stabilné.""",
)

# Terraform practical walkthrough
prepend_section(
    "terraform-practical-walkthrough.md",
    "## 11. Formatting a validation",
    """Formatting a validation sú preflight checks nad source a resolved schemas. Nevytvárajú cloud plan ani remote operation, preto ich úspech nemožno preniesť na authorization, quota alebo runtime. Nasledujúce commands sa čítajú ako dva odlišné verdicts a ich outputs sa uchovávajú oddelene.""",
)
prepend_section(
    "terraform-practical-walkthrough.md",
    "## 17. State read-back",
    """Po apply sa state číta ako successor knowledge snapshot, nie ako náhrada cloud verification. Read-back musí potvrdiť lineage/serial, expected addresses, provider association a immutable remote IDs a následne ich porovnať s AWS API a runtime capability.""",
)
replace_section(
    "terraform-practical-walkthrough.md",
    "## 24. Diagnostický walkthrough",
    """Diagnostika začína presným symptómom a immutable operation subjectom. H1/H2 testujú, či pipeline zvolila správny backend, workspace, lineage a serial. H3 a H7 porovnávajú configuration addresses so state inventory, aby odlíšili chýbajúci `moved` contract od lost bindingu.

CloudTrail alebo ekvivalentné request IDs testujú H4/H5: remote create mohol uspieť pred timeoutom alebo objekt mohol vytvoriť iný writer. Caller identity, provider alias/region a debug metadata bez secrets testujú H6, teda wrong target configuration. Každá observation má timestamp a account/region context.

Až po tomto rozlíšení sa vyberie recovery: backend correction, import, moved transition, remote cleanup alebo state restore. Slepý `terraform apply`, `state rm`, `force-unlock` alebo `-target` sú zakázané, kým nie je známy first divergent transition. Closure vyžaduje remote/state binding, runtime test, forbidden wrong-target fixture a druhý no-op plan.""",
)

# Terraform troubleshooting anti-patterns
for heading, body in {
    "### Rollback all axes naraz bez inventory": "Rollback provider, module, variables, state aj remote objects naraz zničí schopnosť určiť, ktorá vrstva spôsobila failure, a môže vytvoriť ďalšiu ownership asymetriu. Recovery mení jednu autoritatívnu os po zachovaní state/remote evidence a po každom kroku vykoná discriminating read-back.",
    "### Retry unknown external operation": "Timeout po provider requeste môže mať unknown outcome: remote side effect prebehol, ale response alebo state commit sa stratili. Retry bez request-ID a remote reconciliation môže vytvoriť duplicate. Najprv sa číta provider/platform operation status a state binding, až potom sa rozhoduje o retry alebo importe.",
    "### Roll-forward cez live patch": "Live patch môže obnoviť službu, ale vytvára drift mimo versionovaného source a často neprežije replacement. Containment musí mať ownera a expiry a následne sa premietnuť do authoritative configuration alebo vedome odstrániť. Inak ďalší apply patch prepíše alebo ho ticho adoptuje.",
    "### Health green ako recovery closure": "Health endpoint môže potvrdiť iba malú runtime cestu a starú serving cohort. Recovery sa uzatvára exact artifact/config identity, business operation, forbidden pathom, state/remote consistency a druhým planom. Zelený health bez týchto dôkazov môže existovať pri partial alebo wrong-target recovery.",
}.items():
    replace_section("terraform-troubleshooting.md", heading, body)

print("Terraform explanation-depth pass applied.")
