from pydantic import BaseModel, Field
from typing import List

class SetContentPlan(BaseModel):
    hook: str = Field(description="The first 1-3 seconds of the reel")
    script: str = Field(description="The spoken narration (15-60 seconds)")
    visual_ideas: List[str] = Field(description="Descriptions of scenes and transitions")
    caption: str = Field(description="The social media caption (1-5 paragraphs)")
    hashtags: List[str] = Field(description="5-12 relevant hashtags")
    call_to_action: str = Field(description="Specific engagement instruction")