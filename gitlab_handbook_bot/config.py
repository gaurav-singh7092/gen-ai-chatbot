import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DEFAULT_INDEX_PATH = DATA_DIR / "gitlab_handbook_index.jsonl"

HANDBOOK_ROOT = "https://handbook.gitlab.com/handbook/"
DIRECTION_ROOT = "https://about.gitlab.com/direction/"
ALLOWED_ROOTS = (HANDBOOK_ROOT, DIRECTION_ROOT)


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class Settings:
    def __init__(
        self,
        index_path: Path = DEFAULT_INDEX_PATH,
        openai_api_key: str | None = None,
        openai_model: str | None = None,
        openai_base_url: str | None = None,
        max_pages_default: int = 30,
        request_timeout_seconds: float = 20.0,
        chunk_size: int = 1200,
        chunk_overlap: int = 200,
        retrieval_k: int = 5,
    ) -> None:
        self.index_path = index_path
        self.openai_api_key = _clean_optional(openai_api_key) or _clean_optional(os.getenv("OPENAI_API_KEY"))
        self.openai_model = _clean_optional(openai_model) or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.openai_base_url = _clean_optional(openai_base_url) or _clean_optional(os.getenv("OPENAI_BASE_URL"))
        self.max_pages_default = max_pages_default
        self.request_timeout_seconds = request_timeout_seconds
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.retrieval_k = retrieval_k
