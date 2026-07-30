#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_exact(relative_path: str, old: str, new: str) -> None:
    path = ROOT / relative_path
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match in {relative_path}, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


replace_exact(
    "docs/14-sre-and-operations/reliability-availability-durability.md",
    """Reliability je širšia než availability. Pre Atlas settlement journey obsahuje najmenej päť samostatných vlastností:\n\n- **availability** — validný merchant môže operation začať a dostať pravdivý výsledok alebo bezpečný explicitný failure;\n""",
    """Reliability je širšia než availability. Availability opisuje použiteľnosť capability, correctness pravdivosť výsledku, latency časovú hranicu a durability schopnosť zachovať alebo reprodukovať už potvrdený business state. Pre Atlas settlement journey sa tieto vlastnosti vyhodnocujú samostatne, pretože každá má inú failure boundary a iný authoritative dôkaz.\n\n- **availability** — validný merchant môže operation začať a dostať pravdivý výsledok alebo bezpečný explicitný failure;\n""",
)

replace_exact(
    "docs/14-sre-and-operations/reliability-availability-durability.md",
    """## 12. Anti-patterny\n\n### Uptime equals reliability\n\nRunning proces alebo úspešný health check nepreukazuje correctness, durability ani final business completion.\n\n### Replication equals backup\n\nReplication zvyšuje availability a odolnosť voči physical failure-u, ale replikuje aj chybnú mutation. Recovery potrebuje oddelenú lineage a restore test.\n\n### `202` znamená, že sa o to systém postará\n\n`202` je sľub iba v rozsahu server-side contractu. Bez durable intentu, status identity a bounded completion/failure semantics je nepravdivý.\n\n### Globálny priemer\n\nAggregate availability môže skryť úplný failure kritického tenant-a, Regionu alebo release cohorty.\n\n### Recovery overená počtom rows\n\nTechnický row count nepreukazuje referential, workflow ani provider consistency. Validácia musí skončiť business outcome-om.\n""",
    """## 12. Anti-patterny\n\nNasledujúce skratky zamieňajú čiastkový technický signal za celý reliability outcome. Každá z nich odstráni dôležitú boundary z merania alebo recovery, a preto môže vytvoriť zelený verdict počas reálneho user impactu.\n\n- **Uptime equals reliability —** Running proces alebo úspešný health check nepreukazuje correctness, durability ani final business completion. Zelený process signal musí byť korelovaný s operation-level outcome-om.\n- **Replication equals backup —** Replication zvyšuje availability a odolnosť voči physical failure-u, ale replikuje aj chybnú mutation. Recovery potrebuje oddelenú lineage, restore test a business reconciliation.\n- **`202` znamená, že sa o to systém postará —** `202` je sľub iba v rozsahu server-side contractu. Bez durable intentu, status identity a bounded completion/failure semantics je acknowledgement nepravdivý.\n- **Globálny priemer —** Aggregate availability môže skryť úplný failure kritického tenant-a, Regionu alebo release cohorty. Critical cohorts preto potrebujú vlastný denominator a verdict.\n- **Recovery overená počtom rows —** Technický row count nepreukazuje referential, workflow ani provider consistency. Validácia musí skončiť pôvodným business outcome-om a forbidden duplicate/lost paths.\n""",
)

replace_exact(
    "docs/14-sre-and-operations/sli-slo-sla.md",
    """## 12. Anti-patterny\n\n### Začať metricou, ktorú už máme\n\nEasy-to-export CPU alebo HTTP status môže byť diagnostický signal, ale nie user-relevant SLI.\n\n### `2xx` equals success\n\nStatus code môže potvrdiť iba jednu protocol boundary. Async a business completion potrebuje samostatný oracle.\n\n### Missing telemetry equals zero errors\n\nEvidence outage znižuje confidence a môže vytvoriť blocking unknown state; nesmie zlepšiť SLI.\n\n### Jeden global objective\n\nAggregate SLO skryje tenant, Region, operation alebo release cohort failure.\n\n### SLA diktuje interné meranie\n\nExternal agreement je minimum commitmentu, nie horná hranica interného user-centric observability.\n""",
    """## 12. Anti-patterny\n\nTieto anti-patterny vznikajú, keď dostupný signal alebo contractual minimum nahradí user-centered measurement contract. Výsledkom je reprodukovateľné číslo, ktoré však odpovedá na inú otázku než používateľská spoľahlivosť.\n\n- **Začať metricou, ktorú už máme —** Easy-to-export CPU alebo HTTP status môže byť diagnostický signal, ale nie user-relevant SLI. Najprv sa definuje required outcome a až potom najbližší authoritative observation point.\n- **`2xx` equals success —** Status code môže potvrdiť iba jednu protocol boundary. Async a business completion potrebuje samostatný oracle a operation-level correlation.\n- **Missing telemetry equals zero errors —** Evidence outage znižuje confidence a môže vytvoriť blocking unknown state; nesmie zlepšiť SLI. Coverage a lateness sú preto súčasťou measurement generation.\n- **Jeden global objective —** Aggregate SLO skryje tenant, Region, operation alebo release cohort failure. Critical cohorts potrebujú samostatné views alebo hard non-aggregate gates.\n- **SLA diktuje interné meranie —** External agreement je minimum commitmentu, nie horná hranica interného user-centric observability. Interný SLO má odhaliť risk ešte pred contractual breachom.\n""",
)

replace_exact(
    "docs/14-sre-and-operations/error-budgets.md",
    """## 12. Anti-patterny\n\n### Budget ako povolenie míňať chyby\n\nBudget umožňuje bounded risk, nie vedomé poškodzovanie users alebo ignorovanie known defectu.\n\n### Percento bez operation countu a času\n\n`40 % zostáva` nehovorí, či ide o štyri alebo štyri milióny events ani ako rýchlo sa budget míňa.\n\n### Automatický freeze všetkého\n\nBlokuje aj changes, ktoré risk znižujú. Policy musí rozlišovať discretionary a remediation work.\n\n### Calendar reset ako recovery\n\nWindow reset mení číslo, nie production mechanismus.\n\n### Priemer budgets\n\nAvailability, correctness, durability a critical cohorts majú nekompenzovateľné verdicts.\n""",
    """## 12. Anti-patterny\n\nError-budget anti-patterny oddeľujú aritmetiku od user risku alebo policy consequence. Taký budget môže vyzerať presne, ale nevedie k bezpečnému change rozhodnutiu ani k uzavretiu recurrence mechanizmu.\n\n- **Budget ako povolenie míňať chyby —** Budget umožňuje bounded risk, nie vedomé poškodzovanie users alebo ignorovanie known defectu. Known high-impact mechanismus potrebuje remediation aj pri formálne zdravom budgete.\n- **Percento bez operation countu a času —** `40 % zostáva` nehovorí, či ide o štyri alebo štyri milióny events ani ako rýchlo sa budget míňa. Decision potrebuje remaining count, burn rate a zostávajúci window.\n- **Automatický freeze všetkého —** Globálny freeze blokuje aj changes, ktoré risk znižujú. Policy musí rozlišovať discretionary, emergency, security a remediation work.\n- **Calendar reset ako recovery —** Window reset mení číslo, nie production mechanismus. Normal mode sa obnoví až po SLI recovery a recurrence evidence.\n- **Priemer budgets —** Availability, correctness, durability a critical cohorts majú nekompenzovateľné verdicts. Composite average nesmie zelenou osou prekryť exhausted critical objective.\n""",
)

replace_exact(
    "docs/14-sre-and-operations/toil.md",
    """## 6. Elimination strategy order\n\nRiešenia majú poradie od odstránenia demandu po explicitné prijatie:\n\n1. **Eliminate root demand** — oprav failure mechanismus, aby trigger nevznikal.\n""",
    """## 6. Elimination strategy order\n\nRiešenie sa vyberá podľa toho, kde možno bezpečne prerušiť demand loop. Najvyššiu hodnotu má odstránenie upstream condition; automatizácia posledného kroku je vhodná až vtedy, keď demand zostáva legitímny a decision možno formalizovať bez skrytia uncertainty.\n\nPoradie zároveň vyjadruje trade-off medzi trvalým znížením práce a nákladom na redesign. Tím môže zvoliť partial automation alebo bounded acceptance, ale musí explicitne uviesť, prečo root-demand elimination zatiaľ nie je primerané a aký residual toil zostáva.\n\n1. **Eliminate root demand** — oprav failure mechanismus, aby trigger nevznikal.\n""",
)

replace_exact(
    "docs/14-sre-and-operations/toil.md",
    """## 12. Anti-patterny\n\n### Automatizuj každý manuálny krok\n\nManual work môže obsahovať risk judgment. Najprv oddel deterministic execution od ambiguous decisionu.\n\n### Toil equals celé on-call\n\nNovel diagnosis a incident command nie sú rovnaké ako opakovaný runbook.\n\n### Počítaj iba hodiny\n\nNízkoobjemový destructive workflow môže mať vyššiu prioritu než častá low-risk práca.\n\n### Presuň ticket inému tímu\n\nOrganizačný transfer nemení system demand ani customer wait.\n\n### Odstráň alert\n\nAk failure pokračuje, zníženie page countu nie je toil reduction.\n""",
    """## 12. Anti-patterny\n\nToil anti-patterny optimalizujú viditeľnosť alebo ownership práce bez odstránenia demandu a risku. Program preto hodnotí end-to-end occurrence, human touch, customer wait a reliability outcome, nie iba počet tickets jedného tímu.\n\n- **Automatizuj každý manuálny krok —** Manual work môže obsahovať risk judgment. Najprv oddel deterministic execution od ambiguous decisionu a zachovaj fenced human path pre uncertainty.\n- **Toil equals celé on-call —** Novel diagnosis a incident command nie sú rovnaké ako opakovaný runbook. Inventory musí klasifikovať konkrétne workflows, nie celú službu v rotačnom kalendári.\n- **Počítaj iba hodiny —** Nízkoobjemový destructive workflow môže mať vyššiu prioritu než častá low-risk práca. Prioritization kombinuje volume, privilege, blast radius a growth.\n- **Presuň ticket inému tímu —** Organizačný transfer nemení system demand ani customer wait. Úspech vyžaduje pokles end-to-end worku alebo jasný transfer authority a capability.\n- **Odstráň alert —** Ak failure pokračuje, zníženie page countu nie je toil reduction. Alert možno zmeniť až spolu s detection contractom a dôkazom, že user risk neklesol iba z observability.\n""",
)

print("SRE block 1 style remediation applied")
