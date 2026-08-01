# GitLab troubleshooting

GitLab incident sa nemá začínať otázkou „ktorý job je červený“. Najprv treba identifikovať presný platform subject: project a namespace, pipeline source, commit a target SHA, resolved CI graph, job attempt, runner/executor, credential capability, artifact alebo report, registry digest, deployment record a runtime generation. Rovnaký názov jobu môže patriť inému pipeline-u a zelený pipeline môže byť neúplný, ak sa required job pre `rules` vôbec nevytvoril.

Táto kapitola používa preserve-first workflow:

```text
user alebo release symptom
→ project/pipeline/job/artifact/deployment identity
→ timeline a recent changes
→ resolved graph a trust context
→ first missing alebo false transition
→ competing hypotheses
→ diskriminačný read-back
→ bounded containment
→ authoritative recovery
→ original, forbidden a second-operation verification
```

## Incident subject a minimálny evidence manifest

Atlas Payments hlási: production používa starý image, hoci GitLab pipeline pre commit `C72` je zelený. Pred retry alebo manual deployom sa uloží:

```text
GitLab instance a project ID
pipeline ID a source
commit SHA, target SHA a merge-result SHA
pipeline config SHA a included-config identities
job IDs, attempts a runner IDs
artifact/report checksums a expiry
container image index/platform digests
environment a deployment IDs
cluster/workload live digest
request a business operation ID
```

Praktické read-backy možno vykonať cez UI, REST API alebo `glab`. Commands nižšie sú model; exact fields a dostupnosť závisia od verzie a oprávnení inštancie.

```bash
glab api projects/:id/pipelines/8421 | jq .
glab api projects/:id/pipelines/8421/jobs --paginate | jq '.[] | {id,name,status,stage,runner:.runner.id,sha,web_url}'
glab api projects/:id/pipelines/8421/bridges --paginate | jq '.[] | {id,name,status,downstream_pipeline}'
```

Pipeline record dokazuje, ako GitLab klasifikoval konkrétny pipeline. Neobsahuje automaticky celý resolved YAML ani dôkaz, že runtime používa jeho artifact.

## 1. Pipeline sa nevytvoril alebo vznikol dvakrát

Prvým rozhodnutím je `pipeline source`: push, merge request event, tag, schedule, parent pipeline, API, web alebo iný trigger. `workflow: rules` rozhodujú, či pipeline vznikne. Job `rules` rozhodujú, či konkrétny job patrí do graphu.

Competing hypotheses pri chýbajúcom pipeline-e:

```text
workflow rule ho zámerne odmietla
include sa nedal načítať
YAML alebo expression bol neplatný
push a MR používajú odlišné variables
branch/tag pattern nesedel
pipeline bol superseded alebo auto-cancelled
permission alebo quota zabránila vytvoreniu
```

Source konfiguráciu treba odlíšiť od resolved configuration. Lint source súboru bez includes nepreukazuje výsledný graph. V GitLab UI/CI Lint alebo API sa kontroluje merged YAML a simulácia konkrétnych variables.

Duplicate push a merge-request pipelines často vzniknú, keď job rules povoľujú oba sources bez top-level `workflow` contractu. Symptómom sú dva artifacts, dva deploy attempts alebo approvals viazané na nesprávny pipeline. Oprava nevypína náhodný job; stanoví jediný authoritative pipeline pre merge decision a explicitne klasifikuje ostatné pipelines ako advisory.

## 2. Job je pending

`pending` znamená, že scheduler nevie job priradiť eligible runneru alebo čaká na inú platformovú podmienku. Kontroluje sa:

```text
job tags
runner tags a run-untagged policy
protected job/ref verzus protected runner
runner online/paused/stale status
runner scope: instance/group/project
concurrency a queue saturation
required executor/platform
resource group alebo environment lock
```

```bash
glab api projects/:id/jobs/9912 | jq '{status,tag_list,runner,queued_duration,ref,protected}'
```

Zvýšenie runner countu nepomôže, ak tags alebo protected eligibility nesedia. Naopak odstránenie tags môže poslať trusted deploy job na untrusted shared runner. Recovery musí zachovať trust class, nie iba skrátiť queue.

## 3. Job zlyhá pred scriptom

Failure pred prvým command outputom patrí často executor alebo preparation fáze:

```text
image pull alebo helper image
workspace/volume permission
Kubernetes Pod scheduling
Docker daemon alebo machine provisioning
cache/artifact restore
secret/variable resolution
network/DNS/TLS k GitLab-u alebo registry
```

Job trace treba čítať od prvého platform message, nie iba posledný riadok. Runner logs a executor events sú samostatný evidence source. Pri Kubernetes executore napríklad `Unschedulable`, image pull alebo admission failure nevyrieši retry application commandu.

Containment môže presmerovať jobs na known-good runner generation, ale najprv sa zachová runner version, config revision, executor image, node/Pod events a helper image digest. Inak sa po autoscaling replacement-e stratí jediný dôkaz.

## 4. Job script skončil nesprávnym statusom

Shell semantics, `allow_failure`, retries a after-script môžu vytvoriť false verdict. Pipeline môže byť zelený, ak failing scanner job je optional alebo command maskuje exit code:

```bash
scanner | tee scanner.log
```

Bez `pipefail` môže pipeline prevziať status `tee`. Podobne `command || true` mení failure na success. Diagnostika porovná native exit code, report artifact a GitLab job classification.

```text
command execution result
≠ uploaded report validity
≠ job status
≠ pipeline fan-in verdict
```

Oprava definuje stabilné verdict classes: pass, change failure, missing/incomplete evidence, tool/infrastructure failure a superseded. Infrastructure retry zachová first-attempt trace; nesmie premeniť neklasifikovaný fail-then-pass na čistý green result.

## 5. Includes, `extends`, defaults a variables vytvorili iný job

Resolved job môže dediť `image`, `before_script`, variables, cache alebo rules z viacerých zdrojov. Pri probléme sa porovná source snippet s merged YAML a job payloadom.

Variables majú precedence a scope. Rovnaký názov môže pochádzať z instance, group, project, environment scope, pipeline input, trigger, dotenv report alebo job definition. Masked/protected flags opisujú GitLab handling, nie to, že hodnota je bezpečná v každom command outpute.

Praktický incident: production deploy používa staging cluster. Source job obsahuje `${KUBE_CONTEXT}`, no environment-scoped variable `production/*` sa nezhoduje s názvom environmentu `prod`. Job preto použije group default. Read-back musí zaznamenať effective environment name, variable source a target cluster identity pred applyom.

Secret sa pri incidente nevypisuje. Overuje sa jeho fingerprint, issuer, audience, expiry a target capability. Pri OIDC/ID token flow sa kontroluje trust policy a claims; validný token ešte neznamená povolenú cloud operáciu.

## 6. Cache alebo artifact je stale, chýba alebo patrí inému subjectu

Cache je performance optimization a môže byť restored z iného pipeline-u podľa key a fallback policy. Artifact je deklarovaný job output a report má ďalšiu GitLab semantics. Troubleshooting vždy identifikuje:

```text
producer job ID a attempt
candidate SHA
artifact checksum
archive paths
expiry a retention
consumer job a `needs`/dependencies edge
cache key a protection namespace
```

Chýbajúci artifact môže znamenať, že producer nebežal, upload zlyhal, archive expiroval alebo consumer nepožiadal o správnu dependency. Stale output môže pochádzať z cache, warm workspace alebo rebuild-u.

Recovery neprekopíruje náhodný file z predchádzajúceho pipeline-u. Znovu vytvorí alebo získa output pre exact subject a invaliduje poisoned cache namespace. Security-sensitive generated code alebo dependencies sa nemajú považovať za authoritative iba preto, že cache hit zrýchlil job.

## 7. Registry tag ukazuje iné bytes

Container pipeline má odlíšiť tag, image index digest a per-platform manifest digest. Kontroluje sa publication output a registry read-back:

```bash
image='registry.example.com/atlas/payments'
tag='4.2.0'
crane digest "$image:$tag"
crane manifest "$image:$tag" | jq .
```

Ak production node spúšťa iba `linux/arm64`, index digest sám nestačí na koreláciu konkrétneho platform artifactu. Mutable tag môže byť prepísaný po schválení. Promotion a deployment preto používajú digest a release manifest.

Pri pull failure sa oddelí DNS/TLS/auth, manifest availability, platform match, blob transfer a local runtime unpack. `manifest unknown` nie je to isté ako `unauthorized` alebo `no matching manifest`.

## 8. Deployment record je úspešný, runtime nie

GitLab environment/deployment record opisuje pipeline operation. Pri push deployment-e môže byť vytvorený po úspešnom command-e. Pri GitOps môže pipeline iba commitnúť desired state. Ani jeden model automaticky nedokazuje controller reconciliation, serving cohort alebo business outcome.

Deployment troubleshooting spája:

```text
GitLab deployment ID
→ artifact/release digest
→ target environment identity
→ external controller operation
→ live workload generation
→ serving route/endpoints
→ business request
```

Príkazy závisia od targetu. Pri Kubernetes:

```bash
kubectl -n payments get deployment payments-api -o json | jq '.metadata.generation,.status.observedGeneration,.spec.template.spec.containers[].image'
kubectl -n payments get replicasets,pods,endpointslices -l app=payments-api -o wide
```

`Available=True` nepreukazuje správny digest ani business behavior. Environment URL môže smerovať na inú route alebo cache. Acceptance používa version endpoint a business operation identity.

## 9. Security scanning je zelený, ale evidence je neúplná

Analyzer job môže skončiť success bez reportu, report môže mať neplatnú schema alebo pipeline source nemusel vytvoriť očakávaný scanner. Vytvor expected scanner inventory podľa languages, packages, images, IaC a enabled policies a porovnaj ho s received valid reports.

```text
expected: sast, dependency, secret, container, IaC
received: sast, dependency, container
missing: secret, IaC
verdict: INCOMPLETE, nie PASS
```

Finding closure potrebuje fixed artifact a deployed-runtime correlation. Dismissal secretu bez revocation nie je remediation. Default-branch fix bez production redeployu ponecháva zraniteľný digest aktívny.

## 10. Preserve-first troubleshooting walkthrough

Pre incident „green pipeline, old production image“ postupuj:

1. Ulož project/pipeline/job/deployment IDs a UTC timeline.
2. Zisti pipeline source, candidate SHA a resolved job inventory.
3. Over build producer a artifact/image digest, nie tag.
4. Over, ktorý pipeline a job vytvoril deployment record.
5. Read-backni target identity a live runtime digest.
6. Porovnaj route/serving cohort s workload generation.
7. Vykonaj business probe so stabilným request ID.
8. Až potom zvoľ retry, redeploy toho istého digestu, rollout recovery alebo nový release.

Príklad causal chainu:

```text
MR pipeline testoval C72
→ tag pipeline rebuildla mutable base a vytvorila digest D73
→ deploy job použil tag, ktorý bol neskôr prepísaný na D74
→ GitLab deployment record stále niesol label 4.2.0
→ cluster bežal D71 pre imagePullPolicy/cache dôvod
→ health bol green, version endpoint starý
```

Oprava pinne build inputs, publikuje jeden digest, uloží ho v dotenv/release manifeste, scanner a deploy čítajú ten istý digest a runtime read-back ho porovná. Zakázaný test potvrdí, že mutable tag alebo chýbajúci scanner report nemôže dostať production verdict.

## Recovery a closure

Recovery sa uzatvára až keď:

```text
pipeline subject a expected jobs sú úplné
runner/executor trust zodpovedá jobu
credential je short-lived a target-scoped
artifact/report checksum patrí candidate-u
registry digest je immutable
GitLab deployment koreluje s runtime generation
business request prejde presne raz
zakázaná alternate path zostáva blocked
re-run alebo druhá operácia nevytvorí nový drift
```

Troubleshooting GitLabu je preto troubleshooting distribuovaného delivery systému. UI status je index, nie source pravdy pre všetky vrstvy. Presný verdict vzniká až koreláciou source, resolved graphu, execution, artifacts, deploymentu, runtime-u a business outcome-u.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Security scanning](security-scanning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Infrastructure as Code principles →](../07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
