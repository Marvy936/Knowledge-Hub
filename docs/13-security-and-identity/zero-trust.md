# Zero Trust

Zero Trust je súbor security princípov a architecture patterns pre riadenie prístupu k enterprise resources. Odstraňuje predstavu, že používateľ, zariadenie alebo workload je dôveryhodný iba preto, že sa nachádza vo firemnej sieti, vo VPN, vo VPC alebo v Kubernetes clusteri. Každý prístup sa posudzuje voči konkrétnemu resource-u a action na základe identity, aktuálneho stavu zariadenia alebo workloadu, citlivosti resource-u, kontextu a policy.

Zero Trust nie je jeden produkt ani samostatný protokol. Je to spôsob, ako poskladať identity, authorization, network controls, telemetry a recovery tak, aby kompromitovanie jedného účtu, endpointu alebo interného service-u automaticky neotvorilo široký trust path do zvyšku prostredia.

```text
subject alebo workload
→ žiada konkrétnu action na konkrétnom resource-e
→ policy engine získa identity, posture a contextual signals
→ vyhodnotí policy a risk
→ enforcement point povolí, obmedzí alebo odmietne prístup
→ session zostáva časovo ohraničená a môže byť znovu vyhodnotená
```

## 1. Prečo Zero Trust vznikol

Klasický perimeter model predpokladal, že hlavná security boundary je hranica podnikovej siete. Používateľ sa pripojil do LAN alebo VPN a následne mal často širokú konektivitu k mnohým interným systems. Tento model bol praktický v prostredí s centralizovanými datacentrami, managed workstations a malým počtom remote users, ale slabne pri SaaS, multi-cloud, hybrid work, partner access a microservices.

Problém nie je v tom, že network segmentation prestala byť užitočná. Problém je, že network location sama nedokazuje, kto request vytvoril, v akom stave je jeho zariadenie, v mene koho service koná ani či má žiadateľ právo vykonať konkrétnu business action. Compromised laptop pripojený cez VPN je stále compromised laptop. Malicious process v internom Pod-e je stále malicious process.

Zero Trust preto presúva primárnu otázku z „je requester v správnej sieti?“ na „má tento overený principal právo vykonať túto action na tomto resource-e za aktuálnych podmienok?“ NIST SP 800-207 tento posun opisuje ako ochranu resources namiesto samotných network segments.

## 2. Čo Zero Trust nie je

Zero Trust neznamená, že systém „nikomu neverí“ v ľudskom zmysle. Bez určitej dôvery nemožno overovať certificates, identity providers, device-management platformy ani policy data. Cieľom je implicitnú a neobmedzenú dôveru nahradiť explicitnou, overiteľnou a ohraničenou dôverou.

Zero Trust preto nie je:

- samotné MFA — MFA zvyšuje istotu o human identity, ale neurčuje všetky resource permissions;
- samotná VPN alebo ZTNA proxy — remote access je iba jeden access path;
- samotný service mesh — mesh môže poskytnúť workload identity a mTLS, ale nevyrieši všetku application authorization;
- samotná microsegmentation — obmedzuje network paths, ale nemusí rozumieť user delegation alebo data scope;
- odstránenie firewallov — network controls zostávajú vrstvou defense in depth;
- jeden „trust score“ — niektoré podmienky musia zostať hard requirements, nie priemerované číslo;
- jednorazový migration project — identity, resources, policies a attack paths sa priebežne menia.

Produkt môže implementovať jednu alebo viac Zero Trust capabilities, ale architektúra vzniká až prepojením identity lifecycle-u, resource inventory, policy decisionov, enforcementu, telemetry a recovery.

## 3. Resource-centric mentálny model

Resource je konkrétna vec, ktorú organizácia chráni: application, API operation, database, data object, administrative interface, queue, secret, workflow alebo device capability. Resource-centric security znamená, že policy sa viaže na tento chránený objekt a nie iba na sieťový segment, v ktorom sa nachádza.

Predstavme si internú fakturačnú aplikáciu. Perimeter model môže po pripojení do VPN sprístupniť celý subnet. Resource-centric model povoľuje účtovníkovi čítať invoices, senior účtovníkovi schváliť refund do definovaného limitu a platform engineerovi spravovať deployment bez prístupu k finančným údajom. Všetci môžu používať tú istú network path, ale policy odlišuje action, resource a data scope.

Network segmentation zostáva dôležitá, pretože znižuje počet možných paths a blast radius. Nie je však dostatočným authorization dôkazom. Source IP môže byť contextual signal, ale nie stabilná human alebo workload identity.

## 4. Access request ako explicitný decision

Užitočný authorization model je:

```text
principal + action + resource + context → decision
```

**Principal** je overený actor, napríklad user, service account alebo workload identity. **Action** je požadovaná operácia, napríklad `read`, `approve`, `deploy` alebo `decrypt`. **Resource** je presný cieľ operácie. **Context** obsahuje podmienky, ktoré ovplyvňujú decision: environment, čas, authentication strength, device posture, tenant, delegation chain alebo active incident state.

Decision nemá byť iba boolean `allow/deny`. Systém môže povoliť prístup s obmedzeniami, napríklad iba read-only, bez downloadu, s kratšou session alebo po step-up authentication. Takýto structured decision musí enforcement point vedieť reálne presadiť; policy obligation bez implementovaného enforcementu je iba deklarácia.

## 5. Least privilege per resource

Least privilege v Zero Trust znamená obmedziť prístup vo viacerých dimenziách súčasne. Nestačí priradiť používateľa do broad group a považovať problém za vyriešený.

- **Subject identity** určuje, kto alebo čo request vytvára. Stabilná identity je základ auditu a revocation.
- **Action** určuje konkrétnu operáciu. Čítanie, zmena, schválenie a administrácia majú rozdielny impact.
- **Exact resource** zabraňuje tomu, aby permission pre jednu aplikáciu automaticky platila na celý subnet alebo account.
- **Data scope** obmedzuje tenant, rows, columns, projekty alebo klasifikáciu údajov.
- **Environment** oddeľuje development, staging a production, pretože rovnaká action má iný risk.
- **Time** umožňuje expiring access, maintenance window alebo just-in-time privilege.
- **Device alebo workload state** viaže access na aktuálny bezpečnostný stav execution environmentu.
- **Delegation context** rozlišuje, či service koná vo vlastnom mene alebo v mene konkrétneho usera.

Praktický príklad: deployment service môže mať permission nasadiť konkrétny signed artifact do stagingu automaticky. Production deployment môže vyžadovať approved release identity, krátkodobý workload token, protected environment a explicitný change window. Obe operácie sú „deploy“, ale ich resource, environment a assurance requirements sú odlišné.

Broad network access po successful login je opakom tohto modelu, pretože jeden authentication event sa nepriamo mení na množstvo nešpecifikovaných permissions.

## 6. Dynamic policy a význam jednotlivých signálov

Static group membership zostáva užitočným inputom, ale sama nedokáže zachytiť aktuálny risk. Dynamic policy kombinuje dlhodobejšie identity attributes s časovo premenlivými signals o requeste, zariadení, workload-e a resource-e.

**Authentication strength** opisuje, akým spôsobom bol principal overený. Password-only session má nižšiu assurance než phishing-resistant WebAuthn authentication. **Device compliance** opisuje, či managed endpoint spĺňa pravidlá ako patch level, disk encryption alebo EDR health. **Resource sensitivity** označuje dopad kompromitovania resource-u a určuje, aká assurance je potrebná.

**Workload attestation** je proces, pri ktorom platforma pred vydaním workload credentialu overí, že request pochádza od očakávaného procesu alebo Pod-u v schválenom execution context-e. Nejde iba o kontrolu mena service-u. Verifier porovnáva dôkazy ako Kubernetes namespace a ServiceAccount, process UID, container metadata, node identity alebo cloud instance document s registration policy. Workload attestation je podrobne rozobratá v samostatnej sekcii nižšie.

**User risk** a **behavior anomalies** sú signals o možnom compromise účtu, napríklad impossible travel, nezvyčajný authenticator reset alebo náhle privileged actions. **Vulnerability state** informuje, či endpoint alebo workload obsahuje relevantnú známu vulnerability. **Active incident status** môže dočasne sprísniť policy pre zasiahnutý tenant, identity domain alebo service.

Každý signal potrebuje tri vlastnosti:

1. **Trusted source** — policy engine musí vedieť, kto hodnotu vydal a či ju requester nemôže svojvoľne spoofnúť.
2. **Freshness** — staré posture alebo risk data nesmú byť bez obmedzenia považované za aktuálne.
3. **Failure semantics** — pri nedostupnom zdroji musí byť explicitné, či sa access odmietne, obmedzí alebo použije krátkodobý cached decision.

Napríklad nedostupný EDR backend nemá automaticky znamenať „device compliant“. Pre production administration môže policy fail-closed, zatiaľ čo low-risk read-only dashboard môže použiť krátky cached posture result.

## 7. Authentication a authorization sú samostatné

Authentication odpovedá na otázku „kto alebo čo žiada?“. Authorization odpovedá na otázku „smie tento principal vykonať požadovanú action na konkrétnom resource-e v aktuálnom context-e?“ Úspešná authentication je vstup do authorization decisionu, nie všeobecné povolenie.

```text
authentication
→ overí identity a authentication context

authorization
→ vyhodnotí principal, action, resource a context
```

Používateľ môže úspešne vykonať MFA a napriek tomu dostať `403 Forbidden`, pretože nemá permission na daný resource. Naopak, zle navrhnutá application môže overiť platný token, ale nevalidovať audience, tenant alebo object ownership, čím vznikne authorization bypass.

Zero Trust preto vyžaduje, aby authentication evidence bolo prenesené do správneho resource-level decisionu a aby application alebo proxy neodvodzovala broad access iba z existencie session.

## 8. Session nie je permanentná dôvera

Session je časovo ohraničený výsledok predchádzajúceho decisionu. Po jej vytvorení sa však môže zmeniť account status, device posture, resource classification, credential validity alebo incident state. Dlhá session bez re-evaluation vytvára interval, počas ktorého systém pokračuje v dôvere k už neplatným podmienkam.

**Continuous verification** neznamená plnú re-authentication pri každom network packet-e. Znamená kombináciu primeraných session lifetimes, opätovného vyhodnotenia pri významných events, telemetry počas session a funkčného revocation pathu.

Príklad: používateľ otvorí privileged administration session na compliant device. EDR neskôr označí endpoint ako compromised. Identity alebo posture event má spôsobiť revocation existujúcej session alebo aspoň zablokovať ďalšie privileged operations. Ak systém kontroluje posture iba pri rannom login-e a session platí celý deň, „dynamic policy“ existuje iba na papieri.

Cadence re-evaluation musí zodpovedať risku a performance. High-value administration potrebuje kratší interval a event-driven revocation než verejný read-only content.

## 9. NIST logical components: PE, PA a PEP

NIST SP 800-207 rozdeľuje access control flow na tri logické roly. Logická rola neznamená nutne samostatný produkt; jeden produkt môže implementovať viac rolí a jedna rola môže byť distribuovaná medzi viac systems.

**Policy Engine (PE)** vyhodnocuje policy a rozhoduje, či má byť access povolený, odmietnutý alebo obmedzený. Potrebuje identity data, resource attributes, posture, threat alebo risk signals a policy revision.

**Policy Administrator (PA)** vykoná control-plane kroky potrebné na realizáciu decisionu. Môže vydať session credential, nakonfigurovať proxy, vytvoriť communication path alebo ukončiť existujúcu session. NIST Policy Administrator nie je to isté ako Policy Administration Point z kapitoly [Policy as Code](policy-as-code.md); podobný názov označuje inú architektonickú rolu.

**Policy Enforcement Point (PEP)** stojí na prístupovej ceste medzi principalom a resource-om a reálne presadí výsledok. Môže ním byť identity-aware proxy, API gateway, application middleware, database proxy, host agent alebo service-mesh proxy.

```text
Policy Engine vyhodnotí request
→ Policy Administrator pripraví alebo ukončí access path
→ Policy Enforcement Point presadí decision na trafficu alebo operácii
```

Ak je PEP umiestnený iba pred jedným hostname, ale backend zostáva dostupný priamo cez internú IP, vzniká bypass path. Zero Trust preto potrebuje nielen správnu policy, ale aj topology, v ktorej všetky relevantné paths prechádzajú enforcementom.

## 10. Control plane a data plane

Control plane spravuje identity, policy, posture data, decisions a konfiguráciu sessions alebo enforcement points. Data plane prenáša actual application traffic po tom, čo bol access povolený.

Compromise control plane-u má často väčší blast radius než compromise jedného data-plane workloadu. Attacker s právom meniť policy, issuer trust alebo PEP configuration môže otvoriť prístup k mnohým resources naraz. Preto policy repositories, identity providers, certificate authorities, device-management systems a deployment pipelines patria medzi kritické security dependencies.

Data-plane encryption alebo segmentation neochráni pred malicious policy revision. Naopak, silný control plane nepomôže, ak resource možno osloviť mimo PEP. Návrh musí chrániť obe vrstvy a priebežne overovať, že enforcement configuration zodpovedá intended policy revision.

## 11. Human identity lifecycle

Zero Trust stojí na dôveryhodnej identity, ale identity nie je iba username. Potrebuje authoritative source, enrollment, authenticator issuance, role alebo attribute governance, session management, recovery a revocation.

Slabý joiner-mover-leaver proces vytvára stale accounts a privilege creep. Zero Trust policy potom iba automatizuje chybný identity dataset. Podobne silná runtime MFA nevyrieši compromised recovery flow, pri ktorom helpdesk bez dostatočného identity proofingu resetuje authenticator útočníkovi.

Human identity návrh má preto odpovedať:

- kto smie vytvoriť alebo meniť account;
- ako sa overí väzba accountu na reálnu osobu;
- ako sa vydáva phishing-resistant authenticator;
- ako sa mení role pri zmene pracovnej pozície;
- ako rýchlo sa ukončia sessions po offboardingu alebo incidente;
- ako sa auditujú delegated a break-glass operations.

Podrobnejšie lifecycle a authorization modely sú v kapitolách [Authentication, authorization a auditing](authentication-authorization-auditing.md), [Least privilege](least-privilege.md) a [IAM a RBAC](iam-rbac.md).

## 12. Authentication strength a step-up authentication

Authentication strength vyjadruje assurance, ktorú poskytuje konkrétna authentication metóda a context. Phishing-resistant FIDO2/WebAuthn authenticator je viazaný na legitímny origin a používa cryptographic proof. Password, SMS alebo jednoduchý push approval má odlišné attack paths.

**Step-up authentication** znamená, že používateľ s existujúcou session vykoná silnejšie alebo čerstvejšie overenie pred citlivejšou action. Bežná session môže stačiť na čítanie interného dashboardu, ale production change alebo export regulated data môže vyžadovať čerstvé phishing-resistant MFA.

Step-up nie je náhrada authorization. Po silnejšom overení musí policy stále skontrolovať resource permission, tenant, device posture a action. Systém má tiež zabrániť tomu, aby step-up token určený pre jednu application alebo action bol opätovne použitý inde.

## 13. Device identity a device posture

**Device identity** dokazuje, o ktoré zariadenie ide. Môže byť založená na managed certificate, hardware-backed key, TPM evidence, MDM enrollment alebo cloud instance identity. Stabilná device identity umožňuje viazať audit a policy na konkrétny endpoint.

**Device posture** opisuje aktuálny security state zariadenia. Typické signals sú OS a patch level, disk encryption, secure boot, EDR health, local firewall, root alebo jailbreak state a certificate status.

Tieto pojmy sa nesmú zamieňať. Stolen managed laptop môže stále prezentovať platný device certificate, ale jeho posture alebo user context môže byť kompromitovaný. Naopak, zariadenie môže vyzerať patchované, ale bez dôveryhodnej device identity nie je jasné, ku ktorému assetu posture report patrí.

Posture collector musí chrániť signal pred spoofingom a uvádzať čas merania. Policy má explicitne riešiť nedostupný agent, oneskorené data a conflict medzi viacerými sources.

## 14. Managed a unmanaged devices

Unmanaged device nemusí byť vždy úplne zablokovaný. Rozhodnutie závisí od citlivosti resource-u a dostupných compensating controls.

Napríklad osobné zariadenie môže dostať browser-isolated read-only access k low-sensitivity application bez možnosti downloadu. Production console alebo regulated dataset môže vyžadovať managed endpoint, hardware-backed device identity a healthy EDR.

Tento model je bezpečnejší než univerzálny allow alebo deny, pretože explicitne spája resource classification s povolenými actions. Dôležité je, aby „restricted mode“ presadzovala application, proxy alebo isolated workspace; samotný policy result bez technického enforcementu nezabráni copy alebo downloadu.

## 15. Workload identity

Workload je running software vykonávajúci určitú funkciu, napríklad API service, queue worker alebo database process. Workload identity je overiteľná identity tohto software execution contextu. Nemala by byť odvodená iba z IP adresy, pretože IP je recyklovateľná, môže sa meniť pri reschedulingu a často identifikuje network interface namiesto konkrétneho processu.

Workload identity môže mať formu short-lived mTLS certificate, signed JWT assertion, cloud workload identity alebo audience-bound Kubernetes ServiceAccount tokenu. Dôležitá je väzba medzi credentialom a skutočným workloadom, krátky lifecycle a možnosť revocation alebo replacementu.

Shared static service password je slabý model, pretože viaceré instances používajú rovnaký credential, attribution je nepresná a rotation zasiahne všetkých consumers naraz. Short-lived per-workload credentials zmenšujú blast radius, ale vyžadujú spoľahlivú issuance a renewal dependency.

## 16. Workload attestation podrobne

Workload attestation odpovedá na otázku: „Je proces žiadajúci identity skutočne workload, ktorému má byť táto identity vydaná?“ Je to issuance-time verification, nie iba neskoršia kontrola certificate-u.

Typický flow vyzerá takto:

```text
workload process požiada local identity agent o credential
→ agent identifikuje volajúci process
→ získa selectors z OS, orchestratora alebo platformy
→ porovná selectors s registration policy
→ vydá alebo vráti credential patriaci zodpovedajúcej workload identity
```

**Selectors** sú overiteľné vlastnosti workloadu alebo jeho execution contextu. V Kubernetes to môže byť namespace, ServiceAccount, Pod UID alebo node identity. Na Linux hoste môže ísť o process UID, executable path alebo cgroup. Cloud platforma môže poskytnúť signed instance identity document.

Node attestation a workload attestation riešia rozdielne hranice. **Node attestation** overuje host alebo agent, na ktorom workload beží. **Workload attestation** identifikuje konkrétny process alebo Pod na tomto node. Ak je node plne compromised, lokálny agent alebo kernel evidence môže byť nedôveryhodné; návrh preto musí definovať, akú úroveň node compromise dokáže attestation model tolerovať a kedy je potrebný hardware-backed alebo measured-boot dôkaz.

Príklad: SPIRE Agent na Kubernetes node zistí, že caller beží v namespace `payments` pod ServiceAccountom `settlement-api`. Registration entry mapuje túto kombináciu na SPIFFE ID `spiffe://prod.example/payments/settlement-api`. Agent vydá zodpovedajúci short-lived SVID. Pod v inom namespace alebo s iným ServiceAccountom túto identity nedostane, aj keď pozná jej názov.

## 17. SPIFFE, SVID a SPIRE

SPIFFE definuje platform-neutral model workload identity. **SPIFFE ID** je štruktúrovaný identifikátor workloadu, napríklad `spiffe://prod.example/payments/settlement-api`. Prvá časť identifikuje trust domain a path identifikuje workload v rámci tejto boundary.

**SVID — SPIFFE Verifiable Identity Document** je cryptographically verifiable dokument, ktorým workload preukazuje SPIFFE ID. Môže mať formu X.509-SVID pre mTLS alebo JWT-SVID pre token-based flow. SVID obsahuje alebo je viazaný na cryptographic key a má obmedzenú validity.

**Workload API** je lokálne rozhranie, cez ktoré workload získava svoje SVIDs a trust bundles bez toho, aby mal v image statický bootstrap secret. Application alebo proxy môže API používať priamo; sidecar alebo node agent môže credentials prekladať do mTLS.

SPIRE je production implementation SPIFFE APIs. SPIRE Server spravuje registration entries a signing authority. SPIRE Agent beží na nodes, vykonáva workload attestation a poskytuje Workload API lokálnym processes. SPIRE teda nie je synonymum SPIFFE: SPIFFE je specification a identity model, SPIRE je jedna implementácia.

## 18. Trust domains a federation

Trust domain je administrative a cryptographic boundary, v ktorej sú SPIFFE identities vydávané a overované podľa spoločných trust roots a governance. Nie je to iba DNS-like string.

Production a development často patria do odlišných trust domains, pretože majú rozdielne administrators, issuance controls a compromise impact. Ak by development issuer mohol vydávať production identities, compromise dev prostredia by sa preniesol do production authorization.

Federation umožňuje workloads z rôznych trust domains navzájom overovať SVIDs. Vyžaduje výmenu trust bundles, explicitné identity mapping rules a authorization policy. Federated authentication neznamená automaticky federated authorization: service z partnerského trust domainu môže byť cryptographically overený, ale stále potrebuje konkrétne permissions.

Key rotation, bundle distribution, revocation latency a tenant isolation sú súčasťou federation lifecycle-u. Stale trust bundle môže spôsobiť outage po rotation alebo predĺžiť dôveru k compromised issueru.

## 19. mTLS autentizuje endpoints, nie business intent

Mutual TLS poskytuje encrypted channel a vzájomnú certificate-based authentication endpoints. Client aj server prezentujú certificates a overia ich voči trust roots.

mTLS však samo neurčuje, ktorú business action smie service vykonať, pre ktorého tenant-a koná ani či request nesie platnú user delegation. Certificate `settlement-api` dokazuje service identity, nie automatické právo refundovať ľubovoľnú platbu.

Application alebo proxy policy musí mapovať workload identity na resource-level permissions. Pri sensitive operations môže navyše kontrolovať user subject, transaction amount, tenant a request integrity. Service mesh, ktorý zapne mTLS pre celý cluster, preto ešte nevytvára kompletnú Zero Trust architecture.

## 20. User-to-service delegation

Pri downstream call-e treba rozlíšiť tri situácie:

1. service koná vo vlastnom mene, napríklad maintenance worker číta vlastnú queue;
2. service koná v mene usera, napríklad API číta invoice, ktorú user otvoril;
3. service dostane obmedzenú delegated authority na konkrétnu downstream action.

Propagovanie rovnakého broad bearer tokenu cez celý service chain zväčšuje blast radius. Každý compromised downstream service môže token ukradnúť a použiť na iné audiences alebo resources, ak nie je správne obmedzený.

Bezpečnejší model používa audience restriction, token exchange alebo explicitný delegation context. Downstream service overí workload identity volajúceho aj delegated user identity a aplikuje vlastnú authorization policy. Audit má zachytiť oboch actors: initiating usera aj service, ktorá operation vykonala.

## 21. Resource inventory a data classification

Zero Trust nemôže chrániť resource, o ktorom organizácia nevie. Inventory má obsahovať applications, APIs, data stores, administrative interfaces, workloads, SaaS services, owners, dependencies, sensitivity a všetky access paths.

Data classification určuje požadovanú assurance. Verejné dáta môžu tolerovať anonymous access. Interné dáta môžu vyžadovať enterprise identity. Regulated alebo highly restricted data môžu vyžadovať managed device, stronger authentication, no-download policy, approval a detailný audit.

Classification musí ovplyvniť technické controls. Label `confidential` bez väzby na authorization, encryption, retention alebo export policy je iba metadata. Rovnako inventory bez topology a ownera nepomôže zistiť, či backend zostáva dostupný mimo PEP.

## 22. Data-centric controls

Connection allow/deny je iba začiatok. Application môže potrebovať row-level alebo column-level authorization, tenant isolation, field masking, tokenization alebo approval pre export.

Napríklad support engineer môže mať access k customer accountu, ale citlivé payment fields zostanú masked. Incident responder môže dostať dočasný read-only access k širšiemu datasetu s auditovaným case ID. Takéto controls patria bližšie k data a application semantics než network firewall.

Data-centric policy tiež musí riešiť derived data, exports a caches. Ak application správne chráni database query, ale exportovaný CSV súbor sa uloží do broad shared bucketu, resource-level boundary bola obídená v ďalšom lifecycle kroku.

## 23. Segmentation a microsegmentation

Segmentation rozdeľuje network alebo workload environment na menšie communication zones. **Microsegmentation** používa jemnejšie policies medzi workloads, applications alebo tiers, aby obmedzila lateral movement.

Zero Trust microsegmentation nemá byť iba veľké množstvo statických IP rules. Stabilnejší model viaže policy na workload identity, namespace, service alebo application role a kombinuje network-tier a identity-tier controls.

Príklad: frontend môže volať iba public API operation backendu; backend môže pristupovať iba k svojej database; build runner nemá network path k production database. Ak attacker kompromituje frontend, segmentation obmedzí reachable targets, zatiaľ čo application authorization obmedzí povolené operations.

Microsegmentation môže zlyhať pri neúplnom traffic inventory, broad fallback rules alebo policy drift-e. Pred enforcementom je užitočný observe alebo audit mode, ale migration musí mať deadline; permanentný non-enforcing mode nevytvára protection.

## 24. ZTNA, VPN, SSE a SASE

**Zero Trust Network Access — ZTNA** je access pattern, pri ktorom broker alebo proxy poskytne authenticated a policy-controlled access ku konkrétnym applications namiesto broad network connectivity. Resource môže zostať skrytý pred priamym routovaním a session sa vytvorí až po decisione.

VPN vytvára encrypted network tunnel, ale jej authorization granularity závisí od konkrétnej implementácie. VPN a ZTNA môžu počas migrácie coexistovať. Dôležité je, aby VPN nezostala paralelným broad bypass pathom k resources, ktoré majú byť chránené resource-level policy.

**Security Service Edge — SSE** spája cloud-delivered security capabilities ako ZTNA, secure web gateway a cloud access security broker. **Secure Access Service Edge — SASE** rozširuje tento model o networking capabilities, napríklad SD-WAN. Ide o architecture alebo service-delivery categories, nie automatický dôkaz Zero Trust maturity.

## 25. API gateways a service mesh

API gateway môže fungovať ako PEP pre north-south API traffic. Overuje tokens, aplikuje rate limits, request policy a routing. Musí však zabrániť direct backend accessu a správne propagovať identity alebo delegation context.

Service mesh môže poskytovať workload identity, mTLS, traffic policy a telemetry pre east-west communication. Sidecar alebo ambient proxy vidí network calls, ale nemusí poznať všetky business semantics. Application-level authorization zostáva potrebná pre tenant, object ownership alebo transaction rules.

NIST SP 800-207A zdôrazňuje identity-tier a network-tier policies v cloud-native multi-cloud applications. Praktický návrh preto kombinuje gateway, workload identity infrastructure, proxies a application authorization namiesto predpokladu, že jedna vrstva vyrieši všetky threats.

## 26. Cloud a Kubernetes kontext

Cloud resources majú vlastné control planes, IAM policies, network policies a workload identity mechanisms. Zero Trust návrh musí rozlišovať human administration, workload-to-workload access a access k managed data services.

V Kubernetes môže ServiceAccount token identifikovať workload, RBAC chráni Kubernetes API, NetworkPolicy obmedzuje L3/L4 traffic a admission policy kontroluje resource creation. Tieto controls riešia rôzne boundaries. Kubernetes RBAC napríklad neurčuje automaticky, ktoré rows smie application user čítať v database.

Pod identity musí byť viazaná na správny namespace, ServiceAccount a audience. Broad node role alebo shared secret mountovaný do mnohých Pods znižuje granularitu. Direct access k cloud metadata alebo node credentials môže obísť workload identity model, preto je potrebné chrániť node a metadata paths.

## 27. Privileged administration

Administratívny access má vyšší impact než bežný application access a potrebuje oddelené identity, just-in-time privilege, short-lived sessions a detailný audit.

Privileged Access Workstation alebo managed admin environment znižuje riziko, že production credentials budú použité na bežnom browsing endpoint-e. Step-up authentication, approval a session recording môžu byť primerané pre kritické systems.

Break-glass path musí existovať pre outage identity alebo policy plane-u, ale nesmie byť skrytým permanentným bypassom. Credential alebo account má byť oddelene chránený, použitie alertované, časovo obmedzené a po incidente reviewed a rotated.

## 28. Legacy systems, SaaS, IoT a OT

Nie všetky resources podporujú moderné protocols alebo agents. Legacy application môže používať header-based identity, static service account alebo broad network trust. Migrácia preto často používa compensating PEP, napríklad reverse proxy, privileged access gateway alebo isolated virtual desktop.

SaaS policy závisí od identity federation, session controls, application roles, API tokens a provider audit capabilities. Organizácia musí poznať provider-side limitations a offboarding semantics.

IoT a OT devices môžu mať obmedzený compute, dlhý lifecycle alebo safety constraints. Agresívne re-authentication alebo blocking policy môže narušiť physical process. Zero Trust princípy sa stále dajú aplikovať cez device identity, allowlisted communication paths, gateways, monitoring a segmentation, ale failure policy musí rešpektovať safety a availability requirements.

## 29. Telemetry, risk a vysvetliteľné decisions

Policy engine potrebuje telemetry, ale viac signals automaticky neznamená lepší decision. Každý signal má provenance, freshness, confidence a cost.

Jedno agregované trust score môže zakryť hard requirements. High score nemá kompenzovať chýbajúcu phishing-resistant authentication pre critical action. Vhodnejší model kombinuje explicitné mandatory conditions s vysvetliteľnými risk signals.

Decision log má zachytiť principal, action, resource, result, policy revision, relevantný context a correlation ID. Sensitive raw signals nemusia byť uložené celé, ale audit musí umožniť vysvetliť, prečo bol access povolený alebo odmietnutý.

Telemetry platforma sama je security dependency. Ak attacker môže meniť posture alebo risk data, môže ovplyvniť authorization decisions. Preto potrebuje integrity, least privilege a monitoring rovnako ako identity provider.

## 30. Degraded modes a outage dependencies

Zero Trust pridáva dependencies na identity provider, posture service, policy engine, certificate issuance a enforcement platform. Ich outage nesmie byť riešený implicitným „allow all“.

**Fail-closed** odmietne access, keď decision nemožno bezpečne urobiť. Je vhodný pre privileged alebo high-impact operations, ale môže znížiť availability. **Fail-open** pokračuje bez určitého controlu a zvyšuje security risk. Medzi nimi existuje **degraded access mode**, napríklad povolenie existujúcich low-risk sessions, read-only operations alebo krátkeho cached decisionu.

Príklad outage policy:

```text
IdP nedostupný
→ nové privileged sessions odmietnuté
→ existujúce krátkodobé sessions platia do expiration
→ low-risk read-only access môže použiť cached policy
→ break-glass je dostupný iba cez oddelený auditovaný proces
```

Degraded mode musí byť navrhnutý, testovaný a časovo ohraničený. Emergency fallback, ktorý sa nikdy netestuje, pravdepodobne zlyhá práve počas incidentu.

## 31. Incident response a recovery dôvery

Pri compromise identity, device, workload alebo policy plane-u nestačí zablokovať jednu IP adresu. Response musí identifikovať všetky odvodené sessions, tokens, credentials a trust relationships.

Typický postup:

```text
identifikovať compromised identity alebo control plane
→ zablokovať nové issuance a decisions
→ revoke alebo skrátiť existujúce sessions
→ rotovať keys, certificates alebo trust bundles podľa boundary
→ izolovať zasiahnuté workloads alebo devices
→ overiť policy a enforcement configuration
→ obnoviť z dôveryhodného source
→ potvrdiť, že staré credentials a bypass paths už nefungujú
```

Po compromise identity providera môže byť potrebné obnoviť signing keys, revalidate sessions a preskúmať malicious account changes. Po compromise SPIRE Servera alebo certificate authority sa incident dotýka workload identities v celom trust domain-e. Po compromise PEP treba overiť, či traffic neprechádzal bez auditu alebo policy.

Recovery nie je dokončená, kým systém neobnoví dôveryhodný chain od authoritative identity sources po enforcement a nepreukáže invaliditu starých trust artifacts.

## 32. Migračný model

Zero Trust migration nemá začínať nákupom produktu. Začína inventory, data classification, identity hygiene a mapovaním access paths.

Praktické poradie:

1. identifikovať kritické resources, owners a users;
2. zmapovať všetky priame aj nepriame access paths;
3. odstrániť stale identities a broad standing privilege;
4. zaviesť silnú human a workload identity;
5. umiestniť PEP tak, aby neexistoval direct bypass;
6. začať audit alebo observe mode a porovnať intended a actual access;
7. zavádzať enforcement po resource cohorts;
8. merať denied legitimate traffic, bypass paths a revocation latency;
9. odstrániť staré VPN, network alebo shared-secret paths až po overení nového modelu.

Najväčším rizikom migrácie je paralelný slabý path. Ak nová identity-aware proxy chráni application hostname, ale starý backend port zostáva dostupný z VPN, útočník použije jednoduchšiu cestu.

## 33. CISA Zero Trust Maturity Model

CISA Zero Trust Maturity Model Version 2.0 používa päť pillars:

- Identity;
- Devices;
- Networks;
- Applications and Workloads;
- Data.

Tieto pillars opisujú hlavné control areas, nie izolované projekty. Identity decision závisí od device posture; application access závisí od data classification; network enforcement potrebuje workload inventory.

Model zároveň používa tri cross-cutting capabilities: **Visibility and Analytics**, **Automation and Orchestration** a **Governance**. Visibility poskytuje evidence, automation prepája events s response actions a governance určuje ownership, policy a risk acceptance.

Maturity model je planning tool, nie certification. Organizácia môže byť silná v jednom pillar-e a slabá v inom. Cieľom je identifikovať gaps a dependencies, nie dosiahnuť jedno marketingové číslo.

## 34. Ako merať reálny pokrok

Počet nasadených agents alebo kúpených products nie je spoľahlivá maturity metrika. Užitočnejšie metrics merajú coverage a failure behavior.

- **Resource enforcement coverage** — podiel kritických resources, ktorých všetky známe paths prechádzajú PEP.
- **Identity coverage** — podiel human a workload accessu používajúceho spravované, krátkodobé a attributable identities.
- **Standing privilege** — množstvo permanentných broad permissions oproti just-in-time accessu.
- **Revocation latency** — čas od disable alebo incident signal-u po neplatnosť sessions a credentials.
- **Policy freshness** — čas medzi approved policy revision a jej enforcementom vo všetkých PEPs.
- **Bypass findings** — počet priamych paths obchádzajúcich intended enforcement.
- **Decision explainability** — podiel decisions, pri ktorých možno spätne identifikovať policy revision a relevantné inputs.

Metric musí mať denominator a scope. „90 % applications používa SSO“ nehovorí, či production administration, service accounts alebo direct database access zostali mimo kontroly.

## 35. Kompletný príklad access decisionu

Predstavme si developera, ktorý chce vykonať production deployment.

1. Developer sa autentizuje cez enterprise OIDC provider pomocou WebAuthn. ID Token alebo session nesie informáciu o authentication method a čase overenia.
2. Identity-aware access proxy overí user identity a device certificate. Posture service potvrdí aktuálny patch level, disk encryption a healthy EDR.
3. Deployment portal skontroluje, že user má oprávnenie požiadať o deployment, ale nevydá mu permanentné cloud credentials.
4. Approved workflow spustí CI workload. Workload identity platform vykoná attestation runnera a vydá short-lived credential viazaný na repository, workflow a production environment.
5. Policy engine overí signed artifact digest, approval, change window, environment a error-budget policy.
6. Deployment PEP povolí iba nasadenie konkrétneho digestu do konkrétneho clusteru. Credential nemožno použiť na čítanie production database.
7. Audit prepojí user request, approval, workload identity, artifact digest, policy revision a deployment result.
8. Ak EDR počas human session nahlási compromise, nové privileged operations sa zablokujú. Ak je CI issuer compromised, workflow identity trust sa revoke-ne a deployments sa zastavia.

Tento príklad ukazuje, že Zero Trust nevzniká jedným loginom. Je to chain explicitných identities, obmedzených permissions, workload attestation, artifact trust, policy decisionu a enforcementu.

## 36. Troubleshooting Zero Trust accessu

Pri zamietnutom alebo neočakávane povolenom access-e postupuj po decision chain-e, nie náhodným menením rules.

```text
presný principal a credential
→ requested action a resource
→ authentication context
→ device alebo workload evidence
→ policy inputs a revision
→ PE decision
→ PA session setup
→ PEP enforcement
→ direct bypass paths
```

Pri `401` alebo authentication failure over issuer, signature, audience, expiration a session binding. Pri `403` over effective authorization, resource attributes, tenant a delegation context. Pri timeout-e rozlíš policy dependency outage od data-plane connectivity problému.

Ak log ukazuje `allow`, ale request zlyhá, problém môže byť v PA alebo PEP configuration. Ak application request uspeje bez decision logu, pravdepodobne existuje bypass path alebo lokálna fallback policy. Ak workload dostáva nesprávnu identity, preskúmaj attestation selectors, registration entries a node trust.

## 37. Časté anti-patterny

**Network location ako identity.** Interná IP alebo VPN membership sa používa ako hlavný authorization dôkaz. Compromised internal endpoint potom získava broad reachability.

**MFA equals authorization.** Po silnom login-e application neoveruje object alebo tenant permissions. Authentication strength nezaručuje resource entitlement.

**Service mesh equals Zero Trust.** Mesh zapne mTLS, ale všetky services môžu volať všetky endpoints a application ignoruje user delegation.

**Dynamic policy zo stale data.** Device posture sa načíta raz denne a používa sa bez freshness limitu. Decision vyzerá contextual, ale nereaguje na aktuálny compromise.

**PEP s bypass pathom.** Proxy chráni verejný hostname, ale backend je priamo dostupný z interného subnetu.

**Permanentný fail-open.** Emergency fallback sa stane bežným access pathom a nie je auditovaný ani časovo obmedzený.

**Trust score bez hard requirements.** Vysoké priemerné score prekryje chýbajúce phishing-resistant MFA alebo neoverený workload.

**Identity bez lifecycle-u.** Short-lived tokens existujú, ale stale accounts, broad groups a compromised recovery zostávajú nezmenené.

## 38. Kontrolné otázky

1. Prečo network location nemôže byť root identity ani dostatočný authorization dôkaz?
2. Ako sa líšia Policy Engine, Policy Administrator a Policy Enforcement Point?
3. Čo presne overuje workload attestation a ako sa líši od validácie už vydaného certificate-u?
4. Prečo mTLS nevyrieši tenant alebo business-action authorization?
5. Ako rozlíšiš device identity od device posture?
6. Aké failure semantics zvolíš pri výpadku posture service-u pre read-only dashboard a pre production administration?
7. Ako zistíš, že resource má direct bypass path mimo PEP?
8. Aký je rozdiel medzi service konajúcou vo vlastnom mene a delegated user contextom?
9. Ako by si navrhol revocation po compromise workload identity issueru?
10. Ktoré metrics dokazujú resource-level enforcement coverage a ktoré sú iba activity metrics?
11. Ako migrovať z broad VPN accessu bez vytvorenia paralelného slabého pathu?
12. Navrhni Zero Trust decision pre production database query vrátane identity, device/workload state, data scope a audit evidence.

## Glossary impact

Relevantné pojmy: Zero Trust, Zero Trust Architecture, implicit trust, resource-centric security, assume breach, continuous verification, Policy Engine, Policy Administrator, Zero Trust Policy Enforcement Point, control plane, data plane, device identity, device posture, workload identity, workload attestation, node attestation, selector, SPIFFE ID, SVID, SPIRE, Workload API, trust domain, workload federation, identity-aware proxy, Zero Trust Network Access, Security Service Edge, Secure Access Service Edge, microsegmentation, egress policy, risk-adaptive access, step-up authentication, session binding, continuous diagnostics, revocation latency, CISA Zero Trust Maturity Model, Zero Trust pillar, visibility and analytics, automation and orchestration, Zero Trust governance, degraded access mode, direct access bypass, resource enforcement coverage a Zero Trust migration.

## Primárne zdroje

- [NIST SP 800-207 — Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [NIST SP 800-207A — Zero Trust for Cloud-Native Multi-Cloud Applications](https://csrc.nist.gov/pubs/sp/800/207/a/final)
- [NIST CSWP 20 — Planning for a Zero Trust Architecture](https://csrc.nist.gov/pubs/cswp/20/planning-for-a-zero-trust-architecture/final)
- [NIST SP 1800-35 — Implementing a Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/1800/35/final)
- [CISA Zero Trust Maturity Model Version 2.0](https://www.cisa.gov/sites/default/files/2023-04/zero_trust_maturity_model_v2_508.pdf)
- [CISA Microsegmentation in Zero Trust — Introduction and Planning](https://www.cisa.gov/sites/default/files/2025-07/ZT-Microsegmentation-Guidance-Part-One_508c.pdf)
- [SPIFFE Concepts](https://spiffe.io/docs/latest/spiffe/concepts/)
- [SPIFFE ID and SVID specification](https://spiffe.io/docs/latest/spiffe-specs/spiffe-id/)
- [SPIRE Concepts](https://spiffe.io/docs/latest/spire-about/spire-concepts/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Policy as Code](policy-as-code.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
