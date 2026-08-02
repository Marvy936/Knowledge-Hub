# MFA, WebAuthn, passkeys a step-up authentication

MFA v Keycloak-e nie je vlastnosť usera ani boolean na clientovi. Je to výsledok konkrétnej authentication transaction, v ktorej sa skombinuje credential inventory používateľa, realm WebAuthn/OTP policy generation, authentication-flow graph, client-specific requirement, remembered SSO session, requested authentication context a downstream protected operation. User môže mať registrovaný WebAuthn credential a napriek tomu dostať token bez fresh WebAuthn, ak existujúca SSO session už uspokojí flow alebo client nevyžiada vyšší Level of Authentication.

Passkey takisto nie je synonymum pre každý WebAuthn credential. Keycloak používa WebAuthn ako Relying Party a rozlišuje klasický WebAuthn druhý faktor od WebAuthn Passwordless credentials. Passwordless/passkey credential potrebuje discoverable credential a user verification tak, aby authenticator vedel vybrať account a overiť používateľa bez hesla. Bez presného rozlíšenia registration policy, credential type, authenticator capabilities a flow execution môže „passwordless“ login potichu fallbacknúť na password + OTP alebo na remembered SSO.

## 1. Dominantný credential-to-operation lifecycle

```text
business operation a required assurance
→ exact realm, client a authentication-context policy generation
→ user identity a credential inventory
→ OTP, WebAuthn 2FA, WebAuthn Passwordless/passkey alebo recovery credential
→ authentication session a existing SSO session
→ flow binding, execution graph a requested LoA/ACR
→ authenticator challenge, user presence a user verification
→ authentication result, auth_time, acr a amr
→ Keycloak user/client session
→ token alebo SAML assertion
→ downstream validation a protected operation
→ credential loss, recovery, revocation a second-login closure
```

Registrácia credentialu je samostatný lifecycle. Úspešné vytvorenie public-key credentialu preukazuje, že browser, authenticator a Keycloak dokončili ceremony podľa danej policy generation. Nepreukazuje, že všetky privileged clients tento credential vyžadujú, že user verification bola pri každom login-e enforced ani že application/API odmietne nižší authentication context.

Authentication ceremony je tiež iba časť outcome-u. Resource server môže dostať token s požadovaným `acr`, ale nesprávne ho mapovať na operation risk. Step-up acceptance sa preto uzatvára až protected business requestom a negative testom s nedostatočným assurance levelom.

## 2. Exact MFA a WebAuthn subject

Pri incidente veta „WebAuthn bolo zapnuté“ nestačí. Zachovaj:

```yaml
mfaSubject:
  keycloak:
    publicBaseUrl: https://sso.atlas.example
    deploymentGeneration: kc-2026-08-02-21
    realm: atlas-prod
    issuer: https://sso.atlas.example/realms/atlas-prod
  client:
    clientId: payments-admin-web
    internalId: 7f00e85a-8d89-4f18-8a5c-c3e2135d0cb6
    configurationRevision: client-191
    browserFlowOverride: atlas-privileged-browser-v5
    minimumAcr: 2
  flow:
    alias: atlas-privileged-browser-v5
    internalId: 5966...
    executionRevision: flow-81
  user:
    internalId: 1d86...
    federationLink: null
    credentialRevision: credentials-44
  credential:
    credentialIdHash: sha256:...
    type: webauthn-passwordless
    aaguid: adce0002-35bc-c60a-648b-0b25f1f05503
    createdAt: 2026-07-11T12:31:00Z
    userLabel: work-laptop-passkey
  policy:
    rpEntityName: Atlas Production
    rpId: sso.atlas.example
    signatureAlgorithms: [ES256, RS256]
    userVerificationRequirement: required
    discoverableCredential: required
    attestationConveyancePreference: none
    acceptableAaguids: []
    avoidSameAuthenticatorRegistration: true
  transaction:
    authenticationSessionId: 67df...
    existingUserSessionId: 42b1...
    requestedAcrValues: ["2"]
    prompt: login
    maxAge: 300
```

Rovnaký credential label nie je stable identity. Credential ID sa nemá zapisovať v plaintext incident reportoch; používaj hash alebo interný reference. Rovnaký user môže mať viac OTP, WebAuthn 2FA, passwordless a recovery credentials. Rovnaký flow alias po editácii nemusí reprezentovať rovnakú execution generation.

## 3. OTP ako shared-secret druhý faktor

TOTP používa shared seed uložený na serveri a v authenticator aplikácii. Keycloak generuje a validuje jednorazový kód podľa algorithmu, digits, periodu a look-ahead window. TOTP dokazuje possession seed-u v danom časovom okne, nie origin-bound phishing resistance. Attacker, ktorý používateľa presmeruje na reverse proxy alebo falošnú stránku, môže password aj aktuálny OTP odovzdať real Keycloak-u v reálnom čase.

```text
TOTP seed registration
→ server a authenticator zdieľajú secret
→ time counter + HMAC
→ krátky numeric code
→ Keycloak window validation
```

OTP policy potrebuje exact algorithm, digits, period a resynchronization/window semantics. Rozšírenie look-ahead window znižuje false rejects pri clock drift-e, ale zväčšuje počet platných kódov. Secret sa nemá exportovať alebo logovať. Reset OTP credentialu je security-sensitive mutation a má viesť k descendant-session reviewu.

OTP zostáva použiteľný fallback, ale privileged phishing-resistant path má preferovať WebAuthn/passkeys. Recovery kódy nie sú druhý nezávislý faktor, ak sú uložené vedľa passwordu alebo v rovnakom compromised password manageri bez ďalšej ochrany.

## 4. WebAuthn registration ceremony

Keycloak je WebAuthn Relying Party. Pri registration vytvorí challenge a options vrátane RP ID, user handle, algorithms, authenticator selection a attestation preference. Browser a authenticator vytvoria asymmetric credential. Keycloak uloží public key a metadata; private key zostane v authenticatori alebo synchronizovanom passkey provideri.

```text
required action alebo AIA request
→ authentication session a exact user
→ Keycloak registration challenge/options
→ browser WebAuthn API
→ authenticator user presence/verification
→ credential key pair a attestation data
→ signed registration response
→ challenge, origin, RP ID a policy validation
→ public-key credential stored pri userovi
→ registration read-back a second-login test
```

Challenge musí byť unpredictable, transaction-bound a expirovať. Browser origin a RP ID musia zodpovedať deployment hostname contractu. Reverse-proxy alebo hostname misconfiguration môže vytvoriť policy, ktorú browser odmietne, aj keď Admin Console vyzerá správne.

WebAuthn používa `user.id` ako opaque user handle s maximálnou dĺžkou 64 bajtov. Keycloak pre lokálnych users typicky používa interné UUID. Pri external user federation môže storage ID obsahovať prefix provider ID a external user ID; príliš dlhý výsledok môže prekročiť WebAuthn limit. Federation component IDs a external IDs preto patria do preflight acceptance pred masovým enrollmentom.

## 5. WebAuthn 2FA verzus Passwordless/passkey

WebAuthn 2FA typicky nasleduje po username/password a overuje ďalší credential. WebAuthn Passwordless môže identifikovať aj autentizovať používateľa bez passwordu, ak credential je discoverable a authenticator vykoná user verification.

```text
WebAuthn 2FA
username/password
→ known user
→ non-discoverable alebo discoverable credential
→ user presence/verification podľa policy
→ second factor

WebAuthn Passwordless / passkey
browser mediation alebo account selection
→ discoverable credential
→ user handle
→ user verification
→ user identity + authentication bez passwordu
```

Keycloak má oddelenú WebAuthn Policy a WebAuthn Passwordless Policy, oddelené required actions a authenticators. Registrácia cez `Webauthn Register` nevytvorí automaticky passwordless credential. Pre passkey/passwordless lifecycle sa používa `Webauthn Register Passwordless` alebo príslušná Application-Initiated Action.

V aktuálnych Keycloak verziách je passkey UX integrované do login forms. Policy `Enable Passkeys` a mediation určujú, či sa credentials ponúkajú cez conditional autofill alebo otvorenejší selection dialog. UI convenience nemení cryptographic contract; acceptance stále overuje RP ID, discoverability, user verification, account selection a fallback path.

## 6. Discoverable credential a user verification

Discoverable credential určuje, či authenticator uchová user/account association a vie credential ponúknuť bez predchádzajúceho username lookup-u. Aktuálna policy rozlišuje `required`, `preferred` a `discouraged`. Passwordless/passkey design typicky vyžaduje discoverable credential; `preferred` môže vytvoriť heterogeneous population podľa authenticator capabilities.

User Verification Requirement môže byť `required`, `preferred` alebo `discouraged`. User presence znamená interakciu s authenticatorom; user verification znamená lokálny PIN, biometriku alebo ekvivalent. Privileged passwordless login bez required user verification môže zmeniť nájdený alebo ukradnutý authenticator na bearer-like credential.

```text
UP=true
→ používateľ sa authenticatora dotkol alebo s ním interagoval

UV=true
→ authenticator lokálne overil používateľa
```

Application alebo API nesmie z claimu či UI predpokladať UV bez toho, aby Keycloak flow a policy túto vlastnosť enforce-li a premietli do stabilného authentication-context contractu.

## 7. RP ID, origin a hostname authority

RP ID je WebAuthn security scope. Browser overuje, že origin patrí RP ID alebo jeho povolenému domain relationshipu. Keycloak public hostname a proxy configuration preto priamo ovplyvňujú registration aj authentication.

```text
public origin https://sso.atlas.example
→ RP ID sso.atlas.example
→ credential scoped to RP
```

Migrácia hostname alebo rozdelenie login domains môže zneplatniť použiteľnosť existujúcich credentials, pretože authenticator nebude credential ponúkať pre nový RP ID. Hostname migration potrebuje predecessor/successor credential strategy, overlap test a recovery path; nie je to iba DNS alebo ingress change.

## 8. Attestation, AAGUID a authenticator allowlist

Attestation môže poskytnúť informáciu o authenticator modeli a trust chain-e. `Attestation Conveyance Preference = none` minimalizuje identifikáciu zariadenia a často anonymizuje AAGUID. Ak organizácia používa Acceptable AAGUIDs, potrebuje attestation mode, ktorý dôveryhodný AAGUID poskytne, a trust anchors v Keycloak truststore.

AAGUID allowlist môže vynútiť enterprise-approved authenticators, ale zvyšuje operational coupling. Firmware/model changes, privacy-preserving attestation alebo synchronized passkeys môžu registration odmietnuť. Policy musí mať explicitný business dôvod, device inventory, exception a recovery path. AAGUID nie je identity konkrétneho zariadenia ani dôkaz jeho aktuálneho security posture.

## 9. Avoid Same Authenticator Registration a credential inventory

`Avoid Same Authenticator Registration` zabraňuje opätovnej registrácii rovnakého credentialu pri tom istom userovi. Nezabraňuje tomu, aby user registroval viac authenticatorov alebo synchronizované kópie passkey podľa provider semantics.

Credential inventory potrebuje type, creation time, user label, AAGUID, transports/capabilities ak sú dostupné, last-used evidence podľa telemetry contractu a owner-approved purpose. User label je mutable presentation field. Pri incident response sa nesmie používať ako jediná identity credentialu.

Self-service delete credentialu môže používateľa uzamknúť, ak nemá ďalší faktor alebo recovery path. Enrollment policy preto vyžaduje minimálny počet independent recovery paths alebo helpdesk identity-proofing proces.

## 10. Step-up cez LoA a ACR

Step-up znamená, že current session nestačí pre požadovaný client alebo operation. Keycloak vyhodnotí requested authentication context, client minimum a dosiahnutý Level of Authentication. Vyšší level môže vyžadovať fresh authenticator execution.

```text
existing session LoA 1
+ privileged client minimum LoA 2
+ request acr_values=2
→ flow musí dosiahnuť LoA 2
→ WebAuthn/OTP challenge
→ new authentication context
→ token acr=2
```

Ak neexistuje path, ktorý požadovaný level dosiahne, správny outcome je protocol error alebo denial, nie tichý token s nižším assurance. SAML step-up používa authentication context classes a mapovanie na LoA; OIDC používa `acr` request/claim semantics podľa client a realm configuration.

`acr=2` nie je globálny štandard sám osebe. Organizácia musí definovať, čo level 2 znamená, ktoré authenticator combinations ho dosiahnu, či vyžaduje phishing resistance, aký je max authentication age a ktorí consumers ho validujú.

## 11. Fresh authentication, `max_age` a remembered SSO

Remembered SSO môže byť úplne správny pre low-risk client a nedostatočný pre privileged operation. `prompt=login`, `max_age` a step-up policy riešia odlišné veci. `prompt=login` žiada reauthentication UI, `max_age` limituje vek primary authentication a LoA/ACR určuje required assurance.

```text
user session auth_time 08:00
operation 09:30 vyžaduje max_age=300 a LoA 2
→ existing session je príliš stará
→ fresh challenge
```

Application nesmie iba presmerovať na login a po návrate predpokladať step-up. Musí validovať new token/session `auth_time`, `acr`, issuer, audience a transaction binding. Old application session alebo cached authorization decision sa musí nahradiť successor contextom.

## 12. Passkey mediation a fallback path

Conditional mediation umožňuje browseru ponúknuť passkeys cez autofill bez okamžitého modalu. Optional/modal behavior môže otvoriť selection dialog a stále dovoliť fallback. UX path ovplyvňuje, ktorý authenticator branch sa vykoná, ale nesmie meniť required assurance.

Ak WebAuthn Passwordless execution a Password-with-OTP flow sú `ALTERNATIVE`, používateľ môže zvoliť passkey alebo fallback. Privileged policy musí explicitne rozhodnúť, či fallback OTP je rovnocenný assurance level. Ak nie je, nesmie dostať rovnaký `acr` ani prístup k rovnakej operation.

User bez passkey credentialu nemá byť ticho autentizovaný slabším pathom, ak client vyžaduje passkey/phishing-resistant level. Outcome má byť enrollment challenge alebo denial podľa lifecycle stage.

## 13. Recovery codes a MFA recovery

Keycloak recovery codes sú sekvenčné one-time codes používané ako záložný 2FA path. Každý použitý code sa odstráni. Recovery codes znižujú lockout risk, ale sú phishable a exportovateľné. Nemajú automaticky rovnaký assurance ako WebAuthn.

```text
recovery-code generation
→ codes zobrazené používateľovi
→ secure offline storage
→ one code used
→ code removed
→ remaining inventory
→ successor MFA credential registration
```

Recovery code login má zvýšené telemetry a post-login required action na registráciu successor credentialu. Protected high-risk operation môže recovery-code session odmietnuť alebo vyžiadať ďalší helpdesk/transaction verification.

Helpdesk reset WebAuthn/OTP credentials je identity-proofing operation. Administrator, ticket a evidence musia byť auditovateľné. Reset nesmie ponechať attacker-controlled user session alebo refresh token descendants bez reviewu.

## 14. Connected incident `KC-PAY-67`

Atlas nasadil passkeys pre `payments-admin-web`. Realm WebAuthn Passwordless Policy mala `userVerification=preferred` a discoverable credential `preferred`. Browser flow ponechal Cookie authenticator ako top-level `ALTERNATIVE`; privileged client nemal minimum ACR ani `max_age` contract.

Existing operator s rannou password+OTP session otvoril settlement approval o tri hodiny neskôr. Cookie authenticator uspokojil flow a token dostal default `acr=1`, ale aplikácia iba kontrolovala, že user mal vo svojom profile registrovaný passkey. Operáciu preto povolila bez fresh passkey ceremony.

Súčasne bol passkey enrollment povolený ako default action len pre nových users. Existing users bez passwordless credentialu fallbackovali na password+OTP. UI oba paths označilo rovnakým textom „secure login“ a API ich nerozlišovalo.

```text
registered passkey existence
≠ passkey used in current transaction

remembered SSO LoA 1
→ no client minimum ACR
→ Cookie ALTERNATIVE success
→ token acr=1
→ application checks profile credential existence
→ privileged approval accepted
```

Incident closure zaviedol versionovaný privileged flow, minimum LoA 2, required user verification, bounded max authentication age, explicitné `acr/auth_time` validation v application/API a staged enrollment existing users. Recovery-code session dostala nižší level a nemohla schváliť settlement bez ďalšieho step-up.

## 15. Evidence-preserving containment a recovery

Zachovaj realm/client IDs, WebAuthn a Passwordless policy exports, flow/execution IDs a requirements, user credential metadata bez private materialu, authentication session a user/client session IDs, event timestamps, requested/dosiahnuté ACR, `auth_time`, token hash a business operation ID.

Containment môže zablokovať high-risk operations pre sessions pod required levelom, disable-nuť chybný client path a revoke-nuť affected sessions. Recovery vytvorí successor policy/flow generation, priradí test client cohort, vykoná enrollment a fresh/remembered/recovery tests a až potom rozšíri rollout.

Credential deletion alebo realm-wide session logout bez dôkazov môže zničiť incident timeline a uzamknúť users. Bounded containment oddeľuje compromised credential cohort od celej population.

## 16. Positive, recovery a forbidden acceptance

Positive path:

```text
existing user s passkey
→ privileged client requests LoA 2 a max_age 300
→ fresh passkey ceremony s UV=true
→ token acr=2 a current auth_time
→ intended settlement approval succeeds once
```

Forbidden paths:

```text
registered passkey, ale current session LoA 1
→ operation rejects alebo vyžiada step-up

user bez passwordless credentialu
→ enrollment alebo explicitný fallback s nižším ACR
→ no silent privileged access

wrong RP ID/origin
→ browser alebo Keycloak ceremony rejects

UV absent pri required policy
→ authentication rejects

expired/replayed registration alebo authentication challenge
→ rejects

recovery-code session pre phishing-resistant operation
→ rejects alebo ďalší step-up
```

Second-login test používa nový browser bez SSO session. Remembered-session test používa staršiu LoA 1 session. Second-device test overí platform aj roaming authenticator. Successor-policy test overí novú credential registration aj predecessor credential compatibility alebo planned retirement.

## 17. Troubleshooting a anti-patterny

Pri symptom-e „passkey sa nezobrazila“ oddeľ RP ID/origin, passkey policy, `Enable Passkeys`, mediation, discoverable credential, user verification, browser/platform support, user credential inventory, flow binding, execution requirement a current authentication session.

Pri symptom-e „MFA sa preskočila“ zisti exact client, existing session, Cookie branch, requested/minimum ACR, achieved LoA, max age, token `acr/amr/auth_time` a downstream decision. Credential existence v user profile nie je transaction evidence.

Anti-patterny sú: `WebAuthn enabled = všetky clients ho vyžadujú`, `registered passkey = passkey použitý`, `user presence = user verification`, `preferred = guaranteed`, `AAGUID = device identity`, `same UI label = same assurance`, `logout = credential revocation`, `recovery code = phishing-resistant MFA`, `acr=2 = univerzálny význam` a `Admin Console save = browser/runtime acceptance`.

## 18. Kontrolné otázky

- Ktorý exact realm/client/policy/flow/credential/transaction subject sa overuje?
- Ide o OTP, WebAuthn 2FA alebo WebAuthn Passwordless/passkey credential?
- Je discoverable credential a user verification required, preferred alebo discouraged?
- Aký RP ID a browser origin credential používa?
- Ktorý LoA/ACR vyžaduje client a protected operation?
- Môže remembered SSO alebo fallback branch uspokojiť flow s nižším assurance?
- Ako sa rozlišuje passkey, OTP a recovery-code session v tokene a API?
- Ako sa rieši enrollment existing users, lost authenticator a credential reset?
- Prešli fresh, remembered, wrong-origin, missing-credential, UV-absent, recovery a second-device paths?

## Glossary impact

Relevantné pojmy: Keycloak MFA subject, OTP policy, WebAuthn Relying Party, WebAuthn credential, WebAuthn Passwordless credential, passkey, discoverable credential, user presence, user verification, RP ID, origin, attestation, AAGUID, authenticator selection, passkey mediation, Level of Authentication, ACR, `auth_time`, step-up authentication, recovery code a credential descendant revocation.

## Primárne zdroje

- [Keycloak — Server Administration Guide: WebAuthn, Passkeys, Recovery Codes and Step-up Authentication](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak — Supported and preview features](https://www.keycloak.org/server/features)
- [W3C Web Authentication Level 3](https://www.w3.org/TR/webauthn-3/)
- [OpenID Connect Core 1.0 — Authentication Context and max_age](https://openid.net/specs/openid-connect-core-1_0.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Authentication flows, executions a required actions](authentication-flows-executions-and-required-actions.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Password policies, brute-force protection a account recovery →](password-policies-brute-force-protection-and-account-recovery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
