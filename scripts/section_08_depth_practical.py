from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "08-container-fundamentals-and-docker"


def insert(heading: str, prose: str) -> None:
    path = SECTION / "docker-practical-walkthrough.md"
    text = path.read_text(encoding="utf-8")
    marker = heading + "\n"
    pos = text.find(marker)
    if pos == -1:
        raise RuntimeError(f"Heading not found: {heading}")
    start = pos + len(marker)
    next_heading = text.find("\n## ", start)
    end = len(text) if next_heading == -1 else next_heading
    body = prose.strip()
    if body in text[start:end]:
        return
    updated = text[:start] + "\n" + body + "\n\n" + text[start:].lstrip("\n")
    path.write_text(updated.rstrip() + "\n", encoding="utf-8", newline="\n")


insert(
    "## 10. Container najprv vytvor, až potom spusti",
    """`docker create` materializuje immutable image config spolu s runtime overrides do container objectu, ale ešte nespúšťa application process. Tento oddelený krok vytvára bezpečný inspection point: možno overiť image reference, user, entrypoint a command, environment, mounts, port publication, cgroup limits a security options pred prvou process mutation.

Container ID je exact runtime subject pre ďalšie kroky. Ak effective config nezodpovedá schválenému contractu, objekt sa odstráni bez spustenia. Ak je config správny a `docker start` zlyhá, problém sa už lokalizuje na process alebo runtime boundary, nie na create-time argument parsing či Engine object configuration.""",
)

insert(
    "## 12. Host-published path a loaded configuration",
    """Host request na `127.0.0.1:18080` testuje inú cestu než container-local healthcheck. Prechádza host socketom, Docker port-publishing dataplane-om, container network namespace-om a application listenerom. Exact container ID, published host IP a port a container target port preto patria k rovnakému request evidence.

Endpoint `/version` pridáva application oracle: vracia binary version a loaded configuration generation. Tým odlišuje iba otvorený port od správneho processu s očakávanými inputs. Stále nepreukazuje service-to-service DNS, external load balancer ani business write; tie majú samostatné testy.""",
)

insert(
    "## 13. Business zápis do volume-u",
    """POST request vytvára durable business subject `pay-100` cez application validation a write path do named volume-u. Úspešná HTTP odpoveď sama nestačí, preto nasleduje read-back rovnakého operation ID a exact fields. Tým sa odlišuje prijatý request od skutočne čitateľného application state-u.

Volume persistence sa však ešte nepreukázala: dáta môžu existovať iba v aktuálnom container a writer context-e. Až neskorší container replacement s novým container ID a rovnakým volume subjectom ukáže, že zápis prežil replacement na tom istom hoste. Backup, host loss, concurrent writers a crash consistency zostávajú samostatné boundaries.""",
)

insert(
    "## 14. Graceful stop",
    """`docker stop` odošle configured stop signal hlavnému PID 1 a čaká do grace timeoutu; potom môže Engine proces ukončiť násilne. Test preto sleduje signal handling, process exit code a completion time pre exact container ID. Exit code `0` je process-level výsledok, nie automatický dôkaz bezpečného ukončenia všetkých in-flight business operácií.

Po opätovnom štarte sa kontroluje health a dostupnosť predchádzajúceho payment subjectu. V produkčnej aplikácii by acceptance navyše vytvorila request počas shutdownu a overila drain, idempotency alebo recovery semantics. `STOPSIGNAL` a grace period iba definujú transport a časový budget; correctness patrí aplikácii.""",
)

insert(
    "## 16. Compose environment",
    """Compose interpolation je samostatná configuration-resolution vrstva. Hodnoty môžu pochádzať zo shell environmentu, `.env`, explicitného `--env-file` a defaults alebo error expressions v Compose modeli; ich precedence musí byť stabilná a auditovateľná. `env.example` preto dokumentuje required interface, zatiaľ čo konkrétny `.env` vytvára jednu local execution generation.

Pred mutation sa resolved values overia cez `docker compose config` bez vypisovania secrets. Production credentials do `.env` nepatria, pretože file, shell history, process environment a CI logs sú exposure boundaries. Image reference a configuration generation sa majú viazať na immutable artifact a konkrétny run, nie na implicitný developer shell state.""",
)

insert(
    "## 19. Spustenie Compose application",
    """`docker compose up` porovná resolved application model s existujúcimi Engine objects a vytvorí, znovu použije alebo nahradí networks, volumes a containers podľa identity a config hashov. `--wait` čaká na configured health alebo completion conditions, ale jeho success je infrastructure verdict nad Compose graphom, nie application business acceptance.

Po mutation sa preto čítajú container IDs, image digests, processy, health a logs a vykonajú sa dve odlišné request paths: internal service DNS z verifier containeru a host publication z loopbacku. Volume read-back a druhý unchanged `up` dopĺňajú persistence a no-op reconciliation. Tak sa oddeľuje successful Compose orchestration od skutočne dostupnej a správne nakonfigurovanej služby.""",
)

print("Applied Section 08 practical walkthrough depth pass.")
