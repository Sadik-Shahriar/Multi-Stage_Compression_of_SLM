# Ideal-TQ Realization-Gap Summary

The measured TQ-Ref path is numerically active, uses one uint8 index per coordinate at nominal 2/3/4 bits, retains materialized K/V, and is unfused. It is not a simulation and not a physically packed cache.

The analytical ideal removes persistent materialized K/V, packs indices at the observed nominal bit width, retains FP32 norms and a 128-token FP16 residual, and assumes reconstruction remains in registers/shared memory. Tensor descriptors are reconstructed from runtime-asserted contracts and reconciled to persisted aggregate bytes; no direct live tensor dump was preserved.

Unit gates reproduced retained FP16 bytes and eight-bit package payloads exactly before projection. Bit-width and budget monotonicity passed. Persistent-memory dominance is proved only where index savings exceed norm, residual, alignment, and metadata overhead.

Prefill and decode modeled byte demand are separate. The model is logical compulsory algorithmic demand, not exact hardware DRAM traffic. Total break-even uses both phases. Because no justified finite domains exist for `epsilon_mem` or `O_net`, break-even remains symbolic and robust bootstrap-frequency bounds remain unavailable. This fail-closed result prevents fabricated ideal joules.

Quality transfers only under strict output equivalence. Four-bit TQ-only and compound hard paths are eligible; Qwen low-bit TQ-only comparisons use the common 15 scenarios; Llama historical low-bit quality and all unobserved low-bit compounds are excluded from hard-quality energy Pareto claims.
