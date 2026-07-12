# Port Plan — Qwen3 PyramidKV + TurboQuant for C3/C4

## Goal

Port PyramidKV + TurboQuant to Qwen3-4B so configurations C3 (AWQ + PyramidKV) and C4 (AWQ + PyramidKV + TurboQuant) run correctly on the T4 in `experiments/qwen3_energy_ablation_colab.ipynb`.

---

## Current Status

| Config | Actual Method | Status |
|--------|---------------|--------|
| C0 | Qwen3-4B FP16 + FullKV | Passed pilot and 512-token NIAH |
| C1 | Qwen3-4B-AWQ + FullKV | Passed pilot and 512-token NIAH |
| C2 | Qwen3-4B-AWQ + HQQ 4-bit `QuantizedCache` | Passed pilot and 512-token NIAH |
| C3 | AWQ + PyramidKV | Blocked, did not run |
| C4 | AWQ + PyramidKV + TurboQuant | Blocked, did not run |

**Notes**
- C0 is FP16, not BF16, because the T4 lacks native BF16 support.
- TurboQuant was attempted but rejected because it retained reachable FP16 K/V tensors alongside compressed data, failing the notebook's physical-storage gate.
- The notebook correctly labelled C2 as `HF_HQQ_4BIT_KIVI_INSPIRED`, not TurboQuant.
- Full experiments are zero because all three collection flags (`RUN_FULL_PERFORMANCE`, `RUN_FULL_NIAH`, `RUN_FULL_THINKING`) remain disabled.

---

## Root Causes

### 1. PyramidKV / SnapKV

Official KVCache-Factory pins `transformers==4.44.2` and only patches Llama/Mistral. Qwen3 uses `Qwen3Attention`, which has a different API surface incompatible with existing adapters. Qwen3 requires `transformers>=4.51.0`.

### 2. TurboQuant

The community package (`back2matching/turboquant`) stores compressed data but keeps reachable FP16 K/V tensors alive in the same cache object. The notebook correctly rejects it because live storage never drops below the FP16 FullKV baseline.

---

## Implementation Plan

### Step 1 — PyramidKV Monkey-Patch for Qwen3Attention

Create a forward-patch for `Qwen3Attention.forward` that:

1. Collects attention scores from the final observation window (last 512 tokens)
2. Computes layerwise PyramidKV budgets — 36 layers, geometric distribution averaging 1024 retained tokens per layer
3. Evicts low-importance KV pairs, preserving exactly 8 KV heads (GQA: 32 Q heads, 8 KV heads)
4. Maintains separate logical token position and retained cache length so RoPE positions and causal masks remain correct
5. Falls back to SnapKV-style eviction for layers below the Pyramid threshold

**Constraints:**
- Runs in eager mode (no SDPA flash path) because PyramidKV needs raw attention scores
- After eviction, stores only surviving KV pairs in a standard `DynamicCache`
- Preserves `transformers==5.3.0` — no downgrade

### Step 2 — TurboQuant Cache (Physical-Compressing)

Replace the current community wrapper with a `QuantizedCache` subclass that:

1. Encodes K/V into packed indices + scales at forward time
2. Keeps only the last 64 tokens in FP16 as a residual window (for accurate recent attention)
3. Dequantizes to FP16 only inside the attention call, then discards the FP16 result immediately
4. Never stores persistent FP16 tensors beyond the residual window

**Gate condition:** `sys.getsizeof` on cache buffers must be strictly below FP16 FullKV for the same sequence length at 8192 tokens.

**Target compression:** 4-bit K/V keys, 4-bit V values with per-channel scaling.

### Step 3 — Notebook Integration

1. Register new cache factories for `"pyramidkv"` and `"turboquant_v2"` in `SUPPORTED_CACHE_IMPLS`
2. Update `KV_CACHE_TYPE` mapping:
   - C3 → pyramidkv
   - C4 → pyramidkv + turboquant_v2
3. Keep C2 as HQQ unless TurboQuant v2 proves strictly better

### Step 4 — Validation Pilots

All pilots must pass before full collection:

| Context | C2 (HQQ) | C3 (PyramidKV) | C4 (Compound) |
|---------|----------|----------------|---------------|
| 512 | Storage < FullKV, NIAH retrieval | No pruning < 1024, layer budgets met | Both checks + NIAH |
| 2048 | Storage < FullKV, NIAH retrieval | No pruning < 1024, layer budgets met | Both checks + NIAH |
| 8192 | Storage < FullKV, NIAH retrieval | No pruning < 1024, layer budgets met | Both checks + NIAH |

**Global sanity checks (all configs):**
- Idempotent across 3 restarts
- Atomic CSV writes, no corruption
- Power-trace JSONL files non-empty
- Finite logits (no NaN/Inf)

### Step 5 — Full Experiment Collection

Once all pilots pass:

1. Set `RUN_FULL_PERFORMANCE = True`, `RUN_FULL_NIAH = True`, `RUN_FULL_THINKING = True`
2. Execute C0–C4 × 3 context lengths (512, 2048, 8192) × 3 seeds = 36 runs
3. Verify all CSV rows and JSONL traces written to Google Drive
4. Run statistical analysis: Friedman / Wilcoxon / McNemar + Pareto frontier (energy vs NIAH)

---

## Files to Modify

- `experiments/qwen3_energy_ablation_colab.ipynb` — new cache implementations, updated KV mapping, pilot checks
- No new files — everything lives in notebook cells

---

## Non-Goals

- Full KVCache-Factory integration (notebook patches Qwen3 directly)
- FP8 or INT8 quantization (T4 has no native FP8)
- Multi-GPU (notebook assumes single T4)
- BF16 (T4 lacks native BF16; FP16 is the real baseline)

---

## Fallback Plan

If the Qwen3 attention patch proves impossible (e.g., custom CUDA kernels required for KV eviction), revert to C0/C1/C2-only experiment and clearly acknowledge the gap in the final paper.
