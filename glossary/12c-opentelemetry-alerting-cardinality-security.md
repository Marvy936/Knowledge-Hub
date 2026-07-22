# OpenTelemetry, alerting, cardinality and CIA glossary entries

## Actionable alert

Alert, ktorý má jasného ownera, definovaný impact, konkrétnu okamžitú akciu, runbook a spôsob overenia resolution. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Active series

Time series, ktorá má recent samples a spotrebúva active TSDB memory a metadata resources. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Active stream — Loki

Log stream, do ktorého sa aktuálne zapisujú log entries a ktorý drží ingester state a chunk resources. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Agent Collector

OpenTelemetry Collector nasadený blízko workloadu alebo Node-u na lokálny príjem, enrichment, batching, buffering a forwarding telemetry. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Alert as Code

Version-controlled model alerting rules, routing, templates, tests, ownership a runbook references nasadzovaný cez review a automatizovaný pipeline. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert condition

Query alebo expression spolu s thresholdom a time semantics, ktoré určujú, kedy alert prejde do active, pending alebo firing stavu. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert fatigue

Pokles pozornosti a dôvery spôsobený nadmerným počtom neakčných, duplicitných, flapping alebo nesprávne routovaných notifications. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert flapping

Opakované rýchle prepínanie alertu medzi firing a resolved stavom spôsobené nestabilným signalom, thresholdom, missing data alebo nedostatočným time windowom. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert identity

Stabilná identita alert instance odvodená z label setu a používaná na deduplication, grouping, silences a routing. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert precision

Podiel alerts, ktoré správne identifikujú relevantný a actionable stav oproti false positives a neakčným notifications. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert severity

Klasifikácia požadovanej reakcie a urgency, napríklad page, ticket alebo info, nie iba technická veľkosť nameranej hodnoty. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Assurance — security

Dôkazy a miera dôvery, že navrhnuté security controls sú správne implementované a účinné. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Asset — security

Dáta, systém, identita, služba, konfigurácia, artifact alebo business process, ktorého strata alebo kompromitovanie má hodnotiteľný dopad. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Authenticity

Vlastnosť umožňujúca dôverovať, že entity, dáta alebo artifacts pochádzajú z deklarovaného a overeného source-u. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Availability — security

Zabezpečenie včasného a spoľahlivého prístupu k informáciám a službám pre autorizovaných používateľov a procesy. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Bounded dimension

Telemetry dimension s malým, riadeným a relatívne stabilným počtom možných hodnôt. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Burn-rate alert

SLO alert sledujúci rýchlosť spotrebúvania error budgetu oproti tempu, ktoré by vyčerpalo budget v definovanom období. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Cardinality

Počet unikátnych hodnôt alebo kombinácií dimensions, ktoré vytvárajú time series, log streams, indexed terms alebo ďalšie telemetry identities. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality budget

Explicitný limit a očakávaný growth model pre series, streams, indexed values alebo attributes per service, metric, tenant alebo backend. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality incident

Prevádzkový incident, pri ktorom nekontrolovaný rast telemetry identities alebo indexed values ohrozuje ingestion, memory, storage, query výkon alebo cost. Pozri [Cardinality](docs/12-observability/cardinality.md).

## CIA triáda

Základný model bezpečnostných cieľov Confidentiality, Integrity a Availability. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Collector distribution

Konkrétny build OpenTelemetry Collectora s definovanou množinou receivers, processors, exporters a extensions, napríklad core, contrib, vendor alebo custom distribution. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Combinatorial cardinality

Rast počtu telemetry identities spôsobený kombináciou viacerých dimensions, ktorých hodnoty sa navzájom násobia. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Compensating control

Alternatívny security control použitý na dosiahnutie porovnateľného zníženia risku, keď primárny control nie je možný alebo primeraný. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Confidentiality

Zachovanie autorizovaných obmedzení prístupu a disclosure informácií. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Corrective control

Control, ktorý po zistení incidentu opravuje alebo obmedzuje jeho následky. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Data at rest

Dáta uložené v database, filesysteme, object storage, backupe, snapshot-e alebo inom persistentnom médiu. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Data in transit

Dáta prenášané medzi clientmi, službami, storage systémami alebo telemetry komponentmi. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Data in use

Dáta počas spracovania v process memory, CPU/GPU, temporary files alebo dešifrovanom application contexte. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Detective control

Control určený na odhalenie incidentu, policy violation alebo nežiaducej zmeny. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Fast burn

Prudké spotrebúvanie error budgetu signalizujúce významný krátkodobý user impact a potrebu rýchlej reakcie. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Firing alert

Alert instance, ktorej condition zostala aktívna podľa požadovaných time semantics a je pripravená na notification routing. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Gateway Collector

Shared OpenTelemetry Collector tier používaný na centralized sampling, routing, redaction, policy, fan-out a backend export. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Global ordinals

Lucene/Elasticsearch/OpenSearch dátová štruktúra urýchľujúca aggregations nad keyword values, ktorej memory a build cost rastie pri high-cardinality fields. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Impact — security

Následok straty confidentiality, integrity alebo availability pre používateľov, organizáciu, assets alebo mission. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Integrity — security

Ochrana accuracy, completeness a správnosti dát, konfigurácie a processingu pred neautorizovanou alebo nesprávnou zmenou. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Mapping explosion

Nekontrolovaný rast počtu indexed field definitions spôsobený dynamic schemas alebo arbitrary object keys. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Memory limiter — OpenTelemetry

Collector processor chrániaci process pred uncontrolled memory growth a aktivujúci pressure behavior podľa nastavenej memory policy. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Metamonitoring — alerting

Monitoring celého monitoring a notification reťazca vrátane source signalov, rule evaluation, Alertmanagera a externého receivera. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Mute interval

Opakovateľné časové pravidlo, počas ktorého sa pre matching route neposielajú notifications, napríklad plánovaná pravidelná maintenance. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## No-data policy

Explicitné pravidlo určujúce, ako alerting engine interpretuje neprítomnosť očakávaných dát. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Non-repudiation

Schopnosť poskytnúť dôkaz o pôvode alebo vykonaní operácie tak, aby ju zodpovedná entita nemohla vierohodne poprieť. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## OpenTelemetry

Vendor-neutral observability framework a specification pre instrumentation, generation, collection a export traces, metrics a logs. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## OTel API

Programovací contract používaný application a instrumentation libraries bez vynútenia konkrétneho backendu alebo runtime konfigurácie. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## OTel SDK

Runtime implementácia OpenTelemetry API zabezpečujúca sampling, aggregation, processing, resource configuration a export. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Pending alert

Alert instance, ktorej condition je aktívna, ale ešte nesplnila požadované `for` alebo ekvivalentné time semantics. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Persistent queue — telemetry

Queue uchovávajúca telemetry state na persistentnom médiu, aby prežila process restart podľa contractu konkrétneho komponentu. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Preventive control

Control znižujúci pravdepodobnosť vzniku bezpečnostného incidentu. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Promoted trace attribute

Span attribute vybraný na indexovanie, metrics generation alebo ďalšie zrýchlené query spracovanie, čím získava samostatný cardinality a cost dopad. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Recovery control

Control umožňujúci obnoviť službu, dáta alebo dôveryhodný stav po incidente. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Resolved alert

Alert instance, ktorej firing condition už neplatí a prešla do ukončeného stavu podľa alerting lifecycle-u. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Resource — OpenTelemetry

Súbor attributes identifikujúcich entitu produkujúcu telemetry, napríklad service, host, cloud resource alebo Kubernetes workload. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Resource Detector

Komponent automaticky získavajúci OpenTelemetry resource attributes z environmentu, cloudu, Kubernetes alebo runtime metadata. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Schema URL — OpenTelemetry

Reference na semantic-convention schema používanú resource alebo instrumentation scope-om na podporu compatibility a migration. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Security categorization

Určenie impact levelu straty confidentiality, integrity a availability pre konkrétny system alebo information type. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Security control

Management, operational, technical alebo physical safeguard navrhnutý na ochranu assets a zníženie security risku. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Security risk

Riziko vznikajúce z možnej straty confidentiality, integrity alebo availability s ohľadom na pravdepodobnosť a dopad. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Semantic Conventions — OpenTelemetry

Štandardizované názvy a významy telemetry operations, resources, attributes, metrics a events. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Sending queue — OpenTelemetry

Exporter queue absorbujúca krátkodobý downstream výpadok alebo throttling pred retry alebo drop behaviorom. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Series churn

Rýchle vytváranie a zánik time series, ktoré zaťažuje WAL, index, compaction a remote storage aj pri nižšom počte súčasne active series. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Silence — alerting

Dočasné potlačenie notifications pre alerts matchujúce definovaný label set, s ownerom, dôvodom a expiration. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Slow burn

Dlhšie mierne prekračovanie reliability targetu, ktoré spotrebúva error budget pomalšie, ale systematicky. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Stream churn

Rýchle vytváranie a zánik log streams, často spôsobené ephemeral alebo dynamic label hodnotami. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Symptom alert

Alert založený na user alebo business impacte namiesto jednej možnej technickej príčiny. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Synthetic alert

Kontrolovaný testovací alert používaný na overenie rule evaluation, routing, receiver delivery a acknowledgement path. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Tail sampling — OpenTelemetry

Sampling decision vykonané po zhromaždení väčšej časti trace-u, typicky v stateful Collector pipeline. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Telemetry contract test

Automatizovaný test overujúci names, units, attributes, resources, correlation, cardinality a compatibility telemetry po zmene instrumentation alebo pipeline. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Telemetry fan-out

Odosielanie rovnakého prijatého signalu do viacerých processing pipelines alebo backendov s odlišnými retention, security alebo analytics účelmi. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Telemetry tragedy of the commons

Stav shared observability platformy, v ktorom jednotliví producenti pridávajú drahú telemetry bez vlastného cost feedbacku a spoločne vyčerpajú kapacitu alebo budget. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Threat

Potenciálna príčina neželaného bezpečnostného incidentu, napríklad attacker, insider, human error alebo infrastructure failure. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Trace affinity

Routing vlastnosť zabezpečujúca, že spans rovnakého trace-u dorazia na rovnakú stateful processing identity, napríklad tail sampler. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Unbounded dimension

Telemetry dimension s nekontrolovaným alebo prakticky neobmedzeným počtom hodnôt, napríklad request ID, trace ID alebo user ID. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Vulnerability

Slabina v systéme, konfigurácii, procese alebo control-e, ktorú môže threat využiť. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## W3C Trace Context

Štandardný propagation format používajúci najmä `traceparent` a `tracestate` na prenos distributed trace contextu. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).
