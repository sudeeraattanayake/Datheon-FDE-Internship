# Task 02 — Enterprise Multi-Tenant RAG with RBAC

A local, runnable implementation of the Datheon FDE Task 02 brief.

## Features
- Signed JWT authentication, Argon2 password hashes, tenant-bound user identity
- Pre-retrieval ChromaDB metadata filtering for tenant, department, and clearance
- Cross-encoder reranking with `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Deterministic query expansion (PTO/HR/FAQ) and original query retained
- Extractive evidence-only answers with source/page citations
- PDF, Markdown and CSV ingestion with source metadata
- Next.js dashboard and automated security-policy tests

## Quick start (Windows PowerShell)
From **task-02-enterprise-rag** with repository `.venv` activated:

```powershell
python -m pip install -r requirements.txt
$env:JWT_SECRET = python -c "import secrets; print(secrets.token_urlsafe(48))"
python bootstrap.py
python -m uvicorn api.main:app --reload --port 8001
```

In another terminal:

```powershell
cd frontend
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

Open `http://localhost:3001`. Swagger API: `http://127.0.0.1:8001/docs`.

Demo users (LOCAL ONLY):
- `alice` / `AliceDemo123!` — acme HR employee (read-only)
- `manager` / `ManagerDemo123!` — acme HR manager (can upload)
- `admin` / `AdminDemo123!` — acme admin (can upload across departments)
- `other` / `OtherDemo123!` — globex admin (different tenant)

Use manager to upload `task-01-vector-etl/data/raw/hr_policy.md` with HR/internal metadata, then sign in as alice to ask about annual leave.

## Tests

```powershell
python -m pytest tests -v
```

## Security and limitations
This is a **local prototype**, not an audited production service. Never deploy with demo credentials. `JWT_SECRET` must be strong and private. Accounts are provisioned from local JSON and there is no rate limiting, revocation, TLS termination, audit log, virus scanning, CSRF strategy for cookie auth, or distributed ingestion lock. The vector database must not be exposed directly. Tenant and clearance are taken only from the verified token; client-supplied tenant is never trusted. Metadata filtering is applied **inside the vector query**, with a defense-in-depth post-filter. Documents without `tenant_id` are excluded, so Task 01's old collection is intentionally not queried.

The answerer is **extractive**, not a generative LLM. It quotes retrieved evidence and declines when no evidence passes the relevance threshold. Cross-encoder thresholds are heuristic and should be calibrated on evaluation data. Citations identify PDF page numbers when the PDF contains extractable text; Markdown and CSV have no page numbers. Scanned PDFs require OCR. No accuracy or hallucination-free guarantee is claimed. Query rewriting is rule-based, not LLM-based. For production, add a grounded LLM with citation validation, secure identity provider, real RBAC policy administration, secret management, metrics, evaluation harness, and integration tests.
