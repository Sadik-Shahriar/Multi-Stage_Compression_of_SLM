# Multi-Stage Compression of Small Language Models for Energy-Efficient Inference: An Empirical Systems Ablation

**Course:** CSE407 — East West University  
**Authors:** Md. Sadik Shahriar, Nipa Mridha, Tanha Humaira, Ahmed Abdal Shafi Rasel\
**Measurement platform:** Google Colab with an NVIDIA Tesla T4 GPU

[![License: All Rights Reserved](https://img.shields.io/badge/License-All%20Rights%20Reserved-red.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Core runs: PyTorch 2.11](https://img.shields.io/badge/Core%20runs-PyTorch%202.11%2Bcu128-red.svg)](https://pytorch.org/)
[![Hardware: NVIDIA Tesla T4](https://img.shields.io/badge/Hardware-NVIDIA%20Tesla%20T4-green.svg)](https://www.nvidia.com/en-us/data-center/tesla-t4/)
[![Platform: Google Colab](https://img.shields.io/badge/Platform-Google%20Colab-F9AB00.svg)](https://colab.research.google.com)

---

## 📌 Overview & Objective

This repository contains the experiment notebooks, measured results, and statistical analyses for our study of multi-stage small language model (SLM) compression.

We measure GPU-board energy from 10 Hz NVML power traces, memory footprint, decode throughput, and exact-match retrieval for three compression techniques.

- **4-bit Weight Quantization (AWQ)**
- **Custom PyramidKV-style KV-cache token eviction**
- **TurboQuant reference KV-cache quantization (TQ-Ref)**

Evaluated across two sub-4B open-weights model architectures on **NVIDIA Tesla T4** hardware:
1. **Llama 3.2-3B-Instruct** (28 layers, 24 Query / 8 KV heads, $3:1$ GQA ratio)
2. **Qwen2.5-3B-Instruct** (36 layers, 16 Query / 2 KV heads, $8:1$ GQA ratio)

The measured energy and throughput characterize T4 inference. Edge accelerators require separate measurements.

---

## 🗺 Chronological Execution Sequence

To reproduce the core pipeline, upload the notebooks to Google Colab and follow this sequence. The [wrapper follow-up](#supplemental-llama-wrapper-control) can be run independently.

| Step | Task | Notebook | Colab Runtime | Approximate Time |
|:---:|:---|:---|:---:|:---:|
| **1** | Llama 3.2-3B Systems Baseline Matrix | [`notebooks/historical/llama/llama3_2.ipynb`](notebooks/historical/llama/llama3_2.ipynb) | T4 GPU | ~2 hours |
| **2** | Prompt Benchmark Freeze & Calibration | [`experiments/track_a_failsafe_colab/04_llama_hard_retrieval_pilot_v4.ipynb`](experiments/track_a_failsafe_colab/04_llama_hard_retrieval_pilot_v4.ipynb) | T4 GPU | ~20 min |
| **3** | Full Llama Hard-Retrieval & Energy Control | [`experiments/track_a_failsafe_colab/05_llama_full_quality_control_v1.ipynb`](experiments/track_a_failsafe_colab/05_llama_full_quality_control_v1.ipynb) | T4 GPU | ~1.5 hours |
| **4** | Power Telemetry Robustness Analysis | [`experiments/track_a_failsafe_colab/06_llama_power_robustness_analysis.ipynb`](experiments/track_a_failsafe_colab/06_llama_power_robustness_analysis.ipynb) | CPU | ~2 min |
| **5** | Qwen2.5-3B Adapter Validation Pilot | [`experiments/track_a_failsafe_colab/07_qwen2_5_adapter_parity_pilot_v1.ipynb`](experiments/track_a_failsafe_colab/07_qwen2_5_adapter_parity_pilot_v1.ipynb) | T4 GPU | ~10 min |
| **6** | Qwen2.5-3B Full Reference Experiment | [`experiments/track_a_failsafe_colab/08_qwen2_5_full_reference_v1.ipynb`](experiments/track_a_failsafe_colab/08_qwen2_5_full_reference_v1.ipynb) | T4 GPU | ~2 hours |
| **7** | Cross-Model Statistical Synthesis & Break-Even | [`experiments/track_a_failsafe_colab/09_cross_model_synthesis_v1.ipynb`](experiments/track_a_failsafe_colab/09_cross_model_synthesis_v1.ipynb) | CPU | ~2 min |
| **8** | Multi-Panel Publication Figure Generation | [`experiments/track_a_failsafe_colab/09b_cross_model_visualization.ipynb`](experiments/track_a_failsafe_colab/09b_cross_model_visualization.ipynb) | CPU | ~2 min |
| **9** | Environment & Reproducibility Audit | [`experiments/track_a_failsafe_colab/10_reproducibility_environment_audit.ipynb`](experiments/track_a_failsafe_colab/10_reproducibility_environment_audit.ipynb) | CPU / GPU | ~1 min |

---

## 🛠 Step-by-Step Reproduction Guide (From Scratch)

### General Google Colab Setup Instructions

1. Open [Google Colab](https://colab.research.google.com).
2. Click **Upload** and upload the corresponding `.ipynb` notebook.
3. For GPU steps: Go to **Runtime → Change runtime type** → select **T4 GPU**.
4. For CPU steps: Default standard CPU runtime is sufficient.
5. Execute all cells from top to bottom (**Runtime → Run all**).

Follow each notebook's setup instructions for package versions and input artifacts.

---

### Step 1: Llama 3.2-3B Systems Baseline Matrix

- **Notebook:** [`notebooks/historical/llama/llama3_2.ipynb`](notebooks/historical/llama/llama3_2.ipynb)
- **Colab Runtime:** T4 GPU (~2 hours)
- **Objective:** Evaluates 5 compression configurations ($C_0, C_1, C_2, C_3\text{-Ref}, C_4\text{-Ref}$) across context lengths of 1024, 2048, and 4096 tokens.
- **Measurements:**
  - 10 Hz NVML GPU-board power polling and integrated energy in joules
  - Prefill latency, decode latency, and decode throughput (tokens/sec)
  - Peak allocated VRAM
  - Baseline retrieval accuracy across 5 replicates
- **Output:** Produces 380 execution measurement rows and 95 raw NVML power trace files.

---

### Step 2: Prompt Benchmark Calibration & Freeze

- **Notebook:** [`experiments/track_a_failsafe_colab/04_llama_hard_retrieval_pilot_v4.ipynb`](experiments/track_a_failsafe_colab/04_llama_hard_retrieval_pilot_v4.ipynb)
- **Colab Runtime:** T4 GPU (~20 min)
- **Objective:** Generates and validates the calibrated 60-scenario Needle-In-A-Haystack (NIAH) key-value retrieval benchmark at 4096 context tokens:
  - 20 scenarios at shallow depth (10%)
  - 20 scenarios at middle depth (50%)
  - 20 scenarios at deep depth (90%)
  - 32 distractor records, controlled pairs, query window = 32
- **Output:** Freezes the prompt specification into [`research/frozen_hard_retrieval_v4.json`](research/frozen_hard_retrieval_v4.json) used by all downstream evaluation runs.

---

### Step 3: Full Llama Hard-Retrieval & Energy Control

- **Notebook:** [`experiments/track_a_failsafe_colab/05_llama_full_quality_control_v1.ipynb`](experiments/track_a_failsafe_colab/05_llama_full_quality_control_v1.ipynb)
- **Colab Runtime:** T4 GPU (~1.5 hours)
- **Objective:**
  - Runs all 5 compression configurations ($C_0, C_1\text{-W}, C_2, C_3\text{-Ref}, C_4\text{-Ref}$) against all 60 frozen hard-retrieval scenarios = 300 quality rows.
  - Runs 5 repeated $C_1$-W energy control blocks at 4096 tokens with teacher-forced decode and 10 Hz power sampling.
- **Output:** Produces 300 hard-retrieval quality rows, 5 energy control rows, and 5 power trace files.

---

### Step 4: Power Telemetry Robustness Analysis

- **Notebook:** [`experiments/track_a_failsafe_colab/06_llama_power_robustness_analysis.ipynb`](experiments/track_a_failsafe_colab/06_llama_power_robustness_analysis.ipynb)
- **Colab Runtime:** CPU (~2 min)
- **Objective:**
  - Integrates all 100 power traces (95 from Step 1 + 5 from Step 3).
  - Reintegrates the raw traces and repeats the analysis after clipping samples at 82 W and 70 W.
  - Runs pairwise paired t-tests and Wilcoxon signed-rank tests with Holm-Bonferroni corrections.
- **Finding:** The tested rankings and registered significance decisions held under both clipping thresholds.

---

### Step 5: Qwen2.5-3B Adapter Validation Pilot

- **Notebook:** [`experiments/track_a_failsafe_colab/07_qwen2_5_adapter_parity_pilot_v1.ipynb`](experiments/track_a_failsafe_colab/07_qwen2_5_adapter_parity_pilot_v1.ipynb)
- **Colab Runtime:** T4 GPU (~10 min)
- **Objective:** Unit tests the Qwen2 attention wrapper before running the full reference benchmark:
  - Validates 36 layers, 16 Query / 2 KV heads ($8:1$ GQA architecture).
  - Verifies exact logit parity between the stock AWQ model ($Q_1$-S) and wrapped model ($Q_1$-W).
  - Asserts TurboQuant reconstruction error NMSE $\le 0.025$.
  - Verifies active-returned cache and storage deduplication.

---

### Step 6: Qwen2.5-3B Full Reference Experiment

- **Notebook:** [`experiments/track_a_failsafe_colab/08_qwen2_5_full_reference_v1.ipynb`](experiments/track_a_failsafe_colab/08_qwen2_5_full_reference_v1.ipynb)
- **Colab Runtime:** T4 GPU (~2 hours)
- **Objective:**
  - Runs 75 core energy runs ($5 \text{ configs} \times 3 \text{ contexts} \times 5 \text{ replicates}$) + 20 sensitivity energy runs.
  - Logs 95 raw 10 Hz NVML power trace files.
  - Evaluates 300 core hard-retrieval quality scenarios + 60 sensitivity-quality scenarios across retention budgets (512, 1024, 1536 tokens).
- **Output:** Produces 455 measurement rows and 95 raw NVML power traces.

---

### Step 7: Cross-Model Statistical Synthesis & Break-Even Modeling

- **Notebook:** [`experiments/track_a_failsafe_colab/09_cross_model_synthesis_v1.ipynb`](experiments/track_a_failsafe_colab/09_cross_model_synthesis_v1.ipynb)
- **Colab Runtime:** CPU (~2 min)
- **Objective:**
  - Merges Llama 3.2-3B and Qwen2.5-3B datasets.
  - Computes sequential interaction contrasts:
    $$I = [E(C_4) - E(C_1)] - [E(C_2) - E(C_1)] - [E(C_3) - E(C_1)]$$
  - Runs paired t-tests, Wilcoxon tests, Holm-Bonferroni corrections, exact McNemar tests, and Wilson 95% confidence intervals.
  - Models compulsory DRAM byte demand versus non-traffic compute overhead break-even boundaries.
- **Output:** A 41-file provisional synthesis with statistical summaries, Pareto results, and modeled break-even results.

---

### Step 8: Multi-Panel Publication Figure Generation

- **Notebook:** [`experiments/track_a_failsafe_colab/09b_cross_model_visualization.ipynb`](experiments/track_a_failsafe_colab/09b_cross_model_visualization.ipynb)
- **Colab Runtime:** CPU (~2 min)
- **Objective:** Renders eight figures from the synthesis tables in vector PDF and high-resolution PNG:
  - `fig01_measured_tq_overhead.pdf` — TurboQuant Reference Overhead & Latency Inflation
  - `fig02_measured_context_scaling.pdf` — Energy & Throughput Scaling vs. Context
  - `fig03_retrieval_wilson.pdf` — Hard-Retrieval Accuracy with Wilson 95% CIs
  - `fig04_storage_realization_gap.pdf` — Storage Realization Gap (Measured vs. Realized vs. Ideal)
  - `fig05_ideal_packed_components.pdf` — Ideal Analytical 2/3/4-bit Component Scaling
  - `fig06_modeled_phase_byte_demand.pdf` — Prefill vs. Decode Phase Byte Demand Model
  - `fig07_symbolic_energy_break_even.pdf` — Closed-Form Symbolic Energy Break-Even Contours
  - `fig08_measured_pareto_energy_quality_memory.pdf` — Multi-Objective Pareto Frontier
- **Output:** Writes 16 figure files to `/content/CSE407_cross_model_visualization_v1/`. The [saved figure bundle](evidence/accepted/CSE407_cross_model_visualization_v1/) is available in this repository.

---

### Step 9: Environment & Reproducibility Audit

- **Notebook:** [`experiments/track_a_failsafe_colab/10_reproducibility_environment_audit.ipynb`](experiments/track_a_failsafe_colab/10_reproducibility_environment_audit.ipynb)
- **Colab Runtime:** Any Colab runtime (~1 min)
- **Objective:** Automatically queries the live environment (host OS, GPU clock rates, NVML polling settings, library builds, layerwise eviction budgets) and exports:
  - [`reproducibility_export/reproducibility_specs_full.json`](reproducibility_export/reproducibility_specs_full.json)
  - [`reproducibility_export/reproducibility_summary.md`](reproducibility_export/reproducibility_summary.md)

---

### Supplemental Llama wrapper control

Open [Notebook 12](experiments/track_a_failsafe_colab/12_llama_matched_wrapper_interaction_v1.ipynb) in a fresh Colab T4 runtime and run its numbered cells in order. The follow-up compares stock and wrapped AWQ alongside the three compressed paths in ten counterbalanced blocks. Every run uses the same 4,096-token prompt and 64 teacher-forced decode tokens.

The [verified result archive](evidence/supplemental/bundles/CSE407_llama_matched_wrapper_interaction_v1_20261122T112205Z-348460e2.zip) contains 50 measurements and 50 raw power traces, paired contrasts, the runtime manifest, and a checksum inventory. The completed run used PyTorch 2.14.1+cu130.

---

## 🔬 Reproducing Recorded Results

- Use the pinned checkpoints, frozen prompt IDs, and fixed decode settings in the notebooks. Compare retrieval counts with the archived results.
- GPU energy, latency, and throughput vary across sessions. Record the GPU, runtime, and software versions when comparing a fresh run with the archived measurements.
- Reintegrate the saved traces to check energy totals and repeat the registered statistics. The 82 W and 70 W clipping checks use those same traces.

---

## ⚙️ Experimental Configurations Matrix

| Config | Weight Precision | KV Cache Retention Policy | KV Cache Precision | Pipeline Stage Order |
|:---|:---|:---|:---|:---|
| **$C_0$ / $Q_0$** | FP16 (Baseline) | Full Attention (No eviction) | FP16 (Baseline) | Standard uncompressed model |
| **`C1`, `C1-W`, `Q1-W`** | AWQ INT4 (group 128) | Full Attention (No eviction) | FP16 (Baseline) | AWQ linear projections |
| **$C_2$ / $Q_2$** | AWQ INT4 (group 128) | Custom PyramidKV ($\bar{b}=1024$) | FP16 (Baseline) | AWQ $\to$ Pyramidal token pruning |
| **$C_3\text{-Ref}$ / $Q_3\text{-Ref}$** | AWQ INT4 (group 128) | Full Attention (No eviction) | Nominal 4-bit TQ-Ref (128-token FP16 residual) | AWQ $\to$ TQ coordinate quantization |
| **$C_4\text{-Ref}$ / $Q_4\text{-Ref}$** | AWQ INT4 (group 128) | Custom PyramidKV ($\bar{b}=1024$) | Nominal 4-bit TQ-Ref (128-token FP16 residual) | AWQ $\to$ PyramidKV $\to$ TQ Quantization |

`C1` is stock Llama AWQ. `C1-W` and `Q1-W` use the attention wrapper. TQ-Ref stores byte-sized indices and retains materialized FP16 keys and values.

---

## 📊 Summary of Core Empirical Findings

### 1. Llama 3.2-3B systems results at 4096 tokens

The values below come from the [Llama core systems summary](evidence/accepted/bundles/CSE407_llama_v5_final/v5_final_core_summary.csv).

| Configuration | Total energy (J), mean ± SD | Decode (tok/s) | Active KV cache (MiB) |
|:---|---:|---:|---:|
| FP16 (C0) | 701.08 ± 8.12 | 11.34 | 455.00 |
| Stock AWQ (C1) | 631.25 ± 5.05 | 13.77 | 455.00 |
| AWQ + eviction (C2) | 529.30 ± 20.02 | 20.34 | 119.00 |
| AWQ + TQ-Ref (C3-Ref) | 913.48 ± 2.11 | 7.66 | 696.50 |
| AWQ + eviction + TQ-Ref (C4-Ref) | 659.50 ± 21.35 | 12.53 | 187.25 |

At 4096 tokens, eviction used 16.15% less energy and reduced the active cache by 73.8% relative to stock AWQ.

### 2. Hard retrieval at 4096 tokens

| Configuration | Llama 3.2-3B | Qwen2.5-3B |
|:---|---:|---:|
| FP16 (C0 / Q0) | 47/60 | 53/60 |
| Wrapped AWQ (C1-W / Q1-W) | 38/60 | 48/60 |
| AWQ + eviction (C2 / Q2) | 37/60 | 1/60 |

The separate 15-scenario Qwen budget sweep yielded 0/15, 1/15, and 2/15 at mean budgets of 512, 1024, and 1536 tokens per layer. GQA ratio, layer count, tokenization, and implementation details vary between Llama and Qwen, leaving the cause of the retrieval gap unresolved. [Llama retrieval evidence](evidence/accepted/bundles/CSE407_llama_track_a_full_v1/track_a_full_quality_results.csv) · [Qwen retrieval evidence](evidence/accepted/bundles/CSE407_qwen_track_a_reference_v1/core_quality_results.csv) · [Qwen sensitivity evidence](evidence/accepted/bundles/CSE407_qwen_track_a_reference_v1/sensitivity_quality_results.csv)

### 3. Same-session Llama interaction

| Paired contrast | Mean (J) | 95% CI (J) |
|:---|---:|:---|
| Wrapper shift (C1-W minus C1) | −4.13 | [−16.36, +8.10] |
| Interaction with stock AWQ | −212.41 | [−226.65, −198.16] |
| Interaction with wrapped AWQ | −216.54 | [−237.15, −195.92] |

The wrapper interval spans zero. The interaction stayed negative with either baseline on the tested workload.

---

## 📖 Citation

```bibtex
@misc{shahriar2026multistage,
  title  = {Multi-Stage Compression of Small Language Models for Energy-Efficient Inference: An Empirical Systems Ablation},
  author = {Shahriar, Md. Sadik and Mridha, Nipa and Humaira, Tanha and Rasel, Ahmed Abdal Shafi},
  year   = {2026},
  note   = {Accepted manuscript}
}
```

## 👥 Authors, Contributors & License

- **Md. Sadik Shahriar** — [shahriarsadik@gmail.com](mailto:shahriarsadik@gmail.com)
- **Nipa Mridha** — [mridhanipa886@gmail.com](mailto:mridhanipa886@gmail.com)
- **Tanha Humaira** — [chandnihumaira373@gmail.com](mailto:chandnihumaira373@gmail.com)
- **Ahmed Abdal Shafi Rasel** — project supervision and manuscript co-authorship

Department of Computer Science and Engineering, **East West University**
 
**Copyright © 2026 Md. Sadik Shahriar, Nipa Mridha, Tanha Humaira. All Rights Reserved.**  
This research codebase, experimental methodology, and empirical evidence are proprietary academic assets pending formal publication. Authorized for confidential course evaluation and academic review only. Unauthorized reproduction, distribution, or public re-hosting is strictly prohibited. See [LICENSE](LICENSE) for details.
