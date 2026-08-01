from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "11-cloud-and-aws"


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
    "aws-practical-walkthrough.md",
    "## 2. Reprodukovateľný zip a lokálny checksum",
    """Lambda deployment package je immutable input až vtedy, keď rovnaký source a build procedure vytvoria rovnaké bytes. Exact artifact subject preto zahŕňa source revision, runtime a dependency set, archive file order, timestamps a metadata normalization. Lokálny hex alebo base64 SHA-256 identifikuje konkrétny `function.zip`; názov súboru ani pipeline job identity nestačia.

Nasledujúci build odstráni ZIP extra fields a stabilizuje timestamp, potom vytvorí dve reprezentácie rovnakého digestu. Hex checksum je vhodný pre local evidence a base64 hodnota sa porovnáva s Lambda `CodeSha256`. Zhoda preukazuje, že AWS eviduje rovnaký uploadnutý ZIP payload; nepreukazuje správnu handler configuration, runtime compatibility, execution role ani business behavior.""",
)

insert(
    "aws-practical-walkthrough.md",
    "## 3. DynamoDB table",
    """DynamoDB table je durable business-state subject pre operation IDs, nie iba prerequisite Lambda funkcie. Table name, account, region, partition key schema a billing mode tvoria ownership a cost boundary. Partition key `operationId` umožní conditional create a následný consistent read rovnakého business subjectu; zmena key schema by vytvorila iný deduplication contract.

`create-table` mutuje control plane a `table-exists` čaká na service-reported availability. Následný `describe-table` read-back zachová ARN, ktorý sa použije v IAM policy a evidence. Available table ešte nepreukazuje, že Lambda execution role smie čítať alebo zapisovať, že conditional expression funguje ani že business item prežije retry bez duplicity.""",
)

insert(
    "aws-practical-walkthrough.md",
    "## 5. Vytvorenie Lambda `$LATEST`",
    """`$LATEST` je mutable working generation funkcie, do ktorej sa spájajú code bytes, runtime, handler, execution role, timeout, memory, environment a logging configuration. Vytvorenie funkcie preto musí viazať lokálny artifact digest na exact account, region, function name a role ARN. `$LATEST` ešte nie je immutable release subject a nemá sa používať ako stabilný production traffic target.

`create-function` zapisuje control-plane configuration a uploaduje code. Waiter uzatvára iba service state transition do active generation. `get-function` následne číta `CodeSha256`, `RevisionId`, runtime, role a environment a porovnáva ich s local evidence. Až publication vytvorí immutable numbered version; invocation a business read-back potom dokazujú runtime a application outcome.""",
)

insert(
    "aws-practical-walkthrough.md",
    "## 8. DynamoDB remote read-back",
    """Remote read-back používa rovnaký table subject a business `operationId`, ktorý niesli obe Lambda invocations. `--consistent-read` žiada strongly consistent observation v regione table, aby sa acceptance neopierala o prípadne oneskorenú eventual read. Výsledok sa koreluje s `authorizationId`, amount, release ID a response outcomes.

Jeden item podporuje tvrdenie, že conditional write nevytvoril druhý business result pre tento operation key. Nehovorí, koľko invocation attempts, throttles alebo failed writes nastalo a nepreukazuje všeobecnú exactly-once garanciu mimo definovaného idempotency contractu. Tieto hranice dopĺňajú structured Lambda logs, AWS request IDs a CloudTrail management evidence.""",
)

insert(
    "aws-practical-walkthrough.md",
    "## Acceptance walkthroughu",
    """Acceptance je evidence matrix nad jedným sandbox lab subjectom. Každý riadok nižšie musí byť naviazaný na rovnaký account, region, artifact digest, function version, alias revision, table a business operation ID. Úspech jednej vrstvy sa neprenáša automaticky na ďalšiu: control-plane creation, immutable publication, alias exposure, runtime execution, durable business state, audit evidence a cleanup sú samostatné verdicts.

Checklist zároveň definuje negatívnu hranicu. Walkthrough nepreukazuje production concurrency, multi-region recovery, organization-wide policy, reserved concurrency, VPC networking ani dlhodobú cost optimalizáciu. Preukazuje iba explicitné transitions a forbidden outcomes vykonané v tomto cost-bounded sandboxe vrátane broken candidate isolation, compare-and-swap alias recovery, retry idempotency a resource-deletion read-backu.""",
)

insert(
    "aws-troubleshooting.md",
    "## Minimálny incident manifest",
    """Incident manifest fixuje identity skôr, než sa symptoms interpretujú alebo začne containment. AWS CLI profile a shell region sú iba klientsky context; authoritative subject vzniká až z STS caller identity, partition, account, region, resource ARN alebo ID, request ID a relevantnej configuration alebo artifact generation. Pri assumed role sa zaznamenáva aj session name, source identity, credential expiry a session policy boundary.

Manifest musí odlíšiť caller identity od workload identity. Operátor môže používať správny account, zatiaľ čo Lambda, EC2 instance profile, ECS task role alebo EKS Pod používa inú principal generation. Zozbierané network, KMS, deployment a business fields vytvoria korelačný contract pre CloudTrail, CloudWatch a service-native read-back; samotný zoznam resource names bez UTC timeline a immutable IDs nie je incident subject.""",
)

print("Applied targeted preserve-first Section 11 explanation-depth pass.")
