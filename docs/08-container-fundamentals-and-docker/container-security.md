# Container security

Container security je effective trust lifecycle od source-u a artifactu až po process authority, host-kernel exposure, network/storage access, observation, patchovanie a incident recovery. Zoznam flags nie je security model: rozhoduje ich kombinácia nad konkrétnym workload subjectom.

Dominantný lifecycle:

```text
workload threat model a data/tenant classification
→ trusted source/build/image subject
→ registry evidence a deployment eligibility
→ effective runtime policy construction
→ process identity, authority a filesystem/network/storage access
→ host/runtime isolation boundary
→ continuous observation a vulnerability reassessment
→ bounded incident containment
→ rebuild, credential rotation, redeploy a adjacent-scope verification
```

Security success neznamená iba „container beží ako non-root“ alebo „scanner je green“. Znamená, že exact runtime subject dodržiava schválenú authority a exposure boundary a incident možno bezpečne vyšetriť a odstrániť bez neauditovaného live patchu.

## 1. Atlas security subject

Atlas Payments API release `3.13.0`:

```text
source commit: C417
platform manifest: MAMD313
provenance: PROV313
signature: SIG313
SBOM: SBOM313
vulnerability verdict generation: VDB-2026-07-27
runtime node: node-12
container ID: CT-PAY-07
process UID/GID: 10001:10001
capabilities: NET_BIND_SERVICE
no_new_privs: true
seccomp profile: atlas-default-v7
LSM profile/label: atlas-payments-prod-v4
rootfs: read-only
writable mounts: /tmp, /var/run/atlas
network policy: NP-552
workload identity: WI-PAY-PROD-07
secret epoch: SE02
resource policy: RP-88
```

Security verdict musí viazať artifact evidence na effective runtime state, nie iba na deployment YAML.

## 2. Threat model

Začni assets, actors a boundaries:

```text
assets:
payment data, credentials, signing keys, node/runtime authority, adjacent workloads

threats:
vulnerable app, malicious dependency/image, compromised builder,
stolen registry identity, container escape, lateral movement,
resource DoS, secret exfiltration, privileged insider, policy misconfiguration

boundaries:
source/build, registry, deployment controller, runtime daemon,
container process, shared host kernel, network, storage, external services
```

Threat model určuje, či shared-kernel container boundary postačuje alebo workload potrebuje dedicated VM, microVM či sandboxed runtime.

## 3. Security subject a evidence inventory

Rekonštruovateľný subject zahŕňa:

- source a build revision;
- builder/execution identity;
- image index a selected platform digest;
- signature, provenance, SBOM a scan reports;
- node kernel/runtime/snapshotter versions;
- generated runtime configuration;
- process UID/GID/groups a capabilities;
- `no_new_privs`, seccomp a LSM policy;
- mounts, devices a runtime-socket exposure;
- network policy a published ports;
- secrets/workload identity;
- cgroup limits;
- policy exceptions a expiration;
- runtime/deployment generation.

Chýbajúca evidence nie je clean pass.

## 4. Source, build a image trust

Artifact trust chain:

```text
reviewed source
→ isolated builder a pinned toolchain
→ controlled dependencies/secrets/network
→ image digest
→ provenance a SBOM
→ scan/policy verdict
→ signature
→ registry publication
```

Build environment má často širší access než runtime. Chráň:

- short-lived scoped credentials;
- secret mounts namiesto build arguments;
- trusted pinned build images/actions;
- isolated workspaces a caches;
- restricted egress;
- complete build-context inventory;
- artifact read-back a provenance verification.

Compromised builder môže vytvoriť validne podpísaný malicious artifact, ak signing policy iba slepo dôveruje builder identity. Trust model potrebuje hardened builder a source/input claims.

## 5. Base image lifecycle

Base image je executable dependency:

```text
publisher/source
+ platform digest
+ package/userspace inventory
+ support/update policy
+ compatibility
```

Digest pinning dáva reprodukovateľnú identity, ale môže zamraziť vulnerability. Potrebuje update workflow:

```text
new trusted base digest alebo advisory
→ rebuild bez source change
→ test/scan/sign
→ deploy successor digest
→ verify runtime
```

Mutable `latest` nie je patch policy.

## 6. SBOM a vulnerability evidence

SBOM inventarizuje components pre konkrétny digest. Nepreukazuje:

- že inventory je complete;
- že component je reachable;
- že artifact je bez malware;
- že runtime configuration je bezpečná;
- že neskoršia CVE nevznikne.

Scan subject:

```text
platform manifest digest
+ scanner/version
+ vulnerability database generation
+ analyzované ecosystems/layers
+ report validity
+ exceptions
```

Risk decision zahŕňa severity, exploitability, reachability, runtime exposure, fix availability, compensating controls a exception expiry.

Continuous reassessment musí korelovať nové advisories s running platform digests.

## 7. Deployment eligibility

Pred runtime create:

```text
exact digest
→ required artifact/evidence inventory
→ signer/provenance policy
→ vulnerability/configuration policy
→ environment/tenant restrictions
→ exception validation
→ eligible alebo denied
```

Policy engine outage, invalid report alebo missing signature nie sú „0 violations“. Majú samostatný fail/incomplete verdict.

Admission/deployment policy nemá dôverovať mutable tagu ani image-supplied claims o vlastnej bezpečnosti.

## 8. Effective runtime policy

Effective state môže vzniknúť z image defaults, deployment spec, daemon defaults, orchestrator policy, user namespace a host configuration.

```text
image config
+ deployment overrides
+ runtime/daemon defaults
+ node security policy
→ generated OCI runtime config
→ kernel-enforced process state
```

Kontroluj generated/effective state, nie iba source manifest.

## 9. Process identity

Preferuj explicitný non-root numeric UID/GID a stable ownership contract.

Non-root znižuje authority iba v kombinácii s:

- filesystem permissions/ACL;
- user namespace mapping;
- capabilities;
- seccomp/LSM;
- mount/device exposure;
- runtime socket absence;
- network/storage credentials.

Non-root process s writable host mountom alebo runtime socketom môže stále ovládnuť host alebo citlivé dáta.

Rootless runtime znižuje default host-daemon authority, ale nemení application vulnerabilities a potrebuje vlastný networking/storage/user-mapping model.

## 10. Capabilities a privilege transitions

Capabilities rozdeľujú root authority. Policy:

```text
drop all
→ pridaj iba konkrétnu operation potrebnú workloadom
```

Každá capability potrebuje ownera, workload use case, test a scope.

Broad capabilities ako `SYS_ADMIN`, `NET_ADMIN`, `SYS_PTRACE` alebo `DAC_OVERRIDE` môžu výrazne oslabiť boundary.

`no_new_privs` zabraňuje novému privilege gain-u cez `execve`, ale neodstraňuje už existujúce capabilities alebo file access.

## 11. Seccomp a LSM

Authorization layers:

```text
syscall exists/support
→ seccomp allow/deny
→ capability/credential check
→ LSM object/operation policy
→ filesystem/network/device-specific check
```

Seccomp zmenšuje syscall surface. SELinux/AppArmor riadi object/operation policy. Jedna vrstva nenahrádza druhú.

Pri `EPERM` alebo `permission denied` zachovaj:

- failing operation/syscall;
- capability sets;
- seccomp verdict/audit;
- SELinux AVC/AppArmor denial;
- path label/profile;
- mount flags a UID mapping.

`unconfined` alebo globálne vypnutie LSM ničí observation aj protection boundary.

## 12. Privileged mode a host authority

Privileged mode môže rozšíriť capabilities, devices a security profiles natoľko, že container boundary prakticky kolabuje.

Osobitne rizikové:

- host root filesystem mount;
- Docker/containerd/CRI socket;
- host PID/network namespace;
- `/dev` alebo raw block devices;
- `CAP_SYS_ADMIN`;
- writable `/proc`/`sysfs`;
- unconfined seccomp/LSM.

Runtime socket často umožní vytvoriť nový privileged container, host mount alebo exec a predstavuje host-admin authority.

Privileged mode nie je diagnostický nástroj.

## 13. Filesystem authority

Secure filesystem model:

```text
read-only image rootfs
+ explicit writable paths
+ least-privilege UID/GID
+ narrow mount sources
+ noexec/nosuid/nodev podľa contractu
+ LSM labels
+ size/cleanup policy
```

Writable paths klasifikuj podľa data sensitivity a persistence. Read-only rootfs nebráni zápisu do volume, tmpfs, host mountu alebo external API.

Secrets nesmú byť baked do layers. Nález secretu vyžaduje rotate/revoke, clean rebuild, old-digest containment a usage audit.

## 14. Device boundary

Device sprístupňuje host kernel subsystem. GPU, KVM, FUSE, block, USB alebo network device potrebuje:

- exact device allowlist;
- driver/kernel risk;
- process permissions/capabilities;
- LSM policy;
- tenant/node placement;
- audit;
- behavior pri reset/failure.

Device plugin alebo helper môže byť privileged component a musí byť súčasť threat modelu.

## 15. Network security

Effective exposure:

```text
application listener
→ namespace/dataplane
→ port publication/load balancer
→ firewall/network policy
→ remote identity/protocol
```

Controls:

- explicit ingress allowlist;
- default-deny east-west podľa platformy;
- egress restrictions;
- metadata-service protection;
- DNS/control-plane/registry/secret paths;
- IPv4/IPv6 parity;
- mTLS alebo workload identity podľa threat modelu.

Port publish na `0.0.0.0` môže obísť reverse proxy alebo expected authentication boundary.

Network location/container name nie sú sufficient identity.

## 16. Workload identity a secrets

Preferuj short-lived federated workload identity pred statickým cloud credentialom.

Identity subject:

```text
workload/environment identity
+ audience
+ scope/permissions
+ token epoch/expiration
+ issuance and use audit
```

Runtime secret path môže viesť cez environment, mounted file/tmpfs, API response, process memory, child process, logs a dumps.

File mount alebo environment injection nie je end-to-end confidentiality. Rotation musí overiť loaded new value a revoke old credential.

## 17. Storage security

Mounted encrypted volume poskytuje plaintext oprávnenému processu. Storage security preto zahŕňa:

- correct data/volume identity;
- read/write access mode;
- writer fencing;
- UID/GID/ACL/LSM;
- secret exclusion z backups;
- encryption keys a restore access;
- host-path exposure;
- mount propagation a flags.

Application container nesmie dostať runtime socket len preto, aby „spravoval volumes“.

## 18. Resource security a availability

CPU, memory, PID a I/O policy obmedzuje denial-of-service blast radius.

Príliš vysoké alebo chýbajúce limits umožnia noisy-neighbor/host exhaustion. Príliš nízke limits môžu spôsobiť:

- cgroup OOM;
- CPU throttling;
- PID exhaustion;
- storage queue collapse;
- restart storm;
- operator bypass security controls počas incidentu.

Security baseline musí byť load-tested a spojený s availability SLO.

## 19. Host a runtime boundary

Shared kernel a privileged daemon robia node kritickou boundary.

Host controls:

- patched minimal OS/kernel/runtime;
- restricted runtime socket/API;
- short-lived admin access;
- LSM/seccomp enforcement;
- audit a runtime event collection;
- node trust/attestation podľa potreby;
- workload separation podľa tenant/risku;
- immutable/recoverable node lifecycle;
- kernel module a device policy.

Containers vo VMs vytvárajú dve boundaries a dva patch lifecycles. Sensitive untrusted workloads môžu potrebovať sandbox/microVM.

## 20. Observability a effective-state verification

Zachytávaj mimo ephemeral containeru:

- source/image/platform digests;
- signature/provenance/scan verdicts;
- generated runtime config;
- process UID/GID/capabilities/`no_new_privs`;
- seccomp a LSM profile/denials;
- mounts/devices/socket exposure;
- network publication/policy;
- cgroup state a OOM/throttling;
- secret/workload identity generation;
- create/start/exec/stop events;
- runtime/admin API access.

Source policy bez effective-state telemetry nevie odhaliť mutation, daemon default alebo emergency bypass.

## 21. Patch a replacement lifecycle

Immutable patch model:

```text
new advisory alebo fixed input
→ rebuild exact source/base/dependencies
→ regenerate SBOM/provenance
→ scan/policy/sign
→ deploy new digest
→ verify effective runtime state a business outcome
→ retire old instances/digest support
```

Ručný package install v live containeri vytvára snowflake state, ktorý zmizne pri replacement-e a scan image-u ho nemusí vidieť.

Host-kernel vulnerability sa neopraví application image rebuildom. Potrebuje node patch/replacement a workload rescheduling.

## 22. Exceptions

Security exception obsahuje:

```text
exact subject a environment
control being bypassed
risk a business reason
owner/approver
compensating controls
expiration
revalidation trigger
removal plan
```

Exception pre `privileged: true` bez scope-u a expiry je nová permanentná security architecture.

## 23. Incident state machine

```text
detect and classify subject
→ contain workload/network/credentials
→ preserve volatile and durable evidence
→ determine host/adjacent blast radius
→ eradicate through trusted rebuild/replacement
→ rotate/revoke identities
→ redeploy verified successor
→ validate business/security outcome
→ close root cause and earlier control
```

Blind `docker rm` môže zničiť volatile evidence. Naopak compromised process nemá zostať aktívny iba kvôli forensics bez containment.

## 24. Worked failure: application fungovala iba privileged

Application nevedela bindovať low port. Operator nastavil privileged mode.

```text
missing narrow NET_BIND_SERVICE authority
→ privileged grants broad capabilities/devices/policy bypass
→ one socket problem becomes host-compromise path
```

Recovery: zachovať denial evidence, vrátiť restrictive baseline, použiť high port + proxy alebo pridať iba required capability, potom verify forbidden operations zostávajú denied.

## 25. Worked failure: runtime socket v application containeri

Atlas helper potreboval „zistiť stav ostatných containers“ a dostal Docker socket.

```text
application compromise
→ attacker calls daemon API
→ creates privileged container with host root mount
→ reads host credentials and controls node
```

Socket read/write API má root-equivalent impact podľa daemon capabilities. Použi narrow read-only mediated service alebo external telemetry, nie raw admin API.

## 26. Worked failure: signed image z compromised buildera

Builder credential a signing identity boli kompromitované. Attacker vložil binary a publikoval platnú signature.

```text
policy checks allowed signer
→ signature cryptographically valid
→ builder/source/input trust was compromised
→ malicious artifact becomes eligible
```

Signature nie je náhrada builder security a provenance verification. Incident scope zahŕňa všetky artifacts podpísané počas compromise window, credentials, registry records a running digests.

## 27. Worked failure: non-root s writable host mountom

Process bežal ako UID 10001, ale host path `/srv/shared` bol world-writable a obsahoval script spúšťaný host service-om.

```text
non-root container writes host script
→ host service executes modified content as root
→ privilege crosses mount boundary
```

Security review musí sledovať mount consumer graph a host execution context, nie iba container UID.

## 28. Worked failure: secret v logu

Application pri startup chybe vypísala celý environment vrátane database tokenu.

```text
short-lived token enters process env
→ error path logs env
→ external log sink retains plaintext
→ broad log readers gain credential
```

Containment: restrict log access, rotate/revoke token, inspect use, remove/expire copies podľa policy a opraviť redacted error contract. Masking future output nerevokuje uniknutú hodnotu.

## 29. Worked failure: image scan green, runtime vulnerable

Image nemala critical findings. Deployment však pripojil host runtime socket a publikoval debug port na všetkých interfaces.

```text
artifact evidence clean
→ runtime effective policy introduces host-admin and network exposure
→ image-only gate misses dominant risk
```

Security evidence inventory musí zahŕňať runtime config a effective exposure.

## 30. Causal troubleshooting walkthrough: container bol podozrivý z escape-u

Atlas container vytvoril neočakávaný process na node-e a security monitoring hlási access k host pathu.

### 1. Zafixuj workload a host subject

Zaznamenaj:

- source/image/platform digest a provenance;
- container/runtime/node identity;
- generated OCI config;
- UID/GID, namespace maps a capabilities;
- seccomp/LSM profiles a audit;
- mounts, devices, runtime socket a host namespaces;
- process tree, executable digests a network flows;
- workload/secret credentials a use audit;
- daemon/admin API events;
- host kernel/runtime versions a adjacent workloads.

### 2. Súťažiace hypotézy

1. Legitímny host helper alebo runtime process bol pripísaný containeru.
2. Container mal host PID namespace alebo broad process visibility.
3. Writable host mount umožnil modification/host execution.
4. Runtime socket umožnil vytvoriť ďalší container.
5. Privileged capability/device umožnil host mutation.
6. User namespace mapping/UID attribution je nesprávna.
7. Kernel/runtime vulnerability umožnila escape.
8. Compromised builder/image už obsahoval malicious code.
9. Admin vykonal `exec` alebo debug operation.
10. Security alert vznikol z LSM denial bez successful mutation.

### 3. Diskriminačné observation points

- runtime create/exec/API audit a container ancestry;
- host/container PID, mount a user namespace relations;
- exact mount/device/socket exposure;
- capabilities, seccomp a LSM allowed/denied events;
- host file inode/change/audit timeline;
- executable provenance a image-layer membership;
- network/credential use timeline;
- kernel exploit indicators a host integrity;
- adjacent container runtime subjects.

### 4. Containment

Izoluj node a workload traffic, revoke relevant identities a zablokuj runtime-admin access. Zachovaj memory/process, runtime metadata, logs a filesystem evidence podľa incident planu. Nespoliehaj sa iba na restart containeru.

### 5. Recovery

- false attribution/helper → oprav telemetry a zachovaj narrow helper policy;
- host mount/socket/privileged exposure → odstráň boundary bypass a rebuild deployment;
- malicious image/builder → quarantine digests, rotate build/signing identities a rebuild z trusted source;
- kernel/runtime escape → replace node z trusted image, patch platform a presuň workloads;
- admin misuse → revoke access a audit all operations;
- LSM denial only → potvrď, že mutation neprešla, a oprav alert/policy podľa intentu.

### 6. Over pôvodný outcome

Deploy successor na clean patched node. Potvrď exact digest/evidence, restrictive runtime policy, žiadny host socket/root mount, expected network/storage access, valid business transaction a nulové adjacent indicators.

### 7. Posuň control skôr

Pridaj effective-runtime admission, socket/host-mount/privileged deny policy, node isolation telemetry, builder attestation a tested forensic/credential-rotation workflow.

## 31. Referenčné pravidlá

- Container security je subject-bound lifecycle, nie zoznam flags.
- Shared kernel určuje host-wide failure boundary.
- Signature dokazuje iba to, čo trust policy overí o signerovi a subjecte.
- SBOM a scan sú artifact evidence, nie runtime-policy evidence.
- Missing/invalid security evidence nie je pass.
- Non-root neznamená bez capabilities, mounts, devices alebo secrets.
- Rootless znižuje daemon authority, nie application risk na nulu.
- `no_new_privs`, capabilities, seccomp a LSM riešia odlišné transitions.
- Privileged mode je boundary collapse.
- Runtime socket je host-admin authority.
- Read-only rootfs potrebuje explicitný writable-path model.
- Workload identity má byť short-lived, scoped a auditovaná.
- Resource policy je súčasť security aj availability.
- Image rebuild neopraví host kernel.
- Live container patch nie je durable remediation.
- Incident recovery potrebuje adjacent-host/workload scope a credential revocation.

## 32. Kontrolné otázky

1. Čo tvorí container security subject?
2. Ako threat model určuje isolation boundary?
3. Prečo signature a green scan nestačia?
4. Ako vzniká effective runtime policy z viacerých sources?
5. Prečo non-root process môže stále kompromitovať host?
6. Ako sa líšia capability, `no_new_privs`, seccomp a LSM?
7. Prečo runtime socket predstavuje host-admin authority?
8. Aký je rozdiel medzi image patchom a host-kernel patchom?
9. Čo musí obsahovať container incident subject?
10. Aké evidence odlíšia host helper, policy denial, runtime socket abuse a kernel escape?

## Glossary impact

Relevantné pojmy: container security subject, effective runtime policy subject, workload threat boundary, artifact evidence inventory, runtime security evidence, builder compromise window, privileged-boundary collapse, runtime-socket authority, mount-mediated privilege path, workload identity subject, security exception subject, node compromise subject, adjacent workload scope, trusted successor runtime a container incident closure.

## Oficiálna dokumentácia

- [Docker Engine security](https://docs.docker.com/engine/security/)
- [Docker rootless mode](https://docs.docker.com/engine/security/rootless/)
- [Docker seccomp profiles](https://docs.docker.com/engine/security/seccomp/)
- [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Container storage](container-storage.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Docker architecture →](docker-architecture.md)
<!-- KNOWLEDGE-NAVIGATION:END -->