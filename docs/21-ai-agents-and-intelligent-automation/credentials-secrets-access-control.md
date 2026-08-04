# Credentials, secrets a access control

n8n credential prepája workflow node s authentication materialom a jeho configuration. Bezpečnosť nezávisí iba od šifrovania secretu v database; potrebuje ownera, project scope, user/workload access, least privilege, runtime decryption, rotation, audit, redaction a recovery s rovnakou encryption key generation.

Táto kapitola uzatvára incident `AGENT-N8N-07`. Workflow používal shared OAuth credential s write scope pre všetky tenanty. Editor nemohol secret priamo zobraziť, ale mohol spustiť alebo upraviť workflow, ktorý credential použil; chybný item mapping preto vykonal autorizovaný API call do nesprávneho tenant contextu.

Nosný credential lifecycle je:

```text
resource a operation authority
→ credential owner, type, tenant a scopes
→ secret issuance alebo external reference
→ encrypted persistence a project sharing
→ workflow/node binding
→ runtime identity, decryption a token acquisition
→ API call a provider audit
→ rotation, revocation a loaded-generation proof
→ backup/restore a second-workflow negative test
```

## 1. Credential verzus secret

Secret je citlivá hodnota, napríklad API key, client secret, private key alebo refresh token. n8n credential je managed object, ktorý spája secret fields s authentication type, service configuration, owner a sharing metadata.

Credential object môže obsahovať aj non-secret endpoint, tenant alebo region. Skrytie UI value neznamená, že credential nemôže byť zneužitý cez node execution.

## 2. Authentication type

API key, Basic auth, OAuth 2.0, service account, certificate a signed request majú odlišný issuance, expiry a revocation model. Credential type musí zodpovedať provider contractu a operation risku.

Long-lived static key je jednoduchý, ale zvyšuje exposure window. Short-lived token znižuje lifetime, no pridáva identity provider, clock, refresh a audience dependencies.

## 3. Credential owner

Credential má accountable ownera pre business resource a technical ownera pre lifecycle. „Shared integrations“ bez konkrétnej osoby alebo team queue vedú k stale secrets a nejasnej revocation authority.

Owner pravidelne overuje necessity, scopes, tenant a active workflows. Unused credential je attack surface aj recovery burden.

## 4. Resource a tenant scope

Credential sa viaže na exact provider account, tenant, subscription, region a resource class. Názov `Jira Production` je nedostatočný, ak credential môže pristupovať k viacerým organizations alebo projects.

Tenant scope musí byť machine-checkable v workflow contracte alebo provider policy. Text v credential name nie je enforcement.

## 5. Least privilege

Scopes a provider roles povoľujú iba operations, ktoré workflow potrebuje. Read-only diagnostics a mutation workflow nemajú automaticky zdieľať writer alebo admin credential.

Least privilege znižuje blast radius mapping, prompt-injection a operator errors. Neodstraňuje potrebu tenant validation a business policy.

## 6. Human a workload authority

User oprávnený editovať workflow a runtime workload, ktorý credential dešifruje a použije, sú odlišní actors. Audit chain musí zachytiť human change, workflow release, execution identity a provider-side principal.

Shared service account skryje jednotlivého human caller pred providerom. Local audit preto potrebuje silnú correlation a segregation of duties.

## 7. Credential persistence

Self-hosted n8n ukladá credential data šifrovane pomocou instance encryption key. Database reader bez key nemá dostať plaintext secret, ale runtime s key a workflow execution authority ho môže použiť.

Encryption at rest nechráni pred malicious alebo over-privileged workflowom. Access control a node/network restrictions ostávajú potrebné.

## 8. Encryption key

Encryption key je root dependency pre decrypt credential records. V multi-process alebo queue deploymentoch musí compatible key používať main, workers a ďalšie components, ktoré credentials načítavajú.

Náhodne rozdielny key spôsobí decryption failures; neplánovaná strata key môže zmeniť database backup na nepoužiteľný artifact. Key sa spravuje mimo repository a pravidelne restore-testuje.

## 9. Key rotation

Rotation mení encryption key podľa podporovaného postupu a musí prešifrovať alebo migrovať credential data bez mixed unreadable state. Rollout vyžaduje coordination všetkých runtime components a backup pred zmenou.

„Zmenili sme environment variable“ nie je rotation proof. Representative credentials sa musia dešifrovať a použiť až po loaded-generation overení.

## 10. External secrets

External secrets integration umožňuje referencovať values spravované v samostatnom secret manageri podľa dostupnej n8n edície a konfigurácie. External manager môže poskytnúť centralized rotation, access policy a audit.

Reference neodstraňuje runtime access. n8n process alebo workload stále potrebuje identity, ktorá secret načíta, a cache/refresh semantics musia byť známe.

## 11. Secret reference identity

Reference obsahuje provider, vault alebo namespace, path, key a podľa možnosti version. Alias `latest` zjednodušuje rotation, ale sťažuje reprodukciu execution bez loaded-version evidence.

High-impact workflow eviduje secret generation alebo provider version v audit metadata bez plaintextu. Tak možno rozlíšiť stale worker od provider authentication incidentu.

## 12. Credential sharing

Credential sharing určuje, ktorí users alebo projects môžu credential použiť alebo spravovať podľa n8n role modelu a edície. Use permission nie je to isté ako view plaintext; aj bez zobrazenia môže user spustiť authorized action cez workflow.

Review preto hodnotí effective capability. Kto môže editovať node URL, method, resource ID alebo data mapping pri shared credential, môže meniť destination a impact.

## 13. Workflow sharing interaction

Workflow editor môže používať credentials už pripojené k workflowu, aj keď nemá samostatné právo editovať credential, podľa platform sharing semantics. n8n obmedzuje editáciu nodes s unshared credentials v relevantných prípadoch, ale workflow-level access stále potrebuje presné posúdenie.

Control sa nesmie sumarizovať vetou „secret nevidia“. Otázka je, aké calls môžu vyvolať, s akými parameters a k akým execution data majú prístup.

## 14. Projects a RBAC

Projects oddeľujú workflows, credentials a members podľa organizational boundary. RBAC priraďuje role a permissions, ktoré určujú create, edit, run, share alebo administrative operations podľa edition a configuration.

Project boundary je control-plane isolation, nie automaticky provider tenant isolation. Shared credential s cross-project access môže túto hranicu obísť cez runtime capability.

## 15. Custom roles a plan dependencies

Dostupné role, custom permissions, external secrets, source control a enterprise controls sa líšia podľa n8n deploymentu a licencie. Dokumentácia a design musia uviesť exact edition a feature availability.

Security architecture sa nesmie spoliehať na feature, ktorú instance nemá. Alternatíva môže byť samostatná instance, provider-side role alebo deployment isolation.

## 16. OAuth scopes

OAuth access token nesie scopes a audience určené authorization serverom a providerom. Scope `write` alebo organization-wide admin je často širší než jedna node operation.

Consent a refresh token lifecycle patria do credential inventory. Revoked refresh token alebo changed consent môže zlyhať až pri ďalšom refreshi, nie okamžite.

## 17. OAuth audience a tenant

Token vydaný pre jednu audience alebo tenant sa nesmie posielať inému API hostu. Dynamic base URL s predefined credential môže vytvoriť token exfiltration alebo wrong-audience failure.

Allowed host sa viaže na credential type a tenant. Redirects a custom API calls musia zachovať rovnakú boundary.

## 18. Service accounts

Service account je vhodný pre unattended workflow, ak provider podporuje scoped workload identity alebo key-based principal. Nemá používať osobný účet zamestnanca, ktorého odchod zmení business automation.

Service account potrebuje ownera, rotation, MFA alebo key policy podľa provider modelu a provider-side audit. Shared account bez per-workflow correlation znižuje forenznú hodnotu.

## 19. Short-lived workload credentials

Cloud workload identity alebo assume-role flow môže vydať krátkodobý token pre exact workload. Znižuje potrebu uloženého long-lived secretu a umožňuje provider-side policy podľa workload identity.

Benefit existuje iba pri silnej workload attestation a scoped role. Over-privileged assumed role je stále over-privileged, len s kratším tokenom.

## 20. Node binding

Workflow node odkazuje na credential object ID alebo type. Binding patrí do release manifestu, pretože zmena credential reference môže zmeniť tenant, environment a permissions bez zmeny node logic.

Credential display name sa môže meniť alebo kolidovať. Stable ID a environment-specific mapping sú dôležitejšie než label.

## 21. Credential testing

UI test credential overí typicky authentication alebo jednoduchý provider call. Neoverí všetky scopes, target resources, rate limits, tenant restrictions ani mutation semantics.

Test môže byť pozitívny aj pre príliš široký credential. Negative test musí preukázať, že forbidden tenant alebo operation je providerom odmietnutá.

## 22. Rotation lifecycle

Rotation vytvorí novú generation, aktualizuje reference alebo secret, overí canary, odoberie starú generation a reconciliuje failures. Overlap window musí byť krátke a auditované.

Ak provider nepodporuje paralelné keys, rotation potrebuje maintenance alebo atomic secret update model. Retry queues s old tokens sa klasifikujú podľa operation outcome.

## 23. Revocation

Revocation je emergency alebo lifecycle action, ktorá zruší token, key, certificate alebo provider role. Local credential delete bez provider revocation môže ponechať uniknutý secret platný.

Incident response odoberá provider authority, zastaví workflows a zachová evidence. Potom vytvorí replacement identity s minimálnym scope.

## 24. Backup a restore

Credential recovery potrebuje database backup, encryption key, external-secret configuration, provider identities a compatible runtime. Backup obsahujúci encrypted blob bez key je neúplný.

Restore drill nesmie robiť production mutation. Použije isolated environment, read-only alebo sandbox credentials a overí decryption, binding a controlled API call.

## 25. Source control a exports

Workflow source control typicky prenáša credential stubs alebo references, nie plaintext secret values. To je správna separácia, ale target environment musí mať explicitný mapping na local credentials.

Import, ktorý automaticky vyberie credential podľa name, môže použiť nesprávny tenant. Promotion potrebuje environment manifest a approval pre binding changes.

## 26. Execution data a redaction

Node inputs/outputs, errors a HTTP headers môžu obsahovať secrets alebo sensitive responses. Redaction policy musí pokryť application logs, execution persistence, error messages a external observability export.

Príliš agresívna redaction nesmie odstrániť identifiers potrebné na audit. Ukladajú sa credential ID, generation, scope class a provider request ID bez token value.

## 27. Risky nodes

HTTP Request, Code, filesystem, shell-like alebo community/custom nodes môžu rozšíriť capability runtime podľa deploymentu. Credential s úzkym app node operation môže byť zneužitý, ak rovnaký secret možno pripojiť k arbitrary endpointu.

Node allow/block policy a project permissions obmedzujú capability catalog. Security audit identifikuje risky alebo unprotected patterns, ale nález treba posúdiť v konkrétnom workflow contextu.

## 28. Network a egress control

Credential scope sa kombinuje s network policy. Worker, ktorý môže posielať requests na ľubovoľný internet host, má väčší exfiltration potential než workload s provider allowlistom.

Egress control nesmie blokovať required token endpoints alebo certificate revocation checks. Architecture dokumentuje DNS, proxy a private endpoint dependencies.

## 29. Break-glass access

Emergency credential má narrow purpose, short expiry, named approver a post-use review. Nemá byť permanentne pripojený k bežnému workflowu ako skrytý fallback.

Break-glass use vytvára high-severity audit event a automaticky sa revoke. Úspešný incident zásah neospravedlňuje neobmedzený standing admin token.

## 30. Shared incident `AGENT-N8N-07`

Credential `Ticketing Production` mal organization-wide ticket create/edit scope a bol zdieľaný do operations projektu. Workflow editor nepoznal OAuth secret, ale mohol meniť ticket project a tenant fields a spustiť workflow s credential capability.

Chybný item mapping vybral tenant A pre order B. Provider call bol správne autentifikovaný a autorizovaný, preto API vrátilo success; bezpečnostná chyba bola v confused-deputy a over-broad authority chain.

## 31. Competing failure hypotheses

Prvá hypotéza je stolen credential, druhá over-broad legitimate credential, tretia wrong credential binding po promotion, štvrtá stale external-secret generation a piata provider-side role change. Všetky môžu vyzerať ako unexpected authorized call.

Evidence porovná workflow release, credential object ID, project sharing, human actor, execution, token metadata a provider audit. Authentication success nevylučuje authorization design defect.

## 32. Evidence preservation

Zachová sa credential ID, type, owner, project, scope, tenant, secret generation, last rotation, workflow bindings, execution IDs, user changes a provider audit events. Secret value sa nekopíruje do incident artifacts.

Access review potrebuje point-in-time snapshot. Current permissions po remediation nemusia dokazovať, čo platilo počas incidentu.

## 33. Containment

Provider credential sa revoke alebo scope zúži, affected workflows sa zastavia a mutation nodes prejdú na deny. Read-only diagnostika môže pokračovať s oddelenou identity.

Cross-tenant resources sa označia pre reconciliation, nie okamžite bulk-delete. Každá compensation používa explicitný approver a audit.

## 34. Recovery

Vzniknú tenant-scoped writer credentials alebo short-lived workload roles, oddelené od read-only accessu. Workflow binding sa viaže na exact environment a tenant a editor nemôže meniť destination mimo allowed scope.

Encryption/external-secret generation sa rolloutne do všetkých workers a testuje negative callom. Staré tokeny, refresh grants a provider sessions sa revoke.

## 35. Positive acceptance

Workflow môže vykonať intended operation iba v approved tenantovi a provider audit ukáže expected service principal. Execution record obsahuje credential reference a generation bez secretu.

Authorized editor môže meniť business mapping iba v policy boundary. Forbidden host, tenant a operation sú odmietnuté providerom alebo runtime controlom.

## 36. Forbidden acceptance

Credential nie je secure iba preto, že UI maskuje value alebo database field je encrypted. Neprípustný je organization-wide admin scope, osobný účet, permanent break-glass, shared cross-tenant credential a secret v workflow JSON alebo logs.

Positive credential test nie je least-privilege evidence. Potrebný je negative authorization test a provider-side read-back.

## 37. Recovery acceptance

Rotation drill zmení secret/key generation, postupne aktualizuje components a overí, že old credential je neplatný. Pending executions s old tokenom skončia controlled errorom alebo získajú new short-lived token bez duplicate mutation.

Restore drill načíta encrypted records s recovery key v isolated prostredí a preukáže binding. Bez backup key a external-secret identity sa recovery označí za failed.

## 38. Second-workflow acceptance

Druhý workflow v inom projekte a tenantovi nesmie použiť prvý credential ani cez copied workflow, name collision alebo HTTP Request custom auth. Import zostane unresolved, kým owner explicitne vyberie local binding.

Test overí control-plane aj runtime isolation. Project UI separation bez provider-side denial nie je dostatočný dôkaz.

## 39. Praktický credential inventory

Inventory prepája credential s resource, scope, workflows, encryption a rotation lifecycle. Je machine-readable pre review a zároveň neobsahuje secret material.

Každá zmena bindingu alebo scope je release-relevantná. Inventory sa porovnáva s provider-side principals a actual usage.

```yaml
credential:
  id: cred_ticketing_refund_writer_acme
  type: oauth2
  owner: platform-integrations
  provider_tenant: tenant_acme
  allowed_hosts: [api.ticketing.example]
  scopes: [tickets.create, tickets.read]
  forbidden_scopes: [admin, users.write, cross_tenant]
  projects: [refund-automation-acme]
  workflows: [wf_refund_review]
  secret_source: external-secrets/ticketing/acme/refund-writer
  secret_generation: version-17
  rotation_due: 2026-09-01
  break_glass: false
```

## 40. Prevádzkové metriky

Sledujú sa credential count, unused a stale credentials, rotation age, failed decrypts, auth failures, scope denials, cross-project bindings, break-glass use, secrets in logs detections a provider principals bez ownera. Metriky sa segmentujú podľa environmentu, tenant a risk tieru.

Nulové authorization denials môžu znamenať clean traffic alebo príliš široké scopes. Periodické negative tests a access reviews sú preto potrebné.

## 41. Primárne zdroje

- [n8n Docs — Credentials](https://docs.n8n.io/credentials/)
- [n8n Docs — Credential sharing](https://docs.n8n.io/credentials/credential-sharing/)
- [n8n Docs — Workflow sharing](https://docs.n8n.io/workflows/sharing/)
- [n8n Docs — Role-based access control](https://docs.n8n.io/user-management/rbac/)
- [n8n Docs — Projects](https://docs.n8n.io/user-management/rbac/projects/)
- [n8n Docs — External secrets](https://docs.n8n.io/external-secrets/)
- [n8n Docs — Set a custom encryption key](https://docs.n8n.io/hosting/configuration/configuration-examples/encryption-key/)
- [n8n Docs — Encryption key rotation](https://docs.n8n.io/hosting/securing/encryption-key-rotation/)
- [n8n Docs — Security audit](https://docs.n8n.io/hosting/securing/security-audit/)

## 42. Zhrnutie

n8n credential je executable capability, nie iba skrytý secret. Encryption chráni persistence, no effective safety vzniká až kombináciou scoped provider identity, project/RBAC policy, controlled workflow editing, runtime isolation, redaction, rotation a provider-side audit.

Bezpečný lifecycle viaže credential na exact tenant, resource, operation, workflow a generation a testuje aj forbidden access. Masked UI, successful authentication alebo external secret reference sú čiastkové controls; accepted stav vyžaduje negative authorization, revocation, restore a second-workflow isolation proof.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Webhooks a API integrations](webhooks-api-integrations.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
