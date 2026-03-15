from __future__ import annotations

from .models import ChunkRecord, SourceDocument


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    normalized = " ".join(text.split())
    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    step = max(chunk_size - chunk_overlap, 1)
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(normalized):
            break
        start = max(end - chunk_overlap, start + step)
    return chunks


def chunk_documents(documents: list[SourceDocument], chunk_size: int, chunk_overlap: int) -> list[ChunkRecord]:
    chunks: list[ChunkRecord] = []
    for document in documents:
        for index, chunk in enumerate(split_text(document.content, chunk_size, chunk_overlap)):
            chunks.append(
                ChunkRecord(
                    chunk_id=f"{document.section}-{len(chunks) + 1}",
                    url=document.url,
                    title=document.title,
                    section=document.section,
                    content=chunk,
                )
            )
    return chunks
