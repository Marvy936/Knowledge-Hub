from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "17-keycloak-and-identity-platform"

replacements = {
    SECTION / "high-availability-multi-az-multi-cluster-trade-offs.md": [
        (
            "## 3. Architektonické úrovne\n\n### Single instance",
            "## 3. Architektonické úrovne\n\nJednotlivé topology sa nelíšia iba počtom Pods alebo clusters. Každá posúva failure boundary, pridáva nové shared dependencies a mení, ktorý state sa musí synchronizovať pred traffic failoverom. Nasledujúce varianty preto hodnotíme podľa tolerovaného failure domainu, authoritative database/cache/session modelu a kapacity po strate jednej časti architektúry.\n\n### Single instance",
        ),
        (
            "### Single instance\n\n```text",
            "### Single instance\n\nSingle instance je baseline bez runtime redundancy. Je vhodná iba tam, kde je výpadok processu akceptovaný a recovery sa meria ako restart alebo rebuild, nie ako transparentné pokračovanie identity journey. Backup môže znížiť data-loss risk, ale nepridáva serving capacity počas failure.\n\n```text",
        ),
        (
            "### Multi-node single cluster v jednej failure zone\n\n```text",
            "### Multi-node single cluster v jednej failure zone\n\nViac nodes odstraňuje jeden process alebo host ako jediný serving point a umožňuje rolling maintenance. Ak však všetky nodes, databáza alebo load balancer zostávajú v rovnakej failure zone, topology stále nevie prežiť zone outage; zvyšuje dostupnosť iba pre menšie failure classes.\n\n```text",
        ),
        (
            "## 12. Traffic mode: active-active vs active-passive\n\n### Active-active",
            "## 12. Traffic mode: active-active vs active-passive\n\nTraffic mode určuje, kedy sa standby capacity, state synchronization a dependencies reálne používajú. Active-active priebežne preveruje obe sites, ale vyžaduje trvalú consistency a survivor headroom; active-passive zjednodušuje normal routing, no musí samostatne dokazovať, že warm site nie je drifted alebo cold. Výber preto mení failover trigger, monitoring aj testovací cadence.\n\n### Active-active",
        ),
    ],
    SECTION / "infinispan-caches-clustering-session-behavior.md": [
        (
            "## 20. Node failure a full restart\n\nNode failure pri persistent sessions:",
            "## 20. Node failure a full restart\n\nFailure outcome závisí od authority konkrétneho state-u. Pri persistent regular sessions je cache loss performance a reload problém, kým pri volatile sessions môže byť cache loss authoritative data loss; authentication session a brute-force state majú zase vlastný persistence model. Test preto nesmie zovšeobecniť výsledok jedného refresh tokenu na všetky identity journeys.\n\nNode failure pri persistent sessions:",
        )
    ],
    SECTION / "keycloak-operator-kubernetes-deployment.md": [
        (
            "## 4. Basic `Keycloak` CR\n\n```yaml",
            "## 4. Basic `Keycloak` CR\n\nBasic CR je authoritative desired-state vstup pre Operator, nie hotový runtime manifest. First-class fields dávajú controlleru semantic context pre dependent resources, status a rollout, zatiaľ čo referenced Secrets a custom image zostávajú samostatnými generations. YAML preto čítame spolu s následným observed-generation, workload a protocol read-backom.\n\n```yaml",
        ),
        (
            "## 14. Reconcile a status conditions\n\n```bash",
            "## 14. Reconcile a status conditions\n\nReconcile evidence musí odlíšiť prijatú spec generation, controllerom spracovanú generation, vytvorený workload revision a usable Keycloak outcome. Conditions vysvetľujú controller a health state, ale nepreukazujú canonical hostname, realm initialization ani client journey. Nasledujúce príkazy preto slúžia ako prvý controller read-back, nie ako finálny acceptance verdict.\n\n```bash",
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

print("Applied focused Section 17 block 21-24 audit closeout.")
