from pathlib import Path

path = Path(__file__).resolve().parents[1] / "docs" / "17-keycloak-and-identity-platform" / "high-availability-multi-az-multi-cluster-trade-offs.md"
text = path.read_text(encoding="utf-8")

replacements = [
    (
        "### Single cluster across multiple AZs\n\n```text",
        "### Single cluster across multiple AZs\n\nTento model rozkladá serving a database capacity cez zones, ale zachováva jednu transparentnú cluster/network a regional control-plane boundary. Failover môže byť rýchly, pretože Pods patria do jedného cache clusteru, no latency, synchronous database replication a surviving-zone capacity musia zostať v podporovanom limite.\n\n```text",
    ),
    (
        "### Multi-cluster v1\n\n```text",
        "### Multi-cluster v1\n\nV1 oddeľuje Kubernetes control planes a Keycloak deployments, takže vie tolerovať failure celého clusteru. Cena za túto izoláciu je external Infinispan cross-site, explicitná site-health/fencing authority a resynchronization lifecycle; samotná shared database nestačí na safe invalidation a session behavior.\n\n```text",
    ),
    (
        "### Multi-cluster v2 / stateless\n\n```text",
        "### Multi-cluster v2 / stateless\n\nV2 presúva volatile authentication state do synchronously replicated database a odstraňuje external Infinispan cross-site. Tým zjednodušuje site failover, ale zvyšuje database write/latency sensitivity a v Keycloak 26.7 zostáva preview; support status je preto rovnako dôležitý ako architektonická jednoduchosť.\n\n```text",
    ),
    (
        "## 18. V1 versus v2 trade-off\n\n```text",
        "## 18. V1 versus v2 trade-off\n\nPorovnanie nie je iba zoznam komponentov. V1 presúva complexity do external cache, fencing-u a resync-u, ale vychádza zo supported blueprintu; v2 ju presúva do database capacity a preview feature lifecycle-u. Rozhodnutie musí preto porovnať supportability, operational burden, latency, failure recovery a upgrade risk na rovnakom workload-e.\n\n```text",
    ),
]

for old, new in replacements:
    if new in text:
        continue
    if text.count(old) != 1:
        raise RuntimeError(f"Expected exactly one HA closeout marker: {old!r}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8", newline="\n")
print("Applied final HA prose closeout.")
