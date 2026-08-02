from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "17-keycloak-and-identity-platform"

TARGETS = {
    "mfa-webauthn-passkeys-step-up-authentication.md": (
        "## 15. Positive, recovery a forbidden acceptance",
        "Acceptance musí oddelene overiť bežnú autentizáciu, obnovu po strate alebo compromise credentialu a downgrade paths, ktoré nikdy nesmú vytvoriť požadovanú assurance. Positive verdict dokazuje intended credential, flow a downstream operation; recovery verdict navyše dokazuje predecessor credential a session closure; forbidden verdict falsifikuje slabšie origin, RP, user-verification, recovery-code a adjacent-client alternatívy.",
    ),
    "password-policies-brute-force-protection-account-recovery.md": (
        "## 17. Positive, recovery a forbidden acceptance",
        "Password a recovery acceptance nie je jeden successful login. Positive path overuje policy a authoritative credential write, recovery path pridáva identity re-verification a descendant revocation a forbidden paths dokazujú, že enumeration, stale links, weak candidates, guessing a predecessor sessions nemôžu obísť successor contract.",
    ),
    "identity-brokering.md": (
        "## 18. Positive, recovery a forbidden acceptance",
        "Broker acceptance musí preukázať správny external issuer+subject, bezpečný local link a intended downstream session ako jeden chain. Recovery navyše uzatvára wrong link, stored upstream token a local descendants, zatiaľ čo forbidden paths dokazujú, že email collision, wrong issuer, low assurance alebo explicitný provider hint nevytvoria privilegovanú local identity.",
    ),
    "ldap-active-directory-federation.md": (
        "## 20. Positive, recovery a forbidden acceptance",
        "Directory acceptance musí odlíšiť správny LDAP entry/provider/UUID mapping od cached, imported a session snapshots. Positive path overuje intended login a role projection, recovery path dokazuje sync/cache/session convergence a forbidden paths testujú disabled users, removed groups, wrong replicas, provider failures a unsupported writes bez identity substitution.",
    ),
}

for name, (heading, paragraph) in TARGETS.items():
    path = SECTION / name
    text = path.read_text(encoding="utf-8")
    if paragraph in text:
        continue
    marker = heading + "\n\n"
    if marker not in text:
        raise RuntimeError(f"Missing acceptance heading in {name}: {heading}")
    text = text.replace(marker, marker + paragraph + "\n\n", 1)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"expanded {path.relative_to(ROOT)}")
