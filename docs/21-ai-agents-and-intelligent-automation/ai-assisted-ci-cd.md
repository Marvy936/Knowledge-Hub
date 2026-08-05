# AI-assisted CI/CD

AI-assisted CI/CD môže skrátiť authoring, failure analysis a remediation, ale zároveň pridáva probabilistický komponent do cesty, ktorá drží source, credentials, artifacts a production authority. Bez deterministic gates môže model vytvoriť zelenú pipeline tým, že odstráni dôkaz namiesto odstránenia chyby.

Incident `AGENT-AUTO-14` zahŕňal AI patch, ktorý na základe incomplete logu označil test za flaky a zmenil workflow condition tak, že required regression path nebežal. Redelivered event spustil druhý build, broad OIDC trust umožnil deployment a mutable tag oddelil reviewed source od nasadeného artifactu.

Nosný lifecycle je:

```text
change alebo pipeline failure
→ exact repository, ref a workflow generation
→ bounded AI context a proposal
→ schema, policy, permissions a test-integrity gates
→ human alebo protected-branch decision
→ immutable build a provenance
→ bounded deployment identity a environment approval
→ live resource a business verification
→ rollback, audit a eval feedback
```

## 1. AI role v delivery lifecycle

AI môže vysvetľovať pipeline, generovať YAML, navrhovať tests, klasifikovať failure, pripraviť patch, sumarizovať release a odporučiť rollback. Každá rola má iný impact a musí mať samostatný tool allowlist a approval.

Read-only explanation nie je to isté ako branch write, workflow edit, secret access alebo production deployment. Capability sa udeľuje podľa najhoršieho možného side effectu, nie podľa názvu agenta.

## 2. Exact change subject

Každý agent run viaže repository, base SHA, head SHA, workflow path, event, actor, model/prompt generation, tools a runner image. Bez exact subjectu sa finding alebo patch môže aplikovať na posunutý branch.

Pred merge a deploymentom sa znovu overí, že reviewed digest zodpovedá current head. Stale approval sa invaliduje.

## 3. Untrusted repository content

Source code, issue, PR description, test output, build log a artifact metadata sú untrusted model input. Útočník môže vložiť text, ktorý sa tvári ako system instruction alebo žiada secret exfiltration.

Prompt boundary označí source a zakáže, aby repository text menil tool policy. Model nemá raw secret values a output sa validuje mimo modelu.

## 4. Pipeline generation

AI-generated workflow je proposal. Prejde syntax parserom, schema validation, policy checks, changed-path analysis, permissions review, action pinning a dry-run alebo sandbox execution.

Generátor nesmie potichu odstrániť required job, `if` guard, environment alebo artifact verification. Diff sa porovná s intentom a protected invariants.

## 5. Test generation

AI môže vytvoriť unit, integration, property alebo regression tests, no test validity sa hodnotí podľa independent oracle. Test, ktorý iba reprodukuje aktuálnu implementáciu, nemusí chrániť business requirement.

Agent nesmie meniť production code a test oracle v jednom neoddelenom kroku bez review. Mutation testing alebo known-bad fixture overí, že nový test skutočne zlyhá pri regresii.

## 6. Failure analysis

AI failure analyzer sumarizuje logs, recent changes a known patterns a navrhuje competing hypotheses. Root cause nevzniká iba z najpravdepodobnejšieho textu.

Analyzer uvádza missing logs, truncation, flaky history a environment differences. Fix recommendation musí mať discriminating test.

## 7. Automated remediation

Remediation agent pracuje na novej branchi, vytvorí minimal diff a spustí independent checks. Nemá obísť branch protection ani sám schváliť vlastný patch.

High-impact changes v auth, billing, infrastructure, policy alebo workflow permissions vyžadujú domain ownera. Auto-merge je povolený iba pre presne klasifikované low-risk changes s proven controls.

## 8. Required checks integrity

Green CI je meaningful iba ak expected jobs bežali na exact SHA a neboli skipped, neutral alebo nahradené slabším jobom. Gate kontroluje check identity a provenance, nie iba názov.

AI patch, ktorý zmení workflow paths alebo condition, môže odstrániť vlastný verifier. Meta-policy preto chráni CI definitions a required workflow references.

## 9. GitHub token permissions

`GITHUB_TOKEN` a ďalšie job permissions sa nastavujú explicitne na minimum. Read job nepotrebuje `contents: write`; build job nepotrebuje deployment cloud role.

AI nesmie rozširovať permissions iba preto, aby fix prešiel. Permission diff je security-sensitive artifact a vyžaduje dedicated review.

## 10. OIDC deployment identity

GitHub Actions môže cez OIDC získať short-lived cloud credential bez long-lived secretu. Cloud trust policy však musí viazať repository alebo immutable IDs, environment, branch alebo reusable workflow a audience.

`id-token: write` iba umožní vyžiadať token; skutočnú authority určuje provider trust. Broad subject condition môže dať deployment capability nečakanému workflowu.

## 11. Environments a approval

Production job sa viaže na protected environment s branch/tag restrictions, required reviewers alebo custom deployment protection. Environment name je súčasť execution subjectu a OIDC contextu.

AI recommendation môže pripraviť deployment, ale approval viaže exact artifact digest a manifest. Approver nevidí iba modelové summary.

## 12. Reusable workflows

Central reusable workflow štandardizuje build, attest, scan a deployment. Caller odovzdáva typed inputs a secrets podľa explicitného contractu.

Reference sa pinne na trusted tag alebo SHA podľa governance. AI-generated caller nesmie obísť reusable workflow vlastnou inline implementáciou.

## 13. Third-party actions

Action je executable dependency. Version tag môže byť mutable, preto high-trust workflows pinujú immutable commit SHA a používajú dependency update process.

AI návrh novej action prejde source, publisher, permissions, network a supply-chain review. Marketplace popularity nie je trust proof.

## 14. Runner isolation

Untrusted PR code sa nesmie spúšťať na persistent self-hosted runner s production network alebo secrets. Ephemeral runner, network segmentation, clean workspace a artifact boundaries obmedzia persistence.

AI agent runtime je tiež workload. Jeho cache, tool credentials, MCP connectors a workspace sa resetujú a auditujú medzi tenants a repositories.

## 15. Privileged workflow events

Privileged workflow event, ktorý beží v base repository context-e, nesmie checkoutnúť a executeovať untrusted PR head so secrets. AI nemá generovať taký pattern ako convenience fix.

Bezpečný design oddeľuje metadata/comment job od untrusted build jobu a používa explicitný artifact handoff. Event choice je security decision.

## 16. Artifact identity

Build output sa viaže na source SHA, workflow, runner, dependencies a digest. Tag alebo filename nestačí.

Deployment spotrebuje exact digest a overí provenance. AI nesmie nahradiť missing digest latest tagom.

## 17. Artifact attestations

GitHub artifact attestations vytvárajú signed provenance claims viazané na workflow a OIDC identity. Verification môže byť admission alebo deployment gate.

Attestation dokazuje build provenance podľa policy, nie functional correctness ani absence vulnerability. Stále sú potrebné tests, scans a business verification.

## 18. SBOM a dependency evidence

Build môže vytvoriť SBOM a dependency lock evidence. AI používa tieto artifacts pri impact analysis, ale nesmie halucinovať package reachability.

Dependency update agent viaže advisory, package version, transitive path, tests a artifact digest. Emergency upgrade má rollback a compatibility plan.

## 19. Secrets

Model input a logs nesmú obsahovať raw secrets. CI masking nie je dokonalá ochrana proti transformed alebo chunked exfiltration.

Agent dostáva opaque credential handle alebo tool, ktorý vykoná bounded operation. Secret access a provider call sa auditujú oddelene.

## 20. Log a artifact poisoning

Build output môže obsahovať ANSI control sequences, fake annotations alebo prompt injection. Parser a model prompt zachovajú source boundaries a limitujú content.

Agent nesmie vykonať shell command skopírovaný z logu bez allowlistu a human review. External URL z failure message sa nefetchuje automaticky privilegovaným runnerom.

## 21. Model a prompt generation

AI output sa viaže na model, provider, region, prompt template, policy version, tool schemas a decoding settings. Rovnaký natural-language request nemusí vytvoriť rovnaký patch.

Reproducibility preto znamená zachovať inputs a evidence, nie garantovať byte-identical generáciu. Deterministic gates rozhodujú o acceptance.

## 22. Evaluation

Offline eval obsahuje real failure classes, malicious logs, permission escalation, skipped-test návrhy a false root causes. Metriky zahŕňajú valid patch rate, unsafe suggestion rate, test preservation, time-to-fix a human rejection reasons.

Eval generation musí zodpovedať production agent generation. Prompt alebo model update bez regression gate je release.

## 23. Confidence a abstention

Confidence sa kalibruje na konkrétnu task class. Agent sa musí vedieť zdržať fixu pri neúplných logs, missing reproduction alebo security-sensitive change.

Low confidence neznamená automaticky safe read-only action, ak action môže exfiltrovať data. Tool policy je nezávislá od confidence.

## 24. Cost a latency

AI analysis môže predĺžiť feedback loop a spotrebovať token budget. Pipeline stanoví timeout, max artifacts, sampling a fallback na human triage.

Cost saving nesmie odstrániť required test alebo provenance. Budget exhaustion vytvorí explicitný `analysis_unavailable`, nie green result.

## 25. Incident AGENT-AUTO-14

AI analyzer označil integration test za flaky podľa orezaného logu a patch zmenil condition tak, že job pri release branchi nebežal. Pipeline zostala zelená a deployment použil OIDC trust viazaný iba na repository bez environment alebo reusable-workflow restriction.

Redelivered event spustil druhý build a mutable image tag ukazoval na iný artifact. Observability agent neskôr videl pokles errorov, pretože test aj telemetry path boli odstránené. Delivery evidence nebola business proof.

## 26. Competing hypotheses

CI failure môže pochádzať z code regression, flaky testu, runner image, dependency outage, secret expiry, quota, network, cache poisoning alebo workflow change. AI uvádza každú hypothesis a discriminating evidence.

Green build po patchi môže znamenať opravu, ale aj skipped path, weakened assertion alebo missing data. Independent verifier kontroluje execution graph.

## 27. Containment

Pri podozrení na unsafe AI change sa zastaví merge alebo deployment, revoke-ne cloud session, pinne artifact digest a zachová logs, agent transcript a workflow generations. Branch sa neprepíše force pushom.

Ak už prebehol deployment, traffic alebo mutation sa obmedzí a provider state sa reconciliuje. Revert commit bez business read-backu nestačí.

## 28. Recovery

Recovery obnoví required checks a permissions z authoritative template, znovu spustí tests na exact source a oddelí artifact build od deploymentu. Compromised runner alebo credential sa rotuje.

AI patch sa označí superseded, rejection reason sa pridá do eval datasetu a policy sa upraví na general control, nie iba konkrétny prompt string.

## 29. Positive acceptance

Agent analyzuje failure, navrhne minimal patch, zachová failing regression test a independent CI prejde na exact SHA. Artifact má digest, provenance a environment approval.

Deployment použije bounded OIDC identity a business canary potvrdí outcome. Druhý test vloží malicious log a agent sa zdrží privileged action.

## 30. Forbidden acceptance

Agent nesmie meniť required checks, permissions, environment alebo artifact reference bez explicitného security review. Untrusted PR nesmie získať production secret alebo persistent runner.

Green conclusion pri skipped verifieri, missing AI analysis alebo mutable tagu je blocked. Očakáva sa nulový unauthorized deployment.

## 31. Recovery acceptance

Po agent-authored regression sa revertne exact patch, rebuildne trusted artifact a reconciliuje deployment aj business effects. Audit zachová pôvodný agent run.

Alternate test rotuje OIDC trust alebo reusable workflow generation a overí fail-closed behavior. Druhý repository scope nesmie získať credential.

## 32. Practical AI delivery envelope

AI delivery envelope je evidence record medzi repository subjectom, agent generation, tool authority, deterministic gates a artifact outcome. Zabraňuje tomu, aby agent comment, green check a deployment boli interpretované ako jeden status.

Príklad ponecháva `deployed` a `business_verified` false. CI acceptance je iba jedna vrstva a agent nemá deployment tool ani OIDC authority.

```yaml
ai_delivery_run:
  id: AICD-2026-00842
  repository: "Marvy936/service"
  event: pull_request
  base_sha: "aa11..."
  head_sha: "bb22..."
  workflow_sha: "cc33..."
  agent:
    role: failure-analysis-and-patch-proposal
    model_generation: "provider/model@2026-08"
    prompt_digest: "sha256:44dd..."
    tools:
      - read-repository
      - read-ci-logs
      - create-proposal-branch
    prohibited:
      - change-required-checks
      - request-oidc-token
      - deploy
  gates:
    - workflow-policy
    - permission-diff-review
    - regression-test-integrity
    - independent-ci
    - artifact-attestation
    - production-environment-approval
  artifact:
    digest: "sha256:ee55..."
    source_sha: "bb22..."
  outcome:
    ci_verified: true
    deployed: false
    business_verified: false
```

## 33. Primary sources

Harness AI DevOps Agent pipeline creation, error analysis, policy generation a resource operations sú popísané na https://developer.harness.io/3k-docs/ai/devops-agent/. CI failure analysis je na https://developer.harness.io/docs/continuous-integration/troubleshoot-ci/ai/ a repository AI agents na https://developer.harness.io/docs/code-repository/pull-requests/ai-agents/. Tieto features generujú alebo odporúčajú zmeny; merge a production correctness zostávajú mimo modelovej authority.

GitHub Actions security guidance je na https://docs.github.com/en/actions/how-tos/secure-your-work a OIDC trust semantics na https://docs.github.com/en/actions/reference/security/oidc. OIDC odstraňuje potrebu long-lived cloud secretu, ale provider trust conditions na repository, environment, branch alebo reusable workflow určujú skutočnú authority.

Artifact attestation provenance a verification dokumentuje https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations a artifact concepts https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts. Attestation podporuje source-to-build provenance; nepreukazuje functional alebo business correctness.

## Zhrnutie

AI v CI/CD má zostať proposal, analysis alebo bounded implementation worker v deterministic delivery shelli. Exact SHA, permissions, test integrity, runner isolation, OIDC trust, artifact provenance, environment approval a business canary musia rozhodovať nezávisle od modelového presvedčenia.

Ďalšia kapitola rozoberie AI-assisted observability a incident response, kde model koreluje telemetry a change events, ale nesmie meniť no-data alebo confidence na potvrdenú root cause a recovery.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Event-driven automation](event-driven-automation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: AI-assisted observability a incident response →](ai-assisted-observability-incident-response.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
