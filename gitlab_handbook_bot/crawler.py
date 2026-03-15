from __future__ import annotations

import re
from collections import deque
from urllib.parse import urljoin, urldefrag, urlparse, urlunparse

import httpx
import trafilatura
from bs4 import BeautifulSoup

from .config import ALLOWED_ROOTS, HANDBOOK_ROOT, DIRECTION_ROOT, Settings
from .models import SourceDocument


def normalize_url(url: str) -> str:
    clean_url, _fragment = urldefrag(url)
    parsed = urlparse(clean_url)
    path = parsed.path or "/"
    if not path.endswith("/") and "." not in path.rsplit("/", maxsplit=1)[-1]:
        path = f"{path}/"
    normalized = parsed._replace(path=path, params="", query="")
    return urlunparse(normalized)


def is_allowed_url(url: str) -> bool:
    normalized = normalize_url(url)
    if not normalized.startswith(ALLOWED_ROOTS):
        return False
    blocked_patterns = (
        "/search/",
        "/page-data/",
        "/images/",
        "/assets/",
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".gif",
        ".pdf",
        ".xml",
        ".json",
        "mailto:",
    )
    return not any(pattern in normalized for pattern in blocked_patterns)


def extract_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return re.sub(r"\s+", " ", soup.title.string).strip()
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(" ", strip=True)
    return "Untitled GitLab page"


def extract_links(url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    discovered: list[str] = []
    for anchor in soup.find_all("a", href=True):
        absolute = normalize_url(urljoin(url, anchor["href"]))
        if is_allowed_url(absolute):
            discovered.append(absolute)
    return discovered


def extract_text(html: str, url: str) -> str:
    extracted = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_links=True,
        include_tables=False,
        favor_precision=True,
    )
    if extracted:
        return extracted.strip()
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n", strip=True)


def infer_section(url: str) -> str:
    if url.startswith(HANDBOOK_ROOT):
        return "handbook"
    if url.startswith(DIRECTION_ROOT):
        return "direction"
    return "unknown"


def crawl_sources(settings: Settings, max_pages: int, seed_urls: list[str] | None = None) -> list[SourceDocument]:
    seeds = seed_urls or [HANDBOOK_ROOT, DIRECTION_ROOT]
    queue = deque(normalize_url(url) for url in seeds)
    visited: set[str] = set()
    documents: list[SourceDocument] = []

    with httpx.Client(follow_redirects=True, timeout=settings.request_timeout_seconds) as client:
        while queue and len(documents) < max_pages:
            current = queue.popleft()
            if current in visited or not is_allowed_url(current):
                continue
            visited.add(current)

            try:
                response = client.get(current, headers={"User-Agent": "gitlab-handbook-chatbot/1.0"})
                response.raise_for_status()
            except httpx.HTTPError:
                continue

            html = response.text
            text = extract_text(html, current)
            if len(text) < 300:
                continue

            documents.append(
                SourceDocument(
                    url=current,
                    title=extract_title(html),
                    content=text,
                    section=infer_section(current),
                )
            )

            for link in extract_links(current, html):
                if link not in visited:
                    queue.append(link)

    return documents
