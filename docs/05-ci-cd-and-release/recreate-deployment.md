# Recreate deployment

Recreate deployment používa jeden exkluzívny runtime slot. Stará application generation musí slot úplne opustiť skôr, než ho prevezme nová. Tým sa odstráni mixed-version obdobie, ale zámerne vznikne capacity gap, počas ktorého služba alebo konkrétna capability nie je dostupná.

Recreate nie je automaticky primitívna ani nesprávna stratégia. Môže byť najbezpečnejšia pre singleton writer, stateful component bez podporovaného failoveru, incompatible protocol generation alebo malú internú službu s akceptovaným maintenance window. Musí však explicitne riadiť admission, drain, writer fencing, data transition, restart a business recovery. „Scale to zero a potom up“ nie je complete state machine.

## 1. Dominantný exclusive-slot model

```text
approved maintenance a exact release subject
→ zastavenie nového admissionu
→ drain in-flight work a queues
→ fence old writers a potvrď zero ownership
→ old generation stopped
→ backup/checkpoint a migration transition
→ new generation deployed bez trafficu
→ functional readiness a data reconciliation
→ riadené obnovenie admissionu
→ business acceptance
→ old generation retirement alebo recovery closure
```

Najkritickejší boundary je medzi „old sa vypína“ a „new je schopný bezpečne prevziať work“. Ak drain nie je complete alebo old writer stále drží lease, new generation môže vytvoriť duplicate side effects. Ak maintenance window skončí pred business recovery, process readiness nepomôže.

## 2. Exact recreate subject

```yaml
recreateSubject:
  service: settlement-writer
  releaseManifestDigest: sha256:release1000rc4
  oldRelease: payments-9.9.3
  oldArtifactDigest: sha256:writer993
  newRelease: payments-10.0.0-rc.4
  newArtifactDigest: sha256:writer1000
  environmentGeneration: prod-eu-1844
  exclusiveResources:
    writerLease: settlement-writer-primary
    queueConsumerGroup: settlement-finalizer
    databaseWriterRole: payments_writer
  dataContract:
    before: settlement-schema-v41
    transition: migration-42-exclusive
    after: settlement-schema-v42
  maintenanceWindow:
    start: 2026-07-31T22:00:00Z
    end: 2026-07-31T22:15:00Z
  recoveryReference: recreate-recovery-1000rc4
```

Service name a desired image nestačia. Subject musí pomenovať exclusive resources, data contract a recovery point. Inak sa nedá overiť, či old generation naozaj opustila všetky authority paths.

## 3. Eligibility a downtime budget

Recreate je vhodné iba ak user/business owner akceptuje outage alebo existuje alternate capability. Downtime budget sa skladá:

```text
admission stop
+ drain
+ process termination
+ migration/checkpoint
+ startup
+ warm-up
+ functional validation
+ traffic restore
+ business backlog recovery
```

Historický process startup 30 sekúnd neznamená 30-sekundový downtime. Queue drain, cold cache a migration môžu dominovať. Plan má p50/p95 a hard abort points podľa rehearsal evidence.

## 4. Admission stop a drain

Najprv sa zastaví nový work. HTTP ingress môže vrátiť maintenance response alebo route-nuť read-only path. Queue consumer sa pozastaví bez straty ownership evidence. Scheduled producers sa zastavia alebo bufferujú podľa contractu.

Kubernetes workload možno scale-nuť až po explicitnom admission step-e:

```bash
kubectl -n payments annotate deployment settlement-writer \
  atlas.example/admission-state=closed --overwrite

kubectl -n payments scale deployment settlement-writer --replicas=0
kubectl -n payments rollout status deployment/settlement-writer --timeout=5m
```

Scale-to-zero preukazuje desired replica count a controller convergence. Nepreukazuje, že external queue prestala deliverovať, že in-flight request dokončil commit alebo že terminated process nemal unknown provider outcome. Application drain metrics a authoritative operation table musia potvrdiť zero unresolved ownership.

## 5. Writer fencing

Process termination nie je writer fencing. Network partition alebo stuck node môže pokračovať. Safe exclusive transition používa generation/lease/fencing token, ktorý old writer už nemôže obnoviť.

```text
writer epoch 41 active
→ admission closed
→ lease renewal disabled
→ wait expiry alebo revoke epoch
→ database/provider rejects epoch 41
→ issue epoch 42 new generation
```

Database read-back:

```sql
SELECT holder_id, fencing_epoch, expires_at
FROM operational_leases
WHERE lease_name = 'settlement-writer-primary';
```

Query preukazuje authoritative lease row v database snapshot-e transakcie. Nepreukazuje external side effect path, ak provider request neobsahuje fencing/idempotency identity. Exclusive resources inventory musí byť complete.

## 6. Backup, checkpoint a migration

Before irreversible transition sa vytvorí recovery point podľa data consistency contractu. Snapshot existence nepreukazuje application-consistent restore. Recreate môže byť zvolený práve preto, že no writers umožnia clean checkpoint.

```bash
./scripts/create-checkpoint.sh \
  --release payments-9.9.3 \
  --expected-writer-epoch 41 \
  --output checkpoint.json

jq -e '.writerEpoch == 41 and .unresolvedOperations == 0 and .outboxLag == 0' checkpoint.json
```

Predicate preukazuje declared checkpoint fields. Nepreukazuje správnosť scriptu ani storage durability. Backup catalog, restore rehearsal a independent database queries dopĺňajú evidence.

Migration sa vykonáva s exact bundle digest a idempotentným journalom. Timeout po DDL môže byť unknown outcome; pred retry sa číta migration state a schema.

## 7. New generation startup bez admissionu

New workload sa spustí s trafficom stále zatvoreným:

```bash
kubectl -n payments set image deployment/settlement-writer \
  writer='registry.atlas.example/settlement-writer@sha256:writer1000'
kubectl -n payments scale deployment settlement-writer --replicas=1
kubectl -n payments rollout status deployment/settlement-writer --timeout=5m

kubectl -n payments get pods -l app=settlement-writer \
  -o jsonpath='{range .items[*]}{.metadata.uid}{" "}{.status.containerStatuses[0].imageID}{"\n"}{end}'
```

Output preukazuje controller rollout a runtime image ID. Nepreukazuje, že writer získal epoch 42, loaded schema contract alebo že processing je correct. Capability check sa vykoná na bounded synthetic work bez user admission.

## 8. Business recovery a backlog

Po otvorení admissionu môže backlog spôsobiť overload. Recreate plan má recovery capacity a rate limits. Service availability nie je obnovená, kým oldest work age a business completion nevrátia SLO boundary.

```text
new writer owns epoch 42
→ admission opens gradually
→ queue depth/oldest age monitored
→ authoritative outcomes reconciled
→ no duplicate/lost effect
→ normal capacity restored
```

Maintenance page removal pred backlog recovery môže vytvoriť druhý incident.

## 9. Rollback boundary

Rollback je jednoduchý iba pred incompatible data transition. Po schema contract alebo external side effects môže byť old binary neeligible. Plan má checkpoints:

```text
pre-migration
→ old restart možný

post-expand-compatible migration
→ old/new možno compatible podľa evidence

post-destructive migration
→ old restart forbidden; roll-forward/restore required
```

Old artifact retention bez compatible data state nie je rollback readiness.

## Ako funguje recreate deployment state machine

Recreate deployment najprv ukončí starú generation a až potom spustí novú. Jeho hlavnou vlastnosťou je explicitný interval bez aplikačnej kapacity. Táto stratégia môže byť vhodná pri single-writer workload-e, nekompatibilnom local state alebo systéme, kde mixed-version prevádzka nie je možná, ale downtime musí byť súčasťou schváleného contractu.

Pred zastavením starej generation sa overí, že nový artifact a configuration sú dostupné, migrácie majú známu eligibility a existuje recovery cesta. Drain musí uzavrieť alebo presmerovať nové requests, dokončiť či bezpečne uložiť in-flight prácu a zachovať operation identities. Process stop bez business drainu môže zanechať unknown side effects.

Po vypnutí sa read-backom potvrdí, že staré procesy, endpoints a writers naozaj zmizli. Až potom sa vykoná migration alebo spustí nová generation. Startup success a readiness nie sú final verdict; služba musí prejsť reálnou route, loaded configuration a business synthetic.

Ak nový release zlyhá, rollback je možný iba vtedy, keď stará application zostala kompatibilná s aktuálnymi dátami a external effects. Ak migration už contractla schema alebo nový writer emitoval neznámy event, recovery môže vyžadovať roll-forward, restore alebo compensation.

Recreate je jednoduchý v počte cohort, ale náročný na správne modelovanie downtime a state-u. Jeho bezpečnosť nevzniká z príkazu „stop all, start all“, ale z preconditions, drainu, explicitnej outage komunikácie a overeného recovery postupu.

## 10. Connected incident `REL-PAY-69`

Atlas zvolil recreate pre singleton settlement writer, pretože release menil local state format. Maintenance budget bol 10 minút. Runbook scale-nul Deployment a po Pod termination spustil migration. Queue admission však nebola zatvorená na brokeri a old writer na partitioned node držal provider credential aj lease cache.

```text
Kubernetes replicas = 0
→ tím predpokladal zero writers
→ broker ďalej prideľoval work old processu
→ migration zmenila schema
→ new writer získal work s epoch 42
→ old writer dokončil 31 provider requests s epoch 41
```

Kubernetes rollout ukazoval success. Business ledger obsahoval duplicate provider effects a 83 operations v unknown state-e. Downtime prekročil 24 minút kvôli reconciliation.

Root cause bol incomplete exclusive-slot subject. Pod count sa zamieňal za writer fencing a broker/provider paths neboli v inventory.

## 11. Redesign a acceptance verdict

Redesign pridá central admission gate, database fencing epoch, broker pause/read-back, provider idempotency identity, clean checkpoint a staged reopen. Maintenance rehearsal meria end-to-end business recovery, nie iba Pod startup.

Recreate deployment je prijatý iba vtedy, keď:

```text
downtime a recovery budget sú business-approved
+ all admission paths sú zatvorené
+ in-flight/queue ownership je drained alebo bounded
+ old writers sú autoritatívne fenced
+ recovery point je clean a restorable
+ migration outcome je read-backnutý
+ new runtime získa novú exclusive generation
+ admission sa otvorí až po capability validation
+ duplicate/lost outcomes sú forbidden
+ second maintenance rehearsal splní budget
```

## 12. Troubleshooting flow

Pri recreate incidente sleduj:

```text
maintenance/admission state
→ in-flight a queue ownership
→ process/container inventory
→ lease/fencing generations
→ checkpoint a migration journal
→ new runtime image/config/schema
→ admission reopen
→ backlog a business reconciliation
```

Competing hypotheses môžu byť hidden producer, incomplete drain, orphan process, stale lease, migration partial outcome, cold dependency, startup failure, overload pri reopen alebo incompatible rollback. Pod absence je iba jeden observation point.

## 13. Anti-patterny

### Scale to zero ako dôkaz zero writers

External process, broker lease alebo side-effect capability môže prežiť.

### Downtime odhad podľa startup času

Drain, migration, validation a backlog recovery často dominujú.

### Snapshot existence ako restore proof

Recovery point potrebuje consistency a rehearsal evidence.

### Automatický old-version restart po migration failure

Old binary môže byť nekompatibilný s current schema alebo events.

### Otvorenie trafficu po readiness

Readiness nepreukazuje exclusive ownership ani business correctness.

## 14. Kontrolné otázky

1. Kedy je recreate vhodnejšie než mixed-version rollout?
2. Čo tvorí exact exclusive-slot subject?
3. Z čoho sa skladá downtime budget?
4. Prečo Pod count nepreukazuje zero writers?
5. Ako fencing epoch chráni transition?
6. Čo musí preukázať clean checkpoint?
7. Ako sa rieši unknown migration outcome?
8. Prečo new Pod readiness nestačí?
9. Kedy je binary rollback forbidden?
10. Ktoré hidden paths spôsobili `REL-PAY-69`?
11. Ako sa overuje duplicate/lost forbidden outcome?
12. Čo musí zmerať second rehearsal?

## Glossary impact

Relevantné pojmy: recreate deployment, exclusive runtime slot, maintenance window, admission closure, drain, writer fencing, fencing epoch, clean checkpoint, migration journal, unknown migration outcome, bounded reopen, backlog recovery, rollback eligibility a exclusive-slot acceptance.

## Primárne zdroje

- [Kubernetes documentation — Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes documentation — Pod termination](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination)
- [Kubernetes API — Lease](https://kubernetes.io/docs/reference/kubernetes-api/cluster-resources/lease-v1/)
- [PostgreSQL documentation — Backup and Restore](https://www.postgresql.org/docs/current/backup.html)
- [Google SRE — Handling Overload](https://sre.google/sre-book/handling-overload/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Release management](release-management.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Rolling update →](rolling-update.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
