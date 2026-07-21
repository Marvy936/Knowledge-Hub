# Variables a secrets

GitLab CI/CD variables prenášajú configuration a runtime values do pipelines a jobs. Nie každá variable je secret a nie každý secret patrí do GitLab variable storage. Bezpečný návrh oddeľuje verejnú konfiguráciu, citlivé hodnoty, identity, environment scope a runtime secret retrieval.

## 1. Kategórie hodnôt

Rozlišuj:

- public configuration,
- non-secret internal configuration,
- secret material,
- identity token,
- short-lived credential,
- generated runtime value,
- artifact metadata.

Hodnota ako `DEPLOY_ENV=staging` nie je secret. Private key, cloud token alebo database password secret je.

## 2. Variable sources

Variables môžu pochádzať z:

- `.gitlab-ci.yml`,
- predefined variables,
- project settings,
- group settings,
- instance settings,
- pipeline trigger alebo manual inputu,
- schedule,
- dotenv reportu,
- downstream pipeline inputu,
- external secret provideru.

Každý source má odlišný trust, visibility a precedence model.

## 3. Precedence

Pri rovnakom key môže vyššia-precedence hodnota prepísať inú hodnotu. Preto:

- nepoužívaj rovnaký názov pre rozdielne významy,
- dokumentuj povolené override body,
- validuj critical values,
- nepredpokladaj, že YAML default zostane výslednou hodnotou.

Security-sensitive job nemá akceptovať ľubovoľný user override pre image, deployment target alebo secret path.

## 4. Variable type

GitLab podporuje najmä:

- `Variable` type — hodnota ako environment variable,
- `File` type — GitLab vytvorí dočasný súbor a variable obsahuje jeho path.

File type je vhodný pre:

- CA bundle,
- kubeconfig,
- certificate,
- JSON credential document,
- signing material.

Aplikácia má čítať path, nie vypisovať obsah do logu.

## 5. Masked variable

Masked variable sa GitLab pokúsi redigovať v job logu.

Masking nie je úplná ochrana. Secret môže uniknúť cez:

- transformáciu alebo encoding,
- rozdelenie na časti,
- artifact,
- cache,
- process arguments,
- debug output,
- external endpoint,
- malicious pipeline script.

Masking znižuje accidental disclosure, nie úmyselnú exfiltration.

## 6. Hidden variable

Masked-and-hidden hodnota sa po vytvorení nedá znovu zobraziť v UI. To znižuje riziko ľudského odhalenia, ale nemení fakt, že job s variable môže hodnotu použiť alebo odoslať.

## 7. Protected variable

Protected variable je dostupná iba v oprávnenom protected-ref pipeline context-e podľa GitLab pravidiel.

Bezpečnosť vyžaduje súčasne:

- chránený ref,
- kontrolované merge permissions,
- dôveryhodný pipeline code,
- bezpečný runner,
- obmedzené downstream access,
- audit.

Protected variable nemá byť dostupná fork alebo untrusted merge-request pipeline.

## 8. Environment scope

Variable možno obmedziť na environment alebo pattern.

Príklad:

```text
AWS_ROLE_ARN
scope: production
```

Environment scope znižuje exposure, ale názov environmentu pochádza z pipeline configuration. Chráň job, ktorý deklaruje citlivý environment.

## 9. Group variables

Group variable môže byť zdedená mnohými projects. Výhoda je centralizácia, nevýhoda veľký blast radius.

Použi group scope iba pre hodnoty, ktoré skutočne patria celej boundary. Production credential pre jednu službu nemá byť group-wide variable pre stovky projects.

## 10. Variable expansion

Variable môže podľa konfigurácie odkazovať na inú variable. Expansion komplikuje masking, quoting a precedence.

Preferuj explicitné hodnoty a jasné composition v job scripte. Secret nepoužívaj na tvorbu shell code alebo command fragmentu.

## 11. Shell injection

Nebezpečný vzor:

```bash
eval "$DEPLOY_COMMAND"
```

Variable je data, nie trusted code. Použi arrays, validáciu enumov a pevne definované commands.

## 12. Logs

Zakáž alebo kontroluj:

- `set -x`,
- PowerShell verbose/debug dump,
- environment dump,
- HTTP debug headers,
- tool config print,
- crash dump s environmentom.

Redaction po incidente nemusí odstrániť hodnotu z externého log backendu alebo downloaded artifactu.

## 13. Secrets v artifacts a cache

Pred uploadom artifacts alebo cache kontroluj:

- `.env` files,
- credentials directories,
- cloud CLI config,
- kubeconfig,
- package-manager auth files,
- temporary certificates,
- debug bundles.

Použi explicitné artifact paths a exclusions. `artifacts:untracked` môže neúmyselne priložiť secret file.

## 14. External secret providers

Pre citlivé production secrets preferuj runtime retrieval z:

- HashiCorp Vault,
- AWS Secrets Manager,
- Azure Key Vault,
- Google Cloud Secret Manager,
- iného OIDC-compatible provideru.

Job explicitne požiada o secret a provider vykoná authorization podľa identity claims.

## 15. OIDC a ID tokens

Bezpečnejší model:

```text
GitLab job
→ signed ID token
→ cloud alebo secret provider
→ short-lived scoped credential
```

Výhody:

- bez dlhodobého static key v GitLabe,
- krátka platnosť,
- audience restriction,
- claims viazané na project/ref/environment,
- jednoduchšia revokácia policy.

Overuj `aud`, issuer, project, ref protection a ďalšie claims podľa provideru.

## 16. `CI_JOB_TOKEN`

Job token poskytuje dočasnú GitLab identity pre vybrané API a cross-project operácie.

Riziká:

- príliš široký allowlist,
- použitie v nedôveryhodnom jobe,
- logovanie tokenu,
- downstream project s neočakávanými permissions,
- token reuse mimo job lifetime podľa nesprávneho návrhu.

Navrhni explicitný inbound/outbound access model.

## 17. Deploy tokens a access tokens

Rozlišuj:

- personal access token,
- project access token,
- group access token,
- deploy token,
- job token,
- runner authentication token.

Každý má iný ownership, scope a lifecycle. Nepoužívaj personal token človeka ako trvalú production automation identity.

## 18. Secret rotation

Rotation plán musí definovať:

1. ownera,
2. consumer inventory,
3. dual-validity alebo cutover model,
4. aktualizáciu provideru,
5. rollout consumers,
6. invalidáciu starej hodnoty,
7. validation,
8. audit evidence.

Secret bez testovanej rotation je budúci incident.

## 19. Expiration

Každá non-human credential má mať:

- účel,
- ownera,
- minimum scope,
- expiration,
- rotation policy,
- usage telemetry,
- revocation postup.

„Neexpiruje, aby pipeline neprestala fungovať“ je anti-pattern.

## 20. Fork a merge-request pipelines

Untrusted code môže zneužiť každú variable dostupnú jobu. Pri forks a external contributions:

- neposkytuj protected secrets,
- nepoužívaj privileged runner,
- oddeľ validation pipeline od trusted post-merge pipeline,
- kontroluj parent-project pipeline execution,
- reviewuj zmeny CI configuration.

## 21. Manual pipeline variables

Manual input je user-controlled data. Validuj:

- povolený environment,
- artifact digest,
- version format,
- boolean a enum values,
- length,
- path alebo URL constraints.

Manual variable nesmie umožniť command injection alebo deployment ľubovoľného artifactu.

## 22. Dotenv reports

Job môže publikovať runtime variables cez dotenv report pre downstream použitie.

Používaj na non-secret metadata, napríklad:

- generated version,
- review URL,
- artifact digest,
- deployment identifier.

Dotenv artifact nie je vhodný secret transport bez presného access a retention modelu.

## 23. Secret detection

Secret detection pomáha nájsť credential-like patterns v repository alebo pipeline context-e. Nie je náhradou za:

- secret manager,
- prevention controls,
- rotation,
- access review,
- incident response.

Nález committed secretu rieš revokáciou. Odstránenie z posledného commitu nestačí, pretože secret zostáva v histórii a klonoch.

## 24. Troubleshooting

### Variable je prázdna

Over scope, protected status, environment name, pipeline source, precedence a key spelling.

### Masked variable sa nedá uložiť

Hodnota nespĺňa masking constraints alebo je zapnutá incompatible expansion.

### Secret je dostupný v nesprávnom jobe

Over group inheritance, environment scope, protected ref, job rules a downstream pipeline forwarding.

### OIDC authentication zlyháva

Over issuer, audience, token expiry, provider trust policy, claims a clock synchronization.

### Job používa starý secret po rotácii

Over cache, long-running process, provider version, mounted file refresh a rollout všetkých consumers.

## 25. Kontrolné otázky

1. Aký je rozdiel medzi variable a secretom?
2. Čo chráni masked a čo protected variable?
3. Prečo masking nezastaví malicious job?
4. Kedy použiť file-type variable?
5. Ako environment scope znižuje blast radius?
6. Prečo group variable môže byť riziková?
7. Ako funguje OIDC federation pre CI job?
8. Kedy použiť `CI_JOB_TOKEN`?
9. Čo musí obsahovať rotation lifecycle?
10. Ako reagovať na secret commitnutý do Git history?

## Glossary impact

Relevantné pojmy: CI/CD variable, file-type variable, masked variable, hidden variable, protected variable, environment scope, external secret provider, ID token, workload identity federation, `CI_JOB_TOKEN`, deploy token a secret rotation.

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
