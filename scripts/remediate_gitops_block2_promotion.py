from pathlib import Path


def load(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def save(path: str, text: str) -> None:
    Path(path).write_text(text, encoding="utf-8", newline="\n")


def insert_after_heading(text: str, heading: str, prose: str, marker: str) -> str:
    if marker in text:
        return text
    needle = heading + "\n\n"
    if needle not in text:
        raise SystemExit(f"Missing heading: {heading}")
    return text.replace(needle, needle + prose.rstrip() + "\n\n", 1)


def replace_line(text: str, old: str, new: str) -> str:
    if new in text:
        return text
    needle = old + "\n"
    if needle not in text:
        raise SystemExit(f"Missing line: {old}")
    return text.replace(needle, new + "\n", 1)


path = "docs/16-gitops-and-platform-engineering/application-promotion.md"
text = load(path)

text = insert_after_heading(
    text,
    "## 5. Candidate identity a evidence bundle",
    """Evidence bundle je rozhodovací input, nie archív ľubovoľných zelených výsledkov. Každý dôkaz musí niesť subject identity, execution context, čas a policy version, aby promotion engine vedel rozhodnúť, či je stále použiteľný pre konkrétny target.

Jednotlivé evidence classes pokrývajú rozdielne failure boundaries. Ich prítomnosť sama nestačí; promotion policy musí vysvetliť, ktorý risk uzatvárajú a ktoré target-specific riziká zostávajú otvorené.""",
    "Evidence bundle je rozhodovací input",
)

for old, new in [
("- build provenance a artifact signature;",
 "- **Build provenance a artifact signature** — viažu digest na source, builder a build inputs a umožňujú overiť, že candidate nebol po vytvorení nahradený inými bytes."),
("- SBOM a vulnerability decision;",
 "- **SBOM a vulnerability decision** — identifikujú component inventory a dokumentujú, ktoré findings sú blokujúce, remediované alebo prijaté s ownerom a expiry."),
("- unit, integration, contract, component a E2E results;",
 "- **Unit, integration, contract, component a E2E results** — pokrývajú rozdielne failure boundaries od lokálnej logiky po inter-service a user journey behavior; výsledok musí odkazovať na exact candidate."),
("- migration compatibility a rollback eligibility;",
 "- **Migration compatibility a rollback eligibility** — dokazujú, či mixed versions, schema transitions a data state dovolia bezpečný rollout alebo návrat application vrstvy."),
("- staging reconciliation revision a exact running digests;",
 "- **Staging reconciliation revision a exact running digests** — preukazujú, že testované staging Pods skutočne vykonávali candidate digest a konfiguráciu uvedenú v evidence bundle."),
("- load/capacity evidence pri relevantnej configuration;",
 "- **Load a capacity evidence** — platí iba pre testovanú configuration, dependency limits a traffic model; bez nich sa nedá preniesť na odlišný production scale."),
("- operational readiness a monitoring coverage;",
 "- **Operational readiness a monitoring coverage** — dokazujú, že release má version-aware telemetry, alerting, runbook a recovery path potrebné počas rollout-u."),
("- business canary result;",
 "- **Business canary result** — overuje konkrétny customer alebo settlement outcome nad identifikovaným cohortom, nie iba technickú dostupnosť endpointu."),
("- unresolved exceptions, expiry a ownera.",
 "- **Unresolved exceptions** — musia uvádzať residual risk, ownera, scope a expiry, aby temporary waiver neprežila zmenu candidate-u alebo targetu bez nového rozhodnutia."),
]:
    text = replace_line(text, old, new)

text = insert_after_heading(
    text,
    "## 7. Pull request ako promotion transaction",
    """Promotion PR funguje iba vtedy, keď review zobrazuje effective change, nie syntaktický rozdiel jedného values file-u. Reviewer musí vedieť prepojiť candidate identity s target base state-om, transitive dependencies a recovery consequence.

Nasledujúce dimensions tvoria jeden review subject. Ak sa niektorá z nich po approval-e zmení, final merge už nie je tou istou autorizovanou transaction a musí sa znovu vyrenderovať a vyhodnotiť.""",
    "Promotion PR funguje iba vtedy",
)

for old, new in [
("- digest a provenance identity;",
 "- **Digest a provenance identity** — dokazujú, ktoré immutable bytes PR povoľuje a z ktorého trusted build chainu vznikli."),
("- environment-specific rendered delta;",
 "- **Environment-specific rendered delta** — ukazuje final objects a values po overlays, defaults a generators, takže reviewer neposudzuje iba incomplete source fragment."),
("- resource, policy, route a secret-reference changes;",
 "- **Resource, policy, route a secret-reference changes** — odhaľujú behavior a privilege zmeny, ktoré sa nemusia prejaviť v application image digest-e."),
("- migration a compatibility implications;",
 "- **Migration a compatibility implications** — vysvetľujú mixed-version, schema, event a rollback constraints, ktoré určujú bezpečné ordering a recovery."),
("- exposure/rollback plan;",
 "- **Exposure a rollback plan** — definuje cohort, transition gates a per-layer recovery, nie iba príkaz na zmenu image späť."),
("- evidence freshness;",
 "- **Evidence freshness** — potvrdzuje, že testy, scans a staging verdict stále patria current candidate-u, dependency graphu a policy version."),
("- current target base revision.",
 "- **Current target base revision** — vytvára compare-and-swap precondition, aby PR neprebil concurrent production change alebo sa nerebase-ol na netestovanú combination."),
]:
    text = replace_line(text, old, new)

text = insert_after_heading(
    text,
    "## 8. Stale promotion race",
    """Stale race vzniká preto, že evidence, proposal a merge sú oddelené časom a mutable state-om. Approval je platný iba dovtedy, kým zostáva nezmenený celý subject, ktorý reviewer videl; automatický rebase preto nie je neutrálna technická operácia.

Promotion service musí pred authoritative transitionom vykonať compare-and-swap-like kontrolu. Každá precondition chráni inú časť identity continuity a jej porušenie musí proposal vrátiť do validation, nie ho ticho preniesť na nový base.""",
    "Stale race vzniká preto",
)

for old, new in [
("- expected source environment commit;",
 "- **Expected source environment commit** — viaže evidence na staging desired state, z ktorého bol candidate skutočne nasadený a testovaný."),
("- expected candidate digest;",
 "- **Expected candidate digest** — zabraňuje, aby mutable tag, shared base alebo image automation po approval-e nahradili testované bytes."),
("- expected target environment base commit;",
 "- **Expected target base commit** — deteguje concurrent production mutation a zabraňuje lost update-u alebo neoverenej kombinácii dvoch proposals."),
("- expected policy/evidence versions;",
 "- **Expected policy a evidence versions** — invalidujú approval, keď sa zmení decision logic, scanner database, exception alebo test result."),
("- no unreviewed transitive dependency change;",
 "- **No unreviewed transitive dependency change** — chráni chart, policy, schema, route a secret-reference graph, ktorý môže meniť behavior aj bez zmeny image digestu."),
("- re-render final merge result.",
 "- **Final-merge re-render** — vypočíta exact manifests a policy verdict po merge resolution, čím potvrdí, že authoritative commit stále zodpovedá reviewed proposal-u."),
]:
    text = replace_line(text, old, new)

text = insert_after_heading(
    text,
    "## 20. Promotion acceptance verdict",
    """Promotion acceptance spája decision-plane a runtime-plane evidence. Nestačí, že proposal prešiel policy alebo že GitOps controller nasadil nejakú revision; musí ísť o tú istú immutable candidate generation, ktorú autorizoval fresh target-specific decision.

Podmienky nižšie preto overujú identity continuity, concurrency safety, stateful compatibility a recovery. Ich spoločným výsledkom je, že neskorý retry, rebase, superseded proposal alebo rollback nemôžu vytvoriť inú effective release bez nového authoritative rozhodnutia.""",
    "Promotion acceptance spája decision-plane",
)
save(path, text)
