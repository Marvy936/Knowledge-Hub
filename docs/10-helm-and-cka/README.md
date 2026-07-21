# Helm and CKA

Táto sekcia nadväzuje na Kubernetes a rozvíja Helm packaging, templating, release lifecycle a praktické cluster-administration zručnosti pre CKA.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Kubernetes](../09-kubernetes/README.md),
- [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md),
- [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md).

## Odporúčané poradie

1. [Helm chart, template, values a release](helm-chart-template-values-release.md)

Nasledujúci blok doplní template functions a pipelines, named templates, chart dependencies, hooks, upgrade a rollback a Helm testing a troubleshooting. Potom sekcia prejde na CKA timed labs a troubleshooting drills.

## Cieľ zvládnutia

Po dokončení aktuálneho bloku má byť možné:

- rozlíšiť Helm chart, values, rendered manifest, live Kubernetes resources a release state,
- vysvetliť chart version, `appVersion` a release revision,
- orientovať sa v `Chart.yaml`, `values.yaml`, `values.schema.json`, `templates/`, `charts/` a `crds/`,
- používať `.Values`, `.Chart`, `.Release`, `.Capabilities`, `.Files` a `.Template`,
- vysvetliť values precedence a YAML typing,
- používať `helm lint`, `helm template` a server-side dry-run ako samostatné validačné vrstvy,
- rozlíšiť install, upgrade, rollback, uninstall a release history,
- navrhnúť versionovaný chart distribution cez repository alebo OCI registry,
- diagnostikovať template, API validation, rollout, drift a release-state problémy.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Helm chart, template, values a release | Learning | L2 |