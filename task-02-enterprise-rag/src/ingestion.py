from __future__ import annotations
from pathlib import Path
import fitz
from src.retrieval import index_chunks

SUPPORTED = {".pdf", ".md", ".csv"}

def split_text(text: str, max_words: int = 130, overlap: int = 25) -> list[str]:
    words = text.split()
    if not words:
        return []
    step = max_words - overlap
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), step) if words[i:i + max_words]]

def ingest_file(path: Path, filename: str, tenant_id: str, department: str,
                access_tier: str, document_date: str) -> int:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError("Only PDF, CSV and Markdown are supported")
    pages: list[tuple[int, str]] = []
    if suffix == ".pdf":
        with fitz.open(path) as pdf:
            for i, page in enumerate(pdf):
                pages.append((i + 1, page.get_text()))
    else:
        pages.append((1, path.read_text(encoding="utf-8-sig")))
    chunks = []
    for page_number, text in pages:
        for chunk_number, chunk in enumerate(split_text(text), 1):
            metadata = {"tenant_id": tenant_id, "department": department,
                        "access_tier": access_tier, "date": document_date,
                        "source": Path(filename).name, "page": page_number if suffix == ".pdf" else 0,
                        "chunk": chunk_number}
            chunks.append((chunk, metadata))
    if not chunks:
        raise ValueError("Document contains no extractable text; scanned PDFs need OCR")
    return index_chunks(chunks)
