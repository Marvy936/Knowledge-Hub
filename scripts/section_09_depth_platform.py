from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "09-kubernetes"


def insert(name: str, heading: str, prose: str) -> None:
    path = SECTION / name
    text = path.read_text(encoding="utf-8")
    marker = heading + "\n"
    pos = text.find(marker)
    if pos == -1:
        raise RuntimeError(f"Heading not found: {name}: {heading}")
    start = pos + len(marker)
    next_heading = text.find("\n## ", start)
    end = len(text) if next_heading == -1 else next_heading
    body = prose.strip()
    if body in text[start:end]:
        return
    updated = text[:start] + "\n" + body + "\n\n" + text[start:].lstrip("\n")
    path.write_text(updated.rstrip() + "\n", encoding="utf-8", newline="\n")


insert(
    "cluster-installation-lifecycle.md",
    "## Capability gate pre nový Node",
    """`Ready=True` potvrdzuje, že kubelet reportuje základnú Node pripravenosť; nepreukazuje funkčný CNI dataplane, CSI attach alebo mount, DNS path, registry pull, Service translation ani policy enforcement. Nová Node generation preto zostáva za bootstrap taintom, kým capability canary s presným Pod a Node UID neoverí image pull, Pod sandbox, same-Node aj cross-Node traffic, Service alebo DNS request, storage operáciu a požadované security controls.

Gate sa otvára až pre cohortu s rovnakým image, kubelet alebo runtime a add-on generation. Zlyhanie canary zastaví ďalšie untaintovanie alebo rollout Node poolu a zachová Node-local logs, routes, mounts a runtime evidence. Tým sa `Ready` používa ako jeden signal v širšom acceptance contracte, nie ako platform verdict.""",
)

insert(
    "cni-networkpolicy.md",
    "## Povolenie databázového egressu",
    """Egress policy sa vyhodnocuje pre source Pods vybrané `podSelectorom`; destination namespace a Pod selectory následne určujú, ku ktorým endpointom a portom smie traffic odísť. Povolenie databázy preto musí viazať source workload identity, destination namespace identity, database Pod labels, protokol a port. Samotný DNS názov nie je NetworkPolicy subject.

Po aplikovaní treba overiť allowed flow z konkrétneho `payments-api` Pod UID a forbidden flow z neoznačeného Podu alebo na susedný port. Ak databáza stojí mimo Pod networku, treba samostatne modelovať `ipBlock`, NAT a provider implementation; YAML acceptance bez dataplane testu nepreukazuje effective egress.""",
)

insert(
    "configmap-secret.md",
    "## Deployment rollout cez explicitnú generáciu",
    """Zmena ConfigMap alebo Secret objectu sama osebe nemení Deployment Pod template a preto nevytvorí nový ReplicaSet. Explicitná configuration generation alebo checksum annotation prenesie source zmenu do `.spec.template.metadata`, čím sa zmení Pod-template hash a controller vytvorí novú revision. Hodnota annotation musí byť deterministicky odvodená z presne schváleného config alebo secret subjectu, nie z mutable názvu bez epochy.

Rollout evidence potom spája source resourceVersion alebo digest, Deployment generation, nový ReplicaSet UID, Pod UIDs a process-loaded generation. Nový Pod s annotation `C53` ešte nepreukazuje, že volume projection alebo environment obsahuje správne bytes a že aplikácia ich načítala; to uzatvára runtime endpoint alebo bezpečný metadata read-back.""",
)

insert(
    "deployment.md",
    "## Rollout evidence po vrstvách",
    """Rollout nie je jeden status, ale reťazec identít. Source manifest a image digest vedú k admitted Deployment generation; Deployment controller vytvorí ReplicaSet s konkrétnym UID a Pod-template hashom; ReplicaSet vytvorí Pods s vlastnými UID; kubelet spustí runtime s imageID a probes rozhodnú o readiness; EndpointSlice až potom publikuje serving backends.

`kubectl rollout status` uzatvára iba Deployment controller contract podľa observedGeneration, available replicas a progress conditions. Release acceptance preto koreluje Deployment, ReplicaSet a Pod identities, runtime image a configuration generation, ready endpoints a request alebo business outcome. Tak možno rozlíšiť green rollout so zlým imageID, ready Pods mimo Service selectoru alebo dostupnú kapacitu s chybným payment behaviorom.""",
)

insert(
    "hpa-autoscaling.md",
    "## Základný HPA",
    """HPA je writerom scale subresource-u cieľového workloadu. `scaleTargetRef` musí resolve-nuť presný Deployment a metric contract musí mať známu unit, aggregation window a population; pri CPU utilization je denominatorom resource request každého eligible Podu. `minReplicas` a `maxReplicas` sú bounds desired countu, nie rezervovaná serving kapacita.

Po prijatí objektu treba oddeliť HPA recommendation, zapísaný Deployment replica count, vytvorené Pods, schedulované a Ready Pods a Service capacity. GitOps alebo iný controller nesmie súčasne neustále zapisovať statickú `.spec.replicas`, inak vznikne ownership oscillation medzi dvoma správne fungujúcimi control loops.""",
)

insert(
    "hpa-autoscaling.md",
    "## Observácia HPA",
    """Observácia začína exact HPA generation a scale targetom, potom porovná current metrics s timestamps, computed desired replicas a skutočným scale subresource-om Deploymentu. Conditions `AbleToScale`, `ScalingActive` a `ScalingLimited` opisujú jednotlivé controller decisions; bez reason alebo message a aktuálnosti metrík nie sú samostatným health verdictom.

Ak desired count rastie, diagnostika pokračuje cez ReplicaSet Events, quota alebo admission, scheduler a Node capacity až po readiness a EndpointSlice. HPA môže byť úplne zdravá, aj keď serving capacity nerastie, pretože ďalší transition vlastní iný controller alebo platform component.""",
)

insert(
    "job-cronjob.md",
    "## Pozorovanie a logs",
    """Job status agreguje completion a failure nad viacerými Pod attempts, ale root cause patrí ku konkrétnemu Pod UID, container restart alebo termination state a časovej osi. Pri retry môže nový Pod vykonať rovnakú business operáciu znova; preto treba uchovať všetky attempt identities a nekontrolovať iba log posledného úspešného Podu.

Pozorovanie spája Job UID a generation, ownerReferences Podov, completion indexes alebo schedule time, exit codes a application operation key. `kubectl logs job/<name>` je convenience view, nie garantovaný kompletný audit všetkých attempts; pri incidente sa logs a status čítajú per Pod a porovnajú sa s durable business ledgerom.""",
)

print("Applied Section 09 platform controller and autoscaling pass.")
