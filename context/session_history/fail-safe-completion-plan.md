# Track A: Fail-Safe Research Completion Plan

Last updated: 2026-08-04

## 1. Purpose

This is the lowest-risk path to complete the project without depending on a new
TurboQuant implementation, a custom CUDA kernel, or an unverified inference
backend. It preserves the completed Llama energy experiment and strengthens the
parts that currently limit the paper: retrieval difficulty, matched controls,
model-behavior robustness, statistical uncertainty, and cross-model evidence.

Track A must remain independently completable. Track B may add novelty, but no
Track A deliverable may depend on Track B succeeding.

## 2. Central Research Position

The existing TurboQuant path is not inactive or fake. It implements numerical
TurboQuant-MSE behavior: it rotates KV vectors, maps them to codebook indices,
stores indices and norms, reconstructs approximate KV values, and uses those
reconstructed values during decode attention.

The limitation is systems realization. `turboquant==0.2.0` stores one uint8 per
index and persistently retains full-size reconstructed `keys` and `values`.
Therefore, Track A must call it the **TurboQuant 0.2.0 reference path**, not a
physically packed or fused 4-bit cache.

The safe paper claim is:

> We evaluate the numerical and realized systems behavior of an accessible,
> pinned TurboQuant reference path, distinguish nominal precision from physical
> storage, and test how it composes with KV-token eviction on Llama 3.2-3B. The
> planned Qwen2.5-3B replication will test cross-model portability.

## 3. Status Legend

| Status | Meaning |
|---|---|
| COMPLETED | Finished and validated; do not redo unless an error is found |
| ONGOING | Started or designed but not yet fully executed |
| PENDING | Required work not yet started |
| OPTIONAL | Useful only after required Track A work is complete |
| BLOCKED | Cannot proceed until the named dependency is resolved |

## 4. Current Status

### COMPLETED

- Llama 3.2-3B v5 experiment finished without failed assertions.
- 75/75 core energy rows and 225/225 core quality execution rows exist.
- 20/20 sensitivity energy rows and 60/60 sensitivity quality rows exist.
- 95/95 raw 10 Hz power traces exist and reintegrate to stored joules.
- All 380 primary rows have `structural_pass=True`.
- Model revisions, package versions, TurboQuant source hash, session ID, and
  experiment fingerprint were recorded.
- Current C2 uses custom PyramidKV-style eviction; it is not official
  KVCache-Factory PyramidKV.
- Current C3-Ref uses the independent `turboquant==0.2.0` reference package.
- The exact TurboQuant wheel source was inspected and its hash matches the run.
- The current reference path was confirmed to use reconstructed quantized values
  during decode rather than untouched old FP16 values.
- The current IEEE draft reports the main energy, memory, throughput, interaction,
  and quality-ceiling findings with major caveats.
- A0 evidence freeze completed: all 115 historical artifact files, including all
  95 power traces, are externally checksummed and registered.
- The full frozen Llama quality/control run completed under fingerprint
  `106a561c07c62937`: 300/300 quality rows, five C1-W energy blocks, 300 unique
  paired keys, exact C1-S/C1-W parity on the declared probes, and all final
  integrity gates passed.
- Hard-retrieval accuracy was 78.3% for C0, 63.3% for C1-W, and 61.7% for each
  of C2, C3-Ref, and C4-Ref. Each compression path had one paired loss and no
  gains relative to C1-W; the depth-stratified interval was [-5, 0] points.
- A3 power robustness completed under fingerprint `91ebc63773e735e6`. All 100
  traces verified and reintegrated; 82 W and 70 W clipping preserved every core
  and sensitivity mean-energy ranking and every registered significance decision.
- Raw telemetry contained 1501/82/21 samples above 70/82/100 W and a maximum of
  124.496 W. Raw joules remain primary; clipping is sensitivity analysis only.

### ONGOING

- Build and validate the Qwen2.5-3B model adapter and stock-versus-wrapper parity
  pilot before any Qwen measurement matrix.
- Reframing the contribution around implementation-aware realization rather than
  assuming nominal low-bit precision produces physical savings.

### PENDING

- Full Qwen experiment after adapter validation.
- Final paper formatting and reproducibility packaging.

## 5. Scope Rules

Track A must follow these rules:

- Do not overwrite `CSE407_llama_v5_final/`.
- Do not change or reinterpret the completed energy values silently.
- Do not call the current TurboQuant path packed, fused, or physically 4-bit.
- Do not claim that the current result disproves the TurboQuant algorithm.
- Do not claim general quality neutrality from the current easy NIAH ceiling.
- Do not add a custom fused kernel to Track A.
- Do not require 8192-token Llama runs; 8192 previously exceeded the safe
  free-tier T4 workflow.
- Keep C2 = AWQ + eviction and C3-Ref = AWQ + TQ-Ref consistently.
- Use new schemas, fingerprints, CSV names, and result directories for every new
  experiment.
- Implement every new experiment as a self-contained Google Colab `.ipynb`
  notebook with proper Markdown cells; do not use standalone `.py` experiment
  runners.
- Keep Track A notebooks in `experiments/track_a_failsafe_colab/` with numeric
  run-order prefixes.

## 6. Required Execution Order

### A0. Freeze and Register Existing Evidence

Status: COMPLETED

Completion note (2026-08-03):

- `research/llama_v5_artifact_manifest.json` records SHA-256 checksums and byte
  sizes for every file under `CSE407_llama_v5_final/` without modifying it.
- The local repository manifest contains 115 files because it includes the
  non-evidence `.gitignore`; the Colab Drive freeze correctly contains 114
  scientific artifact files, including all 95 power traces.
- `experiments/track_a_failsafe_colab/00_verify_historical_evidence.ipynb`
  checks the complete inventory, five primary CSV row counts and fingerprints,
  380 structural passes, and the exact set of 95 power traces.
- `research/experiment_registry.json` records the immutable v5 schema,
  fingerprint, model revisions, backend, artifact path, and `TQ-Ref` label policy.
- Separate namespaces are reserved for the hard retrieval/control experiment,
  power robustness analysis, Qwen replication, and optional Track B pilot.

Tasks:

- Mark `CSE407_llama_v5_final/` as immutable historical evidence.
- Record checksums for the primary CSVs, validation JSON, environment JSON, and
  power traces.
- Create a small experiment registry listing schema, fingerprint, model revision,
  backend, and artifact path for every future run.
- Use `TQ-Ref` in new analysis labels for the existing TurboQuant path.

Completion gate:

- The old artifacts can be verified and cannot be confused with new quality,
  Qwen, or alternative-backend results.

### A1. Implement the Harder Retrieval Benchmark

Status: COMPLETED

Implementation note (2026-08-03):

- `experiments/track_a_failsafe_colab/04_llama_hard_retrieval_pilot_v4.ipynb`
  embeds a generator for 60 deterministic, model-independent scenarios across
  the three depths with 32 unique, separated records per document and controlled
  similarly named keys.
  named keys.
- Tokenizer-aware materialization enforces exact 4096-token inputs, target depth
  in token space, a complete post-document query in the final 32 tokens, unique
  distractor codes, no answer leakage, and per-prompt token-ID hashes.
- `score_response` reports the strict primary endpoint, exact format, legacy
  target-anywhere correctness, extracted codes, and explicit multiple/wrong/
  truncated/no-code failure categories.
- The pilot notebook contains CPU-level deterministic, integrity, and scoring
  checks before loading the model.
- The same notebook is an isolated, resumable runner for 12 scenarios per
  variant. It runs only C1-W and C2, saves the real Llama token-ID manifest,
  measures strict retrieval and teacher-forced answer log probability after the
  first answer token, and writes only to
  `CSE407_llama_track_a_pilot_v4_discarded/`.
- The V4 generator and prompt set are frozen in
  `research/frozen_hard_retrieval_v4.json`; no further prompt tuning is allowed.

Pilot calibration update (2026-08-03):

- V1 completed with 24/24 paired rows and valid prompt/hash gates, but C1-W and
  C2 each achieved only 50% retrieval. Accuracy was 100% at 10% depth and 25%
  at both 50% and 90%, so V1 is permanently discarded as too hard.
- Failures were well-formed wrong-code selections, usually codes belonging to
  similarly named distractor records. C1-W post-first-token NLL remained near
  zero even on failures, showing that first-token record selection was the main
  calibration problem; C2 continuation NLL increased strongly on failures.
- `02_llama_hard_retrieval_pilot_v2.ipynb` changes exactly one difficulty
  factor, reducing records from 48 to 32, while preserving contexts, depths,
  seeds, key construction, variants, and scoring. It also records target
  first-token rank/NLL as a diagnostic.
- V2 writes only to `CSE407_llama_track_a_pilot_v2_discarded/` and must pass the
  same predeclared C1-W difficulty gate before the benchmark can be frozen.

Pilot V2 update (2026-08-03):

- V2 also completed with 24/24 valid paired rows but remained too hard: C1-W
  and C2 again scored 50%. C1-W was 100% at 10%, 0% at 50%, and 50% at 90%.
- Every correct case had target first-token rank 1; every failure ranked the
  target first token 3rd-6th. Ten of twelve wrong outputs were codes from actual
  distractor records. C1-W and C2 first-token diagnostics were identical, as
  expected because compression affects cache-backed continuation, not prefill
  logits.
- `03_llama_hard_retrieval_pilot_v3.ipynb` keeps 32 records and changes only
  key construction: eight distinct families with four close sibling keys each.
  Every target therefore retains three similarly named distractors without the
  entire namespace being nearly identical.
- V3 may become a freeze candidate only at 75%-95% overall C1-W retrieval with
  at least 50% C1-W retrieval at every depth. It writes only to
  `CSE407_llama_track_a_pilot_v3_discarded/`.

Pilot V3 update (2026-08-03):

- V3 completed but was harder: C1-W scored 25% and C2 scored 16.7%; C1-W was
  75% at 10% depth and 0% at both 50% and 90%. It is discarded.
- Four siblings per target overconstrained exact binding. Fourteen of nineteen
  wrong outputs were document distractor codes. One C1-W pass became a C2 miss
  despite correct target-first-token rank, a useful cache-continuation flip but
  not enough to rescue the invalid benchmark difficulty.
- `04_llama_hard_retrieval_pilot_v4.ipynb` keeps 32 records and uses mostly
  distinct semantic keys plus six controlled near-name pairs across the whole
  document. The existing overall and per-depth freeze gates remain unchanged.

Pilot V4 acceptance (2026-08-03):

- V4 passed the declared gate: C1-W and C2 each scored 75% overall; C1-W scored
  100%, 50%, and 75% at 10%, 50%, and 90% depth respectively.
- All 24 rows, paired prompt hashes, exact lengths, and cache-path checks passed.
  The three C1-W misses were shared by C2. One correct C2 response added a
  period, counted correctly as primary retrieval success but exact-format
  failure.
- The complete 60-prompt semantics and Llama tokenization are frozen in
  `research/frozen_hard_retrieval_v4.json`. Pilot result rows remain discarded;
  only the accepted generator and prompt hashes carry into the full run.
- Do not tune prompts further after this point. The next notebook must assert
  the frozen hashes before exposing C3-Ref or C4-Ref outcomes.

Purpose:

The current task is too easy because it repeats four filler sentences and places
all four code records in one compact block. A harder benchmark is required to
measure whether compression loses important information.

Required protocol:

- Context: 4096 input tokens for the focused Llama follow-up.
- Depths: 10%, 50%, and 90%.
- Scenarios: 20 independent scenarios per depth.
- Core run size: 60 scenarios per configuration.
- Core configurations: C0, C1-W, C2, C3-Ref, and C4-Ref.
- Total core quality runs: 300.
- Use 32 to 64 separated key-code records per document.
- Use diverse paragraphs instead of a repeated four-sentence loop.
- Place only the requested target record at the declared depth.
- Include similarly named keys and identically formatted wrong codes.
- Put the complete question after the document and within the final 32 input
  tokens so the eviction selector can use the task query.
- Use deterministic greedy decoding.
- Keep exact input length assertions.

Primary scoring:

- Extract every code-shaped answer from the response.
- Pass only when exactly one unique extracted code equals the target.
- Treat multiple-code, wrong-code, truncated-code, and no-code outputs as distinct
  failure categories.

Secondary scoring:

- Exact-format correctness.
- Legacy target-anywhere correctness for comparison with the v5 result.
- Output length.
- Correct-answer token log probability after the first generated token.

Prompt integrity gates:

- Target answer appears exactly once in the document.
- Every distractor code is unique.
- The answer does not leak into filler or instructions.
- Target depth is measured in token space.
- Every configuration receives identical input IDs within one model.
- Prompt manifest and token IDs are hashed into the experiment fingerprint.

Pilot rule:

- Run 10 to 15 discarded C1-W/C2 pilot scenarios first.
- Aim for roughly 75% to 95% C1-W retrieval.
- If both remain at 100%, increase distractor density or similarity.
- If C1-W falls below roughly 70%, reduce difficulty.
- Freeze the generator before inspecting C3-Ref or C4-Ref results.

Completion gate:

- A frozen prompt manifest exists and the benchmark is neither trivial nor
  impossible for the matched AWQ baseline.

### A2. Add Experimental Controls and Model-Behavior Robustness

Status: COMPLETED

Implementation note (2026-08-03):

- `experiments/track_a_failsafe_colab/05_llama_full_quality_control_v1.ipynb`
  implements the frozen 300-case quality matrix, C1-S/C1-W parity gates, deep
  cache validation, and five-block C1-W energy control under fingerprint
  `106a561c07c62937`.
- The executed notebook completed without errors. Its 324-file artifact bundle
  contains 300 quality shards, five energy shards, five traces, and complete
  analysis outputs. `analysis/final_integrity.json` passed all acceptance gates.
- C1-S/C1-W logits, top-1 predictions, greedy tokens, responses, and cache
  lengths matched exactly on all three parity probes.
- C1-W energy at 4096 was 639.86 +/- 5.48 J across five blocks. This is a
  cross-session descriptive wrapper-overhead control, not a paired v5 contrast.
- C2, C3-Ref, and C4-Ref each scored 37/60 versus 38/60 for C1-W. None was
  statistically distinguishable from C1-W; do not claim formal 5-point
  non-inferiority because the two-sided interval reaches the -5-point boundary.

Required conditions:

- C1-S: stock AWQ attention.
- C1-W: AWQ through the same custom wrapper used by C2-C4, with no eviction and
  no TurboQuant.

Inference-only parity tests:

- Compare C1-S and C1-W logits on fixed prompts.
- Compare top-1 token agreement.
- Compare greedy generated responses.
- Verify identical cache lengths and no eviction/quantization state.
- Set a numerical tolerance before viewing results.

Compression robustness tests:

- Compare C1-W, C2, C3-Ref, and C4-Ref on identical hard scenarios.
- Report paired prediction flips, not only aggregate accuracy.
- Report correct-answer negative log-likelihood after the first output token.
- Report response truncation and instruction-following failures separately.
- Measure numerical distortion at early, middle, and late layers if runtime
  permits; the v5 diagnostic sampled only an early-layer KV collection.

Minimal systems control:

- Measure C1-W at 4096 tokens for five energy blocks.
- This is the only mandatory new Llama energy condition in Track A.
- Use C1-W rather than stock C1 in the clean AWQ-path interaction contrast.

Reason:

Inference parity can show that the wrapper preserves answers, but only an energy
measurement can quantify wrapper energy overhead. Without C1-W energy, the
current interaction remains configuration-level and wrapper-confounded.

Completion gate:

- C1-S/C1-W behavior parity is documented, and the 4096-token wrapper overhead
  has a measured estimate.

### A3. Add Statistical and Power Robustness

Status: COMPLETED

Quality analysis:

- Report Wilson 95% intervals for each configuration and depth.
- Use paired, depth-stratified bootstrap intervals or an exact paired method for
  C2-C1-W, C3-Ref-C1-W, and C4-Ref-C1-W differences.
- If retaining the five-percentage-point non-inferiority claim, predeclare the
  margin and use a one-sided paired procedure.
- Do not use zero sample SD as evidence of zero population uncertainty.

Completion note (2026-08-03):

- Notebook 5 produced Wilson intervals for retrieval, format, and legacy
  target-anywhere outcomes; paired flip tables; Bonferroni-adjusted exact tests;
  and depth-stratified paired bootstrap intervals.
- Notebook 5 completed the bounded quality component; Notebook 06 subsequently
  completed the immutable-trace and sensitivity components.

Power completion note (2026-08-04):

- Notebook 06 verified 95 v5 and five C1-W traces against both source manifests.
- Raw integration matched stored joules within `1.14e-13` J maximum error.
- Overall 82 W clipping changed integrated energy by 0.148%; 70 W clipping changed
  it by 1.332%. All registered rankings and significance decisions were stable.
- Historical C1 versus C1-W remains descriptive because session and prompt/workload
  differ; it is not an isolated wrapper-overhead estimate.

Power analysis from existing traces:

- Preserve raw joules as primary.
- Reintegrate every trace with raw power.
- Reintegrate with samples capped at 82 W.
- Reintegrate with samples capped at 70 W.
- Report the maximum raw reading and the count of samples above each threshold.
- State whether rankings and significant contrasts change.

Sensitivity analysis:

- Add descriptive or paired comparisons for Pyramid budgets 512/1024/1536.
- Add descriptive comparisons for TurboQuant numerical 2/3/4-bit settings.
- Keep the interpretation clear: TurboQuant 0.2.0 uses one uint8 index per
  coordinate for all three settings.

Completion gate:

- Quality plots use bounded uncertainty and the paper contains a raw-versus-capped
  energy robustness table.

### A4. Build the Qwen2.5-3B Reference-Path Replication

Status: COLAB EXECUTION PENDING; LOCAL REFERENCE VALIDATED

Purpose:

Test whether the Llama conclusions generalize to a similarly sized model with a
substantially smaller KV geometry.

Required setup:

- [x] Pin exact Qwen2.5-3B FP16 and AWQ checkpoints and revisions.
- [x] Confirm architecture, RoPE, cache semantics, and attention signatures for
  the pinned Transformers version.
- [x] Implement and statically validate a Qwen-specific attention adapter in
  Notebook 07 under fingerprint `91def77c920729e9`.
- [x] Execute Notebook 07 on a T4 and accept its five-file artifact bundle after
  exact parity and all registered cache-path gates passed.
- [x] Execute Notebook 08 under fingerprint `861d89617e53034d` and accept its
  593-file artifact bundle after all final-integrity gates passed.
- Use the unified wrapper for all main AWQ configurations from the beginning.
- Add a stock-versus-wrapper parity gate before any measurements.
- Reuse the same semantic retrieval scenarios, but tokenize and pad independently
  to exact Qwen context lengths.
- Use a completely separate schema, fingerprint, directory, and trace namespace.

Main Qwen configurations:

- Q0: FP16 matched baseline.
- Q1-S: stock AWQ parity control only.
- Q1-W: matched-wrapper AWQ baseline for the full matrix.
- Q2: AWQ + custom pyramidal eviction.
- Q3-Ref: AWQ + TurboQuant 0.2.0 reference path.
- Q4-Ref: AWQ + eviction + TurboQuant reference path.

Required validation:

- Model architecture and revision.
- Wrapper parity.
- Layer-by-layer cache lengths.
- Eviction budgets.
- TurboQuant indices, norms, residuals, and reconstructed values.
- Alias-deduplicated live storage.
- Active use of the modified cache during decode.
- Exact prompt and fixed decode lengths.

Completion gate:

- [x] Qwen passed all gates and produced 75 core energy, 20 sensitivity energy,
  95 trace, 300 core quality, and 60 sensitivity-quality rows without
  contaminating Llama artifacts.
- [x] Every trace hash and reintegration matched; all CSV snapshots matched JSON
  shards; the 591-entry artifact manifest had zero mismatches.
- Execution caveat: two repair cells were applied in-session and are now inline
  in the exported notebook, but the experiment fingerprint does not bind their
  source bytes.

### A5. Cross-Model Synthesis

Status: COLAB EXECUTION PENDING; LOCAL REFERENCE VALIDATED

Completion note (2026-08-05):

- A local CPU-only reference completed under provisional fingerprint
  `b19adce0924b4203`; it is not the authoritative Colab run.
- Its 41-file bundle passed 36 source gates, reconstructed all 195 accepted
  traces, and kept empirical, realized-reference, and ideal-counterfactual
  evidence separate.
- Independent review found no blocking, high, or medium issues.
- Ideal energy remains symbolic; the provisional analysis does not claim measured
  packed/fused energy, latency, power, or peak VRAM.

Required analysis:

- Validate all schemas, fingerprints, row counts, and traces before joining data.
- Compare relative changes within each model rather than only absolute values.
- Normalize cache results by analytical KV byte-token and observed live byte-token.
- Compare whether eviction benefit appears later or weaker on Qwen, whose KV cache
  is much smaller per token than Llama's.
- Compare C4-Ref interaction direction across models.
- Rebuild energy-quality Pareto frontiers using harder retrieval and bounded
  quality intervals.
- Report model-specific outcomes rather than attributing every difference to
  architecture alone.
- Add a realization-gap analysis with three explicit evidence tiers: measured
  systems results, realized TQ-Ref storage/execution, and ideal packed/fused TQ.
- Validate the ideal byte formula by reproducing observed FP retained bytes and
  uint8 package payloads before projecting nominal packed bits.
- Separate observed numerical, storage-only, and quality/energy/Pareto
  eligibility; unobserved low-bit compounds receive storage rows only.
- Compute modeled compulsory/logical fixed-decode byte demand, explicitly not
  hardware DRAM traffic, and the indexed energy break-even surface
  `O_net < epsilon_mem * Delta_D`; do not invent an exact ideal-energy point.
- Add a separate prefill byte-demand model that preserves full attention before
  eviction. Permit total-energy projection only when prefill and decode demands
  are both modeled; otherwise report decode-energy projection only.
- Prove persistent-KV memory dominance only under stated representation and
  budget assumptions; do not equate it with total peak VRAM or lower watts.
- Restrict quality projections to observed nominal-bit numerical paths. Exclude
  low-bit compound paths and task-incomparable Llama low-bit quality from hard-
  quality Pareto claims; use common-15 scenarios for Qwen TQ2/TQ3/TQ4.
- Use TQ-Ref retrieval as unchanged only under strict output equivalence;
  otherwise model implementation-induced quality change as unidentified.
- Solve quality-constrained optimality across `A_min`, memory-energy parameters,
  and both models rather than selecting one universal configuration.
- Report point-estimate feasibility separately from exclusive interval states:
  feasible, uncertain, and infeasible.
- Produce point, conservative lower-bound, and possible upper-bound frontiers;
  use conservative feasibility for primary deployment claims.
- Produce empirical, conditional-ideal, and robust Pareto frontiers separately.
  Keep projected latency out unless a separate valid model is introduced.
  Report min/max bootstrap selection frequency over bounded parameters; never
  call it truth probability or call an arbitrary grid fraction a probability.
- Resample energy and quality independently; preserve block pairing only within
  source sessions and paired scenario IDs within depth strata.

Completion gate:

- The final paper has a coherent cross-model answer for energy, storage,
  throughput, retrieval, and implementation realization.
- The final paper distinguishes mathematically proved packed-memory results,
  conditional energy break-even results, and empirically measured outcomes.
- Every projected Pareto point is visibly labeled as counterfactual and carries
  both sampling uncertainty and realization-parameter sensitivity.

### A6. Final Paper and Reproducibility Package

Status: PENDING

Required paper changes:

- Replace broad TurboQuant claims with reference-path wording.
- Separate numerical validity from representation, residency, and deployment
  utility.
- Use C1-W for matched AWQ-path causal language.
- Treat C0 comparisons as descriptive if model-resident phases remain separate.
- Report the easy v5 NIAH result as historical and the hard benchmark as primary.
- Include the missing joint-method baseline as a limitation unless a genuine
  compatible implementation is run.
- State that a T4 is constrained data-center hardware, not an edge device.
- Compile on Overleaf with Biber and resolve visual issues.

Reproducibility package:

- Source notebooks without embedded secrets.
- Executed notebooks or immutable output artifacts.
- Environment manifests.
- Prompt manifests.
- CSV schemas and fingerprints.
- Power traces.
- Analysis scripts.
- README with exact execution order.

Completion gate:

- A third party can identify every result's model, code path, backend, schema,
  prompt set, and raw artifact.

## 7. Optional Demographic Fairness Audit

Status: OPTIONAL

Do not make social fairness a Track A blocker unless required by the course.
Generic quantization-bias studies already exist, so a small fairness benchmark is
not major novelty by itself.

If included:

- Call matched configuration testing "experimental controls," not social fairness.
- Use one established benchmark such as a cache-sensitive adaptation of BBQ or
  DiscrimEvalGen.
- Ask whether compression amplifies baseline disparity, not whether the model is
  universally fair.
- Use C1-W as the behavioral baseline.
- Ensure the measured answer is produced after the compressed cache is active;
  short first-token classification can bypass the relevant cache effect.
- Run inference only; no fairness-specific energy matrix is needed.

## 8. Track A Definition of Done

Track A is complete when all of the following are true:

- Existing Llama artifacts remain intact and registered.
- Harder retrieval is complete with bounded uncertainty.
- C1-W behavior parity and five-block 4096 energy are complete.
- Raw/capped power robustness is reported.
- Qwen reference-path replication is complete or a documented technical blocker
  is demonstrated.
- Cross-model results are synthesized.
- The paper uses accurate method names and claim boundaries.
- The final artifacts are reproducible and clearly separated by experiment.

## 9. Immediate Next Actions

1. Preserve an exported executed copy of Notebook 07; the five validated JSON
   artifacts are already accepted and immutable.
2. Treat `CSE407_qwen_track_a_reference_v1/` as immutable accepted evidence.
3. Run `09_cross_model_synthesis_v1_colab.ipynb` in a Colab CPU runtime.
4. Independently validate and register its `CSE407_cross_model_synthesis_v1/` output.
5. Preserve unmatched baseline/session and tokenizer-materialization caveats.
6. Complete the reproducibility package and Overleaf layout review.
