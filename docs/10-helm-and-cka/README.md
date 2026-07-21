# Helm and CKA

Táto sekcia nadväzuje na Kubernetes a rozvíja Helm packaging, templating, dependency a release lifecycle a praktické cluster-administration zručnosti pre CKA. Cieľom nie je memorovať CLI príkazy, ale rozumieť render graphu, values a helper contracts, release state-u, side effects, upgrade hraniciam, diagnostike a bezpečnej práci pod časovým tlakom.

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
6. [Upgrade a rollback](upgrade-rollback.md)
7. [Helm testing a troubleshooting](helm-testing-troubleshooting.md)
8. [CKA timed labs](cka-timed-labs.md)
9. [CKA troubleshooting drills](cka-troubleshooting-drills.md)

Sekcia je obsahovo dokončená. Lineárna roadmapa ďalej pokračuje sekciou [Cloud and AWS](../11-cloud-and-aws/README.md).

## Cieľ zvládnutia

Po dokončení sekcie má byť možné:

- rozlíšiť chart, values, rendered manifest, live resources, release a release revision,
- vysvetliť chart version, `appVersion`, values precedence, schema a release storage,
- používať built-in objects, template functions, pipelines, serialization a whitespace control,
- rozlíšiť missing, empty a explicitné hodnoty a bezpečne používať `default`, `required`, `hasKey`, `tpl` a `lookup`,
- vytvárať named templates s explicitným scope-om, stabilnými helper contracts a collision-safe names,
- oddeliť stable selector labels od mutable metadata,
- navrhnúť chart dependencies cez `Chart.yaml`, `Chart.lock`, conditions, aliases, global values a versionovaný supply chain,
- rozpoznať transitive dependency, CRD, RBAC, hook a image riziká,
- navrhnúť Helm hooks s orderingom, timeoutom, cleanupom, idempotenciou, least privilege a auditovateľnými side effects,
- vysvetliť, prečo hook resources a external side effects nie sú bežný release inventory,
- pripraviť Helm upgrade z pinovaných artifacts, explicitných values, render diffu, server validation a health gate-u,
- rozlíšiť `reuse-values`, reset values a explicitný values contract,
- vykonať rollback na konkrétnu revision a vyhodnotiť databázovú, CRD, storage a external-state kompatibilitu,
- rozhodnúť medzi rollbackom a roll-forwardom podľa durable side effects,
- diagnostikovať pending upgrade/rollback, immutable fields, hooks, wait timeout a concurrent writers,
- používať Helm testovaciu pyramídu od lint/schema/render cez policy a server dry-run po ephemeral cluster a `helm test`,
- testovať values matrix, helper outputs, dependencies, CRDs, upgrade, rollback a uninstall lifecycle,
- odlíšiť Helm render/release failure od Kubernetes rollout, scheduling, storage alebo networking failure,
- zachovať release evidence cez history, status, values, manifest a hooks bez úniku Secretov,
- pripraviť domain-weighted CKA timed labs podľa aktuálneho oficiálneho curriculum,
- používať task intake protocol, context discipline, imperative skeleton, skip-and-return a verification pass,
- merať correctness, čas, context chyby, invalid attempts a hard validation,
- systematicky riešiť CKA troubleshooting scenáre cez failure-domain narrowing, evidence, minimálnu opravu a overenie,
- diagnostikovať Pods, controllers, scheduler, Nodes, API/admission, RBAC, Services, DNS, CNI, CSI, resources, probes, HPA, control plane a etcd pod časovým limitom,
- rozlišovať diagnosis time, repair time a verification time a vytvárať cielené opakovacie drilly.

## Praktické oblasti

- [CKA timed labs](../../labs/cka/README.md)
- [CKA troubleshooting drills](../../troubleshooting/cka/README.md)

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Helm chart, template, values a release | Learning | L2 |
| Template functions a pipelines | Learning | L2 |
| Named templates | Learning | L2 |
| Chart dependencies | Learning | L2 |
| Hooks | Learning | L2 |
| Upgrade a rollback | Learning | L2 |
| Helm testing a troubleshooting | Learning | L2 |
| CKA timed labs | Learning | L2 |
| CKA troubleshooting drills | Learning | L2 |
