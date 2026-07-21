# Container Fundamentals and Docker glossary entries

## Container

Izolovaný runtime process alebo skupina procesov používajúca host kernel a oddelený pohľad na resources cez namespaces, cgroups a ďalšie security controls. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Container escape

Prelomenie container isolation boundary, pri ktorom process získa access k hostu alebo iným workloads. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Container image

Versionovaný a typicky content-addressed filesystem a runtime-metadata artifact používaný na vytvorenie container instance; bežne neobsahuje kernel použitý pri runtime. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Container runtime

Software vrstva pripravujúca container filesystem, namespaces, cgroups, process a lifecycle podľa runtime configuration alebo štandardu. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Ephemeral runtime instance

Nahraditeľná runtime inštancia, ktorej lokálny procesový a writable-layer stav nie je považovaný za jediný persistentný zdroj dát. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Guest operating system

Operačný systém bežiaci vo virtual machine nad virtualizovaným hardware a vlastným guest kernelom. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Hypervisor

Virtualization vrstva poskytujúca virtual hardware a izoláciu pre virtual machines. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Isolation boundary

Technická a bezpečnostná hranica oddeľujúca workload od hosta alebo iných workloads, napríklad shared-kernel container boundary alebo hypervisor/VM boundary. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## MicroVM

Minimalizovaná virtual machine navrhnutá na rýchlejší startup a menší overhead pri zachovaní samostatnej virtualized-kernel boundary. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Sandboxed container runtime

Runtime model pridávajúci medzi container workload a host kernel ďalšiu isolation vrstvu, napríklad user-space kernel alebo lightweight virtual machine. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Shared kernel

Model, v ktorom viac host a container processes používa ten istý kernel, hoci môže mať odlišné namespace views a resource limits. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Virtual machine — VM

Izolovaný machine environment s virtualizovaným hardware, vlastným guest kernelom a guest userspace, ktorý poskytuje hypervisor. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## VM escape

Prelomenie guest/hypervisor isolation boundary, pri ktorom code z virtual machine ovplyvní hypervisor, host alebo inú VM. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Workload density

Počet alebo množstvo workloads, ktoré možno bezpečne a výkonovo prevádzkovať na spoločnej infraštruktúre pri danom resource a isolation modeli. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Writable layer — container

Dočasná zapisovateľná filesystem vrstva konkrétnej container instance umiestnená nad read-only image layers, ktorej lifecycle je typicky viazaný na container. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).
