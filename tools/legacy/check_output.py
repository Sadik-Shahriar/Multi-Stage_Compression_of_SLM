import json
nb = json.load(open('llama3_2_energy_ablation_simple Output.ipynb', encoding='utf-8'))
for i, c in enumerate(nb['cells']):
    if c.get('outputs'):
        for o in c['outputs']:
            if o.get('output_type') == 'stream' and o.get('name') == 'stdout':
                text = ''.join(o.get('text', []))
                if any(kw in text for kw in ['C1 @', 'C2 @', 'C3 @', 'C4 @', 'NIAH', 'Saved', 'Budget', 'PyramidKV', 'Eviction', '===', 'Diagnostics']):
                    print(f'--- Cell {i} ({c["id"]}) ---')
                    print(text[:3000])
                    print()
