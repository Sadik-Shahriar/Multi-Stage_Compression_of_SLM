# Literature Review: Holistic Optimization of Small Language Models for Energy-Efficient Edge Inference

## Abstract

The environmental footprint of Large Language Model (LLM) inference — now exceeding training in total lifecycle carbon — has driven research into compression techniques that reduce memory and energy without sacrificing accuracy. Three orthogonal approaches dominate: weight quantization, token eviction from the Key-Value (KV) cache, and KV cache quantization. This review synthesizes 20+ peer-reviewed papers and technical reports from MLSys, NeurIPS, ICML, ICLR, COLM, ACL, and AISTATS (2023–2026), sourced and verified via Firecrawl Research. Across all sources, a clear consensus emerges: each technique works well in isolation, but no published work measures the *compound* energy-accuracy-memory trade-off of all three applied simultaneously to a sub-4B Small Language Model (SLM) with built-in reasoning mode, using real hardware power monitoring on a production GPU (NVIDIA T4). This gap — explicitly noted in TurboQuant (ICLR 2026), SLMQuant (2025), and the EMNLP 2025 SLM study — is the focus of this project.

---

## Key Papers

### Weight Quantization

| Paper | Authors | Venue | Key Findings | Relevance |
|-------|---------|-------|-------------|-----------|
| AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration [arXiv:2306.00978] | Lin, Tang, Tang, Yang, Chen, Wang, Xiao, Dang, Gan, Han | MLSys 2024 **Best Paper** | Protecting 1% salient weights via activation-aware per-channel scaling reduces quantization error. No backpropagation needed. 3× speedup vs HuggingFace FP16. Deploys 70B Llama-2 on mobile GPU. | **Primary weight quantization method.** Official Qwen3-4B-AWQ weights on HuggingFace. |
| GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers [arXiv:2210.17323] | Frantar, Ashkboos, Hoefler, Alistarh | ICLR 2023 | Second-order Hessian-based quantization. Widely adopted baseline. Requires calibration dataset. | Baseline comparison for weight quantization. |
| SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models [arXiv:2211.10438] | Xiao, Lin, Seznec et al. | ICML 2023 | W8A8 quantization via activation smoothing. Shifted quantization difficulty from activations to weights. | Alternative approach (8-bit, not 4-bit). |
| An Empirical Study of Qwen3 Quantization [arXiv:2505.02214] | Zheng, Li, Chu, Feng, Ma, Luo, Guo, Qin, Magno, Liu | 2025 | Tested 5 PTQ methods on Qwen3 (0.6B–32B). AWQ outperforms GPTQ at 4-bit on Qwen3-4B: AWQ achieves 66.0% avg commonsense reasoning vs GPTQ 65.8%. Qwen3-4B more quantization-sensitive than LLaMA3-8B due to stronger pretraining. | **Direct evidence** that AWQ > GPTQ for Qwen3-4B. Confirms Qwen3's unique quantization behavior. |
| SLMQuant: Benchmarking Small Language Model Quantization for Practical Deployment [arXiv:2511.13023] | Wang, Zeng, Guo, Ma, Liu, Liu | 2025 | First systematic benchmark of quantization on SLMs (sub-7B). Finds fundamental disparities: SLMs are more quantization-sensitive than LLMs. Direct transfer of LLM-optimized techniques leads to suboptimal results. | **Key justification** for architecture-specific quantization studies on SLMs. |

---

### Token Eviction (KV Cache Pruning)

| Paper | Authors | Venue | Key Findings | Relevance |
|-------|---------|-------|-------------|-----------|
| H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models [arXiv:2306.14048] | Zhang, Sheng, Zhou, Chen, Zheng, Cai, Song, Tian, Ré, Barrett, Wang, Chen | NeurIPS 2023 | 20% of tokens (Heavy Hitters) contribute most attention value. Dynamic retention of recent + H2 tokens. 29× throughput improvement over DeepSpeed. | Foundational eviction method. Proves token importance is highly skewed. |
| SnapKV: LLM Knows What You are Looking for Before Generation [arXiv:2404.14469] | Li, Huang, Yang, Venkitesh, Locatelli, Ye, Cai, Lewis, Chen | NeurIPS 2024 | Attention allocation pattern is consistent during generation and can be identified from an observation window (last 32 tokens). 3.6× speed, 8.2× memory at 16K. 380K tokens on A100-80GB. | **Fallback eviction method.** Simple, proven, strong NIAH performance. |
| PyramidKV: Dynamic KV Cache Compression based on Pyramidal Information Funneling [arXiv:2406.02069] | Cai, Zhang, Gao, Liu, Li, Liu, Lu, Xiong, Dong, Hu, Xiao | COLM 2025 | Attention scatters in lower layers, consolidates in higher layers. Variable cache allocation (more in lower, less in higher layers). 12% cache matches full performance. 20.5% accuracy improvement over uniform at 0.7% cache. | **Target eviction method.** Outperforms SnapKV by 5–15% NIAH at same budget. |
| StreamingLLM: Efficient Streaming Language Models with Attention Sinks [arXiv:2309.17453] | Xiao, Tian, Chen, Han, Lewis | ICLR 2024 | Initial 4 tokens act as "attention sinks" — receive high attention regardless of relevance. Window + sink tokens for infinite generation. | Baseline. Poor retrieval accuracy for mid-context tokens. |
| ScissorHands: Exploiting the Persistence of Importance Hypothesis [arXiv:2305.17118] | Liu, Desai, Liao, Wang, Xie, Xu, Kyrillidis, Shrivastava | NeurIPS 2023 | Token importance persists across time steps. Temporal-persistence-based eviction avoids cumulative-score bias. | Alternative eviction criterion. |

---

### KV Cache Quantization

| Paper | Authors | Venue | Key Findings | Relevance |
|-------|---------|-------|-------------|-----------|
| TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate [arXiv:2504.19874] | Zandieh, Daliri, Hadian, Mirrokni (Google Research) | ICLR 2026 | Random rotation → Beta-distributed coordinates → Lloyd-Max scalar quantization. Data-oblivious, no calibration. Absolute quality neutrality at 3.5 bits. Near-optimal distortion rate (within 2.7× of info-theoretic lower bound). | **Primary KV cache quantization method.** `pip install turboquant`, tested on Qwen models. |
| KIVI: A Tuning-Free Asymmetric 2-bit Quantization for KV Cache [arXiv:2402.02750] | Liu, Yuan, Jin, Zhong, Xu, Braverman, Chen, Hu | ICML 2024 | Keys quantized per-channel, values per-token. 2.6× peak memory reduction. 2.35–3.47× throughput. Llama, Falcon, Mistral. | Baseline for KV cache quantization. |
| PolarQuant: Quantizing KV Caches with Polar Transformation [arXiv:2502.02617] | Shu, Wu et al. | AISTATS 2026 | Polar decomposition + random preconditioning. Recursive polar coordinate quantization. Competitive at 2–3 bits. | Alternative to TurboQuant. |
| Quantization Dominates Rank Reduction for KV-Cache Compression [arXiv:2604.11501] | Salfati | 2026 | **Key finding:** INT4 quantization preserves score ordering; rank reduction can flip attended tokens. INT4 matches FP16 (Mistral 7B: +0.23 PPL) while rank-32 collapses to 0.4%. Gap grows with GQA aggressiveness. | **Validates quantization over low-rank** for GQA models like Qwen3-4B (8 KV heads). 75% KV reduction at +0.18 PPL. |

---

### Compound / Joint Compression (Quantization + Eviction)

| Paper | Authors | Venue | Key Findings | Relevance |
|-------|---------|-------|-------------|-----------|
| RDKV: Rate-Distortion Bit Allocation for Joint Eviction and Quantization of the KV Cache [arXiv:2605.08317] | Zhang, Guo, Benini, Li | 2026 | Casts KV compression as rate-distortion problem. Joint bit allocation per token/channel. Outperforms best baseline by 9.1% avg on LongBench. 97.81% accuracy at 2.48% cache. 4.5× decode speedup at 128K context. | **Closest to our compound approach.** Tests on 7B+ models only, not sub-4B SLMs. No energy measurement. |
| ThinKV: Thought-Adaptive KV Cache Compression for Efficient Reasoning Models [arXiv:2510.01290] | Ramachandran, Neseem, Sakr, Venkatesan, Khailany, Krishna | 2026 | Hybrid quantization-eviction for reasoning (CoT) models. Assigns precision by thought importance. <5% KV cache with near-lossless accuracy. 5.8× throughput. | **Directly relevant to thinking mode.** Tests on DeepSeek-R1, GPT-OSS, AceReason. Does not measure energy. |
| VeriCache: Turning Lossy KV Cache into Lossless LLM Inference [arXiv:2605.17613] | Yao, Shen, Du, Feng, Seo, Zhang, Huang, Liu, Lu, Jiang | 2026 | First framework ensuring identical output to full-cache. Compressed KV drafts tokens, full KV verifies. Up to 4× throughput. | Verifies that compression methods can be losslessly verified; bounds accuracy risk. |
| Quantizing KV cache: Quantization Dominates Rank Reduction [arXiv:2604.11501] | Salfati | 2026 | Joint K+V INT4 achieves 75% KV reduction at only +0.18 PPL on Mistral 7B. GQA-specific finding: quantization advantage grows with fewer KV heads. | **Critical for Qwen3-4B GQA (8 KV heads):** quantization > low-rank for this architecture. |

---

### Energy Measurement & Sustainable AI

| Paper | Authors | Venue | Key Findings | Relevance |
|-------|---------|-------|-------------|-----------|
| Watt Counts: Energy-Aware Benchmark for Sustainable LLM Inference [arXiv:2604.09048] | Argerich, Fürst, Patiño-Martínez | 2026 | **Largest open-access energy dataset:** 5,000+ experiments, 50 LLMs × 10 GPUs. T4 averages 45–65W during decoding. GPU selection crucial for energy efficiency. 70% energy reduction possible with hardware-aware deployment. | **Primary energy methodology reference.** Recommended 50–200ms polling for T4. |
| From Prompts to Power: Measuring the Energy Footprint of LLM Inference [arXiv:2511.05597] | Caravaca, Cuevas, Cuevas | 2025 | 32,500+ measurements, 21 GPU configs, 155 models. Predictive model for inference energy. Implementation as browser extension. | Large-scale energy methodology. |
| TokenPowerBench: Benchmarking the Power Consumption of LLM Inference [arXiv:2512.03024] | (multiple) | 2025 | First lightweight benchmark for LLM inference power. Declarative config covering model, prompt set, GPU. >90% of total power is inference, not training. | Standardized energy benchmarking methodology. |
| From Words to Watts: Benchmarking the Energy Costs of LLM Inference [arXiv:2310.03003] | (multiple) | 2023 | Early systematic energy measurement of LLM inference. Benchmark across model sizes and hardware. | Foundational energy benchmarking work. |

---

### Qwen3-Specific Literature

| Paper | Authors | Venue | Key Findings | Relevance |
|-------|---------|-------|-------------|-----------|
| Qwen3 Technical Report [arXiv:2505.09388] | Yang, Li, Yang, Zhang, Hui, Zheng, Yu et al. (60+ authors) | 2025 | Introduces Qwen3 family (0.6B–235B). Thinking + non-thinking mode in unified framework. Thinking budget mechanism. GQA (32 Q / 8 KV heads for 4B). 32K native context. Apache 2.0 license. | **Model definition.** All architectural specs: 36 layers, GQA, thinking mode via `enable_thinking=True`. |
| An Empirical Study of Qwen3 Quantization [arXiv:2505.02214] | Zheng, Li, Chu et al. | 2025 | Qwen3-4B: FP16 PPL=13.7 Wiki2. AWQ W4A16g128: PPL=16.6. AWQ outperforms GPTQ. Qwen3 more quantization-sensitive than LLaMA3 due to stronger pretraining. Calls for rotation-based methods (TurboQuant) as future work. | **Directly informs our AWQ choice.** Identifies Qwen3's unique quantization sensitivity as open problem. |

---

## Themes And Consensus

1. **Quantization consistency beats rank reduction:** Salfati (2026) formally proves quantization preserves attention score ordering better than dimension removal, especially for GQA. This validates our choice of quantization-based compression (AWQ + TurboQuant) over low-rank methods for Qwen3-4B's 8 KV heads.

2. **SLMs are not small LLMs:** SLMQuant (Wang et al., 2025) and the Qwen3 quantization study (Zheng et al., 2025) independently find that SLMs are more quantization-sensitive than larger models, and that LLM-optimized techniques transfer poorly. Architecture-specific studies are essential.

3. **Token importance is highly skewed:** H2O, SnapKV, and PyramidKV all converge on the same finding: <20% of tokens carry most attention weight. PyramidKV adds that this skew follows a pyramidal pattern across layers — more dispersion at lower layers, more concentration at higher layers.

4. **Compound compression is unmeasured at the SLM scale:** RDKV (2026) is the closest compound work but targets 7B+ models on A100-class GPUs, with no energy measurement. ThinKV (2026) addresses thinking/CoT models but uses different reasoning architectures (DeepSeek-R1), not Qwen3. No paper combines weight quantization + token eviction + KV cache quantization on a sub-4B model.

5. **Energy measurement is methodologically mature:** Watt Counts (2026), From Prompts to Power (2025), and TokenPowerBench (2025) establish standardized protocols: 50–200ms pynvml polling, 3+ runs per configuration, reporting GPU model + TDP + polling interval + variance.

---

## Open Questions And Debates

1. **Does compound quantization + eviction create constructive or destructive interference?** RDKV shows joint rate-distortion allocation outperforms independent optimization, but only on models ≥7B. The interaction may differ for 4B models where each KV head carries more per-entry information.

2. **How does thinking mode interact with KV compression?** ThinKV (2026) addresses this for DeepSeek-R1 but not for Qwen3's integrated thinking. Qwen3's thinking budget mechanism may interact differently with compression than open-ended CoT.

3. **Is the energy overhead of TurboQuant's random rotation worth the memory savings?** The Google Research blog reports up to 8× speedup on H100, but on T4 (no tensor core support for FP8), the overhead may alter the energy trade-off. No published measurement exists on T4.

4. **Can AWQ + TurboQuant + PyramidKV fit in <4 GB for edge deployment?** AWQ alone uses ~2.9 GB on T4. Adding TurboQuant and PyramidKV may save additional 200–500 MB. Whether this crosses the 4 GB edge threshold is unknown without empirical measurement.

---

## Emerging Trends

1. **Joint compression (eviction + quantization) is the next frontier:** Three concurrent 2026 papers (RDKV, ThinKV, MoE-nD) treat eviction and quantization as a single optimization problem rather than separate techniques. This project (C4 config) contributes to this emerging paradigm.

2. **Data-oblivious methods are preferred for deployment:** TurboQuant's data-oblivious design (no calibration, no training) and PyramidKV's calibration-free eviction signal make them practical for real-world deployment where calibration data may not be representative.

3. **Energy as a first-class metric:** Watt Counts, TokenPowerBench, and the ISO software carbon intensity standard (ISO/IEC 21031:2024) are moving energy measurement from a niche concern to a standard reporting requirement.

4. **SLM-specific quantization research is accelerating:** SLMQuant (2025) and the Qwen3 quantization study (2025) mark the beginning of dedicated SLM compression research, distinct from scaling LLM methods downward.

---

## Sources

### Weight Quantization
1. Lin et al. "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration." MLSys 2024 (Best Paper). [arXiv:2306.00978](https://arxiv.org/abs/2306.00978)
2. Frantar et al. "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers." ICLR 2023. [arXiv:2210.17323](https://arxiv.org/abs/2210.17323)
3. Xiao et al. "SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models." ICML 2023. [arXiv:2211.10438](https://arxiv.org/abs/2211.10438)
4. Zheng et al. "An Empirical Study of Qwen3 Quantization." 2025. [arXiv:2505.02214](https://arxiv.org/abs/2505.02214)
5. Wang et al. "SLMQuant: Benchmarking Small Language Model Quantization for Practical Deployment." 2025. [arXiv:2511.13023](https://arxiv.org/abs/2511.13023)
6. Tseng et al. "QuIP#: Even Better LLM Quantization with Latent Lattice Codebooks." ICML 2024. [arXiv:2402.04396](https://arxiv.org/abs/2402.04396)

### Token Eviction
7. Zhang et al. "H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models." NeurIPS 2023. [arXiv:2306.14048](https://arxiv.org/abs/2306.14048)
8. Li et al. "SnapKV: LLM Knows What You are Looking for Before Generation." NeurIPS 2024. [arXiv:2404.14469](https://arxiv.org/abs/2404.14469)
9. Cai et al. "PyramidKV: Dynamic KV Cache Compression based on Pyramidal Information Funneling." COLM 2025. [arXiv:2406.02069](https://arxiv.org/abs/2406.02069)
10. Xiao et al. "StreamingLLM: Efficient Streaming Language Models with Attention Sinks." ICLR 2024. [arXiv:2309.17453](https://arxiv.org/abs/2309.17453)
11. Liu et al. "ScissorHands: Exploiting the Persistence of Importance Hypothesis." NeurIPS 2023. [arXiv:2305.17118](https://arxiv.org/abs/2305.17118)

### KV Cache Quantization
12. Zandieh et al. "TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate." ICLR 2026. [arXiv:2504.19874](https://arxiv.org/abs/2504.19874)
13. Liu et al. "KIVI: A Tuning-Free Asymmetric 2-bit Quantization for KV Cache." ICML 2024. [arXiv:2402.02750](https://arxiv.org/abs/2402.02750)
14. Shu et al. "PolarQuant: Quantizing KV Caches with Polar Transformation." AISTATS 2026. [arXiv:2502.02617](https://arxiv.org/abs/2502.02617)
15. Salfati. "Quantization Dominates Rank Reduction for KV-Cache Compression." 2026. [arXiv:2604.11501](https://arxiv.org/abs/2604.11501)

### Compound Compression
16. Zhang et al. "RDKV: Rate-Distortion Bit Allocation for Joint Eviction and Quantization of the KV Cache." 2026. [arXiv:2605.08317](https://arxiv.org/abs/2605.08317)
17. Ramachandran et al. "ThinKV: Thought-Adaptive KV Cache Compression for Efficient Reasoning Models." 2026. [arXiv:2510.01290](https://arxiv.org/abs/2510.01290)
18. Yao et al. "VeriCache: Turning Lossy KV Cache into Lossless LLM Inference." 2026. [arXiv:2605.17613](https://arxiv.org/abs/2605.17613)

### Energy Measurement
19. Argerich et al. "Watt Counts: Energy-Aware Benchmark for Sustainable LLM Inference on Heterogeneous GPU Architectures." 2026. [arXiv:2604.09048](https://arxiv.org/abs/2604.09048)
20. Caravaca et al. "From Prompts to Power: Measuring the Energy Footprint of LLM Inference." 2025. [arXiv:2511.05597](https://arxiv.org/abs/2511.05597)
21. TokenPowerBench: Benchmarking the Power Consumption of LLM Inference. 2025. [arXiv:2512.03024](https://arxiv.org/abs/2512.03024)
22. From Words to Watts: Benchmarking the Energy Costs of Large Language Model Inference. 2023. [arXiv:2310.03003](https://arxiv.org/abs/2310.03003)

### Qwen3 and SLM Deployment
23. Qwen Team. "Qwen3 Technical Report." 2025. [arXiv:2505.09388](https://arxiv.org/abs/2505.09388)
24. Sarker et al. "Characterizing Energy Footprint of Small Language Models on Edges." 2025. [arXiv:2511.11624](https://arxiv.org/abs/2511.11624)
25. Sustainable LLM Inference for Edge AI. ACM Transactions on Internet of Things, 2026.
26. On-Device LLMs: A Comprehensive Survey. Springer, 2026.

### Energy Context
27. IEA. "Energy Efficiency 2024." International Energy Agency, 2024.
28. Patterson et al. "Carbon Emissions and Large Neural Network Training." 2021. [arXiv:2104.10350](https://arxiv.org/abs/2104.10350)
29. Strubell et al. "Energy and Policy Considerations for Deep Learning in NLP." ACL 2019.
30. Bender et al. "On the Dangers of Stochastic Parrots: Can Language Models Be Too Big?" FAccT 2021.

### Standards
31. ISO/IEC 21031:2024. "Information Technology — Software Carbon Intensity (SCI) Specification."

---

## Rerun Inputs
workflow: firecrawl-research-papers
topic: Holistic optimization of small language models for energy-efficient edge inference — weight quantization (AWQ), token eviction (SnapKV/PyramidKV), KV cache quantization (TurboQuant), compound compression, energy measurement
target_count: 30+
output: markdown
