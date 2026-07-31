# Named templates

Named template je reusable Helm fragment, ktorý centralizuje naming, labels, selectors, image references, ServiceAccount ownership alebo opakovaný YAML contract. Nie je to však typovaná funkcia. Prijíma jeden scope object, produkuje text a jeho meno sa registruje v globálnom template namespace-e parent chartu aj všetkých dependencies.

Táto kombinácia robí helper zároveň užitočným aj rizikovým. Call site sa nemusí zmeniť, no dependency môže priniesť rovnaké globálne meno a zmeniť effective definition. Helper môže dostať inú časť contextu, než očakáva, alebo vrátiť text iného shape-u. Výsledkom môže byť validný YAML s nesprávnou resource identity, immutable selectorom alebo privilege contractom.

## 1. Dominantný helper lifecycle

Helper treba chápať ako versionované API medzi providerom definície a všetkými call sites. Jeho bezpečnosť nevychádza iba z toho, že render prejde. Musí byť možné preukázať, ktorá definition vyhrala v global namespace-e, aký scope dostala, aký text vrátila a do ktorého Kubernetes fieldu sa výsledok vložil.

```text
reuse alebo compatibility intent
→ global helper name a definition origin
→ caller a explicitný scope contract
→ helper call graph
→ output shape a text digest
→ caller serialization/indentation
→ rendered field a resource identity
→ API immutability/ownership effect
→ runtime outcome
→ versioned compatibility a second-render test
```

Pri incidente je helper subject kompletný až vtedy, keď zahŕňa chart/dependency digest, helper name, definition origin, call site, input keys a typy, output shape, output digest a target field. Samotný názov `labels` alebo `fullname` nevysvetľuje, čo sa skutočne vykonalo.

## 2. Exact Atlas helper subject

Atlas Payments používa parent chart `CH57`, dependency lock `D57`, rendered manifest `M57` a release `payments-prod` revision 18. Kritický helper `atlas-payments.selectorLabels` je definovaný parent chartom, volaný z Deploymentu, Pod template a Service a má vracať unindented stable YAML mapu.

Exact subject obsahuje global helper name, origin chart/version/digest, caller template, caller scope, explicitný argument dictionary, output digest a destination field. Pre Deployment selector to znamená napríklad origin `CH57`, caller `templates/deployment.yaml`, root release context `payments-prod`, output `SL57` a destination `Deployment.spec.selector.matchLabels`.

Rovnaké textové meno bez originu nestačí, pretože parent chart, subchart alebo library dependency môžu definovať rovnaký helper. Rovnaký output bez call-site identity tiež nestačí, pretože indentation alebo ďalšia caller pipeline môžu text vložiť na inú YAML úroveň.

## 3. Global namespace a definition resolution

`define` registruje fragment, ale nevytvára samostatný manifest. Convention používa `templates/_helpers.tpl`, pričom underscore iba zabraňuje renderovaniu file-u ako Kubernetes resource; nevytvára namespace. Všetky parent a dependency templates sa kompilujú do spoločného global namespace-u.

To znamená, že generické meno ako `common.labels` je supply-chain collision surface. Ak parent a dependency definujú rovnaký name, effective definition závisí od load/compile resolution. Caller zostane nezmenený, ale output a následný manifest sa môžu zmeniť.

Helper names preto používajú chart/provider prefix, napríklad `atlas-payments.selectorLabels`. Pri nekompatibilných evolúciách je vhodná aj versioned identity ako `atlas-platform.v2.podSecurityContext`. Duplicate-definition scanner nad packaged graphom je praktický gate; review iba parent source-u collision neodhalí.

## 4. `template`, `include` a textový boundary

`template` vloží helper output priamo do current output streamu. `include` vráti text, ktorý možno poslať cez pipeline, napríklad cez `nindent`. Pre YAML fragments je `include` obvykle čitateľnejší, pretože caller vlastní umiestnenie a indentation.

Tým však vzniká explicitný textový boundary. Helper môže logicky reprezentovať mapu alebo list, ale template engine vracia string. Caller musí vedieť, či output obsahuje leading newline, trailing newline, scalar, map fragment, list item alebo celý resource. Nesprávny output-shape assumption môže vytvoriť invalidný YAML alebo validný document so subtree na nesprávnom mieste.

Helper nemá hard-code-núť caller-specific indentation. Má vracať canonical unindented shape a caller ho vloží podľa cieľovej pozície. Final rendered document sa musí parsovať a semantic assertions musia kontrolovať konkrétny field, nie iba isolated helper string.

## 5. Scope ako explicitný argument

Pri `include "atlas-payments.labels" .` predstavuje `.` root odovzdaný callerom. Ak caller pošle `.Values.service`, helper už nevidí pôvodný chart root; aj `$` vo vnútri helpera odkazuje na root odovzdaného invocation scope-u, nie automaticky na parent chart context.

Polymorfný helper, ktorý niekedy očakáva root a inokedy local subtree, je krehký. Keď potrebuje viac údajov, dostane explicitný dictionary contract, napríklad `root`, `name` a `port`. Helper následne validuje required keys a ich význam. Takýto pseudo-signature contract určuje input keys, expected types, output shape, side effects a determinism.

```gotemplate
{{ include "atlas-payments.containerPort" (dict
    "root" .
    "name" "http"
    "port" .Values.service.port
) }}
```

Tento pattern zviditeľní data flow a znižuje riziko, že helper potichu prečíta unrelated values alebo stratí `.Release`, `.Chart` či `.Capabilities` context.

## 6. Output-shape a compatibility contract

Named template vždy produkuje text, ale jeho semantic contract môže byť scalar, YAML map, YAML list, resource fragment alebo empty output. Dokumentácia helpera preto uvádza input subject, output shape, newline/indentation behavior, quoting, stability a allowed evolution.

Selector helper má napríklad vracať stabilnú mapu bez leading newline. Common-label helper môže pridať mutable metadata, ale nesmie byť použitý tam, kde Kubernetes vyžaduje immutable selector. Image helper má vracať jeden immutable `repository@digest` string. ServiceAccount helper musí explicitne rozlíšiť create a external-reference mode.

Zmena helper outputu je API change pre všetkých call sites. Ak library chart odstráni field, zmení map na list alebo pridá mutable label do selectoru, consumer chart môže zlyhať bez zmeny vlastného source. Helper fixtures, output digests a consumer compatibility matrix preto patria do dependency upgrade reviewu.

## 7. Naming a resource identity

Naming helper rozhoduje, či Helm/Kubernetes aktualizuje existujúci object alebo vytvorí nový. Kombinuje release name, chart name, overrides, truncation a suffix trimming. Refactor `fullname` helpera môže premenovať Service, Secret, PVC alebo StatefulSet a tým zmeniť DNS, storage attachment, external reference a rollback behavior.

Takáto zmena nie je kozmetická. Potrebuje migration plan, identity inventory a negative test, že staré a nové resources nevytvoria dual writer alebo orphan data. Dlhé names musia byť testované aj na truncation collision, keď dva odlišné inputs po skrátení vytvoria rovnakú Kubernetes identity.

Stable identity helper nesmie používať random/time functions ani mutable dependency data. Repeated render rovnakého subjectu musí vytvoriť rovnaké names.

## 8. Stable selectors a mutable metadata

Deployment selector, Pod labels a Service selector tvoria routing a ownership contract. Selector musí zostať semantic stable medzi podporovanými revisions. Chart version, app version, image digest alebo release timestamp sú mutable metadata a nepatria do immutable Deployment selectoru.

Správny model oddeľuje `selectorLabels` od širších `labels`. Selector obsahuje iba stable application/release identity. Common labels môžu pridať `helm.sh/chart`, `app.kubernetes.io/version` a `managed-by`, ale ich použitie v selectors je zakázané. Tests porovnávajú selector output medzi current a target chartom a overujú zhodu medzi Deployment selectorom, Pod template labels a Service selection.

Selector drift môže viesť k API immutable-field denial, ale aj k tichému routing failure, keď Service a Pody používajú odlišné helper outputs. Preto sa kontroluje final semantic map v každom call site-e, nie iba helper definition.

## 9. Ownership, identity a security helpers

ServiceAccount helper vyjadruje ownership contract. Pri `create=true` môže vypočítať name vytvoreného resource-u. Pri `create=false` musí vyžadovať explicitný external name. Silent fallback na `default` ServiceAccount by zmenil workload identity a mohol rozšíriť alebo zúžiť privileges bez jasného erroru.

Image helper podobne používa required repository a immutable digest. Mutable tag alebo implicitný `appVersion` fallback oslabuje artifact identity. SecurityContext, RBAC alebo Secret-reference helpery potrebujú úzky output contract, pretože library update môže zmeniť privilege alebo credential boundary všetkých consumers.

Helper nemá vykonávať skrytý live lookup alebo generovať credential. Také behavior patrí do samostatného lifecycle-u s explicitnou authority, nie do reusable text macro.

## 10. Call graph a library charts

Helper call graph má zostať plytký a acyklický. Primitive identity helpers môžu napájať selectors a common labels; tie následne manifests. Hlboké vrstvenie a serialize/parse cycles komplikujú source-to-field provenance a robia compatibility review neprehľadným.

Library chart je provider helper API bez vlastného bežného workload lifecycle-u. To však neznamená malý blast radius. Môže zmeniť names, selectors, images, securityContext, RBAC a ďalšie fields vo všetkých parent releases. Potrebuje versioned contracts, changelog, migration guide, dependency lock, rendered fixtures a canary consumers.

Upgrade library dependency sa preto posudzuje ako source-code dependency upgrade. Parent render sa vytvára proti old aj new version, porovnajú sa helper definition inventory, output digests a final manifests a následne sa vykoná server-side upgrade test.

## 11. Connected incident: dependency prepísala selector helper

Parent chart definoval generický helper `common.selectorLabels` so stable application a release labels. Aktualizovaná library dependency `LD58` definovala rovnaké global name a pridala mutable `helm.sh/chart` hodnotu. Caller v parent charte sa nezmenil, no global resolution použila inú definition.

Exact incident subject zahŕňal parent `CH57`, dependency `LD58`, lock `D57`, helper name, oba definition origins, call sites v Deployment/Pod/Service, old output `SL56`, new output `SL57`, manifest `M57` a live Deployment UID/generation.

Hypotézy zahŕňali values/name change, parent source change, helper collision, wrong scope, whitespace shape, admission mutation a divergent call sites. Effective values a packaged parent source vylúčili prvé dve. Inventory všetkých `define "common.selectorLabels"` v packaged graph-e ukázal collision. Isolated outputs a server dry-run potvrdili, že new helper pridal chart version do immutable selectoru ešte pred admission.

Kauzálny chain bol:

```text
unreviewed library update
→ global helper collision
→ selector SL56 sa zmení na SL57
→ Deployment selector diff
→ API odmietne immutable update
→ Helm revision zlyhá po možných skorších side effects
```

Containment zastavilo retry a dependency re-resolution, zachovalo packaged graph, M57, API error a release history a ponechalo starú serving cohortu. Nepoužilo delete ani `--force`, pretože tie by zmenili resource identity a mohli spôsobiť outage.

Recovery premenovala parent helper na `atlas-payments.selectorLabels`, library contracts dostali provider/version prefix, stable selectors sa oddelili od common metadata a dependency sa pinla reviewed lockom. CI pridalo duplicate-definition scanner, selector stability fixtures a server-side upgrade test.

Acceptance potvrdila, že selector zostáva stable medzi revisions, Service a Pod labels sa zhodujú, mutable metadata nie je v selector contracte, generic colliding helper už neexistuje a repeated render/upgrade sú deterministic a bounded. Tým sa overil pôvodný rollout outcome aj forbidden identity replacement.

## 12. Ďalšie failure boundaries a troubleshooting

Wrong local scope môže helper pripraviť o `.Release` alebo `.Chart`. Fullname refactor môže vytvoriť nové Service/PVC/Secret identities. Hard-coded indentation môže fungovať iba v jednom call site-e. Structured output môže zmeniť map/list type. Nondeterministic naming vytvára perpetual diff. Každý z týchto failure modes potrebuje final field test, nie iba review helper source-u.

Troubleshooting postupuje od exact helper name k všetkým definitions a origins. Potom sa fixne dependency graph, call site a scope, helper output sa vyrenderuje izolovane, porovná sa old/new digest a final target field, vykoná server validation proti live objectu a overí runtime/service outcome. Root context sa nedumpuje celý, pretože môže obsahovať sensitive values.

Test matrix zahŕňa default a overrides, dlhé names a truncation collisions, missing/empty/false/zero, root a local scope, všetky call sites, indentation, selector stability, ServiceAccount modes, image tag/digest combinations, parent/dependency definition inventory, multiple dependency versions a repeated deterministic render.

Najčastejšie anti-patterny sú generické global names, implicitná pseudo-signature, predpoklad že `$` je pôvodný root, mutable metadata v selector helperi, fullname refactor bez migration analýzy, caller-specific indentation, helper generujúci celý komplexný workload, library update bez consumer testu a collision riešená force/delete zásahom.

## Kontrolné otázky

1. Ktoré identity tvoria exact helper subject?
2. Prečo je namespace parent a dependency templates globálny?
3. Ako `include` vytvára textový output boundary?
4. Čo znamenajú `.` a `$` po odovzdaní local scope-u?
5. Ako vyzerá helper pseudo-signature a output-shape contract?
6. Prečo je fullname zmena resource migration?
7. Ktoré labels musia zostať stabilné a prečo?
8. Ako library chart mení supply-chain a compatibility surface?
9. Ktoré observations odhalia helper collision?
10. Ako preukážeš stable resource identity medzi revisions?

## Executable lab: helper s explicitným contextom

Named template je globálne pomenovaný program. Pri väčšom charte je bezpečnejšie odovzdať mu presný context než predpokladať, že bodka vždy reprezentuje root chart object.

V `templates/_helpers.tpl` definuj chart-prefixed helper:

```gotemplate
{{- define "atlas-payments.componentLabels" -}}
app.kubernetes.io/name: {{ include "atlas-payments.name" .root }}
app.kubernetes.io/instance: {{ .root.Release.Name }}
app.kubernetes.io/component: {{ .component | quote }}
{{- end -}}
```

V Deploymente ho zavolaj cez `include` a `dict`:

```gotemplate
metadata:
  labels:
    {{- include "atlas-payments.componentLabels"
        (dict "root" $ "component" "api")
        | nindent 4 }}
```

Znak `$` zachová root context aj vtedy, keď sa call nachádza vo vnútri `with` alebo `range`. `dict` robí vstupy helpera viditeľné: helper dostane root a component, nie nejasnú bodku s meniacim sa významom.

Vyrenderuj iba Deployment a pozri labels:

```bash
helm template payments-dev ./atlas-payments \
  --show-only templates/deployment.yaml \
  | yq '.metadata.labels'
```

Očakávaný output obsahuje stabilné release a component labels:

```yaml
app.kubernetes.io/name: atlas-payments
app.kubernetes.io/instance: payments-dev
app.kubernetes.io/component: api
```

`include` vracia text, takže ho možno ďalej poslať do pipeline a odsadiť cez `nindent`. Ak sa namiesto neho použije action `template`, output nemožno rovnakým spôsobom pipeline-nuť. To je praktický dôvod, prečo sa `include` často používa pri YAML fragments.

Negatívny test zámerne zavolá helper bez `root`:

```gotemplate
{{ include "atlas-payments.componentLabels" (dict "component" "api") }}
```

Render má zlyhať pri prístupe k `.root.Release.Name`. Takýto failure je vhodnejší než tiché vyrenderovanie labels z nesprávneho contextu. Production helper možno ešte posilniť explicitným `required` guardom alebo predaním menšej typed mapy namiesto celého root objectu.

## Glossary impact

Relevantné pojmy: Helm helper subject, global helper namespace, definition origin, helper pseudo-signature, output-shape contract, helper call graph, stable selector contract, helper collision, library-chart provider contract, helper-output digest a helper-driven identity migration.

## Primárne zdroje

- [Helm — Named Templates](https://helm.sh/docs/chart_template_guide/named_templates/)
- [Helm — Templates Best Practices](https://helm.sh/docs/chart_best_practices/templates/)
- [Helm — Library Charts](https://helm.sh/docs/topics/library_charts/)
- [Helm — Subcharts and Global Values](https://helm.sh/docs/chart_template_guide/subcharts_and_globals/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Template functions a pipelines](template-functions-pipelines.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Chart dependencies →](chart-dependencies.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
