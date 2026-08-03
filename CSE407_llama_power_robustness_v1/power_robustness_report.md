# Llama Power Robustness Report

- Fingerprint: `91ebc63773e735e6`
- Verified traces: 100 (95 historical v5 + 5 C1-W)
- Maximum raw sample: 124.496 W in `C3-TQ2_ctx4096_block2.json`
- Samples above 70/82/100 W: 1501 / 82 / 21
- Rankings stable at 82 W: True
- Rankings stable at 70 W: True
- Core significance decisions stable: True

Raw joules remain primary. Capped integrations are sensitivity analyses only.
Historical C1 versus C1-W is descriptive because both session and prompt/workload differ.
