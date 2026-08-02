from pathlib import Path

# Branch-only, idempotent prose closeout for the final Keycloak troubleshooting chapter.
path = Path(__file__).resolve().parents[1] / "docs" / "17-keycloak-and-identity-platform" / "keycloak-troubleshooting.md"
text = path.read_text(encoding="utf-8")

replacements = [
    (
        "## 22. Identity brokering\n\n```text",
        "## 22. Identity brokering\n\nBroker troubleshooting musí oddeliť upstream authentication, federated-link resolution a vytvorenie lokálneho Keycloak user/session state-u. Platný external token alebo SAML assertion dokazuje iba upstream identity; nedokazuje, že sa prepojil správny lokálny account, mappers aplikovali intended attributes alebo post-broker flow skončil úspešne. Evidence chain preto sleduje exact IdP configuration, upstream subject, federated link a local session generation.\n\n```text",
    ),
    (
        "## 27. Schema migration\n\n```text",
        "## 27. Schema migration\n\nSchema troubleshooting je koordinovaný binary/database problém, nie iba čítanie startup logu. Rovnaký lock alebo timeout môže znamenať zdravú dlhú migration, súbežných migration writerov, incompatible mixed-version fleet alebo už commitnutý unknown outcome. Evidence musí pred retry alebo restartom spojiť source/target versions, migration ownera, exact SQL/schema generation a rollback boundary.\n\n```text",
    ),
    (
        "## 28. Infinispan a cluster\n\n```text",
        "## 28. Infinispan a cluster\n\nCache a cluster troubleshooting začína určením, ktorý state je database-authoritative a ktorá cache/topology generation ho má sprístupniť na každom node. Node-specific stale claim môže vzniknúť split membershipom, zlyhanou `work` invalidation, rebalancingom alebo mixed cache configuration; restart node-u môže všetky štyri mechanizmy dočasne zakryť. Pred mutation preto porovnaj cluster views, topology a successor object/session behavior naprieč všetkými Pods.\n\n```text",
    ),
    (
        "## 29. Operator reconciliation\n\n```text",
        "## 29. Operator reconciliation\n\nOperator troubleshooting musí oddeliť desired CR generation, controllerom observed generation, managed child revision a usable Keycloak outcome. Ready Pod môže stále patriť stale CR generation, zatiaľ čo miznúci manual patch môže byť iba očakávaný reconcile vlastníka. Conditions, events, owner references a rollout, Secret aj image revisions sa preto čítajú spolu pred zmenou child workloadu.\n\n```text",
    ),
    (
        "## 31. Custom provider failure\n\n```text",
        "## 31. Custom provider failure\n\nProvider incident treba analyzovať ako server-binary, transaction a external-dependency failure zároveň. Startup alebo registry success nepreukazuje shared-classloader compatibility, thread safety, bounded queues ani custom schema semantics pri rollbacku. Evidence preto spája exact provider/dependency/image generation, request transaction, thread/heap state a affected external effect skôr, než sa JAR vypne alebo vráti.\n\n```text",
    ),
    (
        "## 32. Themes a localization\n\n```text",
        "## 32. Themes a localization\n\nTheme troubleshooting musí oddeliť artifact selection, parent/template inheritance, server a browser cache, rendered transaction URLs a výslednú identity mutation. Vizuálne správna password stránka nepreukazuje passkey, required-action alebo email path a stale locale override môže meniť iba jednu population. Preto sa porovnáva exact theme/JAR generation, selected realm setting, locale source a journey-specific output.\n\n```text",
    ),
    (
        "## 35. Safe containment patterns\n\n```text",
        "## 35. Safe containment patterns\n\nContainment má zastaviť ďalší impact pri čo najmenšej zmene authority a zároveň zachovať dôkazy pre root-cause analysis. Bezpečný pattern izoluje konkrétny Pod, client, tool, route alebo mutation class, má explicitný owner a rollback a nemení širšiu authentication či authorization semantics. Nasledujúce zásahy sú preto príklady bounded reduction blast radiusu, nie univerzálne recovery kroky.\n\n```text",
    ),
    (
        "## 36. Dangerous troubleshooting anti-patterns\n\n```text",
        "## 36. Dangerous troubleshooting anti-patterns\n\nNebezpečné troubleshooting kroky vytvárajú nový security alebo consistency incident skôr, než vysvetlia pôvodný symptom. Broad restart, wildcard, disabled validation alebo direct database edit môže dočasne zmeniť outcome, ale ničí evidence, rozširuje privilege path alebo vytvára nezdokumentovanú state generation. Každý taký návrh musí byť pred vykonaním odmietnutý alebo premenený na bounded, auditovaný experiment.\n\n```text",
    ),
]

for old, new in replacements:
    if new in text:
        continue
    if text.count(old) != 1:
        raise RuntimeError(f"Expected exactly one final troubleshooting marker: {old!r}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8", newline="\n")
print("Applied complete final Keycloak troubleshooting prose closeout.")
