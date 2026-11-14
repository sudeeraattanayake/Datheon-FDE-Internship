import os,secrets,logging
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1]/'.env')
from fastapi import FastAPI,Depends,Header,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from services.database import init,query
from services.operations import read,request,decide,BusinessError
from agent.workflow import chat
logger=logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app):
    init();yield
app=FastAPI(title='Datheon Task 03 — Autonomous ERP/CRM Agent',version='1.0',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:3003','http://127.0.0.1:3003'],allow_methods=['GET','POST'],allow_headers=['Content-Type','X-Demo-API-Key'])
class Ask(BaseModel):question:str=Field(min_length=3,max_length=2000)
class LeadStatus(BaseModel):status:str
class Ticket(BaseModel):customer:str;subject:str;priority:str='medium'
class Decision(BaseModel):approve:bool
def guard(x_demo_api_key:str|None=Header(default=None)):
    expected=os.getenv('DEMO_API_KEY')
    if expected and (not x_demo_api_key or not secrets.compare_digest(x_demo_api_key,expected)):
        raise HTTPException(401,'Invalid demo API key')
def safe(fn,*args):
    try:return fn(*args)
    except BusinessError as e:raise HTTPException(400,str(e)) from e
@app.get('/health')
def health():return {'status':'healthy'}
@app.get('/erp/inventory')
def inventory(_:None=Depends(guard)):return {'items':query('SELECT * FROM inventory ORDER BY sku')}
@app.get('/erp/inventory/{sku}')
def product(sku:str,_:None=Depends(guard)):
    data=safe(read,'inventory_lookup',{'sku':sku})
    if not data['found']:raise HTTPException(404,'Product not found')
    return data['data'][0]
@app.get('/crm/leads')
def leads(_:None=Depends(guard)):return {'leads':query('SELECT * FROM leads ORDER BY id')}
@app.get('/crm/leads/{id}')
def lead(id:str,_:None=Depends(guard)):
    data=safe(read,'lead_lookup',{'lead_id':id})
    if not data['found']:raise HTTPException(404,'Lead not found')
    return data['data'][0]
@app.post('/crm/leads/{id}/status')
def update(id:str,body:LeadStatus,_:None=Depends(guard)):return safe(request,'update_lead_status',{'lead_id':id,'status':body.status})
@app.get('/support/tickets')
def tickets(_:None=Depends(guard)):return {'tickets':query('SELECT * FROM tickets ORDER BY created_at DESC')}
@app.post('/support/tickets')
def create(body:Ticket,_:None=Depends(guard)):return safe(request,'create_support_ticket',body.model_dump())
@app.get('/support/tickets/{id}')
def ticket(id:str,_:None=Depends(guard)):
    data=safe(read,'ticket_lookup',{'ticket_id':id})
    if not data['found']:raise HTTPException(404,'Ticket not found')
    return data['data'][0]
@app.post('/agent/chat')
def agent(body:Ask,_:None=Depends(guard)):
    try:return chat(body.question)
    except Exception:
        logger.exception('Agent error')
        raise HTTPException(503,'Agent unavailable. Check OpenAI configuration and network.')
@app.get('/approvals')
def approvals(_:None=Depends(guard)):return {'approvals':query('SELECT * FROM approvals ORDER BY created_at DESC')}
@app.get('/approvals/pending')
def pending(_:None=Depends(guard)):return {'approvals':query("SELECT * FROM approvals WHERE status='pending' ORDER BY created_at DESC")}
@app.post('/approvals/{id}/decision')
def approve(id:str,body:Decision,_:None=Depends(guard)):
    try:return decide(id,body.approve)
    except BusinessError as e:raise HTTPException(409,str(e)) from e
@app.get('/audit')
def audit(limit:int=50,_:None=Depends(guard)):return {'events':query('SELECT * FROM audit ORDER BY id DESC LIMIT ?',(max(1,min(200,limit)),))}
@app.get('/stats')
def stats(_:None=Depends(guard)):
    return {k:query(f'SELECT COUNT(*) AS n FROM {v}')[0]['n'] for k,v in {'inventory_items':'inventory','crm_leads':'leads','support_tickets':'tickets','approval_requests':'approvals','audit_events':'audit'}.items()}
