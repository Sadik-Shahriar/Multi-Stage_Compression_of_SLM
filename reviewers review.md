View Reviews
Paper ID
744
Paper Title
Multi-Stage Compression of Small Language Models for Energy-Efficient Inference: An Empirical
Systems Ablation

Reviewer #1

Questions
6. Comments to the authors (Your suggestions are extremely important for the
authors to improve the quality of the paper. We humbly request you to provide
feedback to authors.)
1. Hardware generalizability gap between claims and platform. The paper repeatedly
references “power-constrained hardware,” “edge accelerators,” and “edge deployments,”
but all experiments were conducted on an NVIDIA T4, which is a 70 W server-class GPU
used in data center inference, not a typical edge device. The T4’s memory hierarchy,
thermal envelope, and power management behavior differ substantially from ARM-based
NPUs, Jetson Orin, or mobile inference chips. The claims about edge relevance should
either be qualified more explicitly (“these findings characterize T4 server-class inference;
edge deployment behavior requires separate characterization”) or, ideally, at least one
representative edge device (e.g., Jetson Nano or Orin) should be added.
2. Confounds in cross-model GQA comparison. Llama and Qwen differ not only in GQA
ratio (3:1 vs. 8:1) but also in layer count (28 vs. 36), vocabulary size (128k vs. 152k),
native context length (8K vs. 32K), and tokenization. The paper attributes Qwen eviction
failure primarily to GQA head sharing, supported by the sensitivity sweep, but the
sensitivity sweep only tests token budget size, not the other confounds. A more controlled
experiment using models that differ only in GQA ratio (e.g., using the same base model
with different KV-head configurations) would substantially strengthen this claim. If such
experiments are not feasible, the limitation should be stated more prominently.
3. Custom attention wrapper validation. The custom PyramidKV implementation is central
to the eviction results, but it is not validated against the original authors’ implementation.
The ~8.61 J baseline shift from applying the attention wrapper to quantized Llama variants
is noted but not fully investigated. Please either: (a) provide a validation comparison
showing that the custom wrapper reproduces PyramidKV’s published accuracy results on
a standard benchmark, or (b) quantify the magnitude and direction of the baseline shift
more precisely and assess its impact on the interaction contrast measurement.

11/19/26, 9:41 AM Conference Management Toolkit - View review

https://cmt3.research.microsoft.com/ICECE2026/Submission/Reviews/744 1/2

4. Table IV notation issue. Several rows in Table IV appear to merge throughput and
retrieval values in a single column (e.g., “11.34 ± .06.783”), which reads as a formatting
error. Please verify and correct the column alignment in this table.

Reviewer #3

Questions
6. Comments to the authors (Your suggestions are extremely important for the
authors to improve the quality of the paper. We humbly request you to provide
feedback to authors.)
"Main concerns:
1. Past studies are not analyzed critically. Their contributions and weaknesses are not
mentioned. What are the differences between this work and existing approaches?
2. The conclusion must be revised to highlight the key contributions and future
recommendations. "