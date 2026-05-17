"""Auth router — registration, login, session management, invitations."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from supabase import Client

from auth.dependencies import get_current_user
from auth.models import CurrentUser
from db.client import get_supabase_client
from services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ── Request / Response models ──────────────────────────────────


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    access_token: str
    new_password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class AcceptInviteRequest(BaseModel):
    invite_token: str


# ── Dependency ─────────────────────────────────────────────────


def _get_auth_service(
    supabase: Client = Depends(get_supabase_client),
) -> AuthService:
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available",
        )
    return AuthService(supabase)


# ── Endpoints ──────────────────────────────────────────────────


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    service: AuthService = Depends(_get_auth_service),
):
    """Register a new user account.

    Creates a Supabase Auth user and a profiles row.
    """
    try:
        result = await service.sign_up(body.email, body.password, body.name)
        return result
    except Exception as e:
        logger.error("Registration failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/login")
async def login(
    body: LoginRequest,
    service: AuthService = Depends(_get_auth_service),
):
    """Authenticate with email + password.

    Returns user data, JWT tokens, and org memberships.
    """
    try:
        result = await service.sign_in(body.email, body.password)
        return result
    except Exception as e:
        logger.error("Login failed for %s: %s", body.email, e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from e


@router.post("/logout")
async def logout(
    current_user: CurrentUser = Depends(get_current_user),
    service: AuthService = Depends(_get_auth_service),
):
    """Sign out the current user (invalidate session)."""
    await service.sign_out("")
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    service: AuthService = Depends(_get_auth_service),
):
    """Get the current authenticated user's profile and org memberships."""
    result = await service.get_current_user_data(current_user.id)
    return result


@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequest,
    service: AuthService = Depends(_get_auth_service),
):
    """Request a password reset email.

    Always returns success to avoid email enumeration.
    """
    await service.forgot_password(body.email)
    return {"message": "If an account exists with this email, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    service: AuthService = Depends(_get_auth_service),
):
    """Reset password using the token from the reset email."""
    try:
        await service.reset_password(body.access_token, body.new_password)
        return {"message": "Password has been reset successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/refresh")
async def refresh_token(
    body: RefreshRequest,
    service: AuthService = Depends(_get_auth_service),
):
    """Refresh an expired access token."""
    try:
        result = await service.refresh_session(body.refresh_token)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to refresh session",
        ) from e


@router.post("/accept-invite")
async def accept_invite(
    body: AcceptInviteRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: AuthService = Depends(_get_auth_service),
):
    """Accept an organization invitation.

    The invite_token is the org_members row ID for the pending invitation.
    """
    try:
        result = await service.accept_invitation(body.invite_token, current_user.id)
        return {"message": "Invitation accepted", **result}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
