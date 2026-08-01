from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRANCH = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
if not BRANCH:
    raise SystemExit("Unable to resolve pull request branch")


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=REPO, check=True)


run("git", "fetch", "origin", BRANCH)
run("git", "checkout", "-B", BRANCH, f"origin/{BRANCH}")

path = REPO / "docs/08-container-fundamentals-and-docker/dockerfile.md"
text = path.read_text(encoding="utf-8")
anchor = "## 1. Parser directive a syntax frontend\n"
if text.count(anchor) != 1:
    raise RuntimeError("Dockerfile insertion anchor not found exactly once")

table = r"""## Rýchla orientácia v Dockerfile instructions

Nasledujúca tabuľka slúži ako mapa celej Dockerfile syntaxe. Detailné správanie, scope, cache a runtime dôsledky jednotlivých instructions vysvetľujú nasledujúce časti kapitoly.

| Instruction | Kedy pôsobí | Čo robí | Dôležitá hranica alebo typická chyba |
|---|---|---|---|
| `FROM` | build | Začína nový build stage z base image-u, predchádzajúceho stage-u alebo `scratch`. | Tag nie je immutable identity; stage sa nemusí vykonať, ak neleží v dependency graph-e zvoleného targetu. |
| `ARG` | build | Deklaruje build-time parameter a voliteľný default. | Nie je runtime environment; nie je vhodný na secrets a scope pred `FROM` sa automaticky neprenáša do stage-u. |
| `ENV` | build metadata a runtime default | Zapíše environment premennú pre ďalšie build instructions a do image configu. | Runtime ju môže prepísať; secret zostáva viditeľný v image alebo container metadata. |
| `LABEL` | build metadata | Pridáva key-value metadata, napríklad OCI title, source, version alebo revision. | Label nie je cryptographic provenance a jeho hodnotu môže producer uviesť nesprávne. |
| `RUN` | build | Vykoná command v aktuálnom stage-i a uloží filesystem/config changes do build resultu. | Nezamieňať s runtime `CMD`; shell a exec form majú odlišnú expansion, signal a quoting semantics. |
| `COPY` | build | Kopíruje files alebo directories z build/named contextu či iného stage-u. | Source je obmedzený contextom a `.dockerignore`; `--from` prenáša artifact, nie celý runtime state stage-u. |
| `ADD` | build | Kopíruje podobne ako `COPY`, navyše má širšie semantics, napríklad lokálne tar extraction a podporované remote/Git sources. | Pre obyčajné local files je transparentnejší `COPY`; implicitné rozbalenie alebo remote input môže skryť build contract. |
| `WORKDIR` | build metadata a runtime default | Nastaví pracovný adresár pre nasledujúce `RUN`, `COPY`, `ADD`, `CMD` a `ENTRYPOINT`. | Relative paths sa skladajú s predchádzajúcim `WORKDIR`; implicitný directory z base image-u môže byť prekvapivý. |
| `USER` | build metadata a runtime default | Nastaví default UID/GID pre nasledujúce build kroky a runtime process. | Runtime môže usera prepísať; numeric UID bez potrebných permissions alebo home/passwd contractu môže aplikáciu rozbiť. |
| `SHELL` | build metadata | Mení default shell používaný shell-form instructions v aktuálnom stage-i. | Ovplyvňuje parsing, flags a error semantics ďalších `RUN`, `CMD` a `ENTRYPOINT` shell forms. |
| `EXPOSE` | image metadata | Dokumentuje port a protocol, na ktorom má application počúvať. | Nevytvára host port, listener, route ani firewall rule. |
| `VOLUME` | image metadata a runtime mount intent | Označuje path ako volume mount point. | Nevlastní konkrétny production volume ani backup; neskoršie build changes pod mount pathom môžu mať prekvapivé semantics. |
| `STOPSIGNAL` | image runtime default | Nastaví default signal pre stop lifecycle containeru. | Nezaručuje graceful shutdown; PID 1 a application musia signal spracovať v dostupnom grace period. |
| `HEALTHCHECK` | image runtime default | Definuje command a timing pre Docker health state. | Health nie je automaticky service reachability ani business correctness a runtime ho môže prepísať alebo vypnúť. |
| `ENTRYPOINT` | image runtime default | Určuje hlavný executable alebo shell command containeru. | Exec form poskytuje priame argv a signal semantics; `--entrypoint` ho môže runtime prepísať. |
| `CMD` | image runtime default | Určuje default command alebo default arguments pre `ENTRYPOINT`. | Pri `docker run IMAGE ...` sa typicky nahrádza; nevykonáva sa počas buildu. |
| `ONBUILD` | deferred build | Uloží trigger, ktorý sa vykoná, keď je image použitý ako base v inom Dockerfile-i. | Side effect je odložený do child buildu, preto musí byť úzky a predvídateľný; nesmie používať zakázané nested instructions. |
| `MAINTAINER` | image metadata, deprecated | Historicky zapisoval autora image-u. | Je deprecated; používaj OCI-compatible `LABEL`, napríklad `org.opencontainers.image.authors`. |
| `# syntax=...` | parser/build frontend | Vyberá Dockerfile frontend a dostupnú syntax. | Nie je bežný comment, ak je v úvodnej parser-directive pozícii; zmena frontendu môže zmeniť build semantics. |
| `# escape=...` | parser | Mení escape character, najmä pri Windows Dockerfiles. | Ovplyvňuje line continuation a parsing celého súboru. |
| `# check=...` | build checks | Konfiguruje Dockerfile build checks podporované frontendom. | Je to policy nad authoringom, nie runtime kontrola image-u alebo containeru. |

"""
text = text.replace(anchor, table + anchor, 1)
path.write_text(text, encoding="utf-8")

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run("git", "add", "docs/08-container-fundamentals-and-docker/dockerfile.md")
run("git", "commit", "-m", "docs(docker): add Dockerfile instruction reference table")
run("git", "push", "origin", f"HEAD:{BRANCH}")
