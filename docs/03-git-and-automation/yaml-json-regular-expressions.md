# YAML, JSON a regular expressions

YAML a JSON sú serializačné formáty používané v konfigurácii, API kontraktoch, CI/CD pipelines a Infrastructure as Code. Regular expressions sú pattern language na rozpoznávanie a transformáciu textu. V automatizácii sa často používajú spolu, ale riešia odlišné problémy: parser rekonštruuje štruktúrované dáta podľa gramatiky, regex vyhľadáva text zodpovedajúci patternu.

## 1. Základný mentálny model

Použi najvyššiu dostupnú abstrakciu:

```text
structured JSON/YAML → parser → schema → business validation
line-oriented stable text → delimiter/parser alebo regex
human display output → nestabilný automation input
```

Bezpečný processing lifecycle:

```text
read bounded bytes with explicit encoding
  ↓
parse with configured safe parser
  ↓
reject ambiguous or unsupported constructs
  ↓
validate structural schema
  ↓
normalize explicit fields
  ↓
validate cross-field business rules
  ↓
calculate desired change
  ↓
serialize deterministically
  ↓
parse and validate rendered output again
  ↓
apply and verify runtime result
```

Každá fáza rieši inú triedu chýb. Syntakticky platný dokument môže byť schema-invalid. Schema-valid dokument môže byť prevádzkovo nebezpečný.

## 2. Parser nie je validator

Parser odpovedá najmä na otázku:

```text
Dá sa tento byte stream interpretovať ako dokument daného formátu?
```

Schema validator odpovedá:

```text
Má dokument očakávaný shape, typy a lokálne constraints?
```

Business validation odpovedá:

```text
Je konfigurácia povolená a zmysluplná v konkrétnom systéme?
```

Príklad:

```yaml
replicas: 1000000
```

Dokument môže byť syntakticky aj schema-valid, ale prevádzkovo neprijateľný kvôli capacity alebo policy limitu.

# JSON

## 3. JSON data model

JSON podporuje šesť kategórií hodnôt:

- **object** — neusporiadaná kolekcia string keys a hodnôt,
- **array** — usporiadaná sekvencia hodnôt,
- **string** — Unicode text reprezentovaný JSON escape pravidlami,
- **number** — numerický token bez univerzálneho runtime typu,
- **boolean** — `true` alebo `false`,
- **null** — explicitná nulová hodnota.

```json
{
  "service": "api",
  "replicas": 3,
  "enabled": true,
  "tags": ["public", "critical"],
  "limits": null
}
```

JSON object key je vždy string. Poradie properties nemá byť business contract, hoci konkrétny parser alebo serializer ho môže zachovať.

## 4. JSON syntax

JSON vyžaduje:

- double quotes pre strings a object keys,
- presné literals `true`, `false`, `null`,
- žiadne comments,
- žiadne trailing commas,
- správne escape sequences,
- jeden top-level JSON value.

Neplatný JSON:

```json
{
  'service': 'api',
  "replicas": 3,
}
```

Formáty ako JSON5 alebo JSONC majú iné gramatiky. Consumer musí explicitne deklarovať, ktorý formát prijíma.

## 5. JSON encoding a Unicode

JSON prenášaný medzi systémami má štandardne používať UTF-8. Pri práci so súbormi vždy nastav encoding explicitne.

Riziká:

- neplatné UTF-8 bytes,
- neočakávaný BOM,
- rozdielne Unicode normalization forms,
- escaped surrogate pairs,
- zámenné vizuálne znaky,
- chybný HTTP `Content-Type` alebo charset.

Dve vizuálne rovnaké strings nemusia mať rovnakú byte alebo code-point reprezentáciu. Ak identifikátor tvorí security boundary, definuj allowed alphabet a normalization policy.

## 6. JSON numbers

JSON syntax nerozlišuje univerzálny integer, decimal a binary floating-point runtime typ. Consumer rozhoduje, ako token reprezentuje.

Riziká:

- veľký integer stratí presnosť v prostredí s IEEE-754 `double`,
- desatinná hodnota sa zaokrúhli,
- `1`, `1.0` a `1e0` môžu mať rozdielnu canonical formu,
- `NaN` a infinity nie sú štandardné JSON numbers,
- ID reprezentované číslom môže zmeniť hodnotu alebo odstrániť leading zeros.

Identifikátory, telefónne čísla, account numbers a presné decimal hodnoty majú často byť strings s explicitnou schema semantics.

## 7. Absent, `null` a empty hodnoty

Nasledujúce stavy nie sú ekvivalentné:

```json
{}
```

```json
{"value": null}
```

```json
{"value": ""}
```

```json
{"value": []}
```

```json
{"value": false}
```

Schema a business contract musia definovať:

- či absent field aktivuje default,
- či `null` znamená odstrániť, zdediť alebo neznámu hodnotu,
- či empty collection je validná,
- či `false` a `0` sú explicitné hodnoty, nie „missing“.

## 8. Duplicate JSON object keys

JSON document môže textovo obsahovať rovnaký key viackrát:

```json
{
  "replicas": 2,
  "replicas": 5
}
```

Interoperabilita je nebezpečná, pretože parsers môžu:

- ponechať poslednú hodnotu,
- ponechať prvú hodnotu,
- zachovať všetky páry v špeciálnej štruktúre,
- zlyhať.

Pre config, podpisovanie a security-sensitive payloady majú byť duplicate keys validation error. Inak môžu dve vrstvy systému interpretovať ten istý dokument rozdielne.

Python parser možno nakonfigurovať cez `object_pairs_hook`, ak potrebuješ explicitne detegovať duplicity.

## 9. JSON parsing

Python:

```python
import json
from pathlib import Path

with Path("config.json").open(encoding="utf-8") as handle:
    data = json.load(handle)
```

PowerShell:

```powershell
$data = Get-Content config.json -Raw -Encoding utf8 | ConvertFrom-Json
```

Bash s `jq`:

```bash
jq -e '.service == "api" and (.replicas | type == "number")' config.json
```

Parser output je nedôveryhodný generic object. Pred použitím ho validuj a prelož do doménového modelu.

## 10. JSON serialization

Python:

```python
output = json.dumps(
    data,
    ensure_ascii=False,
    indent=2,
    sort_keys=True,
) + "\n"
```

PowerShell:

```powershell
$data | ConvertTo-Json -Depth 20
```

Pri serializácii definuj:

- encoding,
- newline na konci súboru,
- indentation,
- key ordering, ak sa používa,
- decimal a datetime reprezentáciu,
- Unicode escaping,
- maximum nesting depth,
- správanie pri neznámom type.

`ConvertTo-Json -Depth` môže pri príliš malej hodnote skrátiť nested štruktúru. Serializer output treba testovať, nie iba vizuálne prezrieť.

## 11. Deterministic serialization verzus canonicalization

Stabilné formatovanie znižuje diff noise, ale nie je automaticky kryptografická canonicalization.

```text
stable pretty output
≠
canonical bytes defined by a standard
```

Pre hashing alebo signing musí producer aj verifier používať rovnaký canonicalization štandard vrátane:

- property ordering,
- number normalization,
- Unicode escaping,
- whitespace,
- duplicate-key policy.

„Sort keys“ samo osebe nestačí.

## 12. JSON Schema

JSON Schema môže definovať shape a lokálne constraints:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["service", "replicas"],
  "properties": {
    "service": {
      "type": "string",
      "pattern": "^[a-z][a-z0-9-]{2,31}$"
    },
    "replicas": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100
    }
  },
  "additionalProperties": false
}
```

Dôležité je deklarovať schema draft. Keywords a ich semantics sa medzi draftmi môžu líšiť.

Schema neoverí automaticky:

- či service existuje,
- či je port dostupný,
- či má používateľ oprávnenie,
- či capacity stačí,
- či kombinácia s iným dokumentom dáva zmysel,
- či consumer skutočne používa tú istú schema version.

## 13. Unknown fields a compatibility

`additionalProperties: false` odhalí preklepy a nečakané polia. Zároveň môže zablokovať forward-compatible rollout, keď nový producer pridá pole skôr, než sa aktualizuje starý consumer.

Policy musí určiť:

- ktoré objekty sú strict,
- ktoré tolerujú unknown fields,
- či sa unknown fields zachovajú pri read-modify-write,
- ako sa označujú deprecated fields,
- aký je producer/consumer rollout order.

# YAML

## 14. YAML data model

YAML dokument typicky používa:

- **mapping** — key/value kolekcia,
- **sequence** — usporiadaný zoznam,
- **scalar** — string, number, boolean, null alebo parser-specific typ.

```yaml
service: api
replicas: 3
enabled: true
tags:
  - public
  - critical
limits: null
```

Indentation je syntax. Tab characters sa nemajú používať na indentation.

## 15. YAML stream a documents

Jeden YAML stream môže obsahovať viac documents:

```yaml
---
service: api
---
service: worker
```

Consumer musí explicitne vedieť, či očakáva:

- presne jeden dokument,
- zero alebo jeden,
- viac dokumentov,
- stream spracovaný postupne.

Použitie single-document loadera na multi-document input môže zlyhať alebo ignorovať časť vstupu podľa knižnice.

## 16. YAML 1.1 a YAML 1.2

YAML typing sa môže líšiť podľa verzie a parser schema.

Historické YAML 1.1 parsers môžu interpretovať hodnoty ako:

```yaml
feature: on
answer: yes
```

ako booleans. YAML 1.2 core schema je bližšie JSON literals, ale implementácie nie sú jednotné.

Pre portability cituj nejednoznačné scalars:

```yaml
feature: "on"
answer: "yes"
version: "1.0"
date: "2026-07-24"
```

Consumer version a parser configuration sú súčasť formátového kontraktu.

## 17. Plain, single-quoted a double-quoted scalars

Plain scalar:

```yaml
name: api
```

Single-quoted scalar interpretuje minimum escape syntaxe:

```yaml
pattern: '^api-[0-9]+$'
```

Double-quoted scalar interpretuje YAML escape sequences:

```yaml
message: "line one\nline two"
```

Pri regexoch a Windows paths je single quote často čitateľnejší. Vždy však rozlišuj YAML quoting od regex, shell alebo template escaping vrstvy.

## 18. Block scalars

Literal block zachováva riadkovú štruktúru:

```yaml
script: |
  set -e
  echo "start"
  run-task
```

Folded block väčšinu line breaks skladá do spaces:

```yaml
description: >
  This is a long
  description represented as
  one logical paragraph.
```

Chomping indicators určujú trailing newlines:

- `|-` — odstráni trailing newline,
- `|` — ponechá jeden trailing newline,
- `|+` — zachová ďalšie trailing newlines.

Pri embedded scripts môže jediný newline meniť behavior alebo hash artifactu.

## 19. Anchors a aliases

```yaml
defaults: &defaults
  timeout: 10
  retries: 3

api:
  <<: *defaults
  port: 8080
```

Anchor označí node a alias naň odkazuje. Po parse môžu aliasy reprezentovať zdieľanú object identity alebo skopírovanú hodnotu podľa knižnice a následného spracovania.

Riziká:

- znížená lokálna čitateľnosť,
- zložité override semantics,
- tooling bez plnej podpory,
- prekvapenie pri mutation parsed objectu,
- veľká expanzia aliases.

## 20. Merge key portability

Syntax `<<` sa široko používa, ale merge-key behavior nie je univerzálne podporovaný ako rovnaký core feature vo všetkých YAML consumers.

Pred použitím over:

- parser implementation,
- platform schema pipeline,
- duplicate/override precedence,
- serializer round-trip behavior.

Konfigurácia určená pre viac nástrojov má preferovať jednoduchší portable subset.

## 21. Alias expansion a resource exhaustion

Škodlivý YAML môže vytvoriť veľké množstvo alias-expanded štruktúr alebo hlboké nesting. Aj safe loader môže potrebovať limity na:

- input bytes,
- document count,
- nesting depth,
- alias count,
- expanded node count,
- parse duration.

„Safe“ často znamená zákaz vytvárania ľubovoľných language objects, nie automatickú ochranu proti všetkým denial-of-service vstupom.

## 22. Tags a unsafe deserialization

YAML tags môžu určovať explicitný typ. Niektoré language-specific loaders historicky umožňovali konštrukciu objektov alebo vykonanie nebezpečných code paths.

Python:

```python
import yaml

data = yaml.safe_load(content)
```

Nedôveryhodný input nikdy nenačítavaj cez unsafe/general object loader. Aj pri safe loaderi následne validuj expected primitive structure.

## 23. Duplicate YAML keys

```yaml
replicas: 2
replicas: 5
```

Parsers môžu použiť poslednú hodnotu, prvú hodnotu alebo zlyhať. Duplicate keys majú byť explicitne odmietnuté, najmä pri:

- security policy,
- Kubernetes a IaC manifests,
- CI configuration,
- signed config,
- config override vrstve.

Lint nestačí, ak produkčný parser používa odlišné semantics. Validation má používať rovnaký parser model ako runtime alebo prísnejší kompatibilný model.

## 24. YAML nie je template language

Čistý YAML:

```yaml
image: app:1.2.3
replicas: 3
```

Template source:

```yaml
image: {{ image_repository }}:{{ image_tag }}
```

Template source nemusí byť platný YAML. Diagnostický lifecycle je:

```text
template source
→ template input values
→ rendered text
→ YAML parser
→ structural schema
→ platform validation/admission
→ runtime behavior
```

Kontroluj a uchovávaj rendered output, pretože to je skutočný vstup parsera a platformy.

## 25. Templating security

Riziká templatingu:

- string injection naruší YAML štruktúru,
- nesprávne quoting zmení typ,
- secret sa objaví v rendered artifacte alebo logu,
- template function vykonáva nečakané I/O,
- hodnoty sa interpretujú druhýkrát v shelli alebo inom jazyku,
- environment-specific default vytvorí drift.

Preferuj structured value injection alebo serializer namiesto ručného skladania YAML stringov.

## 26. YAML parsing a round-trip

Bežný parser môže stratiť:

- comments,
- pôvodné quoting,
- anchor names,
- key ordering,
- exact block style,
- whitespace.

Ak nástroj upravuje human-maintained YAML, treba rozhodnúť, či:

- generuje celý súbor zo source of truth,
- používa round-trip parser,
- aplikuje structured patch,
- mení iba explicitne vlastnenú sekciu.

Generic parse-modify-serialize môže vytvoriť veľký formatting diff.

## 27. YAML schema a platform validation

Syntaktická kontrola:

```bash
yamllint config.yaml
yq '.' config.yaml
```

Kubernetes server-side validation:

```bash
kubectl apply --dry-run=server -f manifest.yaml
```

Validácia má typicky viac vrstiev:

```text
YAML syntax
→ Kubernetes/OpenAPI schema
→ admission policy
→ referential dependencies
→ rendered diff/plan
→ runtime reconciliation
```

Client-side parser nevie overiť server-side admission, CRD version alebo aktuálnu cluster policy.

## 28. JSON verzus YAML

| Vlastnosť | JSON | YAML |
|---|---|---|
| Primárny model | machine interchange | human-authored configuration |
| Syntax | explicitná | flexibilná a indentation-based |
| Comments | nie | áno |
| Implicit typing | obmedzené | závisí od verzie/schema |
| Multi-document stream | nie | áno |
| Anchors a aliases | nie | áno |
| Parser complexity | nižšia | vyššia |
| Round-trip comments/style | nerelevantné | môže byť dôležité |

JSON je často vhodnejší pre wire contract a generated artifacts. YAML je pohodlnejší pre ručne udržiavanú konfiguráciu, ale potrebuje prísnejší parser a validation discipline.

## 29. Configuration merge a precedence

Ak systém kombinuje viac config sources:

```text
defaults
< shared file
< environment-specific file
< environment variables
< CLI arguments
```

Musí byť definované:

- deep merge verzus whole-value replacement,
- array append verzus replacement,
- semantics `null`,
- delete/unset marker,
- duplicate key handling,
- provenance každej výslednej hodnoty,
- secret redaction.

„Merge YAML files“ nie je jednoznačná operácia bez merge contractu.

## 30. Schema evolution

Pri zmene formátu rieš:

- explicitnú schema/version identity,
- backward a forward compatibility,
- unknown fields,
- default values,
- field rename a deprecation,
- migration tooling,
- producer/consumer rollout order,
- round-trip zachovanie dát,
- sunset policy.

Breaking zmena môže vzniknúť aj sprísnením patternu, zmenou defaultu alebo prechodom z absent na required field.

# Regular expressions

## 31. Regex ako jazyk patternov

Regex definuje množinu textov alebo častí textu zodpovedajúcich patternu.

```regex
^[a-z][a-z0-9-]{2,31}$
```

Pattern môže slúžiť na:

- validation tvaru,
- extraction hodnôt,
- search,
- replace,
- tokenization jednoduchého stabilného formátu.

Regex nie je vhodný ako náhrada parsera pre nested alebo kontextovú gramatiku.

## 32. Regex dialect je súčasť kontraktu

Engines sa líšia v podpore a semantics:

- POSIX BRE,
- POSIX ERE,
- Python `re`,
- .NET regex,
- JavaScript regex,
- PCRE/PCRE2,
- RE2-like linear-time engines,
- Bash `=~`,
- `grep`, `sed` a `awk` varianty.

Rozdiely zahŕňajú:

- named-group syntax,
- lookbehind,
- backreferences,
- lazy/possessive quantifiers,
- atomic groups,
- Unicode classes,
- anchors,
- timeout alebo linear-time guarantees.

Pattern bez pomenovania engine a flags nie je úplná špecifikácia.

## 33. Základné prvky

```text
.         ľubovoľný znak podľa DOTALL/newline semantics
^         začiatok inputu alebo riadku podľa multiline mode
$         koniec inputu/riadku; niekedy aj pred trailing newline
*         0 alebo viac
+         1 alebo viac
?         0 alebo 1; pri quantifieri môže znamenať lazy variant
{m,n}     rozsah počtu opakovaní
[abc]     character class
[^abc]    negovaná character class
(...)     capturing group
(?:...)   non-capturing group
|         alternation
\d        digit podľa engine/Unicode semantics
\s        whitespace podľa engine semantics
\w        word character podľa engine semantics
```

Metacharacter má špeciálny význam iba v konkrétnom syntaktickom kontexte.

## 34. Search, match a full match

Tri rozdielne operácie:

- **search** — nájdi match kdekoľvek v inpute,
- **prefix match** — match musí začínať na začiatku,
- **full match** — celý input musí zodpovedať patternu.

Python:

```python
import re

NAME_RE = re.compile(r"[a-z][a-z0-9-]{2,31}")

NAME_RE.search(value)
NAME_RE.match(value)
NAME_RE.fullmatch(value)
```

Pre validation preferuj API typu `fullmatch()`, ak ho engine poskytuje. Znižuje závislosť od nejednoznačných anchor semantics.

## 35. Anchors

Bežné anchors:

```regex
^[0-9]+$
```

`^` a `$` môžu pri multiline flagu znamenať začiatok a koniec každého riadku. `$` môže v niektorých engines matchnúť aj pred trailing newline.

Niektoré engines poskytujú absolútne anchors ako `\A`, `\z` alebo `\Z`, ale ich názvy a semantics sa líšia. Pre security validation používaj engine-specific full-match API alebo presne zdokumentované absolute anchors.

## 36. Flags menia jazyk patternu

Typické flags:

- case-insensitive,
- multiline,
- dot-all/singleline,
- verbose/free-spacing,
- ASCII verzus Unicode,
- culture-invariant podľa engine.

Pattern a flags musia byť reviewované spolu. `.` bez DOTALL typicky nematchuje newline. `^` a `$` s multiline menia rozsah validácie.

## 37. Character classes a ranges

```regex
[a-z0-9-]
```

Explicitná ASCII class je vhodná, keď allowed alphabet tvorí kontrakt.

`\w` môže podľa engine zahŕňať:

- ASCII letters, digits a underscore,
- širšie Unicode letters a digits,
- culture-specific kategórie.

Range semantics môžu závisieť od Unicode alebo locale modelu nástroja. Nepoužívaj neurčitú class pre security-sensitive identifier, ak potrebuješ presný alphabet.

## 38. Groups a captures

Non-capturing group:

```regex
^(?:dev|test|prod)-[0-9]+$
```

Named capture v .NET:

```regex
^(?<name>[a-z0-9-]+):(?<tag>[a-zA-Z0-9._-]+)$
```

Named capture v Pythone:

```regex
^(?P<name>[a-z0-9-]+):(?P<tag>[a-zA-Z0-9._-]+)$
```

Capture iba hodnoty, ktoré downstream logika potrebuje. Zbytočné captures komplikujú numbering a môžu mať performance overhead.

## 39. Alternation precedence

Pattern:

```regex
^cat|dog$
```

typicky znamená:

```text
(^cat) OR (dog$)
```

Nie celý input `cat` alebo `dog`. Správne grouping:

```regex
^(?:cat|dog)$
```

Alternation má nižšiu precedence než väčšina sekvenčných prvkov. Chýbajúce grouping je častý validation bug.

## 40. Greedy, lazy a possessive quantifiers

Greedy:

```regex
<.*>
```

sa snaží match rozšíriť čo najďalej a potom backtrackuje.

Lazy:

```regex
<.*?>
```

sa snaží začať najkratším matchom, ale stále môže backtrackovať.

Possessive quantifier alebo atomic group, ak ich engine podporuje, môže zabrániť spätnému uvoľneniu matchu.

Žiadny variant nerobí regex vhodným parserom HTML alebo nested markup.

## 41. Backreferences

Backreference vyžaduje, aby neskoršia časť zopakovala text zachytený groupou:

```regex
^(\w+)\s+\1$
```

Backreferences zvyšujú expressive power, ale často znemožňujú linear-time engine a komplikujú performance analýzu. RE2-like engines ich typicky nepodporujú.

## 42. Lookaround

Positive lookahead:

```regex
^(?=.*[A-Z])(?=.*[0-9]).{12,}$
```

Lookahead a lookbehind kontrolujú kontext bez spotrebovania znakov. Podpora lookbehindu, variabilnej dĺžky a performance semantics sa medzi engines výrazne líši.

Pri password policy regex často vytvára zložitú, ťažko vysvetliteľnú validation logiku. Viaceré explicitné kontroly v kóde bývajú čitateľnejšie a bezpečnejšie.

## 43. Unicode a normalization

Pred matchingom rozhodni:

- či akceptuješ iba ASCII,
- či normalizuješ NFC/NFKC alebo inú formu,
- či case folding používa locale alebo invariant model,
- či povoľuješ combining marks,
- či vizuálne podobné znaky predstavujú riziko,
- či length limit počíta bytes, code points alebo grapheme clusters.

Normalizácia pred validáciou mení security semantics. Producer aj consumer musia používať konzistentný model.

## 44. Escaping vrstvy

Regex môže prechádzať viacerými jazykmi:

```text
regex syntax
→ programming-language string literal
→ JSON/YAML string
→ shell quoting
→ template rendering
```

Raw regex:

```regex
^\d+\.\d+$
```

Python raw string:

```python
pattern = r"^\d+\.\d+$"
```

JSON string:

```json
{"pattern": "^\\d+\\.\\d+$"}
```

YAML single-quoted scalar:

```yaml
pattern: '^\d+\.\d+$'
```

Debugging musí určiť, ktorá vrstva spotrebovala alebo pridala backslash.

## 45. Regex v Pythone

```python
import re

NAME_RE = re.compile(r"[a-z][a-z0-9-]{2,31}", flags=re.ASCII)


def is_valid_name(value: str) -> bool:
    return NAME_RE.fullmatch(value) is not None
```

Compile pattern pri opakovanom použití. Explicitné `re.ASCII` alebo Unicode semantics dokumentujú allowed character model.

Python štandardný `re` engine nemá univerzálny per-match timeout. Pri nedôveryhodnom vstupe používaj jednoduché patterns, limit dĺžky alebo engine/knižnicu s vhodným runtime modelom.

## 46. Regex v PowerShelli

```powershell
if ($Name -cmatch '^[a-z][a-z0-9-]{2,31}$') {
    $Matches[0]
}
```

`-match` je štandardne case-insensitive; `-cmatch` je case-sensitive.

`$Matches` je implicitný mutable state. Po neúspešnom matchi sa nespoliehaj na jeho predchádzajúci obsah. Najprv over boolean výsledok a captures použi okamžite v tom istom control flowe.

.NET regex podporuje timeout pri vytvorení `Regex` objektu. Pre input kontrolovaný používateľom má byť timeout súčasť threat modelu.

## 47. Regex v Bash

```bash
pattern='^[a-z][a-z0-9-]{2,31}$'
if [[ $name =~ $pattern ]]; then
  printf 'valid\n'
fi
```

Bash `=~` používa vlastné ERE-like semantics. Quoting pravej strany menilo medzi verziami behavior a môže zmeniť metacharacters na literals. Pattern v premennej je často čitateľnejší.

Captures sú dostupné cez `BASH_REMATCH`, ktoré je globálne shell state a môže byť prepísané ďalším matchom.

## 48. `grep`, `sed` a `awk`

```bash
grep -E '^[0-9]+$' input.txt
sed -E 's/^([a-z]+)=/\1: /' input.txt
awk -F= '$1 == "port" { print $2 }' config.env
```

Rozlišuj:

- POSIX basic regex,
- POSIX extended regex,
- PCRE mode,
- GNU/BSD/BusyBox implementáciu,
- locale a binary/text mode.

CLI option s podobným názvom nemusí mať rovnakú podporu na všetkých platformách.

## 49. Validation verzus extraction

Validation pattern:

```regex
^[0-9]{1,5}$
```

Extraction pattern:

```regex
status=(?<status>[0-9]{3})
```

Validation tvaru nenahrádza semantic validation. Port `99999` zodpovedá prvému patternu, ale nie je platný TCP/UDP port.

Odporúčaný postup:

```text
match exact lexical shape
→ convert to domain type
→ validate range and cross-field rules
```

## 50. Catastrophic backtracking

Problematický pattern:

```regex
^(a+)+$
```

Pri dlhom non-matching inpute môže backtracking engine skúšať exponenciálne množstvo partition možností.

Rizikové konštrukcie:

- nested quantifiers,
- ambiguous alternation,
- opakované groups s prekrývajúcimi sa matches,
- veľké `.*` okolo ďalších constraints,
- backreferences s nejasným rozsahom.

## 51. ReDoS

Regular Expression Denial of Service vznikne, keď útočník kontroluje input a pattern má patologický runtime alebo memory behavior.

Ochrany:

- limit input length pred regexom,
- jednoduchší jednoznačný pattern,
- linear-time engine,
- match timeout,
- bounded concurrency,
- adversarial performance tests,
- nepovoľovať user-supplied patterns bez sandbox/limit modelu.

Regex v request validation path je security-sensitive code.

## 52. Regex nie je univerzálny parser

Regexom neparsuj:

- nested JSON alebo YAML,
- HTML/DOM,
- programovací jazyk,
- komplexné CSV quoting,
- recursive expressions,
- protocol s escape a nesting grammar.

Použi parser, ktorý pozná grammar, escaping a nesting.

## 53. Secrets a citlivá konfigurácia

YAML/JSON files často obsahujú credentials alebo references na ne.

Controls:

- necommitovať reálne secrets,
- používať secret references alebo sealed/encrypted workflow podľa platformy,
- neprintovať celý config do logu,
- redigovať rendered output,
- chrániť temp files a backups,
- nastaviť minimálne permissions,
- oddeliť public config od secret material,
- validovať target namespace a ownership.

Base64 je encoding, nie encryption.

## 54. Bezpečný write lifecycle

Pri generovaní konfigurácie:

1. vytvor doménový object,
2. validuj business pravidlá,
3. serializuj cez knižnicu,
4. zapíš temporary file v cieľovom filesysteme,
5. znovu parse-ni generated output,
6. schema-validuj ho,
7. spusti platform-specific dry-run alebo plan,
8. vykonaj atomic replace,
9. reload/reconcile službu,
10. over runtime desired state.

Ručné skladanie JSON/YAML stringov obchádza escaping a type safety serializera.

## 55. Diagnostika JSON/YAML

### Parser hlási chybu na neskoršom riadku

Skutočná príčina môže byť skôr:

- neuzavretý string,
- neplatný escape,
- chýbajúca closing collection,
- nesprávna indentation,
- tab v YAML indentation,
- template expression narušujúci syntax.

### Hodnota zmenila typ

Skontroluj:

- YAML version/schema,
- quoting,
- template render,
- environment override parser,
- serializer round-trip,
- schema conversion.

### Tool ignoruje field

Možné príčiny:

- preklep a permissive unknown fields,
- nesprávna schema/API version,
- field na nesprávnej úrovni,
- deprecated alebo nepodporovaný field,
- template ho odstránil,
- proces číta iný config file,
- reload neprebehol.

### Diff zmenil celý dokument

Over:

- serializer a parser version,
- key ordering,
- line endings,
- indentation,
- Unicode escaping,
- round-trip comment/style loss.

## 56. Diagnostika regexu

### Pattern nič nenájde

Skontroluj:

- search verzus full-match API,
- anchors,
- multiline a dot-all flags,
- case sensitivity,
- escaping vrstvy,
- regex dialect,
- Unicode/ASCII semantics,
- `\r` v CRLF inpute.

### Pattern nájde príliš veľa

Skontroluj:

- greedy quantifier,
- chýbajúce grouping pri alternation,
- príliš širokú character class,
- chýbajúci full-match,
- dot-all alebo multiline flag.

### Pattern je pomalý

Testuj:

- dlhý non-matching input,
- nested quantifiers,
- ambiguous alternation,
- backreferences,
- veľký capture count,
- chýbajúci timeout alebo input limit.

## 57. Prevádzkový checklist

Pred použitím config alebo regex pipeline over:

- presný formát, parser a version sú deklarované,
- input bytes a nesting majú limity,
- duplicate keys sa odmietajú,
- YAML loader je safe a má alias limits,
- schema draft/version je explicitná,
- unknown-field policy je vedomá,
- config merge a precedence sú definované,
- secrets sú oddelené a redigované,
- rendered output sa parse-ne a validuje,
- serializer output je deterministický,
- regex engine a flags sú známe,
- validation používa full-match semantics,
- Unicode/ASCII model je explicitný,
- input length a regex runtime sú ohraničené,
- adversarial testy pokrývajú ReDoS riziko.

## 58. Časté omyly

### „Platný YAML znamená platnú konfiguráciu“

Nie. Potrebuješ platform schema, business validation a runtime verification.

### „YAML je iba JSON s comments“

Nie. Má implicit typing, documents, anchors, aliases, tags a komplexnejší parser model.

### „Safe loader vyrieši všetky YAML riziká“

Nie. Znižuje object-construction riziko, ale stále treba limity na veľkosť, nesting a aliases.

### „JSON object nemôže mať duplicate keys“

Text ich môže obsahovať a parsers ich môžu interpretovať rozdielne.

### „Sorted JSON je canonical JSON“

Nie bez presného canonicalization štandardu.

### „Regex validuje business pravidlá“

Regex typicky validuje lexical shape. Range, existence a cross-field pravidlá patria do doménovej validácie.

### „Regex funguje rovnako vo všetkých nástrojoch“

Nie. Dialect, flags, anchors, Unicode a runtime model sa líšia.

### „Lazy quantifier odstráni performance riziko“

Nie automaticky. Aj lazy pattern môže intenzívne backtrackovať.

### „Base64 chráni secret“

Nie. Je reverzibilný encoding.

## 59. Kontrolné otázky

1. Aký je rozdiel medzi parsingom, schema validáciou a business validáciou?
2. Prečo sú duplicate JSON keys nebezpečné?
3. Aké interoperability problémy má JSON number model?
4. Aký je rozdiel medzi absent, `null`, empty a false hodnotou?
5. Prečo deterministic serialization nie je automaticky canonicalization?
6. Ako sa líši YAML 1.1 a YAML 1.2 implicit typing?
7. Aké riziká prinášajú anchors a aliases?
8. Prečo safe loader stále potrebuje resource limits?
9. Prečo sa template source, rendered YAML a runtime object musia diagnostikovať oddelene?
10. Aké rozhodnutia obsahuje config merge contract?
11. Prečo je regex dialect súčasťou kontraktu?
12. Aký je rozdiel medzi search, prefix match a full match?
13. Ako multiline flag mení anchors?
14. Prečo je alternation grouping dôležité?
15. Ako vzniká catastrophic backtracking a ReDoS?
16. Prečo normalizácia Unicode mení security semantics?
17. Ako rozlíšiš validation regex od business validácie?
18. Ako navrhneš bezpečný read-parse-validate-render-apply pipeline?

## Glossary impact

Relevantné pojmy: JSON object, duplicate key, JSON number, JSON Schema, schema draft, canonicalization, deterministic serialization, YAML mapping, sequence, scalar, YAML 1.1, YAML 1.2, implicit typing, document stream, anchor, alias, merge key, safe loader, alias expansion, round-trip parser, template rendering, regular expression, regex dialect, full match, anchor, flag, capturing group, backreference, lookaround, greedy quantifier, catastrophic backtracking, ReDoS, Unicode normalization a config precedence.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Python for automation](python-for-automation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Verification vs. validation →](../04-testing-and-quality/verification-vs-validation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->