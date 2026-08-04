# Paste this entire file into one new Colab code cell. It patches the already
# loaded validator in memory, then resumes the quality schedules from saved rows.
# It is not intended to be run as a standalone experiment script.

def validate_structural_fields(row, prefix, decode_tokens):
    expected = expected_structure(row["variant"], row["context"], decode_tokens)
    key_prefix = f"{prefix}_" if prefix else ""
    active_key = (
        "teacher_forced_active_cache_updates"
        if prefix == "teacher_forced"
        else f"{key_prefix}active_decode_cache_updates"
    )
    assert row[active_key] == expected["active"]
    assert row[f"{key_prefix}evicted_layers"] == expected["evicted"]
    assert row[f"{key_prefix}quantized_layers"] == expected["quantized"]
    assert row[f"{key_prefix}residual_only_layers"] == expected["residual_only"]
    nmse = float(row[f"{key_prefix}tq_actual_path_max_nmse"])
    assert math.isfinite(nmse) and nmse >= 0
    if VARIANT_SPECS[row["variant"]]["tq"]:
        assert nmse <= TQ_NMSE_MAX_BY_BITS[row["tq_bits"]]
    else:
        assert nmse == 0


require_validation()
model = load_fp16()
try:
    done = {
        (row["variant"], row["scenario_id"])
        for row in read_shards(DIRS["core_quality_rows"])
    }
    for item in q0_quality_schedule:
        key = (item["variant"], item["scenario_id"])
        if key in done:
            continue
        row = run_quality_case(model, item)
        commit_quality_row(row, "core")
        done.add(key)
        print("quality", key, row["failure_category"])
finally:
    release_model()

model = load_awq()
try:
    core_done = {
        (row["variant"], row["scenario_id"])
        for row in read_shards(DIRS["core_quality_rows"])
    }
    sensitivity_done = {
        (row["variant"], row["scenario_id"])
        for row in read_shards(DIRS["sensitivity_quality_rows"])
    }
    for item in awq_quality_schedule:
        done = core_done if item["table"] == "core" else sensitivity_done
        key = (item["variant"], item["scenario_id"])
        if key in done:
            continue
        row = run_quality_case(model, item)
        commit_quality_row(row, item["table"])
        done.add(key)
        print("quality", item["table"], key, row["failure_category"])
finally:
    disable_variant()
    release_model()

refresh_csv(DIRS["core_quality_rows"], "core_quality_results.csv")
refresh_csv(DIRS["sensitivity_quality_rows"], "sensitivity_quality_results.csv")
assert len(read_shards(DIRS["core_quality_rows"])) == 300
assert len(read_shards(DIRS["sensitivity_quality_rows"])) == 60
print("Hard-quality matrix complete: 360 rows")
