from __future__ import annotations

from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import settings
from app.costs import estimate_cost_usd
from app.post_builders import (
    build_completed_post,
    build_post_metadata,
    build_skipped_post,
)
from app.prompts.agent_prompts import (
    build_editor_system_prompt,
    build_editor_user_prompt,
)
from app.schemas.agents import CostEntry, EditorOutput
from app.schemas.pipeline import EditorInput, EditorResult


class OpenAIEditorAgent:
    def __init__(self) -> None:
        llm = ChatOpenAI(
            model=settings.editor.model,
            temperature=settings.editor.temperature,
        )
        self.llm = llm.with_structured_output(EditorOutput, include_raw=True)

    def render_skipped(self, angle: str, reasoning: str, missing_info: str) -> str:
        lines: List[str] = [
            f"# {angle}",
            "",
            "> Skipped by judge",
            "",
            f"Reason: {reasoning}",
        ]
        if missing_info:
            lines.extend(["", f"Missing info: {missing_info}"])
        return "\n".join(lines).strip()

    async def edit(self, input_data: EditorInput) -> EditorResult:
        metadata = build_post_metadata(
            artifact_id=input_data.artifact_id,
            user_id=input_data.user_id,
            generation_id=input_data.generation_id,
            tenant_id=input_data.tenant_id,
            project_id=input_data.project_id,
            platform=input_data.platform,
            personas=input_data.personas,
            evaluation=input_data.evaluation.model_dump(),
            planner_grounding=input_data.planner_grounding,
            writer_grounding=input_data.writer_grounding,
        )

        if not input_data.evaluation.is_relevant:
            content = self.render_skipped(
                input_data.angle,
                input_data.evaluation.reasoning,
                input_data.evaluation.missing_info,
            )
            return EditorResult(
                posts=[
                    build_skipped_post(
                        angle=input_data.angle,
                        content=content,
                        metadata=metadata,
                    )
                ],
                cost_entries=[],
            )

        response = await self.llm.ainvoke(
            [
                SystemMessage(
                    content=build_editor_system_prompt(
                        input_data.platform,
                        input_data.personas,
                        input_data.custom_persona,
                        input_data.tenant_id,
                        input_data.project_id,
                    )
                ),
                HumanMessage(
                    content=build_editor_user_prompt(
                        angle=input_data.angle,
                        user_prompt=input_data.user_prompt,
                        platform=input_data.platform,
                        personas=input_data.personas,
                        custom_persona=input_data.custom_persona,
                        draft=input_data.draft.model_dump(),
                    )
                ),
            ]
        )
        edited = response["parsed"]
        raw = response["raw"]
        usage = getattr(raw, "usage_metadata", {}) or {}
        prompt_tokens = usage.get("input_tokens", 0)
        completion_tokens = usage.get("output_tokens", 0)

        return EditorResult(
            posts=[
                build_completed_post(
                    angle=input_data.angle,
                    content=edited.content,
                    graphics_prompt=edited.graphics_prompt,
                    video_script=edited.video_script,
                    metadata=metadata,
                )
            ],
            cost_entries=[
                CostEntry(
                    stage=f"editor:{input_data.platform}",
                    model=settings.editor.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=usage.get("total_tokens", 0),
                    total_cost_usd=estimate_cost_usd(
                        settings.editor.model,
                        prompt_tokens,
                        completion_tokens,
                    ),
                )
            ],
        )
