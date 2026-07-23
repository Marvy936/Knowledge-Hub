# Documentation learning-depth audit

This file tracks the manual pedagogical audit while `scripts/audit_learning_depth.py` provides heuristic repository-wide findings. A heuristic result is a review queue, not proof that an article is technically or pedagogically complete.

## Audit objective

Every authoritative learning article should explain concepts as connected mechanisms rather than as headings followed by one sentence and a list. Review checks whether a reader can answer:

1. What is the concept and what adjacent concept is it not?
2. Why does it exist?
3. How does it work internally?
4. What do newly introduced terms mean?
5. What does the mechanism look like in practice?
6. Where does it fail or create a trade-off?
7. How is it diagnosed and verified?

## Corpus

- Authoritative learning articles: 257 at audit start.
- Sections: 14 at audit start.
- Current manual priority: complete Observability, then continue backward through older sections using heuristic priority and manual review.

## Security and Identity manual audit

### Rewritten to explanatory depth

- `authentication-authorization-auditing.md`
- `least-privilege.md`
- `iam-rbac.md`
- `active-directory.md`
- `ldap.md`
- `kerberos.md`
- `oauth-2.md`
- `openid-connect.md`
- `saml.md`
- `secrets-management.md`
- `encryption-at-rest-and-in-transit.md`
- `vulnerability-and-patch-management.md`
- `threat-modeling.md`
- `supply-chain-security.md`
- `sbom.md`
- `image-signing.md`
- `policy-as-code.md`
- `zero-trust.md`

These rewrites preserve the original technical scope but group fragmented definitions into larger lifecycle, trust-boundary, decision-flow and failure-analysis sections. New terms are explained at first use and long lists are preceded by a model and followed by consequences.

### Manually reviewed and accepted

- `cia-triad.md`

The CIA chapter already contains connected prose, control trade-offs, lifecycle analysis, concrete Kubernetes/CI/CD/observability examples, validation methods and incident reasoning. It does not require a wholesale rewrite. Future maintenance may still improve isolated list-heavy subsections, but the chapter is not an outline-only article.

### Remaining Security and Identity review

The section index and all remaining articles must still be checked for local regressions, terminology introduced before explanation, broken cross-links and consistency with the rewritten foundation articles. Completion of the section-level rewrite does not mean the full 257-article corpus audit is complete.

## Observability manual audit

### Manually reviewed and accepted

- `monitoring-vs-observability.md`
- `metrics-logs-traces-events.md`
- `instrumentation-telemetry.md`
- `red-method.md`
- `use-method.md`
- `golden-signals.md`
- `prometheus.md`
- `alertmanager.md`
- `grafana.md`
- `cardinality.md`

The conceptual articles explain telemetry data models, metric temporality, structured logging, trace causality and sampling, instrumentation contracts, RED numerator/denominator semantics, USE resource and hidden-queue analysis, Golden Signals measurement boundaries and cardinality cost/churn.

The Prometheus, Alertmanager and Grafana articles also meet the standard. Prometheus connects discovery, relabeling, scrape validation, series identity, WAL/TSDB state, PromQL and rule evaluation. Alertmanager separates alert state from notification state and explains fingerprinting, route evaluation, grouping, timing, inhibition, silences and eventually consistent HA notification delivery. Grafana explains the path from backend query through data frames, transformations and fields to panels, alerting and access boundaries, including why dashboard visibility is not data-source authorization.

### Remaining Observability review

- `loki.md`
- `elasticsearch-opensearch.md`
- `fluent-bit.md`
- `jaeger-tempo.md`
- `opentelemetry.md`
- `alert-design-alert-fatigue.md`

The next review must verify that logging, tracing and alerting component lists are tied to ingestion/query lifecycles, state ownership, failure behavior and troubleshooting rather than presented as product catalogs.

## Review classifications

- **Rewrite required** — outline-like structure, unexplained terminology or missing mechanism/failure model across a substantial part of the article.
- **Targeted expansion** — core explanation is sound, but specific sections need local prose, examples or failure semantics.
- **Accepted** — article already explains the mechanism sufficiently; only normal maintenance remains.
- **Reference exception** — list-heavy content is intentional, such as a glossary, command reference, source list or checklist after the mechanism has been explained.

## Automation status

The authoritative documentation workflow runs on:

```yaml
runs-on: [self-hosted, Linux, X64]
```

It synchronizes glossary and navigation and invokes `scripts/audit_learning_depth.py --all-docs`. The generated report must remain advisory until manual review confirms the findings. An empty or failed generated report must not be interpreted as a clean corpus.

## Next audit block

1. Audit Loki, Elasticsearch/OpenSearch and Fluent Bit as one logging pipeline block.
2. Audit Jaeger/Tempo and OpenTelemetry as one tracing and telemetry-platform block.
3. Audit alert design and close the Observability section.
4. Continue to the preceding section using the same selective rewrite policy.
