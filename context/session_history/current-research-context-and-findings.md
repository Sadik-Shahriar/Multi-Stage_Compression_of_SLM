# Consolidated Research Context and Findings

Last updated: 2026-08-04

## 1. How to Use This File

Read this file first in a new session. It summarizes the project, completed
evidence, implementation behavior, limitations, web research, claim boundaries,
and recommended next steps. Then read:

- `previous session context/fail-safe-completion-plan.md` for Track A.
- `previous session context/high-novelty-implementation-plan.md` for Track B.
- `previous session context/things-to-do.md` for the earlier project checklist.

Do not use `archive/` as current evidence.

Experiment format rule: implement all new experiments as self-contained Google
Colab `.ipynb` notebooks with explanatory Markdown cells and isolated Drive
paths. Do not create standalone `.py` experiment runners. Track A notebooks are
stored under `experiments/track_a_failsafe_colab/`.

## 2. Project Goal

Study how weight quantization, KV-token eviction, and numerical KV-cache
quantization affect energy, latency, throughput, physical memory, and long-context
quality for sub-4B language models on an NVIDIA T4.

Current models:

- Completed: Llama 3.2-3B-Instruct.
- Completed: Qwen2.5-3B-Instruct.

Current hardware:

- Google Colab free-tier NVIDIA T4.
- Reported VRAM in the completed run: 14.56 GiB.
- Power measured at approximately 10 Hz with NVML.

## 3. Canonical Current Files

- Historical systems source: `Final notebooks/llama3_2.py`.
- Historical systems artifacts: `CSE407_llama_v5_final/`.
- Completed hard-quality/control notebook:
  `experiments/track_a_failsafe_colab/05_llama_full_quality_control_v1.ipynb`.
- Accepted hard-quality/control artifacts: `CSE407_llama_track_a_full_v1/`.
- Completed A3 notebook:
  `experiments/track_a_failsafe_colab/06_llama_power_robustness_analysis.ipynb`.
- Accepted A3 artifacts: `CSE407_llama_power_robustness_v1/`.
- Colab-ready cross-model synthesis notebook:
  `experiments/track_a_failsafe_colab/09_cross_model_synthesis_v1_colab.ipynb`.
- Local provisional reference artifacts:
  `CSE407_cross_model_synthesis_local_provisional/`, fingerprint
  `b19adce0924b4203`. Authoritative Colab execution is pending.
- Experiment registry: `research/experiment_registry.json`.
- Current IEEE paper: `proposal/ieee format/ieee_proposal.tex`.
- Previous completion context: `previous session context/things-to-do.md`.

## 4. Completed Llama Experiment

### Configuration Names

Use these names consistently:

| Config | Weight path | Eviction | KV quantization |
|---|---|---|---|
| C0 | FP16 | None | None |
| C1 | AWQ 4-bit | None | None |
| C2 | AWQ 4-bit | Custom PyramidKV-style | None |
| C3-Ref | AWQ 4-bit | None | TurboQuant 0.2.0 reference |
| C4-Ref | AWQ 4-bit | Custom PyramidKV-style | TurboQuant 0.2.0 reference |

Important: older project documents may swap C2 and C3. The completed v5 source
and results use C2 = eviction and C3-Ref = TurboQuant reference.

### Experiment Dimensions

- Contexts: 1024, 2048, 4096.
- Energy blocks: five measured blocks per core condition.
- Decode workload: fixed 64 teacher-forced tokens.
- Quality depths: 10%, 50%, 90%.
- Quality seeds: five.
- Pyramid sensitivity at 4096: average budgets 512, 1024, 1536.
- TurboQuant sensitivity at 4096: numerical bits 2, 3, 4.

### Integrity

- Fingerprint: `8d27af8c9ee94de3`.
- Schema: `v5-final-2026-07-31-1`.
- 75/75 unique core energy rows.
- 225/225 unique core quality execution rows.
- 20/20 sensitivity energy rows.
- 60/60 sensitivity quality rows.
- 95/95 power traces.
- Every primary row has `structural_pass=True`.
- Every trace reintegrates to its stored energy within floating-point tolerance.

### Main 4096 Results

| Config | Mean total energy | Decode throughput | Post-decode live cache | Retrieval |
|---|---:|---:|---:|---:|
| C0 | 701.08 +/- 8.12 J | 11.34 tok/s | 455.00 MiB | 100% |
| C1 | 631.25 +/- 5.05 J | 13.77 tok/s | 455.00 MiB | 100% |
| C2 | 529.30 +/- 20.02 J | 20.34 tok/s | 119.00 MiB | 100% |
| C3-Ref | 913.48 +/- 2.11 J | 7.66 tok/s | 696.50 MiB | 100% |
| C4-Ref | 659.50 +/- 21.35 J | 12.53 tok/s | 187.25 MiB | 100% |

Interpretation:

- C2 is the strongest current T4 systems configuration at 4096.
- C2 reduced live cache by 73.8% relative to C1.
- C2 reduced energy and increased throughput relative to C1.
- C3-Ref was slower, larger, and more energy intensive than C1 in the tested
  reference realization.
- C4-Ref was much less expensive than C3-Ref because eviction reduced the number of
  tokens entering TurboQuant.
- C4-Ref did not beat C2.

Current interaction:

`(C4-Ref - C3-Ref) - (C2 - C1)` was strongly non-zero for several metrics, but it is a
configuration-level contrast, not a clean factorial estimate, because C1 used
stock attention while C2-C4 used a custom wrapper.

## 5. Exact TurboQuant 0.2.0 Findings

### Source Verification

Completed environment:

- Package: `turboquant==0.2.0`.
- Recorded source hash:
  `7358e2778c8de6974b0c7212ae8e3dbe00552a96b2e2df0aa42878f239a4c72a`.
- The published wheel was downloaded and independently hashed.
- Its hash exactly matches the completed Colab run.

### What It Implements Correctly

The cache uses `TurboQuantMSE`, which performs:

- Vector norm calculation.
- Normalization.
- Random orthogonal rotation.
- Lloyd-Max-style scalar codebook lookup.
- Codebook index storage.
- Norm storage.
- Dequantization by codebook lookup and inverse rotation.
- A 128-token higher-precision residual window.

The completed validation proved:

- C3-Ref quantized all 28 layers at the tested validation length.
- Indices existed and were uint8.
- Index values respected the requested numerical bit range.
- Norms and residual tensors had expected shapes.
- Reconstructed K/V tensors had expected sequence lengths.
- Distortion changed monotonically with numerical precision.

Average sampled normalized MSE:

- 2-bit: approximately 0.1262.
- 3-bit: approximately 0.0475.
- 4-bit: approximately 0.0190.

The 2-bit sensitivity path had one real output failure: expected `H794-N25`,
returned `H794`. This is evidence that quantized values affected generation.

### Which Values Attention Uses

For prefill:

- The full prompt attends to unquantized prompt K/V.
- This is normal KV-cache behavior; prompt state is compressed for later decode.

For decode:

- Tokens older than the 128-token residual are quantized.
- The package reconstructs approximate old K/V from indices and norms.
- `past_key_values.update(...)` returns those reconstructed values.
- The custom Llama wrapper passes the returned values directly to attention.

Therefore, decode does not secretly use untouched old FP16 values. It uses
approximate values reconstructed from TurboQuant indices.

The first generated token is selected from full-prompt prefill logits. Later
answer tokens use the modified cache. This makes very short answer tasks less
sensitive to cache compression and motivates answer-token loss after the first
token.

### Why Physical Storage Was Larger

`turboquant==0.2.0` does two systems-level things that defeat nominal savings:

1. It uses one uint8 index per coordinate for numerical 2-, 3-, and 4-bit modes.
2. It assigns reconstructed full-size K/V to persistent layer attributes
   `self.keys` and `self.values`.

The live object graph therefore contains:

- Quantized indices.
- FP32 norms.
- FP16 residuals.
- Persistent full-size reconstructed K/V.

At 4096, C3-Ref therefore used 696.5 MiB versus 455 MiB for C1.

The package's own `memory_usage_bytes()` excludes persistent reconstructed K/V
and can miss backing allocation retained by residual slices. The project used an
alias-deduplicated live-storage audit instead.

### Correct Claim Boundary

Valid:

> The pinned TurboQuant 0.2.0 reference path is numerically active but does not
> realize packed physical storage or fused low-bit attention in this stack.

Invalid:

> TurboQuant as an algorithm always increases memory and energy.

## 6. Historical Easy Retrieval Limitations and Completed Hard Evaluation

### Why the Current Task Is Too Easy

The generator in `Final notebooks/llama3_2.py`:

- Defines only four generic filler sentences.
- Repeats a short permutation of those sentences to fill the context.
- Creates four system-code records.
- Places all four records together in one compact 44-46-token block.
- Uses no similarly formatted code records elsewhere.
- Reuses five underlying documents across three target depths.

The question is placed before the document; the suffix after the document is
only similar to `Activation code:`. The eviction selector scores old tokens from
the final 32 prompt positions, so the full requested system name is not directly
inside its observation window.

The primary v5 scorer passes any response containing the target code. A response
containing several codes could therefore pass retrieval.

### Effective Sample Size

The 225 rows are configuration executions, not 225 independent prompts:

- There are 45 unique `(context, depth, seed)` prompt placements.
- Each placement is repeated across five configurations.
- At 4096, each configuration has 15 placements.
- Those 15 placements derive from five underlying seed documents moved across
  three depths.

Even treating 15/15 as independent, a two-sided Wilson interval has a lower bound
near 79.6%, not 100% certainty. Dependence across moved documents makes the
effective evidence weaker.

### Completed Hard Retrieval Decision

The completed hard protocol uses:

- 4096 tokens.
- 32-64 separated records.
- Diverse filler.
- Similar identifiers and code-shaped distractors.
- Query after the document.
- 20 independent scenarios per depth.
- 60 scenarios per configuration.
- Unique-code primary scoring.
- Exact format and legacy target-anywhere secondary scoring.
- Wilson and paired uncertainty.

Notebook 5 completed all 300 hard-quality cases without rerunning the historical
energy matrix. Its accepted results are summarized near the end of this file.

## 7. Fairness and Robustness Terminology

Three concepts were separated during this session:

### Experimental Controls

Question:

> Did every configuration receive the same prompts, workload, wrapper conditions,
> and scoring rules?

Completed control:

- C1-W: AWQ through the same custom wrapper with no compression.

Three fixed parity probes matched exactly, and five 4096-token C1-W energy blocks
completed. Historical C1 versus C1-W energy remains descriptive because both
session and prompt/workload differ.

### Compression Robustness

Question:

> Does model behavior remain stable after eviction or quantization introduces
> information loss/noise?

Metrics:

- Paired retrieval flips.
- Correct-answer token loss.
- Logit divergence.
- Top-1 agreement.
- Truncation and refusal categories.
- Depth and scenario variation.
- Cross-model replication.

### Demographic Fairness

Question:

> Does compression amplify demographic disparities or stereotypical behavior?

This is not currently part of the core experiment. Generic quantization-bias
studies already exist, including work on KV-cache quantization. A small fairness
benchmark would add responsible evaluation but limited novelty unless designed as
a cache-sensitive study of eviction/TurboQuant interactions.

If included, it should be an exploratory appendix using an established benchmark
and C1-W as the baseline. Short first-token classification may bypass the relevant
cache effect because TurboQuant retains 128 recent tokens and first-token logits
come from full-prompt prefill.

## 8. Internet Research: Real TurboQuant Implementations

Status checked: 2026-08-03.

### Official Google Code

- Google Research published the TurboQuant paper and March 2026 blog.
- No official public Google TurboQuant implementation was found.
- The blog links to papers, not a source repository.

### vLLM

Repository:

- `https://github.com/vllm-project/vllm`

Current source includes:

- Named TurboQuant cache presets.
- Packed key and value slot sizes.
- Triton packed cache-store kernel.
- Triton decode attention reading compressed cache.
- No persistent full-history FP16 cache for normal decode.

Practical algorithm:

- Hadamard rotation.
- Lloyd-Max key quantization.
- Quantized values.
- Optional norm correction.
- QJL intentionally omitted due reported attention-quality concerns.

T4 status:

- Issue `#43576`: TurboQuant crashes on T4 because prefill incorrectly selects
  FlashAttention 2.
- PR `#43577`: adds the existing SDPA fallback for pre-Ampere GPUs.
- The contributor reports successful T4 tests with Qwen2.5-0.5B and
  `turboquant_4bit_nc`.
- The PR was still open when checked.

Conclusion:

- Best high-upside production TQ-family candidate.
- Requires an isolated patched-vLLM feasibility track.
- Not a drop-in replacement inside the current Transformers/Pyramid wrapper.

### LMDeploy TurboQuant

Repository:

- `https://github.com/InternLM/lmdeploy`

Documented mode:

- `quant_policy=42`.
- PyTorchEngine only.
- K path: 3-bit Lloyd-Max plus 1-bit QJL.
- V path: 2-bit MSE.
- Claimed approximately 5x KV compression.
- H200 benchmark reports approximately 7-8% runtime overhead.
- Head dimension must be a power of two.

Target compatibility:

- LMDeploy supports Llama 3.2 and Qwen2.5 model families.
- It supports AWQ and T4 in its broader inference stack.
- Exact TQ42 + target 3B AWQ + T4 behavior was not explicitly verified in public
  benchmarks and needs a pilot.

Conclusion:

- Closest available paper-style candidate.
- Second feasibility path after vLLM or an alternative first path if QJL fidelity
  is prioritized.

### LMDeploy Generic INT4 KV

Documented support:

- T4/Turing.
- Llama 3.2-3B.
- Qwen2.5-3B.
- AWQ W4A16.
- Online per-token/per-head INT4 cache.
- Packed and kernel-integrated attention.

Conclusion:

- Safest real production KV quantization baseline if TurboQuant-specific paths
  fail.
- Must be labeled generic INT4 KV, not TurboQuant.

### Hugging Face Quanto/HQQ

Transformers `QuantizedCache` supports:

- Quanto INT2/INT4.
- HQQ multiple bit widths.
- Persistent packed storage.
- Residual higher-precision window.

Limitation:

- It dequantizes historical K/V for ordinary attention.
- It is a physical-at-rest compression control, not fused low-bit attention.
- Arbitrary composition with the current eviction selector is not plug-and-play.

### Other Implementations

- llama.cpp variants: packed/fused work exists, but GGUF and runtime changes create
  major comparison confounds.
- Rust/mistral.rs: packed/fused variants exist, but no verified T4/AWQ path for
  this project.
- Official KIVI: custom compressed kernels, but FlashAttention 2 and old stack
  make T4/Qwen/AWQ integration high risk.
- KVQuant: GQA and environment blockers for the target models.
- GEAR: GQA and FlashAttention blockers.

## 9. Recommended Novelty Strategy

### Publication Floor

Track A:

- Hard retrieval.
- Matched wrapper control.
- Power robustness.
- Qwen replication.
- Reference-path realization audit.
- Cross-model interaction analysis.

### Highest Practical Upside

Add a separate same-backend production comparison:

- vLLM AWQ + FP16 KV versus vLLM AWQ + TQ-family packed/fused KV.
- If blocked, LMDeploy AWQ + FP16 KV versus LMDeploy TQ42.
- If blocked, LMDeploy AWQ + FP16 KV versus LMDeploy INT4 KV.

Do not compare cross-backend absolute energies as isolated method effects. Compare
relative changes within each backend, then synthesize break-even behavior.

### Strongest Central Contribution

> A realization-aware study separating numerical quantization, packed residency,
> and fused execution, combined with memory-matched eviction comparisons and
> cross-model KV-geometry break-even analysis.

This is more defensible than claiming a new compression algorithm.

## 10. Relevant Closest Work and Boundaries

- TurboQuant: numerical near-optimal quantization and long-context quality.
- RDKV: joint eviction/quantization through rate-distortion allocation.
- SAW-INT4: serving-compatible 4-bit KV realization and fused-attention concerns.
- Titanus: cascade pruning plus quantization.
- MoE-nD: per-layer routing across compression axes.
- KV Pareto: systems-level joint model/KV optimization.
- Watt Counts: energy methodology and cross-model T4 evidence.
- The Impact of Inference Acceleration on Bias of LLMs: weight/KV quantization and
  demographic-bias changes.

Do not claim:

- First joint eviction plus quantization.
- First matched-budget comparison without a complete literature audit.
- First TurboQuant implementation.
- TurboQuant universally increases energy.
- Current custom eviction is official PyramidKV.
- T4 is an edge device.

Potentially defensible narrow claims:

- Phase-resolved energy and physical-residency interaction of accessible
  implementations on sub-4B models/T4.
- Cross-model portability conditioned on very different KV geometry.
- Realization-level comparison between numerical, packed-at-rest, and fused paths.
- Nominal-rate versus measured-storage matching for eviction and quantization.

## 11. Immediate Decisions Already Reached

- The project is not fundamentally invalid.
- Existing artifacts remain useful and must be preserved.
- Current TurboQuant is a valid numerical reference, not a production physical
  implementation.
- Harder retrieval is complete and is now the primary quality evidence.
- C1-W matched wrapper control is complete.
- A custom fused kernel is out of scope.
- Qwen is complete as the accepted second-model reference-path replication.
- Social fairness is optional and secondary.
- Production TurboQuant must be tested in a separate backend track.
- Track A must finish even if every Track B experiment fails.

## 12. Recommended New-Session Starting Point

1. Read the two track plans named at the top of this file.
2. Preserve/export the executed Notebook 07 copy for reproducibility.
3. Keep the accepted Notebook 08 artifact directory immutable.
4. Keep the accepted Notebook 09 synthesis bundle immutable.
5. Complete paper formatting and the reproducibility package using the accepted
   synthesis Markdown/CSV/JSON products.
6. Keep any production-backend feasibility work isolated under Track B.

A0 completed on 2026-08-03. The immutable v5 registry is
`research/experiment_registry.json`, and its 115-file checksum manifest is
`research/llama_v5_artifact_manifest.json`.

A1 implementation began on 2026-08-03. The self-contained V1 notebook
`experiments/track_a_failsafe_colab/01_llama_hard_retrieval_pilot.ipynb` embeds
the deterministic generator, integrity checks, matched wrapper, and discarded
pilot runner. Its outputs remain under
`CSE407_llama_track_a_pilot_discarded/` as immutable discarded calibration
evidence.

Pilot V1 subsequently completed and was rejected as too hard: both C1-W and C2
scored 50%, with 100% accuracy at 10% depth and 25% at 50%/90%. The 24 paired
rows and prompt gates were valid, so this is a difficulty-calibration outcome,
not an execution failure. Run
`experiments/track_a_failsafe_colab/02_llama_hard_retrieval_pilot_v2.ipynb`
next. V2 changes only the record count from 48 to 32, adds first-target-token
rank/NLL diagnostics, and writes to a new discarded-pilot directory.

Pilot V2 also completed at 50% for both variants and is discarded. Its new
diagnostics confirmed first-token key selection as the difficulty bottleneck:
all passes ranked the target first token first, while every failure ranked it
3rd-6th; 10/12 wrong outputs were document distractor codes. Run
`experiments/track_a_failsafe_colab/03_llama_hard_retrieval_pilot_v3.ipynb`
next. V3 keeps 32 records but organizes keys into eight distinct four-sibling
families, retaining local key confusion without global ATLAS/ORION ambiguity.

Pilot V3 then fell to 25% C1-W and 16.7% C2 and is discarded. The four-sibling
design was itself too confusable. Run
`experiments/track_a_failsafe_colab/04_llama_hard_retrieval_pilot_v4.ipynb`
next. V4 retains 32 records and six controlled near-name pairs but makes the
remaining key labels semantically distinct.

Pilot V4 passed and is now frozen: C1-W and C2 each scored 75% overall, while
C1-W achieved 100%/50%/75% across 10%/50%/90% depth. The accepted semantic hash
is `fffa82607af6e7d2c892d18d5bc790524570833472ad397b7ab2e54eb03005ef`
and the Llama prompt-set hash is
`4e1ced4fd4829629929a346879cc00c45476f38fa0936137909b8779242321e8`.
See `research/frozen_hard_retrieval_v4.json`. Do not tune prompts again. The full
C0/C1-W/C2/C3-Ref/C4-Ref notebook below preserves these frozen-hash assertions.

The full-run notebook completed at
`experiments/track_a_failsafe_colab/05_llama_full_quality_control_v1.ipynb`
under schema `track-a-llama-full-v1-2026-08-03-1`, fingerprint
`106a561c07c62937`, and isolated path `CSE407_llama_track_a_full_v1/`. Its
324-file artifact bundle passed both frozen hashes, exact C1-S/C1-W parity on
three fixed probes, all cache paths, 300/300 quality rows, five C1-W energy
blocks, unique paired keys, bounded quality analysis, and trace reintegration.

Hard-retrieval accuracy was 47/60 (78.3%) for C0, 38/60 (63.3%) for C1-W, and
37/60 (61.7%) for C2, C3-Ref, and C4-Ref. Each compressed path had zero gains and
one loss relative to C1-W; its depth-stratified paired difference was -1.67
points with a two-sided 95% interval of [-5, 0] and adjusted exact p=1.0. This
does not establish strict 5-point non-inferiority. C1-W energy was
639.86 +/- 5.48 J. The TurboQuant-only C3-Ref path was physically larger than
C1-W because it retained materialized K/V; C4-Ref remained smaller than C1-W
only because prior eviction reduced token count. C2 remained the smallest path.

Notebook 06 addressed the required power robustness while preserving raw joules.
It reintegrated all 95 historical v5 traces and five C1-W traces with raw, 82 W,
and 70 W power. The valid 110.955 W C1-W transient and all other exceedances were
retained in raw evidence and handled only through declared sensitivity caps.

Notebook 06 completed under fingerprint `91ebc63773e735e6`, and its 15-file output
is immutable accepted derived evidence. It verified 95 historical and five C1-W
traces, reproduced raw joules to floating-point precision, found the registered
124.496 W maximum, and found core/sensitivity rankings and all registered
significance decisions stable under both caps. Across all traces, 82 W clipping
removed 0.148% of integrated energy and 70 W clipping removed 1.332%; raw joules
remain primary.

Notebook 07 completed on a Tesla T4 under schema
`track-a-qwen-adapter-pilot-v1-2026-08-04-1`, fingerprint
`91def77c920729e9`, and source SHA-256
`7ddad2c18febcbd23577fb85c52920bfbde18f31de2077fcc9bef6e192927809`.
It pins the official FP16/AWQ revisions, verifies the exact Transformers 5.12.1
Qwen2/cache/mask/SDPA sources, regenerates the 60 scenarios under Qwen prompt
hash `115c1568fea7aeea038a46ce309d0c8bcaf1f5405544466ad6f379ee7e94ae3a`,
and implements fail-closed Q1 parity plus active Q1-W/Q2/Q3-Ref/Q4-Ref probes.
All five artifacts passed independent validation. Q1-S and Q1-W had zero logit
difference and identical greedy outputs at 10%, 50%, and 90% depth. Q2,
Q3-Ref, and Q4-Ref had exact prefill-logit agreement with Q1-W. Q3-Ref and
Q4-Ref actual-path maximum normalized MSE values were 0.02461 and 0.02512.

Alias-deduplicated one-token-probe live storage was 151,031,808 bytes for Q1-W,
37,785,600 for Q2, 231,230,016 for Q3-Ref, and 59,482,896 for Q4-Ref. This is
structural pilot evidence, not an energy result. The five-file bundle is sealed
by `research/qwen2_5_adapter_pilot_v1_artifact_manifest.json`. An exported
executed Notebook 07 copy is not currently present in the workspace and should
be preserved before the final reproducibility package.

Notebook 08 subsequently completed on the same model family under schema
`track-a-qwen-full-reference-v1-2026-08-04-1`, fingerprint
`861d89617e53034d`, and session `20260804T154752-97822cdb`. Independent audit
accepted `CSE407_qwen_track_a_reference_v1/`: 75 core energy rows, 20
sensitivity energy rows, 95 raw traces, 300 core quality rows, and 60
sensitivity-quality rows all matched their schedules, JSON shards, CSV
snapshots, hashes, and final-integrity marker. The artifact manifest has 591
entries and byte hash
`975cb8f19405f9d7e4267bc4a8143ead943c853776c6ba88b8697695ac78c1c9`.

At 4096 tokens, Q0 used 616.78 +/- 6.79 J with 53/60 retrieval; Q1-W used
621.75 +/- 25.14 J with 48/60; Q2 used 550.48 +/- 10.07 J with only 1/60;
Q3-Ref used 812.28 +/- 13.11 J with 49/60; and Q4-Ref used 628.69 +/- 9.77 J
with 1/60. Thus Qwen eviction reduced observed energy but catastrophically
damaged retrieval, while TQ-Ref preserved Q1-W-like quality only on the
non-evicted path at substantial energy cost. The compound energy interaction
was significant for total and decode energy under raw, 82 W, and 70 W
integrations. Rankings and registered significance decisions were cap-stable.

The executed notebook required two in-session repairs: one quality-validator
field-name correction and one capped-analysis merge correction. The exported
notebook contains both successful fixes inline and all persisted evidence is
internally hash-consistent, but fingerprint `861d89617e53034d` does not
cryptographically bind the executed notebook or repair-cell source. Preserve
this as a reproducibility caveat rather than treating it as a measurement
failure.

The registered Notebook 09 extension now includes an ideal-realization
counterfactual. Its contribution is not to assert that TQ-Ref measured an ideal
kernel. It will validate batch-one logical byte accounting against direct FP
tensor geometry and observed uint8 payloads, then project aligned nominal-bit
storage without materialized K/V. Numerical/energy/quality projection is limited
to the same observed path; unobserved low-bit compounds may appear only as
storage-only rows with quality and energy unknown.
This permits a conditional proof of projected persistent-KV memory dominance
under fixed budgets and representation assumptions, not packed hardware
validation or total peak-VRAM proof.

Ideal energy is not point-identified by the completed experiments. Notebook 09
will therefore derive the indexed break-even surface
`O_net < epsilon_mem * Delta_D`, indexed by baseline path, source session,
context/phase, and integration regime. `Delta_D` is modeled compulsory/logical
byte-demand saving rather than observed DRAM traffic and `O_net` excludes all
traffic already counted. Numerical projected energy is allowed only over finite,
justified parameter domains; otherwise results remain symbolic. `O_net=0` is a
zero-net-overhead reference, not an absolute best case. Lower energy does not
prove lower power.

Prefill and decode byte demand are separate. Prefill preserves full-prompt
attention before eviction and counts only justified post-attention representation
writes; total-energy projection requires both phase models. Otherwise only decode
energy may be projected.

The ideal path has unchanged retrieval only under strict output equivalence, not
merely similar reconstruction. Quality/Pareto projection is limited to observed
nominal-bit paths: no 2/3-bit compound quality exists, Llama low-bit quality is
task-incomparable, and Qwen TQ-only bit-width comparisons require common-15
scenarios. Final projected recommendations minimize conditional energy and
persistent KV memory subject to point/interval retrieval feasibility; latency
remains empirical. Point feasibility is separate from exclusive interval states
of feasible, uncertain, or infeasible. Bootstrap membership is selection stability, not truth
probability. Sampling uncertainty and realization-parameter sensitivity remain
separate.

Projected quality under strict equivalence inherits the observed TQ-Ref path
(Q4 from Q4-Ref, not Q2). Point, conservative lower-bound, and possible upper-
bound frontiers are separate, with conservative primary. Energy and quality are
resampled independently; pairing is preserved only within source sessions and
within-depth quality scenario IDs.

## 13. Source Links for Future Verification

- TurboQuant paper: `https://arxiv.org/abs/2504.19874`
- Google blog:
  `https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/`
- vLLM T4 issue: `https://github.com/vllm-project/vllm/issues/43576`
- vLLM T4 patch: `https://github.com/vllm-project/vllm/pull/43577`
- vLLM TQ backend:
  `https://github.com/vllm-project/vllm/blob/main/vllm/v1/attention/backends/turboquant_attn.py`
- LMDeploy KV/TQ documentation:
  `https://github.com/InternLM/lmdeploy/blob/main/docs/en/quantization/kv_quant.md`
- LMDeploy supported models:
  `https://github.com/InternLM/lmdeploy/blob/main/docs/en/supported_models/supported_models.md`
- HF quantized cache:
  `https://huggingface.co/docs/transformers/main/en/kv_cache#quantized-cache`
- RDKV: `https://arxiv.org/abs/2605.08317`
- SAW-INT4: `https://arxiv.org/abs/2604.19157`
- Inference acceleration and bias: `https://arxiv.org/abs/2410.22118`
