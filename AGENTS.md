# Project Context — SLM Energy Ablation Study

## Project
Holistic Optimization of SLMs for Energy-Efficient Edge Inference — An Empirical Ablation Study stacking AWQ + PyramidKV/SnapKV + TurboQuant on Qwen3-4B with T4 GPU power monitoring.

## Directory Structure
```
Project/
├── AGENTS.md               # This file
├── proposal/               # Submission-ready proposal
│   ├── proposal.md         # Canonical markdown (12 sections, 27 citations)
│   ├── proposal.tex        # LaTeX source (ACM sigconf, 22 citations)
│   ├── references.bib      # BibTeX (24 entries, firecrawl-verified)
│   └── literature_review.md# Firecrawl-verified lit review (20+ entries)
├── research/               # Planning docs
│   ├── research_plan.md
│   ├── research_validation.md
│   ├── model_comparison.md
│   └── proposal_guide.md
├── course/                 # Course materials
│   ├── outline.md
│   ├── discussion.md       # RQs, hypotheses, EP rubrics, grading
│   ├── checklists.md
│   ├── research_questions.md
│   ├── lit_review_example.md
│   └── turboquant_reading.md
├── templates/              # LaTeX paper templates
│   ├── acm_sigconf.tex
│   └── ieee_proposal.tex
├── archive/                # Historical content (DO NOT use)
│   ├── Capstone_Proposal_Latest.md
│   ├── outdated/           # Qwen2.5-1.5B-era files
│   └── ...
└── .agents/                # OpenCode internal
```

## Status
- **proposal/proposal.tex** — written, 22 citations, firecrawl-verified
- **proposal/references.bib** — 24 entries, fixed all fabricated author names
- **proposal/proposal.md** — canonical markdown with 27 citations
- **proposal/literature_review.md** — firecrawl-verified (20+ entries)
- **research/research_plan.md** — master research plan

## Model
- **Qwen3-4B**: 36 layers, GQA (32 Q / 8 KV heads), 32K native context
- Thinking mode via chat template `/think` flag, answers in `\boxed{}` delimiters
- Official AWQ weights: `Qwen/Qwen3-4B-AWQ` on HF

## HW
- **NVIDIA T4**: 16 GB VRAM, 70W TDP, measured idle ~12W, max ~82W
- Google Colab via free tier

## Configs
- **C0**: BF16 (baseline)
- **C1**: AWQ 4-bit
- **C2**: AWQ + TurboQuant 4-bit
- **C3**: AWQ + PyramidKV (1024 cap)
- **C4**: AWQ + PyramidKV + TurboQuant (compound)
- Contexts: 512, 2048, 8192; Thinking subset: C0/C1/C4 at 8192

## Critical Facts
- AWQ > GPTQ on Qwen3-4B (66.0 vs 65.8 avg commonsense)
- TurboQuant: Zandieh, Daliri, Hadian, Mirrokni (ICLR 2026) — NOT "Zhou et al."
- SnapKV: Yuhong Li et al. (NeurIPS 2024) — NOT "Yuhang Li"
- PyramidKV: Zefan Cai et al. (COLM 2025) — NOT "Yang, Chen"
- Qwen3 Quant Study: Zheng, Xingyu et al. (arXiv 2505.02214) — NOT "Li, H."
- SLMQuant (arXiv 2511.13023): SLMs more quantization-sensitive than LLMs
- Quantization Dominates Rank Reduction (Salfati 2026, arXiv 2604.11501): INT4 preserves score ordering
- ThinKV (Ramachandran et al., arXiv 2510.01290): hybrid for reasoning models
- RDKV (Zhang et al., arXiv 2605.08317): joint eviction+quantization via rate-distortion
- Watt Counts (Argerich et al., arXiv 2604.09048): T4 power methodology

## Methodology
- 10 Hz pynvml polling for power
- Active KV cache passed for perplexity
- PyramidKV monkey-patch of Qwen3Attention.forward (fallback to SnapKV)
- TurboQuant: outlier-aware mixed precision (32 outlier at 5-bit, 96 at 3-bit)
- Paired t-tests / Wilcoxon + Bonferroni
- Pareto frontier (energy vs NIAH)

## Firecrawl
- CLI v1.19.19 installed
- API key: `fc-fa76f53e7d484a1f822168c4b3780f62`
- Commands: `firecrawl research search-papers/inspect-paper/read-paper/related-papers`
- No fabricated quotes — verify every claim via read-paper

## Next
- Compile proposal.tex on Overleaf (no local LaTeX compiler)
- Final spell-check
