import pytest
from src.loaders import Document
from src.vector_store import EnterpriseVectorStore


@pytest.fixture
def store(tmp_path):
    return EnterpriseVectorStore(
        persist_directory=tmp_path / "chroma",
        collection_name="test_documents",
    )


def test_empty_store(store):
    assert store.search("leave policy", "HR", "internal") == []


def test_add_and_search_with_filters(store):
    documents = [
        Document(
            text="HR employees receive annual leave benefits.",
            metadata={
                "department": "HR",
                "access_tier": "internal",
                "date": "2026-11-08",
                "source": "hr.md",
            },
        ),
        Document(
            text="Finance department handles corporate invoices.",
            metadata={
                "department": "Finance",
                "access_tier": "confidential",
                "date": "2026-11-08",
                "source": "finance.md",
            },
        ),
    ]

    assert store.add_documents(documents) == 2

    results = store.search(
        query="employee annual leave",
        department="HR",
        access_tier="internal",
    )

    assert len(results) == 1
    assert results[0]["metadata"]["department"] == "HR"
    assert "annual leave" in results[0]["text"]

    restricted = store.search(
        query="finance invoices",
        department="HR",
        access_tier="internal",
    )

    assert all(
        result["metadata"]["department"] == "HR"
        for result in restricted
    )


def test_invalid_query(store):
    with pytest.raises(ValueError):
        store.search("", "HR", "internal")
