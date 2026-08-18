from __future__ import annotations


class NoOpRetriever:
    def __init__(self, label: str = "NoOp") -> None:
        self.label = label

    def search(self, query: str, limit: int = 5):
        return [], 0.0
