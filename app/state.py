from __future__ import annotations

import operator
from typing import Annotated, Any, Dict, List, TypedDict

from app.schemas.agents import CostEntry, EvaluationOutput, GroundingContext, WriterDraft
from app.schemas.pipeline import EditorTarget


class Post(TypedDict):
    angle: str
    content: str
    graphics_prompt: str
    video_script: str
    status: str
    metadata: Dict[str, Any]


class ContentState(TypedDict, total=False):
    artifact_id: str
    user_id: str
    generation_id: str
    user_prompt: str
    tenant_id: str
    project_id: str
    angle_count: int
    platforms: List[str]
    personas: List[str]
    custom_persona: str | None
    editor_targets: List[EditorTarget]
    plan: List[str]
    planner_grounding: GroundingContext | None
    cost_entries: Annotated[List[CostEntry], operator.add]
    posts: Annotated[List[Post], operator.add]


class WriterTask(TypedDict):
    angle: str
    artifact_id: str
    user_id: str
    generation_id: str
    tenant_id: str
    project_id: str
    user_prompt: str
    platforms: List[str]
    personas: List[str]
    custom_persona: str | None
    editor_targets: List[EditorTarget]
    planner_grounding: GroundingContext | None


class EditorTask(TypedDict):
    angle: str
    artifact_id: str
    user_id: str
    generation_id: str
    tenant_id: str
    project_id: str
    user_prompt: str
    platform: str
    personas: List[str]
    custom_persona: str | None
    draft: WriterDraft
    evaluation: EvaluationOutput
    planner_grounding: GroundingContext | None
    writer_grounding: GroundingContext | None
