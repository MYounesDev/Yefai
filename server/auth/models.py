"""Auth data models — roles, permissions, user context."""

from enum import Enum

from pydantic import BaseModel


class Role(str, Enum):
    """User roles in the platform."""

    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    TECHNICIAN = "technician"
    PROCUREMENT = "procurement"
    VIEWER = "viewer"


class TokenPayload(BaseModel):
    """Decoded JWT payload from Supabase Auth."""

    sub: str  # user_id (UUID)
    email: str = ""
    exp: int = 0
    aud: str = ""


class CurrentUser(BaseModel):
    """Authenticated user context (from JWT verification)."""

    id: str
    email: str
    is_platform_admin: bool = False


class OrgMembership(BaseModel):
    """A user's membership in a single organization."""

    org_id: str
    org_name: str
    org_slug: str
    org_logo_url: str | None = None
    role: Role
    joined_at: str


class OrgContext(BaseModel):
    """Active organization context for org-scoped requests."""

    org_id: str
    role: Role
    user: CurrentUser
