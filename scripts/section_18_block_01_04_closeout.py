from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "18-machine-learning-fundamentals"


def patch(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise RuntimeError(f"Missing closeout anchor: {label}")
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


patch(
    SECTION / "artificial-intelligence-machine-learning-deep-learning-generative-ai.md",
    """AI system teda nie je automaticky neurónová sieť a už vôbec nie iba model file. Payment review application môže kombinovať:

- deterministic eligibility rules, ktoré odmietnu nekompletný request;
- supervised classifier, ktorý odhadne probability budúcej straty;
- ranking policy, ktorá zoradí prípady podľa expected value kontroly;
- generatívny model, ktorý pripraví analyst summary;
- human reviewer, ktorý má autoritu rozhodnúť o ďalšom kroku;
- audit a reconciliation, ktoré preukážu skutočný business outcome.

Dôsledok je dôležitý: model evaluation preukazuje vlastnosť modelu na definovanom datasete. Nepreukazuje automaticky správnosť identity, authorization, queue semantics, human processu ani finálnej business operácie. AI-system acceptance musí pokryť celý path.
""",
    """AI system teda nie je automaticky neurónová sieť a už vôbec nie iba model file. Payment review application skladá viac komponentov, z ktorých každý vlastní inú transition a inú dôkaznú hranicu. Rules rozhodujú hard eligibility, learned model vytvára štatistický odhad, ranking policy prevádza scores na kapacitné poradie, generátor pripravuje text a človek alebo enforcement layer vlastní citlivý side effect.

- deterministic eligibility rules — odmietajú nekompletný alebo policy-forbidden request ešte pred modelom, takže learned component nikdy nedostane authority obísť hard constraints;
- supervised classifier — odhaduje probability budúcej straty pre exact operation a model generation, ale sám neurčuje review action;
- ranking policy — kombinuje score, recoverable amount, capacity a tie-breaking do auditovateľného poradia kandidátov;
- generatívny model — pripravuje analyst summary ako pomocný content, ktorého factuality a faithful relationship k source evidence sa validujú osobitne;
- human reviewer — vlastní finálne posúdenie prípadu v rámci explicitných permissions a zaznamenáva reason/outcome;
- audit a reconciliation — spájajú input, component generations, action a neskorší business outcome, aby sa dal zmerať aj opraviť celý path.

Komponenty preto netvoria zoznam rovnocenných „AI features“. Tvoria ordered authority chain: hard policy obmedzuje možné actions, model poskytne evidence, ranking vyberie bounded workload, človek rozhodne a reconciliation overí následok. Model evaluation preukazuje vlastnosť modelu na definovanom datasete; nepreukazuje automaticky správnosť identity, authorization, queue semantics, human processu ani finálnej business operácie. AI-system acceptance musí pokryť celý path.
""",
    "AI component inventory",
)

patch(
    SECTION / "supervised-unsupervised-reinforcement-learning.md",
    """Základné subjects:

- environment — systém alebo svet, ktorý reaguje na actions;
- state — informácia potrebná pre predikciu future rewards pri danom decision model;
- observation — to, čo agent skutočne vidí; nemusí byť complete state;
- action — voľba, ktorú agent môže vykonať;
- reward — scalar feedback pre jeden transition;
- return — kumulovaný budúci reward;
- policy — mapping zo state/observation na action distribution;
- episode — bounded sequence interakcií, ak má problem prirodzený začiatok a koniec.

RL nie je „supervised learning, ktorý sa často retrainuje“. Label pre correct action nemusí byť priamo dostupný; agent hodnotí consequences actions cez reward a transition dynamics.
""",
    """RL subject nemožno zredukovať na samotný model file. Environment vlastní transition dynamics, policy vlastní výber action a reward function určuje, ktorý observed consequence sa optimalizuje. State je analytický predpoklad decision problemu, zatiaľ čo observation je konkrétna informácia dostupná agentovi; ich zámena môže vytvoriť policy, ktorá pri trainingu videla informáciu nedostupnú v produkcii.

Základné subjects tvoria jeden transition contract:

- environment — systém alebo svet, ktorý prijme action a vytvorí next state aj observed consequences;
- state — informácia, ktorá je v zvolenom modelovaní potrebná pre predikciu future rewards;
- observation — to, čo agent skutočne dostane na vstupe; pri partial observability nemusí určovať complete state;
- action — explicitne povolená voľba, ktorú policy môže navrhnúť alebo vykonať v danom state;
- reward — scalar feedback priradený transitionu, ktorý reprezentuje iba zakódovanú časť objective-u;
- return — kumulovaný budúci reward, podľa ktorého sa porovnávajú krátkodobé a dlhodobé consequences;
- policy — versionovaný mapping zo state-u alebo observation na action alebo action distribution;
- episode — bounded trajectory od definovaného začiatku po termination, ak má problem takú prirodzenú hranicu.

Tieto položky musia byť versionované spolu, pretože zmena action setu, rewardu alebo observation schema mení meaning policy aj pri rovnakých weights. RL nie je „supervised learning, ktorý sa často retrainuje“. Label pre correct action nemusí byť priamo dostupný; agent hodnotí consequences actions cez reward a transition dynamics, pričom authorization a safety constraints zostávajú mimo reward optimization.
""",
    "RL subject inventory",
)

patch(
    SECTION / "regression-classification-ranking-clustering.md",
    """Wrong-task formulation môže vyzerať ako algorithm failure, hoci model optimalizuje presne zadaný objective.

- classification namiesto ranking — high overall accuracy, ale zlé top-K poradie;
- regression bez action horizon — numerický odhad nemá usable decision boundary;
- clustering interpretovaný ako classes — arbitrary groups sa vydávajú za truth;
- ranking bez candidate evaluation — relevantné items chýbajú ešte pred scorerom;
- probability zamieňaná so utility — high risk s nízkym amountom preplní capacity;
- hard class threshold pri variable capacity — queue size a analyst load sa nekontrolovane menia.

Root cause sa neopraví automatickým hyperparameter tuningom. Najprv sa musí zmeniť task contract a evaluation.
""",
    """Wrong-task formulation môže vyzerať ako algorithm failure, hoci model optimalizuje presne zadaný objective. Diagnostic otázka preto nie je iba „ktorý estimator má lepšie score“, ale „má output rovnakú unit, comparison boundary a action semantics, akú potrebuje business operation?“. Každý z nasledujúcich omylov oddeľuje training objective od downstream decisionu iným spôsobom.

- classification namiesto ranking — model môže mať high overall accuracy, ale nevytvorí správne relatívne top-K poradie pre bounded capacity;
- regression bez action horizon — numerický odhad nemá jasnú dobu platnosti ani usable decision boundary;
- clustering interpretovaný ako classes — arbitrary groups podľa feature metric sa vydávajú za authoritative business truth;
- ranking bez candidate evaluation — relevantné items chýbajú ešte pred scorerom, takže dobrá list metric hodnotí iba neúplnú population;
- probability zamieňaná so utility — high risk s nízkym recoverable amountom môže vytlačiť hodnotnejší prípad a preplniť capacity;
- hard class threshold pri variable capacity — queue size a analyst load sa menia s prevalence a score distribution bez explicitného capacity ownera.

Spoločným mechanizmom je neviditeľný post-model transition: score sa mení na inú business quantity bez versionovanej policy a task-specific evaluation. Root cause sa preto neopraví automatickým hyperparameter tuningom. Najprv sa musí zmeniť task contract, baseline a acceptance tak, aby merali rovnaký decision, aký sa skutočne vykonáva.
""",
    "wrong-task failure modes",
)

patch(
    SECTION / "regression-classification-ranking-clustering.md",
    """Recovery porovnala štyri alternatives nad rovnakým operation/time holdoutom:

1. classification probability sort;
2. predicted expected loss regression;
3. transparent composed utility score;
4. learned ranking model.

Každý variant dostal rovnaký candidate set a capacity `K`. Evaluation oddelila model metric od business metric a serving cost. Learned ranker nebol promoted iba preto, že mal najlepší offline NDCG; musel prejsť shadow queue, latency, stability a cohort checks.
""",
    """Recovery porovnala štyri alternatives nad rovnakým operation/time holdoutom. Porovnanie nebolo zoznamom model names, ale controlled experimentom s rovnakým candidate manifestom, capacity `K`, label maturity a cost assumptions. Tým sa zabránilo tomu, aby jeden variant získal výhodu lepším data coverage alebo iným evaluation windowom.

1. Classification probability sort použil calibrated probability ako jednoduchý ranking baseline a ukázal hodnotu samotného classifieru bez ďalšej amount policy.
2. Predicted expected-loss regression zoradila operations podľa numeric recoverable-loss targetu a odhalila sensitivity na heavy-tail errors.
3. Transparent composed utility score skombinoval probability, recoverable amount a review cost cez explicitnú versionovanú formulu, ktorú vedel risk owner auditovať.
4. Learned ranking model optimalizoval relatívne list order a musel preukázať incremental gain oproti transparentným baselines.

Každý variant dostal rovnaký candidate set a capacity `K`. Evaluation oddelila model metric od business metric, serving latency, operational complexity a recovery cost. Learned ranker nebol promoted iba preto, že mal najlepší offline NDCG; musel prejsť shadow queue, stability a cohort checks a mať schválený fallback na jednoduchšiu ordering policy.
""",
    "recovery alternatives",
)

print("Applied focused prose closeout for Section 18 block 01-04.")
