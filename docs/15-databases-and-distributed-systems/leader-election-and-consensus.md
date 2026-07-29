# Leader election a consensus

Leader election a consensus sú súvisiace, ale odlišné mechanisms.

- **Leader election** rozhoduje, ktorý participant má dočasne vykonávať coordinujúcu rolu.
- **Consensus** zabezpečuje, že distributed participants sa zhodnú na jednej usporiadanej history rozhodnutí napriek failures v podporovanom modeli.

Zvolený leader nie je automaticky oprávnený vykonať arbitrary external effect navždy. Application musí viazať leadership na term, lease, revision alebo fencing token a každý authoritative mutation path musí stale leadera odmietnuť.

## 1. Dominantný model

```text
coordination/invariant intent
→ exact consensus a leadership subject
→ members, failure domains a quorum
→ term/epoch a candidate election
→ leader authority
→ proposal a replicated log
→ quorum commit
→ ordered apply a client acknowledgement
→ lease/fencing pri external mutation
→ failure, re-election a reconciliation
→ second-election validation
```

Kľúčové je rozlíšiť `leader believes`, `cluster elected`, `entry committed`, `state applied` a `external effect accepted`.

## 2. Prečo potrebujeme consensus

Distributed replicas potrebujú jednotne rozhodnúť napríklad o:

- current configuration generation;
- lock/lease ownership;
- membership;
- leader epoch;
- ordered commands;
- failover authority;
- metadata state;
- unique allocation.

Bez consensus alebo domain-specific merge modelu môžu concurrent writers vytvoriť divergentné authoritative histories.

Consensus nie je potrebný pre každý byte alebo read. Používa sa tam, kde coordination chráni non-mergeable invariant.

## 3. Failure model a assumptions

Pred hodnotením algoritmu treba pomenovať:

- crash-stop alebo crash-recovery nodes;
- Byzantine behavior či jeho absenciu;
- message loss, delay a reordering;
- persistent storage guarantees;
- clock assumptions;
- network partition;
- member count a quorum;
- membership change protocol;
- external side effects.

Raft/etcd rieši crash-fault consensus s majority quorum a nie je Byzantine consensus protocol.

## 4. Quorum

Pre `N` voting members je majority quorum:

```text
floor(N / 2) + 1
```

Príklady:

| Members | Quorum | Tolerované simultaneous failures |
|---:|---:|---:|
| 1 | 1 | 0 |
| 3 | 2 | 1 |
| 5 | 3 | 2 |
| 7 | 4 | 3 |

Viac members nezvyšuje automaticky výkon. Zvyšuje quorum communication cost a operational surface.

## 5. Terms a leader election

Consensus history je rozdelená do monotonically increasing terms alebo epochs.

Zjednodušený Raft election flow:

```text
follower nedostáva heartbeat
→ election timeout
→ candidate zvýši term
→ požiada peers o votes
→ majority vote
→ leader pre nový term
→ heartbeats/AppendEntries
```

Election timeout je failure detector založený na čase. Nevie dokázať crash; iba rozhoduje, že communication nebola pozorovaná v limite.

## 6. Election safety

V jednom term-e nesmú byť zvolení dvaja legitímni leaders s majority supportom. Majority quorums sa pretínajú, preto dve disjoint majorities v rovnakom fixed membership sete neexistujú.

To však nezabraňuje:

- old processu veriť, že je stále leader;
- stale client connection;
- external provideru prijať call od old leadera;
- application cache držať starý leader flag;
- nesprávnej membership reconfiguration;
- side effectu mimo consensus guardu.

## 7. Replicated log

Leader prijme proposal a replikuje log entry followers.

```text
client proposal
→ leader appends locally
→ AppendEntries peers
→ majority stores entry
→ entry committed
→ state machines apply in order
→ client acknowledgement podľa contractu
```

Treba rozlíšiť:

- proposed;
- appended;
- replicated;
- committed;
- applied;
- externally visible.

Uncommitted entries starého leadera môže nový leader prepísať. Committed entry sa nesmie stratiť v supported failure model-e.

## 8. Commit vs. apply

Consensus commit znamená, že entry je durably accepted majority logom podľa protocolu. State machine apply môže mierne zaostávať.

Operational evidence preto zahŕňa:

- current term;
- leader identity;
- commit index;
- applied index;
- pending proposals;
- per-member match/applied progress;
- disk fsync latency;
- election count.

Client, ktorý potrebuje current applied state, nesmie zamieňať `committed` s `applied on this local member`.

## 9. Linearizable reads

Linearizable read musí potvrdiť, že read source reprezentuje current consensus authority.

V etcd sú default range reads linearizable; `serializable` range môže byť member-local a stale výmenou za nižšiu latency a vyššiu availability.

Read contract preto musí preniesť:

- requested consistency mode;
- response revision;
- cluster/member identity;
- term;
- minimum acceptable revision/generation.

## 10. Leader election nie je distributed lock navždy

Leader role môže byť viazaná na lease:

```text
campaign
→ leader key + lease
→ lease renew
→ lease expiry/revoke
→ next campaigner
```

Application musí priebežne overovať ownership. Jednorazový úspech `Campaign` neautorizuje nekonečný worker loop.

## 11. Leases a clocks

Lease je časovo obmedzené právo spravované authoritative coordination systemom. Bezpečnosť závisí od:

- kto meria expiry;
- renew acknowledgement;
- failure detector semantics;
- process pause;
- network delay;
- client handling po renew failure;
- grace period;
- external fencing.

Local wall-clock flag `lease valid until 18:10` bez authoritative renew evidence je slabý.

## 12. Fencing tokens

Fencing token je monotonically increasing epoch priradený novej authority.

```text
leader term/epoch 51
→ mutation carries epoch 51
→ resource accepts only epoch >= last_seen_epoch

stale leader epoch 50
→ rejected
```

Fencing musí byť enforced v destination/resource boundary. Token iba zapísaný do logu bez validation nič nezastaví.

Príklady enforcementu:

- database row `writer_epoch` condition;
- storage generation pre lock ownera;
- provider proxy kontrolujúci controller epoch;
- broker producer epoch;
- job table compare-and-set;
- API request field validated current authority service-om.

## 13. Split brain na application vrstve

Consensus cluster môže zostať safe, no application vytvorí dual execution:

```text
old leader stratí lease
→ process-local flag zostane true
→ new leader zvolený
→ oba workers volajú external provider
```

To nie je consensus split brain, ak cluster uznáva iba new leadera. Je to **unfenced application leadership**.

## 14. Leader transfer a planned maintenance

Planned transfer potrebuje:

- current leader eligibility;
- target caught-up state;
- bounded in-flight proposals;
- client routing convergence;
- old leader demotion;
- external fencing;
- post-transfer read/write verification.

Samotný process restart môže vyvolať election, ale negarantuje graceful handoff.

## 15. Membership changes

Membership je consensus state, nie statický config na jednotlivých nodes.

Unsafe changes môžu zmeniť quorum tak, že cluster stratí progress alebo vytvorí ambiguous configuration.

Safe reconfiguration:

```text
one membership change
→ commit current configuration
→ verify new member sync/health
→ next change
```

etcd strict reconfiguration checks odmietajú changes, ktoré by znížili started members pod quorum. Learner musí byť dobehnutý pred promotion.

## 16. Consensus a external systems

Consensus nevie atomicky commitnúť arbitrary provider operation, ak provider nie je participant rovnakého protocolu.

```text
consensus says worker W owns operation O
→ W calls provider
→ response lost
```

Consensus pomáha rozhodnúť ownership, ale unknown external outcome stále potrebuje:

- idempotency key;
- durable attempt record;
- provider lookup;
- reconciliation;
- fencing epoch;
- retry owner.

## 17. Connected incident `DB-PAY-59`

Atlas provider-route control používal päťčlenný etcd cluster. Quorum side Region A commitla route generation `912`.

Samostatný reconciliation scheduler používal etcd Election service:

```text
leader lease TTL: 15 s
renew interval:     5 s
worker batch:       up to 60 s
```

Pred partition-om bol leader `reconciler-b-17` v Region B s leader epoch `51`.

Po partition-e:

1. Region B leader nedokázal renew-nuť lease cez quorum.
2. Region A campaigner získal leadership s epoch `52`.
3. `reconciler-b-17` mal process-local `isLeader=true` nastavený pri pôvodnom `Campaign` success-e.
4. Batch loop nekontroloval lease loss medzi provider operations.
5. Provider request neobsahoval fencing epoch.
6. Starý worker pokračoval ďalších `42 s`.

Consensus cluster uznával iba epoch `52`. Application však umožnila epoch `51` vykonávať external side effects.

## 18. Consensus/leadership root cause

Primary root cause bol:

> Leadership bola overená iba pri vstupe do worker loopu a external mutation boundary nevynucovala current monotonic fencing epoch.

Trigger bol regional partition. Consensus election fungovala správne.

Amplifiers:

- 60-sekundový non-interruptible batch;
- local boolean leadership cache;
- provider API bez epoch validation;
- retry policy nezviazaná s operation owner epoch;
- stale route generation `911` v Region B;
- observability sledovala počet elected leaders v etcd, nie concurrent external actors.

## 19. Dôsledky

Počas overlap window:

- old epoch `51` worker spracoval `318` operation records;
- new epoch `52` worker spracoval rovnaký backlog partition z current authority;
- `74` logical operations dostalo attempts z oboch epochs;
- `27` operations vytvorilo duplicate physical provider attempts;
- provider idempotency zabezpečila jeden financial effect;
- `1 384` timeouted operations zostalo v `sent-unknown` cohort-e pre ďalšie retries/reconciliation.

Znovu platí: zero duplicate financial effects neznamená, že leader/fencing contract prešiel.

## 20. Evidence-preserving containment

```text
pause all reconciliation campaigners
→ preserve etcd term, leader key, lease a revision evidence
→ preserve worker process/batch/epoch logs
→ revoke old workload identity
→ fence provider mutation path
→ classify attempts by operation_id + leader_epoch
→ query provider idempotency ledger
→ resume iba one current fenced worker cohort
```

## 21. Authoritative redesign

### Short bounded work units

```text
acquire operation ownership
→ validate current leader key/epoch
→ process one bounded operation
→ durable result
→ release/next
```

### Transactional leadership guard

Leader key sa používa na transactional guard coordination mutation, nie iba na initial election.

### Fencing

Každý reconciliation/provider command obsahuje:

```text
operation_id
leader_epoch
attempt_id
provider_idempotency_key
```

Provider adapter alebo authoritative command table odmietne epoch nižšiu než current accepted epoch.

### Lease-loss handling

- renew failure okamžite ruší new work admission;
- active operations kontrolujú cancellation boundary;
- unknown external attempts sa nerepeatnú bez lookupu;
- old identity sa revokuje pri failover-e;
- leader change event je business telemetry dimension.

## 22. Consensus acceptance verdict

Leader-election/consensus design je prijatý, keď:

- exact coordination/invariant subject je explicitný;
- failure model, members, failure domains a quorum sú zdokumentované;
- term/epoch, leader, commit a apply state sú observable;
- election timeout a expected failover window sú testované;
- linearizable vs. member-local reads sú explicitné;
- leadership je lease/term-bound, nie process-local forever flag;
- every authoritative/external mutation path vynucuje fencing;
- stale leader nemôže vykonať forbidden effect;
- client acknowledgement zodpovedá committed/applied boundary;
- membership changes sú sequential a quorum-safe;
- unknown external outcomes majú idempotency a reconciliation;
- leader failure, minority partition, majority loss, process pause a second election tests prejdú;
- forbidden dual-writer, stale-epoch a uncommitted-as-success outcomes sú odmietnuté.

## 23. Troubleshooting flow

```text
dual leader, lost decision alebo unavailable coordinator
→ exact cluster/election/application subject
→ membership a quorum
→ terms, votes a current leader
→ log match/commit/applied indexes
→ read consistency mode/revision
→ lease/campaign ownership
→ process-local leadership state
→ fencing token enforcement
→ external side effects a retries
→ re-election/reconciliation
→ second-election validation
```

## 24. Anti-patterny

### Leader bol zvolený, teda môže konať

Leadership môže expirovať alebo byť nahradená. Mutation potrebuje current guard/fencing.

### etcd zabráni všetkým split brainom

Chráni vlastný consensus state. Application môže stále vykonať unfenced dual side effects.

### Lease je timestamp v procese

Authoritative expiry a renew evidence sú dôležitejšie než local clock.

### Jediný leader znamená exactly once

Crash po external effecte pred durable resultom vytvára unknown outcome a retry.

### Viac nodes znamená vyššiu availability bez ceny

Quorum latency, failure domains a operations sa menia.

### Remove/add members naraz

Membership changes môžu stratiť quorum; musia byť committed sequentially.

### Healthy leader znamená current applied state

Commit/apply lag, local read mode a client cache môžu vrátiť starý state.

## 25. Kontrolné otázky

1. Ako sa leader election líši od consensus?
2. Čo je majority quorum pre 5 members?
3. Čo reprezentuje term alebo epoch?
4. Ako sa proposal, commit a apply líšia?
5. Prečo timeout nevie dokázať leader crash?
6. Čo je leader lease?
7. Prečo je fencing token potrebný?
8. Kde sa musí fencing enforce-nuť?
9. Ako application split brain vznikol v `DB-PAY-59`?
10. Prečo provider idempotency nenahrádza fencing?
11. Ako bezpečne meniť membership?
12. Čo overuje consensus acceptance verdict?

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
