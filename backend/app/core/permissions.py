"""RBAC permission checks."""

from enum import Enum
from functools import wraps

from fastapi import HTTPException, status


class Role(str, Enum):
    ADMIN = "Admin"
    PV_OFFICER = "PV-Officer"
    QA = "QA"
    VIEWER = "Viewer"


# Maps roles to permitted actions
ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.ADMIN: {"*"},
    Role.PV_OFFICER: {
        "submissions:read", "submissions:write",
        "qc:read", "qc:write",
        "capas:read", "capas:write",
        "audit:read",
        "copilot:use",
        "products:read", "products:write",
    },
    Role.QA: {
        "submissions:read",
        "qc:read", "qc:write",
        "capas:read", "capas:write",
        "audit:read", "audit:write",
        "copilot:use",
        "products:read",
    },
    Role.VIEWER: {
        "submissions:read",
        "qc:read",
        "capas:read",
        "audit:read",
        "products:read",
    },
}


def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission."""
    try:
        role_enum = Role(role)
    except ValueError:
        return False
    perms = ROLE_PERMISSIONS.get(role_enum, set())
    return "*" in perms or permission in perms


def require_permission(permission: str):
    """Decorator for route handlers that checks RBAC permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if current_user is None or not has_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission}",
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
