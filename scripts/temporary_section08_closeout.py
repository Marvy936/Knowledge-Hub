from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WALKTHROUGH = ROOT / "docs/08-container-fundamentals-and-docker/docker-practical-walkthrough.md"
README = ROOT / "docs/08-container-fundamentals-and-docker/README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label} occurrence, found {count}")
    return text.replace(old, new, 1)


walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
backslash = chr(92)

walkthrough = replace_once(
    walkthrough,
    f'[]byte(`{{{backslash}"status{backslash}":{backslash}"alive{backslash}"}}`)',
    '[]byte(`{"status":"alive"}`)',
    "healthz JSON literal",
)
walkthrough = replace_once(
    walkthrough,
    f'[]byte(`{{{backslash}"status{backslash}":{backslash}"ready{backslash}"}}`)',
    '[]byte(`{"status":"ready"}`)',
    "readyz JSON literal",
)
walkthrough = replace_once(
    walkthrough,
    f'strings.NewReader(`{{{backslash}"id{backslash}":{backslash}"pay-100{backslash}",{backslash}"amount{backslash}":1250,{backslash}"currency{backslash}":{backslash}"EUR{backslash}"}}`)',
    'strings.NewReader(`{"id":"pay-100","amount":1250,"currency":"EUR"}`)',
    "happy-path request body",
)
walkthrough = replace_once(
    walkthrough,
    f'`{backslash}"id{backslash}":{backslash}"pay-100{backslash}"`',
    '`"id":"pay-100"`',
    "happy-path response assertion",
)
walkthrough = replace_once(
    walkthrough,
    f'strings.NewReader(`{{{backslash}"id{backslash}":{backslash}"pay-invalid{backslash}",{backslash}"amount{backslash}":0,{backslash}"currency{backslash}":{backslash}"EUR{backslash}"}}`)',
    'strings.NewReader(`{"id":"pay-invalid","amount":0,"currency":"EUR"}`)',
    "forbidden request body",
)

old_verifier = '''        payload="$(wget -qO- http://payments-api:8080/version)"
        printf '%s\\n' "$payload"
        printf '%s\\n' "$payload" | grep -F '"service":"payments-api"'
        printf '%s\\n' "$payload" | grep -F '"config_generation":"${CONFIG_GENERATION}"'
'''
new_verifier = '''        payload="$$(wget -qO- http://payments-api:8080/version)"
        printf '%s\\n' "$$payload"
        printf '%s\\n' "$$payload" | grep -F '"service":"payments-api"'
        printf '%s\\n' "$$payload" | grep -F '"config_generation":"${CONFIG_GENERATION}"'
'''
walkthrough = replace_once(
    walkthrough,
    old_verifier,
    new_verifier,
    "Compose verifier shell variables",
)
walkthrough = replace_once(
    walkthrough,
    'and (.HostConfig.SecurityOpt | index("no-new-privileges:true") != null)',
    'and any(.HostConfig.SecurityOpt[]; startswith("no-new-privileges"))',
    "SecurityOpt normalization assertion",
)

WALKTHROUGH.write_text(walkthrough, encoding="utf-8")

readme = README.read_text(encoding="utf-8")
old_intro = '''# Container Fundamentals and Docker

Táto sekcia vysvetľuje containers od Linux process isolation a OCI standards až po Docker Engine, images, networking, storage, security, Dockerfile, Compose, BuildKit a systematické troubleshooting. Cieľom nie je memorovať Docker CLI príkazy, ale rozumieť kernel, image, runtime, build, distribution, configuration a lifecycle modelu.

Containers nadväzujú na Linux namespaces, cgroups, capabilities, networking, filesystems, artifact versioning, registries, CI/CD a Infrastructure as Code. Docker je konkrétna platforma a toolchain nad širšími container a OCI princípmi.
'''
new_intro = '''# Container Fundamentals and Docker

Táto sekcia vysvetľuje containers od Linux process isolation a OCI standards až po Docker Engine, images, networking, storage, security, Dockerfile, Compose, BuildKit a systematické troubleshooting. Cieľom nie je memorovať Docker CLI príkazy, ale rozumieť kernel, artifact, build, runtime, distribution, configuration, data a recovery modelu.

Containers nadväzujú na Linux namespaces, cgroups, capabilities, networking, filesystems, artifact versioning, registries, CI/CD a Infrastructure as Code. Docker je konkrétna platforma a toolchain nad širšími container a OCI princípmi. Sekcia preto oddeľuje source, build graph, image/index/config/layers, registry digest, Engine object, kernel-backed process boundary, mounted data, network flow, health verdict a business outcome.

Pôvodných 18 prose-first kapitol zostáva authoritative. Praktická remediation pridáva jeden celý executable Docker projekt, pretože samostatné Dockerfile, Compose, BuildKit a troubleshooting snippets nepreukazujú, že čitateľ vie zostaviť a overiť celý source-to-runtime lifecycle.
'''
readme = replace_once(readme, old_intro, new_intro, "section introduction")
readme = replace_once(
    readme,
    "## Odporúčané poradie",
    "## Authoritative poradie — aktívne kapitoly",
    "ordering heading",
)
old_order_tail = '''17. [BuildKit a Buildx](buildkit-buildx.md)
18. [Docker troubleshooting](docker-troubleshooting.md)
'''
new_order_tail = '''17. [BuildKit a Buildx](buildkit-buildx.md)
18. [Praktický Docker projekt od Dockerfile-u po overený Compose runtime](docker-practical-walkthrough.md)
19. [Docker troubleshooting](docker-troubleshooting.md)
'''
readme = replace_once(readme, old_order_tail, new_order_tail, "ordering tail")

walkthrough_section = '''## Hlavný praktický walkthrough

Kapitola [Praktický Docker projekt od Dockerfile-u po overený Compose runtime](docker-practical-walkthrough.md) vytvára malú Go HTTP službu s health, readiness, version a persistentným payment write/read contractom. Následne prechádza celý source tree, unit testy, `.dockerignore`, multi-stage Dockerfile, explicitný BuildKit test target, local single-platform build, image config a filesystem inspection, constrained `docker run`, non-root volume initialization, PID 1 a signal handling, health history, host port, named-volume persistence, Compose interpolation a resolved model, `depends_on` conditions, service DNS, runtime-hardening read-back, second `compose up`, configuration recreate, multi-platform registry publication, digest-pinned consumption a evidence-preserving troubleshooting.

Walkthrough obsahuje reálny Go source, testy, Dockerfile, Compose YAML, Bash a PowerShell commands, `jq`/`yq` assertions a GitLab release skeleton. Pri každom významnom kroku vysvetľuje, čo output preukazuje a čo ešte nie. Failure paths zahŕňajú container-loopback bind mismatch, volume ownership, mount obscuring, green process health pri zlyhávajúcom business write, mutable tag po scan-e, cgroup OOM a nesprávnu platformu alebo loader.

## Practical-example acceptance contract

Sekcia sa nepovažuje za prakticky hotovú iba preto, že jednotlivé kapitoly obsahujú Docker CLI alebo YAML snippets. Čitateľ musí vedieť prejsť jeden celý projekt od source inputs po verified runtime a vysvetliť identity a authority boundaries medzi Dockerfile-om, BuildKit builderom, image digestom, Docker contextom, container configom, volume-om, networkom a Compose projectom.

Každý významný command musí odpovedať na tri otázky: aký subject číta alebo mení, aký output očakávame a akú hranicu output skutočne dokazuje. `docker buildx build --target test` dokazuje executed test graph, nie final runtime image; `image inspect` dokazuje image metadata, nie effective container config; `docker ps` dokazuje Engine process state, nie readiness; `compose config` dokazuje resolved model, nie mutation; `compose up --wait` dokazuje bounded running/health verdict, nie persistentný business outcome; POST/GET po recreate dokazuje konkrétnu data persistence path, nie backup/restore alebo host-failure recovery.

'''
readme = replace_once(
    readme,
    "## Cieľ zvládnutia",
    walkthrough_section + "## Cieľ zvládnutia",
    "walkthrough section insertion point",
)

status_start = readme.find("## Stav\n")
if status_start == -1:
    raise RuntimeError("README status section not found")

completion = '''## Revalidation completion gate

Sekcia je `Ready for user review`, keď:

1. všetkých 18 concept kapitol zostáva prose-first a mechanisticky konzistentných;
2. praktický walkthrough je zaradený do authoritative ordering a navigation chainu;
3. walkthrough obsahuje kompletný source, test, Dockerfile, Compose model a verification scripts;
4. build, image, container, network, mount, health, Compose a business states sa nezlievajú;
5. examples používajú explicitný non-root user, read-only root, bounded writable paths, capability drop a resource limits;
6. test stage, local runtime, multi-platform publication a digest read-back majú samostatné verdicts;
7. business údaj prežije container aj Compose recreate v rovnakom data subjecte;
8. second `compose up` a configuration update rozlišujú no-op reconciliation od controlled replacementu;
9. failure walkthroughs používajú competing hypotheses, discriminating commands, containment a recovery;
10. navigation, ledger a learning-depth audit prejdú bez dočasných workflowov alebo closeout skriptov v merge diff-e.

## Aktuálny stav revalidácie

| Blok | Kapitoly | Stav |
|---|---:|---|
| Container/OCI/kernel, images, registry, network, storage a security | 8/8 | Complete |
| Docker Engine, Dockerfile, context/cache a multi-stage build | 4/4 | Complete |
| Mounts, networking, configuration/health a Compose | 4/4 | Complete |
| BuildKit/Buildx a troubleshooting | 2/2 | Complete |
| End-to-end Docker practical walkthrough | 1/1 | Complete |

Celkový authoritative stav: **19/19 · Ready for user review**. Tento stav znamená dokončený repository prose/practical pass; neznamená automatické používateľské schválenie, Accepted, Verified ani Stable. Príkazy boli technicky a syntakticky auditované proti aktuálnemu Docker CLI/Compose/Buildx contractu, ale neboli v tomto repository workflowe spustené proti reálnemu Docker Engine-u alebo registry.
'''
readme = readme[:status_start] + completion
README.write_text(readme, encoding="utf-8")

ledger = LEDGER.read_text(encoding="utf-8")
pattern = re.compile(r"^\| `08-container-fundamentals-and-docker` — Container Fundamentals and Docker \|.*$", re.MULTILINE)
match = pattern.search(ledger)
if not match:
    raise RuntimeError("Section 08 ledger row not found")

new_row = "| `08-container-fundamentals-and-docker` — Container Fundamentals and Docker | 19/19 prose-first + practical walkthrough revalidation | Ready for user review | 2026-07-31 | Pôvodných 18 authoritative kapitol zostáva strict revalidovaných. Praktická remediation pridala `docker-practical-walkthrough.md`, ktorý vytvára celý Go/Docker/Compose project od source a testov cez `.dockerignore`, multi-stage Dockerfile, BuildKit test graph, local a multi-platform image build, image/runtime inspect, non-root read-only container, cgroup/capability boundary, named-volume persistence, host port a service DNS, Compose resolved model, second reconciliation, digest-pinned registry consumption a evidence-preserving troubleshooting. Walkthrough obsahuje positive, forbidden, recreate, persistence, wrong-bind, mount-obscuring, volume-permission, OOM a platform/loader paths a pri každom command-e oddeľuje configured, resolved, exported, effective, runtime a business evidence. README ordering, navigation a practical acceptance contract boli zosúladené. Sekcia je pripravená na používateľskú kontrolu, nie automaticky používateľsky schválená, Accepted, Verified ani Stable. |"
ledger = ledger[: match.start()] + new_row + ledger[match.end() :]
LEDGER.write_text(ledger, encoding="utf-8")

print("Section 08 walkthrough corrections and closeout metadata applied.")
