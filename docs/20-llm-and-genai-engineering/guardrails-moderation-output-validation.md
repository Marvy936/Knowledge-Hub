# Guardrails, moderation a output validation

Guardrail je runtime control, ktorý z konkrétneho risk signálu vytvorí vynútiteľné rozhodnutie nad konkrétnym vstupom, contextom, tool callom, tool response alebo výstupom. Nie je to iba classifier, system prompt ani všeobecná veta „model nesmie“. Produkčný guardrail potrebuje exact intervention point, policy generation, detector generation, threshold, response action, enforcement owner a evidence o tom, čo bolo skutočne povolené, zablokované alebo odoslané ďalej.

V incidente `GENAI-SUPPORT-09` aplikácia spracovala obrázok dokladu a hlasovú správu. Textová moderácia skontrolovala až finálny summary, ktorý neobsahoval explicitne škodlivý jazyk, a preto vrátila allow. Medzitým multimodálny model navrhol tool call s osobnými údajmi, output validator overil iba JSON Schema a downstream workflow vytvoril refund pre nesprávnu osobu. Každý lokálny komponent hlásil success, ale chýbal guardrail chain cez media input, extracted text, tool proposal, business invariants a final egress.

## 1. Exact guardrail subject

Guardrail verdict platí iba pre presne identifikovaný artifact, policy a intervention point. Bez tohto subjectu nie je možné vysvetliť, prečo bola rovnaká veta raz povolená a inokedy zablokovaná.

```yaml
guardrail_subject:
  operation_id: support-case-82477
  intervention_point: tool_call
  content_digest: sha256:8a4d...
  content_type: application/json
  modality: structured-text
  policy_release: support-safety-v14
  detector_release: moderation-2026-06-18
  threshold_profile: sk-retail-high-impact-v5
  schema_release: refund-tool-v9
  tenant: sk-retail
  locale: sk-SK
  enforcement_mode: block
```

Verdict bez `policy_release`, `detector_release` a `content_digest` je iba diagnostický hint. Pri incidente musí byť možné reprodukovať presný input, canonicalization a rozhodovací profil bez spoliehania sa na aktuálny mutable default.

## 2. Guardrail nie je jeden filter

Produkčný guardrail chain skladá viacero odlišných controlov. Každý rieši inú otázku a má inú authority boundary.

```text
schema validator
→ je output syntakticky a typovo platný?

business-rule validator
→ je navrhnutá operácia povolená pre tento case a principal?

content moderator
→ obsahuje vstup alebo výstup regulovaný alebo škodlivý obsah?

groundedness alebo factuality validator
→ je tvrdenie podporené povoleným evidence setom?

DLP a privacy policy
→ môže tento data object opustiť aktuálny trust boundary?

tool policy
→ smie sa táto capability použiť s týmito argumentmi a destination?
```

Jeden classifier nedokáže nahradiť tieto kontrakty. Napríklad harm moderation môže správne povoliť neutrálny text, ktorý napriek tomu obsahuje cudzie osobné údaje alebo navrhuje neoprávnenú finančnú operáciu.

## 3. Intervention points

Guardrails sa aplikujú na viacerých miestach, pretože riziko môže vzniknúť alebo zmeniť formu počas celého flow. Kontrola iba finálneho textu nevidí skrytú inštrukciu v dokumente, nebezpečný tool argument ani citlivý tool response.

```text
raw user input
→ uploaded media a extracted content
→ retrieved context
→ assembled prompt
→ model output
→ proposed tool call
→ tool response
→ transformed final output
→ external egress
```

Pre každý intervention point sa určí detector, policy, timeout a fail behavior. Rovnaký control sa nemusí dať bezpečne preniesť medzi inputom a outputom, pretože kategórie, thresholdy a význam false positive sú rozdielne.

## 4. Policy decision a policy enforcement

Detector alebo moderator produkuje signál; policy decision point z neho vytvára rozhodnutie; enforcement point rozhodnutie vykoná. Tieto tri kroky sa nesmú zlúčiť do neurčitého `is_safe=true`.

```yaml
policy_decision:
  risk_signals:
    violence: 0.02
    personal_data: 0.91
    protected_material: 0.04
  policy_rule: no-regulated-data-to-external-recipient
  verdict: deny
  action: redact-and-escalate
  reason_code: DLP-EXTERNAL-004
```

Ak classifier iba vráti metadata, aplikácia musí stále explicitne blocknúť, redactnúť, požiadať o confirmation alebo eskalovať. Azure AI Content Safety napríklad vracia classification metadata; samotná služba automaticky neodstráni obsah ani nezablokuje používateľa, pokiaľ enforcement nevykoná aplikácia alebo gateway policy.

## 5. Input moderation

Input moderation chráni používateľa, model a downstream systémy pred obsahom, ktorý je mimo povoleného use case alebo vyžaduje osobitné spracovanie. Kontroluje text aj podporované media modality pred tým, než sa obsah vloží do promptu alebo uloží do memory.

Normalizácia musí zachovať auditovateľný vzťah k originálu. Unicode folding, whitespace collapse, OCR a transcription môžu odhaliť obfuscated obsah, ale nesmú prepísať authoritative raw artifact bez digestu a transform lineage.

## 6. Context a retrieval moderation

Retrieved dokument nie je dôveryhodný iba preto, že pochádza z interného vector store. Corpus môže obsahovať stale, kompromitovaný, cross-tenant alebo policy-incompatible obsah.

Guardrail nad contextom overuje tenant, ACL, classification, temporal validity, provenance a injection risk. Dokument, ktorý neprejde, sa odstráni pred context assembly a trace zaznamená dôvod; model nemá dostať zakázaný obsah s inštrukciou, aby ho „ignoroval“.

## 7. Tool-call validation

Tool call je navrhnutá operácia, nie autorizovaný business action. Schema validácia overuje tvar, ale policy musí overiť canonical resource, principal, destination, data classification, action risk a confirmation digest.

```json
{
  "tool": "create_refund",
  "arguments": {
    "case_id": 82477,
    "customer_id": "cust-441",
    "amount_minor": 12990,
    "currency": "EUR",
    "reason_code": "duplicate-charge"
  }
}
```

Validator musí napríklad potvrdiť, že `customer_id` patrí case-u, suma neprekračuje policy limit a refund nebol už vytvorený. Validný JSON s chybným customerom je stále forbidden output.

## 8. Tool-response validation

Tool response môže obsahovať prompt injection, cross-tenant data, nečakaný MIME typ alebo príliš veľký payload. Executor preto neodovzdáva raw response priamo modelu.

Response sa canonicalize-ne, klasifikuje, zúži na povolené fields a označí provenance. Ak tool vráti HTML s hidden instructions alebo redirect na externý objekt, control rozhodne, či obsah zahodí, izoluje alebo odošle na human review.

## 9. Output moderation

Output moderation hodnotí text alebo media, ktoré budú zobrazené používateľovi alebo odoslané externému systému. Musí sa vykonať nad finálnym canonical outputom po template rendering, citation insertion, localization a postprocessingu.

Moderovať iba raw model completion nestačí. Aplikácia môže po model call pridať citlivé metadata, nesprávny link alebo obsah z tool response, ktorý pôvodná moderácia nevidela.

## 10. Structured output validation

Structured Outputs a JSON Schema znižujú syntaktickú variabilitu, ale nepreukazujú pravdivosť ani business correctness. Validator preto oddeľuje syntax, semantic constraints a authoritative read-back.

```yaml
output_contract:
  schema: refund-decision-v9
  semantic_rules:
    - amount_minor > 0
    - currency == case.currency
    - customer_id == case.customer_id
    - evidence_ids subset_of authorized_evidence
  side_effect: none
```

Najprv sa output parse-ne proti pinned schema. Potom deterministic rules overia cross-field invariants a až následne môže ďalšia vrstva použiť výstup na decision alebo tool proposal.

## 11. Business invariants

Business invariant vyjadruje podmienku, ktorú model nesmie zmeniť presvedčivým odôvodnením. Príklady sú tenant equality, maximálna refund suma, povinný approval, zakázaná zmena bankového účtu alebo requirement na authoritative evidence.

Invariant sa vykonáva mimo modelu nad canonical data. Model môže poskytnúť explanation, ale explanation nie je vstup do authorization rule, pokiaľ pravidlo explicitne nepracuje s overenou kategóriou alebo evidence fieldom.

## 12. Refusal a abstention contract

Bez definovaného refusal contractu aplikácia nevie rozlíšiť bezpečné odmietnutie od technického zlyhania alebo policy bypassu. Refusal má typed reason, user-safe message a next action.

```json
{
  "status": "needs_human_review",
  "reason_code": "IDENTITY_MISMATCH",
  "user_message": "Údaje sa nezhodujú s prípadom. Žiadosť odošleme na manuálne overenie.",
  "tool_calls_allowed": false
}
```

Abstention sa hodnotí ako legitímny výsledok pre neanswerable alebo high-risk cases. Tlak na maximálnu answer rate často znižuje bezpečnosť a factuality, preto acceptance zahŕňa aj správne odmietnutia.

## 13. Harm categories a custom policy

Všeobecné harm categories ako hate, violence, sexual content a self-harm sú iba časť policy surface. Enterprise application často potrebuje custom categories: financial advice, credential disclosure, regulated personal data, protected material, unsafe code alebo prohibited transaction.

Custom category potrebuje examples, counterexamples, locale coverage, threshold a ownera. Názov kategórie bez operational definition vedie k nekonzistentným labels a neauditovateľným blokáciám.

## 14. Threshold calibration

Classifier score nie je univerzálna pravdepodobnosť a rovnaký threshold nemusí fungovať pre všetky jazyky, modality alebo user segments. Threshold sa kalibruje na reprezentatívnom eval datasete podľa nákladov false positive a false negative.

```text
public chat + low-impact output
→ môže tolerovať review queue

financial write + regulated data
→ vyžaduje konzervatívny block alebo human approval
```

Calibration report uvádza confusion matrix, segment breakdown, confidence intervals a unresolved cases. Global average nesmie zakryť slabú výkonnosť pre slovenčinu, OCR text alebo multimodálne inputy.

## 15. Severity a action mapping

Severity score sa mapuje na explicitnú response action. Medzi `allow` a `block` môžu existovať `allow-with-warning`, `redact`, `safe-complete`, `require-confirmation`, `route-to-specialist` a `quarantine`.

Mapping je policy artifact s verziou. Zmena threshold alebo action mappingu je behavior release a prechádza evalom, review a controlled promotion rovnako ako prompt alebo model.

## 16. Fail-open, fail-closed a degraded mode

Pri nedostupnom guardraile musí mať každý flow vopred určené správanie. High-impact write sa typicky fail-closed alebo prepne na manual queue; low-risk read-only assistant môže použiť obmedzený degraded mode.

```yaml
failure_policy:
  content_moderator_timeout:
    read_only_answer: safe_template
    financial_tool_call: deny
    internal_draft: queue_for_review
```

Improvised retry bez budgetu môže zvýšiť latency a duplicate work. Failure policy zahŕňa timeout, retry count, alternate detector, queue capacity a user-visible message.

## 17. Streaming output

Streaming komplikuje output moderation, pretože škodlivý obsah môže byť používateľovi odoslaný skôr, než classifier vidí celý význam. Aplikácia môže bufferovať celé outputy, používať sliding windows s overlapom alebo kombinovať pre-generation a post-generation controls.

Window size a overlap sú súčasťou exact policy subjectu. Príliš malé windows stratia kontext; bez overlapu môže zakázaná fráza prejsť cez hranicu chunkov.

## 18. Canonicalization a obfuscation

Attackers používajú homoglyphs, whitespace, base64, markdown, HTML comments, image text, QR kódy alebo nested archives. Canonicalization vrstva pripraví analyzovateľnú reprezentáciu, ale uchová raw digest a transform chain.

Decoder nesmie automaticky vykonávať arbitrary code alebo fetchovať externé URL. Každá transformácia má limity na recursion, size, time a supported formats, aby sa guardrail nestal decompression alebo parser attack surface.

## 19. Multimodálne guardrails

Text-only moderation nevidí obsah v obrázku, audiu alebo videu. Multimodálny pipeline preto rozlišuje raw media moderation, OCR/transcription moderation, cross-modal interpretation a generated media checks.

Obrázok môže byť vizuálne neškodný, ale obsahovať malý text s osobnými údajmi alebo indirect prompt injection. Audio môže obsahovať viac hovoriacich a citlivé údaje, ktoré transcription model zle priradí; guardrail evidence preto zahŕňa timestamps, bounding boxes alebo speaker labels.

## 20. Protected material a provenance

Protected-material detector alebo similarity check je risk signal, nie automatický copyright verdict. Application policy určuje povolené transformácie, citation requirements a response action.

Provenance sa zachováva od source artifactu cez extraction po final output. Pri blokácii musí byť možné určiť, či match vznikol z user uploadu, retrieved dokumentu alebo model generation.

## 21. PII, secrets a DLP

PII a secret detection sa vykonáva pred provider callom, v context assembly, v tool response aj pred egressom. Redaction používa stable placeholders, aby sa zachovala referential consistency bez odhalenia raw value.

```text
<PERSON_1> požiadal o refund pre účet <ACCOUNT_1>
```

Nie všetky identifikátory sa majú automaticky odstrániť. Policy zohľadňuje účel, legal basis, tenant, recipient a minimum necessary; nesprávna redaction môže znemožniť autorizáciu alebo vytvoriť zámenu osôb.

## 22. Model-based guardrails

LLM-as-guardrail môže rozumieť zložitému contextu, ale je nondeterministic, môže podľahnúť injection a môže zdieľať bias s hodnoteným modelom. Preto sa nepoužíva ako jediný enforcement pre jednoduché deterministic invariants.

Model judge má pinned model, prompt, schema, examples a calibration dataset. Jeho verdict sa kombinuje s deterministic controls a pri neistej alebo high-impact situácii smeruje na expert review.

## 23. Guardrail ordering

Poradie controlov ovplyvňuje latency, cost aj bezpečnosť. Lacné deterministic checks sa často vykonajú pred drahým modelovým classifierom, ale data minimization alebo secret redaction musí prebehnúť ešte pred odoslaním obsahu externému detectoru.

```text
size a MIME validation
→ tenant/ACL check
→ secret/PII minimization
→ prompt-injection a harm detection
→ model call
→ schema a business validation
→ DLP a egress enforcement
```

Ordering je súčasťou release manifestu. Paralelné classifiers potrebujú jasné merge rules a timeout policy.

## 24. Human review

Human review nie je neurčitý fallback. Queue obsahuje exact artifact, detector evidence, policy rule, redacted context, reviewer authority a SLA.

Reviewer nemá automaticky vidieť všetky raw dáta. Access sa riadi classification a need-to-know; rozhodnutie sa zaznamená ako label pre incident a calibration, nie ako neauditovaný chat comment.

## 25. Observability

Guardrail telemetry potrebuje operation ID, intervention point, policy/detector generations, latency, verdict, reason code, action a enforcement result. Raw content sa neloguje defaultne, pretože guardrail môže spracúvať najcitlivejšie dáta v systéme.

Metrics zahŕňajú block rate, review rate, false-positive appeals, escaped incidents, timeout rate, degraded-mode usage a segment performance. Náhly pokles block rate môže znamenať zlepšenie inputov alebo nefunkčný detector; samotná hodnota bez denominatora a segmentu nestačí.

## 26. Testing dataset

Guardrail eval dataset obsahuje pozitívne, negatívne, boundary a benign hard-negative cases. Zahŕňa multilingual, obfuscated, long-context, streaming, multimodal, tool-call a policy-conflict scenáre.

Každý case má expected action, nie iba expected classifier label. Napríklad PII v internom read-only summary môže byť allowed, zatiaľ čo rovnaký field v externom email tool calle musí byť denied.

## 27. Adversarial evaluation

Red team testuje transformácie, role-play, encoded instructions, document injection, tool-response injection, schema smuggling, destination obfuscation a chunk-boundary attacks. Test sa považuje za úspešný iba vtedy, keď forbidden side effect alebo disclosure nevznikne.

Detekcia attack textu nie je business acceptance. Agent môže attack označiť ako škodlivý a napriek tomu vykonať navrhnutý tool call, ak enforcement chain nie je atomicky prepojený s verdictom.

## 28. Release a promotion

Guardrail release obsahuje policy rules, detector/model versions, thresholds, intervention points, ordering, fail behavior a response templates. Mutable dashboard konfigurácia bez exportovateľného manifestu nie je reprodukovateľný release.

Promotion prechádza static validation, offline eval, shadow alebo canary traffic a segment gates. Zmena detectora bez zmeny policy verzie musí byť stále zachytená, pretože behavior sa môže zmeniť pri identickom configu.

## 29. Rollback

Rollback vracia celý guardrail release, nie iba threshold. Musí zahŕňať classifier generation, custom categories, prompt shield config, output schemas, business rules, cache generation a response action mapping.

Po rollbacku sa vykoná loaded-state read-back a replay incident cases. Ak už vznikol side effect alebo disclosure, rollback nezvráti business škodu; recovery zahŕňa aj revocation, deletion, customer notification alebo compensating transaction.

## 30. Failure hypotheses

Pri escaped unsafe outpute sa paralelne overujú aspoň tieto hypotézy. Každá má inú evidence a recovery path.

- **Wrong intervention point** — detector kontroloval final text, ale riziko vzniklo v tool proposal alebo retrieved documente; trace musí ukázať celý flow.
- **Wrong subject generation** — runtime načítal starý threshold, detector alebo schema; loaded-state digest sa porovná s intended release.
- **Canonicalization gap** — škodlivý obsah bol v OCR, encoded texte alebo cez chunk boundary; overí sa transform chain a windows.
- **Policy gap** — detector správne klasifikoval obsah, ale neexistovalo pravidlo pre konkrétny data flow alebo business invariant.
- **Enforcement bypass** — policy verdict bol deny, no downstream pokračoval kvôli timeoutu, exception handlingu alebo race condition.
- **Segment weakness** — classifier nebol kalibrovaný pre jazyk, modality alebo domain vocabulary incidentu.
- **Human-process failure** — review queue nemala správneho experta, SLA alebo dostatočnú evidence a verdict sa nesprávne uzavrel.

Incident review nevyberie prvé presvedčivé vysvetlenie. Zachová competing hypotheses, kým authoritative telemetry, replay a business read-back neukážu first divergence.

## 31. Containment a recovery

Containment najprv zastaví forbidden outcome: vypne high-risk tool, zablokuje destination, prepne flow do read-only alebo manual mode a zachová evidence. Až potom sa ladí detector.

Recovery obnoví known-good composed release, invaliduje policy caches, overí loaded state a replay-ne incident plus benign controls. Produkcia sa obnoví po segment acceptance, nie po jednom bezpečnom prompt-e.

## 32. Acceptance

Pozitívna acceptance dokazuje, že povolené inputy prejdú s prijateľnou latency a správnym output contractom. Forbidden acceptance dokazuje, že unsafe content, unauthorized tool call, privacy violation a business-invariant breach nevytvoria side effect ani disclosure.

Second-operation test overí, že po policy update alebo rollbacku sa nový request vyhodnotí podľa novej generation a staré cache verdicts sa nepoužijú. Alternate-scenario test použije iný jazyk, modality, tenant a intervention point, aby sa nepotvrdil iba jeden memorovaný incident case.

## 33. Čo dokumentačná validácia nepreukazuje

Markdown, schema examples a CI audit môžu overiť konzistenciu modelu a prose depth. Nepreukazujú classifier quality, threshold calibration, provider availability, streaming enforcement, human-review SLA ani absenciu produkčných escapes.

Runtime status `Verified` vyžaduje vykonaný eval dataset, adversarial exercise, enforcement read-back a business outcome. Produkčný stav `Stable` navyše vyžaduje časové evidence z reálnej prevádzky, incident handling a kontrolovaný rollback.

## Primárne zdroje

- [OpenAI Moderations API](https://platform.openai.com/docs/api-reference/moderations)
- [Microsoft Foundry guardrails and controls overview](https://learn.microsoft.com/en-us/azure/foundry/guardrails/guardrails-overview)
- [Azure AI Content Safety overview](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview)
- [Azure API Management `llm-content-safety` policy](https://learn.microsoft.com/en-us/azure/api-management/llm-content-safety-policy)
- [OWASP GenAI Security Project](https://genai.owasp.org/)

## Kontrolné otázky

1. Ktorý exact artifact, policy release, detector release a intervention point vytvorili guardrail verdict?
2. Kde sa oddeľuje classifier signal, policy decision a enforcement action?
3. Ktoré business invariants sa overujú mimo modelu po schema validation?
4. Aký je fail-open, fail-closed alebo degraded behavior pri nedostupnom guardraile?
5. Ako sa kalibrujú thresholdy pre jazyk, modality, tenant a high-impact segment?
6. Dokáže forbidden test preukázať, že nevznikol side effect ani disclosure?
7. Vracia rollback celý guardrail release vrátane caches, schemas a action mappingu?

## Navigácia

- Predchádzajúca kapitola: [Data exfiltration, tool abuse a excessive agency](data-exfiltration-tool-abuse-excessive-agency.md)
- Späť na sekciu: [LLM and GenAI Engineering](README.md)
- Nasledujúca kapitola: [Privacy, retention a provider data controls](privacy-retention-provider-data-controls.md)
