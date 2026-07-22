# Policy as Code

Policy as Code je prístup, pri ktorom systémové rozhodnutia o povolenom stave alebo operácii vyjadrujeme ako versionované, testovateľné a automaticky vyhodnocované pravidlá. Neznamená to prepísať každý interný dokument do programovacieho jazyka. Formalizujú sa najmä tie pravidlá, ktoré musí software konzistentne presadiť pri authorization, build-e, deployment-e, Kubernetes admission, Infrastructure as Code alebo runtime operácii.

Policy file sám osebe nie je security control. Reálna kontrola vznikne až vtedy, keď správny enforcement point zachytí každú relevantnú operáciu, použije správnu policy revision, dostane dôveryhodné inputs a dokáže výsledok presadiť. Policy as Code je preto celý lifecycle od ľudského zámeru cez decision až po audit a recovery.

```text
policy intent
→ executable policy a supporting data
→ versionovaný policy artifact
→ distribúcia do decision points
→ vyhodnotenie trusted inputu
→ structured decision
→ enforcement
→ decision log, exception a lifecycle management
```

## 1. Prečo Policy as Code existuje

Organizačné pravidlo napísané v dokumente môže byť správne, ale software ho nevie automaticky a konzistentne vyhodnotiť. Ľudia môžu rovnakú vetu interpretovať odlišne, kontrola sa môže vykonávať iba pri manuálnom review a audit často nevie preukázať, ktorá verzia pravidla rozhodla o konkrétnej operácii.

Policy as Code rieši túto medzeru tým, že policy intent preloží do deterministického decision contractu. Napríklad veta „production workloads musia používať schválené images“ sa zmení na pravidlo, ktoré presne určí production scope, identity image-u, trusted registries alebo signing identities, požadované attestations, exception model a failure behavior.

Výsledkom nie je iba automatické `allow` alebo `deny`. Dobre navrhnutý systém poskytuje vysvetliteľný decision, policy revision, audit evidence a bezpečný rollout. To umožňuje policy testovať pred deploymentom, porovnať intended a actual behavior a obnoviť predchádzajúcu známu validnú revision.

## 2. Policy, configuration a control

**Policy** určuje, čo je povolené, zakázané, požadované alebo odporúčané. **Configuration** nastavuje konkrétny component. **Control** je celý mechanizmus, ktorý threatu zabraňuje, deteguje ho alebo umožňuje recovery.

Napríklad pravidlo „container nesmie bežať privileged“ je policy. `ValidatingAdmissionPolicy`, Gatekeeper Constraint alebo Kyverno rule je executable representation. Kubernetes API admission je enforcement boundary. Decision logs, audit mode a incident postup dopĺňajú celý control.

Toto rozlíšenie bráni falošnému pocitu bezpečnosti. Policy môže existovať v Git-e, ale ak cluster nepoužíva príslušný admission mechanism alebo workload možno vytvoriť iným bypass pathom, control neexistuje. Rovnako správne nakonfigurovaný policy engine nepomôže, ak supporting data sú stale alebo attacker môže meniť policy artifact bez review.

## 3. Policy intent a executable policy

Policy intent je ľudsky formulovaný cieľ. Musí byť zrozumiteľný vlastníkom risku a systému. Executable policy je presný machine-readable contract, podľa ktorého decision engine vyhodnotí konkrétny input.

```text
Intent:
Production workloads musia používať podpísané images.

Executable contract musí určiť:
- čo presne patrí do production scope-u;
- ktorý OCI digest je signed subject;
- ktoré issuer a signer identities sú dôveryhodné;
- aké provenance alebo SBOM attestations sú povinné;
- kedy a na ktorej boundary sa decision vykonáva;
- čo sa stane pri nedostupnej verification dependency;
- kto a na ako dlho môže schváliť exception.
```

Preklad intentu do executable policy je design a governance činnosť. Syntax je až posledná vrstva. Ak sú pojmy ako „approved“, „secure“ alebo „critical“ nejasné, code iba automatizuje nejasnosť.

## 4. Policy lifecycle

Policy má lifecycle podobný application code-u, ale jej chyba môže naraz povoliť alebo zablokovať veľký počet operácií. Preto potrebuje ešte presnejší rollout a recovery model.

```text
identifikácia risku
→ definícia intentu a ownera
→ formalizácia inputu, data a decisionu
→ review a threat analysis
→ unit a integration tests
→ audit-only alebo shadow evaluation
→ canary enforcement
→ širší rollout
→ monitoring a exception management
→ zmena, rollback alebo retirement
```

Policy bez ownera a retirement podmienok sa časom stane stale. Napríklad dočasný registry allowlist môže zostať navždy a neskôr povoliť už neudržiavaný source. Lifecycle preto musí zahŕňať effective date, review cadence, compatibility a evidence, že policy je stále vykonávaná na zamýšľanej boundary.

## 5. PAP, PDP, PEP a PIP

Policy architecture sa dá rozdeliť na štyri logické roly. Môžu ich implementovať samostatné produkty alebo viac components jedného systému.

**Policy Administration Point — PAP** spravuje authoring, approval, publication, rollout, rollback, ownership, exceptions a retirement. PAP môže byť kombinácia Git repository, CI pipeline, artifact registry a change-management workflow.

**Policy Decision Point — PDP** prijme input a supporting data, vyhodnotí konkrétnu policy revision a vráti decision. PDP má byť deterministický pre rovnaké inputs alebo explicitne uviesť časové a external dependencies.

**Policy Enforcement Point — PEP** zachytí chránenú operáciu a výsledok presadí. Príkladom je API gateway, Kubernetes admission, Terraform pipeline gate, deployment controller alebo application middleware. PEP musí byť neobíditeľný alebo musí existovať spoľahlivá detekcia bypassu.

**Policy Information Point — PIP** poskytuje attributes a reference data, napríklad identity groups, device posture, asset classification, approved registries alebo vulnerability status. Nesprávne alebo stale PIP data spôsobia nesprávny decision aj pri bezchybnej policy logike.

```text
PAP publikuje policy revision
→ PDP načíta policy a PIP data
→ PEP odošle request input
→ PDP vráti structured decision
→ PEP decision presadí
→ decision log zachová identity a revision
```

## 6. Structured decision ako operational contract

Jednoduchý boolean môže stačiť v malej function, ale production policy potrebuje vysvetliteľný a auditovateľný result. Structured decision môže obsahovať `allow`, reasons, policy IDs, revision, obligations a decision identifier.

```json
{
  "allow": false,
  "decision_id": "01J...",
  "policy_id": "K8S-IMAGE-004",
  "policy_revision": "sha256:...",
  "reason": "image registry is not approved",
  "violations": [
    {
      "path": "spec.template.spec.containers[0].image",
      "expected": "registry.example.com/*"
    }
  ]
}
```

PEP musí rozumieť semantics resultu. Ak PDP vráti obligation `require_step_up`, ale application pozná iba boolean, obligation sa stratí. Decision schema preto patrí k versionovanému contractu rovnako ako API response.

Reason nesmie vyzradiť sensitive interné data nedôveryhodnému callerovi. Používateľská správa môže byť všeobecná, zatiaľ čo interný decision log uchová presnejšiu diagnostiku.

## 7. Input, supporting data a schema

**Input** predstavuje konkrétny request alebo object vyhodnocovaný teraz. **Supporting data** obsahujú reference state používaný viacerými decisions.

Pri Kubernetes admission je inputom AdmissionReview s vytváraným Deploymentom a caller contextom. Supporting data môžu obsahovať approved registries, namespace classification alebo allowed capabilities.

Obe vrstvy potrebujú schema, provenance, freshness a integrity contract. Policy musí rozlišovať „field neexistuje“, „field má prázdnu hodnotu“ a „data source je nedostupný“. Tiché zamieňanie missing data za bezpečnú default hodnotu je častý authorization a admission failure.

Schema versioning je dôležité pri rollout-e. Nový producer môže pridať alebo premenovať fields skôr, než všetky PDP instances načítajú kompatibilnú policy. Compatibility tests preto musia zahŕňať starý aj nový input shape.

## 8. Declarative policy a jej limity

Declarative policy opisuje požadovaný invariant alebo decision bez detailného imperatívneho postupu. OPA Rego a Kubernetes CEL sú príklady jazykov určených na reasoning nad structured data.

Declarative model uľahčuje composition, testovanie a partial evaluation, ale syntax sama nezaručuje zrozumiteľnosť. Komplexné negácie, implicitné defaults a nejasné helper rules môžu byť rovnako nebezpečné ako procedural code.

Policy má pomenovať business alebo security invariant, nie implementačný trik. Namiesto jedného veľkého rule-u je vhodné oddeliť reusable predicates, violation reasons a scope selection tak, aby reviewer vedel vysvetliť výsledok bez simulácie celého programu v hlave.

## 9. Defaults, allowlist a denylist

Každý policy domain potrebuje explicitný behavior pre neznámy alebo neaplikovateľný prípad.

**Default deny** odmietne request, ktorý nebol explicitne povolený. Je vhodný pre authorization a high-risk operations, ale pri neúplnom inventory alebo missing data môže spôsobiť outage.

**Default allow** nechá neznámy prípad pokračovať. Môže byť vhodný počas audit-only rollout-u alebo pre advisory policy, ale nesmie sa omylom stať permanentným security defaultom.

Allowlist enumeruje známe povolené identities, registries, actions alebo resources. Denylist blokuje známe zlé prípady. Denylist je užitočný pre emergency response, no nevie predvídať všetky nové unsafe states.

Príklad: production image policy má používať allowlist trusted signing identities. Emergency denylist konkrétneho digestu môže okamžite zablokovať compromised release, ale nenahrádza positive trust policy.

## 10. Policy composition a conflicts

Jednu operation často hodnotí viac policies: security, compliance, cost, platform a tenant policy. Systém musí mať explicitné combining semantics.

- **Deny overrides** znamená, že jediný deny zablokuje operation.
- **All must pass** vyžaduje úspech všetkých applicable mandatory policies.
- **First applicable** používa prvú matching policy a vyžaduje stabilné ordering.
- **Priority-based** rieši conflicts podľa explicitnej priority.
- **Advisory plus enforcing** oddeľuje warnings od blocking decisions.

Conflict vznikne, keď policies požadujú nezlučiteľné states. Platform policy môže generovať sidecar, zatiaľ čo security policy blokuje jeho capabilities. Region policy môže súčasne vyžadovať dve odlišné locations.

Conflict detection má byť súčasťou tests a pre-production evaluation. Ak sa conflict objaví až v admission-e, používateľ vidí iba blocked deployment a platform team musí spätne zisťovať, ktorá kombinácia revisions ho spôsobila.

## 11. Policy identity, revision a artifact

Každá decision-relevant policy potrebuje stabilné ID, ownera, scope, severity, effective date a immutable revision. Revision môže byť commit SHA, artifact digest alebo release version podľa distribution modelu.

Historical decision bez revision metadata nie je reprodukovateľný. Current source code môže byť už iný než policy, ktorá rozhodla v čase incidentu.

Production policy je vhodné distribuovať ako immutable artifact alebo bundle obsahujúci policy modules, supporting data, manifest, compatibility metadata a integrity evidence. Priamo načítaná mutable branch zhoršuje audit, rollback a supply-chain protection.

Artifact identity tiež umožňuje canary rollout. Časť PDP instances môže načítať novú revision a porovnávať decisions so stabilnou revision pred širšou aktiváciou.

## 12. Repository governance a separation of duties

Policy repository je high-impact source. Malicious change môže otvoriť access, vypnúť image verification alebo zablokovať všetky deployments.

Použi protected branches, CODEOWNERS, mandatory review, CI tests, immutable releases a podľa risku signed artifacts. Write permissions majú byť užšie než read permissions.

Separation of duties oddeľuje policy authora, approvera, artifact publishera, enforcement administratora a exception approvera. Jedna compromised identity nemá vedieť zmeniť policy, publikovať ju, vypnúť PEP a zmazať decision logs.

Emergency path musí byť auditovaný a časovo obmedzený. Break-glass nie je argument pre permanentné admin permissions k celému policy plane-u.

## 13. Policy distribution a OPA bundles

PDP potrebuje dostať správnu policy revision a data. Distribution môže používať container image, configuration artifact, GitOps sync alebo policy-specific bundle protocol.

OPA bundle je tarball alebo directory representation obsahujúca Rego, JSON data a manifest. OPA dokáže bundles periodicky sťahovať, validovať a aktivovať. Ak activation zlyhá, bezpečný model zachová poslednú známu validnú revision a odošle status error.

Signed bundle chráni integrity a publisher authenticity pri prenose a storage. Nepotvrdzuje však, že policy intent je správny alebo že publisher account nebol compromised.

Distribution potrebuje observability: každá PDP instance má hlásiť active revision, posledný successful update a validation failure. Bez toho môže časť fleet-u dlhodobo používať starú policy bez viditeľného incidentu.

## 14. Revision skew, caching a consistency

Pri distribuovaných PDPs nevznikne nová revision všade naraz. **Revision skew** je stav, keď rôzne instances vyhodnocujú rovnaký typ requestu podľa rozdielnych policy versions.

Skew môže byť krátkodobý a prijateľný, ale musí mať limit. High-risk migration môže vyžadovať coordinated activation alebo routing requests iba na ready PDPs.

Decision caching znižuje latency, ale cache key musí zahŕňať všetky decision-relevant inputs: principal, action, resource, tenant, policy revision a relevantný context. Cache iba podľa URL môže nesprávne zdieľať allow medzi users.

Expiration musí rešpektovať revocation requirements. Ak policy zablokuje compromised identity okamžite, desaťminútový cached allow predĺži exposure o desať minút.

## 15. OPA a Rego mentálny model

Open Policy Agent je general-purpose policy engine pre structured data. Application alebo PEP pošle input a položí query do OPA data document tree. Rego rules vytvárajú virtual documents alebo hodnoty, ktoré predstavujú decision.

```text
request input
+ loaded base data
+ Rego rules
→ query result
```

Rego nie je event processor ani enforcement proxy. OPA vyhodnotí policy; caller musí result správne interpretovať a presadiť.

Dôležité je rozlišovať undefined od explicitného `false`. Query môže nemať výsledok, ak sa žiadne rule body nevyhodnotí. Authorization policy má preto definovať bezpečný default a testovať missing fields.

OPA sa môže používať ako sidecar, daemon, centralized service, Go library alebo compiled WebAssembly podľa latency, isolation a distribution requirements. Topology mení failure a consistency model, nie samotnú policy semantics.

## 16. Partial evaluation a WebAssembly

Partial evaluation vopred vyhodnotí časť policy voči známym data a vytvorí zjednodušenú residual policy pre inputs, ktoré budú známe až neskôr. Môže znížiť runtime cost alebo preložiť policy bližšie k data source-u.

WebAssembly umožňuje skompilovať časť OPA policy na portable runtime module. To je užitočné v environments, kde nechceme samostatný OPA process alebo potrebujeme low-latency local evaluation.

Oba modely pridávajú artifact a compatibility lifecycle. Musíme vedieť, z ktorej source revision compiled policy vznikla, s akým runtime ABI je kompatibilná a ako sa aktualizuje. Compiled policy nesmie byť neauditovateľný binary oddelený od source a tests.

## 17. Policy testing

Unit test overuje konkrétne allow, deny a violation outputs pre definované inputs. Table-driven tests pokrývajú kombinácie identities, resources, environments a edge cases bez duplicity test code-u.

Negative tests sú rovnako dôležité ako positive tests. Policy pre approved registry musí testovať podobne vyzerajúci attacker domain, missing digest, uppercase alebo normalization edge cases a exception expiration.

Property tests overujú invariant naprieč veľkým input priestorom, napríklad „žiadny unauthenticated principal nesmie dostať write“. Differential tests porovnávajú starú a novú revision a zobrazia všetky zmenené decisions nad reprezentatívnym corpusom.

Integration test musí overiť celý path od PEP po PDP a späť. Samotný Rego unit test nepreukazuje, že API gateway posiela správny tenant alebo že Kubernetes admission binding matchuje zamýšľané namespaces.

## 18. Shift-left, runtime enforcement a background audit

Shift-left policy poskytuje skorý feedback v developer workflowe. Conftest môže vyhodnocovať OPA/Rego policies nad YAML, JSON alebo Terraform planom ešte pred deploymentom.

Runtime enforcement chráni skutočnú operation na authoritative boundary. Background audit periodicky kontroluje už existujúce resources a odhaľuje drift alebo objects vytvorené pred zavedením policy.

```text
shift-left
→ rýchly feedback, ale môže byť obídený

runtime enforcement
→ blokuje skutočnú operation na boundary

background audit
→ deteguje existujúci alebo vzniknutý drift
```

Tieto vrstvy sa dopĺňajú. CI pass nie je dôkaz runtime enforcementu. Admission policy zase neposkytuje developerovi taký rýchly a zrozumiteľný feedback ako local test.

## 19. Infrastructure as Code policy

IaC policy môže hodnotiť source configuration, Terraform plan alebo actual cloud state. Každá vrstva vidí inú informáciu.

Source scan vidí author intent, ale nie všetky computed values. Plan policy vidí provider-resolved proposed changes a replacement actions. Runtime audit odhalí drift a zmeny vykonané mimo Terraformu.

Terraform plan je sensitive artifact: môže obsahovať secrets alebo interné topology data. Policy engine preto potrebuje least-privilege access a redaction. Saved plan a policy decision musia patriť k rovnakému source revision a provider contextu; inak môžeme schváliť jeden plan a aplikovať iný.

Príklad cost policy nemá iba blokovať „instance type je príliš drahý“. Má poznať environment, ownera, exception a business purpose. Inak bude obchádzaná alebo bude blokovať legitímne high-capacity workloads.

## 20. Kubernetes admission flow

Kubernetes admission prebieha po authentication a authorization API requestu, ale pred persistence objectu do etcd. Mutating mechanisms môžu object zmeniť a validating mechanisms ho môžu odmietnuť.

```text
API request
→ authentication
→ authorization
→ mutation
→ validation
→ persistence
→ controllers reagujú na nový desired state
```

Admission policy chráni create, update a niektoré delete operations podľa API semantics. Neoveruje automaticky runtime správanie po vytvorení resource-u ani external resources mimo Kubernetes API.

Caller identity dostupná v admission requeste môže byť dôležitá pre request-time policy, ale background audit často nemá rovnaký user context. Policy musí rozlišovať, ktoré rules sú auditovateľné bez historical caller data.

## 21. ValidatingAdmissionPolicy a CEL

`ValidatingAdmissionPolicy` je Kubernetes in-process declarative validation mechanism. Používa Common Expression Language — CEL a nevyžaduje external webhook network call.

Policy object definuje logic, binding určuje scope a enforcement actions a voliteľný parameter resource dopĺňa environment-specific data. Toto oddelenie umožňuje jednu reusable policy použiť s rôznymi parameters.

In-process evaluation znižuje network dependency, ale stále môže zablokovať API operations pri chybnej expression alebo príliš širokom match-e. Preto treba používať test cluster, scoped bindings, audit alebo warn rollout a recovery model pre admission configuration.

Validation je vhodná, keď chceme object prijať alebo odmietnuť bez mutation. Príkladom je zákaz privileged containers alebo požiadavka na approved image registry.

## 22. MutatingAdmissionPolicy

`MutatingAdmissionPolicy` je Kubernetes declarative in-process mutation mechanism používajúci CEL. V Kubernetes v1.36 je stable a podporuje mutation cez apply configuration alebo JSON Patch.

Mutation mení submitted object pred validation a persistence. Je vhodná pre jednoduché, deterministické defaults alebo platform metadata, ale zvyšuje vzdialenosť medzi authorovým manifestom a stored objectom.

Mutation musí byť idempotentná: opakované vyhodnotenie nemá stále meniť object. Viaceré mutators môžu interagovať a ordering nemusí byť vhodný základ correctness. Po mutation je preto dôležitá validation, ktorá overí final invariant.

Ak je cieľ iba zakázať unsafe state, validation je jednoduchšia než mutation. Automatické „opravovanie“ security-sensitive fields môže skryť chybný intent a komplikovať troubleshooting.

## 23. Admission webhooks oproti in-process policy

Admission webhook volá external HTTPS service. Je flexibilný a môže používať ľubovoľný jazyk alebo external data, ale pridáva network, TLS, certificate, availability a latency dependencies do Kubernetes API pathu.

In-process CEL policy beží v API server admission stacku a odstráni external network hop. Má užší execution model, čo znižuje niektoré operational risks, ale nemusí pokryť komplexné use cases.

Výber závisí od potreby external lookups, language expressiveness, performance a failure modelu. Webhook `failurePolicy: Fail` chráni invariant, ale outage webhooku môže zablokovať API writes. `Ignore` zachová availability, ale počas outage-u vytvorí enforcement gap.

Timeout, match scope, side effects a recovery musia byť explicitné. Admission component nemá blokovať vlastný repair path bez break-glass alebo manifest-based recovery mechanizmu.

## 24. Gatekeeper: ConstraintTemplate a Constraint

Gatekeeper je Kubernetes policy controller postavený na OPA. `ConstraintTemplate` definuje reusable violation logic a schema parameters. Z neho vznikne custom resource type pre konkrétne `Constraint` objects.

Constraint potom určuje parameters, match scope a enforcement behavior. Napríklad template môže definovať „vyžaduj labels“ a constraints môžu pre production a development používať rozdielne required labels.

Tento model oddeľuje policy implementation od instances, ale template schema je compatibility contract. Zmena parameter shape môže rozbiť existujúce Constraints. Versioning a migration preto musia byť plánované.

Gatekeeper môže vyhodnocovať admission requests a vykonávať background audit existujúcich resources. Audit výsledky však reprezentujú current state a nemusia mať caller context dostupný pri pôvodnom requeste.

## 25. Gatekeeper audit a jeho hranice

Gatekeeper audit periodicky prejde existing resources a zapíše violations do Constraint statusu, metrics alebo events podľa configuration. Je užitočný pri zavedení novej policy, pre-existing objects a detection driftu.

Audit nie je historical event log. Typicky ukazuje posledný audit state a počet výsledkov môže byť limitovaný. Pre dlhodobú evidenciu treba exportovať metrics, events alebo findings do external systemu.

Rules závislé od admission `userInfo` nemusia byť v background audite vyhodnotiteľné, pretože historical caller identity nie je súčasťou stored objectu. Takéto policy treba navrhovať ako request-time controls a ich decisions logovať pri admission-e.

## 26. Kyverno policy model

Kyverno poskytuje Kubernetes-native policy APIs a pracuje s validation, mutation, generation, image verification a ďalšími lifecycle operáciami. Jeho API sa vyvíja smerom k CEL-based policy types.

Aktuálna dokumentácia odlišuje nové `ValidatingPolicy`, `ImageValidatingPolicy`, `MutatingPolicy`, `GeneratingPolicy` a `DeletingPolicy` typy od staršieho `ClusterPolicy` modelu. Pri návrhu treba overiť version a deprecation state konkrétnej Kyverno release, nie kopírovať starý manifest bez compatibility review.

Kyverno Policy Reports sú current-state compliance resources, nie úplný historical audit. `PolicyReport` je namespaced a `ClusterPolicyReport` cluster-scoped. Audit mode môže povoliť object a zapísať violation; Enforce mode ho zablokuje.

Kubernetes-native syntax znižuje bariéru pre platform teams, ale nemení potrebu tests, rollout-u, exception governance a protection policy repository.

## 27. Image verification policy

Image verification policy spája admission s artifact trust modelom z kapitoly [Image signing](image-signing.md). Policy nemá kontrolovať iba tag alebo prítomnosť ľubovoľnej signature.

Decision potrebuje immutable image digest, trusted signer identity, issuer, repository/workflow constraints a požadované attestations. Pri multi-architecture image treba vedieť, či sa podpisuje image index alebo platform manifests.

Verification dependency outage potrebuje explicitný model. Production môže fail-closed, zatiaľ čo development môže krátko použiť audit mode. Cached verification musí byť viazaná na digest a trust-policy revision.

Image policy musí byť presadená na každom deployment path-e. Ak cluster admission kontroluje Pods, ale privileged operator môže priamo spustiť image na nodes mimo Kubernetes, boundary zostáva neúplná.

## 28. Exceptions a break-glass

Policy exception je riadené a časovo ohraničené odchýlenie od pravidla. Potrebuje ownera, scope, business alebo incident dôvod, approvera, expiration, compensating controls a audit.

Exception nemá byť broad boolean `disable_policy`. Má sa viazať na konkrétny resource, tenant, artifact digest alebo action. Čím presnejší scope, tým menší blast radius.

Break-glass je emergency path pre situáciu, keď bežný policy alebo identity mechanism bráni recovery. Musí byť oddelený, silno chránený a po použití reviewed. Permanentná hidden allow rule nie je break-glass, ale bypass.

Expiration sa má presadzovať technicky. Ticket s dátumom ukončenia nepomôže, ak allowlist zostane v policy data navždy.

## 29. Audit-only, canary a enforcement rollout

Nová policy môže odhaliť stovky existujúcich violations alebo obsahovať false positives. Priamy global enforcement môže spôsobiť outage.

Audit-only alebo shadow mode vyhodnocuje requests bez blokovania a zbiera expected impact. Po oprave major violations možno enforcement zapnúť pre test namespace, non-critical tenant alebo malý cohort.

Canary musí merať denied legitimate operations, latency, PDP errors, revision activation a bypass paths. Promotion má mať explicitné criteria a rollback.

Audit mode nesmie byť permanentný bez risk acceptance. Policy, ktorá iba reportuje critical unsafe state a nikdy neprejde do enforcementu, je detection control, nie preventive control.

## 30. Decision logs a observability

Decision log má zachytiť query, result, policy revision, decision ID, PDP instance a relevantný context. OPA decision logs môžu obsahovať input a bundle metadata a podporujú masking sensitive fields pred exportom.

Logs musia byť korelovateľné s PEP requestom. Ak gateway loguje request ID a OPA iný decision ID bez väzby, incident investigation nevie spojiť decision s actual operation.

Status telemetry má ukazovať loaded bundle revision, activation errors, plugin health a last successful update. Metrics majú pokrývať evaluation latency, errors, undefined decisions, cache behavior a decision counts podľa policy ID bez neobmedzenej cardinality.

Policy telemetry môže obsahovať sensitive identities a resource data. Access, retention a redaction patria k designu, nie k neskoršej log-platform úprave.

## 31. Performance a availability

Policy evaluation sa často nachádza v latency-sensitive request path-e. Komplexné rules, veľké data documents alebo synchronous external lookups môžu zhoršiť tail latency.

Preferuj local deterministic evaluation a pravidelne distribuované supporting data, ak freshness requirements dovoľujú. External lookup pri každom requeste pridáva failure dependency a môže vytvoriť cascading outage.

Timeout musí mať explicitný outcome. Authorization request po timeout-e nesmie náhodne prejsť iba preto, že caller nerozlišuje `deny` od `PDP unavailable`.

PDP capacity plánuj podľa peak request rate-u, evaluation costu a rollout events. Bundle update alebo cache invalidation môže krátkodobo zvýšiť CPU a latency vo všetkých instances.

## 32. Security policy plane-u

Policy plane je high-value target. Threats zahŕňajú malicious source change, compromised publisher, bundle tampering, stale policy, poisoned supporting data, PEP bypass a decision-log deletion.

Ochrana zahŕňa least privilege, separation of duties, artifact signatures, secure distribution, revision reporting, immutable audit a monitoring changes. Policy signing keys a CI workload identities majú mať úzky scope.

Input je často nedôveryhodný. Policy language a engine musia bezpečne spracovať crafted nested data, large payloads a missing fields bez denial of service alebo panic-u.

Policy nemá obsahovať secrets. Secret použitý ako allowlist alebo API credential v bundle-i sa distribuuje do všetkých PDPs a objaví sa v artifacts alebo debug outpute.

## 33. Incident response

Pri malicious alebo chybnej policy revision je prvým cieľom zastaviť ďalšiu distribúciu a zistiť active revision v každom PDP.

```text
freeze publication
→ identify affected revision a scope
→ rollback na last-known-good artifact
→ verify activation vo fleet-e
→ preserve source, approval, CI a decision evidence
→ identify decisions vykonané počas exposure window
→ remove bypass alebo poisoned data
→ rotate publisher credentials, ak boli compromised
→ add regression tests a rollout guardrails
```

Rollback source code-u nestačí, ak PDPs naďalej používajú cached bundle. Recovery musí potvrdiť actual active state na enforcement path-e.

Ak policy neprimerane blokovala operations, treba overiť aj partial side effects. Napríklad deployment mohol vytvoriť niektoré resources pred neskorším policy failure-om v external workflowe.

## 34. Kompletný príklad: production image admission

Cieľ je povoliť iba release images vytvorené schváleným CI workflowom.

1. Build pipeline vytvorí OCI image a určí immutable digest.
2. Protected release workflow podpíše digest keyless identity a pripojí provenance attestation.
3. Kubernetes admission PEP zachytí Deployment request a odošle image digest, namespace a caller context do PDP alebo in-process policy.
4. PIP data určia, že namespace je production a ktoré signer/workflow identities sú trusted.
5. Policy overí digest reference, signature identity, provenance subject a exception state.
6. Structured decision uvedie allow alebo konkrétne violations a policy revision.
7. PEP request odmietne alebo prijme. Decision log sa koreluje s Kubernetes audit eventom.
8. Background audit pravidelne kontroluje existing workloads a registry re-scanning môže spustiť quarantine proces pre compromised digest.

Failure modes zahŕňajú mutable tag bez digestu, unavailable transparency evidence, stale trust roots, direct Pod creation bypass cez privileged path alebo PEP configuration, ktorá nematchuje custom workload CRD.

## 35. Troubleshooting workflow

Pri neočakávanom deny alebo allow postupuj po celom chain-e:

```text
request a exact input
→ PEP match a scope
→ PDP endpoint alebo in-process evaluator
→ loaded policy revision
→ supporting data revision a freshness
→ query result a undefined handling
→ combining semantics
→ enforcement action
→ decision log a bypass paths
```

Ak local test povoľuje a production deny, porovnaj input schema, policy revision a data. Ak PDP vracia allow, ale operation je blocked, skontroluj PEP mapping a ďalšie policies v chain-e. Ak operation prejde bez decision logu, hľadaj bypass alebo fallback.

Pri Kubernetes admission skontroluj policy a binding match, namespace selectors, parameter resource, failure policy, webhook timeout a final object po mutation. Pri OPA bundles skontroluj status API, active revision, signature validation a download errors.

## 36. Časté anti-patterny

**Policy file equals control.** Pravidlo je v Git-e, ale neexistuje neobíditeľný PEP.

**Boolean bez explanation.** User ani operator nevie, ktorá policy a field decision spôsobili.

**Stale PIP data.** Správna logika rozhoduje nad starým allowlistom alebo posture.

**Permanentný audit mode.** Critical violations sa reportujú, ale nikdy neblokujú ani nemajú risk ownera.

**Global exception.** Jeden emergency case vypne policy pre celý cluster alebo environment.

**Mutable distribution.** PDPs načítavajú branch bez immutable revision a fleet reporting-u.

**Policy unit tests bez integration testu.** Rego je správne, ale PEP posiela nesprávny tenant alebo vôbec nematchuje request.

**Fail-open bez visibility.** PDP outage automaticky povoľuje operations a nevytvára urgentný alert.

## 37. Kontrolné otázky

1. Prečo policy súbor nie je sám osebe security control?
2. Ako sa líšia PAP, PDP, PEP a PIP a aké trust boundaries medzi nimi vznikajú?
3. Čo má obsahovať structured decision pre audit a troubleshooting?
4. Prečo input a supporting data potrebujú samostatný schema a freshness contract?
5. Ako sa líši default deny, allowlist a emergency denylist?
6. Ako odhalíš conflict medzi dvoma policies pred enforcement rolloutom?
7. Prečo decision cache musí obsahovať policy revision a všetky relevantné dimensions?
8. Aký je rozdiel medzi shift-left policy, runtime enforcementom a background auditom?
9. Kedy zvoliť Kubernetes CEL admission policy a kedy external webhook?
10. Prečo mutation potrebuje následnú validation a idempotenciu?
11. Ako fungujú Gatekeeper ConstraintTemplate a Constraint?
12. Aké limitations má background audit pri policy závislej od caller identity?
13. Ako navrhneš časovo ohraničenú policy exception bez global bypassu?
14. Ako obnovíš fleet po malicious policy bundle-i a preukážeš active revision?
15. Navrhni tests a rollout pre production image-signing policy.

## Glossary impact

Relevantné pojmy: Policy as Code, policy intent, executable policy, policy lifecycle, Policy Administration Point, Policy Decision Point, Policy Enforcement Point, Policy Information Point, policy input, policy data, declarative policy, default deny, policy composition, policy conflict, policy revision, policy artifact, policy bundle, signed policy bundle, policy distribution, revision skew, Open Policy Agent, Rego, undefined decision, structured decision, partial evaluation, policy WebAssembly, policy unit test, differential policy testing, shift-left policy, Conftest, infrastructure policy, admission policy, ValidatingAdmissionPolicy, ValidatingAdmissionPolicyBinding, MutatingAdmissionPolicy, CEL policy, admission webhook, failure policy, Gatekeeper, ConstraintTemplate, Constraint, Gatekeeper audit, Kyverno, Policy Report, policy obligation, policy exception, break-glass policy, policy canary, decision log a policy bypass.

## Primárne zdroje

- [Open Policy Agent documentation](https://www.openpolicyagent.org/docs)
- [OPA Policy Language — Rego](https://www.openpolicyagent.org/docs/policy-language)
- [OPA Bundles](https://www.openpolicyagent.org/docs/management-bundles)
- [OPA Decision Logs](https://www.openpolicyagent.org/docs/management-decision-logs)
- [OPA Status](https://www.openpolicyagent.org/docs/management-status)
- [Gatekeeper documentation](https://open-policy-agent.github.io/gatekeeper/website/docs/)
- [Gatekeeper Constraint Templates](https://open-policy-agent.github.io/gatekeeper/website/docs/constrainttemplates/)
- [Gatekeeper Audit](https://open-policy-agent.github.io/gatekeeper/website/docs/audit/)
- [Kubernetes Validating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/)
- [Kubernetes Mutating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/mutating-admission-policy/)
- [Kubernetes admission webhook good practices](https://kubernetes.io/docs/concepts/cluster-administration/admission-webhooks-good-practices/)
- [Kyverno policy types](https://kyverno.io/docs/policy-types/overview/)
- [Kyverno Policy Reports](https://kyverno.io/docs/guides/reports/)
- [Conftest documentation](https://www.conftest.dev/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Image signing](image-signing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Zero Trust →](zero-trust.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
