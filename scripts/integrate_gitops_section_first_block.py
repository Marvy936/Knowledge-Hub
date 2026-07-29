from pathlib import Path

ledger_path = Path("DOCUMENTATION-REVIEW-STATUS.md")
text = ledger_path.read_text(encoding="utf-8")

row_marker = "| `16-gitops-and-platform-engineering` — GitOps and Platform Engineering |"
row = (
    "| `16-gitops-and-platform-engineering` — GitOps and Platform Engineering | "
    "4/15 authoritative drafting | In progress | 2026-07-29 | "
    "Sekcia je net-new authoritative doména podľa roadmapy. Prvý blok používa connected Atlas Payments incident `GITOPS-PAY-61`: release `payments 9.0` mal Git commit `9f31c2a`, ale effective production state určovali súčasne Argo CD parameter override, CI direct `kubectl apply`, human live patch, HPA/admission writers a mutable production ref. Git deklaroval image `sha256:pay900a` a route policy generation `1842`, Argo resolve-ol `sha256:pay899hf7`, live Deployment používal `sha256:pay900b` s generation `1841` a running Pods tvorili dva cohorts. System-wide `ignoreDifferences` ignorovalo celý containers subtree, `selfHeal` bolo vypnuté a broad default AppProject/weak tracking/incomplete health oracle umožnili false `Synced/Healthy` verdict. Dôsledkom bolo 18 Podov na `pay900b`, 6 na `pay899hf7`, 3 214 settlements so stale route generation a 96 operations vyžadujúcich provider-ledger reconciliation. `Git ako source of truth` používa `business/platform intent → exact desired-state subject → declarative pinned source → validation/promotion → controller resolution/render → reconcile → effective/business verification → drift/rollback/second-change`; `Pull-based deployment` používa `approved intent → authoritative ref → target-side agent pull → source auth/render/policy → sync → health → continuous re-observation`; `Reconciliation a drift detection` používa `desired generation → observed inventory → normalization/ownership → classified delta → report/ignore/adopt/reconcile/refuse → bounded mutation → second observation`; `Argo CD` používa `Application/AppProject subject → source resolution → repo-server render → controller compare → sync/phases/waves/prune → tracking/health → drift/rollback/second-sync`. Root README aktivoval 17. sekciu, section README je `4/15 · In progress`, roadmap má prvé štyri topics prelinkované, navigation vedie `Idempotency a backpressure → Git source of truth → Pull-based deployment → Reconciliation/drift → Argo CD → ROADMAP`, glossary fragment `16a` a generated `GLOSSARY.md` sú synchronizované a audit-failure artifacts sú prázdne. Zostáva 11 kapitol a finálny section-level pass. |"
)

if row_marker not in text:
    marker = "\n## Section-level completion criteria"
    if marker not in text:
        raise SystemExit("Unable to find ledger insertion marker")
    text = text.replace(marker, f"\n{row}\n{marker}", 1)
    ledger_path.write_text(text, encoding="utf-8")
