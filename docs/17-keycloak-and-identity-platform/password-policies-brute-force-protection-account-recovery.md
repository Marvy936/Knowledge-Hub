# Password policies, brute-force protection a account recovery

Password security v Keycloak-e nie je jedna realm policy. Je to lifecycle od credential creation a hashing authority cez online login, failure counters, temporary alebo permanent lockout, reset-credentials transaction, email/action-token delivery, authoritative password mutation a session/token descendant handling. Silná password policy nepomôže, ak reset link ide do kompromitovanej mailbox schránky; brute-force lockout môže zastaviť guessing, ale zároveň umožniť denial of service; úspešná password zmena nemusí zrušiť už existujúce Keycloak a application sessions.

Keycloak local password a LDAP/AD password majú odlišnú storage authority. Pri local userovi Keycloak hash vytvára a ukladá. Pri LDAP userovi password spravidla neimportuje a validáciu alebo update deleguje directory serveru. Realm policy, required action a directory password policy sa preto môžu rozísť. Recovery acceptance musí identifikovať, ktorý systém vlastní credential a ktoré descendants zostávajú použiteľné.

## 1. Dominantný password-to-recovery lifecycle

```text
credential ownership a password-policy generation
→ password creation alebo validation authority
→ online authentication attempt
→ brute-force failure state a lockout decision
→ reset/recovery initiation
→ user lookup bez account enumeration
→ action-token creation a delivery
→ reset-credentials authentication flow
→ authoritative credential mutation
→ required actions a session/token disposition
→ second login, old credential a old session validation
```

Každá fáza môže byť zelená a celkový recovery outcome stále nesprávny. SMTP môže doručiť email, ale link smeruje na wrong public hostname. Action token môže byť validný, ale account bol medzitým disabled alebo email reassigned. Password update môže uspieť v Keycloak DB, ale user je LDAP-backed a login stále používa directory credential. Browser môže zobraziť „password updated“, no attackerova refresh token alebo local application session zostane aktívna.

## 2. Exact password a recovery subject

```yaml
passwordRecoverySubject:
  keycloak:
    publicBaseUrl: https://sso.atlas.example
    deploymentGeneration: kc-2026-08-02-09
    realm: atlas-prod
    realmRevision: realm-301
  user:
    userId: 4b8e...
    username: dana.settlement
    enabled: true
    email: dana@atlas.example
    emailVerified: true
    storageProvider: local
    credentialRevision: pwd-91
  passwordPolicy:
    revision: password-policy-17
    hashAlgorithm: argon2
    minimumLength: 14
    history: 10
    maxAuthAge: 300
    expirePasswordDays: 180
  bruteForce:
    mode: temporary_then_permanent
    revision: brute-force-12
    maxLoginFailures: 5
    waitIncrementSeconds: 30
    maxWaitSeconds: 900
    failureResetSeconds: 43200
    maximumTemporaryLockouts: 3
    secondaryAuthenticationFailures: 5
  recovery:
    resetFlow: atlas-reset-credentials-v3
    actionTokenIdHash: sha256:...
    issuedAt: 2026-08-02T06:20:00Z
    expiresAt: 2026-08-02T06:35:00Z
    initiatingClient: account
    redirectUri: https://account.atlas.example/
  descendants:
    userSessionIds: [04d9...]
    offlineSessionCount: 1
    applicationSessions: [payments-admin:app-771]
```

Username a email sú lookup attributes, nie stable identity. Recovery mutation musí byť viazaná na internal user ID, realm a current storage-provider link. Delete/recreate user môže zachovať username alebo email, ale vytvoriť nový identity subject.

## 3. Realm password policy ako composition

Realm password policy je composition viacerých rules. Keycloak pri novom passworde overuje všetky configured policies, napríklad length, character classes, prohibited values, username/email similarity, password history, expiry, hashing algorithm a hashing parameters. Realm bez configured policy môže akceptovať jednoduché passwordy; production realm preto potrebuje explicitný baseline od svojho vzniku.

```text
candidate password
→ syntax/length/character policies
→ prohibited/history/user-attribute checks
→ hashing policy selection
→ credential write
→ predecessor credential history update
```

Nová policy sa automaticky neaplikuje na existujúce credential bytes. Existujúci users zostanú na predecessor credential až do ďalšej zmeny alebo required/expiry action. Migration potrebuje population inventory a staged `UPDATE_PASSWORD` alebo expiry contract, nie iba Admin Console save.

Complexity policy nie je hlavná obrana proti credential stuffing. Dlhé unikátne passwordy, breached-password detection, MFA/passkeys, rate limiting a monitoring majú vyššiu hodnotu než extrémne composition rules, ktoré vedú k predvídateľným patterns. Keycloak policy musí zostať kompatibilná s upstream LDAP policy, helpdesk a application UX.

## 4. Hashing authority a rehash lifecycle

Pre local users Keycloak ukladá salted password hash. Aktuálne non-FIPS deployments typicky používajú Argon2 ako default; FIPS deployments používajú PBKDF2-SHA512 podľa provider/configuration. Hash algorithm, iterations alebo memory parameters sú súčasť credential generation.

```text
plaintext candidate v TLS-protected requeste
→ password policy validation
→ configured hash provider a parameters
→ salt + hash
→ local credential record
```

Plaintext nemá byť logovaný ani zachytený v tracing payloads. DB backup obsahuje password hashes a stále je high-value secret. Zmena hashing policy môže vyvolať rehash pri ďalšom successful authentication podľa credential/provider behavioru; acceptance musí overiť actual stored credential metadata, nie iba realm configuration.

Pri LDAP-backed userovi Keycloak password zvyčajne nehashuje do local DB. LDAP bind alebo password validation prebieha proti directory serveru. Pri write môže Keycloak odoslať plaintext cez secure LDAP spojenie a directory server vykoná vlastné hashing/storage rules. `ldaps` alebo StartTLS, truststore a directory hashing sú preto súčasť password boundary.

## 5. Password expiry a `UPDATE_PASSWORD`

Expiry policy môže pri login-e automaticky spustiť required action `UPDATE_PASSWORD`. Admin môže používateľovi nastaviť temporary password alebo explicitne priradiť required action. Dokončenie action mení credential authority a odstráni pending action podľa výsledku.

```text
password age alebo temporary marker
→ credential authentication
→ UPDATE_PASSWORD required action
→ candidate policy validation
→ authoritative write
→ required action removed
→ session continuation podľa policy
```

Označenie passwordu ako temporary nie je descendant revocation. Ak incident vyžaduje account recovery, treba samostatne rozhodnúť o existing sessions, refresh/offline tokens a application sessions.

## 6. Brute-force state a supported mechanisms

Keycloak brute-force detection sleduje online failures pre mechanisms náchylné na guessing: password, OTP a recovery codes. Je disabled by default a musí byť explicitne enabled. User-facing error zostáva všeobecné `Invalid username or password`, aby lockout neprezrádzal account existence alebo state.

Failure state nie je iba counter. Obsahuje počet failures, timestampy, quick-login signal, temporary wait, temporary-lockout counter a permanent disabled state podľa mode. Success môže resetovať failure state, ale policy sa líši podľa mode a secondary-authentication configuration.

```text
failed credential attempt
→ user resolution bez enumeration response
→ failure state read
→ count/timing update
→ wait alebo permanent-lockout decision
→ generic external error
→ admin/event evidence
```

## 7. Permanent, temporary a mixed lockout

Permanent mode disable-ne usera po threshold-e, kým administrator account znovu nepovolí. Temporary mode vypočíta wait podľa failure count, increment strategy a max wait; failure reset time musí byť väčší než max wait, inak intended escalation nemusí nastať. Mixed mode povolí určitý počet temporary lockouts a potom permanent lockout.

`Quick Login Check Milliseconds` identifikuje príliš rýchle pokusy a môže uplatniť `Minimum Quick Login Wait` ešte pred bežným threshold-om. `Maximum Secondary Authentication Failures` chráni OTP/recovery-code stage samostatne, aby attacker po správnom passworde nemal neobmedzené 2FA guesses.

Brute-force protection vytvára DoS risk. Attacker poznajúci usernames môže úmyselne locknúť users. Gateway rate limiting, IP/device/risk signals, alerting a helpdesk unlock process musia dopĺňať per-user Keycloak state.

## 8. Failure evidence a admin operations

Pri lockout incidente zachovaj user ID, realm, brute-force configuration revision, attack-detection record, login-error events, source IP/ASN/device cohort, client IDs, authentication mechanism, timestamps a unlock actor.

Admin REST API poskytuje attack-detection endpoints pre realm/user failure state. Príklad read-backu:

```bash
USER_ID='4b8e...'

kcadm.sh get "attack-detection/brute-force/users/${USER_ID}" \
  -r atlas-prod \
  | jq '{numFailures,disabled,lastIPFailure,lastFailure,maxLoginFailures,failedLoginNotBefore}'
```

Output preukazuje Keycloak brute-force state pre exact user v danom realm-e. Nepreukazuje, že directory account nie je locknutý, že upstream IdP nepridal vlastný lockout ani že application session bola ukončená.

Unlock alebo clear failure state je mutation:

```bash
kcadm.sh delete "attack-detection/brute-force/users/${USER_ID}" \
  -r atlas-prod
```

Po mutation nasleduje read-back, successful intended login, invalid-password negative test a event verification. Automatické periodické clear-all by zrušilo security control.

## 9. Reset Credentials flow

`Forgot password` spúšťa bound Reset Credentials flow. Default flow identifikuje usera, pošle reset email a môže podľa configuration resetovať OTP alebo ďalšie credentials. Client môže používateľa poslať na supported `/forgot-credentials` OIDC path; nemá konštruovať interné `/login-actions` URL.

```text
forgot-credentials request
→ exact client/redirect a realm
→ user lookup
→ generic response bez account enumeration
→ action token issue
→ SMTP delivery
→ token validation
→ password/credential reset executions
→ user mutation a session policy
```

Reset flow je authentication flow a má versioned alias, execution graph, priorities a requirements. Passwordless browser flow môže potrebovať vlastný Reset Credentials variant, aby sa neopakoval username step alebo aby recovery zachovala intended assurance.

## 10. Action token a email delivery boundary

Reset email nesie signed action token s realm/user/action/client/redirect/time contextom. Bezpečnosť závisí od Keycloak signing key, token lifespan, public hostname, SMTP delivery a mailbox security.

```text
action-token generation R-411
→ email template a public URL
→ SMTP accepted
→ mailbox delivered
→ user opens link
→ signature, expiry, action, user a client validation
→ one authorized recovery transaction
```

SMTP `250 Accepted` nepreukazuje delivery správnemu človeku. Reassigned email, forwarding rule, compromised mailbox alebo stale verified email môžu odovzdať recovery attackerovi. Sensitive realm môže vyžadovať ďalší factor, helpdesk verification, managed-device evidence alebo delayed approval.

Action token sa nesmie logovať v plnej URL. Proxy access logs, analytics referrers, support tickets a screenshots môžu token leaknúť. Token expiry a replay behavior sa testujú explicitne.

## 11. Email verification a recovery identity

`emailVerified=true` je Keycloak state, nie večná ownership guarantee. Identity broker s `Trust Email`, LDAP sync alebo admin mutation môže email označiť verified. Recovery policy musí poznať source authority, sync mode a lifecycle email reassignment.

Pri high-risk accountoch používaj stable workforce ID a verified communication channels oddelene. Email-only recovery je silné ako mailbox account, jeho own MFA a organization offboarding.

## 12. Recovery codes a factor reset

Recovery codes sú one-time 2FA backup, nie password reset. Môžu umožniť login po primary factor-e, ak OTP/WebAuthn device nie je dostupné. Reset Credentials flow môže samostatne resetovať OTP podľa configured executions; to nesmie byť prekvapivý side effect.

Regenerácia recovery codes invaliduje predecessor set. Helpdesk, Account Console a required action majú odlišných actors. User musí bezpečne uložiť set a Keycloak má sledovať remaining-code warning. Used code replay sa odmieta.

## 13. Session a token descendants po password change

Password change nevytvára univerzálny guarantee, že všetky sessions a bearer tokens sú neplatné. Rozhodujú realm/session policies, not-before/revocation, offline tokens, adapters a local application sessions.

```text
password generation P-92
→ predecessor password invalid
→ Keycloak user sessions inventory
→ client sessions a refresh/offline tokens
→ self-contained access tokens
→ application cookies/sessions
→ resource-server caches
```

Incident recovery musí explicitne revoke-nuť descendants podľa risku. Old password negative test nestačí. Otestuj existing browser cookie, refresh token, offline token, access token na každej API cohort-e a downstream application session.

## 14. LDAP a directory recovery boundary

Pri LDAP/AD userovi password reset môže mutovať directory. `READ_ONLY` mode update nepovolí; `WRITABLE` posiela update do LDAP; `UNSYNCED` môže uložiť local credential/data podľa mapper configuration. Directory môže nastaviť „must change password“ flag, vlastný lockout alebo password history.

Keycloak `Enable LDAP password policy` môže reagovať na directory signal a pridať `UPDATE_PASSWORD`. Bind account používaný na password update môže spôsobiť, že directory update vyzerá ako admin reset a znovu vynúti change. Recovery test preto musí zahŕňať directory entry/state a druhý login.

## 15. Connected incident `KC-PAY-67` — mailbox recovery bez session closure

Attacker získal mailbox používateľa `dana.settlement` cez external IdP account takeover. Keycloak user mal verified email synchronizovaný z LDAP. Attacker spustil Forgot Password, dostal action link a zmenil local password. Realm mal brute-force temporary lockout, ale reset flow nevyžadoval current MFA ani recovery code.

Helpdesk po hlásení používateľa zmenil password druhýkrát a vymazal brute-force state. Nezrušil však offline token mobilnej aplikácie ani local settlement-admin session. Attacker pokračoval v exportoch aj po tom, čo old password už nefungoval.

```text
compromised mailbox
→ valid reset action token
→ password generation changed
→ brute-force state cleared
→ predecessor offline/application sessions retained
→ continued privileged operations
```

## 16. Evidence-preserving containment a recovery

Zachovaj password-policy revision, user/storage-provider identity, brute-force record, login/reset events, action-token hash a issuance context, SMTP message ID, credential history metadata, session/token inventory a downstream request IDs. Neuchovávaj plaintext password alebo full action token.

Containment môže disable-nuť usera, blocknúť high-risk API operations, revoke-nuť sessions/offline tokens, invalidate action links a suspend mailbox/broker identity. Recovery overí authoritative email a user identity, vytvorí successor credential cez adequate factor/helpdesk process, obnoví MFA/passkeys a uzatvorí all descendants.

## 17. Positive, recovery a forbidden acceptance

Password a recovery acceptance nie je jeden successful login. Positive path overuje policy a authoritative credential write, recovery path pridáva identity re-verification a descendant revocation a forbidden paths dokazujú, že enumeration, stale links, weak candidates, guessing a predecessor sessions nemôžu obísť successor contract.

Positive path:

```text
valid current password alebo approved reset
→ candidate spĺňa policy
→ authoritative credential updated
→ intended fresh login succeeds
→ required MFA/step-up succeeds
```

Recovery path:

```text
compromised credential/mailbox
→ account a high-risk operations contained
→ action tokens a sessions revoked
→ identity re-verified
→ successor password/MFA enrolled
→ second login succeeds
→ old password, old link a old sessions fail
```

Forbidden paths:

```text
unknown email/username reset request
→ rovnaká external response bez enumeration

expired alebo replayed reset token
→ reject

password nespĺňa policy/history
→ no mutation

quick repeated guesses
→ configured wait/lockout a event

attacker-triggered lockout
→ monitoring detects DoS pattern; no silent bulk unlock

password changed, old offline/application session works
→ recovery acceptance fails
```

## 18. Troubleshooting

Pri password update failure oddeľ realm policy, user storage provider/edit mode, LDAP password policy, required action, current authentication freshness a directory response. Pri reset email failure sleduj public hostname, client redirect, SMTP connection, template, message acceptance, delivery a mailbox filtering.

Pri unexpected lockout čítaj exact brute-force mode, failure count, timing, quick-login state, secondary failures a upstream LDAP/IdP lockout. Restart Keycloak node nie je authoritative reset. Cluster/cache behavior a persistent brute-force state treba čítať cez Admin API a events.

## 19. Kontrolné otázky

- Kto vlastní password: Keycloak DB, LDAP/AD alebo external IdP?
- Ktorá policy a hashing generation platila pri credential creation?
- Ako sa existujúca population dostane na successor policy?
- Aký brute-force mode, threshold, wait a reset semantics sú active?
- Je recovery odolná voči account enumeration a mailbox compromise?
- Ktoré executions resetujú password, OTP alebo recovery artifacts?
- Čo sa deje s user/client/offline/application sessions po recovery?
- Prešli old password, expired/replayed link, used recovery code, lockout DoS, old token a second-login paths?

## Glossary impact

Relevantné pojmy: password-policy generation, credential hashing authority, Argon2, PBKDF2, password expiry, temporary password, brute-force failure state, quick-login check, temporary/permanent/mixed lockout, secondary-authentication lockout, Reset Credentials flow, action token, account enumeration, recovery identity, password descendant session a credential-recovery acceptance matrix.

## Primárne zdroje

- [Keycloak — Server Administration Guide: Password policies, brute-force attacks, reset credentials and recovery codes](https://www.keycloak.org/docs/latest/server_admin/)
- [OWASP — Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [NIST SP 800-63B — Authentication and Lifecycle Management](https://pages.nist.gov/800-63-4/sp800-63b.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: MFA, WebAuthn, passkeys a step-up authentication](mfa-webauthn-passkeys-step-up-authentication.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Identity brokering →](identity-brokering.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
