# AWS Organizations a accounts

AWS account je základná isolation, billing, quota, identity a resource ownership boundary. AWS Organizations umožňuje viac účtov centrálne spravovať v hierarchii rootu a organizational units (OUs), aplikovať organization policies, používať consolidated billing a delegovať správu vybraných služieb. Dobre navrhnutý multi-account model znižuje blast radius a oddeľuje workloads, environments, security a billing responsibilities.

## 1. AWS account ako boundary

AWS account poskytuje samostatný scope pre:

- resources a ich ARN identities,
- IAM principals a policies,
- service quotas,
- billing a cost allocation,
- CloudTrail a security telemetry,
- KMS keys,
- network topológiu,
- support a service configuration,
- incident a administrative blast radius.

Account nie je iba billing container. Je to jedna z najsilnejších AWS-native isolation boundaries.

## 2. Prečo nepoužívať jeden account

Jeden veľký account vedie k:

- broad IAM permissions,
- konfliktom mien, quotas a network ranges,
- slabému oddeleniu production/non-production,
- nejasnému cost ownershipu,
- veľkému blast radiusu,
- zložitej log separation,
- riziku, že cleanup alebo automation zasiahne nesprávny workload.

Multi-account model neposkytuje automatickú bezpečnosť; potrebuje centrálne guardrails, identity a observability.

## 3. AWS Organizations

Organization je kolekcia AWS accounts centrálne spravovaná cez:

- management account,
- organization root,
- organizational units,
- member accounts,
- organization policies,
- consolidated billing,
- trusted access a delegated administrators.

Hierarchia:

```text
Organization
└─ Root
   ├─ Security OU
   │  ├─ Log archive account
   │  └─ Security tooling account
   ├─ Infrastructure OU
   │  ├─ Network account
   │  └─ Shared services account
   ├─ Workloads OU
   │  ├─ Production OU
   │  └─ Non-production OU
   └─ Sandbox OU
```

## 4. Management account

Management account vytvára a spravuje organization a má špeciálne billing a administrative capabilities.

Bezpečnostné zásady:

- nenasadzuj doň bežné workloady,
- minimalizuj trvalých principals,
- používaj phishing-resistant MFA a federáciu,
- obmedz root-user použitie,
- centralizuj logging,
- monitoruj Organizations a account-management changes,
- používaj delegated administration pre podporované služby.

Service control policies neobmedzujú principals v management account-e. Preto je management account mimoriadne citlivý trust root.

## 5. Member account

Member account patrí do organization a môže byť:

- vytvorený cez Organizations,
- pozvaný ako existujúci account,
- umiestnený priamo pod root alebo do OU.

Member account má vlastné resources, IAM a quotas, ale podlieha organization-level controls podľa hierarchy a service integration.

## 6. Organization root

Root je najvyšší kontajner organization hierarchy. Policies aplikované na root sa dedia na OUs a member accounts pod ním podľa policy type semantics.

Root nepoužívaj ako jednoduché miesto pre všetky accounts bez OU designu. Stratíš lifecycle a policy differentiation.

## 7. Organizational Unit

OU je logická skupina accounts spravovaná ako jednotka.

OU navrhuj podľa policy a lifecycle, napríklad:

- security,
- infrastructure,
- production,
- non-production,
- sandbox,
- suspended,
- exceptions.

OU nie je regionálna ani network boundary. Je to governance hierarchy.

## 8. OU design

Dobré OU design principles:

- organizuj podľa spoločných controls, nie iba org chartu,
- oddeľ production a non-production,
- oddeľ security/log archive,
- vytvor quarantine alebo suspended OU,
- minimalizuj exception OUs,
- nepoužívaj príliš hlbokú hierarchy,
- dokumentuj policy inheritance.

Organizačná štruktúra firmy sa mení častejšie než security requirements. Preto OU hierarchy nemá slepo kopírovať tímy.

## 9. Service Control Policy

SCP definuje maximum dostupných permissions pre principals v member accounts.

Dôležité:

- SCP sám access neudeľuje,
- IAM identity/resource policy musí request stále povoliť,
- effective permission je prienik relevantných authorization layers,
- explicit deny v SCP blokuje request,
- SCP sa aplikuje podľa root/OU/account inheritance,
- management account nie je SCP obmedzený.

Zjednodušene:

```text
IAM/resource policy allow
∩ SCP allowed boundary
∩ permissions boundary/session policy
∩ service-specific controls
= možný effective access
```

## 10. Allow-list a deny-list SCP stratégia

### Deny-list

`FullAWSAccess` zostáva a SCP explicitne zakazuje vybrané rizikové actions alebo Regions.

Výhody:

- jednoduchšie zavedenie,
- menej blokovaných nových služieb.

Riziká:

- nové actions sú default povolené,
- guardrail coverage musí byť priebežne aktualizovaná.

### Allow-list

SCP povoľuje iba vybrané services/actions.

Výhody:

- prísnejší control.

Riziká:

- vysoká maintenance complexity,
- nové service features nefungujú bez zmeny,
- ľahko sa zablokujú shared/global dependencies.

## 11. SCP nie je IAM policy replacement

SCP nerieši:

- kto konkrétne má role,
- resource-level least privilege v account-e,
- application authorization,
- credential lifecycle,
- resource policy trust,
- KMS key policy.

Použi SCP ako organization guardrail a IAM ako account/workload authorization.

## 12. Policy inheritance

Effective SCP závisí od všetkých relevantných úrovní:

```text
Root policies
→ parent OU policies
→ child OU policies
→ account policies
```

Pri allow-list modeli musí byť action povolená na každej potrebnej úrovni. Pri deny sa explicitný deny presadí.

Troubleshooting potrebuje analyzovať celú hierarchy, nie iba policy priamo attached k accountu.

## 13. Region guardrails

Organization môže obmedziť používanie nepovolených Regions.

Riziká:

- global services používajú regionálne alebo global endpoints,
- security/billing/support services potrebujú výnimky,
- existing resources môžu zostať,
- STS a identity behavior sa líši podľa konfigurácie,
- recovery Region musí byť povolený.

Region deny SCP najprv testuj v non-production OU a používaj presne zdokumentované výnimky.

## 14. Tag policies

Tag policy pomáha štandardizovať tag keys a hodnoty naprieč organization.

Použitie:

- cost allocation,
- ownership,
- environment,
- data classification,
- automation selection.

Tag policy nie je automaticky access-control mechanizmus. Enforcement capabilities a service support treba overiť.

## 15. Backup a AI/data policies

AWS Organizations podporuje viac policy typov podľa integrovaných služieb a aktuálnych capabilities. Každý policy type má vlastnú inheritance a merge semantics.

Nepredpokladaj, že všetky organization policies fungujú ako SCP. Používaj service-specific dokumentáciu.

## 16. Consolidated billing

Organizations združuje billing member accounts do jedného payer/management scope-u.

Výhody:

- centrálne faktúry,
- cost visibility,
- zdieľanie vybraných volume/commitment discountov podľa pravidiel,
- account-level chargeback/showback,
- central cost governance.

Billing consolidation nemení resource ownership. Resource zostáva v member account-e.

## 17. Account vending

Nový account má byť vytvorený cez automatizovaný workflow:

1. business/technical owner,
2. environment a OU,
3. account email a contact údaje,
4. baseline IAM/federation,
5. CloudTrail/config/security services,
6. network model,
7. budgets a quotas,
8. mandatory tags,
9. break-glass procedure,
10. lifecycle/decommission owner.

Ručne vytvorený account bez baseline vytvára governance gap.

## 18. Account naming a email

Definuj:

- stabilné account name,
- unikátnu email adresu alebo email alias strategy,
- business owner,
- technical owner,
- environment,
- data classification,
- cost center.

Account name sa môže zmeniť; account ID je stabilnejšia technická identity. ID však nie je secret.

## 19. Workforce access

Preferuj centrálne federované access cez identity provider a krátkodobé sessions.

Model:

```text
workforce IdP
→ IAM Identity Center alebo federation
→ permission set / role
→ target member account
```

Výhody:

- central joiner/mover/leaver,
- MFA,
- short-lived credentials,
- account/role selection,
- auditability.

Nevytváraj IAM users v každom account-e bez opodstatnenia.

## 20. Workload cross-account access

Používaj role assumption a resource policies s explicitným trust modelom.

Over:

- trusted principal/account/organization,
- external ID pri third-party access,
- conditions,
- session duration,
- source identity/session tags,
- resource policy,
- SCP a KMS policy,
- audit events.

`Principal: *` s broad condition alebo bez condition môže vytvoriť cross-account exposure.

## 21. Delegated administrator

Podporované AWS services umožňujú zaregistrovať member account ako delegated administrator.

Výhody:

- menej operácií v management account-e,
- oddelenie security/network/backup ownershipu,
- least privilege organization operations,
- špecializované admin accounts.

Delegation nemení fakt, že management account zostáva najvyšší organization trust root.

## 22. Security accounts

Bežné účty:

### Log archive

Central immutable/retained logs s obmedzeným write/read accessom.

### Security tooling

Delegated administration pre detection, findings a response tooling.

### Audit/read-only

Cross-account visibility pre compliance a assurance.

Oddeľ administráciu security tooling od workload administratorov.

## 23. Network account

Central network account môže vlastniť:

- Transit Gateway,
- shared VPC resources podľa zvoleného modelu,
- Direct Connect/VPN integration,
- DNS resolver endpoints,
- inspection appliances,
- IPAM.

Centralizácia znižuje duplicitu, ale vytvára shared critical dependency. Potrebuje HA, quotas, change control a ownership.

## 24. Shared services account

Môže obsahovať:

- artifact repositories,
- directory/identity integrations,
- CI runners,
- observability,
- package mirrors,
- internal DNS alebo certificates.

Shared service failure môže ovplyvniť celú organization. Použi explicitné SLO, isolation a recovery.

## 25. Production a non-production accounts

Oddelenie poskytuje:

- menší blast radius,
- odlišné SCPs a budgets,
- samostatné quotas,
- jasnejší access,
- oddelenú telemetry a data classification.

Nepoužívaj iba tag `Environment=prod` v jednom account-e ako náhradu account boundary pri kritických workloadov.

## 26. Sandbox accounts

Sandbox potrebuje:

- cost limit/budget,
- restricted services a Regions,
- zákaz production dát,
- automatic cleanup,
- expiration alebo owner review,
- obmedzené network prepojenie,
- no-trust path do production.

Sandbox bez guardrails sa stáva shadow production prostredím.

## 27. Suspended/quarantine OU

Pri compromise alebo decommission môže account prejsť do quarantine OU s prísnymi policies.

Postup musí zohľadniť:

- zachovanie logs/evidence,
- incident-response access,
- blokovanie destructive alebo egress actions,
- service dependencies,
- billing a backup,
- legal hold.

Náhodný deny-all SCP môže zablokovať aj response tooling.

## 28. Account closure

Pred closure:

- inventory resources a data,
- export logs a evidence,
- zachovaj required backups,
- zruš subscriptions a third-party contracts,
- odstráň network/trust relationships,
- vyrieš DNS/domains/certificates,
- skontroluj bills a commitments,
- dokumentuj retention,
- počkaj na closure/recovery window podľa AWS procesu.

Account deletion nie je instantný garbage collection všetkých externých závislostí.

## 29. Break-glass access

Každý critical account potrebuje núdzový access model:

- oddelené credentials,
- phishing-resistant MFA,
- secure custody,
- explicitný approval/use process,
- alert pri použití,
- pravidelný test,
- post-use rotation a review.

Break-glass, ktorý nebol testovaný, nemusí fungovať počas IdP outage.

## 30. Observability a audit

Centralizuj:

- organization changes,
- account creation/move/closure,
- SCP attachments,
- delegated admin changes,
- CloudTrail coverage,
- configuration compliance,
- root-user events,
- cross-account role assumptions,
- billing anomalies.

Organization control plane je security-critical a potrebuje samostatné detections.

## 31. Anti-patterny

### Workloads v management account-e

Zväčšujú blast radius najcitlivejšieho účtu.

### OU podľa org chartu

Reorganizácie potom nútia policy-presuny bez security dôvodu.

### SCP ako grant

SCP iba obmedzuje maximum; access musí udeliť IAM/resource policy.

### Deny-all quarantine bez incident role výnimky

Zablokuje response a evidence collection.

### IAM users v každom account-e

Komplikuje lifecycle, MFA a audit.

### Jeden shared services account bez HA

Vytvorí organization-wide single point of failure.

## 32. Troubleshooting

### AccessDenied napriek IAM allow

Over SCP hierarchy, permissions boundary, session policy, resource policy a KMS key policy.

### SCP zmena nefunguje podľa očakávania

Over policy type enablement, attachment point, inheritance, explicit deny a management-account exception.

### Account nevie použiť Region

Over account Region enablement, SCP, service availability a IAM.

### Delegated admin nevidí accounts/resources

Over service trusted access, delegated administrator registration, Region/service scope a resource enrollment.

### Cost nie je správne priradený

Over linked account, tags, cost categories, shared cost allocation a billing period.

## 33. Kontrolné otázky

1. Prečo je AWS account security a isolation boundary?
2. Akú úlohu má management account?
3. Čo je organization root a OU?
4. Čo SCP robí a čo nerobí?
5. Prečo SCP neobmedzuje management account?
6. Ako sa líši deny-list a allow-list stratégia?
7. Prečo OU nemá slepo kopírovať org chart?
8. Aký je účel delegated administratora?
9. Ktoré účty patria do security foundation?
10. Ako navrhneš safe account vending a decommission proces?

## Glossary impact

Relevantné pojmy: AWS account, AWS Organizations, organization, management account, member account, organization root, organizational unit, service control policy, SCP inheritance, consolidated billing, delegated administrator, account vending, log archive account, security tooling account, shared services account, network account, quarantine OU a break-glass account access.

## Oficiálna dokumentácia

- [What is AWS Organizations?](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html)
- [Organizations terminology and concepts](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html)
- [Best practices for organizational units](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_ous_best_practices.html)
- [Best practices for the management account](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_best-practices_mgmt-acct.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: High availability a disaster recovery](high-availability-disaster-recovery.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
