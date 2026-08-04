# Track B: High-Novelty Systems Realization Plan

Last updated: 2026-08-03

## 1. Purpose

Track B seeks the highest defensible novelty without requiring the team to design
a fused CUDA kernel from scratch. It investigates whether a physically packed and
kernel-integrated KV quantizer can turn the numerical compression studied in
Track A into real memory, throughput, and energy benefits.

Track B is optional and fault-contained. Track A remains the publication floor.
Every Track B experiment must use separate notebooks, environments, schemas,
result directories, and same-backend baselines.

Experiment format rule: every implementation must be a self-contained Google
Colab `.ipynb` notebook with proper Markdown cells. Do not create standalone
`.py` experiment runners. Store future Track B notebooks in their own dedicated
notebook folder with numeric run-order prefixes.

## 2. High-Novelty Research Question

> How do numerical quantization, packed cache residency, and fused compressed
> attention differ in their actual energy, latency, memory, and retrieval effects
> on 3B models and a T4, and where are their context/decode break-even points?

This reframes the project from "stack three techniques" to a realization-aware
systems study.

## 3. Status Legend

| Status | Meaning |
|---|---|
| COMPLETED | Verified research or implementation fact |
| ONGOING | Active design or feasibility work |
| PENDING | Not yet executed |
| GATED | May begin only after the named gate passes |
| FALLBACK | Used only if a higher-ranked path fails |
| REJECTED | Not appropriate under current constraints |

## 4. Confirmed State of Available Implementations

### COMPLETED: Internet and Source Audit

As checked on 2026-08-03:

- Google Research has published the paper and blog but no official public
  TurboQuant code repository was found.
- vLLM `main` contains a physically packed TurboQuant-family backend with Triton
  cache-store and decode-attention kernels.
- vLLM intentionally omits QJL in its practical presets and uses Hadamard plus
  Lloyd-Max key quantization and quantized values.
- vLLM has a T4/Turing prefill bug because FlashAttention capability is checked
  incorrectly.
- vLLM issue `#43576` documents the T4 failure.
- vLLM PR `#43577` provides an SDPA fallback and reports successful T4 testing on
  Qwen2.5-0.5B, but the PR was still open when checked.
- LMDeploy documents TurboQuant `quant_policy=42`: 3-bit Lloyd-Max plus 1-bit QJL
  for keys and 2-bit MSE for values, approximately 5x cache compression.
- LMDeploy TurboQuant is PyTorchEngine-only and was publicly benchmarked on H200;
  the exact T4 + AWQ + target-model combination still requires validation.
- LMDeploy's ordinary KV INT4 supports T4, Llama 3.2, Qwen2.5, and AWQ and is the
  safest production low-bit fallback.
- Hugging Face Quanto and HQQ `QuantizedCache` backends provide physically packed
  persistent storage but dequantize full history transiently for ordinary
  attention.
- llama.cpp and Rust/mistral.rs TurboQuant implementations exist, but changing to
  GGUF or a different weight/runtime ecosystem would create major confounds.

## 5. Track B Architecture

Track B has four realization levels:

| Level | Label | Example | Persistent packing | Compressed/fused decode |
|---|---|---|---:|---:|
| Reference | TQ-Ref | Current PyPI v0.2 | No | No |
| Packed at rest | KVQ-Pack | HF Quanto/HQQ | Yes | No |
| Production generic | KVQ-Fused | LMDeploy INT4 | Yes | Yes |
| Production TQ-family | TQ-Fused | Patched vLLM or LMDeploy TQ | Yes | Yes |

These levels do not all use identical quantization mathematics. They compare
implementation realization classes. Any paper must state that limitation.

## 6. Required Execution Order

### B0. Preserve Track A and Create an Isolated Feasibility Harness

Status: PENDING

Tasks:

- Create a separate Colab notebook for backend feasibility only.
- Do not import or write into Track A result directories.
- Add a minimal NVML monitor, exact prompt builder, fixed 64-token decode, and
  deterministic quality smoke test.
- Record backend version, git commit, applied patch commit, CUDA, driver, GPU,
  checkpoint revision, and command-line/runtime settings.

Completion gate:

- A backend can be installed and removed without affecting the completed
  Transformers environment.

### B1. Feasibility Path 1: Patched vLLM TurboQuant

Status: PENDING

Priority: HIGHEST UPSIDE

Candidate configuration:

- Same AWQ checkpoints where supported.
- `kv_cache_dtype="turboquant_4bit_nc"`.
- T4 SDPA prefill patch from vLLM PR `#43577` or a later merged equivalent.
- Triton TurboQuant decode.
- Start with eager execution to reduce graph-related variables.

Smoke-test order:

1. Reproduce the documented Qwen2.5-0.5B T4 smoke test.
2. Test the exact Qwen2.5-3B AWQ checkpoint.
3. Test the exact Llama 3.2-3B AWQ checkpoint.
4. Test 4096-token prefill plus 64-token decode.
5. Confirm physical cache allocation from backend cache shapes and NVML.
6. Confirm coherent deterministic generation.

Mandatory gates:

- T4 `sm_75` compile and startup succeed.
- Both target AWQ checkpoints load or a documented model-format blocker is found.
- 4096 + 64 workload completes without OOM.
- The packed cache is at least approximately 3x smaller than same-backend FP16 KV.
- Decode uses the TurboQuant Triton path.
- No persistent full-history FP16 cache exists.
- Hard retrieval remains within a predeclared quality margin.
- Power monitoring captures sufficiently long synchronized phases.

Failure rule:

- If any mandatory gate cannot be resolved quickly, stop. Do not port vLLM or
  write a replacement kernel. Move to B2 while retaining all diagnostic logs.

### B2. Feasibility Path 2: LMDeploy TurboQuant

Status: FALLBACK

Candidate configuration:

- LMDeploy PyTorchEngine.
- `quant_policy=42`.
- AWQ model format if supported by the selected engine/model combination.
- Optional `fast_hadamard_transform`; fall back to the documented matrix path if
  unavailable on T4.

Why this path matters:

- It is closer to the paper's QJL-based construction than the practical vLLM
  presets.
- It documents K4 QJL plus V2 MSE and approximately 5x KV compression.

Mandatory gates:

- Exact target models and AWQ format load.
- T4 kernels or documented fallback execute correctly.
- Cache is physically packed.
- 4096 + 64 workload completes.
- Same-backend FP16 KV baseline can be measured.
- Quality and power instrumentation can be reproduced.

Failure rule:

- If TQ42 is unsupported on the target combination, stop rather than modifying
  LMDeploy internals. Move to B3.

### B3. Feasibility Path 3: LMDeploy Generic KV INT4

Status: FALLBACK

Priority: SAFEST PRODUCTION LOW-BIT CONTROL

Confirmed documented support:

- T4/Turing.
- Llama 3.2-3B.
- Qwen2.5-3B.
- AWQ W4A16.
- Online per-token, per-head KV INT4.
- Packed cache and quantized paged-attention kernels.

Purpose:

This is not TurboQuant. It supplies a credible production control showing what
physically packed and kernel-integrated KV quantization can achieve on the same
hardware and model family.

Required comparison:

- LMDeploy AWQ + FP16 KV.
- LMDeploy AWQ + INT4 KV.

Completion gate:

- Same-backend relative changes in energy, throughput, memory, and hard retrieval
  are available for both models.

### B4. Same-Stack Packed-at-Rest Control with HF Quanto

Status: OPTIONAL

Purpose:

Create an intermediate realization between TQ-Ref and fused production KVQ.

Candidate:

- Transformers `QuantizedCache`.
- Optimum-Quanto INT4.
- 128-token residual window.
- Standard Transformers attention.

Expected behavior:

- Persistent cache is physically packed.
- Historical K/V is dequantized transiently for the active layer.
- Memory residency should improve.
- Latency and energy may worsen because decode is not fused.

Scientific value:

This can test whether packing alone is enough, or whether fused compressed
attention is necessary for energy savings.

Restrictions:

- Do not assume it can compose with arbitrary Pyramid token selection.
- Do not label it TurboQuant.
- Audit nested packed tensor storage rather than trusting public shape/dtype.

### B5. Same-Backend Baselines and Measurement Design

Status: GATED on one production path passing

Rule:

Never infer a method effect by directly subtracting energies from different
backends.

Valid comparisons:

- Transformers TQ-Ref relative to Transformers C1-W.
- vLLM TQ-Fused relative to vLLM AWQ + FP16 KV.
- LMDeploy TQ/INT4 relative to LMDeploy AWQ + FP16 KV.
- HF Quanto relative to the matched Transformers AWQ wrapper baseline.

Cross-backend synthesis:

- Compare percentage changes.
- Compare context/decode break-even points.
- Compare measured live bytes per KV byte-token.
- Report backend as an explicit factor.
- Treat absolute cross-backend energy as a system comparison, not isolated
  TurboQuant causality.

### B6. Production Experiment Matrix

Status: GATED on feasibility and quality gates

Models:

- Llama 3.2-3B-Instruct AWQ.
- Qwen2.5-3B-Instruct AWQ.

Contexts:

- 1024, 2048, 4096.
- Add 8192 only if both same-backend conditions fit and prefill remains valid.

Decode lengths:

- 64 tokens for direct continuity with Track A.
- 256 tokens as an optional break-even stress condition.

Repetitions:

- One warmup per condition.
- Five randomized measured blocks.
- Separate model-resident phases where unavoidable.

Metrics:

- Prefill/decode/total energy.
- Decode J/token.
- Latency and throughput.
- Packed cache bytes.
- Allocated, reserved, and NVML memory.
- Temporary workspace peak.
- Hard retrieval and answer-token loss.
- Backend-specific cache-capacity increase.

### B7. Memory-Matched Eviction Versus Quantization

Status: OPTIONAL HIGH-VALUE EXTENSION

Research question:

> Under the same measured persistent cache budget, is it better to retain fewer
> tokens precisely or retain all tokens approximately?

Two matching rules:

- Nominal-rate match: compare 4-bit all-token storage with approximately 25%
  FP16 token retention.
- Realized-storage match: tune eviction budget to match measured persistent bytes,
  including residuals and metadata.

Required caveat:

If methods run in different backends, this is a system-level comparison. A clean
algorithmic comparison requires the same backend and attention path.

### B8. Standard Quality Benchmarks

Status: OPTIONAL FOR HIGH-TIER SUBMISSION

Add after hard NIAH is stable:

- A bounded RULER subset.
- A bounded LongBench or LongBench-E subset.
- Exact task templates and deterministic decoding.
- Per-task and aggregate reporting; do not hide task-specific failures.

Purpose:

External validity beyond a custom synthetic retrieval generator.

### B9. Cross-Model Break-Even Analysis

Status: GATED on both models

Key architectural contrast:

- Llama 3.2-3B: 28 layers, 8 KV heads, head dimension 128.
- Qwen2.5-3B: 36 layers, 2 KV heads, head dimension 128.
- Qwen's nominal FP16 KV bytes/token are roughly 32% of Llama's.

Hypothesis:

- Production KV quantization and eviction should have a later or weaker energy
  break-even on Qwen because its uncompressed KV cache is already smaller.
- Quantization transformation overhead may remain substantial even when bytes
  saved are smaller.

Do not attribute all differences to architecture; tokenizer, training, checkpoint,
and kernels also differ.

## 7. Highest-Novelty Contribution Package

The strongest coherent paper combines:

1. Numerical-reference audit from Track A.
2. Packed/fused same-backend production control from Track B.
3. Memory-matched eviction-versus-quantization analysis.
4. Cross-model KV-geometry break-even analysis.
5. Hard NIAH plus at least one standard long-context benchmark.

Proposed central claim:

> We show that conclusions about KV-cache compression change materially across
> numerical, packed-at-rest, and fused-execution realizations. On two 3B models
> with different KV geometry, we quantify when compression becomes physically and
> energetically useful and compare those break-even points with token eviction
> under nominal and measured cache budgets.

## 8. Rejected High-Risk Paths

Status: REJECTED unless project scope changes

- Writing a custom fused CUDA/Triton TurboQuant attention kernel.
- Porting official KIVI to T4, current Transformers, AWQ, and Qwen.
- Using KVQuant despite current GQA and environment incompatibilities.
- Using GEAR despite GQA and FlashAttention constraints.
- Migrating the main experiment to llama.cpp/GGUF and treating results as directly
  comparable to the AWQ Transformers matrix.
- Replacing completed artifacts silently with a new backend.
- Claiming first joint eviction and quantization; RDKV, Titanus, MoE-nD, and other
  work already cover joint or staged compression.

## 9. Publication Reality

Track B can substantially improve scientific novelty, but it does not guarantee a
NeurIPS main-track paper. A competitive high-tier submission would likely need:

- Standard benchmark breadth.
- Strong recent baselines such as RDKV or deployable fused KVQ where feasible.
- More than one hardware environment for broad energy claims.
- Kernel or memory-traffic profiling.
- Public reproducible code.
- Sufficient statistical power.
- A clearly new method or a broadly important empirical finding.

A realization-aware T4/SLM paper is still valuable for a systems, Green AI, or
efficient-ML workshop even if Track B stops before the full matrix.

## 10. Track B Stop/Go Decisions

| Result | Decision |
|---|---|
| vLLM TQ passes all gates | Run same-backend Llama pilot, then Qwen |
| vLLM fails but LMDeploy TQ passes | Use LMDeploy TQ as production path |
| Both TQ paths fail, LMDeploy INT4 passes | Use INT4 as production KVQ control |
| Only HF Quanto passes | Publish packing-versus-reference audit; no fused claim |
| Every external path fails | Stop Track B and finish Track A |
| Production memory improves but energy worsens | Report capacity benefit and energy cost |
| Production memory and energy improve | Expand contexts, models, and quality benchmarks |
| Quality loss exceeds margin | Report trade-off; do not tune after seeing test results |

## 11. Immediate Next Actions

1. Finish Track A hard retrieval design first.
2. Create an isolated vLLM feasibility notebook.
3. Reproduce the documented patched-T4 smoke test.
4. Test exact Qwen and Llama AWQ checkpoints at 4096 + 64.
5. Stop or proceed strictly according to the gates above.
6. If vLLM fails, test LMDeploy TQ42, then LMDeploy INT4.
7. Run a complete production matrix only after feasibility is proven.
