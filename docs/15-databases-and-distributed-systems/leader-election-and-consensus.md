# Leader election a consensus

Leader election rozhoduje, ktorý participant má dočasne coordinovať prácu. Consensus rozhoduje, aká ordered history decisions je committed napriek podporovaným failures. Zvolený leader preto nie je automaticky navždy oprávnený vykonávať external effects. Authority musí byť viazaná na current term, lease alebo monotonic fencing epoch a destination musí stale epoch odmietnuť.

```text
coordination intent a non-mergeable invariant
→ exact cluster/application subject
→ members, failure domains a quorum
→ election timeout, term a leader
→ proposal a replicated log
→ quorum commit a ordered apply
→ client acknowledgement/read revision
→ lease-bound application ownership
→ fenced external mutation
→ failure, re-election a reconciliation
→ process-pause a second-election validation
```

Treba oddeľovať states `process believes leader`, `cluster elected leader`, `entry committed`, `member applied entry` a `external resource accepted effect`.

## 1. Consensus subject, failure model a quorum

Exact subject musí pomenovať chránený invariant, cluster a membership generation, voting/learner members, failure domains, quorum, crash/recovery a network assumptions, persistent storage, election/lease timing, read consistency, application ownership a external mutation boundary.

Raft/etcd je crash-fault consensus, nie Byzantine protocol. Timeouts nevedia dokázať crash; iba pozorujú chýbajúcu komunikáciu. Pre `N` voting members je majority quorum `floor(N/2)+1`: tri members tolerujú jeden simultaneous failure, päť members dva, ak zostane connected majority a storage/protocol assumptions platia.

Viac members nezvyšuje automaticky throughput ani availability. Zvyšuje quorum communication, failure-domain a operational surface. Členovia v rovnakom zone/account failure domain-e neposkytujú deklarovanú nezávislosť.

Consensus patrí k non-mergeable decisions, napríklad current configuration generation, ownership, unique allocation, membership alebo failover authority. Nie každý read ani byte potrebuje consensus.

## 2. Election, replicated log a visibility

Raft election zjednodušene:

```text
heartbeat absent do election timeoutu
→ follower zvýši term a kandiduje
→ majority vote
→ leader pre nový term
→ AppendEntries/heartbeats
```

V jednom fixed membership term-e sa legitímne majority leaders nemôžu rozdeliť do dvoch disjoint majorities. Old process však môže stále veriť, že je leader, držať stale connection alebo volať external provider. Consensus safety vlastnej history preto nestačí na application safety.

Proposal lifecycle je:

```text
client proposal
→ leader local append
→ replication peers
→ majority stores entry
→ entry committed
→ state machines apply in order
→ result visible podľa read contractu
→ client acknowledgement
```

Proposed, appended, replicated, committed, applied a externally visible sú odlišné states. Uncommitted entries old leadera môže nový leader prepísať. Local member môže zaostávať za commit indexom. Client, ktorý potrebuje current state, nesmie zamieňať local applied value s cluster-authoritative readom.

Operational evidence zahŕňa current term, leader identity, commit/applied index, per-member progress, pending proposals, fsync latency, election count a response revision.

## 3. Reads, leases a application leadership

Linearizable read musí overiť current consensus authority. Member-local/serializable read môže byť stale výmenou za latency alebo availability. Application musí explicitne preniesť requested mode, response revision/term a minimum acceptable generation.

Leader election service často používa lease-bound key:

```text
campaign
→ leader key attached to lease
→ periodic renew
→ lease loss/expiry
→ next campaigner
```

Jednorazový `Campaign` success neautorizuje nekonečný worker loop. Renew failure musí zastaviť new work admission a active work musí rešpektovať cancellation/unknown-outcome contract.

Lease nie je process-local timestamp. Bezpečnosť závisí od authoritative lease service-u, renew acknowledgement, process pause, network delay a behavioru po uncertainty. Local boolean `isLeader=true` je cache, nie authority.

## 4. Fencing external mutations

Fencing token je monotonically increasing epoch novej authority:

```text
new leader epoch 52
→ command carries 52
→ resource stores last accepted epoch 52

stale leader epoch 51
→ resource rejects mutation
```

Fencing musí byť enforce-nutý v mutation destination: database conditional write, command table, provider adapter/proxy, storage generation alebo broker producer epoch. Token iba zalogovaný v callerovi nič nezastaví.

Consensus môže vybrať operation ownera, ale nevie atomicky commitnúť arbitrary provider side effect mimo protocolu. External attempt stále potrebuje stable idempotency key, durable attempt/result evidence, lookup pri lost response-e a reconciliation. Fencing a idempotency riešia odlišné otázky: kto smie konať a či opakovaný logical intent vytvorí viac effectov.

Application split brain vzniká, keď consensus cluster uznáva jedného current leadera, ale old process pokračuje unfenced. Nie je to chyba election safety; je to missing enforcement medzi coordination a resource boundary.

## 5. Membership, maintenance a recovery

Membership je committed consensus state. Unsafe simultaneous remove/add môže znížiť reachable members pod quorum alebo vytvoriť ambiguous configuration. Changes sa robia sequentially: commit one change, overiť member sync/health, až potom ďalšia. Learner sa promotuje až po catch-up-e.

Planned leader transfer potrebuje caught-up target, bounded in-flight proposals, old leader demotion, client convergence a external fencing. Restart leadera nie je graceful handoff proof.

Pri majority loss-u cluster správne nemôže commitovať. Recovery nesmie vytvoriť nový independent cluster z minority bez explicitného disaster-recovery authority a reconciliation history. Pri disk corruption alebo restore-i treba zachovať cluster/member identity, committed revision a membership generation.

## 6. Connected incident `DB-PAY-59`

Atlas používal päťčlenný etcd cluster. Region A commitla route generation `912`. Reconciliation scheduler používal Election service s lease TTL `15 s`, renew intervalom `5 s` a batchom trvajúcim až `60 s`. Pred partition-om bol leader `reconciler-b-17` v Region B s epoch `51`.

Po partition-e old leader nedokázal lease renewnúť a Region A zvolila epoch `52`. Old process však nastavil `isLeader=true` iba pri pôvodnom campaign success-e, batch loop nekontroloval lease loss a provider request neniesol epoch. Pokračoval ďalších `42 s`, hoci cluster uznával iba epoch `52`.

Old worker spracoval `318` records; `74` operations dostalo attempts z oboch epochs a `27` vytvorilo duplicate physical provider attempts. Provider idempotency zachovala jeden financial effect, no `1 384` timeouted operations zostalo `sent-unknown` pre ďalšie reconciliation.

Root cause bola leadership overená iba pri vstupe do worker loopu a missing fencing na external mutation boundary. Election fungovala správne; application nepremietla current authority do každého effectful commandu.

## 7. Redesign a acceptance paths

Work unit je krátka a bounded: acquire operation ownership, overiť current leader key/epoch, vykonať jednu operation, durably zapísať result a až potom pokračovať. Každý provider command nesie `operation_id`, `leader_epoch`, `attempt_id` a stable provider idempotency key. Adapter alebo command authority odmietne epoch nižšiu než last accepted.

**Positive path** zvolí leadera, commitne decision, vykoná fenced mutation a zapíše durable result s current epoch.

**Lease-loss path** zastaví new admission okamžite; active operation sa dokončí iba podľa bounded contractu alebo vstúpi do unknown/reconciliation state-u.

**Recovery path** zabije leadera, zvolí nový term a redeliveruje operation. Old process alebo delayed request s old epoch je odmietnutý.

**Forbidden path** odmietne process-local permanent leadership, external mutation bez epoch, stale-epoch retry, uncommitted entry vydávanú za success a unsafe parallel membership changes.

Acceptance zahŕňa minority partition, majority loss, process pause dlhší než TTL, delayed old request, second election, leader transfer a membership reconfiguration.

## 8. Troubleshooting a anti-patterny

Diagnostika ide od exact cluster/application subjectu cez membership/quorum, terms/votes, leader, commit/applied indexes, read mode/revision, lease/campaign evidence, process-local state, fencing enforcement a external attempts až po re-election a reconciliation.

Najčastejšie anti-patterny sú `leader bol zvolený, môže konať`, predstava, že etcd zabráni všetkým application split brainom, lease uložená ako local timestamp, single leader zamieňaný s exactly-once, viac nodes bez failure-domain modelu, naraz menená membership a healthy leader považovaný za current applied state na každom memberovi.

## 9. Kontrolné otázky

1. Ako sa leader election líši od consensus?
2. Čo je quorum pre päť voting members?
3. Čo reprezentuje term alebo epoch?
4. Ako sa proposal, commit, apply a visibility líšia?
5. Prečo election timeout nedokazuje crash?
6. Prečo jednorazový Campaign success nestačí?
7. Kde sa musí fencing token enforce-nuť?
8. Ako idempotency dopĺňa fencing?
9. Prečo consensus v `DB-PAY-59` fungoval a application napriek tomu zlyhala?
10. Ktoré positive, lease-loss, recovery a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: consensus subject, leader election, consensus, voting member, learner member, majority quorum, term, candidate, leader, replicated log, proposal, commit index, applied index, election timeout, leader lease, leader key, fencing token, writer epoch, stale leader, application split brain, quorum-safe reconfiguration a consensus acceptance verdict.

## Primárne zdroje

- [etcd API guarantees](https://etcd.io/docs/v3.7/learning/api_guarantees/)
- [etcd Failure modes](https://etcd.io/docs/v3.8/op-guide/failures/)
- [etcd Runtime reconfiguration](https://etcd.io/docs/v3.6/op-guide/runtime-configuration/)
- [etcd Election API reference](https://etcd.io/docs/v3.6/dev-guide/api_concurrency_reference_v3/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Consistency models](consistency-models.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Retry, timeout a circuit breaker →](retry-timeout-and-circuit-breaker.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
