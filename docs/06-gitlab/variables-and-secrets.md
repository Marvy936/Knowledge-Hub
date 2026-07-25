# Variables a secrets

## Metadata

- Status: Learning
- Level: L2
- Domain: GitLab

GitLab CI/CD variables prenášajú configuration a runtime hodnoty do pipelines a jobs. Nie každá variable je secret a nie každý secret má byť uložený v GitLabe. Bezpečný návrh musí vysvetliť, odkiaľ hodnota pochádza, ktorá hodnota vyhrá, v ktorej fáze existuje, ktorému jobu sa sprístupní, čo s ňou môže job urobiť a ako sa hodnota rotuje alebo revokuje.

## 1. Mental model

```text
value source
→ precedence a scope resolution
→ pipeline/job eligibility
→ runtime injection alebo secret retrieval
→ použitie
→ redaction a audit
→ cleanup
→ expiration / rotation / revocation
```

Secret bezpečnosť nie je vlastnosť jedného checkboxu. Je výsledkom celého exposure graphu.

## 2. Kategórie hodnôt

Rozlišuj:

- **Public configuration —** napríklad názov komponentu alebo build mode bez citlivosti.
- **Internal configuration —** nie je tajná, ale nemusí patriť do verejného repository.
- **Secret material —** password, private key, API token alebo signing key.
- **Identity assertion —** krátkodobý ID token, ktorý dokazuje job context.
- **Derived credential —** short-lived cloud alebo Vault credential získaný federáciou.
- **Generated metadata —** artifact digest, environment URL alebo release ID.
- **User-controlled input —** manual alebo trigger parameter, ktorý musí byť validovaný.

Kategória určuje storage, scope, logging, retention a incident response.

## 3. Variable sources

Hodnota môže pochádzať z:

- `.gitlab-ci.yml`,
- predefined variables,
- project, group alebo instance settings,
- pipeline policy alebo triggera,
- manual pipeline inputu,
- schedule,
- downstream pipeline forwarding,
- dotenv reportu,
- external secret provideru,
- runtime aplikácie alebo deployment platformy.

Každý source má inú dôveru. Hodnota z chráneného group settingu a hodnota z manual inputu nesmú byť považované za ekvivalentné iba preto, že používajú rovnaký key.

## 4. Effective value

Pri duplicitnom key vzniká effective value podľa GitLab precedence pravidiel a konkrétneho pipeline contextu.

Bezpečný postup:

1. inventarizuj všetky možné sources,
2. urč povolené override body,
3. zisti, ktorá hodnota vyhrá,
4. over scope a pipeline source,
5. validuj výsledok pred citlivou operáciou,
6. zaloguj ne-secretnú identitu rozhodnutia.

Nepoužívaj rovnaký key na rozdielne významy. `TARGET` ako branch, environment aj hostname vytvára neauditovateľný override model.

## 5. Override authorization

Security-sensitive hodnoty nemajú byť ľubovoľne prepísateľné používateľom alebo upstream pipeline.

Chráň najmä:

- artifact digest,
- deployment environment,
- image alebo template reference,
- cloud role/identity,
- secret path,
- registry namespace,
- destructive-operation flag,
- migration mode.

Manual input `DEPLOY_IMAGE=...` môže obísť build a promotion evidence. Preferuj výber z overeného release manifestu alebo presný digest validovaný proti registry policy.

## 6. Availability phases

Nie každá variable existuje v každej fáze:

- pri pipeline creation,
- pri job graph construction,
- pri runner execution,
- po upstream jobe,
- v downstream pipeline.

`workflow:rules` alebo job `rules` nemôžu spoľahlivo používať hodnotu, ktorá vznikne až počas script execution. Phase mismatch môže vytvoriť missing jobs alebo neočakávané defaults.

## 7. Variable type

GitLab podporuje bežnú variable a file-type variable.

File type vytvorí dočasný súbor a environment variable obsahuje jeho path. Je vhodný pre:

- CA bundle,
- certificate,
- kubeconfig,
- JSON credential document,
- signing material,
- tool configuration s citlivým obsahom.

Job má čítať path, nie vypisovať súbor. Cleanup musí odstrániť dočasný file aj pri cancellation alebo failure.

## 8. Masked value

Masking sa pokúša redigovať presnú hodnotu v job logu. Chráni pred náhodným vypísaním, nie pred úmyselnou exfiltráciou.

Secret môže uniknúť cez:

- encoding alebo hash fragmenty,
- rozdelenie na časti,
- process arguments,
- artifact alebo cache,
- debug dump,
- HTTP request,
- child process environment,
- external logs,
- malicious script.

Job, ktorý dostane secret, musí byť považovaný za schopný secret odoslať.

## 9. Hidden value

Hidden variable znižuje možnosť neskoršieho zobrazenia hodnoty v UI. Neobmedzuje runtime job, ktorý ju dostane.

Hidden state rieši human readback. Protected scope, trusted code, runner isolation a external-secret policy riešia execution exposure.

## 10. Protected variable

Protected variable je dostupná iba v eligible protected-ref context-e podľa GitLab pravidiel.

Bezpečnosť závisí aj od:

- protection branchu alebo tagu,
- allowed-to-push a allowed-to-merge policy,
- pipeline code a included templates,
- runner poolu,
- fork/MR contextu,
- downstream pipeline forwarding,
- environment scope.

Protected variable neznamená production-only variable.

## 11. Environment scope

Environment scope obmedzuje hodnotu podľa názvu environmentu alebo patternu.

Riziká:

- job deklaruje podobný, ale nechránený názov,
- wildcard match je širší než očakávanie,
- staging fallback vyhrá nad production-specific hodnotou,
- review app sa pomenuje ako produkčný scope,
- environment sa určuje z user-controlled inputu.

Environment name je súčasť authorization contractu. Musí byť kanonický, validovaný a chránený spolu s deploy jobom.

## 12. Group a instance variables

Vyšší namespace scope zväčšuje blast radius. Group variable používaj iba vtedy, keď:

- skutočne patrí celej group boundary,
- všetky dedičné projekty majú rovnakú dôveru,
- owner a consumers sú známi,
- environment/protected scopes obmedzujú exposure,
- project transfer alebo subgroup zmena je auditovaná.

Secret pre jednu aplikáciu nemá byť dostupný stovkám projektov iba kvôli pohodliu.

## 13. Variable expansion a composition

Expansion môže skladať hodnoty z iných variables, ale komplikuje precedence, quoting a masking.

Preferuj:

- jasné atomic values,
- explicitné composition v kontrolovanom scripte,
- validované enumy,
- pevné command templates,
- žiadne `eval` nad variable obsahom.

Variable je data, nie shell code.

## 14. Manual a trigger inputs

Manual alebo trigger variable je user-controlled input. Validuj:

- type,
- enum alebo allowlist,
- dĺžku,
- format,
- environment,
- URL/hostname,
- artifact digest,
- path traversal,
- destructive intent.

Citlivý input má byť typed a policy-bound. Voľný text nie je vhodný na výber produkčnej identity alebo commandu.

## 15. Downstream a child pipelines

Variables môžu prechádzať do child alebo multi-project pipeline. Pred forwardingom urči:

- ktoré keys sú potrebné,
- či sú secrets,
- aký je target-project trust,
- kto môže meniť downstream pipeline code,
- aký runner a environment downstream používa,
- či sa hodnoty ukladajú v logs, dotenv alebo artifacts.

Preferuj explicitný allowlist. Forward všetkého runtime environmentu vytvára neviditeľný privilege propagation.

## 16. Dotenv report

Dotenv report je vhodný pre non-secret metadata, napríklad:

- artifact digest,
- version,
- environment URL,
- deployment ID,
- generated path.

Je to artifact s vlastným access a retention modelom. Nepoužívaj ho ako implicitný secret transport, pokiaľ nie je celý downstream a storage lifecycle navrhnutý pre citlivé dáta.

## 17. Predefined variables

Predefined variables poskytujú context projektu, commitu, pipeline, jobu, registry a environmentu.

Pri security rozhodnutí over:

- pipeline source,
- ref a jeho protected stav,
- source/target project,
- commit SHA,
- environment identity,
- job identity,
- availability phase.

Samotný branch name nie je dôkaz trusted pipeline contextu.

## 18. `CI_JOB_TOKEN`

`CI_JOB_TOKEN` je krátkodobá GitLab job identity pre podporované API a cross-project operácie.

Navrhni:

- explicitný inbound allowlist target projektu,
- minimum required endpoints,
- source-project trust,
- protected-ref podmienku podľa rizika,
- žiadne logovanie alebo artifact export,
- audit použitia,
- oddelenie read a publish use cases.

Job token nemá byť univerzálny organization-wide service credential.

## 19. ID tokens a OIDC federation

Preferovaný model pre cloud alebo secret provider:

```text
GitLab job
→ podpísaný ID token
→ provider overí issuer, audience a claims
→ vydá krátkodobý credential
→ job vykoná scoped operáciu
→ credential expiruje
```

Provider policy má overovať podľa potreby:

- issuer,
- audience,
- project alebo namespace,
- ref a protection,
- environment,
- pipeline source,
- job účel,
- token lifetime.

Audience musí byť konkrétna. Provider nemá akceptovať token určený inej službe.

## 20. External secret provider

External provider oddeľuje secret storage a authorization od GitLab variable storage.

Lifecycle:

```text
job identity
→ authenticate/federate
→ authorize konkrétny secret path
→ issue lease alebo value
→ use
→ revoke/expire
→ audit
```

Výhody:

- kratšia životnosť,
- centrálna rotácia,
- presnejší access policy,
- usage logs,
- menší počet statických credentials.

External provider nepomôže, ak job dostane príliš širokú role alebo secret vypíše do artifactu.

## 21. Token taxonomy

Rozlišuj:

- personal access token,
- project access token,
- group access token,
- deploy token,
- `CI_JOB_TOKEN`,
- runner authentication token,
- ID token,
- cloud/provider derived credential.

Každý typ má inú subject identity, scope, lifetime, revocation a audit. Osobný token človeka nie je vhodná trvalá automation identity.

## 22. Secret rotation

Rotation contract:

1. identifikuj secret a ownera,
2. inventarizuj consumers,
3. vytvor novú hodnotu alebo key version,
4. zabezpeč dual-validity alebo kontrolovaný cutover,
5. rolloutni consumers,
6. over použitie novej hodnoty,
7. revokuj starú,
8. skontroluj zlyhané alebo offline consumers,
9. uchovaj audit evidence.

Rotation, ktorá iba zmení GitLab variable, môže nechať starý credential aktívny u providera.

## 23. Expiration a revocation

Každá non-human credential potrebuje:

- účel,
- ownera,
- scope,
- expiration,
- rotation cadence,
- usage telemetry,
- revocation runbook.

Expiration je plánovaný koniec. Revocation je okamžité zneplatnenie pri incidente, zmene ownershipu alebo nepotrebnosti.

## 24. Secret cleanup

Po jobe odstráň:

- file-type variable files,
- temporary certificates a keys,
- cloud CLI profiles,
- kubeconfig,
- package-manager auth,
- mounted secret volumes,
- generated tokens,
- debug output.

Persistent runner musí overiť cleanup aj pri cancellation. Ephemeral worker znižuje riziko, ale persistent volumes a external logs môžu secret zachovať.

## 25. Logs, traces a debugging

Kontroluj:

- shell tracing,
- environment dumps,
- HTTP debug headers,
- PowerShell verbose/debug output,
- crash dumps,
- tool config print,
- third-party CI observability agents.

Redakcia GitLab logu nemusí odstrániť secret z externého log backendu. Debug režim pre production credentials musí mať explicitný approval a cleanup.

## 26. Artifacts a cache

Pred uploadom kontroluj:

- `.env`,
- credential directories,
- kubeconfig,
- certificates,
- package auth files,
- debug archives,
- Terraform state/plan s citlivými hodnotami,
- generated configuration.

Použi explicitné paths. `untracked` alebo celý workspace je nebezpečný default.

## 27. Fork a untrusted MR pipelines

Untrusted code nesmie dostať citlivé variables iba preto, aby pipeline bola „rovnaká ako na main“.

Bezpečný model:

```text
untrusted MR validation
→ bez production secrets a privileged runnera
→ merge/review
→ trusted post-merge build/deploy
```

Ak maintainer spúšťa parent-project pipeline pre fork MR, musí presne rozumieť, ktorý pipeline code a commit sa vykoná.

## 28. Secret leak response

Pri podozrení na leak:

1. revokuj credential u zdrojového provideru,
2. zastav jobs, ktoré ho môžu ďalej používať,
3. identifikuj logs, artifacts, caches a downstream pipelines,
4. rotuj súvisiace alebo odvodené credentials,
5. audituj API, registry, cloud a deployment activity,
6. odstráň alebo obmedz citlivé uložené dáta podľa možností,
7. oprav exposure path,
8. pridaj prevention alebo detection kontrolu,
9. dokumentuj incident a affected scope.

Odstránenie hodnoty z GitLab UI secret nerevokuje.

## 29. Committed secret

Ak sa secret dostane do Git history:

- okamžite ho revokuj,
- urč, kde bol pushnutý alebo mirrorovaný,
- prehľadaj pipelines, artifacts a packages,
- rotuj dependent credentials,
- podľa potreby rewrite-ni history, ale nepovažuj to za revokáciu,
- pridaj secret detection a pre-commit prevention.

Secret možno existuje v klonoch aj po history rewrite.

## 30. Observability a inventory

Sleduj:

- počet secrets podľa scope-u,
- credentials bez ownera alebo expiry,
- blížiace sa expirácie,
- group-wide secret exposure,
- OIDC/provider authorization failures,
- stale alebo nepoužívané tokens,
- manual overrides citlivých keys,
- secret-detection findings,
- rotation success a failed consumers.

Neloguj samotné hodnoty. Používaj secret ID, version alebo provider path.

## 31. Diagnostický postup

Keď variable chýba alebo má nesprávnu hodnotu:

1. identifikuj pipeline source a job,
2. zisti všetky sources rovnakého key,
3. aplikuj precedence,
4. over protected ref a environment scope,
5. over availability phase,
6. skontroluj manual/trigger/downstream forwarding,
7. over expansion a quoting,
8. over runner injection a file cleanup,
9. pri external providerovi over issuer, audience, claims a lease,
10. nezverejňuj hodnotu pri diagnostike.

## 32. Typické anti-patterny

### Všetko je uložené ako variable

Configuration, identity aj long-lived secrets nemajú rovnaký lifecycle.

### Masked znamená bezpečný

Malicious job môže hodnotu transformovať alebo odoslať.

### Group secret pre jednu službu

Blast radius zahŕňa všetky dedičné projekty.

### Personal token ako produkčná automation identity

Lifecycle závisí od človeka a jeho membershipu.

### Free-text manual deployment input

Používateľ môže zvoliť neoverený artifact, target alebo command.

### Forward všetkých variables downstream

Privilege sa neviditeľne prenáša do iného project a pipeline trust contextu.

### Rotácia bez revokácie starej hodnoty

Pôvodný credential ostáva použiteľný.

## 33. Praktický rozhodovací rámec

Pre každú citlivú hodnotu odpovedz:

1. Je to configuration, secret alebo identity assertion?
2. Kde je source of truth?
3. Ktoré sources ju môžu prepísať?
4. V ktorej fáze je dostupná?
5. Ktoré projects, refs, environments a jobs ju dostanú?
6. Môže prejsť do downstream pipeline, artifactu alebo cache?
7. Je vhodnejší external provider a short-lived credential?
8. Ako sa hodnota rotuje a revokuje?
9. Ako sa čistí po jobe?
10. Ako sa zistí a rieši leak?

## 34. Kontrolný checklist

- hodnoty sú klasifikované;
- effective-value precedence je známa;
- critical keys nemožno ľubovoľne override-nuť;
- protected a environment scopes sú testované;
- environment name je kanonický;
- untrusted jobs nemajú secrets;
- downstream forwarding používa allowlist;
- OIDC claims a audience sú presné;
- static credentials majú ownera a expiry;
- external secret leases sú krátkodobé;
- artifacts, caches a logs sú kontrolované;
- rotation zahŕňa revokáciu;
- leak response je zdokumentovaný.

## 35. Kontrolné otázky

1. Aký je rozdiel medzi variable, secretom a identity tokenom?
2. Ako vzniká effective value pri viacerých sources?
3. Prečo masking nezastaví úmyselnú exfiltráciu?
4. Čo protected variable skutočne obmedzuje?
5. Prečo environment scope závisí od dôveryhodného environment name?
6. Ktoré variables môžu byť dostupné pri pipeline creation?
7. Aké riziko prináša downstream forwarding?
8. Ako funguje OIDC workload federation?
9. Aký je rozdiel medzi expiration a revocation?
10. Prečo rotation nekončí zmenou hodnoty v GitLabe?
11. Ako bezpečne diagnostikovať chýbajúcu variable?
12. Čo treba urobiť po committed secret incidente?

## Summary

GitLab variable je mechanizmus prenosu hodnoty, nie automaticky bezpečný secret store. Dôveryhodný návrh pozná source, precedence, phase, scope, pipeline trust, runtime exposure, downstream propagation, cleanup a lifecycle hodnoty. Masking chráni najmä pred náhodným logovaním. Pre citlivé produkčné oprávnenia je silnejší model GitLab ID token, presná provider policy a krátkodobý credential. Rotation, revocation a leak response musia pokrývať aj providera, logs, artifacts, cache a všetkých consumers.

## Glossary impact

Relevantné pojmy: CI/CD variable, effective value, variable precedence, file-type variable, masked variable, hidden variable, protected variable, environment scope, external secret provider, ID token, OIDC federation, workload identity, `CI_JOB_TOKEN`, deploy token, secret rotation, revocation a variable forwarding.

## Oficiálna dokumentácia

- [CI/CD variables](https://docs.gitlab.com/ci/variables/)
- [Use external secrets in CI/CD](https://docs.gitlab.com/ci/secrets/)
- [ID token authentication](https://docs.gitlab.com/ci/secrets/id_token_authentication/)
- [CI/CD job token](https://docs.gitlab.com/ci/jobs/ci_job_token/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Runners a executors](runners-and-executors.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Artifacts a cache →](artifacts-and-cache.md)
<!-- KNOWLEDGE-NAVIGATION:END -->