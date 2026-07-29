from pathlib import Path

path = Path("docs/16-gitops-and-platform-engineering/internal-developer-platform.md")
text = path.read_text(encoding="utf-8")

def add(heading: str, prose: str, marker: str) -> None:
    global text
    if marker in text:
        return
    needle = heading + "\n\n"
    if needle not in text:
        raise SystemExit(f"Missing heading: {heading}")
    text = text.replace(needle, needle + prose.rstrip() + "\n\n", 1)

add(
    "## 1. Dominantný model",
    """Dominantný model sleduje request ako durable platform operation, nie ako synchronný portal click. Každá transition mení authoritative state v inom systeme a môže skončiť úspešne, zlyhať, zostať partial alebo mať unknown outcome.

Repository creation, cloud resource readiness, GitOps reconciliation a developer-functional verification sú samostatné dôkazy. Platform ich musí korelovať cez rovnaký operation subject, inak optimistický portal status zakryje neúplný alebo nefunkčný resource graph.""",
    "Dominantný model sleduje request ako durable platform operation",
)
add(
    "## 2. Platform engineering, IDP a developer portal",
    """Tieto tri pojmy opisujú disciplínu, výsledný capability system a používateľské rozhranie. Ich zamieňanie vedie k tool-first návrhu: organizácia nainštaluje portal, ale nezavedie authoritative API, durable workflows, ownership, policy enforcement ani lifecycle.

Rozlíšenie je praktické aj pri incidente. Portal môže byť dostupný a zobrazovať cached projection, zatiaľ čo platform control plane alebo execution systems zlyhali; platform capability môže naopak fungovať cez API aj pri výpadku portal UI.""",
    "Tieto tri pojmy opisujú disciplínu",
)
add(
    "### Internal Developer Platform",
    """IDP skladá capabilities do konzistentného product contractu. Nie všetky organizácie potrebujú každý capability domain, ale tie, ktoré platforma deklaruje, musia zdieľať identity, policy, operation-state a support model namiesto izolovaných automatizačných skriptov.

Zoznam capability domains preto nie je feature checklist. Každý z nich predstavuje časť developer journey a zároveň authority boundary, ktorú platforma musí bezpečne orchestrate-nuť a následne pozorovať.""",
    "IDP skladá capabilities do konzistentného product contractu",
)
add(
    "## 3. Problém, ktorý IDP rieši",
    """Problémom nie je iba počet nástrojov, ale počet rozhodnutí a neviditeľných dependencies, ktoré musí každý application tím opakovane správne poskladať. Rovnaká business potreba tak vytvára odlišné security, lifecycle a failure semantics podľa lokálneho skriptu alebo znalostí konkrétneho človeka.

Uvedené symptómy sa navzájom posilňujú. Duplicated automation vedie k inconsistent implementations, tie zvyšujú support toil a central ticket queues následne ešte viac oddeľujú developera od mechanizmu, ktorý jeho service prevádzkuje.""",
    "Problémom nie je iba počet nástrojov",
)
add(
    "## 4. Exact platform request subject",
    """Platform request je semantic command nad existujúcim resource graphom. Exact subject umožňuje rozhodnúť, či ide o nový service, update tej istej capability alebo conflicting request a poskytuje idempotency identity pre downstream systems.

Každý rozmer subjectu mení provisioning, policy alebo support consequence. Preto sa nemá ukladať iba vo form fields; musí byť versionovaný v durable operation a prenesený do authoritative resources a catalog relations.""",
    "Platform request je semantic command",
)
add(
    "## 5. Capability contract",
    """Capability contract je produktový aj technický záväzok medzi platform teamom a consumerom. Musí byť dostatočne high-level, aby skryl incidental provider complexity, ale dostatočne explicitný, aby developer rozumel failure, cost, security a lifecycle dôsledkom svojich choices.

Guarantees, defaults, consumer choices, policies, observability, support a deletion semantics sa vyhodnocujú spolu. Create action bez upgrade a decommission contractu je neúplný product, aj keď initial provisioning prejde.""",
    "Capability contract je produktový aj technický záväzok",
)
add(
    "## 7. Control plane, orchestration a execution planes",
    """Rozdelenie planes chráni authority a vysvetľuje, kde vzniká ktorý dôkaz. Experience plane prijíma intent a prezentuje projection, control plane drží operation state a decisions, execution planes vykonávajú mutations a workload plane poskytuje reálny application outcome.

Ak sa tieto vrstvy zlúčia do portal processu, UI response sa ľahko zamení za infrastructure alebo business success. Samostatné planes umožňujú aj to, aby portal mohol bezpečne zlyhať bez straty durable operation a aby backend policy nebola obídená priamym API clientom.""",
    "Rozdelenie planes chráni authority",
)
add(
    "## 9. Idempotency a identity reservation",
    """Identity reservation serializuje semantic creation skôr, než workflow vykoná drahé alebo ťažko vratné side effects. Stable service identity potom slúži ako lookup key pri retry a umožňuje odlíšiť existujúci equivalent resource od collision s iným contractom.

Bez reservation sa duplicate repositories, namespaces, cloud IDs, DNS a IAM objects stanú rozdielnymi authority candidates. Neskoršia deduplikácia je nebezpečná, pretože každý z nich už môže mať vlastné data, permissions alebo users.""",
    "Identity reservation serializuje semantic creation",
)
add(
    "### Managed contract",
    """Managed contract oddeľuje stable consumer interface od evolvujúcej platform implementation. Generated repository nemusí dostať každý nový file, ak zostáva napojený na versionovaný reusable pipeline, platform API alebo controller, ktorý platform team môže bezpečne upgradovať.

Aby táto väzba nebola hidden lock-in, contract musí byť pozorovateľný, testovateľný a migrovateľný. Input schema, version, output inventory, permission boundaries a migration strategy spolu určujú, či platforma vie meniť implementation bez tichého behavior driftu.""",
    "Managed contract oddeľuje stable consumer interface",
)
add(
    "## 12. Software catalog a ownership metadata",
    """Catalog je projection software ecosystemu, nie automaticky authoritative runtime inventory. Jeho hodnota vzniká až vtedy, keď owner, API a resource relations možno korelovať s reálnymi Git, platform a runtime identities a keď stale alebo orphan entries vyvolajú remediation.

Otázky v tejto sekcii preto nie sú iba discovery convenience. Odpovede sa používajú pri impact analysis, incidente, deprecation, cost attribution a decommission-e a musia mať definovaný source a freshness.""",
    "Catalog je projection software ecosystemu",
)
add(
    "## 14. Self-service nie je unrestricted privilege",
    """Self-service automatizuje vopred schválený action contract, nie prenos underlying administrator rights na každého requestera. Platform identity môže byť silnejšia než user identity, preto musí konať iba nad resource subjectom odvodeným z validovaných inputs a tenant policy.

Zakázané examples ukazujú, kde by abstraction prestala byť bounded capability. Arbitrary provider code, IAM role alebo production mutation by z platformy urobili confused deputy a odstránili audit, idempotency a recovery semantics.""",
    "Self-service automatizuje vopred schválený action contract",
)
add(
    "## 16. Partial failure a compensation",
    """Partial failure je normálny stav distributed platform operation, pretože Git, cloud, DNS a Kubernetes nemajú spoločnú transaction. Control plane musí vedieť, ktoré steps sa už stali authoritative, ktoré majú unknown outcome a ktoré možno bezpečne zopakovať.

Compensation nie je automatické vymazanie všetkého. Každý step potrebuje preconditions, pretože repository už môže obsahovať user commits, database data alebo DNS traffic a destructive rollback by mohol spôsobiť väčšiu škodu než zachovaný partial state.""",
    "Partial failure je normálny stav distributed platform operation",
)
add(
    "## 17. Verification vrstvy",
    """Platform verification musí oddeliť existenciu resource-u od jeho integrácie a použiteľnosti. Provider môže reportovať available database, ale workload identity nemusí mať access; GitOps môže byť Ready, ale developer nemusí vedieť nasadiť prvú zmenu.

Preto sa provisioning, integration, developer-functional, operational a business evidence skladajú postupne. Každá vrstva uzatvára iný failure boundary a až ich kombinácia umožňuje označiť capability za usable.""",
    "Platform verification musí oddeliť existenciu resource-u",
)
add(
    "## 18. Platform observability",
    """Platform observability musí odpovedať na dve odlišné otázky: či control plane spracúva operations spoľahlivo a či consumers dostávajú usable capabilities v sľúbenom čase. Samotné CPU, HTTP latency alebo successful task count neodhalia partial resources, stale projections ani developer journey failure.

Signály v zozname sledujú request lifecycle aj product outcome. Ich kombinácia umožňuje odlíšiť insufficient worker capacity, downstream throttling, poison request, policy friction, reconciliation lag, lifecycle debt a adoption problém.""",
    "Platform observability musí odpovedať na dve odlišné otázky",
)
add(
    "## 20. Lifecycle: update, migrate a deprecate",
    """Platform capability je dlhodobý contract, preto create predstavuje iba prvú transition. Existing consumers potrebujú version-aware updates, ownership transfer, credential rotation, migration a safe decommission bez straty identity alebo data.

Deprecation list opisuje riadený closure proces. Replacement, inventory, tooling, deadlines, evidence a final gate musia zostať prepojené, aby platforma nevypla capability na základe neúplného self-reportingu alebo ponechala permanentné exceptions.""",
    "Platform capability je dlhodobý contract",
)
add(
    "## 21. Multi-tenancy",
    """Platform tenant identity musí prežiť prechod z requester session cez durable operation až do Git, cloud, secret a runtime resources. UI filter ani catalog owner label nie sú authorization; každý execution adapter musí znovu presadiť tenant-bound scope.

Identity, API, accounts, Git, IAM, secret paths, network, logs a cost attribution tvoria jeden isolation chain. Slabá jediná vrstva môže z platform identity urobiť confused deputy alebo umožniť noisy-neighbor tenantovi vyčerpať shared workers a quotas.""",
    "Platform tenant identity musí prežiť prechod",
)
add(
    "## 22. Security threat model",
    """IDP je privileged automation control plane, preto threat model sleduje, ako untrusted request alebo compromised plugin využije platform identity. Každý threat sa posudzuje podľa vstupnej boundary, získanej authority, possible side effectu a evidence potrebnej na detection a containment.

Scenáre pokrývajú requester identity, template execution, third-party tokens, egress, distributed retries a projections. Spoločnou otázkou je, či platforma môže vykonať action, ktorú samotný používateľ vykonať nesmie, a ak áno, čo ju viaže na schválený operation subject.""",
    "IDP je privileged automation control plane",
)
add(
    "## 23. Backstage ako portal framework",
    """Backstage poskytuje composable experience a integration primitives, ale neurčuje autoritatívny resource model ani distributed transaction semantics celej platformy. Každý plugin alebo scaffolder action môže volať underlying API s vlastným tokenom a failure behaviorom.

Preto treba rozlíšiť Backstage task completion od IDP capability acceptance. Portal framework môže vytvoriť proposal alebo resource, no durable control plane musí ďalej sledovať reconciliation, runtime a developer-functional outcome.""",
    "Backstage poskytuje composable experience",
)
add(
    "## 24. Connected incident `GITOPS-PAY-62`",
    """LaunchPad workflow treba analyzovať ako distributed operation, ktorej UI task log zachytil iba skoré side effects. Každý vykonaný step vytvoril state v inom authoritative systeme, ale portal nemal persisted resource IDs a completion oracle, ktorý by ich spojil s Flux runtime a business canary.

Repository a catalog creation boli úspešné local outcomes, no direct ConfigMap write a promotion PR zároveň zaviedli hidden authority a ešte nepreukázali usable production capability. Označenie `Completed` preto bolo false-success verdictom, nie iba nepresným textom v UI.""",
    "LaunchPad workflow treba analyzovať ako distributed operation",
)
add(
    "### Redesign",
    """Redesign presúva authority z portal tasku do declarative platform resource-u a durable controller operation. Portal prijme request a zobrazuje projection; control plane udržiava step state, downstream IDs a recovery a GitOps/runtime systems poskytujú acceptance evidence.

Operation sa môže bezpečne resume-nuť po process alebo provider failure. Rovnaký operation ID zabráni duplicate resources a status `Succeeded` vznikne až po developer-functional a business verification, nie po prvom úspešnom API call-e.""",
    "Redesign presúva authority z portal tasku",
)
add(
    "## 25. IDP acceptance verdict",
    """IDP acceptance hodnotí platformu ako distributed product system. Musí byť súčasne bezpečná pre tenantov, spoľahlivá pri partial a unknown outcomes a použiteľná pre developera; úspech iba jednej z týchto osí nestačí.

Verdict spája request identity, durable operation, authoritative writers, effective resources a user outcome. Jeho rozhodujúcim testom je opakovaný rovnaký request po controller restarte alebo dependency failure, ktorý musí obnoviť ten istý resource graph a pravdivý status.""",
    "IDP acceptance hodnotí platformu ako distributed product system",
)
add(
    "## 26. Troubleshooting flow",
    """Troubleshooting začína exact operation ID a semantic requestom, pretože portal status alebo resource name nemusia identifikovať všetky retries a partial side effects. Z operation ledgeru sa postupuje do jednotlivých authoritative systems a porovnáva sa intended output inventory s read-back evidence.

Recovery sa volí podľa prvého neuzavretého boundary: workflow možno resume-nuť, bezpečne compensate-nuť alebo odovzdať manual ownerovi. Po oprave sa zopakuje developer-functional test aj identický request, aby sa preukázala end-to-end idempotency.""",
    "Troubleshooting začína exact operation ID",
)

path.write_text(text, encoding="utf-8", newline="\n")
