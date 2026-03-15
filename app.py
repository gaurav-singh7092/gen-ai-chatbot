from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from gitlab_handbook_bot import GitLabHandbookChatbot
from gitlab_handbook_bot.config import Settings
from gitlab_handbook_bot.indexer import build_index


load_dotenv()

st.set_page_config(
    page_title="GitLab Handbook Guide",
    page_icon="GL",
    layout="wide",
)


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(252, 214, 179, 0.8), transparent 35%),
                radial-gradient(circle at top right, rgba(232, 245, 233, 0.9), transparent 30%),
                linear-gradient(180deg, #fffaf5 0%, #f5f7f2 100%);
        }
        .block-container {
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        .hero {
            padding: 1.5rem;
            border: 1px solid rgba(54, 69, 79, 0.12);
            border-radius: 24px;
            background: rgba(255, 255, 255, 0.72);
            backdrop-filter: blur(10px);
            box-shadow: 0 12px 40px rgba(72, 58, 37, 0.08);
            margin-bottom: 1rem;
        }
        .hero h1 {
            font-size: 2.6rem;
            line-height: 1;
            margin-bottom: 0.4rem;
            color: #1f3a2e;
        }
        .hero p {
            font-size: 1.02rem;
            color: #34423d;
            margin-bottom: 0;
        }
        div[data-testid="stChatMessage"] {
            background: rgba(255, 255, 255, 0.74);
            border: 1px solid rgba(54, 69, 79, 0.08);
            border-radius: 18px;
            color: #1a1a1a !important;
        }
        div[data-testid="stChatMessage"] p,
        div[data-testid="stChatMessage"] li,
        div[data-testid="stChatMessage"] span,
        div[data-testid="stChatMessage"] a {
            color: #1a1a1a !important;
        }
        div[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #163127 0%, #21473a 100%);
        }
        div[data-testid="stSidebar"] * {
            color: #f5f7f2;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Ask about GitLab's public handbook or direction pages. "
                    "I answer from indexed GitLab sources and show the supporting pages."
                ),
            }
        ]
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = GitLabHandbookChatbot(Settings())
    if "last_sources" not in st.session_state:
        st.session_state.last_sources = []


def sidebar(chatbot: GitLabHandbookChatbot) -> None:
    st.sidebar.title("GitLab Handbook Guide")
    st.sidebar.caption("Transparent Q&A grounded in GitLab's public handbook and direction pages.")

    st.sidebar.metric("Indexed chunks", chatbot.document_count)
    st.sidebar.metric("Mode", "LLM" if chatbot.settings.openai_api_key else "Retrieval only")

    max_pages = st.sidebar.slider("Pages to crawl", min_value=10, max_value=120, value=30, step=10)
    if st.sidebar.button("Build or refresh index", use_container_width=True):
        with st.spinner("Crawling GitLab pages and building the index..."):
            build_index(settings=chatbot.settings, max_pages=max_pages)
            chatbot.reload()
        st.sidebar.success("Index refreshed.")

    st.sidebar.divider()
    st.sidebar.subheader("Guardrails")
    st.sidebar.write("Answers are restricted to indexed GitLab public content.")
    st.sidebar.write("If evidence is weak, the app should say so instead of improvising.")

    if st.session_state.last_sources:
        st.sidebar.divider()
        st.sidebar.subheader("Last retrieved sources")
        for item in st.session_state.last_sources:
            st.sidebar.markdown(f"- [{item.chunk.title}]({item.chunk.url})")


def render_messages() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main() -> None:
    init_state()
    apply_styles()
    chatbot: GitLabHandbookChatbot = st.session_state.chatbot

    sidebar(chatbot)

    st.markdown(
        """
        <section class="hero">
            <h1>GitLab Handbook Guide</h1>
            <p>
                Explore GitLab's public handbook and direction pages through a grounded chat interface.
                Every answer is tied back to retrieved GitLab sources so users can inspect the evidence.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if not chatbot.has_index:
        st.info("No index found yet. Use the sidebar to crawl GitLab pages and build the local search index.")

    render_messages()

    prompt = st.chat_input("Ask a question about GitLab's handbook or direction")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not chatbot.has_index:
            answer = "Build the index first from the sidebar, then ask your question again."
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            return

        try:
            with st.spinner("Retrieving GitLab context..."):
                result = chatbot.ask(prompt, st.session_state.messages[:-1])
        except Exception:
            answer = "Something went wrong while processing that question. Try rebuilding the index or checking your model configuration."
            st.error(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            return

        st.markdown(result.answer)
        if result.retrieved_chunks:
            with st.expander("Sources", expanded=True):
                for item in result.retrieved_chunks:
                    st.markdown(f"- [{item.chunk.title}]({item.chunk.url})")
        st.session_state.last_sources = result.retrieved_chunks
        st.session_state.messages.append({"role": "assistant", "content": result.answer})


if __name__ == "__main__":
    main()
