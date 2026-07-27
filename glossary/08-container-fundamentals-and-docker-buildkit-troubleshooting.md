# BuildKit release and Docker incident glossary entries

Tento doplnok zachováva hlavný section glossary a pridáva pojmy zavedené v záverečných kapitolách [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md) a [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Authoritative remediation — Docker

Recovery vykonaná cez versionovaný source, configuration, policy, nový immutable artifact alebo explicitnú state generation namiesto ponechania ručnej mutation v bežiacom containeri. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Build publication acceptance

Verdict potvrdzujúci, že exact build subject bol exportovaný do požadovaného destinationu, registry read-back obsahuje complete artifact graph a platform inventory a všetky požadované evidence patria publikovanému subjectu. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Builder node subject

Identita jedného BuildKit node-u zahŕňajúca endpoint, worker, BuildKit version/configuration, driver, platform capabilities, kernel/runtime, snapshotter, cache access, credentials a trust classification. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Builder state lifecycle

Lifecycle content store-u, snapshots, cache records, active leases, temporary exports, logs, node capacity, retention, garbage collection a retirement konkrétnej builder instance. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Builder trust domain

Boundary určujúca, ktoré source classes môže builder vykonávať a ku ktorým secrets, SSH agents, caches, registry namespaces, attestations, signing identities a entitlements má access. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## BuildKit entitlement subject

Explicitná identita širšej build authority, napríklad host networking alebo insecure execution mode, viazaná na exact build subject, builder, requester, purpose, audit a expiration. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## BuildKit release subject

Rekonštruovateľná identita release build-u spájajúca source, frontend, contexts, base a dependency subjects, selected target, builder/nodes, platforms, caches, secrets references, exporters a expected evidence inventory. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Cache trust and freshness verdict

Samostatné rozhodnutie potvrdzujúce, že cached result pochádza z povoleného writer trust domainu, patrí správnemu platform/node subjectu a spĺňa požadovanú freshness alebo controlled-refresh policy. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Discriminating observation point — Docker

Observation, ktorého výsledok odlišuje aspoň dve konkurenčné causal hypotheses, napríklad cgroup OOM od host OOM alebo wrong socket bind od firewall failure. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker containment subject

Presný incident subject, scope, časové okno, protected data/side effects a dočasné actions, ktoré znižujú dopad bez zničenia evidence alebo vytvorenia nevratnej mutation. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker container generation

Konkrétna Engine container instance identifikovaná object ID, create time, image digest, create configuration, mounts, endpoints, cgroup, process a health history; odlišná od service name alebo Compose service definition. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker incident subject

Spoločná identita incidentu zahŕňajúca time window, Docker context/host/project, release a platform digest, container/config/data/endpoint generations, cgroup a flow state, request IDs a business audit. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker-to-Kubernetes diagnostic bridge

Prenos subject-bound diagnostickej metódy z Docker Engine modelu na Kubernetes control planes: artifact/process/cgroup/mount/flow identities zostávajú, no pribúdajú API desired state, controllers, scheduler, kubelet/CRI, Pod, Service endpoint a rollout generations. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Exporter contract — BuildKit

Contract určujúci, ktorý graph result sa musí exportovať, do akého destinationu a formátu, pod akou immutable identity, s akou retention a read-back verification. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Forbidden outcome — Docker incident

Stav, ktorý recovery nesmie povoliť, napríklad duplicate business side effect, staging access z production, stale writer, broad port exposure alebo strata authoritative data. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Graph execution subject — BuildKit

Identita vykonaného build graphu zahŕňajúca frontend translation, reachable nodes, selected target, platform branches, cache hit/miss outcomes, node scheduling, execution results a exporter roots. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Hypothesis evidence matrix — Docker

Mapovanie konkurenčných causal hypotheses na observation points a výsledky, ktoré jednotlivé hypotézy podporia alebo vyvrátia. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Incident closure verdict — Docker

Verdict potvrdzujúci, že authoritative recovery je nasadená, pôvodný business outcome funguje, forbidden outcomes sú absent, adjacent scope bol overený a skorší preventive control má ownera. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Management-plane/workload-plane split — Docker

Rozlíšenie medzi Docker client/Engine API a daemon object managementom na jednej strane a container taskom, processom, application health a business request pathom na druhej strane. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Native runtime gate

Požadovaný test exact platform manifestu na native target platforme, ktorý overuje startup, loader/dependencies, health, signal behavior a business outcome nad digestom určeným na publication. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Original outcome contract — Docker incident

Explicitný client-to-business journey a jeho latency, correctness, data, identity a exactly-once expectations, podľa ktorého sa posudzuje incident aj recovery. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Per-platform evidence inventory

Očakávaná množina manifest, SBOM, provenance, test, runtime a policy verdictov pre každú podporovanú OS/architecture/variant branch a vyšší image index subject. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Platform branch subject — BuildKit

Identita jednej target-platform vetvy build graphu zahŕňajúca selected node, native/emulated/cross-compile mode, base manifest, platform cache, output manifest a test evidence. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Subject-preserving reproduction — Docker

Kontrolovaný experiment, ktorý zachová relevantný image/platform digest, runtime configuration, kernel/runtime class, data clone a flow/load condition a mení iba jednu hypothesis variable. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Unknown publication outcome — BuildKit

Stav po timeoute alebo partial exporte, keď nie je známe, či registry prijala úplný index, manifests, blobs, tag a attestations; pred retry vyžaduje registry read-back a graph-generation reconciliation. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Volatile evidence inventory — Docker

Vopred definovaná množina krátkodobých Docker events, container state/logs, daemon/kernel records, cgroup counters, sockets, conntrack, endpoint a process evidence, ktoré treba zachovať pred restartom, recreate, delete alebo prune. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).
