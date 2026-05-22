
# LLM Comparison Harness — Claude vs GPT-4

A CLI tool that fires any prompt at both Anthropic (Claude Haiku 3.5) and OpenAI (GPT-3.5-turbo) simultaneously, streams both responses in real time, and logs latency, token counts, and cost per call. Results below are from a structured benchmark across 10 prompts covering factual retrieval, creative writing, reasoning, coding, and customer-support classification.

---

## Quickstart

```bash
# Install dependencies
pip install anthropic openai
npm install @anthropic-ai/sdk openai

# Set API keys (never hardcode)
export ANTHROPIC_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here

# Run a prompt against both models
python ask.py "Explain what a transformer model is"

# Stream tokens as they arrive
python ask.py --stream "Write a short poem about debugging at 2am"

# Add a system prompt
python ask.py --system "You are a senior Python engineer" "Review this function for edge cases"
```

---

## Benchmark Results — 10 Prompts

All runs were single-turn, no caching, measured on the same machine. Costs use published pricing as of mid-2025: Claude Haiku 3.5 at $0.80/$4.00 per million tokens (input/output); GPT-3.5-turbo at $0.50/$1.50 per million tokens.

| # | Category | Prompt (abbreviated) | Claude Latency | GPT Latency | Claude Tokens | GPT Tokens | Claude Cost | GPT Cost | Quality Notes |
|---|----------|----------------------|---------------|-------------|---------------|------------|-------------|----------|---------------|
| 1 | Factual | Mitochondria explained | 1.72s | 6.22s | 125 | 189 | $0.00043 | $0.00026 | Both correct. Claude more structured; GPT added evolutionary context. |
| 2 | Factual | TCP vs UDP differences | 1.21s | 5.53s | 90 | 307 | $0.00030 | $0.00044 | Both correct. Claude concise and formatted; GPT verbose with extra detail. |
| 3 | Creative | Poem: overworked coffee mug | 1.43s | 5.33s | 82 | 333 | $0.00025 | $0.00048 | Subjective. Claude more lyrical; GPT more imagistic and experimental. |
| 4 | Creative | Brand name + tagline (biodegradable case) | 0.92s | 9.53s | 50 | 766 | $0.00010 | $0.00113 | Claude: one sharp answer. GPT: five options unprompted — useful but verbose. |
| 5 | Reasoning | Bat-and-ball problem | 2.04s | 6.08s | 152 | 518 | $0.00046 | $0.00073 | Both correct. Claude showed algebra clearly; GPT slightly wordier. |
| 6 | Reasoning | 100 machines / 100 widgets | 2.01s | 5.63s | 166 | 347 | $0.00054 | $0.00049 | Both correct. Claude explained the proportionality insight well. |
| 7 | Coding | Python `is_palindrome()` | 0.90s | 5.15s | 101 | 404 | $0.00026 | $0.00057 | Both correct and idiomatic. Claude returned clean fenced code only. |
| 8 | Coding | SQL: second-highest salary | 0.92s | 14.85s | 73 | 453 | $0.00017 | $0.00064 | Both correct. GPT latency spike notable (14.8s). Claude returned query only as asked. |
| 9 | Classification | "Charged twice" → billing | 0.82s | 2.15s | 54 | 120 | $0.00006 | $0.00013 | Both correct. Claude used 4 output tokens; GPT used 74 for the same single label. |
| 10 | Classification | "App crashes on Android 14" → technical | 1.03s | 1.12s | 54 | 58 | $0.00006 | $0.00004 | Both correct. Only prompt where token counts were comparable. |

---

## Aggregate Summary

| Metric | Claude Haiku 3.5 | GPT-3.5-turbo |
|--------|-----------------|---------------|
| Average latency | **1.30s** | 6.16s |
| Total input tokens | 364 | 326 |
| Total output tokens | **583** | 3,169 |
| Total tokens | **947** | 3,495 |
| Total cost (10 prompts) | **$0.0026** | $0.0049 |
| Accuracy (all prompts) | 10/10 | 10/10 |

Claude was **4.7× faster** on average and **1.9× cheaper** across this benchmark. GPT-3.5-turbo produced significantly more output tokens — sometimes useful (reasoning steps, multiple creative options), often not (74 tokens to return a single classification label).

---

## Key Observations

**Latency.** Claude was faster on every single prompt. The gap was largest on coding tasks — GPT took 14.8 seconds on the SQL prompt vs Claude's 0.92 seconds. For any user-facing product, this difference is felt.

**Token efficiency.** Claude followed instructions more literally. When asked for a single label, it returned one word (4 tokens). When asked for just a function, it returned just the function. GPT consistently generated preamble, alternatives, or follow-up offers — even when not asked. This matters at scale: more output tokens = higher cost and slower response.

**Accuracy.** Both models answered all 10 prompts correctly. On this benchmark, accuracy was not a differentiator. Evaluation was objective where possible (math, code, classification) and qualitative for creative tasks.

**Creative quality.** This is genuinely subjective. GPT's poem (prompt 3) was more experimental; Claude's was more polished. Neither is objectively better.

**Streaming UX.** Anthropic's Python SDK has a cleaner streaming interface. The `with client.messages.stream()` context manager handles backpressure and cleanup more gracefully than OpenAI's equivalent. Meaningful for production applications.

---

## Recommendation: Cheapest Accurate Model for Customer-Support Classification

**Use Claude Haiku 3.5.**

For a startup running high-volume customer-support classification, three things matter above all else: accuracy, cost per call, and latency. On this benchmark, both models were equally accurate — so cost and speed determine the winner.

Claude Haiku 3.5 returned the correct classification label using 4 output tokens. GPT-3.5-turbo returned the same correct label using 74 output tokens on one prompt and 10 on another. That variance in output length is unpredictable and directly inflates your bill. At 100,000 classifications per day, that token inefficiency compounds into a meaningful cost difference — even though GPT-3.5-turbo has a lower output token price per million.

Claude was also 4.7× faster on average. For classification pipelines that run synchronously in a support ticket flow, sub-second responses keep the product feeling responsive.

The practical recommendation: use Claude Haiku 3.5 for classification with a tightly scoped system prompt that enforces single-label output. Measure output token counts in production and set up cost alerts early. If you later need multi-turn reasoning or nuanced tone judgment in responses, re-evaluate with Claude Sonnet or GPT-4o at that point — but for classification specifically, Haiku is the right call today.

---

## Project Structure

```
.
├── ask.py                  # CLI tool — prompts both models, prints side-by-side
├── run_benchmark.py        # Runs 10 sample prompts, saves results to JSON
├── results/
│   └── benchmark.json      # Raw results with tokens, latency, cost per prompt
├── requirements.txt        # Python dependencies
├── package.json            # Node dependencies
├── .env.example            # Template for environment variables
├── .gitignore              # Excludes .env, __pycache__, node_modules
└── README.md
```

## Requirements

```
# requirements.txt
anthropic>=0.25.0
openai>=1.30.0
```

```
# package.json (dependencies)
"@anthropic-ai/sdk": "^0.21.0"
"openai": "^4.47.0"
```

---

## Notes

- All benchmark runs used default temperature settings for both providers.
- Costs are estimates based on published pricing and may vary with API tier or promotional rates.
- SQLite caching is implemented — re-running any prompt from `benchmark.json` skips the API call entirely.
- No API keys appear anywhere in this repository. Use `.env` or shell exports only.

---

*Built as part of a hands-on LLM API project. Full benchmark data in `results/benchmark.json`.*