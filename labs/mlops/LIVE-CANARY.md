# Live canary evidence and rollback decision

Táto vrstva spája authoritative routing state s dvoma samostatnými HTTP serving generáciami. Harness nevykonáva DNS, service-mesh ani load-balancer konfiguráciu. Vykonáva však skutočné loopback HTTP requesty, číta späť response identity a vytvára bounded canary evidence.

```text
routing state
+ stable/canary deployment manifests
+ exact loopback endpoints
+ versioned request corpus
→ deterministic request assignment
→ live HTTP predictions
→ response identity verification
→ canary evidence window
→ continue / no-data / insufficient / rollback decision
→ exact rollback routing state
```

## Endpoint boundary

Harness povoľuje iba:

- `http://127.0.0.1:<port>`,
- `http://localhost:<port>`.

Nevykonáva remote production traffic. Endpoint map musí obsahovať presne deployment IDs referencované routing state-om. Request sa najprv priradí deterministic routing contractom a až potom odošle na endpoint príslušného deployment subjectu.

## Response identity

HTTP 200 sa nepovažuje automaticky za úspech. Response musí obsahovať hodnoty z presného routed deployment manifestu:

- `deployment_id`,
- generation,
- `release_id`,
- model SHA-256,
- image digest.

Ak endpoint odpovie ako iná generation alebo iný deployment, observation je failure `identity_mismatch`. To zachytí napríklad nesprávny port mapping, stale Service selector alebo router smerujúci canary subject na stable workload.

Request payload sa do evidence neukladá. Ukladá sa iba canonical request SHA-256 a routing-key SHA-256.

## Evidence window

Evidence obsahuje:

- exact `routing_state_id`,
- total/stable/canary request counts,
- successful a failed counts,
- stable a canary failures oddelene,
- identity mismatches,
- explicitný `no_data` state,
- min/average/p95/max latency,
- per-request bounded observation,
- canonical `canary_window_id`.

Latencia je observed runtime data. Nie je deterministická a rovnaký request corpus môže vytvoriť iný evidence ID pri inom rune.

## Decision states

Decision nie je iba boolean:

| Action | Význam |
|---|---|
| `no_data` | Window nemá žiadne requesty. Nesmie sa interpretovať ako healthy. |
| `insufficient_evidence` | Canary nedosiahla minimálny počet requestov. |
| `rollback` | Identity mismatch alebo canary error rate prekročili threshold. |
| `continue` | Aktuálne evidence gates prešli; nejde automaticky o plnú promotion. |

Decision pinne `canary_window_id`, `routing_state_id`, thresholdy a observed canary error rate. Evidence z iného routing state-u sa odmietne.

## Rollback

Rollback helper prijme iba decision s action `rollback`. Decision a current routing state musia mať rovnaký `routing_state_id`. Výsledkom je nový canonical state:

- exact predchádzajúci stable deployment ostáva stable,
- canary subject sa odstráni,
- canary traffic je 0,
- previous routing-state ID odkazuje na failed canary state.

Tento state ešte musí aplikovať skutočný router alebo platforma. Vytvorenie JSON rollback state-u samo osebe nepreukazuje, že traffic prestal smerovať na failed workload.

## Executable driver

Request corpus je JSONL:

```json
{"routing_key":"tenant-1/request-1","record":{"tenure_months":18,"monthly_spend_eur":84.5,"support_tickets_90d":2,"login_days_30d":12,"days_since_last_login":5,"contract_type":"monthly","region":"east","auto_pay":"no"}}
```

Spustenie:

```bash
python labs/mlops/scripts/run_canary_window.py \
  --routing-state labs/mlops/.runtime/canary-routing.json \
  --stable labs/mlops/.runtime/stable-deployment.json \
  --stable-endpoint http://127.0.0.1:8081 \
  --canary labs/mlops/.runtime/canary-deployment.json \
  --canary-endpoint http://127.0.0.1:8082 \
  --requests-jsonl labs/mlops/.runtime/canary-requests.jsonl \
  --minimum-canary-requests 20 \
  --maximum-canary-error-rate 0.05 \
  --evidence-output labs/mlops/.runtime/canary-evidence.json \
  --decision-output labs/mlops/.runtime/canary-decision.json \
  --rollback-output labs/mlops/.runtime/rollback-routing.json
```

Exit codes:

- `0` — continue,
- `2` — invalid contract/input,
- `3` — no-data alebo insufficient evidence,
- `4` — rollback decision a rollback state vytvorený.

## Testovaná hranica

Source tests spúšťajú dve oddelené Uvicorn apps na dvoch loopback portoch. Preukazujú:

- live HTTP requests na stable aj canary generation,
- deterministic routing distribution,
- 100/100 identity-bound successful responses v positive variante,
- latency evidence,
- continue decision po dosiahnutí request gate-u,
- wrong-endpoint identity mismatch,
- rollback decision a exact rollback state,
- no-data a insufficient-evidence stavy.

Test nepoužíva Docker engine, OCI image ani reálny trained model. Preto Practical v1 canary/rollback gate zostáva otvorený do containerized execution, actual image digest, live artifact mount a post-rollback traffic read-backu.
