# Variables a secrets

GitLab CI/CD variable je input do pipeline alebo jobu. Môže niesť public configuration, user-controlled parameter, citlivú value, file content alebo identity assertion. Bezpečnosť nevytvára checkbox `masked`. Vzniká až po vyriešení source-u, precedence, availability phase, pipeline trustu, runtime exposure, propagation, loaded generation, cleanupu a revocation lifecycle-u.

Secret nie je iba string uložený v GitLab. Je to capability k external systemu alebo protected value. Ak job získa cloud key, database password alebo signing token, môže vytvoriť descendants — sessions, images, deployments alebo provider effects — ktoré prežijú zmazanie variable. Recovery preto nekončí editáciou UI; musí zrušiť target credential a všetky loaded/issued descendants.

## 1. Dominantný value-to-capability model

```text
configuration alebo capability intent
→ exact variable/secret subject and authority
→ source/scope/environment/protection/precedence resolution
→ pipeline/job eligibility
→ runtime injection or ID-token issuance
→ process/file/network exposure
→ external credential/session acquisition
→ side effects and audit
→ rotation, revocation, cleanup and second-use validation
```

Configured variable, resolved job value, loaded application value a external target credential sú rozdielne states.

## 2. Exact variable/secret subject

```yaml
secretSubject:
  key: PROVIDER_CREDENTIAL
  classification: high
  owner: payments-security
  purpose: provider-settlement-production
  authority: vault.atlas.example/secret/payments/provider
  gitlabReference:
    scope: project/481
    environmentScope: production
    protected: true
    masked: true
    hidden: true
    variableType: file
  generation: pv-43
  consumers:
    - production_deploy
    - settlement-reconciliation
  targetCredential:
    providerKeyId: provider-prod-43
  expiresAt: 2026-08-31T00:00:00Z
```

GitLab key name bez authority/generation/purpose nie je enough. Rovnaký `TOKEN` môže existovať v group, project, pipeline trigger a job scope s odlišnou precedence.

## 3. Variable sources a precedence

Sources môžu zahŕňať predefined variables, instance/group/project variables, pipeline inputs, trigger/schedule/API variables, environment-scoped variables, job variables, `dotenv` reports a manual job inputs. Exact precedence sa musí overiť pre current GitLab generation.

Critical key inventory identifikuje all definitions. Hidden override sa odhalí tým, že job publikuje non-secret source/generation metadata, nie value.

```bash
printf 'provider_credential_generation=%s\n' "$PROVIDER_CREDENTIAL_GENERATION"
printf 'target_environment=%s\n' "$CI_ENVIRONMENT_NAME"
printf 'pipeline_source=%s\n' "$CI_PIPELINE_SOURCE"
```

Output preukazuje process environment values. Nepreukazuje authoritative origin ani absence shadowed variable. Resolved pipeline metadata a external secret audit dopĺňajú evidence.

## 4. Masked, hidden a protected

Masked variable sa GitLab pokúša redigovať v logs pri supported values/patterns. Transformation, encoding, substring, debug trace alebo third-party tool môže value odhaliť. Hidden obmedzuje UI retrieval, nie runtime access. Protected obmedzuje availability podľa protected ref contextu, ale stale/direct-push protected ref môže stále spustiť untrusted code.

Tieto controls znižujú accidental exposure; nenahrádzajú least privilege, short lifetime a trusted job boundary.

## 5. File-type variables

File-type variable vytvorí temporary file a environment variable obsahuje path. Pomáha pre certificates alebo kubeconfig, no job stále môže file prečítať a exfiltrovať. Cleanup musí odstrániť file a runner runtime.

```bash
stat --printf='mode=%a owner=%U path=%n\n' "$PROVIDER_CREDENTIAL"
```

Output preukazuje local file metadata. Nepreukazuje content confidentiality, mount persistence ani that helper process did not copy file. Runtime isolation and audit matter.

## 6. ID tokens a workload federation

GitLab job môže dostať OIDC ID token s configured audience. External provider overí issuer, audience a claims a vydá short-lived credential.

```yaml
production_deploy:
  id_tokens:
    VAULT_ID_TOKEN:
      aud: https://vault.atlas.example
  script:
    - ./scripts/exchange-vault-token.sh
```

ID token je signed assertion, nie cloud permission itself. External trust policy určuje capability. Claims majú bound project ID/path, ref type/name, ref protection, namespace, environment a job context podľa supported claims.

Token payload sa môže inspectnúť bez signature validation iba pre diagnosis; acceptance používa cryptographic validation external providerom. Raw token sa nesmie logovať.

## 7. External secret provider

Preferred model získava secret just-in-time z Vault/cloud secret managera:

```bash
vault write -format=json auth/jwt/login \
  role=payments-production \
  jwt="$VAULT_ID_TOKEN" \
  | jq -r '.auth.client_token' > /tmp/vault-token

VAULT_TOKEN="$(cat /tmp/vault-token)" \
  vault kv get -format=json secret/payments/provider \
  | jq -r '.data.data.generation'
```

Generation output preukazuje secret metadata returned providerom. Nepreukazuje target credential rotation, consumer use alebo absence token leakage. Vault audit and target provider read-back complete chain.

## 8. Environment scope

Environment-scoped variable relies on job environment name/pattern. Dynamic environment mismatch can expose or hide value unexpectedly. Environment scope is distribution filter, not complete authorization boundary.

Production secret should require protected environment/ref, trusted runner and external role claims. A job without environment declaration must not get equivalent alternate static credential.

## 9. User-controlled variables

Manual, trigger or API variables are untrusted inputs unless authorized and validated. They must not directly choose shell commands, image references, include URLs, runner tags, environment names or role ARNs.

```bash
case "$DEPLOY_REGION" in
  eu-central-1|eu-west-1) ;;
  *) echo 'invalid deploy region' >&2; exit 2 ;;
esac
```

Validation preukazuje allowlisted string in one job. Nepreukazuje that downstream template does not use original unvalidated variable under different name.

## 10. Secret exposure paths

Secrets môžu uniknúť cez:

- command echo and debug tracing;
- process arguments and `/proc`;
- files/workspace/cache/artifacts;
- Docker build args/layers/history;
- environment dumps and crash reports;
- child processes and service containers;
- network exfiltration;
- transformed values not masked;
- generated manifests or Terraform plans.

Jobs handling high-value secret use restricted egress, ephemeral runtime and no untrusted source-controlled tools.

## 11. Rotation and loaded state

Rotation has several states:

```text
new secret version created
→ target provider credential changed
→ GitLab/external reference points to new generation
→ job acquires new value
→ application/runtime reloads value
→ old sessions/credentials revoked
→ second operation validates new generation
```

Changing GitLab variable alone may leave target credential and long-running consumers unchanged. Environment variables loaded at process start require redeploy/restart. Connection pools and tokens can retain old descendants.

## 12. Revocation after exposure

When secret may be exposed:

```text
preserve job/runner/audit evidence
→ stop affected jobs and external effects
→ revoke target credential/session
→ rotate authoritative secret
→ inventory artifacts/logs/caches containing value
→ redeploy/reload consumers
→ test old credential forbidden
→ validate new second operation
```

Masking a log or deleting variable is not revocation.

## 13. Connected incident `GL-PAY-73`

Atlas stored production provider key as masked, protected project variable. Protected runner executed a pipeline from direct-pushed protected `main`. Job script base64-encoded an environment dump for diagnostics; masking did not recognize transformed secret. Shared shell runner preserved the dump in workspace.

At the same time broad Vault JWT role trusted any protected ref in group, not exact project/environment. Experiment project job obtained provider credential through ID token and created sessions.

```text
protected variable + protected ref assumption
→ untrusted code on protected runner
→ transformed log/workspace exposure
+ broad OIDC trust
→ external credential descendants
```

Team rotated GitLab variable, but provider key and active sessions remained valid. Attacker continued for 37 minutes.

Root cause was capability lifecycle and trust policy, not redaction failure alone.

## 14. Containment, recovery a acceptance

Containment pause-ne runners/jobs, preserve-ne logs/workspace/audit, revoke-ne provider/Vault sessions and blocks network. Recovery creates new provider generation, narrows OIDC claims, moves secret out of GitLab static storage, redeploys consumers and verifies old key failure.

Variable/secret model is accepted only when:

```text
source/scope/precedence and generation are exact
+ public config and secret capability are classified
+ masked/hidden/protected meanings are not overclaimed
+ untrusted inputs are validated
+ high-value secret uses trusted ephemeral runner and bounded egress
+ federation trust binds exact project/ref/environment/audience
+ target credential and consumer-loaded state are observed
+ rotation revokes old descendants
+ old credential forbidden test passes
+ second job/application operation uses new generation
```

## 15. Troubleshooting flow

```text
key/purpose/authority
→ all GitLab variable definitions and precedence
→ pipeline/ref/environment eligibility
→ runner injection and exposure paths
→ ID-token claims/external trust
→ target credential/session
→ side effects and audit
→ rotation/revocation/consumer reload
```

Competing hypotheses include variable shadowing, environment-scope mismatch, protected-ref bypass, masking transformation, file persistence, Docker layer, broad JWT trust or stale consumer-loaded state.

## 16. Anti-patterny

### Masked equals secure

Redaction is not isolation, least privilege or revocation.

### Static production secret in group variable

Broad descendant scope and long lifetime increase blast radius.

### ID token equals least privilege

External trust policy may issue broad capability.

### Rotation only in GitLab UI

Target credential and loaded consumers may stay old.

### Secret in cache/artifact for job transfer

Creates durable uncontrolled copies.

## 17. Kontrolné otázky

1. Aký je rozdiel medzi variable a secret capability?
2. Čo tvorí exact secret subject?
3. Prečo precedence matters?
4. Čo masked/hidden/protected controls do and do not prove?
5. Ako file-type variable changes exposure?
6. What does ID token prove?
7. How external trust policy limits capability?
8. Why environment scope is not full authorization?
9. What happened in `GL-PAY-73`?
10. Why GitLab variable rotation did not revoke attacker?
11. How loaded consumer generation is verified?
12. What must forbidden old-credential test prove?

## Glossary impact

Relevantné pojmy: CI/CD variable, secret capability, variable source, variable precedence, masked variable, hidden variable, protected variable, file-type variable, environment scope, ID token, workload federation, external secret provider, loaded secret generation, target credential, rotation, revocation and secret descendant.

## Primárne zdroje

- [GitLab Docs — CI/CD variables](https://docs.gitlab.com/ci/variables/)
- [GitLab Docs — Secrets management](https://docs.gitlab.com/ci/secrets/)
- [GitLab Docs — ID token authentication](https://docs.gitlab.com/ci/secrets/id_token_authentication/)
- [GitLab Docs — HashiCorp Vault secrets](https://docs.gitlab.com/ci/secrets/hashicorp_vault/)
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)
- [HashiCorp Vault JWT/OIDC auth](https://developer.hashicorp.com/vault/docs/auth/jwt)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Runners a executors](runners-and-executors.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Artifacts a cache →](artifacts-and-cache.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
