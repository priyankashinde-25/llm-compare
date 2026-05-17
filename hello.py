"""hello.py — smoke test that both API keys work."""
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI

# Load keys from .env into environment variables
load_dotenv()

# Quick check that keys are present (not their values, just that they exist)
assert os.getenv("ANTHROPIC_API_KEY"), "ANTHROPIC_API_KEY missing from .env"
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY missing from .env"

# --- Ask Claude ---
print("Calling Claude...")
anthropic_client = Anthropic()
claude_reply = anthropic_client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hello in exactly 5 words."}],
)
print("Claude says:", claude_reply.content[0].text)

# --- Ask GPT ---
print("\nCalling GPT...")
openai_client = OpenAI()
gpt_reply = openai_client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": "Say hello in exactly 5 words."}],
)
print("GPT says:", gpt_reply.choices[0].message.content)