# Helm and CKA

Táto sekcia vysvetľuje Helm ako package, render a release-lifecycle mechanizmus nad Kubernetes a CKA ako praktickú administrátorskú disciplínu. Mechanistický výklad však nie je náhradou za prácu s reálnymi súbormi a príkazmi. Preto sekcia kombinuje súvislé vysvetlenie s executable examples: úplným chartom, vyrenderovaným YAML-om, Helm a `kubectl` príkazmi, očakávanými výsledkami a vysvetlením, čo každý výsledok dokazuje a čo ešte nedokazuje.

Helm status, Kubernetes readiness a úspešný exam command sú iba čiastkové verdicts. Sekcia oddeľuje source, render, admitted/live state, serving workload, process-loaded configuration, durable side effects a používateľský outcome. CKA časti používajú rovnaký model pod časovým tlakom: správny context a resource identity, evidence pred mutation, najmenšia bezpečná oprava, positive aj forbidden validation a reprodukovateľný learning loop.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md),
- [Kubernetes](../09-kubernetes/README.md),
- [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md).

## Authoritative poradie — aktívne kapitoly

1. [Helm chart, template, values a release](helm-chart-template-values-release.md)
2. [Praktický Helm chart od prázdneho adresára po overený release](helm-chart-practical-walkthrough.md)
3. [Template functions a pipelines](template-functions-pipelines.md)
4. [Named templates](named-templates.md)
5. [Chart dependencies](chart-dependencies.md)
6. [Hooks](hooks.md)
7. [Upgrade a rollback](upgrade-rollback.md)
8. [Helm testing a troubleshooting](helm-testing-troubleshooting.md)
9. [CKA timed labs](cka-timed-labs.md)
10. [CKA troubleshooting drills](cka-troubleshooting-drills.md)

Aktuálny authoritative stav sekcie je **10 kapitol · practical-example remediation in progress**. Pôvodný prose-first pass zostáva platný, ale používateľská kontrola odhalila nedostatok konkrétnych chartov, príkazov, rendered outputs a vysvetlených diagnostických postupov. Sekcia preto zatiaľ nie je používateľsky schválená.

## Practical-example acceptance contract

Technická kapitola sa po tejto náprave nepovažuje za hotovú iba preto, že má súvislý text a strict audit `0/0/0`. Musí obsahovať primeraný executable surface. Pri Helme to znamená reálne `Chart.yaml`, `values.yaml`, schema, Go templates, rendered Kubernetes YAML a príkazy `helm lint`, `helm template`, `helm upgrade`, `helm history`, `helm get`, `helm test` a relevantné `kubectl` diagnostické príkazy.

Každý významný príkaz musí vysvetliť tri veci: aký subject číta alebo mení, aký úspešný alebo chybný výsledok očakávame a akú hranicu výsledok skutočne dokazuje. Napríklad `helm template` dokazuje lokálny render, nie admission ani runtime; server-side dry-run dokazuje API a admission verdict, nie rollout; `kubectl rollout status` dokazuje controller readiness, nie business correctness.

## Hlavný praktický walkthrough

Kapitola [Praktický Helm chart od prázdneho adresára po overený release](helm-chart-practical-walkthrough.md) vytvára celý chart `atlas-payments` od nuly. Obsahuje:

- `Chart.yaml` a vysvetlenie rozdielu medzi chart version, `appVersion` a image digestom;
- typed `values.yaml` a `values.schema.json`;
- `_helpers.tpl` so stabilnými labels, selectors a `required` guardom;
- Deployment, Service, ServiceAccount a Helm test Pod;
- bezpečné spracovanie explicitného boolean `false` bez chybného `default true`;
- lokálny render, kontrolu outputu cez `yq`, server-side dry-run a bounded install;
- upgrade, diff, history, runtime Service test, troubleshooting a rollback;
- package, digest, OCI promotion a decommission kontrolu.

Tento walkthrough je referenčný model pre doplnenie ďalších kapitol. Template functions dostanú malé vstup/output príklady; dependencies reálny `Chart.yaml`, `Chart.lock` a `helm dependency` flow; hooks reálny Job s delete policy a idempotency ledgerom; upgrade/rollback vysvetlený mixed-version scenár; troubleshooting príkazové rozhodovacie stromy.

## Connected learning scenarios

### Helm render a dependency authority

Atlas Payments release používa chart `CH57`, dependency lock `D57`, values `V57`, manifest `M57`, image `I57` a source commit `C57`. Explicitné `legacyAuthorizer.enabled=false` sa cez Sprig `default` zmenilo na `true`; Helm aj Kubernetes preto korektne vykonali nesprávny render. Praktický walkthrough teraz ukazuje chybný aj opravený template a príkaz, ktorým sa hodnota overí priamo vo vyrenderovanom Deploymente.

### Hooks, upgrade a business-compatible recovery

Pre-upgrade hook `atlas-payments/schema-expand/19` commitol schema transition `S12 → S13`, ale Helm timeoutoval pred uložením successful verdictu. Durable operation ledger umožnil controlled retry ako no-op verification namiesto druhej migration. Neskorší upgrade zaviedol image, schema a event generation, ktoré neboli kompatibilné so starým consumerom. Recovery preto použila roll-forward namiesto slepého rollbacku.

### CKA execution a diagnosis pod časom

Timed lab `CKA-MIXED-42` ukazuje, že správny rollout command v nesprávnom contexte mení nesprávny Deployment. Troubleshooting drill `CKA-NET-17` ukazuje Service flow zlyhávajúci iba z jednej Node generation. Každý drill musí používať konkrétne `kubectl` commands, expected observations a hard validation, nie iba opis postupu.

## Dominantný model sekcie

```text
versionovaný release alebo task intent
→ exact chart/dependency/values/context subject
→ executable input a render/current-state observation
→ validation a bounded mutation
→ Kubernetes/controller convergence
→ serving a process-loaded state
→ business alebo exam outcome
→ recovery, rollback, roll-forward alebo targeted drill
→ second-operation a lifecycle closure
```

## Cieľ zvládnutia

Po dokončení sekcie má byť možné nielen vysvetliť Helm release subject, ale aj samostatne napísať malý bezpečný chart, vyrenderovať ho, skontrolovať exact output, vykonať server validation, nasadiť ho, nájsť príčinu zlyhania a vysvetliť hranice rollbacku. V CKA časti má byť možné rovnakú disciplínu použiť pod časovým tlakom cez reprodukovateľné commands a dôkazové checkpoints.

## Aktuálny CKA contract

K **30. júlu 2026** je CKA online proctored performance-based skúška s trvaním **2 hodiny** a environmentom Kubernetes **v1.35**. Doménové váhy sú Troubleshooting 30 %, Cluster Architecture, Installation and Configuration 25 %, Services and Networking 20 %, Workloads and Scheduling 15 % a Storage 10 %. Pred reálnou skúškou treba tieto temporálne premenlivé parametre znovu overiť v oficiálnych materiáloch Linux Foundation.

## Praktické oblasti

- [CKA timed labs](../../labs/cka/README.md)
- [CKA troubleshooting drills](../../troubleshooting/cka/README.md)

## Primárne zdroje

- [Helm documentation](https://helm.sh/docs/)
- [Helm chart template guide](https://helm.sh/docs/chart_template_guide/)
- [Helm commands](https://helm.sh/docs/helm/)
- [Linux Foundation — Certified Kubernetes Administrator](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/)
- [Kubernetes documentation](https://kubernetes.io/docs/)