from __future__ import annotations

from typing import Protocol

from app.schemas.pipeline import PlannerInput, PlannerResult


class PlannerProtocol(Protocol):
    async def setup(self) -> object: ...
    async def plan(self, input_data: PlannerInput) -> PlannerResult: ...