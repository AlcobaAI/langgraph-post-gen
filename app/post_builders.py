from __future__ import annotations

from typing import Any, Dict

from app.schemas.agents import GroundingContext
from app.schemas.artifacts import PostArtifact


def _serialize_grounding(grounding: GroundingContext | None) -> Dict[str, Any] | None:
    if not grounding:
        return None
    return grounding.model_dump()


def _collect_source_refs(*groundings: GroundingContext | None) -> list[str]:
    refs: list[str] = []
    seen = set()

    for grounding in groundings:
        if not grounding:
            continue
        for doc in grounding.retrieved_docs:
            ref = doc.source_ref.strip()
            if not ref or ref in seen:
                continue
            seen.add(ref)
            refs.append(ref)

    return refs


def build_post_metadata(
    *,
    artifact_id: str,
    user_id: str,
    generation_id: str,
    tenant_id: str,
    project_id: str,
    platform: str,
    personas: list[str],
    evaluation: Dict[str, Any],
    planner_grounding: GroundingContext | None = None,
    writer_grounding: GroundingContext | None = None,
) -> Dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "user_id": user_id,
        "generation_id": generation_id,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "platform": platform,
        "personas": personas,
        "judge": evaluation,
        "retrieval": {
            "planner": _serialize_grounding(planner_grounding),
            "writer": _serialize_grounding(writer_grounding),
        },
        "grounding_source_refs": _collect_source_refs(planner_grounding, writer_grounding),
    }


def build_completed_post(
    *,
    angle: str,
    content: str,
    graphics_prompt: str,
    video_script: str,
    metadata: Dict[str, Any],
) -> PostArtifact:
    return PostArtifact(
        angle=angle,
        content=content,
        graphics_prompt=graphics_prompt,
        video_script=video_script,
        status="completed",
        metadata=metadata,
    )


def build_skipped_post(
    *,
    angle: str,
    content: str,
    metadata: Dict[str, Any],
) -> PostArtifact:
    return PostArtifact(
        angle=angle,
        content=content,
        graphics_prompt="",
        video_script="",
        status="skipped",
        metadata=metadata,
    )
