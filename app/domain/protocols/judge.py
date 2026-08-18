from __future__ import annotations

from typing import Protocol

from app.schemas.pipeline import JudgeInput, JudgeResult


class JudgeProtocol(Protocol):
    async def evaluate_draft(self, input_data: JudgeInput) -> JudgeResult: ...