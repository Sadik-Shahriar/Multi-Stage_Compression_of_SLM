# Cross-Model Visualization Findings

## Provenance

- Source: provisional synthesis bundle, fingerprint `b19adce0924b4203`.
- Acquisition: public ZIP via `gdown`; no Google Drive mount.
- This visualization does not promote provisional synthesis to accepted evidence.

## Measured TQ-Ref

- At 4096 tokens, measured TQ-only total-energy overhead was 44.7% for Llama and 30.8% for Qwen relative to their registered energy baselines.
- These values describe the numerically active, materialized-K/V, uint8-indexed, unfused TQ-Ref path. They are not packed-kernel overhead estimates.
- The Llama stock-C1 TQ-only comparison remains wrapper-confounded; Qwen uses matched Q1-W.

## Ideal Packed/Fused Envelope

- Llama four-bit decode persistent storage: 455.0 MiB matched non-TQ, 696.5 MiB realized TQ-Ref, and 131.1 MiB ideal packed.
- Qwen four-bit decode persistent storage: 146.2 MiB matched non-TQ, 223.9 MiB realized TQ-Ref, and 42.2 MiB ideal packed.
- The ideal four-bit TQ-only envelope is about 28.8% of matched FP16 persistent KV for both geometries under the declared residual/norm layout.
- This supports a persistent-memory advantage, not a measured total-VRAM, latency, energy, throughput, or power advantage.

## Conditional Energy

- Ideal energy remains `E_ideal = E_baseline - epsilon_mem * Delta_D + O_net`.
- Prefill conversion adds modeled logical demand, while the fixed 64-token decode avoids substantially more demand under fused reconstruction.
- Numerical ideal joules are intentionally absent because `epsilon_mem` and `O_net` have no justified measured domains.

## Reuse

- Reuse the plotting structure with explicit per-model variant maps, immutable input fingerprints, separate quality populations, and evidence-tier styling.
- For a new model, regenerate the normalized synthesis tables first; do not relabel another model's ideal storage or quality path.
