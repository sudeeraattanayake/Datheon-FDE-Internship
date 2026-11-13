from __future__ import annotations
import os
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
import jwt
from fastapi import HTTPException
from pydantic import BaseModel, Field
from pwdlib import PasswordHash

class Role(str, Enum):
    employee = "employee"
    manager = "manager"
    admin = "admin"

class Identity(BaseModel):
    username: str
    tenant_id: str
    department: str
    role: Role

LEVELS = {"public": 0, "internal": 1, "confidential": 2}
ROLE_MAX = {Role.employee: 1, Role.manager: 2, Role.admin: 2}
password_hash = PasswordHash.recommended()

def allowed(identity: Identity, metadata: dict[str, Any]) -> bool:
    if metadata.get("tenant_id") != identity.tenant_id:
        return False
    if identity.role != Role.admin and metadata.get("department") != identity.department:
        return False
    tier = metadata.get("access_tier")
    return isinstance(tier, str) and tier in LEVELS and LEVELS[tier] <= ROLE_MAX[identity.role]

def filter_for(identity: Identity) -> dict:
    clauses = [{"tenant_id": {"$eq": identity.tenant_id}},
               {"access_tier": {"$in": [k for k, v in LEVELS.items() if v <= ROLE_MAX[identity.role]]}}]
    if identity.role != Role.admin:
        clauses.append({"department": {"$eq": identity.department}})
    return {"$and": clauses}

def secret() -> str:
    value = os.environ.get("JWT_SECRET", "")
    if len(value) < 32:
        raise RuntimeError("Set JWT_SECRET to at least 32 random characters")
    return value

def issue_token(identity: Identity) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": identity.username, "tenant_id": identity.tenant_id,
               "department": identity.department, "role": identity.role.value,
               "iat": now, "exp": now + timedelta(hours=1)}
    return jwt.encode(payload, secret(), algorithm="HS256")

def decode_token(token: str) -> Identity:
    try:
        payload = jwt.decode(token, secret(), algorithms=["HS256"], options={"require": ["sub", "exp", "tenant_id", "department", "role"]})
        return Identity(username=payload["sub"], tenant_id=payload["tenant_id"],
                        department=payload["department"], role=payload["role"])
    except (jwt.PyJWTError, ValueError, KeyError) as exc:
        raise HTTPException(401, "Invalid or expired token") from exc
