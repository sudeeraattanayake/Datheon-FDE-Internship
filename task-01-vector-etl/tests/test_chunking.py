from src.chunking import semantic_chunk_documents
from src.loaders import Document


def test_chunking_preserves_metadata():
    document = Document(
        text=(
            "Employees receive annual leave. "
            "Leave requests require manager approval. "
            "HR maintains employee records."
        ),
        metadata={
            "department": "HR",
            "access_tier": "internal",
            "date": "2026-11-08",
            "source": "hr_policy.md",
        },
    )

    chunks = semantic_chunk_documents(
        [document],
        max_words=8,
        overlap_sentences=1,
    )

    assert len(chunks) >= 2

    for chunk in chunks:
        assert chunk.metadata["department"] == "HR"
        assert chunk.metadata["access_tier"] == "internal"
        assert chunk.metadata["source"] == "hr_policy.md"
        assert len(chunk.text.split()) <= 8


def test_empty_document():
    document = Document(text="", metadata={})
    chunks = semantic_chunk_documents([document])
    assert chunks == []
