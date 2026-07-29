# Security goals, access, privilege and IAM lifecycle glossary entries

## Access acceptance verdict

Dôkaz, že current identity/session mapovanie, authorization policy, enforcement path, operation result a audit chain vytvárajú správny allowed aj forbidden outcome a prežijú second-login alebo second-sync test. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Access subject

Exact identity, account, authenticator, session/token, principal mapping, requested action/resource/context, policy generation, enforcement point a audit scope analyzovaného accessu. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Active-cardinality verdict

Rozhodnutie, či počet súčasne aktívnych series, streams, terms, alert instances alebo promoted trace dimensions zostáva v budgete pre konkrétny tenant a signal. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Asset-impact matrix — CIA

System-specific mapping assetu alebo business procesu na confidentiality, integrity a availability loss, impact threshold, controls, evidence a ownera. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Attribute-authority matrix

Mapping identity, ownership a authorization attributes na ich authoritative source, consumers, freshness a invalidation contract. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Audit completeness verdict — identity

Rozhodnutie, či security audit zachoval trusted time, original actora, delegated subject, action, target, policy generation, result a celý source-to-query delivery path. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Audit-generation subject

Exact source event, schema, actor/delegation fields, exporter, queue, central store, retention, access a query generation relevantnej security evidence. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Authentication-event generation

Versionovaný výsledok verifiera viažuci principal, authenticator, method, assurance, verifier identity, timestamp a subsequent session alebo token issuance. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Authoritative security recovery

Obnova identity, credential, configuration, data a business state-u z dôveryhodných sources vrátane revocation, rotation, reconciliation a allowed/forbidden validation. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Authorization explainability

Schopnosť rekonštruovať principal/session, direct a nested assignments, roles/policies, resource/context, combining semantics, decision, enforcement a výsledok jedného allow alebo deny. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Authorization request tuple

Exact principal, action, resource a context spolu s policy generation, nad ktorými vzniká authorization decision. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Capability confidentiality

Confidentiality property citlivej capability, pri ktorej principal nesmie secret alebo key iba čítať, ale ani neobmedzene používať signing, decryption, impersonation či export operation. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## CIA acceptance verdict

Dôkaz, že chránený asset zachoval required confidentiality, integrity a availability, incident bol reconciled a forbidden aj residual-risk outcomes boli explicitne vyhodnotené. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## CIA security subject

Exact business capability, assets, identities, data/config generations, trust boundaries, impact thresholds, controls a evidence scope analyzovanej CIA otázky. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Control generation — security

Versionovaný source a runtime realization security policy, identity rule, key/credential boundary, detector alebo recovery controlu. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Delegated-actor chain

Auditovateľný chain od original human alebo workload actora cez session/token, impersonation alebo delegated workload identity až po downstream action a target. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Effective-access graph

Výsledný graph direct, group, nested, inherited, delegated a resource-policy paths spájajúci principal so sensitive capability po zohľadnení session a platform semantics. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Effective-privilege graph

Výsledná množina priamych aj nepriamych capabilities principalu vrátane role inheritance, workload creation, credential access, impersonation a policy-modification paths. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Effective security control

Control, ktorého schválená generation je načítaná a presadzovaná na každej relevantnej boundary a ktorého allowed, forbidden a recovery outcomes boli testované. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Enforcement-path coverage

Dôkaz, že authorization decision je presadený na každej skutočnej API, data-plane, delegated alebo alternate ceste ku chránenému side effectu. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Entitlement catalog

Governed inventory assignable roles, groups a capabilities s purpose, actions, scope, ownerom, eligibility, activation, conflicts, review, tests a retirement contractom. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Entitlement desired generation

Complete desired identity-to-entitlement graph vypočítaný z authoritative identity, job-function, ownership a policy state-u pre konkrétny reconciliation cycle. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Evidence-preserving security containment

Bounded action, ktorá zastaví pokračujúci security impact a exposure bez zničenia session, identity, policy, workload, data a audit evidence potrebnej na reconstruction. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Identity eligibility generation

Versionovaný stav určujúci, či identity stále spĺňa organizational a risk podmienky na použitie accountu, service-u alebo privileged entitlementu. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Identity reconciliation

Proces porovnávajúci authoritative identity/entitlement desired state s downstream accounts, groups, roles, sessions a local access paths a pridávajúci aj odstraňujúci delta. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Identity-to-workload audit chain

Korelácia human alebo upstream principalu, jeho session a authorization s vytvorenou workload identity a downstream actions tejto workload identity. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## IAM drift

Rozdiel medzi authoritative identity/entitlement desired state-om a effective downstream accounts, groups, roles, sessions alebo resource policies. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## IAM/RBAC acceptance verdict

Dôkaz, že authoritative state, reconciliation, session claims, policy bindings a effective access sú zhodné, required access funguje, forbidden paths zlyhávajú a second reconciliation neobnoví defect. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## IAM subject

Exact authoritative identity record, entitlement generation, group/role graph, federation/session, platform policy, resource scope a audit generation analyzovaného IAM lifecycle-u. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Indirect privilege path

Povolená operation, ktorá umožní získať inú alebo vyššiu authority cez workload creation, credential read, role binding, impersonation, delegated role, trusted artifact alebo policy mutation. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Just-enough capability

Mediated a bounded operation poskytujúca presný business alebo administrative task bez full shellu, broad role alebo ambient control-plane authority. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Mover reconciliation

Identity lifecycle transition, ktorá vypočíta nové desired entitlements, odstráni staré incompatible paths, vykoná SoD kontrolu, pridá nové access paths a revoke-ne stale sessions. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Maximum-permission envelope

Guardrail, boundary alebo architecture contract určujúci najvyššiu authority, ktorú principal, delegated administrator alebo workload môže získať bez ohľadu na jednotlivé role assignments. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Nested-group access path

Transitive entitlement cesta, v ktorej principal získava role alebo permission cez jednu alebo viac vnorených group memberships. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Policy-decision verdict

Exact allow, deny alebo error výsledok PDP nad principal–action–resource–context tuple-om a konkrétnou policy/attribute generation. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Policy-information freshness

Dôkaz, že group, ownership, tenant, device, risk a ďalšie PIP attributes použité pri authorization zodpovedajú current authoritative state-u. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Principal-mapping generation

Versionované pravidlá mapujúce federovaný issuer/subject a claims na local application, cloud alebo Kubernetes principal. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Privilege-dimension inventory

Explicitný inventory action, resource, data, environment, tenant, time, delegation, session-assurance a operation-budget scope-u jedného entitlementu. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Privilege-removal closure

Dôkaz, že source assignment, nested paths, active sessions, tokens, delegated workloads a alternate identities už neposkytujú odstránenú capability. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Privilege subject

Exact principal, business task, entitlement generation, activation/session, action/resource/data/time scope, maximum envelope a validation set analyzovaného privilege-u. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Residual-risk verdict

Explicitné rozhodnutie o zostávajúcom security risku po containment, recovery a effective-control validation vrátane ownera, duration a acceptance podmienok. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Role-contract generation

Versionovaný role design s purpose, permissions, scope, ownerom, eligibility, activation, conflicts, tests, review a retirement semantics. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Second-session revocation test

Validation, ktorá overí odstránený privilege v predtým active session aj v novo vydanej session po source a policy reconciliation. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Second-sync test

Opakovaný identity/entitlement reconciliation cycle dokazujúci, že odstránený group, role alebo binding sa z authoritative source-u alebo stale mappingu znovu nevytvorí. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Security assurance verdict

Grounds for confidence založené na source/runtime read-backu, allowed a forbidden tests, audit evidence a recovery rehearsal, že security objectives konkrétnej implementácie sú splnené. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Session-assurance state

Current authentication method, assurance level, authentication age, device/risk context, validity a revocation state dlhšie trvajúcej session. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Session revocation closure

Dôkaz, že browser sessions, access/refresh tokens, delegated grants a ďalšie artifacts odvodené z identity alebo authenticatora už verifier a resource services neprijímajú. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Task-capability contract

Mapping jedného business alebo administrative tasku na required observations, preconditions, exact mutation, resource/data scope, forbidden actions, validation a audit. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Trusted-attribute contract

Pravidlo určujúce authoritative source, schema, writer permissions, freshness, normalization a failure behavior attribute-u používaného pri ABAC alebo role eligibility. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Workload IAM subject

Exact workload owner, runtime/deployment binding, issuer, audience, credential generation, permissions, expiration, rotation, usage a audit identity non-human principalu. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).
