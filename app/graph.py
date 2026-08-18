from __future__ import annotations

import asyncio

from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph

from app.domain.protocols.editor import EditorProtocol
from app.domain.protocols.judge import JudgeProtocol
from app.domain.protocols.planner import PlannerProtocol
from app.domain.protocols.writer import WriterProtocol
from app.schemas.pipeline import EditorInput, JudgeInput, PlannerInput, WriterInput
from app.state import ContentState, WriterTask


async def setup_graph(
    *,
    planner: PlannerProtocol,
    writer: WriterProtocol,
    judge: JudgeProtocol,
    editor: EditorProtocol,
):
    await planner.setup()

    workflow = StateGraph(ContentState)

    async def planner_node(state: ContentState):
        result = await planner.plan(
            PlannerInput(
                user_prompt=state.get("user_prompt", ""),
                tenant_id=state.get("tenant_id", ""),
                project_id=state.get("project_id", "default"),
                angle_count=state.get("angle_count", 1),
            )
        )
        return {
            "plan": result.plan,
            "planner_grounding": result.grounding,
            "cost_entries": result.cost_entries,
        }

    workflow.add_node("planner", planner_node)

    async def process_angle(state: WriterTask):
        writer_result = await writer.write(
            WriterInput(
                angle=state["angle"],
                tenant_id=state["tenant_id"],
                project_id=state.get("project_id", "default"),
                user_prompt=state.get("user_prompt", ""),
            )
        )

        judge_result = await judge.evaluate_draft(
            JudgeInput(
                angle=state["angle"],
                tenant_id=state.get("tenant_id", ""),
                project_id=state.get("project_id", "default"),
                user_prompt=state.get("user_prompt", ""),
                draft=writer_result.draft,
                grounding=writer_result.grounding,
            )
        )

        editor_coroutines = [
            editor.edit(
                EditorInput(
                    angle=state["angle"],
                    artifact_id=state.get("artifact_id", ""),
                    user_id=state.get("user_id", ""),
                    generation_id=state.get("generation_id", ""),
                    tenant_id=state.get("tenant_id", ""),
                    project_id=state.get("project_id", "default"),
                    user_prompt=state.get("user_prompt", ""),
                    platform=target.platform,
                    personas=target.personas,
                    custom_persona=target.custom_persona,
                    draft=writer_result.draft,
                    evaluation=judge_result.evaluation,
                    planner_grounding=state.get("planner_grounding"),
                    writer_grounding=writer_result.grounding,
                )
            )
            for target in state.get("editor_targets", [])
        ]

        editor_results = await asyncio.gather(*editor_coroutines)

        posts = []
        cost_entries = []
        cost_entries.extend(writer_result.cost_entries)
        cost_entries.extend(judge_result.cost_entries)
        for result in editor_results:
            posts.extend([post.model_dump() for post in result.posts])
            cost_entries.extend(result.cost_entries)

        return {"posts": posts, "cost_entries": cost_entries}

    workflow.add_node("process_angle", process_angle)

    workflow.add_edge(START, "planner")

    def parallelize_angles(state: ContentState):
        plan = list(state.get("plan", []))
        editor_targets = list(state.get("editor_targets", []))

        if not plan or not editor_targets:
            return []

        return [
            Send(
                "process_angle",
                WriterTask(
                    angle=angle,
                    artifact_id=state["artifact_id"],
                    user_id=state["user_id"],
                    generation_id=state["generation_id"],
                    tenant_id=state["tenant_id"],
                    project_id=state["project_id"],
                    user_prompt=state["user_prompt"],
                    platforms=list(state.get("platforms", [])),
                    personas=list(state.get("personas", [])),
                    custom_persona=state.get("custom_persona"),
                    editor_targets=editor_targets,
                    planner_grounding=state.get("planner_grounding"),
                ),
            )
            for angle in plan
        ]

    workflow.add_conditional_edges("planner", parallelize_angles, ["process_angle"])
    workflow.add_edge("process_angle", END)

    return workflow.compile()
