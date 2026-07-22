# Security identity, directory and Kerberos glossary entries

## Access review

Pravidelné alebo event-driven overenie, či principal stále potrebuje pridelené permissions, či ich scope a duration zostávajú primerané a či access možno odstrániť. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Account

Administratívny záznam identity v konkrétnom systéme, ktorý môže mať vlastný lifecycle, credentials, attributes a permissions. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Active Directory Domain Services — AD DS

Distribuovaná Microsoft directory a identity platforma poskytujúca domains, forests, domain controllers, LDAP, Kerberos/NTLM, DNS-integrated discovery, Group Policy a multimaster replication. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Attribute-Based Access Control — ABAC

Authorization model používajúci attributes principalu, resource-u, action a environmentu na vytvorenie access decisionu. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Authentication

Proces overenia identity alebo kontroly nad authenticatorom pred vytvorením session, tokenu alebo iného authenticated contextu. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Authentication Service — Kerberos AS

Časť KDC, ktorá po počiatočnej authentication vydáva clientovi Ticket-Granting Ticket. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Authenticator

Prostriedok kontrolovaný claimantom a používaný na preukázanie identity, napríklad password, passkey, smart card, certificate alebo cryptographic device. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Authoritative identity source

Systém považovaný za zdroj pravdy pre existenciu, status, ownera alebo attributes identity, napríklad HR systém alebo service catalog. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Authorization

Rozhodnutie, či principal smie vykonať konkrétnu action voči konkrétnemu resource-u v danom context-e. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Bind — LDAP

LDAP operation, ktorá nastavuje authentication state connectionu pomocou anonymous, simple alebo SASL mechanismu. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Break-glass access

Oddelený a kontrolovaný emergency access model určený pre stav, keď bežná identity alebo privilege activation cesta nie je dostupná. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Capability-based security

Model, v ktorom držanie konkrétnej obmedzenej capability alebo reference oprávňuje principal vykonať presne definovanú operáciu bez broad ambient authority. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Claimant

Entita, ktorá sa pokúša preukázať kontrolu nad authenticatorom a byť rozpoznaná ako konkrétny subscriber alebo principal. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## ClusterRole — Kubernetes

Kubernetes RBAC objekt obsahujúci cluster-scoped alebo reusable rules, ktoré možno bindnúť cluster-wide alebo v konkrétnom namespace. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## ClusterRoleBinding — Kubernetes

Kubernetes RBAC objekt, ktorý priraďuje ClusterRole principals na úrovni celého clusteru. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Confused deputy

Security problém, pri ktorom privilegovaná služba zneužije alebo nesprávne použije svoju authority v prospech menej privilegovaného caller-a bez správneho context bindingu. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Credential

Dôkaz alebo secret naviazaný na principal, napríklad password, private key, token seed alebo certificate key material. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Credential cache — Kerberos

Client-side store obsahujúci TGT a service tickets pre aktuálnu Kerberos session. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## DC locator

AD DS proces, ktorým client pomocou DNS, site informácií a ďalších pravidiel nájde vhodný domain controller. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Delegation — identity

Kontrolované odovzdanie obmedzenej authority z jedného principalu na iný principal alebo service. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Directory Information Tree — DIT

Hierarchická štruktúra LDAP directory entries organizovaná podľa Distinguished Names. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Directory partition — AD DS

Replikovaný naming context AD DS, napríklad schema, configuration, domain alebo application partition, s vlastným replication scope-om. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Distinguished Name — DN

Jednoznačný hierarchický názov LDAP entry, napríklad `uid=alice,ou=People,dc=example,dc=com`. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Domain — AD DS

Logical AD DS partition s vlastným DNS name, domain-wide objects, replication scope a domain operations roles. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Domain controller

Server hostujúci AD DS directory partitions a poskytujúci LDAP, Kerberos KDC, authentication, replication a SYSVOL/Group Policy služby. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Domain Local group

AD DS group scope typicky používaný na priradenie permissions k resources v konkrétnej doméne. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Dynamic separation of duties

Constraint, ktorý zakazuje použiť conflictujúce roles alebo capabilities v tej istej session alebo transaction, aj keď ich principal môže mať pridelené. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Effective access

Výsledná množina permissions po vyhodnotení direct a inherited assignments, groups, roles, conditions, boundaries, resource policies a explicit denies. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Encryption type — Kerberos

Cryptographic algorithm a associated key semantics používané pre Kerberos long-term keys, tickets alebo session keys. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Entitlement

Konkrétne oprávnenie, role, group membership alebo capability, ktorú možno prideliť principalu. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Federation

Trust model, v ktorom relying party prijíma authentication assertion alebo token od samostatne spravovaného identity provider-a. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Flexible Single Master Operations — FSMO

AD DS roles určené pre operácie, ktoré nemajú byť vykonávané súčasne viacerými domain controllers. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Forest — AD DS

Najvyššia AD DS logical a významná security boundary združujúca domains so spoločnou schema, configuration a Global Catalog modelom. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Forest recovery

Koordinovaný recovery proces na obnovu dôveryhodného AD DS forest-u po rozsiahlej corruption alebo compromise udalosti. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Global Catalog

AD DS capability obsahujúca partial attribute set z objects naprieč forestom pre forest-wide search a vybrané authentication/group-resolution scenáre. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Global group — AD DS

AD DS group scope typicky obsahujúci accounts z rovnakej domény a používaný na reprezentovanie business alebo job membership. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Group Managed Service Account — gMSA

AD DS managed service identity s automatizovanou password lifecycle správou pre podporované Windows services a hosts. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## IAM

Disciplína a platformové capabilities na správu identities, credentials, authentication, authorization, federation, provisioning, privileged access, review a audit. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Identity

Reprezentácia osoby, workloadu, zariadenia alebo organizácie používaná naprieč identity a access lifecycle-om. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Identity proofing

Proces zhromažďovania a overovania evidence, ktorým sa digitálna identita spoľahlivo priraďuje reálnej osobe alebo entite. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Impersonation

Mechanizmus, pri ktorom systém alebo administrator vykonáva action ako iný principal, pričom audit má zachovať pôvodného aj impersonovaného actora. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Joiner-mover-leaver lifecycle

Identity governance proces pre vytvorenie identity, zmenu pracovnej funkcie a úplné odstránenie accessu pri odchode. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Just-enough administration

Privilege model poskytujúci iba konkrétne administratívne capabilities potrebné na úlohu namiesto full admin shellu alebo broad role. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Just-in-time access

Dočasná aktivácia privilege na obmedzený čas po splnení podmienok ako MFA, approval alebo justification. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## KDC

Kerberos Key Distribution Center obsahujúce Authentication Service, Ticket-Granting Service a principal/key database. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Kerberos

Ticket-based network authentication protocol používajúci KDC, TGT a service tickets na vzájomnú authentication clientov a services. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Keytab

Súbor obsahujúci Kerberos service-principal long-term keys, encryption types a key versions; ide o citlivý service credential. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Key version number — KVNO

Číslo verzie Kerberos long-term key-u používané na zosúladenie ticketu s aktuálnym alebo starším keytab entry. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## LDAP

Aplikačný protocol na prístup k hierarchickým directory službám cez operations ako Bind, Search, Add, Modify a Delete. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## LDAP control

Rozšírenie LDAP operation behavior, napríklad paged results alebo server-side sorting, označené ako critical alebo non-critical. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## LDAP filter

Výraz určujúci, ktoré directory entries zodpovedajú Search requestu; user input musí byť správne escaped. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## LDAP injection

Injection attack vznikajúci vložením neescaped alebo nevalidovaného inputu do LDAP filteru alebo Distinguished Name. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## LDAP referral

LDAP response odkazujúci clienta na iný directory server alebo naming context. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## LDAPS

LDAP connection chránená TLS od začiatku transportného spojenia, typicky na samostatnom porte. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## LDIF

Textový LDAP Data Interchange Format používaný na reprezentovanie entries a directory changes. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Least privilege

Princíp prideľovania iba permissions potrebných na konkrétnu úlohu, v najmenšom scope-e a na najkratší potrebný čas. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Multimaster replication — AD DS

Replication model, v ktorom môžu directory changes vzniknúť na viacerých writable domain controllers a následne convergovať cez replication metadata a topology. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Mutual authentication — Kerberos

Kerberos flow, pri ktorom client aj service cryptographically overia druhú stranu pomocou zdieľaného session contextu. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Need-to-do

Obmedzenie privilege na actions nevyhnutné pre pracovnú alebo system task. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Need-to-know

Obmedzenie prístupu k informáciám iba na principals, ktorí ich potrebujú na oprávnenú úlohu. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Object class — LDAP

Schema definícia typu LDAP entry určujúca required a allowed attributes a inheritance. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Organizational Unit — OU

AD DS container používaný na organizáciu objects, administrative delegation a aplikáciu Group Policy; nie je plnou security isolation boundary. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## PAC — Kerberos

Microsoft Privilege Attribute Certificate prenášajúci authorization-related identity a group information v Kerberos ticketoch pre Windows authorization scenarios. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Pass-the-ticket

Attack, pri ktorom útočník použije ukradnutý Kerberos TGT alebo service ticket bez znalosti pôvodného passwordu. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Permissions boundary

Guardrail určujúci maximálny permissions envelope identity bez samostatného udelenia accessu. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## PDC Emulator

Per-domain FSMO role významná pre time hierarchy, password-change preference, lockout a compatibility scenáre. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Policy Administration Point — PAP

Komponent alebo proces, ktorý vytvára, mení a publikuje authorization policies. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Policy Decision Point — PDP

Komponent vyhodnocujúci authorization request voči policies a contextu a vracajúci allow alebo deny decision. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Policy Enforcement Point — PEP

Komponent pri resource boundary, ktorý presadzuje authorization decision a povolí alebo zablokuje operation. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Policy Information Point — PIP

Zdroj trusted attributes a contextu potrebných na authorization decision. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Pre-authentication — Kerberos

Mechanizmus, ktorým client pred vydaním TGT preukazuje kontrolu nad long-term credentialom alebo iným initial authentication factorom. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Principal

Security identity používaná pri authentication alebo authorization, napríklad user, workload, service alebo device. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Privilege creep

Postupné hromadenie nepotrebných alebo zastaraných permissions počas zmien role, projektov a manuálnych grants. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Relative Distinguished Name — RDN

Časť Distinguished Name identifikujúca LDAP entry relatívne voči jeho parent entry. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Role — Kubernetes

Namespaced Kubernetes RBAC objekt obsahujúci additive allow rules pre resources v konkrétnom namespace. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Role engineering

Disciplína navrhovania roles z pracovných tasks, required permissions, resource scopes, constraints, ownershipu a usage evidence. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Role explosion

Nekontrolovaný rast počtu roles pri modelovaní každej kombinácie tímu, prostredia, aplikácie, resource scope-u a privilege levelu. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Role-Based Access Control — RBAC

Authorization model, ktorý združuje permissions do roles a tieto roles priraďuje principals v konkrétnom scope-e. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## RoleBinding — Kubernetes

Kubernetes RBAC objekt, ktorý priraďuje Role alebo ClusterRole principals v konkrétnom namespace. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## SASL — LDAP

Simple Authentication and Security Layer framework používaný LDAP na podporu rôznych authentication mechanisms nad rámec simple bindu. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Search base — LDAP

Distinguished Name určujúci východiskový entry pre LDAP Search operation. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Search scope — LDAP

Rozsah LDAP Search operation: base object, one level alebo subtree. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Separation of duties

Rozdelenie conflictujúcich alebo kritických actions medzi viac nezávislých principals, aby jeden actor nemohol celý citlivý workflow vykonať a zakryť. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Service principal name — SPN

Kerberos identity služby viazaná na service class a hostname, ktorú client používa pri žiadosti o service ticket. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Service ticket — Kerberos

Časovo obmedzený ticket vydaný KDC pre konkrétny service principal a šifrovaný long-term key-om služby. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Session

Dočasný authenticated context vytvorený po úspešnej authentication a používaný na ďalšie authorization decisions. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Simple Bind — LDAP

LDAP Bind mechanism používajúci identity a password; musí byť chránený TLS, pretože sám neposkytuje transport encryption. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Standing privilege

Permission alebo role, ktorá je principalu aktívne pridelená nepretržite bez samostatnej time-bound activation. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## StartTLS — LDAP

LDAP extended operation, ktorá upgraduje existujúcu plaintext LDAP connection na TLS-protected connection. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Static separation of duties

Constraint zakazujúci prideliť jednému principalu konfliktujúce roles alebo entitlements súčasne. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Subject

Entita, ktorá iniciuje operation alebo pristupuje k resource-u a je reprezentovaná principalom v security context-e. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## SYSVOL

AD DS replicated share obsahujúci Group Policy template data a domain logon scripts. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Ticket-Granting Service — Kerberos TGS

Časť KDC, ktorá na základe validného TGT vydáva service tickets pre požadované service principals. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Ticket-Granting Ticket — TGT

Kerberos ticket používaný clientom na získavanie service tickets bez opakovaného zadávania passwordu. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Universal group — AD DS

AD DS group scope, ktorý môže obsahovať principals z viacerých domains vo forest-e a je replikovaný cez Global Catalog podľa platform semantics. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).
