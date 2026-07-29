# Image signing, Policy as Code and Zero Trust lifecycle glossary entries

## Active policy generation

Exact immutable policy artifact a supporting-data revisions skutočne načítané konkrétnym evaluatorom alebo enforcement cohortom. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Continuous access verdict

Priebežný alebo event-driven výsledok, či existujúca session alebo communication path stále spĺňa identity, posture, entitlement, resource, policy a incident podmienky. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Delegated-actor continuity

Zachovanie väzby medzi human initiatorom, delegujúcou service a executing workloadom cez downstream authorization, operation result a audit. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Digest-bound quarantine

Policy state viazaný na exact artifact digest, ktorý blokuje promotion, deployment alebo ďalšie použitie bez potreby meniť historical artifact alebo signature. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Enforcement-path inventory

Versionovaný zoznam všetkých direct, proxy, controller, automation, recovery a legacy paths, ktorými možno vykonať action nad protected resource-om, vrátane príslušných PEPs. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Explicit resource decision

Authorization verdict viazaný na exact principal, action, resource, data scope, environment a current context namiesto implicitnej dôvery podľa network location alebo predchádzajúceho loginu. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Identity-posture generation

Matching human, device alebo workload identity state spolu s časovo označenou posture a assurance evidence použitou pri konkrétnom access decisione. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Image-signing subject

Exact OCI image index alebo platform manifest digest, product/environment scope, signer purpose, evidence requirements, registry path, policy revision a runtime/rollback cohort analyzovaného podpisu. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Input/data generation pair — policy

Matching request-input schema/generation a supporting-data revision, nad ktorými policy engine vytvoril decision. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Intent-to-enforcement lifecycle

Policy chain od human intentu cez exact decision subject, executable rules, immutable artifact, loaded generation, evaluation a enforcement po audit, revocation a bypass validation. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Multi-platform signing contract

Explicitné pravidlo určujúce, či release authority podpisuje OCI index, jednotlivé platform manifests alebo obe vrstvy a aké per-platform provenance/SBOM evidence sú povinné. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Parallel trust path

Alternatívna cesta k resource-u, ktorá používa slabšiu identity, policy, session alebo enforcement boundary než intended primary Zero Trust path. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## PEP coverage verdict

Dôkaz, že každá relevantná operation a resource path je zachytená zamýšľaným Policy Enforcement Pointom alebo equivalentným controlom bez hidden exemption či fail-open bypassu. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy acceptance verdict

Dôkaz, že intended policy, input/data contract, active revision, structured decision, enforcement, cache, exception, audit a alternate-path behavior vytvárajú správne allowed aj forbidden outcomes. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy decision subject

Exact operation, caller/delegation, resource, environment, policy/data revisions, evaluator, PEP, cache, decision a enforcement outcome analyzovaného Policy as Code verdictu. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy realization chain

Runtime väzba `published policy artifact → loaded evaluator generation → exact request input → decision → PEP action → observed resource outcome`. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy revocation closure

Dôkaz, že retired alebo malicious policy/data generation, cached decisions, exceptions a bypass paths už nedokážu vytvoriť accepted operation. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Posture-triggered revocation

Mechanizmus, ktorým zmena device alebo workload posture zneplatní alebo obmedzí existujúce sessions, credentials alebo ďalšie high-impact operations v bounded čase. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Quarantine-aware decision cache

Policy cache, ktorej key a invalidation zahŕňajú exact resource/artifact identity, policy/data revision a current quarantine alebo revocation generation. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Resource-access lifecycle

Zero Trust chain od protected business operation cez identities, posture, exact resource decision, bounded path a enforcement po continuous verification, revocation, recovery a bypass validation. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Second-decision validation

Opakovaný policy test po rollout-e, rollbacku, cache invalidation alebo revocation, ktorý dokazuje, že rovnaký allowed input zostáva správny a old/forbidden input sa nevrátil. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Second-operation validation — Zero Trust

Opakovanie protected business operation s fresh identities a generations spolu s negative testom starej session, posture, policy, artifactu a direct pathu. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Signature acceptance verdict

Dôkaz, že exact OCI subject, signature, trust/time evidence, signer authorization, attestations, promotion, active policy a resolved runtime digest vytvárajú intended release a odmietajú wrong-subject, unsigned-platform a quarantined paths. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Signature-to-runtime chain

Väzba od signed OCI subjectu cez registry promotion, policy decision a stored workload object po platform manifest digest skutočne načítaný runtime-om. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Signer authorization generation

Versionovaný contract spájajúci trusted root/issuer s exact signer identity, repository, workflow, ref, environment, purpose, subject a required evidence. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Subject-to-runtime trust lifecycle

Image-signing chain od release intentu a immutable OCI subjectu cez signing authority, trust evidence, semantic policy a promotion po runtime digest, quarantine a second-release validation. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Trust-recovery generation

Matching authoritative identity, posture, policy, trust-root, PEP configuration a resource/runtime state obnovené po security incidente. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Verification-bundle generation

Exact signature, certificate, chain, transparency/timestamp evidence, trusted-root generation a signed subject používané pri jednej historical alebo offline verification. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Wrong-subject negative test

Test dokazujúci, že validná signature alebo attestation na inom digest-e, platform manifeste, producte alebo environment-e nemôže autorizovať target artifact. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Zero Trust acceptance verdict

Dôkaz, že resource inventory, human/device/workload identities, explicit decisions, bounded sessions, complete PEP coverage, continuous revocation, degraded mode a recovery vytvárajú správny allowed, forbidden a bypass outcome. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust access subject

Exact protected operation, human/workload/device identity chain, credential and posture generations, action/resource/data scope, policy/PE/PA/PEP state, created session/path, audit a revocation descendants. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust revocation closure

Dôkaz, že disabled identity, stale posture, retired policy, compromised issuer, old session, direct path a quarantined resource už nedokážu vytvoriť accepted access. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).