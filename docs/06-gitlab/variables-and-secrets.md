# Variables a secrets

## Metadata

- Status: Learning
- Level: L2
- Domain: GitLab

GitLab CI/CD variable je vstup do pipeline alebo jobu. Môže niesť bežnú konfiguráciu, citlivú hodnotu, user-controlled parameter alebo identity assertion. Bezpečnosť nevytvára checkbox `masked`; vzniká až po vyriešení source-u, precedence, availability phase, pipeline trustu, runtime exposure, propagation, cleanupu a revocation lifecycle-u.

```text
value contract
→ possible sources a precedence
→ pipeline/job eligibility
→ effective non-secret configuration
→ job identity assertion
→ short-lived secret/credential retrieval
→ bounded use
→ redaction a propagation controls
→ cleanup
→ rotation, expiration alebo revocation
```

Kritické pravidlo: hodnota zobrazená v GitLab settings nie je automaticky hodnota, ktorú job skutočne použil.

## 1. Nosný model: effective-value a credential lifecycle

Pre každý key existujú dve odlišné otázky:

```text
Aká effective hodnota vznikla?
→ source + precedence + scope + phase + forwarding

Akú capability táto hodnota alebo identity poskytla?
→ runtime exposure + provider authorization + use + lifetime
```

Konfiguračná chyba môže zvoliť nesprávny environment. Secret exposure môže umožniť neautorizovanú operáciu. OIDC claim môže byť správny, ale provider policy príliš široká.

Troubleshooting preto nesmie vypisovať všetky variables. Musí rekonštruovať provenance bez odhalenia hodnôt.

## 2. Nosný scenár: Atlas production deployment

Atlas deploy job používa:

```text
RELEASE_MANIFEST = immutable non-secret release identity
DEPLOY_ENV = typed enum, canonical value production
CLOUD_ROLE = non-secret provider role identifier
VAULT_PATH = non-secret secret path
GitLab ID token = krátkodobá identity assertion
cloud credential = derived short-lived secret
```

Desired flow:

```text
protected main pipeline
→ resolved deploy job
→ kanonický environment production
→ release manifest určí artifact digest D42
→ GitLab vydá ID token pre audience cloud-sts
→ provider overí project/ref/environment/job claims
→ vydá 10-minútový deploy credential
→ job nasadí iba D42 do Atlas production
→ credential expiruje a temporary files sa odstránia
```

Manual operator smie zvoliť iba schválený release manifest z typed inputu. Nesmie voľným textom prepísať digest, cloud role, secret path alebo command.

## 3. Hodnoty majú odlišné kategórie

- **Public configuration:** build mode alebo component name.
- **Internal configuration:** endpoint alebo feature matrix bez secretu.
- **Secret material:** static token, private key alebo password.
- **Identity assertion:** ID token dokazujúci job context.
- **Derived credential:** krátkodobý cloud/Vault credential.
- **Generated metadata:** artifact digest, deployment ID alebo URL.
- **User-controlled input:** manual, API, schedule alebo trigger parameter.

Tieto kategórie nemajú rovnaký storage ani lifecycle. Artifact digest patrí do provenance, private key nie. ID token má krátku lifetime a audience, statický token potrebuje rotation a revocation.

## 4. Value source a provenance

Hodnota môže pochádzať z:

```text
root/resolved CI configuration
predefined GitLab context
project/group/instance settings
pipeline policy alebo trigger
manual/API/schedule input
downstream forwarding
dotenv/report artifact
external secret provider
runtime platform
```

Provenance record pre citlivý key neukladá hodnotu. Ukladá:

```text
key name
source type a scope
source revision/ID
protected/environment match
override decision
effective-value fingerprint alebo version
consumer job
```

Rovnaký key z group settingu a manual triggera nemá rovnakú dôveru.

## 5. Precedence je authorization boundary

Ak viaceré sources definujú rovnaký key, GitLab vytvorí effective value podľa platformových precedence pravidiel a konkrétneho pipeline contextu.

Bezpečný návrh:

```text
inventarizuj sources
→ explicitne povoľ alebo zakáž override
→ vyrieš precedence
→ validuj effective value
→ viaž decision na immutable subject
```

Security-sensitive keys:

- artifact digest alebo release manifest;
- environment a deployment tier;
- cloud role alebo identity audience;
- registry namespace;
- secret path;
- migration/restore mode;
- destructive-operation flag.

Tieto keys nemajú byť neobmedzene prepísateľné manual alebo upstream variable-om.

## 6. Availability phase určuje, kde možno hodnotu použiť

Rozlišuj:

```text
pre-pipeline / pipeline creation
→ include a workflow selection

pipeline graph
→ job rules a job definition

runner execution
→ runtime variables, file secrets a tokens

after-job output
→ dotenv, artifacts a downstream metadata
```

Job output nemôže spätne rozhodnúť, či ten istý job alebo pipeline vznikne. Ak runtime discovery určuje ďalší graph, vytvor plan artifact a child pipeline s explicitným contractom.

Phase mismatch často vyzerá ako prázdna variable alebo chýbajúci job, ale mechanizmus je nesprávne načasovanie, nie nevyhnutne secret distribution failure.

## 7. Scope a environment identity

Protected variable filtruje podľa trusted ref contextu. Environment-scoped variable filtruje podľa deklarovaného environment name/patternu.

```text
value source
+ protected eligibility
+ canonical environment match
+ pipeline/ref context
+ precedence
→ available alebo absent
```

Ak deploy job deklaruje `production-new`, variable scoped na `production` môže chýbať — alebo širší wildcard môže nečakane vyhrať. Environment name je security input a musí byť kanonický, trusted a mapovaný na skutočný runtime target.

Protected variable neznamená, že ju môže dostať iba bezpečný code. Chránený ref môže obsahovať kompromitovaný include alebo škodlivú zmenu.

## 8. Masked, hidden a file-type riešia odlišné problémy

### Masked

Rediguje presnú hodnotu v GitLab job logu. Nezastaví encoding, fragmentáciu, artifact upload, network exfiltration ani úmyselný script.

### Hidden

Znižuje human readback z UI. Runtime job ju stále dostane.

### File type

Vytvorí temporary file a variable nesie jeho path. Je vhodný pre certifikát, CA bundle, kubeconfig alebo JSON secret, ale potrebuje cleanup aj pri cancellation.

Job, ktorý secret dostane, sa musí považovať za schopný ho prečítať a odoslať.

## 9. Pipeline trust predchádza secret injection

Atlas oddeľuje:

```text
untrusted MR validation
→ bez production secrets a privileged identity

trusted post-merge build
→ iba build-scoped credentials

release/deploy job
→ exact protected context + environment + short-lived identity
```

Fork alebo MR pipeline nemá dostať secrets iba preto, aby bola identická s main pipeline. Funkčnú validáciu možno vykonať so synthetic credentials alebo isolated test targetom.

## 10. ID token a workload federation

Preferovaný production model:

```text
GitLab job
→ podpísaný ID token
→ provider overí issuer + audience + claims
→ provider vydá bounded credential
→ job vykoná konkrétnu operáciu
→ credential expiruje
```

Provider policy podľa rizika overuje:

- project/namespace;
- source/ref a protected status;
- pipeline source;
- environment;
- job name alebo purpose;
- audience;
- token lifetime;
- prípadne release/deployment subject.

Príliš všeobecná audience alebo namespace wildcard môže premeniť krátkodobý token na širokú capability.

## 11. `CI_JOB_TOKEN` a cross-project propagation

`CI_JOB_TOKEN` je krátkodobá GitLab job identity pre podporované API a cross-project operácie. Target project má explicitne povoliť relevantný source project a minimum capability.

Downstream forwarding potrebuje allowlist:

```text
metadata keys
→ explicitne forward

secret keys
→ radšej znovu získať z identity v downstream context-e
```

Forward všetkých variables môže preniesť privilege do projektu s iným ownerom, CI code-om, runnerom a environment policy.

## 12. External secret provider

External provider oddeľuje storage a authorization od GitLab settings:

```text
job identity
→ authorize secret path
→ issue value/lease
→ bounded use
→ revoke/expire
→ audit
```

To neznižuje riziko, ak job môže čítať príliš široký path, vypísať secret alebo ho uložiť do artifactu. Provider audit a GitLab job provenance musia byť korelovateľné.

## 13. Manual a trigger input je nedôveryhodné data

Atlas povoľuje:

```text
release_manifest = výber z approved inventory
environment = enum staging|production
operation = enum deploy|verify|rollback
```

Nepovoľuje:

```text
IMAGE = ľubovoľný registry path
CLOUD_ROLE = ľubovoľný ARN/identifier
COMMAND = voľný shell text
SECRET_PATH = ľubovoľný path
```

Input sa validuje pred získaním privilegovanej identity. Validácia po cloud login-e už vytvorila zbytočne široké exposure okno.

## 14. Logs, artifacts, cache a child processes rozširujú exposure graph

Secret môže zostať v:

- shell trace alebo environment dump-e;
- process arguments a crash dump-e;
- package-manager configu;
- dotenv reporte;
- artifacte alebo cache;
- child process environment-e;
- external observability agentovi;
- persistent workspace alebo volume.

Masking GitLab trace nerieši externý log backend. Upload celého workspace-u je neprijateľný pri jobe s production credentials.

## 15. Rotation a revocation sú state transitions

Rotation:

```text
consumer inventory
→ vytvor novú version
→ dual-validity alebo controlled cutover
→ rollout consumers
→ over usage novej version
→ revoke starú
→ over offline/stale consumers
```

Zmena GitLab variable bez revokácie u providera ponecháva starý token aktívny.

Revocation pri incidente:

```text
revoke source credential/lease
→ stop active jobs
→ audit derived credentials a usage
→ rotate related secrets
→ odstráň exposure artifacts/cache/logs podľa možností
→ oprav policy
```

Vymazanie secretu z UI nie je revocation.

## 16. Worked failure: manual variable prepísala schválený artifact digest

Atlas deploy pipeline mala YAML default `RELEASE_MANIFEST=approved/3.12.0`. Operátor pri manuálnom spustení zadal rovnaký key s hodnotou ukazujúcou na testovací manifest.

```text
manual pipeline variable má vyššiu effective precedence
→ deploy job načíta testovací manifest
→ environment a cloud role sú produkčné
→ job nasadí digest, ktorý nebol predmetom production approvalu
```

### Príčina

Security-sensitive identity bola modelovaná ako voľne prepísateľná variable. Approval patrila inému manifestu než effective runtime value.

### Dôsledok

GitLab UI zobrazoval úspešný authorized job, ale release provenance chain bol prerušený.

### Trvalá náprava

```text
manual input je typed release ID
→ trusted job ho mapuje na server-side approved manifest
→ digest sa overí voči approval recordu
→ effective manifest ID je auditované
→ arbitrary override rovnakého keya je zakázaný
```

## 17. Worked failure: masking nezabránil úniku static tokenu

Debug job na protected branchi použil masked `PACKAGE_TOKEN`. Script vytvoril support archive:

```text
env a package-manager config
→ support/debug directory
→ artifacts: untracked
→ token sa uloží do config file-u
→ GitLab trace token neukáže
→ artifact ho však obsahuje
```

### Príčina

Tím zamieňal log redaction za runtime confinement. Artifact publication contract neobsahoval forbidden-secret scan ani explicitné paths.

### Recovery

Atlas revokoval token u registry providera, zastavil jobs, auditoval pulls/pushes, odstránil dostupné artifacts a rotoval dependent credentials.

### Trvalá náprava

- short-lived job credential namiesto static tokenu;
- explicitné artifact paths;
- secret scan pred uploadom;
- package config v temporary directory;
- cleanup aj pri failure;
- protected job bez nepotrebného debug režimu.

## 18. Worked failure: rotation zlomila offline consumer a starý token ostal platný

Tím zmenil GitLab group variable na nový API token a označil rotation za hotovú. Nočný schedule v inom projekte stále používal skopírovaný project token a provider starý token nerevokoval.

```text
hlavné pipelines používajú new token
→ dashboard vyzerá zdravo
→ offline schedule používa old token
→ old token ostáva aktívny bez ownera
→ incidentný blast radius sa nezmenšil
```

### Príčina

Chýbal consumer inventory a provider-side revocation proof.

### Náprava

Token dostal central owner, version telemetry, expiry a usage inventory. Rotation gate čaká na novú version u všetkých consumers a následné provider revocation confirmation.

## 19. Kauzálny diagnostický walkthrough

Symptom: production deploy job dostane `AccessDenied`, hoci príslušná GitLab variable existuje a predchádzajúci deployment prešiel.

### Krok 1 — stabilizuj execution subject bez zobrazenia secretu

```text
pipeline P815 / job deploy_production
source SHA S45 / resolved config C21
pipeline source a protected status
environment name production
variable key/version provenance
ID-token audience a claims fingerprint
provider role/policy revision
```

### Krok 2 — formuluj konkurenčné hypotézy

```text
H1: variable nie je dostupná pre tento ref/environment
H2: iný source s vyššou precedence vytvoril nesprávnu effective value
H3: file/variable injection na runneri zlyhala
H4: OIDC issuer/audience/claims nezodpovedajú provider policy
H5: derived credential expiroval alebo bol revoked
H6: downstream job nedostal alebo nesprávne forwardol metadata
H7: cloud operation presahuje credential scope
```

### Krok 3 — diskriminačné observation points

- variable provenance a scope match testujú H1/H2;
- runner prepare logs bez hodnoty testujú H3;
- token claims a STS/Vault audit testujú H4;
- issue/expiry/revocation timestamps testujú H5;
- parent/downstream key inventory testuje H6;
- cloud authorization decision testuje H7.

Atlas zistí, že job deklaroval environment `prod`, zatiaľ čo provider trust aj variable scope očakávali `production`. H1/H4 vysvetľujú failure; secret samotný nebol chybný.

### Krok 4 — oprav identity contract, nie hodnotu

Environment name sa vráti na canonical `production`; job získa nový ID token a derived credential. Kopírovanie static keya do jobu by obišlo správnu policy.

### Krok 5 — over outcome

```text
canonical environment matchuje GitLab aj provider policy
credential je short-lived a job-scoped
deployuje iba approved digest
po jobe credential expiruje
temporary files a downstream propagation sú prázdne
```

### Krok 6 — vráť learning

Finding sa zmení na environment-name lint, provider-claim fixture a effective-value provenance panel.

## 20. Diagnostický runbook

1. Urči pipeline/job/source/environment subject.
2. Klasifikuj key ako config, secret, identity assertion alebo user input.
3. Inventarizuj všetky sources a vyrieš precedence.
4. Over availability phase, protected status a environment scope.
5. Skontroluj explicitný downstream/child forwarding.
6. Pri federation over issuer, audience, claims, policy a lease lifetime.
7. Rozlíš absent value, wrong effective value, injection failure a authorization denial.
8. Diagnostikuj cez IDs, versions a fingerprints, nie výpis hodnoty.
9. Over cleanup, expiry a provider-side revocation.
10. Zmeň finding na scope, override, claim alebo lifecycle control.

## 21. Referenčné pravidlá

- Variable je transport hodnoty, nie automaticky secret store.
- Effective value vzniká zo source-u, precedence, scope-u a phase.
- Critical keys nemajú byť voľne override-nuteľné.
- Masking rieši náhodný log leak, nie malicious execution.
- Protected scope závisí od trusted refu, code-u, runnera a environmentu.
- Environment name je authorization input.
- Secret sa má získavať čo najneskôr a na čo najkratší čas.
- Downstream forwarding potrebuje allowlist.
- OIDC bezpečnosť závisí od audience a presných claims.
- Rotation končí provider revocation a consumer verification.
- Leak response pokrýva logs, artifacts, cache, derived credentials a externé systémy.

## 22. Časté omyly

### „Variable existuje, job ju určite používa“

Scope, precedence, phase alebo forwarding môžu vytvoriť inú effective hodnotu alebo absenciu.

### „Masked znamená bezpečný secret“

Job ho môže uložiť do artifactu alebo odoslať po sieti.

### „Protected variable je production-only“

Rozhoduje protected ref context, nie automaticky runtime target.

### „OIDC odstráni potrebu authorization návrhu“

Príliš široká provider policy vydá krátkodobý, ale stále neprimeraný credential.

### „Rotation je zmena hodnoty v GitLabe“

Bez consumer cutoveru a revokácie starého credentialu lifecycle nie je uzavretý.

## 23. Zhrnutie

Dôveryhodný Atlas value lifecycle je:

```text
klasifikovaný value contract
→ rekonštruovateľné sources a precedence
→ correct phase a trusted eligibility
→ validated effective config
→ job-scoped identity assertion
→ short-lived credential
→ bounded use a propagation
→ verified cleanup
→ rotation/revocation evidence
```

Variable troubleshooting sa nekončí kontrolou jedného settings riadku. Musí dokázať, ktorá effective hodnota a identity vznikli pre konkrétny job, prečo provider povolil alebo odmietol operáciu a či exposure capability po jobe skutočne zanikla.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Runners a executors](runners-and-executors.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Artifacts a cache →](artifacts-and-cache.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
