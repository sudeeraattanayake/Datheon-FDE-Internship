
# Datheon — Forward Deployed Engineering Internship

**Enterprise AI Engineering | Vector ETL • RAG • Agentic AI • MLOps**

A portfolio of four enterprise-focused AI engineering projects developed as part of the **Datheon Forward Deployed Engineering Internship**.

This repository demonstrates practical approaches to building document processing pipelines, semantic retrieval systems, AI agents, and deployable AI services.

---

## Internship Projects

| Task | Project | Status |
|------|---------|--------|
| 01 | Enterprise Vector ETL Pipeline | Implemented — Final Review |
| 02 | Enterprise Multi-Tenant RAG System | Upcoming |
| 03 | Autonomous ERP/CRM AI Agent | Upcoming |
| 04 | Dockerized AI Microservice | Upcoming |

---

## Task 01 — Enterprise Vector ETL Pipeline

A full-stack document ingestion and semantic search system built with **Python, FastAPI, Sentence Transformers, ChromaDB, and Next.js**.

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
- **ESLint passed**
- **Next.js production build passed**
- Document ingestion tested
- Metadata-filtered semantic search tested
- Analytics dashboard implemented

### Task 01 Documentation

[View Task 01 Source Code and Documentation](task-01-vector-etl/README.md)

---

## Task 02 — Enterprise Multi-Tenant RAG System

**Status: Upcoming**

Planned capabilities:

- Authenticated tenant isolation
- Role-based access control
- Query rewriting
- Hybrid retrieval and reranking
- Grounded answer generation
- Source citations
- Retrieval guardrails

---

## Task 03 — Autonomous ERP/CRM AI Agent

**Status: Upcoming**

Planned capabilities:

- Agentic business workflows
- Mock ERP/CRM REST integrations
- Tool-calling agents
- Human-in-the-loop approvals
- Retry and recovery mechanisms
- Execution audit trails

---

## Task 04 — Dockerized AI Microservice

**Status: Upcoming**

Planned capabilities:

- Docker and Docker Compose
- Containerized FastAPI deployment
- Health and readiness checks
- Prometheus metrics
- API hardening
- Deployment documentation

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
|-- .gitignore
|-- README.md
```

Additional task directories will be introduced as their implementations progress.

---

## Engineering Focus

This internship portfolio emphasizes:

- Enterprise AI application development
- Machine learning integration
- Retrieval and vector database systems
- Agentic workflow orchestration
- API engineering
- Automated testing
- Performance benchmarking
- Modular software architecture
- Deployment readiness

---

## Author

**Sudeera Attanayake**

AI Engineer | Machine Learning | RAG | Agentic AI

**GitHub:** [sudeeraattanayake](https://github.com/sudeeraattanayake)

---

## Security Note

Task 01 is a local engineering demonstration. Department and access-tier metadata filters are not a substitute for authenticated authorization. Additional security and operational controls are required before handling sensitive production data.

## License

No open-source license has been declared for this repository.
