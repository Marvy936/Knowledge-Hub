# Template functions a pipelines

Helm template engine premieňa typed values a release context na text, ktorý sa následne interpretuje ako YAML a Kubernetes objekty. Funkcia alebo pipeline preto nie je iba pohodlná syntax. Je to transformačná hranica, na ktorej sa môže zmeniť typ, význam, precedence, dôvernosť, deterministickosť aj runtime behavior výsledného resource-u.

Bezpečný návrh nezačína otázkou „ktorú Sprig funkciu použijem“. Začína exact inputom a cieľovým fieldom: odkiaľ hodnota pochádza, či je prítomná, aký má runtime typ, akú transformáciu podstúpi, ako sa serializuje a čo jej výsledok spôsobí v API a aplikácii.

## 1. Dominantný transformačný lifecycle

Každá kritická pipeline sa dá opísať ako typed graph. Hodnota vstúpi z values alebo release contextu, prejde presence a policy rozhodnutím, prípadne conversion alebo merge, následne serialization a whitespace formátovaním a skončí v konkrétnom rendered fielde. Až potom ju interpretuje YAML parser, Kubernetes schema, admission a runtime consumer.

```text
values path a authority
→ presence, empty a default semantics
→ Go-template runtime type
→ function/pipeline transform
→ merge alebo structured composition
→ serialization a whitespace
→ rendered field identity
→ YAML/API/admission interpretation
→ process-loaded behavior
→ deterministic replay a evidence
```

Pipeline je vysvetliteľná iba vtedy, keď poznáme typ pred a po každom kroku. Ak čitateľ nevie povedať, či výraz stále pracuje s mapou, už so stringom alebo s chýbajúcou hodnotou, transformáciu treba rozdeliť na pomenované intermediate variables alebo helper s explicitným contractom.

## 2. Exact transform subject

Atlas Payments release používa chart `CH57`, values bundle `V57`, manifest `M57`, release `payments-prod` revision 18 a cluster generation `K136`. Kritický values path `legacyAuthorizer.enabled` má boolean hodnotu `false`; image digest je `I57` a release annotation odkazuje na source commit `C57`.

Transform subject však nekončí pri values path-e. Musí spájať source value, runtime type, presný pipeline expression, output shape, rendered object/field, manifest digest, admitted object, Pod configuration generation a request, na ktorom sa behavior overuje. Pre legacy flag je výsledným fieldom `ConfigMap.data.legacy-authorizer-enabled`; jeho consumerom je application process a business oracle-om payment authorization `P-884`.

Takéto prepojenie umožní rozlíšiť tri odlišné chyby: value bola nesprávna už na vstupe, pipeline ju transformovala nesprávne alebo render/live object bol správny, ale proces používa starú snapshot generation.

## 3. Funkcie, pipelines a argument flow

Funkcia používa explicitné argumenty, napríklad `quote .Values.logLevel`. Pipeline zapisuje rovnaký flow zľava doprava: `.Values.logLevel | lower | quote`. Výsledok ľavej časti sa odovzdáva ako posledný argument ďalšej funkcie. Pri viacargumentových funkciách je to dôležité, pretože vizuálne poradie nemusí zodpovedať naivnému čítaniu.

```gotemplate
{{ .Values.name | repeat 3 | quote }}
```

je konceptuálne rovnaké ako:

```gotemplate
{{ quote (repeat 3 .Values.name) }}
```

Dobre navrhnutá pipeline má krátky a stabilný type flow, napríklad `map alebo nil → map → YAML string → indented YAML string`. Príklad `.Values.podAnnotations | default dict | toYaml | nindent 8` je bezpečný iba vtedy, keď empty map a missing value skutočne znamenajú rovnaký contract a caller očakáva YAML map fragment na presnej indentation úrovni.

## 4. Tri vrstvy typov

Helm pracuje minimálne s troma typing vrstvami. YAML alebo CLI parser najprv vytvorí Go-template hodnoty. Template funkcie ich môžu meniť alebo serializovať. Výsledný YAML potom znovu parsuje Kubernetes a validuje ho proti API schema.

```text
values YAML/CLI representation
→ Go-template runtime type
→ rendered YAML representation
→ Kubernetes API type
```

Hodnota `3`, string `"3"` a CLI `--set-string version=3` môžu viesť k odlišným runtime typom. String environment variable preto potrebuje quoting, kým `spec.replicas` má zostať integer. Univerzálne pravidlo „všetko quote-ni“ vytvára rovnaké chyby ako „nič nequote-ni“. Správny typ určuje cieľový API a application contract.

Conversion funkcie ako `int` alebo `toString` majú zmysel pri explicitne podporovaných vstupných formátoch. Nemajú maskovať invalid input. Ak chart prijíma string aj číslo bez jasného dôvodu, silent coercion môže vytvoriť validný render s iným významom. Preferovaná hranica je values schema, ktorá odmietne nečakaný typ ešte pred templatingom.

## 5. Missing, empty a explicitná hodnota

Helm/Sprig empty semantics považuje za empty nielen `nil` a prázdny string, ale aj numeric zero, boolean `false` a prázdny list alebo mapu. To je užitočné pri niektorých UI-like fallbackoch, ale nebezpečné pri configuration API, kde každá hodnota môže niesť samostatný význam.

```text
key chýba
≠ key je false
≠ key je 0
≠ key je prázdny string
≠ key je prázdny list
```

`default` je preto policy decision. Výraz `.Values.service.port | default 8080` hovorí, že všetky empty hodnoty vrátane `0` majú znamenať port 8080. Výraz `.Values.legacyAuthorizer.enabled | default true` hovorí, že explicitné `false` sa má zmeniť na `true`. Ak to nie je intended contract, fallback je chybný aj keď template syntakticky funguje.

Static defaults patria primárne do `values.yaml` a schema contractu. Keď treba odlíšiť absent boolean od explicitného `false`, používa sa presence check ako `hasKey`, prípadne sa chart navrhne tak, aby schema zabezpečila vždy prítomnú typed hodnotu. Rovnaký princíp platí pre zero replicas, empty allowlist alebo empty hostname, ktoré nemusia znamenať „použi default“.

## 6. Validation responsibilities

`values.schema.json`, `required`, `fail`, Kubernetes API a runtime test kontrolujú odlišné veci. Schema je vhodná pre typy, required fields, enums a základnú štruktúru. `required` a `fail` môžu kontrolovať chart-specific cross-field invariant, napríklad že `ingress.host` je prítomný iba pri enabled ingress-e alebo že disabled ServiceAccount creation vyžaduje explicitný existing name.

Kubernetes API následne overuje resource schema a admission policy. Ani ono však nevie, či application správne interpretuje ConfigMap alebo či route vedie na intended backend. Posledná vrstva preto patrí runtime a business testu. Error messages zo schema alebo template vrstvy nesmú dumpovať secret payload alebo celé sensitive values objects.

## 7. Fallback chains a hidden configuration

`coalesce` vyberá prvú non-empty hodnotu. Krátky a dokumentovaný fallback môže byť legitímny, napríklad explicitný local ServiceAccount name, potom organization-wide default a nakoniec computed chart name. Dlhý chain cez local value, global value, chart metadata, release name a live `lookup` však vytvára hidden authority.

Pri incidente potom nie je jasné, ktorý source rozhodol. Kritické identities, image digests, tenant IDs, credential references a policy generations majú mať jeden authoritative source alebo krátku, testovanú precedence. Effective value evidence musí zachytiť aj branch, ktorá skutočne vyhrala, nie iba final string.

## 8. Maps, mutation a merge semantics

`dict`, `get`, `index` a `dig` pomáhajú pracovať so structured values. Dot notation je čitateľná pri stabilnej schema, ale dlhý nested path môže zlyhať na missing intermediate objecte. Bezpečný pattern najprv stabilizuje parent mapu a až potom číta leaf. Aj vtedy sa však nesmie použiť `default`, ak zero alebo false zostávajú platnými hodnotami.

`set` a `unset` mapu mutujú. `merge` a `mergeOverwrite` môžu zdieľať nested references. Helper, ktorý zmutuje input mapu, môže ovplyvniť neskorší template a výsledok sa stane závislým od evaluation orderu. Preto sa pred merge používa explicitná copy boundary, napríklad `deepCopy`, a contract určuje precedence, význam `null`, behavior nested maps, list replacement a zachovanie explicitného `false` alebo `0`.

Merge test matrix musí obsahovať missing leaf, null, false, zero, empty map, nested override a list replacement. Názov funkcie sám nepreukazuje, ktorý source vyhrá ani či sa inputy zachovajú immutable.

## 9. Serialization a whitespace boundary

`toYaml` a `toJson` menia structured value na text. Po serializácii template engine už nepracuje so semantic mapou alebo listom, ale so stringom. `indent` a `nindent` tento string umiestnia do caller YAML contextu. Chyba môže vytvoriť invalidný YAML, ale aj syntakticky validný dokument, v ktorom subtree skončí na nesprávnej úrovni.

Named helper alebo `include` preto potrebuje output-shape contract: vracia scalar, map fragment, list alebo celý document? Pridáva leading newline? Očakáva caller, že ho odsadí? Helper nemá hard-code-núť indentation konkrétneho call site-u. Whitespace trim markers sa používajú opatrne, pretože agresívne odstránenie newline môže spojiť dva YAML tokeny.

Final test musí parsovať celý rendered document a kontrolovať semantic field paths. Unit test stringu z helpera nestačí, ak caller ďalšou transformáciou zmení jeho význam.

## 10. `include`, `tpl`, `lookup` a trust boundary

`include` vyrenderuje named template do stringu, ktorý možno ďalej poslať cez pipeline. Je to užitočný composition mechanismus, ale caller musí poznať scope a output shape helpera.

`tpl` ide ďalej: vyhodnotí string z values ako template. Tým mení values z dát na executable render input. Untrusted PR alebo tenant-controlled value môže získať prístup k sprístupnenému scope-u, functions a podľa execution contextu aj cluster-aware operáciám. `tpl` sa preto povoľuje iba pre trusted, versionovaný contract a nikdy nie ako všeobecný „custom YAML“ input v pipeline s production credentials.

`lookup` číta live Kubernetes API a pridáva do render subjectu cluster identity, caller RBAC, object UID/resourceVersion, API availability a current object ownership. Rovnaký chart a values potom nemusia vytvoriť rovnaký manifest v inom čase alebo clustri. Restore do prázdneho clusteru môže dopadnúť inak než upgrade existujúcej release. Preferované sú explicitné versionované inputs alebo controller reconciliation; `lookup` potrebuje úzky lifecycle dôvod a captured observed-object evidence.

## 11. Determinism a target capabilities

Functions ako `now`, random generators, certificate generation a live reads menia output bez zmeny source. Ak random credential vzniká pri každom upgrade-e, Pod dostane nový secret, zatiaľ čo downstream systém môže stále očakávať starý credential. Rollout môže byť technicky green a authentication zlyhá.

Stable identity alebo credential sa vytvára v samostatnom authoritative lifecycle-e a chart používa jeho reference. `.Capabilities` sa tiež nesmie brať ako univerzálna pravda: local render používa flags a Helm defaults, ktoré nemusia zodpovedať target clusteru. Produkčný pipeline používa explicitný target API inventory alebo server-side validation. Ak staré API nie je podporovaným contractom, fail-closed je bezpečnejší než tichý legacy fallback.

Deterministic render gate spustí rovnaký subject opakovane a porovná semantic manifest digest. Rozdiel musí mať vysvetlenú versionovanú príčinu; inak chart nie je reprodukovateľný.

## 12. Connected incident: `false` sa zmenilo na `true`

Values `V57` obsahovali `legacyAuthorizer.enabled: false`. Template použil pipeline:

```gotemplate
legacy-authorizer-enabled: {{ .Values.legacyAuthorizer.enabled | default true | quote }}
```

Render `M57` obsahoval string `"true"`. Exact subject spájal values path, runtime `bool(false)`, pipeline, ConfigMap field, manifest M57, Pod config checksum `CFG57` a payment request `P-884`.

Hypotézy zahŕňali wrong effective values, CLI string conversion, fallback semantics, helper/merge overwrite, stale ConfigMap projection, application parser a old traffic cohort. `helm get values --all` potvrdil boolean false. Isolated render ukázal, že sa hodnota mení už v pipeline. Live ConfigMap, Pod checksum a request trace potom vylúčili admission mutation a stale workload ako primary cause.

Root cause bol presný: `default` považoval false za empty a vybral fallback true; `quote` už iba serializovalo chybný verdict. Containment zastavilo promotion M57, zachovalo values/render/live/process evidence a nepatchovalo iba live ConfigMap. Recovery použila explicitnú presence logiku alebo schema default, pridala fixtures pre missing/false/true, vytvorila CH58/M58 a rolloutovala novú Pod generation.

Acceptance overila false v effective values, renderi, live ConfigMap aj procese; explicitné true aj missing-default path; deterministic second render; odstránenie old endpoint cohorty a exactly-once payment outcome. Tým sa odlíšila oprava template od náhodného symptom removal.

## 13. Failure patterns a troubleshooting

`toYaml` s nesprávnym `nindent` môže vložiť validný subtree na nesprávne miesto. Merge bez copy boundary môže zmeniť input iného template-u. `tpl` nad untrusted inputom rozširuje execution capability. `lookup` ako source of truth ničí reproducibility. Random credential vyvoláva neplánovanú rotation. Local capabilities môžu vybrať API variant nepodporovaný target clusterom.

Troubleshooting začína exact values sources a runtime types. Potom sa izoluje najmenší template a field, sledujú sa intermediate values, renderuje sa s exact target capabilities, parsuje sa celý YAML, vykoná server-side validation a admission diff a až následne sa porovná live object, process-loaded state a business trace. Debug output sa rediguje, pretože `--debug` môže exponovať sensitive rendered fields.

Najčastejšie anti-patterny sú pipeline bez vysvetliteľného type graphu, `default true` nad booleanom, silent coercion namiesto schema, map mutation bez copy contractu, merge bez matrixu, helper s hard-coded indentation, `tpl` nad untrusted values, `lookup` ako hlavný desired-state source a nondeterministická funkcia v stable resource identity.

## Kontrolné otázky

1. Aký type graph vytvára konkrétna pipeline od values po API field?
2. Prečo missing, false, zero a empty string nie sú automaticky ekvivalentné?
3. Kedy je `default` legitímna policy a kedy mení explicitný intent?
4. Ako sa delia zodpovednosti medzi schema, `required`/`fail`, API a runtime test?
5. Prečo merge potrebuje copy a precedence contract?
6. Čo sa stráca na serialization boundary?
7. Ako `tpl` a `lookup` menia trust a reproducibility model?
8. Ako preukážeš deterministic render a process-loaded correctness?

## Executable lab: boolean `false`, `required`, pipeline a `toYaml`

Najčastejšie template chyby nevznikajú na zložitej syntaxi, ale na nesprávnej interpretácii typu. V tomto labe má explicitné `false` znamenať vypnutú legacy funkcionalitu a nesmie byť nahradené defaultom.

Do `values.yaml` vlož:

```yaml
config:
  logLevel: info
  legacyAuthorizerEnabled: false
resources:
  requests:
    cpu: 100m
    memory: 128Mi
```

Template používa `required` pre povinný string, `ternary` pre explicitný boolean a `toYaml | nindent` pre vnorenú mapu:

```gotemplate
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
spec:
  selector:
    matchLabels:
      app: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
    spec:
      containers:
        - name: api
image: nginx:1.27-alpine
env:
  - name: LOG_LEVEL
    value: {{ required "config.logLevel je povinné" .Values.config.logLevel | quote }}
  - name: LEGACY_AUTHORIZER_ENABLED
    value: {{ ternary "true" "false" .Values.config.legacyAuthorizerEnabled | quote }}
resources:
  {{- toYaml .Values.resources | nindent 12 }}
```

Render vykonaj s explicitným override-om `false`:

```bash
helm template payments-dev ./atlas-payments \
  --set config.legacyAuthorizerEnabled=false \
  --show-only templates/deployment.yaml \
  > /tmp/functions.yaml

yq '.spec.template.spec.containers[0].env[]
    | select(.name == "LEGACY_AUTHORIZER_ENABLED")
    | .value' /tmp/functions.yaml
```

Očakávaný výstup je string `false`. Ak template použije chybný výraz:

```gotemplate
value: {{ .Values.config.legacyAuthorizerEnabled | default true | quote }}
```

rovnaký test vráti `true`, pretože Sprig považuje boolean `false` za empty hodnotu pre potreby `default`. Helm syntax aj YAML môžu zostať úplne validné; zlyhá významový contract.

Povinnú hodnotu otestuj jej odstránením:

```bash
helm template payments-dev ./atlas-payments \
  --set config.logLevel=null \
  --show-only templates/deployment.yaml
```

Render má skončiť chybou s textom `config.logLevel je povinné`. Tento negatívny test dokazuje, že `required` guard je zapojený. Nedokazuje, že povolená hodnota `info` je kompatibilná s konkrétnou application verziou; to patrí do runtime testu.

Pipeline čítaj zľava doprava ako transformáciu hodnoty. Pri `toYaml .Values.resources | nindent 12` sa mapa najprv serializuje na YAML a potom sa každý riadok vloží pod `resources:` s dvanásťmi medzerami. Ak sa `nindent` vynechá alebo má nesprávnu hodnotu, výsledkom môže byť syntakticky neplatný manifest alebo field na nesprávnej úrovni.

## Glossary impact

Relevantné pojmy: Helm typed transform graph, presence contract, empty semantics, default policy, effective value authority, merge copy boundary, serialization boundary, helper output shape, executable values, live lookup dependency, target capabilities a deterministic render verdict.

## Primárne zdroje

- [Helm — Template Functions and Pipelines](https://helm.sh/docs/chart_template_guide/functions_and_pipelines/)
- [Helm — Function List](https://helm.sh/docs/chart_template_guide/function_list/)
- [Helm — Values Files](https://helm.sh/docs/chart_template_guide/values_files/)
- [Helm — Accessing Files Inside Templates](https://helm.sh/docs/chart_template_guide/accessing_files/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Praktický Helm chart od prázdneho adresára po overený release](helm-chart-practical-walkthrough.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Named templates →](named-templates.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
