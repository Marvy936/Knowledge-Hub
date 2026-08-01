from __future__ import annotations

import re
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected block not found in {path}: {old[:100]!r}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "docs/03-git-and-automation/bash-automation.md",
    "## Argument parser\n\n```bash\nwhile (($#)); do",
    """## Argument parser

Argument parser premieňa raw positional parameters na explicitný internal state skriptu. Musí spotrebovať presný počet arguments, odlíšiť flag od option s hodnotou a zastaviť sa na `--`, za ktorým už tokens neinterpretuje ako vlastné options. Parser success dokazuje iba syntakticky rozpoznaný CLI contract; existencia file-u, allowed environment a business constraints sa overujú až v ďalšej validačnej vrstve.

```bash
while (($#)); do""",
)

replace_once(
    "docs/03-git-and-automation/commit-branch-tag-head.md",
    "## Reflog ako lokálny pohyb refs\n\n```bash\ngit reflog show HEAD",
    """## Reflog ako lokálny pohyb refs

Reflog je lokálny append-oriented záznam o tom, na ktoré object IDs konkrétny ref alebo `HEAD` v tomto repository postupne ukazoval. Nezapisuje nový commit do zdieľanej histórie a neposiela sa fetchom ani pushom. Jeho hlavná dôkazná hodnota je recovery po reset-e, rebase alebo branch movement-e, kým príslušné objects ešte neboli odstránené garbage collection.

```bash
git reflog show HEAD""",
)

replace_once(
    "docs/03-git-and-automation/merge-conflicts.md",
    """## Three-way merge

Git porovnáva tri snapshots:

```text
merge base
ours
other side
```""",
    """## Three-way merge

Three-way merge nepáruje iba dva aktuálne files. Git najprv nájde spoločný ancestor snapshot, potom samostatne vypočíta zmenu z base do `ours` a z base do druhej strany. Konflikt vzniká tam, kde tieto dve delty nemožno bezpečne skombinovať podľa textového merge modelu; aj čistá kombinácia však môže byť domainovo nesprávna.

Git teda pracuje s tromi snapshots:

```text
merge base
ours
other side
```""",
)

replace_once(
    "docs/03-git-and-automation/reset-revert-restore.md",
    "### Odstageovanie\n\n```bash\ngit restore --source=HEAD --staged -- config/orders.yaml",
    """### Odstageovanie

Odstageovanie mení iba index entry pre zvolený path. Source snapshot je v tomto príklade `HEAD`, takže Git vloží do indexu blob identitu z aktuálneho commitu, ale pracovný file ponechá s používateľskými editmi. Operácia preto nemení históriu ani nestráca working-tree obsah; mení candidate snapshot budúceho commitu.

```bash
git restore --source=HEAD --staged -- config/orders.yaml""",
)

replace_once(
    "docs/03-git-and-automation/powershell-fundamentals.md",
    "## Parameter contract\n\n```powershell\n[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]",
    """## Parameter contract

Parameter contract je prvá boundary medzi callerom a automatizáciou. PowerShell binding priradí named alebo positional values, vykoná deklarované type conversions a validation attributes a až potom vstúpi do body skriptu. Táto fáza môže odmietnuť chýbajúci alebo syntakticky neplatný input, ale nepreukazuje, že file, remote subject alebo runtime precondition zostanú platné v okamihu mutation.

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]""",
)

replace_once(
    "docs/03-git-and-automation/powershell-fundamentals.md",
    "## Native processes\n\n```powershell\n& git diff --quiet",
    """## Native processes

Native executable nevytvára PowerShell error record rovnakým mechanizmom ako cmdlet. PowerShell spustí process, prepojí jeho standard streams a po ukončení sprístupní process exit code cez `$LASTEXITCODE`. Wrapper preto musí bezprostredne zachytiť command-specific code a samostatne rozhodnúť, či znamená success, očakávaný rozdiel alebo tool failure.

```powershell
& git diff --quiet""",
)

replace_once(
    "docs/03-git-and-automation/powershell-fundamentals.md",
    "## Mechanický rozbor kľúčových PowerShell vzorov\n\n### Object pipeline nie je vizuálna tabuľka",
    """## Mechanický rozbor kľúčových PowerShell vzorov

Nasledujúce rozbory sledujú každý vzor od parameter bindingu alebo object emission cez pipeline, error a serialization boundary až po mutation a read-back. Cieľom nie je zopakovať syntax, ale ukázať, ktorý runtime objekt alebo stream vznikne, čo môže ďalší krok skutočne použiť a kde sa úspešný PowerShell command ešte nesmie zameniť za verified outcome.

### Object pipeline nie je vizuálna tabuľka""",
)

replace_once(
    "docs/03-git-and-automation/python-for-automation.md",
    "## CLI boundary\n\n```python\nfrom __future__ import annotations",
    """## CLI boundary

CLI boundary prevádza process argument vector na syntakticky rozpoznaný command model a určuje, ktoré chyby patria callerovi. `argparse` môže potvrdiť prítomnosť options a vybrať subcommand, ale path ešte nie je canonical subject a string hodnota ešte nie je validný domain limit. Parser output sa preto odovzdá samostatnej resolution a validation vrstve namiesto priamej mutation.

```python
from __future__ import annotations""",
)

replace_once(
    "docs/03-git-and-automation/python-for-automation.md",
    "## Typed immutable model\n\n```python\nfrom dataclasses import dataclass",
    """## Typed immutable model

Typed domain model oddeľuje external representation od state-u, nad ktorým planning a verification skutočne rozhodujú. Loader musí najprv odmietnuť unknown fields, konvertovať hodnoty a overiť invariants; až potom vytvorí model. `frozen=True` chráni pred bežnou neskoršou assignment mutation, ale nenahrádza runtime validation ani deep immutability nested structures.

```python
from dataclasses import dataclass""",
)

replace_once(
    "docs/03-git-and-automation/python-for-automation.md",
    "## Canonical fingerprint\n\n```python\nimport hashlib",
    """## Canonical fingerprint

Fingerprint má identifikovať presne definovaný semantic subject, nie náhodnú textovú presentation. Automation najprv zostaví canonical representation so stabilným field setom, orderingom, encodingom a number semantics a až potom hashne výsledné bytes. Rovnaký digest dokazuje zhodu podľa tohto canonicalization contractu; nedokazuje pravdivosť inputu ani runtime aplikovanie state-u.

```python
import hashlib""",
)

replace_once(
    "docs/03-git-and-automation/python-for-automation.md",
    "## Atomic local write\n\n```python\nimport os",
    """## Atomic local write

Atomic local write oddeľuje prípravu nového obsahu od okamihu, keď sa stane viditeľným pod production pathname. Temporary file sa vytvorí na rovnakom filesysteme, úplne zapíše a flushne; `os.replace` potom jednou pathname transition nahradí target. Tento model bráni readers vidieť partial serialization, ale jeho crash durability, ownership, mode a následné runtime načítanie zostávajú samostatnými contracts.

```python
import os""",
)

replace_once(
    "docs/03-git-and-automation/python-for-automation.md",
    "## Mechanický rozbor Python automation ukážok\n\n### Parser vytvára syntaktický model, nie validný domain object",
    """## Mechanický rozbor Python automation ukážok

Nasledujúce rozbory spájajú skrátené ukážky s reálnym Python execution modelom. Pri každom vzore sledujú vznik objektu alebo file descriptoru, ownership a exception boundary, presnú mutation a read-back, ktorý výsledok potvrdzuje. Zároveň pomenúvajú to, čo lokálne úspešné volanie nepreukazuje pri concurrent writerovi, power loss, remote API alebo novej tool generation.

### Parser vytvára syntaktický model, nie validný domain object""",
)

replace_once(
    "docs/03-git-and-automation/yaml-json-regular-expressions.md",
    "## Mechanický rozbor parserov, serializácie a regex hraníc\n\n### Duplicate-key rejection v JSON",
    """## Mechanický rozbor parserov, serializácie a regex hraníc

Nasledujúce rozbory sledujú bytes cez decoding, parser a effective type model až po schema/domain validation, controlled serialization a platform read-back. Regex príklady sú zámerne vedené oddelene: engine pracuje nad textovým patternom a nevlastní syntax tree structured dokumentu. Každý rozbor preto pomenúva parser generation, vstupný subject, stratené informácie a failure, ktorý samotný parse success ešte nevylučuje.

### Duplicate-key rejection v JSON""",
)

# Practical walkthrough transition explanations.
replace_once(
    "docs/03-git-and-automation/git-automation-practical-walkthrough.md",
    "## 3. Dve samostatné clones\n\n```bash\ngit clone origin.git alice",
    """## 3. Dve samostatné clones

Clone vytvorí dve nezávislé local object databases, working trees, local branches a remote-tracking refs, hoci oba repositories začínajú z rovnakého remote snapshotu. Konfigurácia identity mení iba author/committer metadata budúcich commitov v danom clone. Po clone sa preto overí local `HEAD`, upstream binding a `origin/main`; existencia dvoch adresárov sama nepreukazuje rovnaký ref state.

```bash
git clone origin.git alice""",
)

replace_once(
    "docs/03-git-and-automation/git-automation-practical-walkthrough.md",
    "## 4. Alice vytvorí feature branch a object evidence\n\n```bash\ncd alice",
    """## 4. Alice vytvorí feature branch a object evidence

Alice najprv vytvorí nový movable ref na aktuálnom commite; Git nekopíruje file history ani object database. Následná editácia mení working tree, `hash-object -w` vytvorí content-addressed blob bez priradenia pathname a `git add` až potom zapíše blob identity do indexu pod konkrétnym pathom. Read-back po každom kroku odlišuje file content, loose alebo packed object, index entry a commit snapshot.

```bash
cd alice""",
)

replace_once(
    "docs/03-git-and-automation/git-automation-practical-walkthrough.md",
    "## 6. Alice dostane non-fast-forward a najprv pozoruje\n\n```bash\ncd ../alice",
    """## 6. Alice dostane non-fast-forward a najprv pozoruje

Alice local `main` a remote `main` teraz obsahujú rozdielne descendant commits. Non-fast-forward rejection je server-side ochrana pred presunutím remote refu na commit, ktorý by zahodil Bobovu viditeľnú históriu. Pred akoukoľvek integráciou Alice fetchne nové objects a aktualizuje iba local remote-tracking ref; graph a left/right comparison potom ukážu presné commits na každej strane bez mutation working history.

```bash
cd ../alice""",
)

replace_once(
    "docs/03-git-and-automation/git-automation-practical-walkthrough.md",
    "## 14. Commit automation change\n\n```bash\ngit add tools scripts tests schemas config .gitignore",
    """## 14. Commit automation change

Automation source, schemas, wrappers a tests tvoria jeden review subject a musia byť uložené v jednom konzistentnom commit snapshot-e. Staging read-back pred commitom potvrdí exact files a whitespace validity; po pushi sa local `HEAD`, local `origin/main` a remote branch porovnajú na rovnaký object ID. Clean working tree bez tejto ref identity by nepreukazoval, že publikovaný remote obsahuje testovanú generation.

```bash
git add tools scripts tests schemas config .gitignore""",
)

replace_once(
    "docs/03-git-and-automation/git-automation-practical-walkthrough.md",
    "## 16. Druhý no-op run\n\n```bash\n./scripts/release.sh --dry-run",
    """## 16. Druhý no-op run

Druhý run používa rovnaký desired fingerprint, znovu observe-ne current state a musí vytvoriť prázdnu delta. Dry-run a apply sa vykonajú ako dve samostatné operations, aby sa potvrdilo, že planner aj mutator rozpoznajú converged state. No-op sa dokazuje `changed: false`, rovnakým state fingerprintom a absenciou write-u, nie iba exit codeom nula.

```bash
./scripts/release.sh --dry-run""",
)

replace_once(
    "docs/03-git-and-automation/git-automation-practical-walkthrough.md",
    "## 17. Stale-plan failure\n\nVytvor plan:",
    """## 17. Stale-plan failure

Stale-plan test vytvorí plan nad konkrétnou desired a observed generation a potom zámerne zmení jeden z jeho preconditions. Apply musí pred mutation znovu načítať oba subjects, porovnať fingerprinty a skončiť stabilným precondition exit codeom. Test je úspešný iba vtedy, keď odmietnutie zachová pôvodný runtime state a nový plan by už obsahoval zmenený intent.

Vytvor plan:""",
)

# README and review ledger.
replace_once(
    "docs/03-git-and-automation/README.md",
    """## Stav

Všetkých pätnásť kapitol je po full prose rewritingu pripravených na používateľskú kontrolu. `Ready for user review` neznamená automatické používateľské schválenie ani overenie každého príkazu na každej platforme. Git/Python/Bash practical flow má samostatnú executable validation hranicu; PowerShell a hosting-specific protection rules zostávajú platformovou hranicou.
""",
    """## Stav

Všetkých pätnásť kapitol prešlo chapter-by-chapter explanation-depth revalidáciou. Existujúci object/state a code-mechanism základ zostal zachovaný; cielené doplnenia uzavreli code-first transitions pri Git reflogu, three-way merge, odstageovaní, Bash argument parseri, PowerShell parameter/native-process boundaries, Python CLI/model/fingerprint/atomic-write boundaries a YAML/JSON/regex parser modeloch. Praktický walkthrough teraz explicitnejšie oddeľuje clone state, blob/index/commit transition, non-fast-forward evidence, publikovaný automation subject, second no-op operation a stale-plan rejection.

Sekcia je pripravená na používateľskú kontrolu. `Ready for user review` neznamená automatické používateľské schválenie ani overenie každého príkazu na každej platforme. Git/Python/Bash practical flow má samostatnú executable validation hranicu; PowerShell a hosting-specific protection rules zostávajú platformovou hranicou.
""",
)

ledger = Path("DOCUMENTATION-REVIEW-STATUS.md")
text = ledger.read_text(encoding="utf-8")
pattern = re.compile(r"^\| `03-git-and-automation` — Git and Automation Basics \|.*$", re.MULTILINE)
replacement = "| `03-git-and-automation` — Git and Automation Basics | 15/15 chapter-by-chapter explanation-depth revalidation | Ready for user review | 2026-08-01 | Všetkých 15 kapitol bolo znovu prečítaných podľa subject/state/mutation/read-back/failure/recovery štandardu. Existujúci Git object/ref model a detailné Bash, PowerShell, Python a structured-data rozbory zostali zachované. Cielený pass doplnil chýbajúce úvody nadradených mechanických blokov, parser a native-process boundaries, canonical fingerprint a atomic-write contracts, reflog/three-way/index transitions a praktický chain clone → object/index/commit → non-fast-forward observation → publikovaný automation subject → second no-op → stale-plan refusal. README, review ledger, navigation, glossary a full audit boli synchronizované. Sekcia je Ready for user review, nie automaticky runtime Verified ani používateľsky Accepted. |"
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise RuntimeError("Section 03 ledger row not found exactly once")
ledger.write_text(text, encoding="utf-8")

print("Section 03 explanation-depth updates applied.")
