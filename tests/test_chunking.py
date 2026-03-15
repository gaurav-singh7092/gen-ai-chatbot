from gitlab_handbook_bot.chunking import split_text


def test_split_text_preserves_multiple_chunks() -> None:
    text = "word " * 1000
    chunks = split_text(text=text, chunk_size=500, chunk_overlap=100)

    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)
