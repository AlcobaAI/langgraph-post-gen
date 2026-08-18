from typing import List
from pydantic import BaseModel, Field


class GroundingDoc(BaseModel):
    text: str = Field(description="Retrieved grounding text")
    source_ref: str = Field(description="Source reference for the retrieved grounding text")
    score: float | None = Field(default=None, description="Retriever score if available")


class GroundingContext(BaseModel):
    retrieval_query: str = Field(description="Query used to retrieve grounding context")
    retriever: str = Field(description="Retriever label or identifier")
    collection_name: str = Field(description="Backing collection name")
    retrieved_docs: List[GroundingDoc] = Field(
        default_factory=list,
        description="Retrieved grounding documents",
    )


class CostEntry(BaseModel):
    stage: str = Field(description="Workflow stage that produced the usage")
    model: str = Field(description="Model name used for the call")
    prompt_tokens: int = Field(default=0, description="Prompt/input token count")
    completion_tokens: int = Field(default=0, description="Completion/output token count")
    total_tokens: int = Field(default=0, description="Total token count")
    total_cost_usd: float = Field(default=0.0, description="Estimated USD cost for the call")


class ContentPlanOutput(BaseModel):
    angles: List[str] = Field(
        min_length=1,
        description="Distinct content angles to generate in parallel",
    )


class WriterDraft(BaseModel):
    title: str = Field(description="Short title for the post")
    hook: str = Field(description="Opening hook for the post")
    body: str = Field(description="Main post body")
    visual_ideas: List[str] = Field(description="Visual scenes or transitions")
    caption: str = Field(description="Social caption")
    hashtags: List[str] = Field(description="Relevant hashtags")
    call_to_action: str = Field(description="Specific call to action")
    image_prompt: str = Field(description="Prompt for the image generator")
    video_script: str = Field(description="Short video narration script")


class EvaluationOutput(BaseModel):
    is_relevant: bool = Field(description="Is the draft aligned to the requested angle?")
    reasoning: str = Field(description="Brief explanation of the audit result")
    missing_info: str = Field(description="Any missing information, if relevant")


class EditorOutput(BaseModel):
    content: str = Field(description="Final platform-specific post content in Markdown")
    graphics_prompt: str = Field(description="Prompt for the image generator")
    video_script: str = Field(description="Platform-specific video narration script")
