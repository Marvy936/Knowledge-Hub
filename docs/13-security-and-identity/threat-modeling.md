# Threat modeling

Threat modeling je systematický engineering proces, ktorým tím odvodzuje security a privacy requirements z konkrétneho systému ešte pred incidentom. Jeho výstupom nie je iba diagram ani zoznam STRIDE kategórií. Hodnota vzniká v reťazi od chráneného business outcome-u cez exact architecture generation a realistický attack path až po control, negative test, operational evidence a residual-risk decision.

Model musí byť dostatočne presný na rozhodnutie. „Attacker kompromituje CI“ nie je použiteľný threat statement, kým nevieme, ktorý actor, cez ktorý input alebo trust boundary, s akou capability, ktorý asset ovplyvní a aký forbidden outcome vznikne.

## Objective-to-negative-test lifecycle

Threat model je engineering control iba vtedy, keď chránený outcome vedie ku konkrétnemu attack pathu, requirementu a negative testu. Lifecycle ukazuje, ako sa architecture assumptions menia na falsifikovateľné dôkazy a residual-risk rozhodnutie.

```text
business/security objective
→ exact system generation a scope
→ assets, actors, data a state transitions
→ trust, identity a administrative boundaries
→ assumptions a dependency failure modes
→ concrete threat statement alebo attack tree
→ control mechanism a owner
→ testovateľná security requirement
→ negative test a runtime evidence
→ residual risk, exception a update trigger
```

Threat model nie je jednorazový dokument pri design review. Mení sa pri architecture, identity, data flow, dependency, deployment, trust alebo incident change-i. Model bez update triggera sa stáva historickou ilustráciou.

## Exact model subject SEC-PAY-50

Model subject fixuje source, builder, output a trust boundaries jednej release generation. To umožňuje rozlíšiť source-level controls od post-review a post-test mutation paths na persistentnom runneri.

```yaml
apiVersion: security.atlas.example/v1
kind: ThreatModel
metadata:
  name: payments-build-and-release
spec:
  generation: TM-PAY-50
  sourceRevision: a81f2e9
  builder: runner-prod-17
  builderImage: sha256:builder17
  outputImage: sha256:pay7240
  protectedOutcomes:
    - final image contains only approved build graph outputs
    - signing and provenance authority cannot be influenced by untrusted input
    - production runs only semantically verified platform digests
  trustBoundaries:
    - pull-request input to trusted build
    - tenant job to runner host
    - builder to registry
    - registry to admission
  forbiddenOutcomes:
    - command execution from PR metadata
    - post-test artifact injection
    - tenant-generated trusted provenance
    - unsigned or mismatched platform runtime
```

Manifest preukazuje exact architecture generation a required outcomes. Nepreukazuje, že diagram pokrýva všetky data flows, controls sú loaded alebo tests reálne bežia.

## Scope, assets a actors

Scope určuje, ktoré components, environments, identities a lifecycle stages model zahŕňa. Príliš úzky source-only scope v incidente vynechal persistent runner, builder helper, registry publication a signing authority. Príliš široký model „celá firma“ nevytvorí actionable requirements.

Assets zahŕňajú source, dependency graph, build definition, builder image, runner host, credentials, artifact digest, provenance, SBOM, signatures, registry tags/referrers, deployment policy a production business outcome. Actor nie je iba external attacker; patrí sem untrusted contributor, compromised dependency maintainer, malicious insider, compromised workload a accidental automation.

## Data-flow a trust-boundary model

Pre build pipeline môže byť dominantný flow:

```text
external contributor
→ pull-request title/body/files
→ source-control merge controls
→ CI orchestration
→ persistent runner host
→ build helper a toolchain
→ final filesystem
→ registry publication
→ signing/provenance/SBOM
→ admission policy
→ platform-specific runtime
```

Trust boundary je miesto, kde sa mení authority, validation alebo administrative control. PR metadata vstupuje do shellu; tenant workflow beží na privileged runneri; build output prechádza do signing authority; registry artifact prechádza do cluster admission. Network segment sám nie je jediný trust boundary. Identity a administrative boundaries sú rovnako dôležité.

## Assumptions musia byť falsifikovateľné

Assumption „runner je trusted“ je slabá. Falsifikovateľná verzia znie: „každý release build beží na fresh ephemeral workerovi bez state-u z predchádzajúceho jobu; tenant step nemá host root, Docker socket ani signing credential; platform mimo tenant jobu generuje provenance“. Každá časť sa dá overiť.

Incident ukázal nepravdivé assumptions: runner bol persistentný, helper spracoval PR title cez shell, signing/provenance bežali v rovnakom tenant-controlled jobe a final SBOM inventarizovala source lockfile, nie final filesystem.

## Threat statements

Použiteľný threat statement má actor, condition, action, asset a impact. Tieto prvky vytvárajú kauzálnu vetu, z ktorej možno odvodiť presný control owner, observation point a forbidden negative test; samotný názov attack technique takýto engineering vstup neposkytuje.

```text
Ak untrusted contributor vloží shell metacharacters do merged-PR title
pričom vulnerable build helper interpoluje title do privileged shellu na persistentnom runneri,
môže po testoch zmeniť final filesystem a publikovať podpísaný malicious image,
čím poruší artifact integrity a production settlement trust.
```

Takýto statement priamo vedie ku controls: structured argument passing, pinned fixed helper, ephemeral isolation, no tenant signing authority, final-artifact inventory a semantic admission.

## STRIDE, attack trees, CAPEC a ATT&CK

STRIDE pomáha systematicky prejsť spoofing, tampering, repudiation, information disclosure, denial of service a elevation of privilege pri každom elemente/flow-e. Nie je risk score ani zoznam mitigácií.

Attack tree rozkladá cieľ na alternatívne a kombinované paths. Cieľ „run malicious production artifact“ môže mať branches compromise source, dependency, builder, registry, signer, admission alebo runtime. Tree odhalí, že podpis artifactu nechráni pred compromised builderom, ak signer autorizuje každý builder output.

CAPEC poskytuje attack-pattern vocabulary; MITRE ATT&CK opisuje observed adversary techniques a detection context. Ani jeden framework nenahrádza system-specific data flow a requirement. Copy-paste technique IDs bez boundary a evidence nevytvára threat model.

## Z threatu na requirement a negative test

Threat sa uzavrie až testovateľným requirementom. Pre PR metadata:

```text
Requirement TM-PAY-50-R7:
Release pipeline nesmie interpretovať source-control metadata ako shell program.
Všetky metadata sa prenášajú cez structured API alebo argument array.
Adversarial title s `$(...)`, backticks, quotes a newlines nesmie vytvoriť process,
meniť filesystem ani ovplyvniť artifact digest mimo expected metadata field-u.
```

Controlled negative fixture môže vytvoriť test PR metadata a sledovať process/file evidence:

```bash
python scripts/render_release_metadata.py \
  --title 'release $(touch /tmp/SHOULD_NOT_EXIST) `id`' \
  --output /tmp/release-metadata.json

test ! -e /tmp/SHOULD_NOT_EXIST
jq -e '.title == "release $(touch /tmp/SHOULD_NOT_EXIST) `id`"' \
  /tmp/release-metadata.json
```

Prvý command preukazuje spracovanie konkrétnej fixture v test harness-e. `test` a `jq` overia forbidden side effect a exact data preservation. Nepreukazujú production runner isolation, všetky input fields ani absence command execution v inom pipeline kroku.

## Authentication, authorization a multi-tenancy threats

Identity flow sa modeluje od proofing/authenticatora cez session/token, claims mapping, resource authorization a revocation. Threat „valid token accesses wrong tenant object“ nie je authentication defect; je object authorization a tenant-boundary failure.

Multi-tenant model musí zahŕňať control plane, data plane, backups, caches, observability, support/admin tools, migrations a external providers. Tenant ID v UI alebo request header nie je trust anchor. Authority sa odvodzuje z verified principal-to-tenant relation a server-side resource identity.

## Availability, privacy a unsafe fallback

Threat modeling zahŕňa outage a recovery. Fail-open policy pri PDP outage, global retry pri provider failure, broad break-glass alebo restore bez tenant filtering môžu porušiť C/I pri pokuse zachrániť A.

Privacy model sleduje collection, purpose, linkage, retention, access a deletion. Observability fields môžu obísť primary data controls. Recovery path môže obnoviť zmazané data alebo old credentials. Tieto flows patria do modelu rovnako ako primary request.

## Risk treatment a residual risk

Likelihood a impact nie sú presné čísla bez uncertainty. Tím môže používať qualitative alebo quantitative model, ale zachová inputs a assumptions. Treatment môže znížiť probability, blast radius alebo recovery time; residual risk potrebuje ownera, expiration a monitoring.

Control „code review“ neznižuje builder compromise risk, ak malicious state vzniká po review. WAF neznižuje malicious CI metadata path. Každý control sa viaže na exact mechanism a observation point.

## Incident SEC-PAY-50

Pôvodný threat model končil pri approved source a dependency scan-e. Nezahŕňal persistent runner, PR metadata ako code-adjacent input, builder helper, post-test filesystem mutation ani tenant-controlled evidence generation. Crafted title preto spustil command injection a vložil `settlement-debug.jar` do final image po testoch.

Image mala matching signature a provenance, pretože compromised pipeline podpisovala vlastný output. SBOM bola source-lockfile inventory a injected JAR neobsahovala. Admission kontrolovalo existenciu evidence, nie approved builder a final-artifact completeness.

Root cause bol incomplete trust model a vulnerable privileged execution path. Scanner finding bol trigger; assumptions o runner isolation, provenance authority a SBOM stage boli system-level defects.

## Containment, model update a acceptance

Containment quarantinuje runner a outputs, zachová evidence a zastaví promotion. Model sa aktualizuje pred výberom controls, aby recovery neopravila iba konkrétny title parser a nevynechala persistent host, signing authority alebo final filesystem.

Authoritative recovery používa fresh ephemeral workers, pinned fixed helper, structured metadata, no tenant signing credentials, platform-generated provenance, final-artifact SBOM a semantic admission. Negative tests pokrývajú crafted metadata, state z previous jobu, post-test injection, wrong builder identity a evidence generated neapproved authority.

Acceptance vyžaduje, aby každý threat statement mal ownera, requirement, automated alebo rehearsed negative test a runtime observation. Druhý architecture change — napríklad nový build cache alebo runner pool — musí explicitne trigger-nuť model review. Model, ktorý sa po zmene trust boundary automaticky neotvorí, nie je lifecycle control.

## Kontrolné otázky

1. Prečo diagram bez security objectives nie je kompletný threat model?
2. Ako sa identity a administrative boundary líšia od network boundary?
3. Čo robí assumption falsifikovateľnou?
4. Ako STRIDE, attack tree a ATT&CK slúžia odlišným účelom?
5. Prečo podpis artifactu nebráni compromised builderu?
6. Čo negative fixture pre PR title preukazuje a čo nie?
7. Ktoré architecture changes musia znovu otvoriť model?

## Referencie

- [NIST Threat Modeling Workshop materials](https://www.nist.gov/itl/ssd/software-quality-group/threat-modeling)
- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [Microsoft Threat Modeling](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool)
- [MITRE CAPEC](https://capec.mitre.org/)
- [MITRE ATT&CK](https://attack.mitre.org/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Vulnerability a patch management](vulnerability-and-patch-management.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Supply-chain security →](supply-chain-security.md)
<!-- KNOWLEDGE-NAVIGATION:END -->