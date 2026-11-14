# Task 03 — Autonomous Field Agent: ERP/CRM Tool Orchestration

FastAPI + LangGraph + OpenAI + SQLite + Next.js demo for Datheon FDE internship.

## Features
- Agent tool calling for inventory, CRM lead lookup, ticket lookup
- Approval-gated lead updates and support ticket creation
- Persistent SQLite mock ERP/CRM data, audit events and approvals
- Bounded retries for transient SQLite read failures
- Execution trace (tool calls and observations, not private model reasoning)
- Responsive Next.js dashboard with approvals, inventory, leads and tickets
- Automated backend API tests

## Start backend (Windows PowerShell)
```powershell
cd task-03-autonomous-erp-crm-agent
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and set OPENAI_API_KEY
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8002
```
API docs: http://localhost:8002/docs

## Start frontend (new terminal)
```powershell
cd task-03-autonomous-erp-crm-agent/frontend
Copy-Item .env.local.example .env.local
npm install
npm run dev -- -p 3003
```
Dashboard: http://localhost:3003

## Tests
```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

## Sample prompts
- Check stock and price for LAP-001
- Look up CRM lead LEAD-001
- Update lead LEAD-001 status to qualified
- Create a high priority ticket for Acme about a laptop failure

## Important limitations
This is a local mock enterprise demo, not production-ready. Agent tools call the same local service layer as REST endpoints rather than making HTTP requests to an external ERP/CRM. The optional DEMO_API_KEY is a shared key, **not** user authentication or role-based approver authorization. Never expose the service publicly or use real sensitive customer data. For production: implement authenticated approver identities, RBAC, secret management, rate limits, stronger prompt-injection defenses, external API adapters and end-to-end evaluation.
