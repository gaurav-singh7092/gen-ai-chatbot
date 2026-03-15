from __future__ import annotations

from dataclasses import dataclass

from .config import Settings
from .indexer import load_index
from .llm import generate_answer
from .retriever import RetrievedChunk, TfidfRetriever


@dataclass(slots=True)
class ChatResult:
    answer: str
    retrieved_chunks: list[RetrievedChunk]


class GitLabHandbookChatbot:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self._chunks = load_index(self.settings.index_path)
        self._retriever = TfidfRetriever(self._chunks)

    @property
    def has_index(self) -> bool:
        return bool(self._chunks)

    @property
    def document_count(self) -> int:
        return len(self._chunks)

    def reload(self) -> None:
        self._chunks = load_index(self.settings.index_path)
        self._retriever = TfidfRetriever(self._chunks)

    def ask(self, question: str, history: list[dict[str, str]]) -> ChatResult:
        retrieved = self._retriever.search(question, top_k=self.settings.retrieval_k)
        answer = generate_answer(self.settings, question, history, retrieved)
        return ChatResult(answer=answer, retrieved_chunks=retrieved)
