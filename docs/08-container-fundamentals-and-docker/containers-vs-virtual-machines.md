# Containers vs. virtual machines

Container a virtual machine neriešia presne ten istý problém rovnakým spôsobom. Obe technológie vytvárajú prostredie, v ktorom môže bežať aplikácia, ale hranicu izolácie umiestňujú na iné miesto. Virtual machine dostane virtualizovaný hardware a vlastný guest kernel. Linux container zostáva skupinou procesov na hostiteľskom kerneli, ktorým runtime pripraví oddelený pohľad na procesy, sieť, filesystem, používateľov a zdroje.

Tento rozdiel je podstatnejší než bežné porovnanie typu „container je ľahší a VM bezpečnejšia“. Pri návrhu platformy potrebujeme vedieť, čo sa izoluje, čo sa stále zdieľa, kde sa nachádza persistentný stav, kto patchuje jednotlivé vrstvy a čo presne prežije reštart alebo náhradu runtime inštancie.

Budeme sledovať službu `payments-api`. V lokálnom prostredí ju vývojár spúšťa ako container. V cloude beží container na Linux worker VM. Databáza je mimo oboch vrstiev ako samostatná managed služba. Tento model je bežný, pretože VM vytvára infraštruktúrnu a kernelovú hranicu a container poskytuje menšiu, rýchlo nahraditeľnú aplikačnú jednotku.

## 1. Jeden workload, viac vrstiev

Produkčný request prejde cez viac vrstiev, než naznačuje jednoduchá veta „aplikácia beží v Dockeri“:

```text
fyzický cloud host
→ hypervisor
→ worker VM
→ guest Linux kernel
→ container runtime
→ container filesystem, namespaces a cgroups
→ payments-api process
→ databáza a ďalšie externé služby
```

Každá vrstva má vlastnú identitu a vlastný lifecycle. Worker VM môže byť vytvorená z machine image `node-os-2026.08.1`, zatiaľ čo aplikácia používa image digest `sha256:payments460`. Container môže byť odstránený a znovu vytvorený bez zmeny VM. VM môže byť nahradená bez zmeny aplikačného image-u. Databáza môže prežiť obidve operácie.

Keď incident report povie iba „payments container nefungoval“, stále nevieme, či bol problém v aplikačnom binary, image filesysteme, runtime konfigurácii, guest kerneli, hypervisore, sieti alebo databáze. Preto sa pri troubleshooting-u identifikuje aspoň image digest, container ID, VM alebo node identity, kernel a runtime verzia, loaded configuration generation a persistentný data owner.

## 2. Čo je obyčajný process

Aplikácia sa nakoniec vždy vykonáva ako process. Process má vlastný virtual address space, file descriptors, threads, credentials a execution state. Bez ďalšej izolácie však vidí rovnaký host process tree, rovnaký network stack, rovnaký mount tree a rovnaký resource pool ako ostatné procesy.

Na bežnom Linux hoste si to možno predstaviť takto:

```bash
ps -eo pid,ppid,user,cmd
ip address
mount
cat /proc/self/cgroup
```

Tieto príkazy ukážu pohľad aktuálneho procesu na hostiteľský systém. Container runtime nemení skutočnosť, že aplikácia je process. Mení prostredie, ktoré jej kernel ukazuje, a pravidlá, podľa ktorých môže spotrebúvať zdroje alebo volať privilegované operácie.

## 3. Ako vznikne Linux container

Pri vytvorení containeru runtime skombinuje image root filesystem s runtime konfiguráciou. Kernel následne vytvorí alebo pripojí namespaces, zaradí process do cgroups, nastaví credentials, capabilities, seccomp a prípadnú SELinux alebo AppArmor policy a pripojí volumes a network interfaces.

Zjednodušený tok vyzerá takto:

```text
image manifest a layers
+ runtime environment, command a user
+ mounts a writable layer
+ network namespace a interface
+ cgroup limits
+ capabilities, seccomp a LSM policy
→ exec hlavného procesu
```

V containere preto nebootuje druhý Linux kernel. Binary volá syscalls do kernelu hostiteľskej Linux vrstvy. To vysvetľuje aj jednu dôležitú hranicu prenositeľnosti: image balí userspace, nie celý operačný systém. Linux image potrebuje Linux kernel a kompatibilnú CPU architektúru. Docker Desktop na Windows alebo macOS preto pre Linux containers používa Linux VM alebo inú Linuxovú virtualizačnú vrstvu.

Prakticky možno zistiť, že proces z containeru stále existuje na hoste:

```bash
docker run --rm --name process-demo alpine:3.22 sleep 300
```

V druhom termináli:

```bash
docker inspect process-demo --format '{{.State.Pid}}'
ps -fp "$(docker inspect process-demo --format '{{.State.Pid}}')"
```

Hostiteľ vidí skutočný PID procesu. Process vo vlastnom PID namespace môže pritom vidieť sám seba ako PID 1. Obe pozorovania sú správne; patria inému namespace pohľadu.

## 4. Ako vznikne virtual machine

Virtual machine začína o vrstvu nižšie. Hypervisor poskytne virtual CPU, memory, disk, network interface a ďalšie zariadenia. Guest firmware alebo bootloader načíta guest kernel, kernel inicializuje userspace a init systém spustí služby.

```text
physical CPU, memory a devices
→ hypervisor
→ virtual hardware
→ guest kernel boot
→ init a system services
→ application alebo container runtime
```

VM môže mať inú kernel verziu a často aj inú OS family než hostiteľ, pokiaľ to podporuje architektúra a hypervisor. Kompromitovaná aplikácia sa najprv nachádza v guest OS. Na priamy zásah hypervisora alebo inej VM musí útočník prekonať ďalšiu virtualizačnú hranicu.

To neznamená, že VM je automaticky bezpečná. Guest OS môže byť nepatchovaný, cloud identity príliš široká, virtual disk verejne dostupný a management plane zle chránený. Rozdiel je v tom, že VM pridáva samostatný guest kernel a hypervisor boundary, zatiaľ čo containers na jednom node zdieľajú kernel.

## 5. Prečo sa containers často spúšťajú vo VMs

Pri cloudovom nasadení nejde zvyčajne o rozhodnutie „VM alebo container“. Používajú sa obe vrstvy:

```text
VM
→ node a kernel failure domain

container
→ aplikačný artifact a replaceable process unit
```

Atlas Payments používa worker VM ako infraštruktúrny node. Na nej beží Docker Engine alebo Kubernetes container runtime. `payments-api` je container, ktorý možno rýchlo nahradiť pri novom release. Keď však treba opraviť kernel vulnerability alebo container runtime, platforma drain-ne workloady a nahradí celú worker VM.

Tento model vytvára dva oddelené patch lifecycles. Rebuild aplikačného image-u aktualizuje binary a userspace libraries, ale neopraví guest kernel. Nová VM image opraví kernel a runtime, ale môže znovu spustiť starý zraniteľný aplikačný image. Bez inventára oboch vrstiev môže dashboard ukazovať „všetky nodes patched“, hoci produkcia stále používa zraniteľný image digest.

## 6. Image nie je bežiaci container

Container image je nemenný alebo aspoň content-addressed aplikačný template. Obsahuje filesystem layers a image configuration, napríklad defaultného používateľa, environment, working directory, entrypoint a command.

```bash
docker image inspect registry.example.com/atlas/payments-api@sha256:<digest>
```

Výstup opisuje image. Neopisuje všetky runtime overrides. Pri spustení môže operator zmeniť používateľa, command, environment, mounts, ports, limits a security options:

```bash
docker run --rm \
  --user 65532:65532 \
  --read-only \
  --memory 256m \
  --env LOG_LEVEL=debug \
  registry.example.com/atlas/payments-api@sha256:<digest>
```

Dva containers z rovnakého digestu preto môžu mať odlišné správanie. Jeden môže mať správny volume a druhý zapisovať iba do dočasnej writable layer. Jeden môže bežať ako non-root a druhý byť prepísaný na root. Image identity je nevyhnutná, ale sama nestačí na rekonštrukciu runtime-u.

## 7. Rýchlejší štart nie je automaticky readiness

Container sa typicky vytvára rýchlejšie než boot celej VM. Runtime nemusí inicializovať virtual hardware, guest kernel ani plný init systém. Pripraví filesystem snapshot, namespaces, cgroups, mounts a sieť a vykoná entrypoint.

To však ešte neznamená, že služba je pripravená prijímať traffic. `payments-api` po štarte načíta konfiguráciu, otvorí database pool, overí schema compatibility a začne počúvať na porte. Process môže existovať, ale readiness endpoint ešte vracia chybu.

Preto treba rozlišovať:

```text
container created
→ process started
→ process alive
→ application ready
→ service reachable
→ business operation úspešná
```

`docker ps` dokazuje najmä stav hlavného procesu z pohľadu Engine-u. Healthcheck môže dokazovať lokálnu aplikačnú podmienku. Až reálny request cez publikovaný port alebo service network dokazuje konkrétnu serving path.

## 8. Resources: cgroup limit a virtual hardware nie sú to isté

Container používa cgroups na accounting a obmedzenie CPU, memory, PID alebo I/O zdrojov. Napríklad:

```bash
docker run --rm \
  --cpus 0.50 \
  --memory 256m \
  --pids-limit 128 \
  registry.example.com/atlas/payments-api@sha256:<digest>
```

Tieto flags nevytvárajú fyzický procesor ani garantovaný diskový výkon. Nastavia cgroup policy v rámci hostiteľského systému. Pri memory limite môže kernel procesy v cgroup ukončiť. Pri CPU kvóte môže aplikácia trpieť throttlingom. I/O a network môžu zostať zdieľané s ostatnými workloadmi na node.

VM dostane virtual CPUs a virtual memory, ale aj tam môže hypervisor používať overcommit a workload môže pozorovať CPU steal alebo storage contention. Pri pomalej aplikácii preto nestačí pozerať iba container metrics. Treba korelovať aplikačnú latenciu, cgroup throttling alebo OOM, tlak v guest kerneli a stav VM alebo fyzickej infraštruktúry.

## 9. Persistence musí mať vlastného ownera

Container writable layer je viazaná na konkrétny container object. Keď sa container odstráni, jeho writable layer sa bežne odstráni s ním. Je vhodná pre dočasné súbory, cache alebo replaceable generated state. Nenahraditeľné business dáta tam nemajú zostať bez explicitného rozhodnutia.

Atlas Payments zapisuje transakcie do PostgreSQL a lokálny export buffer do named volume-u. To umožňuje nahradiť aplikačný container bez straty dát:

```text
container generation C1
→ mount volume V1
→ zápis dát
→ odstránenie C1
→ container generation C2
→ mount rovnakého V1
→ dáta zostávajú
```

Volume však nie je automaticky backup. Stále treba riešiť ownership, filesystem permissions, host failure, corruption, snapshot consistency, restore a prípadných viacerých writers. Podobne ani virtual disk VM nie je automaticky application-consistent databázový backup. Persistence potrebuje samostatný lifecycle bez ohľadu na to, či aplikácia beží v containere alebo priamo vo VM.

## 10. Bezpečnostný rozdiel sa prejaví pri zlom runtime nastavení

Shared-kernel model môže byť dostatočný pre veľké množstvo interných služieb, pokiaľ sú containers spustené s úzkymi oprávneniami a host je správne hardenovaný. Hranica sa však dramaticky oslabí pri privileged mode, host namespace-och, runtime socket mounte alebo writable host filesystem mounte.

Nasledujúci príkaz by bol z pohľadu izolácie extrémne rizikový:

```bash
docker run --rm -it \
  --privileged \
  --pid host \
  --mount type=bind,src=/,dst=/host \
  --mount type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock \
  alpine:3.22 sh
```

Takýto workload má prístup k hostiteľským procesom, filesystemu, zariadeniam a Docker API. Označenie „container“ už neposkytuje rozumnú bezpečnostnú garanciu. Kompromitácia aplikácie sa môže zmeniť na kompromitáciu node-u a všetkých workloadov, ktoré s ním zdieľajú kernel.

Pri citlivom multi-tenant workload-e môže byť vhodná dedicated VM, microVM alebo sandboxed runtime aj vtedy, keď sa aplikácia naďalej distribuuje ako OCI image. Packaging a isolation boundary sú dve samostatné rozhodnutia.

## 11. Praktické rozhodnutie pre Atlas Payments

Pre bežnú internú verziu `payments-api` zvolí Atlas container na worker VM. Aplikácia je stateless voči hlavnej databáze, rýchlo sa nahrádza a nepotrebuje vlastný kernel. Runtime policy zakazuje privileged mode, Docker socket a host namespaces, používa non-root usera, read-only root filesystem, explicitné volumes a resource limits.

Pre support nástroj, ktorý potrebuje analyzovať kernel crash dumps a host devices, by rovnaká boundary nestačila. Nástroj by dostal dedicated VM alebo úzko navrhnutý node-level workflow s presne obmedzenými mounts a capabilities. Dôvodom nie je, že VM je vždy „lepšia“, ale že požadované oprávnenia by z container boundary spravili iba formálne označenie.

Rozhodovací proces preto začína otázkami: Aký je threat model? Ktoré zdroje sa musia zdieľať? Aké oprávnenia potrebuje workload? Kde sú business dáta? Ako sa patchuje kernel a userspace? Aký blast radius je akceptovateľný? Až potom má zmysel hovoriť o hustote, rýchlosti štartu alebo prevádzkových nákladoch.

## 12. Incident: dáta zmizli pri úplne korektnom replacement-e

Atlas export worker zapisoval pending reconciliation records do `/var/lib/atlas/pending`, ale path nebola volume. Počas výmeny node-u platforma odstránila starý container a vytvorila nový z rovnakého image digestu.

```text
worker zapíše 8 000 pending records do writable layer
→ node drain odstráni container
→ writable layer zanikne
→ nový container začína z čistého image-u
→ databáza a exportný systém sa rozídu
```

Container runtime sa nesprával chybne. Presne vykonal požadovaný replacement. Chyba bola v architektúre dát: nenahraditeľný stav bol uložený do vrstvy, ktorej lifecycle bol kratší než lifecycle business operácie.

Recovery musela rekonštruovať pending records z autoritatívnej databázy a externého export systému. Trvalá oprava presunula ledger do databázy a replacement test začal overovať, že rozpracovaná operácia prežije odstránenie containeru aj node-u.

## 13. Ako túto kapitolu použiť pri troubleshooting-u

Keď aplikácia funguje ako systemd service vo VM, ale v containere zlyhá, nezačínaj všeobecným tvrdením, že „Docker má problém“. Najprv porovnaj konkrétne runtime rozdiely:

```bash
docker image inspect IMAGE
docker inspect CONTAINER
docker logs --timestamps CONTAINER
docker top CONTAINER -eo pid,ppid,user,args
docker stats --no-stream CONTAINER
```

Skontroluj používateľa, command, environment, mounts, read-only filesystem, capabilities, seccomp alebo LSM denial, CPU architektúru a dynamic loader. Binary môže byť správny, ale nemá write access k volume-u. Process môže bežať, ale počúva iba na container loopbacku. Image môže byť `linux/amd64`, zatiaľ čo runtime node je `arm64`.

Kľúčové je nájsť prvú vrstvu, na ktorej sa očakávaný a pozorovaný stav rozídu. Container, VM, image, process, network endpoint a persistentné dáta nie sú jedna identita a nemajú rovnaký lifecycle.

## Čo si z kapitoly odniesť

Container je izolovaný hostiteľský process alebo skupina procesov, nie malá VM. VM pridáva virtual hardware, guest kernel a hypervisor boundary. V praxi sa často kombinujú: VM vytvára node a kernel failure domain, container predstavuje menšiu aplikačnú jednotku.

Image nie je bežiaci container, `running` nie je `ready` a writable layer nie je persistentný data store. Rebuild image-u nepatchuje kernel a výmena VM neaktualizuje aplikačný artifact. Správny návrh preto musí oddeliť packaging, runtime isolation, persistence, networking, patching a recovery.

## Primárne zdroje

- [Docker overview](https://docs.docker.com/get-started/docker-overview/)
- [Docker Engine security](https://docs.docker.com/engine/security/)
- [Running containers](https://docs.docker.com/engine/containers/run/)
- [Resource constraints](https://docs.docker.com/engine/containers/resource_constraints/)
- [Rootless mode](https://docs.docker.com/engine/security/rootless/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Terraform vs. Ansible](../07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Namespaces, cgroups a capabilities →](namespaces-cgroups-capabilities.md)
<!-- KNOWLEDGE-NAVIGATION:END -->