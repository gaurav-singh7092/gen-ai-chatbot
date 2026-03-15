from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
DEFAULT_INDEX_PATH = DATA_DIR / "gitlab_handbook_index.jsonl"

HANDBOOK_ROOT = "https://handbook.gitlab.com/handbook/"
DIRECTION_ROOT = "https://about.gitlab.com/direction/"
ALLOWED_ROOTS = (HANDBOOK_ROOT, DIRECTION_ROOT)


@dataclass(slots=True)
class Settings:
    index_path: Path = DEFAULT_INDEX_PATH
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    openai_base_url: str | None = os.getenv("OPENAI_BASE_URL") or None
    max_pages_default: int = 30
    request_timeout_seconds: float = 20.0
    chunk_size: int = 1200
    chunk_overlap: int = 200
    retrieval_k: int = 5
