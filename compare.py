"""compare.py — run a batch of prompts against Claude and GPT, aggregate results."""
import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI

from ask import ask_claude, ask_gpt


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Batch-compare Claude and GPT on a set of prompts.")
    parser.add_argument("--prompts", default="prompts/sample.json",
                        help="Path to prompts JSON file.")
    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY missing from .env")
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY missing from .env")

    prompts = json.loads(Path(args.prompts).read_text())
    print(f"Loaded {len(prompts)} prompts from {args.prompts}")

    anthropic_client = Anthropic()
    openai_client = OpenAI()

    records = []
    for i, item in enumerate(prompts, 1):
        print(f"[{i}/{len(prompts)}] {item['id']} ({item['category']})")

        claude_result = ask_claude(anthropic_client, item["prompt"])
        gpt_result = ask_gpt(openai_client, item["prompt"])

        records.append({
            "id": item["id"],
            "category": item["category"],
            "prompt": item["prompt"],
            "claude": {
                "text": claude_result.text,
                "input_tokens": claude_result.input_tokens,
                "output_tokens": claude_result.output_tokens,
                "latency_s": claude_result.latency_s,
            },
            "gpt": {
                "text": gpt_result.text,
                "input_tokens": gpt_result.input_tokens,
                "output_tokens": gpt_result.output_tokens,
                "latency_s": gpt_result.latency_s,
            },
        })

    Path("results").mkdir(exist_ok=True)
    Path("results/results.json").write_text(json.dumps(records, indent=2))
    print(f"\nWrote results/results.json ({len(records)} records)")


if __name__ == "__main__":
    main()