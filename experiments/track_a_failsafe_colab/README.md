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
8. Build and validate the next numbered Qwen2.5-3B adapter/parity pilot before
   running any Qwen energy or full quality matrix.

## Safety Rules

- Never write into `CSE407_llama_v5_final/`.
- Keep discarded pilot outputs under
  `CSE407_llama_track_a_pilot_discarded/` and
  `CSE407_llama_track_a_pilot_v2_discarded/` and
  `CSE407_llama_track_a_pilot_v3_discarded/` and
  `CSE407_llama_track_a_pilot_v4_discarded/`.
- Do not tune the frozen V4 prompts or reuse pilot rows as final evidence.
- C3-Ref and C4-Ref were exposed only after the frozen-hash checks passed.
- Notebook 05 writes only to `CSE407_llama_track_a_full_v1/` under schema
  `track-a-llama-full-v1-2026-08-03-1` and fingerprint `106a561c07c62937`.
- Notebook 05 is accepted: `analysis/final_integrity.json` records 300 unique
  quality rows, five energy rows, paired prompt hashes, and trace reintegration.
- Treat `CSE407_llama_track_a_full_v1/` as immutable evidence. Resolve copied
  trace files by basename rather than rewriting their original Colab paths.
- Treat `CSE407_llama_power_robustness_v1/` as immutable derived evidence.
- Keep every future experiment in this notebook folder with a numeric run-order
  prefix and a separate Drive artifact directory.
