from pathlib import Path

path = Path('docs/16-gitops-and-platform-engineering/gitops-secrets.md')
text = path.read_text(encoding='utf-8')


def add(heading: str, prose: str, marker: str) -> None:
    global text
    if marker in text:
        return
    needle = heading + '\n\n'
    if needle not in text:
        raise SystemExit(f'Missing heading: {heading}')
    text = text.replace(needle, needle + prose.rstrip() + '\n\n', 1)


def repl(old: str, new: str) -> None:
    global text
    if new in text:
        return
    needle = old + '\n'
    if needle not in text:
        raise SystemExit(f'Missing line: {old}')
    text = text.replace(needle, new + '\n', 1)

for old, new in [
('- local clones a developer backups;', '- **Local clones a developer backups** — kopírujú secret bytes mimo central repository controls a môžu zostať na unmanaged diskoch aj po odstránení current file-u.'),
('- pull request diffs a email notifications;', '- **Pull request diffs a notifications** — distribuujú value reviewerom, botom a email systems, ktoré majú vlastnú retention a access policy.'),
('- CI workspaces, caches a artifacts;', '- **CI workspaces, caches a artifacts** — môžu plaintext uložiť na runner disk alebo do dlhodobo dostupného artifact store-u s širším reader scope-om.'),
('- search indexov;', '- **Search indexes** — extrahujú text pre full-text query a môžu sprístupniť secret actorom, ktorí nemajú priamy clone access.'),
('- Git object history aj po odstránení z current branch;', '- **Git object history** — zachováva blob v reachable alebo reflog/mirror history aj po odstránení z current tree-u, takže bežný follow-up commit exposure neuzatvorí.'),
('- forks, mirrors a audit exports.', '- **Forks, mirrors a audit exports** — vytvárajú ďalšie administratívne domains, v ktorých sa deletion a access revocation vykonávajú nezávisle.'),
]: repl(old, new)

for old, new in [
('- plaintext value nemusí byť v Git-e ani encrypted formou;', '- **No value payload in Git** — repository drží iba logical provider reference a target mapping, takže compromise Git readera priamo neodhalí credential bytes.'),
('- provider môže centralizovať generation, rotation, audit a revocation;', '- **Central provider authority** — provider priraďuje versions, vykonáva rotation a revocation a produkuje audit events nad jedným authoritative lifecycle-om.'),
('- short-lived credentials a leases sú prirodzenejšie.', '- **Short-lived credentials a leases** — môžu byť generované alebo obnovované providerom bez commitu každej ephemeral value do Git history.'),
('- provider availability a IAM sú runtime dependencies;', '- **Provider availability a IAM dependency** — reconciliation alebo workload refresh zlyhá, ak external API, network, workload identity alebo authorization nie sú dostupné.'),
('- broad SecretStore môže umožniť tenantovi načítať cudzie secrets;', '- **Broad SecretStore scope** — tenant-controlled ExternalSecret môže zneužiť shared provider role na čítanie pathu mimo svojho namespace alebo business boundary.'),
('- reference na mutable alias môže meniť effective value bez Git commit-u;', '- **Mutable provider alias** — alias ako `current` môže resolve-nuť novú version bez Git change-u, takže exact effective generation musí byť zachytená v runtime evidence.'),
('- target Secret a consumer môžu zostať stale;', '- **Stale materialization alebo consumer** — provider už môže mať new version, zatiaľ čo controller, Kubernetes Secret alebo application cache stále používajú old value.'),
('- provider restore alebo version deletion môže znemožniť rollback.', '- **Provider retention boundary** — deleted alebo unavailable historical version znamená, že Git reference sama nedokáže obnoviť predchádzajúcu credential generation.'),
]: repl(old, new)

for old, new in [
('- wrong KMS key alebo encryption context;', '- **Wrong KMS key alebo encryption context** — ciphertext je validný, ale cryptographic authorization subject nezodpovedá key policy alebo additional authenticated contextu.'),
('- workload identity trust policy nepovoľuje service account;', '- **Workload-identity trust mismatch** — projected token je vydaný, no cloud role odmietne namespace, service account, issuer alebo audience a controller data key neotvorí.'),
('- KMS outage/throttling;', '- **KMS outage alebo throttling** — source artifact zostáva dostupný, ale render nemôže vzniknúť a aggressive retry môže zosilniť provider pressure.'),
('- encrypted regex nechala citlivý field plaintext;', '- **Incomplete encrypted-field selection** — nesprávny `encrypted_regex` ponechá citlivú value čitateľnú v Git-e aj napriek tomu, že file obsahuje SOPS metadata.'),
('- key policy povoľuje príliš broad decrypt;', '- **Broad decrypt policy** — shared controller alebo compromised tenant môže otvoriť ciphertext iného environmentu, hoci Kubernetes target RBAC vyzerá oddelene.'),
('- shared global credential obchádza tenant boundary;', '- **Shared global private credential** — jeden age key alebo static cloud key spája všetky tenants do jedného compromise a rotation blast radiusu.'),
('- controller log alebo debug output vypíše decrypted content;', '- **Plaintext logging** — decryption alebo template error môže preniesť secret z transient memory do persistent logs, support bundles a alert systems.'),
('- decrypted Secret sa aplikuje do wrong namespace.', '- **Wrong target namespace** — cryptographically správna value sa materializuje do nesprávneho authorization domainu a stáva sa čitateľnou cudzím workloads.'),
]: repl(old, new)

for old, new in [
('- vytvorí operator celý Secret alebo merge-ne iba vybrané keys?', '- **Whole-object create verzus key merge** — whole-object ownership zjednodušuje convergence, kým merge umožní shared target, ale zavádza per-key writers a conflict semantics.'),
('- odstráni sa target pri delete ExternalSecretu?', '- **Deletion coupling** — owner-based deletion odstráni credential spolu s declaration, zatiaľ čo orphan policy zachová availability za cenu stale secret debt-u.'),
('- smie iný controller meniť rovnaké keys?', '- **Multiple key writers** — ak ďalší controller alebo human mení rovnaký key, systém potrebuje precedence contract; inak target oscilluje alebo silently overwrituje values.'),
('- čo sa stane, ak provider property zmizne?', '- **Missing provider property** — policy musí rozhodnúť medzi fail-closed deletion/invalid state a zachovaním last-known value s explicitným stale warningom.'),
('- má stale target zostať dostupný alebo sa odstrániť?', '- **Stale-target behavior** — availability a security trade-off musí byť explicitný, pretože ponechaná revoked credential zlyháva inak než okamžite odstránený Secret.'),
('- je target immutable?', '- **Target immutability** — immutable Secret vyžaduje replace/new-name rollout namiesto in-place update-u a mení rotation aj cleanup ordering.'),
]: repl(old, new)

for old, new in [
('- issuer a audience validation;', '- **Issuer a audience validation** — cloud provider musí akceptovať token iba od trusted cluster issueru a pre intended federation endpoint, nie generic bearer token.'),
('- trust policy bez wildcardov;', '- **Subject-bound trust policy** — namespace a service-account claims sa viažu na konkrétny controller/tenant a wildcard nesmie rozšíriť assume-role na celý cluster.'),
('- provider resource restrictions;', '- **Provider resource restrictions** — role smie decryptovať alebo čítať iba environment/tenant key a secret paths potrebné pre daný reconciliation subject.'),
('- token/credential TTL;', '- **Short token a credential TTL** — obmedzuje usefulness ukradnutej identity a núti pravidelné reauthorization namiesto permanentného bootstrap secretu.'),
('- audit correlation;', '- **Audit correlation** — cloud request ID, assumed role session a Kubernetes service account sa musia spojiť s Flux/ExternalSecret operation identity.'),
('- fail-closed behavior pri identity error.', '- **Fail-closed identity error** — controller nesmie pri federation failure použiť shared fallback key alebo stale broad credential, ktorý obíde tenant boundary.'),
]: repl(old, new)

for old, new in [
('- API authorization a RBAC;', '- **API authorization a RBAC** — obmedzujú principals, ktoré môžu list/get/watch Secret objects alebo ich získavať nepriamo cez Pod create a service-account bindings.'),
('- admission a namespace isolation;', '- **Admission a namespace isolation** — zabraňujú materialization do wrong targetu a presadzujú allowed Secret types, labels, mounts a workload relationships.'),
('- etcd encryption at rest;', '- **etcd encryption at rest** — chráni persisted control-plane bytes a backups pred raw storage readerom, ale nie pred legitímnym API server decryptom.'),
('- control-plane backups;', '- **Control-plane backups** — obsahujú historical plaintext-equivalent secret data a potrebujú encryption, access, retention a secure disposal ako production secret store.'),
('- audit logs;', '- **Audit logs** — majú zaznamenať metadata o Secret access-e bez request/response bodies, ktoré by samy vytvorili ďalší plaintext archive.'),
('- node/kubelet access;', '- **Node a kubelet access** — privileged node actor môže čítať mounted Secret alebo container state, preto scheduling a node administration patria do confidentiality modelu.'),
('- container runtime a process isolation;', '- **Container runtime a process isolation** — chránia environment, files a memory pred susedným workloadom, debug toolingom a host compromise-om.'),
('- debug, exec a ephemeral-container permissions.', '- **Debug, exec a ephemeral-container permissions** — môžu obísť application API a priamo čítať mounted files alebo process environment, preto sú secret-reader privileges.'),
]: repl(old, new)

for old, new in [
('- secret logical ID a version/generation;', '- **Logical secret ID a version/generation** — umožňujú korelovať rotation bez zverejnenia value a musia pochádzať z authoritative provider/controller metadata.'),
('- ciphertext digest;', '- **Ciphertext digest** — odlišuje encrypted payload generations a dokazuje, ktorý Git blob controller spracoval, no neslúži ako hash plaintextu.'),
('- provider object ARN/path hash;', '- **Provider object coordinate alebo bezpečný opaque ID** — identifikuje authority object; path sa má maskovať, ak jeho názov odhaľuje tenant alebo business context.'),
('- controller operation ID;', '- **Controller operation ID** — spája fetch/decrypt/materialize attempt s logs, status conditions a downstream API requestmi.'),
('- refresh timestamp a result;', '- **Refresh timestamp a result** — ukazujú freshness a posledný úspešný/failed provider sync bez tvrdenia, že workload value už načítal.'),
('- target Secret resourceVersion;', '- **Target Secret resourceVersion** — dokazuje Kubernetes object update a umožňuje zistiť, ktoré Pods vznikli pred alebo po materialization.'),
('- workload loaded generation;', '- **Workload loaded generation** — application endpoint alebo metric potvrdzuje value používanú processom, čo Secret resourceVersion sama nevie.'),
('- revocation status;', '- **Revocation status** — provider authority potvrdzuje, či old generation je ešte akceptovaná a či negative test má zlyhať.'),
('- KMS key ID a audit request ID.', '- **KMS key ID a audit request ID** — dokazujú, ktorý cryptographic authority decision otvoril data key a umožňujú incident correlation.'),
('- raw values;', '- **Raw values** — nikdy nepatria do logu, diffu ani eventu, pretože observability store by sa stal ďalším neautorizovaným secret managerom.'),
('- complete rendered Secret manifests;', '- **Complete rendered Secret manifests** — obsahujú všetky data keys a môžu uniknúť cez CI preview, controller debug alebo support export.'),
('- environment dumps;', '- **Environment dumps** — kopírujú process-loaded secrets spolu s unrelated diagnostics a často sa uchovávajú dlhšie než credential TTL.'),
('- provider API responses;', '- **Provider API responses** — môžu obsahovať value, lease token alebo sensitive metadata a majú sa parsovať/redactovať pred loggingom.'),
('- templating errors obsahujúce secret;', '- **Templating errors s input contextom** — nesmú serializovať decrypted document alebo substituted value do exception message-u.'),
('- debug command history.', '- **Debug command history** — shell, terminal recording a ticket copy môžu zachovať plaintext aj po ukončení incident session.'),
]: repl(old, new)

for old, new in [
('- cross-namespace reference na shared decryption Secret;', '- **Cross-namespace decryption reference** — tenant môže získať key material alebo controller capability spravovanú v inom trust boundary.'),
('- ClusterSecretStore s broad provider role;', '- **Broad `ClusterSecretStore` role** — namespaced requester môže cez cluster-scoped store čítať provider paths, ktoré Kubernetes namespace policy sama neobmedzuje.'),
('- tenant môže zvoliť arbitrary remote key path;', '- **Arbitrary remote key path** — untrusted `remoteRef.key` zmení controller na confused deputy a obíde catalog alebo UI ownership checks.'),
('- controller používa cluster-wide KMS decrypt;', '- **Cluster-wide KMS decrypt** — compromise jedného controller processu alebo tenant-controlled ciphertextu ohrozuje všetky environment keys.'),
('- target Secret možno vytvoriť v inom namespace;', '- **Cross-tenant target placement** — materializuje plaintext tam, kde ho môžu čítať cudzie service accounts alebo workloads.'),
('- catalog/portal ukáže secret metadata cudziemu tenantovi;', '- **Metadata disclosure v portali** — provider paths, versions a ownership môžu odhaliť topology alebo business relationships aj bez plaintext value.'),
('- backup alebo support bundle mieša namespaces.', '- **Mixed-tenant backup alebo support bundle** — export obíde runtime namespace boundaries a vytvorí shared reader/retention domain.'),
]: repl(old, new)

for old, new in [
('- Git history;', '- **Git history** — musí uchovať required ciphertext generation a repository trust evidence; samotný current branch nemusí obsahovať rollback candidate.'),
('- decryption key/KMS availability;', '- **Decryption key alebo KMS availability** — recovery cluster potrebuje authorization otvoriť historical data key bez použitia broad emergency credentialu.'),
('- controller manifests a identity trust;', '- **Controller manifests a identity trust** — obnovujú exact decryption implementation, service account a cloud federation contract, ktoré ciphertext spracujú.'),
('- target cluster bootstrap;', '- **Target cluster bootstrap** — musí bezpečne vytvoriť namespaces, RBAC, KMS trust a Git source skôr, než sa plaintext materializuje.'),
('- test, že historical required payload sa dá decryptovať.', '- **Functional decryption a consumer test** — overuje nielen cryptographic open, ale aj target Secret, workload load a úspešnú autentizáciu expected version.'),
('- provider backup/version retention;', '- **Provider backup a version retention** — určujú, či logical reference ešte resolve-ne required generation a či provider dokáže obnoviť metadata a value.'),
('- IAM a workload identity restore;', '- **IAM a workload-identity restore** — obnovujú subject-bound provider read bez static break-glass key-u alebo cross-tenant wildcardu.'),
('- SecretStore/ExternalSecret desired state;', '- **`SecretStore` a `ExternalSecret` desired state** — rekonštruujú provider, authentication, property, refresh a target ownership contract.'),
('- target Secret reconstruction;', '- **Target Secret reconstruction** — musí vytvoriť správny namespace/name/schema a spustiť consumer reload podľa application consumption mode.'),
('- decision, či restored old credential je ešte validná.', '- **Validity decision pre historical credential** — provider a incident policy určia, či old version možno používať, zostáva revoked alebo sa musí nahradiť new generation.'),
]: repl(old, new)

add('## 22. Connected incident `GITOPS-PAY-62`', '''Secret incident je writer a generation race, nie iba nesprávne načasovaný restart. Provider, Git ciphertext, Kubernetes Secret a running process mali štyri odlišné states a manual patch zmenil iba jednu z nich.

Jednotlivé body nižšie vysvetľujú, ako shared decryption authority a chýbajúci rollout/reload contract zabránili bezpečnej rotation. Flux potom správne obnovil starý desired payload, čím emergency patch zvrátil.''', 'Secret incident je writer a generation race')
for old, new in [
('- ciphertext bol zašifrovaný pre shared age recipient;', '- **Shared age recipient** — rovnaký private key mohol otvoriť staging aj production payloady a vytvoril spoločný compromise a rotation boundary.'),
('- private age key bol uložený v `flux-system/sops-age` a broad kustomize-controller ho používal pre staging aj production;', '- **Broad controller decryption identity** — jeden controller Secret a service account obchádzali environment isolation pri každom renderi.'),
('- production Secret obsahoval `pv-42`;', '- **Materialized target zostal na `pv-42`** — Kubernetes object zodpovedal old Git desired state-u pred emergency rotation.'),
('- emergency operator vytvoril `pv-43` a zmenil Secret, ale neexistoval rollout trigger;', '- **Manual target patch bez authoritative transitionu** — `pv-43` sa objavil iba v live objecte a controller ho pri ďalšom reconcile považoval za drift.'),
('- running Pods používali environment variable snapshot `pv-42`;', '- **Pods držali startup snapshot `pv-42`** — target Secret update nemenil process environment a bez rollout-u nevznikla consumer convergence.'),
('- provider revokoval `pv-42` pred consumer convergence;', '- **Predčasná provider revocation** — old credential prestala fungovať skôr, než telemetry potvrdila, že všetky Pods používajú `pv-43`.'),
('- Flux health check videl healthy Deployment a existujúci Secret;', '- **Incomplete health oracle** — readiness dokazovala available Pods a Secret object, nie loaded credential generation ani provider authentication.'),
('- LaunchPad nemal loaded-secret-generation signal.', '- **Chýbajúca generation telemetry** — portal nemohol rozlíšiť materialized `pv-43` od process-loaded `pv-42` a oznámil false success.'),
]: repl(old, new)

path.write_text(text, encoding='utf-8', newline='\n')
