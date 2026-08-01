# YAML, JSON a regular expressions

JSON a YAML sú dátové serializačné formáty. Regex je jazyk na rozpoznávanie textových vzorov. Riešia odlišné problémy a nemajú sa zamieňať.

**JSON** má malý, presný dátový model: object, array, string, number, boolean a null. Neobsahuje comments ani natívny date alebo binary typ. Duplicate object keys sú problematické, pretože parsers môžu vybrať prvú, poslednú alebo chybu. Bez schema validation syntakticky platný JSON ešte nemusí byť platnou configuration.

**YAML** je bohatší human-oriented formát s indentation, scalars, sequences, mappings, anchors a tags. Existuje viac verzií a parserov s odlišnými schema pravidlami. Text `on`, `yes` alebo dátum môže byť v niektorých parseroch interpretovaný inak než string. Preto treba pinovať parser, používať safe loading a explicitne validovať domain model.

JSON je syntaktickým subsetom YAML 1.2, ale súbor s príponou `.yaml` nemusí byť JSON. Na všeobecné YAML nemožno bezpečne používať JSON parser.

Pipeline pre structured data:

```text
read bytes s explicitným encodingom
→ parse syntax
→ odmietnuť duplicate alebo nebezpečné constructs
→ schema validation
→ domain validation
→ canonical normalization
→ controlled serialization
→ platform apply
→ runtime verification
```

Schema overí shape a typy. Domain validation overí význam medzi fields, napríklad že production replicas nemôžu byť nula. Canonical serialization je dôležitá pre fingerprinty a signatures; obyčajné textové porovnanie môže považovať ekvivalentné dokumenty za odlišné.

**Regular expression** pracuje s textom, nie so syntax tree YAML/JSON. Je vhodný na validáciu obmedzeného tokenu alebo extrakciu zo stabilného line protocolu. Nie je vhodný na všeobecné prepísanie nested structured data. Escaping sa navyše skladá cez viac vrstiev: shell, programming string a regex dialect.

Regex engine môže mať backtracking a pri nevhodnom pattern-e spôsobiť ReDoS. Vstupná dĺžka, anchors, bounded quantifiers a engine semantics sú súčasťou bezpečnosti.

Ak potrebuješ zmeniť hodnotu v YAML alebo JSON, dokument sa má parse-nuť, zmeniť cez dátový model, validovať a serialize-nuť. Regexové nahradenie môže trafiť comment, podobný key v inom scope alebo quoted text.

Atlas automation načítava `orders.yaml`, overuje ho proti schema contractu, vytvára canonical plan JSON a v logoch hľadá presné operation IDs. Tieto tri formy textu majú odlišné parsery a riziká. YAML a JSON sú structured data formáty; regex je pattern language nad textom. Regex nemá nahrádzať parser hierarchical data.

## Processing pipeline

Bezpečný flow:

```text
bytes a encoding
→ parse podľa deklarovaného formátu
→ syntaktický model
→ schema validation
→ domain validation
→ canonical internal model
→ mutation alebo render
→ platform validation
→ runtime read-back
```

Každá vrstva môže zlyhať inak. Validný YAML môže porušiť schema. Schema-valid config môže obsahovať business limit mimo povoleného environment range. Rendered file môže byť prijatý toolom, ale runtime nemusí načítať novú generation.

## JSON

JSON má objects, arrays, strings, numbers, booleans a null. Neobsahuje komentáre ani dátumový type. Duplicate object keys sú nejednoznačné; rôzne parsery môžu ponechať prvú alebo poslednú hodnotu. Security-sensitive parser má duplicates odmietnuť.

```python
import json

def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result

value = json.loads(text, object_pairs_hook=no_duplicates)
```

Numbers môžu stratiť precision pri prechode cez IEEE-754 runtimes. Identifiers a money sa často reprezentujú stringom alebo integerom v najmenšej jednotke podľa contractu.

Canonical JSON pre hashing musí definovať key order, whitespace, Unicode a number representation. Bežný pretty print nie je cryptographic canonicalization standard.

## YAML

YAML podporuje comments, anchors, aliases, block scalars a viac scalar styles. Táto flexibilita zvyšuje human ergonomics aj parser complexity. YAML versions a libraries sa môžu líšiť v implicitnom typovaní.

Hodnoty ako `yes`, `on`, dátumy alebo čísla s leading zero boli historicky interpretované rozdielne. Kritické strings sa quotujú a schema overí výsledný type.

```yaml
service: orders-api
environment: dev
release: "4.2.0"
maxOrderAmount: 5000
currency: EUR
```

Anchors znižujú duplicitu, ale môžu skryť effective value. Automation má po parse pracovať s resolved modelom a pri review podľa potreby renderovať effective config.

Untrusted YAML sa nikdy nenačítava unsafe object constructors. Používa sa safe loader a limits proti alias expansion alebo nadmernému nesting-u.

## JSON-compatible YAML subset

JSON dokument je v YAML 1.2 použitelný ako veľmi úzky interoperabilný subset. Praktický lab používa file `orders.yaml` s JSON syntaxou, aby ho štandardná Python `json` knižnica načítala bez externého package. Je to zámerný lab contract, nie všeobecný YAML parser.

Ak user pridá comments alebo YAML block syntax, tool to odmietne. Production tool má pinned YAML library, explicitnú supported version a tests pre parser behavior.

## Schema a domain validation

JSON Schema môže overiť required fields, types, ranges, enums a additional properties. Schema však nemusí poznať environment-specific business policy.

```text
schema: maxOrderAmount je integer >= 1
domain: v dev môže byť <= 10000
policy: v production zmena nad 20 % vyžaduje approval
```

Tieto gates majú oddelené errors a owners.

## Serialization a round trip

Parser–serializer cycle môže zmeniť comments, anchors, ordering alebo numeric presentation. Automation nemá prepisovať human-authored YAML, ak potrebuje zachovať presentation. Lepší model je oddeliť source config a generated artifact.

Pri JSON outpute sa určí UTF-8, newline, key order a trailing newline. Stable serialization znižuje noisy diffs a zlepšuje hashing.

## Regex dialect a anchoring

Regex syntax sa líši medzi Python, PCRE, RE2, .NET, grep a JavaScript. Pattern sa dokumentuje spolu s engine-om. Anchors `^` a `$` môžu byť line-based pri multiline mode; `\A` a `\z`/`\Z` majú engine-specific význam.

Pre Atlas operation ID:

```python
r"\Areq-[0-9a-f]{4,32}\Z"
```

Validation má použiť full-match API, nie search:

```python
re.fullmatch(r"req-[0-9a-f]{4,32}", value)
```

## Escaping layers

Regex vložený do YAML, shellu alebo programming stringu prechádza viacerými escaping vrstvami. Pattern pre digit `\d` môže vyžadovať iný zápis v každom context-e.

Najbezpečnejšie je pattern uložiť ako samostatnú raw string hodnotu a testovať presný runtime input. `eval`, shell interpolation a regex composition z nedôveryhodných fragments vytvára injection risk.

## ReDoS

Backtracking regex s nested quantifiers môže mať katastrofickú zložitosť:

```text
(a+)+$
```

na dlhom takmer matching inpute. Untrusted input potrebuje bounded length, bezpečný engine alebo pattern bez nebezpečnej ambiguity. Regex validator nie je automaticky lacný.

## Regex nie je YAML editor

Príkaz:

```bash
sed -i 's/maxOrderAmount:.*/maxOrderAmount: 5000/' config/orders.yaml
```

môže prepísať commented example, nested field alebo block scalar. Nechá invalid duplicates a nerozumie anchors. Structured data sa parse-ne, zmení v model-e, schema-validuje a serializuje podľa contractu.

Regex je vhodný na lokálny text pattern, log line alebo striktne definovaný flat format. Nie na všeobecnú hierarchical mutation.

## Mechanický rozbor parserov, serializácie a regex hraníc

Nasledujúce rozbory sledujú bytes cez decoding, parser a effective type model až po schema/domain validation, controlled serialization a platform read-back. Regex príklady sú zámerne vedené oddelene: engine pracuje nad textovým patternom a nevlastní syntax tree structured dokumentu. Každý rozbor preto pomenúva parser generation, vstupný subject, stratené informácie a failure, ktorý samotný parse success ešte nevylučuje.

### Duplicate-key rejection v JSON

```python
def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result

value = json.loads(text, object_pairs_hook=no_duplicates)
```

Bežný `dict` už duplicate informáciu stratil, preto hook dostáva ordered list `(key, value)` pairs skôr, než sa object zostaví. Function iteruje a odmietne druhý výskyt. Hook sa volá pre každý nested JSON object, takže kontrola nie je iba top-level.

Tento kód nerieši limits na document size, nesting alebo number precision. `json.loads` môže parse-nuť veľmi veľký integer, ale downstream JavaScript/DB ho môže stratiť. Pre peniaze a IDs definuj representation v schema a domain modeli.

Ak JSON pochádza z bytes:

```python
text = raw.decode("utf-8", errors="strict")
```

Strict decoding odmietne invalid bytes namiesto silent replacement characters. BOM a alternate encodings musia mať explicitnú policy.

### Safe YAML loading a effective types

Všeobecný YAML vyžaduje pinned library. Príklad s PyYAML:

```python
from pathlib import Path
import yaml

raw = Path("orders.yaml").read_text(encoding="utf-8")
value = yaml.safe_load(raw)
if not isinstance(value, dict):
    raise ValueError("root must be a mapping")
```

`safe_load` blokuje Python-specific object constructors, ale nie všetky resource-exhaustion risks a nevaliduje domain schema. Library/version určuje YAML schema a implicitné scalar types. Po parse si vypíš typy v teste:

```python
assert isinstance(value["release"], str)
assert isinstance(value["maxOrderAmount"], int)
```

Anchors a merge keys môžu vytvoriť effective mapping odlišný od lokálneho textu. Review tool má vedieť zobraziť resolved model. Alias count/nesting limits sú potrebné pri nedôveryhodnom inpute.

### Schema verzus domain validation

Schema example:

```json
{
  "type": "object",
  "required": ["environment", "maxOrderAmount"],
  "additionalProperties": false,
  "properties": {
    "environment": {"enum": ["dev", "staging", "prod"]},
    "maxOrderAmount": {"type": "integer", "minimum": 1}
  }
}
```

`additionalProperties: false` zachytí typo field, ale komplikuje forward compatibility; versioning contract musí povedať, kedy sú unknown fields povolené. Schema nevie automaticky, že production limit nad 20 % vyžaduje approval. Domain function pracuje nad už schema-valid modelom a vydá odlišný error class.

### Controlled serialization

```python
serialized = json.dumps(
    model,
    ensure_ascii=False,
    sort_keys=True,
    indent=2,
) + "\n"
Path("generated.json").write_text(serialized, encoding="utf-8", newline="\n")
```

Explicitný key order a newline znižujú noisy diffs. Pretty JSON nie je automaticky canonical hashing formát. Pri YAML round-tripe môže serializer odstrániť comments/anchors a zmeniť quoting; preto human source a generated artifact často majú byť oddelené files.

Pred prepísaním source porovnaj semantic model a vykonaj atomic write. Serializer success nepreukazuje, že target platform config prijme alebo application načíta.

### Regex full match a escaping

```python
pattern = re.compile(r"req-[0-9a-f]{4,32}")
match = pattern.fullmatch(value)
```

Raw string zabráni Pythonu interpretovať väčšinu backslashes; regex engine stále interpretuje pattern. `fullmatch` vyžaduje pokrytie celého stringu, takže nepotrebuje `^...$` a vyhne sa multiline anchor prekvapeniam.

Ak pattern prichádza z YAML:

```yaml
operationIdPattern: 'req-[0-9a-f]{4,32}'
```

single quotes v YAML minimalizujú backslash escapes. V double-quoted YAML stringu majú backslashes vlastnú escape vrstvu. Pattern, programming language string a shell command sú tri odlišné parsers.

Pre literal user fragment používaj `re.escape(fragment)`, nie string concatenation do regex syntaxe. To rieši regex injection, nie ReDoS z okolitého patternu.

### ReDoS test

Nebezpečný pattern `(a+)+$` môže pri inpute `aaaa...!` explorovať veľa backtracking paths. Bezpečnostný gate zahŕňa:

```text
maximálnu input dĺžku
pattern review bez nested ambiguous quantifiers
engine s lineárnym-time contractom, ak treba
execution timeout alebo isolation
positive aj near-match performance test
```

Regex correctness test s krátkymi matches neodhalí complexity failure.

### Prečo `sed` YAML edit nevie, čo mení

```bash
sed -i 's/maxOrderAmount:.*/maxOrderAmount: 5000/' config/orders.yaml
```

Shell najprv odovzdá single-quoted script bez expanzie. Sed potom matchne text na každom zodpovedajúcom riadku podľa implementácie. Nevidí indentation scope, comments, anchors ani duplicate keys. Môže zmeniť:

```yaml
# maxOrderAmount: 1000
examples:
  maxOrderAmount: 2500
production:
  maxOrderAmount: 4000
```

na viac nesprávnych miest. Parser-based mutation vyberie exact object path, overí pôvodnú expected value, zmení model, schema/domain-validuje a až potom serializuje. Pri potrebe zachovať comments použi round-trip YAML library s explicitným version/tool contractom.

## Incident: duplicate key zmení production limit

Config obsahuje dvakrát `maxOrderAmount`. Linter ponechá prvú hodnotu 5000, runtime parser poslednú 50000. Pipeline a aplikácia teda overujú odlišný effective state.

Oprava zjednotí parser library a duplicate-key rejection, schema gate a runtime loaded-config read-back. Regression test používa presne duplicate input a očakáva failure pred planom.

## Zhrnutie

YAML a JSON sa spracúvajú parserom, schema a domain validationom. Regex je engine-specific textový pattern a nemá suplovať hierarchical parser. Stable encoding, duplicate handling, canonicalization, escaping a complexity sú súčasť correctness a security contractu. Výsledok sa overuje v runtime, nie iba v source file-i.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Python for automation](python-for-automation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Praktický Git a automation projekt od prázdneho adresára po overený apply →](git-automation-practical-walkthrough.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
