# Helm testing a troubleshooting

Helm testing nemá dokazovať iba to, že chart sa dá vyrenderovať alebo nainštalovať. Má vytvoriť súvislý dôkaz, že konkrétny immutable release subject prešiel od source artifactu cez dependency resolution, render, API a Kubernetes reconciliation až po očakávaný runtime a business outcome.

Troubleshooting používa ten istý model opačným smerom. Začína symptómom, fixne exact release a runtime subject a hľadá prvú boundary, na ktorej sa očakávaný state odlišuje od pozorovaného. Náhodné preskakovanie medzi template source-om, Pod logs a release Secrets zvyšuje riziko straty evidence aj nesprávnej recovery.

## 1. Dominantný evidence lifecycle

Každá testovacia vrstva odpovedá na inú otázku. Lint môže potvrdiť chart structure, ale nie production values. Render môže byť deterministický a napriek tomu server admission object odmietne. Deployment môže byť Available a časť processov môže používať starú credential generation.

```text
release risk a acceptance contract
→ immutable chart/dependency/values/render subject
→ expected evidence inventory
→ schema, helper a deterministic render tests
→ API, admission a policy validation
→ install/upgrade/rollback/uninstall lifecycle
→ Kubernetes a serving-cohort convergence
→ Helm tests a application synthetics
→ business a forbidden-outcome acceptance
→ incident hypotheses a discriminating evidence
→ containment, authoritative recovery a regression closure
```

Zelená vrstva nepreukazuje automaticky nasledujúcu. `lint success ≠ valid production render ≠ API acceptance ≠ ready serving cohort ≠ loaded configuration ≠ business correctness`. Test report preto musí pomenovať presnú boundary a artifact, ktorú overil.

## 2. Exact Atlas test subject

Atlas Payments prechádza zo source revision 22 na target revision 23. Target používa chart `CH59`, dependency lock `D59`, values `V59`, manifest `M59`, image `I59`, credential epoch `SE10` a cluster generation `K136`.

Complete subject zahŕňa aj Helm a deployment-engine generation, target context/namespace, expected resource a hook inventory, operation IDs, image/config/credential generations a technical, security, business a forbidden outcomes. Bez týchto identities sa môže lint týkať source directory, ephemeral install iného package-u a production test mutable tagu.

Promotion model preto package-ne chart raz, vypočíta digest a všetky reports viaže na rovnaký CH59. Rebuild alebo dependency update medzi testom a promotion vytvára nový subject a pôvodné evidence sa naň nevzťahuje.

## 3. Expected evidence inventory

Pred spustením pipeline sa definuje, aký dôkaz musí každá vrstva vyprodukovať. Inventory zahŕňa chart metadata/digest, dependency lock a artifacts, effective values digest, manifest digest, schema/helper assertions, server/admission verdict, release revision a hooks, live UID/generations, Pod image a loaded config/credential epochs, EndpointSlice cohort, application synthetic, business ledger a negative tests.

Green job bez reportu alebo bez väzby na promoted digest nie je complete evidence. Rovnako nepostačuje iba link na transient CI log. Critical results sa archivujú v redacted forme, majú timestamp, tool/policy generation a definovanú invalidation podmienku.

Evidence sa invaliduje pri zmene chartu, dependency, values, Kubernetes/API policy, target cluster generation alebo external compatibility contractu. Staging install na inom admission profile nie je production acceptance.

## 4. Test pyramid od source po business outcome

Najlacnejšie testy zachytávajú chyby blízko source-u: metadata, lock, values schema, helper fixtures a deterministic render. Ďalšie vrstvy parsujú YAML, validujú Kubernetes schema a policy a používajú server dry-run/admission. Realistický cluster následne overí install, upgrade z podporovanej previous revision, rollback/roll-forward a uninstall.

`helm test` a application synthetics sú vyššie vrstvy. Majú vedieť overiť DNS/request path, authentication, schema endpoint, read-only transaction, expected runtime generations a dependency reachability cez application path. Business synthetic navyše overuje settlement ledger, idempotency a forbidden side effects.

Pyramída neznamená, že vyšší test opraví nedostatok nižšieho. Cohort-aware production canary nemá byť jediným miestom, ktoré odhalí `default true` nad explicitným false. Regression sa pridáva na najskoršej spoľahlivej boundary a zároveň sa zachová end-to-end acceptance.

## 5. Artifact, dependency a values gates

Artifact gate overuje chart name/version/type, exact lock, first-level aj transitive dependency digests, source registry, packaged chart digest a inventory hooks, CRDs, RBAC a images. `helm dependency update` sa v release/test jobe nepoužíva, pretože môže vytvoriť iný graph než reviewovaný subject.

Values matrix nepoužíva iba defaults. Zahŕňa production-like config, feature on/off, explicitné false/zero/empty/null, dependency modes, replica/resource bounds, ingress/gateway variants, supported API generations a upgrade values zo current production revision. Každý case má semantic oracle, napríklad `feature=false` znamená absent resource aj false process flag, nie iba successful render.

Schema kontroluje typy a structure; semantic assertions kontrolujú identity, selectors, ServiceAccount, image digest, hook lifecycle a rollout epochs. Snapshot diff bez vysvetlenia významných fields nie je acceptance verdict.

## 6. Deterministic render a helper assertions

Target render sa opakuje nad rovnakým chartom, lockom, values, release identity a capabilities. Semantic manifest digest musí zostať rovnaký. Neplánovaný `lookup`, `now`, random output, mutable dependency alebo helper collision gate zlyhá.

High-blast-radius assertions sledujú names, selectors/Pod labels, Service ports, images, RBAC, securityContext, hooks, checksum/epoch annotations, dependency enablement a API-version branching. Test porovnáva stable fields medzi current a target revision a explicitne povoľuje iba intended changes.

Ak chart používa cluster-dependent capabilities alebo lookup, evidence zaznamená server-connected render identity a observed objects. Local `helm template` sa vtedy nesmie interpretovať ako production-equivalent output bez exact capabilities.

## 7. API, admission, policy a cluster validation

Local YAML parse zachytí syntax a časť schema chýb. Server dry-run pridá current API discovery, OpenAPI/CRD schema, admission mutation/denial, RBAC, quota, Pod Security a namespace-specific policy. Ani server dry-run však nespustí controllers, scheduler, volume attach, CNI alebo application.

Policy verdict sa viaže na M59 a versionovanú policy generation. Kontroluje privileged/host authority, capabilities/seccomp, workload-creation RBAC escalation, mutable images, plaintext secret material, hook authority, resources, NetworkPolicy/PDB contract a cluster-scoped resources.

Ephemeral cluster potrebuje relevantnú fidelity: rovnaký Kubernetes/API range, admission/Pod Security, CNI/CSI/DNS assumptions, StorageClass, quotas a test identities. Fresh install je iba jeden scenario; samostatne sa testuje upgrade zo supported previous state-u s retained values, PVC/data, old selectors a mixed application cohorts.

## 8. Upgrade, recovery a decommission tests

Upgrade-path test začína revision 22 s representative data, config a credential generations a prejde cez target hooks, migrations, mixed-version interval a business acceptance. Testuje renamed/removed values, immutable fields, pending/timeout recovery, external side effects a rollback eligibility.

Rollback test neoveruje iba `helm status`. Posudzuje compatibility old application s current schema, events a credentials. Roll-forward test overuje opravu po irreversible change. Uninstall/decommission test kontroluje retained PVC/CRD/hook/external resources a negative evidence, že stará identity alebo endpoint už nefungujú.

Failure injection je cielený: strata response po hook commit-e, partial API mutation, delayed rollout alebo stale secret reload. Recovery musí použiť rovnaký operation identity a nevytvoriť duplicate side effect.

## 9. `helm test` a cohort-aware acceptance

Chart test je point-in-time hook. Má exact release/generation, least-privilege identity, bounded deadline, explicitný exit status, idempotentnú alebo read-only operáciu a retained logs. Nie je monitoring, load test ani automaticky complete multi-replica validation.

Jeden request môže zasiahnuť jediný zdravý Pod. Replicated workload preto eviduje všetky serving Pod UIDs, image digest, process-loaded config/credential epoch, EndpointSlice target references a repeated request-to-backend correlation. Test buď priamo enumeruje cohortu, alebo opakuje synthetic tak, aby preukázal každú eligible backend identity.

External user path môže zahŕňať DNS, TLS, Gateway alebo CDN, zatiaľ čo `helm test` volá ClusterIP. Business acceptance preto testuje aj relevantný external route a provider/ledger outcome.

## 10. Release evidence a troubleshooting domains

Pri incidente sa zachová `helm status/history/get values/get manifest/get hooks`, ale tieto commands dokazujú iba Helm-stored state. Nehovoria automaticky, ktorý Pod prijíma traffic alebo čo process načítal.

Troubleshooting domains sa prechádzajú v poradí od artifact/dependency fetchu cez values/schema, render/helper/YAML, API/admission, hook/external operation, release storage/concurrency, Kubernetes reconciliation, network/storage a application/business outcome. Prvá failing boundary určuje ďalšie observations.

Incident subject fixuje cluster/context/namespace, release a source/target/current revisions, chart/dependency/values/render digests, live UIDs/generations, Pod/image identities, config/credential/data generations, request/transaction ID, timeline a recent change. Až potom sa vytvoria competing hypotheses a vyberú diskriminačné observation points.

## 11. Connected incident: Helm aj test green, polovica requests vracia 401

Revision 23 menila external database credential z epoch `SE09` na `SE10`. Desired state aktualizoval secret-provider reference aj application `credentialEpoch`; provider ponechal overlap, kým rollout nemal convergovať, a po acceptance sa mal SE09 revoke-nuť.

Helm status bol deployed a `helm test` vykonal jeden úspešný request. Po revokácii SE09 však približne polovica production requests vracala 401 z database proxy. Subject zahŕňal CH59/D59/V59/M59, Secret generation SE10, štyri serving Pody `P59a–P59d`, EndpointSlice cohortu a provider audit.

Hypotézy pokrývali wrong values/render, external-secret failure, stale projection, stale process cache, old release cohort, provider/tenant chybu, wrong network backend a test, ktorý trafil iba healthy Pod.

Archived V59 a M59 správne požadovali SE10. Kubernetes Secret aj mounted files obsahovali SE10. Per-process telemetry však ukázala, že P59a/P59b reloadli SE10, zatiaľ čo P59c/P59d stále používali SE09. Všetky štyri Pody boli Ready a serving; Helm test trafil P59a.

Kauzálny chain bol:

```text
Secret reference sa zmení
→ Pod template generation sa nezmení
→ reload je best-effort
→ readiness neoveruje loaded epoch
→ single-request test neoverí cohortu
→ SE09 sa revoke-ne
→ stale processes vracajú 401
```

Containment zastavilo credential automation, vyradilo stale Pody z trafficu alebo ich bounded restartlo a zachovalo per-Pod/provider evidence. Chart ani Secret sa nevracali naslepo; krátky overlap SE09 bol možný iba podľa security policy počas drain-u.

Recovery pridala non-secret `credentialEpoch: SE10` do Pod template annotation, čím vznikla nová Deployment generation. Rollout prebehol po cohorts, readiness overovala process-loaded SE10 a test koreloval repeated requests so všetkými serving Pod UIDs. SE09 sa revoke-ol až po complete cohort acceptance.

Verification potvrdila SE10 na každom serving Pode, absence stale UID v EndpointSlice, successful synthetics cez všetky cohorts, denial SE09, acceptance SE10, jednu ledger transaction pre P-884 a nulové 401 z epoch mismatchu.

## 12. Recovery hierarchy a regression closure

Preferovaný recovery order opravuje authoritative source/effective values a vytvorí novú revision; potom dokončí alebo state-aware zopakuje idempotentný hook; použije roll-forward; rollback iba pri preukázanej eligibility; compensation pre external side effect a restore iba pri skutočnej data/control-plane recovery.

Closure vyžaduje exact subject, scope/timeline, current-target-live comparison, competing hypotheses, preserved volatile evidence, bounded containment, authoritative fix, original aj forbidden outcomes, adjacent cohorts/failure domains, stable second render/retry/reconcile a regression test na najskoršej spoľahlivej vrstve.

Najčastejšie anti-patterny sú defaults-only test, mutable artifact medzi testom a release, snapshot bez semantics, fresh install považovaný za upgrade test, single-request Helm test, mounted Secret považovaný za loaded state, debug dump secrets, timeout retry bez observation a ručné mazanie release Secrets pri runtime chybe.

## Kontrolné otázky

1. Čo tvorí immutable Helm test subject a expected evidence inventory?
2. Prečo jedna zelená vrstva nepreukazuje ďalšiu?
3. Ktoré cases musí obsahovať values a upgrade matrix?
4. Ako sa release evidence líši od live, serving a process-loaded evidence?
5. Čo `helm test` dokazuje a čo musí doplniť cohort-aware synthetic?
6. Ako server/admission validation dopĺňa local render?
7. Prečo mounted credential generation nemusí byť loaded generation?
8. Ako sa incident finding premení na skorší regression control?

## Practical gate: od lint-u po runtime failure, ktorý readiness neodhalí

Jedna zelená kontrola je slabý dôkaz. Praktický gate používa rovnaký chart artifact v niekoľkých vrstvách a na každej presne pomenuje, čo bolo overené.

```bash
helm lint ./atlas-payments

helm template payments-dev ./atlas-payments \
  -n payments-dev \
  > /tmp/payments.yaml

kubectl apply --server-side --dry-run=server \
  -f /tmp/payments.yaml

helm upgrade --install payments-dev ./atlas-payments \
  -n payments-dev \
  --create-namespace \
  --wait \
  --timeout 5m

kubectl rollout status deployment/payments-dev-atlas-payments \
  -n payments-dev --timeout=3m

helm test payments-dev -n payments-dev --logs
```

`lint` kontroluje chart conventions a časť template problémov. `template` materializuje effective values. Server dry-run zapája API a admission. Upgrade vytvára release a controllers. Rollout status overuje Deployment readiness. Až Helm test alebo samostatný business canary overí cestu cez Service k aplikácii.

Dobrý fault injection je chybný Service `targetPort`. Nasadiť ho možno bez zmeny Pod template-u:

```bash
helm upgrade payments-dev ./atlas-payments \
  -n payments-dev \
  --reuse-values \
  --set service.targetPort=9999 \
  --wait \
  --timeout 3m
```

Helm upgrade a Deployment rollout môžu zostať zelené, pretože Pods sú ready a Service resource nemá vlastnú application readiness. Helm test, ktorý volá Service, má zlyhať. Diagnostika potom sleduje request path, nie náhodný restart:

```bash
helm test payments-dev -n payments-dev --logs

kubectl get service payments-dev-atlas-payments \
  -n payments-dev -o yaml

kubectl get endpointslice -n payments-dev \
  -l kubernetes.io/service-name=payments-dev-atlas-payments \
  -o yaml

kubectl get pods -n payments-dev \
  -l app.kubernetes.io/instance=payments-dev \
  -o custom-columns=NAME:.metadata.name,POD_IP:.status.podIP,PORT:.spec.containers[0].ports[0].containerPort

kubectl run service-probe \
  -n payments-dev \
  --image=busybox:1.36 \
  --restart=Never \
  --rm -i \
  -- wget -S -O- http://payments-dev-atlas-payments
```

Service YAML ukáže effective `targetPort: 9999`; EndpointSlice preukáže, že selector našiel Pod IPs, nie že na cieľovom porte niečo počúva. Pod output ukáže reálny container port. Probe cez Service lokalizuje failure medzi Service port mappingom a process listenerom.

Recovery vráti approved port a zopakuje rovnaký gate:

```bash
helm upgrade payments-dev ./atlas-payments \
  -n payments-dev \
  --reuse-values \
  --set service.targetPort=8080 \
  --wait \
  --timeout 3m

helm test payments-dev -n payments-dev --logs
```

Second-operation test je dôležitý: zopakovaný upgrade s rovnakými values nesmie vytvoriť nový ReplicaSet, hook side effect ani configuration drift. Over ho cez `helm history`, ReplicaSet inventory a business request. Tým sa troubleshooting uzatvára stabilitou, nie iba jedným úspešným retryom.

## Glossary impact

Relevantné pojmy: Helm evidence lifecycle, immutable chart test subject, expected evidence inventory, values matrix oracle, deterministic render evidence, upgrade-path test, cohort-aware Helm test, release/runtime evidence boundary, incident subject, recovery hierarchy a troubleshooting closure.

## Primárne zdroje

- [Helm — `helm lint`](https://helm.sh/docs/helm/helm_lint/)
- [Helm — `helm template`](https://helm.sh/docs/helm/helm_template/)
- [Helm — `helm test`](https://helm.sh/docs/helm/helm_test/)
- [Helm — Debugging Templates](https://helm.sh/docs/chart_template_guide/debugging/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Upgrade a rollback](upgrade-rollback.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CKA timed labs →](cka-timed-labs.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
