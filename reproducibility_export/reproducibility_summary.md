# Reproducibility Specification Reference Sheet

**Generated:** 2026-08-16 07:47:53 UTC  
**Schema:** `cse407-reproducibility-audit-v1`

## 1. Hardware & Power Sampling
- **GPU:** NVIDIA Tesla T4 (Turing, Compute Capability 7.5, 40 SMs)
- **VRAM:** 16 GB nominal / 14.56 GiB usable (256-bit bus, ~320 GB/s bandwidth)
- **Power Limit:** 70.0 W enforced cap
- **Power Telemetry:** 10 Hz NVML sampling (100 ms interval), trapezoidal Riemann integration
- **Power Robustness Verification:** Reintegrated under raw, 82 W cap, and 70 W cap

## 2. Software Stack & Pinned Revisions
- **CUDA / Driver:** CUDA 12.8 / Driver 550.54.15
- **PyTorch:** 2.11.0+cu128
- **Transformers:** 5.12.1 (`ddb849abe009d1089e6c691bfc897f27211c663c`)
- **TurboQuant:** 0.2.0 (SHA-256: `7358e2778c8de6974b0c7212ae8e3dbe00552a96b2e2df0aa42878f239a4c72a`)
- **GPTQModel:** 7.1.0
- **Accelerate:** 1.14.0
- **Python:** 3.11 (NumPy 2.2.6, SciPy 1.16.1/3, Pandas 2.2.2)

## 3. Evaluated Model Geometry
- **Llama 3.2-3B-Instruct:**
  - FP16: `unsloth/Llama-3.2-3B-Instruct` (rev: `006f5dcd1393c3add266de40994ba96225e9689d`)
  - AWQ: `casperhansen/llama-3.2-3b-instruct-awq` (rev: `272b3bde867b606760447deb9a4d2719fbdfd3ae`)
  - Geometry: 28 layers, 24 Q / 8 KV heads (3:1 GQA), head dim 128, 8K context
- **Qwen2.5-3B-Instruct:**
  - FP16: `Qwen/Qwen2.5-3B-Instruct` (rev: `aa8e72537993ba99e69dfaafa59ed015b17504d1`)
  - AWQ: `Qwen/Qwen2.5-3B-Instruct-AWQ` (rev: `3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd`)
  - Geometry: 36 layers, 16 Q / 2 KV heads (8:1 GQA), head dim 128, 32K context

## 4. Compression Pipelines & Parameters
- **Weight Quantization:** AWQ GEMM INT4, group size 128
- **Token Eviction:** Custom PyramidKV (geometric decay beta=20, pool kernel=5, window=32, avg budget=1024 tokens)
- **KV Quantization:** TurboQuant 0.2.0 numerical reference (uint8 index container, FP32 norms, 128-token FP16 residual)
- **Sequential Compound:** AWQ -> PyramidKV eviction -> TurboQuant reference

## 5. Experimental Protocols & Statistical Tests
- **Quality Evaluation:** Hard-retrieval Needle-in-a-Haystack (NIAH) 60 scenarios (20 at 10%, 20 at 50%, 20 at 90% depth)
- **Decoding:** Teacher-forced 64-token decode, greedy generation (temp=0.0)
- **Energy Samples:** n=5 blocks per condition
- **Statistical Corrections:** Paired t-tests / Wilcoxon with Holm-Bonferroni correction (alpha=0.05); exact McNemar with Bonferroni correction; Wilson 95% CIs; 2000 bootstrap resamples for Pareto stability
