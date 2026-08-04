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
├── experiments/            # Active experiment notebooks
│   └── track_a_failsafe_colab/  # Numbered Track A notebooks
├── evidence/               # Immutable/provisional experiment bundles
│   ├── accepted/bundles/
│   ├── provisional/bundles/
│   └── discarded/bundles/
├── notebooks/              # Executed and historical notebook copies
├── archive/                # Historical content (DO NOT use)
├── context/session_history/# Prior session notes (historical)
├── repairs/                # Paste-ready Colab repair cells
├── tools/legacy/           # Historical utility scripts
├── logs/                   # Retained execution logs
└── .agents/                # OpenCode internal
```

## Status
- **proposal/proposal.tex** — written, 22 citations, firecrawl-verified (still targets Qwen3-4B)
- **proposal/references.bib** — 24 entries, fixed all fabricated author names
- **proposal/proposal.md** — canonical markdown with 27 citations
- **proposal/literature_review.md** — firecrawl-verified (20+ entries)
- **research/research_plan.md** — master research plan (updated for Llama 3.2-3B)
- **evidence/accepted/bundles/CSE407_llama_v5_final/** — immutable completed v5 systems evidence: 380
  execution rows and 95 power traces, fingerprint `8d27af8c9ee94de3`
- **experiments/track_a_failsafe_colab/05_llama_full_quality_control_v1.ipynb**
  — completed hard-retrieval/control run: 300 quality rows and five C1-W energy
  blocks, fingerprint `106a561c07c62937`
- **evidence/accepted/bundles/CSE407_llama_track_a_full_v1/** — immutable accepted Notebook 5 artifacts;
  final integrity passed
- **06_llama_power_robustness_analysis.ipynb** — completed against all 100
  immutable traces, fingerprint `91ebc63773e735e6`; rankings and registered
  significance decisions were stable under 82 W and 70 W caps
- **evidence/accepted/bundles/CSE407_llama_power_robustness_v1/** — immutable accepted A3 derived evidence
- **07_qwen2_5_adapter_parity_pilot_v1.ipynb** — completed Qwen adapter pilot;
  five immutable artifacts passed all gates, fingerprint `91def77c920729e9`
- **evidence/accepted/bundles/CSE407_qwen_track_a_adapter_pilot_v1/** — immutable accepted Qwen pilot
  evidence; do not modify
- **08_qwen2_5_full_reference_v1.ipynb** — completed Qwen experiment; 455
  measurement rows and 95 power traces passed final integrity under schema
  `track-a-qwen-full-reference-v1-2026-08-04-1`, fingerprint `861d89617e53034d`
- **evidence/accepted/bundles/CSE407_qwen_track_a_reference_v1/** — immutable accepted A4 evidence;
  artifact manifest `975cb8f19405f9d7e4267bc4a8143ead943c853776c6ba88b8697695ac78c1c9`
- **09_cross_model_synthesis_v1_colab.ipynb** — clean Colab-ready CPU-only A5
  notebook; Drive execution is pending
- **evidence/provisional/bundles/CSE407_cross_model_synthesis_local_provisional/** — validated local reference
  output, fingerprint `b19adce0924b4203`; not authoritative Colab evidence
- Prior Colab artifacts use a flat `/content/drive/MyDrive/CSE407_*` layout;
  Notebook 09 resolves this artifact base separately from the source tree

## Experiment Delivery Rule
- All new experiment implementations must be self-contained Google Colab
  `.ipynb` notebooks with clear Markdown cells, numbered run order, validation
  gates, and isolated Drive output paths.
- Do not create standalone `.py` files as experiment runners.
- Track A notebooks live under `experiments/track_a_failsafe_colab/`.

## Model
- **Llama 3.2-3B-Instruct**: 28 layers, GQA (24 Q / 8 KV heads), 8K native context, head_dim=128
- No built-in thinking mode; completed evidence includes a 380-row systems matrix
  plus 300 hard-quality and five matched-control energy rows
- Official AWQ weights: `casperhansen/llama-3.2-3b-instruct-awq`
- Baseline FP16: `unsloth/Llama-3.2-3B-Instruct`
- **Qwen2.5-3B-Instruct**: 36 layers, GQA (16 Q / 2 KV heads), 32K native
  context, head_dim=128; completed evidence includes 75 core energy, 20
  sensitivity energy, 300 core quality, and 60 sensitivity-quality rows

## HW
- **NVIDIA T4**: 16 GB nominal VRAM and a 70 W enforced limit in completed runs;
  raw NVML includes isolated transients up to 124.496 W overall and 116.109 W
  in the Qwen run
- Google Colab via free tier

## Configs
- **C0**: FP16 (baseline)
- **C1 / C1-W**: AWQ 4-bit stock / matched-wrapper baseline
- **C2**: AWQ + custom pyramidal eviction (layerwise budget avg 1024)
- **C3-Ref**: AWQ + `turboquant==0.2.0` numerical reference path
- **C4-Ref**: AWQ + custom pyramidal eviction + TQ-Ref (sequential compound)
- Historical systems contexts: 1024, 2048, 4096
- Frozen hard-retrieval context: 4096; 60 scenarios per configuration
- TQ-Ref is numerically active but not packed, fused, or physically 4-bit

## Critical Facts
- Llama 3.2-3B: 28 layers, 24 Q / 8 KV heads (3:1 GQA ratio)
- KVCache-Factory supports Llama, but accepted evidence uses a validated custom
  Llama attention wrapper and custom PyramidKV-style scorer
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
- Custom PyramidKV-style eviction through a validated Llama attention wrapper
- TQ-Ref validates indices, norms, residuals, materialized K/V, active cache use,
  and alias-deduplicated live storage; retained materialized K/V is reported
  rather than rejected
- Paired t-tests / Wilcoxon + Bonferroni
- Pareto frontier (energy vs NIAH)
- Notebook 09 separates measured, realized-reference, and ideal packed/fused
  evidence; it proves only conditional persistent-memory results and uses an
  indexed non-traffic-overhead versus modeled compulsory-byte-demand break-even
  model

## Firecrawl
- CLI v1.19.19 installed
- API key: `fc-fa76f53e7d484a1f822168c4b3780f62`
- Commands: `firecrawl research search-papers/inspect-paper/read-paper/related-papers`
- No fabricated quotes — verify every claim via read-paper

## Next
- Keep the registered Notebook 5 evidence immutable
- Preserve/export the executed Notebook 07 copy for the reproducibility package
- Keep `evidence/accepted/bundles/CSE407_qwen_track_a_reference_v1/` immutable; Notebook 08 required two
  in-session repair cells, now preserved inline in the exported notebook
- Run `09_cross_model_synthesis_v1_colab.ipynb` in a Colab CPU runtime and
  independently accept the resulting `CSE407_cross_model_synthesis_v1/` bundle
- Complete final paper formatting, figure placement, and reproducibility package
