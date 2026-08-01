# YAML, JSON a regular expressions

<!-- CONCEPT-FIRST:START -->
## Čo sú YAML, JSON a regular expressions

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
<!-- CONCEPT-FIRST:END -->

## Atlas scenár a praktické použitie

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
