from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "docs" / "08-container-fundamentals-and-docker" / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"


def replace_prefixed_line(path: Path, prefix: str, replacement: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [index for index, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one line starting with {prefix!r} in {path}, found {len(matches)}")
    lines[matches[0]] = replacement
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


replace_prefixed_line(
    README,
    "Celkový authoritative stav je **19/19",
    "Celkový authoritative stav je **19/19 chapter-by-chapter explanation-depth revalidation · Ready for user review**. Posledný preserve-first pass doplnil presné build/request/artifact boundaries v BuildKit a Buildx, resolved application model v Compose, signal/PID 1 a multi-stage graph v Dockerfile a create → inspect → start → host request → volume write/read → graceful stop → Compose reconciliation chain v praktickom walkthroughe. Existujúce Dockerfile, YAML, CLI, incidenty a runtime-verification kroky zostali zachované. Section 08 nemá critical ani high learning-depth findings. Repository workflow overuje dokumentačnú konzistenciu, navigation, glossary a audit; reálny Docker Engine, platform-native images, Buildx builder/cache, Compose runtime a registry publication neboli týmto passom vykonané. Stav preto neznamená používateľské `Accepted`, runtime `Verified` ani produkčné `Stable`.",
)

replace_prefixed_line(
    LEDGER,
    "| `08-container-fundamentals-and-docker`",
    "| `08-container-fundamentals-and-docker` — Container Fundamentals and Docker | 19/19 chapter-by-chapter explanation-depth revalidation | Ready for user review | 2026-08-01 | Všetkých 19 authoritative kapitol bolo znovu prečítaných podľa image/build/container/network/storage/security/Compose subjectu, mutation, read-back, failure a replacement štandardu. Existujúci plynulý `payments-api` výklad, Dockerfile/YAML/CLI, incidenty, practical walkthrough a troubleshooting zostali zachované. Cielený preserve-first pass doplnil BuildKit/Buildx chain od immutable inputs cez builder/cache trust po platform manifests a index digest; Compose resolved graph, initializer/application ownership a request-path acceptance; Dockerfile `STOPSIGNAL`, PID 1 a multi-stage artifact handoff; a practical create-before-start inspection, host-published loaded-generation oracle, volume-backed business read-back, graceful stop, Compose interpolation a `up --wait` proof boundary. Section 08 nemá critical ani high learning-depth findings. README, review ledger, navigation, glossary a full audit boli synchronizované. Docker Engine, native platform images, Buildx cache/publication, Compose runtime a registry neboli týmto documentation workflowom vykonané; sekcia je Ready for user review, nie runtime Verified ani používateľsky Accepted. |",
)

print("Finalized Section 08 README and review ledger.")
