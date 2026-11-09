from __future__ import annotations

import pytest
from src.loaders import Document
from src.vector_store import EnterpriseVectorStore


@pytest.fixture
def store(tmp_path):
    return EnterpriseVectorStore(
        persist_directory=tmp_path / "chroma"
    )


def make_document(
    text: str,
    department: str = "HR",
    access_tier: str = "internal",
) -> Document:
    return Document(
        text=text,
        metadata={
            "department": department,
            "access_tier": access_tier,
            "date": "2026-11-09",
            "source": "test_policy.md",
        },
    )


def test_duplicate_ingestion_is_idempotent(store):
    document = make_document(
        "Employees must request annual leave approval."
    )

    store.add_documents([document])
    first_count = store.collection.count()

    store.add_documents([document])
    second_count = store.collection.count()

    assert first_count == 1
    assert second_count == 1


def test_department_isolation(store):
    store.add_documents([
        make_document(
            "HR annual leave policy.",
            department="HR",
        ),
        make_document(
            "Finance budget approval policy.",
            department="Finance",
        ),
    ])

    results = store.search(
        query="budget approval policy",
        department="HR",
        access_tier="internal",
    )

    assert all(
        result["metadata"]["department"] == "HR"
        for result in results
    )

    assert all(
        "Finance budget" not in result["text"]
        for result in results
    )


def test_access_tier_isolation(store):
    store.add_documents([
        make_document(
            "General employee handbook.",
            access_tier="internal",
        ),
        make_document(
            "Confidential executive compensation.",
            access_tier="restricted",
        ),
    ])

    results = store.search(
        query="executive compensation",
        department="HR",
        access_tier="internal",
    )

    assert all(
        result["metadata"]["access_tier"] == "internal"
        for result in results
    )

    assert all(
        "Confidential executive" not in result["text"]
        for result in results
    )


def test_empty_document_rejected(store):
    with pytest.raises(ValueError):
        store.add_documents([
            make_document("   ")
        ])


@pytest.mark.parametrize(
    "batch_size",
    [0, -1],
)
def test_invalid_batch_size(store, batch_size):
    with pytest.raises(ValueError):
        store.add_documents(
            [make_document("Valid policy content.")],
            batch_size=batch_size,
        )


def test_empty_batch_returns_zero(store):
    assert store.add_documents([]) == 0
    assert store.collection.count() == 0


def test_invalid_search_limit(store):
    with pytest.raises(ValueError):
        store.search(
            query="annual leave",
            department="HR",
            access_tier="internal",
            n_results=0,
        )


@pytest.mark.parametrize("invalid_size", [1.5, "32", True, None])
def test_non_integer_batch_size_rejected(store, invalid_size):
    with pytest.raises(ValueError):
        store.add_documents(
            [make_document("Valid employee policy.")],
            batch_size=invalid_size,
        )


def test_duplicate_ingestion_across_instances(tmp_path):
    database_path = tmp_path / "persistent_chroma"
    document = make_document("Employee leave policy.")

    first_store = EnterpriseVectorStore(
        persist_directory=database_path
    )
    first_store.add_documents([document])

    second_store = EnterpriseVectorStore(
        persist_directory=database_path
    )
    second_store.add_documents([document])

    assert second_store.collection.count() == 1
