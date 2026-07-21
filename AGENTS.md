# Project Context — SLM Energy Ablation Study

## Project
Holistic Optimization of SLMs for Energy-Efficient Edge Inference — An Empirical Ablation Study stacking AWQ + PyramidKV/SnapKV + TurboQuant on Llama 3.2-3B with T4 GPU power monitoring.

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
├── experiments/            # Experiment notebooks
│   ├── llama3_2_energy_ablation_colab.ipynb  # Primary experiment (active)
│   ├── qwen3_energy_ablation_colab_output.ipynb  # Archived (blocked)
│   └── qwen3_energy_ablation_colab_reconstructed output.ipynb  # Archived
├── archive/                # Historical content (DO NOT use)
│   ├── Capstone_Proposal_Latest.md
│   ├── outdated/           # Qwen2.5-1.5B-era files
│   └── ...
└── .agents/                # OpenCode internal
```

## Status
- **proposal/proposal.tex** — written, 22 citations, firecrawl-verified (still targets Qwen3-4B)
- **proposal/references.bib** — 24 entries, fixed all fabricated author names
- **proposal/proposal.md** — canonical markdown with 27 citations
- **proposal/literature_review.md** — firecrawl-verified (20+ entries)
- **research/research_plan.md** — master research plan (updated for Llama 3.2-3B)
- **experiments/llama3_2_energy_ablation_colab.ipynb** — written, ~53 KB, ready for Colab T4

## Model
- **Llama 3.2-3B-Instruct**: 28 layers, GQA (24 Q / 8 KV heads), 8K native context, head_dim=128
- No built-in thinking mode (simpler ablation — 5 configs × 3 contexts = 15 runs only)
- Official AWQ weights: `casperhansen/llama-3.2-3b-instruct-awq`
- Baseline FP16: `unsloth/Llama-3.2-3B-Instruct`

## HW
- **NVIDIA T4**: 16 GB VRAM, 70W TDP, measured idle ~12W, max ~82W
- Google Colab via free tier

## Configs
- **C0**: FP16 (baseline)
- **C1**: AWQ 4-bit
- **C2**: AWQ + TurboQuant 4-bit
- **C3**: AWQ + PyramidKV (layerwise budget avg 1024)
- **C4**: AWQ + PyramidKV + TurboQuant (compound)
- Contexts: 512, 2048, 8192 (no thinking mode subset)
- C2 TurboQuant validated via physical-storage gate (FP16-leak check)

## Critical Facts
- Llama 3.2-3B: 28 layers, 24 Q / 8 KV heads (3:1 GQA ratio)
- KVCache-Factory natively supports Llama for PyramidKV — no custom monkey-patch
- TurboQuant: Zandieh, Daliri, Hadian, Mirrokni (ICLR 2026) — NOT "Zhou et al."
- SnapKV: Yuhong Li et al. (NeurIPS 2024) — NOT "Yuhang Li"
- PyramidKV: Zefan Cai et al. (COLM 2025) — NOT "Yang, Chen"
- SLMQuant (arXiv 2511.13023): SLMs more quantization-sensitive than LLMs
- Quantization Dominates Rank Reduction (Salfati 2026, arXiv 2604.11501): INT4 preserves score ordering
- ThinKV (Ramachandran et al., arXiv 2510.01290): hybrid for reasoning models
- RDKV (Zhang et al., arXiv 2605.08317): joint eviction+quantization via rate-distortion
- Watt Counts (Argerich et al., arXiv 2604.09048): T4 power methodology

## Methodology
- 10 Hz pynvml polling for power
- Active KV cache passed for perplexity
- PyramidKV via KVCache-Factory `DynamicCache` adapter (falls back to SnapKV-style scoring)
- TurboQuantCache with physical-storage validation gate (rejects if FP16 copies retained)
- Paired t-tests / Wilcoxon + Bonferroni
- Pareto frontier (energy vs NIAH)

## Firecrawl
- CLI v1.19.19 installed
- API key: `fc-fa76f53e7d484a1f822168c4b3780f62`
- Commands: `firecrawl research search-papers/inspect-paper/read-paper/related-papers`
- No fabricated quotes — verify every claim via read-paper

## Next
- Run experiment notebook on Colab T4 runtime
- Check `cache_pilots.json` for TurboQuant validation outcome
- Update `proposal/` docs and `ieee_proposal.tex` after results are in
