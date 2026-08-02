from pathlib import Path

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
]

for old, new in replacements:
    if new in text:
        continue
    if text.count(old) != 1:
        raise RuntimeError(f"Expected exactly one final troubleshooting marker: {old!r}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8", newline="\n")
print("Applied final Keycloak troubleshooting prose closeout.")
