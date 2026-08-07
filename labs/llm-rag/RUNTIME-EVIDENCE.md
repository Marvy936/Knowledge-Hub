# Knowledge Hub LLM/RAG runtime evidence

> **Evidence status: Pending**

Tento dokument je authoritative runtime-evidence boundary pre LLM/RAG flagship. Prvý implementovaný block je corpus snapshot a deterministic chunking. `Pending` znamená, že source a tests existujú, ale repository zatiaľ nemá successful authoritative CI/runtime run pre exact implementation revision.

GitHub Actions dispatch je momentálne otvorený repository-level blocker v issue #151. Tento dokument preto nesmie byť interpretovaný ako `Runtime verified`.

## Required corpus evidence

Authoritative run musí zaznamenať:

- exact Git commit SHA,
- include roots,
- corpus snapshot ID,
- file count,
- per-file relative path, byte size a SHA-256 v generated snapshot artefakte,
- successful byte read-back proti exact checkoutu,
- chunk manifest ID,
- chunk count,
- chunking configuration,
- successful deterministic rebuild verification,
- Python/package version,
- cleanup read-back.

## Required forbidden evidence

Run musí odmietnuť alebo odhaliť:

- branch name alebo skrátený SHA namiesto exact commit subjectu,
- changed file bytes po snapshot vytvorení,
- tampered snapshot ID,
- symlinked corpus file,
- chunk content alebo metadata tampering,
- chunk source digest odlišný od snapshotu,
- manifest patriaci inému corpus snapshotu,
- rehashed manifest s vynechaným chunkom,
- output alebo runtime state ponechaný v Git worktree po cleanup-e.

## Proof boundary

Úspešný run tejto vrstvy preukáže iba deterministic corpus a chunking lifecycle. Nepreukáže retrieval, embeddings, reranking, answers, citations, eval quality, prompt-injection defense ani model execution.
