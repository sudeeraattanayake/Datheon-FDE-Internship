from __future__ import annotations
import json
import os
from pathlib import Path
from src.security import Identity, password_hash

USERS_FILE = Path("data/users.json")

def get_user(username: str) -> dict | None:
    if not USERS_FILE.exists():
        return None
    users = json.loads(USERS_FILE.read_text(encoding="utf-8"))
    return users.get(username)

def verify_user(username: str, password: str) -> Identity | None:
    record = get_user(username)
    if not record or not password_hash.verify(password, record["password_hash"]):
        return None
    return Identity(username=username, tenant_id=record["tenant_id"],
                    department=record["department"], role=record["role"])
