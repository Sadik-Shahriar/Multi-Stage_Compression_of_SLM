# Reconstruction Plan: Method-Faithful Qwen3 AWQ + PyramidKV + TurboQuant Ablation

## 1. Purpose And Non-Negotiable Standard

Rebuild `experiments/qwen3_energy_ablation_colab.ipynb` so it can make valid claims about the following five configurations on an NVIDIA T4:

| ID | Weights | Token eviction | KV-cache quantization | Required label |
|---|---|---|---|---|
| C0 | Qwen3-4B FP16 | Full KV cache | FP16 | `FP16 + FullKV` |
| C1 | Qwen3-4B-AWQ | Full KV cache | FP16 | `AWQ + FullKV` |
| C2 | Qwen3-4B-AWQ | Full KV cache | TurboQuant | `AWQ + TurboQuant` only after method validation |
| C3 | Qwen3-4B-AWQ | PyramidKV | FP16 | `AWQ + PyramidKV` |
| C4 | Qwen3-4B-AWQ | PyramidKV | TurboQuant | `AWQ + PyramidKV + TurboQuant` |

The notebook must fail closed. A configuration is **blocked**, not substituted, when its requested method does not pass its correctness and storage gates. For example, HQQ 4-bit may be collected as a separately labelled exploratory configuration, but it must never be reported as TurboQuant.

This document is an implementation blueprint. It applies the same engineering pattern to another Transformers model only after its attention and cache API have been separately inspected and pinned.

## 2. What The Existing Notebook Proves

The current notebook establishes a useful base but not the requested compound method:

- C0 and C1 run as FullKV and pass their 512-token sanity/NIAH pilot.
- The existing community TurboQuant cache exposes compressed tensors but retains FP16 K/V tensors. The physical-storage gate rejects it.
- C2 therefore runs Transformers `QuantizedCache` with the HQQ backend. This is not TurboQuant.
- C3 and C4 are intentionally blocked because official PyramidKV/SnapKV adapters do not support Qwen3 and pin an incompatible Transformers version.
- The current full matrices enumerate only C0, C1, and C2. Enabling their flags cannot produce C3/C4 results.

The archived Qwen2.5 notebook is useful as an example of a custom attention patch and a cache passed to `generate()`. It is not reusable code: it patches `Qwen2Attention`, does not preserve evicted-token positions, monkey-patches the TurboQuant constructor, and never proves physical KV-cache compression.

## 3. Research Questions This Notebook Must Answer

### RQ1: Compound trade-off

At 512, 2048, and 8192 input tokens, compare C0-C4 for:

- GPU energy in joules, both gross and idle-baseline-subtracted
- average/median power in watts
- prefill and decode latency
- prefill and decode throughput
- allocated and reserved peak VRAM
- persistent KV-cache bytes
- NIAH retrieval accuracy
- an active-cache language-modelling loss or perplexity measure, if a valid held-out corpus is available

This isolates AWQ (C1 vs C0), TurboQuant (C2 vs C1), PyramidKV (C3 vs C1), and their compound effect (C4 vs C1/C2/C3).

### RQ2: Thinking-mode trade-off

At 8192 input tokens, compare C0, C1, and a validated C4 in both non-thinking and thinking modes. Report energy, generated-token count, latency, answer correctness, and parse success. Do not replace unavailable C4 with C2 while calling the experiment the planned C4 subset.

### Supporting questions from the literature review

- Does the compound method cause constructive or destructive interaction between eviction and quantization?
- Is the T4 cost of TurboQuant's rotation/quantization work justified by lower persistent cache memory?
- Does the compound configuration meet a clearly defined edge-memory target? Report measured VRAM; do not infer it from weight size.
- Are SLM/Qwen3 results sensitive to compression despite results reported on larger models?

## 4. Claims That Require Evidence

| Claim | Required evidence before it appears in results |
|---|---|
| AWQ | Official AWQ model loads, runs, and is identified in the environment manifest. |
| PyramidKV | Code follows a pinned, inspected reference algorithm; per-layer budgets and retained absolute positions are logged; structural and NIAH gates pass. |
| TurboQuant | The exact algorithm/implementation is pinned, its quantizer applies to K and V as documented, compressed state is physically stored, and persistent FP16 history is absent. |
| C4 compound | C3 and C2 gates both pass when composed, not only in isolation. |
| Cache-memory saving | Recursive accounting of every reachable cache tensor, not global peak VRAM alone. |
| Peak-VRAM saving | `torch.cuda.max_memory_allocated()` and `max_memory_reserved()` reset and recorded per run. |
| Energy saving | NVML power trace covers the whole timed interval, with at least three randomized repetitions and raw traces retained. |
| Accuracy impact | Fixed deterministic NIAH items/depths and a stored correctness field in the primary result row. |

## 5. Method Definition Decisions To Lock Before Coding

### 5.1 Version and environment contract

1. Pin Python, PyTorch, CUDA, Transformers, AutoAWQ/GPTQ backend, `accelerate`, `pynvml`, and every custom repository commit.
2. Record those versions, model revisions, GPU name, driver, CUDA runtime, seed, and notebook git revision in `environment_manifest.json`.
3. Assert Qwen3-4B architecture at runtime: 36 layers, 32 query heads, 8 KV heads, and head dimension 128.
4. Call the C0 baseline FP16, not BF16: a T4 has no native BF16 execution.
5. Pin to one inspected Transformers implementation. A forward patch copied from one version cannot silently run against another.

### 5.2 PyramidKV budget definition

The phrase "1024 cap" is ambiguous. Resolve it in the notebook metadata and paper before implementation:

- **Recommended definition:** mean physical retention of 1024 tokens per layer, with a total budget of `36 * 1024 = 36,864` layer-token entries distributed by PyramidKV's layerwise allocation rule.
- State the exact per-layer budget vector in the output. Its sum must equal the total budget.
- Do not claim a 1024-token cache if each of 36 layers keeps 1024 tokens; that is a 36,864 layer-token budget.
- Verify the direction of the pyramid against the pinned PyramidKV reference. The current proposal contains contradictory descriptions of whether early or late layers get more capacity. Do not choose a ramp by intuition.

### 5.3 TurboQuant method identity

Before coding C2/C4, inspect and pin the official paper code or an implementation demonstrably faithful to it. Create an algorithm checklist from that source covering rotation, quantizer/codebooks, metadata, and attention/dequantization path.

- A generic packed INT4 cache with scales is **not** TurboQuant.
- The often quoted `32 * 5-bit + 96 * 3-bit` allocation averages 3.5 bits/channel, not 4 bits, and must not be labelled "TurboQuant 4-bit" without source-backed justification.
- Do not mention outlier handling or QJL unless the code actually implements it.
- If the available implementation cannot pass the physical-storage and functional gates, keep C2/C4 blocked and optionally add `C2-HQQ` / `C4-HQQ` as clearly separate exploratory configurations.

### 5.4 Fair attention backend

Score-based eviction requires attention probabilities, so C3/C4 need an eager attention path or an equivalent explicit score computation. Backend choice affects energy and latency.

- Primary controlled comparison: run C1, C3, and C4 with the same eager attention backend.
- Optional deployment comparison: separately measure C1 with SDPA, explicitly labelling backend as a factor.
- Never attribute a difference between eager C3 and SDPA C1 solely to cache eviction.

## 6. Correct Qwen3 Integration Design

### 6.1 Do not reimplement the whole model

Keep the loaded Hugging Face Qwen3 model and its AWQ-backed linear modules. Reimplementing AWQ weight unpacking, CUDA kernels, RMSNorm, MLP, generation, and the LM head would create a new unvalidated model.

Implement only the research contribution:

1. a Qwen3-aware cache object; and
2. a tightly scoped, version-pinned Qwen3 attention/model mask adapter.

Use native `q_proj`, `k_proj`, `v_proj`, `o_proj`, `q_norm`, `k_norm`, RoPE, and output projection modules. This preserves the official AWQ behavior.

### 6.2 Required Qwen3 attention sequence

For every layer invocation, preserve the pinned Qwen3 order:

1. Project hidden states into Q, K, V with native modules.
2. Reshape Q to 32 heads and K/V to 8 heads.
3. Apply Q/K normalization in the native location.
4. Apply RoPE to Q and K using the model-provided position embeddings and absolute positions.
5. Assemble cached K/V with their original absolute token positions.
6. Build a causal mask from query absolute positions to retained key absolute positions.
7. Repeat K/V from 8 to 32 heads only for the attention computation.
8. Compute eager attention, including masking and dtype behavior matching the pinned implementation.
9. Aggregate observation-window scores and compact the persistent cache only after attention has used the candidate K/V.
10. Apply the native output projection and return the exact expected forward signature.

### 6.3 Position-safe custom cache contract

A normal `DynamicCache` is not sufficient after non-contiguous eviction. For every layer the custom cache must maintain:

```text
logical_length: number of tokens ever processed for the sequence
key_states: physical retained K tensor, [batch, 8, retained_tokens, 128]
value_states: physical retained V tensor, [batch, 8, retained_tokens, 128]
key_positions: absolute positions for the retained token columns
compression_state: TurboQuant data and only the documented residual window
```

Rules:

- `logical_length` is monotonic and determines the next query's RoPE/cache position.
- `retained_tokens` may be much smaller than `logical_length` after eviction.
- `key_positions` are sorted, batch-safe, and used to gather/build the attention mask.
- Never pretend retained entries occupy contiguous positions `0..retained_tokens-1`.
- Never feed 8192 logical positions into a cache update that stores only a selected 1024-token tensor without preserving the selected absolute positions.
- At batch size greater than one, selections must be per-example or explicitly reject batch size greater than one. Never apply `keep_indices[0]` to every example.

### 6.4 Cache composition order

For C4, perform operations in this order:

1. prefill computes candidate FP16 K/V and attention scores;
2. PyramidKV selects retained absolute positions;
3. only the selected K/V are passed to TurboQuant for persistent storage;
4. on decode, quantized retained K/V are restored only for the duration required by attention;
5. newly generated K/V are appended using the next logical position, then the configured retention/compression rule runs.

This avoids quantizing entries that eviction will discard and lets cache-byte reporting separate eviction savings from quantization savings.

## 7. Notebook Reconstruction Layout

Rebuild in ordered sections. Do not enable full collection until every pilot section reports `PASS`.

### Section 0 — Scope, status, and run switches

- Document the method contract, known limitations, IDs, contexts, seeds, and all output paths.
- Set `RUN_IMPLEMENTATION_TESTS = True` and every expensive collection flag to `False` by default.
- Define `RUN_FULL_PERFORMANCE`, `RUN_FULL_NIAH`, `RUN_FULL_THINKING`, and `RUN_PERPLEXITY` separately.
- Make each full matrix enumerate all configurations only when their validation status is `ready`; emit explicit blocked rows otherwise.

### Section 1 — Reproducible environment

- Install exact pinned dependencies.
- Load the pinned TurboQuant source only after recording its commit and checksum.
- Assert GPU availability and T4 identity.
- Save the manifest before loading a model.
- Expose a single `clear_model_and_cuda()` routine that deletes references, synchronizes, runs collection, empties cache, and records baseline memory.

### Section 2 — Data contracts and persistence

- Define immutable `ExperimentConfig`, `RunSpec`, `RunResult`, and `ValidationResult` data classes.
- Assign a unique `run_id` before inference. Every power trace, raw completion, result row, and error row includes it.
- Write JSONL traces and CSV/Parquet result rows atomically. A result row is complete only after correctness, cache evidence, and timing fields are populated.
- Preserve `requested_method`, `actual_method`, `implementation_id`, `status`, `blocked_reason`, and `validation_evidence_path`.

### Section 3 — Measurement utilities

- Implement an NVML monitor sampling at 10 Hz. Take a synchronous first sample immediately before timing and a final sample immediately after synchronization.
- Capture timestamp, power, GPU utilization, memory utilization, temperature, clock, and NVML memory used.
- Synchronize CUDA before both timing boundaries.
- Integrate power over timestamps using trapezoids; report `gross_energy_j` and `net_energy_j = gross - idle_power * duration`.
- Record allocated and reserved current/peak Torch memory, plus persistent cache bytes. Explain that peak VRAM contains model weights and transient attention/dequantization allocations.
- Warm up each model/backend outside measured runs and randomize configuration order within each matched block.

### Section 4 — Exact-token workloads

- Keep deterministic exact-token construction after applying the Qwen3 chat template.
- Persist target/actual input tokens, output-token cap, prompt hash, needle position/depth, expected answer, template parameters, and seed.
- Use completion-style NIAH prompts only after C0 proves correct at 512 tokens.
- Use 30 matched NIAH prompts per condition, balanced across 25%, 50%, and 75% depth. Do not use one item as the accuracy estimate.
- Build a preregistered thinking set with deterministic expected answers and store raw output plus extraction outcome.

### Section 5 — Model loaders and controls

- C0 loads `Qwen/Qwen3-4B` in FP16.
- C1-C4 load the official `Qwen/Qwen3-4B-AWQ` model revision.
- Assert model IDs and structural facts after load.
- Provide loaders for matched eager and optional SDPA controls; never change backend invisibly.
- Seed Python, NumPy, Torch CPU, and Torch CUDA. Use greedy decoding for structural comparisons.

### Section 6 — Reference cache accounting

Implement a recursive tensor walker that finds every tensor reachable from the cache object, including nested lists, dicts, dataclasses, and object attributes, while avoiding cycles.

For each tensor log:

- owner path
- shape, dtype, device, byte count
- role: FP16 K/V, quantized indices, scale, rotation/codebook, residual, metadata, or unknown

Compute:

- `persistent_cache_bytes`
- `persistent_fp16_history_bytes`
- `compressed_payload_bytes`
- `metadata_bytes`
- `residual_bytes`

Reject a quantized configuration if persistent FP16 K/V history outside its explicitly configured residual window is reachable. `sys.getsizeof()` alone is insufficient because it misses tensor storage.

### Section 7 — TurboQuant source audit and adapter

Before connecting the cache to Qwen3:

1. Produce an in-notebook machine-readable `turboquant_method_manifest` listing package/repository, commit, algorithm components, bits, and tensor formats.
2. Run a standalone round-trip test over Qwen3-shaped K/V tensors: `[1, 8, tokens, 128]` for 512 and 8192 tokens.
3. Verify packed storage, decoded shape/dtype/device, finite reconstruction, and no persistent full-precision duplicate.
4. Run a multi-step cache test: prefill, then at least 32 token-by-token updates; logical and physical sequence invariants must hold.
5. Compare physical bytes against FP16 FullKV at equal logical length.

Only after every test passes may the cache register as `TurboQuant`. Otherwise report the exact failure and leave C2/C4 blocked. If a separately implemented HQQ/INT4 path works, give it a distinct config ID and method name.

### Section 8 — Qwen3 position-aware cache and baseline adapter

Implement the custom cache first with **no eviction and no quantization**. Patch Qwen3 only enough to route through the custom cache and retain all tokens.

Acceptance gate:

- greedy continuation exactly matches the unpatched eager C1 model;
- logits agree within an explicit FP16 tolerance;
- logical length equals physical length;
- retained positions are contiguous;
- no NaN/Inf occurs during prefill or 32 decode steps.

Do not start eviction until this gate passes. This separates cache/mask bugs from the compression algorithm.

### Section 9 — SnapKV reference stage

Implement a shared-position, per-layer SnapKV-style selector before PyramidKV. It is the safest diagnostic step because it changes selection but not the layer-budget system.

- Use the pinned SnapKV definition of observation-window scoring.
- Apply masks before score aggregation.
- Aggregate the four query heads associated with each KV head deliberately; do not score the repeated 32-head K/V tensor as independently stored heads.
- Use one shared retained-position set per layer to avoid ragged per-head K/V tensors.
- Keep the configured recent window plus selected historical positions as defined by the reference algorithm.

Acceptance gate:

- at 512 tokens with 1024 capacity, no token is evicted and output matches the eager C1 control;
- at 2048/8192, each layer obeys its physical budget and has ordered, valid absolute positions;
- decode continues for at least 32 tokens without position/mask errors;
- NIAH passes a preregistered pilot threshold before timing runs.

This stage may be retained as a separate C3-SnapKV diagnostic, but it is not PyramidKV.

### Section 10 — PyramidKV stage

Replace the uniform SnapKV layer budget with a source-faithful PyramidKV allocation while preserving the same position-aware cache and score-selection semantics.

- Store the budget vector, actual retained count, selected-position histogram, and score summary for every layer and run.
- Assert the allocation sums to the declared total cache budget.
- At lengths below capacity, operate as a FullKV no-op.
- Name C3 `PyramidKV` only after a pinned reference implementation/reproduction checklist is satisfied.

### Section 11 — Compound C4 stage

Compose validated PyramidKV with validated TurboQuant.

- Quantize only after selected FP16 K/V are compacted.
- During decode, make dequantized K/V temporary. They must not remain in the cache object after forward returns.
- Log cache bytes before selection, after selection, and after quantization.
- Test C4 at 512, 2048, and 8192 with prefill plus multi-step decode before NIAH or power measurements.

### Section 12 — Correctness and method-identity pilot suite

Run this table, save every assertion/result to `validation_results.jsonl`, and block any failed configuration:

| Test | C0/C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| Model/cache identity | required | required | required | required |
| 512-token no-op equivalence | C1 control | cache functional | exact C1 match | exact C1 match if no quantization activates; otherwise tolerance + NIAH |
| 2048/8192 logical position correct | reference | required | required | required |
| 8 KV heads, head dimension 128 | required | required | required | required |
| 32-step decode, finite logits | required | required | required | required |
| Persistent bytes below corresponding FullKV | N/A | required | required at eviction lengths | required |
| No hidden FP16 history | N/A | required | required | required |
| NIAH pilot | required | required | required | required |

For lossy quantization, do not demand bitwise logit equality. Define and preregister tolerances, greedy-output agreement tests on a small prompt suite, and minimum NIAH pilot performance.

### Section 13 — Timed inference runner

- Use explicit prefill followed by fixed-length greedy decode. Do not stop on EOS if claiming a fixed 128-token decode; alternatively record actual output length and call it variable-length.
- Record prefill and decode timing/energy separately, then combined totals.
- Run `torch.cuda.synchronize()` around every measured segment.
- Supply explicit absolute positions and the custom cache for C3/C4.
- Run a non-measured warm-up for each model/backend/configuration.
- Record failures as structured rows; do not silently retry under a different cache implementation.

### Section 14 — Perplexity/loss evaluation

Perplexity is optional and must not be described as evaluating a cache method unless it genuinely uses that cache.

- Use a fixed held-out corpus, not repeated filler text.
- Evaluate sequential chunks with the selected cache and correct logical positions/masks.
- Keep this separate from timed generation because teacher-forced loss has a different workload.
- If custom eviction cannot support correct chunked teacher forcing, omit perplexity from cache-method claims and explain why.

### Section 15 — Full matrices

Enable only validated C0-C4 configurations.

- Performance: 3 or more repetitions per config/context, randomized in matched blocks across all comparable configurations.
- NIAH: 30 items per config/context, three depths balanced, with result correctness in the primary table.
- Thinking: C0/C1/C4 at 8192 only after C4 validation; pair each thinking task with its non-thinking counterpart.
- Persist after every run and allow restart using `run_id` and completed-result checks.

### Section 16 — Analysis and provenance

- Generate context-scaling plots for gross/net energy, latency, throughput, allocated/reserved peak VRAM, persistent cache bytes, and NIAH accuracy.
- Include an energy-versus-NIAH Pareto frontier and identify non-dominated configurations.
- Apply paired tests only to observations actually randomized and matched in blocks. Use normality checks, paired t-tests or Wilcoxon signed-rank tests, multiple-comparison correction, confidence intervals, and effect sizes.
- Use McNemar or a paired binary analysis for matched NIAH items.
- State that three repetitions are exploratory and report uncertainty rather than overclaiming significance.
- Generate a provenance report listing exact implementation IDs, validation results, blocked configs, fallback configurations, raw-trace paths, and every deviation from the planned methods.

## 8. Required Output Schema

Each completed run must contain at least:

```text
run_id, timestamp_utc, block_id, repetition, seed
config_id, requested_method, actual_method, implementation_id, backend
model_id, model_revision, dtype, gpu_name, software_manifest_path
workload_id, prompt_hash, context_target, context_actual, needle_depth
thinking_enabled, decode_target_tokens, decode_actual_tokens
prefill_seconds, decode_seconds, total_seconds
prefill_energy_j, decode_energy_j, gross_energy_j, net_energy_j
power_mean_w, power_median_w, power_min_w, power_max_w, power_samples
allocated_peak_mb, reserved_peak_mb, nvml_peak_mb
persistent_cache_bytes, compressed_payload_bytes, metadata_bytes, residual_bytes
logical_cache_length, retained_cache_length, layer_budget_summary
niah_correct, expected_answer, extracted_answer, raw_output_path
valid, validation_status, failure_reason, trace_path
```

Keep per-layer cache details in a linked JSONL file keyed by `run_id`, rather than placing large tensors or position lists in the main result table.

## 9. Completion Criteria

The notebook is ready for data collection only when all statements are true:

1. C0/C1 are validated controls with exact-token prompts and reliable power traces.
2. C2 is either a physically validated, source-faithful TurboQuant implementation or explicitly blocked.
3. C3 is a source-faithful, position-safe PyramidKV implementation with a resolved budget definition.
4. C4 passes both C2 and C3 requirements together.
5. 512-token C3 behaves as a no-op at a 1024-token capacity.
6. C3/C4 prefill and multi-step decode use correct absolute RoPE/mask positions at 2048 and 8192 tokens.
7. Every result row identifies what actually ran and contains correctness before it is persisted.
8. Full collection includes every validated configuration, and analysis pairs only genuinely matched observations.

## 10. Honest Fallbacks

| Situation | Allowed action | Required reporting |
|---|---|---|
| TurboQuant source fails physical-storage gate | Block C2/C4-TurboQuant; optionally run HQQ as a new config | State that TurboQuant was unavailable; never rename HQQ. |
| PyramidKV source cannot be ported safely | Run validated SnapKV as a distinct method | Change C3/C4 labels, proposal method text, and claims to SnapKV. |
| Compound cache fails NIAH/correctness gate | Do not collect energy results as a successful C4 method | Report failure as an engineering/negative result. |
| Time prevents full port | Run only C0/C1 plus explicitly labelled exploratory cache experiments | Narrow RQ1; do not claim a five-way compound ablation. |

## 11. Recommended Build Order

1. Rebuild Sections 0-6 and confirm C0/C1 controls.
2. Audit and isolate TurboQuant outside the model; accept or block it based on physical storage.
3. Implement a no-op position-aware Qwen3 custom cache and prove equivalence.
4. Implement/validate SnapKV selection.
5. Convert its layer allocation to source-faithful PyramidKV and validate C3.
6. Connect accepted TurboQuant to FullKV for C2 and validate it.
7. Compose the two validated components for C4 and validate it.
8. Only then enable full measurement and analysis sections.

This order is deliberate: it ensures that a failed compound method can be traced to a specific component rather than debugging AWQ, masking, eviction, quantization, energy monitoring, and statistical analysis simultaneously.
