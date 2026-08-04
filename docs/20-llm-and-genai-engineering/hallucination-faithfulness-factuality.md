# Hallucination, faithfulness a factuality

Hallucination nie je jeden presný failure type. V produkčnej GenAI aplikácii treba rozlíšiť minimálne faktickú nepravdu, tvrdenie bez dostatočného evidence, odpoveď v rozpore s dodaným contextom, nesprávnu citáciu, neautorizované použitie pravdivých informácií a správne no-answer rozhodnutie. Bez tejto taxonómie tím často optimalizuje všeobecný „hallucination score“, hoci root cause leží v retrievere, zastaranej autorite, context assembly, citáciách alebo business policy.

V incidente `GENAI-SUPPORT-08` assistant odpovedal, že zákazník má nárok na refund. Tvrdenie bolo všeobecne pravdivé podľa novej policy, ale runtime dostal iba starú autorizovanú policy generation. Odpoveď preto bola fakticky správna vo svete, no nefaithful voči povolenému evidence setu a neauditovateľná pre daný decision. Následná citácia smerovala na chunk, ktorý podporoval iba všeobecnú lehotu, nie konkrétnu exception. Jedno číslo „answer correctness = pass“ zakrylo tri rozdielne failures.

## 1. Exact evaluation subject

Factuality verdict sa viaže na konkrétny answer, exact claim set, authority snapshot a evaluation time.

```yaml
factuality_subject:
  case_id: refund-case-82413
  answer_digest: sha256:71aa...
  release_manifest: support-release-2026-08-04.8
  evidence_set: refund-evidence-4f20
  corpus_generation: refund-policy-2026-08-01
  evaluated_at: 2026-08-04T09:12:00Z
  authority_policy: support-policy-authority-v6
  claim_extractor: atomic-claims-v4
  verifier: factuality-suite-v9
```

Rovnaký text môže dostať odlišný verdict pri inom evaluation time alebo authority snapshot. „Je to pravda?“ je neúplná otázka bez domain, temporal a authority boundary.

## 2. Taxonómia

Kľúčové pojmy sa oddeľujú:

```text
factual correctness
→ tvrdenie zodpovedá authoritative reality

faithfulness alebo groundedness
→ tvrdenie je odvodené z poskytnutého povoleného evidence

citation correctness
→ citovaný zdroj podporuje príslušný claim

citation completeness
→ všetky claims vyžadujúce evidence majú podporu

calibration
→ model primerane vyjadruje neistotu alebo no-answer

policy correctness
→ odpoveď rešpektuje business a authorization pravidlá
```

Fakticky správna odpoveď môže byť nefaithful, ak vznikla z parametric memory namiesto povoleného evidence. Faithful odpoveď môže byť fakticky nesprávna, ak authoritative source je zastaraný alebo chybný. Obe situácie vyžadujú inú recovery.

## 3. Claim ako jednotka hodnotenia

Dlhá odpoveď sa rozkladá na atomic claims. Binárny verdict pre celý paragraph zakryje zmes podporovaných a nepodporovaných tvrdení.

```yaml
claim:
  id: claim-7
  text: "Zákazník môže požiadať o refund do 30 dní."
  type: policy
  verifiability: verifiable
  temporal_scope: 2026-08-04
  required_authority: refund-policy
  cited_evidence: [chunk-22]
  verdict: supported
```

Atomic decomposition nesmie meniť význam, vynechať qualification alebo rozbiť negáciu. Claim extractor je preto versioned grader, nie neutrálny parser.

## 4. Verifiable a unverifiable content

Nie každá veta je overiteľný fakt. Recommendation, creative text, subjective preference, hedged possibility a policy instruction majú odlišné semantics.

```text
"Refund lehota je 30 dní."
→ verifiable factual claim

"Toto je pravdepodobne najjednoduchší postup."
→ evaluative judgment

"Mohlo dôjsť k oneskoreniu."
→ uncertainty statement
```

Factuality score nesmie penalizovať legitímne unverifiable alebo non-factual content ako false. Dataset označuje claim type a verifiability pred verification.

## 5. Authority hierarchy

Evidence source má domain, owner, revision, effective interval a trust level. Search result alebo citačný snippet nie je automaticky authoritative.

```yaml
authority:
  domain: refund-policy
  source_id: policy-114
  revision: 9
  effective_from: 2026-08-01T00:00:00Z
  effective_to: null
  owner: legal-operations
  tenant_scope: sk-retail
  status: approved
```

Pri konflikte zdrojov sa aplikuje explicitná hierarchy. Tichý majority vote medzi starou policy, FAQ a blogom je forbidden.

## 6. Closed-domain a open-domain factuality

Closed-domain task vyžaduje odpoveď iba z definovaného evidence setu. Open-domain task môže používať externé authoritative sources. Ich eval contracts sa nesmú miešať.

V closed-domain support use-case je správne odmietnuť odpoveď, ak povolený corpus nemá evidence, aj keď model pozná všeobecne správnu informáciu. V open-domain research use-case môže byť externé vyhľadanie povolené, ale musí mať provenance, freshness a source-quality rules.

## 7. Temporal factuality

Tvrdenie môže byť historicky pravdivé a aktuálne nepravdivé. Evaluation preto pinne `effective_at`.

```yaml
temporal_check:
  claim: "Refund lehota je 14 dní."
  source_revision: 8
  source_effective_to: 2026-07-31
  question_time: 2026-08-04
  verdict: stale
```

Retriever, cache a citation layer musia zachovať temporal metadata. Latest document modification timestamp bez effective interval nestačí.

## 8. Entity a scope resolution

Factuality často zlyhá pre nesprávny subject, nie pre neznalosť faktu. Rovnaká policy môže mať odlišné pravidlá podľa tenant, product, jurisdiction alebo customer segment.

```text
správny fakt + nesprávny tenant
= nesprávna odpoveď

správna hodnota + nesprávne obdobie
= nesprávna odpoveď
```

Eval case obsahuje exact entity identifiers a scope, nie iba natural-language question.

## 9. Evidence sufficiency

Relevantný chunk nemusí byť dostatočný. Evidence musí pokrývať claim, qualifiers, exceptions a scope.

```yaml
evidence_verdict:
  claim_id: claim-7
  direct_support: true
  scope_match: true
  temporal_match: true
  exception_coverage: false
  verdict: insufficient
```

Top-k relevance alebo embedding similarity nie je support verdict. Reranker môže vybrať text o rovnakom topic bez rozhodujúcej podmienky.

## 10. Contradiction a conflict

Context môže obsahovať protichodné zdroje. Generator nesmie zvoliť pohodlnejší claim bez authority resolution.

```text
conflict detection
→ source identity a effective interval
→ authority hierarchy
→ explicit unresolved-conflict state
→ answer alebo no-answer
```

Ak conflict nemožno vyriešiť, správnym outcome môže byť escalation. Fluent synthesis konfliktu nie je acceptance.

## 11. Citation correctness

Citation syntax iba ukazuje pointer. Verification musí skontrolovať, či source podporuje konkrétny claim.

```yaml
citation_check:
  citation_label: "[3]"
  claim_ids: [claim-7, claim-8]
  resolved_chunk: chunk-22
  supports:
    claim-7: true
    claim-8: false
```

Jedna citation za paragraph môže podporovať iba časť textu. Claim-level mapping znižuje falošnú dôveryhodnosť.

## 12. Citation completeness

Odpoveď môže mať všetky citácie správne, ale niektoré tvrdenia bez citation. Completeness meria coverage všetkých evidence-requiring claims.

```text
citation correctness = podporované citované claims / citované claims
citation completeness = podporené claims / všetky claims vyžadujúce evidence
```

Tieto metriky sa reportujú oddelene.

## 13. Faithfulness a post-rationalization

Model môže vytvoriť answer z parametric knowledge a následne pripojiť plausibilnú citation. Citation correctness potom nemusí dokazovať, že evidence skutočne ovplyvnilo generation.

Faithfulness sa testuje counterfactual alebo ablation experimentmi: odstránenie alebo zmena evidence by mala primerane zmeniť answer. Ak output zostáva identický napriek protichodnému contextu, model môže context ignorovať alebo post-rationalizovať.

## 14. Factual precision a recall

Atomic factual precision meria podiel podporovaných claims. Samotná precision môže motivovať extrémne krátke odpovede. Pri taskoch vyžadujúcich coverage sa pridáva recall alebo required-facet coverage.

```text
precision = supported claims / verifiable claims produced
coverage = required supported facets / required facets
```

Model, ktorý odpovie jedným triviálnym faktom, môže mať 100 % precision a zároveň nesplniť task.

## 15. No-answer a abstention

No-answer je pozitívny outcome, keď evidence chýba, konfliktuje alebo authority scope nie je splnený. Eval dataset potrebuje answerable aj unanswerable cases.

```yaml
abstention_case:
  evidence_available: false
  expected_behavior: no_answer
  accepted_output:
    - explicit_insufficient_evidence
    - safe_escalation
```

Over-refusal je opačný failure. Calibration sa hodnotí ako správne answer versus abstain rozhodnutie podľa case.

## 16. Uncertainty

Model-generated confidence nie je spoľahlivá pravdepodobnosť bez kalibrácie. Lepšie signals môžu byť evidence coverage, retrieval margin, conflict count, validator verdict a out-of-domain detection.

User-facing uncertainty musí byť konkrétna: chýba policy revision, zdroje konfliktujú alebo údaj nie je v autorizovanom corpus. Vágne „môžem sa mýliť“ neposkytuje actionable informáciu.

## 17. Automated graders

Model grader môže rozkladať claims a hodnotiť support, ale potrebuje exact prompt/model/evidence generation, calibrated benchmark a periodic human audit.

```yaml
grader_release:
  claim_extractor: provider/model-eval-2026-07-20
  verifier: provider/model-eval-2026-07-20
  prompt: factuality-grader-v9
  retrieval: verifier-search-v5
  threshold: 0.82
  calibration_set: factuality-human-gold-v7
```

Judge nesmie byť označený ako ground truth. Same-family grader môže mať correlated bias s candidate modelom.

## 18. Human evaluation

Domain experts rozhodujú policy truth a exceptions. General annotators môžu hodnotiť clarity, ale nemajú automaticky authority pre legal alebo technical correctness.

Adjudication zachytáva evidence a rationale. Majority vote medzi nekompetentnými annotators neprekoná jedného kvalifikovaného experta.

## 19. Factuality dataset

Dataset pokrýva jednoduché facts, multi-hop claims, negácie, numbers, dates, entity ambiguity, stale evidence, conflicts, missing evidence, policy exceptions a adversarial citations.

```yaml
case_manifest:
  case_id: refund-stale-014
  question_time: 2026-08-04
  tenant: sk-retail
  authoritative_sources: [policy-114-r9]
  distractors: [policy-114-r8, faq-legacy-3]
  required_facets: [window, exception, jurisdiction]
  expected_behavior: answer
```

Split sa robí podľa source, policy family alebo time, aby rovnaké passages neunikli do train a test.

## 20. Retrieval diagnostics

Nízka factuality môže vzniknúť pred generation. Eval preto zaznamená oracle evidence recall, retrieved evidence recall, packed-context coverage a answer support.

```text
oracle evidence exists?
→ retriever ho našiel?
→ reranker ho ponechal?
→ context assembly ho zabalil?
→ model ho použil?
→ citation ho správne mapovala?
```

Prvý divergence určuje recovery. Fine-tuning generatora nepomôže, ak evidence neprišlo do contextu.

## 21. Context effects

Viac contextu nie je automaticky lepšie. Redundantné, stale alebo conflicting chunks znižujú signal-to-noise. Long-context eval testuje position, ordering, distractors a truncation.

Context assembly loguje, ktorý claim mal byť podporený ktorým evidence itemom. Bez tejto expected mapping sa debugging mení na dojem.

## 22. Parametric knowledge boundary

Parametric memory môže byť užitočná pre open-domain generation, ale v governed domain nesmie obísť current authority. Prompt explicitne určí, či model smie dopĺňať externé knowledge.

```yaml
knowledge_policy:
  allowed_sources: retrieved_authoritative_only
  external_knowledge: forbidden
  unsupported_claim_behavior: abstain
```

Model compliance sa testuje s cases, kde parametric answer je známa, ale evidence ju úmyselne neobsahuje alebo jej odporuje.

## 23. Numbers a calculations

Numerické claims vyžadujú units, scale, rounding a source. Model môže správne citovať inputs a nesprávne vypočítať result.

Deterministic calculation tool alebo validator je vhodnejší než language-model arithmetic pri high-stakes use-case. Trace spája operands, formula version a output.

## 24. Structured output

Schema validity nepreukazuje truth. Structured field môže obsahovať presvedčivú, ale nepodporenú hodnotu.

```json
{
  "eligible": true,
  "refund_days": 30,
  "evidence_ids": ["chunk-22"]
}
```

Validator overí typy; factuality layer overí hodnoty a evidence. Obe gates sú potrebné.

## 25. Mitigation layers

Factuality sa zlepšuje kombináciou current authority, quality retrieval, conflict-aware context assembly, explicit no-answer, claim-level citations, validators a evaluation. Jeden prompt „nehallucinuj“ nie je control.

Mitigation môže znížiť helpfulness alebo coverage. Trade-off sa meria segmentovane, nie iba globálnym error rate.

## 26. Production monitoring

Online signals zahŕňajú no-evidence rate, citation coverage, validator failures, user corrections, expert escalations, post-resolution reversals a claim-level audits. User thumbs-up nie je reliable factuality label.

Delayed outcomes sa pripájajú k exact release. Aggregate complaint rate bez exposure denominator a maturity window je slabý signal.

## 27. Incident triage

Pri nesprávnej odpovedi sa zachová question, exact answer, release manifest, evidence set, retrieval trace, citation mapping a authority snapshot. Tím najprv určí claim-level failure class.

```text
false claim?
unsupported claim?
correct but unauthorized claim?
stale claim?
wrong entity/scope?
wrong citation?
missing no-answer?
```

Až potom sa mení prompt, retriever alebo model.

## 28. Failure hypotheses

Ak answer obsahuje false claim, možné príčiny zahŕňajú absent evidence, conflicting stale source, context truncation, model misinterpretation, calculation error alebo grader false negative. Ak answer je correct but unfaithful, preverí sa parametric-memory leakage, ignored context a post-rationalized citation. Ak citation je wrong, preverí sa label drift, deduplication, chunk remapping a streaming reordering.

Každá hypotéza má predikovaný evidence. Náhodné pridanie ďalších chunks alebo prísnejšieho promptu bez first-divergence diagnosis môže zhoršiť výsledok.

## 29. Containment a recovery

Containment môže vynútiť no-answer pre affected domain, vypnúť stale corpus alias, zablokovať high-risk auto-actions a presmerovať cases na expert review. Incident evidence sa zachová pred reindexom alebo prompt change.

Recovery opraví source authority, retrieval, context assembly, prompt alebo validator podľa first divergence. Candidate prejde historical replay, fresh holdout, unanswerable a adversarial citation cases a bounded canary. Druhá operácia testuje odlišný entity, time alebo exception segment.

## 30. Acceptance

Pozitívna acceptance vyžaduje exact answer/evidence/authority subject, claim-level decomposition, factual correctness oddelenú od faithfulness a citations, temporal a scope checks, answerability calibration, retrieval diagnostics, calibrated graders, expert adjudication a online outcome monitoring.

Recovery acceptance vyžaduje identifikovaný first divergence, corrected authority alebo component, replay, fresh holdout, bounded canary a second-operation test s odlišným factuality failure mode.

Forbidden acceptance je fluent answer ako truth, valid JSON ako correctness, citation presence ako support, general web consensus ako domain authority, model judge ako ground truth, 100 % factual precision pri nulovej required coverage alebo documentation audit ako vykonaná production factuality validation.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Tracing, token usage a cost observability](tracing-token-usage-cost-observability.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Prompt injection a indirect prompt injection →](prompt-injection-indirect-prompt-injection.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
