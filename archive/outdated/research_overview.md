# Research Overview & Project Proposal

**Project Title:** Holistic Optimization of Small Language Models for Energy-Efficient Edge Inference  
**Course:** CSE407 Green Computing  
**Model Focus:** Qwen2.5 (1.5 Billion Parameters)  

---

## 1. The Problem Statement (Green Computing Context)
The environmental impact and energy consumption of Artificial Intelligence are skyrocketing. While large language models (LLMs) are powerful, their memory requirements during generation—specifically the **Key-Value (KV) Cache**—grow linearly with the context length. 

When generating long responses or analyzing large documents, the KV cache becomes so massive that it causes severe hardware bottlenecks. This forces data centers to run high-wattage GPUs at maximum power, consuming excessive electricity (Joules) and preventing these models from running efficiently on sustainable, low-power "Edge" devices (like IoT sensors or smartphones). 

**The Complex Engineering Problem (EP1 & EP2):** How do we aggressively compress the memory footprint of an LLM to save electrical energy and memory (VRAM), without destroying the model's accuracy or text-generation speed?

---

## 2. The Research Methodology
To solve this, we are conducting a strict, hardware-level empirical study (an "ablation study"). We are evaluating the energy and memory impact of stacking **three state-of-the-art 2026 AI optimization techniques**:

### Technique 1: Activation-aware Weight Quantization (AWQ)
*   **What it does:** Shrinks the actual "brain" (weights) of the model from 16-bit precision down to 4-bit.
*   **The Goal:** Reduces the baseline model footprint from 3.1 GB down to just 0.77 GB.

### Technique 2: Dynamic Token Eviction (SnapKV)
*   **What it does:** Instead of remembering every single word in a long document, SnapKV uses an "observation window" during the initial reading phase to mathematically determine which tokens (words) the model's attention mechanism actually cares about. It permanently deletes the unimportant tokens from memory.
*   **The Goal:** Prevents the KV cache memory from growing infinitely. 

### Technique 3: KV Cache Compression (TurboQuant)
*   **What it does:** For the highly important tokens that SnapKV decides to *keep*, TurboQuant applies an advanced mathematical rotation and compresses those surviving tokens into tiny 4-bit integers. 
*   **The Goal:** Squeezes the surviving memory into the absolute smallest physical footprint possible.

---

## 3. The Experiment (The "Ablation Study")
To prove which combination of these technologies is the most sustainable, we built a **custom PyTorch model architecture** that natively combines them. We are testing the model on 5 different document lengths (512 to 8,192 tokens) using 5 distinct configurations:

| Configuration | Description | What It Tests |
| :--- | :--- | :--- |
| **C0 (Baseline)** | Uncompressed Qwen2.5 (1.5B) | The standard energy and memory baseline. |
| **C1 (AWQ Only)** | Model weights are 4-bit. | How much energy does weight quantization save? |
| **C2 (AWQ + TurboQuant)** | 4-bit weights + 4-bit cache. | Does compressing the cache save energy, or does the decompression overhead cost *more* energy? |
| **C3 (AWQ + SnapKV)** | 4-bit weights + deleted weak tokens. | How much memory does intelligent token dropping save? |
| **C4 (The Ultimate SLM)** | 4-bit weights + Eviction + 4-bit cache. | The bleeding-edge combination of all three. |

---

## 4. How We Measure "Green Computing"
During the experiment, we run a background GPU monitor thread that directly polls the hardware sensors. We record:
1.  **Peak VRAM (MB):** Proves if the model can fit on low-power IoT hardware.
2.  **Average Power Draw (Watts) & Total Energy (Joules):** The ultimate sustainability metric; calculates the exact electrical cost of the inference.
3.  **Throughput (Tokens per Second):** Measures if the optimizations make the model too slow to be useful.

## 5. Expected Outcomes for the Term Paper
By analyzing the final data, this research will confidently answer whether combining modern software optimizations (SnapKV + TurboQuant) actually results in a greener, more sustainable AI system, or if the computational overhead of these algorithms ironically costs more electricity than it saves.
