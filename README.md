# GitLab Handbook Guide

GitLab Handbook Guide is a retrieval-augmented chatbot that answers questions from GitLab's public Handbook and Direction pages. It crawls public GitLab pages, chunks and indexes the content locally, retrieves the most relevant passages with a lightweight pure-Python TF-IDF-style scorer, and optionally uses an OpenAI-compatible model to produce concise grounded answers with source links.

## What this project delivers

- Data ingestion for GitLab Handbook and Direction content.
- A Generative AI chatbot with retrieval grounding and follow-up support.
- A Streamlit interface with source transparency and basic guardrails.
- Project documentation and local deployment instructions.

## Tech stack

- Python 3.11
- Streamlit for the UI
- httpx, BeautifulSoup, and trafilatura for crawling and extraction
- A lightweight pure-Python lexical retriever for local search
- OpenAI-compatible API integration for answer generation

## Project structure

```text
.
├── app.py
├── docs/
│   └── project-writeup.md
├── scripts/
│   └── build_index.py
├── src/gitlab_handbook_bot/
│   ├── chatbot.py
│   ├── chunking.py
│   ├── config.py
│   ├── crawler.py
│   ├── indexer.py
│   ├── llm.py
│   ├── models.py
│   └── retriever.py
└── tests/
```

## Local setup

Use Python 3.11 for the most reliable experience with the current dependency set.

1. Create a virtual environment.
2. Install the dependencies.
3. Optionally configure an OpenAI-compatible model.
4. Build the local index.
5. Run the Streamlit app.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export PYTHONPATH=src
python scripts/build_index.py --max-pages 30
streamlit run app.py
```

If you want generated answers instead of retrieval-only excerpts, set `OPENAI_API_KEY`. You can also set `OPENAI_MODEL` and `OPENAI_BASE_URL` for other OpenAI-compatible providers.

## How it works

1. The crawler starts from GitLab's public handbook and direction seed pages.
2. Page text is extracted and normalized into source documents.
3. Source documents are split into overlapping chunks.
4. TF-IDF search finds the most relevant chunks for a user query.
5. The chatbot either:
   - Sends the retrieved context to an OpenAI-compatible model, or
   - Falls back to a retrieval-only answer when no API key is configured.

## Guardrails and transparency

- Answers are constrained to indexed public GitLab content.
- The UI exposes retrieved source links for every answer.
- The prompt instructs the model to admit when the indexed context is insufficient.
- Internal-only GitLab pages are not treated as valid sources.

## Testing

```bash
export PYTHONPATH=src
pytest
```

Validated locally with:

```bash
PYTHONPATH=src .venv/bin/python -m pytest
PYTHONPATH=src .venv/bin/python scripts/build_index.py --max-pages 20
PYTHONPATH=src .venv/bin/python -m streamlit run app.py --server.headless true --server.port 8502
```

## Deployment

This project is ready for Streamlit Community Cloud deployment.

1. Push the repository to GitHub.
2. In Streamlit Community Cloud, create a new app from the repository.
3. Set these secrets:
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL`
   - `OPENAI_BASE_URL` if needed
4. Set the app entrypoint to `app.py`.

## Deliverables in this repository

- Project write-up: `docs/project-writeup.md`
- Source code: repository root
- Local run instructions: this README
