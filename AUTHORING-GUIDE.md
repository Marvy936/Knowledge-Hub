# Authoring guide for learning chapters

Knowledge Hub is a learning system, not a catalog of terms. A chapter is complete only when a reader can explain the mechanism, dependencies, practical use, and likely failure modes—not merely recognize the vocabulary.

## Core rule

A heading followed by one sentence and a list is usually an outline, not an explanation.

Lists are useful for summarizing dimensions, options, signals, steps, or checks. They must not carry the entire conceptual load unless the section is explicitly a reference checklist, source list, control-question set, or glossary.

## Required shape of a conceptual section

A normal conceptual section should contain enough connected prose to answer these questions:

1. **What is it?** Define the concept precisely and distinguish it from adjacent concepts.
2. **What problem does it solve?** Explain why the concept or mechanism exists.
3. **How does it work internally?** Describe the actors, state, data flow, decision flow, lifecycle, or control boundary.
4. **Why do the listed dimensions matter?** Explain unfamiliar terms before or where they first appear.
5. **What does it look like in practice?** Give a concrete example, small scenario, or applied interpretation.
6. **Where does it fail or become a trade-off?** State at least one limitation, dependency, failure mode, or misuse when relevant.

Not every section needs six labeled subsections. Two to five coherent paragraphs can satisfy the model.

## Minimum explanatory depth

For a conceptual heading, use the following baseline:

- at least two explanatory sentences before a multi-item list;
- normally at least one short paragraph describing the mechanism;
- a second paragraph or worked example when the concept introduces several new terms;
- a local reminder even when the authoritative explanation exists in another chapter.

A cross-link does not replace all local explanation. The reader should understand why the referenced concept matters in the current context before leaving the page.

## Introducing terminology

A term should not first appear as an unexplained bullet item.

Prefer one of these patterns:

```text
Workload attestation is the process by which a platform verifies that a
credential is being issued to the intended workload running in an expected
execution context. The verifier evaluates evidence such as node identity,
scheduler metadata, process attributes, or a signed cloud instance document.
```

or:

```text
- workload attestation — verification that the requesting process or Pod is the
  expected workload on an approved node before workload credentials are issued;
- device posture — current security state of a device, such as patch level,
  disk encryption, secure boot, and EDR health.
```

Use the second form when a compact comparison is appropriate. Use prose when the term affects architecture, trust, lifecycle, or failure behavior.

## Explaining lists

Before a list, state what unifies the items and how the system uses them. After the list, explain the consequence.

Weak:

```text
Policy can use:

- device compliance,
- workload attestation,
- resource sensitivity,
- user risk.
```

Better:

```text
A dynamic access decision combines signals about the requester, execution
environment, and protected resource. Each signal changes a different part of
the risk model: device compliance describes endpoint state, workload
attestation proves workload provenance, resource sensitivity determines the
required assurance level, and user risk captures current evidence of account
compromise.

The policy engine consumes these values from trusted sources, checks their
freshness, and then permits, constrains, or denies the requested action.
```

The list may follow as a summary, but the prose establishes meaning and mechanism.

## Examples and failure modes

Examples should expose cause and effect, not merely name a product.

Useful example:

```text
A developer authenticates with phishing-resistant MFA, but the laptop has a
stale EDR agent. The policy allows read-only access to an internal dashboard,
blocks production administration, and requires the device to regain compliant
posture before a privileged session can be created.
```

Useful failure boundary:

```text
If posture data is unavailable, the system must not silently treat the device
as compliant. It needs an explicit failure policy, such as denying privileged
access while allowing a narrowly scoped read-only session.
```

## Reference-style exceptions

The following sections can legitimately be list-heavy:

- control questions;
- source lists;
- troubleshooting checklists after the diagnostic model has been explained;
- command or field references;
- glossary impact;
- status tables;
- concise anti-pattern summaries after the underlying mechanisms are covered.

Even in these sections, unfamiliar terms should link to or briefly recall their authoritative explanation.

## Chapter-level requirements

Each learning chapter should include:

- an opening explanation that places the topic in the broader system;
- a mental model or lifecycle when the topic has multiple actors or states;
- explicit dependencies and trust boundaries;
- practical examples;
- failure modes and troubleshooting reasoning;
- trade-offs rather than one universally “correct” product choice;
- control questions that test understanding, not only recall;
- primary sources;
- glossary impact;
- generated navigation.

## Review questions for authors

Before marking a chapter complete, ask:

- Could a reader explain the mechanism without reading only the bullet lists?
- Are all important terms explained before or at first use?
- Does each long list have a unifying model and a consequence?
- Is there at least one concrete scenario for every major concept cluster?
- Are the failure semantics explicit?
- Does the text explain why a control exists and what it cannot guarantee?
- Are product names presented as implementations of a concept rather than the concept itself?
- Would the chapter support troubleshooting and design decisions at L4/L5?

## Audit remediation workflow

The generated audit is a prioritization system, not a bulk rewrite instruction. Remediation proceeds in controlled passes so that expanding prose does not introduce inaccurate terminology or duplicate explanations across chapters.

1. **Inventory pass** — confirm that every authoritative article listed in a section `README.md` is present in the audit corpus.
2. **Critical pass** — fix empty sections and sections classified as `outline-instead-of-explanation`.
3. **Terminology pass** — explain terms reported as `term-before-explanation` where they first matter.
4. **Mechanism pass** — add actors, state, data flow, decision flow, lifecycle, and trust boundaries.
5. **Example and failure pass** — add concrete cause-and-effect examples, limits, and failure semantics.
6. **Cross-section pass** — remove accidental duplication and link to the earlier authoritative chapter while preserving a short local reminder.
7. **Verification pass** — rerun the audit, read the rendered chapter, validate technical claims against primary sources, and update glossary impact.

Files are remediated in priority order by audit score, but chapters in the same conceptual chain should be reviewed together. For example, OAuth 2.0, OpenID Connect and SAML share federation terminology; editing only one can create inconsistent definitions.

A finding is closed only after human review. Adding filler sentences merely to exceed a word-count threshold is explicitly not acceptable.

## Automated audit

Run:

```bash
python scripts/audit_learning_depth.py
```

This generates:

- `DOCUMENTATION-AUDIT.md` — human-readable review queue;
- `documentation-audit.json` — machine-readable findings.

To include every Markdown file under `docs/`, not only authoritative learning articles:

```bash
python scripts/audit_learning_depth.py --all-docs
```

The audit is heuristic. It intentionally over-reports borderline sections so a human can decide whether the prose is sufficient. Passing the heuristic is not proof of technical correctness or pedagogical quality.
