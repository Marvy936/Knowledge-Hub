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