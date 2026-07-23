# Authoring guide for learning chapters

Knowledge Hub is a learning system, not a catalog of terms. A chapter is complete only when a reader can explain the mechanism, dependencies, practical use, and likely failure modes—not merely recognize the vocabulary.

## Core rule

A heading followed by one sentence and a list is usually an outline, not an explanation. A single sentence is not considered sufficient explanatory content for a normal conceptual section, even when no list follows it.

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

- at least two connected explanatory sentences, whether or not a list follows;
- at least two explanatory sentences before a multi-item list;
- normally at least one short paragraph describing the mechanism;
- a second paragraph or worked example when the concept introduces several new terms;
- a local reminder even when the authoritative explanation exists in another chapter.

The minimum is not a writing target. Two filler sentences do not make a section educational. The prose must explain meaning, mechanism, consequence, or boundary rather than restating the heading in different words.

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

## Bullet-level explanation contract

A meaningful bullet must be understandable inside the current section without forcing the reader to guess why the item was listed. A bare noun, acronym, product name, signal name, service name, flag, or short phrase is not sufficient when the item introduces knowledge.

Each conceptual bullet must use at least one of these forms:

- `term — explanation` — define the item and state its role in this mechanism;
- `condition: consequence` — explain what the condition changes or causes;
- a complete explanatory sentence — state what happens, why it matters, or where it fails;
- a compact example whose meaning has already been explicitly established in the preceding prose.

Weak:

```text
Relevant signals:

- queue depth,
- worker concurrency,
- oldest message age,
- retry count.
```

Better:

```text
Relevant signals describe different parts of the queue lifecycle. Queue depth
shows the amount of pending work, while oldest message age reveals how long the
worst waiting item has already violated freshness expectations.

- queue depth — number of items waiting or currently eligible for processing;
- worker concurrency — number of consumers that can make progress in parallel;
- oldest message age — end-to-end waiting time of the oldest unprocessed item;
- retry count — evidence that work is being repeated and may be amplifying load.

Together these signals distinguish insufficient capacity from a poison message,
a stalled dependency, or a retry storm.
```

Do not rely on a generic introductory sentence such as “The following items are important.” It must explain the relationship between the items. After the list, state how the items combine, which one is authoritative, how they affect a decision, or what failure becomes visible through them.

Short literal inventories can remain concise only when they are genuinely reference data, such as allowed enum values, command flags, source links, status fields, or control questions. Even then, any unfamiliar item needs a local definition or an immediately adjacent table column explaining its meaning.

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

- Does every normal conceptual section contain more than one substantive explanatory sentence?
- Could a reader explain the mechanism without reading only the bullet lists?
- Does every meaningful bullet explain what the item means and why it belongs in this context?
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
2. **Critical pass** — fix empty sections, single-sentence conceptual sections, bare bullet lists, and sections classified as `outline-instead-of-explanation`.
3. **Terminology pass** — explain terms reported as `term-before-explanation` where they first matter.
4. **Bullet semantics pass** — replace bare names with `term — explanation`, full sentences, or explicit prose that explains every listed item in the current context.
5. **Mechanism pass** — add actors, state, data flow, decision flow, lifecycle, and trust boundaries.
6. **Example and failure pass** — add concrete cause-and-effect examples, limits, and failure semantics.
7. **Cross-section pass** — remove accidental duplication and link to the earlier authoritative chapter while preserving a short local reminder.
8. **Verification pass** — rerun the audit, read the rendered chapter, validate technical claims against primary sources, and update glossary impact.

Files are remediated in priority order by audit score, but chapters in the same conceptual chain should be reviewed together. For example, OAuth 2.0, OpenID Connect and SAML share federation terminology; editing only one can create inconsistent definitions.

A finding is closed only after human review. Adding filler sentences or mechanically appending the same generic explanation to every bullet is explicitly not acceptable.

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
