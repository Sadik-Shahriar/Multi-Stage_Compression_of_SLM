# Next Session Prompt

Continue the CSE407 SLM energy-ablation project from completed Track A stages
A0-A3. Read these files first:

- `AGENTS.md`
- `previous session context/fail-safe-completion-plan.md`
- `previous session context/current-research-context-and-findings.md`
- `research/experiment_registry.json`
- `research/frozen_hard_retrieval_v4.json`
- `research/llama_v5_artifact_manifest.json`
- `research/llama_track_a_full_v1_artifact_manifest.json`
- `research/llama_power_robustness_v1_artifact_manifest.json`
- `experiments/track_a_failsafe_colab/README.md`
- `experiments/track_a_failsafe_colab/05_llama_full_quality_control_v1.ipynb`
- `experiments/track_a_failsafe_colab/06_llama_power_robustness_analysis.ipynb`

Do not use archived Qwen3/Qwen2.5-1.5B notebooks as current implementations.

## Completed State

- Historical Llama v5 evidence is immutable and registered:
  fingerprint `8d27af8c9ee94de3`, 380 execution rows, 95 traces, and 114
  scientific Drive artifacts.
- The frozen Llama hard-quality/control run is immutable and registered:
  fingerprint `106a561c07c62937`, 300 quality rows, five C1-W energy rows,
  exact declared C1-S/C1-W parity, and all final integrity gates passed.
- Frozen semantic hash:
  `fffa82607af6e7d2c892d18d5bc790524570833472ad397b7ab2e54eb03005ef`.
- Frozen Llama prompt-set hash:
  `4e1ced4fd4829629929a346879cc00c45476f38fa0936137909b8779242321e8`.
- Hard retrieval was 78.3% for C0, 63.3% for C1-W, and 61.7% for C2,
  C3-Ref, and C4-Ref. Each compression path had zero gains and one loss versus
  C1-W; do not claim strict 5-point non-inferiority.
- A3 power robustness is immutable accepted derived evidence under fingerprint
  `91ebc63773e735e6`. All 100 traces verified and reintegrated.
- Raw telemetry contained 1501/82/21 samples above 70/82/100 W and a maximum of
  124.496 W. Raw joules remain primary.
- Core and sensitivity energy rankings and all registered significance decisions
  were unchanged under both 82 W and 70 W clipping.
- Historical C1 versus Notebook 5 C1-W is descriptive only because both session
  and prompt/workload differ; it is not an isolated wrapper-overhead estimate.

Never write into or modify:

- `CSE407_llama_v5_final/`
- `CSE407_llama_track_a_full_v1/`
- `CSE407_llama_power_robustness_v1/`
- Any V1-V4 discarded pilot directory

## Mandatory Delivery Rule

All new experiment implementations must be self-contained Google Colab `.ipynb`
notebooks with clear Markdown cells, numbered run order, validation gates,
resumability where measurements are written, and isolated Drive paths. Do not
create standalone `.py` experiment runners. Keep Track A notebooks under
`experiments/track_a_failsafe_colab/`.

## Immediate Task

Create the next numbered self-contained Colab notebook:

`experiments/track_a_failsafe_colab/07_qwen2_5_adapter_parity_pilot_v1.ipynb`

This is an adapter/parity pilot only. Build and statically validate it, but do
not fabricate outputs, mark it executed, or launch the full Qwen energy/quality
matrix.

## Required Notebook Scope

1. Pin exact immutable revisions for the official checkpoints:
   - FP16: `Qwen/Qwen2.5-3B-Instruct`
   - AWQ: `Qwen/Qwen2.5-3B-Instruct-AWQ`
   Verify the repositories and revisions rather than assuming model metadata.
2. Keep the comparable reference stack pinned, including
   `transformers==5.12.1` and `turboquant==0.2.0`, unless source inspection proves
   a blocking incompatibility. Record package versions and source hashes.
3. Inspect the exact pinned Qwen2.5 architecture and Transformers attention
   source before implementing the adapter. Validate expected values rather than
   silently assuming them; expected Qwen2.5-3B geometry is approximately 36
   layers, 16 query heads, two KV heads, and head dimension 128.
4. Implement a Qwen-specific attention wrapper targeting the actual pinned
   `Qwen2Attention` API. Preserve Qwen RoPE behavior, cache positions, attention
   masks, GQA head mapping, and absolute decode positions.
5. Preserve full 4096-token prefill attention before storing either full or
   selected K/V. For Q4-Ref, perform custom pyramidal eviction first and pass
   only retained K/V into TQ-Ref.
6. Use these labels consistently:
   - Q0: FP16 baseline
   - Q1-S: stock AWQ parity control
   - Q1-W: matched-wrapper AWQ baseline
   - Q2: AWQ + custom pyramidal eviction
   - Q3-Ref: AWQ + `turboquant==0.2.0` numerical reference path
   - Q4-Ref: sequential eviction then TQ-Ref
   Never call TQ-Ref packed, fused, or physically 4-bit.
7. Regenerate the exact 60 frozen V4 semantic scenarios and assert semantic hash
   `fffa82607af6e7d2c892d18d5bc790524570833472ad397b7ab2e54eb03005ef`.
   Tokenize independently with the pinned Qwen tokenizer to exactly 4096 tokens,
   retain 32 records and 20 scenarios per 10%/50%/90% depth, enforce the complete
   query within the final 32 tokens, and create a new Qwen prompt-set hash.
   Do not alter scenario facts or tune prompts for Qwen outcomes.
8. Use a new schema, fingerprint, CSV/JSON names, and isolated pilot directory,
   such as `CSE407_qwen_track_a_adapter_pilot_v1/`. Register the Qwen tokenizer
   hash, prompt-set hash, model revisions, architecture, backend, and protocol.
9. Add predeclared Q1-S versus Q1-W parity gates on one fixed prompt per depth:
   final-position logits with fixed tolerances, top-1 agreement, exact greedy
   token IDs and responses, full layer-by-layer cache lengths, and absence of
   eviction/TQ state. Do not widen tolerances after seeing results.
10. Add one-token active-cache probes for Q1-W, Q2, Q3-Ref, and Q4-Ref. Validate:
    - all layer cache lengths before and after decode;
    - full prefill attention length;
    - exact pyramidal budgets and eviction-first ordering;
    - TQ indices, norms, residuals, materialized K/V, numerical bounds, and active
      returned-cache use;
    - alias-deduplicated live storage;
    - Q4-Ref layers below the 128-token residual threshold without falsely
      requiring quantized indices.
11. Prove that Q2/Q3-Ref/Q4-Ref prefill logits agree with Q1-W within the
    predeclared tolerance, because compression must affect only cache-backed
    continuation, not full-prompt prefill output.
12. Save a machine-readable validation JSON and Qwen prompt manifest atomically.
    The pilot passes only if architecture, prompt, parity, cache, active-use,
    eviction, and TQ-Ref gates all pass. No energy rows are required in this pilot.
13. Fail closed on any model revision, source signature, architecture, prompt
    hash, parity, position, cache, or storage mismatch. A documented blocker is
    preferable to silently adapting the protocol.
14. Add a clear next gate: the full Qwen matrix may be built only after this
    pilot executes successfully on a Colab T4 and its artifacts are reviewed.

## Before Editing

- Inspect the validated Llama wrapper and gates in Notebook 5, but port only the
  minimal reusable logic; do not assume Llama and Qwen attention signatures are
  interchangeable.
- Verify current Hugging Face model revisions and the exact Transformers 5.12.1
  Qwen2 source/API.
- Update `research/experiment_registry.json` and active handoff Markdown only
  after the new source notebook passes JSON, nbformat, embedded-Python syntax,
  fingerprint, no-output, and forbidden-write safety checks.
- Keep Notebook 07 unexecuted with empty outputs and null execution counts.
