from __future__ import annotations

import logging
import tempfile
from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import date
from pathlib import Path
from threading import Lock
from typing import Annotated
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from src.pipeline import EnterpriseETLPipeline


# ============================================================
# CONFIGURATION
# ============================================================

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    BASE_DIR / "data" / "processed" / "chroma_db"
)

ALLOWED_EXTENSIONS = {".pdf", ".csv", ".md"}

MAX_UPLOAD_BYTES = 10 * 1024 * 1024

pipeline: EnterpriseETLPipeline | None = None

ingestion_lock = Lock()


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline

    logger.info("Initializing Enterprise Vector ETL API")

    pipeline = EnterpriseETLPipeline(
        persist_directory=DATABASE_PATH
    )

    logger.info("Enterprise Vector ETL API started")

    try:
        yield

    finally:
        pipeline = None
        logger.info("Enterprise Vector ETL API stopped")


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Datheon Enterprise Vector ETL API",
    description=(
        "Enterprise document ingestion, semantic chunking, "
        "vector embeddings, ChromaDB indexing, "
        "metadata-filtered semantic search and analytics."
    ),
    version="1.2.0",
    lifespan=lifespan,
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class SearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=2000,
        description="Semantic search query",
    )

    department: str = Field(
        min_length=1,
        max_length=100,
        description="Department metadata filter",
    )

    access_tier: str = Field(
        min_length=1,
        max_length=100,
        description="Document access tier filter",
    )

    n_results: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of search results",
    )


# ============================================================
# HELPERS
# ============================================================

def get_pipeline() -> EnterpriseETLPipeline:
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="ETL pipeline is not initialized",
        )

    return pipeline


def normalize_department(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Department must be a string")

    normalized = value.strip().upper()

    if not normalized:
        raise ValueError("Department is required")

    return normalized


def normalize_access_tier(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Access tier must be a string")

    normalized = value.strip().lower()

    if not normalized:
        raise ValueError("Access tier is required")

    return normalized


def get_original_filename(upload: UploadFile) -> str:
    filename = Path(
        (upload.filename or "").replace("\\", "/")
    ).name.strip()

    if not filename or filename in {".", ".."}:
        raise HTTPException(
            status_code=422,
            detail="A valid filename is required",
        )

    if len(filename) > 255:
        raise HTTPException(
            status_code=422,
            detail="Filename is too long",
        )

    return filename


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/", tags=["System"])
def root():
    return {
        "name": "Datheon Enterprise Vector ETL API",
        "version": app.version,
        "status": "running",
        "documentation": "/docs",
        "features": [
            "PDF, CSV and Markdown ingestion",
            "Semantic document chunking",
            "Vector embeddings",
            "ChromaDB indexing",
            "Metadata-filtered semantic search",
            "Batch ingestion",
        ],
    }


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get("/health", tags=["System"])
def health():
    service = get_pipeline()

    try:
        service.store.collection.count()

    except Exception:
        logger.exception("Vector database health check failed")

        raise HTTPException(
            status_code=503,
            detail="Vector database unavailable",
        )

    return {
        "status": "healthy",
        "service": "Datheon Vector ETL",
        "database": "connected",
    }


# ============================================================
# STATISTICS ENDPOINT
# ============================================================

@app.get("/stats", tags=["Analytics"])
def stats():
    service = get_pipeline()

    return {
        "indexed_chunks": service.store.collection.count(),
        "embedding_model": "all-MiniLM-L6-v2",
        "vector_database": "ChromaDB",
        "distance_metric": "cosine",
        "supported_formats": [
            "PDF",
            "CSV",
            "Markdown",
        ],
        "max_upload_size_mb": 10,
    }


# ============================================================
# SEMANTIC SEARCH ENDPOINT
# ============================================================

@app.post("/search", tags=["Semantic Search"])
def search(request: SearchRequest):
    service = get_pipeline()

    try:
        department = normalize_department(
            request.department
        )

        access_tier = normalize_access_tier(
            request.access_tier
        )

        matches = service.search(
            query=request.query.strip(),
            department=department,
            access_tier=access_tier,
            n_results=request.n_results,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception("Semantic search failed")

        raise HTTPException(
            status_code=500,
            detail="Semantic search failed",
        )

    return {
        "query": request.query.strip(),
        "department": department,
        "access_tier": access_tier,
        "total_results": len(matches),
        "results": matches,
    }


# ============================================================
# DOCUMENT INGESTION ENDPOINT
# ============================================================

@app.post("/ingest", tags=["Document Ingestion"])
def ingest(
    file: Annotated[
        UploadFile,
        File(description="PDF, CSV or Markdown document"),
    ],
    department: Annotated[
        str,
        Form(min_length=1, max_length=100),
    ],
    access_tier: Annotated[
        str,
        Form(min_length=1, max_length=100),
    ],
    document_date: Annotated[
        date,
        Form(),
    ],
    batch_size: Annotated[
        int,
        Form(ge=1, le=512),
    ] = 32,
):
    service = get_pipeline()

    original_name = get_original_filename(file)

    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=(
                "Unsupported file format. "
                "Only PDF, CSV and Markdown are allowed."
            ),
        )

    temporary_path: Path | None = None

    try:
        normalized_department = normalize_department(
            department
        )

        normalized_access_tier = normalize_access_tier(
            access_tier
        )

        # ----------------------------------------------------
        # SAVE UPLOADED FILE TEMPORARILY
        # ----------------------------------------------------

        total_bytes = 0

        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=extension,
            delete=False,
        ) as temporary_file:

            temporary_path = Path(temporary_file.name)

            while True:
                chunk = file.file.read(1024 * 1024)

                if not chunk:
                    break

                total_bytes += len(chunk)

                if total_bytes > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail="Maximum upload size is 10 MB",
                    )

                temporary_file.write(chunk)

        if total_bytes == 0:
            raise HTTPException(
                status_code=422,
                detail="Uploaded file is empty",
            )

        # ----------------------------------------------------
        # PREPARE METADATA
        # ----------------------------------------------------

        metadata = {
            "department": normalized_department,
            "access_tier": normalized_access_tier,
            "date": document_date.isoformat(),
            "original_filename": original_name,
        }

        # ----------------------------------------------------
        # RUN ETL PIPELINE
        # ----------------------------------------------------

        with ingestion_lock:
            result = service.ingest(
                path=temporary_path,
                metadata=metadata,
                batch_size=batch_size,
                source_name=original_name,
            )

        # Original source name is now stored before indexing.
        # No post-ingestion ChromaDB metadata update needed.

        logger.info(
            "Successfully ingested %s: %d documents, "
            "%d chunks, %.3fs",
            original_name,
            result.documents_loaded,
            result.chunks_created,
            result.elapsed_seconds,
        )

        return {
            "status": "success",
            "filename": original_name,
            **asdict(result),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Document ingestion failed: %s",
            original_name,
        )

        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed",
        )

    finally:
        file.file.close()

        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)

            except OSError:
                logger.warning(
                    "Could not delete temporary file: %s",
                    temporary_path,
                )
