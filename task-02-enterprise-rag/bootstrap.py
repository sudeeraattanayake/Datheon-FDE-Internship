"""Create local demo accounts; never use these passwords in production."""
import json
from pathlib import Path
from src.security import password_hash

users = {
    "alice": {"password": "AliceDemo123!", "tenant_id": "acme", "department": "HR", "role": "employee"},
    "manager": {"password": "ManagerDemo123!", "tenant_id": "acme", "department": "HR", "role": "manager"},
    "admin": {"password": "AdminDemo123!", "tenant_id": "acme", "department": "IT", "role": "admin"},
    "other": {"password": "OtherDemo123!", "tenant_id": "globex", "department": "HR", "role": "admin"},
}
for info in users.values():
    info["password_hash"] = password_hash.hash(info.pop("password"))
path = Path("data/users.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(users, indent=2), encoding="utf-8")
print("Demo accounts created: alice, manager, admin, other. See bootstrap.py for passwords.")
