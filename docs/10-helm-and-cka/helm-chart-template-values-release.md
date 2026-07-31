# Helm chart, template, values a release

Helm je package, render a release-lifecycle nástroj pre Kubernetes. Jeho úloha nekončí pri skrátení YAML-u: spája versionovaný chart artifact, dependency graph, values contract, release identity a capabilities cieľového clusteru do konkrétnej generácie Kubernetes objektov. Zároveň uchováva release históriu, ktorá umožňuje vysvetliť, aký intent bol do clusteru odoslaný a akým Helm revision prešiel.

Helm však nevlastní runtime výsledok. Po prijatí objektov preberajú ďalšiu prácu API server, admission, controllers, scheduler, kubelet, CNI, CSI a samotná aplikácia. Úspešný `helm upgrade` preto dokazuje iba určitú časť reťazca. Nedokazuje automaticky, že všetky Pody bežia s očakávaným image digestom, proces načítal správnu configuration generation ani že business operácia skončila správne.

## 1. Dominantný release lifecycle

Helm release treba čítať ako viacvrstvový prechod, nie ako jednu atómovú operáciu. Každá vrstva má vlastnú identitu, failure mode a dôkaz. Ak sa tieto vrstvy zlúčia do jedného statusu `deployed`, diagnostika nevie rozlíšiť chybný input, chybný render, partial API mutation, stale workload cohort ani business regresiu.

```text
release intent a business outcome
→ exact chart, dependency a values subject
→ deterministic render generation
→ schema, API a admission validation
→ Helm release mutation a revision storage
→ Kubernetes reconciliation
→ live object a serving workload generation
→ process-loaded configuration
→ business acceptance
→ recovery, ďalšia revision alebo decommission
```

Silný release verdict preto koreluje source commit, chart digest, dependency lock, effective values, rendered manifest, Helm revision, Kubernetes object UID/generation, Pod artifact a configuration generation a používateľský outcome. Jedna chýbajúca väzba vytvára priestor pre false-green výsledok.

## 2. Exact release subject

V tejto sekcii používame Atlas Payments release do clusteru `atlas-prod-eu1`. Current generation clusteru je `K136`, namespace je `atlas-payments-prod` a release sa volá `payments-prod`. Revision 17 je current a revision 18 je plánovaný transition. Release používa chart `atlas-payments` version `2.7.0`, OCI digest `CH57`, dependency lock `D57`, values bundle `V57`, rendered manifest `M57`, application image `I57` a source commit `C57`.

Tieto identifikátory nie sú redundantné. Chart version opisuje package contract, OCI digest konkrétne bytes, lock dependency graph, values effective configuration a manifest výsledok renderu. Helm revision je lokálna história jednej release identity; Deployment revision a ReplicaSet generation sú zase Kubernetes runtime identity. Bez ich oddelenia môže tím porovnávať nesúvisiace generácie a mylne tvrdiť, že production používa testovaný release.

Cieľ revision 18 je nasadiť image `I57`, vypnúť legacy authorizer, zachovať presne-once payment authorization a nezmeniť Service identity ani persistent data. Zakázaný výsledok nie je iba nedostupnosť. Rovnako neprípustné je, aby legacy path zostala aktívna, release použil iný dependency artifact, Service stratila eligible endpointy, vznikli duplicate authorizations alebo sa secret dostal do values či release storage.

## 3. Chart artifact, chart metadata a toolchain

Chart je versionovaný package. Typicky obsahuje `Chart.yaml`, default `values.yaml`, optional `values.schema.json`, templates, helpers, dependencies, CRDs a ďalšie packaged files. Source directory je authoring workspace, nie automaticky production artifact. Reproducibilný release identifikuje packaged chart alebo OCI manifest immutable digestom a dokáže spätne preukázať, z akých source a dependency bytes vznikol.

```text
source C57
→ dependency resolution podľa reviewed locku D57
→ lint, render a policy tests
→ packaged chart
→ OCI publication CH57
→ promotion rovnakého digestu
```

`Chart.yaml` oddeľuje viac identít. `version` označuje chart package contract; `appVersion` je informačná metadata a sama nemení image reference; image tag alebo digest identifikuje application artifact. `kubeVersion` môže obmedziť podporovaný Kubernetes range, ale nenahrádza server-side validation proti reálnemu API a admission konfigurácii.

Release subject zahŕňa aj Helm major/minor version, command flags, plugins, post-renderers, storage driver a Kubernetes endpoint. Helm 4 je aktuálny stable major a priniesol zmeny v architektúre a CLI/SDK boundaries; Helm 3 je v ukončovanom support lifecycle. Produkčný pipeline preto nesmie spoliehať na neurčité `helm latest`. Toolchain sa pinne a jeho upgrade sa testuje ako zmena release mechanizmu, nie ako administratívny detail.

## 4. Values ako versionované configuration API

Values nie sú iba premenné pre templating. Tvoria verejné configuration API chartu. Každý významný field potrebuje definovaný typ, default, allowed values, ownership, sensitivity, compatibility a väzbu na výsledný Kubernetes alebo external behavior. Zmena values môže vyvolať iba metadata diff, ale môže tiež nahradiť Pod template, zmeniť Service selector, aktivovať migration hook alebo prepnúť writer authority.

Effective values vznikajú precedence merge-om chart defaults, parent/subchart mappings, jedného alebo viacerých `-f` súborov a CLI overrides. Poradie je súčasťou subjectu. Samotný `values-prod.yaml` preto nereprezentuje production configuration, ak ho prepisuje region-specific file alebo `--set-string image.digest=...`.

```text
chart defaults
→ parent a dependency mappings
→ values-prod.yaml
→ values-prod-eu1.yaml
→ explicitné CLI overrides
→ effective values V57
```

Incident-safe evidence uchováva redacted effective values, poradie a digests vstupov, schema verdict a zoznam secret references bez plaintextu. Kritické values majú aj semantic invariants. Napríklad `legacyAuthorizer.enabled=false` musí znamenať, že legacy endpoint, environment field a policy fragment sa vôbec nevyrenderujú. JSON schema dokáže kontrolovať typy a required fields, ale pravidlo medzi viacerými fields alebo zákaz mutable image tagu potrebuje semantic test.

## 5. Render generation a deterministickosť

Render je vlastná evidence generation. Vzniká kombináciou chartu, dependencies, effective values, release name/namespace, Helm engine, API capabilities a optional dynamic inputs. Rovnaká chart version nemusí vytvoriť rovnaký manifest, ak sa zmení values order, dependency digest, `lookup` result, random/time function, plugin alebo post-renderer.

```text
CH57 + D57 + V57
+ release identity
+ Helm/toolchain generation
+ target capabilities
+ optional lookup/post-renderer
→ manifest M57
```

Built-in objects majú odlišnú authority. `.Values` nesie effective configuration, `.Chart` package metadata, `.Release` operation context, `.Capabilities` pohľad na API inventory a `.Files` packaged content. Tieto vstupy nesmú byť zamieňané. Napríklad `.Capabilities` z lokálneho renderu nemusí zodpovedať target clusteru a live `lookup` môže urobiť render závislý od momentálneho cluster state-u.

Deterministický chart vytvorí pri rovnakom subjecte rovnaký semantic manifest. Generovanie credentialu alebo certifikátu počas každého renderu, časová hodnota v Pod template alebo mutable dependency resolution spôsobujú perpetual diff a komplikujú rollback aj incident reconstruction. Dynamic behavior sa povoľuje iba s explicitnou authority, lifecycle a testom opakovateľnosti.

## 6. Validation ladder

Žiadny jednotlivý Helm command nepokrýva celý release contract. Validácia preto postupuje cez viac hraníc. Chart structure, dependency lock a values schema zachytia authoring chyby. Template execution a YAML parse zachytia render chyby. Kubernetes schema, discovery a server dry-run overia current API. Admission môže object mutovať alebo odmietnuť. Apply/update semantics môžu zlyhať na immutable fielde alebo ownership konflikte. Až controllers, workload a business canary overia effective outcome.

```text
package a lock
→ values schema a semantic fixtures
→ deterministic render
→ YAML a Kubernetes object validation
→ server dry-run a admission result
→ semantic diff proti current state-u
→ bounded release mutation
→ rollout a serving cohort
→ process-loaded generation
→ business acceptance
```

`helm lint` ani `helm template` nepreukazujú target RBAC, admission, current immutable fields alebo runtime behavior. `helm status` zase nepreukazuje, že traffic smeruje iba na novú cohortu. Každý zelený výsledok musí byť interpretovaný podľa presnej boundary, ktorú skutočne meria.

## 7. Release mutation, revision a unknown outcome

Helm upgrade nie je distribuovaná transakcia cez všetky Kubernetes objekty a external side effects. Helm vyrenderuje desired set, odošle viac API requests, podľa flags čaká na vybrané readiness conditions a uloží revision state. Medzitým controllers pokračujú asynchrónne. Časť objektov môže byť aktualizovaná pred zlyhaním ďalšieho requestu a hook môže commitnúť durable side effect skôr, než command skončí non-zero.

Timeout preto nevypovedá, že sa nič nestalo. Vytvára unknown outcome, ktorý sa rieši read-backom release history, Helm-stored manifestu, live object generations, hook Jobs a external operation ledgeru. Blind retry môže vytvoriť ďalšiu revision, opakovať migration alebo prebiť novší writer state.

Helm revision je lokálna lifecycle identity release-u. Evidence musí vytvoriť koreláciu `C57 → CH57/D57/V57 → M57 → revision 18 → object UID/generation → Pod I57/config epoch → payment P-884`. Release storage je citlivý subject, pretože môže obsahovať chart, values a manifests. Nie je náhradou za Git, registry, secret manager ani application-data backup.

## 8. Desired, admitted, live a effective state

Rendered manifest nie je posledná vrstva. API defaulting a mutating admission môžu objekt zmeniť. HPA, operator, GitOps controller, manual edit alebo iný field manager môžu vlastniť ďalšie fields. Controller potom vytvorí ReplicaSets a Pody a aplikácia môže configuration načítať iba pri štarte.

```text
versionovaný source
→ effective values V57
→ rendered M57
→ admitted object
→ live desired spec
→ controller child generation
→ serving Pod cohort
→ process-loaded configuration
→ business behavior
```

Drift sa preto klasifikuje podľa authority. HPA-owned replicas nie sú rovnaký problém ako manual image patch. Admission-injected sidecar nie je rovnaký problém ako dependency helper, ktorý prepísal Service selector. Pri false-green release musí byť možné nájsť prvú generation, na ktorej sa očakávaný a skutočný stav rozišli.

## 9. Connected incident: explicitné `false` sa zmenilo na `true`

CI vykonalo revision 18 nad `CH57`, `D57` a `V57`. Helm skončil úspešne, Deployment bol Available a technický health endpoint bol green. Payment audit však ukázal, že request `P-884` stále použil legacy authorizer, hoci effective values explicitne obsahovali `legacyAuthorizer.enabled: false`.

Prvé hypotézy pokrývali wrong values order, CLI override, helper/dependency drift, admission mutation, stale Pody, old traffic cohort a omyl v cluster identity. Rozlišujúce evidence bolo rozdielne pre každú z nich: CI command a `helm get values --all` overili effective input; exact render M57 ukázal template output; packaged chart a lock overili helper graph; server response a managed fields overili admission; ReplicaSet/Pod creation time a EndpointSlices overili serving cohortu.

Root cause bol template výraz:

```gotemplate
legacyAuthorizerEnabled: {{ .Values.legacyAuthorizer.enabled | default true }}
```

Helm/Sprig `default` považoval explicitné boolean `false` za empty. Render M57 preto obsahoval `true` a Helm aj Kubernetes korektne vykonali nesprávny desired state. `deployed` nebol klamlivý Helm status; klamlivé bolo jeho použitie ako business verdictu.

Containment zastavilo ďalšie release retries, zachovalo CH57/D57/V57/M57, release storage, audit a Pod evidence a obmedzilo legacy path bez vymazania histórie. Recovery zmenila template tak, aby odlišoval missing value od explicitného `false`, pridala schema a golden-render fixtures, vytvorila chart `CH58` a manifest `M58`, vykonala server validation a rollout revision 19.

Acceptance vyžadovala viac než green rollout. Všetky active endpoints museli patriť revision 19, legacy fields nesmeli existovať v rendered ani live state-e, synthetic payment musel použiť nový authorizer presne raz a druhý render rovnakého subjectu musel vytvoriť rovnaký manifest digest. Negative test zároveň potvrdil, že broken CH57 už nie je promotion target.

## 10. Secrets, uninstall a decommission

Values a release storage nie sú secret manager. Plaintext môže uniknúť cez Git history, CLI/CI logs, rendered manifest, `helm get`, debug output alebo Kubernetes Secret s nedostatočným RBAC a encryption modelom. Preferovaný model používa versionované references na external secret, workload identity alebo encrypted source workflow. Evidence koreluje opaque generation, checksum alebo resourceVersion bez publikovania payloadu.

`helm uninstall` odstráni iba objekty v Helm-managed release inventory podľa current semantics. Nemusí odstrániť CRDs, retained hooks, PVC/PV, operator-created dependents, external DNS/LB/IAM resources, credentials, backup copies alebo právne retention artifacts. Decommission preto začína complete subject inventory, pokračuje traffic a writer fencingom a končí negative tests, že stará identity ani endpoint už nie sú použiteľné.

## 11. Rollback, roll-forward a durable state

Helm rollback obnovuje starší Helm-stored chart/config/manifest intent a vytvorí ďalšiu revision. Nevracia automaticky database schema, CRD storage version, hook side effect, external resource, credential generation ani data zapísané novou application version. Rozhodnutie sa preto robí podľa current durable state-u a compatibility matrixu.

Rollback je vhodný, keď starý application/chart contract je kompatibilný s current data a external state-om a predstavuje najmenší bezpečný change. Roll-forward je vhodnejší po irreversible migration, novom event contracte alebo vtedy, keď malý fix obnoví correctness bez návratu nekompatibilného writera. Compensation alebo restore sú samostatné recovery mechanizmy a nemajú byť skryté pod jedným tlačidlom `rollback`.

## 12. Troubleshooting a acceptance contract

Pri release incidente sa postupuje od immutable inputs k business outcome-u. Najprv sa potvrdí cluster endpoint, namespace a release identity. Potom chart/dependency/values/render generations, Helm revision a admitted live objects. Následne sa overia controllers, serving cohorts, loaded configuration a request trace. Prvá odlišná generation určí failure boundary a zabráni náhodnému editovaniu viacerých vrstiev naraz.

Produkčný acceptance record má obsahovať release intent a approvera, cluster identity, Helm/toolchain generation, source/chart/dependency/values/render digests, server/admission evidence, revision, live UID/generation inventory, image/config/secret epochs, hook a external side effects, business canary a recovery/decommission boundary. Takýto record umožňuje bezpečný retry aj vysvetliteľný incident.

Najčastejšie anti-patterny sú zamieňanie chart version, appVersion a release revision; mutable chart alebo dependency reference; rekonštrukcia effective values z jedného file-u; plaintext secrets vo values; local render interpretovaný ako runtime verdict; timeout okamžite retryovaný bez read-backu; manual patch bez authority rozhodnutia; rollback považovaný za zvrátenie durable side effects a uninstall považovaný za kompletný decommission.

## Kontrolné otázky

1. Ktoré identity tvoria exact Helm release subject a prečo sa nesmú zlúčiť?
2. Ako vznikajú effective values a prečo je poradie vstupov súčasťou evidence?
3. Ktoré inputs môžu zmeniť render bez zmeny chart version?
4. Čo presne preukazuje Helm revision a čo musí overiť Kubernetes/runtime evidence?
5. Prečo timeout alebo `failed` status nevypovedá, že nevznikol side effect?
6. Ako sa desired, admitted, live, serving a process-loaded state líšia?
7. Kedy je rollback bezpečný a kedy je potrebný roll-forward alebo reconciliation?
8. Ktoré positive a forbidden outcomes musia uzavrieť release acceptance?

## Glossary impact

Relevantné pojmy: Helm release subject, chart artifact generation, dependency lock generation, effective values, render generation, rendered-manifest digest, release revision, release mutation boundary, unknown Helm outcome, admitted/live/serving/process-loaded state, release acceptance, rollback eligibility a Helm decommission subject.

## Primárne zdroje

- [Helm documentation](https://helm.sh/docs/)
- [Helm 4 Overview](https://helm.sh/docs/overview/)
- [Charts](https://helm.sh/docs/topics/charts/)
- [Chart Template Guide](https://helm.sh/docs/chart_template_guide/)
- [Values Files](https://helm.sh/docs/chart_template_guide/values_files/)
- [Helm Version Support Policy](https://helm.sh/docs/topics/version_skew/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Kubernetes troubleshooting](../09-kubernetes/kubernetes-troubleshooting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Praktický Helm chart od prázdneho adresára po overený release →](helm-chart-practical-walkthrough.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
