# Pull-based deployment

Pull-based deployment nie je iba to, že controller pravidelne číta Git. Je to trust a execution model, v ktorom deployment agent pri target environment-e získava approved desired state, porovnáva ho s live state-om a vykonáva mutation podľa vlastnej scoped identity.

Hlavný bezpečnostný a operational benefit vzniká vtedy, keď CI alebo developer nemusí držať production cluster credentials a nemôže obísť reconciler priamym pushom do target API.

## 1. Dominantný model

```text
approved environment intent
→ authoritative desired-state ref
→ agent observation/pull
→ source authentication a revision resolution
→ deterministic render a policy gate
→ desired-vs-live comparison
→ bounded sync/prune operation
→ health a business verification
→ continuous re-observation
→ failure, rollback a second-pull closure
```

Pull model musí zachovať identity a evidence od approved source generation až po effective target mutation.

## 2. Push vs. pull

### Push-based deployment

External pipeline alebo operator sa pripojí k target environment-u a vykoná mutation:

```text
CI runner
→ production credential
→ kubectl/helm/cloud API
→ target mutation
```

### Pull-based deployment

Agent s target-scoped identity pozoruje desired state a vykonáva reconciliation:

```text
CI
→ commit/promotion do Git-u

in-cluster alebo target-side agent
→ pull approved desired state
→ compare
→ apply/reconcile
```

Rozdiel nie je iba network direction. Rozdiel je:

- kto drží production write credential;
- kto rozhoduje, ktorá source generation je aktuálna;
- či deployment pokračuje po výpadku CI;
- či live drift vzniknutý neskôr možno detegovať a opraviť;
- či target agent vynucuje destination a resource boundaries;
- či deployment mutation je opakovateľná a reconciled.

## 3. Pull model podľa OpenGitOps

OpenGitOps oddeľuje štyri vlastnosti:

1. desired state je declarative;
2. desired state je versioned a immutable;
3. software agents ho pullujú automaticky;
4. software agents kontinuálne pozorujú actual state a pokúšajú sa ho reconcile-nuť.

Webhook môže zrýchliť observation, ale nesmie byť jediným spôsobom, ako agent zistí zmenu. Agent musí vedieť periodicky znovu overiť source aj target state.

## 4. Deployment subject

Pull-based deployment subject obsahuje:

- environment a application identity;
- desired repository, path a resolved revisions;
- source credential a trust roots;
- destination cluster/namespace a agent identity;
- allowed Kubernetes API groups/kinds/namespaces;
- render toolchain a inputs;
- sync policy, prune, self-heal a retry policy;
- dependency ordering a hooks;
- live resource tracking identity;
- deployment, health a business acceptance boundaries;
- rollback a emergency mutation contract.

Bez exact subjectu sa tvrdenie `agent pulluje Git` nedá overiť.

## 5. Credential boundary

Silný pull model minimalizuje production credentials mimo target control plane-u.

```text
CI identity
→ write approved Git refs
→ no direct production API permission

GitOps agent identity
→ read trusted repositories
→ mutate iba povolené destinations/resources
```

To znižuje blast radius compromised CI runnera. Neodstraňuje však potrebu:

- chrániť repository write path;
- overovať source authenticity;
- obmedziť agent RBAC;
- chrániť repository a cluster credentials;
- oddeliť tenants a projects;
- auditovať agent actions;
- riadiť break-glass access.

Controller s cluster-admin prístupom ku všetkým clusters a repositories môže byť väčší trust concentration než pôvodný pipeline.

## 6. Source polling a webhook

Agent môže zistiť zmenu:

- periodickým pollingom;
- Git webhookom;
- cache invalidation eventom;
- explicitným refresh requestom.

Webhook je hint:

```text
push event
→ webhook
→ agent refresh
```

Ak webhook vypadne, periodic reconciliation musí zmenu nakoniec zachytiť. Ak source branch force-pushne alebo dependency zmení význam bez eventu, agent musí aj tak znovu resolve-nuť effective source.

Observation interval ovplyvňuje:

- deployment latency;
- drift detection latency;
- source load;
- rate-limit exposure;
- simultaneous fleet refresh;
- incident recovery time.

Jitter a bounded concurrency bránia thundering herd-u pri veľkom počte applications.

## 7. Pull neznamená automatický sync

Agent môže desired state pullovať a porovnávať, ale mutation môže byť:

- automatická;
- manuálne schválená v Argo CD;
- viazaná na change window;
- pozastavená pre freeze;
- postupná podľa waves alebo external rollout controlleru.

```text
pull + compare
→ OutOfSync evidence
→ manual alebo automated sync decision
```

Pull model teda opisuje authority a execution direction. Auto-sync je samostatná policy.

## 8. Deployment trigger vs. deployment authority

CI job môže po merge zavolať refresh alebo sync endpoint. To ešte nemusí porušiť pull model, ak:

- agent sám číta source;
- CI neposiela rendered manifests ako hidden desired state;
- agent používa vlastnú scoped target identity;
- requested revision je authoritative a policy-valid;
- controller urobí vlastný compare a apply;
- continuous reconciliation pokračuje aj bez CI.

Rizikový model:

```text
CI render
→ CI kubectl apply
→ Argo CD iba monitoruje
```

Tu je CI deployment writer a pull agent nie je authoritative executor.

## 9. Source authentication a revision resolution

Agent musí overiť:

- repository endpoint;
- SSH host key alebo TLS trust;
- authentication credential scope;
- commit/tag signature, ak je required;
- branch/tag/commit resolution;
- path a generator inputs;
- submodules a dependencies;
- chart alebo OCI artifact digest;
- ambiguous ref names;
- revoked repository access.

`targetRevision: release-1.0` môže byť nejednoznačný, ak rovnaké meno má branch aj tag. Fully qualified ref alebo commit pin znižuje ambiguity.

## 10. Render a policy pred mutation

Target agent nesmie slepo aplikovať source files. Potrebuje:

```text
source revision
→ render
→ parse/schema validation
→ target-aware policy
→ diff
→ dry-run alebo server-side validation
→ mutation
```

Policy môže overiť:

- trusted source a artifact;
- namespace/destination;
- prohibited cluster-scoped resources;
- image digest a provenance;
- security context;
- resource requests/limits;
- destructive prune;
- required labels/ownership;
- secret reference policy;
- change-window alebo approval evidence.

CI policy a agent-side policy majú rozdielne observation points. Agent-side gate vidí final rendered state a destination context.

## 11. Sync operation

Pull agent typicky vykonáva:

1. inventory desired resources;
2. inventory tracked live resources;
3. normalizáciu a diff;
4. ordering;
5. apply/create/replace podľa policy;
6. prune removed resources, ak je povolený;
7. čakanie na health alebo hooks;
8. status a evidence publication.

Sync success neznamená automaticky business success. Apply môže prejsť, ale workload môže používať nesprávnu database generation, provider credential alebo feature flag.

## 12. Continuous pull a convergence

Jednorazový pull po merge nie je GitOps closure.

```text
source changes
→ agent reconciles
→ live drift occurs later
→ agent observes again
→ reports alebo repairs
```

Continuous observation zachytáva:

- manual mutation;
- failed alebo partial previous apply;
- controller/defaulting changes;
- deleted resource;
- new source revision;
- target recovery po outage-i;
- source credential recovery;
- cluster reconnect;
- resource ownership change.

Agent musí po restarte vedieť reconstruct-nuť desired a live inventory bez skrytého in-memory deployment state-u.

## 13. Offline a disconnected behavior

Keď agent stratí Git:

- live workloads zvyčajne pokračujú;
- agent nemôže potvrdiť newest desired generation;
- cached source môže byť stale;
- manual drift môže zostať neopravený;
- prune alebo destructive action nemá používať neúplný empty render ako truth;
- status musí rozlíšiť source-unreachable od Synced.

Keď agent stratí target API:

- source môže ďalej postupovať;
- desired revisions sa queue-ujú alebo preskakujú podľa policy;
- po reconnecte treba rozhodnúť, či aplikovať najnovšiu generation alebo postupné required transitions;
- hooks a migrations môžu mať unknown outcome.

## 14. Push/pull hybrid a multi-writer race

Najčastejší anti-pattern:

```text
merge do Git-u
→ Argo auto-sync

súčasne
→ CI kubectl apply

súčasne
→ on-call patch
```

Writers môžu aplikovať odlišné renders a field-manager ownership:

```text
Argo apply generation A
→ CI apply generation B
→ Argo compare s ignore rules
→ on-call patch generation C
```

Každý krok môže technicky prejsť, ale final state nemá jednu authority ani deterministic rollback.

## 15. Emergency a break-glass path

Production incident môže vyžadovať rýchlu direct mutation. Pull model ju nemusí absolútne zakázať, ale musí ju ohraničiť:

```text
explicit incident/break-glass approval
→ short-lived scoped credential
→ evidence-preserving mutation
→ immediate Git proposal alebo temporary exception record
→ owner a expiry
→ controller diff visible
→ authoritative reconciliation
→ credential revoke
→ second-drift test
```

Self-heal môže emergency patch okamžite revertovať. Preto break-glass procedure musí koordinovať controller policy, nie agent jednoducho vypnúť bez návratového gate-u.

## 16. Rollback v pull modeli

Rollback je nový desired-state transition:

```text
current generation B
→ approved rollback commit/ref na generation A alebo compatible C
→ agent pull
→ compare
→ reconcile
→ validate
```

Nie je to:

```text
kubectl rollout undo
→ Git stále B
```

Taký rollback vytvorí drift a pull controller ho môže znovu prepísať.

Kompletný rollback musí zahŕňať:

- manifests a image digests;
- database compatibility;
- config/secrets generation;
- hooks a external effects;
- traffic/feature state;
- controller overrides;
- pruned resources;
- business reconciliation.

## 17. Connected incident `GITOPS-PAY-61`

Intended pull path pre `payments 9.0`:

```text
CI build/test
→ image digest + environment PR
→ merge commit 9f31c2a
→ Argo repository observation
→ Argo render/compare
→ Argo sync
→ health + settlement canary
```

Skutočný path:

```text
merge commit 9f31c2a
→ CI kubectl apply rendered workspace
→ Argo auto-sync inej resolved generation
→ on-call kubectl patch
→ self-heal disabled
→ broad ignoreDifferences
```

CI runner mal production kubeconfig s oprávnením meniť Deployments a ConfigMaps. Po merge:

- Git webhook dorazil do Argo CD o `20:14:03`;
- CI direct apply začal o `20:14:04`;
- Argo sync začal o `20:14:07`;
- on-call patch prišiel o `20:18:26`;
- production branch bola force-pushnutá na starší commit o `20:21:11` a vrátená o `20:28:09`.

Writers používali odlišné inputs:

```text
CI render:       pay900a + route 1841
Argo resolved:   pay899hf7 + route 1842
manual patch:    pay900b, ostatné fields ponechané live
```

Argo agent nebol jediný deployment executor. Pull model preto nedokázal garantovať:

- že target mutation pochádza z approved Git generation;
- že controller apply je posledný writer;
- že rollback ref-u obnoví live state;
- že drift bude detegovaný alebo opravený;
- že CI compromise nemá direct cluster blast radius.

### Pull-based root cause

Production deployment mal hybrid push/pull ownership. CI a humans držali direct write credentials nad rovnakými fields ako Argo controller a neexistoval mandatory handoff alebo reconciliation gate.

### Recovery

- revoke production kubeconfig z CI;
- oddeliť CI permission na Git promotion od Argo target identity;
- zaviesť project-scoped Argo destination/resource permissions;
- odstrániť hidden rendered workspace apply;
- obnoviť one-writer field contract;
- zaviesť short-lived break-glass credential;
- overiť agent behavior pri webhook loss, source outage, target outage a restart-e;
- testovať second pull po manual drift-e.

## 18. Pull-based acceptance verdict

Pull-based deployment je prijatý, keď:

- exact source, target, agent a credential subjects sú explicitné;
- desired state je automatically observed nezávisle od jedného webhooku;
- agent resolve-uje authoritative revision a final render inputs;
- CI nemá direct target write access alebo má explicitne oddelený, bounded contract;
- agent identity je scoped podľa destination, namespace a resource type;
- repository credentials a trust roots sú scoped a rotovateľné;
- agent-side validation/policy vidí final render a destination context;
- sync, prune, hooks a health boundaries sú explicitné;
- source/target outage a agent restart behavior sú definované;
- manual sync, auto-sync a self-heal semantics sú rozlíšené;
- break-glass path má expiry, audit, Git reconciliation a credential revoke;
- rollback je desired-state transition a neostáva iba live patchom;
- webhook loss, CI compromise, direct drift, partial sync a second-pull tests prejdú;
- forbidden hidden push, cluster-wide credential, stale cache apply a false-deployment outcomes sú odmietnuté.

## 19. Troubleshooting flow

```text
declared Git change sa neaplikoval alebo runtime obsahuje inú generation
→ exact application/environment subject
→ authoritative ref a resolved commit
→ webhook/poll observation evidence
→ agent source auth/cache/render
→ policy/diff/sync decision
→ target credential a API response
→ field managers a concurrent writers
→ health/business outcome
→ source/target outage alebo retry history
→ authoritative reconcile a second pull
```

## 20. Anti-patterny

### Pipeline zavolá `kubectl`, ale Git je stále source of truth

Pipeline je vtedy production writer. Git môže byť evidence source, nie jediná mutation authority.

### Webhook = pull

Webhook je trigger/hint. Pull agent musí source pozorovať aj bez neho.

### Auto-sync je povinný pre GitOps

Nie. Pull a continuous compare môžu existovať aj s manual sync gate-om.

### Agent má cluster-admin, lebo je to jednoduchšie

Centralizuje blast radius a oslabuje tenant/project boundary.

### Rollback spravíme `kubectl rollout undo`

Ak Git zostáva na broken generation, reconciler rollback zruší alebo drift zostane permanentný.

### Vypneme Argo počas incidentu

Bez evidence, expiry a re-enable gate-u sa dočasný postup zmení na unmanaged environment.

## 21. Kontrolné otázky

1. Ako sa push-based a pull-based deployment líšia v credential boundary?
2. Prečo webhook nie je jediný pull mechanismus?
3. Ako pull súvisí s continuous reconciliation?
4. Prečo pull neznamená automatický sync?
5. Kedy CI-triggered sync zostáva pull modelom?
6. Čo musí agent overiť pri revision resolution?
7. Ako source outage mení deployment verdict?
8. Ako target outage mení pending desired generations?
9. Prečo direct CI apply porušil `GITOPS-PAY-61`?
10. Ako má vyzerať break-glass lifecycle?
11. Prečo live rollback musí byť zaznamenaný v desired state?
12. Čo overuje pull-based acceptance verdict?

## Glossary impact

Relevantné pojmy: pull-based deployment subject, target-side agent, source observation, reconciliation polling, webhook hint, target credential boundary, agent identity, agent-side policy, sync decision, continuous pull, source-unreachable state, target-unreachable state, push/pull hybrid, break-glass handoff, desired-state rollback a pull-based acceptance verdict.

## Primárne zdroje

- [OpenGitOps Principles](https://opengitops.dev/)
- [Argo CD — Automated Sync Policy](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/)
- [Argo CD — Architectural Overview](https://argo-cd.readthedocs.io/en/stable/operator-manual/architecture/)
- [Argo CD — Tracking and Deployment Strategies](https://argo-cd.readthedocs.io/en/stable/user-guide/tracking_strategies/)
