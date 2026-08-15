"""Recreate the 60 frozen Llama Track A hard-retrieval test prompts.

Install in Colab:
    !pip install -q transformers

Example:
    !python 05_llama_retrieval_prompt_generator.py
    !python 05_llama_retrieval_prompt_generator.py --scenario-id d10-s00 --output d10-s00.md

The default output is a human-readable Markdown file containing all 60 prompts.
No GPU or model weights are required. The script downloads only the pinned
tokenizer needed to reproduce the exact 4,096-token prompt layout. Use
``--format json`` to also export the canonical ``input_ids`` for exact inference.
"""

import argparse
import hashlib
import json
import random
from pathlib import Path

try:
    from transformers import AutoTokenizer
except ModuleNotFoundError as error:
    raise SystemExit("Install the tokenizer dependency first: pip install transformers") from error


MODEL_AWQ = "casperhansen/llama-3.2-3b-instruct-awq"
MODEL_AWQ_REVISION = "272b3bde867b606760447deb9a4d2719fbdfd3ae"
EXPECTED_SEMANTIC_SHA256 = "fffa82607af6e7d2c892d18d5bc790524570833472ad397b7ab2e54eb03005ef"
EXPECTED_PROMPT_SET_SHA256 = "4e1ced4fd4829629929a346879cc00c45476f38fa0936137909b8779242321e8"

GENERATOR_VERSION = "track-a-hard-retrieval-v4-controlled-pairs-draft"
MANIFEST_SCHEMA = "cse407-hard-retrieval-manifest-v1"
BASE_SEED = 407_100
DEPTHS = (0.1, 0.5, 0.9)
SCENARIOS_PER_DEPTH = 20
RECORD_COUNT = 32
CONTEXT_TOKENS = 4096
FINAL_QUERY_WINDOW = 32
MIN_RECORD_GAP_TOKENS = 16
# The Llama chat template otherwise substitutes the machine's current date.
ACCEPTED_CHAT_TEMPLATE_DATE = "03 Aug 2026"
SYSTEM_INSTRUCTION = "Use only the document. Return exactly one activation code and no explanation."
PLACEHOLDER = "{HARD_RETRIEVAL_DOCUMENT}"
KEY_LABELS = (
    "AURORA", "BOREAL", "CEDAR", "DRAGON", "EMBER", "FALCON", "GARNET", "HARBOR",
    "INDIGO", "JASPER", "KESTREL", "LANTERN", "MARINER", "NEBULA", "ORBIT", "PRAIRIE",
    "QUARTZ", "RAVEN", "SUMMIT", "TEMPEST", "UMBRA", "VECTOR", "WILLOW", "XENON",
    "YARROW", "ZEPHYR", "ORBITAL", "MARINA", "CEDRIC", "FALCONE", "GARNET-X", "HARBOR-X",
)
FILLER_TOPICS = (
    "thermal scheduling", "memory allocation", "coastal monitoring",
    "warehouse routing", "battery maintenance", "traffic forecasting",
    "compiler testing", "water treatment", "satellite imaging",
    "clinical logistics", "network telemetry", "acoustic sensing",
    "grid balancing", "crop analysis", "robot calibration", "archive indexing",
)
FILLER_METHODS = (
    "compares recent measurements with a rolling baseline",
    "records each decision before the next review cycle",
    "uses independent checks to detect inconsistent observations",
    "separates routine maintenance from exceptional interventions",
    "prioritizes stable operation over short-lived peak performance",
    "tracks uncertainty alongside every summarized measurement",
    "repeats validation after any material configuration change",
    "keeps raw observations available for later auditing",
)
FILLER_OUTCOMES = (
    "The review found that seasonal variation explained most of the change.",
    "Operators retained the conservative threshold for the next evaluation.",
    "No single measurement was treated as sufficient evidence for deployment.",
    "The team documented both successful trials and inconclusive observations.",
    "A later audit confirmed the ordering but revised the uncertainty estimate.",
    "The report emphasized reproducibility and clearly separated derived values.",
    "Follow-up work focused on failure recovery rather than headline throughput.",
    "The final recommendation required another independent measurement period.",
)


def canonical_hash(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def token_ids_hash(input_ids):
    return hashlib.sha256(",".join(map(str, input_ids)).encode("ascii")).hexdigest()


def _make_unique_codes(rng, count):
    letters = "ABCDEFGH"
    suffixes = "KLMNPQ"
    codes = set()
    while len(codes) < count:
        codes.add(
            f"{rng.choice(letters)}{rng.randrange(100, 1000):03d}-"
            f"{rng.choice(suffixes)}{rng.randrange(10, 100):02d}"
        )
    result = sorted(codes)
    rng.shuffle(result)
    return result


def _make_similar_keys(rng, count):
    candidates = [f"NODE-{label}" for label in KEY_LABELS]
    if count > len(candidates):
        raise ValueError("At most 32 records are supported")
    rng.shuffle(candidates)
    return candidates[:count]


def build_semantic_manifest():
    """Build the frozen set of 60 records-only retrieval scenarios."""
    scenarios = []
    for depth_index, depth in enumerate(DEPTHS):
        for index in range(SCENARIOS_PER_DEPTH):
            scenario_seed = BASE_SEED + depth_index * 100_000 + index
            rng = random.Random(scenario_seed)
            keys = _make_similar_keys(rng, RECORD_COUNT)
            codes = _make_unique_codes(rng, RECORD_COUNT)
            target_index = rng.randrange(RECORD_COUNT)
            records = [
                {"key": key, "code": code, "is_target": position == target_index}
                for position, (key, code) in enumerate(zip(keys, codes))
            ]
            rng.shuffle(records)
            target = next(record for record in records if record["is_target"])
            scenarios.append({
                "scenario_id": f"d{int(depth * 100):02d}-s{index:02d}",
                "seed": scenario_seed,
                "depth": depth,
                "target_key": target["key"],
                "target_code": target["code"],
                "records": records,
            })
    manifest = {
        "manifest_schema": MANIFEST_SCHEMA,
        "generator_version": GENERATOR_VERSION,
        "status": "DRAFT_UNTIL_C1W_C2_PILOT_PASSES",
        "base_seed": BASE_SEED,
        "depths": list(DEPTHS),
        "scenarios_per_depth": SCENARIOS_PER_DEPTH,
        "record_count": RECORD_COUNT,
        "scenarios": scenarios,
    }
    manifest["semantic_sha256"] = canonical_hash(manifest)
    if manifest["semantic_sha256"] != EXPECTED_SEMANTIC_SHA256:
        raise AssertionError("The regenerated semantic scenarios do not match accepted evidence")
    return manifest


def _make_filler_text(rng, minimum_paragraphs=512):
    paragraphs = []
    topic_order = list(FILLER_TOPICS)
    method_order = list(FILLER_METHODS)
    outcome_order = list(FILLER_OUTCOMES)
    for index in range(minimum_paragraphs):
        if index % len(topic_order) == 0:
            rng.shuffle(topic_order)
        if index % len(method_order) == 0:
            rng.shuffle(method_order)
        if index % len(outcome_order) == 0:
            rng.shuffle(outcome_order)
        paragraphs.append(
            f"Memo {index + 1} discusses {topic_order[index % len(topic_order)]}. "
            f"The working group {method_order[index % len(method_order)]}. "
            f"Sample batch {2000 + index} was reviewed by {2 + index % 7} analysts. "
            f"{outcome_order[index % len(outcome_order)]}\n"
        )
    return "\n".join(paragraphs)


def _record_text(record):
    return f"\n[Access record] System {record['key']} uses activation code {record['code']}.\n"


def _encode(tokenizer, text):
    return list(tokenizer.encode(text, add_special_tokens=False))


def _allocate_gaps(total, count, rng):
    minimum = MIN_RECORD_GAP_TOKENS * count
    if total < minimum:
        raise ValueError("The region cannot keep all records separated")
    remaining = total - minimum
    gaps = [MIN_RECORD_GAP_TOKENS] * count
    order = list(range(count))
    rng.shuffle(order)
    for index in range(remaining):
        gaps[order[index % count]] += 1
    return gaps


def _pack_region(tokenizer, records, token_budget, rng):
    record_ids = [_encode(tokenizer, _record_text(record)) for record in records]
    filler_budget = token_budget - sum(map(len, record_ids))
    gaps = _allocate_gaps(filler_budget, len(records) + 1, rng)
    filler_text = _make_filler_text(rng)
    filler_ids = _encode(tokenizer, filler_text)
    while len(filler_ids) < filler_budget:
        filler_text += _make_filler_text(rng)
        filler_ids = _encode(tokenizer, filler_text)
    result = []
    cursor = 0
    for index, encoded_record in enumerate(record_ids):
        next_cursor = cursor + gaps[index]
        result.extend(filler_ids[cursor:next_cursor])
        result.extend(encoded_record)
        cursor = next_cursor
    result.extend(filler_ids[cursor:cursor + gaps[-1]])
    if len(result) != token_budget:
        raise AssertionError(f"Packed {len(result)} tokens, expected {token_budget}")
    return result


def materialize_scenario(tokenizer, scenario):
    """Create one exact 4,096-token input from a frozen semantic scenario."""
    question = f"What is the code for {scenario['target_key']}?"
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": f"<DOC>\n{PLACEHOLDER}\n</DOC>\n{question}"},
    ]
    template = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        date_string=ACCEPTED_CHAT_TEMPLATE_DATE,
    )
    if template.count(PLACEHOLDER) != 1:
        raise ValueError("Chat template did not preserve the document placeholder exactly once")
    prefix_text, suffix_text = template.split(PLACEHOLDER)
    prefix_ids = _encode(tokenizer, prefix_text)
    suffix_ids = _encode(tokenizer, suffix_text)
    if len(suffix_ids) > FINAL_QUERY_WINDOW:
        raise ValueError("The question/template suffix exceeds its 32-token limit")

    document_budget = CONTEXT_TOKENS - len(prefix_ids) - len(suffix_ids)
    target_record = next(record for record in scenario["records"] if record["is_target"])
    distractors = [record for record in scenario["records"] if not record["is_target"]]
    target_ids = _encode(tokenizer, _record_text(target_record))
    target_start = round(scenario["depth"] * document_budget)
    after_budget = document_budget - target_start - len(target_ids)
    if target_start <= 0 or after_budget <= 0:
        raise ValueError("Target depth leaves no room on one side of the target record")

    rng = random.Random(scenario["seed"] + 17)
    rng.shuffle(distractors)
    before_count = round(scenario["depth"] * len(distractors))
    before_ids = _pack_region(
        tokenizer, distractors[:before_count], target_start, random.Random(scenario["seed"] + 31)
    )
    after_ids = _pack_region(
        tokenizer, distractors[before_count:], after_budget, random.Random(scenario["seed"] + 47)
    )
    input_ids = prefix_ids + before_ids + target_ids + after_ids + suffix_ids
    if len(input_ids) != CONTEXT_TOKENS:
        raise AssertionError("Prompt materialization failed the exact-length gate")
    return {
        "scenario_id": scenario["scenario_id"],
        "depth": scenario["depth"],
        "target_key": scenario["target_key"],
        "target_code": scenario["target_code"],
        "record_count": len(scenario["records"]),
        "context_tokens": CONTEXT_TOKENS,
        "document_tokens": document_budget,
        "target_start_document_token": target_start,
        "target_start_input_token": len(prefix_ids) + target_start,
        "target_record_tokens": len(target_ids),
        "realized_depth": target_start / document_budget,
        "query_window_tokens": len(suffix_ids),
        "input_ids_sha256": token_ids_hash(input_ids),
        "input_ids": input_ids,
    }


def build_prompts():
    """Return ``(tokenizer, prompts)`` after validating both accepted hashes."""
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_AWQ, revision=MODEL_AWQ_REVISION, trust_remote_code=True
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    manifest = build_semantic_manifest()
    prompts = [materialize_scenario(tokenizer, scenario) for scenario in manifest["scenarios"]]
    prompt_set_sha256 = canonical_hash([
        {"scenario_id": prompt["scenario_id"], "sha256": prompt["input_ids_sha256"]}
        for prompt in prompts
    ])
    if prompt_set_sha256 != EXPECTED_PROMPT_SET_SHA256:
        raise AssertionError(
            "Generated input IDs do not match accepted evidence. Verify the pinned tokenizer revision."
        )
    return tokenizer, prompts


def prompt_with_text(tokenizer, prompt):
    """Add a readable decoding while retaining canonical token IDs for inference."""
    return {
        **prompt,
        "prompt_text": tokenizer.decode(
            prompt["input_ids"], skip_special_tokens=False, clean_up_tokenization_spaces=False
        ),
    }


def prompts_as_markdown(tokenizer, prompts):
    """Render all inputs for inspection without the large token-ID arrays."""
    sections = [
        "# Frozen Llama Track A Hard-Retrieval Prompts",
        "",
        f"- Tokenizer: `{MODEL_AWQ}`",
        f"- Tokenizer revision: `{MODEL_AWQ_REVISION}`",
        f"- Semantic SHA-256: `{EXPECTED_SEMANTIC_SHA256}`",
        f"- Prompt-set SHA-256: `{EXPECTED_PROMPT_SET_SHA256}`",
        "- Every prompt has exactly 4,096 input tokens.",
    ]
    for prompt in prompts:
        prompt_text = tokenizer.decode(
            prompt["input_ids"], skip_special_tokens=False, clean_up_tokenization_spaces=False
        )
        sections.extend([
            "",
            f"## {prompt['scenario_id']}",
            "",
            f"- Target depth: {prompt['depth']}",
            f"- Target key: `{prompt['target_key']}`",
            f"- Expected activation code: `{prompt['target_code']}`",
            f"- Input-ID SHA-256: `{prompt['input_ids_sha256']}`",
            "",
            "```text",
            prompt_text,
            "```",
        ])
    return "\n".join(sections) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario-id", help="One scenario, for example d10-s00. Omit for all 60.")
    parser.add_argument(
        "--format", choices=("json", "markdown"), default="markdown",
        help="Use markdown for a human-readable prompt document (default: markdown).",
    )
    parser.add_argument("--output", type=Path, help="Output file path.")
    args = parser.parse_args()

    tokenizer, prompts = build_prompts()
    if args.scenario_id:
        prompts = [prompt for prompt in prompts if prompt["scenario_id"] == args.scenario_id]
        if not prompts:
            raise SystemExit(f"Unknown scenario ID: {args.scenario_id}")
    output_path = args.output or Path(
        "llama_hard_retrieval_prompts." + ("md" if args.format == "markdown" else "json")
    )
    if args.format == "markdown":
        output_path.write_text(prompts_as_markdown(tokenizer, prompts), encoding="utf-8")
    else:
        output = {
            "model_tokenizer": MODEL_AWQ,
            "tokenizer_revision": MODEL_AWQ_REVISION,
            "semantic_sha256": EXPECTED_SEMANTIC_SHA256,
            "prompt_set_sha256": EXPECTED_PROMPT_SET_SHA256,
            "prompts": [prompt_with_text(tokenizer, prompt) for prompt in prompts],
        }
        output_path.write_text(json.dumps(output, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"Wrote {len(prompts)} exact retrieval prompt(s) to {output_path}")
    for prompt in prompts:
        print(f"{prompt['scenario_id']}: expected answer {prompt['target_code']}")


if __name__ == "__main__":
    main()
