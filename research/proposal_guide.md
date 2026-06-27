# Project Proposal Guide — CSE407 Green Computing

## Your Project at a Glance

**Institution:** East West University, CSE407 Green Computing, Summer 2026
**Instructor:** Ahmed Abdal Shafi Rasel (AASR)
**Student:** Md. Sadik Shahriar
**Model:** Qwen3-4B | **Hardware:** NVIDIA T4 (16GB, 70W TDP)

**Research:** An empirical ablation study investigating how stacking AWQ (4-bit weight quantization), PyramidKV/SnapKV (attention-based token eviction), and TurboQuant (KV cache quantization) affects the energy efficiency, memory footprint, and accuracy of a 4B-parameter SLM during edge-like inference — with an additional axis evaluating the energy cost of the model's built-in thinking mode.

---

## How to Write the Project Proposal

The proposal is worth **5 marks** and maps to CO4 (C6: Creating, 3 marks; A3/A4: Valuing/Organizing, 0.5 marks; P3: Precision, 0.5 marks). Required sections:

### 1. Introduction & Background

**Global context**: ICT contributes 2–3% of global CO₂ emissions. Data centers consume ~415 TWh/year (~2% of global electricity), projected to double by 2030 (IEA, 2024). AI inference now produces more total carbon than one-time training — each AI query uses ~10× the energy of a web search.

**Technical context**: Transformer-based LLMs store a Key-Value (KV) cache during generation that grows linearly with context length. For long-document inference, this cache dominates memory and energy. Small Language Models (SLMs, sub-7B) are promising for edge deployment but still face the KV cache bottleneck.

**The gap**: Prior work has studied weight quantization (AWQ), token eviction (SnapKV, H2O), and KV cache compression (TurboQuant, KIVI) in isolation. No published study has empirically measured the **compound energy effect** of stacking all three techniques on a single SLM while monitoring real hardware power draw. Additionally, no study has quantified the **energy cost of reasoning** (thinking mode) under compressed configurations.

### 2. Problem Statement

Frame as Complex Engineering Problems (per course outline):

**EP1 — Depth of knowledge required (40%):** The problem cannot be resolved without in-depth engineering knowledge at the level of K8 (Research Literature):
- Transformer attention mechanics and the KV cache growth problem
- Activation-aware weight quantization (AWQ) theory
- Attention-based token eviction algorithms (SnapKV observation windows, PyramidKV pyramidal information funneling)
- Online vector quantization theory (TurboQuant's random rotation + Beta distribution + QJL)
- Hardware power monitoring via NVML and energy measurement methodology

**EP2 — Range of conflicting requirements (40%):** Three-way trade-off:
- Aggressive memory compression → lower energy → higher accuracy degradation
- TurboQuant adds quant/dequant overhead → may ironically *increase* energy per token
- Thinking mode improves reasoning quality → dramatically increases energy (2–5× more tokens)
- Edge deployment requires low memory AND low energy AND acceptable accuracy simultaneously

**EP5 — Extent of applicable codes (20%):** Diverse stakeholders with varying needs:
- Edge device manufacturers: prioritize memory and power constraints
- Cloud providers: prioritize throughput and total energy at scale
- End users: prioritize response quality and latency
- AI researchers: need empirical baselines for compound compression

### 3. Research Objectives

**General aim:** To empirically investigate the compound effect of AWQ, PyramidKV/SnapKV, and TurboQuant on the energy efficiency, memory footprint, and accuracy of a 4B-parameter SLM during edge-like inference, including the energy cost of reasoning.

**Specific objectives:**
1. **Measure** peak VRAM, average power (W), total energy (J), and throughput (tok/s) for all 5 configurations across 3 context lengths in non-thinking mode
2. **Isolate** each technique's contribution via ablation — compare C1 (AWQ only) vs C2 (AWQ+TQ) vs C3 (AWQ+eviction) vs C4 (all three)
3. **Quantify** the energy cost of reasoning by comparing non-thinking vs thinking mode on a focused subset
4. **Determine** the Pareto-optimal configuration(s) for the energy-accuracy-memory trade-off
5. **Evaluate** whether compound compression enables deployment on edge-class hardware (<4 GB VRAM)

### 4. Research Questions

**Primary research question:**
*"How does stacking AWQ (4-bit weights), PyramidKV/SnapKV (1024-token capacity), and TurboQuant (4-bit KV cache) affect total inference energy (Joules), peak VRAM (MB), and NIAH retrieval accuracy compared to the uncompressed BF16 baseline and each individual technique, when running Qwen3-4B at context lengths of 512, 2048, and 8192 tokens on an NVIDIA T4 GPU?"*

**Secondary research question:**
*"What is the additional energy cost of Qwen3-4B's built-in thinking mode under each compression configuration, and does compression disproportionately degrade reasoning quality relative to direct response?"*

**Hypotheses:**
- **H1:** AWQ (C1) reduces energy by ~3× over BF16 baseline at 8K context without significant NIAH degradation
- **H2:** Adding TurboQuant to AWQ (C2) further reduces peak VRAM but increases per-token energy due to quant/dequant overhead
- **H3:** Adding token eviction to AWQ (C3) reduces peak VRAM at 8K+ contexts and maintains NIAH accuracy
- **H4:** C4 (all three) achieves the lowest peak VRAM and energy but shows NIAH degradation from compound compression noise
- **H5:** Thinking mode increases total energy by 2–5× over non-thinking at the same configuration, but this ratio is smaller under compression (fewer tokens to reason with)
- **H0:** No statistically significant difference in energy between configurations (paired t-test, α = 0.05)

### 5. Planned Methodology

**Model:**
- BF16 baseline: `Qwen/Qwen3-4B` (~8 GB at FP16, ~2.9 GB at AWQ-INT4)
- AWQ quantized: `Qwen/Qwen3-4B-AWQ` (official HuggingFace weights)
- Thinking mode: switchable via `enable_thinking=True/False`

**Hardware:**
- GPU: NVIDIA T4 (16 GB VRAM, 70W TDP, compute capability 7.5)
- Power monitoring: pynvml background thread polling at 100 ms

**Experimental design — 5 × 3 × 2 = 30 runs (with thinking subset):**

| Config | Weights | Token Eviction | KV Cache Quant | Description |
|---|---|---|---|---|
| C0 | BF16 | None | FP16 cache | Uncompressed baseline |
| C1 | AWQ 4-bit | None | FP16 cache | Weight quantization only |
| C2 | AWQ 4-bit | None | TurboQuant 4-bit | + KV cache compression |
| C3 | AWQ 4-bit | PyramidKV (cap=1024) | FP16 cache | + Token eviction |
| C4 | AWQ 4-bit | PyramidKV (cap=1024) | TurboQuant 4-bit | All three stacked |

Context lengths: 512, 2048, 8192 tokens
Thinking mode subset: C0, C1, C4 at 8192 tokens

**Metrics:**
- Peak VRAM (MB) — `torch.cuda.max_memory_allocated()`
- Average power (W) — pynvml polling
- Total energy (J) — avg power × inference time
- Throughput (tokens/sec) — `max_new_tokens / time`
- Perplexity — WikiText-2, computed WITH active cache for C2/C4
- NIAH accuracy — completion-style prompt (fixed from old notebook)
- KV cache size (MB) — actual tensor sizes

**Data analysis:**
- Shapiro-Wilk normality test → paired t-test (parametric) or Wilcoxon signed-rank (non-parametric)
- Effect size reporting (Cohen's d)
- Pareto frontier visualization (energy vs. NIAH accuracy vs. VRAM)

### 6. Expected Results

- **C1**: ~3× energy reduction vs C0, NIAH > 90% at all lengths
- **C2**: Slightly higher per-token energy than C1 (quant/dequant overhead), lower peak VRAM
- **C3**: VRAM savings only visible at 8K+ (SnapKV inactive below 1024 tokens), NIAH comparable to C1
- **C4**: Lowest VRAM and energy per task, NIAH may drop to 60–80% at 8K
- **Pareto frontier**: C2 or C3 likely optimal for energy-accuracy balance; C4 optimal for memory-constrained deployment
- **Thinking mode**: 2–5× energy increase, with compressed configs showing a smaller ratio (fewer preserved tokens limit reasoning depth)

### 7. EP5 — Stakeholder Analysis

| Stakeholder | Need | How This Research Addresses It |
|---|---|---|
| Edge device manufacturers | Models fitting in <4 GB VRAM | C4 achieves ~1.5 GB total footprint |
| Cloud providers | Lower energy per inference | Quantifies exactly which technique saves how many Joules |
| End users | Functional accuracy | Measures NIAH across all configs |
| AI researchers | Empirical baselines | First compound ablation with real power monitoring |

---

## ACM Template Instructions

Your `paper_templates/overleaf template for manuscript.tex` is an ACM `sigconf` template. Fill in:
- **Title**: "Holistic Optimization of Small Language Models for Energy-Efficient Edge Inference: An Empirical Ablation Study"
- **Author**: Md. Sadik Shahriar, East West University
- **Abstract**: 150–250 words covering problem, RQ, method (5 configs × 3 lengths, 2 thinking modes), key metrics, expected outcomes
- **CCS Concepts**: `Computing methodologies → Natural language generation; Applied computing → Green computing`
- **Reference format**: IEEE numbered style, 25+ sources minimum

---

## Key Resources in Your Repo

| File | Use For |
|---|---|
| `research_overview.md` | Existing problem statement and methodology draft |
| `research_validation.md` | SOTA validation, alternative analysis, architecture justification |
| `implementation_plan.md` | Technical implementation details, SnapKV code, Qwen3 attention patch |
| `project_context.md` | Known issues (NaN perplexity, NIAH difficulty) |
| `Course Files/CSE407 - Term Project - Discussion - Summer 26.md` | RQ formulation, hypothesis templates, statistical workflow |
| `Course Files/Checklists for Term Project - CSE407.md` | Self-evaluation checklist for every section |
| `model_comparison.md` | Qwen3-4B vs Phi-4 Mini rationale |
| `research_plan.md` | Complete research plan document |
