import json, os, sqlite3
from pathlib import Path
from contextlib import contextmanager

def path():
    p=Path(os.getenv("AGENT_DB_PATH","data/enterprise.db"))
    return p if p.is_absolute() else Path(__file__).resolve().parents[1]/p

@contextmanager
def connect():
    p=path();p.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(p,timeout=20)
    db.row_factory=sqlite3.Row
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS inventory(sku TEXT PRIMARY KEY,name TEXT,quantity INTEGER,price REAL);
        CREATE TABLE IF NOT EXISTS leads(id TEXT PRIMARY KEY,name TEXT,email TEXT,status TEXT);
        CREATE TABLE IF NOT EXISTS tickets(id TEXT PRIMARY KEY,customer TEXT,subject TEXT,priority TEXT,status TEXT DEFAULT 'open',created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS approvals(id TEXT PRIMARY KEY,operation TEXT,args TEXT,status TEXT DEFAULT 'pending',created_at TEXT DEFAULT CURRENT_TIMESTAMP,resolved_at TEXT);
        CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,event TEXT,details TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        """)
        db.executemany("INSERT OR IGNORE INTO inventory VALUES(?,?,?,?)",[
          ("LAP-001","Business Laptop",25,1200),("MON-002","Dell Monitor",18,340),
          ("KEY-003","Mechanical Keyboard",60,95),("SRV-004","Enterprise Server",4,4800)])
        db.executemany("INSERT OR IGNORE INTO leads VALUES(?,?,?,?)",[
          ("LEAD-001","Acme Industries","contact@acme.example","new"),
          ("LEAD-002","Globex","sales@globex.example","qualified"),
          ("LEAD-003","Stark Enterprises","business@stark.example","contacted")])

def query(sql,args=()):
    with connect() as db:return [dict(x) for x in db.execute(sql,args).fetchall()]

def log(event,details):
    with connect() as db:db.execute("INSERT INTO audit(event,details) VALUES(?,?)",(event,json.dumps(details)))
