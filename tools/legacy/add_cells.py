import json

nb = json.load(open('experiments/llama3_2_energy_ablation_simple.ipynb'))

# Add C0 markdown before execute_c0
c0_md = {
    'cell_type': 'markdown',
    'id': 'execute_c0_md',
    'metadata': {},
    'source': [
        "## 7a. C0: FP16 Baseline\n",
        "Runs in its own cell. Model unloaded after completion.\n",
        "\n",
        "> C0 @ 4096 may OOM on T4 (6.0 GB model + 1.5 GB attention matrix = borderline).\n",
        "> If OOM occurs, skip this context \u2014 it's expected hardware constraint."
    ]
}
nb['cells'].insert(15, c0_md)

json.dump(nb, open('experiments/llama3_2_energy_ablation_simple.ipynb', 'w'), indent=1)
print(f'Updated: {len(nb["cells"])} cells, JSON valid')
