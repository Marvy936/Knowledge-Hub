# YAML, JSON a regular expressions

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Python for automation](python-for-automation.md), [Bash automation](bash-automation.md), [PowerShell fundamentals](powershell-fundamentals.md)
- Súvisiace témy: parsing, schema validation, configuration precedence, templating, serialization, regex safety

## 1. Cieľ kapitoly

YAML a JSON sú serializačné formáty. Regex je jazyk textových patternov. V automatizácii sa môžu objaviť v jednom workflowe, ale nesmú sa zamieňať:

```text
structured document
→ parser
→ schema
→ domain validation

stable flat text
→ delimiter alebo regex
→ typed value
```

Najdôležitejšie pravidlo je použiť najvyššiu dostupnú abstrakciu. YAML alebo JSON sa parsuje parserom. Regex sa používa na presne ohraničený lexical tvar alebo extraction zo stabilného textového kontraktu.

## 2. Nosný scenár: Atlas rollout configuration

Tím Atlas udržiava ručne čitateľnú konfiguráciu:

```yaml
apiVersion: atlas/v1
service: orders-api
environment: prod
image: registry.example/orders@sha256:abc123
replicas: 4
healthPath: /health/ready
publicAccess: false
```

Release pipeline musí vytvoriť bezpečný desired state:

```text
bounded UTF-8 bytes
→ strict YAML parse
→ primitive object graph
→ schema validation
→ AtlasConfig domain object
→ business validation
→ deterministic release manifest
→ platform dry-run
→ apply
→ runtime verification
```

Regex sa v tomto flowe používa iba napríklad na lexical kontrolu mena `orders-api`. Nepoužíva sa na vyhľadávanie alebo prepísanie YAML keys.

## 3. Päť odlišných hraníc

### Byte a encoding boundary

Určuje, aké bytes sa čítajú, ich maximálnu veľkosť a encoding.

### Parser boundary

Určuje, či bytes zodpovedajú gramatike YAML alebo JSON a aké runtime hodnoty vzniknú.

### Schema boundary

Určuje očakávané fields, typy a lokálne constraints.

### Business boundary

Určuje cross-field pravidlá, policy, capacity a oprávnenosť zmeny.

### Runtime verification boundary

Určuje, či platforma skutočne dosiahla zamýšľaný stav.

Platný YAML preto ešte neznamená platnú ani bezpečnú konfiguráciu.

## 4. Najprv čítaj ohraničené bytes

Pred parsingom definuj:

- maximálnu veľkosť dokumentu,
- UTF-8 a BOM policy,
- povolený počet YAML dokumentov,
- maximálnu hĺbku,
- timeout parsera, ak ho implementácia podporuje,
- alias a expanded-node limity pri YAML.

Príklad v Pythone:

```python
from pathlib import Path

MAX_CONFIG_BYTES = 1_000_000


def read_config(path: Path) -> str:
    raw = path.read_bytes()
    if len(raw) > MAX_CONFIG_BYTES:
        raise ValueError("configuration exceeds size limit")
    return raw.decode("utf-8-sig")
```

`utf-8-sig` môže byť vedomou policy pre tolerovanie BOM. Iný systém môže BOM odmietať. Dôležité je konzistentné rozhodnutie, nie náhodný default knižnice.

## 5. Parser vytvára generic object graph

YAML mapping alebo JSON object sa typicky zmení na dictionary-like objekt. Sequence alebo array sa zmení na list. Scalar sa preloží na string, number, boolean alebo null-like hodnotu.

Parser output je stále nedôveryhodný generic object:

```python
raw: object = parse_yaml(content)
```

Až ďalšia vrstva má zistiť, či ide o mapping s presnými Atlas fields.

Neposielaj parser output priamo do deployment API iba preto, že parsing uspel.

## 6. JSON má menší syntax model, nie nulové riziko

JSON podporuje:

- object,
- array,
- string,
- number,
- boolean,
- `null`.

Relevantné failure boundaries:

- duplicate object keys,
- veľké integers alebo decimals interpretované rozdielnymi runtime typmi,
- absent field verzus explicitné `null`,
- príliš hlboký document,
- nečakaný Unicode alebo normalization model,
- serializer s príliš malou depth,
- rozdiel medzi stabilným formattingom a štandardizovanou canonicalization.

Identifikátory a presné decimal hodnoty často patria do stringu alebo explicitného decimal typu doménovej vrstvy, nie do neurčitého JSON number contractu.

## 7. Duplicate keys musia byť chyba

Text môže obsahovať:

```json
{
  "publicAccess": false,
  "publicAccess": true
}
```

alebo:

```yaml
publicAccess: false
publicAccess: true
```

Rôzne parsers môžu ponechať prvú hodnotu, poslednú hodnotu alebo zlyhať. Pri config, policy, signing a IaC dokumentoch preto duplicate keys odmietni ešte na parser boundary.

Bez tejto policy môžu dve vrstvy vyhodnotiť rovnaké bytes odlišne.

## 8. YAML implicit typing je súčasť kontraktu

YAML parser a schema version môžu interpretovať tieto scalars rozdielne:

```yaml
feature: on
answer: yes
version: 1.0
date: 2026-07-26
```

Pre portable config cituj hodnoty, ktoré majú zostať strings:

```yaml
feature: "on"
answer: "yes"
version: "1.0"
date: "2026-07-26"
```

Consumer musí deklarovať podporovaný YAML model. Rozdiel medzi YAML 1.1 a 1.2 alebo parser-specific schema nie je vizuálny detail; môže zmeniť runtime typ.

## 9. YAML anchors a aliases zvyšujú parserový state

```yaml
defaults: &defaults
  replicas: 3
  healthPath: /health/ready

orders:
  <<: *defaults
  replicas: 4
```

Anchors môžu znižovať duplicitu, ale pridávajú:

- nepriamu lokálnu interpretáciu,
- override a merge semantics,
- parser compatibility riziko,
- alias expansion riziko,
- nečakanú shared object identity po parse,
- round-trip zmeny.

Pre konfiguráciu určenú viacerým consumers používaj jednoduchý podporovaný subset. `safe_load` obmedzuje konštrukciu ľubovoľných language objects, ale automaticky nerieši všetky resource-exhaustion riziká.

## 10. Normalizácia vytvorí doménový objekt

```python
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AtlasConfig:
    api_version: str
    service: str
    environment: str
    image: str
    replicas: int
    health_path: str
    public_access: bool


def parse_atlas_config(data: Any) -> AtlasConfig:
    if not isinstance(data, dict):
        raise ValueError("top-level configuration must be a mapping")

    expected = {
        "apiVersion",
        "service",
        "environment",
        "image",
        "replicas",
        "healthPath",
        "publicAccess",
    }
    unknown = set(data) - expected
    missing = expected - set(data)

    if unknown:
        raise ValueError(f"unknown fields: {sorted(unknown)}")
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")

    if type(data["replicas"]) is not int:
        raise ValueError("replicas must be an integer")
    if type(data["publicAccess"]) is not bool:
        raise ValueError("publicAccess must be a boolean")

    return AtlasConfig(
        api_version=str(data["apiVersion"]),
        service=str(data["service"]),
        environment=str(data["environment"]),
        image=str(data["image"]),
        replicas=data["replicas"],
        health_path=str(data["healthPath"]),
        public_access=data["publicAccess"],
    )
```

Použitie `type(value) is int` je v tomto príklade zámerné, pretože v Pythone je `bool` subclass `int`. Doménový contract má rozhodnúť, či takúto konverziu povoľuje.

## 11. Schema a business validácia riešia rozdielne otázky

Schema môže overiť:

- required fields,
- typy,
- formát alebo lexical pattern,
- minimum a maximum,
- unknown-field policy,
- lokálnu štruktúru.

Business validácia overí napríklad:

```text
prod replicas musia byť aspoň 3
publicAccess=true vyžaduje explicitnú security approval
image musí používať immutable digest
healthPath musí existovať v service contracte
apiVersion musí byť podporovaná release platformou
```

Príklad:

```python
def validate_business(config: AtlasConfig) -> None:
    if config.environment == "prod" and config.replicas < 3:
        raise ValueError("production requires at least three replicas")
    if "@sha256:" not in config.image:
        raise ValueError("image must use an immutable digest")
    if config.public_access:
        raise ValueError("public access requires separate approved workflow")
```

Schema-valid dokument môže byť prevádzkovo nebezpečný. Business-valid desired state môže stále zlyhať pri platform admission alebo runtime reconciliation.

## 12. Absent, null a empty nie sú synonymá

Tieto stavy majú rozdielny význam:

```json
{}
{"value": null}
{"value": ""}
{"value": []}
{"value": false}
{"value": 0}
```

Config contract musí definovať:

- či absent aktivuje default,
- či `null` znamená unset, inherit alebo explicitne prázdnu hodnotu,
- či empty collection je povolená,
- či `false` a `0` zostávajú explicitnými hodnotami,
- či read-modify-write zachová unknown fields.

Pravdivostná skratka nesmie meniť doménovú semantiku.

## 13. Config precedence a merge sú samostatná gramatika

Ak Atlas kombinuje:

```text
defaults
< shared config
< environment config
< environment variables
< CLI
```

musí definovať:

- whole-value replacement verzus deep merge,
- array replacement verzus append,
- význam `null`,
- delete/unset marker,
- provenance každej výslednej hodnoty,
- conflict policy,
- secret redaction.

„Merge YAML files“ nie je jednoznačná operácia. Merge contract je samostatná súčasť config API.

Po merge znovu vytvor a validuj doménový objekt. Nespoliehaj na to, že každá čiastková vrstva bola samostatne platná.

## 14. Template source nie je výsledný dokument

```text
template source
→ template values
→ rendered text
→ YAML/JSON parser
→ schema
→ business validation
→ platform plan
```

Template source môže obsahovať syntax, ktorá ešte nie je platný YAML:

```yaml
image: {{ image_repository }}@{{ image_digest }}
```

Autoritatívny vstup platformy je rendered output. Pipeline ho musí uchovať ako auditný artifact, znovu parse-nuť a validovať.

Preferuj structured value injection alebo serializer. Ručné skladanie stringov môže zmeniť quoting, typ alebo indentation a môže vložiť secret do rendered outputu.

## 15. Deterministická serializácia znižuje diff noise

Pri generated manifeste definuj:

- UTF-8 a BOM policy,
- newline policy,
- indentation,
- ordering, ak ho workflow používa,
- datetime a decimal representation,
- Unicode escaping,
- serializer version,
- unknown-type behavior.

Stabilný pretty output nie je automaticky kryptografická canonicalization:

```text
sort_keys=True
≠
štandardom definované canonical bytes
```

Hashing alebo signing vyžaduje konkrétny canonicalization contract zdieľaný producerom aj verifierom.

## 16. Round-trip edit verzus generovaný artifact

Bežný parse-modify-serialize môže stratiť:

- comments,
- quoting style,
- anchor names,
- key ordering,
- block-scalar style,
- whitespace.

Nástroj musí vedieť, či:

1. generuje celý súbor zo source of truth,
2. používa round-trip parser,
3. aplikuje structured patch,
4. vlastní iba jednu explicitnú sekciu.

Regex alebo line-by-line replacement nie je bezpečný generic structured patch.

## 17. Regex má ohraničenú úlohu

Atlas používa regex pre lexical tvar service name:

```regex
[a-z][a-z0-9-]{2,31}
```

V Pythone:

```python
import re

SERVICE_RE = re.compile(r"[a-z][a-z0-9-]{2,31}", flags=re.ASCII)


def validate_service_name(value: str) -> None:
    if SERVICE_RE.fullmatch(value) is None:
        raise ValueError("invalid service name")
```

Následná business validácia ešte môže overiť, či služba existuje, či patrí danému tímu a či je povolená v prostredí.

Regex validuje lexical shape. Nevaliduje celý business contract.

## 18. Regex dialect a match API patria do kontraktu

Pattern bez engine a flags nie je úplná špecifikácia.

Rozdiely existujú medzi:

- Python `re`,
- .NET regex,
- JavaScript,
- PCRE/PCRE2,
- RE2-like engines,
- POSIX BRE/ERE,
- Bash `=~`,
- `grep`, `sed` a `awk` implementáciami.

Rozlišuj:

- search kdekoľvek,
- prefix match,
- full match.

Validation zvyčajne potrebuje full-match semantics. Anchors `^` a `$` môžu mať pri multiline režime iný význam než začiatok a koniec celého inputu.

## 19. Escaping má viac vrstiev

Jeden pattern môže prejsť cez:

```text
regex syntax
→ language string
→ YAML/JSON string
→ template
→ shell
```

Raw regex:

```regex
^\d+\.\d+$
```

Python raw string:

```python
pattern = r"^\d+\.\d+$"
```

JSON:

```json
{"pattern": "^\\d+\\.\\d+$"}
```

YAML single-quoted scalar:

```yaml
pattern: '^\d+\.\d+$'
```

Diagnostika musí určiť, ktorá vrstva backslash pridala, odstránila alebo interpretovala.

## 20. Unicode model musí byť explicitný

Pred matchingom rozhodni:

- ASCII-only verzus Unicode,
- normalization form,
- case-folding model,
- povolené combining marks,
- ochranu pred vizuálne podobnými znakmi,
- či length limit počíta bytes, code points alebo grapheme clusters.

Normalizácia pred validáciou mení security semantics. Producer aj consumer musia používať rovnaký model.

Pre systémové identifiers je často bezpečnejší explicitný ASCII allowlist než všeobecné `\w`.

## 21. Regex runtime musí byť ohraničený

Pattern:

```regex
^(a+)+$
```

môže pri dlhom non-matching inpute spôsobiť catastrophic backtracking.

ReDoS ochrany:

- limit input length,
- jednoduchý jednoznačný pattern,
- linear-time engine, kde je vhodný,
- match timeout, ak ho engine podporuje,
- bounded concurrency,
- adversarial performance tests,
- zákaz user-supplied patternov bez sandboxu a limitov.

Regex v request alebo config validation path je security-sensitive code.

## 22. Worked failure: dve vrstvy videli inú security hodnotu

Rendered YAML obsahoval:

```yaml
service: orders-api
publicAccess: false
replicas: 4
publicAccess: true
```

Policy scanner použil parser, ktorý ponechal prvú hodnotu. Deployment tool ponechal poslednú.

Výsledok:

```text
scanner videl publicAccess=false
→ approval prešla
→ runtime parser videl publicAccess=true
→ služba sa publikovala externe
```

Príčina nebola iba „preklep v YAML“. Pipeline nemala jednotný parser contract ani duplicate-key rejection.

Náprava:

1. rendered bytes sa archivujú,
2. strict parser odmietne duplicity,
3. ten istý primitive model vstupuje do schema a policy validácie,
4. deployment manifest sa generuje z validovaného doménového objektu,
5. platform dry-run a runtime verification kontrolujú exposure.

## 23. Worked failure: regex prepísal nesprávny image field

Pôvodná automatizácia:

```bash
sed -E -i 's#image: .*#image: registry/orders:new#' deployment.yaml
```

Manifest obsahoval:

```yaml
containers:
  - name: orders
    image: registry/orders:old
  - name: telemetry-sidecar
    image: registry/telemetry:stable
```

Regex zmenil oba riadky. YAML zostal syntakticky platný a diff nebol dôsledne reviewnutý.

Dôsledok:

```text
orders image sa zmenil správne
+ sidecar dostal neexistujúci orders image
→ pod neprešiel readiness
```

Náprava je structured patch podľa identity containeru:

```text
parse YAML
→ nájdi containers[name=orders]
→ zmeň presné field
→ serialize
→ reparse
→ schema/platform validation
→ verify rollout
```

Regex nepozná YAML nesting ani doménovú identitu objektu.

## 24. Schema evolution potrebuje rollout model

Pri zmene config formátu definuj:

- explicitnú schema alebo API version,
- backward a forward compatibility,
- unknown-field policy,
- defaults,
- rename a deprecation,
- migration tooling,
- producer/consumer rollout order,
- round-trip zachovanie neznámych dát,
- sunset policy.

Breaking change nie je iba odstránenie field-u. Môže ňou byť aj nový required field, sprísnený pattern, zmena defaultu alebo zmena významu `null`.

## 25. Secrets sú samostatný lifecycle

YAML a JSON často obsahujú secret references, ale nemajú sa stať všeobecným secret store.

Controls:

- necommitovať plaintext credentials,
- používať workload identity alebo secret reference,
- nelogovať celý parsed alebo rendered config,
- redigovať plan a diffs,
- chrániť temp files a backups,
- nastaviť minimálne permissions,
- oddeliť public config od secret material,
- validovať target namespace a ownership.

Base64 je encoding, nie encryption.

## 26. Bezpečný read–render–apply lifecycle

```text
read bounded bytes
→ strict safe parse
→ reject duplicate/ambiguous constructs
→ schema validation
→ domain normalization
→ business validation
→ merge desired state
→ deterministic serialization
→ reparse generated bytes
→ platform dry-run/admission
→ atomic publication
→ reconcile
→ runtime verification
```

Každá fáza vytvára vlastný dôkaz. Parser success nemožno použiť ako dôkaz schema, policy alebo runtime success.

## 27. Diagnostický postup

Keď konfigurácia nefunguje:

1. zachovaj presné source a rendered bytes,
2. over encoding, BOM a line endings,
3. identifikuj parser, YAML/JSON version a options,
4. odmietni duplicate keys a nečakané documents,
5. vypíš parsed primitive shape bez secrets,
6. over schema version a unknown fields,
7. over config precedence a provenance hodnôt,
8. porovnaj doménový objekt s generated manifestom,
9. spusti platform-specific dry-run alebo plan,
10. over reálne načítaný config a runtime postcondition.

Pri regex failure navyše over:

- engine a flags,
- search verzus full match,
- escaping vrstvy,
- Unicode/ASCII model,
- CRLF/newline semantics,
- input length a runtime.

## 28. Referenčné pravidlá

- JSON/YAML parsuj parserom, nie regexom.
- Duplicate keys odmietni.
- Safe YAML loader doplň resource limitmi.
- Parser output prelož do explicitného doménového typu.
- Schema a business validation drž oddelene.
- Config merge a precedence dokumentuj ako contract.
- Validuj rendered output, nie iba template source.
- Deterministický serializer nie je automaticky canonicalizer.
- Human-maintained YAML neupravuj generic parse–serialize bez round-trip policy.
- Validation regex používaj s full-match semantics.
- Engine, flags, Unicode model a runtime limit sú súčasť regex contractu.
- Structured mutation vykonaj podľa identity objektu, nie podľa vizuálneho riadku.
- Po apply over reálny runtime stav.

## 29. Časté omyly

### „Platný YAML znamená platnú konfiguráciu“

Nie. Stále chýba schema, business, platform a runtime validation.

### „YAML je iba JSON s comments“

Nie. Má implicit typing, document streams, anchors, aliases, tags a zložitejší parser model.

### „Safe loader vyrieši všetky YAML riziká“

Nie. Resource exhaustion, duplicate keys a doménová validácia zostávajú.

### „JSON object nemôže obsahovať duplicate keys“

Text ich môže obsahovať a parsers ich môžu interpretovať rozdielne.

### „Sorted JSON je canonical JSON“

Nie bez presného canonicalization štandardu.

### „Regex validuje business pravidlá“

Regex typicky validuje lexical shape. Range, existencia, ownership a cross-field pravidlá patria do doménovej vrstvy.

### „Regex funguje rovnako vo všetkých nástrojoch“

Dialect, flags, anchors, Unicode a runtime model sa líšia.

### „Regexom môžem bezpečne upraviť YAML riadok“

Nie všeobecne. Regex nepozná structured identity, nesting ani parser semantics.

## 30. Zhrnutie

YAML a JSON sú transport pre štruktúrované hodnoty. Regex je nástroj pre ohraničený textový pattern.

Spoľahlivý config workflow:

```text
bytes
→ parser
→ primitive graph
→ schema
→ domain object
→ business rules
→ desired state
→ deterministic artifact
→ platform verification
```

Regex vstupuje iba tam, kde je lexical contract skutočne textový. Nemá preskakovať parser, schema ani doménovú identitu.

Toto rozlíšenie pripravuje základ pre nasledujúcu kapitolu: parser, validator a runtime verifier dokazujú rozdielne vlastnosti systému.

## 31. Kontrolné otázky

1. Aký je rozdiel medzi parsingom, schema validáciou a business validáciou?
2. Prečo sa input bytes limitujú ešte pred parsingom?
3. Prečo sú duplicate JSON/YAML keys nebezpečné?
4. Ako YAML implicit typing môže zmeniť runtime typ?
5. Aké riziká prinášajú anchors a aliases?
6. Prečo safe loader stále potrebuje resource limits?
7. Aký význam majú absent, `null`, empty, `false` a `0`?
8. Aké rozhodnutia tvorí config merge contract?
9. Prečo treba validovať rendered output?
10. Aký je rozdiel medzi deterministic serialization a canonicalization?
11. Kedy treba round-trip parser alebo structured patch?
12. Prečo je regex dialect súčasťou kontraktu?
13. Aký je rozdiel medzi search a full match?
14. Ako escaping vrstvy menia pattern?
15. Ako vzniká catastrophic backtracking a ReDoS?
16. Prečo regex nemá upravovať nested YAML alebo JSON?
17. Ako vznikol Atlas duplicate-key incident?
18. Aké dôkazy vytvára bezpečný read–render–apply lifecycle?

## Glossary impact

Relevantné pojmy: JSON object, duplicate key, JSON number, JSON Schema, schema version, canonicalization, deterministic serialization, YAML mapping, sequence, scalar, YAML 1.1, YAML 1.2, implicit typing, document stream, anchor, alias, merge key, safe loader, alias expansion, round-trip parser, template rendering, configuration precedence, domain normalization, regular expression, regex dialect, full match, anchor, flag, Unicode normalization, catastrophic backtracking a ReDoS.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Python for automation](python-for-automation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Verification vs. validation →](../04-testing-and-quality/verification-vs-validation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
