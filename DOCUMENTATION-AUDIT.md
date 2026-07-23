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
- Completed manual section audits: Security and Identity, Observability.
- Current manual priority: Cloud and AWS, then continue backward through older sections using heuristic priority and manual review.

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
- `loki.md`
- `elasticsearch-opensearch.md`
- `fluent-bit.md`
- `jaeger-tempo.md`
- `opentelemetry.md`
- `alert-design-alert-fatigue.md`
- `cardinality.md`

All sixteen authoritative Observability articles were manually reviewed. The section already uses connected runtime and data-flow explanations rather than product-only catalogs:

- signal chapters explain metric temporality, log schemas, trace causality, event semantics, instrumentation contracts and context propagation;
- RED, USE and Golden Signals explain measurement boundaries, denominator contracts, retries, hidden queues, saturation and user impact;
- Prometheus connects discovery, relabeling, scraping, WAL/TSDB state, PromQL and rule evaluation;
- Alertmanager separates alert identity, notification state, routing, grouping, inhibition, silences and eventually consistent HA delivery;
- Grafana explains backend query, data frames, transformations, visualization and access boundaries;
- Loki explains streams, labels, structured metadata, chunks, TSDB index, write/read paths, tenancy and LogQL;
- Elasticsearch/OpenSearch explains documents, mappings, Lucene segments, shards, data streams, lifecycle, snapshots and recovery;
- Fluent Bit explains input offsets, parsing, routing, chunks, filesystem buffering, retries, backpressure, duplicates and loss boundaries;
- Jaeger/Tempo explains propagation, sampling, ingestion durability, recent and historical trace paths, object storage and derived metrics;
- OpenTelemetry explains APIs, SDKs, semantic conventions, resources, OTLP, Collector topology, processor ordering and delivery semantics;
- alert design explains actionability, SLO burn, no-data behavior, alert identity, grouping, inhibition, ownership and fatigue reduction.

No Observability article required a wholesale rewrite during this pass. This is an audit result, not an assumption that long text is automatically complete.

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

1. Audit Cloud and AWS from its section order.
2. Rewrite the first article with systemic fragmentation immediately; otherwise record accepted articles without unnecessary edits.
3. Check that cloud service names are tied to request flow, control/data planes, consistency, failure domains, IAM and cost behavior.
4. Continue section by section until all authoritative articles have a manual classification.
