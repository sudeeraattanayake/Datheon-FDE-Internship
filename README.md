
# Datheon — Forward Deployed Engineering Internship

**Enterprise AI Engineering | Vector ETL • Secure RAG • Agentic AI • MLOps**

An enterprise AI engineering portfolio developed as part of the **Datheon Forward Deployed Engineering Internship**, featuring three implemented projects and a fourth deployment-focused task in progress.

This repository demonstrates practical approaches to building enterprise document pipelines, secure retrieval-augmented generation (RAG) systems, autonomous AI agents, and deployable AI services.

## Internship Projects

| Task | Project | Status |
|------|---------|--------|
| 01 | Enterprise Vector ETL Pipeline | Completed |
| 02 | Enterprise Multi-Tenant RAG System | Implemented — Final Review |
| 03 | Autonomous ERP/CRM AI Agent | Completed — 13/13 tests passed |
| 04 | Dockerized AI Microservice | Starter prepared — deployment not verified |

---

## Task 01 — Enterprise Vector ETL Pipeline

A full-stack document ingestion and semantic search system built using **Python, FastAPI, Sentence Transformers, ChromaDB, and Next.js**.

### Key Features

- PDF, CSV, and Markdown document ingestion
- Semantic chunking with configurable parameters
- Sentence Transformer embedding generation
- Persistent ChromaDB vector indexing
- Cosine-distance semantic retrieval
- Department and access-tier metadata filtering
- Deterministic document IDs and upsert operations
- Batch ingestion and performance benchmarking
- Input validation and automated resilience testing
- FastAPI REST endpoints
- Interactive Next.js dashboard
- Document upload, semantic search, and analytics interfaces

### Technology Stack

| Category | Technologies |
|----------|--------------|
| Backend | Python, FastAPI |
| Machine Learning | Sentence Transformers, all-MiniLM-L6-v2 |
| Vector Database | ChromaDB |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Document Processing | PyMuPDF, Pandas |
| Testing | Pytest |
| Analytics | Recharts |

### System Architecture

```text
Enterprise Documents
        |
        v
PDF / CSV / Markdown Loaders
        |
        v
Metadata Validation
        |
        v
Semantic Chunking
        |
        v
Sentence Transformer Embeddings
        |
        v
ChromaDB Vector Storage
        |
        v
Metadata-Filtered Semantic Search
        |
        v
FastAPI REST API
        |
        v
Next.js Dashboard
```

### Performance Benchmarks

Historical measurements using 100 synthetic CSV records, four batch sizes, and three repetitions per configuration.

| Batch Size | Avg. Time | Avg. Throughput |
|------------|-----------|-----------------|
| 8 | 6.095 s | 17.51 chunks/s |
| 16 | 4.520 s | 22.15 chunks/s |
| 32 | 4.110 s | 24.34 chunks/s |
| 64 | 4.131 s | 24.38 chunks/s |

**Recommended default batch size:** 32

Results represent local measurements, not production performance guarantees.

### Quality Checks

- **30/30 Python tests passed**
- ESLint passed
- Next.js production build passed
- Document ingestion tested
- Metadata-filtered semantic search tested
- Analytics dashboard implemented

### Task 01 Documentation

[View Task 01 Source Code and Documentation](task-01-vector-etl/README.md)

---

## Task 02 — Enterprise Multi-Tenant RAG System

A full-stack enterprise RAG application designed to demonstrate authenticated document retrieval, tenant isolation, role-based access control, semantic reranking, grounded AI-generated answers, and verifiable source citations.

**Status: Implemented — Final Review**

### Key Features

#### Authentication and Authorization

- JWT-based authentication
- Authenticated user identity verification
- Multi-tenant document isolation
- Department-based access restrictions
- Role-based access control (RBAC)
- Document clearance-level enforcement
- Restricted document upload permissions
- Authorization-aware retrieval filtering

#### Document Processing

- PDF, CSV, and Markdown ingestion
- Document metadata validation
- Semantic text chunking
- Sentence Transformer embeddings
- Persistent ChromaDB vector storage
- Deterministic chunk identification
- Document metadata indexing
- PDF page reference preservation

#### Retrieval Pipeline

- Natural-language question processing
- Query rewriting and abbreviation expansion
- Tenant-aware vector search
- Department and clearance filtering
- Cross-encoder reranking
- Top-K evidence selection
- Authorized document retrieval

#### Grounded Answer Generation

- OpenAI-powered answer generation
- Evidence-constrained prompting
- Source citation generation
- PDF page references
- Insufficient-evidence refusal
- Extractive fallback behavior
- Citation identifier validation

#### Full-Stack Application

- FastAPI REST backend
- Next.js frontend
- User authentication interface
- Authenticated document uploads
- RAG question-answering interface
- Source citation display
- Authorized retrieval result counts
- Tenant and user information display

### Technology Stack

| Category | Technologies |
|----------|--------------|
| Backend | Python, FastAPI |
| Authentication | JWT |
| Embeddings | Sentence Transformers, all-MiniLM-L6-v2 |
| Vector Database | ChromaDB |
| Reranking | CrossEncoder, ms-marco-MiniLM-L-6-v2 |
| LLM | OpenAI API, GPT-4o-mini |
| Frontend | Next.js, React, TypeScript |
| Document Processing | PDF, CSV, Markdown |
| Testing | Pytest |
| Configuration | Python Dotenv |

### System Architecture

```text
                  Enterprise User
                         |
                         v
                  Next.js Frontend
                         |
                         v
                    FastAPI API
                         |
                         v
                 JWT Authentication
                         |
                         v
                 Verified Identity
                         |
                         v
                 Natural Language Query
                         |
                         v
                   Query Rewriting
                         |
                         v
                 RBAC Metadata Filter
                         |
                         v
                ChromaDB Vector Search
                         |
                         v
              Authorization Verification
                         |
                         v
                 Cross-Encoder Reranking
                         |
                         v
                Authorized Evidence
                         |
                         v
                Grounded LLM Generation
                         |
                         v
               Citation Validation
                         |
                         v
               Answer + PDF Citations
                         |
                         v
                  Next.js Dashboard
```

### Multi-Tenant Security Model

The system uses authenticated identity attributes to restrict document retrieval.

Each document can include authorization metadata such as:

- Tenant identifier
- Department
- Access tier
- Source filename
- Source page number

Access decisions are based on the authenticated user's tenant, department, role, and clearance permissions.

The application is designed to prevent unauthorized documents from entering the answer-generation context.

#### Authorization Rules

| Security Control | Behavior |
|------------------|----------|
| Tenant isolation | Users cannot retrieve documents belonging to another tenant |
| Department isolation | Access depends on department permissions |
| Clearance enforcement | Documents above the user's permitted access tier are denied |
| Role restrictions | Upload operations are restricted to authorized roles |
| Administrative access | Administrative permissions remain tenant-scoped |
| Retrieval filtering | Authorization filters are applied during retrieval and candidate verification |

### Demonstrated Security Scenarios

#### Test 01 — Authorized Employee Retrieval

**User:** alice  
**Tenant:** acme  
**Department:** HR  
**Role:** Employee

An HR employee queried an authorized annual leave policy document.

**Observed result:**

- Authorized document chunks retrieved
- Grounded answer generated
- Source citations returned
- PDF page references displayed

**Result: Passed**

#### Test 02 — Cross-Tenant Isolation

**User:** other  
**Tenant:** globex  
**Department:** HR  
**Role:** Admin

The user attempted to retrieve information from an HR policy document belonging to the `acme` tenant.

**Observed result:**

- Zero authorized matches
- No source citations
- Insufficient authorized evidence response

**Result: Passed**

This demonstrated tenant isolation for the tested scenario, including an administrator belonging to another tenant.

#### Test 03 — Unsupported Question Refusal

A user asked:

> What is the company's CEO's annual salary?

The indexed HR policy did not provide sufficient evidence for the requested information.

**Observed response:**

> I cannot find sufficient authorized source evidence to answer that question.

**Result: Passed**

This demonstrates refusal behavior for the tested unsupported question. It does not establish comprehensive hallucination prevention.

### Automated Security Tests

The Task 02 security test suite includes:

| Test | Result |
|------|--------|
| Same-tenant employee access | Passed |
| Cross-tenant isolation for administrators | Passed |
| Department isolation | Passed |
| Clearance enforcement | Passed |
| Same-tenant administrator department access | Passed |
| Unknown access-tier rejection | Passed |
| Tenant-constrained query filtering | Passed |

**Automated test results: 7/7 passed**

Additional observed verification results:

- Python compilation completed successfully
- Python dependency check found no broken requirements
- ESLint completed with zero errors and one warning
- Next.js production build completed successfully
- TypeScript compilation passed
- Static page generation passed

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health |
| POST | `/auth/login` | Authenticate user |
| GET | `/auth/me` | Retrieve authenticated identity |
| GET | `/stats` | Retrieve tenant-scoped application status |
| POST | `/documents/upload` | Upload an authorized document |
| POST | `/rag/ask` | Ask a question using authorized evidence |

Protected endpoints require a valid bearer token.

### Local Development Setup

#### Requirements

- Python 3.13
- Node.js and npm
- OpenAI API key for LLM-based answers
- Internet connection for initial model downloads

#### 1. Clone the Repository

```bash
git clone https://github.com/sudeeraattanayake/Datheon-FDE-Internship.git
cd Datheon-FDE-Internship/task-02-enterprise-rag
```

#### 2. Create Python Virtual Environment

Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install python-dotenv openai
```

#### 3. Configure Environment Variables

Create a `.env` file in the `task-02-enterprise-rag` directory:

```env
OPENAI_API_KEY=your_openai_api_key
RAG_ANSWER_MODEL=gpt-4o-mini
```

The OpenAI API key is required for OpenAI-generated answers. Without it, the application can use its extractive fallback behavior.

Never commit real API keys or environment files containing secrets.

#### 4. Initialize Demo Accounts

```powershell
.\.venv\Scripts\python.exe bootstrap.py
```

The bootstrap script prepares local demonstration account data.

Refer to the bootstrap implementation for the configured demo users and credentials.

Demo accounts and locally stored account data are intended for development and testing only.

#### 5. Start FastAPI Backend

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8001
```

Backend:

http://localhost:8001

Interactive API documentation:

http://localhost:8001/docs

#### 6. Start Next.js Frontend

Open a second terminal:

```powershell
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

Start the frontend:

```powershell
npm run dev -- -p 3001
```

Frontend:

http://localhost:3001

#### 7. Run Security Tests

From the Task 02 root directory:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

#### 8. Build Frontend

From the `frontend` directory:

```powershell
npm run lint
npm run build
```

### Task 02 Security Limitations

Task 02 is an enterprise-oriented engineering demonstration, not a production-certified security system.

Before deployment with sensitive organizational data, additional work would be required, including:

- External identity provider integration
- Production-grade user and credential management
- Secure secret management
- Stronger audit logging
- Rate limiting and abuse prevention
- Prompt-injection resistance testing
- Expanded retrieval and answer-quality evaluation
- Citation-to-claim verification
- Comprehensive authorization integration testing
- Production monitoring and incident response controls

The current citation validation checks citation identifiers; it does not independently prove that every generated claim is semantically supported by the cited passage.

The retrieval pipeline implements dense vector retrieval with cross-encoder reranking. It should not be described as a fully implemented hybrid dense-and-sparse search system without an additional sparse retrieval component.

### Task 02 Documentation

[View Task 02 Source Code](task-02-enterprise-rag/)

---

## Task 03 — Autonomous ERP/CRM AI Agent

**Status: Implemented — 13/13 automated API tests passed**

A full-stack enterprise field agent that uses tool-driven workflows to interact with simulated ERP, CRM, and support systems. It demonstrates business-data retrieval, controlled write operations, human-in-the-loop approvals, and execution auditing.

### Key Features

- AI agent workflow orchestration and tool calling
- Mock enterprise inventory lookup, CRM lead updates, and support ticket creation
- Input validation and business operation checks
- Human approval requests before sensitive write operations
- Approval and rejection workflows
- Execution traces and audit history
- FastAPI backend with an interactive Next.js dashboard
- Automated API tests for inventory, leads, tickets, approvals, audit, and statistics

### Demonstrated Workflows

| Scenario | Observed Result |
|----------|-----------------|
| Check stock and price of `LAP-001` | Retrieved Business Laptop inventory: 25 units, $1,200 |
| Update `LEAD-001` to `qualified` | Pending approval generated; approved update reflected in CRM |
| Create high-priority support ticket | Ticket `TKT-36D780E654` created for a laptop power issue |
| Validate approval controls | Pending, approve, reject, duplicate-denial, and invalid-status API cases passed |

These are local demonstration scenarios using mock enterprise data, not real customer transactions.

### Architecture

```text
Business User
    |
    v
Next.js Agent Workspace
    |
    v
FastAPI Agent Service
    |
    v
Workflow Orchestration + Tool Selection
    |
    +--> ERP Inventory Lookup
    +--> CRM Lead Management
    +--> Support Ticket Operations
    |
    v
Validation + Human Approval for Sensitive Writes
    |
    v
Business Operation + Audit Trail
    |
    v
Execution Trace + Dashboard Response
```

### Validation

**13/13 Pytest API tests passed**, covering health, inventory, missing inventory, lead operations, approval lifecycle, ticket approval, duplicate denial, invalid status, audit history, statistics, and pending requests.

### Local Development

From `task-03-autonomous-erp-crm-agent/`, install dependencies from `requirements.txt`, configure environment variables using `.env.example`, and refer to the task-specific README for current startup commands.

**Demonstrated local ports:** FastAPI `8002`, Next.js `3003`.

### Task 03 Documentation

[View Task 03 Source Code and Documentation](task-03-autonomous-erp-crm-agent/README.md)

---

## Task 04 — Dockerized AI Microservice

**Status: Starter implementation prepared locally — Docker deployment not verified**

This project focuses on packaging and operating an AI-powered service using containerization and deployment-oriented engineering practices.

### Deployment Scope

- Docker containerization
- Docker Compose
- Containerized FastAPI deployment
- Health and readiness checks
- Prometheus-compatible metrics
- API validation and hardening
- Environment-based configuration
- Structured logging
- Deployment documentation
- Service testing

### Target Architecture

```text
API Client
     |
     v
Containerized FastAPI Service
     |
     v
Request Validation
     |
     v
AI Inference / Processing
     |
     v
Structured API Response
     |
     v
Monitoring and Metrics
```

---

The initial Task 04 scaffold includes Docker Compose, FastAPI gateway, Prometheus monitoring, health endpoints, benchmarks, tests, and documentation. The Docker Engine did not start on the development machine, so container startup, production readiness, and measured deployment latency are **not verified**. Integration with the actual Task 01–03 APIs also remains outstanding. The local Task 04 folder is not yet part of the confirmed GitHub submission.

---

## Repository Structure

```text
Datheon-FDE-Internship/
|
|-- task-01-vector-etl/
|   |-- api/
|   |-- benchmarks/
|   |-- data/
|   |-- frontend/
|   |-- src/
|   |-- tests/
|   |-- README.md
|
|-- task-02-enterprise-rag/
|   |-- api/
|   |   |-- main.py
|   |
|   |-- frontend/
|   |-- src/
|   |   |-- accounts.py
|   |   |-- guardrails.py
|   |   |-- ingestion.py
|   |   |-- retrieval.py
|   |   |-- security.py
|   |
|   |-- tests/
|   |   |-- test_security.py
|   |
|   |-- bootstrap.py
|   |-- requirements.txt
|
|-- task-03-autonomous-erp-crm-agent/
|   |-- agent/
|   |-- api/
|   |-- frontend/
|   |-- services/
|   |-- tests/
|   |-- README.md
|   |-- requirements.txt
|
|-- .gitignore
|-- README.md
```

Task 04 is currently a separate local starter project and is not included in this confirmed repository structure.

Local virtual environments, generated caches, credentials, and persistent development databases are excluded from version control.

---

## Engineering Focus

This internship portfolio emphasizes:

- Enterprise AI application development
- Machine learning integration
- Vector database engineering
- Retrieval-augmented generation
- Multi-tenant application design
- Authentication and authorization
- Agentic workflow orchestration
- API engineering
- Automated testing
- Performance benchmarking
- Modular software architecture
- Deployment readiness

---

## Project Validation Summary

| Validation | Task 01 | Task 02 | Task 03 |
|------------|---------|---------|---------|
| Python tests | 30 passed | 7 security tests passed | 13 API tests passed |
| Frontend lint | Passed | 0 errors, 1 warning | Not independently verified |
| Production build | Passed | Passed | Not independently verified |
| API implementation | Implemented | Implemented | Implemented |
| Document ingestion | Tested | Tested | Not applicable |
| Vector retrieval | Tested | Tested | Not applicable |
| Authentication | Not implemented as a security boundary | JWT implemented | Not independently verified as production security |
| Tenant isolation | Not implemented as a security boundary | Tested | Not applicable |
| Grounded LLM answers | Not a Task 01 requirement | Tested | Not independently evaluated |
| Source citations | Not a Task 01 requirement | Tested | Not applicable |
| Human-in-the-loop approval | Not applicable | Not applicable | Demonstrated |

These results describe local development validation rather than independent production certification.

---

## Author

**Sudeera Attanayake**

AI Engineer | Machine Learning | RAG | Agentic AI

**GitHub:** [sudeeraattanayake](https://github.com/sudeeraattanayake)

---

## Security and Responsible AI

The projects in this repository are educational and engineering demonstrations.

Task 01 metadata filtering is not a substitute for authenticated authorization.

Task 02 adds JWT authentication, tenant-aware retrieval, RBAC restrictions, and grounded answer generation. Task 03 adds approval-gated business operations and audit traces. These controls require further hardening and independent evaluation before production use with sensitive enterprise data.

Never upload real credentials, private customer records, or confidential enterprise documents into public repositories.

---

## License

No open-source license has been declared for this repository.
