# GitLab

Táto sekcia aplikuje všeobecné Git, testing a release-engineering princípy na konkrétny GitLab platform model. GitLab sa tu neposudzuje podľa polohy nastavení v UI. Každá kapitola sleduje, ako versionovaný source a platform intent prechádza cez namespace, effective membership, merge policy, resolved CI graph, runner trust, credentials, artifact registry a environment deployment až k auditovateľnému runtime a security outcome-u.

GitLab features, permissions, syntax a dostupnosť controls závisia od verzie, offeringu a tieru. Stabilný learning model preto oddeľuje product-independent authority a lifecycle princípy od konkrétneho GitLab feature surface-u. Každý production návrh musí overiť current documentation a effective configuration konkrétnej inštancie.

## Section-wide GitLab lifecycle

```text
business/project ownership intent
→ exact group/project/namespace subject
→ direct, inherited a shared effective access
→ protected source a merge-decision subject
→ resolved pipeline graph a trust context
→ runner/executor a short-lived workload identity
→ immutable artifact/report/registry subject
→ protected environment deployment
→ runtime/business acceptance
→ security finding, remediation a deployed-digest closure
→ access, artifact a environment retirement
```

Najdôležitejšie distinctions zostávajú explicitné:

- project membership nie je jediný effective access source;
- reviewer nie je automaticky eligible approver;
- protected branch nie je protected environment;
- source `.gitlab-ci.yml` nie je resolved pipeline graph;
- masked variable nie je automaticky bezpečný secret;
- cache nie je artifact ani report;
- registry tag nie je immutable image identity;
- environment record nie je runtime acceptance;
- successful analyzer job nie je complete processed security evidence;
- fixed default branch nie je dôkaz, že production digest bol nahradený.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Git and Automation Basics](../03-git-and-automation/README.md),
- [Testing and Software Quality](../04-testing-and-quality/README.md),
- [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md).

## Authoritative poradie — aktívne kapitoly

1. [Projects, groups a permissions](projects-groups-permissions.md)
2. [Merge requests a approvals](merge-requests-and-approvals.md)
3. [Protected branches a environments](protected-branches-and-environments.md)
4. [GitLab CI/CD syntax](gitlab-ci-cd-syntax.md)
5. [Praktický GitLab pipeline od source change po overený deployment](gitlab-pipeline-practical-walkthrough.md)
6. [Runners a executors](runners-and-executors.md)
7. [Variables a secrets](variables-and-secrets.md)
8. [Artifacts a cache](artifacts-and-cache.md)
9. [Container a package registry](container-and-package-registry.md)
10. [Environments, deployments a releases](environments-deployments-releases.md)
11. [Security scanning](security-scanning.md)
12. [GitLab troubleshooting](gitlab-troubleshooting.md)

Po tejto sekcii nasleduje Infrastructure as Code and Configuration Management. GitLab merge, pipeline, registry, credential a environment subjects sa tam použijú na plánovanie a bezpečné aplikovanie Terraform a Ansible state transitions.

## Hlavný praktický walkthrough

Kapitola [Praktický GitLab pipeline od source change po overený deployment](gitlab-pipeline-practical-walkthrough.md) vytvára jeden celý executable release flow namiesto izolovaných YAML fragmentov. Začína repository layoutom a malou HTTP aplikáciou, pokračuje Dockerfile-om a Kubernetes manifestom a následne prechádza kompletný `.gitlab-ci.yml`.

Walkthrough vysvetľuje `workflow: rules`, job `rules`, `needs` DAG, JUnit a dotenv reports, trusted Docker build runner, build-once image digest, registry read-back, scanner nad exact digestom, server-side dry-run, `resource_group`, protected staging/production environments, rollout status, live Deployment image a Service/EndpointSlice smoke test. Pri každom kroku oddeľuje source YAML, resolved graph, runner execution, artifact/report state, GitLab deployment record, Kubernetes live state a aplikačný outcome.

Praktický acceptance contract pre túto sekciu preto vyžaduje, aby čitateľ vedel nielen vysvetliť GitLab concepts, ale aj prejsť konkrétny pipeline riadok po riadku, určiť trust boundary každého jobu, identifikovať artifact hand-off a dokázať, že staging aj production používajú rovnaký immutable image digest. Missing scanner job, mutable tag, nesprávny cluster context a rollout-ready-but-business-broken paths musia byť diagnostikovateľné z konkrétnych outputs.

## GitLab troubleshooting

[GitLab troubleshooting](gitlab-troubleshooting.md) používa jeden preserve-first model naprieč pipeline source, resolved YAML, runner eligibility, variables a workload identity, artifacts/cache, registry digest, environment deployment, runtime generation a security evidence. Kapitola ukazuje, prečo `green pipeline`, `successful deployment` alebo `closed finding` nie sú samostatne complete verdicty.

Connected incident `green pipeline, old production image` sa diagnostikuje cez pipeline/job/deployment IDs, expected job inventory, producer artifact checksum, OCI digest, target identity, live workload a business operation. Recovery overuje aj forbidden alternate path a druhú operáciu.

## Connected learning scenarios

### `GL-PAY-72` — inherited access, stale approval a protected-source bypass

Prvý blok spája projects/groups/permissions, merge requests a protected branches/environments. Atlas Payments presunie project medzi groups, no inherited Owner membership a shared group access zostanú effective. Merge request approval sa nereštartuje po force-pushi a direct push role má širšie oprávnenie než merge policy. Production environment používa samostatný deploy identity path, ktorý branch protection nevidí.

```text
namespace ownership
→ effective membership graph
→ source change a merge subject
→ approval freshness
→ protected ref decision
→ environment deployment authority
→ audit a revocation
```

Acceptance musí preukázať exact namespace generation, effective access vrátane inheritance/share/tokens, immutable merge candidate a independent source/runtime enforcement.

### `GL-PAY-73` — resolved CI graph, runner trust a secret capability drift

Druhý blok spája GitLab CI/CD syntax, runners/executors a variables/secrets. Root `.gitlab-ci.yml` používa mutable include a `rules` vytvoria duplicate pipelines. Fork-controlled job sa dostane na protected persistent runner, restore-ne shared cache a cez broad ID-token trust získa environment credential. Masked variable sa objaví v transformed outpute.

```text
pipeline source a event
→ includes/rules/inheritance
→ resolved DAG
→ runner/executor trust class
→ variable/ID-token resolution
→ short-lived capability
→ job side effect a audit
```

Block musí oddeľovať source od resolved graphu, runner od executora, secret storage od effective capability a configured variable od loaded job environmentu.

### `GL-PAY-74` — artifact/registry identity, false deployment a incomplete security closure

Záverečný blok spája artifacts/cache, registries, environments/deployments/releases a security scanning. Pipeline publikuje mutable multi-platform tag, report artifact chýba po analyzer infrastructure failure a release record ukazuje deployment success po GitOps commit-e bez runtime correlation. Secret finding je dismissed bez provider revocation a default branch fix nevymení production digest.

```text
job output
→ artifact/report/cache authority
→ immutable package/image graph
→ deployment/release record
→ runtime digest a business outcome
→ security finding/vulnerability
→ remediation a deployed-artifact closure
```

Acceptance musí preukázať complete expected scanner inventory, exact artifact subject, deployment-to-runtime correlation a revocation/redeployment, nie iba zelené jobs alebo closed findings.

## Cieľ zvládnutia

Po dokončení sekcie má byť možné:

- navrhnúť GitLab group/project hierarchy podľa ownershipu a security boundary;
- vypočítať direct, inherited, shared, token a custom-role effective access;
- oddeliť human, service account, access token a CI workload identity lifecycle;
- viazať merge verdict na exact diff, approvals, discussions, pipeline a target generation;
- navrhnúť protected branches/tags a protected environments ako samostatné enforcement boundaries;
- rozlíšiť source YAML od includes/rules/extends rozbaleného runtime DAG-u;
- zvoliť runner scope, tags, protected status, executor a ephemeral isolation podľa trust classu;
- používať ID tokens a external secret providers s bounded claims a short-lived credentials;
- odlíšiť artifact, report, cache, package, image index a release manifest;
- presadzovať write-once versions, digest promotion, signatures, SBOM a provenance;
- korelovať GitLab environment/deployment/release s controller, runtime a business state-om;
- vrstviť security analyzers podľa attack surface-u a overovať coverage/completeness;
- uzavrieť finding až po revocation alebo nasadení fixed artifactu a runtime read-backu;
- diagnostikovať alternate source, pipeline, credential, registry a deployment paths;
- vykonať evidence-preserving containment, authoritative recovery a forbidden-path validation.

## Revalidation completion gate

Sekcia bude `Ready for user review` iba vtedy, keď:

1. všetkých 12 authoritative kapitol vrátane end-to-end pipeline walkthroughu používa connected Keycloak-style prose, dominantný lifecycle a primeraný executable surface;
2. každá kapitola definuje exact namespace, merge, pipeline, runner, credential, artifact, deployment alebo finding subject;
3. každá kapitola obsahuje reálne GitLab API/CLI, YAML, shell, policy alebo runtime read-back príklady;
4. každý významný output vysvetľuje, čo preukazuje a čo nepreukazuje;
5. source/configured/resolved/loaded/effective/runtime/business states sa nezlievajú;
6. complex failures obsahujú competing hypotheses a discriminating evidence;
7. recovery overuje allowed, forbidden, alternate-path a second-operation outcome;
8. strict learning-depth audit je 12/12 bez critical/high/medium findings a practical gate nemá failures;
9. README, navigation, glossary a centrálny ledger sú synchronizované;
10. čistý PR head bez dočasných artifacts prejde štandardným documentation workflowom.

## Aktuálny stav revalidácie

Step 2 chapter-by-chapter explanation-depth pass zachoval všetkých dvanásť existujúcich lifecycle a incident modelov a doplnil chýbajúce prose transitions. Každý code-first lifecycle/exact-subject/troubleshooting blok teraz najprv vysvetľuje, čo je subject, ako sa mení state a čo nasledujúci diagram alebo YAML dokazuje. Bare inventories pre effective access, secret exposure, artifact/cache authority, registry retention, dry-run hranicu a preserve-first troubleshooting boli nahradené mechanistickým výkladom; jednovetové anti-patterny teraz uvádzajú failure mechanism, dôsledok a acceptance boundary.

| Blok | Kapitoly | Stav |
|---|---:|---|
| `GL-PAY-72` — access, merge a protected boundaries | 3/3 | Complete |
| `GL-PAY-73` — CI graph, runner a secret capabilities | 3/3 | Complete |
| `GL-PAY-74` — artifacts, registry, deployments a security closure | 4/4 | Complete |
| End-to-end GitLab pipeline walkthrough | 1/1 | Complete |
| GitLab troubleshooting | 1/1 | Complete |

Celkový authoritative stav: **12/12 · Ready for user review**. Pôvodný prose-first pass zostáva zachovaný a nový walkthrough dopĺňa chýbajúcu súvislú code-execution vrstvu. Tento stav neznamená automatické používateľské schválenie, Accepted, Verified ani Stable.
