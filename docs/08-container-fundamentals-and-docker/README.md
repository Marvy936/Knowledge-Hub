# Container Fundamentals and Docker

Táto sekcia vysvetľuje container platformu ako jeden súvislý systém. Začína obyčajným Linux procesom a otázkou, čo presne oddeľuje container od virtual machine. Potom postupne pridáva namespaces, cgroups, capabilities, OCI image graph, filesystem layers, registry, sieť, storage a security. Až na tomto základe prechádza ku konkrétnemu Docker Engine-u, Dockerfile-u, BuildKitu, Compose a systematickému troubleshooting-u.

Cieľom nie je memorovať desiatky CLI príkazov. Čitateľ má po sekcii rozumieť tomu, ako sa source zmena stane build graphom, image indexom a platform manifestom, ako Docker Engine z image-u a runtime konfigurácie vytvorí process a prečo `running`, `healthy`, `reachable` a správny business outcome nie sú rovnaké stavy.

Celá sekcia používa jeden priebežný scenár `payments-api`. Rovnaká služba sa objavuje pri vysvetľovaní PID 1, non-root runtime-u, volume ownershipu, network bindu, image digestu, multi-platform build-u, loaded configuration generation aj incident recovery. Kód a príkazy preto nie sú izolované recepty. Každý príklad nadväzuje na rovnaký artifact, process, data a request lifecycle.

## Predpoklady

Sekcia nadväzuje najmä na [Linux and Systems](../01-linux-and-systems/README.md), [Networking and Web Fundamentals](../02-networking-and-web/README.md), [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md), [GitLab](../06-gitlab/README.md) a [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md). Linux kapitoly poskytujú process, filesystem, permission a network základ. CI/CD a GitLab vysvetľujú immutable artifact, evidence a promotion. IaC a Ansible pripravujú desired-state, ownership a runtime-verification model.

## Authoritative poradie kapitol

1. [Containers vs. virtual machines](containers-vs-virtual-machines.md)
2. [Namespaces, cgroups a capabilities](namespaces-cgroups-capabilities.md)
3. [OCI image a runtime standards](oci-image-runtime-standards.md)
4. [Images, layers a copy-on-write](images-layers-copy-on-write.md)
5. [Registries](registries.md)
6. [Container networking](container-networking.md)
7. [Container storage](container-storage.md)
8. [Container security](container-security.md)
9. [Docker architecture](docker-architecture.md)
10. [Dockerfile](dockerfile.md)
11. [Build context a layer cache](build-context-layer-cache.md)
12. [Multi-stage builds](multi-stage-builds.md)
13. [Volumes a bind mounts](volumes-bind-mounts.md)
14. [Docker networks a port publishing](docker-networks-port-publishing.md)
15. [Environment variables a health checks](environment-variables-health-checks.md)
16. [Docker Compose](docker-compose.md)
17. [BuildKit a Buildx](buildkit-buildx.md)
18. [Praktický Docker projekt od prázdneho adresára po overený Compose runtime](docker-practical-walkthrough.md)
19. [Docker troubleshooting](docker-troubleshooting.md)

Poradie je zámerné. Prvé dve kapitoly vysvetlia runtime isolation. OCI, layers a registry potom vytvoria artifact a distribution model. Network, storage a security ukážu, čo sa k image-u pripája až pri runtime. Docker-specific blok následne prejde od Engine API cez Dockerfile a build graph po Compose application. Praktický walkthrough všetko spojí a troubleshooting kapitola ukáže, ako sa rovnaký model používa pri incidente.

Po tejto sekcii nasleduje Kubernetes. Docker a OCI pojmy sa tam objavia vo väčšom control-plane modeli ako Pod sandbox, container runtime interface, image pull, probes, Services, volumes, security context a node-level diagnosis.

## Výkladový štandard sekcie

Všetkých devätnásť kapitol bolo kompletne prepísaných do rovnakého plynulého štýlu ako Keycloak a CI/CD. Kapitola najprv stanoví konkrétny problém, potom vysvetlí mechanizmus na priebežnom Atlas scenári, vloží príkaz alebo konfiguráciu priamo tam, kde ju čitateľ potrebuje, a bezprostredne vysvetlí, čo výstup dokazuje a čo ešte nie. Odrážky zostávajú iba pri krátkom inventári alebo acceptance zozname; nenahrádzajú hlavný výklad.

Príklady sú navzájom prepojené. `payments-api` beží ako non-root UID `65532`, počúva na porte `8080`, publikuje `/healthz`, `/readyz` a `/version`, používa configuration generation a zapisuje jednoduchý ledger do named volume-u. Vďaka tomu možno na jednom workload-e porovnať image config s container configom, local health so service DNS a host portom, container replacement s volume persistence a amd64 image s multi-platform indexom.

Každý významný command sa interpretuje v troch rovinách: aký objekt číta alebo mení, aký výsledok očakávame a kde končí dôkazová hranica. `docker image inspect` číta image metadata, nie effective container security options. `docker ps` číta Engine process state, nie readiness. `docker compose config` vytvára resolved model, nie runtime objects. `docker compose up --wait` čaká na running alebo health podmienky, ale nenahrádza payment POST/GET a persistence test.

## Praktický walkthrough

Kapitola [Praktický Docker projekt od prázdneho adresára po overený Compose runtime](docker-practical-walkthrough.md) vytvorí celý malý projekt. Začína Go source-om a unit testom, pokračuje cez `.dockerignore`, multi-stage Dockerfile a explicitný BuildKit test target a vytvorí lokálny runtime image. Následne image inspectne, exportuje jeho root filesystem, vytvorí network a volume, pripraví ownership, skontroluje container ešte pred štartom a až potom overí PID 1, health, host port a business write/read.

Druhá polovica vytvorí celý Compose model so službami `init-data`, `api` a `verifier`. Najprv sa kontroluje interpolation a resolved YAML. Potom sa oddelene overí container-local health, Compose DNS, host-published path a volume-backed payment. Walkthrough ukáže no-op druhý run, configuration-driven recreate, persistence cez novú container generation, zámerne chybný loopback bind a volume-permission incident. Záver publikuje multi-platform image, read-backne index a platform manifests a prejde na digest-pinned consumption.

Go source z praktickej kapitoly bol formátovaný cez `gofmt` a úspešne spustený cez `go test` na dostupnom Go 1.23.2 toolchaine po dočasnom znížení `go` directive na 1.23 pre lokálnu syntax a test kontrolu. Dokumentovaný project contract zostáva Go 1.25. Docker, Compose, Buildx a registry príkazy sú syntakticky a mechanisticky auditované, ale repository documentation workflow ich nespúšťa proti reálnemu Docker Engine-u alebo registry.

## Čo má čitateľ po sekcii vedieť

Po dokončení má vedieť vysvetliť container ako kernel-backed process boundary a porovnať ho s guest-kernel a hypervisor hranicou VM. Má rozumieť namespaces, cgroups, capabilities, seccomp a LSM ako rozdielnym vrstvám, nie ako synonymám. Má vedieť čítať OCI index, platform manifest, config a layers a vysvetliť rozdiel medzi tagom, digestom a deployed platform artifactom.

V build časti má vedieť navrhnúť Dockerfile s kontrolovanými bases, zúženým contextom, zmysluplnou cache hranicou, explicitným test targetom a úzkym runtime stage-om. Má rozlíšiť `--load`, `--push`, local artifact export, external cache, provenance a SBOM a vedieť, prečo multi-platform metadata musí zodpovedať skutočnému binary.

V runtime časti má vedieť read-backnúť effective usera, command, environment, mounts, ports, limits a security options. Má rozlíšiť writable layer, named volume, bind mount a tmpfs, navrhnúť UID/GID, backup a restore contract a vysvetliť mount obscuring. Pri networku má vedieť sledovať packet od application bindu cez namespace, bridge, DNS a port publishing až po return path.

V Compose časti má rozumieť project identity, interpolation, multiple files, profiles, `depends_on`, health conditions, networks a volumes ako resolved application modelu. Má vedieť, kedy `up` vykoná no-op, kedy recreatne container a prečo `restart` neaplikuje nové environment alebo image inputs.

Pri incidente má vedieť zachovať context, inspect, image, events, logs, network, volume a disk evidence pred destructive operáciou. Má vedieť odlíšiť pull, create, runtime exec, process, health, network, storage a business failure a zvoliť restart, recreate, rebuild alebo host replacement podľa prvej chybnej vrstvy.

## Stav revalidácie

| Blok | Kapitoly | Stav |
|---|---:|---|
| Linux container boundary, OCI, images a registry | 5/5 | Complete |
| Network, storage a security runtime model | 3/3 | Complete |
| Docker Engine, Dockerfile, context/cache a multi-stage build | 4/4 | Complete |
| Mounts, networking, environment/health a Compose | 4/4 | Complete |
| BuildKit/Buildx, practical walkthrough a troubleshooting | 3/3 | Complete |

Celkový authoritative stav je **19/19 · Ready for user review**. Znamená to dokončený full-section prose, code-example a navigation pass. Neznamená automaticky používateľské `Accepted`, reálne Docker `Verified` ani produkčné `Stable`. Tieto vyššie stavy vyžadujú používateľskú kontrolu a samostatné vykonanie príkladov v reprezentatívnom Docker a registry prostredí.