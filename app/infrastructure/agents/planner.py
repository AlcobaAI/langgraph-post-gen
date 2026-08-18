from __future__ import annotations

import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import settings
from app.costs import estimate_cost_usd
from app.prompts.agent_prompts import build_planner_system_prompt
from app.schemas.agents import CostEntry, ContentPlanOutput, GroundingContext, GroundingDoc
from app.schemas.pipeline import PlannerInput, PlannerResult
from app.tools.rag_tools import search_rag


class OpenAIContentPlanner:
    def __init__(self) -> None:
        llm = ChatOpenAI(
            model=settings.planner.model,
            temperature=settings.planner.temperature,
        )
        self.llm = llm.with_structured_output(ContentPlanOutput, include_raw=True)

    async def setup(self) -> object:
        return self

    def _should_retrieve(self, user_prompt: str) -> bool:
        text = user_prompt.strip()
        if not text:
            return False

        lower = text.lower()
        if any(keyword in lower for keyword in ["document", "docs", "pdf", "file", "knowledge base", "kb"]):
            return True

        word_count = len(re.findall(r"\w+", text))
        return word_count <= 12

    def _build_grounding(self, input_data: PlannerInput) -> GroundingContext | None:
        if not self._should_retrieve(input_data.user_prompt):
            return None

        retrieval_query = input_data.user_prompt.strip()
        try:
            response = search_rag(
                query=retrieval_query,
                tenant_id=input_data.tenant_id,
                project_id=input_data.project_id,
                limit=5,
            )
        except Exception:
            return GroundingContext(
                retrieval_query=retrieval_query,
                retriever="unavailable",
                collection_name="",
                retrieved_docs=[],
            )

        return GroundingContext(
            retrieval_query=retrieval_query,
            retriever=response.retriever,
            collection_name=response.collection_name,
            retrieved_docs=[
                GroundingDoc(
                    text=result.text,
                    source_ref=result.source_ref,
                    score=result.score,
                )
                for result in response.results
            ],
        )

    def _normalize_angles(self, raw_angles: list[str], requested_count: int, user_prompt: str) -> list[str]:
        cleaned = []
        seen = set()

        for angle in raw_angles:
            value = angle.strip()
            if not value:
                continue
            key = value.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(value)

        cleaned = cleaned[:requested_count]

        if not cleaned:
            base = user_prompt.strip() or "General content angle"
            cleaned = [base]

        while len(cleaned) < requested_count:
            if len(cleaned) == 1:
                cleaned.append(f"{cleaned[0]} - variation 2")
            else:
                cleaned.append(f"{cleaned[0]} - variation {len(cleaned) + 1}")

        return cleaned[:requested_count]

    async def plan(self, input_data: PlannerInput) -> PlannerResult:
        requested_count = max(1, input_data.angle_count)
        grounding = self._build_grounding(input_data)
        grounding_lines = ""
        if grounding and grounding.retrieved_docs:
            grounding_lines = (
                f"Grounding retrieval query: {grounding.retrieval_query}\n"
                f"Grounding docs: {[doc.model_dump() for doc in grounding.retrieved_docs]}\n"
            )

        response = await self.llm.ainvoke(
            [
                SystemMessage(
                    content=build_planner_system_prompt(
                        input_data.tenant_id,
                        input_data.project_id,
                    )
                ),
                HumanMessage(
                    content=(
                        f"User request: {input_data.user_prompt}\n"
                        f"{grounding_lines}"
                        f"Requested number of angles: {requested_count}\n"
                        f"Return exactly {requested_count} distinct content angle(s)."
                    )
                ),
            ]
        )
        parsed = response["parsed"]
        raw = response["raw"]
        usage = getattr(raw, "usage_metadata", {}) or {}
        prompt_tokens = usage.get("input_tokens", 0)
        completion_tokens = usage.get("output_tokens", 0)

        angles = self._normalize_angles(
            parsed.angles,
            requested_count,
            input_data.user_prompt,
        )

        return PlannerResult(
            plan=angles,
            grounding=grounding,
            cost_entries=[
                CostEntry(
                    stage="planner",
                    model=settings.planner.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=usage.get("total_tokens", 0),
                    total_cost_usd=estimate_cost_usd(
                        settings.planner.model,
                        prompt_tokens,
                        completion_tokens,
                    ),
                )
            ],
        )
