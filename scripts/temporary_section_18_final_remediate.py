from pathlib import Path

ROOT = Path("docs/18-machine-learning-fundamentals")


def replace_once(filename: str, old: str, new: str) -> None:
    path = ROOT / filename
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{filename}: expected one replacement target, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


replace_once(
    "ml-troubleshooting-mental-model.md",
    """## 3. Symptom taxonomy

Symptom sa najprv zaradí podľa vrstvy, kde bol pozorovaný:

- data/label — missing records, schema drift, delayed labels, changed prevalence;""",
    """## 3. Symptom taxonomy

Symptom taxonomy neurčuje root cause; vytvára prvú mapu systému a určuje, ktoré authority treba čítať ako nasledujúce. Rovnaký business symptom sa môže prvýkrát prejaviť v inom technickom signále podľa toho, aké observability systém poskytuje. Napríklad pokles recovered loss môže byť outcome symptom, zatiaľ čo jeho prvý dostupný leading signal je zvýšený feature fallback alebo nižšia queue completion.

Zaradenie sa robí podľa miesta pozorovania, nie podľa predpokladanej príčiny. Každá kategória má iný authoritative read a typický denominator. Data/label vrstva používa manifests a maturity; feature vrstva request-correlated values; serving vrstva actual execution a fallback; policy vrstva decision trace; outcome vrstva mature adjudication. Až po tomto rozlíšení sa vytvára hypothesis tree:

- data/label — missing records, schema drift, delayed labels, changed prevalence;""",
)

replace_once(
    "ml-troubleshooting-mental-model.md",
    """## 6. Evidence preservation

Prvá mutation často zničí dôkaz. Pred rollbackom alebo retrainingom sa zachová:

- affected a healthy request IDs;""",
    """## 6. Evidence preservation

Prvá mutation často zničí dôkaz, preto preservation predchádza rollbacku, retrainingu aj config editácii, pokiaľ safety containment nevyžaduje okamžitý zásah. Cieľom nie je skopírovať všetko, ale zachovať minimálnu korelovateľnú stopu, z ktorej sa dá zrekonštruovať composite generation a first divergence.

Preservation musí pokryť affected aj healthy comparator, aby sa dalo rozlíšiť broad platform zlyhanie od cohort-specific failure. Každý artifact potrebuje event time, request/entity identity, source a retention/access policy. Aggregate dashboard screenshot bez raw IDs nepostačuje. Zachová sa najmä:

- affected a healthy request IDs;""",
)

replace_once(
    "ml-troubleshooting-mental-model.md",
    """## 22. Recovery layers

Recovery sa uzatvára v troch vrstvách:

1. component recovery — chybná vrstva vracia expected evidence;
2. journey recovery — end-to-end request prejde feature, prediction, policy a action;
3. business recovery — mature outcome a harm guardrails sa vrátia do accepted range.

Component green bez journey/business proof je partial recovery. Business recovery môže byť delayed; interim containment ostáva aktívny.""",
    """## 22. Recovery layers

Recovery sa uzatvára postupne, pretože úspech jednej vrstvy nepreukazuje downstream outcome. Component recovery dokazuje, že opravená vrstva vracia expected authoritative evidence: feature store poskytuje správne point-in-time values, serving načíta approved digest alebo queue používa intended policy generation. Tento test je najrýchlejší, ale zostáva lokálny.

Journey recovery prejde representative end-to-end request cez eligibility, feature retrieval, preprocessing, prediction, policy a action. Odhaľuje compatibility chyby, stale cache a fallbacks, ktoré component smoke test nevidí. Business recovery používa mature outcome a harm guardrails, takže môže za technickou obnovou časovo zaostávať.

Component green bez journey a business proof je partial recovery. Kým business evidence nedozrie, interim containment a zvýšené monitorovanie ostávajú aktívne. Closure record preto uvádza, ktorá z troch vrstiev je potvrdená a ktorá ešte čaká na evidence.""",
)

replace_once(
    "ml-troubleshooting-mental-model.md",
    """## 27. Competing failure hypotheses

Pre každý ML incident sa udržiava minimum competing hypotheses across layers:

- observation failure — dashboard, query, window alebo denominator je chybný;""",
    """## 27. Competing failure hypotheses

Pre každý ML incident sa udržiava minimum competing hypotheses across layers, aby prvý plausibilný príbeh neviedol priamo k mutation. Hypotheses sa zoradia podľa first-divergence evidence, pravdepodobnosti, impactu a ceny diskriminačného testu. Každá obsahuje supporting signal, falsifier a authoritative read.

Observation failure sa testuje reprodukciou dashboard query z immutable predictions a labels. Data/label hypotheses sa testujú membershipom, maturity a authority. Feature/serving hypotheses používajú matched request parity a actual execution trace. Model behavior sa posudzuje až po potvrdení inputs a artifact identity. Policy/action/outcome hypotheses používajú decision, completion a mature response evidence. V tomto rámci sa rozlišujú:

- observation failure — dashboard, query, window alebo denominator je chybný;""",
)

replace_once(
    "offline-evaluation-production-outcome.md",
    """## 23. Competing failure hypotheses

Offline-online gap sa diagnostikuje podľa najskoršej vrstvy, kde sa evidence odchýli. Najprv sa overí population a feature coverage, potom prediction parity, policy/action execution a nakoniec labels/outcome attribution.

- population mismatch — production eligibility alebo cohort mix sa líši od offline testu;""",
    """## 23. Competing failure hypotheses

Offline-online gap sa diagnostikuje podľa najskoršej vrstvy, kde sa evidence odchýli. Najprv sa overí population a feature coverage, potom prediction parity, policy/action execution a nakoniec labels/outcome attribution. Tento order bráni tomu, aby sa downstream business symptom automaticky pripísal model weights.

Každá hypothesis musí predpovedať odlišný matched-request alebo denominator pattern. Population mismatch zmení eligibility/cohort counts ešte pred feature retrieval. Skew vytvorí rozdiel v values alebo preprocessing pri rovnakých IDs. Artifact mismatch zachová features, ale zmení prediction. Policy/capacity failure zachová prediction a zmení action. Label alebo counterfactual failure sa prejaví až v outcome layeri pri rovnakých upstream traces. Rozlišujú sa najmä tieto mechanisms:

- population mismatch — production eligibility alebo cohort mix sa líši od offline testu;""",
)
