# main.tex Pareto Update Guide (v5 → Notebook 09)

Purpose: replace the outdated v5 ceiling-based Pareto analysis in
`paper/main.tex` with the current hard-retrieval, bootstrap-stability
Pareto evidence from Notebook 09 / provisional synthesis fingerprint
`b19adce0924b4203`.

Authoritative evidence references:

- Table of bootstrap frontier members: `research/project_findings_master.md`
  §18.8 (10-point table, 2000 resamples)
- Figure source: `paper/figures/fig08_measured_pareto_energy_quality_memory.pdf`
  (Notebook 09B output)
- Provisional data bundle:
  `evidence/provisional/bundles/CSE407_cross_model_synthesis_local_provisional/`

---

## Edit 1 — Replace the outdated figure + prose in §5.6 "Pareto Frontier with Uncertainty"

Find this block (starts at `\subsection{Pareto Frontier with Uncertainty}`,
ends right before the table that begins with `\begin{table}[htbp]` /
`\caption{Three-Objective Pareto Frontier at 4096 Tokens ...}`):

```latex
\subsection{Pareto Frontier with Uncertainty}

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{figures/v5_final_pareto_uncertainty_4096.pdf}
\caption{Pareto frontier for Llama at 4096 tokens: energy (x-axis, mean $\pm$ SD)
vs.\ NIAH retrieval (y-axis). C2 (green) is the only non-dominated configuration
with both low energy and acceptable quality. C3 is expensive with no quality gain.
Error bars show sample SD over five blocks. Data from accepted bundle fingerprint
\texttt{8d27af8c9ee94de3}.}
\label{fig:pareto-uncertainty}
\end{figure}

Figure~\ref{fig:pareto-uncertainty} is the Pareto uncertainty plot that directly
answers the question of which configuration is best when we account for measurement
variability. The x-axis shows total GPU energy with error bars representing the
sample standard deviation (SD) over five blocks. The y-axis shows NIAH retrieval
accuracy.

C2 (green) is clearly the best measured point: it has the lowest energy and its
quality is essentially equal to C1. The error bars show that C2's energy advantage
is real and consistent (the error bars do not overlap with C1). C3 is far to the
right (expensive) with no quality benefit. C4 sits between C1 and C3 in energy but
gains nothing in quality.

The three-objective Pareto table (energy, quality, memory) is shown in
Table~\ref{tab:pareto3}, using bootstrap resampling to assess stability:
```

Replace it with:

```latex
\subsection{Pareto Frontier with Uncertainty}

The measured three-objective Pareto frontier (raw total energy, hard retrieval,
persistent KV bytes) at 4096 tokens is shown in Table~\ref{tab:pareto3}, with
bootstrap frontier-selection frequency over 2000 resamples.
Figure~\ref{fig:pareto3obj} shows the same measured points: marker area encodes
persistent KV storage (bigger = more memory), horizontal bars show energy SD,
vertical bars show Wilson quality intervals, and edge width encodes bootstrap
frontier-selection stability.

\begin{figure*}[htbp]
\centering
\includegraphics[width=\textwidth]{figures/fig08_measured_pareto_energy_quality_memory.pdf}
\caption{Measured energy--quality--memory Pareto view at 4096 tokens. Each marker
shows one configuration; marker area encodes persistent KV storage (bigger = more
memory); horizontal bars show energy SD; vertical bars show Wilson quality intervals;
edge width shows bootstrap frontier stability. Left: Llama. Right: Qwen. The Qwen
panel shows the stark separation between eviction (very low energy, very low quality)
and TQ-Ref (high energy, high quality). Data from provisional synthesis fingerprint
\texttt{b19adce0924b4203}.}
\label{fig:pareto3obj}
\end{figure*}

For Llama, C2 is the most compelling measured point: the lowest Llama energy
(529.30 J), the smallest persistent cache (119 MiB), and hard retrieval only one
scenario below the C1-W baseline (37/60 vs.\ 38/60). C0 and C1-W are also
frontier members (bootstrap frequency 100\% and 63\%), so C2 is not unique; it is
attractive because it achieves the lowest energy at a quality cost of only one
scenario. C3 and C4 were never or rarely selected (0\% and 0.6\%) because TQ-Ref
raised both energy and storage without improving hard retrieval.

For Qwen, the front separates into two incompatible regions: Q0 is the strongest
high-quality measured point (0.883 retrieval; 97.2\% bootstrap frequency), while
Q2 was always selected on energy and storage (100\%) but fails any minimum-quality
constraint (1/60 retrieval). Q3-Ref was rarely selected (3.8\%) because its high
energy dominates its quality advantage over Q1-W.

Bootstrap frontier frequency is resampling selection stability, not the probability
that a configuration is truly optimal. Pareto membership alone is not a deployment
recommendation; a minimum-quality constraint is required before any configuration
is selected.
```

Keep the following table unchanged — it is already correct (2000-bootstrap
three-objective table):

```latex
\begin{table}[htbp]
\caption{Three-Objective Pareto Frontier at 4096 Tokens (2000 Bootstrap Resamples)}
\label{tab:pareto3}
...
\end{table}
```

---

## Edit 2 — Delete the duplicated §5.18 "Cross-Model Energy-Quality-Memory Pareto View"

Find this entire block (subheading, the `figure*` float, and the two prose
paragraphs after it) and delete it:

```latex
\subsection{Cross-Model Energy-Quality-Memory Pareto View}

\begin{figure*}[htbp]
\centering
\includegraphics[width=\textwidth]{figures/fig08_measured_pareto_energy_quality_memory.pdf}
\caption{Measured energy--quality--memory Pareto view at 4096 tokens. Each marker
shows one configuration; marker area encodes persistent KV storage (bigger = more
memory); horizontal bars show energy SD; vertical bars show Wilson quality intervals;
edge width shows bootstrap frontier stability. Left: Llama. Right: Qwen. The Qwen
panel shows the stark separation between eviction (very low energy, very low quality)
and TQ-Ref (high energy, high quality). Data from provisional synthesis fingerprint
\texttt{b19adce0924b4203}.}
\label{fig:pareto3obj}
\end{figure*}

Figure~\ref{fig:pareto3obj} shows the three-objective view. For Llama, C2 is the
most attractive single point: low energy, small cache, acceptable quality. For
Qwen, there is no single best point: Q0 has the best quality but uses FP16; Q2
uses the least energy but quality is essentially zero; Q3-Ref preserves quality
but is expensive. The visual confirms that a quality constraint is essential before
recommending any configuration.
```

Note: the figure and label `fig:pareto3obj` moved to §5.6 in Edit 1, so deleting
this block does not create an undefined reference.

---

## Edit 3 — Fix the Conclusion (item 5)

Find:

```latex
  \item \textbf{Pareto frontier with uncertainty} (Figure~\ref{fig:pareto-uncertainty})
    shows that Llama C2 is the only configuration that is clearly non-dominated in
    energy, memory, and quality simultaneously.
```

Replace with:

```latex
  \item \textbf{Pareto frontier with uncertainty} (Figure~\ref{fig:pareto3obj})
    shows that C2 is the most attractive measured Llama point: lowest energy,
    smallest persistent cache, and hard retrieval one scenario below baseline,
    with 100\% bootstrap frontier-selection frequency. It is not unique---C0 and
    C1-W are also frontier members---and Pareto membership alone is never a
    deployment recommendation: a minimum-quality constraint is required (Qwen's
    Q2 is always frontier-selected yet unusable at 1/60 retrieval).
```

---

## Edit 4 — Delete obsolete figure files

- Delete `paper/figures/v5_final_pareto_uncertainty_4096.pdf`
  (superseded v5 plot, no longer referenced after Edit 1)
- Delete `paper/figures/fig_empirical_and_projected_pareto.pdf`
  (never referenced in main.tex — unused leftover)

Keep these v5 figures (valid energy/system data, not Pareto):

- `paper/figures/v5_final_results.png`
- `paper/figures/v5_final_system_tradeoffs_4096.png`
- `paper/figures/v5_final_sensitivity_4096.png`
  (caption already discloses the easy-task quality ceiling)

---

## Verification after edits

1. Compile: `pdflatex → bibtex → pdflatex → pdflatex` (Overleaf).
2. Check for unresolved labels:
   - `fig:pareto-uncertainty` must appear nowhere (label removed, no remaining
     `\ref`). Grep for `pareto-uncertainty` — expect zero hits.
   - `fig:pareto3obj` must be defined exactly once (in §5.6) and referenced
     from §5.6 and the Conclusion.
   - `tab:pareto3` must be defined exactly once.
3. Grep for `v5_final_pareto` in main.tex — expect zero hits.

## Optional follow-up (evidence-side bookkeeping, not the paper)

- Mark the four v5 Pareto artifacts as superseded (do not delete; they are in
  the immutable accepted bundle and are recorded as Notebook 09 inputs):
  - `evidence/accepted/bundles/CSE407_llama_v5_final/v5_final_pareto_4096.csv`
  - `evidence/accepted/bundles/CSE407_llama_v5_final/v5_final_multiobjective_pareto_4096.csv`
  - `evidence/accepted/bundles/CSE407_llama_v5_final/v5_final_pareto_uncertainty_4096.pdf`
  - `evidence/accepted/bundles/CSE407_llama_v5_final/v5_final_pareto_uncertainty_4096.png`
- Optionally add `status: superseded` + `superseded_by` to the four entries in
  `research/llama_v5_artifact_manifest.json` (lines ~534-549).
- Do NOT touch
  `evidence/provisional/bundles/CSE407_cross_model_synthesis_local_provisional/input_manifest.json`
  (immutable provenance record).
