from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import pymupdf


@dataclass
class Document:
    text: str
    metadata: dict[str, Any]


REQUIRED_METADATA = ("department", "access_tier", "date")


def validate_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Validate required enterprise document metadata."""
    cleaned = dict(metadata)

    for field in REQUIRED_METADATA:
        value = cleaned.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Missing or invalid metadata: {field}")
        cleaned[field] = value.strip()

    date.fromisoformat(cleaned["date"])
    return cleaned


def load_pdf(path: str | Path, metadata: dict[str, Any]) -> list[Document]:
    """Extract PDF text while retaining page numbers."""
    path = Path(path)
    base_metadata = validate_metadata(metadata)
    documents = []

    with pymupdf.open(path) as pdf:
        for page_index, page in enumerate(pdf):
            text = page.get_text("text").strip()

            if not text:
                continue

            documents.append(
                Document(
                    text=text,
                    metadata={
                        **base_metadata,
                        "source": path.name,
                        "file_type": "pdf",
                        "page_number": page_index + 1,
                    },
                )
            )

    return documents


def load_csv(path: str | Path, metadata: dict[str, Any]) -> list[Document]:
    """Convert CSV records into searchable documents."""
    path = Path(path)
    base_metadata = validate_metadata(metadata)
    frame = pd.read_csv(path).fillna("")
    documents = []

    for row_index, row in frame.iterrows():
        text = "\n".join(
            f"{column}: {value}"
            for column, value in row.items()
            if str(value).strip()
        )

        if not text.strip():
            continue

        documents.append(
            Document(
                text=text,
                metadata={
                    **base_metadata,
                    "source": path.name,
                    "file_type": "csv",
                    "row_number": int(row_index) + 2,
                },
            )
        )

    return documents


def load_markdown(
    path: str | Path, metadata: dict[str, Any]
) -> list[Document]:
    """Extract Markdown content with heading metadata."""
    path = Path(path)
    base_metadata = validate_metadata(metadata)
    content = path.read_text(encoding="utf-8-sig")

    sections = re.split(r"(?=^#{1,6}\s+)", content, flags=re.MULTILINE)
    documents = []

    for section in sections:
        section = section.strip()

        if not section:
            continue

        heading = re.search(r"^#{1,6}\s+(.+)$", section, re.MULTILINE)

        documents.append(
            Document(
                text=section,
                metadata={
                    **base_metadata,
                    "source": path.name,
                    "file_type": "markdown",
                    "section": heading.group(1).strip() if heading else "Introduction",
                },
            )
        )

    return documents


def load_document(
    path: str | Path, metadata: dict[str, Any]
) -> list[Document]:
    """Automatically select the appropriate document loader."""
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"Document not found: {path}")

    extension = path.suffix.lower()

    loaders = {
        ".pdf": load_pdf,
        ".csv": load_csv,
        ".md": load_markdown,
    }

    if extension not in loaders:
        raise ValueError(f"Unsupported document format: {extension}")

    return loaders[extension](path, metadata)
