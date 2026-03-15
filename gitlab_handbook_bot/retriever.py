from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from .models import ChunkRecord


@dataclass(slots=True)
class RetrievedChunk:
    chunk: ChunkRecord
    score: float


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class TfidfRetriever:
    def __init__(self, chunks: list[ChunkRecord]) -> None:
        self._chunks = chunks
        self._doc_tokens = [tokenize(chunk.content) for chunk in chunks]
        self._doc_term_counts = [Counter(tokens) for tokens in self._doc_tokens]
        self._doc_lengths = [math.sqrt(sum(count * count for count in counts.values())) or 1.0 for counts in self._doc_term_counts]
        self._idf = self._build_idf(self._doc_tokens)

    def _build_idf(self, tokenized_documents: list[list[str]]) -> dict[str, float]:
        doc_count = len(tokenized_documents)
        document_frequencies: Counter[str] = Counter()
        for tokens in tokenized_documents:
            document_frequencies.update(set(tokens))
        return {
            term: math.log((doc_count + 1) / (frequency + 1)) + 1.0
            for term, frequency in document_frequencies.items()
        }

    def search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        if not self._chunks:
            return []

        query_counts = Counter(tokenize(query))
        if not query_counts:
            return []

        query_norm = math.sqrt(
            sum((count * self._idf.get(term, 0.0)) ** 2 for term, count in query_counts.items())
        ) or 1.0

        scored_indexes: list[tuple[int, float]] = []
        for index, document_counts in enumerate(self._doc_term_counts):
            numerator = 0.0
            for term, query_count in query_counts.items():
                if term not in document_counts:
                    continue
                idf = self._idf.get(term, 0.0)
                numerator += (query_count * idf) * (document_counts[term] * idf)
            score = numerator / (query_norm * self._doc_lengths[index])
            scored_indexes.append((index, score))

        scored_indexes.sort(key=lambda item: item[1], reverse=True)
        return [
            RetrievedChunk(chunk=self._chunks[index], score=float(score))
            for index, score in scored_indexes[:top_k]
            if score > 0
        ]
