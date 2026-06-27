# Phi-4 Mini 3.8B vs Qwen3 4B — Model Selection for Green Computing Project

## Quick Verdict

**Use Qwen3-4B.** For your Green Computing project specifically, Qwen3-4B is the better choice over Phi-4 Mini. It has official AWQ support, native thinking mode (relevant for evaluating reasoning-quality trade-offs under compression), stronger benchmark scores, and wider multilingual coverage — all at essentially the same hardware cost on a T4 GPU.

---

## Side-by-Side Comparison

| Specification | Microsoft Phi-4 Mini | Alibaba Qwen3-4B |
|---|---|---|
| **Parameters** | 3.8B | 4.0B |
| **Architecture** | Dense Transformer (GQA) | Dense Transformer (GQA, 32 Q / 8 KV heads) |
| **Release Date** | February 2025 | April 2025 (v1), July 2025 (Thinking-2507) |
| **Context Length** | 128K native (LongRoPE) | 32K native, 131K (YaRN) / 262K (Thinking-2507) |
| **Vocabulary** | 200,064 tokens | 151,936 tokens |
| **Languages** | 23 | 201 |
| **License** | MIT | Apache 2.0 |
| **Thinking Mode** | Separate variant (Phi-4-mini-reasoning) | Built-in, switchable on/off |
| **Multimodal** | Text only | Text (images/video via Qwen3.5) |

### Benchmark Scores

| Benchmark | Phi-4 Mini | Phi-4-mini-reasoning | Qwen3-4B (base) | Qwen3-4B (thinking) | Qwen3-4B-Thinking-2507 |
|---|---|---|---|---|---|
| **MMLU-Pro** | 52.8 | — | 50.6 | 70.4 | **74.0** |
| **MMLU** | **73.0** | — | 72.99 | — | — |
| **GPQA Diamond** | 24.6–38.2 | 52.0 | 36.9 | 55.9 | **65.8** |
| **MATH** | 62.0–71.2 | **94.6 (MATH-500)** | 54.1 | — | — |
| **AIME 2025** | 10.0 | 57.5 | — | 65.6 | **81.3** |
| **HumanEval** | 68.3–80.5 | — | — | — | — |
| **LiveCodeBench** | 33.1 | — | — | 48.4 | **55.2** |
| **IFEval** | 66.8 | — | — | 81.9 | **87.4** |

Sources: [Phi-4 Mini on Local AI Master](https://localaimaster.com/models/phi-4-mini), [Phi-4-mini-reasoning HF](https://huggingface.co/microsoft/Phi-4-mini-reasoning), [Qwen3-4B Technical Report](https://arxiv.org/html/2505.09388v1), [Qwen3-4B-Thinking-2507 HF](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507)

### Memory & Speed (Quantized)

| Metric | Phi-4 Mini | Qwen3-4B |
|---|---|---|
| **AWQ-INT4 VRAM** | ~2.1–2.8 GB | **~2.9 GB** |
| **Speed (Transformers, AWQ)** | ~300 tok/s (RTX 4090) | **~52 tok/s (T4-like), ~200 tok/s (SGLang, A100)** |
| **Q4_K_M GGUF size** | 2.49 GB | 2.41 GB |
| **BF16 size** | 8.1 GB | 8.0 GB |

Sources: [RunAIatHome Phi-4](https://www.runaiathome.com/model/phi-4-mini/), [Qwen3 Speed Benchmark](https://qwen.readthedocs.io/en/latest/getting_started/speed_benchmark.html), [llmrun Qwen3](https://llmrun.dev/model/qwen-qwen3-4b)

---

## Analysis for Your Green Computing Project

### Why Qwen3-4B Wins for This Project

**1. Official AWQ support from the Qwen team**
Qwen3 has first-party AWQ-quantized weights on HuggingFace (`Qwen/Qwen3-4B-AWQ`). This removes uncertainty about whether the AWQ quantization will work correctly — critical for your ablation study where AWQ is the foundation of C1–C4. Phi-4 Mini's AWQ support is community-driven and less battle-tested.

**2. Dual-mode thinking is a research advantage**
Qwen3-4B has built-in thinking mode (switchable on/off with `enable_thinking=True/False`). For your project, this lets you measure **how quantization and token eviction affect reasoning quality** — not just perplexity and NIAH. You can compare C0–C4 under both thinking and non-thinking modes, adding a valuable dimension to your analysis.

**3. Stronger reasoning under compression**
Qwen3-4B's MMLU-Pro score of 70.4 (thinking) vs Phi-4 Mini's 52.8 suggests Qwen3 retains more reasoning capability after the same compression. This is relevant to your EP2 conflicting requirements analysis — a model that maintains higher accuracy under compression gives you a better Pareto frontier.

**4. Better multilingual coverage (if relevant)**
201 languages vs 23. If your edge deployment scenario involves non-English text, Qwen3 is the clear choice.

**5. Architecture alignment with your existing work**
Your `implementation_plan.md` already targets Qwen3-4B:
> "Target Model: Qwen/Qwen3-4B (~8GB), AWQ: Qwen/Qwen3-4B-AWQ (~2.1GB)"
> "Attention class: Qwen3Attention in transformers.models.qwen3.modeling_qwen3"

Staying with Qwen3-4B means you reuse your planned SnapKV monkey-patch work (already designed for Qwen3Attention with QK-Norm handling). Switching to Phi-4 Mini would require redoing this integration from scratch.

### Where Phi-4 Mini Has Advantages

**1. MIT license (slightly more permissive than Apache 2.0)**
Not a meaningful difference for an academic project.

**2. Slightly smaller memory footprint at Q4 (~2.1–2.8 GB vs ~2.9 GB)**
Both fit comfortably on a T4 (16 GB). The ~0.5 GB difference is negligible for your experiments.

**3. Faster inference speed**
Phi-4 Mini reports ~300 tok/s on RTX 4090 vs Qwen3-4B's ~200 tok/s (SGLang). On a T4, this difference narrows. For energy measurement, faster inference at the same power means **lower total energy (Joules)** — which is actually better for Phi-4 Mini's case in a Green Computing context.

**4. Better availability in GGUF/llama.cpp ecosystem**
Phi-4 Mini has been in llama.cpp longer, with more quantization variants and community fine-tunes. Qwen3-4B's GGUF support has caught up since April 2025.

### The Real Question: Phi-4-mini-reasoning vs Qwen3-4B-Thinking-2507

If reasoning quality is important for your evaluation:

| Benchmark | Phi-4-mini-reasoning (3.8B) | Qwen3-4B-Thinking-2507 |
|---|---|---|
| **AIME 2025** | 57.5 | **81.3** |
| **MATH-500** | **94.6** | — |
| **GPQA Diamond** | 52.0 | **65.8** |

Qwen3-4B-Thinking-2507 (July 2025) pulls ahead significantly on AIME and GPQA. Phi-4-mini-reasoning matches on MATH-500. For general reasoning quality, Qwen3-4B wins.

---

## Final Recommendation

| Factor | Winner | Why |
|--------|--------|-----|
| **AWQ compatibility** | **Qwen3-4B** | Official AWQ weights, tested by Qwen team |
| **Reasoning quality** | **Qwen3-4B** | Higher MMLU-Pro, GPQA, AIME scores |
| **Memory efficiency** | Phi-4 Mini | Slightly smaller at Q4, but both fit T4 easily |
| **Speed / Energy** | Phi-4 Mini | ~300 tok/s vs ~200, meaning lower Joules for same work |
| **Integration effort** | **Qwen3-4B** | Your implementation_plan.md already targets Qwen3Attention |
| **Multilingual** | **Qwen3-4B** | 201 vs 23 languages |
| **Context length** | Tie | Both support 128K+ |
| **Thinking mode** | **Qwen3-4B** | Built-in, switchable — adds research dimension |
| **Ecosystem maturity** | Phi-4 Mini | Older, more community quantizations |

**Stick with Qwen3-4B.** It has the better benchmark profile, official AWQ support, native thinking mode for richer evaluation, and — most importantly — your implementation plan and SnapKV integration is already designed for it. The energy cost difference from slightly slower inference is a finding, not a problem — your ablation study will capture it.

If you want the absolute strongest reasoning from a small model, use **Qwen3-4B-Thinking-2507** (the July 2025 update), which achieves 81.3 on AIME 2025 — competitive with models 2x its size.
