# Research Plan — CSE407 Green Computing Term Project

**Title:** Holistic Optimization of Small Language Models for Energy-Efficient Edge Inference: An Empirical Ablation Study
**Student:** Md. Sadik Shahriar
**Course:** CSE407 Green Computing — East West University (Summer 2026)
**Instructor:** Ahmed Abdal Shafi Rasel (AASR)

---

## 1. Research Summary

| Field | Detail |
|---|---|
| **Model** | Qwen3-4B (4.0B params, 36 layers, GQA 32 Q / 8 KV heads) |
| **Hardware** | NVIDIA T4 (16 GB VRAM, 70W TDP) |
| **Weight quant** | AWQ (Activation-aware Weight Quantization) — 4-bit INT4 |
| **Token eviction** | PyramidKV (target) / SnapKV (fallback) — 1024-token capacity |
| **KV cache quant** | TurboQuant — 4-bit online vector quantization |
| **Thinking mode** | Qwen3-4B built-in `enable_thinking` — tested on a focused subset |
| **Metrics** | Peak VRAM, Avg Power (W), Energy (J), Throughput (tok/s), Perplexity, NIAH |
| **Context lengths** | 512, 2048, 8192 tokens |
| **Configurations** | C0 (BF16 baseline), C1 (AWQ), C2 (AWQ+TQ), C3 (AWQ+eviction), C4 (all three) |

---

## 2. Motivation & Background

### 2.1 The Problem

Transformer-based Large Language Models (LLMs) store a Key-Value (KV) cache during autoregressive generation. This cache grows linearly with sequence length. For long-document inference (8K–128K tokens), the KV cache dominates GPU memory and contributes significantly to energy consumption.

The AI industry's carbon footprint is accelerating:
- ICT contributes 2–3% of global CO₂, projected at 7–8% by 2030
- Data centers consume ~415 TWh/year — ~2% of global electricity (IEA, 2024)
- AI inference now produces more total carbon than one-time training
- Each AI query uses ~10× the energy of a web search

Small Language Models (SLMs, sub-7B parameters) are a promising direction for sustainable AI because they require fewer FLOPs per token and can run on lower-wattage hardware. However, they still suffer from the KV cache bottleneck.

### 2.2 The Gap

Three orthogonal compression techniques exist:
1. **Weight quantization** (AWQ, GPTQ) — compresses model weights to 4-bit
2. **Token eviction** (SnapKV, H2O, PyramidKV) — removes unimportant tokens from cache
3. **KV cache quantization** (TurboQuant, KIVI) — compresses surviving tokens to low-bit values

Existing literature studies these techniques in isolation. **No published work has empirically measured the compound energy effect of all three on a single SLM with real hardware power monitoring.** Furthermore, no study has quantified how a model's **built-in reasoning (thinking mode)** interacts with compression in terms of energy cost.

### 2.3 Why Qwen3-4B

| Reason | Detail |
|---|---|
| Official AWQ weights | `Qwen/Qwen3-4B-AWQ` exists on HuggingFace — no calibration needed |
| Built-in thinking mode | Switchable `enable_thinking` — lets us measure reasoning energy cost |
| Architecture maturity | Qwen3-4B-Base matches Qwen2.5-7B-Base on benchmarks per Qwen3 Technical Report |
| GQA efficiency | 32 Q / 8 KV heads — memory-efficient attention |
| Existing implementation | `implementation_plan.md` already targets Qwen3Attention with QK-Norm |
| AWQ performance | ~2.9 GB VRAM at INT4; ~52 tok/s (Transformers), ~200 tok/s (SGLang) |

### 2.4 Why This Combination

| Technique | Why Chosen | Why Not Alternatives |
|---|---|---|
| **AWQ** (weights) | Best-in-class for SLMs per EMNLP 2025; 3–4× speedup over FP16 | GPTQ: slower to quantize, worse perplexity. Pruning: doesn't generalize to SLMs |
| **PyramidKV** (eviction) | Best NIAH among eviction methods; variable layer budget more efficient | SnapKV: simpler but 5–15% worse NIAH. H2O/StreamingLLM: strictly worse for retrieval |
| **TurboQuant** (KV cache) | Data-oblivious, near-lossless at 3.5 bits, tested on Qwen models | KIVI: slight degradation on sub-7B. PolarQuant: less ecosystem support |

---

## 3. Research Questions & Hypotheses

### 3.1 Primary Research Question

*"How does stacking AWQ (4-bit weights), PyramidKV/SnapKV (1024-token capacity), and TurboQuant (4-bit KV cache) affect total inference energy (Joules), peak VRAM (MB), and NIAH retrieval accuracy compared to the uncompressed BF16 baseline and each individual technique, when running Qwen3-4B at context lengths of 512, 2048, and 8192 tokens on an NVIDIA T4 GPU?"*

### 3.2 Secondary Research Question

*"What is the additional energy cost of Qwen3-4B's built-in thinking mode under each compression configuration, and does compression disproportionately degrade reasoning quality relative to direct response?"*

### 3.3 Hypotheses

**H1:** AWQ (C1) reduces total inference energy by approximately 3× compared to the BF16 baseline (C0) at 8K context, while maintaining NIAH accuracy above 90%.

**H2:** Adding TurboQuant to AWQ (C2) reduces peak VRAM by ~15–20% compared to C1, but per-token energy increases by 5–15% due to the quantize/dequant overhead of the rotation transform.

**H3:** Adding token eviction (PyramidKV) to AWQ (C3) reduces peak VRAM at 8K+ context lengths but shows no effect at 512 tokens (where total tokens < capacity). NIAH accuracy remains comparable to C1.

**H4:** The compound configuration (C4 — all three techniques) achieves the lowest peak VRAM and total energy per task, but shows measurable NIAH degradation (10–30% reduction) due to compound compression noise from the interaction of eviction and quantization.

**H5:** Thinking mode increases total energy by 2–5× compared to non-thinking mode at the same configuration. This ratio is smaller under compressed configurations because fewer preserved tokens limit the depth of the reasoning chain.

**H0:** No statistically significant difference in energy consumption exists between configurations (paired t-test, α = 0.05).

---

## 4. Experimental Design

### 4.1 Configurations (5-Way Ablation)

| Config | Weights | Token Eviction | KV Cache Quant | What It Tests |
|---|---|---|---|---|
| **C0** | BF16 | None | FP16 (default) | Uncompressed baseline — the energy and memory cost without optimization |
| **C1** | AWQ 4-bit | None | FP16 (default) | Isolates the effect of weight quantization alone |
| **C2** | AWQ 4-bit | None | TurboQuant 4-bit | Isolates the effect of KV cache quantization (on top of AWQ) |
| **C3** | AWQ 4-bit | PyramidKV (cap=1024) | FP16 (default) | Isolates the effect of token eviction (on top of AWQ) |
| **C4** | AWQ 4-bit | PyramidKV (cap=1024) | TurboQuant 4-bit | Compound effect of all three techniques |

This design ensures each technique's individual contribution can be isolated:
- C1 − C0 = effect of weight quantization
- C2 − C1 = effect of KV cache quantization
- C3 − C1 = effect of token eviction
- C4 − C1 = effect of both eviction + cache quant (and their interaction)

### 4.2 Context Lengths

| Length | Rationale |
|---|---|
| **512 tokens** | Short — below PyramidKV capacity threshold (1024). All configs should behave identically to C1. Sanity check for bugs. |
| **2048 tokens** | Medium — exceeds capacity. PyramidKV activates. Moderate KV cache size. |
| **8192 tokens** | Long — largest tested. Where memory and energy savings should be most visible. |

### 4.3 Thinking Mode Subset

To limit experiment runtime while still addressing the secondary RQ, thinking mode is tested on:

| Config | Context | Rationale |
|---|---|---|
| C0 | 8192 | Baseline cost of reasoning on uncompressed model |
| C1 | 8192 | Does AWQ affect reasoning quality or energy? |
| C4 | 8192 | Can the compressed model still reason? What's the energy ratio? |

### 4.4 Experiment Matrix

| Axis | Values | Runs |
|---|---|---|
| Configs | C0, C1, C2, C3, C4 | 5 |
| Context lengths | 512, 2048, 8192 | 3 |
| Thinking mode (subset) | C0/C1/C4 at 8192 | 3 |
| **Total primary runs** | 5 × 3 = **15** | |
| **Total with thinking subset** | 15 + 3 = **18** | |

Each run produces: Inference time, Tokens/sec, Peak VRAM (MB), Average Power (W), Total Energy (J), Perplexity, NIAH accuracy, KV Cache size (MB).

---

## 5. Methodology

### 5.1 Environment

- **Python 3.10+** with PyTorch 2.4+
- Transformers 4.45+ (for Qwen3 support)
- AutoAWQ — for loading AWQ-quantized weights
- TurboQuant — `pip install turboquant`
- pynvml — for GPU power monitoring
- Hardware: Google Colab (T4 GPU, 16 GB VRAM, 70W TDP)

### 5.2 Implementation Steps

#### Step 1: Environment Setup
```
pip install turboquant autoawq transformers datasets accelerate
pip install matplotlib seaborn pandas scipy
pip install nvidia-ml-py3 psutil
```

#### Step 2: Imports & GPU Check
- Import all libraries, verify T4 GPU, print VRAM and CUDA version
- Check TurboQuant version and Qwen3 model availability

#### Step 3: Helper Functions
- `ExperimentResult` dataclass (stores all metrics per run)
- `GPUMonitor` class — background thread polling `pynvml` at 100ms for power (W)
- `clear_cache()` — torch CUDA cache clearing between runs
- `compute_perplexity()` — accepts optional `past_key_values` to measure WITH active cache (critical fix from old notebook)

#### Step 4: NIAH Implementation (Fixed)
- `create_needle_haystack()` — completion-style prompt (not open-ended)
  - Needle value: `"The secret project code name is SHADOW-8821."`
  - Inserted at 50% depth in haystack
  - Prompt ends with `"The secret project code name is"` → forces completion
- `check_needle()` — case-insensitive search for `"SHADOW-8821"` in generated response
- For thinking mode: extract final answer from `\boxed{...}` delimiter before checking

#### Step 5: PyramidKV / SnapKV Implementation
- Monkey-patch `Qwen3Attention.forward` to implement token eviction
- **PyramidKV approach** (target):
  - Allocate cache budget pyramidally across 36 layers (more in early layers, less in deep)
  - Use attention scores from observation window (last 32 tokens) to select top tokens per layer
- **SnapKV fallback** (if PyramidKV integration is too complex):
  - Uniform budget of 1024 tokens per layer
  - Same observation-window scoring
- Controlled by global `USE_EVICTION` and `EVICTION_METHOD` flags
- Key considerations for Qwen3:
  - Import from `transformers.models.qwen3.modeling_qwen3`
  - Handle QK-Norm (LayerNorm on Q and K before attention)
  - No QKV bias in Qwen3
  - Proper `apply_rotary_pos_emb` import from qwen3 module

#### Step 6: TurboQuant Integration
- Create `TurboQuantCache(key_bits=4, value_bits=4)` instance
- Pass as `past_key_values` to `model.generate()`
- Verify compatibility with Qwen3's GQA (8 KV heads)

#### Step 7: Model Loaders
- `load_bf16_model()` → `Qwen/Qwen3-4B` with `attn_implementation="eager"`
- `load_awq_model()` → `Qwen/Qwen3-4B-AWQ` with `attn_implementation="eager"`

#### Step 8: Experiment Runner
For each configuration:
1. Load appropriate model (BF16 or AWQ)
2. Set `USE_EVICTION` flag (on/off), `EVICTION_METHOD` (pyramid/snapkv)
3. Create `TurboQuantCache` if needed (C2, C4)
4. Set `enable_thinking` flag (False for primary, True for subset)
5. For each context length:
   a. Build NIAH test input
   b. Run generation with GPU monitoring
   c. Compute perplexity with active cache
   d. Check NIAH
   e. Store all metrics in `ExperimentResult`
6. Unload model, clear cache
7. Save intermediate results to CSV after each config

#### Step 9: Results Analysis
- Load CSV into pandas DataFrame
- Generate 4 primary plots:
  1. Peak VRAM vs Context Length (all configs, one line per config)
  2. Energy (J) vs Context Length (all configs)
  3. NIAH accuracy heatmap (configs × context lengths)
  4. Tokens/sec comparison bar chart
- Generate 2 thinking-mode plots:
  5. Energy comparison: non-thinking vs thinking (C0, C1, C4 at 8K)
  6. NIAH comparison: non-thinking vs thinking
- Statistical tests: Shapiro-Wilk normality → paired t-test or Wilcoxon
- Pareto frontier: energy vs NIAH accuracy with config labels

#### Step 10: Summary Report
- Auto-generated markdown with key findings
- Comparison table of all data points
- Answers to research questions
- Recommendations for edge deployment

### 5.3 Measurement Protocol

| Metric | Tool | Granularity |
|---|---|---|
| GPU Power (W) | pynvml (`nvmlDeviceGetPowerUsage`) | 100 ms polling |
| Energy (J) | avg_power(W) × inference_time(s) | Per run |
| Peak VRAM (MB) | `torch.cuda.max_memory_allocated()` | Per run (reset before each) |
| Inference Time (s) | Python `time.time()` | Wall clock |
| Throughput | `max_new_tokens / inference_time` | Per run |
| Perplexity | Cross-entropy loss with active cache | Per run |
| NIAH | Completion-string match | Per run |

### 5.4 Verification Plan

**Sanity checks before full run:**
1. **NIAH sanity**: C0 at 512 tokens must pass NIAH — if BF16 baseline fails, the test is broken
2. **Eviction gate**: At 512 tokens (below 1024 capacity), C3 metrics should ≈ C1 metrics
3. **TurboQuant isolation**: C2 vs C1 at 512 — if NIAH fails on C2 but passes on C1, TurboQuant is too aggressive for 4-bit

**Post-run validation:**
- No NaN perplexity values (known AWQ issue — acceptable if documented)
- Energy values physically reasonable (T4: 30–70W range during inference)
- C1 VRAM < C0 VRAM (AWQ reduces weight memory)
- C3 VRAM < C1 VRAM at 8K (eviction caps cache)
- C2 VRAM < C1 VRAM (quantized cache uses less memory)

---

## 6. Expected Outcomes

### 6.1 Quantitative Predictions

| Config | VRAM @ 8K | Energy @ 8K | NIAH @ 8K | Tok/s @ 8K |
|---|---|---|---|---|
| C0 (BF16) | ~10.5 GB | ~1100 J | >95% | ~2 |
| C1 (AWQ) | ~9.5 GB | ~350 J | >90% | ~3 |
| C2 (AWQ+TQ) | ~9.3 GB | ~380 J | ~85% | ~2.5 |
| C3 (AWQ+evict) | ~9.0 GB | ~340 J | >90% | ~3 |
| C4 (all three) | ~8.8 GB | ~360 J | ~70% | ~2.5 |

Note: VRAM values are approximate. At 8K context on a 4B model, the attention computation's O(n²) prefill matrix dominates VRAM, so KV cache savings are modest at this scale. Savings become dramatic at 32K+ contexts.

### 6.2 Expected Pareto Frontier

- **Best for accuracy (NIAH > 90%)**: C1 or C3
- **Best for energy efficiency**: C1 or C3
- **Best for memory-constrained edge (<4 GB)**: C4
- **Optimal all-rounder**: C3 (AWQ + eviction) — low energy, good accuracy, moderate memory

### 6.3 Expected Thinking Mode Findings

- Thinking mode: 2–5× more energy per task (2,000–8,000 internal thinking tokens)
- C4 thinking: may show degraded reasoning quality (fewer preserved tokens → shorter reasoning chains)
- Energy per **answer token** (excluding thinking tokens): similar across configs

---

## 7. Timeline

| Week | Milestone | Deliverable |
|---|---|---|
| **1–2** | Literature review + Proposal | Project proposal (5 marks) |
| **3** | Methodology design + Pilot | Verify Qwen3-4B-AWQ exists, test NIAH sanity |
| **4** | Implementation | Build Python notebook with all 5 configs |
| **4–5** | Debug | Fix perplexity, NIAH, PyramidKV integration |
| **5** | Data collection | Run all 15 experiments + 3 thinking subset |
| **6** | Analysis | Statistical tests, plots, Pareto frontier |
| **7** | Writing | Results, Discussion, Conclusion |
| **8** | Final report | Complete term paper (15 marks) + presentation |

---

## 8. Complex Engineering Problems Mapping

### EP1 — Depth of Knowledge Required (40%)

The research requires in-depth engineering knowledge (K8 level) across multiple domains:
- **Transformer architecture**: Attention mechanisms, KV cache dynamics, Grouped Query Attention (Qwen3-4B: 32 Q / 8 KV heads), QK-Norm, Rotary Position Embeddings
- **Quantization theory**: AWQ's activation-aware scaling, TurboQuant's random rotation + Beta distribution + Lloyd-Max quantizer + QJL inner product estimation
- **Token eviction algorithms**: PyramidKV's pyramidal information funneling hypothesis, attention score computation, observation window design
- **Hardware-software co-design**: GPU memory hierarchy, CUDA kernel behavior under compressed caches, NVML power sensor polling
- **Energy measurement methodology**: Power × time integration, statistical noise reduction, handling T4's power state transitions

### EP2 — Range of Conflicting Requirements (40%)

The problem involves fundamental trade-offs:
- **Memory vs. Accuracy**: More compression → lower memory → higher accuracy loss
- **Energy vs. Latency**: TurboQuant saves memory but adds quant/dequant overhead per token
- **Energy vs. Reasoning quality**: Thinking mode improves answers but costs 2–5× more energy
- **Throughput vs. Memory**: Larger batch sizes improve throughput but require more VRAM
- **Edge feasibility vs. Model capability**: Smaller models fit on edge but have weaker reasoning

These are quantified via the ablation study and visualized as Pareto frontiers.

### EP5 — Extent of Applicable Codes (20%)

Four distinct stakeholder groups with varying needs:
- **Edge device manufacturers** (Qualcomm, MediaTek, NVIDIA Jetson): Need models that run in <4 GB VRAM at <15W — prioritize C4
- **Cloud providers** (Google, AWS, Azure): Need maximum throughput at minimum energy per query — prioritize C1 or C3
- **End users**: Need acceptable response quality (NIAH > 80%) and reasonable latency (<5s) — may accept C3 or C4 depending on task
- **AI/Green Computing researchers**: Need empirical baselines for compound compression — the primary contribution of this study

The research design explicitly addresses all four by measuring the full accuracy-energy-memory space rather than optimizing for a single objective.

---

## 9. Literature Review Sources (Pre-Gathered)

### Core Papers (Required Reading)

| # | Paper | Venue | Relevance |
|---|---|---|---|
| 1 | [Qwen3 Technical Report](https://arxiv.org/abs/2505.09388) | arXiv, May 2025 | Model architecture, benchmarks, thinking mode |
| 2 | [AWQ: Activation-aware Weight Quantization](https://arxiv.org/abs/2306.00978) | MLSys 2024 Best Paper | Weight quantization methodology |
| 3 | [TurboQuant: Online Vector Quantization](https://arxiv.org/abs/2504.19874) | ICLR 2026 | KV cache quantization, our approach |
| 4 | [SnapKV: LLM Knows What You Are Looking For](https://arxiv.org/abs/2404.14469) | NeurIPS 2024 | Token eviction (fallback method) |
| 5 | [PyramidKV: Dynamic KV Cache Compression](https://arxiv.org/abs/2406.02069) | COLM 2025 | Token eviction (target method) |
| 6 | [H2O: Heavy-Hitter Oracle](https://arxiv.org/abs/2306.14048) | NeurIPS 2023 | Token eviction baseline |
| 7 | [KIVI: Asymmetric 2-bit KV Cache Quantization](https://arxiv.org/abs/2402.02750) | ICML 2024 | KV cache quantization baseline |
| 8 | [PolarQuant: KV Cache Quantization](https://arxiv.org/abs/2502.02617) | 2025 | KV cache quantization alternative |
| 9 | [Revisiting Pruning vs Quantization for SLMs](https://aclanthology.org/2025.findings-emnlp.645/) | EMNLP 2025 Findings | Justifies AWQ over pruning for sub-4B |
| 10 | [Speculative Decoding for SLMs](https://aclanthology.org/2026.eacl-long.255/) | EACL 2026 | Why we don't use speculative decoding (<2B fails) |
| 11 | [StreamingLLM: Attention Sinks](https://arxiv.org/abs/2309.17453) | ICLR 2024 | Token eviction baseline (poor retrieval) |
| 12 | [GPTQ: Post-Training Quantization](https://arxiv.org/abs/2210.17323) | ICLR 2023 | Weight quantization baseline |
| 13 | [SmoothQuant: W8A8 Quantization](https://arxiv.org/abs/2211.10438) | ICML 2023 | Alternative approach (activation quantization) |
| 14 | [QuIP#: Lattice-Based Quantization](https://arxiv.org/abs/2402.04396) | ICML 2024 | SOTA 2-bit weight quantization |
| 15 | [Keyformer: KV Cache Reduction](https://proceedings.mlsys.org/paper_files/paper/2024/hash/48fecef47b19fe501d27d338b6d52582-Abstract-Conference.html) | MLSys 2024 | Alternative eviction method |
| 16 | [ScissorHands: Persistence of Importance](https://arxiv.org/abs/2305.17118) | NeurIPS 2023 | Alternative eviction method |

### Background and Context Papers

| # | Paper | Relevance |
|---|---|---|
| 17 | IEA (2024) — Global electricity consumption of data centers | Energy context |
| 18 | Patterson et al. (2021) — Carbon emissions of AI training | AI carbon footprint |
| 19 | Bender et al. (2021) — Environmental impact of large language models | AI sustainability |
| 20 | Strubell et al. (2019) — Energy requirements of NLP models | Foundational energy measurement |
| 21 | Hoffmann et al. (2022) — Scaling laws | Model scaling and efficiency |
| 22 | Dao et al. (2022) — FlashAttention | Attention computation optimization |
| 23 | Kwon et al. (2023) — PagedAttention (vLLM) | KV cache memory management |
| 24 | Xiao et al. (2023) — Efficient Streaming LLMs | Streaming inference |
| 25 | Leviathan et al. (2023) — Speculative Decoding | Fast inference baseline |

### Benchmarking and Ethics Sources

| # | Resource | Purpose |
|---|---|---|
| 26 | LongBench / LongBench-E | Long-context evaluation |
| 27 | Needle in a Haystack (NIAH) | Retrieval accuracy |
| 28 | WikiText-2 | Perplexity evaluation |
| 29 | CodeCarbon (Python package) | Energy measurement standard |
| 30 | ISO/IEC 21031:2024 (SCI Standard) | Software Carbon Intensity |

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Qwen3-4B-AWQ not available on HF | Low | High | Fall back to AutoAWQ calibration |
| TurboQuant incompatible with Qwen3 GQA | Medium | High | Verify with small test; fall back to KIVI |
| PyramidKV too complex to integrate | Medium | Medium | Fall back to SnapKV (already partially implemented) |
| Colab T4 session timeout (12h limit) | Medium | Medium | Save CSV after each config; run in multiple sessions |
| NaN perplexity from AWQ CUDA kernels | High | Low | Document as known artifact; use NIAH as primary metric |
| NIAH fails on BF16 baseline | Low | Critical | Fix prompt format; test before full run |
| Thinking mode produces unparseable output | Medium | Medium | Handle multiple delimiter formats; log raw output |

---

## 11. References to Use in the Proposal

The proposal requires ≥3 cited sources in the problem statement and ≥25 in the final paper. For the proposal, cite at minimum:

1. Qwen3 Technical Report (2025) — for model capability claims
2. TurboQuant paper (ICLR 2026) — for KV cache quantization theory
3. AWQ paper (MLSys 2024) — for weight quantization methodology
4. IEA (2024) or similar — for energy context statistics
5. SnapKV or PyramidKV paper — for token eviction methodology
6. EMNLP 2025 SLM quantization paper — for justification of AWQ over pruning

Use IEEE numbered citation style throughout.
