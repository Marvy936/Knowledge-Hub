# Security scanning

## Metadata

- Status: Learning
- Level: L2
- Domain: GitLab

GitLab security scanning je evidence a risk-decision systém. Scanner sám o sebe nevytvára bezpečnostný verdict. Dôveryhodný lifecycle musí vedieť, čo malo byť analyzované, čo sa skutočne analyzovalo, aký immutable subject report opisuje, ako sa findings vyhodnotili a či zraniteľný obsah reálne beží.

```text
attack-surface a immutable subject
→ expected scanner inventory
→ valid analyzer execution
→ complete report evidence
→ contextual risk triage
→ gate / exception / remediation
→ fixed artifact verification
→ deployed-digest correlation
→ continuous rescanning a revocation
```

`0 findings` je dôveryhodný výsledok iba vtedy, keď coverage a execution validity sú dokázané.

## 1. Nosný model: coverage, evidence, decision a runtime state

Security scanning odpovedá na štyri oddelené otázky.

### Coverage

Ktoré časti attack surface boli applicable a analyzované?

### Evidence

Prebehli required scanners nad správnym subjectom a vytvorili complete, spracovateľné reporty?

### Decision

Aký risk predstavujú findings vzhľadom na reachability, exposure, confidence a compensating controls?

### Runtime state

Ktorý release digest je publikovaný, podporovaný a skutočne nasadený?

```text
clean source scan
≠ clean release image
≠ complete scanner inventory
≠ bezpečný deployed runtime
```

## 2. Nosný scenár: Atlas Payments release 3.13.0

Atlas release manifest `RM313` obsahuje:

```text
source SHA S313
api image digest D_api_313
worker image digest D_worker_313
amd64 manifest D_api_amd64
arm64 manifest D_api_arm64
SBOM E313
config C44
production environment production-eu
```

Expected scanner inventory `SEC313`:

```text
SAST nad merged-result source S313
dependency scan nad resolved lockfiles/SBOM
secret detection nad diffom a relevantnou históriou
container scan per platform digest
IaC scan nad deployment source a rendered plan
API/DAST scan nad review deploymentom RM313
continuous rescan nad podporovanými a deployed digests
```

Lifecycle:

```text
vytvor expected inventory SEC313
→ spusti scanners v správnych contexts
→ validuj analyzer/report identities
→ triage findings a exceptions
→ gate release RM313
→ deploy D_api_313/D_worker_313
→ mapuj findings na production-eu
→ pri novej advisory znovu vyhodnoť deployed digests
→ patch, rebuild, verify a redeploy
```

## 3. Scan subject musí byť immutable

Možné subjects:

- source alebo merged-result SHA;
- resolved dependency graph a lockfile revision;
- SBOM digest;
- package version a checksum;
- OCI image alebo platform manifest digest;
- IaC source a rendered plan revision;
- API schema plus deployment digest/config;
- release manifest.

Scan `app:latest` nie je stabilný dôkaz. Tag sa môže medzi scanom, gate-om a deploymentom presunúť.

Atlas report preto uchováva:

```text
scanner a version
ruleset/advisory revision
subject type a immutable ID
platform/variant
pipeline/job/attempt
report schema a checksum
scan time
coverage limitations
```

## 4. Expected scanner inventory oddeľuje clean od incomplete

Pre každý project alebo release class definuj, ktoré controls musia existovať.

```text
SEC313 expected:
SAST = required
dependency = required
secret = required
container amd64 = required
container arm64 = required
IaC source + plan = required
DAST/API = required pre production promotion
```

Actual inventory môže byť:

```text
SAST complete
secret complete
container amd64 complete
container arm64 missing
IaC complete
DAST tool error
```

Verdict nie je clean. Je `incomplete/tool-error`, aj keď prijaté reporty obsahujú nula blocking findings.

## 5. Execution validity

Scanner execution je platný iba ak:

```text
expected subject bol dostupný
→ analyzer/ruleset identity je známa
→ required source/build metadata existuje
→ advisory data je dostupná a fresh podľa policy
→ analysis dokončila bez silent fallbacku
→ report vznikol
→ report schema je podporovaná
→ upload a GitLab processing prešli
→ expected components/shards/platformy sú complete
```

Verdicty:

- `clean` — platný complete scan nenašiel findings v deklarovanej coverage;
- `findings` — platný scan našiel výsledky;
- `incomplete` — chýba scanner, component, shard alebo report;
- `invalid` — scanner analyzoval nesprávny subject alebo unusable input;
- `tool error` — analyzer, runner, registry alebo advisory service zlyhali;
- `unsupported` — relevantný surface nemá podporovaný analyzer;
- `skipped by approved policy` — zámerná výnimka s ownerom a scope-om.

Tool error ani unsupported nie sú clean.

## 6. Vrstvy attack surface

### Source a data flow — SAST

SAST analyzuje source/build representation a hľadá napríklad injection, path traversal, unsafe deserialization a taint flows. Nevidí automaticky runtime identity, effective config alebo všetky dynamické paths.

### Resolved dependencies a SBOM

Dependency scan potrebuje lockfile, resolved graph alebo SBOM. Manifest bez resolution môže vynechať transitive, platform-specific alebo vendored components.

SBOM je inventory, nie bezpečnostný verdict ani provenance. Musí byť viazaný na konkrétny artifact digest a kontrolovaný na completeness.

### Runtime image — container scanning

Container scan analyzuje final OCI platform digest. Dependency scan source tree a container scan odpovedajú na odlišné otázky: deklarovaný graph verzus skutočný runtime obsah.

### Secret exposure

Secret detection hľadá credential-like material v diff-e alebo histórii. Pozitívny nález spúšťa revoke/rotate/audit workflow; dismissal alebo history rewrite credential nezneplatní.

### Runtime behavior — DAST a API security testing

DAST/API scan potrebuje konkrétny environment, deployment digest, role matrix, route scope, test data, rate limits, abort criteria a cleanup. Jedna privileged identity neoverí tenant a object-level authorization.

### Infrastructure as Code

IaC source scan treba pri kritických zmenách vrstviť s rendered-plan policy a runtime verification, pretože source nemusí obsahovať provider defaults, admission mutations alebo drift.

Žiadna vrstva nenahrádza ostatné.

## 7. Pipeline contexts nie sú zameniteľné

Security evidence môže vzniknúť v:

- pre-commit alebo push protection;
- merge-request pipeline;
- merged-results alebo merge-train pipeline;
- default-branch pipeline;
- artifact/release pipeline;
- scheduled scan;
- DAST environment-e;
- continuous rescan systéme.

Branch SAST nad S313 nepreukazuje, že D_api_313 obsahuje rovnaké dependencies. Default-branch scan neopisuje automaticky starší release stále bežiaci v produkcii.

## 8. Report je evidence contract

Machine-readable report musí umožniť overiť:

```text
subject identity
scanner/ruleset/advisory revision
component a platform inventory
execution verdict
finding identity a location
report schema/checksum
pipeline/job/attempt
```

Zelený analyzer job bez prijatého reportu vytvára execution evidence, nie security evidence.

Fan-in gate porovnáva expected a actual report manifest. Neagreguje iba to, čo náhodou existuje.

## 9. Finding, vulnerability record a baseline

- **Finding:** výsledok konkrétneho scanu konkrétneho subjectu.
- **Vulnerability record:** dlhšie žijúci risk objekt s ownerom, SLA, exception a remediation históriou.

Lifecycle:

```text
needs triage
→ confirmed/false positive
→ risk decision
→ remediation alebo exception
→ fixed artifact
→ verified
→ closed alebo re-detected
```

MR delta musí používať fresh baseline aktuálneho target subjectu. Stará baseline môže finding nesprávne označiť ako nový alebo ho skryť.

## 10. Contextual risk decision

Severity je iba vstup. Atlas zohľadňuje:

- reachability a exploitability;
- internet/tenant exposure;
- privilege a data sensitivity;
- affected deployed digest;
- active exploitation;
- dostupnosť fixu;
- compensating controls;
- scanner confidence;
- business impact.

Príklad:

```text
reachable high v internet-facing runtime dependency
→ môže blokovať

critical v nepoužitom test-only tooli
→ urgentne triage, ale odlišný runtime risk
```

Risk decision musí byť reprodukovateľný a viazaný na finding, subject a environment context.

## 11. Gate verdicty

```text
complete + clean
→ allow

complete + blocking finding
→ block

complete + valid nonblocking exception
→ allow with visible risk

required scanner/report missing
→ incomplete, nepovoliť promotion

advisory database alebo analyzer failure
→ policy-defined pause / fail / break-glass
```

Gate nemá používať iba celkový počet findings. Legacy baseline a newly introduced reachable risk majú odlišný význam.

## 12. Exceptions a dismissals

Exception obsahuje:

```text
finding/vulnerability identity
affected component a release digest
contextual risk a dôvod
compensating controls
owner a approver
expiration/review date
remediation plan
```

Prehodnotí sa pri novom release, zmene exposure, novej exploit intelligence, zmene finding fingerprintu alebo expirácii controlu.

Dismissal bez expirácie mení dočasné rozhodnutie na skrytý permanentný debt.

## 13. Analyzer je supply-chain dependency

Scanner často dostáva celý source, dependency metadata a niekedy registry credentials. Analyzer image, template, ruleset a advisory database preto potrebujú:

- pinned alebo controlled identity;
- provenance/signature podľa assurance modelu;
- protected update workflow;
- isolated runner a scoped credentials;
- outbound network policy;
- canary rollout novej version;
- invalid/tool-error monitoring;
- compromise response.

Kompromitovaný analyzer môže exfiltrovať viac než aplikácia, ktorú skúma.

## 14. Deployed-artifact correlation

Security systém musí vedieť prepojiť:

```text
finding/advisory
→ component/package version
→ SBOM a image digest
→ release manifest
→ deployment record
→ effective environment/runtime digest
→ service owner a exposure
```

Oprava v `main` neznamená opravenú produkciu. Produkcia je opravená až po buildnutí nového immutable artifactu, jeho overení, deployment-e a effective-state validácii.

## 15. Continuous rescanning

Nové CVE môže vzniknúť bez source zmeny.

```text
nová advisory
→ match proti SBOM/package/image inventory
→ nájdi supported releases
→ nájdi deployed digests a exposure
→ triage reachability/risk
→ patch source/dependency
→ build nový immutable artifact
→ scan a gate
→ redeploy
→ verify runtime replacement
→ update support/revocation state
```

Rescan iba default branchu vynechá staršie podporované releases a production digests.

## 16. DAST safety state machine

```text
target a digest prechecks
→ test identity a route scope
→ scan active
→ guardrail monitoring
→ abort pri side effecte alebo instability
→ cleanup test data/session
→ environment validation
```

DAST nesmie neúmyselne vytvoriť reálne payments, emaily alebo destructive mutations. Scope, rate, identity a cleanup sú súčasť security evidence.

## 17. Worked failure: zelený security job nevytvoril platný report

Atlas aktualizoval analyzer. Job skončil exit code 0, ale nový report schema nebola podporovaná GitLab processing vrstvou.

```text
analyzer job green
→ report upload prejde ako súbor
→ parser report odmietne
→ aggregate gate počíta iba prijaté reports
→ pipeline pass
→ MR UI ukáže nula findings
```

### Príčina

Gate nemal expected report inventory ani processing-verdict check. Zamieňal job success za security evidence.

### Dôsledok

Release RM313 bol promotionovaný bez SAST výsledku.

### Náprava

```text
expected scanner/report manifest
→ report schema compatibility fixture
→ processing acknowledgement
→ missing/invalid report = incomplete
→ analyzer canary rollout
```

## 18. Worked failure: scan tagu minul arm64 digest

Publication job vytvoril multi-platform tag `3.13.0`. Container scanner analyzoval `app:3.13.0` v čase, keď tag dočasne ukazoval iba na amd64 manifest. Neskôr fan-in doplnil arm64 digest a presunul tag.

```text
scan tag → D_api_amd64 clean
→ tag sa presunie na OCI index amd64 + arm64
→ gate zachová starý clean report
→ arm64 workload nasadí D_api_arm64
→ arm64 variant obsahuje vulnerable package
```

### Príčina

Evidence bola viazaná na mutable tag, nie na final OCI index a expected platform inventory.

### Náprava

- publish final index digest až po complete fan-in;
- scan každý platform digest;
- reporty viazať na platformu a final release subject;
- missing variant = incomplete;
- deployment policy overí scanned index/digest relation.

## 19. Worked failure: secret finding bol dismissed, credential ostal aktívny

Secret detection našla provider token v commit history. Developer ho označil ako resolved po odstránení z latest commitu.

```text
finding dismissed
→ token ostáva v Git history a starom job artifacte
→ provider credential nebol revoked
→ external actor token použije
```

### Príčina

Security workflow považoval source cleanup za credential recovery. Chýbal provider-side revocation a usage audit.

### Náprava

```text
revoke/disable u providera
→ rotate dependent credentials
→ audit exposure window a use
→ odstráň artifacts/logs podľa možností
→ history cleanup ako sekundárny krok
→ prevention regression
```

## 20. Worked failure: main bol opravený, produkcia ostala zraniteľná

Nová advisory označila dependency vo verzii 3.13.0. Tím aktualizoval dependency na `main` a default-branch scan bol clean.

```text
main clean
→ release 3.13.0 stále referencuje D_api_313
→ production-eu stále beží D_api_313
→ dashboard sleduje iba current branch
→ runtime vulnerability zostáva
```

### Príčina

Continuous rescan neprepájal advisory so supported release a deployed digest inventory.

### Náprava

Vytvoriť patched release 3.13.1, overiť nový digest, nasadiť ho, potvrdiť effective runtime replacement a podľa rizika revoke-nuť 3.13.0.

## 21. Kauzálny diagnostický walkthrough

Symptom: security dashboard tvrdí `0 blocking vulnerabilities`, ale incident feed uvádza kritické CVE v package, ktorý môže byť v production image.

### Krok 1 — stabilizuj subject a runtime

```text
release = RM313
production digest = D_api_313
platform = arm64
SBOM = E313
expected inventory = SEC313
```

### Krok 2 — konkurenčné hypotézy

```text
H1: dependency nie je v D_api_313
H2: scanner analyzoval iný tag/digest alebo iba amd64
H3: container scanner/report chýbal alebo bol invalid
H4: advisory database pri pôvodnom scane CVE nepoznala
H5: finding má platnú exception alebo bol nesprávne dismissed
H6: deployment inventory nesprávne mapuje runtime digest
H7: package je prítomný, ale nereachable; dashboard používa contextual suppression
```

### Krok 3 — diskriminačné observation points

- runtime package inventory a SBOM testujú H1;
- report subject/platform/index mapping testuje H2;
- expected-versus-actual scanner/report manifest testuje H3;
- advisory/ruleset revision a rescan time testujú H4;
- vulnerability record a exception audit testujú H5/H7;
- live runtime digest a deployment record testujú H6.

Atlas zistí, že original scan pokrýval iba amd64 a continuous rescan nemal arm64 digest v inventory. D_api_arm64 package obsahuje. H2/H3 vysvetľujú false clean.

### Krok 4 — containment

- zastaviť ďalšie arm64 promotion/deployments;
- označiť RM313 security verdict ako incomplete/affected;
- podľa exploitability znížiť exposure alebo route-nuť na safe platform/release;
- spustiť scan presného arm64 digestu;
- vytvoriť patched immutable release.

### Krok 5 — over pôvodný outcome

```text
nový arm64 digest scan complete
CVE package absent alebo fixed
OCI index inventory complete
production runtime používa patched digest
old digest je blocked/revoked podľa policy
security dashboard mapuje finding na správny runtime
```

### Krok 6 — skorší control

Finding sa mení na per-platform expected inventory, final-index scan binding, deployed-digest continuous rescan a gate invariant `missing platform report cannot be clean`.

## 22. Scanner compromise response

Pri podozrení na kompromitovaný analyzer alebo template:

```text
stop affected jobs a credential access
→ identifikuj pipelines/projects/releases
→ revoke runner/registry/cloud credentials
→ audit egress, artifacts a publications
→ označ evidence za nedôveryhodnú
→ obnov pinned trusted analyzer
→ znovu skenuj release subjects
→ prehodnoť artifacts vytvorené v rovnakom trust context-e
```

## 23. Diagnostický runbook

1. Urči immutable source/package/image/plan/environment subject.
2. Zostav expected scanner a report inventory.
3. Over pipeline applicability a job creation.
4. Over analyzer, ruleset, advisory data a execution verdict.
5. Over report schema, checksum, upload a processing.
6. Skontroluj platform/shard/component completeness.
7. Over baseline, finding identity, exception a triage context.
8. Prepoj affected digest s release a effective deployments.
9. Rozlíš clean, findings, incomplete, invalid a tool error.
10. Contain-ni runtime risk, vytvor fixed artifact a over redeployment.

## 24. Referenčné pravidlá

- Nula findings bez coverage evidence nie je clean.
- Scan subject musí byť immutable a platform-specific podľa potreby.
- Job success nie je report success.
- Expected inventory odlišuje complete pass od false green.
- Dependency a container scan nie sú zameniteľné.
- SBOM je inventory, nie bezpečnostný verdict ani provenance.
- Secret remediation začína revocation, nie dismissalom.
- Severity potrebuje reachability, exposure a runtime context.
- Exceptions majú ownera, scope a expiráciu.
- Analyzer je privileged supply-chain dependency.
- Oprava v main nie je oprava production runtime-u.
- Continuous rescan musí zahŕňať supported releases a deployed digests.

## 25. Časté omyly

### „Pipeline je zelená, scanners sú clean“

Scanner mohol byť skipped, unsupported alebo bez prijatého reportu.

### „Scanli sme release tag“

Tag môže neskôr ukazovať na iný digest alebo neúplný platform inventory.

### „Critical vždy blokuje a medium nikdy“

Risk závisí od reachability, exposure, confidence a compensating controls.

### „Secret sme odstránili z commitu“

Provider credential, history, artifacts a klony môžu zostať.

### „Main je patched, incident je uzavretý“

Starší vulnerable digest môže byť stále podporovaný a nasadený.

## 26. Zhrnutie

Dôveryhodný GitLab security lifecycle je:

```text
explicitný attack-surface model
→ immutable scan subjects
→ expected scanner/report inventory
→ valid complete execution evidence
→ contextual finding a vulnerability decision
→ bounded exception alebo remediation
→ fixed artifact verification
→ deployed-digest correlation
→ continuous rescanning, redeployment a revocation
```

Security scanning nie je počet jobs ani počet findings. Je to schopnosť dokázať coverage, odlíšiť chýbajúcu evidence od čistého výsledku a preniesť nový risk až k release-u a runtime digestu, ktorý skutočne ovplyvňuje používateľov.

## Oficiálna dokumentácia

- [Application security testing](https://docs.gitlab.com/user/application_security/)
- [SAST](https://docs.gitlab.com/user/application_security/sast/)
- [Dependency scanning](https://docs.gitlab.com/user/application_security/dependency_scanning/)
- [Container scanning](https://docs.gitlab.com/user/application_security/container_scanning/)
- [Secret detection](https://docs.gitlab.com/user/application_security/secret_detection/)
- [DAST](https://docs.gitlab.com/user/application_security/dast/)
- [Security policies](https://docs.gitlab.com/user/application_security/policies/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Environments, deployments a releases](environments-deployments-releases.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Infrastructure as Code principles →](../07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md)
<!-- KNOWLEDGE-NAVIGATION:END -->