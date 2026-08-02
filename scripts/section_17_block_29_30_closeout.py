from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "17-keycloak-and-identity-platform"

replacements = {
    SECTION / "keycloak-performance-sizing-load-testing.md": [
        (
            "## 18. Test phases\n\n```text",
            "## 18. Test phases\n\nJeden dlhý load run nevie oddeliť scenario correctness, JIT/cache warm-up, steady-state capacity, overload behavior, leak risk a recovery. Fázy preto menia presne jednu vlastnosť testu a majú vlastné SLO, stop conditions a evidence window. Až ich spojenie ukáže, či systém zvláda normálny demand, prudkú zmenu aj návrat do stabilného stavu.\n\n```text",
        ),
        (
            "## 19. Warm versus cold tests\n\n```text",
            "## 19. Warm versus cold tests\n\nWarm a cold state reprezentujú odlišné production moments. Warm run meria stabilized JIT, pools a caches, kým cold alebo mixed rollout ukazuje startup, database reload, cache fill a temporary cohort asymmetry. Capacity plan musí prijať oba outcomes, pretože incident alebo deploy môže presunúť celý traffic na cold successor.\n\n```text",
        ),
        (
            "## 24. Bottleneck signatures\n\n```text",
            "## 24. Bottleneck signatures\n\nBottleneck sa neurčuje podľa najvyššej jednej metriky, ale podľa spoločného patternu medzi arrival rate, latency, queues a resource saturation. Rovnaká high latency môže vzniknúť hashing CPU, database waitom, cache churnom alebo load-generator limitom. Signatures sú preto hypothesis shortcuts, ktoré sa musia potvrdiť one-axis comparative experimentom.\n\n```text",
        ),
        (
            "## 25. Change-one-axis discipline\n\n```text",
            "## 25. Change-one-axis discipline\n\nTuning je experiment s kauzálnou hypotézou. Ak sa súčasne zmení CPU, pool, cache a replicas, výsledok nedokáže priradiť improvement ani regression konkrétnemu mechanismu a nový limit zostane neznámy. One-axis rerun zachováva dataset, workload, topology a SLO, aby sa dala zmena reprodukovať alebo bezpečne vrátiť.\n\n```text",
        ),
    ],
    SECTION / "keycloak-troubleshooting.md": [
        (
            "## 9. `502`, `503`, `504`\n\n```text",
            "## 9. `502`, `503`, `504`\n\nTieto statusy generuje edge alebo proxy podľa rozdielnych upstream outcomes a nesmú sa zjednotiť na generic Keycloak outage. `502` typicky znamená connect/TLS/protocol failure, `503` nedostupnú alebo zámerne odmietajúcu capacity a `504` prekročený response timeout. Diagnostika preto koreluje edge error s endpoint population, Pod healthom a Keycloak request logom.\n\n```text",
        ),
        (
            "## 16. `invalid_client` a token endpoint\n\n```text",
            "## 16. `invalid_client` a token endpoint\n\n`invalid_client` je client-authentication alebo client-resolution verdict, nie dôkaz nesprávneho user passwordu. Token endpoint najprv musí nájsť exact realm/client generation, overiť enabled grant a potom credential method vrátane secretu, private-key JWT alebo mTLS. Troubleshooting preto oddeľuje client capability, credential generation a request endpoint skôr, než mení grant alebo secret.\n\n```text",
        ),
        (
            "## 19. Session, refresh a logout\n\n```text",
            "## 19. Session, refresh a logout\n\nBrowser session, Keycloak user/client session, refresh alebo offline credential, access token a local application session sú samostatné descendants. Failure alebo revocation jednej vrstvy nemusí okamžite odstrániť ostatné, preto sa symptom mapuje na exact session/token generation a consumer. Nasledujúce patterns pomáhajú odlíšiť stale bearer acceptance od refresh alebo logout lifecycle problému.\n\n```text",
        ),
        (
            "## 21. Required actions a email links\n\n```text",
            "## 21. Required actions a email links\n\nRequired-action journey spája stored pending action, signed action-token generation, hostname/theme render, SMTP delivery, browser transaction a authoritative user mutation. Zelený SMTP response alebo redirect pokrýva iba jednu časť chainu. Troubleshooting musí preto prejsť issue, delivery, validation, mutation a replay denial v rovnakom user/client context-e.\n\n```text",
        ),
    ],
}

for path, pairs in replacements.items():
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in text:
            continue
        if text.count(old) != 1:
            raise RuntimeError(f"Expected exactly one closeout marker in {path}: {old!r}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8", newline="\n")

print("Applied final Section 17 chapters 29-30 prose closeout.")
