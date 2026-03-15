from __future__ import annotations

import argparse

from gitlab_handbook_bot.config import Settings
from gitlab_handbook_bot.indexer import build_index


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a searchable index from GitLab Handbook and Direction pages.")
    parser.add_argument("--max-pages", type=int, default=30, help="Maximum number of pages to crawl.")
    args = parser.parse_args()

    settings = Settings()
    chunks = build_index(settings=settings, max_pages=args.max_pages)
    print(f"Indexed {len(chunks)} chunks into {settings.index_path}")


if __name__ == "__main__":
    main()
