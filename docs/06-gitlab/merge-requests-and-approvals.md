# Merge requests a approvals

Merge request (MR) je GitLab workflow objekt pre návrh, diskusiu, automatizované overenie a integráciu source zmeny do target branch. Approval je explicitný review signal oprávneného používateľa; jeho skutočný blocking význam závisí od approval rules, branch policy, pipeline stavu a GitLab tieru.

## 1. Merge request lifecycle

```text
source branch
→ open merge request
→ pipeline and checks
→ review and discussion
→ approvals
→ mergeability evaluation
→ merge
→ post-merge pipeline/deployment
```

MR nie je iba webová obrazovka pre `git merge`. Spája identity, commits, diff, review, CI evidence, approvals, policy a audit trail.

## 2. Source a target

MR má:

- source project a branch,
- target project a branch,
- autora,
- reviewers/assignees,
- commits a diff,
- pipeline context,
- approvals a discussions,
- merge strategy a final result.

Pri fork MR sa approval a protection pravidlá odvodzujú najmä od target projektu. Source project je samostatná trust boundary.

## 3. Draft merge request

Draft signalizuje, že zmena ešte nie je pripravená na merge. Je vhodný na:

- skorú architektonickú diskusiu,
- priebežnú CI validáciu,
- zviditeľnenie rozpracovanej práce,
- koordináciu závislostí.

Draft nemá obchádzať branch protection ani required pipeline. Je to workflow stav, nie security control.

## 4. Review vs. approval

**Review** je proces čítania, komentovania, testovania a hodnotenia zmeny.

**Approval** je zaznamenané rozhodnutie oprávnenej identity.

Používateľ môže reviewovať bez formálneho approval a approval môže byť policy-neplatný, ak používateľ nie je eligible approver pre dané pravidlo.

## 5. Approval rules

Approval rule definuje:

- názov a účel,
- počet potrebných approvals,
- eligible users alebo groups,
- target branches alebo protected-branch scope,
- Code Owners podľa konfigurácie,
- override behavior podľa tieru a settings.

Viac rules môže reprezentovať rozdielne oversight boundaries:

```text
service owners: 1 approval
security: 1 approval pri security-sensitive paths
operations: 1 approval pri production manifests
```

Jedna osoba môže podľa GitLab pravidiel ovplyvniť viac rules, ak je eligible vo viacerých skupinách; pri separation of duties to treba navrhnúť vedome.

## 6. Optional vs. required approvals

Na niektorých tiers sú approvals iba informatívne. Required approval rules, Code Owner enforcement a centrálne policy možnosti môžu vyžadovať Premium alebo Ultimate.

Dokumentácia projektu musí jasne rozlíšiť:

- čo GitLab technicky blokuje,
- čo je iba tímová konvencia,
- čo vynucuje external compliance/policy systém.

## 7. Eligible approvers

Eligibility môže závisieť od:

- project/group membershipu,
- direct vs. inherited membershipu,
- role,
- explicitného user/group approveru,
- Code Owner statusu,
- target branch,
- security approval policy,
- project/tier settings.

Pri group approvers GitLab môže vyžadovať direct membership pre platné approval. Vždy over konkrétnu verziu a tier.

## 8. Author a committer approvals

Silnejší governance model môže zakázať:

- approval vlastného MR autorom,
- approval používateľom, ktorý pridal commit,
- zmenu approval rules priamo v MR,
- zachovanie approvals po novom commite.

Tieto pravidlá znižujú self-approval a stale-evidence riziko, ale môžu spomaliť malé tímy. Použi risk-based model.

## 9. Reset approvals po zmene

Nový commit môže meniť reviewed content. Approval lifecycle má definovať:

- či sa approvals resetujú po pushi,
- ktoré changes vyžadujú nový security review,
- ako sa rieši rebase alebo conflict resolution,
- či merge train/merge queue vytvorí nový commit identity,
- ako sa zachová audit reviewovaného SHA.

Approval bez väzby na konkrétny commit SHA je slabá evidence.

## 10. Discussions a resolved threads

Open discussion môže indikovať nevyriešený risk. Project policy môže vyžadovať resolved threads pred merge.

Riziká:

- autor označí thread ako resolved bez skutočnej opravy,
- reviewer nevie, že diff sa zmenil,
- komentár sa viaže na outdated line,
- summary rozhodnutia chýba.

Pri dôležitých pripomienkach zachovaj explicitný outcome a reviewer re-check.

## 11. Code Owners

Code Owners mapujú paths na zodpovedných reviewers. Môžu pomôcť pri:

- security-sensitive kóde,
- infrastructure manifests,
- database migrations,
- shared libraries,
- compliance files,
- ownership boundaries.

CODEOWNERS nie je automaticky úplný organizačný model. Musí byť aktuálny, testovaný a prepojený s protected-branch approval enforcementom, ak má blokovať merge.

## 12. Pipeline a mergeability

MR môže zostať blocked aj po approvals kvôli:

- failed alebo running pipeline,
- merge conflicts,
- open threads,
- missing approvals,
- stale branch alebo policy,
- required status checks,
- merge train state.

„Approved“ neznamená „safe to merge“.

## 13. Pipeline types

Rozlišuj:

- branch pipeline,
- merge request pipeline,
- merged-results pipeline,
- merge train pipeline,
- parent/child alebo multi-project pipeline.

Review evidence má zodpovedať tomu, čo sa reálne mergeuje. Branch pipeline na source branch nemusí zachytiť konflikt s aktuálnym target branch stavom.

## 14. Merge strategies

GitLab môže podľa projektu podporovať napríklad:

- merge commit,
- merge commit so semi-linear history,
- fast-forward merge,
- squash pri merge,
- rebase pred merge.

Voľba ovplyvňuje:

- históriu,
- commit identity,
- rollback/cherry-pick,
- release notes,
- traceability,
- pipeline behavior.

Stratégia musí byť konzistentná s branching a release modelom.

## 15. Squash

Squash môže zjednodušiť mainline, ale:

- mení commit SHA,
- môže stratiť granularitu jednotlivých commits,
- komplikuje väzbu na podpísané commits,
- ovplyvňuje backport/cherry-pick.

MR, issue a release record majú zachovať potrebnú traceability.

## 16. Merge when pipeline succeeds

Automatický merge po splnení podmienok znižuje manuálne čakanie. Potrebuje však:

- aktuálny target state,
- správny pipeline context,
- nezastaralé approvals,
- merge conflict handling,
- branch protection,
- cancellation pri novej zmene.

Automatický merge nie je náhrada za merge queue pri vysokej concurrency.

## 17. Merge trains a queues

Merge train overuje sériu MRs v predpokladanom poradí integrácie. Pomáha udržať mainline health, keď viac zmien čaká na merge.

Sleduj:

- queue time,
- pipeline duplication,
- failure attribution,
- reordering,
- cancellation,
- stale approvals,
- artifact identity po merge.

## 18. Approval policy

Centrálna approval policy môže vynucovať pravidlá podľa:

- protected branch,
- changed paths,
- security findings,
- scanner results,
- severity,
- project/group scope,
- author/committer restrictions.

Policy musí definovať fallback pri nevyhodnotiteľnom alebo chýbajúcom scan výsledku. Pre kritické rules je typicky bezpečnejší blocking default.

## 19. Security findings

Security approval založený na pipeline výsledku potrebuje:

- dôveryhodný scanner job,
- artifact/report integrity,
- aktuálny target/source comparison,
- jasné „new vs. existing“ finding semantics,
- exception lifecycle,
- qualified approver group.

Samotná severity bez reachability, exploitability a asset contextu môže vytvárať noise.

## 20. Exceptions

Approval bypass alebo exception má mať:

- dôvod,
- ownera,
- approvera s oddelenou zodpovednosťou,
- scope,
- expiry,
- compensating controls,
- audit trail,
- follow-up issue.

Permanentný bypass ruší hodnotu approval policy.

## 21. Review quality

Dobrý reviewer overuje:

- intent a scope,
- correctness a failure modes,
- security a data handling,
- operability a observability,
- compatibility,
- tests a rollback,
- documentation,
- unnecessary complexity.

Approval count nie je priamou metrikou review kvality.

## 22. Small merge requests

Menšie MRs zvyčajne:

- skracujú review time,
- znižujú cognitive load,
- uľahčujú rollback,
- zlepšujú failure attribution,
- znižujú merge conflicts.

Umelé rozdelenie jednej nekompatibilnej zmeny bez bezpečného intermediate state však môže zvýšiť risk.

## 23. Audit a traceability

Zachovaj väzbu:

```text
requirement/issue
→ merge request
→ reviewed commit SHA
→ approvals
→ pipeline evidence
→ merge commit
→ artifact digest
→ deployment/release
```

Tým možno spätne určiť, čo bolo reviewované a čo reálne nasadené.

## 24. Troubleshooting

### MR má approvals, ale nemožno ho mergeovať

Skontroluj pipeline, conflicts, unresolved threads, target branch protection, approval-rule scope a merge train.

### Approval zmizol po pushi

Project/policy resetuje approvals pri novom commite alebo rule sa prepočítala.

### Používateľ je v approver group, ale approval sa nepočíta

Over direct membership, role, target branch, group sharing a konkrétne rule eligibility.

### Pipeline v MR nevidí protected variables

Source/ref nie je trusted alebo pipeline pochádza z fork-u. Neobchádzaj trust boundary len kvôli testu.

### Code Owner approval sa nevyžaduje

Over CODEOWNERS match, protected target branch a zapnutie Code Owner requirement v branch rule.

## 25. Anti-patterny

### Approval od autora vlastnej zmeny

Neposkytuje nezávislý review signal.

### Required approvals bez dostupných approvers

Vytvára permanentný delivery bottleneck.

### Review iba podľa zeleného pipeline

Automatické testy neoverujú všetky design, security a operational riziká.

### Approval zostáva po zásadnom novom commite

Evidence je stale.

### Maintainer bypass ako štandardný workflow

Branch a approval policy sa stáva iba dekoráciou.

## 26. Kontrolné otázky

1. Aký je rozdiel medzi review a approval?
2. Čo definuje approval rule?
3. Prečo approval musí byť viazaný na commit SHA?
4. Ako sa líši branch pipeline od merged-results pipeline?
5. Kedy použiť Code Owners?
6. Čo môže blokovať merge aj po approvals?
7. Ako merge strategy ovplyvňuje traceability?
8. Čo rieši merge train?
9. Aké riziká má approval policy založená na scanner results?
10. Čo má obsahovať approval exception?

## Glossary impact

Relevantné pojmy: GitLab merge request, approval rule, eligible approver, Code Owner, resolved thread, merged-results pipeline, merge train, merge strategy, squash merge, stale approval, approval policy a mergeability.

## Oficiálna dokumentácia

- [Merge request approvals](https://docs.gitlab.com/user/project/merge_requests/approvals/)
- [Merge request approval rules](https://docs.gitlab.com/user/project/merge_requests/approvals/rules/)
- [Merge request approval settings](https://docs.gitlab.com/user/project/merge_requests/approvals/settings/)
- [Merge request approval policies](https://docs.gitlab.com/user/application_security/policies/merge_request_approval_policies/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Projects, groups a permissions](projects-groups-permissions.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Protected branches a environments →](protected-branches-and-environments.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
