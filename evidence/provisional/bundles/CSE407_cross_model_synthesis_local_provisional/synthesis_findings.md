# Cross-Model Synthesis Findings

## Evidence boundary

- All accepted source manifests, identities, row counts, CSV correspondences, and 195 traces passed before analysis.
- Raw joules are primary. The 82 W and 70 W values are clipped-trace sensitivity integrations, not hardware reruns.
- Llama systems effects use historical stock C1; Qwen uses matched-wrapper Q1-W. Llama's C1-W control is a separate-session 4096-only descriptive comparison.
- Each model uses the same semantic scenarios but tokenizer-specific exact 4096-token materialization. Architecture alone is not identified as the cause of cross-model differences.

## Empirical results

- Llama hard retrieval: C1-W 38/60, C2 37/60, C3-Ref 37/60, C4-Ref 37/60.
- Qwen hard retrieval: Q1-W 48/60, Q2 1/60, Q3-Ref 49/60, Q4-Ref 1/60.
- Qwen eviction collapsed hard retrieval while Q3-Ref retained Q1-W-like retrieval at substantially higher measured energy. The Llama hard run did not show the same eviction collapse.
- Sequential compound interactions and rankings retained their registered raw/capped interpretation. Five blocks limit Wilcoxon resolution.

## Provenance caveat

Notebook 08 required an in-session quality-validator correction and capped-analysis merge correction. The exported notebook preserves both fixes and persisted artifacts are hash-consistent, but fingerprint `861d89617e53034d` and its artifact manifest do not cryptographically bind repair-cell source bytes. This is a reproducibility caveat, not a measurement-integrity failure.

## Ideal realization gap

- FP retained-byte and uint8 logical-payload calibration gates passed for both models and TQ-only/compound paths.
- Under the declared perfectly packed persistent layout, all projected 2/3/4-bit rows are smaller than matched FP16 persistent KV because packed-index savings exceed norms, residuals, alignment, and metadata.
- This proves only conditional persistent-KV memory dominance under the declared representation. It does not prove total peak-VRAM, latency, hardware traffic, energy, or power improvement.
- Ideal energy is only identified by `E_ideal = E_baseline - epsilon_mem * Delta_D + O_net`. No numerical parameter domain was justified, so no numerical ideal-energy or projected energy-Pareto point was produced.
- Conservative, point, and possible quality rules are exported separately across the complete threshold partition. Unobserved 2/3-bit compound rows remain storage-only.
