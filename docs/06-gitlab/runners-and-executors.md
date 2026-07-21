# Runners a executors

GitLab Runner je agent, ktorý prijíma eligible CI/CD jobs z GitLabu a vykonáva ich pomocou zvoleného executora. Runner nie je iba compute worker. Je to trust boundary medzi pipeline code, secrets, repository obsahom, host systémom, container runtime, cloud účtom a cieľovým environmentom.

## 1. Runner model

Zjednodušený tok:

```text
pipeline job
→ GitLab queue
→ matching runner
→ executor pripraví runtime
→ checkout, cache, artifacts
→ job script
→ artifacts, cache, logs
→ cleanup
```

Runner manager môže obsluhovať viac jobs a podľa executora vytvárať samostatné containers, pods alebo instances.

## 2. Runner scope

Runner môže byť dostupný na rôznom scope:

- instance,
- group,
- project.

Scope určuje, ktoré projects môžu runner používať. Neurčuje automaticky bezpečnosť workloadu.

Shared runner pre nedôveryhodné projects potrebuje silnejšiu isolation než project runner pre jeden kontrolovaný repository.

## 3. Runner authentication

Runner sa autentizuje voči GitLabu runner tokenom. Token:

- identifikuje runner,
- musí byť chránený,
- má mať ownera a rotation lifecycle,
- nesmie byť uložený v repository,
- má byť revokovaný pri decommissioningu.

Runner authentication token nie je to isté ako CI job token používaný jobom na prístup k ďalším GitLab resources.

## 4. Tags a job matching

Jobs môžu požadovať runner tags:

```yaml
windows_build:
  tags:
    - windows
    - trusted-build
  script:
    - .\build.ps1
```

Tag je scheduling label, nie bezpečnostná kontrola sám osebe. Security vzniká z runner scope, protected-runner nastavení, permissions a runtime isolation.

## 5. Protected runners

Runner môže byť obmedzený na protected branches alebo tags. To je užitočné pre jobs s citlivejšími credentials.

Stále platí:

- protected ref môže obsahovať zraniteľný pipeline code,
- included template môže byť mutable,
- runner host môže byť kompromitovaný,
- secrets môžu uniknúť cez logs alebo artifacts.

Protected runner je jedna vrstva, nie úplné riešenie.

## 6. Executor

Executor určuje, kde a ako sa job vykoná.

Bežné možnosti:

- Docker,
- Kubernetes,
- Docker Autoscaler,
- Instance,
- Shell.

Niektoré staršie executors zostávajú podporované iba v maintenance režime. Pri návrhu over aktuálnu support policy GitLab Runner verzie.

## 7. Docker executor

Docker executor vytvára samostatný job container z definovaného image a voliteľné service containers.

Výhody:

- reprodukovateľný runtime,
- jednoduché dependency packaging,
- rýchly startup,
- rozumná process a filesystem isolation,
- lokálna reprodukcia image behavioru.

Riziká:

- privileged mode,
- Docker socket mount,
- shared host kernel,
- mutable images,
- cache a volume sharing,
- container breakout alebo runtime vulnerability.

## 8. Docker socket a privileged mode

Mount:

```text
/var/run/docker.sock
```

prakticky dáva jobu kontrolu nad Docker daemonom a často nad hostom.

Privileged Docker-in-Docker môže byť potrebný pre niektoré build scenáre, ale rozširuje blast radius. Preferuj:

- rootless builders,
- BuildKit s obmedzeným scope,
- dedicated ephemeral runner,
- remote builder s workload identity,
- kanonický build service.

## 9. Kubernetes executor

Kubernetes executor typicky vytvorí pod pre každý job. Pod môže obsahovať:

- build container,
- helper container,
- service containers.

Výhody:

- dynamické scheduling,
- ephemeral pods,
- resource requests a limits,
- namespace a service-account controls,
- autoscaling platformy.

Riziká:

- príliš široký Kubernetes service account,
- privileged pods,
- hostPath mounts,
- shared cluster trust,
- unbounded pod creation,
- secrets v pod spec alebo logs,
- weak network isolation.

## 10. Kubernetes security controls

Použi podľa rizika:

- dedicated namespace,
- least-privilege service account,
- Pod Security controls,
- seccomp,
- dropped capabilities,
- read-only root filesystem,
- NetworkPolicy,
- resource quotas,
- runtime class,
- node isolation,
- short-lived credentials.

CI workload je arbitrary code execution. Neumiestňuj ho bez silných boundaries vedľa citlivých production workloads.

## 11. Shell executor

Shell executor spúšťa job priamo na runner hoste.

Výhody:

- jednoduché nastavenie,
- prístup k host tools a hardware,
- nízky overhead.

Nevýhody:

- slabá isolation,
- shared filesystem a process environment,
- dependency drift,
- riziko krádeže dát medzi jobs,
- host compromise pri nedôveryhodnom code.

Používaj iba pre dôveryhodné workloads na dedikovanom hoste. Shell executor je podľa aktuálnej GitLab dokumentácie v maintenance režime.

## 12. Docker Autoscaler a Instance executor

Autoscaling executors vytvárajú alebo prideľujú instances podľa dopytu.

Ciele:

- elastic capacity,
- ephemeral workers,
- nižší cross-job contamination risk,
- scale-to-zero alebo controlled idle capacity.

Treba riadiť:

- image hardening,
- instance boot time,
- cloud quotas,
- identity bootstrap,
- cleanup po jobe,
- spot/preemptible interruption,
- stale instances,
- cost visibility.

## 13. Ephemeral vs. persistent runners

### Persistent runner

Obsluhuje viac jobs počas dlhého času.

Riziká:

- state leakage,
- dependency drift,
- stale credentials,
- disk exhaustion,
- cache contamination.

### Ephemeral runner

Worker sa vytvorí pre job alebo malý počet jobs a následne zanikne.

Výhody:

- čistejší stav,
- jednoduchší incident containment,
- menšie cross-job riziko.

Nevýhody:

- startup latency,
- vyššie náklady,
- potreba bezpečného bootstrapu.

## 14. Concurrency

Runner concurrency treba nastaviť podľa:

- CPU a memory,
- disk I/O,
- network throughput,
- external API limits,
- cache backendu,
- license alebo tool limits,
- build isolation.

Príliš vysoká concurrency vedie k contention, OOM, throttlingu a dlhšiemu critical pathu.

## 15. Resource limits

Job má mať explicitné alebo platformovo vynútené limity:

- CPU,
- memory,
- ephemeral storage,
- process count,
- timeout,
- network egress podľa potreby.

Bez limitov môže jeden job poškodiť celý runner pool.

## 16. Runner images

Base images majú byť:

- versionované,
- scanované,
- minimálne,
- pravidelne rebuildované,
- podpisované alebo overované podľa assurance požiadaviek,
- bez embedded long-lived secrets.

Toolchain image je súčasť build provenance.

## 17. Helper image

Runner používa helper functionality pre checkout, cache a artifact transfer. Version mismatch, registry access alebo custom helper image môže spôsobiť zlyhania ešte pred job scriptom.

Pri diagnostike odliš:

- prepare failure,
- image pull failure,
- checkout failure,
- cache restore failure,
- user script failure,
- artifact upload failure,
- cleanup failure.

## 18. Network access

Runner jobs často nepotrebujú neobmedzený egress.

Zváž:

- allowlist registry a package endpoints,
- private dependency proxy,
- blokovanie metadata service,
- egress proxy,
- DNS policy,
- network segmentation,
- audit outbound connections.

Supply-chain job s neobmedzeným internet accessom a signing credentials má vysoké riziko.

## 19. Identity

Preferuj workload identity a krátkodobé credentials:

```text
job identity token
→ cloud/security provider federation
→ short-lived scoped credential
```

Nedávaj všetkým runner jobs jeden shared cloud access key.

Identity scope má zohľadniť:

- project,
- ref protection,
- environment,
- job purpose,
- audience,
- duration.

## 20. Cache a workspace hygiene

Persistent runner musí po jobe odstrániť:

- working tree,
- temporary files,
- generated credentials,
- mounted secrets,
- background processes,
- sockets,
- untracked artifacts.

Cache je explicitný shared state. Workspace nemá byť neúmyselný cache.

## 21. Observability

Sleduj:

- queue duration,
- job duration,
- runner utilization,
- executor startup time,
- image pull latency,
- failure rate podľa runner/executora,
- system failures,
- OOM a disk pressure,
- cache hit rate,
- stale/offline runners,
- cost per job alebo compute minute.

## 22. Upgrade lifecycle

Runner version musí byť kompatibilná s GitLab serverom a executor dependencies.

Upgrade process:

1. over release notes,
2. test canary runner,
3. sleduj job failure signatures,
4. postupne aktualizuj pool,
5. zachovaj rollback image/config,
6. odstráň deprecated configuration.

## 23. Troubleshooting

### Job zostáva pending

Over runner online stav, scope, tags, protected-ref eligibility, capacity a paused runner nastavenie.

### Image pull zlyháva

Over registry auth, DNS, TLS trust, pull policy, image path a platform architecture.

### Job funguje lokálne, nie na runneri

Porovnaj image digest, architecture, environment variables, filesystem permissions, network a mounted volumes.

### Náhodné zlyhania pri concurrency

Over shared directories, ports, cache keys, host resources a external rate limits.

### Kubernetes job nevznikne

Over service account RBAC, quotas, Pod Security, scheduling, image pull secrets a namespace policy.

### Shell job vidí súbory iného projektu

Runner nemá dostatočnú isolation. Zastav pool, vykonaj incident review a presuň workload na dedikovaný alebo ephemeral executor.

## 24. Kontrolné otázky

1. Čo je runner a čo executor?
2. Ako runner scope súvisí s trust boundary?
3. Prečo tags nie sú plnohodnotná security kontrola?
4. Aké riziká má Docker socket mount?
5. Ako Kubernetes executor vytvára job runtime?
6. Kedy je shell executor prijateľný?
7. Aké výhody má ephemeral runner?
8. Ako navrhnúť runner workload identity?
9. Ktoré metriky odhalia capacity bottleneck?
10. Ako izolovať nedôveryhodný merge-request workload?

## Glossary impact

Relevantné pojmy: GitLab Runner, runner scope, runner tag, protected runner, executor, Docker executor, Kubernetes executor, Shell executor, ephemeral runner, runner manager, helper image a runner system failure.

## Oficiálna dokumentácia

- [Executors](https://docs.gitlab.com/runner/executors/)
- [Docker executor](https://docs.gitlab.com/runner/executors/docker/)
- [Kubernetes executor](https://docs.gitlab.com/runner/executors/kubernetes/)
- [Shell executor](https://docs.gitlab.com/runner/executors/shell/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: GitLab CI/CD syntax](gitlab-ci-cd-syntax.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Variables a secrets →](variables-and-secrets.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
