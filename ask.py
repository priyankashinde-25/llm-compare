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

def ask_claude(client: Anthropic, prompt: str, model: str = "claude-haiku-4-5",system: str | None = None) -> Result:
    """Send a prompt to Claude, return a Result with text + tokens + latency."""
    r = Result(provider="anthropic", model=model)

    t0 = time.time()
    kwargs = dict(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    if system:
        kwargs["system"] = system
    response = client.messages.create(**kwargs)
    r.latency_s = time.time() - t0

    r.text = response.content[0].text
    r.input_tokens = response.usage.input_tokens
    r.output_tokens = response.usage.output_tokens
    return r

def ask_gpt(client: OpenAI, prompt: str, model: str = "gpt-5-mini",system: str | None = None) -> Result:
    """Send a prompt to GPT, return a Result with text + tokens + latency."""
    r = Result(provider="openai", model=model)

    t0 = time.time()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    r.latency_s = time.time() - t0

    r.text = response.choices[0].message.content
    r.input_tokens = response.usage.prompt_tokens
    r.output_tokens = response.usage.completion_tokens
    return r

def stream_claude(client: Anthropic, prompt: str, model: str = "claude-haiku-4-5",system: str | None = None) -> Result:
    """Stream Claude's response, printing tokens as they arrive."""
    r = Result(provider="anthropic", model=model)
    print(f"\n--- Claude ({model}) ---")

    t0 = time.time()
    ttft = None
    kwargs = dict(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    if system:
        kwargs["system"] = system
    with client.messages.stream(**kwargs) as stream:
        for text in stream.text_stream:
            if ttft is None:
                ttft = time.time() - t0
            sys.stdout.write(text)
            sys.stdout.flush()
            r.text += text
        final = stream.get_final_message()
    print()  # newline after streaming finishes

    r.latency_s = time.time() - t0
    r.input_tokens = final.usage.input_tokens
    r.output_tokens = final.usage.output_tokens
    print(f"ttft={ttft:.2f}s  total={r.latency_s:.2f}s  "
          f"tokens in/out={r.input_tokens}/{r.output_tokens}")
    return r


def stream_gpt(client: OpenAI, prompt: str, model: str = "gpt-5-mini",
               system: str | None = None) -> Result:
    """Stream GPT's response, printing tokens as they arrive."""
    r = Result(provider="openai", model=model)
    print(f"\n--- GPT ({model}) ---")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    t0 = time.time()
    ttft = None
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
    )
    for chunk in stream:
        if chunk.choices:
            delta = chunk.choices[0].delta.content
            if delta:
                if ttft is None:
                    ttft = time.time() - t0
                sys.stdout.write(delta)
                sys.stdout.flush()
                r.text += delta
        if chunk.usage:
            r.input_tokens = chunk.usage.prompt_tokens
            r.output_tokens = chunk.usage.completion_tokens
    print()

    r.latency_s = time.time() - t0
    print(f"ttft={ttft:.2f}s  total={r.latency_s:.2f}s  "
          f"tokens in/out={r.input_tokens}/{r.output_tokens}")
    return r



def print_side_by_side(a: Result, b: Result, width: int = 60) -> None:
    """Print two Results in two aligned columns."""
    def wrap(text: str, w: int) -> list[str]:
        """Break `text` into lines no wider than `w` characters."""
        lines = []
        for paragraph in text.splitlines() or [""]:
            while len(paragraph) > w:
                cut = paragraph.rfind(" ", 0, w)
                if cut <= 0:
                    cut = w
                lines.append(paragraph[:cut])
                paragraph = paragraph[cut:].lstrip()
            lines.append(paragraph)
        return lines

    left_header = f"Claude ({a.model})"
    right_header = f"GPT ({b.model})"
    print(f"\n{left_header:<{width}}  | {right_header}")
    print(f"{'-' * width}  | {'-' * width}")

    left_lines = wrap(a.text, width)
    right_lines = wrap(b.text, width)
    for i in range(max(len(left_lines), len(right_lines))):
        left = left_lines[i] if i < len(left_lines) else ""
        right = right_lines[i] if i < len(right_lines) else ""
        print(f"{left:<{width}}  | {right}")

    print(f"{'-' * width}  | {'-' * width}")
    print(f"{'latency: ' + f'{a.latency_s:.2f}s':<{width}}  | latency: {b.latency_s:.2f}s")
    print(f"{'tokens in/out: ' + f'{a.input_tokens}/{a.output_tokens}':<{width}}  | "
          f"tokens in/out: {b.input_tokens}/{b.output_tokens}")



def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Ask Claude and GPT the same question.")
    parser.add_argument("prompt", help="The question to ask both models.")
    parser.add_argument("--stream", action="store_true", help="Stream tokens as they arrive.")
    parser.add_argument("--system", help="Optional system prompt to steer both models.")
    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY missing from .env")
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY missing from .env")

    anthropic_client = Anthropic()
    openai_client = OpenAI()

    # print("Asking Claude...")
    # claude_result = ask_claude(anthropic_client, args.prompt)

    # print("Asking GPT...")
    # gpt_result = ask_gpt(openai_client, args.prompt)

    # print_side_by_side(claude_result, gpt_result)

    if args.stream:
        claude_result = stream_claude(anthropic_client, args.prompt, system=args.system)
        gpt_result = stream_gpt(openai_client, args.prompt, system=args.system)
    else:
        print("Asking Claude...")
        claude_result = ask_claude(anthropic_client, args.prompt, system=args.system)
        print("Asking GPT...")
        gpt_result = ask_gpt(openai_client, args.prompt, system=args.system)
        print_side_by_side(claude_result, gpt_result)


if __name__ == "__main__":
    main()