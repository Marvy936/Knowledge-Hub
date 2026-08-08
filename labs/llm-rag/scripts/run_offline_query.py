from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from knowledge_hub_rag.contracts import ContractError, atomic_write_json, read_json
from knowledge_hub_rag.offline_adapter import run_offline_adapter
from knowledge_hub_rag.retrieval import build_grounded_context, retrieve
from knowledge_hub_rag.runtime_config import build_runtime_config
from knowledge_hub_rag.tracing import build_trace


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one deterministic offline RAG query with security and trace evidence."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--generation", required=True)
    parser.add_argument("--implementation-revision", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--min-score", type=float, default=0.01)
    parser.add_argument("--context-max-chars", type=int, default=6000)
    parser.add_argument("--answer-max-chars", type=int, default=700)
    parser.add_argument("--config-output", type=Path, required=True)
    parser.add_argument("--retrieval-output", type=Path, required=True)
    parser.add_argument("--context-output", type=Path, required=True)
    parser.add_argument("--adapter-output", type=Path, required=True)
    parser.add_argument("--trace-output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        manifest = read_json(args.manifest)
        index = read_json(args.index)
        config = build_runtime_config(
            generation=args.generation,
            implementation_revision=args.implementation_revision,
            top_k=args.top_k,
            min_score=args.min_score,
            context_max_chars=args.context_max_chars,
            answer_max_chars=args.answer_max_chars,
        )
        started = time.perf_counter()
        retrieval = retrieve(
            index=index,
            manifest=manifest,
            query=args.query,
            top_k=config["retrieval"]["top_k"],
            min_score=config["retrieval"]["min_score"],
        )
        context = build_grounded_context(
            retrieval,
            index=index,
            manifest=manifest,
            max_chars=config["context"]["max_chars"],
        )
        adapter = run_offline_adapter(
            retrieval_result=retrieval,
            index=index,
            manifest=manifest,
            runtime_config=config,
        )
        latency_ms = (time.perf_counter() - started) * 1000.0
        trace = build_trace(
            runtime_config=config,
            retrieval_result=retrieval,
            adapter_result=adapter,
            context=context,
            index=index,
            manifest=manifest,
            latency_ms=latency_ms,
        )
        atomic_write_json(args.config_output, config)
        atomic_write_json(args.retrieval_output, retrieval)
        atomic_write_json(args.context_output, context)
        atomic_write_json(args.adapter_output, adapter)
        atomic_write_json(args.trace_output, trace)
    except ContractError as exc:
        print(
            json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True),
            file=sys.stderr,
        )
        return 2

    print(
        json.dumps(
            {
                "status": adapter["answer"]["status"],
                "abstention_reason": adapter["answer"]["abstention_reason"],
                "runtime_config_id": config["runtime_config_id"],
                "implementation_revision": config["implementation_revision"],
                "retrieval_result_id": retrieval["retrieval_result_id"],
                "answer_id": adapter["answer"]["answer_id"],
                "trace_id": trace["trace_id"],
                "latency_ms": trace["latency_ms"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
