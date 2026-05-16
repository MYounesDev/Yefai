"""FastAPI dependencies for authentication and authorization.

Usage in routers:
    from auth.dependencies import get_current_user, get_org_context, require_role, require_permission

    @router.get("/data")
    async def get_data(
        org: OrgContext = Depends(get_org_context),
        _: None = Depends(require_permission(Permission.VIEW_DASHBOARD)),
    ):
        # org.org_id, org.role, org.user available
        ...
"""

import logging
import os
from collections.abc import Callable
from typing import Any

import jwt
from fastapi import Depends, Header, HTTPException, status

from auth.models import CurrentUser, OrgContext, Role
from auth.permissions import Permission, check_permission
from db.client import get_supabase_client
from db.config import get_settings

logger = logging.getLogger(__name__)


def _is_test_mode() -> bool:
    settings = get_settings()
    return settings.environment == "test" and bool(os.getenv("PYTEST_CURRENT_TEST"))


async def get_current_user(
    authorization: str | None = Header(None, alias="Authorization"),
) -> CurrentUser:
    """Verify Supabase JWT and return the authenticated user.

    Reads the Authorization header (Bearer <token>), decodes the JWT using
    the Supabase JWT secret, and looks up the user's profile for admin status.

    Raises:
        HTTPException 401: If token is missing, invalid, or expired.
    """
    if not authorization:
        if _is_test_mode():
            return CurrentUser(id="test-user", email="test@example.com", is_platform_admin=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'",
        )

    token = authorization[7:]  # Strip "Bearer "
    settings = get_settings()

    if not settings.supabase_jwt_secret:
        # Fallback: in development without JWT secret, try basic decode
        logger.warning("SUPABASE_JWT_SECRET not set — using unverified decode (dev only)")
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
        except jwt.PyJWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {e}",
            ) from e
    else:
        try:
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            ) from e
        except jwt.PyJWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {e}",
            ) from e

    user_id = payload.get("sub")
    email = payload.get("email", "")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing 'sub' claim",
        )

    # Check if user is a platform admin
    is_admin = _check_platform_admin(user_id, email)

    return CurrentUser(id=user_id, email=email, is_platform_admin=is_admin)


def _check_platform_admin(user_id: str, email: str) -> bool:
    """Check if user is a platform admin via profiles table or admin_emails config."""
    settings = get_settings()

    # Check admin emails list from config
    if settings.admin_emails:
        admin_list = [e.strip().lower() for e in settings.admin_emails.split(",")]
        if email.lower() in admin_list:
            return True

    # Check profiles table
    client = get_supabase_client()
    if client is None:
        return False

    try:
        result = (
            client.table("profiles")
            .select("is_platform_admin")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )
        if result.data:
            return bool(result.data.get("is_platform_admin", False))
    except Exception:
        logger.debug("Could not check profiles table for admin status")

    return False


async def get_org_context(
    current_user: CurrentUser = Depends(get_current_user),
    x_organization_id: str | None = Header(None, alias="X-Organization-Id"),
) -> OrgContext:
    """Validate user is a member of the specified organization and return context.

    Reads X-Organization-Id header, checks org_members table for the user's
    membership and role in that organization.

    Raises:
        HTTPException 400: If org ID is missing or invalid.
        HTTPException 403: If user is not a member of the organization.
    """
    if _is_test_mode():
        return OrgContext(
            org_id="test-org",
            role=Role.MANAGER,
            user=current_user,
        )

    if not x_organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Organization-Id header is required",
        )

    client = get_supabase_client()
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available",
        )

    try:
        result = (
            client.table("org_members")
            .select("role, status")
            .eq("org_id", x_organization_id)
            .eq("user_id", current_user.id)
            .maybe_single()
            .execute()
        )
    except Exception as e:
        logger.error("Failed to check org membership: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify organization access",
        ) from e

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )

    member = result.data
    if member.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Your membership is '{member.get('status')}' — access denied",
        )

    role = Role(member["role"])

    return OrgContext(org_id=x_organization_id, role=role, user=current_user)


def require_role(*roles: Role) -> Callable[..., Any]:
    """Dependency factory: checks if the user's org role is in the allowed set.

    Usage:
        @router.get("/admin-data")
        async def admin_data(
            org: OrgContext = Depends(get_org_context),
            _: None = Depends(require_role(Role.MANAGER, Role.ADMIN)),
        ):
    """

    async def _check(org: OrgContext = Depends(get_org_context)) -> None:
        if org.role not in roles:
            allowed = ", ".join(r.value for r in roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{org.role.value}' not allowed. Required: {allowed}",
            )

    return _check


def require_permission(permission: Permission) -> Callable[..., Any]:
    """Dependency factory: checks if the user's role has the given permission.

    Usage:
        @router.post("/approve")
        async def approve(
            org: OrgContext = Depends(get_org_context),
            _: None = Depends(require_permission(Permission.APPROVE_PO)),
        ):
    """

    async def _check(org: OrgContext = Depends(get_org_context)) -> None:
        check_permission(org.role, permission)

    return _check


async def require_platform_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Dependency: ensures the user is a platform administrator.

    Usage:
        @router.get("/admin/orgs")
        async def list_orgs(admin: CurrentUser = Depends(require_platform_admin)):
    """
    if not current_user.is_platform_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform administrator access required",
        )
    return current_user
