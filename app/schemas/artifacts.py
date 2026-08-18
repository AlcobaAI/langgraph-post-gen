from typing import Any, Dict, Literal
from pydantic import BaseModel, Field


class PostArtifact(BaseModel):
    angle: str
    content: str
    graphics_prompt: str
    video_script: str
    status: Literal["completed", "skipped"]
    metadata: Dict[str, Any] = Field(default_factory=dict)