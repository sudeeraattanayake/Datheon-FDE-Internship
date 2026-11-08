from src.loaders import load_document


def test_markdown_loader(tmp_path):
    path = tmp_path / "policy.md"
    path.write_text(
        "# HR Policy\nEmployees receive annual leave.",
        encoding="utf-8",
    )

    metadata = {
        "department": "HR",
        "access_tier": "internal",
        "date": "2026-11-08",
    }

    documents = load_document(path, metadata)

    assert len(documents) == 1
    assert documents[0].metadata["department"] == "HR"
    assert documents[0].metadata["access_tier"] == "internal"
    assert documents[0].metadata["section"] == "HR Policy"
    assert "annual leave" in documents[0].text


def test_missing_metadata(tmp_path):
    import pytest

    path = tmp_path / "policy.md"
    path.write_text("# Policy\nTest content", encoding="utf-8")

    with pytest.raises(ValueError):
        load_document(path, {"department": "HR"})
