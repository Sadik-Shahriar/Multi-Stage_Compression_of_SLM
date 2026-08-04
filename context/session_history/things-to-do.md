# Project Status and Next Actions

Last updated after the accepted full Qwen2.5-3B reference-path run.

## Experiment Format Rule

- Implement all new experiments as self-contained Google Colab `.ipynb`
  notebooks with proper Markdown cells.
- Do not create standalone `.py` experiment runners.
- Keep each experiment track in a dedicated notebook folder with numeric
  run-order prefixes and isolated Drive output paths.
- Current Track A notebooks are in `experiments/track_a_failsafe_colab/`.

## I. Current Project Narrative

**Project goal:** Measure the physical energy, latency, throughput, memory, and quality interactions of AWQ weight quantization, pyramidal KV-token eviction, and TurboQuant numerical KV quantization on sub-4B language models running on an NVIDIA T4.

**Current implementation:** AWQ + a custom PyramidKV-style eviction path + the independent `turboquant==0.2.0` reference package.

**Current Llama finding:** AWQ plus pyramidal eviction (C2) provides the best tested core systems trade-off at 4096 tokens. TurboQuant-only C3-Ref adds substantial runtime energy and live-storage overhead. Applying eviction before TurboQuant in C4-Ref is associated with much lower overhead than C3-Ref, producing a significant configuration-level non-additivity contrast.

**Important wording boundary:** C4-Ref is a sequential stack, not an implementation of RDKV or ThinKV. The custom eviction path is PyramidKV-style and is not the official KVCache-Factory implementation. TurboQuant bit width is numerical codebook precision in this package, not packed physical 2/3/4-bit storage.

---

## II. Instructor Feedback Status

| Instructor concern | Current status | Remaining action |
|---|---|---|
| Discuss sequential stacking versus joint mathematical optimization | Partially complete | IEEE paper now discusses RDKV/ThinKV and states that C4-Ref is sequential. Expand this discussion in the final paper. |
| Compare against an existing joint eviction-and-quantization method | Not completed | Run a genuine compatible joint method if feasible. Otherwise document the missing baseline as a limitation. Do not use a fake PyTorch dynamic-quantization proxy. |
| Add a Pareto frontier with uncertainty | Implemented | The historical frontier exists and Notebook 5 adds hard retrieval with Wilson intervals and paired uncertainty. Regenerate the final frontier after power robustness. |
| Extend to a second SLM family | Completed | Synthesize the accepted Llama and Qwen evidence without over-attributing architectural causes. |

---

## III. Completed Llama 3.2-3B Work

### Notebook and Artifacts

- [x] Final source notebook: `experiments/Latest/llama3_2_energy_ablation_final_v5.ipynb`.
- [x] Executed notebook: `Latest notebook run output.ipynb`.
- [x] Artifact directory: `CSE407_llama_v5_final/`.
- [x] Experiment fingerprint: `8d27af8c9ee94de3`.
- [x] Schema: `v5-final-2026-07-31-1`.
- [x] Pinned FP16/AWQ model revisions and TurboQuant source hash.
- [x] All notebook sections completed without a Jupyter error or failed assertion.
- [x] Full hard-retrieval/control notebook completed with fingerprint
  `106a561c07c62937`, 300 quality rows, five C1-W energy rows, and passed final
  integrity.

### Core Matrix

- [x] Five configurations: C0--C4.
- [x] Contexts: 1024, 2048, and 4096 tokens.
- [x] Five measured energy blocks per condition.
- [x] 75/75 unique core energy rows.
- [x] 225/225 unique core NIAH rows.
- [x] Fixed 64-token teacher-forced decode workload.
- [x] Separate retrieval correctness and exact-format compliance.

### Sensitivity Studies

- [x] Dynamic `average_budget` and `tq_bits` parameters.
- [x] Pyramid-style budgets 512 and 1536 at 4096, with core C2/1024 as baseline.
- [x] TurboQuant bits 2 and 3 at 4096, with core C3-Ref/TQ4 as baseline.
- [x] 20/20 sensitivity energy rows.
- [x] 60/60 sensitivity quality rows.
- [x] TurboQuant distortion diagnostics for 2, 3, and 4 bits.

### Measurement and Validation

- [x] Approximately 10 Hz NVML sampling.
- [x] 95/95 raw power traces present.
- [x] Every trace reintegrates to its stored joules within floating-point precision.
- [x] Idle-adjusted and gross energy stored separately.
- [x] Prefill and decode energy/timing stored separately.
- [x] Temperature, clocks, power limit, and throttle telemetry stored.
- [x] Post-prefill and post-decode memory stored.
- [x] Deduplicated live cache bytes and logical retention metrics stored.
- [x] Seven mandatory validation paths passed.
- [x] Every one of the 380 primary rows has `structural_pass=True`.
- [x] Unified full-prompt prefill semantics for C2--C4.

### Analysis and Figures

- [x] Core energy summary and paired AWQ-path tests.
- [x] Holm multiple-comparison correction.
- [x] Configuration-level difference-in-differences interaction table.
- [x] Energy-vs-retrieval Pareto frontier with X/Y sample-SD bars.
- [x] Multi-objective empirical mean Pareto table.
- [x] Throughput-vs-energy plot.
- [x] Peak-vs-persistent-memory plot.
- [x] Pyramid-budget and TurboQuant-bit sensitivity plot.
- [x] Figures copied into `proposal/ieee format/` for Overleaf.

### Main Llama Results at 4096

| Config | Mean total energy | Decode throughput | Post-decode live cache | Retrieval |
|---|---:|---:|---:|---:|
| C0 FP16 | 701.08 +/- 8.12 J | 11.34 tok/s | 455.00 MiB | 100% |
| C1 AWQ | 631.25 +/- 5.05 J | 13.77 tok/s | 455.00 MiB | 100% |
| C2 AWQ + pyramidal eviction | **529.30 +/- 20.02 J** | **20.34 tok/s** | **119.00 MiB** | 100% |
| C3-Ref AWQ + TQ-Ref | 913.48 +/- 2.11 J | 7.66 tok/s | 696.50 MiB | 100% |
| C4-Ref sequential compound | 659.50 +/- 21.35 J | 12.53 tok/s | 187.25 MiB | 100% |

### Paper Update

- [x] `proposal/ieee format/ieee_proposal.tex` changed from planned methodology to an executed Llama findings draft.
- [x] Abstract updated with measured results.
- [x] Results, interaction, sensitivity, Pareto, discussion, threats, and conclusion sections added.
- [x] Retrieval ceiling and power-telemetry caveats documented.
- [x] Custom PyramidKV-style implementation disclosed.
- [x] C1 stock-attention versus C2--C4-Ref wrapper confound disclosed.
- [x] Sequential C4-Ref versus joint-method distinction disclosed.
- [x] `\nocite{*}` removed and table checkmarks made LaTeX-safe.
- [ ] Compile the paper on Overleaf with Biber and resolve any visual layout/float issues.

---

## IV. Llama Validity Work Still Needed

### 1. Harder Retrieval Evaluation

- [x] Replace repetitive filler with a larger, semantically diverse distractor corpus.
- [x] Separate target and distractor records rather than placing all codes in one compact block.
- [x] Calibrate and freeze 60 scenarios: 20 per depth with 32 records each.
- [x] Accept V4 at 75% C1-W pilot retrieval with every depth at least 50%.
- [x] Run all 20 frozen scenarios per depth for every final configuration.
- [x] Rerun quality only; the completed energy matrix was not repeated.
- [x] Report bounded quality uncertainty with Wilson and paired bootstrap intervals.
- [ ] Regenerate the retrieval Pareto figure after the harder quality run.
- [ ] Add an exact-format Pareto frontier as a secondary analysis.

### 2. Matched Wrapper Control

- [x] Add C1-W through the custom wrapper with neither eviction nor TurboQuant.
- [x] Measure C1-W at 4096 tokens with five blocks.
- [x] Verify exact C1-S/C1-W parity on fixed probes.
- [x] Use C1-W as the matched behavioral baseline for hard quality comparisons.
- [ ] Keep historical v5 C1 versus new C1-W energy descriptive because the runs
  are from separate sessions rather than paired blocks.

### 3. Power-Telemetry Robustness

- [x] Build and locally validate the self-contained Notebook 06 source against
  all 100 copied immutable traces.
- [x] Execute the robustness notebook/table using raw, 82 W-capped, and 70 W-capped energy.
- [x] Report samples above 70/82/100 W and the maximum 124.496 W reading.
- [x] Confirm that core and sensitivity rankings remain unchanged under both caps.
- [ ] Add the robustness table or appendix figure to the paper.
- [ ] Preserve raw joules as the primary measured result; do not silently overwrite them with capped values.

### 4. Statistical Follow-up

- [ ] Add descriptive or inferential comparisons for the sensitivity conditions.
- [ ] Keep C0-vs-AWQ context results descriptive because C0 ran in a separate model-resident phase.
- [ ] Do not interpret zero retrieval SD as zero population uncertainty.
- [ ] Correct generated test-column labels that use `_j` for seconds and tokens/s if analysis is rerun.

### 5. Documentation Consistency

- [ ] Align C2/C3 names across `AGENTS.md`, `proposal/proposal.md`, `research/research_plan.md`, and any presentation files.
- [ ] Use C2 = AWQ + pyramidal eviction and C3-Ref = AWQ + TQ-Ref consistently for the current experiment.
- [ ] State that the eviction path is custom PyramidKV-style, not official KVCache-Factory PyramidKV.
- [ ] State that TurboQuant 2/3/4-bit settings use one uint8 index per coordinate and identical physical index storage.
- [ ] Complete or clean incomplete bibliography metadata before final submission.

---

## V. Next GPU Task After A3: Qwen2.5-3B Replication

### Notebook Construction

- [x] Build and execute the isolated Qwen adapter/parity pilot; all registered gates passed under fingerprint `91def77c920729e9`.
- [x] Build and statically validate the complete Qwen Notebook 08 without modifying completed Llama artifacts.
- [x] Select and pin the exact Qwen2.5-3B FP16 and AWQ checkpoints.
- [x] Confirm Qwen architecture values, rotary embedding behavior, attention signatures, and cache semantics from the pinned Transformers version.
- [x] Rewrite the attention wrapper for `transformers.models.qwen2.modeling_qwen2.Qwen2Attention.forward`.
- [x] Preserve full-prompt attention before storing full or selected K/V.
- [x] Add a stock-versus-wrapper parity gate before running measurements.
- [x] Port all structural, storage, distortion, telemetry, trace, and resumability gates.
- [x] Use a separate schema, Drive folder, CSV names, trace directory, and fingerprint (`861d89617e53034d`).

### Qwen Experiment

- [x] Use Q1-S only for parity, then run Q0, Q1-W, Q2, Q3-Ref, and Q4-Ref at 1024, 2048, and 4096 tokens with five measured energy blocks.
- [x] Run the same fixed 64-token decode trace.
- [x] Run the frozen harder retrieval protocol: 300 core quality rows.
- [x] Run 4096-token Pyramid-budget and TurboQuant-bit sensitivity.
- [x] Validate every requested path before accepting rows.
- [x] Inspect and reintegrate all 95 power traces; raw/82 W/70 W decisions are stable.
- [x] Accept the 593-file bundle under fingerprint `861d89617e53034d`; preserve the in-session repair/provenance caveat.

---

## VI. Joint-Method Decision

- [ ] Investigate whether an authentic RDKV, ThinKV, or another joint eviction-and-quantization implementation can run fairly on Qwen/Llama with a T4.
- [ ] Match context, retained cache, workload, and quality protocol if a joint baseline is feasible.
- [ ] Do not label sequential SnapKV plus unrelated dynamic weight quantization as a joint KV baseline.
- [ ] If no fair implementation is feasible, document the hardware/software incompatibility and retain the missing baseline as an explicit limitation.

---

## VII. Cross-Model Synthesis

- [ ] Create CPU-only Notebook 09 to read final Llama and Qwen evidence.
- [ ] Validate fingerprints, schemas, row counts, and trace availability before combining results.
- [ ] Produce side-by-side energy-vs-context plots.
- [ ] Produce side-by-side Pareto frontiers with bounded quality uncertainty.
- [ ] Compare interaction contrasts across architectures.
- [ ] Compare raw and capped-energy robustness across architectures.
- [ ] Determine whether the C4 energy-shield pattern generalizes.
- [ ] Reproduce observed FP retained bytes and uint8 TQ logical payloads with a
  unit-tested analytical storage model.
- [ ] Build an eligibility matrix and project only observed nominal-bit paths;
  use separate numerical/storage/Pareto eligibility fields and label unobserved
  low-bit compound footprints storage-only with unknown quality and energy.
- [ ] Project packed KV storage with exact layerwise budgets, tensor alignment,
  norms, residuals, and configuration-specific metadata.
- [ ] Compute modeled compulsory/logical fixed-decode byte demand and indexed
  non-traffic-overhead/memory-energy break-even regions; do not label it measured
  DRAM traffic or fabricate ideal joules/watts.
- [ ] Model prefill separately with full attention before eviction; allow total-
  energy projection only after prefill and decode demand both pass.
- [ ] Evaluate quality-constrained winners across retrieval thresholds rather
  than assuming the most compressed path is universally best.
- [ ] Report point-estimate feasibility separately from exclusive confidence-
  interval states: feasible, uncertain, or infeasible.
- [ ] Build separate point, conservative, and possible quality-filtered
  frontiers, with conservative feasibility primary for deployment claims.
- [ ] Keep projected Pareto objectives to conditional energy and persistent KV;
  latency/throughput remain empirical unless separately modeled.
- [ ] Bootstrap empirical blocks/scenarios for each bounded ideal scenario, then
  report selection-frequency bounds, not truth probabilities, across realization
  parameters.
- [ ] Resample energy and quality independently, preserving pairing only within
  source sessions and within-depth paired quality scenario IDs.
- [ ] Keep measured, realized-reference, and ideal-counterfactual outputs and
  plot markers separate.
- [ ] Update the IEEE paper abstract, results, discussion, limitations, and conclusion with Qwen findings.

---

## VIII. Recommended Execution Order

1. Preserve/export the executed Notebook 07 copy for reproducibility.
2. Keep the accepted Notebook 08 artifact directory immutable.
3. [ ] Run the Colab-ready CPU-only Notebook 09 and accept its Drive artifacts.
   The local fingerprint `b19adce0924b4203` is provisional only.
4. Validate packed-memory proofs, energy break-even regions, quality constraints,
   and empirical versus projected Pareto uncertainty.
5. Compare within-model relative effects and disclose unmatched Llama/Qwen AWQ controls.
6. Decide and document the genuine joint-method baseline outcome.
7. Update the paper and presentation, then compile on Overleaf with Biber.
