# Rollback a roll-forward

Rollback obnovuje predchádzajúci application artifact alebo configuration state. Roll-forward nasadí novú opravnú zmenu, ktorá odstráni problém bez návratu na starú verziu. Správna voľba závisí najmä od kompatibility shared state, rýchlosti prípravy opravy a schopnosti presne identifikovať posledný známy dobrý stav.

## 1. Recovery nie je iba redeployment

Deployment failure môže ovplyvniť:

- application binaries,
- configuration,
- databázovú schema a dáta,
- cache a sessions,
- queues a events,
- external side effects,
- IAM a network policy,
- client compatibility.

Vrátenie starého artifactu rieši iba časť systému.

## 2. Typy rollbacku

### Artifact rollback

Nasadenie predchádzajúceho immutable artifact digestu.

### Configuration rollback

Obnovenie predchádzajúcej versionovanej konfigurácie alebo flag state.

### Traffic rollback

Presmerovanie trafficu na stable/canary/blue target bez zmeny artifactov.

### Infrastructure rollback

Návrat desired state infraštruktúry na predchádzajúcu deklaráciu.

### Data rollback

Obnovenie dát alebo schema stavu. Je najrizikovejší a často vyžaduje restore, point-in-time recovery alebo compensating operations.

Tieto operácie sa nesmú zamieňať.

## 3. Roll-forward

Roll-forward je vhodný, keď:

- stará verzia už nerozumie novému state,
- databázová zmena je nevratná,
- side effects už nemožno odvolať,
- oprava je malá a rýchlo validovateľná,
- rollback by znovu otvoril security problém,
- clients alebo downstream systems už používajú nový kontrakt.

Roll-forward stále potrebuje immutable artifact, test evidence a kontrolovaný rollout.

## 4. Decision matrix

| Otázka | Skôr rollback | Skôr roll-forward |
|---|---|---|
| Starý artifact je kompatibilný s aktuálnymi dátami? | Áno | Nie |
| Predchádzajúci digest je dostupný a overený? | Áno | Nie |
| Oprava je pripravená veľmi rýchlo? | Nie | Áno |
| Nová verzia vytvorila externé side effects? | Nie | Áno/kompenzácia |
| Ide o aktívnu security zraniteľnosť starej verzie? | Nie | Áno |
| Rollback mechanizmus je pravidelne testovaný? | Áno | Nie |

Rozhodnutie nemá byť založené iba na preferencii tímu.

## 5. Last known good

Predchádzajúca verzia nie je automaticky „known good“. Potrebuje evidenciu:

- artifact digest,
- config revision,
- environment state,
- deployment timestamp,
- health/SLO výsledky,
- kompatibilitu s aktuálnou schema,
- známe security a functional chyby.

Rollback na neidentifikovaný tag `previous` alebo `latest-1` je nebezpečný.

## 6. Recovery package

Pre release uchovaj:

```text
current digest
previous compatible digest
config revisions
schema compatibility range
feature flag defaults
rollback command/workflow
roll-forward owner
known irreversible changes
```

Recovery package má byť vytvorený pred produkčným rolloutom, nie počas incidentu.

## 7. Configuration a feature flags

Najrýchlejší recovery môže byť:

- vypnutie capability,
- zníženie traffic weightu,
- obnovenie configu,
- deaktivácia background workeru,
- zmena rate limitu,
- prechod na fallback dependency.

Flag/config rollback je bezpečný iba vtedy, keď kód a data state podporujú oba stavy.

## 8. Database constraints

Rollback artifactu je bezpečný len ak stará verzia:

- rozumie aktuálnej schema,
- toleruje nové columns/values,
- nevyžaduje odstránené polia,
- dokáže čítať nové serialization formáty,
- nepoškodí dáta novým writer behaviorom.

Destruktívna migration pred koncom rollback window prakticky ruší artifact rollback.

## 9. Data recovery

Možnosti:

- backward migration,
- forward-fix migration,
- point-in-time restore,
- restore do nového targetu a cutover,
- compensating transaction,
- selective data repair,
- event replay.

Každá možnosť má RPO, RTO, consistency a audit trade-offy. Backward migration nie je automaticky bezpečná ani úplná.

## 10. External side effects

Rollback neodvolá:

- odoslané emaily,
- payment capture,
- partner API mutations,
- vydané certificates/tokens,
- publikované events,
- zákaznícke rozhodnutia.

Potrebné môžu byť compensating actions a business incident proces.

## 11. Queues a event streams

Pri rollbacku consumerov over:

- event schema compatibility,
- backlog vytvorený novou verziou,
- poison messages,
- changed partitioning,
- idempotency,
- duplicate processing,
- replay policy,
- producer/consumer version skew.

Starý consumer môže zlyhať na events, ktoré už nová verzia publikovala.

## 12. Client-server compatibility

Server rollback môže poškodiť novšie clients, ktoré už očakávajú nový endpoint alebo response field. Používaj:

- backward-compatible API,
- capability negotiation,
- version support window,
- feature disable,
- tolerant clients,
- staged client release.

Pri mobile/desktop produktoch nemožno predpokladať okamžitý client rollback.

## 13. Rolling rollback

Pri rolling update možno staré instances vracať postupne. Počas procesu existuje zmiešaná fleet opačným smerom.

Over:

- readiness,
- state compatibility,
- session behavior,
- capacity,
- connection draining,
- version-level telemetry,
- rollback batch size.

Ak je nová verzia kriticky chybná, príliš pomalý rolling rollback predlžuje exposure.

## 14. Blue-green rollback

Routing späť na blue môže byť rýchly, ak:

- blue zostal warm a healthy,
- shared state je kompatibilný,
- connections možno drainovať,
- schedulers/workers sú koordinované,
- routing propagation je známa.

Routing rollback nie je data rollback.

## 15. Automatic rollback

Automatický rollback vyžaduje:

- nízko-noise signal,
- version-specific telemetry,
- explicitný threshold a duration,
- known compatible target,
- cooldown a oscillation protection,
- audit trail,
- human escalation pri nejednoznačnosti.

Noisy alert alebo všeobecný dependency incident môže spustiť škodlivý rollback.

## 16. Rollback window

Rollback window je obdobie, počas ktorého sa zachováva:

- kompatibilná schema,
- predchádzajúci artifact,
- config compatibility,
- warm alebo dostupný target,
- potrebná operational evidence,
- support schopnosť.

Po jeho skončení musí byť explicitné, že recovery stratégiou je roll-forward alebo restore.

## 17. Testing recovery

Testuj:

- artifact rollback,
- config/flag rollback,
- traffic switch,
- migration compatibility,
- restore procedure,
- event replay,
- credentials a permissions,
- rollback pod loadom,
- rollback po partial rollout-e.

Runbook bez pravidelného vykonania nie je dôkaz recovery capability.

## 18. Recovery observability

Počas recovery sleduj:

- exposure podľa verzie,
- error a latency trend,
- backlog,
- data repair progress,
- side-effect count,
- stale instances,
- config propagation,
- customer impact,
- recovery time.

Recovery nie je dokončený iba preto, že deployment job skončil zeleno.

## 19. Troubleshooting

### Rollback job uspel, incident pokračuje

Over stale instances, cache/config, side effects, database state, clients a dependency incident.

### Starý artifact sa nespustí

Chýba schema compatibility, secret/config key alebo runtime dependency. Prejdi na roll-forward alebo restore plan.

### Automatika opakovane prepína verzie

Zaveď cooldown, hysteresis, stable observation a odstráň noisy signal.

### Roll-forward oprava pridala ďalšiu chybu

Zníž exposure, aktivuj fallback a vráť sa k risk-based pipeline; incident urgency neruší minimálne safety checks.

## 20. Anti-patterny

### „Vždy rollbackujeme“

Ignoruje nekompatibilný state a external side effects.

### „Vždy roll-forwardujeme“

Predlžuje incident, keď je bezpečný known-good rollback okamžite dostupný.

### Mutable rollback tag

Nie je zaručené, ktoré bytes sa nasadia.

### Destruktívna migration pred observation window

Odstráni recovery možnosť príliš skoro.

### Recovery sa netestuje, aby sa neriskovala produkcia

Prvý skutočný test potom prebehne počas incidentu.

## 21. Rozhodovací rámec

1. Aký presný stav je chybný: artifact, config, data alebo dependency?
2. Je posledný known-good digest kompatibilný s aktuálnym state?
3. Aké side effects už vznikli?
4. Aký je najrýchlejší bezpečný containment?
5. Je oprava pripravená rýchlejšie než rollback?
6. Aké recovery kroky sú reverzibilné?
7. Potrebujeme compensating action alebo restore?
8. Ako zamedzíme oscillation?
9. Kedy je recovery dokončený podľa user-facing signálu?
10. Čo z incidentu zmení budúci deployment design?

## 22. Kontrolné otázky

1. Aký je rozdiel medzi rollbackom a roll-forwardom?
2. Aké typy rollbacku poznáš?
3. Prečo predchádzajúca verzia nemusí byť known good?
4. Čo obsahuje recovery package?
5. Prečo artifact rollback nie je data rollback?
6. Ako event streams komplikujú rollback?
7. Kedy je automatic rollback nebezpečný?
8. Čo je rollback window?
9. Ako testovať recovery capability?
10. Ktoré signály dokazujú, že recovery je dokončený?

## Glossary impact

Relevantné pojmy: rollback, roll-forward, artifact rollback, configuration rollback, traffic rollback, data rollback, last known good, recovery package, compensating action, rollback window, automatic rollback, recovery oscillation a forward-fix migration.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Progressive delivery](progressive-delivery.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Databázová kompatibilita počas deploymentu →](database-compatibility-during-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
