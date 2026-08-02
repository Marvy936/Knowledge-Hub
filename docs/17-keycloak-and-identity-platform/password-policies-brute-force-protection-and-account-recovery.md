# Password policies, brute-force protection a account recovery

Password security v Keycloak-e nie je jedna realm policy. Je to prepojený lifecycle medzi vytvorením credentialu, storage/hash generation, online authentication, brute-force detection, temporary/permanent lockout, reset-credentials flow, email action tokenom, helpdesk zásahom, session descendants a downstream application sessions. Silná password policy nezabráni credential stuffing-u a brute-force protection nevyrieši kompromitovaný mailbox alebo recovery proces, ktorý attackerovi dovolí nahradiť credential.

Najčastejší omyl je považovať úspešný reset passwordu za incident closure. Reset zmení authoritative credential generation, ale nemusí automaticky odstrániť všetky Keycloak user/client sessions, refresh/offline tokens ani local application sessions. Pri federovanom userovi nemusí Keycloak password vôbec vlastniť. Recovery acceptance preto musí zafixovať user storage authority, reset path, resulting credential, attack-detection state a descendant-session behavior.

## 1. Dominantný credential-compromise lifecycle

```text
user identity a credential authority
→ realm password-policy generation
→ credential create/update/reset
→ password hash alebo external-directory mutation
→ online login attempts
→ brute-force counters, wait a lockout state
→ successful authentication alebo denial
→ recovery request a action-token lifecycle
→ successor credential generation
→ Keycloak sessions, tokens a application sessions
→ second-login, old-password a attacker-session validation
```

Každý krok má odlišnú authority. Password policy rozhoduje, ktoré nové heslo možno uložiť. Password hashing provider rozhoduje, ako Keycloak-owned credential uloží. Brute-force detection používa runtime/login failure state. Reset Credentials flow rozhoduje, ako sa user identifikuje a dostane action token. User storage provider rozhoduje, či mutation patrí do Keycloak database alebo LDAP/AD. Session policy rozhoduje, čo po zmene credentialu zostane aktívne.

## 2. Exact password a recovery subject

```yaml
passwordRecoverySubject:
  keycloak:
    deploymentGeneration: kc-2026-08-02-21
    realm: atlas-prod
    issuer: https://sso.atlas.example/realms/atlas-prod
  user:
    internalId: 1d86...
    username: alice.payments
    federationLink: null
    enabled: true
    emailVerified: true
  credentialAuthority:
    mode: keycloak-local
    passwordCredentialId: 884f...
    credentialGeneration: password-18
  passwordPolicy:
    revision: password-policy-24
    rules:
      length: 14
      upperCase: 1
      lowerCase: 1
      digits: 1
      specialChars: 1
      notUsername: true
      passwordHistory: 12
      hashAlgorithm: argon2
      hashIterationsOrParameters: production-profile-7
  bruteForce:
    enabled: true
    permanentLockout: false
    maxLoginFailures: 8
    waitIncrementSeconds: 60
    maxFailureWaitSeconds: 900
    failureResetSeconds: 43200
    quickLoginCheckMilliseconds: 1000
    minimumQuickLoginWaitSeconds: 60
  recovery:
    resetFlowAlias: reset-credentials-v4
    actionTokenLifespanSeconds: 900
    forceLoginAfterReset: true
    clientId: account-console
    redirectUri: https://account.atlas.example/
```

Username, email a display name sú mutable identifiers. Recovery musí používať stable internal user ID po bezpečnom resolutione. Pri LDAP/AD userovi `federationLink` mení credential authority; local password policy môže byť nerelevantná alebo môže chrániť iba local fallback credential podľa provider mode.

## 3. Password policy je write-time gate

Realm password policy sa vyhodnocuje pri vytvorení alebo zmene password credentialu. Neznamená automaticky, že všetky existujúce passwords spĺňajú novú policy. Zvýšenie minimálnej dĺžky nevynúti okamžitú zmenu existujúcej population bez required-action alebo migration plánu.

Policy môže kombinovať length, character classes, not-username, not-email, history, expiration, hashing algorithm a ďalšie pravidlá. Character-class complexity sama osebe často vedie k predvídateľným patternom; dĺžka, compromised-password screening, rate limiting a MFA majú väčší význam než mechanické pravidlo typu jedno veľké písmeno.

```text
candidate password
→ normalization/validation podľa policy
→ history a user-attribute checks
→ hashing provider
→ new credential record
```

Admin Console success preukazuje uloženie novej credential generation. Nepreukazuje login na všetkých nodes, external-directory propagation ani invalidáciu predecessor sessions.

## 4. Hashing a storage authority

Pre Keycloak-local users sa password neukladá ako plaintext. Credential record obsahuje salt, hash a algorithm/parameters metadata. Hashing policy sa môže meniť; po úspešnom login-e môže Keycloak credential rehashnúť na novší provider/parameter set podľa current policy.

Hash algorithm je offline-attack control. Brute-force protection je online-attack control. Silný Argon2/PBKDF profile nezabráni miliónom online attempts, ak rate limiting a lockout nefungujú. Naopak aggressive lockout nevyrieši database leak so slabými hashes.

Pri LDAP/AD federation môže password validation a update prebiehať voči directory. Keycloak nemá automaticky local hash. Password policy, expiration a lockout authority môžu byť rozdelené medzi Keycloak a directory; jeden UI symptom preto potrebuje evidence z oboch systems.

## 5. Password history, expiration a forced update

Password history zabraňuje reuse posledných N credential generations. Nie je to revocation list všetkých passwords, ktoré user kedy použil. History records majú storage a privacy dôsledky a musia byť kompatibilné s provider authority.

Password expiration môže pridať `UPDATE_PASSWORD` required action pri login-e. Expiration sama osebe neznižuje kompromitáciu, ak user vytvára predvídateľné iterácie. Forced periodic rotation bez incidentu môže zhoršiť passwords; moderný model preferuje silné unikátne passwords a rotation pri compromise alebo authority change.

Temporary admin-set password znamená, že user musí password zmeniť. Neznamená automaticky, že delivery kanál temporary passwordu bol bezpečný ani že attacker nemal čas vytvoriť session pred update-om.

## 6. Brute-force detection state

Keycloak brute-force detection sleduje failed login attempts a podľa realm configuration aplikuje wait alebo lockout. Exact behavior závisí od max failures, wait incrementu, maximum wait, quick-login controls, reset time a permanent-lockout policy.

```text
failed credential validation
→ attack-detection state pre usera
→ failure count a timestamps
→ calculated wait/disabled state
→ subsequent attempt allowed alebo rejected
```

Brute-force state nie je business user enabled flag. User môže byť enabled a súčasne dočasne blocked attack-detection mechanizmom. Permanent lockout alebo admin disable majú odlišné recovery a audit paths.

Distributed cluster musí poskytovať konzistentný enough state pre attack detection. Node restart alebo cache behavior nesmie byť predpokladaný reset bez evidence. Reverse proxy a source IP information môžu pomáhať telemetry, ale lockout je typicky user-centric a môže byť zneužitý na denial of service voči známym usernames.

## 7. Enumeration a quick-login controls

Login a reset UI nesmú spoľahlivo prezradiť, či username/email existuje. Response text, status, timing a email delivery behavior môžu vytvoriť enumeration oracle. Uniform UI response nestačí, ak existujúci user spustí drahý flow a neexistujúci user sa vráti výrazne rýchlejšie.

Quick Login Check a minimum wait pomáhajú reagovať na extrémne rýchle attempts. Nie sú náhradou za edge rate limiting, bot detection, breached-password controls a MFA. Source NAT môže spojiť legitímnych users do jednej IP cohorty, preto IP-only blocking potrebuje opatrný design.

## 8. Attack-detection read-back a reset

Admin API poskytuje brute-force status pre konkrétneho stable user ID a operáciu na jeho odstránenie:

```bash
USER_ID="$({
  kcadm.sh get users -r atlas-prod \
    -q username=alice.payments \
    --fields id,username,enabled
} | jq -er '.[0].id')"

kcadm.sh get "attack-detection/brute-force/users/${USER_ID}" \
  -r atlas-prod
```

Read-back preukazuje current attack-detection representation v oslovenom deployment/realm-e. Nepreukazuje source attempts, correct user resolution ani downstream session status.

Reset countera:

```bash
kcadm.sh delete "attack-detection/brute-force/users/${USER_ID}" \
  -r atlas-prod
```

Delete je mutation. Má sa vykonať až po identity verification a containment of attack source. Counter reset bez password/MFA recovery môže iba okamžite umožniť attackerovi pokračovať.

## 9. Reset Credentials flow

Forgot-password path používa realm Reset Credentials flow. Flow typicky identifikuje usera, odošle signed action link, overí token a vykoná required action ako Update Password.

```text
recovery request
→ user identification bez enumeration leak-u
→ action-token issue
→ email delivery
→ browser opens link
→ signature, action, user, lifespan a client/redirect validation
→ update-password required action
→ authoritative credential mutation
→ force login alebo session continuation podľa policy
```

Flow alias a execution graph sú versionované operational subjects. Custom reset flow môže odstrániť alebo pridať identity verification, OTP, broker reauthentication alebo helpdesk step. „Forgot password funguje“ nepreukazuje bezpečný user resolution ani post-reset session behavior.

## 10. Action token, email a redirect boundary

Reset link je bearer credential počas svojho lifespan-u. Mailbox compromise, forwarding, browser history, proxy logs a support tickets môžu token odhaliť. Link musí byť single-purpose, time-bound a viazaný na exact user/action/client/redirect context.

Expired alebo replayed link musí zlyhať. Ak user požiada o nový reset, policy musí definovať, či starší link zostáva platný. Application nesmie považovať návrat na redirect URI za dôkaz úspešnej mutation bez server-side session/user evidence.

Email verification status nie je dôkaz current mailbox control. High-risk recovery môže potrebovať additional factor alebo helpdesk proofing, najmä po email-change incidente.

## 11. Force login po resete a federovaní users

Po reset password flowe môže configuration vyžadovať nový login. To je bezpečnejšie než automaticky pokračovať v session, ktorú mohol začať attacker. Pri federovaných users je force-login obzvlášť dôležitý, pretože user storage provider môže mutation spracovať odlišne a Keycloak nemá istotu, že current authentication context zostal validný.

```text
password reset success
→ no automatic privileged application continuation
→ fresh authentication proti current credential authority
→ new user/client session
```

Fresh login stále neznamená revokáciu starších sessions. Je to verification successor credentialu. Descendant cleanup sa rieši samostatne.

## 12. Account recovery a MFA reset

Recovery nie je iba password reset. User môže stratiť WebAuthn authenticator, OTP device, email alebo všetky faktory. Každý reset factoru znižuje assurance na úroveň recovery proofingu.

Helpdesk workflow musí zachovať stable user ID, žiadateľa, admin identity, ticket, overovacie evidence, resetovaný credential ID/type, timestamp a session actions. Helpdesk nemá prijať iba knowledge-based answers, ktoré attacker získa z verejných alebo uniknutých dát.

Bezpečný recovery môže:

```text
zablokovať high-risk operations
→ overiť identity podľa approved proofing
→ odstrániť compromised credential
→ priradiť required action pre successor credential
→ revoke-nuť affected sessions/tokens
→ vykonať fresh login a second-device test
```

## 13. Session a token descendants po zmene passwordu

Password mutation neprepíše už vydaný access token. Offline-validating resource server môže token akceptovať až do expiry. Refresh/offline token a Keycloak sessions môžu pokračovať podľa realm/session policy a explicitných revocation actions. Local application session môže zostať ešte dlhšie.

```text
credential generation P-17 compromised
→ sessions S1, S2
→ refresh tokens R1, R2
→ access tokens A1..An
→ local sessions L1, L2

password reset → P-18
≠ automatické odstránenie všetkých descendants
```

Incident policy musí určiť realm not-before, user session logout, offline-session revocation, application backchannel logout a API cache invalidation. Broad realm-wide not-before má veľký blast radius a nemá sa používať bez scope analýzy.

## 14. Connected incident `KC-PAY-68`

Atlas password policy vyžadovala 12 znakov a jednu číslicu. Brute-force detection mala max 30 failures a krátky wait. Credential-stuffing campaign používala pomalé distributed attempts, takže jednotlivý user sa dlho nedostal do lockout-u.

Po compromise účtu `alice.payments` attacker vytvoril application session a refresh token. Alice použila Forgot Password a zmenila password. Reset flow ju automaticky vrátil do account console a support incident uzavrel, pretože old password už nefungoval.

Old refresh token však zostal použiteľný a vytváral nové access tokens. Settlement application mala vlastnú 8-hodinovú session a nekontrolovala Keycloak session revocation. Attacker pokračoval v approvals.

```text
credential stuffing
→ valid password login
→ Keycloak + application sessions
→ password reset P-18
→ old password rejects
→ old refresh/application sessions remain
→ continued business access
```

Recovery zaviedla breached-password screening, nižší bounded brute-force threshold, edge telemetry, force-login po resete, logout all user sessions pri confirmed compromise, offline-token inventory, application backchannel/session invalidation a API denial pre predecessor session generation.

## 15. Evidence-preserving containment a recovery

Zachovaj user internal ID, credential authority/provider, password-policy export, brute-force realm settings, per-user attack status, login events a source cohort, reset-flow graph, action-token issue/use timestamps, credential mutation admin event, session IDs, token hashes a business operation IDs. Password, hash, reset token a OTP seed sa do incident reportu nekopírujú.

Containment môže dočasne disable-nuť usera alebo high-risk operations, revoke-nuť sessions a zablokovať suspicious source patterns. Recovery vytvorí successor credential, odstráni attack-detection state až po proofingu, vykoná fresh login a uzavrie token/application descendants.

## 16. Positive, recovery a forbidden acceptance

Positive path:

```text
legitímny user po approved recovery
→ successor password spĺňa policy
→ fresh authentication succeeds
→ required MFA succeeds
→ new intended application session
→ protected operation succeeds
```

Forbidden paths:

```text
old password
→ rejects

expired alebo replayed reset link
→ rejects

wrong client/redirect pri action token-e
→ rejects

attacker refresh token alebo old application session
→ rejects podľa incident revocation contractu

helpdesk reset bez approved proofing
→ administratívny workflow rejects

brute-force counter reset bez credential recovery
→ forbidden operational procedure
```

Second-login test používa nový browser. Second-node test overí cluster consistency. Federated-user test overí actual LDAP/AD authority a fresh login. Second reset request overí predecessor action-token behavior.

## 17. Troubleshooting a anti-patterny

Pri „user je zablokovaný“ oddeľ `enabled=false`, brute-force temporary/permanent state, LDAP/AD lockout, expired credential, required action a application-local denial. Pri „reset prešiel, ale starý access funguje“ sleduj token TTL, user sessions, offline sessions, not-before, resource-server validation a local application session.

Anti-patterny sú: `silná password policy = odolnosť proti stuffing-u`, `lockout = attacker odstránený`, `counter reset = recovery`, `email verified = mailbox stále bezpečný`, `password reset = všetky sessions revoked`, `old password rejects = incident closed`, `force login = descendant revocation`, `temporary password = bezpečný delivery channel` a `Keycloak policy riadi LDAP password bez overenia provider mode-u`.

## 18. Kontrolné otázky

- Kto vlastní password credential: Keycloak, LDAP/AD alebo custom provider?
- Ktorá exact password-policy a hashing generation platí pre nový credential?
- Ako sa odlišuje user enabled state od brute-force attack state?
- Aké online, edge a breached-password controls dopĺňajú policy?
- Ktorý Reset Credentials flow a action-token lifespan sa použil?
- Je po resete vyžadovaný fresh login?
- Ktoré Keycloak, refresh/offline a application sessions zostali?
- Ako sa overuje helpdesk identity a MFA reset?
- Prešli old-password, expired-link, replay, wrong-redirect, old-session, second-node a federated-user paths?

## Glossary impact

Relevantné pojmy: Keycloak password policy, credential generation, password hashing provider, password history, temporary password, brute-force detection, attack-detection state, quick-login check, reset-credentials flow, reset action token, force login after reset, account recovery proofing, credential stuffing, session descendant a recovery acceptance matrix.

## Primárne zdroje

- [Keycloak — Server Administration Guide: Password Policies, Brute Force Detection and Reset Credentials](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak Admin REST API — Attack Detection](https://www.keycloak.org/docs-api/latest/rest-api/)
- [NIST SP 800-63B — Authentication and Lifecycle Management](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: MFA, WebAuthn, passkeys a step-up authentication](mfa-webauthn-passkeys-and-step-up-authentication.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Identity brokering →](identity-brokering.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
