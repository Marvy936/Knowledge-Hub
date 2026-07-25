# Environments, deployments a releases

## Metadata

- Status: Learning
- Level: L2
- Domain: GitLab

## 1. Definícia

GitLab rozlišuje tri súvisiace, ale odlišné objekty:

- **Environment —** pomenovaná runtime boundary, do ktorej sa nasadzuje a ku ktorej sa viažu permissions, variables, URL, tier a deployment history.
- **Deployment —** zaznamenaný pokus alebo výsledok nasadenia konkrétneho subjectu do environmentu.
- **Release —** distribučno-produktový záznam pomenovanej verzie, ktorý prepája tag, immutable artifacts, release notes, evidence a support lifecycle.

Tieto objekty nemajú byť zamenené:

```text
source commit alebo tag
→ immutable artifact a config revision
→ deployment do environmentu
→ runtime validation
→ release acceptance a distribúcia
```

GitLab môže uchovať metadata o každom kroku, ale samotný záznam v GitLabe nie je dôkaz, že runtime stav skutočne zodpovedá deklarácii. Dôveryhodný model prepája GitLab record s artifact digestom, konfiguráciou, cieľovou identitou a produkčnou telemetry.

## 2. Mental model: desired, recorded a effective state

Pri environmentoch rozlišuj tri stavy:

- **Desired state —** čo pipeline alebo GitOps konfigurácia žiada nasadiť.
- **Recorded state —** čo GitLab deployment objekt eviduje ako nasadené alebo dokončené.
- **Effective state —** čo reálne beží v runtime vrátane configu, traffic routingu a shared state.

```text
GitLab job success
≠ automaticky správny deployment record
≠ automaticky správny runtime stav
```

Rozdiel môže vzniknúť pri asynchrónnom controlleri, partial failure, manuálnom zásahu, drift-e, stale pipeline alebo nesprávnom targete. Post-deployment verification musí preto overiť effective state nezávislým observation pointom.

## 3. Environment identity

Environment nie je iba voľný string. Jeho identita má obsahovať alebo jednoznačne odvodiť:

- project alebo release unit,
- environment name,
- deployment tier,
- account/subscription/cluster,
- region alebo zone podľa potreby,
- namespace alebo runtime target,
- configuration boundary,
- data boundary,
- ownera,
- protection a approval policy.

Príklady:

```text
production
staging
review/1234
region/eu-central-1/production
customer/acme/pilot
```

Názov ovplyvňuje variable scopes, protected-environment matching, UI grouping, metrics a cleanup automation. Neštandardné alebo dynamicky manipulovateľné názvy môžu vytvoriť nový neprotected target s podobným názvom a obísť zamýšľanú policy.

## 4. Static a dynamic environments

### Static environment

Dlhodobo používaný target, napríklad staging alebo production. Má stabilný ownership, runtime dependencies, access policy a deployment history.

### Dynamic environment

Dočasný target vytvorený pre branch, merge request, tenant alebo testovací scenár. Typickým príkladom je review app.

Dynamic environment potrebuje už pri vytvorení:

- jednoznačnú identity,
- izolované credentials a data,
- resource quota,
- TTL alebo auto-stop,
- idempotentný teardown,
- ownera,
- evidenciu external resources,
- pravidelný reconciler pre zlyhaný cleanup.

GitLab stav `stopped` neznamená, že cloud resources, DNS, volumes alebo identity boli skutočne odstránené.

## 5. Environment tier

Deployment tier klasifikuje význam targetu, napríklad development, testing, staging alebo production. Tier pomáha reportingu a governance, ale nie je permission boundary sám osebe.

Environment s názvom `prod-eu` a nesprávnym development tierom môže skresliť deployment metrics. Naopak environment označený ako production nie je bezpečný bez protected-environment policy a scoped identity.

## 6. Deployment subject

Deployment musí jednoznačne identifikovať, čo sa nasadzuje. Samotný commit SHA často nestačí.

Deployment subject môže obsahovať:

```text
source commit alebo tag
+ artifact digest/package version
+ configuration revision
+ infrastructure revision
+ schema/migration phase
+ feature-flag policy version
+ rollout strategy
```

Pri multi-component release použi release manifest, ktorý mapuje každú komponentu na immutable digest a relevantnú config revision.

## 7. Deployment state machine

Deployment modeluj ako state machine:

```text
created
→ waiting for prerequisites
→ approved alebo eligible
→ running
→ runtime change requested
→ verifying
→ succeeded / failed / canceled / blocked / inconclusive
→ recovery alebo superseded
```

`Job succeeded` môže znamenať iba to, že API prijalo deployment request. Pri asynchrónnom GitOps alebo cloud controlleri musí byť úspech viazaný na reconciliation a runtime verification.

Rozlišuj:

- **Failed —** deployment mechanizmus zistil konkrétne zlyhanie.
- **Blocked —** chýba approval, permission, lock alebo prerequisite.
- **Canceled —** execution bolo zámerne ukončené.
- **Inconclusive —** runtime change prebehol, ale telemetry alebo validation nestačí na rozhodnutie.
- **Superseded —** novší desired deployment nahradil starší ešte pred jeho dokončením.

## 8. Deployment job contract

Deployment job má explicitne definovať:

- immutable artifact input,
- target environment identity,
- config a infra revision,
- required evidence a approvals,
- workload identity a permissions,
- rollout strategy,
- serialization alebo lease,
- timeouty podľa fázy,
- cancellation semantics,
- post-deploy verification,
- rollback/roll-forward eligibility,
- failure artifacts a audit metadata.

Job má byť idempotentný alebo bezpečne resumable. Opakované spustenie po timeout-e nesmie vytvoriť nekontrolované duplicity alebo paralelné migrations.

## 9. Protected environment

Protected environment je runtime authorization boundary. Obmedzuje, kto alebo ktorá identity môže spustiť deployment do konkrétneho targetu.

Bezpečný deployment vyžaduje súčasne:

- dôveryhodný ref alebo release subject,
- chránený deployment job a pipeline config,
- allowed-to-deploy policy,
- scoped protected/environment variables,
- bezpečný runner alebo controller,
- short-lived runtime identity,
- immutable artifact,
- auditovateľné approval a exception pravidlá.

Protected environment nechráni pred malicious kódom už mergeovaným do trusted refu ani pred príliš privilegovaným runnerom.

## 10. Manual job verzus approval

`when: manual` iba čaká na používateľský trigger. Nie je to automaticky kvalifikovaný approval.

Approval rozhodnutie potrebuje:

- presný artifact a environment subject,
- evidence summary,
- eligible approvera,
- separation of duties podľa rizika,
- freshness a expiráciu,
- audit trail,
- možnosť revokácie pred execution,
- break-glass pravidlá.

Používateľ, ktorý môže kliknúť manual job, nemusí mať právo schváliť business alebo compliance risk.

## 11. Environment-scoped variables a identity

Environment scope znižuje exposure credentials, ale výsledná bezpečnosť závisí od názvu environmentu a deployment jobu.

Kontroluj:

- presný scope a wildcard precedence,
- kto môže zmeniť `environment:name`,
- protected-ref kontext,
- variable precedence,
- downstream forwarding,
- runner trust,
- cleanup file secrets,
- cloud-side authorization claims.

Preferuj OIDC alebo inú workload federation:

```text
GitLab deployment job
→ signed ID token
→ runtime/cloud provider
→ short-lived environment-scoped credential
```

## 12. Deployment concurrency

Dva jobs mutujúce rovnaký environment vytvárajú race. `resource_group` alebo iný lock serializuje execution, ale potrebuje definovanú queue policy.

Možnosti:

- vykonať všetky deployments v poradí,
- supersedovať staršie pending deployments,
- nechať running mutation dokončiť a potom prehodnotiť desired state,
- použiť controller s compare-and-set nad aktuálnou generation.

Lock má obsahovať ownera, lease/timeout a recovery pri orphaned stave. Externé manuálne deploymenty mimo GitLabu môžu lock obísť, preto je vhodný aj runtime-side coordination mechanizmus.

## 13. Outdated deployments

Outdated deployment nastane, keď starší pipeline prepíše novší environment state.

Príklad:

```text
pipeline A pre commit 100 začne skôr, ale čaká
pipeline B pre commit 101 sa nasadí
pipeline A sa neskôr dokončí
→ production sa vráti na commit 100
```

Ochrany:

- serialized resource group,
- prevent-outdated-deployment policy,
- desired generation alebo sequence number,
- compare-and-set pred mutation,
- revalidation subjectu po čakaní,
- zákaz mutable artifact tags,
- runtime telemetry s digestom.

## 14. Deployment freshness

Pred execution znovu over:

- artifact stále spĺňa policy,
- approval sa vzťahuje na rovnaký digest a config,
- environment nebol zmenený novším deploymentom,
- release nebol revoked,
- security evidence neexpirovala,
- freeze alebo incident policy sa nezmenila,
- target credentials a dependencies sú platné.

Dlhé čakanie na manual job môže z pôvodne bezpečného deploymentu vytvoriť stale rozhodnutie.

## 15. Post-deployment verification

Deployment nie je úspešný iba preto, že command skončil s exit code 0. Overuj minimálne:

- runtime digest a config revision,
- rollout completion,
- readiness a healthy capacity,
- routing/exposure state,
- synthetic critical journey,
- error rate a latency,
- saturation a dependency health,
- queue/backlog stav,
- business invariants,
- databázovú alebo eventovú kompatibilitu.

Telemetry musí byť filtrovatelná podľa deployment ID, artifact digestu, environmentu, regionu a rollout cohorty.

## 16. Deployment record quality

Dôveryhodný record prepája:

```text
project a pipeline
→ job a actor/workload identity
→ source SHA/tag
→ artifact digest
→ config/infra revision
→ target environment
→ rollout a exposure state
→ verification result
→ recovery outcome
```

Job, ktorý iba vypíše `deployed` bez kontroly targetu, vytvára falošnú evidence. Pri GitOps workflowe zaznamenaj zvlášť configuration change request a skutočný reconciled runtime deployment.

## 17. GitOps interaction

Pri GitOps modeli CI typicky:

1. vytvorí a publikuje immutable artifact,
2. aktualizuje desired-state repository alebo release manifest,
3. GitOps controller zmenu reconciliuje,
4. runtime health a effective state sa vrátia do evidence systému.

Pipeline commit do config repository nie je dokončený deployment. Potrebuje koreláciu medzi:

- source pipeline,
- config commit,
- controller reconciliation,
- runtime digest,
- environment deployment recordom.

## 18. Review apps

Review app je dynamic environment pre konkrétnu zmenu. Jeho hodnota je vysoká iba vtedy, keď reprezentuje relevantnú application boundary bez neprimeraného security rizika.

Review app contract obsahuje:

- MR/pipeline identity,
- immutable artifact digest,
- izolovaný namespace a URL,
- test identity a synthetic data,
- environment-scoped variables,
- network policy,
- resource quota,
- stop job,
- TTL,
- cleanup ownera,
- cleanup evidence.

Untrusted fork nesmie dostať production secrets, privileged runner ani network access k citlivým interným službám.

## 19. Review-app cleanup

Cleanup je samostatný lifecycle:

```text
stop application
→ odstráň workloads/services
→ odstráň DNS a ingress
→ odstráň volumes/data podľa policy
→ revoke credentials
→ odstráň cloud resources
→ over nulový inventory
→ označ environment stopped/deleted
```

Použi viac ochranných vrstiev:

- `on_stop` job,
- auto-stop/TTL,
- cloud labels s ownerom a expiry,
- periodický garbage collector,
- budget/quota alert,
- reconciler orphaned resources.

## 20. Environment drift

Drift môže vzniknúť manuálnou zmenou, controllerom, secret rotation, cloud defaultom alebo partial deploymentom.

Rozlišuj:

- desired-state drift,
- configuration drift,
- artifact drift,
- permission drift,
- data/schema drift,
- routing/exposure drift.

Deployment verification a pravidelná reconciliation majú porovnávať GitLab record s runtime inventárom. Manuálny zásah musí vytvoriť auditný a následný desired-state update.

## 21. Rollback a roll-forward

GitLab redeploy alebo rollback action rieši iba časť recovery. Pred rollbackom over:

- previous artifact digest a jeho dostupnosť,
- compatibility s aktuálnou schema a dátami,
- config a secrets compatibility,
- events už publikované novou verziou,
- external side effects,
- active clients,
- runtime target a routing state.

Možnosti containmentu:

1. pause promotion,
2. znížiť exposure,
3. vypnúť feature flag,
4. route traffic na stable target,
5. rollback artifact/configu,
6. roll-forward,
7. compensating action alebo restore.

Deployment record musí zachytiť aj recovery subject a výsledok.

## 22. Deployment freeze

Freeze period mení eligibility plánovaných deployments. Nemá nahrádzať protected environment ani recovery capability.

Freeze policy potrebuje:

- scope a timezone,
- ownera,
- ktoré jobs sú blokované,
- emergency výnimku,
- approvera a audit,
- expiráciu výnimky,
- post-freeze queue policy.

Po skončení freeze nevypúšťaj automaticky veľký batch stale deployments bez opätovnej validácie.

## 23. GitLab Release

GitLab Release je platformový záznam distribuovanej verzie. Nemá byť procesom, ktorý vyrába nové bytes. Má referencovať už existujúce immutable artifacts.

Release môže obsahovať:

- protected tag,
- release name a version,
- released-at timestamp,
- release notes,
- milestones alebo issues,
- asset links,
- checksums, SBOM a signatures,
- release evidence,
- deployment/support informácie.

## 24. Release subject a manifest

Pri jednoduchej aplikácii môže release subject tvoriť jeden package alebo image digest. Pri viacerých komponentoch vytvor release manifest:

```text
release_version
component A → image digest
component B → package version/checksum
infra → revision
config → revision
schema → compatibility state
```

Manifest musí byť immutable alebo versionovaný. Release tag bez väzby na výsledné artifacts neidentifikuje, čo používatelia alebo produkcia skutočne dostali.

## 25. Release eligibility

Pred vytvorením alebo akceptovaním release over:

- tag a version policy,
- artifact immutability,
- provenance a signatures,
- SBOM completeness,
- required test a scan evidence,
- compatibility matrix,
- known issues a exceptions,
- release notes,
- support a rollback window,
- approval freshness.

Release job musí zlyhať pri neúplnej evidence. Chýbajúci scanner report alebo package nemá byť interpretovaný ako čistý výsledok.

## 26. Release assets

Dlhodobé assets patria do package/container/generic registry alebo iného trvalého artifact store. Job artifact s krátkym `expire_in` nie je vhodný ako jediný release download.

Asset link má smerovať na immutable subject:

- package version a checksum,
- image digest,
- generic package path,
- SBOM,
- signature alebo attestation,
- dokumentáciu viazanú na release verziu.

Mutable `latest` link môže slúžiť na discovery, ale release record musí uchovať immutable identity.

## 27. Release lifecycle

Release modeluj ako stavový lifecycle:

```text
candidate
→ approved/published
→ supported
→ deprecated
→ end-of-life
→ archived alebo revoked
```

### Deprecation

Informuje consumers o plánovanom ukončení podpory a náhrade.

### Yanking

Zabráni novým consumers automaticky vybrať chybnú verziu, ale môže zachovať bytes pre existujúce deployments a audit.

### Revocation

Označí release alebo artifact ako nedôveryhodný, napríklad pri kompromitácii signing key alebo kritickom supply-chain incidente.

### Deletion

Fyzicky odstráni metadata alebo bytes. Je posledným krokom a musí rešpektovať consumer inventory, legal hold, incident analysis a rollback potreby.

GitLab Release nemusí priamo implementovať všetky tieto stavy; organizácia ich musí reprezentovať v policy a registry lifecycle.

## 28. Release evidence freshness

Release bol bezpečný v čase publikovania, ale risk sa môže zmeniť. Nové vulnerabilities alebo compromised dependency môžu vyžadovať:

- continuous rescanning,
- identifikáciu dotknutých release digests,
- aktualizáciu support statusu,
- yanking alebo revocation,
- rebuild s patched dependencies,
- informovanie consumers,
- nový deployment.

Pôvodný zelený pipeline zostáva historickou evidence, nie aktuálnym security verdictom.

## 29. Release a deployment nie sú totožné

Jeden release môže byť:

- publikovaný, ale ešte nenasadený,
- nasadený iba do stagingu,
- vystavený iba jednému ringu,
- nasadený v niektorých regiónoch,
- stiahnutý z distribúcie, ale stále bežať v produkcii.

Preto udržiavaj zvlášť:

- release/distribution state,
- deployment state,
- exposure state,
- support state,
- vulnerability/revocation state.

## 30. Observability a metriky

Sleduj:

- deployment frequency a lead time,
- queue a approval time,
- outdated/superseded deployments,
- deployment success a inconclusive rate,
- post-deploy validation failures,
- exposure before detection,
- rollback/roll-forward úspešnosť,
- environment drift,
- orphaned review apps,
- deployment record completeness,
- percent releases s immutable assets, SBOM a provenance,
- release revocation a recovery time.

Metrika má byť odvodená z pravdivého runtime a release recordu, nie iba zo zeleného job statusu.

## 31. Diagnostický postup

Keď deployment alebo release stav nesedí:

1. **Identifikuj subject —** source, artifact digest, config, environment a release version.
2. **Over GitLab record —** pipeline, job, actor, status, approvals a timestamps.
3. **Over effective runtime —** digest, replicas, config, routing a health.
4. **Skontroluj controller —** GitOps/cloud reconciliation, eventy a partial failures.
5. **Skontroluj concurrency —** resource group, novší desired state a outdated job.
6. **Skontroluj variables/identity —** environment scope, claims a target account.
7. **Over shared state —** schema, events, cache a side effects.
8. **Urči containment —** pause, disable, traffic shift, rollback alebo roll-forward.
9. **Uchovaj evidence —** logs, runtime inventory, config a deployment timeline.
10. **Oprav lifecycle —** policy, validation, cleanup alebo release manifest.

## 32. Typické anti-patterny

### Environment je iba názov v YAML

Chýba owner, target identity, permission boundary a runtime verification.

### Zelený deploy job = zdravá produkcia

Job môže iba odoslať asynchrónny request alebo zmeniť nesprávny target.

### Manual job = approval

Kliknutie bez evidence a eligibility nie je risk decision.

### Mutable artifact tag v deployment recorde

Neskôr nemožno určiť, ktoré bytes boli nasadené.

### Review app bez TTL

External resources zostávajú po merge a vytvárajú náklady aj attack surface.

### Stopped environment = odstránené resources

GitLab UI status nemusí reflektovať cloud, storage, DNS ani identity cleanup.

### Release job znovu buildne artifact

Release bytes sa líšia od testovaného candidate artifactu.

### Release asset smeruje na expirovateľný job artifact

Download a rollback capability po čase zmiznú.

### Tag alebo release object = runtime deployment

Distribučný záznam nehovorí, kde a komu je verzia reálne vystavená.

## 33. Praktický rozhodovací rámec

Pred deploymentom alebo release odpovedz:

1. Aká je presná environment identity a runtime boundary?
2. Aký immutable artifact a config revision sú subjectom?
3. Čo je desired, recorded a effective state?
4. Ktorá identity smie deployovať a prečo?
5. Ako sa rieši approval freshness?
6. Aký lock alebo generation zabráni outdated deploymentu?
7. Čo presne znamená job success?
8. Ako sa overí runtime digest, health a business outcome?
9. Aký je rollback/roll-forward a shared-state limit?
10. Ako sa cleanupnú dynamic resources a identities?
11. Čo obsahuje release manifest?
12. Kde sú dlhodobé immutable assets?
13. Ako sa rieši deprecation, yanking a revocation?
14. Ako sa produkčný deployment spätne mapuje na MR, pipeline a evidence?

## 34. Kontrolný checklist

- environment names a tiers sú konzistentné;
- production environment je protected;
- deployment job a runner sú v trusted boundary;
- subject obsahuje artifact digest a config revision;
- approvals sú viazané na rovnaký subject;
- stale a outdated deployments sú blokované;
- mutation jobs sú serializované;
- workload identity je short-lived a environment-scoped;
- runtime verification kontroluje effective state;
- GitOps request a reconciled deployment sa odlišujú;
- review apps majú izoláciu, TTL a reconciled cleanup;
- rollback eligibility je overená pred rolloutom;
- release job nerebuildí artifacts;
- release manifest je immutable;
- release assets používajú dlhodobý registry store;
- SBOM, provenance a signatures sa viažu na digest;
- support, deprecation a revocation lifecycle má ownera;
- audit trail prepája source, artifact, deployment a release.

## 35. Kontrolné otázky

1. Aký je rozdiel medzi environmentom, deploymentom a releaseom?
2. Čo odlišuje desired, recorded a effective state?
3. Prečo commit SHA nemusí identifikovať deployment subject?
4. Aké stavy má deployment state machine?
5. Prečo manual job nie je automaticky approval?
6. Ako vzniká outdated deployment?
7. Čo má dokazovať post-deployment verification?
8. Ako GitOps mení význam úspešného CI jobu?
9. Prečo stav `stopped` nedokazuje teardown review appu?
10. Aký je rozdiel medzi tagom, artifactom a GitLab Release?
11. Čo obsahuje multi-component release manifest?
12. Prečo release asset nemá smerovať iba na job artifact?
13. Aký je rozdiel medzi deprecation, yanking, revocation a deletion?
14. Prečo historicky zelený release nemusí byť dnes bezpečný?
15. Ako sa preukáže, čo je reálne nasadené v produkcii?

## Summary

GitLab environment reprezentuje runtime boundary, deployment zaznamenáva zmenu konkrétneho artifact/config subjectu v tejto boundary a Release eviduje distribuovanú a podporovanú verziu. Dôveryhodný lifecycle odlišuje desired, recorded a effective state, chráni deployment cez scoped identity, approvals a concurrency control, blokuje outdated deployments a overuje runtime nezávislou telemetry. Review apps potrebujú úplný teardown a releases musia referencovať immutable registry assets, release manifest, SBOM a provenance. Release, deployment, exposure, support a revocation sú odlišné stavy a musia zostať spätne mapovateľné na source a evidence.

## Glossary impact

Relevantné pojmy: GitLab environment, environment identity, deployment tier, desired state, effective state, deployment subject, deployment record, outdated deployment, resource group, review app, stop job, GitOps reconciliation, GitLab Release, release manifest, release asset, yanking a release revocation.

## Oficiálna dokumentácia

- [Environments](https://docs.gitlab.com/ci/environments/)
- [Deployments](https://docs.gitlab.com/ci/environments/deployments/)
- [Releases](https://docs.gitlab.com/user/project/releases/)
- [Review apps](https://docs.gitlab.com/ci/review_apps/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Container a package registry](container-and-package-registry.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Security scanning →](security-scanning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
