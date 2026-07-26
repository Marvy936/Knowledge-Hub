# Protected branches a environments

Protected branches a tags chránia dôveryhodné Git refs. Protected environments chránia runtime mutation. Ide o dve samostatné authorization boundaries, ktoré musia byť spojené immutable artifactom a auditovateľnou deployment identity.

```text
source actor
→ protected ref policy
→ reviewed final SHA
→ immutable artifact digest
→ trusted deployment job identity
→ protected environment policy
→ runtime mutation
```

Chránený `main` nezaručuje chránenú produkciu. Protected environment nezaručuje, že nasadený artifact pochádza z reviewovaného source. Bez oboch boundaries možno obísť delivery chain na source alebo runtime strane.

Konkrétne branch-rule combination, deployment approvals a environment controls závisia od GitLab verzie, offeringu, tieru a konfigurácie. Effective policy treba overiť na konkrétnej inštancii.

## 1. Nosný scenár: Atlas Payments release

Atlas používa:

```text
protected branch: main
protected release tags: v*
protected environment: production
trusted deploy job: deploy_production
artifact: registry digest D42
```

Developer vytvorí MR. Po review a merged-result pipeline sa zmena dostane do `main`. Post-merge build publikuje digest `D42`. Production job používa short-lived cloud identity a deklaruje environment `production`.

Ochranný chain:

```text
MR a approvals
→ allowed-to-merge na main
→ build D42
→ release approval pre D42 + config C8
→ allowed-to-deploy do production
→ serialized deployment generation G42
```

Tri incidenty odhalia slabé hranice:

1. wildcard branch rule povolí Developerom direct push napriek špecifickej release rule;
2. job deklaruje environment `production-new`, ktorý nie je protected;
3. starší pipeline run dokončí po novšom a prepíše produkciu späť.

## 2. Source a runtime authorization sú oddelené

### Source boundary

Chráni:

- direct push;
- merge;
- force push a history rewrite;
- branch/tag deletion;
- Code Owner a approval enforcement;
- trusted ref contexts pre CI a publication.

### Runtime boundary

Chráni:

- kto alebo čo smie deployovať;
- target environment identity;
- deployment approvals;
- environment-scoped credentials;
- serialization a outdated-deployment prevention;
- break-glass runtime mutations.

```text
allowed to merge
≠ allowed to deploy

pipeline trigger permission
≠ runtime cloud authorization
```

## 3. Protected branch subject a rule resolution

Protection sa vzťahuje na branch name alebo pattern. Effective policy vzniká z applicable project a group rules.

```text
branch name
→ exact a wildcard matches
→ project a inherited group rules
→ capability-specific combination
→ effective push/merge/force/unprotect decision
```

Pri overlapping rules sa nespoliehaj na intuitívne „najprísnejšie určite vyhrá“. GitLab môže pri viacerých matching rules kombinovať settings rozdielne; pri mnohých permissions je výsledok permissive. Reprezentatívne identities a operations treba testovať.

Rizikový príklad:

```text
release/* → iba release managers
*         → Developers môžu pushovať
```

Široké pravidlo môže oslabiť zamýšľanú release boundary.

## 4. Allowed to push a allowed to merge

### Allowed to push

Priama aktualizácia refu môže obísť:

- MR review;
- approvals;
- discussions;
- merged-result pipeline;
- merge train;
- path ownership.

### Allowed to merge

Povoľuje dokončiť MR po splnení ostatných policy conditions. Neznamená automaticky direct push.

Bezpečný default pre kritický mainline:

```text
direct push: nobody alebo úzka automation
merge: eligible actor cez MR
force push: disabled
unprotect: silne obmedzené
```

## 5. Unprotect je policy-management capability

Actor schopný odstrániť protection môže následne vykonať operáciu, ktorú policy blokovala.

Dočasný unprotect potrebuje:

```text
explicitný incident/change record
→ presný ref a actor scope
→ backup pôvodného ref state-u
→ audit mutations počas okna
→ obnova protection
→ verification a post-event review
```

Unprotect bez restoration evidence je otvorená security boundary.

## 6. Protected tags a release identity

Tag môže spustiť publication alebo production release. Chráň tags používané na:

- release pipelines;
- package/container publication;
- signing a provenance;
- support/backport lines.

```text
validated release subject
→ authorized protected tag
→ tag pipeline overí commit/policy
→ immutable artifact digest
→ release record
```

Tag stále nie je content identity. Record musí uchovať commit SHA aj artifact digest.

## 7. Protected environment subject

Deployment subject je:

```text
artifact digest
+ rendered config/infrastructure revision
+ trusted job definition revision
+ target environment
+ deployment actor/job identity
+ rollout policy
```

Protected environment obmedzuje runtime mutation nad konkrétnou environment identity. Používateľ s deploy-only accessom nemusí mať push alebo merge access k source branchu.

## 8. Environment naming je security-relevant input

GitLab environment vzniká z mena deklarovaného jobom.

```text
production
prod
Production
production-new
prod/us-east
```

Ak je protected iba `production`, job s podobným názvom môže vytvoriť iný neprotected environment a pritom používať rovnaký external target.

Atlas zavádza:

- kanonické environment names;
- explicitný deployment tier;
- shared trusted template;
- lint/policy nad environment declaration;
- zákaz mena odvodeného z nedôveryhodného inputu;
- inventory GitLab environmentov voči reálnym cloud targets.

## 9. Allowed to deploy a runtime identity

Deployment authorization hodnotí:

```text
human/job actor
+ project/group access path
+ pipeline/ref trust context
+ environment match
+ approval state
+ service/workload identity scope
→ deployment permission
```

Právo spustiť pipeline alebo manual job nie je automaticky právo deployovať. Job musí byť asociovaný so správnym environmentom a následne získať external runtime authorization.

## 10. Deploy job je privilegovaný program

Trust závisí od:

- CI definition revision;
- source/ref contextu;
- included templates a scripts;
- runner/executor trustu;
- effective variables;
- artifact digestu;
- environment declaration;
- cloud/cluster identity.

```text
untrusted branch verification
→ immutable artifact/evidence
→ trusted deployment entrypoint
→ short-lived environment identity
→ protected runtime target
```

MR branch script nemá dostať produkčné credentials iba preto, že job sa volá `deploy-production`.

## 11. Protected a environment-scoped variables

Protected variable obmedzuje distribution podľa trusted ref contextu. Nechráni pred:

- malicious code na trusted refe;
- kompromitovaným include/template;
- log/artifact/cache leakage;
- príliš širokým runner hostom;
- static external credential scope-om.

Environment-scoped variable pridáva environment match a precedence:

```text
variable key
+ source level
+ protected status
+ environment scope
+ pipeline/ref context
+ job override
→ effective runtime value alebo absence
```

Preferuj short-lived workload identity pred dlhodobým production key.

## 12. Deployment approval musí patriť immutable subjectu

Approval packet obsahuje:

- artifact digest;
- config/infrastructure revision;
- target environment;
- risk a evidence;
- rollout/observation plan;
- recovery eligibility;
- known exceptions a blast radius.

Zmena digestu, configu, deploy jobu alebo významného environment state-u môže approval invalidovať. Manuálne kliknutie bez decision contextu je ceremónia.

## 13. Deployment serialization a generation

Dva runs môžu meniť rovnaký target:

```text
run A deployuje D41
run B deployuje D42
run B dokončí prvý
run A dokončí neskôr
→ production sa vráti na D41
```

Ochranný model:

```text
candidate generation G
→ acquire environment lock/resource group
→ compare current generation
→ deploy iba ak candidate stále eligible
→ record new generation a digest
→ verify effective runtime state
```

Serialization sama nerieši stale candidate, external actor, idempotency ani partial mutation.

## 14. Review apps sú untrusted runtime boundary

Review app potrebuje:

- unique environment/resource identity;
- izolovaný namespace/account;
- žiadne production credentials;
- bounded network access;
- anonymizované/synthetic data;
- quotas;
- TTL a idempotentný teardown;
- orphan cleanup;
- ochranu pred fork pipeline code.

Rovnaký deployment template môže byť znovupoužitý, ale identity a policy musia zostať environment-specific.

## 15. Worked failure: overlapping rule povolila direct push

Atlas nakonfiguroval:

```text
main → Maintainers môžu mergeovať, nobody push
*    → Developers môžu pushovať
```

Developer úspešne pushol priamo na `main`.

### Príčina

Tím predpokladal, že exact rule automaticky prepíše wildcard. Effective combination však ponechala permissive push capability.

### Dôsledok

Commit obišiel MR approvals a merged-result pipeline, ale post-merge build ho považoval za trusted mainline source.

### Náprava

- odstrániť permissive overlap;
- explicitne nastaviť direct push na critical refs;
- testovať rule matrix cez reprezentatívne identities;
- auditovať direct push a protection changes;
- source provenance gate rozlišuje reviewed merge od direct mutation.

## 16. Worked failure: environment-name spoofing obišlo protection

Útočne upravený job deklaroval:

```yaml
environment:
  name: production-new
```

Job používal cloud script smerujúci na rovnaký production cluster. `production-new` nebol GitLab protected environment.

### Príčina

Policy viazala ochranu iba na voľné meno, nie na canonical deployment contract a external target identity.

### Dôsledok

MR pipeline mohla získať neprimeraný runtime path alebo vytvoriť deployment mimo očakávanej approval history.

### Náprava

- canonical environment allowlist v trusted component-e;
- job policy over resolved CI config;
- environment tier a external target mapping;
- cloud identity trust iba pre trusted deploy job/ref;
- zákaz user-controlled environment names.

## 17. Worked failure: outdated run prepísal novší release

Run A začal deploy `D41`, potom čakal na pomalý rollout. Run B nasadil `D42` a skončil. Run A následne pokračoval a dokončil `D41`.

### Príčina

Chýbal generation check po získaní runtime locku a outdated-deployment prevention.

### Náprava

- jeden environment resource group;
- candidate generation compare-and-swap;
- superseded-run cancellation;
- deployment idempotency;
- runtime verification a relation previous/next deployment.

## 18. Kauzálny diagnostický walkthrough

Symptom: production zmenila version po jobe spustenom z MR, hoci `main` aj `production` sú označené ako protected.

### Krok 1 — stabilizuj subjects

```text
source SHA a pipeline source
resolved CI config digest
deploy job identity
environment name/tier
artifact digest
cloud target a workload identity
```

### Krok 2 — konkurenčné hypotézy

```text
H1: direct push alebo unprotected source ref
H2: deploy job vznikol v untrusted MR context-e
H3: environment name nezhoduje protected rule
H4: protected/environment variable precedence odhalila credential
H5: downstream job nie je asociovaný s protected environmentom
H6: cloud credential povoľuje deploy mimo GitLab authorization
H7: starší authorized job dokončil po novšom release
```

### Krok 3 — observation points

- branch audit a matching rules testujú H1;
- pipeline source a resolved job rules testujú H2;
- environment record a protection match testujú H3;
- variable provenance testuje H4;
- parent/downstream environment metadata testuje H5;
- cloud identity audit testuje H6;
- deployment generation/timeline testuje H7.

Atlas zistí, že MR pipeline vytvorila `production-new`, dostala static cloud key z broad project variable a deployla rovnaký cluster. H2/H3/H4/H6 sú podporené.

### Krok 4 — containment

- revoke/rotate cloud key;
- stop neautorizovaný job/environment;
- obnov intended digest cez trusted deployment workflow;
- audit artifacts, logs a runtime mutations.

### Krok 5 — verify outcome

```text
MR pipeline nemá production identity
iba canonical production job matchuje protected environment
cloud trust povoľuje iba trusted job subject
intended digest beží v runtime
environment/deployment record je kompletný
```

### Krok 6 — skorší control

Finding sa mení na resolved-config policy, canonical environment contract, workload identity a end-to-end unauthorized-deploy fixture.

## 19. Break-glass a drift

```text
urgent risk
→ explicitná break-glass identity/workflow
→ úzky čas/resource scope
→ immutable subject
→ audit a alert
→ stabilizácia
→ protection restoration a credential rotation
→ post-event review
```

Policy-as-Code musí rozlíšiť:

```text
intended policy
| schválená dočasná výnimka
| unauthorized drift
```

Automatické prepisovanie počas aktívneho incidentu bez contextu môže zhoršiť stav; výnimka však musí mať expiry a closure.

## 20. Diagnostický runbook

1. Urči source, artifact, job a runtime target identity.
2. Vyhodnoť všetky matching branch/tag rules.
3. Rozlíš push, merge, unprotect a deploy capabilities.
4. Skontroluj pipeline source a resolved deploy job.
5. Over environment name, tier a protected match.
6. Zostav effective variable a workload-identity provenance.
7. Over approvals, freshness, lock a deployment generation.
8. Contain-ni source alebo runtime path podľa mechanizmu.
9. Obnov intended digest a over external target.
10. Zmeň finding na rule, naming, identity alebo serialization control.

## 21. Referenčné pravidlá

- Protected ref a protected environment sú dve boundaries.
- Allowed to push a allowed to merge nie sú synonymá.
- Unprotect je policy-management capability.
- Release tag musí byť chránený, ale digest ostáva content identity.
- Effective branch policy sa počíta zo všetkých matching rules.
- Environment name je security-relevant input.
- Deploy job je privilegovaný program.
- Protected variable nie je úplná secret boundary.
- Deployment approval patrí digestu, configu a targetu.
- Runtime mutations potrebujú serialization aj generation check.
- Review app nemá production trust.
- Break-glass končí restoration evidence.

## 22. Zhrnutie

Dôveryhodný GitLab source-to-runtime authorization chain je:

```text
protected reviewed ref
→ immutable final SHA a artifact digest
→ trusted resolved deploy job
→ environment-scoped short-lived identity
→ protected canonical target
→ serialized generation-aware mutation
→ runtime a audit verification
```

Protection nie je názov alebo ikona v UI. Je to effective decision nad konkrétnou operáciou a subjectom. Diagnostika preto sleduje celý chain od ref rule cez pipeline context a variable provenance až po external runtime identity.

## Kontrolné otázky

1. Prečo protected branch nechráni automaticky production?
2. Ako sa líšia allowed-to-push a allowed-to-merge?
3. Prečo overlapping rules treba testovať?
4. Prečo je unprotect vyššia capability?
5. Čo tvorí deployment subject?
6. Ako environment-name spoofing obíde policy?
7. Čo protected variable nechráni?
8. Aký race rieši deployment generation check?
9. Prečo review app nesmie zdediť production identity?
10. Kedy je break-glass uzavretý?

## Oficiálna dokumentácia

- [Protected branches](https://docs.gitlab.com/user/project/repository/branches/protected/)
- [Protection rules and permissions](https://docs.gitlab.com/user/project/repository/branches/protection_rules/)
- [Protected environments](https://docs.gitlab.com/ci/environments/protected_environments/)
- [Deployment approvals](https://docs.gitlab.com/ci/environments/deployment_approvals/)
- [Deployment safety](https://docs.gitlab.com/ci/environments/deployment_safety/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Merge requests a approvals](merge-requests-and-approvals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: GitLab CI/CD syntax →](gitlab-ci-cd-syntax.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
