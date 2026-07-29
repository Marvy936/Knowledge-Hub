# Active Directory

Active Directory Domain Services — AD DS — je distribuovaná directory, authentication a policy platforma. Bezpečnostný výsledok nevzniká iba tým, že user alebo group object existuje. Závisí od toho, na ktorom domain controlleri change vznikol, kam sa replikoval, ktorý DC našiel client, aký directory a Kerberos state načítal a ktoré sessions alebo downstream tokens boli z tohto state-u vytvorené.

AD DS preto treba chápať ako versionovaný identity state distribuovaný cez DNS, sites, replication, LDAP, Kerberos, SYSVOL a Windows authorization boundaries.

## 1. Dominantný lifecycle

```text
authoritative identity alebo policy change
→ exact forest/domain/object/DC generation
→ local directory commit a replication metadata
→ topology, site link a partition replication
→ DNS/DC locator a selected replica
→ LDAP/Kerberos/Group Policy read
→ logon token, group alebo policy effective state
→ resource/application authorization
→ audit a convergence verdict
→ revocation, recovery a second-session validation
```

Tento lifecycle oddeľuje stavy, ktoré sa často zamieňajú:

```text
change je uložený na jednom DC
≠ change je replikovaný do všetkých required replicas
≠ client číta converged replica
≠ existujúca logon session používa nový group state
≠ downstream application alebo token už starý access nepovoľuje
```

## 2. Exact AD DS subject

Pri incidente nestačí názov domény. Zaznamenaj:

```text
forest a domain
schema/config/domain partition
object GUID, SID a distinguished name
attribute alebo group edge
originating DC a originating time
attribute version, USN a invocation ID
replication partners, sites a site links
selected client/KDC/LDAP DC
authentication a logon-session generation
SYSVOL/GPO generation, ak je relevantná
application alebo resource consumer
```

Connected Atlas Payments subject:

```text
security incident: SEC-PAY-48
AD subject: AD-PAY-48
forest/domain: corp.atlas.example
privileged group: GG-PAY-Settlement-Approvers
member SID: S-1-5-21-2418-6317-9044-1842
origin DC: DC-BTS-01
stale DC: DC-FRA-02
sites: Bratislava-HQ, Frankfurt-Prod
management subnet: 10.48.24.0/24
membership removal: 2026-07-29 07:40 UTC
```

## 3. Forest, domain a OU riešia odlišné boundaries

Forest zdieľa schema, configuration partition, Global Catalog model a transitive trust fabric. Forest-level compromise má preto mimoriadne široký blast radius. Samostatný domain nie je plná isolation boundary voči forest-level administration.

Domain poskytuje vlastný DNS namespace, domain partition, SID namespace, domain controllers a domain-wide policies. Organizational Unit je administratívny container pre delegation a Group Policy. OU nie je samostatný authentication realm ani pevná security boundary; jej ACL a inheritance môžu byť zle delegované alebo prekročené vyššou forest/domain authority.

Praktické pravidlo:

```text
organizácia objects alebo GPO targeting → OU
separate namespace a domain replication scope → domain
separate high-assurance security boundary → spravidla separate forest alebo iná platformová boundary
```

## 4. Objects, schema a identifiers

AD DS uchováva users, groups, computers, service accounts, OUs, Group Policy containers a ďalšie objects. Schema určuje object classes, attributes, syntax a constraints.

Dôležité identities:

- distinguished name opisuje aktuálnu pozíciu objectu;
- object GUID stabilne identifikuje object cez rename alebo move;
- SID sa používa vo Windows authorization;
- `sIDHistory` a trust translation môžu vytvoriť ďalšiu effective access cestu;
- attribute replication metadata identifikuje verziu a origin change-u.

Schema extension je forest-wide a ťažko vratná. Potrebuje unique OID, compatibility review, test forest, ownera a recovery plán.

## 5. Domain controller a directory partitions

Domain controller poskytuje viac navzájom previazaných services:

```text
LDAP directory
+ Kerberos KDC
+ Windows authentication
+ DNS-integrated discovery
+ AD replication
+ SYSVOL/NETLOGON
+ Group Policy distribution
```

Directory používa minimálne schema, configuration a domain partitions. Application partitions majú vlastný replication scope. Global Catalog drží partial attribute set z objects naprieč forestom a podporuje forest-wide lookup a niektoré logon/group-resolution paths.

Healthy process alebo reachable LDAP port nepreukazuje, že DC má aktuálnu required partition alebo SYSVOL generation.

## 6. DNS, sites, subnets a DC locator

AD clients objavujú domain controllers, KDCs a Global Catalog cez DNS SRV records a DC locator. Sites a subnet objects mapujú network location na vhodné services a replication topology.

```text
client IP
→ matching AD subnet object
→ AD site
→ DNS SRV/DC locator
→ preferred local DC/KDC/GC
→ fallback mimo site, ak local path nie je dostupný
```

Chýbajúci alebo prekrývajúci sa subnet môže spôsobiť, že client použije vzdialený alebo nečakaný DC. To mení latency, availability aj freshness identity state-u.

Pri diagnostike zachovaj:

- client IP, DNS servers a timestamp;
- výsledok site determination;
- queried SRV records;
- selected DC/KDC/GC;
- fallback dôvod;
- network path a firewall/RPC state.

Public DNS resolver priamo na domain clientovi nie je náhrada AD-integrated DNS discovery.

## 7. Replication je causal state transition

Multimaster neznamená okamžitú globálnu consistency. Change vznikne na jednom DC, získa replication metadata a prechádza topology podľa partition, site linkov, schedule, availability a partner state-u.

```text
LDAP write na origin DC
→ local commit
→ attribute version/USN/invocation identity
→ replication notification alebo scheduled intersite transfer
→ partner apply
→ ďalšia propagation
→ convergence verdict
```

Pri každom security-relevant change-i rozlišuj:

- originating write success;
- outbound replication eligibility;
- inbound apply na required DCs;
- Global Catalog alebo SYSVOL convergence;
- client selection konkrétnej replica;
- cache/session state odvodený pred alebo po convergence.

Manual copy `ntds.dit` alebo SYSVOL súborov nie je podporovaná replication recovery.

## 8. Replication metadata a conflict model

Replication troubleshooting potrebuje object-level evidence, nie iba všeobecný `replication healthy` dashboard.

Over:

```text
object GUID/DN
→ attribute version
→ originating DC a time
→ local USN a invocation ID
→ up-to-dateness vector
→ partner failure/error
→ tombstone/lingering-object state
```

Multimaster conflict resolution vedie ku convergence podľa metadata rules; nemusí zachovať business intent posledného human change-u. Preto destructive alebo security-sensitive conflict potrebuje application/owner validation.

## 9. FSMO roles

Nie všetky operations sú multimaster. Forest-wide FSMO roles sú Schema Master a Domain Naming Master. Per-domain roles sú RID Master, PDC Emulator a Infrastructure Master.

PDC Emulator je dôležitý pre time hierarchy, password-change preference, lockout a compatibility paths. Outage FSMO holdera má odlišný dopad podľa role a duration. Seizure je recovery decision po posúdení návratu pôvodného ownera, nie reflex pri každom krátkom výpadku.

## 10. LDAP, Kerberos a Windows authorization

AD DS spája viac vrstiev, ktoré sa nesmú zlúčiť:

```text
LDAP
→ číta alebo mení directory state

Kerberos/NTLM
→ autentizuje principal a vytvára security context

Windows access token + ACL/policy
→ rozhoduje effective OS/resource access

application policy
→ rozhoduje business operation
```

Fresh Kerberos authentication voči stale DC môže byť cryptographically validná a súčasne niesť starý group state. LDAP search na inom DC môže v rovnakom čase vrátiť inú membership generation.

## 11. Groups a effective Windows access

Group scopes — global, universal a domain local — umožňujú modelovať accounts, business memberships a resource permissions. AGDLP/AGUDLP oddeľuje user membership od resource ACLs.

Nested groups však vytvárajú graph:

```text
user SID
→ global/universal memberships
→ domain-local resource group
→ ACL allow
```

Po logine Windows access token typicky obsahuje user SID, group SIDs a privileges. Zmena group membership neprepíše automaticky už existujúci token. Potrebná môže byť nová logon session, service restart alebo explicitná downstream revocation.

Pre access review preto nestačí skontrolovať current group object. Potrebuješ effective graph aj active sessions/tokens.

## 12. Group Policy ako dvojdielna generation

Group Policy Object má directory metadata a SYSVOL content. Effective application závisí od:

```text
site/domain/OU links
→ link order, inheritance a enforced state
→ security a WMI filtering
→ AD metadata generation
→ SYSVOL content generation
→ client-side extension processing
→ resultant set of policy
```

GPO viditeľné v konzole nepreukazuje, že konkrétny client načítal matching AD aj SYSVOL generation. AD/SYSVOL divergence môže vytvoriť partial policy state.

## 13. Trusts a service identities

Trust umožní authentication path medzi domains alebo forests; neudeľuje automaticky resource permission. Direction, transitivity, selective authentication, SID filtering a name-suffix routing určujú blast radius.

Service identities potrebujú explicitný owner, SPNs, allowed hosts, group memberships a rotation. Preferuj gMSA alebo iný managed mechanismus tam, kde je podporovaný. Classic account s `password never expires`, interactive logon a broad groups je hidden long-term credential path.

## 14. Privileged administration a recovery boundary

Domain controllers a privileged admin sessions patria do najvyššieho trust tieru. Domain-admin credential na bežnom workstatione prenáša forest/domain authority do nižšej boundary.

Controls:

- separate privileged accounts a workstations;
- minimal standing membership;
- JIT/JEA/PAM podľa platformy;
- monitoring privileged group a delegation changes;
- protected backups a DSRM/recovery credentials;
- tested forest recovery;
- žiadne implicitné spoliehanie sa iba na hypervisor snapshot.

Recycle Bin rieši vybrané object deletions. Nerobí forest compromise dôveryhodne obnoviteľným.

## 15. Worked failure: fresh session z neconverged directory state-u

### Symptom

O `08:17 UTC` bývalá settlement approverka úspešne schváli provider-route change, hoci jej privileged membership bola odstránená o `07:40 UTC`. Security tím najprv predpokladá ukradnutý starý browser token.

### Exact subject

```text
incident: SEC-PAY-48
AD subject: AD-PAY-48
user: martina.kovacova@corp.atlas.example
user SID: S-1-5-21-2418-6317-9044-1842
privileged group: GG-PAY-Settlement-Approvers
originating removal DC: DC-BTS-01
consumer/KDC DC: DC-FRA-02
site link: BTS-FRA
management subnet: 10.48.24.0/24
```

### Competing hypotheses

1. stará Windows logon session prežila membership removal;
2. LDAP application cache neexpirovala;
3. removal sa zapísal na nesprávny group object;
4. replication medzi DCs neconvergovala;
5. client použil nečakaný DC pre chýbajúci subnet mapping;
6. `sIDHistory`, nested group alebo alternate account stále udeľuje access;
7. downstream OAuth/resource policy ignoruje current eligibility.

### Discriminating evidence

```text
DC-BTS-01 group member attribute:
  removal version 44, originating time 07:40 UTC

DC-FRA-02 group member attribute:
  version 43, user SID stále prítomný

BTS-FRA site-link schedule:
  replication blocked 07:00–10:00 UTC po maintenance change-i

10.48.24.0/24:
  bez matching AD subnet objectu

client DC locator:
  selected DC-FRA-02

Kerberos logon:
  nový TGT vydaný 08:11 UTC, teda po removal-e
  PAC/group state obsahuje privileged group SID

LDAP query na DC-FRA-02:
  user stále member

LDAP query na DC-BTS-01:
  user už nie je member
```

Fresh session diskriminuje hypotézu, že išlo iba o starý pre-removal cache. Root cause je neconverged directory state spôsobený chybnou intersite replication schedule. Chýbajúci subnet mapping je causal amplifier, pretože client a consumers vybrali stale DC.

### Evidence-preserving containment

- zastaviť ďalšie privileged approvals pre affected identity/cohort;
- zachovať replication metadata, site-link revision, DNS/DC locator, KDC, LDAP a application audit;
- revoke-nuť downstream application/OAuth sessions a refresh grants;
- pri podozrení na compromise dočasne disable-nuť account podľa incident policy;
- neprepisovať membership manuálne na každom DC bez zachovania origin a metadata;
- nezvyšovať privilege ani neobchádzať policy cez emergency shared admin účet.

### Authoritative recovery

1. obnoviť intended `BTS-FRA` replication schedule a network/RPC path;
2. vytvoriť správny subnet-to-site mapping pre `10.48.24.0/24`;
3. spustiť podporovanú replication convergence a overiť object metadata na všetkých required DC/GC replicas;
4. potvrdiť odstránenie nested, direct aj `sIDHistory` access paths;
5. vytvoriť novú logon session a overiť, že privileged SID v tokene/PAC chýba;
6. zneplatniť application/OAuth sessions odvodené zo stale state-u;
7. zosúladiť high-risk authorization s JIT entitlementom a fresh eligibility checkom;
8. auditovať actions vykonané počas exposure window-u a obnoviť affected business state.

### Acceptance verdict

Incident možno uzavrieť až keď:

- removal metadata je rovnaká na required writable DCs a GCs;
- client v každom relevantnom site vyberie intended DC;
- fresh Kerberos a LDAP reads neobsahujú privileged membership;
- existing session, refresh grant a downstream access token sú neplatné;
- oprávnený JIT approver môže schváliť validný settlement;
- removed principal nedokáže schváliť cez UI, direct API, alternate DC ani nested group;
- druhá controlled membership removal prejde convergence a second-login testom;
- directory, KDC, LDAP a resource audit vytvoria kompletný actor-to-outcome chain.

## 16. Troubleshooting flow

### Domain logon

```text
client time a DNS
→ site/subnet mapping
→ SRV lookup a selected DC/KDC
→ account/computer trust
→ AS/TGS/AP alebo NTLM fallback
→ group/PAC/access-token state
→ application/resource authorization
```

### Replication

```text
exact object/attribute
→ originating metadata
→ partner/topology/site-link eligibility
→ DNS/RPC/auth/time
→ inbound apply a error code
→ partition/SYSVOL distinction
→ client-selected replica
→ business/security outcome
```

### Group Policy

```text
object a OU
→ link/inheritance/filtering
→ AD metadata generation
→ SYSVOL generation
→ client processing
→ resultant set
→ intended a forbidden behavior
```

## 17. Earlier controls

- change-triggered convergence SLO pre privileged membership removal;
- alert na privileged change, ktorý nie je do limitu prítomný na required DCs;
- automated subnet coverage a overlap validation;
- object-level replication canary medzi sites;
- session/token revocation hook pri mover/leaver a privileged removal events;
- high-risk application authorization, ktorá sa nespolieha iba na long-lived group snapshot;
- pravidelný test forest recovery, DSRM a isolated backup restore;
- explicitný owner site links, trusts, privileged groups, gMSA a schema extensions.

## 18. Anti-patterny

### Jeden green DC reprezentuje celú doménu

Local health nepreukazuje partition convergence ani client selection.

### Group removal = okamžitá revocation

Existing logon sessions, PACs, application caches a OAuth tokens môžu prežiť.

### OU ako isolation boundary

Delegated ACL alebo vyššia forest/domain authority ju môže prekročiť.

### Ručný write na všetky DCs

Ničí causal metadata a môže vytvoriť conflicts namiesto opravy topology.

### Snapshot ako jediný recovery model

Neoveruje podporovaný directory/forest recovery a trust state.

### NTLM fallback ako úspech

Maskuje SPN, DNS alebo Kerberos defect a zachováva slabší path.

## 19. Kontrolné otázky

1. Prečo local write success nie je replication convergence?
2. Ako sa forest, domain a OU líšia ako security boundaries?
3. Ako DNS, sites a subnets určujú selected DC?
4. Čo identifikujú attribute version, originating DC a invocation ID?
5. Prečo fresh Kerberos session môže obsahovať stale group state?
6. Ako sa LDAP, Kerberos, Windows token a application policy dopĺňajú?
7. Prečo membership removal neukončí existujúce sessions?
8. Ako sa AD a SYSVOL generations podieľajú na Group Policy?
9. Kedy je FSMO seizure oprávnené recovery rozhodnutie?
10. Čo musí overiť AD acceptance verdict po security incidente?

## Glossary impact

Relevantné pojmy: AD DS subject, directory convergence generation, originating directory change, replication metadata, client-selected replica, site/subnet coverage, DC locator evidence, group-state generation, fresh-but-stale logon, AD/SYSVOL generation pair, privileged-removal convergence a AD acceptance verdict.

## Primárne zdroje

- [Active Directory Domain Services overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview)
- [Active Directory replication concepts](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/replication/active-directory-replication-concepts)
- [Active Directory replication troubleshooting](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/troubleshoot-adreplication-guidance)
- [Active Directory sites and replication](https://learn.microsoft.com/en-us/training/modules/active-directory-site-replication/)
- [Active Directory security groups](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups)
- [FSMO roles](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-fsmo-roles)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: IAM a RBAC](iam-rbac.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: LDAP →](ldap.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
