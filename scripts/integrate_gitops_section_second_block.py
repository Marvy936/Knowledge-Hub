from pathlib import Path

ledger_path = Path("DOCUMENTATION-REVIEW-STATUS.md")
text = ledger_path.read_text(encoding="utf-8")
prefix = "| `16-gitops-and-platform-engineering` — GitOps and Platform Engineering |"
replacement = '| `16-gitops-and-platform-engineering` — GitOps and Platform Engineering | 8/15 authoritative drafting | In progress | 2026-07-29 | Druhý authoritative blok rozšíril sekciu o `Flux`, `Application promotion`, `GitOps secrets` a `Internal Developer Platform` a zachoval strict mechanistický model namiesto toolových alebo odrážkových prehľadov. Connected incident `GITOPS-PAY-62` nadviazal na Argo incident release-om `payments 9.1`: staging evidence bola viazaná na `pay910a`, route generation `1850` a credential contract `pv-42`, no image automation medzičasom prepísala shared base na `pay910b`, LaunchPad direct-written `postBuild.substituteFrom` ConfigMap zmenila route na `1849`, promotion PR sa rebase-la bez final-render/evidence revalidation a shared SOPS age identity nemala environment boundary. Flux následne korektne reconcile-ol configured artifact, ale effective production bežala na `pay910b/1849`, workload mal stále environment snapshot `pv-42` a provider už akceptoval iba `pv-43`. Dôsledkom bolo 2 746 settlements cez stale route, 61 provider authentication failures, 14 unknown outcomes a portal false-success 17 minút pred potvrdeným incidentom. `Flux` používa `approved intent → source resolution/artifact → decryption/substitution/build → SSA apply alebo Helm action → inventory/prune/health → effective/business verification → second reconcile`; `Application promotion` používa `immutable candidate → subject-bound evidence → fresh proposal/approval → target-base CAS a final render → authoritative environment transition → reconciliation → business acceptance`; `GitOps secrets` používa `secret authority → encrypted/reference desired state → decrypt/fetch → materialization → workload load/reload → overlap rotation → revocation/second rotation`; `Internal Developer Platform` používa `capability need → exact request/contract → durable idempotent operation → bounded orchestration → effective capability → developer/operational/business verification → lifecycle closure`. Redesign používa immutable release manifest, environment-specific Flux coordinates, no critical cluster-local substitutions, scoped apply a KMS identities, generation-bound evidence, final-merge revalidation, secret consumer-convergence telemetry a durable LaunchPad operation. Section README je `8/15 · In progress`, roadmap a navigation chain zahŕňajú `Argo CD → Flux → Application promotion → GitOps secrets → Internal Developer Platform → ROADMAP`, glossary fragment `16b` dopĺňa `16a` a generated artifacts sa synchronizujú repository-native workflowom. Zostáva sedem kapitol od Platform as a Product po Multi-tenancy a finálny section-level consistency pass. |'

lines = text.splitlines()
matches = [index for index, line in enumerate(lines) if line.startswith(prefix)]
if len(matches) != 1:
    raise SystemExit(f"Expected exactly one GitOps ledger row, found {len(matches)}")

index = matches[0]
if "| 4/15 authoritative drafting |" not in lines[index] and "| 8/15 authoritative drafting |" not in lines[index]:
    raise SystemExit("GitOps ledger row has an unexpected completion state")

lines[index] = replacement
ledger_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
