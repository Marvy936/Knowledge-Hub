# MLOps Supply Chain Integrity

A fraud model is registered from a successful training run and its serving image has a valid signature. The composite release is still not trustworthy: the runtime dependencies are only directly pinned, the base image is referenced by a mutable tag, the builder is persistent and network-unrestricted, provenance was generated outside the trusted platform, the model is stored under a mutable `latest` URI, and admission verifies the signed image without verifying the remote-loaded model or the full release manifest.

The incident is grounded in `MLOPS-PAY-96` and the authoritative `ml-supply-chain-security.md` chapter. Repair `supply_chain_gate.py` so a signed image, green build or HTTP-200 synthetic request cannot substitute for an end-to-end chain of custody.

The repaired gate must bind the exact immutable release manifest; exact source commit, dataset manifest and dependency-lock identity; transitive hash-checked binary-only dependency installation; digest-pinned base image and audited build network; isolated ephemeral trusted builder plus platform-generated signed provenance whose subjects bind the exact model and image; immutable model URI, model attestation, image signer identity, SBOM/image and model-BOM/model binding; composite admission including remote model verification and loaded fingerprint; and a second trusted rebuild/deploy from the same immutable inputs without mutable package indexes, long-lived secrets or manual digest edits.

Supply-chain verification is evidence only and preserves `rollout_authorized=false`, `promotion_authorized=false` and `retraining_authorized=false`. Exact replay must be byte-idempotent, tampered authority/provenance subjects must be rejected, and conflicting durable evidence must never be overwritten.

Use `lab-help`, `status`, `hint`, `verify-chain`, `check`, `assess`, `reset` and `self-test`. This is a shell-only evidence lab; it needs no privileged runtime or external registry.
