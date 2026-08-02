# Themes, email templates a localization

Keycloak theme nie je iba CSS skin. Login, account, admin, email a welcome themes sú runtime-rendered artifacts, ktoré môžu meniť security-relevant text, form structure, links, JavaScript, email action URLs a locale resolution. Custom FreeMarker template beží v Keycloak procese a musí sa považovať za trusted executable extension. Production acceptance preto nesleduje iba vizuálny screenshot, ale exact theme artifact, parent inheritance, template/message generation, realm selection, cache state, action-token URL, locale source a výslednú authentication alebo recovery operáciu.

Najčastejší upgrade incident vzniká vtedy, keď custom theme skopíruje starý built-in template. Nová Keycloak verzia pridá hidden field, accessibility fix, WebAuthn mediation alebo CSP-compatible resource pattern, ale custom override zostane na predecessor contracte. Login stránka môže vyzerať správne a pritom rozbiť passkey, required action alebo error handling.

## 1. Dominantný render-to-operation lifecycle

Theme lifecycle začína ešte pred renderom: release vyberie artifact a parent generation, realm zvolí theme a request určí journey aj locale. Rendered HTML alebo email je iba medzistav; authoritative výsledok vznikne až po browser/email interaction, Keycloak transaction validation a user/session mutation. Diagram preto spája supply-chain, server render, client behavior a identity outcome do jednej testovateľnej cesty.

```text
realm/client identity journey
→ selected theme type a theme name
→ deployed theme artifact generation
→ parent/import/resource inheritance
→ FreeMarker template a message bundle resolution
→ locale resolution
→ absolute frontend/resource/action URLs
→ rendered HTML/text/email
→ browser alebo email-client behavior
→ submitted authentication/required-action request
→ authoritative user/session mutation
→ second-locale a upgrade regression test
```

Render success nepreukazuje operation success. Email SMTP delivery nepreukazuje, že link smeruje na correct hostname alebo že action token je stále validný. Login screenshot nepreukazuje CSP, WebAuthn, keyboard accessibility ani correct error branch.

## 2. Exact theme subject

```yaml
themeSubject:
  keycloak:
    deploymentGeneration: kc-2026-08-02-20
    version: 26.7.0
    realm: atlas-prod
    realmRevision: realm-204
  selection:
    loginTheme: atlas-identity-v7
    accountTheme: keycloak.v3
    adminTheme: keycloak.v2
    emailTheme: atlas-identity-v7
    internationalizationEnabled: true
    supportedLocales: [en, sk, de]
    defaultLocale: en
  artifact:
    jar: atlas-keycloak-theme-7.4.1.jar
    sha256: 7f2e...
    providerPath: /opt/keycloak/providers/atlas-keycloak-theme-7.4.1.jar
    keycloakThemesDescriptorRevision: 4
    parentTheme: keycloak
    importTheme: common/keycloak
  cache:
    cacheThemes: true
    cacheTemplates: true
    staticMaxAge: 2592000
  journey:
    clientId: settlement-admin-web
    flow: atlas-privileged-browser-v5
    requiredAction: UPDATE_PASSWORD
    localeSource: ui_locales
    locale: sk
```

Theme name bez artifact digest nestačí. Rovnaký JAR filename môže byť prepísaný inými bytes. Rovnaký realm môže používať odlišný login a email theme. Account/Admin consoles môžu používať iný frontend stack a inheritance contract než login FreeMarker templates.

## 3. Theme types a responsibility

Keycloak pozná login, account, admin, email a welcome theme. Realm settings vyberajú login/account/admin/email theme; welcome theme je server-level setting. Master realm admin theme ovplyvňuje Admin Console pre master.

```text
login theme
→ authentication, registration, required-action a error pages

account theme
→ self-service account console

admin theme
→ administration console shell

email theme
→ subject, text a HTML email content

welcome theme
→ server welcome page
```

Customizácia login theme má najvyššie protocol/security riziko. Email theme má action-token phishing a absolute-URL riziko. Admin/account SPA override má upgrade compatibility riziko. Welcome theme sa nemá publikovať ako náhrada production routing/access controlu.

## 4. Parent inheritance a minimal override

Theme typicky dedí parent a imports common resources:

```properties
# themes/atlas-identity/login/theme.properties
parent=keycloak
import=common/keycloak
styles=css/atlas.css
locales=en,sk,de
contentHashPattern=resources/.+\.[0-9a-f]{8}\.(css|js)
```

Minimal override je bezpečnejší než kopírovanie všetkých templates. CSS, message bundles a images majú menší upgrade surface než full `login.ftl` override. Ak musíš override-nuť template, eviduj source Keycloak version, upstream template hash a diff.

```bash
jar tf atlas-keycloak-theme-7.4.1.jar | sort
sha256sum atlas-keycloak-theme-7.4.1.jar
unzip -p atlas-keycloak-theme-7.4.1.jar META-INF/keycloak-themes.json | jq .
```

Tieto príkazy preukazujú artifact bytes a deklarovaný theme inventory. Nepreukazujú, že JAR je loaded, realm ho vybral alebo rendered journey funguje.

## 5. Deployment a trust boundary

Production theme sa distribuuje ako versionovaný JAR v `providers/` alebo ako controlled directory v `themes/`. JAR obsahuje `META-INF/keycloak-themes.json` a theme resources. Po nasadení je potrebný restart/build lifecycle podľa deployment modelu.

FreeMarker templates sú server-rendered code. Theme z neovereného zdroja môže čítať context, generovať malicious links alebo spustiť expression/template attack v procese. Write access do `providers/` a `themes/` patrí iba trusted release automation. Admin Console nemá byť artifact deployment kanál.

```json
{
  "themes": [{
    "name": "atlas-identity-v7",
    "types": ["login", "email"]
  }]
}
```

Supply-chain acceptance zahŕňa source commit, build provenance, dependency inventory, JAR digest, image digest, loaded provider/theme inventory a realm selection.

## 6. Theme cache a development mode

Počas developmentu sa cache môže vypnúť:

```bash
bin/kc.sh start-dev \
  --spi-theme--static-max-age=-1 \
  --spi-theme--cache-themes=false \
  --spi-theme--cache-templates=false
```

Takáto konfigurácia nepatrí do production. Vypnutie cache zvyšuje filesystem/template work a môže spôsobiť latency. Production deploy používa immutable artifact a restart/rollout. Manuálne mazanie `data/tmp/kc-gzip-cache` je recovery krok, nie normálny release mechanismus.

Stale theme incident treba odlíšiť od browser/CDN cache. Evidence zahŕňa Pod/image/JAR digest, server cache state, HTTP response headers, resource URL/hash a browser cache bypass.

## 7. Login templates a protocol correctness

Login templates musia zachovať action URL, execution/tab context, hidden fields, error messages, form method, autocomplete semantics, WebAuthn/JavaScript integration a accessibility. Form nesmie posielať credential na custom endpoint.

```html
<form id="kc-form-login" action="${url.loginAction}" method="post">
  <input id="username" name="username" autocomplete="username" />
  <input id="password" name="password" type="password" autocomplete="current-password" />
  <button type="submit">${msg("doLogIn")}</button>
</form>
```

`${url.loginAction}` nesmie byť hardcoded. Authentication session/tab/execution parameters sú transaction-bound. Kopírovanie action URL do analytics alebo external scriptu môže exfiltrovať transaction data.

Custom JavaScript musí rešpektovať CSP a nesmie čítať password/OTP/WebAuthn response pre telemetry. Externé CDN scripts vytvárajú supply-chain a availability dependency na login path.

## 8. Email theme a action-token URL

Email theme má subject, plain-text body a HTML body. Message bundle môže definovať napríklad:

```properties
passwordResetSubject=Reset your Atlas password
passwordResetBody=Open this link within {2} minutes: {0}
passwordResetBodyHtml=<p>Open <a href="{0}">this password reset link</a> within {2} minutes.</p>
```

Parameter `{0}` je security-relevant action URL. Jeho hostname/scheme/path vzniká z Keycloak frontend hostname configuration a action-token contextu. Theme ho nemá prepisovať alebo obaliť cez untrusted tracking redirect.

Email images potrebujú absolute URL, preto sa používa `${url.resourcesUrl}` alebo `${url.resourcesCommonUrl}`, nie relative Path. Externé images môžu leakovať email open/IP a vytvárajú tracking/privacy contract.

SMTP acceptance:

```text
send action email requested
→ action token issued
→ theme/locale rendered
→ SMTP accepted
→ mailbox delivered
→ intended user opens exact URL
→ Keycloak validates signature, expiry, user, action a client
→ mutation succeeds
→ replay rejects
```

SMTP `250 OK` nepreukazuje mailbox delivery ani action completion.

## 9. Localization precedence

Pri zapnutej internationalization sa locale vyberá podľa dostupného contextu. Praktický precedence model zahŕňa explicitný user selection, user profile preferred locale, client `ui_locales`, persisted locale cookie, `Accept-Language`, realm default a fallback English.

```text
explicit selector
→ user preferred locale
→ client ui_locales
→ locale cookie
→ Accept-Language
→ realm default
→ English fallback
```

Locale cookie je preference, nie identity alebo authorization signal. Client nemá cez `ui_locales` meniť security semantics. Preklad musí zachovať význam action, warning, expiry a consent textu.

Realm-specific message overrides môžu prebiť theme bundle. Pri incidente treba zachytiť theme artifact aj realm localization revision.

## 10. Message bundles a format stability

Message keys sú API medzi templates a translations. Chýbajúci key môže fallbacknúť na parent/English alebo sa zobraziť nesprávne. Placeholders `{0}`, `{1}` musia mať rovnaký význam a počet vo všetkých locales.

```bash
for locale in en sk de; do
  grep -E '^(passwordResetSubject|passwordResetBody|passwordResetBodyHtml)=' \
    "theme/atlas-identity/email/messages/messages_${locale}.properties"
done
```

CI má kontrolovať required keys, duplicate keys, placeholder parity, UTF-8 decoding, HTML escaping a forbidden external URLs. Translation review je security/content review, nie iba jazyková korektúra.

## 11. Accessibility a browser matrix

Login je kritický UI. Acceptance zahŕňa keyboard-only flow, screen reader labels, focus management, contrast, error association, zoom, reduced motion a supported browser/device matrix. WebAuthn/passkey flow treba testovať na platform a roaming authenticators.

Screenshot regression je pomocný dôkaz. Nepreukazuje DOM semantics, action URLs, form submission ani required-action outcome.

## 12. Upgrade boundaries

Keycloak upgrade môže zmeniť built-in parent templates, message keys, resources, JS contracts a console versions. Pred upgrade:

```text
current theme source version/hash
→ compare overridden files s successor built-in templates
→ identify security/functional upstream changes
→ rebuild theme artifact
→ test all journeys/locales
→ deploy to canary realm/client
→ promote
```

Custom copied template, ktorý neprevezme upstream security fix, môže zachovať zraniteľnosť. Minimal overrides a automated diff znižujú risk.

## 13. Incident `KC-PAY-70`

Atlas theme skopíroval starý `login.ftl` a `webauthn-authenticate.ftl`. Po upgrade Keycloak parent theme zmenil passkey mediation a error branch, ale custom templates zostali predecessor. Login cez password fungoval, preto smoke test prešiel. Passkey-required users dostali blank page.

Email theme zároveň hardcoded `https://sso-old.atlas.example` okolo reset linku. Hostname bol migrovaný na `https://sso.atlas.example`; HTML link smeroval na starý reverse proxy, zatiaľ čo plain-text body používal correct `{0}`. Slovenský bundle mal nesprávny placeholder a expiry text tvrdil 60 minút pri reálnom 15-minútovom lifespan-e.

```text
copied template drift
→ password path green, passkey path broken

hardcoded email host + locale placeholder drift
→ misleading alebo unusable recovery link
→ support bypass a risky manual reset
```

Recovery vytvorila minimal child theme, odstránila hardcoded URLs, zaviedla placeholder parity a upstream-template diff. Acceptance pokryla login, passkey, registration, verify-email, reset-password a required actions vo všetkých locales.

## 14. Evidence-preserving recovery

Zachovaj source commit, JAR/image digest, `keycloak-themes.json`, parent/import config, overridden-file list a hashes, realm theme selections, localization/message overrides, cache settings, rendered HTML/email samples bez secrets, CSP/response headers a exact action-token URL hash.

Containment môže prepnúť realm na built-in theme, zastaviť broken locale alebo disable-nuť affected journey iba ak existuje bezpečný alternate path. Recovery nasadí successor artifact, restartne/canary-nuje Pods, read-backne realm selection a vykoná fresh journeys. Old theme artifact sa odstráni až po rollback windowe.

## 15. Acceptance matrix

Positive:

```text
fresh login/passkey/required-action journey
→ correct theme a locale
→ correct action URL
→ authoritative mutation/session succeeds
```

Recovery:

```text
successor theme rollout
→ all Pods load same artifact digest
→ browser/CDN cache dostane successor resources
→ second journey succeeds
```

Forbidden:

```text
untrusted theme JAR
→ supply-chain policy rejects

hardcoded external action URL alebo analytics exfiltration
→ CI/security review rejects

missing translation/security placeholder mismatch
→ localization gate rejects
```

Second-locale test zopakuje tú istú operation v každom podporovanom locale. Second-version test porovná custom overrides proti successor built-in templates.

## Kontrolné otázky

- Ktorý exact theme artifact, parent a realm selection sa renderovali?
- Je custom template skutočne potrebný alebo stačí CSS/message override?
- Zachováva action URL a authentication-session context?
- Sú email URLs absolute, correct-host a bez tracking redirectu?
- Sú locale precedence a message overrides zdokumentované?
- Majú translations placeholder parity a rovnakú security semantics?
- Je production cache zapnutá a rollout immutable?
- Prešli passkey, password, registration, recovery, required-action, locale, accessibility, browser a upgrade tests?

## Primárne zdroje

- [Keycloak UI customization — Working with themes](https://www.keycloak.org/ui-customization/themes)
- [Keycloak UI customization — Localization](https://www.keycloak.org/ui-customization/localization)
- [Keycloak Server Administration Guide — Themes and internationalization](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak Server Developer Guide — Theme Resource and Locale Selector SPIs](https://www.keycloak.org/docs/latest/server_development/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Events, audit, metrics a observability](events-audit-metrics-observability.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Keycloak server configuration, hostname a reverse proxy →](keycloak-server-configuration-hostname-reverse-proxy.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
