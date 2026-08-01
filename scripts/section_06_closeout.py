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
        raise RuntimeError(f"Missing heading {heading!r} in {path}")
    write(path, text.replace(marker, marker + prose + "\n\n", 1))


def replace_exact(path: str, old: str, new: str) -> None:
    text = read(path)
    if new.strip() in text:
        return
    if old not in text:
        raise RuntimeError(f"Missing exact block in {path}: {old[:100]!r}")
    write(path, text.replace(old, new, 1))


path = "docs/06-gitlab/container-and-package-registry.md"
insert_after_heading(
    path,
    "## 2. Exact registry subject",
    """
Registry subject musí pomenovať celý content graph a producer, nie iba repository a tag. Pri OCI image sa rozlišuje index digest, per-platform manifesty a evidence referrers; pri package subjecte coordinate dopĺňa checksum a publication job. Nasledujúci YAML je release identity envelope, podľa ktorého sa overuje publication, promotion aj runtime consumption.
""",
)
insert_after_heading(
    path,
    "## 4. Multi-platform build and push",
    """
Multi-platform publication vytvára OCI index, ktorý odkazuje na samostatné manifesty pre jednotlivé platformy. Jeden úspešný build command preto môže skončiť partial graphom: index alebo jeden manifest môže chýbať, prípadne evidence nemusí byť naviazaná na rovnaký subject. Po push-i sa vždy číta index digest a enumerujú platform descriptors.
""",
)
insert_after_heading(
    path,
    "## 15. Troubleshooting flow",
    """
Registry investigation začína locatorom, ale okamžite prechádza na immutable digests a mapping history. Následne sa overí producer identity, complete platform/package graph, evidence, mirrors a runtime image IDs; až potom retention alebo revocation verdict. Tento ordering odlíši mutable tag od incomplete publication, mirror lagu alebo runtime cache.
""",
)

path = "docs/06-gitlab/environments-deployments-releases.md"
insert_after_heading(
    path,
    "## 4. Deployment record API",
    """
Deployment API je GitLab-side read-back workflow recordu. Query musí byť viazaná na exact project a environment locator a výsledok sa koreluje s pipeline, deployable jobom a release manifestom. API status nepreukazuje controller ani runtime outcome, ale umožní zistiť, ktorý request a actor GitLab považuje za deployment.
""",
)
insert_after_heading(
    path,
    "## 8. Runtime read-back",
    """
Runtime read-back sa vykonáva až po potvrdení target contextu, aby presný output nepatril nesprávnemu clusteru alebo namespace-u. Najprv sa číta desired/controller state Deploymentu a potom per-Pod resolved image identity. Tieto outputs stále nepreukazujú serving route ani business behavior, preto na ne nadväzuje traffic a capability canary.
""",
)

path = "docs/06-gitlab/variables-and-secrets.md"
replace_exact(
    path,
    """Secret exposure path je každé miesto, kde sa capability presunie mimo pôvodný provider alebo bounded process. Každý path má inú retention a observation boundary:

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
""",
    """Secret exposure path je každé miesto, kde sa capability presunie mimo pôvodný provider alebo bounded process. Každý path má inú retention, access a observation boundary, preto nemožno vykonať jednu univerzálnu kontrolu „secret nie je v logu“.

Command echo, debug tracing, process arguments a `/proc` vystavujú value počas execution window-u alebo ju zapisujú do durable job logu. Masking závisí od podporovaného formátu a nemusí zachytiť encoding alebo rozdelenie hodnoty. Preferovaný interface používa stdin, file descriptor alebo provider-native helper a diagnostiku smeruje do oddeleného streamu bez secret data.

Files, workspace, cache, artifacts, Docker layers a image history vytvárajú kópie s vlastným lifecycle-om. Cleanup hlavného jobu nemusí odstrániť distributed cache ani už uploadnutý artifact a build argument môže zostať v immutable image graph-e. Secret mount preto nesmie persistovať do výslednej vrstvy a output graph sa kontroluje pred publication.

Environment dumps, crash reports, child processes a service containers rozširujú consumer graph mimo hlavný script. Child môže zdediť environment alebo file a prežiť cancellation, zatiaľ čo diagnostic bundle môže odísť do observability alebo support systému. Acceptance sleduje process tree, runtime teardown a redaction pred export boundary.

Network exfiltration nepotrebuje log ani file; untrusted tool môže capability okamžite odoslať. High-value job preto používa pinned reviewed tooling, restricted egress a ephemeral runtime. Generated manifests, Terraform plans a ďalšie diagnostic artifacts majú explicitný sensitive-data contract, pretože resolved secret môžu uchovať dlhšie než pôvodný credential.

Jobs handling high-value capability získavajú short-lived target-scoped credential až po trust decisione. Closure zahŕňa search v artifacts, cache a logs, target-side revocation a old-credential forbidden test, nie iba absenciu plain textu v jednom job logu.
""",
)
insert_after_heading(
    path,
    "## 12. Revocation after exposure",
    """
Revocation je response na možnú capability compromise, nie kozmetická úprava GitLab variable. Najprv sa zachová evidence a zastaví ďalšie vydávanie alebo používanie credentialu, potom sa ruší authority na target systéme a až následne sa čistia kópie a reloadujú consumers. Poradie chráni forenzný subject a zároveň skracuje exploitation window.
""",
)
insert_after_heading(
    path,
    "## 15. Troubleshooting flow",
    """
Secret incident sa sleduje od key/purpose k autoritatívnemu providerovi a všetkým GitLab definitions, nie od jednej runtime value. Po resolution sa skúma eligibility, injection/exposure, external trust a resulting sessions a napokon loaded consumer generation. Takto sa odlíši variable shadowing od leak-u, broad federation alebo neúplnej rotácie.
""",
)

print("Section 06 closeout applied.")
