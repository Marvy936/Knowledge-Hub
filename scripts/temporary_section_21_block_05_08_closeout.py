#!/usr/bin/env python3
"""Temporary closeout helper for Section 21 chapters 5-8."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs/21-ai-agents-and-intelligent-automation"


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old[:160]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# Targeted learning-depth remediation. Each replacement is limited to the
# exact section reported by the chapter-level audit.
approval = SECTION / "human-in-the-loop-approval-gates.md"
replace_exact(
    approval,
    """## 7. Approve, edit, reject a escalate

Approval UI môže podporovať viac rozhodnutí:

- **Approve** — povoľuje presne zobrazený action digest.
- **Edit** — vytvorí novú proposal generation s novými arguments a digestom; pôvodný approval sa nepoužije.
- **Reject** — zastaví action a môže pridať bounded feedback pre replanning.
- **Escalate** — odovzdá rozhodnutie reviewerovi s vyššou authority alebo inej roli.

Edit nie je approval pôvodnej akcie. Po zmene resource, amount alebo parameter sa musí spustiť nová policy evaluation.
""",
    """## 7. Approve, edit, reject a escalate

Rozhodnutia v approval UI nie sú štyri textové odpovede na jednu otázku. Každé z nich vykonáva odlišný state transition nad presným `approval_request_id`, proposal generation a action digestom. Approval service preto nesmie previesť voľný komentár modelu alebo reviewera priamo na execution permission; najprv musí validovať, ktorý transition je povolený z aktuálneho stavu a či rozhodujúci principal má preň authority.

- **Approve** — povoľuje výhradne zobrazený action digest a zachováva pôvodné canonical subjects, arguments, preconditions, tool contract a expiry. Ak sa ktorýkoľvek execution-relevant field zmení, tento verdict sa už nesmie použiť.
- **Edit** — nevykonáva pôvodnú akciu s ručne prepísaným parametrom. Vytvorí novú proposal generation, znovu canonicalizuje subject, prepočíta digest a spustí novú policy evaluation, aby reviewer videl presný efekt upravenej akcie.
- **Reject** — uzavrie aktuálnu proposal ako nepovolenú a môže pridať bounded reason code alebo feedback pre replanning. Agent nesmie rejection obísť kozmetickým preformulovaním rovnakej akcie pod novým technical attempt ID.
- **Escalate** — nemení proposal ani ju dočasne neschvaľuje. Presunie decision ownership na principal alebo rolu s vyššou authority a zachová rovnaký digest, evidence envelope a audit lineage.

Tieto transitions majú rozdielne recovery dôsledky. Po `edit` alebo zmene subjectu sa predchádzajúce approvals invalidujú; po `reject` sa musí objaviť nový diskriminačný dôkaz alebo odlišná bounded action; po `escalate` zostáva execution blokovaný, kým oprávnený reviewer nevydá nový verdict. UI tak nevytvára všeobecný súhlas „pokračovať“, ale presne auditovateľnú zmenu stavu jednej action proposal.
""",
)
replace_exact(
    approval,
    """## 13. Revalidation po resume

Pred execution sa porovná current state so schváleným envelope:

```text
same action digest?
same canonical subject and UID?
same resource generation or allowed drift?
same policy generation or compatible policy?
reviewer still authorized?
credentials still valid?
preconditions still true?
no equivalent action already committed?
```

Pri zmene sa request označí `stale` a agent musí replanovať alebo vytvoriť nový approval request.
""",
    """## 13. Revalidation po resume

Durable checkpoint dokáže obnoviť to, čo agent a approval service vedeli v okamihu prerušenia, ale nezaručuje, že svet zostal nezmenený. Medzi approvalom a resume sa môže zmeniť resource UID alebo generation, policy, reviewerova rola, credential, incident ownership aj downstream business state. Executor preto nepoužíva uložený verdict ako trvalý token; používa ho iba ako dôkaz, že konkrétny digest bol schválený za konkrétnych preconditions.

Pred execution sa porovná current state so schváleným envelope:

```text
same action digest?
same canonical subject and UID?
same resource generation or allowed drift?
same policy generation or compatible policy?
reviewer still authorized?
credentials still valid?
preconditions still true?
no equivalent action already committed?
```

Kontrola musí prebehnúť v trusted executor alebo policy vrstve nad authoritative read-backmi, nie modelovým odhadom podobnosti. Povolený drift musí byť explicitne opísaný v tool contracte alebo policy; napríklad nový observation timestamp môže byť kompatibilný, zatiaľ čo iný deployment UID alebo refund amount nie je.

Pri akejkoľvek nekompatibilnej zmene sa request označí `stale`, execution zostane blokovaný a agent musí replanovať alebo vytvoriť nový approval request. Tým sa oddeľuje bezpečné pokračovanie rovnakého subjectu od replayu starého súhlasu na novú realitu.
""",
)
replace_exact(
    approval,
    """## 38. Failure hypotheses

Pri incidente po ľudskom schválení nie je správny záver „človek to povolil“. Failure môže vzniknúť v proposal, UI, identity, policy, persistence, resume, execution alebo outcome verification.

- **Ambiguous subject** — karta nezobrazila exact resource, recipient, amount alebo environment.
- **Digest mismatch** — vykonané arguments sa líšili od schváleného envelope.
- **Stale approval** — resource, policy, identity alebo evidence sa zmenili počas čakania.
- **Authorization drift** — reviewer už pri execution nemal required role.
- **Duplicate proposal** — viac agentov vytvorilo ekvivalentné approval requests.
- **Replay** — starý decision artifact sa použil na nový action attempt alebo operation.
- **Unknown outcome retry** — timeout viedol k opakovaniu už commitnutej akcie.
- **UI omission** — critical field alebo alternative bol skrytý.
- **Approval fatigue** — reviewer schvaľoval bez primeranej kontroly pre vysoký volume.
- **Audit gap** — chýbal displayed evidence digest alebo execution request ID.

Každá hypotéza sa testuje proti approval, identity, execution a business records.
""",
    """## 38. Failure hypotheses

Pri incidente po ľudskom schválení nie je správny záver „človek to povolil“. Approval je reťaz proposal → policy → presentation → identity decision → resume → execution → outcome, takže first divergence môže vzniknúť pred kliknutím aj po ňom. Diagnostika najprv zmrazí štyri časové línie: všetky proposal generations a ich digests, reviewerovu autentifikáciu a entitlement snapshots, execution attempts s provider alebo target request IDs a authoritative business state. Až ich korelácia ukáže, či človek schválil nesprávne zobrazený subject, či executor vykonal inú generation alebo či bola správna akcia zopakovaná po unknown outcome.

Competing hypotheses sa nevyvracajú tým, že audit log obsahuje `approved=true`. Ambiguous UI sa testuje proti presnému payloadu, ktorý reviewer reálne videl; stale approval proti resource a policy generations pri resume; replay a duplicate proposal proti stabilnému business operation a action ID; approval fatigue proti decision timing, edit/reject patterns a reviewer workloadu. Business ledger alebo runtime resource read-back zostáva authority pre skutočný side effect, aj keď approval service hlási úspešný transition.

- **Ambiguous subject** — karta nezobrazila exact resource, recipient, amount alebo environment, takže verdict nemožno jednoznačne priradiť k vykonanému side effectu.
- **Digest mismatch** — vykonané arguments alebo tool defaults sa líšili od canonical envelope, ktorý reviewer schválil.
- **Stale approval** — resource, policy, identity alebo supporting evidence sa zmenili počas čakania a resume nevyžiadal nový verdict.
- **Authorization drift** — reviewer už pri decisione alebo execution nemal required role, incident assignment alebo authentication freshness.
- **Duplicate proposal** — viac agentov vytvorilo ekvivalentné approval requests pre jeden business operation a deduplication ich nerozpoznala.
- **Replay** — starý decision artifact sa použil na nový action attempt, proposal generation, tenant alebo operation.
- **Unknown outcome retry** — timeout po možnom commitnutí viedol k opakovaniu akcie bez authoritative reconciliation.
- **UI omission** — critical field, competing hypothesis, rollback boundary alebo alternative bol skrytý a reviewer nemal informed evidence.
- **Approval fatigue** — vysoký volume a slabé risk tiering viedli k mechanickému schvaľovaniu bez primeranej kontroly.
- **Audit gap** — chýbal displayed evidence digest, identity snapshot, execution request ID alebo business read-back, takže causal chain nemožno uzavrieť.

Root cause verdict musí pomenovať prvý chybný transition a jeho dôkaz, nie iba posledného človeka v reťazci. Incident sa uzavrie až po containment-e pending a replayable requests, oprave konkrétnej generation, replayi incidentu aj benign controlu a potvrdení, že druhá nezávislá operácia nevie zdediť pôvodný approval.
""",
)

memory = SECTION / "short-term-state-long-term-external-memory.md"
replace_exact(
    memory,
    """## 12. Freshness, TTL a invalidation

Každá memory class potrebuje freshness policy. Krátkodobý observation môže expirovať po sekundách, entitlement snapshot po minútach a schválený runbook až po novej verzii. TTL však nie je jediný invalidation trigger.

Záznam sa invaliduje aj pri:

- zmene architecture generation;
- zmene ownera alebo policy;
- odvolaní súhlasu používateľa;
- oprave pôvodného incidentu;
- zmene identity alebo tenancy scope;
- explicitnom supersede novším záznamom;
- zistení poisoning alebo nesprávnej generalizácie.

Retrieval musí filtrovať neplatné záznamy predtým, než sa dostanú do model contextu.
""",
    """## 12. Freshness, TTL a invalidation

Každá memory class potrebuje freshness policy odvodenú od volatility a authority jej subjectu. Krátkodobý observation môže expirovať po sekundách, entitlement snapshot po minútach a schválený runbook až po novej verzii. TTL však modeluje iba plynutie času; nevie zachytiť udalosti, ktoré okamžite menia význam záznamu. Memory lifecycle preto kombinuje časovú platnosť s event-driven invalidation a explicitnou supersession lineage.

Záznam sa invaliduje aj pri nasledujúcich udalostiach:

- **Architecture generation change** — memory opisujúca staré komponenty, dependency graph alebo rollout mechanizmus sa nesmie použiť na novú generation bez compatibility review.
- **Owner alebo policy change** — zmena service ownera, approval policy alebo procedural authority môže znížiť trust recordu aj pred jeho časovým expiry.
- **Odvolanie súhlasu používateľa** — personal preference alebo profilový údaj musí prestať vstupovať do retrievalu podľa consent a purpose policy, nie až po všeobecnom TTL.
- **Oprava pôvodného incidentu** — corrigendum alebo nový postmortem môže vyvrátiť predchádzajúcu interpretáciu; record sa označí superseded alebo quarantined, aby starý záver neprežil source opravu.
- **Identity alebo tenancy transition** — account merge, role change, tenant migration alebo canonical-ID oprava môže zmeniť, komu record patrí a kto ho smie načítať.
- **Explicitné supersede novšou generation** — nový reviewed record vytvorí lineage k staršiemu záznamu, aby retrieval vedel vybrať aktuálnu authority a audit vedel vysvetliť prechod.
- **Poisoning alebo chybná generalizácia** — záznam, ktorého source, transformation alebo scope bol kompromitovaný, sa okamžite quarantinuje bez čakania na expiry.

Invalidation event musí aktualizovať authoritative store aj všetky serving vrstvy: retrieval index, caches, summaries a precomputed context packs. Retrieval potom filtruje neplatné records pred rankingom a model dostane iba records, ktorých scope, authority a validity boli overené pre aktuálny operation subject. Úspešný delete alebo update v primary store nie je postačujúci, kým stale index alebo cache stále môže record vrátiť.
""",
)
replace_exact(
    memory,
    """## 24. Failure hypotheses

Keď agent použije nesprávnu informáciu, „model si zle zapamätal“ je iba jedna hypotéza. Failure môže vzniknúť pri scope resolution, retrieval, compaction, stale cache, identity mapping, source transformation alebo authority selection. Diagnostika preto zachováva viacero alternatív, kým evidence neurčí first divergence.

- **Wrong namespace** — retrieval použil nesprávny tenant, user, service alebo environment scope.
- **Stale memory** — záznam expiroval alebo mal byť invalidovaný novou architecture generation.
- **Authority inversion** — unreviewed summary prebil aktuálny external read-back.
- **Compaction loss** — summary odstránil pending action, approval digest alebo unresolved hypothesis.
- **Poisoned write** — nedôveryhodný observation sa uložil ako procedural fact.
- **Identity drift** — záznam sa priradil k nesprávnej canonical identity.
- **Index lag** — store obsahoval opravu, ale retrieval index ešte vracal starý record.
- **Deletion gap** — primary record bol odstránený, no derived summary alebo index entry zostal dostupný.

Každá hypotéza potrebuje potvrdzujúci a vyraďujúci dôkaz. Pri high-impact akcii sa memory nepoužije ako jediná authority.
""",
    """## 24. Failure hypotheses

Keď agent použije nesprávnu informáciu, „model si zle zapamätal“ je iba jedna hypotéza. Memory decision vzniká cez write lineage, namespace resolution, authoritative store read, index a cache serving, ranking, compaction a finálnu context assembly. Diagnostika preto rekonštruuje, ktorý exact record bol v každej vrstve dostupný, ktorý bol vybraný a aké metadata model skutočne videl. Store truth, index truth a prompt context môžu byť v rovnakom čase rozdielne states.

First divergence sa hľadá porovnaním memory query subjectu s autentifikovaným tenantom a identity mappingom, record generation s invalidation events, source authority s external read-backom a selected-context digestom s model trace. Napríklad správny record v store nevyvracia `index lag`; správny record v prompt capture nevyvracia `authority inversion`; úspešné primary deletion nevyvracia derived-copy gap. Každá hypotéza potrebuje dôkaz, ktorý ju vie potvrdiť aj konkrétny observation, ktorý ju vyradí.

- **Wrong namespace** — retrieval použil nesprávny tenant, user, service alebo environment scope; falsifikáciou je storage-enforced query a returned-record lineage s aktuálnym canonical auth contextom.
- **Stale memory** — záznam expiroval alebo mal byť invalidovaný novou architecture generation; rozhoduje validity metadata a doručenie invalidation eventu do serving vrstiev.
- **Authority inversion** — unreviewed summary alebo episodic record prebil aktuálny external read-back; porovnáva sa authority policy a evidence, ktoré context curator použil.
- **Compaction loss** — summary odstránil pending action, approval digest alebo unresolved hypothesis; raw event archive a compaction coverage ukážu prvý stratený invariant.
- **Poisoned write** — nedôveryhodný observation sa uložil ako procedural fact; write producer, source refs, review transition a namespace propagation určia blast radius.
- **Identity drift** — záznam sa priradil k nesprávnej canonical identity po merge, role alebo tenancy zmene; identity mapping history potvrdí alebo vyvráti chybný scope.
- **Index lag** — authoritative store obsahoval opravu, ale retrieval index alebo cache ešte vracali starú generation; index watermark a serving trace určia oneskorenie.
- **Deletion gap** — primary record bol odstránený, no derived summary, embedding, eval copy alebo backup zostal dostupný; deletion graph a reachability query ukážu chýbajúcu vetvu.

Pri high-impact akcii sa memory nepoužije ako jediná authority ani po identifikovaní pravdepodobnej príčiny. Recovery verdict vyžaduje opravený record alebo serving generation, incident replay s rovnakým query subjectom, benign control pre relevantnú memory a druhú tenant-isolated operáciu bez preneseného state-u.
""",
)
replace_exact(
    memory,
    """## 25. Evidence envelope

Troubleshooting záznam pre memory decision môže mať tento tvar:

```yaml
memory_decision_id: md-8831
operation_id: checkout-recovery-017
query_subject:
  tenant: retail-eu
  service: checkout
  environment: production
retrieved_records:
  - memory_id: mem-ops-00491
    generation: 3
    authority: reviewed-episodic
    valid: true
    source_digest: sha256:...
external_readbacks:
  - subject: kubernetes/deployment/checkout
    resource_version: "8839201"
    observed_at: 2026-08-04T14:17:33Z
conflicts:
  - memory_id: mem-ops-00122
    reason: architecture_generation_mismatch
selected_context_digest: sha256:...
```

Envelope umožňuje spätne vysvetliť, prečo sa konkrétna memory dostala do kontextu a ktorá external authority ju potvrdila alebo vyvrátila.
""",
    """## 25. Evidence envelope

Evidence envelope zmrazí vstupy a rozhodnutia context curation pre jednu exact business operation. Nie je náhradou samotnej memory store ani dôkazom, že vybraný record je pravdivý; je to auditovateľná väzba medzi query subjectom, returned generations, authority rozhodnutím, external read-backmi, konfliktmi a contextom, ktorý model skutočne dostal. Bez envelope môže tím vidieť dnešný opravený index a nesprávne predpokladať, že rovnaký result bol dostupný aj počas incidentu.

Troubleshooting záznam pre memory decision môže mať tento tvar:

```yaml
memory_decision_id: md-8831
operation_id: checkout-recovery-017
query_subject:
  tenant: retail-eu
  service: checkout
  environment: production
retrieved_records:
  - memory_id: mem-ops-00491
    generation: 3
    authority: reviewed-episodic
    valid: true
    source_digest: sha256:...
external_readbacks:
  - subject: kubernetes/deployment/checkout
    resource_version: "8839201"
    observed_at: 2026-08-04T14:17:33Z
conflicts:
  - memory_id: mem-ops-00122
    reason: architecture_generation_mismatch
selected_context_digest: sha256:...
```

Envelope umožňuje spätne vysvetliť, prečo sa konkrétna memory dostala do kontextu a ktorá external authority ju potvrdila alebo vyvrátila. Pri replayi sa používa na rozlíšenie dvoch testov: reprodukcie pôvodného incidentu s historickými inputs a validácie recovery s novou store/index generation. Ak chýba query subject, record generation alebo selected-context digest, evidence nedokáže lokalizovať first divergence a incident zostáva iba pravdepodobnou interpretáciou.
""",
)

architecture = SECTION / "single-agent-multi-agent-architecture.md"
replace_exact(
    architecture,
    """## 5. Prečo začať single-agent návrhom

Single-agent návrh má menšiu coordination surface, jednoduchší trace, nižšiu latency a nižší token cost. Ak jeden agent s dobre navrhnutými tools a contextom spoľahlivo plní úlohu, pridanie agentov je zbytočný complexity tax.

Single-agent je vhodný najmä vtedy, keď:

- úloha používa jeden koherentný context;
- kroky sú silno závislé a ťažko paralelizovateľné;
- jeden owner má formulovať finálnu odpoveď;
- tools sa dajú bezpečne obmedziť v jednom contracte;
- latency alebo cost sú kritické;
- evals neukazujú významný benefit špecializácie.

Toto nie je zákaz multi-agent architektúry. Je to requirement, aby zložitosť mala merateľný dôvod.
""",
    """## 5. Prečo začať single-agent návrhom

Single-agent návrh má menšiu coordination surface, jednoduchší trace, nižšiu latency a nižší token cost. Ak jeden agent s dobre navrhnutými tools a contextom spoľahlivo plní úlohu, pridanie agentov je zbytočný complexity tax. Baseline nie je iba lacnejší prototyp; poskytuje porovnávací outcome, voči ktorému sa musí preukázať hodnota samostatných context windows, delegation alebo privilege separation.

Single-agent je vhodný najmä v nasledujúcich situáciách:

- **Jeden koherentný context** — všetky rozhodujúce facts a constraints patria do jedného task subjectu, takže rozdelenie by vytvorilo compression a handoff loss bez reálnej izolácie.
- **Silné sekvenčné dependencies** — každý krok potrebuje authoritative outcome predchádzajúceho kroku, preto paralelní specialists nemajú nezávislú prácu a iba duplikujú assumptions.
- **Jeden outcome owner** — jedna rola musí formulovať finálnu odpoveď, udržiavať unresolved hypotheses a niesť zodpovednosť za business postcondition; ďalší agent by rozmazal ownership.
- **Jedna bezpečnostná contract boundary** — tools a credentials možno obmedziť jedným catalogom a policy contextom, takže ďalšie agent identities neprinášajú privilege separation.
- **Prísna latency alebo cost hranica** — route, nested inference, specialist queue a synthesis by prekročili SLO alebo ekonomický budget bez primeranej kvalitatívnej návratnosti.
- **Evals nepreukazujú benefit špecializácie** — multi-agent candidate nezlepšuje business accuracy, unsupported-action rate, recovery alebo segment outcomes oproti jednoduchšiemu baseline-u.

Toto nie je zákaz multi-agent architektúry. Je to requirement, aby zložitosť mala merateľný dôvod a jasný failure, ktorý rieši. Architecture review má pomenovať očakávaný benefit, experiment, cost a rollback path; ak multi-agent variant neprinesie lepší authoritative outcome, systém zostáva pri single-agent alebo deterministic workflow návrhu.
""",
)
replace_exact(
    architecture,
    """## 30. Failure hypotheses

Pri zlyhaní multi-agent systému netreba automaticky obviniť „coordination“. First divergence môže byť v routing, context packaging, specialist contracte, state merge, model route, tool authorization alebo synthesis. Hypotézy zostávajú otvorené, kým trace a loaded topology neurčia presnú vrstvu.

- **Wrong routing** — input bol poslaný nesprávnemu alebo nedostatočnému specialistovi.
- **Missing specialist** — required domain vetva sa vôbec nespustila.
- **Duplicate delegation** — rovnaký business subtask dostal viac technical task IDs.
- **Context contamination** — specialist dostal instructions alebo data z iného domainu alebo tenanta.
- **State race** — paralelní writers prepísali shared field bez merge rule.
- **Privilege overlap** — viac agentov mohlo vykonať rovnaký side effect.
- **Synthesis loss** — supervisor odstránil conflict, uncertainty alebo source refs.
- **Cycle** — delegation graph opakoval rovnakú prácu bez nového evidence.
- **Budget fragmentation** — každý agent bol pod lokálnym limitom, ale topology prekročila global cost alebo latency budget.
- **Version skew** — supervisor a specialist používali nekompatibilné contract generations.

Každá hypotéza sa testuje proti exact run, task, agent a topology generations.
""",
    """## 30. Failure hypotheses

Pri zlyhaní multi-agent systému netreba automaticky obviniť „coordination“. Najprv sa načíta composed topology manifest a effective registry state, potom sa rekonštruuje causal task graph od jedného business operation ID cez routing, subtask IDs, technical attempts, context packages, specialist outputs, state merges a synthesis. Tým sa odlíši nesprávna architektúra od správnej topológie s jedným chybným route rozhodnutím alebo nekompatibilnou specialist generation.

Dôležité je rozlišovať počet agentov od nezávislosti dôkazov. Dva specialist outputs môžu pochádzať z rovnakého shared memory recordu, rovnakého metric query alebo leading hypothesis, takže ich zhoda nie je konsenzus. Rovnako dva technical task IDs môžu predstavovať duplicate attempts jedného business subtasku. Falsifikácia preto používa contract a context digests, source lineage, writer ownership a downstream side-effect records, nie iba finálne prose summaries.

- **Wrong routing** — input bol poslaný nesprávnemu alebo nedostatočnému specialistovi; route features a taxonomy generation ukážu, či chyba vznikla pred specialist runom.
- **Missing specialist** — required domain vetva sa vôbec nespustila; topology plan a join policy určia, či išlo o omission, timeout alebo nesprávne označenie optionality.
- **Duplicate delegation** — rovnaký business subtask dostal viac technical task IDs; objective a contract digests odhalia duplikát aj pri rozdielnom wording-u.
- **Context contamination** — specialist dostal instructions alebo dáta z iného domainu alebo tenanta; context package digest a storage access log určia prvý leak.
- **State race** — paralelní writers prepísali shared field bez merge rule; checkpoint generations a writer ownership odhalia stratený update.
- **Privilege overlap** — viac agentov mohlo vykonať rovnaký side effect; loaded tool catalogs, credentials a action ledger určia skutočný mutation surface.
- **Synthesis loss** — supervisor odstránil conflict, uncertainty alebo source refs; porovnanie typed specialist outputs so synthesis artifactom ukáže stratený evidence.
- **Cycle** — delegation graph opakoval rovnakú prácu bez nového evidence; repeated task digest a absence nových observations potvrdia stagnáciu.
- **Budget fragmentation** — každý agent bol pod lokálnym limitom, ale topology prekročila global cost alebo latency budget; parent budget ledger musí zahrnúť všetky nested attempts.
- **Version skew** — supervisor a specialist používali nekompatibilné contract generations; loaded-state read-back a schema validation určia prvú nekompatibilnú edge.

Root cause verdict pomenúva exact run, task, agent a topology generation aj prvý chybný transition. Recovery sa prijme až po replayi incidentného task graphu, benign single-agent control-e, overení jedného side-effect ownera a druhej operácii bez preneseného state-u alebo duplicate delegation.
""",
)

patterns = SECTION / "supervisor-router-specialist-patterns.md"
replace_exact(
    patterns,
    """## 5. Exact routing subject

Route decision musí byť viazaný na presný input, taxonomy generation a policy state:

```yaml
route_decision_id: route-2044-01
operation_id: checkout-incident-2044
router_generation: incident-router/v7
taxonomy_generation: ops-domains/v12
input_digest: sha256:...
auth_context_digest: sha256:...
features:
  service: checkout
  environment: production
  alert_family: latency
  affected_dependency: payment-provider
selected_routes:
  - business-metrics-specialist
  - provider-connectivity-specialist
confidence: 0.84
abstained: false
reason_codes:
  - CROSS_DOMAIN_SIGNAL
  - PAYMENT_DEPENDENCY_PRESENT
```

Bez taxonomy generation nemožno vyhodnotiť route drift po zmene kategórií alebo descriptions.
""",
    """## 5. Exact routing subject

Route decision musí byť replayable nad presným business a security subjectom, nie iba nad textom, ktorý model náhodne dostal. Input digest bez canonical features nestačí, pretože dva rovnaké alert titles môžu patriť inému tenantovi, environmentu, dependency graphu alebo risk tieru. Decision artifact preto viaže operation identity, autentifikovaný context, router a taxonomy generations, extracted features, selected destinations, confidence alebo abstain a policy reason codes.

Route decision musí byť viazaný na presný input, taxonomy generation a policy state:

```yaml
route_decision_id: route-2044-01
operation_id: checkout-incident-2044
router_generation: incident-router/v7
taxonomy_generation: ops-domains/v12
input_digest: sha256:...
auth_context_digest: sha256:...
features:
  service: checkout
  environment: production
  alert_family: latency
  affected_dependency: payment-provider
selected_routes:
  - business-metrics-specialist
  - provider-connectivity-specialist
confidence: 0.84
abstained: false
reason_codes:
  - CROSS_DOMAIN_SIGNAL
  - PAYMENT_DEPENDENCY_PRESENT
```

Runtime navyše musí zaznamenať, ktorú capability-registry generation skutočne resolve-oval pre každú route. Bez taxonomy a loaded specialist generations nemožno vyhodnotiť route drift po zmene kategórií, descriptions alebo deploymentu. Takýto artifact umožní rozlíšiť chybný feature enrichment od správneho route decisionu, ktorý neskôr zlyhal v specialistovi.
""",
)
replace_exact(
    patterns,
    """## 27. Hybrid pattern

Praktický systém často kombinuje deterministic policy router, bounded LLM router a supervisora:

```text
security and tenant policy routing
→ probabilistic domain classification
→ supervisor for complex multi-hop cases
→ specialists as read-only tools
→ approval-bound executor
```

Každá vrstva rieši inú neistotu a má vlastné telemetry.
""",
    """## 27. Hybrid pattern

Praktický systém často kombinuje viac orchestration vrstiev, ale každá musí mať odlišnú authority. Deterministický policy router najprv vynúti tenant, data-classification a forbidden-route hranice, ktoré sa nesmú meniť podľa modelového reasoning-u. Bounded LLM router potom rieši iba nejednoznačnú domain klasifikáciu a môže abstain-núť. Stateful supervisor sa aktivuje až pri multi-hop alebo cross-domain prípadoch, kde nové observations skutočne menia ďalší plán.

```text
security and tenant policy routing
→ probabilistic domain classification
→ supervisor for complex multi-hop cases
→ specialists as read-only tools
→ approval-bound executor
```

Toto poradie zabraňuje tomu, aby všeobecný supervisor získal širšie oprávnenia iba preto, že classifier nepoznal route. Specialists zostávajú read-only evidence producers a mutation authority sa objaví až v samostatnom executor contracte po syntéze a approvale. Každá vrstva má vlastnú release generation, latency a cost contribution, failure modes a telemetry, takže incident možno lokalizovať na policy enforcement, classification, planning, specialist execution alebo side-effect path namiesto neurčitého „agent zlyhal“.
""",
)
replace_exact(
    patterns,
    """## 32. Observability

Trace zachytáva:

```text
router input digest and taxonomy generation
route decision and confidence
supervisor plan version
specialist contract and context digests
parent-child run IDs
specialist tool calls and outputs
join decision
synthesis evidence graph
final action proposal and business outcome
```

Bez týchto údajov nemožno odlíšiť wrong route od specialist failure alebo synthesis loss.
""",
    """## 32. Observability

Observability musí zobraziť orchestration ako jeden causal graph, nie ako neprepojený zoznam model calls. Parent-child identity viaže router decision, supervisor plan, specialist attempts, joins a synthesis k jednému business operation ID; loaded generations a contract digests ukazujú, čo runtime skutočne vykonal. Trace sampling nesmie zahodiť failed alebo cancelled specialist attempts, pretože finálny úspešný synthesis span by potom vytvoril falošne zdravý obraz.

Trace zachytáva:

```text
router input digest and taxonomy generation
route decision and confidence
supervisor plan version
specialist contract and context digests
parent-child run IDs
specialist tool calls and outputs
join decision
synthesis evidence graph
final action proposal and business outcome
```

Každý specialist finding má source lineage a observation timestamp, aby dve summaries z rovnakého upstream evidence nevyzerali ako nezávislý konsenzus. Action proposal a business outcome zostávajú samostatné spans alebo linked records: úspešná syntéza ani HTTP 200 z executor toolu nepreukazujú obnovenú checkout konverziu. Bez týchto údajov nemožno odlíšiť wrong route od specialist failure, join omission, synthesis loss alebo downstream business failure.
""",
)
replace_exact(
    patterns,
    """## 34. Failure hypotheses

Pri nesprávnom supervisor outcome zostáva otvorených viacero failure paths. First divergence sa hľadá od input enrichmentu cez route decision, capability resolution, context packaging, specialist execution, join až po synthesis.

- **Feature omission** — router nedostal dependency, tenant, environment alebo risk signal.
- **Taxonomy overlap** — route descriptions boli nejednoznačné alebo nekompatibilné.
- **Forced classification** — router nemal abstain a zvolil nesprávnu destination.
- **Capability drift** — registry resolve-ovala inú specialist generation než release manifest.
- **Context leakage** — specialist dostal cudzie alebo leading údaje.
- **Contract violation** — specialist prekročil tools, scope, time window alebo output schema.
- **Join error** — supervisor pokračoval bez required resultu alebo čakal na nepotrebnú vetvu.
- **False consensus** — viac outputs pochádzalo z jedného upstream source alebo zdieľanej hypotézy.
- **Synthesis omission** — conflict alebo uncertainty sa stratili vo finálnom summary.
- **Hidden nested approval** — citlivá akcia zostala v specialist run-e bez parent policy.

Hypotézy sa falsifikujú loaded-state read-backom a causal trace, nie podľa posledného model outputu.
""",
    """## 34. Failure hypotheses

Pri nesprávnom supervisor outcome zostáva otvorených viacero failure paths. Diagnostika prechádza rovnaké lifecycle poradie ako produkčný request: authoritative enrichment → route artifact → capability resolution → context package → specialist execution → join → synthesis → action. V každom bode porovná desired manifest s loaded generation a zachová technical attempts aj cancelled alebo failed branches. Tým sa first divergence nehľadá podľa najhlasnejšieho specialist summary, ale podľa prvého rozdielu medzi očakávaným a skutočným state transitionom.

Falsifikácia musí rešpektovať source correlation. Dva specialists môžu opakovať rovnakú leading hypotézu zo shared contextu, router môže vybrať správnu route, ale registry resolve-ovať stale specialist generation, a validný specialist output sa môže stratiť až pri synthesis. Preto sa porovnávajú feature provenance, route reason codes, registry read-back, context a contract digests, specialist source refs, join policy a finálny evidence graph.

- **Feature omission** — router nedostal dependency, tenant, environment alebo risk signal; enrichment record ukáže, či pole chýbalo už pred modelovým dispatchom.
- **Taxonomy overlap** — route descriptions boli nejednoznačné alebo nekompatibilné; route-level eval a taxonomy generation odhalia systematický conflict.
- **Forced classification** — router nemal abstain alebo confidence policy a zvolil destination pri nedostatočnom evidence.
- **Capability drift** — registry resolve-ovala inú specialist generation než release manifest; loaded registry a nested run metadata určia effective version.
- **Context leakage** — specialist dostal cudzie tenant dáta, irelevantné instructions alebo leading hypotézu; context package digest a access logs určia contaminating edge.
- **Contract violation** — specialist prekročil allowed tools, subject, time window alebo output schema; runtime tool trace má prednosť pred self-reportom.
- **Join error** — supervisor pokračoval bez required resultu, čakal na optional vetvu alebo nesprávne interpretoval cancellation; join artifact ukáže rozhodujúci stav.
- **False consensus** — viac outputs pochádzalo z jedného upstream source, shared memory alebo zdieľanej hypotézy; evidence graph odhalí common-source lineage.
- **Synthesis omission** — conflict, uncertainty alebo source refs sa stratili vo finálnom summary; diff typed findings proti synthesis artifactu lokalizuje stratu.
- **Hidden nested approval** — citlivá akcia zostala v specialist run-e bez parent policy a operation owner nevidel interruption ani action digest.

Root cause sa prijme iba s exact operation, route, specialist a contract generations a diskriminačným dôkazom, ktorý vyradí hlavné konkurujúce hypotézy. Recovery potom replay-ne incident aj single-domain control, overí safe fallback a potvrdí, že druhá operácia nepoužije stale route, context ani approval.
""",
)

readme = SECTION / "README.md"
text = readme.read_text(encoding="utf-8")
active_anchor = "4. [Planning, decomposition a replanning](planning-decomposition-replanning.md)\n"
active_addition = active_anchor + (
    "5. [Short-term state, long-term memory a external memory](short-term-state-long-term-external-memory.md)\n"
    "6. [Single-agent a multi-agent architecture](single-agent-multi-agent-architecture.md)\n"
    "7. [Supervisor, router a specialist patterns](supervisor-router-specialist-patterns.md)\n"
    "8. [Human-in-the-loop a approval gates](human-in-the-loop-approval-gates.md)\n"
)
if active_anchor not in text:
    raise SystemExit("Section 21 active-list anchor not found")
text = text.replace(active_anchor, active_addition, 1)

for planned in (
    "5. Short-term state, long-term memory a external memory\n",
    "6. Single-agent a multi-agent architecture\n",
    "7. Supervisor, router a specialist patterns\n",
    "8. Human-in-the-loop a approval gates\n",
):
    if planned not in text:
        raise SystemExit(f"Planned README entry not found: {planned.strip()}")
    text = text.replace(planned, "", 1)

status_marker = "## Stav\n\n"
if status_marker not in text:
    raise SystemExit("Section 21 status marker not found")
status = (
    "Aktuálny authoritative stav sekcie je **8/62 · In progress**. Druhý authoritative blok aktivuje kapitoly 5–8 a incident `AGENT-OPS-02`. "
    "Memory kapitola oddeľuje thread-scoped typed state, reviewed cross-session semantic/episodic/procedural memory a external authoritative systems; zavádza exact namespace a identity, provenance, authority hierarchy, freshness, TTL a event-driven invalidation, compaction lineage, conflict resolution, poisoning controls, privacy/deletion graph a tenant-isolated second-operation acceptance. "
    "Architecture kapitola používa single-agent návrh ako default baseline a povoľuje multi-agent topológiu iba pri preukázanej potrebe context isolation, paralelizácie alebo privilege separation; definuje versioned topology manifest, state a memory ownership, delegation/output contracts, join/cancellation policy, single-writer side-effect ownera a topology-wide cost/latency budget. "
    "Pattern kapitola oddeľuje bounded router decision, stateful supervisor orchestration a specialist contract cez route taxonomy, abstain, single/multi-route fan-out, capability registry, context packaging, independent evidence, authority-aware synthesis, false-consensus detection, recursion a nested-approval propagation. "
    "Approval kapitola modeluje immutable action envelope s canonical subjectom, proposal/tool/policy generations, argument digestom, preview a evidence, reviewer identity a current authorization, separation of duties, TTL, edit/reject/escalate semantics, durable interruption, resume revalidation, duplicate-proposal control, idempotency, unknown-outcome reconciliation a business read-back. "
    "Kapitoly 5–8 sú pripravené na repository closeout; reálne memory stores, multi-agent runs, routing, approvals, identity systems, side effects, recovery drills ani business outcomes neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 9–12: durable execution, idempotency, Model Context Protocol a agent interoperability.\n"
)
text = text.split(status_marker, 1)[0] + status_marker + status
readme.write_text(text, encoding="utf-8")

roadmap = ROOT / "ROADMAP.md"
for title, target in (
    ("Short-term state, long-term memory a external memory", "short-term-state-long-term-external-memory.md"),
    ("Single-agent a multi-agent architecture", "single-agent-multi-agent-architecture.md"),
    ("Supervisor, router a specialist patterns", "supervisor-router-specialist-patterns.md"),
    ("Human-in-the-loop a approval gates", "human-in-the-loop-approval-gates.md"),
):
    replace_exact(
        roadmap,
        f"- [ ] {title}",
        f"- [x] [{title}](docs/21-ai-agents-and-intelligent-automation/{target})",
    )

ledger = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
replacement = (
    "| `21-ai-agents-and-intelligent-automation` — AI Agents and Intelligent Automation | 8/62 authoritative drafting | In progress | 2026-08-04 | "
    "Druhý authoritative blok aktivuje kapitoly 5–8 a incident `AGENT-OPS-02`. Memory kapitola oddeľuje thread-scoped typed state, reviewed cross-session semantic/episodic/procedural memory a external authoritative systems s exact namespace a identity, provenance, authority hierarchy, freshness, invalidation, compaction lineage, poisoning, privacy/deletion a tenant-isolation boundaries. Architecture kapitola používa single-agent ako default baseline a multi-agent povoľuje iba pri merateľnej potrebe context isolation, parallelism alebo privilege separation; definuje topology manifest, state/memory ownership, delegation/output contracts, join/cancellation policy, single-writer side-effect ownera a global cost/latency budget. Pattern kapitola oddeľuje bounded router, stateful supervisor a bounded specialist cez taxonomy, abstain, capability registry, context packaging, independent evidence, authority-aware synthesis, false-consensus detection, recursion a nested approvals. Approval kapitola zavádza immutable action envelope, canonical subject a digest, preview/evidence, current reviewer identity/authorization, separation of duties, TTL, durable pause/resume, drift revalidation, duplicate-proposal control, idempotency, unknown-outcome reconciliation a business read-back. Reálne memory stores, multi-agent runs, routing, approvals, identity systems, side effects, recovery drills a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
found = False
for index, line in enumerate(lines):
    if line.startswith("| `21-ai-agents-and-intelligent-automation`"):
        lines[index] = replacement
        found = True
        break
if not found:
    raise SystemExit("Section 21 ledger row not found")
ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("Remediated and synchronized Section 21 chapters 5-8 README, ROADMAP and review ledger.")
