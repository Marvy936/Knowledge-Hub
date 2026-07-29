from pathlib import Path


def load(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def save(path: str, text: str) -> None:
    Path(path).write_text(text, encoding="utf-8", newline="\n")


def insert_after_heading(text: str, heading: str, prose: str, marker: str) -> str:
    if marker in text:
        return text
    needle = heading + "\n\n"
    if needle not in text:
        raise SystemExit(f"Missing heading: {heading}")
    return text.replace(needle, needle + prose.rstrip() + "\n\n", 1)


def replace_line(text: str, old: str, new: str) -> str:
    if new in text:
        return text
    needle = old + "\n"
    if needle not in text:
        raise SystemExit(f"Missing line: {old}")
    return text.replace(needle, new + "\n", 1)


path = "docs/16-gitops-and-platform-engineering/flux.md"
text = load(path)

text = insert_after_heading(
    text,
    "## 1. Dominantný model",
    """Dominantný model sleduje jednu generation od schváleného intentu až po business outcome. Každá šípka predstavuje samostatnú state a trust boundary, na ktorej vzniká vlastný dôkaz aj vlastný typ zlyhania.

Tento chain zabraňuje skratke, pri ktorej sa dostupný source artifact alebo `Ready=True` condition považujú za hotový release. Flux môže úspešne dokončiť skoršiu reconciliation fázu a zároveň zlyhať pri renderi, target authorization, health assessment-e alebo až v application behavior-e.""",
    "Dominantný model sleduje jednu generation",
)

text = insert_after_heading(
    text,
    "## 3. Exact Flux subject",
    """Exact subject je korelačný kľúč celého incidentu alebo acceptance rozhodnutia. Spája declarative Flux objects s konkrétnym controller processom, source bytes, target identity a runtime outcome-om; bez neho sa statusy z rôznych reconciliation behov môžu omylom zložiť do jedného neexistujúceho úspechu.

Jednotlivé rozmery subjectu nie sú administratívne metadata. Každý z nich môže zmeniť final manifests, oprávnenie vykonať mutation, inventory ownership alebo význam health verdictu, preto musia zostať pozorovateľné spolu.""",
    "Exact subject je korelačný kľúč",
)

for old, new in [
("- Flux installation identity a controller versions — určujú, ktorý control plane a ktoré API semantics vykonali reconciliation;",
 "- **Flux installation identity a controller versions** — určujú konkrétny control plane, implementované API semantics a upgrade generation, ktoré vykonali reconciliation; bez tejto identity nemožno odlíšiť configuration failure od controller-version regresie."),
("- source object identity — napríklad namespace, name, UID a generation `GitRepository` alebo `OCIRepository`;",
 "- **Source object identity** — namespace, name, UID a generation odlišujú current source specification od starého objectu s rovnakým názvom a viažu downstream evidence na správny reconcile subject."),
("- configured source selector — URL, branch, tag, commit, SemVer range alebo digest;",
 "- **Configured source selector** — URL a branch, tag, commit, SemVer range alebo digest určujú pravidlo výberu remote contentu, pričom mutable selector ešte nie je resolved immutable identity."),
("- resolved source revision a artifact digest — určujú bytes, ktoré downstream controller reálne konzumoval;",
 "- **Resolved source revision a artifact digest** — identifikujú konkrétne bytes publikované source-controllerom a umožňujú preukázať, že downstream controller nekonzumoval stale alebo iný artifact."),
("- `Kustomization` alebo `HelmRelease` UID a generation — určujú reconciliation policy a values;",
 "- **`Kustomization` alebo `HelmRelease` UID a generation** — identifikujú exact reconciliation specification vrátane policy, values, timeoutov a target settings, nie iba názov release-u."),
("- path, dependencies, substitutions, decryption inputs a external references — menia final desired state;",
 "- **Path, dependencies, substitutions, decryption inputs a external references** — tvoria render graph, ktorý môže z rovnakého source artifactu vytvoriť odlišný final desired state."),
("- service account a target cluster/namespace — určujú authorization a destination;",
 "- **Service account a target cluster/namespace** — určujú principal, povolený mutation scope a fyzický destination; wrong identity alebo target môže nasadiť správny artifact do nesprávneho boundary."),
("- inventory, prune a field-management policy — určujú ownership a deletion behavior;",
 "- **Inventory, prune a field-management policy** — určujú, ktoré live objects Flux považuje za vlastné, ktoré fields presadzuje a kedy je deletion považovaná za eligible."),
("- health, timeout, retry a remediation policy — určujú, kedy sa transition považuje za technicky úspešnú;",
 "- **Health, timeout, retry a remediation policy** — definujú technický oracle, failure deadline a recovery action, takže rovnaký workload môže pri odlišnej policy dostať iný controller verdict."),
("- workload a business oracle — určujú, či nasadený system poskytuje zamýšľaný outcome.",
 "- **Workload a business oracle** — overujú exact running generation, loaded configuration a používateľský alebo settlement outcome, ktoré controller-level readiness sama nedokazuje."),
]:
    text = replace_line(text, old, new)

for old, new in [
("- path použitá downstream Kustomization existuje;",
 "- **Path existence** — `Ready=True` na source objekte nepreukazuje, že downstream `Kustomization.spec.path` v artifacte existuje; missing path zlyhá až na consumer build boundary."),
("- decryption key je dostupný;",
 "- **Decryption availability** — source artifact môže byť korektný ciphertext, ale KMS, age identity alebo workload-identity authorization môže zlyhať až pri decryption."),
("- manifests sú syntakticky alebo schema-valid;",
 "- **Manifest validity** — source controller neinterpretuje všetky downstream Kubernetes manifests, takže syntax, Kustomize transformácia alebo API schema môžu byť neplatné aj pri úspešnom fetchi."),
("- target API povoľuje apply;",
 "- **Target authorization** — artifact readiness nehovorí nič o Kubernetes RBAC, admission policy alebo target availability, ktoré rozhodujú až pri mutation."),
("- health checks prejdú;",
 "- **Health convergence** — úspešný source fetch nezaručuje, že aplikované controllers dosiahnu required observed generation a readiness v povolenom timeout-e."),
("- workload načítal správnu runtime generation;",
 "- **Runtime loading** — live object môže obsahovať nový config alebo Secret, ale už bežiaci process môže stále používať starú environment alebo cache generation."),
("- business canary prešiel.",
 "- **Business acceptance** — source readiness neoveruje end-to-end settlement, provider compatibility ani ďalší outcome, ktorý je mimo source-controller contractu."),
]:
    text = replace_line(text, old, new)

for old, new in [
("- source path sa omylom vyrenderuje na prázdny set;",
 "- **Prázdny render** — chybný path, condition alebo generator môže vytvoriť prázdny desired inventory; pri prune policy sa z build chyby môže stať mass deletion."),
("- resource bol presunutý medzi Kustomizations bez ownership handoffu;",
 "- **Presun bez ownership handoffu** — pôvodná Kustomization môže resource považovať za stale práve vtedy, keď nová Kustomization ešte neprevzala stabilnú inventory a field ownership."),
("- dve Kustomizations riadia rovnaký object;",
 "- **Overlapping inventories** — dve Kustomizations nad rovnakým objectom môžu striedavo meniť fields, reportovať conflict alebo jedna môže prune-nuť resource stále potrebný druhou."),
("- namespace alebo CRD sa odstráni skôr než dependents;",
 "- **Dependency-order deletion** — odstránenie namespace-u, CRD alebo shared controller resource-u pred dependents môže zničiť objects alebo znemožniť ich korektné finalization a recovery."),
("- generated name alebo target namespace sa zmení;",
 "- **Identity relocation** — zmena generated name-u alebo target namespace-u vyzerá ako create nového plus delete starého resource-u, nie ako bezpečný in-place update."),
("- Kustomization deletion spustí garbage collection podľa deletion policy.",
 "- **Kustomization deletion policy** — odstránenie samotného reconciliation subjectu môže podľa configured policy odstrániť celý jeho inventory, preto decommission potrebuje samostatný reviewovaný transition."),
]:
    text = replace_line(text, old, new)

for old, new in [
("- exact container digest vo všetkých running Pods;",
 "- **Exact workload digest** — generic resource health môže potvrdiť dostupné replicas, ale nemusí overiť, že každý running Pod patrí správnej ReplicaSet a používa intended digest."),
("- loaded configuration alebo secret generation v process memory;",
 "- **Loaded configuration a secret generation** — API object readiness nevidí process memory, environment snapshot ani application cache, v ktorých môže prežiť stale generation."),
("- network route cez všetky intermediaries;",
 "- **Effective network route** — healthy Service a Pods nepreukazujú DNS, ingress, gateway, service mesh, firewall ani provider path používanú reálnym klientom."),
("- database schema compatibility;",
 "- **Database compatibility** — deployment readiness nepreukazuje, že new reader/writer behavior je kompatibilný s current schema, backlogom a mixed-version consumers."),
("- provider-side effect;",
 "- **Provider-side effect** — Kubernetes status nevie potvrdiť remote authorization, idempotency alebo unknown operation outcome v external providerovi."),
("- customer journey alebo settlement correctness.",
 "- **Customer alebo settlement correctness** — resource health sa musí doplniť subject-bound business canary, pretože technicky dostupný workload môže stále produkovať nesprávny business result."),
]:
    text = replace_line(text, old, new)

for old, new in [
("- namespace segmentation a Kubernetes RBAC;",
 "- **Namespace segmentation a Kubernetes RBAC** — obmedzujú, kto môže vytvárať Flux objects a ktoré target resources môže tenant-bound service account čítať alebo meniť."),
("- `spec.serviceAccountName` na Kustomizations a HelmReleases;",
 "- **Explicitné `spec.serviceAccountName`** — núti target apply alebo Helm action používať tenant principal namiesto broad controller service accountu."),
("- controller default service account bez permissions, ak explicitný account chýba;",
 "- **Permissionless default identity** — fail-closed nastavenie zabráni tomu, aby omitted service account nevedomky zdedil cluster-wide write privilege controllera."),
("- zákaz cross-namespace source references;",
 "- **Zákaz cross-namespace source references** — bráni tenantovi konzumovať Git/OCI artifact alebo credentials spravované v cudzom namespace bez explicitného trust contractu."),
("- zákaz remote Kustomize bases;",
 "- **Zákaz remote Kustomize bases** — odstraňuje uncontrolled network a source dependency, ktorú tenant môže zmeniť mimo schváleného artifact graphu."),
("- oddelené source credentials a decryption identities;",
 "- **Oddelené source credentials a decryption identities** — obmedzujú repository a KMS blast radius na konkrétny environment alebo tenant, aj keď je shared controller kompromitovaný."),
("- resource quotas a admission policies pre tenant-created Flux objects;",
 "- **Resource quotas a admission policies** — limitujú počet, interval, target scope a nebezpečné options tenant-created reconciliation loops, aby jeden tenant nevytvoril control-plane denial of service."),
("- platform-admin reconciliation oddelenú od tenant reconciliation.",
 "- **Oddelená platform-admin reconciliation** — chráni CRDs, controllers a cluster baseline pred tým, aby tenant workflow vlastnil alebo prune-oval shared platform resources."),
]:
    text = replace_line(text, old, new)

text = insert_after_heading(
    text,
    "## 18. Connected incident `GITOPS-PAY-62`",
    """Incident sa musí čítať ako rozpad jednej generation identity cez štyri control planes, nie ako nezávislé chyby Fluxu, portalu a providera. Každý writer bol lokálne schopný vykonať svoju operáciu, ale systém nemal invariant, ktorý by zachoval schválený image, route a credential contract od staging evidence po production process.

Nasledujúce body preto pomenúvajú konkrétne authority transitions. Ich spoločným dôsledkom bolo, že Flux `Ready=True` opisoval configured reconciliation, zatiaľ čo promotion UI, running workload a provider authority opisovali tri odlišné release subjects.""",
    "Incident sa musí čítať ako rozpad jednej generation identity",
)

text = insert_after_heading(
    text,
    "### Redesign",
    """Redesign nemení iba niekoľko Flux fields. Obnovuje jednu reprodukovateľnú desired-state generation, odstraňuje hidden render writerov a zavádza runtime oracles pre properties, ktoré Kubernetes readiness nevidí.

Každý nasledujúci transition má vlastného ownera a evidence. Promotion autorita vytvorí immutable environment reference, Flux ju resolve-ne a reconcile-ne, secret lifecycle zabezpečí consumer convergence a platform operation sa uzavrie až po business canary.""",
    "Redesign nemení iba niekoľko Flux fields",
)

text = insert_after_heading(
    text,
    "## 19. Flux acceptance verdict",
    """Acceptance je zložený verdict nad celou sieťou controllerov. Source readiness, apply completion, inventory safety, workload readiness a business correctness sa overujú oddelene a potom sa korelujú cez rovnakú revision a operation identity.

Nasledujúce podmienky nie sú univerzálny checklist bez kontextu. Spolu dokazujú, že controller môže po source change-i, direct drift-e, výpadku alebo restarte znovu dosiahnuť rovnaký bounded outcome bez cross-tenant mutation a hidden inputu.""",
    "Acceptance je zložený verdict nad celou sieťou controllerov",
)

text = insert_after_heading(
    text,
    "## 20. Troubleshooting flow",
    """Troubleshooting postupuje od najskoršej authoritative identity k neskorším materializovaným stavom. Cieľom nie je opakovane volať manual reconcile, ale nájsť prvú boundary, na ktorej sa expected revision prestala zhodovať s observed evidence.

Po oprave sa flow vykoná druhýkrát: controller musí znovu resolve-nuť source, obnoviť inventory a health a workload musí preukázať exact loaded generation aj business outcome.""",
    "Troubleshooting postupuje od najskoršej authoritative identity",
)
save(path, text)
