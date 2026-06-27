# Holistic Optimization of Small Language Models for Energy-Efficient Edge Inference: An Empirical Ablation Study

**Course:** CSE407 Green Computing — East West University (Summer 2026)
**Student:** Md. Sadik Shahriar
**Instructor:** Ahmed Abdal Shafi Rasel (AASR)

---

## 1. Introduction & Background

### 1.1 The Sustainability Challenge in AI

Information and Communications Technology (ICT) currently contributes 2–3% of global CO₂ emissions, with projections reaching 7–8% by 2030 [17]. Data centers consume approximately 415 Terawatt-hours (TWh) annually — roughly 2% of global electricity — with demand expected to double by 2030 (IEA, 2024) [17]. Within this landscape, AI inference has emerged as a dominant and growing contributor. Inference at scale now produces more total carbon than the one-time training of models [8, 9], and each AI query consumes approximately 10× the energy of a conventional web search [9]. The GPU is the primary energy consumer in AI inference, accounting for up to 90% of total system power draw [19].

Large Language Models (LLMs) are at the center of this energy challenge. During autoregressive generation, transformer-based models maintain a Key-Value (KV) cache that stores attention key and value tensors for every preceding token. This cache grows linearly with sequence length; at 8K–128K tokens, it dominates GPU memory and contributes significantly to inference energy consumption [7, 23].

### 1.2 Small Language Models as a Sustainable Alternative

Small Language Models (SLMs, sub-7B parameters) require fewer FLOPs per token than larger counterparts, can run on lower-wattage edge GPUs, and eliminate the energy overhead of cloud-based inference [18, 20, 22]. Recent work has demonstrated that quantized SLMs achieve 3–11× lower energy per query than 14B-parameter models [18].

The Qwen3 model family [1] introduces a 4-billion-parameter dense variant (Qwen3-4B) with 36 layers, Grouped Query Attention (GQA) with 32 query heads and 8 KV heads, 32K native context length, and a unified thinking/non-thinking mode framework [1]. The thinking mode enables multi-step reasoning via a configurable thinking budget, while non-thinking mode provides rapid direct responses — all within a single model [1]. Official Activation-aware Weight Quantization (AWQ) 4-bit weights are available on HuggingFace (`Qwen/Qwen3-4B-AWQ`), making Qwen3-4B an accessible testbed for energy-optimized edge deployment research.

### 1.3 The Research Gap

Three orthogonal compression techniques exist for reducing the memory and energy footprint of LLM inference:

1. **Weight quantization** (AWQ [2], GPTQ [12]) — compresses static model weights to 4-bit or lower precision, reducing weight memory by approximately 4× while preserving model quality via activation-aware salient weight protection [2].

2. **Token eviction** (SnapKV [4], PyramidKV [5], H2O [6]) — dynamically removes unimportant tokens from the KV cache based on attention scores. SnapKV computes importance scores within an observation window of the last 32 tokens [4]; PyramidKV extends this with a pyramidal allocation that varies cache size across layers [5].

3. **KV cache quantization** (TurboQuant [3], KIVI [7]) — compresses surviving KV cache entries to low-bit-width representations (2–4 bits). TurboQuant uses data-oblivious random rotation followed by Lloyd-Max scalar quantization, achieving near-lossless compression at 3.5 bits per channel [3].

Existing literature studies these techniques predominantly in isolation. The AWQ paper [2] evaluates weight quantization alone; TurboQuant [3] focuses exclusively on KV cache compression; SnapKV [4] and PyramidKV [5] consider only token eviction. **No published work has empirically measured the compound effect of all three techniques applied simultaneously to a single SLM, using real hardware power monitoring on a production GPU.** The TurboQuant paper [3] compares against SnapKV and PyramidKV as baselines but does not explore compounding them with weight quantization. SLMQuant [24], the first systematic benchmark of quantization on SLMs, explicitly recommends investigating SLM-specific compression designs and notes, "quantization techniques optimized for LLMs may not proportionally benefit SLMs" [24]. The Empirical Study of Qwen3 Quantization [23] calls for evaluating rotation-based quantization strategies (such as TurboQuant) on Qwen3 as future work.

Furthermore, no study has quantified how a model's built-in reasoning mode (thinking mode) interacts with compression in terms of energy cost. ThinKV [25] investigates hybrid quantization-eviction for reasoning models (DeepSeek-R1) but does not address Qwen3's integrated thinking mode or measure energy. Given that thinking mode can generate 2,000–8,000 internal reasoning tokens per query, this interaction may substantially affect both energy consumption and reasoning quality under compression.

---

## 2. Problem Statement

The problem this research addresses is the **absence of empirical data on the compound energy-accuracy-memory trade-offs when stacking weight quantization (AWQ), token eviction (PyramidKV/SnapKV), and KV cache quantization (TurboQuant) on a small language model with built-in thinking mode, deployed on an NVIDIA T4 GPU.**

Current recommendations for energy-efficient LLM deployment lack an evidence base for combined compression strategies on SLMs. A practitioner choosing between AWQ-only, AWQ+TurboQuant, AWQ+eviction, or all three techniques has no published measurements at the sub-4B scale to inform decisions about Pareto-optimal configurations for specific energy, memory, and accuracy constraints. The addition of thinking mode — a feature in Qwen3, DeepSeek-R1, and similar models — introduces a further unknown: the energy cost of reasoning under compressed conditions has not been empirically characterized.

This is a timely and consequential problem for three stakeholder groups: (a) **edge device manufacturers** who need models running under 4 GB VRAM at low power, (b) **cloud providers** seeking maximum throughput at minimum energy per query, and (c) **AI sustainability researchers** who require empirical baselines for compound compression strategies on SLMs.

---

## 3. Research Objectives

### 3.1 Aim

To empirically investigate the energy, memory, and accuracy trade-offs of compounding weight quantization, token eviction, and KV cache quantization on the Qwen3-4B small language model, with and without built-in thinking mode, deployed on an NVIDIA T4 GPU.

### 3.2 Specific Objectives

1. **Implement** five distinct compression configurations — C0 (BF16 baseline), C1 (AWQ 4-bit), C2 (AWQ + TurboQuant 4-bit), C3 (AWQ + PyramidKV 1024-token capacity), and C4 (all three) — on Qwen3-4B.

2. **Measure** peak VRAM (MB), average power (W), total energy (J), throughput (tok/s), perplexity, and Needle-in-a-Haystack (NIAH) retrieval accuracy for each configuration at context lengths of 512, 2048, and 8192 tokens.

3. **Quantify** the additional energy cost of Qwen3-4B's built-in thinking mode under C0, C1, and C4 at 8192-token context.

4. **Analyze** the statistical significance of differences between configurations using paired t-tests (or non-parametric alternatives), with a significance threshold of $\alpha = 0.05$, and report effect sizes (Cohen's $d$ or Cliff's $\delta$).

5. **Construct** Pareto frontier plots mapping energy (J) against NIAH accuracy to identify optimal configurations for different stakeholder deployment scenarios.

---

## 4. Research Questions

### 4.1 Primary Research Question (RQ1)

*How does stacking AWQ (4-bit weights), PyramidKV/SnapKV (1024-token capacity), and TurboQuant (4-bit KV cache) affect total inference energy (Joules), peak VRAM (MB), and NIAH retrieval accuracy compared to the uncompressed BF16 baseline and each individual technique, when running Qwen3-4B at context lengths of 512, 2048, and 8192 tokens on an NVIDIA T4 GPU?*

**Context:** Qwen3-4B — 36 layers, GQA (32 Q / 8 KV heads), 32K native context, tie embedding enabled [1]. T4 GPU — 16 GB VRAM, 70W TDP (measured max ~82W during inference [19]). Metrics directly measurable via `pynvml`, `torch.cuda.max_memory_allocated`, and standardized completion-style NIAH prompts.

### 4.2 Secondary Research Question (RQ2)

*What is the additional energy cost of Qwen3-4B's built-in thinking mode under each compression configuration, and does compression disproportionately degrade reasoning quality relative to direct response?*

**Context:** Tested at 8K context only, on C0, C1, and C4 (a focused subset to limit experiment runtime to one Colab session). Thinking mode enabled via Qwen3's chat template `/think` flag; answers extracted from `\boxed{}` or `\boxed{...}` delimiters [1]. Thinking budget set to 8192 tokens (Qwen3 report default for long-context tasks [1]).

---

## 5. Hypotheses

### 5.1 Primary Hypotheses

**H1 (AWQ energy savings):** AWQ (C1) reduces total inference energy by approximately 3× compared to the BF16 baseline (C0) at 8K context, while maintaining NIAH accuracy above 90%.

*Basis:* AWQ achieves 3× speedup over HuggingFace FP16 on mobile GPUs [2]. Qwen3-4B-AWQ reduces VRAM from ~10 GB (BF16) to ~3 GB, substantially reducing memory bandwidth and energy.

**H2 (TurboQuant memory-accuracy trade-off):** Adding TurboQuant to AWQ (C2) reduces peak VRAM by 15–20% compared to C1, but per-task energy may increase by 5–15% due to quantize/dequant overhead from the random rotation and QJL transform [3].

*Basis:* TurboQuant achieves 4.5× KV cache compression at 3.5-bit with quality neutrality on 7B+ models [3]. The overhead of random rotation and per-coordinate quantization (Lloyd-Max, QJL) on T4 (no tensor-core support for reduced precision) may negate some energy savings.

**H3 (Eviction capacity gate):** Adding token eviction (C3) to AWQ reduces peak VRAM at 8K+ context lengths but shows no statistically significant effect at 512 tokens (where total prompt tokens < eviction capacity of 1024).

*Basis:* SnapKV retains less than 20% of tokens [4]; PyramidKV achieves 12% cache matching full performance [5]. At 512 tokens, the cache is below the 1024 capacity, so no eviction occurs.

**H4 (Compound compression degradation):** The compound configuration (C4 — all three techniques) achieves the lowest peak VRAM and total energy per task, but shows measurable NIAH degradation of 10–30% due to compound compression noise from the interaction of eviction and quantization.

*Basis:* RDKV [26] shows that joint eviction+quantization requires careful bit-allocation to avoid compound degradation. The interaction of PyramidKV's score-based selection with TurboQuant's rotation-based quantization has not been characterized.

**H0 (Null):** No statistically significant difference in energy consumption exists between any pair of configurations (paired t-test, $\alpha = 0.05$) [27].

### 5.2 Secondary Hypothesis

**H5 (Thinking mode energy multiplier):** Thinking mode increases total energy by 2–5× compared to non-thinking mode at the same configuration. This ratio is smaller under compressed configurations (C4) because fewer preserved tokens limit the depth of the reasoning chain.

*Basis:* Qwen3 technical report shows thinking mode generates substantially more tokens [1]. ThinKV [25] demonstrates that compression methods for reasoning models must account for varying token importance within chain-of-thought.

---

## 6. Planned Methodology

### 6.1 Experimental Design

A 5 × 3 within-subjects ablation design with an additional 3-run thinking-mode subset (total 18 experiments):

| Config | Weights | Eviction | KV Cache Quant | What It Tests |
|---|---|---|---|---|
| **C0** | BF16 | None | FP16 (default) | Uncompressed baseline |
| **C1** | AWQ 4-bit | None | FP16 (default) | Weight quantization alone |
| **C2** | AWQ 4-bit | None | TurboQuant 4-bit | KV cache quantization (on AWQ) |
| **C3** | AWQ 4-bit | PyramidKV (cap=1024) | FP16 (default) | Token eviction (on AWQ) |
| **C4** | AWQ 4-bit | PyramidKV (cap=1024) | TurboQuant 4-bit | Compound effect |

**Context lengths:** 512, 2048, 8192 tokens.
**Thinking subset:** C0, C1, C4 at 8192 (with thinking mode via Qwen3 chat template `/think` flag).
**Total runs:** 5 × 3 + 3 = **18 experiments**, each repeated 3 times for statistical power.

### 6.2 Environment

- **Hardware:** Google Colab (NVIDIA T4, 16 GB VRAM, 70W TDP; measured max ~82W, idle ~12W during inference [19])
- **Software:** Python 3.10+, PyTorch 2.4+, Transformers 4.45+, AutoAWQ, TurboQuant (community PyTorch implementation [3]), pynvml, scipy, statsmodels, pandas, matplotlib, seaborn
- **Models:** `Qwen/Qwen3-4B` (BF16), `Qwen/Qwen3-4B-AWQ` (INT4) — both available on HuggingFace [1]

### 6.3 Measurement Protocol

| Metric | Tool | Granularity |
|---|---|---|
| GPU Power (W) | pynvml (`nvmlDeviceGetPowerUsage`) | 100 ms polling via background thread (10 Hz, matching Watt Counts recommendation [19]) |
| Energy (J) | avg_power(W) × inference_time(s) | Per run |
| Peak VRAM (MB) | `torch.cuda.max_memory_allocated()` | Per run (reset before each config) |
| Inference Time (s) | `time.time()` | Wall clock |
| Throughput | `max_new_tokens / inference_time` | Per run |
| Perplexity | Cross-entropy loss with active `past_key_values` (the KV cache must be included in loss computation) | Per run |
| NIAH | Completion-style prompt match ("SHADOW-8821") | Per run |

### 6.4 Implementation Steps

**Step 1 — Environment setup:** Install dependencies; verify T4 GPU (must be Pascal or newer for `nvmlDeviceGetPowerUsage`), CUDA version, and Qwen3 model availability on HuggingFace.

**Step 2 — Helper functions:** Build `ExperimentResult` dataclass, `GPUMonitor` threaded power tracker (10 Hz polling, background thread to avoid blocking inference), `clear_cache()` utility with `torch.cuda.empty_cache()`, and `compute_perplexity()` with active `past_key_values` passed to `model()`.

**Step 3 — NIAH implementation:** Create completion-style prompts with needle "The secret project code name is SHADOW-8821" inserted at 50% depth of context. Maximum new tokens = 50. For thinking mode, extract final answer from `\boxed{...}` or `\boxed{}` delimiters before checking for "SHADOW-8821". Log raw output for failed extractions.

**Step 4 — PyramidKV/SnapKV integration:** Monkey-patch `Qwen3Attention.forward` to intercept KV cache. SnapKV: compute attention scores over observation window (last 32 tokens), select top-1024 clustered positions [4]. PyramidKV: allocate cache budget following pyramidal ramp across 36 layers (256 at layer 0 → 4096 at layer 35 at full budget, scaled to 1024 average). Handle Qwen3-specific QK-Norm and GQA (32 Q / 8 KV heads) in attention patching. Fallback to SnapKV if PyramidKV integration proves too complex for Qwen3's architecture.

**Step 5 — TurboQuant integration:** Create TurboQuant quantizer instance (effective bits = 4.0, using outlier-aware mixed precision: 32 outlier channels at 5-bit, 96 regular at 3-bit for head_dim=128 [3]). Apply as `past_key_values` wrapper that quantizes keys and values on insertion and dequantizes (or uses QJL inner product estimation [3]) on attention computation. Verify compatibility with Qwen3's GQA head structure in a pilot test.

**Step 6 — Experiment runner:** For each config × context length combination: load model (or reload for config change), set eviction/quantization flags, run generation with GPU monitoring, store results as CSV row. Save intermediate CSV after each config to guard against Colab 12-hour session timeout. Run 3 repetitions per combination.

**Step 7 — Analysis:** Shapiro-Wilk normality test → choose parametric (repeated-measures ANOVA, paired t-test) or non-parametric (Kruskal-Wallis, Wilcoxon signed-rank). Generate plots: (1) VRAM vs. context length, (2) Energy vs. context length, (3) NIAH accuracy heatmap (configs × context lengths), (4) throughput bar chart, (5) energy bar chart comparing thinking vs. non-thinking for C0/C1/C4 at 8K, (6) Pareto frontier (energy vs. NIAH accuracy).

### 6.5 Verification Plan

**Pre-flight sanity checks:**
- C0 at 512 tokens must pass NIAH (if the BF16 baseline fails, the test is broken)
- At 512 tokens (below 1024 capacity), C3 metrics should approximately match C1 metrics, confirming the eviction gate
- C2 vs C1 at 512: if NIAH fails on C2 but passes on C1, TurboQuant is too aggressive at 4-bit on Qwen3-4B

**Post-run validation:**
- Energy values must fall within physically reasonable range (T4: 12W idle–82W max during inference [19])
- C1 VRAM must be lower than C0 VRAM; C3 VRAM lower than C1 VRAM at 8K; C2 VRAM lower than C1 VRAM
- NaN perplexity values (if any) documented as known AWQ CUDA kernel artifact on certain group-size configurations

---

## 7. Data Analysis Plan

### 7.1 Statistical Framework

Following the hypothesis testing workflow specified in the course [27]:

1. **Normality check:** Shapiro-Wilk test on energy and NIAH metrics per configuration ($\alpha = 0.05$). If $p < 0.05$, use non-parametric alternatives.

2. **Main effect test:** If assumptions hold — one-way repeated-measures ANOVA with config as within-subjects factor; if non-normal — Kruskal-Wallis test.

3. **Pairwise comparisons:** Paired t-tests (normal) or Wilcoxon signed-rank tests (non-normal) with Bonferroni correction for 10 pairwise config comparisons.

4. **Effect size:** Cohen's $d$ for parametric tests; Cliff's $\delta$ for non-parametric.

5. **Reporting format:** Test statistic, degrees of freedom, $p$-value, and effect size for every comparison (e.g., "Paired t-test: $t(14) = 4.32$, $p < 0.001$, $d = 1.12$") [27].

### 7.2 Visualization Plan

| Plot | Variables | Purpose |
|---|---|---|
| Line plot | Peak VRAM vs. Context Length (one line per config) | Memory scaling behavior |
| Line plot | Energy (J) vs. Context Length | Energy efficiency ranking |
| Heatmap | NIAH accuracy (configs × context lengths) | Accuracy degradation patterns |
| Bar chart | Tokens/sec per config | Throughput comparison |
| Paired bar chart | Energy: non-thinking vs. thinking (C0, C1, C4 at 8K) | Thinking mode energy cost |
| Paired bar chart | NIAH: non-thinking vs. thinking | Reasoning quality under compression |
| Scatter plot | Energy vs. NIAH accuracy (Pareto frontier) | Optimal config identification |

### 7.3 Software Tools

- Python: `scipy.stats` (t-tests, ANOVA, Shapiro-Wilk), `statsmodels` (post-hoc tests), `pingouin` (effect sizes, power analysis), `matplotlib` + `seaborn` (visualization)
- G*Power or `statsmodels.stats.power` for post-hoc power analysis

---

## 8. Expected Results & Outcomes

### 8.1 Quantitative Predictions

| Config | VRAM @ 8K | Energy @ 8K | NIAH @ 8K | Tok/s @ 8K |
|---|---|---|---|---|
| C0 (BF16) | ~10.5 GB | ~1100 J | >95% | ~2 |
| C1 (AWQ) | ~9.5 GB | ~350 J | >90% | ~3 |
| C2 (AWQ+TQ) | ~9.3 GB | ~380 J | ~85% | ~2.5 |
| C3 (AWQ+evict) | ~9.0 GB | ~340 J | >90% | ~3 |
| C4 (all three) | ~8.8 GB | ~360 J | ~70% | ~2.5 |

**Note:** VRAM savings from KV cache techniques are expected to be modest at 8K context on a 4B model because the $O(n^2)$ prefill attention matrix dominates peak memory at this scale. Savings become more pronounced at 32K+ contexts.

### 8.2 Expected Pareto Frontier

- **Best accuracy (NIAH > 90%):** C1 (AWQ only) or C3 (AWQ + eviction)
- **Best energy efficiency:** C1 or C3
- **Best for memory-constrained edge (<4 GB):** C4 (all three)
- **Optimal all-rounder:** C3 (AWQ + PyramidKV eviction) — low energy, good accuracy, moderate memory
- **Thinking mode:** 2–5× more energy per task; C4 thinking may show degraded reasoning quality (consistent with ThinKV findings [25] that reasoning quality under compression is thought-type-dependent)

### 8.3 Expected Significance

This study will provide the first empirical, hardware-measured comparison of compound LLM compression strategies on a sub-4B SLM, yielding actionable Pareto-optimal configurations for three distinct stakeholder groups. The findings will directly inform energy-efficient AI deployment decisions in edge, cloud, and research contexts. The open-source implementation and dataset will serve as a reproducible benchmark for future work on sustainable SLM inference, addressing the gap identified by SLMQuant [24] regarding the lack of SLM-specific compression benchmarks with real hardware energy measurements.

---

## 9. Complex Engineering Problems Mapping

### EP1 — Depth of Knowledge Required (40%)

This research requires in-depth engineering knowledge (K8 level) across five domains:
- **Transformer architecture:** Attention mechanisms (Qwen3Attention with QK-Norm), KV cache dynamics, Grouped Query Attention (32 Q / 8 KV heads), Rotary Position Embeddings, YiARN scaling [1]
- **Quantization theory:** AWQ's activation-aware per-channel scaling for salient weight protection [2]; TurboQuant's random orthogonal rotation + induced Beta distribution + Lloyd-Max optimal scalar quantization + QJL inner product estimation [3]
- **Token eviction algorithms:** SnapKV's observation-window-based clustered selection [4]; PyramidKV's pyramidal information funneling with variable layer-wise cache allocation [5]
- **Hardware-software co-design:** GPU memory hierarchy (HBM2 on T4), CUDA kernel behavior under compressed caches, NVML power sensor polling at 10 Hz, T4 power state transitions (12W idle–82W active) [19]
- **Energy measurement methodology:** Power × time integration via pynvml, statistical noise reduction across 3 repetitions, handling thermal throttling and cold-down periods between runs [19]

### EP2 — Range of Conflicting Requirements (40%)

The problem involves fundamental trade-offs resolved through multi-objective Pareto analysis:
- **Memory vs. Accuracy:** More compression → lower memory → higher accuracy loss (H2, H4)
- **Energy vs. Latency:** TurboQuant saves memory but adds quantize/dequant overhead per decoding step (H2)
- **Energy vs. Reasoning Quality:** Thinking mode improves answers but costs 2–5× more energy (H5)
- **Throughput vs. Memory:** Larger batch sizes improve throughput but require more VRAM
- **Edge Feasibility vs. Model Capability:** 4B models fit on edge but have weaker reasoning than larger models

These trade-offs are quantified via the ablation study, statistically tested, and visualized as Pareto frontiers, enabling evidence-based configuration selection for each stakeholder group.

### EP5 — Extent of Applicable Codes (20%)

Four distinct stakeholder groups with widely varying needs:
- **Edge device manufacturers** (Qualcomm, MediaTek, NVIDIA Jetson): Need models running in <4 GB VRAM at <15W — prioritize C4 for maximum compression, accepting accuracy trade-offs
- **Cloud providers** (Google, AWS, Azure): Need maximum throughput at minimum energy per query — prioritize C1 or C3 for best energy-accuracy balance
- **End users:** Need acceptable response quality (NIAH > 80%) and reasonable latency (<5 seconds) — may accept C3 or C4 depending on task criticality
- **Green Computing researchers:** Need empirical baselines for compound compression on SLMs — the primary contribution, addressed by publishing the full 18-experiment dataset and analysis code

The research design explicitly measures the full accuracy-energy-memory space rather than optimizing for a single objective, ensuring actionable recommendations for all stakeholder groups.

---

## 10. Timeline

| Week | Milestone | Deliverable |
|---|---|---|
| 1–2 | Literature review + Proposal submission | Project proposal (5 marks) |
| 3 | Environment setup + verification | Verify Qwen3-4B-AWQ on HF, test NIAH sanity at BF16 on T4 Colab |
| 4 | Implementation | Build Python notebook: all 5 configs + PyramidKV/SnapKV monkey-patch + TurboQuant integration + GPU monitor |
| 4–5 | Debug + pilot run | Fix perplexity computation (active KV cache), NIAH extraction (completion-style), TurboQuant GQA compatibility |
| 5 | Full data collection | Run all 15 primary experiments + 3 thinking subset runs; save CSV after each config |
| 6 | Statistical analysis + visualization | Hypothesis tests (Shapiro-Wilk, ANOVA/Wilcoxon, post-hoc), Pareto frontier, all 7 plots |
| 7 | Writing (Results, Discussion, Conclusion) | Draft sections of term paper |
| 8 | Final submission | Complete term paper (15 marks) + presentation |

---

## 11. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| TurboQuant incompatible with Qwen3 GQA (8 KV heads, head_dim=128) | Medium | High | Verify with small pilot (single layer); fallback to KIVI [7] |
| PyramidKV integration too complex for Qwen3Attention with QK-Norm | Medium | Medium | Fallback to SnapKV [4] (monkey-patch pattern already exists for Llama/Mistral) |
| Colab T4 session timeout (12h limit) | Medium | Medium | Save CSV after each config; run in multiple sessions; starting from C0 ensures baseline data first |
| NaN perplexity from AWQ CUDA kernels at certain group sizes | High | Low | Document as known artifact; NIAH is primary accuracy metric; use WikiText-2 as secondary |
| NIAH fails on BF16 baseline (C0) | Low | Critical | Fix prompt format before full run; use completion-style prompts (needle at 50% depth); test on 512 context first |
| Thinking mode unparseable output (malformed `\boxed{}`) | Medium | Medium | Handle multiple delimiter formats (`\boxed{}`, `\boxed{...}`, plain text); log raw output for failed cases |

---

## 12. References

[1] Qwen Team. "Qwen3 Technical Report." arXiv:2505.09388, May 2025.

[2] Lin, J., Tang, J., Tang, H., Yang, S., Chen, W.-M., Wang, W.-C., Xiao, G., Dang, X., Gan, C., Han, S. "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration." MLSys 2024 (Best Paper).

[3] Zandieh, A., Daliri, M., Hadian, M., Mirrokni, V. "TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate." ICLR 2026.

[4] Li, Y., Huang, Y., Yang, B., Venkitesh, B., Locatelli, A., Ye, H., Cai, T., Lewis, P., Chen, D. "SnapKV: LLM Knows What You are Looking For Before Generation." NeurIPS 2024.

[5] Cai, Z., Zhang, Y., Gao, B., Liu, Y., Li, Y., Liu, T., Lu, K., Xiong, W., Dong, Y., Hu, J., Xiao, W. "PyramidKV: Dynamic KV Cache Compression based on Pyramidal Information Funneling." COLM 2025.

[6] Zhang, Z., Sheng, Y., Zhou, T., Chen, T., Zheng, L., Cai, R., Song, Z., Tian, Y., Ré, C., Barrett, C., Wang, Z., Chen, B. "H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models." NeurIPS 2023.

[7] Liu, Z., Yuan, J., Jin, H., Zhong, S., Xu, Z., Braverman, V., Chen, B., Hu, X. "KIVI: A Tuning-Free Asymmetric 2-bit Quantization for KV Cache." ICML 2024.

[8] Strubell, E., Ganesh, A., McCallum, A. "Energy and Policy Considerations for Deep Learning in NLP." ACL 2019.

[9] Patterson, D., et al. "Carbon Emissions and Large Neural Network Training." arXiv:2104.10350, 2021.

[10] Hoffmann, J., Borgeaud, S., Mensch, A., et al. "Training Compute-Optimal Large Language Models." NeurIPS 2022.

[11] Dao, T., Fu, D., Ermon, S., Rudra, A., Ré, C. "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness." NeurIPS 2022.

[12] Frantar, E., Ashkboos, S., Hoefler, T., Alistarh, D. "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers." ICLR 2023.

[13] Xiao, G., Lin, J., Seznec, M., et al. "SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models." ICML 2023.

[14] Kwon, W., Li, Z., Zhuang, S., et al. "Efficient Memory Management for Large Language Model Serving with PagedAttention." SOSP 2023.

[15] Leviathan, Y., Matias, Y., Schuster, T., et al. "Fast Inference from Transformers via Speculative Decoding." ICML 2023.

[16] Bender, E. M., Gebru, T., McMillan-Major, A., Shmitchell, S. "On the Dangers of Stochastic Parrots: Can Language Models Be Too Big?" FAccT 2021.

[17] IEA. "Energy Efficiency 2024." International Energy Agency, 2024.

[18] Sarker, et al. "Characterizing Energy Footprint of Small Language Models on Edges." arXiv:2511.11624, 2025.

[19] Argerich, M. F., Fürst, J., Patiño-Martínez, M. "Watt Counts: Energy-Aware Benchmark for Sustainable LLM Inference on Heterogeneous GPU Architectures." arXiv:2604.09048, 2026.

[20] Sustainable LLM Inference for Edge AI: Evaluating Quantized LLMs for Energy Efficiency, Output Accuracy, and Inference Latency. arXiv:2504.03360, 2025.

[21] EdgeCIM: Hardware-Software Co-Design for CIM-Based Acceleration of SLMs. arXiv:2604.11512, 2026.

[22] SLMQuant: Benchmarking Small Language Model Quantization for Practical Deployment. ACM RichMediaGAI 2025.

[23] Zheng, X., Li, Y., Chu, H., et al. "An Empirical Study of Qwen3 Quantization." arXiv:2505.02214, 2025.

[24] Salfati, S. "Quantization Dominates Rank Reduction for KV-Cache Compression." arXiv:2604.11501, 2026.

[25] Ramachandran, A., Neseem, M., Sakr, C., Venkatesan, R., Khailany, B., Krishna, T. "ThinKV: Thought-Adaptive KV Cache Compression for Efficient Reasoning Models." arXiv:2510.01290, 2026.

[26] Zhang, J., Guo, H., Benini, L., Li, Y. "RDKV: Rate-Distortion Bit Allocation for Joint Eviction and Quantization of the KV Cache." arXiv:2605.08317, 2026.

[27] CSE407 Term Project Discussion Slides. East West University, Summer 2026.
