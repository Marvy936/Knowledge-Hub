# Least privilege

Least privilege znamená, že principal, process alebo component dostane iba permissions potrebné na konkrétnu úlohu, v najmenšom potrebnom scope-e a na najkratší potrebný čas. Nejde iba o výber menšej role. Je to lifecycle disciplína zahŕňajúca identity, authorization, privilege activation, monitoring, review, removal a incident response.

## 1. Mentálny model

```text
business task
→ required actions
→ required resources
→ required conditions
→ minimal permission set
→ time-bound activation
→ audit a monitoring
→ review a removal
```

Least privilege optimalizuje blast radius bez blokovania legitímnej práce.

## 2. Dimensions privilege-u

Privilege má viac dimensions:

- **action scope** — čo možno vykonať,
- **resource scope** — voči čomu,
- **data scope** — ktoré dáta,
- **environment scope** — dev/test/prod,
- **tenant/account scope**,
- **network/device context**,
- **time scope**,
- **delegation scope**,
- **session assurance**.

Permission `read` nad všetkými production secrets môže byť riskantnejšia než `admin` nad jedným test resource-om.

## 3. Need-to-know a need-to-do

- **Need-to-know** obmedzuje prístup k informáciám.
- **Need-to-do** obmedzuje actions potrebné na pracovnú úlohu.

Oba princípy sa aplikujú na ľudí aj workloads.

## 4. Standing oproti just-in-time privilege

### Standing privilege

Permission je stále aktívna.

Riziká:

- credential compromise má veľký blast radius,
- privilege sa zabudne odstrániť,
- znižuje sa kvalita auditu,
- admin môže omylom vykonať production action.

### Just-in-time privilege

Privilege sa aktivuje na obmedzený čas po splnení podmienok.

Controls:

- approval,
- MFA alebo step-up authentication,
- justification,
- duration,
- session recording,
- automatic expiration,
- post-use review.

JIT znižuje exposure window, ale potrebuje dostupný activation a emergency model.

## 5. Just-enough administration

Just-enough administration znamená vytvoriť capability pre konkrétnu úlohu bez poskytnutia plného admin prístupu.

Príklady:

- restart konkrétnej služby bez root shellu,
- deploy do jedného namespace bez cluster-admin,
- rotate konkrétny secret bez čítania všetkých secrets,
- spustiť schválený Systems Manager runbook bez SSH,
- upraviť DNS record iba v jednej hosted zone.

## 6. Human identities

Odporúčania:

- oddeliť bežný a privileged account,
- nepoužívať shared accounts,
- MFA a phishing-resistant authentication pre privilegované účty,
- JIT/PIM aktivácia,
- minimalizovať local admin,
- pravidelné access reviews,
- automatický offboarding,
- monitorovať role assignment a use.

Privileged account nemá byť používaný na email, web browsing alebo bežnú prácu.

## 7. Workload identities

Workload identity má používať:

- short-lived credentials,
- platform-native identity,
- explicitný audience a scope,
- samostatnú identity per workload alebo trust boundary,
- automatickú rotation,
- minimálne permissions,
- auditovateľné token issuance.

Anti-patterny:

- jedna service account pre celý cluster,
- cloud access keys v image,
- CI runner s organization admin právami,
- database superuser pre application,
- shared Kubernetes ServiceAccount pre nesúvisiace Pods.

## 8. Permission decomposition

Začni od operations, nie od existujúcej broad role.

Príklad deployment automation:

```text
read artifact
→ verify signature
→ update Deployment v namespace X
→ read rollout status
→ read Events/Pods
```

Nepotrebuje automaticky:

- create ClusterRole,
- read Secrets v iných namespaces,
- delete Nodes,
- organization billing access.

## 9. Resource scoping

Preferuj najmenší resource scope:

- konkrétny bucket/prefix,
- konkrétny namespace,
- konkrétny secret path,
- konkrétny project/account,
- konkrétna database/schema,
- konkrétna Git repository/environment.

Wildcard môže byť odôvodnený iba s explicitným threat modelom a compensating controls.

## 10. Conditions a context

ABAC alebo policy conditions môžu obmedziť:

- source network,
- device compliance,
- MFA presence,
- resource tags,
- time,
- requested Region,
- encryption requirement,
- session name alebo principal type.

Conditions nesmú byť jediným controlom, ak ich možno ľahko meniť rovnakým principalom.

## 11. Permission boundaries a maximum envelope

Permission boundary, SCP alebo podobný guardrail definuje maximum, ktoré identita môže získať.

Model:

```text
identity/resource policy allow
∩ permissions boundary
∩ organization guardrail
∩ session restrictions
− explicit deny
```

Boundary sama permission neudeľuje. Znižuje maximum.

## 12. Separation of duties

Citlivý workflow rozdeľ medzi viac actors:

- developer pripraví change,
- reviewer schváli,
- pipeline deployne,
- security policy overí,
- auditor číta evidence.

Riziko vzniká, ak jedna osoba môže:

- vytvoriť permission,
- priradiť si ju,
- vykonať action,
- zmazať audit.

## 13. Break-glass a emergency privilege

Emergency access je kontrolovaná výnimka, nie trvalý admin účet používaný z pohodlnosti.

Vyžaduje:

- oddelené credentials,
- test dostupnosti,
- jasný trigger,
- okamžité alerting,
- obmedzený duration/scope,
- povinný post-incident review,
- rotation po použití.

## 14. Privilege creep

Privilege creep vzniká, keď sa permissions pridávajú, ale neodstraňujú.

Príčiny:

- zmena role alebo tímu,
- dočasný project access,
- manuálne grants,
- nested groups,
- stale service accounts,
- deprecated automation,
- environment cloning.

Controls:

- expiration,
- owner,
- access review,
- usage analytics,
- deprovisioning,
- IaC source of truth.

## 15. Access review

Review má odpovedať:

- Kto má access?
- Prečo ho potrebuje?
- Kedy bol naposledy použitý?
- Je permission stále primeraná?
- Kto je owner resource-u a identity?
- Je grant direct, group-based, inherited alebo delegated?
- Má expiration?

Review bez removal workflowu je iba report.

## 16. Usage-based refinement

Permission usage data pomáha zmenšiť policy, ale má limity:

- krátke observation window nemusí zachytiť disaster recovery action,
- seasonal operation sa môže javiť nepoužitá,
- denied action môže indikovať chýbajúci access alebo attack,
- emergency permissions potrebujú test, nie production use.

Použitie je evidence, nie automatická pravda.

## 17. Least privilege v Linuxe

Mechanizmy:

- users/groups,
- file permissions a ACLs,
- `sudo` per command,
- capabilities namiesto root,
- systemd sandboxing,
- SELinux/AppArmor,
- namespaces/cgroups,
- read-only filesystem.

`sudo ALL=(ALL) ALL` nie je granular least privilege.

## 18. Least privilege v Kubernetes

- namespace-scoped Roles namiesto ClusterRoles,
- RoleBinding pre konkrétny ServiceAccount,
- nebindovať `cluster-admin`,
- minimalizovať Secret read,
- projected short-lived tokens,
- separate ServiceAccounts,
- admission a Pod Security controls,
- audit privileged operations.

Permission vytvárať Pods môže viesť k indirect privilege escalation, ak Pod môže mountnúť privileged ServiceAccount, hostPath alebo node credentials.

## 19. Least privilege v cloud-e

- roles namiesto long-lived users/keys,
- resource-level scoping,
- condition keys,
- account separation,
- SCP/organization guardrails,
- permissions boundaries,
- short sessions,
- cross-account roles,
- access analyzer a activity review.

Cloud managed policy môže byť vhodný baseline, ale nie automaticky najmenší privilege pre konkrétny workload.

## 20. CI/CD a automation

Pipeline identity má mať:

- access iba k potrebnej repository/environment,
- short-lived federation/OIDC,
- oddelené build a deploy identities,
- protected environment approval,
- minimal artifact/registry permissions,
- žiadne broad organization tokeny,
- audit subject, workflow, commit a environment.

Pull request z nedôveryhodného fork-u nemá automaticky získať production credentials.

## 21. AI agents

Agent potrebuje capability-based least privilege:

- explicitný tool allowlist,
- read-only default,
- parameter constraints,
- approval pre mutating/high-impact actions,
- tenant a data scoping,
- time/cost/action budgets,
- sandbox,
- complete audit,
- kill switch.

Prompt instruction nie je authorization boundary. Tool alebo backend musí permission presadiť.

## 22. Validation

Least privilege sa validuje:

- positive tests — required task funguje,
- negative tests — zakázaná task zlyhá,
- privilege escalation tests,
- cross-tenant/resource tests,
- expired session tests,
- audit evidence,
- break-glass rehearsal,
- removal/offboarding test.

## 23. Troubleshooting denied access

```text
správna identity a session?
→ required action/resource?
→ explicit allow?
→ resource scope?
→ conditions?
→ boundary/SCP/session restriction?
→ explicit deny?
→ propagation/cache?
→ target service policy?
```

Neopravuj incident okamžitým pridaním admin role bez identifikácie presného missing permission.

## 24. Troubleshooting excessive access

```text
direct grant?
→ group/nested group?
→ inherited role?
→ resource policy?
→ wildcard?
→ condition bypass?
→ delegated/impersonated access?
→ stale session/token?
→ alternate path?
```

Po odstránení permission over revocation existujúcich sessions a credentials.

## 25. Anti-patterny

### Admin pre rýchlosť

Dočasný broad grant sa stane trvalým.

### Jedna role pre celý tím

Nesúvisiace duties majú rovnaký blast radius.

### Read-only považované za bezpečné

Read secrets, personal data alebo configuration môže byť kritické.

### Access review podľa role names

Custom policies a indirect paths sa prehliadnu.

### Least privilege bez availability plánu

Emergency response sa zablokuje, ak JIT alebo identity provider zlyhá.

### Permission usage automaticky odstráni všetko nepoužité

Zničí rare recovery operations.

## 26. Kontrolné otázky

1. Aké dimensions má privilege?
2. Ako sa líši standing, JIT a just-enough privilege?
3. Prečo workload nemá používať user credential?
4. Čo je permissions boundary?
5. Ako separation of duties znižuje risk?
6. Ako vzniká privilege creep?
7. Ako navrhnúť access review?
8. Aké indirect escalation risks existujú v Kubernetes?
9. Ako aplikovať least privilege na CI/CD a AI agentov?
10. Ako validovať, že policy je minimálna, ale funkčná?

## Glossary impact

Relevantné pojmy: least privilege, need-to-know, need-to-do, standing privilege, just-in-time access, just-enough administration, privilege activation, privilege creep, access review, separation of duties, permissions boundary, effective permissions, capability-based security a break-glass privilege.

## Primárne zdroje

- [NIST least privilege glossary](https://csrc.nist.gov/glossary/term/least_privilege)
- [NIST SP 800-53 Rev. 5 — Access Control](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)
- [Kubernetes RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
- [Microsoft Entra role best practices](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/best-practices)
