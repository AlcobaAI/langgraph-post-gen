from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.artifacts import PostArtifact
from app.schemas.agents import CostEntry
from app.prompts.persona_prompts import (
    CUSTOM_PERSONA_KEY,
    DEFAULT_PERSONA,
    list_personas,
    normalize_persona,
)
from app.prompts.platform_prompts import normalize_platform


class PlatformPersonaPair(BaseModel):
    platform: str
    persona: Optional[str] = None
    customPersona: Optional[str] = None


class AiGenerateInput(BaseModel):
    artifactId: str
    tenantId: str
    userId: str
    userPrompt: str
    projectId: Optional[str] = None
    platform: Optional[str] = None
    platforms: Optional[List[str]] = None
    persona: Optional[str] = None
    personas: Optional[List[str]] = None
    customPersona: Optional[str] = None
    platformPersonaPairs: Optional[List[PlatformPersonaPair]] = None
    angleCount: int = Field(default=1, ge=1)
    responseFormat: str = "text"
    stream: bool = False

    @model_validator(mode="after")
    def validate_personas(self) -> "AiGenerateInput":
        available = set(list_personas())

        if self.platformPersonaPairs:
            normalized_pairs: list[PlatformPersonaPair] = []
            seen_pairs = set()

            for pair in self.platformPersonaPairs:
                normalized_platform = normalize_platform(pair.platform)
                has_builtin = bool(pair.persona)
                has_custom = bool(pair.customPersona and pair.customPersona.strip())
                if has_builtin == has_custom:
                    raise ValueError(
                        "Each platformPersonaPair must include exactly one of 'persona' or 'customPersona'."
                    )
                normalized_persona = CUSTOM_PERSONA_KEY
                if has_builtin:
                    normalized_persona = normalize_persona(pair.persona or "")
                if normalized_persona != CUSTOM_PERSONA_KEY and normalized_persona not in available:
                    raise ValueError(
                        f"Unsupported persona '{pair.persona}'. Supported personas: {', '.join(sorted(available))}"
                    )
                pair_key = (normalized_platform, normalized_persona, (pair.customPersona or "").strip())
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)
                normalized_pairs.append(
                    PlatformPersonaPair(
                        platform=normalized_platform,
                        persona=None if normalized_persona == CUSTOM_PERSONA_KEY else normalized_persona,
                        customPersona=(pair.customPersona or "").strip() or None,
                    )
                )

            self.platformPersonaPairs = normalized_pairs
            return self

        raw_values: list[str] = []

        if self.personas:
            raw_values.extend(self.personas)
        if self.persona:
            raw_values.append(self.persona)
        if self.customPersona and self.customPersona.strip():
            raw_values.append(CUSTOM_PERSONA_KEY)

        if not raw_values:
            if self.customPersona and self.customPersona.strip():
                self.personas = [CUSTOM_PERSONA_KEY]
                self.persona = CUSTOM_PERSONA_KEY
            else:
                self.personas = [DEFAULT_PERSONA]
                self.persona = DEFAULT_PERSONA
            return self

        normalized: list[str] = []
        seen = set()
        for value in raw_values:
            key = normalize_persona(value)
            if key != CUSTOM_PERSONA_KEY and key not in available:
                raise ValueError(
                    f"Unsupported persona '{value}'. Supported personas: {', '.join(sorted(available))}"
                )
            if key in seen:
                continue
            seen.add(key)
            normalized.append(key)

        self.personas = normalized
        self.persona = normalized[0]
        return self


class AiGenerateOutput(BaseModel):
    result: str
    generationId: str
    durationMs: float
    totalCostUsd: float = 0.0
    costBreakdown: List[CostEntry] = Field(default_factory=list)
    artifacts: List[PostArtifact]
