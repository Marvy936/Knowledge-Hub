# Helm and CKA

Táto sekcia vysvetľuje Helm ako package, render a release-lifecycle mechanizmus nad Kubernetes a CKA ako praktickú administrátorskú disciplínu založenú na presnej identifikácii subjectu, bounded mutation a hard validation. Nejde o memorovanie CLI príkazov ani o skrátenie YAML-u. Každá kapitola sleduje, ako versionovaný chart, dependencies, values, helpers, hooks a release transitions vytvárajú konkrétny Kubernetes a business outcome a ako sa pri zlyhaní nájde prvá divergentná boundary.

Helm status, Kubernetes readiness a úspešný exam command sú iba čiastkové verdicts. Sekcia preto oddeľuje source, render, admitted/live state, serving workload, process-loaded configuration, durable side effects a používateľský outcome. CKA časti používajú rovnaký model pod časovým tlakom: správny context a resource identity, evidence pred mutation, najmenšia bezpečná oprava, positive aj forbidden validation a reprodukovateľný learning loop.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md),
- [Kubernetes](../09-kubernetes/README.md),
- [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md).

## Authoritative poradie — aktívne kapitoly

1. [Helm chart, template, values a release](helm-chart-template-values-release.md)
2. [Template functions a pipelines](template-functions-pipelines.md)
3. [Named templates](named-templates.md)
4. [Chart dependencies](chart-dependencies.md)
5. [Hooks](hooks.md)
6. [Upgrade a rollback](upgrade-rollback.md)
7. [Helm testing a troubleshooting](helm-testing-troubleshooting.md)
8. [CKA timed labs](cka-timed-labs.md)
9. [CKA troubleshooting drills](cka-troubleshooting-drills.md)

Aktuálny authoritative stav sekcie je **9/9 · Ready for user review**.

## Completion state

Všetkých deväť kapitol bolo po pôvodnom authoring passe kompletne znovu spracovaných podľa prose-first strict štandardu sekcií 14–17. Každá kapitola má explicitný subject/generation/evidence model, connected failure alebo training scenario, vysvetlený recovery lifecycle a positive aj forbidden acceptance paths. Per-file gate vykazuje nulové critical, high a medium learning-depth findings.

Finálny comparative pass bol dokončený **30. júla 2026**. Authoritative ordering, navigation, technické identity a incidentové fakty zostali zachované. Sekcia je pripravená na používateľskú kontrolu; tento stav ju automaticky neoznačuje ako používateľsky schválenú, Accepted, Verified ani Stable.

## Connected learning scenarios

### Helm render a dependency authority

Atlas Payments release používa chart `CH57`, dependency lock `D57`, values `V57`, manifest `M57`, image `I57` a source commit `C57`. Explicitné `legacyAuthorizer.enabled=false` sa cez Sprig `default` zmenilo na `true`; Helm aj Kubernetes preto korektne vykonali nesprávny render. Samostatný dependency incident ukazuje, ako chýbajúci `Chart.lock` dovolil production CI znovu resolve-nuť library chart `1.6.3/LD58`, prepísať global selector helper a vytvoriť immutable-field failure.

```text
reviewed source a dependency intent
→ exact chart/lock/values/toolchain subject
→ deterministic render
→ API/admission a live generation
→ serving a process-loaded behavior
→ business request P-884
→ authoritative template/dependency recovery
→ deterministic second render a forbidden-path test
```

### Hooks, upgrade a business-compatible recovery

Pre-upgrade hook `atlas-payments/schema-expand/19` commitol schema transition `S12 → S13`, ale Helm timeoutoval pred uložením successful verdictu. Durable operation ledger umožnil controlled retry ako no-op verification namiesto druhej migration. Neskorší upgrade z revision 19 na 20 zaviedol image `I58`, schema `S14` a event `E2`; automatic rollback na revision 21 bol technicky deployed, no old consumer `I57` nevedel spracovať E2 backlog. Recovery preto použila roll-forward revision 22 s tolerantným `I58.1`.

```text
release transition subject
→ hook operation a durable side effects
→ Kubernetes rollout a mixed cohorts
→ technical verdict
→ schema/event/credential compatibility
→ business outcome
→ rollback eligibility alebo roll-forward
→ exactly-once a forbidden-outcome closure
```

### CKA execution a diagnosis pod časom

Timed lab `CKA-MIXED-42` ukazuje, že správny rollout command v nesprávnom contexte mení nesprávny Deployment. Troubleshooting drill `CKA-NET-17` ukazuje Service flow zlyhávajúci iba z Node generation `NG42`, hoci Node aj dataplane DaemonSet hlásili readiness. Oprava vytvorila immutable Node generation `NG43` a capability canary overil PodIP, ServiceIP, DNS aj NetworkPolicy allow/deny paths.

```text
exact exam/lab a task subject
→ current-state evidence
→ competing hypotheses
→ discriminating observation
→ minimálna authoritative repair
→ controller/runtime reconvergence
→ positive a forbidden validation
→ targeted follow-up drill
```

## Dominantný model sekcie

```text
versionovaný release alebo task intent
→ exact chart/dependency/values/context subject
→ render alebo current-state observation
→ validation a bounded mutation
→ Kubernetes/controller convergence
→ serving a process-loaded state
→ business alebo exam outcome
→ recovery, rollback, roll-forward alebo targeted drill
→ second-operation a lifecycle closure
```

Komplexné kapitoly dôsledne rozlišujú:

- chart source, dependency graph, values, render a release revision;
- rendered, admitted, live, serving a process-loaded state;
- API acceptance, controller readiness a business correctness;
- hook resource, execution attempt, durable side effect a Helm verdict;
- technical rollback a business-compatible recovery;
- object existence a hard outcome validation;
- root cause, contributing control failure a symptom removal;
- prvý úspech a stabilný second render, retry alebo drill reset.

## Cieľ zvládnutia

Po dokončení sekcie má byť možné reprodukovateľne zostaviť a vysvetliť Helm release subject, navrhnúť typed values a helper contracts, uzamknúť celý dependency graph, modelovať hooks ako idempotentné durable operations a rozlíšiť rollback, roll-forward, compensation a restore podľa current state-u. Testovanie má vedieť preukázať rovnaký artifact od source-u cez render a admission po serving cohortu, loaded configuration a business outcome.

V CKA časti má byť možné pod časovým tlakom zachovať context discipline, zvoliť vhodnú imperative alebo declarative execution path, identifikovať failure domain, chrániť volatile evidence, vybrať diskriminačné pozorovanie a uzavrieť task positive aj forbidden validation. Výsledky timed labov a troubleshooting drillov sa majú meniť na konkrétne targeted cvičenia, nie na neurčitý cieľ „viac sa učiť“.

## Aktuálny CKA contract

K **30. júlu 2026** je CKA online proctored performance-based skúška s trvaním **2 hodiny** a environmentom Kubernetes **v1.35**. Doménové váhy sú Troubleshooting 30 %, Cluster Architecture, Installation and Configuration 25 %, Services and Networking 20 %, Workloads and Scheduling 15 % a Storage 10 %. Pred reálnou skúškou treba tieto temporálne premenlivé parametre znovu overiť v oficiálnych materiáloch Linux Foundation.

## Praktické oblasti

- [CKA timed labs](../../labs/cka/README.md)
- [CKA troubleshooting drills](../../troubleshooting/cka/README.md)

Praktické sety materializujú modely tejto sekcie ako resetovateľné initial states, task sheets, fault injections a hard-validation scripts. Výsledky sa vracajú do learning loopu podľa konkrétnej chyby v knowledge, context-e, diagnosis, repair, validation alebo time management-e.

## Primárne zdroje

- [Helm documentation](https://helm.sh/docs/)
- [Helm 4 Overview](https://helm.sh/docs/overview/)
- [Linux Foundation — Certified Kubernetes Administrator](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/)
- [Kubernetes documentation](https://kubernetes.io/docs/)
