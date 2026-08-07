# Current A5 Visualization Handoff

## Status

- Accepted Llama and Qwen measurement bundles remain immutable.
- Notebook 09 produced a validated but provisional local synthesis bundle at
  `evidence/provisional/bundles/CSE407_cross_model_synthesis_local_provisional/`.
- Source synthesis fingerprint: `b19adce0924b4203`.
- The connected Colab notebook was rebuilt from scratch as Drive-independent
  Notebook 09B and completed on 2026-08-07.
- Visualization fingerprint: `53ead4e6db45d2a8`.
- Visualization ZIP SHA-256:
  `e718e64193f2b162f674d87d5654935ba1f879fa5064243e4e30c3493ae0eb88`.
- The visualization run generated eight figures in both PNG and PDF and proved
  that the provisional source files were unchanged.

## Portable Execution Contract

Notebook 09B has no Google Drive mount or `MyDrive` dependency. It:

1. Downloads the uploaded project ZIP with `gdown` using file ID
   `1MtCVx8ZkSVVgQ6Q1SNNEOMnrqvh393O4`.
2. Locates the provisional synthesis bundle inside the extracted repository.
3. Validates fingerprint, schema, output manifest, 39 manifest-bound files, 41
   source files, and exact table row counts.
4. Writes only to `/content/CSE407_cross_model_visualization_v1/`.
5. Packages `/content/CSE407_cross_model_visualization_v1.zip` for download.

Colab runtime storage is ephemeral. Preserve both the edited notebook and ZIP
before disconnecting.

## Generated Figures

1. Measured TQ-Ref energy overhead by phase and context.
2. Measured prefill/decode energy and throughput context scaling.
3. Hard-60 Wilson intervals and Qwen common-15 low-bit sensitivity.
4. Matched non-TQ versus realized TQ-Ref versus ideal packed storage.
5. Ideal 2/3/4-bit packed-KV component scaling.
6. Modeled prefill conversion cost and decode byte-demand savings.
7. Parameter-free symbolic ideal-energy break-even boundaries.
8. Measured energy-quality-memory Pareto view.

## Findings Boundary

- TQ-Ref is numerically active but uses uint8 indices, materialized K/V, and
  unfused execution. Its measured overhead is not packed-kernel overhead.
- At 4096 tokens, measured TQ-only total-energy overhead is approximately 44.7%
  for Llama and 30.6% for Qwen relative to the registered energy baselines.
- Under the declared ideal four-bit layout, TQ-only decode persistent KV is
  approximately 28.8% of matched FP16 persistent KV for both model geometries.
- The ideal result concerns persistent KV only, not total peak VRAM.
- Ideal energy remains partially identified:

```text
E_ideal = E_baseline - epsilon_mem * Delta_D + O_net
```

- Numerical ideal energy, latency, throughput, power, and peak VRAM are not
  available without a measured packed/fused kernel or justified parameter
  domains.
- The visualization is derived from provisional synthesis. It does not promote
  fingerprint `b19adce0924b4203` to accepted A5 evidence.

## Reuse For Another Model

Read `research/cross_model_visualization_guide.md`. A new model must first export
the same normalized schemas and its own model geometry, layer budgets, observed
TQ paths, quality populations, and immutable fingerprints. Never reuse Llama or
Qwen storage, energy, or quality rows as another model's projection.

## Next

1. Download and preserve the Colab notebook and visualization ZIP.
2. Select the strongest figures for the paper while retaining provisional labels.
3. Decide whether to independently promote or rerun the A5 synthesis from one
   canonical Notebook 09 source.
4. Complete paper figure placement, final formatting, and the reproducibility
   package.
