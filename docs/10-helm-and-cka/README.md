# Helm and CKA

Táto sekcia nadväzuje na Kubernetes a rozvíja Helm packaging, templating, dependency a release lifecycle a praktické cluster-administration zručnosti pre CKA. Helm obsah nebude postavený iba na CLI príkazoch; cieľom je rozumieť render graphu, values a helper contracts, release state-u, side effects, upgrade hraniciam a diagnostike.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Kubernetes](../09-kubernetes/README.md),
- [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md),
- [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md).

## Odporúčané poradie

1. [Helm chart, template, values a release](helm-chart-template-values-release.md)
2. [Template functions a pipelines](template-functions-pipelines.md)
3. [Named templates](named-templates.md)
4. [Chart dependencies](chart-dependencies.md)
5. [Hooks](hooks.md)

Nasledujúci Helm blok doplní upgrade a rollback a Helm testing a troubleshooting. Potom sekcia prejde na CKA timed labs a troubleshooting drills.

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
- diagnostikovať template, API validation, rollout, drift a release-state problémy,
- vysvetliť Helm template language ako Go templates, Helm helpers a Sprig functions,
- používať pipelines s vedomím, že ľavý výsledok sa posiela ako posledný argument ďalšej funkcie,
- rozlíšiť `default`, `coalesce`, `required`, `fail` a `hasKey` podľa missing/empty/explicit-value semantics,
- používať `dict`, `list`, merge/deep-copy, type conversion a YAML/JSON serialization bez skrytého coercion,
- správne kombinovať `toYaml`, `indent`, `nindent` a whitespace control,
- vyhodnotiť reprodukovateľnosť a security riziká `tpl`, `lookup`, random a time-dependent functions,
- používať `.Capabilities` a server validation pri API-version-dependent templates,
- vytvárať named templates cez `define` a používať `include` oproti `template` podľa pipeline a indentation potreby,
- vysvetliť globálny namespace helperov a predchádzať collision cez chart-prefixed alebo versioned names,
- navrhnúť explicitný helper scope a pseudo-signature cez `dict`,
- oddeliť stabilné selector labels od mutable common labels,
- navrhnúť stabilné fullname, image a ServiceAccount helpers bez upgrade alebo security regresie,
- používať `_helpers.tpl`, library charts a reusable fragments s dokumentovaným input/output contractom,
- vysvetliť application subchart ako stand-alone chart a parent override/global-values model,
- rozlíšiť dependency declaration, resolved graph, `Chart.lock` a obsah `charts/`,
- používať `helm dependency update` na re-resolution a `helm dependency build` na lock-based reconstruction,
- navrhnúť dependency version, repository/OCI, provenance, mirror a air-gapped supply-chain model,
- používať dependency `condition`, `tags`, `alias` a `import-values` bez nejasného lifecycle coupling,
- rozpoznať, kedy komponent patrí do samostatného release-u namiesto spoločného dependency graphu,
- analyzovať transitive dependencies, CRDs, hooks, RBAC a images ako súčasť dependency trust boundary,
- vysvetliť hook lifecycle body pre install, upgrade, rollback, delete a test,
- používať hook weight, delete policy, Job TTL, deadline a release timeout s jasným ordering/cleanup contractom,
- navrhnúť hook Job s least-privilege identity, resources, observability a idempotentnými side effects,
- vysvetliť, prečo hook resources nie sú rovnaký release inventory ako bežné manifests,
- navrhnúť backward-compatible database migration namiesto slepého spoliehania sa na rollback,
- rozlíšiť Helm CLI hook semantics od GitOps-controller-specific lifecycle behavior,
- diagnostikovať hook Pending/failure, stale resources, AlreadyExists, timeout a opakovanú migráciu.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Helm chart, template, values a release | Learning | L2 |
| Template functions a pipelines | Learning | L2 |
| Named templates | Learning | L2 |
| Chart dependencies | Learning | L2 |
| Hooks | Learning | L2 |