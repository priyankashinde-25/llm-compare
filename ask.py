"""ask.py — ask Claude and GPT the same question, compare answers."""
import argparse
import os
import sys
import time
from dataclasses import dataclass

from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI


@dataclass
class Result:
    """Holds everything we want to know about one model's response."""
    provider: str        # "anthropic" or "openai"
    model: str           # e.g. "claude-haiku-4-5"
    text: str = ""       # the actual reply
    input_tokens: int = 0
    output_tokens: int = 0
    latency_s: float = 0.0

def ask_claude(client: Anthropic, prompt: str, model: str = "claude-haiku-4-5") -> Result:
    """Send a prompt to Claude, return a Result with text + tokens + latency."""
    r = Result(provider="anthropic", model=model)

    t0 = time.time()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    r.latency_s = time.time() - t0

    r.text = response.content[0].text
    r.input_tokens = response.usage.input_tokens
    r.output_tokens = response.usage.output_tokens
    return r

def ask_gpt(client: OpenAI, prompt: str, model: str = "gpt-5-mini") -> Result:
    """Send a prompt to GPT, return a Result with text + tokens + latency."""
    r = Result(provider="openai", model=model)

    t0 = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    r.latency_s = time.time() - t0

    r.text = response.choices[0].message.content
    r.input_tokens = response.usage.prompt_tokens
    r.output_tokens = response.usage.completion_tokens
    return r

def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Ask Claude and GPT the same question.")
    parser.add_argument("prompt", help="The question to ask both models.")
    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY missing from .env")
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY missing from .env")

    anthropic_client = Anthropic()
    openai_client = OpenAI()

    print("Asking Claude...")
    claude_result = ask_claude(anthropic_client, args.prompt)

    print("Asking GPT...")
    gpt_result = ask_gpt(openai_client, args.prompt)

    print("\n--- Claude ---")
    print(claude_result.text)
    print(f"latency={claude_result.latency_s:.2f}s  "
          f"tokens in/out={claude_result.input_tokens}/{claude_result.output_tokens}")

    print("\n--- GPT ---")
    print(gpt_result.text)
    print(f"latency={gpt_result.latency_s:.2f}s  "
          f"tokens in/out={gpt_result.input_tokens}/{gpt_result.output_tokens}")


if __name__ == "__main__":
    main()