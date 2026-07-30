#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_exact(path: str, old: str, new: str) -> None:
    file = ROOT / path
    text = file.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}")
    file.write_text(text.replace(old, new), encoding="utf-8")


replace_exact(
    "docs/14-sre-and-operations/backup-and-restore.md",
    """## 3. Backup, replication, snapshot, archive a export\n\nTieto artifacts riešia odlišné problems:\n\n- **backup —** recovery-oriented copy s policy, retention, catalogom a restore pathom;\n""",
    """## 3. Backup, replication, snapshot, archive a export\n\nTieto artifacts riešia odlišné problems a systém ich používa na iných boundaries. Backup je spravovaný recovery contract: policy určuje, ktorý subject sa zachytí, ako dlho sa uchová a ako sa nájde a obnoví. Replication je availability mechanismus, ktorý udržiava ďalší current copy, ale zvyčajne zdieľa mutation stream a preto rýchlo prenesie logical corruption. Snapshot, archive a export zase menia point-in-time, retention alebo portability semantics.\n\nRozlíšenie rozhoduje o tom, ktorý failure model je pokrytý. Live replica pomôže pri instance loss-e, no nemusí poskytnúť clean historical point; archive zachová históriu, no nemusí splniť krátky RTO. Restore materializuje artifact, zatiaľ čo recovery až overí business capability.\n\n- **backup —** recovery-oriented copy s policy, retention, catalogom a restore pathom;\n""",
)

replace_exact(
    "docs/14-sre-and-operations/root-cause-analysis.md",
    """Užitočná RCA rozlišuje viac príčinných vrstiev:\n\n- **technical root cause —** missing scope sa pri destructive query interpretoval ako wildcard;\n""",
    """Užitočná RCA rozlišuje viac príčinných vrstiev, pretože každá vedie k inému controlu. Technical root cause opisuje executable failure mechanismus. Systemic cause vysvetľuje design alebo governance, ktorý mechanismus dovolil. Escape a detection causes patria delivery a observability boundaries; amplification vysvetľuje blast radius a recovery-delay cause nepripravenosť obnovy. Bez tejto taxonómie by tím opravil query, ale ponechal broad database role, weak canary aj stale restore workload identity.\n\nV incidente sa preto analyzuje nielen prvá chybná mutation, ale aj to, prečo test, policy, detection a recovery paths nedokázali incident zastaviť alebo rýchlo napraviť. Jednotlivé causes nie sú konkurenčné odpovede; tvoria causal portfolio jedného outcome-u.\n\n- **technical root cause —** missing scope sa pri destructive query interpretoval ako wildcard;\n""",
)

replace_exact(
    "docs/14-sre-and-operations/rpo-and-rto.md",
    """## 7. Target verzus actual measurement\n\nObjective a nameraný výsledok majú samostatné fields:\n\n- **RPO target —** požadovaný recovery point;\n""",
    """## 7. Target verzus actual measurement\n\nRecovery objective je plánovaný limit; actual measurement je evidence z konkrétneho incidentu alebo exercise-u. RPO target určuje najstarší prijateľný business-valid point, zatiaľ čo actual recovered point identifikuje timestamp alebo sequence, ktorý bol skutočne obnovený. RTO target určuje maximálny prijateľný interval a actual recovery time meria celý definovaný start-to-end path. Tieto hodnoty sa nesmú zapisovať do jedného poľa, lebo by želaný contract prepisoval nameranú realitu.\n\nVýsledok zároveň potrebuje vysvetliť, čo bolo permanentne stratené, čo sa rekonštruovalo a koľko času spotrebovali technical restore a work recovery. Až táto kombinácia ukáže, či target prešiel a kde vznikol gap.\n\nObjective a nameraný výsledok majú samostatné fields:\n\n- **RPO target —** požadovaný recovery point;\n""",
)

replace_exact(
    "docs/14-sre-and-operations/rpo-and-rto.md",
    """## 9. Corrective objective generation `REC-PAY-55`\n\nNový contract oddelil permanent loss, initial reconstructability a staged service recovery:\n\n```text\n""",
    """## 9. Corrective objective generation `REC-PAY-55`\n\nPôvodný objective miešal data-loss invariant, initial recovery point, safe new traffic a historical work recovery do jedného RPO/RTO páru. Nová generation tieto boundaries oddeľuje, aby architecture a exercise mohli každú zmerať samostatne. Permanent loss je hard invariant, business-consistent replay window je point objective a staged RTOs určujú, kedy sa vracia durable admission, automatic completion a nakoniec historical reconciliation.\n\nToto rozdelenie neoslabuje business commitment. Naopak odhaľuje, či služba iba prijíma nové intents, či ich vie bezpečne dokončiť a či už uzavrela affected historical cohort. Každý target má vlastný observation point a nesmie byť splnený green stavom inej boundary.\n\nNový contract oddelil permanent loss, initial reconstructability a staged service recovery:\n\n```text\n""",
)

print("SRE block 3 depth remediation complete")
