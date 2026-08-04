# Paste this entire file into one new Colab code cell and run it.
# It reruns only derived analysis from saved rows/traces; no model is loaded.

core_energy = pd.DataFrame(read_shards(DIRS["core_energy_rows"])); sensitivity_energy = pd.DataFrame(read_shards(DIRS["sensitivity_energy_rows"])); energy = pd.concat([core_energy, sensitivity_energy])
assert (len(core_energy), len(sensitivity_energy)) == (75, 20)
trace_rows = []
for row in energy.to_dict("records"):
    path = DIRS["power_traces"] / row["trace_name"]; assert hashlib.sha256(path.read_bytes()).hexdigest() == row["trace_sha256"]
    trace = json.loads(path.read_text()); record = {"table": row["table"], "variant": row["variant"], "context": row["context"], "block": row["block"], "trace_name": path.name}
    values = validate_trace_and_row(row, path)
    for regime in ("raw", "cap82", "cap70"):
        record[f"{regime}_prefill_energy_j"] = values[f"{regime}_prefill"]
        record[f"{regime}_decode_energy_j"] = values[f"{regime}_decode"]
        record[f"{regime}_total_energy_j"] = values[f"{regime}_total"]
    trace_rows.append(record)
traces = pd.DataFrame(trace_rows); assert len(traces)==95; traces.to_csv(DIRS["analysis"] / "trace_level_power_robustness.csv", index=False)
summary=[]
for (table,variant,context),g in traces.groupby(["table","variant","context"]):
    r={"table":table,"variant":variant,"context":context,"n":len(g)}
    for regime in ("raw","cap82","cap70"):
        r[f"{regime}_mean_j"]=g[f"{regime}_total_energy_j"].mean(); r[f"{regime}_sd_j"]=g[f"{regime}_total_energy_j"].std(ddof=1)
    summary.append(r)
condition_summary=pd.DataFrame(summary); assert len(condition_summary)==19; condition_summary.to_csv(DIRS["analysis"] / "condition_power_summary.csv",index=False)

def finite_paired_t(a, b):
    difference = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    if np.allclose(difference, 0): return 0.0, 1.0
    if np.isclose(difference.std(ddof=1), 0): return math.copysign(float("inf"), difference.mean()), 0.0
    result = stats.ttest_rel(a, b); assert np.isfinite(result.statistic) and np.isfinite(result.pvalue)
    return float(result.statistic), float(result.pvalue)

def finite_onesample_t(values):
    values = np.asarray(values, dtype=float)
    if np.allclose(values, 0): return 0.0, 1.0
    if np.isclose(values.std(ddof=1), 0): return math.copysign(float("inf"), values.mean()), 0.0
    result = stats.ttest_1samp(values, 0); assert np.isfinite(result.statistic) and np.isfinite(result.pvalue)
    return float(result.statistic), float(result.pvalue)

def holm(pvalues):
    p=np.asarray(pvalues, dtype=float); assert np.isfinite(p).all() and ((0 <= p) & (p <= 1)).all()
    order=np.argsort(p); adjusted=np.empty(len(p)); running=0.0
    for rank,index in enumerate(order): running=max(running,(len(p)-rank)*p[index]); adjusted[index]=min(1.0,running)
    return adjusted
contrasts=[tuple(pair) for pair in ANALYSIS_PROTOCOL["energy_contrasts"]]
metric_map=ANALYSIS_PROTOCOL["energy_metrics"]
test_rows=[]
for regime in ("raw","cap82","cap70"):
    frame=core_energy[core_energy.context==4096].copy()
    if regime != "raw":
        frame["total_energy_j"] = frame[f"{regime}_total_energy_j"]
        frame["decode_energy_j"] = frame[f"{regime}_decode_energy_j"]
    start=len(test_rows)
    for left,right in contrasts:
        for label,column in metric_map.items():
            a=frame[frame.variant==left].sort_values("block")[column].to_numpy(); b=frame[frame.variant==right].sort_values("block")[column].to_numpy(); d=a-b
            t_value, p_value = finite_paired_t(a, b)
            test_rows.append({"regime":regime,"comparison":f"{left}-{right}","metric":label,"n":5,"mean_difference":d.mean(),
                              "t":t_value,"p_raw":p_value,
                              "wilcoxon_p":float(stats.wilcoxon(d).pvalue) if np.any(d) else 1.0})
    adjusted=holm([r["p_raw"] for r in test_rows[start:]])
    for r,p in zip(test_rows[start:],adjusted): r["p_holm_20"]=float(p); r["significant_0_05"]=bool(p<.05)
tests=pd.DataFrame(test_rows); assert len(tests)==60; tests.to_csv(DIRS["analysis"] / "core_energy_tests_by_regime.csv",index=False)

interaction_rows=[]
for regime in ("raw","cap82","cap70"):
    frame=core_energy[core_energy.context==4096].copy()
    if regime != "raw":
        frame["total_energy_j"] = frame[f"{regime}_total_energy_j"]
        frame["decode_energy_j"] = frame[f"{regime}_decode_energy_j"]
    start=len(interaction_rows)
    for metric,column in metric_map.items():
        pivot=frame.pivot(index="block",columns="variant",values=column).sort_index()
        values=(pivot["Q4-Ref"]-pivot["Q3-Ref"])-(pivot["Q2"]-pivot["Q1-W"])
        t_value, p_value = finite_onesample_t(values)
        interaction_rows.append({"regime":regime,"metric":metric,"n":5,"mean_interaction":values.mean(),
                                 "t":t_value,"p_raw":p_value})
    adjusted=holm([r["p_raw"] for r in interaction_rows[start:]])
    for row,p in zip(interaction_rows[start:],adjusted): row["p_holm_4"]=float(p)
interactions=pd.DataFrame(interaction_rows); assert len(interactions)==12
interactions.to_csv(DIRS["analysis"] / "interaction_tests_by_regime.csv",index=False)
sensitivity_summary=[]
for axis,baseline,variants in (("pyramid","Q2",["Q2-B512","Q2-B1536"]),("tq","Q3-Ref",["Q3-Ref-TQ2","Q3-Ref-TQ3"])):
    for variant in variants:
        left=sensitivity_energy[sensitivity_energy.variant==variant].sort_values("block")
        right=core_energy[(core_energy.variant==baseline)&(core_energy.context==4096)].sort_values("block")
        assert list(left.block)==list(right.block)==list(range(5))
        difference=left.total_energy_j.to_numpy()-right.total_energy_j.to_numpy()
        sensitivity_summary.append({"axis":axis,"variant":variant,"baseline":baseline,"n":5,
                                    "mean_energy_difference_j":difference.mean(),"sd_difference_j":difference.std(ddof=1)})
pd.DataFrame(sensitivity_summary).to_csv(DIRS["analysis"] / "sensitivity_energy_summary.csv",index=False)

raw=tests[tests.regime=="raw"][["comparison","metric","significant_0_05"]].rename(columns={"significant_0_05":"raw_significant"})
stability=[]
for regime in ("cap82","cap70"):
    cap=tests[tests.regime==regime][["comparison","metric","significant_0_05"]]
    joined=raw.merge(cap,on=["comparison","metric"])
    for _,r in joined.iterrows(): stability.append({"regime":regime,"comparison":r.comparison,"metric":r.metric,"raw_significant":r.raw_significant,"capped_significant":r.significant_0_05,"stable":r.raw_significant==r.significant_0_05})
significance=pd.DataFrame(stability); assert len(significance)==40; significance.to_csv(DIRS["analysis"] / "significance_stability.csv",index=False)

rankings=[]; rank_stability=[]
for context in CONTEXTS:
    orders={}
    for regime in ("raw","cap82","cap70"):
        group=condition_summary[(condition_summary.table=="core")&(condition_summary.context==context)].sort_values(f"{regime}_mean_j")
        orders[regime]=group.variant.tolist()
        for rank,(_,r) in enumerate(group.iterrows(),1): rankings.append({"axis":f"core_ctx{context}","regime":regime,"rank":rank,"variant":r.variant,"mean_j":r[f"{regime}_mean_j"]})
    rank_stability.append({"axis":f"core_ctx{context}","stable_82":orders["raw"]==orders["cap82"],"stable_70":orders["raw"]==orders["cap70"]})
for axis,levels in (("pyramid",["Q2-B512","Q2","Q2-B1536"]),("tq",["Q3-Ref-TQ2","Q3-Ref-TQ3","Q3-Ref"])):
    source=pd.concat([condition_summary[(condition_summary.table=="sensitivity")],condition_summary[(condition_summary.table=="core")&(condition_summary.context==4096)]])
    orders={}
    for regime in ("raw","cap82","cap70"):
        group=source[source.variant.isin(levels)].sort_values(f"{regime}_mean_j"); orders[regime]=group.variant.tolist()
        for rank,(_,r) in enumerate(group.iterrows(),1): rankings.append({"axis":axis,"regime":regime,"rank":rank,"variant":r.variant,"mean_j":r[f"{regime}_mean_j"]})
    rank_stability.append({"axis":axis,"stable_82":orders["raw"]==orders["cap82"],"stable_70":orders["raw"]==orders["cap70"]})
rankings=pd.DataFrame(rankings); assert len(rankings)==63; rankings.to_csv(DIRS["analysis"] / "energy_rankings_by_regime.csv",index=False)
rank_stability=pd.DataFrame(rank_stability); assert len(rank_stability)==5; rank_stability.to_csv(DIRS["analysis"] / "ranking_stability.csv",index=False)

def pareto_table(energy_frame, quality_frame, variants, repetitions=2000):
    points=[]
    for v in variants:
        e=energy_frame[(energy_frame.variant==v)&(energy_frame.context==4096)].sort_values("block").total_energy_j
        q=quality_frame[quality_frame.variant==v].sort_values("scenario_id").retrieval_correct.astype(float)
        assert len(e)==5 and len(q)>0
        lo,hi=wilson(int(q.sum()),len(q)); points.append({"variant":v,"energy_mean_j":e.mean(),"energy_sd_j":e.std(ddof=1),"retrieval_rate":q.mean(),"wilson95_low":lo,"wilson95_high":hi})
    result=pd.DataFrame(points); memberships={v:0 for v in variants}; rng=np.random.default_rng(SEED+99000)
    awq_variants=[v for v in variants if v!="Q0"]
    quality_ids_by_depth={depth:sorted(quality_frame[quality_frame.depth==depth].scenario_id.unique()) for depth in sorted(quality_frame.depth.unique())}
    for _ in range(repetitions):
        awq_blocks=rng.integers(0,5,5); q0_blocks=rng.integers(0,5,5)
        sampled_ids=[]
        for ids in quality_ids_by_depth.values(): sampled_ids.extend(np.asarray(ids)[rng.integers(0,len(ids),len(ids))].tolist())
        sampled=[]
        for v in variants:
            e=energy_frame[(energy_frame.variant==v)&(energy_frame.context==4096)].set_index("block").total_energy_j
            block_draw=q0_blocks if v=="Q0" else awq_blocks
            energy_mean=float(e.loc[block_draw].mean())
            q=quality_frame[quality_frame.variant==v].set_index("scenario_id").retrieval_correct.astype(float)
            quality_mean=float(q.loc[sampled_ids].mean())
            sampled.append((v,energy_mean,quality_mean))
        for v,e,q in sampled:
            dominated=any((oe<=e and oq>=q and (oe<e or oq>q)) for ov,oe,oq in sampled if ov!=v)
            memberships[v]+=not dominated
    result["frontier_membership_probability"]=result.variant.map(lambda v:memberships[v]/repetitions); return result
core_pareto=pareto_table(core_energy,core_quality,list(CORE_VARIANTS)); assert len(core_pareto)==5; core_pareto.to_csv(DIRS["analysis"] / "core_pareto_uncertainty.csv",index=False)
common_energy=pd.concat([core_energy,sensitivity_energy]); common_quality=pd.concat([subset_core,sensitivity_quality])
common_variants=list(CORE_VARIANTS)+list(SENSITIVITY_VARIANTS); common_pareto=pareto_table(common_energy,common_quality,common_variants); assert len(common_pareto)==9
common_pareto.to_csv(DIRS["analysis"] / "common15_pareto_uncertainty.csv",index=False)

analysis_core_energy_rows = read_shards(DIRS["core_energy_rows"])
analysis_sensitivity_energy_rows = read_shards(DIRS["sensitivity_energy_rows"])
analysis_core_quality_rows = read_shards(DIRS["core_quality_rows"])
analysis_sensitivity_quality_rows = read_shards(DIRS["sensitivity_quality_rows"])
analysis_input_sha256 = canonical_hash({
    "core_energy": sorted(analysis_core_energy_rows, key=lambda r: (r["variant"], r["context"], r["block"])),
    "sensitivity_energy": sorted(analysis_sensitivity_energy_rows, key=lambda r: (r["variant"], r["context"], r["block"])),
    "core_quality": sorted(analysis_core_quality_rows, key=lambda r: (r["variant"], r["scenario_id"])),
    "sensitivity_quality": sorted(analysis_sensitivity_quality_rows, key=lambda r: (r["variant"], r["scenario_id"])),
    "trace_hashes": sorted((row["trace_name"], row["trace_sha256"])
                           for row in analysis_core_energy_rows + analysis_sensitivity_energy_rows),
})
provenance_exclusions = {"analysis_provenance.json", "analysis_manifest.json", "final_integrity.json"}
output_hashes = {
    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(DIRS["analysis"].iterdir()) if p.is_file() and p.name not in provenance_exclusions
}
atomic_write_json(DIRS["analysis"] / "analysis_provenance.json", {
    "fingerprint": EXPERIMENT_FINGERPRINT, "analysis_input_sha256": analysis_input_sha256,
    "output_sha256": output_hashes,
})
