# Deep Research: Validation & Optimization of Compound SLM Compression for Edge Inference

## Executive Summary

This report validates the current project plan — **AWQ (4-bit weight quantization) + SnapKV/PyramidKV (attention-based token eviction) + TurboQuant (KV cache quantization) on Llama 3.2-3B** — against the state of the art as of mid-2026.

**Core finding: The technical stack is state-of-the-art for SLM compression. Three validated decisions:**

1. **Llama 3.2-3B is the right architecture choice** — Official AWQ support from the community, native KVCache-Factory support for PyramidKV (no custom monkey-patch), 24 Q / 8 KV GQA heads for efficient inference, and proven TurboQuant compatibility with LLaMA architectures.
2. **AWQ + TurboQuant is the optimal quantization stack** — EMNLP 2025 confirms AWQ > all alternatives for sub-4B models; TurboQuant is the best KV cache quantizer (data-oblivious, near-lossless at 3.5 bits).
3. **PyramidKV is recommended over SnapKV** — Variable layerwise budget gives 5–15% better NIAH accuracy at the same memory budget; SnapKV remains a valid simpler fallback.

---

## 1. Key Findings

### 1.1 Model Architecture: Llama 3.2-3B

| Specification | Llama 3.2-3B |
|---|---|
| **Parameters** | 3.2B |
| **Layers** | 28 |
| **Attention** | GQA — 24 Q heads, 8 KV heads |
| **Head dim** | 128 |
| **Context** | 8K native (supports RoPE scaling to 32K+) |
| **Thinking mode** | None (simpler ablation — 15 runs only) |
| **AWQ support** | Community — `casperhansen/llama-3.2-3b-instruct-awq` on HuggingFace |
| **License** | Llama 3.2 Community License |

**Why Llama 3.2-3B is the right choice for this project:**
- **Official community AWQ weights** exist — no calibration needed for C1–C4
- **KVCache-Factory natively supports Llama** for PyramidKV — no custom attention monkey-patch required
- **TurboQuantCache supports LLaMA architecture** — the cache wrapper works without architecture-specific changes
- **No built-in thinking mode** simplifies the ablation (5 configs × 3 contexts = 15 runs instead of 18+)
- **28 layers with 3:1 GQA ratio** gives a meaningful PyramidKV layer budget gradient

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

**For Llama 3.2-3B (28 layers)**: The pyramid allocation is especially beneficial — the variable budget across layers maps naturally to Llama's uniform architecture.

**Decision**: Target PyramidKV for implementation. Fall back to SnapKV if integration complexity becomes prohibitive — 90% of energy savings come from the other components anyway.

### 1.3 Weight Quantization: AWQ Is Optimal for SLMs

| Finding | Source |
|---------|--------|
| **AWQ > GPTQ > SparseGPT > Wanda** for SLMs (sub-4B) | [EMNLP 2025 Findings](https://aclanthology.org/2025.findings-emnlp.645/) |
| **Pruning does NOT generalize to SLMs** — AWQ beats all pruning at same compression | Same source |
| **AWQ achieves 3–4× speedup over FP16** with negligible perplexity increase | [AWQ Paper](https://arxiv.org/abs/2306.00978) |
| **Llama 3.2-3B has community AWQ weights** — `casperhansen/llama-3.2-3b-instruct-awq` | HuggingFace |

**Decision**: AWQ is locked in. `casperhansen/llama-3.2-3b-instruct-awq` is a well-maintained community quant.

### 1.4 KV Cache Quantization: TurboQuant Is Best-in-Class

| Aspect | TurboQuant | KIVI |
|--------|-----------|------|
| Bit-width | 2.5–3.5 bits/channel | 2-bit K + 2-bit V |
| Data requirement | **None (data-oblivious)** — online, no calibration | Tuning-free (distribution-dependent) |
| Small model compat. | ✅ Tested on Qwen2.5-1.5B | ⚠️ Degradation on sub-7B |
| Compression | 5× at 3.5 bits, cosine similarity ~0.985 | 2.6× peak memory |
| Overhead | Low (random rotation matrix) | Low (fused CUDA ops) |
| Accuracy | Near-lossless at 3.5b | Near-lossless on 7B+ |

**Decision**: TurboQuant is locked in. It's data-oblivious (no calibration for your ablation), compatible with LLaMA architectures, and growing ecosystem (vLLM 0.18+, llama.cpp). A physical-storage validation gate in the notebook confirms no FP16 copies leak through.

---

## 2. Simplified Ablation Design (No Thinking Mode)

The switch from Qwen3-4B (with built-in thinking mode) to Llama 3.2-3B (no thinking mode) simplifies the experimental design:

- **Reduced experiment count**: 5 configs × 3 contexts = 15 runs (vs 18+ with thinking mode subset)
- **No output parsing complexity**: No `\boxed{}` delimiters or thinking-token stripping needed
- **Cleaner attribution**: All energy is generation energy — no reasoning overhead to disentangle
- **Faster total runtime**: Less risk of Colab session timeout

The trade-off is losing the "reasoning cost" experimental dimension. However, the primary research question — *"What is the compound energy effect of stacking AWQ + PyramidKV + TurboQuant?"* — is fully addressed with the 5-config × 3-context design.

---

## 3. Contrarian Views and Risks

### 3.1 PyramidKV via KVCache-Factory
KVCache-Factory natively supports Llama for PyramidKV — no custom monkey-patch needed. The `DynamicCache` adapter handles budget allocation. Fall back to SnapKV-style scoring if the adapter has issues.

### 3.2 TurboQuant Physical Storage Validation
TurboQuantCache may silently retain FP16 copies of K/V tensors, defeating the purpose of quantization. The notebook includes a **physical-storage validation gate** that compares total storage bytes of the cache against the FP16 baseline — C2/C4 are rejected if the gate fails.

### 3.3 Perplexity Must Use Active Cache
As noted in the notebook, perplexity must be computed with the **active cache** (TurboQuantCache / evicted DynamicCache), not the default cache. Without this, C1 and C4 will show identical perplexity and the ablation is invalid.

---

## 4. Revised Recommendations

### Final Stack

```
Model:         Llama 3.2-3B (FP16 baseline) / casperhansen/llama-3.2-3b-instruct-awq
Weights:       AWQ INT4 (community HuggingFace weights)
KV Eviction:   PyramidKV via KVCache-Factory (target) / SnapKV (fallback)
KV Quant:      TurboQuant 4-bit (TurboQuantCache + storage validation gate)
Hardware:      NVIDIA T4 (16 GB VRAM, 70W TDP)
Measurement:   pynvml (power), torch.cuda.max_memory_allocated (VRAM)
```

### Priority Action Items

| Priority | Change | Impact |
|----------|--------|--------|
| **P0** | Run experiment notebook on Colab T4 | Primary deliverable |
| **P0** | Check `cache_pilots.json` for TurboQuant validation | Foundation for C2/C4 |
| **P1** | If C2 TurboQuant validation fails, fall back to HQQ | Valid C2/C4 comparison |
| **P2** | Run all 15 experiments (5 configs × 3 contexts) | Complete ablation data |
| **P3** | Statistical analysis (paired t-test, Pareto frontier) | Answer research questions |
| **P4** | Update proposal docs with results | Final submission |

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
- [Llama 3.2 Model Card](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct)
- [casperhansen/llama-3.2-3b-instruct-awq](https://huggingface.co/casperhansen/llama-3.2-3b-instruct-awq)
- [ChunkKV NIAH Comparison](https://arxiv.org/html/2502.00299v5)

### Tools
- [TurboQuant GitHub](https://github.com/0xSero/turboquant)
- [KVCache-Factory (PyramidKV)](https://github.com/Zefan-Cai/KVCache-Factory)
- [CodeCarbon](https://codecarbon.io/)
