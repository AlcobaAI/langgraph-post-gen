from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import settings
from app.costs import estimate_cost_usd
from app.prompts.agent_prompts import (
    build_writer_system_prompt,
    build_writer_user_prompt,
)
from app.schemas.agents import CostEntry, GroundingContext, GroundingDoc, WriterDraft
from app.schemas.pipeline import WriterInput, WriterResult
from app.tools.rag_tools import search_rag


class OpenAIWriterAgent:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model=settings.writer.model,
            temperature=settings.writer.temperature,
        ).with_structured_output(WriterDraft, include_raw=True)

    def _build_grounding(self, input_data: WriterInput) -> GroundingContext:
        retrieval_query = (
            f"User request: {input_data.user_prompt}\n"
            f"Angle: {input_data.angle}\n"
            "Find grounding context that supports writing this draft."
        ).strip()
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

    async def write(self, input_data: WriterInput) -> WriterResult:
        grounding = self._build_grounding(input_data)
        response = await self.llm.ainvoke(
            [
                SystemMessage(
                    content=build_writer_system_prompt(
                        input_data.tenant_id,
                        input_data.project_id,
                    )
                ),
                HumanMessage(
                    content=build_writer_user_prompt(
                        input_data.angle,
                        input_data.user_prompt,
                        input_data.tenant_id,
                        input_data.project_id,
                        grounding.model_dump(),
                    )
                ),
            ]
        )
        draft = response["parsed"]
        raw = response["raw"]
        usage = getattr(raw, "usage_metadata", {}) or {}
        prompt_tokens = usage.get("input_tokens", 0)
        completion_tokens = usage.get("output_tokens", 0)
        return WriterResult(
            draft=draft,
            grounding=grounding,
            cost_entries=[
                CostEntry(
                    stage="writer",
                    model=settings.writer.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=usage.get("total_tokens", 0),
                    total_cost_usd=estimate_cost_usd(
                        settings.writer.model,
                        prompt_tokens,
                        completion_tokens,
                    ),
                )
            ],
        )
