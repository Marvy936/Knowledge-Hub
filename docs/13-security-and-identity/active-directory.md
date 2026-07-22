# Active Directory

Active Directory Domain Services (AD DS) je distribuovaná directory a identity platforma pre Windows doménové prostredia. Uchováva objekty ako users, groups, computers a services, poskytuje LDAP directory access, Kerberos a NTLM authentication, Group Policy, DNS-integrated service discovery a multimaster replication medzi domain controllers.

Active Directory nie je synonymum pre Microsoft Entra ID. AD DS je doménová directory platforma založená na domains, forests, domain controllers, LDAP, Kerberos, DNS a Group Policy. Microsoft Entra ID je cloudová identity and access management služba s odlišným object, protocol a management modelom.

## 1. Mentálny model

```text
forest a schema
→ domains a trusts
→ domain controllers
→ replicated directory partitions
→ DNS service discovery
→ LDAP directory operations
→ Kerberos/NTLM authentication
→ groups, ACLs a Group Policy
→ audit, backup a recovery
```

AD DS je zároveň identity system, directory database, authentication infrastructure a policy distribution platforma.

## 2. Directory objects

AD DS uchováva objects definované schema triedami a attributes.

Príklady:

- users,
- groups,
- computers,
- managed service accounts,
- organizational units,
- contacts,
- printers,
- service connection points,
- Group Policy containers.

Každý object má distinguished name a ďalšie identifiers, napríklad SID alebo object GUID podľa typu a use case-u.

## 3. Forest

Forest je najvyššia AD DS logical security a schema boundary.

Domains vo forest-e zdieľajú:

- schema,
- configuration partition,
- global catalog,
- forest-wide trusts,
- niektoré forest-wide operations roles.

Forest admin alebo compromise forest-level controlu má extrémne široký blast radius. Samostatný domain nie je plná isolation boundary voči forest admins.

## 4. Domain

Domain je logical partition s:

- vlastným DNS name,
- users, groups, computers a policies,
- domain-wide replication,
- domain SID namespace,
- domain-specific operations master roles.

Väčšina organizácií nepotrebuje vytvárať veľa domains iba podľa organizačnej štruktúry. OUs a delegation často riešia administratívne členenie s nižšou komplexitou.

## 5. Organizational Units

OU je container používaný hlavne na:

- delegation administration,
- aplikáciu Group Policy,
- organizáciu objects.

OU nie je authentication realm ani automatická security boundary.

ACL na OU a inheritance určujú, kto môže meniť objects. Nesprávna delegation môže umožniť reset passwords, pridať members do privilegovaných groups alebo meniť computer accounts.

## 6. Domain controllers

Domain controller hostuje directory partitions a poskytuje:

- LDAP,
- Kerberos KDC,
- authentication,
- replication,
- Group Policy/SYSVOL access,
- service discovery cez DNS.

Production návrh potrebuje viac DCs v relevantných sites/failure domains.

DC nie je bežný application server. Kompromitácia domain controllera môže viesť ku kompromitácii celej domény alebo forest-u.

## 7. Directory partitions

AD DS používa naming contexts/partitions:

- schema partition,
- configuration partition,
- domain partition,
- application partitions podľa use case-u.

Replication scope sa líši podľa partition.

Global Catalog obsahuje partial attribute set z objects naprieč forestom a umožňuje forest-wide search a podporu niektorých logon/group resolution scenárov.

## 8. DNS dependency

AD DS silno závisí od DNS.

Clients používajú DNS SRV records na nájdenie:

- domain controllers,
- Kerberos services,
- Global Catalog,
- site-appropriate services.

Typický troubleshooting chain:

```text
client DNS configuration
→ domain DNS zone
→ SRV records
→ DC locator
→ network ports
→ LDAP/Kerberos communication
```

Použitie public DNS resolvera priamo na domain clientovi často poškodí domain discovery.

## 9. Sites a subnets

AD sites reprezentujú network topology a používajú sa na:

- client affinity k blízkemu DC,
- replication topology,
- service location,
- riadenie cross-site trafficu.

Subnets musia byť správne mapované na sites. Inak sa client môže autentizovať vo vzdialenom DC a replication môže byť neefektívna.

AD DS používa multimaster, store-and-forward replication. Nie všetky operácie sú však multimaster.

## 10. FSMO roles

Flexible Single Master Operations roles riešia úlohy, ktoré nemajú byť vykonávané súčasne viacerými DCs.

Forest-wide:

- Schema Master,
- Domain Naming Master.

Per-domain:

- RID Master,
- PDC Emulator,
- Infrastructure Master.

PDC Emulator je významný pre:

- time hierarchy,
- password change preference,
- account lockout a compatibility scenáre,
- niektoré Group Policy operations.

FSMO role holder outage má odlišný dopad podľa role a duration. Nie každý výpadok vyžaduje okamžité seizure.

## 11. Replication

Replication závisí od:

- DNS,
- network connectivity,
- authentication/authorization,
- directory database,
- topology,
- time,
- SYSVOL/DFSR podľa obsahu.

Concepts:

- update sequence numbers,
- invocation ID,
- replication metadata,
- up-to-dateness vectors,
- site links a schedules,
- Knowledge Consistency Checker.

Neopravuj replication manuálnym kopírovaním directory database alebo SYSVOL súborov.

## 12. Conflict a convergence

Multimaster replication znamená, že changes môžu vzniknúť na rôznych DCs.

Directory používa replication metadata a conflict-resolution rules na convergence.

Operational otázky:

- Kde change vznikol?
- Replikoval sa do všetkých partnerov?
- Je object tombstoned/deleted?
- Existuje lingering object?
- Je problém iba v AD database alebo aj SYSVOL/DNS?

## 13. Authentication

AD DS štandardne používa Kerberos pre domain authentication, s NTLM compatibility/fallback scenármi.

Kerberos potrebuje:

- správny DNS,
- synchronizovaný čas,
- service principal names,
- funkčný KDC/DC,
- správne keys a encryption support.

NTLM usage má byť inventoryované a redukované, pretože môže signalizovať legacy dependency alebo chybný Kerberos configuration.

## 14. Security identifiers a access tokens

Windows authorization používa SIDs.

Po authentication sa vytvorí access token obsahujúci napríklad:

- user SID,
- group SIDs,
- privileges,
- integrity/context fields.

Resource DACL sa vyhodnocuje voči tokenu.

Group membership zmena nemusí byť viditeľná v už existujúcej logon session. Môže byť potrebné vytvoriť novú session/token.

## 15. Groups

Group scopes:

- domain local,
- global,
- universal.

Typický model AGDLP/AGUDLP oddeľuje:

```text
Accounts
→ Global groups
→ Universal groups podľa potreby
→ Domain Local groups
→ Permissions
```

Cieľom je nevkladať jednotlivých users priamo do veľkého množstva resource ACLs.

Nested groups zjednodušujú správu, ale komplikujú effective access a token size.

## 16. Group Policy

Group Policy Objects majú directory a SYSVOL časti.

Aplikácia závisí od:

- site/domain/OU linkov,
- inheritance a enforced/block inheritance,
- security filtering,
- WMI filters,
- client-side extensions,
- SYSVOL dostupnosti,
- replication.

Troubleshooting musí porovnať AD metadata a SYSVOL content.

## 17. Schema

Schema definuje object classes a attributes.

Schema extension je forest-wide a typicky ťažko vratná. Vyžaduje:

- compatibility review,
- unique OIDs,
- test forest,
- backup/recovery plán,
- ownera a dokumentáciu.

Aplikácia nemá rozširovať schema bez dlhodobého lifecycle záväzku.

## 18. Trusts

Trust umožňuje authentication path medzi domains alebo forests.

Properties:

- direction,
- transitivity,
- scope,
- selective authentication,
- SID filtering,
- name suffix routing.

Trust nie je automatické povolenie na resource. Umožňuje identitu rozpoznať; authorization stále vyžaduje permission.

## 19. Service accounts

Preferuj podľa platformy:

- group Managed Service Accounts,
- managed identities v cloud scenároch,
- oddelené service principals,
- automatickú password/key rotation.

Riziká klasických service accounts:

- password never expires,
- interactive logon,
- broad group membership,
- shared use,
- SPN conflicts,
- neznámy owner.

## 20. Tiering a privileged administration

Privileged identities a devices majú byť oddelené podľa trust tieru.

Controls:

- separate admin accounts,
- privileged access workstations,
- deny logon na nižších tiers,
- JIT/JEA/PAM podľa prostredia,
- monitorovanie privileged groups,
- chránené admin sessions.

Domain admin credential použitý na kompromitovanom workstatione môže kompromitovať celú doménu.

## 21. Backup a recovery

AD recovery potrebuje:

- System State backups relevantných DCs,
- forest recovery plán,
- DSRM credentials,
- authoritative/non-authoritative restore znalosti,
- pravidelné recovery rehearsal,
- backup isolation.

Snapshot hypervisora nie je univerzálny substitute za podporovaný AD recovery model.

Recycle Bin pomáha pri object deletion, ale nerieši každý forest-wide compromise alebo corruption scenár.

## 22. Monitoring

Sleduj:

- DC availability,
- DNS a SRV records,
- replication failures/latency,
- SYSVOL/NETLOGON shares,
- time synchronization,
- authentication failures,
- account lockouts,
- privileged group changes,
- directory service events,
- disk/database health,
- backup/restore validation,
- certificate a secure LDAP lifecycle.

## 23. Troubleshooting domain logon

```text
client time
→ client DNS points to AD DNS?
→ domain/DC SRV lookup?
→ closest site?
→ network ports/firewall?
→ computer trust/account?
→ Kerberos ticket alebo NTLM fallback?
→ account state/lockout?
→ DC health a replication?
→ policy/GPO?
```

Zachovaj `whoami`, `klist`, DNS queries, event IDs, chosen DC a exact timestamp.

## 24. Troubleshooting replication

```text
scope: jeden partner, site alebo forest?
→ DNS/name resolution?
→ network/RPC?
→ authentication/time?
→ replication metadata a error code?
→ topology/site link?
→ database alebo lingering objects?
→ SYSVOL oddelene?
```

Nástroje typicky zahŕňajú `repadmin`, PowerShell AD cmdlets, event logs a DNS diagnostics.

## 25. Troubleshooting Group Policy

```text
object v správnej OU?
→ link order/inheritance?
→ security/WMI filtering?
→ user vs computer scope?
→ AD/SYSVOL replication?
→ client processing/event logs?
→ resultant set of policy?
```

GPO existence v konzole nepreukazuje, že sa aplikovalo na konkrétneho clienta.

## 26. AD DS oproti Entra ID a Entra Domain Services

### AD DS

- domain controllers,
- LDAP/Kerberos/NTLM,
- Group Policy,
- forests/domains/OUs,
- customer-operated infrastructure.

### Microsoft Entra ID

- cloud IAM,
- modern federation/token protocols,
- cloud apps/resources,
- tenant model.

### Microsoft Entra Domain Services

- managed domain services pre LDAP, Kerberos/NTLM, domain join a Group Policy,
- integrácia/synchronizácia s Entra ID,
- bez customer managementu domain controllers,
- odlišné operational constraints než plné AD DS.

Tieto platformy nie sú interchangeable.

## 27. Anti-patterny

### Jeden domain controller

Vytvára availability a maintenance risk.

### Public DNS na domain clients

Rozbíja service discovery.

### Domain Admin na bežný workstation

Credential exposure má forest-level dopad.

### OU ako security isolation boundary

Forest admins a delegated ACLs môžu boundary prekročiť.

### Snapshot ako jediný backup

Nerieši podporovaný forest recovery contract.

### NTLM ignorované

Legacy path zostáva neviditeľná a zvyšuje attack surface.

### Schema extension bez lifecycle plánu

Vytvára trvalý forest-wide záväzok.

## 28. Kontrolné otázky

1. Aký je rozdiel medzi forest, domain a OU?
2. Prečo forest predstavuje dôležitú security boundary?
3. Ako AD DS používa DNS?
4. Ako sites a subnets ovplyvňujú clients a replication?
5. Ktoré FSMO roles existujú?
6. Ako funguje multimaster replication?
7. Ako Kerberos, LDAP a Group Policy súvisia s AD DS?
8. Ako group scopes a nested groups ovplyvňujú access?
9. Prečo AD DS nie je Entra ID?
10. Ako diagnostikuješ domain logon alebo replication incident?

## Glossary impact

Relevantné pojmy: Active Directory Domain Services, forest, domain, domain controller, organizational unit, directory partition, Global Catalog, site, subnet, DC locator, FSMO, PDC Emulator, multimaster replication, SYSVOL, Group Policy, SID, access token, domain local group, global group, universal group, trust, gMSA, DSRM a forest recovery.

## Primárne zdroje

- [Active Directory Domain Services overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview)
- [Understanding the Active Directory logical model](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/understanding-the-active-directory-logical-model)
- [DNS and AD DS](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/dns-and-ad-ds)
- [FSMO roles](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-fsmo-roles)
- [Troubleshooting AD replication](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/troubleshoot/troubleshooting-active-directory-replication-problems)
- [Microsoft Entra Domain Services overview](https://learn.microsoft.com/en-us/entra/identity/domain-services/overview)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: IAM a RBAC](iam-rbac.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: LDAP →](ldap.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
