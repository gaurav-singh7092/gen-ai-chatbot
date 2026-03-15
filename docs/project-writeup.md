# Project Write-Up

## Objective

The goal was to build a transparent, accessible chatbot that helps employees or aspiring employees explore GitLab's public Handbook and Direction pages through a conversational interface.

## Approach

I chose a retrieval-augmented generation architecture that keeps the system practical and inspectable:

1. Crawl the public GitLab Handbook and Direction pages.
2. Extract readable content from HTML.
3. Chunk the content into retrieval-friendly passages.
4. Rank passages with a lightweight TF-IDF retriever.
5. Pass the ranked evidence to an OpenAI-compatible model for grounded answers.

This architecture keeps the system simple enough to run locally while still meeting the requirement for a generative AI chatbot.

## Technical choices

### Why Streamlit

Streamlit provides a fast path to a clean chat experience, local testing, and low-friction cloud deployment. It also supports a practical sidebar pattern for indexing controls and transparency features.

### Why a crawler plus local index

GitLab's Handbook and Direction pages are large and distributed across many URLs. A crawler-based ingestion flow makes it possible to refresh the source material directly from the live public pages. A local JSONL index keeps the project easy to inspect and debug.

### Why TF-IDF retrieval

For this project, TF-IDF is a pragmatic baseline:

- No separate embedding service is required.
- Retrieval is fast and inexpensive.
- Local development remains straightforward.

This choice prioritizes reliability and accessibility over maximum semantic recall.

### Why OpenAI-compatible generation

The application supports any OpenAI-compatible endpoint through environment variables. That keeps the code flexible across OpenAI, GitHub Models, or self-hosted compatible providers.

## User experience choices

- The initial assistant message explains the scope of the chatbot.
- The sidebar exposes index build controls instead of hiding data ingestion.
- Each answer includes supporting sources in the UI.
- If no API key is configured, the app still works in retrieval-only mode.

## Guardrails and transparency

The design explicitly favors trust over fluency:

- The model is instructed to answer only from provided context.
- The app surfaces the retrieved sources used for each response.
- The prompt forbids claims about internal-only GitLab content.
- When evidence is missing, the assistant should say so directly.

## Limitations

- The current crawler is intentionally lightweight and may not cover every public page in one run.
- TF-IDF retrieval can miss semantically relevant results compared with dense embeddings.
- Deployment to a public URL still requires GitHub and hosting credentials.

## Future improvements

1. Add hybrid retrieval with both dense embeddings and TF-IDF.
2. Improve crawl coverage with sitemap support and page freshness metadata.
3. Add answer quality evaluation and feedback capture.
4. Persist chat history and source analytics.
5. Add persona-aware prompts for employees, candidates, and contributors.
