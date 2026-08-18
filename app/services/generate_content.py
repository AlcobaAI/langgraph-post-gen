import uuid
from time import perf_counter
from typing import Any, Dict, List, cast

from app.graph import setup_graph
from app.infrastructure.agents.editor import OpenAIEditorAgent
from app.infrastructure.agents.judge import OpenAIJudgeAgent
from app.infrastructure.agents.planner import OpenAIContentPlanner
from app.infrastructure.agents.writer import OpenAIWriterAgent
from app.prompts.persona_prompts import DEFAULT_PERSONA, normalize_persona
from app.prompts.platform_prompts import normalize_platform
from app.schemas.agents import CostEntry
from app.schemas.api import AiGenerateInput, AiGenerateOutput
from app.schemas.pipeline import EditorTarget
from app.state import ContentState


class GenerateContentService:
    def __init__(self) -> None:
        self._resources: Dict[str, Any] = {}

    async def startup(self) -> None:
        print("Compiling AI Graph...")

        planner = OpenAIContentPlanner()
        writer = OpenAIWriterAgent()
        judge = OpenAIJudgeAgent()
        editor = OpenAIEditorAgent()

        self._resources["graph"] = await setup_graph(
            planner=planner,
            writer=writer,
            judge=judge,
            editor=editor,
        )

    def _get_graph(self) -> Any:
        graph = self._resources.get("graph")
        if not graph:
            raise RuntimeError("Graph not ready")
        return graph

    def _normalize_platforms(self, input_data: AiGenerateInput) -> List[str]:
        raw_platforms: List[str] = []

        if input_data.platforms:
            raw_platforms.extend(input_data.platforms)

        if input_data.platform:
            raw_platforms.append(input_data.platform)

        if not raw_platforms:
            raw_platforms = ["linkedin"]

        normalized: List[str] = []
        seen = set()

        for platform in raw_platforms:
            value = normalize_platform(platform)
            if not value:
                continue
            if value in seen:
                continue
            seen.add(value)
            normalized.append(value)

        return normalized or ["linkedin"]

    def _build_initial_state(
        self,
        input_data: AiGenerateInput,
        generation_id: str,
    ) -> ContentState:
        editor_targets: list[EditorTarget] = []

        if input_data.platformPersonaPairs:
            for pair in input_data.platformPersonaPairs:
                editor_targets.append(
                    EditorTarget(
                        platform=normalize_platform(pair.platform),
                        personas=[normalize_persona(pair.persona)] if pair.persona else [],
                        custom_persona=pair.customPersona,
                    )
                )
        else:
            platforms = self._normalize_platforms(input_data)
            personas = [
                normalize_persona(persona)
                for persona in (input_data.personas or [input_data.persona or DEFAULT_PERSONA])
            ]
            for platform in platforms:
                editor_targets.append(
                    EditorTarget(
                        platform=platform,
                        personas=personas,
                        custom_persona=input_data.customPersona,
                    )
                )

        platforms = []
        personas = []
        for target in editor_targets:
            if target.platform not in platforms:
                platforms.append(target.platform)
            for persona in target.personas:
                if persona not in personas:
                    personas.append(persona)

        return cast(
            ContentState,
            {
                "artifact_id": input_data.artifactId,
                "user_id": input_data.userId,
                "generation_id": generation_id,
                "user_prompt": input_data.userPrompt,
                "tenant_id": input_data.tenantId,
                "project_id": input_data.projectId or "default",
                "angle_count": max(1, input_data.angleCount),
                "platforms": platforms,
                "personas": personas,
                "custom_persona": input_data.customPersona,
                "editor_targets": editor_targets,
                "plan": [],
                "planner_grounding": None,
                "cost_entries": [],
                "posts": [],
            },
        )

    def _summarize_costs(self, cost_entries: list[CostEntry]) -> tuple[float, list[CostEntry]]:
        total_cost_usd = sum(entry.total_cost_usd for entry in cost_entries)
        return total_cost_usd, cost_entries

    async def generate(self, input_data: AiGenerateInput) -> AiGenerateOutput:
        graph = self._get_graph()
        generation_id = str(uuid.uuid4())
        initial_state = self._build_initial_state(input_data, generation_id)

        start_time = perf_counter()
        final_state = await graph.ainvoke(initial_state)
        duration_ms = (perf_counter() - start_time) * 1000
        cost_entries = final_state.get("cost_entries", [])
        total_cost_usd, cost_breakdown = self._summarize_costs(cost_entries)

        return AiGenerateOutput(
            result="Success" if final_state.get("posts") else "No posts generated",
            artifacts=final_state.get("posts", []),
            generationId=generation_id,
            durationMs=duration_ms,
            totalCostUsd=total_cost_usd,
            costBreakdown=cost_breakdown,
        )
