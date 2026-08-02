# MFA, WebAuthn, passkeys a step-up authentication

MFA v Keycloak-e nie je vlastnosť používateľa typu „má zapnuté OTP“. Je to výsledok konkrétnej authentication transaction, v ktorej exact flow generation vyhodnotila credentials, user session, client, requested authentication context a recovery alternatives. User môže mať TOTP aj passkey a napriek tomu získať privileged token iba z remembered SSO cookie, brokered loginu alebo nesprávne namapovaného authentication levelu. Naopak príliš rigidný flow môže používateľa bez enrolled credential zablokovať alebo mu počas rovnakého loginu dovoliť credential zaregistrovať a okamžite ju považovať za nezávislý druhý faktor.

WebAuthn a passkeys treba rozlišovať podľa role credentialu. `WebAuthn Authenticator` sa typicky používa ako druhý faktor po identifikácii a prvom faktore. `WebAuthn Passwordless Authenticator` môže používateľa autentizovať bez hesla; discoverable credential môže navyše umožniť login bez predchádzajúceho username inputu. Passkey je WebAuthn discoverable public-key credential s user-verification schopnosťou a môže byť synchronizovaná platformovým credential providerom. Kryptografická validita assertion však sama nepreukazuje intended client, tenant, LoA ani povolenie konkrétnej business operation.

## 1. Dominantný credential-to-assurance lifecycle

```text
protected journey a required assurance
→ exact realm, client a authentication-flow generation
→ current Keycloak user/session authentication level
→ credential inventory a enrollment authority
→ authenticator selection alebo conditional branch
→ challenge, origin/RP ID a user-verification ceremony
→ Keycloak authenticator verdict
→ resulting authentication level, acr/amr/auth_time
→ client session a token/assertion
→ downstream step-up and resource authorization
→ recovery, credential revocation a second-login validation
```

MFA acceptance sa uzatvára až downstream outcome-om. Keycloak môže správne overiť WebAuthn assertion, ale aplikácia ignoruje `acr`; client môže vyžiadať `acr=gold`, ale flow dosiahne nižšiu úroveň; token môže niesť správny `acr`, ale pochádzať zo starej SSO session pred credential revocation. Každá vrstva preto potrebuje vlastný subject a read-back.

## 2. Exact MFA a WebAuthn subject

Pri incidente veta „user mal passkey“ nestačí. Zachovaj:

```yaml
mfaSubject:
  keycloak:
    publicBaseUrl: https://sso.atlas.example
    deploymentGeneration: kc-2026-08-02-09
    realm: atlas-prod
    issuer: https://sso.atlas.example/realms/atlas-prod
  client:
    clientId: settlement-admin-web
    internalId: 2b2b...
    configurationRevision: client-211
    browserFlowOverride: atlas-privileged-browser-v5
  request:
    protocol: oidc
    requestedAcr: gold
    prompt: login
    maxAge: 300
    stateHash: sha256:...
    nonceHash: sha256:...
  session:
    authenticationSessionId: 64c1...
    predecessorUserSessionId: 04d9...
    predecessorAuthenticationTime: 2026-08-02T05:40:00Z
  user:
    userId: 4b8e...
    credentialInventoryRevision: cred-83
  webauthn:
    rpId: sso.atlas.example
    rpName: Atlas Production SSO
    policy: passwordless-v4
    credentialIdHash: sha256:...
    aaguid: 08987058-cadc-4b81-b6e1-30de50dcbe96
    userVerification: required
    discoverableCredential: required
    attestationConveyance: none
  flow:
    alias: atlas-privileged-browser-v5
    executionRevision: flow-97
    achievedLoa: 2
    resultingAcr: gold
```

Credential label, username alebo AAGUID nie sú stable user identity. WebAuthn credential je viazaná na Keycloak user internal ID a RP ID/origin contract. Pri federated useroch môže Keycloak storage ID obsahovať provider prefix; WebAuthn `user.id` má limit 64 bytes, preto príliš dlhý provider alebo external user ID môže registráciu rozbiť. Provider a user identifier design sa musí overiť pred masovým enrollmentom.

## 3. TOTP a HOTP ako shared-secret OTP

TOTP generuje kód z tajného seed-u a časového kroku; HOTP používa counter. Keycloak pri enrollment-e vytvorí seed, používateľ ho prenesie do authenticator app cez QR alebo manual secret a server ho uloží ako credential. OTP je phishing-prone bearer proof: kto získa aktuálny kód a prvý ho použije, môže dokončiť challenge.

OTP policy zahŕňa algorithm, digits, period alebo counter, look-ahead window a initial counter. Zmena policy neprepisuje automaticky všetky existujúce credentials. Migration musí vedieť, ktoré credentials boli enrolled podľa predecessor policy a či successor policy zostáva kompatibilná.

```text
password alebo brokered first factor
→ OTP challenge pre exact authentication session
→ code validation voči stored seed a time/counter window
→ replay/previous-code behavior
→ authenticator success
→ resulting session assurance
```

Clock synchronizácia ovplyvňuje TOTP acceptance. Rozšírenie look-ahead window môže zlepšiť usability, ale zväčšuje accepted code set. OTP success nepreukazuje phishing resistance ani device identity.

## 4. WebAuthn registration ceremony

Keycloak vystupuje ako WebAuthn Relying Party. Registration ceremony vytvorí RP-scoped asymmetric credential. Browser a authenticator dostanú challenge, RP information, user handle, algorithm preferences, authenticator selection a attestation preference. Authenticator vytvorí private/public key pair; private key neopustí authenticator alebo credential provider a Keycloak uloží public-key credential metadata.

```text
authorized enrollment transaction
→ random server challenge
→ rp.id + expected origin
→ opaque Keycloak user handle
→ authenticatorMakeCredential
→ user presence a prípadná user verification
→ credential ID, public key, flags a attestation object
→ server challenge/origin/RP/algorithm verification
→ credential record linked to exact user
→ second-login test
```

Registration success nie je authentication success. Required action alebo Application-Initiated Action musí byť spustená z dostatočne silnej current session. Pri step-up-enabled credential managemente má pridanie alebo odstránenie credentialu vyžadovať úroveň zodpovedajúcu credentialu, ak user už credential tejto úrovne má. Inak by attacker s ukradnutou low-assurance session mohol pridať vlastný passkey a vytvoriť persistentný authentication path.

## 5. WebAuthn authentication ceremony

Pri authentication Keycloak vytvorí nový challenge a browser zavolá WebAuthn `get()`. Authenticator podpíše authenticator data a client data private keyom. Keycloak overuje challenge, RP ID hash, origin, credential ID, signature a flags ako user presence a user verification podľa policy.

```text
server challenge C-771
+ expected RP ID sso.atlas.example
+ expected origin https://sso.atlas.example
+ allowed credential alebo discoverable lookup
→ authenticator assertion
→ challenge/origin/RP/signature/flags verification
→ credential counter/metadata handling
→ exact authentication execution success
```

Reverse proxy a hostname configuration sú súčasťou RP contractu. Zmena verejného hostname alebo nesprávne trusted forwarded headers môžu rozbiť origin/RP expectations alebo vytvoriť nejasnú authority. TLS terminácia, browser origin a Keycloak public base URL musia byť konzistentné.

## 6. WebAuthn 2FA versus passwordless credential

Keycloak má oddelenú WebAuthn policy pre druhý faktor a WebAuthn Passwordless Policy. Druhofaktorová credential sa používa po identifikácii usera a typicky po hesle alebo inom first factor-e. Passwordless credential môže nahradiť heslo; pri discoverable credential môže identifikovať aj usera.

```text
WebAuthn 2FA
username/password alebo iný first factor
→ WebAuthn Authenticator
→ two-step authentication path

Passwordless/passkey
WebAuthn Passwordless Authenticator
→ possession + user verification
→ password absent

Loginless
empty allowCredentials + discoverable credential
→ authenticator vyberie RP-scoped account
→ user handle identifikuje Keycloak usera
```

`User Verification Requirement=required` je kľúčový pre passwordless multi-factor property. Samotná possession roaming tokenu bez PIN/biometrie môže byť single-factor. `Discoverable Credential=required` je potrebné pre loginless flow, ale hardware authenticators majú obmedzenú storage capacity.

## 7. Passkeys, conditional UI a mediation

Passkeys používajú WebAuthn passwordless credential. Keycloak ich integruje do username a password forms. Conditional UI umožní browser autofill ponúknuť discoverable credentials pri focus-e username field-u; modal UI sa spustí explicitným tlačidlom.

Passkey mediation policy určuje page-load behavior:

```text
conditional
→ bez automatického dialogu; passkeys cez autofill dropdown

none
→ bez automatickej akcie; explicitné tlačidlo stále dostupné

optional
→ browser môže automaticky otvoriť passkey selection dialog
```

Conditional UI je environment capability, nie authentication guarantee. Browser alebo platform bez podpory musí mať bezpečný fallback. Fallback nesmie ticho znížiť assurance pre privileged clienta; password fallback môže vyžadovať OTP/WebAuthn 2FA alebo explicitný step-up.

Synchronizovaná passkey zlepšuje recovery a multi-device usability, ale trust sa presúva aj na credential provider account a device-unlock model. Platform policy musí rozhodnúť, či akceptuje synced passkeys, iba device-bound/hardware authenticators alebo konkrétny authenticator class.

## 8. Attestation, AAGUID a authenticator allowlist

Attestation môže poskytnúť evidence o type a pôvode authenticatora. Pri `attestation=none` RP nedostane spoľahlivý manufacturer/model proof; AAGUID môže byť anonymizovaný alebo nulový. Acceptable AAGUID allowlist preto dáva zmysel iba s vhodnou attestation conveyance a validovaným trust chainom.

Strict attestation policy znižuje supported device set a môže vytvoriť recovery alebo accessibility problém. Attestation tiež prináša privacy trade-off. Rozhodnutie má vychádzať z konkrétneho risku, nie z predstavy, že „hardware key je vždy bezpečnejší“.

Evidence inventory obsahuje policy generation, attestation preference, imported trust anchors, accepted algorithms, AAGUID allowlist, actual registration attestation result a authentication flags. Admin Console policy screenshot nepreukazuje credential, ktorá bola enrolled podľa tejto policy.

## 9. Credential inventory, labels a priority

User môže mať viac WebAuthn, passwordless, OTP a recovery credentials. Label je používateľská pomôcka, nie stable key identity. Credential ID, type, creation metadata a policy/enrollment generation sú dôležitejšie.

Keycloak môže ponúknuť najvyššie prioritnú credential a `Try another way` pre alternatives. Každá alternative musí spĺňať intended assurance. Ak recovery code alebo OTP zostane slabším bypassom pre client, ktorý vyžaduje phishing-resistant authentication, výsledný assurance určuje najslabší povolený path.

```text
credential inventory
→ intended primary method
→ approved recovery alternatives
→ disabled/deprecated methods
→ per-client/LoA policy
→ actual path recorded in session/token evidence
```

## 10. Recovery codes

Keycloak generuje sekvenciu jednorazových recovery codes, ktoré možno zaradiť ako alternatívny 2FA authenticator. Použitý kód sa odstráni a ďalší login vyžaduje ďalší remaining code. Regenerácia vytvorí nový set a invaliduje predecessor set podľa credential lifecycle-u.

Recovery code je offline bearer secret. Je phishing-prone a jeho storage je mimo Keycloak controlu. Má slúžiť ako ohraničený backup, nie ako permanentný slabší first-class factor. Acceptance testuje one-time use, replay denial, regeneration, remaining-code warning a incident revocation.

```text
primary factor success
→ Recovery Authentication Code Form
→ exact unused code accepted
→ code consumed
→ session assurance podľa configured levelu
→ used-code replay rejected
```

## 11. Step-up a Level of Authentication

Step-up umožňuje reuse existujúcej session, ak už dosiahla požadovanú úroveň, alebo vykonanie ďalšej authentication vetvy, ak je current level nedostatočný. OIDC client môže requestnúť `acr` cez `claims` parameter; realm alebo client policy mapuje ACR values na numeric LoA. SAML používa requested authentication context a client/realm mapping podľa enabled feature a configuration.

```text
current user session LoA 1
+ request acr=gold mapped to LoA 2
→ Cookie authenticator načíta session
→ condition level 2 ešte nesplnený
→ WebAuthn/OTP step-up branch
→ session LoA 2
→ token acr=gold
```

`acr` mapper nesmie tvrdiť vyššiu úroveň, než flow skutočne dosiahol. Client nemá veriť iba requested ACR; validuje resulting claim a freshness (`auth_time`, `max_age`) podľa operation risku. Resource server môže vyžadovať step-up pre konkrétnu action aj keď UI session existuje.

## 12. Enrollment a removal ako privileged operations

Credential creation, rename, reordering a deletion sú security mutations. Account Console, Admin Console, AIA a Admin REST API majú odlišných actorov a audit paths. Helpdesk deletion všetkých passkeys môže zmeniť account na password-only; pridaním nového passkey možno vytvoriť persistence.

High-risk mutation contract:

```text
exact authenticated actor
+ target user internal ID
+ current authentication level a freshness
+ predecessor credential inventory hash
+ requested add/delete operation
→ Keycloak authoritative mutation
→ successor inventory hash
→ audit event
→ old credential negative test
→ successor credential second-login test
```

Pri lost authenticator recovery sa nesmie automaticky znížiť assurance na mailbox-only bez risk review. Recovery môže vyžadovať existing second credential, verified helpdesk process, managed-device evidence alebo delayed approval.

## 13. Connected incident `KC-PAY-67` — nesprávne namapovaný step-up

Atlas zaviedol passkeys pre `settlement-admin-web`. WebAuthn Passwordless Policy vyžadovala discoverable credential, ale `User Verification Requirement` zostala `preferred`. Privileged client requestoval `acr=gold`, no ACR-to-LoA mapping priradil `gold` úrovni 1. Existing brokered SSO session na LoA 1 preto prešla Cookie executionom a token dostal `acr=gold` bez nového WebAuthn challenge.

Súčasne bol Recovery Authentication Code Form nastavený ako `ALTERNATIVE` na rovnakej úrovni ako WebAuthn. Helpdesk po strate telefónu odstránil userovi passkey a vygeneroval reset link bez samostatného descendant-session revocation. Attacker s kompromitovanou mailbox session dokončil reset, vytvoril vlastný passkey a použil stále aktívnu application session.

```text
requested acr=gold
→ chybná mapping gold→LoA1
→ remembered low-assurance SSO accepted
→ token nesie gold bez step-up
→ weak recovery pridá attacker passkey
→ predecessor sessions zostávajú aktívne
→ privileged settlement operation
```

## 14. Authoritative recovery

Recovery vytvorí successor flow a policy generation. `gold` sa mapuje na LoA 2, passwordless policy vyžaduje user verification, privileged client má exact flow override a resource server validuje resulting `acr`, `auth_time`, client a action. Credential management vyžaduje current LoA 2. Recovery codes sú povolené iba pre bounded recovery path a po použití spúšťajú fresh WebAuthn enrollment alebo risk review.

Incident closure zahŕňa inventory všetkých credential IDs, removal attacker credentialu, invalidáciu compromised recovery setu, revocation user/client/application sessions a token descendants, kontrolu Admin/Account events a second-login test na novom browseri aj remembered SSO.

## 15. Positive, recovery a forbidden acceptance

Positive path:

```text
fresh privileged login
→ passkey assertion s UV=true
→ achieved LoA2
→ token acr=gold a fresh auth_time
→ exact settlement operation succeeds
```

Recovery path:

```text
user stratí primary passkey
→ approved recovery actor/process
→ predecessor sessions a recovery artifacts revoked
→ successor credential enrolled z adequate assurance
→ old credential fails
→ new credential second login succeeds
```

Forbidden paths:

```text
low-assurance remembered SSO + acr=gold
→ step-up required; token absent before completion

WebAuthn assertion s wrong origin alebo RP ID
→ reject

credential s UV=false pre passwordless-gold policy
→ reject

used recovery code replay
→ reject

helpdesk reset bez descendant-session closure
→ incident acceptance fails

susedný client bez gold requirement
→ nesmie dostať gold claim iba reuse sessionu
```

## 16. Troubleshooting

Pri passkey failure oddeľ server challenge, browser capability, secure context/TLS, public hostname, origin/RP ID, user handle length, authenticator algorithms, discoverable/user-verification requirements, attestation trust, credential inventory a assertion flags. `NotAllowedError` v browseri môže znamenať cancel, timeout, absent credential alebo policy mismatch; potrebuje correlation s Keycloak events a exact transaction.

Pri step-up failure porovnaj requested ACR, ACR-to-LoA mappings, client policy/flow selector, current session level, execution graph a resulting token claims. Token `acr=gold` bez evidence o achieved LoA je security defect; repeated prompt napriek dostatočnej úrovni je session/mapping alebo freshness defect.

## 17. Kontrolné otázky

- Ktorý exact credential ID, RP ID, policy a enrollment generation sa použili?
- Je credential 2FA, passwordless alebo discoverable loginless passkey?
- Vyžaduje policy user verification a je assertion flag skutočne nastavený?
- Ktoré alternative paths môžu dosiahnuť rovnaký LoA?
- Zodpovedá resulting `acr` skutočne dosiahnutej flow úrovni?
- Ako sú chránené add/delete credential operations?
- Čo sa stane so sessions a tokens po credential recovery alebo removal?
- Prešli wrong origin, wrong RP, UV=false, stale session, used recovery code, second client a second-login paths?

## Glossary impact

Relevantné pojmy: MFA transaction subject, TOTP, HOTP, WebAuthn Relying Party, registration ceremony, authentication assertion, passkey, discoverable credential, user verification, RP ID, origin, attestation, AAGUID, WebAuthn Passwordless Policy, conditional UI, passkey mediation, recovery code, authentication level, ACR-to-LoA mapping, step-up authentication a credential descendant revocation.

## Primárne zdroje

- [Keycloak — Server Administration Guide: WebAuthn, passkeys, recovery codes and step-up authentication](https://www.keycloak.org/docs/latest/server_admin/)
- [W3C — Web Authentication Level 3](https://www.w3.org/TR/webauthn-3/)
- [OpenID Connect Core 1.0 — Authentication Context and `acr`](https://openid.net/specs/openid-connect-core-1_0.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Authentication flows, executions a required actions](authentication-flows-executions-and-required-actions.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Password policies, brute-force protection a account recovery →](password-policies-brute-force-protection-account-recovery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
