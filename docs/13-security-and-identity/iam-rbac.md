# IAM a RBAC

Identity and Access Management je širšia disciplína správy identities, credentials, authentication, authorization, provisioning, federation, privileged access a auditing. Role-Based Access Control je jeden authorization model v rámci IAM. Zamieňanie IAM a RBAC vedie k predstave, že vytvorenie roles samo vyrieši celý identity lifecycle.

## 1. Mentálny model

```text
identity source
→ account a credential lifecycle
→ authentication/federation
→ principal a session
→ role/attribute/policy evaluation
→ authorization decision
→ enforcement
→ audit a access review
```

RBAC rieši najmä mapovanie:

```text
principal → role → permissions → resource scope
```

## 2. IAM capabilities

IAM platforma typicky zahŕňa:

- identity repository alebo integráciu na authoritative source,
- account provisioning a deprovisioning,
- credential a authenticator lifecycle,
- authentication a MFA,
- federation a single sign-on,
- authorization policies,
- role/group management,
- privileged access,
- workload identities,
- access requests a approvals,
- audit, review a governance.

Nie každý produkt pokrýva všetky vrstvy.

## 3. Authoritative source

Authoritative source určuje, odkiaľ pochádza pravda o identity a lifecycle stave.

Príklady:

- HR systém pre zamestnancov,
- customer identity store,
- cloud account inventory,
- Kubernetes API pre ServiceAccounts,
- CMDB alebo service catalog pre workload ownerov.

Bez autoritatívneho source-u vznikajú orphaned accounts, conflicting attributes a nejasný offboarding.

## 4. Joiner, mover, leaver

### Joiner

- identity proofing,
- account creation,
- baseline access,
- authenticator enrollment,
- owner a manager assignment.

### Mover

- zmena tímu alebo pozície,
- odstránenie starých roles,
- pridanie nových permissions,
- conflict/separation-of-duties check.

### Leaver

- disable account,
- revoke sessions/tokens,
- remove role/group membership,
- rotate shared dependencies,
- transfer ownership,
- preserve audit a data podľa policy.

Offboarding iba v jednom identity providerovi nemusí zrušiť local accounts, API keys alebo service credentials.

## 5. RBAC model

Základné prvky:

- users alebo principals,
- roles,
- permissions,
- role assignments,
- sessions,
- constraints.

Permission možno modelovať ako:

```text
(action, resource, condition)
```

Role je pomenovaná množina permissions pre pracovnú funkciu alebo technical capability.

## 6. Flat a hierarchical RBAC

### Flat RBAC

Roles nemajú inheritance.

Výhody:

- jednoduchšia interpretácia,
- menšie riziko transitive privilege.

Nevýhody:

- duplicita permissions.

### Hierarchical RBAC

Senior role dedí permissions junior role.

Výhody:

- reuse,
- model organizačnej hierarchie.

Riziká:

- neviditeľné effective permissions,
- role explosion alebo príliš broad parent role,
- komplikovaný removal.

## 7. Static a dynamic separation of duties

### Static SoD

Principal nesmie mať konfliktujúce roles súčasne.

Príklad:

- vytvoriť vendor účet,
- schváliť platbu tomu istému vendorovi.

### Dynamic SoD

Principal môže mať obe roles, ale nesmie ich použiť v rovnakom workflowe alebo session.

Vyžaduje context a transaction-aware enforcement.

## 8. Role engineering

Dobrý role design vychádza z tasks a permissions, nie iba z organizačných názvov.

Postup:

1. inventory operations,
2. mapovanie na resource scopes,
3. zoskupenie podľa job function,
4. oddelenie common a privileged capabilities,
5. conflict analysis,
6. owner a approval,
7. usage validation,
8. periodic review.

Role má mať:

- účel,
- permissions,
- scope,
- ownera,
- eligibility,
- approval,
- expiration/review,
- incompatibilities.

## 9. Role explosion

Role explosion vzniká pri vytváraní role pre každú kombináciu:

```text
tím × environment × application × privilege level × region
```

Controls:

- composable roles,
- resource scope v assignment-e,
- ABAC conditions,
- group-based assignment,
- standard entitlement catalog,
- odstránenie duplicate roles.

Príliš broad role je opačný extrém.

## 10. RBAC a ABAC

RBAC je vhodný pre stabilné job functions.

ABAC je vhodný pre dynamické decisions podľa:

- principal attributes,
- resource tags,
- environment,
- tenant,
- request context.

Hybrid model:

```text
role povoľuje capability
+ attribute condition obmedzí resource/context
```

Attributes musia mať trusted source a controlled write permissions. Ak principal môže meniť vlastný authorization attribute, control je neúčinný.

## 11. Group-based access

Groups zjednodušujú assignment, ale vytvárajú:

- nested membership,
- propagation delay,
- circular alebo transitive access,
- stale memberships,
- nejasného ownera.

Audit musí vedieť vysvetliť effective path:

```text
user → group A → group B → role → permission
```

## 12. Resource roles oproti directory roles

Rozlišuj:

- identity/directory administration,
- cloud/resource administration,
- application role,
- data-plane permission.

Príklad: Microsoft Entra role spravuje Entra resources, zatiaľ čo Azure RBAC role spravuje Azure resources. Názov `Global Administrator` alebo `Owner` má význam iba v konkrétnom policy plane.

## 13. Kubernetes RBAC

Kubernetes objekty:

- `Role` — namespaced permissions,
- `ClusterRole` — cluster-scoped alebo reusable permissions,
- `RoleBinding` — bind v namespace,
- `ClusterRoleBinding` — bind cluster-wide.

Rule obsahuje:

- API groups,
- resources/subresources,
- verbs,
- optional resource names,
- non-resource URLs.

Kubernetes RBAC je additive allow model. Nemá explicit deny. Ak jedna binding permission povoľuje, iná ju neodoberie.

## 14. Kubernetes privilege escalation

Permissions, ktoré môžu viesť k eskalácii:

- create/update Roles alebo RoleBindings,
- bind alebo escalate verbs,
- impersonate,
- create Pods s privileged settings,
- read Secrets,
- exec/attach,
- create certificate signing requests,
- access node proxy,
- modify admission alebo webhook config.

`Can create Pods` nemusí byť low privilege.

## 15. Cloud IAM policy model

Cloud IAM často kombinuje:

- identity policies,
- resource policies,
- role trust policy,
- organization guardrails,
- permissions boundaries,
- session policies,
- condition keys,
- explicit deny.

Troubleshooting musí identifikovať všetky policy planes a effective intersection/union semantics konkrétnej platformy.

## 16. Policy as code

IAM/RBAC konfigurácia má byť:

- version-controlled,
- reviewovaná,
- staticky analyzovaná,
- testovaná positive/negative cases,
- deploymentovaná cez controlled pipeline,
- drift-monitorovaná,
- auditovateľná.

Testy:

```text
principal X môže action A na resource R
principal X nesmie action B
principal Y nesmie cross-tenant access
```

## 17. Access request a approval

Access request musí obsahovať:

- requester a beneficiary,
- resource a role,
- business reason,
- duration,
- owner/approver,
- conflict check,
- authentication assurance,
- audit ID.

Approval od nesprávneho ownera nie je meaningful control.

## 18. Privileged Access Management

PAM/PIM capability môže poskytovať:

- eligible role,
- JIT activation,
- MFA,
- approval,
- session duration,
- recording,
- credential checkout/rotation,
- alerts,
- access reviews.

PAM nenahrádza správny role design.

## 19. Workload IAM

Workload identity governance zahŕňa:

- ownera,
- purpose,
- environment,
- credential type,
- permissions,
- expiration,
- deployment binding,
- rotation,
- usage a audit.

Service principal bez ownera a recent use je kandidát na quarantine/removal.

## 20. Audit a explainability

Pre každé allow/deny má byť možné vysvetliť:

```text
principal
→ session/credential
→ groups/roles
→ policies
→ resource/context
→ decision
→ enforcement point
```

Authorization explainability je kritická pri incidentoch a access reviews.

## 21. Troubleshooting RBAC deny

```text
správny principal?
→ role assignment/binding?
→ správny scope/namespace?
→ action verb a resource/subresource?
→ group membership?
→ session/token refresh?
→ conditions?
→ organization/boundary/explicit deny?
→ target resource policy?
```

Kubernetes:

```bash
kubectl auth can-i get pods --as=system:serviceaccount:team:app -n team
kubectl auth can-i --list --as=... -n team
```

Výsledok testu interpretuj s impersonation permissions a admission/runtime controls.

## 22. Troubleshooting excessive permission

- direct assignments,
- nested groups,
- inherited roles,
- wildcard actions/resources,
- broad ClusterRoleBinding,
- resource policy,
- stale eligible role,
- alternate identity,
- permission to modify policy itself.

Po oprave over existujúce sessions a token cache.

## 23. Anti-patterny

### IAM = login page

Chýba provisioning, authorization, review a audit.

### Role podľa mena človeka

Role nereprezentuje reusable job function.

### Jedna admin role pre automation

Blast radius je neprimeraný.

### Group nesting bez limitu

Effective access je nečitateľný.

### Kubernetes `cluster-admin` ako troubleshooting fix

Maskuje chýbajúcu konkrétnu permission a zostáva trvalý risk.

### Role count ako maturity metric

Veľa roles môže znamenať role explosion, nie granularitu.

## 24. Kontrolné otázky

1. Prečo je IAM širšie než RBAC?
2. Čo je authoritative identity source?
3. Ako funguje joiner/mover/leaver lifecycle?
4. Čo je role engineering?
5. Ako vzniká role explosion?
6. Kedy kombinovať RBAC a ABAC?
7. Ako vysvetliť effective access cez nested groups?
8. Ako Kubernetes Role a ClusterRole súvisia s bindings?
9. Ktoré Kubernetes permissions umožňujú indirect escalation?
10. Ako testovať IAM/RBAC policy as code?

## Glossary impact

Relevantné pojmy: IAM, RBAC, ABAC, authoritative identity source, joiner-mover-leaver, role engineering, role hierarchy, role assignment, entitlement, role explosion, static separation of duties, dynamic separation of duties, effective access, Kubernetes Role, ClusterRole, RoleBinding, ClusterRoleBinding, bind, escalate a impersonate.

## Primárne zdroje

- [NIST Role-Based Access Control](https://csrc.nist.gov/projects/role-based-access-control)
- [Kubernetes RBAC authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Kubernetes RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
- [Microsoft Entra RBAC](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/)
- [Azure ABAC overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/conditions-overview)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Least privilege](least-privilege.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Active Directory →](active-directory.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
