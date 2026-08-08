# Paper Figure & Evidence Use Guide

Purpose: rebuild `paper/main.tex` figures from the correct evidence sources,
remove unnecessary/outdated figures, and add the missing accepted figures so the
paper is detailed and impressive.

Applies on top of `paper/PARETO_UPDATE_GUIDE.md` (the v5 Pareto removal).

---

## 1. Authoritative sources of plots (evidence tree)

| Source (immutable) | Figures provided | Status |
|---|---|---|
| `evidence/accepted/CSE407_cross_model_visualization_v1/` | `fig01`–`fig08` (PDF + PNG) | **Canonical** — validated 09B set, viz fingerprint `53ead4e6db45d2a8` |
| `evidence/accepted/bundles/CSE407_llama_power_robustness_v1/` | `core_4096_power_cap_robustness.{pdf,png}`, `maximum_power_samples.png` | Accepted A3 |
| `evidence/accepted/bundles/CSE407_llama_v5_final/` | `v5_final_results.png`, `v5_final_sensitivity_4096.png`, `v5_final_system_tradeoffs_4096.png`, `v5_final_pareto_uncertainty_4096.*` | Accepted but historical; energy valid, Pareto quality ceiling-limited |
| `evidence/provisional/bundles/CSE407_cross_model_synthesis_local_provisional/` | `fig_hard_quality_wilson`, `fig_energy_throughput_vs_context`, `fig_measured_realized_ideal_storage`, `fig_interaction_by_power_regime`, `fig_energy_break_even_regions`, `fig_empirical_and_projected_pareto` (PDF+PNG) + CSVs | Provisional; fingerprint `b19adce0924b4203` |

Note: `paper/figures/` currently contains a MIX — the provisional family
(`fig_*` names) and the accepted family (`fig01`–`fig08`). For any figure that
exists in both families, prefer the **accepted `fig01`–`fig08`** versions.

---

## 2. Inventory of `paper/figures/` (current state)

### Referenced by `main.tex` (11 files)

| File | Referenced at | Source | Verdict |
|---|---|---|---|
| `v5_final_results.png` | main.tex:478 | v5 accepted | Keep, or optionally drop (mostly subsumed by fig02) |
| `fig_interaction_by_power_regime.pdf` | main.tex:555 | provisional 09 | Keep (unique interaction content) |
| `v5_final_system_tradeoffs_4096.png` | main.tex:568 | v5 accepted | Keep (throughput/VRAM, unique) |
| `v5_final_pareto_uncertainty_4096.pdf` | main.tex:644 | v5 accepted | **DELETE — outdated** (PARETO_UPDATE_GUIDE.md) |
| `core_4096_power_cap_robustness.pdf` | main.tex:708 | robustness accepted | Keep |
| `maximum_power_samples.png` | main.tex:724 | robustness accepted | Keep |
| `v5_final_sensitivity_4096.png` | main.tex:737 | v5 accepted | Optional — replace with fig03 + Qwen table |
| `fig_hard_quality_wilson.pdf` | main.tex:842 | provisional | **Swap → `fig03_retrieval_wilson.pdf` (accepted)** |
| `fig_energy_throughput_vs_context.pdf` | main.tex:899 | provisional | **Swap → `fig02_measured_context_scaling.pdf` (accepted)** |
| `fig_measured_realized_ideal_storage.pdf` | main.tex:917 | provisional | **Swap → `fig04_storage_realization_gap.pdf` (accepted)** |
| `fig08_measured_pareto_energy_quality_memory.pdf` | main.tex:962 | accepted 09B | Keep (correct) |

### NOT referenced by `main.tex` (8 files)

| File | Status |
|---|---|
| `fig01_measured_tq_overhead.pdf` | **ADD to Results** — ranked #1 main-paper candidate (findings §17.10) |
| `fig02_measured_context_scaling.pdf` | Use instead of `fig_energy_throughput_vs_context.pdf` |
| `fig03_retrieval_wilson.pdf` | Use instead of `fig_hard_quality_wilson.pdf` |
| `fig04_storage_realization_gap.pdf` | Use instead of `fig_measured_realized_ideal_storage.pdf` |
| `fig05_ideal_packed_components.pdf` | **ADD to appendix** |
| `fig06_modeled_phase_byte_demand.pdf` | **ADD to appendix** |
| `fig07_symbolic_energy_break_even.pdf` | **ADD to appendix** |
| `fig_empirical_and_projected_pareto.pdf` | **DELETE** — methodologically risky and unused |

---

## 3. Planned figure set for the final paper

| # | File | Placement | Content | Evidence tier |
|---|---|---|---|---|
| 1 | `fig01_measured_tq_overhead.pdf` | Results | TQ-Ref total/prefill/decode energy overhead by context, both models | measured_system |
| 2 | `fig02_measured_context_scaling.pdf` | Results | Prefill/decode energy + throughput across 1024/2048/4096 | measured_system |
| 3 | `fig03_retrieval_wilson.pdf` | Results | Wilson intervals: Llama hard-60, Qwen hard-60, Qwen common-15 TQ bits | measured_system |
| 4 | `fig04_storage_realization_gap.pdf` | Results | Matched vs realized TQ-Ref vs ideal packed storage (log axis) | measured + ideal |
| 5 | `fig05_ideal_packed_components.pdf` | Appendix | Ideal storage decomposition (indices, norms, residual, metadata) | ideal_counterfactual |
| 6 | `fig06_modeled_phase_byte_demand.pdf` | Appendix | Prefill/decode logical byte-demand dumbbells | ideal_counterfactual |
| 7 | `fig07_symbolic_energy_break_even.pdf` | Appendix | O_net/epsilon_mem break-even boundaries | symbolic |
| 8 | `fig08_measured_pareto_energy_quality_memory.pdf` | Results | Measured energy–quality–memory Pareto (bootstrap edge width) | measured_system |
| — | `fig_interaction_by_power_regime.pdf` | Results | Sequential interaction under raw/82W/70W | measured_system |
| — | `core_4096_power_cap_robustness.pdf` | Results | Power-cap robustness bars | measured_system |
| — | `maximum_power_samples.png` | Results | Max NVML sample distribution, 82/70 lines | measured_system |
| — | `v5_final_system_tradeoffs_4096.png` | Results | Llama throughput-vs-energy + VRAM-vs-cache | v5 historical |

---

## 4. Action list

1. Apply `PARETO_UPDATE_GUIDE.md` first (removes the v5 Pareto figure, swaps in fig08, fixes conclusion).
2. **Swap** the three provisional figures for accepted ones:
   - `fig_hard_quality_wilson.pdf` → `fig03_retrieval_wilson.pdf`
   - `fig_energy_throughput_vs_context.pdf` → `fig02_measured_context_scaling.pdf`
   - `fig_measured_realized_ideal_storage.pdf` → `fig04_storage_realization_gap.pdf`
3. **Add unnumbered figures** to Results: fig01, fig08 (already there), fig_interaction.
4. **Add appendix** for fig05, fig06, fig07 (ideal packed/fused envelope) — cite fingerprint `b19adce0924b4203`, keep claim boundaries: ideal is a mathematical projection, no numerical ideal Joules/VRAM claimed.
5. **Delete** from `paper/figures/`:
   - `v5_final_pareto_uncertainty_4096.pdf` (superseded)
   - `fig_empirical_and_projected_pareto.pdf` (unused + risky)
   - the 3 provisional duplicates after the swap (`fig_hard_quality_wilson.pdf`, `fig_energy_throughput_vs_context.pdf`, `fig_measured_realized_ideal_storage.pdf`)
6. **Optional pruning** (needs a decision, see §5).

---

## 5. Open decisions (ask user)

- **Keep or prune** `v5_final_results.png`, `v5_final_system_tradeoffs_4096.png`, `v5_final_sensitivity_4096.png`:
  - `v5_final_results.png` (Llama-only context) — largely subsumed by fig02; keep as a Llama detail or drop.
  - `v5_final_system_tradeoffs_4096.png` — unique throughput/VRAM view; recommend keep.
  - `v5_final_sensitivity_4096.png` — easy-task ceiling; recommend drop in favor of fig03 + Qwen Table `tab:qwen-sensitivity`.
2. **Swap or keep both families** — recommended: use accepted fig01–fig08; provisional figures removed.

---

## 6. Caption guidance

- Every captured figure must state: evidence status (accepted/provisional), source fingerprint, n, uncertainty definition (Wilson / SD / bootstrap frequency), claim boundary (measured vs realized vs ideal).
- fig01–fig08 reference provisional synthesis fingerprint `b9dee0924...` **only if the figure depends on provisional data**; fig08 currently cites `b19adce0924b4203`.
- Ideal figures (fig05–07) must state "mathematical projection, not measured".

---

## 7. Supporting data (if you build custom figures later)

Provisional bundle CSVs available for reuse:
- `energy_break_even_surface.csv`, `robust_optimality_regions.csv`, `quality_constraint_regions.csv`
- `measured_realized_ideal_storage.csv`, `ideal_packed_kv_tensor_accounting.csv`, `modeled_phase_byte_demand.csv`
- `empirical_pareto.csv` (the 10-row bootstrap Pareto input)
- `within_model_effects.csv`, `cross_model_interaction_summary.csv`

Also already on disk: full `fig01`–`fig08` PNG + PDF copies in `evidence/accepted/CSE407_cross_model_visualization_v1/`.