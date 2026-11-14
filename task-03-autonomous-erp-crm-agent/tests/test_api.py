import pytest
from fastapi.testclient import TestClient
from api.main import app
@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('AGENT_DB_PATH',str(tmp_path/'test.db'))
    monkeypatch.delenv('DEMO_API_KEY',raising=False)
    with TestClient(app) as c:yield c

def test_health(client):assert client.get('/health').json()['status']=='healthy'
def test_inventory(client):assert client.get('/erp/inventory/LAP-001').json()['quantity']==25
def test_missing_inventory(client):assert client.get('/erp/inventory/NA').status_code==404
def test_leads(client):assert len(client.get('/crm/leads').json()['leads'])==3
def test_pending_not_executed(client):
    r=client.post('/crm/leads/LEAD-001/status',json={'status':'qualified'})
    assert r.json()['status']=='pending'
    assert client.get('/crm/leads/LEAD-001').json()['status']=='new'
def test_approve(client):
    id=client.post('/crm/leads/LEAD-001/status',json={'status':'qualified'}).json()['approval_id']
    assert client.post(f'/approvals/{id}/decision',json={'approve':True}).json()['status']=='approved'
    assert client.get('/crm/leads/LEAD-001').json()['status']=='qualified'
def test_reject(client):
    id=client.post('/crm/leads/LEAD-001/status',json={'status':'won'}).json()['approval_id']
    assert client.post(f'/approvals/{id}/decision',json={'approve':False}).json()['status']=='rejected'
    assert client.get('/crm/leads/LEAD-001').json()['status']=='new'
def test_ticket_approval(client):
    id=client.post('/support/tickets',json={'customer':'Acme','subject':'Laptop failed','priority':'high'}).json()['approval_id']
    assert client.get('/support/tickets').json()['tickets']==[]
    client.post(f'/approvals/{id}/decision',json={'approve':True})
    assert len(client.get('/support/tickets').json()['tickets'])==1
def test_duplicate_denied(client):
    id=client.post('/crm/leads/LEAD-001/status',json={'status':'won'}).json()['approval_id']
    client.post(f'/approvals/{id}/decision',json={'approve':True})
    assert client.post(f'/approvals/{id}/decision',json={'approve':True}).status_code==409
def test_invalid_status(client):assert client.post('/crm/leads/LEAD-001/status',json={'status':'hacked'}).status_code==400
def test_audit(client):
    client.get('/erp/inventory/LAP-001')
    assert len(client.get('/audit').json()['events'])>=1
def test_stats(client):assert client.get('/stats').json()['inventory_items']==4
def test_pending_list(client):
    client.post('/crm/leads/LEAD-001/status',json={'status':'won'})
    assert len(client.get('/approvals/pending').json()['approvals'])==1
