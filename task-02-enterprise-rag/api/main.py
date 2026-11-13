from __future__ import annotations
import logging
import tempfile
from datetime import date
from pathlib import Path
from typing import Annotated
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from src.accounts import verify_user
from src.guardrails import grounded_answer
from src.ingestion import ingest_file
from src.retrieval import retrieve, rewrite, collection
from src.security import Identity, Role, issue_token, decode_token, LEVELS, ROLE_MAX
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)
app = FastAPI(title="Datheon Task 02 - Secure Enterprise RAG", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
                   allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])


class LoginRequest(BaseModel):
    username: str
    password: str


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)


def current_user(authorization: Annotated[str | None, Header()] = None) -> Identity:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Bearer token required")
    return decode_token(authorization[7:])


@app.get("/health")
def health():
    return {"status": "healthy", "service": "task02-rag"}


@app.post("/auth/login")
def login(body: LoginRequest):
    user = verify_user(body.username, body.password)
    if user is None:
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": issue_token(user), "token_type": "bearer", "user": user.model_dump()}


@app.get("/auth/me")
def me(user: Annotated[Identity, Depends(current_user)]):
    return user


@app.get("/stats")
def stats(user: Annotated[Identity, Depends(current_user)]):
    # Global counts are intentionally not exposed to non-admin users.
    return {"tenant": user.tenant_id, "status": "ready"}


@app.post("/documents/upload")
def upload(file: Annotated[UploadFile, File()],
           department: Annotated[str, Form(min_length=1, max_length=100)],
           access_tier: Annotated[str, Form()],
           document_date: Annotated[date, Form()],
           user: Annotated[Identity, Depends(current_user)]):
    name = Path((file.filename or "").replace("\\", "/")).name
    if Path(name).suffix.lower() not in {".pdf", ".csv", ".md"}:
        raise HTTPException(415, "Only PDF, CSV and Markdown are supported")
    if user.role != Role.admin and department != user.department:
        raise HTTPException(403, "Cannot upload into another department")
    if access_tier not in LEVELS or LEVELS[access_tier] > ROLE_MAX[user.role]:
        raise HTTPException(403, "Insufficient clearance")
    # For this demo, only managers/admins may ingest documents.
    if user.role == Role.employee:
        raise HTTPException(403, "Only managers and admins may upload")
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(name).suffix) as temp:
            temp_path = Path(temp.name)
            total = 0
            while data := file.file.read(1024 * 1024):
                total += len(data)
                if total > 10 * 1024 * 1024:
                    raise HTTPException(413, "10MB upload limit")
                temp.write(data)
        count = ingest_file(temp_path, name, user.tenant_id,
                            department, access_tier, document_date.isoformat())
        return {"status": "success", "filename": name, "indexed_chunks": count}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except HTTPException:
        raise
    except Exception:
        log.exception("Ingestion failed")
        raise HTTPException(500, "Document ingestion failed")
    finally:
        file.file.close()
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


@app.post("/rag/ask")
def ask(body: AskRequest, user: Annotated[Identity, Depends(current_user)]):
    try:
        matches = retrieve(body.question, user, body.top_k)
        answer, citations = grounded_answer(body.question, matches)
        return {"question": body.question, "rewritten_query": rewrite(body.question),
                "answer": answer, "citations": citations, "retrieved": len(matches)}
    except Exception:
        log.exception("RAG request failed")
        raise HTTPException(503, "RAG service temporarily unavailable")
