from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from app.schemas.agents import CostEntry, EvaluationOutput, GroundingContext, WriterDraft
from app.schemas.artifacts import PostArtifact


class PlannerInput(BaseModel):
    user_prompt: str = ""
    tenant_id: str = ""
    project_id: str = "default"
    angle_count: int = 1


class PlannerResult(BaseModel):
    plan: List[str]
    grounding: GroundingContext | None = None
    cost_entries: List[CostEntry] = Field(default_factory=list)


class WriterInput(BaseModel):
    angle: str
    tenant_id: str
    project_id: str = "default"
    user_prompt: str = ""


class WriterResult(BaseModel):
    draft: WriterDraft
    grounding: GroundingContext | None = None
    cost_entries: List[CostEntry] = Field(default_factory=list)


class JudgeInput(BaseModel):
    angle: str
    tenant_id: str = ""
    project_id: str = "default"
    user_prompt: str = ""
    draft: WriterDraft
    grounding: GroundingContext | None = None


class JudgeResult(BaseModel):
    evaluation: EvaluationOutput
    cost_entries: List[CostEntry] = Field(default_factory=list)


class EditorInput(BaseModel):
    angle: str
    artifact_id: str = ""
    user_id: str = ""
    generation_id: str = ""
    tenant_id: str = ""
    project_id: str = "default"
    user_prompt: str = ""
    platform: str = "linkedin"
    personas: List[str] = Field(default_factory=list)
    custom_persona: str | None = None
    draft: WriterDraft
    evaluation: EvaluationOutput
    planner_grounding: GroundingContext | None = None
    writer_grounding: GroundingContext | None = None


class EditorResult(BaseModel):
    posts: List[PostArtifact]
    cost_entries: List[CostEntry] = Field(default_factory=list)


class EditorTarget(BaseModel):
    platform: str
    personas: List[str] = Field(default_factory=list)
    custom_persona: str | None = None
