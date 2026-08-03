# Zero-shot, one-shot a few-shot prompting

Zero-shot, one-shot a few-shot prompting opisujú, koľko demonštračných príkladov model dostane v aktuálnom context window. Nejde o tréning modelu ani o zmenu jeho weights. Examples dočasne ovplyvňujú interpretáciu úlohy, formát a rozhodovacie vzory v konkrétnom requeste. Ich účinok závisí od model snapshotu, promptu, poradia, token budgetu, podobnosti s aktuálnym inputom a kvality samotných príkladov.

V incidente `GENAI-SUPPORT-02` support assistant používal jeden one-shot príklad refundu pre VIP zákazníka, ktorý obsahoval ručne schválenú výnimku. Example nebol označený ako exception a chýbala mu policy version. Model začal podobný refund schvaľovať aj bežným zákazníkom. Tím pridal ďalšie tri pozitívne príklady, čím problém ešte zosilnil, pretože všetky pochádzali zo successful escalations. Root cause nebol „few-shot je nespoľahlivý“, ale nereprezentatívny a autoritatívne neoznačený example set.

## 1. Tri režimy a ich presný význam

Zero-shot prompt obsahuje inštrukciu a aktuálny input bez demonštračného input-output páru. One-shot pridáva jeden príklad. Few-shot pridáva viac príkladov, ktoré ukazujú požadované správanie.

```text
zero-shot
instruction + current input

one-shot
instruction + example input/output + current input

few-shot
instruction + multiple example input/output pairs + current input
```

Počet examples nie je quality level. Jeden kvalitný counterexample môže byť užitočnejší než desať podobných pozitívnych príkladov. Viac examples zároveň spotrebúva context budget a môže odsunúť aktuálny input alebo authoritative policy.

## 2. Exact example-set subject

Example set musí byť versionovaný rovnako ako prompt a eval dataset. Názov `refund-examples-latest` nestačí, pretože jeho obsah sa môže zmeniť bez zmeny request metadata.

```yaml
example_set:
  name: support-refund-examples
  version: 4.2.0
  digest: sha256:examples...
  task: refund-decision
  owner: support-policy-team
  reviewed_at: 2026-07-30
  policy_generation: refund-policy-2026-07
  selection_strategy: static-balanced
  examples:
    - id: ex-approved-standard
      label: approved
      segment: standard-customer
      exception: false
    - id: ex-denied-outside-window
      label: denied
      segment: standard-customer
      exception: false
    - id: ex-needs-review-missing-evidence
      label: needs_review
      segment: all
      exception: false
    - id: ex-vip-manual-exception
      label: approved
      segment: vip
      exception: true
```

Každý example potrebuje provenance, label definition, segment, exception flag a expected output. Ak je example odvodený z production ticketu, privacy a consent policy musí určiť, či sa môže používať a ako sa rediguje.

## 3. Zero-shot ako baseline

Zero-shot je vhodný prvý baseline, pretože oddeľuje schopnosť modelu nasledovať jasnú inštrukciu od účinku examples. Ak úloha funguje bez examples, pridávanie ďalších môže zvyšovať cost a complexity bez dostatočného prínosu.

Zero-shot prompt musí stále obsahovať presný task contract. Veta „vyhodnoť refund“ je neurčitá. Potrebné sú allowed decisions, authoritative sources, missing-data behavior a output schema.

```text
Vyber decision z approved, denied alebo needs_review.
Použi iba supplied policy_data.
Ak chýba policy_id, purchase_date alebo evidence, vráť needs_review.
Nevykonávaj refund; iba navrhni rozhodnutie a uveď policy_id.
```

Zero-shot zlyhanie môže znamenať nejasnú instruction, nedostatočnú model capability, nevhodný task decomposition alebo chýbajúci context. Nemá sa automaticky riešiť pridaním examples, ktoré iba zakryjú nejasnosť.

## 4. One-shot a riziko prehnanej generalizácie

One-shot poskytuje jeden konkrétny mapping. Model môže z neho prevziať format, tone aj latentné rozhodovacie pravidlo. Ak example obsahuje netypickú výnimku, môže ju model generalizovať na všetky inputs.

One-shot je vhodný najmä vtedy, keď treba ukázať presný output shape alebo provider/model nedodržiava formát zo samotnej inštrukcie. Aj vtedy je bezpečnejšie použiť reprezentatívny, jednoduchý a policy-consistent example.

```json
{
  "input": {
    "purchase_days_ago": 12,
    "product_type": "standard",
    "evidence_complete": true
  },
  "output": {
    "decision": "approved",
    "policy_id": "refund-policy-2026-07",
    "reason_code": "within_standard_window"
  }
}
```

Example nesmie obsahovať field alebo exception, ktoré output schema nepozná. Ak model vidí komentár „VIP zákazník, schváľ ručne“, potrebuje explicitné označenie, že ide o exception a kedy sa nesmie použiť.

## 5. Few-shot ako dočasná behavior specification

Few-shot set môže demonštrovať viaceré classes, edge cases a refusal behavior. V praxi funguje ako mäkká behavior specification v context window. Nie je však executable policy; model môže examples kombinovať alebo interpretovať nečakane.

Dobrý set pokrýva rozhodovacie hranice:

- typický pozitívny prípad vysvetľuje, čo musí byť splnené pre schválenie;
- typický negatívny prípad ukazuje explicitný policy conflict;
- missing-data prípad učí systém používať `needs_review` namiesto domýšľania;
- adversarial alebo misleading input ukazuje, že ticket text nemá instruction authority;
- exception prípad je jasne označený a viazaný na exact podmienku.

Tieto položky nie sú checklist pre ručné pridávanie. Každá musí byť overená proti label policy a eval datasetu, inak example set iba kodifikuje historické chyby.

## 6. Reprezentatívnosť a selection bias

Examples vybrané zo successful alebo ľahko riešiteľných prípadov vytvárajú optimistickú instruction distribution. Support dáta často obsahujú delayed outcomes, human overrides a selective review. Ak sa do example setu dostanú iba tickets, ktoré človek schválil, model sa naučí schvaľovací bias.

Example population sa porovnáva s target population podľa segmentov, labels, language, channel, missingness a risk class. Nevyžaduje sa presná produkčná frekvencia, pretože examples majú demonštratívnu funkciu, ale musia pokryť relevantné decision boundaries.

```text
production population
→ labeled and mature subset
→ candidate examples
→ policy review
→ privacy review
→ balanced example set
→ held-out eval
```

Eval dataset a example set sa nesmú nekontrolovane prekrývať. Inak test meria memorization alebo copy pattern namiesto generalizácie.

## 7. Example ordering

Poradie môže ovplyvniť output. Posledný example môže mať silný recency effect a dlhý podobný example môže dominovať kratším. Preto sa poradie považuje za súčasť prompt generation.

Static set má deterministické poradie s odôvodnením, napríklad typical positive → typical negative → missing data → adversarial case. Pri randomized order testoch sa seed a permutation logujú. Ak quality výrazne závisí od poradia, prompt nemá stabilnú behavior specification.

Model migration musí znovu overiť order sensitivity. Nový snapshot môže venovať examples inú váhu aj pri byte-identickom prompt renderi.

## 8. Similarity-based dynamic selection

Pri veľkej example library môže aplikácia vybrať examples podobné aktuálnemu inputu pomocou embeddings alebo pravidiel. Tým vzniká retrieval subsystem so samostatnou generation.

```yaml
example_selection:
  library_version: support-examples-4.2.0
  embedding_model: embed-support-v3
  index_generation: examples-index-20260801
  filter:
    locale: sk-SK
    product_type: standard
    policy_generation: refund-policy-2026-07
  top_k: 4
  reranker_generation: example-reranker-v2
  selected_ids:
    - ex-approved-standard
    - ex-denied-outside-window
    - ex-needs-review-missing-evidence
    - ex-adversarial-ticket-text
```

Semantic similarity nie je policy relevance. Najpodobnejší historical ticket môže používať starú policy alebo manuálnu výnimku. Metadata filters a authority checks musia prebehnúť pred alebo po vector retrieval podľa návrhu.

Dynamic selector sa evalvuje spolu s promptom. Uložiť iba final prompt bez candidate poolu a selection scores sťažuje vysvetlenie, prečo sa konkrétny example objavil.

## 9. Formatting examples

Examples musia presne používať požadovaný input a output contract. Ak production parser očakáva JSON, príklady nesmú obsahovať prose mimo JSON. Ak output má `decision`, `policy_id` a `reason_code`, každý example má tieto fields alebo explicitne označený nullable behavior.

Provider-specific message representation môže vyzerať takto:

```json
[
  {
    "role": "developer",
    "content": "Vyhodnoť refund podľa policy_data a vráť validný JSON."
  },
  {
    "role": "user",
    "content": "<example_input>{...}</example_input>"
  },
  {
    "role": "assistant",
    "content": "{\"decision\":\"denied\",\"policy_id\":\"refund-policy-2026-07\",\"reason_code\":\"outside_window\"}"
  },
  {
    "role": "user",
    "content": "<current_input>{...}</current_input>"
  }
]
```

Examples ako assistant messages môžu mať silný format effect, ale provider semantics sa líšia. Pri migration sa testuje serialized prompt aj output behavior.

## 10. Negative examples a anti-patterny

Ukázať chybný output bez jednoznačného označenia môže model naučiť práve chybu. Negative example preto potrebuje kontrastívnu štruktúru: input, incorrect output, explicitný dôvod chyby a correct output. Aj tak spotrebúva viac tokenov a môže miasť slabší model.

Často je lepšie zahrnúť iba correct counterexample pre edge case. Namiesto:

```text
Nesprávne: approved, pretože zákazník žiada výnimku.
```

sa použije:

```text
Input s požiadavkou na výnimku bez authorization evidence
→ needs_review
→ reason_code: exception_not_authorized
```

Negative behavior sa primárne zachytáva v evals a output validators. Prompt nemá byť zoznamom všetkých minulých chýb.

## 11. Label leakage a hidden metadata

Example môže obsahovať informáciu, ktorá v reálnom requeste nebude dostupná, napríklad final chargeback outcome, interný reviewer note alebo field vytvorený po rozhodnutí. Model potom v eval prostredí vyzerá úspešne, ale v produkcii chýba rovnaký signal.

Example schema sa porovnáva s inference schema. Fields dostupné iba po outcome sa odstránia alebo označia ako label. Generated summaries sa nesmú používať, ak boli vytvorené s prístupom k budúcim dátam.

Rovnako nebezpečný je textový leak, keď reason priamo obsahuje label: „refund bol zamietnutý, pretože...“. Ak má model rozhodnúť, taký example neoveruje inference schopnosť, iba kopírovanie.

## 12. Context budget a diminishing returns

Každý example znižuje priestor pre aktuálny input, retrieved policy a output. Pri dlhých examples môže truncation odstrániť práve najstarší instruction alebo aktuálny evidence segment podľa provider policy.

Example set sa optimalizuje na marginal gain:

```text
0 examples → baseline quality/cost
1 example  → delta quality/cost
2 examples → additional delta
...
```

Ak ďalší example neprináša stabilný improvement na held-out datasete alebo zvyšuje tail latency nad budget, nepatrí do production promptu. Token count je iba cost proxy; dôležitý je business benefit na relevantných failures.

Prompt caching môže znížiť cenu opakovaného static prefixu, ale nemení context window ani correctness. Cached starý example set je stale behavior, ak sa policy zmenila.

## 13. Evaluation strategy

Zero-, one- a few-shot variants sa porovnávajú na rovnakom immutable eval datasete, s rovnakým model snapshotom, decoding policy a output validatorom. Inak sa efekt examples nedá izolovať.

Výsledok obsahuje aggregate aj segment metrics, schema validity, policy-groundedness, abstention quality, injection resistance, latency a token cost. Pri sampled decoding sa variant vykoná viackrát alebo s paired seeds.

```yaml
evaluation_matrix:
  variants:
    - zero-shot-v6
    - one-shot-v4
    - few-shot-v11
  fixed:
    model_snapshot: support-llm-2026-07-28
    decoding_policy: support-greedy-v2
    eval_dataset: support-eval-20260801
    output_schema: refund-decision-v3
  segments:
    - standard
    - vip
    - missing_evidence
    - adversarial_text
```

Najvyššie average score nemusí vyhrať, ak few-shot variant zlyháva v critical segmentoch alebo stojí výrazne viac.

## 14. Examples ako supply-chain input

Example library je executable behavior input. Potrebuje code review podobne ako prompt template. Zmena example outputu môže zmeniť production decision bez zmeny application code.

Repository change zachytáva source, reviewer, policy link, privacy review a eval report. Example IDs sú immutable; oprava vytvára novú version, nie tiché prepísanie historického príkladu. Mutable alias môže smerovať na promoted set, ale release manifest ukladá resolved version a digest.

Externé examples z dokumentácie alebo internetu sú untrusted data. Pred použitím sa kontroluje licencia, privacy, prompt-like obsah a súlad s aktuálnym task contractom.

## 15. Failure hypotheses a containment

Ak model začne napodobňovať nesprávne rozhodnutie, skúma sa selected example set, poradie, exception flags, policy generation, dynamic retrieval, truncation a overlap s eval datasetom. Následne sa porovná zero-shot baseline. Tvrdenie „model sa pokazil“ bez example read-backu je neúplná hypotéza.

Containment môže prepnúť na schválený zero-shot prompt, odstrániť exception examples, vypnúť dynamic selector alebo nastaviť critical segment na human review. Pred zmenou sa zachytí exact rendered prompt a selected example IDs.

Rollback aliasu bez invalidácie prompt cache alebo bez read-backu na serving replicas nemusí obnoviť starý behavior. Recovery musí dokázať resolved example generation v request traces.

## 16. Recovery a acceptance

Component recovery overí example registry, selector, filters, ordering a renderer. Journey recovery vykoná typical, edge, missing-data a adversarial cases a potvrdí, že examples nemenia policy authority. Business recovery sleduje správne refund decisions a mature ticket outcomes.

Pozitívna acceptance vyžaduje versioned example set, explicitnú provenance a labels, separation od eval datasetu, representative boundary coverage, prompt render read-back a paired variant evaluation. Recovery acceptance zahŕňa druhý request s iným segmentom, aby sa ukázalo, že one-shot alebo selected examples neboli prehnane generalizované.

Forbidden acceptance je „few-shot je vždy lepší“, production transcript bez review ako example, exception bez označenia, eval overlap, similarity-only dynamic selection alebo manuálne hodnotenie jedného pekného outputu. Examples sú riadený behavior input, nie náhrada policy a testov.
