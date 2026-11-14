import json, uuid, sqlite3, time
from services.database import connect,query,log
READ={"inventory_lookup":("inventory","sku","sku"),"lead_lookup":("leads","id","lead_id"),"ticket_lookup":("tickets","id","ticket_id")}
WRITE={"update_lead_status","create_support_ticket"}
STATUSES={"new","contacted","qualified","proposal","won","lost"}
PRIORITIES={"low","medium","high","critical"}
class BusinessError(ValueError):pass

def field(args,key,max_len=300):
    v=args.get(key)
    if not isinstance(v,str) or not v.strip() or len(v)>max_len:raise BusinessError("Invalid "+key)
    return v.strip()

def read(name,args):
    if name not in READ:raise BusinessError("Unknown tool")
    table,column,key=READ[name]; value=field(args,key)
    result=query(f"SELECT * FROM {table} WHERE {column}=?",(value,))
    log("read",{"tool":name,"id":value,"found":bool(result)})
    return {"found":bool(result),"data":result}

def retry_read(name,args):
    for attempt in range(3):
        try:return read(name,args)
        except sqlite3.OperationalError:
            if attempt==2:raise
            time.sleep(0.15*2**attempt)

def validate(name,args):
    if name=="update_lead_status":
        lead_id=field(args,"lead_id");status=field(args,"status").lower()
        if status not in STATUSES:raise BusinessError("Invalid status")
        if not query("SELECT id FROM leads WHERE id=?",(lead_id,)):raise BusinessError("Unknown lead")
        return {"lead_id":lead_id,"status":status}
    if name=="create_support_ticket":
        priority=field(args,"priority").lower()
        if priority not in PRIORITIES:raise BusinessError("Invalid priority")
        return {"customer":field(args,"customer"),"subject":field(args,"subject",500),"priority":priority}
    raise BusinessError("Unknown operation")

def request(name,args):
    values=validate(name,args);id=str(uuid.uuid4())
    with connect() as db:
        db.execute("INSERT INTO approvals(id,operation,args) VALUES(?,?,?)",(id,name,json.dumps(values)))
        db.execute("INSERT INTO audit(event,details) VALUES(?,?)",("approval_requested",json.dumps({"id":id,"operation":name})))
    return {"approval_id":id,"operation":name,"arguments":values,"status":"pending"}

def decide(id,approve):
    with connect() as db:
        a=db.execute("SELECT * FROM approvals WHERE id=?",(id,)).fetchone()
        if not a:raise BusinessError("Approval not found")
        if a["status"]!="pending":raise BusinessError("Already resolved")
        args=json.loads(a["args"])
        if approve and a["operation"]=="update_lead_status":
            if args["status"] not in STATUSES:raise BusinessError("Invalid status")
            cur=db.execute("UPDATE leads SET status=? WHERE id=?",(args["status"],args["lead_id"]))
            if cur.rowcount!=1:raise BusinessError("Unknown lead")
            result={"lead_id":args["lead_id"],"status":args["status"]}
        elif approve and a["operation"]=="create_support_ticket":
            if args["priority"] not in PRIORITIES:raise BusinessError("Invalid priority")
            ticket="TKT-"+uuid.uuid4().hex[:10].upper()
            db.execute("INSERT INTO tickets(id,customer,subject,priority) VALUES(?,?,?,?)",
                       (ticket,args["customer"],args["subject"],args["priority"]))
            result={"ticket_id":ticket}
        elif not approve:result={"message":"Rejected"}
        else:raise BusinessError("Unknown operation")
        status="approved" if approve else "rejected"
        db.execute("UPDATE approvals SET status=?,resolved_at=CURRENT_TIMESTAMP WHERE id=?",(status,id))
        db.execute("INSERT INTO audit(event,details) VALUES(?,?)",
                   ("approval_resolved",json.dumps({"id":id,"status":status,"result":result})))
    return {"approval_id":id,"status":status,"result":result}
