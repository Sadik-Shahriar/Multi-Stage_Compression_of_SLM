# Completed Notebook 09 Prompt

> Status: a local reference run completed under provisional fingerprint
> `b19adce0924b4203`, but the authoritative Colab execution is pending. Run
> `experiments/track_a_failsafe_colab/09_cross_model_synthesis_v1_colab.ipynb`
> in a Colab CPU runtime. It reads prior artifacts from the flat MyDrive root and
> writes `/content/drive/MyDrive/CSE407_cross_model_synthesis_v1/`, which must not
> already exist.

Continue the CSE407 SLM energy-ablation project after the accepted Llama and
Qwen2.5-3B Track A runs. Read these files first:

- `AGENTS.md`
- `research/experiment_registry.json`
- `context/session_history/fail-safe-completion-plan.md`
- `context/session_history/current-research-context-and-findings.md`
- `experiments/track_a_failsafe_colab/README.md`
- `evidence/accepted/bundles/CSE407_llama_v5_final/v5_final_environment.json`
- `evidence/accepted/bundles/CSE407_llama_track_a_full_v1/analysis/final_integrity.json`
- `evidence/accepted/bundles/CSE407_llama_power_robustness_v1/analysis/final_integrity.json`
- `evidence/accepted/bundles/CSE407_qwen_track_a_reference_v1/analysis/final_integrity.json`
- `evidence/accepted/bundles/CSE407_qwen_track_a_reference_v1/artifact_manifest.json`
- `evidence/accepted/bundles/CSE407_qwen_track_a_reference_v1/analysis/analysis_provenance.json`
- `experiments/track_a_failsafe_colab/08_qwen2_5_full_reference_v1.ipynb`

Do not use archived Qwen3 or Qwen2.5-1.5B notebooks as current evidence.

## Accepted Qwen State

Notebook 08 completed successfully on a Tesla T4 and its artifacts passed an
independent integrity audit:

- Schema: `track-a-qwen-full-reference-v1-2026-08-04-1`
- Fingerprint: `861d89617e53034d`
- Session: `20260804T154752-97822cdb`
- Executed notebook SHA-256:
  `28089774e7abd540ff385f08d3acb729e0c0263f2ee048d6d02fe927295a1629`
- Artifact-manifest SHA-256:
  `975cb8f19405f9d7e4267bc4a8143ead943c853776c6ba88b8697695ac78c1c9`
- Validation SHA-256:
  `f05ef59b3eb3679b7de9a78a1f22f96c37430e50afad377612cdbd2c0b3b94be`
- Analysis-input SHA-256:
  `fd44a27a71e7370e4735dae3ae66b4b285dfcfd9741c3000d0bd51230dc0f971`
- 75 core energy rows, 20 sensitivity energy rows, and 95 raw traces
- 300 core quality rows and 60 sensitivity-quality rows
- 455 unique measurement keys and zero Q1-S measurement rows
- All 95 traces hash-matched and reintegrated with zero energy discrepancy
- All JSON shards matched their CSV snapshots
- All 591 artifact-manifest entries matched byte size and SHA-256
- Raw, 82 W, and 70 W rankings and significance decisions were stable

Treat `evidence/accepted/bundles/CSE407_qwen_track_a_reference_v1/` as immutable accepted evidence.

## Qwen Findings To Preserve

At 4096 tokens:

| Variant | Mean raw energy | Hard retrieval |
|---|---:|---:|
| Q0 | 616.78 +/- 6.79 J | 53/60 |
| Q1-W | 621.75 +/- 25.14 J | 48/60 |
| Q2 | 550.48 +/- 10.07 J | 1/60 |
| Q3-Ref | 812.28 +/- 13.11 J | 49/60 |
| Q4-Ref | 628.69 +/- 9.77 J | 1/60 |

- Q2 reduced mean energy by 71.27 J relative to Q1-W, but the Holm-adjusted
  total-energy result narrowly missed 0.05 (`p=0.06556`) and retrieval collapsed.
- Q3-Ref preserved Q1-W-like retrieval but added 190.53 J; its energy and
  throughput penalties were significant after Holm correction.
- Q4-Ref had Q2-like retrieval failure. Its energy was close to Q1-W because
  prior eviction shielded the TQ-Ref overhead, not because TQ-Ref was free.
- The compound interaction was significant for total and decode energy under
  raw, 82 W, and 70 W integrations.
- TQ-Ref is numerical, materialized-K/V, and unfused. Its 2/3/4-bit settings all
  use one uint8 index per coordinate and are not physically packed caches.

## Provenance Caveat

Notebook 08 required two in-session repairs:

1. A quality-validator field-name correction.
2. A capped-analysis Pandas merge correction.

The exported notebook contains both successful fixes inline and the persisted
measurement/analysis artifacts are internally complete and hash-consistent.
However, fingerprint `861d89617e53034d` and the artifact manifest do not
cryptographically bind the executed notebook or repair-cell source. State this
as a reproducibility/provenance caveat, not as a measurement-integrity failure.

The persisted `qwen_full_environment.json` also retains the stale descriptive
status `VALIDATION_PASSED_MEASUREMENTS_PENDING`; the authoritative acceptance
marker is `analysis/final_integrity.json`.

## Immutable Evidence

Never modify or write into:

- `evidence/accepted/bundles/CSE407_llama_v5_final/`
- `evidence/accepted/bundles/CSE407_llama_track_a_full_v1/`
- `evidence/accepted/bundles/CSE407_llama_power_robustness_v1/`
- `evidence/accepted/bundles/CSE407_qwen_track_a_adapter_pilot_v1/`
- `evidence/accepted/bundles/CSE407_qwen_track_a_reference_v1/`
- Any discarded pilot directory

## Immediate Task

Build a self-contained CPU-only Google Colab notebook:

`experiments/track_a_failsafe_colab/09_cross_model_synthesis_v1_colab.ipynb`

It must read accepted Llama and Qwen evidence without changing either bundle,
validate both sides before analysis, and write only to a new isolated directory:

`CSE407_cross_model_synthesis_v1/`

Do not collect new GPU measurements in Notebook 09.

## Mandatory Synthesis Requirements

1. Validate source directory names, schemas, fingerprints, final-integrity
   markers, manifest hashes, row counts, unique keys, and trace availability
   before joining any data.
2. Treat JSON shards and raw traces as canonical. Verify CSV correspondence or
   rebuild in-memory normalized tables without modifying accepted files.
3. Compare within-model relative changes first. Do not treat absolute Llama and
   Qwen joules as paired observations.
4. Preserve the baseline asymmetry:
   - Historical Llama systems energy uses stock C1 across all contexts.
   - Qwen systems energy uses matched-wrapper Q1-W across all contexts.
   - Llama has a separate five-block C1-W control only at 4096 tokens.
   Any wrapper-controlled 4096 comparison spanning Llama experiments is
   descriptive because the sessions were separate.
5. Use semantically matched hard-retrieval scenarios, but acknowledge that each
   model has tokenizer-specific exact 4096-token prompt materialization.
6. Report raw joules as primary and 82 W/70 W reintegrations as sensitivity
   analyses. Do not describe clipped integrations as hardware-cap reruns.
7. Compare at least:
   - Energy and throughput versus context for corresponding core paths.
   - Within-model AWQ-to-eviction and AWQ-to-TQ-Ref effects at 4096.
   - Hard-retrieval rates with Wilson intervals.
   - Eviction quality collapse differences across models.
   - Sequential compound interaction direction and uncertainty.
   - Raw/capped ranking and significance stability.
   - Analytical retained KV bytes and alias-deduplicated live storage, normalized
     by model KV geometry where valid.
   - Energy-quality Pareto frontiers with bounded or bootstrap uncertainty.
8. Preserve model-specific labels in source tables. Introduce a clearly defined
   normalized mapping only in derived synthesis tables.
9. Do not infer that architecture alone caused cross-model differences. The
   study has one T4, one run/session per major experiment, model-specific
   adapters, and unmatched baseline/session structure.
10. Keep Q0 cross-phase comparisons descriptive and TQ-Ref claims limited to the
    accessible reference implementation.
11. Add the registered ideal-TurboQuant realization-gap analysis defined below.
    Keep every projected result separate from empirical measurements.
12. Produce machine-readable synthesis CSV/JSON outputs, publication-ready
    figures, a concise findings Markdown report, and a final integrity JSON.
13. Bind Notebook 09's input file hashes, analysis protocol, source hash, output
    hashes, and final inventory so the synthesis can be reproduced exactly.
14. Fail closed on any evidence mismatch. Do not silently repair or rewrite an
    accepted source artifact.

## Ideal-TurboQuant Realization-Gap Analysis

This is a counterfactual analytical extension, not a new measured experiment.
Its novel contribution is to separate three levels that are usually conflated:

1. Measured FP16/AWQ/eviction systems behavior.
2. Measured numerically active TQ-Ref behavior with uint8 indices, materialized
   K/V, and unfused execution.
3. An ideal packed/fused realization that preserves the same quantized
   reconstruction but removes materialized global-memory K/V and packs indices
   at their nominal bit width.

Do not call TQ-Ref a simulation. Call it a numerically active reference path.
Do not call the ideal realization measured, observed, or validated hardware.

### A. Exact Packed-Memory Model

Fix batch size at one. For model `m`, layer `l`, retained tokens `B_ml`, KV
heads `H_m`, head dimension `d_m`, FP element bytes `s_fp`, nominal index width
`q`, residual window `r_ml = min(r, B_ml)`, norm bytes `s_norm`, packing
alignment `a`, and layer/configuration-specific metadata `M_meta(m,l,q,B_ml)`,
compute the unaligned logical payload first:

```text
M_KV_FP(m) = 2 * H_m * d_m * s_fp * sum_l(B_ml)

M_KV_ideal_logical(m, q) = 2 * H_m * sum_l(
    (B_ml - r_ml) * (d_m * q / 8 + s_norm)
    + r_ml * d_m * s_fp
)
```

Then construct every actual projected tensor category with `align_up(bytes, a)`
and add `M_meta(m,l,q,B_ml)` at tensor/layer granularity. Use layerwise budgets,
not only the average budget. Report both unaligned logical payload and aligned
projected allocation in decimal MB and MiB.

Validate the accounting before using it:

- The FP formula must reproduce stored analytical retained-FP bytes.
- The same logical formula at eight physical index bits must reproduce the
  package-reported TQ payload for observed rows using one uint8 index per
  coordinate, using direct tensor shapes and dtypes rather than trusting only a
  previously calculated summary field.
- Numerical/quality/energy projection at nominal `q` is allowed only for the
  same observed `(model, variant, tq_bits)` path. A four-bit index stream must
  never be relabeled as two or three bits. Purely algebraic storage-only rows may
  be generated for unobserved bit/configuration combinations only when they are
  explicitly ineligible for quality, energy, and Pareto projection.
- Materialized K/V must be included in the realized-reference column and removed
  only in the explicitly ideal column.
- Assert monotonicity in nominal bit width and retained-token budget.

The notebook may prove projected persistent-KV memory dominance only when the inequality
follows from these definitions. Under the same AWQ weights and same retained
tokens, packed `q < 16` is lower than FP16 only if index savings exceed norms,
residuals, alignment, and metadata. State and verify this condition. Do not
equate persistent KV bytes with total peak VRAM, because weights, allocator
reserves, kernels, and temporary workspace remain.

Create an explicit eligibility matrix before projection:

- Include separate booleans `observed_numerical_path`,
  `storage_only_eligible`, and `quality_energy_pareto_eligible`, plus a reason.

- Both models: hard-quality-constrained core analysis is allowed only for the
  observed four-bit Q3/C3 and Q4/C4 numerical paths.
- Qwen: TQ-only 2/3/4-bit quality comparison is allowed only on the common 15
  sensitivity scenarios for every bit width.
- Llama: historical 2/3-bit quality used a different/easier task and must not be
  mixed into the frozen hard-retrieval Pareto analysis.
- Neither model has observed numerical 2/3-bit compound Q4/C4 quality. Such
  footprints may be shown only as storage-only counterfactuals with quality
  marked unknown, no projected energy, and
  `quality_energy_pareto_eligible=false`.

### B. Modeled Phase Byte Demand

Compute prefill and decode compulsory/logical byte demand separately.

For prefill, preserve the actual algorithm order: full-prompt attention occurs
before eviction, then retained K/V is stored or quantized. Count only dataflow
differences justified by that order, including retained K/V writes, packed
index/norm/residual writes, and any materialized reconstruction writes. Do not
claim compressed attention reads during prefill when full-prompt attention used
uncompressed K/V.

For the fixed 64-token decode, for every decode step and layer,
account separately for the growing retained sequence, K and V attention reads,
packed index reads, norm reads, residual FP reads, new-token writes,
residual-to-packed transitions, and any ideal materialization writes. Assume
reconstructed vectors remain in registers/shared memory only in the ideal fused
case; label this assumed dataflow explicitly.

Export exact byte counts under this algorithmic dataflow model for FP and ideal
packed paths. Do not claim exact hardware DRAM traffic: the artifacts do not
identify cache hits, SDPA tiling, compiler fusion, GQA expansion traffic, or
allocator copies. Realized-reference hardware traffic is unknown; only its
logical compulsory demand may be modeled. Export `Delta_D_prefill`,
`Delta_D_decode`, and `Delta_D_total = Delta_D_prefill + Delta_D_decode` relative
to the corresponding non-TQ dataflow. Decode-energy projection uses only
`Delta_D_decode`; prefill uses only `Delta_D_prefill`; total-energy projection is
allowed only when both phase models pass and uses `Delta_D_total`.

### C. Energy Break-Even, Not Fabricated Joules

Use the partially identified model:

```text
E_ideal[m,b,v,q,c,phase,s,regime] = E_baseline[m,b,c,phase,s,regime]
    - epsilon_mem[m,b,c,phase,s,regime] * Delta_D[m,v,q,c,phase]
    + O_net[m,b,v,q,c,phase,s,regime]
```

where `b` is the corresponding baseline path, `s` is the source session, and
`regime` is raw/82 W/70 W integration. Raw is primary; any capped projection is
a separate sensitivity surface. `epsilon_mem` is path/session/regime-specific
effective joules per avoided modeled byte and `O_net` is non-traffic incremental energy: rotation,
packing/reconstruction compute, launch/control effects, occupancy/runtime
changes, and changed background/static energy. All modeled index/norm/residual
memory traffic must be included in `Delta_D` and must not be charged again in
`O_net`. Derive and export both equivalent break-even conditions only when
`Delta_D > 0`:

```text
O_net < epsilon_mem * Delta_D
epsilon_mem > O_net / Delta_D
```

Use the corresponding non-TQ configuration as the baseline: Q1-W/C1-W (or the
registered AWQ baseline where wrapper matching is unavailable) for TQ-only, and
Q2/C2 for eviction-plus-TQ. Preserve all cross-session baseline caveats.

The zero-net-overhead case `O_net = 0` is a reference envelope, not necessarily
the physical best case and not a claim that real quantization is free. It
establishes strict energy reduction only when `epsilon_mem > 0` and `Delta_D >
0`. It cannot prove lower instantaneous or peak power. Keep watts, joules, and
runtime distinct.

Report the zero-net-overhead, perfectly packed result as a reference envelope.
Do not describe it as an achievable or absolute best point unless a real kernel
later measures it and the remaining parameter domain justifies that statement.

Require `epsilon_mem >= 0`, `Delta_D > 0` before division, and
`E_ideal >= 0`. Do not choose an unsupported single value for `epsilon_mem` or
`O_net`. Every finite parameter domain must be justified and fingerprinted;
otherwise keep the result symbolic and do not generate a numerical energy Pareto
point. Unbounded arbitrary parameter regions are not admissible analyses.
Notebook 09 must provide:

- A parameter-free break-even surface.
- A zero-net-overhead reference envelope.
- A literature-bounded sensitivity region only if every numerical bound is
  verified from a citable source and recorded in the assumptions manifest.
- An optional empirical marginal-energy model only as a sensitivity analysis,
  with its confounding assumptions and uncertainty stated; never treat it as a
  hardware constant.

### D. Quality Counterfactual

Use measured TQ-Ref retrieval as an unchanged-quality proxy only in a strict
output-equivalence scenario: same observed nominal-bit path, indices, norms,
residual policy, reconstructed K/V, eviction order, accumulation precision,
reduction order, logits, and greedy outputs. Similar reconstruction or ordinary
rounding alone does not guarantee identical retrieval. Outside this strict case,
implementation-induced quality change is unidentified and must be represented
as an unknown structural parameter, not assumed zero.

Do not assume implementation changes can repair eviction quality. Conditional on
strict output equivalence, ideal Q4 inherits Q4-Ref's observed scenario outcomes;
Q2 is only the corresponding non-TQ energy baseline and corroborating eviction-
collapse evidence. Qwen Q3-Ref preserves Q1-W-like retrieval. Compute the unidentified
quality-change margin at which each eligible projected configuration changes
feasibility, rather than assigning an arbitrary penalty.

### E. Quality-Constrained Optimality

Define the deployment problem without a subjective weighted score:

```text
minimize (conditional_energy, projected_persistent_KV_bytes)
subject to retrieval_rate >= A_min
```

Evaluate optimality over the full predeclared quality-threshold axis `A_min`, not
only one convenient threshold. Produce regions identifying which configuration
is feasible and non-dominated as `A_min`, `epsilon_mem`, `O_net`, and any
unidentified quality-change parameter vary. Keep latency/throughput only on the
empirical measured frontier; no fused packed latency model is identified by the
accepted artifacts.

For every `A_min`, store `point_estimate_feasible = (estimate >= A_min)` as a
separate boolean. Also export one exclusive interval state: `feasible` when
`lower >= A_min`; `uncertain` when `lower < A_min <= upper`; and `infeasible`
when `upper < A_min`. Use the common 15 scenarios for every Qwen 2/3/4-bit
comparison and keep its 60-scenario four-bit estimate as a separate analysis.

Produce three quality-filtered projected frontiers at every `A_min`:

- Point frontier: admit configurations with `estimate >= A_min`.
- Conservative frontier: admit configurations with `lower >= A_min`.
- Possible frontier: admit configurations with `upper >= A_min`.

Label the conservative frontier as primary for deployment claims. Never mix the
three feasibility rules in one frontier.

The notebook may prove the lowest persistent-KV option under explicit fixed
budget/bit assumptions. It must describe energy winners as conditional regions
unless all terms are empirically identified. It must not claim one universal
best configuration when Qwen eviction fails the quality constraint.

### F. Uncertainty-Aware Projected Pareto

Produce three visibly and machine-readably separate Pareto products:

- Empirical measured frontier using only observed systems points.
- Conditional ideal frontier at each declared realization scenario.
- Robust optimality summary across the full admissible parameter region.

For each fixed, numerically bounded realization scenario, independently
bootstrap energy and quality because they have no shared sampling unit. Preserve
registered block pairing only within a source experiment/session; resample
different sessions and models independently. For quality, resample paired
scenario IDs across compared configurations within depth strata. Keep common-15
Qwen bit-width comparisons paired on exactly those IDs. Then report
`bootstrap_frontier_membership_frequency`, interpreted only as resampling
selection stability. Across bounded unknown realization parameters, report the
minimum and maximum conditional bootstrap frequency and whether a point is
non-dominated for all, some, or none of the declared region.

Do not call bootstrap frequency the probability that a point belongs to the true
population frontier. Do not call the fraction of an arbitrarily spaced parameter grid a probability.
Only integrate over parameter values if a predeclared, justified distribution is
recorded. Otherwise report dominance regions, interval bounds, and scenario
sensitivity. Plot projected points with hollow/dashed markers and never merge
them into the empirical frontier without an explicit `evidence_tier` field.

### Required Counterfactual Outputs

- `ideal_tq_assumptions.json`
- `counterfactual_eligibility.csv`
- `measured_realized_ideal_storage.csv`
- `ideal_packed_kv_footprint.csv`
- `modeled_phase_byte_demand.csv`
- `energy_break_even_surface.csv`
- `quality_constraint_regions.csv`
- `conditional_ideal_pareto.csv`
- `robust_optimality_regions.csv`
- `realization_gap_summary.md`
- Measured-versus-realized-versus-ideal storage figure
- Energy break-even region figure
- Empirical and projected Pareto figure with distinct evidence styling

All formulas, source fields, units, assumptions, parameter ranges, bootstrap
seeds, and proof-condition assertions must be fingerprinted by Notebook 09.

## Statistical Guidance

- Keep the registered within-model inferential results unchanged.
- For cross-model contrasts, use uncertainty-aware descriptive differences or
  bootstrap distributions unless a genuinely matched sampling unit exists.
- Do not manufacture paired tests from coincident block numbers across separate
  sessions or models.
- Report effect sizes and intervals alongside adjusted p-values.
- Explicitly note that five energy blocks limit Wilcoxon resolution and that the
  Qwen sensitivity-quality subsets contain only 15 scenarios per variant.
- Separate sampling uncertainty from realization-parameter uncertainty. Do not
  convert an unidentified counterfactual into a conventional confidence interval.

## Source Validation Before Handoff

- JSON and `nbformat` validation
- Unique cell IDs and numbered Markdown run order
- Embedded Python syntax validation, excluding notebook magics
- All execution counts null and outputs empty before first execution
- No secrets
- CPU-only dependency set
- No writes into accepted evidence directories
- Deterministic input manifest and analysis fingerprint
- Exact expected synthesis output assertions
- Unit tests showing the byte model reproduces observed FP and uint8 logical
  payloads before projecting packed 2/3/4-bit storage
- Independent review of baseline alignment, counterfactual assumptions,
  conditional claims, Pareto uncertainty, and final integrity

After Notebook 09 is executed and accepted, update the IEEE paper's abstract,
methods, results, discussion, limitations, conclusion, tables, and figures with
the completed cross-model evidence and the Notebook 08 provenance caveat.
