# Protected branches a environments

Protected branches a tags chránia dôveryhodné Git refs. Protected environments chránia runtime mutation. Ide o dve samostatné authorization boundaries, ktoré musia byť spojené immutable artifactom, subject-bound pipeline evidence a auditovateľnou deployment identity. Branch protection nepreukazuje, že production nemožno zmeniť alternate credentialom. Environment protection nepreukazuje, že deployed artifact vznikol z reviewed source.

Safe design sleduje celý chain od source actor-a cez final merge SHA a artifact digest po exact environment generation a runtime outcome. Allowed-to-push, allowed-to-merge, allowed-to-create-protected-tag, allowed-to-deploy a allowed-to-approve-deployment sú rozdielne capabilities.

## 1. Dominantný source-to-runtime enforcement model

```text
source actor a exact ref
→ protected branch/tag policy
→ reviewed merge-decision subject
→ final trusted SHA
→ immutable artifact digest a provenance
→ protected deployment job identity
→ protected environment policy/approval
→ runtime mutation and convergence
→ business acceptance and audit
```

Každá boundary môže mať alternate path. Maintainer môže meniť branch rules, project token môže volať API, runner môže mať direct kubeconfig a environment môže byť zmenené mimo GitLab. Complete protection zahŕňa capability inventory a forbidden-path tests.

## 2. Exact protection subject

Protection verdict musí pomenovať source ref, rule generation, actor capability, deployment target a artifact policy naraz. Human-readable pattern ako `main` alebo `production/*` je iba locator; effective behavior závisí od overlapping rules, current namespace a exact environment name. Nasledujúci subject preto oddeľuje source enforcement od runtime enforcement a spája ich release digestom.

```yaml
protectionSubject:
  projectId: 481
  source:
    branch: main
    branchRuleGeneration: branch-main-31
    allowedToMerge: [payments-maintainers]
    allowedToPush: []
    forcePushAllowed: false
    codeOwnerApprovalRequired: true
  tags:
    pattern: payments-*
    ruleGeneration: release-tags-12
    allowedToCreate: [release-controller]
  environment:
    name: production
    environmentId: 77
    protectionGeneration: env-prod-44
    allowedToDeploy: [production-release-bot]
    deploymentApprovalsRequired: 2
  artifactPolicySha: release-policy-66cf902
```

Pattern a human-readable names nie sú complete identity. Overlapping branch rules alebo environment-scoped variables môžu zmeniť effective behavior. Rule generation sa má odvodiť z exported configuration alebo policy repository commit.

## 3. Protected branch semantics

Protected branch controls typicky rozhodujú, kto smie pushovať alebo mergeovať a či force-push/code-owner rules platia. Exact feature behavior závisí od current GitLab version/tier. Dôležitý mechanizmus je oddeliť direct push od MR merge.

Ak Developer nemôže pushovať, ale Maintainer môže, Maintainer stále môže obísť MR unless `allowed_to_push` je empty alebo strict. „Only Maintainers can push“ nie je no-direct-push policy.

API read-back:

```bash
curl --fail --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/481/protected_branches/main" \
  | jq '{name,push_access_levels,merge_access_levels,allow_force_push,code_owner_approval_required}'
```

Output preukazuje current protected-branch API representation. Nepreukazuje overlapping wildcard rules, instance admin capability, deploy keys/tokens alebo current user effective access. List all branch rules a execute bounded forbidden push test v test project-e.

## 4. Protected tags

Protected tag chráni creation určitého ref patternu. Nezaručuje immutable package alebo image. Tag môže ukazovať na reviewed commit a pipeline môže stále rebuildnúť mutable artifact. Release promotion sa viaže na artifact digest a signed release manifest.

Overlapping patterns môžu vytvoriť unexpected effective permission. Release tag creator nemá automaticky dostať production deploy capability; tag event je trigger, nie final authorization.

## 5. Protected environment

Environment protection obmedzuje, kto môže deployovať. Deployment approval môže pridať human gate. Environment-scoped variables a protected variables môžu byť dostupné iba eligible jobs/ref contexts podľa product semantics.

Environment name v `.gitlab-ci.yml` musí presne zodpovedať protected environment patternu. Dynamic names ako `production/$REGION` môžu byť outside intended rule alebo matchovať broad wildcard.

```yaml
production_deploy:
  stage: deploy
  environment:
    name: production/eu-central-1
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
  script:
    - ./deploy.sh "$RELEASE_MANIFEST_DIGEST"
```

YAML preukazuje source intent. Nepreukazuje resolved rules, environment protection, job identity ani actual deploy target. GitLab API a runtime read-back dopĺňajú evidence.

## 6. Source/runtime separation

Source protection a runtime protection sa spájajú immutable artifactom:

```text
trusted final SHA
→ build-once artifact digest
→ signature/provenance
→ subject-bound promotion
→ protected environment deployment
```

Deployment job nemá checkoutovať a vykonávať arbitrary source scripts z untrusted branch. Má používať reviewed workflow a immutable deploy tool/artifact. Otherwise protected environment credential môže execute source-controlled code.

## 7. Deployment identity

Long-lived kubeconfig v project variable vytvára alternate runtime authority. Better model používa GitLab ID token a external federation s claims pre project, namespace, ref, environment a job.

```yaml
id_tokens:
  GITLAB_OIDC_TOKEN:
    aud: https://vault.atlas.example
```

Token issuance preukazuje, že GitLab poskytol signed assertion pre configured audience. Nepreukazuje, že Vault/cloud trust policy je narrow alebo že job je current approved deployment subject. External role binding a resulting caller identity sa read-backnú.

## 8. Deployment approvals

Approval je viazané na deployment subject: artifact digest, target environment generation a requested action. Approval nad job name alebo pipeline ID môže byť stale po retry/rebuild. Approvers nemajú byť zároveň sole authors alebo environment operators pre high-risk transitions.

Failure, timeout alebo canceled approval flow nesmie sprístupniť fallback manual job bez rovnakého enforcementu.

## 9. Review apps a dynamic environments

Review app je environment created pre MR. Nemá používať production secrets, broad network, shared production database ani never-expiring resources. Dynamic environment name, namespace, DNS, identity a TTL tvoria exact review-app subject.

```text
MR/candidate
→ isolated namespace/account resources
→ non-production credential and data
→ bounded exposure
→ acceptance evidence
→ stop request
→ independent cleanup reconciliation
```

GitLab environment status `stopped` nepreukazuje deletion cloud resources. Cleanup read-back musí potvrdiť absence DNS, namespace, database, identity a storage.

## 10. Break-glass

Break-glass používa short-lived scoped capability, incident ID a explicitný resource/action. Po mutation sa authoritative source a deployment record reconciliujú, capability revokuje a forbidden normal path zostáva blocked.

```text
incident authority
→ temporary environment deploy permission
→ exact emergency artifact/config
→ runtime read-back
→ source/release reconciliation
→ revoke access
→ audit and retrospective
```

Permanent Maintainer access alebo shared production kubeconfig nie je break-glass.

## 11. Connected incident `GL-PAY-72`

Atlas protected `main` a required MR approvals, no Maintainers zostali allowed to push. Release job bežal z protected tagu a používal long-lived production kubeconfig v protected variable. Consultant s inherited Maintainer access force-pushol `main` počas incident window-u a vytvoril release tag. Tag pipeline spustila deploy bez environment approval, pretože job environment name bol `prod/eu`, zatiaľ čo protected environment rule chránila iba exact `production`.

```text
protected branch with Maintainer direct push
→ protected tag trigger
→ environment-name mismatch
→ protected variable/kubeconfig available
→ direct production mutation
```

Branch a tag UI zobrazovali protected status, no source review aj runtime approval boli bypassnuté. 18 Pods bežalo na unreviewed digest.

Root cause bol incomplete source/runtime protection subject a alternate paths.

## 12. Containment, recovery a acceptance

Containment revoke-ne kubeconfig/tokens, pause-ne environment jobs, preserve-ne branch/tag/audit/deployment events a inventory runtime digests. Recovery obnoví reviewed mainline, rebuild-ne trusted artifact, pinne environment naming/rules a nasadí cez scoped federation.

Protection model je prijatý iba vtedy, keď:

```text
branch/tag/environment rules and generations sú exact
+ direct push je forbidden where MR is required
+ force-push and unprotect capabilities sú reviewed
+ protected tag does not replace artifact policy
+ environment names match intended protection
+ deployment identity je scoped/short-lived
+ approval is artifact/target-bound and fresh
+ review apps have isolated identity/data/cleanup
+ break-glass reconciles and revokes
+ alternate API/token/credential paths are tested
```

## 13. Troubleshooting flow

Pri bypass-e sa branch, tag a environment badges nesmú zliať do jedného tvrdenia „bolo to protected“. Investigation sleduje každú capability osobitne: kto mohol meniť ref, kto vytvoril tag, aký pipeline/ref context dostal credential, ktorý environment pattern matchol a aká external identity vykonala runtime mutation. Prvý divergentný verdict určí skutočný bypass.

```text
source actor and effective role
→ branch/tag rules and overlapping patterns
→ final SHA and tag creator
→ pipeline/ref protection context
→ variable/ID-token availability
→ environment name and protection
→ deployment identity and audit
→ runtime digest and business outcome
```

Competing hypotheses môžu byť direct push, force-push, unprotect permission, tag rule, environment mismatch, protected variable exposure, runner kubeconfig alebo external deploy path. Protected badge samostatne nie je end-to-end proof.

## 14. Anti-patterny

### Maintainer push ako no-bypass policy

Maintainer-only push stále povoľuje direct source mutation mimo MR, iba ju obmedzuje na silnejšiu rolu. Ak policy vyžaduje review, `allowed_to_push` musí byť prázdne alebo presne bounded break-glass path a forbidden push test musí preukázať odmietnutie. Samotný protected badge no-bypass semantics nedokazuje.

### Protected tag ako immutable release

Protected tag chráni creation Git refu, nie bytes v registry ani dôkazy, ktoré pipeline neskôr vytvorí. Rovnaký tag-triggered job môže rebuildnúť odlišný image alebo publikovať mutable tag. Release authority preto patrí immutable digestu a subject-bound provenance, nie samotnému Git tagu.

### Production kubeconfig v variable

Long-lived kubeconfig v CI variable je reusable alternate authority priamo k runtime API. Môže prežiť job, byť skopírovaný do workspace-u a obísť protected-environment approval cez job bez environment declaration. Short-lived federation viazaná na exact project/ref/environment zmenšuje capability aj revocation window.

### Environment protection podľa nesprávneho mena

Protected-environment policy sa vyhodnocuje nad effective environment name. Ak job použije `prod/eu` a rule chráni iba `production`, credential a approval path môžu byť úplne odlišné. Naming contract sa preto validuje v resolved pipeline a testuje sa reprezentatívny dynamic name aj forbidden variant.

### Review app status `stopped` ako cleanup proof

GitLab status `stopped` je workflow record, nie inventory external resources. DNS, database, storage, IAM identity alebo namespace môžu zostať po partial cleanup-e. Closure potrebuje ownership labels, independent reconciliation a read-back absencie na každom authoritative targete.

## 15. Kontrolné otázky

1. Čím sa protected branch líši od protected environmentu?
2. Čo tvorí exact protection subject?
3. Prečo allowed-to-push a allowed-to-merge musia byť oddelené?
4. Čo preukazuje protected-branch API a čo nie?
5. Prečo protected tag nenahrádza artifact digest?
6. Ako environment name ovplyvňuje protection?
7. Ako sa spája source SHA s runtime digestom?
8. Prečo long-lived kubeconfig oslabuje boundary?
9. Čo sa bypasslo v `GL-PAY-72`?
10. Ako sa overuje review-app cleanup?
11. Čo musí obsahovať break-glass closure?
12. Ktoré alternate paths treba testovať?

## Glossary impact

Relevantné pojmy: protected branch, branch rule, allowed to push, allowed to merge, force push, protected tag, protected environment, allowed to deploy, deployment approval, protected variable, environment-scoped variable, deployment identity, review app, break-glass a source/runtime enforcement boundary.

## Primárne zdroje

- [GitLab Docs — Protected branches](https://docs.gitlab.com/user/project/repository/branches/protected/)
- [GitLab API — Protected branches](https://docs.gitlab.com/api/protected_branches/)
- [GitLab Docs — Protected tags](https://docs.gitlab.com/user/project/protected_tags/)
- [GitLab Docs — Protected environments](https://docs.gitlab.com/ci/environments/protected_environments/)
- [GitLab Docs — Deployment approvals](https://docs.gitlab.com/ci/environments/deployment_approvals/)
- [GitLab Docs — OpenID Connect authentication](https://docs.gitlab.com/ci/secrets/id_token_authentication/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Merge requests a approvals](merge-requests-and-approvals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: GitLab CI/CD syntax →](gitlab-ci-cd-syntax.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
