from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "docs" / "11-cloud-and-aws" / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
AUDIT = ROOT / "DOCUMENTATION-AUDIT.md"


def replace_prefixed_line(path: Path, prefix: str, replacement: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one line starting with {prefix!r} in {path}, found {len(matches)}")
    lines[matches[0]] = replacement
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


if "### `docs/11-cloud-and-aws/" in AUDIT.read_text(encoding="utf-8"):
    raise RuntimeError("Section 11 still has critical/high learning-depth findings")

old_status = "Všetkých 30 authoritative kapitol vrátane samostatného AWS walkthroughu a troubleshooting kapitoly je pripravených na používateľskú kontrolu. Stav neznamená automatické používateľské schválenie, certifikačný výsledok ani runtime overenie labu v každom AWS account-e. SOA-C03 fakty a tool-specific syntax zostávajú viazané na uvedené official source a toolchain generation."
new_status = "Všetkých **30/30 authoritative kapitol prešlo chapter-by-chapter explanation-depth revalidation** a sekcia je `Ready for user review`. Posledný preserve-first pass uzavrel artifact/checksum, DynamoDB table, Lambda `$LATEST`, remote business read-back a acceptance boundaries v praktickom walkthroughe a caller-versus-workload identity v minimálnom incident manifeste. Existujúce AWS CLI flows, service chapters, incidents, recovery a cleanup zostali zachované. Section 11 nemá critical ani high learning-depth findings. Repository workflow overuje dokumentačnú konzistenciu, navigation, glossary a audit; reálne AWS resources, IAM propagation, Lambda runtime, DynamoDB writes, CloudTrail delivery, billing a cleanup neboli týmto passom vykonané. Stav preto neznamená používateľské `Accepted`, certifikačný výsledok, runtime `Verified` ani produkčné `Stable`. SOA-C03 fakty a tool-specific syntax zostávajú viazané na uvedené official source a toolchain generation."
readme = README.read_text(encoding="utf-8")
if old_status not in readme and new_status not in readme:
    raise RuntimeError("Expected Section 11 README status paragraph not found")
README.write_text(readme.replace(old_status, new_status, 1).rstrip() + "\n", encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `11-cloud-and-aws`",
    "| `11-cloud-and-aws` — Cloud and AWS | 30/30 chapter-by-chapter explanation-depth revalidation | Ready for user review | 2026-08-01 | Všetkých 30 authoritative kapitol bolo znovu prečítaných podľa account/region/principal/resource/request identity, control/data/recovery pathu, immutable release subjectu, business operation a cost/cleanup boundary. Core cloud a AWS service kapitoly už spĺňali prose-first štandard a zostali bez redundantného prepisu. Cielený pass doplnil exact ZIP artifact a `CodeSha256` boundary, DynamoDB table a conditional-operation contract, mutable Lambda `$LATEST` versus immutable version, consistent business read-back a layered acceptance v AWS practical walkthroughe; AWS troubleshooting doplnil minimálny incident manifest odlišujúci CLI caller identity od workload role/session generation. Section 11 nemá critical ani high learning-depth findings. README, review ledger, navigation, glossary a full audit boli synchronizované. Reálne AWS resources, IAM propagation, Lambda runtime, DynamoDB, telemetry delivery, billing a cleanup neboli týmto documentation workflowom vykonané; sekcia je Ready for user review, nie runtime Verified ani používateľsky Accepted. |",
)

print("Finalized Section 11 README and central review ledger.")
