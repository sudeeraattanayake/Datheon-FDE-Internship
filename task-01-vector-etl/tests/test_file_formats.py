from __future__ import annotations

import pandas as pd
import pymupdf
import pytest
from src.loaders import load_document
from src.pipeline import EnterpriseETLPipeline


@pytest.fixture
def metadata():
    return {
        "department": "HR",
        "access_tier": "internal",
        "date": "2026-11-08",
    }


def test_pdf_loader_with_page_numbers(tmp_path, metadata):
    path = tmp_path / "policy.pdf"

    with pymupdf.open() as pdf:
        for text in [
            "Employee annual leave policy.",
            "Manager approval is required.",
        ]:
            page = pdf.new_page()
            page.insert_text((72, 72), text)
        pdf.save(path)

    documents = load_document(path, metadata)

    assert len(documents) == 2
    assert documents[0].metadata["page_number"] == 1
    assert documents[1].metadata["page_number"] == 2
    assert "annual leave" in documents[0].text


def test_csv_loader_with_row_numbers(tmp_path, metadata):
    path = tmp_path / "employees.csv"

    pd.DataFrame(
        [
            {"employee": "Alice", "department": "HR"},
            {"employee": "Bob", "department": "Finance"},
        ]
    ).to_csv(path, index=False)

    documents = load_document(path, metadata)

    assert len(documents) == 2
    assert documents[0].metadata["row_number"] == 2
    assert documents[1].metadata["row_number"] == 3
    assert "Alice" in documents[0].text


def test_unsupported_file_format(tmp_path, metadata):
    path = tmp_path / "unknown.txt"
    path.write_text("Test", encoding="utf-8")

    with pytest.raises(ValueError):
        load_document(path, metadata)


def test_missing_file(tmp_path, metadata):
    with pytest.raises(FileNotFoundError):
        load_document(tmp_path / "missing.pdf", metadata)


def test_invalid_date(tmp_path, metadata):
    path = tmp_path / "policy.md"
    path.write_text("# Policy\nTest", encoding="utf-8")

    metadata["date"] = "invalid-date"

    with pytest.raises(ValueError):
        load_document(path, metadata)


def test_markdown_end_to_end(tmp_path, metadata):
    path = tmp_path / "policy.md"
    path.write_text(
        "# Annual Leave\nEmployees must request leave. "
        "Managers approve leave requests.",
        encoding="utf-8",
    )

    pipeline = EnterpriseETLPipeline(
        persist_directory=tmp_path / "chroma"
    )

    result = pipeline.ingest(path, metadata)

    assert result.documents_loaded == 1
    assert result.chunks_created >= 1

    matches = pipeline.search(
        query="Who approves leave requests?",
        department="HR",
        access_tier="internal",
    )

    assert len(matches) >= 1
    assert matches[0]["metadata"]["source"] == "policy.md"
