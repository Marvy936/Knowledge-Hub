# Container security

Container security je defense-in-depth model naprieč source, buildom, registry, runtime, host kernelom, identities, networkingom, storage a operations. Container nie je automatická security boundary rovnocenná virtual machine. Väčšina Linux containers zdieľa host kernel, preto kompromitácia runtime alebo kernelu môže mať širší blast radius.

## 1. Threat model

Najprv definuj, pred čím sa chrániš:

- zraniteľná aplikácia,
- malicious image alebo dependency,
- kompromitovaný CI builder,
- ukradnuté registry credentials,
- container escape,
- lateral movement medzi workloads,
- host compromise,
- secret exfiltration,
- supply-chain substitution,
- denial of service cez resources,
- privileged insider alebo chybnú konfiguráciu.

Bez threat modelu sa security redukuje na nekonzistentný zoznam flags.

## 2. Security lifecycle

Bezpečný lifecycle:

```text
trusted source
→ reproducible build
→ signed/provenance artifact
→ registry policy
→ admission/deployment policy
→ hardened runtime
→ observed execution
→ patch/rebuild/replace
```

Kontrola v jednej vrstve nenahrádza ostatné. Image scan nezachytí všetky runtime misconfigurations; seccomp neodstráni vulnerable dependency.

## 3. Minimal image

Minimalizuj runtime obsah:

- nepoužívané packages,
- compilers a build tools,
- shells, ak nie sú potrebné,
- package manager cache,
- debugging utilities bez support dôvodu,
- default credentials a sample config.

Menší image znižuje attack surface, ale musí zostať operabilný. Incident response môže používať external alebo ephemeral debug tooling namiesto permanentného toolsetu v application image.

## 4. Trusted base image

Base image musí mať:

- známeho ownera,
- update a support policy,
- pinned digest,
- provenance,
- vulnerability monitoring,
- kompatibilitu s workloadom,
- pravidelný rebuild.

Tag ako `ubuntu:latest` alebo `alpine:3` nie je immutable input. Pinning digestu zvyšuje reproducibility, ale potrebuje automatizovaný update workflow, inak zamrzne na starej zraniteľnej verzii.

## 5. Build security

Build environment často pristupuje k source, registries, package repositories a secrets. Chráň:

- isolated builders,
- short-lived credentials,
- secret mounts namiesto build args,
- restricted network egress,
- pinned build images/actions,
- clean workspaces,
- artifact provenance,
- build logs a cache.

Build cache môže obsahovať source alebo credentials. Zdieľanie cache medzi nedôveryhodnými projects vytvára cross-tenant risk.

## 6. Secrets v image

Secret zapísaný do layeru zostáva dostupný aj po odstránení v neskoršom layeri.

Nikdy nevkladaj do image:

- `.env` s reálnymi credentials,
- SSH private keys,
- cloud access keys,
- registry tokens,
- TLS private keys,
- production configuration s heslami.

Pri náleze secretu:

1. okamžite revoke/rotate credential,
2. odstráň ho zo source/build history,
3. rebuildni clean image,
4. odstráň alebo quarantine staré artifacts,
5. audituj použitie.

## 7. SBOM

Software Bill of Materials inventarizuje components a versions v artifacte. Pomáha pri:

- vulnerability response,
- license governance,
- dependency ownership,
- incident scope,
- provenance analýze.

SBOM nie je vulnerability scan ani dôkaz, že všetky runtime dependencies boli zachytené. Musí byť viazaný na konkrétny image digest.

## 8. Vulnerability scanning

Skenuj:

- OS packages,
- language dependencies,
- application binaries,
- base image,
- secrets a malware podľa toolchainu,
- configuration/IaC/runtime manifests.

Výsledok vyhodnocuj podľa:

- severity,
- exploitability,
- reachability,
- runtime exposure,
- fixed version availability,
- compensating controls,
- environmentu,
- exception expiration.

Scan je bodový dôkaz. Nové CVE môže vzniknúť po deployment-e, preto je potrebné continuous rescanning a rebuild policy.

## 9. Signing a provenance

Signature viazaná na digest dokazuje schválenie alebo pôvod podľa trust policy. Provenance môže zachytiť:

- source repository a commit,
- builder identity,
- build process,
- inputs,
- timestamps,
- artifact digest.

Verification policy musí overovať identity claims, nie iba prítomnosť ľubovoľného podpisu.

## 10. Run as non-root

Workload má typicky bežať ako explicitný non-root UID/GID.

Výhody:

- menší dopad application compromise,
- obmedzený write access,
- lepšia kompatibilita s restricted policies.

Obmedzenia:

- non-root môže stále mať capabilities,
- writable host mount môže byť prístupný,
- kernel vulnerability zostáva relevantná,
- application secret môže byť čitateľný processom.

Použi explicitné numeric UID, stabilné ownership contracts a `USER` v image alebo runtime override.

## 11. Rootless containers

Rootless engine/runtime beží bez host root daemon identity a používa user namespaces a unprivileged helpers.

Výhody:

- znižuje blast radius daemon/runtime compromise,
- host root nie je default control identity.

Trade-offy:

- networking/storage limitations,
- odlišné performance,
- device a low-port restrictions,
- filesystem UID mapping,
- nie všetky workloads sú kompatibilné.

Rootless neznamená bezrizikové; application, kernel a user account stále tvoria attack surface.

## 12. Drop capabilities

Začni s minimálnym capability setom:

```text
drop all
→ pridaj iba dokázateľne potrebné capabilities
```

Vyhýbaj sa širokým capabilities ako `CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, `CAP_SYS_PTRACE` alebo `CAP_DAC_OVERRIDE`, ak nie sú nevyhnutné.

Každá pridaná capability má mať:

- ownera,
- zdôvodnenie,
- test,
- scope,
- review pri zmene image alebo kernelu.

## 13. Privileged mode

Privileged container zásadne oslabuje isolation. Môže dostať široké capabilities, devices a uvoľnené security profiles.

Použitie je vhodné iba pre úzko definované infra workloads, ak neexistuje bezpečnejšia alternatíva. Aplikácia nesmie používať privileged mode ako opravu permission alebo device problému.

## 14. Seccomp

Seccomp obmedzuje syscalls. Default profile znižuje kernel attack surface. Custom profile môže byť presnejší, ale musí byť testovaný proti reálnemu behavioru.

Pri policy návrhu:

- začni z maintained baseline,
- sleduj denials,
- povoľ konkrétny syscall iba s dôvodom,
- testuj upgrade runtime/application,
- nepoužívaj `unconfined` bez risk acceptance.

## 15. AppArmor a SELinux

Mandatory Access Control obmedzuje process aj pri povolených Unix permissions.

Policy môže kontrolovať:

- filesystem paths,
- executable transitions,
- capabilities,
- network alebo ďalšie operácie podľa LSM.

Runtime labels/profiles a mounted storage musia byť koordinované. Audit denial je diagnostický dôkaz, nie dôvod vypnúť host policy.

## 16. Read-only root filesystem

Read-only root filesystem:

- obmedzuje persistence útočníka,
- zabraňuje package/runtime mutation,
- zmenšuje writable surface,
- podporuje immutable operation.

Explicitne povoľ iba potrebné writable mounts. Každý writable path má mať size, permissions, data classification a cleanup policy.

## 17. Filesystem permissions

Používaj:

- least-privilege UID/GID,
- presné mode bits,
- read-only mounts,
- `noexec`, `nosuid`, `nodev` podľa potreby,
- bez host root mountu,
- bez runtime socketu v application containeri.

Mount Docker/containerd socketu často poskytuje možnosť ovládať host runtime a prakticky predstavuje host-admin boundary.

## 18. Device access

Sprístupnenie device môže otvoriť host kernel subsystem. Pri GPU, KVM, block device, USB alebo network device kontroluj:

- konkrétny device allowlist,
- permissions,
- capabilities,
- driver attack surface,
- isolation medzi tenants,
- node placement,
- audit.

`/dev` ako široký host mount je neprimeraný default.

## 19. PID a process controls

Použi:

- PID limit,
- správny init/PID 1 behavior,
- zakázanie privilege escalation,
- signal handling,
- process count monitoring.

Fork bomb alebo runaway thread creation môže poškodiť host aj bez container escape.

## 20. Resource limits

CPU, memory, PID a I/O limits znižujú denial-of-service blast radius. Limity musia byť založené na workload profile a load tests.

Bez limitov môže jeden container vyčerpať shared host. Príliš nízke limity spôsobia OOM, throttling alebo nestabilitu, čo môže viesť k security bypassom počas incidentu.

## 21. Network segmentation

Default-deny alebo explicitný allow model znižuje lateral movement.

Kontroluj:

- ingress ports,
- service-to-service paths,
- egress destinations,
- metadata service,
- DNS,
- control-plane a registry access,
- IPv4/IPv6 parity.

Port publish na všetkých host interfaces môže neúmyselne obísť očakávaný reverse proxy alebo firewall boundary.

## 22. Secrets pri runtime

Runtime secrets dodávaj cez:

- secret manager,
- workload identity,
- short-lived token,
- memory/tmpfs file,
- protected environment variable iba pri akceptovanom leakage modeli.

Environment variables môžu uniknúť cez process inspection, debug dumps, logs alebo child processes. File secret potrebuje permissions, rotation a cleanup.

## 23. Workload identity

Preferuj federovanú alebo workload identity pred statickými cloud credentials v image/config.

Identity má byť:

- viazaná na workload a environment,
- krátkodobá,
- audience/scoped,
- least privilege,
- auditovaná,
- revokovateľná.

Network location alebo container name nie sú dostatočná identita.

## 24. Host hardening

Shared kernel znamená, že host je kritická boundary. Chráň:

- kernel a runtime patching,
- minimal host OS,
- runtime API/socket,
- SSH/admin access,
- audit logs,
- kernel modules,
- LSM a seccomp,
- filesystem a disk encryption,
- node separation podľa trust levelu.

Nedôveryhodné multi-tenant workloads môžu vyžadovať VM, microVM alebo sandboxed runtime boundary.

## 25. Runtime daemon

Container daemon môže mať vysoké host privileges. Chráň:

- Unix socket permissions,
- remote API TLS a authentication,
- authorization plugins/policy,
- žiadny public unauthenticated endpoint,
- audit API operations,
- oddelené admin a workload identities.

Členstvo v skupine s prístupom k Docker socketu je často prakticky root-equivalentné.

## 26. Logging a audit

Zachytávaj:

- image digest a signature verification,
- runtime configuration,
- user/capabilities/seccomp/LSM profile,
- mounts a devices,
- network exposure,
- container create/start/stop/exec events,
- admin API access,
- OOM a security denials.

Logs nesmú obsahovať secrets. Audit trail musí prežiť zánik containeru.

## 27. Patchovanie

Container sa typicky nepatchuje ručne. Bezpečný model:

1. aktualizuj source/base/dependencies,
2. rebuildni image,
3. znovu skenuj a podpíš,
4. deployni nový digest,
5. over runtime,
6. odstráň staré instances podľa rollout policy.

Rebuildni aj bez source zmeny, ak sa zmení base image alebo security data.

## 28. Incident response

Pri kompromitácii:

- izoluj workload/network,
- zachovaj image digest, runtime config a logs,
- rotuj secrets a identities,
- nepatchuj iba live container,
- analyzuj host/kernel exposure,
- rebuildni z trusted source,
- over adjacent workloads,
- zdokumentuj initial access a persistence path.

Odstránenie containeru môže zničiť volatile evidence. Forensic postup musí byť pripravený vopred.

## 29. Security baseline

Praktický baseline:

- trusted pinned image,
- signature/provenance verification,
- non-root user,
- no privilege escalation,
- drop capabilities,
- default seccomp,
- SELinux/AppArmor enforced,
- read-only root filesystem,
- explicit writable mounts,
- resource limits,
- network allowlist,
- short-lived workload identity,
- bez runtime socketu a host root mounts.

Exceptions musia mať ownera, dôvod, compensating controls a expiration.

## 30. Troubleshooting

### Aplikácia funguje iba v privileged mode

Izoluj konkrétnu chýbajúcu capability, device, mount alebo syscall. Privileged mode neponechávaj ako výsledné riešenie.

### Non-root process nevie zapisovať

Over image ownership, runtime UID, volume permissions, user namespace mapping a SELinux/AppArmor label.

### Scanner hlási CVE bez fixu

Vyhodnoť reachability, exposure, base alternative, compensating controls a časovo obmedzenú exception. Finding neignoruj bez evidence.

### Container nevie vykonať syscall

Over seccomp denial, capability checks, kernel podporu a LSM audit. Neprepínaj profil na unconfined bez analýzy.

### Secret sa objavil v logu

Okamžite ho rotuj, obmedz log access/retention, oprav redaction a audituj použitie. `no_log` alebo masking nie sú náhradou rotácie uniknutého credentialu.

## 31. Kontrolné otázky

1. Prečo container security potrebuje lifecycle model?
2. Čo SBOM poskytuje a čo neposkytuje?
3. Prečo digest pinning potrebuje update workflow?
4. Prečo non-root sám nestačí?
5. Aké riziko predstavuje Docker socket?
6. Ako sa líšia capabilities, seccomp a LSM?
7. Prečo privileged mode nie je bežný fix?
8. Ako resource limits prispievajú k security?
9. Kedy je vhodná silnejšia VM/microVM boundary?
10. Ako sa patchuje immutable container workload?

## Glossary impact

Relevantné pojmy: container threat model, container security baseline, trusted base image, image signing, build provenance, SBOM, continuous image scanning, rootless container, non-root container, no privilege escalation, capability drop, seccomp profile, container LSM profile, read-only root filesystem, runtime socket exposure, workload identity, container host hardening a container forensic evidence.

## Oficiálna dokumentácia

- [Docker Engine security](https://docs.docker.com/engine/security/)
- [Docker rootless mode](https://docs.docker.com/engine/security/rootless/)
- [Docker seccomp profiles](https://docs.docker.com/engine/security/seccomp/)
- [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Container storage](container-storage.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
