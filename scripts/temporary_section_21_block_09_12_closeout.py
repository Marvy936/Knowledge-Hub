#!/usr/bin/env python3
"""Temporary closeout helper for Section 21 chapters 9-12."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs/21-ai-agents-and-intelligent-automation"


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old[:160]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# Targeted prose remediation from the first strict audit. The taxonomy remains,
# but each failure section first explains the causal layers and evidence path.
replace_exact(
    SECTION / "durable-execution-retries-resumability.md",
    """## 27. Failure hypotheses

Pri zlyhaní durable runu nie je dostatočné povedať „retry ho vykonal dvakrát“. First divergence môže byť v identity, persistence, replay determinism, timeout classification, activity contract, downstream deduplication alebo recovery read-backu.

- **History gap** — command bol odoslaný, ale durable store neobsahuje scheduling alebo acknowledgement event; treba porovnať executor request log a workflow history.
- **Operation-key drift** — retry vytvoril nový business key namiesto nového attempt ID; downstream dedup store preto prijal druhý side effect.
- **Nondeterministic replay** — nový worker pri rovnakej history zvolil inú vetvu alebo tool; dôkazom je replay failure alebo rozdielny command digest.
- **Unsafe retry classification** — timeout alebo connection reset bol označený ako definitívny failure bez status reconciliation.
- **State-version mismatch** — nový code generation nesprávne interpretoval starý pending state alebo enum.
- **Lost cancellation** — stale snapshot prebil novší cancel request a workflow pokračoval v mutácii.
- **Heartbeat misuse** — progress marker bol považovaný za business commit alebo naopak ignorovaný pri resumable worku.
- **Remote-task duplication** — reconnect vytvoril nový task namiesto resubscribe alebo `get` pôvodného tasku.
- **Compensation loop** — recovery action zlyhala a bola opakovaná bez vlastnej idempotency identity.
- **False terminal success** — orchestration skončila `completed`, ale chýbal authoritative technical a business postcondition.

Každá hypotéza sa testuje proti exact operation/run/attempt IDs, persisted history, executor ledger, downstream idempotency record a business telemetry. Log posledného workera nie je úplný causal record.
""",
    """## 27. Failure hypotheses

Pri zlyhaní durable runu nie je dostatočné povedať „retry ho vykonal dvakrát“. Diagnostika najprv zostaví časovú os jednej business operation a oddelí orchestration transition, activity scheduling, remote acknowledgement, external commit a durable result persistence. Až táto chain of custody ukáže, či druhý efekt vznikol preto, že systém stratil history, zmenil identity alebo nesprávne vyhodnotil neznámy outcome.

Druhá vrstva porovná loaded workflow a state generation s generation, ktorá vytvorila pôvodný command. Ak replay zvolil inú vetvu, nový tool alebo iný argument digest, ide o determinism alebo compatibility failure; ak replay zvolil rovnaký command, ale executor mu pridelil nový operation key, ide o side-effect identity failure. Tieto prípady majú odlišný containment aj recovery.

Napokon sa overí terminal proof boundary. Stav `completed` v orchestration store je platný iba vtedy, keď executor ledger a downstream idempotency record vysvetľujú každý attempt a authoritative technical aj business read-back potvrdí zamýšľaný outcome. Nasledujúca taxonómia preto sumarizuje konkrétne miesta, kde môže táto evidence chain prvýkrát divergovat:

- **History gap** — command bol odoslaný, ale durable store neobsahuje scheduling alebo acknowledgement event; treba porovnať executor request log a workflow history.
- **Operation-key drift** — retry vytvoril nový business key namiesto nového attempt ID; downstream dedup store preto prijal druhý side effect.
- **Nondeterministic replay** — nový worker pri rovnakej history zvolil inú vetvu alebo tool; dôkazom je replay failure alebo rozdielny command digest.
- **Unsafe retry classification** — timeout alebo connection reset bol označený ako definitívny failure bez status reconciliation.
- **State-version mismatch** — nový code generation nesprávne interpretoval starý pending state alebo enum.
- **Lost cancellation** — stale snapshot prebil novší cancel request a workflow pokračoval v mutácii.
- **Heartbeat misuse** — progress marker bol považovaný za business commit alebo naopak ignorovaný pri resumable worku.
- **Remote-task duplication** — reconnect vytvoril nový task namiesto resubscribe alebo `get` pôvodného tasku.
- **Compensation loop** — recovery action zlyhala a bola opakovaná bez vlastnej idempotency identity.
- **False terminal success** — orchestration skončila `completed`, ale chýbal authoritative technical a business postcondition.

Každá hypotéza sa testuje proti exact operation/run/attempt IDs, persisted history, executor ledger, downstream idempotency record a business telemetry. Log posledného workera nie je úplný causal record; bez prepojenia týchto artifactov sa incident nesmie uzavrieť ako „transient retry issue“.
""",
)

replace_exact(
    SECTION / "idempotency-side-effect-control.md",
    """## 33. Failure hypotheses

Pri duplicate side effecte sa hypotézy zoradia podľa identity a commit boundaries. „API ignorovalo key“ je iba jedna možnosť; chyba môže vzniknúť ešte pred API alebo v descendant systéme.

- **Key regeneration** — framework vytvoril nový key pri každom attempt-e; porovnajú sa operation a request records.
- **Scope collision** — key neobsahoval tenant, environment alebo side-effect kind a zablokoval inú legitímnu operáciu.
- **Digest omission** — server akceptoval rovnaký key s inými arguments a vrátil nesprávny existing result.
- **Non-atomic claim** — check-then-insert race dovolila dvom executorom prejsť naraz.
- **Lease without fencing** — starý owner commitol po prevzatí operation novým workerom.
- **Layered retries** — client, proxy a workflow vytvorili násobný attempt count mimo jedného budgetu.
- **Downstream gap** — primary write bol deduplikovaný, ale event, email alebo job nebol.
- **Expired tombstone** — delayed retry prišiel po purge dedup recordu.
- **Wrong reconciliation source** — eventually consistent index tvrdil `not found`, hoci authoritative ledger už obsahoval commit.
- **False success** — duplicate sa nevytvoril, ale existing result nepatril current canonical subject alebo business postcondition neplatila.

Každá hypotéza sa overuje cez key lineage, digest, claim generation, downstream ledger a effective-state read-back. Modelové vysvetlenie bez týchto artifactov nie je root cause.
""",
    """## 33. Failure hypotheses

Pri duplicate side effecte sa diagnostika nezačína posledným HTTP requestom, ale deriváciou business operation identity. Tím najprv dokáže, že všetky technické attempts mali patriť k jednej operácii, a potom porovná idempotency key, canonical argument digest a tenant/environment scope. Ak sa niektorá z týchto hodnôt zmenila, downstream systém nemal dostatok informácií na deduplikáciu, aj keby jeho implementation fungovala presne podľa contractu.

Druhá vrstva sleduje ownership od atomic claimu cez lease a fencing až po downstream commit. Dve úspešné claims ukazujú storage alebo transaction race; jedna claim s dvoma commitmi ukazuje chýbajúce fencing alebo descendant deduplication. Samostatne sa spočítajú retries v clientovi, proxy, service meshi a workflow engine, pretože lokálne limity sa môžu násobiť do retry amplification.

Posledná vrstva overí effective outcome graph. Primary write môže byť vykonaný iba raz, ale duplicate event, email, job alebo compensation stále porušuje business invariant. Nasledujúce hypotézy preto pomenúvajú presné divergence v identity, ownership, delivery a read-backu:

- **Key regeneration** — framework vytvoril nový key pri každom attempt-e; porovnajú sa operation a request records.
- **Scope collision** — key neobsahoval tenant, environment alebo side-effect kind a zablokoval inú legitímnu operáciu.
- **Digest omission** — server akceptoval rovnaký key s inými arguments a vrátil nesprávny existing result.
- **Non-atomic claim** — check-then-insert race dovolila dvom executorom prejsť naraz.
- **Lease without fencing** — starý owner commitol po prevzatí operation novým workerom.
- **Layered retries** — client, proxy a workflow vytvorili násobný attempt count mimo jedného budgetu.
- **Downstream gap** — primary write bol deduplikovaný, ale event, email alebo job nebol.
- **Expired tombstone** — delayed retry prišiel po purge dedup recordu.
- **Wrong reconciliation source** — eventually consistent index tvrdil `not found`, hoci authoritative ledger už obsahoval commit.
- **False success** — duplicate sa nevytvoril, ale existing result nepatril current canonical subject alebo business postcondition neplatila.

Každá hypotéza sa overuje cez key lineage, digest, claim generation, downstream ledger a effective-state read-back. Modelové vysvetlenie bez týchto artifactov nie je root cause a samotný pokles duplicate countu nepreukazuje opravu descendant side effectov.
""",
)

replace_exact(
    SECTION / "model-context-protocol.md",
    """## 34. Failure hypotheses

MCP incident sa diagnostikuje po vrstvách. „Server vrátil chybu“ alebo „model vybral zlý tool“ nevysvetľuje version, transport, auth, catalog, schema ani business outcome.

- **Wrong server identity** — host sa pripojil k endpointu alebo subprocessu inej generation; overí sa endpoint, executable digest a server metadata.
- **Protocol-era mismatch** — client a server interpretovali lifecycle, sessions alebo extensions rozdielne; dôkazom sú wire headers a loaded revision.
- **Stale catalog** — model/host použil starý tool schema alebo description; porovná sa catalog digest s approval a execution.
- **Capability assumption** — host volal feature, ktorá nebola negotiated alebo discoverovaná.
- **Authorization audience error** — token bol vydaný pre inú resource URI alebo scope.
- **Schema-only validation** — payload prešiel JSON Schema, ale porušil tenant, generation alebo business invariant.
- **Unsafe transport retry** — gateway zopakovala mutation po timeoute bez stable operation key.
- **Untrusted annotation** — host uveril server metadata o read-only alebo destructive behavior.
- **Task duplication** — client po reconnecte vytvoril nový tool call namiesto pollingu pôvodného tasku.
- **False protocol success** — JSON-RPC response bol success, ale effective resource alebo business outcome sa nezmenil správne.

Každá hypotéza sa testuje proti connection manifestu, wire trace, auth metadata, catalog generation, tool contract, executor ledger a business read-backu. Model transcript je iba jedna časť evidence.
""",
    """## 34. Failure hypotheses

MCP incident sa diagnostikuje od connection subjectu k business outcome-u. Connection manifest najprv určí presnú server identity, endpoint alebo executable digest, transport a loaded protocol revision. **URI** je v tomto modeli canonical identifikátor remote resource alebo servera, nie iba textová adresa; zmena URI alebo token audience môže znamenať inú trust a authorization boundary aj pri rovnakom display name.

Druhá vrstva rekonštruuje **JSON-RPC** exchange. JSON-RPC request ID koreluje jednu wire request/response dvojicu, ale nie je business operation identity ani idempotency key. Wire trace preto musí spojiť request ID s catalog/tool schema generation, canonical arguments digestom, authorization subjectom a prípadným remote taskom. Ak sa client a server nezhodli na protocol era alebo capability set-e, rovnaký JSON payload môže mať inú lifecycle alebo extension semantics.

Tretia vrstva oddeľuje **resource** a **scope**. Resource je chránený server alebo domain object, pre ktorý bol token a tool call určený; scope je povolený rozsah operácií, nie dôkaz user consentu či business policy. JSON Schema môže potvrdiť syntaktický tvar arguments, ale neoverí tenant ownership, current generation ani zamýšľaný outcome. Nasledujúce hypotézy preto sumarizujú konkrétne prvé divergence naprieč identity, protocolom, authorization, catalogom, execution a read-backom:

- **Wrong server identity** — host sa pripojil k endpointu alebo subprocessu inej generation; overí sa endpoint, executable digest a server metadata.
- **Protocol-era mismatch** — client a server interpretovali lifecycle, sessions alebo extensions rozdielne; dôkazom sú wire headers a loaded revision.
- **Stale catalog** — model/host použil starý tool schema alebo description; porovná sa catalog digest s approval a execution.
- **Capability assumption** — host volal feature, ktorá nebola negotiated alebo discoverovaná.
- **Authorization audience error** — token bol vydaný pre inú resource URI alebo scope.
- **Schema-only validation** — payload prešiel JSON Schema, ale porušil tenant, generation alebo business invariant.
- **Unsafe transport retry** — gateway zopakovala mutation po timeoute bez stable operation key.
- **Untrusted annotation** — host uveril server metadata o read-only alebo destructive behavior.
- **Task duplication** — client po reconnecte vytvoril nový tool call namiesto pollingu pôvodného tasku.
- **False protocol success** — JSON-RPC response bol success, ale effective resource alebo business outcome sa nezmenil správne.

Každá hypotéza sa testuje proti connection manifestu, wire trace, auth metadata, catalog generation, tool contract, executor ledger a business read-backu. Model transcript je iba jedna časť evidence; validný JSON-RPC success bez local postcondition je stále neuzavretý incident.
""",
)

replace_exact(
    SECTION / "agent-interoperability-protocol-evolution.md",
    """## 42. Failure hypotheses

Interoperability incident sa analyzuje od discovery po local business interpretation. Wire success je začiatok diagnostiky, nie koniec.

- **Stale Agent Card** — client routoval podľa starej skill/interface generation; porovná sa cached a served digest.
- **Version downgrade** — negotiation alebo gateway použili staršiu protocol semantics bez required controlu.
- **Binding skew** — HTTP, gRPC alebo JSON-RPC adapter mapoval state či errors rozdielne.
- **Duplicate initial message** — reconnect vytvoril nový task, pretože client message identity nebola stable.
- **Task association loss** — message použila nesprávny context/task pair a remote agent začal novú vetvu.
- **Interrupted-state collapse** — input-required alebo auth-required bolo mapované na failed/completed.
- **Artifact schema drift** — local adapter ignoroval nový field, enum meaning alebo media type.
- **Extension mismatch** — required extension bola ignorovaná alebo rozdielne versionovaná.
- **Identity propagation gap** — remote agent vykonal task pod nesprávnym user/tenant authority.
- **False semantic success** — remote completed artifact bol inconclusive alebo negative, ale local synthesis ho interpretoval ako úspech.

Každá hypotéza sa testuje cez served card, registry cache, wire/task trace, adapter mapping, artifact bytes/schema a local decision record. Prose summary remote agenta sa nepoužíva ako jediný dôkaz.
""",
    """## 42. Failure hypotheses

Interoperability incident sa analyzuje od discovery po local business interpretation. Najprv sa overí, ktorú Agent Card generation a skill contract local router skutočne načítal a ktorú interface/protocol combination použil. Ak served a cached manifest nesedia, ďalšie task alebo artifact závery sa nesmú interpretovať podľa aktuálnej dokumentácie, ale podľa generation platnej pri vytvorení delegácie.

Druhá vrstva zostaví task timeline z local delegation ID, client message ID, remote context/task ID a všetkých status transitions. Tým sa rozlíši duplicate initial send od legitímneho pokračovania existujúceho tasku a zistí sa, či adapter nezamenil interrupted stavy `input_required` alebo `auth_required` za terminal failure či completion. Binding adapter musí zachovať rovnakú semantics bez ohľadu na HTTP, gRPC alebo JSON-RPC wire formu.

Napokon sa raw artifact parts a schema interpretujú oddelene od remote prose summary. Local `completed` je iba remote task state; positive business evidence vzniká až vtedy, keď expected contract, media type, source references a status field prejdú local validation. Nasledujúce hypotézy preto pokrývajú discovery, negotiation, task identity, state mapping, artifacts a authority propagation:

- **Stale Agent Card** — client routoval podľa starej skill/interface generation; porovná sa cached a served digest.
- **Version downgrade** — negotiation alebo gateway použili staršiu protocol semantics bez required controlu.
- **Binding skew** — HTTP, gRPC alebo JSON-RPC adapter mapoval state či errors rozdielne.
- **Duplicate initial message** — reconnect vytvoril nový task, pretože client message identity nebola stable.
- **Task association loss** — message použila nesprávny context/task pair a remote agent začal novú vetvu.
- **Interrupted-state collapse** — input-required alebo auth-required bolo mapované na failed/completed.
- **Artifact schema drift** — local adapter ignoroval nový field, enum meaning alebo media type.
- **Extension mismatch** — required extension bola ignorovaná alebo rozdielne versionovaná.
- **Identity propagation gap** — remote agent vykonal task pod nesprávnym user/tenant authority.
- **False semantic success** — remote completed artifact bol inconclusive alebo negative, ale local synthesis ho interpretoval ako úspech.

Každá hypotéza sa testuje cez served card, registry cache, wire/task trace, adapter mapping, artifact bytes/schema a local decision record. Prose summary remote agenta sa nepoužíva ako jediný dôkaz a protocol conformance bez domain-contract read-backu neuzatvára semantic incident.
""",
)

readme = SECTION / "README.md"
text = readme.read_text(encoding="utf-8")
active_anchor = "8. [Human-in-the-loop a approval gates](human-in-the-loop-approval-gates.md)\n"
active_addition = active_anchor + (
    "9. [Durable execution, retries a resumability](durable-execution-retries-resumability.md)\n"
    "10. [Idempotency a side-effect control](idempotency-side-effect-control.md)\n"
    "11. [Model Context Protocol](model-context-protocol.md)\n"
    "12. [Agent interoperability a protocol evolution](agent-interoperability-protocol-evolution.md)\n"
)
if active_anchor not in text:
    raise SystemExit("Section 21 active-list anchor not found")
text = text.replace(active_anchor, active_addition, 1)

for planned in (
    "9. Durable execution, retries a resumability\n",
    "10. Idempotency a side-effect control\n",
    "11. Model Context Protocol\n",
    "12. Agent interoperability a protocol evolution\n",
):
    if planned not in text:
        raise SystemExit(f"Planned README entry not found: {planned.strip()}")
    text = text.replace(planned, "", 1)

status_marker = "## Stav\n\n"
if status_marker not in text:
    raise SystemExit("Section 21 status marker not found")
status = (
    "Aktuálny authoritative stav sekcie je **12/62 · In progress**. Tretí authoritative blok aktivuje kapitoly 9–12 a incident `AGENT-OPS-03`. "
    "Durable-execution kapitola oddeľuje business operation lifetime od process/workflow attemptu, authoritative event history alebo checkpoint, deterministic replay, activities, commit boundaries, retries, timeouts, heartbeats, durable timers, signals, pause/resume, state a code versioning, cancellation, compensation, remote tasks a unknown-outcome reconciliation. "
    "Idempotency kapitola definuje stable operation-scoped key, canonical argument digest, atomic claim, leases a fencing, effectively-once invariant, side-effect inventory a single writera, outbox/inbox, retry ownership, conditional writes, compensation identity, retention, multi-region a tenant-isolated deduplication. "
    "MCP kapitola oddeľuje host/client/server, exact server identity a protocol revision, JSON-RPC correlation od business idempotency, capability a catalog generations, tools/resources/prompts, stdio a HTTP trust boundaries, OAuth-based authorization, consent, structured results, Tasks/extensions, caching a independent business read-back. "
    "Interoperability kapitola používa A2A 1.0 model Agent Card, interfaces, skills, security requirements, message/context/task IDs, submitted/working/interrupted/terminal states, artifacts, streaming, push notifications, semantic contracts, extensions, compatibility matrix, conformance, deprecation, rolling upgrade a rollback. "
    "Kapitoly 9–12 sú pripravené na repository closeout; reálne workflow engines, durable stores, MCP/A2A servers, remote tasks, retries, side effects, protocol upgrades, recovery drills ani business outcomes neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 13–16: agent identity, least privilege, sandboxing a prompt injection cez tools alebo retrieved content.\n"
)
text = text.split(status_marker, 1)[0] + status_marker + status
readme.write_text(text, encoding="utf-8")

roadmap = ROOT / "ROADMAP.md"
for title, target in (
    ("Durable execution, retries a resumability", "durable-execution-retries-resumability.md"),
    ("Idempotency a side-effect control", "idempotency-side-effect-control.md"),
    ("Model Context Protocol", "model-context-protocol.md"),
    ("Agent interoperability a protocol evolution", "agent-interoperability-protocol-evolution.md"),
):
    replace_exact(
        roadmap,
        f"- [ ] {title}",
        f"- [x] [{title}](docs/21-ai-agents-and-intelligent-automation/{target})",
    )

ledger = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
replacement = (
    "| `21-ai-agents-and-intelligent-automation` — AI Agents and Intelligent Automation | 12/62 authoritative drafting | In progress | 2026-08-04 | "
    "Tretí authoritative blok aktivuje kapitoly 9–12 a incident `AGENT-OPS-03`. Durable execution oddeľuje operation lifetime od process/run attemptu, persisted history/checkpoint, deterministic replay, activities, commit boundaries, retry/timeout/heartbeat/timer policy, pause/resume, state a code versioning, cancellation, compensation, remote tasks a unknown-outcome reconciliation. Idempotency kapitola zavádza operation-scoped key, canonical digest, atomic claim, leases/fencing, side-effect graph a single writera, outbox/inbox, retry ownership, conditional writes, compensation identity, retention a multi-region/tenant boundaries. MCP kapitola pokrýva exact server/protocol/catalog identity, JSON-RPC, capabilities, tools/resources/prompts, transports, OAuth authorization, consent, structured results, Tasks/extensions, caching a business proof boundary. Interoperability kapitola používa A2A 1.0 Agent Cards, interfaces, skills, security requirements, message/context/task IDs, task states, artifacts, streaming/push, semantic contracts, extensions, compatibility, conformance, deprecation a upgrade/rollback. Reálne workflow engines, durable stores, MCP/A2A servers, remote tasks, retries, side effects, protocol upgrades, recovery drills a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
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

print("Synchronized and remediated Section 21 chapters 9-12.")
