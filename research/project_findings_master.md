# Master Project Findings and Paper-Building Record

## Document Status and Evidence Rules

This document is the single long-form record of the CSE407 project, including
research motivation, protocol evolution, successful experiments, failed pilots,
repairs, quantitative findings, counterfactual analysis, limitations, and
remaining work. It is intended to support the final project report or paper.

The document is being written incrementally from validated project sources. The
companion tracker is `research/project_findings_processing_tracker.md`.

Evidence labels used throughout:

- **Accepted measured evidence:** immutable experiment bundles that passed final
  integrity and are registered as accepted.
- **Accepted derived evidence:** analysis based only on accepted measurements
  that passed its own integrity gates.
- **Provisional synthesis:** the local cross-model synthesis under fingerprint
  `b19adce0924b4203`; internally validated but not independently promoted to
  accepted A5 evidence.
- **Accepted visualization:** the downloaded visualization bundle under
  `evidence/accepted/CSE407_cross_model_visualization_v1/`, generated from the
  provisional synthesis. Acceptance of the figures does not promote the source
  synthesis or turn ideal projections into measurements.
- **Discarded pilot evidence:** useful for documenting failures and protocol
  evolution, but excluded from final outcome estimates.
- **Analytical counterfactual:** mathematical packed/fused storage and logical
  byte-demand models; not observed hardware performance.

No claim in this document should call TQ-Ref physically packed or fused. No ideal
energy, latency, throughput, power, or peak-VRAM number is treated as measured.

## Planned Sections

1. Executive summary
2. Project motivation and research gap
3. Research questions and hypotheses
4. Final executed protocol
5. Models, hardware, configurations, and metrics
6. Literature and proposal evolution
7. Llama systems experiment
8. Llama systems findings
9. Failed hard-retrieval pilots and lessons
10. Llama hard-quality and matched-control experiment
11. Power robustness
12. Qwen adapter parity pilot
13. Qwen full reference experiment
14. Qwen findings
15. Cross-model synthesis
16. Ideal TurboQuant realization-gap analysis
17. Visualization products and figure interpretations
18. Statistical interpretation
19. Failures, repairs, and provenance caveats
20. Threats to validity and limitations
21. Reproducibility and artifact map
22. Paper-ready claims and claims that are not supported
23. Remaining work

## 1. Executive Summary

This project investigates whether three nominally complementary compression
methods can be stacked for energy-efficient small-language-model inference on an
NVIDIA T4:

- 4-bit AWQ weight quantization;
- PyramidKV-style KV-token eviction;
- TurboQuant-based KV quantization.

The central engineering problem is multi-objective rather than single-objective.
A useful edge-inference configuration must reduce energy and persistent memory
without destroying retrieval quality or causing unacceptable runtime overhead.
This directly addresses the course requirement for a complex engineering problem
with conflicting requirements: energy, memory, quality, throughput,
reproducibility, and deployment feasibility cannot all be optimized
independently.

The completed project contains accepted measured evidence for Llama 3.2-3B and
Qwen2.5-3B, accepted derived power-robustness evidence, a provisional but
internally validated cross-model synthesis, and an accepted visualization bundle.
The project also records four hard-retrieval calibration pilots, including three
failed pilots that were deliberately discarded rather than reused as final
evidence.

The most important conceptual result is that the accessible TurboQuant package
path and an ideal production implementation are different evidence objects.
TQ-Ref is numerically active, but it uses one uint8 index per coordinate, retains
materialized K/V, and is unfused. Its measured energy and throughput overhead is
real evidence about the reference path, not evidence that a packed/fused kernel
would have the same overhead. Conversely, the ideal packed/fused analysis proves
conditional persistent-KV savings under explicit representation assumptions,
but it does not identify numerical ideal energy, latency, throughput, power, or
total peak VRAM.

## 2. Motivation and Research Gap

Autoregressive transformers retain key and value tensors for prior tokens. KV
storage grows with context length, layers, KV heads, and head dimension. Even
small language models can therefore become memory- and bandwidth-constrained on
edge-class accelerators during long-context generation.

The original motivation combined two sustainability concerns:

- inference is repeated at deployment scale and can dominate lifetime compute;
- edge deployment is constrained by memory capacity, bandwidth, power, latency,
  and quality simultaneously.

Three major compression families address different parts of this problem:

| Technique | Resource targeted | Executed project object |
|---|---|---|
| AWQ | Model-weight storage and weight traffic | Official 4-bit AWQ checkpoints |
| Token eviction | Number of retained KV tokens | Validated custom PyramidKV-style layerwise scorer |
| KV quantization | Bytes per retained KV element | `turboquant==0.2.0` numerical TQ-Ref |

The research gap was not merely whether each technique works independently. The
project asked what happens when they are stacked on the same model and hardware,
including interaction effects that isolated studies cannot expose. The Qwen
results later made this especially important: an energy-saving eviction path can
be operationally useless when retrieval collapses, while a quality-preserving
TQ-Ref path can be unattractive because reference implementation overhead
dominates.

The work also addresses a method gap noted in the course material: many green
computing studies rely on simulation or a single objective. This project uses
raw 10 Hz NVML power traces, phase-separated energy integration, explicit
quality tasks, measured throughput, storage accounting, registered statistical
comparisons, and Pareto analysis.

## 3. Research Questions and Hypothesis Evolution

### 3.1 Original proposal questions

The canonical proposal originally targeted Qwen3-4B and asked:

- how stacking AWQ, PyramidKV/SnapKV, and TurboQuant affected energy, peak VRAM,
  and NIAH accuracy at 512, 2048, and 8192 tokens on a T4;
- how Qwen3 thinking mode changed energy and whether compression affected
  reasoning quality disproportionately.

The proposal hypotheses expected approximately threefold AWQ energy savings,
15-20% TurboQuant VRAM reduction with 5-15% energy overhead, an eviction capacity
gate below 1024 tokens, the compound path to minimize energy and memory with
10-30% NIAH degradation, and thinking mode to multiply energy by two to five.
These were proposal-stage expectations, not findings.

### 3.2 Why the questions changed

The executed protocol replaced Qwen3-4B with Llama 3.2-3B as the primary model
and later added Qwen2.5-3B as a cross-model reference. Consequences included:

- no built-in thinking mode on Llama, so the proposed thinking-mode study was
  removed rather than approximated;
- exact contexts changed to 1024, 2048, and 4096 tokens;
- the baseline became FP16 rather than proposal-stage BF16;
- the configuration labels were corrected so C2/Q2 denotes eviction and
  C3-Ref/Q3-Ref denotes TQ-Ref;
- NIAH evolved into a frozen, tokenizer-specific, exact-4096-token hard-retrieval
  benchmark;
- cross-model absolute joules were treated descriptively because sessions,
  adapters, prompts, and baseline structures were not fully matched.

### 3.3 Final operational questions

The completed evidence addresses the following operational questions:

1. Within each model, how do AWQ, eviction, TQ-Ref, and sequential
   eviction-plus-TQ affect measured energy and decode throughput as context grows?
2. At 4096 tokens, does eviction reduce energy without violating hard-retrieval
   quality, and is that result consistent across Llama and Qwen?
3. How much overhead does the accessible numerical TQ-Ref path add with and
   without prior eviction?
4. Is the sequential compound effect additive, shielding, or amplifying?
5. Are energy rankings and registered significance decisions stable when the
   same raw traces are reintegrated after clipping at 82 W and 70 W?
6. What persistent-KV footprint would an ideal packed/fused realization have,
   and under what symbolic condition could reduced logical byte demand overcome
   non-traffic implementation overhead?
7. Which measured configurations are non-dominated when energy, retrieval, and
   persistent KV storage are considered together?

The null hypothesis for registered energy comparisons remained that there is no
configuration difference at the chosen significance level. Directional proposal
hypotheses were evaluated against executed evidence rather than retroactively
rewritten to match outcomes.

## 4. Final Executed Protocol

### 4.1 Experiment sequence

| Track | Notebook/object | Role | Status |
|---|---|---|---|
| A0 | Notebook 00 and Llama v5 | Verify historical systems evidence | Immutable historical/accepted source evidence |
| A1 | Notebooks 01-04 | Calibrate hard retrieval | Three failed pilots; V4 accepted only for prompt freeze |
| A1-A2 | Notebook 05 | Frozen Llama hard quality and C1-W energy control | Accepted measured evidence |
| A3 | Notebook 06 | Raw/82 W/70 W trace robustness | Accepted derived evidence |
| A4 | Notebook 07 | Qwen adapter and path parity | Accepted pilot evidence |
| A4 | Notebook 08 | Full Qwen reference experiment | Accepted measured evidence |
| A5 | Notebook 09 | Cross-model and ideal-realization synthesis | Provisional, internally validated |
| A5 figures | Notebook 09B | Portable visualization from provisional synthesis | Accepted visualization output |

### 4.2 Reproducibility and fail-closed rules

The notebooks use explicit schemas, fingerprints, isolated artifact directories,
frozen prompt hashes, source manifests, row-count assertions, unique-key gates,
and trace reintegration. Accepted bundles are never modified. Failed pilots are
preserved under `evidence/discarded/` and are excluded from final estimates.

New experiment implementations are self-contained Colab notebooks rather than
standalone runners. The final CPU-only visualization pattern removes Google Drive
as a runtime dependency: the public project ZIP is downloaded with `gdown`,
outputs are written under `/content`, and a downloadable ZIP is produced.

### 4.3 Measurement design

- Hardware: NVIDIA T4, 16 GB nominal VRAM, completed runs under a 70 W enforced
  limit.
- Power: `pynvml` polling at 10 Hz.
- Energy: trapezoidal integration, with prefill and decode handled separately.
- Decode workload: fixed 64-token teacher-forced decode for systems energy.
- Contexts: 1024, 2048, and 4096 for systems measurements.
- Hard quality: 4096 exact tokenizer-specific tokens, 60 frozen scenarios per
  configuration.
- Repetitions: five energy blocks per model/configuration/context in the core
  matrices.
- Statistics: registered paired tests where a true within-session pairing
  existed, non-parametric alternatives, multiplicity adjustment, effect sizes,
  Wilson quality intervals, interaction contrasts, and bootstrap frontier
  stability.
- Sensitivity: the same traces reintegrated after clipping power samples at 82 W
  and 70 W. These are sensitivity integrations, not hardware-cap reruns.

## 5. Models, Configurations, and Metrics

### 5.1 Model geometry

| Property | Llama 3.2-3B-Instruct | Qwen2.5-3B-Instruct |
|---|---:|---:|
| Layers | 28 | 36 |
| Query heads | 24 | 16 |
| KV heads | 8 | 2 |
| GQA ratio | 3:1 | 8:1 |
| Head dimension | 128 | 128 |
| Native context | 8K | 32K |
| Thinking mode in executed study | None | Not used |

Llama checkpoints were pinned to
`unsloth/Llama-3.2-3B-Instruct` for FP16 and
`casperhansen/llama-3.2-3b-instruct-awq` for AWQ. Qwen used pinned FP16 and AWQ
revisions registered in `research/experiment_registry.json`.

### 5.2 Semantic configuration map

| Semantic role | Llama label | Qwen label | Meaning |
|---|---|---|---|
| FP16 baseline | C0 | Q0 | Unquantized FP16 model path |
| AWQ baseline | C1 or C1-W | Q1-W | 4-bit AWQ; `-W` denotes matched wrapper |
| Eviction | C2 | Q2 | AWQ plus custom pyramidal token eviction |
| TQ reference | C3-Ref, systems source label C3 | Q3-Ref | AWQ plus numerical TQ-Ref |
| Compound | C4-Ref, systems source label C4 | Q4-Ref | AWQ plus eviction followed by TQ-Ref |

Historical Llama systems energy uses stock C1 at all contexts. Llama has a
separate C1-W matched-wrapper control only at 4096, collected in a different
session. Qwen uses matched Q1-W throughout. Therefore, the Llama C1-to-C3
TQ-only contrast is wrapper-confounded, while the Qwen Q1-W-to-Q3-Ref contrast
is better matched.

### 5.3 Implementation boundaries

- AWQ uses 4-bit GEMM weights with group size 128.
- Eviction uses a custom validated Llama/Qwen attention integration and
  PyramidKV-style scorer with average layer budget 1024; it is not evidence about
  the official KVCache-Factory implementation.
- TQ-Ref uses `turboquant==0.2.0` and validates active indices, norms,
  residuals, reconstructed K/V, active cache use, and alias-deduplicated storage.
- Nominal 2/3/4-bit TQ-Ref settings still use uint8 physical indices and retain
  materialized K/V. They are not physically packed caches.

### 5.4 Outcome variables

The project records:

- prefill, decode, and total joules;
- prefill and decode runtime;
- decode tokens per second;
- raw power traces and capped reintegrations;
- retained analytical FP bytes and alias-deduplicated live cache storage;
- TQ index, norm, package, residual, and materialized-storage categories where
  available;
- hard-retrieval success, format success, target NLL, and Wilson intervals;
- interaction contrasts and energy-quality Pareto membership.

The course submission requires a 150-250 word abstract, complete methodology,
results, discussion, conclusion, at least 25 scientific references, ACM-format
PDF and LaTeX sources, figures, a private reproducible repository, and an
individual contribution declaration. Those requirements define the final
packaging work but do not alter the evidence.

## 6. Literature, Proposal, and Design Evolution

### 6.1 Related Works (Literature Review)

Researchers have studied various ways to compress language models. This section reviews the most relevant work across weight quantization, token eviction, KV cache quantization, compound methods, and energy measurement.

**Weight Quantization:** Lin et al. developed AWQ, which protects activation-salient weights and enables low-bit deployment when paired with suitable kernels. Frantar et al. proposed GPTQ as a second-order alternative. The broader SLMQuant benchmark shows that compression behavior does not transfer uniformly from large models to SLMs, motivating direct measurement on Llama 3.2-3B.

**Token Eviction:** Zhang et al. showed that only about 20% of tokens in the KV cache actually matter, which they called the Heavy Hitter Oracle (H2O). Li et al. built on this with SnapKV, which uses a short observation window to figure out which tokens can be safely removed, achieving large memory savings at 16K context. Cai et al. improved further with PyramidKV, which uses a pyramidal budget across layers and beats SnapKV by 5–15% NIAH accuracy.

**KV Cache Quantization:** Zandieh et al. proposed TurboQuant, which uses random rotation and an optimized scalar codebook without calibration data. Liu et al. offered KIVI as a 2-bit alternative. Salfati showed that preserving dimensions through quantization can outperform rank reduction, with a growing advantage for GQA. These results motivate both TurboQuant and the executed bit-width sensitivity analysis.

**Compound Methods:** Zhang et al. jointly allocate eviction and quantization through a rate-distortion formulation (RDKV) and report strong long-context accuracy and throughput. ThinKV likewise uses hybrid quantization and eviction for reasoning models. These methods demonstrate that joint compression is important, but neither supplies the sub-4B T4 energy ablation of AWQ, custom PyramidKV-style eviction, and TQ-Ref reported here. The present C4-Ref stack remains sequential rather than a reproduction of either joint optimizer.

**Energy Measurement:** Argerich et al. published Watt Counts (2026), a large benchmark covering 5,000+ LLM inference experiments. They established that T4 GPUs draw about 12W idle and up to 82W at peak, and selected 10 Hz (100 ms) polling via pynvml as the best accuracy–overhead trade-off after evaluating rates from 1 Hz to 200 Hz.

| Work | Wt.Q | Evict | KVQ | Energy |
|---|---|---|---|---|
| AWQ | ✓ | - | - | - |
| GPTQ | ✓ | - | - | - |
| SLMQuant | ✓ | - | - | - |
| H2O | - | ✓ | - | - |
| SnapKV | - | ✓ | - | - |
| PyramidKV | - | ✓ | - | - |
| TurboQuant | - | - | ✓ | - |
| KIVI | - | - | ✓ | - |
| RDKV | - | ✓ | ✓ | - |
| ThinKV | - | ✓ | ✓ | - |
| Watt Counts | - | - | - | ✓ |
| **This Work** | **✓** | **✓** | **✓** | **✓** |

As the table shows, the reviewed work does not cover all four dimensions together, especially at the SLM scale with real hardware energy measurement.

### 6.2 Proposal-stage design

The canonical proposal is a genuine planning artifact, not a description of the
final experiment. It targeted Qwen3-4B because an earlier model comparison favored
Qwen3 over Phi-4 Mini for official AWQ availability, built-in thinking mode,
multilingual coverage, and anticipated integration reuse.

The proposed matrix used BF16/AWQ, contexts 512/2048/8192, three repetitions, a
single fixed needle, and a thinking-mode subset. It predicted approximately 1100
J for BF16 at 8K, 350 J for AWQ, modest TurboQuant memory savings, and C3 as an
all-rounder. None of those numerical predictions should appear in a results
section. They were hypotheses used to motivate measurement.

### 6.2 Model and scope change

Research validation later recommended Llama 3.2-3B because community AWQ weights,
28-layer GQA geometry, lack of thinking mode, and Llama/TurboQuant ecosystem
support reduced implementation risk. This eliminated the thinking-mode question
and narrowed the immediate design to five configurations at three contexts.
Qwen2.5-3B was subsequently added as a second complete model after its adapter
passed independent parity gates.

The final paper must update every proposal section that still says Qwen3-4B,
BF16, 512/8192 tokens, three repetitions, thinking mode, or the old C2/C3 label
order. The proposal remains useful for motivation, research-gap framing,
stakeholders, and literature, but its methods and expected-results tables are
superseded.

### 6.3 Planning assumptions that did not survive execution

Several validation-stage statements were too optimistic:

- It stated that native KVCache-Factory support meant no custom monkey patch was
  needed. The accepted study ultimately used validated custom Llama and Qwen
  attention wrappers and a custom PyramidKV-style scorer.
- It described a physical-storage gate that would reject TQ paths if FP16 copies
  remained. The accessible TQ-Ref package did retain materialized K/V. Rather
  than discarding a numerically valid path, the executed protocol reported its
  realized storage honestly and separated it from an ideal packed envelope.
- It called TurboQuant's overhead low based on literature expectations. The
  measured unfused reference path had large energy and throughput penalties.
- It assumed AWQ speedups would translate directly to energy reductions. Llama
  showed context-dependent energy benefits; Qwen Q1-W was not below Q0 at 4096.
- It expected PyramidKV to preserve retrieval generally. That held approximately
  for Llama but failed catastrophically for Qwen under the custom scorer.

These are valuable negative findings. They demonstrate why package capability,
paper-level compression ratios, and model-card speedups cannot substitute for
path validation and hardware measurement.

### 6.4 Method-choice alignment with course requirements

The course required an empirical, focused, feasible green-computing problem with
measurable variables, comparisons, statistical analysis, and explicit
limitations. The executed study aligns well:

- energy is measured in joules from power traces rather than inferred from FLOPs;
- quality is operationalized as exact retrieval with bounded uncertainty;
- configurations provide explicit baselines and controlled component contrasts;
- failed pilots are documented rather than hidden;
- trade-offs are reported with Pareto and quality constraints;
- the absence of human participants removes consent requirements, while
  environmental impact and responsible claims remain ethical considerations.

The final submission should use the official ACM Conference Proceedings Primary
Article Template unless the instructor approves a journal/arXiv track. The
current project also contains IEEE-oriented material, but that does not override
the latest course submission instruction.

## 7. Llama Systems Experiment

### 7.1 Evidence identity

The historical Llama systems matrix is stored in
`evidence/accepted/bundles/CSE407_llama_v5_final/` and registered as
`llama-3.2-3b-v5-reference`.

| Field | Value |
|---|---|
| Schema | `v5-final-2026-07-31-1` |
| Fingerprint | `8d27af8c9ee94de3` |
| Session | `20260731T125351-ad1b5249` |
| Primary execution rows | 380 |
| Raw power traces | 95 |
| Manifest inventory | 115 files, including `.gitignore` |
| GPU | Tesla T4, reported 14.56 GiB available |
| Software | PyTorch 2.11.0+cu128, Transformers 5.12.1, TurboQuant 0.2.0 |
| Seed | 407 |

The matrix contains five core configurations at three contexts with five blocks,
plus sensitivity conditions for eviction budgets 512 and 1536 and TQ nominal
bits 2 and 3 at 4096. The fixed decode length is 64 tokens.

The accepted artifact manifest binds model revisions, TurboQuant source SHA-256,
all summary products, and every trace. The v5 bundle is historical in the sense
that its original quality task was easy; its systems energy and storage data
remain current accepted source evidence, while final hard-quality interpretation
comes from Notebook 05.

### 7.2 Measured systems summary

| Context | Variant | Total energy, mean +/- SD (J) | Decode tok/s | Peak VRAM (MiB) | Live cache (MiB) |
|---:|---|---:|---:|---:|---:|
| 1024 | C0 | 244.11 +/- 13.10 | 21.09 | 8810.21 | 119.00 |
| 1024 | C1 | 268.77 +/- 26.20 | 18.24 | 4942.71 | 119.00 |
| 1024 | C2 | 253.61 +/- 14.36 | 19.31 | 4919.68 | 92.29 |
| 1024 | C3 | 367.00 +/- 28.44 | 13.49 | 5099.44 | 187.25 |
| 1024 | C4 | 364.91 +/- 21.59 | 12.75 | 5041.51 | 146.77 |
| 2048 | C0 | 345.26 +/- 4.97 | 17.42 | 9662.75 | 231.00 |
| 2048 | C1 | 313.81 +/- 9.31 | 20.13 | 5795.25 | 231.00 |
| 2048 | C2 | 338.74 +/- 21.03 | 17.81 | 5690.93 | 119.00 |
| 2048 | C3 | 439.58 +/- 9.11 | 13.33 | 6115.67 | 357.00 |
| 2048 | C4 | 435.05 +/- 24.47 | 12.87 | 5853.25 | 187.25 |
| 4096 | C0 | 701.08 +/- 8.12 | 11.34 | 12687.83 | 455.00 |
| 4096 | C1 | 631.25 +/- 5.05 | 13.77 | 8820.33 | 455.00 |
| 4096 | C2 | 529.30 +/- 20.02 | 20.34 | 8500.01 | 119.00 |
| 4096 | C3 | 913.48 +/- 2.11 | 7.66 | 9468.12 | 696.50 |
| 4096 | C4 | 659.50 +/- 21.35 | 12.53 | 8662.32 | 187.25 |

### 7.3 Interpretation of context scaling

AWQ did not produce the proposal's expected threefold energy reduction. At 4096,
C1 used about 10.0% less total energy than C0 and reduced measured peak VRAM by
about 30.5%, while decode throughput increased from 11.34 to 13.77 tokens/s. At
1024, however, C1 consumed more energy and decoded more slowly than C0. The AWQ
benefit therefore depended on context and phase rather than being a universal
constant.

Eviction's advantage emerged most clearly at long context. At 4096, C2 used
529.30 J versus 631.25 J for C1, a reduction of 101.95 J or 16.15%. Decode energy
fell by 100.63 J and throughput rose by 6.57 tokens/s. Live cache fell from 455
MiB to 119 MiB, a reduction of approximately 73.8%. At 1024 the effect was much
smaller and uncertain; at 2048 C2 was actually above C1 in mean energy. This is
consistent with compression becoming more valuable only after retained history
is large enough to dominate.

The accessible TQ-Ref path behaved in the opposite direction. At 4096, C3 used
913.48 J versus 631.25 J for C1: 282.24 J or 44.7% more total energy. Decode
energy increased by 247.68 J and throughput dropped by 6.11 tokens/s. Live cache
increased from 455 MiB to 696.5 MiB because the reference implementation retained
materialized K/V and added quantization state. This result is not evidence
against a future packed/fused kernel; it is direct evidence that the accessible
reference path was not an efficient physical cache implementation.

The compound C4 path sat between C2 and C3. At 4096 it used 659.50 J, only 28.26
J above stock C1, but 130.21 J above C2. Its cache was 187.25 MiB: far below C3
because eviction reduced the number of tokens exposed to TQ-Ref, but above C2
because TQ state and materialized storage remained.

## 8. Llama Systems Statistical and Interaction Findings

### 8.1 Registered 4096-token comparisons

The v5 core tests use five paired blocks and Holm adjustment. Important total
energy contrasts are:

| Comparison, first minus second | Mean difference (J) | 95% CI (J) | Holm p | Interpretation |
|---|---:|---:|---:|---|
| C1 - C2 | 101.95 | [73.81, 130.08] | 0.00549 | C2 lower than C1 |
| C1 - C3 | -282.24 | [-287.23, -277.25] | 1.88e-7 | C3 much higher than C1 |
| C1 - C4 | -28.26 | [-60.28, 3.76] | 0.2465 | No adjusted significance |
| C2 - C4 | -130.21 | [-168.32, -92.09] | 0.00620 | C4 higher than C2 |
| C3 - C4 | 253.98 | [226.93, 281.02] | 0.000206 | C4 lower than C3 |

The corresponding decode-energy, decode-time, and throughput tests support the
same broad story: C2 strongly improves the long-context decode path, C3 strongly
worsens it, and prior eviction reduces but does not eliminate TQ-Ref overhead.

Only five blocks were available. The very large effects were nevertheless
stable, but small-effect inference remains low-resolution and should be reported
with intervals and effect sizes rather than only p-values.

### 8.2 Sequential interaction

The registered interaction is a difference in differences:

```text
I = (C4 - C3) - (C2 - C1)
  = (TQ overhead with eviction) - (TQ overhead without eviction)
```

For total energy, `I = -152.03 J`, 95% CI `[-187.11, -116.96]`, Holm-adjusted
`p = 0.00109`. Decode energy and decode time also had significant negative
interactions. The negative sign means eviction shielded part of TQ-Ref overhead
by shortening the cache before quantization. It does not mean TQ-Ref became free:
the direct C4-minus-C2 total-energy overhead remained approximately 130.21 J.

### 8.3 Historical quality and sensitivity caution

The original v5 task gave every core configuration 100% accuracy at 4096, so its
energy-quality Pareto table marked C2 as optimal simply because quality did not
separate the paths. This was a benchmark-ceiling problem, not proof that all
methods preserve hard retrieval.

The v5 sensitivity task found:

- C2 budgets 512, 1024, and 1536 all at 100% on the easy task, with mean energy
  525.65 J, 529.30 J, and 536.49 J respectively;
- C3-TQ2 at 93.33% with 890.11 J;
- C3-TQ3 and C3-TQ4 at 100% with 895.38 J and 913.48 J.

These low-bit Llama quality rows used a different and easier task. They cannot be
mixed with the later frozen hard-60 benchmark or used to assign hard-quality
values to ideal 2/3-bit paths.

## 9. Failed Hard-Retrieval Pilots and Lessons

### 9.1 Why pilots were necessary

The v5 quality task had a ceiling effect, so it could not reveal whether
eviction or TQ-Ref damaged difficult retrieval. A new exact-output benchmark was
therefore calibrated before exposing the full five-configuration matrix. The
pilot compared only matched-wrapper AWQ (C1-W) and eviction (C2), used 12
scenarios per variant across 10%, 50%, and 90% target depths, and failed closed:
the full experiment could not proceed until a prompt generator passed an
explicit difficulty and depth-floor review.

All pilot rows are preserved under `evidence/discarded/bundles/`. They document
method development but are excluded from final quality estimates.

### 9.2 Pilot V1: too many confusing records

| Field | Value |
|---|---|
| Fingerprint | `b0e6646087995e5f` |
| Result | C1-W 6/12; C2 6/12 |
| Decision | `TOO_HARD_REDUCE_DIFFICULTY` |

V1 used 48 records and produced perfect behavior on the sampled 10%-depth cases
but many wrong-code outputs at 50% and 90%. Both configurations failed at the
same overall rate, indicating that the benchmark itself was too difficult to
support a useful compression comparison. The result was not interpreted as an
eviction failure.

### 9.3 Pilot V2: reducing record count was insufficient

| Field | Value |
|---|---|
| Fingerprint | `922e8877398679eb` |
| Result | C1-W 6/12; C2 6/12 |
| Decision | `TOO_HARD_REDUCE_DIFFICULTY` |

V2 reduced the record count to 32 and added first-answer-token diagnostics. The
overall retrieval remained 50% for both paths. Near-depth cases passed, but many
mid- and late-depth cases returned another valid-looking code. This showed that
simply shortening the haystack did not resolve target confusion.

### 9.4 Pilot V3: close siblings made the task worse

| Field | Value |
|---|---|
| Fingerprint | `43041ef3243f87a3` |
| C1-W | 3/12 overall; depth rates 0.75, 0.00, 0.00 |
| C2 | 2/12 overall |
| Decision | `TOO_HARD_REDUCE_DIFFICULTY`; depth floor failed |

V3 introduced four close sibling records per target. This increased semantic
confusion rather than creating a controlled hard task. C1-W fell to 25% and C2
to 16.7%; both failed completely at the sampled 50% and 90% depths except for no
successful C1-W cases there. The failure taught an important benchmark-design
lesson: difficulty must leave enough baseline headroom to observe treatment
effects. A benchmark where the control mostly fails cannot diagnose compression.

### 9.5 Pilot V4: calibrated freeze candidate

| Field | Value |
|---|---|
| Fingerprint | `15a1017ec54949b9` |
| C1-W | 9/12 overall; depth rates 1.00, 0.50, 0.75 |
| C2 | 9/12 overall |
| Decision | `PASS_FREEZE_CANDIDATE` |
| Depth floor | Passed |

V4 simplified target neighborhoods and used distinctive node names while
retaining exact code retrieval. It restored useful control headroom and retained
failures at multiple depths. One C2 answer contained the correct code with a
trailing period, illustrating why retrieval correctness and strict formatting
were recorded separately.

V4 was accepted only as a calibration source. Its 24 result rows remained in a
discarded directory and were never merged into final quality statistics. The
semantic generator and exact tokenizer-specific prompt hashes were frozen into
`research/frozen_hard_retrieval_v4.json`, then expanded to 60 scenarios for each
of five configurations.

### 9.6 Methodological lessons from failure

1. Pilot failures prevented a misleading final benchmark rather than delaying a
   valid experiment.
2. Equal failure of baseline and treatment is evidence of benchmark difficulty,
   not evidence of equal model quality.
3. Aggregate accuracy alone hid the depth failure in V3; the depth floor was an
   essential gate.
4. Exact response, extracted target code, format correctness, first-token rank,
   answer log probability, and NLL provide complementary failure diagnostics.
5. Calibration rows must remain separate from final evidence after they influence
   benchmark design.

## 10. Llama Hard-Quality and Matched-Control Experiment

### 10.1 Evidence and validation

Notebook 05 is the accepted frozen hard-retrieval/control experiment:

| Field | Value |
|---|---|
| Schema | `track-a-llama-full-v1-2026-08-03-1` |
| Fingerprint | `106a561c07c62937` |
| Session | `20260803T153710-2a4dc573` |
| Quality rows | 300 unique rows |
| Energy control rows | 5 |
| Power traces | 5 |
| Artifact inventory | 324 files |
| Semantic SHA-256 | `fffa82607af6e7d2c892d18d5bc790524570833472ad397b7ab2e54eb03005ef` |
| Prompt-set SHA-256 | `4e1ced4fd4829629929a346879cc00c45476f38fa0936137909b8779242321e8` |

The final-integrity marker confirms unique keys, paired prompt hashes, raw trace
reintegration, Wilson uncertainty, and depth-stratified paired bootstrap
analysis. The manifest binds 300 individual quality shards, five energy shards,
five traces, six analysis products, and the executed notebook hash.

Before measurement, stock C1-S and wrapped C1-W were compared on one scenario at
each depth. Maximum absolute logit difference was zero; top-1 logits, greedy
token IDs, responses, full-cache lengths, and absence of compression state were
identical. This validates the wrapper's semantic parity for the tested paths.

Structural probes then verified:

- C1-W: no eviction or quantization, 28 active decode cache updates;
- C2: all 28 layers evicted with pyramidal lengths from 1966 to 82 at prefill;
- C3-Ref: 28 quantized layers, full sequence length retained, materialized K/V
  plus index/norm/residual state;
- C4-Ref: all 28 layers evicted and 27 reported quantized layers, with active
  cache updates and retained TQ state.

### 10.2 Hard-retrieval results

| Variant | Successes | Rate | Wilson 95% interval |
|---|---:|---:|---:|
| C0 | 47/60 | 0.783 | [0.664, 0.869] |
| C1-W | 38/60 | 0.633 | [0.507, 0.744] |
| C2 | 37/60 | 0.617 | [0.490, 0.729] |
| C3-Ref | 37/60 | 0.617 | [0.490, 0.729] |
| C4-Ref | 37/60 | 0.617 | [0.490, 0.729] |

The FP16 model outperformed all AWQ paths on this hard task. However, eviction,
TQ-Ref, and the compound path each differed from matched AWQ by only one scenario
overall. The depth-stratified paired bootstrap estimate for C2, C3-Ref, and
C4-Ref versus C1-W was `-1/60 = -0.0167`, with 95% interval `[-0.05, 0]`.
Bonferroni-adjusted exact McNemar p-values were 1.0.

The paired flip tables make the result concrete:

- C2 and C3-Ref had no gains and one loss relative to C1-W, at 90% depth;
- C4-Ref had no gains and one loss, at 10% depth;
- the remaining 59 scenarios in each comparison had the same correctness state.

Thus, unlike Qwen, the Llama hard experiment did not show an eviction-specific
retrieval collapse. It also does not prove exact quality equivalence: n=60 leaves
uncertainty, and every AWQ-derived path was below FP16.

### 10.3 Depth and formatting patterns

All variants were strongest at 10% depth and weaker at 50%/90% depth:

| Variant | 10% | 50% | 90% |
|---|---:|---:|---:|
| C0 | 19/20 | 13/20 | 15/20 |
| C1-W | 18/20 | 10/20 | 10/20 |
| C2 | 18/20 | 10/20 | 9/20 |
| C3-Ref | 18/20 | 10/20 | 9/20 |
| C4-Ref | 17/20 | 10/20 | 10/20 |

Failure categories were overwhelmingly `wrong_code`, not missing output. Median
target first-token rank remained one in the aggregated diagnostics, while
continuation NLL and strict formatting varied. Retrieval and formatting must
therefore remain separate metrics: a response can contain the correct code but
violate exact formatting.

### 10.4 Matched-wrapper energy control

The five C1-W energy controls at 4096 averaged approximately `639.86 +/- 5.48 J`
with decode throughput approximately 13.71 tokens/s. Their analytical retained
FP cache was 469,762,048 bytes after prefill and 477,102,080 bytes after the
64-token decode. All rows passed structural gates and trace reintegration.

This control is close to historical stock C1 (`631.25 +/- 5.05 J`) but was
collected in a separate session with a different exact prompt/workload. The
cross-session C1-W-to-v5 comparisons are descriptive only; they are not valid
paired or causal tests.

## 11. Llama Power Robustness

### 11.1 Purpose and evidence identity

Raw NVML traces contained samples above the nominal 70 W enforced limit and even
isolated samples above 100 W. Notebook 06 tested whether these transients were
driving the conclusions by reintegrating every trace after clipping samples at
82 W and 70 W.

| Field | Value |
|---|---|
| Schema | `track-a-llama-power-robustness-v1-2026-08-03-1` |
| Fingerprint | `91ebc63773e735e6` |
| Evidence class | Immutable accepted derived evidence |
| Verified traces | 100: 95 v5 plus 5 C1-W |
| Maximum reintegration error | `1.14e-13 J` |
| Maximum raw sample | 124.496 W in `C3-TQ2_ctx4096_block2.json` |
| Samples above 70 W | 1501 |
| Samples above 82 W | 82 |
| Samples above 100 W | 21 |

The analysis verified both source manifests, all source files, exact raw
reintegration, frozen raw tests, rankings, and significance decisions. The
15-file output includes trace-level integrations, anomaly inventory, condition
summaries, rankings, statistical tables, figures, and final integrity.

### 11.2 Ranking stability

Every registered ranking was unchanged under both clipping regimes:

| Analysis | Raw, 82 W, and 70 W ordering from lowest to highest energy |
|---|---|
| Core 1024 | C0 < C2 < C1 < C4-Ref < C3-Ref |
| Core 2048 | C1 < C2 < C0 < C4-Ref < C3-Ref |
| Core 4096 | C2 < C1 < C4-Ref < C0 < C3-Ref |
| Eviction budget 4096 | B512 < B1024 < B1536 |
| TQ nominal bits 4096 | TQ2 < TQ3 < TQ4 |

This strengthens two patterns: compression benefits change with context, and
the materialized TQ-Ref path remains the highest-energy core path even when
power spikes are clipped.

### 11.3 Significance stability

All 40 raw-versus-capped decisions were unchanged. For total and decode energy,
decode time, and throughput:

- C1 versus C2 remained significant;
- C1 versus C3-Ref remained significant;
- C1 versus C4-Ref remained non-significant after adjustment;
- C2 versus C4-Ref remained significant;
- C3-Ref versus C4-Ref remained significant.

Clipping reduced mean energy only modestly at 82 W and more at 70 W. For example,
C4-Ref at 4096 changed from 659.50 J raw to 658.45 J at 82 W and 644.79 J at 70
W; C2 changed from 529.30 J to 527.70 J and 517.92 J. These shifts did not alter
the scientific ordering.

### 11.4 Interpretation boundary

Raw joules remain the primary measurements. The capped values are deterministic
sensitivity analyses over observed traces, not experiments rerun under different
hardware power limits. They show that isolated high-power samples do not explain
the principal Llama rankings or inferential decisions. They cannot identify how
hardware behavior would change if the GPU were physically reconfigured to a
different limit.

## 12. Qwen Adapter Parity Pilot

### 12.1 Why a separate adapter pilot was required

The validated Llama attention wrapper could not be assumed correct for Qwen2.5.
Qwen has different geometry, source signatures, position handling, tokenizer
materialization, and an 8:1 GQA ratio. Running the full matrix without a separate
parity gate would risk collecting internally consistent but semantically invalid
measurements.

Notebook 07 therefore performed no energy or quality collection. Its only role
was to prove that the Qwen adapter and compression paths were structurally and
numerically active before Notebook 08.

| Field | Value |
|---|---|
| Schema | `track-a-qwen-adapter-pilot-v1-2026-08-04-1` |
| Fingerprint | `91def77c920729e9` |
| Session | `20260804T074536-e61a076f` |
| Artifact files | 5 |
| Prompt count | 60 |
| Parity rows | 3 |
| Path probes | 4 |
| Energy/quality rows | 0/0 |

The five-file accepted pilot bundle contains frozen semantic and Qwen prompt
manifests, environment identity, full validation, and Q1-S/Q1-W parity. It binds
the FP16/AWQ model revisions, Transformers commit and source files, tokenizer and
chat-template hashes, TurboQuant source, notebook source, architecture, and
prompt set.

### 12.2 Architecture and source gates

The pilot verified:

- 36 Qwen2 attention layers;
- hidden size 2048, 16 query heads, 2 KV heads, head dimension 128;
- 32,768 maximum positions and RoPE theta 1,000,000;
- FP16 `Qwen2Attention` and AWQ `AwqExllamaV2Linear` projections;
- AWQ GEMM 4-bit, group size 128, asymmetric zero point;
- exact source hashes for Qwen2 modeling, cache utilities, masking, and SDPA;
- the actual forward signature, including absence of a separately assumed
  `cache_position` argument.

The 36-layer pyramidal budgets ranged from 1966 to 82 retained tokens and averaged
1024, preserving the same semantic budget target as Llama while respecting Qwen's
layer count.

### 12.3 Exact wrapper parity

Q1-S and Q1-W were compared on one frozen scenario at each depth. For all three:

- maximum absolute logit difference was zero;
- top-1 prediction agreed;
- greedy token IDs and decoded responses were identical;
- every layer had equal full-cache lengths;
- no eviction or TQ state was present.

This allowed Q1-W to serve as Qwen's matched-wrapper AWQ baseline. Q1-S remained
parity-only and correctly produced zero measurement rows in Notebook 08.

### 12.4 Compression path gates

The probe validated prompt identity, absolute-position behavior, cache updates,
active returned-cache use, eviction-before-quantization order, alias-deduplicated
storage, and actual TQ reconstruction. Prefill top-1 logits agreed before the
post-attention cache transformations for Q2, Q3-Ref, and Q4-Ref.

The maximum observed actual-path normalized MSE was approximately 0.02461 for
Q3-Ref and 0.02512 for Q4-Ref, below the registered 0.25 gate. This showed that
the numerical path was active and bounded; it did not claim packed storage or
quality equivalence for the later full task.

The adapter pilot is important positive evidence about implementation validity,
but it is not outcome evidence. It should appear in the methods/reproducibility
section rather than being counted as an additional experimental sample.

## 13. Qwen Full Reference Experiment

### 13.1 Evidence identity and inventory

Notebook 08 collected the full Qwen systems and quality matrix only after the
adapter pilot passed.

| Field | Value |
|---|---|
| Schema | `track-a-qwen-full-reference-v1-2026-08-04-1` |
| Fingerprint | `861d89617e53034d` |
| Session | `20260804T154752-97822cdb` |
| Core energy rows | 75 |
| Sensitivity energy rows | 20 |
| Raw power traces | 95 |
| Core quality rows | 300 |
| Sensitivity quality rows | 60 |
| Unique measurement keys | 455 |
| Q1-S measurement rows | 0, by design |
| Artifact files | 593 total; 591 manifest entries plus declared exceptions |
| Trace reintegration maximum error | 0.0 J |

The final-integrity marker binds runtime, analysis protocol, validation, prompt
set, schedule, fixed decode IDs, and artifact manifest. All JSON shards matched
their CSV snapshots; every trace hash matched and reintegrated exactly; the
analysis products have a separate provenance hash map.

Qwen used the same semantic hard-retrieval scenarios as Llama but materialized
its own exact 4096-token prompts with a different tokenizer and chat template.
Energy prompts were separately hashed at 1024, 2048, and 4096. The fixed decode
sequence was also bound by SHA-256.

### 13.2 Core energy scaling

| Context | Q0 | Q1-W | Q2 | Q3-Ref | Q4-Ref |
|---:|---:|---:|---:|---:|---:|
| 1024 | 258.57 +/- 27.40 | 293.42 +/- 21.61 | 272.02 +/- 13.92 | 358.58 +/- 9.61 | 342.96 +/- 14.14 |
| 2048 | 334.15 +/- 17.52 | 398.46 +/- 12.46 | 342.56 +/- 10.34 | 540.87 +/- 14.11 | 435.18 +/- 20.00 |
| 4096 | 616.78 +/- 6.79 | 621.75 +/- 25.14 | 550.48 +/- 10.07 | 812.28 +/- 13.11 | 628.69 +/- 9.77 |

Values are raw total joules, mean +/- sample SD over five blocks. Unlike Llama,
Qwen's FP16 Q0 was slightly below Q1-W even at 4096. AWQ therefore did not provide
a measured total-energy advantage in this software/hardware path, despite
reducing weight storage.

The context ranking changed as sequence length grew, but Q3-Ref remained the
highest-energy core path at all three contexts. At 4096, Q2 was the lowest-energy
path, followed by Q0, Q1-W, Q4-Ref, and Q3-Ref.

### 13.3 Hard-retrieval quality

| Variant | Successes | Rate | Wilson 95% interval |
|---|---:|---:|---:|
| Q0 | 53/60 | 0.883 | [0.778, 0.942] |
| Q1-W | 48/60 | 0.800 | [0.682, 0.882] |
| Q2 | 1/60 | 0.0167 | [0.00295, 0.0886] |
| Q3-Ref | 49/60 | 0.817 | [0.701, 0.894] |
| Q4-Ref | 1/60 | 0.0167 | [0.00295, 0.0886] |

Eviction failed at every depth: Q2 scored 0/20, 0/20, and 1/20 at 10%, 50%, and
90%. Q4-Ref had the identical depth profile. Paired against Q1-W, both paths had
47 losses, zero gains, and Bonferroni-adjusted exact p approximately `1.71e-13`.

Q3-Ref, by contrast, had one gain and zero losses relative to Q1-W. The paired
difference was +1/60 and the adjusted exact p was 1.0. Its four-bit numerical
reconstruction therefore preserved Q1-W-like hard retrieval in this sample,
while eviction did not.

## 14. Qwen Energy, Interaction, Sensitivity, and Pareto Findings

### 14.1 AWQ-to-eviction trade-off

At 4096, Q2 reduced mean energy by 71.27 J relative to Q1-W, or approximately
11.5%. Decode energy fell by 76.61 J. However, Holm correction over 20 energy
tests produced `p = 0.06556`, narrowly above 0.05; decode runtime and throughput
did not differ significantly. More importantly, the path lost 47 of 48 Q1-W
retrieval successes.

This is the clearest example of why energy-only optimization is insufficient. Q2
can appear attractive on an energy axis and still be infeasible under almost any
reasonable retrieval constraint.

### 14.2 AWQ-to-TQ-Ref trade-off

Q3-Ref added 190.53 J relative to Q1-W at 4096, a 30.6% increase. Decode energy
increased by 174.66 J, decode time by 2.60 s, and throughput fell by 4.59
tokens/s, approximately 35%. All four penalties remained significant after Holm
adjustment.

The quality result moved in the opposite direction: Q3-Ref achieved 49/60 versus
48/60 for Q1-W. Thus the accessible TQ-Ref path was quality-preserving but
systems-inefficient. This measured result should motivate implementation work,
not be generalized to a physically packed/fused TurboQuant kernel.

### 14.3 Compound path and shielding interaction

Q4-Ref used 628.69 J, only 6.94 J above Q1-W; total and decode energy were not
significantly different from Q1-W. Runtime and throughput were significantly
worse, however. Relative to Q2, Q4-Ref added 78.21 J and 76.26 decode joules,
with significant runtime and throughput penalties.

The total-energy interaction was `-112.32 J` with Holm `p = 0.00352`; decode
interaction was `-98.40 J` with Holm `p = 0.00739`. The direction was stable at
82 W and 70 W. As in Llama, eviction shielded TQ-Ref overhead by reducing retained
tokens before quantization. Q4-Ref's energy being close to Q1-W does not imply
that TQ-Ref was free. It means an energy-saving but quality-destroying eviction
path offset part of a costly reference quantization path.

Quality followed the eviction path, not the TQ-only path: Q4-Ref scored 1/60,
identical to Q2. A different implementation cannot be assumed to repair this
eviction failure unless it changes the eviction decisions or numerical outputs.

### 14.4 Budget sensitivity

At 4096:

| Variant | Mean energy (J) | Common-15 retrieval |
|---|---:|---:|
| Q2-B512 | 515.22 +/- 8.86 | 0/15 |
| Q2-B1024 | 550.48 +/- 10.07 | 1/15 |
| Q2-B1536 | 590.64 +/- 13.19 | 2/15 |

Larger budgets increased energy and recovered only limited quality. The common-15
sample is small, but no tested budget approached Q1-W quality. The result suggests
that the specific pyramidal scorer/budget distribution was poorly matched to
Qwen's retrieval behavior, not merely that 1024 was slightly too small.

### 14.5 Nominal-bit TQ sensitivity

The common 15 scenarios produced:

| Variant | Mean energy (J) | Retrieval | Wilson 95% interval |
|---|---:|---:|---:|
| Q3-Ref-TQ2 | 808.94 +/- 33.95 | 4/15 | [0.109, 0.520] |
| Q3-Ref-TQ3 | 791.33 +/- 19.55 | 11/15 | [0.480, 0.891] |
| Q3-Ref-TQ4 | 812.28 +/- 13.11 | 12/15 | [0.548, 0.930] |

Two-bit quality was much lower, with eight paired losses and no gains relative to
four-bit on the common set, but Bonferroni adjustment and n=15 left the adjusted
p-value at 0.125. Three-bit differed by only one loss. Energy was non-monotonic in
nominal bits because all three reference settings still use uint8 physical
indices and unfused execution. These rows must not be described as measured
packed 2/3/4-bit caches.

### 14.6 Power and Pareto stability

Core, budget, and bit-width energy rankings were unchanged under 82 W and 70 W
trace clipping. All registered raw-versus-capped significance decisions were
stable.

The measured energy-quality Pareto analysis illustrates a subtle point. Q2 can
be non-dominated because it has the lowest energy, even though its retrieval is
nearly zero. Q0 is also a strong frontier point because it has high quality and
moderate energy. Q3-Ref's quality is competitive but its high energy gives it low
frontier-selection frequency. Pareto membership alone is not a deployment
recommendation; a minimum quality constraint is required.

### 14.7 Execution repairs and provenance

Notebook 08 required two in-session repairs:

1. The quality structural validator used the wrong active-cache field name for
   teacher-forced rows. The repair selected
   `teacher_forced_active_cache_updates` and resumed from committed shards.
2. The capped-analysis cell had a Pandas merge/analysis defect. The repair reran
   derived analysis from saved rows and traces without loading a model or
   recollecting measurements.

The exported notebook preserves both successful fixes inline, and persisted
measurements are complete, hash-consistent, and independently audited. However,
the experiment fingerprint and artifact manifest do not cryptographically bind
the executed notebook or repair-cell source bytes. This is a reproducibility
caveat, not a measurement-integrity failure.

The environment file also retains a stale descriptive status from before
completion. The authoritative acceptance marker is
`analysis/final_integrity.json`, not that stale string.

## 15. Cross-Model Synthesis

### 15.1 Status and integrity

Notebook 09 combines the accepted Llama and Qwen sources without collecting new
GPU measurements. Its local output is internally validated but remains
provisional:

| Field | Value |
|---|---|
| Schema | `cse407-cross-model-synthesis-v1-2026-08-05-1` |
| Fingerprint | `b19adce0924b4203` |
| Output files | 41 |
| Source validation gates | 36, all passed |
| Source traces reintegrated | 195 |
| Normalized energy rows | 585 |
| Normalized quality rows | 885 |
| Empirical Pareto rows | 10 |
| Conditional/robust symbolic rows | 19,272 each |

The synthesis verifies input manifests, identities, schemas, fingerprints,
sessions, row counts, unique keys, JSON/CSV correspondence, trace hashes, and
reintegrated energies before joining data. It rehashes sources at the end and
records that they were unchanged.

The provisional status is a provenance/acceptance boundary, not a failed
integrity gate. The bundle passed its registered proof conditions, but a single
canonical Notebook 09 source has not yet been independently promoted as accepted
A5 evidence.

### 15.2 Baseline asymmetry

Cross-model interpretation preserves different baseline structures:

- Llama context-matrix energy: stock C1;
- Llama matched-wrapper control: C1-W at 4096 only, separate session;
- Qwen context-matrix energy: matched-wrapper Q1-W;
- compound baseline: C2 for Llama and Q2 for Qwen.

Absolute Llama and Qwen joules are not paired observations. Model geometry,
tokenization, prompts, wrappers, sessions, and software paths differ. The
synthesis therefore prioritizes within-model relative effects and treats
cross-model contrasts as independent descriptive bootstraps.

### 15.3 Cross-model quality contrast

The within-model eviction effects on hard-60 retrieval were:

| Contrast | Estimate | Bootstrap 95% interval |
|---|---:|---:|
| Llama C2 minus C1-W | -0.0167 | [-0.050, 0.000] |
| Qwen Q2 minus Q1-W | -0.7833 | [-0.867, -0.683] |
| Qwen effect minus Llama effect | -0.7667 | [-0.867, -0.667] |

The contrast is large and practically important: the same semantic eviction role
was nearly neutral for Llama and catastrophic for Qwen. Architecture alone is
not identified as the cause. Plausible contributors include model geometry,
attention distributions, tokenizer-specific prompt materialization, adapter
details, and scorer/model interaction. With only two models and one main session
per model, this is evidence of model dependence, not a general architecture law.

### 15.4 Cross-model interaction pattern

Both models had negative sequential energy interactions:

- Llama total interaction: -152.03 J, but stock-C1 versus wrapped-path
  confounding remains;
- Qwen total interaction: -112.32 J within a matched session;
- both remained negative under 82 W and 70 W trace clipping.

This repeated direction supports a systems mechanism: eviction reduces retained
tokens before TQ-Ref, so the expensive reference transform and materialized state
operate over less cache. The magnitude should not be directly compared as if the
models shared a paired unit.

### 15.5 Measured multi-objective frontier

At 4096, the empirical frontier uses measured raw energy, hard retrieval, and
persistent KV bytes:

- Llama C2 is attractive because it combines the lowest Llama energy, 119 MiB
  decode cache, and retrieval only one scenario below C1-W;
- Llama C3/C4 are dominated or unstable because TQ-Ref adds energy and storage
  without improving hard retrieval;
- Qwen Q0 is the strongest high-quality measured point;
- Qwen Q2 is low-energy/low-memory but almost zero-quality, demonstrating why a
  quality constraint is necessary;
- Qwen Q3-Ref preserves quality but is high-energy and high-storage in realized
  form.

Bootstrap frontier frequency is interpreted only as resampling selection
stability. It is not the probability that a configuration is truly optimal.

## 16. Ideal TurboQuant Realization-Gap Analysis

### 16.1 Three evidence tiers

Notebook 09 explicitly separates:

1. measured FP16/AWQ/eviction systems behavior;
2. measured numerical TQ-Ref with uint8 indices, materialized K/V, and unfused
   execution;
3. an analytical ideal that packs indices at nominal width, removes persistent
   materialized K/V, retains FP32 norms and a 128-token FP16 residual, and assumes
   fused reconstruction remains in registers/shared memory.

TQ-Ref is not called a simulation because it really changes numerical K/V values
and affects model outputs. The ideal is not called measured because no such
kernel was run.

### 16.2 Packed persistent-KV model

For batch one, model KV heads `H`, head dimension `d`, FP bytes `s_fp`, retained
tokens `B_l`, residual `r_l = min(128, B_l)`, nominal bits `q`, and norm bytes
`s_norm = 4`:

```text
M_FP = 2 * H * d * s_fp * sum_l(B_l)

M_ideal = 2 * H * sum_l(
    (B_l - r_l) * (d * q / 8 + s_norm)
    + r_l * d * s_fp
) + metadata
```

The implementation applies tensorwise bit ceilings and declared alignment. The
current envelope uses one-byte alignment and zero persistent metadata, making it
optimistic by design but explicit and testable.

Before projection, unit gates reproduced accepted retained FP16 bytes and the
realized eight-bit logical TQ payload. Bit-width and budget monotonicity passed.
Every reported ideal row was smaller than matched FP16 persistent KV because
packed-index savings exceeded norms, residuals, alignment, and metadata.

### 16.3 Measured, realized, and ideal storage

Four-bit decode storage illustrates the realization gap:

| Model/path | Matched non-TQ | Realized TQ-Ref | Ideal packed | Ideal / matched FP |
|---|---:|---:|---:|---:|
| Llama TQ-only | 455.00 MiB | 696.50 MiB | 131.14 MiB | 28.82% |
| Llama eviction+TQ | 119.00 MiB | 187.25 MiB | 41.89 MiB | 35.20% |
| Qwen TQ-only | 146.25 MiB | 223.88 MiB | 42.15 MiB | 28.82% |
| Qwen eviction+TQ | 38.25 MiB | 60.19 MiB | 13.46 MiB | 35.20% |

The normalized ratios match across models because the declared representation
scales with geometry. Qwen's absolute cache is smaller primarily because it has
two KV heads versus Llama's eight. The compound ideal ratio is higher than the
TQ-only ratio because the fixed 128-token residual is a larger fraction of a
smaller evicted cache.

For non-evicted decode, ideal storage rises monotonically from approximately
16.7% of FP16 at two bits to 22.8% at three bits and 28.8% at four bits. With
eviction, the corresponding ratios are approximately 24.2%, 29.7%, and 35.2%.
Unobserved 2/3-bit compound rows are valid storage-only algebra; they have unknown
quality and no numerical energy eligibility.

These values are persistent/cache-live representation sizes, not total peak
VRAM. They exclude weights, allocator reserves, kernels, temporary workspace,
and other live tensors. Tensor descriptors were reconstructed from runtime
contracts and persisted aggregate/category bytes because no direct live tensor
dump was preserved.

### 16.4 Modeled phase byte demand

The ideal analysis models logical compulsory dataflow, not exact hardware DRAM
traffic. Full-prompt attention happens before eviction/quantized persistence, so
prefill cannot claim compressed attention reads. Packing introduces a conversion
read and compressed writes. Decode then repeatedly reads the growing cache; a
fused implementation can potentially avoid materialized reconstruction writes.

For the observed four-bit paths, modeled `Delta_D = baseline - ideal` is:

| Model/path | Prefill Delta | Decode Delta | Total Delta |
|---|---:|---:|---:|
| Llama TQ-only | -0.126 GiB | +20.074 GiB | +19.948 GiB |
| Llama eviction+TQ | -0.039 GiB | +4.656 GiB | +4.617 GiB |
| Qwen TQ-only | -0.041 GiB | +6.452 GiB | +6.411 GiB |
| Qwen eviction+TQ | -0.013 GiB | +1.496 GiB | +1.484 GiB |

Negative prefill values mean conversion adds logical demand. Positive decode and
total values mean the declared fused path avoids modeled demand over the fixed
64-token decode. Cache hits, SDPA tiling, compiler fusion, allocator copies, GQA
expansion traffic, and actual DRAM transactions are not identified.

### 16.5 Partially identified energy model

Ideal energy is represented as:

```text
E_ideal = E_baseline - epsilon_mem * Delta_D + O_net
```

`epsilon_mem` is path/session/regime-specific effective joules per avoided
modeled byte. `O_net` includes rotations, packing/reconstruction compute,
launch/control overhead, occupancy and runtime changes, and changed static or
background energy. Modeled index/norm/residual traffic is already included in
`Delta_D` and must not be double-counted in `O_net`.

When `Delta_D > 0`, strict reduction requires:

```text
O_net < epsilon_mem * Delta_D
epsilon_mem > O_net / Delta_D
```

No justified finite domain was available for either unknown. The notebook
therefore produced parameter-free symbolic boundaries and a zero-net-overhead
reference envelope, but no numerical ideal joules or projected numerical energy
Pareto point. The zero-overhead envelope is not an achievable best case; it is a
conditional mathematical reference.

### 16.6 Quality transfer and eligibility

Measured TQ-Ref quality may transfer to an ideal implementation only under strict
output equivalence: same observed nominal-bit path, indices, norms, residual
policy, reconstruction, eviction order, accumulation/reduction order, logits,
and greedy output. Outside that condition, implementation-induced quality change
is an unidentified structural parameter.

Eligibility rules prevent accidental extrapolation:

- four-bit TQ-only and compound hard paths are eligible for conditional
  equivalence analysis;
- Qwen 2/3/4-bit TQ-only quality uses exactly the common 15 scenarios;
- Llama historical 2/3-bit quality is excluded from hard-quality analysis;
- unobserved low-bit compound footprints are storage-only;
- an ideal implementation is never assumed to repair eviction quality.

## 17. Accepted Visualization Products and Figure Interpretations

### 17.1 Bundle identity

The downloaded visualization bundle is stored at
`evidence/accepted/CSE407_cross_model_visualization_v1/`.

| Field | Value |
|---|---|
| Schema | `cse407-cross-model-visualization-v1-2026-08-07-1` |
| Visualization fingerprint | `53ead4e6db45d2a8` |
| Source synthesis fingerprint | `b19adce0924b4203` |
| Source unchanged | True |
| Figures | 8 |
| PNG/PDF figure files | 16 |
| Directory files | 23 |
| Numerical ideal energy claimed | False |
| Downloaded archive SHA-256 | `e718e64193f2b162f674d87d5654935ba1f879fa5064243e4e30c3493ae0eb88` |

The bundle was generated in a CPU-only Colab notebook that downloaded the public
project ZIP with `gdown` and did not mount Google Drive. Its manifest hashes the
16 figure files, two derived CSVs, findings, metrics, and protocol. The manifest
itself and final-integrity marker complete the 23-file local directory.

The figures are accepted as visualization artifacts, but their numerical source
remains the provisional synthesis. Paper captions must retain that provenance.

### 17.2 Figure 1: measured TQ-Ref overhead

`fig01_measured_tq_overhead` plots all five paired-block percentage changes plus
mean and SD for prefill, decode, and total energy at each context.

Visible patterns include:

- Llama TQ-only total overhead rises from roughly 38% at 1024 to 45% at 4096;
- Llama TQ-only decode overhead rises especially sharply, reaching roughly 80%
  at 4096;
- eviction reduces Llama compound prefill overhead toward zero as context grows,
  but decode overhead remains large;
- Qwen TQ-only total overhead is about 22%, 36%, and 31% across contexts;
- Qwen compound total overhead falls to about 14.2% at 4096;
- all plotted mean energy overheads remain above zero.

The metrics file records 4096 total-overhead means of 44.72% for Llama TQ-only,
24.75% for Llama eviction+TQ, 30.79% for Qwen TQ-only, and 14.22% for Qwen
eviction+TQ. The Llama TQ-only comparison remains wrapper-confounded.

### 17.3 Figure 2: measured context scaling

`fig02_measured_context_scaling` separates prefill energy, decode energy, and
decode throughput in six panels. This avoids misleading dual axes.

The figure shows that prefill energy increases similarly for most paths because
full-prompt attention precedes post-attention compression. The largest
configuration differences occur in decode. At 4096, eviction sharply lowers
Llama decode energy and increases throughput, while TQ-Ref sharply raises decode
energy and lowers throughput. Qwen shows the same reference-overhead direction,
but its eviction throughput improvement is limited even though decode energy is
lower.

### 17.4 Figure 3: retrieval and bit sensitivity

`fig03_retrieval_wilson` presents separate Wilson-interval panels for Llama
hard-60, Qwen hard-60, and Qwen common-15 TQ bits. This prevents the 15-scenario
low-bit results from being visually treated as 60-scenario estimates.

The figure makes three results immediately visible:

- Llama's C2/C3/C4 estimates cluster closely around C1-W;
- Qwen Q2/Q4 collapse near zero while Q3-Ref overlaps Q1-W;
- Qwen quality improves from 4/15 at two bits to 11/15 at three bits and 12/15 at
  four bits, with wide intervals due to n=15.

### 17.5 Figure 4: four-bit storage realization gap

`fig04_storage_realization_gap` uses a logarithmic storage axis and three bars for
each phase/path: matched non-TQ, realized TQ-Ref, and ideal packed/fused.

The realized TQ-Ref bars are always above matched non-TQ because materialized K/V
is retained together with quantization state. The ideal bars are always far
below both. For example, Llama TQ-only prefill is approximately 448.0 MiB matched,
1119.8 MiB realized, and 129.3 MiB ideal; decode is 455.0, 696.5, and 131.1 MiB.
The drop in realized storage from prefill to decode reflects released/transient
backing categories in the accepted accounting, while persistent ideal storage
changes only slightly with 64 additional tokens.

### 17.6 Figure 5: ideal packed components

`fig05_ideal_packed_components` decomposes ideal storage into packed indices,
FP32 norms, FP16 residual, and metadata as a fraction of matched FP16. The
two- and three-bit Llama TQ-only and both models' unobserved low-bit compound
paths are hatched as storage-only where quality/energy eligibility is absent.

Packed indices grow with bit width, while the norm and residual components remain
fixed for a given retained-token structure. The matching normalized ratios across
models confirm that the model is geometry-normalized rather than claiming equal
absolute bytes.

### 17.7 Figure 6: modeled phase demand

`fig06_modeled_phase_byte_demand` uses dumbbells from matched baseline demand to
ideal modeled demand. Prefill ideal diamonds sit to the right of baseline circles,
showing conversion cost. Decode ideal diamonds sit far to the left, showing
modeled savings over 64 growing-cache reads.

Two-bit paths have the largest modeled decode savings because they have the
smallest packed index stream. Eviction reduces absolute demand and therefore
reduces the amount of traffic available to save. This helps explain why
eviction shields TQ overhead but also makes the ideal TQ opportunity smaller in
absolute bytes.

### 17.8 Figure 7: symbolic break-even

`fig07_symbolic_energy_break_even` plots the maximum allowable
`O_net/epsilon_mem` in GiB-equivalent modeled bytes for each observed path. It is
not an energy bar chart.

The boundaries are largest for non-evicted two-bit paths and smallest for
four-bit compound paths. Examples are 23.42 GiB-equivalent for Llama TQ-only
two-bit, 19.95 for Llama four-bit, 4.62 for Llama compound four-bit, 7.53 for
Qwen two-bit, 6.41 for Qwen four-bit, and 1.48 for Qwen compound four-bit.

Conditional energy reduction lies below each boundary, subject also to
`epsilon_mem > 0` and nonnegative energy. The plot intentionally does not choose
values for either unknown.

### 17.9 Figure 8: measured energy-quality-memory Pareto view

`fig08_measured_pareto_energy_quality_memory` uses measured points only. Horizontal
error bars are energy SD, vertical bars are Wilson quality intervals, marker area
encodes persistent KV storage, and edge width encodes bootstrap frontier
selection stability.

The Llama panel shows C2 as a compelling low-energy, low-memory point with quality
close to C1-W. The Qwen panel visually separates two incompatible regions: Q2 is
low-energy but near-zero quality; Q0/Q1-W are moderate-energy high-quality; and
Q3-Ref is high-energy high-quality. The plot demonstrates why an unconstrained
Pareto frontier must be supplemented with an explicit minimum-quality rule.

### 17.10 Recommended paper use

The strongest main-paper candidates are:

1. Figure 1 for the measured reference implementation overhead;
2. Figure 3 for the cross-model quality difference;
3. Figure 4 for the measured-realized-ideal storage gap;
4. Figure 8 for the deployment trade-off.

Figures 5-7 fit naturally in an analytical extension or appendix because they
depend on explicit ideal-layout/dataflow assumptions. Figure 2 supports detailed
systems discussion and can be used when page space permits.

## 18. Statistical Interpretation

### 18.1 Test framework and multiplicity

The project uses paired tests wherever a true within-session blocking structure
exists: five paired energy blocks per model/configuration/context, and 60 paired
quality scenarios stratified by three depth bins. Holm sequential adjustment
controls the familywise error rate within each registered test family. Wilcoxon
signed-rank tests serve as non-parametric alternatives for small-sample energy
comparisons (n=5). McNemar exact tests address paired binary quality outcomes.

Multiple testing and small n constrain resolution. With five blocks per
comparison, the minimum detectable Holm-adjusted p-value for any single test is
limited, and confidence intervals on differences remain wide. The strategy is
therefore to emphasize effect sizes and intervals alongside adjusted p-values and
to avoid interpreting non-significance as proven equivalence.

### 18.2 Llama energy inferences at 4096

The Llama v5 core energy tests at 4096 produced the following adjusted results:

| Comparison | Mean diff (J) | 95% CI (J) | Holm p | Decision |
|---|---:|---:|---:|---|
| C1 vs C2 | +101.95 | [73.81, 130.08] | 0.00549 | C2 lower; significant |
| C1 vs C3-Ref | −282.24 | [−287.23, −277.25] | 1.88e-7 | C3 much higher; significant |
| C1 vs C4-Ref | −28.26 | [−60.28, 3.76] | 0.2465 | Not significant after adjustment |
| C2 vs C4-Ref | −130.21 | [−168.32, −92.09] | 0.00620 | C4 higher; significant |
| C3-Ref vs C4-Ref | +253.98 | [226.93, 281.02] | 0.000206 | C4 lower; significant |

Decode energy, decode time, and throughput tests yielded consistent decisions.
The C1-vs-C4-Ref non-significance after Holm correction means the adjusted
evidence does not support a significant total-energy difference between stock AWQ
and the compound reference path. However, this is a five-block test with wide
intervals, not proof of exact energy equivalence.

### 18.3 Qwen energy inferences at 4096

Qwen used matched Q1-W wrapper throughout, eliminating the Llama
stock-versus-wrapper confound. The Holm-adjusted Qwen core energy tests produced:

| Comparison | Metric | Raw significant | Stable at 82 W | Stable at 70 W |
|---|---|:---:|:---:|:---:|
| Q1-W vs Q2 | Total energy | No | Yes (unchanged) | Yes (unchanged) |
| Q1-W vs Q3-Ref | Total energy | Yes | Yes | Yes |
| Q1-W vs Q4-Ref | Total energy | No | Yes (unchanged) | Yes (unchanged) |
| Q2 vs Q4-Ref | Total energy | Yes | Yes | Yes |
| Q3-Ref vs Q4-Ref | Total energy | Yes | Yes | Yes |
| Q1-W vs Q2 | Decode energy | No | Yes (unchanged) | Yes (unchanged) |
| Q1-W vs Q3-Ref | Decode energy | Yes | Yes | Yes |
| Q1-W vs Q4-Ref | Decode energy | No | Yes (unchanged) | Yes (unchanged) |
| Q1-W vs Q4-Ref | Decode time | Yes | Yes | Yes |
| Q1-W vs Q4-Ref | Throughput | Yes | Yes | Yes |

The Q1-W-vs-Q2 total energy contrast was `p = 0.06556` under Holm correction —
a near-marginal result. Despite Q2 showing 71.27 J less mean energy than Q1-W,
the adjusted test did not cross the 0.05 threshold. This marginal p-value should
not be over-interpreted in either direction: a larger sample could resolve it.
Importantly, Q2's 1/60 retrieval rate makes its energy advantage practically
unusable regardless of energy significance.

### 18.4 Sequential interaction significance

The registered interaction contrasts `I = (compound − TQ-only) − (eviction − AWQ)`
measure whether eviction modifies TQ-Ref overhead:

| Model | Regime | Metric | Mean I | 95% CI | Holm p |
|---|---|---|---:|---:|---:|
| Llama | Raw | Total energy | −152.03 | [−187.11, −116.96] | 0.00109 |
| Llama | Raw | Decode energy | −126.00 | [−160.08, −91.92] | 0.00152 |
| Llama | Raw | Decode time | −1.74 s | [−2.33, −1.16] | 0.00234 |
| Llama | Raw | Throughput | −1.70 tok/s | [−4.05, 0.66] | 0.1164 (n.s.) |
| Qwen | Raw | Total energy | −112.32 | [−147.36, −77.28] | 0.00352 |
| Qwen | Raw | Decode energy | −98.40 | [−138.66, −58.14] | 0.00739 |
| Qwen | Raw | Decode time | −0.65 s | [−1.54, 0.24] | 0.2227 (n.s.) |
| Qwen | Raw | Throughput | +1.09 tok/s | [−1.39, 3.57] | 0.2895 (n.s.) |

Both models showed significant negative total and decode energy interactions:
eviction shielded TQ-Ref overhead by shrinking the cache before the reference
quantization transform. The Llama interaction magnitude was larger, but the
Llama stock-C1 baseline was not wrapper-matched. Throughput and decode time
interactions were not significant for both models after adjustment, consistent
with the eviction-shielding effect being energy-dominated rather than
throughput-dominated at these sample sizes.

### 18.5 Hard-quality Wilson intervals and cross-model contrast

At 4096 tokens with n=60, the Wilson 95% intervals for aggregate retrieval were:

| Model | Variant | Rate | Wilson 95% |
|---|---|---:|---|
| Llama | C0 | 0.783 | [0.664, 0.869] |
| Llama | C1-W | 0.633 | [0.507, 0.744] |
| Llama | C2 | 0.617 | [0.490, 0.729] |
| Llama | C3-Ref | 0.617 | [0.490, 0.729] |
| Llama | C4-Ref | 0.617 | [0.490, 0.729] |
| Qwen | Q0 | 0.883 | [0.778, 0.942] |
| Qwen | Q1-W | 0.800 | [0.682, 0.882] |
| Qwen | Q2 | 0.017 | [0.003, 0.089] |
| Qwen | Q3-Ref | 0.817 | [0.701, 0.894] |
| Qwen | Q4-Ref | 0.017 | [0.003, 0.089] |

All Llama AWQ-derived paths overlapped heavily and differed from C1-W by one
scenario. All Qwen non-eviction AWQ-derived paths overlapped, while Q2 and Q4-Ref
were separated from Q1-W by the entire interval width. The Bonferroni-adjusted
McNemar p for Q2 and Q4-Ref versus Q1-W was approximately `1.71e-13`.

The depth-stratified paired bootstrap cross-model eviction contrast was:

| Contrast | Estimate | Bootstrap 95% CI |
|---|---:|---|
| Llama C2 − C1-W | −0.017 | [−0.050, 0.000] |
| Qwen Q2 − Q1-W | −0.783 | [−0.867, −0.683] |
| Qwen effect − Llama effect | −0.767 | [−0.867, −0.667] |

The cross-model difference in eviction impact was large and practically
important. The bootstrap interval for the contrast does not contain zero. However,
this is evidence of model dependence from two models with different architectures,
tokenizers, prompts, and sessions — not a causal identification of the
architecture feature responsible.

### 18.6 Sensitivity-population quality: Qwen low-bit TQ

The common-15 scenario subset yielded:

| Variant | Successes | Rate | Wilson 95% |
|---|---:|---:|---|
| Q3-Ref (4-bit) | 12/15 | 0.800 | [0.548, 0.930] |
| Q3-Ref-TQ3 | 11/15 | 0.733 | [0.480, 0.891] |
| Q3-Ref-TQ2 | 4/15 | 0.267 | [0.109, 0.520] |

The two-bit path showed substantially lower quality, but the Bonferroni-adjusted
paired McNemar p for two-bit versus four-bit was 0.125 (n=15 limits power). The
three-bit path lost only one scenario relative to four-bit. The wide Wilson
intervals reflect the small quality-sensitivity sample and should not be confused
with the 60-scenario main estimates.

### 18.7 Energy ranking and significance stability

Across all registered raw-versus-capped stability checks:

- **Llama:** All 40 significance decisions (5 comparisons × 4 metrics × 2 cap
  regimes) were unchanged. All core and sensitivity energy rankings were preserved
  under 82 W and 70 W clipping.
- **Qwen:** All registered raw-versus-capped significance decisions were stable
  at both 82 W and 70 W for all comparisons and metrics.

No registered decision flipped. This is a strong robustness result showing that
isolated NVML power transients (including samples up to 124.496 W for Llama and
116.109 W for Qwen) did not drive the main energy conclusions.

### 18.8 Bootstrap Pareto frontier interpretation

At 4096 tokens, the measured three-objective Pareto frontier (raw total energy,
hard retrieval, persistent KV bytes) contained the following points under 2000
bootstrap resamples:

| Model | Variant | Energy (J) | Retrieval | Storage (MiB) | Point member | Bootstrap freq |
|---|---|---:|---:|---:|:---:|---:|
| Llama | C0 | 701.08 | 0.783 | 455.0 | Yes | 100.0% |
| Llama | C1-W | 639.86 | 0.633 | 455.0 | Yes | 63.0% |
| Llama | C2 | 529.30 | 0.617 | 119.0 | Yes | 100.0% |
| Llama | C3 | 913.48 | 0.617 | 696.5 | No | 0.0% |
| Llama | C4 | 659.50 | 0.617 | 187.2 | No | 0.6% |
| Qwen | Q0 | 616.78 | 0.883 | 146.2 | Yes | 97.2% |
| Qwen | Q1-W | 621.75 | 0.800 | 146.2 | No | 36.0% |
| Qwen | Q2 | 550.48 | 0.017 | 38.3 | Yes | 100.0% |
| Qwen | Q3-Ref | 812.28 | 0.817 | 223.9 | No | 3.8% |
| Qwen | Q4-Ref | 628.69 | 0.017 | 60.2 | No | 0.0% |

Bootstrap frequency is resampling selection stability, not the probability that a
configuration is truly optimal. C3 and C4 were never or rarely selected because
TQ-Ref increased both energy and storage without improving hard retrieval on
Llama. Q2 was always selected on energy and storage axes but would be excluded by
any minimum-quality constraint above approximately 2%. Q3-Ref was rarely selected
because its high energy dominated its quality advantage over Q1-W.

C2 is the most compelling measured point for Llama: it combined the lowest Llama
energy, the smallest persistent cache, and retrieval only one scenario below
C1-W. For Qwen, Q0 was the strongest quality-energy combination, while Q2
demonstrated why a quality gate is essential before interpreting Pareto
membership.

### 18.9 What the statistics do and do not establish

The registered statistical evidence establishes:

1. Eviction reduces long-context energy relative to AWQ baseline (Llama
   significant; Qwen marginal after Holm adjustment).
2. The accessible TQ-Ref path increases energy substantially (both models
   significant).
3. Sequential eviction-then-TQ shows a significant negative energy interaction
   (both models), meaning eviction partially shields TQ-Ref overhead.
4. Hard retrieval was nearly identical across Llama compression paths but
   catastrophically degraded by eviction on Qwen.
5. Energy rankings and significance decisions were robust to power-trace
   clipping.
6. The empirical Pareto frontier is well-separated, but Pareto membership alone
   is not a deployment recommendation.

The registered evidence does not establish:

- That C1-W and C4-Ref have exactly equal energy (non-significance ≠ equivalence).
- That eviction failure on Qwen was caused by architecture rather than scorer,
  budget, or adapter interaction.
- That TQ-Ref overhead would persist in a packed/fused implementation.
- That Llama quality preservation extends to contexts longer than 4096 or harder
  tasks.
- Any causal cross-model ordering because models were tested in separate sessions
  with different architectures and tokenizers.

## 19. Failures, Repairs, and Provenance Caveats

### 19.1 Failed hard-retrieval pilots (Notebooks 01-04)

Three of four hard-retrieval calibration pilots were classified
`TOO_HARD_REDUCE_DIFFICULTY` and their result rows discarded:

| Pilot | Fingerprint | C1-W rate | C2 rate | Failure type |
|---|---|---:|---:|---|
| V1 | `b0e6646087995e5f` | 0.50 | 0.50 | Too many confusing records (48 records) |
| V2 | `922e8877398679eb` | 0.50 | 0.50 | Reduced record count insufficient (32 records) |
| V3 | `43041ef3243f87a3` | 0.25 | 0.17 | Close siblings increased confusion |
| V4 | `15a1017ec54949b9` | 0.75 | 0.75 | Passed — accepted for prompt freeze only |

V4 rows remained discarded because they influenced the frozen benchmark design.
All four pilot directories are preserved under `evidence/discarded/bundles/`.
The failure sequence itself is a positive methodological outcome: it prevented a
final benchmark with insufficient baseline headroom.

### 19.2 Notebook 08 in-session repairs

The Qwen full-reference experiment required two in-session repair cells:

**Repair 1: quality structural validator.** The validator referenced an incorrect
active-cache field name during teacher-forced quality collection. The fix
selected `teacher_forced_active_cache_updates` and resumed from committed shards
without recollecting measurements.

- Repair source SHA-256:
  `1c7e7b2220173911d4b6dc382ea63b92be964714c48037a5485fb355c9909484`
  (`repairs/colab_fix_quality_collection_cell.py`)

**Repair 2: capped-analysis cell.** A Pandas merge/analysis defect broke the
capped-energy integration cell. The fix reran derived analysis from persisted
rows and traces without loading a model or recollecting measurements.

- Repair source SHA-256:
  `d5fe5f49936457d157dc8982cea4e0ceb3ce4ff1107537752a24999ae119432f`
  (`repairs/colab_fix_analysis_cell.py`)

The exported notebook preserves both successful fixes inline. However, the
experiment fingerprint `861d89617e53034d` and the artifact manifest SHA-256
`975cb8f19405f9d7e4267bc4a8143ead943c853776c6ba88b8697695ac78c1c9` bind the
output artifacts, not the executed notebook source or repair-cell bytes. This is
a reproducibility caveat, not a measurement-integrity failure: persisted
measurements and traces are hash-consistent and independently audited, but exact
reproducing the same Colab cell execution sequence requires the repaired notebook
rather than the pre-repair source.

### 19.3 Stale environment status field

The Qwen environment file `qwen_full_environment.json` retains a `status` field
set to `VALIDATION_PASSED_MEASUREMENTS_PENDING`. This string was written before
measurement collection began and was never updated during the session. The
authoritative acceptance marker is `analysis/final_integrity.json`, which records
`"passed": true`, the correct fingerprint, all row counts, and trace
reintegration results. The stale status field should not be interpreted as
evidence that measurements are incomplete.

### 19.4 Llama stock-versus-wrapper confound

Historical Llama systems energy used stock C1 (no attention wrapper) at all three
contexts. The matched-wrapper C1-W control was collected only at 4096 tokens in a
separate session. Consequently:

- The Llama context-scaling results (Section 7) compare C2/C3/C4 against stock C1,
  not matched C1-W. The stock-to-wrapper difference was small
  (~8.61 J at 4096) but not zero.
- The Llama TQ-only energy overhead (Section 17, Figure 1) uses stock C1 as the
  denominator and is therefore wrapper-confounded.
- The Llama sequential interaction contrast (Section 18.4) uses stock C1 in the
  `(C2 − C1)` arm, introducing a potential wrapper offset.
- Qwen used matched Q1-W throughout, making its TQ-only and interaction contrasts
  wrapper-clean.

This asymmetry should be reported in the paper. It does not invalidate the Llama
results, but it makes Qwen's within-session contrasts more precisely identified.

### 19.5 Synthesis provisional status

The cross-model synthesis (Notebook 09) passed all registered internal proof
gates and produced 41 output files under fingerprint `b19adce0924b4203`. It
remains provisional rather than accepted because a single canonical Colab
execution has not been independently completed and registered. The provisional
status is a provenance/acceptance boundary, not evidence of a validation failure.

Figures derived from the provisional synthesis must carry that provenance in
paper captions. Acceptance of the visualization bundle (fingerprint
`53ead4e6db45d2a8`) does not promote the source synthesis.

### 19.6 Notebook 09B acquisition pattern

The Notebook 09B visualization run used a CPU-only Colab notebook that downloaded
the public project ZIP via `gdown`, validated immutable provisional inputs, and
wrote only to `/content/CSE407_cross_model_visualization_v1/`. This pattern
eliminates Google Drive as a runtime dependency. The downloaded archive SHA-256
`e718e64193f2b162f674d87d5654935ba1f879fa5064243e4e30c3493ae0eb88` binds the
specific public ZIP version used.

However, the Notebook 09B source itself may not yet be in the local repository.
Preserving or exporting it is listed as an open item.

### 19.7 Source and version drift

The original proposal targeted Qwen3-4B and described BF16 baselines, contexts
512/2048/8192, three repetitions, thinking mode, and different configuration
labels. The executed study replaced the model, baseline precision, contexts,
configuration semantics, and sample sizes. The proposal LaTeX source
(`proposal/proposal.tex`) and canonical Markdown (`proposal/proposal.md`) still
contain superseded content. They must be updated to match executed evidence
before final paper submission.

The literature review (`proposal/literature_review.md`) references Qwen3-specific
papers and still frames the gap around Qwen3-4B. While the general technique
literature remains valid, Qwen3-specific sections should either be reframed as
historical motivation or annotated with the model change.

### 19.8 Tensor storage provenance

Ideal packed-KV storage projections reconstruct tensor descriptors from
runtime-asserted contracts (layer counts, KV heads, head dimension, retained
tokens, nominal bit widths) reconciled against persisted aggregate and category
byte totals. No direct live tensor dump was preserved from any session. The
projections are therefore structurally valid given their declared inputs but
cannot be independently verified against runtime memory allocator state.

## 20. Threats to Validity and Limitations

### 20.1 Construct validity

**Quality task scope.** Hard retrieval is one operationalization of quality. The
frozen 60-scenario benchmark uses exact code extraction at three depths within
4096 tokens. It does not cover open-ended generation, reasoning, summarization,
multilingual tasks, or contexts beyond 4096. A configuration that preserves hard
retrieval may still degrade other quality dimensions.

**Energy as joules from power traces.** Energy is trapezoidal integration of 10 Hz
NVML power samples over wall-clock time. This captures GPU board power
(including memory subsystem) but excludes CPU, host DRAM, cooling, and other
system components. The measurement is a valid relative indicator for comparing
configurations on the same hardware session but is not an absolute system-level
energy consumption metric.

**Throughput as decode tokens per second.** The fixed 64-token teacher-forced decode
provides a controlled throughput measurement. Real deployment uses variable-length
open-ended generation, which may differ in throughput behavior because of
different cache utilization patterns.

**Persistent KV storage versus total VRAM.** The project distinguishes persistent
KV cache bytes from peak allocated VRAM. Persistent storage accounts for the
declared cache representation only. Total peak VRAM includes weights, allocator
reserves, temporary buffers, kernel workspace, and other live tensors. The
project does not claim that ideal packed KV storage translates directly into the
same total VRAM reduction.

### 20.2 Internal validity

**Single session per model.** Each model's core matrix was collected in one Colab
session. Environmental factors — GPU thermal state, background load, Colab
scheduling, DRAM refresh, and runtime initialization — were shared across blocks
within a session but not independently varied. Cross-session comparisons
(including Llama C1-W versus v5 C1) are descriptive only.

**Five energy blocks.** Each configuration/context has five energy blocks. This
provides adequate power for large effects (the C2-vs-C1 and C3-vs-C1 contrasts)
but limits resolution for small effects. The C1-vs-C4 non-significance at 4096
may reflect either true proximity or insufficient sample size.

**Llama stock-versus-wrapper confound (Section 19.4).** The Llama v5 systems
matrix used stock C1 as the AWQ reference, while compressed paths used a custom
attention wrapper. The wrapper overhead was small at 4096 (~8.61 J), but it
introduces a systematic offset in all Llama contrasts involving C1.

**Qwen eviction failure mechanism.** The catastrophic eviction failure on Qwen
(1/60) is a measured outcome, but the responsible factor is not isolated. The
custom PyramidKV-style scorer, specific pyramidal budget distribution, Qwen's
8:1 GQA ratio, tokenizer-specific prompt materialization, and adapter interaction
are all plausible contributors. No ablation over eviction parameters at Qwen's
granularity was performed beyond the three-budget sensitivity check (B512, B1024,
B1536), which showed uniformly poor retrieval.

**Teacher-forced versus autoregressive decode.** Energy measurements used
teacher-forced 64-token decode for reproducibility. Autoregressive generation
with different output lengths and content could yield different energy and
throughput patterns because of changed cache access patterns and KV-growth
dynamics.

### 20.3 External validity

**Two models.** Llama 3.2-3B and Qwen2.5-3B have different layer counts (28 vs
36), GQA ratios (3:1 vs 8:1), native contexts (8K vs 32K), tokenizers, and
community AWQ implementations. The divergent eviction outcomes demonstrate that
results from one SLM do not automatically transfer to another. No claim of
general architecture-level findings is supported.

**One hardware platform.** All experiments used a single NVIDIA T4 on Google
Colab's free tier. Energy consumption, throughput, and power behavior may differ
on other GPU architectures (A100, L4, edge accelerators), different software
stacks, or different T4 instances with varying thermal environments.

**One eviction design.** The custom PyramidKV-style scorer used attention-based
importance scoring with a fixed observation window and pyramidal layer budget
averaging 1024. Alternative eviction methods (SnapKV, H2O, Ada-KV, ChunkKV),
different budget targets, different window sizes, or official KVCache-Factory
implementations might produce different quality and energy trade-offs.

**One TQ-Ref package version.** All TQ-Ref measurements used `turboquant==0.2.0`.
Future versions with different implementations, optimizations, or packed kernels
would constitute different evidence objects. The measured TQ-Ref overhead is
specific to the unfused, materialized-K/V, uint8-indexed reference path.

**One context window.** The hard-quality benchmark used exactly 4096 tokens with
tokenizer-specific materialization. Behavior at shorter contexts (where eviction
is less active) or longer contexts (approaching model native limits) is not
established.

**Free-tier Colab variability.** Google Colab free tier does not guarantee
consistent hardware assignment, thermal conditions, or background load. While
within-session blocking mitigates run-to-run variation, across-session
comparisons remain subject to uncontrolled environmental differences.

### 20.4 Statistical conclusion validity

**Multiple comparison adjustment.** Holm sequential correction was applied within
each test family. The familywise error rate is controlled within families, but
comparisons drawn across families (e.g., citing a Llama energy result alongside
a Qwen quality result) increase effective multiplicity.

**Wilson intervals at n=60 and n=15.** The 60-scenario Wilson intervals span
roughly ±13 percentage points around mid-range rates. The 15-scenario sensitivity
intervals are much wider (±20 pp or more). Small quality differences between
configurations may be real but unresolvable at these sample sizes.

**Bootstrap Pareto frequency.** Bootstrap frontier frequency measures resampling
stability. It is not the probability that a configuration is truly Pareto-optimal
in a population sense. Configurations with high frequency were consistently
selected under resampling; configurations with zero frequency were always
dominated.

**Interaction interpretation.** The sequential interaction `I = (C4−C3) − (C2−C1)`
measures whether the compound path deviates from the sum of individual component
effects. It does not decompose the mechanism. The Llama interaction uses a
confounded stock-C1 arm. Both models have n=5, so interaction precision is
limited.

### 20.5 Ethical and broader impact considerations

The project does not involve human participants, personal data, or sensitive
applications. Ethical considerations include:

- **Environmental reporting honesty.** The study measures real energy but cannot
  claim lifecycle emissions savings without accounting for production
  implementation effort, infrastructure changes, and embodied carbon.
- **Responsible compression claims.** Quality-destroying configurations (Qwen Q2)
  should not be recommended for deployment regardless of their energy advantage.
- **Publication of failure.** The three failed pilots and the Qwen eviction
  collapse are published rather than suppressed. Selective reporting of only
  successful paths would misrepresent the difficulty of compound compression.

## 21. Reproducibility and Artifact Map

### 21.1 Accepted evidence bundles

| Bundle | Path | Fingerprint | Files | Status |
|---|---|---|---:|---|
| Llama v5 systems | `evidence/accepted/bundles/CSE407_llama_v5_final/` | `8d27af8c9ee94de3` | 115 | Immutable historical/accepted |
| Llama hard quality/control | `evidence/accepted/bundles/CSE407_llama_track_a_full_v1/` | `106a561c07c62937` | 324 | Immutable accepted |
| Llama power robustness | `evidence/accepted/bundles/CSE407_llama_power_robustness_v1/` | `91ebc63773e735e6` | 15 | Immutable accepted derived |
| Qwen adapter pilot | `evidence/accepted/bundles/CSE407_qwen_track_a_adapter_pilot_v1/` | `91def77c920729e9` | 5 | Immutable accepted pilot |
| Qwen full reference | `evidence/accepted/bundles/CSE407_qwen_track_a_reference_v1/` | `861d89617e53034d` | 593 | Immutable accepted |
| Visualization | `evidence/accepted/CSE407_cross_model_visualization_v1/` | `53ead4e6db45d2a8` | 23 | Accepted visualization |

### 21.2 Provisional and discarded evidence

| Bundle | Path | Fingerprint | Files | Status |
|---|---|---|---:|---|
| Cross-model synthesis | `evidence/provisional/bundles/CSE407_cross_model_synthesis_local_provisional/` | `b19adce0924b4203` | 41 | Provisional, internally validated |
| Pilot V1 (discarded) | `evidence/discarded/bundles/CSE407_llama_track_a_pilot_discarded/` | `b0e6646087995e5f` | — | Discarded |
| Pilot V2 (discarded) | `evidence/discarded/bundles/CSE407_llama_track_a_pilot_v2_discarded/` | `922e8877398679eb` | — | Discarded |
| Pilot V3 (discarded) | `evidence/discarded/bundles/CSE407_llama_track_a_pilot_v3_discarded/` | `43041ef3243f87a3` | — | Discarded |
| Pilot V4 (discarded) | `evidence/discarded/bundles/CSE407_llama_track_a_pilot_v4_discarded/` | `15a1017ec54949b9` | — | Discarded (calibration only) |

### 21.3 Notebook inventory

| # | Notebook | Role | Status |
|---|---|---|---|
| 00 | `00_verify_historical_evidence.ipynb` | Verify v5 historical evidence | CPU, completed |
| 01 | `01_llama_hard_retrieval_pilot.ipynb` | V1 pilot | Completed, discarded |
| 02 | `02_llama_hard_retrieval_pilot_v2.ipynb` | V2 pilot | Completed, discarded |
| 03 | `03_llama_hard_retrieval_pilot_v3.ipynb` | V3 pilot | Completed, discarded |
| 04 | `04_llama_hard_retrieval_pilot_v4.ipynb` | V4 calibration pilot | Completed, prompt freeze accepted |
| 05 | `05_llama_full_quality_control_v1.ipynb` | Llama hard quality and C1-W control | Completed, accepted |
| 06 | `06_llama_power_robustness_analysis.ipynb` | Power trace robustness | CPU, completed, accepted |
| 07 | `07_qwen2_5_adapter_parity_pilot_v1.ipynb` | Qwen adapter parity | Completed, accepted pilot |
| 08 | `08_qwen2_5_full_reference_v1.ipynb` | Qwen full experiment | Completed, accepted (with repairs) |
| 09 | `09_cross_model_synthesis_v1_colab.ipynb` | Cross-model synthesis | CPU, completed, provisional |
| 09B | (Colab-connected, Drive-independent) | Visualization | CPU, completed, accepted figures |

All notebooks live under `experiments/track_a_failsafe_colab/`. The Notebook 09B
source may not yet be in the local repository and should be preserved.

### 21.4 Key integrity markers

Each accepted bundle contains a `final_integrity.json` file that records:

- schema version and experiment fingerprint;
- row counts for energy, quality, and sensitivity;
- trace reintegration pass/fail;
- unique-key gate;
- artifact manifest SHA-256 (where applicable);
- prompt-set and semantic SHA-256 hashes;
- completion timestamp.

The experiment registry (`research/experiment_registry.json`) binds each
experiment to its schema, fingerprint, model revisions, backend specification,
artifact path, and completion status. It also records pilot fingerprints,
discarded/accepted decisions, and repair provenance.

### 21.5 Measurement row summary

| Model | Energy rows | Quality rows | Power traces | Sensitivity energy | Sensitivity quality |
|---|---:|---:|---:|---:|---:|
| Llama v5 systems | 380 | (easy task, historical) | 95 | (included in 380) | (included) |
| Llama hard quality/control | 5 (C1-W only) | 300 | 5 | — | — |
| Qwen full reference | 75 core | 300 core | 95 | 20 | 60 |
| **Total unique measurement rows** | **460** | **600** | **195** | **20** | **60** |

The Llama power robustness analysis reintegrated all 100 Llama traces (95 v5 +
5 C1-W) without collecting new measurements. The cross-model synthesis joined
585 normalized energy rows and 885 normalized quality rows from both models.

### 21.6 Course submission mapping

The course requires specific submission artifacts:

| Artifact | Source | Status |
|---|---|---|
| Compiled PDF report | From LaTeX source | Not yet compiled |
| LaTeX source `.zip` | `proposal/ACM_Conference_Proceedings_Primary_Article_Template/` | Template present; paper content pending |
| `.bib` bibliography | `proposal/references.bib` (if present) or new | Needs updating to match executed evidence |
| Figures directory | `evidence/accepted/CSE407_cross_model_visualization_v1/` | 8 figure pairs (PNG+PDF) available |
| Private GitHub repository | Current workspace | Must add instructor as collaborator |
| Individual contribution % | Separate Google Sheet | Not in repository |
| `README.md` | Already exists at repository root and in notebooks | May need updating |

### 21.7 Reproducibility boundaries

A reviewer can independently verify:

- artifact manifest hashes against individual file hashes;
- final integrity JSON markers against claimed row counts;
- trace reintegration by re-running trapezoidal integration on raw power traces;
- quality rates and Wilson intervals from quality shard JSONs;
- statistical tests from CSV summaries;
- ideal storage projections from declared geometry and representation parameters.

A reviewer cannot independently verify without re-running in Colab:

- that the notebook source produces the same persisted artifacts (exact GPU state
  and runtime are not reproducible on free-tier Colab);
- that the Notebook 08 repair cells were the only modifications made during the
  session;
- that the `gdown`-acquired public ZIP for Notebook 09B exactly matches the local
  project state (the ZIP SHA-256 is recorded but the ZIP build is not versioned).

## 22. Paper-Ready Claims and Claims That Are Not Supported

### 22.1 Claims supported by accepted measured evidence

The following claims can appear in the paper results and discussion sections with
full provenance:

1. **AWQ reduces peak VRAM but does not uniformly reduce energy.** Llama C1
   reduced peak VRAM by approximately 30.5% at 4096 and energy by approximately
   10.0% relative to C0. However, at 1024, C1 consumed more energy and decoded
   more slowly than C0. Qwen Q1-W energy was approximately equal to Q0 at 4096.

2. **Eviction is context-dependent in its energy benefit.** Llama C2 reduced
   total energy by 101.95 J (16.15%) relative to C1 at 4096 (significant after
   Holm adjustment). At shorter contexts, the effect was smaller or reversed. Qwen
   Q2 reduced mean energy by 71.27 J (11.5%) relative to Q1-W but did not reach
   adjusted significance at p=0.05.

3. **The accessible TQ-Ref path adds substantial energy.** Llama C3 added
   282.24 J (44.7%) and Qwen Q3-Ref added 190.53 J (30.6%) at 4096, both
   significant. This is specific to the unfused, materialized-K/V reference path.

4. **Sequential eviction shields TQ-Ref overhead.** Both models showed
   significant negative total-energy interactions (Llama −152.03 J, Qwen
   −112.32 J). Prior eviction shortens the cache before TQ-Ref operates, reducing
   the expensive reference transform's scope.

5. **Eviction impact on hard retrieval is model-dependent.** Llama: C2/C3/C4 each
   differed from C1-W by only 1/60 scenarios. Qwen: Q2 and Q4-Ref scored 1/60
   versus Q1-W's 48/60. The cross-model eviction contrast was −0.767 with
   bootstrap 95% CI [−0.867, −0.667].

6. **TQ-Ref preserved quality while adding overhead.** Qwen Q3-Ref scored 49/60
   (one gain relative to Q1-W) despite using 30.6% more energy. Llama C3-Ref
   scored 37/60, matching C2 and C4-Ref.

7. **Energy rankings are robust to power-trace clipping.** All core and
   sensitivity rankings and all registered significance decisions were unchanged
   under 82 W and 70 W trace clipping for both models.

8. **Three failed pilots prevented a misleading benchmark.** Equal baseline and
   treatment failure rates in V1–V3 demonstrated benchmark difficulty, not equal
   model quality. The calibrated V4 prompt freeze restored useful headroom.

### 22.2 Claims supported by accepted derived or provisional evidence

These claims are analytically valid within their evidence tier but carry
additional provenance requirements in paper presentation:

9. **Persistent-KV memory dominance under ideal packing.** Under the declared
   packed representation (nominal-width indices, FP32 norms, 128-token FP16
   residual, one-byte alignment, zero metadata), ideal four-bit persistent KV is
   approximately 28.8% of matched FP16 for TQ-only and 35.2% for
   eviction-plus-TQ, across both model geometries. This is conditional on the
   declared layout. *Provenance: provisional synthesis.*

10. **Modeled decode byte-demand savings.** The fused ideal path avoids modeled
    logical byte demand during 64-token decode because compressed reads replace
    FP16 reads. Prefill adds conversion cost. These are logical demand estimates,
    not measured DRAM traffic. *Provenance: provisional synthesis.*

11. **Symbolic energy break-even.** A conditional inequality relates net
    implementation overhead to effective energy per avoided byte times modeled
    demand savings. No numerical ideal energy or projected Pareto point was
    produced. *Provenance: provisional synthesis.*

12. **Cross-model interaction direction stability.** Both models showed negative
    energy interactions under raw, 82 W, and 70 W regimes. The Llama interaction
    uses a confounded stock-C1 arm. *Provenance: synthesis of accepted sources.*

### 22.3 Claims that are explicitly NOT supported

The following claims must NOT appear in the paper because they lack evidence:

- **"TQ-Ref is packed/fused/physically 4-bit."** All TQ-Ref measurements use
  uint8 indices and retain materialized K/V. No packed kernel was executed.

- **"Ideal energy is X joules."** No numerical ideal energy, latency, throughput,
  power, or peak VRAM was identified. `epsilon_mem` and `O_net` have no justified
  measured domains.

- **"Eviction failure on Qwen was caused by GQA ratio / architecture."** The
  mechanism is not isolated. Architecture, scorer, budget, tokenizer, and adapter
  are all confounded.

- **"Llama quality results generalize to longer contexts or harder tasks."** The
  benchmark used exactly 4096 tokens with 60 frozen scenarios. Performance at
  different contexts, task types, or difficulty levels is unknown.

- **"AWQ provides uniform energy savings across all contexts."** AWQ was more
  expensive than FP16 at 1024 on Llama and approximately equal on Qwen at 4096.

- **"The compound path is energy-equivalent to AWQ baseline."** The Llama
  C1-vs-C4 non-significance is a five-block test with intervals crossing zero.
  Non-significance ≠ equivalence.

- **"Two-bit TQ-Ref quality is comparable to four-bit."** The common-15 Qwen
  sample showed 4/15 at two bits versus 12/15 at four bits, but n=15 limits
  formal inference.

- **"These results apply to other SLMs or hardware."** Only Llama 3.2-3B and
  Qwen2.5-3B on T4 were tested. No general architecture or hardware claim is
  supported.

- **"The provisional synthesis is accepted evidence."** Fingerprint
  `b19adce0924b4203` passed internal gates but has not been independently
  promoted. Figures derived from it must carry provisional provenance.

### 22.4 Proposal-versus-execution evaluation

The original proposal hypotheses evaluated against executed evidence:

| Proposal hypothesis | Outcome |
|---|---|
| H1: AWQ reduces energy ~3× at 8K | Not observed. Llama C1 reduced energy ~10% at 4096; Qwen Q1-W ≈ Q0. No 8K test. |
| H2: TQ reduces VRAM 15-20%, energy +5-15% | Realized TQ-Ref increased storage. Energy overhead was 31-45%, not 5-15%. |
| H3: Eviction VRAM savings with NIAH preserved | Llama quality preserved; Qwen eviction catastrophically failed. |
| H4: Compound achieves lowest VRAM+energy, 10-30% NIAH loss | Llama C4 was not significantly different from C1. Qwen Q4 quality was 1/60. |
| H0: No significant difference | Rejected for C1-C2, C1-C3, C2-C4, C3-C4 on Llama. Mixed on Qwen. |

The divergence between proposal expectations and executed outcomes is itself a
finding. It demonstrates that package capability and literature-level compression
ratios do not predict measured multi-objective behavior on specific SLMs.

## 23. Remaining Work

### 23.1 Paper writing

The final paper must be written in ACM Conference Proceedings Primary Article
Template format (unless the instructor approves a journal/arXiv track). The
following sections need to be authored from this master findings document:

| Paper section | Source in this document | Key requirement |
|---|---|---|
| Abstract (150-250 words) | Section 1 executive summary | Compress to required word count |
| Introduction / Motivation | Sections 2, 3 | Frame gap, state questions, summarize findings |
| Related Work | Section 6 + `proposal/literature_review.md` | Update for executed models; ≥25 references |
| Methodology | Sections 4, 5 | Configurations, hardware, metrics, protocol |
| Results: Systems energy | Sections 7, 8, 13, 14 | Tables and analysis for both models |
| Results: Quality | Sections 10, 13.3, 14.4-14.5 | Wilson intervals, depth patterns, sensitivity |
| Results: Cross-model | Sections 15, 16, 17 | Synthesis, ideal analysis, figures |
| Discussion | Sections 18, 19, 22 | Statistical interpretation, failures, claims |
| Threats / Limitations | Section 20 | Required by course rubric |
| Conclusion | Sections 22.1, 22.4 | Supported claims and proposal evaluation |

### 23.2 Proposal and literature update

The following proposal-stage content must be updated:

- Replace all Qwen3-4B references with Llama 3.2-3B and Qwen2.5-3B.
- Update BF16 references to FP16.
- Replace contexts 512/2048/8192 with 1024/2048/4096.
- Update configuration labels from old C2 (TQ) / C3 (eviction) to current
  C2 (eviction) / C3-Ref (TQ-Ref).
- Remove thinking-mode sections or mark as historical.
- Update expected outcomes with actual findings.
- Update references.bib to include all 25+ cited sources with correct author
  attributions (TurboQuant: Zandieh et al., SnapKV: Yuhong Li et al.,
  PyramidKV: Zefan Cai et al.).

### 23.3 Figure placement

Eight accepted figures are available in PNG and PDF format:

| Figure | Recommended placement | Format |
|---|---|---|
| fig01: measured TQ overhead | Main paper, results | PDF |
| fig02: context scaling | Main paper or appendix | PDF |
| fig03: retrieval Wilson intervals | Main paper, results | PDF |
| fig04: storage realization gap | Main paper, discussion | PDF |
| fig05: ideal packed components | Appendix | PDF |
| fig06: modeled phase demand | Appendix | PDF |
| fig07: symbolic break-even | Appendix | PDF |
| fig08: energy-quality-memory Pareto | Main paper, discussion | PDF |

Paper captions must note that figures derive from provisional synthesis
fingerprint `b19adce0924b4203`. The visualization bundle itself is accepted under
fingerprint `53ead4e6db45d2a8`.

### 23.4 Reproducibility package

The private GitHub repository must include:

- [ ] All source notebooks under `experiments/track_a_failsafe_colab/`
- [ ] Notebook 09B source (may need export from Colab)
- [ ] All accepted evidence bundles (or instructions to obtain them)
- [ ] Repair cell sources under `repairs/`
- [ ] Experiment registry
- [ ] Frozen hard-retrieval specification
- [ ] Comprehensive `README.md` with run instructions
- [ ] Instructor added as collaborator (`ahmed.shafi@ewubd.edu`)

### 23.5 Synthesis promotion decision

The provisional synthesis under fingerprint `b19adce0924b4203` can be:

- **Promoted as-is:** Accept the local execution as sufficient, update the
  registry status, and remove "provisional" from paper language.
- **Re-executed from canonical Colab:** Re-run Notebook 09 in a fresh Colab
  session, independently validate, and register a new or matching fingerprint.

Either path requires updating the tracker and evidence status before submission.

### 23.6 Submission checklist

| Item | Format | Status |
|---|---|---|
| Compiled PDF report | ACM format PDF | Not started |
| LaTeX source `.zip` | `.tex`, `.bib`, figures, `.sty`/`.cls` | Template present |
| Private GitHub repo | Instructor collaborator added | Pending |
| Individual contribution % | Google Sheet | Not applicable to master findings |
| Cross-check: ≥25 references | BibTeX | Needs verification/update |
| Cross-check: 150-250 word abstract | In PDF | Not started |
| Cross-check: all figures have captions with provenance | In PDF | Not started |

### 23.7 Open items from tracker

- Preserve/export the edited Notebook 09B if it is not yet in the local
  repository.
- Decide whether provisional synthesis will be independently promoted or rerun.
- Integrate selected visualization figures into the final paper.
- Complete the final paper narrative from this master findings document.

