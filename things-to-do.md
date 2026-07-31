### I. Overall Project Context & Narrative

**Project Goal:** A multi-objective empirical ablation study measuring the physical energy (Joules), latency, and memory interactions of three compression techniques on a sub-4B Small Language Model deployed on constrained edge hardware (NVIDIA T4 GPU).
**The Stack:** Weight Quantization (AWQ) + Token Eviction (PyramidKV) + KV Quantization (TurboQuant).
**The Core Discovery:** While theoretical papers advocate for joint eviction and quantization, real-world edge deployment relies on "unfused" quantization code (like the PyPI `turboquant==0.2.0` package) which causes a massive computational overhead and energy spike. However, applying eviction *before* this unfused quantization acts as a physical "energy shield," filtering tokens out and drastically dropping energy consumption back down.

---

### II. Instructor's Review & Our Rebuttal

**The Instructor's Critique:**

* **Weakness:** The novelty is narrower than claimed because joint eviction and quantization methods (like RDKV and ThinKV) already exist.
* **Suggestions:**
1. Compare against existing joint eviction-and-quantization methods.
2. Add a Pareto-frontier-with-uncertainty analysis.
3. Extend beyond Llama 3.2-3B to a second small-model family (like Qwen2.5-3B) to test architectural generalization.



**Our Reply & Commitments:**
We successfully defended our domain by clarifying that RDKV and ThinKV focus on datacenter throughput (A100 GPUs), whereas we are measuring **physical hardware energy (Joules) on the edge (T4)**. We agreed to their suggestions and committed to:

1. Discussing the theoretical limits of sequential stacking vs. joint math in the paper.
2. Adding Pareto frontiers with standard deviation error bars to prove statistical significance.
3. Replicating the entire pipeline on `Qwen2.5-3B-Instruct`.

---

### III. Gap Analysis: Proposal vs. Current `llama3_2_energy_ablation_final_v5.py`

Your coding agent needs to know that the current Llama 3.2 script is missing several commitments explicitly stated in your project proposal.

**1. Missing TurboQuant Bit-Width Sensitivity Study**

* *What the proposal promised:* Evaluating C3 path sensitivity using TurboQuant bit widths of **2, 3, and 4** at 4096 tokens.


* *What the code has:* TurboQuant is hardcoded to `bits=4` via `TurboQuantCache(bits=4)`.



**2. Missing PyramidKV Retention-Budget Sensitivity Study**

* *What the proposal promised:* Evaluating C2 path sensitivity using PyramidKV average budgets of **512, 1024, and 1536** at 4096 tokens.


* *What the code has:* The budget is hardcoded to 1024 via `build_pyramid_budgets(layers=28, average=1024, window=32, beta=20)`.



**3. Missing Pareto-Frontier-with-Uncertainty Visualization**

* *What the code has:* Basic line plots of Energy/VRAM/Decode vs. Context Length.


* *What is needed:* A scatter plot at 4096 tokens mapping Total Energy (X-axis) vs. NIAH Accuracy (Y-axis) with crosshair error bars (standard deviations from the 5 repeated runs), as requested by the instructor.

**4. Missing "Joint-Method" Proxy / Baseline (Instructor Suggestion 1)**

* *What is needed:* A Configuration 5 (C5) that acts as a proxy for joint compression to compare against your sequential C4 stack.

---

### IV. Master To-Do List for the Coding Agent

Instruct your agent to execute these tasks in the following strict order:

**Task 1: Complete the Llama 3.2-3B Notebook**

* **Step 1.1:** Refactor `build_pyramid_budgets` and `new_cache` to accept dynamic `average_budget` and `tq_bits` parameters.
* **Step 1.2:** Add the Sensitivity Matrix logic to Section 9 (Energy) and Section 10 (Quality). It must specifically test PyramidKV budgets `[512, 1536]` (since 1024 is already tested in C2) and TurboQuant bits `[2, 3]` (since 4 is already tested in C3/C4) **only at the 4096 context length**.


* **Step 1.3:** Inject the matplotlib code to generate the "Pareto Frontier with Uncertainty" plot (Energy vs. Accuracy with X/Y standard deviation error bars) in Section 11.
* **Step 1.4:** *(Optional but recommended)* Integrate a basic joint-compression baseline (e.g., standard SnapKV + INT4 PyTorch dynamic quantization) to serve as a proxy for RDKV/ThinKV to satisfy the instructor's first suggestion.

**Task 2: Build the Qwen2.5-3B Notebook**

* **Step 2.1:** Create a duplicate of the completed Llama notebook.
* **Step 2.2:** Swap `MODEL_FP16` and `MODEL_AWQ` to target `Qwen/Qwen2.5-3B-Instruct`.
* **Step 2.3:** Completely rewrite the monkey-patch hook in Section 6. It must target `transformers.models.qwen2.modeling_qwen2.Qwen2Attention.forward` instead of `LlamaAttention.forward`. The slicing and RoPE application logic will need to be adjusted to match Qwen2's specific source code.
* **Step 2.4:** Update the output CSV filenames (e.g., `v5_qwen_energy_results.csv`) to prevent overwriting the Llama data.

**Task 3: Data Synthesis Script**

* **Step 3.1:** Create a final, separate analysis script that ingests both the Llama and Qwen CSV files.
* **Step 3.2:** Plot side-by-side Pareto frontiers and energy-spike graphs to prove the "Energy Shield" effect generalizes across both model architectures.