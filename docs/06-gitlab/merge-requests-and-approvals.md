# Merge requests a approvals

Merge request (MR) je evidence-driven integration decision nad presným source a target contextom. Git príkaz dokáže spojiť históriu; MR má dokázať, prečo bolo spojenie konkrétneho obsahu povolené.

```text
change intent
→ source SHA a diff
→ review a discussion outcomes
→ applicable ownership a approval policy
→ fresh pipeline evidence nad správnym candidate
→ mergeability verdict
→ final merge SHA
→ artifact a deployment provenance
```

Nosný model je:

```text
presný decision subject
+ úplné a čerstvé evidence
+ aplikovateľná policy
→ mergeability verdict
```

Ak sa zmení source SHA, target context, pipeline candidate alebo policy, predchádzajúce rozhodnutie môže byť stale.

Konkrétne approval, merged-results a merge-train capabilities sa menia podľa GitLab offeringu, tieru, verzie a konfigurácie. Stabilný je princíp subject identity, evidence freshness a integration-race kontroly.

## 1. Priebežný scenár: Jana a Atlas Payments

Jana mení payment API v branchi `feature/idempotency`. MR obsahuje:

- aplikačnú zmenu;
- databázovú migration;
- úpravu `.gitlab-ci.yml`;
- nové idempotency testy.

Prvá branch pipeline prejde. Počas review sa však `main` posunie zmenou request modelu. Janina zelená branch pipeline stále dokazuje iba jej source SHA, nie výsledok spojenia s aktuálnym targetom.

GitLab vytvorí merged-result candidate:

```text
source SHA S4
+ current target SHA T9
→ synthetic candidate C4
```

Path ownership aktivuje service-owner, database-owner a platform-owner review. Jana pridá opravný commit `S5`; approvals viazané na `S4` a pipeline nad `C4` už nemusia platiť.

MR sa následne zaradí do merge trainu. Candidate sa testuje za skôr čakajúcimi zmenami. Po squash merge vznikne final SHA `F11`, z ktorého build publikuje artifact digest `D11`.

```text
MR !142
→ reviewed S5
→ train candidate C7
→ final SHA F11
→ artifact D11
→ deployment record
```

## 2. Decision subject nie je MR číslo

MR `!142` je dlhodobý container diskusie. Počas života môže obsahovať mnoho source SHA a target contexts.

Auditovateľný subject zahŕňa:

```text
MR ID
+ source SHA
+ target SHA alebo merge-base context
+ diff identity
+ merged-result/train candidate SHA
+ policy revision
```

Branch name je mutable pointer. Zelený badge alebo approval bez SHA väzby nie je dostatočný dôkaz.

## 3. Source SHA, diff, candidate a final SHA

- **Source SHA:** aktuálny commit source branchu.
- **Diff:** zmena voči konkrétnemu base/target contextu.
- **Merged-result SHA:** dočasný candidate source + target.
- **Merge-train candidate:** source + target + earlier queued MRs.
- **Final merge SHA:** commit reálne zapísaný do target branchu po zvolenej merge stratégii.

```text
source branch
+ current target
+ queue position
→ tested integration candidate
→ merge strategy
→ final target SHA
```

Branch pipeline a merged-result pipeline môžu mať rozdielny verdict, pretože testujú odlišný subject.

## 4. Review, discussion a approval

### Review

Poznávací proces nad intentom, correctness, security, compatibility, operability, test evidence a recovery.

### Discussion

Záznam otázky alebo rizika. `Resolved` má znamenať známy outcome:

```text
opravené v commite X
| akceptovaný trade-off
| odložené do issue Y s ownerom
| zamietnuté po dohode
```

### Approval

Zaznamenané rozhodnutie eligible identity nad konkrétnym subjectom a riskom.

```text
review bez approval
→ poznanie existuje, policy nemusí byť splnená

approval bez review
→ formálny klik bez silnej evidence
```

Počet approvals nie je automaticky kvalita.

## 5. Approval rule musí chrániť pomenovaný risk

Príklad Atlas policy:

```text
application logic
→ service owner

database migration
→ database owner

CI/deployment definition
→ platform owner

critical security finding
→ security risk decision
```

Rule potrebuje:

- applicability scope;
- eligible approvers;
- required count;
- self/committer restrictions;
- reset a freshness policy;
- fallback a exception lifecycle.

Univerzálne „dve approvals na všetko“ môže byť zároveň slabé pre vysoké riziko a zbytočne drahé pre triviálnu zmenu.

## 6. Code Owners sú path ownership, nie dependency graph

CODEOWNERS môže automaticky priradiť ownerov pre:

- migrations;
- deployment manifests;
- shared CI templates;
- public API/event schemas.

Mechanizmus potrebuje:

```text
correct pattern match
+ eligible owner access
+ enforcement na target branchi
+ fallback pri absencii
+ protection samotného ownership súboru
```

Shared library môže ovplyvniť Payments bez zmeny v `payments/` path-e. Path policy treba kombinovať s dependency a rendered-output evidence tam, kde je to dôležité.

## 7. Approval freshness

Approval je viazaný minimálne na:

```text
reviewed source SHA
+ target context
+ applicable ownership/policy
+ supporting pipeline/security evidence
```

Po novom pushi, rebase alebo významnom target posune sa rozhodnutie môže invalidovať.

Nie každá oprava preklepu vyžaduje celý review od nuly, ale výnimka musí byť explicitná. Tichá persistencia approvalu po zásadnej code zmene je stale evidence.

## 8. Pipeline contexts

### Branch pipeline

Rýchly feedback nad source branchom. Nedokazuje integráciu s aktuálnym targetom.

### Merge-request pipeline

Používa MR context a môže mať odlišné rules a variables.

### Merged-results pipeline

Testuje dočasný merged commit source + target.

### Merge train

Testuje MR za zmenami, ktoré sú pred ním vo fronte.

```text
main + MR-A
→ candidate A

main + MR-A + MR-B
→ candidate B
```

Ak A zlyhá alebo sa zmení, B musí byť prepočítaný.

## 9. Pipeline evidence má viac stavov než green/red

- `passed` — všetky required checks pre správny subject dokončili;
- `failed` — kontrola našla porušenie;
- `running/pending` — evidence ešte nie je úplná;
- `canceled/superseded` — run patrí starému subjectu;
- `skipped/not applicable` — treba dokázať správnu applicability;
- `tool/infrastructure error` — kontrola neprebehla dôveryhodne;
- `incomplete` — chýba shard, child pipeline alebo report.

Tool error a incomplete nie sú pass.

## 10. Mergeability je odvodený verdict

```text
MR nie je draft
+ source/target nemajú conflict
+ required evidence je fresh a complete
+ applicable approvals sú splnené
+ required discussions majú outcome
+ actor smie mergeovať do target branchu
+ integration candidate je aktuálny
→ mergeable
```

MR môže byť approved a stále blocked. Target branch posun môže zmeniť mergeability bez nového source commitu.

## 11. Merge strategy a traceability

### Merge commit

Zachová source commits a explicitný integration commit.

### Fast-forward alebo semi-linear

Udržiava lineárnejšiu mainline, ale často vyžaduje rebase a nové SHA.

### Squash merge

Vytvorí jeden final commit. Source commits sa nemusia dostať do mainline.

Pri squash:

```text
source commits
→ MR review history
→ squash final SHA
→ artifact digest
→ deployment record
```

Stratégia sa vyberá podľa audit, backport, release a recovery požiadaviek, nie iba podľa vzhľadu histórie.

## 12. Worked failure: dve zelené branch pipelines rozbili main

MR-A mení request schema. MR-B súčasne mení serializer. Obe branch pipelines sú zelené proti starému `main`.

```text
MR-A branch pass
MR-B branch pass
→ A sa merge-ne
→ B sa merge-ne bez fresh merged-result candidate
→ serializer očakáva starú schema
→ mainline integration test zlyhá
```

### Príčina

Evidence patrila individuálnym source branches, nie predpokladanému final integration state-u.

### Trvalá náprava

- merged-results pipeline pre relevantné MRs;
- merge train pri vysokej concurrency;
- candidate SHA v gate evidence;
- invalidation po target posune;
- post-merge broken-main recovery.

## 13. Worked failure: approval prežil zásadný push

Database owner schválil migration v `S4`. Jana potom pridala commit `S5`, ktorý zmenil `NOT NULL` timing a backfill behavior.

```text
approval nad S4 zostane viditeľný
→ pipeline nad S5 prejde syntax a unit tests
→ MR sa merge-ne
→ old workers narazia na constraint
```

### Príčina

Approval policy neviazala database approval na current source SHA alebo neinvalidovala relevantnú zmenu.

### Trvalá náprava

- reset approvalu pri source zmene;
- risk-specific owner re-review;
- migration compatibility test;
- audit relation approver → reviewed SHA;
- explicitná policy pre trivial post-approval changes.

## 14. Kauzálny diagnostický walkthrough

Symptom: MR má všetky viditeľné approvals a zelenú pipeline, ale GitLab ho nepovoľuje merge-nuť.

### Krok 1 — stabilizuj subject

```text
MR !142
source SHA S5
target SHA T12
latest candidate C9
final policy revision P7
```

### Krok 2 — formuluj konkurenčné hypotézy

```text
H1: approval patrí starému source SHA
H2: applicable Code Owner rule nie je splnená
H3: pipeline je branch run, nie required merged-result run
H4: required child/shard evidence je incomplete
H5: unresolved alebo outdated discussion stále blokuje
H6: merge-train candidate je invalidovaný target posunom
H7: actor nemá merge capability nad protected targetom
```

### Krok 3 — diskriminačné observation points

- approval timestamps a reviewed SHA testujú H1;
- changed paths, CODEOWNERS match a eligible approvers testujú H2;
- pipeline source/candidate SHA testujú H3;
- expected job/child inventory testuje H4;
- discussion outcomes testujú H5;
- train queue/invalidation reason testuje H6;
- protected branch effective permission testuje H7.

Atlas zistí, že zelená pipeline patrí `S5` branchu, ale required merged-result candidate `C9` bol canceled po target posune. Approvals sú fresh; H3/H6 vysvetľujú blocked verdict.

### Krok 4 — oprav mechanizmus

Vytvorí sa nový candidate nad aktuálnym targetom a znovu sa spustia required checks. Bypass approvalu ani branch protection problém nerieši.

### Krok 5 — over outcome

```text
current candidate pipeline complete
required child reports present
approvals viazané na S5
mergeability = allowed
final SHA mapovaný na MR a artifact
```

### Krok 6 — vráť learning

Finding sa mení na mergeability diagnostický panel, required candidate identity a alert pri stale-green branch evidence.

## 15. Approval exception a break-glass

```text
urgent change
→ konkrétny MR/rule scope
→ risk owner a dôvod
→ minimálne safety checks
→ privileged merge action
→ deployment/runtime evidence
→ dodatočný review
→ doplnenie preskočených controls
→ closure
```

Ak Maintainer bypassuje pravidlá pravidelne, nejde o emergency proces, ale o chybnú policy alebo delivery flow.

## 16. MR nekončí merge kliknutím

```text
requirement/issue
→ MR a reviewed SHA
→ approvals/discussions
→ integration candidate evidence
→ final SHA
→ artifact digest
→ deployment/release record
→ runtime validation
```

Pri squash, rebase a merge train modeli musí provenance explicitne mapovať meniace sa commit identities.

## 17. Diagnostický runbook

1. Urči current source, target, candidate a policy revision.
2. Rozlíš branch, MR, merged-result a train pipeline.
3. Over expected required job/child/report inventory.
4. Skontroluj approval freshness a reviewed SHA.
5. Vyhodnoť applicable Code Owner a approval rules.
6. Over discussion outcomes a conflicts.
7. Skontroluj train position a invalidation reason.
8. Over protected-target merge capability aktora.
9. Po oprave potvrď final SHA a artifact provenance.
10. Zmeň finding na freshness, policy alebo integration-race control.

## 18. Referenčné pravidlá

- MR ID nie je identity reviewovaného obsahu.
- Review, discussion a approval sú odlišné vrstvy.
- Každá approval rule chráni pomenovaný risk.
- Approvals a pipelines potrebujú freshness policy.
- Branch pipeline nie je merge-result evidence.
- `Approved` nie je synonymum `mergeable`.
- Tool error a incomplete evidence nie sú pass.
- Merge train rieši queue integration race, nie slabý review.
- Merge strategy musí zachovať post-merge traceability.
- Bypass potrebuje uzavretý exception lifecycle.

## 19. Časté omyly

### „Má dve approvals, teda je bezpečný“

Bez definovaného risku, eligibility a freshness ide iba o počet kliknutí.

### „Pipeline je zelená“

Treba vedieť, ktorý SHA a context testovala.

### „Code Owner je v súbore, approval sa určite vyžaduje“

Potrebný je match, eligible owner a enforcement na target branchi.

### „Resolved znamená vyriešené“

Thread musí mať explicitný outcome.

### „Merge train zabráni každému incidentu“

Rieši interakcie queued changes, nie chýbajúci test alebo nesprávnu migration.

## 20. Zhrnutie

Dôveryhodný GitLab MR lifecycle je:

```text
immutable source/target subject
→ risk-specific review a ownership
→ fresh candidate evidence
→ complete mergeability policy
→ serialized integration decision
→ final SHA
→ artifact a runtime provenance
```

Troubleshooting sa nesmie zastaviť pri ikonách `approved` a `passed`. Musí vysvetliť, či tieto evidence patria current subjectu, či sú úplné a ktorá konkrétna policy vrstva ešte blokuje alebo povoľuje merge.

## Kontrolné otázky

1. Prečo MR číslo nie je decision subject?
2. Ako sa líšia source SHA, merged-result SHA a final SHA?
3. Prečo review a approval nie sú synonymá?
4. Čo musí chrániť approval rule?
5. Ako vzniká stale approval?
6. Kedy Code Owner approval skutočne platí?
7. Prečo branch pipeline nestačí na integration decision?
8. Aký race rieši merge train?
9. Prečo approved MR nemusí byť mergeable?
10. Ako sa final artifact mapuje späť na reviewovaný obsah?

## Oficiálna dokumentácia

- [Merge request approvals](https://docs.gitlab.com/user/project/merge_requests/approvals/)
- [Merge request reviews](https://docs.gitlab.com/user/project/merge_requests/reviews/)
- [Merged results pipelines](https://docs.gitlab.com/ci/pipelines/merged_results_pipelines/)
- [Merge trains](https://docs.gitlab.com/ci/pipelines/merge_trains/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Projects, groups a permissions](projects-groups-permissions.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Protected branches a environments →](protected-branches-and-environments.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
