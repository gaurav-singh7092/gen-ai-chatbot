from __future__ import annotations

import json
from pathlib import Path

from .chunking import chunk_documents
from .config import DATA_DIR, Settings
from .crawler import crawl_sources
from .models import ChunkRecord


def build_index(settings: Settings, max_pages: int) -> list[ChunkRecord]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    documents = crawl_sources(settings=settings, max_pages=max_pages)
    chunks = chunk_documents(
        documents=documents,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    save_index(chunks, settings.index_path)
    return chunks


def save_index(chunks: list[ChunkRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk.to_dict(), ensure_ascii=True) + "\n")


def load_index(path: Path) -> list[ChunkRecord]:
    if not path.exists():
        return []
    chunks: list[ChunkRecord] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            chunks.append(ChunkRecord(**row))
    return chunks
