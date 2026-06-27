# Deep Research: Validation & Optimization of Compound SLM Compression for Edge Inference

## Executive Summary

This report validates the current project plan — **AWQ (4-bit weight quantization) + SnapKV/PyramidKV (attention-based token eviction) + TurboQuant (KV cache quantization) on Qwen3-4B with built-in thinking mode** — against the state of the art as of mid-2026.

**Core finding: The technical stack is state-of-the-art for SLM compression. Three validated decisions:**

1. **Qwen3-4B is the right architecture choice** — Official AWQ support, built-in thinking mode (adds a second experimental dimension), 32 Q / 8 KV GQA heads for efficient inference, and your SnapKV monkey-patch is already designed for Qwen3Attention.
2. **AWQ + TurboQuant is the optimal quantization stack** — EMNLP 2025 confirms AWQ > all alternatives for sub-4B models; TurboQuant is the best KV cache quantizer (data-oblivious, near-lossless at 3.5 bits).
3. **PyramidKV is recommended over SnapKV** — Variable layerwise budget gives 5–15% better NIAH accuracy at the same memory budget; SnapKV remains a valid simpler fallback.

---

## 1. Key Findings

### 1.1 Model Architecture: Qwen3-4B

| Specification | Qwen3-4B |
|---|---|
| **Parameters** | 4.0B (non-embedding: 3.6B) |
| **Layers** | 36 |
| **Attention** | GQA — 32 Q heads, 8 KV heads |
| **Context** | 32K native, 131K (YaRN), 262K (Thinking-2507) |
| **Thinking mode** | Built-in, switchable via `enable_thinking=True/False` |
| **AWQ support** | Official — `Qwen/Qwen3-4B-AWQ` on HuggingFace |
| **AWQ VRAM** | ~2.9 GB at INT4 |
| **License** | Apache 2.0 |
| **Languages** | 201 |

**Why Qwen3-4B is the right choice for this project:**
- **Official AWQ weights** exist — no calibration needed for C1–C4
- **Built-in thinking mode** lets you measure the energy cost of reasoning as a secondary experimental axis
- **Your SnapKV implementation** in `implementation_plan.md` already targets `Qwen3Attention` with QK-Norm handling
- **Qwen3-4B-Base matches Qwen2.5-7B-Base** on most benchmarks (per Qwen3 Technical Report) — you're getting 7B-class capability at 4B size

### 1.2 Token Eviction: PyramidKV > SnapKV

| Method | Keep Criteria | Budget per Layer | Overhead | NIAH (128 budget) | LongBench (64 budget) |
|--------|--------------|-----------------|----------|-------------------|----------------------|
| StreamingLLM | Position (sink + recent) | Uniform | None | ~24% | 26.87 |
| H2O | Cumulative attention | Uniform | Moderate | ~48% | 33.89 |
| **SnapKV** | Observation window attention | **Uniform** | Low | ~59% | 34.36 |
| **PyramidKV** | Pyramid budget + attention | **Variable (pyramid)** | Low | **~65%** | **39.35** |
| Ada-KV | Attention + adaptive head budget | **Variable (per-head)** | Low | ~67% | ~38 |

Sources: NIAH from [ChunkKV Table 7](https://arxiv.org/html/2502.00299v5); LongBench from [PyramidKV Table 1](https://arxiv.org/html/2406.02069v3)

**PyramidKV exploits pyramidal information funneling**: early layers have dispersed attention (need more cache), deep layers focus on few tokens (need less). SnapKV's uniform budget wastes deep-layer capacity and starves early layers.

**For Qwen3-4B (36 layers)**: The pyramid allocation is especially beneficial because each layer is a meaningful fraction of total budget.

**Decision**: Target PyramidKV for implementation. Fall back to SnapKV if integration complexity becomes prohibitive — 90% of energy savings come from the other components anyway.

### 1.3 Weight Quantization: AWQ Is Optimal for SLMs

| Finding | Source |
|---------|--------|
| **AWQ > GPTQ > SparseGPT > Wanda** for SLMs (sub-4B) | [EMNLP 2025 Findings](https://aclanthology.org/2025.findings-emnlp.645/) |
| **Pruning does NOT generalize to SLMs** — AWQ beats all pruning at same compression | Same source |
| **AWQ achieves 3–4× speedup over FP16** with negligible perplexity increase | [AWQ Paper](https://arxiv.org/abs/2306.00978) |
| **Qwen3-4B has official AWQ weights** — tested by Qwen team with SGLang benchmarks | [Qwen3 Speed Benchmark](https://qwen.readthedocs.io/en/latest/getting_started/speed_benchmark.html) |

**Decision**: AWQ is locked in. Qwen3-4B-AWQ is a first-party HuggingFace model.

### 1.4 KV Cache Quantization: TurboQuant Is Best-in-Class

| Aspect | TurboQuant | KIVI |
|--------|-----------|------|
| Bit-width | 2.5–3.5 bits/channel | 2-bit K + 2-bit V |
| Data requirement | **None (data-oblivious)** — online, no calibration | Tuning-free (distribution-dependent) |
| Small model compat. | ✅ Tested on Qwen2.5-1.5B | ⚠️ Degradation on sub-7B |
| Compression | 5× at 3.5 bits, cosine similarity ~0.985 | 2.6× peak memory |
| Overhead | Low (random rotation matrix) | Low (fused CUDA ops) |
| Accuracy | Near-lossless at 3.5b | Near-lossless on 7B+ |

**Decision**: TurboQuant is locked in. It's data-oblivious (no calibration for your ablation), tested on Qwen models, and growing ecosystem (vLLM 0.18+, llama.cpp).

---

## 2. Rethinking with Thinking Mode

### 2.1 Experimental Design Impact

Qwen3-4B's built-in thinking mode lets you toggle between:
- **Non-thinking**: Direct response (low latency, low energy)
- **Thinking**: Internal chain-of-thought (2,048+ internal tokens, higher energy, better reasoning)

This adds a valuable experimental dimension to your ablation:

| Config | Non-thinking | Thinking |
|--------|-------------|----------|
| C0 (BF16) | Baseline energy/accuracy | Cost of reasoning on uncompressed model |
| C1 (AWQ) | Quantization impact on direct response | Does AWQ affect reasoning quality? |
| C2 (AWQ+TQ) | KV quant + weight quant interaction | Same, with compressed cache |
| C3 (AWQ+PyramidKV) | Token eviction + quantization | Does eviction hurt reasoning more? |
| C4 (All three) | Max compression, direct response | Can compressed model still reason? |

### 2.2 Measurement Considerations for Thinking Mode

- Output length in thinking mode is unpredictable (2K–8K internal tokens before answer)
- Measure energy **per answer token** (strip thinking tokens from total)
- NIAH needle must be extracted from final answer inside `\boxed{}` delimiter
- Perplexity is not meaningful in thinking mode — use downstream accuracy instead

### 2.3 Recommended Primary Design

Run the core ablation in **non-thinking mode** (5 configs × 3 context lengths = 15 experiments). Then run a focused subset (C0, C1, C4 at 8K) in **thinking mode** to produce an energy-accuracy-reasoning Pareto frontier.

---

## 3. Contrarian Views and Risks

### 3.1 PyramidKV Integration Complexity
PyramidKV requires per-layer budget allocation. For Qwen3-4B's 36 layers, you need to tune the pyramid ratio. Fall back to SnapKV if implementation time is tight — the energy contribution of eviction is secondary to AWQ and TurboQuant.

### 3.2 TurboQuant + Qwen3 GQA Compatibility
Qwen3-4B has 8 KV heads (GQA). TurboQuant was designed for MHA. The random rotation operates per-head, so GQA should not cause issues, but this needs empirical validation in C2.

### 3.3 Thinking Mode Doubles Experiment Time
30 experiments (15 non-thinking + 15 thinking) vs 15. On a T4, this could exceed Colab session limits. Recommended mitigation: run thinking mode only on a 3-config × 1-length subset.

### 3.4 Perplexity Is Still Broken for C2/C4
As noted in `implementation_plan.md`, perplexity must be computed with the **active cache** (TurboQuant/SnapKV), not the default cache. This is critical — without it, C1 and C4 will show identical perplexity and the ablation is invalid.

---

## 4. Revised Recommendations

### Final Stack

```
Model:         Qwen3-4B (BF16 baseline) / Qwen/Qwen3-4B-AWQ
Weights:       AWQ INT4 (official HuggingFace weights)
KV Eviction:   PyramidKV (target) / SnapKV (fallback)
KV Quant:      TurboQuant 4-bit (TurboQuantCache)
Thinking mode: Primary axis (non-thinking) + subset (thinking)
Hardware:      NVIDIA T4 (16 GB VRAM, 70W TDP)
Measurement:   pynvml (power), torch.cuda.max_memory_allocated (VRAM)
```

### Priority Action Items

| Priority | Change | Impact |
|----------|--------|--------|
| **P0** | Fix perplexity with active cache | Correct accuracy metric |
| **P0** | Fix NIAH with completion-style prompt | Valid retrieval measure |
| **P1** | Verify Qwen3-4B-AWQ exists on HuggingFace | Foundation for C1–C4 |
| **P2** | Implement PyramidKV (or SnapKV fallback) | +5–15% NIAH |
| **P3** | Add thinking-mode subset experiments | Richer Pareto frontier |
| **P4** | Test at 32K context | Demonstrate TurboQuant value |

---

## 5. Sources

### Papers
- [Qwen3 Technical Report](https://arxiv.org/abs/2505.09388) — May 2025
- [SnapKV: LLM Knows What You Are Looking For Before Generation](https://arxiv.org/abs/2404.14469) — NeurIPS 2024
- [PyramidKV: Dynamic KV Cache Compression](https://arxiv.org/abs/2406.02069) — COLM 2025
- [TurboQuant: Online Vector Quantization](https://arxiv.org/abs/2504.19874) — ICLR 2026
- [AWQ: Activation-aware Weight Quantization](https://arxiv.org/abs/2306.00978) — MLSys 2024 Best Paper
- [Revisiting Pruning vs Quantization for SLMs](https://aclanthology.org/2025.findings-emnlp.645/) — EMNLP 2025 Findings

### Benchmarks
- [Qwen3-4B-Thinking-2507 Benchmarks](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507)
- [Qwen3 Official Speed Benchmarks](https://qwen.readthedocs.io/en/latest/getting_started/speed_benchmark.html)
- [ChunkKV NIAH Comparison](https://arxiv.org/html/2502.00299v5)

### Tools
- [TurboQuant GitHub](https://github.com/0xSero/turboquant)
- [KVCache-Factory (PyramidKV)](https://github.com/Zefan-Cai/KVCache-Factory)
- [CodeCarbon](https://codecarbon.io/)
