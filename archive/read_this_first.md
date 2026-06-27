# CSE407 Green Computing — Term Project Context

## What We Are Building

An empirical ablation study stacking **AWQ** (weight quantization), **PyramidKV/SnapKV** (token eviction), and **TurboQuant** (KV cache quantization) on **Qwen3-4B** to measure energy, memory, and accuracy trade-offs for edge inference on an **NVIDIA T4 GPU** (70W TDP). Includes built-in thinking mode as a secondary axis.

## Current Task

Write or fix the **project proposal** (5 marks) as LaTeX using the ACM sigconf template. The proposal must satisfy the course requirements below.

---

## Required Reading Order (read these first)

### 1. Core Research Plan
| File | Why Read It |
|---|---|
| `research_plan.md` | Master document: full motivation, RQs, hypotheses, experimental design, 5×3 ablation matrix, methodology, timeline, EP mapping, literature sources, risk assessment |

### 2. Proposal Guidance
| File | Why Read It |
|---|---|
| `proposal_guide.md` | Section-by-section guide for writing the proposal targeting Qwen3-4B |
| `proposal.md` | Markdown draft of the proposal (the source we wrote before converting to LaTeX) |
| `proposal/proposal.tex` | Current LaTeX version of the proposal |
| `proposal/references.bib` | BibTeX references for the proposal |

### 3. Model Selection Rationale
| File | Why Read It |
|---|---|
| `model_comparison.md` | Why Qwen3-4B was chosen over Phi-4 Mini 3.8B |

### 4. SOTA Validation
| File | Why Read It |
|---|---|
| `research_validation.md` | Validates that our chosen stack (AWQ + TurboQuant + PyramidKV) is still SOTA; documents alternatives considered |

### 5. Course Requirements (Mandatory)
| File | Why Read It |
|---|---|
| `Course Files/CSE407 - Term Project - Discussion - Summer 26.md` | Full research framework: weak vs strong RQs, hypothesis structure, statistical tests, EP1/EP2/EP5 rubrics, timeline, grading criteria |
| `Course Files/Checklists for Term Project - CSE407.md` | Self-evaluation checklist for every proposal section (problem statement, aims, objectives, RQs, methods) |
| `Course Files/2026.2.CSE407.02.03.AASR.CourseOutline.md` | Official course outline: CO4 mapping, EP definitions, mark distribution |
| `Course Files/7. Good_Research_Questions.ppt.md` | How to formulate strong research questions (avoid value-laden, obvious, unfalsifiable) |
| `Course Files/Check this paper to understand how Structured Literature Review is written.md` | Example of a well-structured ACM survey paper |

### 6. ACM LaTeX Template
| File | Why Read It |
|---|---|
| `paper_templates/overleaf template for manuscript.tex` | ACM sigconf format: `\documentclass[sigconf]{acmart}`, `\bibliographystyle{ACM-Reference-Format}`, sectioning, tables, figures |

---

## Outdated Files (DO NOT USE — Qwen2.5-1.5B era)

These files are in `outdated/` and reference the old model and approach. Read them only if you need historical context for debugging a specific implementation detail.

| File | Reason Outdated |
|---|---|
| `outdated/research_overview.md` | Targeted Qwen2.5-1.5B, not Qwen3-4B |
| `outdated/project_context.md` | Qwen2.5-1.5B details, old SnapKV implementation notes |
| `outdated/implementation_plan.md` | Qwen2.5-1.5B specific, monkey-patches `Qwen2Attention`, not `Qwen3Attention` |
| `outdated/CSE407_Green_Computing_FinalResults.ipynb` | Old experiment notebook for Qwen2.5-1.5B |

---

## Key Decisions Summary

| Decision | Choice | Rationale |
|---|---|---|
| **Model** | Qwen3-4B | Official AWQ weights on HF, built-in thinking mode, 36 layers, GQA (32Q/8KV), 32K context |
| **Weight quant** | AWQ 4-bit | Best-in-class for SLMs per EMNLP 2025; 3–4× speedup over FP16 |
| **Eviction** | PyramidKV (target) / SnapKV (fallback) | PyramidKV gives 5–15% better NIAH at same budget; PyramidKV too complex → fallback to SnapKV |
| **KV cache quant** | TurboQuant 4-bit | Data-oblivious, near-lossless at 3.5 bits, tested on Qwen models |
| **Context lengths** | 512, 2048, 8192 | 512 = below eviction capacity gate; 8192 = longest feasible on T4 with prefill |
| **Configurations** | C0 (BF16), C1 (AWQ), C2 (AWQ+TQ), C3 (AWQ+evict), C4 (all three) | Isolates each technique's individual contribution |
| **Thinking mode** | Tested on C0/C1/C4 at 8K only | Limits experiment runtime while addressing secondary RQ |
| **Hardware** | NVIDIA T4 (Colab) | Only available GPU; 16 GB VRAM, 70W TDP |
| **NIAH prompt** | Completion-style | Forces model to output "SHADOW-8821"; avoids open-ended failure mode |
| **Perplexity** | Compute with active `past_key_values` | Without this, C1 and C4 return identical perplexity (bug fixed) |

---

## Proposal Requirements (from Course Outline)

### Structure (must include all):
1. **Introduction & Background** — Green computing context, AI energy problem, SLMs as alternative, research gap
2. **Problem Statement** — "The problem this research addresses is..." with ≥3 cited papers
3. **Research Objectives** — General aim + specific objectives with active verbs (implement, measure, quantify, analyze, construct)
4. **Research Questions** — Specific, measurable, scoped; primary RQ + secondary RQ
5. **Hypotheses** — H1–H4 with quantitative predictions; H0 with named statistical test (α=0.05); H5 for thinking mode
6. **Planned Methodology** — Experimental design (5×3+3=18 runs), environment, measurement protocol, implementation steps, verification plan
7. **Data Analysis Plan** — Shapiro-Wilk → t-test/ANOVA or Wilcoxon/Kruskal-Wallis; effect sizes; visualization plan
8. **Expected Results & Outcomes** — Quantitative predictions table, Pareto frontier
9. **EP Mapping** — EP1 (depth of knowledge), EP2 (conflicting requirements), EP5 (stakeholder codes)
10. **Risk Assessment** — With likelihood, impact, and mitigation
11. **Timeline** — 8-week plan with milestones
12. **References** — ≥25 IEEE-style; Core: Qwen3 Tech Report, AWQ, TurboQuant, SnapKV/PyramidKV, IEA 2024

### Writing Rules:
- **No personal pronouns** in problem statement ("I, we, us, me, my")
- Every claim needs a citation or measured data
- IEEE numbered citation style: `\cite{qwen3, awq, turboquant}`
- ACM sigconf format: `\documentclass[sigconf]{acmart}`, `\bibliographystyle{ACM-Reference-Format}`

### Grading (5 marks):
- Cognitive (C6 — Creating): 3 marks
- Affective (A3/A4 — Valuing/Organizing): 0.5 marks
- Psychomotor (P3 — Precision): 0.5 marks

### EP Weighting:
- **EP1 (Depth of Knowledge):** 40% — Analyze using specified knowledge profile (K8 research literature)
- **EP2 (Conflicting Requirements):** 40% — Compare conflicting technical/engineering issues
- **EP5 (Applicable Codes):** 20% — Differentiate diverse stakeholder groups

---

## File Paths (Absolute)

All paths start from: `C:\Users\Sadik\Documents\Google Antigravity\CSE407\Project\`

| Purpose | Path |
|---|---|
| LaTeX proposal | `proposal/proposal.tex` |
| BibTeX references | `proposal/references.bib` |
| Proposal markdown source | `proposal.md` |
| Research plan | `research_plan.md` |
| Proposal guide | `proposal_guide.md` |
| Model comparison | `model_comparison.md` |
| Research validation | `research_validation.md` |
| Course discussion | `Course Files/CSE407 - Term Project - Discussion - Summer 26.md` |
| Course checklists | `Course Files/Checklists for Term Project - CSE407.md` |
| Course outline | `Course Files/2026.2.CSE407.02.03.AASR.CourseOutline.md` |
| Good RQs guide | `Course Files/7. Good_Research_Questions.ppt.md` |
| Literature review example | `Course Files/Check this paper to understand how Structured Literature Review is written.md` |
| ACM template | `paper_templates/overleaf template for manuscript.tex` |

---

## Common Pitfalls to Avoid

1. **Don't reference Qwen2.5 or 1.5B** — the model is Qwen3-4B (4.0B params)
2. **Don't remove EP1/EP2/EP5 sections** — they are 40%/40%/20% of the proposal rubric
3. **Don't use open-ended NIAH prompts** — must be completion-style
4. **Don't compute perplexity without active past_key_values** — bug from old notebook
5. **Don't cite non-scientific sources** — no blogs, Wikipedia, or news articles
6. **Don't use personal pronouns** in problem statement section
7. **Don't forget the thinking mode axis** — it is a secondary RQ worth marks
8. **Don't embed the BibTeX in the .tex** — keep it in `references.bib` as a separate file

---

## Verification Checklist for the New Model

After making changes, verify:
- [ ] `\cite{...}` keys all exist in `references.bib`
- [ ] No reference to Qwen2.5 or 1.5B anywhere
- [ ] At least 25 references in the .bib file
- [ ] Problem statement cites ≥3 papers
- [ ] EP1, EP2, EP5 sections present with proper rubrics
- [ ] Hypotheses include H0 with named statistical test
- [ ] No personal pronouns in §2 (Problem Statement)
- [ ] ACM sigconf format used correctly
- [ ] File compiles without errors
