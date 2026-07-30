#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/17-keycloak-and-identity-platform"


def replace_section(path: Path, heading: str, next_heading: str, body: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.index(heading)
    end = text.index(next_heading, start)
    replacement = heading + "\n\n" + body.strip() + "\n\n"
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8", newline="\n")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"Expected one replacement marker in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


oidc = DOCS / "oidc-clients-redirect-uris-scopes-pkce.md"
replace_section(
    oidc,
    "## 1. Dominantný registration-to-session model",
    "## 2. Exact OIDC client subject",
    r'''
OIDC client registration je server-side policy object, ktorý musí zostať kontinuálne viazaný na konkrétnu application generation. Najprv sa určí vlastník a protected journey, potom realm issuer, client type, redirect destinations, browser transaction controls, grants, scopes a token consumers. Keycloak tieto values použije počas authorization a token exchange-u; client a resource server následne vykonajú vlastnú validation a authorization.

```text
application ownership a protected journey
→ exact realm issuer a OIDC client generation
→ client type, authentication method a enabled grants
→ exact redirect URI a web-origin contract
→ authorization transaction: state, nonce a PKCE
→ Keycloak authentication a consent/policy
→ authorization code via browser redirect
→ token endpoint client/PKCE validation
→ ID/access/refresh token generation
→ client-side issuer/audience/nonce validation
→ local application session
→ resource-server authorization
→ refresh, logout, revocation a second-login validation
```

Žiadna jednotlivá zelená fáza nepreukazuje celý outcome. Keycloak môže bezpečne vydať code, ale broad redirect ho doručí cudziemu hostu; client môže validovať ID Token, ale API dostane access token bez správnej audience; browser logout môže skončiť, ale starý bearer token zostane platný. Registration generation preto musí byť viazaná na application release aj downstream validation contract.

Ak frontend release používa callback `/oauth/callback`, ale Keycloak stále povoľuje historický wildcard, effective trust určuje širší server-side allowlist. Druhý client alebo druhý environment musí mať samostatný subject a negative test; kopírovanie registration bez nového reviewu prenáša staré privilege a redirect assumptions.
''',
)
replace_section(
    oidc,
    "## 17. Acceptance matrix",
    "## 18. Troubleshooting flow",
    r'''
Acceptance matrix nie je zoznam smoke testov. Je to dôkaz, že rovnaká exact client generation povoľuje intended browser, token a API path a súčasne odmieta substitúcie, ktoré v incidente `KC-PAY-65` vytvorili privilege. Každý test musí zachovať realm issuer, client UUID/ID, redirect, PKCE transaction, token claims, local session a resource outcome, aby zelený výsledok nepatril inej konfigurácii.

Pozitívna vetva overuje použiteľnosť a least privilege:

- **Exact production redirect** — Keycloak doručí authorization code iba na `https://payments-admin.atlas.example/oauth/callback`; test následne overí, že callback patrí k pôvodnej `state` transaction.
- **PKCE `S256` exchange** — client s pôvodným verifierom vymení code presne raz; token endpoint tým dokáže väzbu na client instance, nie iba znalosť code-u.
- **Minimálna token projection** — intended user dostane iba schválenú audience, scopes a `payments-admin` client roles; unrelated realm alebo partner role sa v tokene nenachádza.
- **End-to-end protected journey** — client validuje ID Token, vytvorí local session a API prijme access token iba pre povolený tenant, action a workflow state.
- **Lifecycle behavior** — refresh rotation, idle/max session a logout vytvoria očakávané descendants a audit events bez toho, aby rozšírili token lifetime.

Negatívna vetva overuje security boundary a recovery:

- **Foreign redirect** — sibling preview subdomain a iný path sú odmietnuté ešte pred vydaním code-u; to dokazuje, že wildcard z incidentu už nie je effective.
- **PKCE downgrade alebo substitution** — request bez challenge, metóda `plain`, wrong verifier a druhý exchange toho istého code-u zlyhajú bez vydania tokenu.
- **Wrong trust subject** — wrong client, wrong realm issuer a token s wrong audience sú odmietnuté na príslušnej client alebo API boundary.
- **Privilege non-projection** — user môže mať unrelated effective realm role, ale role scope a mapper ju nesmú vložiť do tokenu tohto clienta.
- **Incident revocation** — starý access token, refresh descendant aj local cookie po revocation nedokážu privileged operation; browser návrat na login stránku sám osebe nestačí.

Verdict je green až vtedy, keď všetky positive aj forbidden paths patria rovnakej candidate generation. Ak test iba prejde cez login UI, ale nezachová token audience, role diff a API result, výsledok je neúplný a nesmie povoliť production rollout.
''',
)
replace_once(
    oidc,
    "Browser redirect neoveruje access token ani application session invalidation.",
    "Browser redirect neoveruje access token ani application session invalidation. Tento anti-pattern vytvára false recovery verdict: používateľ vidí login stránku, zatiaľ čo ukradnutý bearer token alebo server-side application session stále vykonáva business operácie.",
)

realm = DOCS / "realm-client-user-group-role-session.md"
replace_once(
    realm,
    "Po sign-out-e zmizla Keycloak browser session. OIDC access token a local SAML application session však pokračovali. Incident ukázal tri odlišné defects:\n\n1. group hierarchy bola použitá ako permission hierarchy;\n2. realm role bola použitá pre client-specific privilege;\n3. session revocation sa skončila pri Keycloak SSO state-e.",
    "Po sign-out-e zmizla Keycloak browser session. OIDC access token a local SAML application session však pokračovali. Incident ukázal tri kauzálne odlišné defects, ktoré treba opraviť na troch boundaries:\n\n1. **Group hierarchy sa stala permission hierarchy** — contractor zdedil privilege z organizačného parenta, hoci direct-role audit bol čistý; náprava preto musí oddeliť organization group od dedicated access group.\n2. **Realm role reprezentovala client-specific privilege** — `settlement-admin` sa dostala do OIDC aj SAML projection; náprava používa client roles a explicitné role scope mappings.\n3. **Revocation skončila pri Keycloak SSO state-e** — sign-out odstránil browser session, ale nie už vydaný token ani local SP session; recovery musí prejsť celý session descendant graph.",
)

saml = DOCS / "saml-clients-metadata-assertions-bindings.md"
replace_section(
    saml,
    "## 8. IdP-initiated flow a unsolicited Response",
    "## 9. Signing direction a signature requirements",
    r'''
IdP-initiated login vzniká bez predchádzajúceho SP AuthnRequest-u. Keycloak preto nemôže vložiť `InResponseTo` väzbu na pending SP transaction a Service Provider nemá pôvodný request, z ktorého by odvodil expected client, Assertion Consumer Service, return destination a requested assurance. Tento flow môže byť potrebný pre legacy launcher, ale používa slabší login-intent model než SP-initiated SSO.

Bezpečný návrh musí nahradiť chýbajúci request context explicitným a úzkym contractom. Keycloak vyberie presne jeden target client a jeho allowlisted default ACS; Service Provider prijme unsolicited Response iba na dedikovanom path-e a nepoužije arbitrary `RelayState` ako tenant, role alebo open-redirect authority. Response a Assertion IDs idú do shared replay cache, pretože validná podpísaná bearer assertion nesmie vytvoriť druhú local session.

Controls majú samostatné úlohy:

- **Exact target client a default ACS** — IdP launcher nesmie dynamicky vybrať iný privileged client alebo neinventarizovaný callback.
- **Bounded `RelayState`** — hodnota odkazuje iba na server-side allowlisted return state; neobsahuje neoverený tenant ani externú URL.
- **Replay a login-CSRF control** — SP spotrebuje Response/Assertion IDs raz a viaže vytvorenie session na očakávaný browser/login intent podľa vlastného launcher contractu.
- **Client-specific mapper** — assertion obsahuje iba NameID a attributes, ktoré tento SP smie authoritative konzumovať; broad effective realm roles sa nepublikujú.
- **Local authorization a revocation** — SP po assertion validation stále overí tenant a resource permission a musí vedieť server-side zrušiť local session nezávisle od SLO.

Privileged admin applications majú preferovať SP-initiated flow. Ak IdP-initiated path zostane, patrí do samostatného low-risk clienta a acceptance matrix musí preukázať, že unsolicited Response pre privileged clienta je odmietnutá. Samotná schopnosť Keycloaku tento flow emitovať nie je bezpečnostné zdôvodnenie.
''',
)
replace_section(
    saml,
    "## 13. Audience, Destination, Recipient a time",
    "## 14. Keycloak session a downstream SAML session",
    r'''
Keycloak ako Identity Provider generuje viacero navzájom dopĺňajúcich bindings. Service Provider ich musí vyhodnotiť voči jednej pending transaction a jednej client/metadata generation; validácia iba podpisu necháva otvorenú substitúciu medzi clients, endpoints alebo starými responses. Každé pole odpovedá na inú otázku o intended consumerovi, transport destination, bearer presentation, request correlation a časovej platnosti.

- **`AudienceRestriction` — logical SP identity.** Hodnota musí obsahovať exact entity ID clienta, pre ktorý assertion vznikla; assertion pre sibling SP sa nesmie prijať iba preto, že používa rovnaký certificate.
- **`Destination` — protocol Response endpoint.** SP porovná externú URL, na ktorú bola Response adresovaná, s aktuálnym request endpointom po trusted proxy normalization.
- **`Recipient` — povolený ACS pre bearer assertion.** SubjectConfirmation musí smerovať na konkrétny Assertion Consumer Service; iný shared alebo historický ACS je substitution failure.
- **`InResponseTo` — pending AuthnRequest.** SP nájde request ID v shared transaction store a atomicky ho spotrebuje; missing väzba je povolená iba v osobitnom IdP-initiated contracte.
- **`NotBefore` a `NotOnOrAfter` — bounded validity.** SP používa monitorovanú malú clock-skew toleranciu a rešpektuje exclusive expiry boundary, aby nepredĺžil stolen-assertion window.
- **`SessionIndex` — session/logout correlation.** Identifier pomáha spojiť assertion s Keycloak a SP session state-om, ale sám neautorizuje business action ani negarantuje úspešné SLO.

Tieto fields nie sú duplicitné. Wrong audience znamená client substitution, wrong destination alebo recipient callback confusion, missing `InResponseTo` zmenu transaction modelu a veľká časová tolerancia replay risk. Acceptance preto musí meniť každú hodnotu samostatne a potvrdiť, že SP odmietne práve tú chybnú boundary.
''',
)
replace_section(
    saml,
    "## 17. SAML redesign",
    "## 18. Metadata a key rollover test",
    r'''
Redesign odstraňuje implicitný shared-client model a vytvára jeden reprodukovateľný federation contract pre privileged SP. Každá zmena entity ID, endpointu, keyu alebo mappera je nová client generation, ktorá musí prejsť metadata diffom a protocol canary pred produkčným použitím.

```text
unique production SP entity ID
→ reviewed metadata artifact
→ exact ACS a SLO endpoints
→ SP-initiated flow pre privileged login
→ signed AuthnRequest required
→ InResponseTo a shared replay/transaction store
→ Keycloak realm/client-specific signing keys
→ client-role allowlist mapper
→ persistent non-email subject identifier
→ SP tenant/object authorization
→ server-side local session revocation
```

Tento chain presúva tenant a privilege decision z `RelayState` a broad realm role na exact client, allowlisted mapper a downstream resource policy. Signed request chráni client-controlled request fields, `InResponseTo` obnovuje transaction binding a server-side SP revocation poskytuje recovery aj počas SLO outage-u.

Ak IdP-initiated path zostane pre low-risk portal, použije samostatného clienta, default landing page bez privilege, bounded `RelayState` a samostatný acceptance test. Nesmieme ho pridať ako alternate path k privileged clientovi, pretože by znovu obišiel pending request a jeho assurance contract.
''',
)
replace_section(
    saml,
    "## 18. Metadata a key rollover test",
    "## 19. Acceptance matrix",
    r'''
Rollover je distribuovaná trust transition medzi Keycloakom, metadata publication, všetkými SP replicas a in-flight assertions. Cieľom nie je iba „nový certificate je uložený“, ale kontinuálna schopnosť overiť správne assertions počas overlapu a definitívne odmietnuť starý key po retirement-e. Rehearsal používa exact old/new key generations a zachováva, ktorý verifier načítal ktorú metadata revision.

1. **Publish new verification material.** Keycloak IdP metadata obsahujú nový signing certificate spolu so starým počas plánovaného overlapu; metadata hash a validity sa archivujú.
2. **Converge every SP verifier.** Každá SP replica načíta old aj new certificate a read-back potvrdí loaded generation, nie iba úspešný configuration push.
3. **Switch active signing key.** Keycloak začne podpisovať novým keyom a canary assertion nesie jeho expected certificate alebo key identity.
4. **Verify new assertions fleet-wide.** Rovnaký SP-initiated journey prejde cez každú SP replica, aby load balancer neskryl stale verifier.
5. **Preserve bounded old validity.** Assertion podpísaná starým keyom pred cutoverom zostane overiteľná iba do svojej pôvodnej expiry a overlap limitu; nové assertions už starý key nepoužívajú.
6. **Retire after convergence.** Starý certificate sa odstráni z metadata a verifier trustu až po expiry in-flight artifacts a potvrdenej fleet convergence.
7. **Prove forbidden old path.** Čerstvo vytvorená alebo replaynutá assertion podpísaná retired keyom je odmietnutá a nevytvorí local session.

Encryption rollover vykoná zrkadlový test pre SP decryption keys: Keycloak musí šifrovať new public keyom až po tom, čo všetky SP replicas načítali corresponding private key, a old private key sa odstráni až po drain-e in-flight responses. Ak ktorýkoľvek verifier nevie reportovať loaded generation, rollover verdict zostáva unknown.
''',
)
replace_section(
    saml,
    "## 19. Acceptance matrix",
    "## 20. Troubleshooting flow",
    r'''
SAML client je accepted iba vtedy, keď jedna exact metadata a client generation vytvorí správnu SP-initiated session a odmietne client, endpoint, message a key substitutions. Test musí korelovať AuthnRequest ID, Keycloak client UUID, Response/Assertion IDs, signed node, audience/destination/recipient, NameID/attributes, Keycloak SessionIndex, local SP session a protected resource result.

Pozitívna vetva overuje celý intended lifecycle:

- **Signed SP-initiated request** — AuthnRequest s exact issuerom, registered ACS, approved bindingom a trusted SP signature sa priradí správnemu Keycloak clientovi.
- **Bound response semantics** — Response nesie expected audience, destination, recipient, validity a `InResponseTo`; SP pending request nájde a spotrebuje presne raz.
- **Authoritative subject a attributes** — NameID má dohodnutý format a stable source, attributes majú expected type/cardinality a mapper nepublikuje unrelated roles.
- **Least-privilege local session** — SP vytvorí account/session iba pre intended tenant a client-specific permission; resource authorization overí konkrétnu action a object state.
- **Lifecycle closure** — logout alebo incident revocation zruší Keycloak client session aj local SP session podľa contractu a zanechá auditovateľný partial-failure state.

Negatívna vetva dokazuje boundaries:

- **Wrong client alebo endpoint** — unknown entity ID, unregistered ACS, wrong destination alebo recipient sú odmietnuté bez vytvorenia session.
- **Request-integrity failure** — unsigned alebo nesprávne podpísaný AuthnRequest je odmietnutý, keď client signature required.
- **Unsolicited privileged response** — IdP-initiated Response pre privileged clienta zlyhá, pretože chýba povolený alternate contract a pending request.
- **Semantic alebo replay failure** — wrong audience, expired/not-yet-valid assertion, wrong `InResponseTo` a reused Response/Assertion ID sú odmietnuté aj pri validnej XML signature.
- **Privilege non-projection** — inherited unrelated realm role sa v AttributeStatement nenachádza a SP ju nevie získať cez missing-value fallback.
- **Retired-key denial** — assertion podpísaná old keyom po retirement-e zlyhá na každej SP replica, nie iba na jednej canary node.
- **SLO outage recovery** — nedostupný Single Logout endpoint nezabráni server-side invalidácii local session a downstream business accessu.

Green verdict vyžaduje obe vetvy. Login demo bez actual assertion inspection a protected-resource checku preukazuje iba to, že browser prešiel cez Keycloak, nie že federation contract je bezpečný.
''',
)

subprocess.run(["python", "scripts/update_navigation.py", "--write"], cwd=ROOT, check=True)
subprocess.run(["python", "scripts/audit_learning_depth.py", "--all-docs"], cwd=ROOT, check=True)
subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)

audit = json.loads((ROOT / "documentation-audit.json").read_text(encoding="utf-8"))
paths = {
    "docs/17-keycloak-and-identity-platform/keycloak-architecture-and-responsibility-boundary.md",
    "docs/17-keycloak-and-identity-platform/realm-client-user-group-role-session.md",
    "docs/17-keycloak-and-identity-platform/oidc-clients-redirect-uris-scopes-pkce.md",
    "docs/17-keycloak-and-identity-platform/saml-clients-metadata-assertions-bindings.md",
}
rows = [entry for entry in audit.get("files", []) if entry.get("path") in paths]
if {entry.get("path") for entry in rows} != paths:
    raise SystemExit("Incomplete audit inventory")
for entry in rows:
    print(f"AUDIT {entry['path']}: words={entry['words']} critical={entry['critical']} high={entry['high']} medium={entry['medium']} low={entry['low']} grade={entry['grade']}")
    if entry["critical"] or entry["high"] or entry["medium"]:
        raise SystemExit(f"Strict depth gate failed: {entry['path']}")

for path in [
    ROOT / "scripts/remediate_keycloak_block1_depth.py",
    ROOT / ".github/workflows/keycloak-block1-remediation.yml",
    ROOT / "docs/keycloak-block1-remediation-trigger.md",
]:
    path.unlink(missing_ok=True)
