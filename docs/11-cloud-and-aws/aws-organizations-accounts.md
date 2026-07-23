# AWS Organizations a accounts

AWS account je základná AWS-native boundary pre resource ownership, identity, quotas, billing a veľkú časť incident blast radiusu. AWS Organizations spája viac účtov do centrálne riadenej hierarchie, v ktorej možno delegovať administráciu, aplikovať organization policies, centralizovať billing a vytvoriť opakovateľný account lifecycle.

Multi-account model sám osebe nevytvára bezpečnosť. Účty musia byť správne zaradené do organizational units, dostať identity a logging baseline, podliehať vhodným guardrails a mať jasného ownera od vytvorenia po closure.

## 1. Mentálny model

Najjednoduchší model oddeľuje resource boundary od governance hierarchy. Member account vlastní svoje resources a IAM configuration, zatiaľ čo organization pridáva nad účty centrálne maximum permissions, declarative configuration, billing a service integrations.

```text
AWS Organizations management account
→ organization root
→ organizational units podľa policy a lifecycle
→ member accounts
→ resources, IAM, data a workloads
```

Organization control plane rozhoduje, kde account patrí, ktoré policies zdedí a ktoré služby môžu spravovať celú organizáciu. Samotné application alebo data-plane permissions však stále vznikajú v IAM, resource policies, KMS policies a service-specific authorization modeloch.

## 2. AWS account ako isolation boundary

AWS account poskytuje samostatný namespace a ownership scope pre resources, IAM principals, KMS keys, quotas a veľkú časť audit telemetry. Chybná automation alebo broad administrator role je preto zvyčajne obmedzená na resources v danom account-e, pokiaľ nemá cross-account trust alebo organization-level oprávnenia.

Account nie je absolútna security boundary. Shared network, central CI/CD, organization administrator, delegated services alebo cross-account resource policies môžu preniesť riziko medzi účtami, preto musia byť tieto väzby explicitne modelované.

## 3. Prečo nepoužívať jeden veľký account

Jeden account zjednodušuje začiatok, ale mieša production, development, security tooling, billing a quotas do jedného failure a administrative scope-u. Ako počet workloads rastie, role sa rozširujú, resource names a CIDR ranges kolidujú a je čoraz ťažšie určiť, ktorá automation smie meniť ktorú časť prostredia.

Multi-account model umožní oddeliť production od non-production, workloady od security platformy a sandbox od corporate data. Výhodu však prináša iba vtedy, keď account creation, identity, network, logging a decommission sú automatizované; inak vznikne iba väčší počet nekonzistentných účtov.

## 4. AWS Organizations

Organization je centrálne spravovaná množina AWS accounts. Obsahuje jeden management account, organization root, voliteľné organizational units, member accounts a viac typov organization policies.

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

Hierarchy nie je iba vizuálne triedenie. Attachment point policy a poloha accountu určujú zdedené guardrails, configuration a časť service behavioru.

## 5. All features a consolidated-billing-only mode

Organizations môže fungovať iba ako consolidated billing alebo s aktivovanými všetkými features. Advanced governance capabilities, ako Service Control Policies a Resource Control Policies, vyžadujú organization s all features enabled.

Prechod na all features je governance zmena, nie iba prepínač v konzole. Pred migráciou treba overiť account invitations, policy behavior, service integrations a oprávnenia, pretože organization začne ovplyvňovať authorization a central configuration naprieč member accounts.

## 6. Management account

Management account je account, ktorý organization vytvoril a zostáva jej najvyšším trust rootom pre organization, billing a policy administration. Má capabilities, ktoré member account nemôže plne nahradiť, a jeho compromise môže zmeniť hierarchy, policies, delegated administrators alebo account lifecycle.

Do management accountu nepatria bežné workloads ani business data. AWS odporúča používať ho iba na operácie, ktoré tento account skutočne vyžadujú, minimalizovať access a čo najviac administrácie delegovať do určených member accounts.

## 7. Prečo SCP a RCP nechráni management account

Service Control Policies neobmedzujú users ani roles v management account-e. Resource Control Policies rovnako neobmedzujú resources vlastnené management accountom, preto management account nemá rovnaký organization guardrail ako member accounts.

Tento rozdiel je dôvodom, prečo je workload v management account-e rizikový. IAM chyba alebo compromised administrator môže pracovať mimo ochrany SCP/RCP a súčasne má prístup k citlivému organization control plane-u.

## 8. Member account

Member account je každý account v organization okrem management accountu. Vlastní svoje resources, IAM principals, service quotas a väčšinu lokálnej konfigurácie, ale súčasne podlieha policies zdedeným z organization hierarchy.

Member account môže byť workload account, security account, network account alebo delegated administrator. Delegovaný status mu dáva service-specific organization oprávnenia, ale neruší naň pôsobiace SCP, RCP ani lokálne IAM controls.

## 9. Organization root

Organization root je najvyšší kontajner hierarchy, z ktorého sa policies dedia do OUs a member accounts. Policy attached na root môže ovplyvniť prakticky celú organization, preto má vysoký blast radius a vyžaduje testovanie v menšom scope-e pred globálnym nasadením.

Root nemá slúžiť ako jediný neusporiadaný zoznam všetkých accounts. OUs umožňujú rozdeliť lifecycle a policy requirements tak, aby sandbox, production a security foundation nemuseli používať identický control set.

## 10. Organizational Unit

Organizational Unit (OU) je governance kontajner pre accounts a ďalšie child OUs. Neposkytuje network isolation ani samostatný billing account, ale určuje spoločnú inheritance cestu policies a uľahčuje lifecycle operácie nad skupinou účtov.

OU má reprezentovať stabilný policy alebo risk profile, nie momentálny org chart. Tímy a reporting lines sa menia častejšie než production, sandbox alebo regulated-data requirements; slepé kopírovanie organizačnej štruktúry preto vedie k zbytočným presunom účtov a policy driftu.

## 11. OU design

Dobrý OU design vytvára malé množstvo zrozumiteľných governance vrstiev. Typicky oddelí security foundation, shared infrastructure, production, non-production, sandbox a quarantine alebo suspended accounts.

Príliš plochá hierarchy núti používať veľa account-specific výnimiek. Príliš hlboká hierarchy zase komplikuje effective policy, pretože pri troubleshooting treba analyzovať root, všetky parent OUs a policy priamo pripojené k accountu.

## 12. Organization policy categories

AWS Organizations dnes rozlišuje authorization policies a declarative policies. Authorization policies nastavujú maximum dostupného accessu, zatiaľ čo declarative policies centrálne konfigurujú podporované AWS service features a používajú vlastnú inheritance a merge logiku.

Do authorization policies patria Service Control Policies (SCPs) pre principals a Resource Control Policies (RCPs) pre resources. Declarative policy types zahŕňajú podľa aktuálnej podpory napríklad tag, backup, Security Hub, Inspector, Bedrock, S3 alebo ďalšie service-specific policies; ich presný zoznam a semantics sa musia overovať v aktuálnej dokumentácii.

## 13. Service Control Policy

Service Control Policy definuje maximum permissions, ktoré môžu používať IAM users a roles v member accounts. SCP access neudeľuje; iba určuje, ktoré actions môžu lokálne IAM a resource policies vôbec povoliť.

```text
identity alebo resource policy allow
∩ SCP permission boundary
∩ permissions boundary a session restrictions
− applicable explicit denies
= možný effective access
```

Ak SCP action blokuje, ani `AdministratorAccess` v member account-e ju neobnoví. Naopak action povolená SCP stále zostane implicitne denied, ak ju žiadna IAM alebo resource policy skutočne nepovolí.

## 14. Resource Control Policy

Resource Control Policy nastavuje organization-level maximum permissions pre podporované resources v member accounts. Dopĺňa SCP tým, že chráni resource boundary aj pred niektorými external principals alebo resource-policy paths, ktoré samotný SCP nemusí priamo obmedziť.

RCP rovnako access neudeľuje. Effective decision vzniká prienikom RCP, SCP a lokálnych identity alebo resource policies; navyše treba rešpektovať, že podporované services a resource types sa vyvíjajú a management-account resources RCP nepokrýva.

## 15. SCP a RCP spolu

SCP odpovedá najmä na otázku, aké maximum má principal spravovaný organization member accountom. RCP odpovedá, aké maximum môže byť vykonané voči podporovanému resource-u vlastnenému member accountom.

Kombinácia je dôležitá pri cross-account access. Principal môže mať identity allow a resource policy môže povoľovať request, ale action sa uskutoční iba vtedy, ak ju povoľuje aj applicable SCP a RCP boundary.

## 16. Effective policy a inheritance

Effective organization policy vzniká z policies attached na root, parent OUs, child OUs a samotný account podľa semantics konkrétneho policy typu. SCP/RCP evaluation a declarative policy merging sa nesmú považovať za rovnaký mechanizmus.

Pri allow-list SCP modeli musí byť potrebná permission povolená na každej relevantnej úrovni. Explicitný deny blokuje action bez ohľadu na nižší allow, zatiaľ čo declarative policies môžu používať inheritance operators a vytvárať výslednú konfiguráciu zlúčením parent a child pravidiel.

## 17. Deny-list a allow-list SCP stratégia

Deny-list stratégia ponechá broad `FullAWSAccess` boundary a explicitne zakazuje vybrané actions, services, Regions alebo riskantné configuration paths. Je jednoduchšia na adoption a nové AWS capabilities sa menej často zablokujú, ale governance tím musí priebežne pridávať guardrails pre nové riziká.

Allow-list stratégia povoľuje iba definované services a actions. Poskytuje prísnejší default, no zvyšuje maintenance a môže neočakávane zablokovať global services, security integrations alebo nové API actions použité pri upgrade.

Výber nemusí byť jednotný pre celú organization. Sandbox môže používať obmedzený deny-list s cost controls, zatiaľ čo vysoko regulované OUs môžu potrebovať kontrolovanejší allow-list model.

## 18. Policy rollout a blast radius

Organization policy change sa nemá nasadiť priamo na root bez testovania. Chybný deny môže zablokovať deployment, incident response, logging alebo recovery naraz vo všetkých accounts.

Bezpečný rollout používa test account alebo canary OU, policy simulation a konkrétne positive aj negative testy. Zmena musí mať ownera, rollback postup a výnimku pre kritické break-glass alebo security operations iba tam, kde je technicky odôvodnená.

## 19. Region guardrails

Region guardrail obmedzuje vytváranie alebo používanie resources mimo povolených Regions. Cieľom môže byť data residency, cost, support alebo zmenšenie attack surface-u, ale implementation musí rozlišovať regionálne a globálne services.

Príliš všeobecný deny môže zablokovať IAM, billing, support, security telemetry alebo DR operácie. Recovery Region a všetky potrebné control-plane calls musia byť súčasťou testu skôr, než sa policy aplikuje na production OU.

## 20. Declarative policies

Declarative policy centrálne nastavuje podporovanú service configuration namiesto jednoduchého allow/deny requestu. Parent a child policies sa kombinujú podľa service-specific inheritance operators, takže výsledkom je effective configuration pre account.

Takáto policy môže napríklad štandardizovať backup, tagging alebo security-service behavior. Governance tím musí poznať, ktoré services policy podporujú, čo možno override-nuť a ako sa zmena prejaví na existujúcich oproti novým resources.

## 21. Tag policies

Tag policy štandardizuje názvy tag keys, povolené hodnoty a compliance reporting. Pomáha vytvoriť konzistentný ownership, environment a cost-allocation contract naprieč accounts.

Tag policy sama osebe nemusí zabrániť vytvoreniu non-compliant resource-u vo všetkých services a operations. Enforcement treba overiť podľa podporovaných resource types a prípadne doplniť IaC validation, Service Catalog alebo policy-as-code controls.

## 22. Trusted access

Trusted access umožňuje podporovanej AWS service vykonávať organization-level operácie a vytvárať service-linked roles v member accounts. Je to trust expansion, pretože service získava capabilities naprieč organizáciou.

Pred enablementom treba overiť, aké permissions service dostane, ktoré Regions používa a ako sa integrácia vypína. Disable trusted access môže zmeniť central monitoring alebo security coverage, preto sa nemá vykonávať bez dependency review.

## 23. Delegated administrator pre AWS service

Mnohé services umožňujú zaregistrovať member account ako delegated administrator. Tento account následne spravuje organization-wide service configuration alebo resources bez potreby bežného prístupu do management accountu.

Delegation znižuje počet ľudí a automations s management-account accessom, ale neprenáša neobmedzenú organization authority. Konkrétne permissions, počet podporovaných delegated accounts a Region behavior určuje integrovaná service.

## 24. Delegated policy management pre Organizations

AWS Organizations môže pomocou resource-based delegation policy povoliť určeným member accounts spravovať vybrané organization policies a attachments. Ide o inú capability než service-specific delegated administrator, pretože sa týka priamo Organizations policy operations.

Delegácia musí byť granulárna a podporená IAM permissions v delegated account-e. Resource policy bez zodpovedajúceho IAM allow access nevytvorí, rovnako ako IAM allow nemôže prekročiť rozsah organization delegation policy.

## 25. Consolidated billing

Consolidated billing zhromažďuje charges member accounts pod management account a umožňuje centralizovaný payer model. Môže tiež zdieľať vybrané volume alebo commitment benefits podľa pravidiel konkrétnej služby.

Billing consolidation nemení resource ownership ani security boundary. Workload resource zostáva v member account-e a jeho IAM, quota, network a incident lifecycle treba spravovať lokálne alebo cez príslušnú organization integration.

## 26. Account vending

Account vending je automatizovaný proces vytvorenia accountu a aplikácie povinného baseline-u. Cieľom nie je iba zavolať `CreateAccount`, ale odovzdať používateľovi account s identity, logging, network, budgets, policies a lifecycle ownershipom.

```text
account request a approval
→ create account
→ zaradiť do OU
→ identity a break-glass baseline
→ CloudTrail, Config a security integrations
→ network a DNS
→ budgets, quotas a tags
→ validation
→ handover ownerovi
```

Ručne vytvorený account bez baseline-u vytvára okamžitý governance gap. Account vending workflow má byť idempotentný, auditovateľný a schopný opraviť partial provisioning failure.

## 27. Account metadata a stable identity

Account name a email majú odrážať účel, environment a ownership, ale názov sa môže časom zmeniť. Dvanásťmiestny account ID je stabilnejšia technická identity a nemá sa považovať za secret.

Inventory má uchovávať business ownera, technical ownera, OU, environment, data classification, cost center a expected closure date. Bez týchto údajov nie je jasné, kto schvaľuje access, reaguje na findings alebo rozhoduje o decommission.

## 28. Workforce access

Workforce access má používať centrálnu federáciu a short-lived role sessions namiesto IAM users vytvorených v každom account-e. Joiner, mover a leaver lifecycle sa potom riadi v identity source a permission sets alebo role assignments sa mapujú na konkrétne accounts.

```text
workforce identity provider
→ IAM Identity Center alebo federation
→ permission set alebo role
→ target member account
→ short-lived session
```

Centrálna federácia zlepšuje MFA, revocation a audit, ale identity administrator sa stáva kritickým trust actorom. Prístup do management accountu potrebuje prísnejší model než bežný workload access a pravidelné review.

## 29. Workload cross-account access

Workload má pristupovať do ďalšieho accountu cez role assumption alebo presne scope-nutú resource policy. Trust policy určuje, kto smie role assume-nuť, zatiaľ čo permissions policy určuje, čo session následne smie vykonať.

Návrh musí overiť source identity, session tags, external ID pri third-party access, organization conditions, SCP/RCP a KMS key policy. Broad `Principal: *` s nepresnou condition môže otvoriť resource účtom alebo principals, ktoré pôvodný owner neočakával.

## 30. Security foundation accounts

Security foundation oddeľuje log retention, detection a audit od workload administratorov. Najčastejšie obsahuje log archive account, security tooling account a podľa governance modelu samostatný audit alebo read-only access path.

Log archive má prijímať organization telemetry a obmedziť delete alebo mutation. Security tooling account môže fungovať ako delegated administrator pre podporované services a vykonávať findings aggregation alebo response bez uloženia production workloadov.

## 31. Network a shared-services accounts

Network account môže vlastniť Transit Gateway, Direct Connect, VPN, IPAM, Resolver endpoints alebo inspection appliances. Centralizácia znižuje duplicitu, ale vytvára organization-wide dependency, preto potrebuje HA, quota headroom, change control a recovery plan.

Shared-services account môže hostovať artifact repositories, CI runners, package mirrors, directory integrations alebo observability. Každá shared služba musí mať explicitný consumer inventory a SLO, pretože jej outage môže naraz zablokovať deployments alebo access vo veľkej časti organization.

## 32. Production, non-production a sandbox

Oddelenie production a non-production do samostatných accounts znižuje blast radius, oddeľuje quotas a umožňuje odlišné access a cost policies. Tag `Environment=prod` v jednom spoločnom account-e neposkytuje rovnakú isolation boundary pre kritické workloads.

Sandbox accounts potrebujú cost limit, restricted Regions a services, automatic cleanup a zákaz production dát. Bez expiration a network guardrails sa sandbox môže postupne zmeniť na shadow production systém mimo pravidelného patching, backup a incident ownershipu.

## 33. Quarantine a suspended OU

Compromised alebo decommissionovaný account možno presunúť do quarantine OU s prísnejšími policies. Cieľom je zastaviť egress alebo destructive changes a súčasne zachovať evidence, logs a incident-response access.

Blind deny-all policy môže zablokovať forensics, backup alebo recovery role. Quarantine design preto musí byť pripravený vopred, testovaný a rozlišovať actions, ktoré sa majú zastaviť, od actions potrebných na containment a investigation.

## 34. Account closure

Closure je riadený lifecycle krok, nie okamžité vymazanie všetkých externých dependencies. Pred zatvorením treba inventory resources, exportovať required evidence, zachovať backups, odstrániť trust relationships a vyriešiť domains, certificates, commitments a subscriptions.

Member account musí byť chránený pred neúmyselným `LeaveOrganization` alebo `CloseAccount` podľa governance modelu. Nové Organizations vytvorené cez AWS Console od 10. júla 2026 dostávajú default root SCP pre tieto actions automaticky, ale staršie alebo programovo vytvorené organizations musia guardrail zaviesť samy.

## 35. Root-user a break-glass governance

Root user má capabilities, ktoré bežná IAM role nemá, preto musí mať samostatnú custody, phishing-resistant MFA a monitorovanie použitia. AWS podporuje centralizovanejšiu správu root accessu member accounts, ale konkrétny model treba navrhnúť podľa aktuálnych Organizations a IAM capabilities.

Break-glass access musí fungovať aj pri outage workforce IdP alebo IAM Identity Center. Credentials a recovery proces sa pravidelne testujú, použitie okamžite alertuje a po incidente nasleduje rotation a review.

## 36. Observability a audit organization control plane-u

Organization changes sú security-critical udalosti. Presun accountu do inej OU, attachment SCP/RCP, zmena delegated administratora alebo disable trusted access môže zmeniť effective access a coverage naprieč veľkou časťou prostredia.

Central monitoring má sledovať account creation a closure, policy changes, root-user events, organization service integrations, cross-account role assumptions a billing anomalies. Audit trail musí byť uložený mimo jednoduchého dosahu workload administratorov.

## 37. Troubleshooting effective access

Pri `AccessDenied` nestačí kontrolovať IAM role v member account-e. Decision môže blokovať SCP, RCP, permissions boundary, session policy, resource policy, KMS key policy alebo service-specific control.

```text
caller identity a session
→ identity policy
→ trust alebo resource policy
→ SCP hierarchy
→ RCP hierarchy
→ permissions boundary/session restrictions
→ service-specific policy a resource state
→ final decision a CloudTrail evidence
```

Pri organization policy probléme over policy type enablement, attachment path, account OU, effective policy a management-account exception. Pri declarative policy over aj inheritance operators a to, či service už podporuje daný resource alebo Region.

## 38. Anti-patterny

### Workloads v management account-e

Management account má organization-wide privilege a nie je chránený SCP/RCP. Bežný workload v ňom zbytočne spája application incident s najcitlivejším governance trust rootom.

### OU podľa org chartu

Tímy sa reorganizujú a accounts by sa museli presúvať bez zmeny risk profile-u. OU má vyjadrovať policy a lifecycle, ktoré zostávajú stabilnejšie než reporting line.

### SCP ako grant

SCP iba stanovuje maximum permissions. Ak lokálna IAM alebo resource policy action nepovolí, broad SCP z implicitného deny neurobí allow.

### Všetky organization policy types sa považujú za SCP

RCP chráni resource boundary a declarative policies používajú service-specific merge semantics. Rovnaký mentálny model pre všetky policy types vedie k nesprávnemu effective-policy troubleshootingu.

### Jeden shared-services account bez isolation

Centralizácia môže vytvoriť organization-wide single point of failure. Shared platforma potrebuje SLO, capacity, tenant isolation a recovery rovnako ako production workload.

## 39. Kontrolné otázky

1. Prečo je AWS account silnejšia boundary než tag alebo naming convention?
2. Aký je rozdiel medzi management a member accountom?
3. Prečo SCP a RCP nechránia management account?
4. Čo je OU a prečo nemá kopírovať org chart?
5. Aký je rozdiel medzi authorization a declarative organization policies?
6. Čo SCP povoľuje alebo blokuje a prečo access nikdy neudeľuje?
7. Aký problém rieši RCP oproti SCP?
8. Ako vzniká effective permission pri kombinácii IAM, SCP a RCP?
9. Kedy zvoliť deny-list a kedy allow-list SCP model?
10. Prečo sa policy rollout najprv vykonáva cez canary OU?
11. Aký je rozdiel medzi trusted access a delegated administratorom?
12. Čo všetko musí vykonať account-vending workflow?
13. Ako navrhnúť bezpečný cross-account workload access?
14. Prečo quarantine OU potrebuje incident-response výnimky?
15. Aké evidence potrebuješ pri troubleshooting organization-level `AccessDenied`?

## Glossary impact

Relevantné pojmy: AWS account, AWS Organizations, all features, management account, member account, organization root, organizational unit, authorization policy, declarative policy, Service Control Policy, Resource Control Policy, effective policy, SCP inheritance, RCP, trusted access, delegated administrator, organization delegation policy, consolidated billing, account vending, log archive account, security tooling account, shared services account, network account, quarantine OU a break-glass account access.

## Oficiálna dokumentácia

- [What is AWS Organizations?](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html)
- [Organizations terminology and concepts](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html)
- [Managing organization policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html)
- [Service control policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html)
- [Resource control policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps.html)
- [Best practices for the management account](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_best-practices_mgmt-acct.html)
- [Delegated administrators for AWS services](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_delegated_admin.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: High availability a disaster recovery](high-availability-disaster-recovery.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: IAM →](iam.md)
<!-- KNOWLEDGE-NAVIGATION:END -->