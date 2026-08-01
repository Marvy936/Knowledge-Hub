from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "08-container-fundamentals-and-docker"


def insert(name: str, heading: str, prose: str) -> None:
    path = SECTION / name
    text = path.read_text(encoding="utf-8")
    marker = heading + "\n"
    pos = text.find(marker)
    if pos == -1:
        raise RuntimeError(f"Heading not found: {name}: {heading}")
    start = pos + len(marker)
    next_heading = text.find("\n## ", start)
    end = len(text) if next_heading == -1 else next_heading
    body = prose.strip()
    if body in text[start:end]:
        return
    updated = text[:start] + "\n" + body + "\n\n" + text[start:].lstrip("\n")
    path.write_text(updated.rstrip() + "\n", encoding="utf-8", newline="\n")


insert(
    "buildkit-buildx.md",
    "## 19. Od build requestu po overený digest",
    """Referenčný flow musí udržať jednu build identity od source commit-u cez Dockerfile a context checksums, builder a BuildKit frontend generation až po platform manifests a publikovaný OCI index digest. Test target, runtime target a multi-platform publication nesmú byť tri nesúvisiace jobs, ktoré iba používajú rovnaký tag; evidence sa viaže na rovnaké immutable inputs a dôveryhodný builder a cache domain.

Každý command nižšie vytvára alebo číta inú vrstvu dôkazu. `buildx inspect` identifikuje builder a workers, input checksums fixujú source subject, test build uzatvára test stage, registry exporter publikuje content-addressed graph a registry read-back potvrdí platform descriptors a digests. Úspešný push ešte nepreukazuje správny binary pre každú platformu ani funkčný runtime business path; to uzatvára platform-specific smoke alebo integration evidence naviazaná na manifest digest.""",
)

insert(
    "docker-compose.md",
    "## 5. Celý `payments-api` model",
    """Compose model skladá viac runtime subjects do jedného application graphu. `init-data` vlastní jednorazovú prípravu volume permissions a `api` vlastní application process a health contract. Networks, volumes, environment interpolation, image references a dependency conditions sa resolve-nú pred Engine mutation, preto sa musí najprv čítať výsledok `docker compose config`, nie iba source YAML.

Nasledujúci model oddeľuje privileged initializer od non-root aplikácie, persistent data od read-only root filesystemu a host publication od internal service DNS. `depends_on` určuje startup ordering, nie business readiness celej application. Acceptance preto pokračuje cez container identities, runtime image digests, health, service-to-service request, host-published request a volume persistence po replacement-e.""",
)

insert(
    "dockerfile.md",
    "## 15. `STOPSIGNAL`",
    """`STOPSIGNAL` zapisuje do image configu defaultný signal, ktorý runtime použije pri stop lifecycle, ak caller neurčí iný. Signal musí doraziť k skutočnému application PID 1; shell-form entrypoint alebo wrapper bez `exec` ho môže zachytiť alebo neforwardovať. Image metadata preto treba čítať spolu s runtime process tree.

Graceful shutdown vzniká až v aplikácii: prestane prijímať novú prácu, dokončí alebo bezpečne preruší in-flight operácie, flushne state a skončí pred timeoutom. `docker stop` plus exit code a business read-back testuje celý transition; samotná Dockerfile inštrukcia iba nastavuje default transport.""",
)

insert(
    "dockerfile.md",
    "## 16. Kompletný multi-stage Dockerfile",
    """Kompletný Dockerfile je jeden build graph s oddelenými source, test, build a runtime subjects. Pinned base digests, presný build context a automatic platform args určujú inputs každého node-u; cache reuse je platný iba pri rovnakých effective inputs a dôveryhodnom producerovi. Test stage musí skončiť pred publication a runtime stage kopíruje iba explicitný artifact a potrebný runtime content.

Výsledný image config definuje non-root user, exec-form process contract a stop signal, zatiaľ čo layers nesmú niesť compiler, source alebo credentials. Build acceptance preto číta stage logs, final history a config, binary platform a runtime smoke test. Syntakticky úspešný multi-stage build ešte nepreukazuje správny target architecture, TLS trust store ani business behavior.""",
)

insert(
    "multi-stage-builds.md",
    "## 16. Praktický graph pre `payments-api`",
    """Praktický graph používa shared `source` stage ako immutable predecessor pre samostatné `test` a `build` branches. `TARGETOS` a `TARGETARCH` viažu compiled artifact na requested platform, `debug` stage pridáva diagnostické tools iba pre controlled troubleshooting a `runtime` stage zostáva minimálny non-root release artifact. Stage name je build-graph identity, nie automatická security boundary.

Pipeline má najprv vykonať `test` target, potom buildnúť a inspectovať artifact pre každú platformu a až nakoniec publikovať runtime manifests a index. `COPY --from=build` preukazuje artifact handoff v jednom graph-e, ale source SHA, Dockerfile digest, builder a cache trust a final manifest digest musia zostať korelované. Runtime acceptance dopĺňa process start, TLS alebo network dependency a business endpoint.""",
)

print("Applied Section 08 build, Compose and Dockerfile depth pass.")
