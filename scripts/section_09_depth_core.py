from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "09-kubernetes"


def read(name: str) -> str:
    return (SECTION / name).read_text(encoding="utf-8")


def write(name: str, text: str) -> None:
    (SECTION / name).write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def insert(name: str, heading: str, prose: str) -> None:
    text = read(name)
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
    write(name, text[:start] + "\n" + body + "\n\n" + text[start:].lstrip("\n"))


def replace(name: str, old: str, new: str) -> None:
    text = read(name)
    if new.strip() in text:
        return
    if old not in text:
        raise RuntimeError(f"Expected block not found: {name}")
    write(name, text.replace(old, new, 1))


replace(
    "desired-state-reconciliation-loops.md",
    """Reconcile musí byť správny aj vtedy, keď dostane:

- viac rovnakých eventov,
- iba poslednú z viacerých rýchlych zmien,
- delete tombstone namiesto plného objektu,
- stale cache snapshot,
- event po reštarte controllera.

Tieto prípady sú prirodzenou súčasťou distribuovaného systému.""",
    """Reconcile nesmie odvodzovať správnosť z toho, že event stream je úplný a presne zoradený. Viac rovnakých eventov musí viesť k rovnakému effective state-u, pretože queue môže objekt zaradiť opakovane. Ak sa niekoľko zmien udeje rýchlo za sebou, controller môže vidieť iba poslednú resourceVersion; autoritatívnym vstupom je preto aktuálny objekt z cache alebo API, nie historická sekvencia callbackov.

Delete tombstone môže niesť iba identity potrebné na cleanup, stale cache snapshot môže dočasne zaostávať za API serverom a po reštarte controllera prídu objekty bez zachovanej lokálnej histórie. Controller má v každom prípade znovu zostaviť exact subject z UID, generation a external identity, porovnať desired a observed state a vykonať iba idempotentný transition. Periodický resync zvyšuje šancu na opätovné spracovanie; neopravuje reconcile logiku, ktorá potrebuje stratený event alebo poradie eventov na dosiahnutie správneho výsledku.""",
)

replace(
    "desired-state-reconciliation-loops.md",
    """Pri zlyhaní sa pýtaj v tomto poradí:

1. Aký desired state je aktuálne persistovaný?
2. Ktorý controller vlastní ďalší transition?
3. Spracoval aktuálnu generation?
4. Aký dependent object alebo external effect mal vzniknúť?
5. Existuje, ale má zlý stav, alebo vôbec nevznikol?
6. Je retry bezpečný a idempotentný?
7. Ktorý writer vlastní problematický field?

Takto sa vyhneš plošnému restartovaniu controllerov bez pochopenia, či je problém v stale cache, admission, ownership konflikte alebo samotnom external API.""",
    """Troubleshooting reconcile začína persistovaným desired state-om, nie logom controllera. Najprv zafixuj API object cez name, UID, generation a resourceVersion a urč, ktorý controller alebo field manager vlastní nasledujúci transition. Potom porovnaj `metadata.generation` s `status.observedGeneration`; staršia observed generation znamená, že status ešte nepatrí aktuálnemu intentu.

Ďalší krok sleduje konkrétny dependent object alebo external effect. Over ownerReference alebo stabilnú external identity a rozlíš tri outcomes: objekt nevznikol, vznikol so zlým stavom alebo mutation mohla uspieť, ale výsledok zostal neznámy. Až podľa tohto read-backu rozhodni, či je retry bezpečný. Nakoniec skontroluj managedFields a ďalších writerov problematického fieldu, pretože restart controllera nevyrieši admission odmietnutie, ownership konflikt ani chybu externého API a môže iba prekryť pôvodnú evidence.""",
)

insert(
    "kubernetes-troubleshooting.md",
    "## Service nemá endpoints",
    """Service object je iba stabilná virtuálna identita a port contract. Backend inventory vzniká až v EndpointSlice objects, ktoré controller skladá z Podov zodpovedajúcich selectoru a z ich readiness state-u. Diagnostika preto musí porovnať Service selector a port mapping s konkrétnymi Pod labels, Pod UID a ready condition; samotná existencia Service nepreukazuje, že existuje jediný routovateľný backend.""",
)

insert(
    "kubernetes-troubleshooting.md",
    "## Detailný incident: green cluster, intermittent 502 po Node upgrade-e",
    """Incident je vedený ako porovnanie dvoch Node generations pri rovnakom application image a configuration generation. Cieľom nie je hľadať prvý červený status, ale zafixovať failing request, backend Pod UID a Node UID, nájsť prvý rozdiel medzi zdravou a chybnou cohortou a oddeliť application, Service, CNI a telemetry failures. Až tento causal chain určí bezpečný containment a replacement boundary.""",
)

insert(
    "rbac.md",
    "## Kontrola permissions",
    """Permission check musí používať rovnaký subject, namespace, verb, resource a subresource ako plánovaná operácia. `kubectl auth can-i` posiela API serveru authorization review a odpovedá na otázku, či by authorizer daný request povolil; nepreukazuje, že objekt existuje, že admission request prijme ani že external cloud identity dovolí následný efekt. Pozitívny test preto dopĺňa explicitný forbidden test pre susedný Secret, namespace alebo verb.""",
)

replace(
    "rbac.md",
    """Identita, ktorá smie vytvárať Pods, môže:

- vybrať povolený ServiceAccount,
- mountnúť dostupný Secret,
- použiť hostPath alebo privileged context, ak admission dovolí,
- spustiť image s vlastným kódom,
- pristúpiť k network a cloud metadata podľa platformy.

Preto „nemá get secrets“ nemusí znamenať „nevie získať secret“. Admission, ServiceAccount use policy, Pod Security a node isolation musia doplniť RBAC.""",
    """Právo vytvoriť Pod je nepriamou code-execution authority v namespace. Caller môže zvoliť ServiceAccount, ktorý Pod použije, a tým získať jeho Kubernetes alebo federovanú cloud identity. Môže pripojiť Secret, ktorý kubelet smie materializovať pre workload, aj keď caller nemá priamy `get` na Secret API. Vložením vlastného image alebo commandu potom dokáže hodnotu prečítať z procesu alebo filesystemu.

Ak admission dovolí `hostPath`, privileged SecurityContext alebo neobmedzené capabilities, Pod creation môže prekročiť namespace boundary až k Node-u. Aj bez host accessu môže workload použiť povolený network egress alebo cloud metadata endpoint. Preto tvrdenie „identita nemá `get secrets`“ nie je kompletný confidentiality verdict. Effective boundary vzniká kombináciou RBAC, obmedzenia použiteľných ServiceAccounts, Pod Security alebo admission, secret mounting policy, Node isolation, NetworkPolicy a cloud workload identity controls.""",
)

print("Applied Section 09 reconciliation, troubleshooting and RBAC pass.")
