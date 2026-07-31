# Active Directory

Active Directory Domain Services — AD DS — je distribuovaná directory, authentication a policy platforma. Bezpečnostný výsledok nevzniká iba tým, že user alebo group object existuje. Závisí od toho, na ktorom domain controlleri change vznikol, kam sa replikoval, ktorý DC našiel client, aký LDAP a Kerberos state načítal, ktoré claims alebo PAC z neho vznikli a ako dlho prežijú downstream sessions.

AD DS preto treba chápať ako versionovaný identity state distribuovaný cez DNS, sites, subnets, replication, Global Catalog, LDAP, Kerberos a SYSVOL boundaries. „Membership removed“ na jednom DC nepreukazuje revocation v enterprise. Revocation je hotová až vtedy, keď required replicas convergujú, clients vyberajú správnu repliku a sessions odvodené zo starej generation sú zrušené.

## Directory-change lifecycle

```text
authoritative identity alebo policy change
→ exact forest/domain/object/DC generation
→ local directory commit a replication metadata
→ site topology, schedule a transport
→ inbound apply na required DC/GC replicas
→ DNS/DC locator a client-selected replica
→ LDAP/Kerberos/GPO read
→ logon, PAC/group alebo policy effective state
→ resource authorization a downstream session
→ convergence, revocation a second-session verdict
```

Každá šípka je samostatná failure boundary. Successful write na originating DC nepreukazuje outbound eligibility. Healthy replication connection nepreukazuje, že konkrétny attribute version dorazil. Fresh user login nepreukazuje fresh authorization, ak client vybral stale DC.

## Exact AD subject SEC-PAY-48

```yaml
forest: corp.atlas.example
domain: corp.atlas.example
object: CN=Marcel Novak,OU=Finance,DC=corp,DC=atlas,DC=example
objectGuid: 4b7a6d2d-7731-4cc1-a9fa-8842d2d72a11
userSid: S-1-5-21-8841-7732-9911-7421
removedGroup: GG-PAY-Settlement-Approvers
originatingDC: DC-BTS-01
originatingChangeTime: 2026-07-29T07:40:00Z
requiredReplica: DC-FRA-02
siteLink: BTS-FRA
clientSubnet: 10.48.24.0/24
clientSite: FRA-PROD
selectedDC: DC-FRA-02
kerberosTicketTime: 2026-07-29T08:11:00Z
incident: SEC-PAY-48
```

GUID identifikuje directory object stabilnejšie než distinguished name, ktorý sa pri move zmení. SID je authorization identity vo Windows security descriptoroch a PAC. Attribute replication metadata nesie version, originating USN, originating server a timestamp konkrétnej zmeny. Tieto identities sa pri incidente nesmú zamieňať.

## Forest, domain, OU a administrative boundaries

Forest je hlavný AD DS security a schema boundary. Domains poskytujú naming, replication a policy scope, ale trust v rámci forestu znamená, že kompromitovaný forest-level alebo privileged directory control môže zasiahnuť všetky domains. OU je organizačný a delegation scope, nie samostatná security boundary voči domain adminovi.

Domain controller hostí writable alebo read-only directory partitions, Kerberos KDC, LDAP endpoint a často DNS. Global Catalog obsahuje partial attribute set z forestu pre search a universal-group resolution. FSMO roles koordinujú špecifické operácie, no bežná directory dostupnosť nestojí na jednom „primary DC“.

## DNS, sites, subnets a DC locator

Client nevyberá DC náhodne. Používa DNS SRV records a site information odvodenú z IP subnet mappingu. Ak subnet nie je priradený k správnemu AD site-u, client môže použiť vzdialený alebo stale DC aj pri healthy lokálnej replike.

Praktický read-back na Windows clientovi:

```powershell
nltest /dsgetsite
nltest /dsgetdc:corp.atlas.example /force
Resolve-DnsName _ldap._tcp.FRA-PROD._sites.dc._msdcs.corp.atlas.example -Type SRV
```

Prvý príkaz preukazuje site, ktorú client aktuálne odvodil. Druhý ukáže vybraný DC a flags, tretí DNS candidates pre site-specific LDAP service. Nepreukazujú freshness konkrétneho user attribute ani to, že Kerberos a LDAP použijú tú istú repliku počas celej transakcie.

Pre incident subnet `10.48.24.0/24` neexistoval v AD Sites and Services. Client preto spadol do broader locator pathu a vybral `DC-FRA-02`, ktorý ešte nemal membership removal.

## Replication ako causal state transition

AD replication je multimaster a attribute-version-aware. Zmena sa najprv commitne lokálne, získa originating metadata a cez connection objects a site links sa replikuje podľa topology a schedule. „Replication successful“ musí byť viazaná na exact object a attribute, nie iba na všeobecnú zelenú repliku.

Základný stav topology a backlogu:

```powershell
repadmin /replsummary
repadmin /showrepl DC-FRA-02
repadmin /showobjmeta DC-FRA-02 "CN=Marcel Novak,OU=Finance,DC=corp,DC=atlas,DC=example"
```

`/replsummary` ukáže aggregate failures a latency. `/showrepl` ukáže inbound neighbors a last attempts. `/showobjmeta` je diskriminačný dôkaz pre konkrétne attributes a versions. Ani jeden príkaz sám nepreukazuje, že client používa správny DC alebo že issued tickets a application sessions boli revoke-nuté.

PowerShell môže porovnať membership na dvoch DCs:

```powershell
Get-ADPrincipalGroupMembership -Identity 7421 -Server DC-BTS-01 |
  Select-Object -ExpandProperty DistinguishedName

Get-ADPrincipalGroupMembership -Identity 7421 -Server DC-FRA-02 |
  Select-Object -ExpandProperty DistinguishedName
```

Rozdiel medzi výstupmi preukazuje replica divergence v čase query. Nepreukazuje root cause topology failure; na to treba site-link schedule, RPC/network path, connection objects a replication metadata.

## SYSVOL, Group Policy a logon state

Group Policy má directory časť a SYSVOL files. Directory replication môže byť healthy, zatiaľ čo SYSVOL alebo DFS Replication zaostáva. Client potom nájde GPO object, ale načíta starý template. GPO troubleshooting preto spája selected DC, user/computer scope, security/WMI filtering, version numbers a client-side processing logs.

Kerberos a Windows logon používajú authorization snapshot. PAC môže obsahovať group memberships platné v čase ticket issuance. Neskoršia directory zmena automaticky neprepíše už vydaný ticket ani local logon session. Revocation musí počítať s ticket lifetime, service sessions a downstream tokens.

## Privileged administration a recovery

AD recovery boundary je forest, nie jeden domain controller. Secure administration používa oddelené privileged identities, hardened workstations, minimálny standing membership, JIT/JEA podľa capability, monitoring zmien v privileged groups a testovaný forest-recovery plán. DSRM credential, system-state backup a backup encryption keys sú recovery secrets s vlastným lifecycle-om.

Virtual-machine snapshot alebo nekontrolované restore-nutie DC nie je bežný rollback identity state-u. Recovery musí rešpektovať AD replication semantics, authoritative/non-authoritative restore a protection pred USN rollbackom. Pri compromise sa navyše rieši trust recovery, credential rotation a persistence, nie iba availability directory služby.

## Worked incident: fresh session z neconverged state-u

O 07:40 UTC odstránil `DC-BTS-01` principal 7421 zo skupiny `GG-PAY-Settlement-Approvers`. Local commit bol správny. Site link `BTS-FRA` však mal chybnú schedule a change sa do `DC-FRA-02` nepreniesol. Chýbajúce subnet mapping spôsobilo, že application host v sieti `10.48.24.0/24` vybral stale FRA replica.

Competing hypotheses zahŕňali starú Windows session, LDAP cache, odstránenie nesprávnej skupiny, SIDHistory, replication lag a nesprávny DC locator. Fresh LDAP query priamo proti `DC-FRA-02` stále vracala group. Fresh TGT vydaný o 08:11 obsahoval privileged PAC. Tým sa vylúčilo, že problém je iba stará client cache alebo prežitá session.

Root cause bol neconverged directory state. Missing subnet mapping a stale replica selection boli causal amplifiers. Protocols fungovali správne nad nesprávnou generation.

## Evidence-preserving containment

Containment najprv zablokuje privileged application operation a suspenduje affected principal bez broad vypnutia všetkých DCs. Zachová object metadata z originating aj stale replica, site/subnet configuration, replication summary, KDC events, LDAP query evidence a downstream authorization logs. Force replication sa nevykoná skôr, než sa uloží divergence evidence; inak sa stratí dôkaz o pôvodnej generation a topology path.

## Authoritative recovery

Recovery opraví `BTS-FRA` schedule a RPC/network path, pridá subnet `10.48.24.0/24` do `FRA-PROD`, nechá change convergovať a overí exact object metadata na všetkých required DC/GC replicas. Potom revoke-ne Kerberos tickets, application sessions a OAuth descendants odvodené zo stale state-u.

```powershell
repadmin /syncall DC-FRA-02 /AdeP
Get-ADReplicationAttributeMetadata \
  -Object "CN=Marcel Novak,OU=Finance,DC=corp,DC=atlas,DC=example" \
  -Server DC-FRA-02 \
  -ShowAllLinkedValues
```

Force sync je remediation až po oprave topology a zachovaní evidence. Metadata read-back preukazuje applied attribute generation na konkrétnej replike; nepreukazuje revocation už vydaných tickets ani business authorization.

Acceptance vyžaduje rovnakú membership generation na required replicas, správny site selection, fresh TGT bez privileged group, fresh LDAP query bez membership, denied application operation a neexistenciu alternate direct, nested alebo SIDHistory pathu. Druhý removal/add-remove test musí opäť convergovať v definovanom intervale; jednorazový force sync bez topology closure nie je stabilná oprava.

## Kontrolné otázky

1. Prečo successful write na jednom DC nepreukazuje enterprise revocation?
2. Ako subnet mapping ovplyvní security outcome?
3. Čo `/showobjmeta` preukazuje navyše oproti `replsummary`?
4. Prečo fresh TGT môže stále obsahovať stale authorization?
5. Ako sa directory replication líši od session revocation?
6. Prečo treba zachovať replica divergence pred force sync?
7. Ktorý second-change test uzatvára topology recovery?

## Referencie

- [Microsoft Active Directory Domain Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/active-directory-domain-services)
- [AD DS replication](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/replication/active-directory-replication-concepts)
- [DC locator](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/dc-locator)
- [Forest recovery guide](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-guide)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: IAM a RBAC](iam-rbac.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: LDAP →](ldap.md)
<!-- KNOWLEDGE-NAVIGATION:END -->