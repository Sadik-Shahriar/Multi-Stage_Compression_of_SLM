# Reusable Cross-Model Visualization Guide

## Purpose

This guide defines the reusable contract implemented by the Drive-independent
Notebook 09B visualization run. It is for CPU-only derived analysis after each
model has completed and validated its own measurement notebook.

The current reference source is the provisional synthesis bundle with fingerprint
`b19adce0924b4203`. The completed visualization fingerprint is
`53ead4e6db45d2a8`.

## Required Inputs

Each new model must provide normalized products equivalent to:

- `normalized_energy_rows.csv`
- `quality_wilson_intervals.csv`
- `measured_realized_ideal_storage.csv`
- `ideal_packed_kv_footprint.csv`
- `modeled_phase_byte_demand.csv`
- `energy_break_even_surface.csv`
- `empirical_pareto.csv`
- `analysis_protocol.json`
- `ideal_tq_assumptions.json`
- `output_manifest.json`
- `final_integrity.json`

Every product must be bound to an immutable source fingerprint and output
manifest. Visualization code must validate hashes and exact row identities before
plotting.

## Model Adapter

Declare an explicit per-model adapter instead of inferring labels:

```python
MODEL_ADAPTER = {
    "model_name": {
        "fp16": "M0",
        "awq": "M1-W",
        "eviction": "M2",
        "tq_ref": "M3-Ref",
        "eviction_tq_ref": "M4-Ref",
        "layers": 0,
        "kv_heads": 0,
        "head_dim": 0,
    }
}
```

Populate geometry and labels from validated model artifacts. Do not copy Llama
or Qwen geometry into a new model.

## Evidence Tiers

Keep these tiers machine-readable and visually distinct:

1. `measured_system`: observed energy, runtime, throughput, quality, and live
   storage.
2. `realized_reference`: the observed numerical TQ-Ref implementation, including
   materialized K/V and physical uint8 index allocation.
3. `ideal_counterfactual`: packed persistent storage and modeled logical demand
   under declared assumptions.

Use filled marks for measured/realized values and hollow or hatched marks for
ideal values. Never join ideal points into a measured frontier.

## Required Calculations

### Measured TQ-Ref overhead

Pair blocks only within the same model, context, session, and registered path:

```text
Delta E = E_TQ-Ref - E_non-TQ
Relative overhead = Delta E / E_non-TQ
```

Calculate prefill, decode, and total energy separately. Report runtime and
throughput separately from power-clipping sensitivity because clipping does not
create new timing measurements.

### Ideal persistent KV

For batch one and layerwise retained tokens `B_l`:

```text
M_FP = 2 * H_kv * d * s_fp * sum_l(B_l)

M_ideal = 2 * H_kv * sum_l(
    (B_l - r_l) * (d * q / 8 + s_norm)
    + r_l * d * s_fp
) + metadata
```

Apply tensor-level packing ceilings and alignment. Reproduce observed FP bytes
and the realized uint8 logical payload before projecting nominal 2/3/4-bit
storage. Persistent-KV savings are not total peak-VRAM savings.

### Conditional ideal energy

```text
E_ideal = E_baseline - epsilon_mem * Delta_D + O_net
```

Only divide by `Delta_D` when it is positive. Unless measured or externally
bounded parameters are registered, plot the parameter-free boundary:

```text
O_net / epsilon_mem < Delta_D
```

Do not assign numerical ideal joules, latency, throughput, or power from storage
compression alone.

## Standard Figure Set

1. Measured TQ-Ref overhead by context and phase.
2. Measured context scaling for phase energy and throughput.
3. Quality point estimates with Wilson intervals, separated by population.
4. Matched non-TQ, realized-reference, and ideal persistent storage.
5. Ideal packed component scaling over nominal bit width.
6. Prefill/decode logical byte-demand dumbbells.
7. Symbolic ideal-energy break-even boundaries.
8. Measured energy-quality-memory Pareto view.

Export 300-dpi PNG and vector PDF. Include evidence status, source fingerprint,
sample size, uncertainty definition, and claim boundary in captions.

## Validation Gates

- Input fingerprint and schema match the registered source.
- Every manifest-listed input matches byte size and SHA-256.
- Energy keys are unique and total energy equals prefill plus decode.
- Quality estimates equal successes divided by sample size.
- Wilson intervals are valid and populations are not mixed.
- Physical aliases are removed from storage and byte-demand plots.
- Ideal components sum to logical bytes and aligned bytes are not smaller.
- Ideal footprints are monotone in nominal bit width for fixed geometry/budget.
- Modeled `Delta_D` equals baseline demand minus ideal demand.
- Numerical ideal energy fields remain empty without registered parameter domains.
- Source hashes are unchanged after plotting.
- The output ZIP has its own visualization fingerprint and SHA-256.

## Current Reference Findings

- Measured TQ-Ref adds substantial energy and reduces throughput in both current
  models because the accessible path is materialized and unfused.
- Qwen TQ-only preserves hard retrieval at four bits but eviction collapses its
  hard retrieval; Llama does not show the same collapse in this study.
- The declared ideal four-bit TQ-only representation is about 28.8% of matched
  FP16 persistent KV for both current geometries.
- Prefill conversion adds modeled logical demand, while fixed-64-token decode
  savings dominate total modeled demand.
- These findings motivate a production packed/fused kernel experiment; they do
  not substitute for one.
