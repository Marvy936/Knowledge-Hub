# Environments, deployments a releases

GitLab rozlišuje environment, deployment a release ako prepojené, ale odlišné objekty. Environment reprezentuje runtime target, deployment zaznamenáva nasadenie konkrétnej zmeny do targetu a release zhromažďuje distribuovanú verziu, notes, links a evidence.

## 1. Environment

Environment je pomenovaný deployment target, napríklad:

- `development`,
- `staging`,
- `production`,
- `review/feature-login`.

Nie je to iba string v UI. Má reprezentovať konzistentný runtime context s ownershipom, permissions, variables, URL, lifecycle a deployment history.

## 2. Static a dynamic environments

### Static environment

Opakovane používaný target:

```text
staging
production
```

### Dynamic environment

Dočasný target vytvorený pre branch alebo merge request:

```text
review/$CI_COMMIT_REF_SLUG
```

Dynamic environment potrebuje stop job, TTL alebo iný garantovaný cleanup.

## 3. Environment v jobe

```yaml
deploy_staging:
  stage: deploy
  script:
    - ./deploy.sh staging
  environment:
    name: staging
    url: https://staging.example.com
```

Úspešný deployment job vytvorí deployment record pre environment.

## 4. Environment URL

URL zlepšuje navigáciu z pipeline a merge requestu do nasadenej aplikácie.

URL nie je health check. Environment môže mať URL a pritom byť nefunkčný alebo smerovať na nesprávnu version.

## 5. Deployment

Deployment je udalosť, ktorá spája:

- environment,
- commit alebo ref,
- pipeline/job,
- čas,
- status,
- identity,
- deployment metadata.

GitLab udržiava deployment history, aby bolo možné zistiť, čo sa kedy nasadilo.

Pre high-assurance workflow doplň artifact digest a configuration revision, pretože commit sám nemusí identifikovať nasadené bytes a config.

## 6. Deployment job

Deployment job má byť idempotentný alebo bezpečne resumable. Definuj:

- immutable artifact input,
- target environment,
- configuration revision,
- rollout strategy,
- timeout,
- concurrency lock,
- validation,
- failure a recovery semantics.

## 7. Manual deployment

```yaml
deploy_prod:
  stage: deploy
  script: ./deploy.sh production
  environment:
    name: production
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
```

Manual job je mechanizmus spustenia, nie automaticky kvalifikovaný approval. Kto smie job spustiť a akú evidence vidí, musí byť vynútené policy.

## 8. Protected environment

Protected environment obmedzuje identities alebo groups oprávnené deployovať a podľa dostupnej GitLab funkcionality môže používať deployment approvals.

Chráň súčasne:

- deployment job inclusion,
- environment permission,
- protected variables,
- runner,
- artifact identity,
- target cloud/Kubernetes identity.

## 9. Environment-scoped variables

Variables možno obmedziť na konkrétny environment alebo pattern.

Používaj presné scopes. Wildcard ako `*` pre production secret ruší environment boundary.

## 10. Deployment concurrency

Dva súbežné deploymenty do rovnakého environmentu môžu vytvoriť race:

```yaml
deploy_prod:
  resource_group: production
```

Serialization musí mať jasnú queue policy:

- spustiť všetky postupne,
- zrušiť obsolete deployment,
- preferovať najnovší pipeline,
- nechať mutation dokončiť a potom prehodnotiť stav.

## 11. Outdated deployments

Novší pipeline môže deploynúť skôr než starší pipeline. Bez ochrany potom starší job prepíše environment starou verziou.

Použi:

- resource serialization,
- prevent-outdated-deployment controls,
- immutable desired version,
- deployment controller s compare-and-set semantics.

## 12. Review apps

Review app je dynamic environment pre konkrétnu branch alebo merge request.

Typický model:

```yaml
deploy_review:
  script: ./deploy-review.sh
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    url: https://$CI_ENVIRONMENT_SLUG.review.example.com
    on_stop: stop_review

stop_review:
  script: ./destroy-review.sh
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    action: stop
  when: manual
```

Cleanup nesmie závisieť iba od manuálneho kliknutia. Pridaj TTL alebo periodický garbage collector.

## 13. Review app security

Review apps môžu sprístupniť:

- internú funkcionalitu,
- test data,
- environment variables,
- preview URL,
- cloud resources.

Použi authentication, izolované data, least privilege, unique namespace a network policy. Review app z untrusted forku nesmie používať production secrets.

## 14. Stop a delete environment

Rozlišuj:

- stop runtime workloadu,
- delete GitLab environment recordu,
- delete cloud/Kubernetes resources,
- delete DNS a storage,
- revoke identity.

UI stav `stopped` nemusí dokazovať, že external resources boli odstránené.

## 15. Deployment tiers

Environment môže mať logical deployment tier, napríklad development, testing, staging alebo production.

Tier pomáha reportingu a GitLab features, ale nenahrádza security policy ani názvovú konvenciu.

## 16. Deployment tracking

Deployment history umožňuje:

- zobraziť aktuálnu a predchádzajúce versions,
- korelovať incidents so zmenami,
- sledovať included merge requests,
- vytvoriť audit trail,
- merať deployment metriky.

Deployment record musí byť pravdivý. Job, ktorý iba vypíše „deployed“ bez overenia targetu, vytvára falošnú evidence.

## 17. Environment health

Po deployment-e overuj:

- rollout completion,
- readiness,
- synthetic critical path,
- version/digest telemetry,
- error rate,
- latency,
- saturation,
- business KPI,
- dependency health.

Pipeline success nie je automaticky production success.

## 18. Rollback

GitLab môže ponúkať redeploy/rollback workflow podľa deployment modelu. Bezpečnosť závisí od:

- artifact availability,
- configuration compatibility,
- database/schema state,
- external side effects,
- runtime controller behavior.

Rollback button nie je dôkaz reverzibility.

## 19. Releases

GitLab Release je platformový objekt pre pomenovanú distribuovanú verziu. Môže obsahovať:

- tag,
- release name,
- description/release notes,
- released-at timestamp,
- asset links,
- milestones,
- evidence podľa dostupnej funkcionality.

Release objekt nemá vytvárať nové bytes. Má referencovať už vytvorený immutable artifact.

## 20. Tag a release

Git tag označuje source revision alebo release point. Release pridáva produktové a distribučno-prevádzkové metadata.

Tag bez artifact digestu nemusí jednoznačne identifikovať package alebo image, najmä ak build nie je reprodukovateľný.

## 21. Release job

```yaml
release_job:
  stage: release
  script:
    - echo "create release metadata"
  release:
    tag_name: "$CI_COMMIT_TAG"
    name: "Release $CI_COMMIT_TAG"
    description: "Release notes for $CI_COMMIT_TAG"
  rules:
    - if: '$CI_COMMIT_TAG'
```

Release job má validovať:

- tag policy,
- immutable artifacts,
- checksums/digests,
- test a scan evidence,
- version uniqueness,
- release notes.

## 22. Release assets

Asset link môže smerovať na:

- package registry,
- generic package,
- container image digest,
- binary download,
- documentation,
- SBOM,
- checksum/signature.

Nespoliehaj sa na expirovateľný job artifact ako jediný dlhodobý release asset.

## 23. Generic packages

Generic Package Registry je vhodný pre release binaries alebo bundles bez špecifického package-manager protokolu.

Použi immutable version path a checksum. Release link smeruje na package, nie na mutable „latest“ URL.

## 24. Release evidence

Release evidence má spájať:

- source tag/commit,
- artifact digests,
- SBOM,
- provenance/signatures,
- CI pipeline,
- approvals,
- scan results,
- release notes,
- deployment status.

Presná podpora GitLab features závisí od verzie a tieru; návrhový princíp zostáva rovnaký.

## 25. Freeze periods

Deployment freeze môže blokovať alebo obmedziť production deploymenty počas definovaného času.

Freeze nesmie:

- znemožniť emergency recovery,
- nahradiť observability,
- viesť k obrovskému batchu po skončení,
- zostať bez ownera a exception policy.

## 26. Environment naming

Použi konzistentné názvy a prefixy:

```text
production
staging
review/<slug>
region/eu-west-1/production
```

Názov ovplyvňuje variable scopes, UI grouping a automation. Rename environmentu môže zmeniť security a reporting behavior.

## 27. GitOps interaction

Pri GitOps modeli CI pipeline nemusí priamo mutovať cluster. Môže:

1. publishnúť artifact,
2. aktualizovať environment configuration repository,
3. GitOps controller reconciliuje desired state,
4. deployment status sa spätne koreluje.

Deployment record musí odlíšiť configuration request od skutočného runtime rollout-u.

## 28. Troubleshooting

### Deployment job je zelený, environment starý

Over artifact digest, target context, controller reconciliation, deployment record a runtime telemetry.

### Starší pipeline prepísal novší deployment

Chýba serialization alebo outdated-deployment protection.

### Review app zostala po merge

Stop job sa nespustil alebo external cleanup zlyhal. Použi TTL a periodic reconciler.

### Production variable nie je dostupná

Over environment name/scope, protected ref, deployment job rules a variable precedence.

### Release link prestal fungovať

Smeroval na expirovaný job artifact alebo mutable external URL. Presuň asset do dlhodobej registry.

### Rollback zlyhal

Artifact, config alebo schema už nie sú kompatibilné. Použi roll-forward/restore podľa recovery plánu.

## 29. Kontrolné otázky

1. Aký je rozdiel medzi environmentom a deploymentom?
2. Čo odlišuje static a dynamic environment?
3. Ako zabrániť outdated deploymentu?
4. Čo musí riešiť review-app cleanup?
5. Prečo protected environment nestačí bez bezpečného runnera?
6. Čo má dokazovať deployment record?
7. Aký je rozdiel medzi Git tagom a GitLab Release?
8. Kde majú byť dlhodobé release assets?
9. Ako deployment freeze ovplyvňuje emergency change?
10. Ako GitOps mení význam deployment jobu?

## Glossary impact

Relevantné pojmy: GitLab environment, static environment, dynamic environment, deployment record, outdated deployment, review app, stop job, deployment tier, GitLab Release, release asset a deployment freeze.

## Oficiálna dokumentácia

- [Environments](https://docs.gitlab.com/ci/environments/)
- [Deployments](https://docs.gitlab.com/ci/environments/deployments/)
- [Releases](https://docs.gitlab.com/user/project/releases/)
- [Review apps](https://docs.gitlab.com/ci/review_apps/)
