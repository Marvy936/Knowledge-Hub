# Merge requests a approvals

Merge request je evidence-driven integration decision nad presným source, target a policy contextom. Git dokáže technicky spojiť histories; MR má preukázať, prečo bolo spojenie konkrétneho candidate-u povolené. Review comment, approval badge ani green branch pipeline samostatne nevytvárajú dôveryhodný merge verdict. Decision musí byť viazaný na exact diff/candidate, current target generation, eligible approvers, resolved discussions, applicable ownership a complete fresh evidence.

MR nie je statická stránka. Source branch sa môže meniť, target branch napredovať, approval rules resetovať alebo nereštartovať, Code Owners sa zmeniť a pipelines môžu patriť branch, merged-results alebo merge-train candidate-u. Každá zmena relevantného subjectu musí invalidovať alebo revalidovať decision evidence.

## 1. Dominantný change-to-merge model

Lifecycle nižšie opisuje kompiláciu merge verdictu, nie iba poradie obrazoviek v GitLab UI. Každý transition mení subject alebo evidence, na ktoré sa approval viaže: source SHA, target SHA, synthetic candidate, diff version, policy generation alebo pipeline context. Ak sa ktorýkoľvek z nich zmení, predchádzajúci verdict sa musí explicitne invalidovať alebo znovu preukázať.

```text
change intent a issue/risk context
→ exact source SHA a current target SHA
→ diff a synthetic merge candidate
→ reviewer/discussion outcomes
→ applicable Code Owner a approval rules
→ complete fresh pipeline/security evidence
→ mergeability a policy verdict
→ final merge action
→ merged commit SHA a mainline read-back
→ post-merge invalidation alebo incident closure
```

Approval je decision nad subjectom, nie trvalý súhlas s branch name. Force-push alebo target movement môže zmeniť bytes, ktoré sa mergnú.

## 2. Exact merge-decision subject

Merge decision potrebuje identity envelope, ktorý umožní dokázať, aké bytes a aký target context reviewer a pipeline skutočne posudzovali. Branch name alebo MR IID sú iba locators; bez source, target, candidate a diff generation nemožno odlíšiť fresh approval od stale badge-u. YAML preto spája source, policy a evidence do jedného auditovateľného subjectu.

```yaml
mergeDecisionSubject:
  projectId: 481
  mergeRequestIid: 1842
  sourceBranch: feature/provider-routing-v18
  sourceSha: 8e21b8d
  targetBranch: main
  targetSha: 53d92af
  candidateSha: d94e1c6
  diffVersionId: 9021
  pipeline:
    id: 771184
    type: merged-results
    sha: d94e1c6
  approvalPolicyGeneration: mr-policy-pay-31
  codeOwnerGeneration: codeowners-44
  requiredApprovals:
    payments-codeowners: 1
    security: 1
    database: 1
  unresolvedDiscussions: 0
```

MR IID bez project ID nie je globally unique. Source SHA bez target/candidate SHA nepreukazuje integrated result. Pipeline ID bez type/sha môže patriť branch state-u.

## 3. Practical MR API read-back

```bash
curl --fail --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/481/merge_requests/1842" \
  | jq '{iid,state,sha,diff_refs,merge_status,detailed_merge_status,blocking_discussions_resolved,head_pipeline}'
```

Output preukazuje GitLab API representation v čase query. Nepreukazuje complete approval-rule evaluation, Code Owner freshness ani actual final merge candidate po ďalšom target update. Approval a pipeline endpoints sa čítajú samostatne a merge request sa znovu fetch-ne tesne pred merge action.

Approval state:

```bash
curl --fail --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/481/merge_requests/1842/approvals" \
  | jq '{approved,approvals_required,approvals_left,approved_by,rules}'
```

Tento output preukazuje current approval API. Nepreukazuje independent judgment, že approvers review-li current diff, ani že alternate merge path rovnaké rules presadí.

## 4. Reviewer, approver a Code Owner

Reviewer vykonáva technical review a discussion. Approver je subject eligible pre approval rule. Code Owner je ownership signal odvodený z matched paths a branch/rule semantics. Jeden user môže zastávať viac rolí, no policy má riešiť conflict of interest a separation of duties.

Code Owners rule je účinná iba ak matched paths, protected branch settings a approval requirement fungujú spolu. Pattern error alebo file move môže zmeniť ownership. Generated, vendored alebo infrastructure files potrebujú explicitného ownera.

## 5. Approval freshness

Approval má byť resetnuté alebo explicitne revalidated po zmene source SHA, meaningful diff, target/candidate alebo approval policy. GitLab settings sa môžu správať rozdielne podľa version/tier. Dôveryhodný project zaznamenáva expected reset semantics a testuje ich.

```text
approved subject d94e1c6
→ source force-push vytvorí candidate e11a902
→ approvals pre old subject sú stale
→ rules a evidence sa re-evaluate
```

Approval timestamp po force-push nie je sám o sebe proof, ak GitLab retained approval podľa configuration.

## 6. Pipeline context

Branch pipeline testuje source branch. Merge-request pipeline používa MR context. Merged-results pipeline testuje synthetic merge result. Merge train testuje candidate v poradí s predchodcami. Required context závisí od concurrency modelu.

Ak viac MRs môže byť schválených proti rovnakému targetu, branch-green evidence je stale po merge prvého. Merge train alebo fresh merged-result pipeline uzatvára integration race.

## 7. Discussions a review evidence

Unresolved discussion môže reprezentovať blocking defect, no resolved status samostatne nepreukazuje fix. Reviewer môže discussion resolve-núť bez code change alebo source sa môže neskôr zmeniť. Review closure má byť korelovaná s diff version a relevantným commitom.

Checklist nemá nahrádzať mechanistic review. Security-sensitive change potrebuje threats/permissions/evidence, database change mixed-version contract a pipeline change resolved graph/trust review.

## 8. Merge methods

Merge commit, squash, rebase a fast-forward menia history a traceability. Policy má definovať, ako sa source commits, MR, approvals, pipeline candidate a final mainline SHA korelujú.

Squash môže vytvoriť final commit SHA, ktorý neexistoval počas branch pipeline. Content tree môže byť rovnaký, no commit identity sa zmení. Post-merge check alebo server-generated commit metadata musí zachovať link na verified candidate.

## 9. Merge train a concurrency

Merge train vytvára ordered candidates a revaliduje changes v predicted mainline context-e. Ak predchodca zlyhá alebo sa odstráni, nasledujúce candidates sa prepočítajú. Evidence pre old train position je superseded.

Train nepreukazuje correct tests ani policy completeness. Rieši target concurrency, nie oracle quality.

## 10. Exceptions a emergency merge

Emergency merge môže mať shortened approval path, ale subject identity a audit zostávajú. Record obsahuje incident, exact diff/candidate, actor, omitted controls, compensating controls, expiry a mandatory retrospective validation.

Direct push na protected branch ako „emergency“ obchádza MR evidence a môže spustiť odlišný pipeline graph. Ak je break-glass nevyhnutný, má bounded credential a následnú source/release reconciliation.

## 11. Connected incident `GL-PAY-72`

MR 1842 menil provider routing a `.gitlab-ci.yml`. Dostala payments a security approvals nad source SHA `8e21b8d`, target `53d92af`. Potom author force-pushol commit, ktorý zmenil external include na fork. Project setting nezresetoval approvals a required pipeline bola branch pipeline, nie merged-results.

Súčasne iný MR zmenil shared event contract na main. MR 1842 sa mergol s novým targetom bez fresh candidate pipeline.

```text
approval pre diff v1
→ force-push diff v2
→ retained approvals
→ target advanced
→ branch-green evidence
→ merge candidate nebol testovaný
```

Final mainline obsahoval untrusted CI include a incompatible event producer. 6 412 events ostalo v backlogu. Root cause bol stale merge-decision subject a wrong pipeline context.

## 12. Containment, recovery a acceptance

Containment pause-ne merge/deploy pipelines, preserve-ne MR versions, approvals, pipelines, audit events a external include content a revoke-ne affected runner credentials. Recovery revert-ne alebo roll-forward-ne mainline cez fresh MR, pinne include SHA a pridá merged-results/merge-train policy.

MR model je prijatý iba vtedy, keď:

```text
source/target/candidate/diff subjects sú exact
+ applicable owner/approval rules sú current
+ approvals sú eligible, independent a fresh
+ discussions sa viažu na current diff
+ required pipeline testuje correct candidate context
+ final merge SHA/tree sa read-backne
+ source change alebo target advance invaliduje stale evidence
+ direct-push/emergency path je bounded and audited
+ forbidden retained-approval force-push je testovaný
+ second concurrent MR prejde train/revalidation
```

## 13. Troubleshooting flow

Pri nesprávnom merge verdict-e sa najprv rekonštruuje časová os subjectu. Diff versions, force-push, target movement, approval reset a pipeline type sa čítajú ako samostatné state transitions; až potom sa skúma, ktorý alternate merge alebo direct-push path policy obišiel. Aggregate green badge je iba index do týchto záznamov.

```text
project/MR identity
→ diff versions a source SHA history
→ target movements and candidate generation
→ approval rules/eligible approvers/reset semantics
→ Code Owner matching
→ pipeline types and SHAs
→ merge method/final SHA
→ alternate direct/API merge paths
```

Competing hypotheses môžu byť retained approval, wrong approver eligibility, Code Owner mismatch, branch pipeline, stale target, merge-train supersession, unresolved discussion bypass alebo direct push. MR green badge je aggregate presentation, nie complete evidence.

## 14. Anti-patterny

### Approval ako permanentný branch property

Approval patrí konkrétnej diff/candidate generation, nie názvu branchu. Force-push alebo target movement môže zmeniť výsledný tree bez zmeny MR URL, takže retained approval môže autorizovať bytes, ktoré reviewer nikdy nevidel. Policy musí definovať reset/revalidation trigger a acceptance test ho musí reprodukovať.

### Reviewer rovná sa approver

Reviewer participation je technical evidence; approver eligibility je authorization decision podľa konkrétneho rule-u. User môže komentovať alebo resolve-núť discussion bez toho, aby spĺňal required ownership, independence alebo role constraints. Verdict preto kontroluje approved_by proti effective rule evaluation, nie iba zoznam reviewerov.

### Branch pipeline ako merge result

Branch pipeline testuje source branch v jednom target context-e alebo bez neho. Nezahŕňa automaticky current target SHA ani concurrent changes, ktoré vytvoria final merge candidate. Pre high-risk integráciu sa evidence viaže na merged-results alebo merge-train candidate a po target movement-e sa znovu vytvorí.

### Code Owners file bez enforcement testu

CODEOWNERS je source declaration, nie samostatný enforcement verdict. Pattern môže nematchovať presunutý file, protected branch nemusí vyžadovať Code Owner approval alebo alternate merge path môže rule obísť. Test musí zmeniť reprezentatívny owned path a potvrdiť, že neeligible actor merge nedokončí.

### Emergency direct push bez reconciliation

Emergency direct push obchádza merge-decision subject, approval freshness a často aj iný pipeline graph. Ak je break-glass nevyhnutný, credential musí byť incident-scoped, short-lived a auditovaný a výsledný mainline/runtime state sa následne reconciliuje cez normálny source a release lifecycle. Bez tejto closure zostáva production na nepreukázanom alternate authority path-e.

## 15. Kontrolné otázky

1. Čo tvorí exact merge-decision subject?
2. Prečo source SHA nestačí?
3. Čo preukazuje MR API a čo nie?
4. Ako sa líši reviewer, approver a Code Owner?
5. Kedy sa approval stáva stale?
6. Aký je rozdiel medzi MR a merged-results pipeline?
7. Čo rieši merge train?
8. Ako merge method mení traceability?
9. Čo sa pokazilo v `GL-PAY-72`?
10. Ako sa testuje approval reset po force-pushi?
11. Ako sa uzatvára emergency merge?
12. Čo musí preukázať final mainline read-back?

## Glossary impact

Relevantné pojmy: merge request, merge-decision subject, diff version, source SHA, target SHA, candidate SHA, reviewer, approver, eligible approver, Code Owner, approval freshness, merged-results pipeline, merge train, merge method, blocking discussion a emergency merge.

## Primárne zdroje

- [GitLab Docs — Merge requests](https://docs.gitlab.com/user/project/merge_requests/)
- [GitLab Docs — Merge request approvals](https://docs.gitlab.com/user/project/merge_requests/approvals/)
- [GitLab Docs — Code Owners](https://docs.gitlab.com/user/project/codeowners/)
- [GitLab Docs — Merged results pipelines](https://docs.gitlab.com/ci/pipelines/merged_results_pipelines/)
- [GitLab Docs — Merge trains](https://docs.gitlab.com/ci/pipelines/merge_trains/)
- [GitLab API — Merge requests](https://docs.gitlab.com/api/merge_requests/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Projects, groups a permissions](projects-groups-permissions.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Protected branches a environments →](protected-branches-and-environments.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
