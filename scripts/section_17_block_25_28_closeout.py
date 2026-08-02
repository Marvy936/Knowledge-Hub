from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "17-keycloak-and-identity-platform"

replacements = {
    SECTION / "backup-restore-realm-import-export-disaster-recovery.md": [
        (
            "## 18. Restore validation ladder\n\n```text",
            "## 18. Restore validation ladder\n\nRestore sa neakceptuje jedným health checkom, pretože každá vyššia vrstva závisí od predchádzajúcej a zároveň pridáva vlastnú authority. Ladder začína integritou backup artifactu, pokračuje durable schema a runtime generation a končí protocolom, sessions, auditom a business outcome. Failure na ktoromkoľvek stupni zastaví route activation, aj keď nižšie technické checks zostali zelené.\n\n```text",
        )
    ],
    SECTION / "custom-providers-spi-extension-lifecycle.md": [
        (
            "## 7. Packaging a optimized build\n\n```Dockerfile",
            "## 7. Packaging a optimized build\n\nProvider artifact sa nestáva aktívnym iba skopírovaním JAR-u do filesystemu. Build musí spojiť exact Keycloak base, provider a dependency bytes, service descriptors a build-time SPI selection do jednej immutable optimized image generation. Až runtime registry a behavior test dokazujú, že nasadený server používa intended provider namiesto built-in fallbacku alebo stale predecessor registry.\n\n```Dockerfile",
        ),
        (
            "## 10. Lifecycle methods\n\n```text",
            "## 10. Lifecycle methods\n\nLifecycle určuje, ktoré resources sú process-wide, ktoré request-scoped a kedy je bezpečné ich vytvoriť alebo zatvoriť. Factory môže obsluhovať concurrent requests a nesie iba thread-safe shared state; provider instance používa konkrétny `KeycloakSession` a nesmie prežiť jeho transaction. Nasledujúce callbacks preto tvoria ownership a cleanup contract, nie iba poradie frameworkových metód.\n\n```text",
        ),
        (
            "## 21. Testing ladder\n\n```text",
            "## 21. Testing ladder\n\nProvider testovanie musí postupne zvyšovať realizmus, pretože compile ani mocked session neodhalia shared classloader, optimized registry, database transaction, cache alebo external backpressure behavior. Každý stupeň pridáva nový failure domain a uchováva exact target Keycloak/provider/dependency generation. Release môže prejsť až po node/upgrade a target-next-version rehearsal, nie po prvom úspešnom requeste.\n\n```text",
        ),
    ],
    SECTION / "securing-apis-microservices-mcp-servers.md": [
        (
            "## 9. Role, scope a permission semantics\n\n```text",
            "## 9. Role, scope a permission semantics\n\nTieto štyri pojmy môžu používať rovnaký textový názov, ale vznikajú v odlišnej authority a dokazujú odlišnú vec. OAuth scope opisuje granted client capability, role je Keycloak entitlement, Authorization Services permission je PDP decision a local permission je finálny business-resource verdict. API musí preto fixovať namespace, issuer a writer každého claimu skôr, než ho porovná s endpoint policy.\n\n```text",
        ),
        (
            "## 14. Error semantics\n\n```text",
            "## 14. Error semantics\n\nHTTP status je súčasť security contractu, nie iba UX detail. `401` signalizuje, že request nemá prijateľnú credential identity; `403` znamená validnú identity bez požadovanej local permission a `404` môže zámerne skryť foreign-resource existence. Konzistentná voľba riadi client retry, reauthentication, audit aj ochranu pred enumeration.\n\n```text",
        ),
        (
            "## 23. MCP scopes a local tool policy\n\n```text",
            "## 23. MCP scopes a local tool policy\n\nMCP scopes definujú hrubú capability surface, nie automatické povolenie každého toolu, resource alebo promptu. Server musí po scope gate-e vykonať local decision nad callerom, tenantom, exact operation name-om, arguments/resource ownershipom a risk contextom. Tým sa z MCP servera nestane confused deputy, ktorý broad capability premení na neobmedzený downstream access.\n\n```text",
        ),
    ],
    SECTION / "upgrades-migration-guides-rollback-boundaries.md": [
        (
            "## 12. Acceptance inventory\n\nMinimálne journeys:",
            "## 12. Acceptance inventory\n\nUpgrade acceptance musí reprezentovať skutočné identity paths a state descendants, nie iba server startup alebo jeden local login. Inventory pokrýva protocol families, sessions, external identity authorities, machine clients, administration, extensions a operational evidence, aby successor generation nebola zelená iba v nepoužívanej happy path. Každá journey fixuje predecessor/successor subject a positive aj forbidden outcome.\n\nMinimálne journeys:",
        ),
        (
            "## 21. Rollback decision point\n\nPred rolloutom definuj stop conditions:",
            "## 21. Rollback decision point\n\nRollback je bezpečný iba do okamihu, keď successor zmení state spôsobom, ktorý predecessor nevie čítať alebo korektne meniť. Decision point preto kombinuje technické stop conditions s časovou hranicou pred irreversible schema, provider-data alebo client behavior changes. Po jej prekročení sa incident nesmie riešiť reflexívnym image rollbackom, ale vopred zvoleným forward fixom alebo coordinated restore-om.\n\nPred rolloutom definuj stop conditions:",
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

print("Applied focused Section 17 block 25-28 prose closeout.")
