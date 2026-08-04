import json
from pathlib import Path


def lines(text):
    return text.strip("\n").splitlines(keepends=True)


def markdown(cell_id, text):
    return {"cell_type": "markdown", "id": cell_id, "metadata": {}, "source": lines(text)}


def code(cell_id, text):
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": cell_id,
        "metadata": {},
        "outputs": [],
        "source": lines(text),
    }


cells = [
    markdown(
        "title",
        r'''
# Llama 3.2-3B Compound Compression Energy Ablation - v5

**CSE407 Green Computing | Google Colab free-tier T4 | 10 Hz NVML monitoring**

| Config | Weights | Eviction | KV quantization |
|---|---|---|---|
| C0 | FP16 | None | None |
| C1 | AWQ 4-bit | None | None |
| C2 | AWQ 4-bit | PyramidKV | None |
| C3 | AWQ 4-bit | None | TurboQuant 4-bit codebook |
| C4 | AWQ 4-bit | PyramidKV | TurboQuant 4-bit codebook |

Contexts are **1024, 2048, and 4096**. The 8192 condition is excluded because it
previously exceeded the free-tier T4 memory limit.

### Correctness boundary

- One minimal `LlamaAttention.forward` wrapper is used only by C2 and C4.
- Prefill attends to full K/V, then PyramidKV selects K/V per KV head.
- C4 sends only selected K/V through `TurboQuantCache.update`; evicted tokens never
  enter TurboQuant's internal state.
- TurboQuant is the independent PyPI reference implementation, not a fused INT4
  attention kernel. Version 0.2.0 uses a 16-level codebook but uint8 indices and
  retained dequantized working tensors. Runtime VRAM therefore does not represent
  packed 4-bit storage; the experiment measures numerical quantization and overhead.
- Energy uses a fixed 64-token teacher-forced decode trace. NIAH quality is measured
  separately with natural greedy generation.
''',
    ),
    markdown("install_md", "## 1. Install\n\nRun once, restart the Colab session, then continue."),
    code(
        "install",
        r'''
%pip install -q "autoawq==0.2.9" "gptqmodel==7.1.0" "turboquant==0.2.0"
%pip install -q "transformers==5.12.1" accelerate nvidia-ml-py pandas matplotlib scipy
print("Restart the Colab session: Runtime -> Restart session")
''',
    ),
    markdown("setup_md", "## 2. Imports, paths, and configuration"),
    code(
        "setup",
        r'''
import gc, hashlib, importlib.metadata, json, os, random, threading, time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import torch
import torch.nn.functional as F

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import pynvml
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache, set_seed
from transformers.models.llama.modeling_llama import (
    LlamaAttention, apply_rotary_pos_emb, eager_attention_forward, repeat_kv,
)
from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS
from turboquant import TurboQuantCache

SEED = 407
MODEL_FP16 = "unsloth/Llama-3.2-3B-Instruct"
MODEL_AWQ = "casperhansen/llama-3.2-3b-instruct-awq"
CONTEXTS = [1024, 2048, 4096]
DEPTHS = [0.1, 0.5, 0.9]
QUALITY_SEEDS = range(5)
MEASURED_BLOCKS = 5
FIXED_DECODE_TOKENS = 64
QUALITY_MAX_NEW = 32

# Drive persistence is recommended for free-tier session disconnects.
USE_DRIVE = True
if USE_DRIVE:
    from google.colab import drive
    drive.mount("/content/drive")
    SAVE_DIR = Path("/content/drive/MyDrive/CSE407_llama_v5")
else:
    SAVE_DIR = Path("/content/CSE407_llama_v5")
SAVE_DIR.mkdir(parents=True, exist_ok=True)
ENERGY_CSV = SAVE_DIR / "v5_energy_results.csv"
QUALITY_CSV = SAVE_DIR / "v5_quality_results.csv"
VALIDATION_JSON = SAVE_DIR / "v5_validation.json"

set_seed(SEED)
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
assert torch.cuda.is_available(), "A CUDA GPU is required."

pynvml.nvmlInit()
NVML_HANDLE = pynvml.nvmlDeviceGetHandleByIndex(0)
GPU = torch.cuda.get_device_properties(0)

def package_version(name):
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"

ENVIRONMENT = {
    "gpu": GPU.name,
    "vram_gb": round(GPU.total_memory / 2**30, 2),
    "torch": torch.__version__,
    "transformers": transformers.__version__,
    "turboquant": package_version("turboquant"),
    "gptqmodel": package_version("gptqmodel"),
    "contexts": CONTEXTS,
    "fixed_decode_tokens": FIXED_DECODE_TOKENS,
    "seed": SEED,
}
assert ENVIRONMENT["transformers"] == "5.12.1"
assert ENVIRONMENT["turboquant"] == "0.2.0"
assert ENVIRONMENT["gptqmodel"] == "7.1.0"
(SAVE_DIR / "v5_environment.json").write_text(json.dumps(ENVIRONMENT, indent=2))
print(json.dumps(ENVIRONMENT, indent=2))
''',
    ),
    markdown("monitor_md", "## 3. Power monitor and small helpers"),
    code(
        "monitor",
        r'''
class GPUMonitor:
    # Samples at 10 Hz and explicitly captures both integration endpoints.
    def __init__(self, interval_s=0.1):
        self.interval_s = interval_s
        self.samples = []
        self.running = False

    def sample(self):
        mem = pynvml.nvmlDeviceGetMemoryInfo(NVML_HANDLE)
        self.samples.append((
            time.perf_counter() - self.t0,
            pynvml.nvmlDeviceGetPowerUsage(NVML_HANDLE) / 1000.0,
            mem.used / 2**20,
        ))

    def poll(self):
        deadline = self.t0
        while self.running:
            try:
                self.sample()
            except pynvml.NVMLError:
                pass
            deadline += self.interval_s
            time.sleep(max(0.0, deadline - time.perf_counter()))

    def start(self):
        torch.cuda.synchronize()
        self.samples = []
        self.t0 = time.perf_counter()
        self.running = True
        self.sample()
        self.thread = threading.Thread(target=self.poll, daemon=True)
        self.thread.start()

    def stop(self):
        torch.cuda.synchronize()
        try:
            self.sample()
        except pynvml.NVMLError:
            pass
        self.running = False
        self.thread.join(timeout=2)
        if len(self.samples) < 2:
            raise RuntimeError(f"Only {len(self.samples)} power samples were captured.")
        t = np.array([x[0] for x in self.samples])
        p = np.array([x[1] for x in self.samples])
        return {
            "energy_j": float(np.trapezoid(p, t)),
            "avg_power_w": float(np.trapezoid(p, t) / max(t[-1] - t[0], 1e-9)),
            "max_power_w": float(p.max()),
            "nvml_peak_mb": float(max(x[2] for x in self.samples)),
            "n_samples": len(self.samples),
        }

def clear_gpu():
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize()

def append_row(path, row):
    frame = pd.DataFrame([row])
    frame.to_csv(path, mode="a", header=not path.exists(), index=False)

def completed_keys(path, columns, fingerprint):
    if not path.exists():
        return set()
    old = pd.read_csv(path)
    if "fingerprint" not in old or not (old["fingerprint"] == fingerprint).all():
        raise RuntimeError(f"{path} belongs to a different experiment. Move or delete it.")
    return set(map(tuple, old[columns].itertuples(index=False, name=None)))

print("Monitor and helpers ready.")
''',
    ),
    markdown("data_md", "## 4. Exact-length prompts and fixed decode trace"),
    code(
        "data",
        r'''
tokenizer = AutoTokenizer.from_pretrained(MODEL_FP16, trust_remote_code=True)
if tokenizer.pad_token_id is None:
    tokenizer.pad_token_id = tokenizer.eos_token_id

FILLERS = [
    "Computing systems balance latency, memory, power, and reliability. ",
    "Engineers measure workloads carefully before selecting an optimization. ",
    "Long documents contain many details that may or may not affect an answer. ",
    "Energy efficiency depends on both hardware behavior and software design. ",
]

def make_niah_input(ctx_len, depth, seed):
    rng = random.Random(SEED + 1000 * seed + ctx_len)
    systems = rng.sample(["ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO"], 4)
    codes = [f"{rng.choice('ABCDEFGH')}{rng.randrange(100, 999)}-{rng.choice('KLMNPQ')}{rng.randrange(10, 99)}" for _ in systems]
    target = rng.randrange(len(systems))
    records = [f"System {name} uses activation code {code}." for name, code in zip(systems, codes)]
    needle = "\n" + " ".join(records) + "\n"
    answer = codes[target].lower()

    messages = [
        {"role": "system", "content": "Return only the exact requested activation code."},
        {"role": "user", "content": (
            f"Read the document and report the activation code for System {systems[target]}.\n\n"
            "<DOC>\n{HAYSTACK}\n</DOC>\n\nActivation code:"
        )},
    ]
    template = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    prefix_text, suffix_text = template.split("{HAYSTACK}")
    prefix = tokenizer.encode(prefix_text, add_special_tokens=False)
    suffix = tokenizer.encode(suffix_text, add_special_tokens=False)
    needle_ids = tokenizer.encode(needle, add_special_tokens=False)
    filler_ids = tokenizer.encode("".join(rng.sample(FILLERS, len(FILLERS))), add_special_tokens=False)

    filler_budget = ctx_len - len(prefix) - len(suffix) - len(needle_ids)
    assert filler_budget > 32
    before = int(filler_budget * depth)
    after = filler_budget - before
    before_ids = (filler_ids * (before // len(filler_ids) + 1))[:before]
    after_ids = (filler_ids * (after // len(filler_ids) + 1))[:after]
    ids = prefix + before_ids + needle_ids + after_ids + suffix
    assert len(ids) == ctx_len
    return torch.tensor([ids], dtype=torch.long), answer

TRACE_TEXT = (
    "A controlled decode trace keeps the generated workload identical across every "
    "compression configuration. This prevents early end tokens from changing the amount "
    "of measured work and supports a fair energy comparison. "
) * 4
TRACE_IDS = tokenizer.encode(TRACE_TEXT, add_special_tokens=False)[:FIXED_DECODE_TOKENS]
assert len(TRACE_IDS) == FIXED_DECODE_TOKENS

for ctx in CONTEXTS:
    for depth in DEPTHS:
        ids, _ = make_niah_input(ctx, depth, seed=0)
        assert ids.shape[1] == ctx
print("Prompt lengths and fixed decode trace verified.")
''',
    ),
    markdown("loaders_md", "## 5. Model loaders"),
    code(
        "loaders",
        r'''
def load_fp16():
    clear_gpu()
    return AutoModelForCausalLM.from_pretrained(
        MODEL_FP16, dtype=torch.float16, device_map={"": 0},
        attn_implementation="sdpa", trust_remote_code=True,
    ).eval()

def load_awq():
    clear_gpu()
    return AutoModelForCausalLM.from_pretrained(
        MODEL_AWQ, device_map={"": 0},
        attn_implementation="sdpa", trust_remote_code=True,
    ).eval()

def new_cache(use_tq):
    return TurboQuantCache(bits=4) if use_tq else DynamicCache()

print("Model loaders ready.")
''',
    ),
    markdown(
        "pyramid_md",
        "## 6. Minimal PyramidKV attention wrapper\n\n"
        "This is the only patched function. Prefill attention uses full K/V, then selected "
        "K/V are inserted into DynamicCache or TurboQuantCache.",
    ),
    code(
        "pyramid",
        r'''
WINDOW = 32
POOL_KERNEL = 5
PYRAMID_AVERAGE = 1024
PYRAMID_BETA = 20
PKV_LOG = []
_BUDGET_OVERRIDE = None
_ORIGINAL_LLAMA_FORWARD = LlamaAttention.forward

def build_pyramid_budgets(layers=28, average=1024, window=32, beta=20):
    old_average = average - window
    last = round(old_average / beta)
    first = 2 * old_average - last
    old = np.linspace(first, last, layers).round().astype(int)
    return (old + window).tolist()

PYRAMID_BUDGETS = build_pyramid_budgets()

def layer_budget(layer_idx):
    return _BUDGET_OVERRIDE[layer_idx] if _BUDGET_OVERRIDE is not None else PYRAMID_BUDGETS[layer_idx]

def select_pyramid_kv(query_states, key_states, value_states, layer_idx, groups, scaling):
    cache_len = key_states.shape[-2]
    budget = min(layer_budget(layer_idx), cache_len)
    if cache_len <= budget:
        return key_states, value_states

    obs = min(WINDOW, cache_len)
    old_len = cache_len - obs
    old_keep = max(budget - obs, 0)
    if old_keep >= old_len:
        return key_states, value_states

    recent_q = query_states[:, :, -obs:, :]
    repeated_k = repeat_kv(key_states, groups) if groups > 1 else key_states
    scores = torch.matmul(recent_q, repeated_k.transpose(2, 3)) * scaling

    causal = torch.triu(torch.full(
        (obs, obs), float("-inf"), device=scores.device, dtype=scores.dtype,
    ), diagonal=1)
    scores[:, :, :, -obs:] += causal[None, None, :, :]
    probs = F.softmax(scores, dim=-1, dtype=torch.float32)

    # Reduce 24 query heads to 8 KV heads, then score old tokens per KV head.
    prefix_scores = probs[:, :, :, :old_len].sum(dim=-2)
    prefix_scores = prefix_scores.reshape(
        prefix_scores.shape[0], key_states.shape[1], groups, old_len,
    ).mean(dim=2)
    prefix_scores = F.avg_pool1d(
        prefix_scores, kernel_size=POOL_KERNEL, stride=1, padding=POOL_KERNEL // 2,
    )

    topk = prefix_scores.topk(old_keep, dim=-1).indices.sort(dim=-1).values
    gather_idx = topk.unsqueeze(-1).expand(-1, -1, -1, key_states.shape[-1])
    kept_k = key_states[:, :, :old_len, :].gather(2, gather_idx)
    kept_v = value_states[:, :, :old_len, :].gather(2, gather_idx)
    selected_k = torch.cat([kept_k, key_states[:, :, -obs:, :]], dim=2).contiguous()
    selected_v = torch.cat([kept_v, value_states[:, :, -obs:, :]], dim=2).contiguous()

    PKV_LOG.append({
        "layer": int(layer_idx), "before": int(cache_len),
        "after": int(selected_k.shape[-2]), "budget": int(budget),
        "head_selection_differs": bool((topk[:, 1:] != topk[:, :-1]).any().item()),
    })
    return selected_k, selected_v

def pyramid_forward(
    self, hidden_states, position_embeddings=None, attention_mask=None,
    past_key_values=None, **kwargs,
):
    input_shape = hidden_states.shape[:-1]
    hidden_shape = (*input_shape, -1, self.head_dim)
    q = self.q_proj(hidden_states).view(hidden_shape).transpose(1, 2)
    k = self.k_proj(hidden_states).view(hidden_shape).transpose(1, 2)
    v = self.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)
    cos, sin = position_embeddings
    q, k = apply_rotary_pos_emb(q, k, cos, sin)
    q_len = q.shape[-2]

    # Decode updates before attention. Prefill intentionally does not: full K/V
    # must be used for the current prompt before selected K/V are stored.
    if past_key_values is not None and q_len < WINDOW:
        k, v = past_key_values.update(k, v, self.layer_idx)

    attention_interface = ALL_ATTENTION_FUNCTIONS.get_interface(
        self.config._attn_implementation, eager_attention_forward,
    )
    attn_output, attn_weights = attention_interface(
        self, q, k, v, attention_mask,
        dropout=0.0, scaling=self.scaling, **kwargs,
    )

    if past_key_values is not None and q_len >= WINDOW:
        stored_k, stored_v = select_pyramid_kv(
            q, k, v, self.layer_idx, self.num_key_value_groups, self.scaling,
        )
        past_key_values.update(stored_k, stored_v, self.layer_idx)

    attn_output = attn_output.reshape(*input_shape, -1).contiguous()
    return self.o_proj(attn_output), attn_weights

def enable_pyramid():
    PKV_LOG.clear()
    LlamaAttention.forward = pyramid_forward

def disable_pyramid():
    LlamaAttention.forward = _ORIGINAL_LLAMA_FORWARD

print("Pyramid budgets:", PYRAMID_BUDGETS)
print("Average:", np.mean(PYRAMID_BUDGETS))

FINGERPRINT_DATA = {
    **ENVIRONMENT,
    "model_fp16": MODEL_FP16,
    "model_awq": MODEL_AWQ,
    "depths": DEPTHS,
    "quality_seeds": list(QUALITY_SEEDS),
    "measured_blocks": MEASURED_BLOCKS,
    "quality_max_new": QUALITY_MAX_NEW,
    "window": WINDOW,
    "pool_kernel": POOL_KERNEL,
    "pyramid_budgets": PYRAMID_BUDGETS,
    "trace_ids": TRACE_IDS,
}
EXPERIMENT_FINGERPRINT = hashlib.sha256(
    json.dumps(FINGERPRINT_DATA, sort_keys=True).encode()
).hexdigest()[:16]
print("Experiment fingerprint:", EXPERIMENT_FINGERPRINT)
''',
    ),
    markdown("runners_md", "## 7. Energy and quality runners"),
    code(
        "runners",
        r'''
CONFIGS = {
    "C0": (False, False),
    "C1": (False, False),
    "C2": (True, False),
    "C3": (False, True),
    "C4": (True, True),
}

def cache_lengths(cache):
    lengths = []
    for layer in cache.layers:
        if hasattr(layer, "_total_len"):
            lengths.append(int(layer._total_len))
        else:
            lengths.append(int(layer.get_seq_length()))
    return lengths

def tq_payload_elements(cache):
    total = 0
    for layer in cache.layers:
        for name in ["_key_indices", "_value_indices"]:
            tensor = getattr(layer, name, None)
            if tensor is not None:
                total += tensor.numel()
    return total

def run_energy(model, config, ctx, block, warmup=False):
    use_pkv, use_tq = CONFIGS[config]
    ids, _ = make_niah_input(ctx, depth=0.5, seed=99)
    ids = ids.to(model.device)
    cache = new_cache(use_tq)
    prefill_monitor = decode_monitor = None
    if use_pkv:
        enable_pyramid()

    try:
        clear_gpu()
        torch.cuda.reset_peak_memory_stats()
        prefill_monitor = GPUMonitor()
        prefill_monitor.start()
        t0 = time.perf_counter()
        with torch.inference_mode():
            out = model(
                input_ids=ids, past_key_values=cache, use_cache=True,
                logits_to_keep=1,
            )
        torch.cuda.synchronize()
        prefill_s = time.perf_counter() - t0
        prefill_power = prefill_monitor.stop()

        before_decode = cache_lengths(cache)
        decode_monitor = GPUMonitor()
        decode_monitor.start()
        t0 = time.perf_counter()
        with torch.inference_mode():
            for step, token_id in enumerate(TRACE_IDS):
                token = torch.tensor([[token_id]], device=model.device)
                position = torch.tensor([[ctx + step]], device=model.device)
                out = model(
                    input_ids=token, position_ids=position,
                    past_key_values=cache, use_cache=True, logits_to_keep=1,
                )
        torch.cuda.synchronize()
        decode_s = time.perf_counter() - t0
        decode_power = decode_monitor.stop()
        after_decode = cache_lengths(cache)

        row = {
            "fingerprint": EXPERIMENT_FINGERPRINT,
            "config": config, "context": ctx, "block": block, "warmup": warmup,
            "prefill_s": prefill_s, "decode_s": decode_s,
            "prefill_energy_j": prefill_power["energy_j"],
            "decode_energy_j": decode_power["energy_j"],
            "total_energy_j": prefill_power["energy_j"] + decode_power["energy_j"],
            "decode_tok_s": FIXED_DECODE_TOKENS / decode_s,
            "avg_power_w": decode_power["avg_power_w"],
            "max_power_w": max(prefill_power["max_power_w"], decode_power["max_power_w"]),
            "vram_peak_mb": torch.cuda.max_memory_allocated() / 2**20,
            "nvml_peak_mb": max(prefill_power["nvml_peak_mb"], decode_power["nvml_peak_mb"]),
            "power_samples": prefill_power["n_samples"] + decode_power["n_samples"],
            "cache_min_prefill": min(before_decode), "cache_max_prefill": max(before_decode),
            "cache_min_after": min(after_decode), "cache_max_after": max(after_decode),
            "tq_index_elements": tq_payload_elements(cache),
            "evicted_layers": len(PKV_LOG) if use_pkv else 0,
        }
        return row
    finally:
        for monitor in [prefill_monitor, decode_monitor]:
            if monitor is not None and monitor.running:
                try:
                    monitor.stop()
                except Exception:
                    monitor.running = False
        if use_pkv:
            disable_pyramid()
        del cache, ids
        clear_gpu()

def run_quality(model, config, ctx, depth, seed):
    use_pkv, use_tq = CONFIGS[config]
    ids, answer = make_niah_input(ctx, depth, seed)
    ids = ids.to(model.device)
    cache = new_cache(use_tq)
    if use_pkv:
        enable_pyramid()
    generated = []

    try:
        with torch.inference_mode():
            out = model(input_ids=ids, past_key_values=cache, use_cache=True, logits_to_keep=1)
            next_token = out.logits[:, -1, :].argmax(-1, keepdim=True)
            for step in range(QUALITY_MAX_NEW):
                generated.append(next_token)
                if next_token.item() in np.atleast_1d(tokenizer.eos_token_id):
                    break
                if step == QUALITY_MAX_NEW - 1:
                    break
                position = torch.tensor([[ctx + step]], device=model.device)
                out = model(
                    input_ids=next_token, position_ids=position,
                    past_key_values=cache, use_cache=True, logits_to_keep=1,
                )
                next_token = out.logits[:, -1, :].argmax(-1, keepdim=True)
        output_ids = torch.cat(generated, dim=1)[0].tolist()
        response = tokenizer.decode(output_ids, skip_special_tokens=True)
        return {
            "fingerprint": EXPERIMENT_FINGERPRINT,
            "config": config, "context": ctx, "depth": depth, "seed": seed,
            "answer": answer,
            "correct": response.strip().lower().strip("`'\" .") == answer,
            "output_tokens": len(output_ids), "response": response[:160],
        }
    finally:
        if use_pkv:
            disable_pyramid()
        del cache, ids
        clear_gpu()

print("Experiment runners ready.")
''',
    ),
    markdown("validation_md", "## 8. Mandatory validation gates\n\nRun this before either experiment matrix."),
    code(
        "validation",
        r'''
model = load_awq()
cache = ids = out = token = None
validation = {"passed": False}
VALIDATION_JSON.unlink(missing_ok=True)
try:
    raw_quant = model.config.quantization_config
    quant = raw_quant.to_dict() if hasattr(raw_quant, "to_dict") else dict(raw_quant)
    assert quant["quant_method"] == "awq"
    assert quant["bits"] == 4 and quant["group_size"] == 128

    # C4 prefill must put only selected tokens into TurboQuant internals.
    ctx = 2048
    ids, _ = make_niah_input(ctx, 0.5, seed=123)
    ids = ids.to(model.device)
    cache = TurboQuantCache(bits=4)
    enable_pyramid()
    with torch.inference_mode():
        out = model(input_ids=ids, past_key_values=cache, use_cache=True, logits_to_keep=1)
    disable_pyramid()

    lengths = cache_lengths(cache)
    expected = [min(ctx, budget) for budget in PYRAMID_BUDGETS]
    assert lengths == expected, (lengths, expected)
    assert len(PKV_LOG) == sum(ctx > b for b in PYRAMID_BUDGETS)
    assert any(row["head_selection_differs"] for row in PKV_LOG)
    assert tq_payload_elements(cache) > 0
    prefill_log = PKV_LOG.copy()

    before = lengths.copy()
    enable_pyramid()
    with torch.inference_mode():
        token = out.logits[:, -1, :].argmax(-1, keepdim=True)
        position = torch.tensor([[ctx]], device=model.device)
        model(
            input_ids=token, position_ids=position,
            past_key_values=cache, use_cache=True, logits_to_keep=1,
        )
    disable_pyramid()
    after = cache_lengths(cache)
    assert after == [x + 1 for x in before]
    assert max(after) < ctx + 1  # Full prompt must not reappear in C4.

    validation = {
        "passed": True,
        "fingerprint": EXPERIMENT_FINGERPRINT,
        "awq": quant,
        "pyramid_budgets": PYRAMID_BUDGETS,
        "c4_prefill_lengths": lengths,
        "c4_after_one_decode": after,
        "evicted_layers": len(prefill_log),
        "different_head_selection_seen": any(x["head_selection_differs"] for x in prefill_log),
        "turboquant_index_elements": tq_payload_elements(cache),
        "note": (
            "TurboQuant 0.2.0 applies a 16-level codebook but stores uint8 indices "
            "and retains dequantized working tensors. This is numerical quantization, "
            "not packed 4-bit physical storage."
        ),
    }
    VALIDATION_JSON.write_text(json.dumps(validation, indent=2))
    print(json.dumps(validation, indent=2))
finally:
    disable_pyramid()
    del model, cache, ids, out, token
    clear_gpu()

assert validation["passed"], "Do not run experiments until all gates pass."
''',
    ),
    markdown(
        "energy_run_md",
        "## 9. Energy matrix\n\n"
        "Runs 90 executions per fresh session: 15 unrecorded warmups and 75 measured "
        "runs. Results append after every measured run.",
    ),
    code(
        "energy_run",
        r'''
validation = json.loads(VALIDATION_JSON.read_text()) if VALIDATION_JSON.exists() else {}
assert validation.get("passed") and validation.get("fingerprint") == EXPERIMENT_FINGERPRINT
done = completed_keys(
    ENERGY_CSV, ["config", "context", "block"], EXPERIMENT_FINGERPRINT,
)

# C0 is separate because repeatedly swapping FP16 and AWQ models wastes Colab time.
model = load_fp16()
for ctx in CONTEXTS:
    run_energy(model, "C0", ctx, block=-1, warmup=True)
    for block in range(MEASURED_BLOCKS):
        key = ("C0", ctx, block)
        if key in done:
            continue
        row = run_energy(model, "C0", ctx, block, warmup=False)
        append_row(ENERGY_CSV, row)
        print("energy", key, round(row["total_energy_j"], 1), "J")
del model
clear_gpu()

model = load_awq()
for ctx in CONTEXTS:
    for config in ["C1", "C2", "C3", "C4"]:
        run_energy(model, config, ctx, block=-1, warmup=True)
    for block in range(MEASURED_BLOCKS):
        order = list(
            np.random.default_rng(SEED + ctx + block).permutation(["C1", "C2", "C3", "C4"])
        )
        for config in order:
            key = (config, ctx, block)
            if key in done:
                continue
            row = run_energy(model, config, ctx, block, warmup=False)
            append_row(ENERGY_CSV, row)
            print("energy", key, round(row["total_energy_j"], 1), "J")
del model
clear_gpu()
print("Saved:", ENERGY_CSV)
''',
    ),
    markdown(
        "quality_run_md",
        "## 10. Quality matrix\n\n"
        "Runs 225 unique NIAH cases without power monitoring or PPL.",
    ),
    code(
        "quality_run",
        r'''
validation = json.loads(VALIDATION_JSON.read_text()) if VALIDATION_JSON.exists() else {}
assert validation.get("passed") and validation.get("fingerprint") == EXPERIMENT_FINGERPRINT
done = completed_keys(
    QUALITY_CSV, ["config", "context", "depth", "seed"], EXPERIMENT_FINGERPRINT,
)

model = load_fp16()
for ctx in CONTEXTS:
    for depth in DEPTHS:
        for seed in QUALITY_SEEDS:
            key = ("C0", ctx, depth, seed)
            if key not in done:
                row = run_quality(model, "C0", ctx, depth, seed)
                append_row(QUALITY_CSV, row)
                print("quality", key, "OK" if row["correct"] else "FAIL")
del model
clear_gpu()

model = load_awq()
for ctx in CONTEXTS:
    for depth in DEPTHS:
        for seed in QUALITY_SEEDS:
            for config in ["C1", "C2", "C3", "C4"]:
                key = (config, ctx, depth, seed)
                if key not in done:
                    row = run_quality(model, config, ctx, depth, seed)
                    append_row(QUALITY_CSV, row)
                    print("quality", key, "OK" if row["correct"] else "FAIL")
del model
clear_gpu()
print("Saved:", QUALITY_CSV)
''',
    ),
    markdown("analysis_md", "## 11. Compact analysis"),
    code(
        "analysis",
        r'''
energy = pd.read_csv(ENERGY_CSV)
energy = energy[~energy["warmup"].astype(bool)].copy()
quality = pd.read_csv(QUALITY_CSV)

assert set(energy.fingerprint) == {EXPERIMENT_FINGERPRINT}
assert set(quality.fingerprint) == {EXPERIMENT_FINGERPRINT}
assert not energy.duplicated(["config", "context", "block"]).any()
assert not quality.duplicated(["config", "context", "depth", "seed"]).any()
assert len(energy) == 5 * len(CONTEXTS) * MEASURED_BLOCKS, len(energy)
assert len(quality) == 5 * len(CONTEXTS) * len(DEPTHS) * len(list(QUALITY_SEEDS)), len(quality)
assert (energy.groupby(["config", "context"]).size() == MEASURED_BLOCKS).all()

summary = energy.groupby(["config", "context"]).agg(
    total_energy_j=("total_energy_j", "mean"),
    prefill_energy_j=("prefill_energy_j", "mean"),
    decode_energy_j=("decode_energy_j", "mean"),
    decode_tok_s=("decode_tok_s", "mean"),
    vram_peak_mb=("vram_peak_mb", "mean"),
    cache_min=("cache_min_prefill", "mean"),
    cache_max=("cache_max_prefill", "mean"),
).round(2)
print("Energy summary")
display(summary)

accuracy = (quality.groupby(["config", "context", "depth"])["correct"].mean() * 100).round(1)
print("NIAH accuracy (%)")
display(accuracy.unstack(["context", "depth"]))

# Exploratory paired comparisons among AWQ configurations at 4096.
d = energy[energy.context == 4096].pivot(index="block", columns="config", values="total_energy_j")
comparisons = []
for left, right in [("C1", "C2"), ("C1", "C3"), ("C1", "C4"), ("C3", "C4")]:
    pair = d[[left, right]].dropna()
    assert len(pair) == MEASURED_BLOCKS
    diff = pair[left] - pair[right]
    t, p = stats.ttest_rel(pair[left], pair[right])
    effect = diff.mean() / diff.std(ddof=1) if diff.std(ddof=1) else np.nan
    comparisons.append({
        "comparison": f"{left}-{right}", "n": len(pair),
        "difference_j": diff.mean(), "percent_of_left": 100 * diff.mean() / pair[left].mean(),
        "paired_t": t, "p_unadjusted": p, "paired_d": effect,
    })
tests = pd.DataFrame(comparisons)
tests["p_holm"] = np.maximum.accumulate(
    (tests.sort_values("p_unadjusted").p_unadjusted * np.arange(len(tests), 0, -1)).clip(upper=1)
).reindex(tests.index)
print("Exploratory paired tests (n=5; emphasize effects, not p-values)")
display(tests.round(4))

fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
for config in ["C0", "C1", "C2", "C3", "C4"]:
    s = summary.loc[config]
    axes[0].plot(s.index, s.total_energy_j, "o-", label=config)
    axes[1].plot(s.index, s.vram_peak_mb, "o-", label=config)
    axes[2].plot(s.index, s.decode_tok_s, "o-", label=config)
axes[0].set(title="Total energy", xlabel="Context", ylabel="J")
axes[1].set(title="Peak allocated VRAM", xlabel="Context", ylabel="MB")
axes[2].set(title="Fixed-trace decode", xlabel="Context", ylabel="tokens/s")
for ax in axes:
    ax.grid(alpha=0.3)
    ax.legend()
plt.tight_layout()
plt.savefig(SAVE_DIR / "v5_results.png", dpi=150, bbox_inches="tight")
plt.show()
''',
    ),
]


notebook = {
    "cells": cells,
    "metadata": {
        "accelerator": "GPU",
        "colab": {"gpuType": "T4", "provenance": []},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

for index, cell in enumerate(cells):
    source = "".join(cell["source"])
    if cell["cell_type"] == "code" and not source.lstrip().startswith("%"):
        compile(source, f"cell {index} ({cell['id']})", "exec")

target = Path("experiments/Latest/llama3_2_energy_ablation_final_v5.ipynb")
target.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
print(f"Wrote {target} with {len(cells)} cells; Python syntax valid")
