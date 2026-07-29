from pathlib import Path

path = Path("docs/16-gitops-and-platform-engineering/gitops-secrets.md")
text = path.read_text(encoding="utf-8")

def add(heading: str, prose: str, marker: str) -> None:
    global text
    if marker in text:
        return
    needle = heading + "\n\n"
    if needle not in text:
        raise SystemExit(f"Missing heading: {heading}")
    text = text.replace(needle, needle + prose.rstrip() + "\n\n", 1)

add(
    "## 1. Dominantný model",
    """Secret lifecycle prechádza viacerými authority a plaintext boundaries. Model preto sleduje nielen to, kde je value deklarovaná, ale aj kto ju smie vytvoriť, decryptovať alebo načítať a kedy je stará generation skutočne nepoužiteľná.

Každá transition vytvára odlišný failure mode: Git môže obsahovať správny ciphertext, controller nemusí dostať KMS access, target Secret môže zostať stale a running process môže držať starú value aj po úspešnom update-e Kubernetes objectu.""",
    "Secret lifecycle prechádza viacerými authority",
)
add(
    "## 2. Exact secret subject",
    """Exact subject oddeľuje logical secret purpose od konkrétnej credential generation a jej consumers. Bez neho sa provider version, Git payload, Kubernetes Secret a process-loaded value môžu javiť ako jeden stav, hoci každý z nich má inú identity a lifecycle.

Rozmery subjectu spolu určujú, kto je autorita, kde môže vzniknúť plaintext, aký je tenant a environment scope a podľa čoho sa rotation považuje za dokončenú. Vynechanie ktoréhokoľvek rozmeru vytvára blind spot pri revocation alebo incident recovery.""",
    "Exact subject oddeľuje logical secret purpose",
)
add(
    "## 4. Prečo base64 nie je ochrana",
    """Base64 mení textovú reprezentáciu bytes, nie ich confidentiality. Reader nepotrebuje secret key ani permission k ďalšiemu systému; stačí mu repository content a štandardný decoder.

Riziko sa násobí tým, že Git a delivery tooling vytvárajú viac trvalých kópií. Každý clone, diff, cache alebo export rozširuje reader graph a môže prežiť odstránenie value z current branch-e.""",
    "Base64 mení textovú reprezentáciu bytes",
)
add(
    "## 5. Dva hlavné GitOps modely",
    """Oba modely versionujú secret intent, ale authority a availability umiestňujú na inú boundary. Encrypted-in-Git drží ciphertext spolu s application desired state-om a potrebuje decryption key pri reconciliation; external reference drží value v providerovi a potrebuje provider identity a availability pri refreshi.

Voľba preto nie je súboj nástrojov. Je to rozhodnutie o reprodukovateľnosti, runtime dependency, rotation cadence, audit authority a blast radius, pričom v oboch prípadoch treba samostatne vyriešiť Kubernetes a workload plaintext lifecycle.""",
    "Oba modely versionujú secret intent",
)
add(
    "### Encrypted secret value v Git-e",
    """Ciphertext je súčasťou immutable desired generation, takže Git diff a rollback dokážu identifikovať jeho zmenu bez zverejnenia plaintextu. Decryption však presúva vysokú dôveru na controller identity a key management: kto môže otvoriť payload, môže potenciálne čítať všetky secrets vo svojom scope.

Versioning zlepšuje audit a offline reproducibility, ale nemení fakt, že plaintext vzniká v controller memory a zvyčajne aj v Kubernetes API. Preto sa repository encryption musí doplniť runtime RBAC, key rotation, redaction a consumer convergence.""",
    "Ciphertext je súčasťou immutable desired generation",
)
add(
    "### External secret reference v Git-e",
    """External-reference model ponecháva value a authoritative versions v secret providerovi. Git deklaruje retrieval policy a target mapping, zatiaľ čo controller alebo workload resolve-ne current alebo pinned provider generation pomocou runtime identity.

Model centralizuje rotation a revocation, ale pridáva distributed consistency problém. Provider, ExternalSecret status, Kubernetes Secret a running process môžu každý ukazovať inú generation a mutable provider alias môže zmeniť effective value bez nového Git commit-u.""",
    "External-reference model ponecháva value",
)
add(
    "## 8. Flux SOPS decryption",
    """SOPS decryption je samostatná trust transition medzi source artifactom a final manifestom. Controller najprv musí získať workload identity, KMS alebo age mechanismus musí autorizovať otvorenie data key-u a až potom môže build pokračovať s plaintextom v memory.

Failure list preto pokrýva odlišné boundaries: cryptographic identity, cloud authorization, availability, encryption selection, logging a target placement. Úspešný Git fetch nevylučuje ani jednu z nich.""",
    "SOPS decryption je samostatná trust transition",
)
add(
    "## 11. ExternalSecret refresh policies",
    """Refresh policy určuje, ktorá udalosť premení provider state na nový target Secret. Nejde iba o interval alebo optimalizáciu API volaní; policy definuje consistency, audit a promotion model medzi mutable external authority a Git-managed declaration.

Periodic sleduje provider automation, OnChange vyžaduje explicitný desired-state trigger a CreatedOnce chráni initial bootstrap value pred nečakaným prepisom. Každý režim má preto iný stale-value a recovery behavior.""",
    "Refresh policy určuje, ktorá udalosť",
)
add(
    "## 12. Target creation a deletion semantics",
    """Target policy je ownership contract nad Kubernetes Secretom. Určuje, či operator vlastní celý object alebo iba vybrané keys, ako reaguje na missing provider property a či deletion desired declarationu odstráni aj materialized credential.

Tieto decisions menia availability aj security. Fail-open môže ponechať revoked value, fail-closed môže spôsobiť outage a shared target s viacerými writers môže oscillovať bez jasného authoritative ownera.""",
    "Target policy je ownership contract",
)
add(
    "## 14. Workload identity a secret-zero problem",
    """Workload identity nahrádza long-lived bootstrap key krátkodobým credentialom odvodeným z overeného service-account subjectu. Bez úzkej trust policy by však iba presunula broad privilege z Kubernetes Secretu do cloud role.

Issuer, audience, subject, provider resource scope a TTL sa preto vyhodnocujú ako jeden chain. Audit musí vedieť spojiť cloud decrypt alebo read request s konkrétnou controller reconciliation a tenant boundary.""",
    "Workload identity nahrádza long-lived bootstrap key",
)
add(
    "## 15. Kubernetes Secret boundary",
    """Po materialization sa ochrana presúva z Git/KMS modelu na Kubernetes control a node plane. Secret môže byť encrypted v etcd a zároveň čitateľný broad API principalom, node administratorom alebo actorom s `exec` do workloadu.

Jednotlivé controls preto chránia odlišné paths: RBAC chráni API, etcd encryption storage bytes, namespace a admission target placement a process isolation runtime consumption. Žiadna z týchto vrstiev sama neposkytuje end-to-end confidentiality.""",
    "Po materialization sa ochrana presúva",
)
add(
    "## 19. Logging, diff a observability",
    """Secret observability musí dokazovať generation flow bez reprodukovania citlivej value. Provider version IDs, ciphertext digests, resource versions a operation identities umožňujú koreláciu, ale neposkytujú credential použiteľný na autentizáciu.

Safe a unsafe fields tvoria boundary contract pre controllery, CI, portal aj support tooling. Redaction po persistencii je neskoro; plaintext sa nesmie dostať do pôvodného log eventu, rendered diffu ani error response-u.""",
    "Secret observability musí dokazovať generation flow",
)
add(
    "## 20. Multi-tenancy",
    """Secret multi-tenancy je end-to-end property. Namespace filter v portali alebo Kubernetes RBAC nestačia, ak shared controller role môže decryptovať všetky KMS keys alebo načítať ľubovoľný provider path.

Tenant subject musí zostať rovnaký v Git declaration, decryption/retrieval identity, provider authorization, target namespace aj workload binding. Slabá jediná boundary môže z trusted controllera urobiť confused deputy.""",
    "Secret multi-tenancy je end-to-end property",
)
add(
    "## 21. Backup, restore a disaster recovery",
    """Recovery musí obnoviť celý secret access graph, nie iba declarative YAML. Potrebný je desired payload alebo reference, key/provider availability, workload identity, target materialization a functional consumer test.

Restore zároveň nesmie automaticky reaktivovať historickú credential. Provider authority a incident context určia, či old generation zostáva validná, musí zostať revoked alebo sa nahradí úplne novou generation.""",
    "Recovery musí obnoviť celý secret access graph",
)
add(
    "### Encrypted-in-Git",
    """Pri encrypted-in-Git modeli je retained Git history nepoužiteľná bez decryption key-u, controller trust a target bootstrapu. Tieto dependencies tvoria jeden recovery graph a musia sa testovať spolu.

Recovery proof nekončí pri úspešnom decrypt-e. Test workload musí dostať materialized value, načítať ju a úspešne sa autentizovať bez toho, aby evidence alebo logs obsahovali plaintext.""",
    "Pri encrypted-in-Git modeli je retained Git history",
)
add(
    "### External provider",
    """External-provider restore závisí od provider version retention a od obnovenia presne scoped workload identity. Git reference bez jedného z týchto predpokladov zostane iba nefunkčnou deklaráciou.

Provider audit musí potvrdiť, či restore candidate je ešte validný. Obnovenie revoked historical value bez explicitného decisionu by zmenilo security incident na recovery-induced credential reuse.""",
    "External-provider restore závisí od provider version retention",
)
add(
    "### Redesign",
    """Redesign obnovuje rotation ako jednu authoritative state machine. Provider vytvorí new generation, GitOps desired state ju identifikuje, controller ju materializuje a workload telemetry preukáže consumer convergence skôr, než provider zruší old generation.

Tým sa odstráni dual-writer oscillation medzi manual patchom a Fluxom. Emergency operátor už nemení iba target Secret; mení alebo pozastaví authoritative flow a recovery sa uzavrie negative testom revoked credentialu.""",
    "Redesign obnovuje rotation ako jednu authoritative state machine",
)
add(
    "## 23. GitOps secret acceptance verdict",
    """Acceptance musí prepojiť confidentiality, authority a liveness. Secret môže byť správne zašifrovaný, ale nepoužiteľný pre workload; môže byť správne materializovaný, ale už revoked providerom; alebo môže fungovať, no byť čitateľný cudzím tenant principalom.

Verdict preto pokrýva repository a KMS boundary, target materialization, process-loaded generation, rotation, revocation a restore. Platí iba pre exact environment, tenant, provider version a consumer cohort.""",
    "Acceptance musí prepojiť confidentiality",
)
add(
    "## 24. Troubleshooting flow",
    """Troubleshooting začína pri provider authority, pretože tá rozhoduje, ktorá generation je aktívna alebo revoked. Potom sleduje desired reference, controller authorization, materialization a consumer loading, až kým nájde prvú boundary s odlišnou generation alebo failed operation.

Po náprave nestačí pozrieť Kubernetes Secret. Každý workload cohort musí reportovať new loaded generation, provider audit musí potvrdiť jej použitie a old generation musí zlyhať podľa revocation contractu.""",
    "Troubleshooting začína pri provider authority",
)

path.write_text(text, encoding="utf-8", newline="\n")
