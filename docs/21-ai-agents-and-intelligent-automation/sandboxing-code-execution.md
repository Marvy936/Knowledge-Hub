# Sandboxing a code execution

Code execution mení agentický systém z textového rozhodovania na runtime schopný vytvárať procesy, čítať a zapisovať súbory, komunikovať po sieti a spotrebúvať host resources. Sandbox preto nie je „bezpečný container“, ale explicitná trust boundary s threat modelom, isolation mechanismami, resource policy, lifecycle a authoritative evidence o tom, čo bolo procesu skutočne dostupné.

Táto kapitola pokračuje v incidente `AGENT-SEC-04`. Code specialist dostal repository workspace, cloud credential v environment variable, writable home directory, Docker socket a unrestricted outbound network. Malicious issue content presvedčil model, aby vytvoril diagnostický script, ktorý prečítal `.env`, zavolal cloud metadata endpoint a odoslal výstup cez legitímny HTTP tool. Nebol potrebný kernel escape: sandbox bol nakonfigurovaný tak široko, že útok zostal v povolených hraniciach.

Nosný lifecycle je:

```text
exact execution subject a untrusted inputs
→ threat model a isolation tier
→ immutable image/runtime generation
→ filesystem, process, syscall a device policy
→ network a credential boundary
→ CPU, memory, time, I/O a process quotas
→ code materialization a dependency policy
→ isolated execution a runtime telemetry
→ output validation a controlled export
→ teardown, secret cleanup a residual-state proof
→ escape, exfiltration a second-operation acceptance
```

## 1. Sandbox chráni boundary, nie correctness

Sandbox obmedzuje, kam sa škodlivý alebo chybný kód dostane. Nezaručuje, že kód vypočíta správny výsledok, nepoškodí dáta vo svojom writable priestore alebo nezneužije legitímne dostupný network endpoint.

Preto sa izolácia kombinuje s tool authorization, data classification, output validation a business read-backom. „Proces skončil exit code 0 v sandboxe“ nie je dôkaz správnosti ani bezpečnosti výsledku.

## 2. Threat model

Threat model určuje, či kód pochádza od trusted developera, LLM generation, používateľa, retrieved repository alebo third-party dependency. Čím menej dôveryhodný source a čím citlivejšie host data, tým silnejšia isolation a menší exposed surface sú potrebné.

Model musí explicitne zahŕňať kernel escape, runtime/VMM exploit, credential theft, data exfiltration, resource exhaustion, cross-tenant leakage, supply-chain execution, side channels a residual state. Bez tohto zoznamu sa „sandboxed“ stáva marketingovým labelom bez acceptance hranice.

## 3. Exact execution subject

Každý run zaznamenáva code digest, source lineage, runtime image digest, sandbox implementation a generation, policy bundle, tenant, mounts, network profile a resource limits. Human-readable job name nestačí na reprodukciu alebo incident analýzu.

```yaml
execution_manifest:
  execution_id: exec-2049-17
  operation_id: checkout-incident-2049
  code_digest: sha256:4aa1...
  source: generated-from/repository-issue-8831
  image: registry.example.com/agent-python@sha256:91ef...
  sandbox:
    type: gvisor
    runtime_class: runsc-v202608
  policy: code-sandbox/restricted-v14
  tenant: retail-eu
```

Ak image tag alebo runtime class resolve-ne inú generation, výsledok nepatrí schválenému execution subjectu.

## 4. Isolation tiers

Nie každý workload potrebuje rovnakú technológiu. Trusted build step môže bežať v hardened containeri, untrusted generated code v userspace-kernel sandboxe a hostile multi-tenant code v microVM alebo dedicated host boundary.

Selection má byť policy decision založené na source truste, data sensitivity, required syscalls, devices, networke a tenancy. Performance preference nesmie silent znížiť isolation tier pri fallbacku.

## 5. Native process nie je sandbox

Spustenie subprocessu pod rovnakým OS userom oddeľuje lifecycle, ale neposkytuje silnú filesystem, network ani kernel boundary. Process môže čítať všetko, čo môže parent, dediť environment a file descriptors a signalovať alebo debugovať sibling processes podľa host permissions.

Native execution je vhodné iba pre trusted code s explicitným host hardeningom. Agent-generated alebo retrieved code sa nepovažuje za trusted len preto, že prešlo syntax checkom.

## 6. Container boundary

Container používa host kernel a izoluje namespaces, cgroups, mounts a capabilities. Pri správnej konfigurácii významne znižuje exposure, ale workload stále komunikuje s rovnakým kernelom a allowed syscall môže obsahovať exploitable path.

Container preto nie je automaticky dostatočný pre hostile multi-tenant code. Privileged mode, host namespaces, broad capabilities alebo mounted Docker socket môžu prakticky odstrániť väčšinu izolácie.

## 7. User namespaces

User namespace mapuje UID/GID v containery na odlišné, menej privilegované host identities. Proces môže vyzerať ako root v sandboxe, no na hoste zostáva unprivileged a tým znižuje následky niektorých escape paths.

Mapping a filesystem ownership musia byť overené na loaded runtime. Deklarovaný `hostUsers: false` alebo rootless flag bez node/runtime podpory nie je účinný control.

## 8. Seccomp

Seccomp obmedzuje syscall surface, ktorý proces môže volať. Default runtime profile je lepší než unconfined execution, ale allowed syscalls stále môžu obsahovať chyby a custom profil sa musí udržiavať pri zmene aplikácie.

Kubernetes dokumentácia odporúča default seccomp profil a pri potrebe silnejšej izolácie sandbox typu gVisor. Privileged container môže seccomp úplne obísť, preto policy musí zakázať privilege escalation a overiť loaded profile.

## 9. Linux capabilities

Linux capabilities rozdeľujú časť root privilege na menšie jednotky. Sandbox začína s drop-all a pridáva iba konkrétnu capability, ak ju workload preukázateľne potrebuje.

`CAP_SYS_ADMIN` je broad a často signalizuje nesprávnu architektúru. Capability requirement sa nesmie riešiť privileged containerom bez threat review a alternate designu.

## 10. AppArmor a SELinux

Mandatory access control obmedzuje filesystem, process a ďalšie operácie podľa loaded profilu alebo labelu. Profil musí byť prítomný na node a enforcement status sa musí overiť; chýbajúci profil nesmie viesť k silent unconfined fallbacku.

Policy je defense-in-depth, nie jediná boundary. Attack v povolenom path alebo nesprávne označený volume môže stále sprístupniť citlivé dáta.

## 11. gVisor

gVisor presúva veľkú časť Linux system interface do per-sandbox userspace application kernelu a minimalizuje priame interakcie workloadu s host kernelom. Jeho security model explicitne uvádza, že sandbox nezastavuje všetky side channels, vyššie vrstvy ani resource exhaustion bez host cgroups a network policy.

To je dôležitá mentálna hranica: gVisor znižuje kernel attack surface, ale súbory, network a data, ktoré sandbox dostane, zostávajú dostupné kompromitovanému workloadu. Runtime class a platform generation sa preto pinujú a kombinujú s no-secret/no-egress policy.

## 12. MicroVM

Firecracker a podobné microVMs používajú hardware virtualization a samostatný guest kernel pri menšom device modeli než všeobecná VM. Firecracker threat model považuje guest vCPU threads za malicious a odporúča ďalšie vrstvy ako jailer, seccomp, namespaces, cgroups a minimal devices.

MicroVM neposkytuje automatický network firewall. Firecracker výslovne ponecháva egress filtering host platforme, takže guest s povolenou sieťou môže exfiltrovať všetko, čo v guestovi prečíta.

## 13. Dedicated host

Najcitlivejší alebo nekompatibilný workload môže vyžadovať dedicated host, node pool alebo hardware partition. Tým sa znižuje cross-tenant a shared-kernel risk, no stále zostáva management plane, firmware, network a storage boundary.

Dedicated infrastructure je drahšia a pomalšia, preto musí mať jasné admission criteria. Nemá sa používať ako výhovorka na broad credentials alebo uncontrolled egress.

## 14. Sandbox manifest

Isolation konfigurácia je immutable alebo versioned artifact, ktorý policy schváli pred execution. Manifest obsahuje runtime, image, user mapping, capabilities, seccomp/AppArmor/SELinux, mounts, devices, network, secrets, quotas a export rules.

```yaml
sandbox_policy:
  id: code-sandbox/restricted-v14
  run_as_non_root: true
  user_namespace: required
  privileged: false
  allow_privilege_escalation: false
  capabilities:
    drop: [ALL]
  seccomp: RuntimeDefault
  root_filesystem: read_only
  devices: []
  network:
    mode: none
  mounts:
    - source: input-snapshot
      target: /workspace/input
      read_only: true
    - source: scratch
      target: /workspace/tmp
      read_only: false
  secrets: none
```

Admission controller odmietne configuration, ktorá nevie splniť required field. Silent downgrade z `network:none` na default bridge je security failure.

## 15. Immutable runtime image

Sandbox image sa referencuje digestom, nie mutable tagom. Image obsahuje iba potrebný runtime a packages a neobsahuje cloud CLI credentials, SSH keys, package-manager tokens ani organization CA private material.

SBOM a signature pomáhajú overiť provenance, ale nepreukazujú runtime isolation. Loaded image digest, runtime binary a policy generation sa zaznamenajú pri každom execution.

## 16. Read-only root filesystem

Read-only root obmedzuje persistence a modifikáciu runtime binaries. Writable priestory sa vytvoria explicitne ako ephemeral scratch alebo bounded output volumes.

Aplikácia, ktorá potrebuje zapisovať do `/tmp`, nemá dostať writable celý root. Mount size, inode count a executable flag sa definujú samostatne.

## 17. Input snapshot

Repository alebo document inputs sa mountujú ako immutable snapshot s digestom. Sandbox nesmie počas execution meniť source, ktorý neskôr audit považuje za pôvodný input.

Ak workload potrebuje experimentovať so súbormi, vytvorí copy-on-write working tree. Export diffu sa validuje voči input digestu a povoleným paths.

## 18. Writable workspace

Writable workspace je operation-scoped a tenant-isolated. Má quota, noexec tam, kde sa kód nemá spúšťať, a cleanup policy po terminal outcome alebo retention intervale.

Shared cache môže byť supply-chain a cross-tenant path. Package cache, compiler cache a model artifacts potrebujú content-addressed identity, ownership a poisoning controls.

## 19. Host mounts

Host home, `/var/run/docker.sock`, SSH agent socket, Kubernetes service-account token, cloud metadata proxy a orchestration control socket sú forbidden default. Ich mount často dáva sandboxu nepriamu host alebo cluster authority.

Docker socket umožňuje vytvoriť privileged sibling container alebo mount host filesystem. Taká configuration sa nepovažuje za sandbox, aj keď samotný process beží non-root.

## 20. Device access

GPU, block device, USB, TUN/TAP a `/dev/kvm` rozširujú attack surface a môžu obísť očakávanú isolation. Device sa pridá iba pre explicitný workload class a s dedicated runtime policy.

GPU workload môže vyžadovať odlišný isolation tier alebo node pool. Fallback na unsandboxed execution pri nekompatibilite je zakázaný bez human decisionu.

## 21. Network default deny

Code execution začína bez networku. Ak task potrebuje dependency fetch alebo API, egress sa povoľuje cez destination allowlist, protocol/port policy, DNS control, proxy a byte/request budgets.

Read a write network capabilities sa oddeľujú. Stiahnutie approved package z registry nevyžaduje možnosť POST na arbitrary internet origin.

## 22. DNS a redirects

Hostname allowlist nestačí, ak DNS môže resolve-nuť private addresses alebo endpoint redirectne na iný origin. Proxy overuje resolved IP class, TLS identity, redirect chain a request method.

SSRF protections blokujú metadata endpoints, loopback, link-local a internal control planes, pokiaľ nie sú explicitne required. DNS answer a destination identity sa logujú bez sensitive payloadu.

## 23. Credentials mimo sandboxu

Cloud, repository a database credentials sa nevkladajú do environmentu sandboxu. Privileged operácia ostáva za narrow external tool boundary, ktorá dostáva structured request a sama používa opaque credential.

Ak code potrebuje package token, používa scoped one-time proxy alebo pre-snapshotted dependencies. Token sa nesmie objaviť v command line, environment dump, `/proc`, shell history ani output archive.

## 24. Environment variables

Environment je explicitný allowlist. Host environment sa nekopíruje wholesale, pretože môže obsahovať credentials, proxy settings, debug flags alebo paths k sensitive sockets.

Každá variable má ownera a sensitivity. Diagnostic tool môže vypísať allowlisted non-secret values, ale runtime redaction nemá byť jedinou ochranou pred secret inheritance.

## 25. Dependency installation

`pip install`, `npm install`, build scripts a package post-install hooks sú code execution. Dependency source, version, digest, signature a allowed lifecycle scripts sa musia kontrolovať rovnako ako generated code.

Preferované sú prebuilt immutable environments alebo internal mirror s lockfile enforcement. Dynamic install z modelom navrhnutého URL je supply-chain boundary a vyžaduje separate policy.

## 26. Compiler a interpreter controls

Allowed languages a interpreters sa pinujú. Arbitrary native compilation môže rozšíriť syscall a device requirements a vytvoriť payloady, ktoré obchádzajú vyššie-level policy.

Runtime môže povoliť Python bez FFI, WebAssembly s capability-based imports alebo restricted shell subset podľa threat modelu. Language sandbox sám o sebe nestačí, ak host process má broad filesystem a network access.

## 27. Process limits

Sandbox má maximum processes/threads, open files, stack, memory mappings a execution depth. Fork bomb alebo recursive agent-spawn nesmie vyčerpať host ani queue.

PID limit sa kombinuje s CPU, memory a wall-clock budgetom. Kill po limite sa zaznamená ako resource termination, nie ako model failure alebo clean completion.

## 28. CPU a memory

CPU quota, memory hard limit a OOM behavior sú per execution. Shared-node oversubscription nesmie umožniť jednému tenantovi ovplyvniť latency alebo dostupnosť iných sandboxov bez detekcie.

Memory limit zahŕňa process, page cache a príslušné runtime overheady podľa platformy. OOM-killed job môže zanechať partial output, ktorý sa nesmie automaticky publikovať.

## 29. Wall-clock a durable timers

Timeout sa meria monotonic clockom mimo sandboxu. Workload nemôže predĺžiť vlastný deadline zmenou system time alebo blokovaním heartbeat procesu.

Long-running task checkpointuje iba non-secret state a output digests. Resume vytvorí nový sandbox s current policy a nepoužíva stale credential alebo network lease.

## 30. I/O a storage quotas

Disk bytes, inodes, read/write bandwidth a output count majú limity. Malicious code môže inak vyplniť filesystem množstvom malých súborov alebo zablokovať shared storage intenzívnym I/O.

Quota breach vedie k controlled termination a evidence o consumed resources. Partial archive sa označí incomplete a neexportuje ako validný result.

## 31. Output contract

Sandbox nepublikuje ľubovoľný filesystem. Exportuje explicitné artifacts podľa path, media type, size, schema a sensitivity rules.

```yaml
allowed_outputs:
  - path: /workspace/out/report.json
    media_type: application/json
    max_bytes: 1048576
    schema: diagnostic-report/v3
  - path: /workspace/out/patch.diff
    media_type: text/x-diff
    max_bytes: 524288
    requires_review: true
```

Symlinks, device files, sockets, hardlink escapes a path traversal sa odmietnu pred exportom.

## 32. Output scanning

Output sa považuje za untrusted aj po úspešnom execution. Validator kontroluje schema, secret patterns, malware, executable content, archive expansion, policy violations a provenance metadata.

Generated patch navyše prejde code review a tests mimo sandboxu. Report s tvrdením „fix applied“ sa porovná s authoritative repository alebo runtime read-backom.

## 33. Terminal state

`completed` znamená iba to, že sandbox lifecycle skončil podľa orchestratora. Acceptance oddeľuje process exit, output validation, artifact publication a business outcome.

Timeout, OOM, policy violation, manual cancel a sandbox infrastructure failure sú rozdielne states. Ich zliatie do `failed` komplikuje retry a môže viesť k opakovaniu side effectu.

## 34. Teardown

Teardown odpojí mounts, zruší network namespace, ukončí processes, revokuje temporary handles a odstráni scratch podľa retention policy. Cleanup je samostatný observable phase a môže zlyhať.

Sandbox sa nevracia do poolu, kým isolation layer nepotvrdí reset relevantného state. Reuse bez scrubbingu môže preniesť files, memory-backed caches alebo credentials medzi operations.

## 35. Snapshoty a reuse

MicroVM alebo container snapshot môže zrýchliť startup, ale snapshot files sú trusted control-plane inputs a môžu obsahovať memory, tokens, random state alebo tenant data. Base snapshot vzniká pred vložením secrets a per-run mutable state.

Resume snapshotu potrebuje uniqueness a key regeneration. Clone s rovnakou machine identity alebo cached credentialom môže vytvoriť identity collision.

## 36. Monitoring

Telemetry zachytáva sandbox policy digest, runtime/image generation, mounts, network decisions, resource usage, denied syscalls, policy violations, process tree, output export a teardown. Payloady a secrets sa minimalizujú alebo hashujú podľa data policy.

Host monitoring musí zostať mimo sandbox authority. Workload nesmie vypnúť audit, meniť log destination alebo označiť vlastný violation ako benign.

## 37. Kill switch

Platforma vie zastaviť konkrétny execution, agent release, sandbox runtime generation alebo celý mutation class. Kill switch zároveň odoberie network a credential leases a označí output ako untrusted.

`SIGKILL` procesu nemusí stačiť, ak child VM, network job alebo downstream task pokračuje. Kill flow sleduje descendant graph a potvrdí termination na každej vrstve.

## 38. Incident `AGENT-SEC-04`

Code specialist dostal repository issue ako prompt context a mohol písať shell script. Sandbox bežal v native container runtime s writable rootom, host Docker socketom, production cloud tokenom a internet egressom. Script načítal environment, spustil sibling container s host mountom a odoslal credential metadata na attacker endpoint.

Platforma hlásila „sandbox job completed“, pretože žiadny syscall neporušil profil. Z pohľadu configured permissions sa útok správal legitímne.

Správny tok mal byť:

```text
untrusted issue marked as data
→ generated code review and digest
→ restricted sandbox admission
→ immutable read-only input snapshot
→ no credentials, no Docker socket, no network
→ bounded execution and output schema
→ secret/executable/path validation
→ reviewed artifact export
→ teardown and residual-state proof
```

Containment zastavil affected runtime class, zrušil cloud tokens a izoloval hosts s mounted control sockets. Recovery prešla na gVisor pre generated code, default-deny egress a external privileged tools.

## 39. Failure hypotheses

Sandbox incident sa diagnostikuje od declared manifestu po loaded host state. Najprv sa overí, či scheduler skutočne použil požadovaný runtime class, image digest, user namespace, seccomp/MAC profil, mounts a network mode. Deklarácia v job requeste nestačí, ak admission alebo node fallback zmenili effective configuration.

Druhá vrstva sleduje process, filesystem, credential a network exposure. Útok nemusí znamenať escape; často stačí, že sandbox legitímne dostal Docker socket, service-account token alebo unrestricted egress. Napokon sa kontroluje output a teardown, aby sa zistilo, či nebezpečný artifact alebo residual state prežil terminal job.

- **Runtime downgrade** — scheduler použil native container namiesto required gVisor alebo microVM generation.
- **Privileged override** — `privileged`, host namespace alebo `CAP_SYS_ADMIN` znefunkčnili očakávané controls.
- **Profile not loaded** — seccomp, AppArmor alebo SELinux deklarácia sa na node neuplatnila a workload bežal unconfined.
- **Mount exposure** — host path, Docker socket, SSH agent, cloud config alebo cudzie tenant data boli prístupné sandboxu.
- **Credential inheritance** — parent environment alebo mounted token poskytli production authority code procesu.
- **Egress gap** — network policy povoľovala arbitrary DNS, redirects, metadata endpoint alebo outbound POST.
- **Resource exhaustion** — procesy, memory, disk, inodes alebo I/O prekročili intended tenant budget a ovplyvnili host.
- **Supply-chain execution** — dependency install alebo build hook spustili neapproved code mimo očakávaného digestu.
- **Output escape** — symlink, archive, executable alebo secret prešli export validatorom.
- **Residual-state leak** — reused sandbox, snapshot, cache alebo volume obsahovali dáta predchádzajúcej operácie.

Každá hypotéza sa testuje proti scheduler/admission recordu, node runtime telemetry, mount a namespace inventory, process tree, network flows, credential broker logu, output validatoru a teardown evidence. Exit code a model explanation neposkytujú effective isolation proof.

## 40. Containment

Pri sandbox incidente sa zastaví affected runtime/image/policy generation a zakáže reuse. Network sa odpojí, credentials a sessions sa revokujú a hosts s možným escape alebo control-socket exposure sa izolujú.

Artifacts zostanú quarantined a nepublikujú sa. Memory/disk snapshots a logs sa zachovajú podľa forenznej policy bez ďalšieho spúšťania payloadu na bežnom analyst hoste.

## 41. Recovery

Recovery opraví admission, runtime pinning, user/capability/profile controls, mounts, credential separation, network policy, quotas, output validation a teardown. Host alebo node sa rebuildne, ak nie je možné preukázať integrity po možnom escape.

Known-good test image overí loaded controls a malicious corpus skúsi filesystem, network, process, device, metadata, secret a output escape paths. Produkčný návrat vyžaduje current runtime telemetry a business workflow acceptance, nie iba unit test manifestu.

## 42. Positive acceptance

Pozitívny test spustí approved code digest v required sandbox generation, prečíta iba immutable input, zapisuje do bounded scratch, nemá credentials ani network a exportuje validný schema artifact. Loaded runtime, profiles, quotas a teardown sú potvrdené telemetry.

Artifact následne prejde independent validation. Business workflow ho nepoužije, kým nie je explicitne accepted.

## 43. Forbidden acceptance

Zakázaný test skúsi host path, Docker socket, metadata endpoint, arbitrary DNS/HTTP, privilege escalation, forbidden syscall, fork bomb, disk fill, secret print a symlink export. Každá cesta musí byť blokovaná alebo bounded bez cross-tenant či host impactu.

Fallback test odstráni gVisor node availability. Scheduler musí job odmietnuť alebo čakať; nesmie silent použiť slabší runtime.

## 44. Recovery acceptance

Recovery test zabije sandbox počas execution, reštartuje node, ponechá stale volume a zmení runtime policy. Resume musí vytvoriť fresh sandbox, overiť input digest a nepoužiť starý scratch, credential ani network state.

Cleanup musí dokázať termination descendants, odpojenie mounts, zrušenie leases a nepoužiteľnosť exported partial outputs.

## 45. Second-operation acceptance

Nová operation dostane nový execution ID, fresh workspace, process namespace, network identity a output directory. Nesmie vidieť files, caches, environment ani telemetry payload predchádzajúceho runu mimo explicitne approved immutable base artifacts.

Tým sa overí tenant a operation isolation aj pri pooling alebo snapshot optimization.

## 46. Zhrnutie

Sandboxing je vrstvený control nad runtime, kernel boundary, user/capabilities, syscalls, MAC, mounts, devices, network, credentials, resources, outputs a teardownom. Žiadna jedna technológia neodstraňuje potrebu ostatných vrstiev.

Najdôležitejšia otázka nie je „bežal kód v containery?“, ale „ktorý exact code a runtime generation, s akým loaded isolation manifestom, mal prístup ku ktorým resources a dokázal po execution exportovať alebo zanechať aký state?“

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Least privilege pre tools a credentials](least-privilege-tools-credentials.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Prompt injection cez tools a retrieved content →](prompt-injection-tools-retrieved-content.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
