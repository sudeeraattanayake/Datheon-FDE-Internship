from src.security import Identity, Role, allowed, filter_for

def user(role="employee", tenant="acme", dept="HR"):
    return Identity(username="test", role=role, tenant_id=tenant, department=dept)

def meta(tenant="acme", dept="HR", tier="internal"):
    return {"tenant_id": tenant, "department": dept, "access_tier": tier}

def test_same_tenant_employee_internal():
    assert allowed(user(), meta())

def test_tenant_isolation_even_for_admin():
    assert not allowed(user("admin"), meta(tenant="globex"))

def test_department_isolation():
    assert not allowed(user(), meta(dept="Finance"))

def test_clearance():
    assert not allowed(user(), meta(tier="confidential"))
    assert allowed(user("manager"), meta(tier="confidential"))

def test_admin_can_access_other_department_same_tenant():
    assert allowed(user("admin"), meta(dept="Finance"))

def test_unknown_tier_denied():
    assert not allowed(user("admin"), meta(tier="secret"))

def test_query_filter_has_tenant_constraint():
    assert {"tenant_id": {"$eq": "acme"}} in filter_for(user("admin"))["$and"]
