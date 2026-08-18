from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from pypdf import PdfReader


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_json_file(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    return json.dumps(data, ensure_ascii=True, indent=2)


def _read_pdf_file(path: Path) -> str:
    reader = PdfReader(str(path))
    pages: List[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text)

    return "\n\n".join(pages)


def _chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> Iterable[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    step = max(1, chunk_size - chunk_overlap)
    chunks: List[str] = []

    start = 0
    while start < len(cleaned):
        chunk = cleaned[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks


def load_documents(documents_dir: str, chunk_size: int, chunk_overlap: int) -> list[dict]:
    base_path = Path(documents_dir)
    if not base_path.exists():
        return []

    documents: list[dict] = []

    for path in sorted(base_path.rglob("*")):
        if not path.is_file():
            continue

        suffix = path.suffix.lower()
        if suffix not in {".txt", ".md", ".json", ".pdf"}:
            continue

        try:
            if suffix == ".json":
                text = _read_json_file(path)
            elif suffix == ".pdf":
                text = _read_pdf_file(path)
            else:
                text = _read_text_file(path)
        except Exception:
            continue

        for index, chunk in enumerate(_chunk_text(text, chunk_size, chunk_overlap)):
            documents.append(
                {
                    "id": f"{path.stem}-{index}",
                    "text": chunk,
                    "source_ref": str(path.relative_to(base_path)).replace("\\", "/"),
                }
            )

    return documents
