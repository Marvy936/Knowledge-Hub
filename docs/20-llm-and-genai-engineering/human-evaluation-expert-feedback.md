# Human evaluation a expert feedback

Human evaluation je riadený measurement proces, v ktorom presne definovaní ľudia hodnotia exact model/application outputs podľa rubric, authority a task contextu. Nie je to neformálne „pozreli sme si odpovede“, thumbs-up widget ani automatický predpoklad, že väčšina annotators predstavuje správny verdict. Pri LLM systémoch sa musí odlíšiť domain correctness, user preference, policy compliance, safety, language quality a business outcome, pretože tieto dimensions môžu vyžadovať odlišné skupiny ľudí.

V incidente `GENAI-SUPPORT-07` eval pipeline zlúčila labels od všeobecných crowd workers, support agentov a jedného policy experta do jediného priemerného `quality_score`. Crowd workers preferovali zdvorilú a rozhodnú odpoveď, support agents kratší handling time a expert správnu interpretáciu výnimky. Candidate získal vysoké skóre, hoci pri zriedkavej refund exception odporúčal nepovolený postup. Disagreement bolo nesprávne označené ako annotation noise a odstránené majority vote. Root cause bol chýbajúci authority model: preference annotator prehlasoval domain experta v otázke, na ktorú nemal kompetenciu.

## 1. Human-evaluation subject

Evaluation subject zahŕňa dataset, release, rendered output, evidence context, task, rubric, annotator cohort, assignment, interface generation a adjudication policy. Bez tejto identity sa nedá vysvetliť, prečo sa judgments líšia.

```yaml
human_eval:
  study_id: support-refund-human-v8
  dataset: support-refund-eval-v12
  release_candidate: support-assistant-2026.08.04.4
  baseline: support-assistant-2026.07.28.2
  task_version: refund-review-v6
  rubric_version: refund-rubric-v9
  interface_version: review-ui-v5
  cohorts:
    policy_correctness: certified-policy-experts-2026Q3
    workflow_usability: trained-support-agents-2026Q3
    clarity_preference: target-user-panel-sk-v4
  adjudication: expert-panel-v3
```

Human verdict sa viaže na exact output a evidence. Ak reviewer hodnotí iba final text bez retrieved policy alebo tool trace, nemôže spoľahlivo rozhodnúť faithfulness či safe execution.

## 2. Evaluation question

Každá study začína konkrétnou otázkou. Môže ísť o absolute quality, pairwise preference, error identification, safety review, domain correctness alebo task success.

„Ktorá odpoveď je lepšia?“ je neúplné, ak rubric neurčuje, či sa optimalizuje factuality, clarity, tone alebo actionability. Dve odpovede môžu byť správne v odlišných dimensions a aggregate preference zakryje kritickú chybu.

## 3. Human roles

Human evaluation oddeľuje annotator, reviewer, domain expert, adjudicator, study designer, quality auditor a affected user. Jedna osoba môže zastávať viac rolí, ale kompetencie a conflicts of interest sa dokumentujú.

```text
annotator
→ vytvára prvotný judgment

adjudicator
→ rieši definované disagreementy

domain authority
→ rozhoduje odborný alebo policy fact

study owner
→ definuje estimand, sampling a report
```

Model developer by nemal byť jediným evaluatorom vlastného candidate, pretože pozná hypothesis a môže nevedome interpretovať ambiguous outputs priaznivo.

## 4. Authority matrix

Nie všetky judgments majú rovnakú authority. Domain expert má vyššiu authority pri legal alebo policy correctness, ale target user môže byť authoritative pri zrozumiteľnosti a usability.

| Dimension | Primárna authority | Dôvod |
|---|---|---|
| policy correctness | certifikovaný policy expert | pozná authoritative rules a exceptions |
| tool-action safety | system owner a security reviewer | rozumie execution a authorization contractu |
| workflow usefulness | trained support agent | pozná reálny handling proces |
| clarity a tone | reprezentatívny user panel | reprezentuje používateľské vnímanie |
| schema validity | deterministic validator | človek nie je potrebný pre syntaktický invariant |

Authority matrix zabraňuje majority vote naprieč neporovnateľnými rolami. Disagreement medzi user preference a expert correctness sa reportuje ako trade-off, nie ako noise.

## 5. Annotator selection

Annotators sa vyberajú podľa tasku, jazyka, domain knowledge a target population. Convenience sample interných developerov môže byť rýchly, ale nereprezentuje zákazníkov ani odbornú authority.

Selection metadata zahŕňa recruitment source, qualifications, language proficiency, training a exclusion criteria. Pri citlivých tasks sa preveruje confidentiality a conflict of interest.

## 6. Representativeness

Panel má reprezentovať population relevantnú pre estimand. Multilingual product potrebuje native alebo dostatočne kvalifikovaných reviewers pre každý language segment; preklad všetkých cases do angličtiny môže odstrániť skutočné jazykové failures.

Demographic representation môže byť dôležitá pri tone, harm alebo accessibility. Nie je univerzálne potrebná pre každý deterministic domain task, ale rozhodnutie a obmedzenia sa dokumentujú.

## 7. Expertise levels

Expertise sa definuje operacionálne, napríklad certifikácia, roky praxe, successful qualification set alebo role v procese. Label `expert` bez kritérií je slabá metadata.

Junior a senior experts môžu mať odlišné agreement patterns. Study môže použiť tiered workflow: trained annotator hodnotí bežné cases a senior adjudicator rieši high-risk alebo ambiguous cases.

## 8. Training annotators

Annotator training vysvetľuje task, rubric, authority sources, examples, edge cases, UI a escalation path. Po trainingu nasleduje qualification set so known judgments.

```text
rubric onboarding
→ worked examples
→ independent practice
→ feedback
→ qualification threshold
→ production annotation
```

Qualification score nepreukazuje permanentnú kvalitu. Ongoing hidden gold cases a drift monitoring overujú, či annotator rubric stále používa konzistentne.

## 9. Rubric design

Rubric rozkladá quality na explicitné dimensions s definíciou, scale anchors, examples a forbidden states. Každý label musí mať rozhodovaciu hranicu, nie iba intuitívny názov.

```yaml
rubric_dimension:
  name: policy_correctness
  labels:
    correct:
      definition: "Všetky rozhodujúce tvrdenia a navrhnutý postup zodpovedajú poskytnutej policy."
    incorrect:
      definition: "Aspoň jedno rozhodujúce tvrdenie alebo postup odporuje policy."
    insufficient_evidence:
      definition: "Poskytnutý evidence context nestačí na rozhodnutie."
  hard_failure:
    - "Navrhne refund pri povinnej expert escalation."
```

Rubric má viacvetové guidance pre ambiguous prípady. Ak sa annotators opakovane pýtajú tú istú otázku, ide o rubric defect alebo missing authority, nie automaticky o ich chybu.

## 10. Scale design

Categorical labels sú vhodné pre correctness alebo policy compliance. Ordinal scales zachytávajú úroveň helpfulness či severity. Continuous slider môže pôsobiť presne, ale ľudia často nepoužívajú scale lineárne.

Scale anchors majú konkrétne examples. Päťbodové hodnotenie bez rozdielu medzi 3 a 4 vytvára pseudo-precision. Pri high-risk decision sa preferuje explicitný pass/fail plus reason codes pred priemerom hviezdičiek.

## 11. Absolute rating

Absolute evaluation hodnotí jednu odpoveď podľa rubric. Umožňuje porovnať output s minimálnym contractom a identifikovať, že obidve porovnávané odpovede sú zlé.

Nevýhodou je rozdielna kalibrácia annotators. Training, anchored scales, overlap a adjudication znižujú variation. Absolute score sa nesmie porovnávať medzi studies s odlišnou rubric alebo panelom bez linking designu.

## 12. Pairwise preference

Pairwise evaluation ukazuje dve anonymizované odpovede a pýta sa, ktorá lepšie spĺňa criterion. Pre ľudí môže byť jednoduchšia než absolute scale, ale je citlivá na position, length a presentation bias.

Order sa randomizuje a podporuje sa `tie` alebo `both fail`, ak task umožňuje. Forced choice môže označiť jednu chybnú odpoveď za víťaza a vytvoriť falošný training signal.

## 13. Ranking

Ranking viacerých outputs môže byť efektívny pri model selection, ale cognitive load rastie s počtom kandidátov a dĺžkou textu. Reviewer môže hodnotiť relatívny štýl namiesto hard correctness.

Balanced incomplete block design rozdelí pair comparisons tak, aby sa každý candidate stretol s porovnateľným mixom protivníkov. Ranking model a uncertainty sa reportujú spolu s raw pair counts.

## 14. Error annotation

Error annotation žiada reviewerov označiť konkrétne chyby, claims, spans alebo violated rules. Je diagnostickejšia než jediný score a umožňuje vytvoriť regression cases.

```json
{
  "case_id": "REF-009481",
  "errors": [
    {
      "type": "policy_exception_ignored",
      "severity": "critical",
      "span": "Refund can be approved immediately",
      "evidence": "policy-4.2-b"
    }
  ]
}
```

Error taxonomy sa versionuje. Príliš široká taxonomy vedie k misc labels; príliš detailná znižuje agreement a potrebuje viac trainingu.

## 15. Rationale a evidence

Reviewer môže uviesť stručný reason code, evidence ID alebo rationale. Rationale pomáha adjudication a grader calibration, ale zvyšuje čas a môže obsahovať citlivé údaje.

Rationale nie je raw private chain-of-thought requirement. Stačí decision-relevant explanation, napríklad violated rule a evidence reference. UI nemá nútiť ľudí písať špekulatívny vnútorný monológ.

## 16. Blindness

Reviewer by spravidla nemal vedieť, ktorý output je baseline, candidate alebo od ktorého providera pochádza. Brand a expectation bias môžu meniť judgment.

Úplná blindness nie je vždy možná, ak modely majú rozpoznateľný štýl alebo task vyžaduje runtime metadata. Study report uvádza, ktoré identity boli skryté a aké bias zostávajú.

## 17. Randomization

Case order, response order a assignment sa randomizujú alebo blockujú podľa segmentu. Bez randomization môže fatigue alebo learning efekt systematicky znevýhodniť neskorší candidate.

Random seed a assignment manifest sa ukladajú. Reproducibility neznamená, že každý reviewer dostane všetko; znamená, že allocation a overlap sú vysvetliteľné.

## 18. Overlap

Časť cases hodnotí viac annotators, aby bolo možné merať agreement a kvalitu. Overlap rate závisí od risku, budgetu a očakávanej subjektivity.

High-risk alebo rubric-new cases môžu mať 100 % double review. Bežné low-risk cases môžu mať sample overlap, pričom disagreement triggeruje adjudication alebo zvýšenie coverage.

## 19. Inter-annotator agreement

Agreement metric sa volí podľa label type, počtu annotators, missing labels a prevalence. Percent agreement je jednoduchý, ale neodpočítava agreement náhodou. Cohenovo kappa, Fleissovo kappa alebo Krippendorffovo alpha majú rozdielne predpoklady.

Samotné číslo agreementu nestačí. Pri imbalanced labels môže byť kappa nízka napriek vysokému percent agreementu. Report preto ukazuje confusion/disagreement matrix, prevalence a confidence interval.

## 20. Disagreement analysis

Disagreement môže znamenať subjektívny task, nejasnú rubric, missing evidence, annotator error alebo reálnu plurality preferences. Cieľom nie je automaticky ho vymazať.

```text
disagreement
→ skontroluj authority a evidence
→ klasifikuj rubric versus case ambiguity
→ adjudikuj high-risk verdict
→ oprav rubric alebo case, ak treba
→ zachovaj disagreement metadata
```

Cases s legitímnou pluralitou môžu uchovávať distribution judgments namiesto jedného gold labelu.

## 21. Adjudication

Adjudication je definovaný proces riešenia disagreementu. Adjudicator vidí pôvodné labels, evidence a reason codes a aplikuje authority hierarchy.

Adjudicated label nie je jednoduchý majority vote. Pri policy correctness môže jeden kvalifikovaný expert prehlasovať troch preference reviewers, ale decision a rationale sa zaznamenajú. Ak ani expert nemá dostatok evidence, správny verdict môže byť `insufficient_evidence` a case sa vráti study ownerovi.

## 22. Gold a silver labels

Gold label typicky prešiel expert review alebo adjudication podľa definovaného processu. Silver label môže pochádzať z majority, model assistance alebo operational proxy a má nižšiu authority.

Tieto label classes sa nesmú miešať bez metadata. Training alebo eval môže používať silver data, ale reportuje sensitivity a nekvalifikuje ich automaticky ako ground truth.

## 23. Hidden quality cases

Production annotation batch môže obsahovať hidden known cases na monitoring annotator quality. Gold cases sa pravidelne obnovujú, aby sa predišlo memorization a leakage.

Quality threshold spúšťa retraining, review alebo exclusion. Automatické penalizovanie jedného disagreementu bez adjudication môže byť nespravodlivé, najmä pri ambiguous rubric.

## 24. Annotator drift

Judgment sa môže časom meniť po novej policy, fatigue alebo neformálnom prispôsobení tímu. Drift monitoring sleduje hidden-gold accuracy, label distribution, disagreement a time-per-case.

Pri zmene rubric alebo policy sa vytvára nová task generation a annotators sa znovu trénujú. Staré a nové judgments sa neporovnávajú ako rovnaká scale bez bridge setu.

## 25. Fatigue a workload

Dlhé contexts a multimodal cases zvyšujú cognitive load. Study definuje maximum session length, breaks, case complexity a expected time.

Extrémne krátky time-per-case môže signalizovať low effort, ale nie je sám osebe dôkaz. Expert môže rýchlo rozpoznať známu chybu; quality review kombinuje čas s judgment patternom a hidden cases.

## 26. Interface design

Evaluation UI zobrazuje presne tie informácie, ktoré reviewer potrebuje, a oddeľuje authoritative evidence od candidate textu. Truncation, scroll position, collapsed citations alebo rozdielne formatting môžu biasovať verdict.

Interface generation sa versionuje a testuje. Ak UI odstrihne exception clause, nejde o annotator error ani model failure, ale o measurement pipeline defect.

## 27. Model-assisted review

Model môže predvyplniť error candidates, sumarizovať evidence alebo upozorniť na rubric rule. Human reviewer však musí vedieť, čo generoval model, a nesmie iba potvrdiť jeho návrh bez nezávislého posúdenia.

Automation bias sa meria kontrolnou skupinou alebo randomized assistance. Model-assisted labels sa označujú a kalibrujú proti unassisted expert judgments.

## 28. Expert feedback loop

Expert feedback môže slúžiť na eval, prompt improvement, dataset correction alebo training. Každý downstream use má odlišný consent, leakage a governance contract.

```text
expert judgment
→ eval verdict
→ RCA taxonomy
→ approved regression case
→ optional training candidate
```

Nie každý disagreement sa automaticky pridá do training data. Najprv sa určí, či problém patrí do promptu, retrievalu, tool policy, model behavior alebo measurement rubric.

## 29. Preference data

Pairwise human preferences môžu vytvoriť DPO/RLHF data, ale preference nie je absolútna correctness. Dataset musí zachovať criterion, annotator cohort, confidence, both-fail možnosť a authority.

Style preference od crowd panelu nesmie prepísať expert safety label. Multi-objective training a eval oddelia helpfulness, harmlessness, correctness a product tone.

## 30. User feedback

Thumbs-up, complaint, edit alebo conversation abandonment sú behavior signals, nie čisté labels. Sú ovplyvnené user motivation, exposure, UI a selective reporting.

User feedback sa spája s request/release identity a segmentuje. Negatívna spätná väzba môže byť silný incident trigger, ale absencia feedbacku nepreukazuje spokojnosť ani correctness.

## 31. Operational expert review

V production môže expert auditovať sample reálnych cases. Sampling zahŕňa random traffic, high-risk routes, model uncertainty, incidents a complaints.

Audit verdict sa viaže na business outcome a loaded release. Reviewer musí rozlíšiť model error od agent workflow, retrieval, stale policy alebo human override failure.

## 32. Compensation a ethics

Annotators majú primeranú kompenzáciu, realistické time estimates a transparentné task conditions. Harmful alebo citlivý content vyžaduje wellbeing controls, opt-out a support.

Study dokumentuje data handling, consent a worker privacy. Detailná telemetry nemá slúžiť na invazívne sledovanie ľudí bez legitímneho účelu.

## 33. Privacy a confidentiality

Cases sa minimalizujú a redigujú. Annotators dostávajú iba data potrebné pre task a používajú controlled environment pri citlivých údajoch.

Export, screenshot a copy permissions sa riadia classification. Rationale môže obsahovať nové osobné údaje, preto sa filtruje a retencia sa definuje samostatne.

## 34. Study preregistration

Pred zberom sa fixujú primary metrics, thresholds, sampling, exclusion rules a analysis plan. To znižuje cherry-picking a opakované prepočítavanie scale, kým candidate nevyhrá.

Exploratory findings sú legitímne, ale označia sa ako exploratory a overia na fresh sample. Post-hoc rubric zmena nevytvára validný confirmatory verdict na rovnakých labels bez re-annotation.

## 35. Statistical analysis

Human results uvádzajú sample size, overlap, uncertainty a paired structure. Pairwise wins sa analyzujú per case a annotator, nie ako nezávislé observations, ak ten istý reviewer hodnotil veľa cases.

Praktická významnosť je rovnako dôležitá ako statistical significance. Malý preference gain nemusí ospravedlniť vyšší cost alebo safety regression.

## 36. Segment reporting

Human verdict sa reportuje podľa language, risk, task, annotator cohort a case source. Aggregate score môže zakryť, že target users preferujú candidate, ale experts nachádzajú viac correctness failures.

Dashboard ukazuje disagreement a authority-specific metrics vedľa summary. Jeden blended score je vhodný nanajvýš ako navigačný signál, nie ako jediný promotion gate.

## 37. Human-model grader calibration

Expert-adjudicated set slúži na kalibráciu model graders. Porovnáva sa precision/recall, confusion matrix, score calibration a failure taxonomy.

Keď model grader a expert nesúhlasia, nepredpokladá sa automaticky, že expert je vždy správny. Case sa preskúma na missing evidence, rubric ambiguity a expert error; výsledok aktualizuje calibration set novou generation.

## 38. Promotion decision

Human evaluation je jedna vrstva evidence. Promotion kombinuje deterministic gates, model graders, expert verdicts, operational metrics a risk policy.

```yaml
promotion_decision:
  candidate: support-assistant-2026.08.04.4
  deterministic_gates: passed
  model_grader_bundle: passed
  expert_policy_review: failed
  user_clarity_preference: +4.2%
  verdict: rejected
  reason: critical policy-exception regression
```

Vyššia preference nemôže kompenzovať hard expert correctness failure, ak product contract označuje tento dimension ako forbidden regression.

## 39. Observability a lineage

Každý judgment má case ID, output ID, annotator pseudonymous ID, cohort, task/rubric/UI version, timestamp, duration, label, reason code a adjudication history. Identity access je obmedzený podľa privacy policy.

Lineage spája judgment s eval runom, candidate release, promotion decision a prípadným regression/training artifactom. Manuálny spreadsheet export bez versioning a immutable row IDs oslabuje audit.

## 40. Failure hypotheses

Pri nízkom agreemente sa skúma rubric ambiguity, chýbajúce evidence, nesprávna cohort authority, UI truncation, language mismatch, annotator drift, fatigue alebo skutočne subjective task. Pri neočakávanom candidate win sa skúma order/length bias, unblinding, sample mix a majority vote naprieč roles.

Ak policy experts systematicky nesúhlasia s crowd panelom iba na exceptions, pravdepodobný je authority conflict, nie random noise. Ak všetky cohorts zmenia score po UI release, treba overiť presentation a data, nie okamžite pripísať zmenu modelu.

## 41. Containment

Containment zastaví promotion a zmrazí assignments, judgments, rubric, UI a output artifacts. Chybné labels sa neprepisujú na mieste; study sa označí ako under investigation alebo invalid.

Pri privacy incidente sa zruší access, identifikujú exports a auditujú annotator sessions. Odstránenie UI bez zachovania version metadata môže sťažiť pochopenie, čo reviewers skutočne videli.

## 42. Recovery

Recovery opraví rubric, UI, sampling alebo cohort assignment novou study generation. Annotators prejdú retrainingom a affected cases sa znovu hodnotia bez ukázania starého consensus, ak by to biasovalo judgment.

Druhá operácia používa fresh cases a odlišný segment. Úspešná re-annotation iba pôvodných disagreements môže overfitnúť process na známe edge cases.

## 43. Acceptance

Pozitívna acceptance vyžaduje explicitnú evaluation question, authority matrix, kvalifikované a reprezentatívne cohorts, versioned rubric/UI, training a qualification, overlap, agreement a disagreement analysis, adjudication, privacy/ethics controls, uncertainty, segment reporting a release lineage.

Recovery acceptance vyžaduje zachované failing judgments, identifikovaný measurement defect, novú immutable study generation, requalification, re-annotation, adjudication a fresh second-sample validation.

Forbidden acceptance je majority vote naprieč neporovnateľnými kompetenciami, thumbs-up ako ground truth, nezdokumentovaní „experti“, forced pairwise choice bez both-fail, agreement číslo bez prevalence a confusion analysis, alebo human approval viazaný iba na prompt/model name namiesto exact output release.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: LLM evaluation datasets a graders](llm-evaluation-datasets-graders.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->