# YAML, JSON a regular expressions

YAML a JSON sú dátové serializačné formáty používané v konfigurácii, API kontraktoch, CI/CD pipelines a Infrastructure as Code. Regular expressions sú pattern language na rozpoznávanie a transformáciu textu. V automatizácii sa často používajú spolu, ale riešia odlišné problémy: parser má spracovať štruktúrované dáta, regex iba textový pattern.

## 1. Základný princíp

Použi správnu abstrakciu:

```text
structured data → parser a schema validation
line-oriented text → parser, delimiter alebo regex podľa kontraktu
human display output → nie je stabilné automation API
```

Regexom neparsuj JSON, YAML, XML ani programovací jazyk, ak existuje štandardný parser.

## 2. JSON data model

JSON podporuje:

- object,
- array,
- string,
- number,
- boolean,
- `null`.

Príklad:

```json
{
  "service": "api",
  "replicas": 3,
  "enabled": true,
  "tags": ["public", "critical"],
  "limits": null
}
```

JSON object keys sú strings. Poradie properties nemá byť business contract, aj keď parser môže insertion order zachovať.

## 3. JSON syntax

JSON vyžaduje:

- double quotes pre keys a strings,
- žiadne trailing commas,
- žiadne comments,
- presné lowercase literals `true`, `false`, `null`.

Neplatné:

```json
{
  'service': 'api',
  "replicas": 3,
}
```

## 4. JSON numbers

JSON nerozlišuje integer a floating-point typ na úrovni syntaxe tak, ako konkrétny jazyk. Consumer môže číslo interpretovať rozdielne.

Riziká:

- strata presnosti veľkých integerov v JavaScript-like prostredí,
- decimal rounding,
- timestamps uložené ako nejasné číslo,
- IDs nesprávne reprezentované numericky.

Veľký identifikátor alebo číslo vyžadujúce presnosť môže byť bezpečnejšie uložiť ako string s explicitným schema kontraktom.

## 5. JSON null, absent a empty

Tieto stavy nie sú rovnaké:

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

API a config schema musí definovať semantics každého stavu.

## 6. JSON encoding

JSON text sa bežne prenáša ako UTF-8. Pri files explicitne nastav encoding a nepoužívaj platform-dependent default.

BOM, invalid bytes alebo nesprávny `Content-Type` môžu spôsobiť interoperability problémy.

## 7. JSON parsing a serialization

Python:

```python
import json

with open("config.json", encoding="utf-8") as handle:
    data = json.load(handle)

print(json.dumps(data, indent=2, sort_keys=True))
```

PowerShell:

```powershell
$data = Get-Content config.json -Raw -Encoding utf8 | ConvertFrom-Json
$data | ConvertTo-Json -Depth 20
```

Bash s `jq`:

```bash
jq -e '.service == "api" and (.replicas | type == "number")' config.json
```

## 8. Canonicalization a diff

Formatting-only zmeny vytvárajú noise. V automation pipelines často pomáha stabilné:

- indentation,
- newline policy,
- key ordering, ak to organizácia vedome používa,
- number representation,
- encoding.

Key sorting nie je univerzálna canonical JSON definícia. Pre cryptographic signing alebo deterministic hashing použi konkrétny canonicalization štandard.

## 9. JSON Schema

JSON Schema opisuje očakávanú štruktúru:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["service", "replicas"],
  "properties": {
    "service": {
      "type": "string",
      "minLength": 1
    },
    "replicas": {
      "type": "integer",
      "minimum": 1
    }
  },
  "additionalProperties": false
}
```

Schema môže validovať syntax a shape, nie business reality. `replicas: 3` môže byť schema-valid, ale prevádzkovo nedostatočné.

## 10. YAML data model

YAML je human-oriented serialization language s mappings, sequences a scalars.

```yaml
service: api
replicas: 3
enabled: true
tags:
  - public
  - critical
limits: null
```

Indentation je syntax. Tabs sa v indentation nepoužívajú.

## 11. YAML documents

Jeden stream môže obsahovať viac documents:

```yaml
---
service: api
---
service: worker
```

Consumer musí vedieť, či očakáva jeden alebo viac documents. Nie každý nástroj multi-document YAML podporuje rovnako.

## 12. YAML scalars a implicit typing

YAML parser môže implicitne interpretovať hodnoty ako boolean, number, date alebo null podľa schema/verzie parsera.

Potenciálne nejasné hodnoty cituj:

```yaml
version: "1.0"
port: 8080
feature: "on"
date: "2026-07-21"
```

Konkrétne správanie závisí od YAML verzie a implementácie. Nespoliehaj sa na nejasné implicitné typovanie.

## 13. Quoting v YAML

Plain scalar:

```yaml
name: api
```

Single-quoted:

```yaml
pattern: '^api-[0-9]+$'
```

Double-quoted interpretuje escape sequences:

```yaml
message: "line one\nline two"
```

Pri regexoch je single quoting často čitateľnejší, pretože backslash sa nemusí zdvojovať podľa double-quoted YAML rules.

## 14. Multiline strings

Literal block zachováva newlines:

```yaml
script: |
  set -e
  echo "start"
  run-task
```

Folded block spája riadky:

```yaml
description: >
  This is a long
  description rendered as
  one logical line.
```

Chomping indicators `|-`, `|+`, `>-` určujú trailing newline behavior.

## 15. Anchors, aliases a merge keys

```yaml
defaults: &defaults
  timeout: 10
  retries: 3

api:
  <<: *defaults
  port: 8080
```

Anchors a aliases znižujú duplicitu, ale môžu zhoršiť čitateľnosť, tooling alebo platform compatibility. Merge key nie je podporovaný jednotne vo všetkých YAML consumers.

## 16. YAML tags

YAML podporuje explicitné tags, ktoré môžu meniť typ alebo spustiť language-specific object construction.

Pri nedôveryhodnom YAML používaj safe loader. Unsafe deserialization môže viesť k vykonaniu kódu alebo vytvoreniu nebezpečných objektov.

Python:

```python
import yaml

data = yaml.safe_load(content)
```

Nikdy nepoužívaj unsafe loader na neoverený vstup.

## 17. YAML nie je templating language

Konfigurácia:

```yaml
image: app:1.2.3
replicas: 3
```

Templating:

```yaml
image: {{ image_repository }}:{{ image_tag }}
```

Po vložení template expressions už súbor nemusí byť platný YAML pred renderovaním. Debugging musí rozlišovať:

```text
template input
→ rendered YAML
→ parser result
→ platform schema
→ runtime behavior
```

## 18. YAML duplicate keys

```yaml
replicas: 2
replicas: 5
```

Niektoré parsers použijú poslednú hodnotu, iné zlyhajú. Duplicate keys majú byť validation error.

Zapni linting a parser settings, ktoré ich odmietnu.

## 19. YAML formatting a linting

Nástroje podľa ekosystému:

```bash
yamllint config.yaml
yq '.' config.yaml
```

Pre Kubernetes:

```bash
kubectl apply --dry-run=server -f manifest.yaml
```

Syntakticky platný YAML nemusí byť platný Kubernetes manifest. Potrebuje aj platform schema a admission validation.

## 20. JSON vs. YAML

| Vlastnosť | JSON | YAML |
|---|---|---|
| Primárne použitie | machine interchange, API | human-authored configuration |
| Comments | nie | áno |
| Syntax | explicitnejšia | flexibilnejšia |
| Typové prekvapenia | menej | viac podľa parsera/schema |
| Multi-document stream | nie | áno |
| Anchors/aliases | nie | áno |
| Parser complexity | nižšia | vyššia |

YAML je superset-like vo vzťahu k JSON syntaxe podľa špecifikácie, ale praktická interoperabilita závisí od parserov.

## 21. Configuration precedence

Ak systém prijíma YAML/JSON aj environment/CLI overrides, definuj precedence:

```text
defaults
< config file
< environment variables
< CLI arguments
```

Loguj výsledný nesensitive config source, nie secrets.

## 22. Schema evolution

Pri zmene config alebo API formátu rieš:

- backward compatibility,
- unknown fields,
- defaults,
- deprecated fields,
- migration,
- versioning,
- producer/consumer rollout order.

`additionalProperties: false` odhaľuje preklepy, ale môže komplikovať forward compatibility.

## 23. Regular expressions

Regex opisuje jazyk textových patternov.

Príklad:

```regex
^[a-z][a-z0-9-]{2,31}$
```

Pattern validuje lowercase name s dĺžkou 3–32 znakov.

## 24. Základné prvky regexu

```text
.        ľubovoľný znak podľa engine/flags
^        začiatok stringu alebo line
$        koniec stringu alebo line
*        0 alebo viac
+        1 alebo viac
?        0 alebo 1; prípadne lazy modifier
{m,n}    počet opakovaní
[abc]    character class
[^abc]   negovaná character class
(...)    capturing group
(?:...)  non-capturing group
|        alternation
\d       digit podľa engine semantics
\s       whitespace
\w       word character podľa engine semantics
```

Regex dialects sa líšia. Pattern fungujúci v Python PCRE-like engine nemusí fungovať v POSIX ERE, RE2, JavaScript alebo .NET.

## 25. Anchoring

Validácia celej hodnoty má byť ukotvená:

```regex
^[0-9]{4}-[0-9]{2}-[0-9]{2}$
```

Bez anchors môže engine nájsť iba substring.

V niektorých engines je bezpečnejšie použiť absolute anchors ako `\A` a `\z`/`\Z`, pretože `^` a `$` sa môžu meniť s multiline režimom.

## 26. Capturing groups

```regex
^(?<name>[a-z0-9-]+):(?<tag>[a-zA-Z0-9._-]+)$
```

.NET používa named group syntax `(?<name>...)`; Python podporuje `(?P<name>...)`. Nie všetky dialects sú zhodné.

Zachytávaj iba hodnoty, ktoré downstream logika reálne potrebuje.

## 27. Greedy a lazy quantifiers

Greedy:

```regex
<.*>
```

môže zachytiť od prvého `<` po posledný `>`.

Lazy:

```regex
<.*?>
```

zastaví pri prvom vhodnom `>` v engines, ktoré lazy quantifier podporujú.

Ani jeden variant nerobí regex vhodným parserom HTML.

## 28. Lookaround

Príklad positive lookahead:

```regex
^(?=.*[A-Z])(?=.*[0-9]).{12,}$
```

Lookbehind a lookahead nie sú podporované vo všetkých engines. RE2-like engines ich často odmietajú kvôli linear-time garanciám.

## 29. Unicode

`\w`, case-insensitive matching a character classes môžu mať Unicode alebo ASCII semantics podľa engine a flags.

Pre explicitný lowercase ASCII identifier používaj:

```regex
^[a-z0-9-]+$
```

Nespoliehaj sa na `\w`, ak presný allowed alphabet tvorí security contract.

## 30. Escaping vrstvy

Regex často prechádza viacerými syntaktickými vrstvami:

```text
regex syntax
→ string literal syntax
→ YAML/JSON syntax
→ shell quoting
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

YAML single-quoted string:

```yaml
pattern: '^\d+\.\d+$'
```

Rozlišuj, ktorá vrstva interpretuje backslash.

## 31. Catastrophic backtracking

Problematický pattern:

```regex
^(a+)+$
```

Na určitých non-matching vstupoch môže backtracking engine spotrebovať extrémny čas.

Ochrany:

- jednoduchšie patterny,
- limit dĺžky vstupu,
- linear-time engine,
- timeout,
- atomic groups alebo possessive quantifiers, ak ich engine podporuje,
- performance tests na adversarial inputoch.

## 32. ReDoS

Regular Expression Denial of Service vzniká, keď útočník kontroluje vstup pre pattern s patologickým runtime.

Regex používaný na request validation je security-sensitive code. Review musí zahŕňať complexity a max input size.

## 33. Regex nie je univerzálny parser

Nepoužívaj regex na:

- nested JSON,
- YAML indentation model,
- HTML/DOM,
- programovací jazyk,
- komplexné CSV quoting,
- recursive expressions.

Použi parser s definovanou grammar.

## 34. Python regex

```python
import re

NAME_RE = re.compile(r"^[a-z][a-z0-9-]{2,31}$")


def is_valid_name(value: str) -> bool:
    return NAME_RE.fullmatch(value) is not None
```

`fullmatch()` jasnejšie vyjadruje validáciu celého stringu než manuálne anchors.

## 35. PowerShell regex

```powershell
if ($Name -match '^[a-z][a-z0-9-]{2,31}$') {
    $Matches[0]
}
```

`-match` je defaultne case-insensitive. Pre case-sensitive použite `-cmatch`.

`$Matches` sa aktualizuje posledným úspešným matchom a pri neúspechu môže zachovať starú hodnotu; nepoužívaj ho bez vedomej kontroly výsledku.

## 36. Bash regex

```bash
if [[ $name =~ ^[a-z][a-z0-9-]{2,31}$ ]]; then
  printf 'valid\n'
fi
```

V `[[ ... =~ ... ]]` má quoting regexu version-sensitive a často neočakávané semantics. Pattern môže byť čitateľnejší v premennej:

```bash
pattern='^[a-z][a-z0-9-]{2,31}$'
[[ $name =~ $pattern ]]
```

## 37. grep, sed a awk

```bash
grep -E '^[0-9]+$' input.txt
sed -E 's/^([a-z]+)=/\1: /' input.txt
awk -F= '$1 == "port" { print $2 }' config.env
```

Rozlišuj:

- POSIX basic regex,
- POSIX extended regex,
- PCRE mode,
- platform-specific tool variant.

GNU a BSD implementations sa môžu líšiť.

## 38. Validation vs. extraction

Validation:

```regex
^[0-9]{1,5}$
```

Extraction:

```regex
status=(?<status>[0-9]{3})
```

Validation pattern má typicky pokrývať celý input a následne musí business logika overiť range. Regex `^[0-9]{1,5}$` stále akceptuje port `99999`.

## 39. Normalizácia pred validáciou

Rozhodni, či pred matchingom:

- trimuješ whitespace,
- normalizuješ Unicode,
- meníš case,
- dekóduješ percent encoding,
- odstraňuješ separators.

Normalizácia môže meniť security semantics. Producer aj consumer musia používať konzistentný model.

## 40. Secret a config handling

YAML/JSON files často obsahujú sensitive values. Bezpečnostné pravidlá:

- necommitovať reálne secrets,
- používať placeholders alebo secret references,
- neprintovať celý config do logu,
- chrániť temp files a backups,
- schema-validovať pred apply,
- kontrolovať permissions,
- oddeliť public configuration od secret material.

Base64 encoding nie je encryption.

## 41. Safe processing pipeline

```text
read bytes with explicit encoding
→ parse with safe parser
→ validate schema
→ normalize allowed fields
→ apply business validation
→ calculate plan
→ serialize deterministically
→ validate rendered output
→ apply atomically
→ verify runtime result
```

Každá vrstva rieši inú triedu chýb.

## 42. Troubleshooting YAML/JSON

### Parser hlási chybu na inom riadku

Skutočná chyba môže byť skôr:

- chýbajúca closing quote,
- nesprávna indentation,
- neuzavretá flow collection,
- tab,
- invalid escape.

### Hodnota zmenila typ

Skontroluj YAML implicit typing, quoting a parser schema.

### Tool ignoruje field

Možné príčiny:

- typo a permissive unknown fields,
- nesprávna schema version,
- field je na nesprávnej úrovni,
- templating ho odstránil,
- consumer používa inú config file.

### JSON diff je celý zmenený

Over formatting, newline, key ordering a serializer version.

## 43. Troubleshooting regexu

### Pattern nič nenájde

Skontroluj:

- anchors,
- flags,
- escaping layers,
- newline mode,
- Unicode semantics,
- dialect,
- skrytý carriage return.

### Pattern nájde príliš veľa

Skontroluj greedy quantifier, character class, alternation precedence a chýbajúce anchors.

### Pattern je pomalý

Testuj adversarial non-matching inputs, nested quantifiers a ambiguous alternation.

## 44. Časté omyly

### „Platný YAML znamená platnú konfiguráciu“

Nie. Potrebuješ schema aj business validation.

### „YAML je iba JSON s comments“

Nie. Má komplexnejší typing, anchors, tags, multi-document streams a indentation semantics.

### „Regex validuje všetku business logiku“

Nie. Pattern overuje tvar; range a cross-field pravidlá patria do kódu alebo schema constraints.

### „Base64 skryje secret“

Nie. Je to reverzibilné encoding.

### „Regex funguje rovnako vo všetkých nástrojoch“

Nie. Dialect, flags a Unicode behavior sa líšia.

## 45. Kontrolné otázky

1. Aký je rozdiel medzi absent, `null` a empty value v JSON?
2. Aké riziká má JSON number model?
3. Prečo môže YAML scalar zmeniť typ?
4. Aký je rozdiel medzi literal a folded block scalar?
5. Prečo sú duplicate YAML keys nebezpečné?
6. Prečo sa má nedôveryhodný YAML načítať safe loaderom?
7. Kedy použiť JSON Schema a čo nevaliduje?
8. Aký je rozdiel medzi validation a extraction regexom?
9. Ako vzniká catastrophic backtracking a ReDoS?
10. Prečo treba sledovať viac vrstiev escaping-u?
11. Prečo regex nie je vhodný JSON/YAML parser?
12. Ako navrhneš bezpečný config processing pipeline?

## Glossary impact

Relevantné pojmy: JSON object, JSON Schema, canonicalization, YAML mapping, YAML sequence, scalar, implicit typing, document stream, anchor, alias, safe loader, schema validation, regular expression, regex dialect, capturing group, lookaround, greedy quantifier, catastrophic backtracking, ReDoS, Unicode normalization a deterministic serialization.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Python for automation](python-for-automation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Verification vs. validation →](../04-testing-and-quality/verification-vs-validation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
