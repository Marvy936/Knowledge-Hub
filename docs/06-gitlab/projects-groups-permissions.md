# Projects, groups a permissions

GitLab project nie je iba Git repository. Spája source, merge requests, pipelines, registries, variables, environments, releases, security evidence a audit. Permission decision nad projectom preto môže ovplyvniť celý delivery chain. Group a subgroup nie sú iba organizačné folders; vytvárajú namespace, inheritance, sharing a policy boundaries, ktoré určujú effective access aj po presune projektu alebo zmene direct membership.

Bezpečný model sa nepýta iba „akú rolu má user v project-e“. Pýta sa, cez ktoré direct, inherited, shared, custom-role, token alebo service-account paths získava capability nad konkrétnym resource a operation. Najvyššia effective role nemusí byť viditeľná v project member list-e, ak pochádza z parent group alebo shared group accessu.

## 1. Dominantný namespace-to-capability model

```text
business ownership a lifecycle intent
→ exact group/subgroup/project namespace subject
→ direct, inherited, shared a token access paths
→ role/custom permission a resource policy
→ highest effective capability
→ konkrétna source/pipeline/registry/environment operation
→ audit, expiration, review, transfer a revocation
```

Role je agregát permissions. Capability verdict je vždy viazaný na operation a resource. Developer môže pushovať do unprotected branch-e, no protected branch policy ho odmietne. Maintainer môže meniť project settings, no protected environment môže vyžadovať inú deployment authority.

## 2. Exact namespace subject

```yaml
namespaceSubject:
  instance: gitlab.atlas.example
  topGroup:
    id: 42
    fullPath: atlas
  subgroup:
    id: 117
    fullPath: atlas/payments
  project:
    id: 481
    pathWithNamespace: atlas/payments/settlement-api
    repositoryStorage: default
    visibility: private
    namespaceGeneration: ns-pay-184
  ownership:
    businessOwner: payments
    technicalOwner: settlement-platform
    securityBoundary: regulated-payments
  lifecycle:
    createdAt: 2024-03-14
    plannedReviewAt: 2026-08-31
```

Names a paths môžu byť zmenené. Numeric IDs pomáhajú zachovať internal identity, no project transfer mení inheritance a policy context. Transfer je authorization transition, nie cosmetic rename.

## 3. Group hierarchy podľa authority

Hierarchy má vyjadrovať shared ownership, policy a lifecycle. Kopírovanie organizačného diagramu môže vytvoriť príliš broad parent roles. Každý parent group member sa môže zdediť do všetkých descendants podľa effective role rules.

```text
atlas
├── platform
├── payments
│   ├── shared-libraries
│   ├── settlement-api
│   └── reporting
└── experiments
```

Ak `atlas` obsahuje široký Maintainer membership, všetky regulated subprojects môžu mať neočakávaný access. High-risk boundary môže potrebovať samostatný top-level group, explicitné membership a vlastné policy inheritance.

## 4. Effective membership graph

Access paths zahŕňajú:

- direct project membership;
- inherited parent-group membership;
- project alebo group sharing s inou group;
- invited external user;
- service account alebo bot;
- personal, project alebo group access token;
- deploy token a CI job token;
- custom role permissions;
- instance administrator alebo external authorization system.

Effective capability je union allowed paths obmedzená resource-specific policy. Expired direct role neodstráni access, ak user stále dedí vyššiu parent role.

Praktický API read-back:

```bash
curl --fail --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/481/members/all?per_page=100" \
  | jq '.[] | {id,username,access_level,expires_at,created_by}'
```

Endpoint `members/all` môže v podporovanej GitLab generation zahrnúť inherited/invited effective memberships podľa API semantics. Output preukazuje current API representation, nie všetky token capabilities, admin bypass alebo external authorization. Token inventory a protected-resource policies sa čítajú samostatne.

## 5. Built-in a custom roles

Built-in roles Guest, Planner, Reporter, Developer, Maintainer a Owner majú product-specific permissions a scope. Owner je typicky group-level authority, nie bežná project role. Exact semantics sa musia overiť pre current GitLab version/tier.

Custom role môže pridať selected permissions k base access levelu. Nie je vhodné vytvoriť desiatky neauditovateľných near-duplicate rolí. Custom role subject má ownera, permission inventory, approved use cases, consumers a review date.

```text
base role
+ explicit custom permissions
→ effective capability set
```

Názov `Deployment Operator` nepreukazuje least privilege. Praktický forbidden test musí ukázať, že subject vie deployovať approved environment a nevie meniť protected branch alebo unrelated variables.

## 6. Human a non-human identities

Human user, service account, project access token, group access token, deploy token a CI job token majú odlišný lifecycle a audit meaning.

```text
human
→ joiner/mover/leaver, MFA/SSO, personal accountability

service account
→ owned non-human principal, bounded purpose, credential rotation

access token
→ capability via scopes + role + resource context + expiry

CI job token / ID token
→ pipeline-bound short-lived workload identity
```

Generic shared user ničí attribution. Long-lived token bez ownera a expiry prežíva team changes. Non-human access sa má viazať na system purpose a revocation event, nie na osobný účet developera.

## 7. Token capability

Token scope nie je jediný authorization boundary. Project access token má role, API scopes, target project a expiry. Personal token zdedí user capabilities. Deploy token má repository/package scopes, no nemá byť použitý ako general API credential.

Token metadata read-back:

```bash
curl --fail --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/481/access_tokens" \
  | jq '.[] | {id,name,access_level,scopes,expires_at,revoked,active}'
```

Output preukazuje listed project access tokens podľa caller authority. Nepreukazuje token secret, actual use, group/personal/deploy tokens ani cached credentials na runners. Audit events a registry/API logs dopĺňajú usage evidence.

## 8. Onboarding, mover a leaver

Joiner dostane najnižší required access s expiry pre temporary work. Mover transition odstráni old paths pred pridaním new broad role, inak union access zostane. Leaver process revokuje sessions, tokens, group shares, service-account ownership a CI variables, ktoré boli viazané na osobu.

```text
identity event
→ effective-path inventory
→ desired capability decision
→ remove obsolete direct/inherited/share/token paths
→ add bounded new path
→ effective read-back
→ positive a forbidden operation test
```

„Removed from project“ nie je leaver completion, ak parent group membership alebo personal token stále umožňuje access.

## 9. Access review

Review sa nerobí iba exportom current members. Potrebuje resource ownera, identity ownera, effective path, role/capability, last use, expiry a business reason. High-risk reviews zahŕňajú protected branches, environments, variable management, runner administration, registry deletion a token creation.

Unused access nemusí byť visible v Git events. User môže mať schopnosť meniť CI variables alebo environment approvals bez recent commitov.

## 10. Project sharing a transfer

Sharing projektu s groupou pridáva ďalší membership path. Share expiry a max role sú critical. Transfer projectu mení full path, parent policies, inherited members, runners, variables, registry paths a integrations. Pred transferom sa vytvorí before/after authority graph.

```text
current namespace + effective controls
→ intended target namespace
→ predicted inherited access/policies
→ transfer lock and backup
→ project transfer
→ member/token/runner/variable/protected-resource read-back
→ forbidden old-path test
```

## 11. Connected incident `GL-PAY-72`

Atlas presunul `settlement-api` z `atlas/legacy` do `atlas/payments`. Tím odstránil direct Maintainer role externého consultanta z projektu. Consultant však zostal Owner v shared group `atlas-vendors`, ktorá bola invited do parent group s Developer accessom. Parent `atlas` zároveň zdedil broad Maintainer role pre platform contractorov.

```text
project transfer
→ new parent inheritance
+ existing shared-group path
→ effective Developer/Maintainer capabilities
→ source and CI configuration mutation
```

Consultant nemohol merge-núť protected branch, ale mohol vytvoriť branch, zmeniť `.gitlab-ci.yml` a spustiť pipeline na shared runneri. Jeho personal access token mal `api` scope a neexpiroval. Po 19 dňoch zmenil CI include na external fork; incident bol zistený až z audit eventu.

Root cause bol incomplete effective-access graph. Direct project member list sa zamieňal za complete authority.

## 12. Containment, recovery a acceptance

Containment revoke-ne user sessions a tokens, pause-ne pipelines, preserve-ne audit/member/share records a identifikuje source/artifacts vytvorené počas exposure window-u. Recovery odstráni shared/inherited paths, zavedie boundary-specific group, pinne trusted CI dependencies a rebuild-ne affected artifacts.

Access model je prijatý iba vtedy, keď:

```text
namespace IDs, paths a ownership sú exact
+ all direct/inherited/shared/token paths sú inventoried
+ role/custom permission meaning je current
+ human/non-human identities majú owner/expiry
+ mover/leaver odstráni old paths
+ transfer prepočíta effective access
+ source, variable, runner, registry a environment capabilities sú reviewed
+ effective API read-back zodpovedá intentu
+ forbidden alternate path je testovaný
+ second review neobjaví orphan token alebo share
```

## 13. Troubleshooting flow

```text
subject identity
→ group/project namespace and transfer history
→ direct/inherited/shared memberships
→ custom roles and protected policies
→ personal/project/group/deploy/CI tokens
→ actual operation and audit event
→ revocation and residual sessions/caches
```

Competing hypotheses môžu byť parent inheritance, shared group, admin, token, custom role, project transfer, stale session alebo alternate API path. Project members page samostatne neuzatvára investigation.

## 14. Anti-patterny

### Project member list ako celý access inventory

Ignoruje inheritance, shares, tokens, admin a protected-resource policy.

### Broad parent Maintainer pre convenience

Propaguje high capability do všetkých descendants.

### Shared bot user

Niči attribution, ownera a bezpečný leaver lifecycle.

### Token bez expiry

Capability prežíva project, team a purpose changes.

### Transfer bez before/after authority diffu

Nový parent môže pridať members, runners, variables a policies.

## 15. Kontrolné otázky

1. Prečo GitLab project nie je iba repository?
2. Čo tvorí exact namespace subject?
3. Ako sa počíta effective membership?
4. Ktoré token types majú odlišný purpose?
5. Čo preukazuje `members/all` API a čo nie?
6. Ako custom role dopĺňa base role?
7. Prečo direct removal nemusí revoke-núť access?
8. Čo musí obsahovať project transfer gate?
9. Ktoré hidden paths zostali v `GL-PAY-72`?
10. Ako sa testuje forbidden variable alebo environment operation?
11. Čo musí access review hodnotiť okrem last commit?
12. Ako sa uzatvára token compromise?

## Glossary impact

Relevantné pojmy: GitLab namespace, group, subgroup, project, namespace generation, direct membership, inherited membership, shared membership, effective access, built-in role, custom role, service account, project access token, group access token, deploy token, access review, project transfer a access-path revocation.

## Primárne zdroje

- [GitLab Docs — Members of a project](https://docs.gitlab.com/user/project/members/)
- [GitLab Docs — Permissions and roles](https://docs.gitlab.com/user/permissions/)
- [GitLab Docs — Groups](https://docs.gitlab.com/user/group/)
- [GitLab API — Members](https://docs.gitlab.com/api/members/)
- [GitLab Docs — Project access tokens](https://docs.gitlab.com/user/project/settings/project_access_tokens/)
- [GitLab API — Project access tokens](https://docs.gitlab.com/api/project_access_tokens/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Praktický CI/CD projekt od source change po overený production release](../05-ci-cd-and-release/ci-cd-practical-walkthrough.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Merge requests a approvals →](merge-requests-and-approvals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
