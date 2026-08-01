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
    "kubernetes-practical-walkthrough.md",
    "## 6. Deployment: jedna úplná Pod template",
    """Pod template je rollout identity Deploymentu. Každá zmena labels, annotations, image digestu, configuration alebo secret generation, ServiceAccountu, SecurityContextu, resources, volumes alebo probes vytvorí nový Pod-template hash a tým nový ReplicaSet. Manifest preto skladá tieto polia ako jeden reviewovateľný runtime contract, nie ako nezávislý zoznam YAML možností.

V walkthroughe musí template súčasne spĺňať Restricted security boundary, mať explicitné writable paths, stabilné scheduling inputs a probes viazané na skutočný application lifecycle. Neskorší read-back prepojí source digest a generations s ReplicaSet UID, Pod UIDs, Node assignmentom, runtime imageID, loaded configuration a ready EndpointSlice.""",
)

insert(
    "kubernetes-practical-walkthrough.md",
    "## 17. Diff",
    """Diff je pre-mutation porovnanie medzi serverom resolve-nutým proposed objectom a aktuálnym live objectom pre rovnaký field manager. Server-side režim zahŕňa schema, defaulting, admission a managed-field ownership, takže výsledok je bližšie apply semantics než lokálny textový diff. CI musí rozlíšiť exit code pre nulový rozdiel, nájdený rozdiel a tool alebo API chybu.

Review kontroluje nielen zmenené YAML fields, ale aj identity a následky: či sa mení Pod template a vznikne revision, či selector zostáva immutable-compatible, či sa nepreberá field vlastnený HPA alebo iným managerom a či security alebo admission defaulting nevytvorili neočakávaný effective object. Diff stále nepreukazuje controller convergence ani runtime outcome.""",
)

insert(
    "kubernetes-practical-walkthrough.md",
    "## 18. Apply",
    """Server-side apply odošle deklarované fields s explicitným field managerom. API server request autentizuje, autorizuje, preženie admissionom, vyrieši field ownership a persistuje novú object generation; úspešná odpoveď preto potvrdzuje API transition, nie vytvorený ReplicaSet, schedulovaný Pod alebo fungujúci Service.

Bezprostredne po mutation sa zachová Deployment UID, generation a resourceVersion a sleduje sa observedGeneration, nový ReplicaSet, Pod UIDs, Node assignment, imageID, readiness a EndpointSlice. Ak klient stratí odpoveď, apply sa neopakuje naslepo ako nový intent; najprv sa read-backne live object a managedFields, aby sa unknown outcome zmenil na known persisted alebo not-persisted state.""",
)

insert(
    "kubernetes-practical-walkthrough.md",
    "## 30. Čo walkthrough dokázal",
    """Záverečný verdict je evidence matrix nad jednou walkthrough generation, nie tvrdenie, že Kubernetes je všeobecne zdravý. Každý bod nižšie patrí ku konkrétnemu source renderu, admitted objectom, controller graphu, Pod alebo Node a runtime identitám a request pathu vykonanému v tomto prostredí.

Rovnako dôležitá je negatívna hranica. Nevykonané external Gateway, production database, multi-zone, CSI recovery alebo upgrade scenáre nemožno odvodiť z úspešného namespace labu. Výsledok preto oddeľuje presne preukázané transitions od capabilities, ktoré vyžadujú samostatný target environment a acceptance test.""",
)

insert(
    "probes.md",
    "## Conditions a EndpointSlice",
    """Kubelet zapisuje container a Pod conditions, ale Service backend eligibility vzniká až kombináciou Pod readiness, Service selectoru a EndpointSlice controllera. `ContainersReady=True` opisuje container readiness v Pode; `Ready=True` môže zahŕňať additional readiness gates. EndpointSlice condition `ready=true` následne hovorí, že konkrétny endpoint je publikovaný ako ready backend pre daný Service inventory.

Diagnostika preto koreluje Pod UID a conditions s EndpointSlice targetRef UID. Liveness success nepreukazuje readiness a Ready Pod nepreukazuje, že ho vyberá správny Service. Request test cez Service uzatvára dataplane boundary, ktorú samotné conditions neoverujú.""",
)

insert(
    "requests-limits-qos.md",
    "## QoS classes",
    """QoS class sa vypočíta z requests a limits všetkých containers v Pode. `Guaranteed` vyžaduje pre každý CPU a memory resource rovnaký request a limit; `Burstable` pokrýva ostatné Pods s aspoň jedným requestom alebo limitom a `BestEffort` nemá ani jedno. Class je teda vlastnosť admitted Pod specu, nie voľne nastavený label.

Kubelet používa QoS spolu s usage, priority a Node pressure pri eviction rozhodovaní. Vyššia class znižuje relatívne riziko, ale negarantuje prežitie, výkon ani absenciu OOM v container limite. Read-back musí kontrolovať effective requests a limits po admission a skutočný Pod `status.qosClass`.""",
)

insert(
    "resourcequota-limitrange.md",
    "## ResourceQuota pre compute",
    """ResourceQuota je namespace admission accounting boundary. Pri create alebo update requeste quota controller porovná nový aggregate request alebo limit a object count s hard limitom; ak by ho prekročil, API object nevznikne. Quota nereprezentuje voľnú Node kapacitu ani negarantuje, že prijatý Pod bude schedulovateľný.

Kontrola preto porovnáva `hard` a `used` pre presný namespace a následne sleduje ReplicaSet Events. HPA alebo Deployment môže zvýšiť desired replicas, zatiaľ čo quota odmieta nové Pods; controller intent a serving capacity zostanú rozdielne states.""",
)

insert(
    "resourcequota-limitrange.md",
    "## LimitRange defaults",
    """LimitRange admission môže doplniť default requests alebo limits a odmietnuť hodnoty mimo min, max alebo ratio contractu. Effective Pod spec preto nemusí byť totožný so source YAML. Doplnený CPU request ovplyvní scheduler aj HPA utilization denominator a doplnený memory limit vytvorí runtime OOM boundary.

Pred rolloutom sa používa server-side dry-run a číta admitted Pod template alebo vytvorený Pod, aby sa defaulting zahrnul do capacity a autoscaling modelu. Následný quota výpočet pracuje s týmito effective hodnotami, nie s tým, čo autor vynechal zo source manifestu.""",
)

insert(
    "resourcequota-limitrange.md",
    "## LimitRange pre PVC",
    """PVC LimitRange môže obmedziť alebo defaultovať requested storage pre claims v namespace. Admission tým kontroluje API request size, ale nepreukazuje dostupnú StorageClass kapacitu, topology-compatible PV ani úspešný CSI provisioning.

Read-back preto sleduje admitted PVC request, StorageClass, PVC alebo PV UID, binding mode, selected Node pri delayed bindingu a CSI volumeHandle. Prijatý PVC môže zostať Pending a `Bound` PVC stále nepreukazuje attach, mount ani správnu data generation.""",
)

insert(
    "scheduling.md",
    "## Events a unschedulable message",
    """Scheduler vytvára alebo aktualizuje PodScheduled condition a Event s dôvodom, prečo žiadna Node neprešla filteringom alebo scoring neviedol k bindu. Message je agregované vysvetlenie pre daný scheduling attempt; treba ho čítať spolu s exact Pod UID a spec, aktuálnym Node inventory a scheduler profilem.

Events sú časovo obmedzené a môžu sa agregovať, preto sa pri incidente zachovajú skôr než zmiznú. `0/20 nodes are available` nie je automatický dôvod pridať Nodes: affinity, taint, topology, volume binding, host ports, quota alebo resource request môžu vytvárať constraints, ktoré nová nesprávna Node group nevyrieši.""",
)

insert(
    "taints-tolerations-affinity-topology.md",
    "## Toleration v Pode",
    """Taint odpudzuje Pods podľa key, value a effect a toleration iba ruší túto konkrétnu prekážku. Toleration nevyberá Node, negarantuje scheduling na tainted cohortu a neoveruje, že Node má požadovanú capability. Ak má workload bežať iba na GPU alebo hardened Nodes, potrebuje popri toleration aj nodeSelector alebo required node affinity viazanú na dôveryhodný Node label.

Exact effect mení lifecycle: `NoSchedule` blokuje nové umiestnenie, `PreferNoSchedule` je mäkký signal a `NoExecute` môže evictovať existujúci Pod podľa `tolerationSeconds`. Read-back preto kontroluje Pod spec, Node taints, scheduler decision a prípadnú eviction časovú os.""",
)

insert(
    "upgrades.md",
    "## Presný current a target inventory",
    """Upgrade subject nie je iba Kubernetes minor version. Current inventory zahŕňa control-plane a Node versions, kubelet alebo runtime, API resources a stored versions, CRDs a conversion webhooks, admission webhooks, CNI, CSI, DNS a metrics add-ons a jednotlivé Node image generations. Target inventory pinne ich kompatibilné successor versions a podporovaný version-skew path.

Pred mutation sa inventory viaže na konkrétny cluster UID a cohorty. Discovery, deprecated API scan, webhook reachability a add-on compatibility rozhodnú, či je target vôbec admissible. Po každom kroku sa porovná API alebo control-plane health, controller progress, Node capability canary a workload a business outcomes; zelený control plane nepreukazuje, že nová Node alebo dataplane generation je pripravená.""",
)

print("Applied Section 09 practical, resource and upgrade pass.")
