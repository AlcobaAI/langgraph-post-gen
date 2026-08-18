from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import settings
from app.costs import estimate_cost_usd
from app.prompts.agent_prompts import (
    build_judge_system_prompt,
    build_judge_user_prompt,
)
from app.schemas.agents import CostEntry, EvaluationOutput
from app.schemas.pipeline import JudgeInput, JudgeResult


class OpenAIJudgeAgent:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model=settings.judge.model,
            temperature=settings.judge.temperature,
        ).with_structured_output(EvaluationOutput, include_raw=True)

    async def evaluate_draft(self, input_data: JudgeInput) -> JudgeResult:
        response = await self.llm.ainvoke(
            [
                SystemMessage(
                    content=build_judge_system_prompt(
                        input_data.tenant_id,
                        input_data.project_id,
                    )
                ),
                HumanMessage(
                    content=build_judge_user_prompt(
                        input_data.angle,
                        input_data.user_prompt,
                        input_data.draft.model_dump(),
                        input_data.grounding.model_dump() if input_data.grounding else None,
                    )
                ),
            ]
        )
        evaluation = response["parsed"]
        raw = response["raw"]
        usage = getattr(raw, "usage_metadata", {}) or {}
        prompt_tokens = usage.get("input_tokens", 0)
        completion_tokens = usage.get("output_tokens", 0)
        return JudgeResult(
            evaluation=evaluation,
            cost_entries=[
                CostEntry(
                    stage="judge",
                    model=settings.judge.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=usage.get("total_tokens", 0),
                    total_cost_usd=estimate_cost_usd(
                        settings.judge.model,
                        prompt_tokens,
                        completion_tokens,
                    ),
                )
            ],
        )
