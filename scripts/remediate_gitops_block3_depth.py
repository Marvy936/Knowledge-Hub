#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected remediation marker not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


golden = ROOT / "docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md"
replace_once(
    golden,
    "Path testovanie musí pokryť viac než render skeletonu. Test subject má obsahovať exact generation a representative input matrix.\n\nTesting layers:",
    "Path testovanie musí pokryť viac než render skeletonu. Test subject má obsahovať exact generation a representative input matrix.\n\n"
    "Jednotlivé testovacie vrstvy sledujú ten istý path subject cez odlišné failure boundaries. Schema test môže dokázať, že input vytvorí očakávané súbory, ale nevie preukázať, že delegated identity smie vytvoriť databázu, že composition nevytvorí konflikt ownershipu ani že výsledný workload vykoná business operáciu. Preto sa evidence skladá od lacného deterministického renderu cez sandbox mutation a complete composition až po developer journey a runtime canary.\n\n"
    "Rozhodujúca je kontinuita identity: každý result musí uviesť path generation, resolved dependencies, input digest a output inventory. Bez nej môže upgrade testovať inú action image než produkčný scaffolder alebo happy-path demo nevedomky používať oprávnenia platform engineera, ktoré cieľový používateľ nemá. Failure v jednej vrstve preto neobchádza nižšie gates; zužuje presný boundary, na ktorom path contract neplatí.\n\n"
    "Testing layers:",
)

self_service = ROOT / "docs/16-gitops-and-platform-engineering/self-service.md"
replace_once(
    self_service,
    "Self-service neodstraňuje podporu. Mení ju z rutinného vykonávania na product assistance, exception handling a incident recovery. Support musí používať rovnakú operation identity a evidence ako používateľ, inak vzniká paralelný neauditovaný proces.\n\nDobrá podpora poskytuje:",
    "Self-service neodstraňuje podporu. Mení ju z rutinného vykonávania na product assistance, exception handling a incident recovery. Support musí používať rovnakú operation identity a evidence ako používateľ, inak vzniká paralelný neauditovaný proces.\n\n"
    "Support boundary začína tam, kde automatizovaný state machine nevie bezpečne rozhodnúť bez nového ľudského vstupu, exception authority alebo externého zásahu. Podpora preto najprv načíta authoritative operation, child-operation IDs, last confirmed state a recovery options; nevytvára nový ticket-only workflow, ktorý by stratil väzbu na pôvodný request. Ak napríklad databáza čaká na kapacitu, support nemá označiť request za hotový ani ju vytvoriť bokom pod inou identity. Má zaznamenať dependency, ownera, next observation time a povolený resume alebo cancel transition.\n\n"
    "Tým sa support stáva súčasťou product feedback loopu. Opakovaná manuálna oprava je evidence chýbajúceho preflightu, slabého error modelu alebo absentnej capability, nie trvalý úspešný fallback. Support SLO preto sleduje čas k ďalšiemu dôveryhodnému rozhodnutiu a k usable outcome-u, nie iba čas prvej odpovede.\n\n"
    "Dobrá podpora poskytuje:",
)
replace_once(
    self_service,
    "Self-service interface je privileged automation surface. Threat model zahŕňa compromised user account, malicious inputs, confused deputy, privilege escalation, resource exhaustion, cross-tenant reference, secret exfiltration a destructive request.\n\nControls musia byť kompozitné:",
    "Self-service interface je privileged automation surface. Threat model zahŕňa compromised user account, malicious inputs, confused deputy, privilege escalation, resource exhaustion, cross-tenant reference, secret exfiltration a destructive request.\n\n"
    "Threat sa realizuje cez celý request-to-mutation chain, nie iba cez formulár. Principal môže byť legitímne autentizovaný, ale požiadať o cudzí namespace; schema-valid input môže vložiť nebezpečný IAM wildcard; delegated orchestrator môže ako confused deputy použiť broad credential nad nesprávnym tenantom; retry po unknown outcome môže zdvojiť drahý resource. Security decision preto viaže requester identity, owner, semantic request digest, approved plan, delegated principal, target inventory a observed outcome.\n\n"
    "Controls sa skladajú sekvenčne. Authentication určí kto žiada, authorization a policy rozhodnú čo smie nad ktorým subjectom, semantic validation obmedzí význam vstupu, quota a admission chránia shared capacity a delegated execution vynucuje least privilege pri reálnej mutation. Read-back, audit a anomaly detection potom dokazujú, čo sa skutočne stalo. Vynechanie jednej boundary nemožno kompenzovať skrytím tlačidla v UI; API alebo orchestrator by stále zostali zneužiteľné.\n\n"
    "Controls musia byť kompozitné:",
)

devex = ROOT / "docs/16-gitops-and-platform-engineering/developer-experience.md"
replace_once(
    devex,
    "Acceptance verdict musí dokázať zlepšenie konkrétneho developer journey a vysvetliť mechanismus. Nemôže byť založený na jednej activity metrike, voluntary survey úspešných používateľov alebo priemere bez cohortov.\n\nDeveloper-experience design je prijatý, keď:",
    "Acceptance verdict musí dokázať zlepšenie konkrétneho developer journey a vysvetliť mechanismus. Nemôže byť založený na jednej activity metrike, voluntary survey úspešných používateľov alebo priemere bez cohortov.\n\n"
    "Verdict preto koreluje tri vrstvy. Experience evidence ukazuje, či používateľ rozumel stavu, dôveroval systému a zvládol rozhodnutie bez neprimeranej cognitive load. Flow evidence meria waiting, handoffs, rework a čas k usable outcome-u. Guard outcomes dokazujú, že zdanlivé zrýchlenie nezvýšilo incidenty, security exceptions, support toil alebo downstream business chyby. Zlepšenie je prijaté iba vtedy, keď sa tieto vrstvy vzťahujú na rovnaký cohort, journey generation a časové okno.\n\n"
    "Mechanistické vysvetlenie odlišuje koreláciu od príčiny. Ak time-to-first-production klesne po novom path-e, treba ukázať, ktorú wait alebo decision boundary path odstránil, či sa nezmenila zložitosť workloadov a či benefit pretrval pri druhom tíme, prvom failure a druhej zmene. Bez tejto triangulácie môže dashboard pripísať platforme sezónne ľahší workload alebo vylúčiť abandoned requests a vytvoriť false-positive DevEx verdict.\n\n"
    "Developer-experience design je prijatý, keď:",
)

print("Deepened GitOps block 3 critical sections")
