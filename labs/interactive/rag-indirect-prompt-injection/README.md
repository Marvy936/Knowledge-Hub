# RAG Indirect Prompt Injection and Tool Authorization

This challenge models an agentic RAG application that retrieves external content and can also call a privileged `read_file` tool.

The retrieval itself is legitimate. The bug is the authorization boundary: the starter policy trusts every tool proposal produced after retrieval. A poisoned document can therefore smuggle a `TOOL_REQUEST` into model context and cause a secret file to be read even though the user only asked for a summary.

Work on `/workspace/policy.py`.

Your repaired policy must satisfy this contract:

- retrieved content is evidence, not instruction authority;
- a tool proposal is denied unless it exactly matches an explicit trusted tool request carried by the user/control-plane request;
- the tool must also be listed in `allowed_tools`;
- the exact argument must be listed in `allowed_paths`;
- a normal RAG summary must still return its evidence and citations when a retrieved document contains an injected tool request;
- an explicitly authorized `read_file` request for `/workspace/public/release-status.txt` must still execute successfully;
- do not solve the lab by disabling tools globally or by filtering one known secret path.

The deterministic `model_sim.py` is intentionally capable of proposing a tool call from retrieved text. It is not meant to represent model quality. It exists so the lab can test the application security boundary offline and reproducibly.

Useful inspection commands:

```bash
cat policy.py
cat attack-request.json
cat retrieved.json
query
check
```

The vulnerable starter makes the attack visible through `query`: the retrieved document contains useful incident evidence plus an injected `TOOL_REQUEST`. A secure design preserves the useful evidence while refusing to treat that document as authorization.

Key idea:

```text
trusted user intent / control-plane policy
        |
        v
explicit allowed tool + exact argument
        |
        v
pre-execution authorization gate ---------+
        ^                                  |
        |                                  v
model/tool proposal <--- retrieved data   execute
                         (authority none)
```

Prompt wording such as "ignore retrieved instructions" can be defense in depth, but it is not the authority boundary tested here. The decisive control is deterministic authorization before the sensitive tool executes.

Lab commands: `query`, `status`, `check`, `hint`, `reset`.
