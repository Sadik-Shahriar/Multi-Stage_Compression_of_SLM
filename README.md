# Multi-Stage Compression of Small Language Models for Energy-Efficient Edge Inference

**Course:** CSE407 — East West University  
**Authors:** Md. Sadik Shahriar, Nipa Mridha, Tanha Humaira  
**Platform:** All experiments were executed entirely on **Google Colab** (free tier, NVIDIA Tesla T4 GPU)

[![License: All Rights Reserved](https://img.shields.io/badge/License-All%20Rights%20Reserved-red.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![PyTorch 2.11](https://img.shields.io/badge/PyTorch-2.11%2Bcu128-red.svg)](https://pytorch.org/)
[![Hardware: NVIDIA Tesla T4](https://img.shields.io/badge/Hardware-NVIDIA%20Tesla%20T4-green.svg)](https://www.nvidia.com/en-us/data-center/tesla-t4/)
[![Platform: Google Colab](https://img.shields.io/badge/Platform-Google%20Colab-F9AB00.svg)](https://colab.research.google.com)

---

## 📌 Overview & Objective

This repository contains the complete experimental suite, ablation pipelines, and statistical analysis for our empirical research paper on multi-stage Small Language Model (SLM) compression. 

We evaluate the physical energy (10 Hz continuous NVML telemetry), dynamic memory footprint, decode throughput, and exact retrieval accuracy of sequentially stacked compression techniques:
- **4-bit Weight Quantization (AWQ)**
- **Dynamic Pyramidal KV-Cache Eviction (PyramidKV)**
- **KV-Cache Quantization (TurboQuant)**

Evaluated across two sub-4B open-weights model architectures on **NVIDIA Tesla T4** hardware:
1. **Llama 3.2-3B-Instruct** (28 layers, 24 Query / 8 KV heads, $3:1$ GQA ratio)
2. **Qwen2.5-3B-Instruct** (36 layers, 16 Query / 2 KV heads, $8:1$ GQA ratio)

> **Execution Platform:** Every notebook in this repository is completely self-contained and designed to run directly on **Google Colab** (free tier). No local GPU, high-performance workstation, or private cloud instance is needed.

---

## 🗺 Chronological Execution Sequence

To execute the entire pipeline from scratch, upload the `.ipynb` files to Google Colab and run them in the following order:

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

Each GPU notebook automatically installs required packages (`transformers`, `turboquant`, `gptqmodel`, `pynvml`, etc.) and asserts pinned software versions at startup.

---

### Step 1: Llama 3.2-3B Systems Baseline Matrix

- **Notebook:** [`notebooks/historical/llama/llama3_2.ipynb`](notebooks/historical/llama/llama3_2.ipynb)
- **Colab Runtime:** T4 GPU (~2 hours)
- **Objective:** Evaluates 5 compression configurations ($C_0, C_1, C_2, C_3\text{-Ref}, C_4\text{-Ref}$) across context lengths of 1024, 2048, and 4096 tokens.
- **Measurements:**
  - 10 Hz continuous NVML GPU board power polling (Joules)
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
  - Re-evaluates energy under raw transients, an 82 W ceiling, and a 70 W enforced cap.
  - Runs pairwise paired t-tests and Wilcoxon signed-rank tests with Holm-Bonferroni corrections.
- **Finding:** Proves that energy rankings and statistical significance decisions remain 100% stable regardless of power cap clipping.

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
- **Output:** Generates 41 statistical tables, Pareto frontiers, and analytical break-even surfaces.

---

### Step 8: Multi-Panel Publication Figure Generation

- **Notebook:** [`experiments/track_a_failsafe_colab/09b_cross_model_visualization.ipynb`](experiments/track_a_failsafe_colab/09b_cross_model_visualization.ipynb)
- **Colab Runtime:** CPU (~2 min)
- **Objective:** Reads the synthesis tables and automatically renders all 8 publication figures in both vector PDF and high-resolution PNG:
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

## 🔬 Deterministic vs. Physical Measurement Behavior

When you re-run these experiments on Google Colab:

| Measurement Dimension | On Fresh Colab Run | Technical Reason |
|:---|:---:|:---|
| **Retrieval Accuracy (e.g., 37/60, 48/60, 1/60)** | **100% Exact Match** | Greedy decoding (`temperature=0.0`), fixed seed (`407`), pinned model checkpoints. |
| **Quality Evaluation Output CSVs** | **100% Exact Match** | Deterministic token generation and exact string matching. |
| **Energy Rankings ($C_2 < C_1 < C_0 < C_4 < C_3$)** | **100% Stable** | Confirmed across multiple runs and 3 power clipping regimes in Step 4. |
| **Statistical Decisions ($p < 0.01$, Interaction $I < 0$)** | **100% Stable** | Robust across paired t-tests and Wilcoxon signed-rank tests. |
| **Analytical Synthesis & Figure Generation** | **Byte-Identical** | Pure deterministic arithmetic on generated tables. |
| **Raw Energy in Joules** | **$\pm 2\text{--}5\%$ variation** | Normal physical noise from NVML hardware board power sampling. |
| **Raw Power Traces** | **Similar shape, slight variance** | Physical board-level power fluctuations on GPU. |

---

## ⚙️ Experimental Configurations Matrix

| Config | Weight Precision | KV Cache Retention Policy | KV Cache Precision | Pipeline Stage Order |
|:---|:---|:---|:---|:---|
| **$C_0$ / $Q_0$** | FP16 (Baseline) | Full Attention (No eviction) | FP16 (Baseline) | Standard uncompressed model |
| **$C_1$ / $Q_1$** | AWQ INT4 (group 128) | Full Attention (No eviction) | FP16 (Baseline) | AWQ linear projections |
| **$C_2$ / $Q_2$** | AWQ INT4 (group 128) | Custom PyramidKV ($\bar{b}=1024$) | FP16 (Baseline) | AWQ $\to$ Pyramidal token pruning |
| **$C_3\text{-Ref}$ / $Q_3\text{-Ref}$** | AWQ INT4 (group 128) | Full Attention (No eviction) | TurboQuant 4-bit (128-tok FP16 res) | AWQ $\to$ TQ coordinate quantization |
| **$C_4\text{-Ref}$ / $Q_4\text{-Ref}$** | AWQ INT4 (group 128) | Custom PyramidKV ($\bar{b}=1024$) | TurboQuant 4-bit (128-tok FP16 res) | AWQ $\to$ PyramidKV $\to$ TQ Quantization |

---

## 📊 Summary of Core Empirical Findings

### 1. Llama 3.2-3B Performance at 4096 Context Length

| Configuration | Total Energy (J) | Energy $\Delta$ vs $C_0$ | Decode Throughput | Active KV Cache | Hard NIAH Accuracy |
|:---|:---:|:---:|:---:|:---:|:---:|
| **$C_0$ (FP16 Baseline)** | $631.33 \pm 4.21\text{ J}$ | — | $13.77\text{ tok/s}$ | $455\text{ MiB}$ | $38 / 60\ (63.3\%)$ |
| **$C_1$ (AWQ INT4)** | $603.95 \pm 2.65\text{ J}$ | $-4.34\%$ | $14.15\text{ tok/s}$ | $455\text{ MiB}$ | $38 / 60\ (63.3\%)$ |
| **$C_2$ (AWQ + PyramidKV)** | **$529.38 \pm 3.12\text{ J}$** | **$-16.15\%$** | **$20.34\text{ tok/s}$** | **$119\text{ MiB}$ ($-73.8\%$)** | **$37 / 60\ (61.7\%)$** |
| **$C_3\text{-Ref}$ (AWQ + TQ-Ref)**| $791.42 \pm 6.14\text{ J}$ | $+25.36\%$ | $9.82\text{ tok/s}$ | $523\text{ MiB}$ ($+14.9\%$) | $38 / 60\ (63.3\%)$ |
| **$C_4\text{-Ref}$ (Compound)** | $668.74 \pm 4.88\text{ J}$ | $+5.93\%$ | $13.56\text{ tok/s}$ | $187\text{ MiB}$ ($-58.9\%$) | $37 / 60\ (61.7\%)$ |

### 2. GQA Architecture Fragility (Llama 3.2-3B vs. Qwen2.5-3B)

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│ RETRIEVAL ACCURACY UNDER TOKEN EVICTION (4096 Context, 60 Scenarios)            │
├──────────────────────────────┬────────────────────────┬─────────────────────────┤
│ Configuration                │ Llama 3.2-3B (3:1 GQA) │ Qwen2.5-3B (8:1 GQA)    │
├──────────────────────────────┼────────────────────────┼─────────────────────────┤
│ Baseline ($C_0 / Q_0$)       │ 38 / 60 (63.3%)        │ 48 / 60 (80.0%)         │
│ AWQ ($C_1 / Q_1$)            │ 38 / 60 (63.3%)        │ 48 / 60 (80.0%)         │
│ AWQ + PyramidKV ($C_2 / Q_2$)│ 37 / 60 (61.7%)        │ 1 / 60 (1.7%) [COLLAPSE]│
│ Retention Budget +50% (1536) │ —                      │ 2 / 15 (13.3%) [FAILED] │
└──────────────────────────────┴────────────────────────┴─────────────────────────┘
```

---

## 📖 Citation

```bibtex
@inproceedings{shahriar2026multistage,
  title     = {Multi-Stage Compression of Small Language Models for Energy-Efficient Inference: An Empirical Systems Ablation},
  author    = {Shahriar, Md. Sadik and Mridha, Nipa and Humaira, Tanha},
  booktitle = {Proceedings of the ACM Conference (ACM sigconf)},
  year      = {2026},
  publisher = {Association for Computing Machinery}
}
```

## 👥 Authors & License

- **Md. Sadik Shahriar** — [shahriarsadik@gmail.com](mailto:shahriarsadik@gmail.com)
- **Nipa Mridha** — [mridhanipa886@gmail.com](mailto:mridhanipa886@gmail.com)
- **Tanha Humaira** — [chandnihumaira373@gmail.com](mailto:chandnihumaira373@gmail.com)

Department of Computer Science and Engineering, **East West University**
 
**Copyright © 2026 Md. Sadik Shahriar, Nipa Mridha, Tanha Humaira. All Rights Reserved.**  
This research codebase, experimental methodology, and empirical evidence are proprietary academic assets pending formal publication. Authorized for confidential course evaluation and academic review only. Unauthorized reproduction, distribution, or public re-hosting is strictly prohibited. See [LICENSE](LICENSE) for details.
