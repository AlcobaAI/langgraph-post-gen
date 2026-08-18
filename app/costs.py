from __future__ import annotations


MODEL_PRICING_PER_1M_TOKENS: dict[str, dict[str, float]] = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


def estimate_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    pricing = MODEL_PRICING_PER_1M_TOKENS.get(model)
    if not pricing:
        return 0.0

    input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost
