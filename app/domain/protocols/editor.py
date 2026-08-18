from __future__ import annotations

from typing import Protocol

from app.schemas.pipeline import EditorInput, EditorResult


class EditorProtocol(Protocol):
    async def edit(self, input_data: EditorInput) -> EditorResult: ...