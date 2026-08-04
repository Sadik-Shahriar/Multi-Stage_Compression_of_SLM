# Track A Fail-Safe Colab Notebooks

All experiment implementations in this project must be delivered as Google
Colab `.ipynb` notebooks with explanatory Markdown cells. Do not create or use
standalone `.py` files as experiment runners.

## Required Order

1. Run `00_verify_historical_evidence.ipynb` on a CPU runtime.
2. `01_llama_hard_retrieval_pilot.ipynb` is the completed, discarded V1 pilot;
   it was too hard at 48 records and must not be rerun as the final benchmark.
3. `02_llama_hard_retrieval_pilot_v2.ipynb` is the completed, discarded V2
   pilot; reducing the record count to 32 was insufficient.
4. `03_llama_hard_retrieval_pilot_v3.ipynb` is the completed, discarded V3
   pilot; four close siblings per target made retrieval harder.
5. `04_llama_hard_retrieval_pilot_v4.ipynb` is the accepted calibration pilot;
   its 60-prompt specification is frozen in
   `research/frozen_hard_retrieval_v4.json`, while its 24 result rows remain
   discarded pilot evidence.
6. `05_llama_full_quality_control_v1.ipynb` is complete. Its executed copy and
   324-file artifact bundle passed both frozen hashes, C1-S/C1-W parity, all
   cache-path gates, five C1-W energy blocks, 300 quality cases, bounded quality
   analysis, and trace reintegration. Do not rerun or append to this experiment.
7. `06_llama_power_robustness_analysis.ipynb` is complete under fingerprint
   `91ebc63773e735e6`. It verified all 100 traces and found core/sensitivity
   rankings and registered significance decisions unchanged under 82 W and 70 W
   caps. Its 15-file output is immutable accepted derived evidence.
8. `07_qwen2_5_adapter_parity_pilot_v1.ipynb` completed under fingerprint
   `91def77c920729e9`. Its five-file artifact bundle passed exact Q1-S/Q1-W
   parity, architecture, prompt, position, cache, eviction-first, TQ-Ref, active
   use, and storage gates. Treat the pilot directory as immutable.
9. `08_qwen2_5_full_reference_v1.ipynb` completed under fingerprint
   `861d89617e53034d`. Its 593-file bundle contains 455 measurement rows and 95
   traces; all manifest, shard/CSV, reintegration, analysis, and final-integrity
    checks passed. Treat the local mirror at
    `evidence/accepted/bundles/CSE407_qwen_track_a_reference_v1/` as immutable.
10. Run `09_cross_model_synthesis_v1_colab.ipynb` in a Google Colab CPU runtime.
    It mounts Drive and resolves the source tree separately from the established
    flat artifact base `/content/drive/MyDrive`, where prior `CSE407_*` bundles
    were written. It validates dependencies and fails if the flat output
    `/content/drive/MyDrive/CSE407_cross_model_synthesis_v1/` already exists. The prior
    local output is preserved separately as
    `evidence/provisional/bundles/CSE407_cross_model_synthesis_local_provisional/`
    and is not authoritative.

## Safety Rules

- Never write into accepted bundles under `evidence/accepted/bundles/`.
- Keep discarded pilot outputs under `evidence/discarded/bundles/`.
- Do not tune the frozen V4 prompts or reuse pilot rows as final evidence.
- C3-Ref and C4-Ref were exposed only after the frozen-hash checks passed.
- Notebook 05 writes only to `CSE407_llama_track_a_full_v1/` under schema
  `track-a-llama-full-v1-2026-08-03-1` and fingerprint `106a561c07c62937`.
- Notebook 05 is accepted: `analysis/final_integrity.json` records 300 unique
  quality rows, five energy rows, paired prompt hashes, and trace reintegration.
- Treat `evidence/accepted/bundles/CSE407_llama_track_a_full_v1/` as immutable evidence. Resolve copied
  trace files by basename rather than rewriting their original Colab paths.
- Treat `evidence/accepted/bundles/CSE407_llama_power_robustness_v1/` as immutable derived evidence.
- Keep every future experiment in this notebook folder with a numeric run-order
  prefix and a separate Drive artifact directory.
- Notebook 07 writes only to `CSE407_qwen_track_a_adapter_pilot_v1/`. It fails
  closed if that directory is nonempty; preserve failed attempts and advance the
  protocol version rather than mixing sessions.
- `evidence/accepted/bundles/CSE407_qwen_track_a_adapter_pilot_v1/` is now immutable accepted pilot
  evidence. Never rerun Notebook 07 against or write into that directory.
- Notebook 08 produced 75 core energy rows, 20 sensitivity energy rows, 95 raw
  traces, 300 core quality rows, and 60 sensitivity-quality rows. Q1-S remained
  parity-only with zero measurement rows.
- The executed Notebook 08 required in-session quality-validator and capped-
  analysis repairs. The exported notebook contains both fixes, but fingerprint
  `861d89617e53034d` does not cryptographically bind the repair-cell source.
- Qwen TQ-Ref remains numerical, materialized-K/V, and unfused; do not present
  its 2/3/4-bit settings as physically packed cache measurements.
- The Colab Notebook 09 writes only to `CSE407_cross_model_synthesis_v1/`. Ideal packed
  storage is analytical, modeled byte demand is not measured DRAM traffic, and
  ideal energy/latency are not point-identified.
