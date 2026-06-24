# Energy-Efficient Edge Inference Through Compound Compression
## An Empirical Ablation of Weight Quantization, Token Eviction, and TurboQuant on a Small Language Model

**Model:** Qwen3-4B | **Hardware:** Google Colab Free (T4 16GB) | **Course:** CSE407 Green Computing

---

## Audit of Old Notebook — Critical Bugs Found

### Bug 1: NIAH is Broken for ALL Configs (Not Just C4)

The **new notebook's** live output shows:
```
[Needle Response]: SHAR# 19999999999999999999999999
Needle: NO        ← Even C0 Baseline BF16 fails!
```

The old notebook (`Final output.ipynb`) shows `Needle: YES` for C0/C1. The discrepancy comes from **two different NIAH implementations**:

| | Old Notebook (works) | New Notebook (broken) |
|---|---|---|
| **Needle value** | `"The secret project code name is SHADOW-8821"` — full sentence | Just the code name passed to `create_needle_haystack(needle, ...)` with `f"[IMPORTANT NOTICE: The secret project code name is {needle}]"` — **double-wrapping if needle already contains the sentence** |
| **Prompt construction** | Encodes at token level with `prefix_ids + haystack_ids + needle_ids + suffix_ids` | Joins strings then applies `apply_chat_template()` |
| **Prompt suffix** | `"The secret project code name is"` — forces completion | `"Question: Based on the document above, what is the secret project code name? Answer concisely."` — open-ended |
| **Response** | Model completes `"SHADOW-8821"` directly | Model generates garbage (`SHAR# 199...`) |

**Root cause:** The new notebook uses an open-ended question format that Qwen2.5-1.5B can't handle well. The old notebook uses a completion-style prompt that forces the model to output the code name directly.

### Bug 2: Old Notebook Uses StreamingLLM/SinkCache, NOT SnapKV

The old notebook's token eviction (Step 4) uses **SinkCache** (StreamingLLM-style eviction with 4 attention sinks + sliding window), NOT SnapKV (attention-importance-based eviction). The markdown even says:

> "Uses the Hugging Face SinkCache which implements StreamingLLM with automatic RoPE key re-rotation."

The new notebook has a `Qwen2Attention` monkey-patch that implements SnapKV. **These are two completely different techniques:**

| | SinkCache (old) | SnapKV (new) |
|---|---|---|
| **Strategy** | Keep first 4 tokens + last N tokens (sliding window) | Keep tokens with highest attention scores |
| **Implementation** | `transformers.cache_utils.SinkCache` (clean API) | Monkey-patching `Qwen2Attention.forward` (fragile) |
| **RoPE handling** | ✅ Automatic re-rotation | ❌ Not handled in monkey-patch |

### Bug 3: Missing Configs C2 and C3

The old CSV only has C0, C1, C4. The intermediate configs (AWQ+TurboQuant, AWQ+SnapKV) were never run. Without these, you can't isolate which technique causes what effect — it's not a proper ablation study.

### Bug 4: C4 Fails NIAH Even at 512 Tokens

At 512 tokens with `MAX_CAPACITY=1024`, SnapKV **should not activate** (since `q_len=502 < 1024`). Yet C4 fails NIAH at 512. This means either:
- TurboQuant at 4-bit is corrupting the cache enough to break retrieval on a 1.5B model, OR
- The TurboQuantCache `__init__` monkey-patch has a bug (double-popping kwargs)

### Bug 5: Perplexity Doesn't Measure What We Think

Perplexity is computed via a standard `model(**tok, labels=tok["input_ids"])` call — this uses the **default cache**, NOT TurboQuant/SnapKV. So perplexity is identical for C1 and C4 because it's measuring the AWQ model without any cache optimizations.

---

## New Project Plan — From Scratch on Qwen3-4B

### Target Model
- **BF16 Baseline:** `Qwen/Qwen3-4B` (~8GB)
- **AWQ:** `Qwen/Qwen3-4B-AWQ` (~2.1GB) — confirm existence, fallback to community AWQ

### Architecture Facts (Qwen3-4B)
- 36 layers, 32 Q-heads, 8 KV-heads (GQA), hidden_size=2560
- Attention class: `Qwen3Attention` in `transformers.models.qwen3.modeling_qwen3`
- QK-Norm added (unlike Qwen2), no QKV-bias
- Standard transformer — no hybrid/linear attention

### Configurations (5-way Ablation)

| Config | Weights | Token Eviction | KV Cache Quant | Description |
|---|---|---|---|---|
| **C0** | BF16 | None | FP16 cache | Unoptimized baseline |
| **C1** | AWQ 4-bit | None | FP16 cache | Weight quantization only |
| **C2** | AWQ 4-bit | None | TurboQuant 4-bit | + KV cache compression |
| **C3** | AWQ 4-bit | SnapKV (cap=1024) | FP16 cache | + Token eviction |
| **C4** | AWQ 4-bit | SnapKV (cap=1024) | TurboQuant 4-bit | All three stacked |

### Context Lengths
- **512, 2048, 8192 tokens** (same as before, covers short/medium/long)

### Evaluation Metrics (per config × context length = 15 data points)

| Metric | How Measured |
|---|---|
| **Peak VRAM (MB)** | `torch.cuda.max_memory_allocated()` |
| **Inference Time (s)** | Wall clock for full generate |
| **Tokens/sec** | `max_new_tokens / time` |
| **Perplexity** | Fixed: compute WITH active cache for C2/C4 |
| **NIAH (pass/fail)** | Fixed: completion-style prompt, not open-ended |
| **Avg Power (W)** | `pynvml` background polling at 100ms |
| **Energy (J)** | `avg_power × time` |
| **KV Cache Size (MB)** | Measure actual cache tensor sizes |

---

### Implementation Cells

> [!IMPORTANT]
> We are writing a **completely new notebook from scratch**. No code is reused from the old notebook.

#### Cell 1: Environment Setup
```
pip install turboquant autoawq transformers datasets accelerate
pip install matplotlib seaborn pandas scipy
pip install nvidia-ml-py3 psutil
```

#### Cell 2: Imports & GPU Check
- Import all libraries
- Verify T4 GPU, print VRAM, check TurboQuant version
- NO monkey-patching of TurboQuantCache init (verify if still needed for Qwen3)

#### Cell 3: Helper Functions
- `ExperimentResult` dataclass
- `GPUMonitor` class (background power polling)
- `clear_cache()` utility
- `compute_perplexity()` — **Fixed:** accept optional `past_key_values` to measure with active cache

#### Cell 4: NIAH Test — Fixed Implementation
- `create_needle_haystack()` — Use **completion-style** prompt (not open-ended question)
- Insert needle at 50% depth
- Prompt ends with `"The secret project code name is"` → model completes with the code name
- `check_needle()` — case-insensitive check for `"SHADOW-8821"` in response

#### Cell 5: SnapKV Implementation for Qwen3
- Monkey-patch `Qwen3Attention.forward`
- Key changes from Qwen2 patch:
  - Import from `transformers.models.qwen3.modeling_qwen3`
  - Handle **QK-Norm** (Qwen3 applies LayerNorm to Q and K before attention)
  - Handle **no QKV-bias** (Qwen3 removed bias from Q/K/V projections)
  - Proper `apply_rotary_pos_emb` import from qwen3 module
- Controlled by global `USE_SNAPKV` flag

#### Cell 6: Model Loaders
- `load_bf16_model()` → `Qwen/Qwen3-4B` with `attn_implementation="eager"`
- `load_awq_model()` → `Qwen/Qwen3-4B-AWQ` with `attn_implementation="eager"`

#### Cell 7: Experiment Runner
- For each config:
  1. Load appropriate model
  2. Set `USE_SNAPKV` flag
  3. Create `TurboQuantCache` if needed
  4. Run NIAH test with GPU monitoring
  5. Run perplexity evaluation
  6. Record all metrics
  7. Unload model, clear cache
- Save results to CSV after each config

#### Cell 8: Results Analysis
- Load CSV into DataFrame
- Generate 4 plots:
  1. VRAM vs Context Length (per config)
  2. Energy vs Context Length (per config)
  3. NIAH Accuracy heatmap
  4. Tokens/sec comparison bar chart
- Statistical tests (paired t-test or Wilcoxon for energy savings)

#### Cell 9: Summary Report
- Auto-generated markdown summary with key findings
- Comparison table of all 15 data points
- Research question answers

---

## Verification Plan

### Sanity Checks Before Full Run
1. **NIAH sanity:** Run C0 at 512 tokens → must pass NIAH (if BF16 baseline fails, the test is broken)
2. **SnapKV activation gate:** At 512 tokens with cap=1024, SnapKV must NOT activate → C3@512 should == C1@512
3. **TurboQuant isolation:** C2@512 vs C1@512 — if NIAH fails on C2 but passes on C1, TurboQuant is too aggressive

### Full Run
- Run all 5 configs × 3 context lengths = 15 experiments
- Expect total runtime ~30-45 minutes on T4

### Post-Run Validation
- Verify no `NaN` perplexity values
- Verify energy values are physically reasonable (30-70W range for T4)
- Cross-check: C1 VRAM < C0 VRAM (AWQ reduces weights)
- Cross-check: C3 VRAM < C1 VRAM at 8K (SnapKV caps cache)

---

## Open Questions

> [!IMPORTANT]
> **AWQ Model Availability:** Need to confirm `Qwen/Qwen3-4B-AWQ` exists on HuggingFace. If not, we'll use a community AWQ model or quantize ourselves using `autoawq`.

> [!IMPORTANT]
> **TurboQuant + Qwen3 Compatibility:** Need to verify that `TurboQuantCache` works with Qwen3's GQA (8 KV heads). The `turboquant` pip package was built when Qwen2 was current — may need version check.

> [!WARNING]
> **SnapKV on Qwen3 — QK-Norm Interaction:** Qwen3 applies LayerNorm to Q and K *before* computing attention scores. SnapKV uses attention scores to decide which tokens to evict. The QK-Norm might affect the distribution of attention scores. This needs empirical validation (run C3 and check NIAH).
