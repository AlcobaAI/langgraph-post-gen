from __future__ import annotations

from typing import Protocol

from app.schemas.pipeline import WriterInput, WriterResult


class WriterProtocol(Protocol):
    async def write(self, input_data: WriterInput) -> WriterResult: ...