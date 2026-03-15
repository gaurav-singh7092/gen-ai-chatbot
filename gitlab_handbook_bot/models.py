from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(slots=True)
class SourceDocument:
    url: str
    title: str
    content: str
    section: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(slots=True)
class ChunkRecord:
    chunk_id: str
    url: str
    title: str
    section: str
    content: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
