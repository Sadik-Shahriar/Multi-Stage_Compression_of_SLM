# Project Findings Processing Tracker

## Purpose

This tracker records which project sources have been inspected for the master
paper-ready findings document, what was extracted, and what remains. It prevents
the final narrative from being written from memory or from one oversized context
window.

Master document:
`research/project_findings_master.md`

Status labels:

- `PENDING`: not yet inspected for the master document.
- `IN PROGRESS`: currently being inspected and written.
- `PROCESSED`: inspected and incorporated with provenance.
- `INVENTORIED`: file set checked, but individual raw rows/traces were not read
  line by line because validated manifests and integrity products are the
  authoritative summaries.
- `HISTORICAL ONLY`: retained for failure/process history, not current evidence.

## Processing Log

| Block | Status | Principal sources | Output section |
|---|---|---|---|
| Project scope, protocol, registry, and research questions | PROCESSED | `AGENTS.md`, `research/experiment_registry.json`, `research/research_plan.md`, course requirements | Sections 1-5 |
| Proposal and literature state | PROCESSED | `proposal/proposal.md`, `proposal/literature_review.md`, `proposal/references.bib`, validation docs | Sections 6 and 18 |
| Llama v5 systems experiment | PROCESSED | accepted v5 environment/results, registry, Notebook 00/legacy provenance | Sections 7-8 |
| Failed hard-retrieval pilots | PROCESSED | Notebooks 01-04, discarded pilot summaries, session completion plan | Section 9 |
| Llama hard-quality and matched control | PROCESSED | accepted Notebook 05 bundle and final integrity | Section 10 |
| Llama power robustness | PROCESSED | accepted Notebook 06 bundle/report and final integrity | Section 11 |
| Qwen adapter parity pilot | PROCESSED | accepted Notebook 07 bundle, registry, notebook | Section 12 |
| Qwen full reference experiment | PROCESSED | accepted Notebook 08 bundle, provenance, final integrity | Sections 13-14 |
| Cross-model synthesis | PROCESSED | provisional Notebook 09 bundle, findings, realization-gap products | Sections 15-16 |
| Accepted visualization bundle | PROCESSED | `evidence/accepted/CSE407_cross_model_visualization_v1/` (23 files) | Section 17 |
| Statistical interpretation | PROCESSED | All accepted energy/quality tests, synthesis registered inferential tables, Wilson intervals, interaction contrasts, bootstrap analyses | Section 18 |
| Failures, repairs, and provenance caveats | PROCESSED | pilot history, Notebook 08 repair record, source/version drift, environment stale status | Section 19 |
| Threats to validity and limitations | PROCESSED | measurement design, five-block resolution, single-session, model count, benchmark scope, NVML limits | Section 20 |
| Reproducibility and artifact map | PROCESSED | manifests, notebooks, bundle inventory, course submission artifacts | Section 21 |
| Paper-ready claims and unsupported claims | PROCESSED | synthesis findings, visualization findings, realization gap, eligibility rules | Section 22 |
| Remaining work | PROCESSED | paper formatting, proposal update, figure placement, reproducibility package, submission | Section 23 |

## Artifact Inventory Policy

The accepted experiment bundles contain hundreds of JSON shards and 195 raw
power traces. The master document will use their validated final-integrity files,
artifact manifests, registered statistical tables, and canonical CSV/JSON
summaries. Raw files are inventoried through their manifests and trace-validation
gates rather than manually paraphrased one by one. Any spot-check or direct raw
file inspection will be recorded below.

## Detailed Source Checklist

### Core Project Documents

- [x] `AGENTS.md`
- [ ] `prompt.md`
- [x] `research/experiment_registry.json`
- [x] `research/research_plan.md`
- [ ] `research/research_validation.md`
- [ ] `research/model_comparison.md`
- [ ] `research/cross_model_visualization_guide.md`
- [x] `experiments/track_a_failsafe_colab/README.md`
- [x] `course/discussion.md`
- [x] `course/research_questions.md`
- [ ] `course/checklists.md`
- [x] `course/term-project-submission.md`

### Llama Evidence

- [x] `CSE407_llama_v5_final` environment and canonical result tables
- [x] v5 artifact manifest and fingerprint
- [x] Notebooks 01-04 and discarded pilot evidence
- [x] `CSE407_llama_track_a_full_v1/analysis/final_integrity.json`
- [x] Notebook 05 quality/control summaries and registered rows
- [x] `CSE407_llama_power_robustness_v1/final_integrity.json`
- [x] Notebook 06 power robustness report and statistical tables

### Qwen Evidence

- [x] Notebook 07 adapter parity notebook and accepted pilot products
- [x] Notebook 08 source and repair provenance
- [x] Qwen artifact manifest
- [x] Qwen final integrity and analysis provenance
- [x] Qwen energy, quality, interaction, and power-stability tables

### Synthesis and Visualization

- [x] Provisional synthesis final integrity and output manifest
- [x] Normalized energy and quality products
- [x] Empirical effects and Pareto products
- [x] Ideal storage assumptions and calibrated footprints
- [x] Modeled byte demand and symbolic break-even products
- [x] Accepted visualization final integrity, protocol, metrics, and findings
- [x] Eight accepted visualization PNGs inspected; matching PDFs inventoried and hash-bound

### Proposal, Literature, and Paper

- [x] Canonical proposal Markdown (inspected for version drift; Section 19.7)
- [ ] LaTeX proposal/paper state (template present, content superseded)
- [x] Literature review and references (inspected; Section 19.7)
- [x] Research validation notes (inspected; Sections 6, 19)
- [x] Submission requirements and remaining formatting work (inspected; Sections 21.6, 23)

## Open Items

- Preserve/export the edited Notebook 09B itself if it is not yet in the local
  repository.
- Decide whether provisional synthesis fingerprint `b19adce0924b4203` will be
  independently promoted or rerun from one canonical Notebook 09 source.
- Integrate selected accepted visualization figures into the final paper.
- Complete the final paper narrative after this master findings document is
  cross-checked.
