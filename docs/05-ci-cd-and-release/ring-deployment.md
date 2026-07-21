# Ring deployment

Ring deployment rozdeľuje rollout do stabilných, vopred definovaných skupín používateľov, zariadení, tenantov alebo infraštruktúrnych jednotiek. Každý ďalší ring zvyšuje exposure a zvyčajne aj reprezentatívnosť a business kritickosť.

## 1. Základný model

```text
ring 0: development/internal
→ ring 1: trusted early adopters
→ ring 2: limited production segment
→ ring 3: broad production
→ ring 4: regulated alebo najkritickejší segment
```

Ring nie je iba percento trafficu. Je to stabilná rollout boundary s definovaným membershipom, risk profilom, observation window a promotion policy.

## 2. Canary vs. rings

Canary často pracuje s malým dynamickým traffic weightom. Ring deployment používa dlhodobejšie alebo organizačne významné cohorts.

Príklad:

- canary: 2 % náhodných requestov,
- ring: interní zamestnanci, pilotní zákazníci, konkrétny región alebo device channel.

Obe techniky možno kombinovať: v každom ringu vykonať vlastný canary rollout.

## 3. Návrh ringov

Ringy možno definovať podľa:

- interní vs. externí používatelia,
- customer tier,
- tenant kritickosť,
- región a data residency,
- device model alebo OS version,
- compliance režim,
- support preparedness,
- workload profile,
- dependency topology,
- rollback schopnosť.

Poradie má zvyšovať dôkaz a kontrolovane rozširovať blast radius.

## 4. Ring 0

Najskorší ring môže obsahovať:

- vývojový tím,
- test accounts,
- interné workflows,
- synthetic traffic,
- non-critical environments.

Ring 0 nemá byť jediný dôkaz. Interný workload, permissions a data distribution často nereprezentujú externú produkciu.

## 5. Early adopters

Dobrovoľní alebo zmluvne definovaní early adopters môžu poskytovať kvalitný feedback, ale potrebujú:

- jasné očakávania,
- support channel,
- opt-in/opt-out,
- privacy a compliance kontrolu,
- rýchly rollback/disable,
- komunikáciu známych rizík.

Nesmú byť používaní ako nevedomí testeri kritických zmien.

## 6. Stable membership

Membership musí byť:

- deterministický,
- auditovateľný,
- versionovaný,
- konzistentný naprieč services,
- odolný voči náhodnému reshuffle,
- dostupný pre observability.

Dynamické membership pravidlá môžu spôsobiť, že používateľ počas workflow prejde medzi verziami.

## 7. Promotion contract

Pre každý ring definuj:

- entry criteria,
- minimálnu duration,
- minimálnu sample size,
- technické a business metrics,
- required approvals,
- support readiness,
- abort criteria,
- rollback alebo roll-forward plan,
- maximum exposure.

Promotion nie je iba zmena percenta; je to rozhodnutie o prijatí väčšieho rizika na základe evidence.

## 8. Observation windows

Neskoršie ringy môžu potrebovať dlhšie observation window, pretože obsahujú:

- zriedkavé workflows,
- batch procesy,
- mesačné alebo denné cykly,
- väčšie dátové objemy,
- regulované operácie,
- vyššiu business kritickosť.

Fixné „10 minút na ring“ často ignoruje čas potrebný na prejavenie failure mode.

## 9. Regionálne ringy

Rollout podľa regiónov môže obmedziť blast radius, ale treba zohľadniť:

- regionálny workload a latency,
- data residency,
- failover topology,
- dependency endpoints,
- časové pásma,
- support coverage,
- global shared state.

Regionálny ring neizoluje zmenu, ak všetky regióny používajú rovnakú databázu alebo control plane.

## 10. Device a client rings

Pri desktop, mobile, agent alebo firmware produktoch sú ringy často distribuované channels:

```text
internal
→ beta
→ preview
→ stable
→ long-term support
```

Potrebné sú:

- update eligibility,
- download integrity,
- compatibility matrix,
- offline clients,
- staged availability,
- downgrade policy,
- telemetry s client version,
- support lifecycle.

Rollback klienta môže byť podstatne ťažší než rollback servera.

## 11. Tenant rings

V multi-tenant systéme možno rolloutovať po tenant cohorts. Over:

- izoláciu konfigurácie,
- shared database compatibility,
- noisy-neighbor effects,
- tenant-specific integrations,
- custom schemas,
- contractual obligations,
- cross-tenant workflows.

Jeden veľký tenant môže predstavovať väčší workload než tisíce malých, preto percento tenantov nie je percento trafficu.

## 12. Ring-specific configuration

Rozdielna config medzi ringmi môže byť potrebná, ale zvyšuje riziko driftu.

Každý ring musí mať evidované:

- artifact digest,
- config revision,
- feature flag state,
- policy version,
- membership definition,
- deployment timestamp.

Promotion evidence musí dokazovať, že neskorší ring používa ekvivalentnú konfiguráciu okrem zámerných rozdielov.

## 13. Version skew

Dlhé rollouty znamenajú dlhšie obdobie viacerých verzií. Potrebná je kompatibilita:

- API,
- events,
- database schema,
- cache a session formats,
- background workers,
- configuration,
- authentication claims.

Ring deployment nie je vhodný pre zmenu, ktorá vyžaduje okamžitý globálny cutover bez kompatibilnej fázy.

## 14. Observability

Telemetry musí umožniť filtrovať podľa:

- ring ID,
- release version/digest,
- tenant alebo region cohort,
- client channel,
- deployment wave,
- config revision.

Porovnávaj ring s vhodnou baseline. Ring 0 a final ring môžu mať úplne iný workload.

## 15. Support a communication

Každý ring potrebuje:

- ownera,
- support readiness,
- release notes podľa audience,
- known-issues channel,
- escalation path,
- rollback communication,
- status evidence.

Technicky úspešný rollout bez podpory môže stále poškodiť používateľov.

## 16. Emergency changes

Urgentná security alebo incident fix zmena môže ringy zrýchliť alebo preskočiť, ale musí zachovať:

- immutable artifact identity,
- minimálne safety checks,
- explicitný risk acceptance,
- observability,
- recovery plan,
- audit trail.

„Emergency“ nemá znamenať neidentifikovateľný manuálny deployment.

## 17. Troubleshooting

### Ring 1 je zdravý, ring 2 zlyháva

Porovnaj workload, integrations, permissions, scale, region topology, tenant customizations a config.

### Používatelia preskakujú medzi ringmi

Over membership key, caching, identity lifecycle a konzistentnosť assignmentu naprieč services.

### Rollback jedného ringu poškodí kompatibilitu

Novší ring už zmenil shared state. Použi compatibility bridge, feature disable alebo roll-forward.

### Telemetry nevie odlíšiť ringy

Doplň deployment/ring labels a release markers. Bez nich promotion zastav.

## 18. Anti-patterny

### Ringy sú iba názvy prostredí

Ring je production exposure cohort, nie synonymum dev/stage/prod.

### Každý ring má iný artifact build

Nie je zachovaná build-once-promote-many identita.

### Najkritickejší zákazník je prvý ring

Zvyšuje blast radius bez predchádzajúcej evidence.

### Membership sa mení bez auditu

Výsledky a incident scope sa nedajú rekonštruovať.

### Rollout ostane mesiace v polovici

Version skew, support complexity a technical debt rastú.

## 19. Kontrolné otázky

1. Čo odlišuje ring deployment od percentuálneho canary?
2. Ako navrhnúť poradie ringov podľa rizika?
3. Prečo musí byť membership stabilný?
4. Čo má obsahovať promotion contract?
5. Ako regionálne ringy súvisia so shared state?
6. Čím sa líšia client/device ringy od server rolloutov?
7. Prečo počet tenantov nereprezentuje traffic share?
8. Ako dlhý rollout ovplyvňuje compatibility?
9. Ako má telemetry označovať ringy?
10. Ako riešiť emergency release bez straty kontroly?

## Glossary impact

Relevantné pojmy: ring deployment, deployment ring, rollout wave, ring membership, early-adopter ring, release channel, staged rollout, ring promotion, version skew a ring-specific telemetry.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shadow deployment](shadow-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Feature flags →](feature-flags.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
