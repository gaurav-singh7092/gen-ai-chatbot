from __future__ import annotations

from openai import APIError
from openai import OpenAI

from .config import Settings
from .retriever import RetrievedChunk


SYSTEM_PROMPT = """You are a GitLab Handbook and Direction assistant.
Answer only using the provided context.
If the answer is not supported by the context, say that clearly.
Keep answers concise, factual, and cite sources using markdown bullet lines at the end.
Do not claim access to internal-only GitLab content.
"""


def build_context(chunks: list[RetrievedChunk]) -> str:
    sections: list[str] = []
    for index, item in enumerate(chunks, start=1):
        sections.append(
            f"Source {index}\n"
            f"Title: {item.chunk.title}\n"
            f"URL: {item.chunk.url}\n"
            f"Section: {item.chunk.section}\n"
            f"Content: {item.chunk.content}"
        )
    return "\n\n".join(sections)


def generate_answer(settings: Settings, question: str, history: list[dict[str, str]], chunks: list[RetrievedChunk]) -> str:
    if not settings.openai_api_key:
        return fallback_answer(question=question, chunks=chunks)

    client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
    try:
        response = client.responses.create(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Conversation history:\n{format_history(history)}\n\n"
                        f"Question: {question}\n\n"
                        f"Context:\n{build_context(chunks)}"
                    ),
                },
            ],
        )
    except APIError:
        return fallback_answer(question=question, chunks=chunks)
    return response.output_text.strip()


def format_history(history: list[dict[str, str]]) -> str:
    if not history:
        return "No previous messages."
    lines = [f"{item['role']}: {item['content']}" for item in history[-6:]]
    return "\n".join(lines)


def fallback_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return (
            "I could not find enough indexed GitLab Handbook or Direction content to answer that yet. "
            "Build the index first, or widen the crawl scope."
        )

    summary_lines = [
        "No LLM API key is configured, so this is a grounded retrieval-only answer.",
        f"The question was: {question}",
        "Most relevant evidence:",
    ]
    for item in chunks[:3]:
        excerpt = item.chunk.content[:300].strip()
        summary_lines.append(f"- {item.chunk.title}: {excerpt}...")
        summary_lines.append(f"  Source: {item.chunk.url}")
    return "\n".join(summary_lines)
